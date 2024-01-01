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

import { AICToolCall, AICMessage, AICMessageGroup } from '@/types/editables/chatTypes';
import { ChatStore } from './useChatStore';
import {
  deepCopyChat,
  getGroup,
  getLastGroup,
  getLastMessage,
  getMessage,
  getToolCall,
} from '@/utils/editables/chatUtils';

export type MessageSlice = {
  loadingMessages: boolean;
  isViableForRunningCode: (toolCallId: string) => boolean;
  setIsAnalysisInProgress(isAnalysisInProgress: boolean): void;
  editGroup: (change: (group: AICMessageGroup) => void, groupId: string) => void;
  editMessage: (change: (message: AICMessage) => void, messageId: string) => void;
  editToolCall: (change: (output: AICToolCall) => void, outputId: string) => void;
  appendToolCall: (toolCall: AICToolCall, messageId?: string) => void;
  appendMessage: (message: AICMessage, groupId?: string) => void;
  appendGroup: (group: AICMessageGroup) => void;
  deleteToolCall: (toolCallId: string) => void;
  deleteGroup: (groupId: string) => void;
  deleteMessage: (messageId: string) => void;
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
  setIsAnalysisInProgress: (isAnalysisInProgress: boolean) => {
    set((state) => {
      console.log(state.chat);
      const chat = deepCopyChat(state.chat);

      if (!chat) {
        throw new Error('Chat is not initialized');
      }

      chat.is_analysis_in_progress = isAnalysisInProgress;

      return {
        chat,
      };
    });
  },
  editGroup: (change: (group: AICMessageGroup) => void, groupId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);
      const groupLocation = getGroup(chat, groupId);

      if (!groupLocation) {
        console.log(`Group ${groupId} found in`, chat);
        throw new Error(`Group ${groupId} found in ${chat}`);
      }

      if (change) change(groupLocation.group);

      return {
        chat,
      };
    });
  },
  editMessage: (change: (message: AICMessage) => void, messageId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);
      const messageLocation = getMessage(chat, messageId);
      if (!messageLocation) {
        console.trace();
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
  editToolCall: (change: (toolCall: AICToolCall) => void, toolCallId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);
      const outputLocation = getToolCall(chat, toolCallId);

      if (!outputLocation) {
        console.trace();
        console.error(`Tool call with id ${toolCallId} not found in`, chat);
        throw new Error(`Tool call with id ${toolCallId} not found`);
      }

      if (change) change(outputLocation.toolCall);

      return {
        chat,
      };
    });
  },
  appendToolCall: (toolCall: AICToolCall, messageId?: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);
      const messageLocation = messageId === undefined ? getLastMessage(chat) : getMessage(chat, messageId);

      if (!messageLocation) {
        throw new Error(`Message with id ${messageId} is not a code message`);
      }

      messageLocation.message.tool_calls.push({
        ...toolCall,
      });

      return {
        chat,
      };
    });
  },
  appendGroup: (group: AICMessageGroup) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);

      if (!chat) {
        throw new Error('Chat is not initialized');
      }

      chat.message_groups.push({
        ...group,
      });

      return {
        chat,
      };
    });
  },
  deleteGroup: (groupId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);

      if (!chat) {
        throw new Error('Chat is not initialized');
      }

      const groupLocation = getGroup(chat, groupId);

      if (!groupLocation) {
        throw new Error(`Group ${groupId} found in ${chat}`);
      }

      chat.message_groups.splice(chat.message_groups.indexOf(groupLocation.group), 1);

      return {
        chat,
      };
    });
    get().saveCurrentChatHistory();
  },
  appendMessage: (message: AICMessage, groupId?: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);

      const groupLocation = groupId === undefined ? getLastGroup(chat) : getGroup(chat, groupId);

      if (!groupLocation) {
        throw new Error(`Group ${groupId} found in ${chat}`);
      }

      groupLocation.group.messages.push({
        ...message,
      });

      return {
        chat,
      };
    });
  },
  deleteMessage: (messageId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);

      if (!chat) {
        throw new Error('Chat is not initialized');
      }

      const messageLocation = getMessage(chat, messageId);

      if (!messageLocation) {
        throw new Error('Message not found');
      }

      messageLocation.group.messages.splice(messageLocation.messageIndex, 1);

      if (messageLocation.group.messages.length === 0) {
        chat.message_groups.splice(chat.message_groups.indexOf(messageLocation.group), 1);
      }

      return {
        chat,
      };
    });
    get().saveCurrentChatHistory();
  },
  deleteToolCall: (toolCallId: string) => {
    set((state) => {
      const chat = deepCopyChat(state.chat);

      const toolCallLocation = getToolCall(chat, toolCallId);

      if (!toolCallLocation) {
        throw new Error(`Tool call with id ${toolCallId} not found`);
      }

      toolCallLocation.message.tool_calls.splice(toolCallLocation.toolCallIndex, 1);

      if (toolCallLocation.message.tool_calls.length === 0 && toolCallLocation.message.content === '') {
        toolCallLocation.group.messages.splice(toolCallLocation.messageIndex, 1);
      }

      return {
        chat,
      };
    });
    get().saveCurrentChatHistory();
  },
});
