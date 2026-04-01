#!/bin/bash
# Spawn Claude — Launch a new Claude Code session with a specific task.
#
# This opens a new Terminal tab and runs Claude with a prompt.
# The spawned session reads AUTO_HANDOFF.md automatically (via CLAUDE.md).
#
# Usage:
#   bash tools/spawn-claude.sh "build hogar saas phase 2"
#   bash tools/spawn-claude.sh "list 10 products on gumroad"
#   bash tools/spawn-claude.sh build    # autonomous build mode
#
# From Claude Code, the parent session can call this to spawn workers:
#   subprocess.run(["bash", "tools/spawn-claude.sh", "task description"])

TASK="${1:-Read Ceiba/inbox/AUTO_HANDOFF.md and continue building.}"
BEHIQUE="$HOME/behique"

# Detect terminal app
if [ -d "/Applications/iTerm.app" ]; then
    # iTerm2
    osascript -e "
    tell application \"iTerm\"
        activate
        tell current window
            create tab with default profile
            tell current session
                write text \"cd $BEHIQUE && claude --print '$TASK'\"
            end tell
        end tell
    end tell
    "
elif [ -d "/Applications/Terminal.app" ]; then
    # macOS Terminal
    osascript -e "
    tell application \"Terminal\"
        activate
        do script \"cd $BEHIQUE && claude '$TASK'\"
    end tell
    "
else
    echo "No supported terminal found. Run manually:"
    echo "  cd $BEHIQUE && claude '$TASK'"
fi

echo "Spawned Claude session: $TASK"
