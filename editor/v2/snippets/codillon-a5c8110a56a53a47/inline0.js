
let worker = null, ready = null, state = 'idle', failure = '', nextId = 1, startedAt = 0, loadMs = -1;
const pending = new Map();
function fail(why) {
  state = 'failed';
  failure = why;
  for (const p of pending.values()) p.reject(new Error(why));
  pending.clear();
  if (worker) { try { worker.terminate(); } catch (e) {} }
  worker = null;
}
function start() {
  state = 'loading';
  startedAt = performance.now();
  ready = new Promise((resolve, reject) => {
    try {
      worker = new Worker(new URL('z3/z3w-worker.js', document.baseURI), { type: 'module' });
    } catch (e) {
      fail('the solver could not start: ' + e);
      reject(new Error(failure));
      return;
    }
    worker.onmessage = (e) => {
      const d = e.data || {};
      if ('ready' in d) {
        if (d.ready) { state = 'ready'; loadMs = performance.now() - startedAt; resolve(); }
        else { fail('the solver did not load: ' + d.error); reject(new Error(failure)); }
        return;
      }
      const p = pending.get(d.id);
      if (p) { pending.delete(d.id); p.resolve(String(d.output)); }
    };
    worker.onerror = (e) => {
      if (e && e.preventDefault) e.preventDefault();
      fail('the solver did not load' + (e && e.message ? ': ' + e.message : ''));
      reject(new Error(failure));
    };
  });
  ready.catch(() => {});
  return ready;
}
export function z3_solve(text) {
  if (state === 'failed') return Promise.reject(new Error(failure));
  if (!ready) start();
  return ready.then(() => new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    // a fresh context for each query ((reset) in the text does not forget recursive functions)
    worker.postMessage({ id: nextId++, reset: true });
    worker.postMessage({ id, smtlib: text });
  }));
}
export function z3_state() { return state; }
export function z3_load_ms() { return loadMs; }
export function z3_failure() { return failure; }
export function z3_now() { return performance.now(); }
export function z3_sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
