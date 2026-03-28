#!/usr/bin/env python3
"""
Wan2GP API Server for Cobo — Fixed version
Routes video generation requests to Wan2GP Gradio backend.
Port 9878. Requires Wan2GP Gradio running on port 7860.

DEPLOY: Copy this to C:\behique\wan2gp\video_server.py and restart:
  pm2 restart cobo-videogen
"""
import http.server
import json
import threading
import os
import sys
import time
from pathlib import Path

# Fix Windows Unicode encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

PORT = 9878
GRADIO_URL = "http://127.0.0.1:7860"
OUTPUT_DIR = Path(r"C:\behique\video_output")
OUTPUT_DIR.mkdir(exist_ok=True)

jobs = {}

def check_gradio():
    """Check if Gradio backend is running."""
    try:
        import urllib.request
        req = urllib.request.urlopen(f"{GRADIO_URL}/", timeout=3)
        return req.status == 200
    except Exception:
        return False

def generate_video(job_id, prompt, duration=5, resolution="480p"):
    """Generate video via Gradio Client API."""
    jobs[job_id]["status"] = "generating"
    jobs[job_id]["started_at"] = time.time()

    try:
        from gradio_client import Client
        client = Client(GRADIO_URL, verbose=False)

        # Call the generate endpoint
        # Wan2GP's main generate function - parameters depend on the Gradio interface
        result = client.predict(
            prompt,           # prompt
            "",               # negative prompt
            duration,         # video length in seconds
            480 if resolution == "480p" else 720,  # height
            832 if resolution == "480p" else 1280,  # width
            30,               # steps
            5.0,              # guidance scale
            42,               # seed
            fn_index=0        # first function
        )

        # Result could be a file path or dict
        if isinstance(result, str) and os.path.exists(result):
            output_path = OUTPUT_DIR / f"{job_id}.mp4"
            import shutil
            shutil.copy2(result, str(output_path))
            jobs[job_id]["status"] = "done"
            jobs[job_id]["output"] = str(output_path)
            jobs[job_id]["size_mb"] = output_path.stat().st_size / (1024*1024)
        elif isinstance(result, dict) and result.get("video"):
            output_path = OUTPUT_DIR / f"{job_id}.mp4"
            import shutil
            shutil.copy2(result["video"], str(output_path))
            jobs[job_id]["status"] = "done"
            jobs[job_id]["output"] = str(output_path)
            jobs[job_id]["size_mb"] = output_path.stat().st_size / (1024*1024)
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = f"Unexpected result type: {type(result).__name__}"

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e).encode('ascii', errors='replace').decode('ascii')

    jobs[job_id]["completed_at"] = time.time()


class VideoHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            gradio_up = check_gradio()
            self._json_response(200, {
                "ok": True, "name": "Cobo-VideoGen",
                "gpu": "GTX 1080 Ti 11GB", "model": "Wan2.1-1.3B",
                "gradio_backend": gradio_up,
                "active_jobs": len([j for j in jobs.values() if j["status"] == "generating"]),
            })
            return

        if self.path.startswith("/status/"):
            job_id = self.path.split("/status/")[1]
            if job_id in jobs:
                self._json_response(200, jobs[job_id])
            else:
                self._json_response(404, {"error": "job not found"})
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
            self._json_response(404, {"error": "not ready"})
            return

        if self.path == "/jobs":
            self._json_response(200, {"jobs": jobs})
            return

        self._json_response(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/generate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}

            prompt = body.get("prompt", "")
            duration = body.get("duration", 3)
            resolution = body.get("resolution", "480p")

            if not prompt:
                self._json_response(400, {"error": "prompt required"})
                return

            if not check_gradio():
                self._json_response(503, {"error": "Gradio backend not running. Start wgp.py first."})
                return

            job_id = f"vid-{int(time.time())}-{os.urandom(3).hex()}"
            jobs[job_id] = {
                "id": job_id, "prompt": prompt, "status": "queued",
                "duration": duration, "resolution": resolution,
                "created_at": time.time(),
            }

            thread = threading.Thread(target=generate_video, args=(job_id, prompt, duration, resolution))
            thread.start()

            self._json_response(202, {"ok": True, "job_id": job_id})
            return

        self._json_response(404, {"error": "not found"})

    def _json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=True).encode('utf-8'))

    def log_message(self, fmt, *args):
        print(f"[VideoGen] {args[0]}")


if __name__ == "__main__":
    print(f"[Cobo VideoGen] Starting on port {PORT}")
    print(f"[Cobo VideoGen] Gradio backend: {GRADIO_URL}")
    print(f"[Cobo VideoGen] Output: {OUTPUT_DIR}")
    server = http.server.HTTPServer(("0.0.0.0", PORT), VideoHandler)
    server.serve_forever()
