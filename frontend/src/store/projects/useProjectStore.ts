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

import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { ProjectsAPI } from '../../api/api/ProjectsAPI';
import { useChatStore } from '../editables/chat/useChatStore';
import { useSettingsStore } from '../settings/useSettingsStore';

export type ProjectSlice = {
  projectPath?: string; //undefined means loading, '' means no project, otherwise path
  projectName?: string;
  chooseProject: (path?: string) => Promise<void>;
  isProjectLoading: boolean;
  isProjectOpen: boolean;
  isProjectSwitchFetching: boolean;
  onProjectOpened: ({ path, name, initial }: { path: string; name: string; initial: boolean }) => Promise<void>;
  onProjectClosed: () => Promise<void>;
  onProjectLoading: () => void;
  resetProjectSwitchFetching: () => void;
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const useProjectStore = create<ProjectSlice>((set, _) => ({
  projectPath: undefined,
  projectName: undefined,
  isProjectLoading: true,
  isProjectOpen: false,
  isProjectSwitchFetching: false,
  onProjectOpened: async ({ path, name, initial }: { path: string; name: string; initial: boolean }) => {
    if (!path || !name) {
      throw new Error('Project path or name is not defined');
    }

    set(() => ({
      projectPath: path,
      projectName: name,
      isProjectOpen: true,
      isProjectLoading: false,
      isProjectSwitchFetching: false,
    }));

    await Promise.all([useChatStore.getState().initCommandHistory(), useEditablesStore.getState().initChatHistory()]);

    if (initial) {
      await Promise.all([
        useEditablesStore.getState().initAgents(),
        useEditablesStore.getState().initMaterials(),
        useSettingsStore.getState().initSettings(),
      ]);
    }
  },
  onProjectClosed: async () => {
    set(() => ({
      projectPath: '',
      projectName: '',
      isProjectOpen: false,
      isProjectLoading: false,
    }));
  },
  onProjectLoading: () => {
    set(() => ({
      projectPath: undefined,
      projectName: undefined,
      isProjectOpen: false,
      isProjectLoading: true,
      isProjectSwitchFetching: false,
    }));
  },
  resetProjectSwitchFetching: () => {
    set({
      isProjectSwitchFetching: false,
    });
  },
  chooseProject: async (path?: string) => {
    // If we are in electron environment, use electron dialog, otherwise rely on the backend to open the dialog
    if (!path && window?.electron?.openDirectoryPicker) {
      const path = await window?.electron?.openDirectoryPicker();
      if (path) {
        set({
          isProjectSwitchFetching: true,
        });
        await ProjectsAPI.chooseProject(path);
      }

      return;
    }
    if (path) {
      set({
        isProjectSwitchFetching: true,
      });
    }
    await ProjectsAPI.chooseProject(path);
  },
}));
