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

import { Button } from '@/components/common/Button';
import Tooltip from '@/components/common/Tooltip';
import { Icon } from '@/components/common/icons/Icon';
import { useChatStore } from '@/store/assets/chat/useChatStore';
import { Material } from '@/types/assets/assetTypes';
import { cn } from '@/utils/common/cn';
import { LucideIcon } from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import ChatOptions from './ChatOptions';
import { CommandOptionsPanel } from './CommandOptionsPanel';

interface CommandInputProps {
  actionIcon: LucideIcon | ((props: React.SVGProps<SVGSVGElement>) => JSX.Element);
  className?: string;
  actionLabel: string;
  onSubmit?: (command: string) => void;
  textAreaRef: React.RefObject<HTMLTextAreaElement>;
}

export const CommandInput = ({
  className,
  onSubmit,
  actionIcon: ActionIcon,
  actionLabel,
  textAreaRef,
}: CommandInputProps) => {
  const [showChatOptions, setShowChatOptions] = useState<boolean>(false);
  const chatOptionsInputRef = useRef<HTMLInputElement>(null);

  const { editCommand, historyDown, historyUp } = useChatStore((state) => state.actions);
  const command = useChatStore((state) => state.actions.getCommand());
  const selectedMaterialIds = useChatStore((state) => state.chat.chat_options.materials_ids);
  const draftCommand = useChatStore((state) => state.chat.chat_options.draft_command);

  const chat = useChatStore((state) => state.chat);

  const updateChatOptions = useChatStore((state) => state.updateChatOptions);

  const handleSendMessage = useCallback(
    async (e?: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
      updateChatOptions({ draft_command: '' });

      if (onSubmit) onSubmit(command);

      if (e) e.currentTarget.blur();
    },
    [command, onSubmit],
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      editCommand(e.target.value);
      updateChatOptions({ draft_command: e.target.value });

      const mentionMatch = e.target.value.match(/@(\s*)$/);
      setShowChatOptions(!!mentionMatch);

      setTimeout(() => {
        chatOptionsInputRef?.current?.focus();
      }, 0);
    },
    [editCommand, updateChatOptions],
  );

  const handleKeyDown = useCallback(
    async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();

        await handleSendMessage();
      }

      if (textAreaRef.current) {
        const caretAtStart = textAreaRef.current.selectionStart === 0 && textAreaRef.current.selectionEnd === 0;
        const caretAtEnd =
          textAreaRef.current.selectionStart === textAreaRef.current.value.length &&
          textAreaRef.current.selectionEnd === textAreaRef.current.value.length;

        if (e.key === 'ArrowUp' && caretAtStart) {
          historyUp();
        } else if (e.key === 'ArrowDown' && caretAtEnd) {
          historyDown();
        }

        if (e.key === 'Backspace' && caretAtStart) {
          if (selectedMaterialIds.length > 0) {
            const newChosenMaterials = [...selectedMaterialIds];
            newChosenMaterials.pop();
            updateChatOptions({ materials_ids: newChosenMaterials });
          } else {
            updateChatOptions({ agent_id: '' });
          }
        }
      }
    },
    [handleSendMessage, historyDown, historyUp, updateChatOptions, selectedMaterialIds],
  );

  useEffect(() => {
    editCommand(draftCommand || '');
  }, [draftCommand, editCommand]);

  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.focus();
    }
  }, [chat.id]);

  useEffect(() => {
    textAreaRef.current?.setSelectionRange(draftCommand?.length || 0, draftCommand?.length || 0);
  }, []);

  const removeLastAt = () => {
    if (command.endsWith('@')) {
      const newCommand = command.slice(0, -1);
      editCommand(newCommand);
    }
  };

  const onSelectAgentId = (id: string) => {
    updateChatOptions({ agent_id: id, draft_command: '' });
    setShowChatOptions(false);
    removeLastAt();
    setTimeout(() => {
      textAreaRef?.current?.focus();
    }, 0);
  };

  const handleMaterialSelect = (material: Material) => {
    updateChatOptions({ materials_ids: [...selectedMaterialIds, material.id], draft_command: '' });
    setShowChatOptions(false);
    removeLastAt();
    setTimeout(() => {
      textAreaRef?.current?.focus();
    }, 0);
  };

  const handleFocus = useCallback(() => {
    setShowChatOptions(false);
  }, []);

  return (
    <div className={cn(className, 'flex w-full flex-col px-4 py-[20px] bg-gray-900 z-50')}>
      <div className="flex items-end gap-[10px] max-w-[700px] w-full mx-auto relative">
        {showChatOptions && (
          <ChatOptions
            onSelectAgentId={onSelectAgentId}
            handleMaterialSelect={handleMaterialSelect}
            setShowChatOptions={setShowChatOptions}
            inputRef={chatOptionsInputRef}
            textAreaRef={textAreaRef}
          />
        )}
        <div className="w-full overflow-y-auto border border-gray-500 focus-within:border-gray-400 transition duration-100 rounded-[8px] flex flex-col flex-grow resize-none">
          <CommandOptionsPanel />
          <TextareaAutosize
            ref={textAreaRef}
            className="w-full bg-transparent text-[15px] text-white resize-none overflow-y-auto px-[20px] py-[12px] placeholder:text-gray-400 focus:outline-none"
            value={command}
            onChange={handleChange}
            onFocus={handleFocus}
            onKeyDown={handleKeyDown}
            placeholder={`Type "@" to select a specific agent or materials`}
            rows={1}
            maxRows={4}
          />
        </div>

        <Tooltip label={actionLabel} position="top" align="center" sideOffset={10} disableAnimation withArrow>
          <div>
            <Button variant="primary" iconOnly={true} onClick={handleSendMessage} classNames={cn('p-[12px]', {})}>
              <Icon icon={ActionIcon} width={24} height={24} className="w-6 h-6" />
            </Button>
          </div>
        </Tooltip>
      </div>
    </div>
  );
};
