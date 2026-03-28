#!/usr/bin/env python3
"""
Wan2GP CLI-Mode Video Server for Cobo
Routes video generation requests via Wan2GP CLI (--process flag).
Port 9878.

DEPLOY: Copy to C:\\behique\\wan2gp\\video_server.py and restart:
  pm2 restart cobo-videogen
"""
import http.server
import json
import threading
import os
import sys
import time
import subprocess
import shutil
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PORT = 9878
WAN2GP_DIR = Path(r"C:\behique\wan2gp")
OUTPUT_DIR = Path(r"C:\behique\video_output")
OUTPUT_DIR.mkdir(exist_ok=True)

jobs = {}


def generate_video(job_id, prompt, duration=3, resolution="480p"):
    """Generate video via Wan2GP CLI mode."""
    jobs[job_id]["status"] = "generating"
    jobs[job_id]["started_at"] = time.time()

    try:
        # Create queue JSON for Wan2GP
        queue_file = WAN2GP_DIR / f"queue_{job_id}.json"
        job_output_dir = OUTPUT_DIR / job_id
        job_output_dir.mkdir(exist_ok=True)

        h = 480 if resolution == "480p" else 720
        w = 832 if resolution == "480p" else 1280

        queue_data = {
            "prompt": prompt,
            "negative_prompt": "",
            "height": h,
            "width": w,
            "steps": 30,
            "cfg_scale": 5.0,
            "seed": -1,
            "num_frames": duration * 8,  # ~8 fps for Wan2.1
        }

        with open(queue_file, 'w') as f:
            json.dump(queue_data, f)

        # Try CLI mode first
        result = subprocess.run(
            [sys.executable, "wgp.py",
             "--process", str(queue_file),
             "--output-dir", str(job_output_dir)],
            cwd=str(WAN2GP_DIR),
            capture_output=True, text=True,
            timeout=600,  # 10 min max
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
        )

        # Check for output video
        mp4_files = list(job_output_dir.glob("*.mp4"))
        if not mp4_files:
            # Also check WAN2GP's default output
            for pattern in ["output/*.mp4", "outputs/*.mp4", "*.mp4"]:
                found = list(WAN2GP_DIR.glob(pattern))
                if found:
                    # Get newest file
                    newest = max(found, key=lambda f: f.stat().st_mtime)
                    if newest.stat().st_mtime > jobs[job_id]["started_at"]:
                        mp4_files = [newest]
                        break

        if mp4_files:
            output_path = OUTPUT_DIR / f"{job_id}.mp4"
            shutil.copy2(str(mp4_files[0]), str(output_path))
            jobs[job_id]["status"] = "done"
            jobs[job_id]["output"] = str(output_path)
            jobs[job_id]["size_mb"] = output_path.stat().st_size / (1024 * 1024)
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "No output video found"
            if result.stderr:
                jobs[job_id]["error"] += f": {result.stderr[-200:]}"

        # Cleanup queue file
        queue_file.unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = "Generation timed out (10 min)"
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e).encode('ascii', errors='replace').decode('ascii')

    jobs[job_id]["completed_at"] = time.time()


class VideoHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._json(200, {
                "ok": True, "name": "Cobo-VideoGen-CLI",
                "gpu": "GTX 1080 8GB", "model": "Wan2.1-1.3B",
                "mode": "cli",
                "active_jobs": len([j for j in jobs.values() if j["status"] == "generating"]),
                "total_jobs": len(jobs),
            })
        elif self.path.startswith("/status/"):
            jid = self.path.split("/status/")[1]
            if jid in jobs:
                self._json(200, jobs[jid])
            else:
                self._json(404, {"error": "job not found"})
        elif self.path.startswith("/download/"):
            jid = self.path.split("/download/")[1]
            if jid in jobs and jobs[jid].get("output"):
                fpath = Path(jobs[jid]["output"])
                if fpath.exists():
                    self.send_response(200)
                    self.send_header("Content-Type", "video/mp4")
                    self.send_header("Content-Length", str(fpath.stat().st_size))
                    self.end_headers()
                    with open(fpath, "rb") as f:
                        self.wfile.write(f.read())
                    return
            self._json(404, {"error": "not ready"})
        elif self.path == "/jobs":
            self._json(200, {"jobs": jobs})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            prompt = body.get("prompt", "")
            duration = body.get("duration", 3)
            resolution = body.get("resolution", "480p")

            if not prompt:
                self._json(400, {"error": "prompt required"})
                return

            jid = f"vid-{int(time.time())}-{os.urandom(3).hex()}"
            jobs[jid] = {
                "id": jid, "prompt": prompt, "status": "queued",
                "duration": duration, "resolution": resolution,
                "created_at": time.time(),
            }

            thread = threading.Thread(target=generate_video, args=(jid, prompt, duration, resolution))
            thread.start()

            self._json(202, {"ok": True, "job_id": jid})
        else:
            self._json(404, {"error": "not found"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=True).encode('utf-8'))

    def log_message(self, fmt, *args):
        print(f"[VideoGen] {args[0]}")


if __name__ == "__main__":
    print(f"[Cobo VideoGen CLI] Port {PORT}")
    print(f"[Cobo VideoGen CLI] WAN2GP: {WAN2GP_DIR}")
    print(f"[Cobo VideoGen CLI] Output: {OUTPUT_DIR}")
    server = http.server.HTTPServer(("0.0.0.0", PORT), VideoHandler)
    server.serve_forever()
