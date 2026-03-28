# Hutia Rebuild Plan: Clean Wipe + Old Laptop Fleet Expansion

Created: 2026-03-21
Purpose: Wipe Hutia (Machine C) clean, rebuild it as a headless always-on node using ONLY the AI Employee Guide instructions. Then repeat the process on grandpa's old laptops. This is dogfooding. If it works on old hardware, the guide is proven and sellable.

---

## Phase 1: Save What Matters (BEFORE Wiping)

Hutia is currently a Windows machine at 192.168.0.152 running:
- Bridge server on port 9877 (Node.js, pm2)
- Auth token at C:\behique\.bridge_token
- Task queue at C:\behique\tasks.json
- Can forward tasks to Cobo at 192.168.0.151:9876

### What to back up

| Item | Location on Hutia | Why |
|------|-------------------|-----|
| Bridge server code | C:\behique\bridge_server.js | Reference for rebuild (also in HUTIA_SETUP.md) |
| Bridge auth token | C:\behique\.bridge_token | Ceiba uses this to authenticate. Regenerate on rebuild. |
| Task history | C:\behique\tasks.json | Optional. Historical data only. |
| Any custom scripts | C:\behique\*.py, C:\behique\*.js | Catch anything we forgot about |
| Scheduled tasks | Windows Task Scheduler | Equivalent of cron. Check for anything running. |
| Installed services | Services list | Check what's auto-starting |
| Network config | Static IP settings | Need to keep 192.168.0.152 |
| SSH keys | C:\Users\kalani\.ssh\ | If any exist |

### Backup script (run FROM Ceiba)

Save this as `~/behique/tools/hutia-backup.sh` and run it before wiping.

```bash
#!/bin/bash
# hutia-backup.sh - Run from Ceiba (Mac) before wiping Hutia
# Pulls everything important off Hutia via SSH/SCP
# Requires: SSH access to kalani@192.168.0.152

HUTIA="kalani@192.168.0.152"
BACKUP_DIR="$HOME/behique/hutia-backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "=== Hutia Backup Starting ==="
echo "Backup dir: $BACKUP_DIR"
echo ""

# 1. Bridge server and config
echo "[1/8] Pulling bridge server files..."
scp "$HUTIA:C:/behique/bridge_server.js" "$BACKUP_DIR/" 2>/dev/null
scp "$HUTIA:C:/behique/.bridge_token" "$BACKUP_DIR/" 2>/dev/null
scp "$HUTIA:C:/behique/tasks.json" "$BACKUP_DIR/" 2>/dev/null

# 2. All scripts in behique directory
echo "[2/8] Pulling all scripts from C:\\behique..."
scp "$HUTIA:C:/behique/*.py" "$BACKUP_DIR/" 2>/dev/null
scp "$HUTIA:C:/behique/*.js" "$BACKUP_DIR/" 2>/dev/null
scp "$HUTIA:C:/behique/*.sh" "$BACKUP_DIR/" 2>/dev/null
scp "$HUTIA:C:/behique/*.bat" "$BACKUP_DIR/" 2>/dev/null
scp "$HUTIA:C:/behique/*.ps1" "$BACKUP_DIR/" 2>/dev/null

# 3. SSH keys (if any)
echo "[3/8] Pulling SSH keys..."
mkdir -p "$BACKUP_DIR/ssh-keys"
scp "$HUTIA:C:/Users/kalani/.ssh/*" "$BACKUP_DIR/ssh-keys/" 2>/dev/null

# 4. List of installed programs (for reference)
echo "[4/8] Capturing installed programs list..."
ssh "$HUTIA" "powershell -Command \"Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Format-Table -AutoSize\"" > "$BACKUP_DIR/installed-programs.txt" 2>/dev/null

# 5. Scheduled tasks
echo "[5/8] Capturing scheduled tasks..."
ssh "$HUTIA" "powershell -Command \"Get-ScheduledTask | Where-Object {\$_.State -ne 'Disabled'} | Select-Object TaskName, TaskPath, State | Format-Table -AutoSize\"" > "$BACKUP_DIR/scheduled-tasks.txt" 2>/dev/null

# 6. Running services
echo "[6/8] Capturing running services..."
ssh "$HUTIA" "powershell -Command \"Get-Service | Where-Object {\$_.Status -eq 'Running'} | Select-Object Name, DisplayName | Format-Table -AutoSize\"" > "$BACKUP_DIR/running-services.txt" 2>/dev/null

# 7. Network configuration
echo "[7/8] Capturing network config..."
ssh "$HUTIA" "ipconfig /all" > "$BACKUP_DIR/network-config.txt" 2>/dev/null

# 8. PM2 process list
echo "[8/8] Capturing pm2 processes..."
ssh "$HUTIA" "pm2 list" > "$BACKUP_DIR/pm2-processes.txt" 2>/dev/null

echo ""
echo "=== Backup Complete ==="
echo "Files saved to: $BACKUP_DIR"
echo ""
echo "Review the backup before wiping:"
echo "  ls -la $BACKUP_DIR/"
echo ""
echo "If everything looks good, proceed with Phase 2."
```

### Manual checks before wiping

Do these by hand. SSH into Hutia or sit at the machine:

1. **Check for SDXL Turbo remnants.** Already nuked, but verify no large model files are sitting around eating disk space.
2. **Check if Syncthing was running.** If so, remove Hutia from the Syncthing cluster on Ceiba/Cobo so it doesn't try to sync to a dead machine.
3. **Check for any Ollama models.** If Ollama was installed, those models are large. Not worth backing up since we'll pull fresh ones.
4. **Write down the Windows product key** if this is a licensed copy you want to keep. Run `powershell -Command "(Get-WmiObject -query 'select * from SoftwareLicensingService').OA3xOriginalProductKey"` to extract it.

---

## Phase 2: Fresh Install

### Recommended OS

| Hardware | Recommended OS | Why |
|----------|---------------|-----|
| Modern (8GB+ RAM, SSD) | Ubuntu Server 24.04 LTS | Current LTS, great Ollama support, huge community |
| Mid-range (4-8GB RAM) | Ubuntu Server 22.04 LTS | Lighter, still fully supported until 2027 |
| Old/weak (2-4GB RAM) | Debian 12 Minimal | Smallest footprint, runs on anything |
| Ancient (<2GB RAM) | Debian 12 Minimal (no desktop) | Last resort. Script runner only. |

For Hutia specifically: **Ubuntu Server 24.04 LTS.** No desktop environment. Headless only.

### Step-by-step install

**1. Create bootable USB**

On Ceiba (Mac):
```bash
# Download Ubuntu Server 24.04 LTS ISO
# https://ubuntu.com/download/server

# Find the USB drive
diskutil list

# Unmount the USB (replace diskN with your USB disk number)
diskutil unmountDisk /dev/diskN

# Write the ISO (replace diskN - this erases the USB)
sudo dd if=~/Downloads/ubuntu-24.04-live-server-amd64.iso of=/dev/rdiskN bs=4m status=progress

# Eject when done
diskutil eject /dev/diskN
```

**2. Boot and install**

Plug USB into Hutia, boot from USB (usually F12 or DEL at BIOS).

During install:
- Language: English
- Keyboard: US (or your preference)
- Installation type: **Ubuntu Server (minimized)** if offered. Otherwise standard server.
- Network: Configure the ethernet adapter. Set static IP now or do it after.
- Storage: **Use entire disk.** No LVM needed for this use case. Keep it simple.
- Username: `kalani`
- Server name: `hutia`
- Install OpenSSH server: **YES** (critical, check this box)
- Featured server snaps: skip all. We install everything manually.

Wait for install to complete, remove USB, reboot.

**3. Post-install: Static IP**

After first boot, log in at the console and set the static IP:

```bash
# Find your network interface name
ip a
# Look for the one with an IP (probably enp0s3, eth0, eno1, etc.)
# Note the interface name for the next step

# Edit netplan config
sudo nano /etc/netplan/00-installer-config.yaml
```

Replace contents with:
```yaml
network:
  version: 2
  ethernets:
    enp0s3:  # Replace with your actual interface name
      dhcp4: no
      addresses:
        - 192.168.0.152/24
      routes:
        - to: default
          via: 192.168.0.1  # Your router IP
      nameservers:
        addresses:
          - 8.8.8.8
          - 1.1.1.1
```

Apply:
```bash
sudo netplan apply
```

Verify:
```bash
ip a  # Should show 192.168.0.152
ping 192.168.0.1  # Should reach router
ping 8.8.8.8  # Should reach internet
```

**4. SSH from Ceiba**

From Ceiba, test SSH:
```bash
ssh kalani@192.168.0.152
```

If it works, you never need to touch Hutia's keyboard again. Everything from here is remote.

---

## Phase 3: Base Setup (Following the AI Employee Guide)

All commands below run on Hutia via SSH from Ceiba.

### Step 1: Update system

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git htop tmux ufw
```

### Step 2: Install Python 3 + pip

```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version  # Should be 3.10+ on Ubuntu 22.04, 3.12+ on 24.04
```

### Step 3: Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify:
```bash
ollama --version
sudo systemctl status ollama  # Should be active and running
```

### Step 4: Pull a model

Check available RAM first:
```bash
free -h
```

Then pull the right model:
```bash
# If 4-6GB RAM:
ollama pull tinyllama

# If 6-8GB RAM:
ollama pull phi3:mini

# If 8-16GB RAM (Hutia likely falls here):
ollama pull llama3.2

# If 16GB+ RAM:
ollama pull mistral
```

Test it:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Say hello in one sentence.",
  "stream": false
}'
```

### Step 5: Install Node.js (for bridge server)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version  # Should be 20.x
npm --version
```

### Step 6: Set up the bridge/dispatch server

```bash
# Create the behique directory
sudo mkdir -p /opt/behique
sudo chown kalani:kalani /opt/behique
mkdir -p /opt/behique/logs
```

Create the bridge server. This is a Linux version of what was running on Windows:

```bash
cat << 'BRIDGEOF' > /opt/behique/bridge_server.js
const http = require("http");
const fs = require("fs");
const { execFile } = require("child_process");
const os = require("os");

const PORT = 9877;
const TOKEN_FILE = "/opt/behique/.bridge_token";
const TASKS_FILE = "/opt/behique/tasks.json";
const COBO_HOST = "192.168.0.151";
const COBO_PORT = 9876;

// Generate token if it doesn't exist
if (!fs.existsSync(TOKEN_FILE)) {
  const crypto = require("crypto");
  const token = crypto.randomBytes(32).toString("hex");
  fs.writeFileSync(TOKEN_FILE, token);
  console.log(`Generated new bridge token: ${token}`);
}

const TOKEN = fs.readFileSync(TOKEN_FILE, "utf8").trim();

// Task queue
let tasks = [];
try { tasks = JSON.parse(fs.readFileSync(TASKS_FILE, "utf8")); } catch {}
function saveTasks() { fs.writeFileSync(TASKS_FILE, JSON.stringify(tasks, null, 2)); }

function genId() { return `task-${Date.now()}-${Math.random().toString(36).slice(2,6)}`; }

function auth(req) {
  const h = req.headers.authorization || "";
  return h === `Bearer ${TOKEN}`;
}

function readBody(req) {
  return new Promise((resolve) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString())); }
      catch { resolve(null); }
    });
  });
}

function forwardToCobo(taskDesc) {
  return new Promise((resolve) => {
    const payload = JSON.stringify({ description: taskDesc });
    const req = http.request({
      hostname: COBO_HOST, port: COBO_PORT, path: "/task", method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload) },
      timeout: 10000,
    }, (res) => {
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => resolve({ ok: true, data: Buffer.concat(chunks).toString() }));
    });
    req.on("error", () => resolve({ ok: false }));
    req.on("timeout", () => { req.destroy(); resolve({ ok: false }); });
    req.write(payload);
    req.end();
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  res.setHeader("Content-Type", "application/json");

  // Health check (no auth)
  if (req.method === "GET" && url.pathname === "/") {
    return res.end(JSON.stringify({
      ok: true, name: "Hutia", role: "worker",
      platform: "linux", uptime: process.uptime()
    }));
  }
  if (req.method === "HEAD" && url.pathname === "/") {
    return res.end();
  }

  // Auth required for everything else
  if (!auth(req)) {
    res.statusCode = 401;
    return res.end(JSON.stringify({ error: "unauthorized" }));
  }

  // GET /tasks
  if (req.method === "GET" && url.pathname === "/tasks") {
    return res.end(JSON.stringify({ tasks }));
  }

  // POST /task
  if (req.method === "POST" && url.pathname === "/task") {
    const body = await readBody(req);
    if (!body || !body.description) {
      res.statusCode = 400;
      return res.end(JSON.stringify({ error: "description required" }));
    }

    const task = {
      id: genId(),
      description: body.description,
      command: body.command || null,
      args: body.args || [],
      status: "pending",
      result: null,
      createdAt: new Date().toISOString(),
      completedAt: null,
      source: body.source || "remote",
    };

    if (task.command) {
      task.status = "running";
      tasks.push(task);
      saveTasks();

      execFile(task.command, task.args, { cwd: "/opt/behique", timeout: 300000 }, (err, stdout, stderr) => {
        task.status = err ? "failed" : "done";
        task.result = err ? (stderr || err.message) : stdout.trim();
        task.completedAt = new Date().toISOString();
        saveTasks();
      });

      return res.end(JSON.stringify({ ok: true, task }));
    }

    if (body.forward_to === "cobo") {
      const fwd = await forwardToCobo(body.description);
      task.status = fwd.ok ? "forwarded_to_cobo" : "pending";
      task.result = fwd.ok ? fwd.data : "Could not reach Cobo";
    } else {
      task.status = "pending";
    }

    tasks.push(task);
    saveTasks();
    return res.end(JSON.stringify({ ok: true, task }));
  }

  // GET /status
  if (req.method === "GET" && url.pathname === "/status") {
    return res.end(JSON.stringify({
      ok: true,
      name: "Hutia",
      hostname: os.hostname(),
      platform: os.platform(),
      cpus: os.cpus().length,
      memory: { total: os.totalmem(), free: os.freemem() },
      uptime: os.uptime(),
      tasks: {
        total: tasks.length,
        pending: tasks.filter(t => t.status === "pending").length,
        done: tasks.filter(t => t.status === "done").length
      },
    }));
  }

  // POST /ollama - proxy to local Ollama
  if (req.method === "POST" && url.pathname === "/ollama") {
    const body = await readBody(req);
    const payload = JSON.stringify(body);
    const ollamaReq = http.request({
      hostname: "127.0.0.1", port: 11434, path: "/api/generate", method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload) },
      timeout: 120000,
    }, (ollamaRes) => {
      const chunks = [];
      ollamaRes.on("data", (c) => chunks.push(c));
      ollamaRes.on("end", () => res.end(Buffer.concat(chunks).toString()));
    });
    ollamaReq.on("error", (e) => {
      res.statusCode = 502;
      res.end(JSON.stringify({ error: "ollama unreachable", detail: e.message }));
    });
    ollamaReq.write(payload);
    ollamaReq.end();
    return;
  }

  // POST /forward-to-cobo
  if (req.method === "POST" && url.pathname === "/forward-to-cobo") {
    const body = await readBody(req);
    if (!body || !body.description) {
      res.statusCode = 400;
      return res.end(JSON.stringify({ error: "description required" }));
    }
    const result = await forwardToCobo(body.description);
    return res.end(JSON.stringify(result));
  }

  res.statusCode = 404;
  res.end(JSON.stringify({ error: "not_found" }));
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`[Hutia] Bridge server running on http://0.0.0.0:${PORT}`);
  console.log(`[Hutia] Can forward tasks to Cobo at ${COBO_HOST}:${COBO_PORT}`);
  console.log(`[Hutia] Ollama proxy available at /ollama`);
});
BRIDGEOF
```

### Step 7: Configure SSH keys from Ceiba

On Ceiba (not Hutia):
```bash
# Copy your SSH key to the new Hutia
ssh-copy-id kalani@192.168.0.152

# Test passwordless login
ssh kalani@192.168.0.152 "echo 'SSH key auth works'"
```

### Step 8: Set up systemd services (auto-start on boot)

```bash
# Create systemd service for the bridge
sudo tee /etc/systemd/system/hutia-bridge.service << 'EOF'
[Unit]
Description=Hutia Bridge Server
After=network.target ollama.service

[Service]
Type=simple
User=kalani
WorkingDirectory=/opt/behique
ExecStart=/usr/bin/node /opt/behique/bridge_server.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production
StandardOutput=append:/opt/behique/logs/bridge.log
StandardError=append:/opt/behique/logs/bridge-error.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable hutia-bridge
sudo systemctl start hutia-bridge

# Verify
sudo systemctl status hutia-bridge
```

### Step 9: Configure firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (critical, do this first)
sudo ufw allow 22/tcp

# Bridge server
sudo ufw allow 9877/tcp

# Ollama (only from local network)
sudo ufw allow from 192.168.0.0/24 to any port 11434

# Enable firewall
sudo ufw enable

# Verify
sudo ufw status
```

### Step 10: Quality of life

```bash
# Set timezone
sudo timedatectl set-timezone America/Puerto_Rico

# Enable automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Set hostname if not already set
sudo hostnamectl set-hostname hutia

# Add fleet hosts for easy reference
sudo tee -a /etc/hosts << 'EOF'
192.168.0.145  ceiba
192.168.0.151  cobo
192.168.0.152  hutia
EOF
```

---

## Phase 4: Old Laptop Considerations

For grandpa's old laptops (specs unknown yet). Run this when you get access to figure out what you're working with.

### Discovery script (run on the laptop after basic OS install)

```bash
echo "=== MACHINE SPECS ==="
echo "CPU:"
lscpu | grep -E "Model name|CPU\(s\)|Thread"
echo ""
echo "RAM:"
free -h | grep Mem
echo ""
echo "Disk:"
df -h / | tail -1
echo ""
echo "GPU:"
lspci | grep -iE "vga|3d|display"
echo ""
echo "Architecture:"
uname -m
```

### Decision matrix

| RAM | CPU | What it can be | Install |
|-----|-----|----------------|---------|
| <2GB | Any | **Not worth it.** Donate or recycle. | N/A |
| 2-4GB | Single/dual core | **Script runner.** No AI model. Runs cron jobs, file serving, simple Python scripts. | Debian 12 Minimal |
| 4-6GB | Dual core+ | **Tiny AI node.** Can run tinyllama (1.1B). Slow but functional for basic classification, tagging, summarization. | Ubuntu Server 22.04 |
| 6-8GB | Quad core+ | **Light AI node.** Can run phi3:mini (3.8B). Decent reasoning, good for structured tasks. | Ubuntu Server 24.04 |
| 8-16GB | Quad core+ | **Full worker node.** Can run llama3.2 (3B) or even mistral (7B, slow). Real capability. | Ubuntu Server 24.04 |

### Model recommendations by RAM

| RAM | Model | Parameters | Speed (est.) | Good For |
|-----|-------|------------|-------------|----------|
| 2-4GB | None | N/A | N/A | Script runner, file server, cron jobs, web scraping |
| 4-6GB | tinyllama:1.1b | 1.1B | ~5 tok/s | Basic chat, text classification, simple extraction |
| 6-8GB | phi3:mini | 3.8B | ~3 tok/s | Better reasoning, code tasks, structured output |
| 8-12GB | llama3.2:3b | 3.2B | ~5-10 tok/s | General purpose, customer service, content generation |
| 12-16GB | mistral:7b | 7B | ~3-5 tok/s | Full capability, complex reasoning, slow but strong |
| 16GB+ | llama3.1:8b | 8B | ~5-8 tok/s | Best local option, near-GPT-3.5 quality |

### GPU check

If the old laptop has a dedicated GPU (even an old Nvidia):
```bash
# Check for Nvidia GPU
lspci | grep -i nvidia

# If found, check if Ollama picked it up
ollama ps  # After pulling a model, run a query and check this
```

Even an old GTX 750 Ti (2GB VRAM) can accelerate tinyllama inference significantly. Ollama auto-detects compatible GPUs.

### If the laptop is 32-bit or ARM

```bash
uname -m
# x86_64 = good, standard install
# i686 = 32-bit, Ollama won't work. Script runner only.
# armv7l = 32-bit ARM, same deal.
# aarch64 = 64-bit ARM, Ollama supports this.
```

### Minimum viable setup for a script runner (no AI)

If the machine is too weak for Ollama, it's still useful:
```bash
# Install just Python + Node + the bridge
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nodejs npm curl git

# Set up the bridge server (same as Phase 3, Step 6)
# This machine receives tasks from Ceiba and executes Python/bash scripts

# Example use cases:
# - Web scraping with Playwright
# - File processing (PDF conversion, image resize)
# - Cron jobs (scheduled data pulls)
# - Network monitoring
# - Backup server
```

---

## Phase 5: Network Integration

### Register the new machine in the fleet

On Ceiba, update your fleet config. Create or edit `~/behique/fleet.json`:

```json
{
  "machines": [
    {
      "name": "ceiba",
      "ip": "192.168.0.145",
      "role": "hq",
      "bridge_port": null,
      "ollama_port": 11434,
      "models": ["qwen2.5:7b"],
      "status": "active"
    },
    {
      "name": "cobo",
      "ip": "192.168.0.151",
      "role": "worker",
      "bridge_port": 9876,
      "ollama_port": 11434,
      "models": ["llama3.2"],
      "status": "active"
    },
    {
      "name": "hutia",
      "ip": "192.168.0.152",
      "role": "worker",
      "bridge_port": 9877,
      "ollama_port": 11434,
      "models": ["llama3.2"],
      "status": "active"
    }
  ]
}
```

Add new laptops to this file as you bring them online.

### Health monitor script

Save as `~/behique/tools/fleet-health.sh`:

```bash
#!/bin/bash
# fleet-health.sh - Check all machines in the fleet
# Run manually or via cron every 60 seconds

MACHINES=("ceiba:192.168.0.145:11434" "cobo:192.168.0.151:9876" "hutia:192.168.0.152:9877")

echo "=== Fleet Health Check - $(date) ==="
echo ""

for entry in "${MACHINES[@]}"; do
    IFS=':' read -r name ip port <<< "$entry"

    # Ping check
    if ping -c 1 -W 2 "$ip" > /dev/null 2>&1; then
        ping_status="UP"
    else
        ping_status="DOWN"
        echo "[$name] $ip - OFFLINE"
        continue
    fi

    # Bridge/service check
    if curl -s --max-time 3 "http://$ip:$port/" > /dev/null 2>&1; then
        service_status="RUNNING"
    else
        service_status="NO RESPONSE on port $port"
    fi

    # Ollama check
    if curl -s --max-time 3 "http://$ip:11434/api/tags" > /dev/null 2>&1; then
        ollama_status="RUNNING"
        models=$(curl -s --max-time 3 "http://$ip:11434/api/tags" | python3 -c "import sys,json; d=json.load(sys.stdin); print(','.join(m['name'] for m in d.get('models',[])))" 2>/dev/null)
    else
        ollama_status="OFF"
        models="none"
    fi

    echo "[$name] $ip - Ping: $ping_status | Service: $service_status | Ollama: $ollama_status | Models: $models"
done

echo ""
echo "=== Done ==="
```

Make it executable and add to cron:
```bash
chmod +x ~/behique/tools/fleet-health.sh

# Run every 5 minutes, log to file
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/behique/tools/fleet-health.sh >> ~/behique/logs/fleet-health.log 2>&1") | crontab -
```

### Task routing (send work to whichever machine is free)

Simple approach. On Ceiba, create `~/behique/tools/dispatch.sh`:

```bash
#!/bin/bash
# dispatch.sh - Send a task to the first available worker
# Usage: ./dispatch.sh "task description" ["command"] ["args"]

DESCRIPTION="$1"
COMMAND="${2:-}"
ARGS="${3:-}"

if [ -z "$DESCRIPTION" ]; then
    echo "Usage: ./dispatch.sh \"task description\" [command] [args]"
    exit 1
fi

# Workers in priority order (add new machines here)
WORKERS=(
    "hutia:192.168.0.152:9877"
    "cobo:192.168.0.151:9876"
)

for entry in "${WORKERS[@]}"; do
    IFS=':' read -r name ip port <<< "$entry"

    # Check if worker is alive
    if curl -s --max-time 2 "http://$ip:$port/" > /dev/null 2>&1; then
        # Read token (stored per-machine)
        TOKEN_FILE="$HOME/behique/.tokens/$name"
        if [ ! -f "$TOKEN_FILE" ]; then
            echo "No token file for $name at $TOKEN_FILE"
            continue
        fi
        TOKEN=$(cat "$TOKEN_FILE")

        # Build payload
        if [ -n "$COMMAND" ]; then
            PAYLOAD="{\"description\":\"$DESCRIPTION\",\"command\":\"$COMMAND\",\"args\":[$ARGS],\"source\":\"ceiba\"}"
        else
            PAYLOAD="{\"description\":\"$DESCRIPTION\",\"source\":\"ceiba\"}"
        fi

        # Send task
        RESULT=$(curl -s --max-time 10 -X POST "http://$ip:$port/task" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$PAYLOAD")

        echo "Dispatched to $name ($ip): $RESULT"
        exit 0
    fi
done

echo "ERROR: No workers available"
exit 1
```

### Store tokens per machine

```bash
mkdir -p ~/behique/.tokens

# After Hutia rebuild, get the token:
ssh kalani@192.168.0.152 "cat /opt/behique/.bridge_token" > ~/behique/.tokens/hutia

# Cobo token (if not already saved):
# Get it from Cobo and save to:
# ~/behique/.tokens/cobo
```

---

## Phase 6: Verification Checklist

Run through this after every machine rebuild. Every box must be checked.

### Hutia rebuild verification

- [ ] Ubuntu Server installed, boots to login prompt
- [ ] Static IP is 192.168.0.152
- [ ] SSH from Ceiba works: `ssh kalani@192.168.0.152`
- [ ] SSH key auth works (no password prompt)
- [ ] Python 3 installed: `python3 --version`
- [ ] Node.js installed: `node --version`
- [ ] Ollama installed and running: `sudo systemctl status ollama`
- [ ] Model pulled and responds: `curl http://localhost:11434/api/generate -d '{"model":"llama3.2","prompt":"hello","stream":false}'`
- [ ] Bridge server running: `sudo systemctl status hutia-bridge`
- [ ] Bridge responds to health check: `curl http://192.168.0.152:9877/`
- [ ] Bridge accepts authenticated tasks from Ceiba
- [ ] Firewall is active: `sudo ufw status`
- [ ] Services auto-start after reboot: `sudo reboot` then check everything
- [ ] Fleet health script sees Hutia as UP
- [ ] Dispatch script can route a task to Hutia

### Old laptop verification (same list, adjusted)

- [ ] OS installed, boots to login
- [ ] Static IP assigned (pick next available: 192.168.0.153, .154, etc.)
- [ ] SSH from Ceiba works
- [ ] SSH key auth works
- [ ] Python 3 installed
- [ ] If RAM >= 4GB: Ollama installed and model responds
- [ ] If RAM < 4GB: Bridge server runs and accepts script tasks
- [ ] Bridge server running (systemd)
- [ ] Services survive reboot
- [ ] Added to fleet.json
- [ ] Fleet health script sees it
- [ ] Dispatch script can reach it

---

## Phase 7: The Sales Angle

This is the entire point of doing this exercise. The AI Employee Guide is a $19.99 product. Dogfooding it on Hutia and grandpa's laptops proves it works.

### What you capture during the process

1. **Screenshots.** Every step. Terminal output. System stats. The Ollama response on old hardware. Save these to `~/behique/Ceiba/projects/content-empire/marketing/hutia-rebuild/`.

2. **Timing.** How long did the full rebuild take? "I wiped a machine and had a working AI node in 47 minutes" is a real selling point.

3. **The old laptop story.** If you get a 2015 laptop running tinyllama and answering questions, that is gold. "I built an AI employee on my grandpa's laptop from 2015. Total cost: $0."

4. **Before/after.** Screenshot the old Windows Hutia (cluttered, scripts everywhere, SDXL remnants). Then screenshot the clean Ubuntu system with Ollama running.

### Content that comes from this

| Format | Angle | Platform |
|--------|-------|----------|
| Instagram post | "I wiped my server and rebuilt it in under an hour" | @behikeai |
| Reel | Time-lapse of terminal commands running during setup | Instagram/TikTok |
| Thread | Step-by-step walkthrough with screenshots | X/Twitter |
| Case study update | Add "tested on old hardware" section to existing case study | Gumroad product page |
| Product update | Add "minimum hardware" section to AI Employee Guide | Guide itself |

### The pitch

The guide already says "you can build this on hardware you own." This rebuild process PROVES it. The old laptop is the clincher. If it runs on a machine someone was about to throw away, the value proposition writes itself.

"Your old laptop is not trash. It's an employee that works 24/7 for free."

That is the headline.

---

## Quick Reference: All Commands in Order

For copy-paste speed. This is the entire Hutia rebuild compressed.

```bash
# === ON CEIBA (before wipe) ===
bash ~/behique/tools/hutia-backup.sh

# === AFTER FRESH UBUNTU INSTALL, SSH INTO HUTIA ===
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git htop tmux ufw python3 python3-pip python3-venv
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo mkdir -p /opt/behique && sudo chown kalani:kalani /opt/behique
mkdir -p /opt/behique/logs
# (paste bridge_server.js from Phase 3 Step 6)
# (create systemd service from Phase 3 Step 8)
sudo systemctl daemon-reload && sudo systemctl enable hutia-bridge && sudo systemctl start hutia-bridge
sudo ufw default deny incoming && sudo ufw default allow outgoing
sudo ufw allow 22/tcp && sudo ufw allow 9877/tcp && sudo ufw allow from 192.168.0.0/24 to any port 11434
sudo ufw enable
sudo timedatectl set-timezone America/Puerto_Rico

# === ON CEIBA (after Hutia is up) ===
ssh-copy-id kalani@192.168.0.152
ssh kalani@192.168.0.152 "cat /opt/behique/.bridge_token" > ~/behique/.tokens/hutia
curl http://192.168.0.152:9877/
bash ~/behique/tools/fleet-health.sh
```

---

*This document is the test case. If following these instructions produces a working node, the AI Employee Guide is validated. If something fails, fix the guide. The guide and this plan should converge into the same truth.*
