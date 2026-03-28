#!/usr/bin/env python3
"""
Batch generate images for all stories missing them.
Auto-detects Hutia (remote SDXL Turbo) or falls back to local mflux.

Usage:
    python3 batch_generate_images.py              # generate all missing
    python3 batch_generate_images.py --limit 5    # limit to N stories
    python3 batch_generate_images.py --compose    # also compose after generating
    python3 batch_generate_images.py --remote     # force Hutia (remote) only
    python3 batch_generate_images.py --local      # force local mflux only
"""
import json, subprocess, os, sys, time
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"
MODEL_PATH = os.path.expanduser("~/behique/tools/reel-pipeline/flux-schnell-4bit")


def generate_image(prompt, output_path, steps=4, backend="auto"):
    """Generate one image. Uses Hutia (remote) if available, else local mflux."""
    if backend in ("auto", "remote"):
        try:
            from remote_image_gen import is_hutia_available, generate_remote
            if is_hutia_available():
                return generate_remote(prompt, str(output_path), steps=steps)
        except ImportError:
            pass
        if backend == "remote":
            print("    [ERROR] Hutia not available and --remote was specified")
            return False

    # Local mflux fallback
    start = time.time()
    result = subprocess.run(
        ["mflux-generate",
         "--model", MODEL_PATH,
         "--prompt", prompt,
         "--steps", str(steps),
         "--width", "768", "--height", "1024",
         "--output", str(output_path)],
        capture_output=True, text=True,
        env={**os.environ, "HF_HUB_DISABLE_XET": "1"},
    )
    elapsed = time.time() - start
    if os.path.exists(output_path):
        print(f"    [LOCAL] Generated in {elapsed:.0f}s")
        return True
    else:
        print(f"    [LOCAL] FAILED ({elapsed:.0f}s): {result.stderr[-200:]}")
        return False


def generate_narration(text, output_path, voice="af_heart", speed=0.9):
    """Generate narration with Kokoro TTS."""
    import kokoro_onnx
    import soundfile as sf

    kokoro = kokoro_onnx.Kokoro(
        str(PIPELINE_DIR / "kokoro-v1.0.onnx"),
        str(PIPELINE_DIR / "voices-v1.0.bin")
    )
    samples, sample_rate = kokoro.create(text, voice=voice, speed=speed)
    sf.write(str(output_path), samples, sample_rate)
    duration = len(samples) / sample_rate
    return duration


def find_incomplete_stories():
    """Find stories that need images or narration."""
    incomplete = []
    for story_json in sorted(STORIES_DIR.glob("*.json")):
        name = story_json.stem
        story_dir = OUTPUT_DIR / name
        story_dir.mkdir(exist_ok=True)

        with open(story_json) as f:
            story = json.load(f)

        scenes = story.get("scenes", [])
        existing_images = [f for f in story_dir.glob("scene_*.png")
                          if '_sub' not in f.name and '_cap' not in f.name]
        has_narration = (story_dir / "narration.wav").exists()
        has_timing = (story_dir / "timing.json").exists()

        missing_images = len(scenes) - len(existing_images)
        if missing_images > 0 or not has_narration:
            incomplete.append({
                'name': name,
                'json': story_json,
                'story': story,
                'scenes': scenes,
                'missing_images': missing_images,
                'has_narration': has_narration,
                'has_timing': has_timing,
                'existing_count': len(existing_images),
            })
    return incomplete


def process_story(story_info):
    """Generate all missing assets for a story."""
    name = story_info['name']
    story = story_info['story']
    story_dir = OUTPUT_DIR / name
    scenes = story_info['scenes']

    print(f"\n{'='*50}")
    print(f"  {story.get('title', name)}")
    print(f"  Missing: {story_info['missing_images']} images, narration={'NO' if not story_info['has_narration'] else 'YES'}")
    print(f"{'='*50}")

    # Generate narration if missing
    if not story_info['has_narration']:
        narration_text = story.get("narration", " ".join(s["text"] for s in scenes))
        print(f"[TTS] Generating narration...")
        duration = generate_narration(narration_text, story_dir / "narration.wav")
        print(f"[TTS] {duration:.1f}s narration generated")

    # Generate timing.json if missing
    if not story_info['has_timing']:
        narration_path = story_dir / "narration.wav"
        duration = float(subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(narration_path)],
            capture_output=True, text=True
        ).stdout.strip())

        scene_dur = duration / len(scenes)
        timing = {"title": story.get("title", name), "scenes": [], "total_duration": duration}
        for i, scene in enumerate(scenes):
            timing["scenes"].append({
                "index": i,
                "text": scene["text"],
                "image_prompt": scene["image_prompt"],
                "start": i * scene_dur,
                "duration": scene_dur,
                "end": (i + 1) * scene_dur,
            })
        with open(story_dir / "timing.json", 'w') as f:
            json.dump(timing, f, indent=2)

    # Generate missing images
    for i, scene in enumerate(scenes):
        img_path = story_dir / f"scene_{i}.png"
        if img_path.exists():
            print(f"  [IMG {i+1}/{len(scenes)}] Already exists, skipping")
            continue

        print(f"  [IMG {i+1}/{len(scenes)}] {scene['image_prompt'][:60]}...")
        success = generate_image(scene["image_prompt"], img_path, backend=backend)
        if not success:
            print(f"  [IMG {i+1}] Retrying...")
            generate_image(scene["image_prompt"], img_path, backend=backend)

    print(f"[DONE] {name} - all assets ready")


def main():
    limit = None
    auto_compose = False
    backend = "auto"

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == '--limit' and i < len(sys.argv) - 1:
            limit = int(sys.argv[i + 1])
        if arg == '--compose':
            auto_compose = True
        if arg == '--remote':
            backend = "remote"
        if arg == '--local':
            backend = "local"

    incomplete = find_incomplete_stories()

    if not incomplete:
        print("All stories have complete assets!")
        return

    if limit:
        incomplete = incomplete[:limit]

    print(f"Processing {len(incomplete)} stories...")
    total_images = sum(s['missing_images'] for s in incomplete)
    print(f"Total images to generate: {total_images}")
    print(f"Backend: {backend}")
    if backend == "local":
        est_minutes = total_images * 2.5  # ~2.5 min per image on M4
    else:
        est_minutes = total_images * 1  # ~1 min per image on Hutia SDXL Turbo
    print(f"Estimated time: ~{est_minutes:.0f} minutes")

    for s in incomplete:
        process_story(s)

    if auto_compose:
        print("\n\n=== AUTO-COMPOSING INSTAGRAM REELS ===")
        subprocess.run([sys.executable, str(PIPELINE_DIR / "instagram_compose.py"), "--all"])


if __name__ == '__main__':
    main()
