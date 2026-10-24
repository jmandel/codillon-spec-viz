# Input: the "proofs as Wasm values" design conversation (2026-10-24)

Pasted by the study's author from a separate Claude conversation. It is the design input for v2 (research 16 onward).
Decisions taken afterwards (2026-10-24): pivot to proofs-as-values; kernel-only checker (no Z3, no SMT anywhere in v2);
one core design for Codillon plus a vericoding mode on top; Hazel out of scope; an LLM (via OpenRouter) is optional and
the editor must work fully without it.

## 1. Extending Codillon with refinement types: proofs as Wasm values instead of @annotations

Codillon's best visual idea is dataflow you can see: each instruction's inputs are cups, outputs are shapes, and curves
connect them. The v1 study adds a separate predicate language on top of that and hands the logic to Z3. Proof wires were
only drawn on hover. If proofs are ordinary stack values made by instructions, that question disappears. Proofs simply are
dataflow. A load is safe because a visible curve runs from the comparison that justified it into the load's proof cup. A
missing proof is an empty cup, which Codillon already draws for a missing operand.

Wasm's own typing rules already contain the logic.
- `unreachable` is already absurdity. The validator treats code after unreachable, br, or return as stack-polymorphic: it
  can be typed at any type. If `unreachable` instead requires a proof of False, then "trap-free" means every unreachable
  is fed a proof that it can't be reached.
- Block types are already invariants and contracts. A loop with typed params gets those values on every back-edge, and
  `br $L` must supply them. Put a proposition in the loop's block type and it is the loop invariant. Refined function types
  are pre- and postconditions the same way. No @invariant or @ensures.
- Propositions come from comparisons students already write. `i32.lt_u` followed by `if` can hand the then-branch a proof
  of u($i) < u($n) and the else-branch its negation. Students never write predicate syntax inside code; the proposition is
  the type of a value, shown in the margin. The only place a proposition is written out is in a type, and even there it can
  be "this pure Wasm function returns nonzero" (like Lean's `decide`).

Checking becomes plain type checking: the editor checks a derivation rather than searching for one. Instant,
deterministic, local, no "unknown" state. Errors take one form: "this cup needs a proof of X and nothing feeds it." An LLM
can emit proof terms, and a fast trusted checker accepts or rejects them.

Precedent: Xi & Harper's Dependently Typed Assembly Language (index refinements on assembly, array bounds), ATS (proofs as
erased program terms), typed assembly language and proof-carrying code.

Sketch, division by a value that might be zero:

```wat
local.get $d
i32.eqz
if (result ‹$d ≠ 0›)   ;; then-arm receives ‹$d = 0›, else-arm receives ‹$d ≠ 0›
  i32.const 0
  return               ;; polymorphic after return: this arm owes nothing
else
end                    ;; ‹$d ≠ 0› flows out of the block
local.set $nz          ;; a proof-typed local, erased from the binary
local.get $n
local.get $d
local.get $nz
i32.div_u              ;; cups: i32, i32, ‹$d ≠ 0›
```

Two catches.
- Trap-freedom alone is too weak: Wasm arithmetic wraps rather than trapping. The only traps are integer division or
  remainder by zero and signed INT_MIN / −1; out-of-bounds memory; non-saturating float-to-int of NaN or out of range;
  indirect-call failures; unreachable; call-stack exhaustion. abs and isqrt can't trap; their bugs are wrong answers.
  It is also too easy: `if (i < n) load else return 0` is a valid proof. Fix: state functional specs as ordinary Wasm that
  ends in `unreachable` (call the function, compute the check, `br_if` past the `unreachable` when the check passes). Then
  "prove trap-freedom for all inputs" covers functional correctness; the harness runs on concrete inputs as a test and is
  proved for all inputs as a theorem. A harness check like r*r <= n in i32 can itself overflow (spec bugs), so use i64
  checks or a ghost unbounded type.
- Bookkeeping on a stack machine is heavy: (1) stack order (a proof pushed early sits under the operands it justifies; a
  separate lane for facts may read better than stack discipline); (2) mutable locals (a proof about $i goes stale at
  local.set $i; propositions should be about values, not variables — Xi's index variables; the editor shows a proof going
  invalid, like prototype 04's fraying fact ribbons); (3) arithmetic tedium: one instruction `prove k` consumes k proofs and
  produces the proof its consumer's cup asks for (goal from the cup, bidirectional), checked by a decision procedure for
  linear integer and bitvector arithmetic — Lean's `omega [h1, h2]` with the hypotheses as visible curves. Nonlinear facts
  need lemma functions: pure, total, erased, with their own proofs.
- Smaller: call-stack depth is implementation-defined (needs a recursion-depth model or carve-out); gradual mode: an
  instruction with an unfed proof cup falls back to a runtime check, drawn as an empty cup with a possible 💣.

Recommendation: proofs as values fed by comparison and branch evidence; refined block and function types as the only
spec syntax; `unreachable` consuming False, functional specs as Wasm harnesses; `prove k` backed by a decision procedure;
lemmas as erased pure functions. Keeps "one instruction per line, types are shapes, dataflow is curves" intact. "A crash
you've ruled out is a curve you can point to."

## 2. Checker data structures: flat vectors, no GC

At run time nothing new exists: refinements and automatic rules are erased; predicates are ordinary functions called only
when a fact is checked at run time. The checker's "types" look like trees but need not be stored as trees.

Terms are slots: a symbolic term is "this instruction applied to these input slots"; Codillon already records opcode and
input slots per line, so the term for an output slot is a pointer into the existing dataflow graph. Two slots can denote the
same term (two `local.get $a`, the same `i32.add` twice), so use value numbering: `local.get` takes the canonical id of the
slot that currently defines that local (param or last `local.set`); a pure instruction looks up (opcode, canonical input ids)
in a hash table cleared every pass. "Same term" = same id.

Facts are fixed-size records:

```rust
struct Slot  { ty: ValType, canon: SlotId, facts: Range<u32> }   // today's slot, plus two fields
struct Fact  { pred: FuncIdx, args: Range<u32>, origin: Origin } // args index into fact_args
struct Frame { /* existing control-frame fields */ fact_mark: u32, locals_mark: u32 }
fact_args: Vec<SlotId>
```

Lifetimes nest like a stack: (1) the whole pass (slots, canonical ids, hash table, birth facts) — an arena cleared each pass;
(2) until the end of a block (branch-narrowing facts on a fact stack; each control frame records the stack mark; at `end` cut
back and push the join result; the locals→defining-slot map is saved/restored per frame); (3) one check at one cup (unfolding,
substitution, evaluation, normalization in a scratch area reset per check). All because checking is a single forward pass
over nested blocks, with declared types at loop heads and no fixed-point iteration. Each function checked against other
functions' declared contracts; an edit re-checks only that function.

Bounds: polynomial normalization capped (e.g. 64 terms; past the cap the cup reports it and suggests a lemma; the cap is on
the rule card, deterministic). Coefficients are u32/u64 with Wasm wraparound (no bigints). Unfolding nested predicates:
value-number the scratch area so shared subterms are stored once; recursive predicates unfold one step at a time, only when
asked. Joins keep only facts present on every arm that falls through (intersection — can only shrink). Memory terms carry a
memory epoch; a store or call increments it; facts about loads from an older epoch are dropped unless from functions
declared stable. Each slot is ~16 bytes; facts per slot bounded by program text plus one round of automatic rules.

## 3. Example predicate: "i64 $n is prime"

```wat
;; $n is prime, reading $n as unsigned
(func $prime (param $n i64) (result i32)
  local.get $n
  i64.const 2
  i64.lt_u
  if (result i32)
    i32.const 0                  ;; 0 and 1 are not prime
  else
    local.get $n
    i64.const 2
    call $no_divisor_from        ;; cup on the 2: $at_least_2(2), decided by evaluation
  end)

;; no d' with $d ≤ d' and d'·d' ≤ $n divides $n
(func $no_divisor_from (param $n i64) (param $d (i64 | $at_least_2)) (result i32)
  local.get $d
  local.get $n
  local.get $d
  i64.div_u
  i64.gt_u
  if (result i32)                ;; d > n / d, i.e. d·d > n: no candidates left
    i32.const 1
  else
    local.get $n
    local.get $d
    i64.rem_u
    i64.eqz
    if (result i32)              ;; d divides n
      i32.const 0
    else
      local.get $n
      local.get $d
      i64.const 1
      i64.add
      call $no_divisor_from
    end
  end)

(func $at_least_2 (param $x i64) (result i32)
  local.get $x
  i64.const 2
  i64.ge_u)
```

Decisions visible: the signedness reading lives in lt_u/div_u/rem_u; the stopping test `d > n / d` avoids the overflow
of `d * d > n` (the isqrt trap, in a spec); recursion rather than a loop, because the kernel can unfold a recursive call one
step; a loop's meaning lives in an invariant.

Predicates must be total, trap-free, pure. Trap-freedom of div_u/rem_u: the refinement $at_least_2 on $d; $prime discharges
it by evaluating $at_least_2(2); the recursive call proves it for d+1 (needs d+1 not to wrap, from d < n). Termination: the
measure is an ordinary Wasm function registered by export-name convention, e.g. `(export "measure:no_divisor_from")`,
returning n − d read unsigned; at each recursive call the measure on the new arguments must be less (unsigned) than on the
current ones; (n − (d+1)) < (n − d) iff d < n, which follows from the else-arm fact d ≤ n/d, the refinement d ≥ 2 (so
n/d ≥ 2, n ≥ 4) and an axiom about i64.div_u (d ≥ 2, n ≥ 1 ⇒ n/d < n): two or three lemma calls.

How the checker uses $prime: constants decided by evaluation under a fixed step budget ("evaluation exceeded the budget" is a
visible, deterministic outcome; a fact can be true and too expensive to establish by evaluation). Branches narrow at run
time: `call $prime; if` gives the then-arm $prime($n). Unfolding: $prime is not recursive so it unfolds automatically; its
body contains an `if`, so unfolding produces a conditional term that reduces when facts or constants decide the condition.
$no_divisor_from is recursive: it unfolds one step, only when invoked explicitly.

Clear vs fast specs: $prime_spec (no divisor in [2, n), clear, slow) and $prime (stops at √n, fast), plus a lemma proving
they agree (real number theory; a good student project). Types use the fast one; the lemma connects it to the trusted one.
Deeper facts (Euclid's lemma) can be supplied by an instructor: prove once in Lean that the Wasm $prime agrees with Mathlib's
Nat.Prime on n.toNat; import selected facts as axioms backed by that bridge.

## 4. The plan (as approved)

A. design document (research 16); B. examples rewritten in v2 form with seeded bugs; C. kernel in the fork (branch
`proofs`), no Z3; D. visualization in Codillon's idiom (proof cups, always-on proof wires, fraying fact ribbons, False cup on
unreachable, `prove k` fractions, gradual mode with runtime checks, four states: proven / refuted / runtime-checked /
assumed); E. vericoding mode (ownership lock, adequacy panel for vacuous specs and surviving mutants, scripted LLM sessions,
optional live LLM via OpenRouter); F. revise study materials (v2 walkthrough, gcd v2 section, synthesis and landing page,
"from annotations to proofs as values" note; v1 kept as the first iteration); G. review (Gemini Argon via pi, real-editor QA).
