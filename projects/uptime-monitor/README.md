# Behike Uptime Monitor

Google Apps Script that pings your sites every 5 minutes and pushes a notification to your iPhone via **ntfy.sh** (free, no account) the second something goes down. Runs on Google's servers, so it keeps working even when Hutia, Ceiba, and your laptop are all off.

## Why ntfy.sh

- Free, no account, no API key
- Open-source iPhone app
- Push shows up like any iOS notification
- Works over wifi + cellular
- Topic-based: anyone who knows your topic string can push to you, so **pick something un-guessable**

If you don't want ntfy, the script also emails you as a fallback.

## One-time setup

### 1. Install ntfy on iPhone
- App Store: search **ntfy** (the one by Philipp Heckel, it's free)
- Open it, tap **+** (add subscription)
- Enter a random private topic, e.g. `behike-alerts-8f9k2q`
- Tap Subscribe. Allow notifications.

### 2. Create the Apps Script
- Go to https://script.google.com/ and click **New Project**
- Delete the default `Code.gs` content
- Open `Monitor.gs` in this folder, copy the whole file, paste into `Code.gs`
- Hit **Save** (cmd+S)

### 3. Configure
At the top of the script, in the `CONFIG` block:
- Set `NTFY_TOPIC` to the topic you picked in step 1
- Set `ALERT_EMAIL` to your email
- Edit `URLS` if you want to add/remove sites

### 4. Authorize and install the trigger
- In the function dropdown (top toolbar), pick `setup`
- Click **Run**
- Google asks for permissions: approve (needs UrlFetchApp + Mail + Triggers)
- Check the Executions tab, you should see `setup` complete

### 5. Test it
- Pick `testAlert` from the dropdown, click Run
- Your phone should buzz within 1-3 seconds with `[Behike Uptime] TEST`
- If it doesn't: open the ntfy app, tap the topic, pull to refresh. If the test message is there but didn't push, check iOS Settings -> Notifications -> ntfy -> allow

### 6. Force a real alert (optional)
- Add `https://this-does-not-exist.behike.co/` to `URLS`
- Save. Pick `runCheck`, click Run.
- You should get a `DOWN` push within a few seconds.
- Remove the fake URL and hit `resetState` + run `runCheck` again to clear.

## How it behaves

- Checks every 5 min
- Retries each URL once after 3 seconds before declaring DOWN (kills false positives from transient blips)
- **Only alerts on state changes**: one DOWN push when it goes down, one RECOVERED push when it comes back. Doesn't spam you every 5 min.
- DOWN pushes are marked `urgent` priority (bypasses iPhone focus/DND if you allow critical ntfy notifications)
- RECOVERED pushes are `default` priority

## Ops

- **Change URLs**: edit `CONFIG.URLS`, save. No re-setup needed.
- **Add an ntfy subscriber on Mac**: go to ntfy.sh/YOUR_TOPIC in a browser and leave the tab open, or use the desktop app. Useful as a backup display.
- **Disable**: pick `teardown` from the dropdown, run.
- **Reset state** (stop waiting on a stuck alert): run `resetState`.
- **Check state**: run `status`, look at the Executions log.
- **Execution history**: Apps Script editor -> Executions tab, filter by `runCheck`.

## Limits (Google free tier)

Apps Script free tier: 6 min/execution max, 90 min/day trigger time, 20k UrlFetch calls/day. You're using about 864 UrlFetch/day (3 URLs * 288 five-min intervals) plus retries. Way under.

## Adding more alert channels later

If you want SMS (via Twilio), Slack, Discord, Telegram, just add another `try` block in `notify()`. The ntfy + email pattern shows the shape.

## One more option: skip the script

If you want zero-maintenance and don't need the ntfy flow, **UptimeRobot** has a free tier (50 monitors, 5-min checks, push + SMS alerts). Sign up at uptimerobot.com, add your URLs, done. This script gives you more control and no account dependency — pick whichever fits.
