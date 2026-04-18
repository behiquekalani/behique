# Make Hutia auto-start services on boot

The permanent fix for "laptop off → Hutia off → sites down" is making Hutia come back up on its own whenever it boots. Two pieces:

1. Hutia must **boot automatically** when power returns (BIOS setting)
2. All services must **start automatically** when Windows logs in (Task Scheduler)

Do both. Takes about 10 minutes.

---

## Part 1: BIOS — boot on power restore

If power goes out, you want Hutia to come back on by itself. This is a motherboard setting.

1. Reboot Hutia, tap `Del` or `F2` repeatedly during POST to enter BIOS
2. Find **Power Management** / **AC Power Recovery** / **Restore AC Power Loss** (wording varies by motherboard)
3. Set to **Power On** or **Last State**
4. Save and exit (usually F10)

Now if power drops and comes back, Hutia boots by itself.

## Part 2: Auto-login to Windows

Task Scheduler can run things on boot, but services that bind to ports reliably want a real user session. Enable auto-login:

1. `Win + R` → type `netplwiz` → Enter
2. Uncheck **Users must enter a user name and password to use this computer**
3. Apply, enter your password twice to confirm
4. OK

Reboot to test — it should log in without you touching it.

## Part 3: Task Scheduler — run start-all.sh on login

1. Open **Task Scheduler** (Win + S, search "Task Scheduler")
2. Right panel → **Create Task** (not "Create Basic Task" — we need the advanced version)
3. **General tab:**
   - Name: `Behike Services`
   - Description: `Starts Behike web servers + Cloudflare Tunnel on login`
   - Check **Run only when user is logged on**
   - Check **Run with highest privileges**
4. **Triggers tab** → New:
   - Begin the task: **At log on**
   - Specific user: your user
   - Delay task for: **30 seconds** (gives network time to come up)
   - OK
5. **Actions tab** → New:
   - Action: **Start a program**
   - Program/script: `C:\Program Files\Git\bin\bash.exe`
     (adjust if Git is installed elsewhere — find it with `where bash` in Git Bash)
   - Add arguments: `-l -c "~/behique/ops/hutia/start-all.sh"`
   - Start in: `C:\Users\Kalan`  (your Windows home)
   - OK
6. **Conditions tab:**
   - Uncheck **Start the task only if the computer is on AC power** (desktops only — doesn't matter, but uncheck it)
7. **Settings tab:**
   - Check **Allow task to be run on demand**
   - Check **If the task fails, restart every:** → 1 minute, up to 3 times
8. OK. Enter password if prompted.

## Part 4: Test it

1. Right-click the `Behike Services` task → **Run**
2. After ~30 seconds, check from Ceiba or your phone:
   ```
   curl -I https://behike.co/
   curl -I https://innovabarberpr.shop/
   ```
   Both should return 200.
3. Full cycle test: reboot Hutia. Don't touch anything. Wait 2 minutes. Check the same URLs from your phone. If they load, you're done.

## Part 5: Confirm with the uptime monitor

After you've set up `projects/uptime-monitor/Monitor.gs`, you'll get a `RECOVERED` ntfy push every time Hutia boots and services come back. That's your proof auto-start is working.

## Troubleshooting

**Task ran but nothing's listening**
- Open Task Scheduler → History tab for the task → look for exit codes
- Run the script manually in Git Bash first (`bash ~/behique/ops/hutia/start-all.sh`). If it works manually but not from Task Scheduler, it's almost always a PATH issue — bash needs `-l` to load your login profile (already set above).

**`bash.exe` not found**
- In Git Bash: `where bash` → copy that path into the Action's Program/script field

**Cloudflare tunnel doesn't come up on boot**
- The tunnel can race network init. The 30-second delay in the trigger usually fixes it. If not, bump it to 60 seconds.
- Alternative: install cloudflared as a Windows service:
  ```
  cloudflared.exe service install
  ```
  Then it's managed by Windows independently of the Task Scheduler entry.

## Alternative: use NSSM to make each service a Windows service

If Task Scheduler keeps being flaky, use [NSSM](https://nssm.cc/) to register each Python server + cloudflared as a proper Windows service. More reliable, a bit more setup. Only worth it if Task Scheduler keeps giving you trouble.
