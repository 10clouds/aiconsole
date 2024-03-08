from typing import Any, Generic, Literal, TypeVar, cast

from pydantic import BaseModel

from fastmutation.mutation_executor import MutationExecutor

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

    def __hash__(self):
        return hash((self.id, self.parent))

    def __eq__(self, other):
        if not isinstance(other, ObjectRef):
            return NotImplemented
        return self.id == other.id and self.parent == other.parent

    def collection(self, id: str) -> "CollectionRef":
        return CollectionRef(id=id, parent=self)

    def set(self, executor: MutationExecutor, key: str, value: Any):
        return executor.mutate(SetValueMutation(ref=self, key=key, value=value))

    def delete(
        self,
        executor: MutationExecutor,
    ):
        return executor.mutate(DeleteMutation(ref=self))

    def get(
        self,
        executor: MutationExecutor,
    ) -> TBaseObject:
        return cast(TBaseObject, executor.get(self))

    def exists(
        self,
        executor: MutationExecutor,
    ) -> bool:
        return executor.exists(self)


class CollectionRef(BaseModel, Generic[TBaseObject]):
    id: str
    parent: "ObjectRef | None"

    def __hash__(self):
        return hash((self.id, self.parent))

    def __eq__(self, other):
        if not isinstance(other, CollectionRef):
            return NotImplemented
        return self.id == other.id and self.parent == other.parent

    def __getitem__(self, id: str) -> ObjectRef:
        return ObjectRef(parent=self, id=id)

    def create(self, executor: MutationExecutor, object: TBaseObject):
        return executor.mutate(
            CreateMutation(
                ref=ObjectRef(parent=self, id=object.id),
                object_type=object.__class__.__name__,
                object=object.model_dump(mode="json", exclude_unset=True, exclude=set(["id"])),
            )
        )

    def get_item_id_by_index(self, executor: MutationExecutor, index: int) -> str:
        objects_list = self.get(executor)
        if index < 0 or index >= len(objects_list):
            raise IndexError("Index out of range.")
        obj_id = objects_list[index].id
        return obj_id

    def get(self, executor: MutationExecutor) -> list[TBaseObject]:
        return cast(list[TBaseObject], executor.get(self))


AnyRef = ObjectRef | CollectionRef


class AttributeRef(BaseModel, Generic[T]):
    name: str
    object: ObjectRef

    def set(self, executor: MutationExecutor, value: T):
        return executor.mutate(
            SetValueMutation(
                ref=self.object,
                key=self.name,
                value=value,
            )
        )

    def get(
        self,
        executor: MutationExecutor,
    ) -> T:
        return getattr(executor.get(self.object), self.name)


class StringAttributeRef(AttributeRef[T]):
    def set(self, executor: MutationExecutor, value: T):
        return super().set(executor, value)

    def append(self, executor: MutationExecutor, value: str):
        return executor.mutate(
            AppendToStringMutation(
                ref=self.object,
                key=self.name,
                value=value,
            )
        )

    def get(self, executor: MutationExecutor) -> T:
        return super().get(executor)
