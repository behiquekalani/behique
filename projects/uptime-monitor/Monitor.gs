/**
 * Behike Uptime Monitor — Google Apps Script
 *
 * Pings every URL in CONFIG.URLS every 5 minutes. Sends a Telegram message
 * to Kalani's phone ONLY on state changes (UP -> DOWN, or DOWN -> UP).
 *
 * Runs on Google's infrastructure. Works even when Ceiba, Hutia, and the
 * laptop are all off.
 *
 * SETUP (10 min total):
 *  1. Create a Telegram bot:
 *     - In Telegram, open a chat with @BotFather
 *     - Send /newbot
 *     - Pick a name: "Behike Uptime"
 *     - Pick a username: something like behike_uptime_bot
 *     - Copy the token it gives you (looks like 1234567890:ABCdefGHI...)
 *  2. Start a chat with your new bot (search its username, click Start).
 *     This is required — bots can't DM you until you DM them first.
 *  3. Get your chat_id:
 *     - Open in a browser: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
 *     - Find "chat":{"id":XXXXXXXX — that number is your chat_id
 *  4. Go to https://script.google.com/ -> New Project
 *  5. Paste this whole file into Code.gs. Save.
 *  6. Fill in CONFIG.TELEGRAM_TOKEN and CONFIG.TELEGRAM_CHAT_ID below.
 *  7. Run setup() once manually. Approve permissions when prompted.
 *  8. Run testAlert() — your phone should buzz with a test message in <5s.
 *
 * Ops:
 *  - View logs: script editor -> Executions tab
 *  - Change URLs: edit CONFIG.URLS, save. No re-setup needed.
 *  - Disable monitoring: run teardown()
 *  - Clear stuck state: run resetState()
 */

const CONFIG = {
  // Sites to monitor. Add/remove freely.
  URLS: [
    'https://behike.co/',
    'https://innovabarberpr.shop/',
    'https://checkout.behike.co/health',
  ],

  // Telegram bot credentials. Get both from the setup steps above.
  TELEGRAM_TOKEN: 'PASTE_BOT_TOKEN_HERE',
  TELEGRAM_CHAT_ID: 'PASTE_CHAT_ID_HERE',

  // Optional: email fallback. Comment out EMAIL to skip.
  EMAIL: 'kalani@behike.co',

  // Behavior
  REQUEST_TIMEOUT_SEC: 15,
  RETRY_ON_FAIL: true,        // one retry before declaring DOWN (kills transient blips)
  RETRY_DELAY_MS: 3000,
  DOWN_THRESHOLD: 1,          // consecutive failures before alerting (1 = alert on first confirmed down)
};

// ============ DO NOT EDIT BELOW ============

const PROPS = PropertiesService.getScriptProperties();

function runCheck() {
  const results = CONFIG.URLS.map(checkOne);
  results.forEach(handleResult);
  PROPS.setProperty('last_run_iso', new Date().toISOString());
}

function checkOne(url) {
  const attempt = () => {
    const t0 = Date.now();
    try {
      const res = UrlFetchApp.fetch(url, {
        muteHttpExceptions: true,
        followRedirects: true,
        validateHttpsCertificates: true,
        method: 'get',
        headers: { 'User-Agent': 'BehikeUptimeMonitor/1.0' },
      });
      const code = res.getResponseCode();
      return { url, code, ms: Date.now() - t0, ok: code >= 200 && code < 400, err: null };
    } catch (e) {
      return { url, code: 0, ms: Date.now() - t0, ok: false, err: String(e) };
    }
  };
  let r = attempt();
  if (!r.ok && CONFIG.RETRY_ON_FAIL) {
    Utilities.sleep(CONFIG.RETRY_DELAY_MS);
    r = attempt();
  }
  return r;
}

function handleResult(r) {
  const key = 'state__' + r.url;
  const fails_key = 'fails__' + r.url;
  const prev = PROPS.getProperty(key) || 'UP';

  if (r.ok) {
    PROPS.setProperty(fails_key, '0');
    if (prev === 'DOWN') {
      PROPS.setProperty(key, 'UP');
      notify(
        '✅ RECOVERED',
        `<b>${escapeHtml(r.url)}</b>\nBack online • HTTP ${r.code} • ${r.ms}ms`
      );
    } else {
      PROPS.setProperty(key, 'UP');
    }
    return;
  }

  const fails = parseInt(PROPS.getProperty(fails_key) || '0', 10) + 1;
  PROPS.setProperty(fails_key, String(fails));

  if (fails >= CONFIG.DOWN_THRESHOLD && prev !== 'DOWN') {
    PROPS.setProperty(key, 'DOWN');
    const detail = r.err ? `ERROR: ${escapeHtml(r.err)}` : `HTTP ${r.code}`;
    notify(
      '🚨 SITE DOWN',
      `<b>${escapeHtml(r.url)}</b>\n${detail}\nConfirmed after ${fails} failed check(s).`
    );
  }
}

function notify(title, body) {
  const msg = `${title}\n\n${body}\n\n<i>${new Date().toLocaleString('en-US', { timeZone: 'America/Puerto_Rico' })} AST</i>`;

  // 1. Telegram (primary channel)
  try {
    const tgUrl = `https://api.telegram.org/bot${CONFIG.TELEGRAM_TOKEN}/sendMessage`;
    const resp = UrlFetchApp.fetch(tgUrl, {
      method: 'post',
      contentType: 'application/json',
      muteHttpExceptions: true,
      payload: JSON.stringify({
        chat_id: CONFIG.TELEGRAM_CHAT_ID,
        text: msg,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
      }),
    });
    if (resp.getResponseCode() !== 200) {
      console.error('Telegram error:', resp.getResponseCode(), resp.getContentText());
    }
  } catch (e) {
    console.error('Telegram send failed:', e);
  }

  // 2. Email fallback (also useful paper trail)
  if (CONFIG.EMAIL) {
    try {
      MailApp.sendEmail({
        to: CONFIG.EMAIL,
        subject: '[Behike Uptime] ' + title.replace(/[^\w\s]/g, '').trim(),
        body: stripHtml(msg),
      });
    } catch (e) {
      console.error('Email send failed:', e);
    }
  }

  console.log(title + ' — ' + stripHtml(body));
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function stripHtml(s) { return String(s).replace(/<[^>]+>/g, ''); }

// ============ SETUP / TEARDOWN / TEST ============

function setup() {
  if (CONFIG.TELEGRAM_TOKEN.indexOf('PASTE') === 0 || CONFIG.TELEGRAM_CHAT_ID.indexOf('PASTE') === 0) {
    throw new Error('Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in CONFIG before running setup().');
  }
  teardown();
  ScriptApp.newTrigger('runCheck').timeBased().everyMinutes(5).create();
  console.log('Trigger installed: runCheck every 5 min.');
  runCheck();
}

function teardown() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'runCheck') ScriptApp.deleteTrigger(t);
  });
  console.log('Triggers removed.');
}

function testAlert() {
  notify('🧪 TEST', 'If you see this on your phone, Telegram alerts work. Monitor is armed.');
}

function resetState() {
  const p = PROPS.getProperties();
  Object.keys(p).forEach(k => {
    if (k.startsWith('state__') || k.startsWith('fails__')) PROPS.deleteProperty(k);
  });
  console.log('State cleared.');
}

function status() {
  const p = PROPS.getProperties();
  console.log('Last run: ' + (p.last_run_iso || 'never'));
  Object.keys(p).filter(k => k.startsWith('state__')).forEach(k => {
    const url = k.replace('state__', '');
    console.log(`  ${p[k]}  ${url}  (fails: ${p['fails__' + url] || '0'})`);
  });
}
