import logging
import asyncio
from collections import defaultdict

from fastapi import HTTPException

from aiconsole.api.websockets.connection_manager import (
    AICConnection,
    connection_manager,
)
from aiconsole.api.websockets.server_messages import (
    NotifyAboutChatMutationServerMessage,
)
from aiconsole.core.chat.apply_mutation import apply_mutation
from aiconsole.core.chat.chat_mutations import (
    ChatMutation,
    LockAcquiredMutation,
    LockReleasedMutation,
)
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.save_chat_history import save_chat_history
from aiconsole.core.chat.types import Chat

chats: dict[str, Chat] = {}
lock_events: dict[str, asyncio.Event] = defaultdict(asyncio.Event)

lock_timeout = 30  # Time in seconds to wait for the lock

_log = logging.getLogger(__name__)


async def wait_for_lock(chat_id: str) -> None:
    try:
        _log.debug(f"Waiting for lock {chat_id}")
        await asyncio.wait_for(lock_events[chat_id].wait(), timeout=lock_timeout)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Lock acquisition timed out")


async def acquire_lock(chat_id: str, request_id: str, skip_mutating_clients: bool = False):
    _log.debug(f"Acquiring lock {chat_id} {request_id}")
    if chat_id in chats and chats[chat_id].lock_id:
        await wait_for_lock(chat_id)

    if chat_id not in chats:
        chat_history = await load_chat_history(chat_id)
        chat_history.lock_id = None
        chats[chat_id] = chat_history

    chats[chat_id].lock_id = request_id
    lock_events[chat_id].clear()

    if not skip_mutating_clients:
        await connection_manager().send_to_chat(
            NotifyAboutChatMutationServerMessage(
                request_id=request_id, chat_id=chat_id, mutation=LockAcquiredMutation(lock_id=request_id)
            ),
            chat_id,
        )
    return chats[chat_id]


async def release_lock(chat_id: str, request_id: str) -> None:
    if chat_id in chats and chats[chat_id].lock_id == request_id:
        chats[chat_id].lock_id = None
        save_chat_history(chats[chat_id])
        del chats[chat_id]
        lock_events[chat_id].set()

        await connection_manager().send_to_chat(
            NotifyAboutChatMutationServerMessage(
                request_id=request_id, chat_id=chat_id, mutation=LockReleasedMutation(lock_id=request_id)
            ),
            chat_id,
        )


class DefaultChatMutator(ChatMutator):
    def __init__(self, chat_id: str, request_id: str, connection: AICConnection | None):
        self.chat_id = chat_id
        self.request_id = request_id
        self.connection = connection

    @property
    def chat(self) -> Chat:
        return chats[self.chat_id]

    async def mutate(self, mutation: ChatMutation) -> None:
        if self.chat_id not in chats or chats[self.chat_id].lock_id != self.request_id:
            raise Exception(
                f"Lock not acquired for chat {self.chat_id} request_id={self.request_id} lock_id={self.chat.lock_id}",
            )

        apply_mutation(self.chat, mutation)

        await connection_manager().send_to_chat(
            NotifyAboutChatMutationServerMessage(
                request_id=self.request_id,
                chat_id=self.chat_id,
                mutation=mutation,
            ),
            self.chat_id,
            except_connection=self.connection,
        )
