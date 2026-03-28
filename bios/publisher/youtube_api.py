#!/usr/bin/env python3
"""
YouTube Data API v3 uploader.
Uploads videos via resumable upload and fetches channel stats.
Falls back to saving upload instructions if no credentials are set.

Env vars or ~/.env.youtube:
  YOUTUBE_CLIENT_SECRET  (path to client_secret.json)
"""

import argparse
import json
import os
import sys
from pathlib import Path

PUBLISHER_DIR = Path(__file__).parent
LOGS_DIR = PUBLISHER_DIR / "logs"
TOKEN_FILE = Path.home() / ".youtube_oauth_token.json"

# YouTube category IDs: 22=People&Blogs, 28=Science&Tech, 24=Entertainment, 10=Music
CATEGORIES = {"science": "28", "tech": "28", "entertainment": "24", "music": "10",
              "people": "22", "education": "27", "howto": "26", "gaming": "20"}


def _load_config():
    """Load client secret path from env or ~/.env.youtube."""
    secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    if secret:
        return secret
    env_file = Path.home() / ".env.youtube"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "YOUTUBE_CLIENT_SECRET":
                    return v.strip().strip("\"'")
    return None


def _get_service(client_secret_path):
    """Build an authenticated YouTube API service object."""
    try:
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("Install: pip install google-api-python-client google-auth-oauthlib")
        return None
    scopes = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube.readonly"]
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes) if TOKEN_FILE.exists() else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not Path(client_secret_path).exists():
            print(f"Client secret not found: {client_secret_path}"); return None
        else:
            creds = InstalledAppFlow.from_client_secrets_file(client_secret_path, scopes).run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload_video(file_path, title, description="", tags=None, category="28", privacy="private"):
    """
    Upload a video via YouTube Data API v3 with resumable upload.
    Returns the video ID on success, or None on fallback.
    """
    video = Path(file_path)
    if not video.exists():
        print(f"Error: Video file not found: {file_path}")
        return None

    secret_path = _load_config()
    if not secret_path:
        return _fallback_instructions(file_path, title, description, tags, category)

    service = _get_service(secret_path)
    if not service:
        return _fallback_instructions(file_path, title, description, tags, category)

    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return _fallback_instructions(file_path, title, description, tags, category)

    # Resolve category name to ID
    cat_id = CATEGORIES.get(category.lower(), category)

    body = {
        "snippet": {"title": title, "description": description, "tags": tags or [], "categoryId": cat_id},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(str(video), chunksize=10 * 1024 * 1024, resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    print(f"Uploading: {video.name} ({video.stat().st_size / 1024 / 1024:.1f} MB)")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}% uploaded")

    vid_id = response["id"]
    print(f"Upload complete. Video ID: {vid_id}")
    print(f"  https://www.youtube.com/watch?v={vid_id}")
    return vid_id


def _fallback_instructions(file_path, title, description, tags, category):
    """Save upload instructions when API is not configured."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = "".join(c for c in title[:30] if c.isalnum() or c in " -_").strip().replace(" ", "_")
    out_file = LOGS_DIR / f"yt-upload-{safe_title}.json"

    data = {"file": str(file_path), "title": title, "description": description,
            "tags": tags or [], "category": category,
            "instructions": f"1. studio.youtube.com > Upload  2. Select: {file_path}  3. Title: {title}"}
    out_file.write_text(json.dumps(data, indent=2))
    print(f"No API credentials. Upload instructions saved to: {out_file}")
    print("Set YOUTUBE_CLIENT_SECRET in env or ~/.env.youtube to enable API uploads.")
    return None


def get_channel_stats():
    """Fetch subscriber count, view count, video count."""
    secret_path = _load_config()
    if not secret_path:
        print("No API credentials. Set YOUTUBE_CLIENT_SECRET in env or ~/.env.youtube"); return None
    service = _get_service(secret_path)
    if not service:
        return None
    resp = service.channels().list(part="snippet,statistics", mine=True).execute()
    for ch in resp.get("items", []):
        s = ch["statistics"]
        print(f"{ch['snippet']['title']} | {s.get('subscriberCount','?')} subs | {s.get('viewCount','?')} views | {s.get('videoCount','?')} videos")
        return s
    print("No channel found."); return None


def main():
    p = argparse.ArgumentParser(description="YouTube Data API v3 uploader")
    p.add_argument("--upload", help="Path to video file")
    p.add_argument("--title", help="Video title")
    p.add_argument("--description", default="", help="Video description")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--category", default="28", help="Category ID or name")
    p.add_argument("--privacy", default="private", choices=["public", "private", "unlisted"])
    p.add_argument("--stats", action="store_true", help="Show channel stats")
    a = p.parse_args()
    if a.stats:
        get_channel_stats()
    elif a.upload:
        if not a.title:
            print("Error: --title required"); sys.exit(1)
        tags = [t.strip() for t in a.tags.split(",")] if a.tags else []
        upload_video(a.upload, a.title, a.description, tags, a.category, a.privacy)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
