import logging
from typing import cast

from aiconsole.core.chat.locations import MessageRef
from aiconsole.core.chat.types import AICToolCall
from aiconsole.core.code_running.code_interpreters.language import LanguageStr
from aiconsole.core.code_running.code_interpreters.language_map import language_map
from aiconsole.core.gpt.partial import GPTPartialToolsCall

_log = logging.getLogger(__name__)


def tool_name_to_language(name: str) -> str:
    if name.endswith("_tool"):
        return name[:-5]

    raise Exception(f"Unable to convert name {name} to language")


async def send_code(
    tool_calls: list[GPTPartialToolsCall],
    message_ref: MessageRef,
    tools_requiring_closing_parenthesis,
    language_classes: list[type],
):
    for index, tool_call in enumerate(tool_calls):
        default_language = LanguageStr(tool_name_to_language(language_classes[0].__name__))

        # All tool calls with lower indexes are finished
        prev_tool = tool_calls[index - 1] if index > 0 else None

        if prev_tool:
            prev_tool_mutator = message_ref.tool_calls[prev_tool.id]

            if prev_tool.id in tools_requiring_closing_parenthesis:
                await prev_tool_mutator.code.append(")")
                tools_requiring_closing_parenthesis.remove(prev_tool.id)

            tool_call_mutator = message_ref.tool_calls[prev_tool.id]
            if tool_call_mutator.is_streaming.get():
                await prev_tool_mutator.is_streaming.set(False)

        tool_call_mutator = message_ref.tool_calls[tool_call.id]

        if not tool_call_mutator.exists():
            await message_ref.tool_calls.create(
                AICToolCall(
                    id=tool_call.id,
                    code="",
                    headline="",
                    language=None,
                    output=None,
                    is_streaming=True,
                    is_executing=False,
                    is_successful=False,
                ),
            )

        async def send_language_if_needed(lang: LanguageStr):
            if tool_call_mutator.language.get() is None:
                await tool_call_mutator.language.set(lang)

        async def send_headline_delta_for_headline(headline: str):
            if not headline.startswith(await tool_call_mutator.headline.get()):
                _log.warning(f"Reseting headline to: {headline}")
                await tool_call_mutator.headline.set(headline)
            else:
                start_index = len(await tool_call_mutator.headline.get())
                headline_delta = headline[start_index:]

                if headline_delta:
                    await tool_call_mutator.headline.append(headline_delta)

        async def send_code_delta_for_code(code: str):
            if not code.startswith(await tool_call_mutator.code.get()):
                _log.warning(f"Reseting code, code={repr(code)} original={repr(tool_call_mutator.code.get())}")
                await tool_call_mutator.code.set(code)
            else:
                start_index = len(await tool_call_mutator.code.get())
                code_delta = code[start_index:]

                if code_delta:
                    await tool_call_mutator.code.append(code_delta)

        if tool_call.type == "function":
            function_call = tool_call.function

            if not function_call.arguments:
                continue

            if function_call.name in [language_cls.__name__ for language_cls in language_classes]:
                # Languge is in the name of the function call

                languages = language_map.keys()

                if tool_call_mutator.language.get() is None and function_call.name in languages:
                    await send_language_if_needed(cast(LanguageStr, function_call.name))

                code = None
                headline = None

                if function_call.arguments_dict:
                    code = function_call.arguments_dict.get("code", None)
                    headline = function_call.arguments_dict.get("headline", None)
                else:
                    # Sometimes we don't have a dict, but it's still a json string

                    if not function_call.arguments.startswith("{"):
                        code = function_call.arguments

                if code:
                    await send_language_if_needed(default_language)
                    await send_code_delta_for_code(code)

                if headline:
                    await send_headline_delta_for_headline(headline)
            else:
                # We have a direct function call, without specifying the language

                await send_language_if_needed(default_language)

                if function_call.arguments_dict:
                    # ok we have a dict, those are probably arguments and the name of the function call is the name of the function

                    arguments_materialised = [
                        f"{key}={repr(value)}" for key, value in function_call.arguments_dict.items()
                    ]
                    code = f"{function_call.name}({', '.join(arguments_materialised)})"

                    await send_code_delta_for_code(code)
                else:
                    # We have a string in the arguments, thats probably the code
                    await send_code_delta_for_code(function_call.arguments)
