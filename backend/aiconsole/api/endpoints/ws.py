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
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from aiconsole.api.websockets.connection_manager import (
    ConnectionManager,
    connection_manager,
)
from aiconsole.api.websockets.handle_incoming_message import handle_incoming_message
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.project import project

router = APIRouter()

_log = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    connection_manager: ConnectionManager = Depends(dependency=connection_manager),
):
    connection = await connection_manager.connect(websocket)
    await project.send_project_init(connection)

    try:
        while True:
            _log.debug("Waiting for message")
            json_data = await connection.receive_json()
            _log.debug(f"Received message: {json_data}")
            try:
                await handle_incoming_message(connection, json_data)
            except Exception as e:
                await connection.send(
                    ErrorServerMessage(error=f"Error handling message: {e} type={e.__class__.__name__}")
                )
                _log.exception(e)
                _log.error(f"Error handling message: {e}")
    except WebSocketDisconnect:
        connection_manager.disconnect(connection)
