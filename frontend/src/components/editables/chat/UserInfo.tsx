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

import { useRef } from 'react';
import { Link } from 'react-router-dom';

import { useUserContextMenu } from '@/utils/common/useUserContextMenu';
import { UserAvatar } from './UserAvatar';
import { ContextMenu, ContextMenuRef } from '@/components/common/ContextMenu';

export function UserInfo({ username, email }: { username?: string; email?: string }) {
  const triggerRef = useRef<ContextMenuRef>(null);

  const userMenuItems = useUserContextMenu();

  const menuItems = userMenuItems;

  return (
    <ContextMenu options={menuItems} ref={triggerRef}>
      <Link to={''} className="flex-none items-center flex flex-col">
        <UserAvatar email={email} title={`${username}`} type="small" />
        <div
          className="text-[15px] w-32 text-center text-gray-300 max-w-[120px] truncate overflow-ellipsis overflow-hidden whitespace-nowrap"
          title={`${username}`}
        >
          {username}
        </div>
      </Link>
    </ContextMenu>
  );
}
