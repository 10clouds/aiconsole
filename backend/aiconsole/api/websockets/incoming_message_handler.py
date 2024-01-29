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
from dataclasses import dataclass
from typing import Any, Callable, cast
from uuid import uuid4

from aiconsole.api.websockets.client_messages import (
    AcceptCodeClientMessage,
    AcquireLockClientMessage,
    CloseChatClientMessage,
    InitChatMutationClientMessage,
    OpenChatClientMessage,
    ProcessChatClientMessage,
    ReleaseLockClientMessage,
    StopChatClientMessage,
)
from aiconsole.api.websockets.connection_manager import (
    AcquiredLock,
    AICConnection,
    connection_manager,
)
from aiconsole.api.websockets.server_messages import (
    ChatOpenedServerMessage,
    NotificationServerMessage,
    ResponseServerMessage,
)
from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.materials.content_evaluation_context import (
    ContentEvaluationContext,
)
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.assets.models import AssetLocation
from aiconsole.core.chat.execution_modes.execution_mode import (
    AcceptCodeContext,
    ProcessChatContext,
)
from aiconsole.core.chat.execution_modes.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.chat.locking import DefaultChatMutator, acquire_lock, release_lock
from aiconsole.core.chat.types import AICMessageGroup, Chat
from aiconsole.core.code_running.run_code import reset_code_interpreters
from aiconsole.core.code_running.virtual_env.create_dedicated_venv import (
    WaitForEnvEvent,
)
from aiconsole.core.gpt.consts import ANALYSIS_GPT_MODE
from aiconsole.core.project import project
from aiconsole.utils.events import internal_events


@dataclass
class MaterialsAndRenderedMaterials:
    materials: list[Material]
    rendered_materials: list[RenderedMaterial]


class IncomingMessageHandler:
    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)
        # TODO: Move this to a file
        self._director_agent = Agent(
            id="director",
            name="Director",
            gpt_mode=ANALYSIS_GPT_MODE,
            execution_mode="aiconsole.core.chat.execution_modes.director:execution_mode",
            usage="",
            usage_examples=[],
            defined_in=AssetLocation.AICONSOLE_CORE,
            override=False,
            system="",
        )
        self._stop_flag = False
        self._running_tasks = defaultdict(dict)

        self._handlers = {
            AcquireLockClientMessage.__name__: self._handle_acquire_lock_ws_message,
            ReleaseLockClientMessage.__name__: self._handle_release_lock_ws_message,
            OpenChatClientMessage.__name__: self._handle_open_chat_ws_message,
            StopChatClientMessage.__name__: self._handle_stop_chat_ws_message,
            CloseChatClientMessage.__name__: self._handle_close_chat_ws_message,
            InitChatMutationClientMessage.__name__: self._handle_init_chat_mutation_ws_message,
            AcceptCodeClientMessage.__name__: self._handle_accept_code_ws_message,
            ProcessChatClientMessage.__name__: self._handle_process_chat_ws_message,
        }

    async def handle_incoming_message(self, connection: AICConnection, json: dict):
        message_type = json["type"]
        handler = self._handlers[message_type]

        self._log.info(f"Handling message {message_type}")

        task_id = str(uuid4())
        task = asyncio.create_task(handler(connection, json))
        self._running_tasks[json["chat_id"]][task_id] = task
        task.add_done_callback(self._get_done_callback(json["chat_id"], task_id))

    async def _handle_acquire_lock_ws_message(self, connection: AICConnection, json: dict):
        message: AcquireLockClientMessage | None = None
        try:
            message = AcquireLockClientMessage(**json)
            await acquire_lock(chat_id=message.chat_id, request_id=message.request_id)

            connection.acquired_locks.append(
                AcquiredLock(
                    chat_id=message.chat_id,
                    request_id=message.request_id,
                )
            )

            self._log.info(f"Acquired lock {message.request_id} {connection.acquired_locks}")
            await connection.send(
                ResponseServerMessage(
                    request_id=message.request_id, payload={"chat_id": message.chat_id}, is_error=False
                )
            )
        except Exception:
            if message is not None:
                await connection.send(
                    ResponseServerMessage(
                        request_id=message.request_id,
                        payload={"error": "Error during acquiring lock", "chat_id": message.chat_id},
                        is_error=True,
                    )
                )

    async def _handle_release_lock_ws_message(self, connection: AICConnection, json: dict):
        message = ReleaseLockClientMessage(**json)
        await release_lock(chat_id=message.chat_id, request_id=message.request_id)

        lock_data = AcquiredLock(chat_id=message.chat_id, request_id=message.request_id)

        if lock_data in connection.acquired_locks:
            connection.acquired_locks.remove(lock_data)
        else:
            self._log.error(f"Lock {lock_data} not found in {connection.acquired_locks}")

    async def _handle_open_chat_ws_message(self, connection: AICConnection, json: dict):
        message = OpenChatClientMessage(**json)
        temporary_request_id = str(uuid4())

        try:
            chat = await acquire_lock(
                chat_id=message.chat_id,
                request_id=temporary_request_id,
                skip_mutating_clients=True,  # Skip because they do not yet have the chat
            )

            connection.open_chats_ids.add(message.chat_id)

            await connection.send(
                ResponseServerMessage(
                    request_id=message.request_id, payload={"chat_id": message.chat_id}, is_error=False
                )
            )

            await connection.send(
                ChatOpenedServerMessage(
                    chat=chat,
                )
            )
        except Exception:
            await connection.send(
                ResponseServerMessage(
                    request_id=message.request_id,
                    payload={"error": "Error during opening chat", "chat_id": message.chat_id},
                    is_error=True,
                )
            )
        finally:
            await release_lock(chat_id=message.chat_id, request_id=temporary_request_id)

    async def _handle_stop_chat_ws_message(self, connection: AICConnection, json: dict):
        message: StopChatClientMessage | None = None
        try:
            message = StopChatClientMessage(**json)
            reset_code_interpreters(chat_id=message.chat_id)
            for task in self._running_tasks[message.chat_id].values():
                task.cancel()
            await connection.send(
                ResponseServerMessage(
                    request_id=message.request_id, payload={"chat_id": message.chat_id}, is_error=False
                )
            )
        except Exception:
            if message is not None:
                await connection.send(
                    ResponseServerMessage(
                        request_id=message.request_id,
                        payload={"error": "Error during closing chat", "chat_id": message.chat_id},
                        is_error=True,
                    )
                )

    async def _handle_close_chat_ws_message(self, connection: AICConnection, json: dict):
        message = CloseChatClientMessage(**json)
        connection.open_chats_ids.discard(message.chat_id)

    async def _handle_init_chat_mutation_ws_message(self, connection: AICConnection | None, json: dict):
        message = InitChatMutationClientMessage(**json)
        mutator = DefaultChatMutator(chat_id=message.chat_id, request_id=message.request_id, connection=connection)

        await mutator.mutate(message.mutation)

    async def _handle_accept_code_ws_message(self, connection: AICConnection, json: dict):
        message = AcceptCodeClientMessage(**json)

        async def _notify(event):
            await connection_manager().send_to_chat(
                NotificationServerMessage(title="Wait", message="Environment is still being created"),
                message.chat_id,
            )

        try:
            chat = await acquire_lock(chat_id=message.chat_id, request_id=message.request_id)

            internal_events().subscribe(
                WaitForEnvEvent,
                _notify,
            )

            chat_mutator = DefaultChatMutator(
                chat_id=message.chat_id,
                request_id=message.request_id,
                connection=None,  # Source connection is None because the originating mutations come from server
            )

            tool_call_location = chat.get_tool_call_location(message.tool_call_id)

            if tool_call_location is None:
                raise Exception(f"Tool call with id {message.tool_call_id} not found")

            agent_id = tool_call_location.message_group.agent_id

            agent = project.get_project_agents().get_asset(agent_id)

            if agent is None:
                raise Exception(f"Agent with id {agent_id} not found")

            agent = cast(Agent, agent)

            execution_mode = await import_and_validate_execution_mode(agent)

            mats = await self._render_materials_from_message_group(
                tool_call_location.message_group, chat_mutator.chat, agent
            )

            await execution_mode.accept_code(
                AcceptCodeContext(
                    chat_mutator=chat_mutator,
                    agent=agent,
                    materials=mats.materials,
                    rendered_materials=mats.rendered_materials,
                    tool_call_id=tool_call_location.tool_call.id,
                )
            )
        finally:
            await release_lock(chat_id=message.chat_id, request_id=message.request_id)

    async def _handle_process_chat_ws_message(self, connection: AICConnection, json: dict):
        message = ProcessChatClientMessage(**json)
        try:
            await acquire_lock(chat_id=message.chat_id, request_id=message.request_id)

            chat_mutator = DefaultChatMutator(
                chat_id=message.chat_id,
                request_id=message.request_id,
                connection=None,  # Source connection is None because the originating mutations come from server
            )

            agent = self._director_agent

            execution_mode = await import_and_validate_execution_mode(agent)
            await execution_mode.process_chat(
                ProcessChatContext(
                    chat_mutator=chat_mutator,
                    agent=agent,
                    materials=[],
                    rendered_materials=[],
                )
            )
        finally:
            await release_lock(chat_id=message.chat_id, request_id=message.request_id)

    async def _render_materials_from_message_group(
        self, message_group: AICMessageGroup, chat: Chat, agent: Agent
    ) -> MaterialsAndRenderedMaterials:
        relevant_materials_ids = message_group.materials_ids

        relevant_materials = [
            cast(Material, project.get_project_materials().get_asset(material_id))
            for material_id in relevant_materials_ids
        ]

        content_context = ContentEvaluationContext(
            chat=chat,
            agent=agent,
            gpt_mode=agent.gpt_mode,
            relevant_materials=relevant_materials,
        )

        rendered_materials = await asyncio.gather(
            *[
                material.render(content_context)
                for material in relevant_materials
                if material.type == "rendered_material"
            ]
        )

        return MaterialsAndRenderedMaterials(materials=relevant_materials, rendered_materials=rendered_materials)

    def _get_done_callback(self, chat_id: str, task_id: str) -> Callable:
        def remove_running_task(_: Any) -> None:
            del self._running_tasks[chat_id][task_id]

        return remove_running_task


incoming_message_handler = IncomingMessageHandler()
