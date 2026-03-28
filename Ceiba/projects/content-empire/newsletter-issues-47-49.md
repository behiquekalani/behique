---
title: "Newsletter Issues 47-49 — Services and Agency Content"
type: content
tags: [newsletter, services, consulting, automation, portfolio, local-business]
created: 2026-03-22
issues: [47, 48, 49]
---

# Newsletter Issues 47-49 — Services and Agency Content

---

## Issue 47 — My First Client Pitch

**Subject line:** I almost said nothing. Then I asked one question.

---

There is a pharmacy near where I study. Family-owned. They had a whiteboard on the wall behind the counter with a list of things to restock. Hand-written. Updated whenever someone noticed something was missing.

I had been thinking about automation for weeks. Not in the abstract. Specifically: what was the simplest possible system I could build for a real business, and could I do it well enough that they would pay for it.

I walked in and asked to speak with whoever handled the operations side. The owner came out. I asked him one question: "What is the most repetitive thing your team does every week that does not actually require a human decision?"

He pointed at the whiteboard.

---

The problem was not complicated. Every few days, someone would manually check certain inventory levels, compare them to a handwritten reorder threshold, and then type up a message to the supplier. The whole thing took about an hour per week and was prone to being forgotten when the store got busy.

I told him I could automate that. Track the inventory in a shared spreadsheet, run a check every morning, and send a WhatsApp message to the supplier automatically when anything hit the reorder threshold. No whiteboard. No manual check. No forgotten reorders.

He asked how much. I said $600.

He said yes before I finished the sentence.

---

The build took me about five hours. A Google Sheets setup for inventory levels, an n8n workflow running on a schedule, and a WhatsApp Business API integration for the supplier message. I tested it with fake data for two days before handing it over.

The handoff call was 30 minutes. I showed him where to update the reorder thresholds. I showed him the log where he could see every message the system had sent. I showed him how to pause it if something went wrong.

He asked if I could do anything about the customer inquiry problem they had.

That became the second project.

---

What I learned from that first pitch was specific: the client does not need to understand how it works. He needs to trust that it will work. And trust comes from the conversation before the contract, not from the technical explanation.

I did not explain n8n. I did not say anything about APIs. I said "this saves you an hour a week and eliminates the chance of forgetting to reorder."

That is the whole pitch. Time saved. Error eliminated. Done.

The hardest part of that first conversation was showing up. Everything after that was just following what the problem told me to do.

---

**Word count: ~385 (tight issue, intentional)**

---

---

## Issue 48 — What Local Businesses Actually Need From AI

**Subject line:** Not a language model. Just the hour they keep losing.

---

Something shifts when you start having real conversations with small business owners about AI.

You go in with all this knowledge about what is technically possible. Large language models. Agent pipelines. Multi-step reasoning. Automated workflows that can handle complex decision trees.

And then the owner of a boutique clothing store tells you that what she actually needs is for someone to handle the 30 messages she gets every Monday from people asking if something is back in stock.

That is the gap. Not between AI and non-AI. Between what is technically impressive and what is commercially valuable right now.

---

The businesses I have talked to are not waiting for a sophisticated AI transformation. They are waiting for basic automation they have not gotten around to because they are too busy running the business.

Three examples from actual conversations:

**Inbox triage.** A small accounting firm receives between 40 and 60 emails per day. About 70% of them are clients asking the same five things. Status updates. Document requests. Meeting scheduling. None of these require a CPA to answer. They require a reliable system that can classify, route, or respond automatically. The CPA's time costs $200 per hour. Each email takes three minutes. The math is uncomfortable.

**Calendar booking.** A physiotherapist I spoke with was spending 45 minutes per day going back and forth with patients to schedule appointments. WhatsApp threads. Phone calls. The occasional walk-in who wanted to book for next week. A calendar integration with a booking link, automated confirmation, and a 24-hour reminder would eliminate all of that. She knew this. She just had not had time to set it up.

**Price update notifications.** A small wholesaler who supplies restaurants and cafes manually updates prices in a spreadsheet and then calls or texts each client when prices change. Sometimes weekly. Sometimes more. This is a job for a script that reads the spreadsheet and sends a formatted update to a WhatsApp group. Two hours to build. Currently taking four hours per week of a person's time.

---

None of these are AI in the way the industry talks about AI. None of them require a model that can reason about complex problems.

They require someone who knows how to connect the tools that already exist, configure them correctly, and hand over a system that runs without anyone touching it.

The gap between what is technically possible and what is commercially valuable right now is not about intelligence. It is about reliability and trust.

A business owner does not want the most sophisticated system. They want a system that works every time without surprising them.

That is the product. Build that.

---

The mistake I made early on was showing up with the impressive version. The full pipeline. The AI agent that could handle edge cases and route complex queries.

The owners' eyes glazed over.

The conversation that works is the one that starts with their specific problem and ends with "here is what stops happening and here is what starts happening instead." Specific. Bounded. Reliable.

Start with the unglamorous automations. The inbox triage. The booking link. The price notification. These are the ones that create trust and generate referrals.

The sophisticated builds come later, after you have proven you can be trusted with the simple ones.

---

**Word count: ~545**

---

---

## Issue 49 — Building a Portfolio Before the Clients Arrive

**Subject line:** Three automations for free. Zero clients when I started.

---

Nobody wants to be your first client.

That is not a criticism. It is rational. Hiring someone to build an automated system for your business involves real risk. If the system breaks or behaves unexpectedly, it creates problems that did not exist before. Why would you take that bet on someone with no track record?

You would not. I would not.

The answer is not to wait until someone gives you a chance. The answer is to build before anyone is paying you to.

---

Three months before I charged my first client, I had built three working automations for real businesses. None of them paid me anything.

The first was for a family member's small retail operation. A basic inventory alert system that sent a Telegram message when certain products dropped below a threshold. I built it in a weekend. It ran without issues for six weeks before I showed it to anyone outside the family.

The second was for a neighbor who ran a cleaning service. She was spending time every day texting appointment confirmations and reminders manually. I built an n8n workflow that handled confirmations and sent a 24-hour reminder automatically. The setup call took an hour. The build took an afternoon. She referred me to two other business owners within a month.

The third was for a small tutoring center. They were manually sending end-of-week progress summaries to parents via WhatsApp. I built a template-based system that generated and sent the summaries automatically based on data they entered in a shared spreadsheet.

---

By the time I pitched my first paying client, I had three documented outcomes.

Not course completions. Outcomes. Weeks of runtime. Error logs showing the system working. Referrals from people who had used the systems. Screenshots of the workflows running.

That is a portfolio. And it costs nothing to build except time.

---

How to document it correctly matters as much as building it.

Each project should have a one-page summary that covers four things: the problem, what the system does, how long it has been running, and the specific outcome in measurable terms. Minutes saved per week. Errors eliminated. Messages automated.

Keep it simple. Do not over-design it. A clean PDF or a simple Notion page works. The goal is to show that you built something real for a real business and that it worked reliably.

The portfolio page, when you build one, should show this in the same format for each project. Problem. Solution. Result. Running since.

Three projects with real outcomes is enough to have the first paid conversation. More than that and you are overqualified for the local business market, which is not a problem you have yet.

---

The other thing those three free projects gave me was calibration.

I learned what documentation clients actually need (less than I thought). I learned how long integrations take to set up reliably (longer than I expected). I learned that the handoff conversation is half the work.

None of that knowledge comes from a certification program. It comes from doing the build, watching it run, and fixing the things that break.

Start with the three free builds. Use them as tuition. Then charge.

---

**Word count: ~580**

---
