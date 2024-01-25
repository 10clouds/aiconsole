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
from datetime import datetime
from typing import cast
from uuid import uuid4

from litellm.utils import StreamingChoices  # type: ignore

from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.materials.content_evaluation_context import (
    ContentEvaluationContext,
)
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.chat_mutations import (
    AppendToContentMessageMutation,
    CreateMessageMutation,
    SetContentMessageMutation,
    SetIsStreamingMessageMutation,
)
from aiconsole.core.chat.convert_messages import convert_messages
from aiconsole.core.chat.execution_modes.execution_mode import (
    AcceptCodeContext,
    ExecutionMode,
    ProcessChatContext,
)
from aiconsole.core.chat.execution_modes.get_agent_system_message import (
    get_agent_system_message,
)
from aiconsole.core.chat.types import AICMessageGroup
from aiconsole.core.gpt.create_full_prompt_with_materials import (
    create_full_prompt_with_materials,
)
from aiconsole.core.gpt.gpt_executor import GPTExecutor
from aiconsole.core.gpt.request import GPTRequest
from aiconsole.core.gpt.types import CLEAR_STR
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
    _log.debug("execution_mode_normal")

    gpt_executor = GPTExecutor()

    # Create a new message in the message group
    message_id = str(uuid4())

    await context.chat_mutator.mutate(
        CreateMessageMutation(
            message_group_id=context.chat_mutator.chat.message_groups[-1].id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            content="",
        )
    )

    # SetIsStreamingMessageMutation
    await context.chat_mutator.mutate(
        SetIsStreamingMessageMutation(
            message_id=message_id,
            is_streaming=True,
        )
    )
    try:
        async for chunk in gpt_executor.execute(
            GPTRequest(
                messages=convert_messages(context.chat_mutator.chat),
                gpt_mode=context.agent.gpt_mode,
                system_message=create_full_prompt_with_materials(
                    intro=get_agent_system_message(context.agent),
                    materials=context.rendered_materials,
                ),
                min_tokens=250,
                preferred_tokens=2000,
            )
        ):
            if chunk == CLEAR_STR:
                await context.chat_mutator.mutate(SetContentMessageMutation(message_id=message_id, content=""))
            else:
                choices = cast(list[StreamingChoices], chunk.choices)

                await context.chat_mutator.mutate(
                    AppendToContentMessageMutation(message_id=message_id, content_delta=choices[0].delta.content or "")
                )
    except Exception as e:
        _log.exception(e)
    finally:
        await context.chat_mutator.mutate(
            SetIsStreamingMessageMutation(
                message_id=message_id,
                is_streaming=False,
            )
        )


async def execution_mode_accept_code(
    context: AcceptCodeContext,
):
    raise Exception("This agent does not support running code")


execution_mode = ExecutionMode(
    process_chat=execution_mode_process,
    accept_code=execution_mode_accept_code,
)
