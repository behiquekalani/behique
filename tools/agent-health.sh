#!/bin/bash
# Agent Health Checker
# Monitors background agent output files for activity
# Usage: ./agent-health.sh [task_dir]
# If output file hasn't grown in 120 seconds, flags it as STUCK

TASK_DIR="${1:-/private/tmp/claude-501}"
STALE_THRESHOLD=120  # seconds without output = potentially stuck

echo "=== Agent Health Check ==="
echo "Threshold: ${STALE_THRESHOLD}s without output = STUCK"
echo ""

found=0
for f in $(find "$TASK_DIR" -name "*.output" -type f 2>/dev/null); do
    found=$((found + 1))
    task_id=$(basename "$f" .output)
    lines=$(wc -l < "$f" 2>/dev/null || echo 0)

    # Check last modified time
    if [[ "$(uname)" == "Darwin" ]]; then
        last_mod=$(stat -f %m "$f" 2>/dev/null || echo 0)
    else
        last_mod=$(stat -c %Y "$f" 2>/dev/null || echo 0)
    fi
    now=$(date +%s)
    age=$((now - last_mod))

    if [ "$age" -gt "$STALE_THRESHOLD" ]; then
        status="STUCK"
        color="\033[91m"
    elif [ "$age" -gt 60 ]; then
        status="SLOW"
        color="\033[93m"
    else
        status="ALIVE"
        color="\033[92m"
    fi

    echo -e "  ${color}[${status}]\033[0m ${task_id:0:12}... | ${lines} lines | last activity ${age}s ago"
done

if [ "$found" -eq 0 ]; then
    echo "  No active agents found."
fi
echo ""
echo "Done. Run again to recheck."
