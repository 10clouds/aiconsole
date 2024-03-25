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

import { ScrollOption } from 'react-scroll-to-bottom';
import { v4 as uuid } from 'uuid';
import { ChatAPI } from '../../../api/api/ChatAPI';
import { ChatStore } from './useChatStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { MutationsAPI } from '@/api/api/MutationsAPI';

export type CommandSlice = {
  commandHistory: string[];
  commandIndex: number;
  commandPending: boolean;
  scrollChatToBottom?: (props: ScrollOption) => void;

  actions: {
    historyUp: () => void;
    newCommand: () => void;
    historyDown: () => void;
    getCommand: () => string;
    editCommand: (prompt: string) => void;
    initCommandHistory: () => Promise<void>;
    appendFilePathToCommand: (path: string) => void;
    submitCommand: (prompt: string, isNewChat?: boolean) => Promise<void>;
    saveCommandAndMessagesToHistory: (command: string, isUserCommand: boolean) => Promise<void>;
  };
};

export const createCommandSlice: StateCreator<ChatStore, [], [], CommandSlice> = (set, get) => ({
  commandHistory: [''],
  commandIndex: 0,
  commandPending: false,
  scrollChatToBottom: undefined,

  actions: {
    initCommandHistory: async () => {
      const history: string[] = await (await ChatAPI.getCommandHistory()).json();

      set(() => ({
        commandHistory: [...history, ''],
        commandIndex: history.length,
      }));
    },
    historyDown: () => {
      set((state) => ({
        commandIndex: Math.min(state.commandHistory.length - 1, state.commandIndex + 1),
      }));
    },
    historyUp: () => {
      set((state) => ({ commandIndex: Math.max(0, state.commandIndex - 1) }));
    },
    newCommand: () =>
      set((state) => ({
        commandHistory: [...state.commandHistory, ''],
        commandIndex: state.commandHistory.length,
      })),
    editCommand: (command) => {
      set((state) => ({
        commandHistory: [
          ...state.commandHistory.slice(0, state.commandIndex),
          command,
          ...state.commandHistory.slice(state.commandIndex + 1, state.commandHistory.length),
        ],
      }));
    },
    getCommand: () => {
      return get().commandHistory[get().commandIndex];
    },
    appendFilePathToCommand: (path: string) => {
      const { getCommand, editCommand } = get().actions;
      const command = getCommand();
      editCommand(`${command} ${path}`);
    },
    saveCommandAndMessagesToHistory: async (command: string, isUserCommand: boolean) => {
      if (isUserCommand) {
        const history: string[] = await (await ChatAPI.saveCommandToHistory({ command })).json();
        set(() => ({
          commandHistory: [...history, ''],
          commandIndex: history.length,
        }));
      }
    },
    submitCommand: async (command: string) => {
      if (get().commandPending) {
        return;
      }
      set(() => ({ commandPending: true }));

      await get().stopWork();

      const { saveCommandAndMessagesToHistory } = get().actions;

      while (get().chatOptionsSaveDebounceTimer) {
        //Let's wait until any chat option modifiactions are saved
        await new Promise((resolve) => setTimeout(resolve, 50));
        console.debug('Waiting for chatOptionsSaveDebounceTimer to be null');
      }

      if (command.trim() !== '') {
        const chat = get().chat;

        if (!chat) {
          throw new Error('Chat is not initialized');
        }

        const messageGroupId = uuid();
        const messageId = uuid();

        await get().userMutateChat((chat, lockId) =>
          MutationsAPI.create({
            asset: chat,
            path: ['message_groups', messageGroupId],
            object: {
              actor_id: { type: 'user', id: useSettingsStore.getState().settings.user_profile.id || 'user' },
              task: '',
              materials_ids: [],
              analysis: '',
              role: 'user',
              messages: [
                {
                  is_streaming: false,
                  id: messageId,
                  content: command,
                  timestamp: new Date().toISOString(),
                  tool_calls: [],
                },
              ],
            },
            requestId: lockId,
          }),
        );

        await saveCommandAndMessagesToHistory(command, true);
      }

      const scrollChatToBottom = get().scrollChatToBottom;
      if (scrollChatToBottom) {
        scrollChatToBottom({
          behavior: 'smooth',
        });
      }

      await get().doProcess();
      set(() => ({ commandPending: false }));
    },
  },
});
