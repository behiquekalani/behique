#!/bin/bash
# Copyright 2026 Behike. All rights reserved.
# Auto News Pipeline -- Cron wrapper for daily AI news content generation.
#
# Runs the full pipeline at 6am daily.
#
# CRON SETUP (run: crontab -e):
#   0 6 * * * /Users/kalani/behique/tools/auto_news_pipeline.sh
#
# Or run manually:
#   ./auto_news_pipeline.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../Ceiba/news/logs"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/pipeline-$TODAY.log"

# Create log directory
mkdir -p "$LOG_DIR"

echo "========================================" >> "$LOG_FILE"
echo "Behike AI News Pipeline -- $TODAY $(date +%H:%M:%S)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Run the pipeline
cd "$SCRIPT_DIR"
python3 ai_news_pipeline.py --daily 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "" >> "$LOG_FILE"
    echo "Pipeline completed successfully at $(date +%H:%M:%S)" >> "$LOG_FILE"
else
    echo "" >> "$LOG_FILE"
    echo "Pipeline FAILED with exit code $EXIT_CODE at $(date +%H:%M:%S)" >> "$LOG_FILE"
fi

# Clean up logs older than 30 days
find "$LOG_DIR" -name "pipeline-*.log" -mtime +30 -delete 2>/dev/null || true

exit $EXIT_CODE
