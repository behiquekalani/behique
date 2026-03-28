---
title: "Newsletter Issues 53-55"
type: content
tags: [newsletter, adhd, finance, voice, content, automation]
created: 2026-03-22
issues: [53, 54, 55]
---

# Newsletter Issues 53-55
# Topics: Zero-App Expense Log, Unedited AI Content, The 5-Hour Content Week

---

## Issue 53 | The Zero-App Expense Log

**Subject:** The expense log that lives in Telegram
**Preview text:** No app. No friction. One message.

---

Last Tuesday I spent $14 on coffee I didn't budget for.

I know this because I texted my bot about it at the same moment I paid. Not later. Not in a Sunday recap. Right there, at the counter, while the barista handed me the cup.

That's the zero-app expense log. And it took me two years of failed budget apps to get there.

The thing most finance apps get wrong is the interface assumption. They assume you'll navigate to them, remember why you're there, enter the data correctly, and close them. That's four cognitive steps. For an ADHD brain in a busy moment, that's four chances for the habit to fail.

Telegram is already open. I use it all day. Sending a message is the same action I take a hundred times before noon. No new app. No new habit. Just one message that happens to go to my bot instead of a friend.

The bot handles everything else.

It reads the message. It pulls out the amount and category. It logs it. It sends a confirmation. If the category is ambiguous, it asks one clarifying question. The whole exchange takes 12 seconds.

The data ends up in a spreadsheet that I review on Sundays. The Sunday review is a separate habit from the daily logging. Those two things used to be combined, which was the problem. Reviewing while logging adds friction to both.

The insight I keep coming back to: the problem was never motivation or discipline. The problem was friction at the wrong moment. When you're paying for coffee, you have three seconds of attention to give. A financial logging system that needs more than three seconds will fail at 8am on a Tuesday.

One message. Three seconds. That's the whole system.

**To try this yourself:**

You don't need a custom bot. Start with the simplest version.

Make a Telegram group with just yourself. Every time you spend money, send a message in the format: "$14 coffee impulse." Amount, category, optional note.

Do that for two weeks. Review on Sunday. You'll have 14 days of real spending data with near-zero friction.

If it works and you want to add logging, classification, and weekly summaries, that's when the bot becomes useful.

But start with the message. The habit has to come before the automation.

---

## Issue 54 | Why I Don't Post AI-Generated Content Unedited

**Subject:** Why I edit everything the AI writes
**Preview text:** The draft is not the content.

---

There's a version of this newsletter I could ship in 8 minutes.

Paste the topic into Claude. Copy the output. Publish. Done.

I don't do that. And it's not because the output is bad. It's because the output isn't mine, and the difference matters more than the time saved.

Here's the honest version of how I use AI for writing.

Every piece of content I ship starts with a draft from Claude. I prompt it with my Voice Bible, three samples of my own writing, and the specific topic. The output is usually pretty good. Clear structure, reasonable word choices, stays on topic.

Then I edit it.

Not because I'm fixing mistakes. Because the draft is missing something the tool can't produce: the specific detail that comes from my actual experience.

When Claude writes about budgeting, it writes something accurate. When I write about budgeting, I write about texting my bot while holding a coffee cup at 8am and watching the confirmation come back before I finished paying. That detail is not in the model. It's in my Tuesday.

The AI draft gets me to 60% in 8 minutes. My edit pass gets it to 100% in 20. That's the math.

What I'm doing in the edit pass: replacing general statements with specific ones. Cutting any sentence that sounds like it could have been written by anyone. Adding one detail from my actual experience that grounds the piece. Cutting the closing paragraph that wraps everything up too neatly.

The last point matters. AI writing tends to close with a tidy summary or a call to action formatted exactly like every other call to action you've seen. Real writing ends somewhere specific. Not summarized.

The risk of skipping the edit pass is not legal or technical. It's that the content stops being yours. The audience can tell. Maybe not on individual pieces, but over time the voice goes flat. The specific details disappear. The writing starts to sound like the average of all writing, which is the exact opposite of a brand.

What I tell myself when I'm tempted to skip the edit: the draft is raw material, not content.

The AI handles the blank page. You handle the voice.

**One practical thing:**

Before you post anything AI-drafted, read it out loud.

If you wouldn't say those exact words to a person you know, rewrite the sentences that don't land. That's the quickest edit pass and it catches 80% of the AI tells.

Your voice is in your speech patterns. The edit pass is how you put it back.

---

## Issue 55 | The 5-Hour Week I Stole Back From Content Logistics

**Subject:** 5 hours a week, returned
**Preview text:** The automation that changed how I work.

---

Six months ago, content logistics was eating my Mondays.

Not the thinking. Not the writing. The moving of things from one place to another. Reformatting. Resizing. Pasting into three different tools. Writing the same idea in four different tones.

That part. The part that isn't creative work but somehow takes longer than the creative work.

I built an n8n workflow to handle it. And I want to be specific about what changed, because "I automated my content" is one of those phrases that sounds impressive and tells you nothing.

Here's exactly what the workflow does.

I finish a long-form piece. Could be this newsletter. Could be a blog post. I paste it into a form field and hit submit. That's my one action.

The workflow receives the text. It runs it through a structured prompt that I built over six iterations. The prompt knows my voice. It knows I don't use exclamation marks. It knows I lead with the observation, not the declaration. It knows my sentence length preference.

Four outputs come back within 90 seconds: two Twitter threads, three Instagram captions, one short-form video script.

They land in a Google Doc. My Telegram receives a notification with a direct link.

I open the doc, spend 20 minutes on edits, and the week's social content is done.

That's the 5 hours. Not in one block. In 45-minute sessions I no longer have to schedule because the logistics are gone.

The part that took the most time to build was not the workflow. It was the prompt. Getting the AI output to match my actual writing required six rounds of testing, failing, and adjusting. The workflow itself took about 3 hours to set up. The prompt took three weeks of refinement.

That's the honest version of "I automated my content pipeline."

There's real work on the front end. The payoff is on the back end, compounding over every week after.

What I'd tell you if you're thinking about building something similar: start with the prompt, not the workflow. If you can't get the AI to match your voice in a plain chat window, the workflow won't fix that. The workflow just runs the prompt faster.

Get the prompt right first. Then automate it.

**The three-question test before you automate anything:**

One: can you produce the output manually in under an hour? If not, the task isn't defined well enough to automate.

Two: do you do this task more than once a week? If not, the automation setup cost won't pay off.

Three: does the output require a judgment call you'd want to make yourself? If yes, automate the setup and the delivery, not the decision.

Content logistics passes all three. The actual writing never will.

---
