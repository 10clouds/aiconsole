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
from typing import cast

from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.materials.content_evaluation_context import (
    ContentEvaluationContext,
)
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.execution_modes.analysis.director import director_analyse
from aiconsole.core.chat.execution_modes.execution_mode import (
    AcceptCodeContext,
    ExecutionMode,
    ProcessChatContext,
)
from aiconsole.core.chat.execution_modes.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.chat.types import AICMessageGroup
from aiconsole.core.project import project

_log = logging.getLogger(__name__)


def agent_from_message_group(message_group: AICMessageGroup) -> Agent:
    # Find the message group with id context.message_group_id
    agent_id = message_group.agent_id
    agent = cast(Agent, project.get_project_agents().get_asset(agent_id))
    return agent


async def render_materials_from_message_group(
    message_group: AICMessageGroup, context: ProcessChatContext, agent: Agent
) -> list[RenderedMaterial]:
    # Find the message group with id context.message_group_id
    relevant_materials_ids = message_group.materials_ids
    relevant_materials = [
        cast(Material, project.get_project_materials().get_asset(material_id))
        for material_id in relevant_materials_ids
    ]

    content_context = ContentEvaluationContext(
        chat=context.chat_mutator.chat,
        agent=agent,
        gpt_mode=agent.gpt_mode,
        relevant_materials=relevant_materials,
    )

    rendered_materials = await asyncio.gather(
        *[material.render(content_context) for material in relevant_materials if material.type == "rendered_material"]
    )

    return rendered_materials


async def execution_mode_process(
    context: ProcessChatContext,
):
    _log.debug("execution_mode_director")

    analysis = await director_analyse(context.chat_mutator)

    if analysis.agent.id != "user" and analysis.next_step:
        content_context = ContentEvaluationContext(
            chat=context.chat_mutator.chat,
            agent=analysis.agent,
            gpt_mode=analysis.agent.gpt_mode,
            relevant_materials=analysis.relevant_materials,
        )

        rendered_materials = [
            await material.render(content_context) for material in content_context.relevant_materials
        ]

        context = ProcessChatContext(
            chat_mutator=context.chat_mutator,
            agent=analysis.agent,
            materials=analysis.relevant_materials,
            rendered_materials=rendered_materials,
        )

        execution_mode = await import_and_validate_execution_mode(analysis.agent)

        await execution_mode.process_chat(context)


async def execution_mode_accept_code(
    context: AcceptCodeContext,
):
    raise Exception("Director does not support running code")


execution_mode = ExecutionMode(
    process_chat=execution_mode_process,
    accept_code=execution_mode_accept_code,
)
