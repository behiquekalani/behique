#!/bin/bash
# ============================================================
# wake.sh — Power On the Behique AI Cluster
# ============================================================
# Verifies all services on both machines are alive.
# Run this at session start or after Cobo comes online.
#
# Usage:
#   bash wake.sh           # full health check + context load
#   bash wake.sh --quick   # just ping services, skip context
#
# What it checks:
#   [Cobo] Ollama API (port 11434)
#   [Cobo] n8n dashboard (port 5678)
#   [Cobo] n8n tunnel (n8n.merchoo.shop)
#   [Cobo] Syncthing sync status
#   [Ceiba] CMP database
#   [Ceiba] Vault graph freshness
#   [Ceiba] primer.md exists and recent
# ============================================================

set -e

# ============ Config ============
COBO_IP="192.168.0.151"
OLLAMA_URL="http://${COBO_IP}:11434"
N8N_URL="http://${COBO_IP}:5678"
N8N_TUNNEL="https://n8n.merchoo.shop"
BEHIQUE_DIR="$HOME/behique"
BRIDGE_DIR="${BEHIQUE_DIR}/bridge"
PRIMER="${BEHIQUE_DIR}/primer.md"
VAULT_GRAPH="${BEHIQUE_DIR}/Ceiba/vault_graph.json"
CMP_DB="${BEHIQUE_DIR}/tools/ai_agent_kernel/cmp.db"

QUICK=false
[ "$1" = "--quick" ] && QUICK=true

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ok() { echo -e "  ${GREEN}✓${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; FAILURES=$((FAILURES + 1)); }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
info() { echo -e "  ${CYAN}ℹ${NC} $1"; }

FAILURES=0
SERVICES=0

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🌳 Behique AI Cluster — Wake Check    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ============ Cobo Network ============
echo "── Cobo (${COBO_IP}) ──"

# Ping
if ping -c 1 -W 2 "$COBO_IP" &>/dev/null; then
    ok "Cobo reachable"
else
    fail "Cobo unreachable at ${COBO_IP}"
    echo ""
    echo -e "${RED}Cobo is offline. Start the machine and re-run wake.sh${NC}"
    exit 1
fi

# Ollama
if curl -s --connect-timeout 3 "${OLLAMA_URL}/api/tags" &>/dev/null; then
    MODELS=$(curl -s "${OLLAMA_URL}/api/tags" | python3 -c "import sys,json; models=json.load(sys.stdin).get('models',[]); print(', '.join(m['name'] for m in models))" 2>/dev/null || echo "unknown")
    ok "Ollama alive — models: ${MODELS}"
    SERVICES=$((SERVICES + 1))
else
    fail "Ollama not responding at ${OLLAMA_URL}"
fi

# n8n local
if curl -s --connect-timeout 3 -o /dev/null -w "%{http_code}" "${N8N_URL}" | grep -q "200\|301\|302"; then
    ok "n8n dashboard alive (local)"
    SERVICES=$((SERVICES + 1))
else
    warn "n8n local not responding (may need login redirect)"
fi

# n8n tunnel
if curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" "${N8N_TUNNEL}" | grep -q "200\|301\|302"; then
    ok "n8n tunnel alive (${N8N_TUNNEL})"
    SERVICES=$((SERVICES + 1))
else
    warn "n8n tunnel not responding"
fi

echo ""

# ============ Ceiba Local ============
echo "── Ceiba (local) ──"

# primer.md
if [ -f "$PRIMER" ]; then
    AGE_SECONDS=$(( $(date +%s) - $(stat -f %m "$PRIMER") ))
    AGE_HOURS=$((AGE_SECONDS / 3600))
    if [ "$AGE_HOURS" -lt 24 ]; then
        ok "primer.md exists (updated ${AGE_HOURS}h ago)"
    else
        warn "primer.md is ${AGE_HOURS}h old — needs update"
    fi
else
    fail "primer.md not found at ${PRIMER}"
fi

# CMP database
if [ -f "$CMP_DB" ]; then
    CMP_SIZE=$(du -h "$CMP_DB" | cut -f1)
    CMP_COUNT=$(sqlite3 "$CMP_DB" "SELECT COUNT(*) FROM memories;" 2>/dev/null || echo "?")
    ok "CMP database: ${CMP_SIZE} (${CMP_COUNT} entries)"
    SERVICES=$((SERVICES + 1))
else
    warn "CMP database not found (will create on first use)"
fi

# Vault graph
if [ -f "$VAULT_GRAPH" ]; then
    NODES=$(python3 -c "import json; d=json.load(open('$VAULT_GRAPH')); print(len(d.get('nodes',[])))" 2>/dev/null || echo "?")
    GRAPH_AGE=$(( ($(date +%s) - $(stat -f %m "$VAULT_GRAPH")) / 3600 ))
    ok "Vault graph: ${NODES} nodes (${GRAPH_AGE}h old)"
else
    warn "Vault graph not found — run vault_grapher.py"
fi

# Syncthing check (file freshness)
TASKS_FILE="${BRIDGE_DIR}/tasks.md"
if [ -f "$TASKS_FILE" ]; then
    SYNC_AGE=$(( ($(date +%s) - $(stat -f %m "$TASKS_FILE")) / 60 ))
    if [ "$SYNC_AGE" -lt 60 ]; then
        ok "Syncthing active (tasks.md updated ${SYNC_AGE}m ago)"
    else
        warn "Syncthing may be stale (tasks.md is ${SYNC_AGE}m old)"
    fi
else
    warn "tasks.md not found in bridge/"
fi

echo ""

# ============ Context Load (skip with --quick) ============
if [ "$QUICK" = false ]; then
    echo "── Session Context ──"

    # Load primer summary
    if [ -f "$PRIMER" ]; then
        FOCUS=$(grep -A1 "Current Focus\|## Focus\|## What" "$PRIMER" 2>/dev/null | head -3 | tail -1)
        if [ -n "$FOCUS" ]; then
            info "Focus: ${FOCUS}"
        fi
    fi

    # Check bridge tasks
    if [ -f "$TASKS_FILE" ]; then
        PENDING=$(grep -c "\[PENDING\]" "$TASKS_FILE" 2>/dev/null || echo "0")
        IN_PROGRESS=$(grep -c "\[IN PROGRESS\]" "$TASKS_FILE" 2>/dev/null || echo "0")
        if [ "$PENDING" -gt 0 ] || [ "$IN_PROGRESS" -gt 0 ]; then
            info "Bridge tasks: ${PENDING} pending, ${IN_PROGRESS} in progress"
        fi
    fi

    # Git status
    cd "$BEHIQUE_DIR" 2>/dev/null
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    info "Git: branch=${BRANCH}, ${CHANGES} uncommitted changes"

    echo ""
fi

# ============ Summary ============
echo "══════════════════════════════════════════"
if [ "$FAILURES" -eq 0 ]; then
    echo -e "  ${GREEN}ALL SYSTEMS OPERATIONAL${NC} — ${SERVICES} services online"
else
    echo -e "  ${YELLOW}${FAILURES} issue(s) detected${NC} — ${SERVICES} services online"
fi
echo "══════════════════════════════════════════"
echo ""
