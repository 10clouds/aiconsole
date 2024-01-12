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

import { Icon } from '@/components/common/icons/Icon';
import { cn } from '@/utils/common/cn';
import { Trash, Pencil, Save, X } from 'lucide-react';
interface MessageControlsProps {
  isEditing?: boolean;
  hideControls?: boolean;
  onSaveClick?: () => void;
  onEditClick?: () => void;
  onRemoveClick?: () => void;
  onCancelClick?: () => void;
}

export function MessageControls({
  isEditing,
  hideControls,
  onSaveClick,
  onCancelClick,
  onEditClick,
  onRemoveClick,
}: MessageControlsProps) {
  return (
    <div className="min-w-[48px]">
      {isEditing ? (
        <div className="flex justify-between">
          <button>
            <Icon icon={Save} width={20} height={20} onClick={onSaveClick} />
          </button>
          <button>
            <Icon icon={X} width={20} height={20} onClick={onCancelClick} />{' '}
          </button>
        </div>
      ) : (
        <div
          className={cn('flex flex-none gap-4 justify-end', {
            'hidden group-hover:flex': hideControls,
          })}
        >
          {onSaveClick && onEditClick && onCancelClick ? (
            <button onClick={onEditClick}>
              <Icon icon={Pencil} className="pointer-events-none" />{' '}
            </button>
          ) : (
            <div className="h-4 w-4"></div>
          )}
          {onRemoveClick && (
            <button onClick={onRemoveClick}>
              <Icon icon={Trash} />{' '}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
