import { Z3W } from '../dist/z3w.js';
function php(p, h) {
  let s = '';
  for (let i = 0; i < p; i++) for (let j = 0; j < h; j++) s += `(declare-const x_${i}_${j} Bool)`;
  for (let i = 0; i < p; i++) s += `(assert (or ${Array.from({ length: h }, (_, j) => `x_${i}_${j}`).join(' ')}))`;
  for (let j = 0; j < h; j++) for (let i = 0; i < p; i++) for (let k = i + 1; k < p; k++) s += `(assert (or (not x_${i}_${j}) (not x_${k}_${j})))`;
  return s;
}
const z3 = await Z3W.create();
let t = performance.now();
console.log('PHP(8,7) unlimited:', z3.eval(php(8, 7) + '(check-sat)(get-info :rlimit)').trim().replace(/\n/g, ' '), (performance.now() - t).toFixed(0), 'ms');
z3.reset(); t = performance.now();
console.log('rlimit 1000 then 0, same assertions:', JSON.stringify(z3.eval('(set-option :rlimit 1000)' + php(8, 7) + '(check-sat)(set-option :rlimit 0)(check-sat)(get-info :reason-unknown)').trim()), (performance.now() - t).toFixed(0), 'ms');
z3.reset(); t = performance.now();
console.log('rlimit 1000 then 100000000:', JSON.stringify(z3.eval('(set-option :rlimit 1000)' + php(8, 7) + '(check-sat)(set-option :rlimit 100000000)(check-sat)').trim()), (performance.now() - t).toFixed(0), 'ms');
z3.reset(); t = performance.now();
console.log('rlimit 1000, check, rlimit 0, push+new assert, check:', JSON.stringify(z3.eval('(set-option :rlimit 1000)' + php(8, 7) + '(check-sat)(set-option :rlimit 0)(push)(declare-const q Int)(assert (= q 1))(check-sat)(get-info :reason-unknown)(pop)').trim()), (performance.now() - t).toFixed(0), 'ms');
z3.reset(); t = performance.now();
console.log('no rlimit, push+new assert, check:', JSON.stringify(z3.eval(php(8, 7) + '(push)(declare-const q Int)(assert (= q 1))(check-sat)(get-info :reason-unknown)(pop)').trim()), (performance.now() - t).toFixed(0), 'ms');
z3.reset(); t = performance.now();
console.log('PHP(11,10) push+check under :rlimit 0 (default) with :timeout 2000:', JSON.stringify(z3.eval('(set-option :timeout 2000)' + php(11, 10) + '(push)(declare-const q Int)(assert (= q 1))(check-sat)(get-info :reason-unknown)(pop)').trim()), (performance.now() - t).toFixed(0), 'ms');
