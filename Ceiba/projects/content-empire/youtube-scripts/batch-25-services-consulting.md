---
title: "YouTube Batch 25 — Services and Consulting"
type: content
tags: [youtube, scripts, services, consulting, automation, n8n]
created: 2026-03-22
batch: 25
---

# YouTube Batch 25 — Services and Consulting

---

## Script 1: "I Can Automate That: How I Pitch AI Automation to Local Businesses"

**[HOOK — first 15 seconds]**

Most small businesses have a problem they've stopped thinking about. Not because it's solved. Because they got used to it.

That's the opening. That's where the pitch starts.

---

**[SCRIPT]**

The first time I walked into a business and said "I can automate that," I had no deck. No case study. No agency name on a card.

What I had was thirty minutes and a specific question.

Here's the question: "What's the most repetitive thing your team does every week that doesn't require a human decision?"

That question does two things. It positions you as someone who thinks in systems. And it makes the business owner do the work of finding their own problem.

Nine times out of ten, they'll name something within two minutes. Inventory checks. Answering the same five customer questions by email. Manually copying orders from one system to another. These are real answers I've gotten.

That's the audit. Not thirty slides. Thirty minutes and one question.

---

**[The conversation flow]**

Once they name the problem, you don't jump to solution. You ask one more question.

"How long does that take each week, total?"

Let's say they say four hours. You do the math out loud. Four hours per week is 200 hours per year. If an employee's time is worth $20 per hour, that's $4,000 per year on a task that can be automated.

Now you're speaking business, not tech.

The pitch is: I can build you a system that handles this automatically, for a one-time fee between $500 and $2,000 depending on complexity, and it runs without anyone touching it.

---

**[What they respond to vs. what they don't]**

What doesn't work: leading with the technology. Do not say "I'll use n8n and connect it to your CRM via webhook." That ends the conversation.

What works: leading with time saved and errors eliminated. "You'll stop manually copying orders. The system catches it automatically. Your team can focus on the parts that actually need them."

That's the frame. Time, errors, focus.

---

**[The tools]**

What's actually running under the hood: n8n for workflow orchestration, Claude API for any response generation, Python for custom logic when n8n's built-in nodes aren't enough.

Most local business automations I've built don't need anything exotic. The complexity is in the integration, not the AI.

An n8n workflow that watches a Gmail inbox, classifies incoming customer questions, and routes them to the right folder takes about two hours to build. The client perceives this as magic.

---

**[Pricing]**

$500 is the floor for a single-integration automation. Something like: new order in Shopify triggers a WhatsApp confirmation to the customer.

$1,500 to $2,000 is where it goes when there are multiple systems involved, custom logic, or ongoing data processing.

The case study that closes deals: a local services business I showed how to automate customer inquiry responses. Before: someone spent 45 minutes per day replying to the same five questions via WhatsApp. After: an n8n flow reads the message, classifies it, and sends a pre-approved response instantly. That took me three hours to build. They paid $800.

They referred me two more clients within a month.

---

**[Closing]**

The pitch works because it's honest. You're not promising a full AI transformation. You're promising to fix one specific thing that wastes their time.

Start with one automation per client. Build it. Make it work. Then ask what else is annoying them.

That's the business model.

---

**Word count: ~590**

---

---

## Script 2: "Building AI Agents for Non-Technical Clients"

**[HOOK — first 15 seconds]**

The hardest part of building an AI agent for a client isn't the build. It's the demo.

Show the wrong thing and you lose them. Show the right thing and they'll tell their entire network.

Here's what the right thing looks like.

---

**[SCRIPT]**

There's a gap in every client conversation about AI, and if you don't close it yourself, the project dies.

The gap is this: you're thinking about nodes, API calls, and memory management. They're thinking about whether this is going to embarrass them in front of a customer.

That's not a tech gap. That's a trust gap.

---

**[What clients understand]**

Small business owners don't think in terms of AI agents. They think in terms of employees.

When I explain what I'm building, I use one phrase: "It's like hiring a part-time employee who only does one job and never makes the same mistake twice."

That's it. That's the whole pitch.

They understand the analogy immediately because they've hired unreliable people. They understand the value of consistent, predictable work. An AI agent that handles customer inquiry routing is not a technical curiosity. It's a reliable team member they don't have to manage.

---

**[How to demo without confusing people]**

The demo should take five minutes. No terminal windows. No JSON. No "let me just explain what's happening here."

What they should see: a message comes in, something happens, the right person gets notified or the right response goes out. That's the whole demo.

I use a WhatsApp or email test from my phone. I send a message. I turn the laptop toward them. They watch the response arrive in under ten seconds.

That's the close.

If they ask how it works, you say: "It reads the message, figures out what category it falls into, and sends the right response. The rules are ones we set together."

That last part matters. "We set together." It makes them feel in control.

---

**[The installation and handoff process]**

Building the agent is maybe 20% of the work. The other 80% is setup, testing with their real data, and the handoff conversation.

The handoff conversation covers three things.

First: what it does and what it doesn't do. Be explicit. "This handles X. It does not handle Y. If Y happens, it flags a human."

Second: how to update it. Most clients will want to change a response or add a new rule eventually. Show them where that lives. Ideally, it's a simple document or spreadsheet they control, not code.

Third: what to do when something goes wrong. Give them a direct line to you. They will call. Build that expectation in.

---

**[The ongoing support model]**

I charge a flat monthly fee for what I call "agent maintenance." It's small: $100 to $200 per month. What it covers: checking that the integrations are still running, updating any API keys that expire, and one small adjustment per month.

Most months, nothing breaks. The fee is for the peace of mind, not the hours.

The honest reason to offer maintenance: it keeps you close to the client. You hear about new problems. You get referrals from a relationship, not from cold outreach.

---

**[Closing]**

Non-technical clients don't need to understand how the agent works. They need to trust that it will work.

Build that trust through the demo. Maintain it through the handoff. Extend it through the relationship.

The technology is almost incidental at that point.

---

**Word count: ~575**

---

---

## Script 3: "The 3 Automations Every Small Business Needs First"

**[HOOK — first 15 seconds]**

Three automations. That's the whole list.

Not a hundred AI tools. Not a complete digital transformation. Three specific systems that cover the problems almost every small business has, and none of them require a technical co-founder.

Let me walk through each one.

---

**[SCRIPT]**

After building automations for several local businesses, I started noticing a pattern. The same three problems kept showing up, independent of industry.

Customer questions that nobody was answering fast enough. Appointment bookings that were being handled manually. Inventory or order status that nobody was tracking in real time.

These three problems waste real hours every week. They're also the easiest automations to build and the easiest to sell.

---

**[Automation 1: Customer Inquiry Response]**

The problem: a business gets 15 to 30 messages per day via WhatsApp, Instagram DMs, or email. Most are the same five questions. Hours get lost.

The solution: a triage bot that reads incoming messages, classifies the intent, and sends a relevant response from a pre-approved template library. Complex or urgent questions get flagged for a human.

Tech stack: n8n for the orchestration, Claude API for classification and response generation, WhatsApp Business API or Gmail depending on the channel.

Time to build: 3 to 5 hours for a basic version. 8 to 10 hours if they have multiple channels.

Cost to client: $800 to $1,200 for a single channel.

What they gain: on average, 45 minutes to 2 hours per day back. Response times go from hours to seconds.

---

**[Automation 2: Appointment Booking]**

The problem: appointment-based businesses, clinics, salons, consultants, spend significant time going back and forth to schedule. "Are you free Thursday? What about Friday?" That conversation is expensive.

The solution: a calendar integration that shows real availability, handles booking confirmations, and sends reminders automatically.

Tech stack: n8n connected to Google Calendar or Calendly, with a simple booking link embedded wherever the business already talks to customers. Automatic confirmation message via WhatsApp or email. Reminder 24 hours before.

Time to build: 2 to 4 hours depending on their existing calendar setup.

Cost to client: $500 to $800.

What they gain: zero scheduling back-and-forth. No-show rates drop because of the reminder. Booking happens while they sleep.

---

**[Automation 3: Inventory and Order Tracking Alerts]**

The problem: small businesses that carry physical product either over-order because they're nervous, or run out because nobody was watching the numbers. Both cost money.

The solution: an alert system that monitors inventory levels and sends a notification when something hits a threshold you define. If you carry 20 units of something and drop below 5, you get a WhatsApp or Telegram message immediately.

Tech stack: depends on where they track inventory. If it's a spreadsheet, n8n has a Google Sheets node that runs on a schedule. If it's Shopify or WooCommerce, those have native webhooks. Python handles any custom calculation logic.

Time to build: 2 to 6 hours depending on the data source.

Cost to client: $600 to $1,000.

What they gain: they stop running out of things. They stop over-ordering things. The system does the watching.

---

**[Why start here]**

These three automations work because they solve problems the business owner can feel. They're not abstract. They're not "AI strategy." They're: customers get answered faster, appointments get booked without friction, stock levels stay visible.

Each one is self-contained. Each one has a clear before and after. Each one is easy to demo.

Build all three for one client and you have a portfolio. A real one, with real outcomes, that closes the next five conversations.

---

**[Closing]**

Start with whichever of the three problems your first client mentions first. Build it. Document it. Then go back in a month and show them what else is possible.

That's the pattern.

---

**Word count: ~610**
