from __future__ import annotations

import src.event_handlers.game_handlers
import src.event_handlers.player_handlers
import src.event_handlers.skill_handlers

from .base import EventHandler
from .decorator import (
    auto_register,
    clear_registry,
    event_handler,
    get_global_registry,
    register_handler,
)
from .game_handlers import GameStatsHandler
from .player_handlers import PlayerHealthLogger
from .registry import EventHandlerRegistry

__all__ = [
    "EventHandler",
    "EventHandlerRegistry",
    "event_handler",
    "auto_register",
    "get_global_registry",
    "register_handler",
    "clear_registry",
    "PlayerHealthLogger",
    "GameStatsHandler",
]
