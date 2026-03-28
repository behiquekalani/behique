#!/bin/bash
# Copyright (c) 2026 Kalani Andre Gomez Padin / Behique
# Cron wrapper for reddit_meme_scraper.py
# Usage: crontab -e, then add:
#   0 */6 * * * /Users/kalani/behique/tools/auto_meme_scrape.sh >> /tmp/meme_scrape.log 2>&1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/tmp/meme_scrape.log"

echo "================================================"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting meme scrape..."
echo "================================================"

python3 "$SCRIPT_DIR/reddit_meme_scraper.py" --count 5 --min-score 1000

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Scrape complete."
echo ""
