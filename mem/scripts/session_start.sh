#!/bin/bash
# Ceiba Session Start - run at beginning of each Claude Code session.
# Add to CLAUDE.md as first instruction.

cd ~/behique

# Register this session
python3 mem/scripts/session_manager.py register "${1:-general}" 2>/dev/null

# Show live status snapshot
python3 mem/scripts/live_status.py --once 2>/dev/null

# Start heartbeat in background (updates every 60s)
while true; do
    python3 mem/scripts/session_manager.py heartbeat 2>/dev/null
    sleep 60
done &
HEARTBEAT_PID=$!

echo "Heartbeat running (PID: $HEARTBEAT_PID)"
echo "To stop: kill $HEARTBEAT_PID"
