---
title: "System: Ceiba-Cobo Bridge"
type: system
tags: [bridge, syncthing]
created: 2026-03-16
---

# System: Ceiba-Cobo Bridge

Cross-machine task delegation via bridge/tasks.md (Syncthing-synced). Wake.sh checks health, sleep.sh closes session. No SSH — file-based protocol.

## Components
- `bridge/tasks.md` — task queue
- `bridge/wake.sh` — cluster health check
- `bridge/sleep.sh` — session teardown
- Syncthing — bidirectional file sync

## Links
- [[SYS_AI_Cluster]]
- [[Computer-2]]
