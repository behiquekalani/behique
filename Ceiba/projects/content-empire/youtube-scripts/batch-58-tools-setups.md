---
title: "YouTube Batch 58 -- Tools and Setups"
type: youtube-scripts
batch: 58
theme: tools-and-setups
created: 2026-03-22
status: draft
scripts: 5
estimated_length: "8-12 min each"
---

# YouTube Batch 58 -- Tools and Setups

---

## Script 1: My Complete Mac Setup for a One-Person Business

**Hook (first 15 seconds):**

> This is the exact Mac setup I use to run a one-person business. No team. No virtual assistant. Three networked machines doing the work of what would normally take five people to coordinate.
>
> I'm going to walk you through every app, every setting that matters, and the actual workflows that tie it together. Not a tour. Not a list of software. The actual system.

---

**[SECTION 1: The Foundation -- OS and System Settings]**

First thing I do on a fresh Mac: turn off everything that pulls attention.

Notifications off except for calendar and messages from family. Focus modes set up for three states: deep work, admin, and offline. System Preferences > Focus. No badge counts on any app icon. The dock is hidden by default.

Stage Manager is on. It sounds annoying but it saves me three context switches per hour once you get used to it.

Hot corners: top-right puts the display to sleep. Bottom-left opens Mission Control. I use Mission Control constantly. Four desktops: one for the project I'm building, one for communication, one for research, one for media and output.

File organization: everything lives in `~/behique`. That folder syncs across machines via Syncthing. The structure is flat enough to navigate quickly but organized enough that nothing gets lost.

```
~/behique/
  Ceiba/         -- memory, notes, project files
  tools/         -- scripts and automation
  bridge/        -- cross-machine task queue
  themes/        -- web assets
```

---

**[SECTION 2: The Browser -- Arc]**

Arc is my main browser. The reason is spaces. I have a space for each project area: product research, content pipeline, client work, and personal. Each space remembers its own tabs and doesn't bleed into the others.

The command bar (Cmd+T) replaces bookmarks entirely. I type what I want and Arc finds it. This alone cut my tab count by 60%.

Installed extensions: uBlock Origin, Bitwarden, and one custom CSS injector I use for dark mode on sites that don't offer it natively. That's it. No AI extensions. I use AI from the terminal, not the browser.

---

**[SECTION 3: Writing and Notes -- Obsidian]**

Obsidian is the operating system for my thinking. Full breakdown in the next video. For now: I run it in local-only mode. No Sync subscription. Syncthing handles the file sync.

Two vaults: one for business (linked to the behique folder), one for personal thinking and study. Business vault has a daily note that I write in every morning. It takes five minutes. It's the most valuable five minutes of the day.

The plugins I actually use: Dataview, Templater, Calendar, and a local graph view that I open when I'm thinking about how ideas connect.

---

**[SECTION 4: Terminal -- Warp]**

More on this in Script 3. Short version: Warp replaces iTerm2 for everything. The AI command assist is genuinely useful for flags I don't have memorized. The blocks interface makes scrolling through output actually workable.

My `.zshrc` has about 40 aliases. The most important ones:

```bash
alias ceiba='cd ~/behique && code .'
alias bridge='cat ~/behique/bridge/tasks.md'
alias sync='cd ~/behique && git add -A && git commit -m "auto: checkpoint" && git push'
```

That last one is dangerous if you use it without thinking. I use it for checkpoints only.

---

**[SECTION 5: AI Tools -- The Stack]**

Claude in the terminal via the Claude Code CLI. This is my main AI interface. Not the browser. Not a dedicated app. The terminal.

The reason: I work next to my code and my files. When Claude can see the file system, the responses are 10x more useful than pasting context manually.

Ollama for local model runs. Three models I keep available: llama3.2 for fast drafts, mistral for code review, and nomic-embed-text for embedding generation. All run on my M4 MacBook or routed to Cobo (my Linux machine with the 1080 Ti) for heavier tasks.

n8n runs locally for automation pipelines. I have a Railway-hosted version for things that need to stay running when my machine is closed.

---

**[SECTION 6: Design and Media]**

Figma for anything with a visual layer. I don't use Canva. I know that's an unusual take. Figma's component system is worth the learning curve even if you're not a designer.

CapCut for video editing. Still the fastest path from raw footage to something postable.

Whisper via CLI for transcription. I record voice memos constantly. The transcription pipeline turns them into structured notes automatically.

---

**[SECTION 7: The Workflows That Actually Matter]**

Three workflows I couldn't operate without:

**Morning capture:** Voice memo recorded in 10 minutes. Transcribed by Whisper. Sent to BehiqueBot via Telegram. Bot classifies and files it. I don't touch a keyboard until the thinking is done.

**Commit pipeline:** Every meaningful code change gets a git commit with a descriptive message. A post-commit hook appends the summary to `project_memory.md`. Six months from now I can read that file and know exactly what I built and when.

**End-of-session update:** Five minutes before I close the laptop. I rewrite `primer.md` with where I am, what just got done, and what the next action is. The next session starts from that file, not from memory.

Those three things prevent almost every form of context loss I used to experience.

---

**[CLOSING]**

That's the full setup. Not every app I have installed. The ones that actually run the business.

If you want the Obsidian system, that's the next video. If you want the terminal configuration in full, that's Script 3 in this batch.

The whole system as a file structure: download link in the description. It's a zip of my starter folder layout with empty templates.

---

## Script 2: How I Use Obsidian for Second Brain + Business Operations

**Hook (first 15 seconds):**

> Most people who say they use Obsidian as a second brain are lying. They have a folder full of notes that they never look at again.
>
> I'm going to show you how I actually use it. Not the theory. The specific vault structure, the daily workflow, and the three plugins that do real work.

---

**[SECTION 1: The Problem with Most Note-Taking Systems]**

The problem isn't the app. It's the mental model.

People think notes are for storing information. They're not. Notes are for thinking. The difference is that storage is passive and thinking is active. If you're not processing your notes regularly, you're just delaying the moment when you have to figure something out from scratch.

Obsidian solves this if you build it correctly. It does not solve it automatically.

---

**[SECTION 2: Vault Structure]**

My business vault lives at `~/behique/Ceiba/`. Here's the actual structure:

```
00-Inbox/        -- first capture, unprocessed
01-Projects/     -- one folder per active project
02-Areas/        -- ongoing responsibilities (health, finance, learning)
03-Check-ins/    -- daily notes, one file per day
04-Patterns/     -- observations, mental models, things I keep returning to
05-Knowledge/    -- permanent notes on specific topics
06-Archive/      -- completed projects, old material
07-Transcripts/  -- voice memo transcriptions
```

The numbers force alphabetical order in the file tree. The names are self-explanatory enough that I never have to think about where something goes.

---

**[SECTION 3: The Daily Note]**

Every morning. Five to ten minutes. The template:

```markdown
# {{date}}

## Yesterday's carry-over
[what didn't get done]

## Today's focus (one thing)
[one sentence]

## Captures
[anything that comes up during the day gets logged here]

## End-of-day note
[what actually happened]
```

That's it. No mood tracking. No habit tracker. Just the one thing and the captures.

The Dataview plugin turns these into a timeline I can scroll through. If I want to know when I first started working on a specific project, I can query the daily notes:

```dataview
LIST
FROM "03-Check-ins"
WHERE contains(captures, "product research")
```

---

**[SECTION 4: Project Notes]**

Each active project gets a folder inside `01-Projects/`. Inside that folder:

- `README.md` -- what the project is, what done looks like, current status
- `breadcrumbs.md` -- a running log of decisions and why I made them
- `next-action.md` -- one file, one next action, updated every session

The breadcrumbs file is the most valuable thing I've built. Six months from now I'll read it and understand exactly why the system is built the way it is. Without it, I'd be reverse-engineering my own decisions.

---

**[SECTION 5: Permanent Notes]**

These live in `05-Knowledge/`. A permanent note is a note I write in my own words, not copied from somewhere else, that captures a single idea completely.

Rules:
- One idea per note
- Written as if explaining to a reader, not just to myself
- Has links to related notes
- Gets reviewed every 90 days

I have about 80 of them right now. That number grows slowly because I'm strict about what gets permanent status. Most ideas are captures, not permanents.

---

**[SECTION 6: The Three Plugins That Actually Do Work]**

**Dataview** -- query your vault like a database. I use it for project dashboards, product idea lists, and revenue tracking templates. If you learn one plugin, make it this one.

**Templater** -- runs JavaScript in note templates. My daily note auto-populates the date and pulls the previous day's carry-over items. My project README template pulls the project name from the file name.

**Local Graph** -- built-in, not a plugin. But most people leave it at default settings. Zoom out to 0.3, set link distance to 100, set node size to file length. Now you can see your knowledge map at a scale that's actually useful.

---

**[SECTION 7: Business Operations in Obsidian]**

This is the part most tutorials skip.

I track three business metrics in Obsidian: revenue by product (updated weekly), content production (linked to my content calendar), and ideas in pipeline. All three are Dataview tables.

The content calendar is a folder of files named by date. Each file is one post or video. Status tracked as a tag: `#draft`, `#ready`, `#published`. One Dataview query shows me everything ready to post.

The bridge between Obsidian and the terminal: I have a script that reads `primer.md` and injects it into every Claude Code session. That means my AI assistant always knows my current project state without me typing it out.

---

**[CLOSING]**

Obsidian is not magic. The vault structure is not what makes it work. What makes it work is the daily discipline of returning to it.

Five minutes in the morning. Five minutes before you close your laptop. That's the minimum viable practice.

The starter vault template I use is in the description. No plugins installed. Just the folder structure and base templates. Add the plugins yourself. Start with Dataview.

---

## Script 3: The Terminal Setup That Makes Me 3x Faster

**Hook (first 15 seconds):**

> Most developers use maybe 20% of what their terminal can do. They type commands, read output, move on.
>
> I built a terminal setup that handles about a third of my daily workflow automatically. I'm going to show you the specific configuration -- Warp, the aliases, and the key commands I actually use every day.

---

**[SECTION 1: Why the Terminal First]**

Every GUI tool adds a layer of abstraction. Sometimes that's good. Often it's just slower.

The terminal is the one place where every tool is equally accessible. I can run Python scripts, query my notes, manage git, talk to Claude, control my servers, and build HTML files from the same window. Switching between GUIs for each of those things is friction I don't want.

Once your terminal is set up correctly, it's faster than every other tool for the things it can do.

---

**[SECTION 2: Warp -- The Setup]**

Warp is my terminal app. I switched from iTerm2 eight months ago and haven't looked back.

Three things that matter:

**Blocks.** Every command and its output is wrapped in a "block." You can collapse old blocks, copy just the output of one command, share a block with someone. This sounds minor until you're debugging a script with 200 lines of output and you can collapse everything you've already addressed.

**AI command assist.** I type `#` and then describe what I want in plain language. Warp writes the command. I review it. I run it if it looks right. This is not AI replacing my understanding. It's AI handling the flag lookup I'd otherwise do on Stack Overflow.

**Workflows.** Saved command sequences. I have workflows for: starting a dev server, running my content batch scripts, and doing my end-of-day git checkpoint.

---

**[SECTION 3: The `.zshrc` Configuration]**

The full file is 180 lines. Here are the sections that matter.

**Core aliases:**

```bash
# Navigation
alias b='cd ~/behique'
alias desk='cd ~/Desktop'
alias docs='cd ~/Documents'

# Git shortcuts
alias gs='git status'
alias ga='git add -A'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline -20'

# Project quick-jumps
alias ceiba='cd ~/behique && code .'
alias bot='cd ~/behique/tools/behiquebot'
alias bridge='cat ~/behique/bridge/tasks.md'

# Python shortcuts
alias py='python3'
alias venv='python3 -m venv .venv && source .venv/bin/activate'

# Servers
alias serve='python3 -m http.server 8000'
```

**Functions (more powerful than aliases):**

```bash
# Create a project folder with standard structure
mkproject() {
  mkdir -p "$1"/{src,docs,scripts}
  cd "$1"
  git init
  touch README.md .gitignore
  echo "Project $1 initialized"
}

# Search my Obsidian vault
vsearch() {
  grep -r "$1" ~/behique/Ceiba/ --include="*.md" -l
}

# Quick commit with message
checkpoint() {
  git add -A && git commit -m "auto: checkpoint $(date '+%Y-%m-%d %H:%M')"
}
```

---

**[SECTION 4: Key Commands I Use Every Day]**

These are not aliases. These are standard commands that people don't use enough.

**`fd` instead of `find`.** Faster, simpler syntax. `fd .py` finds all Python files from the current directory. `fd -e md Ceiba` finds all Markdown files in the Ceiba folder.

**`bat` instead of `cat`.** Syntax highlighted output. Reads like an editor, not a wall of text.

**`ripgrep` (rg) instead of `grep`.** Searches file contents across entire directories in milliseconds. I use this for searching my code and notes constantly.

**`jq` for JSON.** Any API response, any JSON file. `jq '.items | length'` tells me how many items are in a JSON array. `jq '.name'` pulls a specific field. Non-negotiable if you work with APIs.

**`tmux` for persistence.** If I'm running a long process, it goes in a tmux session so it survives if the terminal closes. Three commands: `tmux new -s name`, `tmux attach -t name`, `Ctrl+B then D` to detach.

---

**[SECTION 5: Claude Code in the Terminal]**

This deserves its own video. Short version: Claude Code runs in the terminal, has access to my file system, and can read, write, and execute code. It's not a chatbot. It's a collaborator that operates in my environment.

I start every coding session with:

```bash
cd ~/behique && claude
```

From there I can say "read primer.md and tell me what I was working on" or "look at the tools folder and clean up any dead scripts." It does the work in the terminal. I review and approve.

The speed difference compared to copy-pasting code into a browser tab is significant. Three hours of work becomes one.

---

**[SECTION 6: Shell Scripting as a Business Tool]**

Two scripts I run regularly that are worth seeing:

**`morning_brief.sh`** -- runs on wake. Reads `primer.md`, checks git status on all projects, shows today's calendar events via `icalBuddy`, prints the bridge task queue. Total runtime: 4 seconds. By the time coffee is poured, I know exactly what state the business is in.

**`content_batch.sh`** -- runs before a content session. Checks the content calendar Dataview output (via a Python script that reads the Obsidian vault), lists what's due for posting, opens the relevant files in Cursor.

Scripts like this are the real return on terminal investment. You write them once. They save you the same five-minute orientation every single day. Compound it over a year and that's days of time back.

---

**[CLOSING]**

The three things to start with: install Warp, write 10 aliases for your most common navigation commands, and learn `rg` for searching.

Everything else is additive. But those three changes will feel like a different computer within a week.

My `.zshrc` starter file is in the description. It's commented so you know what each line does.

---

## Script 4: Syncthing for Cross-Machine File Sync: Setup and Real World Use

**Hook (first 15 seconds):**

> Two machines. One Mac, one Linux box. Everything synced, always current, no subscription, no cloud middleman.
>
> Syncthing handles this for me and has for six months without a single data loss incident. Here's the setup and what I actually use it for.

---

**[SECTION 1: Why Not iCloud or Google Drive?]**

iCloud doesn't play well with Linux. Google Drive requires a client app that adds background processes and rate-limits sync. Dropbox is expensive for the storage I need. OneDrive is a Microsoft product.

Syncthing is open source, peer-to-peer, and stores nothing on any third-party server. Files go directly from machine to machine. The only server involved is a relay for NAT traversal, which can be self-hosted.

For a business where the files are the product, keeping them off third-party servers is not paranoia. It's just sensible.

---

**[SECTION 2: Installation]**

On Mac: `brew install syncthing`, then `brew services start syncthing`. The web interface runs at `http://127.0.0.1:8384`.

On Linux (Debian/Ubuntu): add the apt repository, `apt install syncthing`, enable as a systemd service.

Both machines now have a Syncthing daemon running in the background. Open the web interface on both. Add each device using the Device ID (visible in Settings > Device ID). Accept the connection request on the other machine.

Total time: about 15 minutes for both machines.

---

**[SECTION 3: Folder Structure for Sync]**

I sync two folders:

**`~/behique`** -- the full project folder. This is the primary sync. Every script, every note, every project file. About 2GB of data.

**`~/shared`** -- a smaller folder for files that cross between machines frequently. Datasets, model files, anything that's too big for the main repo but needs to be on both machines.

Configuration: both folders set to "Send and Receive" on both machines. Version history enabled with 30-day retention. This is the safety net. If I accidentally delete a file, it's in the `.stversions` folder.

---

**[SECTION 4: Conflict Handling]**

This is the part most documentation glosses over.

When two machines edit the same file at the same time, Syncthing creates a conflict file. It doesn't pick a winner. Both files survive.

Conflict files are named like: `filename.sync-conflict-20260322-MACHINEID.ext`

For my workflow, this almost never happens because I use git for code files (git handles conflicts) and I rarely edit the same note on two machines simultaneously. When it does happen, I have a small script that finds conflict files and shows me a diff:

```bash
find ~/behique -name "*.sync-conflict*" -exec ls -la {} \;
```

I review, pick the right version, delete the conflict file.

---

**[SECTION 5: Real-World Use Cases]**

**Case 1: Offloading compute to Cobo.**
Cobo is my Linux machine with a GTX 1080 Ti. When I need to run a model or a heavy script, I write the script on the Mac, it syncs to Cobo via Syncthing, I SSH into Cobo and run it. Results write to the shared folder and sync back.

**Case 2: Session continuity.**
I work on the Mac in the morning. Syncthing pushes everything. In the afternoon on a different machine (or via SSH), the state is current. `primer.md` is up to date. The git repo is up to date. No manual transfer step.

**Case 3: Backup redundancy.**
Both machines have the full file set. If one machine dies, no data is lost. I also push to GitHub for an off-site copy. Three copies is the minimum for anything I'd cry about losing.

---

**[SECTION 6: Performance and Limits]**

Sync speed depends on the local network. On my home network (gigabit), large file syncs run at about 100MB/s. Typical daily changes (code, notes) sync in under two seconds.

Battery impact on the Mac is negligible. The daemon uses maybe 0.2% CPU at idle.

Limits: Syncthing is designed for hundreds of thousands of files. It's not designed for constantly changing binary files (like a running database or a video being actively edited). For those cases, I pause sync during heavy operations.

---

**[CLOSING]**

Syncthing is one of those tools that disappears into the background after setup. After six months I don't think about it. Files are just where I expect them to be.

The setup guide with screenshots is in the description. It's the exact steps I used for my Mac + Ubuntu configuration.

---

## Script 5: The Git Workflow I Use for Solo Projects (No Team Required)

**Hook (first 15 seconds):**

> Git is not just for teams. Solo developers who don't use git properly are one hard drive failure away from losing months of work.
>
> Here's the workflow I actually use. It's simple. It's consistent. And it gives me a complete audit trail of every decision I've made on every project.

---

**[SECTION 1: The Mindset -- Git as a Time Machine]**

Most developers treat git as a backup tool. "I'll commit when the feature is done."

Wrong mental model. Git is a time machine with labeled stops. Every commit is a moment you can return to, examine, and understand. If you commit only when features are complete, you've thrown away all the intermediate moments.

The right mental model: commit when the code is in a state that makes sense. Not necessarily working. Just meaningful. "Added auth middleware (broken, debugging)." That commit is valuable. You can see what you tried. You can go back to before you tried it.

---

**[SECTION 2: The Commit Message Format I Use]**

Every commit message follows this format:

```
type: short description (under 50 chars)

Optional longer explanation if needed.
```

Types I use:
- `feat:` -- new feature or functionality
- `fix:` -- bug fix
- `refactor:` -- restructuring without behavior change
- `docs:` -- documentation or notes
- `auto:` -- automated checkpoint (from scripts)
- `wip:` -- work in progress (I know it's not clean yet)

Examples:
```
feat: add voice transcription to BehiqueBot
fix: handle empty response from Ollama endpoint
docs: update primer.md with current project state
auto: checkpoint 2026-03-22 09:15
```

Six months from now, `git log --oneline` tells me the entire story of the project. That log is a development diary.

---

**[SECTION 3: Branch Strategy for Solo Work]**

I use branches. Not because I have to. Because they let me experiment without risking the working state.

My rules:
- `main` is always in a working state. Never commit broken code directly to main.
- Feature work happens in `feat/description` branches.
- Experiments happen in `exp/description` branches. These get deleted when done.
- Hotfixes go directly to main (solo project, move fast).

Merge process: `git merge feat/branch --no-ff`. The `--no-ff` flag creates a merge commit even when fast-forward is possible. This means you can see in the log when a feature was merged in. Clean history.

---

**[SECTION 4: The Hooks That Automate the Work]**

Two git hooks I run on every project:

**post-commit:** appends the commit message and timestamp to `project_memory.md`. That file becomes a running development log. I can open it and read the entire history of decisions in plain text.

```bash
#!/bin/bash
echo "$(date '+%Y-%m-%d %H:%M') | $(git log -1 --format='%s')" >> project_memory.md
```

**pre-push:** runs a quick check for accidentally committed secrets. Looks for patterns like `sk-`, `API_KEY`, hardcoded passwords.

```bash
#!/bin/bash
if git diff HEAD~1 | grep -E "(sk-|API_KEY|password\s*=)" ; then
  echo "Possible secret detected. Review before pushing."
  exit 1
fi
```

These two hooks take ten minutes to set up. They've saved me from embarrassment at least twice.

---

**[SECTION 5: The Remote Setup]**

Private repos on GitHub for everything. Free tier covers unlimited private repos.

`git remote add origin git@github.com:username/repo.git` -- I always use SSH, not HTTPS. SSH keys don't expire and don't ask for passwords.

Frequency: I push at the end of every meaningful work session. Not every commit. But before I close the laptop, everything is off-machine.

The commit hook script I mentioned earlier also triggers a push reminder. Terminal output: "Session ended. Don't forget to push."

---

**[SECTION 6: Reading History -- The Commands I Actually Use]**

`git log --oneline -20` -- the 20 most recent commits in one line each. My most used git command.

`git log --all --graph --oneline` -- visual branch history. Shows where branches split and merged.

`git show COMMIT_HASH` -- full diff for a specific commit. When something broke, I use this to find exactly what changed.

`git bisect` -- binary search through commits to find when a bug was introduced. I've used this three times. It found the bug in under five minutes each time.

`git stash` -- I use this constantly. Working on something, need to check something else, don't want to commit yet. `git stash`, do the thing, `git stash pop`.

---

**[SECTION 7: What I Don't Do]**

I don't rebase to clean up history. Clean history is nice. Accurate history is better. If I wrote ten messy commits while figuring something out, those commits are real. They stay.

I don't force push to main. Ever. If I've pushed something and need to undo it, I make a new commit that reverses the change. The mistake stays in history. The correction stays in history.

I don't commit generated files, dependencies, or binary outputs. `.gitignore` handles this. My template `.gitignore` file covers Python, Node, and Mac-specific files.

---

**[CLOSING]**

Git is not a team tool. It's a precision instrument for anyone who writes code and wants to understand what they built and why.

The setup I use takes about an hour to put in place across all projects. The payoff compounds every month.

The starter config, my `.gitignore` template, and both hooks are in the description as a zip file.

---
