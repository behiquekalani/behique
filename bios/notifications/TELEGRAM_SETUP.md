# Telegram Bot Setup Guide for BIOS

This guide walks through creating a Telegram bot, getting your chat ID, and testing the connection.

---

## Step 1: Create a Bot via @BotFather

1. Open Telegram and search for `@BotFather`
2. Start a chat and send exactly:
   ```
   /newbot
   ```
3. BotFather asks: "Alright, a new bot. How are we going to call it?"
   - Send a display name, e.g.: `BIOS Alerts`
4. BotFather asks: "Good. Now let's choose a username for your bot."
   - Send a username ending in `bot`, e.g.: `behike_bios_bot`
   - If taken, try variations like `behike_alerts_bot`
5. BotFather replies with your **bot token**. It looks like this:
   ```
   7123456789:AAH1bGc_xKz2mW9qPvR4sT5uV6wX8yZ0aBC
   ```
6. Copy that token. You will need it in Step 3.

Optional but recommended. Send these commands to BotFather:
```
/setdescription
```
Then select your bot and send: `BIOS notification system for Kalani`

```
/setuserpic
```
Then select your bot and upload an icon if you want one.

---

## Step 2: Get Your Chat ID

1. Open Telegram and search for the bot username you just created (e.g. `@behike_bios_bot`)
2. Press "Start" or send any message to the bot, e.g.:
   ```
   hello
   ```
3. Open a terminal and run this command (replace YOUR_TOKEN with the token from Step 1):
   ```bash
   curl -s "https://api.telegram.org/botYOUR_TOKEN/getUpdates" | python3 -m json.tool
   ```
4. Look for `"chat"` in the JSON output. Your chat ID is the `"id"` field:
   ```json
   "chat": {
     "id": 123456789,
     "first_name": "Kalani",
     "type": "private"
   }
   ```
5. Copy that number. That is your `TELEGRAM_CHAT_ID`.

If the response is `{"ok":true,"result":[]}` (empty), it means no messages have been sent to the bot yet. Go back to Telegram, send a message to the bot, then run the curl command again.

---

## Step 3: Configure Environment

Option A -- Environment variables (recommended for production):
```bash
export TELEGRAM_BOT_TOKEN="7123456789:AAH1bGc_xKz2mW9qPvR4sT5uV6wX8yZ0aBC"
export TELEGRAM_CHAT_ID="123456789"
```

Option B -- .env.telegram file (used by the test script):
```bash
cp ~/behique/.env.telegram.template ~/behique/.env.telegram
```
Then edit `~/behique/.env.telegram` and paste your real token and chat ID.

---

## Step 4: Test It

Run the test script:
```bash
python3 ~/behique/bios/notifications/test_telegram.py
```

Or run the full bot test suite:
```bash
python3 ~/behique/bios/notifications/telegram_bot.py test
```

You should receive a message in Telegram within a few seconds.

---

## Troubleshooting

**"TELEGRAM_BOT_TOKEN is not set"**
- Make sure you exported the variable or created the .env.telegram file

**Empty getUpdates response**
- Send a message to your bot first, then try again

**"Unauthorized" error**
- Double-check your token. Copy it again from BotFather (`/mybots` then select your bot, then "API Token")

**"Chat not found" error**
- Make sure you sent a message to the bot before trying to send to it
- Verify the chat ID is correct (run the getUpdates curl command again)

**Rate limiting (429 error)**
- Telegram limits bots to ~30 messages per second. The BIOS bot has built-in rate limiting (20 messages per 60 seconds). If you hit this, just wait a minute.
