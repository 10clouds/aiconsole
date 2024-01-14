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

import { useRef, MouseEvent } from 'react';
import { Link } from 'react-router-dom';

import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { useUserContextMenu } from '@/utils/common/useUserContextMenu';
import { useEditableObjectContextMenu } from '@/utils/editables/useContextMenuForEditable';
import { AgentAvatar } from './AgentAvatar';
import { ContextMenu, ContextMenuRef } from '@/components/common/ContextMenu';

function AgentInfoMaterialLink({ materialId }: { materialId: string }) {
  const materials = useEditablesStore((state) => state.materials) || [];
  const material = materials.find((m) => m.id === materialId);
  const menuItems = useEditableObjectContextMenu({ editableObjectType: 'material', editable: material });

  return (
    <ContextMenu options={menuItems}>
      <Link to={`/materials/${materialId}`}>
        <div
          className="text-[12px] text-center text-gray-400 whitespace-nowrap pb-1 max-w-[120px] px-[10px] truncate"
          title={materialId}
        >
          {materialId}
        </div>
      </Link>
    </ContextMenu>
  );
}

export function AgentInfo({
  agentId,
  materialsIds,
  task,
}: {
  agentId: string;
  materialsIds: string[];
  task?: string;
}) {
  const agents = useEditablesStore((state) => state.agents) || [];
  const agent = agents.find((m) => m.id === agentId);

  const editableMenuItems = useEditableObjectContextMenu({
    editableObjectType: 'agent',
    editable: agent || {
      id: agentId,
      name: agentId,
    },
  });

  const triggerRef = useRef<ContextMenuRef>(null);

  const openContext = (event: MouseEvent) => {
    if (triggerRef.current && agentId === 'user') {
      triggerRef?.current.handleTriggerClick(event);
    }
  };

  const userMenuItems = useUserContextMenu();

  const menuItems = agentId !== 'user' ? editableMenuItems : userMenuItems;

  return (
    <>
      <ContextMenu options={menuItems} ref={triggerRef}>
        <Link
          to={agentId != 'user' ? `/agents/${agentId}` : ''}
          onClick={openContext}
          className="flex-none items-center flex flex-col"
        >
          <AgentAvatar
            agentId={agentId}
            title={`${agent?.name || agentId}${task ? ` tasked with:\n${task}` : ``}`}
            type="small"
          />
          <div
            className="text-[15px] w-32 text-center text-gray-300 max-w-[120px] truncate overflow-ellipsis overflow-hidden whitespace-nowrap"
            title={`${agent?.id} - ${agent?.usage}`}
          >
            {agent?.name || agent?.id}
          </div>
        </Link>
      </ContextMenu>
      {materialsIds.length > 0 && <div className="text-xs opacity-40 text-center">+</div>}
      {materialsIds.map((material_id) => (
        <AgentInfoMaterialLink key={material_id} materialId={material_id} />
      ))}
    </>
  );
}
