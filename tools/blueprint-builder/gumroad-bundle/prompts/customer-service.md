# Customer Service Prompts
## 10 Battle-Tested Prompts for Email Replies, FAQ Generation, and Complaint Handling

---

### 1. Customer Email Response Generator

**When to use:** You have a customer email and need a professional reply fast. Handles support, complaints, and general inquiries.

**Prompt:**
```
You are a customer support specialist for [BUSINESS NAME].

Our product/service: [DESCRIBE].
Our tone: [FRIENDLY AND CASUAL / PROFESSIONAL / WARM BUT EFFICIENT].
Our refund policy: [DESCRIBE BRIEFLY].
Our response time promise: [E.G., "within 24 hours"].

Here is the customer's email:

"""
[PASTE THE EMAIL]
"""

Write a response that:
1. Acknowledges their specific situation (don't start with "Thank you for reaching out")
2. Addresses every question or concern they raised (don't skip any)
3. Provides a clear next step or resolution
4. Sets expectations for timeline if action is needed
5. Ends with something specific, not "don't hesitate to reach out"

If the email is angry, do NOT apologize excessively. Acknowledge the frustration once, then focus on the solution.
If information is missing to solve their problem, ask for it specifically (max 3 questions).

Keep it under 150 words unless the situation requires more detail.
```

**Expected output:** Ready-to-send email reply that sounds human and resolves the issue.

---

### 2. FAQ Generator From Customer Data

**When to use:** You've been answering the same questions over and over. This turns your inbox into a FAQ page.

**Prompt:**
```
I run [BUSINESS NAME] and these are the most common questions/complaints I get:

1. [QUESTION/ISSUE]
2. [QUESTION/ISSUE]
3. [QUESTION/ISSUE]
4. [QUESTION/ISSUE]
5. [QUESTION/ISSUE]
6. [QUESTION/ISSUE]
7. [QUESTION/ISSUE]
8. [QUESTION/ISSUE]

For each one, write:
- The question (rewritten clearly, as a customer would phrase it)
- A short answer (2-3 sentences, direct)
- An expanded answer (for customers who need more detail)

Group them into logical categories (e.g., Billing, Getting Started, Troubleshooting, Account).

Also suggest:
- 5 questions customers SHOULD be asking but aren't
- Which 3 questions, if answered proactively, would reduce my support tickets the most
- Where to place the FAQ (product page, checkout page, onboarding email, help center)

Write all answers in [FIRST PERSON "WE" / THIRD PERSON / CONVERSATIONAL] voice.
```

**Expected output:** Organized FAQ document ready to publish, with strategic placement recommendations.

---

### 3. Complaint Resolution Framework

**When to use:** A customer is upset and you need to de-escalate while protecting your business.

**Prompt:**
```
I received this complaint from a customer:

"""
[PASTE THE COMPLAINT - email, review, social media comment, etc.]
"""

Context:
- Source: [EMAIL / SOCIAL MEDIA / REVIEW SITE / DIRECT MESSAGE]
- Customer history: [NEW CUSTOMER / REPEAT BUYER / HIGH-VALUE ACCOUNT]
- Is their complaint valid? [YES / PARTIALLY / NO]
- Our policy on this situation: [DESCRIBE]

Provide:
1. SEVERITY ASSESSMENT
   - Is this a one-off or a systemic issue?
   - Reputation risk level (low/medium/high)
   - Urgency (respond within hours / within a day / within a week)

2. RESPONSE DRAFT
   - If public (review/social): short, professional, move to private
   - If private (email/DM): detailed resolution
   - Acknowledge without over-apologizing
   - Offer a specific resolution (not "we'll look into it")

3. RESOLUTION OPTIONS (ranked)
   - Option A: [IDEAL for customer, what it costs us]
   - Option B: [BALANCED compromise]
   - Option C: [MINIMUM acceptable response]

4. FOLLOW-UP PLAN
   - When to check back
   - How to prevent this from happening again
   - Whether to update internal processes

Do not be a pushover. If the customer is wrong, the response should be respectful but firm.
```

**Expected output:** Severity assessment, ready-to-send response, resolution options with cost analysis.

---

### 4. Review Response Templates

**When to use:** You have reviews (positive and negative) on Google, Yelp, Amazon, or social media that need responses.

**Prompt:**
```
Write response templates for [BUSINESS NAME] reviews on [PLATFORM].

Our business: [DESCRIBE].

Create response templates for these scenarios:

POSITIVE REVIEWS:
1. Short positive review ("Great product!")
2. Detailed positive review (specific praise)
3. Positive review that mentions a staff member by name
4. Positive review from a repeat customer

NEGATIVE REVIEWS:
5. Legitimate complaint about product/service quality
6. Complaint about shipping/delivery
7. Complaint about pricing ("too expensive")
8. Unreasonable or unfair complaint
9. Competitor or fake review (subtle, not accusatory)

NEUTRAL REVIEWS:
10. Mixed review (some good, some bad)

Rules for all templates:
- Never copy-paste the same response to multiple reviews
- Include [BRACKETS] for customizable sections
- Keep positive responses under 50 words (don't over-explain)
- Keep negative responses under 100 words (acknowledge, resolve, move offline)
- Never argue. Never get defensive. Never blame the customer publicly.
- For negative reviews: always include a way to continue the conversation privately
- Sound like a real person, not a corporate PR team
```

**Expected output:** 10 customizable response templates covering every common review scenario.

---

### 5. Onboarding Email Sequence for New Customers

**When to use:** After purchase. The customer just bought and you need to prevent buyer's remorse, teach them the product, and set up a long-term relationship.

**Prompt:**
```
Create a post-purchase onboarding email sequence for [PRODUCT/SERVICE NAME].

Product type: [DIGITAL PRODUCT / PHYSICAL PRODUCT / SaaS / SERVICE].
Price point: [PRICE].
Biggest reason customers don't use what they bought: [DESCRIBE - e.g., "overwhelmed by features", "forgot about it"].

Write a 5-email sequence:

EMAIL 1 (Immediately after purchase):
- Confirm the purchase warmly
- Tell them exactly what to do first (one action, not five)
- Set expectations for what they'll receive and when

EMAIL 2 (Day 2):
- Quick win tutorial (the fastest way to see value)
- Address the #1 thing that confuses new customers

EMAIL 3 (Day 5):
- Deeper feature/use case they probably haven't tried
- Social proof from another customer who had the same starting point

EMAIL 4 (Day 10):
- Check in: "How's it going?"
- Offer help (link to FAQ, reply to this email, book a call)
- Subtle feedback request

EMAIL 5 (Day 21):
- Advanced tips / hidden features
- Referral or review request
- Cross-sell or upsell (only if genuinely useful, not pushy)

For each email:
- Subject line
- Body (under 200 words each)
- Single CTA
```

**Expected output:** 5-email onboarding sequence that reduces refunds and increases product usage.

---

### 6. Support Ticket Categorizer and Router

**When to use:** You're drowning in support tickets and need a system to triage them automatically.

**Prompt:**
```
I get support tickets for [BUSINESS NAME] through [EMAIL / HELPDESK / CHAT].

Here are 15-20 recent ticket subjects or first lines:

1. [PASTE]
2. [PASTE]
3. [PASTE]
...

Analyze these and create:

1. CATEGORY SYSTEM
   - Define 4-6 categories that cover 90%+ of tickets
   - For each category: name, description, example tickets, priority level

2. AUTO-RESPONSE TEMPLATES
   - For each category, write an immediate auto-response that:
     - Confirms receipt
     - Sets realistic timeline
     - Provides self-service links if applicable
     - Asks for specific info needed to resolve (if applicable)

3. ESCALATION RULES
   - Which categories need human response within 1 hour?
   - Which can wait 24 hours?
   - Which can be fully resolved with self-service?

4. KEYWORD TRIGGERS
   - List specific words/phrases that identify each category
   - These should be usable in email filters, Zapier/n8n triggers, or helpdesk rules

5. METRICS TO TRACK
   - What should I measure weekly to know if support is healthy?
```

**Expected output:** Complete ticket categorization system with auto-responses and routing rules.

---

### 7. Refund Request Handler

**When to use:** Someone wants a refund and you need to handle it professionally while protecting your revenue.

**Prompt:**
```
A customer is requesting a refund for [PRODUCT/SERVICE].

Details:
- Purchase date: [DATE]
- Amount: [AMOUNT]
- Reason given: [THEIR STATED REASON]
- Our refund policy: [DESCRIBE - e.g., "30-day no questions asked" or "case by case"]
- Have they used the product? [YES/NO/PARTIALLY]
- Customer history: [FIRST PURCHASE / REPEAT CUSTOMER / PREVIOUS REFUND REQUEST]

Provide 3 response options:

OPTION 1: FULL REFUND
- When this is the right call
- Response email (professional, no guilt-tripping)
- Follow-up actions (remove access, update records, etc.)

OPTION 2: ALTERNATIVE RESOLUTION
- Exchange, credit, extended access, or other alternatives
- Response email that presents the alternative genuinely, not as a bait
- When this works better than a refund for both sides

OPTION 3: DECLINE (only if policy supports it)
- Response email that's firm but not combative
- What to offer instead
- How to handle if they push back or threaten a chargeback

Also provide:
- Red flags that suggest refund fraud
- How to use this interaction to improve the product
- Whether this customer is worth saving (honest assessment)
```

**Expected output:** Three response options with complete email drafts and decision framework.

---

### 8. Knowledge Base Article Writer

**When to use:** You need help documentation that customers will actually read and that reduces support tickets.

**Prompt:**
```
Write a knowledge base article for [BUSINESS NAME] about:

Topic: [SPECIFIC TOPIC - e.g., "How to reset your password" or "Understanding your invoice"]

Audience: [TECHNICAL LEVEL - beginner / intermediate / advanced]
Product: [PRODUCT NAME]

Article structure:
1. Title (clear, matches what someone would search for)
2. One-line summary (what this article solves)
3. Prerequisites (what they need before starting, if any)
4. Step-by-step instructions
   - Numbered steps, one action per step
   - Include what they should SEE at each step (expected result)
   - Include screenshots descriptions [SCREENSHOT: description of what to capture]
5. Troubleshooting section
   - 3 common issues that happen during this process
   - Solution for each
6. Related articles (suggest 2-3 topics to link to)

Rules:
- Write at a 6th grade reading level
- No jargon without explanation
- Use "you" not "the user"
- Bold the clickable elements (button names, menu items)
- Keep it under 500 words (shorter articles get read)
```

**Expected output:** Ready-to-publish help article with screenshot placeholders and troubleshooting.

---

### 9. Customer Satisfaction Survey Builder

**When to use:** You need feedback but don't want a 20-question survey that nobody completes.

**Prompt:**
```
Create a customer satisfaction survey for [BUSINESS NAME].

Product/service: [DESCRIBE]
When this survey is sent: [AFTER PURCHASE / AFTER SUPPORT INTERACTION / QUARTERLY / AFTER CANCELLATION]
Goal: [WHAT SPECIFIC DECISION WILL THIS DATA INFORM?]

Build a survey with:
- Maximum 7 questions
- Estimated completion time under 2 minutes
- Mix of quantitative (1-5 scale) and qualitative (open text)

Questions should cover:
1. Overall satisfaction (NPS or CSAT format)
2. The specific thing we're trying to measure: [DESCRIBE]
3. What they value most (multiple choice, max 4 options)
4. What needs improvement (open text, but with a prompt that gets specific answers)
5. Likelihood to recommend or repurchase

Also provide:
- Survey introduction text (3 sentences max, explains why their input matters)
- Thank you message after completion
- Follow-up action plan:
  - Score 1-2: what to do immediately
  - Score 3: what to do within a week
  - Score 4-5: how to leverage these happy customers
- How to increase completion rate (subject line, timing, incentive suggestions)
```

**Expected output:** Complete survey with questions, intro copy, and action plan for each score range.

---

### 10. Churn Prevention Email Sequence

**When to use:** A customer is showing signs of leaving (inactive, downgraded, complained) and you want to save the relationship.

**Prompt:**
```
Create a churn prevention email sequence for [BUSINESS NAME].

Product: [DESCRIBE]
Monthly price: [PRICE]
What "at risk" looks like for us: [DEFINE - e.g., "hasn't logged in for 14 days" or "support ticket followed by silence"]

Write a 4-email win-back sequence:

EMAIL 1: THE CHECK-IN (Trigger: [INACTIVITY SIGNAL])
- Not salesy. Not "we miss you." Genuinely helpful.
- Acknowledge they might be busy or stuck
- Offer one specific piece of value (tip, resource, shortcut)
- Ask one direct question about their experience

EMAIL 2: THE VALUE REMINDER (3 days after Email 1, if no response)
- Show them what they're not using that other customers love
- Include a specific result or metric from an active customer
- Make it easy to re-engage (one-click action, not a 10-step process)

EMAIL 3: THE HONEST ASK (5 days after Email 2, if no response)
- Be direct: "Is [PRODUCT] still right for you?"
- Offer alternatives: pause instead of cancel, downgrade option, quick call
- No guilt. No manipulation. Real respect for their time and money.

EMAIL 4: THE DOOR IS OPEN (7 days after Email 3, if no response)
- Graceful exit
- Tell them what happens if they cancel (data retention, etc.)
- Leave the door open with a specific way to come back
- Optional: offer a genuine last incentive (discount, extended trial)

For each email: subject line, body (under 150 words), single CTA.
```

**Expected output:** 4-email churn prevention sequence with trigger conditions and graceful exit strategy.
