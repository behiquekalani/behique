---
title: "computer2-session-instructions"
type: knowledge
tags: [paste, this, into]
created: 2026-03-16
---

# PASTE THIS INTO CLAUDE CODE ON COMPUTER 2

You are running on Computer 2 (192.168.0.151), Kalani's Windows worker node. The main Ceiba instance is running on his Mac. Your job is one thing: get n8n a stable HTTPS webhook URL via a named Cloudflare tunnel.

## Step 1: Install cloudflared (if not installed)
Run `winget install Cloudflare.cloudflared` or check if `cloudflared --version` already works.

## Step 2: Login to Cloudflare
Run `cloudflared tunnel login` — this opens a browser for auth. Wait for Kalani to approve if needed.

## Step 3: Create the named tunnel
```
cloudflared tunnel create behique-n8n
```
Note the tunnel ID from the output.

## Step 4: Create the config file
Write `C:\Users\Kalani\.cloudflared\config.yml` with:
```yaml
tunnel: behique-n8n
credentials-file: C:\Users\Kalani\.cloudflared\<TUNNEL_ID>.json
ingress:
  - hostname: behique-n8n.cfargotunnel.com
    service: http://localhost:5678
  - service: http_status:404
```
Replace `<TUNNEL_ID>` with the actual ID from step 3.

If Kalani has a custom domain, ask him. Otherwise use the tunnel's default URL.

## Step 5: Route DNS
```
cloudflared tunnel route dns behique-n8n behique-n8n
```

## Step 6: Start the tunnel and register with pm2
```
pm2 start cloudflared -- tunnel run behique-n8n
pm2 save
```

## Step 7: Update n8n webhook URL
Go to http://localhost:5678/settings and set the Webhook URL to the tunnel's HTTPS URL. Then:
```
pm2 restart n8n
```

## Step 8: Test
The /spec workflow in n8n has a Telegram trigger. Activate it and ask Kalani to send a test message to the bot.

## Step 9: Update primer.md
Edit `~/behique/primer.md` LIVE STATE block to reflect the tunnel is live. Syncthing will sync it to Mac.

## Rules
- Do NOT touch routing.py, ceiba_lite.py, CLAUDE.md, or vault files
- Do NOT install Python packages or start new projects
- If something fails, troubleshoot it. Don't skip steps.
- When done, stop. Don't look for more work.
