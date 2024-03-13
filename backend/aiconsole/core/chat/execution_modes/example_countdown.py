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
from aiconsole.core.chat.execution_modes.execution_mode import ExecutionMode
from aiconsole.core.chat.locations import ChatRef
from aiconsole.core.chat.types import AICMessage, AICToolCall
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
    chat_ref: ChatRef,
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
    msg_group_ref = chat_ref.message_groups[await chat_ref.message_groups.get_item_id_by_index(index=-1)]
    await msg_group_ref.messages.create(
        AICMessage(
            id=message_id,
            timestamp=datetime.now().isoformat(),
            content=f'This is a demo of execution mode. I will count down from {start} to {end} and then run code that prints "{message}".\n\n',
        )
    )

    for i in range(start, end - 1, -1):
        await msg_group_ref.messages[message_id].content.append(f"{i}...")
        await asyncio.sleep(1)

    await asyncio.sleep(1)

    message_id = str(uuid4())
    await msg_group_ref.messages.create(
        AICMessage(
            id=message_id,
            timestamp=datetime.now().isoformat(),
            content="Done",
        ),
    )
    message_mutator = msg_group_ref.messages[message_id]

    tool_call_id = str(uuid4())

    code = f"print('{message}')"

    await message_mutator.tool_calls.create(
        AICToolCall(
            id=tool_call_id,
            code=code,
            headline="",
            language="python",
            output="",
            is_streaming=False,
            is_executing=False,
            is_successful=False,
        ),
    )
    tool_call_mutator = message_mutator.tool_calls[tool_call_id]

    try:
        try:
            async for token in run_in_code_interpreter("python", (await chat_ref.get()).id, code, []):
                await tool_call_mutator.output.append(token)
            await tool_call_mutator.is_successful.set(True)
        except CodeExecutionError:
            pass
        except asyncio.CancelledError:
            (await get_code_interpreter("python", (await chat_ref.get()).id)).terminate()
            raise
    except Exception as e:
        await connection_manager().send_to_ref(ErrorServerMessage(error=str(e)), chat_ref)
        raise e


execution_mode = ExecutionMode(
    process_chat=_execution_mode_process,
)
