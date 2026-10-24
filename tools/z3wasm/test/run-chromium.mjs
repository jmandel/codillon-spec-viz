// Drives headless Chromium via CDP (Node's built-in WebSocket) against a plain
// `python3 -m http.server` (no COOP/COEP). Usage: node run-chromium.mjs <url> <userDataDir>
import { spawn } from 'node:child_process';
const url = process.argv[2];
const userDir = process.argv[3];
const port = 9300 + Math.floor(Math.random() * 500);
const chrome = spawn('chromium', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${userDir}`,
  '--no-first-run', '--no-default-browser-check', '--disable-gpu', 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const deadline = Date.now() + 180000;
let targets;
for (;;) {
  try { targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); if (targets.find((t) => t.type === 'page')) break; } catch {}
  if (Date.now() > deadline) throw new Error('chromium did not start');
  await sleep(200);
}
const page = targets.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let seq = 0; const waiters = new Map(); const consoleLines = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && waiters.has(m.id)) { waiters.get(m.id)(m); waiters.delete(m.id); }
  else if (m.method === 'Runtime.consoleAPICalled') consoleLines.push(m.params.args.map((a) => a.value ?? a.description).join(' '));
  else if (m.method === 'Runtime.exceptionThrown') consoleLines.push('EXC ' + JSON.stringify(m.params.exceptionDetails).slice(0, 500));
};
const cdp = (method, params = {}) => new Promise((r) => { const id = ++seq; waiters.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
await cdp('Runtime.enable');
await cdp('Network.enable');
await cdp('Network.setCacheDisabled', { cacheDisabled: true });
const t0 = Date.now();
await cdp('Page.navigate', { url });
let res;
while (Date.now() < deadline) {
  const r = await cdp('Runtime.evaluate', { expression: 'JSON.stringify(window.__results ?? null)', returnByValue: true });
  res = JSON.parse(r.result?.result?.value ?? 'null');
  if (res && res.done) break;
  await sleep(250);
}
const ua = (await cdp('Runtime.evaluate', { expression: 'navigator.userAgent', returnByValue: true })).result.result.value;
ws.close(); chrome.kill();
if (!res) { console.log('TIMEOUT; console:', consoleLines); process.exit(2); }
res.userAgent = ua; res.totalWallMs = Date.now() - t0; res.console = consoleLines;
for (const t of res.tests) console.log(`[${t.ok ? 'PASS' : 'FAIL'}] (${t.id}) ${t.ms} ms  ${(t.first ?? t.output).trim().split('\n')[0]}`);
for (const t of res.tests) delete t.output;
const { tests: _t, ...rest } = res; console.log(JSON.stringify(rest, null, 1));
process.exit(res.error || res.tests.some((t) => !t.ok) ? 1 : 0);
