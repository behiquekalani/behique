# Local Reel Stack: $0/Month Video Pipeline

**Created:** 2026-03-19
**Status:** RESEARCH COMPLETE, READY TO BUILD
**Machines:** Ceiba (M4 Mac 16GB), Cobo (Windows + Ollama), Hutia (TBD)

---

## Architecture Overview

```
Story (text) --> [Cobo: llama3.2] --> Scene splits + image prompts
                                          |
                                          v
Image prompts --> [Ceiba: MLX Stable Diffusion] --> Scene images
                                                        |
Story text ----> [Ceiba: Chatterbox/Kokoro TTS] --> Narration audio
                                                        |
                                                        v
                            [Ceiba: FFmpeg + Python] --> Final 1080x1920 reel
                            (Ken Burns + subtitles)
```

**Total cost: $0/month. Everything runs on hardware you already own.**

---

## 1. TTS / Voice Narration

### Research Summary

| Model | Quality | Speed | M4 Mac Support | VRAM Needed | Emotion Control | Verdict |
|-------|---------|-------|----------------|-------------|-----------------|---------|
| **Chatterbox** (Resemble AI) | Best. Beats ElevenLabs in blind tests (63.75% preference) | Good. Turbo model: single-step decoder | Yes, MPS with community patches. CPU fallback works fine | ~4GB | Emotion exaggeration dial | **PRIMARY PICK** |
| **Kokoro** (hexgrad) | Very good. 44% TTS Arena win rate | Fastest. Under 0.3s for most texts | Yes, pip install, MPS fallback | ~500MB (82M params) | Limited, tone via voice selection | **SECONDARY / FAST OPTION** |
| **Bark** (Suno) | Good for short clips | Slow. 15s to generate 10s audio on GPU | Yes but slow on CPU. Needs ~12GB VRAM for full model | 8-12GB | Best. Laughter, sighs, crying, music via brackets | **SKIP for now. Too slow, too much VRAM** |
| **XTTS-v2** (Coqui) | Good. Voice cloning from 6s clip | Moderate | Broken MPS. CPU-only on Mac, but works | ~4GB | Moderate | **BACKUP. Voice cloning use case only** |
| **EmotiVoice** (NetEase) | Decent. 2000+ voices | Moderate | Needs NVIDIA GPU for acceleration. CPU fallback possible | ~4GB | Good. Emotion tags: Happy, Sad, Angry | **SKIP. Designed for NVIDIA** |

### Winner: Chatterbox TTS (primary) + Kokoro (fast drafts)

**Why Chatterbox:** State-of-the-art quality, MIT license, emotion dial, voice cloning from reference audio. Community Apple Silicon patches exist and work. Falls back to CPU gracefully on M4 (still fast enough for 30-60s reels).

**Why Kokoro as backup:** 82M parameters means it runs anywhere instantly. Good for drafting/previewing before final render with Chatterbox. Dead simple install.

### Install: Chatterbox on M4 Mac

```bash
# Step 1: Install Python 3.11 (Chatterbox is tested on 3.11, not 3.14)
brew install python@3.11

# Step 2: Create dedicated venv
python3.11 -m venv ~/behique/venvs/chatterbox
source ~/behique/venvs/chatterbox/bin/activate

# Step 3: Install PyTorch FIRST (critical for Apple Silicon)
pip install torch==2.6.0 torchaudio==2.6.0

# Step 4: Install Chatterbox
pip install chatterbox-tts

# Step 5: Test it
python -c "
from chatterbox.tts import ChatterboxTTS
import torchaudio

model = ChatterboxTTS.from_pretrained(device='cpu')
text = 'The forest was silent. Not the peaceful kind of silent. The kind that means something is watching.'
wav = model.generate(text)
torchaudio.save('test_narration.wav', wav, model.sr)
print('Saved test_narration.wav')
"
```

**With emotion control:**
```python
# The exaggeration parameter controls emotional intensity (0.0 to 1.0)
wav = model.generate(text, exaggeration=0.7)
```

**With voice cloning (use any 10-30s reference WAV):**
```python
wav = model.generate(text, audio_prompt_path="reference_voice.wav")
```

### Install: Kokoro (fast fallback)

```bash
# Can use the same venv or a separate one
source ~/behique/venvs/chatterbox/bin/activate

# Step 1: Install espeak (required dependency)
brew install espeak

# Step 2: Install Kokoro
pip install kokoro soundfile

# Step 3: Test it
PYTORCH_ENABLE_MPS_FALLBACK=1 python -c "
from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code='a')  # 'a' = American English
generator = pipeline('The shadows grew longer as the sun disappeared behind the mountains.', voice='af_heart')
for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f'kokoro_test_{i}.wav', audio, 24000)
    print(f'Saved kokoro_test_{i}.wav')
"
```

**Available Kokoro voices:** af_heart, af_bella, af_sarah, am_adam, am_michael (26 total across 8 languages)

---

## 2. Image Generation

### Research Summary

| Model | Quality | Speed on M4 16GB | Memory Use | Setup Complexity | Verdict |
|-------|---------|-------------------|------------|------------------|---------|
| **MLX Stable Diffusion (SD 1.5)** | Good. Classic SD quality | 8-15s per image | ~4GB | Low. pip install | **FAST OPTION** |
| **SDXL via Draw Things** | Very good. Higher res | 20-40s per image | ~8GB | Easiest. App install | **EASY OPTION** |
| **Flux Schnell (4-step)** | Excellent. Best quality | 2-3 min per image | ~12GB (quantized fits 16GB) | Medium | **BEST QUALITY** |
| **MLX Stable Diffusion 3 Medium** | Very good | 15-30s | ~6GB | Medium | **SWEET SPOT** |
| **DiffusionKit** | Very good. Apple optimized | Fast | Varies | Low. CLI tool | **WORTH TRYING** |

### Winner: MLX Stable Diffusion (SD 1.5 for speed, SDXL for quality)

For a pipeline that generates 5-8 images per reel, you want speed. SD 1.5 via MLX gives you images in 8-15 seconds each. For hero shots or thumbnails, bump up to SDXL.

Flux Schnell produces the best images but at 2-3 minutes each, a 6-scene reel takes 12-18 minutes just for images. Use it when quality matters more than speed.

### Install: MLX Stable Diffusion

```bash
# Step 1: Create venv (or reuse chatterbox venv)
python3.11 -m venv ~/behique/venvs/imggen
source ~/behique/venvs/imggen/bin/activate

# Step 2: Clone MLX examples
git clone https://github.com/ml-explore/mlx-examples.git ~/behique/tools/mlx-examples
cd ~/behique/tools/mlx-examples/stable_diffusion

# Step 3: Install requirements
pip install -r requirements.txt

# Step 4: Generate a test image
python txt2image.py "A dark forest at twilight, cinematic lighting, moody atmosphere, volumetric fog, 4k" --n_images 1 --output test_scene.png

# Step 5: Generate with negative prompt for better quality
python txt2image.py "A warrior standing on a cliff overlooking a burning city, epic cinematic, dramatic lighting" --n_images 1 --output hero_shot.png --negative_prompt "blurry, low quality, text, watermark, deformed"
```

### Install: DiffusionKit (Apple-optimized alternative)

```bash
pip install diffusionkit

# Generate from CLI
diffusionkit-cli --prompt "A mysterious temple in dense jungle, rays of light through canopy, cinematic" --output temple.png
```

### Install: Draw Things (GUI, easiest start)

```bash
# Download from Mac App Store (free)
# Supports: SD 1.5, SDXL, Flux Schnell, Flux Dev
# Metal FlashAttention optimization built in
# No command line needed, but less scriptable
```

### For the Pipeline (scriptable approach):

```python
# generate_scene_images.py
import subprocess
import json

def generate_image(prompt, output_path, model_dir="~/behique/tools/mlx-examples/stable_diffusion"):
    """Generate a single image using MLX Stable Diffusion."""
    cmd = [
        "python", f"{model_dir}/txt2image.py",
        prompt,
        "--n_images", "1",
        "--output", output_path,
        "--negative_prompt", "blurry, low quality, text, watermark, deformed, ugly"
    ]
    subprocess.run(cmd, check=True)
    return output_path

def generate_scenes(scenes_json_path, output_dir):
    """Generate images for all scenes from Ollama's scene split."""
    with open(scenes_json_path) as f:
        scenes = json.load(f)

    for i, scene in enumerate(scenes):
        output = f"{output_dir}/scene_{i:02d}.png"
        generate_image(scene["image_prompt"], output)
        print(f"Generated {output}")
```

---

## 3. Video Assembly (FFmpeg + Python)

### Ken Burns Effect Commands (Vertical 1080x1920)

```bash
# ZOOM IN (slow zoom toward center, 5 seconds)
ffmpeg -loop 1 -framerate 30 -i scene_01.png \
  -vf "scale=8000:-1,zoompan=z='min(zoom+0.0015,1.5)':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=150:s=1080x1920:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p -y scene_01.mp4

# ZOOM OUT (start zoomed in, pull back, 5 seconds)
ffmpeg -loop 1 -framerate 30 -i scene_02.png \
  -vf "scale=8000:-1,zoompan=z='if(eq(on,1),1.5,max(zoom-0.0015,1.0))':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=150:s=1080x1920:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p -y scene_02.mp4

# PAN LEFT TO RIGHT (5 seconds)
ffmpeg -loop 1 -framerate 30 -i scene_03.png \
  -vf "scale=-1:3840,zoompan=z=1.2:x='iw/2-(iw/zoom/2)+((iw/zoom/2)*on/150)':y=ih/2-(ih/zoom/2):d=150:s=1080x1920:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p -y scene_03.mp4
```

### Subtitle Overlay

```bash
# Burn subtitles into video (ASS format for styling)
ffmpeg -i reel_no_subs.mp4 -vf "subtitles=narration.srt:force_style='FontName=Arial Bold,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=120'" \
  -c:v libx264 -c:a copy -y reel_final.mp4
```

### Full Assembly Python Script

```python
# assemble_reel.py
import subprocess
import json
import os

def create_scene_clip(image_path, duration, output_path, effect="zoom_in"):
    """Create a Ken Burns clip from a single image."""
    if effect == "zoom_in":
        zoom = f"z='min(zoom+0.0015,1.5)':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)"
    elif effect == "zoom_out":
        zoom = f"z='if(eq(on,1),1.5,max(zoom-0.0015,1.0))':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)"
    elif effect == "pan_right":
        frames = int(duration * 30)
        zoom = f"z=1.2:x='iw/2-(iw/zoom/2)+((iw/zoom/4)*on/{frames})':y=ih/2-(ih/zoom/2)"
    else:
        zoom = f"z=1.0:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)"

    frames = int(duration * 30)
    cmd = [
        "ffmpeg", "-loop", "1", "-framerate", "30", "-i", image_path,
        "-vf", f"scale=8000:-1,zoompan={zoom}:d={frames}:s=1080x1920:fps=30",
        "-t", str(duration), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", output_path
    ]
    subprocess.run(cmd, check=True)

def generate_srt(scenes, output_path):
    """Generate SRT subtitle file from scene data with timestamps."""
    with open(output_path, 'w') as f:
        for i, scene in enumerate(scenes):
            start = scene["start_time"]
            end = scene["end_time"]
            text = scene["subtitle_text"]

            start_str = format_srt_time(start)
            end_str = format_srt_time(end)

            f.write(f"{i+1}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{text}\n\n")

def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def concat_clips(clip_paths, audio_path, srt_path, output_path):
    """Concatenate scene clips, add audio narration and subtitles."""
    # Create concat file
    concat_file = "/tmp/concat_list.txt"
    with open(concat_file, 'w') as f:
        for path in clip_paths:
            f.write(f"file '{path}'\n")

    # Step 1: Concat video clips
    temp_video = "/tmp/reel_concat.mp4"
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", temp_video
    ], check=True)

    # Step 2: Add audio
    temp_with_audio = "/tmp/reel_with_audio.mp4"
    subprocess.run([
        "ffmpeg", "-i", temp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-shortest", "-y", temp_with_audio
    ], check=True)

    # Step 3: Burn subtitles
    subprocess.run([
        "ffmpeg", "-i", temp_with_audio,
        "-vf", f"subtitles={srt_path}:force_style='FontName=Arial Bold,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=120'",
        "-c:v", "libx264", "-c:a", "copy", "-y", output_path
    ], check=True)

    print(f"Final reel: {output_path}")

def assemble_reel(scenes_json, images_dir, audio_path, output_path):
    """Full pipeline: images + audio + subtitles = reel."""
    with open(scenes_json) as f:
        scenes = json.load(f)

    effects = ["zoom_in", "pan_right", "zoom_out", "zoom_in", "pan_right", "zoom_out"]
    clip_paths = []

    for i, scene in enumerate(scenes):
        image = os.path.join(images_dir, f"scene_{i:02d}.png")
        clip = os.path.join(images_dir, f"clip_{i:02d}.mp4")
        effect = effects[i % len(effects)]

        create_scene_clip(image, scene["duration"], clip, effect)
        clip_paths.append(clip)

    srt_path = os.path.join(images_dir, "narration.srt")
    generate_srt(scenes, srt_path)
    concat_clips(clip_paths, audio_path, srt_path, output_path)
```

---

## 4. Story Splitting (Ollama on Cobo)

Ollama with llama3.2 splits a story into scenes, generates image prompts, and assigns durations.

### Prompt Template

```
You are a cinematic director breaking a short story into visual scenes for a vertical video reel (1080x1920, 30-60 seconds total).

STORY:
{story_text}

Return ONLY valid JSON. No explanation. Format:

[
  {
    "scene_number": 1,
    "narration_text": "The exact text the narrator reads for this scene.",
    "subtitle_text": "Short subtitle overlay (max 10 words per line, 2 lines max).",
    "image_prompt": "Detailed Stable Diffusion prompt. Include: subject, setting, lighting, mood, camera angle. Style: cinematic, dramatic lighting, 4k, photorealistic.",
    "duration": 5.0,
    "start_time": 0.0,
    "end_time": 5.0
  }
]

Rules:
- 4 to 8 scenes total
- Each scene 3 to 8 seconds
- Total duration 30 to 60 seconds
- Image prompts must be vivid, specific, cinematic
- Subtitles are short emotional hooks, not full narration
- Always specify lighting and mood in image prompts
```

### Call from Ceiba (Mac) to Cobo via API

```python
# story_splitter.py
import requests
import json

OLLAMA_HOST = "http://bridge.merchoo.shop:11434"  # Cobo's Ollama endpoint

def split_story(story_text):
    """Send story to Cobo's llama3.2 and get scene breakdown."""
    prompt = f"""You are a cinematic director breaking a short story into visual scenes for a vertical video reel (1080x1920, 30-60 seconds total).

STORY:
{story_text}

Return ONLY valid JSON array. No explanation. Each scene needs:
- scene_number, narration_text, subtitle_text, image_prompt, duration, start_time, end_time

Image prompts must include: subject, setting, lighting, mood, camera angle. Style: cinematic, dramatic lighting, 4k.
4 to 8 scenes. Each 3-8 seconds. Total 30-60 seconds."""

    response = requests.post(f"{OLLAMA_HOST}/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    })

    result = response.json()["response"]
    scenes = json.loads(result)
    return scenes

def split_story_local(story_text):
    """Use local Ollama if available."""
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3.2",
            "prompt": story_text,
            "stream": False,
            "format": "json"
        })
        return json.loads(response.json()["response"])
    except:
        print("Local Ollama not available, trying Cobo...")
        return split_story(story_text)
```

### Or run locally on Ceiba (Ollama is installed)

```bash
# Ceiba already has Ollama installed at /usr/local/bin/ollama
# Pull llama3.2 if not already present
ollama pull llama3.2

# Test scene splitting
ollama run llama3.2 "Break this story into 5 cinematic scenes with image prompts: 'A fisherman discovers a glowing stone beneath the waves. As he brings it to shore, the sky darkens and the ocean begins to pull back from the beach. The stone pulses with light, and ancient symbols appear in the sand around his feet.'"
```

---

## 5. Complete Pipeline Script

```python
#!/usr/bin/env python3
"""
local_reel_pipeline.py
Full pipeline: Story -> Scenes -> Images -> Audio -> Reel
$0/month. Runs entirely on local hardware.
"""

import os
import sys
import json
import subprocess

# Configuration
PROJECT_DIR = os.path.expanduser("~/behique/reel-output")
MLX_SD_DIR = os.path.expanduser("~/behique/tools/mlx-examples/stable_diffusion")
OLLAMA_URL = "http://localhost:11434"  # Local first, fallback to Cobo

def ensure_dirs(reel_name):
    reel_dir = os.path.join(PROJECT_DIR, reel_name)
    os.makedirs(os.path.join(reel_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(reel_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(reel_dir, "clips"), exist_ok=True)
    return reel_dir

def step1_split_story(story_text, reel_dir):
    """Use Ollama to split story into scenes."""
    print("[1/4] Splitting story into scenes...")
    # Import from story_splitter.py
    from story_splitter import split_story_local
    scenes = split_story_local(story_text)

    scenes_path = os.path.join(reel_dir, "scenes.json")
    with open(scenes_path, 'w') as f:
        json.dump(scenes, f, indent=2)

    print(f"  Created {len(scenes)} scenes -> {scenes_path}")
    return scenes

def step2_generate_images(scenes, reel_dir):
    """Use MLX Stable Diffusion to generate scene images."""
    print("[2/4] Generating scene images...")
    images_dir = os.path.join(reel_dir, "images")

    for i, scene in enumerate(scenes):
        output = os.path.join(images_dir, f"scene_{i:02d}.png")
        prompt = scene["image_prompt"]

        subprocess.run([
            sys.executable, os.path.join(MLX_SD_DIR, "txt2image.py"),
            prompt,
            "--n_images", "1",
            "--output", output,
            "--negative_prompt", "blurry, low quality, text, watermark, deformed"
        ], check=True)
        print(f"  Scene {i}: {output}")

def step3_generate_narration(scenes, reel_dir):
    """Use Chatterbox TTS to generate narration audio."""
    print("[3/4] Generating narration audio...")
    from chatterbox.tts import ChatterboxTTS
    import torchaudio

    model = ChatterboxTTS.from_pretrained(device='cpu')

    # Combine all narration text
    full_narration = " ".join([s["narration_text"] for s in scenes])

    wav = model.generate(full_narration, exaggeration=0.6)
    audio_path = os.path.join(reel_dir, "audio", "narration.wav")
    torchaudio.save(audio_path, wav, model.sr)
    print(f"  Narration saved: {audio_path}")
    return audio_path

def step4_assemble_reel(scenes, reel_dir, audio_path):
    """Combine images + audio + subtitles into final reel."""
    print("[4/4] Assembling final reel...")
    from assemble_reel import create_scene_clip, generate_srt, concat_clips

    images_dir = os.path.join(reel_dir, "images")
    clips_dir = os.path.join(reel_dir, "clips")
    effects = ["zoom_in", "pan_right", "zoom_out", "zoom_in", "pan_right", "zoom_out"]
    clip_paths = []

    for i, scene in enumerate(scenes):
        image = os.path.join(images_dir, f"scene_{i:02d}.png")
        clip = os.path.join(clips_dir, f"clip_{i:02d}.mp4")
        create_scene_clip(image, scene["duration"], clip, effects[i % len(effects)])
        clip_paths.append(clip)

    srt_path = os.path.join(reel_dir, "narration.srt")
    generate_srt(scenes, srt_path)

    output = os.path.join(reel_dir, "reel_final.mp4")
    concat_clips(clip_paths, audio_path, srt_path, output)
    print(f"\n  DONE: {output}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python local_reel_pipeline.py <reel-name> <story-file.txt>")
        sys.exit(1)

    reel_name = sys.argv[1]
    story_file = sys.argv[2]

    with open(story_file) as f:
        story_text = f.read()

    reel_dir = ensure_dirs(reel_name)
    scenes = step1_split_story(story_text, reel_dir)
    step2_generate_images(scenes, reel_dir)
    audio_path = step3_generate_narration(scenes, reel_dir)
    step4_assemble_reel(scenes, reel_dir, audio_path)

if __name__ == "__main__":
    main()
```

---

## 6. Setup Checklist

Run these once to set up the full pipeline on Ceiba.

```bash
# 1. Create project structure
mkdir -p ~/behique/venvs
mkdir -p ~/behique/tools
mkdir -p ~/behique/reel-output

# 2. Install Python 3.11 (Chatterbox needs it)
brew install python@3.11

# 3. Create venv with Python 3.11
python3.11 -m venv ~/behique/venvs/reel-pipeline
source ~/behique/venvs/reel-pipeline/bin/activate

# 4. Install PyTorch (Apple Silicon)
pip install torch==2.6.0 torchaudio==2.6.0

# 5. Install Chatterbox TTS
pip install chatterbox-tts

# 6. Install Kokoro TTS (fast backup)
brew install espeak
pip install kokoro soundfile

# 7. Clone and install MLX Stable Diffusion
git clone https://github.com/ml-explore/mlx-examples.git ~/behique/tools/mlx-examples
pip install -r ~/behique/tools/mlx-examples/stable_diffusion/requirements.txt

# 8. Install video assembly deps
pip install requests

# 9. Verify FFmpeg (already installed)
ffmpeg -version

# 10. Pull llama3.2 for local scene splitting
ollama pull llama3.2

# 11. Test each component
echo "Testing Kokoro..."
PYTORCH_ENABLE_MPS_FALLBACK=1 python -c "
from kokoro import KPipeline
import soundfile as sf
p = KPipeline(lang_code='a')
for i, (gs, ps, audio) in enumerate(p('Testing the pipeline.', voice='af_heart')):
    sf.write('test_kokoro.wav', audio, 24000)
    break
print('Kokoro OK')
"

echo "Testing MLX SD..."
cd ~/behique/tools/mlx-examples/stable_diffusion
python txt2image.py "A test image, simple landscape" --n_images 1 --output ~/behique/reel-output/test.png

echo "Testing Chatterbox..."
python -c "
from chatterbox.tts import ChatterboxTTS
import torchaudio
m = ChatterboxTTS.from_pretrained(device='cpu')
w = m.generate('Testing Chatterbox.')
torchaudio.save('test_chatterbox.wav', w, m.sr)
print('Chatterbox OK')
"
```

---

## 7. Performance Estimates (M4 Mac 16GB)

| Step | Time per Reel (6 scenes) | Notes |
|------|--------------------------|-------|
| Story splitting (Ollama) | 10-30s | Local llama3.2, fast |
| Image generation (MLX SD 1.5) | 60-90s | ~10-15s per image |
| TTS narration (Chatterbox) | 30-60s | CPU mode, 30-60s story |
| Video assembly (FFmpeg) | 20-40s | Ken Burns + subtitles |
| **Total** | **~3-4 minutes per reel** | |

If you use Flux Schnell instead of SD 1.5 for images, add 10-15 minutes.
If you use Kokoro instead of Chatterbox for TTS, save ~20 seconds.

---

## 8. Upgrade Path

When you want better quality without spending money:

1. **Better images:** Switch from SD 1.5 to SDXL (still fits 16GB). Or use Flux Schnell with Q6 quantization for best-in-class quality at ~3 min/image.

2. **Voice cloning:** Record a 30-second reference clip of the voice you want. Chatterbox clones it from that clip alone. No training needed.

3. **Offload to Cobo:** If Cobo has a decent NVIDIA GPU, run Bark there for maximum emotional range (laughter, sighs, crying). Or run SDXL/Flux there for faster image gen.

4. **Background music:** Use facebook/musicgen-small (runs on M4) to generate ambient music from text prompts. Layer it under narration at -15dB with FFmpeg.

5. **Animated scenes:** Look into Stable Video Diffusion or AnimateDiff for turning still images into 3-4 second video clips. Heavier on VRAM but possible on 16GB with quantization.

---

## 9. Existing Open-Source Pipelines (Reference)

These are worth studying but they rely on cloud APIs. The architecture above is purpose-built for your local setup.

| Project | What it does | Why not use directly |
|---------|-------------|---------------------|
| [SamurAIGPT/Text-To-Video-AI](https://github.com/SamurAIGPT/Text-To-Video-AI) | Full text-to-reel pipeline | Uses OpenAI API + Pexels stock video. Not local |
| [Trekky12/kburns-slideshow](https://github.com/Trekky12/kburns-slideshow) | FFmpeg Ken Burns slideshow generator | Good reference for Ken Burns commands. No AI |
| [hpcaitech/Open-Sora](https://github.com/hpcaitech/Open-Sora) | Text to video generation | Needs serious GPU (48GB+ VRAM) |
| [sniklaus/3d-ken-burns](https://github.com/sniklaus/3d-ken-burns) | 3D depth-aware Ken Burns from single image | Cool but needs CUDA GPU |

---

## Usage Example

```bash
# Activate the pipeline venv
source ~/behique/venvs/reel-pipeline/bin/activate

# Write a story
cat > /tmp/test_story.txt << 'STORY'
A fisherman discovers a glowing stone beneath the waves. As he brings it to shore, the sky darkens and the ocean begins to pull back from the beach. The stone pulses with light, and ancient symbols appear in the sand around his feet. He realizes he has awakened something that was meant to stay asleep.
STORY

# Run the full pipeline
python ~/behique/tools/local_reel_pipeline.py glowing-stone /tmp/test_story.txt

# Output: ~/behique/reel-output/glowing-stone/reel_final.mp4
```

---

## Decision Log

- **Chatterbox over Bark:** Bark is too slow and needs too much VRAM for the M4 Mac. Chatterbox beats ElevenLabs in blind tests and has an emotion dial.
- **Chatterbox over XTTS-v2:** XTTS-v2 has broken MPS support and Coqui is less maintained. Chatterbox is actively developed with Apple Silicon community patches.
- **Kokoro as backup:** 82M params, runs anywhere in under a second. Perfect for quick drafts.
- **EmotiVoice skipped:** Designed for NVIDIA GPUs. CPU fallback exists but the ecosystem is China-focused (Chinese docs, models).
- **MLX SD over ComfyUI:** ComfyUI is a GUI. We need scriptable CLI for the pipeline. MLX is Apple's own framework, native Metal acceleration.
- **Flux Schnell as upgrade:** Best image quality available locally but 2-3 min per image is too slow for the default pipeline. Available when quality matters.
- **Local Ollama over Cobo:** Ceiba already has Ollama installed. Run scene splitting locally to avoid network dependency. Cobo is the fallback.
