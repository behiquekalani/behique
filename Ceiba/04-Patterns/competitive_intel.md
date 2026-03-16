---
type: pattern
tags: [competitive-intelligence, product, strategy]
---

# Competitive Intelligence Log

Every time Kalani feeds competitor data (reels, tweets, product demos, conversations), Ceiba extracts and accumulates insights here. This isn't a one-off reaction — it's a growing knowledge base that informs product decisions.

---

## EXTRACTION FRAMEWORK

For every competitor signal, capture:

1. **WHO** — person/company, what they built
2. **WHAT** — specific features, architecture, capabilities
3. **GAP** — what they have that we don't
4. **EDGE** — what we have that they don't
5. **STEAL** — concrete improvements to prioritize
6. **IGNORE** — what looks shiny but doesn't serve our roadmap

---

## COMPETITOR LOG

### 001 — OpenClaw Multi-Agent Setup (2026-03-16)
**Source:** Instagram reel (shared by Kalani)
**Who:** Individual builder, OpenClaw platform user

**What they built:**
- Multiple specialized agents: boss (Craig), trainer, journal, networker
- Each connected to Telegram for mobile access
- Auto-generated email addresses for each agent
- Connected social accounts so agents know about the user
- Shared knowledge base across all agents
- To-do list connected so agents proactively help
- Agents trained on specific skills

**Gap — what they have that we don't:**
- [ ] Specialized agents (ours are filters in one monolithic bot)
- [ ] Proactive behavior (their agents act on to-do list unprompted)
- [ ] Social integrations (agents aware of public life)
- [ ] Inter-agent communication (shared knowledge base, automated)
- [ ] Auto-generated contact points (email per agent)

**Edge — what we have that they don't:**
- Clinical psychologist framework (not generic life coaching)
- Deep memory architecture (primer → observations → breadcrumbs)
- Book-to-Agent vision (auto-extract frameworks, not manual config)
- Ceiba vault with decision history and pattern tracking
- Person-to-Agent evolution path (digital twins)

**Steal — prioritized improvements:**
1. **Split BehiqueBot into specialized agents** — each filter becomes its own agent with distinct capabilities
2. **Add proactive behavior** — agents check to-do list and act without being asked
3. **Shared knowledge base** — automate what the vault does manually (agents write to and read from shared memory)
4. **Telegram as universal interface** — already done, but expand to multiple bot handles (one per agent)

**Ignore:**
- Auto-generated emails — nice to have, not core
- "100x'd my life" marketing energy — focus on what actually ships

### 002 — FocusLab Weekly Dashboard (2026-03-16)
**Source:** Instagram reel — @mindsetstack60
**Who:** MindsetStack, productivity content creator (7.7K followers)

**What they built:**
- Google Sheets weekly dashboard called "FocusLab Weekly"
- Daily task lists with checkboxes (strikethrough on completion)
- Daily completion % as donut charts (Sun–Sat)
- Overall Progress bar chart (tasks completed per day of week)
- Habit Tracker grid: wake 6am, no alcohol, cold shower, 1hr social media limit, budget tracking, gym, reading, English
- Weekly progress % per habit with horizontal bar visualization
- Overall weekly completion % (showed 39%)

**Gap — what they have that we don't:**
- [ ] Visual dashboard for task/habit completion
- [ ] Daily completion percentage tracking
- [ ] Habit tracker with streak visualization
- [ ] Weekly progress overview at a glance

**Edge — what we have that they don't:**
- Data already flows in automatically via BehiqueBot (his is 100% manual entry)
- Psychologist-backed framework (his habits are generic self-improvement)
- Ceiba can spot patterns and warn on drops (his spreadsheet is static)
- Voice memos + auto-classification (he types every checkbox)

**Steal — prioritized improvements:**
1. **Build a dashboard that auto-populates from BehiqueBot data** — tasks sent via Telegram become the checklist, completions update the %
2. **Habit tracker tied to accountability framework** — not generic habits, habits from Kalani's psychologist
3. **Weekly completion visualization** — donut charts or progress bars, generated from real data
4. **Pattern detection on the data** — Ceiba flags when completion drops 2+ days in a row

**Ignore:**
- Google Sheets as the platform — fine for him, we want something connected to the bot
- Manual data entry — the whole point is automation
- Generic habit lists — ours come from clinical framework

---

## PATTERN TRACKER

Patterns that emerge across multiple competitors:

| Pattern | Seen In | Count | Priority |
|---------|---------|-------|----------|
| Multi-agent specialization | OpenClaw | 1 | HIGH |
| Telegram as mobile interface | OpenClaw | 1 | ALREADY DONE |
| Shared knowledge base | OpenClaw | 1 | HIGH |
| Proactive task execution | OpenClaw | 1 | MEDIUM |
| Social account integration | OpenClaw | 1 | LOW |
| Visual life dashboard | FocusLab | 1 | HIGH |
| Habit tracking + streaks | FocusLab | 1 | HIGH |
| Daily/weekly completion % | FocusLab | 1 | MEDIUM |

*When a pattern appears 3+ times across competitors, it becomes a confirmed market signal.*

---

## HOW TO USE THIS FILE

1. Kalani shares competitor content → Ceiba extracts using the framework above
2. New entry added to COMPETITOR LOG with structured analysis
3. PATTERN TRACKER updated — recurring patterns get promoted
4. Patterns with 3+ signals feed directly into product roadmap decisions
5. Review quarterly: what patterns became features? What did we correctly ignore?

---

*Ceiba rule: every competitor signal gets logged here. No more one-off reactions that die in conversation.*
