import { useChatStore } from '@/store/assets/chat/useChatStore';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { Material } from '@/types/assets/assetTypes';
import { useMemo } from 'react';
import { ActorAvatar } from './ActorAvatar';
import { BanIcon, X } from 'lucide-react';
import { Icon } from '@/components/common/icons/Icon';
import { cn } from '@/utils/common/cn';
import React from 'react';

export const CommandOptionsPanel = React.memo(() => {
  const updateChatOptions = useChatStore((state) => state.updateChatOptions);
  const selectedAgentId = useChatStore((state) => state.chat.chat_options.agent_id);
  const aiCanAddExtraMaterials = useChatStore((state) => state.chat.chat_options.ai_can_add_extra_materials);
  const selectedMaterialIds = useChatStore((state) => state.chat.chat_options.materials_ids);

  const assets = useAssetStore((state) => state.assets);

  const selectedMaterials = useMemo(
    () => assets?.filter(({ id }) => selectedMaterialIds.includes(id)) || [],
    [assets, selectedMaterialIds],
  );

  const getAgent = (agentId: string) => assets.find((agent) => agent.id === agentId);

  const removeAgentId = () => {
    updateChatOptions({ agent_id: '' });
  };

  const removeSelectedMaterial = (id: string) => () => {
    const material = selectedMaterials.find((material) => material.id === id) as Material;
    updateChatOptions({ materials_ids: selectedMaterialIds.filter((id) => id !== material.id).map((id) => id) });
  };

  const handleAnalysisClick = () => {
    updateChatOptions({ ai_can_add_extra_materials: !aiCanAddExtraMaterials });
  };

  const clearChatOptions = () => {
    updateChatOptions({ agent_id: '', materials_ids: [], ai_can_add_extra_materials: true });
  };
  return (
    <>
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
                <Icon icon={X} className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer text-gray-400')} />
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
                <Icon icon={X} className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer text-gray-400')} />
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
    </>
  );
});
