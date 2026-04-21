#!/usr/bin/env python3
"""UPS monitor for Cobo.

Queries Windows WMI (Win32_Battery) for the UPS stats that PowerPanel
Personal hides behind a paywall: battery health, runtime remaining,
online/on-battery status.

Serves a live dashboard at http://localhost:9100
Logs every poll to logs/ups-YYYY-MM-DD.csv

Usage:  python ups_monitor.py
Stop:   Ctrl+C
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import threading
import time
from collections import deque
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 9100
POLL_SECONDS = 5
HISTORY_POINTS = 720          # 720 * 5s = 1 hour of sparkline data
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

BATTERY_STATUS_CODES = {
    1: "Discharging (On Battery)",
    2: "On AC Power",
    3: "Fully Charged",
    4: "Low",
    5: "Critical",
    6: "Charging",
    7: "Charging + High",
    8: "Charging + Low",
    9: "Charging + Critical",
    10: "Undefined",
    11: "Partially Charged",
}

# Shared state between poll thread and HTTP handler.
state_lock = threading.Lock()
state: dict = {
    "ok": False,
    "last_poll": None,
    "error": "Waiting for first poll...",
    "charge_pct": None,
    "runtime_min": None,
    "status_code": None,
    "status_text": None,
    "design_capacity_mwh": None,
    "full_capacity_mwh": None,
    "health_pct": None,
    "name": None,
    "history": deque(maxlen=HISTORY_POINTS),
}


def query_wmi() -> dict:
    """Return a single battery reading dict or raise on failure."""
    ps_script = (
        "Get-CimInstance -ClassName Win32_Battery | "
        "Select-Object Name, BatteryStatus, EstimatedChargeRemaining, "
        "EstimatedRunTime, DesignCapacity, FullChargeCapacity | "
        "ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"PowerShell failed: {result.stderr.strip()}")

    raw = result.stdout.strip()
    if not raw:
        raise RuntimeError("No battery/UPS detected via WMI. Check USB cable to UPS.")

    data = json.loads(raw)
    if isinstance(data, list):
        data = data[0]  # first battery; on Cobo there should only be the UPS
    return data


def poll_loop() -> None:
    log_file = None
    current_date = None
    while True:
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        if today != current_date:
            if log_file:
                log_file.close()
            log_file = open(LOG_DIR / f"ups-{today}.csv", "a", newline="")
            writer = csv.writer(log_file)
            if log_file.tell() == 0:
                writer.writerow([
                    "timestamp", "charge_pct", "runtime_min",
                    "status_code", "status_text", "health_pct",
                    "full_capacity_mwh", "design_capacity_mwh",
                ])
            current_date = today

        try:
            raw = query_wmi()
            charge = raw.get("EstimatedChargeRemaining")
            runtime = raw.get("EstimatedRunTime")
            status_code = raw.get("BatteryStatus")
            # EstimatedRunTime reports 71582788 when on AC — sentinel for "not applicable"
            if isinstance(runtime, int) and runtime > 100000:
                runtime = None
            design = raw.get("DesignCapacity")
            full = raw.get("FullChargeCapacity")
            health = None
            if design and full and design > 0:
                health = round((full / design) * 100, 1)

            reading = {
                "ts": now.isoformat(timespec="seconds"),
                "charge_pct": charge,
                "runtime_min": runtime,
                "status_code": status_code,
                "status_text": BATTERY_STATUS_CODES.get(status_code, f"Unknown ({status_code})"),
                "design_capacity_mwh": design,
                "full_capacity_mwh": full,
                "health_pct": health,
                "name": raw.get("Name"),
            }

            with state_lock:
                state.update(reading)
                state["ok"] = True
                state["last_poll"] = now.isoformat(timespec="seconds")
                state["error"] = None
                state["history"].append({
                    "ts": reading["ts"],
                    "charge": charge,
                    "code": status_code,
                })

            writer = csv.writer(log_file)
            writer.writerow([
                reading["ts"], charge, runtime, status_code, reading["status_text"],
                health, full, design,
            ])
            log_file.flush()
            print(f"[{now:%H:%M:%S}] {reading['status_text']} | "
                  f"{charge}% | runtime={runtime}min | health={health}%")

        except Exception as e:
            with state_lock:
                state["ok"] = False
                state["last_poll"] = now.isoformat(timespec="seconds")
                state["error"] = str(e)
            print(f"[{now:%H:%M:%S}] ERROR: {e}", file=sys.stderr)

        time.sleep(POLL_SECONDS)


HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>COBO // PWR-CORE</title>
<style>
  :root {
    --bg: #05080a;
    --bg2: #0a1015;
    --panel: rgba(12, 20, 26, 0.85);
    --amber: #ffb347;
    --amber-dim: #cc7a00;
    --cyan: #00e5ff;
    --cyan-dim: #007a99;
    --red: #ff3a3a;
    --red-dim: #7a0000;
    --green: #5aff9d;
    --text: #d7e3ec;
    --muted: #5a7380;
    --grid: rgba(0, 229, 255, 0.04);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }

  html, body { height: 100%; }
  body {
    background: radial-gradient(ellipse at top, var(--bg2) 0%, var(--bg) 60%);
    color: var(--text);
    font-family: "Consolas", "SF Mono", "Menlo", monospace;
    font-weight: 400; letter-spacing: 0.5px;
    padding: 24px 32px 48px;
    min-height: 100vh;
    position: relative; overflow-x: hidden;
  }
  /* Grid overlay */
  body::before {
    content: ""; position: fixed; inset: 0; pointer-events: none;
    background-image:
      linear-gradient(var(--grid) 1px, transparent 1px),
      linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: 1;
  }
  /* Scanlines */
  body::after {
    content: ""; position: fixed; inset: 0; pointer-events: none;
    background: repeating-linear-gradient(
      to bottom,
      rgba(0, 229, 255, 0.02) 0px,
      rgba(0, 229, 255, 0.02) 1px,
      transparent 1px,
      transparent 3px
    );
    z-index: 2;
  }

  .wrap { position: relative; z-index: 3; max-width: 1200px; margin: 0 auto; }

  /* Top bar */
  header {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--cyan-dim);
    padding-bottom: 14px; margin-bottom: 28px;
    position: relative;
  }
  header::after {
    content: ""; position: absolute; bottom: -1px; left: 0;
    height: 1px; width: 180px;
    background: linear-gradient(90deg, var(--amber), transparent);
  }
  .sys-title {
    color: var(--amber);
    font-size: 20px; font-weight: 700; letter-spacing: 6px;
    text-shadow: 0 0 8px rgba(255, 179, 71, 0.6);
  }
  .sys-sub {
    color: var(--muted); font-size: 10px; letter-spacing: 3px;
    margin-top: 2px; text-transform: uppercase;
  }
  .sys-meta {
    text-align: right; font-size: 10px; letter-spacing: 2px;
    color: var(--cyan); text-transform: uppercase;
  }
  .sys-meta .clock { font-size: 13px; color: var(--amber); letter-spacing: 3px; }

  /* Panel (clipped corners, corner brackets) */
  .panel {
    position: relative;
    background: var(--panel);
    border: 1px solid var(--cyan-dim);
    padding: 18px 20px;
    clip-path: polygon(
      12px 0, 100% 0, 100% calc(100% - 12px),
      calc(100% - 12px) 100%, 0 100%, 0 12px
    );
  }
  .panel::before, .panel::after {
    content: ""; position: absolute; width: 14px; height: 14px;
    border: 2px solid var(--amber); pointer-events: none;
  }
  .panel::before { top: -1px; right: -1px; border-left: 0; border-bottom: 0; }
  .panel::after  { bottom: -1px; left: -1px; border-right: 0; border-top: 0; }

  .panel h2 {
    font-size: 10px; font-weight: 700; letter-spacing: 3px;
    color: var(--cyan); text-transform: uppercase;
    margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
  }
  .panel h2::before {
    content: "▶"; color: var(--amber); font-size: 8px;
  }
  .panel h2 .tag {
    margin-left: auto; color: var(--muted); font-size: 9px;
    letter-spacing: 1.5px;
  }

  /* Big readout */
  .readout {
    font-size: 44px; font-weight: 700; letter-spacing: -1px;
    color: var(--amber);
    text-shadow: 0 0 12px rgba(255, 179, 71, 0.4);
    line-height: 1; font-variant-numeric: tabular-nums;
  }
  .readout .unit {
    font-size: 14px; color: var(--cyan); margin-left: 6px;
    letter-spacing: 2px; font-weight: 400;
  }
  .readout.small { font-size: 18px; letter-spacing: 1px; }

  /* Status colors */
  .s-on   { color: var(--green); text-shadow: 0 0 12px rgba(90, 255, 157, 0.5); }
  .s-batt { color: var(--amber); text-shadow: 0 0 14px rgba(255, 179, 71, 0.8); animation: pulse 1.2s ease-in-out infinite; }
  .s-crit { color: var(--red);   text-shadow: 0 0 16px rgba(255, 58, 58, 0.9); animation: pulse 0.6s ease-in-out infinite; }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.55; }
  }

  /* Meter bar */
  .meter {
    position: relative; height: 14px; margin-top: 14px;
    background: rgba(0, 229, 255, 0.08);
    border: 1px solid var(--cyan-dim);
  }
  .meter > .fill {
    position: absolute; inset: 0; right: auto;
    background: linear-gradient(90deg, var(--amber-dim), var(--amber));
    transition: width 0.6s ease;
    box-shadow: inset 0 0 8px rgba(255, 179, 71, 0.6);
  }
  .meter > .fill.warn { background: linear-gradient(90deg, var(--amber-dim), var(--amber)); }
  .meter > .fill.bad  { background: linear-gradient(90deg, var(--red-dim), var(--red)); }
  .meter > .fill.ok   { background: linear-gradient(90deg, #007a33, var(--green)); }
  .meter > .ticks {
    position: absolute; inset: 0;
    background-image: repeating-linear-gradient(
      90deg, transparent 0, transparent 9px,
      rgba(0, 229, 255, 0.3) 9px, rgba(0, 229, 255, 0.3) 10px
    );
    pointer-events: none;
  }

  /* Grid layout */
  .grid {
    display: grid; gap: 14px;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  }
  .grid.two { grid-template-columns: 2fr 1fr; }
  @media (max-width: 760px) {
    .grid.two { grid-template-columns: 1fr; }
  }

  /* Hero status panel — bigger */
  .hero .readout { font-size: 56px; }
  .hero { padding: 24px 28px; }
  .hero .indicator {
    display: inline-block; width: 12px; height: 12px;
    border-radius: 50%; margin-right: 10px; vertical-align: middle;
    background: currentColor; box-shadow: 0 0 10px currentColor;
  }

  /* Data rows */
  .kv { display: flex; justify-content: space-between; padding: 6px 0;
        font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;
        border-bottom: 1px dashed rgba(0, 229, 255, 0.15); }
  .kv:last-child { border: 0; }
  .kv .k { color: var(--muted); }
  .kv .v { color: var(--amber); font-weight: 700; }

  /* Error panel */
  .error {
    border: 1px solid var(--red); color: var(--red);
    background: rgba(255, 58, 58, 0.08);
    padding: 18px 22px; clip-path: polygon(
      12px 0, 100% 0, 100% calc(100% - 12px),
      calc(100% - 12px) 100%, 0 100%, 0 12px
    );
  }
  .error b { color: var(--red); letter-spacing: 3px; display: block; margin-bottom: 6px; }

  /* Footer */
  footer {
    margin-top: 32px; padding-top: 14px;
    border-top: 1px solid var(--cyan-dim);
    color: var(--muted); font-size: 10px; letter-spacing: 2px;
    display: flex; justify-content: space-between; text-transform: uppercase;
  }
  footer .blink { animation: pulse 1.5s infinite; color: var(--green); }

  /* Spacing helper */
  .mt { margin-top: 14px; }
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div>
      <div class="sys-title">COBO // PWR-CORE</div>
      <div class="sys-sub">UPS Telemetry · CyberPower HID-PD · Port 9100</div>
    </div>
    <div class="sys-meta">
      <div class="clock" id="clock">--:--:--</div>
      <div id="subtitle">link: establishing...</div>
    </div>
  </header>

  <div id="content">
    <div class="panel"><h2>Init</h2><div class="readout small">Connecting to core…</div></div>
  </div>

  <footer>
    <div>WIN32_BATTERY · 5s poll · local:9100 · logs/ups-*.csv</div>
    <div class="blink">● LINK ACTIVE</div>
  </footer>

</div>

<script>
function pad(n){ return n < 10 ? "0" + n : n; }
function clock() {
  const d = new Date();
  document.getElementById('clock').textContent =
    pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
}
setInterval(clock, 1000); clock();

function statusClass(code) {
  if (code === 2 || code === 3) return 's-on';
  if (code === 4 || code === 5) return 's-crit';
  return 's-batt';
}
function chargeFillClass(p) {
  if (p === null || p === undefined) return '';
  if (p < 20) return 'bad';
  if (p < 50) return 'warn';
  return 'ok';
}
function healthFillClass(h) {
  if (h === null || h === undefined) return '';
  if (h < 60) return 'bad';
  if (h < 80) return 'warn';
  return 'ok';
}

async function tick() {
  try {
    const r = await fetch('/api/state');
    const s = await r.json();
    render(s);
  } catch (e) {
    document.getElementById('content').innerHTML =
      '<div class="error"><b>// LINK LOST</b>Poller unreachable on 127.0.0.1:9100 — ' + e + '</div>';
  }
}

function render(s) {
  document.getElementById('subtitle').textContent =
    (s.name || 'UNKNOWN') + ' · last ping ' + (s.last_poll || '—');

  if (!s.ok) {
    document.getElementById('content').innerHTML =
      '<div class="error"><b>// NO TELEMETRY</b>' + (s.error || 'unknown fault') + '</div>';
    return;
  }

  const charge = s.charge_pct ?? 0;
  const runtime = s.runtime_min;
  const health = s.health_pct;
  const sCls = statusClass(s.status_code);

  const runtimeText = (runtime === null || runtime === undefined) ? '—' : runtime;
  const healthText = (health === null || health === undefined) ? '—' : health;

  document.getElementById('content').innerHTML = `
    <div class="grid two">
      <div class="panel hero">
        <h2>Core Status <span class="tag">PWR-01</span></h2>
        <div class="readout ${sCls}">
          <span class="indicator"></span>${(s.status_text || 'UNKNOWN').toUpperCase()}
        </div>
      </div>
      <div class="panel">
        <h2>Runtime <span class="tag">T-MINUS</span></h2>
        <div class="readout">${runtimeText}<span class="unit">MIN</span></div>
      </div>
    </div>

    <div class="grid mt">
      <div class="panel">
        <h2>Charge Level <span class="tag">CAP-%</span></h2>
        <div class="readout">${charge}<span class="unit">%</span></div>
        <div class="meter">
          <div class="fill ${chargeFillClass(charge)}" style="width:${charge}%"></div>
          <div class="ticks"></div>
        </div>
      </div>
      <div class="panel">
        <h2>Battery Health <span class="tag">WEAR</span></h2>
        <div class="readout">${healthText}<span class="unit">%</span></div>
        <div class="meter">
          <div class="fill ${healthFillClass(health)}" style="width:${health || 0}%"></div>
          <div class="ticks"></div>
        </div>
      </div>
      <div class="panel">
        <h2>Capacity Matrix <span class="tag">mWh</span></h2>
        <div class="kv"><span class="k">Full</span><span class="v">${s.full_capacity_mwh ?? '—'}</span></div>
        <div class="kv"><span class="k">Design</span><span class="v">${s.design_capacity_mwh ?? '—'}</span></div>
        <div class="kv"><span class="k">Status code</span><span class="v">${s.status_code ?? '—'}</span></div>
        <div class="kv"><span class="k">Device</span><span class="v" style="font-size:10px">${(s.name || '—').slice(0, 24)}</span></div>
      </div>
    </div>
  `;
}

tick();
setInterval(tick, 5000);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/state":
            with state_lock:
                payload = {k: v for k, v in state.items() if k != "history"}
                payload["history"] = list(state["history"])
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):  # silence default access log
        return


def main() -> None:
    poll_thread = threading.Thread(target=poll_loop, daemon=True)
    poll_thread.start()

    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"UPS dashboard → http://localhost:{PORT}")
    print(f"Logs → {LOG_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
