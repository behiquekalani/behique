# KALANI_CLAUDE_PLAYBOOK

Short reference. How to talk to Claude so it stops drifting, and basic git so you don't lose work.
Paste this (or link it) at the start of any new Claude session.

---

## 1. What you're doing wrong (real patterns from your chats)

- **Mega-prompts.** You asked for 3 website variants + Liquid conversion + SEO audit + security audit + Shrine Pro features in one message. No AI holds all that. It picks 1-2 and fakes the rest.
- **Contradictions inside one thread.** "No concrete" then "use concrete." The model treats both as equally true and blends them.
- **Uploading full zips.** Claude wastes context parsing folder trees when you needed 40 lines of one file.
- **Arguing when it's wrong.** Every "no you did it wrong" turn burns tokens and makes the drift worse.
- **Zero state between sessions.** Each new chat starts from nothing. Steam dies.
- **No git.** When Claude breaks code, you have no undo, so you try to fix it by chatting, which makes it worse.

## 2. Fixes (exact behaviors)

- **One task per prompt.** Finish. Then next. "Build the header" → done → "now the product grid."
- **Start with a verbosity rule.** "Code only. No prose. No explanations unless I ask."
- **Paste the exact code block.** Not the whole site. Not a zip. The 30-80 lines that matter.
- **When Claude drifts, reset — don't argue.** Open a new chat. Paste the last working code + the single next instruction.
- **Use "NEVER" not "don't".** Models follow hard negatives better. "NEVER introduce new CSS classes."
- **Say "inject" / "replace," never "merge" or "blend."** "Merge" tells the AI to invent a middle ground.
- **Name the skeleton vs. the skin.** "Skylark HTML is the skeleton. Obra text/images are the skin. Skin goes in. Skeleton stays untouched."

## 3. Git in 5 commands (enough to not lose work)

```bash
git status                 # what changed
git add .                  # stage everything
git commit -m "message"    # save point
git log --oneline          # list save points
git checkout .             # undo all unstaged changes (escape hatch)
```

Rule of thumb:
- **Before** you paste AI code into a file: `git add . && git commit -m "before AI change"`
- **After** it works: `git commit -am "AI change worked: X"`
- **If it broke it**: `git checkout .` — back to last commit, instantly.

If the terminal stresses you out, install **GitHub Desktop**. Same commands, clickable buttons. Zero shame in that.

## 4. Branching (stop overwriting good versions)

Each website variant = its own branch. You can jump between them without losing anything.

```bash
git checkout -b v1-skylark      # make + switch to a new branch
git checkout main                # go back to main
git checkout v1-skylark          # switch back to your variant
git branch                       # list all your branches
```

You wanted 3 obra versions? That's 3 branches: `v1-skylark`, `v2-yeezy`, `v3-concrete`. Each one has its own commits. None of them mess with each other.

## 5. Session handoff protocol (stop losing steam between chats)

Keep one file per project: **`CURRENT_STATE.md`**

Four lines, updated at end of every session:

```
CURRENT TASK: Skylark layout + obra content
CONSTRAINTS: NEVER use concrete textures. NEVER change Skylark CSS.
LAST WORKING FILE: /websites/obra-skylark/index.html
NEXT STEP: Swap product grid to use obra images
```

Start every new Claude session with:
> "Read CURRENT_STATE.md. That's the anchor. Follow it exactly."

End every session with:
> "Update CURRENT_STATE.md with what we finished and the next step."

Then commit that file. Git log + `CURRENT_STATE.md` = your memory across sessions.

## 6. Things to never do

- Never attach a zip when you only need one file
- Never ask "also can we fix X and Y?" mid-task
- Never keep arguing past 2-3 wrong replies — start a fresh chat
- Never write "merge the styles" — write "inject obra content into existing skylark HTML"
- Never accept AI code changes without committing first
- Never start a new session without pasting CURRENT_STATE.md

## 7. Token-saver openers (copy-paste)

Start of any code session:
```
Code only. No prose. No explanations. No "would you like me to also...".
Reply in minimal tokens. If you understand, reply "ok".
```

When feeding a skeleton + skin:
```
SKELETON (do not modify CSS or structure):
<paste html>

CONTENT (inject into existing elements):
<paste product names/prices/images>

TASK: Replace text/images only. Output full HTML once.
```

When it drifts:
```
Wrong. You violated constraint [X]. Fix only that. Output code only.
```
(If it drifts twice more: start a fresh chat with last good code.)

---

**Bottom line:** you're not a shitty programmer. You're trying to build without a safety net (git) and without a memory system between chats (CURRENT_STATE.md). Add those two things and your flow stops breaking.
