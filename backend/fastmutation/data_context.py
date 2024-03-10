import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Dict, List, Type, overload

if TYPE_CHECKING:
    from fastmutation.mutations import AssetMutation
    from fastmutation.types import AnyRef, BaseObject, CollectionRef, ObjectRef


class DataContext(ABC):
    """
    Locking is only for long term locks that are held across multiple requests.
    """

    @abstractmethod
    async def mutate(self, mutation: "AssetMutation", originating_from_server: bool) -> None:
        pass

    @abstractmethod
    async def acquire_write_lock(self, ref: "ObjectRef", lock_id: str, originating_from_server: bool):
        pass

    @abstractmethod
    async def release_write_lock(self, ref: "ObjectRef", lock_id: str, originating_from_server: bool):
        pass

    @abstractmethod
    @overload
    async def get(self, ref: "ObjectRef") -> "BaseObject | None":  # fmt: off
        ...

    @abstractmethod
    @overload
    async def get(self, ref: "CollectionRef") -> "List[BaseObject] | None":  # fmt: off
        ...

    @abstractmethod
    async def get(self, ref: "AnyRef") -> "BaseObject | List[BaseObject] | None":
        pass

    @abstractmethod
    async def exists(self, ref: "AnyRef") -> bool:
        pass

    @property
    @abstractmethod
    def type_to_cls_mapping(self) -> "Dict[str, Type[BaseObject]]":
        pass

    @asynccontextmanager
    async def write_lock(self, ref: "ObjectRef", originating_from_server: bool):
        lock_id = str(uuid.uuid4())
        try:
            await self.acquire_write_lock(ref, lock_id, originating_from_server)
            yield lock_id
        finally:
            await self.release_write_lock(ref, lock_id, originating_from_server)
