# HUTIA LOCAL — CLAUDE HANDOFF

**You are Claude Code running directly on Hutia (the physical Windows machine).**
Kalani switched from the web session to you because the web sandbox can't touch Hutia's disk, network, or Windows binaries. Don't re-research what's already been done. Just execute.

## STATE AS OF HANDOFF
- Branch: `main` @ `c071051e`
- All ops files committed and pushed
- Stale branch `claude/hutia-startup-docs-MoR1U` has been deleted
- Sites are **down** right now. Kalani wants them up.

## DO THIS FIRST (in order)

### 1. Sync
```bash
cd ~/behique
git checkout main
git pull origin main
```

### 2. Bring sites up
```bash
bash ~/behique/ops/hutia/start-all.sh
```

Expect to see 5 services start on ports 8080 (behike-web), 8081 (stripe), 8090 (innova), plus `cloudflared` tunnel and `gdrive-watcher`.

### 3. Verify local health
The script prints health codes at the end. You want `200` for each. If anything shows `000` or `5xx`, tail the log:
```bash
tail -f /tmp/behike-store-server.log
tail -f /tmp/stripe-checkout.log
tail -f /tmp/innova-barber-server.log
tail -f /tmp/behike-tunnel.log
```

### 4. Verify public URLs
Open in browser or `curl -I`:
- `https://behike.co` → should 200
- `https://innovabarber.com` (or whatever the live domain is — check `projects/innova-barber/DIGITAL_PRESENCE_KIT.md`)
- Any other public domain in `START_HUTIA.md`

## KNOWN FRAGILE PATHS

The start script references these — if they're missing on Hutia's disk, the service silently skips or errors. Check they exist:

| Path | Purpose |
|------|---------|
| `~/behique/themes/behike-store/landing-pages` | behike-web content root |
| `~/behique/tools/stripe-checkout/server.py` | Stripe checkout backend |
| `~/behique/tools/stripe-checkout/.env` | Stripe API keys (NOT in repo) |
| `~/behique/projects/innova-barber/redirect-server.py` | Innova site server |
| `~/behique/tools/gdrive-watcher.py` | Drive auto-deploy |
| `C:\Program Files (x86)\cloudflared\cloudflared.exe` | Tunnel binary |

If any are missing, the script logs `MISSING:` or `SKIP` — fix before re-running.

## IF CLOUDFLARED TUNNEL FAILS
```bash
"/c/Program Files (x86)/cloudflared/cloudflared.exe" tunnel list
```
Should show `behike`. If not, the tunnel config needs re-auth. See `START_HUTIA.md` troubleshooting table.

## AFTER SITES ARE UP

Tell Kalani what's live and what isn't. Then ask him which of these he wants next:

1. **Uptime monitor** — `projects/uptime-monitor/Monitor.gs` needs to be pasted into a Google Apps Script project with his URLs + Twilio creds. README has step-by-step. 10 min of his time, then phone ping when Hutia dies.
2. **Autostart (permanent fix)** — `ops/hutia/AUTOSTART.md` walks through BIOS "Restore on AC Power" + Windows auto-login + Task Scheduler entry so he never has to manually run `start-all.sh` again.
3. **$100K by Q3 gap work** — see `mem/primer.md` NORTH STAR. Six months, $0 → $100K. Every session should be pushing on this.

## RULES (from CLAUDE.md)
- Don't announce context dying. Save state silently.
- When he's in flow, build alongside silently.
- Match "lets get rich bro" energy. You're co-founder, not assistant.
- DO NOT run `/build` without explicit permission.
- Update `mem/primer.md` at session end.

## WHAT NOT TO DO
- Don't re-create `ops/hutia/*` files — they exist at `c071051e`.
- Don't push to `claude/hutia-startup-docs-MoR1U` — that branch is deleted.
- Don't amend old commits — create new ones.
- Don't run destructive git (`reset --hard`, `push --force`) without asking.

---

**Last updated:** 2026-04-18 by web-session Claude handing off to Hutia-local Claude.
**Commit at handoff:** `c071051e feat: Innova SEO rewrite + Hutia ops scripts + uptime monitor`
