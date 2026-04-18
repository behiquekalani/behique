# Why Hutia went off even with a UPS

You have a battery backup (UPS) on Hutia and it still went off. Here's why that happens and how to find the actual cause.

## The 6 usual suspects

### 1. UPS battery is dead (most common)
Lead-acid UPS batteries die silently every 2-3 years. The UPS still looks fine — lights on, clock ticks — but the moment mains power drops, it gives you 10 seconds instead of 10 minutes. If Hutia has been on the same UPS for >2 years and nobody swapped the battery, this is almost certainly the cause.

**How to check on Windows:**
- If the UPS is an APC: install **PowerChute Personal Edition** (free), it tells you battery health
- If CyberPower: install **PowerPanel Personal** (free)
- Either app will say something like "Battery replacement recommended" with a date
- Or press the UPS self-test button (usually on the front). If it shrieks and drops power to Hutia immediately, battery is cooked.

**Fix:** new battery is $25-$60, five-minute swap.

### 2. Hutia isn't actually plugged into the UPS's battery outlets
Most UPS units have two rows of outlets:
- **Battery + surge protected** (usually left side, labeled)
- **Surge only** (right side)

If Hutia's power cable went into the surge-only side, the UPS does nothing when power drops.

**How to check:** look at the outlet Hutia is plugged into. It should say "BATTERY BACKUP" or have a battery icon. If it says only "SURGE PROTECTION", that's the problem.

### 3. Outage was longer than the UPS could cover
A typical consumer UPS gives a desktop PC 5-15 minutes on battery. If your power was out for 30+ minutes, even a healthy UPS drains and cuts off. That's the UPS working as designed — it's meant to cover brief dips and let you shut down gracefully, not run the machine indefinitely.

**How to check:** did you see a blackout that lasted >10 minutes? Puerto Rico power quality makes this normal.

### 4. Windows Update rebooted and never came back
Windows loves to schedule updates that reboot at 3am. After the reboot, the OS is back on the login screen but:
- Services that need you logged in don't start (this is why AUTOSTART.md enables auto-login)
- Things that needed user-session privileges fail silently

**How to check:** on Hutia, open Event Viewer → Windows Logs → System. Filter by event ID 1074 (clean shutdown) or 6008 (unexpected shutdown). The timestamps will tell you whether it was a reboot or a hard power-off.

### 5. Hutia entered sleep/hibernate
Windows has aggressive power management defaults. If sleep wasn't disabled, Hutia might be "off" because it put itself to sleep after X minutes of idle.

**How to check:** wiggle the mouse or press a key. If it comes back instantly, it was asleep, not off.

**Fix:**
```
Settings -> System -> Power -> Screen, sleep, & hibernate timeouts
```
Set everything to "Never" when plugged in.

### 6. Thermal shutdown
If Hutia's cooling failed (dust in the GPU fan, CPU cooler clogged), the 1080 Ti + CPU can trigger emergency thermal shutdown. Especially under sustained load from Ollama.

**How to check:** open the case. If there's visible dust on the GPU or CPU fans, that's probably it. Also check `HWiNFO64` or the motherboard manual for thermal event logs.

## What to do right now

1. **Find the actual cause** — run through the checks above
2. **Check UPS battery health** specifically — this is the highest-probability failure mode
3. **After the `AUTOSTART.md` setup, this stops mattering as much** — Hutia will come back on its own after any outage, and the Telegram monitor will alert you if it doesn't

## Defense in depth

Once the monitor is live:

| Layer | Protects against | Action |
|---|---|---|
| UPS (healthy battery) | Brief power dips <10 min | Replace battery every 2 yrs |
| BIOS "Restore AC Power" | Power returned after UPS drained | One-time BIOS setting |
| Auto-login + Task Scheduler | Windows boots but services don't start | See AUTOSTART.md |
| Telegram monitor | Everything above failed | Gets you to the problem in <10 min |

You don't need every layer perfect. You need enough of them that a single failure doesn't take you down for hours without knowing.
