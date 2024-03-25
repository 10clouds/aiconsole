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

import { AICMessage, AICMessageGroup, AICToolCall, AICChat } from '@/types/assets/chatTypes';

export type AICGroupLocation = { groupIndex: number; group: AICMessageGroup };
export type AICMessageLocation = AICGroupLocation & { messageIndex: number; message: AICMessage };
export type AICOutputLocaion = AICMessageLocation & { toolCallIndex: number; toolCall: AICToolCall };

export function getLastGroup(chat?: AICChat): AICGroupLocation | undefined {
  if (!chat) {
    return undefined;
  }

  const group = chat.message_groups[chat.message_groups.length - 1];

  if (!group) {
    return undefined;
  }

  return {
    group,
    groupIndex: chat.message_groups.length - 1,
  };
}

export function getGroup(chat: AICChat | undefined, groupId: string): AICGroupLocation | undefined {
  if (!chat) {
    return undefined;
  }

  const groupIndex = groupId
    ? chat.message_groups.findIndex((group) => group.id === groupId)
    : chat.message_groups.length - 1;

  if (groupIndex === -1) {
    return undefined;
  }

  const group = chat.message_groups[groupIndex];

  return {
    group,
    groupIndex,
  };
}

export function getLastMessage(chat?: AICChat): AICMessageLocation | undefined {
  if (!chat) {
    return undefined;
  }

  const group = chat.message_groups[chat.message_groups.length - 1];
  const message = group.messages[group.messages.length - 1];

  if (!message) {
    return undefined;
  }

  return {
    groupIndex: chat.message_groups.length - 1,
    group,
    messageIndex: group.messages.length - 1,
    message,
  };
}

export function getMessage(chat: AICChat | undefined, messageId: string): AICMessageLocation | undefined {
  if (!chat) {
    return undefined;
  }

  let groupIndex = 0;
  for (const group of chat.message_groups) {
    let messageIndex = 0;
    for (const message of group.messages) {
      if (message.id === messageId) {
        return {
          groupIndex,
          group,
          messageIndex,
          message,
        };
      }

      messageIndex++;
    }
    groupIndex++;
  }
}

export function getToolCall(chat: AICChat | undefined, toolCallId: string): AICOutputLocaion | undefined {
  let groupIndex = 0;
  for (const group of chat?.message_groups || []) {
    let messageIndex = 0;
    for (const message of group.messages) {
      let outputIndex = 0;
      for (const tool_call of message.tool_calls) {
        if (tool_call.id === toolCallId) {
          return {
            groupIndex,
            group,
            messageIndex,
            message,
            toolCallIndex: outputIndex,
            toolCall: tool_call,
          };
        }
        outputIndex++;
      }
      messageIndex++;
    }
    groupIndex++;
  }

  return undefined;
}
