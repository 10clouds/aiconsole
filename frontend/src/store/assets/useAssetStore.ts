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

import { create } from 'zustand';

import { useProjectStore } from '@/store/projects/useProjectStore';
import { Agent, Asset, AssetType, Material } from '@/types/assets/assetTypes';
import { getAssetType } from '@/utils/assets/getAssetType';
import { AssetsAPI } from '../../api/api/AssetsAPI';
import { AICChat } from '@/types/assets/chatTypes';

export type AssetsState = {
  assets: Asset[];
  initAssets: () => Promise<void>;
  deleteAsset: (id: string) => Promise<void>;
  canOpenFinderForEditable(editable: Asset): boolean;
  openFinderForEditable: (editable: Asset) => void;
  selectedAsset?: Asset;
  lastSavedSelectedAsset?: Asset;
  newAssetFromParams: (location: URLSearchParams) => void;
  getAsset: (id: string) => Asset | undefined;
  setSelectedAsset: (asset?: Asset) => void;
  setLastSavedSelectedAsset: (asset?: Asset) => void;
  setIsEnabledFlag: (id: string, enabled: boolean) => Promise<void>;
};

export const useAssetStore = create<AssetsState>((set) => ({
  assets: [],
  initAssets: async () => {
    const assets: Asset[] = [];

    if (useProjectStore.getState().isProjectOpen) {
      assets.push(...(await AssetsAPI.fetchAssets()));
    }

    set({
      assets: assets,
    });
  },
  deleteAsset: async (id: string) => {
    await AssetsAPI.deleteAsset(id);

    set((state: AssetsState) => ({
      assets: (state.assets || []).filter((asset) => asset.id !== id),
    }));
  },
  canOpenFinderForEditable: (editable: Asset) => {
    const asset = editable as Asset;
    if (asset.defined_in === 'aiconsole') {
      return false;
    }

    if (window?.electron?.openFinder === undefined) {
      return false;
    }

    return true;
  },
  openFinderForEditable: async (editable: Asset) => {
    const type = getAssetType(editable);
    if (type === undefined) {
      return;
    }

    const path = await AssetsAPI.getPathForAsset(editable.id);
    window?.electron?.openFinder?.(path || '');
  },

  lastSavedSelectedAsset: undefined,
  selectedAsset: undefined,
  setLastSavedSelectedAsset: (asset?: Asset) => {
    set({
      lastSavedSelectedAsset: asset,
    });
  },
  newAssetFromParams: (location: URLSearchParams) => {
    //TODO: There should be only one place where this is defined, right now it's both in backend and frontend

    const params = location;

    const type: AssetType = params.get('type') as AssetType;

    if (type === 'agent') {
      const agent: Agent = {
        version: '0.0.1',
        type: 'agent',
        id: 'new_agent',
        name: 'New agent',
        usage: '',
        usage_examples: [],
        system: '',
        defined_in: 'project',
        enabled: true,
        gpt_mode: 'quality',
        execution_mode: 'aiconsole.core.chat.execution_modes.normal:execution_mode',
        execution_mode_params_values: {},
        enabled_by_default: true,
        override: false,
        last_modified: new Date().toISOString(),
      };

      return agent;
    } else if (type === 'material') {
      const material: Material = {
        version: '0.0.1',
        type: 'material',
        id: 'new_material',
        name: 'New material',
        usage: '',
        usage_examples: [],
        defined_in: 'project',
        enabled: true,
        content: '',
        content_type: 'static_text',
        enabled_by_default: true,
        override: false,
        last_modified: new Date().toISOString(),
      };

      return material;
    } else if (type === 'chat') {
      const chat: AICChat = {
        version: '0.0.1',
        type: 'chat',
        id: 'new_chat',
        name: 'New Chat',
        defined_in: 'project',
        enabled: true,
        enabled_by_default: true,
        override: false,
        last_modified: new Date().toISOString(),
        usage: '',
        title_edited: false,
        message_groups: [],
        is_analysis_in_progress: false,
        usage_examples: [],
        chat_options: {
          agent_id: '',
          materials_ids: [],
          ai_can_add_extra_materials: true,
          draft_command: '',
        },
      };

      return chat;
    } else {
      throw new Error(`Unknown asset type ${type}`);
    }
  },
  getAsset: (id: string): Asset | undefined => {
    if (id === 'user') {
      const agent: Agent = {
        version: '0.0.1',
        type: 'agent',
        id: 'user',
        name: 'You',
        usage: '',
        usage_examples: [],
        system: '',
        defined_in: 'aiconsole',
        enabled: true,
        gpt_mode: 'quality',
        execution_mode: 'aiconsole.core.chat.execution_modes.normal:execution_mode',
        execution_mode_params_values: {},
        enabled_by_default: true,
        override: false,
        last_modified: new Date().toISOString(),
      };

      return agent;
    }

    const asset = useAssetStore.getState().assets?.find((asset) => asset.id === id);

    if (asset) {
      return asset;
    }

    return undefined;
  },
  setSelectedAsset: (asset?: Asset) => {
    set({
      selectedAsset: asset,
    });
  },
  setIsEnabledFlag: async (id: string, enabled: boolean) => {
    useAssetStore.setState((state) => ({
      assets: (state.assets || []).map((asset) => {
        if (asset.id === id) {
          asset.enabled = enabled;
        }
        return asset;
      }),
    }));

    await AssetsAPI.setAssetEnabledFlag(id, enabled);
  },
}));
