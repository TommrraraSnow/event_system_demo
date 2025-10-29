from __future__ import annotations

from enum import Enum
from typing import Union


class EventTypes(str, Enum):
    DEFAULT = "default"
    PLAYER_CREATED = "player.created"
    PLAYER_HEALTH_CHANGED = "player.health_changed"
    PLAYER_STATE_CHANGED = "player.state_changed"
    SYSTEM_TICK = "system.tick"


class SkillEventTypes(str, Enum):
    ON_TRIGGERING = "skill.on_triggering"
    ON_HIT = "skill.on_hit"
    ON_END = "skill.on_end"


EventType = Union[EventTypes, SkillEventTypes]

SKILL_ON_HIT = SkillEventTypes.ON_HIT
