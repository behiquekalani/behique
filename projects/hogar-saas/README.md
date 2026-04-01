# Hogar SaaS — AI Compliance & Operations for Nursing Homes

## The Problem
Puerto Rico nursing homes (hogares de ancianos) get shut down for non-compliance.
One failed inspection = months of paperwork or closure.
Owners are 50-70 years old, non-technical, speak Spanish.
They manage compliance with paper binders and memory.
When regulations change, they find out when the inspector shows up.

## The Solution
An AI-powered system that:
- Tracks ALL regulatory requirements (Dept de Salud, ASES, fire, health)
- Auto-generates checklists when laws/requirements change
- Assigns daily tasks to employees via WhatsApp
- Sends medication reminders for every resident
- Tracks task completion (tap to confirm)
- Generates inspection-ready reports (print and hand to inspector)
- Flags non-compliance BEFORE the inspector finds it
- Speaks Spanish. Sends WhatsApp. No app to download.

## Architecture
```
[WhatsApp] ←→ [Twilio API] ←→ [Python Backend] ←→ [SQLite DB]
                                      ↓
                              [AI Engine (Claude API)]
                                      ↓
                              [Web Dashboard]
                              [PDF Report Generator]
```

## Why WhatsApp
- 95%+ of PR adults use WhatsApp daily
- No app installation needed
- Staff already know how to use it
- Push notifications are native
- Voice messages supported (for staff who prefer speaking)

## Revenue Model
- $500/month per hogar (basic: tasks + reminders + reports)
- $1,000/month per hogar (premium: AI compliance monitoring + law updates)
- 300+ hogares in PR = $150K-300K/month TAM
- Start with Hogar Ana Gabriel (free, proof of concept)
- First 5 paying clients = $2,500-5,000/month

## Tech Stack
- Python (FastAPI backend)
- SQLite (simple, no server needed, portable)
- Twilio WhatsApp API ($0.005/message)
- Claude API (compliance analysis, task generation)
- HTML dashboard (same dark theme as Behike products)
- WeasyPrint (PDF report generation)

## Phase 1: MVP (build now)
1. Resident database (name, conditions, medications, schedule)
2. Daily task generator (morning/afternoon/evening checklists)
3. WhatsApp task delivery (send checklist to staff)
4. Task completion tracking (staff replies "done" or taps button)
5. Basic web dashboard (see all tasks, completion %)
6. PDF daily report

## Phase 2: Compliance Engine
1. Regulatory requirement database (Dept de Salud rules)
2. Compliance checker (does this hogar meet all requirements?)
3. Gap analysis (what's missing?)
4. Corrective action generator (AI suggests how to fix gaps)
5. Inspection preparation report

## Phase 3: Intelligence
1. Pattern detection (which tasks are always late?)
2. Staff performance tracking
3. Resident health trend monitoring
4. Predictive compliance (flag risks before they happen)
5. Multi-hogar management (for owners with 2+ locations)
