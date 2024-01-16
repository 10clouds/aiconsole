from abc import ABC, ABCMeta
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Awaitable, Callable, Type, TypeVar


@dataclass(frozen=True, slots=True)
class InternalEvent(ABC):
    pass


InternalEventT = TypeVar("InternalEventT", bound=InternalEvent)


class InternalEvents:
    """
    Class for multi origin and multi handler  events.
    """

    def __init__(self) -> None:
        self._handlers: dict[ABCMeta, list] = defaultdict(list)

    def subscribe(self, event_type: Type[InternalEventT], handler: Callable[[InternalEventT], Awaitable]):
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: Type[InternalEventT], handler: Callable[[InternalEventT], Awaitable]):
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    async def emit(self, event: InternalEvent) -> None:
        for handler in self._handlers[type(event)]:
            await handler(event)


@lru_cache
def internal_events() -> InternalEvents:
    return InternalEvents()
