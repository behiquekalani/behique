#!/usr/bin/env python3
"""
Reel Production Pipeline - Local Only ($0/month)
Turns a story script into a finished vertical video reel.

Components:
- Kokoro TTS (local, ~4x realtime on M4)
- MLX Stable Diffusion (local, Metal GPU)
- FFmpeg (Ken Burns effect + subtitle overlay)

Usage:
    python3 make_reel.py --story story.json --output reel.mp4
    python3 make_reel.py --text "Your story here" --output reel.mp4
"""

import argparse
import json
import os
import subprocess
import sys
import time
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
KOKORO_MODEL = PIPELINE_DIR / "kokoro-v1.0.onnx"
KOKORO_VOICES = PIPELINE_DIR / "voices-v1.0.bin"
MLX_SD_DIR = Path(os.path.expanduser("~/behique/tools/mlx-examples/stable_diffusion"))
OUTPUT_DIR = PIPELINE_DIR / "output"

# Reel dimensions
WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Remote video generation (Cobo)
COBO_VIDEO_URL = "http://192.168.0.151:9878"


def generate_narration(text, output_path, voice="af_heart", speed=0.9):
    """Generate narration audio using Kokoro TTS."""
    import kokoro_onnx
    import soundfile as sf

    print(f"[TTS] Generating narration ({len(text)} chars)...")
    start = time.time()

    kokoro = kokoro_onnx.Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    samples, sample_rate = kokoro.create(text, voice=voice, speed=speed)

    sf.write(str(output_path), samples, sample_rate)
    duration = len(samples) / sample_rate
    elapsed = time.time() - start
    print(f"[TTS] Generated {duration:.1f}s audio in {elapsed:.1f}s -> {output_path}")
    return duration


def get_audio_duration(audio_path):
    """Get duration of audio file using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def generate_image_mlx(prompt, output_path, steps=20):
    """Generate image using mflux (FLUX on MLX Apple Silicon)."""
    print(f"[IMG] Generating: {prompt[:60]}...")
    start = time.time()

    # Use mflux with locally quantized FLUX schnell 4-bit model
    model_path = os.path.expanduser("~/behique/tools/reel-pipeline/flux-schnell-4bit")
    result = subprocess.run(
        ["mflux-generate",
         "--model", model_path,
         "--prompt", prompt,
         "--steps", str(min(steps, 4)),
         "--width", "768", "--height", "1024",
         "--output", str(output_path)],
        capture_output=True, text=True,
        env={**os.environ, "HF_HUB_DISABLE_XET": "1"},
    )

    elapsed = time.time() - start
    if os.path.exists(output_path):
        print(f"[IMG] Generated in {elapsed:.1f}s -> {output_path}")
        return True
    else:
        print(f"[IMG] FAILED ({elapsed:.1f}s): {result.stderr[-200:]}")
        return False


def generate_image_ollama(prompt, output_path):
    """Generate image description via Ollama, use placeholder if no image model."""
    # Fallback: create a gradient placeholder image
    from PIL import Image, ImageDraw, ImageFont

    print(f"[IMG] Creating placeholder for: {prompt[:50]}...")
    img = Image.new('RGB', (WIDTH, HEIGHT), '#1a1a2e')
    draw = ImageDraw.Draw(img)

    # Dark cinematic gradient
    for y in range(HEIGHT):
        r = int(26 + (y / HEIGHT) * 20)
        g = int(26 + (y / HEIGHT) * 10)
        b = int(46 + (y / HEIGHT) * 30)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Add subtle text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except Exception:
        font = ImageFont.load_default()

    words = prompt.split()[:10]
    text = " ".join(words) + "..."
    draw.text((WIDTH // 2, HEIGHT // 2), text, fill=(100, 100, 140),
              anchor="mm", font=font)

    img.save(str(output_path))
    print(f"[IMG] Placeholder saved -> {output_path}")
    return True


def check_cobo_video():
    """Check if Cobo's video generation server is reachable."""
    try:
        req = urllib.request.Request(f"{COBO_VIDEO_URL}/", method="GET")
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        return data.get("ok", False)
    except Exception:
        return False


def request_animated_scene(prompt, duration=5, resolution="480p"):
    """Send a video generation request to Cobo and wait for result."""
    payload = json.dumps({
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
    }).encode()

    req = urllib.request.Request(
        f"{COBO_VIDEO_URL}/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        job_id = data.get("job_id")
        if not job_id:
            return None

        print(f"[ANIM] Job {job_id} queued on Cobo. Waiting...")

        # Poll for completion (max 20 min)
        for _ in range(240):
            time.sleep(5)
            try:
                status_req = urllib.request.Request(f"{COBO_VIDEO_URL}/status/{job_id}")
                status_resp = urllib.request.urlopen(status_req, timeout=10)
                status = json.loads(status_resp.read())

                if status["status"] == "done":
                    print(f"[ANIM] Job {job_id} complete! Downloading...")
                    return job_id
                elif status["status"] == "failed":
                    print(f"[ANIM] Job {job_id} failed: {status.get('error', 'unknown')}")
                    return None
            except Exception:
                continue

        print(f"[ANIM] Job {job_id} timed out after 20 min")
        return None
    except Exception as e:
        print(f"[ANIM] Failed to reach Cobo: {e}")
        return None


def download_video_from_cobo(job_id, output_path):
    """Download a completed video from Cobo."""
    try:
        req = urllib.request.Request(f"{COBO_VIDEO_URL}/download/{job_id}")
        resp = urllib.request.urlopen(req, timeout=120)
        with open(output_path, "wb") as f:
            f.write(resp.read())
        print(f"[ANIM] Downloaded -> {output_path}")
        return True
    except Exception as e:
        print(f"[ANIM] Download failed: {e}")
        return False


def create_ken_burns_clip(image_path, duration, output_path, effect="zoom_in"):
    """Create a Ken Burns effect clip from a still image using FFmpeg."""
    # Scale image to 1.3x the target to allow for zoom/pan
    zoom_factor = 1.3

    if effect == "zoom_in":
        # Slowly zoom in from full frame
        zoompan = (f"zoompan=z='min(zoom+0.001,{zoom_factor})':x='iw/2-(iw/zoom/2)'"
                   f":y='ih/2-(ih/zoom/2)':d={int(duration * FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}")
    elif effect == "zoom_out":
        # Start zoomed in, slowly zoom out
        zoompan = (f"zoompan=z='if(eq(on,1),{zoom_factor},max(zoom-0.001,1))':x='iw/2-(iw/zoom/2)'"
                   f":y='ih/2-(ih/zoom/2)':d={int(duration * FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}")
    else:  # pan
        # Slow pan from left to right
        zoompan = (f"zoompan=z='{zoom_factor}':x='if(eq(on,1),0,min(x+1,iw-iw/zoom))'"
                   f":y='ih/2-(ih/zoom/2)':d={int(duration * FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}")

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        "-vf", f"scale={int(WIDTH*zoom_factor)}:{int(HEIGHT*zoom_factor)}:force_original_aspect_ratio=increase,"
               f"crop={int(WIDTH*zoom_factor)}:{int(HEIGHT*zoom_factor)},{zoompan}",
        "-t", str(duration), "-pix_fmt", "yuv420p",
        "-c:v", "libx264", "-preset", "fast", str(output_path)
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return output_path


def burn_subtitles(video_path, text, output_path):
    """Burn subtitles into the video using FFmpeg drawtext."""
    # Split text into lines of ~40 chars for readability
    words = text.split()
    lines = []
    current = []
    for word in words:
        current.append(word)
        if len(" ".join(current)) > 35:
            lines.append(" ".join(current))
            current = []
    if current:
        lines.append(" ".join(current))

    subtitle_text = "\\n".join(lines[-3:])  # Show last 3 lines
    subtitle_text = subtitle_text.replace("'", "\\'").replace('"', '\\"')

    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", (f"drawtext=text='{subtitle_text}'"
                f":fontsize=36:fontcolor=white:borderw=2:bordercolor=black"
                f":x=(w-text_w)/2:y=h-th-100"
                f":fontfile=/System/Library/Fonts/Helvetica.ttc"),
        "-c:v", "libx264", "-preset", "fast", "-c:a", "copy",
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True, check=True)


def assemble_reel(scene_clips, narration_path, output_path):
    """Concatenate scene clips and overlay narration audio."""
    # Create concat file
    concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    for clip in scene_clips:
        concat_file.write(f"file '{clip}'\n")
    concat_file.close()

    # Concat video clips
    temp_video = str(output_path).replace('.mp4', '_temp.mp4')
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file.name, "-c", "copy", temp_video
    ], capture_output=True, check=True)

    # Overlay narration audio
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_video, "-i", str(narration_path),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-shortest",
        str(output_path)
    ], capture_output=True, check=True)

    # Cleanup
    os.unlink(concat_file.name)
    os.unlink(temp_video)
    print(f"[FINAL] Reel assembled -> {output_path}")


def parse_story(story_data):
    """Parse a story into scenes. Accepts dict or plain text."""
    if isinstance(story_data, dict):
        return story_data

    # Plain text: split into 4-6 scenes by sentences
    import re
    sentences = re.split(r'(?<=[.!?])\s+', story_data.strip())

    # Group sentences into scenes (2-3 sentences each)
    scenes = []
    chunk_size = max(1, len(sentences) // 5)
    for i in range(0, len(sentences), chunk_size):
        chunk = sentences[i:i + chunk_size]
        text = " ".join(chunk)
        # Generate a simple image prompt from the text
        scenes.append({
            "text": text,
            "image_prompt": f"Cinematic still, emotional, warm lighting, {text[:80]}, shallow depth of field, 4k"
        })

    return {
        "title": sentences[0][:50] if sentences else "Untitled",
        "scenes": scenes[:6],  # Max 6 scenes
        "narration": story_data
    }


def main():
    parser = argparse.ArgumentParser(description="Reel Production Pipeline")
    parser.add_argument("--story", help="JSON file with story data")
    parser.add_argument("--text", help="Plain text story")
    parser.add_argument("--output", default="reel.mp4", help="Output file")
    parser.add_argument("--voice", default="af_heart", help="Kokoro voice ID")
    parser.add_argument("--speed", type=float, default=0.9, help="Narration speed")
    parser.add_argument("--steps", type=int, default=20, help="SD inference steps")
    parser.add_argument("--use-placeholders", action="store_true",
                        help="Use placeholder images instead of SD generation")
    parser.add_argument("--animated", action="store_true",
                        help="Generate animated video scenes via Cobo (Wan2GP)")
    parser.add_argument("--cobo-url", default=COBO_VIDEO_URL,
                        help="Cobo video server URL (default: http://192.168.0.151:9878)")
    args = parser.parse_args()

    if args.cobo_url != COBO_VIDEO_URL:
        global COBO_VIDEO_URL
        COBO_VIDEO_URL = args.cobo_url

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Load story
    if args.story:
        with open(args.story) as f:
            story_data = json.load(f)
        story = parse_story(story_data)
    elif args.text:
        story = parse_story(args.text)
    else:
        print("Provide --story (JSON) or --text (plain text)")
        sys.exit(1)

    output_path = OUTPUT_DIR / args.output
    work_dir = OUTPUT_DIR / "work"
    work_dir.mkdir(exist_ok=True)

    print(f"\n{'='*50}")
    print(f"REEL PIPELINE - {story.get('title', 'Untitled')}")
    print(f"{'='*50}")
    print(f"Scenes: {len(story['scenes'])}")
    print(f"Voice: {args.voice} @ {args.speed}x speed")
    print()

    # Step 1: Generate narration
    narration_path = work_dir / "narration.wav"
    narration_text = story.get("narration", " ".join(s["text"] for s in story["scenes"]))
    audio_duration = generate_narration(narration_text, narration_path, args.voice, args.speed)

    # Step 2: Calculate per-scene duration
    scene_count = len(story["scenes"])
    scene_duration = audio_duration / scene_count

    # Step 3: Generate images for each scene
    scene_clips = []
    effects = ["zoom_in", "zoom_out", "pan", "zoom_in", "zoom_out", "pan"]

    # Check animated mode
    use_animated = args.animated
    if use_animated:
        if check_cobo_video():
            print("[MODE] ANIMATED - Cobo is online, generating video scenes")
        else:
            print("[MODE] Cobo not reachable, falling back to static images + Ken Burns")
            use_animated = False

    for i, scene in enumerate(story["scenes"]):
        print(f"\n--- Scene {i+1}/{scene_count} ---")
        img_path = work_dir / f"scene_{i:02d}.png"
        clip_path = work_dir / f"clip_{i:02d}.mp4"

        if use_animated:
            # Send to Cobo for animated video generation
            video_prompt = scene["image_prompt"] + ", smooth cinematic motion, slow camera movement"
            job_id = request_animated_scene(video_prompt, duration=int(scene_duration) + 1)
            if job_id and download_video_from_cobo(job_id, clip_path):
                # Trim to exact scene duration and scale to reel dimensions
                trimmed = work_dir / f"clip_{i:02d}_trimmed.mp4"
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(clip_path),
                    "-t", str(scene_duration),
                    "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264", "-preset", "fast",
                    str(trimmed)
                ], capture_output=True, check=True)
                os.replace(str(trimmed), str(clip_path))
                scene_clips.append(str(clip_path))
                print(f"[CLIP] Animated scene, {scene_duration:.1f}s")
                continue
            else:
                print("[ANIM] Falling back to static image for this scene")

        # Static image path (original pipeline or fallback)
        if args.use_placeholders:
            generate_image_ollama(scene["image_prompt"], img_path)
        else:
            success = generate_image_mlx(scene["image_prompt"], img_path, args.steps)
            if not success:
                generate_image_ollama(scene["image_prompt"], img_path)

        # Create Ken Burns clip
        effect = effects[i % len(effects)]
        create_ken_burns_clip(img_path, scene_duration, clip_path, effect)
        scene_clips.append(str(clip_path))
        print(f"[CLIP] {effect} effect, {scene_duration:.1f}s")

    # Step 4: Assemble final reel
    print(f"\n--- Assembly ---")
    assemble_reel(scene_clips, narration_path, output_path)

    # Stats
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n{'='*50}")
    print(f"DONE!")
    print(f"Output: {output_path}")
    print(f"Duration: {audio_duration:.1f}s")
    print(f"Size: {file_size:.1f} MB")
    print(f"Format: {WIDTH}x{HEIGHT} @ {FPS}fps (vertical)")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
