from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar

from src.events.base import BaseEventMessage, EventABC, EventContext

T = TypeVar("T", bound=BaseEventMessage)


class EventHandler(Generic[T], ABC):
    """Base contract for user-defined event handlers."""

    @abstractmethod
    def supports(self, event: EventABC[T]) -> bool: ...

    @abstractmethod
    def handle(
        self, event: EventABC[T], context: EventContext
    ) -> Iterable[EventABC[BaseEventMessage]]: ...
