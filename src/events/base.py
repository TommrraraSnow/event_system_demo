from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict
from uuid import uuid4
from pydantic import BaseModel, Field
from event_types import EventType


class BaseEventMessage(BaseModel):
    """Standard payload container for all events."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))


# Player Event Messages
class PlayerCreatedMessage(BaseEventMessage):
    """玩家创建事件消息。"""

    player_id: str
    player_name: str
    initial_level: int = 1


class PlayerHealthChangedMessage(BaseEventMessage):
    """玩家生命值变化事件消息。"""

    player_id: str
    value: int
    source_event: str | None = None


class PlayerStateChangedMessage(BaseEventMessage):
    """玩家状态变化事件消息。"""

    player_id: str
    state: str
    trail: list[str] = []


# Skill Event Messages
class SkillHitMessage(BaseEventMessage):
    """技能命中事件消息。"""

    skill_id: str
    target_id: str
    damage: int = 0
    is_critical: bool = False
    is_extra_damage: bool = False


class SkillEndMessage(BaseEventMessage):
    """技能结束事件消息。"""

    skill_id: str
    target_id: str | None = None


# System Event Messages
class SystemTickMessage(BaseEventMessage):
    """系统tick事件消息。"""

    tick_count: int
    timestamp: float | None = None


class EventContext(BaseModel):
    """Carries ambient information while an event traverses the tree."""

    state_path: tuple[str, ...] = ()
    attributes: Dict[str, Any] = {}

    def with_state(self, node_id: str) -> "EventContext":
        return EventContext(
            state_path=self.state_path + (node_id,),
            attributes=self.attributes,
        )


class EventABC[T: BaseEventMessage](ABC):
    """Abstract view for events flowing through the system."""

    @property
    @abstractmethod
    def event_type(self) -> EventType: ...

    @property
    @abstractmethod
    def event_message(self) -> BaseEventMessage: ...


class Event[T: BaseEventMessage](EventABC[T]):
    """Concrete event implementation used by the dispatcher."""

    def __init__(self, event_type: EventType, event_message: T):
        self._event_type = event_type
        self._event_message: T = event_message

    @property
    def event_type(self) -> EventType:
        return self._event_type

    @property
    def event_message(self) -> BaseEventMessage:
        return self._event_message

    def copy_with(
        self,
        *,
        event_type: EventType | None = None,
        **updates: Any,
    ) -> "Event[T]":
        """创建事件副本，可选择更新事件类型和消息字段。"""
        new_event_type = event_type or self._event_type

        # 如果有更新，创建新的消息实例
        if updates:
            # 根据当前消息类型创建新实例
            current_message = self._event_message
            message_data = current_message.model_dump()
            message_data.update(updates)
            new_message = type(current_message)(**message_data)
        else:
            new_message = deepcopy(self._event_message)

        return Event(new_event_type, new_message)
