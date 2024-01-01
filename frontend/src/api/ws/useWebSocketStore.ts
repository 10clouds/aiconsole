// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import ReconnectingWebSocket from 'reconnecting-websocket';
import { create } from 'zustand';
import { ErrorEvent } from 'reconnecting-websocket/events';
import { useChatStore } from '../../store/editables/chat/useChatStore';
import { OutgoingWSMessage } from './outgoingMessages';
import { IncomingWSMessage } from './incomingMessages';
import { useAPIStore } from '../../store/useAPIStore';
import { useSettingsStore } from '../../store/settings/useSettingsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { handleChatMessage } from './chat/handleChatMessage';
import { useToastsStore } from '@/store/common/useToastsStore';
import { handleRequestProcessingFinishedWSMessage } from './chat/handleRequestProcessingFinishedWSMessage';

export type WebSockeStore = {
  ws: ReconnectingWebSocket | null;
  initWebSocket: () => void;
  disconnect: () => void;
  sendMessage: (message: OutgoingWSMessage) => void;
  initStarted: boolean;
};

// Create Zustand store
export const useWebSocketStore = create<WebSockeStore>((set, get) => ({
  ws: null,
  initStarted: false,

  // updated function to init the WebSocket connection
  initWebSocket: () => {
    if (get().initStarted) return;
    set({ initStarted: true });

    const getBaseHostWithPort = useAPIStore.getState().getBaseHostWithPort;
    const ws = new ReconnectingWebSocket(`ws://${getBaseHostWithPort()}/ws`);
    const showToast = useToastsStore.getState().showToast;

    ws.onopen = () => {
      set({ ws });

      const chatId = useChatStore.getState().chat?.id || '';

      get().sendMessage({
        type: 'SetChatIdWSMessage',
        chat_id: chatId,
      });
    };

    ws.onmessage = async (e: MessageEvent) => {
      const data: IncomingWSMessage = JSON.parse(e.data);

      console.log('WebSocket message: ', data);

      switch (data.type) {
        case 'ErrorWSMessage':
          console.error(data.error);
          showToast({
            title: 'Error',
            message: data.error,
            variant: 'error',
          });
          break;
        case 'NotificationWSMessage':
          showToast({
            title: data.title,
            message: data.message,
          });
          break;
        case 'DebugJSONWSMessage':
          console.log(data.message, data.object);
          break;
        case 'InitialProjectStatusWSMessage':
          if (data.project_path && data.project_name) {
            useProjectStore.getState().onProjectOpened({
              name: data.project_name,
              path: data.project_path,
              initial: true,
            });
          } else {
            useProjectStore.getState().onProjectClosed();
          }
          break;
        case 'ProjectOpenedWSMessage':
          useProjectStore.getState().onProjectOpened({
            name: data.name,
            path: data.path,
            initial: false,
          });
          break;
        case 'ProjectClosedWSMessage':
          useProjectStore.getState().onProjectClosed();
          break;
        case 'ProjectLoadingWSMessage':
          useProjectStore.getState().onProjectLoading();
          break;
        case 'AssetsUpdatedWSMessage':
          if (data.asset_type === 'agent') {
            useEditablesStore.getState().initAgents();
            if (!data.initial) {
              showToast({
                title: 'Agents updated',
                message: `Loaded ${data.count} agents.`,
              });
            }
          }

          if (data.asset_type === 'material') {
            useEditablesStore.getState().initMaterials();
            if (!data.initial) {
              showToast({
                title: 'Materials updated',
                message: `Loaded ${data.count} materials.`,
              });
            }
          }
          break;

        case 'SettingsWSMessage':
          useSettingsStore.getState().initSettings();
          useEditablesStore.getState().initMaterials();
          useEditablesStore.getState().initAgents();
          if (!data.initial) {
            showToast({
              title: 'Settings updated',
              message: `Loaded new settings.`,
            });
          }
          break;
        case 'RequestProcessingFinishedWSMessage':
          await handleRequestProcessingFinishedWSMessage(data);
          break;
        case 'OpCreateMessageGroupWSMessage':
        case 'OpDeleteMessageGroupWSMessage':
        case 'OpSetIsAnalysisInProgressWSMessage':
        case 'OpSetMessageGroupTaskWSMessage':
        case 'OpAppendToMessageGroupTaskWSMessage':
        case 'OpSetMessageGroupRoleWSMessage':
        case 'OpSetMessageGroupAgentIdWSMessage':
        case 'OpSetMessageGroupMaterialsIdsWSMessage':
        case 'OpAppendToMessageGroupMaterialsIdsWSMessage':
        case 'OpSetMessageGroupAnalysisWSMessage':
        case 'OpAppendToMessageGroupAnalysisWSMessage':
        case 'OpCreateMessageWSMessage':
        case 'OpDeleteMessageWSMessage':
        case 'OpAppendToMessageContentWSMessage':
        case 'OpSetMessageContentWSMessage':
        case 'OpSetMessageIsStreamingWSMessage':
        case 'OpCreateToolCallWSMessage':
        case 'OpDeleteToolCallWSMessage':
        case 'OpSetToolCallHeadlineWSMessage':
        case 'OpAppendToToolCallHeadlineWSMessage':
        case 'OpSetToolCallCodeWSMessage':
        case 'OpAppendToToolCallCodeWSMessage':
        case 'OpSetToolCallLanguageWSMessage':
        case 'OpSetToolCallOutputWSMessage':
        case 'OpAppendToToolCallOutputWSMessage':
        case 'OpSetToolCallIsStreamingWSMessage':
        case 'OpSetToolCallIsExecutingWSMessage':
          await handleChatMessage(data);
          break;
        default:
          console.error('Unknown message type: ', data);
      }
    };

    ws.onerror = (e: ErrorEvent) => {
      console.log('WebSocket error: ', e);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
      set({ ws: null });
    };
  },

  disconnect: () => {
    get().ws?.close();
    set({ ws: null });
  },

  sendMessage: (message: OutgoingWSMessage) => {
    get().ws?.send(JSON.stringify(message));
  },
}));
