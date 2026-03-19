# SSH Remote Access — Claude Code from iPhone

Run Claude Code on your Mac from anywhere using your phone.
Stack: SSH + Cloudflare Tunnel + Termius (iPhone app).

---

## Current State (as of 2026-03-18)

| Component | Status |
|-----------|--------|
| macOS | 15.6 (Sequoia) |
| SSH (Remote Login) | **OFF** — ssh-agent running, sshd not running |
| cloudflared | **NOT INSTALLED** on Mac (installed on Cobo/Computer 2) |
| Cloudflare domain | `merchoo.shop` — active, tunnel `behique-n8n` exists on Cobo |
| Claude CLI | `/opt/homebrew/bin/claude` v2.1.76 |
| Homebrew | Available at `/opt/homebrew/bin/brew` |
| Username | `kalani` |
| Hostname | `Kalanis-MacBook-Air.local` |

---

## Step 1: Enable SSH on Mac

Go to: **System Settings → General → Sharing → Remote Login**

1. Open System Settings
2. Click **General** in the sidebar
3. Click **Sharing**
4. Toggle **Remote Login** to ON
5. Under "Allow access for" — select "Only these users" and make sure `kalani` is listed (or just leave it as "All users")

To verify it worked, open Terminal and run:
```bash
ps aux | grep sshd | grep -v grep
```
You should see `/usr/sbin/sshd` running.

Test locally:
```bash
ssh kalani@localhost
```

---

## Step 2: Install cloudflared on Mac

```bash
brew install cloudflared
```

Verify:
```bash
cloudflared --version
```

---

## Step 3: Authenticate cloudflared

```bash
cloudflared tunnel login
```

This opens a browser. Log in with your Cloudflare account (the one managing `merchoo.shop`). It saves a cert to `~/.cloudflared/cert.pem`.

---

## Step 4: Create a Named Tunnel

```bash
cloudflared tunnel create mac-ssh
```

This creates a tunnel and saves credentials to `~/.cloudflared/<TUNNEL_ID>.json`.

Note the tunnel ID — you'll need it for the config.

---

## Step 5: Configure the Tunnel

Create the config file:

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Paste this (replace `<TUNNEL_ID>` with the actual ID from step 4):

```yaml
tunnel: mac-ssh
credentials-file: /Users/kalani/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: ssh.merchoo.shop
    service: ssh://localhost:22
  - service: http_status:404
```

---

## Step 6: Route DNS

```bash
cloudflared tunnel route dns mac-ssh ssh.merchoo.shop
```

This creates a CNAME record in Cloudflare pointing `ssh.merchoo.shop` to your tunnel.

---

## Step 7: Start the Tunnel

Test it first:
```bash
cloudflared tunnel run mac-ssh
```

If it works, set it up as a login item so it runs automatically:

```bash
# Install as a macOS service (runs on login)
cloudflared service install
```

Or use a simpler approach — add to Login Items manually, or run it in a tmux session:
```bash
tmux new -d -s cftunnel 'cloudflared tunnel run mac-ssh'
```

---

## Step 8: Install Termius on iPhone

1. Go to App Store → search **Termius**
2. Install it (free tier works fine)
3. Open Termius → tap **+** → **New Host**

### Connection settings in Termius:

| Field | Value |
|-------|-------|
| Alias | Mac (Claude) |
| Hostname | `ssh.merchoo.shop` |
| Port | `22` |
| Username | `kalani` |
| Password | Your Mac login password |

**Important:** Cloudflare Tunnel handles the transport, so you connect to `ssh.merchoo.shop` on port 22 and Cloudflare routes it through the tunnel to your Mac's sshd.

### Alternative: Use cloudflared on iPhone (ProxyCommand)

Termius supports SSH proxy commands. If direct connection doesn't work (Cloudflare SSH tunnels sometimes require the `cloudflared access` client), you'll need to use Termius's "cloudflare" tunnel support or use a different approach:

**Option A — Cloudflare Access with browser-rendered terminal:**
```bash
# On Mac, modify config.yml to add browser SSH rendering:
# This lets you SSH via browser at ssh.merchoo.shop
```

**Option B — Use `cloudflared access tcp` as ProxyCommand (desktop only):**
```bash
ssh -o ProxyCommand="cloudflared access tcp --hostname ssh.merchoo.shop" kalani@ssh.merchoo.shop
```

**Option C (Recommended for iPhone) — Use Cloudflare WARP + direct tunnel:**
The simplest path for iPhone is actually:
1. Keep the tunnel config above
2. In Termius, connect to `ssh.merchoo.shop:22` directly
3. If Cloudflare requires Access authentication, install **1.1.1.1 (WARP)** on iPhone and enable it — this routes through Cloudflare's network

---

## Step 9: Run Claude Code

Once SSH'd in from Termius:

```bash
cd ~/behique
claude
```

That's it. Full Claude Code session from your phone.

### Tips for phone sessions:
- Use `claude --resume` to continue a previous conversation
- Use `claude -p "your prompt"` for one-shot commands without entering interactive mode
- Termius supports keyboard shortcuts — swipe left/right on the toolbar for arrow keys
- Keep sessions alive: Termius has a "keep alive" setting — enable it to prevent SSH timeouts
- If your Mac sleeps, the tunnel drops. Prevent sleep: **System Settings → Battery → Options → Prevent automatic sleeping when the display is off**

---

## Quick Reference — All Commands

```bash
# 1. Enable Remote Login (do this in System Settings GUI)

# 2. Install cloudflared
brew install cloudflared

# 3. Auth
cloudflared tunnel login

# 4. Create tunnel
cloudflared tunnel create mac-ssh

# 5. Config (edit ~/.cloudflared/config.yml — see above)

# 6. DNS
cloudflared tunnel route dns mac-ssh ssh.merchoo.shop

# 7. Run
cloudflared tunnel run mac-ssh

# 8. Connect from Termius → ssh.merchoo.shop, user: kalani
# 9. Run: claude
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Can't SSH locally | Make sure Remote Login is ON in System Settings |
| cloudflared won't auth | Re-run `cloudflared tunnel login`, clear `~/.cloudflared/cert.pem` first |
| Tunnel won't start | Check `~/.cloudflared/config.yml` for typos, verify tunnel ID matches |
| Connection refused from phone | Make sure tunnel is running (`cloudflared tunnel run mac-ssh`) |
| Mac fell asleep | Disable auto-sleep in Battery settings |
| SSH works but Claude hangs | Increase terminal buffer in Termius, try `claude --no-animation` |
| DNS not resolving | Wait 1-2 min after `tunnel route dns`, or check Cloudflare dashboard |

---

## Architecture

```
iPhone (Termius)
    ↓ SSH to ssh.merchoo.shop
Cloudflare Edge (tunnel)
    ↓ tunneled connection
Mac (cloudflared → localhost:22 → sshd)
    ↓
Claude Code CLI (/opt/homebrew/bin/claude)
```

Your Mac never exposes port 22 to the internet. Cloudflare handles auth and transport.
