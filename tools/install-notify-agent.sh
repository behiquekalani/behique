#!/bin/bash
# install-notify-agent.sh
# Installs the Ceiba Telegram notify watcher as a Mac LaunchAgent.
# Run once: bash ~/behique/tools/install-notify-agent.sh

set -e

PLIST_NAME="com.behique.notify"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/$PLIST_NAME.plist"
PYTHON=$(which python3)
SCRIPT="$HOME/behique/tools/notify.py"
LOG_OUT="$HOME/behique/output/notify-agent.log"
LOG_ERR="$HOME/behique/output/notify-agent-err.log"

mkdir -p "$PLIST_DIR"
mkdir -p "$HOME/behique/output"
mkdir -p "$HOME/behique/pending-notifications"

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$SCRIPT</string>
        <string>--watch</string>
    </array>

    <!-- Run every 60 seconds -->
    <key>StartInterval</key>
    <integer>60</integer>

    <!-- Start on login -->
    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$LOG_OUT</string>

    <key>StandardErrorPath</key>
    <string>$LOG_ERR</string>

    <!-- Restart if it crashes -->
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

# Load it now (no reboot needed)
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "✓ Ceiba notify agent installed and running"
echo "  Watches: ~/behique/pending-notifications/*.json"
echo "  Fires:   every 60 seconds"
echo "  Logs:    ~/behique/output/notify-agent.log"
echo ""
echo "Test it now:"
echo "  python3 ~/behique/tools/notify.py --queue 'Ceiba notify relay is working 🌱'"
echo "  (wait up to 60 seconds for the message on Telegram)"
