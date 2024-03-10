import uuid
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Dict, List, Protocol, Type, overload

if TYPE_CHECKING:
    from fastmutation.mutations import AssetMutation
    from fastmutation.types import AnyRef, BaseObject, CollectionRef, ObjectRef


class DataContext(Protocol):
    """
    Locking is only for long term locks that are held across multiple requests.
    """

    async def mutate(self, mutation: "AssetMutation", originating_from_server: bool) -> None:  # fmt: off
        ...

    async def acquire_write_lock(self, ref: "ObjectRef", lock_id: str, originating_from_server: bool):  # fmt: off
        ...

    async def release_write_lock(self, ref: "ObjectRef", lock_id: str, originating_from_server: bool):  # fmt: off
        ...

    @overload
    async def get(self, ref: "ObjectRef") -> "BaseObject | None":  # fmt: off
        ...

    @overload
    async def get(self, ref: "CollectionRef") -> "List[BaseObject] | None":  # fmt: off
        ...

    async def get(self, ref: "AnyRef") -> "BaseObject | List[BaseObject] | None":  # fmt: off
        ...

    async def exists(self, ref: "AnyRef") -> bool:  # fmt: off
        ...

    @property
    def type_to_cls_mapping(self) -> "Dict[str, Type[BaseObject]]":  # fmt: off
        ...

    @asynccontextmanager
    async def write_lock(self, ref: "ObjectRef", originating_from_server: bool):
        lock_id = str(uuid.uuid4())
        try:
            await self.acquire_write_lock(ref, lock_id, originating_from_server)
            yield lock_id
        finally:
            await self.release_write_lock(ref, lock_id, originating_from_server)
