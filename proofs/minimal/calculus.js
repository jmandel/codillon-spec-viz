// calculus.js — "types as finite sets of states": a five-rule refinement calculus
// (ASSIGN, SEQ, SUB, WHILE, FUN) with every leaf premise discharged by enumeration
// over a bounded domain. Shared verbatim by the tutorial page and the node checker.
//
// A state is (x, y) for fixed parameters (a, b); the domain is 0..N for every variable.
// A type is a set of states = Uint8Array over the (N+1)^2 grid, index = y*(N+1)+x.
// Divisor sets Div(v) are bitmasks over d = 1..N (N <= 32); Div(0) = all bits.
const Calc = (() => {
  'use strict';

  // ---------- expressions, set terms, formulas (tiny ASTs) ----------
  const V = n => ({ t: 'var', n });
  const K = v => ({ t: 'num', v });
  const MOD = (l, r) => ({ t: 'mod', l, r });
  const Div = e => ({ t: 'Div', e });
  const CD = (e1, e2) => ({ t: 'CD', e1, e2 });
  const TRUE = { t: 'true' };
  const CMP = (op, l, r) => ({ t: 'cmp', op, l, r });
  const SETEQ = (l, r) => ({ t: 'seteq', l, r });
  const SETSUB = (l, r) => ({ t: 'setsub', l, r });   // l ⊆ r
  const AND = (...fs) => ({ t: 'and', fs });
  const NOT = f => ({ t: 'not', f });

  function pe(e) {
    switch (e.t) {
      case 'var': return e.n;
      case 'num': return String(e.v);
      case 'mod': return pe(e.l) + ' mod ' + pe(e.r);
    }
  }
  function ps(s) { return s.t === 'Div' ? 'Div(' + pe(s.e) + ')' : 'CD(' + pe(s.e1) + ', ' + pe(s.e2) + ')'; }
  function pf(f) {
    switch (f.t) {
      case 'true': return 'true';
      case 'cmp': return pe(f.l) + ' ' + f.op + ' ' + pe(f.r);
      case 'seteq': return ps(f.l) + ' = ' + ps(f.r);
      case 'setsub': return ps(f.l) + ' ⊆ ' + ps(f.r);
      case 'and': return f.fs.map(pf).join(' ∧ ');
      case 'not': return '¬(' + pf(f.f) + ')';
    }
  }
  function subst(f, name, expr) {   // f[expr/name]
    const se = e => e.t === 'var' ? (e.n === name ? expr : e) : e.t === 'mod' ? MOD(se(e.l), se(e.r)) : e;
    const ss = s => s.t === 'Div' ? Div(se(s.e)) : CD(se(s.e1), se(s.e2));
    switch (f.t) {
      case 'true': return f;
      case 'cmp': return CMP(f.op, se(f.l), se(f.r));
      case 'seteq': return SETEQ(ss(f.l), ss(f.r));
      case 'setsub': return SETSUB(ss(f.l), ss(f.r));
      case 'and': return AND(...f.fs.map(g => subst(g, name, expr)));
      case 'not': return NOT(subst(f.f, name, expr));
    }
  }

  // ---------- the trusted base: an evaluator over a bounded domain ----------
  function makeDomain(N) {
    if (N > 32) throw new Error('N must be <= 32 (divisor bitmasks)');
    const W = N + 1, M = W * W;
    const divmask = new Int32Array(W);
    divmask[0] = -1;                                   // every d divides 0
    for (let v = 1; v <= N; v++) { let m = 0; for (let d = 1; d <= N; d++) if (v % d === 0) m |= (1 << (d - 1)); divmask[v] = m; }
    const idx = (x, y) => y * W + x;
    const xy = i => [i % W, (i / W) | 0];

    // evaluation; `undefined` means the primitive is not defined here (a trap)
    function ev(e, s) {
      switch (e.t) {
        case 'var': return s[e.n];
        case 'num': return e.v;
        case 'mod': { const l = ev(e.l, s), r = ev(e.r, s); if (l === undefined || r === undefined || r === 0) return undefined; return l % r; }
      }
    }
    function evset(st, s) {
      if (st.t === 'Div') { const v = ev(st.e, s); return v === undefined ? undefined : divmask[v]; }
      const p = ev(st.e1, s), q = ev(st.e2, s); if (p === undefined || q === undefined) return undefined; return divmask[p] & divmask[q];
    }
    function holds(f, s) {
      switch (f.t) {
        case 'true': return true;
        case 'cmp': { const l = ev(f.l, s), r = ev(f.r, s); if (l === undefined || r === undefined) return false;
          return f.op === '=' ? l === r : f.op === '≠' ? l !== r : f.op === '<' ? l < r : f.op === '≤' ? l <= r : f.op === '>' ? l > r : l >= r; }
        case 'seteq': { const l = evset(f.l, s), r = evset(f.r, s); return l !== undefined && l === r; }
        case 'setsub': { const l = evset(f.l, s), r = evset(f.r, s); return l !== undefined && r !== undefined && (l & ~r) === 0; }
        case 'and': return f.fs.every(g => holds(g, s));
        case 'not': return !holds(f.f, s);
      }
    }
    // a type, as a set of states, for fixed parameters a, b
    function setOf(f, a, b) {
      const S = new Uint8Array(M), s = { a, b, x: 0, y: 0 };
      for (let i = 0; i < M; i++) { s.x = i % W; s.y = (i / W) | 0; if (holds(f, s)) S[i] = 1; }
      return S;
    }
    function strip(f, a, b) {   // a set of result values r
      const S = new Uint8Array(W), s = { a, b, r: 0 };
      for (let r = 0; r <= N; r++) { s.r = r; if (holds(f, s)) S[r] = 1; }
      return S;
    }
    const subset = (A, B) => { const bad = []; for (let i = 0; i < M; i++) if (A[i] && !B[i]) bad.push(i); return bad; };
    const equal = (A, B) => { const bad = []; for (let i = 0; i < M; i++) if (A[i] !== B[i]) bad.push(i); return bad; };
    const inter = (A, B) => { const C = new Uint8Array(M); for (let i = 0; i < M; i++) C[i] = A[i] & B[i]; return C; };
    const count = A => { let c = 0; for (let i = 0; i < A.length; i++) c += A[i]; return c; };
    // exact image of a set under a simultaneous assignment; records states where it is undefined
    function image(targets, exprs, A, a, b) {
      const out = new Uint8Array(M), bad = [], s = { a, b, x: 0, y: 0 }, map = new Int32Array(M).fill(-1);
      for (let i = 0; i < M; i++) if (A[i]) {
        s.x = i % W; s.y = (i / W) | 0;
        const vals = exprs.map(e => ev(e, s));
        if (vals.some(v => v === undefined || v < 0 || v > N)) { bad.push(i); continue; }
        const t = { x: s.x, y: s.y }; targets.forEach((n, k) => t[n] = vals[k]);
        const j = idx(t.x, t.y); out[j] = 1; map[i] = j;
      }
      return { out, bad, map };
    }
    return { N, W, M, idx, xy, divmask, ev, holds, setOf, strip, subset, equal, inter, count, image };
  }

  // ---------- the five rules, as a checker over an explicit derivation ----------
  // node shapes:
  //  {rule:'FUN', name, params:['a','b'], result:{v:'r', q}, ret: expr, body}
  //  {rule:'SEQ', first, second}
  //  {rule:'ASSIGN', in: formula, targets:[..], exprs:[..]}
  //  {rule:'SUB', inner, out: formula}
  //  {rule:'WHILE', in: formula (invariant I), guard: formula, measure: expr, body}
  function declaredIn(n) { return n.rule === 'SEQ' ? declaredIn(n.first) : n.rule === 'SUB' ? declaredIn(n.inner) : n.in; }

  // run a loop-free derivation as a function on sets (used for the measure premise)
  function apply(D, n, A, a, b) {
    switch (n.rule) {
      case 'ASSIGN': return D.image(n.targets, n.exprs, A, a, b).out;
      case 'SUB': return apply(D, n.inner, A, a, b);
      case 'SEQ': return apply(D, n.second, apply(D, n.first, A, a, b), a, b);
      default: throw new Error('measure premise: loop body must be loop-free in this calculus');
    }
  }

  let nid = 0;
  function check(D, node, a, b) {
    nid = 0;
    const recs = [];
    function rec(n, parentIn) {
      const r = { id: ++nid, node: n, rule: n.rule, premises: [], children: [] };
      recs.push(r);
      const P = (kind, text, bad, extra) => { const p = Object.assign({ kind, text, ok: bad.length === 0, bad, trusted: true }, extra || {}); r.premises.push(p); return p; };
      switch (n.rule) {
        case 'ASSIGN': {
          r.in = D.setOf(n.in, a, b);
          const im = D.image(n.targets, n.exprs, r.in, a, b);
          r.out = im.out; r.map = im.map;
          P('defined', n.targets.join(', ') + ' := ' + n.exprs.map(pe).join(', ') + ' is defined on every state of ' + pf(n.in), im.bad);
          r.text = 'ASSIGN: the output type is the exact image of the input type';
          break;
        }
        case 'SEQ': {
          const f = rec(n.first, parentIn), s = rec(n.second, null);
          r.children = [f, s]; r.in = f.in; r.out = s.out;
          P('dock', 'output of the first part = input of the second: ' + pf(declaredIn(n.second)), D.equal(f.out, s.in));
          r.text = 'SEQ: two pictures share one panel';
          break;
        }
        case 'SUB': {
          const c = rec(n.inner, parentIn); r.children = [c];
          r.in = c.in; r.out = D.setOf(n.out, a, b); r.have = c.out;
          P('subset', 'what we have ⊆ what we claim: ' + pf(n.out), D.subset(c.out, r.out));
          r.text = 'SUB: a smaller set may be read as a larger one';
          break;
        }
        case 'WHILE': {
          r.in = D.setOf(n.in, a, b);
          const G = D.setOf(n.guard, a, b), notG = D.setOf(NOT(n.guard), a, b);
          r.cont = D.inter(r.in, G); r.out = D.inter(r.in, notG);
          const body = rec(n.body, null); r.children = [body];
          P('dock', 'the body starts from I ∧ guard: ' + pf(n.in) + ' ∧ ' + pf(n.guard), D.equal(r.cont, body.in));
          P('dock', 'the body ends back inside I: ' + pf(n.in), D.equal(body.out, r.in));
          // measure: for every stratum m = k, the image of the body lies strictly below
          const bad = [], pairs = [], s = { a, b, x: 0, y: 0 };
          const strat = new Uint8Array(D.M);
          for (let k = 0; k <= D.N; k++) {
            let any = false; strat.fill(0);
            for (let i = 0; i < D.M; i++) if (r.cont[i]) { s.x = i % D.W; s.y = (i / D.W) | 0; if (D.ev(n.measure, s) === k) { strat[i] = 1; any = true; } }
            if (!any) continue;
            const img = apply(D, n.body, strat, a, b);
            for (let j = 0; j < D.M; j++) if (img[j]) { s.x = j % D.W; s.y = (j / D.W) | 0; const m2 = D.ev(n.measure, s); pairs.push([k, m2]); if (!(m2 < k)) bad.push([k, m2]); }
          }
          r.measurePairs = pairs;
          P('measure', 'the measure ' + pe(n.measure) + ' strictly decreases across the body (for every row k, the image lies below k)', bad);
          r.text = 'WHILE: a set closed under the body, entered through the guard, left through its negation';
          break;
        }
        case 'FUN': {
          const U = D.setOf(TRUE, a, b);
          const body = rec(n.body, U); r.children = [body];
          r.in = U; r.out = D.setOf(subst(n.result.q, n.result.v, n.ret), a, b);
          r.strip = D.strip(n.result.q, a, b);
          P('dock', 'the body starts from the parameters alone (every state)', D.equal(U, body.in));
          P('dock', 'the body ends in the result type read through "return ' + pe(n.ret) + '": ' + pf(subst(n.result.q, n.result.v, n.ret)), D.equal(body.out, r.out));
          r.text = 'FUN: the contract is the type of the body, read through the return expression';
          break;
        }
      }
      r.ok = r.premises.every(p => p.ok) && r.children.every(c => c.ok);
      return r;
    }
    const root = rec(node, null);
    return { root, recs, ok: root.ok, a, b };
  }

  // ---------- running the program (evidence, not proof) ----------
  function trace(D, node, a, b, limit) {
    const steps = []; const s = { a, b, x: 0, y: 0 }; limit = limit || 500;
    function go(n) {
      if (steps.length > limit) return;
      switch (n.rule) {
        case 'FUN': steps.push({ at: n, slot: 'in', s: { ...s } }); go(n.body); if (!steps.trapped) steps.push({ at: n, slot: 'out', s: { ...s }, r: D.ev(n.ret, s) }); break;
        case 'SEQ': go(n.first); if (!steps.trapped) go(n.second); break;
        case 'SUB': go(n.inner); if (!steps.trapped) steps.push({ at: n, slot: 'sub', s: { ...s } }); break;
        case 'ASSIGN': { const vals = n.exprs.map(e => D.ev(e, s)); if (vals.some(v => v === undefined)) { steps.push({ at: n, slot: 'trap', s: { ...s } }); steps.trapped = true; return; }
          n.targets.forEach((t, k) => s[t] = vals[k]); steps.push({ at: n, slot: 'out', s: { ...s } }); break; }
        case 'WHILE': {
          let lap = 0;
          for (;;) {
            steps.push({ at: n, slot: 'head', s: { ...s }, lap });
            if (steps.trapped || steps.length > limit) return;
            if (D.holds(n.guard, s)) { const k = D.ev(n.measure, s); steps.push({ at: n, slot: 'cont', s: { ...s }, lap }); go(n.body); if (steps.trapped) return; steps.push({ at: n, slot: 'measure', s: { ...s }, k, k2: D.ev(n.measure, s), lap }); lap++; }
            else { steps.push({ at: n, slot: 'exit', s: { ...s }, lap }); break; }
          }
          break;
        }
      }
    }
    go(node);
    return steps;
  }

  // ---------- Euclid, and the seeded mistakes ----------
  const x = V('x'), y = V('y'), a = V('a'), b = V('b'), r = V('r');
  const I_good = SETEQ(CD(x, y), CD(a, b));                 // the common divisors never change
  const Q = SETEQ(Div(r), CD(a, b));                        // the result type: Div(r) = CD(a, b)
  function euclid(opts) {
    opts = opts || {};
    const I = opts.inv || I_good;
    const guard = opts.guard || CMP('≠', y, K(0));
    const ret = opts.ret || x;
    return {
      rule: 'FUN', name: 'gcd', params: ['a', 'b'], result: { v: 'r', q: Q }, ret,
      body: {
        rule: 'SEQ',
        first: { rule: 'SUB', out: I, inner: { rule: 'ASSIGN', in: TRUE, targets: ['x', 'y'], exprs: [a, b] } },
        second: {
          rule: 'SUB', out: subst(Q, 'r', ret),
          inner: {
            rule: 'WHILE', in: I, guard, measure: y,
            body: { rule: 'SUB', out: I, inner: { rule: 'ASSIGN', in: AND(I, guard), targets: ['x', 'y'], exprs: [y, MOD(x, y)] } }
          }
        }
      }
    };
  }
  const seeds = {
    ok:    { title: 'correct', kind: 'none', what: 'Euclid as written', build: () => euclid() },
    retY:  { title: 'return y', kind: 'code bug', what: 'the function returns y (always 0 at exit) instead of x', build: () => euclid({ ret: y }) },
    weak:  { title: 'weak invariant', kind: 'spec bug', what: 'invariant keeps only one direction, CD(a,b) ⊆ CD(x,y): true at every lap, but it does not pin the exit down', build: () => euclid({ inv: SETSUB(CD(a, b), CD(x, y)) }) },
    guardX:{ title: 'guard on x', kind: 'code bug', what: 'the loop tests x ≠ 0 instead of y ≠ 0, so x mod y can be asked with y = 0', build: () => euclid({ guard: CMP('≠', x, K(0)) }) },
    strong:{ title: 'strong invariant', kind: 'spec bug', what: 'invariant adds y ≤ x: preserved by the body, but false on entry whenever a < b', build: () => euclid({ inv: AND(I_good, CMP('≤', y, x)) }) },
  };

  // check every slice (a, b) of the domain
  function checkAll(D, node) {
    let failures = [], applications = 0, leaves = 0;
    for (let a = 0; a <= D.N; a++) for (let b = 0; b <= D.N; b++) {
      const res = check(D, node, a, b);
      if (a === 0 && b === 0) { applications = res.recs.length; leaves = res.recs.reduce((c, r) => c + r.premises.length, 0); }
      if (!res.ok) failures.push([a, b]);
    }
    return { slices: (D.N + 1) * (D.N + 1), failures, applications, leaves };
  }

  return { V, K, MOD, Div, CD, TRUE, CMP, SETEQ, SETSUB, AND, NOT, pe, pf, ps, subst, makeDomain, check, checkAll, trace, apply, declaredIn, euclid, seeds, I_good, Q };
})();
if (typeof module !== 'undefined') module.exports = Calc;
