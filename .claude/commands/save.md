Emergency context save. Run this when context is getting low.

1. Update primer.md with EVERYTHING done this session:
   - List every file created/modified
   - List every agent that ran and what it built
   - List what's still running or incomplete
   - Set the "next action" to the most important unbuild item

2. Update Ceiba/AUTONOMOUS_LOG.md with session summary

3. Update Ceiba/MASTER_TODO.md - mark completed items, add new ones discovered

4. Write Ceiba/SESSION_HANDOFF.md with:
   - What was being built when context got low
   - Exact file paths of work in progress
   - Agent IDs still running (if any)
   - The NEXT 5 things to build (in priority order)
   - Any copy-paste prompt that the next session should run immediately

5. Run voice_checker.py on any new .md product files

6. Convert any new products to PDF

This ensures ZERO work is lost between sessions. The next session reads SESSION_HANDOFF.md and picks up exactly where we left off.
