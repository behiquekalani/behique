---
title: "The Prediction Market Playbook: How to Research, Bet, and Profit on Polymarket"
type: product
price: $14.99
tags: [trading, prediction-markets, polymarket, research, strategy, kelly-criterion, risk-management]
created: 2026-03-22
---

**DISCLAIMER: This is educational content only. Nothing in this guide constitutes financial or investment advice. Prediction markets involve real financial risk. Never risk money you cannot afford to lose entirely. Past performance does not predict future results. The author is not a licensed financial advisor.**

---

# The Prediction Market Playbook
## How to Research, Bet, and Profit on Polymarket

---

## Table of Contents

1. [What Polymarket Is and Why It Beats Traditional Investing for Quick Capital Growth](#chapter-1)
2. [How Prediction Markets Actually Work](#chapter-2)
3. [The 5 Types of Markets Worth Betting On](#chapter-3)
4. [Research Framework: How to Find Your Edge Before Placing a Bet](#chapter-4)
5. [The Kelly Criterion Simplified: Position Sizing for Prediction Markets](#chapter-5)
6. [Common Biases That Destroy Accounts](#chapter-6)
7. [The $500 Deployment Framework: How to Start Small and Scale](#chapter-7)
8. [Case Studies: 3 Specific Market Types with Analysis](#chapter-8)
9. [Risk Management: The Full Framework](#chapter-9)
10. [The Meta-Game: Following Sharp Money and Reading Market Movements](#chapter-10)

---

## Chapter 1: What Polymarket Is and Why It Beats Traditional Investing for Quick Capital Growth {#chapter-1}

Polymarket is a prediction market platform built on the Polygon blockchain. It lets you trade on the outcomes of real-world events by buying and selling binary contracts. If the event resolves YES, the contract pays $1.00. If it resolves NO, it pays $0.00. You buy and sell these contracts at prices between $0.01 and $0.99, and the price reflects the market's current estimate of how likely the event is.

That is the full mechanism. Everything else in this guide is built on understanding that one structure deeply.

### The Core Advantage Over Stocks

Traditional stock investing has real value, but it is structurally slow. You buy shares, hold through earnings cycles, wait for the market to recognize value. A good stock thesis might take 18 months to play out. A prediction market thesis plays out in days, weeks, or at most a few months because every contract has a fixed resolution date.

This time compression is the key structural advantage. You are not waiting for the world to eventually agree with you. You are waiting for a specific event to either happen or not happen. That binary, time-bound nature means capital that was tied up for 6 months in a stock might cycle through 15 prediction market positions instead, each one a discrete learning opportunity.

This is not about which is "better." Stocks build long-term wealth through compounding. Prediction markets offer a different surface area: faster feedback loops, clearly defined resolution criteria, and the ability to profit on specific information advantages rather than general market trends.

### Where Prediction Markets Sit in the Landscape

Prediction markets are not gambling. They are not investing in the traditional sense. They are information markets.

The gambler bets on outcomes based on preference, intuition, or luck. The investor buys ownership in an asset with indefinite hold time. The prediction market trader buys a probability assessment and profits if their assessment is more accurate than the market's.

The difference is the information component. Gambling at a casino is negative expected value by design. Sports betting has a built-in house edge (the vig) that makes it negative expected value by default. Prediction markets do not have a guaranteed house edge. The price is set by other participants. If you have better information or better analysis than the crowd, you have positive expected value.

This is why the serious question in prediction markets is never "what do I think will happen." It is "is the market mispricing this event, and do I have a specific reason to believe it is?"

### Why Capital Grows Faster in the Learning Phase

A beginner stock investor learns slowly. Market feedback arrives in quarterly increments. One year of stock trading might give you four significant learning cycles.

A beginner prediction market trader can have 30 resolved positions in the first 60 days. Each one is a complete lesson: your probability estimate, the market price, the outcome, the difference. That feedback density is how you actually learn to calibrate.

This is why the $500 starting framework in Chapter 7 is structured around learning first, not returns first. The returns come from the calibration. The calibration comes from the feedback loops. The faster feedback loops are the actual structural advantage.

---

## Chapter 2: How Prediction Markets Actually Work {#chapter-2}

### The Contract Mechanics

Every contract on Polymarket is a question with a specific resolution condition. "Will Bitcoin close above $80,000 on April 1, 2026?" is an example. If it does, YES contracts pay $1.00. If it does not, NO contracts pay $1.00.

You do not need to hold until resolution. You can buy a YES contract at $0.55 and sell it at $0.72 if the price moves in your favor before resolution. This makes prediction markets a continuous trading environment, not just a bet-and-wait system.

The price at any moment reflects the aggregated opinion of all current market participants, weighted by how much money they put behind their view. A $0.70 YES price means the market collectively believes there is a 70% probability of YES. Whether that assessment is accurate is the only question worth asking.

### Probability and Price Are the Same Thing

This sounds obvious but most new traders do not internalize it.

When you see a Polymarket contract priced at $0.63, you are not seeing a "bet line." You are seeing a probability estimate. 63%. The market thinks there is a 63% chance this event occurs.

Your job is not to decide if you "like" YES or NO. Your job is to decide if 63% is accurate. If you believe the true probability is 75%, you buy YES because you think the market is underpricing the event. If you believe the true probability is 50%, you buy NO (or sell YES) because you think the market is overpricing it.

This reframe changes how you approach every trade. You are not picking winners. You are finding mispriced probabilities.

### Market Making and Liquidity

Polymarket runs on an order book system. When you want to buy YES contracts, you are either:

- Matching against someone who already has a sell order posted (a resting ask)
- Posting your own bid and waiting for someone to match it

Market makers are participants who continuously post both bids and asks, capturing the bid-ask spread as their profit. They provide liquidity. Without them, every trade would require finding a willing counterparty at exactly your price.

The bid-ask spread is your transaction cost in addition to the platform fee. If the best ask for YES is $0.64 and the best bid is $0.62, you pay $0.64 to buy and receive $0.62 if you immediately sell. That $0.02 spread is friction.

In deep, liquid markets (major elections, high-volume crypto price markets), spreads are tight, often $0.01 or less. In thin markets, spreads can be $0.05-0.10, meaning you need a significant price move in your favor just to break even.

### How Contracts Resolve

Resolution criteria are the most important and most underread section of any prediction market contract. Every contract specifies:

1. What specific condition constitutes YES.
2. What source or oracle determines the outcome.
3. When resolution happens.

Polymarket uses UMA Protocol as its dispute resolution layer. If a resolution is contested, UMA token holders vote on the outcome. This is rare but not nonexistent. The implication: even if you are right about the underlying event, a resolution dispute can go against you.

Before trading any contract, read the resolution criteria carefully. Specifically check: what counts as YES, what source is used to determine it, and whether the criteria match what you think they mean.

Common resolution errors people make:

A contract about "winning the election" might resolve based on major networks calling it, not the final certified result. The timing matters. A contract about GDP growth might resolve on the initial estimate, not the revised figure released 90 days later. The specific number matters.

### The Aggregate Information Signal

One of the documented properties of prediction markets is that they consistently outperform polls, expert panels, and media consensus on forecasting event probabilities. The reason is simple: money creates accountability. Anyone who believes the market is wrong has a direct financial incentive to trade it toward accuracy.

This property has a double implication. First, the crowd is often right, which means you need a specific reason to disagree. Second, the crowd has systematic biases and information processing delays, which is where individual traders with specific knowledge find edge.

---

## Chapter 3: The 5 Types of Markets Worth Betting On {#chapter-3}

Not all prediction markets are equally worth your time. Some are efficient and offer almost no edge for a retail trader. Others are systematically underserved. Here are the five categories worth focusing on and why.

### 1. Elections and Political Outcomes

Electoral markets are the most popular on Polymarket by volume. They are also among the most efficient for major races. The US presidential election draws hundreds of millions of dollars in volume. That capital means the market has processed nearly every publicly available piece of information.

Major elections are hard to edge unless you have genuine local knowledge or polling analysis expertise that differs from the consensus.

Where elections are worth it: regional, local, and less-watched political events. Gubernatorial races in smaller states. Parliamentary outcomes in smaller countries. Puerto Rico-specific political events. The information asymmetry between someone with local context and the average Polymarket participant is real and exploitable.

What to watch for: event-driven price moves following debates, polls, or major news. The market sometimes overreacts to a single data point. If you understand the underlying race deeply, you can identify when the market's reaction is disproportionate.

### 2. Crypto Price Markets

Polymarket has extensive crypto price markets. Will Bitcoin be above X on date Y? Will Ethereum stay below Z?

These markets are interesting for a specific reason: crypto price action has documented patterns tied to on-chain data, exchange flows, and macro catalysts. If you track these signals, you sometimes see information entering the market before it shows up in the price of the prediction contract.

The challenge: crypto markets are followed by sophisticated participants who also track on-chain data. The edge here requires genuinely better information or analysis, not just general familiarity with crypto.

What works: short-horizon markets (24-72 hour resolution) where on-chain signals give you a view on near-term price action. Long-horizon crypto markets are too uncertain for most retail traders to edge consistently.

### 3. Sports Outcomes

Sports markets on Polymarket exist but tend to be smaller in volume than the specialized sports betting platforms. The prediction market structure is often less favorable than pure sports betting lines for major events because the liquidity is thinner.

Where sports markets are worth it: outcome markets for specific events that are adjacent to the actual game result. "Will this player participate in the game?" is a different market than "who wins the game." Health and availability markets for key players can be edged by people who follow a team closely.

Avoid: wagering on game outcomes in thin markets without doing the comparison to what real sportsbooks are pricing. If the market price on Polymarket significantly differs from sharp sportsbook lines, that gap is usually explained by liquidity, not mispricings you can exploit.

### 4. News Events and Current Affairs

These are markets about specific news-adjacent outcomes. Will a central bank cut rates? Will a government pass a specific bill? Will a specific executive resign?

This category is where retail traders with domain expertise often find the best edge. The market is betting on outcomes that require reading primary sources: actual policy statements, legislative text, regulatory filings. Most participants read headlines. Primary source readers have an information advantage.

The specific type of edge here: understanding what the actual resolution criteria mean relative to how headlines characterize the situation. A market about "rate cut at the March meeting" might resolve based on the basis point change, not the market's narrative about what counts as a "cut." If you read the Fed's actual statement and the contract's criteria, you sometimes see a mismatch.

### 5. Technology and AI Milestones

Markets about specific technology events have expanded significantly as AI development accelerates. Will GPT-5 launch before a specific date? Will a specific model achieve a benchmark score? Will a specific company release a specific product?

This category has a genuine retail edge opportunity: people who closely follow AI development, software company announcements, and technology research are better positioned than generalist traders. The information is public but requires deep familiarity to interpret correctly.

The AI and tech milestone markets also tend to be less liquid than election markets, which means both that the spreads are wider and that a small number of informed traders can move the price. This is a feature: it means the market has not fully processed all available information.

What to watch: official announcements, research papers, developer conference dates, product roadmap leaks through legitimate channels. The pattern is that market prices on tech milestones often lag clear public signals by hours to days.

---

## Chapter 4: Research Framework: How to Find Your Edge Before Placing a Bet {#chapter-4}

Edge in prediction markets is not general. You do not have edge in the market as a whole. You have edge in specific domains where your information is better, your analysis is more accurate, or your interpretation of resolution criteria is more precise than the crowd's. The research framework exists to identify when that condition is met.

### Source Hierarchy

Before researching any market, know which sources you are working from and what weight to give them.

**Tier 1 (primary sources):** Official announcements, regulatory filings, legal documents, scientific papers, vote records, court rulings, government data releases. These are facts. They require interpretation but do not require verification.

**Tier 2 (direct reporting):** Journalists with documented access to primary sources. Articles that quote primary documents directly or quote named decision-makers. These are one step removed but close to the source.

**Tier 3 (aggregated analysis):** Commentary, opinion, expert predictions, podcasts. Useful for framing but not for establishing probability. These are downstream.

**Tier 4 (market sentiment):** Twitter, Reddit, prediction market discussion boards. This tells you what people currently believe. It does not tell you what will happen. It is noise relative to outcome prediction.

Build research from Tier 1 downward. Traders who start from Tier 4 are not trading probability. They are trading sentiment. Sentiment is unreliable.

### Establishing a Base Rate

Every event on a prediction market is an instance of a category. Before analyzing the specific event, find out what happens historically in that category.

FDA drug approvals at Phase 3: approximately 60-65% historical approval rate. That is your starting point before examining the specific drug and company.

Incumbent re-election rates: varies by jurisdiction and economic conditions, but the historical data is publicly available. That is your prior.

Central bank rate decisions: you can find the historical record of what the Fed or ECB has done in similar economic conditions. That is your prior.

Using base rates prevents both overconfidence and underconfidence in specific analyses. If your research leads you to a probability estimate dramatically different from the historical base rate, your burden of evidence is higher. The base rate is not always right, but departing from it requires specific, well-sourced justification.

### The 48-Hour Rule

Do not trade any market you discovered less than 48 hours ago.

This rule exists for a specific reason: the first exposure to a market creates a strong impression that feels more complete than it is. Most research errors happen when traders act on the first layer of what they know without discovering what they do not know yet.

The 48 hours allows:
- Time to find primary sources instead of relying on the secondary ones that introduced you to the market
- Time to identify and stress-test the counterargument
- Time to receive new information that might arrive and change your analysis
- Time to confirm the resolution criteria match your understanding of the outcome

The exception: if you have deep pre-existing domain knowledge and the opportunity is genuinely time-sensitive. But this exception applies rarely. Most urgency in prediction markets is false.

### The Counterargument Requirement

Before finalizing any position, write down the strongest argument for the opposite side.

Not the easiest argument. The most credible one. If you cannot identify a strong counterargument after researching a market, you have not researched it enough. Every non-trivial binary outcome has a credible case for both sides.

After writing the strongest counterargument:

If it changes your probability estimate, update your estimate. You found new information.

If it does not change your estimate, you now understand specifically why you believe what you believe. That is a better position to trade from than general confidence.

### The Edge Identification Test

Before placing any bet, answer this question completely: what specific information or analytical insight do I have that the market has not fully priced in?

The answer must be specific. Not "I think X is more likely." Specific: "I read the primary source document and it contains a condition that makes YES resolution ambiguous in a way the market price does not reflect" or "I follow this research domain daily and the paper released last week changes the probability more than the current price suggests."

If you cannot answer this question specifically, you do not have identified edge. You have an opinion. An opinion on a well-researched market is already priced in by other people who had the same opinion before you.

### When Not to Trade

The research process sometimes concludes correctly that you should not trade. This is the right outcome.

Do not trade when:
- Your probability estimate falls within the bid-ask spread of the current market price
- Your primary information sources are the same ones most participants are using
- The resolution criteria contain ambiguities that could cause you to win on the outcome but lose on the resolution
- You cannot complete the edge identification test with a specific answer
- Less than 48 hours have passed since you first encountered the market

Discipline in not trading is a skill. It compounds. The traders who succeed long-term take fewer positions, not more.

---

## Chapter 5: The Kelly Criterion Simplified: Position Sizing for Prediction Markets {#chapter-5}

Position sizing in prediction markets is the difference between good trading and going broke. The Kelly Criterion is the mathematical framework for optimal position sizing when you have a known edge. Understanding it prevents the two most common sizing errors: betting too much and betting too little.

### What Kelly Actually Says

The Kelly Criterion was developed by John L. Kelly Jr. at Bell Labs in 1956. The core insight is that there is an optimal fraction of your capital to bet on any given wager, based on the size of your edge and the odds.

The full formula:

Kelly % = (bp - q) / b

Where:
- b = the net odds (what you win relative to what you risk)
- p = your estimated probability of winning
- q = your estimated probability of losing (1 - p)

For a prediction market contract priced at $0.60 YES, if you buy YES:
- You are risking $0.60 to win $0.40 (the $1.00 payout minus your $0.60 cost)
- So b = 0.40 / 0.60 = 0.667

If you estimate the true probability is 75%:
- p = 0.75
- q = 0.25
- Kelly % = (0.667 x 0.75 - 0.25) / 0.667
- Kelly % = (0.500 - 0.25) / 0.667
- Kelly % = 0.250 / 0.667
- Kelly % = 37.5%

Full Kelly says bet 37.5% of your prediction market capital on this position. Do not do this.

### Why You Use Fractional Kelly

Full Kelly is mathematically optimal under one condition: that your probability estimate is exactly correct. In reality, your estimate always has uncertainty. You might believe 75% but the true probability could be anywhere from 65% to 85% given the limits of your information.

Fractional Kelly accounts for this estimation uncertainty. The standard practice is to use quarter Kelly (25% of the full Kelly recommendation).

In the example above: 37.5% x 0.25 = 9.4% of portfolio.

Even quarter Kelly can be aggressive in practice. The rule of thumb that overrides Kelly in all circumstances: no single position exceeds 5% of your total prediction market capital.

Use Kelly to rank positions (higher Kelly = stronger edge = larger position relative to other positions), not to set absolute sizes.

### A Practical Sizing Table

For a $500 starting capital, these are the position size ranges:

| Estimated Edge | Quarter Kelly | Capped At |
|---------------|--------------|-----------|
| Very strong (15%+ edge) | ~8-10% of capital | 5% = $25 |
| Strong (8-14% edge) | ~5-7% of capital | 5% = $25 |
| Moderate (3-7% edge) | ~2-4% of capital | $10-20 |
| Weak (1-2% edge) | ~1% of capital | $5 |
| No identified edge | 0% | $0 |

The edge percentage means the difference between your estimated probability and the market price, adjusted for the odds. A market priced at $0.65 where you estimate 75% has a 10-point edge in your favor.

### The Math on Losing Positions

Even with genuine edge, you will lose positions. That is how probability works.

A contract where the true probability is 75% resolves NO 25% of the time. If you take 20 positions where you have genuine 75% probability and size them at 5% of your $500 portfolio ($25 each), you expect to lose approximately 5 of them.

With 5 losses at $25 each: $125 loss from losing positions.
With 15 wins at $25 each, winning $16.67 per contract (at a $0.60 purchase price): $250 in wins.

Net: +$125 on those 20 positions.

This is how the math works out favorably even though you lost 25% of your positions. If any single position were sized at 30% of capital ($150), one loss would destroy 30% of your portfolio even though you were statistically correct to make the trade.

Position sizing is not about being conservative. It is about keeping the math working in your favor over a sample size large enough to matter.

### The Minimum Viable Edge Calculation

Before placing any bet, calculate whether the edge justifies the trade given transaction costs.

Transaction costs: Polymarket charges approximately 0.01% per trade. The bid-ask spread in liquid markets is typically $0.01-0.02. For a $25 position, total friction is roughly $0.25-0.50.

Your edge needs to exceed friction on expected value. If the market is at $0.65 and you estimate $0.67, that 2-point edge on a $25 position is worth about $0.50 in expected value. After transaction costs, you are roughly breakeven in expectation. That is not a trade worth making.

If the market is at $0.65 and you estimate $0.75, that 10-point edge on a $25 position is worth about $2.50 in expected value after costs. That is worth making.

---

## Chapter 6: Common Biases That Destroy Accounts {#chapter-6}

The gap between what traders think they are doing and what they are actually doing is mostly explained by cognitive biases. These are not character flaws. They are systematic patterns in how all human brains process information under uncertainty. Knowing them does not eliminate them, but it gives you a framework to catch them before they cost money.

### Availability Heuristic

The brain estimates the probability of an event based on how easily relevant examples come to mind. Vivid, recent, or emotionally significant events are recalled more easily, so they get higher probability estimates than less vivid events of equal actual likelihood.

How it manifests in prediction markets: a dramatic recent event (a regulatory crackdown, a major political upset, a sudden market crash) makes similar events feel more likely in the near term. The market prices up the probability of another similar event not because the base rate justifies it, but because the recent example is cognitively available.

The correction: after any dramatic event, pull the historical base rate for that category before adjusting your probability estimate. Ask specifically: does this recent event provide genuine predictive information about the probability, or is it just cognitively available?

### Recency Bias

Related but distinct from availability heuristic: recency bias weights recent data disproportionately relative to the longer historical record.

An election poll from two weeks ago feels more relevant than the historical base rate for incumbent re-election, even when the long-run base rate is a better predictor. A crypto price move from yesterday feels more predictive than the three-year trend, even when the trend is more informative.

Prediction markets are particularly vulnerable to recency bias because prices update in real time as news arrives. Every piece of new information creates a reaction. The reaction is often proportionate to the recency and vividness of the information, not to its actual predictive weight.

The correction: when making probability estimates, explicitly note which of your supporting evidence is recent and question whether its recency is making you weight it more than you should.

### Overconfidence in Probability Estimates

Studies consistently show that when people say they are "90% confident," they are actually correct about 75% of the time. When they say "99% confident," they are correct much less than 99% of the time.

This overconfidence is systematic. It does not go away with experience unless you track your predictions and get calibration feedback.

In prediction markets, overconfidence manifests as:
- Taking positions where the market is at $0.70 and you estimate $0.80, when you should only be at $0.73
- Being surprised when you lose positions you were highly confident in
- Not adequately updating your view when counterarguments arise

The correction: keep a prediction log. Track every estimate you make, the outcome, and the difference. Humans generally overestimate probabilities above 50% and underestimate probabilities below 50%. Know which direction you skew and adjust accordingly.

### Anchoring

When a contract has been trading at a specific price for an extended period, that price becomes an anchor. New information arrives, but traders update insufficiently relative to what the information warrants because they are anchored to the prior price.

This creates the classic prediction market profit opportunity: markets that underreact to new information. If a major development happens and the contract price moves from $0.60 to $0.68 when it should move to $0.80 given the new information, the residual gap is exploitable.

The correction: when evaluating a market after significant new information, ask what the price should be based on the new information alone, without referencing what it was before. Then ask whether the current market price reflects that.

### Loss Aversion and the Disposition Effect

Loss aversion is the well-documented asymmetry in how people experience gains and losses. Losing $100 feels roughly twice as bad as winning $100 feels good.

In prediction markets, this creates the disposition effect: traders hold losing positions too long (hoping to avoid locking in a loss) and exit winning positions too early (eager to lock in the gain before losing it).

Both behaviors are costly. Holding a losing position that has new fundamental information against it locks up capital that could be redeployed. Exiting a winning position before full resolution leaves value on the table if your analysis was correct.

The correction: use the reversal test. If you did not hold this position today, would you buy it at the current price? If yes, hold. If no, exit regardless of your entry price. The entry price is irrelevant to whether the current price is correct.

### Confirmation Bias

Once you have formed a view on a market, you will naturally notice evidence that supports your view more readily than evidence against it. This is confirmation bias. It is not deliberate dishonesty. It is how information processing works.

The practical danger: after entering a position, you keep finding reasons you were right and dismissing signals that suggest you were wrong.

The correction: actively seek the strongest argument against your position after entering it, not before. The counterargument requirement from Chapter 4 is specifically designed to force this. Do it again after major new information arrives, not just before the initial trade.

---

## Chapter 7: The $500 Deployment Framework: How to Start Small and Scale {#chapter-7}

**DISCLAIMER: This framework is educational only. This is not financial advice. Only risk money you can afford to lose entirely.**

The $500 starting framework is designed around one primary goal: learning, not returns. The returns in prediction markets come from calibration. Calibration comes from feedback loops. The fastest feedback loops come from taking many small, well-researched positions over time and tracking the outcomes honestly.

### Phase 1: The First 30 Days (Months 1)

**Capital allocation:**
- Total capital: $500
- Cash floor (never deploy): $125
- Working capital: $375

**Position structure:**
- Maximum position size: $15 (3% of total capital)
- Target open positions at any time: 5-8
- Maximum in any single correlated domain: 3 positions

**Activity requirements:**
- Read resolution criteria before every trade
- Complete the research checklist (Chapter 4) before every trade
- Log every position in the trading journal (more on this below)

**Goal for Phase 1:**
Not profit. Volume of resolved positions with honest documentation. The target is 15-20 resolved positions in the first 30 days, each with a logged probability estimate and post-resolution analysis.

**What to trade:**
Start with markets you have genuine domain knowledge in. If you follow crypto daily, start there. If you follow a specific country's politics, start there. Do not trade markets where you are starting from no prior knowledge just because they look interesting.

### Phase 2: First Review (Day 30-35)

Before adding any capital or changing position sizes, conduct a structured review of Phase 1.

Questions to answer honestly:
- What was your hit rate? (How often did your YES/NO call resolve correctly?)
- How calibrated were your probability estimates? If you estimated 70% on 10 positions, did approximately 7 of them resolve YES?
- Which market types did you edge in?
- Which market types were you consistently wrong in?
- Did you exit any positions early? Were those exits correct in hindsight?
- Were there positions you avoided that would have been profitable? Why did you avoid them?

The answers to these questions are more valuable than the dollar amount in your account. They tell you where your actual edge is.

### Phase 3: Refinement (Month 2-3)

After the Phase 1 review, refine based on the data.

If hit rate is above 55% in specific domains: those are your domains. Concentrate attention there. Increase maximum position size to $20 for markets in your strongest domains.

If hit rate is below 50% overall: do not scale. Reduce position sizes to $10, re-examine the research process, and look for the systematic error. Common issues at this stage: trading without a specific identified edge, anchoring on the market price rather than forming an independent estimate first, or consistently misreading resolution criteria in a specific category.

If hit rate is 50-55%: you are near breakeven. The edge is not clear yet. Maintain current sizes, take another 15-20 positions, and review again.

### Phase 4: Scaling (Month 4+)

Scale when all three of these are true:
1. You have 40+ resolved positions documented.
2. Your estimated probability track record shows calibration (not just win rate, but whether your 70% calls resolve YES about 70% of the time).
3. You have a positive return in at least two of the last three review periods.

Scaling does not mean doubling down on everything. It means increasing position sizes in the specific market types where your calibration is strongest, while maintaining the same discipline on position caps.

The ceiling on scaling is this: prediction market capital should remain capital you can afford to lose completely. As your account grows from returns, maintain that principle.

### The Trading Journal (Non-Negotiable)

The trading journal is not a nice-to-have. Without it, you cannot run the review process that drives improvement. Track every position with:

1. Date entered
2. Market name and resolution criteria (summary)
3. Purchase price (market's implied probability)
4. Your estimated true probability
5. Your specific rationale (why you believe the market is mispriced)
6. The strongest counterargument you identified
7. Position size
8. Date resolved
9. Outcome (YES/NO)
10. Return on position
11. One-sentence post-resolution lesson: what did this teach you?

A simple spreadsheet works. The format does not matter. The consistency does.

---

## Chapter 8: Case Studies: 3 Specific Market Types with Analysis {#chapter-8}

These case studies are constructed examples based on real market categories. They are educational illustrations of the research and analysis process, not specific trading recommendations.

### Case Study 1: A Regulatory Decision Market

**Setup:** A prediction market asks whether the FDA will approve a specific drug for a new indication by a specific date. The current market price is $0.55 YES.

**Standard research approach:**

First, the resolution criteria. Read them completely. The question is: does "approved" mean full approval, accelerated approval, or any formal positive action? The resolution source is specified as an official FDA announcement. This is clear and unambiguous.

Second, the base rate. FDA approval rates for NDA (New Drug Application) filings in the relevant disease category over the past decade run approximately 80-85% when the drug has already cleared an Advisory Committee vote. If this drug has a positive AdCom vote in its history, the base rate suggests the market's 55% may be underpriced.

Third, primary source research. The FDA's PDUFA date (the deadline by which FDA must act) is publicly available. The AdCom briefing documents are publicly available. Read them. Check whether the statistical analysis in the briefing documents was presented favorably or with significant concerns.

Fourth, the counterargument. The strongest case for NO: if there is a complete response letter (CRL) risk due to manufacturing inspection issues or a label negotiation delay. Check the company's most recent public disclosures for any manufacturing audit news.

**Analysis:** If the base rate is 80%, the AdCom was positive, and there are no identified manufacturing issues in public disclosures, the 55% market price may represent a significant mispricing. The edge is specific: most participants are reading media coverage of the drug, not the actual AdCom transcript and PDUFA history.

**Risk factors:** Resolution timing risk (FDA can extend review), label negotiation complexity, and any information the company has not yet disclosed publicly.

### Case Study 2: A Technology Milestone Market

**Setup:** A prediction market asks whether a major AI lab will release a specific next-generation model by a specific date. Current market price is $0.40 YES.

**Standard research approach:**

First, the resolution criteria. "Release" is potentially ambiguous. Does this mean general availability, API access, limited preview, or any official announcement? The criteria specify "publicly available API access." That is clearer.

Second, what is the base rate? AI model releases are harder to base-rate because the category is new and release cadences are irregular. Instead of a base rate, look at the specific company's release history. How long between generations historically? Are there any public statements about roadmap?

Third, primary source research. The company's research blog, official developer announcements, and researcher social media (which is public and often informative for major labs). Has anyone from the lab mentioned this model in public? What is the most recent communication from the company about their release schedule?

Fourth, information timing. Technology markets often lag clear public signals. If a major researcher at the lab posted something on a public forum two days ago that implies the model is in final testing, and the market has not moved, that is potential edge.

**Analysis:** If primary source research reveals positive signals (researchers discussing the model publicly, company communications suggesting imminent release) that have not yet moved the price from $0.40, the market may not have processed this information. The edge is domain-specific: following AI labs closely gives you faster access to signals that matter for these markets.

**Risk factors:** Unexpected safety issues causing delay, compute constraints, definition disputes about what "publicly available API access" means.

### Case Study 3: A Local Political Market

**Setup:** A Caribbean nation is holding a parliamentary vote on a significant economic policy. The market asks whether it passes. Current price is $0.60 YES.

**Standard research approach:**

First, resolution criteria. This is legislation passing. Clarify: passing on first reading, final reading, or signed into law? The criteria specify: "Passes final parliamentary vote." That is specific.

Second, base rate. What percentage of government-sponsored legislation in this parliament passes final vote when introduced? Check the parliamentary record. If the governing coalition has a majority and regularly passes its own legislation at a 90%+ rate, the 60% market price might underestimate the probability.

Third, primary source research. Access the parliamentary schedule directly. Is this bill on the calendar for the resolution period? Has the opposition announced formal opposition? Are there coalition members who have signaled dissent? Local news sources in the native language often have more specific reporting than English-language sources.

Fourth, the local knowledge edge. This is where the retail advantage is clearest. If you follow this country's political situation regularly, you have context about coalition dynamics, historical precedent, and party discipline that most traders in the Polymarket pool do not have. They are inferring from secondary English-language coverage. You have primary language sources and local context.

**Analysis:** If the base rate for governing coalition legislation is 85%+, the ruling party has the votes based on public statements, and local sources confirm no credible opposition movement within the coalition, the 60% price may significantly underprice the probability.

**Risk factors:** Coalition instability, procedural delays that push resolution past the contract date, definition questions about which "vote" qualifies.

---

## Chapter 9: Risk Management: The Full Framework {#chapter-9}

**DISCLAIMER: This is educational content only. Prediction markets involve real financial risk. Never risk money you cannot afford to lose entirely.**

Risk management is not the boring part of prediction market trading. It is the part that determines whether you are still playing in six months. All the research skill and probability calibration in the world does not matter if a poorly sized position wipes out a meaningful chunk of your capital before you learn the lesson.

### The Non-Negotiable Rules

These are not guidelines. They are rules. Breaking them will cost you eventually, and the eventual cost will be larger than whatever the exception saved.

**Rule 1: Maximum single position is 5% of prediction market capital.**
On $500, that is $25. No exceptions based on conviction, urgency, or "this one is different." Conviction is not edge. The research framework tells you whether you have edge. The 5% cap prevents any single error from being catastrophic.

**Rule 2: Maximum correlated exposure is 15% of total capital.**
If you have three positions that all depend on the same election outcome, the same Fed decision, or the same company announcement, they are effectively one position. Cap the total at 15% of capital ($75 on $500) regardless of how many contracts they are spread across.

**Rule 3: Always maintain 25% cash floor.**
Never fully deploy prediction market capital. Keep 25% ($125 on $500) available at all times. The best opportunities often appear when you are fully deployed. The cash floor prevents the situation where you see a clear edge and cannot act on it.

**Rule 4: The 72-hour reload rule.**
After a losing position resolves, wait 72 hours before entering another position in the same domain. Review what you got wrong before re-entering. This prevents revenge trading, which is the behavior of increasing bet size or frequency immediately after a loss to "get it back."

### Time Horizon and Position Management

Prediction market positions are not set-and-forget. Active management means:

Checking positions after major news relevant to the contract. Not to trade based on emotion, but to assess whether the new information changes your probability estimate.

Exiting early when the reversal test fails. If you would not buy this contract today at the current price, you should not hold it. The price at which you entered is irrelevant to whether the current price is correct.

Not exiting early because of anxiety. If nothing has changed about your fundamental analysis and the position has moved against you on noise, holding is usually correct. Anxiety is not information.

### Portfolio Correlation

Tracking which positions are correlated is not optional once you have 5+ positions open.

Obvious correlations: multiple positions on outcomes that all depend on the same election. Multiple crypto positions that all move on the same macro sentiment.

Less obvious correlations: a position on a tech company's product launch and a position on that company's quarterly earnings. A position on a regulatory outcome in one country and a position on a related outcome in a second country with the same regulatory body dynamics.

Map your open positions and identify which ones move together. The total exposure in any correlated cluster should not exceed 15% of capital.

### Diversification in Prediction Markets

Diversification in this context does not mean spreading bets across as many markets as possible. It means spreading across markets that resolve on independent information.

Five positions on five different elections that all resolve in the same week on US political outcomes are not diversified. Five positions in five different domains (tech milestone, crypto price, regulatory decision, local election, news event) that resolve on independent information are genuinely diversified.

The goal of diversification is to ensure that no single information event can resolve multiple positions against you simultaneously.

### The Psychology of Losing Positions

You will have losing positions. That is a mathematical certainty, not a reflection of your analysis quality.

A well-researched position at 75% probability resolves NO 25% of the time. That is not a failure of research. That is probability working as designed.

The failure condition is: losing money on a 75% probability position while also having sized it at 20% of your capital. The loss itself is expected. The sizing was the error.

Separate outcome quality from process quality. A well-researched, well-sized position that resolves incorrectly is a good trade. A poorly-researched, oversized position that resolves correctly is a bad trade that got lucky. Track both categories in your journal and evaluate on process, not outcome alone.

---

## Chapter 10: The Meta-Game: Following Sharp Money and Reading Market Movements {#chapter-10}

Beyond individual position analysis, there is a layer of market observation that improves over time: learning to read what the market as a whole is signaling, and distinguishing between informed price movement and noise.

### What "Sharp Money" Means in Prediction Markets

In sports betting, "sharp money" refers to large bets placed by professional bettors whose decisions consistently outperform the public. When sharps bet heavily on one side, lines move regardless of public sentiment.

In prediction markets, the equivalent is large orders from traders who have consistently been right. You cannot directly identify who these traders are, but you can observe their effect: significant price moves driven by large orders, often before information has widely propagated.

The observable signals:

**Large single-trade orders.** The Polymarket trade history shows individual trade sizes. A single order of several thousand dollars in a normally low-volume market is not a retail trader. It is someone with a specific reason to move capital at that moment.

**Price movement before news breaks.** When a contract moves significantly and no obvious news explains it, watch for what breaks in the next few hours. Informed traders sometimes have access to information slightly ahead of public release.

**Unusual volume clustering.** A market that normally trades $1,000 per day suddenly sees $20,000 in volume is telling you something. The content of what it is telling you requires investigation.

### Using Price Movements as Information

A price movement you did not anticipate is information. The question is: what new information has the market processed that you had not?

When a contract moves against your position:

1. Check for new information. What broke in the last few hours?
2. If new information exists: does it change your fundamental analysis? If yes, how much?
3. If no obvious new information exists: could this be a large uninformed order, or does the move suggest something you have not seen yet?

The error is reacting to the price movement itself rather than to the underlying information. A price move caused by an uninformed large order may create a temporary mispricing in the opposite direction of your thesis. A price move caused by genuine new information you missed requires you to update your analysis.

### Reading Contract Trajectories

A contract's price over time tells a story about how information has flowed into the market.

A contract that has moved steadily in one direction for weeks: the market has been consistently processing information pointing in that direction. The momentum is information about the overall information flow.

A contract that has been stable for weeks and then makes a sudden large move: a significant piece of information has arrived. Determine what it was before deciding whether the move is proportionate.

A contract that oscillates back and forth without directional movement: market participants disagree, the information is mixed, or the resolution criteria are ambiguous. High uncertainty, low predictability. Usually not worth trading unless you have a very specific view.

### Following the Market Without Following It Blindly

The market is often right. This is both a useful fact and a trap.

Useful: when the market's implied probability is significantly different from your estimate, assume the market knows something before assuming you know something the market does not. The burden of proof is on the person claiming to have better information than the aggregate of all other participants.

Trap: the market is "often right" is not the same as "always right." Markets have systematic biases. The whole premise of trading for edge is that the market is sometimes wrong in predictable ways. If you follow the market price uncritically, you are not trading. You are just observing.

The balance: use the market price as your starting prior, not your conclusion. Research the event independently. Form your own probability estimate. Compare it to the market price. Trade only when the gap is specific, justified, and larger than the cost of the trade.

### The Long Game

Prediction market edge compounds, but slowly.

In the first 20 positions, you are learning your domains and calibrating your estimates. Returns are uncertain. Wins from genuine edge and losses from learning errors mix together.

In positions 20-100, if you are tracking and reviewing honestly, patterns emerge. Your hit rate in specific domains becomes clear. Your systematic biases become visible. You know whether you underestimate or overestimate probabilities. You know which types of resolution criteria you consistently misread.

By position 100, the traders who have been honest in their tracking know specifically where their edge is and where it is not. They take fewer total positions but higher-quality ones. Their returns stabilize.

The meta-game is this: the long-term prediction market trader is not trying to win any individual bet. They are running an ongoing research program into their own performance, continuously identifying where their information and analysis is better than the crowd's, and deploying capital only where that condition is met.

That is the practice. It is harder than it sounds, requires more discipline than most people apply, and pays off for the ones who actually do it.

---

## Final Notes

The framework in this guide is built on one underlying principle: prediction markets reward information accuracy, not enthusiasm. The most common failure mode is entering positions based on having an opinion rather than having a specific reason to believe the market has mispriced a probability.

You will lose positions even when your research is correct. You will win positions you should not have taken. Over a large enough sample of well-documented, well-sized positions, the edge wins.

Document everything. Review regularly. Scale based on evidence, not confidence.

The $500 starting point is not a barrier. It is a calibration device. The lessons you learn on small positions are the same lessons that apply when the position sizes are larger.

---

**DISCLAIMER: This guide is for educational purposes only. Prediction markets involve real financial risk. The strategies described here do not guarantee profit and may result in loss of capital. Always do your own research. Only risk money you can afford to lose completely. The author is not a licensed financial advisor. Nothing in this guide should be construed as investment advice.**
