#!/usr/bin/env python3
"""
Instagram Graph API publisher.
Publishes photos and carousels via the Instagram Graph API.
Falls back to clipboard mode if no API token is configured.

Env vars or ~/.env.instagram:
  INSTAGRAM_ACCESS_TOKEN
  INSTAGRAM_BUSINESS_ID
"""

import argparse
import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

API_BASE = "https://graph.facebook.com/v19.0"


def _load_config():
    """Load credentials from env vars or ~/.env.instagram."""
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    biz_id = os.environ.get("INSTAGRAM_BUSINESS_ID")
    if token and biz_id:
        return token, biz_id
    env_file = Path.home() / ".env.instagram"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip("\"'")
                if k == "INSTAGRAM_ACCESS_TOKEN":
                    token = v
                elif k == "INSTAGRAM_BUSINESS_ID":
                    biz_id = v
    return token, biz_id


def _api(method, url, **kwargs):
    """Minimal HTTP helper using requests."""
    import requests
    resp = getattr(requests, method)(url, **kwargs)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"IG API error: {data['error'].get('message', data['error'])}")
    return data


def _clipboard(text):
    """Copy text to clipboard (macOS)."""
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(text.encode())
        return True
    except Exception:
        return False


def publish_photo(image_url, caption, token=None, biz_id=None):
    """Publish a single photo. image_url must be a publicly accessible URL."""
    if not token:
        token, biz_id = _load_config()
    if not token or not biz_id:
        print("[clipboard mode] No API token. Copying caption to clipboard.")
        _clipboard(caption)
        webbrowser.open("https://www.instagram.com/")
        return {"mode": "clipboard", "caption": caption}
    # Step 1: create media container
    container = _api("post", f"{API_BASE}/{biz_id}/media", params={
        "image_url": image_url, "caption": caption, "access_token": token
    })
    cid = container["id"]
    # Step 2: publish
    result = _api("post", f"{API_BASE}/{biz_id}/media_publish", params={
        "creation_id": cid, "access_token": token
    })
    print(f"Published photo. Media ID: {result.get('id')}")
    return result


def publish_carousel(image_urls, caption, token=None, biz_id=None):
    """Publish a carousel post. image_urls is a list of public URLs."""
    if not token:
        token, biz_id = _load_config()
    if not token or not biz_id:
        print("[clipboard mode] No API token. Copying caption to clipboard.")
        _clipboard(caption)
        webbrowser.open("https://www.instagram.com/")
        return {"mode": "clipboard", "caption": caption}
    # Create child containers
    children = []
    for url in image_urls:
        child = _api("post", f"{API_BASE}/{biz_id}/media", params={
            "image_url": url, "is_carousel_item": "true", "access_token": token
        })
        children.append(child["id"])
    # Create carousel container
    container = _api("post", f"{API_BASE}/{biz_id}/media", params={
        "media_type": "CAROUSEL", "caption": caption,
        "children": ",".join(children), "access_token": token
    })
    # Publish
    result = _api("post", f"{API_BASE}/{biz_id}/media_publish", params={
        "creation_id": container["id"], "access_token": token
    })
    print(f"Published carousel ({len(children)} images). Media ID: {result.get('id')}")
    return result


def get_insights(token=None, biz_id=None):
    """Fetch basic engagement metrics for the account."""
    if not token:
        token, biz_id = _load_config()
    if not token or not biz_id:
        print("No API token configured. Cannot fetch insights.")
        print("Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ID in env or ~/.env.instagram")
        return None
    data = _api("get", f"{API_BASE}/{biz_id}", params={
        "fields": "followers_count,media_count,username,name",
        "access_token": token
    })
    print(f"@{data.get('username', '?')} | {data.get('followers_count', 0)} followers | {data.get('media_count', 0)} posts")
    # Recent media insights
    media = _api("get", f"{API_BASE}/{biz_id}/media", params={
        "fields": "id,caption,like_count,comments_count,timestamp",
        "limit": "5", "access_token": token
    })
    for m in media.get("data", []):
        cap = (m.get("caption") or "")[:40]
        print(f"  {m.get('timestamp','')[:10]} | {m.get('like_count',0)} likes, {m.get('comments_count',0)} comments | {cap}...")
    return data


def main():
    parser = argparse.ArgumentParser(description="Instagram Graph API publisher")
    parser.add_argument("--post", type=str, help="Caption for the post")
    parser.add_argument("--image", type=str, help="Image URL (public) or local path note")
    parser.add_argument("--images", type=str, nargs="+", help="Multiple image URLs for carousel")
    parser.add_argument("--insights", action="store_true", help="Show account insights")
    args = parser.parse_args()

    if args.insights:
        get_insights()
    elif args.post and args.images:
        publish_carousel(args.images, args.post)
    elif args.post and args.image:
        publish_photo(args.image, args.post)
    elif args.post:
        # No image provided, clipboard mode
        _clipboard(args.post)
        print("Caption copied to clipboard. Opening Instagram...")
        webbrowser.open("https://www.instagram.com/")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
