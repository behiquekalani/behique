"""
Stable Diffusion Image Generator
Connects to AUTOMATIC1111 WebUI API on localhost:7860
Supports single and batch generation with preset prompts.
"""

import requests
import base64
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# --- Configuration ---
SD_API_URL = "http://localhost:7860"
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
PRESETS_FILE = SCRIPT_DIR / "presets.json"

# Default negative prompt (good general-purpose negative)
DEFAULT_NEGATIVE = (
    "ugly, blurry, low quality, distorted, deformed, disfigured, "
    "bad anatomy, watermark, signature, text, logo, banner, "
    "extra digits, cropped, worst quality, low resolution, "
    "jpeg artifacts, out of frame, duplicate"
)


def check_api():
    """Check if SD WebUI API is running."""
    try:
        r = requests.get(f"{SD_API_URL}/sdapi/v1/sd-models", timeout=5)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def get_models():
    """List available models."""
    r = requests.get(f"{SD_API_URL}/sdapi/v1/sd-models", timeout=10)
    r.raise_for_status()
    return [m["title"] for m in r.json()]


def generate_image(
    prompt,
    negative_prompt=None,
    width=1920,
    height=1080,
    steps=30,
    cfg=7,
    sampler="DPM++ 2M Karras",
    seed=-1,
    batch_size=1,
    output_subdir=None,
    filename_prefix=None,
):
    """
    Generate an image using the SD WebUI API.

    Args:
        prompt: Text prompt for generation
        negative_prompt: What to avoid (uses default if None)
        width: Image width (default 1920)
        height: Image height (default 1080)
        steps: Sampling steps (default 30)
        cfg: CFG scale (default 7)
        sampler: Sampler name (default DPM++ 2M Karras)
        seed: Random seed (-1 for random)
        batch_size: Number of images per generation
        output_subdir: Subfolder inside output/ (e.g., "frequency")
        filename_prefix: Prefix for filename (e.g., "thumbnail")

    Returns:
        List of saved file paths
    """
    if not check_api():
        print("[ERROR] SD WebUI API not reachable at", SD_API_URL)
        print("Start it with: C:\\behique\\stable-diffusion\\start_sd.bat")
        return []

    if negative_prompt is None:
        negative_prompt = DEFAULT_NEGATIVE

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg,
        "sampler_name": sampler,
        "seed": seed,
        "batch_size": batch_size,
    }

    print(f"[GENERATING] {prompt[:80]}...")
    print(f"  Size: {width}x{height} | Steps: {steps} | CFG: {cfg}")

    try:
        r = requests.post(
            f"{SD_API_URL}/sdapi/v1/txt2img",
            json=payload,
            timeout=300,
        )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Generation failed: {e}")
        return []

    result = r.json()
    saved_files = []

    # Determine output directory
    save_dir = OUTPUT_DIR
    if output_subdir:
        save_dir = OUTPUT_DIR / output_subdir
    save_dir.mkdir(parents=True, exist_ok=True)

    # Save each image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for i, img_data in enumerate(result["images"]):
        # Skip the grid image if batch > 1
        if batch_size > 1 and i == len(result["images"]) - 1:
            continue

        prefix = filename_prefix or "sd"
        filename = f"{prefix}_{timestamp}_{i:02d}.png"
        filepath = save_dir / filename

        img_bytes = base64.b64decode(img_data)
        with open(filepath, "wb") as f:
            f.write(img_bytes)

        saved_files.append(str(filepath))
        print(f"  [SAVED] {filepath}")

    # Save generation info
    info = json.loads(result.get("info", "{}"))
    info_file = save_dir / f"{prefix}_{timestamp}_info.json"
    with open(info_file, "w") as f:
        json.dump(
            {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg,
                "sampler": sampler,
                "seed": info.get("seed", seed),
                "files": saved_files,
            },
            f,
            indent=2,
        )

    return saved_files


def generate_batch(prompts_list, **kwargs):
    """
    Generate images from a list of prompts.

    Args:
        prompts_list: List of prompt strings or dicts with full config.
            If string: uses kwargs as defaults.
            If dict: can override any generate_image parameter.
        **kwargs: Default parameters passed to generate_image.

    Returns:
        Dict mapping prompt to list of saved file paths.
    """
    results = {}
    total = len(prompts_list)

    for i, prompt_config in enumerate(prompts_list, 1):
        print(f"\n[BATCH {i}/{total}]")

        if isinstance(prompt_config, str):
            params = {**kwargs, "prompt": prompt_config}
        elif isinstance(prompt_config, dict):
            params = {**kwargs, **prompt_config}
        else:
            print(f"  [SKIP] Invalid prompt config: {prompt_config}")
            continue

        prompt_text = params.pop("prompt", "")
        if not prompt_text:
            print("  [SKIP] Empty prompt")
            continue

        files = generate_image(prompt_text, **params)
        results[prompt_text[:60]] = files

        # Brief pause between generations to let VRAM clear
        if i < total:
            time.sleep(2)

    return results


def load_presets():
    """Load preset prompts from presets.json."""
    if not PRESETS_FILE.exists():
        print(f"[ERROR] Presets file not found: {PRESETS_FILE}")
        return {}

    with open(PRESETS_FILE) as f:
        return json.load(f)


def generate_from_preset(category, preset_name=None, **kwargs):
    """
    Generate image(s) from a preset category.

    Args:
        category: Preset category (frequency, mockup, social, abstract)
        preset_name: Specific preset name (random if None)
        **kwargs: Override any generation parameter.

    Returns:
        List of saved file paths.
    """
    presets = load_presets()
    if category not in presets:
        print(f"[ERROR] Category '{category}' not found. Options: {list(presets.keys())}")
        return []

    category_presets = presets[category]

    if preset_name:
        preset = next((p for p in category_presets if p["name"] == preset_name), None)
        if not preset:
            names = [p["name"] for p in category_presets]
            print(f"[ERROR] Preset '{preset_name}' not found. Options: {names}")
            return []
    else:
        import random
        preset = random.choice(category_presets)

    print(f"[PRESET] {category} / {preset['name']}")

    params = {
        "prompt": preset["prompt"],
        "negative_prompt": preset.get("negative_prompt", DEFAULT_NEGATIVE),
        "width": preset.get("width", kwargs.get("width", 1920)),
        "height": preset.get("height", kwargs.get("height", 1080)),
        "steps": preset.get("steps", kwargs.get("steps", 30)),
        "cfg": preset.get("cfg", kwargs.get("cfg", 7)),
        "output_subdir": category,
        "filename_prefix": preset["name"].replace(" ", "_"),
    }
    params.update(kwargs)

    prompt = params.pop("prompt")
    return generate_image(prompt, **params)


def list_presets():
    """Print all available presets."""
    presets = load_presets()
    for category, items in presets.items():
        print(f"\n[{category.upper()}]")
        for p in items:
            print(f"  - {p['name']}: {p['prompt'][:70]}...")


# --- CLI Interface ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate.py prompt \"your prompt here\"")
        print("  python generate.py preset <category> [preset_name]")
        print("  python generate.py presets                          (list all)")
        print("  python generate.py models                           (list models)")
        print("  python generate.py status                           (check API)")
        print()
        print("Categories: frequency, mockup, social, abstract")
        sys.exit(0)

    command = sys.argv[1]

    if command == "status":
        if check_api():
            print("[OK] SD WebUI API is running at", SD_API_URL)
            models = get_models()
            print(f"  Models loaded: {len(models)}")
            for m in models:
                print(f"    - {m}")
        else:
            print("[OFFLINE] SD WebUI API not reachable at", SD_API_URL)

    elif command == "models":
        if check_api():
            for m in get_models():
                print(m)
        else:
            print("[OFFLINE] API not running")

    elif command == "presets":
        list_presets()

    elif command == "preset":
        if len(sys.argv) < 3:
            print("Usage: python generate.py preset <category> [preset_name]")
            sys.exit(1)
        category = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        generate_from_preset(category, name)

    elif command == "prompt":
        if len(sys.argv) < 3:
            print("Usage: python generate.py prompt \"your prompt here\"")
            sys.exit(1)
        prompt = " ".join(sys.argv[2:])
        generate_image(prompt)

    else:
        # Treat everything as a prompt
        prompt = " ".join(sys.argv[1:])
        generate_image(prompt)
