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

import { useEffect } from 'react';
import {
  createHashRouter,
  createRoutesFromElements,
  Navigate,
  Outlet,
  Route,
  RouterProvider,
  useMatch,
} from 'react-router-dom';
import { v4 as uuid } from 'uuid';

import { TopBar } from '@/components/common/TopBar';
import { ProjectTopBarElements } from '@/components/projects/ProjectTopBarElements';
import { useToastsStore } from '@/store/common/useToastsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { useAPIStore } from '@/store/useAPIStore';
import { AssetEditor } from './editables/assets/AssetEditor';
import { ChatPage } from './editables/chat/ChatPage';
import SideBar from './editables/sidebar/SideBar';
import { Home } from './projects/Home';
import { GlobalSettingsModal } from './settings/modal/GlobalSettingsModal';

function Project() {
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);

  const isChat = useMatch('/chats/*');
  const isMaterial = useMatch('/materials/*');
  const isAgent = useMatch('/agents/*');

  if (!isProjectOpen && !isProjectLoading) {
    return <Navigate to="/" />;
  }

  const initialTab = isChat ? 'chats' : isMaterial ? 'materials' : isAgent ? 'agents' : 'chats';

  return (
    <div className="App flex flex-col h-screen fixed top-0 left-0 bottom-0 right-0 bg-gray-900 text-stone-400">
      <GlobalSettingsModal />
      <TopBar>
        <ProjectTopBarElements />
      </TopBar>
      <div className="flex flex-row h-full overflow-y-auto">
        <SideBar initialTab={initialTab} />
        <Outlet />
      </div>
    </div>
  );
}

function NoProject() {
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);

  if (isProjectOpen && !isProjectLoading) {
    return <Navigate to={`/chats/${uuid()}`} />;
  }

  return <Outlet />;
}

const HomeRoute = () => (
  <>
    <Home />
    <GlobalSettingsModal />
  </>
);

export function Router() {
  const port = useAPIStore((state) => state.port);

  const showToast = useToastsStore.getState().showToast;

  useEffect(() => {
    window.electron?.onBackendExit(() => {
      showToast({
        title: 'Application Error',
        message: 'Please restart the app.',
        variant: 'error',
      });
    });

    return () => {
      window.electron?.disposeBackendExitListener();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!port) {
    return null;
  }

  return (
    <RouterProvider
      router={createHashRouter(
        createRoutesFromElements(
          <>
            <Route path="/" element={<NoProject />}>
              <Route index element={<HomeRoute />} />
            </Route>
            <Route path="/" element={<Project />}>
              <Route path="chats/:id" element={<ChatPage />} />
              <Route path="chats/*" element={<Navigate to={`/chats/${uuid()}`} />} />
              <Route path="materials/:id" element={<AssetEditor assetType={'material'} />} />
              <Route path="materials/*" element={<></>} />
              <Route path="agents/:id" element={<AssetEditor assetType={'agent'} />} />
              <Route path="agents/*" element={<></>} />
              <Route path="*" element={<Navigate to="/" />} />
            </Route>
          </>,
        ),
      )}
    />
  );
}
