# YouTube Script Batch 96
# Topics: The n8n Automation Guide for Beginners / How to Grow on Twitter/X / The Fear Funnel Explained
# Voice: Dan Koe tone. No em dashes. No exclamation marks. No hype words.

---

## Script 1: The n8n Automation Guide for Beginners (Build Your First Real Workflow)

**Target length:** 1,500-1,700 words | 12 min

---

### HOOK (0:00-0:30)

Every piece of repetitive work you do in your business is a problem waiting to be solved once.

Checking email and manually forwarding leads to a spreadsheet. Posting to multiple social platforms separately. Copying data from one tool to another by hand. These are not tasks. They're systems waiting to be built.

n8n is the tool that lets you build those systems without writing code. And once you understand how it works, the way you think about your workflows will change permanently.

---

### INTRO

n8n is a workflow automation tool. It connects your apps and services together, and it runs logic between them automatically.

Think of it like this: something happens in one tool (a trigger), n8n picks up that event and does things with it (actions). The connection between the trigger and the actions is the workflow you build.

What makes n8n different from alternatives like Zapier or Make: it's open source, self-hostable, and the logic you can build is significantly more complex. You can run loops, use conditional branching, call APIs, process data, and even run code inside workflows.

This video covers the foundational concepts you need to build your first workflow and actually understand what you're doing.

---

### SECTION 1: Core Concepts

Before you touch the interface, understand these four concepts.

**Nodes.** Every step in an n8n workflow is a node. A node is either a trigger (what starts the workflow) or an action (what happens as a result). There are hundreds of pre-built nodes for popular tools: Gmail, Notion, Airtable, Slack, Twitter, and many others.

**Workflow.** The sequence of connected nodes. The flow of data from left to right, from trigger to final action.

**Data flow.** When a node runs, it outputs data. The next node receives that data as input. You can map fields from one node's output into another node's inputs. This is how information moves through the workflow.

**Credentials.** When you connect n8n to an external service, you authenticate with API keys or OAuth. These are stored as credentials. You set them up once and reuse them across any workflow.

These four concepts cover 80% of what you need to know to get started.

---

### SECTION 2: Setting Up n8n

You have two options for running n8n.

**n8n Cloud.** The hosted version. No server to manage. You pay a monthly fee. Easiest way to start. Go to n8n.io, create an account, and you're in the interface within minutes.

**Self-hosted.** Run n8n on your own server or locally. This requires Docker or a Node.js environment. The advantage: you own your data and the cost is lower at scale. For a beginner, start with the cloud version and self-host later if you need to.

For this tutorial, I'm assuming n8n Cloud.

---

### SECTION 3: Your First Workflow (Step by Step)

Let's build something real. This workflow will watch for new subscribers on your email list (using a webhook trigger) and automatically add them to a Notion database.

Step 1: Create a new workflow. Click "New Workflow" in the n8n dashboard.

Step 2: Add a Webhook trigger node. This gives you a URL that external services can send data to. Copy that URL.

Step 3: Go to your email platform (Beehiiv, ConvertKit, or whatever you use) and set up a webhook notification for new subscribers. Paste the n8n webhook URL as the destination.

Step 4: In n8n, click "Listen for test event." Then trigger a test subscriber signup in your email platform. n8n will receive the incoming data and show you its structure.

Step 5: Add a Notion node. Connect your Notion credentials. Select "Create a database item." Map the fields: subscriber email from the webhook output goes into the Email field in your Notion database.

Step 6: Test the full workflow. If everything maps correctly, the test subscriber should appear in your Notion database.

Step 7: Activate the workflow. Toggle it from inactive to active. It will now run automatically every time a new subscriber comes in.

This is a simple workflow. But the logic you just learned, trigger, receive data, map fields, action, is the same logic for every workflow you'll ever build.

---

### SECTION 4: Intermediate Patterns

Once you understand the basics, here are the patterns that unlock more power.

**Conditional branching (IF nodes).** You can route data differently based on conditions. "If the subscriber came from this lead magnet, add them to this segment. Otherwise, add them to the general list." This is how you build personalization into your automation.

**Loops.** When you're processing multiple items (for example, a list of 50 leads), you need a loop to process each one individually. n8n has a SplitInBatches node for this.

**HTTP Request nodes.** If there's no pre-built node for a service you use, you can call its API directly with an HTTP Request node. This unlocks almost any service that has an API, which is most modern software.

**Code nodes.** When you need custom logic, you can write JavaScript directly in n8n. This is where n8n becomes genuinely programmable for builders who are comfortable with code.

---

### SECTION 5: High-Value Workflows for Solopreneurs

Here are five workflows worth building in your first 30 days.

Lead capture to CRM. Webhook from your landing page form, create a contact in Notion or Airtable, send a welcome email via your email platform.

Content repurposing. Post published on your blog via RSS, extract key points with an AI node (Claude or OpenAI), draft a Twitter thread and a LinkedIn post, save to a content queue.

Product sale to thank-you sequence. New Gumroad sale triggers a webhook, create a customer record in Notion, trigger a specific email sequence in your email platform.

Weekly analytics report. Schedule trigger every Monday morning, pull last week's data from your analytics tools, format it into a report, send it to yourself via email or Telegram.

Customer question to Notion knowledge base. Email received in Gmail that matches "question" keyword, route to Notion inbox for review, send acknowledgment reply.

---

### SECTION 6: Where to Learn More

The n8n documentation is genuinely good. The community forum has workflow templates for almost every common use case. Start there before building anything from scratch.

YouTube has a growing library of n8n tutorials. Search for the specific integration you're trying to build. Someone has probably already documented it.

---

### OUTRO + CTA

The first workflow you build will take longer than you expect. The fifth workflow will take a quarter of the time. The skill compounds.

Start with something small and real. A workflow that solves an actual problem in your current work. Build it, see it run, and then look at what else you're doing manually that you could automate.

I have a link in the description to the n8n automation pack I built for solopreneurs. Five pre-built workflow templates with setup guides.

Subscribe for weekly content on building leverage as a one-person operation.

---

## Script 2: How to Grow on Twitter/X in 2026 (The Honest System)

**Target length:** 1,300-1,500 words | 10-11 min

---

### HOOK (0:00-0:30)

Twitter growth advice falls into two categories. Generic tips that don't work and tactical tricks that work for two weeks until everyone does them.

What actually grows a Twitter account over time is simpler and less sexy than either of those.

It's having something real to say, saying it consistently, and engaging with the people who respond. That's most of it.

Today I'm going to break down the actual mechanics of Twitter growth, what the algorithm rewards, and how to build a following that translates into real business outcomes.

---

### INTRO

Twitter, now X, is still the best platform for building an intellectual audience quickly.

The reason: the barrier to engagement is the lowest of any platform. A well-written tweet can get thousands of impressions on an account with 200 followers if it resonates with the right people. That doesn't happen on Instagram or LinkedIn at the same scale.

The audience it builds is also different. Twitter tends to attract builders, thinkers, buyers, and early adopters. For a solopreneur selling digital products or services, that's a high-quality audience.

---

### SECTION 1: What the Algorithm Actually Rewards

Twitter's algorithm rewards engagement velocity and completion rate.

Engagement velocity: how quickly a post gets likes, replies, and bookmarks after being published. A post that gets 20 likes in the first hour will be shown to more people than one that gets 200 likes over three days.

Completion rate: for longer posts and threads, what percentage of readers finish. This means your opening line is not just about hooks. It's about getting enough people to keep reading that the algorithm marks the content as high value.

Replies are the highest signal. A post with 50 comments tells the algorithm there's a real conversation happening. Prioritize writing things that make people want to respond.

---

### SECTION 2: The Post Types That Work

Not all content formats perform the same way on Twitter.

**The insight post.** One idea, stated clearly, in 1-3 sentences. No thread needed. The simplest format that still performs. "Most solopreneurs price their products based on fear, not value. The result is a race to the bottom that benefits no one, including the buyer." That's a post. It makes people think. They engage.

**The thread.** A sequence of connected ideas that tells a story or breaks down a concept. The first tweet must be strong enough to make people click "show more." The rest of the thread delivers the promised depth. Good threads get bookmarked heavily, which is a strong algorithmic signal.

**The list.** "5 things I learned after my first $5K in digital product sales." Direct value, skimmable, shareable. Lists have high bookmark rates because people save them to reference later.

**The story.** Personal experience that contains a lesson or insight. "Six months ago I had zero email subscribers and one product that wasn't selling. Here's what changed." Stories create emotional connection that pure information doesn't.

Rotate through all four formats. Accounts that only post one type become predictable and lose engagement over time.

---

### SECTION 3: Consistency and Timing

The accounts that grow consistently post 3-5 times per day. That sounds like a lot. With batching, it's manageable.

You don't need to post in real time. Schedule your posts the day before using native scheduling or a tool like Hypefury or Buffer. Write everything in one production session.

The timing that works for most audiences: 7-9am local time, 12-1pm, 6-8pm. These are when engagement rates peak. Your specific audience might differ. Check your analytics after 30 days and adjust.

---

### SECTION 4: The Engagement Layer

Posting alone is not enough. The accounts that grow fastest are also active in the replies of other accounts in their space.

This is not generic complimenting. It's substantive replies that add to the original point, offer a different perspective, or share relevant experience.

When you reply meaningfully to a post that gets 500 replies, your response gets surfaced to a portion of those readers. If your reply is good, they click your profile. If your profile has strong content, they follow.

Set aside 15-20 minutes per day specifically for engagement. Not scrolling. Targeted engagement on accounts your ideal audience already follows.

---

### SECTION 5: Converting Followers to Business Outcomes

Followers are not revenue. The conversion from follower to buyer requires a deliberate structure.

Every three to five posts, point somewhere. Your newsletter signup. Your product. Your lead magnet. Not with hard selling. With a soft, natural reference.

"I break this down in more depth in the newsletter. Link in bio."

"The full framework is in the guide. Linked in the thread."

This is how the social media audience becomes an email list and eventually a customer base. The conversion is gradual. The key is doing it consistently and naturally, not treating your audience as a market to extract from.

---

### SECTION 6: Profile Optimization

Before any of the content strategy matters, your profile has to do its job.

Bio: one sentence that tells the reader exactly who you help and how. Not your job title. Not a list of interests. "I build systems for solopreneurs who want to replace their salary with digital products." That's a bio that converts.

Pinned tweet: your best-performing piece of content or your newsletter opt-in. This is the first thing someone sees when they click your profile after discovering you.

Profile picture: real face, clear image, good lighting. Avatars and logos consistently convert worse than faces for personal brand accounts.

---

### OUTRO + CTA

Twitter growth is a long game. The accounts that seem to blow up overnight were usually posting for 6-12 months before the algorithm picked them up.

The system is simple. Post consistently. Make it specific. Engage substantively. Point toward your business. Repeat.

Subscribe for weekly content on building a real audience and a real business as a solo operator.

---

## Script 3: The Fear Funnel Explained (How Your Buyer's Fear Becomes Your Revenue)

**Target length:** 1,400-1,600 words | 11-12 min

---

### HOOK (0:00-0:30)

Every purchase decision is driven by either aspiration or fear. Usually both at once.

The dream of the outcome pulls the buyer toward you. The fear of staying stuck pushes them to act.

Most solopreneurs focus only on the aspiration. Their marketing shows the destination: the freedom, the income, the lifestyle. They ignore the fear.

This is a mistake. The fear funnel is built around the psychology that actually triggers purchases, and it's one of the most important things you can understand about selling digital products.

---

### INTRO

Fear in marketing doesn't mean manipulation. It means understanding what's actually at stake for your buyer when they don't solve the problem you solve.

If you sell a guide on how to price freelance work correctly, the fear is real: "I'm leaving money on the table every month and I don't know how much." That's a real, specific fear. A good fear funnel makes that cost visible, makes the solution believable, and removes the risk of purchase.

That's not manipulation. That's meeting your buyer where they actually are.

---

### SECTION 1: What the Fear Funnel Is

The fear funnel is a sequence of content or touchpoints that takes a buyer from "I might have this problem" to "I need to solve this now."

It works in four stages.

**Stage 1: Pattern interruption.** Something that makes the buyer recognize a problem they've been normalizing. "You're not bad at pricing. You've just never been taught the right framework." This breaks a story the buyer was telling themselves.

**Stage 2: Problem amplification.** Making the cost of the problem concrete and visible. Not to be dramatic. To be honest about what continuing to not solve this actually costs. "If you're underpricing your work by 20%, and you're billing $3,000/month, that's $600/month left on the table. $7,200 per year."

**Stage 3: Solution introduction.** Positioning your product as the specific mechanism that solves the now-amplified problem. Not a generic fix. The specific thing, for their specific situation.

**Stage 4: Risk removal.** Addressing the objections that remain. Usually: "Will this actually work for me?" and "What if I waste my money?" The guarantee handles the money concern. The specificity of the solution handles the "works for me" concern.

---

### SECTION 2: Mapping Fear to Your Product

Every product solves a problem. The fear funnel starts with identifying the specific fear behind that problem.

The way to find the real fear: look at what the buyer is afraid will happen if the problem continues. Not the surface problem. The downstream consequence.

Surface problem: "I don't know how to grow my email list."

The real fear underneath: "I'll build my entire business on social media, the platform will change its algorithm or ban my account, and I'll lose everything I built."

Once you've found the real fear, your marketing speaks to it directly. That's what makes a buyer feel like you understand them in a way other solutions don't.

---

### SECTION 3: Building the Fear Funnel in Content

You don't need a formal sales funnel to use this psychology. You can implement it in your regular content.

On Twitter: pattern interruption posts that challenge a common belief your audience holds incorrectly.

In your newsletter: the problem amplification section. Break down the cost of a common mistake with specific numbers.

On YouTube: videos that start with the fear ("here's what happens if you don't have a content system") and move toward the solution.

On your sales page: the fear-solution-risk-removal sequence, written in the language of your buyer's own words.

---

### SECTION 4: The Ethics of Fear Marketing

This needs to be addressed directly because people conflate fear marketing with manipulation.

The line is this: you're describing a real problem with real consequences for a real person. You're not creating a problem that doesn't exist. You're not exaggerating consequences beyond what's true. You're not using urgency that is false.

If a freelancer is genuinely losing $7,200/year to underpricing, showing them that math is not manipulation. It's service.

The manipulation happens when marketers invent fears, inflate consequences, or manufacture urgency. That's a different thing. Don't do that.

The fear funnel is effective because it's honest. The buyer recognizes the problem as real. The recognition creates the motivation to act.

---

### SECTION 5: Lead Magnets Built on Fear

The fear funnel is the framework behind the best-converting lead magnets.

A lead magnet that says "Get my free productivity guide" is an aspiration offer. Decent conversion.

A lead magnet that says "Find out how much money you're losing every month by not automating your client onboarding" is a fear offer. Significantly higher conversion for the right audience.

The fear-based lead magnet typically takes one of these forms:
- An audit or self-assessment ("Are you making these 5 pricing mistakes?")
- A cost calculator ("How much is this costing you per year?")
- A before/after comparison ("What most freelancers do vs. what works")

These convert better because they activate the loss aversion that's already present in the buyer's decision-making.

---

### SECTION 6: Putting It Together as a System

A full fear funnel as a system looks like this.

Content (social media, YouTube) creates pattern interruption. Buyer realizes they have a problem they've been normalizing.

Lead magnet (fear-based) captures their email. They take an action that confirms the problem is real for them.

Email sequence amplifies the problem across 3-5 emails, introduces the solution, and handles objections.

Sales page completes the purchase. The guarantee removes the final friction.

Post-purchase: the product delivers. The fear is resolved. The buyer becomes a case study and a repeat buyer.

This is the structure behind most high-converting digital product businesses. The fear isn't a trick. It's the honest thread running through the buyer's entire journey.

---

### OUTRO + CTA

The fear funnel is not about making your buyer feel bad. It's about making the cost of inaction visible so they can make a real decision.

Understand the fear behind your product. Build content that makes that fear recognizable. Offer the solution. Remove the risk. That's the sequence.

I have a full breakdown of the fear funnel as a marketing system in the description, including the email sequence templates.

Subscribe for weekly content on building a real, sustainable business as a solo operator.
