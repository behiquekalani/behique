---
title: "tasks"
type: system
tags: [bridge, computer, updated:, 2026-03-15]
created: 2026-03-16
---

# Bridge — Computer 1 ↔ Computer 2 Task Queue
# Updated: 2026-03-15

## How This Works
- Computer 1 (Ceiba) writes tasks below with status [PENDING]
- Computer 2 picks them up, changes to [IN PROGRESS], then [DONE] with notes
- Kalani can also write tasks for either machine
- Pull git before checking. Push after updating.

---

## Tasks for Computer 2

### [DONE] Install Wan2GP Video Generation Server
Completed: 2026-03-20. Server on port 9878 via pm2.

### [PENDING] Fix Wan2GP Gradio API function name in video_server.py
Priority: HIGH
Details: Video server calls `client.predict(api_name="/generate")` but Wan2GP doesn't expose that API name. Jobs fail with "Cannot find a function with api_name: /generate".
Steps:
1. In wan2gp venv Python: `from gradio_client import Client; c = Client("http://127.0.0.1:7860"); print(c.view_api())`
2. Note the actual api_name and parameters
3. Update video_server.py generate_video() to use correct api_name and params
4. `pm2 restart cobo-videogen`

### [WAS] Install Wan2GP Video Generation Server
Details: Ceiba's reel pipeline needs Cobo's GTX 1080 Ti for AI video generation. Scripts are already synced via Syncthing.
Steps:
1. Open PowerShell as Admin
2. Run: `cd C:\Users\kalan\behique\tools\reel-pipeline\cobo-setup`
3. Run: `.\install-wan2gp.ps1`
4. This installs Wan2GP (text-to-video + image-to-video using Wan2.1 models), creates a Python HTTP server on port 9878
5. After install, run: `C:\Wan2GP\start_video_server.bat`
6. Test: `curl http://localhost:9878/jobs` should return `{"jobs":[]}`
7. Ceiba will send video generation requests from 192.168.0.145

### [PENDING] Install ComfyUI + AnimateDiff
Priority: MEDIUM
Details: Secondary video gen option. Scripts synced via Syncthing.
Steps:
1. Run: `.\install-comfyui.ps1` (same cobo-setup folder)
2. Downloads ComfyUI + AnimateDiff motion model (~1.8GB)
3. Starts on port 8188

### [DONE] Cobo Task List — Post-Security Upgrade
Completed: 2026-03-15
Result:
1. **bridge_server_secure.js**: Running via pm2 (pid 15540), auth working. Unauthenticated requests return 401.
2. **OpenClaw Telegram (@CeibaOC2Bot)**: Cannot verify from CLI — needs manual Telegram ping.
3. **Missing skills**: `ceiba-accountability`, `idea-classifier`, `trends-scraper`, `session-closer` are NOT on this machine. Syncthing only syncs `~/behique`, but these skills live in `~/.openclaw/workspace/skills/` on Computer 1 which isn't synced. Current OpenClaw skills on Cobo: ai-tools-navigator, code-auditor, security-auditor (3 of 6).
4. **Syncthing**: Fully synced — 4563/4563 files, 0 needed, 0 errors. Idle state.
5. **COMPUTER2_MIND.md**: Synced and present at `C:\Users\kalan\behique\bridge\COMPUTER2_MIND.md`.
Next: Computer 1 needs to either (a) copy the 4 missing skills into `~/behique/skills/` so Syncthing carries them, or (b) add `~/.openclaw/workspace/skills/` as a separate Syncthing share.

---

## Tasks for Computer 1

### [PENDING] Sync Missing OpenClaw Skills to Cobo
Priority: MEDIUM
Details: Cobo is missing 4 skills (ceiba-accountability, idea-classifier, trends-scraper, session-closer). They exist in `~/.openclaw/workspace/skills/` on Computer 1 but that path isn't synced. Options: (a) copy them into `~/behique/skills/` and have Cobo pull from there, or (b) add a new Syncthing share for the OpenClaw skills directory.

---

## Completed

### [DONE] Install OpenClaw on Computer 2
Completed: 2026-03-15
Notes: OpenClaw v2026.3.13 installed via npm. Onboarded with Anthropic + Telegram. Pairing approved (sender 6168593259). Group policy left as allowlist (DM-only for now).

### [DONE] Set Up Cloudflare Tunnel for n8n
Completed: 2026-03-15
Notes: Tunnel `behique-n8n` (ID: d7f0d4a7-d4e1-4167-adc0-0fe1916b78c2). Domain: n8n.merchoo.shop — LIVE, HTTP 200 confirmed. Running via pm2. Webhook URL set in n8n ecosystem.config.js.

### [DONE] Confirm Ollama Status
Completed: 2026-03-15
Notes: Ollama running, llama3.2:latest (3.2B, Q4_K_M) on port 11434.

### [DONE] Install Cursor
Completed: 2026-03-15
Notes: Cursor v2.6.19 installed via winget.

---

## Tomorrow (2026-03-16)

### [PENDING] Financial Audit
Priority: HIGH
Details: Review all bank/credit card statements. Map every recurring charge — domains, SaaS, subscriptions. Identify what to cancel. Kalani leads this from Computer 1.
