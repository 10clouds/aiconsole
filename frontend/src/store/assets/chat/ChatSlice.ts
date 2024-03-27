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
import { AICChat } from '../constructors';
import { AssetsCollectionRef, ChatRef } from '../locations';
import { useAssetStore } from '../useAssetStore';
import { ChatStore, useChatStore } from './useChatStore';

export type ChatSlice = {
  isSaved: boolean;
  chat: AICChat;
  chatRef: ChatRef;
  chatOptions?: {
    agent_id: string;
    materials_ids: string[];
    ai_can_add_extra_materials: boolean;
    draft_command: string;
  };
  lastUsedChat?: AICChat;
  isChatLoading: boolean;
  isChatOptionsExpanded: boolean;
  setLastUsedChat: (chat?: AICChat) => void;
  setChat: (chat: AICChat) => void;
  renameChat: (newChat: AICChat) => Promise<void>;
  setIsChatLoading: (isLoading: boolean) => void;
  setIsChatOptionsExpanded: (isExpanded: boolean) => void;
  setSelectedAgentId: (id: string) => void;
  setSelectedMaterialsIds: (ids: string[]) => void;
  setAICanAddExtraMaterials: (aiCanAddExtraMaterials: boolean) => void;
  setDraftCommand: (draftCommand: string) => void;
  chatOptionsSaveDebounceTimer: NodeJS.Timeout | null;
  debounceChatOptionsUpdate: (
    chat: AICChat,
    chatOptions: {
      agent_id: string;
      materials_ids: string[];
      ai_can_add_extra_materials: boolean;
      draft_command: string;
    },
  ) => void;
};

export const createChatSlice: StateCreator<ChatStore, [], [], ChatSlice> = (set, get) => ({
  isSaved: false,
  isChatLoading: false,
  chat: AICChat.createEmptyChat(),
  chatRef: undefined,
  chatOptions: undefined,
  agent: undefined,
  lastUsedChat: undefined,
  isChatOptionsExpanded: true,
  materials: [],
  chatOptionsSaveDebounceTimer: null,
  setLastUsedChat: (chat?: AICChat) => {
    set({ lastUsedChat: chat });
  },
  setChat: (chat: AICChat) => {
    set({
      chat,
      chatOptions: {
        agent_id: chat.chat_options.agent_id,
        materials_ids: chat.chat_options.materials_ids,
        ai_can_add_extra_materials: chat.chat_options.ai_can_add_extra_materials,
        draft_command: chat.chat_options.draft_command,
      },
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
  setIsChatOptionsExpanded: (isExpanded: boolean) => {
    set({ isChatOptionsExpanded: isExpanded });
  },
  setSelectedAgentId: (id: string) => {
    set((state) => {
      const chat = state.chat;

      if (!chat) {
        throw new Error('Cannot set agent to chat that does not exist');
      }

      const chatOptions = {
        agent_id: id,
        materials_ids: state.chatOptions?.materials_ids ?? [],
        ai_can_add_extra_materials: state.chatOptions?.ai_can_add_extra_materials ?? true,
        draft_command: state.chatOptions?.draft_command ?? '',
      };

      get().debounceChatOptionsUpdate(chat, chatOptions);

      return {
        chat,
        chatOptions,
      };
    });
  },
  setSelectedMaterialsIds: (ids: string[]) => {
    set((state) => {
      const chat = state.chat;

      if (!chat) {
        throw new Error('Cannot set materials to chat that does not exist');
      }

      const chatOptions = {
        agent_id: state.chatOptions?.agent_id ?? '',
        materials_ids: ids,
        ai_can_add_extra_materials: state.chatOptions?.ai_can_add_extra_materials ?? true,
        draft_command: state.chatOptions?.draft_command ?? '',
      };

      get().debounceChatOptionsUpdate(chat, chatOptions);

      return {
        chat,
        chatOptions,
      };
    });
  },
  setAICanAddExtraMaterials: (aiCanAddExtraMaterials: boolean) => {
    set((state) => {
      const chat = state.chat;

      if (!chat) {
        throw new Error('Cannot set AI can add extra materials to chat that does not exist');
      }

      const chatOptions = {
        agent_id: state.chatOptions?.agent_id ?? '',
        materials_ids: state.chatOptions?.materials_ids ?? [],
        ai_can_add_extra_materials: aiCanAddExtraMaterials,
        draft_command: state.chatOptions?.draft_command ?? '',
      };

      get().debounceChatOptionsUpdate(chat, chatOptions);

      return {
        chat,
        chatOptions,
      };
    });
  },
  setDraftCommand: (draftCommand: string) => {
    set((state) => {
      const chat = state.chat;

      if (!chat) {
        throw new Error('Cannot set draft command to chat that does not exist');
      }

      const chatOptions = {
        agent_id: state.chatOptions?.agent_id ?? '',
        materials_ids: state.chatOptions?.materials_ids ?? [],
        ai_can_add_extra_materials: state.chatOptions?.ai_can_add_extra_materials ?? true,
        draft_command: draftCommand,
      };

      get().debounceChatOptionsUpdate(chat, chatOptions);

      return {
        chat,
        chatOptions,
      };
    });
  },

  debounceChatOptionsUpdate: async (
    chat: AICChat,
    chatOptions: {
      agent_id: string;
      materials_ids: string[];
      ai_can_add_extra_materials: boolean;
      draft_command: string;
    },
  ) => {
    const debounceDelay = 500; // milliseconds

    const timer = useChatStore.getState().chatOptionsSaveDebounceTimer;
    if (timer) {
      clearTimeout(timer);
      useChatStore.setState({ chatOptionsSaveDebounceTimer: null });
    }

    set({
      chatOptionsSaveDebounceTimer: setTimeout(async () => {
        const isSaved = get().isSaved;
        const assetsRef = new AssetsCollectionRef(useAssetStore.getState().dataContext);

        if (!isSaved) {
          await assetsRef.create(chat);
          set({ isSaved: true });
        }

        // MutationsAPI.update({ asset: chat, key: 'chat_options', value: chatOptions });
        await get().chatRef.chat_options.set(chatOptions);
        set({ chatOptionsSaveDebounceTimer: null });
      }, debounceDelay),
    });
  },
});
