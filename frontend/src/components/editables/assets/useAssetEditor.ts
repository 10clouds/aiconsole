import { EditablesAPI } from '@/api/api/EditablesAPI';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { Asset, AssetType } from '@/types/editables/assetTypes';
import { convertNameToId } from '@/utils/editables/convertNameToId';
import { useAssetChanged } from '@/utils/editables/useAssetChanged';
import { useDeleteEditableObjectWithUserInteraction } from '@/utils/editables/useDeleteEditableObjectWithUserInteraction';
import { useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';

export const useAssetEditor = (editableObjectType: AssetType) => {
  const params = useParams();
  const id = params.id || '';
  const asset = useAssetStore((state) => state.selectedAsset);
  const lastSavedAsset = useAssetStore((state) => state.lastSavedSelectedAsset);
  const setLastSavedSelectedAsset = useAssetStore((state) => state.setLastSavedSelectedAsset);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const isAssetChanged = useAssetChanged();
  const handleDeleteWithInteraction = useDeleteEditableObjectWithUserInteraction(editableObjectType);

  const searchParams = useSearchParams()[0];
  const copyId = searchParams.get('copy');

  const getInitialAsset = useCallback(() => {
    if (copyId) {
      // setLastSavedSelectedAsset(undefined);

      EditablesAPI.fetchEditableObject<Asset>({ editableObjectType, id: copyId }).then((assetToCopy) => {
        assetToCopy.name += ' Copy';
        assetToCopy.defined_in = 'project';
        assetToCopy.id = convertNameToId(assetToCopy.name);
        setSelectedAsset(assetToCopy);
      });
    } else {
      //For id === 'new' This will get a default new asset
      const raw_type = searchParams.get('type');
      const type = raw_type ? raw_type : undefined;
      EditablesAPI.fetchEditableObject<Asset>({ editableObjectType, id, type }).then((editable) => {
        setLastSavedSelectedAsset(id !== 'new' ? editable : undefined); // for new assets, lastSavedAsset is undefined
        setSelectedAsset(editable);
      });
    }
  }, [copyId, editableObjectType, id, searchParams, setLastSavedSelectedAsset, setSelectedAsset]);

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
