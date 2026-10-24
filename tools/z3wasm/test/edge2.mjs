import { Z3W } from '../dist/z3w.js';
import { tests } from './tests.mjs';
const php = tests.find((t) => t.id === 'e').smt.split('(check-sat)')[0].replace('(set-option :rlimit 2000000)', '').replace('(set-logic QF_UF)', '');
const z3 = await Z3W.create();
const cases = {
  'push/pop around exhausted query, rlimit kept': '(set-option :rlimit 100000)(push)' + php + '(check-sat)(pop)(declare-const q Int)(assert (= q 1))(check-sat)(get-value (q))',
  'push/pop, then rlimit 0': '(set-option :rlimit 100000)(push)' + php + '(check-sat)(pop)(set-option :rlimit 0)(declare-const q Int)(assert (= q 1))(check-sat)',
  'separate eval calls': null,
};
for (const [name, smt] of Object.entries(cases)) {
  z3.reset();
  if (smt) { console.log(name, JSON.stringify(z3.eval(smt).trim())); continue; }
  console.log(name, JSON.stringify(z3.eval('(set-option :rlimit 100000)(push)' + php + '(check-sat)').trim()),
    JSON.stringify(z3.eval('(pop)(declare-const q Int)(assert (= q 1))(check-sat)').trim()),
    JSON.stringify(z3.eval('(set-option :rlimit 5000000)(push)(assert (> q 0))(check-sat)(pop)').trim()));
}
