End-of-session protocol. Do every step in order.

1. Update `primer.md` with everything done this session. Full rewrite. Include: what was built, current state of all active projects, next actions, open blockers. This is NOT optional.

2. Update `Ceiba/MASTER_TODO.md`. Mark completed items with [x]. Add any new tasks that came up during the session. Remove anything that no longer applies.

3. Run voice checker on any new content files created this session:
   ```
   python3 tools/voice_checker.py <file> --fix
   ```
   Apply to any .md files in Ceiba/news/, any new product copy, any new landing page text.

4. Quick security scan on any new files:
   - Check for hardcoded API keys, tokens, passwords
   - Check for personal info that should not be in the repo (names, addresses, SSN)
   - Check .gitignore covers any new sensitive files
   - Report findings. Do NOT commit secrets.

5. Log session summary to `Ceiba/SESSION_LOG_YYYY-MM-DD.md` (use today's date). Include:
   - Session number (increment from last log)
   - Duration estimate
   - What was built/changed
   - Decisions made
   - Open questions
   - Files created or modified

6. Queue autonomous tasks for overnight by running:
   ```
   python3 tools/ceiba_autonomous.py --plan
   ```
   Show Kalani what will run autonomously. If the plan looks good, note it in the session log.

7. Say goodnight. Something real, not corporate. Reference what was actually accomplished.
