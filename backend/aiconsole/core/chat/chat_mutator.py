from datetime import datetime
from uuid import uuid4
from aiconsole.core.chat.chat_listener import ChatListener
from aiconsole.core.chat.types import AICMessage, AICMessageGroup, AICToolCall, Chat, AICMessageInfo, AICToolCallInfo
from aiconsole.core.code_running.code_interpreters.language_map import LanguageStr
from aiconsole.core.gpt.types import GPTRole
from pydantic import BaseModel


class ChatMutator(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    """
    Chat to which we received an exclusive write access.
    It provides modification methods which should be used instead of modifying the chat directly.
    """

    chat: Chat
    listener: ChatListener

    # Message Groups

    def op_create_message_group(
        self,
        message_group_id: str,
        agent_id: str,
        role: GPTRole,
        task: str,
        materials_ids: list[str],
        analysis: str,
    ) -> AICMessageGroup:
        message_group = AICMessageGroup(
            id=message_group_id,
            agent_id=agent_id,
            role=role,
            task=task,
            materials_ids=materials_ids,
            analysis=analysis,
            messages=[],
        )

        self.chat.message_groups.append(message_group)

        self.listener.op_create_message_group(
            message_group_id=message_group_id,
            agent_id=agent_id,
            role=role,
            task=task,
            materials_ids=materials_ids,
            analysis=analysis,
        )

        return message_group

    def op_delete_message_group(self, message_group_id: str) -> None:
        message_group = self._get_message_group(message_group_id)
        self.chat.message_groups = [group for group in self.chat.message_groups if group.id != message_group.id]
        self.listener.op_delete_message_group(message_group_id=message_group_id)

    def op_set_is_analysis_in_progress(self, is_analysis_in_progress: bool) -> None:
        self.chat.is_analysis_in_progress = is_analysis_in_progress
        self.listener.op_set_is_analysis_in_progress(is_analysis_in_progress=is_analysis_in_progress)

    # Message Groups - Task

    def op_set_message_group_task(self, message_group_id: str, task: str) -> None:
        self._get_message_group(message_group_id).task = task
        self.listener.op_set_message_group_task(message_group_id=message_group_id, task=task)

    def op_append_to_message_group_task(self, message_group_id: str, task_delta: str) -> None:
        self._get_message_group(message_group_id).task += task_delta
        self.listener.op_append_to_message_group_task(message_group_id=message_group_id, task_delta=task_delta)

    # Message Groups - Role

    def op_set_message_group_role(self, message_group_id: str, role: GPTRole) -> None:
        self._get_message_group(message_group_id).role = role
        self.listener.op_set_message_group_role(message_group_id=message_group_id, role=role)

    def op_set_message_group_agent_id(self, message_group_id: str, agent_id: str) -> None:
        self._get_message_group(message_group_id).agent_id = agent_id
        self.listener.op_set_message_group_agent_id(message_group_id=message_group_id, agent_id=agent_id)

    # Message Groups - Materials

    def op_set_message_group_materials_ids(self, message_group_id: str, materials_ids: list[str]) -> None:
        self._get_message_group(message_group_id).materials_ids = materials_ids
        self.listener.op_set_message_group_materials_ids(
            message_group_id=message_group_id, materials_ids=materials_ids
        )

    def op_append_to_message_group_materials_ids(self, message_group_id: str, material_id: str) -> None:
        self._get_message_group(message_group_id).materials_ids.append(material_id)
        self.listener.op_append_to_message_group_materials_ids(
            message_group_id=message_group_id, material_id=material_id
        )

    # Message Groups - Analysis
    def op_set_message_group_analysis(self, message_group_id: str, analysis: str) -> None:
        self._get_message_group(message_group_id).analysis = analysis
        self.listener.op_set_message_group_analysis(message_group_id=message_group_id, analysis=analysis)

    def op_append_to_message_group_analysis(self, message_group_id: str, analysis_delta: str) -> None:
        self._get_message_group(message_group_id).analysis += analysis_delta
        self.listener.op_append_to_message_group_analysis(
            message_group_id=message_group_id, analysis_delta=analysis_delta
        )

    # Messages
    def op_create_message(self, message_group_id: str, message_id: str, timestamp: str, content: str) -> AICMessage:
        message_group = self._get_message_group(message_group_id)

        message = AICMessage(id=message_id, content=content, tool_calls=[], timestamp=datetime.now().isoformat())

        message_group.messages.append(message)

        self.listener.op_create_message(
            message_group_id=message_group_id,
            message_id=message_id,
            timestamp=timestamp,
            content=content,
        )

        return message

    def op_delete_message(self, message_id: str):
        message = self._get_message(message_id)
        message.message_group.messages = [m for m in message.message_group.messages if m.id != message_id]
        self.listener.op_delete_message(message_id=message_id)

    # Messages - Content
    def op_set_message_content(self, message_id: str, content: str):
        self._get_message(message_id).message.content = content
        self.listener.op_set_message_content(message_id=message_id, content=content)

    def op_append_to_message_content(self, message_id: str, content_delta: str):
        self._get_message(message_id).message.content += content_delta
        self.listener.op_append_to_message_content(message_id=message_id, content_delta=content_delta)

    # Messages - Is streaming
    def op_set_message_is_streaming(self, message_id: str, is_streaming: bool):
        self._get_message(message_id).message.is_streaming = is_streaming
        self.listener.op_set_message_is_streaming(message_id=message_id, is_streaming=is_streaming)

    # Tool Calls

    def op_create_tool_call(
        self,
        message_id: str,
        tool_call_id: str,
        code: str = "",
        language: LanguageStr | None = None,
        headline: str = "",
        output: str | None = None,
    ) -> AICToolCall:
        message = self._get_message(message_id).message

        tool_call = AICToolCall(
            id=tool_call_id,
            language=language,
            code=code,
            headline=headline,
            output=output,
        )

        message.tool_calls.append(tool_call)

        self.listener.op_create_tool_call(
            message_id=message_id,
            tool_call_id=tool_call_id,
        )

        return tool_call

    def op_delete_tool_call(self, tool_call_id: str) -> None:
        tool_call = self._get_tool_call(tool_call_id)
        tool_call.message.tool_calls = [tc for tc in tool_call.message.tool_calls if tc.id != tool_call_id]
        self.listener.op_delete_tool_call(tool_call_id=tool_call_id)

    # Tool Calls - Headline

    def op_set_tool_call_headline(self, tool_call_id: str, headline: str) -> None:
        self._get_tool_call(tool_call_id).tool_call.headline = headline
        self.listener.op_set_tool_call_headline(tool_call_id=tool_call_id, headline=headline)

    def op_append_to_tool_call_headline(self, tool_call_id: str, headline_delta: str) -> None:
        self._get_tool_call(tool_call_id).tool_call.headline += headline_delta
        self.listener.op_append_to_tool_call_headline(tool_call_id=tool_call_id, headline_delta=headline_delta)

    # Tool Calls - Code

    def op_set_tool_call_code(self, tool_call_id: str, code: str) -> None:
        self._get_tool_call(tool_call_id).tool_call.code = code
        self.listener.op_set_tool_call_code(tool_call_id=tool_call_id, code=code)

    def op_append_to_tool_call_code(self, tool_call_id: str, code_delta: str):
        self._get_tool_call(tool_call_id).tool_call.code += code_delta
        self.listener.op_append_to_tool_call_code(tool_call_id=tool_call_id, code_delta=code_delta)

    # Tool Calls - Language

    def op_set_tool_call_language(self, tool_call_id: str, language: LanguageStr) -> None:
        self._get_tool_call(tool_call_id).tool_call.language = language
        self.listener.op_set_tool_call_language(tool_call_id=tool_call_id, language=language)

    # Tool Calls - Output

    def op_set_tool_call_output(self, tool_call_id: str, output: str | None) -> None:
        self._get_tool_call(tool_call_id).tool_call.output = output
        self.listener.op_set_tool_call_output(tool_call_id=tool_call_id, output=output)

    def op_append_to_tool_call_output(self, tool_call_id: str, output_delta: str) -> None:
        tool_call = self._get_tool_call(tool_call_id).tool_call
        if tool_call.output is None:
            tool_call.output = ""
        tool_call.output += output_delta
        self.listener.op_append_to_tool_call_output(tool_call_id=tool_call_id, output_delta=output_delta)

    # Tool Calls - Is streaming

    def op_set_tool_call_is_streaming(self, tool_call_id: str, is_streaming: bool) -> None:
        self._get_tool_call(tool_call_id).tool_call.is_streaming = is_streaming
        self.listener.op_set_tool_call_is_streaming(tool_call_id=tool_call_id, is_streaming=is_streaming)

    def op_set_tool_call_is_executing(self, tool_call_id: str, is_executing: bool) -> None:
        self._get_tool_call(tool_call_id).tool_call.is_executing = is_executing
        self.listener.op_set_tool_call_is_executing(tool_call_id=tool_call_id, is_executing=is_executing)

    # Utils

    def _get_message_group(self, message_group_id: str) -> AICMessageGroup:
        message_group = self.chat.get_message_group(message_group_id=message_group_id)

        if not message_group:
            raise ValueError(f"Message group with id {message_group_id} not found")

        return message_group

    def _get_message(self, message_id: str) -> AICMessageInfo:
        message = self.chat.get_message(message_id=message_id)

        if not message:
            raise ValueError(f"Message with id {message_id} not found")

        return message

    def _get_tool_call(self, tool_call_id: str) -> AICToolCallInfo:
        tool_call = self.chat.get_tool_call(tool_call_id=tool_call_id)

        if not tool_call:
            raise ValueError(f"Tool call with id {tool_call_id} not found")

        return tool_call
