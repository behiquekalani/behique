# SESSION 8 FULL HANDOFF — 2026-03-17

## WHAT GOT DONE (14/16 tasks)
1. 14 obsolete tools moved to `tools/_archived/` (3,845 lines): setup_notion.py, chatgpt_relay.py, morning_briefing.py, notify.py, install-notify-agent.sh, export_hub_data.py, session_logger.py, session_tracker.py, memory_ingest.py, graph_query.py, vault_grapher.py, vault_healer.py, vault_context_engine.py, vault_templates.py, notion-triage.jsx
2. AI agent kernel + ai_cluster moved to `tools/_frozen/` (5,878 lines)
3. CLAUDE.md backed up to `Ceiba/backups/CLAUDE.md.backup.20260317` and `~/Documents/CLAUDE.md.backup`
4. Tavily eBay research adapter built: `tools/ebay-listing-assistant/providers/ebay/research_tavily.py` — extracts prices from Tavily search results, builds eBay sold listing queries, Reddit sentiment queries, plugs into existing pipeline
5. Apify MCP installed — 3,000+ pre-built scrapers (eBay, TikTok, Facebook, Google Trends). Replaces trends_scraper.py (790 lines). Token: ROTATED_TOKEN_REPLACE_ME
6. n8n MCP installed — connected to Cobo's n8n at http://192.168.0.151:5678. Can build workflows directly from Claude Code now.
7. Get Shit Done /gsd framework loaded — all slash commands available (gsd:plan-phase, gsd:execute-phase, gsd:autonomous, etc.)
8. Google Calendar wired — 3 events created: Funko listing (10AM), Hello Kitty cups (2PM), Cobo setup (4PM). Calendar ID: kalani1337@gmail.com, timezone America/Puerto_Rico
9. Folder architecture cleaned. Root went from 50 items to 22. Moved: HTML dashboards → dashboards/ and Ceiba/dashboards/, .skill files → skills/, legacy scripts → _legacy/, wake.sh → bridge/. Restored main.py to root (Railway needs it there).
10. Cobo bridge connected and verified. Bridge at http://192.168.0.151:9876 responds with {"status":"Bridge active","machine":"Cobo","execEnabled":false,"anthropicConfigured":false}. Token saved at ~/.behique_bridge_token (value: tmp-token)
11. BehiqueBot redeployed on Railway from Ceiba (not Cobo — Railway CLI is on Mac). Deploy successful, bot polling Telegram.
12. Notion 401 FIXED. Root cause: integration wasn't connected to the BehiqueBot page in Notion. Fix: ... menu → Connections → added BehiqueBot integration. New token was already in Railway. Confirmed working: sent "hello" to bot, got classified response, Notion entry created with ID c3f55575.
13. Ollama running on Cobo — llama3.2 (3.2B, Q4_K_M, 2GB). Verified via API: http://192.168.0.151:11434/api/tags
14. BehiqueBot swapped from OpenAI ($5/mo) to MiniMax M2.5 via OpenRouter (~$0/mo). Changes: (a) Modified modules/classifier.py to read FALLBACK_BASE_URL and FALLBACK_MODEL from env vars instead of hardcoding. (b) Set Railway env vars: OPENAI_BASE_URL=https://openrouter.ai/api/v1, FALLBACK_MODEL=minimax/minimax-m2.5, OPENAI_API_KEY=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. (c) Redeployed. Had polling conflict during redeploy (resolved itself). Kalani put $5 credit on OpenRouter with $5 limit.

## WHAT'S LEFT (2 tasks)
15. Airtable inventory base — Kalani started creating it on airtable.com. The AI assistant proposed 3 tables (items, stock movements, reports). Airtable connector is installed but needs a base ID to work with. No bases exist yet in the account.
16. PASTE FUNKO POP LISTING ON EBAY — listing file: tools/ebay-listing-assistant/listings/funko_pop_the_godfather_vito_corleone_mi_20260316_155205.txt. Price: $27.99 each, qty 3, profit $11.22/unit ($33.66 total). Free shipping via USPS First Class from Puerto Rico.

## EXACT CODE CHANGES

### modules/classifier.py (modified)
Added env var support for model routing. Changed from:
```python
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```
To:
```python
FALLBACK_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-4o-mini")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=FALLBACK_BASE_URL,
)
```
And changed hardcoded model:
```python
# Was: return _classify_with_client(openai_client, "gpt-4o-mini", text)
# Now: return _classify_with_client(openai_client, FALLBACK_MODEL, text)
```

### tools/ebay-listing-assistant/providers/ebay/research_tavily.py (NEW — ~180 lines)
Tavily-powered eBay research adapter. Key methods:
- build_tavily_query(product) — generates search query for eBay sold listings
- build_reddit_query(product) — generates Reddit sentiment query
- extract_prices_from_text(text) — regex price extraction ($XX.XX patterns)
- parse_tavily_results(results) — converts Tavily output → ResearchResult dataclass
- from_ceiba_session(sold_results, active_results) — convenience method for in-session use

### ~/.claude.json (modified)
Added MCP servers:
- apify: HTTP MCP at https://mcp.apify.com?token=...
- n8n: stdio MCP via npx n8n-mcp with N8N_BASE_URL and N8N_API_KEY env vars

### ~/.behique_bridge_token (created)
Contains: tmp-token (for Cobo bridge auth)

### primer.md (full rewrite)
Updated with all session 8 state, new infrastructure, cleaned architecture.

## ACTIVE INFRASTRUCTURE STATE
- Ceiba (Mac): Claude Code + 17 MCP connectors
- Cobo (Windows, 192.168.0.151): bridge on :9876, n8n on :5678, Ollama on :11434 (all verified working)
- Railway: BehiqueBot running with MiniMax M2.5 via OpenRouter, Notion persistence working
- Comp3: Kalani setting up (unknown state)
- Syncthing: syncing behique/ between machines

## RAILWAY ENV VARS (current)
- TELEGRAM_BOT_TOKEN: active (rotated)
- NOTION_SECRET: active (new token)
- NOTION_DATABASE_ID: active
- OPENAI_API_KEY: sk-or-v1-... (OpenRouter key, NOT OpenAI)
- OPENAI_BASE_URL: https://openrouter.ai/api/v1
- FALLBACK_MODEL: minimax/minimax-m2.5

## MCP SERVERS INSTALLED
Local (in ~/.claude.json):
1. Zapier — HTTP
2. Obsidian — stdio (npx mcp-obsidian, port 27123)
3. Apify — HTTP (https://mcp.apify.com?token=...)
4. n8n — stdio (npx n8n-mcp, connected to 192.168.0.151:5678)

Cloud (claude.ai connectors):
5. Notion
6. Gmail
7. Google Calendar
8. Slack
9. Canva
10. Figma
11. Airtable
12. Tavily
13. Hugging Face
14. Claude in Chrome
15. Claude Preview
16. Scheduled Tasks
17. MCP Registry

## COMPREHENSIVE AUDIT RESULTS (from earlier in session)
59% of codebase was dead weight. Breakdown:
- KILL (connector replaces): 3,845 lines → tools/_archived/
- FREEZE (premature): 5,878 lines → tools/_frozen/
- KEEP + refactor: 2,565 lines (bridge, audit, transcribe, codegpt, trends_scraper)
- KEEP (revenue): 2,100 lines (ebay-listing-assistant)

Tools that stay active: ceiba (CLI), ceiba_audit.py, ceiba_bridge.py, ceiba_run.py, ceiba_transcribe.py, codegpt_bridge.py, ebay-listing-assistant/, n8n-workflows/, trends_scraper.py

## MINIMAX M2.5 EVALUATION
- $0 input / $0.001/M output on OpenRouter
- Anthropic-compatible API — swap base URL and key, everything works
- Within 0.6% of Opus on SWE-Bench Verified
- For BehiqueBot classification (tiny messages): essentially free
- GLM-5 also has free tier via Puter.js as backup option
- Kalani deposited $5 on OpenRouter with $5 limit

## NEW TOOLS TO EVALUATE (from Kalani's research)
1. Perplexity MCP — Reddit integration for product research. Deferred until revenue > $0 (API costs money)
2. Get Shit Done /gsd — installed, all commands available. Use for next complex build.
3. MiniMax M2.5 for Claude Code itself — can swap ANTHROPIC_BASE_URL to use MiniMax instead of Anthropic for coding tasks (saves money)

## KALANI FEEDBACK / RULES
- PRE-BUILD GATE is now in CLAUDE.md: check connectors before building anything custom
- "buy then build" — always check if a tool/connector exists first
- "u never told me about connectors" — the Obsidian situation, never repeat
- "youre not human to be making mistakes" — systematic prevention, not promises
- Cobo's Claude keeps modifying classifier.py causing system notification spam — tell it to stop touching files that Ceiba manages

## NEXT SESSION PRIORITIES
1. Post Funko Pop listing on eBay (revenue = $0)
2. List Hello Kitty cups using Tavily research adapter
3. Finish Airtable inventory base setup
4. Test n8n MCP — build first workflow from Ceiba
5. Test Apify scraper for eBay product research
6. Evaluate /gsd for next complex build
7. Build n8n workflow: purchase → email delivery (for when products sell)
