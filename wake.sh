#!/bin/bash
# wake.sh — Wake up Ceiba
# Run this at the start of any session: bash wake.sh

echo ""
echo "🌳 Waking up Ceiba..."
echo "=================================="

# Inject primer (current state)
echo ""
echo "📍 CURRENT STATE (primer.md):"
echo "----------------------------------"
cat primer.md

# Inject context (big picture)
echo ""
echo "🧭 BIG PICTURE (context.md):"
echo "----------------------------------"
cat context.md

# Inject live git state
echo ""
echo "⚡ LIVE GIT STATE:"
echo "----------------------------------"
echo "Branch: $(git branch --show-current 2>/dev/null || echo 'not a git repo')"
echo ""
echo "Last 5 commits:"
git log --oneline -5 2>/dev/null || echo "No commits yet"
echo ""
echo "Modified files:"
git status --short 2>/dev/null || echo "None"
echo ""
echo "Recent errors in logs (if any):"
git log --oneline --all --grep="fix\|error\|crash\|bug" -3 2>/dev/null || echo "None found"

echo ""
echo "=================================="
echo "🌳 Ceiba is awake. What are we building?"
echo ""
