import { Z3W } from '../dist/z3w.js';
const z3 = await Z3W.create();
for (const d of [50000, 100000, 200000, 400000]) {
  const s = performance.now();
  let out;
  try { out = z3.eval(`(declare-const x Int)(assert (= x ${'(+ 1 '.repeat(d)}0${')'.repeat(d)}))(check-sat)`).trim().slice(0, 80); }
  catch (e) { out = 'THROW ' + e.constructor.name + ': ' + e.message.slice(0, 120); }
  console.log(d, (performance.now() - s).toFixed(0) + 'ms', out);
  try { z3.reset(); } catch (e) { console.log('reset failed:', e.message.slice(0, 80)); break; }
}
