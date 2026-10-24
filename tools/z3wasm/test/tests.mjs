// Shared test cases for Node and the browser worker. Each case: {id, desc, smt, check(out) -> bool}
function pigeonhole(p, h) {
  let s = '(set-logic QF_UF)\n';
  for (let i = 0; i < p; i++) for (let j = 0; j < h; j++) s += `(declare-const x_${i}_${j} Bool)\n`;
  for (let i = 0; i < p; i++) s += `(assert (or ${Array.from({ length: h }, (_, j) => `x_${i}_${j}`).join(' ')}))\n`;
  for (let j = 0; j < h; j++) for (let i = 0; i < p; i++) for (let k = i + 1; k < p; k++)
    s += `(assert (or (not x_${i}_${j}) (not x_${k}_${j})))\n`;
  return s;
}

const N = 16; // bound for (f)
const fBody = (quant) => `
(set-logic ${quant ? 'AUFLIA' : 'QF_AUFLIA'})
(declare-const a (Array Int Int))
${quant
  ? `(assert (forall ((i Int)) (! (=> (and (<= 0 i) (< i ${N})) (= (select a i) (* 3 i))) :pattern ((select a i)))))`
  : Array.from({ length: N }, (_, i) => `(assert (= (select a ${i}) ${3 * i}))`).join('\n')}
(declare-const k Int)
(assert (and (<= 0 k) (< k ${N - 1})))
(push)
; unsat goal: consecutive entries differ by 3
(assert (not (= (- (select a (+ k 1)) (select a k)) 3)))
(check-sat)
(pop)
(push)
; sat goal: some entry equals 21, get a model for k
(assert (= (select a k) 21))
(check-sat)
(get-value (k))
(pop)
`;

export const tests = [
  {
    id: 'a', desc: 'QF_BV sat + get-model + get-value',
    smt: `(set-logic QF_BV)
(declare-const x (_ BitVec 32))
(declare-const y (_ BitVec 32))
(assert (= (bvadd x y) #x0000000a))
(assert (bvugt x #x00000003))
(assert (= (bvand x #x00000001) #x00000001))
(assert (= (bvmul x y) #x00000015))
(check-sat)
(get-model)
(get-value (x y))`,
    check: (o) => /^sat/.test(o) && /define-fun x/.test(o) && /\(\(x #x[0-9a-f]{8}\)/.test(o),
  },
  {
    id: 'b', desc: 'QF_LIA unsat (parity) + push/pop',
    smt: `(set-logic QF_LIA)
(declare-const x Int)
(declare-const y Int)
(assert (> x 0))
(push)
(assert (= (+ (* 2 x) (* 4 y)) 7))
(check-sat)
(pop)
(push)
(assert (= (+ (* 2 x) (* 4 y)) 8))
(assert (< y 0))
(check-sat)
(get-value (x y))
(pop)`,
    check: (o) => /^unsat\s+sat\s+\(\(x \d+\)/.test(o),
  },
  {
    id: 'c', desc: 'QF_ABV byte memory: little-endian store/load word, model',
    smt: `(set-logic QF_ABV)
(declare-const mem (Array (_ BitVec 32) (_ BitVec 8)))
(declare-const p (_ BitVec 32))
(declare-const w (_ BitVec 32))
(define-fun store32 ((m (Array (_ BitVec 32) (_ BitVec 8))) (a (_ BitVec 32)) (v (_ BitVec 32))) (Array (_ BitVec 32) (_ BitVec 8))
  (store (store (store (store m a ((_ extract 7 0) v)) (bvadd a #x00000001) ((_ extract 15 8) v))
         (bvadd a #x00000002) ((_ extract 23 16) v)) (bvadd a #x00000003) ((_ extract 31 24) v)))
(define-fun load32 ((m (Array (_ BitVec 32) (_ BitVec 8))) (a (_ BitVec 32))) (_ BitVec 32)
  (concat (select m (bvadd a #x00000003)) (concat (select m (bvadd a #x00000002)) (concat (select m (bvadd a #x00000001)) (select m a)))))
(define-fun mem2 () (Array (_ BitVec 32) (_ BitVec 8)) (store32 mem p w))
; unaligned overlapping read at p+2 must see the upper half of w and 2 old bytes
(assert (= (load32 mem2 (bvadd p #x00000002)) #xbeefcafe))
(assert (= (select mem (bvadd p #x00000004)) #xef))
(assert (bvult p #x00001000))
(check-sat)
(get-value (p w (select mem (bvadd p #x00000005))))
(push)
(assert (not (= (load32 mem2 p) w)))
(check-sat)
(pop)`,
    check: (o) => /^sat/.test(o) && /\(w #xcafe[0-9a-f]{4}\)/.test(o) && /\(\(select mem .*#xbe\)/.test(o) && /unsat\s*$/.test(o),
  },
  {
    id: 'd', desc: 'NIA: integer square root is unique (r*r<=n<(r+1)^2, s likewise => r=s)',
    smt: `(set-option :rlimit 50000000)
(set-logic QF_NIA)
(declare-const n Int)
(declare-const r Int)
(declare-const s Int)
(assert (<= 0 n))
(assert (<= (* r r) n))
(assert (< n (* (+ r 1) (+ r 1))))
(assert (<= (* s s) n))
(assert (< n (* (+ s 1) (+ s 1))))
(assert (not (= r s)))
(check-sat)
(get-info :reason-unknown)`,
    check: (o) => /^(unsat|unknown)/.test(o), // record which
  },
  {
    id: 'd2', desc: 'NIA: r*r<=n<(r+1)^2, 0<=n  =>  0<=r (r is the non-negative root)',
    smt: `(set-option :rlimit 50000000)
(set-logic QF_NIA)
(declare-const n Int)
(declare-const r Int)
(assert (<= 0 n))
(assert (<= (* r r) n))
(assert (< n (* (+ r 1) (+ r 1))))
(assert (< r 0))
(check-sat)`,
    check: (o) => /^(unsat|unknown)/.test(o),
  },
  {
    id: 'e', desc: 'rlimit-bounded pigeonhole PHP(11,10) -> unknown, then context still usable',
    smt: `(set-option :rlimit 2000000)\n${pigeonhole(11, 10)}(check-sat)\n(get-info :reason-unknown)\n(reset)\n(declare-const z Int)(assert (= z 5))(check-sat)`,
    check: (o) => /^unknown\s+\(:reason-unknown "[^"]*(resource|canceled)[^"]*"\)\s+sat/.test(o),
  },
  {
    id: 'f1', desc: `bounded forall over array, expanded (N=${N})`,
    smt: fBody(false),
    check: (o) => /^unsat\s+sat\s+\(\(k 7\)\)/.test(o),
  },
  {
    id: 'f2', desc: `bounded forall over array, as quantifier (N=${N})`,
    smt: '(set-option :rlimit 50000000)\n' + fBody(true),
    check: (o) => /^unsat\s+sat\s+\(\(k 7\)\)/.test(o) || /^unknown|^unsat\s+unknown/.test(o),
  },
  {
    id: 'h', desc: '(extra) wall-clock :timeout 300ms via POLLING_TIMER on PHP(11,10)',
    smt: `(set-option :timeout 300)\n${pigeonhole(11, 10)}(check-sat)\n(get-info :reason-unknown)`,
    check: (o) => /^unknown/.test(o),
  },
  {
    id: 'i', desc: '(extra) deep term: 20000-deep nested (+ 1 (+ 1 ...)) (stack depth)',
    smt: `(declare-const x Int)(assert (= x ${'(+ 1 '.repeat(20000)}0${')'.repeat(20000)}))(check-sat)(get-value (x))`,
    check: (o) => /^sat\s+\(\(x 20000\)\)/.test(o) || /^error:/.test(o),
  },
  {
    id: 'g', desc: 'error path: undeclared constant -> "error:" prefix',
    smt: `(declare-const q Int)(assert (> zz 1))(check-sat)`,
    check: (o) => /^error:/.test(o),
  },
];

export const statefulTests = [
  // run sequentially on one context: push/pop and declarations persist across eval() calls
  { smt: '(declare-const v Int)(push)(assert (> v 10))', check: (o) => o.trim() === '' },
  { smt: '(assert (< v 5))(check-sat)', check: (o) => /^unsat/.test(o) },
  { smt: '(pop)(assert (< v 5))(check-sat)(get-value (v))', check: (o) => /^sat\s+\(\(v /.test(o) },
];
