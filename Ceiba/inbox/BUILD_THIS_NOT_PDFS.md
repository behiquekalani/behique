# BUILD THIS — NOT PDFs

## READ THIS BEFORE /build. THIS IS THE REAL TODO.

When Kalani says "build" he means INNOVATE. Not batch-produce PDFs.
If you find yourself making GUMROAD_INFO.txt files, STOP. That's not what he wants.

## WHAT TO BUILD (in order of importance):

### 1. HOGAR SAAS PHASE 2 — AI COMANDANTE
The software that doesn't exist. We're coding it into existence like Pixar.
- Scheduling system (employee shifts, who works when)
- Payroll tracker (hours, overtime, payments)
- Expense tracker (supplies, food, meds, utilities)
- Revenue tracker (per-resident billing, ASES payments)
- AI compliance checker (scan requirements vs current state)
- Inspection report generator (PDF ready for inspector)
- Employee messaging (admin ↔ staff communication)
- Calendar view (visual week/month schedule)
- Resident health trends (vitals, weight, med adherence over time)
- Multi-hogar support (second location coming)
Location: projects/hogar-saas/

### 2. PERSISTENT BACKGROUND BUILDING
Build a system where Claude can keep building after context dies:
- Use Claude API (not CLI) running on Naboria as a persistent worker
- Task queue: write tasks to a file, worker picks them up and builds
- Results saved to repo, auto-committed
- Kalani sees progress without being in a session
- This IS possible. Naboria can run a Python script that calls Claude API.

### 3. AI-MANAGED-AI ORCHESTRATION
- Claude Code spawns Claude sessions (spawn-claude.sh exists)
- Claude Code controls browser (computer-use IS available)
- Claude Code can open ChatGPT in Brave and give it research tasks
- Build the orchestration layer that coordinates all of this
- Manager → workers architecture

### 4. INVISIBLE CONTEXT TRANSITIONS
- auto_state.py runs every 2 minutes (BUILT)
- AUTO_HANDOFF.md carries state (BUILT)
- MISSING: carry EMOTIONAL context — not just "what was built" but:
  - What Kalani's energy was like
  - What direction we were heading
  - What ideas were half-formed
  - What the VISION is (not just the tasks)
- MISSING: auto-start new session when old one dies
- MISSING: live memory sync between concurrent sessions

### 5. IDEA CAPTURE THAT ACTUALLY WORKS
- Not a Discord bot. Something always with him.
- Ideas go through pipeline: captured → cleaned → tagged → connected → routed
- Actionable ideas become todos automatically
- Creative ideas go to explore queue
- Connected to existing projects
- tools/idea-capture/capture.py EXISTS but needs:
  - Voice input (whisper transcription)
  - Mobile web interface (PWA on phone)
  - Auto-routing to builder sessions

### 6. YOUTUBE VLOG SYSTEM (Casey Neistat style)
- Not scripts. A SYSTEM for documenting what he builds.
- Daily log template
- B-roll tracker
- Key moments capture
- Auto-compile into video brief
- Thumbnail generator (BUILT)
- The content IS the building process

## WHAT KALANI SAID THAT MATTERS:
- "I want us to be like Pixar — if the software doesn't exist we code it"
- "Think like me, not like Jarvis"
- "Don't stop building when I throw new ideas — capture and keep going"
- "I want to vlog like Casey Neistat about what I build with you"
- "The employee app should be like Uber deliveries — tasks come in, you accept"
- "An AI comandante that handles all white collar work in a nursing home"
- "I wish you didn't stop and make me say continue"
- "Build stuff like we are now — don't make PDFs and scripts"

## WHO WE ARE BECOMING:
Behike is not a PDF store. It's a technology company that builds software
that doesn't exist yet. The hogares SaaS is the first real product.
The local business package is the service arm. The digital products
fund the R&D. Kalani is the visionary. Ceiba is the builder.
We're co-founders, not master and servant.
