---
title: "X/Twitter Threads Batch 4"
type: content
tags: [twitter, x, threads, content]
created: 2026-03-22
---

# X/Twitter Thread Templates Batch 4
# Accounts: @kalaniandrez and @behikeai
# Voice: Behike Voice Bible. Short. Direct. Thesis-first. No em dashes.

---

## THREAD 1: I Gave Claude Code a CLAUDE.md and It Changed Everything
**Account:** @behikeai
**Hook:** "I gave Claude Code a CLAUDE.md and it changed everything (thread):"

---

I gave Claude Code a CLAUDE.md and it changed everything (thread):

---

Without it, Claude Code starts every session blind.

It doesn't know your project. Doesn't know your stack. Doesn't know your naming conventions or what you already decided last week.

CLAUDE.md fixes that.

---

What CLAUDE.md is:

A plain markdown file you drop in your project root. Claude Code reads it automatically at the start of every session.

It's not a prompt. It's persistent context. It changes how the model behaves across every conversation.

---

What to put in it:

1. Project overview. What this codebase does in 3-5 sentences. What it's not.

2. Tech stack. Languages, frameworks, libraries. What versions matter.

3. Code style rules. How you name functions. Where types go. Whether you use tabs or spaces.

4. Forbidden patterns. Things the model should never do. "Never add comments to obvious code." "Never use any as a TypeScript type."

---

5. Session protocol. What to read first. What files have the current state. Where the active task lives.

This is where CLAUDE.md goes from useful to transformative.

When the model knows to read primer.md and tasks.md before touching anything, it doesn't repeat work you already did.

---

Before CLAUDE.md:

Every session starts with: "I'm working on a Python project that..." and then you spend 10 minutes re-explaining context the model already lost.

After CLAUDE.md:

You open a session and the model already knows the stack, the conventions, what's in progress, and what was decided yesterday.

---

The difference in real work:

Before: "Use snake_case for functions."
After: Claude uses snake_case by default because you wrote it once in CLAUDE.md and it reads it every time.

Before: "Don't rewrite files from scratch."
After: The model edits existing files because that's in the rules.

One file. Compounding returns.

---

CLAUDE.md is not magic. It's just persistent context.

But persistent context is what separates a tool that assists from one that actually thinks with you.

If you're using Claude Code without one, you're leaving most of its capability on the table.

---

I built a full Claude Code workflow course covering CLAUDE.md, session protocols, memory stacks, and how to run a one-person dev operation with AI.

Get it here:

https://behikeai.gumroad.com/l/claude-code-course

---

## THREAD 2: The Math Behind Digital Products Nobody Talks About
**Account:** @kalaniandrez
**Hook:** "The math behind digital products nobody talks about (thread):"

---

The math behind digital products nobody talks about (thread):

---

Everyone says "sell a PDF and make passive income."

Nobody shows you the actual numbers. So here they are.

---

A $9.99 product on Gumroad.

You sell 100 copies. That looks like $999.

It isn't.

---

What you actually keep on 100 sales at $9.99:

Gross revenue: $999.00
Gumroad fee (10%): $99.90
Payment processing (~3%): $29.97

Net after fees: $869.13

That's what hits your account. Not $999.

---

Annualize it:

$869 net per month, 12 months = $10,428/year from one PDF.

That number is real. And it's from 100 sales a month, which is about 3-4 per day.

Not millions of followers. Not viral videos. Three sales a day.

---

Refund rates:

Industry average is 2-5% for digital products with clear descriptions.

On 100 sales, that's 2-5 refunds. At $9.99 each, you lose $20-50.

Practical fix: write a better product page. Clear outcomes. Honest scope. Refund rates drop when buyers know exactly what they're getting.

---

The traffic math:

If 1-3% of visitors buy, you need 3,300-10,000 monthly visitors to hit 100 sales.

That sounds like a lot until you realize one thread going to 500 followers who reshare it can drive 5,000 impressions in a day.

You don't need a big audience. You need one piece of content that converts.

---

Why the margins are better than physical products:

No inventory. No shipping. No returns that cost you a physical item.

Your cost per unit sold is $0. The only cost is creating the product once.

That means every sale after the first one is pure margin minus fees. No physical product business works like that.

---

The real ceiling isn't the product. It's traffic.

Solve traffic once and the math scales without you doing more work.

That's what makes digital products worth building.

---

The Solopreneur OS breaks down the full system: product selection, pricing, traffic, and the exact workflow for building a one-person digital product business.

https://behikeai.gumroad.com/l/solopreneur-os

---

## THREAD 3: I Analyzed 50 Claude Prompts That Went Viral. Here's the Pattern.
**Account:** @behikeai
**Hook:** "I analyzed 50 Claude prompts that went viral. Here's the pattern (thread):"

---

I analyzed 50 Claude prompts that went viral. Here's the pattern (thread):

---

Most people write prompts like they're texting.

"Write me a blog post about AI."

The prompts that go viral are built differently. Here's the structure they all share.

---

The 4-part structure:

1. Context. What situation the model is in.
2. Role. Who or what the model should behave as.
3. Format. What the output should look like.
4. Constraint. What the model should not do.

Every high-performing prompt has at least 3 of these 4 parts. Most have all 4.

---

Example 1: The Analyst

"You are a business analyst reviewing a startup pitch deck. The founder has 10 minutes of your time. Ask the 5 most important questions an investor would ask. One question per line. No commentary between questions."

Context: pitch deck review.
Role: business analyst.
Format: 5 questions, one per line.
Constraint: no commentary.

---

Example 2: The Editor

"You are an editor at The Atlantic. I will give you a paragraph. Rewrite it so it reads at an 8th grade level without losing the argument. Return only the rewritten paragraph."

Context: paragraph editing.
Role: Atlantic editor.
Format: single rewritten paragraph.
Constraint: return only the paragraph, nothing else.

---

Example 3: The Devil's Advocate

"You are a critic hired to find every reason this plan will fail. Here is the plan: [plan]. List every flaw, assumption risk, and blind spot. Be specific. Do not offer solutions. Only problems."

Context: plan review.
Role: critic.
Format: list of flaws.
Constraint: no solutions.

---

Example 4: The Simplifier

"Explain [concept] as if I am a smart 12-year-old. Use one analogy. No jargon. Maximum 5 sentences."

Context: concept explanation.
Role: teacher.
Format: 5 sentences, one analogy.
Constraint: no jargon.

---

Example 5: The Copywriter

"You are a direct response copywriter. Write a 3-sentence product description for [product]. Lead with the specific result the buyer gets. End with a one-sentence reason to buy now. No hype words."

Context: product copy.
Role: DR copywriter.
Format: 3 sentences.
Constraint: no hype words.

---

What makes them work:

They give the model a lens to see through. Not just a task but a perspective.

The constraint is the most underused part. Telling the model what NOT to do cuts 80% of the generic output that makes AI writing feel like AI writing.

---

50 of these prompts, organized by use case, are in the AI Prompt Cheat Sheet.

Writing, research, business analysis, content creation, and coding. Ready to copy and paste.

https://behikeai.gumroad.com/l/ai-prompt-cheat-sheet

---

## THREAD 4: The Only 4 AI Tools You Need to Run a One-Person Business
**Account:** @behikeai
**Hook:** "The only 4 AI tools you need to run a one-person business (thread):"

---

The only 4 AI tools you need to run a one-person business (thread):

---

Everyone publishes "50 AI tools you need to know."

The list is always wrong. You don't need 50. You need 4, and they need to work together.

Here's the real stack.

---

1. Claude (thinking layer)

This is where decisions happen. Research, writing, strategy, code reviews, content drafts.

Claude is the thinking partner, not a button you press. When you learn to write structured prompts, it operates as a real collaborator.

Cost: $20/month for Pro. Worth it before anything else on this list.

---

2. n8n (automation layer)

n8n connects everything. APIs, webhooks, databases, external tools.

You build flows once. They run on a schedule or trigger automatically.

Use case: new form submission triggers a Notion entry, a welcome email, and a Telegram notification. One build, zero manual work after.

Cost: self-hosted is free. Cloud starts at $20/month.

---

3. Notion (memory layer)

This is where outputs live. Research, decisions, content drafts, project notes, product ideas.

The goal is that anything Claude produces, any decision you make, any content you create gets stored here. It becomes searchable context.

Without a memory layer, you repeat work. Notion prevents that.

Cost: free tier covers most of what you need early.

---

4. Canva (visual layer)

Every product, post, and page needs visuals. Canva handles it without a designer.

Use the AI features: background remover, Magic Write for copy, auto-resize for repurposing across formats.

The rule: every post gets one strong visual. Canva makes that achievable in under 10 minutes.

Cost: free tier is enough to start. Pro at $15/month when you're producing daily.

---

How they connect:

You think in Claude. You automate with n8n. You store in Notion. You publish with Canva.

Four tools. One flow. No subscription creep.

What to skip: every AI image generator, every "all-in-one" tool, every tool that promises to replace one of these four. They don't.

---

The AI Employee Guide shows how to connect this exact stack into a working system that runs daily tasks without you.

Workflows, prompt templates, and the full setup guide included.

https://behikeai.gumroad.com/l/ai-employee-guide

---

## THREAD 5: I Built 3 Income Streams in 90 Days. Here's Exactly How.
**Account:** @kalaniandrez
**Hook:** "I built 3 income streams in 90 days. Here's exactly how (thread):"

---

I built 3 income streams in 90 days. Here's exactly how (thread):

---

Not a flex post. A breakdown of what I actually built, what the numbers looked like, and what I'd do differently.

Three streams. Ninety days. One person.

---

Stream 1: Digital products on Gumroad

What I built: 9 products covering AI tools, business frameworks, and creator guides.

How long it took: about 6 weeks from first product to all 9 live.

The process: identify a question I already knew the answer to, build a PDF around it, write a product page, list it.

Revenue in first 30 days after launch: modest. The catalog was more important than any single product.

---

Stream 2: Content on Instagram and YouTube

What I built: @behikeai on Instagram, short-form Reels, and the beginning of a YouTube channel.

How long it took: 4 weeks to establish a consistent posting rhythm.

The process: batch content every Sunday for the week. One big idea becomes a Reel, a thread, a YouTube short, and an Instagram post.

Revenue model: drives traffic to the Gumroad catalog. Content is the distribution layer.

---

Stream 3: Service (AI installs)

What I built: a service offering where I set up AI employee systems for small businesses using n8n and Claude.

How long it took: first client within 3 weeks of putting it out.

Revenue model: flat rate per setup. Higher ticket than products. Fewer clients needed.

This stream funds the business while the product and content sides build.

---

What the numbers looked like at 90 days:

Products: catalog live, early sales, growing with content volume.
Content: consistent posting, audience building, traffic increasing weekly.
Services: 2 paid clients in 90 days.

Combined, I was covering expenses. Not retiring. Covering expenses.

That's what 90 days actually looks like. Not 6 figures. Proof of concept.

---

What I'd do differently:

Start the service first. It generates cash immediately. Products take time to get traffic. Services don't.

Start one content channel, not three. I spread across platforms too early. Depth on one platform beats shallow presence on four.

Build the email list from day one. The audience you don't own is the audience you'll lose.

---

If you're building a one-person business and want the full framework behind how I set this up, including the product strategy, content system, and service packaging:

The Behike Method v2 is the document.

https://behikeai.gumroad.com/l/behike-method-v2

---

## POSTING SCHEDULE

| Thread | Account | Day | Notes |
|--------|---------|-----|-------|
| Thread 3 (50 Viral Prompts) | @behikeai | Week 1, Day 1 | High shareability. Pin candidate. |
| Thread 5 (3 Income Streams) | @kalaniandrez | Week 1, Day 3 | Personal. Trust builder. High engagement. |
| Thread 4 (4 AI Tools) | @behikeai | Week 1, Day 5 | Practical value. Shareable list format. |
| Thread 2 (Digital Product Math) | @kalaniandrez | Week 2, Day 2 | Specific numbers. Strong trust signal. |
| Thread 1 (CLAUDE.md) | @behikeai | Week 2, Day 4 | Technical audience. High retweet potential. |

---

## NOTES ON FORMAT

Each thread is posted as a reply chain. Hook tweet goes up first, standalone.

Every internal tweet works as a solo post if someone quote-tweets it. Write each one that way.

Threads 2 and 5 contain specific numbers. Numbers perform. Keep them exact.

Thread 3 is the most shareable for @behikeai. Pin it after posting.

Thread 5 is the highest-traffic entry point for new followers on @kalaniandrez. Personal story with real numbers outperforms almost anything else.

Every CTA links to a specific product. No thread ends without a Gumroad link.

Cross-post each thread to Instagram as a carousel within 24 hours of posting on X.
