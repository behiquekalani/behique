---
title: "computer2-openclaw-instructions"
type: knowledge
tags: [instructions, for, claude]
created: 2026-03-16
---

# Instructions for Claude Code on Computer 2

You are setting up OpenClaw on this machine. This machine runs Ollama (llama3.2) and serves as the local AI server on the network at 192.168.0.151.

## Step 1: Install OpenClaw

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

If that fails (Node not found), install Node first:
```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs
```
Then retry the OpenClaw install.

## Step 2: Skip onboarding for now, configure manually

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

Then create the config:
```bash
mkdir -p ~/.openclaw
```

Write `~/.openclaw/.env`:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Step 3: Verify Ollama is accessible

```bash
curl http://localhost:11434/api/tags
```

Should return your installed models.

## Step 4: Verify OpenClaw

```bash
openclaw doctor
openclaw status
```

## Step 5: Start the daemon

```bash
openclaw onboard --install-daemon
```

## Done

Report back what `openclaw doctor` shows. The main machine (Computer 1) will handle Telegram and API keys — this machine just needs to serve Ollama through OpenClaw.
