#!/usr/bin/env python3
"""
Instagram-Ready Reel Compositor
- Animated word-by-word captions (trending style)
- Background music mixed under narration
- Instagram-optimized H.264 encoding (1080x1920, AAC 44.1kHz)
- Ken Burns camera motion on stills

Usage:
    python3 instagram_compose.py story-name
    python3 instagram_compose.py --all          # compose all stories with images
    python3 instagram_compose.py --batch N      # compose N stories
"""
import json, subprocess, os, sys, tempfile, math, struct, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PIPELINE_DIR = Path(__file__).parent
OUTPUT_DIR = PIPELINE_DIR / "output"
MUSIC_DIR = PIPELINE_DIR / "music"
FPS = 30
WIDTH = 1080
HEIGHT = 1920


def get_font(size=52):
    """Get a clean font for captions."""
    font_paths = [
        "/System/Library/Fonts/SFCompact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default(size=size)


def word_wrap(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current = []
    for w in words:
        test = ' '.join(current + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(' '.join(current))
            current = [w]
        else:
            current.append(w)
    if current:
        lines.append(' '.join(current))
    return lines


def render_caption_frame(width, height, words, word_timings, current_time, font):
    """Render yellow film-style captions with word-by-word pop-in animation."""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Yellow film palette
    YELLOW_ACTIVE = (255, 215, 0, 255)       # Gold yellow -- current word
    YELLOW_SPOKEN = (255, 235, 120, 220)      # Soft yellow -- already spoken
    YELLOW_UPCOMING = (255, 235, 120, 100)    # Faint yellow -- not yet spoken
    OUTLINE_COLOR = (0, 0, 0, 220)            # Black outline for readability

    # Find visible words at current_time
    visible_words = []
    active_idx = -1
    for i, wt in enumerate(word_timings):
        if wt['start'] <= current_time < wt['start'] + 2.5:
            visible_words.append(i)
        if wt['start'] <= current_time < wt.get('end', wt['start'] + 0.5):
            active_idx = i

    if not visible_words:
        return overlay

    start_idx = min(visible_words)
    end_idx = max(visible_words)

    # Show a window of words (max ~10 for readability)
    window_size = 10
    if active_idx >= 0:
        window_start = max(0, active_idx - 3)
        window_end = min(len(word_timings), window_start + window_size)
        window_end = min(window_end, end_idx + 1)
        window_start = max(0, window_end - window_size)
    else:
        window_start = start_idx
        window_end = min(start_idx + window_size, end_idx + 1)

    display_words = word_timings[window_start:window_end]
    if not display_words:
        return overlay

    # Build text and wrap
    text = ' '.join(w['word'] for w in display_words)
    max_text_width = width - 140
    lines = word_wrap(text, font, max_text_width, draw)

    # Position: bottom third, above safe area
    line_height = font.size + 14
    block_height = len(lines) * line_height
    y_start = height - 380 - block_height

    # Semi-transparent dark backdrop (subtle, film-style)
    padding = 24
    draw.rounded_rectangle(
        [50, y_start - padding, width - 50, y_start + block_height + padding],
        radius=12,
        fill=(0, 0, 0, 120)
    )

    # Draw each word with film-style yellow highlighting
    word_idx_in_display = 0
    for line_num, line in enumerate(lines):
        line_words = line.split()
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        x = (width - line_width) // 2
        y = y_start + line_num * line_height

        for lw in line_words:
            if word_idx_in_display < len(display_words):
                wt = display_words[word_idx_in_display]
                word_age = current_time - wt['start']
                is_active = (wt['start'] <= current_time < wt.get('end', wt['start'] + 0.4))
                is_past = current_time >= wt.get('end', wt['start'] + 0.4)

                # Pop-in: slight vertical offset that settles (first 0.15s)
                y_offset = 0
                if word_age >= 0 and word_age < 0.15:
                    pop_progress = word_age / 0.15
                    y_offset = int(6 * (1.0 - pop_progress))

                # Black outline (2px stroke) for all words
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if abs(dx) + abs(dy) > 0:
                            draw.text((x + dx, y + dy + y_offset), lw, fill=OUTLINE_COLOR, font=font)

                if is_active:
                    # Active: bright gold yellow, thicker outline for emphasis
                    draw.text((x, y + y_offset), lw, fill=YELLOW_ACTIVE, font=font)
                elif is_past:
                    # Spoken: soft yellow
                    draw.text((x, y), lw, fill=YELLOW_SPOKEN, font=font)
                else:
                    # Upcoming: faint yellow
                    draw.text((x, y), lw, fill=YELLOW_UPCOMING, font=font)
            else:
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if abs(dx) + abs(dy) > 0:
                            draw.text((x + dx, y + dy), lw, fill=OUTLINE_COLOR, font=font)
                draw.text((x, y), lw, fill=YELLOW_UPCOMING, font=font)

            word_idx_in_display += 1
            w_bbox = draw.textbbox((0, 0), lw + ' ', font=font)
            x += w_bbox[2] - w_bbox[0]

    return overlay


def estimate_word_timings(narration_text, total_duration):
    """Estimate word timings from narration text and total duration."""
    words = narration_text.split()
    if not words:
        return []

    # Simple proportional timing based on character count
    total_chars = sum(len(w) for w in words)
    if total_chars == 0:
        return []

    # Add small padding at start/end
    start_pad = 0.3
    end_pad = 0.5
    available = total_duration - start_pad - end_pad

    timings = []
    current_time = start_pad
    for w in words:
        char_ratio = len(w) / total_chars
        word_dur = max(0.15, available * char_ratio)
        timings.append({
            'word': w,
            'start': current_time,
            'end': current_time + word_dur,
        })
        current_time += word_dur

    return timings


def generate_bg_music(duration, output_path, bpm=72):
    """Generate ambient background music - soft piano-like tones."""
    sample_rate = 44100
    num_samples = int(duration * sample_rate)

    # Ambient chord progression (Am - F - C - G) in soft sine waves
    chords = [
        [220.0, 261.63, 329.63],   # Am
        [174.61, 220.0, 261.63],   # F
        [261.63, 329.63, 392.0],   # C
        [196.0, 246.94, 293.66],   # G
    ]

    beat_duration = 60.0 / bpm
    chord_duration = beat_duration * 4  # 4 beats per chord

    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        chord_idx = int(t / chord_duration) % len(chords)
        chord = chords[chord_idx]

        # Position within chord for envelope
        chord_pos = (t % chord_duration) / chord_duration

        # Soft attack/release envelope
        env = min(chord_pos * 4, 1.0) * max(0, 1.0 - max(0, chord_pos - 0.7) * 3.33)

        sample = 0.0
        for freq in chord:
            sample += math.sin(2 * math.pi * freq * t) * 0.15
            # Add soft overtone
            sample += math.sin(2 * math.pi * freq * 2 * t) * 0.03

        sample *= env * 0.3  # Keep it quiet

        # Clamp
        sample = max(-1.0, min(1.0, sample))
        samples.append(sample)

    # Write WAV
    with wave.open(str(output_path), 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for s in samples:
            wav.writeframes(struct.pack('<h', int(s * 32767)))

    return output_path


def compose_instagram_reel(story_name, force=False):
    """Compose a full Instagram-ready reel from pre-generated assets."""
    story_json = PIPELINE_DIR / "stories" / f"{story_name}.json"

    # Detect if this is a translated story (e.g. "the-lunchbox-note_es")
    # Translated stories share images with their base story
    base_name = story_name
    story_lang = "en"
    for lang_code in ["_es", "_pt", "_fr"]:
        if story_name.endswith(lang_code):
            base_name = story_name[:-len(lang_code)]
            story_lang = lang_code[1:]
            break

    story_dir = OUTPUT_DIR / story_name
    base_dir = OUTPUT_DIR / base_name  # Where images live
    final_output = OUTPUT_DIR / f"{story_name}_instagram.mp4"

    if final_output.exists() and not force:
        print(f"[SKIP] {story_name} already composed")
        return str(final_output)

    # Setup output dir for translated stories
    story_dir.mkdir(exist_ok=True)

    # Generate narration if missing (for translated stories)
    narration = story_dir / "narration.wav"
    if not narration.exists() and story_lang != "en":
        if story_json.exists():
            with open(story_json) as f:
                ts = json.load(f)
            narration_text = ts.get("narration", " ".join(s["text"] for s in ts.get("scenes", [])))
            voice = ts.get("voice", "ef_dora" if story_lang == "es" else "pf_dora")
            print(f"[TTS] Generating {story_lang.upper()} narration with voice {voice}...")
            try:
                import kokoro_onnx
                import soundfile as sf
                kokoro = kokoro_onnx.Kokoro(
                    str(PIPELINE_DIR / "kokoro-v1.0.onnx"),
                    str(PIPELINE_DIR / "voices-v1.0.bin")
                )
                samples, sample_rate = kokoro.create(narration_text, voice=voice, speed=0.9)
                sf.write(str(narration), samples, sample_rate)
                dur = len(samples) / sample_rate
                print(f"[TTS] Generated {dur:.1f}s {story_lang.upper()} narration")
            except Exception as e:
                print(f"[ERROR] TTS failed: {e}")
                return None

    if not narration.exists():
        print(f"[ERROR] No narration for {story_name}")
        return None

    # Check images (use base story images for translations)
    images = sorted(base_dir.glob("scene_*.png"))
    images = [img for img in images if '_sub' not in img.name and '_cap' not in img.name]
    if len(images) < 3:
        print(f"[ERROR] Only {len(images)} images for {base_name}, need at least 3")
        return None

    # Load story data
    with open(story_json) as f:
        story = json.load(f)

    print(f"\n{'='*60}")
    print(f"  INSTAGRAM REEL: {story.get('title', story_name)}")
    print(f"{'='*60}")

    # Get narration duration
    duration = float(subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(narration)],
        capture_output=True, text=True
    ).stdout.strip())

    print(f"[INFO] Duration: {duration:.1f}s, Scenes: {len(images)}")

    # Calculate per-scene timing
    scene_duration = duration / len(images)
    narration_text = story.get("narration", " ".join(s["text"] for s in story["scenes"]))

    # Estimate word timings for animated captions
    word_timings = estimate_word_timings(narration_text, duration)

    # Get caption font
    caption_font = get_font(48)

    # Check if AI video generation is available
    use_ai_video = False
    video_model = os.environ.get("REEL_VIDEO_MODEL", "kling-turbo")
    try:
        from video_gen import is_available as video_available, generate_video
        use_ai_video = video_available()
        if use_ai_video:
            from video_gen import estimate_cost, MODELS
            model_info = MODELS.get(video_model, MODELS["kling-turbo"])
            print(f"[VIDEO] AI video enabled: {video_model} (~${model_info['cost_per_clip']:.2f}/clip)")
    except ImportError:
        pass

    if not use_ai_video:
        print("[VIDEO] AI video not available (no FAL_KEY), using Ken Burns fallback")

    # Process each scene
    effects = ['zoom_in', 'zoom_out', 'pan', 'zoom_in', 'zoom_out']
    scene_clips = []

    for i, img_path in enumerate(images):
        scene_start = i * scene_duration
        scene_end = scene_start + scene_duration
        dur = scene_duration + 0.3  # Slight overlap for smooth transitions
        scene_text = story["scenes"][i]["text"] if i < len(story.get("scenes", [])) else ""

        clip_path = story_dir / f"ig_clip_{i}.mp4"
        ai_video_path = story_dir / f"ai_video_{i}.mp4"
        used_ai = False

        # Try AI video generation first
        if use_ai_video and not ai_video_path.exists():
            motion_prompt = f"cinematic slow camera movement, emotional atmosphere, {scene_text[:80]}"
            print(f"[SCENE {i+1}/{len(images)}] AI video: {motion_prompt[:60]}...")
            success = generate_video(
                str(img_path), str(ai_video_path),
                prompt=motion_prompt, model=video_model
            )
            if success:
                used_ai = True
            else:
                print(f"[SCENE {i+1}] AI video failed, falling back to Ken Burns")
        elif use_ai_video and ai_video_path.exists():
            print(f"[SCENE {i+1}/{len(images)}] AI video cached, reusing")
            used_ai = True

        if used_ai:
            # Scale AI video to reel dimensions and trim to scene duration
            print(f"[SCENE {i+1}/{len(images)}] Processing AI video clip...")
            scaled_video = story_dir / f"ai_scaled_{i}.mp4"
            subprocess.run([
                'ffmpeg', '-y', '-i', str(ai_video_path),
                '-vf', f'scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT}',
                '-t', str(dur), '-an', '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264', '-preset', 'fast',
                str(scaled_video)
            ], capture_output=True, check=True)

            # Overlay captions onto AI video
            cap_dir = story_dir / f"cap_frames_{i}"
            cap_dir.mkdir(exist_ok=True)

            num_frames = int(dur * FPS)

            # Extract frames from AI video
            subprocess.run([
                'ffmpeg', '-y', '-i', str(scaled_video),
                '-vf', f'fps={FPS}',
                str(cap_dir / 'vframe_%04d.png')
            ], capture_output=True, check=True)

            # Composite captions onto each video frame
            video_frames = sorted(cap_dir.glob("vframe_*.png"))
            for frame_idx in range(min(num_frames, len(video_frames))):
                t = scene_start + (frame_idx / FPS)
                caption_overlay = render_caption_frame(
                    WIDTH, HEIGHT, [], word_timings, t, caption_font
                )
                frame = Image.open(video_frames[frame_idx]).convert('RGBA')
                frame = Image.alpha_composite(frame, caption_overlay)
                frame = frame.convert('RGB')
                frame.save(cap_dir / f"frame_{frame_idx:04d}.png")

            # Compile captioned frames back to video
            subprocess.run([
                'ffmpeg', '-y', '-framerate', str(FPS),
                '-i', str(cap_dir / 'frame_%04d.png'),
                '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
                str(clip_path)
            ], capture_output=True, check=True)

            # Cleanup
            for f in cap_dir.glob("*.png"):
                f.unlink()
            cap_dir.rmdir()
            if scaled_video.exists():
                scaled_video.unlink()

        else:
            # Ken Burns fallback
            print(f"[SCENE {i+1}/{len(images)}] {dur:.1f}s, effect={effects[i % len(effects)]}")

            img = Image.open(img_path).convert('RGB')
            img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)

            cap_dir = story_dir / f"cap_frames_{i}"
            cap_dir.mkdir(exist_ok=True)

            num_frames = int(dur * FPS)
            for frame_idx in range(num_frames):
                t = scene_start + (frame_idx / FPS)
                caption_overlay = render_caption_frame(
                    WIDTH, HEIGHT, [], word_timings, t, caption_font
                )
                frame = img.copy().convert('RGBA')
                frame = Image.alpha_composite(frame, caption_overlay)
                frame = frame.convert('RGB')
                frame.save(cap_dir / f"frame_{frame_idx:04d}.png")

            effect = effects[i % len(effects)]
            zoom_factor = 1.12

            if effect == 'zoom_in':
                zp = f"zoompan=z='min(zoom+0.0006,{zoom_factor})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={num_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
            elif effect == 'zoom_out':
                zp = f"zoompan=z='if(eq(on,1),{zoom_factor},max(zoom-0.0006,1))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={num_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
            else:
                zp = f"zoompan=z='{zoom_factor}':x='if(eq(on,1),0,min(x+0.4,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={num_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"

            frames_video = story_dir / f"frames_{i}.mp4"
            subprocess.run([
                'ffmpeg', '-y', '-framerate', str(FPS),
                '-i', str(cap_dir / 'frame_%04d.png'),
                '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
                str(frames_video)
            ], capture_output=True, check=True)

            sw = int(WIDTH * zoom_factor)
            sh = int(HEIGHT * zoom_factor)
            subprocess.run([
                'ffmpeg', '-y', '-i', str(frames_video),
                '-vf', f'scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},{zp}',
                '-t', str(dur), '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264', '-preset', 'fast',
                str(clip_path)
            ], capture_output=True, check=True)

            for f in cap_dir.glob("*.png"):
                f.unlink()
            cap_dir.rmdir()
            if frames_video.exists():
                frames_video.unlink()

        scene_clips.append(str(clip_path))
        print(f"[SCENE {i+1}] Done")

    # Step 4: Concatenate all scene clips
    print("[CONCAT] Joining scenes...")
    concat_file = story_dir / "ig_concat.txt"
    with open(concat_file, 'w') as f:
        for c in scene_clips:
            f.write(f"file '{c}'\n")

    concat_video = story_dir / "ig_concat.mp4"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', str(concat_file), '-c', 'copy', str(concat_video)
    ], capture_output=True, check=True)

    # Step 5: Generate or find background music
    print("[MUSIC] Preparing background music...")
    music_path = MUSIC_DIR / "ambient_bg.wav"
    if not music_path.exists():
        MUSIC_DIR.mkdir(exist_ok=True)
        generate_bg_music(duration + 5, music_path)
        print(f"[MUSIC] Generated ambient background -> {music_path}")

    # Step 6: Mix narration + background music + video
    print("[MIX] Mixing audio tracks...")
    # Mix narration at full volume, music at 10%
    mixed_audio = story_dir / "ig_mixed_audio.wav"
    subprocess.run([
        'ffmpeg', '-y',
        '-i', str(narration),
        '-i', str(music_path),
        '-filter_complex',
        f'[0:a]aformat=sample_rates=44100:channel_layouts=mono[narr];'
        f'[1:a]aformat=sample_rates=44100:channel_layouts=mono,volume=0.10,atrim=0:{duration + 1}[music];'
        f'[narr][music]amix=inputs=2:duration=first:dropout_transition=2[out]',
        '-map', '[out]',
        str(mixed_audio)
    ], capture_output=True, check=True)

    # Step 7: Final encode - Instagram optimized
    print("[ENCODE] Instagram-optimized H.264...")
    subprocess.run([
        'ffmpeg', '-y',
        '-i', str(concat_video),
        '-i', str(mixed_audio),
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'libx264',
        '-preset', 'slow',           # Better compression
        '-crf', '20',                 # High quality
        '-profile:v', 'high',
        '-level', '4.0',
        '-maxrate', '8M',
        '-bufsize', '16M',
        '-pix_fmt', 'yuv420p',
        '-r', str(FPS),
        '-c:a', 'aac',
        '-b:a', '128k',
        '-ar', '44100',
        '-ac', '2',
        '-movflags', '+faststart',    # Instagram needs this
        '-shortest',
        str(final_output)
    ], capture_output=True, check=True)

    # Cleanup intermediate files
    for c in scene_clips:
        if os.path.exists(c):
            os.unlink(c)
    for f in [concat_file, concat_video, mixed_audio]:
        if f.exists():
            f.unlink()

    size_mb = os.path.getsize(final_output) / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  DONE: {final_output.name}")
    print(f"  Size: {size_mb:.1f} MB | Duration: {duration:.1f}s")
    print(f"  Format: 1080x1920 @ {FPS}fps H.264 High + AAC 44.1kHz")
    print(f"  Ready for Instagram upload")
    print(f"{'='*60}\n")

    return str(final_output)


def find_composable_stories():
    """Find stories that have narration + at least 3 images."""
    ready = []
    lang_suffixes = ["_es", "_pt", "_fr"]

    for story_json in sorted((PIPELINE_DIR / "stories").glob("*.json")):
        name = story_json.stem

        # Determine base name (for image lookup)
        base_name = name
        for suffix in lang_suffixes:
            if name.endswith(suffix):
                base_name = name[:-len(suffix)]
                break

        base_dir = OUTPUT_DIR / base_name
        story_dir = OUTPUT_DIR / name

        # Check images exist in base dir
        images = [f for f in base_dir.glob("scene_*.png")
                  if '_sub' not in f.name and '_cap' not in f.name]

        # For translated stories, narration can be auto-generated
        has_narration = (story_dir / "narration.wav").exists()

        # Translated stories are composable even without narration (we generate it)
        is_translation = base_name != name
        composable = len(images) >= 3 and (has_narration or is_translation)

        if composable:
            ig_output = OUTPUT_DIR / f"{name}_instagram.mp4"
            ready.append({
                'name': name,
                'images': len(images),
                'done': ig_output.exists(),
                'lang': name.split('_')[-1] if is_translation else 'en',
            })
    return ready


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 instagram_compose.py <story-name|--all|--batch N>")
        stories = find_composable_stories()
        print(f"\nComposable stories: {len(stories)}")
        for s in stories:
            status = "DONE" if s['done'] else f"{s['images']} images"
            print(f"  {'[x]' if s['done'] else '[ ]'} {s['name']} ({status})")
        return

    if sys.argv[1] == '--all':
        stories = find_composable_stories()
        pending = [s for s in stories if not s['done']]
        print(f"Composing {len(pending)} reels...")
        for s in pending:
            compose_instagram_reel(s['name'])

    elif sys.argv[1] == '--batch':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        stories = find_composable_stories()
        pending = [s for s in stories if not s['done']][:n]
        print(f"Composing batch of {len(pending)} reels...")
        for s in pending:
            compose_instagram_reel(s['name'])

    else:
        story_name = sys.argv[1]
        compose_instagram_reel(story_name, force='--force' in sys.argv)


if __name__ == '__main__':
    main()
