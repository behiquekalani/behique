# Business Analysis Prompts
## 10 Battle-Tested Prompts for Market Research, Competitor Intel, and Financial Modeling

---

### 1. Market Opportunity Scanner

**When to use:** Before launching a product, entering a new niche, or validating whether an idea is worth building.

**Prompt:**
```
Analyze the market opportunity for [PRODUCT/SERVICE IDEA] in the [INDUSTRY] space.

My constraints:
- Budget: [STARTUP BUDGET]
- Timeline: [WHEN I NEED REVENUE]
- Team size: [SOLO / SMALL TEAM]
- Current audience: [SIZE AND TYPE, or "none yet"]

Provide:
1. Market size estimate (TAM, SAM, SOM with reasoning, not just numbers)
2. Growth trajectory (is this market expanding, stable, or contracting?)
3. Customer segments (who buys this, ranked by willingness to pay)
4. Distribution channels (where do these customers already hang out?)
5. Pricing landscape (what are people paying for similar solutions?)
6. Barrier to entry assessment (what stops me vs. what stops competitors)
7. Timing analysis (why now? What changed that makes this viable?)
8. 3 signals that this market is real (forums, search trends, competitor revenue)
9. 3 risks that could kill this (be honest, not optimistic)
10. GO / NO-GO recommendation with conditions

Don't give me a generic positive outlook. I need the real picture, including reasons NOT to do this.
```

**Expected output:** Structured market analysis with a clear recommendation, not a cheerleading session.

---

### 2. Competitor Deep Dive

**When to use:** You know who your competitors are but haven't systematically broken down what they do well and where they're weak.

**Prompt:**
```
Do a competitive analysis of these [3-5] competitors in the [INDUSTRY] space:

1. [COMPETITOR 1 - name + URL]
2. [COMPETITOR 2 - name + URL]
3. [COMPETITOR 3 - name + URL]

For each competitor, analyze:
- Positioning: Who are they for? What's their main promise?
- Pricing: Model + price points + what you get at each tier
- Strengths: What do they genuinely do better than everyone else?
- Weaknesses: Where do customers complain? (check reviews, Reddit, Twitter)
- Content strategy: What are they publishing and where?
- Tech stack: What are they built on? (look at job postings, integrations page)
- Growth signals: Are they hiring? Raising money? Launching new features?

Then provide:
1. Competitive positioning map (2x2 matrix with axes I should care about)
2. Gaps in the market that none of them are filling
3. The "unfair advantage" I could build that they can't easily copy
4. Specific features or angles I should steal (legally and ethically)
5. Where I should NOT compete head-to-head
```

**Expected output:** Comparative table plus strategic recommendations, not just a list of features.

---

### 3. Pricing Strategy Builder

**When to use:** You're about to set prices and don't want to leave money on the table or price yourself out of the market.

**Prompt:**
```
Help me build a pricing strategy for [PRODUCT/SERVICE].

Context:
- What I'm selling: [DESCRIBE THE OFFER]
- Who's buying: [TARGET CUSTOMER + THEIR BUDGET RANGE]
- Competitor pricing: [LIST 3-5 COMPETITORS AND THEIR PRICES]
- My costs: [FIXED AND VARIABLE COSTS PER UNIT/CUSTOMER]
- My goal: [REVENUE TARGET / CUSTOMER COUNT TARGET]

Analyze and recommend:
1. Pricing model (one-time, subscription, usage-based, tiered, freemium)
   - Why this model fits my business specifically
2. Price point recommendation with reasoning
   - Anchoring strategy (what's the "compared to what?" framing)
3. Tier structure (if applicable)
   - What goes in free vs. paid vs. premium
   - Name each tier (not "Basic/Pro/Enterprise" - something memorable)
4. Launch pricing vs. long-term pricing
   - Should I start lower and raise? Offer founding member rates?
5. Discount strategy
   - Annual vs. monthly gap
   - When to discount (and when to never discount)
6. Revenue projection at 3 scenarios: conservative, moderate, optimistic
   - Show the math

Warning: If my pricing is way off from what the market will bear, tell me directly. Don't just validate what I want to hear.
```

**Expected output:** Complete pricing framework with numbers, not just theory.

---

### 4. Customer Avatar Builder

**When to use:** You think you know your customer but haven't written it down in a way that makes every marketing decision easier.

**Prompt:**
```
Build a detailed customer avatar for [BUSINESS NAME].

What I sell: [PRODUCT/SERVICE].
Current customers (if any): [DESCRIBE WHO'S ALREADY BUYING OR SHOWING INTEREST].
Price point: [PRICE].

Create 2 distinct avatars (primary and secondary buyer) with:

1. Demographics
   - Age, location, income, job title, education
   - But make these specific, not ranges (not "25-45", pick an age)

2. Psychographics
   - What do they believe about [YOUR INDUSTRY]?
   - What have they already tried that didn't work?
   - What's their relationship with technology?
   - Are they buying for themselves or for a team/company?

3. Day in their life
   - Walk me through a typical workday where they feel the pain my product solves
   - What triggers them to finally search for a solution?

4. Buying behavior
   - Where do they research before buying? (Google, YouTube, Reddit, asking friends?)
   - What would make them buy today vs. "save for later"?
   - Who else influences their decision? (boss, spouse, team, online community)
   - What's their biggest objection at the checkout page?

5. Communication preferences
   - What platforms are they on daily?
   - What content format do they prefer? (video, text, audio)
   - What words and phrases do they use to describe their problem?
   - What language turns them off?

Give each avatar a name and a one-line bio I can reference in future prompts.
```

**Expected output:** Two detailed avatars with enough depth to guide all marketing decisions.

---

### 5. SWOT Analysis (That's Actually Useful)

**When to use:** Quarterly strategy review, before a pivot, or when you need to step back and see the full picture.

**Prompt:**
```
Run a SWOT analysis for [BUSINESS NAME].

Business context:
- What we do: [DESCRIBE]
- Revenue: [CURRENT MONTHLY/ANNUAL]
- Team: [SIZE AND ROLES]
- How long we've been operating: [TIME]
- Biggest recent win: [DESCRIBE]
- Biggest current challenge: [DESCRIBE]

For each quadrant, give me 5 items. But here's the important part:

STRENGTHS: Things that are genuinely hard for competitors to replicate, not just things we do.
WEAKNESSES: Things that are actively costing us money or customers right now, not theoretical risks.
OPPORTUNITIES: Specific moves we could make in the next 90 days, not vague industry trends.
THREATS: Things that could actually happen in the next 6-12 months, not doomsday scenarios.

Then provide:
1. SO strategies (use Strengths to capture Opportunities) - 2 specific plays
2. WO strategies (fix Weaknesses to capture Opportunities) - 2 specific plays
3. ST strategies (use Strengths to defend against Threats) - 2 specific plays
4. WT strategies (fix Weaknesses to reduce Threat impact) - 1 specific play

End with: "The single most important thing to do in the next 30 days based on this analysis is..."
```

**Expected output:** Actionable SWOT, not a college assignment. Each item tied to a real business decision.

---

### 6. Unit Economics Calculator

**When to use:** Before scaling. You need to know if every customer you acquire makes you money or bleeds you dry.

**Prompt:**
```
Calculate the unit economics for [BUSINESS NAME].

Inputs:
- Product/service: [WHAT YOU SELL]
- Price: [PRICE PER UNIT/MONTH]
- Cost to deliver: [VARIABLE COST PER CUSTOMER]
- Customer acquisition cost components:
  - Ad spend per month: [AMOUNT]
  - Customers acquired per month: [NUMBER]
  - Sales team cost (if any): [AMOUNT]
  - Other acquisition costs: [LIST]
- Average customer lifetime: [MONTHS]
- Monthly churn rate (if subscription): [PERCENTAGE]
- Upsell/cross-sell revenue per customer: [AMOUNT]

Calculate:
1. Customer Acquisition Cost (CAC)
2. Lifetime Value (LTV)
3. LTV:CAC ratio (and whether it's healthy)
4. Months to recover CAC (payback period)
5. Gross margin per customer
6. Contribution margin
7. Break-even point (customers needed)

Then model 3 scenarios:
- Current state
- If I reduce CAC by 30% (how?)
- If I increase LTV by 40% (how?)

Show all math. Flag any numbers that look unhealthy. If I'm burning cash on every customer, say it plainly.
```

**Expected output:** Full unit economics breakdown with scenario modeling and health indicators.

---

### 7. Business Model Canvas Generator

**When to use:** Starting a new venture or restructuring an existing one. Gets the whole business on one page.

**Prompt:**
```
Create a Business Model Canvas for [BUSINESS IDEA/NAME].

What we're building: [DESCRIBE IN 2-3 SENTENCES]
Target market: [WHO]
Revenue target: [FIRST YEAR GOAL]

Fill out all 9 blocks with specifics, not generics:

1. Customer Segments (be specific about who pays, not who benefits)
2. Value Propositions (what job are you doing for them that they'd pay for?)
3. Channels (how do customers find you and how do you deliver?)
4. Customer Relationships (self-service, personal, automated, community?)
5. Revenue Streams (how exactly does money come in?)
6. Key Resources (what do you absolutely need to make this work?)
7. Key Activities (what must you do every week to keep the engine running?)
8. Key Partnerships (who do you need that you can't replace easily?)
9. Cost Structure (list every recurring cost, fixed and variable)

For each block, include:
- Current state (or "not started")
- Target state in 90 days
- The #1 risk in this block

End with a "riskiest assumption" callout. What's the one thing that, if wrong, kills the whole model?
```

**Expected output:** Complete BMC with current state, targets, and risk analysis.

---

### 8. Product Launch Checklist

**When to use:** 2-4 weeks before launching anything. This ensures you don't forget the things that sink launches.

**Prompt:**
```
Build a comprehensive launch checklist for [PRODUCT NAME].

Product: [DESCRIBE]
Launch date: [DATE]
Platform: [WHERE IT'S BEING SOLD]
Audience size: [EMAIL LIST, SOCIAL FOLLOWING, etc.]
Budget for launch: [AMOUNT]

Create a week-by-week checklist covering:

WEEK -4 (Four weeks before launch):
- Product readiness tasks
- Landing page / sales page requirements
- Email sequence drafts needed

WEEK -3:
- Beta testing / soft launch tasks
- Content creation for launch
- Affiliate / partner outreach

WEEK -2:
- Pre-launch email sequence activation
- Social proof collection
- Technical testing (checkout, delivery, onboarding)

WEEK -1:
- Final promotional content
- Community seeding
- Contingency planning (what if X breaks?)

LAUNCH DAY:
- Hour-by-hour action plan
- Monitoring checklist
- Response templates for common questions

WEEK +1:
- Follow-up sequence
- Feedback collection
- Performance review metrics to track

For each task, mark it as: [CRITICAL - launch fails without this] or [IMPORTANT - improves results] or [NICE TO HAVE].
```

**Expected output:** A printable, chronological launch plan with priority levels.

---

### 9. Revenue Diversification Planner

**When to use:** You have one income stream and want to build multiple without spreading too thin.

**Prompt:**
```
I currently make money from [CURRENT REVENUE STREAM].

Monthly revenue: [AMOUNT]
Time spent: [HOURS/WEEK]
My skills: [LIST 3-5 CORE SKILLS]
My existing assets: [EMAIL LIST SIZE, SOCIAL FOLLOWING, CONTENT LIBRARY, TOOLS BUILT, etc.]

Suggest 5 additional revenue streams ranked by:
1. Speed to first dollar (fastest first)
2. Effort required (lowest first)
3. Revenue potential (highest first)
4. Synergy with current business (highest first)

For each stream, provide:
- What it is (specific, not "consulting")
- Who pays and why
- Realistic revenue range in months 1-3
- Startup cost (time and money)
- How it leverages what I already have
- One example of someone doing this successfully
- First 3 action steps to get started this week

Also flag:
- Which 2 streams I should start with (and in what order)
- Which streams to avoid until I hit [REVENUE MILESTONE]
- How these streams feed each other (flywheel effect)
```

**Expected output:** Prioritized revenue stream plan with concrete first steps.

---

### 10. Quarterly Business Review Template

**When to use:** End of every quarter. Forces you to look at the numbers and make decisions instead of just "staying busy."

**Prompt:**
```
Run a quarterly business review for [BUSINESS NAME], Q[1/2/3/4] [YEAR].

Data to analyze:
- Revenue this quarter: [AMOUNT] (last quarter: [AMOUNT])
- Expenses this quarter: [AMOUNT]
- New customers: [NUMBER]
- Churned customers: [NUMBER]
- Top revenue source: [SOURCE]
- Hours worked per week (average): [HOURS]
- Key projects shipped: [LIST]
- Key projects delayed: [LIST]

Generate a QBR report with:

1. FINANCIAL HEALTH
   - Revenue growth rate (QoQ and YoY if data available)
   - Profit margin
   - Revenue per hour worked (your real hourly rate)
   - Runway at current burn rate

2. CUSTOMER HEALTH
   - Acquisition rate trend
   - Churn rate and reasons (if known)
   - Customer concentration risk (is one client >30% of revenue?)

3. OPERATIONAL HEALTH
   - Shipped vs. planned ratio
   - Biggest time sinks
   - What should be automated or delegated?

4. STRATEGIC REVIEW
   - What worked this quarter (double down)
   - What didn't work (stop or fix)
   - What was missing (start)

5. NEXT QUARTER PRIORITIES
   - Top 3 goals (with specific numbers, not "grow revenue")
   - Key metric to watch
   - One thing to stop doing
   - One experiment to run

Be direct. If the numbers are bad, say it. If I'm working too many hours for too little revenue, call it out.
```

**Expected output:** Complete QBR document with financial analysis and strategic recommendations.
