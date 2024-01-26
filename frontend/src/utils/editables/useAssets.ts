import { useMemo } from 'react';

import { EditablesAPI } from '@/api/api/EditablesAPI';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { Asset, EditableObjectType } from '@/types/editables/assetTypes';
import { useToastsStore } from '@/store/common/useToastsStore';

export const useAssets = (assetType: EditableObjectType) => {
  const asset = useAssetStore((state) => state.selectedAsset);
  const lastSavedAsset = useAssetStore((state) => state.lastSavedSelectedAsset);
  const showToast = useToastsStore((state) => state.showToast);

  const isAssetStatusChanged = useMemo(() => {
    if (!asset || !lastSavedAsset) {
      return false;
    }
    return asset.status !== lastSavedAsset.status;
  }, [asset, lastSavedAsset]);

  const updateStatusIfNecessary = async () => {
    if (assetType === 'chat') return;
    if (isAssetStatusChanged && asset) {
      await EditablesAPI.setAssetStatus(assetType, asset.id, asset.status);

      showToast({
        title: 'Status changed',
        message: `Status changed to ${asset.status}`,
        variant: 'success',
      });
    }
  };

  const renameAsset = async (previousAssetId: string, updatedAsset: Asset) => {
    await EditablesAPI.updateEditableObject(assetType, updatedAsset, previousAssetId);
    await updateStatusIfNecessary();
  };

  return {
    updateStatusIfNecessary,
    isAssetStatusChanged,
    renameAsset,
  };
};
