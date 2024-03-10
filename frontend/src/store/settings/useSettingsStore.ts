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

import { ProjectsAPI } from '@/api/api/ProjectsAPI';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { create } from 'zustand';
import { SettingsAPI } from '../../api/api/SettingsAPI';
import { PartialSettingsData, SettingsData } from '@/types/settings/settingsTypes';
import { produce } from 'immer';

export type SettingsStore = {
  settings: SettingsData;
  isApiKeyValid?: boolean | undefined;
  isSettingsModalVisible: boolean;
  setSettingsModalVisibility: (isVisible: boolean) => void;
  initSettings: () => Promise<void>;
  setAutoCodeExecution: (autoRun: boolean) => void;
  saveSettings: (settings: PartialSettingsData, isGlobal: boolean, avatar?: FormData | null) => Promise<void>;
  validateApiKey: (key: string) => Promise<boolean>;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const useSettingsStore = create<SettingsStore>((set, get) => ({
  settings: {
    code_autorun: false,
    openai_api_key: '',
    user_profile: {
      id: '',
      display_name: '',
      profile_picture: '',
    },
    assets: {},
    gpt_modes: {},
    extra: {},
  },
  isApiKeyValid: undefined,
  isSettingsModalVisible: false,
  setSettingsModalVisibility: (isVisible: boolean) => {
    set({ isSettingsModalVisible: isVisible });
  },
  setAutoCodeExecution: async (autoRun: boolean) => {
    await SettingsAPI.saveSettings({ code_autorun: autoRun, to_global: true });
    set(
      produce((state: SettingsStore) => {
        state.settings.code_autorun = autoRun;
      }),
    );
  },
  saveSettings: async (settings: PartialSettingsData, isGlobal: boolean, avatar?: FormData | null) => {
    const { user_profile, openai_api_key, code_autorun } = settings;
    await SettingsAPI.saveSettings({
      ...settings,
      to_global: isGlobal,
    });
    if (openai_api_key) {
      set(
        produce((state: SettingsStore) => {
          state.settings.openai_api_key = openai_api_key;
          state.isApiKeyValid = true; // We assume that they key was validated before saving
        }),
      );
    }
    if (user_profile && user_profile.display_name) {
      set(
        produce((state: SettingsStore) => {
          state.settings.user_profile.display_name = user_profile.display_name || '';
        }),
      );
    }

    if (user_profile && user_profile.profile_picture) {
      set(
        produce((state: SettingsStore) => {
          state.settings.user_profile.profile_picture = user_profile.profile_picture || '';
        }),
      );
    }

    if (typeof code_autorun === 'boolean') {
      set(
        produce((state: SettingsStore) => {
          state.settings.code_autorun = code_autorun;
        }),
      );
    }

    if (avatar) {
      await SettingsAPI.setUserAvatar(avatar);
    }
  },
  initSettings: async () => {
    const settings = await SettingsAPI.getSettings();
    set({
      settings: settings,
      isApiKeyValid: await get().validateApiKey(settings.openai_api_key || ''),
    });
  },
  validateApiKey: async (key: string) => {
    if (!key) {
      return false;
    }
    const { key: returnedKey } = (await SettingsAPI.checkKey(key).json()) as {
      key?: string;
    };
    const key_ok = returnedKey !== undefined && returnedKey !== null && returnedKey !== '';

    if (!key_ok && useProjectStore.getState().isProjectOpen) {
      ProjectsAPI.closeProject();
    }

    return key_ok;
  },
}));
