# Fleet reality — as of 2026-04-21

## THE CHANGE
- **Hutia is retired.** The Windows laptop is out.
- **Naboria is retired.** The old always-on Linux worker is out.
- Only **Cobo** (Windows desktop) and **Ceiba** (Mac) remain.
- When Kalani says "the PC" / "the server" / "this machine" / "I" (in an ops context) he means **Cobo** unless he explicitly says "Ceiba" or "the Mac".

## IMPLICATIONS FOR CURRENT WORK
- `behike.co` is served from Cobo (not Hutia anymore).
- All `ops/hutia/*` docs → **legacy patterns**. Content is still useful (BIOS AC recovery, Task Scheduler, NSSM approach, UPS diagnostic) but the machine name is wrong. Port to `ops/cobo/*` when touched.
- `bios/fleet/NABORIA-INSTRUCTIONS.md` and `deploy_naboria.bat` → historical. Cobo now handles what Naboria did.
- Legal/audit files under `legal/evidence/*` that reference these machines → do NOT rewrite; they're records of a past state.

## RESILIENCE STATE (Cobo)
| Layer | Status |
|---|---|
| UPS (CyberPower / PowerPanel) | Physically connected 2026-04-21. Software config pending. |
| BIOS AC power recovery | Not yet configured. |
| Auto-login to Windows | Status unknown — ask. |
| Services autostart (Task Scheduler or NSSM) | Status unknown — ask. |
| Cloudflare Tunnel | Running (behike.co is live). Investigate whether installed as Windows service or ad-hoc. |
| Telegram uptime monitor | Live (commit 776a287b). |

## OPEN SYNCTHING ISSUES
- macOS metadata pollution (`.DS_Store`, `._*` AppleDouble files) landing on Cobo from Ceiba.
- Occasional sync-conflict files (one already in repo: `CEIBA-BRIEFING.sync-conflict-20260327-130449-3MUX7XC.txt`).
- No `.stignore` exists at repo root.
- Fix: create `.stignore-template` + per-device `.stignore` with strong ignore patterns.

## IMMEDIATE TODO (when Kalani is at Cobo)
1. Configure PowerPanel (low-battery shutdown, self-test, auto-start minimized)
2. BIOS: set AC Power Recovery → Power On / Last State
3. Decide Task Scheduler vs. NSSM for service autostart (recommend NSSM for a desktop kept on 24/7)
4. Create `.stignore` to kill the Finder pollution
5. Clean up existing sync-conflict file(s) from the repo

## PRIMER NOTE
`mem/primer.md` is last-modified 2026-03-31 (pre-launch). Update at next session end.
