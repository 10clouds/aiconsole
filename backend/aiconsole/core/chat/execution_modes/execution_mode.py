from dataclasses import dataclass
from typing import Awaitable, Callable

from pydantic import BaseModel

from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.chat_mutator import ChatMutator


@dataclass
class ProcessChatContext:
    chat_mutator: ChatMutator
    agent: Agent
    materials: list[Material]
    rendered_materials: list[RenderedMaterial]


@dataclass
class AcceptCodeContext:
    chat_mutator: ChatMutator
    tool_call_id: str
    agent: Agent
    materials: list[Material]
    rendered_materials: list[RenderedMaterial]


class ExecutionMode(BaseModel):
    process_chat: Callable[[ProcessChatContext], Awaitable[None]]
    accept_code: Callable[[AcceptCodeContext], Awaitable[None]]


def accept_code_not_supported(context: AcceptCodeContext):
    raise NotImplementedError(f"running code is not supported by {context.agent.name} ({context.agent.id}) agent")
