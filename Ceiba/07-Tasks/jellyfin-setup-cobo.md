---
type: task
target: cobo
status: pending
created: 2026-03-17
tags: [infrastructure, media, cobo]
---

# Jellyfin Media Server Setup — Cobo

## What
Install Jellyfin on Cobo (Windows desktop) so Kalani can stream videos to Fire Stick TV on the local network.

## Why Jellyfin
- Free, open source, no account/cloud required
- Fire Stick app available on Amazon App Store
- Runs as a Windows service alongside existing Cobo stack (Ollama, n8n, bridge server)

---

## COBO SETUP STEPS

### 1. Download & Install Jellyfin
```powershell
# Option A: winget (if available)
winget install Jellyfin.Server

# Option B: Manual download
# Go to https://jellyfin.org/downloads/server → Windows → Installer (x64)
# Run the .exe installer
```

### 2. During Install
- Install as a **Windows Service** (runs in background automatically)
- It will open the setup wizard at `http://localhost:8096`

### 3. Setup Wizard (in browser)
1. Create an admin account (username + password)
2. Add media library:
   - Type: **Movies** or **Mixed Content** (depending on what's there)
   - Folder: `C:\Users\kalan\Desktop` (or wherever the videos are — adjust path)
   - Can add multiple folders if videos are spread around
3. Set preferred language: **Spanish** or English
4. Allow remote connections: **Yes** (needed for Fire Stick)
5. Finish wizard

### 4. Verify
- Open browser on Cobo: `http://localhost:8096`
- Confirm videos appear in the library
- From another device on the network, confirm `http://192.168.0.151:8096` loads

---

## FIRE STICK SETUP (Kalani does this on TV)

1. Open **Amazon App Store** on Fire Stick
2. Search **"Jellyfin"** → Install
3. Open Jellyfin app
4. Server address: `http://192.168.0.151:8096`
5. Log in with the admin account created during setup
6. Videos should appear — browse and play

---

## Notes
- Jellyfin auto-detects new files added to the media folder
- Fire Stick natively plays most formats (MP4, MKV, AVI) — minimal transcoding needed
- Jellyfin web UI available at `http://192.168.0.151:8096` from any device
- Service auto-starts with Windows — no need to add to pm2
