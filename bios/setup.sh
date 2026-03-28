#!/bin/bash
# BIOS Setup - Run once to configure automated intelligence pipeline
# Sets up cron jobs and starts the dashboard server

BIOS_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$BIOS_DIR")"

echo ""
echo "  BIOS SETUP"
echo "  =========================================="

# 1. Create log directory
mkdir -p "$BIOS_DIR/logs" "$BIOS_DIR/reports" "$BIOS_DIR/storage"
echo "  [1/4] Directories created"

# 2. Set up cron jobs
CRON_PIPELINE="0 */6 * * * cd $BASE_DIR && /usr/bin/python3 bios/run_all.py --pipeline >> bios/logs/cron.log 2>&1"
CRON_DAILY="0 6 * * * cd $BASE_DIR && /usr/bin/python3 bios/scheduler/daily_report.py >> bios/logs/daily.log 2>&1"

# Check if cron jobs already exist
EXISTING=$(crontab -l 2>/dev/null || echo "")

if echo "$EXISTING" | grep -q "bios/run_all.py"; then
    echo "  [2/4] Cron jobs already configured"
else
    echo "$EXISTING" > /tmp/bios_cron
    echo "" >> /tmp/bios_cron
    echo "# BIOS Intelligence Pipeline - every 6 hours" >> /tmp/bios_cron
    echo "$CRON_PIPELINE" >> /tmp/bios_cron
    echo "" >> /tmp/bios_cron
    echo "# BIOS Daily Report - 6 AM AST" >> /tmp/bios_cron
    echo "$CRON_DAILY" >> /tmp/bios_cron
    crontab /tmp/bios_cron
    rm /tmp/bios_cron
    echo "  [2/4] Cron jobs installed:"
    echo "         Pipeline: every 6 hours"
    echo "         Daily report: 6 AM"
fi

# 3. Symlink data files for dashboard
mkdir -p "$BIOS_DIR/dashboard/data"
ln -sf "$BIOS_DIR/storage/signals.json" "$BIOS_DIR/dashboard/data/signals.json" 2>/dev/null
ln -sf "$BIOS_DIR/storage/insights.json" "$BIOS_DIR/dashboard/data/insights.json" 2>/dev/null
ln -sf "$BIOS_DIR/config.json" "$BIOS_DIR/dashboard/data/config.json" 2>/dev/null
ln -sf "$BIOS_DIR/storage/polymarket.json" "$BIOS_DIR/dashboard/data/polymarket.json" 2>/dev/null
echo "  [3/4] Dashboard data linked"

# 4. Run initial pipeline
echo "  [4/4] Running initial pipeline..."
cd "$BASE_DIR"
python3 bios/run_all.py --pipeline

echo ""
echo "  SETUP COMPLETE"
echo "  =========================================="
echo "  Dashboard: python3 bios/run_all.py --serve"
echo "  Or daemon: python3 bios/run_all.py --daemon"
echo "  Cron: pipeline every 6h, daily report at 6 AM"
echo ""
