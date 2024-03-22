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

from aiconsole.api.websockets.base_server_message import BaseServerMessage
from fastmutation.types import AnyRef, CollectionRef, ObjectRef

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class AcquiredLock:
    ref: AnyRef
    request_id: str


class AICConnection:
    def __init__(self, websocket: WebSocket):
        self._websocket = websocket
        self._open_refs: set[AnyRef] = set()
        self._acquired_locks: list[AcquiredLock] = []

    def receive_json(self):
        return self._websocket.receive_json()

    def is_ref_open(self, ref: AnyRef):
        if ref in self._open_refs:
            return True

        if isinstance(ref, CollectionRef) and ref.parent:
            return self.is_ref_open(ref.parent)

        if isinstance(ref, ObjectRef) and ref.parent_collection:
            return self.is_ref_open(ref.parent_collection)

        return False

    def subscribe_to_ref(self, ref: AnyRef):
        self._open_refs.add(ref)

    def unsubscribe_ref(self, ref: AnyRef):
        self._open_refs.remove(ref)

    def lock_acquired(self, ref: AnyRef, request_id: str):
        if self.is_lock_acquired(ref):
            raise ValueError(f"{ref} is already locked")

        self._acquired_locks.append(AcquiredLock(ref, request_id))

        _log.info(f"Acquired lock {request_id} {ref}")

    def lock_released(self, ref: AnyRef, request_id: str):
        lock_data = AcquiredLock(ref=ref, request_id=request_id)

        if lock_data in self._acquired_locks:
            self._acquired_locks.remove(lock_data)
        else:
            _log.error(f"Lock {lock_data} not found in {self._acquired_locks}")

    def is_lock_acquired(self, ref: AnyRef):
        if any(lock.ref == ref for lock in self._acquired_locks):
            return True

        if isinstance(ref, CollectionRef) and ref.parent:
            return self.is_lock_acquired(ref.parent)

        if isinstance(ref, ObjectRef) and ref.parent_collection:
            return self.is_lock_acquired(ref.parent_collection)

        return False

    async def send(self, msg: BaseServerMessage):
        await self._websocket.send_json({"type": msg.get_type(), **msg.model_dump(exclude_none=True, mode="json")})


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

    async def send_to_ref(
        self,
        message: BaseServerMessage,
        ref: ObjectRef | CollectionRef,
        except_connection: AICConnection | None = None,
    ):
        for connection in self.active_connections:
            if connection.is_ref_open(ref) and except_connection != connection:
                await connection.send(message)

    async def send_to_all(self, message: BaseServerMessage):
        for connection in self.active_connections:
            await connection.send(message)


@lru_cache
def connection_manager():
    return ConnectionManager()
