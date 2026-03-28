#!/usr/bin/env python3
"""
Reel Download Server
Serves Instagram-ready reels on the local network.
Access from phone: http://192.168.0.145:8092

Features:
- Visual gallery of all finished reels with video preview
- One-tap download to phone
- Copy-paste Instagram captions
- Posting schedule view
"""

import http.server
import json
import os
import urllib.parse
from pathlib import Path

PORT = 8092
PIPELINE_DIR = Path(__file__).parent
INSTAGRAM_DIR = PIPELINE_DIR / "instagram_ready"
STORIES_DIR = PIPELINE_DIR / "stories"


class ReelHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "":
            self.serve_gallery()
        elif path.startswith("/video/"):
            self.serve_video(path[7:])
        elif path.startswith("/caption/"):
            self.serve_caption(path[9:])
        elif path.startswith("/download/"):
            self.serve_download(path[10:])
        else:
            self.send_error(404)

    def serve_gallery(self):
        reels = []
        if INSTAGRAM_DIR.exists():
            for mp4 in sorted(INSTAGRAM_DIR.glob("*.mp4")):
                name = mp4.stem
                size_mb = mp4.stat().st_size / (1024 * 1024)
                caption_file = INSTAGRAM_DIR / f"{name}_caption.txt"
                caption = caption_file.read_text() if caption_file.exists() else ""
                title = name.replace("-", " ").title()
                reels.append({
                    "name": name,
                    "title": title,
                    "size_mb": round(size_mb, 1),
                    "caption": caption,
                })

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Reel Hub</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: #0a0a0a; color: #fff;
    font-family: -apple-system, system-ui, sans-serif;
    -webkit-tap-highlight-color: transparent;
}}
.header {{
    text-align: center; padding: 20px 16px 12px;
    background: linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%);
}}
.header h1 {{ font-size: 1.5em; font-weight: 700; }}
.header .count {{ font-size: 0.85em; opacity: 0.8; margin-top: 4px; }}
.reel-list {{ padding: 12px; }}
.reel-card {{
    background: #1a1a1a; border-radius: 16px; margin-bottom: 16px;
    overflow: hidden; border: 1px solid #2a2a2a;
}}
.reel-card video {{
    width: 100%; max-height: 400px; object-fit: cover; background: #000;
    display: block;
}}
.reel-info {{ padding: 14px 16px; }}
.reel-title {{ font-size: 1.1em; font-weight: 600; margin-bottom: 6px; }}
.reel-meta {{ color: #888; font-size: 0.8em; margin-bottom: 12px; }}
.btn-row {{ display: flex; gap: 8px; margin-bottom: 10px; }}
.btn {{
    flex: 1; padding: 12px; border: none; border-radius: 10px;
    font-size: 0.9em; font-weight: 600; cursor: pointer;
    text-align: center; text-decoration: none; display: block;
}}
.btn-download {{
    background: linear-gradient(135deg, #833ab4, #fd1d1d);
    color: white;
}}
.btn-caption {{
    background: #2a2a2a; color: #fff;
}}
.caption-box {{
    display: none; background: #111; border-radius: 10px;
    padding: 12px; margin-top: 8px; font-size: 0.8em;
    color: #ccc; white-space: pre-wrap; max-height: 200px;
    overflow-y: auto; position: relative;
}}
.caption-box.show {{ display: block; }}
.copy-btn {{
    position: absolute; top: 8px; right: 8px;
    background: #333; color: #fff; border: none;
    padding: 6px 12px; border-radius: 6px; font-size: 0.75em;
    cursor: pointer;
}}
.copy-btn.copied {{ background: #4CAF50; }}
.empty {{
    text-align: center; padding: 60px 20px; color: #555;
}}
</style>
</head>
<body>
<div class="header">
    <h1>Reel Hub</h1>
    <div class="count">{len(reels)} reels ready to post</div>
</div>
<div class="reel-list">
"""

        if not reels:
            html += '<div class="empty">No reels ready yet. Pipeline is working...</div>'
        else:
            for i, reel in enumerate(reels):
                caption_escaped = reel["caption"].replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
                html += f"""
    <div class="reel-card">
        <video src="/video/{reel['name']}" controls preload="none" playsinline></video>
        <div class="reel-info">
            <div class="reel-title">{reel['title']}</div>
            <div class="reel-meta">{reel['size_mb']} MB</div>
            <div class="btn-row">
                <a class="btn btn-download" href="/download/{reel['name']}" download="{reel['name']}.mp4">Download</a>
                <button class="btn btn-caption" onclick="toggleCaption({i})">Caption</button>
            </div>
            <div class="caption-box" id="cap-{i}">
                <button class="copy-btn" onclick="copyCaption({i})">Copy</button>
                <span id="cap-text-{i}">{caption_escaped}</span>
            </div>
        </div>
    </div>
"""

        html += """
</div>
<script>
function toggleCaption(i) {
    document.getElementById('cap-'+i).classList.toggle('show');
}
function copyCaption(i) {
    const text = document.getElementById('cap-text-'+i).textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('cap-'+i).querySelector('.copy-btn');
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
    });
}
</script>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_video(self, name):
        path = INSTAGRAM_DIR / f"{name}.mp4"
        if not path.exists():
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(path.stat().st_size))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        with open(path, "rb") as f:
            self.wfile.write(f.read())

    def serve_caption(self, name):
        path = INSTAGRAM_DIR / f"{name}_caption.txt"
        if not path.exists():
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(path.read_bytes())

    def serve_download(self, name):
        path = INSTAGRAM_DIR / f"{name}.mp4"
        if not path.exists():
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Disposition", f'attachment; filename="{name}.mp4"')
        self.send_header("Content-Length", str(path.stat().st_size))
        self.end_headers()
        with open(path, "rb") as f:
            self.wfile.write(f.read())

    def log_message(self, fmt, *args):
        print(f"[ReelHub] {args[0]}")


if __name__ == "__main__":
    os.chdir(PIPELINE_DIR)
    print(f"[ReelHub] Starting on port {PORT}")
    print(f"[ReelHub] Access from phone: http://192.168.0.145:{PORT}")
    print(f"[ReelHub] Serving {len(list(INSTAGRAM_DIR.glob('*.mp4')))} reels")
    server = http.server.HTTPServer(("0.0.0.0", PORT), ReelHandler)
    server.serve_forever()
