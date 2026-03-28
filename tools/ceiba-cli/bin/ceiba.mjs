#!/usr/bin/env node
// Ceiba CLI — talks to Cobo bridge at 192.168.0.151:9876
// Zero dependencies. Node built-ins only.

import { request } from 'http';
import { readFileSync, writeFileSync, existsSync, mkdirSync, appendFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

// --- Machines ---
const MACHINES = {
  cobo: { host: '192.168.0.151', port: 9876, token: (() => { try { return readFileSync(join(homedir(), '.behique_bridge_token'), 'utf8').trim(); } catch { return null; } })() },
  comp3: { host: '192.168.0.152', port: 9877, token: 'comp3-tmp-token' },
};

// --- Config (resolve target machine) ---
function resolveTarget(args) {
  const name = args[0]?.toLowerCase();
  if (MACHINES[name]) return { machine: MACHINES[name], machineName: name, rest: args.slice(1) };
  return { machine: MACHINES.cobo, machineName: 'cobo', rest: args };
}

const BRIDGE_HOST = process.env.BRIDGE_HOST || '192.168.0.151';
const BRIDGE_PORT = process.env.BRIDGE_PORT || 9876;
const TOKEN = process.env.BRIDGE_AUTH_TOKEN
  || (() => { try { return readFileSync(join(homedir(), '.behique_bridge_token'), 'utf8').trim(); } catch { return null; } })();

if (!TOKEN) {
  console.error('No auth token. Set BRIDGE_AUTH_TOKEN or create ~/.behique_bridge_token');
  process.exit(1);
}

// --- HTTP helper ---
function bridgeRequestTo(machine, method, path, body = null) {
  return new Promise((resolve, reject) => {
    const opts = {
      hostname: machine.host,
      port: machine.port,
      path,
      method,
      headers: {
        'Authorization': `Bearer ${machine.token}`,
        'Content-Type': 'application/json',
      },
    };
    const req = request(opts, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const status = res.statusCode;
        let parsed;
        try { parsed = JSON.parse(data); } catch { parsed = data; }
        if (status >= 200 && status < 300) resolve({ status, data: parsed });
        else reject({ status, data: parsed });
      });
    });
    req.on('error', (err) => {
      if (err.code === 'ECONNREFUSED') reject({ status: 0, data: `Offline at ${machine.host}:${machine.port}` });
      else reject({ status: 0, data: err.message });
    });
    req.setTimeout(10000, () => { req.destroy(); reject({ status: 0, data: 'Timeout (10s)' }); });
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function bridgeRequest(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const opts = {
      hostname: BRIDGE_HOST,
      port: BRIDGE_PORT,
      path,
      method,
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json',
      },
    };

    const req = request(opts, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const status = res.statusCode;
        let parsed;
        try { parsed = JSON.parse(data); } catch { parsed = data; }

        if (status >= 200 && status < 300) {
          resolve({ status, data: parsed });
        } else {
          reject({ status, data: parsed });
        }
      });
    });

    req.on('error', (err) => {
      if (err.code === 'ECONNREFUSED') {
        reject({ status: 0, data: `Cobo is offline or bridge not running at ${BRIDGE_HOST}:${BRIDGE_PORT}` });
      } else {
        reject({ status: 0, data: err.message });
      }
    });

    req.setTimeout(10000, () => {
      req.destroy();
      reject({ status: 0, data: 'Request timed out (10s)' });
    });

    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// --- Commands ---
const commands = {
  async wake(args) {
    const { machine, machineName } = resolveTarget(args);
    if (args[0] === 'all') {
      for (const [name, m] of Object.entries(MACHINES)) {
        process.stdout.write(`${name.toUpperCase()}: `);
        try {
          await bridgeRequestTo(m, 'GET', '/');
          console.log('ONLINE');
        } catch { console.log('OFFLINE'); }
      }
      return;
    }
    console.log(`Pinging ${machineName.toUpperCase()} at ${machine.host}:${machine.port}...`);
    try {
      const { data } = await bridgeRequestTo(machine, 'GET', '/');
      console.log(`${machineName.toUpperCase()} is ONLINE`);
      if (typeof data === 'object') {
        if (data.uptime) console.log(`  Uptime: ${Math.floor(data.uptime)}s`);
        if (data.version) console.log(`  Version: ${data.version}`);
        if (data.status) console.log(`  Status: ${data.status}`);
      } else {
        console.log(`  Response: ${data}`);
      }
    } catch (err) {
      console.error(`${machineName.toUpperCase()} is OFFLINE`);
      console.error(`  ${err.data}`);
      process.exit(1);
    }
  },

  async bridge(args) {
    const command = args.join(' ');
    if (!command) {
      console.error('Usage: ceiba bridge <command>');
      console.error('  Example: ceiba bridge "ls -la"');
      process.exit(1);
    }
    console.log(`Sending to Cobo: ${command}`);
    try {
      const { data } = await bridgeRequest('POST', '/exec', { command });
      if (data.stdout) console.log(data.stdout);
      if (data.stderr) console.error(data.stderr);
      if (data.error) console.error(`Error: ${data.error}`);
      if (data.output) console.log(data.output);
    } catch (err) {
      console.error(`Bridge error (${err.status}): ${typeof err.data === 'string' ? err.data : JSON.stringify(err.data)}`);
      process.exit(1);
    }
  },

  async claude(args) {
    const prompt = args.join(' ');
    if (!prompt) {
      console.error('Usage: ceiba claude <prompt>');
      console.error('  Example: ceiba claude "what files are in C:\\behique?"');
      process.exit(1);
    }
    console.log('Sending to Claude via Cobo bridge...');
    try {
      const { data } = await bridgeRequest('POST', '/claude', { prompt });
      if (data.response) {
        console.log('\n' + data.response);
      } else if (data.content) {
        const text = Array.isArray(data.content)
          ? data.content.map(b => b.text || '').join('')
          : data.content;
        console.log('\n' + text);
      } else {
        console.log(JSON.stringify(data, null, 2));
      }
    } catch (err) {
      console.error(`Claude error (${err.status}): ${typeof err.data === 'string' ? err.data : JSON.stringify(err.data)}`);
      process.exit(1);
    }
  },

  async task(args) {
    let priority = 'normal';
    const filtered = [];
    for (let i = 0; i < args.length; i++) {
      if (args[i] === '--priority' && args[i + 1]) {
        priority = args[++i];
        if (!['high', 'normal', 'low'].includes(priority)) {
          console.error('Invalid priority. Use: high, normal, low');
          process.exit(1);
        }
      } else {
        filtered.push(args[i]);
      }
    }
    const description = filtered.join(' ');
    if (!description) {
      console.error('Usage: ceiba task <description> [--priority high|normal|low]');
      console.error('  Example: ceiba task "run full backup" --priority high');
      process.exit(1);
    }
    try {
      const { data } = await bridgeRequest('POST', '/task', { description, priority });
      const id = data.id || data.task_id || '(unknown)';
      console.log(`Task queued: ${id}`);
    } catch (err) {
      console.error(`Task error (${err.status}): ${typeof err.data === 'string' ? err.data : JSON.stringify(err.data)}`);
      process.exit(1);
    }
  },

  async tasks() {
    try {
      const { data } = await bridgeRequest('GET', '/tasks');
      const items = Array.isArray(data) ? data : (data.tasks || []);
      if (items.length === 0) {
        console.log('No tasks in queue.');
        return;
      }
      const statusIcon = { pending: '\u23F3', running: '\uD83D\uDD04', done: '\u2705', failed: '\u274C' };
      const idW = Math.max(4, ...items.map(t => String(t.id || '').length));
      const stW = Math.max(8, ...items.map(t => String(t.status || '').length + 2));
      const prW = Math.max(8, ...items.map(t => String(t.priority || '').length));
      const header = `${'ID'.padEnd(idW)}  ${'STATUS'.padEnd(stW)}  ${'PRIORITY'.padEnd(prW)}  DESCRIPTION`;
      console.log(header);
      console.log('-'.repeat(header.length));
      for (const t of items) {
        const icon = statusIcon[t.status] || ' ';
        const st = `${icon} ${t.status || 'unknown'}`;
        console.log(`${String(t.id || '').padEnd(idW)}  ${st.padEnd(stW)}  ${String(t.priority || '').padEnd(prW)}  ${t.description || ''}`);
      }
    } catch (err) {
      console.error(`Tasks error (${err.status}): ${typeof err.data === 'string' ? err.data : JSON.stringify(err.data)}`);
      process.exit(1);
    }
  },

  async 'task-status'(args) {
    const id = args[0];
    if (!id) {
      console.error('Usage: ceiba task-status <id>');
      process.exit(1);
    }
    try {
      const { data } = await bridgeRequest('GET', `/task/${encodeURIComponent(id)}`);
      if (typeof data === 'object') {
        for (const [key, val] of Object.entries(data)) {
          console.log(`  ${key}: ${typeof val === 'object' ? JSON.stringify(val) : val}`);
        }
      } else {
        console.log(data);
      }
    } catch (err) {
      console.error(`Task status error (${err.status}): ${typeof err.data === 'string' ? err.data : JSON.stringify(err.data)}`);
      process.exit(1);
    }
  },

  async watch(args) {
    const interval = parseInt(args[0]) || 30;
    const logDir = join(homedir(), '.ceiba');
    const logFile = join(logDir, 'watchdog.log');
    if (!existsSync(logDir)) mkdirSync(logDir, { recursive: true });

    const state = {};
    for (const name of Object.keys(MACHINES)) state[name] = null; // null = unknown

    function ts() { return new Date().toISOString().replace('T', ' ').slice(0, 19); }

    function log(msg) {
      const line = `[${ts()}] ${msg}`;
      console.log(line);
      appendFileSync(logFile, line + '\n');
    }

    async function ping(name) {
      const m = MACHINES[name];
      try {
        await bridgeRequestTo(m, 'GET', '/');
        return true;
      } catch {
        return false;
      }
    }

    log(`Watchdog started. Checking every ${interval}s. Log: ${logFile}`);
    log(`Monitoring: ${Object.keys(MACHINES).join(', ')}`);

    // Initial check
    for (const name of Object.keys(MACHINES)) {
      const online = await ping(name);
      state[name] = online;
      log(`${name.toUpperCase()}: ${online ? 'ONLINE' : 'OFFLINE'}`);
    }

    // Loop
    const loop = setInterval(async () => {
      for (const name of Object.keys(MACHINES)) {
        const online = await ping(name);
        const prev = state[name];

        if (prev === true && !online) {
          log(`${name.toUpperCase()} WENT OFFLINE`);
        } else if (prev === false && online) {
          log(`${name.toUpperCase()} BACK ONLINE`);
        }
        state[name] = online;
      }
    }, interval * 1000);

    // Handle graceful shutdown
    process.on('SIGINT', () => {
      clearInterval(loop);
      log('Watchdog stopped.');
      process.exit(0);
    });
    process.on('SIGTERM', () => {
      clearInterval(loop);
      log('Watchdog stopped.');
      process.exit(0);
    });
  },

  async recover() {
    console.log('Checking all machines and attempting recovery...\n');
    const results = [];
    for (const [name, m] of Object.entries(MACHINES)) {
      process.stdout.write(`${name.toUpperCase()}: `);
      try {
        const { data } = await bridgeRequestTo(m, 'GET', '/');
        console.log('ONLINE');
        results.push({ name, status: 'online', data });
      } catch {
        console.log('OFFLINE');
        results.push({ name, status: 'offline' });
      }
    }

    const offline = results.filter(r => r.status === 'offline');
    if (offline.length === 0) {
      console.log('\nAll machines online. Nothing to recover.');
      return;
    }

    console.log(`\n${offline.length} machine(s) offline: ${offline.map(o => o.name).join(', ')}`);
    console.log('Retrying every 10s until all reconnect (Ctrl+C to stop)...\n');

    const remaining = new Set(offline.map(o => o.name));

    const loop = setInterval(async () => {
      for (const name of [...remaining]) {
        try {
          await bridgeRequestTo(MACHINES[name], 'GET', '/');
          console.log(`[${new Date().toISOString().slice(11, 19)}] ${name.toUpperCase()} RECOVERED`);
          remaining.delete(name);
        } catch {
          // still offline
        }
      }
      if (remaining.size === 0) {
        console.log('\nAll machines recovered.');
        clearInterval(loop);
      }
    }, 10000);

    process.on('SIGINT', () => { clearInterval(loop); process.exit(0); });
  },

  help() {
    console.log(`
Ceiba CLI — Behique Network Control

Machines:
  cobo       192.168.0.151:9876
  comp3      192.168.0.152:9877

Commands:
  ceiba wake [machine]                Ping a machine (default: cobo)
  ceiba wake all                      Ping all machines
  ceiba watch [seconds]               Watchdog: monitor all machines (default: 30s)
  ceiba recover                       Detect offline machines, retry until back
  ceiba bridge <cmd>                  Execute command on Cobo
  ceiba claude <prompt>               Send prompt to Claude via Cobo
  ceiba task <desc> [--priority P]    Queue task on Cobo (P: high|normal|low)
  ceiba tasks                         List all tasks in queue
  ceiba task-status <id>              Show task details
  ceiba help                          Show this help

Examples:
  ceiba wake comp3
  ceiba wake all
  ceiba task "run backup" --priority high
`);
  },
};

// --- Main ---
const [cmd, ...args] = process.argv.slice(2);

if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') {
  commands.help();
} else if (commands[cmd]) {
  commands[cmd](args).catch((err) => {
    console.error('Unexpected error:', err);
    process.exit(1);
  });
} else {
  console.error(`Unknown command: ${cmd}`);
  console.error('Run "ceiba help" for usage.');
  process.exit(1);
}
