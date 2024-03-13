from typing import Any, Protocol

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.material import AICMaterial
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.locations import ChatRef, ToolCallRef


class ProcessChatDataProtocol(Protocol):
    async def __call__(
        self,
        chat_ref: ChatRef,
        agent: AICAgent,
        materials: list[AICMaterial],
        rendered_materials: list[RenderedMaterial],
        params_values: dict[str, Any] = {},
    ) -> None:  # fmt: off
        ...


class AcceptCodeDataProtocol(Protocol):

    async def __call__(
        self,
        tool_call_ref: ToolCallRef,
        agent: AICAgent,
        materials: list[AICMaterial],
        rendered_materials: list[RenderedMaterial],
    ) -> None:  # fmt: off
        ...


class FetchDataProtocol(Protocol):
    async def __call__(self, command: str, output_format: str) -> None:  # fmt: off
        ...


def process_chat_not_supported(
    chat_ref: ChatRef,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
    params_values: dict[str, Any] = {},
):
    raise NotImplementedError("process chat is not supported")


def accept_code_not_supported(
    tool_call_ref: ToolCallRef,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
):
    raise NotImplementedError("accept code is not supported")


class ExecutionMode:
    def __init__(
        self,
        process_chat: ProcessChatDataProtocol = process_chat_not_supported,
        accept_code: AcceptCodeDataProtocol = accept_code_not_supported,
    ):
        self.accept_code = accept_code
        self.process_chat = process_chat
