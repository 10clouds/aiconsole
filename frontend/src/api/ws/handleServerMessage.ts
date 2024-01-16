import { useChatStore } from '../../store/editables/chat/useChatStore';
import { useSettingsStore } from '../../store/settings/useSettingsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { useToastsStore } from '@/store/common/useToastsStore';
import { ServerMessage } from './serverMessages';
import { applyMutation } from './chat/applyMutation';
import { deepCopyChat } from '@/utils/editables/chatUtils';

export async function handleServerMessage(message: ServerMessage) {
  const showToast = useToastsStore.getState().showToast;

  console.debug('Received ServerMessage: ', message);

  switch (message.type) {
    case 'ErrorServerMessage':
      console.error(message.error);
      showToast({
        title: 'Error',
        message: message.error,
        variant: 'error',
      });
      break;
    case 'NotificationServerMessage':
      showToast({
        title: message.title,
        message: message.message,
      });
      break;
    case 'DebugJSONServerMessage':
      console.log(message.message, message.object);
      break;
    case 'InitialProjectStatusServerMessage':
      if (message.project_path && message.project_name) {
        useProjectStore.getState().onProjectOpened({
          name: message.project_name,
          path: message.project_path,
          initial: true,
        });
      } else {
        useProjectStore.getState().onProjectClosed();
      }
      break;
    case 'ProjectOpenedServerMessage':
      useProjectStore.getState().onProjectOpened({
        name: message.name,
        path: message.path,
        initial: false,
      });
      break;
    case 'ProjectClosedServerMessage':
      useProjectStore.getState().onProjectClosed();
      break;
    case 'ProjectLoadingServerMessage':
      useProjectStore.getState().onProjectLoading();
      break;
    case 'AssetsUpdatedServerMessage':
      if (message.asset_type === 'agent') {
        useEditablesStore.getState().initAgents();
        if (!message.initial) {
          showToast({
            title: 'Agents updated',
            message: `Loaded ${message.count} agents.`,
          });
        }
      }

      if (message.asset_type === 'material') {
        useEditablesStore.getState().initMaterials();
        if (!message.initial) {
          showToast({
            title: 'Materials updated',
            message: `Loaded ${message.count} materials.`,
          });
        }
      }
      break;

    case 'SettingsServerMessage':
      useSettingsStore.getState().initSettings();
      useEditablesStore.getState().initMaterials();
      useEditablesStore.getState().initAgents();
      if (!message.initial) {
        showToast({
          title: 'Settings updated',
          message: `Loaded new settings.`,
        });
      }
      break;
    case 'NotifyAboutChatMutationServerMessage': {
      const chat = deepCopyChat(useChatStore.getState().chat);
      if (!chat) {
        throw new Error('Chat is not initialized');
      }
      applyMutation(chat, message.mutation);
      useChatStore.setState({ chat });
      break;
    }
    case 'ChatOpenedServerMessage':
      useChatStore.setState({
        chat: message.chat,
      });
      break;
    default:
      console.error('Unknown message type: ', message);
  }
}
