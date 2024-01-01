from aiconsole.core.gpt.types import GPTRole


from typing import Protocol, runtime_checkable


@runtime_checkable
class ChatListener(Protocol):
    # Chat

    def op_set_is_analysis_in_progress(self, is_analysis_in_progress: bool) -> None:
        ...

    # Message Groups

    def op_create_message_group(
        self,
        message_group_id: str,
        agent_id: str,
        role: GPTRole,
        task: str,
        materials_ids: list[str],
        analysis: str,
    ) -> None:
        ...

    def op_delete_message_group(self, message_group_id: str) -> None:
        ...

    # Message Groups - Task

    def op_set_message_group_task(self, message_group_id: str, task: str) -> None:
        ...

    def op_append_to_message_group_task(self, message_group_id: str, task_delta: str) -> None:
        ...

    # Message Groups - Role

    def op_set_message_group_role(self, message_group_id: str, role: GPTRole) -> None:
        ...

    def op_set_message_group_agent_id(self, message_group_id: str, agent_id: str) -> None:
        ...

    # Message Groups - Materials

    def op_set_message_group_materials_ids(self, message_group_id: str, materials_ids: list[str]) -> None:
        ...

    def op_append_to_message_group_materials_ids(self, message_group_id: str, material_id: str) -> None:
        ...

    # Message Groups - Analysis

    def op_set_message_group_analysis(self, message_group_id: str, analysis: str) -> None:
        ...

    def op_append_to_message_group_analysis(self, message_group_id: str, analysis_delta: str) -> None:
        ...

    # Messages

    def op_create_message(self, message_group_id: str, message_id: str, timestamp: str, content: str):
        # await UpdateMessageWSMessage().send_to_chat(context.chat.id)
        ...

    def op_delete_message(self, message_id: str):
        ...

    # Messages - Content

    def op_append_to_message_content(self, message_id: str, content_delta: str):
        ...

    def op_set_message_content(self, message_id: str, content: str):
        ...

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
        ...

    def op_delete_tool_call(self, tool_call_id: str) -> None:
        ...

    # Tool Calls - Headline

    def op_set_tool_call_headline(self, tool_call_id: str, headline: str) -> None:
        ...

    def op_append_to_tool_call_headline(self, tool_call_id: str, headline_delta: str) -> None:
        ...

    # Tool Calls - Code

    def op_set_tool_call_code(self, tool_call_id: str, code: str) -> None:
        ...

    def op_append_to_tool_call_code(self, tool_call_id: str, code_delta: str):
        ...

    # Messages - Is streaming
    def op_set_message_is_streaming(self, message_id: str, is_streaming: bool):
        ...

    # Tool Calls - Language

    def op_set_tool_call_language(self, tool_call_id: str, language: str) -> None:
        ...

    # Tool Calls - Output

    def op_set_tool_call_output(self, tool_call_id: str, output: str | None) -> None:
        ...

    def op_append_to_tool_call_output(self, tool_call_id: str, output_delta: str) -> None:
        ...

    # Tool Calls - Is streaming

    def op_set_tool_call_is_streaming(self, tool_call_id: str, is_streaming: bool) -> None:
        ...

    def op_set_tool_call_is_executing(self, tool_call_id: str, is_executing: bool) -> None:
        ...
