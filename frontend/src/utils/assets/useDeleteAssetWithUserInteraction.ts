import { useAssetStore } from '@/store/assets/useAssetStore';
import { isAsset } from './isAsset';
import { AssetsAPI } from '@/api/api/AssetsAPI';
import { Asset } from '@/store/assets/constructors';

export function useDeleteAssetWithUserInteraction(assetType: Asset['type']) {
  const deleteAsset = useAssetStore((state) => state.deleteAsset);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const setLastSavedSelectedAsset = useAssetStore((state) => state.setLastSavedSelectedAsset);
  const selectedAsset = useAssetStore((state) => state.selectedAsset);

  async function handleDelete(id: string) {
    await deleteAsset(id);

    if (selectedAsset?.id === id) {
      if (isAsset(assetType) && (selectedAsset as Asset).override) {
        //Force reload of the current asset
        const newAsset = await AssetsAPI.fetchAsset<Asset>({ assetType, id });
        setSelectedAsset(newAsset);
        setLastSavedSelectedAsset(newAsset);
      } else {
        //const navigate = useNavigate();
        //This causes the asset list to be fully reloaded, and is probably not really needed:
        //navigate(`/assets`);
      }
    }
  }

  return handleDelete;
}
