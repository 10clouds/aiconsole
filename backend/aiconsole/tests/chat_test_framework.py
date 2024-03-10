import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Type, TypeVar
from uuid import uuid4

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from aiconsole.api.endpoints.projects.services import ProjectDirectory
from aiconsole.api.websockets.base_server_message import BaseServerMessage
from aiconsole.api.websockets.client_messages import (
    AcquireLockClientMessage,
    DoMutationClientMessage,
    ProcessChatClientMessage,
    ReleaseLockClientMessage,
    SubscribeToClientMessage,
    UnsubscribeClientMessage,
)
from aiconsole.api.websockets.server_messages import (
    ChatOpenedServerMessage,
    NotifyAboutAssetMutationServerMessage,
)
from aiconsole.app import app, lifespan
from aiconsole.core.chat.actor_id import ActorId
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.locations import ChatRef
from aiconsole.core.chat.root import Root
from aiconsole.core.chat.types import AICMessage, AICMessageGroup
from fastmutation.apply_mutation import apply_mutation
from fastmutation.data_context import DataContext
from fastmutation.mutations import AssetMutation, LockReleasedMutation
from fastmutation.types import AnyRef, BaseObject, CollectionRef, ObjectRef

TServerMessage = TypeVar("TServerMessage", bound=BaseServerMessage)

TMutation = TypeVar("TMutation", bound=AssetMutation)


class ClientSideDataContext(DataContext):

    def __init__(self, root: Root, websocket: WebSocketTestSession, request_id: str):
        self._root = root
        self._websocket = websocket
        self._request_id = request_id

    async def mutate(self, mutation: AssetMutation) -> None:
        # apply mutation to chat
        apply_mutation(self, mutation)

        await DoMutationClientMessage(
            request_id=self._request_id,
            mutation=mutation,
        ).send(self._websocket)

    def get(self, ref: ObjectRef | CollectionRef) -> BaseObject | list[BaseObject]:
        raise NotImplementedError("This method is not implemented")

    def exists(self, ref: AnyRef) -> bool:
        raise NotImplementedError("This method is not implemented")

    async def acquire_write_lock(self, ref: "AnyRef", lock_id: str) -> None:
        # Implement logic to acquire a write lock
        pass

    async def release_write_lock(self, ref: "AnyRef", lock_id: str) -> None:
        # Implement logic to release a write lock
        pass

    @property
    def type_to_cls_mapping(self) -> dict[str, Type["BaseObject"]]:
        # Return the type to class mapping
        return {}


class ChatTestFramework:
    def __init__(self) -> None:
        os.environ["CORS_ORIGIN"] = "http://localhost:3000"

        self._request_id: str | None = None
        self._message_group_id: str | None = None

        self._project_directory = ProjectDirectory()
        self._background_tasks = BackgroundTasks()
        self._app = app()
        self._client = TestClient(self._app)
        self._lifespan_context = None
        self._lifespan = lifespan

        self._websocket: WebSocketTestSession | None = None
        self._project_path: Path | None = None
        self._context: ClientSideDataContext | None = None

    async def setup(self):
        self._lifespan_context = await self._lifespan(self._app).__aenter__()

    def repeat(self, times: int) -> pytest.MarkDecorator:
        return pytest.mark.repeat(times)

    @asynccontextmanager
    async def initialize_project_with_chat(self, project_path: str):
        self._request_id = str(uuid4())
        self._message_group_id = str(uuid4())
        self._project_path = Path(project_path).absolute()

        await self.setup()
        self._client.post("/api/projects/switch", json={"directory": project_path})
        self._client.patch("/api/settings", json={"to_global": True, "code_autorun": True})

        with self._client.websocket_connect("/ws") as websocket:
            try:
                chat = self._wait_for_websocket_response(websocket, ChatOpenedServerMessage).chat

                root = Root(
                    id="root",
                    assets=[
                        chat,
                    ],
                )

                self._context = ClientSideDataContext(
                    root=root,
                    websocket=websocket,
                    request_id=self._request_id,
                )

                self.chat_ref = ChatRef(id=str(uuid4()), context=self._context)
                await SubscribeToClientMessage(
                    request_id=self._request_id,
                    ref=self.chat_ref,
                ).send(websocket)

                await AcquireLockClientMessage(
                    request_id=self._request_id,
                    ref=self.chat_ref,
                ).send(websocket)

                self._wait_for_websocket_response(websocket, NotifyAboutAssetMutationServerMessage)

                await self.chat_ref.message_groups.create(
                    AICMessageGroup(
                        id=self._message_group_id,
                        actor_id=ActorId(type="user", id="user"),
                        role="user",
                        task="",
                        materials_ids=[],
                        analysis="",
                        messages=[],
                    ),
                )

                self._websocket = websocket

                yield
            finally:
                await UnsubscribeClientMessage(request_id=self._request_id, ref=self.chat_ref).send(websocket)

    async def process_user_code_request(self, message: str, agent_id: str) -> list[AICMessage]:
        if self._websocket is None:
            raise Exception("You have to initialize project with chat first")

        assert self._message_group_id is not None
        assert self._request_id is not None
        assert self.chat_ref is not None

        await self.chat_ref.message_groups[self._message_group_id].messages.create(
            AICMessage(
                id=str(uuid4()),
                timestamp=str(datetime.now()),
                content=message,
            ),
        )

        await ReleaseLockClientMessage(request_id=self._request_id, ref=self.chat_ref).send(self._websocket)

        await ProcessChatClientMessage(request_id=self._request_id, chat_ref=self.chat_ref).send(self._websocket)

        self._wait_for_mutation_type(self._websocket, LockReleasedMutation)

        return await self._get_chat_messages_for_agent(agent_id)

    def _wait_for_mutation_type(self, websocket: WebSocketTestSession, message_class: Type[TMutation]) -> None:
        while True:
            json = websocket.receive_json()
            if mutation := json.get("mutation"):
                if mutation["type"] == message_class.__name__:
                    return

    def _wait_for_websocket_response(
        self, websocket: WebSocketTestSession, message_class: Type[TServerMessage]
    ) -> TServerMessage:
        tries_count = 0
        while tries_count < 100:
            json = websocket.receive_json()
            if json["type"] == "ResponseServerMessage" and json["payload"].get("error", None):
                raise Exception(f"Error received: {json['payload']['error']}")
            if json["type"] == message_class.__name__:
                return message_class(**json)
            tries_count += 1
            sleep(0.1)

        raise Exception(f"Response of type {message_class.__name__} not received")

    async def _get_chat_messages_for_agent(self, agent_id: str, _retries: int = 0) -> list[AICMessage] | list:
        # TODO: this should be extracted to use self._chat_mutator.chat, not read from the database

        assert self.chat_ref is not None
        assert self._project_path is not None

        chat = await load_chat_history(id=self.chat_ref.id, project_path=self._project_path)
        automator_message_group_messages = None
        for message_group in chat.message_groups:
            if message_group.actor_id.id == agent_id:
                automator_message_group_messages = message_group.messages
                break

        if automator_message_group_messages is None and _retries < 30:
            await asyncio.sleep(5)
            return await self._get_chat_messages_for_agent(agent_id, _retries + 1)
        elif automator_message_group_messages is None and _retries >= 30:
            raise Exception(f"[CHAT_ID: {self.chat_ref.id}] Automator message group not found in chat")
        return automator_message_group_messages or []  # Add type hint to indicate possible None value


chat_test_framework = ChatTestFramework()
