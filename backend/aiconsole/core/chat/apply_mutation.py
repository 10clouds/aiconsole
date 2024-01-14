import logging
from datetime import datetime

from aiconsole.core.chat.chat_mutations import (
    AppendToAnalysisMessageGroupMutation,
    AppendToCodeToolCallMutation,
    AppendToContentMessageMutation,
    AppendToHeadlineToolCallMutation,
    AppendToMaterialsIdsMessageGroupMutation,
    AppendToOutputToolCallMutation,
    AppendToTaskMessageGroupMutation,
    ChatMutation,
    CreateMessageGroupMutation,
    CreateMessageMutation,
    CreateToolCallMutation,
    DeleteMessageGroupMutation,
    DeleteMessageMutation,
    DeleteToolCallMutation,
    SetAgentIdMessageGroupMutation,
    SetAnalysisMessageGroupMutation,
    SetCodeToolCallMutation,
    SetContentMessageMutation,
    SetHeadlineToolCallMutation,
    SetIsAnalysisInProgressMutation,
    SetIsExecutingToolCallMutation,
    SetIsStreamingMessageMutation,
    SetIsStreamingToolCallMutation,
    SetLanguageToolCallMutation,
    SetMaterialsIdsMessageGroupMutation,
    SetOutputToolCallMutation,
    SetRoleMessageGroupMutation,
    SetTaskMessageGroupMutation,
)
from aiconsole.core.chat.types import (
    AICMessage,
    AICMessageGroup,
    AICMessageLocation,
    AICToolCall,
    AICToolCallLocation,
    Chat,
)

_log = logging.getLogger(__name__)


def apply_mutation(chat: Chat, mutation: ChatMutation) -> None:
    """
    KEEEP THIS IN SYNC WITH FRONTEND applyMutation!

    Chat to which we received an exclusive write access.
    It provides modification methods which should be used instead of modifying the chat directly.
    """

    {
        CreateMessageGroupMutation.__name__: _handle_CreateMessageGroupMutation,
        DeleteMessageGroupMutation.__name__: _handle_DeleteMessageGroupMutation,
        SetIsAnalysisInProgressMutation.__name__: _handle_SetIsAnalysisInProgressMutation,
        SetTaskMessageGroupMutation.__name__: _handle_SetMessageGroupTaskMutation,
        AppendToTaskMessageGroupMutation.__name__: _handle_AppendToMessageGroupTaskMutation,
        SetRoleMessageGroupMutation.__name__: _handle_SetMessageGroupRoleMutation,
        SetAgentIdMessageGroupMutation.__name__: _handle_SetMessageGroupAgentIdMutation,
        SetMaterialsIdsMessageGroupMutation.__name__: _handle_SetMessageGroupMaterialsIdsMutation,
        AppendToMaterialsIdsMessageGroupMutation.__name__: _handle_AppendToMessageGroupMaterialsIdsMutation,
        SetAnalysisMessageGroupMutation.__name__: _handle_SetMessageGroupAnalysisMutation,
        AppendToAnalysisMessageGroupMutation.__name__: _handle_AppendToMessageGroupAnalysisMutation,
        CreateMessageMutation.__name__: _handle_CreateMessageMutation,
        DeleteMessageMutation.__name__: _handle_DeleteMessageMutation,
        SetContentMessageMutation.__name__: _handle_SetContentMessageMutation,
        AppendToContentMessageMutation.__name__: _handle_AppendToContentMessageMutation,
        SetIsStreamingMessageMutation.__name__: _handle_SetMessageIsStreamingMutation,
        CreateToolCallMutation.__name__: _handle_CreateToolCallMutation,
        DeleteToolCallMutation.__name__: _handle_DeleteToolCallMutation,
        SetHeadlineToolCallMutation.__name__: _handle_SetToolCallHeadlineMutation,
        AppendToHeadlineToolCallMutation.__name__: _handle_AppendToToolCallHeadlineMutation,
        SetCodeToolCallMutation.__name__: _handle_SetToolCallCodeMutation,
        AppendToCodeToolCallMutation.__name__: _handle_AppendToToolCallCodeMutation,
        SetLanguageToolCallMutation.__name__: _handle_SetToolCallLanguageMutation,
        SetOutputToolCallMutation.__name__: _handle_SetToolCallOutputMutation,
        AppendToOutputToolCallMutation.__name__: _handle_AppendToToolCallOutputMutation,
        SetIsStreamingToolCallMutation.__name__: _handle_SetToolCallIsStreamingMutation,
        SetIsExecutingToolCallMutation.__name__: _handle_SetIsExecutingToolCallMutation,
    }[mutation.__class__.__name__](chat, mutation)


# Handlers


def _handle_CreateMessageGroupMutation(chat: Chat, mutation: CreateMessageGroupMutation) -> AICMessageGroup:
    message_group = AICMessageGroup(
        id=mutation.message_group_id,
        agent_id=mutation.agent_id,
        role=mutation.role,
        task=mutation.task,
        materials_ids=mutation.materials_ids,
        analysis=mutation.analysis,
        messages=[],
    )

    chat.message_groups.append(message_group)

    return message_group


def _handle_DeleteMessageGroupMutation(chat, mutation: DeleteMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    chat.message_groups = [group for group in chat.message_groups if group.id != message_group.id]


def _handle_SetIsAnalysisInProgressMutation(chat, mutation: SetIsAnalysisInProgressMutation) -> None:
    chat.is_analysis_in_progress = mutation.is_analysis_in_progress


def _handle_SetMessageGroupTaskMutation(chat, mutation: SetTaskMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.task = mutation.task


def _handle_AppendToMessageGroupTaskMutation(chat, mutation: AppendToTaskMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.task += mutation.task_delta


def _handle_SetMessageGroupRoleMutation(chat, mutation: SetRoleMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.role = mutation.role


def _handle_SetMessageGroupAgentIdMutation(chat, mutation: SetAgentIdMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.agent_id = mutation.agent_id

    if mutation.agent_id == "user":
        message_group.role = "user"
    else:
        message_group.role = "assistant"


def _handle_SetMessageGroupMaterialsIdsMutation(chat, mutation: SetMaterialsIdsMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.materials_ids = mutation.materials_ids


def _handle_AppendToMessageGroupMaterialsIdsMutation(chat, mutation: AppendToMaterialsIdsMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.materials_ids.append(mutation.material_id)


def _handle_SetMessageGroupAnalysisMutation(chat, mutation: SetAnalysisMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.analysis = mutation.analysis


def _handle_AppendToMessageGroupAnalysisMutation(chat, mutation: AppendToAnalysisMessageGroupMutation) -> None:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message_group.analysis += mutation.analysis_delta


def _handle_CreateMessageMutation(chat, mutation: CreateMessageMutation) -> AICMessage:
    message_group = _get_message_group(chat, mutation.message_group_id)
    message = AICMessage(
        id=mutation.message_id,
        content=mutation.content,
        timestamp=datetime.now().isoformat(),
        tool_calls=[],
    )
    message_group.messages.append(message)
    return message


def _handle_DeleteMessageMutation(chat, mutation: DeleteMessageMutation) -> None:
    message_location = _get_message_location(chat, mutation.message_id)
    message_location.message_group.messages = [
        m for m in message_location.message_group.messages if m.id != mutation.message_id
    ]

    # Remove message group if it's empty
    if not message_location.message_group.messages:
        chat.message_groups = [group for group in chat.message_groups if group.id != message_location.message_group.id]


def _handle_SetContentMessageMutation(chat, mutation: SetContentMessageMutation) -> None:
    _get_message_location(chat, mutation.message_id).message.content = mutation.content


def _handle_AppendToContentMessageMutation(chat, mutation: AppendToContentMessageMutation) -> None:
    _get_message_location(chat, mutation.message_id).message.content += mutation.content_delta


def _handle_SetMessageIsStreamingMutation(chat, mutation: SetIsStreamingMessageMutation) -> None:
    _get_message_location(chat, mutation.message_id).message.is_streaming = mutation.is_streaming


def _handle_CreateToolCallMutation(chat, mutation: CreateToolCallMutation) -> AICToolCall:
    message = _get_message_location(chat, mutation.message_id).message
    tool_call = AICToolCall(
        id=mutation.tool_call_id,
        language=mutation.language,
        code=mutation.code,
        headline=mutation.headline,
        output=mutation.output,
    )
    message.tool_calls.append(tool_call)
    return tool_call


def _handle_DeleteToolCallMutation(chat, mutation: DeleteToolCallMutation) -> None:
    tool_call = _get_tool_call_location(chat, mutation.tool_call_id)
    tool_call.message.tool_calls = [tc for tc in tool_call.message.tool_calls if tc.id != mutation.tool_call_id]

    # Remove message if it's empty
    if not tool_call.message.tool_calls and not tool_call.message.content:
        tool_call.message_group.messages = [
            m for m in tool_call.message_group.messages if m.id != tool_call.message.id
        ]

    # Remove message group if it's empty
    if not tool_call.message_group.messages:
        chat.message_groups = [group for group in chat.message_groups if group.id != tool_call.message_group.id]


def _handle_SetToolCallHeadlineMutation(chat, mutation: SetHeadlineToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.headline = mutation.headline


def _handle_AppendToToolCallHeadlineMutation(chat, mutation: AppendToHeadlineToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.headline += mutation.headline_delta


def _handle_SetToolCallCodeMutation(chat, mutation: SetCodeToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.code = mutation.code


def _handle_AppendToToolCallCodeMutation(chat, mutation: AppendToCodeToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.code += mutation.code_delta


def _handle_SetToolCallLanguageMutation(chat, mutation: SetLanguageToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.language = mutation.language


def _handle_SetToolCallOutputMutation(chat, mutation: SetOutputToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.output = mutation.output


def _handle_AppendToToolCallOutputMutation(chat, mutation: AppendToOutputToolCallMutation) -> None:
    tool_call = _get_tool_call_location(chat, mutation.tool_call_id).tool_call
    if tool_call.output is None:
        tool_call.output = ""
    tool_call.output += mutation.output_delta


def _handle_SetToolCallIsStreamingMutation(chat, mutation: SetIsStreamingToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.is_streaming = mutation.is_streaming


def _handle_SetIsExecutingToolCallMutation(chat, mutation: SetIsExecutingToolCallMutation) -> None:
    _get_tool_call_location(chat, mutation.tool_call_id).tool_call.is_executing = mutation.is_executing


# Utils


def _get_message_group(chat: Chat, message_group_id: str) -> AICMessageGroup:
    message_group = chat.get_message_group(message_group_id=message_group_id)

    if not message_group:
        raise ValueError(f"Message group with id {message_group_id} not found")

    return message_group


def _get_message_location(chat: Chat, message_id: str) -> AICMessageLocation:
    message_location = chat.get_message_location(message_id=message_id)

    if not message_location:
        raise ValueError(f"Message with id {message_id} not found")

    return message_location


def _get_tool_call_location(chat: Chat, tool_call_id: str) -> AICToolCallLocation:
    tool_call_location = chat.get_tool_call_location(tool_call_id=tool_call_id)

    if not tool_call_location:
        raise ValueError(f"Tool call with id {tool_call_id} not found")

    return tool_call_location
