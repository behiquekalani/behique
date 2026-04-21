# UPS monitor for Cobo

Free replacement for PowerPanel Business. Shows charge %, runtime remaining, battery health, and online/on-battery status. Logs every poll to CSV.

Uses the Windows `Win32_Battery` WMI class, which is populated automatically when the UPS is connected via USB as a HID Power Device. **No installs.** Pure Python stdlib + a PowerShell subprocess call.

## Run

```
cd ~/behique/tools/ups-monitor
python ups_monitor.py
```

Open http://localhost:9100

Stop with Ctrl+C.

## What you see

- **Status** — "On AC Power" / "Discharging (On Battery)" / "Charging" / "Low" / "Critical"
- **Charge** — % of battery remaining
- **Runtime remaining** — minutes at current load (only meaningful when on battery)
- **Battery health** — `FullChargeCapacity / DesignCapacity × 100`
  - 100% = brand new
  - 80-99% = normal aging, fine
  - 60-79% = battery is wearing out, plan replacement
  - <60% = **order a new battery now**
- **Full / Design capacity** — raw mWh numbers, sanity-check

## Logs

Every 5-second poll appends a row to `logs/ups-YYYY-MM-DD.csv`:
```
timestamp, charge_pct, runtime_min, status_code, status_text, health_pct, full_capacity_mwh, design_capacity_mwh
```

Pull these into a spreadsheet or feed them anywhere you want (e.g., future BIOS dashboard).

## Troubleshooting

**"No battery/UPS detected via WMI"**
- UPS is not connected via USB (it's plugged in for power only). Plug the USB data cable from the back of the UPS into Cobo.
- Windows sometimes needs a minute after USB connect to enumerate the UPS as a HID Power Device. Wait 60s and reload.

**Values show but `design_capacity_mwh` or `full_capacity_mwh` is 0 / null**
- Some UPSes don't report design capacity over HID. Health % will be unavailable, but charge % and runtime still work. Fallback: watch runtime-at-idle trend over weeks. If your UPS used to show "15 min at idle" and now shows "4 min", the battery is dying.

**Dashboard loads but says "Dashboard can't reach the poller"**
- The script crashed or the port is in use. Check the terminal where you ran it.

## Autostart (when you set up the Cobo autostart chain)

Add this line to `ops/cobo/start-all.sh` (when that file exists) or to a new Windows service via NSSM:

```
python ~/behique/tools/ups-monitor/ups_monitor.py
```

Port 9100 is local-only (127.0.0.1) — not exposed externally. Safe.

## Future (if you want)
- Telegram alert when `BatteryStatus` flips to 1 (on battery) — reuse the uptime monitor's bot token.
- Telegram alert when `health_pct` drops below 80%.
- 7-day sparkline chart on the dashboard (history buffer is already in the JSON API response).
