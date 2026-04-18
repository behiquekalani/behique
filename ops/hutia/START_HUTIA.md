# Hutia post-boot checklist

When Hutia boots (or you lost power and came back), run these steps in order. Takes about 2 minutes. Once auto-start is wired up (see `AUTOSTART.md`), this becomes a verification checklist, not a manual startup.

## 0. Verify Hutia is actually up

From Ceiba or your phone, ping it:

```bash
ping 192.168.0.152
```

If no response, Hutia isn't on the LAN yet. Wait 60 seconds, check wifi/ethernet.

## 1. Open Git Bash on Hutia

- Parsec into Hutia
- Open **Git Bash** (not PowerShell, not cmd). The commands below use bash syntax.

## 2. Start every service

Easiest: run the single script that starts everything.

```bash
cd ~/behique/ops/hutia
bash start-all.sh
```

You should see 5 "started PID XXXX" lines.

If you want to start them one-by-one (or something failed), here are the individual commands:

```bash
# 1. Behike main web server (port 8080)
cd ~/behique/themes/behike-store/landing-pages
nohup python -m http.server 8080 > /tmp/behike-store-server.log 2>&1 &

# 2. Stripe checkout (port 8081)
cd ~/behique/tools/stripe-checkout
set -a && source .env && set +a
nohup python server.py > /tmp/stripe-checkout.log 2>&1 &

# 3. Innova Barber (port 8090)
cd ~/behique/projects/innova-barber
nohup python redirect-server.py > /tmp/innova-barber-server.log 2>&1 &

# 4. Cloudflare Tunnel (connects local ports to public domains)
nohup "/c/Program Files (x86)/cloudflared/cloudflared.exe" tunnel run behike > /tmp/behike-tunnel.log 2>&1 &

# 5. Google Drive auto-deploy watcher
nohup python ~/behique/tools/gdrive-watcher.py > /tmp/gdrive-watcher.log 2>&1 &
```

## 3. Verify each service is listening locally

```bash
curl -s -o /dev/null -w "behike   %{http_code}\n" http://127.0.0.1:8080/
curl -s -o /dev/null -w "stripe   %{http_code}\n" http://127.0.0.1:8081/health
curl -s -o /dev/null -w "innova   %{http_code}\n" http://127.0.0.1:8090/
```

You want `200` on all three. If one returns `000` or connection refused, check its log:

```bash
tail -20 /tmp/behike-store-server.log
tail -20 /tmp/stripe-checkout.log
tail -20 /tmp/innova-barber-server.log
```

## 4. Verify the tunnel is up

```bash
tail -5 /tmp/behike-tunnel.log
```

Look for `Registered tunnel connection` or `connection established`. If you see errors, restart just the tunnel:

```bash
pkill -f cloudflared
nohup "/c/Program Files (x86)/cloudflared/cloudflared.exe" tunnel run behike > /tmp/behike-tunnel.log 2>&1 &
```

## 5. Verify public sites load

```bash
curl -s -o /dev/null -w "behike.co            %{http_code}\n" https://behike.co/
curl -s -o /dev/null -w "innovabarberpr.shop  %{http_code}\n" https://innovabarberpr.shop/
curl -s -o /dev/null -w "checkout.behike.co   %{http_code}\n" https://checkout.behike.co/health
```

All `200` means you are fully live.

## 6. (Optional) Confirm the uptime monitor sees you

If you have the Google Apps Script monitor configured (see `projects/uptime-monitor/`), you should either:
- Get a `RECOVERED` ntfy push within 5 minutes, or
- Get no push at all (meaning it never saw you as DOWN)

## Troubleshooting quick reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Public URL `520` or `522` | Tunnel down | Restart cloudflared (step 4) |
| Public URL `502` | Local server down, tunnel up | Restart that service (step 2) |
| Public URL `404` but you expected a page | Tunnel routing wrong | Check `~/.cloudflared/config.yml` |
| Stripe checkout won't start | Missing `.env` | `ls ~/behique/tools/stripe-checkout/.env` must exist |
| `python` not found | Wrong shell | You're in cmd/PowerShell, open Git Bash |

## What got you here

Hutia went off when the laptop went off (or lost power). Websites went down with it because Hutia runs all the web servers and the Cloudflare Tunnel that connects them to your domains. Until auto-start is configured, this will happen every time.

See `AUTOSTART.md` for the permanent fix.
