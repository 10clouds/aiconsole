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
  useParams,
  useSearchParams,
} from 'react-router-dom';
import { v4 as uuid } from 'uuid';

import { TopBar } from '@/components/common/TopBar';
import { ProjectTopBarElements } from '@/components/projects/ProjectTopBarElements';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { useToastsStore } from '@/store/common/useToastsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { useAPIStore } from '@/store/useAPIStore';
import { AssetEditor } from './assets/AssetEditor';
import { ChatPage } from './assets/chat/ChatPage';
import SideBar from './sidebar/SideBar';
import { GenUIComponent } from './genui/GenUIComponent';
import { Home } from './projects/Home';
import { GlobalSettingsModal } from './settings/modal/GlobalSettingsModal';
import { updateDocumentTitle } from '@/utils/projects/changeDocumentTitle';

function Project() {
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);

  if (!isProjectOpen && !isProjectLoading) {
    return <Navigate to="/" />;
  }

  return (
    <div className="App flex flex-col h-screen fixed top-0 left-0 bottom-0 right-0 bg-gray-900 text-stone-400">
      <GlobalSettingsModal />
      <TopBar>
        <ProjectTopBarElements />
      </TopBar>
      <div className="flex flex-row h-full overflow-y-auto">
        <SideBar />
        <Outlet />
      </div>
    </div>
  );
}

function NoProject() {
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);

  updateDocumentTitle('Welcome to AIConsole');

  if (isProjectOpen && !isProjectLoading) {
    return <Navigate to={`/assets/new?type=chat`} />;
  }

  return <Outlet />;
}

const HomeRoute = () => (
  <>
    <Home />
    <GlobalSettingsModal />
  </>
);

const AssetPage = () => {
  const params = useParams();
  const [searchParams] = useSearchParams();
  const type = searchParams.get('type') || '';
  const id = params.id || '';

  const asset = useAssetStore((state) => (id === 'new' ? state.newAssetFromParams(searchParams) : state.getAsset(id)));

  if (asset) {
    const { name, type } = asset;
    const title = `${type}: ${name}`;
    updateDocumentTitle(title);
  }

  if (id === 'new') {
    if (type === 'chat') {
      return <ChatPage />;
    }

    if (type === 'agent') {
      return <AssetEditor assetType={'agent'} />;
    }

    if (type === 'material') {
      return <AssetEditor assetType={'material'} />;
    }
  } else {
    if (asset?.type === 'chat') {
      return <ChatPage />;
    }

    if (asset?.type === 'agent') {
      return <AssetEditor assetType={'agent'} />;
    }

    if (asset?.type === 'material') {
      return <AssetEditor assetType={'material'} />;
    }
  }

  return <></>;
};

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
              <Route path="assets/:id" element={<AssetPage />} />
              <Route path="assets/*" element={<Navigate to={`/asset/${uuid()}`} />} />
              <Route path="genui" element={<GenUIComponent />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Route>
          </>,
        ),
      )}
    />
  );
}
