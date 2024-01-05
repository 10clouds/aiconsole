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

import { AICToolCall, AICMessage } from '@/types/editables/chatTypes';
import { ChatStore } from './useChatStore';
import { deepCopyChat, getMessage, getToolCall } from '@/utils/editables/chatUtils';
import { ChatMutation } from '@/api/ws/chat/chatMutations';
import { applyMutation } from '@/api/ws/chat/applyMutation';
import { useWebSocketStore } from '@/api/ws/useWebSocketStore';

import { v4 as uuidv4 } from 'uuid';

export type MessageSlice = {
  loadingMessages: boolean;
  isViableForRunningCode: (toolCallId: string) => boolean;
  userMutateChat: (mutation: ChatMutation | ChatMutation[]) => Promise<void>;
  lockChat: (lockId: string) => Promise<void>;
  unlockChat: (lockId: string) => Promise<void>;
};

export const createMessageSlice: StateCreator<ChatStore, [], [], MessageSlice> = (set, get) => ({
  isViableForRunningCode: (toolCallId: string) => {
    const chat = get().chat;

    if (!chat) {
      throw new Error('Chat is not initialized');
    }

    try {
      const toolCallLocation = getToolCall(chat, toolCallId);

      if (toolCallLocation) {
        return toolCallLocation.toolCall.output == undefined; //TODO: Why this can be null sometimes?
      } else {
        return false;
      }
    } catch (e) {
      console.error(e);
      return false;
    }
  },
  loadingMessages: false,
  lockChat: async (lockId: string) => {
    const chat = get().chat;

    if (!chat) {
      throw new Error('Chat is not initialized');
    }

    const chat_id = chat.id;

    await useWebSocketStore.getState().sendMessageAndWaitForResponse(
      {
        type: 'AcquireLockClientMessage',
        request_id: lockId,
        chat_id: chat.id,
      },
      (response) =>
        response.type === 'NotifyAboutChatMutationServerMessage' &&
        response.mutation.type === 'LockAcquiredMutation' &&
        response.mutation.lock_id === lockId &&
        response.chat_id === chat_id,
    );
  },
  unlockChat: async (lockId: string) => {
    const chat = get().chat;

    if (!chat) {
      throw new Error('Chat is not initialized');
    }

    await useWebSocketStore.getState().sendMessage({
      type: 'ReleaseLockClientMessage',
      request_id: lockId,
      chat_id: chat.id,
    });
  },
  userMutateChat: async (mutation: ChatMutation | ChatMutation[]) => {
    const mutations = Array.isArray(mutation) ? mutation : [mutation];
    const lockId = uuidv4();
    await get().lockChat(lockId);
    try {
      set((state) => {
        const chat = deepCopyChat(state.chat);

        if (!chat) {
          throw new Error('Chat is not initialized');
        }

        for (const mutation of mutations) {
          applyMutation(chat, mutation);

          // send to server
          useWebSocketStore.getState().sendMessage({
            type: 'InitChatMutationClientMessage',
            request_id: lockId,
            chat_id: chat.id,
            mutation,
          });
        }

        return {
          chat,
        };
      });
    } finally {
      await get().unlockChat(lockId);
    }
  },
  clientEditMessage: (change: (message: AICMessage) => void, messageId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);
      const messageLocation = getMessage(chat, messageId);
      if (!messageLocation) {
        console.error(`Message with id ${messageId} not found in`, chat);
        throw new Error('Message not found');
      }

      if (change) change(messageLocation.message);

      return {
        chat,
      };
    });

    const chat = get().chat;

    if (!chat) {
      throw new Error('Chat is not initialized');
    }
  },
  clientEditToolCall: (change: (toolCall: AICToolCall) => void, toolCallId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);
      const outputLocation = getToolCall(chat, toolCallId);

      if (!outputLocation) {
        console.error(`Tool call with id ${toolCallId} not found in`, chat);
        throw new Error(`Tool call with id ${toolCallId} not found`);
      }

      if (change) change(outputLocation.toolCall);

      return {
        chat,
      };
    });
  },
});
