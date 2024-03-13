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

from pydantic import Field

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.material import AICMaterial
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.execution_modes.execution_mode import ExecutionMode
from aiconsole.core.chat.execution_modes.utils.generate_response_message_with_code import (
    generate_response_message_with_code,
)
from aiconsole.core.chat.execution_modes.utils.get_agent_system_message import (
    get_agent_system_message,
)
from aiconsole.core.chat.execution_modes.utils.run_code import run_code
from aiconsole.core.chat.locations import ChatRef, ToolCallRef
from aiconsole.core.gpt.create_full_prompt_with_materials import (
    create_full_prompt_with_materials,
)
from aiconsole.core.gpt.function_calls import OpenAISchema
from aiconsole.core.settings.settings import settings

_log = logging.getLogger(__name__)


class CodeTask(OpenAISchema):
    headline: str = Field(
        ...,
        description="Must have. Title of this tool call (maximum 15 characters).",
        json_schema_extra={"type": "string"},
    )


class python_tool(CodeTask):
    """
    Execute code in a stateful Jupyter notebook environment.
    You can execute shell commands by prefixing code lines with "!".
    You can execute AppleScript in shell.
    Make sure to pass the code and headline as json and not python variables.
    """

    code: str = Field(
        ...,
        description="Python code to execute. It will be executed in the statefull Jupyter notebook environment. Always show result to the user.",
        json_schema_extra={"type": "string"},
    )


async def _execution_mode_process(
    chat_ref: ChatRef,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
    params_values: dict[str, Any] = {},
):
    # Assumes an existing message group that was created for us
    last_message_group = (await chat_ref.get()).message_groups[-1]

    system_message = create_full_prompt_with_materials(
        intro=get_agent_system_message(agent),
        materials=rendered_materials,
    )

    await generate_response_message_with_code(chat_ref, agent, system_message, [python_tool])

    last_message = last_message_group.messages[-1]

    if last_message.tool_calls:
        # Run all code in the last message
        for tool_call in last_message.tool_calls:
            if settings().unified_settings.code_autorun:
                await _execution_mode_accept_code(
                    tool_call_ref=chat_ref.message_groups[last_message_group.id]
                    .messages[last_message.id]
                    .tool_calls[tool_call.id],
                    agent=agent,
                    materials=materials,
                    rendered_materials=rendered_materials,
                )


async def _check_for_all_code_executed(
    tool_call_ref: ToolCallRef,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
):
    tool_call_message_mutator = tool_call_ref.parent_collection.parent
    tool_call_message = await tool_call_message_mutator.get()
    tool_call_message_group_mutator = tool_call_message_mutator.parent_collection.parent
    tool_call_message_group = await tool_call_message_group_mutator.get()
    tool_call_chat_ref = tool_call_message_group_mutator.parent_collection.parent
    tool_call_chat = await tool_call_chat_ref.get()

    # if is in last message and all tools have finished running, resume operation with the same agent
    if (
        tool_call_message_group.id == tool_call_chat.message_groups[-1].id
        and tool_call_message.id == tool_call_chat.message_groups[-1].messages[-1].id
    ):
        finished_running_code = all(
            (not tool_call.is_executing) and (tool_call.output is not None)
            for tool_call in tool_call_message.tool_calls
        )

        if finished_running_code:
            await _execution_mode_process(
                chat_ref=tool_call_chat_ref,
                agent=agent,
                materials=materials,
                rendered_materials=rendered_materials,
            )


async def _execution_mode_accept_code(
    tool_call_ref: ToolCallRef,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
):
    await run_code(
        tool_call_ref=tool_call_ref,
        materials=materials,
    )

    await _check_for_all_code_executed(
        tool_call_ref=tool_call_ref,
        agent=agent,
        materials=materials,
        rendered_materials=rendered_materials,
    )


execution_mode = ExecutionMode(
    process_chat=_execution_mode_process,
    accept_code=_execution_mode_accept_code,
)
