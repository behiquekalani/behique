# AI Reel Production Pipeline: Tools Research (March 2026)

Research for building an automated pipeline that turns written stories into finished video reels.

---

## Table of Contents

1. [AI Voice / Narration (TTS)](#1-ai-voice--narration-tts)
2. [AI Image / Animation Generation](#2-ai-image--animation-generation)
3. [Video Assembly](#3-video-assembly)
4. [Existing Open Source Pipelines](#4-existing-open-source-pipelines)
5. [Recommended Stacks](#5-recommended-stacks)
6. [Cost Per Reel Estimates](#6-cost-per-reel-estimates)
7. [Quick-Start Guide](#7-quick-start-guide)

---

## 1. AI Voice / Narration (TTS)

### Tool Comparison

| Tool | Price | Quality | Emotional Delivery | API | Local Option | Sign Up |
|------|-------|---------|-------------------|-----|-------------|---------|
| **ElevenLabs** | Free: 10k chars/mo. Starter: $5/mo (30k). Creator: $11/mo (100k). Pro: $99/mo (500k) | Best in class. Eleven v3 model has maximum expressiveness | Yes. Reads emotional cues from text ("she whispered," exclamation marks, etc.) | Full REST API, streaming supported | No | [elevenlabs.io/pricing](https://elevenlabs.io/pricing) |
| **Murf.ai** | Creator: $23/mo. Business: $99/mo | Very good. Built-in timeline editor, multi-voice scripts | Good. SSML support for fine control over tone and emphasis | API available on paid plans | No | [murf.ai](https://murf.ai) |
| **Play.ht** | SHUT DOWN Dec 2025 (acquired by Meta) | Was good | N/A | N/A | N/A | Dead |
| **Fish Audio** | Pay-as-you-go, competitive with ElevenLabs | Strong. S1-mini model supports fine-grained emotion control | Yes. Explicit emotion, tone, and delivery controls | API available | No | [fish.audio](https://fish.audio) |
| **Chatterbox (Resemble AI)** | Free, MIT license | Good. Sub-200ms latency | Yes. Emotion exaggeration dial to control expressiveness | Python library | **Yes, fully local** | [github.com/resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox) |
| **Bark (Suno)** | Free, MIT license | Good for short clips. Can generate laughter, sighs, music | Yes. Non-verbal sounds, multilingual, emotional range | Python library | **Yes, fully local** | [github.com/suno-ai/bark](https://github.com/suno-ai/bark) |
| **EmotiVoice** | Free, open source | Decent. 2000+ voices, English + Chinese | Yes. Explicit emotion tags: happy, excited, sad, angry | Python library | **Yes, fully local** | [github.com/netease-youdao/EmotiVoice](https://github.com/netease-youdao/EmotiVoice) |
| **Kokoro TTS** | Free, open weights | Good for English narration | Moderate. Natural-sounding but less controllable emotion | Python library | **Yes, fully local** | Used by short-video-maker project |
| **XTTS-v2 (Coqui)** | Free, open source | Very good. Voice cloning from 6 seconds of audio | Yes. Replicates emotional tone from reference audio | Python library | **Yes, fully local** | [github.com/coqui-ai/TTS](https://github.com/coqui-ai/TTS) |

### Verdict on TTS

**Best quality:** ElevenLabs (Eleven v3 model). Nothing else matches it for emotional, cinematic narration. The $11/mo Creator plan gives you 100k characters, enough for roughly 50-80 reels per month.

**Best free/local:** Chatterbox or XTTS-v2. Chatterbox has explicit emotion control. XTTS-v2 can clone a voice from a short sample and carry the emotion through.

**For this pipeline:** Start with ElevenLabs Creator ($11/mo). When volume scales up, add Chatterbox as local fallback for drafts/testing.

---

## 2. AI Image / Animation Generation

### Tool Comparison

| Tool | Price | Quality | Style Consistency | API | Local Option | Sign Up |
|------|-------|---------|-------------------|-----|-------------|---------|
| **Midjourney v8** | Basic: $10/mo. Standard: $30/mo. Pro: $60/mo | Top tier. Cinematic, photorealistic | Good with style references and --sref flag | **No official API. Third-party only (risk of ban)** | No | [midjourney.com](https://midjourney.com) |
| **GPT Image 1.5 (OpenAI)** | Low: $0.011/img. Medium: $0.042/img. High: $0.167/img | Excellent. Elo #1 on LM Arena (1,264) | Moderate. Can use reference images in prompt | Full REST API | No | [platform.openai.com](https://platform.openai.com) |
| **DALL-E 3 (OpenAI)** | Standard: $0.04/img. HD: $0.08/img | Good but now legacy | Moderate | Full REST API | No | Same as above |
| **Flux 2 (Black Forest Labs)** | API: varies by provider. Self-hosted: free | Frontier quality. Rivals proprietary models | Strong prompt adherence for layout, lighting, typography | API via Replicate, fal.ai, etc. | **Yes (needs beefy GPU, 24GB+ VRAM)** | [blackforestlabs.ai](https://blackforestlabs.ai) |
| **Stable Diffusion XL/3.5** | Free | Good. Huge ecosystem of fine-tuned models | Excellent via LoRAs and custom checkpoints | ComfyUI, A1111 | **Yes (runs on 8GB+ VRAM)** | [stability.ai](https://stability.ai) |
| **Leonardo.ai** | Free: 150 tokens/day. Apprentice: $12/mo. | Very good. Kino XL model built for cinematic visuals | Good. Style presets and model fine-tuning | API available. Enterprise starts at $0.002/gen | No | [leonardo.ai](https://leonardo.ai) |
| **Google Imagen 4 Fast** | $0.02/image via API | Very good | Good | Google Cloud Vertex AI API | No | [cloud.google.com](https://cloud.google.com/vertex-ai) |

### Style Consistency Across Scenes

This is the hardest problem for multi-image reels. Solutions:

1. **Flux/SD + LoRA training:** Train a LoRA on your visual style (10-20 reference images). Every generation maintains the same look. Free if running locally.
2. **Midjourney --sref:** Style reference flag keeps visual consistency. But no API means manual work.
3. **GPT Image with reference prompting:** Include "maintain the exact same visual style as previous scenes" with detailed style descriptions. Works but less reliable.
4. **Leonardo Kino XL:** Cinematic preset maintains a consistent film look across generations.
5. **ComfyUI workflows:** Build a pipeline that feeds the same seed, style LoRA, and controlnet across all scene generations. Most reliable for automation.

### Verdict on Image Gen

**Best quality + API:** GPT Image 1.5 (High) at $0.167/image. Or GPT Image 1 (Medium) at $0.042/image for 80% of the quality at 25% of the cost.

**Best free/local:** Flux 2 [dev] if you have a GPU with 24GB VRAM. Stable Diffusion XL if you have 8GB VRAM. Both support LoRAs for style consistency.

**Best budget API:** Google Imagen 4 Fast at $0.02/image.

**For this pipeline:** GPT Image 1 (Medium) via API at $0.042/image. 10 images per reel = $0.42. Cheap enough to automate, good enough to look cinematic.

---

## 3. Video Assembly

### Tool Comparison

| Tool | Price | Capabilities | Headless/Automated | API | Sign Up |
|------|-------|-------------|-------------------|-----|---------|
| **FFmpeg + MoviePy (Python)** | Free | Full control: images to video, audio overlay, text overlays, transitions, Ken Burns effect | **Yes, fully headless** | Python library | Already installed or `pip install moviepy` |
| **Shotstack** | Pay-as-you-go: $0.40/min. Subscription: $0.20/min | Cloud rendering. JSON timeline, text overlays, transitions, audio mixing | **Yes, cloud API** | Full REST API | [shotstack.io](https://shotstack.io/pricing/) |
| **Creatomate** | Essential: $54/mo (2,000 credits, ~200 videos). Growth: $129/mo (10,000 credits) | Template-based. Text overlays, animations, audio, dynamic data | **Yes, cloud API** | Full REST API + template editor | [creatomate.com](https://creatomate.com/pricing) |
| **Remotion** | Free (open source). Cloud: pay per render | React-based video creation. Programmable, composable | **Yes, headless** | Node.js library | [remotion.dev](https://remotion.dev) |
| **CapCut** | Free app | Great editor, lots of templates | **No API. No headless option.** | No public API | Not viable for automation |
| **Runway ML** | Gen-4 Turbo: $0.05/sec. Gen-4 Aleph: $0.15/sec | AI video generation (not just assembly). Text-to-video, image-to-video | **Yes, cloud API** | Full REST API | [runwayml.com/api](https://runwayml.com/api) |
| **JSON2Video** | Starter: $25/mo | JSON-based video creation, text overlays, transitions | **Yes, cloud API** | REST API | [json2video.com](https://json2video.com) |

### Verdict on Video Assembly

**Best free:** FFmpeg + MoviePy. You can script the entire assembly in Python. Ken Burns zoom on images, crossfade transitions, text overlays with custom fonts, background music mixing, subtitle rendering. Zero cost. Runs anywhere.

**Best cloud API:** Shotstack or Creatomate. Send a JSON timeline, get back a rendered video. Creatomate has better templates for social content. Shotstack is more flexible.

**For this pipeline:** Start with FFmpeg + MoviePy (free, local, unlimited). If you need fancier templates or faster renders, upgrade to Creatomate ($54/mo).

---

## 4. Existing Open Source Pipelines

### Ready-Made Projects on GitHub

| Project | What It Does | Stack | Stars | Link |
|---------|-------------|-------|-------|------|
| **short-video-maker** | Text to finished short video. TTS narration, captions, B-roll from Pexels, background music | Node/TypeScript, Kokoro TTS, Pexels API, MCP + REST | 5k+ | [github.com/gyoridavid/short-video-maker](https://github.com/gyoridavid/short-video-maker) |
| **ViMax** | End-to-end agentic video: scriptwriting, storyboarding, character creation, video generation | Python, multi-agent | New | [github.com/HKUDS/ViMax](https://github.com/HKUDS/ViMax) |
| **ai-video-generator** | Story-based video automation | Python | Moderate | [github.com/ccallazans/ai-video-generator](https://github.com/ccallazans/ai-video-generator) |
| **FullyAutomatedRedditVideoMakerBot** | Reddit stories to TikTok/Reels/Shorts. Auto-posts to all 3 platforms | Python | Active | [github.com/raga70/FullyAutomatedRedditVideoMakerBot](https://github.com/raga70/FullyAutomatedRedditVideoMakerBot) |
| **Reelsfy** | Cuts long videos into Reels. Face tracking, GPT for highlight selection, Whisper captions | Python, OpenAI, FFmpeg | Moderate | [github.com/eddieoz/reels-clips-automator](https://github.com/eddieoz/reels-clips-automator) |

### Key Takeaway from Existing Pipelines

The **short-video-maker** project is the closest to what you want. It is:
- Completely free to self-host
- Exposes both REST and MCP endpoints (works with n8n)
- Uses Kokoro TTS (free, local)
- Pulls B-roll from Pexels (free API)
- Generates captions automatically
- Outputs vertical video ready for Reels/TikTok/Shorts

The gap: it uses stock B-roll video, not AI-generated images. You would swap the Pexels layer for AI image generation to get the cinematic story-reel look.

---

## 5. Recommended Stacks

### Stack A: Best Quality (paid, ~$0.80-$2.50 per reel)

| Component | Tool | Cost |
|-----------|------|------|
| Voice/Narration | ElevenLabs Creator (Eleven v3) | $11/mo (100k chars, ~50-80 reels) |
| Image Generation | GPT Image 1 Medium via OpenAI API | $0.042/image x 10 images = $0.42/reel |
| Video Assembly | FFmpeg + MoviePy (Python) | Free |
| Background Music | Pixabay or Uppbeat (royalty-free) | Free |
| Text Overlays | MoviePy drawtext or Pillow | Free |
| **Total per reel** | | **~$0.55-$0.65** (after amortizing ElevenLabs) |

### Stack B: Best Budget (mostly free, ~$0.02-$0.10 per reel)

| Component | Tool | Cost |
|-----------|------|------|
| Voice/Narration | Chatterbox or XTTS-v2 (local) | Free |
| Image Generation | Stable Diffusion XL or Flux (local) | Free (need GPU) |
| Video Assembly | FFmpeg + MoviePy (Python) | Free |
| Background Music | Pixabay (royalty-free) | Free |
| Text Overlays | MoviePy or Pillow | Free |
| **Total per reel** | | **$0.00** (just electricity + your GPU) |

### Stack C: Cloud-First / No GPU (paid, ~$1.00-$1.50 per reel)

| Component | Tool | Cost |
|-----------|------|------|
| Voice/Narration | ElevenLabs Starter | $5/mo (30k chars, ~20-30 reels) |
| Image Generation | Google Imagen 4 Fast | $0.02/image x 10 = $0.20/reel |
| Video Assembly | Creatomate Essential | $54/mo (200 videos) |
| Background Music | Pixabay | Free |
| **Total per reel** | | **~$0.50 + subscriptions** |

---

## 6. Cost Per Reel Estimates

Assuming a 60-second story reel with 8-10 scene images, narration, background music, and text overlays.

### Detailed Breakdown (Stack A)

| Component | Unit Cost | Units | Cost |
|-----------|----------|-------|------|
| ElevenLabs narration | ~$0.14 per 1k chars (Creator plan) | ~1,500 chars for 60s script | $0.21 |
| GPT Image 1 (Medium) | $0.042 per image | 10 images | $0.42 |
| FFmpeg assembly | Free | 1 render | $0.00 |
| Background music | Free (Pixabay) | 1 track | $0.00 |
| **Total** | | | **$0.63 per reel** |

### At Scale (100 reels/month)

| Stack | Monthly Cost |
|-------|-------------|
| Stack A (Quality) | ~$74 ($11 ElevenLabs + ~$63 images) |
| Stack B (Budget) | ~$0 (local GPU only) |
| Stack C (Cloud) | ~$79 ($5 ElevenLabs + $20 images + $54 Creatomate) |

---

## 7. Quick-Start Guide

### Today (Day 1): Get your first reel out

1. **Sign up for ElevenLabs** (free tier, 10k characters/month)
   - Go to [elevenlabs.io](https://elevenlabs.io)
   - Create account, pick a voice, test emotional delivery
   - Use Eleven v3 model for best results
   - Generate narration for your first story script

2. **Sign up for OpenAI API** (if you don't already have one)
   - Go to [platform.openai.com](https://platform.openai.com)
   - Add $5 in credits
   - Use GPT Image 1 endpoint to generate 10 scene images
   - Prompt format: "Cinematic, warm lighting, shallow depth of field. Scene: [description]. Style: emotional, storytelling, photorealistic."

3. **Install MoviePy**
   ```
   pip install moviepy
   brew install ffmpeg  # if not already installed
   ```

4. **Download free music** from [pixabay.com/music](https://pixabay.com/music/) (emotional/cinematic category)

5. **Assemble with this Python pattern:**
   ```python
   from moviepy.editor import (
       ImageClip, AudioFileClip, CompositeVideoClip,
       concatenate_videoclips, TextClip
   )

   # Load narration audio
   narration = AudioFileClip("narration.mp3")

   # Create image clips (Ken Burns zoom effect)
   clips = []
   for i, img_path in enumerate(image_paths):
       clip = (ImageClip(img_path)
               .set_duration(segment_duration)
               .resize(height=1920)
               .fx(vfx.resize, lambda t: 1 + 0.02*t))  # slow zoom
       clips.append(clip)

   # Concatenate with crossfade
   video = concatenate_videoclips(clips, method="compose")

   # Add narration + background music
   bg_music = AudioFileClip("music.mp3").volumex(0.15)
   final_audio = CompositeAudioClip([narration, bg_music])
   video = video.set_audio(final_audio)

   # Export vertical (1080x1920)
   video.write_videofile("reel.mp4", fps=30)
   ```

### This Week (Days 2-5): Automate the pipeline

1. **Write a Python script** that:
   - Takes a story text as input
   - Splits it into scenes (use Claude or GPT to do scene splitting)
   - Calls ElevenLabs API for each scene's narration
   - Calls OpenAI API for each scene's image
   - Assembles everything with MoviePy
   - Outputs a finished 9:16 reel

2. **Clone short-video-maker** for reference:
   ```
   git clone https://github.com/gyoridavid/short-video-maker
   ```
   Study how it handles scene splitting, caption timing, and audio sync.

3. **Set up a project folder:**
   ```
   ~/behique/content-empire/
     reel-pipeline/
       pipeline.py        # main script
       templates/          # text overlay templates
       output/             # finished reels
       assets/
         music/            # background tracks
         fonts/            # custom fonts for overlays
   ```

### Next Week: Scale and Polish

1. Upgrade ElevenLabs to Creator ($11/mo) for more characters
2. Add text overlay animations (MoviePy or switch to Remotion for fancier effects)
3. Build a batch mode: feed a list of stories, wake up to finished reels
4. Test posting to Instagram/TikTok (can automate with their APIs or use Later/Buffer)

---

## Key Links

### Voice/TTS
- ElevenLabs: [elevenlabs.io/pricing](https://elevenlabs.io/pricing)
- ElevenLabs API docs: [elevenlabs.io/docs](https://elevenlabs.io/docs/overview/capabilities/text-to-speech)
- Chatterbox (free, local): [github.com/resemble-ai/chatterbox](https://www.resemble.ai/chatterbox/)
- EmotiVoice (free, local): [github.com/netease-youdao/EmotiVoice](https://github.com/netease-youdao/EmotiVoice)
- XTTS-v2 (free, local): [github.com/coqui-ai/TTS](https://github.com/coqui-ai/TTS)

### Image Generation
- OpenAI API (GPT Image): [platform.openai.com](https://platform.openai.com)
- OpenAI pricing: [openai.com/api/pricing](https://openai.com/api/pricing/)
- Leonardo.ai: [leonardo.ai/pricing](https://leonardo.ai/pricing)
- Flux (Black Forest Labs): [blackforestlabs.ai](https://blackforestlabs.ai)
- Stable Diffusion: [stability.ai](https://stability.ai)

### Video Assembly
- MoviePy docs: [zulko.github.io/moviepy](https://zulko.github.io/moviepy/getting_started/quick_presentation.html)
- Shotstack: [shotstack.io](https://shotstack.io/pricing/)
- Creatomate: [creatomate.com](https://creatomate.com/pricing)
- Remotion: [remotion.dev](https://remotion.dev)

### Open Source Pipelines
- short-video-maker: [github.com/gyoridavid/short-video-maker](https://github.com/gyoridavid/short-video-maker)
- ViMax: [github.com/HKUDS/ViMax](https://github.com/HKUDS/ViMax)
- Reddit Video Bot: [github.com/raga70/FullyAutomatedRedditVideoMakerBot](https://github.com/raga70/FullyAutomatedRedditVideoMakerBot)

### Free Music
- Pixabay Music: [pixabay.com/music](https://pixabay.com/music/)
- Uppbeat: [uppbeat.io](https://uppbeat.io)

---

## Bottom Line

The entire pipeline is buildable today. The recommended starting stack is:

- **ElevenLabs** ($11/mo) for voice
- **OpenAI GPT Image 1** (~$0.42 per reel for 10 images) for visuals
- **FFmpeg + MoviePy** (free) for assembly
- **Pixabay** (free) for background music

Total cost: roughly $0.63 per reel, or about $74/month for 100 reels. The whole thing runs from a single Python script on your Mac. No cloud infra needed. No manual editing. Feed it a story, get back a reel.

If you want zero cost, run Chatterbox/XTTS-v2 + Stable Diffusion locally. Quality is 70-80% of the paid stack but it is completely free and unlimited.
