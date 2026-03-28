#!/bin/bash
# Overnight Machine -- First-run setup script
set -e

echo "Setting up Overnight Machine..."
python3 /Users/kalani/behique/tools/overnight_machine.py --setup

# Install cron job
CRON_JOB="0 23 * * * /usr/bin/python3 /Users/kalani/behique/tools/overnight_machine.py >> ~/.overnight/logs/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v overnight_machine; echo "$CRON_JOB") | crontab -

echo ""
echo "Cron job installed: runs at 11 PM every night"
echo ""
echo "Quick commands:"
echo "  Test the pipeline:    python3 /Users/kalani/behique/tools/overnight_machine.py --test"
echo "  Dry run:              python3 /Users/kalani/behique/tools/overnight_machine.py --dry-run"
echo "  Morning report:       cat ~/.overnight/morning_report.txt"
echo "  Review listings:      ls ~/.overnight/review/\$(date +%Y-%m-%d)/"
echo "  Landscape report:     python3 /Users/kalani/behique/tools/overnight_machine.py --report"
echo ""
echo "Machines in the fleet:"
echo "  Ceiba  -- M4 Mac, main (this machine)"
echo "  Cobo   -- GTX 1080 Ti"
echo "  Hutia  -- Always-on server at 192.168.0.152"
echo ""
echo "To run on Hutia nightly instead, SSH in and repeat this setup:"
echo "  ssh kalani@192.168.0.152"
echo "  python3 ~/behique/tools/overnight_setup.sh"
