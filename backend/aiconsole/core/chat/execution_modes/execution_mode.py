from typing import Any, Dict, Protocol

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.material import AICMaterial
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.chat_mutator import ChatMutator


class ProcessChatDataProtocol(Protocol):
    async def __call__(
        self,
        chat_mutator: ChatMutator,
        agent: AICAgent,
        materials: list[AICMaterial],
        rendered_materials: list[RenderedMaterial],
        **kwargs,
    ) -> None:  # fmt: off
        ...


class AcceptCodeDataProtocol(Protocol):
    async def __call__(
        self,
        chat_mutator: ChatMutator,
        tool_call_id: str,
        agent: AICAgent,
        materials: list[AICMaterial],
        rendered_materials: list[RenderedMaterial],
    ) -> None:  # fmt: off
        ...


class FetchDataProtocol(Protocol):
    async def __call__(self, command: str, output_format: str) -> None:  # fmt: off
        ...


def process_chat_not_supported(
    chat_mutator: ChatMutator,
    agent: AICAgent,
    materials: list[AICMaterial],
    rendered_materials: list[RenderedMaterial],
    **kwargs,
):
    raise NotImplementedError("process chat is not supported")


def accept_code_not_supported(
    chat_mutator: ChatMutator,
    tool_call_id: str,
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
        params: Dict[str, Any] = {},
    ):
        self.accept_code = accept_code
        self.params = params
        self.process_chat = self._wrap_process_chat_with_params(process_chat)

    def _wrap_process_chat_with_params(self, process_chat):
        async def wrapper(
            chat_mutator: ChatMutator,
            agent: AICAgent,
            materials: list[AICMaterial],
            rendered_materials: list[RenderedMaterial],
        ):
            await process_chat(
                chat_mutator=chat_mutator,
                agent=agent,
                materials=materials,
                rendered_materials=rendered_materials,
                **self.params,
            )

        return wrapper
