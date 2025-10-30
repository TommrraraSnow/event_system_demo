from __future__ import annotations

from typing import Iterable

from src.event_handlers.base import EventHandler
from src.event_handlers.decorator import auto_register, event_handler
from src.event_types import EventTypes
from src.events import PlayerHealthChangedMessage, PlayerStateChangedMessage
from src.events.base import BaseEventMessage, EventABC, EventContext


@auto_register(EventTypes.PLAYER_HEALTH_CHANGED)
class PlayerHealthLogger(EventHandler[PlayerHealthChangedMessage]):
    """使用装饰器自动注册的玩家生命值记录器。"""

    def supports(self, event: EventABC[PlayerHealthChangedMessage]) -> bool:
        """检查事件是否为玩家生命值变化事件。"""
        return event.event_type == EventTypes.PLAYER_HEALTH_CHANGED

    def handle(
        self, event: EventABC[PlayerHealthChangedMessage], context: EventContext
    ) -> Iterable[EventABC[BaseEventMessage]]:
        """处理玩家生命值变化事件。"""
        if isinstance(event.event_message, PlayerHealthChangedMessage):
            message = event.event_message
            print(
                f"[health-logger] 玩家 {message.player_id} 当前生命值: {message.value}"
            )

        return []


# 使用函数装饰器创建各种玩家处理器
@event_handler(EventTypes.PLAYER_HEALTH_CHANGED)
def handle_player_health(
    event: EventABC[PlayerHealthChangedMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """处理玩家生命值变化事件。

    记录玩家生命值变化，并在生命值过低时发出警告。

    Args:
        event: 玩家生命值变化事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, PlayerHealthChangedMessage):
        message = event.event_message
        health_status = (
            "危险" if message.value <= 20 else "正常" if message.value > 50 else "警告"
        )

        print(
            f"[player-health] 玩家 {message.player_id} 生命值变化: {message.value} ({health_status})"
        )

        # 如果生命值过低，发出警告
        if message.value <= 0:
            print(f"[player-health] 玩家 {message.player_id} 已经死亡！")
        elif message.value <= 20:
            print(f"[player-health] 玩家 {message.player_id} 生命值极低，需要治疗！")

    return []


@event_handler(EventTypes.PLAYER_HEALTH_CHANGED)
def log_health_change(
    event: EventABC[PlayerHealthChangedMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """记录生命值变化的处理函数。

    Args:
        event: 生命值变化事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, PlayerHealthChangedMessage):
        message = event.event_message
        source = message.source_event or "未知"
        print(
            f"[health-log] {message.player_id}: 来源={source}, 当前生命值={message.value}"
        )

    return []


@event_handler(EventTypes.PLAYER_HEALTH_CHANGED)
def check_health_threshold(
    event: EventABC[PlayerHealthChangedMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """检查生命值阈值的处理函数。

    Args:
        event: 生命值变化事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, PlayerHealthChangedMessage):
        message = event.event_message

        # 检查不同阈值
        if message.value <= 0:
            print(f"[health-threshold] {message.player_id}: 死亡状态")
        elif message.value <= 10:
            print(
                f"[health-threshold] {message.player_id}: 濒死状态 (生命值: {message.value})"
            )
        elif message.value <= 30:
            print(
                f"[health-threshold] {message.player_id}: 重伤状态 (生命值: {message.value})"
            )
        elif message.value <= 60:
            print(
                f"[health-threshold] {message.player_id}: 轻伤状态 (生命值: {message.value})"
            )
        else:
            print(
                f"[health-threshold] {message.player_id}: 健康状态 (生命值: {message.value})"
            )

    return []


# 玩家状态处理器
@event_handler(EventTypes.PLAYER_STATE_CHANGED)
def handle_player_state(
    event: EventABC[PlayerStateChangedMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """玩家状态变化处理函数。

    Args:
        event: 玩家状态变化事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, PlayerStateChangedMessage):
        message = event.event_message
        trail_str = " -> ".join(message.trail) if message.trail else "无路径"
        print(
            f"[player-state] 玩家 {message.player_id} 状态变更为: {message.state} (路径: {trail_str})"
        )

    return []


@event_handler(EventTypes.PLAYER_STATE_CHANGED)
def log_state_transition(
    event: EventABC[PlayerStateChangedMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """记录状态转换的处理函数。

    Args:
        event: 玩家状态变化事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, PlayerStateChangedMessage):
        message = event.event_message
        print(f"[state-transition] {message.player_id}: 转换到状态 '{message.state}'")

        # 可以根据状态执行不同的逻辑
        if message.state == "dead":
            print(
                f"[state-transition] {message.player_id}: 玩家已死亡，需要复活或重新开始"
            )
        elif message.state == "respawning":
            print(f"[state-transition] {message.player_id}: 玩家正在复活中...")
        elif message.state == "active":
            print(f"[state-transition] {message.player_id}: 玩家状态活跃，可以继续游戏")

    return []
