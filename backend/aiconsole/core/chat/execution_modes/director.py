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

import logging
from typing import Any

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import NotificationServerMessage
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.content_evaluation_context import (
    ContentEvaluationContext,
)
from aiconsole.core.assets.materials.material import AICMaterial
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.execution_modes.analysis.director import director_analyse
from aiconsole.core.chat.execution_modes.execution_mode import ExecutionMode
from aiconsole.core.chat.execution_modes.utils.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.chat.locations import ChatRef

_log = logging.getLogger(__name__)


async def _execution_mode_process(
    chat_ref: ChatRef,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
    params_values: dict[str, Any] = {},
):
    _log.debug("execution_mode_director")

    # Assumes an existing message group that was created for us
    last_message_group = chat_ref.message_groups[await chat_ref.message_groups.get_item_id_by_index(-1)]

    # if there are no messages in message groups, stop processing
    if not any(group.messages for group in await chat_ref.message_groups.get()):
        # Send an error notification and delete the current message group
        _log.error("No messages in message groups")

        await connection_manager().send_to_ref(
            message=NotificationServerMessage(title="Error", message="No messages to respond to"),
            ref=chat_ref,
        )

        await chat_ref.message_groups[last_message_group.id].delete()

        return

    last_messages = await chat_ref.message_groups[
        await chat_ref.message_groups.get_item_id_by_index(-2)
    ].messages.get()
    for message in last_messages:
        if message.tool_calls and not all(call.output for call in message.tool_calls):
            await chat_ref.message_groups[last_message_group.id].delete()
            return

    analysis = await director_analyse(chat_ref, last_message_group.id)

    if analysis.agent.id != "user" and analysis.next_step:
        content_context = ContentEvaluationContext(
            chat=await chat_ref.get(),
            agent=analysis.agent,
            gpt_mode=analysis.agent.gpt_mode,
            relevant_materials=analysis.relevant_materials,
        )

        rendered_materials = [
            await material.render(content_context) for material in content_context.relevant_materials
        ]

        execution_mode = await import_and_validate_execution_mode(analysis.agent, chat_ref)

        await execution_mode.process_chat(
            chat_ref=chat_ref,
            agent=analysis.agent,
            materials=analysis.relevant_materials,
            rendered_materials=rendered_materials,
            params_values=analysis.agent.execution_mode_params_values,
        )
    else:
        # Delete the current message group
        await chat_ref.message_groups[last_message_group.id].delete()


execution_mode = ExecutionMode(
    process_chat=_execution_mode_process,
)
