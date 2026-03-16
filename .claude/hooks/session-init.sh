#!/bin/bash
# session-init.sh — Auto-injects Ceiba memory context at session start
# stdout goes directly into Claude Code's context window
# This is the fix for the "blank session" problem

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

echo "=========================================="
echo "  CEIBA SESSION CONTEXT — AUTO-INJECTED"
echo "=========================================="
echo ""

# 1. Git state (quick orientation)
echo "## GIT STATE"
cd "$PROJECT_DIR" 2>/dev/null
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
echo "Last 3 commits:"
git log --oneline -3 2>/dev/null || echo "No commits"
MODIFIED=$(git status --short 2>/dev/null)
if [ -n "$MODIFIED" ]; then
  echo "Uncommitted changes:"
  echo "$MODIFIED"
fi
echo ""

# 2. Primer (live state — the most important file)
if [ -f "$PROJECT_DIR/primer.md" ]; then
  echo "## PRIMER.MD (Live State)"
  cat "$PROJECT_DIR/primer.md"
  echo ""
fi

# 3. Vault Index (infrastructure map)
if [ -f "$PROJECT_DIR/Ceiba/VAULT_INDEX.md" ]; then
  echo "## VAULT INDEX"
  cat "$PROJECT_DIR/Ceiba/VAULT_INDEX.md"
  echo ""
fi

# 4. Observations (behavioral patterns)
if [ -f "$PROJECT_DIR/Ceiba/04-Patterns/observations.md" ]; then
  echo "## BEHAVIORAL PATTERNS"
  cat "$PROJECT_DIR/Ceiba/04-Patterns/observations.md"
  echo ""
fi

echo "=========================================="
echo "  CONTEXT LOADED. You are Claude Code."
echo "  You are NOT Ceiba. You are a tool."
echo "  Read the above. Know where things stand."
echo "  Do not ask 'how can I help' — check the"
echo "  primer for what needs to happen next."
echo "=========================================="

exit 0
