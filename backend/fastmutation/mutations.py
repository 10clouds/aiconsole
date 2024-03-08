from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from fastmutation.types import CollectionRef, ObjectRef


class BaseMutation(BaseModel):
    pass


class LockAcquiredMutation(BaseMutation):
    type: Literal["LockAcquiredMutation"] = "LockAcquiredMutation"
    lock_id: str


class LockReleasedMutation(BaseMutation):
    type: Literal["LockReleasedMutation"] = "LockReleasedMutation"
    lock_id: str


class CreateMutation(BaseMutation):
    type: Literal["CreateMutation"] = "CreateMutation"
    collection: "CollectionRef"
    object: dict


class DeleteMutation(BaseMutation):
    type: Literal["DeleteMutation"] = "DeleteMutation"
    path: "ObjectRef"


class SetValueMutation(BaseMutation):
    type: Literal["SetValueMutation"] = "SetValueMutation"
    path: "ObjectRef"
    key: str
    value: Any = None


class AppendToStringMutation(BaseMutation):
    type: Literal["AppendToStringMutation"] = "AppendToStringMutation"
    path: "ObjectRef"
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
