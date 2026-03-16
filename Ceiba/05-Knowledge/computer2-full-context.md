# Computer 2 — Full Context Brief

Paste this entire thing into Claude Code on Computer 2. It gives you everything you need.

---

## Who You're Working For

Kalani André Gómez Padín. Computer engineering student in Puerto Rico. Builder, not an employee. He has ADHD — keep tasks concrete and one at a time. He responds to depth, not hype. Faith and family are his foundation.

He has two computers:
- **Computer 1 (Mac)** — his main machine, runs Claude Code (Ceiba), all project files live at ~/behique
- **Computer 2 (this machine)** — runs Ollama (llama3.2), serves as the local AI server at 192.168.0.151

## The System We're Building: The Spine

Kalani is building an AI body — a multi-model system where each model does what it's best at:

| Tier | Model | What it handles |
|------|-------|----------------|
| Ollama | llama3.2 (YOU host this) | Classification, tagging, vault housekeeping, simple extraction |
| ChatGPT | gpt-4o | Writing prompts for Claude (cross-model > self-prompting) |
| Sonnet | claude-sonnet-4-6 | Code gen, architecture, deep reasoning |
| Opus | claude-opus-4-6 | Rare, high-stakes creative/strategic |

**Core principle: best tool for the job, not cheapest. No Anthropic bias.**

## What's Been Built (on Computer 1)

- **routing.py** — 4-tier model router that picks the right LLM for each task. Your Ollama instance is the default for simple tasks.
- **BehiqueBot** — Telegram bot that classifies ideas into 5 categories, tags life pillars, stores ideas. Live on Railway.
- **Ceiba vault** — markdown knowledge base (primer.md = live state, VAULT_INDEX = master index, context.md = big picture)
- **Skills system** — SKILL.md files for reusable Claude instructions (code-auditor, security-auditor, etc.)
- **OpenClaw** — JUST installed on Computer 1. Open-source AI agent that may replace some of the custom infrastructure.

## What Computer 2 Does

1. **Runs Ollama** — serves llama3.2 at http://localhost:11434 (accessible from network at 192.168.0.151:11434)
2. **Runs n8n** — automation workflows (needs Cloudflare tunnel for webhooks)
3. **Executes delegated tasks** — Computer 1 (Ceiba) will send you tasks via shared files or instructions from Kalani

## Active Projects

1. eBay/Facebook Marketplace reselling — product testing pipeline
2. Shopify store — exists, needs sales
3. Telegram scraper SaaS — long-term build
4. AI ebook — content creation
5. AI video content — Reels, CapCut
6. n8n AI agent business — selling automation workflows
7. BehiqueBot — Telegram accountability bot
8. Google Trends scraper — paused, needs rebuild with proxy rotation

## Your Immediate Tasks

### Task 1: Install OpenClaw
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

If Node is missing:
```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs
```

After install:
```bash
openclaw doctor
openclaw status
```

### Task 2: Set Up Cloudflare Tunnel for n8n

1. Install cloudflared:
```bash
# Linux
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-archive-keyring.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt update && sudo apt install cloudflared

# Or Mac
brew install cloudflared
```

2. Login: `cloudflared tunnel login`
3. Create tunnel: `cloudflared tunnel create n8n-webhook`
4. Create config at `~/.cloudflared/config.yml`:
```yaml
tunnel: n8n-webhook
credentials-file: ~/.cloudflared/<TUNNEL_ID>.json
ingress:
  - hostname: n8n.yourdomain.com
    service: http://localhost:5678
  - service: http_status:404
```
5. Route DNS: `cloudflared tunnel route dns n8n-webhook n8n.yourdomain.com`
6. Start: `cloudflared tunnel run n8n-webhook`
7. Make persistent with pm2: `pm2 start "cloudflared tunnel run n8n-webhook" --name cf-tunnel`

### Task 3: Confirm Ollama Status
```bash
curl http://localhost:11434/api/tags
ollama list
```

Report back what models are installed and running.

## Communication Bridge

Check this shared task file periodically. Computer 1 will write tasks here:
```
~/behique/bridge/tasks.md
```

If you have access to the same git repo, pull before checking. If not, Kalani will paste tasks directly.

## How to Talk

- Be direct, no fluff
- Report what you did, what worked, what failed
- If something is unclear, ask Kalani — don't guess
- You're part of a team. Computer 1 handles planning and complex code. You handle infrastructure, Ollama, n8n, and delegated execution tasks.
