// TEMP ASSET ON WS MUTATION IMPLEMENTATION

import { StateCreator } from 'zustand';
import { AssetsState } from './useAssetStore';
import { Asset } from '@/store/assets/constructors';

export interface AssetSlice {
  subscribedAssets: Asset[];
  subscribeToRef: (asset: any) => void;
  unsubscribeRef: (asset: any) => void;
  getSubscribedAsset: (id: string) => Asset | undefined;
  saveAsset: (asset: Asset) => void;
}

export const createAssetsSlice: StateCreator<AssetsState, [], [], AssetSlice> = (set, get) => ({
  subscribedAssets: [],
  subscribeToRef: (asset: Asset) => {},
  unsubscribeRef: (asset: Asset) => {},
  getSubscribedAsset: (id: string) => {
    return get().subscribedAssets.find((a) => a.id === id);
  },
  saveAsset: (asset: Asset) => {
    set((state: AssetsState) => {
      const index = state.subscribedAssets.findIndex((a) => a.id === asset.id);
      if (index === -1) {
        state.subscribedAssets.push(asset);
      } else {
        state.subscribedAssets[index] = asset;
      }
      return state;
    });
  },
});
