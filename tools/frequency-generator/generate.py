#!/usr/bin/env python3
"""
Frequency / Manifestation Video Generator
Generates 2-hour YouTube videos: ambient sounds + glowing angel number images + subliminal affirmations.
Style reference: @inoneness channel.

Requirements: PIL/Pillow, FFmpeg installed on system.
Designed to run on Cobo (Windows, GTX 1080 Ti).
"""

import json
import math
import os
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

# Paths
BASE_DIR = Path(__file__).parent
THEMES_FILE = BASE_DIR / "themes.json"
AFFIRMATIONS_FILE = BASE_DIR / "affirmations.json"
SOUNDS_DIR = BASE_DIR / "sounds"
OUTPUT_DIR = BASE_DIR / "output"

# Video settings
WIDTH = 1920
HEIGHT = 1080
DURATION_SECONDS = 7200  # 2 hours
FPS = 1  # static image, 1 fps is enough


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_glow_image(number, color_hex, output_path):
    """Create a 1920x1080 image with glowing angel number and star particles."""
    color_rgb = hex_to_rgb(color_hex)
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scatter star/particle dots across background
    random.seed(int(number) + 42)
    for _ in range(300):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        brightness = random.randint(30, 120)
        size = random.choice([1, 1, 1, 2])
        star_color = (
            min(255, color_rgb[0] // 4 + brightness),
            min(255, color_rgb[1] // 4 + brightness),
            min(255, color_rgb[2] // 4 + brightness),
        )
        if size == 1:
            draw.point((x, y), fill=star_color)
        else:
            draw.ellipse([x, y, x + size, y + size], fill=star_color)

    # Add subtle radial gradient vignette from center
    gradient = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    cx, cy = WIDTH // 2, HEIGHT // 2
    max_radius = int(math.sqrt(cx**2 + cy**2))
    for r in range(0, min(400, max_radius), 2):
        alpha = max(0, int(40 * (1 - r / 400)))
        grad_draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(color_rgb[0], color_rgb[1], color_rgb[2], alpha),
        )
    img.paste(Image.alpha_composite(img.convert("RGBA"), gradient).convert("RGB"))

    # Try to load a large font, fall back to default
    font_size = 200
    font = None
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                continue
    if font is None:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    text = number

    # Measure text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    text_x = (WIDTH - tw) // 2
    text_y = (HEIGHT - th) // 2

    # Create glow effect: draw text on separate layer, blur it, composite
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    # Multiple glow passes at decreasing opacity
    for blur_radius, opacity_mult in [(30, 0.3), (20, 0.4), (10, 0.6)]:
        temp = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        glow_color = (
            color_rgb[0],
            color_rgb[1],
            color_rgb[2],
            int(255 * opacity_mult),
        )
        temp_draw.text((text_x, text_y), text, font=font, fill=glow_color)
        temp = temp.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        glow_layer = Image.alpha_composite(glow_layer, temp)

    # Draw the sharp text on top
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.text(
        (text_x, text_y),
        text,
        font=font,
        fill=(color_rgb[0], color_rgb[1], color_rgb[2], 255),
    )

    # Composite glow onto base
    final = Image.alpha_composite(img.convert("RGBA"), glow_layer)
    final.convert("RGB").save(output_path, quality=95)
    print(f"[IMAGE] Saved: {output_path}")
    return output_path


def find_ambient_sound():
    """Pick a random ambient sound from the sounds/ directory."""
    if not SOUNDS_DIR.exists():
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
        return None

    sound_files = [
        f for f in SOUNDS_DIR.iterdir()
        if f.suffix.lower() in (".mp3", ".wav", ".ogg", ".m4a", ".flac")
    ]
    if not sound_files:
        return None
    return random.choice(sound_files)


def generate_affirmation_text(theme_meaning):
    """Pick affirmations matching the theme meaning and return as text."""
    affirmations = load_json(AFFIRMATIONS_FILE)

    # Map theme meanings to affirmation categories
    meaning_map = {
        "new beginnings": "success",
        "balance and harmony": "love",
        "abundance": "abundance",
        "protection and guidance": "confidence",
        "transformation": "success",
        "self-love and healing": "health",
        "divine luck": "abundance",
        "infinite wealth": "abundance",
        "completion and ascension": "confidence",
    }

    category = meaning_map.get(theme_meaning, random.choice(list(affirmations.keys())))
    selected = affirmations.get(category, affirmations["abundance"])
    random.shuffle(selected)
    return selected


def generate_affirmation_audio(affirmations, output_path):
    """Try to generate TTS audio from affirmations. Falls back gracefully."""
    text = ". ".join(affirmations)

    # Try espeak first (common on Linux/Windows)
    for tts_cmd in ["espeak", "espeak-ng"]:
        try:
            subprocess.run(
                [tts_cmd, "-w", str(output_path), "-s", "120", "-p", "30", text],
                check=True,
                capture_output=True,
                timeout=120,
            )
            print(f"[TTS] Generated affirmations audio with {tts_cmd}")
            return output_path
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue

    # Try piper
    try:
        process = subprocess.run(
            ["piper", "--model", "en_US-lessac-medium", "--output_file", str(output_path)],
            input=text,
            text=True,
            check=True,
            capture_output=True,
            timeout=120,
        )
        print(f"[TTS] Generated affirmations audio with piper")
        return output_path
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    print("[TTS] No TTS engine found. Skipping affirmation audio.")
    print("      Install espeak or piper for subliminal affirmations.")
    return None


def check_ffmpeg():
    """Verify FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ERROR: FFmpeg not found. Install it: https://ffmpeg.org/download.html")
        return False


def generate_video(image_path, ambient_path, affirmation_path, output_path):
    """Use FFmpeg to combine image + audio into a 2-hour video."""
    if not check_ffmpeg():
        sys.exit(1)

    cmd = ["ffmpeg", "-y"]

    # Input: loop image for 2 hours
    cmd += ["-loop", "1", "-i", str(image_path), "-t", str(DURATION_SECONDS)]

    # Input: ambient sound (loop if shorter than 2 hours)
    if ambient_path:
        cmd += ["-stream_loop", "-1", "-i", str(ambient_path), "-t", str(DURATION_SECONDS)]

    # Input: affirmation audio (loop and mix at low volume)
    if affirmation_path and os.path.exists(affirmation_path):
        cmd += ["-stream_loop", "-1", "-i", str(affirmation_path), "-t", str(DURATION_SECONDS)]

    # Build filter complex for audio mixing
    audio_inputs = []
    filter_parts = []
    input_idx = 1  # 0 is the image

    if ambient_path:
        audio_inputs.append(f"[{input_idx}:a]")
        filter_parts.append(f"[{input_idx}:a]volume=1.0[ambient]")
        input_idx += 1

    if affirmation_path and os.path.exists(affirmation_path):
        filter_parts.append(f"[{input_idx}:a]volume=0.1[affirm]")
        input_idx += 1

    if len(filter_parts) == 2:
        # Mix ambient + affirmations
        filter_complex = (
            f"{filter_parts[0]}; {filter_parts[1]}; "
            f"[ambient][affirm]amix=inputs=2:duration=first[aout]"
        )
        cmd += ["-filter_complex", filter_complex, "-map", "0:v", "-map", "[aout]"]
    elif len(filter_parts) == 1:
        if ambient_path:
            cmd += ["-map", "0:v", "-map", "1:a"]
        else:
            cmd += ["-map", "0:v", "-map", "1:a"]
    else:
        # No audio at all, generate silent
        cmd += ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-t", str(DURATION_SECONDS)]
        cmd += ["-map", "0:v", "-map", f"{input_idx}:a"]

    # Output settings
    cmd += [
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path),
    ]

    print(f"[FFMPEG] Rendering video (this will take a while)...")
    print(f"[FFMPEG] Command: {' '.join(str(c) for c in cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=14400)  # 4 hour timeout

    if result.returncode != 0:
        print(f"[FFMPEG] Error:\n{result.stderr[-2000:]}")
        sys.exit(1)

    print(f"[VIDEO] Saved: {output_path}")
    return output_path


def generate_metadata(number, theme_data, affirmations, video_path):
    """Generate YouTube metadata JSON."""
    today = datetime.now().strftime("%Y-%m-%d")

    title = theme_data["title"].format(number=number, meaning=theme_data["meaning"].title())

    description_lines = [
        f"{number} Hz Frequency - {theme_data['meaning'].title()} Manifestation",
        "",
        f"Listen to this {number} frequency for deep manifestation, healing, and spiritual alignment.",
        f"Best experienced with headphones. Let the frequency wash over you.",
        "",
        "Subliminal affirmations embedded in this track:",
        "",
    ]
    for aff in affirmations:
        description_lines.append(f"- {aff}")

    description_lines += [
        "",
        f"Angel Number {number} Meaning: {theme_data['meaning'].title()}",
        "",
        "Listen while sleeping, meditating, studying, or working.",
        "Allow the vibration to align your energy with the universe.",
        "",
        f"#angelnumber #{number} #frequency #manifestation #subliminal #meditation",
        f"#{theme_data['meaning'].replace(' ', '')} #healing #spiritualawakening",
    ]

    tags = [
        number, f"{number} hz", f"{number} frequency",
        "angel number", "manifestation", "subliminal affirmations",
        "meditation music", "sleep music", "healing frequency",
        "law of attraction", "spiritual awakening",
    ] + theme_data["keywords"]

    metadata = {
        "title": title,
        "description": "\n".join(description_lines),
        "tags": tags,
        "category": "10",  # Music
        "privacy": "public",
        "video_path": str(video_path),
        "number": number,
        "theme": theme_data["meaning"],
        "generated_at": today,
    }

    meta_path = video_path.with_suffix(".json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[META] Saved: {meta_path}")
    return meta_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Frequency / Manifestation Video Generator")
    parser.add_argument("--number", type=str, default=None,
                        help="Specific angel number to generate (e.g. 111, 222, 888)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Pick angel number (specific or random)
    themes = load_json(THEMES_FILE)
    if args.number:
        number = args.number
        if number not in themes:
            print(f"ERROR: Number {number} not found in themes.json. Available: {', '.join(themes.keys())}")
            sys.exit(1)
    else:
        number = random.choice(list(themes.keys()))
    theme = themes[number]
    print(f"\n{'='*60}")
    print(f"  FREQUENCY GENERATOR - Angel Number {number}")
    print(f"  Theme: {theme['meaning'].title()}")
    print(f"  Color: {theme['color']}")
    print(f"{'='*60}\n")

    today = datetime.now().strftime("%Y%m%d")
    base_name = f"{number}-{theme['meaning'].replace(' ', '-')}-{today}"

    # Step 2: Generate glowing image
    image_path = OUTPUT_DIR / f"{base_name}.png"
    generate_glow_image(number, theme["color"], image_path)

    # Step 3: Find ambient sound
    ambient_path = find_ambient_sound()
    if ambient_path:
        print(f"[SOUND] Using: {ambient_path.name}")
    else:
        print("[SOUND] No ambient sounds found in sounds/ directory.")
        print("        Video will use generated silence.")
        print("        Add .mp3/.wav files to sounds/ for ambient background.")

    # Step 4: Generate affirmation audio
    affirmations = generate_affirmation_text(theme["meaning"])
    affirmation_audio = OUTPUT_DIR / f"{base_name}-affirmations.wav"
    affirmation_path = generate_affirmation_audio(affirmations, affirmation_audio)

    # Step 5: Render video with FFmpeg
    video_path = OUTPUT_DIR / f"{base_name}.mp4"
    generate_video(image_path, ambient_path, affirmation_path, video_path)

    # Step 6: Generate YouTube metadata
    meta_path = generate_metadata(number, theme, affirmations, video_path)

    print(f"\n{'='*60}")
    print(f"  DONE!")
    print(f"  Video: {video_path}")
    print(f"  Metadata: {meta_path}")
    print(f"{'='*60}\n")

    return str(meta_path)


if __name__ == "__main__":
    meta = main()
    print(meta)
