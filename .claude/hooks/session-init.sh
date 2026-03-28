#!/bin/bash
# session-init.sh — Minimal context injection (saves ~15K tokens)
# Only loads git state + pointer to primer
# Full primer/vault/observations available via Read tool when needed

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

echo "SessionStart:resume hook success: "

cd "$PROJECT_DIR" 2>/dev/null
echo "Branch: $(git branch --show-current 2>/dev/null)"
echo "Last commit: $(git log --oneline -1 2>/dev/null)"
echo "Uncommitted: $(git status --short 2>/dev/null | wc -l | tr -d ' ') files"
echo ""
echo "Read primer.md for full state. DO NOT auto-build."

exit 0
