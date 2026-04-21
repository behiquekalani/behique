# PowerPanel config — Cobo UPS hardening

Goal: when mains power drops, Cobo rides the UPS for as long as possible, then shuts down *cleanly* before the battery dies (file corruption risk otherwise). When power returns, BIOS AC-recovery boots Cobo back up → autostart brings services back → Telegram monitor confirms.

PowerPanel is only one layer of that. Configure it right and pair with BIOS AC recovery (see FLEET_REALITY.md).

**Edition check first:** Open PowerPanel → About. You're probably on **Personal** (free, for single UPS on single PC). If it's **Business**, settings have more depth (SNMP, network shutdown) but the core flow below is the same.

---

## Settings to flip (Personal Edition — most common)

Open PowerPanel → left sidebar.

### 1. Preferences
- **Run PowerPanel at Windows startup:** ✅ ON (non-negotiable — otherwise it won't be monitoring)
- **Start minimized:** ✅ ON (no popup window stealing focus on boot)
- **Notification area icon:** ✅ ON (quick visual check)

### 2. Configuration → Shutdown
Pick the policy:
- **Action when utility power fails:** `Shutdown` (not Hibernate — Hibernate is slower and can hang)
- **Delay before shutdown:**
  - If UPS runtime is >10 min → `Start shutdown when battery capacity is below 30%`
  - If UPS runtime is <10 min → `Start shutdown 60 seconds after power fail` (don't wait for % — small UPS drains fast)
- **OS shutdown time needed:** `2 minutes` (Windows needs ~90 sec to shut down cleanly; leave buffer)
- **Shutdown file (optional):** leave empty unless you want to run a pre-shutdown script (e.g., `C:\behique\pre-shutdown.bat` that gracefully stops services — nice-to-have, not required)

### 3. Configuration → Diagnostic / Self Test
- **Self-test schedule:** `Every 2 weeks` (runs a ~10 sec battery load test; catches dead cells before you need the battery)
- **Alert on self-test failure:** ✅ ON (logs an event; you'll know the battery is dying before it matters)

### 4. Configuration → Notification
- **On utility power fail:** log + balloon notification ✅
- **On battery low:** log + balloon + **sound** ✅
- **On self-test failure:** log + balloon ✅
- **Email notification:** optional. If you configure it, use a dedicated alerts@behike.co or a throwaway. Not critical because Telegram monitor will catch the site going down anyway.

### 5. View → Event Log path
- Write down where the log file lives (default: `C:\Program Files\CyberPower PowerPanel Personal Edition\log\event.log` or similar)
- Useful later when diagnosing "why did Cobo shut down at 3am"

### 6. Battery info tab
Check ONCE and write down:
- **Battery capacity %** (should be >95% if battery is healthy)
- **Estimated runtime at current load** (gives you a real number — e.g. "7 minutes at 180W")
- **Battery replacement date** (manufactured date + 3 years is the usual rule)

If battery health is <80% or runtime is <3 min, **the UPS won't save you in a real outage** — order a replacement battery now ($25-60 on Amazon, 5-min swap).

---

## Quick sanity test (5 min, do it NOW)

1. Save any open work.
2. Unplug the UPS from the wall outlet.
3. Watch PowerPanel — it should immediately show "On Battery", log an event, and start counting down.
4. Plug the UPS back in within 30 sec.
5. PowerPanel should log "Utility Power Restored" and switch back to line power.

If step 3 doesn't happen (no event, no icon change), **Cobo is plugged into the SURGE-ONLY outlets on the UPS, not the BATTERY BACKUP outlets**. Most CyberPower units have two rows — half are battery-protected, half are surge-only. Fix: move the plug to the left-side (battery) row.

---

## What this does NOT cover
- **BIOS AC recovery** — separate step, in BIOS. Set it or Cobo won't boot after UPS drains.
- **Service autostart** — separate step (Task Scheduler or NSSM). PowerPanel only handles the shutdown side; autostart handles the recovery side.
- **Dead battery** — PowerPanel will tell you when the battery fails, but it won't fix it. Budget ~$40 every 2-3 years.

See `ops/cobo/FLEET_REALITY.md` for the full resilience stack and what's still pending.
