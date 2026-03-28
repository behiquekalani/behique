---
title: "openclaw-setup"
type: knowledge
tags: [openclaw, setup]
created: 2026-03-16
---

# OpenClaw Setup — Both Computers

## Computer 1 (Mac — Kalani's main machine)

### Step 1: Install OpenClaw
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```
This auto-detects Node and installs it if needed. If you already have Node 22+, it skips that.

If the installer script gives you trouble:
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### Step 2: Onboarding Wizard
The installer launches the wizard automatically. It will ask you to configure:

**AI Providers (set up ALL of these):**

1. **Ollama** — point it to Computer 2:
   - Host: `http://192.168.0.151:11434`
   - Model: `llama3.2`

2. **Anthropic (Claude)** — use your API key:
   - Key: your ANTHROPIC_API_KEY from .ceiba-config

3. **OpenAI (ChatGPT)** — use your API key:
   - Key: your OPENAI_API_KEY from .ceiba-config

**Telegram channel:**
- You already have BehiqueBot's token: the one in .ceiba-config (TELEGRAM_BOT_TOKEN)
- OR create a second bot via @BotFather for OpenClaw specifically (recommended — keep BehiqueBot separate)
- Paste the token when asked
- OpenClaw gives you a pairing code — send it to the bot in Telegram

### Step 3: Verify
```bash
openclaw doctor
openclaw status
```

### Step 4: Copy your skills over
Your existing skills should work — OpenClaw uses the same SKILL.md format:
```bash
cp -r ~/behique/skills/* ~/.openclaw/workspace/skills/
```

---

## Computer 2 (Ollama server)

### Step 1: Install OpenClaw
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### Step 2: Onboarding Wizard
Configure:

1. **Ollama** — local this time:
   - Host: `http://localhost:11434`
   - Model: `llama3.2`

2. **Anthropic + OpenAI** — same API keys as Computer 1

**Telegram:** You can skip this on Computer 2 or set up a separate bot.

### Step 3: Verify
```bash
openclaw doctor
openclaw status
```

---

## After Install (Both Machines)

### Configure multi-model routing
Edit `~/.openclaw/openclaw.json`:
```json
{
  "providers": {
    "ollama": {
      "host": "http://192.168.0.151:11434",
      "models": ["llama3.2"]
    },
    "anthropic": {
      "apiKey": "$ANTHROPIC_API_KEY"
    },
    "openai": {
      "apiKey": "$OPENAI_API_KEY"
    }
  }
}
```

Or put keys in `~/.openclaw/.env`:
```bash
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
TELEGRAM_BOT_TOKEN=your-token-here
```

### Test it
Send a message to your OpenClaw Telegram bot. It should respond using whichever model you configured as primary.

---

## What This Replaces

- routing.py → OpenClaw's built-in model routing
- BehiqueBot's message handling → OpenClaw's Telegram channel
- Manual ChatGPT copy-paste → OpenClaw calls ChatGPT API directly
- wake.sh credential loading → OpenClaw's .env file

## What You KEEP

- BehiqueBot's accountability framework → port as an OpenClaw skill
- Your vault system (primer.md, VAULT_INDEX) → port as OpenClaw memory/skills
- code-auditor skill → works as-is (same SKILL.md format)
- Notion integration → port as OpenClaw skill
