#!/usr/bin/env python3
"""
System Stats Collector for Behike OS System Monitor
Collects CPU, RAM, GPU, disk, network, temp, processes, uptime
Serves stats via HTTP on localhost:8083/stats
Copyright 2026 Behike
"""

import json
import os
import subprocess
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import timedelta

import psutil

STATS_FILE = os.path.join(os.path.dirname(__file__), '..', 'Ceiba', 'system-stats.json')
PORT = 8083
UPDATE_INTERVAL = 2

current_stats = {}
cpu_history = []
net_prev = None
net_prev_time = None


def get_cpu_temp():
    """Try to get CPU temperature on macOS."""
    try:
        # Try powermetrics (requires sudo, may not work)
        # Fall back to osx-cpu-temp if installed
        result = subprocess.run(
            ['osx-cpu-temp'], capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            temp_str = result.stdout.strip().replace('°C', '').strip()
            return float(temp_str)
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass

    # Try psutil sensors (works on some systems)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    return entries[0].current
    except (AttributeError, Exception):
        pass

    # Try Apple Silicon thermal via IOKit (powermetrics snippet)
    try:
        result = subprocess.run(
            ['sudo', '-n', 'powermetrics', '--samplers', 'smc', '-i1', '-n1'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'CPU die temperature' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        temp_val = parts[1].strip().replace('C', '').strip()
                        return float(temp_val)
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass

    return None


def get_gpu_info():
    """Get GPU info on macOS using system_profiler."""
    try:
        result = subprocess.run(
            ['system_profiler', 'SPDisplaysDataType', '-json'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            displays = data.get('SPDisplaysDataType', [])
            if displays:
                gpu = displays[0]
                name = gpu.get('sppci_model', 'Unknown GPU')
                cores = gpu.get('sppci_cores', 'N/A')
                metal = gpu.get('sppci_metal', 'N/A')
                vram = gpu.get('spdisplays_vram', gpu.get('spdisplays_vram_shared', 'Unified'))
                return {
                    'name': name,
                    'cores': cores,
                    'metal': metal,
                    'vram': vram
                }
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {'name': 'N/A', 'cores': 'N/A', 'metal': 'N/A', 'vram': 'N/A'}


def get_top_processes(n=5):
    """Get top N processes by CPU usage."""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            if info['cpu_percent'] is not None and info['name'] not in ('kernel_task', 'idle'):
                procs.append({
                    'pid': info['pid'],
                    'name': info['name'][:25],
                    'cpu': round(info['cpu_percent'], 1),
                    'mem': round(info['memory_percent'], 1) if info['memory_percent'] else 0
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x['cpu'], reverse=True)
    return procs[:n]


def get_network_speed():
    """Calculate network speed since last call."""
    global net_prev, net_prev_time
    counters = psutil.net_io_counters()
    now = time.time()

    if net_prev is None:
        net_prev = counters
        net_prev_time = now
        return {'sent_speed': 0, 'recv_speed': 0, 'total_sent': counters.bytes_sent, 'total_recv': counters.bytes_recv}

    elapsed = now - net_prev_time
    if elapsed == 0:
        elapsed = 1

    sent_speed = (counters.bytes_sent - net_prev.bytes_sent) / elapsed
    recv_speed = (counters.bytes_recv - net_prev.bytes_recv) / elapsed

    net_prev = counters
    net_prev_time = now

    return {
        'sent_speed': round(sent_speed),
        'recv_speed': round(recv_speed),
        'total_sent': counters.bytes_sent,
        'total_recv': counters.bytes_recv
    }


def format_uptime():
    """Get system uptime."""
    boot = psutil.boot_time()
    uptime_seconds = time.time() - boot
    td = timedelta(seconds=int(uptime_seconds))
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return ' '.join(parts)


def collect_stats():
    """Collect all system stats."""
    global cpu_history

    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_history.append(cpu_percent)
    if len(cpu_history) > 60:
        cpu_history = cpu_history[-60:]

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()

    stats = {
        'timestamp': time.time(),
        'cpu': {
            'percent': cpu_percent,
            'cores': cpu_count,
            'freq_current': round(cpu_freq.current, 0) if cpu_freq else 0,
            'freq_max': round(cpu_freq.max, 0) if cpu_freq and cpu_freq.max else 0,
            'history': cpu_history
        },
        'ram': {
            'used': mem.used,
            'total': mem.total,
            'percent': mem.percent,
            'available': mem.available
        },
        'disk': {
            'used': disk.used,
            'total': disk.total,
            'free': disk.free,
            'percent': disk.percent
        },
        'gpu': get_gpu_info(),
        'network': get_network_speed(),
        'processes': get_top_processes(5),
        'uptime': format_uptime(),
        'cpu_temp': get_cpu_temp()
    }
    return stats


class StatsHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves stats as JSON."""

    def do_GET(self):
        if self.path == '/stats' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json.dumps(current_stats, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def stats_loop():
    """Background loop that collects stats every UPDATE_INTERVAL seconds."""
    global current_stats
    # Initial CPU percent call (first call always returns 0)
    psutil.cpu_percent(interval=None)
    time.sleep(0.5)

    while True:
        try:
            current_stats = collect_stats()
            # Also write to file
            stats_path = os.path.abspath(STATS_FILE)
            os.makedirs(os.path.dirname(stats_path), exist_ok=True)
            with open(stats_path, 'w') as f:
                json.dump(current_stats, f, indent=2)
        except Exception as e:
            print(f"Error collecting stats: {e}")
        time.sleep(UPDATE_INTERVAL)


def main():
    print(f"Behike System Monitor - Starting stats collector")
    print(f"HTTP server: http://localhost:{PORT}/stats")
    print(f"Update interval: {UPDATE_INTERVAL}s")
    print(f"Stats file: {os.path.abspath(STATS_FILE)}")

    # Start stats collection in background thread
    collector = threading.Thread(target=stats_loop, daemon=True)
    collector.start()

    # Give collector time for first reading
    time.sleep(1)

    # Start HTTP server
    server = HTTPServer(('127.0.0.1', PORT), StatsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == '__main__':
    main()
