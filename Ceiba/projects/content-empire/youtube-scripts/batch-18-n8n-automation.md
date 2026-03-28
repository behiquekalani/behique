# Batch 18: n8n Automation for Solopreneurs
# Channel: @behikeai
# 5 Scripts, ~1,000-1,200 words each

---

## Script 1: "I Automated My Entire Business with Free Software (n8n Setup Guide)"

**[HOOK — 0:00 to 0:30]**

Six months ago I was spending four hours every single day on tasks that required zero thinking. Copying leads from a form into a spreadsheet. Sending the same three follow-up emails. Posting the same content to four different platforms. Manually backing up files. Checking metrics from five different tabs.

I was not running a business. I was running myself into the ground doing data entry.

Then I found n8n. It's free, it runs on your computer or a cheap server, and it lets you connect any app to any other app without writing a single line of code. Today I want to walk you through exactly how I set it up and what changed.

**[PROBLEM — 0:30 to 2:00]**

Here is what most solopreneurs do wrong with automation. They hear about Zapier, they sign up, they build a workflow, and then they get the bill. Zapier charges per task. At any real volume, you're paying $50 to $100 a month minimum just to have your apps talk to each other. So people either overpay, or they give up on automation entirely.

The second mistake is thinking automation requires a developer. Most tutorials show you Python scripts or API documentation that reads like legal text. You close the tab and go back to doing things manually because the alternative feels harder than the problem.

The third mistake is trying to automate everything at once. People build this huge complex workflow that breaks immediately, can't figure out where the problem is, and conclude automation doesn't work for them. It does work. They just started in the wrong place.

**[SOLUTION — 2:00 to 3:30]**

n8n solves the cost problem because it's open source. You can self-host it on your own machine or on a $5 server. No per-task fees. No monthly subscription eating into your margins. The software itself is free.

It solves the complexity problem because everything works visually. You drag and drop nodes. Each node represents one app or one action. You connect them with lines, like a flowchart a ten-year-old could draw. There's no code required for most workflows. And when you do need something custom, you can drop a single line of JavaScript into a node without needing to know how to build apps.

It solves the fragility problem because you can see exactly where a workflow breaks. Every node shows you its input and output. When something goes wrong, you click the node that failed and see the exact error message.

**[STEPS — 3:30 to 6:00]**

Step one: Install n8n. If you want the easiest possible start, go to app.n8n.cloud and use their free tier. If you want full control and no limits, install it locally using their Docker setup. The documentation is clear. It takes about fifteen minutes.

Step two: Pick your first workflow. Do not start with the hardest thing. Start with one simple connection. Something like: when someone fills out my contact form, add their name and email to a Google Sheet. That's it. One trigger, one action. Get that working before you build anything else.

Step three: Learn the three types of nodes. Trigger nodes start a workflow (a form submission, a scheduled time, an incoming email). Action nodes do something (add a row to a sheet, send an email, post to Slack). Processing nodes modify the data in between (format a date, combine two fields, filter a list). Once you understand those three types, you can build almost anything.

Step four: Connect your core tools. For most solopreneurs that means Gmail, Google Sheets, and either Notion or Airtable. n8n has built-in integrations for all of these. No custom setup needed. You connect them with your API key or OAuth login and they work.

Step five: Set up error notifications. This is one most people skip. Add a node at the end of every workflow that sends you a Telegram message or email if something fails. Otherwise a workflow can silently break and you won't know for a week.

**[REAL EXAMPLE — 6:00 to 7:00]**

Here is one workflow I built in about forty minutes. Every morning at 7am, n8n pulls my top three tasks from a Notion database, checks my Google Calendar for what's scheduled that day, and sends me a formatted summary as a Telegram message. I wake up, I open Telegram, I already know what my day looks like. No checking three apps separately. No mental load before coffee.

That workflow took forty minutes to build. It now saves me ten to fifteen minutes every single morning. That's about five hours a month, and it costs me nothing.

**[CALL TO ACTION — 7:00 to 7:30]**

If you want to speed up the learning curve, I made a guide called "How I Built an AI Employee" that covers my full automation stack, including how I use n8n as part of a multi-agent system running on three computers. It goes deeper than this video and walks you through the exact tools and configurations I'm using right now. Link is in the description.

---

## Script 2: "5 n8n Workflows Every Solopreneur Needs in 2026"

**[HOOK — 0:00 to 0:30]**

I built forty-seven n8n workflows last year. Most of them I deleted because they were solving problems that weren't real problems. But five of them are still running every single day, and I would notice immediately if they stopped. These are the ones worth building first. Not the flashy ones. The boring ones that quietly save you hours every week.

**[PROBLEM — 0:30 to 2:00]**

When you're starting with automation, everyone tells you the same thing: automate your lead capture, automate your social media, automate your email. That advice is real but it's vague. What does that actually look like? What are the specific workflows that move the needle for a one-person business?

The problem is that most automation tutorials are built for companies with teams and budgets. They assume you have a marketing department, a CRM with ten thousand contacts, and a developer on call. You don't. You have yourself, a laptop, and maybe five apps you're trying to keep in sync.

These five workflows are built for that reality.

**[SOLUTION — 2:00 to 3:00]**

Each of these workflows follows the same pattern. One trigger, a few actions, one result you actually care about. None of them require coding. All of them are free to run on n8n self-hosted or on their free cloud tier.

**[THE 5 WORKFLOWS — 3:00 to 6:30]**

Workflow one: Lead capture to CRM. When someone fills out your contact form (Typeform, Tally, Google Forms, any of them), n8n automatically adds them to a Google Sheet or Notion database, tags them by what they said they need, and sends you a Telegram notification with their details. You stop losing leads because you forgot to check your email.

Workflow two: Content repurposing. This one is higher impact than people realize. You write one piece of content, whether that's a tweet, a newsletter, or a short note in Notion. A trigger fires, n8n pulls the content, formats it for three different platforms, and queues it in a scheduling tool. One piece of thinking becomes three posts without any extra effort.

Workflow three: Daily briefing. Every morning at a time you choose, n8n pulls your tasks from Notion, your events from Google Calendar, and any unread emails flagged as important. It formats all of that into one message and sends it to your phone via Telegram. Your day starts with one tap, not ten.

Workflow four: Invoice follow-up. When a payment is overdue (you define the trigger, usually seven days past due), n8n sends a polite follow-up email automatically. No more awkward manual chasing. It just happens. You can customize the message, set how many follow-ups it sends, and tell it to stop once payment is received.

Workflow five: Knowledge base sync. When you save something to Notion, bookmark a link in your browser, or add a note anywhere, n8n pulls it into one central database. You stop losing ideas in different apps. Everything ends up in one place you actually check.

**[REAL EXAMPLE — 6:30 to 7:00]**

Workflow two, the content repurposing one, cut my content time in half. I was spending ninety minutes a day adapting content for different platforms. Now I spend forty-five minutes writing one original piece and the rest happens automatically. Over a month that's about twenty hours back.

**[CALL TO ACTION — 7:00 to 7:30]**

I cover these workflows in detail in my guide "How I Built an AI Employee," including the exact node configurations and the mistakes I made building each one. If you want to skip the trial and error and start with something that works, it's linked in the description below.

---

## Script 3: "How I Send 200 Emails a Month Without Touching My Keyboard"

**[HOOK — 0:00 to 0:30]**

Last month I sent 200 emails. Welcome sequences for new subscribers, follow-ups for inquiries, weekly newsletter delivery, receipts, confirmations. Two hundred emails. I personally typed zero of them.

This is not about having a huge team. I'm one person. This is about building a system once and letting it run. I want to show you how I did it and how you can copy the same setup.

**[PROBLEM — 0:30 to 2:00]**

Email is where solopreneurs bleed time. Not because email is hard, but because it's repetitive. You write the same welcome message every time someone signs up. You send the same "thanks for your inquiry" every time someone fills out your contact form. You manually trigger campaigns instead of having them fire automatically.

The other problem is that most email automation tools are expensive the moment you want to do anything interesting. The entry-level plans are fine until you need to connect email to your other tools, add conditions, or build anything more complex than a simple sequence. Then you're paying $50 or $100 a month for features that should cost nothing.

**[SOLUTION — 2:00 to 3:30]**

The setup I use is n8n combined with a free email sending service. On the email side I use Brevo's free plan, which lets you send 300 emails a day for free. n8n handles all the logic. When something happens (someone signs up, buys a product, fills out a form), n8n receives that trigger and decides what email to send, to whom, and when.

The key is separating the logic from the sending. n8n handles the "when and to whom" part. Brevo handles the "actually delivering it" part. They talk to each other via a simple API connection that takes about ten minutes to set up.

**[STEPS — 3:30 to 6:00]**

Step one: Create your email templates in Brevo. Log in, go to email templates, and write your sequences. Welcome email, follow-up day three, follow-up day seven. Write them once. Give each one a template ID number.

Step two: In n8n, create a trigger for each entry point. Someone buys something? Webhook trigger from Gumroad. Someone signs up? Trigger from your form tool. Keep each entry point as its own workflow so they don't tangle.

Step three: Add a delay node. n8n has a built-in wait node. You set it to wait one day, three days, whatever your sequence requires, and the workflow pauses and resumes automatically. You do not need to babysit it.

Step four: Connect to Brevo. There's a built-in Brevo node in n8n. Add it after your delay. Pass in the subscriber's email address and the template ID. The email goes out. That's it.

Step five: Add logging. After each email send, write one row to a Google Sheet with the email address, the template that fired, and the timestamp. This gives you a simple record of what went out and when. If someone says they never got an email, you can check the log in thirty seconds.

**[REAL EXAMPLE — 6:00 to 7:00]**

When someone buys one of my digital products on Gumroad, a webhook fires in n8n. The workflow reads their name and email from the webhook data. It immediately sends them a welcome email through Brevo. Three days later the wait node releases and it sends a follow-up asking if they have questions. Seven days later another follow-up with a bonus tip. The whole sequence runs without me knowing it happened. The buyer gets a professional, responsive experience. I'm doing something else entirely.

Total setup time for that workflow was about an hour. It has now fired hundreds of times.

**[CALL TO ACTION — 7:00 to 7:30]**

If you want to see the full automation stack including the AI agents I added on top of this, check out my guide "How I Built an AI Employee." It walks through the complete system, the tools, and the exact configurations. It's in the description.

---

## Script 4: "n8n vs Zapier: I Used Both for 6 Months. Here Is the Real Answer."

**[HOOK — 0:00 to 0:30]**

I have an actual answer to this question. Not a sponsored one. I used Zapier for three months, paid real money for it, hit the ceiling, switched to n8n, and have been on n8n for six months since. Both tools work. But they are not for the same person, and nobody is being honest about that.

**[PROBLEM — 0:30 to 2:00]**

The comparison articles you find online about n8n versus Zapier are almost all written by affiliate marketers who get paid when you click the Zapier link. They'll tell you both tools are great, list some features, and then strategically make Zapier sound a little easier to get you to sign up.

The honest problem is that your needs will change. You might start with Zapier and be fine for six months. Then your business grows, you need more workflows, more tasks per month, and suddenly you're paying $100 a month for something that used to be $20. Or you need a workflow Zapier can't do without a premium plan. That's when people start looking at alternatives.

**[THE REAL COMPARISON — 2:00 to 5:30]**

Let me go through the actual differences.

Cost. Zapier charges by task. Their free plan gives you 100 tasks a month, which sounds okay until you realize that one workflow triggering five actions counts as five tasks. A hundred tasks disappear in days if you have any real volume. Their paid plans start at $20/month and scale up fast. n8n self-hosted is free. Their cloud starter plan is $20/month with unlimited workflows and executions. If you're doing any volume at all, n8n wins on cost.

Ease of use. Zapier is genuinely easier to start with. The interface is clean. The onboarding is guided. If you've never done automation before, Zapier will get you to your first working workflow faster. n8n has a learning curve. The interface is more technical. It takes a few hours to feel comfortable. If you're not willing to spend a weekend learning it, Zapier is probably the better choice right now.

Flexibility. This is where n8n wins decisively. n8n lets you add JavaScript directly into any node, build complex branching logic, handle errors gracefully, and build workflows that Zapier simply cannot do. If you ever need to process data before sending it somewhere, filter lists, do calculations, or connect to an API that doesn't have a native integration, n8n handles it. Zapier will make you feel like you're working around the tool instead of with it.

Integrations. Zapier has more pre-built integrations. A lot more. If you use a niche tool, it might only be on Zapier. n8n's integration library is growing fast but it's not at Zapier's level yet. If your workflow requires three specific obscure apps, check both libraries before committing.

Self-hosting. Only n8n does this. Your data stays on your machine or your server. For solopreneurs handling client data or anything sensitive, this matters. Zapier processes everything on their servers.

**[WHO SHOULD USE WHICH — 5:30 to 6:30]**

Use Zapier if you're just starting with automation, you want something working in thirty minutes, your volume is low, and you're using mainstream apps with lots of native integrations.

Use n8n if you're running a real business with real volume, you care about cost at scale, you want flexibility to build complex workflows, or you care about where your data lives.

I switched to n8n because I outgrew Zapier. My automation volume went up, the bill went up, and I needed workflows that Zapier couldn't build. The learning curve was worth it.

**[CALL TO ACTION — 6:30 to 7:30]**

If you're ready to commit to n8n and want to see how it fits into a full AI-powered business setup, my guide "How I Built an AI Employee" breaks down my complete system, including where n8n sits in the stack and what it connects to. Link is in the description.

---

## Script 5: "The 30-Minute Automation That Saved Me 10 Hours a Week"

**[HOOK — 0:00 to 0:30]**

I want to tell you about one specific workflow. Not a system, not a philosophy, not an overview of twenty tools. One workflow. I built it in thirty minutes on a Tuesday afternoon, and by Friday I knew I was never going back to doing it manually.

**[PROBLEM — 0:30 to 2:00]**

Every week I was doing the same thing. Checking which content performed well across Instagram, my email list, and my Gumroad store. Opening four different tabs. Copy-pasting numbers into a spreadsheet. Trying to remember what I had posted and when. Comparing last week to this week. Deciding what to create next based on that comparison.

The whole process took about two hours. It felt like progress because I was staring at data. But the actual decision I was trying to make, what to create next, took about five minutes. I was spending two hours to answer a five-minute question.

That is the kind of task automation is built for. Repetitive, predictable, data gathering that ends in a simple decision.

**[SOLUTION — 2:00 to 3:30]**

The workflow I built does this: every Sunday at 9pm, n8n runs a check. It pulls engagement data from Instagram via their API. It pulls email open rates from my email tool. It pulls product sales from Gumroad's API. It organizes all of that into one formatted summary. Then it sends me that summary as a Telegram message.

Monday morning I wake up, I open Telegram, and my weekly performance review is already there. I read it in five minutes. I make a decision about the week's content focus. Done.

Building that took thirty minutes. Saving two hours a week means I've gotten back more than a full workday every single month.

**[EXACT STEPS — 3:30 to 6:00]**

Here is exactly how to build this.

Node one: Schedule trigger. Set it to run every Sunday at 9pm or whatever time works for you. This is the start of the workflow.

Node two: Gumroad API call. Use an HTTP Request node in n8n. Point it at Gumroad's sales endpoint with your API key. Set the date range to the past seven days. The response comes back as JSON with your sales data.

Node three: Google Sheets read. Pull your email metrics from a sheet where your email tool logs them. Most email tools let you export data to Sheets automatically. n8n reads that data in under a second.

Node four: Instagram API call. This one requires a bit of setup because Meta's API needs an app registration. Give yourself an hour the first time. After that it's just another HTTP request node pulling your post engagement for the past seven days.

Node five: Data formatting. This is one JavaScript node that takes all three data sources and formats them into a clean summary. Something like: "Top post this week: [title], [reach] reach. Email opens: [rate]%. Sales: [number] units, $[amount]. Best performing content type: [type]." Write the format once, it runs every week.

Node six: Telegram send. Connect to Telegram using the Telegram node in n8n. Enter your bot token and your chat ID. Send the formatted message. That's it.

**[REAL EXAMPLE — 6:00 to 7:00]**

The first week this ran, I found out that my short-form posts were getting three times the reach of my longer ones. I had been spending three hours on a long post format that was getting less engagement than a ten-minute short. That one data point shifted my entire content strategy. I would not have caught it without the weekly summary because I was too inconsistent about manually checking.

Automation does not just save time. It makes sure you actually look at the right information consistently. That consistency is what produces useful insights.

**[CALL TO ACTION — 7:00 to 7:30]**

For the complete system that this workflow lives inside, including the AI agents that help me decide what to do with the data, check out my guide "How I Built an AI Employee." It covers the full stack, from automation to AI, in one place. You'll find the link in the description.
