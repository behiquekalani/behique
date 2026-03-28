---
title: "Newsletter Issues 23-25"
type: content
tags: [newsletter, email, automation, adhd, gumroad, n8n, productivity, digital-products]
created: 2026-03-22
updated: 2026-03-22
---

# The Behike Brief — Issues 23–25

---

## Issue 23: Why Most Automation Fails (And What Actually Works)

*The Behike Brief | Week 23*

---

### Opening

I spent two months building automations that did not save me any time. I connected APIs, built multi-step workflows, added conditionals and error handlers. Then I realized the automations were solving problems I had invented. The real bottleneck was still me, sitting at the computer, making decisions that no workflow could make for me.

That is the first failure mode. You automate the wrong things.

---

### Main Topic: The 80/20 of Automation

Most people approach automation backwards. They see a YouTube video about Zapier, get excited about connecting 12 apps, and spend a weekend building a system that breaks two weeks later. The problem is not the tool. The problem is the thinking.

Automation only works when you have a repeatable process. If the task requires judgment every time you do it, you cannot automate it yet. You need to do the task manually enough times to understand exactly what is happening. Then you automate the repetitive part.

Here is the 80/20 that actually matters.

**What to automate first:**

The highest-ROI automations are the ones you hate doing most. Not the ones that look impressive. The ones that make you procrastinate. For me, that was content distribution. Writing a post once and manually copy-pasting it to Instagram, Threads, and a Notion content log was a 15-minute job I hated. I automated that. Saved maybe 45 minutes a week. Small number, but I actually do it now instead of avoiding it.

The second category is data collection. Any time you are manually checking something on a schedule, that is automatable. Checking product prices on eBay. Checking if a competitor dropped a new post. Checking your Gumroad stats. These are pull-based tasks. You can automate the pull and get a summary delivered to you instead.

The third category is notifications and routing. If you get an email and then manually forward it, copy it to a doc, or tag it somewhere, that chain is a workflow. Build it once.

**What not to automate first:**

Do not automate anything you have done fewer than 10 times manually. You do not understand the edge cases yet. Every automation I built too early had to be rebuilt after I discovered the exceptions. An automation that breaks mid-process is worse than doing it manually because now you have incomplete data and a debugging task on top of the original work.

Do not automate your thinking. I see people building AI workflows that generate 50 content ideas a day and pipe them straight into a publishing queue. The content is always generic because the AI was given no context. The output is noise. Automation cannot replace the 10 minutes you spend deciding what is actually worth saying.

**Common failure modes:**

The first is over-engineering. You add retry logic, error handling, Slack notifications when something fails, logging to a Google Sheet. The workflow has 40 steps and breaks every time an API updates. Start with the simplest version that works. Add complexity only when the simple version fails repeatedly.

The second is forgetting maintenance. Automations are not set-and-forget. APIs change. Credentials expire. Rate limits hit. Budget 30 minutes a week just to check that your automations are still running. I use a simple n8n workflow that pings itself every Monday and sends me a status message. If I do not get the message, something is down.

The third is automating a broken process. If your content publishing workflow is disorganized manually, building an n8n workflow around it will not fix it. It will make the mess run faster. Fix the process first. Then automate.

**What actually works:**

Automate the last mile. The stuff that is 80% done but requires a final repetitive step. Automate data collection. Automate notifications. Automate distribution of things you have already created. Leave the judgment, the creation, and the strategy to yourself.

Real numbers from my setup: I run 7 active workflows. Three of them I use every day. Two I use weekly. Two I forgot about and should probably delete. That is a typical ratio. Most people with 20 workflows are actually using 4.

**The one automation every solo creator should build first:**

A webhook that fires when you finish a piece of content and sends it to every distribution channel at once. Set it up in n8n. Connect your Notion or Obsidian writing environment as the trigger. Connect Instagram, your email list, and a content archive as the outputs. That single workflow will save you more time than any other automation you build.

---

### Tool Spotlight: n8n

n8n is a workflow automation tool that sits between Zapier and writing your own scripts. You get a visual interface with nodes, but you also have access to actual JavaScript inside any node. That distinction matters more than it sounds.

The honest comparison to Zapier: n8n has a steeper learning curve but a much higher ceiling. Zapier is faster to set up for simple two-step workflows. n8n is better for anything complex, anything that involves loops, conditionals, or custom logic.

The self-hosted version is free. You run it on your own server or locally. The cloud version starts at around $20/month for higher execution counts.

What I actually like: the code nodes. When an API returns something unexpected, I can write three lines of JavaScript to transform it instead of hunting for a Zapier formatter that almost does what I want. The HTTP request node handles most APIs without needing a dedicated integration. I have connected things to n8n that Zapier does not support at all.

What I do not like: the error messages are cryptic when something breaks. Debugging a failed workflow requires you to understand how n8n processes data, which takes a few hours to learn. The documentation is improving but still has gaps. The UI gets visually cluttered on complex workflows.

One thing worth knowing: n8n's community template library has over 900 pre-built workflows. Before you build anything from scratch, check there first. At least 60% of what you want already exists.

Verdict: worth learning if you plan to build more than 5 workflows. For one or two simple automations, Zapier is faster to set up and maintain.

---

### What I Built This Week

I finished an n8n automation pack with 4 workflows: content distribution on publish, daily eBay product research summary, Gumroad sale notification to Telegram, and a weekly review reminder. The product research workflow alone is saving me 30 minutes of manual eBay searching daily. The whole pack is available in the store for people who want to skip the learning curve and start from working templates.

---

### One Link Worth Your Time

**n8n's official template library** at n8n.io/workflows. Browse 900-plus community-built workflows before building from scratch. Most of what you need is already there, built by people who hit the same edge cases you will.

---

### Closing

Automation is not a productivity hack. It is a discipline. Build it right or do not build it at all. The goal is fewer decisions, not more systems. One workflow that runs cleanly every day is worth more than ten that break when you are too busy to fix them.

---

---

## Issue 24: The Case for Selling Cheap Products First

*The Behike Brief | Week 24*

---

### Opening

The most common advice for digital product creators is to build a $997 course. Position yourself as an expert. Price high to signal value. I tried this mental model for a while and nothing happened. Then I put a $4.99 guide on Gumroad and got 12 sales in the first week without spending a dollar on ads.

The cheap product is not the end goal. It is the beginning of the relationship.

---

### Main Topic: Why Low-Price Products Build Trust Faster

There is a real psychological difference between a $4.99 purchase and a $99 purchase. The $4.99 decision takes about 4 seconds. The $99 decision requires trust you probably have not earned yet. If someone does not know you, they will not pay $99 for your PDF. But they will pay $4.99 to see if you know what you are talking about.

That first purchase is not about revenue. It is about proof.

**The trust ladder:**

Think of it as a sequence. Someone finds you online. They read something free. They see a $4.99 product that solves one specific problem they have right now. They buy it. You over-deliver. Now they trust you. Three weeks later they buy the $27 product. Two months later they are in the $97 bundle.

The $4.99 product is the top of the funnel, not the bottom. If you skip straight to a $99 course, you are asking for trust before you have earned it. Most cold traffic will not take that bet on a creator they do not know.

**What works at the $4.99 to $9.99 price point:**

The products that convert at this range solve one specific problem. Not a general problem. One. The person reads the title and thinks, "I need exactly that right now."

Good examples: a checklist for launching your first Gumroad product. A prompt template pack for writing landing pages. A one-page spreadsheet for tracking eBay margins. A 10-step guide for setting up an n8n workflow from scratch.

Bad examples: "The Complete Guide to Building a Digital Business." That is a $99 product framing on a $4.99 price point. It does not convert because it sounds unfocused. Buyers cannot identify the specific problem it solves for them.

The format matters less than the specificity. A 5-page PDF beats a 40-page PDF if the 5 pages solve the exact problem the customer has right now. People are not paying for volume. They are paying for the answer.

**Gumroad conversion data I actually look at:**

Gumroad shows you views, conversions, and revenue. The number that matters most is conversion rate. Not total views.

A product with 200 views and 20 sales is a 10% conversion rate. That is a winner. A product with 2,000 views and 10 sales is 0.5%. That has a title or description problem. The traffic is there. The product is not connecting. Those are two completely different problems to fix.

For $4.99 products, a healthy conversion rate is 5 to 15%. Below 3% means the title is not matching what people searched for, or the preview page is not showing enough value. Above 15% means you could probably raise the price.

The second metric worth watching is average rating. Gumroad lets buyers leave ratings. A product with 4.8 stars and 20 reviews is a passive sales engine. Every new visitor sees social proof from real buyers before they decide. Build toward that first.

**The volume math:**

At $4.99 per product with a roughly 70% margin after Gumroad's cut, you need 2,850 sales to hit $10,000 in revenue from that one product. That sounds like a lot. At $9.99, you need 1,430. These are not per-month targets. These are cumulative totals that compound over time across a growing catalog.

Most creators have one product. The real play is 10 to 15 products in the $4.99 to $19.99 range, all pointing at each other. A buyer of product one sees product two on the thank-you page. The catalog does the upselling. You do not have to pitch anyone individually.

**One thing most creators skip:**

The follow-up email. Gumroad lets you message your buyers. Most people never use it. Send one email three days after purchase. Ask if they have a question about the product. Mention one other product that solves the next problem they will probably have. That single email, sent to real buyers who already trust you, regularly adds 15 to 20% to total revenue without any new traffic.

---

### Tool Spotlight: Gumroad Analytics

Gumroad's analytics dashboard is minimal but has everything you need to make decisions at early stage. The main view shows sales, views, and revenue over time with a simple line chart. You can filter by product, which is where the useful data lives.

What I actually use: the individual product stats page. It shows visits, conversions, and a referrer breakdown. That last one tells you where traffic is coming from. If 80% of your sales come from one source, you know what to double down on instead of spreading effort across everything.

The honest limitation: Gumroad does not show time-on-page or scroll depth. You cannot tell if people are reading your product description or bouncing immediately after arriving. For that level of detail you would need an external analytics tool, which Gumroad does not make easy to connect.

The built-in email tool is basic. You can message all buyers of a specific product. No segmentation beyond that. For a small catalog it is enough. When you have more than 500 buyers across 20 products, you will want a dedicated email tool like ConvertKit or Resend.

Verdict: the analytics are adequate for decisions at early stage. Do not let the simplicity fool you into thinking you need more data. At under 1,000 sales, the Gumroad dashboard tells you everything you need to act on.

---

### What I Built This Week

I finished one of the low-price digital product guides in the catalog. It is a step-by-step Gumroad setup guide for someone launching their first product. The PDF is 11 pages. Every page covers one action with no filler. I kept it specific because that is the kind of product I wished existed when I was setting up my own store. Total time to build: about 4 hours including the cover design in Canva and writing the description.

---

### One Link Worth Your Time

"1,000 True Fans" by Kevin Kelly at kk.org/thetechnium/1000-true-fans. Written in 2008 and still the clearest explanation of why you do not need a massive audience to earn a living. The math works for digital products at almost any price point. Do the calculation for your own catalog.

---

### Closing

Nobody builds trust through a cold $99 pitch. Start with the $4.99 product. Solve one real problem well. Let the catalog grow. The higher-ticket offer comes later, after the person already knows you deliver what you promise.

---

---

## Issue 25: ADHD and Productivity: What the Research Actually Says

*The Behike Brief | Week 25*

---

### Opening

I was diagnosed with ADHD as an adult. For a long time I used it as an explanation for why certain systems did not work for me. Then I started reading the actual research instead of productivity blog posts. The research is different from what most people think. Some of the most popular ADHD productivity advice has no evidence behind it. Some things that actually work are almost never mentioned.

This is what I found.

---

### Main Topic: ADHD Productivity, Separated from Myth

ADHD is a dysregulation of dopamine and norepinephrine in the prefrontal cortex. The prefrontal cortex handles executive function: planning, working memory, impulse control, and time perception. When those systems are dysregulated, standard productivity advice often fails because it assumes consistent access to those functions. People with ADHD do not have that consistency.

This is not a character flaw. It is a physiological difference. That matters because it changes how you approach fixing it.

**What the research actually supports:**

The clearest evidence is for external structure. People with ADHD perform significantly better when structure comes from outside rather than from internal motivation. This is why a coffee shop or library works better than your bedroom. Why working on video call with a friend works better than working alone at home. The external environment provides the structure your brain does not generate on demand.

A 2020 meta-analysis in the Journal of Attention Disorders found that body doubling, meaning working in the presence of another person even without any direct interaction, improved task completion rates by 20 to 30% for adults with ADHD. That effect size is larger than most of the supplements people spend money on.

The second evidence-backed approach is implementation intentions. Instead of "I will work on my product today," you write: "At 10am, when I sit down at my desk, I will open the product document and write 200 words." Specific time, specific trigger, specific action. A 1999 study by Peter Gollwitzer found that implementation intentions increased follow-through by 200 to 300% in general populations. For ADHD populations the effect is at least as strong because the specificity removes the decision load at the moment of action.

The third is task decomposition pushed to the point of zero ambiguity. Not "work on the guide." Every subtask has to be so small that when you sit down there is no decision to make. Open the document. Copy this paragraph. Write the next bullet point. That level of granularity. If the next action requires any judgment about what to do, you will not do it when activation energy is low.

**What the research does not support:**

The morning productivity journal. This gets recommended constantly. "Write down your three priorities every morning." For most people with ADHD, the journal becomes a guilt document. You fill it in, feel good for 20 minutes, then forget about it entirely by 11am. The research on journaling as a standalone productivity tool for ADHD is weak. It may help some people, but it should not be the foundation of your system.

Multitasking or "context switching strategies." ADHD does not mean you are good at switching between tasks. The research consistently shows the opposite. People with ADHD incur higher cognitive costs from each task switch and take longer to fully re-engage with a task after interruption. Single-focus work sessions with hard stop times outperform juggling multiple tracks.

The 25-minute Pomodoro timer as a universal prescription. The original Pomodoro technique has modest research support for general populations. For ADHD specifically, 25 minutes is often too short to reach the hyperfocus state where you do your best work. Some evidence suggests 50-minute blocks with 15-minute breaks work better for people who can reach hyperfocus. Others do better with 15-minute blocks. The point is to experiment with your own timer rather than defaulting to 25 because that is the well-known number.

**What actually works in practice:**

My most productive hours are 9am to 1pm. I protect that window completely. Everything that does not require creative output, writing, or building gets pushed to the afternoon. Email, admin, posting content all happen after 2pm. This is not preference. It is based on noticing where my cognitive quality actually sits throughout the day over several weeks.

I use a physical notepad next to my keyboard for task capture. When a new idea surfaces during a work session, I write it on the pad and keep working. The idea leaves my head without requiring me to stop and act on it. I process the notepad at the end of the day. This is the analog equivalent of BehiqueBot, which does the same thing for voice notes.

I keep the work environment predictable and boring. No music with lyrics during deep work. Minimal browser tabs. Phone in another room. These are not preference choices. They are necessary conditions for output quality. Every sensory input that is not directly related to the work is a potential activation route for the distraction loop.

**The real insight from the research:**

Most productivity systems were built by people without ADHD for people without ADHD. When one of those systems fails, that is information about the system's fit, not your work ethic. Build your own system from the ground up using evidence. Not productivity content. Not YouTube videos. Read the actual studies, run your own experiments, and document what happens.

---

### Tool Spotlight: Brain.fm

Brain.fm is a focus music app built around functional audio, meaning music designed specifically to affect cognitive state rather than simply to be listened to. It uses a technique called neural phase locking, which involves embedding rhythmic patterns into audio that influence brainwave entrainment. The research base is small but growing.

Honest review: I was skeptical for the first few days. After two weeks of using it during focused work sessions, my output quality improved noticeably. Fewer task switches within a session. Less time needed to reach focus state. The improvement is not dramatic but it is consistent, which matters more.

The library has three modes: Focus, Relax, and Sleep. The focus tracks sound like ambient electronic music but with subtle rhythmic structure underneath. It is not lo-fi. It is not coffeehouse jazz. It is specifically designed for function rather than enjoyment.

Pricing is around $7/month or $50/year. There is a free trial with limited daily minutes.

What I do not like: there is almost no customization. You pick a mode and it plays. You cannot skip tracks or build playlists. The randomness is by design, apparently to prevent the brain from habituating to a specific track. Some people like the simplicity. I occasionally want control I cannot have.

Verdict: worth a two-week trial, especially if you have tried lo-fi music and found it distracting. The $7/month cost is low enough that the experiment costs less than a coffee per week.

---

### What I Built This Week

I finished the ADHD Finance guide. It covers money management specifically for the ADHD brain, including automating bills and transfers so they do not require remembering, using savings buckets with named purposes instead of one account, setting alerts instead of relying on manual checking, and building review rituals that take under 10 minutes. The research I did for this newsletter issue fed directly into the product content. That is the content-to-product pipeline working exactly as designed.

---

### One Link Worth Your Time

"Smart but Stuck" by Thomas E. Brown, available on Amazon. Brown is one of the leading ADHD researchers in the US. This book uses case studies of intelligent adults with ADHD who underperformed until they understood the neuroscience behind their specific patterns. Most useful ADHD book I have read, and I have read most of the popular ones.

---

### Closing

ADHD is not an excuse and it is not a superpower. It is a set of conditions that require different strategies than the ones most productivity content teaches. The research exists. Most people with ADHD never read it. They try systems built for neurotypical brains, fail, and conclude they are broken. You are not broken. You have the wrong system. Fix the system.

---
