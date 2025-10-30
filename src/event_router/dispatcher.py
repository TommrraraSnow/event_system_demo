from __future__ import annotations

from collections import deque
from typing import Any, Deque, Generator, TypeVar

from src.event_handlers.registry import EventHandlerRegistry
from src.events.base import BaseEventMessage, EventABC, EventContext
from src.events.tree import EventStateTree

T = TypeVar("T", bound=BaseEventMessage)


class EventDispatcher:
    """通过handlers和状态树协调路由事件。"""

    def __init__(
        self,
        tree: EventStateTree,
        handler_registry: EventHandlerRegistry,
    ):
        self._tree = tree
        self._handler_registry = handler_registry

    def emit(
        self, event: EventABC[T], context: EventContext | None = None
    ) -> list[EventABC[BaseEventMessage]]:
        context = context or EventContext()
        queue: Deque[tuple[EventABC[BaseEventMessage], EventContext]] = deque(
            [(event, context)]
        )
        processed: list[EventABC[BaseEventMessage]] = []

        while queue:
            current_event, current_context = queue.popleft()
            processed.append(current_event)

            handler_results: Generator[EventABC[BaseEventMessage], Any, None] = (
                self._handler_registry.handle(current_event, current_context)
            )
            tree_results = self._tree.dispatch(current_event, current_context)

            for next_event in handler_results:
                queue.append((next_event, current_context))
            for next_event, next_context in tree_results:
                queue.append(
                    (
                        next_event,
                        EventContext(
                            state_path=(),
                            attributes=next_context.attributes,
                        ),
                    )
                )

        return processed
