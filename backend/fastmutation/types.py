from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel, Field

from fastmutation.data_context import DataContext
from fastmutation.mutations import (
    AppendToStringMutation,
    CreateMutation,
    DeleteMutation,
    SetValueMutation,
)

T = TypeVar("T")


class BaseObject(BaseModel):
    id: str
    lock_id: str | None = None


TBaseObject = TypeVar("TBaseObject", bound=BaseObject)


class ObjectRef(Generic[TBaseObject], BaseModel):
    id: str
    parent_collection: "CollectionRef"
    context: "DataContext | None" = Field(
        exclude=True
    )  # Context must be set externally after deserialisation in order to use the object

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self):
        return hash((self.id, self.parent_collection))

    def __eq__(self, other):
        if not isinstance(other, ObjectRef):
            return NotImplemented
        return self.id == other.id and self.parent_collection == other.parent_collection

    @property
    def ref_segments(self):
        ref = self
        segments = []
        while ref is not None:
            segments.append(ref.id)
            segments.append(ref.parent_collection.id)
            ref = ref.parent_collection.parent
        return list(reversed(segments))

    def collection(self, id: str) -> "CollectionRef":
        assert self.context is not None
        return CollectionRef(id=id, parent=self, context=self.context)

    async def set(self, key: str, value: Any):
        assert self.context is not None
        return await self.context.mutate(
            SetValueMutation(ref=self, key=key, value=value), originating_from_server=True
        )

    async def delete(
        self,
    ):
        assert self.context is not None
        return await self.context.mutate(DeleteMutation(ref=self), originating_from_server=True)

    async def get(
        self,
    ) -> TBaseObject:
        assert self.context is not None
        return cast(TBaseObject, await self.context.get(self))

    async def exists(
        self,
    ) -> bool:
        assert self.context is not None
        return await self.context.exists(self)


class CollectionRef(Generic[TBaseObject], BaseModel):
    id: str
    parent: "ObjectRef | None"
    context: "DataContext | None" = Field(
        exclude=True
    )  # Context must be set externally after deserialisation in order to use the object

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self):
        return hash((self.id, self.parent))

    def __eq__(self, other):
        if not isinstance(other, CollectionRef):
            return NotImplemented
        return self.id == other.id and self.parent == other.parent

    @property
    def ref_segments(self):
        ref = self
        segments = []
        while ref is not None:
            segments.append(ref.id)
            if ref.parent is not None:
                segments.append(ref.parent.id)
                ref = ref.parent.parent_collection
            else:
                ref = None
        return list(reversed(segments))

    def __getitem__(self, id: str) -> ObjectRef:
        return ObjectRef(parent_collection=self, id=id, context=self.context)

    async def create(self, object: TBaseObject):
        assert self.context is not None
        return await self.context.mutate(
            CreateMutation(
                ref=ObjectRef(parent_collection=self, id=object.id, context=self.context),
                object_type=object.__class__.__name__,
                object=object.model_dump(mode="json", exclude_unset=True, exclude=set(["id"])),
            ),
            originating_from_server=True,
        )

    async def get_item_id_by_index(self, index: int) -> str:
        objects_list = await self.get()
        if index < 0 or index >= len(objects_list):
            raise IndexError("Index out of range.")
        obj_id = objects_list[index].id
        return obj_id

    async def get(self) -> list[TBaseObject]:
        assert self.context is not None
        return cast(list[TBaseObject], await self.context.get(self))


AnyRef = ObjectRef | CollectionRef


class AttributeRef(Generic[T], BaseModel):
    name: str
    object: ObjectRef
    context: "DataContext | None" = Field(
        exclude=True
    )  # Context must be set externally after deserialisation in order to use the object

    class Config:
        arbitrary_types_allowed = True

    async def set(self, value: T):
        assert self.context is not None
        return await self.context.mutate(
            SetValueMutation(
                ref=self.object,
                key=self.name,
                value=value,
            ),
            originating_from_server=True,
        )

    async def get(
        self,
    ) -> T:
        assert self.context is not None
        return getattr(await self.context.get(self.object), self.name)


class StringAttributeRef(AttributeRef[T]):
    def set(self, value: T):
        return super().set(value)

    def append(self, value: str):
        assert self.context is not None
        return self.context.mutate(
            AppendToStringMutation(
                ref=self.object,
                key=self.name,
                value=value,
            ),
            originating_from_server=True,
        )

    async def get(self) -> T:
        return await super().get()
