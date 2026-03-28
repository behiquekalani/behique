# YouTube Scripts — Batch 63
**Theme:** n8n automation / Content pipeline / AI email writing
**Brand:** Behike
**Tone:** Educational, direct, Dan Koe meets MrBeast structure

---

### Script 1 — n8n Automation for Beginners: Build Your First Workflow in 20 Minutes

**Thumbnail concept:** Split screen: left side shows a person drowning in tabs and manual work, right side shows a clean dashboard with "AUTOMATED" text. Bold yellow text: "20 MINUTES"

**Hook (0-30s):**
Most people think automation requires a developer or $500/month in software. I'm going to show you how to build a real automation in 20 minutes using n8n, which is free, open source, and more powerful than Zapier. By the end of this video you will have a working workflow that does something useful for your business today.

**Intro (30s-2min):**
My name is Kalani. I build AI-powered systems for one-person businesses. Over the last year I have automated content posting, lead capture, email follow-ups, and product research using n8n. I am not a developer. I learned this by doing. This video is for people who have heard of automation but never actually built anything. You do not need to write code. You do not need prior experience. You need a browser and 20 minutes. Here is what we are building: a workflow that watches a Google Sheet, pulls new rows automatically, and sends a formatted email notification. Small, real, useful.

**Section 1 — What n8n Is and Why It Beats Zapier (2-4min):**
n8n is a workflow automation tool. Think of it as a visual programming language where you connect services together using nodes. Each node does one thing: fetch data, transform it, send it somewhere. The reason I use n8n over Zapier is threefold. First, n8n is open source, meaning you can self-host it for free on Railway or Render. Second, it has over 400 integrations including AI tools, databases, and APIs that Zapier does not have. Third, n8n lets you write custom JavaScript inside workflows, which means you are not limited by what someone pre-built. The visual editor looks like a flow chart. You drag nodes onto a canvas, connect them with lines, and the data flows from left to right. That is the mental model. Hold it.

**Section 2 — Building Your First Workflow Step by Step (4-7min):**
Open n8n. If you do not have it, go to n8n.io and sign up for the cloud trial, or deploy it free on Railway using their template. Step one: create a new workflow. Step two: add a trigger node. We will use "Schedule Trigger" to run every hour, or "Google Sheets Trigger" to watch for new rows. Step three: add a Google Sheets node. Connect it to your account, point it to your spreadsheet, tell it which sheet and which operation, "Read Rows." Step four: add an IF node. This filters rows. We only want rows where a column called "Status" equals "New." Step five: add a Gmail or Email node. Write your message. Use expressions like double curly brackets to pull in the actual row data dynamically. Step six: save and activate. That is it. The workflow now runs on its own. No manual work. Every time a new row appears in your sheet that matches the filter, the email goes out automatically.

**Section 3 — Where to Take This Next (7-10min):**
That workflow is simple on purpose. Once you understand the pattern, trigger to filter to action, you can build anything. Here are three real workflows I use: one watches my Gumroad sales and logs every purchase to a database with buyer details. Another monitors a Reddit feed for keywords related to my niche and drops new posts into a Telegram channel I review every morning. The third pulls YouTube transcripts from competitor videos and runs them through an AI node that extracts the main talking points. All three took me less than 90 minutes to build. The compounding effect of automation is not the time saved on day one. It is the time saved on every day after that. If each workflow saves you 30 minutes a day, that is 180 hours a year. That is four and a half weeks of full-time work handed back to you.

**CTA + Outro (10-12min):**
The n8n Automation Pack I built covers 12 of the most useful workflows for solopreneurs, including the content repurposing workflow, the lead magnet delivery system, and the product research pipeline. Link is below. If you want more automation videos, subscribe. Next video covers how I use n8n to automatically repurpose one YouTube script into Instagram posts, tweets, and a newsletter issue. See you there.

**Description:**
n8n is the most powerful free automation tool most people have never heard of. In this video I walk you through building your first n8n workflow from scratch, no code required. You will learn what n8n is, why it beats Zapier for solopreneurs and one-person businesses, and how to build a real workflow that saves you time starting today. We cover the visual node editor, how to connect Google Sheets, how to use filters and conditions, and how to send automated emails with dynamic data. If you have been putting off learning automation because it seemed too technical, this is the video that removes that excuse. By the end you have a working workflow and a clear mental model for building more. Perfect for content creators, freelancers, digital product sellers, and anyone who wants to stop doing repetitive tasks manually. I also share three real workflows I use in my own business. Subscribe for weekly automation and AI business content.

**Tags:** n8n tutorial, n8n automation for beginners, n8n workflow, no code automation, zapier alternative, n8n vs zapier, workflow automation, n8n google sheets, automate your business, n8n free, solopreneur automation, ai automation tools, n8n tutorial 2025, business automation, n8n beginner guide

---

### Script 2 — How I Automate My Entire Content Pipeline (From One Idea to 10 Platforms)

**Thumbnail concept:** One central idea bubble with arrows pointing out to 10 platform logos (Instagram, Twitter, YouTube, LinkedIn, Pinterest, TikTok, Newsletter, Telegram, Reddit, Blog). Bold text: "1 IDEA. 10 PLATFORMS."

**Hook (0-30s):**
I produce content for six platforms every week. I spend about two hours on it total. Not because I am fast. Because most of the work is automated. I am going to show you the exact pipeline I built, what tools it uses, and how you can copy it even if you have zero technical experience.

**Intro (30s-2min):**
This is not a theory video. I am going to walk you through a real system that is running right now in my business. The content pipeline starts with one idea, usually a YouTube script or a long-form article, and ends with platform-specific posts formatted and ready to publish or already published. The tools I use are n8n for the automation layer, Claude or ChatGPT for the AI rewriting, Notion or Google Sheets as the content database, and Buffer or the native apps for scheduling. You do not need all of these on day one. I will show you how to start with the simplest version and build from there.

**Section 1 — The Mental Model: Content Waterfall (2-4min):**
Think of content like water. You pour it in at the top and it flows down to every platform below. The top of the waterfall is your core content, which is the thing that requires the most thought. A YouTube video. A long tweet thread. A detailed blog post. Everything else is a derivative. A YouTube video becomes a script. The script becomes a tweet thread. The thread becomes five Instagram carousels. The carousels become Pinterest pins. The video transcript becomes a newsletter. The newsletter excerpt becomes a LinkedIn post. None of those derivatives require original thinking. They require reformatting. That is the work you automate. Your job as the creator is to do the top-of-waterfall thinking. The pipeline handles everything below.

**Section 2 — The Actual Workflow I Built (4-7min):**
Here is what my pipeline looks like step by step. First, I write a YouTube script in a Google Doc. Second, I paste the script into a Google Sheet row and mark it "Ready." Third, an n8n workflow triggers on that new row. It pulls the script text, sends it to the OpenAI API with a specific prompt for each format: tweet thread, Instagram carousel outline, Pinterest pin description, newsletter intro. It writes each output into a separate column of the same Google Sheet row. Fourth, I review the outputs, make quick edits where needed, and mark each one "Approved." Fifth, another n8n workflow picks up approved items and either posts them directly via API or sends them to Buffer for scheduled posting. The whole review step takes me 20 minutes. The automation handles the other three to four hours that manual cross-posting would have taken. The key insight is that the AI does not need to be perfect. It needs to be 80 percent there so you can get it to 100 in a few minutes.

**Section 3 — How to Build This Yourself (7-10min):**
Start with two things: a content database and one AI rewrite step. Your database can be a simple Google Sheet with columns for: original content, platform, reformatted output, status, publish date. Your first AI step can literally be a Claude or ChatGPT conversation where you paste the content and say "rewrite this as a tweet thread." Do that manually five times until you understand what the AI produces. Then automate that exact process with n8n. Add platforms one at a time. Do Instagram first because it has the highest ROI for visual content creators. Then Twitter. Then newsletter. Build the habit of feeding the system before you build the full automation. The system only works if you are producing core content consistently.

**CTA + Outro (10-12min):**
I put the full content waterfall system into a guide called the Content Waterfall. It includes the Google Sheet template, the exact AI prompts I use for each platform, and a walkthrough of the n8n workflows. You can grab it at behike.shop, link below. If you want me to do a deeper dive into any part of this system, drop a comment. Subscribe for more content on building one-person businesses with AI. Next video: how I use Claude AI specifically for business work, research, and writing.

**Description:**
If you are manually copy-pasting content across platforms every week, you are wasting hours you could spend building. In this video I break down the content pipeline I built that takes one YouTube script and turns it into posts for 10 different platforms automatically. I walk through the content waterfall mental model, the exact tools I use including n8n, Claude AI, and Google Sheets, and how to build this yourself starting from a basic version with no code required. This is a real system running in my one-person business right now. I also share the exact prompts I use to get platform-specific content from AI tools without it sounding generic or robotic. If you create content for your business and you are not using automation yet, this video will change how you think about your workflow. Subscribe for weekly content on AI tools, automation, and building a one-person business.

**Tags:** content automation, content repurposing, n8n content pipeline, one idea ten platforms, content waterfall, ai content creation, solopreneur content strategy, automate instagram posts, n8n ai workflow, content creator automation, digital product creator, behike, content system 2025, ai tools for creators, automate social media

---

### Script 3 — AI That Writes Your Emails: The System I Use to Never Write a Cold Email Again

**Thumbnail concept:** Inbox showing zero unread messages. Calendar showing "3 deals closed this week." Small text in corner: "I wrote 0 of these." Bold headline text: "AI EMAIL SYSTEM"

**Hook (0-30s):**
Cold email has the highest ROI of any outreach channel. It is also the one most people hate doing because writing a good cold email is hard. I built a system where AI writes personalized cold emails for every prospect I target, and I only spend time on the ones that get replies. Let me show you exactly how it works.

**Intro (30s-2min):**
Before I built this system, I would spend 20 to 30 minutes per prospect researching them, figuring out what angle to use, and writing an email that did not sound templated. Now the whole process takes under five minutes per prospect and the emails are better than what I was writing manually. This video covers: the email framework that actually gets replies, how to set up the AI to write in your voice, and how to connect it all so the system runs mostly on its own. This applies whether you are selling a service, doing B2B outreach, or trying to get partnerships and collaborations.

**Section 1 — Why Most AI Emails Fail (2-4min):**
The reason most people get bad results from AI-generated emails is that they prompt it wrong. They type "write me a cold email to sell my service" and get back something generic that reads like a mass blast. Good cold email is about one thing: making the recipient feel like you actually looked at them. The framework that works is: one specific observation about them, one bridge to a relevant problem they probably have, one clear ask that is low-commitment. Three sentences. That is it. The AI can write this better than most humans if you give it the right context. The context is what most people skip. You need to feed the AI real information about the prospect before you ask it to write anything.

**Section 2 — The AI Email System Step by Step (4-7min):**
Here is the workflow. Step one: build a prospect list. I use a Google Sheet with columns for name, company, role, their recent content or activity, and one specific thing I noticed about them. That last column is the key. It does not need to be deep. It can be "just published a post about pricing their first course" or "announced a product launch last week." Step two: write a master prompt. Mine looks like this: "You are writing a cold email on behalf of Kalani, a solopreneur who builds AI tools and automation systems. Write a three-sentence email to [name] at [company]. They recently [observation]. The email should feel personal and specific, not generic. The ask is [specific ask]. Tone is direct and warm, not pushy. No em dashes. No exclamation marks." Step three: run the prompt for each prospect using either a Claude or GPT API call, or manually if volume is low. Step four: review and send. I review every email before it goes out. The AI gets it right about 80 percent of the time. The other 20 percent needs a quick edit. Step five: track opens and replies. The ones that reply get personal attention. The ones that open but do not reply get one follow-up, also AI-written.

**Section 3 — Scaling This Without Losing the Personal Feel (7-10min):**
The instinct when you have an automated system is to blast it at scale. Resist that instinct. Cold email that actually converts feels personal because it is. The automation does the writing, but the research and list-building still require human judgment. I aim for 10 to 20 highly targeted prospects per week, not 500 generic ones. A five percent reply rate on 20 targeted emails is one new conversation a week. Over a month that is four serious leads. That is enough to build a service business from scratch. The other thing to get right is follow-up. One follow-up email, five to seven days after the first, sent only to people who opened but did not reply. AI writes this too, but even shorter: two sentences acknowledging they might have missed the first one and restating the ask. That follow-up alone doubles my reply rate.

**CTA + Outro (10-12min):**
I included the exact prompt templates I use for cold email, follow-up, and partnership outreach in the AI Employee Guide at behike.shop. It covers this system plus how I use AI for client research, proposal writing, and project management. Link is below. If you found this useful, subscribe for more. Next video: the one-person business model explained, why it works, and how to set one up in under 30 days.

**Description:**
Cold email is the highest ROI outreach channel for solopreneurs and small business owners, but most people either hate writing it or do it wrong. In this video I walk through the AI email system I built that writes personalized cold emails for every prospect I target, using Claude or GPT with specific prompting techniques that make the output feel personal rather than generic. I cover the three-sentence email framework that gets replies, how to build a prospect list that actually converts, the exact master prompt I use, and how to scale outreach without losing the personal touch that makes cold email work. This is a real system I use in my own business for B2B outreach and partnership building. If you are a freelancer, consultant, course creator, or anyone who needs to reach out to people for business, this system will save you hours every week. Subscribe for weekly content on AI tools and one-person business strategies.

**Tags:** ai cold email, cold email system, ai email writing, cold email that gets replies, cold email for freelancers, b2b outreach ai, personalized cold email, claude ai email, chatgpt cold email, solopreneur outreach, cold email framework, email automation, ai sales tools, cold email tips 2025, behike ai
