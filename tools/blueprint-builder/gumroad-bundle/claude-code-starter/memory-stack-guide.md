# How to Set Up Persistent AI Memory

## The Problem

Every time you start a new conversation with an AI, it forgets everything. Your projects, your preferences, your progress, your decisions. You start from zero every single time.

This guide fixes that.

## The Solution: A 3-File Memory Stack

You need three files in your project folder. Each one serves a different purpose, and together they give your AI persistent memory across sessions.

```
your-project/
  CLAUDE.md       <- WHO you are and HOW to work with you (static)
  primer.md       <- WHERE you are right now (dynamic, rewritten every session)
  context.md      <- WHY you're doing this (semi-static, updated monthly)
```

That's it. Three files. No database. No plugins. No complicated setup.

---

## File 1: CLAUDE.md (Static Rules)

**What it is:** Your AI's instruction manual. The rules that never change session to session.

**What goes in it:**
- Your name and working style
- Active projects and their status
- Tech stack
- Communication preferences (how you want the AI to talk to you)
- Rules for every session
- Decision frameworks
- Words and phrases to never use

**How often to update:** Only when something fundamental changes. New project, new tool, changed priorities. Maybe once a month.

**How it works:** Claude Code and Cursor both read CLAUDE.md automatically when it's in your project root. If you're using ChatGPT or another tool, paste it at the top of your conversation or use Custom Instructions.

**The included CLAUDE.md template** has every section pre-built. Fill in the brackets and you're running.

---

## File 2: primer.md (Dynamic State)

**What it is:** A snapshot of where you are right now. This is the file that makes AI memory actually work.

**What goes in it:**
- What project you were working on
- What you accomplished in the last session
- What's next (specific next actions, not vague goals)
- Open blockers or decisions that need to be made
- Any context the AI needs to pick up where you left off

**How often to update:** Every single session. Your AI should rewrite this file completely at the end of each conversation.

**Example primer.md:**

```markdown
# Primer - Current State
## Last updated: 2026-03-20

## Active Focus
Building the email automation workflow for the Shopify store.

## Last Session (2026-03-19)
- Set up n8n instance on Railway
- Connected Shopify webhook for new orders
- Built the first 3 nodes of the order confirmation workflow
- Hit a bug: webhook payload doesn't include customer tags. Need to make a separate API call.

## Next Actions
1. Add a Shopify API node after the webhook trigger to fetch customer tags
2. Build the IF node that routes first-time buyers vs. repeat customers
3. Write the email templates for both paths
4. Test with a real order

## Blockers
- Need to find the Shopify API endpoint for customer tags (check their REST API docs)
- Not sure if n8n's Shopify node supports customer queries or if I need HTTP Request

## Open Decisions
- Should the welcome email go out immediately or wait 1 hour? Need to decide.

## Notes
- The n8n instance is at [URL]. Credentials are in the .env file.
- Customer said they want the emails to feel "like a friend texting, not a company emailing."
```

**Key rule:** The AI rewrites this file, not you. At the end of every session, tell your AI: "Update the primer." It captures everything fresh. Next session, it reads the primer and picks up exactly where you left off.

---

## File 3: context.md (Semi-Static Vision)

**What it is:** The big picture. Why you're building what you're building. This prevents your AI from losing sight of the forest for the trees.

**What goes in it:**
- Your long-term vision (where you want to be in 1-3 years)
- Core values that guide decisions
- Revenue goals and milestones
- What success looks like
- What you're not willing to compromise on

**How often to update:** Monthly, or when your direction changes significantly.

**Example context.md:**

```markdown
# Context - The Big Picture

## Vision
Build a portfolio of AI-powered digital products and services that generates
$10K/month in mostly-passive income within 18 months. No employees. No office.
Location-independent.

## Core Values
- Build assets, not jobs. Everything should work without me actively doing it.
- Quality over quantity. One great product beats ten mediocre ones.
- Transparency. Never sell something I wouldn't use myself.

## Revenue Targets
- Month 3: $1,000/mo (first digital product + 2 automation clients)
- Month 6: $3,000/mo (product suite + recurring automation contracts)
- Month 12: $7,000/mo (scaled products + passive income from templates)
- Month 18: $10,000/mo (full portfolio generating without daily input)

## Current Phase
Phase 1: Validate and ship. Get the first product live, get the first paying
customer, learn what actually sells vs. what I think will sell.

## Non-Negotiables
- I control the product. No clients who want to micromanage.
- No 9-5 schedule. I work when I'm sharp, rest when I'm not.
- Family time is not negotiable. Work fits around life, not the other way around.
```

---

## How to Use the Stack

### Session Start (Your AI reads the files)
1. AI reads CLAUDE.md (knows who you are, how to work with you)
2. AI reads primer.md (knows where you left off)
3. AI opens with something specific: "Last session you hit that webhook bug. Want to tackle the customer tags API call first?"

### During the Session (Normal work)
- Work on whatever you're working on
- The AI has full context from the files
- Reference context.md when making strategic decisions

### Session End (AI updates primer.md)
- Tell your AI: "Update the primer"
- It rewrites primer.md with everything from this session
- Next time you open a conversation, it reads the updated primer

That's the cycle. Read, work, update. Every session.

---

## Setup Checklist

1. [ ] Create a project folder (or use your existing one)
2. [ ] Copy the CLAUDE.md template from this bundle into your project root
3. [ ] Fill in every bracketed section in CLAUDE.md with your real information
4. [ ] Create primer.md with your current project status (just a paragraph is fine to start)
5. [ ] Create context.md with your vision and goals
6. [ ] Start a new AI session and verify it reads the files
7. [ ] At session end, have the AI rewrite primer.md
8. [ ] Start another session and verify it picks up where you left off

---

## Tips From Running This System for Months

**The primer is everything.** If you skip the primer rewrite at session end, the next session starts from zero. Make it non-negotiable.

**Don't over-structure CLAUDE.md.** Start with the basics (projects, tone, rules) and add sections as you discover what your AI keeps getting wrong. Every time you have to correct the AI twice on the same thing, add a rule for it.

**context.md prevents scope creep.** When your AI suggests a "great idea" that doesn't connect to your goals, context.md is the filter. "Does this move us toward $10K/month? No? Then not now."

**Save decisions to files, not just chat.** If you make an important decision during a session (pricing, architecture, strategy), tell the AI to save it to a decisions log or update the relevant project file. Chat history disappears. Files don't.

**Version control with git.** Put your memory stack in a git repo. Then you have a complete history of every primer update, every decision, every pivot. You can literally see how your business evolved session by session.

---

## Compatibility

This system works with:
- **Claude Code** (reads CLAUDE.md automatically from project root)
- **Cursor** (reads .cursorrules and CLAUDE.md)
- **ChatGPT** (paste CLAUDE.md content into Custom Instructions, paste primer at session start)
- **Any AI tool** (paste the files at the beginning of the conversation)

The system is tool-agnostic. The files are the source of truth, not the AI platform.
