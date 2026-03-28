# Batch 36: Solo Business Operations
# 5 YouTube Scripts
# Brand: Behike (@behikeai)
# Tone: Direct, thesis first, Dan Koe meets Robert Greene. No hype. No em dashes. No exclamation marks.
# Created: 2026-03-22

---

## Script 1: "The systems audit: how I review my entire business every 30 days"

**[HOOK]**
Most solo operators don't know if their business is actually working. They're busy, not building. The difference comes down to one habit: the monthly systems audit.

**[CONTEXT]**
I run this at the end of every month. Takes about two hours. It's not journaling. It's not a feelings check. It's a structured review of what's actually moving and what's dead weight.

Here's the exact process.

**[SECTION 1: Revenue audit]**
Start with money. Not feelings. Not vibes. Numbers.

For each income stream, I write down:
- What it made this month
- What it made last month
- The trend direction (up, flat, down)
- One action I could take to improve it

If a stream made nothing in 30 days, it gets flagged. If it's flagged two months in a row, I cut it or renegotiate the strategy. No mercy. Attention is the resource, not time.

**[SECTION 2: Content audit]**
Every piece of content I published gets reviewed. I'm looking for:
- Which format got the most reach
- Which topic got the most saves or comments
- Which post I thought would do well but didn't

The goal here is to kill assumptions. You think you know what your audience wants. You don't, until you check.

**[SECTION 3: Systems audit]**
Every recurring task I do gets a question: should this still be manual, or is there a better setup?

I have a list. Things like:
- Email responses
- Content scheduling
- Product delivery
- Research workflows

Each one gets a status: running clean, needs fixing, or should be cut. Running a business with broken systems is like driving with a flat tire. You're moving but you're burning rubber.

**[SECTION 4: Energy audit]**
Last thing. This one took me the longest to add because it sounds soft. It's not.

I look at the last 30 days and ask: what was I dreading? What did I keep pushing back? What felt like pulling teeth?

Those items are either broken systems, wrong priorities, or things I should never have started. All three need a decision.

**[CLOSE]**
Two hours a month. That's the cost. The return is a business that evolves instead of stagnates.

If you want the exact audit template I use, it's in the Solopreneur OS. Link in description.

---

## Script 2: "How to use Habitica as an accountability system (not just a to-do app)"

**[HOOK]**
Habitica looks like a game. Most people use it like a checklist. That's why it stops working after a week. The setup matters more than the app itself.

**[CONTEXT]**
I've used Habitica for over a year. Not because it's fun, but because it's the only system that connects my daily behavior to visible consequences. If you use it wrong, it's just another app you'll abandon. Here's how I actually use it.

**[SECTION 1: The three task types and how to assign them]**
Habitica has three task categories: Habits, Dailies, and To-Dos.

Most people load everything into Dailies. That's the mistake. Dailies are for non-negotiables. Things that have to happen every single day without exception. Exercise, writing, reading. Three to five max. Any more and you're setting up to fail.

Habits are for the things you're actively trying to build or break. Not mandatory every day, but tracked. "Did I eat well today" or "Did I open social media first thing." These compound invisibly.

To-Dos are for project tasks. One-time actions that belong to a specific deliverable. Not habits. Not daily. Just things that need to get done.

Keep them separated. The whole system breaks if you mix them up.

**[SECTION 2: The party mechanic]**
Solo mode is motivating for about two weeks. Then the novelty fades.

The party mechanic is where Habitica gets real. You join a group. When you skip your Dailies, everyone in the party takes damage. Not metaphorical damage. Game damage. Health points drop.

I'm in a small party of three. We check in every Sunday. I've skipped Dailies twice in six months because the social cost is real. That's not because I fear the game. It's because the accountability is now social, not personal. Personal accountability is easy to negotiate with. Social isn't.

**[SECTION 3: Guilds and challenges]**
Guilds are public groups around themes. There are guilds for builders, writers, students, entrepreneurs. Challenges inside guilds give you external structure, free gear, and a reason to show up consistently.

Find one challenge per month. Not more. One. Too many challenges dilutes focus.

**[SECTION 4: What not to do]**
Don't add streaks for every habit you've ever wanted to build at once. You'll crash hard and quit.

Don't treat the game elements as the goal. The goal is behavior change. The game is the delivery mechanism.

Don't let the streak become the identity. If you miss a day, reset and move. Missing one day is not failure. Quitting is.

**[CLOSE]**
Habitica is not special software. It's a habit loop with social accountability baked in. That's the entire edge. Set it up right and it compounds. Set it up wrong and it's just another notification you'll eventually silence.

---

## Script 3: "BehiqueBot: how I built my own Telegram accountability bot"

**[HOOK]**
I built a bot that knows my goals, tracks my ideas, and holds me accountable every morning. It cost less than $10 a month to run and I built it in Python with no prior backend experience. This is exactly how I did it.

**[CONTEXT]**
BehiqueBot is a personal Telegram bot. It runs on Railway, uses OpenAI for transcription and classification, and stores everything it hears from me into organized categories. The concept came from a framework my psychologist gave me. The implementation took one week.

**[SECTION 1: Why Telegram]**
Telegram has a bot API that's dead simple. You create a bot through BotFather, get an API token, and within 20 lines of Python you're receiving messages.

The other option was WhatsApp or a dedicated app. WhatsApp's API is expensive and designed for businesses. A dedicated app means app store, distribution, maintenance. Telegram is already on my phone. I'm already in it. Zero friction.

**[SECTION 2: The core loop]**
Every message I send to the bot gets:
1. Transcribed if it's a voice note (Whisper API, $0.006 per minute)
2. Classified into one of five categories: Creative, Business, Knowledge, Personal, Technical
3. Tagged with a life pillar: health, wealth, relationships, or general
4. Saved to a daily archive
5. Responded to with a brief confirmation and next action prompt

The classification runs through GPT-4o-mini. Cheap, fast, accurate enough. I don't need perfect AI. I need consistent behavior tracking.

**[SECTION 3: The voice note feature]**
This is the part that changed how I use it. I used to lose ideas constantly. I'd think of something in the shower, at the gym, driving. By the time I reached my phone I'd forgotten.

Now I open Telegram, record a 20-second voice note, and it's logged, transcribed, and categorized in under five seconds. The friction is gone. The idea is captured. I can come back to it when I'm at a desk.

Whisper is accurate enough that I don't need to correct transcriptions more than once a week.

**[SECTION 4: The accountability piece]**
Every morning at 8am the bot sends me a check-in. Three questions:
1. What did I complete yesterday?
2. What is the one priority for today?
3. What is the blocker I need to address?

It's not AI-generated. It's a scheduled message. Simple. But showing up in my most-used app makes it impossible to ignore the same way a productivity app can be ignored.

**[SECTION 5: What's next]**
I'm adding Notion as the real database. Right now everything is flat JSON. The next version connects ideas to projects, tracks completion rates, and surfaces patterns. The check-in will also become conversational, using Claude to ask follow-up questions based on what I said the day before.

**[CLOSE]**
You don't need to build this exactly. But the principle is the thing. Your accountability system should live where you already are. Not in an app you have to remember to open. Building it yourself means you can shape it to how your brain actually works.

All the code is open. Link in description.

---

## Script 4: "The content calendar that actually gets executed (not just planned)"

**[HOOK]**
A content calendar that lives in Notion and never gets touched is not a content calendar. It's a guilt document. Here's the system that actually ships content.

**[CONTEXT]**
I've built content calendars four times. Three of them failed. The fourth one works because it's built around execution constraints, not planning ideals. The difference is in the structure.

**[SECTION 1: The problem with traditional content calendars]**
Most content calendars are built in planning mode. You sit down on a Sunday, you fill in 30 days of slots, you feel productive. Then Monday comes and real life hits and the calendar becomes fiction.

The issue is that planning and execution are different cognitive states. Planning is easy. Execution requires energy, focus, and specificity. A calendar full of "Instagram post - business tips" is not executable. What does that mean at 9pm when you're tired?

**[SECTION 2: Batch creation over daily creation]**
I create content in batches. One session per week, 90 minutes. During that session I produce:
- 5 Instagram posts (caption + visual direction)
- 2 short-form video scripts
- 1 newsletter draft

That's the entire week in one session. The rest of the week I'm distributing, not creating.

Batching works because it collapses context-switching. You're in creative mode once. You ship from that one session all week. You don't have to re-enter the creative mental state daily, which is the real cost that kills most content plans.

**[SECTION 3: The template system]**
Every content type I produce has a template. Not a rigid fill-in-the-blank. A structure.

Instagram post: Thesis sentence. Supporting evidence or personal example. Single call to action.

Newsletter issue: Subject line with thesis. Problem framing. One insight. One next action for the reader.

Short-form script: Hook (one sentence). Context (ten seconds). Three-point body. Close that connects back to the hook.

Templates don't kill creativity. They reduce the starting cost. The blank page is where most content dies.

**[SECTION 4: The distribution layer]**
After the batch session, I load everything into a scheduling tool. Right now it's Buffer for Instagram and a simple CSV for newsletters. The content doesn't sit in drafts where I can second-guess it. It goes straight to scheduled.

Second-guessing is how good content dies. Ship it, see the data, improve the next batch.

**[SECTION 5: The review loop]**
Every Sunday I spend 15 minutes reviewing last week's metrics. I'm looking for:
- What got the most reach
- What got the most saves
- What I skipped posting and why

The "why I skipped" question is the most important one. If I skipped something because it wasn't ready, I need to trace that back to the batch session. Something in the process broke. Fix the process, not the motivation.

**[CLOSE]**
A content calendar that works is not about the tool. It's about reducing the cost of execution until it's lower than the cost of not doing it.

The templates and batch framework I use are in the Social Media Pipeline Guide. Link in description.

---

## Script 5: "Why I don't use project management software (and what I use instead)"

**[HOOK]**
I tried Notion, Asana, Linear, ClickUp, Trello, and Basecamp. None of them stuck. I'm not saying they're bad tools. I'm saying they're the wrong tool for how I work. Here's what I actually use.

**[CONTEXT]**
Project management software is designed for teams. It assumes multiple people need visibility into task status. When you're a solo operator, that entire layer of complexity becomes overhead with no payoff.

**[SECTION 1: The core problem with PM software for solos]**
Every PM tool has the same implicit assumption: there are people who need to be updated on what you're doing. Tickets, assignments, statuses, comments. All of that is team coordination infrastructure.

When it's just you, that infrastructure becomes busywork. You're maintaining a system for an audience of one. And that one person is also the one who has to maintain it, which means the system competes with the actual work.

**[SECTION 2: What I use instead]**
I use three things.

First: a flat markdown file called primer.md. It has one current project, what got done last session, the next action, and open blockers. Nothing else. It takes 30 seconds to read and 2 minutes to update. That's the entire project state.

Second: BehiqueBot for capturing everything that isn't a project task. Ideas, half-thoughts, decisions I need to revisit. They go into the bot so they don't live in my head competing for attention.

Third: a weekly review in a separate markdown file. Every Sunday, what shipped, what didn't, what the priority is for next week.

Three files. Zero subscriptions. The whole thing works because I'm not managing coordination. I'm managing my own attention.

**[SECTION 3: When PM software makes sense]**
I'm not against project management software in general. If you have a team, or if you have client-facing work where visibility matters, a PM tool is the right call.

The mistake is reaching for team infrastructure when you don't have a team yet. It's organizing for a future you haven't built. That energy is better spent on the work itself.

**[SECTION 4: The argument for constraints]**
A one-person operation with three files has a forcing function built in. There's no room for fake productivity. You can't spend an hour reorganizing your Notion database because there is no Notion database. The only way to feel productive is to ship something.

Constraints aren't a limitation. They're a filter. The things that matter bubble to the top because there's nowhere to bury them.

**[CLOSE]**
The best system is the one that reduces friction to the actual work. For me, that's three markdown files and a Telegram bot. Your version will be different. But question whether the complexity of your current setup is serving the work or replacing it.

---

*Batch 36 complete. 5 scripts. Topics: systems audit, Habitica accountability, BehiqueBot build, content calendar execution, solo ops without PM software.*
