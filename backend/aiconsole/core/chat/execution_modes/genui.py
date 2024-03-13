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
from datetime import datetime
from typing import Any
from uuid import uuid4

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
from aiconsole.core.chat.locations import ChatRef
from aiconsole.core.chat.types import AICMessage
from aiconsole.core.gpt.create_full_prompt_with_materials import (
    create_full_prompt_with_materials,
)
from aiconsole.core.gpt.function_calls import OpenAISchema


class react_ui_tool(OpenAISchema):
    """
    Execute react typescript code in a browser.
    """

    headline: str = Field(
        ...,
        description="Must have. Title of this task with maximum 15 characters.",
        json_schema_extra={"type": "string"},
    )

    code: str = Field(
        ...,
        description="React typescript code to execute. It will be executed in the browser environment.",
        json_schema_extra={"type": "string"},
    )


async def show_prototype_warning(chat_ref: ChatRef):
    # TODO: remove after GenUI is fully implemented
    last_message_group = (await chat_ref.message_groups.get())[-1]

    GENUI_WARNING_MESSAGE = "**WARNING!** The GenUI execution mode is currently in an early prototype phase. "

    await chat_ref.message_groups[last_message_group.id].messages.create(
        AICMessage(
            id=str(uuid4()),
            timestamp=datetime.now().isoformat(),
            content=GENUI_WARNING_MESSAGE,
        ),
    )


async def _execution_mode_process(
    chat_ref: ChatRef,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
    params_values: dict[str, Any] = {},
):
    system_message = create_full_prompt_with_materials(
        intro=get_agent_system_message(agent),
        materials=rendered_materials,
    )

    await show_prototype_warning(chat_ref)

    await generate_response_message_with_code(
        chat_ref, agent, system_message, language_classes=[react_ui_tool], enforced_language=react_ui_tool
    )


execution_mode = ExecutionMode(
    process_chat=_execution_mode_process,
)
