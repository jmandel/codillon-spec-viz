import { Z3W } from '../dist/z3w.js';
import { tests } from './tests.mjs';
const php = tests.find((t) => t.id === 'e').smt.split('(check-sat)')[0].replace('(set-option :rlimit 2000000)', '');
const z3 = await Z3W.create();
const cases = {
  'try-for tactic 200ms': php + '(check-sat-using (try-for smt 200))',
  'solver timeout param via set-option :timeout': '(set-option :timeout 200)' + php + '(check-sat)',
  'smt.threads=4': '(set-option :smt.threads 4)(declare-const x Int)(assert (> x 3))(check-sat)',
  'sat.threads=4 (QF_BV)': '(set-option :sat.threads 4)(declare-const b (_ BitVec 8))(assert (= (bvmul b b) #x31))(check-sat)',
  'parallel.enable': '(set-option :parallel.enable true)(declare-const x Int)(assert (> x 3))(check-sat)',
  'tactic par-or': '(declare-const x Int)(assert (> x 3))(check-sat-using (par-or smt simplify))',
  'rlimit then plain query on same ctx': '(set-option :rlimit 1000)' + php + '(check-sat)(set-option :rlimit 0)(push)(declare-const q Int)(assert (= q 1))(check-sat)(pop)',
  'get-info :rlimit': '(declare-const x Int)(assert (> x 3))(check-sat)(get-info :rlimit)',
  'echo / get-option': '(echo "hi")(get-option :produce-models)',
};
for (const [name, smt] of Object.entries(cases)) {
  z3.reset();
  const s = performance.now();
  let out;
  try { out = z3.eval(smt); } catch (e) { out = 'THROW ' + e; }
  console.log(`${name}: ${(performance.now() - s).toFixed(0)} ms -> ${JSON.stringify(out.trim().slice(0, 160))}`);
}
