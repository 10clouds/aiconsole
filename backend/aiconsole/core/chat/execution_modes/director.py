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
from aiconsole.core.chat.chat_mutations import DeleteMessageGroupMutation
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.chat.execution_modes.analysis.director import director_analyse
from aiconsole.core.chat.execution_modes.execution_mode import ExecutionMode
from aiconsole.core.chat.execution_modes.utils.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)

_log = logging.getLogger(__name__)


async def _execution_mode_process(
    chat_mutator: ChatMutator,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
    params_values: dict[str, Any] = {},
):
    _log.debug("execution_mode_director")

    # Assumes an existing message group that was created for us
    last_message_group = chat_mutator.chat.message_groups[-1]

    # if there are no messages in message groups, stop processing
    if not any(group.messages for group in chat_mutator.chat.message_groups):
        # Send an error notification and delete the current message group
        _log.error("No messages in message groups")

        await connection_manager().send_to_chat(
            message=NotificationServerMessage(title="Error", message="No messages to respond to"),
            chat_id=chat_mutator.chat.id,
        )

        await chat_mutator.mutate(DeleteMessageGroupMutation(message_group_id=last_message_group.id))

        return

    last_messages = chat_mutator.chat.message_groups[-2].messages
    for message in last_messages:
        if message.tool_calls and not all(call.output for call in message.tool_calls):
            await chat_mutator.mutate(DeleteMessageGroupMutation(message_group_id=last_message_group.id))
            return

    analysis = await director_analyse(chat_mutator, last_message_group.id)

    if analysis.agent.id != "user" and analysis.next_step:
        content_context = ContentEvaluationContext(
            chat=chat_mutator.chat,
            agent=analysis.agent,
            gpt_mode=analysis.agent.gpt_mode,
            relevant_materials=analysis.relevant_materials,
        )

        rendered_materials = [
            await material.render(content_context) for material in content_context.relevant_materials
        ]

        execution_mode = await import_and_validate_execution_mode(analysis.agent, chat_mutator.chat.id)

        await execution_mode.process_chat(
            chat_mutator=chat_mutator,
            agent=analysis.agent,
            materials=analysis.relevant_materials,
            rendered_materials=rendered_materials,
            params_values=analysis.agent.execution_mode_params_values,
        )
    else:
        # Delete the current message group
        await chat_mutator.mutate(DeleteMessageGroupMutation(message_group_id=last_message_group.id))


execution_mode = ExecutionMode(
    process_chat=_execution_mode_process,
)
