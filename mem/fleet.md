---
purpose: Machine fleet registry and task delegation
last_modified: 2026-03-28
machines_online: 1
---

# Fleet Sync

## Machines

machines:
  ceiba:
    role: primary
    os: macOS
    hostname: Kalanis-MacBook-Pro
    capabilities:
      - claude-code (primary build tool)
      - brave-pdf (PDF rendering with --force-device-scale-factor=2)
      - git-push (SSH key configured, GitHub connected)
      - gumroad (web access for product listing)
      - file-system (full read/write to ~/behique)
    status: online
    ip: local

  cobo:
    role: content-generation
    os: linux
    capabilities:
      - ollama (local LLM inference)
      - free-tier-rotation (ChatGPT, Gemini, etc.)
      - batch-content (generate social posts, blog drafts)
    status: offline
    ip: 192.168.0.151
    notes: "Use for bulk content generation to save Claude credits"

  naboria:
    role: always-on-worker
    os: linux
    capabilities:
      - hosting (behike.store, Railway)
      - background-tasks (cron jobs, scrapers)
      - discord-bot (BehiqueBot)
      - telegram-bot (live on Railway)
    status: offline
    ip: 192.168.0.152
    notes: "Always-on server for 24/7 services"

## Sync Configuration

sync:
  method: syncthing
  shared_folders:
    - mem/          # Memory system synced across all machines
    - READY-TO-SELL/gumroad-ready/  # Product files accessible everywhere
  sync_interval: realtime
  conflict_resolution: newest-wins

## Task Delegation

### Cobo Tasks (when online)
- Generate 10 social media captions using Gemini free tier
- Generate 5 blog post drafts using ChatGPT free tier
- Run niche research with local Ollama
- Batch process content templates
- Generate Instagram post variations

### Naboria Tasks (when online)
- Run Discord bot 24/7
- Host behike.store
- Run niche scanner on schedule
- Process webhook events
- Background data collection

### Ceiba Tasks (always)
- All product building (PDFs, covers, thumbnails)
- Git operations (commit, push)
- Memory system management
- Interactive work with Kalani

## How to Delegate
1. Check machine status in this file
2. If target machine is online: write task to shared sync folder
3. If offline: queue in status.md as todo with owner tag
4. Task results appear in synced output folders

## Wake Commands
```bash
# Wake Cobo
ssh kalani@192.168.0.151 'echo "online"' 2>/dev/null && echo "Cobo: ONLINE" || echo "Cobo: OFFLINE"

# Wake Naboria
ssh kalani@192.168.0.152 'echo "online"' 2>/dev/null && echo "Naboria: ONLINE" || echo "Naboria: OFFLINE"
```
