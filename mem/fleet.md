---
purpose: Machine fleet registry — current reality
last_modified: 2026-04-21
machines_online: 2
---

# Fleet — 2026-04-21

**Hutia is retired. Naboria is retired.** Two machines only.

## Current fleet

machines:
  cobo:
    role: PRIMARY — production web server + dev + everything
    os: Windows
    hostname: (desktop tower)
    capabilities:
      - hosts behike.co (via Cloudflare Tunnel)
      - hosts innova-barber, any other live sites
      - UPS protected (CyberPower, PowerPanel connected as of 2026-04-21)
      - Ollama / local LLM
      - Syncthing endpoint
    status: online
    notes: |
      When "the PC" / "the server" / "this machine" is mentioned
      without qualification, it means Cobo. Default assumption.

  ceiba:
    role: Mac dev machine — Kalani's daily driver
    os: macOS
    hostname: Kalanis-MacBook-Air.local (per recent commits)
    capabilities:
      - claude-code (primary build tool)
      - git-push (SSH + GitHub connected)
      - web/browser work
      - Syncthing endpoint
      - full ~/behique read/write
    status: online
    notes: |
      Only the "Mac" / "Ceiba" when Kalani explicitly names it.
      Everything else defaults to Cobo.

## Retired (do not reference as active)
- **Hutia** — Windows laptop, was previous prod server. All `ops/hutia/*` docs are LEGACY. Patterns inside are still useful but the machine name is stale; read them as "how we did it before" not "current setup".
- **Naboria** — was the 24/7 Linux worker. Replaced by Cobo. `bios/fleet/NABORIA-*` files are historical. Railway still hosts BehiqueBot; that's separate from Naboria.

## Sync

sync:
  method: syncthing
  endpoints: [cobo, ceiba]
  shared_folder: ~/behique
  known issues:
    - macOS drops .DS_Store / ._* metadata that pollutes Cobo
    - Occasional `*.sync-conflict-*` files when both machines edit same file
  mitigation: needs .stignore (see ops/cobo/ for template when created)

## Power / outage resilience (Cobo)

| Layer | Protects against | Status |
|---|---|---|
| UPS (CyberPower + PowerPanel) | Brief power dips | ✅ Connected 2026-04-21, config pending |
| BIOS "Restore AC Power" | Power returned after UPS drained | ⏳ Needs configuration |
| Auto-login + NSSM services | Cold boot to services online | ⏳ Needs configuration |
| Telegram uptime monitor | Everything above failed | ✅ Live |

Next steps tracked in `Ceiba/inbox/FLEET_REALITY_2026-04-21.md`.
