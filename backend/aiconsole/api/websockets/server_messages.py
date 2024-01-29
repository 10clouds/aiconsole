# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os

from pydantic import BaseModel

from aiconsole.core.assets.models import AssetType
from aiconsole.core.chat.chat_mutations import ChatMutation
from aiconsole.core.chat.types import Chat


class BaseServerMessage(BaseModel):
    def get_type(self):
        return self.__class__.__name__

    def model_dump(self, **kwargs):
        # Don't include None values, call to super to avoid recursion
        return {k: v for k, v in super().model_dump(**kwargs).items() if v is not None}


class NotificationServerMessage(BaseServerMessage):
    title: str
    message: str


class DebugJSONServerMessage(BaseServerMessage):
    message: str
    object: dict


class ErrorServerMessage(BaseServerMessage):
    error: str


class InitialProjectStatusServerMessage(BaseServerMessage):
    project_name: str | None = None
    project_path: str | None = None


class ProjectOpenedServerMessage(BaseServerMessage):
    name: str
    path: str


class ProjectClosedServerMessage(BaseServerMessage):
    pass


class ProjectLoadingServerMessage(BaseServerMessage):
    pass


class AssetsUpdatedServerMessage(BaseServerMessage):
    initial: bool
    asset_type: AssetType
    count: int


class SettingsServerMessage(BaseServerMessage):
    initial: bool


class NotifyAboutChatMutationServerMessage(BaseServerMessage):
    request_id: str
    chat_id: str
    mutation: ChatMutation

    def model_dump(self, **kwargs):
        # include type of mutation in the dump of "mutation"
        return {
            **super().model_dump(**kwargs),
            "mutation": {
                **self.mutation.model_dump(**kwargs),
                "type": self.mutation.__class__.__name__,
            },
        }


class ResponseServerMessage(BaseServerMessage):
    request_id: str
    payload: dict
    is_error: bool

    def __init__(self, request_id: str, payload: dict, is_error: bool = False) -> None:
        from aiconsole.core.project.paths import get_project_directory

        project_path = get_project_directory()
        payload = {**payload, "project_path": str(project_path), "project_name": os.path.basename(project_path)}

        super().__init__(**{"request_id": request_id, "payload": payload, "is_error": is_error})


class ChatOpenedServerMessage(BaseServerMessage):
    chat: Chat
