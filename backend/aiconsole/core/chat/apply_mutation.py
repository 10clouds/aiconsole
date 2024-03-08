import logging
from typing import Any, Callable, cast

from pydantic import BaseModel

from aiconsole.core.chat.root import Root
from aiconsole.core.chat.types import AICChat, AICMessage, AICMessageGroup, AICToolCall
from fastmutation.types import (
    AppendToStringMutation,
    AssetMutation,
    CollectionRef,
    CreateMutation,
    DeleteMutation,
    ObjectRef,
    SetValueMutation,
)

_log = logging.getLogger(__name__)


# Handlers


def find_object(root: BaseModel, obj: ObjectRef) -> None:
    base_collection = find_collection(root, obj.parent)

    if not base_collection:
        raise ValueError(f"Collection {obj.parent} not found")

    if obj.id not in base_collection:
        raise ValueError(f"Object {obj.id} not found")

    return next((item for item in base_collection if item.id == obj.id), None)


def find_collection(root: BaseModel, collection: CollectionRef):
    base_object = root

    if collection.parent:
        base_object = find_object(root, collection.parent)

    return cast(list[Any], getattr(base_object, collection.id, None))


def _handle_CreateMutation(root: Root, mutation: CreateMutation) -> None:
    collection = find_collection(root, mutation.ref.parent)

    types = {
        "AICMessageGroup": AICMessageGroup,
        "AICMessage": AICMessage,
        "AICToolCall": AICToolCall,
        "AICChat": AICChat,
    }

    collection.append(types[mutation.object_type](**mutation.object, id=mutation.ref.id))


def _handle_DeleteMutation(root: Root, mutation: DeleteMutation) -> None:
    collection = find_collection(root, mutation.ref.parent)
    collection.remove(find_object(root, mutation.ref))

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


def _handle_SetValueMutation(chat, mutation: SetValueMutation) -> None:
    object = find_object(chat, mutation.ref)
    setattr(object, mutation.key, mutation.value)


def _handle_AppendToStringMutation(chat, mutation: AppendToStringMutation) -> None:
    object = find_object(chat, mutation.ref)
    setattr(object, mutation.key, getattr(object, mutation.key, "") + mutation.value)


MUTATION_HANDLERS: dict[str, Callable[[Root, Any], None]] = {
    CreateMutation.__name__: _handle_CreateMutation,
    DeleteMutation.__name__: _handle_DeleteMutation,
    SetValueMutation.__name__: _handle_SetValueMutation,
    AppendToStringMutation.__name__: _handle_AppendToStringMutation,
}


# Entry point


def apply_mutation(root: Root, mutation: AssetMutation) -> None:
    """
    KEEEP THIS IN SYNC WITH FRONTEND applyMutation!

    Chat to which we received an exclusive write access.
    It provides modification methods which should be used instead of modifying the chat directly.
    """

    MUTATION_HANDLERS[mutation.__class__.__name__](root, mutation)
