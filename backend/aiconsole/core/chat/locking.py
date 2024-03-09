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
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.load_chat_options import load_chat_options
from aiconsole.core.chat.root import Root
from aiconsole.core.chat.save_chat_history import save_chat_history
from aiconsole.core.chat.types import AICChat
from fastmutation.apply_mutation import apply_mutation
from fastmutation.mutation_context import MutationContext
from fastmutation.types import (
    AnyRef,
    AssetMutation,
    BaseObject,
    LockAcquiredMutation,
    LockReleasedMutation,
    ObjectRef,
)

_log = logging.getLogger(__name__)


async def wait_for_lock(ref: ObjectRef, lock_timeout=30) -> None:
    try:
        _log.debug(f"Waiting for lock {ref}")
        await asyncio.wait_for(_long_term_locks[ref].wait(), timeout=lock_timeout)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Lock acquisition timed out")


async def acquire_lock(ref: ObjectRef, request_id: str, skip_mutating_clients: bool = False):
    _log.debug(f"Acquiring lock {ref} {request_id}")
    if ref in _loaded_objects and _loaded_objects[ref].lock_id:
        await wait_for_lock(ref)

    if ref not in _loaded_objects:
        chat_history = await load_chat_history(ref.id)  # TODO: This should be a general object loader
        chat_history.lock_id = None
        _loaded_objects[ref] = chat_history

    _loaded_objects[ref].lock_id = request_id
    _long_term_locks[ref].clear()

    if not skip_mutating_clients:
        await connection_manager().send_to_ref(
            NotifyAboutAssetMutationServerMessage(
                request_id=request_id,
                mutation=LockAcquiredMutation(ref=ref, lock_id=request_id),
            ),
            ref,
        )
    return _loaded_objects[ref]


async def _read_chat_outside_of_lock(chat_id: str):
    _log.debug(f"Reading chat {chat_id}")
    if chat_id not in _loaded_objects:
        return await load_chat_history(chat_id)

    chat_options = await load_chat_options(chat_id)
    _loaded_objects[chat_id].chat_options = chat_options

    return _loaded_objects[chat_id]


async def release_lock(ref: ObjectRef, request_id: str) -> None:
    if ref in _loaded_objects and _loaded_objects[ref].lock_id == request_id:
        _loaded_objects[ref].lock_id = None
        await save_chat_history(cast(AICChat, _loaded_objects[ref]), scope="message_groups")
        del _loaded_objects[ref]
        _long_term_locks[ref].set()

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

        if isinstance(ref, ObjectRef):
            if ref.parent_collection is not None and ref.parent_collection.id == "assets":
                return await _read_chat_outside_of_lock(ref.id)

            if ref.id in _loaded_objects and _loaded_objects[ref.id].lock_id == self.request_id:
                return _loaded_objects[ref]

            await wait_for_lock(ref)
            return _loaded_objects[ref]
        else:
            raise Exception(f"Unknown ref type {ref}")

    async def exists(self, ref: AnyRef) -> bool:
        if isinstance(ref, ObjectRef):
            if ref.parent_collection is not None and ref.parent_collection.id == "assets":
                return ref.id in _loaded_objects

            if ref.id in _loaded_objects and _loaded_objects[ref.id].lock_id == self.request_id:
                return True

            await wait_for_lock(ref)

        return ref.id in _loaded_objects

    async def mutate(self, mutation: AssetMutation) -> None:
        # if ref in mutation is a chat ref, then we need to check if the lock is acquired

        if isinstance(mutation.ref, ObjectRef) and mutation.ref.parent_collection.id == "assets":
            chat_id = mutation.ref.id
            if chat_id not in _loaded_objects or _loaded_objects[chat_id].lock_id != self.request_id:
                raise Exception(
                    f"Lock not acquired for chat {chat_id} request_id={self.request_id}",
                )

        if mutation.ref.id not in _loaded_objects or _loaded_objects[mutation.ref.id].lock_id != self.request_id:
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

_loaded_objects: dict[ObjectRef, BaseObject] = {}
_long_term_locks: dict[ObjectRef, asyncio.Event] = defaultdict(asyncio.Event)
_waiting_mutations: dict[ObjectRef, deque[Callable[[], Coroutine]]] = defaultdict(deque)
_running_mutations: dict[ObjectRef, asyncio.Task | None] = defaultdict(lambda: None)
_mutation_complete_events: dict[ObjectRef, asyncio.Event] = defaultdict(asyncio.Event)


def _check_mutation_queue(ref: ObjectRef):
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

    async def acquire_long_time_lock(self, ref: ObjectRef, request_id: str, skip_mutating_clients: bool = False):
        _log.debug(f"Acquiring lock {ref} {request_id}")

        if ref in _loaded_objects and _loaded_objects[ref].lock_id:
            await wait_for_lock(ref)

        if ref not in _loaded_objects:
            base_object = await load_chat_history(ref.id)  # TODO: This should be a general object loader
            base_object.lock_id = None
            _loaded_objects[ref] = base_object

        _loaded_objects[ref].lock_id = request_id
        _long_term_locks[ref].clear()

        if not skip_mutating_clients:
            await connection_manager().send_to_ref(
                NotifyAboutAssetMutationServerMessage(
                    request_id=request_id,
                    mutation=LockAcquiredMutation(ref=ref, lock_id=request_id),
                ),
                ref,
            )
        return _loaded_objects[ref]

    async def release_long_time_lock(self, ref: ObjectRef, request_id: str):
        if _loaded_objects[ref].lock_id == request_id:
            del _long_term_locks[ref]
        else:
            raise Exception(f"Lock {ref} is not acquired by {request_id}")

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

    async def wait_for_all_mutations(self, ref: ObjectRef):
        while _waiting_mutations[ref] or _running_mutations[ref] is not None:
            await _mutation_complete_events[ref].wait()

    async def in_sequence(self, ref: ObjectRef, f: Callable[[], Coroutine]):
        _waiting_mutations[ref].append(f)
        _check_mutation_queue(ref)
