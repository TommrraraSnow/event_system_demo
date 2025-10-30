from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Iterable, Protocol, Sequence

from src.event_types import EventType

from .base import BaseEventMessage, EventABC, EventContext


class EventCondition(ABC):

    @abstractmethod
    def evaluate(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> bool: ...


class CallableCondition(EventCondition):
    """包装最基本的函数判断器"""

    def __init__(self, fn: Callable[[EventABC[BaseEventMessage], EventContext], bool]):
        self._fn = fn

    def evaluate(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> bool:
        return bool(self._fn(event, context))


class EventAction(ABC):
    """当节点的条件得到满足时，会生成新的事件。"""

    @abstractmethod
    def produce(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> Iterable[EventABC[BaseEventMessage]]: ...


class CallableAction(EventAction):
    """包装函数触发器"""

    def __init__(
        self,
        fn: Callable[
            [EventABC[BaseEventMessage], EventContext],
            Iterable[EventABC[BaseEventMessage]],
        ],
    ):
        self._fn = fn

    def produce(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> Iterable[EventABC[BaseEventMessage]]:
        return list(self._fn(event, context))


@dataclass(frozen=True)
class LeafConfiguration:
    """描述动态叶子运行方式的持久化定义。"""

    listen_event: EventType
    condition: EventCondition
    actions: Sequence[EventAction] = field(default_factory=tuple)


class EventConfigRepository(Protocol):
    """用于加载事件树配置的抽象接口。"""

    def load_leaf_config(self, node_id: str) -> Sequence[LeafConfiguration]: ...


@dataclass
class EventTransition:
    """表示一个状态机风格的、指向另一个节点（可扩展为多子节点）"""

    condition: EventCondition
    target: "EventTreeNode"

    def matches(self, event: EventABC[BaseEventMessage], context: EventContext) -> bool:
        return self.condition.evaluate(event, context)


class EventTreeNode(ABC):
    """事件状态树的基本构建块。"""

    def __init__(self, node_id: str):
        self.node_id = node_id

    def handle(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> Iterable[tuple[EventABC[BaseEventMessage], EventContext]]:
        node_context = context.with_state(self.node_id)
        yield from self._handle(event, node_context)

    @abstractmethod
    def _handle(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> Iterable[tuple[EventABC[BaseEventMessage], EventContext]]: ...


class EventBranchNode(EventTreeNode):

    def __init__(self, node_id: str):
        super().__init__(node_id)
        self._transitions: dict[EventType, list[EventTransition]] = {}

    def add_transition(
        self, listen_event: EventType, transition: EventTransition
    ) -> None:
        self._transitions.setdefault(listen_event, []).append(transition)

    def _handle(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> Iterable[tuple[EventABC[BaseEventMessage], EventContext]]:
        transitions = self._transitions.get(event.event_type, [])
        for transition in transitions:
            if transition.matches(event, context):
                yield from transition.target.handle(event, context)


class DynamicLeafNode(EventTreeNode):

    def __init__(self, node_id: str, repository: EventConfigRepository):
        super().__init__(node_id)
        self._repository = repository
        self._config: Sequence[LeafConfiguration] | None = None

    def _ensure_config_loaded(self) -> Sequence[LeafConfiguration]:
        if self._config is None:
            self._config = self._repository.load_leaf_config(self.node_id)
        return self._config

    def _handle(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> Iterable[tuple[EventABC[BaseEventMessage], EventContext]]:
        for config in self._ensure_config_loaded():
            if config.listen_event != event.event_type:
                continue
            if not config.condition.evaluate(event, context):
                continue
            for action in config.actions:
                for produced in action.produce(event, context):
                    yield produced, context


class EventStateTree:

    def __init__(self, root: EventTreeNode):
        self._root = root

    def dispatch(
        self, event: EventABC[BaseEventMessage], context: EventContext | None = None
    ) -> list[tuple[EventABC[BaseEventMessage], EventContext]]:
        ctx = context or EventContext()
        return list(self._root.handle(event, ctx))
