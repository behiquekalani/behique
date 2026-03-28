# Frequency / Manifestation Video Generator

Automated pipeline that generates 2-hour angel number frequency videos for YouTube.
Style: ambient sounds + glowing number images + subliminal affirmations.
Reference channel: @inoneness

## Quick Start (Cobo - Windows)

### 1. Install dependencies

```bash
pip install Pillow
```

### 2. Install FFmpeg

Download from https://ffmpeg.org/download.html
Add to PATH: `C:\ffmpeg\bin`

Verify: `ffmpeg -version`

### 3. (Optional) Install TTS for subliminal affirmations

```bash
# Option A: espeak
# Download from http://espeak.sourceforge.net/download.html

# Option B: piper (better quality)
pip install piper-tts
```

Without TTS, videos still generate fine, just without subliminal affirmations.

### 4. Add ambient sounds

Drop .mp3 or .wav files into `sounds/` directory.
Good sources:
- freesound.org (search "ambient", "432hz", "singing bowl", "rain")
- YouTube Audio Library (filter by "ambient")
- Generate with Suno/Udio (prompt: "ambient meditation frequency 432hz drone")

The script picks a random file from sounds/ each run.

### 5. Generate a video

```bash
python generate.py
```

Output goes to `output/` - both the .mp4 video and .json metadata.

### 6. Upload to YouTube

#### Automatic (API)

1. Go to https://console.cloud.google.com
2. Create project, enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop app)
4. Download client_secrets.json
5. Set env var: `set YOUTUBE_CLIENT_SECRET=C:\path\to\client_secrets.json`
6. Install: `pip install google-api-python-client google-auth-oauthlib`
7. Run: `python upload.py`

First run opens browser for OAuth consent. Token cached after that.

#### Manual

If no API is configured, `upload.py` saves a .upload-instructions.txt file
with the title, description, and tags ready to copy-paste into YouTube Studio.

## Automate Daily (Windows Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task: "Frequency Video Generator"
3. Trigger: Daily, pick a time (e.g., 3:00 AM)
4. Action: Start a program
   - Program: `python` (or full path like `C:\Python311\python.exe`)
   - Arguments: `C:\path\to\frequency-generator\run_daily.py`
   - Start in: `C:\path\to\frequency-generator`
5. Check "Run whether user is logged on or not"

Logs go to `logs/run-YYYYMMDD.log`.

## File Structure

```
frequency-generator/
  generate.py          - Main video generation pipeline
  upload.py            - YouTube upload (API or manual instructions)
  run_daily.py         - Daily orchestrator for Task Scheduler
  themes.json          - Angel number configs (color, meaning, title)
  affirmations.json    - 50 affirmations across 5 categories
  sounds/              - Drop ambient .mp3/.wav files here
  output/              - Generated videos, images, metadata
  logs/                - Daily run logs
```

## Revenue Projections

Based on channels like @inoneness (2M+ views on top videos):

- Meditation/frequency niche CPM: $3-8
- 1 video/day = 30 videos/month
- Conservative: 500 views/video avg = 15,000 views/month = $45-120/month
- Growth phase (6 months): 5,000 views/video = $150-400/month
- Viral potential: single video can hit 100K+ views = $300-800 per video

Key growth factors:
- Consistency (daily uploads signal algorithm)
- SEO titles with angel numbers (high search volume)
- 2-hour length maximizes watch time
- Thumbnail quality (use the generated glow images)
- First 50 videos build the channel foundation

Cost: $0 (runs on hardware you own, free tools).
Time: 0 minutes per day once automated.

## Customization

### Add new angel numbers

Edit `themes.json`. Add any number with color, meaning, keywords, title template.

### Change video duration

In `generate.py`, change `DURATION_SECONDS = 7200` to whatever you want.

### Change image style

Edit `generate_glow_image()` in `generate.py`. Current style: black background,
glowing text, scattered star particles, subtle color vignette.

### Add more affirmations

Edit `affirmations.json`. Add new categories or expand existing ones.
