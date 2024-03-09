from typing import Any, Generic, Literal, TypeVar, cast

from pydantic import BaseModel

from fastmutation.mutation_context import MutationContext

T = TypeVar("T")


class BaseObject(BaseModel):
    id: str


TBaseObject = TypeVar("TBaseObject", bound=BaseObject)


class BaseMutation(BaseModel):
    ref: "ObjectRef"


class LockAcquiredMutation(BaseMutation):
    type: Literal["LockAcquiredMutation"] = "LockAcquiredMutation"
    lock_id: str


class LockReleasedMutation(BaseMutation):
    type: Literal["LockReleasedMutation"] = "LockReleasedMutation"
    lock_id: str


class CreateMutation(BaseMutation):
    type: Literal["CreateMutation"] = "CreateMutation"
    object_type: str
    object: dict


class DeleteMutation(BaseMutation):
    type: Literal["DeleteMutation"] = "DeleteMutation"


class SetValueMutation(BaseMutation):
    type: Literal["SetValueMutation"] = "SetValueMutation"
    key: str
    value: Any = None


class AppendToStringMutation(BaseMutation):
    type: Literal["AppendToStringMutation"] = "AppendToStringMutation"
    key: str
    value: str


AssetMutation = (
    LockAcquiredMutation
    | LockReleasedMutation
    | CreateMutation
    | DeleteMutation
    | SetValueMutation
    | AppendToStringMutation
)


class ObjectRef(BaseModel, Generic[TBaseObject]):
    id: str
    parent: "CollectionRef"
    context: (
        "MutationContext | None"  # Context must be set externally after deserialisation in order to use the object
    )

    class Config:
        fields = {"context": {"exclude": True}}  # Context is not serialised or sent anywhere

    def __hash__(self):
        return hash((self.id, self.parent))

    def __eq__(self, other):
        if not isinstance(other, ObjectRef):
            return NotImplemented
        return self.id == other.id and self.parent == other.parent

    def collection(self, id: str) -> "CollectionRef":
        assert self.context is not None
        return CollectionRef(id=id, parent=self, context=self.context)

    def set(self, key: str, value: Any):
        assert self.context is not None
        return self.context.mutate(SetValueMutation(ref=self, key=key, value=value))

    def delete(
        self,
    ):
        assert self.context is not None
        return self.context.mutate(DeleteMutation(ref=self))

    def get(
        self,
    ) -> TBaseObject:
        assert self.context is not None
        return cast(TBaseObject, self.context.get(self))

    def exists(
        self,
    ) -> bool:
        assert self.context is not None
        return self.context.exists(self)


class CollectionRef(BaseModel, Generic[TBaseObject]):
    id: str
    parent: "ObjectRef | None"
    context: (
        "MutationContext | None"  # Context must be set externally after deserialisation in order to use the object
    )

    class Config:
        fields = {"context": {"exclude": True}}  # Context is not serialised or sent anywhere

    def __hash__(self):
        return hash((self.id, self.parent))

    def __eq__(self, other):
        if not isinstance(other, CollectionRef):
            return NotImplemented
        return self.id == other.id and self.parent == other.parent

    def __getitem__(self, id: str) -> ObjectRef:
        return ObjectRef(parent=self, id=id, context=self.context)

    def create(self, object: TBaseObject):
        assert self.context is not None
        return self.context.mutate(
            CreateMutation(
                ref=ObjectRef(parent=self, id=object.id, context=self.context),
                object_type=object.__class__.__name__,
                object=object.model_dump(mode="json", exclude_unset=True, exclude=set(["id"])),
            )
        )

    def get_item_id_by_index(self, index: int) -> str:
        objects_list = self.get()
        if index < 0 or index >= len(objects_list):
            raise IndexError("Index out of range.")
        obj_id = objects_list[index].id
        return obj_id

    def get(self) -> list[TBaseObject]:
        assert self.context is not None
        return cast(list[TBaseObject], self.context.get(self))


AnyRef = ObjectRef | CollectionRef


class AttributeRef(BaseModel, Generic[T]):
    name: str
    object: ObjectRef
    context: (
        "MutationContext | None"  # Context must be set externally after deserialisation in order to use the object
    )

    class Config:
        fields = {"context": {"exclude": True}}  # Context is not serialised or sent anywhere

    def set(self, value: T):
        assert self.context is not None
        return self.context.mutate(
            SetValueMutation(
                ref=self.object,
                key=self.name,
                value=value,
            )
        )

    def get(
        self,
    ) -> T:
        assert self.context is not None
        return getattr(self.context.get(self.object), self.name)


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
            )
        )

    def get(self) -> T:
        return super().get()
