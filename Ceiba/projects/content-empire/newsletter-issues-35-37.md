---
title: "Newsletter Issues 35-37"
type: content
tags: [newsletter, email, ebay, automation, product-research]
created: 2026-03-22
brand: Behike
voice: Dan Koe meets Robert Greene. Direct. Thesis first. No em dashes, no exclamation marks.
---

# Behike Newsletter — Issues 35-37
# Theme: eBay reselling, overnight automation, product research

---

## ISSUE 35 — "The Pipeline That Runs While I Sleep"

**Subject line:** The machine that runs my eBay store at 3 AM

**Preheader:** Three computers, one workflow, zero manual research.

---

Hey,

Most eBay sellers wake up and open spreadsheets. I wake up and read a report.

The difference is not effort. It is architecture.

---

### The Overnight Machine

My eBay research pipeline runs on three computers. Not because I need three computers, but because each machine has a different job and doing all three jobs on one machine creates bottlenecks.

Ceiba is the brain. It runs the scoring logic, generates product titles, writes listing descriptions, and decides what moves to the shortlist. It is the M4 MacBook, fast at inference, always on.

Cobo is the muscle. It handles the heavy scraping: Google Trends queries, eBay sold listings pulls, Reddit data extraction. It runs a GTX 1080 Ti, which matters for any image processing or local model inference I push to it.

The bridge between them is a task queue. Ceiba puts jobs in. Cobo runs them. Results come back structured.

By the time I wake up, I have a ranked list of product candidates waiting.

---

### What the Nightly Workflow Actually Does

At 11 PM, a scheduled job kicks off on Cobo. It checks five Reddit subreddits I have flagged for demand signals, pulls a week of sold listings for my tracked categories on eBay, cross-references Google Trends to confirm the search interest is growing and not declining, and writes everything to a structured JSON file.

At 7 AM, I read that file over coffee. The products that scored above 60 on my 15-point model are already tagged STRONG BUY. I do not have to think. I have to decide.

That distinction matters. Thinking is slow. Decision-making on pre-processed data is fast.

The whole research process went from 3 hours per day to 15 minutes. The 15 minutes is review and judgment. The 3 hours was the machine's job all along.

---

### Why Most Sellers Skip This

They tell themselves they will automate eventually. When the store grows. When they have more products. When they have more time.

The inversion is true. You build the pipeline first, and then the store grows, because the pipeline finds winners faster than any manual process can.

The pipeline does not require three computers. It requires one computer running a cron job and a scoring spreadsheet you take seriously. Start there.

What I built is a grown version of a cron job and a spreadsheet. The architecture scaled with the operation. But the logic was the same on day one.

---

### What Is Coming Next

Next issue I am breaking down the scoring model itself, all 15 criteria, the thresholds, and the three verdicts the system can return. That is the part most people want to copy and the part most people get wrong.

The score is not just about profit margin. Margin is one of 15. The products that fail are usually disqualified on criteria nobody thinks to ask about until they have a garage full of returns.

Details next week.

Until then,
Kalani
Behike

All products from this pipeline are available at behike.shop

[Unsubscribe]

---

## ISSUE 36 — "How I Score eBay Products Before I List Them"

**Subject line:** The 15 questions I ask before listing any product

**Preheader:** One number tells me GO, TEST, or PASS. Here is how it is calculated.

---

Hey,

There is a moment every dropshipper knows. You find a product, it looks good, you list it, and 60 days later it has zero sales and you have $200 tied up in dead inventory.

The scoring model exists to eliminate that moment before it happens.

---

### The Viral Vault Methodology

Every product I evaluate gets rated across 15 criteria, each scored 1 to 5. Maximum score: 75. The three verdicts:

- 60 or above: STRONG BUY. List it.
- 40 to 59: TEST. Small batch, watch the numbers.
- Below 40: PASS. Do not waste the time.

The number forces honesty. You cannot talk yourself into a bad product when the score says 34.

---

### The 15 Criteria

Here are all 15, with what each one is actually measuring.

**1. Wow Factor.** Does it make people stop scrolling? Would someone share it in a group chat? This is a proxy for organic demand and word-of-mouth potential.

**2. Problem Solving.** "Nice to have" products score 2. "Need this now" products score 5. Pain point products convert faster and return less.

**3. Broad Appeal.** Niche products require niche traffic. Universal products sell to anyone. The score penalizes products that can only appeal to a specific demographic.

**4. Impulse Buy Price.** The $10-20 sweet spot scores 5. Over $50 scores 1. This is about removing friction from the purchase decision. The more someone has to think about the price, the fewer conversions you get.

**5. Hard to Find Locally.** If it is on a Walmart shelf, you cannot compete on convenience. You are competing on price and losing. Online-only products score highest here.

**6. Profit Margin.** Can you achieve a 3x markup? Cost $5, sell $15. Cost $10, sell $30. Thin margins mean one return can erase a week of profit.

**7. Lightweight and Shippable.** Fits in a padded envelope scores 5. Oversized scores 1. Shipping costs kill margins on heavy products faster than sellers expect.

**8. Not Seasonal.** Evergreen products keep money moving in January. Christmas-only products leave you with three dead months. The score rewards consistency over spikes.

**9. Not Fragile.** Silicone, plastic, and fabric score 5. Glass and electronics score 1 to 3. Fragile products generate disputes. Disputes generate negative feedback. Negative feedback kills your seller metrics.

**10. No Brand Dominance.** If Nike or Apple own the category, you are fighting for scraps. Generic or unbranded product categories leave room for a new seller to win.

**11. Visual and Demonstrable.** Can you show this product doing something in 15 seconds? Before and after products score 5. Products that just look like objects in a photo score low. Visual products convert better across every channel.

**12. Low Competition.** Under 100 eBay listings for the exact product scores 5. Over 2,000 scores 1. Competition data is pulled directly from eBay's sold listings search.

**13. Trending Up.** Google Trends confirms whether search interest is growing, flat, or declining. You want to enter a trend early, not at the peak. Sharp uptrend scores 5.

**14. Repeat Purchase.** Consumable or refillable products score 5. One-and-done products score 1. Repeat buyers are worth 3x to 5x a single sale customer over time.

**15. Cross-sell Potential.** Can you bundle accessories with this product? Natural bundling increases average order value without acquiring new customers.

---

### The Decision That Surprises People

Most sellers think margin is the most important criterion. It is one of 15.

The products that fail my model most consistently fail on criteria 7, 8, and 9. Shipping weight they underestimated. Seasonality they ignored. Fragility they discovered too late.

The model does not tell you what to love. It tells you what will cost you money before you spend it.

The tool is free to run yourself. The logic is in my Ecommerce Playbook, which includes the full scoring template and worked examples.

If you want to start evaluating products the same way I do, that is the direct path.

behike.shop

Until next week,
Kalani
Behike

[Unsubscribe]

---

## ISSUE 37 — "Reddit Is Not a Social Network. It Is a Product Research Database."

**Subject line:** I stopped guessing what people want to buy. I started reading Reddit.

**Preheader:** Five subreddits. Specific signals. Real demand data.

---

Hey,

The fundamental problem with product research is not finding products. It is finding demand before the competition does.

Reddit solved that problem for me.

---

### Why Reddit Works Where Other Sources Fail

Every other research method is backward-looking. eBay sold listings tell you what already sold. Google Trends shows you what already trended. Amazon Best Sellers shows you what already won.

Reddit shows you what people want right now, before a product exists to serve them, before a seller has listed it, before the category has 2,000 competitors.

People on Reddit complain, ask for recommendations, and share frustrations with remarkable specificity. "I can't find a good X that does Y without Z being a problem." That sentence is a product brief.

---

### The Five Subreddits I Monitor

These are the ones I check daily through my scraper. Each one surfaces a different type of signal.

**r/BuyItForLife** is where people describe the exact physical and functional properties they want in a product. "I've been through 5 of these. What's the one that lasts?" Every thread is a demand signal with specifications attached. You learn what makes a product worth buying at a premium and what drives the repeat purchase decision.

**r/shutupandtakemymoney** is the impulse buy database. Products that show up here are visual, novel, and priced for immediate purchase. If something gets 10,000 upvotes on this subreddit, there is real demand. The comment section tells you what people wish was different, which is your product improvement angle.

**r/amazonfinds** and **r/EtsyFinds** show you what is converting on other platforms. A product winning on Amazon is not automatically a lost cause on eBay. Price positioning, bundling strategy, and condition variation (new vs. open box) create room to compete.

**r/frugal** surfaces the pain behind the purchase. People in this subreddit explain exactly what problem they are solving and how much they are willing to pay. That is market research that a survey company would charge you thousands to produce.

**r/whatsthisbug, r/homemaintenance, r/DIY** are problem subreddits. People describe a situation and ask for a solution. The solution is often a product. These threads appear before a product category is saturated.

---

### What to Look for in a Thread

Not all Reddit threads are signal. Most are noise. I filter for three patterns.

The first is the frustrated repeat buyer. "I keep buying X and they all break." That person will pay more for a solution that lasts. Your margin is in that frustration.

The second is the widespread agreement comment. When the top comment on a recommendation thread gets hundreds of upvotes saying "yes, this" about a specific product, that is demand validation you did not have to create yourself.

The third is the gap question. "Does anyone make X that also does Y?" If the answer in the thread is no, or "I've been looking for years," that is a product development signal. If a manufacturer has solved it and it simply is not being listed widely on eBay, you have a sourcing opportunity.

---

### How I Automate This

My scraper runs nightly. It queries specific subreddits for posts from the past 7 days, filters for posts with more than 50 upvotes and more than 10 comments, extracts the product nouns from the titles and comment bodies, and cross-references them against my eBay and Google Trends data.

Products that appear in Reddit with strong engagement and low eBay competition get flagged for scoring.

The whole system runs unattended. I review the flagged products in the morning, run them through the 15-point model from last week's issue, and decide which ones move to sourcing.

The research step that used to take hours is now a 10-minute review.

If you want to replicate this without building a scraper first, start manually. Check those five subreddits every morning for 30 days. You will train your eye faster than any tool can train it for you.

The system comes after the understanding. Build the understanding first.

behike.shop

Until next week,
Kalani
Behike

[Unsubscribe]
