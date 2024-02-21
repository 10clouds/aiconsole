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

import { ActorInfo } from '@/components/editables/chat/ActorInfo';
import { cn } from '@/utils/common/cn';
import { useState } from 'react';
import { AICMessageGroup } from '../../../types/editables/chatTypes';
import { AnalysisClosed, AnalysisOpened } from './Analysis';
import { MessageComponent } from './messages/MessageComponent';
import { MessageControls } from './messages/MessageControls';
import { useChatStore } from '@/store/editables/chat/useChatStore';

export function MessageGroup({ group }: { group: AICMessageGroup }) {
  const [isAnalysisManuallyOpen, setIsAnalysisManuallyOpen] = useState<boolean | undefined>(undefined);
  const isBeingProcessed = useChatStore((state) => !!state.chat?.lock_id);

  const lockId = useChatStore((state) => state.chat?.lock_id);

  const isOpen = isAnalysisManuallyOpen === undefined ? group.messages.length === 0 : isAnalysisManuallyOpen;

  return (
    <div
      className={cn('group flex flex-row shadow-md border-b border-gray-600 py-[30px] px-[10px] bg-gray-900', {
        'message-gradient': group.role === 'assistant' || group.role === 'system',
      })}
    >
      <div className="container flex mx-auto gap-[92px] max-w-[1104px]">
        <div className="flex-none items-center flex flex-col max-w-[120px] ">
          <ActorInfo actorId={group.actor_id} materialsIds={group.materials_ids} task={group.task} />

          {group.messages && !isOpen && (
            <AnalysisClosed group={group} onClick={() => setIsAnalysisManuallyOpen(!isOpen)} />
          )}
        </div>
        <div className="flex-grow flex flex-col gap-5 overflow-x-auto">
          <AnalysisOpened group={group} onClick={() => setIsAnalysisManuallyOpen(!isOpen)} isOpen={isOpen} />
          {group.messages.map((message) => (
            <MessageComponent key={message.id} message={message} group={group} />
          ))}
        </div>
        {!isBeingProcessed && group.messages.length === 0 && (
          <MessageControls
            hideControls={!!lockId}
            onRemoveClick={() => {
              useChatStore.getState().userMutateChat({
                type: 'DeleteMessageGroupMutation',
                message_group_id: group.id,
              });
            }}
          />
        )}
      </div>
    </div>
  );
}
