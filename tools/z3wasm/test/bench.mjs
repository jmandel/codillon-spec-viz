// Fixed-work benchmark for comparing builds. Usage: node bench.mjs <dir> [reps]
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { tests } from './tests.mjs';
const dir = path.resolve(process.argv[2]);
const reps = +(process.argv[3] ?? 5);
const { Z3W } = await import(pathToFileURL(path.join(dir, 'z3w.js')).href);
const z3 = await Z3W.create();
const byId = Object.fromEntries(tests.map((t) => [t.id, t.smt]));
const bench = {
  'php-rlimit2M': byId.e,
  'bv-factor': `(set-logic QF_BV)(declare-const x (_ BitVec 32))(declare-const y (_ BitVec 32))
(assert (= (bvmul x y) #x${(65521 * 65519).toString(16).padStart(8, '0')}))
(assert (bvugt x #x00000001))(assert (bvugt y #x00000001))(assert (bvult x #x00010000))(assert (bvult y #x00010000))
(check-sat)(get-value (x y))`,
  'nia-isqrt': byId.d,
  'quant-f2': byId.f2,
  'abv-c': byId.c,
};
const out = {};
for (const [k, smt] of Object.entries(bench)) {
  const ts = [];
  let o;
  for (let r = 0; r < reps; r++) { z3.reset(); const s = performance.now(); o = z3.eval(smt); ts.push(performance.now() - s); }
  ts.sort((a, b) => a - b);
  out[k] = { min: +ts[0].toFixed(1), median: +ts[Math.floor(ts.length / 2)].toFixed(1), result: o.trim().split('\n')[0] };
}
console.log(JSON.stringify({ dir: path.basename(dir), ...out }));
