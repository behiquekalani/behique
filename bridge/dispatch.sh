#!/bin/bash
# Ceiba → Cobo Task Dispatcher
# Usage: bash dispatch.sh <lane> <prompt>
# Lanes: fast (Ollama), worker (GPT-4o via OpenClaw), brain (stays local)

BRIDGE_TOKEN="${BRIDGE_TOKEN:-$(cat ~/.behique_bridge_token 2>/dev/null)}"
BRIDGE_URL="http://192.168.0.151:9876"
OLLAMA_URL="http://192.168.0.151:11434/api/generate"
COBO_IP="192.168.0.151"

LANE="$1"
shift
PROMPT="$*"

if [ -z "$LANE" ] || [ -z "$PROMPT" ]; then
  echo "Usage: dispatch.sh <fast|worker|brain> <prompt>"
  exit 1
fi

case "$LANE" in
  fast)
    # Ollama — free, fast, simple tasks
    JSON_BODY=$(python3 -c "import json,sys; print(json.dumps({'model':'llama3.2','prompt':sys.argv[1],'stream':False}))" "$PROMPT")
    curl -s -X POST "$OLLAMA_URL" \
      -H "Content-Type: application/json" \
      -d "$JSON_BODY" \
      | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])"
    ;;
  worker)
    # GPT-4o via OpenClaw agent — heavy reasoning
    ESCAPED_PROMPT=$(echo "$PROMPT" | sed 's/"/\\"/g')
    RESULT=$(curl -s -X POST "$BRIDGE_URL" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $BRIDGE_TOKEN" \
      -d "{\"command\": \"openclaw agent --agent main --local --message \\\"$ESCAPED_PROMPT\\\" --json --timeout 60 2>&1\"}" \
      --connect-timeout 70)

    # Extract just the text response from the JSON
    echo "$RESULT" | python3 -c "
import sys, json
raw = json.load(sys.stdin)
stdout = raw.get('stdout', '')
try:
    data = json.loads(stdout.split('\n{')[0] + '\n' if '{' not in stdout[:5] else stdout)
except:
    try:
        # Find the JSON payload in stdout
        import re
        match = re.search(r'\{.*\"payloads\".*\}', stdout, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            print(stdout)
            sys.exit(0)
    except:
        print(stdout)
        sys.exit(0)
payloads = data.get('payloads', [])
if payloads:
    print(payloads[0].get('text', ''))
else:
    print(stdout)
"
    ;;
  brain)
    echo "[BRAIN lane — task stays on Ceiba/Claude Opus]"
    echo "Prompt: $PROMPT"
    echo "Handle this locally."
    ;;
  *)
    echo "Unknown lane: $LANE. Use fast, worker, or brain."
    exit 1
    ;;
esac
