# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, cast
from uuid import uuid4

from aiconsole.api.websockets.client_messages import (
    AcceptCodeClientMessage,
    AcquireLockClientMessage,
    DoMutationClientMessage,
    DuplicateChatClientMessage,
    ProcessChatClientMessage,
    ReleaseLockClientMessage,
    StopChatClientMessage,
    SubscribeToClientMessage,
    UnsubscribeClientMessage,
)
from aiconsole.api.websockets.connection_manager import (
    AICConnection,
    connection_manager,
)
from aiconsole.api.websockets.do_process_chat import do_process_chat
from aiconsole.api.websockets.render_materials import render_materials
from aiconsole.api.websockets.server_messages import (
    ChatOpenedServerMessage,
    DuplicateChatServerMessage,
    NotificationServerMessage,
    ResponseServerMessage,
)
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.chat.execution_modes.utils.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.locations import ChatRef
from aiconsole.core.chat.locking import (
    DefaultRootMutationContext,
    SequentialRootMutationContext,
    acquire_lock,
    release_lock,
)
from aiconsole.core.chat.root import Root
from aiconsole.core.chat.save_chat_history import save_chat_history
from aiconsole.core.chat.types import AICChat
from aiconsole.core.code_running.run_code import reset_code_interpreters
from aiconsole.core.code_running.virtual_env.create_dedicated_venv import (
    WaitForEnvEvent,
)
from aiconsole.core.project import project
from aiconsole.utils.events import InternalEvent, internal_events

_log = logging.getLogger(__name__)

_stoppable_tasks_for_chat: dict[str, dict[str, asyncio.Task]] = defaultdict(dict)


async def handle_incoming_message(connection: AICConnection, json: dict):
    handlers = {
        AcquireLockClientMessage.__name__: _handle_acquire_lock_ws_message,
        ReleaseLockClientMessage.__name__: _handle_release_lock_ws_message,
        DuplicateChatClientMessage.__name__: _handle_duplicate_chat_ws_message,  # Register the new handler here.
        SubscribeToClientMessage.__name__: _handle_open_chat_ws_message,
        StopChatClientMessage.__name__: _handle_stop_chat_ws_message,
        UnsubscribeClientMessage.__name__: _handle_close_chat_ws_message,
        DoMutationClientMessage.__name__: _handle_init_chat_mutation_ws_message,
        AcceptCodeClientMessage.__name__: _handle_accept_code_ws_message,
        ProcessChatClientMessage.__name__: _handle_process_chat_ws_message,
    }

    message_type = json["type"]

    _log.info(f"Handling message {message_type}")

    await handlers[message_type](connection, json)


async def _handle_acquire_lock_ws_message(connection: AICConnection, json: dict):
    message: AcquireLockClientMessage | None = None
    try:
        message = AcquireLockClientMessage(**json)
        await acquire_lock(ref=message.ref, request_id=message.request_id)

        connection.acquire_lock(ref=message.ref, request_id=message.request_id)

        await connection.send(
            ResponseServerMessage(request_id=message.request_id, payload={"ref": message.ref}, is_error=False)
        )
    except Exception as e:
        _log.error(f"Error during acquiring lock {message.ref if message else 'unknown'}: {e}")
        if message is not None:
            await connection.send(
                ResponseServerMessage(
                    request_id=message.request_id,
                    payload={"error": "Error during acquiring lock", "ref": message.ref},
                    is_error=True,
                )
            )


async def _handle_release_lock_ws_message(connection: AICConnection, json: dict):
    message = ReleaseLockClientMessage(**json)

    root_mutator = SequentialRootMutationContext(
        DefaultRootMutationContext(
            root=Root(assets=project.get_project_assets().all_assets()),
            request_id=message.request_id,
            connection=None,  # Source connection is None because the originating mutations come from server
        )
    )

    async def f():
        await release_lock(message.ref, request_id=message.request_id)

        connection.release_lock(ref=message.ref, request_id=message.request_id)

    await root_mutator.in_sequence(message.ref, f)


async def _handle_open_chat_ws_message(connection: AICConnection, json: dict):
    message = SubscribeToClientMessage(**json)

    try:
        connection.subscribe_to_ref(message.ref)

        chat = cast(AICChat, message.ref.get())

        if connection.is_ref_open(message.ref):
            await connection.send(
                ResponseServerMessage(
                    request_id=message.request_id, payload={"chat_id": message.ref.id}, is_error=False
                )
            )

            await connection.send(
                ChatOpenedServerMessage(
                    chat=chat,
                )
            )
    except Exception as e:
        _log.error(f"Error during opening chat {message.ref.id}: {e}")
        _log.exception(e)

        await connection.send(
            ResponseServerMessage(
                request_id=message.request_id,
                payload={"error": "Error during opening chat", "chat_id": message.ref.id},
                is_error=True,
            )
        )


async def _handle_duplicate_chat_ws_message(connection: AICConnection, json: dict):
    message = DuplicateChatClientMessage(**json)
    # Implement the logic for duplicating a chat here.
    # This is a placeholder implementation.
    new_chat_id = str(uuid4())
    try:
        chat = await load_chat_history(message.chat_id)
        chat.id = new_chat_id
        await save_chat_history(chat)
        await project.get_project_assets().reload(initial=True)

        await connection.send(DuplicateChatServerMessage(chat_id=new_chat_id))
    except Exception as e:
        _log.error(f"Error during duplicating chat {message.chat_id}: {e}")
        await connection.send(
            ResponseServerMessage(
                request_id=message.request_id,
                payload={"error": "Error during duplicating chat", "chat_id": message.chat_id},
                is_error=True,
            )
        )


async def _handle_stop_chat_ws_message(connection: AICConnection, json: dict):
    message: StopChatClientMessage | None = None
    try:
        message = StopChatClientMessage(**json)
        reset_code_interpreters(chat_id=message.chat_ref.id)
        for task in _stoppable_tasks_for_chat[message.chat_ref.id].values():
            task.cancel()
        await connection.send(
            ResponseServerMessage(
                request_id=message.request_id, payload={"chat_id": message.chat_ref.id}, is_error=False
            )
        )
    except Exception:
        if message is not None:
            await connection.send(
                ResponseServerMessage(
                    request_id=message.request_id,
                    payload={"error": "Error during closing chat", "chat_id": message.chat_ref.id},
                    is_error=True,
                )
            )


async def _handle_close_chat_ws_message(connection: AICConnection, json: dict):
    message = UnsubscribeClientMessage(**json)
    connection.unsubscribe_ref(message.ref)


async def _handle_init_chat_mutation_ws_message(connection: AICConnection | None, json: dict):
    message = DoMutationClientMessage(**json)
    message.mutation.ref.context = SequentialRootMutationContext(
        DefaultRootMutationContext(
            root=Root(assets=project.get_project_assets().all_assets()),
            request_id=message.request_id,
            connection=connection,
        )
    )

    await message.mutation.ref.context.mutate(message.mutation)


async def _handle_accept_code_ws_message(connection: AICConnection, json: dict):
    events_to_sub: list[type[InternalEvent]] = [
        WaitForEnvEvent,
    ]

    message = AcceptCodeClientMessage(**json)
    message.tool_call_ref.context = SequentialRootMutationContext(
        DefaultRootMutationContext(
            root=Root(assets=project.get_project_assets().all_assets()),
            request_id=message.request_id,
            connection=connection,
        )
    )

    async def _notify(event):
        if isinstance(event, WaitForEnvEvent):
            await connection_manager().send_to_ref(
                NotificationServerMessage(title="Wait", message="Environment is still being created"),
                message.tool_call_ref,
            )

    # This is fishy!
    await message.tool_call_ref.context.wait_for_all_mutations(ref=message.tool_call_ref)
    chat_ref: ChatRef = message.tool_call_ref.parent.parent.parent.parent.parent.parent

    async def cancelable_task_function():
        try:
            for event in events_to_sub:
                internal_events().subscribe(
                    event,
                    _notify,
                )

            await acquire_lock(ref=chat_ref, request_id=message.request_id)

            message_ref = message.tool_call_ref.parent.parent
            message_group_ref = message_ref.parent.parent if message_ref else None

            if message_group_ref is None:
                raise Exception(f"Message group ref not found for {message.tool_call_ref}")

            message_group_ref = chat_ref.message_groups[message_group_ref.id]
            agent_id = message_group_ref.actor_id.get().id
            message_id = message.tool_call_ref.parent.parent.id

            agent = project.get_project_assets().get_asset(agent_id)

            if agent is None:
                raise Exception(f"Agent with id {agent_id} not found")

            agent = cast(AICAgent, agent)

            execution_mode = await import_and_validate_execution_mode(agent, chat_ref)

            mats = await render_materials(
                chat_ref.message_groups[message_group_ref.id].materials_ids.get(), chat_ref.get(), agent
            )

            await execution_mode.accept_code(
                tool_call_ref=message_group_ref.messages[message_id].tool_calls[message.tool_call_ref.id],
                agent=agent,
                materials=mats.materials,
                rendered_materials=mats.rendered_materials,
            )
        finally:
            for event in events_to_sub:
                internal_events().unsubscribe(
                    event,
                    _notify,
                )
            await release_lock(ref=chat_ref, request_id=message.request_id)

    task = asyncio.create_task(cancelable_task_function())
    _stoppable_tasks_for_chat[chat_ref.id][task.get_name()] = task
    task.add_done_callback(_get_done_callback(chat_ref.id, task.get_name()))


async def _handle_process_chat_ws_message(connection: AICConnection, json: dict):
    message = ProcessChatClientMessage(**json)
    message.chat_ref.context = SequentialRootMutationContext(
        DefaultRootMutationContext(
            root=Root(assets=project.get_project_assets().all_assets()),
            request_id=message.request_id,
            connection=None,  # Source connection is None because the originating mutations come from server
        )
    )

    async def cancelable_task_function():
        try:

            async def f():
                await acquire_lock(ref=message.chat_ref, request_id=message.request_id)

            await message.chat_ref.context.in_sequence(message.chat_ref, f)
            await message.chat_ref.context.wait_for_all_mutations(message.chat_ref)

            await do_process_chat(message.chat_ref)
        finally:
            await release_lock(ref=message.chat_ref, request_id=message.request_id)

    task = asyncio.create_task(cancelable_task_function())
    _stoppable_tasks_for_chat[message.chat_ref.id][task.get_name()] = task
    task.add_done_callback(_get_done_callback(message.chat_ref.id, task.get_name()))


def _get_done_callback(chat_id: str, task_id: str) -> Callable:
    def remove_running_task(_: Any) -> None:
        del _stoppable_tasks_for_chat[chat_id][task_id]

    return remove_running_task
