from typing import Any, Awaitable, Callable

from fastmutation.data_context import DataContext
from fastmutation.mutations import (
    AppendToStringMutation,
    AssetMutation,
    CreateMutation,
    DeleteMutation,
    SetValueMutation,
)


async def _handle_CreateMutation(root: DataContext, mutation: CreateMutation):
    collection = await root.get(mutation.ref.parent_collection)

    if collection is None:
        raise ValueError(f"Collection {mutation.ref.parent_collection} not found")

    collection.append(root.type_to_cls_mapping[mutation.object_type](**mutation.object, id=mutation.ref.id))


async def _handle_DeleteMutation(root: DataContext, mutation: DeleteMutation):
    collection = await root.get(mutation.ref.parent_collection)

    if collection is None:
        raise ValueError(f"Collection {mutation.ref.parent_collection} not found")

    object = await root.get(mutation.ref)

    if object is None:
        raise ValueError(f"Object {mutation.ref} not found")

    collection.remove(object)


async def _handle_SetValueMutation(data: DataContext, mutation: SetValueMutation) -> None:
    object = await data.get(mutation.ref)
    setattr(object, mutation.key, mutation.value)


async def _handle_AppendToStringMutation(data: DataContext, mutation: AppendToStringMutation) -> None:
    object = await data.get(mutation.ref)
    setattr(object, mutation.key, getattr(object, mutation.key, "") + mutation.value)


MUTATION_HANDLERS: dict[str, Callable[[DataContext, Any], Awaitable[None]]] = {
    CreateMutation.__name__: _handle_CreateMutation,
    DeleteMutation.__name__: _handle_DeleteMutation,
    SetValueMutation.__name__: _handle_SetValueMutation,
    AppendToStringMutation.__name__: _handle_AppendToStringMutation,
}


def apply_mutation(root: DataContext, mutation: AssetMutation) -> None:
    """
    KEEEP THIS IN SYNC WITH FRONTEND applyMutation!

    Chat to which we received an exclusive write access.
    It provides modification methods which should be used instead of modifying the chat directly.
    """

    MUTATION_HANDLERS[mutation.__class__.__name__](root, mutation)
