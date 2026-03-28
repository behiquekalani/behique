#!/usr/bin/env python3
"""
Transcription SaaS - FastAPI backend for video-to-text transcription.

Uses yt-dlp to download video/audio from any supported URL,
then transcribes via OpenAI Whisper (local model).

Run: python app.py
"""

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/hour")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Preload Whisper model at startup so first request isn't slow
_whisper_model = None

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Behike Transcribe", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TranscribeRequest(BaseModel):
    url: str
    language: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper

        print(f"[whisper] Loading model '{WHISPER_MODEL}'...")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        print("[whisper] Model ready.")
    return _whisper_model


def validate_url(url: str) -> bool:
    """Basic URL validation."""
    return bool(re.match(r"https?://\S+", url.strip()))


def download_media(url: str, tmp_dir: str) -> tuple[str, str]:
    """Download video/audio via yt-dlp. Returns (filepath, title)."""
    output_template = os.path.join(tmp_dir, "%(title).100s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f", "bestaudio/best",
        "-o", output_template,
        "--print", "after_move:filepath",
        "--print", "%(title)s",
        "--no-warnings",
        "--socket-timeout", "30",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "Unsupported URL" in stderr:
            raise ValueError(f"Unsupported URL: {url}")
        if "Video unavailable" in stderr or "Private video" in stderr:
            raise ValueError("Video is unavailable or private.")
        raise RuntimeError(f"Download failed: {stderr[:200]}")

    lines = result.stdout.strip().split("\n")
    if len(lines) >= 2:
        title = lines[0].strip()
        filepath = lines[1].strip()
    elif len(lines) == 1:
        filepath = lines[0].strip()
        title = Path(filepath).stem
    else:
        raise RuntimeError("Download produced no output.")

    if not os.path.isfile(filepath):
        for f in os.listdir(tmp_dir):
            full = os.path.join(tmp_dir, f)
            if os.path.isfile(full):
                filepath = full
                break
        else:
            raise RuntimeError("Downloaded file not found on disk.")

    return filepath, title


def extract_audio(input_path: str, tmp_dir: str) -> str:
    """Convert media to 16kHz mono WAV for Whisper."""
    wav_path = os.path.join(tmp_dir, "audio.wav")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        wav_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError("Audio extraction failed.")
    return wav_path


def get_audio_duration(wav_path: str) -> float:
    """Get duration of audio file in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        wav_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return round(float(result.stdout.strip()), 1)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/")
async def serve_frontend():
    """Serve the HTML frontend."""
    html_path = Path(__file__).parent / "index.html"
    return FileResponse(html_path, media_type="text/html")


@app.get("/health")
async def health():
    return {"status": "ok", "model": WHISPER_MODEL}


@app.post("/transcribe")
@limiter.limit(RATE_LIMIT)
async def transcribe(request: Request, body: TranscribeRequest):
    url = body.url.strip()

    # Validate
    if not url:
        return JSONResponse(
            status_code=400,
            content={"error": "URL is required."},
        )
    if not validate_url(url):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid URL. Must start with http:// or https://"},
        )

    tmp_dir = tempfile.mkdtemp(prefix="transcribe_saas_")

    try:
        # Download
        media_path, title = download_media(url, tmp_dir)

        # Extract audio
        wav_path = extract_audio(media_path, tmp_dir)
        duration = get_audio_duration(wav_path)

        # Transcribe
        model = get_whisper_model()
        options = {}
        if body.language:
            options["language"] = body.language

        t0 = time.time()
        result = model.transcribe(wav_path, **options)
        elapsed = round(time.time() - t0, 1)

        text = result.get("text", "").strip()
        language = result.get("language", "unknown")

        # Build segments
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip(),
            })

        return {
            "text": text,
            "title": title,
            "language": language,
            "duration_seconds": duration,
            "processing_time_seconds": elapsed,
            "segments": segments,
        }

    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except subprocess.TimeoutExpired:
        return JSONResponse(
            status_code=408,
            content={"error": "Request timed out. The video may be too long."},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Transcription failed: {str(e)[:200]}"},
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    """Preload Whisper model on startup."""
    get_whisper_model()


if __name__ == "__main__":
    import uvicorn

    print(f"[server] Starting on {HOST}:{PORT}")
    print(f"[server] Whisper model: {WHISPER_MODEL}")
    print(f"[server] Rate limit: {RATE_LIMIT}")
    uvicorn.run(app, host=HOST, port=PORT)
