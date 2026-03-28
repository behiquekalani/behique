#!/usr/bin/env python3
"""
Full Reel Pipeline: Story JSON -> Instagram-Ready Reel
Chains all steps: TTS -> Image Gen -> Instagram Compose -> Queue

Usage:
    python3 full_pipeline.py grandmas-recipe-card     # single story
    python3 full_pipeline.py --all                     # all stories
    python3 full_pipeline.py --status                  # show full status
    python3 full_pipeline.py --new "My Story Title"    # create new story interactively
"""

import json
import subprocess
import os
import sys
import time
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"
INSTAGRAM_DIR = PIPELINE_DIR / "instagram_ready"


def run_tts(story_name):
    """Generate TTS narration + per-scene audio + timing."""
    out_dir = OUTPUT_DIR / story_name
    if (out_dir / "narration.wav").exists() and (out_dir / "timing.json").exists():
        print(f"  [TTS] Already done")
        return True

    print(f"  [TTS] Generating narration...")
    r = subprocess.run(
        ['python3', 'make_reel.py', story_name, '--tts-only'],
        cwd=str(PIPELINE_DIR),
        capture_output=True, text=True
    )
    # If make_reel.py doesn't have --tts-only, do it inline
    if r.returncode != 0:
        return run_tts_inline(story_name)
    return True


def run_tts_inline(story_name):
    """Generate TTS directly using Kokoro."""
    out_dir = OUTPUT_DIR / story_name
    out_dir.mkdir(parents=True, exist_ok=True)

    story_file = STORIES_DIR / f"{story_name}.json"
    with open(story_file) as f:
        story = json.load(f)

    try:
        from kokoro_onnx import Kokoro
    except ImportError:
        print("  [ERROR] kokoro_onnx not installed")
        return False

    model_path = PIPELINE_DIR / "kokoro-v1.0.onnx"
    voices_path = PIPELINE_DIR / "voices-v1.0.bin"

    if not model_path.exists():
        print(f"  [ERROR] Kokoro model not found at {model_path}")
        return False

    kokoro = Kokoro(str(model_path), str(voices_path))
    # Auto-detect language from story name
    if story_name.endswith("_es"):
        voice = "ef_dora"   # Spanish female
        speed = 0.85        # Slightly slower for clarity
    else:
        voice = "af_heart"  # English female
        speed = 0.9

    import soundfile as sf
    import numpy as np

    # Generate per-scene audio
    timing_data = {"title": story["title"], "scenes": [], "total_duration": 0}
    all_audio = []
    current_time = 0.0

    for i, scene in enumerate(story["scenes"]):
        print(f"    Scene {i}: {scene['text'][:50]}...")
        samples, sample_rate = kokoro.create(scene["text"], voice=voice, speed=speed)

        scene_path = out_dir / f"scene_{i}.wav"
        sf.write(str(scene_path), samples, sample_rate)

        duration = len(samples) / sample_rate
        timing_data["scenes"].append({
            "index": i,
            "text": scene["text"],
            "image_prompt": scene.get("image_prompt", ""),
            "start": current_time,
            "duration": duration,
            "end": current_time + duration,
        })

        all_audio.append(samples)
        current_time += duration

    timing_data["total_duration"] = current_time

    # Concatenate all audio
    full_audio = np.concatenate(all_audio)
    narration_path = out_dir / "narration.wav"
    sf.write(str(narration_path), full_audio, sample_rate)

    # Save timing
    timing_path = out_dir / "timing.json"
    with open(timing_path, 'w') as f:
        json.dump(timing_data, f, indent=2)

    # Save subtitle text
    for i, scene in enumerate(timing_data["scenes"]):
        sub_path = out_dir / f"sub_{i}.txt"
        with open(sub_path, 'w') as f:
            f.write(scene["text"])

    print(f"  [TTS] Done: {current_time:.1f}s total")
    return True


def run_image_gen(story_name, cobo=False):
    """Generate scene images with mflux (or Cobo)."""
    story_file = STORIES_DIR / f"{story_name}.json"
    with open(story_file) as f:
        story = json.load(f)

    out_dir = OUTPUT_DIR / story_name
    out_dir.mkdir(parents=True, exist_ok=True)

    all_done = True
    for i, scene in enumerate(story["scenes"]):
        img = out_dir / f"scene_{i}.png"
        if img.exists():
            continue

        all_done = False
        prompt = scene["image_prompt"]
        print(f"  [IMG] Scene {i}: {prompt[:60]}...")

        model_path = PIPELINE_DIR / "flux-schnell-4bit"
        if not model_path.exists():
            print(f"  [ERROR] FLUX model not found")
            return False

        start = time.time()
        r = subprocess.run([
            'mflux-generate',
            '--model', str(model_path),
            '--prompt', prompt,
            '--steps', '4',
            '--width', '768', '--height', '1024',
            '--output', str(img),
        ], capture_output=True, text=True,
           env={**os.environ, 'HF_HUB_DISABLE_XET': '1'})

        elapsed = time.time() - start
        if img.exists():
            print(f"  [IMG] Scene {i} done ({elapsed:.0f}s)")
        else:
            print(f"  [IMG] Scene {i} FAILED ({elapsed:.0f}s)")
            return False

    if all_done:
        print(f"  [IMG] All images exist")
    return True


def run_instagram(story_name, force=False):
    """Run Instagram pipeline (captions + audio + encode)."""
    r = subprocess.run(
        ['python3', 'instagram_pipeline.py', story_name] + (['--force'] if force else []),
        cwd=str(PIPELINE_DIR),
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print(r.stdout[-200:] if len(r.stdout) > 200 else r.stdout)
        return True
    else:
        print(f"  [ERROR] Instagram pipeline: {r.stderr[-200:]}")
        return False


def process_story(story_name, skip_images=False, force=False):
    """Run the full pipeline for one story."""
    story_file = STORIES_DIR / f"{story_name}.json"
    if not story_file.exists():
        print(f"[ERROR] Story not found: {story_name}")
        return False

    print(f"\n{'='*60}")
    print(f"  FULL PIPELINE: {story_name}")
    print(f"{'='*60}")

    # Step 1: TTS
    print("\n[Step 1] TTS Narration")
    if not run_tts(story_name):
        print("[FAIL] TTS generation failed")
        return False

    # Step 2: Image Generation
    print("\n[Step 2] Image Generation")
    if skip_images:
        print("  [SKIP] --skip-images flag set")
    else:
        if not run_image_gen(story_name):
            print("[FAIL] Image generation failed")
            return False

    # Step 3: Instagram Pipeline
    print("\n[Step 3] Instagram Compose")
    if not run_instagram(story_name, force=force):
        print("[FAIL] Instagram pipeline failed")
        return False

    print(f"\n[COMPLETE] {story_name} is Instagram-ready!")
    ig_file = INSTAGRAM_DIR / f"{story_name}.mp4"
    if ig_file.exists():
        size = ig_file.stat().st_size / (1024 * 1024)
        print(f"  File: {ig_file} ({size:.1f} MB)")
    return True


def show_status():
    """Show full pipeline status for all stories."""
    stories = sorted(STORIES_DIR.glob("*.json"))

    print(f"\n{'='*80}")
    print(f"  FULL PIPELINE STATUS")
    print(f"{'='*80}")
    print(f"{'Story':<30} {'TTS':>4} {'Imgs':>6} {'IG':>4} {'Status':<15}")
    print(f"{'-'*80}")

    total = ready = ig_done = 0
    for sf in stories:
        name = sf.stem
        out = OUTPUT_DIR / name
        ig = INSTAGRAM_DIR / f"{name}.mp4"

        with open(sf) as f:
            expected = len(json.load(f).get("scenes", []))

        has_tts = (out / "narration.wav").exists() if out.exists() else False
        imgs = len(list(out.glob("scene_*.png"))) if out.exists() else 0
        has_ig = ig.exists()

        tts_str = "Y" if has_tts else "n"
        img_str = f"{imgs}/{expected}" if imgs < expected else f" {imgs}"
        ig_str = "Y" if has_ig else "n"

        if has_ig:
            status = "READY"
            ig_done += 1
        elif imgs >= expected and has_tts:
            status = "needs compose"
            ready += 1
        elif has_tts:
            status = "needs images"
        else:
            status = "needs TTS"

        total += 1
        print(f"  {name:<28} {tts_str:>4} {img_str:>6} {ig_str:>4} {status:<15}")

    print(f"{'-'*80}")
    print(f"  Total: {total} | Can compose: {ready} | IG ready: {ig_done}")
    print(f"  Pipeline tools: music/ambient_warm.wav {'EXISTS' if (PIPELINE_DIR/'music'/'ambient_warm.wav').exists() else 'MISSING'}")
    print()


if __name__ == "__main__":
    os.chdir(PIPELINE_DIR)

    if len(sys.argv) < 2:
        print("Usage: python3 full_pipeline.py <story|--all|--status>")
        sys.exit(1)

    arg = sys.argv[1]
    force = "--force" in sys.argv
    skip_images = "--skip-images" in sys.argv

    if arg == "--status":
        show_status()
    elif arg == "--all":
        stories = sorted(STORIES_DIR.glob("*.json"))
        ok = fail = 0
        for sf in stories:
            if process_story(sf.stem, skip_images=skip_images, force=force):
                ok += 1
            else:
                fail += 1
        print(f"\n  BATCH: {ok} complete, {fail} failed")
    else:
        process_story(arg, skip_images=skip_images, force=force)
