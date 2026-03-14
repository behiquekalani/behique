#!/bin/bash
# memory.sh — Injects live git state at Claude Code session launch
# Run this at the start of every session: bash memory.sh
# It prints a context block Claude Code reads automatically

echo "=============================="
echo "  SESSION MEMORY INJECTION"
echo "=============================="
echo ""

# Current branch
echo "## CURRENT BRANCH"
git branch --show-current 2>/dev/null || echo "Not a git repo or no branch"
echo ""

# Last 5 commits
echo "## LAST 5 COMMITS"
git log --oneline -5 2>/dev/null || echo "No commits found"
echo ""

# Modified files (uncommitted changes)
echo "## MODIFIED FILES (uncommitted)"
git status --short 2>/dev/null || echo "Nothing modified or not a git repo"
echo ""

# Recent errors from a log file if it exists
echo "## RECENT ERRORS"
if [ -f "errors.log" ]; then
  tail -10 errors.log
else
  echo "No errors.log found"
fi
echo ""

# Remind Claude to read the key files
echo "=============================="
echo "  ACTION: Read these files now"
echo "  1. primer.md   → current state"
echo "  2. context.md  → big picture"
echo "  3. CLAUDE.md   → rules & identity"
echo "=============================="
