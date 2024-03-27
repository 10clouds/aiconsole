import { useChatStore } from '../../store/assets/chat/useChatStore';
import { useSettingsStore } from '../../store/settings/useSettingsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { useToastsStore } from '@/store/common/useToastsStore';
import { ServerMessage } from './serverMessages';
import { applyMutation } from './chat/applyMutation';
import { AssetsAPI } from '../api/AssetsAPI';
import { v4 as uuidv4 } from 'uuid';
import { MessageBuffer } from '@/utils/common/MessageBuffer';
import { deepCopyObject } from '@/utils/common/deepCopyObject';
import { AICChat } from '@/store/assets/constructors';
import { DataContext } from '@/store/assets/DataContext';
import { ChatRef } from '@/store/assets/locations';

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
        });
      } else {
        useProjectStore.getState().onProjectClosed();
      }
      break;
    case 'ProjectOpenedServerMessage':
      useProjectStore.getState().onProjectOpened({
        name: message.name,
        path: message.path,
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
    case 'NotifyAboutAssetMutationServerMessage': {
      const chat = deepCopyObject(useChatStore.getState().chat);

      if (!chat) {
        throw new Error('Chat is not initialized');
      }

      chat.lock_id = message.request_id;
      applyMutation(chat, message.mutation, messageBuffer);
      useChatStore.setState({ chat });
      break;
    }
    case 'ChatOpenedServerMessage': {
      const chat = AICChat.createChatFromObject(message.chat);

      const currentlySreamingMessage = chat.message_groups
        .flatMap((group) => group.messages)
        .find((message) => message.is_streaming);

      if (currentlySreamingMessage) {
        messageBuffer.reinitialize();
        messageBuffer.processDelta(currentlySreamingMessage.content);
        currentlySreamingMessage.content = messageBuffer.message;
      }

      useChatStore.setState({
        chatRef: new ChatRef(chat.id, new DataContext()),
        chat,
        chatOptions: {
          agent_id: chat.chat_options.agent_id,
          materials_ids: chat.chat_options.materials_ids,
          ai_can_add_extra_materials: chat.chat_options.ai_can_add_extra_materials,
          draft_command: chat.chat_options.draft_command,
        },
      });
      break;
    }
    case 'ResponseServerMessage': {
      const chat = useChatStore.getState().chat;

      if (chat) {
        chat.lock_id = undefined;
      }

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
