import { useChatStore } from '@/store/editables/chat/useChatStore';
import { RequestProcessingFinishedWSMessage } from '@/types/editables/chatWebSocketTypes';

/*

if (data.stage === 'end') {
      useChatStore.getState().editToolCall((toolCall) => {
        toolCall.is_executing = false;
      }, data.id);

      useChatStore.getState().finishProcess(data.request_id, false);
      const chat = useChatStore.getState().chat;

      //if all code in the current message is ran, continue operation with the same agent
      const toolCallLocation = getToolCall(chat, data.id);
      const lastMessage = getLastMessage(chat);

      const message = toolCallLocation?.message;

      if (message?.id === lastMessage?.message.id) {
        // if all tools have finished running, continue operation with the same agent
        const finishedRunnigCode = message?.tool_calls.every(
          (toolCall) => toolCall.is_executing === false && toolCall.output !== undefined,
        );

        if (finishedRunnigCode) {
          await useChatStore.getState().doExecute(); // Resume operation with the same agent
        }
      }
    }

*/

export async function handleRequestProcessingFinishedWSMessage(data: RequestProcessingFinishedWSMessage) {
  useChatStore.getState().finishProcess(data.request_id, data.aborted);

  console.log('Running processes: ', useChatStore.getState().runningProcesses);

  /*
  if (useChatStore.getState().analysis.agent_id) {
    //if analysis ended
    if (useChatStore.getState().analysis.agent_id !== 'user' && useChatStore.getState().analysis.next_step) {
      useChatStore.getState().appendGroup({
        agent_id: useChatStore.getState().analysis.agent_id || '',
        task: useChatStore.getState().analysis.next_step || '',
        materials_ids: useChatStore.getState().analysis.relevant_material_ids || [],
        role: 'assistant',
        messages: [],
        analysis: '',
        id: data.request_id,
      });

      useChatStore.getState().finishProcess(data.request_id, false);
      useChatStore.getState().doExecute();
    } else {
      useChatStore.getState().finishProcess(data.request_id, false);
    }
  } else {
    // execute ended
    useChatStore.getState().finishProcess(data.request_id, false);

    const lastMessage = getLastMessage(useChatStore.getState().chat);
    let hasCodeToRun = false;
    if (lastMessage) {
      for (const toolCall of lastMessage.message.tool_calls) {
        if (useSettingsStore.getState().alwaysExecuteCode) {
          await useChatStore.getState().doRun(toolCall.id);
        }
        hasCodeToRun = true;
      }
    }

    if (!hasCodeToRun) {
      await useChatStore.getState().doAnalysis();
    }

    if (data.request_id) {
      console.log('Received request processing finished message for request id: ', data.request_id);
    } else {
      console.error('Received request processing finished message without request id');
    }
  }*/
}
