# BIOS API Keys and Accounts Setup

Every API key and token the BIOS system needs, with exact steps to get each one.

---

## 1. Telegram Bot Token + Chat ID

**What it does:** Sends all BIOS notifications (sales, signals, system alerts, content reminders).

**How to get it:**

1. Open Telegram, search for `@BotFather`, start a chat
2. Send `/newbot`
3. Follow the prompts to name your bot
4. BotFather gives you a token like `7123456789:AAH1bGc_xKz2...`
5. Copy that token

For the chat ID:
1. Send any message to your new bot in Telegram
2. Open a browser and go to: `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
3. Find `"chat": {"id": 123456789}` in the response
4. That number is your chat ID

**Where to put it:**
```
TELEGRAM_BOT_TOKEN="your-token"
TELEGRAM_CHAT_ID="your-chat-id"
```

**Full guide:** See `TELEGRAM_SETUP.md` in this folder.

---

## 2. Gumroad Access Token

**What it does:** Pulls sales data, product listings, and revenue numbers from your Gumroad store.

**How to get it:**

1. Go to https://app.gumroad.com/settings/advanced
2. Scroll down to "Applications"
3. Click "Create application"
4. Fill in:
   - Application name: `BIOS`
   - Redirect URI: `http://localhost` (does not matter for personal use)
5. Click "Create"
6. You will see a "Application Secret" field. That is your access token.

Alternative (personal token, simpler):
1. Go to https://app.gumroad.com/settings/advanced
2. Under "Access Token", click "Generate Token" or "Create"
3. Copy the token shown

**Where to put it:**
```
GUMROAD_ACCESS_TOKEN="your-token"
```

**API docs:** https://app.gumroad.com/api

---

## 3. Beehiiv API Key

**What it does:** Manages email subscribers, sends newsletters, pulls analytics.

**How to get it:**

1. Go to https://app.beehiiv.com
2. Log in to your publication
3. Click "Settings" in the left sidebar
4. Click "Integrations"
5. Scroll to "API" section
6. Click "API Keys" or "Manage API Keys"
7. Click "Create New API Key"
8. Give it a name: `BIOS`
9. Set permissions: Read + Write (or Full Access)
10. Click "Create"
11. Copy the key immediately. It will not be shown again.

You also need your **Publication ID**:
1. In the same Settings page, look for "Publication ID"
2. Or go to Settings > General. The publication ID is displayed there.

**Where to put it:**
```
BEEHIIV_API_KEY="your-api-key"
BEEHIIV_PUBLICATION_ID="your-pub-id"
```

**API docs:** https://developers.beehiiv.com

---

## 4. Spotify Client ID + Secret

**What it does:** Pulls podcast analytics, episode data, and listener stats (if running a podcast through Spotify).

**How to get it:**

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in:
   - App name: `BIOS`
   - App description: `Personal analytics`
   - Redirect URI: `http://localhost:8888/callback`
   - Check "Web API" under "Which API/SDKs are you planning to use?"
5. Click "Save"
6. You are now on your app's dashboard
7. Click "Settings" (top right)
8. You will see:
   - **Client ID** -- visible on the page
   - **Client Secret** -- click "View client secret" to reveal it
9. Copy both values

**Where to put it:**
```
SPOTIFY_CLIENT_ID="your-client-id"
SPOTIFY_CLIENT_SECRET="your-client-secret"
```

**API docs:** https://developer.spotify.com/documentation/web-api

---

## 5. Instagram Graph API

**What it does:** Pulls post analytics, follower counts, engagement data from your Instagram business/creator account.

**How to get it:**

This one has more steps because Instagram's API goes through Meta (Facebook).

1. Go to https://developers.facebook.com
2. Log in with the Facebook account linked to your Instagram
3. Click "My Apps" (top right), then "Create App"
4. Select "Business" as the app type, click "Next"
5. Fill in:
   - App name: `BIOS`
   - App contact email: your email
6. Click "Create App"
7. On the dashboard, find "Instagram Graph API" and click "Set Up"
8. In the left sidebar, go to "Instagram Graph API" > "Generate Token"
   - Select the Instagram account you want to connect
   - Grant all requested permissions
9. Copy the generated token

For a long-lived token (lasts 60 days instead of 1 hour):
1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Click "Generate Access Token"
4. Go to https://developers.facebook.com/tools/debug/accesstoken/
5. Paste your token, click "Debug"
6. Click "Extend Access Token" at the bottom
7. Copy the new long-lived token

You also need your **Instagram Business Account ID**:
1. In the Graph API Explorer (https://developers.facebook.com/tools/explorer/)
2. Run this query: `me/accounts`
3. Find your Facebook Page, copy its ID
4. Run: `YOUR_PAGE_ID?fields=instagram_business_account`
5. The returned ID is your Instagram Business Account ID

**Where to put it:**
```
INSTAGRAM_ACCESS_TOKEN="your-long-lived-token"
INSTAGRAM_BUSINESS_ACCOUNT_ID="your-account-id"
```

**Important:** Long-lived tokens expire after 60 days. You will need to refresh them. BIOS should handle this automatically once set up.

**API docs:** https://developers.facebook.com/docs/instagram-api

---

## 6. YouTube Data API

**What it does:** Pulls channel stats, video analytics, subscriber counts.

**How to get it:**

1. Go to https://console.cloud.google.com
2. Log in with your Google account
3. Click the project dropdown at the top, then "New Project"
4. Name it `BIOS`, click "Create"
5. Make sure the new project is selected in the dropdown
6. Go to "APIs & Services" > "Library" (left sidebar)
   - Or go directly to: https://console.cloud.google.com/apis/library
7. Search for "YouTube Data API v3"
8. Click on it, then click "Enable"
9. Go to "APIs & Services" > "Credentials" (left sidebar)
   - Or: https://console.cloud.google.com/apis/credentials
10. Click "Create Credentials" > "API Key"
11. A popup shows your new API key. Copy it.
12. Click "Restrict Key" (recommended):
    - Under "API restrictions", select "Restrict key"
    - Choose "YouTube Data API v3" from the dropdown
    - Click "Save"

For your **Channel ID**:
1. Go to https://www.youtube.com and log in
2. Click your profile picture > "Your channel"
3. Look at the URL. It will be either:
   - `youtube.com/channel/UC1234abcd` -- the UC... part is your channel ID
   - `youtube.com/@yourhandle` -- if it shows a handle, go to "About" and look for the channel ID, or use the API: `https://www.googleapis.com/youtube/v3/channels?part=id&forHandle=@yourhandle&key=YOUR_API_KEY`

**Where to put it:**
```
YOUTUBE_API_KEY="your-api-key"
YOUTUBE_CHANNEL_ID="your-channel-id"
```

**API docs:** https://developers.google.com/youtube/v3

---

## Summary: All Environment Variables

```bash
# Telegram
TELEGRAM_BOT_TOKEN=""
TELEGRAM_CHAT_ID=""

# Gumroad
GUMROAD_ACCESS_TOKEN=""

# Beehiiv
BEEHIIV_API_KEY=""
BEEHIIV_PUBLICATION_ID=""

# Spotify
SPOTIFY_CLIENT_ID=""
SPOTIFY_CLIENT_SECRET=""

# Instagram
INSTAGRAM_ACCESS_TOKEN=""
INSTAGRAM_BUSINESS_ACCOUNT_ID=""

# YouTube
YOUTUBE_API_KEY=""
YOUTUBE_CHANNEL_ID=""
```

Store these in `~/behique/.env.telegram` (or a unified `~/behique/.env.bios` file) and make sure it is in `.gitignore` so credentials never get committed.
