#!/usr/bin/env node
// Independent check of the Euclid derivation in the five-rule calculus (types as finite sets of states).
// Usage: node check-euclid.cjs [N]     (N <= 32, default 32: every variable ranges over 0..N)
// Prints, for the correct derivation and each seeded mistake, the verdict for every slice (a, b).
const Calc = require('./calculus.js');
const N = Number(process.argv[2] || 32);
const D = Calc.makeDomain(N);
const order = ['ASSIGN x,y := a,b', 'SUB ⊆ I (entry)', 'WHILE', 'ASSIGN x,y := y, x mod y', 'SUB ⊆ I (back edge)', 'SUB ⊆ post (exit)', 'FUN', 'SEQ'];
function describe(node) {
  const lines = []; const w = (n, ind) => { const p = '  '.repeat(ind);
    switch (n.rule) {
      case 'FUN': lines.push(`${p}FUN ${n.name}(${n.params.join(', ')}) : {${n.result.v} | ${Calc.pf(n.result.q)}}  return ${Calc.pe(n.ret)}`); w(n.body, ind + 1); break;
      case 'SEQ': lines.push(`${p}SEQ`); w(n.first, ind + 1); w(n.second, ind + 1); break;
      case 'SUB': lines.push(`${p}SUB out: {${Calc.pf(n.out)}}`); w(n.inner, ind + 1); break;
      case 'ASSIGN': lines.push(`${p}ASSIGN in: {${Calc.pf(n.in)}}  ${n.targets.join(', ')} := ${n.exprs.map(Calc.pe).join(', ')}`); break;
      case 'WHILE': lines.push(`${p}WHILE inv: {${Calc.pf(n.in)}}  guard: ${Calc.pf(n.guard)}  measure: ${Calc.pe(n.measure)}`); w(n.body, ind + 1); break;
    } };
  w(node, 0); return lines.join('\n');
}
console.log(`domain: every variable in 0..${N}; ${D.M} states per slice (a, b); ${(N + 1) ** 2} slices\n`);
console.log('trusted base: the evaluator (mod, comparisons, Div as a bitmask over d = 1..N, simultaneous assignment) and enumeration of the domain.\n');
let allOk = true;
for (const [key, seed] of Object.entries(Calc.seeds)) {
  const node = seed.build();
  console.log(`== ${seed.title} (${seed.kind}): ${seed.what}`);
  if (key === 'ok') console.log(describe(node).split('\n').map(l => '   | ' + l).join('\n'));
  const t0 = Date.now();
  const all = Calc.checkAll(D, node);
  const sample = Calc.check(D, node, 12, 8);
  console.log(`   rule applications: ${all.applications}; leaf facts per slice: ${all.leaves}; slices refused: ${all.failures.length} of ${all.slices}` + (all.failures.length ? `; first refused (a, b) = (${all.failures[0]})` : '') + `  [${Date.now() - t0} ms]`);
  const fails = sample.recs.flatMap(r => r.premises.filter(p => !p.ok).map(p => [r, p]));
  console.log(`   slice (12, 8): ${sample.ok ? 'PASS' : 'REFUSED'}` + fails.map(([r, p]) => `\n      ✗ ${r.rule}: ${p.text}; first counterexample ${Array.isArray(p.bad[0]) ? 'row ' + p.bad[0][0] + ' → ' + p.bad[0][1] : '(x, y) = (' + D.xy(p.bad[0]) + ')'}`).join(''));
  const tr = Calc.trace(D, node, 12, 8);
  console.log(`   run gcd(12, 8): ${tr.trapped ? 'TRAP (x mod 0)' : 'returns ' + tr[tr.length - 1].r} in ${tr.length} steps  (evidence, not proof)\n`);
  const expectOk = key === 'ok';
  if (expectOk !== (all.failures.length === 0)) allOk = false;
}
// the proof is about all (a, b): the correct derivation must pass every slice, every seed must fail some slice
console.log(allOk ? 'SUMMARY: correct derivation accepted on every slice; every seeded mistake refused on at least one slice.' : 'SUMMARY: UNEXPECTED RESULT');
process.exit(allOk ? 0 : 1);
