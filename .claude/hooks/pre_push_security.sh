#!/bin/bash
# Pre-push security scan — catches exposed secrets before they hit GitHub.
# Installed as a Claude Code PreToolUse hook that fires before git push.
# Also works as a standalone git pre-push hook.

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# Patterns that should NEVER be in committed code
PATTERNS=(
    'TELEGRAM_BOT_TOKEN\s*=\s*"[^"]{10,}'
    'OPENAI_API_KEY\s*=\s*"sk-'
    'NOTION_SECRET\s*=\s*"ntn_'
    'Authorization:\s*Bearer\s+[a-f0-9]{20,}'
    'BRIDGE_TOKEN\s*=\s*"[a-f0-9]{20,}'
    'api_key\s*=\s*"[a-zA-Z0-9_-]{20,}'
    'password\s*=\s*"[^"]{6,}'
    'secret\s*=\s*"[^"]{10,}'
)

FOUND=0

for pattern in "${PATTERNS[@]}"; do
    # Search tracked files only (not .gitignored)
    matches=$(git -C "$PROJECT_ROOT" grep -rn -E "$pattern" -- '*.py' '*.js' '*.ts' '*.sh' '*.json' '*.yaml' '*.yml' '*.md' 2>/dev/null | grep -v '.ceiba-config' | grep -v 'node_modules' | grep -v '.env')
    if [ -n "$matches" ]; then
        if [ "$FOUND" -eq 0 ]; then
            echo "SECURITY: Potential secrets found in tracked files:"
            echo "==========================================="
        fi
        echo "$matches"
        FOUND=1
    fi
done

# Check for .env files that shouldn't be committed
env_files=$(git -C "$PROJECT_ROOT" ls-files '*.env' '.env.*' 2>/dev/null)
if [ -n "$env_files" ]; then
    echo "SECURITY: .env files are tracked by git (should be in .gitignore):"
    echo "$env_files"
    FOUND=1
fi

if [ "$FOUND" -eq 1 ]; then
    echo ""
    echo "Fix these before pushing. Move secrets to environment variables or ~/.ceiba-config."
    exit 1
fi

exit 0
