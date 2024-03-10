import logging
from datetime import datetime
from typing import Type
from uuid import uuid4

from litellm import ModelResponse  # type: ignore

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.chat.convert_messages import convert_messages
from aiconsole.core.chat.execution_modes.utils.send_code import send_code
from aiconsole.core.chat.locations import ChatRef
from aiconsole.core.chat.types import AICMessage
from aiconsole.core.gpt.function_calls import OpenAISchema
from aiconsole.core.gpt.gpt_executor import GPTExecutor
from aiconsole.core.gpt.request import GPTRequest
from aiconsole.core.gpt.tool_definition import ToolDefinition, ToolFunctionDefinition
from aiconsole.core.gpt.types import (
    CLEAR_STR,
    EnforcedFunctionCall,
    EnforcedFunctionCallFuncSpec,
)

_log = logging.getLogger(__name__)


async def generate_response_message_with_code(
    chat_ref: ChatRef,
    agent: AICAgent,
    system_message: str,
    language_classes: list[Type[OpenAISchema]],
    enforced_language: Type[OpenAISchema] | None = None,
):
    executor = GPTExecutor()

    # Assumes an existing message group that was created for us
    chat = await chat_ref.get()
    last_message_group = chat.message_groups[-1]
    last_message_group_ref = chat_ref.message_groups[last_message_group.id]

    tools_requiring_closing_parenthesis: list[str] = []

    message_id = str(uuid4())
    await last_message_group_ref.messages.create(
        AICMessage(
            id=message_id,
            timestamp=datetime.now().isoformat(),
            content="",
        ),
    )

    message_ref = last_message_group_ref.messages[message_id]

    try:
        await message_ref.is_streaming.set(True)

        all_requested_formats: list[ToolDefinition] = []
        for message_group in chat.message_groups:
            for message in message_group.messages:
                if message.requested_format:
                    all_requested_formats.append(message.requested_format)

        async for chunk_or_clear in executor.execute(
            GPTRequest(
                system_message=system_message,
                gpt_mode=agent.gpt_mode,
                messages=[message for message in convert_messages(chat)],
                tools=[
                    *[
                        ToolDefinition(
                            type="function",
                            function=ToolFunctionDefinition(**language_cls.openai_schema()),
                        )
                        for language_cls in language_classes
                    ],
                    *all_requested_formats,
                ],
                tool_choice=(
                    EnforcedFunctionCall(
                        type="function", function=EnforcedFunctionCallFuncSpec(name=enforced_language.__name__)
                    )
                    if enforced_language
                    else None
                ),
                min_tokens=250,
                preferred_tokens=2000,
                temperature=0.2,
            )
        ):
            if chunk_or_clear == CLEAR_STR:
                await message_ref.content.set("")
                continue

            chunk: ModelResponse = chunk_or_clear

            # When does this happen?
            if not chunk.get("choices"):
                continue
            else:
                delta_content = chunk["choices"][0]["delta"].get("content")
                if delta_content:
                    await message_ref.content.append(delta_content)

                message_location = chat.get_message_location(message_id)
                if not message_location:
                    raise Exception(f"Message {message_id} should have been created")

                if executor.partial_response.choices[0].message.tool_calls and message_location.message.is_streaming:
                    await message_ref.is_streaming.set(False)

                await send_code(
                    executor.partial_response.choices[0].message.tool_calls,
                    message_ref,
                    tools_requiring_closing_parenthesis,
                    language_classes=language_classes,
                )

    finally:
        message_location = (await chat_ref.get()).get_message_location(message_id)

        if message_location and message_location.message.is_streaming:
            await message_ref.is_streaming.set(False)

        for tool_id in tools_requiring_closing_parenthesis:
            await message_ref.tool_calls[tool_id].code.append(")")

        # Finish streaming for all tool calls
        for tool_call in executor.partial_response.choices[0].message.tool_calls:
            tool_call_location = (await chat_ref.get()).get_tool_call_location(tool_call.id)
            if tool_call_location and tool_call_location.tool_call.is_streaming:
                await message_ref.tool_calls[tool_call.id].is_streaming.set(False)

        _log.debug(f"tools_requiring_closing_parenthesis: {tools_requiring_closing_parenthesis}")
