#!/usr/bin/env bash
#
# Start Gumroad webhook server in the background.
# Logs to bios/logs/webhook_server.log
#
# Usage: ./start_webhook.sh
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="$PROJECT_DIR/bios/logs/webhook_server.log"
PID_FILE="$SCRIPT_DIR/.webhook_server.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Webhook server already running (PID $OLD_PID)"
        echo "Kill it first: kill $OLD_PID"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

echo "Starting Gumroad webhook server on port 8097..."
cd "$SCRIPT_DIR"
nohup /usr/bin/python3 webhook_server.py >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

echo "Server started (PID $SERVER_PID)"
echo "Logs: $LOG_FILE"
echo "Health: http://localhost:8097/webhook/status"
echo "Stop:  kill $SERVER_PID"
