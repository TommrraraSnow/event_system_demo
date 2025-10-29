from __future__ import annotations

from typing import Iterable

from events.base import EventABC, EventContext, BaseEventMessage
from event_handlers.base import EventHandler
from event_types import EventTypes, SkillEventTypes
from events import PlayerHealthChangedMessage, PlayerStateChangedMessage, SkillHitMessage
from event_handlers.decorator import event_handler, auto_register


# 游戏统计处理器（使用类装饰器，因为需要维护状态）
@auto_register(SkillEventTypes.ON_HIT)
@auto_register(EventTypes.PLAYER_HEALTH_CHANGED)
@auto_register(EventTypes.PLAYER_STATE_CHANGED)
class GameStatsHandler(EventHandler):
    """游戏统计处理器，收集和分析游戏数据。"""

    def __init__(self):
        self.total_damage = 0
        self.health_changes = 0
        self.state_changes = 0

    def supports(self, event: EventABC[BaseEventMessage]) -> bool:
        """支持所有游戏相关事件进行统计。"""
        return True  # 统计所有事件

    def handle(
        self, event: EventABC[BaseEventMessage], context: EventContext
    ) -> Iterable[EventABC[BaseEventMessage]]:
        """收集游戏统计数据。

        Args:
            event: 游戏事件
            context: 事件上下文

        Returns:
            空列表，不产生新事件
        """
        if isinstance(event.event_message, SkillHitMessage):
            self.total_damage += event.event_message.damage
        elif isinstance(event.event_message, PlayerHealthChangedMessage):
            self.health_changes += 1
        elif isinstance(event.event_message, PlayerStateChangedMessage):
            self.state_changes += 1

        print(f"[game-stats] 总伤害: {self.total_damage}, 生命值变化: {self.health_changes}, 状态变化: {self.state_changes}")

        return []


# 使用装饰器创建各种游戏事件处理器
@event_handler(EventTypes.PLAYER_HEALTH_CHANGED)
def game_log_health(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """记录玩家生命值变化到游戏日志。

    Args:
        event: 玩家生命值变化事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    timestamp = context.attributes.get("timestamp", "未知时间")
    print(f"[game-log] [{timestamp}] 玩家生命值变化: {event.event_message}")

    return []


@event_handler(EventTypes.PLAYER_STATE_CHANGED)
def game_log_state(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """记录玩家状态变化到游戏日志。

    Args:
        event: 玩家状态变化事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    timestamp = context.attributes.get("timestamp", "未知时间")
    print(f"[game-log] [{timestamp}] 玩家状态变化: {event.event_message}")

    return []


@event_handler(EventTypes.PLAYER_CREATED)
def game_log_player_created(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """记录玩家创建到游戏日志。

    Args:
        event: 玩家创建事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    timestamp = context.attributes.get("timestamp", "未知时间")
    print(f"[game-log] [{timestamp}] 玩家创建: {event.event_message}")

    return []


@event_handler(EventTypes.SYSTEM_TICK)
def handle_system_tick(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """系统时钟事件处理器。

    Args:
        event: 系统时钟事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    tick_count = context.attributes.get("tick_count", 0)
    print(f"[system-tick] 系统时钟 #{tick_count}")

    return []


@event_handler(EventTypes.PLAYER_CREATED)
def handle_player_created(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """玩家创建事件处理器。

    Args:
        event: 玩家创建事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    print(f"[player-created] 新玩家加入游戏: {event.event_message}")
    return []


# 性能监控处理器
@event_handler(SkillEventTypes.ON_HIT)
def monitor_skill_performance(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """监控技能性能的处理函数。

    Args:
        event: 技能命中事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, SkillHitMessage):
        message = event.event_message
        efficiency = "高" if message.damage >= 100 else "中" if message.damage >= 50 else "低"
        print(f"[skill-monitor] 技能 {message.skill_id} 效率: {efficiency} (伤害: {message.damage})")

    return []


# 事件流程追踪器
@event_handler(EventTypes.DEFAULT)
def trace_event_flow(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """事件流程追踪器，记录事件的完整处理过程。

    Args:
        event: 任意事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    print(f"[event-trace] 开始处理事件: {event.event_type.value}")
    print(f"[event-trace] 当前状态路径: {' -> '.join(context.state_path)}")
    print(f"[event-trace] 上下文属性键: {list(context.attributes.keys())}")

    return []


# 游戏平衡分析器
@event_handler(SkillEventTypes.ON_HIT)
def analyze_game_balance(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """游戏平衡分析器，分析技能伤害是否平衡。

    Args:
        event: 技能命中事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, SkillHitMessage):
        message = event.event_message
        target_health = context.attributes.get("target_health", 100)
        damage_percentage = (message.damage / target_health) * 100 if target_health > 0 else 100

        if damage_percentage > 80:
            print(f"[balance-analysis] 技能 {message.skill_id} 伤害过高，占目标生命值 {damage_percentage:.1f}%")
        elif damage_percentage < 20:
            print(f"[balance-analysis] 技能 {message.skill_id} 伤害过低，仅占目标生命值 {damage_percentage:.1f}%")
        else:
            print(f"[balance-analysis] 技能 {message.skill_id} 伤害适中，占目标生命值 {damage_percentage:.1f}%")

    return []


# 调试处理器 - 输出详细的事件信息
@event_handler(EventTypes.DEFAULT)
def debug_event(event: EventABC[BaseEventMessage], context: EventContext) -> Iterable[EventABC[BaseEventMessage]]:
    """调试事件处理器，输出所有事件的详细信息。

    Args:
        event: 任意事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    print(f"[debug] 事件类型: {event.event_type}")
    print(f"[debug] 事件消息: {event.event_message}")
    print(f"[debug] 上下文路径: {context.state_path}")
    print(f"[debug] 上下文属性: {context.attributes}")
    print("---")

    return []