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

import { TopBar } from '@/components/common/TopBar';
import { HomeTopBarElements } from '@/components/projects/HomeTopBarElements';
import { useUtilsStore } from '@/store/common/useUtilsStore';
import { ProjectModalMode, useProjectFileManagerStore } from '@/store/projects/useProjectFileManagerStore';
import { useRecentProjectsStore } from '@/store/projects/useRecentProjectsStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useProjectStore } from '../../store/projects/useProjectStore';
import AlertDialog from '../common/AlertDialog';
import BackgroundGradient from '../common/BackgroundGradient';
import Offline from './Offline';
import { ProjectCard } from './ProjectCard';
import { RecentProjectsEmpty } from './RecentProjectsEmpty';

export function Home() {
  const openAiApiKey = useSettingsStore((state) => state.settings.openai_api_key);
  const isApiKeyValid = useSettingsStore((state) => state.isApiKeyValid);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);
  const recentProjects = useRecentProjectsStore((state) => state.recentProjects);
  const removeRecentProject = useRecentProjectsStore((state) => state.removeRecentProject);
  const projectModalMode = useProjectFileManagerStore((state) => state.projectModalMode);
  const isProjectDirectory = useProjectFileManagerStore((state) => state.isProjectDirectory);
  const tempPath = useProjectFileManagerStore((state) => state.tempPath);
  const resetProjectOpening = useProjectFileManagerStore((state) => state.resetProjectOpening);
  const openProjectConfirmation = useProjectFileManagerStore((state) => state.openProjectConfirmation);
  const initProject = useProjectFileManagerStore((state) => state.initProject);
  const projectName = useProjectFileManagerStore((state) => state.projectName);

  const isOnline = useUtilsStore((state) => state.isOnline);
  const checkNetworkStatus = useUtilsStore((state) => state.checkNetworkStatus);
  const [onlineStatus, setOnlineStatus] = useState(isOnline);

  useEffect(() => {
    window.addEventListener('online', checkNetworkStatus);
    window.addEventListener('offline', checkNetworkStatus);

    return () => {
      window.removeEventListener('online', checkNetworkStatus);
      window.removeEventListener('offline', checkNetworkStatus);
    };
  }, [checkNetworkStatus]);

  useEffect(() => {
    setOnlineStatus(isOnline);
  }, [isOnline]);

  const deleteProject = useCallback(
    (path: string) => async () => {
      await removeRecentProject(path);
      resetProjectOpening();
    },
    [removeRecentProject, resetProjectOpening],
  );

  const alertDialogConfig = {
    locate: {
      title: "Can't find the project",
      message: `The "${projectName}" project has been deleted or its location has been changed.`,
      confirmText: 'Locate project',
      cancelText: 'Close',
      onConfirm: () => initProject(ProjectModalMode.OPEN_EXISTING),
      onCancel: resetProjectOpening,
    },
    delete: {
      title: 'Delete file',
      message: 'Are you sure you want to delete the file?',
      confirmText: 'Yes, delete',
      cancelText: 'No, cancel',
      onConfirm: deleteProject(tempPath),
      onCancel: resetProjectOpening,
    },
    existingProject: {
      title: 'This folder already contains an AIConsole project',
      message: 'Do you want to open it instead?',
      confirmText: 'Yes, open',
      cancelText: 'No, Close',
      onConfirm: openProjectConfirmation,
      onCancel: resetProjectOpening,
    },
    newProject: {
      title: 'There is no project in this directory',
      message: 'Do you want to create one there instead?',
      confirmText: 'Yes, create',
      cancelText: 'No, close',
      onConfirm: openProjectConfirmation,
      onCancel: resetProjectOpening,
    },
  };

  const currentAlertDialogConfig = useMemo(() => {
    if (projectModalMode === ProjectModalMode.LOCATE) {
      return alertDialogConfig.locate;
    } else if (projectModalMode === ProjectModalMode.DELETE) {
      return alertDialogConfig.delete;
    } else if (isProjectDirectory === true && projectModalMode === ProjectModalMode.OPEN_NEW && Boolean(tempPath)) {
      return alertDialogConfig.existingProject;
    } else if (
      isProjectDirectory === false &&
      projectModalMode === ProjectModalMode.OPEN_EXISTING &&
      Boolean(tempPath)
    ) {
      return alertDialogConfig.newProject;
    }
    return null;
  }, [
    alertDialogConfig.delete,
    alertDialogConfig.existingProject,
    alertDialogConfig.locate,
    alertDialogConfig.newProject,
    isProjectDirectory,
    projectModalMode,
    tempPath,
  ]);

  useEffect(() => {
    if (
      (isProjectDirectory === false && projectModalMode === ProjectModalMode.OPEN_NEW) ||
      (isProjectDirectory === true && projectModalMode === ProjectModalMode.OPEN_EXISTING)
    ) {
      openProjectConfirmation();
    }
  }, [openProjectConfirmation, projectModalMode, isProjectDirectory]);

  if (!onlineStatus) {
    return (
      <div className="min-h-[100vh] relative overflow-x-hidden">
        <BackgroundGradient />
        <Offline />
      </div>
    );
  }

  return (
    <div className="min-h-[100vh] relative overflow-x-hidden">
      <BackgroundGradient />
      <div>
        {(openAiApiKey === undefined && isProjectLoading) || isApiKeyValid === undefined ? (
          <>{/* the request is in progress - don't render anything to avoid flickering */}</>
        ) : (
          <>
            {recentProjects.length > 0 && openAiApiKey && isApiKeyValid ? (
              <div className="h-screen max-h-screen overflow-hidden flex flex-col">
                <TopBar>
                  <HomeTopBarElements />
                </TopBar>
                <div className="px-5 pb-10 pt-[40px] flex-1 flex flex-col grow overflow-hidden">
                  <div className="px-[60px] text-white ">
                    <img src="favicon.png" className="shadows-lg w-[60px] h-[60px] mx-auto m-4" alt="Logo" />
                    <h1 className="mb-[50px] font-extrabold text-center">
                      Welcome to <span className=" text-primary">AIConsole!</span>
                    </h1>
                    <div className="px-4 pb-[30px] text-center opacity-75 text-gray-400">Recent projects:</div>
                  </div>
                  <div className="w-full flex flex-wrap justify-center gap-[20px] mx-auto overflow-auto pr-5">
                    {recentProjects.map(({ name, path, recent_chats, incorrect_path }) => (
                      <div
                        key={path}
                        className="w-full md:w-[calc(50%-10px)] xl:w-[calc(33.333%-13.33px)] 2xl:w-[calc(25%-15px)]"
                      >
                        <ProjectCard
                          name={name}
                          path={path}
                          recentChats={recent_chats}
                          incorrectPath={incorrect_path}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <RecentProjectsEmpty openAiApiKey={openAiApiKey} isApiKeyValid={isApiKeyValid} />
            )}
          </>
        )}
      </div>
      {currentAlertDialogConfig && (
        <AlertDialog
          title={currentAlertDialogConfig.title}
          isOpen={!!currentAlertDialogConfig}
          onClose={currentAlertDialogConfig.onCancel}
          onConfirm={currentAlertDialogConfig.onConfirm}
          confirmationButtonText={currentAlertDialogConfig.confirmText}
          cancelButtonText={currentAlertDialogConfig.cancelText}
        >
          {currentAlertDialogConfig.message}
        </AlertDialog>
      )}
    </div>
  );
}
