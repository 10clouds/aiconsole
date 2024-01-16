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

import { useRef, MouseEvent, useMemo } from 'react';

import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { Agent, Asset, AssetType } from '@/types/editables/assetTypes';
import { getEditableObjectIcon } from '@/utils/editables/getEditableObjectIcon';
import { useEditableObjectContextMenu } from '@/utils/editables/useContextMenuForEditable';
import { useProjectContextMenu } from '@/utils/projects/useProjectContextMenu';
import { AgentAvatar } from './AgentAvatar';
import { cn } from '@/utils/common/cn';
import { ContextMenu, ContextMenuRef } from '@/components/common/ContextMenu';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation } from 'swiper/modules';
import { SliderArrowLeft } from '@/components/common/icons/SliderArrowLeft';
import { SliderArrowRight } from '@/components/common/icons/SliderArrowRight';
import 'swiper/css';
import 'swiper/css/navigation';
import { Button } from '@/components/common/Button';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useSidebarStore } from '@/store/common/useSidebarStore';
import { LeaveProjectDialog } from '@/components/common/LeaveProjectDialog';

function EmptyChatAgentAvatar({ agent }: { agent: Agent }) {
  const menuItems = useEditableObjectContextMenu({ editableObjectType: 'agent', editable: agent });
  const contextMenuRef = useRef<ContextMenuRef>(null);
  const handleClick = (event: MouseEvent) => {
    contextMenuRef.current?.handleTriggerClick(event);
  };

  return (
    <ContextMenu options={menuItems} ref={contextMenuRef}>
      <div
        key={agent.id}
        onClick={handleClick}
        className={cn(
          'flex flex-col justify-center items-center text-gray-400  hover:text-gray-300 cursor-pointer min-w-[110px]',
          {
            'text-agent': agent.status === 'forced',
          },
        )}
      >
        <AgentAvatar agentId={agent.id} type="small" className="mb-[10px] mt-[5px]" />
        <p className="text-[15px] text-center">{agent.name}</p>
      </div>
    </ContextMenu>
  );
}

function EmptyChatAssetLink({ assetType, asset }: { assetType: AssetType; asset: Asset }) {
  const menuItems = useEditableObjectContextMenu({ editableObjectType: assetType, editable: asset });
  const Icon = getEditableObjectIcon(asset);
  const contextMenuRef = useRef<ContextMenuRef>(null);
  const handleClick = (event: MouseEvent) => {
    contextMenuRef.current?.handleTriggerClick(event);
  };

  return (
    <ContextMenu options={menuItems} ref={contextMenuRef}>
      <div className="inline-block cursor-pointer" onClick={handleClick}>
        <div className="group py-2 flex items-center gap-[12px] text-[14px] text-gray-300 hover:text-white">
          <Icon className="w-6 h-6 text-gray-500 group-hover:text-material" />
          <p className="max-w-[160px] truncate">{asset.name}</p>
        </div>
      </div>
    </ContextMenu>
  );
}

const MAX_ASSETS_TO_DISPLAY = 6;

export const EmptyChat = () => {
  const projectName = useProjectStore((state) => state.projectName);
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials || []);
  const { menuItems, isDialogOpen, closeDialog } = useProjectContextMenu();
  const aiChoiceMaterials = materials.filter((m) => m.status === 'enabled');
  const activeSystemAgents = agents.filter((agent) => agent.status !== 'disabled' && agent.id !== 'user');
  const forcedMaterials = materials.filter((m) => m.status === 'forced');
  const triggerRef = useRef<ContextMenuRef>(null);
  const hasForcedMaterials = forcedMaterials.length > 0;
  const hasAiChoiceMaterials = aiChoiceMaterials.length > 0;
  const submitCommand = useChatStore((state) => state.submitCommand);
  const setActiveTab = useSidebarStore((state) => state.setActiveTab);

  const openContext = (event: MouseEvent) => {
    if (triggerRef.current) {
      triggerRef?.current.handleTriggerClick(event);
    }
  };

  const remainingAssetCount = useMemo(
    () => aiChoiceMaterials.length - MAX_ASSETS_TO_DISPLAY,
    [aiChoiceMaterials.length],
  );

  const guideMe = () =>
    submitCommand(
      `I need help with using AIConsole, can you suggest what can I do from this point in the conversation?`,
    );

  return (
    <section className="flex flex-col items-center justify-center container mx-auto px-6 py-[80px] pb-[40px] select-none">
      <img src="chat-page-glow.png" alt="glow" className="absolute top-[40px] -z-[1]" />
      <p className="text-[16px] text-gray-300 text-center mb-[15px]">Welcome to the project</p>
      <ContextMenu options={menuItems} ref={triggerRef}>
        <h2
          className="text-[36px] text-center font-black cursor-pointer uppercase text-white mb-[40px]"
          onClick={openContext}
        >
          {projectName}
        </h2>
      </ContextMenu>
      {activeSystemAgents.length > 0 ? (
        <>
          <p className="mb-[11px] text-center text-[14px] text-gray-400">Agents in the project:</p>
          <div className="flex items-center justify-center mb-8 w-full max-w-[700px] mx-auto">
            <SliderArrowLeft className="swiper-left text-gray-400 cursor-pointer" />
            <Swiper
              modules={[Navigation]}
              navigation={{ nextEl: '.swiper-right', prevEl: '.swiper-left' }}
              spaceBetween={0}
              centerInsufficientSlides
              slidesPerView={MAX_ASSETS_TO_DISPLAY}
              className="w-full"
            >
              {activeSystemAgents.map((agent) => (
                <SwiperSlide className="width-[110px]" key={agent.id}>
                  <EmptyChatAgentAvatar agent={agent} />
                </SwiperSlide>
              ))}
            </Swiper>
            <SliderArrowRight className="swiper-right text-gray-400 cursor-pointer" />
          </div>
        </>
      ) : null}

      <div className="max-w-[700px]">
        <p className="mb-4 text-center text-[14px] text-gray-400">Custom materials in the project:</p>
        {hasForcedMaterials && (
          <div
            className={cn('flex gap-[14px] py-[10px]', {
              'border-b border-gray-600': hasAiChoiceMaterials,
            })}
          >
            <p className="text-[14px] text-gray-400 py-2 min-w-[116px]">User enforced:</p>
            <div className="flex flex-wrap gap-[20px]">
              {forcedMaterials.map(
                (material, index) =>
                  index < MAX_ASSETS_TO_DISPLAY && (
                    <EmptyChatAssetLink assetType="material" asset={material} key={material.id} />
                  ),
              )}
            </div>
          </div>
        )}
        {hasAiChoiceMaterials && (
          <div className="flex gap-[14px] py-[10px]">
            <p className="text-[14px] py-2 text-gray-400 min-w-[116px]">AI choice:</p>
            <div className="flex flex-wrap gap-x-[20px]">
              {aiChoiceMaterials.map(
                (material, index) =>
                  index < MAX_ASSETS_TO_DISPLAY && (
                    <EmptyChatAssetLink assetType="material" asset={material} key={material.id} />
                  ),
              )}
            </div>
          </div>
        )}
        {hasAiChoiceMaterials || hasForcedMaterials ? (
          <p
            className=" text-gray-400 text-right text-[14px] cursor-pointer hover:text-gray-300"
            onClick={() => setActiveTab('materials')}
          >
            and {remainingAssetCount} more...
          </p>
        ) : null}
        <Button classNames="mx-auto mt-[40px]" variant="secondary" transparent onClick={guideMe}>
          Guide me
        </Button>
      </div>
      <LeaveProjectDialog onCancel={closeDialog} isOpen={isDialogOpen} />
    </section>
  );
};
