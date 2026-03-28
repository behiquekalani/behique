# Hutia (Comp3) Setup Guide
# Paste this entire block into PowerShell on Comp3

## Step 1: Install Node.js (if not installed)
# Download from https://nodejs.org/en/download/ or run:
# winget install OpenJS.NodeJS.LTS

## Step 2: Create the behique directory and bridge server
# Open PowerShell as Administrator and paste everything below:

```powershell
# Create directory structure
New-Item -ItemType Directory -Force -Path C:\behique
New-Item -ItemType Directory -Force -Path C:\behique\logs

# Generate auth token
$token = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$token | Out-File -FilePath C:\behique\.bridge_token -NoNewline -Encoding utf8
Write-Host "Bridge token: $token" -ForegroundColor Cyan

# Write the bridge server
@'
const http = require("http");
const fs = require("fs");
const { execFile } = require("child_process");
const path = require("path");

const PORT = 9877;
const TOKEN = fs.readFileSync("C:\\behique\\.bridge_token", "utf8").trim();
const TASKS_FILE = "C:\\behique\\tasks.json";
const COBO_HOST = "192.168.0.151";
const COBO_PORT = 9876;

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

// Forward task to Cobo if we can't handle it locally
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
    return res.end(JSON.stringify({ ok: true, name: "Hutia", role: "worker", uptime: process.uptime() }));
  }
  if (req.method === "HEAD" && url.pathname === "/") {
    return res.end();
  }

  // Auth required for everything else
  if (!auth(req)) {
    res.statusCode = 401;
    return res.end(JSON.stringify({ error: "unauthorized" }));
  }

  // GET /tasks - list all tasks
  if (req.method === "GET" && url.pathname === "/tasks") {
    return res.end(JSON.stringify({ tasks }));
  }

  // POST /task - receive a task
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

    // If command provided, execute it
    if (task.command) {
      task.status = "running";
      tasks.push(task);
      saveTasks();

      execFile(task.command, task.args, { cwd: "C:\\behique", timeout: 300000 }, (err, stdout, stderr) => {
        task.status = err ? "failed" : "done";
        task.result = err ? (stderr || err.message) : stdout.trim();
        task.completedAt = new Date().toISOString();
        saveTasks();
      });

      return res.end(JSON.stringify({ ok: true, task }));
    }

    // No command - check if we should forward to Cobo
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

  // GET /status - machine status for Ceiba dashboard
  if (req.method === "GET" && url.pathname === "/status") {
    const os = require("os");
    return res.end(JSON.stringify({
      ok: true,
      name: "Hutia",
      hostname: os.hostname(),
      platform: os.platform(),
      cpus: os.cpus().length,
      memory: { total: os.totalmem(), free: os.freemem() },
      uptime: os.uptime(),
      tasks: { total: tasks.length, pending: tasks.filter(t => t.status === "pending").length, done: tasks.filter(t => t.status === "done").length },
    }));
  }

  // POST /forward-to-cobo - relay a task to Cobo
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
});
'@ | Out-File -FilePath C:\behique\bridge_server.js -Encoding utf8

# Install pm2 globally
npm install -g pm2

# Start the bridge
cd C:\behique
pm2 start bridge_server.js --name hutia-bridge
pm2 save

# Auto-start on reboot (Windows)
pm2-startup install

Write-Host ""
Write-Host "=== HUTIA SETUP COMPLETE ===" -ForegroundColor Green
Write-Host "Bridge running on port 9877" -ForegroundColor Cyan
Write-Host "Token saved to C:\behique\.bridge_token" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test it:" -ForegroundColor Yellow
Write-Host "  curl http://localhost:9877/" -ForegroundColor White
Write-Host ""
Write-Host "Send this token to Ceiba so it can authenticate:" -ForegroundColor Yellow
Write-Host "  Token: $token" -ForegroundColor White
```
