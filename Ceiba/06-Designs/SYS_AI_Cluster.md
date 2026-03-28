---
title: "System: AI Cluster (Ceiba + Cobo)"
type: system
tags: [architecture, cluster]
created: 2026-03-16
---

# System: AI Cluster (Ceiba + Cobo)

Two-machine AI cluster:
- **Ceiba** (Mac): Claude Code HQ, orchestration, vault, git
- **Cobo** (Windows): Ollama (llama3.2), n8n, Cloudflare tunnel, GPU tasks

Connected via Syncthing (file sync) and bridge/tasks.md (task delegation). CCP (gRPC) for real-time when both online.

## Links
- [[Computer-2]]
- [[SYS_Bridge]]
- [[ceiba-cobo-communication-protocol-ccp]]
