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
import { Settings } from '@/types/settings/Settings';
import { create } from 'zustand';
import { SettingsAPI } from '../../api/api/SettingsAPI';

export type SettingsStore = {
  openAiApiKey?: string;
  isApiKeyValid?: boolean;
  alwaysExecuteCode: boolean;
  username?: string;
  userEmail?: string;
  userAvatarUrl?: string;
  isSettingsModalVisible: boolean;
  setSettingsModalVisibility: (isVisible: boolean) => void;
  initSettings: () => Promise<void>;
  setAutoCodeExecution: (autoRun: boolean) => void;
  saveSettings: (settings: Settings, isGlobal: boolean, avatar?: FormData | null) => Promise<void>;
  validateApiKey: (key: string) => Promise<boolean>;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const useSettingsStore = create<SettingsStore>((set, get) => ({
  openAiApiKey: undefined,
  isApiKeyValid: false,
  alwaysExecuteCode: false,
  username: undefined,
  userEmail: undefined,
  userAvatarUrl: undefined,
  isSettingsModalVisible: false,
  setSettingsModalVisibility: (isVisible: boolean) => {
    set({ isSettingsModalVisible: isVisible });
  },
  setAutoCodeExecution: async (autoRun: boolean) => {
    await SettingsAPI.saveSettings({ code_autorun: autoRun, to_global: true });
    set({ alwaysExecuteCode: autoRun });
  },
  saveSettings: async (settings: Settings, isGlobal: boolean, avatar?: FormData | null) => {
    const { user_profile, openai_api_key, code_autorun } = settings;
    await SettingsAPI.saveSettings({
      ...settings,
      to_global: isGlobal,
    });
    if (openai_api_key) {
      set({
        openAiApiKey: openai_api_key,
        isApiKeyValid: true, // We assume that they key was validated before saving
      });
    }
    if (user_profile && user_profile.username) {
      set({ username: user_profile.username });
    }
    if (user_profile && user_profile.email) {
      set({ userEmail: user_profile.email });
    }
    if (typeof code_autorun === 'boolean') {
      set({ alwaysExecuteCode: code_autorun });
    }

    if (avatar) {
      await SettingsAPI.setUserAvatar(avatar);
      // Refetch updated avatar
      const { avatar_url } = await SettingsAPI.getUserAvatar(user_profile?.email);
      set({
        userAvatarUrl: avatar_url,
      });
    }
  },
  initSettings: async () => {
    const { code_autorun, openai_api_key, user_profile } = await SettingsAPI.getSettings();
    const { avatar_url } = await SettingsAPI.getUserAvatar(user_profile?.email);
    set({
      username: user_profile?.username,
      userEmail: user_profile?.email,
      alwaysExecuteCode: code_autorun,
      openAiApiKey: openai_api_key,
      isApiKeyValid: await get().validateApiKey(openai_api_key || ''),
      userAvatarUrl: avatar_url,
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
