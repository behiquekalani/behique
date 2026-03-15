# Computer 2 — Claude Code Session Instructions
# Give these to Claude Code on Computer 2 (192.168.0.151)
# Date: 2026-03-15

---

## CONTEXT

You are running on Computer 2, Kalani's Windows worker node. The main Ceiba instance is running on his Mac. You are the second agent — your job is infrastructure that the Mac can't do (Cloudflare tunnels, n8n config, Ollama management).

The project folder is `~/behique` (synced via Syncthing from Mac in real time).

---

## YOUR TASKS (in order)

### 1. Create a named Cloudflare tunnel for n8n

n8n needs a stable HTTPS URL for Telegram webhooks. The current quick tunnel URL rotates on restart.

```bash
# Install cloudflared if not already installed
# On Windows: winget install Cloudflare.cloudflared

# Login to Cloudflare (opens browser)
cloudflared tunnel login

# Create the named tunnel
cloudflared tunnel create behique-n8n

# Create config file at ~/.cloudflared/config.yml:
```

```yaml
tunnel: behique-n8n
credentials-file: C:\Users\Kalani\.cloudflared\<TUNNEL_ID>.json

ingress:
  - hostname: n8n.behique.dev
    service: http://localhost:5678
  - service: http_status:404
```

If Kalani doesn't have a domain yet, use the tunnel's default URL instead:
```bash
cloudflared tunnel route dns behique-n8n n8n-behique.cfargotunnel.com
```

Then run:
```bash
cloudflared tunnel run behique-n8n
```

Register it with pm2 so it survives restarts:
```bash
pm2 start cloudflared -- tunnel run behique-n8n
pm2 save
```

### 2. Update n8n webhook URL

Once the tunnel is live, go to n8n settings:
- Open http://localhost:5678/settings
- Set Webhook URL to the tunnel's HTTPS URL
- Save and restart n8n: `pm2 restart n8n`

### 3. Test the Telegram webhook

The /spec workflow in n8n has a Telegram trigger node. Once the webhook URL is set:
- Open the /spec workflow in n8n
- Activate it
- Send a test message to the bot on Telegram
- Verify the webhook fires

### 4. Report back

After completing these tasks, update `~/behique/primer.md` LIVE STATE block:
```
Last update: [date] — Cloudflare named tunnel live on Computer 2.
Focus: n8n webhooks now have stable HTTPS via behique-n8n tunnel.
Next action: Test /spec workflow end-to-end with Telegram trigger.
Blocker: [any blockers found]
Session status: TUNNEL LIVE
```

Syncthing will sync primer.md back to Mac automatically.

---

## WHAT NOT TO DO

- Don't touch routing.py or ceiba_lite.py — Mac Ceiba handles those
- Don't modify CLAUDE.md or vault files — those are Mac-managed
- Don't install new Python packages without checking with Kalani
- Don't create new projects or side-track into other tasks
- Focus: tunnel, n8n webhook, test, report back. That's it.

---

## SERVICES ALREADY RUNNING ON THIS MACHINE

| Service | Manager | Port |
|---------|---------|------|
| n8n | pm2 | 5678 |
| Ollama | system service | 11434 |
| Syncthing | scheduled task | 8384 |
