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
from dataclasses import dataclass
from datetime import datetime
from typing import cast

from aiconsole.consts import DIRECTOR_MIN_TOKENS, DIRECTOR_PREFERRED_TOKENS
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.material import AICMaterial
from aiconsole.core.assets.types import AssetLocation, AssetType
from aiconsole.core.chat.actor_id import ActorId
from aiconsole.core.chat.convert_messages import convert_messages
from aiconsole.core.chat.execution_modes.analysis.agents_to_choose_from import (
    agents_to_choose_from,
)
from aiconsole.core.chat.execution_modes.analysis.create_plan_class import (
    create_plan_class,
)
from aiconsole.core.chat.locations import ChatRef
from aiconsole.core.chat.types import AICChat
from aiconsole.core.gpt.consts import GPTMode
from aiconsole.core.gpt.gpt_executor import GPTExecutor
from aiconsole.core.gpt.request import GPTRequest
from aiconsole.core.gpt.tool_definition import ToolDefinition, ToolFunctionDefinition
from aiconsole.core.gpt.types import (
    EnforcedFunctionCall,
    EnforcedFunctionCallFuncSpec,
    GPTRequestTextMessage,
)
from aiconsole.core.project import project

_log = logging.getLogger(__name__)


def pick_agent(arguments, chat: AICChat, available_agents: list[AICAgent]) -> AICAgent:
    # Try support first
    default_agent = next((agent for agent in available_agents if agent.id == "assistant"), None)

    # Pick any if not available
    if not default_agent:
        default_agent = available_agents[0]

    try:
        picked_agent = next((agent for agent in available_agents if agent.id == arguments.agent_id))
    except StopIteration:
        picked_agent = None

    _log.debug(f"Chosen agent: {picked_agent}")

    if not picked_agent:
        picked_agent = default_agent

    return picked_agent


def _get_relevant_materials(relevant_material_ids: list[str]) -> list[AICMaterial]:
    return [
        cast(AICMaterial, k)
        for k in project.get_project_assets().assets_with_enabled_flag_set_to(True)
        if k.id in relevant_material_ids
    ]


@dataclass
class AnalysisResult:
    agent: AICAgent
    relevant_materials: list[AICMaterial]
    next_step: str


async def gpt_analysis_function_step(
    message_group_id: str,
    chat_ref: ChatRef,
    gpt_mode: GPTMode,
    initial_system_prompt: str,
    last_system_prompt: str,
    force_call: bool,
) -> AnalysisResult:
    gpt_executor = GPTExecutor()

    message_group_ref = chat_ref.message_groups[message_group_id]

    # Pick from forced or enabled agents if no agent is forced
    possible_agent_choices: list[AICAgent]

    if (await chat_ref.chat_options.get()).agent_id:
        agent_id = (await chat_ref.chat_options.get()).agent_id
        agent = project.get_project_assets().get_asset(agent_id, type=AssetType.AGENT, enabled=True)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        possible_agent_choices = [cast(AICAgent, agent)]
    else:
        possible_agent_choices = agents_to_choose_from()

    if len(possible_agent_choices) == 0:
        raise ValueError("No active agents")

    available_materials = []
    forced_materials = []
    if (await chat_ref.chat_options.get()).materials_ids:
        for material in project.get_project_assets().cached_assets.values():
            if material[0].id in ((await chat_ref.chat_options.get()).materials_ids or []):
                forced_materials.append(material[0])

    if (await chat_ref.chat_options.get()).ai_can_add_extra_materials:
        available_materials = [
            *forced_materials,
            *[
                asset
                for asset in project.get_project_assets().assets_with_enabled_flag_set_to(True)
                if asset.type == AssetType.MATERIAL
            ],
        ]

    plan_class = create_plan_class(
        [
            AICAgent(
                id="user",
                name="User",
                usage="When a human user needs to respond",
                usage_examples=[],
                system="",
                defined_in=AssetLocation.AICONSOLE_CORE,
                override=False,
                last_modified=datetime.now(),
            ),
            *possible_agent_choices,
        ],
        available_materials,
    )

    request = GPTRequest(
        system_message=initial_system_prompt,
        gpt_mode=gpt_mode,
        messages=[
            *convert_messages(await chat_ref.get()),
            GPTRequestTextMessage(role="system", content=last_system_prompt),
        ],
        tools=[
            ToolDefinition(
                type="function",
                function=ToolFunctionDefinition(**plan_class.openai_schema()),
            )
        ],
        presence_penalty=2,
        min_tokens=DIRECTOR_MIN_TOKENS,
        preferred_tokens=DIRECTOR_PREFERRED_TOKENS,
    )

    if force_call:
        request.tool_choice = EnforcedFunctionCall(
            type="function",
            function=EnforcedFunctionCallFuncSpec(name=plan_class.__name__),
        )

    await chat_ref.is_analysis_in_progress.set(True)

    await message_group_ref.analysis.set("")

    try:
        async for chunk in gpt_executor.execute(request):
            if len(gpt_executor.partial_response.choices) > 0:
                tool_calls = gpt_executor.partial_response.choices[0].message.tool_calls
                for tool_call in tool_calls:
                    function_call = tool_call.function
                    arguments_dict = function_call.arguments_dict

                    if arguments_dict:
                        # Current fix for https://github.com/10clouds/aiconsole/issues/785
                        if "agent_id" in arguments_dict and "relevant_material_ids" in arguments_dict:
                            await message_group_ref.actor_id.set(ActorId(type="agent", id=arguments_dict["agent_id"]))

                        if "relevant_material_ids" in arguments_dict:
                            await message_group_ref.materials_ids.set(arguments_dict["relevant_material_ids"])

                        if "next_step" in arguments_dict:
                            await message_group_ref.task.set(arguments_dict["next_step"])

                        if "thinking_process" in arguments_dict:
                            await message_group_ref.analysis.set(arguments_dict["thinking_process"])
                if not tool_calls:
                    analysis = gpt_executor.partial_response.choices[0].message.content

                    if analysis:
                        await message_group_ref.analysis.set(analysis)
            else:
                _log.warning("No choices in partial response")
                _log.warning(chunk)

        result = gpt_executor.response.choices[0].message

        if len(result.tool_calls) == 0:
            await message_group_ref.analysis.set(result.content or "")

        if len(result.tool_calls) > 1:
            raise ValueError(f"Expected one tool call, got {len(result.tool_calls)}")

        arguments_dict = result.tool_calls[0].function.arguments_dict

        if arguments_dict is None:
            raise ValueError(f"Could not parse arguments from the text: {result.tool_calls[0].function.arguments}")

        plan = plan_class(**arguments_dict)

        picked_agent = pick_agent(plan, await chat_ref.get(), possible_agent_choices)
        await message_group_ref.actor_id.set(ActorId(type="agent", id=picked_agent.id))

        relevant_materials = _get_relevant_materials(plan.relevant_material_ids)
        await message_group_ref.materials_ids.set(plan.relevant_material_ids)
        await message_group_ref.task.set(plan.next_step)
        await message_group_ref.analysis.set(plan.thinking_process)

        return AnalysisResult(
            agent=picked_agent,
            relevant_materials=relevant_materials,
            next_step=plan.next_step,
        )
    finally:
        await chat_ref.is_analysis_in_progress.set(False)
