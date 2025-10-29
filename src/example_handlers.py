from __future__ import annotations

from typing import Iterable

from events import Event, EventContext, PlayerCreatedMessage, PlayerHealthChangedMessage, PlayerStateChangedMessage, SkillHitMessage
from event_handlers.base import EventHandler
from event_handlers.decorator import event_handler, auto_register
from event_types import EventTypes, SkillEventTypes


# 使用函数装饰器注册事件处理器
@event_handler(EventTypes.PLAYER_CREATED)
def log_player_creation(event: Event, context: EventContext) -> Iterable[Event]:
    """记录玩家创建事件的处理器。"""
    message = event.event_message
    if isinstance(message, PlayerCreatedMessage):
        print(f"[Player Created] 玩家 {message.player_id} ({message.player_name}) 已创建，等级: {message.initial_level}")
    return []


@event_handler(SkillEventTypes.ON_HIT)
def log_skill_damage(event: Event, context: EventContext) -> Iterable[Event]:
    """记录技能伤害事件的处理器。"""
    message = event.event_message
    if isinstance(message, SkillHitMessage):
        critical_text = " (暴击!)" if message.is_critical else ""
        extra_text = " (额外伤害)" if message.is_extra_damage else ""
        print(f"[Skill Hit] 技能 {message.skill_id} 对玩家 {message.target_id} 造成 {message.damage} 点伤害{critical_text}{extra_text}")
    return []


# 使用类装饰器注册事件处理器
@auto_register(EventTypes.PLAYER_STATE_CHANGED)
class PlayerStateEventHandler(EventHandler):
    """玩家状态变更事件处理器。"""

    def supports(self, event: Event) -> bool:
        return event.event_type == EventTypes.PLAYER_STATE_CHANGED

    def handle(self, event: Event, context: EventContext) -> Iterable[Event]:
        message = event.event_message
        if isinstance(message, PlayerStateChangedMessage):
            trail_text = f" (路径: {message.trail})" if message.trail else ""
            print(f"[State Change] 玩家 {message.player_id} 状态变更为: {message.state}{trail_text}")
        return []


@auto_register(EventTypes.PLAYER_HEALTH_CHANGED)
class PlayerHealthEventHandler(EventHandler):
    """玩家生命值变更事件处理器。"""

    def supports(self, event: Event) -> bool:
        return event.event_type == EventTypes.PLAYER_HEALTH_CHANGED

    def handle(self, event: Event, context: EventContext) -> Iterable[Event]:
        message = event.event_message
        if isinstance(message, PlayerHealthChangedMessage):
            source_text = f" (来源: {message.source_event})" if message.source_event else ""
            print(f"[Health Change] 玩家 {message.player_id} 生命值变更为: {message.value}{source_text}")
        return []