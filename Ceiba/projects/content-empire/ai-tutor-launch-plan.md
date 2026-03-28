# AI Tutor — Go-to-Market Plan

## Target audience

### Primary: ADHD students

ADHD brains struggle with passive studying. Reading without active recall is nearly useless for retention. The accountability layer in AI Tutor, XP, streaks, structured lessons, is not a nice-to-have for this group. It is the core value.

This audience also has a strong community. r/ADHD has 4 million members. ADHD content performs well on TikTok and Instagram. Personal stories about tools that "actually work for my brain" spread organically.

Positioning for this audience: "A study tool that works with how your brain actually works."

### Secondary: College students

Large addressable market. High urgency around exam periods. Document-centric studying is exactly how college works: textbooks, lecture notes, study guides. The product fits the workflow without asking students to change how they study.

Positioning for this audience: "Turn your notes into a practice exam in 30 seconds."

### Tertiary: Professionals studying for certifications

Higher willingness to pay. Clear ROI (passing the exam means career advancement or license renewal). Less price-sensitive than students. Study materials are well-defined, which makes the source-locked approach particularly valuable.

Positioning for this audience: "Study from the exact material on your exam. Nothing else."

---

## Launch channels

### Reddit

Reddit is the first channel because it is free, the audiences are concentrated, and genuine product stories perform well when they are not pitched as ads.

**r/ADHD** (4M members). Angle: personal story about building a study tool for ADHD brains. Show the XP and streak system. Talk about why passive reading fails and what active recall actually means. End with a free trial link. Do not make it promotional. Make it a story.

**r/studytips** (800K members). Angle: "I built a tool that generates quizzes from any PDF automatically." Show a before/after. Upload a chapter, show the generated questions. This subreddit is receptive to tools that save time on prep work.

**r/learnprogramming** (4.5M members). Angle: "I use this to study programming documentation and generate quiz questions from it." Developers are document-heavy learners. JavaScript docs, system design guides, certification prep materials all work well.

**r/GetStudying**, **r/college**, **r/Professors** are secondary targets for the same content adapted to each community.

Rules: read the subreddit rules before posting. Most allow tool posts if they are framed as genuine use cases, not ads. Post once, engage the comments, do not spam.

### Product Hunt

Launch on a Tuesday or Wednesday. The goal is not to win the day, it is to get into the "featured" products and generate initial signups from an audience that actively looks for new tools.

Pre-launch tasks: build a waitlist, collect 20-30 people who will upvote on launch day, prepare the tagline, screenshots, and a short demo video. The demo video matters. Show the full flow: upload PDF, see the learning path, ask a question, take a quiz, see XP awarded.

Post-launch: respond to every comment on launch day. This increases visibility on the platform and converts passive viewers to signups.

### Twitter

Primary format: build-in-public posts. Short threads showing specific parts of the product being built or used. "Uploaded my CISSP study guide. AI generated 47 quiz questions from it. Here is what that looks like." Include screenshots.

This audience follows product builders. They are not your primary users, but they share tools that are interesting and often have audiences that overlap with your target.

Secondary format: reply to tweets from students complaining about studying. Not pitching, just being present in the conversation. When it comes up naturally, mention the tool.

### Instagram and TikTok (secondary, after initial launch)

Short-form video of the product in use. 30-60 seconds. Show the flow. "I uploaded my chemistry textbook and got this." Works better once there are real users generating interesting use cases you can showcase.

---

## Free tier strategy: the viral loop

The free tier is the acquisition engine.

Every exported note from AI Tutor includes a one-line attribution: "Studied with AI Tutor. Try it free at [link]." This is visible to anyone the user shares their notes with. Study groups share notes. Students post notes in Discord servers and group chats. Each shared export is a passive distribution event.

The attribution is opt-out, not opt-in. Free tier users who do not want the attribution can remove it by upgrading.

This creates a loop: free users study and share notes, shared notes are seen by potential users, potential users try the free tier, some upgrade. No ad spend required.

Secondary viral surface: the streak system. "Day 14 streak on my bar exam prep" is a natural social share. Build a one-click share card for streak milestones. People share streaks on Twitter and Instagram. Each share shows the product name.

---

## Pricing rationale

### Free tier exists to remove the barrier to trying

If the first interaction requires a credit card, most potential users stop there. The free tier is functional enough to demonstrate real value. The 1-document and 100-page limits are real constraints that create legitimate reasons to upgrade without making the free tier feel broken.

### $9.99/month is positioned below the pain threshold

Most students and professionals spend more than $9.99 on a single study session at a coffee shop. The price needs to feel insignificant relative to the value (passing an exam, advancing a career). $9.99 does that. $19.99 for an individual would not.

### $19.99/month for Team splits the cost

If five students split a Team plan, each pays $4/month. This is a realistic group scenario, especially for friend groups studying for the same exam. The per-person cost is low enough to make it an easy group decision.

---

## Competitor comparison

### ChatPDF

ChatPDF is a document chatbot. You upload a PDF and chat with it. No gamification, no learning path, no quiz generation, no XP, no streaks. It is a Q&A tool. The difference is structure and retention mechanics.

ChatPDF's strength is simplicity. Its weakness is that it solves information retrieval, not learning. You can ask ChatPDF what a concept means. You cannot use ChatPDF to prove you understand it.

### Coursera

Coursera offers structured courses with quizzes and completion tracking. The fundamental limitation is that you cannot bring your own content. You are locked to Coursera's course catalog. If your exam uses a specific textbook that Coursera does not cover, Coursera cannot help.

AI Tutor inverts this: bring any material, get a Coursera-like experience from it.

### Anki

Anki is flashcards. It is excellent for memorization and has a proven spaced repetition algorithm. Its weaknesses: it requires you to create the cards manually, it has no conversational AI layer, and the interface is dated enough that many users abandon it.

AI Tutor generates the quiz questions automatically, which removes the biggest friction point in using Anki. The trade-off is that AI Tutor does not yet implement spaced repetition scheduling. That is a roadmap item.

### NotebookLM (Google)

NotebookLM is a research and summarization tool. It lets you chat with multiple documents and generates summaries and study guides. It does not have gamification, quizzes, XP, or streaks. It is designed for research, not for learning through repetition.

The audience overlap is high. Users who know NotebookLM understand the source-locked AI concept and are already sold on the value. The pitch to this group is: "Like NotebookLM but with the structure and retention mechanics to actually make the knowledge stick."

---

## First 100 users acquisition plan

### Week 1-2: Soft launch, personal network

Post the product in communities where Kalani is already present. Discord servers for builders, subreddits followed regularly, Twitter followers. The goal is not scale, it is feedback. These early users will find bugs, ask for features, and tell you what the product is actually useful for.

Target: 20-30 free signups with genuine usage.

### Week 3-4: Reddit posts

One post in r/ADHD. One post in r/studytips. Frame both as personal stories, not promotions. Include a short video or screenshots showing the key flow.

Target: 50-100 signups from Reddit traffic.

### Week 5-6: Product Hunt launch

Coordinate with people from Week 1-2 to support the launch. The goal is enough visibility to hit the daily featured list.

Target: 50-100 additional signups from Product Hunt.

### Ongoing: Viral loop activation

Monitor whether the note export attribution is generating referral traffic. If it is, double down on making the export sharable and beautiful. If it is not, find the friction point and fix it.

Total target for first 90 days: 200-300 free users, 10-20 paying.

---

## Metrics to track at 30/60/90 days

### 30 days

- Total signups
- Free tier activation rate (signed up, uploaded at least one document)
- Day 7 retention (did they return within 7 days of first session)
- Conversion rate from free to paid
- Top subreddits and referral sources driving traffic

### 60 days

- Monthly active users (logged in and studied at least once in the past 30 days)
- Average session length
- Average streak length before drop-off
- Number of documents uploaded per active user
- Upgrade conversion rate compared to 30-day baseline

### 90 days

- Monthly recurring revenue (MRR)
- Churn rate (paying users who cancelled in the past 30 days)
- Net Promoter Score (survey active users)
- Which features are most used (quiz vs. chat vs. export)
- Organic referral rate (signups that came from shared note exports)

### North star metric

Monthly active users who complete at least one quiz session per week. This is the behavior that separates users who are getting real value from users who signed up and forgot about it.

---

## Adjacent opportunities

If the product works, two expansions follow naturally.

First, a teacher or course creator tier. An instructor uploads their course materials. Students in the class each get a tutor for those materials. The instructor sees aggregate progress data. This adds institutional distribution alongside the consumer path.

Second, corporate training. A company uploads onboarding documentation or compliance materials. New employees study from it. HR sees completion rates. This is a higher-priced B2B play with a different sales motion but uses the exact same product infrastructure.

Neither of these should be built before the core product has 100 paying users. Validate the consumer case first.

---

*Plan written March 2026. Revisit at 30-day mark.*
