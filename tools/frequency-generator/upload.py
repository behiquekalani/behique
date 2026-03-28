#!/usr/bin/env python3
"""
YouTube Upload Script for Frequency Generator videos.
Uses the YouTube Data API v3 via google-api-python-client.

Requires:
  pip install google-api-python-client google-auth-oauthlib

Set env var YOUTUBE_CLIENT_SECRET to the path of your OAuth client_secrets.json file.
On first run, it will open a browser for OAuth consent. Token is cached afterward.

If no credentials are available, saves upload instructions to a text file instead.
"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"


def upload_with_api(metadata_path):
    """Upload video to YouTube using the Data API."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
    except ImportError:
        print("[UPLOAD] google-api-python-client not installed.")
        print("         Run: pip install google-api-python-client google-auth-oauthlib")
        return False

    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    if not client_secret or not os.path.exists(client_secret):
        print("[UPLOAD] YOUTUBE_CLIENT_SECRET env var not set or file not found.")
        return False

    # Load metadata
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    video_path = meta["video_path"]
    if not os.path.exists(video_path):
        print(f"[UPLOAD] Video file not found: {video_path}")
        return False

    # Auth
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    token_path = BASE_DIR / "youtube_token.pickle"
    creds = None

    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": meta["description"][:5000],
            "tags": meta["tags"][:500],
            "categoryId": meta.get("category", "10"),
        },
        "status": {
            "privacyStatus": meta.get("privacy", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=50 * 1024 * 1024,  # 50MB chunks
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    print(f"[UPLOAD] Uploading: {meta['title']}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[UPLOAD] Progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[UPLOAD] Done! https://youtube.com/watch?v={video_id}")
    return True


def save_upload_instructions(metadata_path):
    """Save manual upload instructions when API is not configured."""
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    instructions_path = Path(meta["video_path"]).with_suffix(".upload-instructions.txt")

    lines = [
        "MANUAL UPLOAD INSTRUCTIONS",
        "=" * 50,
        "",
        f"Video file: {meta['video_path']}",
        "",
        "Go to: https://studio.youtube.com",
        "Click 'Create' > 'Upload videos'",
        "Select the video file above",
        "",
        "TITLE (copy this):",
        "-" * 30,
        meta["title"],
        "",
        "DESCRIPTION (copy this):",
        "-" * 30,
        meta["description"],
        "",
        "TAGS (copy this, comma-separated):",
        "-" * 30,
        ", ".join(meta["tags"]),
        "",
        "SETTINGS:",
        f"  Category: Music",
        f"  Privacy: {meta.get('privacy', 'public')}",
        f"  Made for kids: No",
        "",
        "THUMBNAIL:",
        f"  Use the generated image from output/ directory",
        f"  Look for: {Path(meta['video_path']).stem}.png",
    ]

    with open(instructions_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[UPLOAD] No API configured. Instructions saved to:")
    print(f"         {instructions_path}")
    return instructions_path


def main(metadata_path=None):
    if metadata_path is None:
        # Find the most recent metadata JSON in output/
        if not OUTPUT_DIR.exists():
            print("[UPLOAD] No output directory found.")
            sys.exit(1)

        json_files = sorted(OUTPUT_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
        if not json_files:
            print("[UPLOAD] No metadata JSON files found in output/")
            sys.exit(1)

        metadata_path = str(json_files[0])

    print(f"[UPLOAD] Using metadata: {metadata_path}")

    # Try API upload first, fall back to instructions
    if not upload_with_api(metadata_path):
        save_upload_instructions(metadata_path)


if __name__ == "__main__":
    meta_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(meta_path)
