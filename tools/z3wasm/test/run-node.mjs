// Usage: node run-node.mjs <dir containing z3w.js+z3w.wasm> [repeats]
import { tests, statefulTests } from './tests.mjs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const dir = path.resolve(process.argv[2] ?? '../dist');
const reps = +(process.argv[3] ?? 1);
const t0 = performance.now();
const { Z3W } = await import(pathToFileURL(path.join(dir, 'z3w.js')).href);
const z3 = await Z3W.create();
const loadMs = performance.now() - t0;
console.log(`version: ${z3.version}`);
console.log(`load+instantiate: ${loadMs.toFixed(1)} ms`);
let fail = 0;
const results = [];
for (const t of tests) {
  let best = Infinity, first, out;
  for (let r = 0; r < reps; r++) {
    z3.reset();
    const s = performance.now();
    out = z3.eval(t.smt);
    const dt = performance.now() - s;
    if (r === 0) first = dt;
    best = Math.min(best, dt);
  }
  const ok = t.check(out);
  if (!ok) fail++;
  results.push({ id: t.id, ok, firstMs: +first.toFixed(1), bestMs: +best.toFixed(1), first: out.trim().split('\n')[0] });
  console.log(`[${ok ? 'PASS' : 'FAIL'}] (${t.id}) ${t.desc}: first ${first.toFixed(1)} ms, best-of-${reps} ${best.toFixed(1)} ms\n    ${out.trim().replace(/\n/g, '\n    ').slice(0, 600)}`);
}
z3.reset();
for (const [i, t] of statefulTests.entries()) {
  const out = z3.eval(t.smt);
  const ok = t.check(out);
  if (!ok) fail++;
  console.log(`[${ok ? 'PASS' : 'FAIL'}] stateful#${i}: ${JSON.stringify(out.trim())}`);
}
z3.free();
console.log(JSON.stringify({ loadMs: +loadMs.toFixed(1), results }));
console.log(fail ? `${fail} FAILED` : 'ALL PASS');
process.exit(fail ? 1 : 0);
