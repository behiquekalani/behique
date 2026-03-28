# n8n for Solopreneurs
## The No-Code Automation Playbook for One-Person Businesses

**Price:** $29.99
**Target audience:** Solopreneurs, freelancers, and creators who want to automate repetitive work without hiring developers.
**What you will have after this guide:** A running n8n instance with at least 5 production-ready workflows that handle your content pipeline, lead capture, client onboarding, reporting, and e-commerce operations automatically.

---

## Introduction: Why n8n Over Zapier

If you have been automating your business with Zapier, you have probably hit the wall. The free tier runs out fast. The paid tiers are priced for teams, not solo operators. And the most powerful features, multi-step workflows, branching logic, and code nodes, are locked behind the most expensive plans.

n8n is different. It is open source. You can self-host it for the cost of a small cloud server, typically $5 to $10 per month on Railway or Render. There are no task limits. There are no workflow limits. You own the infrastructure and the data.

The capability gap is also significant. Where Zapier gives you linear workflows (do A, then B, then C), n8n gives you a full visual programming environment. You can branch based on conditions, loop through lists, write JavaScript inside nodes, call AI APIs mid-workflow, and handle errors with custom logic. For a one-person business building real automation, that flexibility matters.

The trade-off is a steeper learning curve. Zapier is faster to set up for simple tasks. n8n requires you to understand how data flows between nodes. This guide closes that gap. By the time you finish Part 1, you will have the mental model. By Part 3, you will have a production workflow running. The rest of the guide builds on that foundation.

A note on hosting: you can use n8n Cloud (paid, no self-hosting required) or self-host on Railway, Render, or a VPS. Instructions for both are in Chapter 10. For this guide, the workflow logic is identical regardless of how you host.

---

## Chapter 1: n8n Fundamentals

### Nodes

Every action in n8n is a node. A node is a self-contained unit that does one thing: sends an email, reads a spreadsheet row, calls an API, waits for a webhook, runs a code block. Nodes are connected to each other by drawing lines between them. Data flows along those lines from one node to the next.

There are three categories of nodes you will use constantly:

**Trigger nodes** start a workflow. Common triggers: Webhook (receives an HTTP request), Schedule Trigger (runs at a set time), Email Trigger (fires when a new email arrives), and app-specific triggers like "New row in Airtable" or "New subscriber in ConvertKit."

**Action nodes** do the work. Common examples: Send Email (Gmail, SMTP), Create Page (Notion), HTTP Request (call any API), OpenAI (call GPT-4 or Whisper), Code (run JavaScript), Set (create or transform data variables), If (branch on a condition), and Merge (combine data from multiple branches).

**Utility nodes** shape the flow. Split In Batches processes lists one item at a time. Wait pauses the workflow. Function Item transforms each item in a list independently.

### Workflows

A workflow is a connected sequence of nodes. It has one trigger and any number of actions. When the trigger fires, data flows from left to right through the connected nodes. Each node receives the output of the previous one, transforms or acts on it, and passes its own output forward.

Workflows can be activated (running in production) or deactivated (stopped). You build and test in deactivated mode. You turn them on in activated mode.

### Triggers

The trigger determines when the workflow runs. Understanding triggers is critical because the trigger determines what data the workflow starts with.

A Webhook trigger gives you a URL. When something sends an HTTP POST to that URL, the workflow starts with the payload data that was sent. This is how most third-party tools connect to n8n.

A Schedule trigger runs the workflow at a specified interval. Every day at 8am. Every Monday. Every 30 minutes. The workflow starts with no input data except the timestamp.

An app trigger (like "New Gmail") continuously monitors an external service and fires when the condition is met.

### Credentials

To connect n8n to external services, you need credentials. API keys, OAuth tokens, usernames and passwords. These are stored securely in n8n's credential manager and referenced by name inside nodes. You set them up once and reuse them across all workflows.

The first step with any new service is creating the credential. For Gmail: OAuth2. For Notion: API key. For OpenAI: API key. For ConvertKit: API key plus secret.

---

## Chapter 2: Your First Workflow

### RSS to Notion in 10 Minutes

This workflow monitors an RSS feed and saves new items to a Notion database. It is simple enough to build in 10 minutes and teaches you the core mechanics of every workflow you will ever build.

**What you need before you start:**
- A Notion account with a database that has Title, URL, Published Date, and Summary fields
- A Notion integration token (created at notion.so/my-integrations)
- An RSS feed URL (use any blog or news source you read regularly)
- An OpenAI API key (optional, for the summary step)

**Step 1: Create the workflow**
Open n8n. Click "New Workflow." Give it a name: RSS to Notion.

**Step 2: Add the Schedule Trigger**
Click the + button. Search for "Schedule." Select "Schedule Trigger." Set it to run every day at 9am. This node has no configuration beyond the schedule. It will fire once per day and pass an empty data object to the next node.

**Step 3: Add the RSS Feed Read node**
Click the + button after the Schedule Trigger. Search for "RSS Feed Read." Set the Feed URL to your chosen RSS feed. Set "Return All" to true if you want all available items, or set a limit of 5 to 10 for daily monitoring.

This node will output an array of feed items. Each item has a title, link, pubDate, content, and creator field.

**Step 4: Add the Split In Batches node**
The RSS node returns all items at once. To process each item individually, add a "Split In Batches" node with Batch Size set to 1. This loops through each item one at a time so the next nodes process one article per pass.

**Step 5 (optional): Add the OpenAI node for summaries**
Add an OpenAI node. Set the operation to "Message a Model." Model: gpt-4o-mini (fast and cheap). In the prompt field: "Summarize this article in 2 sentences for a busy reader. Article: {{$json.content}}". The {{$json.content}} pulls the article content from the previous node's output.

**Step 6: Add the Notion node**
Add a Notion node. Credential: your Notion integration token. Operation: Create. Database: your RSS database. Map the fields:
- Title: {{$json.title}}
- URL: {{$json.link}}
- Published Date: {{$json.pubDate}}
- Summary: {{$json["message"]["content"]}} (the OpenAI output, if you added that step)

**Step 7: Test**
Click "Test Workflow." n8n will execute each node and show you the data at each step. Check that the Notion database received a new row. If it did, the workflow is working.

**Step 8: Activate**
Toggle the workflow to Active. It will now run automatically every day at 9am without any action from you.

This workflow taught you triggers, node chaining, array processing, API calls, and output mapping. Every workflow you build in this guide uses the same pattern.

---

## Chapter 3: The Content Automation Stack

### YouTube to Newsletter to Social Media Pipeline

This is the workflow that reclaims the most time for content creators. One YouTube video upload triggers a chain that produces a newsletter draft, tweet ideas, and an Instagram caption, all saved to Notion for review and approval.

**The full node chain:**

1. **YouTube Trigger** (or HTTP Request polling the YouTube API): fires when a new video is published on your channel. Outputs: video ID, title, description, published date.

2. **HTTP Request node (Whisper API)**: sends the video's audio file URL to OpenAI's Whisper API. Returns the full transcript text.

3. **OpenAI node (Newsletter)**: prompt: "You are a newsletter writer. Take this video transcript and rewrite it as a 400-word newsletter section. Keep the author's voice. Use short paragraphs. Add a conclusion with one clear takeaway. Transcript: {{$json.transcript}}"

4. **OpenAI node (Tweets)**: prompt: "Extract 5 tweet-sized insights from this transcript. Each tweet should be under 280 characters, standalone, and provocative. Format as a numbered list. Transcript: {{$json.transcript}}"

5. **OpenAI node (Instagram Caption)**: prompt: "Write a 150-word Instagram caption for this video content. Thesis first. End with a question. No hashtags. Transcript: {{$json.transcript}}"

6. **Notion node**: creates a new page in your Content database with separate text blocks for the transcript, newsletter draft, tweet ideas, and caption draft. Adds a "Needs Review" status.

7. **Gmail node**: sends you an email notification: "New content drafts ready for {{$json.title}}. Review in Notion: [link]"

**Practical configuration notes:**

The YouTube Trigger requires a YouTube API credential (OAuth2). Set up in Google Cloud Console. The Whisper transcription step requires either the video's audio as a URL or a download-and-upload flow using an HTTP Request node. For most creators, a simpler path is to upload the transcript manually to a Notion page and trigger from there, or use a webhook from your editing tool.

The three OpenAI nodes run in parallel using the Merge node afterward. Set Merge mode to "Wait for All" so the Notion page creation happens only after all three AI nodes complete.

**Approval gate:** Add an If node before posting anything publicly. The condition: Notion status equals "Approved." The workflow checks this field before any publish action runs. You review the drafts in Notion, update the status, and the workflow handles distribution automatically.

---

## Chapter 4: Lead Capture Automation

### Form to Email Sequence to CRM

Every lead who opts in deserves a fast, consistent, professional response. This workflow delivers that without your involvement.

**Trigger:** Tally.so form submission via Webhook. Configure the Webhook URL in your Tally form settings under Integrations.

**Node sequence:**

1. **Webhook node**: receives the form payload. Outputs: name, email, source (which form or landing page), and any qualifying fields you included.

2. **Set node**: normalize the data. Create clean variables: leadName, leadEmail, leadSource, leadDate. This makes downstream nodes easier to configure.

3. **ConvertKit node (HTTP Request)**: POST to the ConvertKit API to create a subscriber. Include the leadSource as a tag. This automatically enrolls them in the correct email sequence based on the tag.

4. **Notion node**: creates a row in your Leads database. Fields: Name, Email, Source, Date, Status (default: New).

5. **Gmail node**: sends the welcome email. Subject: "Here's your [lead magnet name], [leadName]." Body: personalized welcome text with the download link attached or linked. Include your intro and what to expect next.

6. **Conditional branch (If node)**: if leadSource equals "High Intent" (for example, a pricing page opt-in), route to an additional Slack notification so you can follow up personally.

7. **Slack node** (optional branch): sends a message to your #leads Slack channel with the lead's name, email, source, and a Notion link. Keeps you informed without requiring you to monitor anything.

**Key configuration detail:** The ConvertKit tag controls which email sequence the lead enters. Create a tag for each opt-in source (lead-magnet-free-tools, lead-magnet-checklist, etc.) and set up matching sequences in ConvertKit. The n8n workflow handles the tagging automatically based on which form was submitted.

---

## Chapter 5: Client Onboarding Automation

When a client pays, every subsequent touchpoint should feel immediate and professional. Delays in onboarding create anxiety and reduce confidence. Automation eliminates delays.

**Trigger:** Gumroad Sale Webhook or Stripe Webhook. Both services allow you to configure a webhook URL that fires on every completed payment.

**Node sequence:**

1. **Webhook node**: receives payment data. Outputs: buyer name, buyer email, product name, amount, date.

2. **Set node**: creates clean variables. Also generates a unique client ID if needed (use the Expression editor: {{$now.toMillis()}}).

3. **Notion node (Create client workspace)**: duplicates a template page in your Notion workspace. The Notion API supports creating pages from parent database entries. Set the page title to the client's name, status to Active, and populate contact fields from the webhook data.

4. **HTTP Request node (DocuSign or HelloSign)**: sends the contract template pre-filled with the client's name and email. Both services have REST APIs that accept template IDs and signer information.

5. **Gmail node (Welcome email)**: sends the onboarding email. Include: welcome message, Notion workspace link, kickoff call scheduling link (Calendly), and what happens in the first 7 days.

6. **Gmail node (Contract notification)**: separate email explaining the contract that was sent and how to sign it.

7. **Slack node**: notifies your #clients channel: "New client onboarded: [Name]. Product: [Product]. Notion: [link]."

**Template management in Notion:** Keep a "Client Template" page in Notion that is never used directly. The n8n workflow duplicates it for each new client using the Notion API's page copy functionality. Every client starts with the same structured workspace.

---

## Chapter 6: Social Listening Workflows

Knowing what is being said about your niche, your brand, and your competitors in real time gives you a material content and business advantage.

**Workflow 1: RSS-based keyword monitoring**

1. **Schedule Trigger**: runs every 4 hours.
2. **RSS Feed Read node**: monitors Google Alerts RSS feeds for your brand name, your product names, and key competitors. Create Google Alerts at google.com/alerts and select "RSS feed" as the delivery method.
3. **Split In Batches**: processes one alert at a time.
4. **If node**: filters for items not already in your Notion database. Use a Set node to create a hash of the URL and check it against a Notion query.
5. **OpenAI node**: classifies the mention: Brand Mention, Competitor Mention, Industry News, or Opportunity. Prompt: "Classify this article. Categories: Brand Mention, Competitor Mention, Industry News, Opportunity. Article title: {{$json.title}}. Article snippet: {{$json.content:snippet}}"
6. **Notion node**: saves to your Social Listening database with category, source, date, and link.
7. **Conditional Slack notification**: if the category is Brand Mention or Opportunity, send a Slack message immediately.

**Workflow 2: Reddit monitoring**

The HTTP Request node can query the Reddit API without authentication for public subreddit data. Use the endpoint https://www.reddit.com/r/[subreddit]/search.json?q=[keyword]&sort=new&t=day to retrieve recent posts mentioning your keywords. Process with the same classification and storage logic as Workflow 1.

---

## Chapter 7: The Weekly Reporting Workflow

Your business generates data constantly. Without a system to surface it, you are flying blind. This workflow assembles your weekly numbers automatically and delivers them on Sunday evening so Monday starts with clarity.

**Schedule Trigger:** every Sunday at 8pm.

**Parallel data collection (all HTTP Request nodes running simultaneously via Merge):**

- YouTube Analytics API: views, watch time, subscribers gained this week
- Gumroad API: sales count, revenue, top product this week
- ConvertKit API: new subscribers, open rate on last email, unsubscribes
- Instagram Basic Display API: follower count, reach on recent posts

**OpenAI node (synthesis):** receives all data and generates a plain-language summary. Prompt: "You are a business analyst for a one-person content business. Here is this week's data: [data]. Write a 200-word summary covering: what grew, what declined, what needs attention, and one recommended action for next week."

**Notion node:** updates your Weekly Dashboard database with all metrics and the AI summary.

**Gmail node:** sends the report to yourself. Subject: "Weekly Report: [date range]". Body: the metrics table and the AI summary. This means you can read it from your phone without opening Notion.

**Key node configuration:** Use the Merge node in "Wait for All" mode to collect all API responses before passing to the OpenAI synthesis step. This prevents partial reports.

---

## Chapter 8: E-commerce Automation

For a Gumroad or Shopify-based product business, the customer journey after purchase matters as much as the purchase itself.

**Trigger:** Gumroad sale webhook or Shopify order webhook.

**Node sequence:**

1. **Webhook node**: receives order data. Outputs: customer name, email, product, amount, date.

2. **Set node**: normalizes data. Determines product category for routing (digital download, coaching, template pack, etc.).

3. **Gmail node (Order confirmation)**: sends confirmation email immediately. Include: order summary, delivery method, expected timeline, and support contact.

4. **Conditional branch (product type):** digital products get a direct download link appended to the confirmation. Physical products (if applicable) get a fulfillment notification trigger.

5. **ConvertKit node**: tags the buyer by product purchased. They enter the post-purchase sequence specific to that product.

6. **Wait node (set to 3 days)**: pauses the workflow.

7. **Gmail node (Check-in)**: sends a 3-day check-in email. "How is [product name] working for you? Here are three things most people try first." This reduces refunds and increases reviews.

8. **Wait node (set to 7 days from the 3-day email)**: another pause.

9. **Gmail node (Review request)**: asks for a testimonial or Gumroad review. Include the review link directly.

10. **Notion node**: logs the full customer journey to your Customer database.

**Revenue tracking:** Add an aggregation step that updates a running revenue total in a Notion formula database. This gives you a live revenue dashboard without any manual entry.

---

## Chapter 9: AI-Powered Workflows

n8n integrates with OpenAI, Anthropic, and any AI service that has a REST API. The combination of workflow logic and AI reasoning opens up automation possibilities that are genuinely new.

**Using the OpenAI node:**

The OpenAI node in n8n supports Chat completions, Embeddings, Image generation, and Audio transcription (Whisper). For most solopreneur use cases, Chat completions with gpt-4o-mini (fast, cheap, capable) is the right default.

Key configuration options:
- **Model**: gpt-4o-mini for speed and cost, gpt-4o for complex reasoning tasks
- **System prompt**: set your persistent role instruction here. "You are a conversion copywriter for a digital product business targeting solopreneurs."
- **User message**: the dynamic content you want processed, built with n8n's expression syntax
- **Temperature**: 0.7 for creative tasks, 0.2 for classification and extraction tasks

**Using Claude via HTTP Request node:**

Anthropic does not have a native n8n node yet. Use the HTTP Request node to call the Anthropic API directly.

URL: https://api.anthropic.com/v1/messages
Method: POST
Headers:
- x-api-key: your Anthropic API key
- anthropic-version: 2023-06-01
- content-type: application/json

Body (JSON):
```json
{
  "model": "claude-3-5-haiku-20241022",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "{{$json.your_input_field}}"
    }
  ]
}
```

**Using Whisper for voice-to-text:**

The OpenAI node's audio transcription operation accepts a binary file input. To transcribe a voice memo, first download the file with an HTTP Request node or a Google Drive node, then pass it to the OpenAI node set to Transcribe Audio. The output is the transcript text, ready to pass into subsequent AI processing nodes.

**Practical AI workflow patterns:**

- Classification: use AI to categorize inputs (form submissions, emails, support tickets) so different types route to different workflows automatically
- Extraction: pull structured data from unstructured text (customer email to extract name, issue, urgency, and product mentioned)
- Generation with review gate: generate first drafts automatically but require human approval before they are published or sent
- Summarization: condense long inputs (transcripts, reports, long emails) before they are logged to Notion

---

## Chapter 10: Hosting and Maintenance

### Option 1: n8n Cloud

n8n Cloud is the managed hosting option. You sign up at app.n8n.cloud, pay a monthly fee (starts around $20/month for the Starter tier), and get a hosted n8n instance with no setup required. This is the right choice if you want to skip infrastructure entirely and focus on building workflows.

Limitations: task limits on lower tiers, no custom code without upgrading, slightly less flexibility than self-hosted.

### Option 2: Railway (Recommended Self-Host)

Railway is the simplest way to self-host n8n. The deployment takes about 10 minutes.

1. Create a Railway account at railway.app
2. Create a new project. Select "Deploy from GitHub repo" or use Railway's template library. Search for "n8n" in the template library and deploy.
3. Set environment variables: N8N_BASIC_AUTH_ACTIVE=true, N8N_BASIC_AUTH_USER=your-username, N8N_BASIC_AUTH_PASSWORD=your-password, N8N_HOST=your-railway-domain, WEBHOOK_URL=https://your-railway-domain
4. Railway assigns a public URL. Use that URL as your n8n instance URL and your webhook base URL.

Estimated cost: $5 to $10 per month depending on usage.

### Option 3: VPS (Advanced)

A $6/month VPS from Hetzner, DigitalOcean, or Vultr can self-host n8n using Docker. This gives maximum control but requires comfort with Linux command line, Docker, and basic nginx configuration for SSL. Not recommended unless you have prior server administration experience.

### Keeping it running

**Backups:** Export your workflows regularly (Settings, Export Workflows) and save them to a Notion page or GitHub repository. If your instance goes down, you can re-import in minutes.

**Monitoring:** Set up a free UptimeRobot account and point it at your n8n URL. It will notify you if the instance goes offline.

**Updates:** n8n releases updates frequently. For Railway, redeploy from the latest image monthly. Most updates are backwards compatible.

**Credential rotation:** When API keys expire or are rotated, update them in n8n's credential manager (Settings, Credentials). You do not need to reconfigure any workflows. All nodes that use that credential pick up the change automatically.

---

## Appendix A: 10 Ready-to-Deploy Workflow Templates

### Template 1: Daily Analytics Digest
**Trigger:** Schedule Trigger (daily 8am). **Nodes:** YouTube API, Gumroad API, ConvertKit API, Merge, OpenAI (summarize), Gmail. **Output:** daily metrics summary in your inbox.

### Template 2: New Lead Notification
**Trigger:** Tally.so Webhook. **Nodes:** Set (normalize), Notion (add row), ConvertKit (tag subscriber), Gmail (welcome email). **Output:** lead captured, tagged, and welcomed automatically.

### Template 3: Product Launch Email Sequence Trigger
**Trigger:** Notion database update (status changed to "Launch Ready"). **Nodes:** If (check date), ConvertKit (activate sequence). **Output:** email sequence activates when you update a Notion field.

### Template 4: Blog Post to Social Content
**Trigger:** Webhook from your CMS. **Nodes:** HTTP Request (fetch post content), OpenAI (tweet ideas), OpenAI (LinkedIn post), OpenAI (Instagram caption), Notion (save all drafts). **Output:** three social drafts ready for review in Notion.

### Template 5: Competitor Product Monitor
**Trigger:** Schedule Trigger (daily). **Nodes:** HTTP Request (scrape competitor Gumroad), If (new product detected), Slack (notify), Notion (log). **Output:** instant Slack alert when a competitor launches a new product.

### Template 6: Voice Memo to Task List
**Trigger:** Webhook from iOS Shortcut (records and sends audio). **Nodes:** OpenAI (Whisper transcription), OpenAI (extract action items), Notion (create tasks). **Output:** voice memo becomes a structured task list in Notion.

### Template 7: Weekly Revenue Report
**Trigger:** Schedule Trigger (Sunday 8pm). **Nodes:** Gumroad API (weekly revenue), Notion (log), Gmail (report email). **Output:** revenue summary every Sunday evening.

### Template 8: Support Email Triage
**Trigger:** Gmail Trigger (new email to support inbox). **Nodes:** OpenAI (classify issue: refund, bug, question, praise), If (route by category), Gmail (auto-reply for common questions), Notion (log all tickets). **Output:** common questions answered automatically, complex issues flagged.

### Template 9: Content Idea Capture
**Trigger:** Webhook (from iOS Shortcut or Telegram bot). **Nodes:** OpenAI (expand the raw idea into a brief), Notion (save to Ideas database). **Output:** raw ideas expanded and stored automatically from anywhere.

### Template 10: Invoice Reminder
**Trigger:** Schedule Trigger (check every Monday). **Nodes:** Notion (query unpaid invoices older than 14 days), If (overdue), Gmail (send reminder). **Output:** overdue invoice reminders sent automatically without you remembering to check.

---

## Appendix B: Troubleshooting Common n8n Errors

### "Workflow did not start"
**Cause:** The workflow is deactivated or the trigger is misconfigured.
**Fix:** Check that the workflow is toggled to Active. For webhook triggers, verify the webhook URL is correct and that the sending service is using the right URL (production URL, not test URL).

### "Could not connect to credentials"
**Cause:** API key expired, wrong key, or missing permission scope.
**Fix:** Go to Settings, Credentials, and edit the affected credential. Re-enter the API key or re-authorize via OAuth. For OAuth credentials, reauthorize if more than 60 days have passed.

### "Data not found in expected field"
**Cause:** The previous node returned data in a different structure than expected.
**Fix:** Open the execution log, click the node that failed, and examine the "Input" tab. The data is there, but the field name may be different from what you referenced. Update the expression in the failing node to match the actual field name.

### "Too many requests" (rate limit errors)
**Cause:** You are calling an external API too frequently.
**Fix:** Add a Wait node (set to 1 to 2 seconds) between API calls inside a loop. For OpenAI specifically, add a Wait node between requests if processing more than 10 items in batch.

### "Webhook URL not reachable"
**Cause:** Your n8n instance is not publicly accessible.
**Fix:** For self-hosted setups, make sure your Railway or VPS deployment has a public URL configured. The WEBHOOK_URL environment variable must match your public domain exactly, including https.

### "Node execution timed out"
**Cause:** A node is waiting for a response that never arrived, or an AI call is taking too long.
**Fix:** Check the external service status (OpenAI, Notion, etc.). For large AI prompts, reduce the input size or switch to a faster model. For Notion operations on large databases, add filters to the query to reduce the dataset size.

### "Merge node not receiving all inputs"
**Cause:** One of the parallel branches failed before the Merge node could receive its input.
**Fix:** Check the execution log for each branch. Find the one that failed and fix the upstream error. The Merge node in "Wait for All" mode will not proceed until every connected branch delivers data.

### "Expression returned undefined"
**Cause:** You are referencing a field that does not exist in the current node's input data.
**Fix:** Open the node editor. Click the expression field. Use the variable selector on the right side to browse the available data fields from the previous node. Replace your manual expression with the selected variable to ensure the field exists.
