#!/usr/bin/env python3
"""
BIOS Run All - Single command to run full pipeline and serve dashboard.

Usage:
    python3 bios/run_all.py              # Run pipeline once, start dashboard
    python3 bios/run_all.py --daemon     # Run pipeline on loop + dashboard
    python3 bios/run_all.py --pipeline   # Pipeline only, no dashboard
    python3 bios/run_all.py --serve      # Dashboard only, no pipeline
"""

import json
import os
import subprocess
import sys
import time
import threading
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BIOS_DIR = BASE_DIR / "bios"
STORAGE_DIR = BIOS_DIR / "storage"
DASHBOARD_DIR = BIOS_DIR / "dashboard"

PIPELINE_STEPS = [
    ("News", "python3 bios/ingestion/news_fetcher.py"),
    ("Polymarket", "python3 bios/ingestion/polymarket_fetcher.py"),
    ("Reddit", "python3 bios/ingestion/reddit_signal.py"),
    ("Intelligence", "python3 bios/intelligence/causal_engine.py"),
]

DASHBOARD_PORT = 8092
INTERVAL_MINUTES = 30


def run_step(name, command):
    print(f"  [{name}]", end=" ", flush=True)
    start = time.time()
    try:
        result = subprocess.run(
            command.split(), cwd=str(BASE_DIR),
            capture_output=True, text=True, timeout=120
        )
        duration = time.time() - start
        status = "OK" if result.returncode == 0 else "FAIL"
        print(f"{status} ({duration:.1f}s)")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def run_pipeline():
    print(f"\n  BIOS Pipeline - {datetime.now().strftime('%H:%M:%S')}")
    print("  " + "-" * 40)
    results = {}
    for name, cmd in PIPELINE_STEPS:
        results[name] = run_step(name, cmd)

    # Count signals
    try:
        with open(STORAGE_DIR / "signals.json") as f:
            signals = json.load(f)
        print(f"  Total signals: {len(signals)}")
    except Exception:
        pass

    # Count insights
    try:
        with open(STORAGE_DIR / "insights.json") as f:
            insights = json.load(f)
        actionable = sum(1 for i in insights if i.get("action_level") == "ACTIONABLE")
        print(f"  Insights: {len(insights)} ({actionable} actionable)")
    except Exception:
        pass

    ok = sum(1 for v in results.values() if v)
    print(f"  Result: {ok}/{len(results)} steps passed")
    return all(results.values())


def start_dashboard():
    """Start dashboard HTTP server in background."""
    import http.server
    import socketserver

    os.chdir(str(DASHBOARD_DIR))

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress request logs

    try:
        with socketserver.TCPServer(("0.0.0.0", DASHBOARD_PORT), QuietHandler) as httpd:
            print(f"  Dashboard: http://192.168.0.145:{DASHBOARD_PORT}")
            httpd.serve_forever()
    except OSError:
        print(f"  Dashboard already running on port {DASHBOARD_PORT}")


def daemon_loop():
    """Run pipeline every INTERVAL_MINUTES."""
    print(f"  Daemon mode: pipeline every {INTERVAL_MINUTES}m")
    print(f"  Press Ctrl+C to stop\n")

    while True:
        run_pipeline()
        print(f"\n  Next run in {INTERVAL_MINUTES}m...")
        time.sleep(INTERVAL_MINUTES * 60)


def send_telegram_summary():
    """Send a quick summary to Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return

    try:
        with open(STORAGE_DIR / "insights.json") as f:
            insights = json.load(f)
        actionable = [i for i in insights if i.get("action_level") == "ACTIONABLE"]
        if not actionable:
            return

        msg = "BIOS Alert:\n"
        for ins in actionable[:3]:
            name = ins.get("pattern", "?").replace("_", " ").title()
            conf = ins.get("confidence", 0)
            msg += f"  {name} ({conf:.0%})\n"

        import urllib.request
        data = json.dumps({"chat_id": chat_id, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def main():
    print("\n  BIOS - Behike Intelligence Operating System")
    print("  " + "=" * 45)

    if "--serve" in sys.argv:
        start_dashboard()
        return

    if "--pipeline" in sys.argv:
        run_pipeline()
        send_telegram_summary()
        return

    if "--daemon" in sys.argv:
        # Start dashboard in background thread
        dash_thread = threading.Thread(target=start_dashboard, daemon=True)
        dash_thread.start()
        time.sleep(1)

        # Run pipeline loop
        try:
            daemon_loop()
        except KeyboardInterrupt:
            print("\n  Shutting down.")
        return

    # Default: run once + start dashboard
    run_pipeline()
    send_telegram_summary()
    print(f"\n  Starting dashboard...")
    start_dashboard()


if __name__ == "__main__":
    main()
