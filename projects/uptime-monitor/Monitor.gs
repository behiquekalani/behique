/**
 * Behike Uptime Monitor — Google Apps Script
 * Runs every 5 min. Pings each URL, retries once on failure, and alerts to your
 * iPhone via ntfy.sh + email ONLY on state changes (UP -> DOWN, or DOWN -> UP).
 *
 * SETUP (5 min total):
 *  1. Install the "ntfy" app on iPhone from the App Store (free).
 *  2. Open the app, tap "+", pick a random private topic (e.g. "behike-alerts-8f9k2q").
 *     Whoever knows the topic name can send you pushes, so make it un-guessable.
 *  3. Go to https://script.google.com/ -> "New Project"
 *  4. Paste this whole file into Code.gs. Save.
 *  5. Edit CONFIG below: set NTFY_TOPIC to the topic you picked, and ALERT_EMAIL
 *     to your email (fallback if ntfy is down).
 *  6. Run setup() once manually from the script editor. Approve permissions.
 *     That registers the 5-minute trigger.
 *  7. Run testAlert() once to verify the ntfy push hits your phone.
 *
 * Ops:
 *  - View logs: script editor -> Executions tab
 *  - Change URLs: edit CONFIG.URLS and hit save. No re-setup needed.
 *  - Disable: call teardown() to remove the trigger.
 */

const CONFIG = {
  // Sites to monitor. Add/remove freely.
  URLS: [
    'https://behike.co/',
    'https://innovabarberpr.shop/',
    'https://behike.store/',
  ],

  // ntfy.sh topic — pick an un-guessable string, NOT "behike".
  // Subscribe to this same topic in the ntfy iPhone app.
  NTFY_TOPIC: 'behike-alerts-REPLACE-ME',

  // Fallback email alert (also receives recovery notices).
  ALERT_EMAIL: 'kalani@behike.co',

  // Request timeout + retry behavior.
  REQUEST_TIMEOUT_SEC: 15,
  RETRY_ON_FAIL: true,       // do one retry before declaring DOWN
  RETRY_DELAY_MS: 3000,

  // Only alert if something has been down for this many consecutive checks.
  // 1 = alert immediately on confirmed downtime. 2 = must be down twice in a row.
  DOWN_THRESHOLD: 1,
};

// ================= DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING =================

const PROPS = PropertiesService.getScriptProperties();

function runCheck() {
  const results = CONFIG.URLS.map(checkOne);
  results.forEach(handleResult);
  // Heartbeat — so you know the script is running even when nothing breaks.
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
  const prev = PROPS.getProperty(key) || 'UP';  // default UP so first success doesn't spam

  if (r.ok) {
    PROPS.setProperty(fails_key, '0');
    if (prev === 'DOWN') {
      PROPS.setProperty(key, 'UP');
      notify('RECOVERED', `${r.url}\nCode ${r.code} in ${r.ms}ms`, 'default', 'white_check_mark');
    } else {
      PROPS.setProperty(key, 'UP');
    }
    return;
  }

  // Failed. Count consecutive failures.
  const fails = parseInt(PROPS.getProperty(fails_key) || '0', 10) + 1;
  PROPS.setProperty(fails_key, String(fails));

  if (fails >= CONFIG.DOWN_THRESHOLD && prev !== 'DOWN') {
    PROPS.setProperty(key, 'DOWN');
    const detail = r.err ? `ERROR: ${r.err}` : `HTTP ${r.code}`;
    notify('DOWN', `${r.url}\n${detail}\n(confirmed after ${fails} failures)`, 'urgent', 'rotating_light');
  }
}

function notify(kind, body, priority, tag) {
  const title = `[Behike Uptime] ${kind}`;
  // 1. ntfy.sh push to phone
  try {
    UrlFetchApp.fetch(`https://ntfy.sh/${CONFIG.NTFY_TOPIC}`, {
      method: 'post',
      payload: body,
      headers: {
        'Title': title,
        'Priority': priority,   // default | high | urgent
        'Tags': tag,            // emoji tag, see ntfy.sh docs
      },
      muteHttpExceptions: true,
    });
  } catch (e) {
    console.error('ntfy push failed:', e);
  }
  // 2. Email fallback (also useful record)
  try {
    MailApp.sendEmail({
      to: CONFIG.ALERT_EMAIL,
      subject: title,
      body: body,
    });
  } catch (e) {
    console.error('email send failed:', e);
  }
  console.log(`${title} — ${body}`);
}

// ================= SETUP / TEARDOWN / TEST =================

function setup() {
  teardown();
  ScriptApp.newTrigger('runCheck').timeBased().everyMinutes(5).create();
  console.log('Trigger installed. runCheck() will fire every 5 minutes.');
  runCheck();  // immediate first check
}

function teardown() {
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'runCheck') ScriptApp.deleteTrigger(t);
  });
  console.log('Triggers removed.');
}

function testAlert() {
  notify('TEST', 'If you see this on your phone, ntfy works.', 'high', 'test_tube');
}

function resetState() {
  const props = PROPS.getProperties();
  Object.keys(props).forEach(k => {
    if (k.startsWith('state__') || k.startsWith('fails__')) PROPS.deleteProperty(k);
  });
  console.log('State cleared.');
}

function status() {
  const props = PROPS.getProperties();
  const rows = Object.keys(props).filter(k => k.startsWith('state__'))
    .map(k => ({ url: k.replace('state__', ''), state: props[k], fails: props['fails__' + k.replace('state__', '')] || '0' }));
  console.log('Last run: ' + (props.last_run_iso || 'never'));
  console.log(JSON.stringify(rows, null, 2));
}
