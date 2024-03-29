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

import { useWebSocketStore } from '../api/ws/useWebSocketStore';
import { useUtilsStore } from './common/useUtilsStore';
import { useRecentProjectsStore } from './projects/useRecentProjectsStore';
import { useSettingsStore } from './settings/useSettingsStore';
import { useAPIStore } from './useAPIStore';

export const initStore = async () => {
  await useAPIStore.getState().initAPIStore();
  useSettingsStore.getState().initSettings();
  await useUtilsStore.getState().checkNetworkStatus();
  useWebSocketStore.getState().initWebSocket();
  useRecentProjectsStore.getState().initRecentProjects();
};
