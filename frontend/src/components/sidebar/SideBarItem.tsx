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

import { AssetsAPI } from '@/api/api/AssetsAPI';
import { ContextMenu, ContextMenuRef } from '@/components/common/ContextMenu';
import { Icon } from '@/components/common/icons/Icon';
import { useToastsStore } from '@/store/common/useToastsStore';
import { useChatStore } from '@/store/assets/chat/useChatStore';
import { AICChat } from '@/types/assets/chatTypes';
import { cn } from '@/utils/common/cn';
import { convertNameToId } from '@/utils/assets/convertNameToId';
import { getAssetIcon } from '@/utils/assets/getAssetIcon';
import { useAssets } from '@/utils/assets/useAssets';
import { useAssetContextMenu } from '@/utils/assets/useContextMenuForEditable';
import { MoreVertical } from 'lucide-react';
import { KeyboardEvent, MouseEvent, useEffect, useRef, useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { Asset } from '@/types/assets/assetTypes';
import { useAssetStore } from '@/store/assets/useAssetStore';

const SideBarItem = ({ asset }: { asset: Asset }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const setLastUsedChat = useChatStore((state) => state.setLastUsedChat);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const renameChat = useChatStore((state) => state.renameChat);
  const setIsChatLoading = useChatStore((state) => state.setIsChatLoading);

  const [isEditing, setIsEditing] = useState(false);
  const [isShowingContext, setIsShowingContext] = useState(false);
  const [blockBlur, setBlockBlur] = useState(false);

  const showToast = useToastsStore((state) => state.showToast);

  const { renameAsset } = useAssets(asset.type);
  const menuItems = useAssetContextMenu({
    assetType: asset.type,
    asset: asset,
    setIsEditing,
  });

  const EditableIcon = getAssetIcon(asset);

  const [inputText, setInputText] = useState(asset.name);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing) {
      setInputText(asset.name);
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 0);
    }
  }, [isEditing, asset.name, setIsEditing]);

  const hideInput = () => {
    setIsEditing(false);
  };

  const handleRename = async () => {
    const previousObjectId = asset.id;
    if (inputText === '' || asset.name === inputText) {
      setInputText(asset.name);
    } else {
      const newId = convertNameToId(inputText);
      asset = {
        ...asset,
        id: newId,
        name: inputText,
      };

      if (asset.type === 'chat') {
        const chat = await AssetsAPI.fetchAsset<AICChat>({
          assetType: asset.type,
          id: previousObjectId,
        });
        asset = { ...chat, name: inputText, title_edited: true } as AICChat;
        await renameChat(asset as AICChat);
        if (location.pathname !== `/assets/${chat.id}`) {
          navigate(`/assets/${chat.id}`);
        }
      } else {
        await renameAsset(previousObjectId, asset as Asset);
        if (location.pathname === `/${asset.type}s/${previousObjectId}`) {
          navigate(`/assets/${newId}`);
        }
      }
      showToast({
        title: 'Overwritten',
        message: `The ${asset.type} has been successfully overwritten.`,
        variant: 'success',
      });
    }
    hideInput();
  };

  const handleBlur = () => {
    // when onKeyDown event was emitted input was losing focus and blur event was fired to - this blocker prevent this situation
    if (blockBlur) {
      setBlockBlur(false);
      return;
    }

    handleRename();
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.code === 'Escape') {
      setInputText(asset.name);
      hideInput();
      setBlockBlur(true);
    }

    if (event.code === 'Enter') {
      setBlockBlur(true);
      handleRename();
    }
  };

  let disabled = false;

  if (asset.type === 'agent' || asset.type === 'material') {
    disabled = !asset.enabled;
  }

  const triggerRef = useRef<ContextMenuRef>(null);

  const handleLinkClick = () => {
    setSelectedAsset(asset);
    if (asset.type === 'chat' && asset.id !== useAssetStore.getState().selectedAsset?.id) {
      setIsChatLoading(true);
    } else if (asset.type !== 'chat') {
      setLastUsedChat(undefined);
    }
  };

  const handleMoreIconClick = (event: MouseEvent) => {
    event.preventDefault();
    if (triggerRef.current) {
      triggerRef?.current.handleTriggerClick(event);
    }
  };

  const handleOpenContextChange = (open: boolean) => {
    setIsShowingContext(open);
  };

  return (
    <ContextMenu options={menuItems} ref={triggerRef} onOpenChange={handleOpenContextChange}>
      <div className="max-w-[295px] mb-[5px]">
        <div
          className={cn(
            false && asset.type === 'agent' && 'text-agent',
            false && asset.type === 'material' && 'text-material',
            disabled && 'opacity-50',
          )}
        >
          <NavLink
            className={({ isActive, isPending }) => {
              return cn(
                'group flex items-center gap-[12px] overflow-hidden p-[9px] rounded-[8px] cursor-pointer relative  hover:bg-gray-700',
                {
                  'bg-gray-700 text-white ': isActive || isPending || isShowingContext,
                },
              );
            }}
            to={`/assets/${asset.id}`}
            onClick={handleLinkClick}
          >
            {({ isActive }) => (
              <>
                <Icon
                  icon={EditableIcon}
                  className={cn(
                    'min-w-[24px] min-h-[24px] w-[24px] h-[24px]',
                    asset.type === 'chat' && 'text-chat',
                    asset.type === 'agent' && 'text-agent',
                    asset.type === 'material' && 'text-material',
                  )}
                />
                {/* TODO: add validation for empty input value */}
                {isEditing ? (
                  <input
                    className="font-normal outline-none border h-[24px] border-gray-400 text-[14px] p-[5px] w-full text-white bg-gray-600 focus:border-primary resize-none overflow-hidden rounded-[4px]  focus:outline-none"
                    value={inputText}
                    ref={inputRef}
                    onBlur={handleBlur}
                    onKeyDown={handleKeyDown}
                    onChange={(e) => setInputText(e.target.value)}
                    autoFocus
                  />
                ) : (
                  <p className="text-[14px] leading-[18.2px] group-hover:text-white truncate">{asset.name}</p>
                )}
                <div className="flex gap-[10px] ml-auto items-center">
                  <Icon
                    icon={MoreVertical}
                    className={cn(
                      'min-h-[16px] min-w-[16px] ml-auto hidden group-hover:text-white group-hover:block',
                      {
                        block: isShowingContext,
                      },
                    )}
                    onClick={handleMoreIconClick}
                  />
                </div>
                <div
                  className={cn(
                    'absolute bottom-[-15px] hidden left-[0px] opacity-[0.3] blur-[10px]  h-[34px] w-[34px] group-hover:block',
                    asset.type === 'chat' && 'fill-chat bg-chat',
                    asset.type === 'agent' && 'fill-agent bg-agent',
                    asset.type === 'material' && 'fill-material bg-material',
                    {
                      block: isActive,
                    },
                  )}
                />
              </>
            )}
          </NavLink>
        </div>
      </div>
    </ContextMenu>
  );
};

export default SideBarItem;
