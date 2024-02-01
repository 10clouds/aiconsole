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
from typing import cast
from uuid import uuid4

from aiconsole.consts import DIRECTOR_MIN_TOKENS, DIRECTOR_PREFERRED_TOKENS
from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.models import AssetLocation, AssetStatus
from aiconsole.core.chat.chat_mutations import (
    CreateMessageGroupMutation,
    SetAgentIdMessageGroupMutation,
    SetAnalysisMessageGroupMutation,
    SetIsAnalysisInProgressMutation,
    SetMaterialsIdsMessageGroupMutation,
    SetTaskMessageGroupMutation,
)
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.chat.convert_messages import convert_messages
from aiconsole.core.chat.execution_modes.analysis.agents_to_choose_from import (
    agents_to_choose_from,
)
from aiconsole.core.chat.execution_modes.analysis.create_plan_class import (
    create_plan_class,
)
from aiconsole.core.chat.types import Chat
from aiconsole.core.gpt.consts import GPTMode
from aiconsole.core.gpt.gpt_executor import GPTExecutor
from aiconsole.core.gpt.request import (
    GPTRequest,
    ToolDefinition,
    ToolFunctionDefinition,
)
from aiconsole.core.gpt.types import (
    EnforcedFunctionCall,
    EnforcedFunctionCallFuncSpec,
    GPTRequestTextMessage,
)
from aiconsole.core.project import project

_log = logging.getLogger(__name__)


def pick_agent(arguments, chat: Chat, available_agents: list[Agent]) -> Agent:
    # Try support first
    default_agent = next((agent for agent in available_agents if agent.id == "assistant"), None)

    # Pick any if not available
    if not default_agent:
        default_agent = available_agents[0]

    is_users_turn = arguments.is_users_turn

    if is_users_turn:
        picked_agent = Agent(
            id="user",
            name="User",
            usage="When a human user needs to respond",
            usage_examples=[],
            system="",
            defined_in=AssetLocation.AICONSOLE_CORE,
            override=False,
        )
    else:
        try:
            picked_agent = next((agent for agent in available_agents if agent.id == arguments.agent_id))
        except StopIteration:
            picked_agent = None

    _log.debug(f"Chosen agent: {picked_agent}")

    if not picked_agent:
        picked_agent = default_agent

    # If it turns out that the user must respond to him self, have the assistant drive the conversation
    if is_users_turn and chat.message_groups and chat.message_groups[-1].role == "user":
        picked_agent = default_agent

    return picked_agent


def _get_relevant_materials(relevant_material_ids: list[str]) -> list[Material]:
    # Maximum of 5 materials
    relevant_materials = [
        cast(Material, k)
        for k in project.get_project_materials().assets_with_status(AssetStatus.ENABLED)
        if k.id in relevant_material_ids
    ][:5]

    relevant_materials += cast(
        list[Material],
        project.get_project_materials().assets_with_status(AssetStatus.FORCED),
    )

    return relevant_materials


@dataclass
class AnalysisResult:
    agent: Agent
    relevant_materials: list[Material]
    next_step: str


async def gpt_analysis_function_step(
    chat_mutator: ChatMutator,
    gpt_mode: GPTMode,
    initial_system_prompt: str,
    last_system_prompt: str,
    force_call: bool,
) -> AnalysisResult:
    gpt_executor = GPTExecutor()

    # Create a new message group for analysis
    message_group_id = str(uuid4())
    await chat_mutator.mutate(
        CreateMessageGroupMutation(
            message_group_id=message_group_id,
            agent_id="director",
            username="",
            email="",
            role="system",
            materials_ids=[],
            analysis="",
            task="",
        )
    )

    # Pick from forced or enabled agents if no agent is forced
    if chat_mutator.chat.chat_options.agent_id:
        agent_id = chat_mutator.chat.chat_options.agent_id
        possible_agent_choices = [agent for agent in agents_to_choose_from(all=True) if agent.id == agent_id]
    else:
        possible_agent_choices = agents_to_choose_from()

    if len(possible_agent_choices) == 0:
        raise ValueError("No active agents")

    plan_class = create_plan_class(
        [
            Agent(
                id="user",
                name="User",
                usage="When a human user needs to respond",
                usage_examples=[],
                system="",
                defined_in=AssetLocation.AICONSOLE_CORE,
                override=False,
            ),
            *possible_agent_choices,
        ]
    )

    request = GPTRequest(
        system_message=initial_system_prompt,
        gpt_mode=gpt_mode,
        messages=[
            *convert_messages(chat_mutator.chat),
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

    await chat_mutator.mutate(
        SetIsAnalysisInProgressMutation(
            is_analysis_in_progress=True,
        )
    )

    await chat_mutator.mutate(
        SetAnalysisMessageGroupMutation(
            message_group_id=message_group_id,
            analysis="",
        )
    )

    try:
        async for chunk in gpt_executor.execute(request):
            if len(gpt_executor.partial_response.choices) > 0:
                tool_calls = gpt_executor.partial_response.choices[0].message.tool_calls
                for tool_call in tool_calls:
                    function_call = tool_call.function
                    arguments_dict = function_call.arguments_dict

                    if arguments_dict:
                        if "agent_id" in arguments_dict:
                            await chat_mutator.mutate(
                                SetAgentIdMessageGroupMutation(
                                    message_group_id=message_group_id,
                                    agent_id=arguments_dict["agent_id"],
                                )
                            )

                        if "relevant_material_ids" in arguments_dict:
                            await chat_mutator.mutate(
                                SetMaterialsIdsMessageGroupMutation(
                                    message_group_id=message_group_id,
                                    materials_ids=arguments_dict["relevant_material_ids"],
                                )
                            )

                        if "next_step" in arguments_dict:
                            await chat_mutator.mutate(
                                SetTaskMessageGroupMutation(
                                    message_group_id=message_group_id,
                                    task=arguments_dict["next_step"],
                                )
                            )

                        if "thinking_process" in arguments_dict:
                            await chat_mutator.mutate(
                                SetAnalysisMessageGroupMutation(
                                    message_group_id=message_group_id,
                                    analysis=arguments_dict["thinking_process"],
                                )
                            )
                if not tool_calls:
                    analysis = gpt_executor.partial_response.choices[0].message.content

                    if analysis:
                        await chat_mutator.mutate(
                            SetAnalysisMessageGroupMutation(
                                message_group_id=message_group_id,
                                analysis=analysis,
                            )
                        )
            else:
                _log.warning("No choices in partial response")
                _log.warning(chunk)

        result = gpt_executor.response.choices[0].message

        if len(result.tool_calls) == 0:
            await chat_mutator.mutate(
                SetAnalysisMessageGroupMutation(
                    message_group_id=message_group_id,
                    analysis=result.content or "",
                )
            )
        if len(result.tool_calls) > 1:
            raise ValueError(f"Expected one tool call, got {len(result.tool_calls)}")

        arguments_dict = result.tool_calls[0].function.arguments_dict

        if arguments_dict is None:
            raise ValueError(f"Could not parse arguments from the text: {result.tool_calls[0].function.arguments}")

        plan = plan_class(**arguments_dict)

        picked_agent = pick_agent(plan, chat_mutator.chat, possible_agent_choices)
        await chat_mutator.mutate(
            SetAgentIdMessageGroupMutation(
                message_group_id=message_group_id,
                agent_id=picked_agent.id,
            )
        )

        relevant_materials = _get_relevant_materials(plan.relevant_material_ids)
        await chat_mutator.mutate(
            SetMaterialsIdsMessageGroupMutation(
                message_group_id=message_group_id,
                materials_ids=[material.id for material in relevant_materials],
            )
        )

        await chat_mutator.mutate(
            SetTaskMessageGroupMutation(
                message_group_id=message_group_id,
                task=plan.next_step,
            )
        )

        await chat_mutator.mutate(
            SetAnalysisMessageGroupMutation(
                message_group_id=message_group_id,
                analysis=plan.thinking_process,
            )
        )

        return AnalysisResult(
            agent=picked_agent,
            relevant_materials=relevant_materials,
            next_step=plan.next_step,
        )
    finally:
        await chat_mutator.mutate(
            SetIsAnalysisInProgressMutation(
                is_analysis_in_progress=False,
            )
        )
