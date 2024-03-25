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
import { cn } from '@/utils/common/cn';
import { useCallback, useEffect, useState } from 'react';
import { CodeInput } from '../../CodeInput';
import { MessageControls } from './MessageControls';
import { useTTSStore } from '@/audio/useTTSStore';

interface EditableContentMessageProps {
  enableTTS?: boolean;
  initialContent: string;
  language?: string;
  children?: React.ReactNode;
  handleRemoveClick?: () => void;
  handleAcceptedContent: (content: string) => Promise<void>;
  className?: string;
  hideControls?: boolean;
  isEditing: boolean;
  setIsEditing: React.Dispatch<React.SetStateAction<boolean>>;
}

export function EditableContentMessage({
  enableTTS,
  initialContent,
  children,
  language,
  handleAcceptedContent,
  handleRemoveClick,
  hideControls,
  className,
  isEditing,
  setIsEditing,
}: EditableContentMessageProps) {
  const isBeingProcessed = useChatStore((state) => !!state.chat?.lock_id);
  const isPlaying = useTTSStore((state) => state.isPlaying);
  const numLoading = useTTSStore((state) => state.numLoading);
  const hasAutoPlay = useTTSStore((state) => state.hasAutoPlay);
  const readText = useTTSStore((state) => state.readText);
  const stopReading = useTTSStore((state) => state.stopReading);

  const [content, setContent] = useState(initialContent);

  useEffect(() => {
    setContent(initialContent);
  }, [initialContent]);

  const handleEditClick = () => {
    if (isBeingProcessed) {
      return;
    }
    setContent(initialContent);
    setIsEditing(true);
  };

  const handleCancelEditClick = useCallback(() => {
    setIsEditing(false);
    setContent(initialContent);
  }, [initialContent, setIsEditing, setContent]);

  const handleOnChange = (value: string) => setContent(value);

  const handleSaveClick = useCallback(async () => {
    await handleAcceptedContent(content);
    setIsEditing(false);
  }, [content, handleAcceptedContent, setIsEditing]);

  const handlePlayClick = useCallback(async () => {
    await readText(content, false);
  }, [content, readText]);

  const handleStopClick = useCallback(() => {
    stopReading();
  }, [stopReading]);

  return (
    <div className={cn('flex flex-row items-start overflow-auto', className)}>
      {isEditing ? (
        <div className="rounded-md flex-grow ">
          <CodeInput
            className="resize-none border-0 bg-transparent w-full outline-none"
            value={content}
            onChange={handleOnChange}
            codeLanguage={language ? language : 'text'}
            transparent
            focused={isEditing}
            maxHeight="400px"
            minHeight="400px"
            onBlur={handleSaveClick}
          />
        </div>
      ) : (
        <div className="flex-grow overflow-auto ">{children}</div>
      )}

      <div
        className={cn('flex flex-none gap-4 px-4 self-start', {
          'min-w-[112px] ml-[92px]': hideControls,
        })}
      >
        {!isBeingProcessed && (
          <MessageControls
            isEditing={isEditing}
            hideControls={hideControls}
            onPlayClick={enableTTS ? handlePlayClick : undefined}
            onPlayStopClick={enableTTS ? handleStopClick : undefined}
            isSoundHighlighted={hasAutoPlay}
            isSoundLoading={numLoading > 0 && !isPlaying}
            onCancelClick={handleCancelEditClick}
            onEditClick={handleEditClick}
            onSaveClick={handleSaveClick}
            onRemoveClick={handleRemoveClick}
          />
        )}
      </div>
    </div>
  );
}
