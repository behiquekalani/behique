# Wan2GP Installer for Cobo (GTX 1080 Ti, 11GB VRAM)
# Paste this entire script into PowerShell on Cobo
# Created: 2026-03-19

Write-Host "=== WAN2GP INSTALLER FOR COBO ===" -ForegroundColor Cyan
Write-Host "GPU: GTX 1080 Ti (11GB VRAM)" -ForegroundColor Yellow
Write-Host ""

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ first." -ForegroundColor Red
    Write-Host "  winget install Python.Python.3.11" -ForegroundColor White
    exit 1
}

# Check Git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "ERROR: Git not found." -ForegroundColor Red
    Write-Host "  winget install Git.Git" -ForegroundColor White
    exit 1
}

# Create directory
$WAN2GP_DIR = "C:\behique\wan2gp"
New-Item -ItemType Directory -Force -Path $WAN2GP_DIR | Out-Null
Set-Location $WAN2GP_DIR

# Clone Wan2GP
Write-Host "[1/5] Cloning Wan2GP..." -ForegroundColor Green
if (Test-Path "$WAN2GP_DIR\.git") {
    Write-Host "  Already cloned, pulling latest..." -ForegroundColor Yellow
    git pull
} else {
    git clone https://github.com/deepbeepmeep/Wan2GP.git .
}

# Create virtual environment
Write-Host "[2/5] Creating virtual environment..." -ForegroundColor Green
python -m venv venv
& "$WAN2GP_DIR\venv\Scripts\Activate.ps1"

# Install PyTorch with CUDA
Write-Host "[3/5] Installing PyTorch + CUDA..." -ForegroundColor Green
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install Wan2GP requirements
Write-Host "[4/5] Installing Wan2GP requirements..." -ForegroundColor Green
pip install -r requirements.txt

# Create optimized config for 11GB VRAM
Write-Host "[5/5] Creating 11GB VRAM config..." -ForegroundColor Green
@"
{
    "model": "wan2.1-t2v-1.3b",
    "memory_profile": 2,
    "vae_tiling": true,
    "teacache": true,
    "sageattn": true,
    "resolution": "480p",
    "video_length": 5,
    "fps": 16,
    "guidance_scale": 5.0,
    "steps": 30,
    "note": "Optimized for GTX 1080 Ti 11GB. Profile 2 = balanced offloading."
}
"@ | Out-File -FilePath "$WAN2GP_DIR\cobo_config.json" -Encoding utf8

# Create the API server script that Ceiba can call
@"
#!/usr/bin/env python3
"""
Wan2GP API Server for Cobo
Receives video generation requests from Ceiba over HTTP.
Runs on port 9878.
"""
import http.server
import json
import subprocess
import threading
import os
import sys
import time
from pathlib import Path

PORT = 9878
WAN2GP_DIR = Path(r"C:\behique\wan2gp")
OUTPUT_DIR = Path(r"C:\behique\video_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Track active jobs
jobs = {}

def generate_video(job_id, prompt, duration=5, resolution="480p"):
    """Run Wan2GP to generate a video clip."""
    output_path = OUTPUT_DIR / f"{job_id}.mp4"
    jobs[job_id]["status"] = "generating"
    jobs[job_id]["started_at"] = time.time()

    try:
        cmd = [
            sys.executable, str(WAN2GP_DIR / "generate.py"),
            "--prompt", prompt,
            "--output", str(output_path),
            "--length", str(duration),
            "--resolution", resolution,
            "--steps", "30",
            "--guidance", "5.0",
            "--memory_profile", "2",
            "--vae_tiling",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)

        if output_path.exists():
            jobs[job_id]["status"] = "done"
            jobs[job_id]["output"] = str(output_path)
            jobs[job_id]["size_mb"] = output_path.stat().st_size / (1024*1024)
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = result.stderr[-500:] if result.stderr else "No output file"
    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = "Timeout (20 min)"
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

    jobs[job_id]["completed_at"] = time.time()

class VideoHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": True, "name": "Cobo-VideoGen",
                "gpu": "GTX 1080 Ti 11GB", "model": "Wan2.1-1.3B",
                "active_jobs": len([j for j in jobs.values() if j["status"] == "generating"]),
            }).encode())
            return

        if self.path.startswith("/status/"):
            job_id = self.path.split("/status/")[1]
            if job_id in jobs:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(jobs[job_id]).encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error":"job not found"}')
            return

        if self.path.startswith("/download/"):
            job_id = self.path.split("/download/")[1]
            if job_id in jobs and jobs[job_id].get("output"):
                fpath = Path(jobs[job_id]["output"])
                if fpath.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Content-Length", str(fpath.stat().st_size))
                    self.end_headers()
                    with open(fpath, "rb") as f:
                        self.wfile.write(f.read())
                    return
            self.send_response(404)
            self.end_headers()
            return

        if self.path == "/jobs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"jobs": jobs}).encode())
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            prompt = body.get("prompt", "")
            duration = body.get("duration", 5)
            resolution = body.get("resolution", "480p")

            if not prompt:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"prompt required"}')
                return

            job_id = f"vid-{int(time.time())}-{os.urandom(3).hex()}"
            jobs[job_id] = {
                "id": job_id, "prompt": prompt, "status": "queued",
                "duration": duration, "resolution": resolution,
                "created_at": time.time(),
            }

            thread = threading.Thread(target=generate_video, args=(job_id, prompt, duration, resolution))
            thread.start()

            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "job_id": job_id}).encode())
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[VideoGen] {args[0]}")

if __name__ == "__main__":
    print(f"[Cobo VideoGen] Starting on port {PORT}")
    print(f"[Cobo VideoGen] GPU: GTX 1080 Ti 11GB")
    print(f"[Cobo VideoGen] Model: Wan2.1 T2V 1.3B")
    print(f"[Cobo VideoGen] Output: {OUTPUT_DIR}")
    server = http.server.HTTPServer(("0.0.0.0", PORT), VideoHandler)
    server.serve_forever()
"@ | Out-File -FilePath "$WAN2GP_DIR\video_server.py" -Encoding utf8

# Create start script
@"
@echo off
echo Starting Wan2GP Video Server on port 9878...
cd /d C:\behique\wan2gp
call venv\Scripts\activate.bat
python video_server.py
"@ | Out-File -FilePath "$WAN2GP_DIR\start_video_server.bat" -Encoding ascii

Write-Host ""
Write-Host "=== INSTALLATION COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "To start the video server:" -ForegroundColor Cyan
Write-Host "  C:\behique\wan2gp\start_video_server.bat" -ForegroundColor White
Write-Host ""
Write-Host "Or with pm2:" -ForegroundColor Cyan
Write-Host "  pm2 start video_server.py --name cobo-videogen --interpreter python" -ForegroundColor White
Write-Host ""
Write-Host "Test it:" -ForegroundColor Cyan
Write-Host '  curl http://localhost:9878/' -ForegroundColor White
Write-Host ""
Write-Host "Ceiba will send requests to http://192.168.0.151:9878/generate" -ForegroundColor Yellow
