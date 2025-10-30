from __future__ import annotations

from typing import Iterable

from src.event_handlers.decorator import event_handler
from src.event_types import SkillEventTypes
from src.events import SkillHitMessage
from src.events.base import BaseEventMessage, EventABC, EventContext


# 使用装饰器创建技能命中处理器
@event_handler(SkillEventTypes.ON_HIT)
def handle_skill_hit(
    event: EventABC[SkillHitMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """技能命中事件处理函数（装饰器版本）。

    Args:
        event: 技能命中事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, SkillHitMessage):
        message = event.event_message
        print(
            f"[skill-hit-handler] 技能命中：{message.skill_id} -> {message.target_id} (伤害: {message.damage})"
        )

    return []


@event_handler(SkillEventTypes.ON_HIT)
def handle_skill_hit_detailed(
    event: EventABC[SkillHitMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """详细的技能命中事件处理函数。

    当技能命中目标时，记录命中信息并可以根据需要触发后续效果。

    Args:
        event: 技能命中事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, SkillHitMessage):
        message = event.event_message
        print(
            f"[skill-hit] 技能 {message.skill_id} 命中目标 {message.target_id}，造成 {message.damage} 点伤害"
        )

        # 可以在这里添加额外的逻辑，比如：
        # - 检查目标是否有护甲
        # - 计算实际伤害
        # - 触发技能特效等

    return []


@event_handler(SkillEventTypes.ON_HIT)
def log_skill_damage(
    event: EventABC[SkillHitMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """记录技能伤害的处理函数。

    Args:
        event: 技能命中事件
        context: 事件上下文

    Returns:
        空列表，不产生新事件
    """
    if isinstance(event.event_message, SkillHitMessage):
        message = event.event_message
        is_critical = "暴击" if message.is_critical else "普通"
        print(
            f"[skill-damage] {message.skill_id} 造成 {message.damage} 点伤害 ({is_critical})"
        )

    return []
