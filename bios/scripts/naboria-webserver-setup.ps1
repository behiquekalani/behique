# ============================================
# NABORIA WEB SERVER SETUP
# Turns Naboria into a website hosting server
# Paste into PowerShell on Naboria
# ============================================

# 1. Install Python http server with HTTPS support
New-Item -ItemType Directory -Force -Path C:\behique\webserver
New-Item -ItemType Directory -Force -Path C:\behique\webserver\sites
New-Item -ItemType Directory -Force -Path C:\behique\webserver\logs

# 2. Copy store files from Syncthing
# (These sync automatically from Ceiba's themes/behike-store/landing-pages/)

# 3. Web server script
@'
import http.server
import socketserver
import sys
import os
from pathlib import Path
from datetime import datetime

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 80
SITES_DIR = Path(r"C:\behique\themes\behike-store\landing-pages")
LOG_FILE = Path(r"C:\behique\webserver\logs\access.log")

class LoggingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITES_DIR), **kwargs)

    def log_message(self, format, *args):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{ts}] {self.client_address[0]} {format % args}\n"
        with open(LOG_FILE, "a") as f:
            f.write(msg)

if __name__ == "__main__":
    print(f"Behike Store serving on port {PORT}")
    print(f"Site directory: {SITES_DIR}")
    print(f"Access log: {LOG_FILE}")
    with socketserver.TCPServer(("0.0.0.0", PORT), LoggingHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
'@ | Out-File -FilePath C:\behique\webserver\server.py -Encoding utf8

# 4. Start script
@'
@echo off
echo Starting Behike Store on Naboria...
echo Press Ctrl+C to stop
cd C:\behique
python webserver\server.py 80
'@ | Out-File -FilePath "$env:USERPROFILE\Desktop\Start-WebServer.bat" -Encoding ascii

# 5. Auto-start on boot (optional)
$trigger = New-ScheduledTaskTrigger -AtStartup
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\behique\webserver\server.py 80" -WorkingDirectory "C:\behique"
Register-ScheduledTask -TaskName "BehikeWebServer" -Trigger $trigger -Action $action -RunLevel Highest -Description "Behike Store Web Server" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NABORIA WEB SERVER READY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Start: Desktop\Start-WebServer.bat"
Write-Host "  Or auto-starts on boot"
Write-Host "  Access: http://192.168.0.152"
Write-Host ""
Write-Host "  To make it public:" -ForegroundColor Yellow
Write-Host "  1. Set up Cloudflare Tunnel (free)"
Write-Host "     cloudflared tunnel --url http://localhost:80"
Write-Host "  2. Point behike.shop DNS to the tunnel"
Write-Host "  3. Free HTTPS, free hosting, runs on your hardware"
Write-Host ""
