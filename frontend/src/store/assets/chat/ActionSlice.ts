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

import { StateCreator } from 'zustand';

import { ChatStore } from './useChatStore';

import { v4 as uuidv4 } from 'uuid';
import { useWebSocketStore } from '@/api/ws/useWebSocketStore';

export type RunninngProcess = {
  requestId: string;
  type: 'execute' | 'run' | 'analyse';
  entityId: string;
  abortController: AbortController;
  cleanup: (process: RunninngProcess, aborted: boolean) => void;
};

export type ActionSlice = {
  doAcceptCode: (toolCallId: string) => Promise<void>;
  isExecutionRunning: () => boolean;
  stopWork: () => Promise<void>;
  doProcess: () => Promise<void>;
};

export const createActionSlice: StateCreator<ChatStore, [], [], ActionSlice> = (_set, get) => ({
  isExecutionRunning: () => {
    const chat = get().chat;
    if (!chat) {
      return false;
    }

    return !!chat.lock_id;
  },

  doAcceptCode: async (toolCallId: string) => {
    const chat = get().chat;

    if (!chat) {
      throw new Error('Chat is not initialized');
    }

    useWebSocketStore.getState().sendMessage({
      type: 'AcceptCodeClientMessage',
      request_id: uuidv4(),
      chat_id: chat.id,
      tool_call_id: toolCallId,
    });
  },
  stopWork: async () => {
    //TODO: Wait for confirmation and maybe switch to a dedicated message type
    const chat = get().chat;

    if (chat && chat.lock_id) {
      useWebSocketStore.getState().sendMessage({
        type: 'StopChatClientMessage',
        request_id: uuidv4(),
        chat_ref: {
          id: chat.id,
          context: null,
          parent_collection: { id: 'assets', parent: null },
        },
      });
    }
  },
  analysis: {
    agent_id: undefined,
    relevant_material_ids: undefined,
    next_step: undefined,
    thinking_process: undefined,
  },
  doProcess: async () => {
    try {
      const chat = get().chat;
      if (!chat) {
        throw new Error('Chat is not initialized');
      }

      useWebSocketStore.getState().sendMessage({
        type: 'ProcessChatClientMessage',
        request_id: uuidv4(),
        chat_ref: {
          id: chat.id,
          context: null,
          parent_collection: { id: 'assets', parent: null },
        },
      });
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        return;
      } else {
        get().stopWork();
        throw err;
      }
    }
  },
});
