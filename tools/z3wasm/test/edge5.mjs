import { Z3W } from '../dist/z3w.js';
function php(p, h) {
  let s = '';
  for (let i = 0; i < p; i++) for (let j = 0; j < h; j++) s += `(declare-const x_${i}_${j} Bool)`;
  for (let i = 0; i < p; i++) s += `(assert (or ${Array.from({ length: h }, (_, j) => `x_${i}_${j}`).join(' ')}))`;
  for (let j = 0; j < h; j++) for (let i = 0; i < p; i++) for (let k = i + 1; k < p; k++) s += `(assert (or (not x_${i}_${j}) (not x_${k}_${j})))`;
  return s;
}
const z3 = await Z3W.create();
for (const second of ['(set-option :rlimit 0)(set-option :timeout 3000)(check-sat)', '(set-option :rlimit 0)(set-option :timeout 3000)(push)(assert true)(check-sat)(pop)', '(set-option :rlimit 3000000)(push)(assert true)(check-sat)(pop)']) {
  z3.reset(); let t = performance.now();
  const a = z3.eval('(set-option :rlimit 1000)' + php(11, 10) + '(check-sat)').trim(); const ta = performance.now() - t; t = performance.now();
  const b = z3.eval(second + '(get-info :reason-unknown)').trim().replace(/\n/g, ' ');
  console.log(second, '|', a, ta.toFixed(0) + 'ms |', b, (performance.now() - t).toFixed(0) + 'ms');
}
