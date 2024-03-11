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
from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.material import AICMaterial
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.chat_mutations import (
    AppendToContentMessageMutation,
    AppendToOutputToolCallMutation,
    CreateMessageMutation,
    CreateToolCallMutation,
    SetIsSuccessfulToolCallMutation,
)
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.chat.execution_modes.execution_mode import ExecutionMode
from aiconsole.core.code_running.code_interpreters.base_code_interpreter import (
    CodeExecutionError,
)
from aiconsole.core.code_running.run_code import (
    get_code_interpreter,
    run_in_code_interpreter,
)


class ExecutionModeParams(BaseModel):
    start: int = Field(default=10)
    end: int = Field(default=1)
    message: str = Field(default="Hello world!")


async def _execution_mode_process(
    chat_mutator: ChatMutator,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
    params_values: dict[str, Any] = {},
):
    params = ExecutionModeParams(**params_values)
    start = params.start
    end = params.end
    message = params.message

    message_id = str(uuid4())

    # Assumes that a group already exists
    await chat_mutator.mutate(
        CreateMessageMutation(
            message_group_id=chat_mutator.chat.message_groups[-1].id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            content=f'This is a demo of execution mode. I will count down from {start} to {end} and then run code that prints "{message}".\n\n',
        )
    )

    for i in range(start, end - 1, -1):
        await chat_mutator.mutate(
            AppendToContentMessageMutation(
                message_id=message_id,
                content_delta=f"{i}...",
            )
        )
        await asyncio.sleep(1)

    await asyncio.sleep(1)

    message_id = str(uuid4())
    await chat_mutator.mutate(
        CreateMessageMutation(
            message_group_id=chat_mutator.chat.message_groups[-1].id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            content="Done",
        )
    )

    tool_call_id = str(uuid4())

    code = f"print('{message}')"

    await chat_mutator.mutate(
        CreateToolCallMutation(
            tool_call_id=tool_call_id,
            message_id=message_id,
            code=code,
            headline="",
            language="python",
            output="",
            is_streaming=False,
            is_executing=False,
            is_successful=False,
        )
    )

    try:
        try:
            async for token in run_in_code_interpreter("python", chat_mutator.chat.id, code, []):
                await chat_mutator.mutate(
                    AppendToOutputToolCallMutation(
                        tool_call_id=tool_call_id,
                        output_delta=token,
                    )
                )
            await chat_mutator.mutate(
                SetIsSuccessfulToolCallMutation(
                    tool_call_id=tool_call_id,
                    is_successful=True,
                ),
            )
        except CodeExecutionError:
            pass
        except asyncio.CancelledError:
            (await get_code_interpreter("python", chat_mutator.chat.id)).terminate()
            raise
    except Exception as e:
        await connection_manager().send_to_chat(ErrorServerMessage(error=str(e)), chat_mutator.chat.id)
        raise e


execution_mode = ExecutionMode(
    process_chat=_execution_mode_process,
)
