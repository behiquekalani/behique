#!/usr/bin/env python3
"""
Master Reel Pipeline - One command to rule them all.

Stages:
  1. NARRATE  - Generate TTS narration for all stories
  2. IMAGE    - Generate images with mflux (FLUX schnell 4-bit)
  3. COMPOSE  - Compose Instagram-ready reels (animated captions, bg music)
  4. QUEUE    - Build posting schedule with captions and hashtags

Usage:
    python3 pipeline.py                    # run full pipeline
    python3 pipeline.py --stage compose    # run from specific stage
    python3 pipeline.py --status           # show pipeline status
    python3 pipeline.py --story NAME       # process single story
"""
import json, os, sys, subprocess, time
from pathlib import Path
from datetime import datetime

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"


def get_pipeline_status():
    """Get status of every story in the pipeline."""
    stories = []
    for story_json in sorted(STORIES_DIR.glob("*.json")):
        name = story_json.stem
        story_dir = OUTPUT_DIR / name

        with open(story_json) as f:
            story = json.load(f)

        num_scenes = len(story.get("scenes", []))
        has_narration = (story_dir / "narration.wav").exists() if story_dir.exists() else False
        images = list(story_dir.glob("scene_*.png")) if story_dir.exists() else []
        images = [f for f in images if '_sub' not in f.name and '_cap' not in f.name]
        has_reel = (OUTPUT_DIR / f"{name}_instagram.mp4").exists()

        if has_reel:
            stage = "DONE"
        elif len(images) >= num_scenes:
            stage = "COMPOSE"
        elif has_narration:
            stage = "IMAGE"
        elif story_dir.exists():
            stage = "NARRATE"
        else:
            stage = "NEW"

        stories.append({
            'name': name,
            'title': story.get('title', name),
            'scenes': num_scenes,
            'narration': has_narration,
            'images': len(images),
            'reel': has_reel,
            'stage': stage,
        })

    return stories


def print_status():
    """Print pipeline status dashboard."""
    stories = get_pipeline_status()

    done = [s for s in stories if s['stage'] == 'DONE']
    compose = [s for s in stories if s['stage'] == 'COMPOSE']
    image = [s for s in stories if s['stage'] == 'IMAGE']
    narrate = [s for s in stories if s['stage'] == 'NARRATE']
    new = [s for s in stories if s['stage'] == 'NEW']

    total_images_needed = sum(s['scenes'] - s['images'] for s in stories if s['stage'] in ('IMAGE', 'NARRATE', 'NEW'))
    est_hours = (total_images_needed * 2.5) / 60

    print(f"\n{'='*60}")
    print(f"  REEL PIPELINE STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"  Total stories: {len(stories)}")
    print(f"  Done:          {len(done)} reels ready for Instagram")
    print(f"  Need compose:  {len(compose)} (have images, need compositing)")
    print(f"  Need images:   {len(image)} (have narration, need mflux)")
    print(f"  Need narrate:  {len(narrate)} (need TTS)")
    print(f"  Brand new:     {len(new)} (need everything)")
    print(f"  Images left:   {total_images_needed} (~{est_hours:.1f} hours on M4)")
    print(f"{'='*60}\n")

    # Detailed view
    stage_icons = {'DONE': '[x]', 'COMPOSE': '[C]', 'IMAGE': '[I]', 'NARRATE': '[N]', 'NEW': '[ ]'}
    for s in stories:
        icon = stage_icons[s['stage']]
        img_str = f"{s['images']}/{s['scenes']} imgs"
        narr_str = "narr" if s['narration'] else "----"
        reel_str = "REEL" if s['reel'] else "----"
        print(f"  {icon} {s['name']:<35} {narr_str} {img_str:<10} {reel_str}")

    # Show completed reel files
    if done:
        print(f"\n  Completed reels:")
        for s in done:
            reel_path = OUTPUT_DIR / f"{s['name']}_instagram.mp4"
            size = os.path.getsize(reel_path) / (1024 * 1024)
            print(f"    {reel_path.name} ({size:.1f} MB)")


def run_stage(stage, story_name=None):
    """Run a specific pipeline stage."""
    py = sys.executable

    if stage in ('narrate', 'image', 'all'):
        args = [py, str(PIPELINE_DIR / "batch_generate_images.py")]
        if story_name:
            # Single story mode not yet in batch script, run make_reel instead
            args = [py, str(PIPELINE_DIR / "make_reel.py"),
                    "--story", str(STORIES_DIR / f"{story_name}.json"),
                    "--output", f"{story_name}.mp4"]
        if stage == 'all':
            args.append('--compose')
        print(f"[PIPELINE] Running: {' '.join(args)}")
        subprocess.run(args)

    if stage in ('compose', 'all'):
        args = [py, str(PIPELINE_DIR / "instagram_compose.py")]
        if story_name:
            args.append(story_name)
        else:
            args.append('--all')
        print(f"[PIPELINE] Running: {' '.join(args)}")
        subprocess.run(args)

    if stage in ('queue', 'all'):
        args = [py, str(PIPELINE_DIR / "instagram_post.py"), "--queue"]
        print(f"[PIPELINE] Running: {' '.join(args)}")
        subprocess.run(args)


def main():
    if '--status' in sys.argv:
        print_status()
        return

    if '--story' in sys.argv:
        idx = sys.argv.index('--story')
        story_name = sys.argv[idx + 1]
        stage = 'all'
        if '--stage' in sys.argv:
            stage = sys.argv[sys.argv.index('--stage') + 1]
        run_stage(stage, story_name)
        return

    stage = 'all'
    if '--stage' in sys.argv:
        stage = sys.argv[sys.argv.index('--stage') + 1]

    run_stage(stage)
    print_status()


if __name__ == '__main__':
    main()
