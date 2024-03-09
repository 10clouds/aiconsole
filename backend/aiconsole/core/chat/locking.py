import asyncio
import logging
from collections import defaultdict, deque
from typing import Callable, Coroutine, cast

from fastapi import HTTPException

from aiconsole.api.websockets.connection_manager import (
    AICConnection,
    connection_manager,
)
from aiconsole.api.websockets.server_messages import (
    NotifyAboutAssetMutationServerMessage,
)
from aiconsole.core.chat.apply_mutation import apply_mutation
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.load_chat_options import load_chat_options
from aiconsole.core.chat.root import Root
from aiconsole.core.chat.save_chat_history import save_chat_history
from aiconsole.core.chat.types import AICChat
from fastmutation.mutation_context import MutationContext
from fastmutation.types import (
    AnyRef,
    AssetMutation,
    BaseObject,
    LockAcquiredMutation,
    LockReleasedMutation,
    ObjectRef,
)

loaded_base_objects: dict[str, BaseObject] = {}
lock_events: dict[str, asyncio.Event] = defaultdict(asyncio.Event)

lock_timeout = 30  # Time in seconds to wait for the lock

_log = logging.getLogger(__name__)


async def wait_for_lock(chat_id: str) -> None:
    try:
        _log.debug(f"Waiting for lock {chat_id}")
        await asyncio.wait_for(lock_events[chat_id].wait(), timeout=lock_timeout)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Lock acquisition timed out")


async def acquire_lock(ref: ObjectRef, request_id: str, skip_mutating_clients: bool = False):
    locked_id = ref.id

    _log.debug(f"Acquiring lock {locked_id} {request_id}")
    if locked_id in loaded_base_objects and loaded_base_objects[locked_id].lock_id:
        await wait_for_lock(locked_id)

    if locked_id not in loaded_base_objects:
        chat_history = await load_chat_history(locked_id)
        chat_history.lock_id = None
        loaded_base_objects[locked_id] = chat_history

    loaded_base_objects[locked_id].lock_id = request_id
    lock_events[locked_id].clear()

    if not skip_mutating_clients:
        await connection_manager().send_to_ref(
            NotifyAboutAssetMutationServerMessage(
                request_id=request_id,
                mutation=LockAcquiredMutation(ref=ref, lock_id=request_id),
            ),
            ref,
        )
    return loaded_base_objects[locked_id]


async def _read_chat_outside_of_lock(chat_id: str):
    _log.debug(f"Reading chat {chat_id}")
    if chat_id not in loaded_base_objects:
        return await load_chat_history(chat_id)

    chat_options = await load_chat_options(chat_id)
    loaded_base_objects[chat_id].chat_options = chat_options

    return loaded_base_objects[chat_id]


async def release_lock(ref: ObjectRef, request_id: str) -> None:
    locked_id = ref.id

    if locked_id in loaded_base_objects and loaded_base_objects[locked_id].lock_id == request_id:
        loaded_base_objects[locked_id].lock_id = None
        await save_chat_history(cast(AICChat, loaded_base_objects[locked_id]), scope="message_groups")
        del loaded_base_objects[locked_id]
        lock_events[locked_id].set()

        await connection_manager().send_to_ref(
            NotifyAboutAssetMutationServerMessage(
                request_id=request_id,
                mutation=LockReleasedMutation(lock_id=request_id, ref=ref),
            ),
            ref,
        )


class DefaultRootMutationContext(MutationContext):
    def __init__(self, root: Root, request_id: str, connection: AICConnection | None):
        self.root = root
        self.request_id = request_id
        self.connection = connection

    async def get(self, ref: AnyRef) -> BaseObject:
        if ref.parent is not None and ref.parent.id == "assets":
            return await _read_chat_outside_of_lock(ref.id)

        if ref.id in loaded_base_objects and loaded_base_objects[ref.id].lock_id == self.request_id:
            return loaded_base_objects[ref.id]

        await wait_for_lock(ref.id)
        return loaded_base_objects[ref.id]

    async def exists(self, ref: AnyRef) -> bool:
        if ref.parent is not None and ref.parent.id == "assets":
            return ref.id in loaded_base_objects

        if ref.id in loaded_base_objects and loaded_base_objects[ref.id].lock_id == self.request_id:
            return True

        await wait_for_lock(ref.id)

        return ref.id in loaded_base_objects

    async def mutate(self, mutation: AssetMutation) -> None:
        # if ref in mutation is a chat ref, then we need to check if the lock is acquired

        if isinstance(mutation.ref, ObjectRef) and mutation.ref.parent.id == "assets":
            chat_id = mutation.ref.id
            if chat_id not in loaded_base_objects or loaded_base_objects[chat_id].lock_id != self.request_id:
                raise Exception(
                    f"Lock not acquired for chat {chat_id} request_id={self.request_id}",
                )

        if (
            mutation.ref.id not in loaded_base_objects
            or loaded_base_objects[mutation.ref.id].lock_id != self.request_id
        ):
            raise Exception(
                f"Lock not acquired for chat {mutation.ref.id} request_id={self.request_id}",
            )

        apply_mutation(self.root, mutation)

        await connection_manager().send_to_ref(
            NotifyAboutAssetMutationServerMessage(
                request_id=self.request_id,
                mutation=mutation,
            ),
            mutation.ref,
            except_connection=self.connection,
        )


# This is responsible for sequencing the mutations and reads on a given ref
_waiting_mutations: dict[AnyRef, deque[Callable[[], Coroutine]]] = defaultdict(deque)
_running_mutations: dict[AnyRef, asyncio.Task | None] = defaultdict(lambda: None)
_mutation_complete_events: dict[AnyRef, asyncio.Event] = defaultdict(asyncio.Event)


def _check_mutation_queue(ref: AnyRef):
    if _running_mutations[ref] is not None or not _waiting_mutations[ref]:
        return

    h = _waiting_mutations[ref].popleft()
    task = asyncio.create_task(h())
    _running_mutations[ref] = task

    def clear_task(future):
        _running_mutations[ref] = None
        _mutation_complete_events[ref].set()
        _mutation_complete_events[ref].clear()
        _check_mutation_queue(ref)

    task.add_done_callback(clear_task)


class SequentialRootMutationContext(MutationContext):
    def __init__(self, mutator: DefaultRootMutationContext):
        self.mutator = mutator

    @property
    def root(self):
        return self.mutator.root

    async def get(self, ref: AnyRef):
        return self.mutator.get(ref)

    async def exists(self, ref: AnyRef):
        return self.mutator.exists(ref)

    async def mutate(self, mutation: AssetMutation) -> None:
        async def h():
            try:
                await self.mutator.mutate(mutation)
            except Exception as e:
                _log.exception(f"Error during mutation: {e}")
                raise

        _waiting_mutations[mutation.ref].append(h)
        _check_mutation_queue(mutation.ref)

        await self.wait_for_all_mutations(mutation.ref)

    async def wait_for_all_mutations(self, ref: AnyRef):
        while ref.parent is not None:
            ref = ref.parent

        while _waiting_mutations[ref] or _running_mutations[ref] is not None:
            await _mutation_complete_events[ref].wait()

    async def in_sequence(self, ref: AnyRef, f: Callable[[], Coroutine]):
        while ref.parent is not None:
            ref = ref.parent

        _waiting_mutations[ref].append(f)
        _check_mutation_queue(ref)
