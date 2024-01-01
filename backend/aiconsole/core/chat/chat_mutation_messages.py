from aiconsole.api.websockets.outgoing_messages import BaseWSMessage
from aiconsole.core.gpt.types import GPTRole


class ChatMutationWSMessage(BaseWSMessage):
    request_id: str
    chat_id: str


class OpCreateMessageGroupWSMessage(ChatMutationWSMessage):
    message_group_id: str
    agent_id: str
    role: GPTRole
    task: str
    materials_ids: list[str]
    analysis: str


class OpDeleteMessageGroupWSMessage(ChatMutationWSMessage):
    message_group_id: str


class OpSetIsAnalysisInProgressWSMessage(ChatMutationWSMessage):
    is_analysis_in_progress: bool


# Message Groups - Task


class OpSetMessageGroupTaskWSMessage(ChatMutationWSMessage):
    message_group_id: str
    task: str


class OpAppendToMessageGroupTaskWSMessage(ChatMutationWSMessage):
    message_group_id: str
    task_delta: str


# Message Groups - Role


class OpSetMessageGroupRoleWSMessage(ChatMutationWSMessage):
    message_group_id: str
    role: GPTRole


class OpSetMessageGroupAgentIdWSMessage(ChatMutationWSMessage):
    message_group_id: str
    agent_id: str


# Message Groups - Materials


class OpSetMessageGroupMaterialsIdsWSMessage(ChatMutationWSMessage):
    message_group_id: str
    materials_ids: list[str]


class OpAppendToMessageGroupMaterialsIdsWSMessage(ChatMutationWSMessage):
    message_group_id: str
    material_id: str


# Message Groups - Analysis


class OpSetMessageGroupAnalysisWSMessage(ChatMutationWSMessage):
    message_group_id: str
    analysis: str


class OpAppendToMessageGroupAnalysisWSMessage(ChatMutationWSMessage):
    message_group_id: str
    analysis_delta: str


# Messages


class OpCreateMessageWSMessage(ChatMutationWSMessage):
    message_group_id: str
    message_id: str
    timestamp: str
    content: str = ""


class OpDeleteMessageWSMessage(ChatMutationWSMessage):
    message_id: str


# Messages - Content


class OpAppendToMessageContentWSMessage(ChatMutationWSMessage):
    message_id: str
    content_delta: str


class OpSetMessageContentWSMessage(ChatMutationWSMessage):
    message_id: str
    content: str


# Messages - Is streaming


class OpSetMessageIsStreamingWSMessage(ChatMutationWSMessage):
    message_id: str
    is_streaming: bool


# Tool Calls


class OpCreateToolCallWSMessage(ChatMutationWSMessage):
    message_id: str
    tool_call_id: str
    code: str = ""
    language: str = ""
    headline: str = ""
    output: str | None = None


class OpDeleteToolCallWSMessage(ChatMutationWSMessage):
    tool_call_id: str


# Tool Calls - Headline


class OpSetToolCallHeadlineWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    headline: str


class OpAppendToToolCallHeadlineWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    headline_delta: str


# Tool Calls - Code


class OpSetToolCallCodeWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    code: str


class OpAppendToToolCallCodeWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    code_delta: str


# Tool Calls - Language


class OpSetToolCallLanguageWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    language: str


# Tool Calls - Output


class OpSetToolCallOutputWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    output: str | None


class OpAppendToToolCallOutputWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    output_delta: str


# Tool Calls - Is streaming


class OpSetToolCallIsStreamingWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    is_streaming: bool


class OpSetToolCallIsExecutingWSMessage(ChatMutationWSMessage):
    tool_call_id: str
    is_executing: bool
