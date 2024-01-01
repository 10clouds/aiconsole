from aiconsole.core.chat.chat_listener import ChatListener
from aiconsole.core.gpt.types import GPTRole


class PrintingChatListener(ChatListener):
    def op_create_message_group(
        self,
        message_group_id: str,
        agent_id: str,
        role: GPTRole,
        task: str,
        materials_ids: list[str],
        analysis: str,
    ) -> None:
        print(
            f"op_create_message_group: {message_group_id=}, {agent_id=}, {role=}, {task=}, {materials_ids=}, {analysis=}"
        )

    def op_delete_message_group(self, message_group_id: str) -> None:
        print(f"op_delete_message_group: {message_group_id=}")

    def op_set_is_analysis_in_progress(self, is_analysis_in_progress: bool) -> None:
        print(f"op_set_is_analysis_in_progress: {is_analysis_in_progress=}")

    # Message Groups - Task

    def op_set_message_group_task(self, message_group_id: str, task: str) -> None:
        print(f"op_set_message_group_task: {message_group_id=}, {task=}")

    def op_append_to_message_group_task(self, message_group_id: str, task_delta: str) -> None:
        print(f"op_append_to_message_group_task: {message_group_id=}, {task_delta=}")

    # Message Groups - Role

    def op_set_message_group_role(self, message_group_id: str, role: GPTRole) -> None:
        print(f"op_set_message_group_role: {message_group_id=}, {role=}")

    def op_set_message_group_agent_id(self, message_group_id: str, agent_id: str) -> None:
        print(f"op_set_message_group_agent_id: {message_group_id=}, {agent_id=}")

    # Message Groups - Materials

    def op_set_message_group_materials_ids(self, message_group_id: str, materials_ids: list[str]) -> None:
        print(f"op_set_message_group_materials_ids: {message_group_id=}, {materials_ids=}")

    def op_append_to_message_group_materials_ids(self, message_group_id: str, material_id: str) -> None:
        print(f"op_append_to_message_group_materials_ids: {message_group_id=}, {material_id=}")

    # Message Groups - Analysis

    def op_set_message_group_analysis(self, message_group_id: str, analysis: str) -> None:
        print(f"op_set_message_group_analysis: {message_group_id=}, {analysis=}")

    def op_append_to_message_group_analysis(self, message_group_id: str, analysis_delta: str) -> None:
        print(f"op_append_to_message_group_analysis: {message_group_id=}, {analysis_delta=}")

    # Messages

    def op_create_message(self, message_group_id: str, message_id: str, content):
        print(f"op_create_message: {message_group_id=}, {message_id=}, {content=}")

    def op_delete_message(self, message_id: str):
        print(f"op_delete_message: {message_id=}")

    # Messages - Content

    def op_append_to_message_content(self, message_id: str, content_delta: str):
        print(f"op_append_to_message_content: {message_id=}, {content_delta=}")

    def op_set_message_content(self, message_id: str, content: str):
        print(f"op_set_message_content: {message_id=}, {content=}")

    # Messages - Is streaming
    def op_set_message_is_streaming(self, message_id: str, is_streaming: bool):
        print(f"op_set_message_is_streaming: {message_id=}, {is_streaming=}")

    # Tool Calls

    def op_create_tool_call(
        self,
        message_id: str,
        tool_call_id: str,
        code: str = "",
        language: str = "",
        headline: str = "",
        output: str | None = None,
    ) -> None:
        print(f"op_create_tool_call: {message_id=}, {tool_call_id=}, {code=}, {language=}, {headline=}, {output=}")

    def op_delete_tool_call(self, tool_call_id: str) -> None:
        print(f"op_delete_tool_call: {tool_call_id=}")

    # Tool Calls - Headline

    def op_set_tool_call_headline(self, tool_call_id: str, headline: str) -> None:
        print(f"op_set_tool_call_headline: {tool_call_id=}, {headline=}")

    def op_append_to_tool_call_headline(self, tool_call_id: str, headline_delta: str) -> None:
        print(f"op_append_to_tool_call_headline: {tool_call_id=}, {headline_delta=}")

    # Tool Calls - Code

    def op_set_tool_call_code(self, tool_call_id: str, code: str) -> None:
        print(f"op_set_tool_call_code: {tool_call_id=}, {code=}")

    def op_append_to_tool_call_code(self, tool_call_id: str, code_delta: str):
        print(f"op_append_to_tool_call_code: {tool_call_id=}, {code_delta=}")

    # Tool Calls - Language

    def op_set_tool_call_language(self, tool_call_id: str, language: str) -> None:
        print(f"op_set_tool_call_language: {tool_call_id=}, {language=}")

    # Tool Calls - Output

    def op_set_tool_call_output(self, tool_call_id: str, output: str | None) -> None:
        print(f"op_set_tool_call_output: {tool_call_id=}, {output=}")

    def op_append_to_tool_call_output(self, tool_call_id: str, output_delta: str) -> None:
        print(f"op_append_to_tool_call_output: {tool_call_id=}, {output_delta=}")

    # Tool Calls - Is streaming

    def op_set_tool_call_is_streaming(self, tool_call_id: str, is_streaming: bool) -> None:
        print(f"op_set_tool_call_is_streaming: {tool_call_id=}, {is_streaming=}")

    def op_set_tool_call_is_executing(self, tool_call_id: str, is_executing: bool) -> None:
        print(f"op_set_tool_call_is_executing: {tool_call_id=}, {is_executing=}")
