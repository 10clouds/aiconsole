import logging
from contextlib import asynccontextmanager

from aiconsole.core.assets.materials.material import AICMaterial
from aiconsole.core.chat.locations import ToolCallRef
from aiconsole.core.code_running.code_interpreters.base_code_interpreter import (
    CodeExecutionError,
)
from aiconsole.core.code_running.run_code import run_in_code_interpreter
from aiconsole.core.settings.settings import settings

_log = logging.getLogger(__name__)


@asynccontextmanager
async def tool_call_executing(tool_call_ref: ToolCallRef):
    try:
        await tool_call_ref.is_executing.set(True)
        yield
    finally:
        await tool_call_ref.is_executing.set(False)


async def run_code(
    tool_call_ref: ToolCallRef,
    materials: list[AICMaterial],
):
    assert tool_call_ref.parent_collection.parent is not None

    tool_call = await tool_call_ref.get()
    chat_id = tool_call_ref.parent_collection.parent.parent_collection.parent.parent_collection.parent.id

    async with tool_call_executing(tool_call_ref):
        await tool_call_ref.output.set("")
        await tool_call_ref.is_successful.set(False)
        assert tool_call.language is not None

        output_length = 0
        TOOL_CALL_OUTPUT_LIMIT = settings().unified_settings.tool_call_output_limit

        if tool_call.language is None:
            logging.error(f"Tool call {(await tool_call_ref.get()).id} has no language specified.")
            return

        try:
            async for token in run_in_code_interpreter(tool_call.language, chat_id, tool_call.code, materials):

                new_output_length = output_length + len(token)

                if TOOL_CALL_OUTPUT_LIMIT is None or new_output_length <= TOOL_CALL_OUTPUT_LIMIT:
                    await tool_call_ref.output.append(token)

                    output_length = new_output_length
                else:
                    await tool_call_ref.output.append("\n[Output truncated due to limit]")
                    break

                await tool_call_ref.output.append(token)

        except CodeExecutionError as e:
            _log.error(f"Code execution error for tool call {tool_call_ref.id}: {e}")

        await tool_call_ref.is_successful.set(True)
