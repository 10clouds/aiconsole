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

from pydantic import BaseModel
from starlette.testclient import WebSocketTestSession

from aiconsole.core.chat.chat_mutations import ChatMutation


class BaseClientMessage(BaseModel):
    def get_type(self):
        return self.__class__.__name__

    async def send(self, websocket: WebSocketTestSession):
        # client messages are sent via Test session which is synchronous
        websocket.send_json({"type": self.get_type(), **self.model_dump()})


# This is both an incoming and an outgoing message
class InitChatMutationClientMessage(BaseClientMessage):
    request_id: str
    chat_id: str
    mutation: ChatMutation


class AcquireLockClientMessage(BaseClientMessage):
    request_id: str
    chat_id: str


class ReleaseLockClientMessage(BaseClientMessage):
    request_id: str
    chat_id: str


class OpenChatClientMessage(BaseClientMessage):
    chat_id: str


class CloseChatClientMessage(BaseClientMessage):
    chat_id: str


class AcceptCodeClientMessage(BaseClientMessage):
    request_id: str
    chat_id: str
    tool_call_id: str


class ProcessChatClientMessage(BaseClientMessage):
    request_id: str
    chat_id: str
