#!/bin/bash
# Copyright 2026 Behike. All rights reserved.
# Behike Overnight Autonomous Pipeline
# Runs all content generation, scraping, and maintenance tasks while Kalani sleeps.
#
# CRON SETUP (run: crontab -e):
#   0 0 * * * /Users/kalani/behique/tools/overnight.sh
#
# Or run manually:
#   ./overnight.sh
#
# Logs: ~/behique/Ceiba/news/logs/overnight-YYYY-MM-DD.log
# Summary: ~/behique/Ceiba/news/daily/YYYY-MM-DD/overnight-summary.md
# Morning report: python3 ~/behique/tools/morning_content_report.py

set -uo pipefail

# --- Paths ---
BEHIQUE_DIR="$HOME/behique"
TOOLS_DIR="$BEHIQUE_DIR/tools"
NEWS_DIR="$BEHIQUE_DIR/Ceiba/news"
LOG_DIR="$NEWS_DIR/logs"
DATE=$(date +%Y-%m-%d)
TIME_START=$(date +%H:%M:%S)
LOG="$LOG_DIR/overnight-$DATE.log"
DAILY_DIR="$NEWS_DIR/daily/$DATE"
SUMMARY="$DAILY_DIR/overnight-summary.md"
NOTIFY="$TOOLS_DIR/notify.py"

# If notify.py is archived, use that path
if [ ! -f "$NOTIFY" ]; then
    NOTIFY="$TOOLS_DIR/_archived/notify.py"
fi

# --- Setup ---
mkdir -p "$LOG_DIR" "$DAILY_DIR"

# --- Helpers ---
log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"
}

run_task() {
    local name="$1"
    shift
    log "START: $name"
    if "$@" >> "$LOG" 2>&1; then
        log "OK:    $name"
        return 0
    else
        log "FAIL:  $name (exit $?)"
        return 1
    fi
}

# --- Counters ---
TASKS_RUN=0
TASKS_OK=0
TASKS_FAIL=0
CAROUSELS=0
CAPTIONS_EN=0
CAPTIONS_ES=0
REELS=0
MEMES=0
STORIES=0
NICHES=0
TRENDS=0

echo "==========================================================" >> "$LOG"
echo "  BEHIKE OVERNIGHT RUN: $DATE $TIME_START" >> "$LOG"
echo "==========================================================" >> "$LOG"
echo "" >> "$LOG"

# ==============================================================
# PHASE 1: CONTENT FETCHING (parallel)
# ==============================================================
log "--- PHASE 1: CONTENT FETCHING (parallel) ---"

# Launch all fetchers in background
PIDS=()

# 1a. Fetch AI news (RSS feeds)
(
    cd "$TOOLS_DIR"
    python3 ai_news_tracker.py --fetch
) >> "$LOG" 2>&1 &
PIDS+=($!)

# 1b. Scrape Reddit stories
(
    cd "$TOOLS_DIR"
    python3 reddit_story_scraper.py --count 3
) >> "$LOG" 2>&1 &
PIDS+=($!)

# 1c. Scrape Reddit memes
(
    cd "$TOOLS_DIR"
    python3 reddit_meme_scraper.py --count 5 --min-score 1000
) >> "$LOG" 2>&1 &
PIDS+=($!)

# 1d. Scan Reddit for niche gaps
(
    cd "$TOOLS_DIR"
    python3 reddit_niche_crawler.py
    python3 reddit_niche_crawler.py --digest
) >> "$LOG" 2>&1 &
PIDS+=($!)

# 1e. Fetch Google Trends (if v2 scraper exists)
if [ -f "$TOOLS_DIR/trends_scraper.py" ]; then
    (
        cd "$TOOLS_DIR"
        python3 trends_scraper.py --quick
    ) >> "$LOG" 2>&1 &
    PIDS+=($!)
fi

# Wait for all Phase 1 tasks
log "Waiting for ${#PIDS[@]} parallel fetchers..."
FETCH_FAILS=0
for pid in "${PIDS[@]}"; do
    if wait "$pid"; then
        TASKS_OK=$((TASKS_OK + 1))
    else
        TASKS_FAIL=$((TASKS_FAIL + 1))
        FETCH_FAILS=$((FETCH_FAILS + 1))
    fi
    TASKS_RUN=$((TASKS_RUN + 1))
done
log "Phase 1 complete. ${FETCH_FAILS} failures out of ${#PIDS[@]} tasks."
echo "" >> "$LOG"

# ==============================================================
# PHASE 2: CONTENT GENERATION (sequential, depends on Phase 1)
# ==============================================================
log "--- PHASE 2: CONTENT GENERATION (sequential) ---"

# 2a. Run AI news pipeline (carousels + captions + reels)
TASKS_RUN=$((TASKS_RUN + 1))
if run_task "AI news pipeline" python3 "$TOOLS_DIR/ai_news_pipeline.py" --daily --stories 5 --reels 2; then
    TASKS_OK=$((TASKS_OK + 1))
else
    TASKS_FAIL=$((TASKS_FAIL + 1))
fi

# Count generated files
if [ -d "$DAILY_DIR" ]; then
    CAROUSELS=$(find "$DAILY_DIR" -name "carousel-*.html" 2>/dev/null | wc -l | tr -d ' ')
    CAPTIONS_EN=$(find "$DAILY_DIR" -name "caption-*-en.txt" 2>/dev/null | wc -l | tr -d ' ')
    CAPTIONS_ES=$(find "$DAILY_DIR" -name "caption-*-es.txt" 2>/dev/null | wc -l | tr -d ' ')
    REELS=$(find "$DAILY_DIR" -name "reel-*.json" 2>/dev/null | wc -l | tr -d ' ')
fi

# Count scraped content
MEMES=$(find "$NEWS_DIR/memes" -name "*.json" -newer "$LOG_DIR/overnight-$DATE.log" 2>/dev/null | wc -l | tr -d ' ')
STORIES_DIR="$TOOLS_DIR/reel-pipeline/stories"
if [ -d "$STORIES_DIR" ]; then
    STORIES=$(find "$STORIES_DIR" -name "*.json" -newer "$LOG_DIR/overnight-$DATE.log" 2>/dev/null | wc -l | tr -d ' ')
fi

echo "" >> "$LOG"

# ==============================================================
# PHASE 3: MAINTENANCE
# ==============================================================
log "--- PHASE 3: MAINTENANCE ---"

# 3a. Clean logs older than 30 days
OLD_LOGS=$(find "$LOG_DIR" -name "*.log" -mtime +30 2>/dev/null | wc -l | tr -d ' ')
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
log "Cleaned $OLD_LOGS old log files"

# 3b. Deduplicate articles database
TASKS_RUN=$((TASKS_RUN + 1))
ARTICLES_FILE="$NEWS_DIR/articles.json"
if [ -f "$ARTICLES_FILE" ]; then
    BEFORE=$(python3 -c "import json; print(len(json.load(open('$ARTICLES_FILE'))))" 2>/dev/null || echo "0")
    # Remove articles older than 14 days to keep the DB lean
    python3 -c "
import json
from datetime import datetime, timedelta

f = '$ARTICLES_FILE'
arts = json.load(open(f))
cutoff = (datetime.now() - timedelta(days=14)).isoformat()
fresh = [a for a in arts if a.get('fetched', '') >= cutoff[:10]]
dupes = len(arts) - len(fresh)
json.dump(fresh, open(f, 'w'), indent=2, default=str)
print(f'Articles: {len(arts)} -> {len(fresh)} (removed {dupes} old entries)')
" >> "$LOG" 2>&1
    TASKS_OK=$((TASKS_OK + 1))
    log "Article DB cleaned"
else
    log "No articles.json found, skipping cleanup"
    TASKS_OK=$((TASKS_OK + 1))
fi

# 3c. Clean empty daily directories older than 7 days
find "$NEWS_DIR/daily" -maxdepth 1 -type d -empty -mtime +7 -delete 2>/dev/null || true

echo "" >> "$LOG"

# ==============================================================
# PHASE 4: SUMMARY
# ==============================================================
log "--- PHASE 4: SUMMARY ---"

TIME_END=$(date +%H:%M:%S)

cat > "$SUMMARY" << SUMMARY_EOF
# Overnight Pipeline Report, $DATE

Started: $TIME_START
Finished: $TIME_END

## Task Results

| Metric | Count |
|--------|-------|
| Tasks run | $TASKS_RUN |
| Succeeded | $TASKS_OK |
| Failed | $TASKS_FAIL |

## Content Generated

| Type | Count |
|------|-------|
| Carousels (HTML) | $CAROUSELS |
| Captions (EN) | $CAPTIONS_EN |
| Captions (ES) | $CAPTIONS_ES |
| Reel scripts | $REELS |
| Reddit stories | $STORIES |
| Memes scraped | $MEMES |

## Files

Location: \`$DAILY_DIR/\`

$(ls -1 "$DAILY_DIR" 2>/dev/null | while read f; do echo "- $f"; done)

## Next Steps

1. Run \`python3 ~/behique/tools/morning_content_report.py\` for a formatted briefing
2. Open carousel HTML files in browser, screenshot each slide
3. Review and edit captions
4. Post to Instagram @behikeai
5. Run reel scripts through make_reel.py if reels were generated

## Log

Full log: \`$LOG\`
SUMMARY_EOF

log "Summary written to $SUMMARY"

# --- Telegram notification ---
if [ -f "$NOTIFY" ]; then
    NOTIFY_MSG="*Behike Overnight Complete*
$DATE | $TIME_START - $TIME_END

Content ready:
- $CAROUSELS carousels
- $CAPTIONS_EN captions (EN)
- $CAPTIONS_ES captions (ES)
- $REELS reel scripts
- $STORIES reddit stories
- $MEMES memes

Tasks: $TASKS_OK ok / $TASKS_FAIL fail

Run: python3 ~/behique/tools/morning_content_report.py"

    python3 "$NOTIFY" --queue "$NOTIFY_MSG" "overnight" >> "$LOG" 2>&1 || true
    log "Telegram notification queued"
fi

echo "" >> "$LOG"
log "==========================================================="
log "  OVERNIGHT PIPELINE COMPLETE"
log "  Tasks: $TASKS_RUN run, $TASKS_OK ok, $TASKS_FAIL failed"
log "  Content: $CAROUSELS carousels, $CAPTIONS_EN captions, $REELS reels"
log "==========================================================="

# Exit with failure if any critical task failed
if [ "$TASKS_FAIL" -gt 0 ]; then
    exit 1
fi
exit 0

# ==============================================================
# CRON INSTALLATION
# ==============================================================
# To install, run:
#
#   crontab -e
#
# Then add this line to run at midnight every day:
#
#   0 0 * * * /Users/kalani/behique/tools/overnight.sh
#
# Optional: also run the news fetcher every 4 hours for fresher data:
#
#   0 */4 * * * /Users/kalani/behique/tools/auto_news_digest.sh fetch
#
# To verify cron is set up:
#
#   crontab -l
#
# To check if overnight ran:
#
#   cat ~/behique/Ceiba/news/logs/overnight-$(date +%Y-%m-%d).log
#
# To read the morning report:
#
#   python3 ~/behique/tools/morning_content_report.py
# ==============================================================
