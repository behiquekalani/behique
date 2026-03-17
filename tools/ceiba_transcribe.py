#!/usr/bin/env python3
"""
ceiba_transcribe.py — Video/audio transcription pipeline for Ceiba.

Transcribes Instagram Reels, TikTok, YouTube Shorts, and local files
using yt-dlp + ffmpeg + OpenAI Whisper (local model).

Requirements (pip install):
    pip install openai-whisper yt-dlp

System requirements:
    - ffmpeg (brew install ffmpeg / apt install ffmpeg)

Usage:
    python ceiba_transcribe.py <URL_or_file> [more URLs/files...]
    python ceiba_transcribe.py https://www.instagram.com/reel/ABC123/
    python ceiba_transcribe.py video.mp4 --model small --lang es
    python ceiba_transcribe.py URL1 URL2 URL3 --summary

Options:
    --output DIR     Output directory (default: ~/behique/Ceiba/07-Transcripts/)
    --model MODEL    Whisper model: tiny, base, small, medium, large (default: base)
    --lang LANG      Force language (e.g. es, en). Omit for auto-detect.
    --summary        Print a short summary header in the transcript
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = Path.home() / "behique" / "Ceiba" / "07-Transcripts"
DEFAULT_MODEL = "base"
SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".mp3", ".wav", ".m4a", ".ogg", ".flac"}


# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------

def check_dependencies():
    """Verify that yt-dlp and ffmpeg are available."""
    missing = []
    if shutil.which("yt-dlp") is None:
        missing.append("yt-dlp  (pip install yt-dlp)")
    if shutil.which("ffmpeg") is None:
        missing.append("ffmpeg  (brew install ffmpeg / apt install ffmpeg)")
    try:
        import whisper  # noqa: F401
    except ImportError:
        missing.append("openai-whisper  (pip install openai-whisper)")
    if missing:
        print("[ERROR] Missing dependencies:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_url(s: str) -> bool:
    return bool(re.match(r"https?://", s))


def sanitize_filename(name: str) -> str:
    """Strip characters that cause issues in filenames."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:120] if name else "untitled"


def download_media(url: str, tmp_dir: str) -> tuple[str, str]:
    """
    Download video/audio from a URL using yt-dlp.
    Returns (path_to_downloaded_file, title).
    """
    print(f"[download] Fetching: {url}")
    output_template = os.path.join(tmp_dir, "%(title).100s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f", "bestaudio/best",
        "-o", output_template,
        "--print", "after_move:filepath",
        "--print", "%(title)s",
        "--no-warnings",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"yt-dlp failed for {url}:\n{stderr}")

    lines = result.stdout.strip().split("\n")
    # yt-dlp --print outputs title first, then filepath (after_move)
    if len(lines) >= 2:
        title = lines[0].strip()
        filepath = lines[1].strip()
    elif len(lines) == 1:
        filepath = lines[0].strip()
        title = Path(filepath).stem
    else:
        raise RuntimeError(f"yt-dlp produced no output for {url}")

    if not os.path.isfile(filepath):
        # Fallback: find any file in tmp_dir
        for f in os.listdir(tmp_dir):
            full = os.path.join(tmp_dir, f)
            if os.path.isfile(full):
                filepath = full
                break
        else:
            raise RuntimeError(f"Downloaded file not found for {url}")

    return filepath, title


def extract_audio(input_path: str, tmp_dir: str) -> str:
    """Convert media to 16kHz mono WAV for Whisper."""
    wav_path = os.path.join(tmp_dir, "audio.wav")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        wav_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr.strip()}")
    return wav_path


def transcribe_audio(wav_path: str, model_name: str, language: str | None) -> dict:
    """Run Whisper on the audio file. Returns the full result dict."""
    import whisper

    print(f"[whisper] Loading model '{model_name}'...")
    model = whisper.load_model(model_name)

    print("[whisper] Transcribing...")
    options = {}
    if language:
        options["language"] = language

    result = model.transcribe(wav_path, **options)
    return result


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS.mmm format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def save_outputs(
    result: dict,
    title: str,
    source: str,
    output_dir: Path,
    include_summary: bool,
) -> tuple[Path, Path]:
    """
    Save transcript as .txt and timestamped .json.
    Returns (txt_path, json_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_title = sanitize_filename(title)
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    base_name = f"{date_prefix}_{safe_title}"

    txt_path = output_dir / f"{base_name}.txt"
    json_path = output_dir / f"{base_name}.json"

    # -- Plain text --
    lines = []
    if include_summary:
        lang = result.get("language", "unknown")
        seg_count = len(result.get("segments", []))
        duration = result["segments"][-1]["end"] if result.get("segments") else 0
        lines.append(f"# Transcription: {title}")
        lines.append(f"# Source: {source}")
        lines.append(f"# Language: {lang} | Segments: {seg_count} | Duration: {format_timestamp(duration)}")
        lines.append(f"# Date: {date_prefix}")
        lines.append("")

    lines.append(result.get("text", "").strip())
    txt_path.write_text("\n".join(lines), encoding="utf-8")

    # -- JSON with timestamps --
    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": round(seg["start"], 3),
            "end": round(seg["end"], 3),
            "start_fmt": format_timestamp(seg["start"]),
            "end_fmt": format_timestamp(seg["end"]),
            "text": seg["text"].strip(),
        })

    json_data = {
        "title": title,
        "source": source,
        "language": result.get("language", "unknown"),
        "date": date_prefix,
        "text": result.get("text", "").strip(),
        "segments": segments,
    }
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return txt_path, json_path


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def process_single(source: str, args) -> bool:
    """Process one URL or local file. Returns True on success."""
    output_dir = Path(args.output)
    tmp_dir = tempfile.mkdtemp(prefix="ceiba_transcribe_")

    try:
        # Step 1: Get the media file
        if is_url(source):
            media_path, title = download_media(source, tmp_dir)
        else:
            # Local file
            local = Path(source).expanduser().resolve()
            if not local.is_file():
                print(f"[ERROR] File not found: {source}")
                return False
            if local.suffix.lower() not in SUPPORTED_EXTENSIONS:
                print(f"[WARN] Unrecognized extension {local.suffix}, attempting anyway...")
            media_path = str(local)
            title = local.stem

        # Step 2: Extract audio to WAV
        print(f"[ffmpeg] Extracting audio from: {Path(media_path).name}")
        wav_path = extract_audio(media_path, tmp_dir)

        # Step 3: Transcribe
        t0 = time.time()
        result = transcribe_audio(wav_path, args.model, args.lang)
        elapsed = time.time() - t0
        lang_detected = result.get("language", "?")
        print(f"[whisper] Done in {elapsed:.1f}s | Language: {lang_detected}")

        # Step 4: Save outputs
        txt_path, json_path = save_outputs(
            result, title, source, output_dir, args.summary,
        )
        print(f"[saved] {txt_path}")
        print(f"[saved] {json_path}")

        # Print transcript preview
        text = result.get("text", "").strip()
        preview = text[:300] + ("..." if len(text) > 300 else "")
        print(f"\n--- Transcript preview ---\n{preview}\n")

        return True

    except Exception as e:
        print(f"[ERROR] {source}: {e}")
        return False

    finally:
        # Cleanup temp files
        import shutil as _shutil
        _shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="Ceiba Transcribe — video/audio transcription pipeline",
    )
    parser.add_argument(
        "sources", nargs="+",
        help="URLs (Instagram Reel, TikTok, YouTube Short) or local file paths",
    )
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--lang", default=None,
        help="Force language code (e.g. es, en). Omit for auto-detect.",
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Include a summary header in the .txt output",
    )

    args = parser.parse_args()

    check_dependencies()

    print(f"[ceiba_transcribe] Model: {args.model} | Output: {args.output}")
    if args.lang:
        print(f"[ceiba_transcribe] Forced language: {args.lang}")
    print()

    success = 0
    total = len(args.sources)
    for i, source in enumerate(args.sources, 1):
        if total > 1:
            print(f"=== [{i}/{total}] ===")
        if process_single(source, args):
            success += 1
        if i < total:
            print()

    print(f"\n[ceiba_transcribe] Finished: {success}/{total} succeeded.")
    sys.exit(0 if success == total else 1)


if __name__ == "__main__":
    main()
