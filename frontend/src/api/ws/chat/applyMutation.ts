import { AICChat, getMessageGroup, getMessageLocation, getToolCallLocation } from '@/types/assets/chatTypes';
import { ChatMutation } from '@/api/ws/chat/chatMutations';
import { MessageBuffer } from '@/utils/common/MessageBuffer';

/**
 * KEEEP THIS IN SYNC WITH BACKEND apply_mutation!
 */
export function applyMutation(chat: AICChat, mutation: ChatMutation, messageBuffer?: MessageBuffer) {
  switch (mutation.type) {
    case 'LockAcquiredMutation':
      chat.lock_id = mutation.lock_id;
      break;
    case 'LockReleasedMutation':
      chat.lock_id = undefined;
      break;
    case 'CreateMessageGroupMutation':
      chat.message_groups.push({
        id: mutation.message_group_id,
        actor_id: mutation.actor_id,
        role: mutation.role,
        task: mutation.task,
        materials_ids: mutation.materials_ids,
        analysis: mutation.analysis,
        messages: [],
      });
      break;
    case 'DeleteMessageGroupMutation': {
      const message_group = getMessageGroup(chat, mutation.message_group_id);
      chat.message_groups = chat.message_groups.filter((group) => group.id !== message_group.id);
      break;
    }
    case 'SetIsAnalysisInProgressMutation':
      chat.is_analysis_in_progress = mutation.is_analysis_in_progress;
      break;
    case 'SetTaskMessageGroupMutation':
      getMessageGroup(chat, mutation.message_group_id).task = mutation.task;
      break;
    case 'AppendToTaskMessageGroupMutation':
      getMessageGroup(chat, mutation.message_group_id).task += mutation.task_delta;
      break;
    case 'SetRoleMessageGroupMutation':
      getMessageGroup(chat, mutation.message_group_id).role = mutation.role;
      break;
    case 'SetActorIdMessageGroupMutation': {
      const messageGroup = getMessageGroup(chat, mutation.message_group_id);
      messageGroup.actor_id = mutation.actor_id;
      if (mutation.actor_id.type === 'user') {
        messageGroup.role = 'user';
      } else {
        messageGroup.role = 'assistant';
      }
      break;
    }
    case 'SetMaterialsIdsMessageGroupMutation':
      getMessageGroup(chat, mutation.message_group_id).materials_ids = mutation.materials_ids;
      break;
    case 'AppendToMaterialsIdsMessageGroupMutation':
      getMessageGroup(chat, mutation.message_group_id).materials_ids.push(mutation.material_id);
      break;
    case 'SetAnalysisMessageGroupMutation':
      getMessageGroup(chat, mutation.message_group_id).analysis = mutation.analysis;
      break;
    case 'AppendToAnalysisMessageGroupMutation':
      getMessageGroup(chat, mutation.message_group_id).analysis += mutation.analysis_delta;
      break;
    case 'CreateMessageMutation': {
      const message_group = getMessageGroup(chat, mutation.message_group_id);
      message_group.messages.push({
        id: mutation.message_id,
        content: mutation.content,
        timestamp: new Date().toISOString(),
        tool_calls: [],
        is_streaming: false,
      });
      messageBuffer?.reinitialize(mutation.content);
      break;
    }
    case 'DeleteMessageMutation': {
      const messageLocation = getMessageLocation(chat, mutation.message_id);
      messageLocation.group.messages = messageLocation.group.messages.filter(
        (m) => m.id !== messageLocation.message.id,
      );

      // Remove the message group if it is empty
      if (messageLocation.group.messages.length === 0) {
        chat.message_groups = chat.message_groups.filter((group) => group.id !== messageLocation.group.id);
      }
      break;
    }
    case 'SetContentMessageMutation':
      getMessageLocation(chat, mutation.message_id).message.content = mutation.content;
      break;
    case 'AppendToContentMessageMutation': {
      if (messageBuffer !== undefined) {
        messageBuffer.processDelta(mutation.content_delta);
        getMessageLocation(chat, mutation.message_id).message.content = messageBuffer.message;
      } else {
        getMessageLocation(chat, mutation.message_id).message.content += mutation.content_delta;
      }
      break;
    }
    case 'SetIsStreamingMessageMutation':
      const message = getMessageLocation(chat, mutation.message_id);
      message.message.is_streaming = mutation.is_streaming;
      const hasFinishedStreaming = !mutation.is_streaming;

      if (hasFinishedStreaming && messageBuffer !== undefined) {
        message.message.content = messageBuffer.message + messageBuffer.buffer;
        messageBuffer.reinitialize();
      }

      break;
    case 'CreateToolCallMutation': {
      const message = getMessageLocation(chat, mutation.message_id);
      message.message.tool_calls.push({
        id: mutation.tool_call_id,
        language: mutation.language,
        code: mutation.code,
        headline: mutation.headline,
        output: mutation.output,
        is_successful: mutation.is_successful,
        is_streaming: mutation.is_streaming,
        is_executing: mutation.is_executing,
      });
      break;
    }

    case 'DeleteToolCallMutation': {
      const tool_call = getToolCallLocation(chat, mutation.tool_call_id);
      tool_call.message.tool_calls = tool_call.message.tool_calls.filter((tc) => tc.id !== tool_call.tool_call.id);

      // Remove the message if it is empty
      if (tool_call.message.tool_calls.length === 0 && tool_call.message.content === '') {
        const messageLocation = getMessageLocation(chat, tool_call.message.id);
        messageLocation.group.messages = messageLocation.group.messages.filter(
          (m) => m.id !== messageLocation.message.id,
        );
      }

      // Remove the message group if it is empty
      if (tool_call.group.messages.length === 0) {
        chat.message_groups = chat.message_groups.filter((group) => group.id !== tool_call.group.id);
      }

      break;
    }
    case 'SetHeadlineToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.headline = mutation.headline;
      break;
    case 'AppendToHeadlineToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.headline += mutation.headline_delta;
      break;
    case 'SetCodeToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.code = mutation.code;
      break;
    case 'AppendToCodeToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.code += mutation.code_delta;
      break;
    case 'SetLanguageToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.language = mutation.language;
      break;
    case 'SetOutputToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.output = mutation.output;
      break;
    case 'AppendToOutputToolCallMutation': {
      const tool_call = getToolCallLocation(chat, mutation.tool_call_id).tool_call;
      if (tool_call.output === undefined) {
        tool_call.output = '';
      }
      tool_call.output += mutation.output_delta;
      break;
    }
    case 'SetIsSuccessfulToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.is_successful = mutation.is_successful;
      break;
    case 'SetIsStreamingToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.is_streaming = mutation.is_streaming;
      break;
    case 'SetIsExecutingToolCallMutation':
      getToolCallLocation(chat, mutation.tool_call_id).tool_call.is_executing = mutation.is_executing;
      break;
    default:
      console.error('Unknown mutation type: ', mutation);
  }
}
