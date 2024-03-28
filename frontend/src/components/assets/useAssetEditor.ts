import { AssetsAPI } from '@/api/api/AssetsAPI';
import { Asset } from '@/store/assets/constructors';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { AssetType } from '@/types/assets/assetTypes';
import { convertNameToId } from '@/utils/assets/convertNameToId';
import { useAssetChanged } from '@/utils/assets/useAssetChanged';
import { useDeleteAssetWithUserInteraction } from '@/utils/assets/useDeleteAssetWithUserInteraction';
import { useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';

export const useAssetEditor = (assetType: AssetType) => {
  const params = useParams();
  const id = params.id || '';
  const asset = useAssetStore((state) => state.selectedAsset);
  const lastSavedAsset = useAssetStore((state) => state.lastSavedSelectedAsset);
  const setLastSavedSelectedAsset = useAssetStore((state) => state.setLastSavedSelectedAsset);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const isAssetChanged = useAssetChanged();
  const handleDeleteWithInteraction = useDeleteAssetWithUserInteraction(assetType);

  const searchParams = useSearchParams()[0];
  const copyId = searchParams.get('copy');

  const getInitialAsset = useCallback(() => {
    if (copyId) {
      // setLastSavedSelectedAsset(undefined);
      AssetsAPI.fetchAsset<Asset>({ assetType, id: copyId }).then((assetToCopy) => {
        assetToCopy.name += ' Copy';
        assetToCopy.defined_in = 'project';
        assetToCopy.id = convertNameToId(assetToCopy.name);
        setSelectedAsset(assetToCopy);
      });
    } else {
      //For id === 'new' This will get a default new asset
      const rawContentType = searchParams.get('content_type');
      const contentType = rawContentType ? rawContentType : undefined;
      AssetsAPI.fetchAsset<Asset>({ assetType, id, contentType: contentType }).then((editable) => {
        setLastSavedSelectedAsset(id !== 'new' ? editable : undefined); // for new assets, lastSavedAsset is undefined
        setSelectedAsset(editable);
      });
    }
  }, [copyId, assetType, id, searchParams, setLastSavedSelectedAsset, setSelectedAsset]);

  const handleDiscardChanges = () => {
    //set last selected asset to the same as selected asset

    if (!asset) {
      return;
    }

    if (lastSavedAsset === undefined) {
      getInitialAsset();
    } else {
      setSelectedAsset({ ...lastSavedAsset } as Asset);
    }
  };

  const handleRevert = (id?: string) => {
    if (!id) return;
    if (isAssetChanged) {
      handleDiscardChanges();
    } else {
      handleDeleteWithInteraction(id);
    }
  };

  const handleRename = async (newName: string) => {
    if (!asset) {
      return;
    }

    setSelectedAsset({ ...asset, name: newName, id: convertNameToId(newName) });
  };

  return { handleRevert, getInitialAsset, handleDiscardChanges, handleDeleteWithInteraction, handleRename };
};
