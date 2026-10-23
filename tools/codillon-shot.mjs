// usage: node cdp-shot.mjs <url> <program.wat> <out.png> [width] [step-fraction]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
const [url, progFile, out, width = '1400', stepFrac] = process.argv.slice(2);
const prog = fs.readFileSync(progFile, 'utf8');
const port = 9300 + Math.floor(Math.random() * 500);
const chrome = spawn('chromium', ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`,
  `--window-size=${width},1200`, `--user-data-dir=/home/jmandel/hobby/.agent-scratch/codalon-viz/real/prof-${port}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws;
for (let i = 0; i < 50; i++) { try { const r = await fetch(`http://127.0.0.1:${port}/json`); const t = (await r.json()).find(x => x.type === 'page'); ws = new WebSocket(t.webSocketDebuggerUrl); break; } catch { await sleep(200); } }
await new Promise(r => ws.addEventListener('open', r));
let id = 0; const pend = new Map(); const logs = [];
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } if (m.method === 'Runtime.consoleAPICalled') logs.push(m.params.args.map(a => a.value).join(' ')); if (m.method === 'Runtime.exceptionThrown') logs.push('EXC ' + m.params.exceptionDetails.text); });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Runtime.enable'); await send('Page.enable');
await send('Page.navigate', { url }); await sleep(1500);
await send('Runtime.evaluate', { expression: `localStorage.setItem('codillon_content', ${JSON.stringify(prog)}); 1` });
await send('Page.reload'); await sleep(3500);
if (stepFrac) {
  await send('Runtime.evaluate', { expression: `(() => { const s = document.querySelector('input.step-slider'); if (!s) return 'no slider'; const v = Math.round(Number(s.max) * ${Number(stepFrac)}); s.value = v; s.dispatchEvent(new Event('input', {bubbles:true})); return v + '/' + s.max; })()`, returnByValue: true }).then(r => logs.push('slider ' + JSON.stringify(r.result?.result?.value)));
  await sleep(1500);
}
const m = await send('Page.getLayoutMetrics');
const h = Math.ceil(m.result.cssContentSize.height);
await send('Emulation.setDeviceMetricsOverride', { width: Number(width), height: Math.min(h, 6000), deviceScaleFactor: 1, mobile: false });
await sleep(800);
const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
fs.writeFileSync(out, Buffer.from(shot.result.data, 'base64'));
console.log(out, 'height', h, logs.slice(0, 8).join(' | '));
ws.close(); chrome.kill();
