from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, TypeVar

from events.base import EventABC, EventContext
from events.base import BaseEventMessage

T = TypeVar("T", bound=BaseEventMessage)


class EventHandler(ABC):
    """Base contract for user-defined event handlers."""

    @abstractmethod
    def supports(self, event: EventABC[T]) -> bool: ...

    @abstractmethod
    def handle(
        self, event: EventABC[T], context: EventContext
    ) -> Iterable[EventABC[BaseEventMessage]]: ...
