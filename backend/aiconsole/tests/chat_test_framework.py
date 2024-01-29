import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Any
from uuid import uuid4

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient

from aiconsole.api.endpoints.projects.services import ProjectDirectory
from aiconsole.api.websockets.client_messages import (
    AcquireLockClientMessage,
    CloseChatClientMessage,
    InitChatMutationClientMessage,
    OpenChatClientMessage,
    ProcessChatClientMessage,
    ReleaseLockClientMessage,
)
from aiconsole.app import app
from aiconsole.core.chat.chat_mutations import (
    CreateMessageGroupMutation,
    CreateMessageMutation,
)
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.types import AICMessage
from aiconsole.core.settings.fs.settings_file_storage import SettingsFileStorage
from aiconsole.core.settings.settings import settings
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData


class ChatTestFramework:
    def __init__(self) -> None:
        os.environ["CORS_ORIGIN"] = "http://localhost:3000"

        self._chat_id = None
        self._request_id = None
        self._message_group_id = None

        self._project_directory = ProjectDirectory()
        self._background_tasks = BackgroundTasks()
        self._client = TestClient(app())

        self._websocket = None
        self._project_path = None

    @property
    def chat_id(self) -> str | None:
        return self._chat_id

    def repeat(self, times: int) -> pytest.MarkDecorator:
        return pytest.mark.repeat(times)

    @asynccontextmanager
    async def initialize_project_with_chat(self, project_path: str):
        self._chat_id = str(uuid4())
        self._request_id = str(uuid4())
        self._message_group_id = str(uuid4())
        self._project_path = project_path

        settings().configure(storage=SettingsFileStorage(project_path=Path(project_path)))
        settings().save(PartialSettingsData(code_autorun=True), to_global=True)

        await self._project_directory.switch_or_save_project(
            directory=project_path, background_tasks=self._background_tasks
        )

        with self._client.websocket_connect("/ws") as websocket:
            try:
                await OpenChatClientMessage(request_id=self._request_id, chat_id=self._chat_id).send(websocket)
                self._wait_for_websocket_response("ChatOpenedServerMessage", websocket)

                await AcquireLockClientMessage(
                    request_id=self._request_id,
                    chat_id=self._chat_id,
                ).send(websocket)
                self._wait_for_websocket_response("NotifyAboutChatMutationServerMessage", websocket)

                await InitChatMutationClientMessage(
                    request_id=self._request_id,
                    chat_id=self._chat_id,
                    mutation=CreateMessageGroupMutation(
                        message_group_id=self._message_group_id,
                        agent_id="user",
                        username="",
                        email="",
                        role="user",
                        task="",
                        materials_ids=[],
                        analysis="",
                    ),
                ).send(websocket)

                self._websocket = websocket

                yield
            finally:
                await CloseChatClientMessage(request_id=self._request_id, chat_id=self._chat_id).send(websocket)

    async def process_user_code_request(self, message: str) -> list[AICMessage]:
        if self._websocket is None:
            raise Exception("You have to initialize project with chat first")

        assert self._message_group_id is not None
        assert self._request_id is not None
        assert self._chat_id is not None
        await InitChatMutationClientMessage(
            request_id=self._request_id,
            chat_id=self._chat_id,
            mutation=CreateMessageMutation(
                message_group_id=self._message_group_id,
                message_id=str(uuid4()),
                timestamp=str(datetime.now()),
                content=message,
            ),
        ).send(self._websocket)
        await ReleaseLockClientMessage(
            request_id=self._request_id,
            chat_id=self._chat_id,
        ).send(self._websocket)

        await ProcessChatClientMessage(request_id=self._request_id, chat_id=self._chat_id).send(self._websocket)

        self._wait_for_mutation_type("LockReleasedMutation", self._websocket)

        return await self._get_chat_messages_for_agent("automator")

    def _wait_for_mutation_type(self, mutation_type: str, websocket: Any) -> None:
        while True:
            json = websocket.receive_json()
            if mutation := json.get("mutation"):
                if mutation["type"] == mutation_type:
                    return

    def _wait_for_websocket_response(self, response_type: str, websocket: Any) -> None:
        tries_count = 0
        while tries_count < 100:
            json = websocket.receive_json()
            if json["type"] == response_type:
                return
            tries_count += 1
            sleep(0.1)

        raise Exception(f"Response of type {response_type} not received")

    async def _get_chat_messages_for_agent(self, agent_id: str, _retries: int = 0) -> list[AICMessage] | list:
        assert self._chat_id is not None
        assert self._project_path is not None
        chat = await load_chat_history(id=self._chat_id, project_path=Path(self._project_path))
        automator_message_group_messages = None
        for message_group in chat.message_groups:
            if message_group.agent_id == agent_id:
                automator_message_group_messages = message_group.messages
                break

        if automator_message_group_messages is None and _retries < 30:
            sleep(5)
            return await self._get_chat_messages_for_agent(agent_id, _retries + 1)
        elif automator_message_group_messages is None and _retries >= 30:
            raise Exception(f"[CHAT_ID: {self._chat_id}] Automator message group not found in chat")
        return automator_message_group_messages or []  # Add type hint to indicate possible None value


chat_test_framework = ChatTestFramework()
