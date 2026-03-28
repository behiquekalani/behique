#!/usr/bin/env python3
"""
AI Image-to-Video generation via fal.ai API.
Supports Kling, Luma, and Hailuo/MiniMax models.
Pay-as-you-go, no subscription needed.

Setup:
    pip install fal-client
    export FAL_KEY="your-api-key-here"

Usage:
    from video_gen import generate_video, is_available

    if is_available():
        success = generate_video("scene.png", "scene.mp4", prompt="gentle camera drift")
"""
import os
import time
import json

FAL_KEY = os.environ.get("FAL_KEY", "")

# Model configs: name -> (fal model ID, default duration, cost estimate)
MODELS = {
    "kling": {
        "model_id": "fal-ai/kling-video/v2/master/image-to-video",
        "duration": 5,
        "cost_per_clip": 0.35,
    },
    "kling-turbo": {
        "model_id": "fal-ai/kling-video/v2.5/turbo-pro/image-to-video",
        "duration": 5,
        "cost_per_clip": 0.35,
    },
    "hailuo": {
        "model_id": "fal-ai/minimax/video-01/image-to-video",
        "duration": 6,
        "cost_per_clip": 0.05,
    },
    "luma": {
        "model_id": "fal-ai/luma-dream-machine/ray-2/image-to-video",
        "duration": 5,
        "cost_per_clip": 0.20,
    },
}

DEFAULT_MODEL = "hailuo"


def is_available():
    """Check if fal.ai API key is configured."""
    return bool(FAL_KEY)


def generate_video(image_path, output_path, prompt="", model=None, duration=None):
    """
    Generate a video clip from a still image using fal.ai.

    Args:
        image_path: Path to input image (PNG/JPG)
        output_path: Path for output video (MP4)
        prompt: Motion/style prompt (e.g. "slow zoom in, gentle wind")
        model: Model key from MODELS dict (default: kling-turbo)
        duration: Video duration in seconds (default: model default)

    Returns:
        True on success, False on failure
    """
    try:
        import fal_client
    except ImportError:
        print("    [VIDEO] fal-client not installed. Run: pip install fal-client")
        return False

    if not FAL_KEY:
        print("    [VIDEO] FAL_KEY not set. Get one at https://fal.ai/dashboard/keys")
        return False

    model_key = model or DEFAULT_MODEL
    model_config = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
    model_id = model_config["model_id"]
    vid_duration = duration or model_config["duration"]

    # Read image and encode as data URI
    import base64
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    img_uri = f"data:{mime};base64,{img_b64}"

    # Build request
    request_input = {
        "image_url": img_uri,
        "prompt": prompt or "cinematic, slow gentle camera movement, atmospheric",
        "duration": str(vid_duration),
    }

    start = time.time()
    print(f"    [VIDEO] Generating {vid_duration}s clip via {model_key}...")

    try:
        # Submit and poll for result
        result = fal_client.subscribe(
            model_id,
            arguments=request_input,
            with_logs=False,
        )

        # Extract video URL from result
        video_url = None
        if isinstance(result, dict):
            video_url = result.get("video", {}).get("url") or result.get("video_url")
            if not video_url and "video" in result:
                v = result["video"]
                if isinstance(v, str):
                    video_url = v
                elif isinstance(v, dict):
                    video_url = v.get("url", v.get("file_url", ""))

        if not video_url:
            elapsed = time.time() - start
            print(f"    [VIDEO] No video URL in response after {elapsed:.0f}s")
            print(f"    [VIDEO] Response keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
            return False

        # Download the video
        import urllib.request
        urllib.request.urlretrieve(video_url, output_path)

        elapsed = time.time() - start
        size_kb = os.path.getsize(output_path) / 1024
        print(f"    [VIDEO] Done in {elapsed:.0f}s ({size_kb:.0f}KB) ~${model_config['cost_per_clip']:.2f}")
        return True

    except Exception as e:
        elapsed = time.time() - start
        print(f"    [VIDEO] Error after {elapsed:.0f}s: {e}")
        return False


def estimate_cost(num_clips, model=None):
    """Estimate total cost for a batch of clips."""
    model_key = model or DEFAULT_MODEL
    config = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
    total = num_clips * config["cost_per_clip"]
    return total


if __name__ == "__main__":
    import sys

    if not is_available():
        print("FAL_KEY not set. Get your API key at https://fal.ai/dashboard/keys")
        print("Then: export FAL_KEY='your-key-here'")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python3 video_gen.py <image.png> [output.mp4] [--model kling|hailuo|luma]")
        print(f"\nAvailable models:")
        for name, cfg in MODELS.items():
            print(f"  {name}: ~${cfg['cost_per_clip']:.2f}/clip, {cfg['duration']}s")
        print(f"\nDefault: {DEFAULT_MODEL}")
        sys.exit(0)

    image = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "output_video.mp4"

    model = DEFAULT_MODEL
    for i, arg in enumerate(sys.argv):
        if arg == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]

    print(f"Image: {image}")
    print(f"Output: {output}")
    print(f"Model: {model} (~${MODELS.get(model, MODELS[DEFAULT_MODEL])['cost_per_clip']:.2f})")

    success = generate_video(image, output, model=model)
    print(f"\nSuccess: {success}")
