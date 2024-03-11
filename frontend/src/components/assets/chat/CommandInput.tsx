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
import { useAssetStore } from '@/store/assets/useAssetStore';
import { Material } from '@/types/assets/assetTypes';
import { cn } from '@/utils/common/cn';
import { BanIcon, LucideIcon, X } from 'lucide-react';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { ActorAvatar } from './ActorAvatar';
import ChatOptions from './ChatOptions';

interface MessageInputProps {
  actionIcon: LucideIcon | ((props: React.SVGProps<SVGSVGElement>) => JSX.Element);
  className?: string;
  actionLabel: string;
  onSubmit?: (command: string) => void;
  textAreaRef: React.RefObject<HTMLTextAreaElement>;
}

export const CommandInput = ({ className, onSubmit, actionIcon, actionLabel, textAreaRef }: MessageInputProps) => {
  const ActionIcon = actionIcon;
  const [showChatOptions, setShowChatOptions] = useState(false);
  const chatOptionsInputRef = useRef<HTMLInputElement>(null);

  const setSelectedAgentId = useChatStore((state) => state.setSelectedAgentId);
  const selectedAgentId = useChatStore((state) => state.chatOptions?.agentId);

  const setAICanAddExtraMaterials = useChatStore((state) => state.setAICanAddExtraMaterials);
  const aiCanAddExtraMaterials = useChatStore((state) => state.chatOptions?.aiCanAddExtraMaterials);

  const chat = useChatStore((state) => state.chat);
  const draftCommand = useChatStore((state) => state.chatOptions?.draft_command);
  const setDraftCommand = useChatStore((state) => state.setDraftCommand);
  const command = useChatStore((state) => state.commandHistory[state.commandIndex]);
  const setCommand = useChatStore((state) => state.editCommand);

  const promptUp = useChatStore((state) => state.historyUp);
  const promptDown = useChatStore((state) => state.historyDown);

  const assets = useAssetStore((state) => state.assets);
  const setSelectedMaterialIds = useChatStore((state) => state.setSelectedMaterialsIds);
  const selectedMaterialIds = useChatStore((state) => state.chatOptions?.materialsIds || []);

  const selectedMaterials = useMemo(
    () => assets?.filter(({ id }) => selectedMaterialIds.includes(id)) || [],
    [assets, selectedMaterialIds],
  );

  const handleSendMessage = useCallback(
    async (e?: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
      setDraftCommand('');

      if (onSubmit) onSubmit(command);

      if (e) e.currentTarget.blur();
    },
    [command, onSubmit],
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setCommand(e.target.value);
      setDraftCommand(e.target.value);
      const mentionMatch = e.target.value.match(/@(\s*)$/);
      setShowChatOptions(!!mentionMatch);

      setTimeout(() => {
        chatOptionsInputRef?.current?.focus();
      }, 0);
    },
    [setCommand],
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
          promptUp();
        } else if (e.key === 'ArrowDown' && caretAtEnd) {
          promptDown();
        }

        if (e.key === 'Backspace' && caretAtStart) {
          if (selectedMaterialIds.length > 0) {
            const newChosenMaterials = [...selectedMaterialIds];
            newChosenMaterials.pop();
            setSelectedMaterialIds(newChosenMaterials);
          } else {
            setSelectedAgentId('');
          }
        }
      }
    },
    [handleSendMessage, promptDown, promptUp, setSelectedAgentId, setSelectedMaterialIds, selectedMaterialIds],
  );

  // auto focus this text area on changes to chatId
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.focus();
    }
  }, [chat?.id]);

  useEffect(() => {
    setCommand(draftCommand || '');
  }, [draftCommand, setCommand]);

  useEffect(() => {
    textAreaRef.current?.setSelectionRange(draftCommand?.length || 0, draftCommand?.length || 0);
  }, []);

  const getAgent = (agentId: string) => assets.find((agent) => agent.id === agentId);

  const removeLastAt = () => {
    if (command.endsWith('@')) {
      const newCommand = command.slice(0, -1);
      setCommand(newCommand);
    }
  };

  const onSelectAgentId = (id: string) => {
    setSelectedAgentId(id);
    setShowChatOptions(false);
    removeLastAt();
    setTimeout(() => {
      textAreaRef?.current?.focus();
    }, 0);
  };

  const removeAgentId = () => {
    setSelectedAgentId('');
  };

  const handleMaterialSelect = (material: Material) => {
    setSelectedMaterialIds([...selectedMaterialIds, material.id]);
    setShowChatOptions(false);
    removeLastAt();
    setTimeout(() => {
      textAreaRef?.current?.focus();
    }, 0);
  };

  const removeSelectedMaterial = (id: string) => () => {
    const material = selectedMaterials.find((material) => material.id === id) as Material;
    setSelectedMaterialIds(selectedMaterialIds.filter((id) => id !== material.id).map((id) => id));
  };

  const handleFocus = useCallback(() => {
    setShowChatOptions(false);
  }, []);

  const handleAnalysisClick = () => {
    setAICanAddExtraMaterials(!aiCanAddExtraMaterials);
  };

  const clearChatOptions = () => {
    setSelectedAgentId('');
    setSelectedMaterialIds([]);
    setAICanAddExtraMaterials(true);
  };

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
          {(selectedAgentId || selectedMaterialIds.length > 0 || !aiCanAddExtraMaterials) && (
            <div className="bg-gray-600">
              <div className="px-[20px] py-[12px] w-full flex flex-wrap gap-2 items-center">
                <span className="text-gray-400 text-[14px]">Talking&nbsp;to</span>

                {selectedAgentId ? (
                  <>
                    <div
                      className="flex jusify-between items-center gap-2 bg-gray-700 px-[6px] py-[6px] rounded-[32px] cursor-pointer"
                      onClick={removeAgentId}
                    >
                      <div className="flex items-center gap-1 w-full">
                        <ActorAvatar
                          actorType="agent"
                          actorId={selectedAgentId}
                          type="extraSmall"
                          className="!mb-0 !mt-0"
                        />

                        <p className="text-[15px]">
                          <span className="text-white">{selectedAgentId ? getAgent(selectedAgentId)?.name : '?'}</span>
                        </p>

                        {selectedAgentId && <Icon icon={X} className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0')} />}
                      </div>
                    </div>
                  </>
                ) : (
                  <span title="AI will choose the agent">?</span>
                )}
                {selectedMaterials.length > 0 || !aiCanAddExtraMaterials ? (
                  <span className="text-gray-400 text-[14px]">using </span>
                ) : null}
                {selectedMaterials.map((material) => (
                  <div
                    key={material.id}
                    onClick={removeSelectedMaterial(material.id)}
                    className="flex gap-1 items-center bg-gray-700 px-[6px] py-[6px] rounded-[32px] cursor-pointer"
                  >
                    <span className="text-white text-[14px] pl-[4px]">{material.name}</span>
                    <Icon
                      icon={X}
                      className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer text-gray-400')}
                    />
                  </div>
                ))}
                {aiCanAddExtraMaterials ? (
                  <div
                    onClick={handleAnalysisClick}
                    title="Allows the AI to add more context to the conversation."
                    className="flex gap-1 items-center cursor-pointer"
                  >
                    <span className="text-gray-400  text-[14px]">with extra context</span>
                  </div>
                ) : (
                  <div
                    onClick={handleAnalysisClick}
                    title="No additonal context will be added to the conversation."
                    className="flex gap-1 items-center bg-gray-700 px-[6px] py-[6px] rounded-[32px] cursor-pointer text-[14px] text-material pl-[8px]"
                  >
                    <Icon icon={BanIcon} className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer')} />
                    No extra
                    <Icon
                      icon={X}
                      className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer text-gray-400')}
                    />
                  </div>
                )}

                <div className="ml-auto">
                  <Icon
                    icon={X}
                    className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer')}
                    onClick={clearChatOptions}
                  />
                </div>
              </div>
            </div>
          )}

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
