#!/usr/bin/env python3
"""
Instagram-Ready Reel Pipeline
Creates reels with word-by-word animated captions using PIL overlay compositing.

Usage:
    python3 instagram_pipeline.py grandmas-recipe-card
    python3 instagram_pipeline.py --all
    python3 instagram_pipeline.py --list
"""

import json
import subprocess
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# -- Config -------------------------------------------------------------------
PIPELINE_DIR = Path(__file__).parent
STORIES_DIR = PIPELINE_DIR / "stories"
OUTPUT_DIR = PIPELINE_DIR / "output"
MUSIC_DIR = PIPELINE_DIR / "music"
INSTAGRAM_DIR = PIPELINE_DIR / "instagram_ready"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
EFFECTS = ['zoom_in', 'zoom_out', 'pan', 'zoom_in', 'zoom_out']
MUSIC_VOLUME = 0.12

# Caption style
FONT_SIZE = 52
HIGHLIGHT_COLOR = (255, 221, 0)     # yellow - current word
SPOKEN_COLOR = (255, 255, 255)      # white - already spoken
UNSPOKEN_COLOR = (140, 140, 140)    # gray - not yet spoken
OUTLINE = (0, 0, 0)
OUTLINE_W = 3

# Encoding
CRF = "18"
PRESET = "slow"


def load_font():
    for p in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        if os.path.exists(p):
            return ImageFont.truetype(p, FONT_SIZE)
    return ImageFont.load_default(size=FONT_SIZE)


def outlined_text(draw, xy, text, font, fill):
    """Draw text with black outline."""
    x, y = xy
    for dx in range(-OUTLINE_W, OUTLINE_W + 1):
        for dy in range(-OUTLINE_W, OUTLINE_W + 1):
            if dx or dy:
                draw.text((x+dx, y+dy), text, font=font, fill=OUTLINE)
    draw.text(xy, text, font=font, fill=fill)


def make_caption_png(words, highlight_idx, font, out_path):
    """
    Render a 1080x1920 transparent PNG with word-by-word highlighted caption.
    Words before highlight_idx: white. Current word: yellow. After: gray.
    """
    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Word wrap into lines
    max_w = WIDTH - 120
    lines = []
    current_line = []
    for w in words:
        test = ' '.join(current_line + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_w and current_line:
            lines.append(current_line)
            current_line = [w]
        else:
            current_line.append(w)
    if current_line:
        lines.append(current_line)

    # Calculate layout
    line_h = FONT_SIZE + 16
    total_h = len(lines) * line_h
    y_start = HEIGHT - 260 - total_h

    # Semi-transparent background
    pad = 20
    draw.rounded_rectangle(
        [40, y_start - pad, WIDTH - 40, y_start + total_h + pad],
        radius=14, fill=(0, 0, 0, 140)
    )

    # Draw words
    global_idx = 0
    for line_words in lines:
        line_text = ' '.join(line_words)
        bbox = draw.textbbox((0, 0), line_text, font=font)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2
        y = y_start

        for word in line_words:
            if global_idx < highlight_idx:
                color = SPOKEN_COLOR
            elif global_idx == highlight_idx:
                color = HIGHLIGHT_COLOR
            else:
                color = UNSPOKEN_COLOR

            outlined_text(draw, (x, y), word, font, color)

            wbbox = draw.textbbox((0, 0), word + ' ', font=font)
            x += wbbox[2] - wbbox[0]
            global_idx += 1

        y_start += line_h

    img.save(out_path)


def ken_burns(img_path, out_path, duration, effect):
    """Ken Burns clip from static image."""
    z = 1.15
    frames = int(duration * FPS)

    if effect == 'zoom_in':
        zp = f"zoompan=z='min(zoom+0.0008,{z})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
    elif effect == 'zoom_out':
        zp = f"zoompan=z='if(eq(on,1),{z},max(zoom-0.0008,1))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
    else:
        zp = f"zoompan=z='{z}':x='if(eq(on,1),0,min(x+0.5,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"

    sw, sh = int(WIDTH * z), int(HEIGHT * z)
    vf = f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},{zp}"

    r = subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', str(img_path),
        '-vf', vf, '-t', str(duration),
        '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'fast',
        str(out_path)
    ], capture_output=True, text=True)
    return r.returncode == 0


def overlay_caption_on_clip(video_path, caption_png, out_path, duration):
    """Overlay a transparent PNG caption onto a video clip using FFmpeg overlay filter."""
    r = subprocess.run([
        'ffmpeg', '-y',
        '-i', str(video_path),
        '-loop', '1', '-i', str(caption_png),
        '-filter_complex',
        f'[1:v]format=rgba,fade=in:st=0:d=0.15:alpha=1[cap];'
        f'[0:v][cap]overlay=0:0:shortest=1[out]',
        '-map', '[out]',
        '-t', str(duration),
        '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
        str(out_path)
    ], capture_output=True, text=True)
    return r.returncode == 0


def process_story(story_name, force=False):
    """Full Instagram pipeline for a single story."""
    out_dir = OUTPUT_DIR / story_name
    story_file = STORIES_DIR / f"{story_name}.json"

    if not story_file.exists():
        print(f"[SKIP] No story JSON: {story_name}")
        return False

    timing_file = out_dir / "timing.json"
    narration_file = out_dir / "narration.wav"

    if not timing_file.exists() or not narration_file.exists():
        print(f"[SKIP] Missing timing/narration: {story_name}")
        return False

    with open(story_file) as f:
        story = json.load(f)
    num_scenes = len(story["scenes"])

    for i in range(num_scenes):
        if not (out_dir / f"scene_{i}.png").exists():
            print(f"[SKIP] Missing scene_{i}.png: {story_name}")
            return False

    INSTAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    final_output = INSTAGRAM_DIR / f"{story_name}.mp4"
    caption_output = INSTAGRAM_DIR / f"{story_name}_caption.txt"

    if final_output.exists() and not force:
        print(f"[SKIP] Done: {story_name}")
        return True

    print(f"\n{'='*60}")
    print(f"  {story_name}")
    print(f"{'='*60}")

    timing = json.load(open(timing_file))
    scenes = timing["scenes"]
    font = load_font()

    # -- Step 1: For each scene, generate per-word caption clips --
    # Strategy: For each scene, split into word segments.
    # Each word segment = Ken Burns clip + caption PNG overlay with that word highlighted.
    # This creates the word-by-word animation effect.

    print("\n[1/4] Creating captioned clips with word-by-word animation...")
    all_clips = []
    cap_dir = out_dir / "ig_caps"
    cap_dir.mkdir(exist_ok=True)

    for si, scene in enumerate(scenes):
        words = scene["text"].split()
        if not words:
            continue

        img = out_dir / f"scene_{si}.png"
        scene_dur = scene["duration"] + 0.5
        word_dur = scene_dur / len(words)
        effect = EFFECTS[si % len(EFFECTS)]

        print(f"  Scene {si}: {len(words)} words, {scene_dur:.1f}s, {effect}")

        # Create one Ken Burns clip for the whole scene
        kb_clip = out_dir / f"ig_kb_{si}.mp4"
        if not ken_burns(img, kb_clip, scene_dur, effect):
            print(f"  [FAIL] Ken Burns scene {si}")
            return False

        # Now split the Ken Burns clip into word segments with different caption overlays
        for wi, word in enumerate(words):
            cap_png = cap_dir / f"cap_{si}_{wi}.png"
            word_clip = out_dir / f"ig_word_{si}_{wi}.mp4"

            # Render caption PNG with this word highlighted
            make_caption_png(words, wi, font, cap_png)

            # Calculate timing within the scene clip
            word_start = wi * word_dur
            word_end = word_start + word_dur

            # Extract segment from Ken Burns clip and overlay caption
            r = subprocess.run([
                'ffmpeg', '-y',
                '-ss', f'{word_start:.3f}',
                '-i', str(kb_clip),
                '-loop', '1', '-i', str(cap_png),
                '-filter_complex',
                '[1:v]format=rgba[cap];[0:v][cap]overlay=0:0:shortest=1[out]',
                '-map', '[out]',
                '-t', f'{word_dur:.3f}',
                '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
                str(word_clip)
            ], capture_output=True, text=True)

            if r.returncode != 0:
                print(f"    [WARN] Word clip {si}:{wi} failed, using plain segment")
                # Fallback: just extract segment without caption
                subprocess.run([
                    'ffmpeg', '-y', '-ss', f'{word_start:.3f}',
                    '-i', str(kb_clip), '-t', f'{word_dur:.3f}',
                    '-c', 'copy', str(word_clip)
                ], capture_output=True)

            all_clips.append(word_clip)
            cap_png.unlink(missing_ok=True)

        # Remove full KB clip
        kb_clip.unlink(missing_ok=True)

    # -- Step 2: Concatenate all word clips --
    print(f"\n[2/4] Concatenating {len(all_clips)} clips...")
    concat_file = out_dir / "ig_concat.txt"
    with open(concat_file, 'w') as f:
        for c in all_clips:
            f.write(f"file '{c.resolve()}'\n")

    raw_video = out_dir / "ig_captioned.mp4"
    # Always re-encode to avoid stream mismatch issues with -c copy
    r = subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', str(concat_file),
            '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
            str(raw_video)
        ], capture_output=True, text=True)

    if r.returncode != 0:
        print(f"  [ERROR] Concat failed: {r.stderr[-300:]}")
        return False

    # -- Step 3: Add audio (narration + optional music) --
    print("\n[3/4] Adding audio...")
    bg_music = find_background_music()

    if bg_music:
        print(f"  Music: {bg_music.name}")
        r = subprocess.run([
            'ffmpeg', '-y',
            '-i', str(raw_video),
            '-i', str(bg_music),
            '-i', str(narration_file),
            '-filter_complex',
            f'[1:a]aloop=loop=-1:size=2e+09,atrim=0:{timing["total_duration"]+2},'
            f'volume={MUSIC_VOLUME}[music];'
            f'[2:a]volume=1.0[narr];'
            f'[music][narr]amix=inputs=2:duration=shortest[aout]',
            '-map', '0:v', '-map', '[aout]',
            '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.0',
            '-preset', PRESET, '-crf', CRF,
            '-pix_fmt', 'yuv420p', '-maxrate', '8M', '-bufsize', '16M',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
            '-shortest', '-movflags', '+faststart',
            str(final_output)
        ], capture_output=True, text=True)
    else:
        print("  No music (add .mp3/.m4a to music/)")
        r = subprocess.run([
            'ffmpeg', '-y',
            '-i', str(raw_video),
            '-i', str(narration_file),
            '-map', '0:v', '-map', '1:a',
            '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.0',
            '-preset', PRESET, '-crf', CRF,
            '-pix_fmt', 'yuv420p', '-maxrate', '8M', '-bufsize', '16M',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
            '-shortest', '-movflags', '+faststart',
            str(final_output)
        ], capture_output=True, text=True)

    if r.returncode != 0:
        print(f"  [ERROR] Audio mix: {r.stderr[-400:]}")
        return False

    # -- Step 4: Instagram caption text --
    print("\n[4/4] Instagram caption...")
    caption = make_ig_caption(story)
    with open(caption_output, 'w') as f:
        f.write(caption)

    # Cleanup
    for c in all_clips:
        c.unlink(missing_ok=True)
    concat_file.unlink(missing_ok=True)
    raw_video.unlink(missing_ok=True)
    # Clean cap dir
    import shutil
    shutil.rmtree(cap_dir, ignore_errors=True)

    size_mb = final_output.stat().st_size / (1024 * 1024)
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', str(final_output)
    ], capture_output=True, text=True)
    dur_s = 0
    if probe.returncode == 0:
        dur_s = float(json.loads(probe.stdout).get("format", {}).get("duration", 0))

    print(f"\n  DONE: {final_output.name} ({size_mb:.1f} MB, {dur_s:.1f}s)")
    return True


def find_background_music():
    if not MUSIC_DIR.exists():
        return None
    for ext in ['*.mp3', '*.m4a', '*.wav']:
        files = list(MUSIC_DIR.glob(ext))
        if files:
            return files[0]
    return None


def make_ig_caption(story):
    """Generate Instagram caption with hook and hashtags."""
    narration = story.get("narration", "")
    hook = narration.split(". ")[0] + "." if ". " in narration else narration[:100]

    return f"""{hook}

{narration}

---
Save this if it hit you. Share with someone who needs it.

#nostalgia #emotional #reels #relatable #feelings #growingup #memories
#storytime #realstories #innerchild #healing #remember
#latinx #familia #culture #puertorican #boricua""".strip()


def list_inventory():
    print(f"\n{'='*70}")
    print(f"  REEL PIPELINE INVENTORY")
    print(f"{'='*70}")
    print(f"{'Story':<35} {'Imgs':>5} {'TTS':>4} {'IG':>4}")
    print(f"{'-'*70}")

    stories = sorted(STORIES_DIR.glob("*.json"))
    ready = done = 0

    for sf in stories:
        name = sf.stem
        out = OUTPUT_DIR / name
        ig = INSTAGRAM_DIR / f"{name}.mp4"

        imgs = len(list(out.glob("scene_*.png"))) if out.exists() else 0
        has_tts = (out / "narration.wav").exists() if out.exists() else False
        has_ig = ig.exists()

        with open(sf) as f:
            expected = len(json.load(f).get("scenes", []))

        img_str = f"{imgs}/{expected}" if imgs < expected else f" {imgs}"
        tts_str = "Y" if has_tts else "n"
        ig_str = "Y" if has_ig else "n"

        if imgs >= expected and has_tts:
            ready += 1
        if has_ig:
            done += 1

        print(f"  {name:<33} {img_str:>5} {tts_str:>4} {ig_str:>4}")

    print(f"{'-'*70}")
    print(f"  Ready: {ready}/{len(stories)}  |  IG done: {done}/{len(stories)}")


def process_all(force=False):
    stories = sorted(STORIES_DIR.glob("*.json"))
    ok = fail = 0
    for sf in stories:
        r = process_story(sf.stem, force=force)
        if r:
            ok += 1
        elif (OUTPUT_DIR / sf.stem / "timing.json").exists():
            fail += 1
    print(f"\n  BATCH: {ok} done, {fail} failed")


if __name__ == "__main__":
    os.chdir(PIPELINE_DIR)
    if len(sys.argv) < 2:
        print("Usage: python3 instagram_pipeline.py <story|--all|--list>")
        sys.exit(1)

    arg = sys.argv[1]
    force = "--force" in sys.argv

    if arg == "--list":
        list_inventory()
    elif arg == "--all":
        process_all(force=force)
    else:
        process_story(arg, force=force)
