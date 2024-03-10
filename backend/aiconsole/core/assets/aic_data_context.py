import asyncio
import logging
from collections import defaultdict, deque
from typing import Any, Callable, Coroutine, List, cast, overload

from aiconsole.api.websockets.connection_manager import (
    AICConnection,
    connection_manager,
)
from aiconsole.api.websockets.server_messages import (
    NotifyAboutAssetMutationServerMessage,
)
from aiconsole.core.chat.root import Root
from aiconsole.core.chat.types import AICChat, AICMessage, AICMessageGroup, AICToolCall
from aiconsole.core.project.project import get_project_assets
from fastmutation.apply_mutation import apply_mutation
from fastmutation.data_context import DataContext
from fastmutation.mutations import (
    AssetMutation,
    LockAcquiredMutation,
    LockReleasedMutation,
)
from fastmutation.types import AnyRef, BaseObject, CollectionRef, ObjectRef

_log = logging.getLogger(__name__)


def create_set_event() -> asyncio.Event:
    e = asyncio.Event()
    e.set()
    return e


_no_lock_taken: dict[ObjectRef, asyncio.Event] = defaultdict(create_set_event)
_waiting_mutations: dict[ObjectRef, deque[Callable[[], Coroutine]]] = defaultdict(deque)
_running_mutations: dict[ObjectRef, asyncio.Task | None] = defaultdict(lambda: None)
_mutation_complete_events: dict[ObjectRef, asyncio.Event] = defaultdict(asyncio.Event)


def _find_object(root: BaseObject, obj: ObjectRef) -> BaseObject | None:
    base_collection = _find_collection(root, obj.parent_collection)

    if not base_collection:
        raise ValueError(f"Collection {obj.parent_collection} not found")

    if obj.id not in base_collection:
        raise ValueError(f"Object {obj.id} not found")

    return next((item for item in base_collection if item.id == obj.id), None)


def _find_collection(root: BaseObject, collection: CollectionRef):
    base_object: BaseObject | None = root

    if collection.parent:
        base_object = _find_object(root, collection.parent)

    return cast(list[Any], getattr(base_object, collection.id, None))


async def _wait_for_lock(ref: ObjectRef, lock_timeout=30) -> None:
    try:
        _log.debug(f"Waiting for lock {ref}")
        await asyncio.wait_for(_no_lock_taken[ref].wait(), timeout=lock_timeout)
    except asyncio.TimeoutError:
        raise Exception(f"Lock acquisition timed out for {ref}")


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


class AICFileDataContext(DataContext):

    def __init__(self, origin: AICConnection | None, lock_id: str):
        self.lock_id = lock_id
        self.origin = origin

    async def mutate(self, mutation: "AssetMutation", originating_from_server: bool) -> None:
        async def h():
            try:
                # Check if ref is locked or any of it's parents are locked with the current lock_id, if not raise an exception
                if isinstance(mutation.ref, ObjectRef):
                    if _no_lock_taken[mutation.ref].is_set():
                        raise Exception(
                            f"Lock not acquired for chat {mutation.ref.id} request_id={self.lock_id}",
                        )

                apply_mutation(self, mutation)
            except Exception as e:
                _log.exception(f"Error during mutation: {e}")
                raise

        await self.__in_sequence(mutation.ref, h)
        await self.__wait_for_all_mutations(mutation.ref)

        # HANDLE DELETE

        # Remove message group if it's empty
        # if not message_location.message_group.messages:
        #     chat.message_groups = [group for group in chat.message_groups if group.id != message_location.message_group.id]

        # Remove message if it's empty
        # if not tool_call.message.tool_calls and not tool_call.message.content:
        #     tool_call.message_group.messages = [
        #         m for m in tool_call.message_group.messages if m.id != tool_call.message.id
        #     ]

        # Remove message group if it's empty
        # if not tool_call.message_group.messages:
        #    chat.message_groups = [group for group in chat.message_groups if group.id != tool_call.message_group.id]

        # SET VSALUE

        # _handle_SetMessageGroupAgentIdMutation
        # if mutation.actor_id == "user":
        #     message_group.role = "user"
        # else:
        #    message_group.role = "assistant"

        await connection_manager().send_to_ref(
            NotifyAboutAssetMutationServerMessage(
                request_id=self.lock_id,
                mutation=mutation,
            ),
            mutation.ref,
            except_connection=None if originating_from_server else self.origin,
        )

    async def acquire_write_lock(self, ref: ObjectRef, originating_from_server: bool):
        _log.debug(f"Acquiring lock {ref} {self.lock_id}")

        async def h():

            obj = await self.get(ref)

            if obj is not None and obj.lock_id:
                await _wait_for_lock(ref)

            _no_lock_taken[ref].clear()

            if self.origin and not originating_from_server:
                self.origin.lock_acquired(ref=ref, request_id=self.lock_id)

            await self.mutate(LockAcquiredMutation(ref=ref, lock_id=self.lock_id), originating_from_server=True)

        await self.__in_sequence(ref, h)
        # Potential deadlock in original code - What if one connection wants to acquire a lock and another is processing and wants to do another mutation in sequence?
        await self.__wait_for_all_mutations(ref)

    async def release_write_lock(self, ref: ObjectRef, originating_from_server: bool):
        async def h():
            obj = await self.get(ref)
            if obj and obj.lock_id == self.lock_id:
                del _no_lock_taken[ref]

                await self.mutate(LockReleasedMutation(ref=ref, lock_id=self.lock_id), originating_from_server=True)

                if self.origin and not originating_from_server:
                    self.origin.lock_released(ref=ref, request_id=self.lock_id)
            else:
                raise Exception(f"Lock {ref} is not acquired by {self.lock_id}")

        await self.__in_sequence(ref, h)

    @overload
    async def get(self, ref: ObjectRef) -> "BaseObject | None":  # fmt: off
        ...

    @overload
    async def get(self, ref: CollectionRef) -> "List[BaseObject] | None":  # fmt: off
        ...

    async def get(self, ref: "AnyRef") -> "BaseObject | List[BaseObject] | None":
        obj: BaseObject | None = Root(id="root", assets=[])

        segments = ref.ref_segments

        if not segments:
            return obj

        segment = segments.pop(0)
        if segment == "assets":
            if not segments:
                return list(get_project_assets().all_assets())
            # Get the object from the assets collection
            segment = segments.pop(0)
            obj = get_project_assets().get_asset(segment)

            if obj is None or not segments:
                return obj

            while True:
                # Get the sub collection
                segment = segments.pop(0)
                col = cast(List[BaseObject], getattr(obj, segment))

                if col is None or not segments:
                    return col

                # Get the object from the sub collection
                segment = segments.pop(0)
                obj = next((x for x in col if x.id == segment), None)

                if obj is None or not segments:
                    return obj
        else:
            raise Exception(f"Unknown ref type {ref}")

    async def exists(self, ref: "AnyRef") -> bool:
        return await self.get(ref) is not None

    @property
    def type_to_cls_mapping(self) -> dict[str, type[BaseObject]]:
        return {
            "AICMessageGroup": AICMessageGroup,
            "AICMessage": AICMessage,
            "AICToolCall": AICToolCall,
            "AICChat": AICChat,
        }

    async def __wait_for_all_mutations(self, ref: ObjectRef):
        while _waiting_mutations[ref] or _running_mutations[ref] is not None:
            await _mutation_complete_events[ref].wait()

    async def __in_sequence(self, ref: ObjectRef, f: Callable[[], Coroutine]):
        _waiting_mutations[ref].append(f)
        _check_mutation_queue(ref)
