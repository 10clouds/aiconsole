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

import { useRef, MouseEvent, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { useAssetStore } from '@/store/assets/useAssetStore';
import { useUserContextMenu } from '@/utils/common/useUserContextMenu';
import { useAssetContextMenu } from '@/utils/assets/useContextMenuForEditable';
import { ActorAvatar } from './ActorAvatar';
import { ContextMenu, ContextMenuRef } from '@/components/common/ContextMenu';
import { cn } from '@/utils/common/cn';
import { useChatStore } from '@/store/assets/chat/useChatStore';
import { ActorId } from '@/types/assets/chatTypes';
import { AICUserProfile } from '@/types/assets/assetTypes';
import { useSettingsStore } from '@/store/settings/useSettingsStore';

function AgentInfoMaterialLink({
  materialId,
  isLoaded,
  isRunning,
}: {
  materialId: string;
  isLoaded: boolean;
  isRunning: boolean;
}) {
  const assets = useAssetStore((state) => state.assets) || [];
  const material = assets.find((m) => m.id === materialId);
  const menuItems = useAssetContextMenu({ assetType: 'material', asset: material });

  return (
    <ContextMenu options={menuItems}>
      <Link to={`/materials/${materialId}`}>
        <div
          className={cn(
            'text-[12px] text-center text-gray-400 whitespace-nowrap pb-1 max-w-[120px] px-[10px] truncate opacity-0',
            {
              'transition-opacity duration-500 opacity-40': isLoaded,
              'opacity-40': isRunning,
            },
          )}
          title={materialId}
        >
          {materialId}
        </div>
      </Link>
    </ContextMenu>
  );
}

export function ActorInfo({
  actorId,
  materialsIds,
  task,
}: {
  actorId: ActorId;
  materialsIds: string[];
  task?: string;
}) {
  const triggerRef = useRef<ContextMenuRef>(null);

  const [isLoaded, setIsLoaded] = useState(false);
  const isAnalysisRunning = useChatStore((state) => state.chat?.is_analysis_in_progress);
  const isExecutionRunning = useChatStore((state) => state.isExecutionRunning());
  const assets = useAssetStore((state) => state.assets) || [];
  const actor = assets.find((m) => m.id === actorId.id);
  const userMenuItems = useUserContextMenu();
  const userProfile = useSettingsStore((state) => state.settings.user_profile);

  const editableMenuItems = useAssetContextMenu({
    assetType: 'agent',
    asset: actor || {
      type: 'agent',
      id: actorId.id,
      name: actorId.id,
      version: '',
      defined_in: 'project',
      usage: '',
      usage_examples: [],
      enabled_by_default: false,
      enabled: true,
      override: false,
      last_modified: new Date().toISOString(),
    },
  });

  useEffect(() => {
    if (actor) {
      setIsLoaded(true);
    }
  }, [actor]);

  if (actorId.type === 'user') {
    const menuItems = userMenuItems;
    let user;

    if (actorId.id === 'user') {
      user = userProfile;
    } else {
      user = actor as AICUserProfile;
    }

    return (
      <ContextMenu options={menuItems} ref={triggerRef}>
        <Link to={''} className="flex-none items-center flex flex-col">
          <ActorAvatar actorId={`${actorId.id}`} actorType="user" title={`${user?.display_name}`} type="small" />
          <div
            className="text-[15px] w-32 text-center text-gray-300 max-w-[120px] truncate overflow-ellipsis overflow-hidden whitespace-nowrap"
            title={`${user?.display_name}`}
          >
            {user?.display_name}
          </div>
        </Link>
      </ContextMenu>
    );
  } else {
    const openContext = (event: MouseEvent) => {
      if (triggerRef.current && actorId.type === 'user') {
        triggerRef?.current.handleTriggerClick(event);
      }
    };

    const menuItems = actorId.type === 'agent' ? editableMenuItems : userMenuItems;
    return (
      <>
        <ContextMenu options={menuItems} ref={triggerRef}>
          <Link
            to={actorId.type === 'agent' ? `/assets/${actorId.id}` : ''}
            onClick={openContext}
            className="flex-none items-center flex flex-col"
          >
            <ActorAvatar
              actorType="agent"
              actorId={actorId.id}
              title={`${actor?.name || actorId}${task ? ` tasked with:\n${task}` : ``}`}
              type="small"
            />
            <div
              className={cn(
                'text-[15px] w-32 text-center text-gray-300 max-w-[120px] truncate overflow-ellipsis overflow-hidden whitespace-nowrap  opacity-0',
                {
                  'transition-opacity duration-500 opacity-100': isLoaded,
                  'opacity-100': !isAnalysisRunning && !isExecutionRunning,
                },
              )}
              title={`${actor?.id} - ${actor?.usage}`}
            >
              {actor?.name || actor?.id}
            </div>
          </Link>
        </ContextMenu>
        <div className="flex flex-col mt-2">
          {materialsIds.map((material_id) => (
            <AgentInfoMaterialLink
              key={material_id}
              materialId={material_id}
              isLoaded={isLoaded}
              isRunning={!isAnalysisRunning && !isExecutionRunning}
            />
          ))}
        </div>
      </>
    );
  }
}
