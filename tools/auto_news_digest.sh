#!/bin/bash
# Auto News Digest -- Run via cron on Hutia or Ceiba
# Fetches AI news every hour, generates daily HTML digest at 6am
#
# Cron setup:
#   # Fetch every hour
#   0 * * * * /Users/kalani/behique/tools/auto_news_digest.sh fetch
#   # Generate digest at 6am
#   0 6 * * * /Users/kalani/behique/tools/auto_news_digest.sh digest
#
# Or run manually:
#   ./auto_news_digest.sh fetch
#   ./auto_news_digest.sh digest

BEHIQUE_DIR="$HOME/behique"
TRACKER="$BEHIQUE_DIR/tools/ai_news_tracker.py"
LOG_DIR="$BEHIQUE_DIR/Ceiba/news/logs"

mkdir -p "$LOG_DIR"

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

case "${1:-fetch}" in
    fetch)
        echo "[$DATE $TIME] Fetching news..." >> "$LOG_DIR/fetch.log"
        python3 "$TRACKER" --fetch >> "$LOG_DIR/fetch.log" 2>&1
        echo "[$DATE $TIME] Done" >> "$LOG_DIR/fetch.log"
        ;;
    digest)
        echo "[$DATE $TIME] Generating daily digest..." >> "$LOG_DIR/digest.log"
        python3 "$TRACKER" --digest --format html \
            --save "$BEHIQUE_DIR/Ceiba/news/digests/digest-$DATE.html" \
            >> "$LOG_DIR/digest.log" 2>&1
        # Also generate text version
        python3 "$TRACKER" --digest --format text \
            --save "$BEHIQUE_DIR/Ceiba/news/digests/digest-$DATE.md" \
            >> "$LOG_DIR/digest.log" 2>&1
        echo "[$DATE $TIME] Digest saved" >> "$LOG_DIR/digest.log"
        ;;
    *)
        echo "Usage: $0 {fetch|digest}"
        exit 1
        ;;
esac
