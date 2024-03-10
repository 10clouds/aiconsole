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

import { Circle, Copy, Edit, File, FolderOpenIcon, Trash, Undo2 } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import { useDeleteAssetWithUserInteraction } from './useDeleteAssetWithUserInteraction';
import { useMemo } from 'react';
import { RadioCheckedIcon } from '@/components/common/icons/RadioCheckedIcon';
import { noop } from '../common/noop';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { ContextMenuItem, ContextMenuItems } from '@/types/common/contextMenu';
import { Asset, AssetType } from '@/types/assets/assetTypes';
import { useWebSocketStore } from '@/api/ws/useWebSocketStore';

export const DISABLED_CSS_CLASSES = 'max-w-[400px] truncate !text-gray-400 pointer-events-none !cursor-default ';

const statusHelper = (enabled: boolean, asset: Asset): Omit<ContextMenuItem, 'type' | 'title'> => {
  const handleClick = (status: boolean) => () => {
    useAssetStore.getState().setIsEnabledFlag(asset.id, status);
  };

  const assetStatusIcon = (itemStatus: boolean) => {
    if ((asset as Asset)?.enabled === itemStatus) {
      return RadioCheckedIcon;
    }

    return Circle;
  };

  const activeItemClass = asset.enabled === enabled ? 'text-white' : 'text-gray-400';

  return {
    className: activeItemClass,
    iconClassName: activeItemClass,
    disabled: asset.enabled === enabled,
    icon: assetStatusIcon(enabled),
    hidden: !asset,
    action: asset.enabled === enabled ? noop : handleClick(enabled),
  };
};

const assetItems = (assetType: AssetType, asset: Asset): ContextMenuItems => {
  if (assetType === 'chat') return [];

  return [
    { type: 'separator', key: 'usage-separator' },
    {
      type: 'label',
      title: 'Usage',
    },

    {
      type: 'item',
      title: 'Enabled',
      ...statusHelper(true, asset),
    },

    {
      type: 'item',
      title: 'Disabled',
      ...statusHelper(false, asset),
    },
  ];
};

export function useAssetContextMenu({
  assetType,
  asset,
  setIsEditing,
}: {
  assetType: AssetType;
  asset?: Asset;
  setIsEditing?: (isEditing: boolean) => void;
}) {
  const navigate = useNavigate();
  const location = useLocation();
  const handleDelete = useDeleteAssetWithUserInteraction(assetType);
  const canOpenFinderForEditable = useAssetStore((state) => state.canOpenFinderForEditable);
  const openFinderForEditable = useAssetStore((state) => state.openFinderForEditable);

  const hasDelete = useMemo(
    () => (assetType === 'chat' ? true : (asset as Asset)?.defined_in === 'project'),
    [asset, assetType],
  );
  const isDeleteRevert = useMemo(
    () => (assetType === 'chat' ? false : (asset as Asset)?.override),
    [asset, assetType],
  );

  function getMenuItems() {
    if (!asset) {
      return [];
    }

    const content: ContextMenuItems = [
      {
        type: 'item',
        icon: Edit,
        title: 'Rename',
        hidden: !setIsEditing || (asset as Asset)?.defined_in === 'aiconsole',
        action: () => {
          if (!setIsEditing) {
            return;
          }
          setIsEditing(true);
        },
      },
      {
        type: 'item',
        icon: Copy,
        title: 'Duplicate',
        action: () => {
          (async () => {
            try {
              await useWebSocketStore
                .getState()
                .sendMessageAndWaitForResponse(
                  { type: 'DuplicateAssetClientMessage', asset_id: asset.id, request_id: uuidv4() },
                  (response) => {
                    if (response.type === 'DuplicateAssetServerMessage') {
                      navigate(`/assets/${response.asset_id}`);
                      return true;
                    }
                    return false;
                  },
                );
            } catch (error) {
              console.error('Error duplicating chat:', error);
            }
          })();
        },
      },
      {
        type: 'item',
        icon: File,
        title: 'Open',
        hidden: location.pathname === `/assets/${asset.id}`,
        action: () => {
          navigate(`/assets/${asset.id}`);
        },
      },
      {
        type: 'item',
        icon: FolderOpenIcon,
        title: `Reveal in ${window.window?.electron?.getFileManagerName()}`,
        hidden: !canOpenFinderForEditable(asset),
        action: () => {
          openFinderForEditable(asset);
        },
      },

      ...assetItems(assetType, asset),
      { type: 'separator', key: 'delete-separator', hidden: !hasDelete },
      {
        type: 'item',
        icon: isDeleteRevert ? Undo2 : Trash,
        title: isDeleteRevert ? 'Revert' : 'Delete',
        hidden: !hasDelete,
        action: () => handleDelete(asset.id),
      },
    ];

    return content;
  }

  const menuItems = getMenuItems();

  return menuItems;
}
