# MIGRATING HQ TO CLAUDE CODE
# Written: 2026-03-15
# One-time setup guide. Delete this file after first successful Claude Code session.

---

## WHY WE'RE MOVING

Cowork is a wrapper. Claude Code is the raw tool. For what we're building (routing layers, wiki graphs, overnight agents), we need the raw tool.

What you gain in Claude Code:
- Direct terminal — run any bash command, execute Python, call git
- CLAUDE.md loads automatically when you open a project directory
- `claude --continue` picks up the last conversation (reduces the amnesia problem)
- Real git integration — commit, push, branch all from inside the session
- No UI overhead — faster, more direct
- Can run on Computer 2 too (Ceiba working on both machines)

What you lose:
- Rendered artifacts (the JSX system map won't render in terminal)
- The Cowork file presenter UI
- Easier for non-technical users (you don't need this)

---

## STEP 1 — INSTALL CLAUDE CODE

Open Terminal on your Mac and run:

```bash
npm install -g @anthropic-ai/claude-code
```

If you don't have Node.js:
```bash
brew install node
npm install -g @anthropic-ai/claude-code
```

Verify it worked:
```bash
claude --version
```

---

## STEP 2 — AUTHENTICATE

```bash
claude
```

First run will ask you to authenticate with your Anthropic account. Follow the prompt. Uses the same account as Claude.ai — your Max subscription applies.

---

## STEP 3 — SET YOUR PROJECT DIRECTORY

Always start Claude Code sessions from ~/behique:

```bash
cd ~/behique
claude
```

CLAUDE.md is in ~/behique. Claude Code reads it automatically on startup. Ceiba loads.

---

## STEP 4 — FIRST SESSION COMMANDS

When Claude Code opens, the first thing to say:

```
Run memory.sh and load the vault. Then tell me where we left off.
```

Claude Code will:
1. Read CLAUDE.md (loads identity, session protocol)
2. Run bash memory.sh (injects git state)
3. Read VAULT_INDEX.md → primer.md → observations.md
4. Open with something specific from the last session

---

## STEP 5 — KEY COMMANDS TO KNOW

```bash
# Start a session in your project
cd ~/behique && claude

# Continue the last conversation (reduces amnesia)
claude --continue

# Continue a specific conversation by ID
claude --resume [conversation-id]

# Run with a specific model
claude --model claude-sonnet-4-6

# Non-interactive (run a single command)
claude -p "update primer.md with today's session state"
```

---

## STEP 6 — INSTALL ON COMPUTER 2 (optional, do this later)

On Computer 2 (192.168.0.151), open terminal and run the same npm install.
Then cd to C:\Users\[you]\behique (Syncthing keeps it in sync).
Ceiba on Computer 2 reads the same vault. Same memory. Different hardware.

This is the redundancy plan — if Mac is unavailable, open laptop, SSH to Computer 2, run claude from ~/behique there.

---

## WHAT TO DO WITH COWORK

Don't delete it. Cowork is useful for:
- Rendering JSX artifacts (system map)
- File operations with the visual presenter
- When you want to share something visually

But Claude Code is HQ now. Cowork is the occasional visual tool.

---

## FIRST REAL TASK IN CLAUDE CODE

After you're set up, the first build task is:

**Add [[wiki links]] to the vault.**

Start with these three files:
1. `Ceiba/05-Knowledge/architecture-spine.md` — already has links at the bottom, expand them
2. `primer.md` — link to every project and concept mentioned
3. `Ceiba/VAULT_INDEX.md` — turn file references into proper [[links]]

Then build the link parser in wake.sh — a bash function that reads a file, extracts [[links]], and loads those files into context.

That's Month 1, Week 1.

---

*Delete this file after first successful Claude Code session. It's a one-time guide, not permanent memory.*
