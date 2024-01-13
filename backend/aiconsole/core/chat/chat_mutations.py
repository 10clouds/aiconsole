from typing import Literal

from pydantic import BaseModel

from aiconsole.core.code_running.code_interpreters.language import LanguageStr
from aiconsole.core.gpt.types import GPTRole


class LockAcquiredMutation(BaseModel):
    type: Literal["LockAcquiredMutation"] = "LockAcquiredMutation"
    lock_id: str


class LockReleasedMutation(BaseModel):
    type: Literal["LockReleasedMutation"] = "LockReleasedMutation"
    lock_id: str


class CreateMessageGroupMutation(BaseModel):
    type: Literal["CreateMessageGroupMutation"] = "CreateMessageGroupMutation"
    message_group_id: str
    agent_id: str
    username: str
    email: str
    role: GPTRole
    task: str
    materials_ids: list[str]
    analysis: str


class DeleteMessageGroupMutation(BaseModel):
    type: Literal["DeleteMessageGroupMutation"] = "DeleteMessageGroupMutation"
    message_group_id: str


class SetIsAnalysisInProgressMutation(BaseModel):
    type: Literal["SetIsAnalysisInProgressMutation"] = "SetIsAnalysisInProgressMutation"
    is_analysis_in_progress: bool


class SetTaskMessageGroupMutation(BaseModel):
    type: Literal["SetTaskMessageGroupMutation"] = "SetTaskMessageGroupMutation"
    message_group_id: str
    task: str


class AppendToTaskMessageGroupMutation(BaseModel):
    type: Literal["AppendToTaskMessageGroupMutation"] = "AppendToTaskMessageGroupMutation"
    message_group_id: str
    task_delta: str


class SetRoleMessageGroupMutation(BaseModel):
    type: Literal["SetRoleMessageGroupMutation"] = "SetRoleMessageGroupMutation"
    message_group_id: str
    role: GPTRole


class SetAgentIdMessageGroupMutation(BaseModel):
    type: Literal["SetAgentIdMessageGroupMutation"] = "SetAgentIdMessageGroupMutation"
    message_group_id: str
    agent_id: str


class SetMaterialsIdsMessageGroupMutation(BaseModel):
    type: Literal["SetMaterialsIdsMessageGroupMutation"] = "SetMaterialsIdsMessageGroupMutation"
    message_group_id: str
    materials_ids: list[str]


class AppendToMaterialsIdsMessageGroupMutation(BaseModel):
    type: Literal["AppendToMaterialsIdsMessageGroupMutation"] = "AppendToMaterialsIdsMessageGroupMutation"
    message_group_id: str
    material_id: str


class SetAnalysisMessageGroupMutation(BaseModel):
    type: Literal["SetAnalysisMessageGroupMutation"] = "SetAnalysisMessageGroupMutation"
    message_group_id: str
    analysis: str


class AppendToAnalysisMessageGroupMutation(BaseModel):
    type: Literal["AppendToAnalysisMessageGroupMutation"] = "AppendToAnalysisMessageGroupMutation"
    message_group_id: str
    analysis_delta: str


# Continuation of Mutation Classes


class CreateMessageMutation(BaseModel):
    type: Literal["CreateMessageMutation"] = "CreateMessageMutation"
    message_group_id: str
    message_id: str
    timestamp: str
    content: str


class DeleteMessageMutation(BaseModel):
    type: Literal["DeleteMessageMutation"] = "DeleteMessageMutation"
    message_id: str


class AppendToContentMessageMutation(BaseModel):
    type: Literal["AppendToContentMessageMutation"] = "AppendToContentMessageMutation"
    message_id: str
    content_delta: str


class SetContentMessageMutation(BaseModel):
    type: Literal["SetContentMessageMutation"] = "SetContentMessageMutation"
    message_id: str
    content: str


class SetIsStreamingMessageMutation(BaseModel):
    type: Literal["SetIsStreamingMessageMutation"] = "SetIsStreamingMessageMutation"
    message_id: str
    is_streaming: bool


class CreateToolCallMutation(BaseModel):
    type: Literal["CreateToolCallMutation"] = "CreateToolCallMutation"
    message_id: str
    tool_call_id: str
    code: str
    language: LanguageStr | None = None
    headline: str
    output: str | None = None


class DeleteToolCallMutation(BaseModel):
    type: Literal["DeleteToolCallMutation"] = "DeleteToolCallMutation"
    tool_call_id: str


class SetHeadlineToolCallMutation(BaseModel):
    type: Literal["SetHeadlineToolCallMutation"] = "SetHeadlineToolCallMutation"
    tool_call_id: str
    headline: str


class AppendToHeadlineToolCallMutation(BaseModel):
    type: Literal["AppendToHeadlineToolCallMutation"] = "AppendToHeadlineToolCallMutation"
    tool_call_id: str
    headline_delta: str


class SetCodeToolCallMutation(BaseModel):
    type: Literal["SetCodeToolCallMutation"] = "SetCodeToolCallMutation"
    tool_call_id: str
    code: str


class AppendToCodeToolCallMutation(BaseModel):
    type: Literal["AppendToCodeToolCallMutation"] = "AppendToCodeToolCallMutation"
    tool_call_id: str
    code_delta: str


class SetLanguageToolCallMutation(BaseModel):
    type: Literal["SetLanguageToolCallMutation"] = "SetLanguageToolCallMutation"
    tool_call_id: str
    language: LanguageStr


class SetOutputToolCallMutation(BaseModel):
    type: Literal["SetOutputToolCallMutation"] = "SetOutputToolCallMutation"
    tool_call_id: str
    output: str | None = None


class AppendToOutputToolCallMutation(BaseModel):
    type: Literal["AppendToOutputToolCallMutation"] = "AppendToOutputToolCallMutation"
    tool_call_id: str
    output_delta: str


class SetIsStreamingToolCallMutation(BaseModel):
    type: Literal["SetIsStreamingToolCallMutation"] = "SetIsStreamingToolCallMutation"
    tool_call_id: str
    is_streaming: bool


class SetIsExecutingToolCallMutation(BaseModel):
    type: Literal["SetIsExecutingToolCallMutation"] = "SetIsExecutingToolCallMutation"
    tool_call_id: str
    is_executing: bool


ChatMutation = (
    LockAcquiredMutation
    | LockReleasedMutation
    | CreateMessageGroupMutation
    | DeleteMessageGroupMutation
    | SetIsAnalysisInProgressMutation
    | SetTaskMessageGroupMutation
    | AppendToTaskMessageGroupMutation
    | SetRoleMessageGroupMutation
    | SetAgentIdMessageGroupMutation
    | SetMaterialsIdsMessageGroupMutation
    | AppendToMaterialsIdsMessageGroupMutation
    | SetAnalysisMessageGroupMutation
    | AppendToAnalysisMessageGroupMutation
    | CreateMessageMutation
    | DeleteMessageMutation
    | AppendToContentMessageMutation
    | SetContentMessageMutation
    | SetIsStreamingMessageMutation
    | CreateToolCallMutation
    | DeleteToolCallMutation
    | SetHeadlineToolCallMutation
    | AppendToHeadlineToolCallMutation
    | SetCodeToolCallMutation
    | AppendToCodeToolCallMutation
    | SetLanguageToolCallMutation
    | SetOutputToolCallMutation
    | AppendToOutputToolCallMutation
    | SetIsStreamingToolCallMutation
    | SetIsExecutingToolCallMutation
)
