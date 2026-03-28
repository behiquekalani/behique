---
title: "n8n Automation Starter Pack — Setup Guide"
type: product-guide
tags: [n8n, automation, solopreneur, workflows, instagram, newsletter, content]
created: 2026-03-22
---

# n8n Automation Starter Pack
## Setup Guide for 5 Content Workflows

---

## Introduction: Why n8n and Not Zapier or Make

Most people who discover automation tools go straight to Zapier. It's the default recommendation. It shows up first in blog posts. It has a friendly interface and a brand that feels safe.

Here's what they don't tell you: Zapier charges per task. Every time a workflow runs, it consumes a "Zap." At scale, that adds up fast. If your RSS feed pulls 50 articles a day and you process each one, you're burning through 1,500 tasks a month before you've done anything interesting. The free plan runs out in a week.

Make (formerly Integromat) is better. More flexible, lower cost, genuinely powerful. But it still runs on their servers, on their pricing model, on their terms.

n8n is different.

n8n is open source. You can self-host it on a $5 VPS and run unlimited workflows with zero per-task fees. Forever. The code is on GitHub. You own the instance. Your API keys live on your machine, not in a third-party database.

If you don't want to manage infrastructure, n8n also has a cloud option. It runs the same way. You pay a flat monthly fee. No per-task pricing. No surprises at the end of the month when one workflow ran more than expected.

For a solopreneur building a content pipeline, this matters. You're going to run these workflows every day. The RSS feed checks every 4 hours. The analytics report runs every Sunday. The lead magnet fires every time someone fills out a form. That volume would cost $50-100/month on Zapier. On a self-hosted n8n instance, it costs nothing extra.

There's one honest tradeoff: n8n has a steeper learning curve. The interface is more complex than Zapier's drag-and-drop simplicity. The first time you look at a workflow canvas, it can feel like a circuit diagram. This guide is written specifically to flatten that curve. I built all five of these workflows and I'll show you exactly how each one works, node by node.

The five workflows in this pack cover the core of a content-first online business:

1. RSS to Instagram Carousel. Turns news from any RSS feed into formatted carousel content, reviewed and scheduled.
2. YouTube Transcript to Newsletter. Pulls any YouTube video's transcript and reformats it as a newsletter draft.
3. One Idea to Five Platforms. Takes a single idea from Telegram and expands it into platform-specific formats.
4. Lead Magnet Auto-Delivery. Handles the entire flow from form submission to welcome email and file delivery.
5. Weekly Analytics Report. Pulls Instagram data every Sunday and sends a formatted digest to your inbox.

Each chapter covers one workflow: what it does, how to configure it, how to test it, and what to do when something breaks.

Start with the Getting Started section. Then open the JSON file for Workflow 1 and follow along in your n8n instance. By the time you finish this guide, you'll have five working automations and the mental model to build more on your own.

---

## Getting Started: Installing n8n and Importing Your First Workflow

### Option 1: n8n Cloud (Recommended if you want zero setup)

Go to n8n.io and click "Start for free." You get a 14-day trial. After that, the Starter plan is $20/month for up to 5 active workflows and 2,500 workflow executions per month. The Pro plan at $50/month removes those limits.

For most of what's in this pack, the Starter plan is enough. The RSS workflow runs every 4 hours, which is about 180 executions per month for that one workflow alone. Add the others and you'll hit around 500-800 executions monthly in normal use. You have room.

After signing up, you land on a workflow canvas. That's where everything happens.

### Option 2: Self-Hosted (Recommended if you want zero ongoing cost)

You need a machine that can run Node.js. A $5/month VPS from DigitalOcean, Hetzner, or Railway works. A Raspberry Pi on your home network works. An old laptop you don't use anymore works.

Install n8n with npm:

```
npm install n8n -g
```

Then run it:

```
n8n start
```

By default it runs on port 5678. Open your browser to http://localhost:5678. You'll see the same canvas as the cloud version.

For a persistent installation (so it keeps running when you close the terminal), use PM2:

```
npm install pm2 -g
pm2 start n8n
pm2 save
pm2 startup
```

For a VPS with a domain, put Nginx in front of it and add a Let's Encrypt certificate. The n8n documentation has a full guide for this at docs.n8n.io/hosting/installation/server-setups/.

### Creating Your Account

On first launch, n8n asks you to create an admin account. Use a real email. You'll need it if you ever reset your instance or switch machines.

Don't connect anything yet. Just get the canvas open and working. The credentials come later, one per workflow.

### Importing a JSON Workflow File

Every workflow in this pack is a .json file. Importing is the same process for all five.

In your n8n canvas:

1. Click the menu in the top left (three horizontal lines).
2. Select "Import from File."
3. Choose the .json file from this pack.
4. The workflow appears on your canvas.
5. Click "Save" in the top right.

The workflow is now in your instance. You'll see all the nodes laid out. Nothing runs yet because the credentials aren't connected and the workflow is inactive.

Each chapter below walks through the exact credentials you need and how to connect them. Once you've done that for a workflow, you set it to "Active" using the toggle in the top right. From that point forward, it runs automatically on its configured schedule.

One important note: when you import a workflow, the credential fields show as empty. n8n doesn't store credentials inside the JSON file (for good reason). You always add them fresh after importing. This is a security feature, not a bug.

---

## Chapter 1: RSS to Instagram Carousel

**Workflow file:** rss-to-instagram-carousel.json

### What This Workflow Does

Every 4 hours, this workflow checks up to 5 RSS feeds you configure. It filters items by keywords relevant to your niche. For each item that passes the filter, it sends the content to OpenAI to summarize into 10 bullet points formatted as an Instagram carousel. It then schedules that carousel to Buffer for posting. Finally, it emails you a digest so you can review what was scheduled before it goes live.

I use this every Monday when I check in on the content pipeline for the week. There's always a queue of carousels waiting. I review, approve anything that needs edits in Buffer, and the rest posts on schedule.

### Node by Node

**Schedule Trigger**

This is the starting node. It fires the workflow on a timer. The default configuration is every 4 hours. To change the interval:

1. Double-click the Schedule Trigger node.
2. Under "Trigger Interval," change "4" and "hours" to whatever you need.
3. Save.

Every time this node fires, it starts one execution of the entire workflow.

**RSS Feed Node**

The RSS Feed node fetches items from a URL you provide. The default configuration in the imported workflow has a placeholder URL. You need to replace it with your actual RSS feed.

To find an RSS feed URL for any publication:
- Most blogs have it at /feed or /rss (example: techcrunch.com/feed)
- For Google News topics: search news.google.com, filter to a topic, and grab the RSS icon from the URL bar
- For YouTube channels: the feed is at https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE

The node is configured to fetch the 10 most recent items per run. This prevents you from processing hundreds of old items if you start the workflow fresh. You can change this under "Options" in the node settings.

To configure multiple feeds, you have two options. The simpler option is to use a single RSS aggregator service (like Feedly) that combines multiple feeds into one. The more powerful option is to duplicate the RSS Feed node for each separate feed and merge them before the IF node.

**IF Node (Keyword Filter)**

The IF node checks each RSS item's title and description against a list of keywords you define. If the item contains any of those keywords, it passes through to OpenAI. If not, it's skipped.

The default keyword list is empty. You need to add your own. To edit:

1. Double-click the IF node.
2. Under "Conditions," find the text-contains check.
3. Replace the example keywords with your actual niche terms.

For a content business in the AI space, you might use keywords like: "AI," "automation," "ChatGPT," "productivity," "solopreneur." Keep the list tight. The more specific your keywords, the higher the quality of what gets through.

Items that don't match go through the "false" path and are skipped. Nothing happens to them.

**OpenAI Node**

This node sends the article title and description to GPT-4o-mini with a specific prompt. The prompt asks for 10 bullet points formatted as carousel slides. Each bullet is 1-2 lines, written to stand alone on its own slide.

The default prompt is:

```
You are a content strategist writing for an Instagram carousel.

Article title: {{$json.title}}
Article summary: {{$json.contentSnippet}}

Write 10 bullet points for an Instagram carousel about this article.
Each bullet should be 1-2 sentences, written to stand alone as a slide.
Be direct. No filler language. No hype words.
Start with the most interesting or unexpected point.
```

You can modify this prompt to match your voice. The important thing is to keep the `{{$json.title}}` and `{{$json.contentSnippet}}` references. Those pull the data from the RSS feed item.

To connect your OpenAI account:
1. Click "Create New Credential" inside the OpenAI node.
2. Enter your API key from platform.openai.com/api-keys.
3. The credential is saved and reusable across all nodes in your instance.

**Code Node (Format as Carousel Text)**

The Code node takes the 10 bullet points from OpenAI and formats them into a single text block ready to copy into a design tool or paste into a carousel template. It numbers each slide, adds a header line with the article title, and adds a footer with a placeholder call to action.

The code is plain JavaScript. It's commented line by line. You don't need to change it unless you want to adjust the formatting. The one thing worth changing is the footer CTA text at the bottom of the code block. Search for "Follow for more" and replace it with your actual account handle and CTA.

**HTTP Request Node (Buffer)**

This node calls the Buffer API to schedule the formatted carousel text as a post. Buffer handles the actual scheduling queue.

To get your Buffer API credentials:
1. Log into buffer.com.
2. Go to Settings > Apps.
3. Under "Access Token," click "Generate."
4. Copy the token.

In the HTTP Request node:
1. Change the Authorization header value to your token.
2. Change the profile_id value to your Buffer profile ID. You can find your profile ID by calling buffer.com/1/profiles.json with your access token in a browser.

Note: Buffer's free plan allows 3 scheduled posts at a time per profile. If you're running this every 4 hours and generating multiple carousels per run, the queue can fill up. Either upgrade Buffer or add a throttle to the workflow by adding a Wait node between the Code node and the HTTP Request node.

**Gmail Node (Review Digest)**

After scheduling to Buffer, the workflow sends you an email digest with the content that was just queued. This is your review pass before anything posts publicly.

The email contains the article titles, the carousel text, and the scheduled post time from Buffer.

To connect Gmail:
1. In the Gmail node, click "Create New Credential."
2. Select "OAuth2."
3. Follow the Google OAuth flow. You'll need a Google Cloud project with the Gmail API enabled. The n8n docs have a step-by-step guide at docs.n8n.io/integrations/built-in/core-nodes/n8n-nodes-base.gmail/.

Once connected, change the "To" field from the placeholder email to your actual email address.

### Testing

Before setting the workflow to Active, test it manually.

1. Click "Execute Workflow" in the top toolbar.
2. Watch each node light up as it runs.
3. Click any node to see the input and output data for that run.

The most useful node to inspect is the OpenAI node. Check that the bullet points it generated are actually usable. If they're generic, adjust the prompt.

Also check the Buffer node. If it returns a 200 status, the post was scheduled. If it returns a 401, your token is invalid. If it returns a 400, the profile_id is wrong.

### Troubleshooting

**RSS feed not updating.** This usually means the feed URL is returning cached results. Most RSS feeds update every 30-60 minutes. If you're running the workflow more frequently than that, you'll often see the same items repeated. The workflow won't repost the same item because n8n tracks execution state, but if you disabled and re-enabled the workflow, the deduplication resets. The fix: add a Google Sheets node to log processed item GUIDs and check against that list before passing items to OpenAI.

**OpenAI rate limit.** GPT-4o-mini has a rate limit based on your usage tier. If you're on the free tier, you might hit limits if multiple RSS items are processed in one run. The fix: add a Wait node set to 2 seconds between the RSS Feed node and the OpenAI node. This spaces out the API calls.

**Buffer API rejected.** The most common cause is an expired or regenerated access token. Buffer tokens don't expire by default, but if you regenerated your token in the Buffer dashboard, the old one stops working immediately. Go back to the HTTP Request node and paste the new token. The second common cause is posting to a profile that's disconnected in Buffer. Log into Buffer and confirm your Instagram account is still connected.

---

## Chapter 2: YouTube Transcript to Newsletter

**Workflow file:** youtube-to-newsletter.json

### What This Workflow Does

You send a YouTube URL to a webhook. The workflow fetches the transcript using a transcript service, sends it to OpenAI to reformat as a newsletter section (intro paragraph, 3 main points, call to action), then creates a draft in ConvertKit and emails you a notification.

I built this because I watch a lot of YouTube for research. Whenever I find a video with usable insight, I used to copy-paste the auto-generated subtitles and spend 30 minutes reformatting them. Now I paste the URL into a trigger and have a draft in ConvertKit in 90 seconds.

### Node by Node

**Webhook Trigger**

The webhook listens for a POST request containing a YouTube URL. Once you deploy the workflow and set it to Active, n8n gives you a unique webhook URL that looks like:

```
https://your-n8n-instance.com/webhook/youtube-to-newsletter
```

You can trigger this from anywhere: a curl command in your terminal, a Telegram bot message (via the One Idea workflow), a browser bookmark with a simple form, or a Siri shortcut on your phone.

The simplest way to use it during testing: open your terminal and run:

```
curl -X POST https://your-n8n-instance.com/webhook/youtube-to-newsletter \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID_HERE"}'
```

Replace `VIDEO_ID_HERE` with any YouTube video ID.

**HTTP Request Node (Transcript Service)**

This node calls a transcript service to get the video's text. The workflow uses the free transcript endpoint from tactiq.io or a self-hosted yt-dlp wrapper, depending on your setup.

The simplest production-ready option: use the YouTube Transcript API. You can self-host a small Python server that accepts a YouTube URL and returns the transcript. The code is three lines:

```python
from youtube_transcript_api import YouTubeTranscriptApi
import json, sys
transcript = YouTubeTranscriptApi.get_transcript(sys.argv[1])
print(json.dumps(" ".join([t['text'] for t in transcript])))
```

Host that on Railway or Render for free. Point the HTTP Request node at it.

For a no-code option: use the RapidAPI YouTube Transcript API (youtube-transcript3.p.rapidapi.com). It has a free tier of 100 requests/month. The workflow's HTTP Request node is pre-configured for this API. Add your RapidAPI key in the Headers section.

**OpenAI Chat Model Node**

This node takes the transcript text and sends it to GPT-4o with a prompt that formats it as a newsletter section. The prompt:

```
You are writing a newsletter section based on a YouTube video transcript.

Transcript:
{{$json.transcript}}

Write a newsletter section with this structure:
- Opening paragraph (2-3 sentences): the main insight from the video
- 3 main points: each is a heading + 2-3 sentence explanation
- Closing paragraph: one honest takeaway and a call to action

Voice: direct, personal, no hype. Write as if you watched this video yourself.
Do not mention that this came from a transcript.
```

The "write as if you watched this yourself" instruction is important. It prevents the output from reading like a summarization bot. The goal is a newsletter section that sounds like a human curator sharing something worth reading.

**HTTP Request Node (ConvertKit)**

This node creates a draft broadcast in ConvertKit using the ConvertKit v3 API.

To get your ConvertKit API key:
1. Log into app.convertkit.com.
2. Go to Settings > Developer.
3. Copy your API Key (not the API Secret, which is for different endpoints).

The node sends a POST to:
```
https://api.convertkit.com/v3/broadcasts
```

With the body:
```json
{
  "api_key": "YOUR_KEY_HERE",
  "subject": "{{$json.video_title}}",
  "content": "{{$json.newsletter_text}}"
}
```

The draft appears in your ConvertKit Broadcasts section. You edit the subject line, add your personal intro, and schedule it from there.

**Gmail Node (Notify Author)**

A short email to you: "New newsletter draft created from [video title]. Preview it in ConvertKit."

This is optional. You can disable this node if you'd rather just check ConvertKit directly. The notification is useful when the workflow runs automatically rather than manually, so you don't have to remember to check.

### Testing with a Sample Video

Use a video you know well. Something where you can verify whether the output is accurate.

Send the webhook request with the URL. Watch the execution in n8n. If the transcript node returns empty, the video might have auto-captions disabled. Not all YouTube videos have transcripts available. The workflow handles this gracefully: if the transcript is empty, the OpenAI node still runs but will note that no transcript was available. You get a notification and no ConvertKit draft is created.

Check the OpenAI output carefully on the first few runs. The newsletter format often needs a prompt adjustment to match your voice. Add your specific style instructions to the prompt. Reference the voice bible rules: direct, no hype, Caribbean builder tone.

---

## Chapter 3: One Idea to Five Platforms

**Workflow file:** one-idea-five-platforms.json

### What This Workflow Does

You send a message to your Telegram bot. The workflow takes that single idea and simultaneously asks OpenAI to format it for five different platforms: X/Twitter (280 characters), LinkedIn (paragraph format), Instagram (caption format), YouTube (description format), and a newsletter paragraph. All five versions are logged to Google Sheets and sent back to you on Telegram.

This is the most useful workflow in the pack for day-to-day content work. I send it a shower thought, a book quote I'm reacting to, an observation from something I built. Two minutes later I have five options. I pick the best one for each platform, edit as needed, and post.

### Why the Five Prompts Are Separate

Each platform prompt is a separate OpenAI node, not one combined request. This is intentional.

A single prompt asking for "all five formats" produces mediocre output. The model tries to balance all the constraints at once. The Twitter version ends up too long. The LinkedIn version reads like a tweet. The quality is inconsistent.

Separate nodes let each prompt focus entirely on one platform's requirements. The Twitter node's only job is to write a 280-character tweet. The LinkedIn node's only job is to write a professional paragraph. Each one can be independently tuned without affecting the others.

The tradeoff is more API calls (5 instead of 1) and slightly more cost. For GPT-4o-mini, 5 calls on a short idea costs about $0.002 total. Worth it for the quality difference.

### Node by Node

**Telegram Trigger**

The Telegram trigger listens for messages sent to your bot. To set this up:

1. Open Telegram and find @BotFather.
2. Send /newbot and follow the prompts to create a bot.
3. Copy the bot token BotFather gives you.
4. In the Telegram Trigger node in n8n, create a new credential with that token.
5. Set the workflow to Active.

From that point, any message you send to your bot triggers the workflow. The message text becomes `{{$json.message.text}}` in all subsequent nodes.

One important note: the Telegram trigger uses long-polling by default. This means n8n continuously polls Telegram's servers for new messages. On self-hosted setups, this works fine. On n8n Cloud, it also works but counts against your execution quota for each poll cycle. If you want to reduce this, switch to webhook mode in the Telegram Trigger settings. Webhook mode fires only when a message arrives, which is both faster and cheaper.

**OpenAI Nodes x5**

Each of the five nodes connects to the same credential (your OpenAI API key) but uses a different prompt.

The prompts are pre-written in the imported workflow. Here they are so you can understand and customize them:

Twitter/X:
```
Write a single tweet (max 280 characters) based on this idea.
Be direct. Lead with the insight, not the context.
No hashtags. No emojis. Sound like a founder, not a marketer.
Idea: {{$json.message.text}}
```

LinkedIn:
```
Write a LinkedIn post (150-250 words) based on this idea.
Start with a one-line hook. Follow with 3-4 short paragraphs.
Professional but personal. No buzzwords.
End with a question that invites real responses.
Idea: {{$json.message.text}}
```

Instagram:
```
Write an Instagram caption based on this idea.
3 short paragraphs max. First line is the hook (under 8 words).
No hashtags in the caption. Sound personal, not promotional.
Idea: {{$json.message.text}}
```

YouTube Description:
```
Write a YouTube video description (100-150 words) based on this idea as a video topic.
First paragraph: what the video is about and why it matters.
Second paragraph: 3-4 bullet points of what the viewer will learn.
End with a subscribe call to action (one direct sentence).
Idea: {{$json.message.text}}
```

Newsletter Paragraph:
```
Write a newsletter paragraph (80-120 words) based on this idea.
Personal, thoughtful, honest. Like a letter to a smart friend.
Start with a specific observation. Connect it to a bigger pattern.
End with one practical insight.
Idea: {{$json.message.text}}
```

To modify any of these prompts, double-click the corresponding OpenAI node and edit the "User" message field.

**Code Node (Formats All 5 Into Structured Output)**

After all five OpenAI nodes complete, a Code node collects the results and formats them into a single structured object. Each platform's output is labeled and numbered. This is what gets logged to Google Sheets and sent back to Telegram.

The code node runs after the five parallel OpenAI nodes have all finished. n8n handles the parallel execution automatically. You don't need to configure anything special for this.

**Google Sheets Node (Log All 5 Versions)**

Every time the workflow runs, it appends a row to a Google Sheet with:
- Timestamp
- Original idea
- Twitter version
- LinkedIn version
- Instagram version
- YouTube version
- Newsletter version

This is your content archive. Every idea you've ever put into the workflow lives here. You can search it, reference it, reuse it later.

To connect Google Sheets:
1. In the Google Sheets node, click "Create New Credential."
2. Select "Service Account" for the most reliable connection.
3. In Google Cloud Console, create a Service Account, download the JSON key, and paste the entire JSON into the credential field.
4. Share your target spreadsheet with the Service Account email address (it looks like something@your-project.iam.gserviceaccount.com).

The Spreadsheet ID is the long string in the Google Sheets URL between /d/ and /edit. The Sheet Name is the tab name at the bottom (usually "Sheet1" unless you've renamed it).

**Telegram Reply Node**

The workflow replies to your Telegram message with all five versions. The formatting uses Telegram's MarkdownV2 format. Each platform section is labeled with a header.

If the message is longer than 4,096 characters (Telegram's limit), the Code node splits it into two messages. Both are sent as separate Telegram messages in sequence.

### How to Modify the Prompts for Your Own Voice

The five prompts are starting points. After running the workflow 10-15 times, you'll notice patterns in what needs fixing. Common ones:

- The Twitter output tends to be too polished. Add: "Sound like a real person, not a brand account."
- The LinkedIn output often overuses bullet points. Add: "Prefer prose over bullet points."
- The Instagram output sometimes ignores the hook rule. Add: "The first line must be under 8 words and must create curiosity."

Paste two or three of your own published posts into the prompt as style examples. This is the fastest way to improve output quality. Example:

```
Here are examples of my Instagram captions:
---
Three computers. Six AI agents. Zero employees.
That's the setup I built to run my entire content pipeline without hiring anyone.
---
Write in this same voice.
```

The model calibrates to examples much more reliably than to descriptions.

---

## Chapter 4: Lead Magnet Auto-Delivery

**Workflow file:** lead-magnet-delivery.json

### What This Workflow Does

Someone fills out a form on your site (Tally or Typeform). The webhook fires. The workflow checks which lead magnet they requested, adds them to the right ConvertKit sequence, sends a welcome email with the download link, and logs the subscriber in Airtable.

The entire sequence runs in under 10 seconds from form submission to email delivery. No manual steps.

### Setting Up the Webhook in Tally or Typeform

**Tally:**
1. Open your form in Tally.
2. Go to Integrations > Webhooks.
3. Paste your n8n webhook URL (from the Webhook Trigger node).
4. Save and publish the form.

**Typeform:**
1. Open your form in Typeform.
2. Go to Connect > Webhooks.
3. Add the n8n webhook URL.
4. Save.

Both platforms send a POST request to your webhook URL every time someone submits the form. The request contains the form field values.

The field names vary depending on how you built your form. The IF node in the workflow checks a specific field to determine which lead magnet to deliver. You'll need to update the field name in the IF node to match your actual form. The default configuration expects a field called "lead_magnet" with values like "ai-guide" or "checklist."

### Building the Gmail Welcome Email Template

The Gmail node sends the welcome email. The default template is:

```
Subject: Here's your [LEAD MAGNET NAME]

Hey,

Here's the download link you requested:

[DOWNLOAD LINK]

This is a direct link to Google Drive. It'll work immediately.

If you have any questions, reply to this email.

Kalani
```

You customize this in the Gmail node's "Message" field. The `{{$json.download_link}}` variable is populated by the IF node based on which lead magnet was requested.

For the download link to work, your file needs to be hosted somewhere accessible. Google Drive with "Anyone with the link can view" is the simplest option. Your Gumroad product URL works too, if you're using Gumroad for delivery.

**Building the Gmail Template:**

1. Double-click the Gmail node.
2. Change the "To" field to `{{$json.email}}` to send to the submitter's email.
3. Update the subject line.
4. Write your welcome message in the "Message" field.
5. Connect your Gmail credential (same OAuth process as in Chapter 1).

**Connecting ConvertKit for the Welcome Sequence:**

The workflow calls the ConvertKit API to:
1. Add the subscriber to your ConvertKit audience.
2. Apply a tag based on which lead magnet they requested.
3. Trigger the corresponding email sequence.

The endpoint is:
```
POST https://api.convertkit.com/v3/forms/FORM_ID/subscribe
```

Replace FORM_ID with the ID of the ConvertKit form you want subscribers added to. You find this in ConvertKit under Forms, by looking at the form URL.

The body includes:
```json
{
  "api_key": "YOUR_KEY",
  "email": "{{$json.email}}",
  "tags": ["lead-magnet-{{$json.lead_magnet}}"]
}
```

This tags the subscriber automatically. You can then set up ConvertKit automations based on those tags.

### The IF Node Logic

The IF node checks the `lead_magnet` field from the form submission and routes to one of two paths: deliver lead magnet A or deliver lead magnet B.

If you have more than 2 lead magnets, add additional output routes to the IF node or use a Switch node instead. The Switch node can handle unlimited cases. To swap in a Switch node: delete the IF node, add a Switch node in its place, and configure one case per lead magnet value.

### The Airtable Log

The Airtable node logs every subscriber with timestamp, email, lead magnet requested, and whether the delivery succeeded. This is your subscriber history outside of ConvertKit.

To connect Airtable:
1. Go to airtable.com/create/tokens.
2. Create a personal access token with read/write access to your base.
3. In the Airtable node, create a new credential with that token.
4. Set the Base ID (from the Airtable URL) and Table Name.

Your Airtable table needs columns that match what the node is sending: Email, Lead Magnet, Timestamp, Status.

### The 3 Common Errors

**Webhook not triggering.** This almost always means the workflow is not set to Active. The webhook URL only works when the workflow is Active. Click the Active toggle in the top right of the workflow canvas. The toggle should turn green. Test by submitting your form manually.

**Tag not applying in ConvertKit.** The most common cause is a mismatch between the tag name in the workflow and the actual tag in ConvertKit. ConvertKit creates tags automatically when you send them via API, but it's case-sensitive. "lead-magnet-ai-guide" and "Lead-Magnet-AI-Guide" are different tags. Check that your tag names are consistent across the workflow and ConvertKit.

**Wrong file linked.** If the download link sends people to the wrong file, the issue is in the IF node logic. Open the IF node and check which path each lead magnet value routes to. Then check the Gmail node on each path and confirm the correct Google Drive link is in the message template. A quick fix: hardcode the correct URL directly in the Gmail node for each path rather than using a variable for the URL.

---

## Chapter 5: Weekly Analytics Report

**Workflow file:** weekly-analytics-report.json

### What This Workflow Does

Every Sunday at 8 AM, the workflow pulls your top 5 Instagram posts from the past 7 days using the Instagram Basic Display API. A JavaScript node calculates reach, engagement rate, and sorts the posts. OpenAI writes a 2-sentence plain-English summary per post. Everything goes into a formatted email that lands in your inbox before you start your week.

I started running this in late 2025 when I realized I had no idea which of my posts was actually performing. I was posting based on intuition. The Sunday report fixed that. Four weeks in, I had a clear picture of what topics, formats, and hooks worked for my audience.

### Getting Your Instagram Access Token

The Instagram Basic Display API is the part of Meta's API stack that lets you read your own account's data. Getting the token is the most complex part of this entire workflow. Do this once and you won't have to touch it again for 60 days (when the token expires and needs refreshing).

Here's the process:

1. Go to developers.facebook.com.
2. Create a new App (select "Consumer" type).
3. Under "Add a Product," add "Instagram Basic Display."
4. In the Instagram Basic Display settings, add your Instagram account as a test user.
5. Under "User Token Generator," click "Generate Token" next to your account.
6. Instagram will ask you to log in and authorize. Approve everything.
7. Copy the token. It's a long string that starts with "IGQ..." or similar.

Paste this token into the HTTP Request node in the workflow. Put it in the Authorization header:

```
Bearer YOUR_TOKEN_HERE
```

The token expires after 60 days by default. The workflow includes an optional Token Refresh node (set to inactive by default) that you can enable to auto-refresh your token every 50 days. Enable it if you want fully hands-off operation.

### The Instagram API Call

The HTTP Request node calls:

```
GET https://graph.instagram.com/me/media?fields=id,caption,media_type,timestamp,like_count,comments_count,reach&limit=10&access_token={{YOUR_TOKEN}}
```

This returns the 10 most recent posts with engagement data. The Code node then filters for posts from the past 7 days and sorts by engagement.

Note: `reach` and `impressions` are only available for Business or Creator accounts connected to a Facebook Page. If your account is a Personal account, these fields return errors. The workflow handles this gracefully: if reach data isn't available, it falls back to likes + comments as the engagement metric.

### The JavaScript Code Node, Explained Line by Line

The Code node is the one place in this pack where you'll see actual code. It's 28 lines. Here's what each section does, in plain English:

```javascript
// Get the list of posts from the previous node
const posts = $input.all().map(item => item.json);
```
This line collects all the Instagram post data from the API response. `$input.all()` is n8n's way of saying "give me everything from the previous step."

```javascript
// Filter to posts from the last 7 days
const oneWeekAgo = new Date();
oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
const recentPosts = posts.filter(p => new Date(p.timestamp) > oneWeekAgo);
```
This creates a date 7 days ago and keeps only posts newer than that. The `timestamp` field comes from Instagram as an ISO date string (like "2026-03-15T14:22:00+0000").

```javascript
// Calculate engagement rate for each post
const withEngagement = recentPosts.map(p => ({
  ...p,
  engagement: (p.like_count + p.comments_count) / Math.max(p.reach || p.like_count, 1),
  total_interactions: p.like_count + p.comments_count
}));
```
Engagement rate = (likes + comments) / reach. The `Math.max(..., 1)` prevents dividing by zero if reach data isn't available.

```javascript
// Sort by total interactions, highest first
const sorted = withEngagement.sort((a, b) => b.total_interactions - a.total_interactions);

// Return top 5
return sorted.slice(0, 5).map(p => ({ json: p }));
```
Sorts the posts and returns the top 5. The `({ json: p })` format is required by n8n. Every item the Code node returns needs to be wrapped in `{ json: ... }`.

That's the entire code node. You don't need to change any of it unless you want to change the sorting logic or the number of posts returned.

### The OpenAI Summary

For each of the top 5 posts, OpenAI writes a 2-sentence summary. The prompt:

```
Instagram post data:
Caption: {{$json.caption}}
Likes: {{$json.like_count}}
Comments: {{$json.comments_count}}
Engagement rate: {{$json.engagement}}

Write 2 sentences:
1. What made this post perform well (or not).
2. What to do differently or repeat next week.

Be direct. No hedging.
```

The output is a brief, actionable note per post. Not a full analysis. Just enough to inform next week's content decisions.

### Customizing the Email Template

The Gmail node sends the final report. The template uses HTML formatting for readability. You can customize the colors, layout, and content by editing the HTML in the Gmail node's "Message" field.

The one thing to definitely change: the subject line. The default is "Weekly Instagram Report - {{$now.format('MMMM D')}}". This inserts the current date automatically. Keep the date pattern if you want. Change the prefix text to whatever you'll actually want to see in your inbox on Sunday morning.

---

## Credentials Checklist

Before you run any workflow, collect the credentials listed here. All of these have free tiers or are free to obtain. The cost column shows what you'd pay at production volume.

| Workflow | Service | Credential | Where to Find It | Free Tier | Est. Monthly Cost |
|----------|---------|------------|------------------|-----------|-------------------|
| 1 - RSS Carousel | OpenAI | API Key | platform.openai.com/api-keys | $5 credit on signup | ~$2-5/mo |
| 1 - RSS Carousel | Buffer | Access Token | buffer.com > Settings > Apps | Free (3 posts queued) | $0 (free tier) or $6/mo (Essentials) |
| 1 - RSS Carousel | Gmail | OAuth2 | Via n8n Google OAuth flow | Free | $0 |
| 2 - YT Newsletter | OpenAI | API Key | Same as above | Same | ~$1-2/mo |
| 2 - YT Newsletter | YouTube Transcript API | RapidAPI Key | rapidapi.com | 100 calls/mo free | $0 (free tier) or $10/mo |
| 2 - YT Newsletter | ConvertKit | API Key | app.convertkit.com > Settings > Developer | Free up to 1,000 subscribers | $0 (free) or $25/mo (Creator) |
| 2 - YT Newsletter | Gmail | OAuth2 | Same as above | Free | $0 |
| 3 - One Idea | OpenAI | API Key | Same as above | Same | ~$0.50-2/mo |
| 3 - One Idea | Telegram Bot | Bot Token | Telegram @BotFather | Free | $0 |
| 3 - One Idea | Google Sheets | Service Account JSON | Google Cloud Console | Free | $0 |
| 4 - Lead Magnet | ConvertKit | API Key | Same as above | Same | $0 (free tier) |
| 4 - Lead Magnet | Gmail | OAuth2 | Same as above | Free | $0 |
| 4 - Lead Magnet | Airtable | Personal Access Token | airtable.com/create/tokens | Free up to 1,200 rows/base | $0 (free tier) |
| 4 - Lead Magnet | Tally/Typeform | Webhook URL only | No key needed | Free | $0 |
| 5 - Analytics | Instagram | Basic Display API Token | developers.facebook.com | Free | $0 |
| 5 - Analytics | OpenAI | API Key | Same as above | Same | ~$0.50-1/mo |
| 5 - Analytics | Gmail | OAuth2 | Same as above | Free | $0 |

**Total estimated monthly cost at production volume: $5-15/mo** (mostly OpenAI, assuming moderate usage). If you're on a tight budget, use GPT-4o-mini for everything (the default in these workflows) and the cost drops to $2-5/mo.

---

## Troubleshooting: The 8 Most Common n8n Errors

**1. "Credential not found" or "Credential is invalid"**

The workflow was imported but the credentials weren't connected. Open each node, look for the red "Credential" indicator, and either select an existing credential or create a new one. This is the first error almost everyone encounters on their first import.

**2. "Execution timed out"**

A node took longer than the default timeout (usually 30-60 seconds). This happens most often with OpenAI calls on large inputs or slow transcript fetches. Fix: increase the node timeout in the node settings (click the three dots, then "Settings"). For OpenAI specifically, switch from GPT-4o to GPT-4o-mini for faster responses.

**3. "Could not get input data"**

A node is trying to read data that the previous node didn't produce. This usually means an upstream node failed silently or returned empty results. Click the previous node to see its output. If it's empty, that's your problem. Common cause: an RSS feed that returned no items, or an API that returned an empty array.

**4. "Workflow is not active"**

The webhook URL or schedule trigger won't fire until the workflow is set to Active. The Active toggle is in the top right of the workflow canvas. It needs to be green.

**5. "401 Unauthorized"**

Your API key or token is wrong, expired, or has insufficient permissions. Go back to the service, regenerate or verify the credential, and update it in n8n. For Google OAuth credentials specifically, they sometimes need to be refreshed by going back through the OAuth flow.

**6. "400 Bad Request"**

The data you're sending to an API is malformed. This often happens when a variable like `{{$json.email}}` is undefined because the previous node's data structure changed. Open the failing node, check the input data (via "Input" tab when looking at the node), and verify the field names match what you're referencing in the node's configuration.

**7. "429 Too Many Requests"**

You've hit a rate limit on an external API. The most common culprits are OpenAI and ConvertKit. Add a Wait node before the rate-limited node and set it to 2-5 seconds. For OpenAI specifically, consider moving to a paid tier if you hit this regularly.

**8. "The workflow ran but nothing happened"**

The workflow executed but produced no output. This is almost always the IF node routing items to the wrong path. Click the IF node after a test run and check which path each item took. If all items are going through the "false" path, your condition logic is inverted.

---

## What's Next: Combining Workflows and Adding Error Handling

### Chaining Workflows Together

The most powerful thing you can do with these five workflows is connect them. Here are three combinations worth building:

**RSS Carousel + One Idea to Five Platforms:**
After the RSS Feed and OpenAI summarization in Workflow 1, instead of formatting as a carousel, send the summary to the Webhook Trigger of Workflow 3. You get a single article summary expanded into five platform-specific content pieces. One RSS item becomes five posts.

**YouTube Newsletter + One Idea:**
The YouTube workflow generates a newsletter section. That section can be sent to Workflow 3 as the "idea" input. You now have a newsletter section plus the Twitter, LinkedIn, and Instagram versions of that same insight.

**Lead Magnet + Weekly Analytics:**
Add a step to Workflow 4 that logs each new lead magnet subscriber to a separate Google Sheet. Modify Workflow 5 to also pull data from that sheet. Your Sunday analytics report then includes both content performance AND lead magnet conversion numbers.

To chain workflows in n8n: use the HTTP Request node to call the webhook URL of the second workflow. Or use n8n's native "Execute Workflow" node, which is cleaner for workflows in the same instance.

### Adding Error Handling

Every production workflow should have error handling. Without it, a failed API call silently kills the execution and you never know what was skipped.

The simplest error handling in n8n: add an "Error Trigger" node to any workflow. This node fires whenever that workflow encounters an unhandled error. Connect it to a Gmail or Telegram node that notifies you.

To add an Error Trigger:
1. In the workflow editor, click Add Node.
2. Search for "Error Trigger."
3. Add a Gmail or Telegram node after it.
4. Configure the notification to include `{{$json.execution.error.message}}` so you know what failed.

For more granular handling, use the "Continue on Fail" option in individual nodes. This lets the workflow continue even when one node fails, rather than stopping completely. You'd then add a downstream check to see which nodes succeeded.

### n8n Community Resources

When you run into something not covered in this guide, these are the places to go:

- **n8n Documentation:** docs.n8n.io. The integration-specific guides are detailed and current.
- **n8n Community Forum:** community.n8n.io. Active forum. Most questions have been asked before.
- **n8n Templates Library:** n8n.io/workflows. Thousands of pre-built workflows. Search by tool or use case.
- **n8n Discord:** discord.gg/XPKeKXeB7d. Faster responses for specific questions.

The n8n team ships updates frequently. Check the changelog (docs.n8n.io/release-notes/) when something stops working after an update. Node parameter names sometimes change between versions.

---

## A Note on Maintenance

Automations are not set-and-forget. APIs change. Rate limits get tightened. Access tokens expire. Google OAuth credentials occasionally need re-authorization.

Set a calendar reminder to check each workflow once a month. A 5-minute review: confirm the last execution succeeded, check that the output quality is still good, and verify credentials are still valid.

The workflows in this pack have been running in production for months. They work. But they require the same periodic attention you'd give any tool in your stack.

Build these. Run them. Observe what they produce. Adjust the prompts to match your voice exactly. That's the work. The automation handles the volume. Your judgment handles the quality.

That's the point of all of this.

---

*n8n Automation Starter Pack. Built by Kalani Andre for Behike. 2026.*
