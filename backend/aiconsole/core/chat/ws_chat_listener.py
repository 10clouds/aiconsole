import asyncio

from aiconsole.core.chat.chat_listener import ChatListener
from aiconsole.core.chat.chat_mutation_messages import (
    OpAppendToMessageContentWSMessage,
    OpAppendToMessageGroupAnalysisWSMessage,
    OpAppendToMessageGroupMaterialsIdsWSMessage,
    OpAppendToMessageGroupTaskWSMessage,
    OpAppendToToolCallCodeWSMessage,
    OpAppendToToolCallHeadlineWSMessage,
    OpAppendToToolCallOutputWSMessage,
    OpCreateMessageGroupWSMessage,
    OpCreateMessageWSMessage,
    OpCreateToolCallWSMessage,
    OpDeleteMessageGroupWSMessage,
    OpDeleteMessageWSMessage,
    OpDeleteToolCallWSMessage,
    OpSetIsAnalysisInProgressWSMessage,
    OpSetMessageContentWSMessage,
    OpSetMessageGroupAgentIdWSMessage,
    OpSetMessageGroupAnalysisWSMessage,
    OpSetMessageGroupMaterialsIdsWSMessage,
    OpSetMessageGroupRoleWSMessage,
    OpSetMessageGroupTaskWSMessage,
    OpSetMessageIsStreamingWSMessage,
    OpSetToolCallCodeWSMessage,
    OpSetToolCallHeadlineWSMessage,
    OpSetToolCallIsExecutingWSMessage,
    OpSetToolCallIsStreamingWSMessage,
    OpSetToolCallLanguageWSMessage,
    OpSetToolCallOutputWSMessage,
)
from aiconsole.core.gpt.types import GPTRole
from pydantic import BaseModel


class WSChatListener(BaseModel):
    request_id: str
    chat_id: str

    def _send(self, coroutine) -> None:
        asyncio.run_coroutine_threadsafe(
            coroutine,
            asyncio.get_event_loop(),
        )

    def op_create_message_group(
        self,
        message_group_id: str,
        agent_id: str,
        role: GPTRole,
        task: str,
        materials_ids: list[str],
        analysis: str,
    ) -> None:
        self._send(
            OpCreateMessageGroupWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                agent_id=agent_id,
                role=role,
                task=task,
                materials_ids=materials_ids,
                analysis=analysis,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_delete_message_group(self, message_group_id: str) -> None:
        self._send(
            OpDeleteMessageGroupWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_set_is_analysis_in_progress(self, is_analysis_in_progress: bool) -> None:
        self._send(
            OpSetIsAnalysisInProgressWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                is_analysis_in_progress=is_analysis_in_progress,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Message Groups - Task

    def op_set_message_group_task(self, message_group_id: str, task: str) -> None:
        self._send(
            OpSetMessageGroupTaskWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                task=task,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_append_to_message_group_task(self, message_group_id: str, task_delta: str) -> None:
        self._send(
            OpAppendToMessageGroupTaskWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                task_delta=task_delta,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Message Groups - Role

    def op_set_message_group_role(self, message_group_id: str, role: GPTRole) -> None:
        self._send(
            OpSetMessageGroupRoleWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                role=role,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_set_message_group_agent_id(self, message_group_id: str, agent_id: str) -> None:
        self._send(
            OpSetMessageGroupAgentIdWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                agent_id=agent_id,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Message Groups - Materials

    def op_set_message_group_materials_ids(self, message_group_id: str, materials_ids: list[str]) -> None:
        self._send(
            OpSetMessageGroupMaterialsIdsWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                materials_ids=materials_ids,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_append_to_message_group_materials_ids(self, message_group_id: str, material_id: str) -> None:
        self._send(
            OpAppendToMessageGroupMaterialsIdsWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                material_id=material_id,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Message Groups - Analysis

    def op_set_message_group_analysis(self, message_group_id: str, analysis: str) -> None:
        self._send(
            OpSetMessageGroupAnalysisWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                analysis=analysis,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_append_to_message_group_analysis(self, message_group_id: str, analysis_delta: str) -> None:
        self._send(
            OpAppendToMessageGroupAnalysisWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_group_id=message_group_id,
                analysis_delta=analysis_delta,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Messages

    def op_create_message(self, message_group_id: str, message_id: str, timestamp: str, content: str):
        self._send(
            OpCreateMessageWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                timestamp=timestamp,
                message_group_id=message_group_id,
                message_id=message_id,
                content=content,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_delete_message(self, message_id: str):
        self._send(
            OpDeleteMessageWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_id=message_id,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Messages - Content

    def op_append_to_message_content(self, message_id: str, content_delta: str):
        self._send(
            OpAppendToMessageContentWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_id=message_id,
                content_delta=content_delta,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_set_message_content(self, message_id: str, content: str):
        self._send(
            OpSetMessageContentWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_id=message_id,
                content=content,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Messages - Is streaming
    def op_set_message_is_streaming(self, message_id: str, is_streaming: bool):
        self._send(
            OpSetMessageIsStreamingWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_id=message_id,
                is_streaming=is_streaming,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

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
        self._send(
            OpCreateToolCallWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                message_id=message_id,
                tool_call_id=tool_call_id,
                code=code,
                language=language,
                headline=headline,
                output=output,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_delete_tool_call(self, tool_call_id: str) -> None:
        self._send(
            OpDeleteToolCallWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Tool Calls - Headline

    def op_set_tool_call_headline(self, tool_call_id: str, headline: str) -> None:
        self._send(
            OpSetToolCallHeadlineWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                headline=headline,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_append_to_tool_call_headline(self, tool_call_id: str, headline_delta: str) -> None:
        self._send(
            OpAppendToToolCallHeadlineWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                headline_delta=headline_delta,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Tool Calls - Code

    def op_set_tool_call_code(self, tool_call_id: str, code: str) -> None:
        self._send(
            OpSetToolCallCodeWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                code=code,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_append_to_tool_call_code(self, tool_call_id: str, code_delta: str):
        self._send(
            OpAppendToToolCallCodeWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                code_delta=code_delta,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Tool Calls - Language

    def op_set_tool_call_language(self, tool_call_id: str, language: str) -> None:
        self._send(
            OpSetToolCallLanguageWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                language=language,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Tool Calls - Output

    def op_set_tool_call_output(self, tool_call_id: str, output: str | None) -> None:
        self._send(
            OpSetToolCallOutputWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                output=output,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_append_to_tool_call_output(self, tool_call_id: str, output_delta: str) -> None:
        self._send(
            OpAppendToToolCallOutputWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                output_delta=output_delta,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    # Tool Calls - Is streaming

    def op_set_tool_call_is_streaming(self, tool_call_id: str, is_streaming: bool) -> None:
        self._send(
            OpSetToolCallIsStreamingWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                is_streaming=is_streaming,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )

    def op_set_tool_call_is_executing(self, tool_call_id: str, is_executing: bool) -> None:
        self._send(
            OpSetToolCallIsExecutingWSMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                tool_call_id=tool_call_id,
                is_executing=is_executing,
            ).send_to_chat(
                chat_id=self.chat_id,
            )
        )
