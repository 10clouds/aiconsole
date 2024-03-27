// TEMP ASSET ON WS MUTATION IMPLEMENTATION

import { ChatOpenedServerMessage, ServerMessage } from '@/api/ws/serverMessages';
import { useWebSocketStore } from '@/api/ws/useWebSocketStore';
import { Asset } from '@/store/assets/constructors';
import { v4 as uuidv4 } from 'uuid';
import { StateCreator } from 'zustand';
import { DataContext } from './DataContext';
import { AssetRef } from './locations';
import { AssetsState } from './useAssetStore';

export interface AssetSlice {
  // subscribedAssets: Asset[];
  subscribeById: (id: string) => Promise<void>;
  unsubscribeById: (id: string) => Promise<void>;
  getAsset: (id: string) => Asset | undefined;
  saveAsset: (asset: Asset) => void;
  dataContext: DataContext;
}

export const createAssetsSlice: StateCreator<AssetsState, [], [], AssetSlice> = (set, get) => ({
  // subscribedAssets: [],
  unsubscribeById: async (id: string) => {
    const response = await useWebSocketStore.getState().sendMessageAndWaitForResponse(
      {
        type: 'UnsubscribeClientMessage',
        ref: new AssetRef(id, null),
        request_id: uuidv4(),
      },
      (response: ServerMessage) => {
        return response.type === 'ResponseServerMessage';
      },
    );
  },
  getAsset: (id: string) => {
    return get().assets.find((a) => a.id === id);
  },
  saveAsset: (asset: Asset) => {
    set((state: AssetsState) => {
      const index = state.assets.findIndex((a) => a.id === asset.id);
      if (index === -1) {
        state.assets.push(asset);
      } else {
        state.assets[index] = asset;
      }
      return state;
    });
  },
  subscribeById: async (id: string) => {
    const response: ChatOpenedServerMessage = (await useWebSocketStore.getState().sendMessageAndWaitForResponse(
      {
        type: 'SubscribeToClientMessage',
        ref: new AssetRef(id, null),
        request_id: uuidv4(),
      },
      (response: ServerMessage) => {
        if (response.type === 'ChatOpenedServerMessage') {
          return response.chat.id === id;
        } else {
          return false;
        }
      },
    )) as ChatOpenedServerMessage;
  },
  dataContext: new DataContext(),
});
