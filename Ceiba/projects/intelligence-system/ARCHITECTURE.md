# Behike Intelligence Operating System (BIOS)
# Architecture Document v2.0
# Authors: Ceiba + Kalani + ChatGPT collaborative design
# Date: 2026-03-23
# Status: PLANNING. No code until Phase 0 is complete.

---

## What This Is

A Personal Intelligence Operating System.

Not a scraper. Not a trading bot. Not a dashboard.

A system that:
1. Observes the world continuously
2. Connects events across domains
3. Surfaces meaning before you ask for it
4. Amplifies your thinking process
5. Tracks what you planned vs what you executed
6. Evolves and learns from its own accuracy

Think: your own Bloomberg terminal + research analyst + strategic advisor + idea amplifier + accountability system, running 24/7 across your fleet.

---

## What This Is NOT

- A replacement for the content empire (that's the revenue engine, it stays)
- A "strategic pivot" (this is the next layer, not a new direction)
- A trading bot that risks money autonomously (you make the calls)
- Something we build in one session (9 phases, methodical)
- A copy of what Wall Street has (we build for one person, not a floor)

---

## How This Connects to Everything Else

The content empire, the products, BehiqueBot, the fleet. BIOS doesn't replace any of it. It makes all of it smarter.

- Content Empire: BIOS tells you WHAT to create content about (trending topics, emerging narratives)
- Products: BIOS itself could become a product ("How I built a personal Bloomberg terminal for $0")
- BehiqueBot: daily intelligence briefing via Telegram ("Good morning. Here's what matters today.")
- Newsletter: gets a "what moved this week" section powered by real data
- Polymarket: positions informed by cross-source signal confirmation
- Product timing: what's trending = what to sell now

---

## The Fleet

| Machine | IP | Hardware | Role | Always On? |
|---|---|---|---|---|
| Ceiba (Mac M4) | 192.168.0.145 | 16GB, Metal GPU | Command center, dashboard, cognitive partner | When Kalani works |
| Cobo (Windows) | 192.168.0.151 | GTX 1080 Ti 11GB | Heavy scraping, GPU tasks, video gen | Yes, except gaming mode |
| Naboria (Comp3) | 192.168.0.152 | TBD | Always-on processing, signal scoring, reports | Yes, dedicated to BIOS |

### Gaming Mode (Cobo)

```json
// C:\behique\mode.json
{
  "mode": "normal",     // "normal" or "gaming"
  "paused_since": null,
  "auto_resume": true   // resume after 4 hours if forgotten
}
```

Toggle methods:
1. Desktop shortcut (batch file)
2. Telegram command: /gaming or /resume
3. Keyboard shortcut (global hotkey)
4. Optional: auto-detect game process running

Behavior:
- gaming mode: all scrapers pause gracefully, no new jobs start, bridge stays up
- normal mode: all scrapers resume
- Telegram notification on every mode change
- Auto-resume after 4 hours if forgotten

### Fleet Orchestration

Ceiba acts as the coordinator:
- Dispatches tasks to Cobo and Naboria via bridge servers
- Monitors health of all machines
- Handles failover (if Cobo is gaming, Naboria picks up critical tasks)
- Centralized logging and status dashboard

Data sync: Syncthing (already running between Ceiba and Cobo, extend to Naboria)

---

# THE FIVE SYSTEMS

---

## SYSTEM 1: PERCEPTION (What is happening?)

The eyes and ears. Continuously collects signals from the world.

### 1A: Signal-First Architecture

Group by signal type, not source:

| Signal Type | Sources |
|---|---|
| Market-moving events | News APIs, ForexFactory, government filings |
| Narrative shifts | Reddit threads, Twitter discourse, YouTube comments |
| Sentiment changes | Social media comments, forum sentiment, Telegram channels |
| Policy/regulation | Government sites, PR news, Colmena66, IRS, SBA |
| Early anomalies | Unusual volume, quiet accounts suddenly active, prediction market spikes |

### 1B: Source Modules

Each source is independent. If one breaks, others keep running.

**Financial Markets:**
- Polymarket API (already built: tools/polymarket_telegram_bot.py)
- Crypto prices (CoinGecko API, free)
- Stock market data (Yahoo Finance API, free)
- ForexFactory calendar (economic events, rate decisions, speeches)
- Fear and Greed Index (CNN)

**Social Intelligence:**
- Twitter/X (specific accounts who consistently make good calls)
- Reddit (r/wallstreetbets, r/cryptocurrency, r/polymarket, r/economics, niche subs)
- YouTube comments (market channels, AI channels)
- Instagram comments (business/finance accounts)
- Facebook groups (relevant communities)
- Telegram channels (crypto signals, market analysis)
- Discord servers (relevant communities)
- Niche forums

**News:**
- Google News RSS (filtered by category)
- Financial news (Reuters, Bloomberg headlines)
- Tech news (AI industry tracking)
- Puerto Rico news (El Nuevo Dia, local sources)

**Government / Local:**
- Puerto Rico government announcements
- Colmena66 updates and programs
- FEMA / federal aid programs
- IRS updates relevant to PR
- Local law changes (tax, business, incentives)
- SBA programs
- Act 60 changes

**Research:**
- Google Trends (already built: tools/trends_scraper_v2.py)
- Academic papers (arxiv for AI trends)
- Patent filings (tech trend detection)

### 1C: Standardized Output

Every module outputs the same structure:

```json
{
  "id": "unique_id",
  "timestamp": "UTC",
  "source": "twitter | reddit | news | polymarket | ...",
  "content": "raw text",
  "author": {"name": "...", "reliability_score": 0.0},
  "engagement": {"likes": 0, "comments": 0, "shares": 0},
  "url": "link",
  "ingestion_confidence": 0.0
}
```

### 1D: Priority Filter

Before sending to System 2:

```
priority_score =
  (engagement_velocity * 0.3) +
  (source_credibility * 0.3) +
  (novelty_score * 0.2) +
  (cross_source_presence * 0.2)
```

- High priority: process immediately
- Low priority: batch for later or discard

### 1E: Early Event Detection

Aggregate micro-signals into macro-events before processing:

Example: 10 tweets + 3 news posts + Reddit thread about "oil disruption"
-> Event object: { type: "supply_shock", asset: "oil", confidence: 0.78 }

### 1F: Source Health Monitor

Track per module:
- Last successful fetch
- Error rate
- Data freshness
- Auto-disable failing modules
- Alert via Telegram when a source goes down

### Where it runs

- Cobo: high-frequency scrapers (social, markets)
- Naboria: news ingestion, government feeds, research
- Ceiba: fallback only, monitoring

---

## SYSTEM 2: PROCESSING (What does the data mean?)

Turns raw noise into structured, decision-ready intelligence objects.

### 2A: Parallel Enrichment Pipeline

Not linear (clean -> tag -> sentiment). Parallel:

```
Raw Signal
  |
  v
Normalization (clean, deduplicate, timestamp to PR timezone)
  |
  v (parallel)
  +-- Tagging
  +-- Sentiment Analysis
  +-- Entity Extraction
  +-- Narrative Detection
  +-- Credibility Scoring
  +-- Topic Modeling
  |
  v
Structured Intelligence Object
```

### 2B: Advanced Tagging

```json
{
  "domain": ["geopolitics", "energy"],
  "assets": ["oil", "XLE"],
  "region": ["global", "middle-east"],
  "urgency": "breaking",
  "narrative": ["supply-shock"],
  "event_type": ["conflict"],
  "time_horizon": "short-term"
}
```

### 2C: Multi-Dimensional Sentiment

Not just positive/negative. Per-asset, with confidence:

```json
{
  "sentiment": -0.7,
  "targets": [
    {"asset": "oil", "direction": "bullish", "confidence": 0.85},
    {"asset": "airlines", "direction": "bearish", "confidence": 0.72}
  ],
  "emotion": "fear"
}
```

### 2D: Narrative Detection

Track themes across posts, not individual items:

```json
{
  "narrative": "AI bubble forming",
  "volume": 342,
  "velocity": "accelerating",
  "sentiment_avg": -0.3,
  "source_diversity": 0.8,
  "first_seen": "2026-03-20",
  "status": "emerging"
}
```

### 2E: Entity Graph

Not flat extraction. Relational:

Person -> Company -> Asset -> Region
Example: Elon Musk -> Tesla -> TSLA -> US market

### 2F: Source Credibility Engine (3 levels)

1. **Source level**: Reddit vs Reuters (Reuters = 0.9, Reddit = 0.5)
2. **Author level**: specific account track record
3. **Topic level**: who is good at WHAT

```json
{
  "account": "@crypto_whale_42",
  "crypto_accuracy": 0.82,
  "macro_accuracy": 0.41,
  "average_lead_time": "2.3 days",
  "false_positive_rate": 0.22
}
```

### 2G: Feedback Loop from System 3

When predictions are wrong:
- Adjust sentiment interpretation weights
- Adjust source credibility scores
- Adjust tagging confidence

### 2H: Output Format (Intelligence Object)

Everything leaving System 2:

```json
{
  "id": "io_20260323_001",
  "timestamp": "2026-03-23T14:30:00Z",
  "event": "oil_supply_disruption",
  "assets": ["oil", "airlines", "defense"],
  "sentiment": {"oil": 0.85, "airlines": -0.72},
  "narratives": ["supply-shock", "inflation-pressure"],
  "entities": [{"person": "...", "company": "...", "region": "..."}],
  "region_relevance": {"global": 0.9, "US": 0.8, "PR": 0.4},
  "confidence": 0.78,
  "source_score": 0.83,
  "time_horizon": "short-term",
  "urgency": "high"
}
```

### Where it runs

Naboria: primary processing
Cobo: overflow when Naboria is loaded
Ceiba: monitoring only

---

## SYSTEM 3: INTELLIGENCE ENGINE (What does this connect to?)

The brain. Connects dots. Generates insights. Learns from accuracy.

### 3A: Probabilistic Causal Graph

Not static rules. A weighted, context-aware graph:

**Node**: event, asset, condition
**Edge**: causal relationship with:
- Weight (0-1): strength of connection
- Lag: time delay (hours, days, weeks, months)
- Confidence: dynamic, updated by feedback
- Context conditions: when does this edge apply?

Example:

```
Event: Oil Supply Disruption
  -> Oil Prices UP
     weight: 0.9, lag: 1-3 days
  -> Inflation UP
     weight: 0.6, lag: 2-6 weeks
  -> Airline Stocks DOWN
     weight: 0.7, lag: 1-5 days
  -> Defense Stocks UP
     weight: 0.5, lag: 1-7 days
  -> Gold UP (safe haven)
     weight: 0.65, lag: 1-3 days
```

**Context-aware edges:**

```
Fed raises rates:
  IF inflation high -> stocks DOWN (0.8)
  IF recession fears -> stocks DOWN (0.9)
  IF market already priced in -> stocks FLAT (0.4)
```

**Learning loop:**
Each prediction gets scored against actual outcome.
- Correct: increase weight and confidence
- Wrong: decrease weight, adjust lag, lower confidence
- Method: Bayesian updating or reinforcement scoring

### 3B: Signal Consensus Engine

Weighted cross-source confirmation:

```
signal_score = SUM(source_weight * signal_strength * independence_factor)
```

**Source weights:**

| Source | Weight |
|---|---|
| Official filings | 1.0 |
| Major news outlets | 0.8 |
| Niche experts (tracked accuracy) | 0.7 |
| Reddit | 0.5 |
| Random Twitter | 0.3 |

**Independence factor** (prevents echo chambers):
If 10 Twitter accounts repeat the same source, it counts as ~1.5 signals, not 10.

**Output:**
```
Event: Oil Disruption
Confidence: 82%
Source Diversity: High (4 independent sources)
Signal Velocity: Increasing
```

### 3C: Temporal Pattern Engine

Store patterns as structured data with decay and regime awareness:

```json
{
  "trigger": "Reddit crypto sentiment flips bullish",
  "outcome": "BTC +5-15%",
  "timeframe": "3-7 days",
  "confidence": 0.72,
  "sample_size": 18,
  "regime": "bull market",
  "decay_rate": 0.05
}
```

**Enhancements:**
1. Time decay: older patterns lose relevance (weight = base * e^(-decay * time))
2. Regime detection: patterns only valid in matching market conditions
3. Actor reliability: track specific accounts as leading indicators

### 3D: Anomaly / Opportunity Engine

Multi-dimensional anomaly detection:

```
anomaly_score =
  (volume_zscore * 0.3) +
  (velocity_spike * 0.3) +
  (source_diversity * 0.2) +
  (sentiment_shift * 0.2)
```

**Classification:**

| Type | Meaning | Action |
|---|---|---|
| Noise spike | Ignore | Discard |
| Coordinated push | Possible manipulation | Flag, caution |
| Early signal | HIGH VALUE | Alert immediately |
| Structural break | Market regime change | VERY HIGH VALUE |

### 3E: Decision Engine

Three output layers, not just trading:

**1. Market actions:**
- Watch specific assets
- Avoid specific sectors
- Set alerts for thresholds

**2. Strategic actions:**
- Research deeper into topic X
- Build a system around signal Y
- Track specific account Z

**3. Personal actions:**
- "This affects Puerto Rico directly"
- "This impacts your business"
- "New opportunity in your niche"

**Confidence gating:**
- 75%+: actionable, surface prominently
- 50-75%: monitor, include in daily digest
- Below 50%: log but don't alert

### 3F: Localization Engine (Puerto Rico First-Class)

Every signal gets geo-relevance scoring:

```json
{
  "geo_relevance": {
    "global": 0.9,
    "US": 0.7,
    "puerto_rico": 0.4
  }
}
```

PR-specific tracking:
- Act 60 changes (affects crypto investors moving to PR)
- Local tax incentives (affects Kalani's business directly)
- Infrastructure spending (local economy)
- Colmena66 programs and opportunities
- FEMA/federal relief programs
- Local law changes

### 3G: Time Horizon Engine

Every insight tagged:
- Immediate: hours to days (crypto moves, breaking news)
- Short-term: days to weeks (earnings, policy announcements)
- Mid-term: weeks to months (inflation trends, rate cycles)
- Long-term: months+ (infrastructure, demographic shifts)

### 3H: Synthesis Engine

This is what was missing in v1. Combines ALL sub-engines into unified insights:

```json
{
  "insight_id": "ins_20260323_001",
  "summary": "Oil supply disruption + rising social discussion + historical pattern match -> High probability of short-term oil price increase",
  "confidence": 0.82,
  "affected_entities": ["oil", "XLE", "airlines"],
  "direction": "oil UP, airlines DOWN",
  "time_horizon": "short-term (1-5 days)",
  "supporting_signals": 4,
  "source_diversity": "high",
  "pr_relevance": 0.4,
  "personal_relevance": "Gas prices may increase locally. Monitor energy costs.",
  "suggested_actions": [
    {"type": "market", "action": "Watch XLE, oil futures"},
    {"type": "strategic", "action": "Content opportunity: explain oil impact to audience"},
    {"type": "personal", "action": "Gas prices may rise in PR, plan accordingly"}
  ]
}
```

### Where it runs

Any machine. Not compute-heavy until ML is added in Phase 8.

---

## SYSTEM 4: COGNITIVE PARTNER (The Thinking Agent)

This is what makes BIOS unique. Not just automation. Structured thinking amplification.

### 4A: Intent Parser

When Kalani gives input, extract multi-dimensional intent:

```
Input: "track Instagram comments"

Parsed Intent:
  primary_goal: "track sentiment"
  domain: "social media"
  platforms: ["Instagram"]
  depth: "comments"
  hidden_goals: ["trend detection", "alpha generation", "content ideas"]
  intent_type: "data acquisition"
```

Intent types: data acquisition, strategy, exploration, execution, reflection

### 4B: Intelligent Expansion Engine

Expand across three dimensions:

**1. Adjacent sources:**
Instagram -> also TikTok, Reddit, YouTube, Telegram, Discord, niche forums

**2. Deeper dimensions:**
Content -> Comments -> Engagement velocity -> Network spread -> Influencer identification

**3. Hidden signals:**
Early adopters, meme emergence, sentiment shifts BEFORE volume spikes

**4. Failure modes:**
Bot activity, echo chambers, platform bias, manipulation

### 4C: Context Linking Engine

Every new input gets connected to existing projects:

```
New Input: "Track IG comments"

Connections:
  - Content Empire (0.9 relevance): use for topic discovery
  - Newsletter (0.8): "what the internet is talking about this week"
  - Polymarket (0.7): sentiment may precede market moves
  - Personal Brand (0.6): understand audience reactions
  - Products (0.5): identify demand signals for new products
```

This prevents wasted signals and enables cross-system compounding.

### 4D: Strategy Synthesizer

Force structured thinking output:

```
Objective: Detect early trend signals from social comments
Approach:
  - Aggregate multi-platform comments
  - Score sentiment + velocity
  - Identify leading users
Edge: Detect trends BEFORE mainstream coverage
Risk: High noise ratio, needs filtering
```

### 4E: Action Engine

Not vague suggestions. Execution-ready, prioritized:

```
Next Steps:
  [High Impact / Low Effort]
  1. Add IG comment scraper to perception layer
  2. Track comment velocity (comments/hour)

  [High Impact / Medium Effort]
  3. Cross-platform sentiment correlation
  4. Identify "early signal" users

  [Experimental]
  5. Test if comment sentiment precedes market moves
```

### 4F: Memory Engine

Persistent thinking memory:

- What Kalani is building (all projects)
- What systems exist (avoid rebuilding)
- What ideas were suggested (avoid repeating)
- What worked and what didn't (learn from history)
- What was mentioned but never acted on (ForexFactory, Colmena66)

This is the fix for "I mentioned ForexFactory and you never used it."

### 4G: Autonomous Mode

Daily intelligence report (generated without prompting):

```
DAILY COGNITIVE REPORT - 2026-03-23

1. EMERGING SIGNALS
   - Unusual Reddit activity around [topic]
   - New PR government announcement about [program]

2. MISSED OPPORTUNITIES
   - [Signal] appeared yesterday but wasn't tracked

3. SUGGESTED EXPERIMENTS
   - Track [new source] based on yesterday's patterns

4. SYSTEM IMPROVEMENTS
   - Source X failing since yesterday, consider replacement

5. CONNECTIONS TO YOUR WORK
   - [Signal] relates to your product on [topic]
```

### Where it runs

Session layer (during conversations with Ceiba).
Autonomous mode: runs as a scheduled job on Naboria.

---

## SYSTEM 5: ACCOUNTABILITY + MEMORY (What did we plan vs what happened?)

### 5A: Project Tracker

Every project:

```yaml
name: BIOS Phase 1
purpose: Foundation and control system
status: planned  # idea/planned/building/running/stalled/needs-rework/killed
value: high
last_touched: 2026-03-23
machine: all
output: job scheduler, gaming mode, notifications
next_action: "Kalani approves architecture (Phase 0)"
```

### 5B: Decision Log

```yaml
decision: "Build BIOS as a multi-phase project, not a single sprint"
date: 2026-03-23
why: "Previous sprints generated volume but not revenue. Planning prevents waste."
alternatives:
  - "Build everything at once (rejected: too complex, lost context before)"
  - "Use existing n8n (rejected: Claude Code is more capable for this)"
reconsider_if: "A commercial tool does 80% of this for under $50/month"
```

### 5C: Execution Tracker

Weekly:

```yaml
week: 2026-W13
planned:
  - "Approve BIOS architecture"
  - "List first 10 products on Gumroad"
  - "Create @behikeai Instagram"
done:
  - "BIOS architecture v2 written"
  - "READY-TO-SELL folder created (65 products)"
  - "iPad launchpad built"
blocked:
  - "Gumroad listings: needs Kalani's 15 minutes"
  - "Instagram: needs account creation"
change: "Stop autonomous building. Focus on listing and launching."
```

### 5D: Knowledge Graph (What Obsidian Was Supposed To Be)

File-based, simple:

Nodes: ideas, projects, events, decisions, tools
Edges: "relates to", "depends on", "contradicts", "builds on"

```yaml
# graph/bios.yaml
nodes:
  - id: bios
    type: project
    status: planning
  - id: polymarket_bot
    type: tool
    status: built
  - id: content_empire
    type: project
    status: active

edges:
  - from: bios
    to: polymarket_bot
    relation: "builds on"
  - from: bios
    to: content_empire
    relation: "feeds into"
```

When a new idea enters:
1. Check: "Have we thought about this before?"
2. Check: "Does this connect to or duplicate something?"
3. Check: "Does this affect any active project?"

Ceiba maintains this during sessions. Can be visualized as a simple network graph.

### Where it runs

File-based system in the main repo. Maintained by Ceiba during sessions, queryable anytime.

---

## THE DASHBOARD (What Kalani Sees)

Single HTML page. Dark mode. iPad-optimized. VR-ready (Phase 9).

```
+--------------------------------------------------+
|              WORLD (live event feed)              |
|  [scrolling ticker of top events by importance]   |
+----------+-------------------+-------------------+
|          |                   |                   |
| MARKETS  |     SIGNALS       |   PUERTO RICO    |
|          |   (AI insights)   |                   |
| BTC      | "Oil likely to    | Local news       |
| ETH      |  rise: conflict   | Gov announcements|
| S&P 500  |  + Reddit shift   | Colmena66        |
| Oil      |  + Trends spike"  | Incentives       |
| Gold     |                   | Law changes      |
| F&G Idx  | Confidence: 82%   |                   |
| Poly top | Sources: 4        |                   |
|          |                   |                   |
+----------+-------------------+-------------------+
|              TRACKER (projects + revenue)          |
|  [Project status] [Execution score] [Revenue]     |
+--------------------------------------------------+
```

---

## BUILD PHASES

| Phase | Focus | Output | Depends On |
|---|---|---|---|
| 0 | Architecture review | Approved blueprint | This document |
| 1 | Foundation + control | Scheduler, gaming mode, notifications | Phase 0 |
| 2 | First perception pipeline | One source end-to-end on Cobo | Phase 1 |
| 3 | Social intelligence | Reddit + Twitter scrapers with credibility | Phase 2 |
| 4 | Intelligence engine v1 | Causal rules, first insights | Phase 3 |
| 5 | Dashboard | Live dashboard with all panels | Phase 4 |
| 6 | Multi-machine distribution | Fleet running, health monitoring | Phase 5 |
| 7 | Cognitive partner | Idea expansion, daily reports | Phase 6 |
| 8 | Advanced intelligence | Pattern detection, ML layer | Phase 7 |
| 9 | VR/AR interface | Wall Street room in Quest 2 (WebXR) | Phase 8 |

### Phase Rules
- Complete one phase fully before starting the next
- Every phase must produce testable, visible output
- No over-engineering early (rules before ML, CSV before database)
- Review after each phase: is this useful? continue/adjust/kill?

---

## EXISTING TOOLS (Reuse, Don't Rebuild)

| Tool | Location | Reuse Strategy |
|---|---|---|
| Polymarket Telegram Bot | tools/polymarket_telegram_bot.py | Upgrade, integrate into perception |
| Polymarket Monitor | Ceiba/projects/tools/polymarket_monitor.py | Integrate into dashboard |
| Google Trends Scraper v2 | tools/trends_scraper_v2.py | Integrate into perception |
| Reddit scrapers (3) | tools/reddit_*.py | Rework for signal extraction |
| AI News Pipeline | tools/ai_news_pipeline.py | Integrate into perception |
| Overnight Machine | tools/overnight_machine.py | Upgrade into BIOS scheduler |
| Bridge Server (Cobo) | 192.168.0.151:9876 | Use as-is for task dispatch |
| Hutia Bridge Setup | Ceiba/HUTIA_SETUP.md | Deploy to Naboria |
| Content Calendar | tools/content_calendar.py | Connect to BIOS insights |
| Sprint Audit | tools/sprint_audit.py | Run on BIOS code too |

---

## PRINCIPLES

1. **OUTPUT FIRST.** Define what you want to SEE before building how to get it.
2. **ONE PIPELINE FULLY** before ten half-pipelines.
3. **MODULAR.** Each piece independent. Break one, others survive.
4. **SIMPLE V1.** Rules before ML. JSON before database. Script before service.
5. **MEASURE.** Track what works. Kill what doesn't. No zombie processes.
6. **EVOLVE.** The system learns from its own accuracy over time.
7. **PERSONAL.** This is for Kalani, not for "users." Optimize for one person.
8. **CONNECTED.** Every new piece links to existing work. Nothing exists in isolation.

---

## NEXT STEP

Phase 0: Kalani reads this document. We discuss. We answer three questions:

1. **What do you want to SEE daily?** (Define exact outputs before building inputs)
2. **What is the FIRST real use case?** (One powerful flow, not everything)
3. **How should memory work?** (This prevents the "wasted effort" feeling)

No code until these three questions are answered.
