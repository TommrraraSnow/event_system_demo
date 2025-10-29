## Event System Demo

This project demonstrates an event-driven runtime where *everything is an event*.
The core idea is a lightweight state-machine rendered as a tree whose leaves are
defined dynamically from persisted (e.g. database) configuration. Each leaf can:

- declare which event types it listens to,
- evaluate business conditions against the event payload plus contextual state,
- emit follow-up events that continue traversing the tree.

### Key Modules

- `events.base`: foundational event/message abstractions (`Event`, `EventContext`)
- `events.tree`: tree nodes (`EventBranchNode`, `DynamicLeafNode`) and their wiring
- `events.repository`: example repository that mimics database-sourced leaf rows
- `event_router.dispatcher`: orchestrates handlers and tree dispatch
- `event_handlers.*`: pluggable application logic reacting to emitted events

### Example Flow

`main.py` assembles the components in four steps:

1. Populate an `InMemoryEventConfigRepository` with mock rows describing
   skill-damage and player-health leaves.
2. Build a tree: root → skill/player branches → dynamic leaves.
3. Register a handler that logs player state changes.
4. Emit a `skill.on_hit` event and let the tree/handlers produce downstream events.

Running `python main.py` prints the processed events and illustrates how a single
input drives a cascade of derived events through the tree.
