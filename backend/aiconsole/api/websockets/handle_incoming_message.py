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
from copy import deepcopy
from typing import Any, Callable, cast
from uuid import uuid4

from aiconsole.api.websockets.client_messages import (
    AcceptCodeClientMessage,
    AcquireLockClientMessage,
    DoMutationClientMessage,
    DuplicateAssetClientMessage,
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
from aiconsole.api.websockets.render_materials import render_materials
from aiconsole.api.websockets.server_messages import (
    ChatOpenedServerMessage,
    DuplicateAssetServerMessage,
    NotificationServerMessage,
    ResponseServerMessage,
)
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.aic_data_context import AICFileDataContext
from aiconsole.core.chat.do_process_chat import do_process_chat
from aiconsole.core.chat.execution_modes.utils.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.chat.locations import ChatRef
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
        SubscribeToClientMessage.__name__: _handle_open_chat_ws_message,
        DuplicateAssetClientMessage.__name__: _handle_duplicate_chat_ws_message,
        StopChatClientMessage.__name__: _handle_stop_chat_ws_message,
        UnsubscribeClientMessage.__name__: _handle_close_chat_ws_message,
        DoMutationClientMessage.__name__: _handle_do_chat_mutation_ws_message,
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
        context = AICFileDataContext(
            lock_id=message.request_id,
            origin=connection,
        )
        await context.acquire_write_lock(ref=message.ref, originating_from_server=False)
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
    context = AICFileDataContext(
        lock_id=message.request_id,
        origin=connection,
    )
    await context.release_write_lock(ref=message.ref, originating_from_server=False)


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
    message = DuplicateAssetClientMessage(**json)
    new_asset_id = str(uuid4())
    try:
        asset = project.get_project_assets().get_asset(message.asset_id)
        if not asset:
            raise Exception("Asset not found")

        duplicated_asset = deepcopy(asset)
        duplicated_asset.id = new_asset_id
        await project.get_project_assets().save_asset(duplicated_asset, old_asset_id=new_asset_id, create=True)
        await project.get_project_assets().reload(initial=True)

        await connection.send(DuplicateAssetServerMessage(asset_id=new_asset_id))
    except Exception as e:
        _log.error(f"Error during duplicating asset {message.asset_id}: {e}")
        await connection.send(
            ResponseServerMessage(
                request_id=message.request_id,
                payload={"error": "Error during duplicating asset", "asset_id": message.asset_id},
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


async def _handle_do_chat_mutation_ws_message(connection: AICConnection | None, json: dict):
    message = DoMutationClientMessage(**json)
    message.mutation.ref.context = AICFileDataContext(
        lock_id=message.request_id,
        origin=connection,
    )

    await message.mutation.ref.context.mutate(message.mutation, originating_from_server=False)


async def _handle_accept_code_ws_message(connection: AICConnection, json: dict):
    events_to_sub: list[type[InternalEvent]] = [
        WaitForEnvEvent,
    ]

    message = AcceptCodeClientMessage(**json)
    context = AICFileDataContext(
        lock_id=message.request_id,
        origin=connection,
    )
    message.tool_call_ref.context = context

    async def _notify(event):
        if isinstance(event, WaitForEnvEvent):
            await connection_manager().send_to_ref(
                NotificationServerMessage(title="Wait", message="Environment is still being created"),
                message.tool_call_ref,
            )

    # This is fishy!
    await message.tool_call_ref.context.__wait_for_all_mutations(ref=message.tool_call_ref)
    chat_ref: ChatRef = (
        message.tool_call_ref.parent_collection.parent.parent_collection.parent.parent_collection.parent
    )

    async def cancelable_task_function():
        for event in events_to_sub:
            internal_events().subscribe(
                event,
                _notify,
            )

        try:
            await context.acquire_write_lock(ref=chat_ref, originating_from_server=True)

            message_ref = message.tool_call_ref.parent_collection.parent
            message_group_ref = message_ref.parent_collection.parent if message_ref else None

            if message_group_ref is None:
                raise Exception(f"Message group ref not found for {message.tool_call_ref}")

            message_group_ref = chat_ref.message_groups[message_group_ref.id]
            agent_id = (await message_group_ref.actor_id.get()).id
            message_id = message.tool_call_ref.parent_collection.parent.id

            agent = project.get_project_assets().get_asset(agent_id)

            if agent is None:
                raise Exception(f"Agent with id {agent_id} not found")

            agent = cast(AICAgent, agent)

            execution_mode = await import_and_validate_execution_mode(agent, chat_ref)

            mats = await render_materials(
                (await chat_ref.message_groups[message_group_ref.id].materials_ids.get()), await chat_ref.get(), agent
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
            await context.release_write_lock(ref=chat_ref, originating_from_server=True)

    task = asyncio.create_task(cancelable_task_function())
    _stoppable_tasks_for_chat[chat_ref.id][task.get_name()] = task
    task.add_done_callback(_get_done_callback(chat_ref.id, task.get_name()))


async def _handle_process_chat_ws_message(connection: AICConnection, json: dict):
    message = ProcessChatClientMessage(**json)
    context = AICFileDataContext(
        lock_id=message.request_id,
        origin=connection,
    )
    message.chat_ref.context = context

    async def cancelable_task_function():
        async with context.write_lock(ref=message.chat_ref, originating_from_server=True):
            await do_process_chat(message.chat_ref)

    task = asyncio.create_task(cancelable_task_function())
    _stoppable_tasks_for_chat[message.chat_ref.id][task.get_name()] = task
    task.add_done_callback(_get_done_callback(message.chat_ref.id, task.get_name()))


def _get_done_callback(chat_id: str, task_id: str) -> Callable:
    def remove_running_task(_: Any) -> None:
        del _stoppable_tasks_for_chat[chat_id][task_id]

    return remove_running_task
