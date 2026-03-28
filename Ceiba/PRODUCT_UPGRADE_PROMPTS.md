# PRODUCT UPGRADE PROMPTS
# Apply each prompt to every product before it goes on sale.
# Nothing ships until ALL prompts have been applied.
# Order matters: run them 1-10 sequentially.

---

## PROMPT 1: THE COMPETITOR CRUSH
```
Search the web for the top 5 competing products to [PRODUCT NAME] on Gumroad, Amazon, Udemy, and Skillshare. For each competitor:
- What do they charge?
- How many pages/lessons/features?
- What do their reviews praise?
- What do their reviews complain about?
- What's missing from their product?

Now rewrite [PRODUCT] to include everything competitors are missing. Add the features reviewers wished existed. Beat the best competitor on depth, not price.
```

## PROMPT 2: THE FIRST CHAPTER TEST
```
Read only the first 500 words of [PRODUCT]. Pretend you just paid $[PRICE] for this.

Answer honestly:
- Would you keep reading or request a refund?
- Does the first sentence hook you?
- Do you know what you're getting within 30 seconds?
- Is there a specific, concrete promise in the first paragraph?
- Does it sound like a human or an AI template?

Rewrite the first 500 words until a stranger would say "okay, this is worth my time."
```

## PROMPT 3: THE SPECIFICITY PASS
```
Read every paragraph of [PRODUCT]. For each paragraph, ask:
- Is there a specific number, date, tool name, or real example?
- Could this paragraph appear in any other book about the same topic?
- If I deleted this paragraph, would anyone notice?

Replace every vague statement with a specific one:
- "a lot of money" -> "$2,847 in 3 months"
- "many tools" -> "7 tools: Ollama, n8n, Kokoro, FFmpeg, Playwright, SDXL, Whisper"
- "it takes time" -> "it took me 14 days of 4-hour sessions"
- "some people succeed" -> "3 out of 10 stores hit $1K/month in 90 days"

If you don't have the real number, make a reasonable estimate and mark it [EST].
```

## PROMPT 4: THE VOICE BIBLE SCRUB
```
Read [PRODUCT] line by line against the Voice Bible at Ceiba/VOICE_BIBLE.md.

Check every sentence for:
- Banned words/phrases (full list in Voice Bible)
- Em dashes (replace with periods or commas)
- Generic AI patterns ("In today's world...", "Let's dive in...")
- Corporate tone (should sound like texting a smart friend)
- Paragraphs longer than 3 sentences (split them)
- Sections without a single specific example (add one)

Run tools/voice_checker.py on the file. Fix every violation.
Then read it out loud. If any sentence sounds like a robot wrote it, rewrite it.
```

## PROMPT 5: THE "SO WHAT?" TEST
```
For every section/chapter in [PRODUCT], ask "So what? Why does the reader care?"

If the answer is "because it's good practice" -> rewrite to show the COST of not doing it
If the answer is "because experts say so" -> replace with a real story of what happened when someone did/didn't do it
If the answer is "because it's important" -> delete the section or prove WHY with numbers

Every section must answer: "What happens to the reader's life/money/time if they apply this?"
```

## PROMPT 6: THE EXERCISE UPGRADE
```
Review every exercise/worksheet in [PRODUCT].

For each exercise:
- Can someone complete it in under 5 minutes? (If no, break it smaller)
- Is the output something they can USE immediately? (Not just "reflect on X")
- Is there a real example of a completed exercise? (Add one)
- Does it connect to a specific outcome? ("After this exercise, you'll have X")

Replace any exercise that says "think about..." with "write down..."
Replace any exercise that says "consider..." with "list 3 specific..."
Replace any exercise that says "reflect on..." with "open [tool] and do..."
```

## PROMPT 7: THE ANTI-REFUND TEST
```
Write 3 realistic 1-star reviews that a disappointed buyer might leave for [PRODUCT].

For each fake bad review:
- What specific complaint would they have?
- Is the complaint valid?
- How can you fix the product so this review becomes impossible?

Then fix the product. Add the missing content. Remove the weak sections. Address every legitimate criticism before a real buyer has to make it.
```

## PROMPT 8: THE DESIGN POLISH
```
For [PRODUCT]'s landing page:

1. Screenshot test: If someone sees ONLY a screenshot of the landing page (no scrolling), do they:
   - Know what the product is?
   - Know the price?
   - Know who it's for?
   - Feel trust (or suspicion)?

2. Mobile test: Open on a phone-width viewport. Is everything:
   - Readable without zooming?
   - Tappable without precision?
   - Loading in under 3 seconds?

3. Differentiation test: Put this landing page next to 3 competitor pages. Can you tell them apart in 2 seconds? If not, redesign.

4. CTA test: Is there exactly ONE clear action on every screen? If there are competing CTAs, remove all but one.
```

## PROMPT 9: THE WATERMARK + PROTECTION PASS
```
For [PRODUCT]:

1. Add copyright footer to every page of the PDF: "Copyright 2026 Behike. Unauthorized distribution prohibited. Purchase ID: [BUYER]"
2. Add anti-AI-training meta tag to every HTML file
3. Add invisible watermark text in the PDF (white text on white, contains copyright notice)
4. Check: could someone copy-paste the entire book into a blog post? If yes, add formatting that makes copy-paste ugly (tables, images, special characters that break plain text)
5. Add "This copy was purchased by [buyer email]" to the last page (Gumroad can inject buyer info)
6. Verify the copyright notice matches the format needed for copyright.gov registration
```

## PROMPT 10: THE FINAL GATE
```
Before [PRODUCT] goes on sale, verify ALL of the following:

CONTENT:
[ ] First 500 words would hook a stranger (Prompt 2 passed)
[ ] Every paragraph has at least one specific detail (Prompt 3 passed)
[ ] Zero Voice Bible violations (Prompt 4 passed)
[ ] Every section answers "so what?" (Prompt 5 passed)
[ ] Every exercise is completable in 5 minutes (Prompt 6 passed)
[ ] All 3 fake 1-star reviews addressed (Prompt 7 passed)

SECURITY:
[ ] No personal names (full legal name, family, girlfriend)
[ ] No personal details (address, school, medical info)
[ ] No internal IPs or machine names
[ ] No file paths or system architecture details
[ ] PDF metadata is clean (no author name, no file paths)

LEGAL:
[ ] Copyright notice on every page
[ ] AI disclosure present and honest
[ ] No trademarked terms used without context
[ ] No income guarantees or promises
[ ] Price is consistent across all materials

DESIGN:
[ ] Landing page loads in under 3 seconds
[ ] Mobile responsive
[ ] ONE clear CTA per screen
[ ] Visually different from other Behike products

BUSINESS:
[ ] Price is research-backed (Prompt 1 competitor analysis)
[ ] Gumroad listing copy matches product content
[ ] Product delivers MORE than the listing promises
[ ] Watermarks applied (Prompt 9)

Only when ALL boxes are checked does the product get listed.
```

---

## HOW TO USE THIS

For each product:
```bash
# Run prompts 1-10 sequentially
# Each prompt should be given to an agent with the product file
# Agent applies the prompt, saves the improved version
# Final gate (Prompt 10) is the go/no-go check

# Example:
# Agent 1: Apply Prompt 1 (competitor analysis) to behike-method-v2.md
# Agent 2: Apply Prompt 2 (first chapter test) to the output of Agent 1
# Agent 3: Apply Prompt 3 (specificity pass) to the output of Agent 2
# ...continue through all 10
```

## PRODUCTS THAT NEED THIS TREATMENT:
1. The Behike Method ($24.99) - FIRST PRIORITY
2. AI Employee Guide ($29.99)
3. Claude Code Course ($39.99)
4. Ecommerce Playbook ($14.99)
5. Solopreneur OS ($19.99)
6. Content Franchise Kit ($99.99)
7. Mastery for Builders ($14.99)
8. Behike Finance ($14.99)
9. Behike Wellness ($9.99)
10. All remaining products

## ESTIMATED TIME PER PRODUCT:
- Prompts 1-3: 1 agent, ~15 min
- Prompts 4-6: 1 agent, ~10 min
- Prompts 7-9: 1 agent, ~10 min
- Prompt 10: 1 agent, ~5 min
- Total per product: ~40 min with parallel agents
- Total for 10 products: ~4-5 hours

Nothing ships until Prompt 10 passes. No exceptions.
