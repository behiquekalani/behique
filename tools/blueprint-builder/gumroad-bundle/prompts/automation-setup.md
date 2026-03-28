# Automation Setup Prompts
## 10 Battle-Tested Prompts for n8n, Zapier, and Integration Planning

---

### 1. Automation Audit and Priority Matrix

**When to use:** Before building anything. This maps every task in your business and tells you what to automate first.

**Prompt:**
```
I run [BUSINESS NAME] and I want to identify what to automate first.

Here's everything I do repeatedly (be honest, include the boring stuff):

1. [TASK - e.g., "respond to customer emails"]
2. [TASK - e.g., "post on social media 3x/week"]
3. [TASK - e.g., "send invoices"]
4. [TASK - e.g., "check competitor prices"]
5. [TASK - e.g., "update spreadsheet with orders"]
6. [TASK - e.g., "follow up with leads who haven't replied"]
7. [TASK - e.g., "generate weekly reports"]
8. [TASK - e.g., "onboard new customers"]

For each task, score it on:
- Time spent per week (hours)
- Complexity (1-5, where 1 = simple rules, 5 = requires judgment)
- Error rate when done manually (low/medium/high)
- Revenue impact if faster (low/medium/high)
- Automation difficulty (easy/medium/hard)

Then rank them using this formula: (Time * Revenue Impact) / Automation Difficulty

Output:
1. Priority matrix table (ranked)
2. "Automate this week" (top 3, easiest + highest impact)
3. "Automate this month" (next 3)
4. "Keep manual for now" (requires too much judgment or too complex)
5. Estimated hours saved per week if top 5 are automated
6. Recommended tools for each automation (n8n, Zapier, Make, Python script, or native integration)
```

**Expected output:** Prioritized automation roadmap with tool recommendations.

---

### 2. n8n Workflow Designer

**When to use:** You know what you want to automate in n8n but need the workflow architecture before you start clicking nodes.

**Prompt:**
```
Design an n8n workflow for this automation:

WHAT IT SHOULD DO:
[DESCRIBE THE FULL PROCESS - e.g., "When a new order comes in on Shopify, check if the customer exists in our Notion database. If new, add them. If existing, update their order count. Then send a personalized thank-you email based on whether it's their 1st, 3rd, or 10th order."]

TOOLS INVOLVED:
- [TOOL 1 - e.g., Shopify]
- [TOOL 2 - e.g., Notion]
- [TOOL 3 - e.g., Gmail/SendGrid]

TRIGGER: [WEBHOOK / SCHEDULE / MANUAL / EVENT-BASED]

Provide:
1. WORKFLOW ARCHITECTURE
   - Node-by-node breakdown in order
   - Node type for each (HTTP Request, IF, Switch, Set, Function, etc.)
   - What each node does in plain English

2. DATA FLOW
   - What data comes in at the trigger
   - How data transforms at each step
   - What the final output/action is

3. ERROR HANDLING
   - What happens if [TOOL] is down?
   - What happens if data is malformed?
   - Where to add error notification nodes
   - Retry logic recommendations

4. CONDITIONAL LOGIC
   - IF/Switch conditions needed
   - Edge cases to handle

5. n8n-SPECIFIC TIPS
   - Which nodes to use (built-in vs HTTP Request)
   - Expression syntax for data mapping
   - Where to use the Function node vs Set node
   - Credential setup notes

Do NOT give me pseudocode. Give me a workflow I can build node-by-node in n8n.
```

**Expected output:** Complete n8n workflow blueprint, node-by-node, ready to build.

---

### 3. Zapier Multi-Step Zap Builder

**When to use:** Building a Zapier automation and need to plan the steps before wasting time on trial and error.

**Prompt:**
```
Design a Zapier automation (Zap) for:

GOAL: [DESCRIBE - e.g., "When someone fills out my Typeform, add them to a specific Mailchimp segment based on their answers, create a task in Todoist for follow-up, and log the submission in Google Sheets"]

Apps involved:
- Trigger app: [APP]
- Action apps: [APP 1, APP 2, APP 3]

Build out:
1. TRIGGER
   - App + specific trigger event
   - What data becomes available from the trigger

2. STEPS (in order)
   - Step type (Action, Search, Filter, Path, Formatter, Delay)
   - App and action for each step
   - Field mapping (which trigger data goes where)
   - Formatter steps needed (dates, text, numbers)

3. PATHS (if conditional logic needed)
   - Condition for each path
   - Actions within each path

4. FILTER STEPS
   - When should this Zap NOT continue?
   - Filter conditions

5. TESTING CHECKLIST
   - Sample data to test with
   - What to verify at each step
   - Common failures and fixes

6. COST ESTIMATE
   - Number of tasks per run
   - Estimated monthly runs
   - Which Zapier plan this requires

Keep it practical. If a simpler approach exists (fewer steps, native integration instead), suggest that instead.
```

**Expected output:** Step-by-step Zap blueprint with field mappings and cost estimate.

---

### 4. API Integration Planner

**When to use:** You need to connect two services that don't have a native integration, and you need to plan the API calls.

**Prompt:**
```
I need to connect [SERVICE A] to [SERVICE B]. There's no native integration.

What I need to happen:
[DESCRIBE THE DATA FLOW - e.g., "When a payment is confirmed in Stripe, create a new row in Airtable with the customer name, email, amount, and date"]

For each service, I have access to:
- [SERVICE A]: [API / WEBHOOK / CSV EXPORT / SCRAPING]
- [SERVICE B]: [API / WEBHOOK / IMPORT / FORM]

Plan the integration:

1. DATA MAPPING
   - Fields from Service A -> Fields in Service B
   - Data type conversions needed (dates, currencies, etc.)
   - Required fields vs optional fields

2. API CALLS NEEDED
   - Endpoint URLs (or where to find them in docs)
   - HTTP method (GET/POST/PUT/PATCH)
   - Authentication type (API key, OAuth, Bearer token)
   - Request headers
   - Request body structure (JSON example)
   - Expected response structure

3. IMPLEMENTATION OPTIONS (ranked by complexity)
   - Option A: n8n/Zapier/Make (no code)
   - Option B: Python script (low code)
   - Option C: Custom webhook handler (code)
   - Recommend the best option for my skill level: [BEGINNER/INTERMEDIATE/ADVANCED]

4. RATE LIMITS AND GOTCHAS
   - API rate limits for each service
   - Pagination handling if pulling lists
   - Webhook reliability (do they retry on failure?)

5. TESTING APPROACH
   - How to test without affecting production data
   - Sample request/response to validate
```

**Expected output:** Complete integration plan with API details, data mapping, and implementation recommendation.

---

### 5. Email Automation Workflow Builder

**When to use:** Setting up automated email flows that go beyond basic "send on signup." Covers lead nurturing, re-engagement, and transactional.

**Prompt:**
```
Design an email automation workflow for [BUSINESS NAME].

Email tool: [MAILCHIMP / CONVERTKIT / SENDGRID / RESEND / OTHER]
Workflow type: [LEAD NURTURE / POST-PURCHASE / RE-ENGAGEMENT / CART ABANDONMENT / ONBOARDING]

Context:
- What triggers this workflow: [DESCRIBE - e.g., "user signs up for free trial"]
- Goal of the workflow: [DESCRIBE - e.g., "convert free trial to paid within 14 days"]
- Audience: [WHO ENTERS THIS WORKFLOW]

Build the complete workflow:

1. TRIGGER CONDITIONS
   - Entry trigger
   - Entry filters (who should NOT enter this workflow)
   - Can someone enter this workflow more than once?

2. WORKFLOW MAP (visual-style, step by step)
   - Each email: timing, subject, goal
   - Decision points: what determines the next step?
   - Exit conditions: when does someone leave the workflow?
   - Wait steps: how long between each action?

3. SEGMENTATION LOGIC
   - How to split the audience mid-workflow
   - Tags or properties to set at each step
   - How this workflow connects to other workflows

4. TRACKING AND METRICS
   - Open rate benchmarks for this type of workflow
   - Click rate benchmarks
   - Conversion events to track
   - When to consider this workflow "broken" and needs fixing

5. A/B TEST SUGGESTIONS
   - Which email to test first
   - What to test (subject line, send time, CTA, length)
   - Minimum sample size needed

Include a simple ASCII diagram of the workflow flow.
```

**Expected output:** Complete email automation blueprint with decision logic, timing, and benchmarks.

---

### 6. Data Pipeline Designer

**When to use:** You need to move data between systems automatically, whether it's daily reports, syncing databases, or aggregating from multiple sources.

**Prompt:**
```
Design a data pipeline for [DESCRIBE THE PURPOSE].

Source(s): [WHERE DATA COMES FROM - e.g., "Shopify orders API, Google Analytics, manual CSV uploads"]
Destination: [WHERE DATA NEEDS TO GO - e.g., "Google Sheets dashboard, Notion database, PostgreSQL"]
Frequency: [REAL-TIME / HOURLY / DAILY / WEEKLY]
Volume: [APPROXIMATE ROWS/RECORDS PER RUN]

Build the pipeline:

1. EXTRACTION
   - How to pull data from each source
   - Authentication required
   - Data format received (JSON, CSV, XML)
   - Pagination or batch handling needed?

2. TRANSFORMATION
   - Fields to keep, rename, or discard
   - Calculations or aggregations needed
   - Data cleaning rules (nulls, duplicates, formatting)
   - Joins between data sources (how to match records)

3. LOADING
   - How to write to the destination
   - Append vs. overwrite vs. upsert
   - Schema/structure at the destination

4. SCHEDULING
   - When to run
   - How to trigger (cron, webhook, manual)
   - Expected runtime

5. MONITORING
   - How to know if a run failed
   - Data quality checks (row counts, null checks)
   - Alerting (email, Slack, Telegram notification)

6. TOOL RECOMMENDATION
   - Best tool for this pipeline: n8n / Python script / Airbyte / custom
   - Why this tool over alternatives
   - Setup time estimate

Show the pipeline as a simple flow diagram using ASCII or text.
```

**Expected output:** End-to-end data pipeline specification with tool recommendation.

---

### 7. Chatbot/Bot Architecture Planner

**When to use:** Before building a Telegram bot, Discord bot, Slack bot, or website chatbot. Plan the conversation flows and integrations first.

**Prompt:**
```
Design a bot for [PLATFORM: Telegram / Discord / Slack / Website chat].

Purpose: [WHAT THE BOT DOES - e.g., "customer support triage", "idea capture and categorization", "order status lookup"]

Target users: [WHO USES IT]

Plan the bot:

1. COMMANDS AND TRIGGERS
   - List every command the bot responds to
   - For each: trigger word/command, what it does, example interaction
   - Natural language inputs it should understand (if applicable)

2. CONVERSATION FLOWS
   - Map out 3-5 main conversation paths
   - For each path: user input -> bot response -> next options
   - Include error/fallback responses ("I didn't understand that")
   - Where does the conversation end?

3. INTEGRATIONS
   - What external services does the bot talk to?
   - Data it sends out (and to where)
   - Data it pulls in (and from where)

4. DATA STORAGE
   - What does the bot need to remember?
   - Where to store it (database, JSON file, Notion, Google Sheets)
   - Per-user data vs. global data

5. TECH STACK RECOMMENDATION
   - Language: [Python / Node.js / Go]
   - Bot framework/library
   - Hosting: [Railway / Render / VPS / serverless]
   - AI integration (if using LLM for responses): which model and why
   - Estimated monthly hosting cost

6. MVP SCOPE
   - What to build in v1 (minimum to be useful)
   - What to add in v2
   - What to save for later
```

**Expected output:** Complete bot architecture document, from commands to hosting, with MVP scope.

---

### 8. Notification and Alerting System Designer

**When to use:** You want to know when important things happen in your business without checking 10 dashboards manually.

**Prompt:**
```
Design a notification/alerting system for [BUSINESS NAME].

Events I need to know about:
1. [EVENT - e.g., "new sale over $100"]
2. [EVENT - e.g., "customer complaint received"]
3. [EVENT - e.g., "inventory below 5 units"]
4. [EVENT - e.g., "website goes down"]
5. [EVENT - e.g., "new signup from ad campaign"]
6. [EVENT - e.g., "daily revenue summary at 9pm"]

For each event:

1. SOURCE
   - Where does this event originate?
   - How to detect it (webhook, API poll, email parse, log monitor)

2. ROUTING
   - Where should the notification go? (Telegram, Slack, email, SMS, push)
   - Why this channel for this event type
   - Who else should be notified (if anyone)

3. URGENCY LEVELS
   - Critical (need to act NOW): which events?
   - Important (within a few hours): which events?
   - Informational (daily digest is fine): which events?

4. NOTIFICATION FORMAT
   - Template for each alert (what info to include)
   - Keep it scannable on mobile

5. IMPLEMENTATION
   - Tools needed (n8n, Zapier, UptimeRobot, custom script)
   - Connection diagram (source -> processor -> channel)
   - Estimated setup time for each alert

6. ANTI-NOISE RULES
   - Rate limiting (don't send 50 alerts for the same issue)
   - Grouping (batch low-priority alerts into daily summary)
   - Quiet hours (when NOT to send non-critical alerts)
```

**Expected output:** Complete alerting system with routing rules, templates, and anti-noise configuration.

---

### 9. CRM Automation Workflow

**When to use:** You have leads coming in and no system to track, nurture, and close them without manual follow-up.

**Prompt:**
```
Design a CRM automation workflow for [BUSINESS NAME].

Current CRM (or what you want to use): [NOTION / AIRTABLE / HUBSPOT / PIPEDRIVE / GOOGLE SHEETS / NONE YET]
Lead sources: [WHERE LEADS COME FROM - website form, DMs, email, referrals]
Sales cycle length: [DAYS/WEEKS/MONTHS]
Team size: [SOLO / 2-5 / 5+]

Build the system:

1. LEAD CAPTURE
   - How each lead source feeds into the CRM
   - Required fields to capture
   - Auto-tagging rules (source, category, priority)

2. PIPELINE STAGES
   - Define 5-7 stages from first contact to closed deal
   - Exit criteria for each stage (what needs to happen to move forward)
   - How long a lead should stay in each stage before a flag is raised

3. AUTOMATED ACTIONS AT EACH STAGE
   - Stage 1: [Auto-send welcome email, assign to rep]
   - Stage 2: [Schedule follow-up task, add to email sequence]
   - etc.

4. FOLLOW-UP AUTOMATION
   - Auto-reminder if no response in X days
   - Follow-up email templates for each stage
   - When to stop following up (dead lead criteria)

5. REPORTING
   - Pipeline value
   - Conversion rate per stage
   - Average time in each stage
   - Lead source performance

6. TOOL CONNECTIONS
   - What connects to what (diagram)
   - n8n/Zapier workflows needed
   - Estimated setup time
```

**Expected output:** Complete CRM automation system with pipeline design, automation triggers, and reporting.

---

### 10. Workflow Documentation Template

**When to use:** After building any automation. Documents what you built so future-you (or your team) can maintain it.

**Prompt:**
```
I built this automation and need to document it so someone else (or future me) can understand, maintain, and troubleshoot it.

Automation name: [NAME]
What it does: [ONE SENTENCE]
Tool used: [n8n / Zapier / Python / Make / custom]

Generate documentation covering:

1. OVERVIEW
   - Purpose (why this exists)
   - Trigger (what starts it)
   - End result (what it produces/does)
   - Frequency (how often it runs)

2. WORKFLOW STEPS
   - Step-by-step breakdown
   - For each step: what happens, what data is used, what's output
   - Decision points and conditional logic

3. CREDENTIALS AND ACCESS
   - Which accounts/API keys are used (DO NOT include actual keys)
   - Where credentials are stored
   - Who has access

4. FAILURE MODES
   - What can go wrong at each step
   - How the system handles each failure
   - What requires manual intervention
   - How to restart after a failure

5. MAINTENANCE
   - What to check monthly
   - API changes or deprecations to watch for
   - When to update credentials (expiration dates)

6. MODIFICATION GUIDE
   - How to add a new [step/filter/output]
   - What NOT to change without testing
   - Testing procedure before going live with changes

7. CONTACTS
   - Who built this
   - Who to contact if it breaks
   - Related documentation or workflows

Format this as a clean, scannable document with headers and bullet points.
```

**Expected output:** Complete automation documentation, ready to store in your team wiki or knowledge base.
