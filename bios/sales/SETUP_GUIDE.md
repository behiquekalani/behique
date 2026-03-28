# Gumroad Webhook Setup Guide

## 1. Get a Telegram Bot Token

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, follow the prompts
3. Copy the bot token (looks like `123456:ABC-DEF...`)
4. Send a message to your new bot (this initializes the chat)
5. Get your chat ID: visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser. Find `"chat":{"id":123456789}` in the response. That number is your chat ID.

## 2. Set Environment Variables

Add to your shell profile (`~/.zshrc`):

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token-here"
export TELEGRAM_CHAT_ID="your-chat-id-here"
export GUMROAD_WEBHOOK_SECRET="pick-a-random-string"  # optional
```

Then reload: `source ~/.zshrc`

## 3. Install Dependencies

```bash
pip3 install fastapi uvicorn
```

## 4. Run the Server

```bash
cd ~/behique/bios/sales
python3 webhook_server.py
```

Server starts on port 8097. Check health at `http://localhost:8097/webhook/status`.

Interactive docs at `http://localhost:8097/docs`.

## 5. Expose the Server (for Gumroad to reach it)

### Option A: ngrok (quick testing)

```bash
ngrok http 8097
```

Copy the `https://xxxx.ngrok.io` URL.

Your webhook URL: `https://xxxx.ngrok.io/webhook/gumroad`

### Option B: Cloudflare Tunnel (production)

```bash
cloudflared tunnel --url http://localhost:8097
```

Or set up a named tunnel for a permanent URL.

### Option C: Deploy to Railway/Fly.io

For always-on, deploy the server to Railway or Fly.io and use that URL.

## 6. Configure Gumroad Webhook

1. Go to [Gumroad Settings](https://app.gumroad.com/settings/advanced)
2. Scroll to "Ping" section
3. Paste your webhook URL: `https://your-domain/webhook/gumroad`
4. Click "Update"
5. Gumroad sends a test ping immediately. Check your server logs.

## 7. Test Locally

```bash
# Test the notifier
python3 notifier.py test "Webhook system is live"

# Simulate a Gumroad webhook
curl -X POST http://localhost:8097/webhook/gumroad \
  -H "Content-Type: application/json" \
  -d '{
    "seller_id": "test-seller",
    "product_id": "test-product",
    "product_name": "Behike OS",
    "price": "97.00",
    "email": "buyer@example.com",
    "sale_timestamp": "2026-03-23T12:00:00Z"
  }'

# Check recent sales
curl http://localhost:8097/webhook/recent
```

## 8. Set Up Daily Digest (cron)

```bash
crontab -e
```

Add this line (runs at 9 PM daily):

```
0 21 * * * cd /Users/kalani/behique/bios/sales && /usr/bin/python3 daily_digest.py >> /Users/kalani/behique/bios/logs/digest.log 2>&1
```

Test it first:

```bash
python3 daily_digest.py --dry-run
```

## File Structure

```
bios/sales/
  webhook_server.py   - FastAPI server (port 8097)
  notifier.py         - Telegram notification helper
  daily_digest.py     - Cron job for daily summary
  SETUP_GUIDE.md      - This file
  webhooks/           - Raw webhook payloads (auto-created)
    raw-20260323-120000-000000.json
```

## Troubleshooting

**No Telegram messages?**
- Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
- Make sure you sent at least one message to the bot first
- Test with `python3 notifier.py test "hello"`

**Gumroad not reaching server?**
- Make sure ngrok/cloudflared is running
- Check the URL ends with `/webhook/gumroad`
- Look at server logs for incoming requests

**Price shows wrong?**
- Gumroad can send price as cents ("9700") or formatted ("$97.00")
- The server handles both formats automatically
