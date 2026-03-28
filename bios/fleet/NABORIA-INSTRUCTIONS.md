# NABORIA SETUP (Windows, Always-On, 192.168.0.152)

## ROLE: Web server + always-on processing node

## STEP 1: Check nothing bad is running
Open Task Manager. Kill any "claude" or "node" processes.
No Claude Code should EVER run on Naboria.

## STEP 2: Install Python packages
Open PowerShell as Admin:
```
pip install requests beautifulsoup4 feedparser fastapi uvicorn
```

## STEP 3: Copy files from Syncthing
Make sure Syncthing is running and paired with Ceiba.
Syncthing Web UI: http://localhost:8384
Ceiba device should show as connected.

If files not syncing:
```
scp -r kalani@192.168.0.145:~/behique/bios C:\behique\bios
scp -r kalani@192.168.0.145:~/behique/storefront C:\behique\storefront
scp -r kalani@192.168.0.145:~/behique/tools C:\behique\tools
```

## STEP 4: Start the web server
```
cd C:\behique
python bios\fleet\webserver.py
```
This serves:
- behike.co (port 8080)
- behike.store (port 8080/store)
- BIOS dashboard (port 8080/bios) - localhost only
Leave this window open.

## STEP 5: Start the worker daemon
Open another CMD:
```
cd C:\behique\bios\fleet
python worker.py --machine naboria
```
This picks up tasks from Ceiba via Syncthing.

## STEP 6: Start news scraper
Open another CMD:
```
cd C:\behique\bios\ingestion
python news_scraper.py --run
```
Run every 30 min via Task Scheduler.

## STEP 7: Cloudflare Tunnel (makes behike.co live)
Only do this AFTER Kalani changes nameservers on Namecheap.
```
cd C:\behique\bios\fleet\cloudflare
install_cloudflared.bat
setup_tunnel.bat
```
Follow prompts. This makes behike.co accessible worldwide.

## STEP 8: Set up auto-start on boot
Create a .bat file on Desktop called START-ALL.bat:
```
@echo off
start cmd /k "cd C:\behique && python bios\fleet\webserver.py"
start cmd /k "cd C:\behique\bios\fleet && python worker.py --machine naboria"
echo All services started.
```
Put this in Startup folder: Win+R > shell:startup > paste shortcut

## WHAT NABORIA DOES:
- Hosts behike.co and behike.store websites
- Runs news scrapers and signal processing
- Executes tasks dispatched from Ceiba
- Runs 24/7, no gaming mode needed

## SAFETY:
- No Claude Code. No /build. No auto-resume.
- Only Python scripts and web server.
- Cloudflare provides DDoS protection.
- Admin routes (dashboard, analytics) are localhost-only.
