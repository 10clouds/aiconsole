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

import { MaterialDefinitionSource, AssetType, RenderedMaterial, Asset } from '@/types/assets/assetTypes';
import ky from 'ky';
import { API_HOOKS, getBaseURL } from '../../store/useAPIStore';
import { useWebSocketStore } from '../ws/useWebSocketStore';
import { ChatOpenedServerMessage, ServerMessage } from '../ws/serverMessages';
import { v4 as uuidv4 } from 'uuid';

const previewMaterial: (asset: Asset) => Promise<RenderedMaterial> = async (asset: Asset) =>
  ky
    .post(`${getBaseURL()}/api/assets/preview`, {
      json: { ...asset },
      timeout: 60000,
      hooks: API_HOOKS,
    })
    .json();

async function fetchAssets<T extends Asset>(): Promise<T[]> {
  return ky.get(`${getBaseURL()}/api/assets/`, { hooks: API_HOOKS }).json();
}

async function setAssetEnabledFlag(id: string, enabled: boolean) {
  return ky
    .post(`${getBaseURL()}/api/assets/${id}/status-change`, {
      json: { enabled, to_global: false },
      hooks: API_HOOKS,
    })
    .json();
}

async function fetchAsset<T extends Asset>({
  assetType,
  id,
  location,
  contentType,
}: {
  assetType: AssetType;
  id: string;
  location?: MaterialDefinitionSource;
  contentType?: string;
}): Promise<T> {
  if (assetType === 'chat') {
    const response: ChatOpenedServerMessage = (await useWebSocketStore.getState().sendMessageAndWaitForResponse(
      {
        type: 'SubscribeToClientMessage',
        ref: { id, context: null, parent_collection: { id: 'assets', parent: null, context: null } },
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

    return response.chat as unknown as T;
  }

  return ky
    .get(`${getBaseURL()}/api/assets/${id}`, {
      searchParams: { location: location || '', type: assetType || '', content_type: contentType || '' },
      hooks: API_HOOKS,
    })
    .json() as Promise<T>;
}

async function closeChat(id: string): Promise<ServerMessage> {
  const response = await useWebSocketStore.getState().sendMessageAndWaitForResponse(
    {
      type: 'UnsubscribeClientMessage',
      ref: { id, context: null, parent_collection: { id: 'assets', parent: null, context: null } },
      request_id: uuidv4(),
    },
    (response: ServerMessage) => {
      return response.type === 'ResponseServerMessage';
    },
  );

  return response;
}

async function doesEdibleExist(id: string, location?: MaterialDefinitionSource) {
  try {
    // Attempt to fetch the object
    const response = await ky
      .get(`${getBaseURL()}/api/assets/${id}/exists`, {
        searchParams: { location: location || '' },
      })
      .json<{ exists: boolean }>();

    // Check if the response is okay (status in the range 200-299)
    if (response.exists) {
      // Optionally, you can add additional checks here
      // if there are specific conditions to determine existence
      return true;
    } else {
      return false;
    }
  } catch (error) {
    // Handle any kind of error by returning false
    return false;
  }
}

async function saveNewAsset(asset_id: string, asset: Asset) {
  return await ky.post(`${getBaseURL()}/api/assets/${asset_id}`, {
    json: { ...asset },
    timeout: 60000,
    hooks: API_HOOKS,
  });
}

async function updateAsset(asset: Asset, originalId?: string) {
  if (!originalId) {
    originalId = asset.id;
  }

  // if (assetType === 'chat') {
  //   throw new Error('Chat cannot be updated');
  // }

  return ky.patch(`${getBaseURL()}/api/assets/${originalId}`, {
    json: { ...asset },
    timeout: 60000,
    hooks: API_HOOKS,
  });
}

async function deleteAsset(id: string) {
  return ky.delete(`${getBaseURL()}/api/assets/${id}`, {
    hooks: API_HOOKS,
  });
}

async function getPathForAsset(id: string) {
  return (
    (await ky
      .get(`${getBaseURL()}/api/assets/${id}/path`, {
        hooks: API_HOOKS,
      })
      .json()) as { path: string }
  ).path;
}

async function setAssetAvatar(assetId: string, avatar: FormData) {
  return ky.post(`${getBaseURL()}/api/assets/${assetId}/avatar`, { body: avatar, hooks: API_HOOKS });
}

export const AssetsAPI = {
  deleteAsset,
  fetchAssets,
  fetchAsset,
  setAssetEnabledFlag,
  doesEdibleExist,
  previewMaterial,
  saveNewAsset,
  updateAsset,
  getPathForAsset,
  closeChat,
  setAssetAvatar,
};
