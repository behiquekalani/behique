#!/usr/bin/env python3
"""
Remote image generation via Hutia (192.168.0.152:9879).
SDXL Turbo on GTX 1050 Ti. Returns PNG bytes.

Usage:
    from remote_image_gen import generate_remote, is_hutia_available

    if is_hutia_available():
        success = generate_remote("a sunset over the ocean", "output.png")
"""
import urllib.request
import urllib.error
import json
import time

HUTIA_URL = "http://192.168.0.152:9879"


def is_hutia_available(timeout=2):
    """Check if Hutia image gen server is reachable."""
    try:
        req = urllib.request.Request(HUTIA_URL, method="GET")
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read())
        return data.get("ok", False)
    except Exception:
        return False


def generate_remote(prompt, output_path, width=768, height=1024, steps=4):
    """Generate an image on Hutia and save to output_path. Returns True on success."""
    payload = json.dumps({
        "prompt": prompt,
        "width": width,
        "height": height,
        "steps": steps,
    }).encode("utf-8")

    start = time.time()
    try:
        req = urllib.request.Request(
            f"{HUTIA_URL}/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=300)  # 5 min timeout for gen
        png_data = resp.read()

        if len(png_data) < 100:
            print(f"    [HUTIA] Response too small ({len(png_data)} bytes), likely error")
            return False

        with open(output_path, "wb") as f:
            f.write(png_data)

        elapsed = time.time() - start
        size_kb = len(png_data) / 1024
        print(f"    [HUTIA] Generated in {elapsed:.0f}s ({size_kb:.0f}KB)")
        return True

    except urllib.error.URLError as e:
        elapsed = time.time() - start
        print(f"    [HUTIA] Network error after {elapsed:.0f}s: {e}")
        return False
    except Exception as e:
        elapsed = time.time() - start
        print(f"    [HUTIA] Error after {elapsed:.0f}s: {e}")
        return False


if __name__ == "__main__":
    import sys
    if is_hutia_available():
        print("Hutia image gen: ONLINE")
        if len(sys.argv) > 1:
            prompt = " ".join(sys.argv[1:])
            print(f"Generating: {prompt}")
            success = generate_remote(prompt, "hutia_test.png")
            print(f"Success: {success}")
    else:
        print("Hutia image gen: OFFLINE")
