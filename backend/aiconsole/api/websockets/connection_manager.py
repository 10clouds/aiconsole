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
"""
Connection manager for websockets. Keeps track of all active connections
"""
import logging
from dataclasses import dataclass
from functools import lru_cache

from fastapi import WebSocket

from aiconsole.api.websockets.server_messages import BaseServerMessage

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class AcquiredLock:
    chat_id: str
    request_id: str


class AICConnection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.open_chats_ids: set[str] = set()
        self.acquired_locks: list[AcquiredLock] = []

    async def send(self, msg: BaseServerMessage):
        await self.websocket.send_json({"type": msg.get_type(), **msg.model_dump(mode="json")})


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[AICConnection] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        connection = AICConnection(websocket)
        self.active_connections.append(connection)
        _log.info("Connected")
        return connection

    def disconnect(self, connection: AICConnection):
        self.active_connections.remove(connection)
        _log.info("Disconnected")

    async def send_to_chat(
        self, message: BaseServerMessage, chat_id: str, except_connection: AICConnection | None = None
    ):
        for connection in self.active_connections:
            if chat_id in connection.open_chats_ids and except_connection != connection:
                await connection.send(message)

    async def send_to_all(self, message: BaseServerMessage):
        for connection in self.active_connections:
            await connection.send(message)


@lru_cache
def connection_manager():
    return ConnectionManager()
