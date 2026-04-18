#!/usr/bin/env bash
# Start every Behike service on Hutia. Safe to run multiple times — kills stale
# processes on the same ports first. Outputs PIDs and log paths.

set -u

log() { printf "[%s] %s\n" "$(date +%H:%M:%S)" "$*"; }

kill_port() {
  local port="$1"
  local pids
  # Windows (Git Bash) and Linux both support this via netstat/ss
  if command -v netstat >/dev/null 2>&1; then
    pids=$(netstat -ano 2>/dev/null | awk -v p=":$port" '$2 ~ p && $4 == "LISTENING" {print $5}' | sort -u)
    for pid in $pids; do
      log "Killing PID $pid on port $port"
      taskkill //PID "$pid" //F >/dev/null 2>&1 || kill -9 "$pid" 2>/dev/null || true
    done
  fi
}

start_bg() {
  local name="$1" logf="$2"; shift 2
  log "Starting $name -> $logf"
  nohup "$@" > "$logf" 2>&1 &
  log "  PID $!"
}

# Clean any zombies on the ports we care about
for p in 8080 8081 8090; do kill_port "$p"; done
# Kill any stale cloudflared
pkill -f cloudflared 2>/dev/null || true
pkill -f gdrive-watcher 2>/dev/null || true

# 1. Behike main web server
cd ~/behique/themes/behike-store/landing-pages || { log "MISSING: landing-pages"; exit 1; }
start_bg "behike-web (8080)" /tmp/behike-store-server.log python -m http.server 8080

# 2. Stripe checkout
cd ~/behique/tools/stripe-checkout || { log "MISSING: stripe-checkout"; exit 1; }
if [ -f .env ]; then
  set -a; # shellcheck disable=SC1091
  source .env; set +a
  start_bg "stripe-checkout (8081)" /tmp/stripe-checkout.log python server.py
else
  log "SKIP stripe-checkout: no .env file"
fi

# 3. Innova Barber
cd ~/behique/projects/innova-barber || { log "MISSING: innova-barber"; exit 1; }
start_bg "innova-barber (8090)" /tmp/innova-barber-server.log python redirect-server.py

# 4. Cloudflare Tunnel
CF="/c/Program Files (x86)/cloudflared/cloudflared.exe"
if [ -x "$CF" ]; then
  start_bg "cloudflared tunnel" /tmp/behike-tunnel.log "$CF" tunnel run behike
else
  log "MISSING: $CF (install cloudflared or update path)"
fi

# 5. Google Drive auto-deploy watcher
if [ -f ~/behique/tools/gdrive-watcher.py ]; then
  start_bg "gdrive-watcher" /tmp/gdrive-watcher.log python ~/behique/tools/gdrive-watcher.py
fi

sleep 3
log ""
log "=== Local health check ==="
for url in "http://127.0.0.1:8080/:behike" "http://127.0.0.1:8081/health:stripe" "http://127.0.0.1:8090/:innova"; do
  target="${url%%:*}:${url#*:}"
  u="${url%:*}"
  name="${url##*:}"
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$u" || echo "000")
  log "  $name -> $u  [$code]"
done

log ""
log "Tail logs:"
log "  tail -f /tmp/behike-store-server.log"
log "  tail -f /tmp/stripe-checkout.log"
log "  tail -f /tmp/innova-barber-server.log"
log "  tail -f /tmp/behike-tunnel.log"
