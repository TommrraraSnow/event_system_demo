from __future__ import annotations

from collections import defaultdict
from typing import Any, DefaultDict, Generator, Iterable, TypeVar

from src.event_handlers.base import EventHandler
from src.event_types import EventType
from src.events.base import BaseEventMessage, EventABC, EventContext

T = TypeVar("T", bound=BaseEventMessage)


class EventHandlerRegistry:
    """Stores handlers grouped by event type for quick lookup."""

    def __init__(self):
        self._handlers: DefaultDict[EventType, list[EventHandler[Any]]] = defaultdict(
            list
        )

    def register(self, event_type: EventType, handler: EventHandler[Any]) -> None:
        self._handlers[event_type].append(handler)

    def iter_handlers(self, event: EventABC[T]) -> Iterable[EventHandler[Any]]:
        for handler in self._handlers.get(event.event_type, []):
            if handler.supports(event):
                yield handler

    def handle(
        self, event: EventABC[T], context: EventContext
    ) -> Generator[EventABC[BaseEventMessage], Any, None]:
        for handler in self.iter_handlers(event):
            yield from handler.handle(event, context)
