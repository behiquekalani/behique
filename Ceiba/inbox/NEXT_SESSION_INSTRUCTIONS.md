# Next Session Instructions — 2026-03-31

## READ FIRST
1. `mem/primer.md` — live state
2. `projects/hogar-saas/README.md` — the big project
3. `CLAUDE.md` — rules (especially rule 6-8)

## CONTINUE BUILDING: Hogar SaaS Phase 2

### What exists (Phase 1 MVP):
- `projects/hogar-saas/api/models.py` — 9 tables, full CRUD, SQLite
- `projects/hogar-saas/api/task_engine.py` — auto-generates 26 daily tasks
- `projects/hogar-saas/api/whatsapp.py` — Twilio WhatsApp integration
- `projects/hogar-saas/api/seed_ana_gabriel.py` — test data (5 residents, 7 meds, 4 staff)
- `projects/hogar-saas/dashboard.py` — admin web dashboard on port 8095
- `projects/hogar-saas/employee-app.html` — mobile task tracker with evidence + points
- Database seeded at `projects/hogar-saas/data/hogar.db`

### What to build next (Phase 2 — AI Comandante):
1. **Scheduling system** — employee shift management (who works when)
2. **Payroll tracker** — hours worked, overtime, payments
3. **Expense tracker** — supplies, food, medications, utilities
4. **Revenue tracker** — per-resident billing, insurance, ASES payments
5. **AI compliance checker** — scan requirements vs current state, flag gaps
6. **Inspection report generator** — PDF ready to hand to inspector
7. **Employee communication** — in-app messaging between admin and staff
8. **Calendar view** — visual schedule for the week/month
9. **Resident health trends** — weight, vitals, medication adherence over time
10. **Multi-hogar support** — for when mum opens second location

### Architecture notes:
- Keep everything in SQLite (no external DB needed)
- Dashboard serves HTML from Python (no React/Node needed)
- WhatsApp via Twilio ($0.005/msg)
- AI analysis via Claude API (compliance checking, report generation)
- Everything runs on one machine (Naboria when deployed)

### Kalani's vision:
- Employees use their phone (or business iPhone) like Homebase
- Admin sees everything — tasks, completion, evidence, payroll, expenses
- AI comandante handles all white-collar work automatically
- The system should feel like a game for employees (points, streaks)
- Evidence photos for medication compliance (inspection-proof)
- Spanish-first, WhatsApp-native, works for boomers

## OTHER PENDING
- 89 products ready, 11 live on Gumroad (78 to list)
- Innova Barber website needs real photos from Luis
- Luis needs to buy innovabarberpr.com ($10.46 on Cloudflare)
- Naboria needs to come online for deployments
- Rotate API keys (Telegram, OpenAI, Notion)
- YouTube Engine has 126 scripts ready

## KALANI CONTEXT
- ADHD, ideas come fast, execute immediately
- When he says build, BUILD. No lectures.
- Don't stop current task for new ideas — capture + spawn agent
- Think like co-founder, not assistant
- He pitched Luis (barber) on house calls for hogares
- His mum runs Hogar Ana Gabriel in Ciales, PR
- The Hogar SaaS is the biggest opportunity — 300+ hogares in PR
