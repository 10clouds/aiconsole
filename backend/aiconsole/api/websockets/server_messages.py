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

import typing

from aiconsole.core.chat.chat_mutations import ChatMutation
from aiconsole.core.chat.types import Chat

if typing.TYPE_CHECKING:
    from aiconsole.api.websockets.connection_manager import AICConnection

from pydantic import BaseModel

from aiconsole.core.assets.asset import AssetType


class BaseServerMessage(BaseModel):
    def get_type(self):
        return self.__class__.__name__

    def send_to_connection(self, connection: "AICConnection"):
        return connection.send(self)

    def send_to_chat(self, chat_id: str, source_connection_to_ommit: "AICConnection | None" = None):
        from aiconsole.api.websockets.connection_manager import send_message_to_chat

        return send_message_to_chat(chat_id, self, source_connection_to_ommit)

    def send_to_all(self, source_connection_to_ommit: "AICConnection | None" = None):
        from aiconsole.api.websockets.connection_manager import send_message_to_all

        return send_message_to_all(self, source_connection_to_ommit)

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
            "mutation": {**self.mutation.model_dump(**kwargs), "type": self.mutation.__class__.__name__},
        }


class ChatOpenedServerMessage(BaseServerMessage):
    chat: Chat
