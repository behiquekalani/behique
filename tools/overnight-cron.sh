#!/bin/bash
# Overnight Machine — cron setup script
# Adds overnight pipeline jobs to crontab
#
# Usage:
#   bash tools/overnight-cron.sh install   # Add cron jobs
#   bash tools/overnight-cron.sh remove    # Remove cron jobs
#   bash tools/overnight-cron.sh status    # Show current jobs

BEHIQUE="$HOME/behique"
PYTHON="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"
LOG_DIR="$BEHIQUE/bios/logs"

case "$1" in
  install)
    echo "Installing overnight cron jobs..."

    # Backup existing crontab
    crontab -l > /tmp/crontab-backup-$(date +%Y%m%d) 2>/dev/null

    # Add overnight jobs (don't duplicate)
    (crontab -l 2>/dev/null | grep -v "# OVERNIGHT-") | crontab -

    (crontab -l 2>/dev/null; cat << CRON
# OVERNIGHT-MACHINE: Trends scraping at 11PM
0 23 * * * $PYTHON $BEHIQUE/tools/overnight_machine.py >> $LOG_DIR/overnight.log 2>&1 # OVERNIGHT-MACHINE
# OVERNIGHT-MACHINE: Reel factory batch at midnight
0 0 * * * $PYTHON $BEHIQUE/tools/reel_factory.py batch --count 5 >> $LOG_DIR/reel_factory.log 2>&1 # OVERNIGHT-MACHINE
# OVERNIGHT-MACHINE: Public build posts at 7AM
0 7 * * * $PYTHON $BEHIQUE/tools/public_build.py >> $LOG_DIR/public_build.log 2>&1 # OVERNIGHT-MACHINE
# OVERNIGHT-MACHINE: Reddit niche scan at 2AM
0 2 * * * $PYTHON $BEHIQUE/tools/reddit_niche_crawler.py --digest >> $LOG_DIR/niche_crawler.log 2>&1 # OVERNIGHT-MACHINE
# OVERNIGHT-MACHINE: Session end checkpoint at 3AM
0 3 * * * cd $BEHIQUE && $PYTHON mem/scripts/session_end.py --checkpoint >> $LOG_DIR/session_checkpoint.log 2>&1 # OVERNIGHT-MACHINE
CRON
    ) | crontab -

    echo "Done. 5 overnight jobs installed."
    echo "  23:00 - Trends scraping"
    echo "  00:00 - Reel factory (5 reels)"
    echo "  02:00 - Reddit niche scan"
    echo "  03:00 - Session checkpoint"
    echo "  07:00 - Public build posts"
    ;;

  remove)
    echo "Removing overnight cron jobs..."
    crontab -l 2>/dev/null | grep -v "# OVERNIGHT-" | crontab -
    echo "Done."
    ;;

  status)
    echo "Overnight cron jobs:"
    crontab -l 2>/dev/null | grep "OVERNIGHT-" || echo "  None installed"
    ;;

  *)
    echo "Usage: bash tools/overnight-cron.sh [install|remove|status]"
    ;;
esac
