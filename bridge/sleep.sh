#!/bin/bash
# ============================================================
# sleep.sh — Graceful Shutdown / End-of-Session for Behique
# ============================================================
# Run this at end of work session. It:
#   1. Saves session state (primer.md check)
#   2. Exports CMP stats
#   3. Commits any uncommitted work
#   4. Updates bridge tasks
#   5. Shows what was accomplished
#
# Usage:
#   bash sleep.sh              # full shutdown routine
#   bash sleep.sh --no-commit  # skip git commit
#
# Note: This does NOT power down Cobo. Cobo stays alive for
# overnight tasks, n8n automations, and Syncthing sync.
# ============================================================

set -e

# ============ Config ============
BEHIQUE_DIR="$HOME/behique"
PRIMER="${BEHIQUE_DIR}/primer.md"
CMP_DB="${BEHIQUE_DIR}/tools/ai_agent_kernel/cmp.db"
BRIDGE_TASKS="${BEHIQUE_DIR}/bridge/tasks.md"
LOG_DIR="${BEHIQUE_DIR}/Ceiba/07-Transcripts"

NO_COMMIT=false
[ "$1" = "--no-commit" ] && NO_COMMIT=true

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🌙 Behique AI Cluster — Sleep Mode    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ============ Session Stats ============
echo "── Session Summary ──"

# CMP stats
if [ -f "$CMP_DB" ]; then
    CMP_COUNT=$(sqlite3 "$CMP_DB" "SELECT COUNT(*) FROM memories;" 2>/dev/null || echo "0")
    CMP_TODAY=$(sqlite3 "$CMP_DB" "SELECT COUNT(*) FROM memories WHERE date(timestamp) = date('now');" 2>/dev/null || echo "0")
    echo -e "  ${CYAN}ℹ${NC} CMP: ${CMP_COUNT} total entries, ${CMP_TODAY} added today"
else
    echo -e "  ${DIM}  CMP database not found${NC}"
fi

# Git changes
cd "$BEHIQUE_DIR" 2>/dev/null
BRANCH=$(git branch --show-current 2>/dev/null || echo "?")
UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
COMMITS_TODAY=$(git log --oneline --since="midnight" 2>/dev/null | wc -l | tr -d ' ')
echo -e "  ${CYAN}ℹ${NC} Git: ${COMMITS_TODAY} commits today, ${UNCOMMITTED} uncommitted files, branch=${BRANCH}"

# Files changed today
FILES_MODIFIED=$(git diff --name-only HEAD~${COMMITS_TODAY} HEAD 2>/dev/null | wc -l | tr -d ' ')
echo -e "  ${CYAN}ℹ${NC} Files touched: ${FILES_MODIFIED} across ${COMMITS_TODAY} commits"

# primer.md check
if [ -f "$PRIMER" ]; then
    AGE_SECONDS=$(( $(date +%s) - $(stat -f %m "$PRIMER") ))
    AGE_MINUTES=$((AGE_SECONDS / 60))
    if [ "$AGE_MINUTES" -gt 120 ]; then
        echo -e "  ${YELLOW}⚠${NC} primer.md last updated ${AGE_MINUTES}m ago — NEEDS UPDATE before sleep"
    else
        echo -e "  ${GREEN}✓${NC} primer.md is fresh (${AGE_MINUTES}m old)"
    fi
else
    echo -e "  ${RED}✗${NC} primer.md missing — session state will be lost!"
fi

echo ""

# ============ Bridge Task Status ============
if [ -f "$BRIDGE_TASKS" ]; then
    echo "── Bridge Tasks ──"
    PENDING=$(grep -c "\[PENDING\]" "$BRIDGE_TASKS" 2>/dev/null || echo "0")
    IN_PROGRESS=$(grep -c "\[IN PROGRESS\]" "$BRIDGE_TASKS" 2>/dev/null || echo "0")
    DONE=$(grep -c "\[DONE\]" "$BRIDGE_TASKS" 2>/dev/null || echo "0")
    echo -e "  Pending: ${PENDING} | In Progress: ${IN_PROGRESS} | Done: ${DONE}"

    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠${NC} Tasks still in progress — Cobo will continue working"
    fi
    echo ""
fi

# ============ Cobo Status ============
echo "── Cobo Status ──"
COBO_IP="192.168.0.151"
if ping -c 1 -W 2 "$COBO_IP" &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Cobo is online — will stay alive for overnight tasks"

    # Quick Ollama check
    if curl -s --connect-timeout 2 "http://${COBO_IP}:11434/api/tags" &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Ollama: running"
    fi
    if curl -s --connect-timeout 2 -o /dev/null "http://${COBO_IP}:5678" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} n8n: running"
    fi
else
    echo -e "  ${DIM}  Cobo is offline${NC}"
fi

echo ""

# ============ Auto-commit (optional) ============
if [ "$NO_COMMIT" = false ] && [ "$UNCOMMITTED" -gt 0 ]; then
    echo "── Auto-Save ──"
    echo -e "  ${CYAN}ℹ${NC} ${UNCOMMITTED} uncommitted files found"
    echo -e "  ${DIM}  Run 'bash sleep.sh --no-commit' to skip auto-save${NC}"
    echo -e "  ${YELLOW}  Note: Auto-commit disabled — commit manually or ask Ceiba${NC}"
fi

echo ""

# ============ Session Log ============
SESSION_LOG="${LOG_DIR}/session_$(date +%Y-%m-%d).md"
mkdir -p "$LOG_DIR" 2>/dev/null

# Append session end marker
cat >> "$SESSION_LOG" 2>/dev/null <<EOL

---
### Session End: $(date '+%Y-%m-%d %H:%M')
- Commits today: ${COMMITS_TODAY}
- Files modified: ${FILES_MODIFIED}
- CMP entries added: ${CMP_TODAY}
- Uncommitted: ${UNCOMMITTED}
---
EOL

echo -e "  ${GREEN}✓${NC} Session logged to $(basename "$SESSION_LOG")"

echo ""
echo "══════════════════════════════════════════"
echo -e "  ${GREEN}Session saved. Cobo stays alive.${NC}"
echo -e "  ${DIM}  Run 'bash wake.sh' next session.${NC}"
echo "══════════════════════════════════════════"
echo ""
