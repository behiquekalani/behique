# YouTube Scripts: Camera-Ready (Word-for-Word)
# 10 complete scripts. Read these on camera exactly as written.
# Style: Biaheza casualness + Dan Koe depth
# Voice Bible loaded. No banned words. No em dashes.
# Copyright 2026 Behike.
# Generated: 2026-03-22

---

## VIDEO 1: I Replaced a $200/Month AI Subscription With Old Laptops
**Length:** 8 minutes
**Thumbnail text:** $0/mo AI Setup
**Hook (first 5 seconds):** "I was paying $200 a month for AI. Now I pay zero. Let me show you how."

---

[CAMERA] Kalani at desk, casual, one monitor behind him, three machines visible on shelf

I was paying $200 a month for AI. Now I pay zero. Let me show you how.

[PAUSE]

So a few months ago I looked at my bank statement and I had this moment where I was like, wait. I'm a computer engineering student. I literally study how computers work. Why am I paying someone else to run AI for me?

[CUT]

ChatGPT Plus, twenty bucks. Claude Pro, twenty bucks. API costs for automation, another fifty to a hundred depending on the month. Plus Midjourney, plus Runway for video stuff. It was adding up to like $200 a month. Sometimes more.

[TEXT] $200+/month in AI subscriptions

And the worst part? Every time I closed the tab, the AI forgot everything. I'd have to re-explain my projects, my business, my preferences. Every. Single. Time.

[CUT]

[CAMERA] Kalani stands up, walks to the shelf with three machines

So here's what I did instead. Three machines. Let me introduce you.

[CAMERA] Points at Mac Mini

This is Ceiba. She's a Mac Mini M4. 16 gigs of RAM. She's the brain. Named after the sacred tree in Taino mythology, the one that connects all three worlds. She handles reasoning, planning, fast text generation. She's quiet. She's efficient. She never complains.

[CAMERA] Points at desktop PC

This is Cobo. Named after the Taino conch shell. He's an old desktop I got used for $200. The only thing that matters in here is the GPU. A GTX 1080 Ti with 11 gigs of VRAM. He's the muscle. Heavy computation, bigger models, anything that needs raw power.

[CAMERA] Points at third machine

And this is Hutia. Named after the little Taino animal. She's a basic server that runs background tasks. Scraping, monitoring, long overnight jobs. She's not flashy but she's always working.

[PAUSE]

Total cost for all three? Under a thousand dollars. One time. Not monthly. One time.

[CUT]

[SCREEN] Terminal open, clean desktop

Alright let me show you how this actually works. First thing you need is Ollama. It's free, it's open source, and it lets you run AI models locally on your own machine.

[SCREEN] Types: curl -fsSL https://ollama.com/install.sh | sh

Installation takes like two minutes. You download it, you run it, done.

[SCREEN] Types: ollama pull llama3

Now you pull a model. I use Llama 3 for most things. It's good at writing, coding, reasoning. Not GPT-4 level for everything, but for 90% of my daily work? It's more than enough.

[SCREEN] Types: ollama run llama3 and sends a prompt, response streams in

Look at that. That's running on my machine. No internet required. No API key. No rate limits. No monthly bill.

[SMILE]

[CUT]

[SCREEN] Split screen. Left: screenshot of cloud API billing page showing charges. Right: terminal showing local model running with $0 overlay

Here's the comparison that made me stop paying. Left side, my old API bill. See those charges? $47 in one week just from Claude API calls for my automation scripts. Right side, the same tasks running locally. Cost? Zero. Well, electricity. So like, a dollar fifty.

[CUT]

[CAMERA] Kalani back at desk, leaning forward

Now here's the part that makes this actually powerful and not just a "look I'm cheap" flex. The bridge.

See, having three separate machines is cool but kind of useless if they can't talk to each other. So I built a bridge server. Super simple concept.

When I send a prompt from my Mac, the system figures out which machine should handle it. Quick text question? Stays on Ceiba, she's fast. Need to run a big model or generate images? Routes to Cobo, he's got the GPU. Need something to run for six hours overnight? Goes to Hutia.

[SCREEN] Diagram showing the three machines connected with arrows, task routing labels

The routing happens automatically. I don't think about it. I just ask a question and the right machine answers.

[CUT]

[SCREEN] Demo: Kalani types a prompt on his Mac, terminal shows it routing to Cobo, response comes back

Watch this. I'm on my Mac right now. I'm going to send a prompt that needs GPU power.

[SCREEN] Shows the prompt being sent, routing indicator, response streaming back

See that? The prompt left my Mac, went to Cobo over my local network, Cobo processed it with the bigger model, and sent the response back. Took about four seconds. No cloud. No API. No bill.

[PAUSE]

[CAMERA] Kalani, genuine, direct to camera

But honestly, my favorite moment with this system was when I set up a research task before going to bed. I told it to find trending products in a specific niche, score them by profit margin, and compile a report.

[PAUSE]

I woke up. The report was sitting there. Done. Hutia had been running all night, pulling data, analyzing it, organizing it. While I was sleeping.

[SMILE]

That's when it stopped being a project and started being infrastructure.

[CUT]

[CAMERA] Kalani, calm, slightly more serious

Now let me be real with you about the downsides because I'm not going to pretend this is perfect.

One. Setup is not easy. If you've never used a terminal, this will be frustrating. It took me about two weeks to get everything working smoothly, and I wiped a drive by accident on day four. [LAUGH] Classic.

Two. Local models are not GPT-4. They're good. They're getting better every month. But for really complex reasoning, there's still a gap. I'd say local handles 85 to 90 percent of what I need. For the other 10 percent, I'll occasionally use a cloud model. But occasionally, not $200 a month worth.

Three. You have to maintain it. Updates, troubleshooting, the occasional restart when Cobo decides to be dramatic. It's not set and forget.

[CUT]

[CAMERA] Kalani, zoomed out slightly, calm energy

But here's what I keep coming back to. When you pay for AI subscriptions, you're a customer. When you build your own AI infrastructure, you're an operator. And that's a completely different relationship with the technology.

I own my tools. They don't reset. They don't change pricing on me. They don't go down because some server in Virginia had an issue. They're on my shelf. Running. Right now.

[PAUSE]

If you're technical, if you're a builder, if you're tired of renting intelligence from companies that don't know you exist, this is worth trying.

I put together a full guide that walks through everything. The hardware, the software, the bridge setup, the cost breakdown, all of it. It's linked in the description below.

[PAUSE]

And if you're not sure if this is for you, just drop a comment. I'll tell you honestly if your setup can handle it.

[CAMERA] Looks at camera, slight nod

I'll see you in the next one.

---

**End screen CTA:** "Full guide is linked in the description. Drop a comment if you have questions about your setup."
**Description:**
I was spending $200/month on AI subscriptions. ChatGPT, Claude, APIs, the works. So I built my own AI system using 3 old computers for under $1,000 total. Monthly cost: $0.

In this video I show you:
- The 3-machine setup (Ceiba, Cobo, Hutia)
- How to install Ollama and run local AI models
- The bridge system that routes tasks between machines
- Real cost comparison: cloud vs local
- Honest downsides you should know

FREE AI Employee Guide: [LINK]
Hardware list + setup instructions: [LINK]

Timestamps:
0:00 - Why I stopped paying for AI
1:30 - Meet the three machines
3:00 - Installing Ollama (live demo)
4:00 - Cloud vs Local cost comparison
5:00 - The bridge system explained
6:00 - The overnight research story
6:45 - Honest downsides
7:30 - Why ownership matters

#AI #LocalAI #Ollama #SaveMoney #AITools #TechSetup #MacMini #BuildDontRent #Solopreneur #AIEmployee
**Tags:** local AI, ollama tutorial, replace AI subscriptions, free AI tools, AI on old computers, mac mini AI, GTX 1080 Ti AI, self-hosted AI, AI for solopreneurs, stop paying for chatgpt

---
---

## VIDEO 2: I Built 25 Products in 7 Days Using AI (Here's How)
**Length:** 10 minutes
**Thumbnail text:** 25 Products, 7 Days
**Hook (first 5 seconds):** "Last week I had zero products. This week I have twenty-five. Let me show you exactly how."

---

[CAMERA] Kalani at desk, casual, slight disbelief energy

Last week I had zero products. This week I have twenty-five. Let me show you exactly how.

[PAUSE]

Okay so before you click away thinking this is one of those "AI can do everything" videos where some dude shows you ChatGPT making a PDF and calls it a business. It's not that. Some of these products are genuinely good. Some of them are mid. I'm going to show you all of them and be honest about which ones are which.

[CUT]

[CAMERA] Kalani leaning back, storytelling mode

Here's how this started. I had a Gumroad account. I had a Shopify store that I'm paying $39 a month for and making zero dollars from. And I had this realization that I've been "building" for months but I had nothing to sell. No products. No catalog. No revenue.

[PAUSE]

And my psychologist, she's been working with me on this pattern. I have ADHD, and one of the things that happens is I spend all my energy on the system and none on the output. I'll build the perfect workflow, the perfect folder structure, the perfect automation pipeline. And then never actually make the thing the pipeline is supposed to produce.

So I gave myself a challenge. Seven days. Twenty-five products. No excuses.

[CUT]

[CAMERA] Direct, clear

Here's the process I used for every single one.

Step one. Pick an idea. I have a backlog of like 200 ideas sitting in a file. Brain dumps, shower thoughts, things I wished existed. I just went through the list and picked ones that could realistically become a product in a few hours.

Step two. Outline it myself. This is important. I don't let AI decide what the product should be. I decide the structure, the sections, what makes it valuable. AI is the assistant, not the architect.

Step three. AI draft. I use Claude to write the first draft based on my outline. This is where the speed comes from. A draft that would take me six hours takes twenty minutes.

Step four. Human edit. This is where I spend most of my time. I rewrite sections that sound generic. I add my actual experience. I cut anything that feels like filler. The AI draft is maybe 60% of the final product.

Step five. Design. PDF layout, cover image, landing page. I have templates for this now so it goes fast.

Step six. Upload and list. Gumroad or Shopify depending on the product type.

[TEXT] Idea > Outline > AI Draft > Human Edit > Design > List

[CUT]

[SCREEN] Scrolling through the product catalog, 25 items visible

Alright here they are. Twenty-five products. Let me walk you through the highlights and the honestly-not-great ones.

[SCREEN] Opens a product page

This is Behike Finance. It's a budgeting tool I built in HTML. Budget tracker, debt payoff calculator, subscription manager, and a Financial Health Score that tells you how you're doing overall. This one is genuinely useful. I use it myself. I'm $35,000 in debt and the app that was supposed to help me budget costs money. So I built my own. This one I'd charge $14.99 for and feel good about it.

[CUT]

[SCREEN] Opens another product

This is the AI Employee Guide. How to set up local AI on your own machines, the exact setup I use with three computers. Walk-through, hardware list, architecture diagrams. This took the most work because it's technical and I wanted it to actually be useful, not just fluff.

[CUT]

[SCREEN] Scrolling through more products

I've got ebook templates, content calendars, automation workflow guides, a solopreneur operating system, prompt libraries. Some of these are solid. The Solopreneur OS and the AI Employee Guide, those are my best ones.

[CUT]

[CAMERA] Kalani, honest face

Now let me be real. Not all 25 are great.

[PAUSE]

Maybe five of them are genuinely good. Products I'd recommend to a friend. Another ten are decent. Useful, but not wow. And the remaining ten are honestly kind of mid. They exist, they have information in them, but they're not special.

[SMILE]

And that's fine. Because the point wasn't to make 25 masterpieces. The point was to break the pattern. To go from zero products to twenty-five products and prove to myself that I can actually ship things, not just build systems.

[CUT]

[SCREEN] Opens Behike OS in browser

But here's the one that surprised me. Behike OS.

[SCREEN] Shows the boot sequence loading

This is a virtual operating system that runs in your browser. I built it with HTML, CSS, and JavaScript. It has a desktop, a taskbar, working windows. You can open apps.

[SCREEN] Opens Music Studio inside Behike OS

This is the music studio. You can make beats right in the browser. Trap, lo-fi, reggaeton. Export as WAV.

[SCREEN] Opens Minecraft clone inside Behike OS

This is Minecraft. Running inside a website. Inside a fake operating system. [LAUGH]

[SCREEN] Opens the terminal

And there's a working terminal where you can type commands.

[CAMERA] Kalani, grinning

I built this mostly because I thought it would be funny. But people actually responded to it. It's the wow moment. When someone sees a full operating system running in their browser, they stop scrolling.

[CUT]

[SCREEN] Opens Behike Finance again

And this is the practical moment. Behike Finance. When someone sees a real budgeting tool that they can actually use, with their actual numbers, that's when they think, okay this person is building real things.

[CUT]

[CAMERA] Kalani, centered, slight lean forward

Here's what I learned from this week.

The trick isn't the AI. The trick is knowing what to tell it.

[PAUSE]

If you give AI a vague prompt, you get a vague product. If you give it a specific outline based on a real problem you actually have, you get something useful.

Every good product in my catalog started the same way. I had a problem. I couldn't afford budgeting apps. I wanted music for my reels without copyright issues. I needed a system to run AI locally. The product is just the solution packaged up so other people can use it too.

[CUT]

[CAMERA] Direct, practical

So if you're sitting there with zero products and thinking you need to make everything perfect before you launch, let me save you some time. You don't.

Ship something. Ship twenty-five somethings. Five of them will be good. Run with those five. Improve them. Let the other twenty sit there. They might become good later, or they might not. Either way, you went from zero to twenty-five, and that momentum is worth more than any perfect product that lives in your head forever.

[PAUSE]

I have a free ebook linked in the description that goes deeper on the AI-assisted product creation process. What tools I use, how I structure outlines, the editing workflow, all of it.

And if you want to see Behike OS or try Behike Finance, those links are there too.

[CAMERA] Nods

Twenty-five products. Seven days. Most of them mid. Five of them solid. But the scoreboard moved. And that's what matters.

I'll see you in the next one.

---

**End screen CTA:** "Free ebook on AI product creation linked below. Go check out Behike OS in your browser, it's kind of ridiculous."
**Description:**
I went from 0 products to 25 in one week using AI as my drafting assistant. Here's the exact process, what worked, what didn't, and which products are actually worth buying.

Process: Idea > Outline > AI Draft > Human Edit > Design > List

Highlights:
- Behike Finance (budgeting tool): [LINK]
- Behike OS (browser operating system): [LINK]
- AI Employee Guide: [LINK]
- Full product catalog: [LINK]

FREE Ebook - AI Product Creation Process: [LINK]

Timestamps:
0:00 - Zero to twenty-five
1:00 - The ADHD pattern (building systems, not products)
2:30 - The 6-step process
4:00 - Product catalog walkthrough
5:30 - Behike OS demo (the wow moment)
6:30 - Behike Finance demo (the practical moment)
7:30 - Honest assessment: 5 good, 10 decent, 10 mid
8:30 - What I learned
9:30 - Your turn

#AIProducts #DigitalProducts #Gumroad #Shopify #Solopreneur #BuildInPublic #ADHD #ProductCreation #AITools #ShipIt
**Tags:** digital products with AI, gumroad products, build products fast, AI product creation, 25 products one week, solopreneur, ship fast, digital product business, AI assistant workflow, build in public

---
---

## VIDEO 3: ADHD is a Superpower for Building Businesses (Not a Weakness)
**Length:** 7 minutes
**Thumbnail text:** ADHD = Superpower
**Hook (first 5 seconds):** "Everyone says ADHD makes you bad at business. They're wrong. And I can prove it."

---

[CAMERA] Kalani at desk, calm but direct, looking straight at camera

Everyone says ADHD makes you bad at business. They're wrong. And I can prove it.

[PAUSE]

I got diagnosed about a year ago. I'm working with a psychologist. She's the one who helped me understand that the problem was never focus. The problem was aim.

[CUT]

[CAMERA] Slightly closer, personal

Let me explain what I mean. People with ADHD don't lack focus. We have a different relationship with focus. When something clicks, when something genuinely interests us, we don't just focus on it. We disappear into it. Hours go by. We forget to eat. We build entire systems at 3am because the idea grabbed us and wouldn't let go.

That's called hyperfocus. And it's the single most powerful tool for building a business that most productivity gurus will never understand. Because they've never experienced it.

[CUT]

[CAMERA] Leaning back, casual

The problem is the other side. The tasks that don't grab us. The admin work. The follow-ups. The boring but important stuff that keeps a business running. That's where ADHD bites. Not because we can't do it, but because our brains literally will not prioritize it over something more interesting.

So the question isn't "how do I fix my ADHD so I can be productive." The question is "how do I build a business that works with my brain instead of against it."

[PAUSE]

[CUT]

[CAMERA] Direct, counting on fingers

My psychologist taught me a framework. I'm going to give you the whole thing because it changed how I operate.

Number one. The Post-It Mental principle.

[TEXT] Post-It Mental

Here's the idea. When your ADHD brain has a thought, an idea, a to-do, a random connection, it needs to go somewhere immediately. Not in five minutes. Not when you get to your desk. Right now.

Because if you don't capture it, two things happen. Either you forget it, which is frustrating. Or you try to hold it in your head, which takes up mental bandwidth and makes everything else harder.

So I built a system for this. I have a Telegram bot called BehiqueBot. When an idea hits me, I send it a voice message. It transcribes it, categorizes it, and saves it. Done. Out of my head. Captured. I can come back to it later when I'm in the right mode.

[PAUSE]

This alone reduced my anxiety by like 40 percent. Not even exaggerating.

[CUT]

[CAMERA] Still counting

Number two. Break tasks into the smallest possible unit.

[TEXT] Smallest Possible Unit

Normal productivity advice says "break tasks into subtasks." ADHD productivity means breaking subtasks into sub-subtasks. Until the next action is so small and so specific that starting it requires zero willpower.

Not "work on the website." Not even "design the homepage." More like "open the code editor and change the background color." That's it. That's the task. Once you start, hyperfocus kicks in and you'll do three hours of work. But you need the entry point to be tiny.

[CUT]

Number three. One thing at a time. Seriously.

[TEXT] One Thing At A Time

I have seven active projects right now. eBay reselling, Shopify store, a Telegram SaaS, ebooks, AI video content, an automation business, and BehiqueBot. Seven things.

My brain wants to work on all of them simultaneously. And when I try to, I make progress on none of them. I just bounce around feeling busy but building nothing.

So the rule is: one project per session. I pick one before I sit down. That's what I'm working on. Everything else doesn't exist until this session is over.

[CUT]

Number four. Visual output.

[TEXT] Visual/Structured Output

ADHD brains process information better when it's visual. Tables, diagrams, color-coded lists, progress bars. Not walls of text. Not long paragraphs of instructions.

I structure all my notes and project tracking visually. If I can't see my progress, it doesn't feel real. And if it doesn't feel real, I won't do it.

[CUT]

[CAMERA] More personal, softer

Number five. And this is the one nobody talks about. Validate effort, not just results.

[TEXT] Effort Over Results

When you have ADHD, you experience a lot of false starts. A lot of days where you sat down, you tried, and it just didn't click. And the normal response to that is "I wasted today. I'm behind. I failed."

My psychologist reframed that. You showed up. That matters. You sat down and tried. That's the hardest part. The result will come. But the habit of showing up is what you're actually building.

[PAUSE]

That reframe alone changed my relationship with work. I stopped punishing myself for the days that didn't produce results. And ironically, I started having more productive days because the pressure was off.

[CUT]

[CAMERA] Kalani, energized but controlled

So here's what my ADHD brain actually built in one week. Twenty-five digital products. A budgeting app. A music studio. A virtual operating system. An AI system running on three old computers. Content for four Instagram accounts.

[PAUSE]

My ADHD brain built more in one week than most people build in a month.

[PAUSE]

Not because I'm special. Because I stopped trying to fix my brain and started building a system that matches how my brain actually works.

[CUT]

[CAMERA] Calm, closing energy

If you have ADHD, or you think you might, stop reading productivity advice written by neurotypical people. It's not for you. It's like reading a swimming manual written by someone who's never been in water.

Find what works for your brain. Build systems around it. And then watch what happens when hyperfocus has a target.

[PAUSE]

I wrote a chapter about this in the Behike Method. It's the ADHD section. I'm giving away the preview for free. Link in the description.

And if you want to hear more about BehiqueBot, the Telegram bot I built for capturing ideas, that's linked there too.

[CAMERA] Slight nod, calm

Your brain isn't broken. It's just wired differently. Build for the wiring you have.

I'll see you in the next one.

---

**End screen CTA:** "Free chapter preview linked below. And seriously, get yourself a capture system. It changes everything."
**Description:**
I have ADHD. I was diagnosed last year. I'm working with a psychologist who taught me a framework that completely changed how I build.

ADHD isn't a weakness for entrepreneurs. Hyperfocus is the most powerful productivity tool that exists. The problem isn't focus. The problem is aim.

In this video:
- Why hyperfocus is a business superpower
- The Post-It Mental principle (capture everything immediately)
- How to break tasks for ADHD brains (smaller than you think)
- Why "effort over results" changed my productivity
- What my ADHD brain built in one week

FREE Chapter - The Behike Method (ADHD Section): [LINK]
BehiqueBot info: [LINK]

#ADHD #ADHDEntrepreneur #Hyperfocus #Productivity #BuildDifferent #MentalHealth #Solopreneur #ADHDBusiness #Neurodivergent #BuildInPublic
**Tags:** ADHD entrepreneur, ADHD business, hyperfocus superpower, ADHD productivity, ADHD tips, building with ADHD, neurodivergent entrepreneur, ADHD framework, post-it mental, ADHD diagnosed

---
---

## VIDEO 4: How to Start a Business From Puerto Rico With $0
**Length:** 8 minutes
**Thumbnail text:** $0 Business from PR
**Hook (first 5 seconds):** "I'm building a business from Puerto Rico with literally zero dollars. And Puerto Rico might actually be the best place to do it."

---

[CAMERA] Kalani, casual, maybe near a window with natural light

I'm building a business from Puerto Rico with literally zero dollars. And Puerto Rico might actually be the best place to do it.

[PAUSE]

Most people hear "Puerto Rico" and think limitation. Small island. Far from tech hubs. Limited market. But I'm going to show you why that thinking is backwards.

[CUT]

[CAMERA] Direct, informative

First thing. Act 60. If you don't know what this is, listen up.

[TEXT] Act 60: 4% Corporate Tax Rate

Puerto Rico has Act 60, which gives qualifying businesses a 4 percent corporate tax rate. Four percent. The mainland US rate is 21 percent. Some states add another 5 to 10 on top of that.

So if you're running a digital business, selling products online, doing consulting, building software, and you're based in Puerto Rico, you could be paying 4 percent instead of 25 to 30 percent in taxes.

Now I'm going to be straight with you. I'm not using Act 60 yet because I'm at zero revenue. [LAUGH] You need a business that makes money before tax advantages matter. But knowing this is ahead of me is motivating. The infrastructure I'm building now gets taxed at 4 percent when it starts producing.

[CUT]

[CAMERA] Casual, walking-and-talking energy if possible, or just relaxed at desk

Second thing. Digital businesses don't care where you live.

I sell digital products on Gumroad. My customers are in the US, Europe, Latin America. They don't know I'm in Puerto Rico and they don't care. The internet doesn't have borders.

My eBay store ships products from US retailers to US customers. I never touch the product. I just find the deal and connect the buyer to it. I could do that from anywhere. I happen to do it from Bayamon.

[SMILE]

[CUT]

[CAMERA] More serious, real talk

Now let me talk about the thing nobody mentions. I call it the Puerto Rican envy problem.

[PAUSE]

When you're building a business in Puerto Rico and your customers are stateside, there's this weird friction. You see creators on YouTube with their nice studios, their fast internet, their same-day Amazon deliveries. And you start thinking, "if I was there, I'd be further along."

That's a trap. Because the truth is, the constraints force creativity.

I run AI on old laptops because I can't afford cloud subscriptions. That became my best content. I built a budgeting app because I couldn't afford the paid ones. That became a product. I do everything locally because sending data to the cloud costs money I don't have.

[PAUSE]

Every limitation became a product or a story. That's the advantage.

[CUT]

[CAMERA] Practical, step-by-step energy

So here's how I'm actually doing it with zero dollars. Let me walk you through the tools.

[TEXT] The $0 Stack

Gumroad. Free to list products. They take a cut when you sell. Until you sell something, you pay nothing.

GitHub. Free. All my code, all my websites, hosted for free through GitHub Pages.

Ollama. Free. Local AI. No subscriptions.

Canva. Free tier for basic design work.

My own machines. Already had them. Ceiba, Cobo, Hutia. Upfront cost? Under $1,000 total. But I already owned most of the hardware.

[SCREEN] Shows Gumroad storefront, GitHub repos, local AI running

Everything you're looking at right now cost me zero dollars in monthly fees.

[CUT]

[CAMERA] Direct

Now here's the real strategy. Build for strangers.

[PAUSE]

What I mean is, stop building for people who know you. Your friends aren't your customers. Your family isn't your market. Build for strangers who have a problem that you solved for yourself.

I built Behike Finance because I needed a budgeting tool. There are millions of people who also need a budgeting tool. I don't need to know any of them. I just need to put the product where they can find it.

I built the AI Employee Guide because I figured out how to run local AI. There are thousands of people trying to figure out the same thing right now. I don't need to be in Silicon Valley to reach them.

[CUT]

[SCREEN] Shows the product store, the tools running, the content pipeline

Here's everything running. Products on Gumroad. Free tools on the website. AI running locally. Content going out to Instagram. All from Puerto Rico. All for zero dollars in monthly costs.

[CUT]

[CAMERA] Kalani, closing energy, genuine

I'm not going to pretend this is easy. It's not. There are days where the internet goes out and I lose half a day. There are moments where I look at people in Austin or Miami or New York and think, that would be easier.

But then I remember. 4 percent tax rate. Low cost of living. My family is here. My faith community is here. And the internet works the same everywhere.

[PAUSE]

Puerto Rico isn't a limitation. It's a position. And I'm building from it.

If you want to see the full breakdown of every tool I use, the Solopreneur OS has everything. It's linked in the description.

[CAMERA] Nods

Dale. I'll see you in the next one.

---

**End screen CTA:** "Solopreneur OS linked below. If you're building from PR or Latin America, drop a comment. I want to hear what you're working on."
**Description:**
I'm 21, in Puerto Rico, building a business with $0 in startup costs. Here's why Puerto Rico might actually be the best place to build a digital business.

In this video:
- Act 60: 4% corporate tax rate (vs 21%+ mainland)
- The $0 tool stack I use (Gumroad, GitHub, Ollama, Canva)
- The "Puerto Rican envy" trap and why constraints create advantages
- Why you should build for strangers, not friends
- Full demo of everything running locally

Solopreneur OS: [LINK]
Free tools: [LINK]

#PuertoRico #Solopreneur #StartABusiness #ZeroDollars #Act60 #DigitalBusiness #BuildFromAnywhere #PRBusiness #Entrepreneur #IslandLife
**Tags:** business from Puerto Rico, Act 60 tax, start business zero dollars, digital business island, solopreneur, Puerto Rico entrepreneur, free business tools, build from anywhere, gumroad free, local AI business

---
---

## VIDEO 5: I Made a Music Studio in HTML (And You Can Too)
**Length:** 6 minutes
**Thumbnail text:** Browser Music Studio
**Hook (first 5 seconds):** "This music studio runs in your browser. It cost me nothing to build. And you can make beats in it right now."

---

[CAMERA] Kalani, slight grin, headphones around neck

This music studio runs in your browser. It cost me nothing to build. And you can make beats in it right now.

[PAUSE]

So I had this problem. I make reels for Instagram. Four accounts. And every single reel needs background music. But every time I used a song from Spotify or YouTube, I'd get a copyright claim. And the royalty-free libraries? They all sound the same. That generic ukulele-and-claps stuff that makes everything feel like a LinkedIn ad.

[LAUGH]

So I thought, what if I just made my own music?

[CUT]

[SCREEN] Opens Behike Music Studio in browser

This is Behike Music Studio. It's a web app. HTML, CSS, JavaScript. No downloads. No installations. You open it in your browser and you have a full beat-making tool.

[SCREEN] Shows the interface, genre selector, controls

You pick a genre up top. Right now I've got Trap, Lo-fi, Reggaeton, Ambient, and a few others. Each genre comes with its own sounds, its own drum patterns, its own vibe.

Let me make something live.

[SCREEN] Selects Trap, hits play

[BROLL] Beat playing, Kalani nodding to it, adjusting controls

Hear that? Trap beat. 808s, hi-hats, snare. All generated by the Web Audio API. No samples. No downloaded files. Your browser is literally synthesizing these sounds in real time.

[CUT]

[SCREEN] Switches to Lo-fi

Now let me switch to lo-fi.

[BROLL] Lo-fi beat playing, mellower vibe

Different feel completely. Softer drums. Vinyl crackle. Warm bass. This is what I use for my chill content. Study reels, reflection posts, that kind of thing.

[CUT]

[SCREEN] Switches to Reggaeton

Now reggaeton. Because, mira, I'm Puerto Rican. [SMILE]

[BROLL] Reggaeton beat playing, dembow pattern

That dembow pattern. Classic. I use this one for anything high-energy.

[CUT]

[SCREEN] Clicks export, downloads WAV file, opens it in a media player, plays it back

And here's the key part. Export as WAV. You click export, it generates a WAV file, you download it. That's your music. You made it. You own it. Zero copyright issues. Use it on YouTube, Instagram, TikTok, wherever. Nobody can claim it because you created it.

[CAMERA] Kalani, satisfied

I use this for all my reel background music now. Every single reel. No more scrolling through royalty-free libraries. No more copyright worries. I just open the studio, pick a genre, tweak it until it sounds right, export, done.

[CUT]

[CAMERA] Slightly technical but keeping it simple

Now for the nerds in the audience. [SMILE] Quick explanation of how this works.

The Web Audio API is built into every modern browser. It can generate sound waves, apply effects, control timing. It's the same technology that powers browser games with sound effects.

I'm using it to create drum patterns with synthesized sounds. The 808 bass is an oscillator with specific frequency curves. The hi-hats are filtered noise. The snare is a combination of noise and a quick tone burst.

[TEXT] Web Audio API = Your browser can make sound

You don't need to understand any of that to use the studio. But if you're a developer and you want to build something like this, the Web Audio API documentation is free and it's actually really well written.

[CUT]

[CAMERA] Practical, direct

One more thing. This entire music studio is part of Behike OS, the browser operating system I built. But the studio also works standalone. You can just open it by itself.

If you want to try it, the link is in the description. It's free. Open it. Make a beat. Use it in your next video.

[PAUSE]

And if you build something cool with it, send it to me. I genuinely want to hear what people make.

[CAMERA] Taps headphones

I'll see you in the next one.

---

**End screen CTA:** "Link to try the Music Studio is below. It's free. Go make something."
**Description:**
I built a music studio that runs entirely in your browser. No downloads. No subscriptions. Just open it and make beats.

Genres: Trap, Lo-fi, Reggaeton, Ambient, and more
Export: WAV files you own completely (zero copyright issues)
Tech: HTML + CSS + JavaScript + Web Audio API

I built this because copyright music was killing my reels. Now I make all my own background music.

Try Behike Music Studio (FREE): [LINK]
Behike OS (full browser operating system): [LINK]

Timestamps:
0:00 - The copyright problem
1:00 - Music Studio demo
1:30 - Making a Trap beat live
2:30 - Lo-fi beat demo
3:00 - Reggaeton beat demo
3:30 - Exporting as WAV
4:00 - How Web Audio API works (simple)
5:00 - Try it yourself

#MusicStudio #WebAudioAPI #FreeBeatMaker #HTML #JavaScript #BrowserApp #CopyrightFree #ReelMusic #MakeBeats #CodeProject
**Tags:** browser music studio, web audio api, make beats free, copyright free music, html music app, beat maker browser, free music for reels, javascript music, make your own beats, trap beat maker

---
---

## VIDEO 6: Stop Paying for Budgeting Apps
**Length:** 5 minutes
**Thumbnail text:** Free Budget App
**Hook (first 5 seconds):** "Mint wants $5 a month. YNAB wants $15. Mine is free. Forever."

---

[CAMERA] Kalani, direct, no fluff energy

Mint wants $5 a month. YNAB wants $15. Mine is free. Forever.

[PAUSE]

And before you say "just use a spreadsheet," no. Spreadsheets are ugly, they're confusing, and nobody actually opens them consistently. I tried. For two years. Didn't work.

[CUT]

[CAMERA] Personal, vulnerable

Let me tell you why I built this. I'm $35,000 in debt. Student loans, mostly. Some credit card stuff from when I didn't know what I was doing. And I realized I couldn't afford the app that was supposed to help me get out of debt.

[PAUSE]

Think about that for a second. The budgeting app costs money. If you're broke enough to need a budgeting app, you probably can't afford the budgeting app. That's insane.

[LAUGH]

So I built my own. It took me three days. And it does everything I needed.

[CUT]

[SCREEN] Opens Behike Finance in browser

This is Behike Finance. It runs in your browser. No account needed. No sign-up. No data sent anywhere. Everything stays on your device.

[SCREEN] Shows the budget tab

Budget tab. You put in your income. You add your expenses by category. Rent, food, transportation, subscriptions, whatever. It shows you what's left. Simple. Clean.

[SCREEN] Shows the debt payoff calculator

Debt payoff. This is the one I use the most. You enter your debts, the interest rates, your monthly payment. It calculates how long it'll take to pay them off using avalanche or snowball method. It shows you exactly how much interest you'll save by paying even $50 extra per month.

[TEXT] Avalanche = highest interest first | Snowball = smallest balance first

[SCREEN] Shows subscription tracker

Subscription tracker. This one is sneaky useful. You list all your subscriptions and it shows your total monthly and yearly cost. I found out I was spending $127 a month on subscriptions. Some of them I forgot I had. [SMILE]

[SCREEN] Shows Financial Health Score

And this is the Financial Health Score. It takes your income, expenses, debt, savings, and gives you a score from 0 to 100. It tells you where you stand. Not a credit score. More like a "how stressed should I be about money" score.

[PAUSE]

Mine is not great right now. [LAUGH] But it's improving. And seeing the number go up week over week is genuinely motivating.

[CUT]

[CAMERA] Kalani, real

Here's what I want you to understand. This isn't a polished Silicon Valley product. There's no AI chatbot giving you financial advice. There's no gamification or achievement badges. It's a tool. You open it, you put in your numbers, you see where you stand.

That's it. And that's enough.

[PAUSE]

I use it every Sunday. Takes me 10 minutes. I update my numbers, check my debt payoff timeline, review subscriptions I might be able to cut. Then I close it and go on with my week.

[CUT]

[CAMERA] Direct, CTA energy

The app is free. The link is in the description. You don't even need to give me your email.

If you want the premium version with extra features, that's $14.99. But the free version does the core job.

[PAUSE]

Thirty-five thousand in debt. Can't afford a budgeting app. So I built one.

[CAMERA] Shrugs, slight smile

That's the whole story. I'll see you in the next one.

---

**End screen CTA:** "Behike Finance link is below. It's free. Stop giving YNAB fifteen dollars a month."
**Description:**
I'm $35,000 in debt. I couldn't afford the budgeting app that was supposed to help me get out of debt. So I built my own.

Behike Finance features:
- Budget tracker (income vs expenses by category)
- Debt payoff calculator (avalanche + snowball methods)
- Subscription tracker (find hidden costs)
- Financial Health Score (0-100, see where you stand)

No sign-up. No data collection. Runs entirely in your browser.

Try Behike Finance (FREE): [LINK]
Premium version ($14.99): [LINK]

#BudgetingApp #FreeBudgetTool #DebtPayoff #PersonalFinance #YNAB #MintAlternative #StopPayingForApps #DebtFree #MoneyManagement #BuildYourOwn
**Tags:** free budgeting app, YNAB alternative free, debt payoff calculator, budget tracker, subscription tracker, financial health score, personal finance tool, stop paying for budget apps, free finance app, student debt

---
---

## VIDEO 7: The $0 AI Stack (Everything You Need, Nothing You Don't)
**Length:** 7 minutes
**Thumbnail text:** $0 AI Stack
**Hook (first 5 seconds):** "You don't need ChatGPT Plus. You don't need Midjourney. Let me show you what you actually need."

---

[CAMERA] Kalani, matter-of-fact, no hype

You don't need ChatGPT Plus. You don't need Midjourney. Let me show you what you actually need.

[PAUSE]

I added up what the "recommended AI stack" costs if you follow what most YouTubers tell you. ChatGPT Plus, $20. Claude Pro, $20. Midjourney, $30. Runway for video, $15. Jasper for copy, $49. Notion AI, $10. An automation platform, $30 minimum. Some sort of transcription tool, another $10.

[TEXT] Total: $184/month minimum

That's $184 a month. And some people are spending way more.

Here's what I use instead. Seven tools. Total monthly cost: zero.

[CUT]

[SCREEN] Terminal, clean

Tool number one. Ollama.

[SCREEN] Shows ollama.com

This is the foundation. Ollama lets you run open-source AI models on your own computer. Llama 3, Mistral, CodeLlama, Phi. All free. All local. All private.

Let me install it right now.

[SCREEN] Downloads and installs Ollama, two-minute real-time speed-up

Done. That took two minutes. Now let me pull a model.

[SCREEN] Types: ollama pull llama3

This downloads the model to your machine. Takes a few minutes depending on your internet. But once it's there, it's there. No internet required to run it after this.

[SCREEN] Types: ollama run llama3, sends a prompt, response streams

There it is. Running on my machine. Ask it anything. Write code. Summarize documents. Draft emails. This replaces ChatGPT Plus for 90 percent of tasks.

[CUT]

[CAMERA] Quick, energetic

Tool number two. Open WebUI.

[SCREEN] Shows Open WebUI running in browser

This gives you a ChatGPT-style interface for your local models. Nice chat window, conversation history, model switching. So you're not stuck in the terminal.

Free. Open source. Self-hosted.

[CUT]

Tool number three. Stable Diffusion via ComfyUI.

[SCREEN] Shows ComfyUI interface

Image generation. This replaces Midjourney. It runs on your GPU. The results are good. Not Midjourney-perfect on every prompt, but for product images, thumbnails, social media graphics? More than enough.

Free. Runs locally.

[CUT]

Tool number four. Whisper.

[SCREEN] Shows Whisper transcribing audio

Voice transcription. OpenAI released Whisper as open source. It runs locally. I use it for transcribing voice memos, podcast clips, video content. It's accurate and it's fast.

This is what my Telegram bot uses to transcribe my voice messages. Free.

[CUT]

Tool number five. n8n.

[SCREEN] Shows n8n workflow interface

Automation. This is the open-source alternative to Zapier, Make, all those paid automation platforms. You build workflows visually. Connect any API. Trigger actions based on events.

I use this for my content pipeline, my eBay research automation, and email workflows. Self-hosted, free.

[CUT]

Tool number six. Claude Code.

[CAMERA] Slight lean in

Okay, this one does have a paid API behind it, but hear me out. Claude Code is a terminal-based AI coding assistant. And for the amount I use it, the API costs me maybe $3 to $5 a month. Not $20 for a Pro subscription. Just pay-as-you-go for what I actually use.

For heavy coding sessions, I switch to my local models. For quick, precise tasks where I need the best reasoning, I'll use Claude Code. Best of both worlds.

[CUT]

Tool number seven. Behike Music Studio.

[SCREEN] Opens the music studio

Yeah, I'm counting this. [SMILE] I built my own music tool. It replaces paying for royalty-free music libraries or audio generation tools.

Free. Runs in your browser.

[CUT]

[CAMERA] Kalani standing or sitting, final summary energy

So let's add it up.

[TEXT] Scrolling comparison

ChatGPT Plus ($20) -> Ollama + Open WebUI ($0)
Midjourney ($30) -> Stable Diffusion ($0)
Jasper ($49) -> Local models ($0)
Zapier ($30) -> n8n ($0)
Transcription ($10) -> Whisper ($0)
Music ($15) -> Behike Music Studio ($0)
Claude Pro ($20) -> Claude Code API (~$4)

Old total: $184/month. New total: roughly $4/month.

[PAUSE]

That's a $180 per month difference. Over a year, that's $2,160. Over three years, $6,480. And unlike subscriptions, local tools don't increase in price.

[CUT]

[CAMERA] Honest, grounded

Now. Is the setup harder? Yes. Does it require some technical knowledge? Yes. Are the local models as good as the absolute best cloud models? For some tasks, no.

But for the work I do every day, writing content, generating ideas, automating workflows, making music, transcribing voice notes, this stack handles it. And it costs me basically nothing.

[PAUSE]

I wrote an ebook that walks through the entire setup. Every tool, every installation step, every configuration. It's linked in the description. It's free.

[CAMERA] Casual nod

$184 a month or $4 a month. The tools are the same. The price doesn't have to be.

I'll see you in the next one.

---

**End screen CTA:** "Free ebook walking through the full setup is in the description. Go save some money."
**Description:**
The "recommended AI stack" costs $184/month. Mine costs $4. Here are the 7 free tools I use instead.

1. Ollama (replaces ChatGPT) - FREE
2. Open WebUI (chat interface) - FREE
3. Stable Diffusion/ComfyUI (replaces Midjourney) - FREE
4. Whisper (replaces transcription tools) - FREE
5. n8n (replaces Zapier) - FREE
6. Claude Code API (pay-as-you-go) - ~$4/mo
7. Behike Music Studio (replaces music libraries) - FREE

Total savings: $180/month = $2,160/year

FREE Ebook - Complete Setup Guide: [LINK]

#FreeAITools #AIStack #Ollama #StableDiffusion #n8n #Whisper #SaveMoney #AISetup #LocalAI #ReplaceSubscriptions
**Tags:** free AI tools, replace chatgpt, ollama tutorial, stable diffusion free, n8n automation, whisper transcription, free AI stack, AI tools 2026, save money on AI, local AI setup

---
---

## VIDEO 8: I Built a Virtual Computer Inside a Website
**Length:** 6 minutes
**Thumbnail text:** Browser OS + Minecraft
**Hook (first 5 seconds):** "This is an operating system. It runs in your browser. And it has Minecraft."

---

[CAMERA] Kalani, barely containing a smile

This is an operating system. It runs in your browser. And it has Minecraft.

[PAUSE]

I know how that sounds. Let me just show you.

[CUT]

[SCREEN] Opens behike.com (or wherever Behike OS is hosted), blank page, then boot sequence starts

[BROLL] Dramatic pause as boot sequence loads, terminal-style text appearing

Watch the boot sequence. This is all CSS and JavaScript animations. No video file. The browser is rendering this in real time.

[SCREEN] Desktop loads. Taskbar appears. Icons populate.

There it is. Behike OS. A full desktop environment running in a browser tab. You've got a taskbar at the bottom, app icons, a wallpaper, window management. You can drag windows, resize them, minimize them, the whole thing.

[CUT]

[SCREEN] Clicks on Minecraft icon, game opens in a window

Minecraft. Well, a Minecraft clone. Voxel-based, first-person, you can place and break blocks. It runs in a window inside the OS inside your browser.

[SCREEN] Plays for 30 seconds. Walking around, placing blocks, breaking them.

[CAMERA] Kalani off-screen, laughing

This is three layers of abstraction deep. A game, inside a fake operating system, inside a real web browser, inside a real operating system. My computer science professor would either be proud or horrified.

[LAUGH]

[CUT]

[SCREEN] Opens Music Studio app inside Behike OS

Here's the Music Studio I showed you earlier. But running inside the OS this time. Same functionality. Pick a genre, make a beat, export it.

[SCREEN] Opens Terminal app

Terminal. This is a functional command line. You can type commands, navigate a virtual file system, run little programs I built in.

[SCREEN] Types a few commands, gets responses

[CUT]

[SCREEN] Opens Store app

And this is the Store. Inside the OS, there's a store where you can browse all the Behike products. It's like having an app store inside a web app. [SMILE]

[CUT]

[CAMERA] Kalani, back on camera, genuine

Okay so let me be honest about why I built this.

[PAUSE]

Part of it was a portfolio piece. I'm a CS student. Building a web-based operating system shows you understand window management, event handling, state management, audio APIs, 3D rendering. It's a resume flex.

Part of it was just to see if I could. Can you build something that feels like a real operating system using only HTML, CSS, and JavaScript? Turns out, yeah. You can get surprisingly close.

But the real reason? It's a show-stopper. When I put this in front of someone, whether it's a potential client, a follower, or a recruiter, they stop. They pay attention. Because nobody expects to open a website and see a full operating system with Minecraft in it.

[PAUSE]

And in a world where everyone has the same portfolio with the same to-do app and the same weather widget, that matters.

[CUT]

[CAMERA] Slightly technical

For the developers watching. The whole thing is vanilla HTML, CSS, and JavaScript. No React. No frameworks. Just raw browser APIs.

The window management system uses absolute positioning and z-index stacking. The Minecraft clone uses Three.js for 3D rendering. The music studio uses the Web Audio API. The terminal parses commands with basic string matching and a virtual file tree stored in a JavaScript object.

Total file size? Under 5 megabytes for the whole OS. It loads fast.

[CUT]

[CAMERA] Closing, excited but controlled

If you want to try it, the link is in the description. Open it on desktop for the best experience. Mobile works but it's not ideal because, you know, you're running an entire operating system in a phone browser. [SMILE]

And if you're a developer who wants to build something like this, I'm thinking about making a tutorial series. Drop a comment if you'd watch that.

[CAMERA] Direct

I built a virtual computer inside a website. Because I could. And because sometimes the best portfolio piece is the one that makes people say "wait, what?"

I'll see you in the next one.

---

**End screen CTA:** "Link to try Behike OS is below. Open it on your computer. Play Minecraft in your browser. Tell me it's not cool."
**Description:**
I built a full operating system that runs in your browser. Desktop, taskbar, draggable windows, and apps including Minecraft, a Music Studio, a Terminal, and a Store.

Built with: HTML + CSS + JavaScript (no frameworks)
Total size: Under 5MB

Apps included:
- Minecraft (voxel clone, playable)
- Music Studio (make beats, export WAV)
- Terminal (functional command line)
- Store (browse products)

Try Behike OS: [LINK]

#WebDev #JavaScript #HTML #CSS #BrowserOS #Minecraft #PortfolioPiece #CodeProject #VanillaJS #WebApp
**Tags:** browser operating system, javascript OS, web based operating system, minecraft in browser, html css javascript project, web dev portfolio, vanilla javascript, threejs minecraft, web audio api, cool coding project

---
---

## VIDEO 9: How I Automate My Instagram (Zero Manual Posting)
**Length:** 8 minutes
**Thumbnail text:** Auto Instagram Pipeline
**Hook (first 5 seconds):** "I run four Instagram accounts. I spend 30 minutes a week on it. Let me show you the system."

---

[CAMERA] Kalani, casual, sitting comfortably

I run four Instagram accounts. I spend 30 minutes a week on it. Let me show you the system.

[PAUSE]

Let me be clear about what I mean by 30 minutes. That's the human time. The time I spend reviewing, editing, approving. The system itself runs for hours. It fetches news, generates carousels, writes captions, creates reel scripts, translates to Spanish. I just approve the output and schedule it.

[CUT]

[CAMERA] Context setting

First, let me tell you about the four accounts so this makes sense.

[TEXT] @behikeai - AI/tech news
[TEXT] @kalaniandrez - personal brand
[TEXT] @s0ftrewind - emotional stories (English)
[TEXT] @dulc3recuerdo - emotional stories (Spanish)

BehikeAI is AI and tech news. Neutral, informative, numbers-driven.

KalaniAndrez is my personal brand. First person, vulnerable, showing the process.

S0ftRewind and Dulc3Recuerdo are emotional story accounts. Short, poetic, visual. Same content, different languages.

Each account has a different voice. Different audience. Different content style. Managing all four manually would be a full-time job.

[CUT]

[SCREEN] Shows the content pipeline architecture, can be a diagram or actual n8n workflow

Here's the pipeline. I'll walk you through each step.

[TEXT] Step 1: News Fetch

Step one. Every morning, the system pulls the latest AI and tech news from multiple sources. RSS feeds, news APIs, trending topics. It collects about 30 to 50 articles per day.

[SCREEN] Shows raw news data coming in

Step two. Filtering and ranking. Not every article is worth posting about. The system scores each article based on relevance, newness, and audience interest. The top 5 to 8 articles make the cut.

[TEXT] Step 2: Filter + Rank (Top 5-8 daily)

Step three. Content generation.

[SCREEN] Shows the output: carousel slides, captions

For each selected article, the system generates a carousel. That means 5 to 7 slides with the key information, designed in a consistent visual style. Plus a caption that follows the Voice Bible rules. No banned words. No AI-sounding fluff. Specific numbers. Clear takeaways.

[TEXT] Step 3: Generate Carousels + Captions

Step four. Reel scripts.

From the same articles, it generates 2 to 3 reel scripts per day. These are short, punchy, designed for me to read on camera or use as voiceovers.

[TEXT] Step 4: Generate Reel Scripts

Step five. Translation.

Everything generated for BehikeAI gets automatically translated to Spanish for the Latin American audience. But not literal translation. The system rewrites it in natural LATAM Spanish. "Tu" form. Tech terms stay in English.

[TEXT] Step 5: Translate to LATAM Spanish

[CUT]

[CAMERA] Kalani, leaning forward

Now let me run the pipeline live so you can see the output.

[SCREEN] Triggers the pipeline (could be a script, n8n workflow, or command)

Watch. It's pulling today's news right now.

[SCREEN] Shows articles being fetched, scored, filtered

Eight articles made the cut. Now it's generating content.

[SCREEN] Shows carousels being generated one by one

There's carousel number one. Five slides. Caption written. Now number two. Now three.

[SCREEN] Shows the batch output: 5 carousels, 10 captions, 2 reel scripts

Done. Five carousels. Ten captions. Two reel scripts. Generated in about four minutes.

[CUT]

[CAMERA] Kalani, reviewing the output on screen

Now here's my 30 minutes. I go through each one. I check the facts because AI can get details wrong and I'm not posting misinformation. I adjust the captions where they feel too generic. I pick which carousels go to which account. I rewrite any reel script that doesn't sound like me.

[PAUSE]

The system gives me 80% of the way there. The last 20% is me. And that's the part that makes it not feel like robot content.

[CUT]

[SCREEN] Shows a content calendar or scheduling tool

Then I plug everything into the content calendar. I use a simple scheduling system. Each account gets 1 to 2 posts per day. The calendar fills up for the whole week from one pipeline run.

[CUT]

[CAMERA] Honest, practical

Now let me tell you what this system does NOT do.

It does not post for me automatically. I review and approve everything before it goes live. I'm not comfortable with fully autonomous posting yet. Maybe someday, but not now.

It does not create original visual designs. The carousels use templates. They look consistent, which is good. But they're not custom-designed each time.

And it does not replace genuine engagement. I still reply to comments, respond to DMs, engage with other accounts. That part is manual and it should be. Nobody wants to talk to a bot.

[CUT]

[CAMERA] Closing, satisfied

Four accounts. Thirty minutes a week of human time. Consistent posting. Consistent voice. And the system gets better over time because I keep refining the prompts and the templates based on what performs.

If you want to build something like this, the Social Media Pipeline Guide is in the description. It covers the architecture, the tools, the prompts, everything.

[PAUSE]

And yeah, the system even translated this video's description to Spanish automatically. [SMILE]

I'll see you in the next one.

---

**End screen CTA:** "Social Media Pipeline Guide linked below. If you run multiple accounts, this will save you hours."
**Description:**
I manage 4 Instagram accounts (@behikeai, @kalaniandrez, @s0ftrewind, @dulc3recuerdo). My content pipeline automates 80% of the work. I spend 30 minutes a week reviewing and approving.

The pipeline:
1. Fetch 30-50 news articles daily
2. Filter and rank (top 5-8)
3. Generate carousels + captions
4. Generate reel scripts
5. Auto-translate to LATAM Spanish

Output per run: 5 carousels, 10 captions, 2 reel scripts
Human time: ~30 minutes review + editing

Social Media Pipeline Guide: [LINK]

Tools used: n8n, Ollama, custom scripts, Voice Bible framework

#InstagramAutomation #ContentPipeline #SocialMediaAutomation #AIContent #n8n #ContentCreation #InstagramGrowth #AutomateInstagram #SocialMediaStrategy #ContentAtScale
**Tags:** instagram automation, automate instagram posting, content pipeline, social media automation, n8n instagram, AI content creation, manage multiple instagram accounts, instagram content system, automated carousels, content at scale

---
---

## VIDEO 10: What Nobody Tells You About Starting a Business at 21
**Length:** 8 minutes
**Thumbnail text:** 21 and $35K in Debt
**Hook (first 5 seconds):** "I'm 21. I have $35,000 in debt. And I'm starting a business anyway."

---

[CAMERA] Kalani, sitting somewhere comfortable. Not at desk. Maybe on a couch or chair. Softer lighting. This is personal.

I'm 21. I have $35,000 in debt. And I'm starting a business anyway.

[PAUSE]

This video is going to be different from the others. No screen recordings. No product demos. Just me being honest about what this actually feels like from the inside.

[CUT]

[CAMERA] Same setting, slightly closer

Here's what nobody tells you about starting a business at 21.

Number one. Nobody cares.

[PAUSE]

And I don't mean that in a self-pitying way. I mean it literally. When you're 21 and you tell people you're building a business, most of them smile politely and move on. Your friends think it's a phase. Your family wants you to get a "real job." And the internet is full of people who are further ahead than you, making your progress feel invisible.

The first month I was working on this, I'd come home from class, build for four hours, and show my work to nobody. Because nobody was watching. Nobody was asking for updates.

[PAUSE]

And that's actually the test. Can you keep building when nobody is paying attention? Because the truth is, most people can't. They need the likes, the comments, the validation. And when it doesn't come, they stop.

I almost stopped. Multiple times.

[CUT]

[CAMERA] Reflective

Number two. $0 revenue is louder than you think.

I have 25 products listed. I have a Shopify store. I have tools, ebooks, a music studio, an operating system. And my total revenue as of right now?

[PAUSE]

Zero dollars.

[PAUSE]

Not "a little." Not "getting there." Zero. Nobody has bought anything yet.

And there's this voice in your head that says, "see? You wasted all that time. You should've just applied to an internship. You should've just gotten a part-time job. You played entrepreneur and you have nothing to show for it."

That voice is loud. Especially at 3am when you can't sleep and you're staring at a Shopify dashboard with zero sales.

[CUT]

[CAMERA] Slightly more energy, but still grounded

But here's what I know that the voice doesn't.

The system is built. The products exist. The content pipeline is running. The AI infrastructure is working. The brand is established. The first sale hasn't happened yet, but the machine that will generate sales is already running.

Most people wait until the machine is perfect. I'm waiting for it to start catching.

And there's a difference between "this isn't working" and "this hasn't worked yet."

[PAUSE]

I believe it hasn't worked yet. Not that it isn't working.

[CUT]

[CAMERA] Personal, faith section

Number three. And this is the part I don't talk about enough.

My faith keeps me going.

[PAUSE]

I'm not going to preach at you. That's not what this is. But I want to be honest about what actually sustains me on the days when the bank account says zero and the effort says a thousand hours.

It's not motivation. Motivation is unreliable. It comes and goes.

It's not discipline either. I have ADHD. Pure discipline is a losing strategy for my brain.

It's trust. Trust that the work matters even when the results aren't visible yet. Trust that building something with integrity leads somewhere, even if I can't see where right now.

For me, that trust comes from my faith. For you it might come from somewhere else. But you need something deeper than "I want to make money" to survive the zero-revenue phase. Because the zero-revenue phase is long and it's quiet and it will test everything you think you believe about yourself.

[CUT]

[CAMERA] More animated, family section

Number four. My family is why I'm doing this.

Not in the "I'm doing this for my family" motivational poster way. In the real way.

My mom works hard. My family works hard. And I've watched what it looks like to exchange time for money your whole life with no leverage, no equity, no ownership of anything.

[PAUSE]

I don't want that. Not for me and not for them.

Building a business is the only path I see where the effort compounds. Where the work I do today is worth more next year. Where I'm not starting from zero every Monday.

That's not ambition. That's math. And it's personal.

[CUT]

[CAMERA] Calm, present

Number five. The real reason I chose this over a job.

I'm graduating soon with a CS degree. I could get a software engineering job. $70K, $80K, maybe more if I get lucky. Stable. Benefits. Regular paycheck.

And I might still do that. I'm not too proud to get a job if I need to. But right now, in this window, while I'm young, while I don't have kids, while my expenses are low, I have a chance to try something that most people put off until they're 35 and then say "I wish I started when I was young."

I'm young right now. This is the window. And I'd rather try and fail at 21 than wonder "what if" at 40.

[CUT]

[CAMERA] Final section. Calm. Direct. No performance.

So here's where I'm at. Twenty-one years old. Puerto Rico. $35,000 in debt. Zero revenue. Twenty-five products. Three AI machines. Four Instagram accounts. A brand called Behike. A psychologist helping me manage my ADHD. A family that doesn't fully understand what I'm doing but supports me anyway. And a God I trust when the numbers don't add up.

[PAUSE]

Most people wait until they're ready. I started while I was scared.

[PAUSE]

And honestly? I'm still scared. Every day. But I'm building anyway. And I think that's the part nobody tells you. The fear doesn't go away. You just learn to build next to it.

[LONG PAUSE]

[CAMERA] Looks at camera, simple

No link in the description this time. No product to sell.

Just follow along. I'll show you everything. The wins, the failures, the zero-revenue months, and hopefully, eventually, the first sale.

[PAUSE]

I'll see you in the next one.

---

**End screen CTA:** "No CTA. Just: follow along. I'll show you everything."
**Description:**
I'm 21. I'm $35,000 in debt. I have zero revenue. And I'm building a business anyway.

This is the honest version. No products to sell you. No hype. Just what it actually feels like to start from nothing at 21.

What I talk about:
- Why nobody cares (and why that's the real test)
- What $0 revenue actually feels like
- Why faith and family keep me going
- Why I chose this over a stable job
- Why I started while I was still scared

If you're in a similar position, you're not alone.

Follow the journey: @kalaniandrez (Instagram)
The brand: @behikeai

#StartingABusiness #Entrepreneur #21YearsOld #BuildInPublic #ZeroRevenue #HonestContent #Faith #ADHD #PuertoRico #TheJourney
**Tags:** starting a business at 21, zero revenue entrepreneur, honest business journey, build in public, young entrepreneur, student entrepreneur, business and debt, ADHD entrepreneur, faith and business, Puerto Rico business

---
---

# PRODUCTION NOTES

## Filming order recommendation:
1. VIDEO 6 (Budgeting App) - shortest, mostly screen recording, good warm-up
2. VIDEO 5 (Music Studio) - fun, high energy, easy to film
3. VIDEO 8 (Browser OS) - mostly screen recording, impressive demo
4. VIDEO 1 (AI Setup) - core content, needs the three machines visible
5. VIDEO 7 ($0 AI Stack) - screen recording heavy, practical
6. VIDEO 9 (Instagram Automation) - needs pipeline running live
7. VIDEO 2 (25 Products) - needs product catalog ready to show
8. VIDEO 4 (Puerto Rico) - talking head, minimal screen recording
9. VIDEO 3 (ADHD) - personal, needs good energy
10. VIDEO 10 (Starting at 21) - save for last, most emotional, film when you're in the right headspace

## Equipment minimum:
- Phone camera (any modern iPhone is fine)
- Ring light or window light
- Quiet room
- Screen recording software (OBS is free)
- Basic editing (CapCut is free)

## Editing style:
- Jump cuts between sentences to keep pace
- Text overlays at every number or stat
- No fancy transitions, just hard cuts
- Background music from Behike Music Studio (use your own tool)
- Thumbnail: use Canva free tier

## Copyright notice
Copyright 2026 Behike. All scripts, concepts, and brand elements are the intellectual property of Kalani Andre Gomez Padin.
