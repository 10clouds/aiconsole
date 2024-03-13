import { useChatStore } from '../../store/assets/chat/useChatStore';
import { useSettingsStore } from '../../store/settings/useSettingsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { useToastsStore } from '@/store/common/useToastsStore';
import { ServerMessage } from './serverMessages';
import { applyMutation } from './chat/applyMutation';
import { deepCopyChat } from '@/utils/assets/chatUtils';
import { AssetsAPI } from '../api/AssetsAPI';
import { AICChat } from '@/types/assets/chatTypes';
import { v4 as uuidv4 } from 'uuid';
import { MessageBuffer } from '@/utils/common/MessageBuffer';

let messageBuffer = new MessageBuffer();

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
      useAssetStore.getState().initAssets();
      if (!message.initial) {
        showToast({
          title: 'Assets updated',
          message: `Loaded ${message.count} assets.`,
        });
      }
      break;
    case 'SettingsServerMessage':
      useSettingsStore.getState().initSettings();
      useAssetStore.getState().initAssets();
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
      applyMutation(chat, message.mutation, messageBuffer);
      useChatStore.setState({ chat });
      break;
    }
    case 'ChatOpenedServerMessage':
      const chat = message.chat;

      const currentlySreamingMessage = chat.message_groups
        .flatMap((group) => group.messages)
        .find((message) => message.is_streaming);

      if (currentlySreamingMessage) {
        messageBuffer.reinitialize();
        messageBuffer.processDelta(currentlySreamingMessage.content);
        currentlySreamingMessage.content = messageBuffer.message;
      }

      useChatStore.setState({
        chat,
      });
      break;
    case 'ResponseServerMessage': {
      if (message.is_error) {
        AssetsAPI.closeChat(message.payload.chat_id);
        AssetsAPI.fetchAsset<AICChat>({ assetType: 'chat', id: uuidv4() }).then((chat) => {
          useChatStore.getState().setChat(chat);
        });
      }
      break;
    }
    default:
      console.error('Unknown message type: ', message);
  }
}
