---
type: resource
tags: [tools, stack, infrastructure, apps]
---

# Tool & Service Database

Every app, service, platform, and tool — whether we use it now, used it before, or might need it later. One place to check before adopting anything new.

---

## ACTIVE — Using Now

| Tool | What It Does | Used For | Cost |
|------|-------------|----------|------|
| GitHub | Version control, repo hosting | All code — BehiqueBot, vault, ai_cluster | Free |
| Railway | Cloud deploy, hosting | BehiqueBot production | Pay-as-you-go |
| Cloudflare | DNS, tunnels | bridge.merchoo.shop tunnel to Cobo | Free |
| Telegram | Messaging platform | BehiqueBot interface, voice memos | Free |
| Claude (Ceiba) | AI thinking partner | Everything — code, strategy, accountability | Paid |
| Cursor | AI-powered code editor | Development environment | Paid |
| n8n | Workflow automation | Self-hosted on Cobo, agency business tool | Free (self-hosted) |
| Ollama | Local LLM inference | llama3.2 on Cobo, free inference | Free |
| Syncthing | File sync between machines | ~/behique synced Mac ↔ Cobo | Free |
| OpenAI API | GPT-4o-mini + Whisper | BehiqueBot classification + voice transcription | Pay-as-you-go |
| CapCut | Video editing | AI video content, reels | Free/Paid |
| NotebookLM | AI research notebook | Research, learning | Free |
| Obsidian | Knowledge management | Vault system (migrating tomorrow) | Free |
| Discord | Community/content hub | Planned — reel preview + approval server | Free |

---

## GRAB NEXT — High Value, Not Yet Set Up

| Tool | What It Does | Why We Need It | When |
|------|-------------|---------------|------|
| Uptime Robot | Monitors uptime, alerts on downtime | BehiqueBot goes down silently — need alerts | Tomorrow |
| Sentry | Error tracking, crash reports | BehiqueBot errors caught automatically, not randomly | Tomorrow |
| Pinecone | Vector database, semantic search | Memory layer for Ceiba/BehiqueBot — search across everything by meaning | When memory system builds |
| Supabase | Backend-as-a-service, Postgres DB | BehiqueBot needs a real database, not just logs | When BehiqueBot scales |
| PostHog | Product analytics | Track user behavior when Behique Product launches | When there are users |

---

## GRAB WHEN SHIPPING — Need Users/Product First

| Tool | What It Does | Why We'd Need It | Trigger |
|------|-------------|-----------------|---------|
| Stripe | Payment processing | Collect money from n8n agency clients or Behique Product | First paying customer |
| Clerk | Authentication | User login/signup for any web product | First product with user accounts |
| Resend | Transactional email | Welcome emails, notifications, receipts | First product with email flows |
| Vercel | Frontend deployment | Host web apps, landing pages | First frontend-heavy product |
| Namesheet/Namecheap | Domain management | Custom domains for products | When branding matters |

---

## PREVIOUSLY USED — Inactive / Paused

| Tool | What It Did | Why We Stopped | Revive? |
|------|------------|---------------|---------|
| Warp | AI-powered terminal | Switched workflow to Claude Code CLI as HQ | Maybe — good terminal, just not primary anymore |
| Google Trends (manual) | Product research | Bot got banned, needs rebuild with proxies | YES — high value for eBay/Shopify pipeline |

---

## WATCHED — Interesting But Not Adopted

| Tool | What It Does | Why It's Interesting | Status |
|------|-------------|---------------------|--------|
| OpenClaw | Multi-agent platform | Competitor built full agent system on it | Watch — extract ideas, don't adopt platform |
| Veo3 | Google AI video generation | Next-gen AI video for content funnel | Learning |
| Kling | AI video generation | Alternative to Veo3 | Learning |
| Sora+ | OpenAI AI video | Another video gen option | Learning |
| getthescript.app | Instagram reel transcription | Could automate link → transcript pipeline for Ceiba | Build our own version |

---

## HOW TO USE THIS FILE

- Before adopting any new tool: check here first — do we already have something that does this?
- When dropping a tool: move it to PREVIOUSLY USED with reason
- When discovering a tool: add to WATCHED with why it's interesting
- Quarterly review: prune WATCHED, promote or kill items in GRAB NEXT
- Cost tracking: update costs when subscriptions change

---

*Ceiba rule: no tool gets adopted without being logged here first. No tool gets abandoned without recording why.*
