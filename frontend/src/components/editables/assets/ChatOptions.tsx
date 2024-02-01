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

import { useDebounceCallback } from '@mantine/hooks';
import * as Collapsible from '@radix-ui/react-collapsible';
import { Content, DropdownMenu, Item, Trigger } from '@radix-ui/react-dropdown-menu';
import { ArrowDownLeftSquare, ArrowUpRightSquare, ChevronDown, ChevronUp, X } from 'lucide-react';
import { useEffect, useState } from 'react';

import Checkbox from '@/components/common/Checkbox';
import { Icon } from '@/components/common/icons/Icon';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { Agent, Material } from '@/types/editables/assetTypes';
import { cn } from '@/utils/common/cn';
import { getEditableObjectIcon } from '@/utils/editables/getEditableObjectIcon';

import { AgentAvatar } from '../chat/AgentAvatar';
import Autocomplete from './Autocomplete';
import { ChatAPI } from '@/api/api/ChatAPI';

const ChatOptions = () => {
  const chat = useChatStore((state) => state.chat);
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials);
  const setChat = useChatStore((state) => state.setChat);
  const isChatLoading = useChatStore((state) => state.isChatLoading);
  const isChatOptionsExpanded = useChatStore((state) => state.isChatOptionsExpanded);
  const setIsChatOptionsExpanded = useChatStore((state) => state.setIsChatOptionsExpanded);

  const [materialsOptions, setMaterialsOptions] = useState<Material[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [chosenMaterials, setChosenMaterials] = useState<Material[]>([]);
  const [allowExtraMaterials, setAllowExtraMaterials] = useState<boolean>(false);
  const materialsIds = chosenMaterials.map((material) => material.id);

  useEffect(() => {
    setSelectedAgentId('');
    setChosenMaterials([]);
    setAllowExtraMaterials(false);
  }, [chat?.id]);

  useEffect(() => {
    if (chat?.chat_options.agent_id) {
      setSelectedAgentId(chat?.chat_options.agent_id);
    }
  }, [chat?.chat_options.agent_id, chat?.id]);

  useEffect(() => {
    const filteredMaterials = materials?.filter(({ id }) => (chat?.chat_options.materials_ids || []).includes(id));
    if (filteredMaterials) {
      setChosenMaterials(filteredMaterials);
    }
  }, [chat?.chat_options.materials_ids, materials, chat?.id]);

  useEffect(() => {
    if (chat?.chat_options.let_ai_add_extra_materials) {
      setAllowExtraMaterials(chat?.chat_options.let_ai_add_extra_materials);
    }
  }, [chat?.chat_options.let_ai_add_extra_materials, chat?.id]);

  const debounceChatUpdate = useDebounceCallback(async () => {
    try {
      if (chat) {
        ChatAPI.patchChatOptions(chat?.id, {
          agent_id: selectedAgentId,
          materials_ids: ['today', ...materialsIds],
          let_ai_add_extra_materials: allowExtraMaterials,
        });

        setChat({
          ...chat,
          chat_options: {
            agent_id: selectedAgentId,
            materials_ids: materialsIds,
            let_ai_add_extra_materials: allowExtraMaterials,
          },
        });
      }
    } catch (error) {
      console.error('An error occurred while updating chat options:', error);
    }
  }, 500);

  const onSelectAgentId = (id: string) => {
    setSelectedAgentId(id);
    debounceChatUpdate();
  };

  const handleMaterialSelect = (material: Material) => {
    setChosenMaterials((prev) => [...prev, material]);
    const filteredOptions = materialsOptions.filter(({ id }) => id !== material.id);
    setMaterialsOptions(filteredOptions);
    debounceChatUpdate();
  };

  const removeSelectedMaterial = (id: string) => {
    const material = chosenMaterials.find((material) => material.id === id) as Material;
    setChosenMaterials((prev) => prev.filter(({ id }) => id !== material.id));
    setMaterialsOptions((prev) => [...prev, material].sort((a, b) => a.name.localeCompare(b.name)));
    debounceChatUpdate();
  };

  const changeAllowExtraMaterials = (checked: boolean) => {
    setAllowExtraMaterials(checked);
    debounceChatUpdate();
  };

  useEffect(() => {
    setMaterialsOptions(materials?.filter((material) => !chosenMaterials.includes(material)) as Material[]);
  }, [chat?.id, materials, chosenMaterials]);

  if (!chat && !isChatLoading) {
    return;
  }

  return (
    <div className="text-gray-300 flex flex-col gap-5 flex-1">
      <Collapsible.Root open={isChatOptionsExpanded} onOpenChange={setIsChatOptionsExpanded}>
        <Collapsible.Trigger className="w-full pt-5">
          <div className="w-full flex justify-between group h-6 transition ease-in-out">
            <h3 className="text-sm">Chat options</h3>
            <div className="hidden group-hover:block">
              {isChatOptionsExpanded ? (
                <ArrowDownLeftSquare className="stroke-[1.2]" />
              ) : (
                <ArrowUpRightSquare className="stroke-[1.2]" />
              )}
            </div>
          </div>
        </Collapsible.Trigger>
        <Collapsible.Content className="CollapsibleContent">
          <div className="pt-5 flex flex-col gap-5">
            <div className="flex flex-col gap-2.5">
              <label htmlFor="agents" className="text-xs">
                Selected agent
              </label>
              <AgentsDropdown
                agents={agents}
                selectedAgent={agents.find(({ id }) => id === selectedAgentId)}
                onSelect={onSelectAgentId}
              />
            </div>

            <div className="flex flex-col gap-2.5">
              <label className="text-xs">Selected materials</label>
              <div className="h-[190px] overflow-y-auto ">
                <div className="flex flex-col gap-2.5 w-full">
                  {chosenMaterials.map((option) => (
                    <ChatOption option={option} onRemove={removeSelectedMaterial} key={option.id} />
                  ))}
                </div>
                <Autocomplete options={materialsOptions} onOptionSelect={handleMaterialSelect} />
              </div>
            </div>

            <div className="flex items-center gap-2.5 mt-auto">
              <Checkbox
                id="extraMaterials"
                checked={allowExtraMaterials}
                onChange={changeAllowExtraMaterials}
                disabled={isChatLoading}
              />
              <label htmlFor="extraMaterials" className="text-sm">
                Let AI add extra materials
              </label>
            </div>
          </div>
        </Collapsible.Content>
      </Collapsible.Root>
    </div>
  );
};

const ChatOption = ({ option, onRemove }: { option: Material; onRemove: (id: string) => void }) => {
  const OptionIcon = getEditableObjectIcon(option);

  return (
    <div className="flex justify-between items-center max-w-full w-max gap-2.5 bg-gray-700 px-2.5 py-2 rounded-[20px]">
      <Icon icon={OptionIcon} className="w-6 h-6 min-h-6 min-w-6 text-material" />
      <p className="flex-1 truncate font-normal text-sm">{option.name}</p>
      <button onClick={() => onRemove(option.id)}>
        <Icon icon={X} />
      </button>
    </div>
  );
};

type AgentsDropdownProps = {
  agents: Agent[];
  selectedAgent?: Agent;
  onSelect: (agentId: string) => void;
};

const AgentsDropdown = ({ agents, selectedAgent, onSelect }: AgentsDropdownProps) => {
  const [opened, setOpened] = useState<boolean>(false);
  const isChatLoading = useChatStore((state) => state.isChatLoading);

  return (
    <DropdownMenu open={opened} onOpenChange={setOpened}>
      <Trigger asChild disabled={isChatLoading}>
        <button
          className={cn(
            'group flex justify-center items-center gap-[12px] rounded-[8px] border border-gray-500 px-[16px] py-[10px] text-gray-300 text-[16px] w-full leading-[23px] hover:border-gray-300 transition duration-200 hover:text-gray-300 disabled:hover:border-gray-500',
            {
              'rounded-b-none bg-gray-700 border-gray-800 text-gray-500': opened,
            },
          )}
        >
          {selectedAgent ? (
            <div className="flex gap-2.5 items-center">
              <AgentAvatar agentId={selectedAgent.id} type="extraSmall" className="!m-0" />
              <p>{selectedAgent.name}</p>
            </div>
          ) : (
            <p>AI Choice</p>
          )}
          <Icon
            icon={opened ? ChevronUp : ChevronDown}
            width={24}
            height={24}
            className="text-gray-500 ml-auto group-hover:text-gray-300 transition duration-200 w-[24px] h-[24px]"
          />
        </button>
      </Trigger>

      <Content
        className={cn('bg-gray-700 border-t-0 border-gray-800 p-0 w-[295px] h-40 overflow-auto z-50', {
          'rounded-t-none ': opened,
        })}
      >
        <Item
          className="group flex p-0 rounded-none hover:bg-gray-600 hover:outline-none w-full cursor-pointer"
          onClick={() => onSelect('')}
        >
          <div className="flex items-center h-11 gap-[12px] px-[16px] py-[10px] text-[14px] text-gray-300 group-hover:text-white w-full">
            <p>AI Choice</p>
          </div>
        </Item>
        {agents
          .sort((a, b) => a.name.localeCompare(b.name))
          .map(({ id, name }) => (
            <Item
              key={id}
              onClick={() => onSelect(id)}
              className="group flex p-0 rounded-none hover:bg-gray-600 hover:outline-none w-full cursor-pointer"
            >
              <div className="flex items-center gap-[12px] px-[16px] py-[10px] text-[14px] text-gray-300 group-hover:text-white w-full">
                <AgentAvatar agentId={id} type="extraSmall" className="!m-0" />
                <p>{name}</p>
              </div>
            </Item>
          ))}
      </Content>
    </DropdownMenu>
  );
};

export default ChatOptions;
