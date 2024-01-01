import { ChatWSMessage } from '@/types/editables/chatWebSocketTypes';
import { useChatStore } from '@/store/editables/chat/useChatStore';

export async function handleChatMessage(data: ChatWSMessage) {
  if (useChatStore.getState().isOngoing(data.request_id)) {
    switch (data.type) {
      case 'OpCreateMessageGroupWSMessage':
        useChatStore.getState().appendGroup({
          id: data.message_group_id,
          agent_id: data.agent_id,
          role: data.role,
          task: data.task,
          materials_ids: data.materials_ids,
          messages: [],
          analysis: data.analysis,
        });
        break;
      case 'OpDeleteMessageGroupWSMessage':
        useChatStore.getState().deleteGroup(data.message_group_id);
        break;
      case 'OpSetIsAnalysisInProgressWSMessage':
        useChatStore.getState().setIsAnalysisInProgress(data.is_analysis_in_progress);
        break;
      case 'OpSetMessageGroupTaskWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.task = data.task;
        }, data.message_group_id);
        break;
      case 'OpAppendToMessageGroupTaskWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.task += data.task_delta;
        }, data.message_group_id);
        break;
      case 'OpSetMessageGroupRoleWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.role = data.role;
        }, data.message_group_id);
        break;
      case 'OpSetMessageGroupAgentIdWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.agent_id = data.agent_id;
        }, data.message_group_id);
        break;
      case 'OpSetMessageGroupMaterialsIdsWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.materials_ids = data.materials_ids;
        }, data.message_group_id);
        break;
      case 'OpAppendToMessageGroupMaterialsIdsWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.materials_ids.push(...data.material_id);
        }, data.message_group_id);
        break;
      case 'OpSetMessageGroupAnalysisWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.analysis = data.analysis;
        }, data.message_group_id);
        break;
      case 'OpAppendToMessageGroupAnalysisWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.analysis += data.analysis_delta;
        }, data.message_group_id);
        break;
      case 'OpCreateMessageWSMessage':
        useChatStore.getState().editGroup((group) => {
          group.messages.push({
            id: data.message_id,
            timestamp: data.timestamp,
            content: data.content,
            tool_calls: [],
            is_streaming: false,
          });
        }, data.message_group_id);
        break;
      case 'OpDeleteMessageWSMessage':
        useChatStore.getState().deleteMessage(data.message_id);
        break;
      case 'OpAppendToMessageContentWSMessage':
        useChatStore.getState().editMessage((message) => {
          if (!message.is_streaming) {
            throw new Error('Received content delta for message that is not streaming');
          }
          message.content += data.content_delta;
        }, data.message_id);
        break;
      case 'OpSetMessageContentWSMessage':
        useChatStore.getState().editMessage((message) => {
          message.content = data.content;
        }, data.message_id);
        break;
      case 'OpSetMessageIsStreamingWSMessage':
        useChatStore.getState().editMessage((message) => {
          message.is_streaming = data.is_streaming;
        }, data.message_id);
        break;
      case 'OpCreateToolCallWSMessage':
        useChatStore.getState().editMessage((message) => {
          message.tool_calls.push({
            id: data.tool_call_id,
            language: data.language,
            is_executing: false,
            is_streaming: false,
            code: '',
            headline: '',
          });
        }, data.message_id);
        break;
      case 'OpDeleteToolCallWSMessage':
        useChatStore.getState().deleteToolCall(data.tool_call_id);
        break;
      case 'OpSetToolCallHeadlineWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          tool_call.headline = data.headline;
        }, data.tool_call_id);
        break;
      case 'OpAppendToToolCallHeadlineWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          if (!tool_call.is_streaming) {
            throw new Error('Received text delta for tool_call that is not streaming');
          }
          tool_call.headline += data.headline_delta;
        }, data.tool_call_id);
        break;
      case 'OpSetToolCallCodeWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          tool_call.code = data.code;
        }, data.tool_call_id);
        break;
      case 'OpAppendToToolCallCodeWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          if (!tool_call.is_streaming) {
            throw new Error('Received text delta for tool_call that is not streaming');
          }
          tool_call.code += data.code_delta;
        }, data.tool_call_id);
        break;
      case 'OpSetToolCallLanguageWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          tool_call.language = data.language;
        }, data.tool_call_id);
        break;
      case 'OpSetToolCallOutputWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          tool_call.output = data.output == null ? undefined : data.output;
        }, data.tool_call_id);
        break;
      case 'OpAppendToToolCallOutputWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          if (!tool_call.is_streaming) {
            throw new Error('Received text delta for tool_call that is not streaming');
          }
          tool_call.output += data.output_delta;
        }, data.tool_call_id);
        break;
      case 'OpSetToolCallIsStreamingWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          tool_call.is_streaming = data.is_streaming;
        }, data.tool_call_id);
        break;
      case 'OpSetToolCallIsExecutingWSMessage':
        useChatStore.getState().editToolCall((tool_call) => {
          tool_call.is_executing = data.is_executing;
        }, data.tool_call_id);
        break;
      default:
        console.error('Unknown message type: ', data);
    }
  } else {
    console.warn(`Received chat mutation message for request ${data.request_id} that is not ongoing`);
  }

  console.log('Chat store after mutation: ', useChatStore.getState().chat);
}
