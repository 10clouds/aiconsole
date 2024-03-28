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

import { useChatStore } from '@/store/assets/chat/useChatStore';
import { AICMessage, AICMessageGroup, AICToolCall } from '@/types/assets/chatTypes';
import { useCallback, useState } from 'react';
import SyntaxHighlighter, { SyntaxHighlighterProps } from 'react-syntax-highlighter';
import { duotoneDark as vs2015 } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { EditableContentMessage } from './EditableContentMessage';

interface OutputProps {
  tool_call: AICToolCall;
  syntaxHighlighterCustomStyles?: SyntaxHighlighterProps['style'];
  group: AICMessageGroup;
  message: AICMessage;
}

export function ToolOutput({ tool_call, syntaxHighlighterCustomStyles, message, group }: OutputProps) {
  const [isEditing, setIsEditing] = useState(false);
  const chatRef = useChatStore((state) => state.chatRef);

  const handleAcceptedContent = useCallback(
    async (content: string) => {
      const messageRef = chatRef?.messagesGroups.getById(group.id).messages.getById(message.id);
      if (!messageRef) {
        throw new Error('No message reference found');
      }

      messageRef.tool_calls.getById(tool_call.id).output.set(content);
    },
    [tool_call.id, chatRef, group.id, message.id],
  );

  const handleRemoveClick = useCallback(() => {
    const messageRef = chatRef?.messagesGroups.getById(group.id).messages.getById(message.id);
    if (!messageRef) {
      throw new Error('No message reference found');
    }

    messageRef.tool_calls.getById(tool_call.id).delete();
  }, [tool_call.id, chatRef, group.id, message.id]);

  return (
    <div className="flex flex-col w-full mt-2">
      <span className="text-[15px] w-20 flex-none">Output: </span>
      <EditableContentMessage
        initialContent={tool_call.output || ''}
        handleAcceptedContent={handleAcceptedContent}
        handleRemoveClick={handleRemoveClick}
        className="flex-grow"
        isEditing={isEditing}
        setIsEditing={setIsEditing}
      >
        <SyntaxHighlighter
          style={syntaxHighlighterCustomStyles || vs2015}
          children={tool_call.output || ''}
          language={'text'}
          className="basis-0 flex-grow rounded-md p-2 overflow-auto"
        />
      </EditableContentMessage>
    </div>
  );
}
