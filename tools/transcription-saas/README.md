# Behike Transcribe

Video-to-text transcription SaaS. Paste any video URL, get a full transcript back.

Supports YouTube, Instagram, TikTok, Facebook, X/Twitter, and any platform yt-dlp supports.

## Requirements

- Python 3.10+
- ffmpeg installed (`brew install ffmpeg`)

## Setup

```bash
cd tools/transcription-saas
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000

## API

### POST /transcribe

```json
{
  "url": "https://youtube.com/watch?v=...",
  "language": "en"
}
```

Response:

```json
{
  "text": "Full transcript text...",
  "title": "Video Title",
  "language": "en",
  "duration_seconds": 120.5,
  "processing_time_seconds": 8.3,
  "segments": [
    {"start": 0.0, "end": 3.5, "text": "First segment..."}
  ]
}
```

### GET /health

```json
{"status": "ok", "model": "base"}
```

## Configuration

Environment variables:

- `WHISPER_MODEL` - Whisper model size: tiny, base, small, medium, large (default: base)
- `RATE_LIMIT` - Rate limit string (default: 5/hour)
- `HOST` - Bind host (default: 0.0.0.0)
- `PORT` - Bind port (default: 8000)

## Rate Limits

Free tier: 5 transcripts per hour per IP address.
