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
import traceback
from datetime import datetime
from uuid import uuid4

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.chat.chat_mutations import (
    AppendToContentMessageMutation,
    AppendToOutputToolCallMutation,
    CreateMessageMutation,
    CreateToolCallMutation,
)
from aiconsole.core.chat.execution_modes.execution_mode import (
    AcceptCodeContext,
    ExecutionMode,
    ProcessChatContext,
)
from aiconsole.core.code_running.run_code import get_code_interpreter


async def execution_mode_process(
    context: ProcessChatContext,
):
    message_id = str(uuid4())

    # Assumes that a group already exists
    await context.chat_mutator.mutate(
        CreateMessageMutation(
            message_group_id=context.chat_mutator.chat.message_groups[-1].id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            content=f"This is a demo of execution mode. I will count down from 10 to 1 and then hello world code.\n\n",
        )
    )

    for i in range(10, 0, -1):
        await context.chat_mutator.mutate(
            AppendToContentMessageMutation(
                message_id=message_id,
                content_delta=f"{i}...",
            )
        )
        await asyncio.sleep(1)

    await asyncio.sleep(1)

    message_id = str(uuid4())
    await context.chat_mutator.mutate(
        CreateMessageMutation(
            message_group_id=context.chat_mutator.chat.message_groups[-1].id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            content=f"Done",
        )
    )

    tool_call_id = str(uuid4())

    code = "print('Hello world!')"

    await context.chat_mutator.mutate(
        CreateToolCallMutation(
            tool_call_id=tool_call_id,
            message_id=message_id,
            code=code,
            headline="",
            language="python",
            output="",
        )
    )

    try:
        try:
            async for token in get_code_interpreter("python").run(code, []):
                await context.chat_mutator.mutate(
                    AppendToOutputToolCallMutation(
                        tool_call_id=tool_call_id,
                        output_delta=token,
                    )
                )
        except asyncio.CancelledError:
            get_code_interpreter("python").terminate()
            raise
        except Exception:
            await connection_manager().send_to_chat(
                ErrorServerMessage(error=traceback.format_exc().strip()), context.chat_mutator.chat.id
            )
            await context.chat_mutator.mutate(
                AppendToOutputToolCallMutation(
                    tool_call_id=tool_call_id,
                    output_delta=traceback.format_exc().strip(),
                )
            )
    except Exception as e:
        await connection_manager().send_to_chat(ErrorServerMessage(error=str(e)), context.chat_mutator.chat.id)
        raise e


async def execution_mode_accept_code(
    context: AcceptCodeContext,
):
    pass


execution_mode = ExecutionMode(
    process_chat=execution_mode_process,
    accept_code=execution_mode_accept_code,
)
