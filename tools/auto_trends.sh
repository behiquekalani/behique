#!/bin/bash
# auto_trends.sh -- Cron wrapper for trends_scraper_v2.py
# Copyright 2026 Behike. All rights reserved.
#
# Runs every 6 hours via cron. Generates JSON + digest.
#
# CRON SETUP (run: crontab -e, then add this line):
#   0 */6 * * * /Users/kalani/behique/tools/auto_trends.sh >> /tmp/auto_trends.log 2>&1
#
# Or manually:
#   bash tools/auto_trends.sh
#   bash tools/auto_trends.sh Technology Health   # specific categories

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRAPER="$SCRIPT_DIR/trends_scraper_v2.py"
LOG_DIR="$SCRIPT_DIR/../Ceiba/news"
TIMESTAMP=$(date "+%Y-%m-%d_%H%M")

echo "=== Auto Trends Run: $TIMESTAMP ==="

# Check python3 is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Check pytrends is installed
python3 -c "import pytrends" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: pytrends not installed. Run: pip install pytrends"
    exit 1
fi

# Build category args
CATEGORIES=""
if [ $# -gt 0 ]; then
    CATEGORIES="--category $@"
fi

# Run the scraper with digest + suggestions
python3 "$SCRAPER" \
    $CATEGORIES \
    --digest \
    --suggest \
    --geo US \
    --timeframe "today 1-m"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Scan completed successfully at $(date "+%H:%M:%S") ==="

    # Archive a timestamped copy
    ARCHIVE_DIR="$LOG_DIR/archive"
    mkdir -p "$ARCHIVE_DIR"
    if [ -f "$LOG_DIR/trends.json" ]; then
        cp "$LOG_DIR/trends.json" "$ARCHIVE_DIR/trends_${TIMESTAMP}.json"
    fi
else
    echo "=== Scan FAILED with exit code $EXIT_CODE ==="
fi

exit $EXIT_CODE
