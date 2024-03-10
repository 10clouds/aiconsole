from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from fastmutation.types import ObjectRef


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
