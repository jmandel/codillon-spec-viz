import { Z3W } from '../dist/z3w.js';
function php(p, h) {
  let s = '';
  for (let i = 0; i < p; i++) for (let j = 0; j < h; j++) s += `(declare-const x_${i}_${j} Bool)`;
  for (let i = 0; i < p; i++) s += `(assert (or ${Array.from({ length: h }, (_, j) => `x_${i}_${j}`).join(' ')}))`;
  for (let j = 0; j < h; j++) for (let i = 0; i < p; i++) for (let k = i + 1; k < p; k++) s += `(assert (or (not x_${i}_${j}) (not x_${k}_${j})))`;
  return s;
}
const z3 = await Z3W.create();
for (const logic of ['', '(set-logic QF_UF)']) {
  z3.reset(); const t = performance.now();
  console.log(JSON.stringify(logic), JSON.stringify(z3.eval(logic + '(set-option :rlimit 1000)' + php(8, 7) + '(check-sat)(set-option :rlimit 0)(push)(declare-const q Int)(assert (= q 1))(check-sat)(get-info :reason-unknown)(pop)').trim()), (performance.now() - t).toFixed(0), 'ms');
}
