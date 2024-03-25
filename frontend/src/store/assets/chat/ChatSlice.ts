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
import { AssetsAPI } from '@/api/api/AssetsAPI';
import { AICChat, createEmptyChat } from '@/types/assets/chatTypes';
import { useAssetStore } from '../useAssetStore';
import { ChatStore, useChatStore } from './useChatStore';
import { MutationsAPI } from '@/api/api/MutationsAPI';

export type ChatSlice = {
  isSaved: boolean;
  chat: AICChat;
  lastUsedChat?: AICChat;
  isChatLoading: boolean;
  updateChatOptions: (chatOptions: Partial<AICChat['chat_options']>) => void;
  debounceChatOptionsUpdate: (chat: AICChat, chatOptions: AICChat['chat_options']) => void;
  setLastUsedChat: (chat?: AICChat) => void;
  setChat: (chat: AICChat) => void;
  renameChat: (newChat: AICChat) => Promise<void>;
  setIsChatLoading: (isLoading: boolean) => void;
  chatOptionsSaveDebounceTimer: NodeJS.Timeout | null;
};

export const createChatSlice: StateCreator<ChatStore, [], [], ChatSlice> = (set, get) => ({
  isSaved: false,
  isChatLoading: false,
  chat: createEmptyChat(),
  agent: undefined,
  lastUsedChat: undefined,
  materials: [],
  chatOptionsSaveDebounceTimer: null,
  setLastUsedChat: (chat?: AICChat) => {
    set({ lastUsedChat: chat });
  },
  setChat: (chat: AICChat) => {
    set({
      chat,
    });
  },
  renameChat: async (newChat: AICChat) => {
    await AssetsAPI.updateAsset(newChat, newChat.id);
    get().setChat(newChat);

    //If it's chat we need to reload chat history because there is no autoreload on change for chats
    useAssetStore.getState().initAssets();
  },
  setIsChatLoading: (isLoading: boolean) => {
    set({ isChatLoading: isLoading });
  },

  updateChatOptions: (chatOptions: Partial<AICChat['chat_options']>) => {
    set((state) => {
      const chat = state.chat;

      if (!chat) {
        throw new Error('Cannot update chat options for chat that does not exist');
      }

      if (!chatOptions) {
        throw new Error('Cannot update chat options without any new options');
      }

      const newChatOptions = {
        ...chat.chat_options,
        ...chatOptions,
      };

      chat.chat_options = newChatOptions;

      get().debounceChatOptionsUpdate(chat, newChatOptions);

      return {
        chat,
      };
    });
  },

  debounceChatOptionsUpdate: (chat: AICChat, chatOptions: AICChat['chat_options']) => {
    const debounceDelay = 500; // milliseconds

    const timer = get().chatOptionsSaveDebounceTimer;
    if (timer) {
      clearTimeout(timer);
      set({ chatOptionsSaveDebounceTimer: null });
    }

    set({
      chatOptionsSaveDebounceTimer: setTimeout(async () => {
        const isSaved = useChatStore.getState().isSaved;

        if (!isSaved) {
          MutationsAPI.create({ object: chat });
          useChatStore.setState({ isSaved: true });
          useAssetStore.setState((state) => ({
            assets: [chat, ...state.assets],
          }));
        }

        MutationsAPI.update({ asset: chat, key: 'chat_options', value: chatOptions });
        useChatStore.setState({ chatOptionsSaveDebounceTimer: null });
      }, debounceDelay),
    });
  },
});
