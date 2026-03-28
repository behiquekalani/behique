# DEPLOY NOW - Fleet Activation

## COBO (192.168.0.151) - Heavy Compute

### Step 1: Open CMD as Admin, run the deploy script

```bat
mkdir C:\behique\bios 2>nul
cd C:\behique\bios
```

Copy the entire contents of `deploy_cobo.bat` and paste into CMD. Or transfer the file and run:

```bat
C:\behique\bios\deploy_cobo.bat
```

### Step 2: Install Python dependencies

```bat
pip install requests
```

### Step 3: Start everything (paste into 3 separate CMD windows)

Window 1 - Worker Daemon:
```bat
cd C:\behique\bios\fleet
python worker.py --machine cobo --interval 30
```

Window 2 - Social Scraper Loop:
```bat
start "BIOS-Scraper" "C:\behique\bios\run_scraper.bat"
```

Window 3 - Blueprint Generator Loop:
```bat
start "BIOS-Blueprint" "C:\behique\bios\run_blueprint.bat"
```

### Gaming Mode Toggle

Switch to gaming (pauses scraper + blueprint loops):
```bat
echo {"mode": "gaming"} > C:\behique\mode.json
```

Switch back to work:
```bat
echo {"mode": "work"} > C:\behique\mode.json
```

---

## NABORIA (192.168.0.152) - Ingestion (Always-On)

### Step 1: Open CMD as Admin, run the deploy script

```bat
mkdir C:\behique\bios 2>nul
cd C:\behique\bios
```

Copy the entire contents of `deploy_naboria.bat` and paste into CMD. Or transfer the file and run:

```bat
C:\behique\bios\deploy_naboria.bat
```

### Step 2: Install Python dependencies

```bat
pip install requests
```

### Step 3: Start everything (paste into 3 separate CMD windows)

Window 1 - Worker Daemon:
```bat
cd C:\behique\bios\fleet
python worker.py --machine naboria --interval 30
```

Window 2 - News Ingestion Loop:
```bat
start "BIOS-News" "C:\behique\bios\run_news.bat"
```

Window 3 - Signal Processing Loop:
```bat
start "BIOS-Signals" "C:\behique\bios\run_signals.bat"
```

---

## VERIFICATION (Run from Ceiba / Mac)

### Ping both machines
```bash
ping -c 1 192.168.0.151 && echo "COBO: UP" || echo "COBO: DOWN"
ping -c 1 192.168.0.152 && echo "NABORIA: UP" || echo "NABORIA: DOWN"
```

### Check worker daemon ports
```bash
curl -s --connect-timeout 3 http://192.168.0.151:9876/status && echo "" || echo "COBO bridge: no response"
curl -s --connect-timeout 3 http://192.168.0.152:9876/status && echo "" || echo "NABORIA bridge: no response"
```

### Check Syncthing sync is working (verify queue files propagate)
```bash
python3 ~/behique/bios/fleet/coordinator.py --ping
```

### Check fleet status
```bash
python3 ~/behique/bios/fleet/coordinator.py --status
```

### Send a test task to Cobo
```bash
python3 ~/behique/bios/fleet/dispatch.py --machine cobo --type custom --params '{"command": "echo BIOS fleet online"}'
```

### Send a test task to Naboria
```bash
python3 ~/behique/bios/fleet/dispatch.py --machine naboria --type custom --params '{"command": "echo BIOS fleet online"}'
```

### Check logs on each machine
Cobo: `type C:\behique\bios\logs\runner.log`
Naboria: `type C:\behique\bios\logs\news_runner.log`
Worker logs: `type C:\behique\bios\fleet\logs\worker-cobo-*.log`
