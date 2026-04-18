# Behike Uptime Monitor

Google Apps Script that pings your sites every 5 minutes and pushes a Telegram message to your phone the moment anything goes down. Runs on Google's servers, so it keeps working when Hutia, Ceiba, and your laptop are all off.

## Why Telegram

- Free forever, no monthly costs
- You already have the app
- Instant push (phone, desktop, tablet all synced)
- One click to create the bot via @BotFather
- No 3rd-party service that can disappear or rate-limit you

## Setup — 10 minutes

### 1. Create the bot (2 min)

1. Open Telegram, search for **@BotFather**, start a chat
2. Send `/newbot`
3. Give it a name: `Behike Uptime`
4. Give it a username: something unique ending in `bot` like `behike_uptime_kg_bot`
5. BotFather replies with your token: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ...`
6. **Copy that token somewhere safe** — you can't view it again, only regenerate

### 2. Start the bot (30 sec)

- Click the link BotFather gave you, or search for your bot's username
- Click **Start**. This opens the conversation — without this step the bot can't message you

### 3. Get your chat_id (1 min)

- Open this URL in a browser, replacing `<TOKEN>` with the one you copied:
  ```
  https://api.telegram.org/bot<TOKEN>/getUpdates
  ```
- Look for `"chat":{"id":` — the number after that is your `chat_id` (usually a 9-10 digit number)
- If you see `"result":[]` (empty), send a message to the bot in Telegram first, then reload the URL

### 4. Create the Apps Script (2 min)

1. Go to https://script.google.com/ → **New Project**
2. Delete the default code in `Code.gs`
3. Open `Monitor.gs` from this folder, copy the whole file, paste into `Code.gs`
4. In the `CONFIG` block at the top:
   - Set `TELEGRAM_TOKEN` to the bot token
   - Set `TELEGRAM_CHAT_ID` to your chat_id
   - Edit `URLS` if you want to add/remove sites
   - `EMAIL` is optional — set to your email for a fallback channel, or delete the line
5. Save (cmd+S). Give the project a name like "Behike Uptime Monitor"

### 5. Authorize and install the trigger (2 min)

1. In the function dropdown (top toolbar), pick `setup`
2. Click **Run**
3. Google will ask for permissions: approve (needs UrlFetchApp, Mail, Triggers)
4. Check the **Executions** tab — you should see `setup` finished successfully

### 6. Test it (30 sec)

- Pick `testAlert` from the function dropdown, click Run
- Your phone should buzz within 1-3 seconds with `🧪 TEST` from your bot
- If nothing comes through: check the Executions tab for errors. Most common issues are wrong token, wrong chat_id, or you skipped step 2

You're armed. You'll now get a Telegram message within ~5 minutes of any site going down, and another message when it recovers.

## How it behaves

- Checks every 5 minutes
- Retries once after 3 seconds before declaring DOWN (kills false positives from transient blips)
- **Only alerts on state changes**: one DOWN message when a site goes down, one RECOVERED message when it comes back. No repeat spam every 5 minutes while it's down.
- DOWN alerts include the HTTP code or error
- All messages include timestamp in Puerto Rico time

## Ops

- **Change URLs**: edit `CONFIG.URLS` in the script, save. No re-setup needed.
- **Add another Telegram chat** (e.g. a group): send a message in that group tagging your bot, reload the getUpdates URL, grab the new chat_id. You could store them both in an array.
- **Disable monitoring**: run `teardown` from the function dropdown
- **Stuck on DOWN alert**: run `resetState`
- **Check current state**: run `status`, look at the Executions log

## Limits (Google free tier)

Free Apps Script tier: 6 min/execution, 90 min/day of trigger runtime, 20k UrlFetch calls/day. You're using ~864 calls/day with 3 URLs checked every 5 min. Way under.

Telegram Bot API: no practical limit for personal use.

## Extending it later

Want SMS on top of Telegram (for critical alerts when you don't have data)? Add a Twilio block in `notify()` — same pattern as the Telegram and Email blocks. Twilio runs ~$1/year for this volume if you want it later.

## Why not iMessage?

Apple doesn't offer an iMessage API. Every "iMessage automation" solution requires a Mac running 24/7 as a relay, which defeats the whole point of monitoring your servers — if the Mac that sends the alerts goes down, the alerts stop. Telegram doesn't have that problem.
