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
from dataclasses import dataclass
from typing import cast
from uuid import uuid4

from aiconsole.api.websockets.client_messages import (
    AcceptCodeClientMessage,
    AcquireLockClientMessage,
    CloseChatClientMessage,
    InitChatMutationClientMessage,
    OpenChatClientMessage,
    ProcessChatClientMessage,
    ReleaseLockClientMessage,
)
from aiconsole.api.websockets.connection_manager import AcquiredLock, AICConnection
from aiconsole.api.websockets.server_messages import ChatOpenedServerMessage
from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.asset import AssetLocation
from aiconsole.core.assets.materials.content_evaluation_context import (
    ContentEvaluationContext,
)
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.execution_modes.execution_mode import (
    AcceptCodeContext,
    ProcessChatContext,
)
from aiconsole.core.chat.execution_modes.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.chat.locking import DefaultChatMutator, acquire_lock, release_lock
from aiconsole.core.chat.types import AICMessageGroup, Chat
from aiconsole.core.gpt.consts import GPTMode
from aiconsole.core.project import project

_log = logging.getLogger(__name__)


# TODO: Move this to a file
director_agent = Agent(
    id="director",
    name="Director",
    gpt_mode=GPTMode.QUALITY,
    execution_mode="aiconsole.core.chat.execution_modes.director:execution_mode",
    usage="",
    usage_examples=[],
    defined_in=AssetLocation.AICONSOLE_CORE,
    override=False,
    system="",
)


async def handle_incoming_message(connection: AICConnection, json: dict):
    message_type = json["type"]
    handler = {
        AcquireLockClientMessage.__name__: lambda connection, json: _handle_acquire_lock_ws_message(
            connection, AcquireLockClientMessage(**json)
        ),
        ReleaseLockClientMessage.__name__: lambda connection, json: _handle_release_lock_ws_message(
            connection, ReleaseLockClientMessage(**json)
        ),
        OpenChatClientMessage.__name__: lambda connection, json: _handle_open_chat_ws_message(
            connection, OpenChatClientMessage(**json)
        ),
        CloseChatClientMessage.__name__: lambda connection, json: _handle_close_chat_ws_message(
            connection, CloseChatClientMessage(**json)
        ),
        InitChatMutationClientMessage.__name__: lambda connection, json: _handle_init_chat_mutation_ws_message(
            connection, InitChatMutationClientMessage(**json)
        ),
        AcceptCodeClientMessage.__name__: lambda connection, json: _handle_accept_code_ws_message(
            connection, AcceptCodeClientMessage(**json)
        ),
        ProcessChatClientMessage.__name__: lambda connection, json: _handle_process_chat_ws_message(
            connection, ProcessChatClientMessage(**json)
        ),
    }[message_type]

    if not handler:
        raise Exception(f"Unknown message type: {message_type}")

    _log.info(f"Handling message {message_type}")

    return await handler(connection, json)


async def _handle_acquire_lock_ws_message(connection: AICConnection, message: AcquireLockClientMessage):
    await acquire_lock(chat_id=message.chat_id, request_id=message.request_id)

    connection.acquired_locks.append(
        AcquiredLock(
            chat_id=message.chat_id,
            request_id=message.request_id,
        )
    )

    _log.info(f"Acquired lock {message.request_id} {connection.acquired_locks}")


async def _handle_release_lock_ws_message(connection: AICConnection, message: ReleaseLockClientMessage):
    await release_lock(chat_id=message.chat_id, request_id=message.request_id)

    lock_data = AcquiredLock(chat_id=message.chat_id, request_id=message.request_id)

    if lock_data in connection.acquired_locks:
        connection.acquired_locks.remove(lock_data)
    else:
        _log.error(f"Lock {lock_data} not found in {connection.acquired_locks}")


async def _handle_open_chat_ws_message(connection: AICConnection, message: OpenChatClientMessage):
    temporary_request_id = str(uuid4())

    try:
        chat = await acquire_lock(
            chat_id=message.chat_id,
            request_id=temporary_request_id,
            skip_mutating_clients=True,  # Skip because they do not yet have the chat
        )

        connection.open_chats_ids.add(message.chat_id)

        await ChatOpenedServerMessage(
            chat=chat,
        ).send_to_connection(connection)
    finally:
        await release_lock(chat_id=message.chat_id, request_id=temporary_request_id)


async def _handle_close_chat_ws_message(connection: AICConnection, message: CloseChatClientMessage):
    connection.open_chats_ids.remove(message.chat_id)


async def _handle_init_chat_mutation_ws_message(
    connection: AICConnection | None, message: InitChatMutationClientMessage
):
    mutator = DefaultChatMutator(chat_id=message.chat_id, request_id=message.request_id, connection=connection)

    await mutator.mutate(message.mutation)


async def _handle_accept_code_ws_message(connection: AICConnection, message: AcceptCodeClientMessage):
    try:
        chat = await acquire_lock(chat_id=message.chat_id, request_id=message.request_id)

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

        mats = await _render_materials_from_message_group(tool_call_location.message_group, chat_mutator.chat, agent)

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


@dataclass
class MaterialsAndRenderedMaterials:
    materials: list[Material]
    rendered_materials: list[RenderedMaterial]


async def _render_materials_from_message_group(
    message_group: AICMessageGroup, chat: Chat, agent: Agent
) -> MaterialsAndRenderedMaterials:
    relevant_materials_ids = message_group.materials_ids

    relevant_materials = [
        cast(Material, project.get_project_materials().get_asset(material_id))
        for material_id in relevant_materials_ids
    ]

    content_context = ContentEvaluationContext(
        chat=chat, agent=agent, gpt_mode=agent.gpt_mode, relevant_materials=relevant_materials
    )

    rendered_materials = await asyncio.gather(
        *[material.render(content_context) for material in relevant_materials if material.type == "rendered_material"]
    )

    return MaterialsAndRenderedMaterials(materials=relevant_materials, rendered_materials=rendered_materials)


async def _handle_process_chat_ws_message(connection: AICConnection, message: ProcessChatClientMessage):
    try:
        chat = await acquire_lock(chat_id=message.chat_id, request_id=message.request_id)

        chat_mutator = DefaultChatMutator(
            chat_id=message.chat_id,
            request_id=message.request_id,
            connection=None,  # Source connection is None because the originating mutations come from server
        )

        agent = director_agent

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
