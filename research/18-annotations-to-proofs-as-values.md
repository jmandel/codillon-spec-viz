# 18 — From annotations to proofs as values: why v1 was replaced

Coordinator note, 2026-10-24. Version 1 of Refined Codillon (research 01–14, the walkthrough
`artifacts/00-refined-codillon.html`, the editor at `editor/`, fork branch `refined`) is the record of the first
iteration. Version 2 (research 15–17, `v2-examples/`, the editor at `editor/v2/`, fork branch `proofs`) replaces its
core. This note says what v1 got right, where it bent Codillon out of shape, what v2 changes, what v2 costs, and what
is not done yet.

## 1. What v1 did well

- **The six-state model.** Refuted and replayed; refuted, not yet replayed; held on this run only; assumed or vacuous;
  unknown; proven (05, 08). Every prototype had to keep these apart, and the rule that "held on this run" must never
  look like "proven" survives into v2 unchanged.
- **A real editor, not a mock-up.** The fork parsed `(T | P)` types, `(@requires …)`, `(@invariant …)`,
  `(@decreases …)` and `(@assume …)`, erased them from the binary, checked them at run time on every keystroke, and
  searched edge inputs for counterexamples. Seeded bugs from 03 showed up as live states with deep links
  (`artifacts/real-editor.html`).
- **Proofs in the browser.** Z3, compiled single-threaded to WebAssembly and run in a worker, decided the verification
  conditions. Across the examples that was 419 obligations: 398 proven, 20 refuted, 1 undecided (on purpose).
  A refuted obligation came back with the solver's model, decoded into a state and, for function-entry states,
  replayed on the slider.

The design questions v1 answered (what to draw always, on failure, and on selection) still stand. What changed is the
logic underneath.

## 2. What v1 bent

- **A second language beside the dataflow.** Codillon's idea is that dataflow is visible: inputs are cups, outputs
  are shapes, curves join them. v1 added a separate predicate language (`0 <= v && v * v <= n`) with its own syntax,
  its own variables and its own reading of integers, and handed it to Z3. The program and its spec lived in two
  languages that met only inside the solver.
- **Proof wires only on hover.** Why a load was safe was a fact the solver knew, not something on screen. The
  prototypes drew the justifying facts only when the student hovered or selected a line, because there was no
  object in the program to point a wire at.
- **Solver timeouts.** "Unknown" was a real state. Z3 could give up on nonlinear arithmetic or quantifiers, and the
  answer depended on a resource budget: the same text could be proven on one machine and undecided on another.
  An indigo `?` is honest, but it is not something a student can fix by reading the code.
- **Unreachable loop-head witnesses.** A failed "invariant preserved" obligation returns a model of the loop head
  that satisfies the invariant and breaks it after one iteration. Often no real run ever reaches that state; it shows
  that the invariant is too weak, not that the code is wrong. v1 drew these as "contract states, possibly
  unreachable", which is correct and hard to explain to a beginner.
- **No boundary between spec and proof.** In v1 the `@invariant`, a `@use` hint and the function contract were all
  annotations. For an LLM writing code and proofs against a student's spec, nothing in the syntax said which lines
  were the claim and which were the evidence, so nothing could stop a model from weakening the claim to make the
  evidence go through.

## 3. What v2 changes

Research 15 is the argument; research 16 is the design. In one line each:

- **Facts are dataflow you can point to.** A comparison followed by `if` or `br_if` gives each arm a fact
  (after `local.get $r`, `i32.const 65535`, `i32.ge_u`, the taken edge of `br_if` knows `u($r) ≥ 65535` and the fall-through knows the negation). Facts travel in a separate **fact lane**, not on the
  operand stack, so ordinary lines keep their stack effect and erase line for line. Every proposition an instruction
  needs is a **proof cup**, fed by exactly one fact: the output of a `prove` line just above, or an exact match in the
  lane. Every feed is a wire, always on. A missing proof is an empty cup, which Codillon already draws for a missing
  operand.
- **Block types are invariants.** A loop's block type carries a `(fact …)`, and every back-edge must supply it. A
  refined function type is the contract. There is no `@invariant`, `@requires` or `@ensures`; refined block and
  function types are the only spec syntax.
- **`unreachable` consumes False.** A functional spec is an ordinary Wasm harness that calls the function, computes a
  check (in i64, so the check itself cannot overflow), and branches past an `unreachable` when the check passes.
  Proving that every `unreachable` is fed a proof of False is proving the spec for all inputs; running the harness on
  concrete inputs is a test of the same text.
- **`prove k` instead of search.** `prove k` takes the `k` most recent lane entries and proves the goal of the cup
  it feeds, using a small decision procedure for linear integer arithmetic with explicit wrap variables (§3 of 16).
  It has fixed caps on terms, variables, atoms and cases. Nonlinear facts beyond monomials are lemmas.
- **Predicates and lemmas are Wasm functions.** A predicate is a pure, total, loop-free function returning i32; a
  lemma is an erased function with fact parameters and fact results; an axiom is a lemma with no body, marked
  *assumed*. Measures for recursive predicates are ordinary functions too.
- **A kernel with no "unknown".** The kernel does not ask whether a proposition is true. It asks whether the text
  contains a derivation, which is decided by lookup, bounded evaluation and §3 within its caps. Each cup ends
  **proven**, **refuted** (only with a concrete witness), **runtime-checked** (unfed; gradual mode compiles it into a
  check) or **assumed**, plus a "relative to checks at lines …" mark. A failed `prove` is a line that failed, with a
  countermodel or a named cap. There is no Z3 and no SMT anywhere in v2.
- **A boundary for vericoding.** The student owns headers, predicates, measures, harnesses and axioms; the LLM (or a
  scripted session) owns bodies, proof lines and lemmas. A submission is accepted only if every function it touched
  is strict-clean (16 §7).

The loop-head witness problem goes away with the search: there are no counterexamples-to-induction, only cups that a
line does or does not feed, and runtime checks whose failures are real runs.

## 4. What v2 costs

- **Proof lines to write.** v1's Z3 found the arithmetic on its own; v2 asks for a `prove k` at each step the
  kernel cannot get by lookup. The examples need four to six `prove` lines per intro function (parity, isqrt, the gcd
  loop). Primality needs measures, an induction lemma and three instructor axioms, and is capstone material, not
  intro material.
- **A positional `prove k`.** The hypotheses are the `k` most recent lane entries. Inserting an unrelated `call` or
  `br_if` between a fact and its `prove` silently changes which facts are taken; `isqrt-wrong-cup.wat` is a two-line
  swap that breaks the proof. Mitigations: every failure lists the hypotheses actually taken, hypotheses are drawn as
  wires, and fact handles (`local.set $h` / `local.get $h`) re-cite older facts. Explicit references
  (`prove @14 @22`) remain an open question (16 §9 Q1).
- **No memory frame rules.** After a store, facts about memory-reading predicates are gone; nothing says "this store
  does not touch slot j". In the hash table, 7 of 29 cups (the representation invariant across stores) are
  runtime-checked for that reason, or need an instructor axiom.
- **No termination for ordinary code.** v2 proves partial correctness: no trap on any input that meets the entry
  contract, except call-stack exhaustion. Predicates, measures and lemmas must be total; ordinary loops and recursion
  are not proven to terminate. v1 at least had `(@decreases …)`.
- **Less automation means more failures shown.** The kernel never answers "unknown", but it also never succeeds on a
  fact that the text does not derive. A true fact that is too expensive to evaluate, or past a cap, is a failed line
  with a named cap; the fix is a lemma.

## 5. The same isqrt in both versions

v1, from `03-sample-programs.md` §A2: a refined signature, two annotations in the loop, and Z3 for the rest.

```wat
  1  (func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v <= n && n < (v + 1) * (v + 1)))
  2    (local $r i32)
  3    i32.const 0
  4    local.set $r
  5    block $done
  6      loop $grow
  7        (@invariant 0 <= r && r * r <= n)
  8        (@decreases n - r * r)
  9        local.get $r
 10        i32.const 1
 11        i32.add
 12        local.get $r
 13        i32.const 1
 14        i32.add
 15        i32.mul
 16        local.get $n
 17        i32.gt_u
 18        br_if $done
 19        local.get $r
 20        i32.const 1
 21        i32.add
 22        local.set $r
 23        br $grow
 24      end
 25    end
 26    local.get $r
 27  )
```

v2, from `v2-examples/isqrt.wat` (the predicates `$sq_le` and `$is_isqrt` are ordinary i64 Wasm functions defined
above it in the file). The spec is the result type and the harness; the loop invariant is the loop's block type; the
proof is five `prove` lines.

```wat
(func $isqrt (export "isqrt") (param $n i32) (result (i32 | (call $is_isqrt (i64.extend_i32_u v) (i64.extend_i32_u $n))))
  (local $r (i32 | (i32.le_u v 65535)))
  block $done (fact (call $is_isqrt (i64.extend_i32_u $r) (i64.extend_i32_u $n)))
    prove 0
    loop $grow (fact (call $sq_le (i64.extend_i32_u $r) (i64.extend_i32_u $n)))
      local.get $r
      i32.const 65535
      i32.ge_u
      prove 2
      br_if $done
      local.get $r
      i64.extend_i32_u
      i64.const 1
      i64.add
      local.get $r
      i64.extend_i32_u
      i64.const 1
      i64.add
      i64.mul
      local.get $n
      i64.extend_i32_u
      i64.gt_u
      prove 2
      br_if $done
      local.get $r
      i32.const 1
      i32.add
      prove 2
      local.set $r
      prove 3
      br $grow
    end
  end
  local.get $r
)
(func $isqrt_harness (export "harness:isqrt") (param $n i32)
  local.get $n
  call $isqrt
  i64.extend_i32_u
  local.get $n
  i64.extend_i32_u
  call $is_isqrt
  br_if 0
  prove 2
  unreachable
)
```

What the comparison shows:

- v1's overflow trap (`(r+1)*(r+1)` in i32 at `r = 46340`, and the signed-compare bug S1) was a solver obligation.
  v2 computes the square in i64 and keeps `$r` refined to `≤ 65535`, so the facts that matter are visible on lines
  and the kernel checks each step separately. The early exit at 65535 is the price of that refinement.
- v1's invariant was a comment-like annotation; v2's is the loop's type, and the `prove 3` before `br $grow` is the
  evidence that the back-edge supplies it.
- v2 reads `n` unsigned throughout, so the precondition `0 <= n` disappears.
- The v2 version is longer by about ten lines, all of them proof lines or i64 widening. That is the cost in §4.
- `isqrt-harness-bug.wat` computes the harness check in i32 and is refuted at n = 2³²−1; the spec bug is a run, not
  a solver model.

## 6. The review loop that hardened v2

Two independent reviews by a second model (Fable) ran against the design and then against the kernel while each was
being written. Both are kept in full.

**Design review** (`16-review-fable.md`). Found four soundness holes and a set of under-specifications; each was a
card change, not a new mechanism:

- *Mutable globals:* predicates may not read a mutable global (purity), so a predicate fact cannot go stale silently.
- *Loops and globals:* loop heads φ-rename every global set in the body, as they already did for locals.
- *`prove` past `br_if`:* a `prove` that feeds a taken-edge cup puts its fact on that edge only, not on the fall-through.
- *Division by zero in virtual terms:* a virtual `rem_u`/`div_u` is guarded by `B = 0 ∨ r < B`, and a constant
  divisor 0 is an opaque leaf.
- *`shr_s`, wrap ranges, expansion order:* `shr_s` by a constant is floor division; wrapped terms are constrained to
  their width; wrap variables are resolved before products are expanded (otherwise i64 `(r+1)²` overflows the
  coefficients).
- *Relative to checks:* a fact downstream of a runtime-checked cup carries `depends_on_checks` and is never drawn as
  plain proven; a function is VERIFIED only if strict-clean.
- *Positional `prove`:* every failure prints the hypotheses it actually took.

**Kernel review** (`17-kernel-review-fable.md`). Read every commit on branch `proofs`, ran about 65 adversarial
functions and fuzzed the decision procedure against exhaustive 8-bit evaluation. Five blocking findings, all fixed
and regression-tested:

- **B1** — `prove` hung forever on any product of two variables (zero coefficients broke the elimination loop).
- **B2** — a sign error in a bound-tightening step proved `x − 1 < x` with no hypotheses (false at x = 0).
- **B3** — an empty `br_table` (a half-typed line) panicked the kernel.
- **B4** — a recursive predicate whose measure returned nothing got no measure cup, so non-termination passed.
- **B5** — the virtual `rem_u` guard did not cover the result's range; settled as "a fact holds iff it evaluates
  without trapping".

After the fixes: the oracle (13 hand-derived examples, 201 cups) matches 201/201 and the test asserts it; the
decision procedure is 0/700 unsound across two fuzz seeds and deterministic. Open non-blocking items include `assume`
being accepted inside a predicate (N4), strict mode not yet reporting unfed cups as errors at the API (N5), and
runtime checks that could not run being silent (N14).

## 7. What is not done yet

- **Visualization (phase D) is in progress.** The kernel runs on every keystroke in `editor/v2/` and runtime checks
  are compiled into the instrumented binary, but the v2 drawing (proof cups, always-on wires, fraying fact chips, the
  False cup) is being built and is not described here.
- **Vericoding (phase E) is designed, not built.** The ownership lock, the adequacy panel (vacuity and six mutation
  operators) and scripted or live LLM sessions exist only in 16 §7.
- **Study materials (phase F) are partly revised.** This note, the synthesis update and the landing page are done; a
  v2 walkthrough and a v2 gcd section are not.
- **External review (phase G)** of v2 (a third model and real-editor QA) has not happened.
- **Open design questions** remain in 16 §9: explicit hypothesis references for `prove`, frame rules for memory, ghost
  integers, congruence for opaque terms, and how instructor axioms would be bridged to Lean.
- **The theorem is partial.** No termination for ordinary code, call-stack exhaustion carved out, floats opaque,
  no `call_indirect` or `memory.grow`.

v1 is not deleted. Its editor stays at `editor/` (branch `refined`), and its walkthrough, prototypes and synthesis
remain the record of the first iteration.
