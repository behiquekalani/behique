#!/usr/bin/env python3
"""Compose a reel from pre-generated images + narration using FFmpeg."""
import json, subprocess, os, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

def burn_subtitle_on_image(img_path, text, output_path):
    """Burn subtitle text onto image using PIL (no FFmpeg drawtext needed)."""
    img = Image.open(img_path).convert('RGB')
    # Scale to 1080x1920 for reel
    img = img.resize((1080, 1920), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
    except Exception:
        font = ImageFont.load_default(size=42)

    # Word wrap
    words = text.split()
    lines = []
    current = []
    for w in words:
        current.append(w)
        if len(' '.join(current)) > 30:
            lines.append(' '.join(current))
            current = []
    if current:
        lines.append(' '.join(current))

    subtitle = '\n'.join(lines[-3:])

    # Draw text with black outline at bottom
    x = 1080 // 2
    y = 1920 - 200
    # Outline
    for dx in [-3, -2, -1, 0, 1, 2, 3]:
        for dy in [-3, -2, -1, 0, 1, 2, 3]:
            draw.multiline_text((x + dx, y + dy), subtitle, fill='black',
                                font=font, anchor='ms', align='center')
    # White text
    draw.multiline_text((x, y), subtitle, fill='white',
                        font=font, anchor='ms', align='center')

    img.save(output_path)


def main():
    story_name = sys.argv[1] if len(sys.argv) > 1 else 'grandmas-recipe-card'
    out_dir = f'output/{story_name}'
    timing = json.load(open(f'{out_dir}/timing.json'))

    FPS = 30
    WIDTH = 1080
    HEIGHT = 1920
    effects = ['zoom_in', 'zoom_out', 'pan', 'zoom_in', 'zoom_out']

    scene_clips = []

    for i, scene in enumerate(timing['scenes']):
        img = f'{out_dir}/scene_{i}.png'
        sub_img = f'{out_dir}/scene_{i}_sub.png'
        clip = f'{out_dir}/clip_{i}.mp4'
        dur = scene['duration'] + 0.5
        effect = effects[i % len(effects)]

        print(f'[CLIP] Scene {i}: {dur:.1f}s, effect={effect}')

        # Burn subtitle onto image first
        burn_subtitle_on_image(img, scene['text'], sub_img)

        zoom_factor = 1.15  # Gentler zoom for subtitled images
        if effect == 'zoom_in':
            zp = f"zoompan=z='min(zoom+0.0008,{zoom_factor})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(dur*FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        elif effect == 'zoom_out':
            zp = f"zoompan=z='if(eq(on,1),{zoom_factor},max(zoom-0.0008,1))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(dur*FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        else:
            zp = f"zoompan=z='{zoom_factor}':x='if(eq(on,1),0,min(x+0.5,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={int(dur*FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS}"

        sw = int(WIDTH * zoom_factor)
        sh = int(HEIGHT * zoom_factor)

        vf = (f"scale={sw}:{sh}:force_original_aspect_ratio=increase,"
              f"crop={sw}:{sh},{zp}")

        result = subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-i', sub_img,
            '-vf', vf,
            '-t', str(dur), '-pix_fmt', 'yuv420p',
            '-c:v', 'libx264', '-preset', 'fast', clip
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f'[ERROR] Scene {i}: {result.stderr[-300:]}')
            return

        scene_clips.append(os.path.abspath(clip))
        os.unlink(sub_img)
        print(f'[CLIP] Scene {i} done')

    # Concat
    concat_file = f'{out_dir}/concat.txt'
    with open(concat_file, 'w') as f:
        for c in scene_clips:
            f.write(f"file '{c}'\n")

    temp_video = f'{out_dir}/temp_concat.mp4'
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_file, '-c', 'copy', temp_video
    ], capture_output=True, check=True)

    # Add narration
    final = f'{out_dir}/{story_name}.mp4'
    subprocess.run([
        'ffmpeg', '-y', '-i', temp_video, '-i', f'{out_dir}/narration.wav',
        '-map', '0:v', '-map', '1:a',
        '-c:v', 'copy', '-c:a', 'aac', '-shortest',
        final
    ], capture_output=True, check=True)

    # Cleanup
    os.unlink(concat_file)
    os.unlink(temp_video)
    for c in scene_clips:
        os.unlink(c)

    size = os.path.getsize(final) / (1024*1024)
    print(f'\n[DONE] {final} ({size:.1f} MB)')

if __name__ == '__main__':
    main()
