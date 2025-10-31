from __future__ import annotations

from typing import Iterable, Literal

from src.event_handlers.decorator import get_global_registry
from src.event_router.dispatcher import EventDispatcher
from src.event_types import EventTypes, SkillEventTypes
from src.events import CallableCondition  # 具体的消息模型
from src.events import (
    BaseEventMessage,
    CallableAction,
    DynamicLeafNode,
    Event,
    EventABC,
    EventBranchNode,
    EventContext,
    EventStateTree,
    EventTransition,
    InMemoryEventConfigRepository,
    LeafConfiguration,
    PlayerHealthChangedMessage,
    PlayerStateChangedMessage,
    SkillHitMessage,
)


def build_state_tree(repo: InMemoryEventConfigRepository) -> EventStateTree:
    """Assemble a simple state-machine tree."""

    root = EventBranchNode("root")
    skill_branch = EventBranchNode("skill_flow")
    player_branch = EventBranchNode("player_flow")

    def always(
        event: EventABC[BaseEventMessage], context: EventContext
    ) -> Literal[True]:
        return True

    any_event = CallableCondition(always)

    root.add_transition(
        SkillEventTypes.ON_HIT,
        EventTransition(any_event, skill_branch),
    )
    root.add_transition(
        EventTypes.PLAYER_HEALTH_CHANGED,
        EventTransition(any_event, player_branch),
    )

    skill_leaf = DynamicLeafNode("skill.damage", repo)
    player_leaf = DynamicLeafNode("player.health", repo)

    skill_branch.add_transition(
        SkillEventTypes.ON_HIT,
        EventTransition(any_event, skill_leaf),
    )
    player_branch.add_transition(
        EventTypes.PLAYER_HEALTH_CHANGED,
        EventTransition(any_event, player_leaf),
    )

    return EventStateTree(root)


def populate_repository(repo: InMemoryEventConfigRepository) -> None:
    """Simulate rows coming from a database describing tree leaves."""

    repo.register(
        "skill.damage",
        LeafConfiguration(
            listen_event=SkillEventTypes.ON_HIT,
            condition=CallableCondition(
                lambda event, context: (
                    isinstance(event.event_message, SkillHitMessage)
                    and event.event_message.damage
                    >= context.attributes.get("damage_threshold", 0)
                )
            ),
            actions=[
                CallableAction(_emit_health_change),
            ],
        ),
    )

    repo.register(
        "player.health",
        LeafConfiguration(
            listen_event=EventTypes.PLAYER_HEALTH_CHANGED,
            condition=CallableCondition(
                lambda event, context: (
                    isinstance(event.event_message, PlayerHealthChangedMessage)
                    and event.event_message.value <= 0
                )
            ),
            actions=[
                CallableAction(_flag_player_state),
            ],
        ),
    )


def _emit_health_change(
    event: EventABC[SkillHitMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """发出生命值变化事件。"""

    message = event.event_message
    remaining = context.attributes.get("target_health", 0) - message.damage

    return [
        Event(
            EventTypes.PLAYER_HEALTH_CHANGED,
            PlayerHealthChangedMessage(
                player_id=message.target_id,
                value=remaining,
                source_event=event.event_type.value,
            ),
        )
    ]


def _flag_player_state(
    event: EventABC[PlayerHealthChangedMessage], context: EventContext
) -> Iterable[EventABC[BaseEventMessage]]:
    """标记玩家状态变化。"""

    message = event.event_message

    return [
        Event(
            EventTypes.PLAYER_STATE_CHANGED,
            PlayerStateChangedMessage(
                player_id=message.player_id,
                state="dead",
                trail=list(context.state_path),
            ),
        )
    ]


def main() -> None:
    repo = InMemoryEventConfigRepository()
    populate_repository(repo)

    tree = build_state_tree(repo)

    # 使用全局注册表（包含装饰器自动注册的处理器）
    registry = get_global_registry()

    # 显示已注册的处理器
    print("已注册的处理器:")
    for event_type, handlers in registry._handlers.items():  # type: ignore
        print(f"  {event_type}: {len(handlers)} 个处理器")
        for handler in handlers:
            print(f"    - {handler}")

    dispatcher = EventDispatcher(tree, registry)

    initial_event = Event(
        SkillEventTypes.ON_HIT,
        SkillHitMessage(
            skill_id="fireball",
            target_id="player-001",
            damage=150,
        ),
    )

    context = EventContext(
        attributes={
            "target_health": 120,
            "damage_threshold": 100,
        }
    )

    processed = dispatcher.emit(initial_event, context=context)

    print(f"Processed {len(processed)} events:")
    for evt in processed:
        print(f" - {evt.event_type.value}: {evt.event_message}")


if __name__ == "__main__":
    main()
