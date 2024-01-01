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
import traceback
from uuid import uuid4

from aiconsole.api.websockets.outgoing_messages import ErrorWSMessage
from aiconsole.core.assets.agents.agent import ExecutionModeContext
from aiconsole.core.code_running.run_code import get_code_interpreter


async def execution_mode_example_countdown(
    context: ExecutionModeContext,
):
    message_id = str(uuid4())

    # Assumes that a group already exists
    context.chat_mutator.op_create_message(
        message_group_id=context.chat_mutator.chat.message_groups[-1].id,
        message_id=message_id,
        timestamp=datetime.now().isoformat(),
        content=f"This is a demo of execution mode. I will count down from 10 to 1 and then hello world code.\n\n",
    )

    for i in range(10, 0, -1):
        context.chat_mutator.op_append_to_message_content(
            message_id=message_id,
            content_delta=f"{i}...",
        )
        await asyncio.sleep(1)

    await asyncio.sleep(1)

    message_id = str(uuid4())
    context.chat_mutator.op_create_message(
        message_group_id=context.chat_mutator.chat.message_groups[-1].id,
        message_id=message_id,
        timestamp=datetime.now().isoformat(),
        content=f"Done",
    )

    tool_call_id = str(uuid4())

    code = "print('Hello world!')"

    context.chat_mutator.op_create_tool_call(
        tool_call_id=tool_call_id,
        message_id=message_id,
        code=code,
        language="python",
        output="",
    )

    try:
        try:
            async for token in get_code_interpreter("python").run(code, []):
                context.chat_mutator.op_append_to_tool_call_output(
                    tool_call_id=tool_call_id,
                    output_delta=token,
                )
        except asyncio.CancelledError:
            get_code_interpreter("python").terminate()
            raise
        except Exception:
            await ErrorWSMessage(error=traceback.format_exc().strip()).send_to_chat(context.chat_mutator.chat.id)
            context.chat_mutator.op_append_to_tool_call_output(
                tool_call_id=tool_call_id,
                output_delta=traceback.format_exc().strip(),
            )
    except Exception as e:
        await ErrorWSMessage(error=str(e)).send_to_chat(context.chat_mutator.chat.id)
        raise e
