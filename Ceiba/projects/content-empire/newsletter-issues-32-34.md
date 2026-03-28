---
title: "Newsletter Issues 32-34"
type: content
tags: [newsletter, email, voice, spanish-market, automation, n8n]
created: 2026-03-22
---

# Behike Newsletter — Issues 32, 33, 34
# Brand: Behike | Voice: Dan Koe x Robert Greene, journalism structure
# Rules: No em dashes. No exclamation marks. Short sentences. One thing per issue.

---

## ISSUE 32 — "How I Write Content That Sounds Like Me"

**Subject line:** The document that stops my content from sounding like a chatbot

**Preheader:** Banned words, tone rules, and why most AI content fails the same way.

---

Hey,

Last month I reviewed a batch of AI-generated content from five different creators.

Every single one read like it was written by the same person. Enthusiastic. Generic. Vague. No point of view.

The problem wasn't the AI. It was that nobody told the AI who they actually are.

---

### The Voice Bible

A Voice Bible is a reference document that defines exactly how you sound.

Not aesthetics. Not vibes. Specific, ruleset-level instructions.

Mine runs about 1,200 words. It covers seven personality adjectives, a vocabulary list, sentence structure rules, a list of banned words, and platform-specific calibration for email, Instagram, X, and YouTube.

When I prompt any AI to write as me, I paste the relevant sections. The output lands 80% of the way there on the first draft. The edit pass takes five minutes instead of thirty.

That ratio changed how much I can ship.

---

### Banned Words

The banned words list is where the real work happens.

Every word on the list earned its place because it signals something false. "Game-changing" signals hype. "Unlock" signals guru content. "Excited to share" signals the AI is talking, not me.

A few from mine:

- "Revolutionary" or "transformative" — adjectives for things that aren't.
- "Deep dive" — meaningless filler.
- "Hustle" as a virtue — I don't want that association.
- "Passive income" — overused to the point of meaning nothing.
- Exclamation marks — they perform enthusiasm instead of earning it.

The list isn't about being restrictive. It's about knowing which words carry weight and which ones borrow credibility they haven't built.

Most AI tools default to the borrowed-credibility version. The Voice Bible corrects for that.

---

### Tone Rules and Sentence Structure

My default sentence pattern is short. Direct. One idea per sentence.

The rhythm: short, short, then a slightly longer sentence that carries the weight. Short again.

Paragraphs max out at three sentences. On a phone screen, anything longer starts to feel like a lecture.

Openings never start with "I." Lead with the observation, the number, or the claim. "Three scripts replaced my marketing team" lands differently than "I built three scripts that replaced my marketing team." Same information. Different energy.

Closings don't summarize. They end forward. One honest line, or a CTA that's specific and not desperate.

---

### Why It Actually Works

The moat in content isn't information. Information is everywhere and getting cheaper.

The moat is specificity of perspective.

A Voice Bible is the technical document behind that specificity. It forces you to articulate what you actually think, how you actually talk, what you actually refuse to say. That's harder than it sounds. Most people haven't done it.

Once it's done, every AI tool in your stack gets significantly more useful. Not because the AI got smarter. Because you got clearer about who's supposed to be writing.

---

I packaged the full framework, including a blank Voice Bible template and my complete vocabulary rules, into the Behike content system.

Everything is at behike.shop.

See you next week,
Kalani
Behike

---
---

## ISSUE 33 — "The Community I'm Building in Spanish"

**Subject line:** 650 million people and almost no AI creators. Here is my plan.

**Preheader:** Why La Ceiba Guild exists and why the timing is right.

---

Hey,

There are roughly 650 million Spanish speakers in the world.

Most AI content is in English. Most AI tools have English-first documentation. Most AI creators targeting the "AI audience" are speaking to the same coastal, tech-adjacent, English-fluent demographic.

The Spanish market is not an afterthought. It's an opening.

---

### What I'm Building

La Ceiba Guild is a Spanish-language community focused on practical AI use for builders. Not for developers. Not for executives. For people who want to work differently and have the ambition to figure it out.

The name comes from the ceiba tree. Taino cosmology. The axis that connects all three worlds. That's the image I wanted: a root system, not a funnel.

The format is a Telegram hub. Weekly check-ins, shared resources, accountability structure, and direct access to the tools and frameworks I'm building under the Behike brand.

No paid subscription at launch. The goal is to build something real before I monetize it.

---

### Why Nobody Else Is Doing This

There are Spanish-language AI channels on YouTube. There are Facebook groups with tens of thousands of members that produce zero actual output.

What's missing is a community organized around execution.

Most Spanish-language AI content is reactive. Translations of trending English content. Reviews of tools. "Top 10" lists that were already stale in English two months ago.

The gap isn't information. It's framework. It's a community where people are actually building things, sharing results, and holding each other accountable.

That's the gap La Ceiba Guild is designed to fill.

---

### The Market Logic

Here's the honest business case.

The AI creator space in English is saturated. Getting to 10,000 followers on X as an English-language AI creator in 2026 requires either a large budget for ads, a large existing audience, or something genuinely differentiated.

The Spanish-language market is three to four years behind in terms of creator saturation. The same content that would be average in English is above average in Spanish right now. That window closes.

I'm in Puerto Rico. Spanish is my first language. I'm not trying to translate an American playbook. I'm building something that fits how people in Latin America and Spain actually think about work, technology, and ambition.

That's the real advantage. Not just language. Context.

---

### What Comes Next

La Ceiba Guild launches as a Telegram community. The first cohort is small and intentional. Builders who want accountability and a practical AI curriculum in Spanish.

From there: a newsletter in Spanish, a YouTube channel, and eventually a Spanish-language version of the Behike product catalog.

One step at a time. The root system before the branches.

---

If you're Spanish-speaking or know someone who is, the community is forming now.

Details at behike.shop.

See you next week,
Kalani
Behike

---
---

## ISSUE 34 — "The System That Writes My Tweets While I Sleep"

**Subject line:** The n8n workflow that handles my content queue automatically

**Preheader:** How Ghost Writer CLI and a few automations replaced three hours of daily content work.

---

Hey,

The honest version of "I post consistently" is this: I built a system that makes inconsistency structurally harder than consistency.

It took about two weeks to get right. Now it runs on its own.

---

### The Problem with Manual Content

Before the automation, content creation looked like this.

Idea comes in. Write it down somewhere. Open a new document. Stare at it. Write a draft. Edit it. Decide it's not ready. Leave it. Come back two days later. Post something different instead.

That's not a discipline problem. It's a systems problem.

The idea pipeline was inconsistent. The drafting environment was inconsistent. The review step was disconnected from the pipeline. Nothing had a trigger. Everything depended on willpower.

Willpower is a bad infrastructure choice.

---

### Ghost Writer CLI

Ghost Writer is a command-line tool I built that takes a topic, a content type, and a platform, then returns a formatted draft calibrated to my Voice Bible.

The input is one line. The output is a ready-to-edit draft in the right format for X, Instagram, or email.

The Voice Bible runs as a system prompt seed. The banned words list runs as a filter. The sentence structure rules are embedded in the format instructions.

Result: first drafts that take five minutes to polish instead of thirty.

One command. One draft. Next.

---

### The n8n Workflow

Ghost Writer is the writing layer. n8n is the pipeline that connects everything.

The workflow runs on a schedule. Every morning at 7 AM, it checks a content queue I maintain in Notion. If there are approved drafts in the queue, it formats them for their destination platform and moves them to the staging folder.

Approved posts for X get formatted and pushed to a Buffer queue. Instagram posts get formatted with caption, hashtag set, and posting time. Newsletter drafts get formatted and pushed to a draft folder in ConvertKit.

Nothing posts automatically without my review. The automation handles formatting and scheduling, not judgment. That distinction matters.

The human step is approval. Everything else is handled.

---

### What This Actually Changes

The mental load of content creation is mostly not writing. It's everything around writing.

Deciding what to write. Formatting it correctly for the platform. Remembering to schedule it. Tracking what went out and when.

The system eliminates those steps. The only creative work left is the idea and the edit.

That's where attention should go. Ideas and edits. Not formatting. Not scheduling. Not remembering.

The n8n workflow + Ghost Writer CLI cut my daily content time from roughly three hours to forty-five minutes. That difference compounded. More consistency, less friction, more ideas getting shipped instead of dying in drafts.

---

The full automation setup, including the n8n workflow JSON and Ghost Writer configuration, is part of the Behike AI Employee system.

Everything is at behike.shop.

See you next week,
Kalani
Behike
