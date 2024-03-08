from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from fastmutation.types import AnyRef, AssetMutation, BaseObject


class MutationExecutor(Protocol):
    async def mutate(self, mutation: "AssetMutation") -> None:  # fmt: off
        ...

    def get(self, ref: "AnyRef") -> "BaseObject | list[BaseObject]":  # fmt: off
        ...

    def exists(self, ref: "AnyRef") -> bool:  # fmt: off
        ...
