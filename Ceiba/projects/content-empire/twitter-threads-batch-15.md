---
title: "Twitter Threads Batch 15"
type: content
tags: [twitter, threads, finance, systems, builder, ebay, latam]
created: 2026-03-22
batch: 15
---

# Twitter Threads Batch 15
# Topics: Budget Tools, 3-Computer System, eBay Research, Why Builders Don't Ship, Spanish Market

---

## Thread 1: The Budget Tool Nobody Builds

**Tweet 1 (opener)**
90% of budget templates fail by week two.

Not because people lack discipline. Because the template was built wrong from the start.

Here's what actually makes budgeting work, and what I built that's different.

---

**Tweet 2**
The standard budget template has three problems.

It requires daily manual entry. It lives inside a subscription app. And it treats every dollar the same.

None of these are how real spending actually works.

---

**Tweet 3**
The subscription app problem is real.

You start paying $8/mo for a tool that was supposed to save you money. Then you feel guilty about canceling. Then you stop using it but keep paying.

That's the opposite of what you needed.

---

**Tweet 4**
The daily entry problem is worse.

Most people skip a day. Then two. Then they open the app two weeks later, face a backlog, and close it again.

The system failed before the month ended.

---

**Tweet 5**
Here's what I built instead.

One spreadsheet. Works in Excel and Google Sheets. One-time setup, maybe 40 minutes. No subscription. No app. Runs on any device with a browser.

You enter data once a week, not every day.

---

**Tweet 6**
The weekly entry model changes everything.

Sunday. Open the sheet. Enter the week. Takes 8 minutes. Close it.

That's a sustainable habit. Daily entry is not.

---

**Tweet 7**
The sheet has three zones.

Fixed costs (rent, subscriptions, insurance). Variable costs (food, gas, impulse). And a category I call "drift" — the money that disappears without a clear category.

Most people have no idea how much drift they have. It's usually the number that breaks the budget.

---

**Tweet 8**
Here's the math that changes the mindset.

If your drift is $200/month, that's $2,400/year. Not invested, not saved. Just gone.

Tracking it doesn't create discipline. Seeing the number does.

---

**Tweet 9**
The spreadsheet also has a rolling average view.

Not just this month. The last 6 months averaged. That number is your real baseline, not your ideal budget.

Most templates plan against an ideal. Mine plans against reality.

---

**Tweet 10**
What changes when you use it for 90 days.

Month 1: you see the drift number. Month 2: you start catching it in real time. Month 3: your actual spending patterns shift without forcing it.

The tool doesn't motivate you. The data does.

---

**Tweet 11**
The reason nobody builds this tool is that it doesn't monetize well.

No subscription. No upsell. No gamification layer. Just a spreadsheet that works.

That's why it doesn't exist on the app store. That's also why I built it.

---

**Tweet 12 (closer)**
The budget template is free.

Works in Sheets or Excel. One-time setup. No account required.

Link in bio. If you use it, tell me what your drift number is.

---

---

## Thread 2: Running 3 Computers as One System

**Tweet 1 (opener)**
Three computers. One network. Zero monthly AI costs.

Most people pay $400+ a month for the same capability I run locally. Here's how the setup works.

---

**Tweet 2**
The three machines are named Ceiba, Cobo, and Hutia.

Names from Taino cosmology, because the island I'm from has a better naming convention than "MacBook Pro 1" and "Gaming PC."

Each machine has a different job.

---

**Tweet 3**
Ceiba is an M4 MacBook. 16GB unified memory. This is the primary workstation. It runs Claude via API, handles writing, planning, and all the work that benefits from a fast display and good keyboard.

It's also the brain of the network.

---

**Tweet 4**
Cobo is a Windows desktop with a GTX 1080 Ti. 11GB VRAM. This machine's job is GPU work.

Local image generation. Video processing. Fine-tuning small models. Things that would cost $0.50-$2.00 per run on cloud infrastructure, Cobo does for free.

---

**Tweet 5**
Hutia is dedicated to Ceiba. It's the file server and memory layer for the whole system.

Syncthing runs on all three machines. Any file saved on one machine is available on all three within seconds. No Dropbox. No iCloud. No data leaving the house.

---

**Tweet 6**
The AI stack on this network costs $0/month.

Ollama runs on Cobo. Models available: Mistral, Llama 3, Phi-3, Qwen. Any of the three machines can send a request to Cobo and get a local AI response.

The only paid AI in the stack is Claude, via API. Maybe $12-18/month depending on usage.

---

**Tweet 7**
What $400+/month in cloud AI looks like as a comparison.

Midjourney Pro: $60/mo. ChatGPT Plus: $20/mo. Claude Pro: $20/mo. Runway Gen-3: $95/mo. Stability AI API usage: ~$80/mo at moderate volume. ElevenLabs Creator: $22/mo.

I run equivalent capability. Locally. For near zero.

---

**Tweet 8**
The part that actually breaks.

Networking. When Cobo sleeps, the Ollama server goes down. I've fixed this three times with different sleep settings.

Also: Windows updates restart the machine. The server doesn't auto-restart after a reboot without a startup script.

Those two things account for 90% of issues.

---

**Tweet 9**
The startup script fix is simple.

A `.bat` file in the Windows startup folder that launches the Ollama server and sets sleep to "never." Three lines. Fixed the problem permanently.

Most local AI setup problems are fixable in under 20 minutes if you know where to look.

---

**Tweet 10**
Why local AI matters beyond the cost.

Your prompts don't leave your house. Your project files don't train anyone's future model. Your API keys don't sit on a server in Virginia.

For anyone building real products, that matters more than the cost.

---

**Tweet 11**
The real benefit is iteration speed.

When I test a new prompt pattern, I run it against the local model first. Free, instant, private. Once it works, I move to Claude for the final pass.

That workflow cut my API spend by 60% without cutting quality.

---

**Tweet 12 (closer)**
The three-computer AI setup isn't about being cheap.

It's about owning your infrastructure. Not renting it from five different companies month to month.

The full setup guide is in the AI Employee Guide. Link in bio.

---

---

## Thread 3: The eBay Research System

**Tweet 1 (opener)**
Finding a product that sells on eBay is not about trend-chasing.

It's about finding the overlap between demand that already exists and supply that's inconsistent.

Here's the research system, step by step.

---

**Tweet 2**
Most people start eBay research by searching "what sells on eBay."

That's already too late. Those products are saturated. The margin is gone. The search results are full of people who found out the same way you did.

Start somewhere else.

---

**Tweet 3**
Start with completed listings, not active ones.

Active listings show you what people are trying to sell. Completed listings show you what people actually bought.

Filter by "sold" on eBay search. That's the only data that matters.

---

**Tweet 4**
The three numbers I check for every product.

Sell-through rate: what percentage of listings actually sold. Velocity: how many units moved in 30 days. Competition score: how many active sellers for the same item.

If sell-through is below 40%, skip it.

---

**Tweet 5**
What good numbers look like in practice.

Sell-through: 60%+. Velocity: 15+ units in 30 days. Competition: under 30 active sellers. Margin after fees and COGS: 30%+ minimum.

Find all four. That's a real product.

---

**Tweet 6**
The overnight pipeline approach.

I don't research products manually one by one. I run a script that pulls eBay sold data across a category, scores every product against those four metrics, and outputs a ranked list by morning.

That's the research system. It runs while I sleep.

---

**Tweet 7**
The niche sniper is the part people underestimate.

The real money on eBay is not in popular categories. It's in subcategories one level deeper than where most people look.

Not "electronics." Not "cameras." "35mm film cameras under $80 with a working shutter."

---

**Tweet 8**
Why specific niches beat broad categories every time.

Less competition. More committed buyers. Less price war. Buyers in specific niches often pay above market because they've been searching for a while.

The more specific the search, the more motivated the buyer.

---

**Tweet 9**
The common mistakes I see from people starting out.

Buying inventory before validating the sell-through rate. Ignoring shipping weight (kills margin fast). Listing at market price instead of slightly below the median sold price.

All three are fixable with one week of data.

---

**Tweet 10**
What the first 30 days should look like.

Week 1: research only. No buying. Run the metrics on 20 products. Week 2: buy one unit each of your top 3 products. Week 3: list and photograph. Week 4: analyze results.

No investment over $150 total in month one.

---

**Tweet 11**
The connection between eBay research and the Shopify store.

Everything I test on eBay feeds my product list for Shopify. eBay proves the demand. Shopify scales what works.

eBay is the research arm. Shopify is the catalog.

---

**Tweet 12 (closer)**
The research pipeline is documented in the product research guide.

Metrics, script, niche scoring framework. Built for people who want a system, not a shortcut.

Link in bio.

---

---

## Thread 4: Why Most Builders Don't Ship

**Tweet 1 (opener)**
Smart people with good ideas don't finish things.

This is not a discipline problem. It's a systems problem. And the failure modes are specific, repeatable, and fixable.

Here's what I've noticed, and what actually works.

---

**Tweet 2**
Failure mode 1: scope creep at the start.

You have an idea for a simple tool. Within 48 hours, it has three features it didn't need, a landing page you haven't designed, and a pricing model you haven't decided.

You haven't written a line of code yet.

---

**Tweet 3**
Scope creep isn't a planning failure. It's an excitement response.

The idea feels good. You want it to be more. Every new feature you add to the mental model extends the high before you have to actually build anything.

The building is where the idea meets friction. So you keep planning instead.

---

**Tweet 4**
Failure mode 2: perfectionism is not about standards.

It's about avoiding judgment. A finished product can be criticized. An unfinished product is safe because it still has potential.

If you've said "I just need to polish it a bit more" for longer than two weeks, perfectionism is the actual problem.

---

**Tweet 5**
Failure mode 3: waiting for someone else's approval.

This one is subtle. It looks like seeking feedback. But the tell is timing: you seek the feedback before you've done the hard part, not after.

You're not asking "is this good?" You're asking "is it okay to build this?"

Nobody can answer that for you.

---

**Tweet 6**
What I actually do to finish things.

First: define the smallest version that would prove the idea works. Not the full product. The proof of concept. Ship that first.

The proof of concept takes two days, not two months.

---

**Tweet 7**
Second: set a one-week hard deadline.

Not a soft "I'd like to have this done by Friday." A hard deadline with a consequence.

The consequence I use: if it's not shipped by the deadline, the project goes to the backlog for 30 days. No exceptions.

That makes the deadline real.

---

**Tweet 8**
Third: reduce dependencies to zero.

If the project requires someone else to do something before you can proceed, it will stall. Every external dependency is a potential infinite pause.

Build the version that only requires you.

---

**Tweet 9**
Fourth: separate the building session from the planning session.

Planning and building feel similar but they are not the same brain state. If you let them mix, you end up planning when you should be building.

Schedule them as separate blocks. Different days if possible.

---

**Tweet 10**
The thing about accountability that most people get wrong.

Public accountability posts ("I'm building X in public, follow along") often make it worse. The engagement from the announcement replaces the satisfaction you should be getting from shipping.

Keep it private until it's done.

---

**Tweet 11**
The hardest shift.

Shipping something imperfect on time is worth more than shipping something perfect late. Not because imperfect is fine. Because the feedback you get from a live product is worth more than the month you spent polishing in private.

The market teaches you more than your own judgment.

---

**Tweet 12 (closer)**
The builders I respect most share one trait.

They have a graveyard of small shipped things, not a portfolio of polished concepts.

Every shipped thing taught them something. The unshipped ones taught them nothing.

---

---

## Thread 5: The Spanish Market Nobody Is Teaching

**Tweet 1 (opener)**
680 million people speak Spanish as a first language.

Almost none of them have access to AI education that isn't a translation of English content.

That gap is the business.

---

**Tweet 2**
Here's what the LATAM AI education market actually looks like.

Most AI content in Spanish is either: translated from English with no cultural context, produced by academics for academics, or three years behind the current tools.

There is almost no builder-to-builder AI education in Spanish.

---

**Tweet 3**
The English AI education market is saturated.

Hundreds of creators. Similar formats. Similar advice. The competition is real and the audience is fragmented.

The Spanish market has maybe a dozen serious creators. Most of them are focused on ChatGPT tutorials, not systems thinking or builder content.

---

**Tweet 4**
Why this gap exists.

Most AI builders are English-first. They build for the audience they're part of. The LATAM market requires cultural knowledge that most English-first creators don't have.

You can't just translate. The examples have to land. The context has to be real.

---

**Tweet 5**
Building from Puerto Rico is a specific advantage.

The island sits between the US tech ecosystem and the Latin American one. English-fluent enough to access the best tools first. Spanish-native enough to explain them to 680 million people clearly.

That's not a small edge.

---

**Tweet 6**
What building for that audience looks like in practice.

Content that assumes the reader is intelligent but not yet technical. Examples from real business contexts, not hypothetical startups. Prices and tools that work on a LATAM budget.

Not just "here's ChatGPT" but "here's how you actually use it if your country doesn't have Stripe."

---

**Tweet 7**
The bilingual content pipeline is the actual infrastructure.

One idea. Two versions. The English version goes to @behikeai on Instagram and X. The Spanish version goes to a parallel feed.

Same insight, different framing. Not translation, adaptation.

---

**Tweet 8**
The adaptation distinction matters.

A translated post says "AI can help you write better emails."

An adapted post says "Si eres freelancer en México y tus clientes no responden correos, esto es lo que yo uso."

Same tool. Completely different resonance.

---

**Tweet 9**
The product gap is just as real.

Most AI education products are priced in USD for a USD audience. A $97 guide is a week's income in parts of LATAM.

The products I'm building are priced for that reality. Not charity pricing. Smart market-entry pricing.

---

**Tweet 10**
Three channels nobody is owning right now.

Spanish-language AI YouTube with actual depth (not tutorials, systems). A newsletter for LATAM freelancers using AI to compete with agencies. A product line priced for purchasing power parity, not US income assumptions.

All three are wide open.

---

**Tweet 11**
The timing is right for exactly one reason.

The gap won't last. In 18-24 months, the major English AI creators will hire Spanish-speaking teams and localize their content. The window to build first-mover brand recognition is now.

After that, it's competing with budgets you can't match.

---

**Tweet 12 (closer)**
The entire Behike brand is built on this thesis.

AI education, in Spanish and English, from Puerto Rico, for builders who don't have a Silicon Valley safety net.

That's the market. That's the moat. That's why it's worth building now.

---
