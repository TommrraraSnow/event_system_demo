from __future__ import annotations

from typing import Sequence

from events.tree import EventConfigRepository, LeafConfiguration


class InMemoryEventConfigRepository(EventConfigRepository):
    """Lightweight repository emulating persisted configuration."""

    def __init__(self, snapshot: dict[str, Sequence[LeafConfiguration]] | None = None):
        self._snapshot: dict[str, list[LeafConfiguration]] = {
            node_id: list(configurations)
            for node_id, configurations in (snapshot or {}).items()
        }

    def register(
        self, node_id: str, configuration: LeafConfiguration
    ) -> "InMemoryEventConfigRepository":
        self._snapshot.setdefault(node_id, []).append(configuration)
        return self

    def load_leaf_config(self, node_id: str) -> Sequence[LeafConfiguration]:
        return tuple(self._snapshot.get(node_id, ()))
