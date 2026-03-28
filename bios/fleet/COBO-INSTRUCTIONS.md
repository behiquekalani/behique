# COBO SETUP (Windows, GTX 1080 Ti, 192.168.0.151)

## STEP 1: Check nothing bad is running
Open Task Manager (Ctrl+Shift+Esc). Kill any "claude" or "node" processes you don't recognize.
Check C:\behique\mode.json exists. If not, create it:
```json
{"mode": "normal", "paused_since": null}
```

## STEP 2: Install Python packages
Open PowerShell as Admin:
```
pip install requests beautifulsoup4 feedparser Pillow pystray
```

## STEP 3: Copy files from Syncthing
Make sure Syncthing is running. Files should sync from Ceiba automatically.
If not syncing, manually copy from Ceiba:
```
scp -r kalani@192.168.0.145:~/behique/bios C:\behique\bios
scp -r kalani@192.168.0.145:~/behique/tools C:\behique\tools
```

## STEP 4: Start the worker daemon
Open CMD:
```
cd C:\behique\bios\fleet
python worker.py --machine cobo
```
This polls the queue/ folder for tasks from Ceiba and executes them.
Leave this window open.

## STEP 5: Start the social scraper loop
Open another CMD:
```
cd C:\behique\bios\ingestion
python social_scraper.py --run
```
Run this every 30 min or set up Task Scheduler.

## STEP 6: Gaming mode toggle
Copy gaming_toggle_simple.bat to your Desktop.
Double-click to toggle between work/gaming mode.
When gaming mode is ON, all BIOS tasks pause.

## STEP 7: Stable Diffusion (optional)
If you want image generation:
```
cd C:\behique\tools\sd-generator
install_cobo.bat
```
Then run: start_sd.bat

## WHAT COBO DOES:
- Runs social scrapers (Reddit, CoinGecko, Fear&Greed)
- Generates images via Stable Diffusion
- Generates blueprints via Ollama
- Executes tasks dispatched from Ceiba
- Pauses everything when you game

## SAFETY:
- No Claude Code runs here. Only Python scripts.
- No /build loops possible. No auto-resume.
- Gaming mode stops all tasks.
- Check mode.json to verify state.
