#!/bin/bash
# Copyright 2026 Behike. All rights reserved.
# Auto Post Script. Reads today's calendar, prepares post files,
# and notifies via Telegram when it is time to post.
#
# Usage:
#   ./auto_post.sh              # check and prepare today's posts
#   ./auto_post.sh --check      # just show what is due
#   ./auto_post.sh --force      # prepare all today's posts regardless of time
#
# Cron setup (run every hour):
#   0 * * * * cd ~/behique && bash tools/auto_post.sh >> Ceiba/news/auto-post.log 2>&1
#
# Requires: python3, jq (optional for JSON parsing)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
NEWS_DIR="$PROJECT_DIR/Ceiba/news"
READY_DIR="$NEWS_DIR/ready-to-post"
TODAY=$(date +%Y-%m-%d)
CURRENT_HOUR=$(date +%H)
MODE="${1:-run}"

echo ""
echo "============================================================"
echo "  BEHIKE AUTO-POST -- $TODAY $(date +%H:%M:%S)"
echo "============================================================"
echo ""

# Find the calendar that covers today
CALENDAR_FILE=""
for f in "$NEWS_DIR"/calendar-*.json; do
    if [ -f "$f" ]; then
        CALENDAR_FILE="$f"
    fi
done

if [ -z "$CALENDAR_FILE" ] || [ ! -f "$CALENDAR_FILE" ]; then
    echo "[!] No calendar found. Generate one first:"
    echo "    python3 $SCRIPT_DIR/content_calendar.py --generate"
    exit 1
fi

echo "  Calendar: $CALENDAR_FILE"
echo ""

# Parse today's slots using Python (more reliable than jq for complex JSON)
python3 -c "
import json, sys
from datetime import datetime

with open('$CALENDAR_FILE') as f:
    cal = json.load(f)

today = '$TODAY'
current_hour = int('$CURRENT_HOUR')
mode = '$MODE'

for day in cal.get('days', []):
    if day.get('date') != today:
        continue

    slots = day.get('slots', [])
    if not slots:
        print('  No posts scheduled for today.')
        sys.exit(0)

    for slot in slots:
        hour = slot.get('hour', 0)
        account = slot.get('account', 'unknown')
        content_type = slot.get('content_type', 'unknown')
        content_id = slot.get('content_id', '')
        source_file = slot.get('file', '')
        caption = slot.get('caption_preview', '')
        status = slot.get('status', 'scheduled')

        # Determine if this slot is due
        is_due = (hour == current_hour) or mode == '--force'
        is_past = hour < current_hour
        is_future = hour > current_hour

        if mode == '--check':
            period = 'AM' if hour < 12 else 'PM'
            dh = hour if hour <= 12 else hour - 12
            if dh == 0: dh = 12
            state = 'DUE NOW' if hour == current_hour else ('PAST' if is_past else 'UPCOMING')
            print(f'  {dh:2d}:00 {period}  [{state}]  @{account}  {content_type}  {caption[:30]}')
            continue

        if not is_due:
            continue

        if status == 'needs_content':
            print(f'  [!] {hour}:00 @{account}: NEEDS CONTENT (skipping)')
            continue

        # Prepare the post
        print(f'  [>>] Preparing: {hour}:00 @{account} ({content_type})')

        # Create ready-to-post directory
        import os
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        post_dir = f'$READY_DIR/{account}/{timestamp}'
        os.makedirs(post_dir, exist_ok=True)

        # Copy source file if it exists
        if source_file and os.path.exists(source_file):
            import shutil
            ext = os.path.splitext(source_file)[1]
            shutil.copy2(source_file, f'{post_dir}/content{ext}')
            print(f'       Copied: {os.path.basename(source_file)}')

        # Write caption
        caption_text = caption or f'[{content_type}] {content_id}'
        with open(f'{post_dir}/caption.txt', 'w') as cf:
            cf.write(caption_text)

        # Write metadata
        meta = {
            'account': account,
            'content_type': content_type,
            'content_id': content_id,
            'scheduled_hour': hour,
            'prepared_at': datetime.now().isoformat(),
        }
        with open(f'{post_dir}/metadata.json', 'w') as mf:
            json.dump(meta, mf, indent=2)

        print(f'       Ready at: {post_dir}/')

    break
else:
    print(f'  No entry found for today ({today}) in calendar.')
"

# Notify via Telegram if notify.py exists and posts were prepared
if [ "$MODE" != "--check" ]; then
    NOTIFY_SCRIPT="$SCRIPT_DIR/notify.py"
    if [ -f "$NOTIFY_SCRIPT" ]; then
        # Check if any posts were just prepared
        if [ -d "$READY_DIR" ]; then
            RECENT=$(find "$READY_DIR" -name "metadata.json" -newer "$CALENDAR_FILE" 2>/dev/null | head -5)
            if [ -n "$RECENT" ]; then
                echo ""
                echo "  Sending Telegram notification..."
                python3 "$NOTIFY_SCRIPT" "Time to post! Files ready in $READY_DIR" 2>/dev/null || true
            fi
        fi
    fi
fi

echo ""
echo "============================================================"
echo "  Done. $(date +%H:%M:%S)"
echo "============================================================"
echo ""
