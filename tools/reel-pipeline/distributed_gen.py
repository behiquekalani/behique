#!/usr/bin/env python3
"""
Distributed Image Generation
Routes image generation requests across all available machines:
- Ceiba (192.168.0.145): mflux FLUX.1-schnell 4-bit (~2.5 min/image)
- Cobo (192.168.0.151): Wan2GP video gen on port 9878
- Hutia (192.168.0.152): SDXL Turbo on port 9879 (~15-30s/image)

Usage:
    python3 distributed_gen.py --status         # check all machines
    python3 distributed_gen.py --generate-all   # generate all missing images
"""

import json
import subprocess
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"

MACHINES = {
    "ceiba": {
        "ip": "192.168.0.145",
        "type": "mflux",
        "speed": "~150s/image",
    },
    "hutia": {
        "ip": "192.168.0.152",
        "port": 9879,
        "type": "http",
        "speed": "~20s/image",
    },
    "cobo": {
        "ip": "192.168.0.151",
        "port": 9878,
        "type": "video",  # video gen, not still images
        "speed": "~60s/video",
    },
}


def check_machine(name, info):
    """Check if a machine's image gen is available."""
    if info["type"] == "mflux":
        # Local machine -- always available
        return True

    url = f"http://{info['ip']}:{info['port']}/"
    try:
        req = urllib.request.urlopen(url, timeout=3)
        data = json.loads(req.read())
        return data.get("ok", False)
    except Exception:
        return False


def generate_on_hutia(prompt, output_path, width=768, height=1024):
    """Send image gen request to Hutia."""
    url = f"http://{MACHINES['hutia']['ip']}:{MACHINES['hutia']['port']}/generate"
    data = json.dumps({"prompt": prompt, "width": width, "height": height, "steps": 4}).encode()

    try:
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=120)

        with open(output_path, 'wb') as f:
            f.write(resp.read())

        return output_path.exists()
    except Exception as e:
        print(f"  [ERROR] Hutia: {e}")
        return False


def generate_on_ceiba(prompt, output_path):
    """Generate image locally with mflux."""
    model_path = PIPELINE_DIR / "flux-schnell-4bit"
    r = subprocess.run([
        'mflux-generate',
        '--model', str(model_path),
        '--prompt', prompt,
        '--steps', '4',
        '--width', '768', '--height', '1024',
        '--output', str(output_path),
    ], capture_output=True, text=True,
       env={**os.environ, 'HF_HUB_DISABLE_XET': '1'})

    return output_path.exists()


def get_missing_images():
    """Find all stories with missing scene images."""
    missing = []
    for sf in sorted(STORIES_DIR.glob("*.json")):
        name = sf.stem
        out_dir = OUTPUT_DIR / name
        with open(sf) as f:
            story = json.load(f)

        for i, scene in enumerate(story["scenes"]):
            img = out_dir / f"scene_{i}.png"
            if not img.exists():
                out_dir.mkdir(parents=True, exist_ok=True)
                missing.append({
                    "story": name,
                    "scene": i,
                    "prompt": scene["image_prompt"],
                    "output": img,
                })
    return missing


def show_status():
    """Show status of all machines."""
    print(f"\n{'='*60}")
    print(f"  DISTRIBUTED IMAGE GEN STATUS")
    print(f"{'='*60}")

    for name, info in MACHINES.items():
        available = check_machine(name, info)
        status = "ONLINE" if available else "OFFLINE"
        print(f"  {name:<10} {info['ip']:<16} {info['type']:<8} {info['speed']:<15} {status}")

    missing = get_missing_images()
    print(f"\n  Missing images: {len(missing)}")
    if missing:
        by_story = {}
        for m in missing:
            by_story.setdefault(m["story"], []).append(m["scene"])
        for story, scenes in by_story.items():
            print(f"    {story}: scenes {scenes}")


def generate_all():
    """Generate all missing images using available machines."""
    missing = get_missing_images()
    if not missing:
        print("All images generated!")
        return

    # Check what's available
    hutia_up = check_machine("hutia", MACHINES["hutia"])

    print(f"\n{'='*60}")
    print(f"  GENERATING {len(missing)} IMAGES")
    print(f"  Ceiba (mflux): always")
    print(f"  Hutia (SDXL):  {'YES' if hutia_up else 'NO'}")
    print(f"{'='*60}\n")

    if hutia_up:
        # Split work: alternate between Ceiba and Hutia
        ceiba_queue = missing[::2]  # even indices
        hutia_queue = missing[1::2]  # odd indices

        print(f"  Ceiba: {len(ceiba_queue)} images")
        print(f"  Hutia: {len(hutia_queue)} images\n")

        # Run Hutia jobs in parallel thread
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}

            for item in hutia_queue:
                f = executor.submit(generate_on_hutia, item["prompt"], item["output"])
                futures[f] = ("hutia", item)

            for item in ceiba_queue:
                f = executor.submit(generate_on_ceiba, item["prompt"], item["output"])
                futures[f] = ("ceiba", item)

            for future in as_completed(futures):
                machine, item = futures[future]
                try:
                    ok = future.result()
                    status = "OK" if ok else "FAIL"
                except Exception as e:
                    status = f"ERROR: {e}"
                print(f"  [{machine}] {item['story']} scene {item['scene']}: {status}")
    else:
        # Ceiba only
        for idx, item in enumerate(missing):
            print(f"[{idx+1}/{len(missing)}] {item['story']} scene {item['scene']}")
            start = time.time()
            ok = generate_on_ceiba(item["prompt"], item["output"])
            elapsed = time.time() - start
            print(f"  {'OK' if ok else 'FAIL'} ({elapsed:.0f}s)")


if __name__ == "__main__":
    os.chdir(PIPELINE_DIR)

    if "--status" in sys.argv:
        show_status()
    elif "--generate-all" in sys.argv:
        generate_all()
    else:
        show_status()
