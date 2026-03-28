# Session 8 — System Audit Transcript (2026-03-17)
# Saved because: comprehensive codebase audit, MCP verdict, PRE-BUILD GATE origin

---

## The 3 MCPs — Verdict

### 1. Perplexity MCP — DEFERRED
Why: Reddit integration for product research. Tavily is good for general search, but Perplexity's deep research + Reddit crawling = knowing what customers actually say about products before you list them. Direct revenue impact.

BUT: Perplexity API isn't free. Kalani canceled subscription — the API is separate, pay-per-query. Need API key from perplexity.ai.

**Decision: Add when revenue > $0. Tavily works right now.**

Install when ready:
```
claude mcp add perplexity -- npx -y @perplexity-ai/mcp-server --transport=stdio -e PERPLEXITY_API_KEY=your-key-here
```

### 2. n8n MCP — INSTALLED (FREE)
Why: n8n running on Cobo already. This MCP lets Ceiba build workflows directly instead of manual node configuration. The Stripe→email delivery workflow use case = exactly what's needed when products sell.

```
claude mcp add n8n -- npx -y n8n-mcp -e N8N_BASE_URL=http://192.168.0.151:5678 -e N8N_API_KEY=your-n8n-api-key
```

### 3. Apify MCP — INSTALLED
Why: 3,000+ pre-built scrapers. eBay sold listings scraper, TikTok scraper, Facebook Marketplace scraper, Google Trends scraper. Kills trends_scraper.py (790 lines) AND unlocks scrapers we'd never build. Free tier: $5 USD/month worth of free compute.

```
claude mcp add apify "https://mcp.apify.com?token=ROTATED_TOKEN_REPLACE_ME" -t http
```

---

## COMPREHENSIVE SYSTEM AUDIT — Behique Toolkit

### The Situation
11,500+ lines of custom code across 35+ files. Many built when connectors didn't exist or weren't known about. 16 cloud connectors active + 2 local MCPs. Time to be honest about dead weight.

### KILL — Obsolete, Replace with Connectors

| Tool | Lines | Replaced By |
|------|-------|-------------|
| setup_notion.py | 110 | Notion connector |
| chatgpt_relay.py | 170 | Direct model access + Tavily |
| morning_briefing.py | 446 | Scheduled Tasks + Slack/Gmail |
| notify.py | 170 | Slack connector |
| install-notify-agent.sh | 68 | Slack replaces custom daemon |
| export_hub_data.py | 309 | Airtable connector |
| session_logger.py | 242 | Notion connector |
| session_tracker.py | 386 | Notion + Scheduled Tasks |
| memory_ingest.py | 575 | Notion connector |
| graph_query.py | 488 | Obsidian MCP |
| vault_grapher.py | 483 | Obsidian MCP |
| vault_healer.py | 398 | Obsidian MCP |

**Total killed: ~3,845 lines — all replaced by connectors already installed.**

### KEEP BUT REFACTOR

| Tool | Lines | Why Keep |
|------|-------|----------|
| ceiba_bridge.py | 206 | Custom LAN infra — no connector |
| ceiba_audit.py | 240 | Code review routing via Cobo/Ollama |
| codegpt_bridge.py | 582 | Multi-model router (evaluate after MiniMax) |
| trends_scraper.py | 790 | Google Trends — no connector equivalent |
| ceiba_transcribe.py | 336 | Local Whisper — no connector |
| bridge/* | ~411 | Hardware-specific Cobo control |

**Total kept: ~2,565 lines — all doing things connectors can't.**

### KEEP — eBay Listing Assistant (Revenue-Critical)

| Component | Lines | Status |
|-----------|-------|--------|
| core/pipeline.py | 117 | Clean architecture |
| core/types.py | 57 | Good data models |
| core/pricing.py | 148 | Fee math works |
| core/shipping.py | 135 | PR shipping rates |
| ai/content_generator.py | 238 | Title/description gen |
| providers/ebay/research.py | 141 | Swap to Tavily |
| providers/ebay/publisher_v2.py | 631 | Needs eBay OAuth |
| run.py + quick_list.py | 521 | CLI works |

**Total: ~2,100 lines — money maker, keep all.**

### FREEZE — AI Agent Kernel (Premature)

| Component | Lines |
|-----------|-------|
| main.py | 390 |
| kernel_dispatcher.py | 192 |
| ceiba_client.py | 325 |
| cmp.py | 632 |
| cobo_server.py | 389 |
| Skills (5 files) | ~1,011 |

**Total: 2,939 lines — bridge + connectors do everything simpler.**

### SCORECARD

| Category | Lines | % |
|----------|-------|---|
| Kill (connector replaces) | 3,845 | 33% |
| Freeze (premature/duplicate) | 2,939 | 26% |
| Keep + refactor | 2,565 | 22% |
| Keep (eBay — revenue) | 2,100 | 18% |
| **Total** | **11,449** | |

**59% of codebase was dead weight. Only 40% doing real work.**

---

## PRE-BUILD GATE (established this session)

Before building ANY new tool:
1. Check MCP connectors first
2. Check existing tools
3. Ask Kalani
4. Only build custom if no connector/tool exists AND use case is truly unique

Gate check format: "Gate check: [Tool name] — Does a connector/existing tool do this?"

Origin: "u never told me about connectors" — the Obsidian situation where custom tools were built when connectors already existed.
