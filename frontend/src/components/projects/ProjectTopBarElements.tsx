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

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';

import { useProjectStore } from '@/store/projects/useProjectStore';
import { useProjectContextMenu } from '@/utils/projects/useProjectContextMenu';
import { AddAssetDropdown } from '../editables/assets/AddAssetDropdown';
import { ContextMenu } from '../common/ContextMenu';
import { LeaveProjectDialog } from '../common/LeaveProjectDialog';

export function ProjectTopBarElements() {
  const projectName = useProjectStore((state) => state.projectName);

  const { menuItems, isDialogOpen, closeDialog, backToProjects } = useProjectContextMenu();

  return (
    <>
      <div className="flex text-sm gap-2 items-center pr-5">
        <div className="flex items-center justify-center gap-[30px]">
          <button className="w-[36px] h-[36px]" onClick={backToProjects}>
            <img src="favicon.png" className="shadows-lg h-full w-full" alt="Logo" />
          </button>
          <ContextMenu options={menuItems}>
            <Link
              to={`/chats/${uuidv4()}`}
              className="h-11 text-grey-300 font-bold  text-lg text-gray-400 hover:animate-pulse cursor-pointer flex gap-2 items-center mr-[32px] uppercase"
            >
              {projectName}
            </Link>
          </ContextMenu>
        </div>
        <AddAssetDropdown />
        <LeaveProjectDialog onCancel={closeDialog} isOpen={isDialogOpen} />
      </div>
    </>
  );
}
