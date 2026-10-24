# Review of 16-v2-design.md (Refined Codillon v2) — independent reviewer (Fable)

Reviewed: `16-v2-design.md` (draft, §0–§9, ~11,100 words, mtime 12:10), `15-input-proofs-as-values.md`,
`v2-examples/parity*.wat|expect.json`, `v2-examples/tools/erase.py`, `run.mjs`. Written incrementally; the
"most important issues" list is kept current. Scratch checks live in `~/hobby/.agent-scratch/codalon-viz/v2review/`.

## Verdict

The pivot is right and the document is close to implementable: the fact lane, "exactly one feed per cup", declared
loop invariants with no fixed point, and the four verdict states are a coherent kernel with no search anywhere. The
rule cards cover every construct the parity example uses, and the erasure table is correct (the erased program has the
same meaning as the source, because no v2 construct touches the operand stack). I found **two concrete soundness holes**
(mutable globals read by pure/predicate functions are not keyed by any epoch, and loop heads do not φ-rename globals),
**one place where the design and its own example contradict each other** (§3.2 declares `shr_s` opaque, but
`parity.expect.json` line 36 is "proven" only if `shr_s` is interpreted), and a cluster of **under-specifications in §3**
that an implementer would otherwise have to guess (result-range constraints for wrapped terms, the order of wrap
resolution versus polynomial expansion, the variable cap 16 vs 24, the `vn` key being fixed at three operands). None of
these needs a new mechanism; each is a one-line card fix. The student-facing burden on parity is fine (four `prove`
lines); the real usability risk is the invisible "k most recent lane entries" rule, which is edit-fragile for both
students and the LLM loop. With the fixes below the design is ready for phase C.

## Most important issues (prioritized; details in §A–§E below)

1. **Soundness — mutable globals.** Predicates and "pure" functions may `global.get` a mutable global, but their call
   value-numbers and `Pred(...)` atoms carry no global state. Counterexample A1 proves `b ≠ 0` and then divides by zero.
   Fix: purity forbids reading mutable globals, or a global epoch is bumped by every `global.set`/impure call and keyed
   like the memory epoch.
2. **Soundness — loops and globals.** R8's loop-head pre-scan renames only locals; a `global.set` in the body leaves
   the pre-loop global id live on the next iteration (A2). Fix: pre-scan `global.set` targets (and impure calls) and
   φ-rename `curg` at loop heads, as for locals.
3. **Design/example contradiction — `shr_s`.** §3.2 lists `shr_s` as an opaque leaf; `parity.expect.json` and R3
   both assume `shr_s` by a constant is floor division of `s(·)`. Fix §3.2 (add the row with its σ variable), or `$half`
   cannot be proven.
4. **Spec gap — wrapped terms need result-range constraints.** §3.2 gives `add` as `A + B − 2ʷq, q ∈ [0,1]` with no
   `0 ≤ A + B − 2ʷq < 2ʷ`; without it `q` is free and even `x + 0 = x` fails (incompleteness, not unsoundness; but
   `$half`'s proof needs it). State: every term's linear form is constrained to its width range.
5. **Spec gap — order of wrap resolution versus expansion.** `(r+1)·(r+1)` in i64 expands to coefficients `2¹²⁸`
   (i128 overflow → `Cap(coefficients)`) unless the inner `q` is resolved to 0 *before* the product is expanded. Make
   the interval pass run bottom-up per term during Step 1, not after it.
6. **Propositions can trap / predicates with refined params used in propositions.** An inline `(fact (i64.div_u v $d))`
   or `(call $no_divisor_from v 0)` (whose `$d` is refined `≥ 2`) traps when evaluated (R28, R35). Nothing in the design
   discharges refined predicate params at proposition-instantiation sites, and R28 has no "trapped" outcome. Fix:
   predicates named in propositions must have unrefined params (total on the full domain) and inline `sexpr` may not
   contain `div`/`rem`/`trunc`; or give every proposition instantiation the callee cups.
7. **Verdict propagation at joins and call sites.** R8 enters `R[#φ]` and R13 enters callee result refinements as
   *proven* even when the cups that justify them are runtime-checked. Sound relative to checks (§6.1 says so), but the
   oracle marks `parity-bug-gate` line 49 and the harness `False` cup "proven" while the function is broken. Add a
   derived state ("proven, relative to checks at lines …") or carry a `depends_on_checks` flag so gradual mode does not
   show solid purple downstream of an empty cup.
8. **Oracle/runner mismatch.** `expect.json` `after_runs` claims a runtime check at line 46 is refuted by
   `half_or_neg1(3)`, but `run.mjs` runs the *erased* (uninstrumented) program, where that input reaches the harness's
   `unreachable` instead. Say which program the runner executes, or split `runs` into `erased` and `instrumented`.
9. **Implementability details.** `vn` key `[CanonId; 3]` cannot hold a call with 4+ arguments; §0 says 16 variables,
   §3.1 says 24; "32 atoms" must say whether side constraints count; the stack value at a join needs the same φ rule
   as locals (the example already uses `#φ` for the `if` result but R8 is about locals only); the handle table and `cur`
   for globals need per-frame save/restore like locals.
10. **Usability — "k most recent" is invisible and shifts.** Lookup-fed cups re-enter their atom (§5.2 "on success
    enter the fed atom"), so inserting an unrelated `call` or `br_if` between a hypothesis and its `prove` silently
    changes the hypotheses. Do not re-enter lookup-fed atoms; print the hypotheses actually taken in every `prove`
    failure; add the lane snapshot to the LLM round's `line_errors`.

## Contents

- A. Soundness probes (value numbering, joins/branches, memory and calls, wraparound, unfolding/measures, lemmas and
  axioms, exact match, erasure), each with a counterexample or an argument that none exists
- B. Completeness and implementability (coverage of the examples, data structures, one-pass algorithm, §3 determinism)
- C. Usability for students and the vericoding loop
- D. Consistency with 15 and the approved plan; internal consistency; the examples and oracles
- E. Prioritized fixes (one line problem, one line fix)
- F. Final pass notes (added when the examples README lands)

## A. Soundness probes

### A.1 Value numbering and staleness (R1, R6–R8, §1.5)

**Locals.** The core idea — facts are about canonical ids, `local.set` only rebinds `cur[$x]` — is sound and I could
not break it with sequential code. `local.tee` returns the input id, so a fact about the teed value stays valid; a later
`local.set $x` of a different value makes cups about the new value miss the old fact, which is the intended "stale"
behaviour. Two `local.get $a` produce the same id, correctly, because `cur` is unchanged in between.

**Loops.** The single `#φ` per assigned local at the head denotes "the value of `$x` on arrival in the current
iteration". Because the loop's `end` is not a join and back-edges only re-establish the declared invariant, no fact born
in iteration *n* about `#φ` can be read in iteration *n+1* with a different value: facts above the loop's `fact_mark`
are cut at the back-edge (they travel only on the edge, where they are discarded, R17). Facts below the mark mention
pre-loop ids, which stay true. Exit via `br_if $exit` snapshots the lane at that line, including facts about `#φ`, and
the `$exit` join keeps `$x ↦ #φ` if it is the only edge — that is the *last* iteration's value, which is what the facts
describe. Sound.

**Hole A2 — globals are not φ-renamed at loop heads.** R8's pre-scan collects `local.set`/`local.tee` targets only; R9
rebinds `curg` on `global.set` and on impure calls, but nothing renames `curg` at the head of a loop whose body sets the
global. Counterexample (v2 syntax, strict mode, every cup proven by the cards as written):

```wat
(global $g (mut i32) (i32.const 7))
(func $a2 (result i32)
  global.get $g          ;; #g0 (curg[$g] on entry)
  i32.eqz
  if (result i32)
    i32.const 0
  else                   ;; lane: ¬eq(#g0,0) = ne(#g0,0)
    loop $L
      i32.const 10
      global.get $g      ;; still #g0: nothing renamed curg at the loop head
      i32.div_u          ;; cup ne(#g0,0): lookup finds the else-arm fact — proven
      drop
      i32.const 0
      global.set $g      ;; curg[$g] := const 0, but only for the text below this line
      br $L              ;; no invariant cups: the loop declares none
    end
    unreachable          ;; dead after br, fed by False (R22)
  end)
```

The second iteration divides 10 by 0. Fix: the loop pre-scan also collects `global.set` targets and "contains an impure
call" (which rebinds every mutable global, R9), and allocates `#φ` for those globals exactly as for locals; a refined
global re-enters its refinement at the head.

**Hole A1 — pure functions and predicates may read mutable globals.** R29's purity list forbids `global.set` but not
`global.get` of a `(mut …)` global; R1 value-numbers a pure call by `(call $f, args, ε-if-reads-memory)`, and a
predicate atom `Pred($p, args)` carries no global state at all. Counterexample:

```wat
(global $g (mut i32) (i32.const 1))
(func $gnz (result i32)            ;; predicate "g ≠ 0": pure by R29's definition
  global.get $g)
(func $div_by_g (param $a (i32 | (call $gnz))) (result i32)
  local.get $a
  global.get $g
  i32.div_u                        ;; cup ne(#g,0): `prove 1` from the entry fact, unfolding $gnz — proven
)
(func $a1 (param $n i32) (result i32)
  call $gnz
  if (result i32)                  ;; then-arm: Pred($gnz)
    i32.const 0
    global.set $g                  ;; g := 0; no epoch, no renaming of anything Pred($gnz) depends on
    local.get $n
    call $div_by_g                 ;; cup Pred($gnz): exact lookup finds the then-arm fact — proven
  else
    i32.const 0
  end)
```

`$div_by_g(n)` divides by zero. (A variant without predicates: a pure non-predicate `$f` that returns `global.get $g`,
called twice around a `global.set`, gets one id for two different values, so any fact about the first result applies to
the second.) Fix, pick one: (a) "pure" and "predicate" additionally mean *reads no mutable global* (simplest; a module
that wants a global in a spec passes it as an argument); or (b) a **global epoch** `γ`, bumped by every `global.set`
and impure call, keyed into pure-call ids and `Pred@γ` atoms exactly like `ε`. R28 evaluation must then also exclude
global-reading predicates (it runs them in a fresh instance). I recommend (a) for v2; it also makes `curg` at function
entry irrelevant to proofs.

**Function entry for globals is unspecified.** R14 gives parameters fresh ids and locals `const 0`, but says nothing
about `curg` on entry (must be fresh per mutable global; a refined mutable global's refinement may be entered because
every `global.set` has a cup — but the *initializer* also needs a cup, not stated).

**Fact handles (§1.5).** "Still in scope" is defined by the fact's lifetime in the lane. Two things to pin down: (i) a
join *re-enters* kept facts "with origin = the `end` line" — if that allocates a new `FactId`, a handle bound inside an
arm to a fact that survived the join becomes an error after `end`, which is surprising but safe; if it keeps the
`FactId`, say so. (ii) `handles` is not saved/restored per frame in `FuncState`; a `local.set $h` in a then-arm that
is read in the else-arm must error ("ended at line N"), which the lifetime test gives for free only if the arm's facts
are really gone from `lane`, not just below a mark. Neither is a soundness hole; both are implementability gaps.

### A.2 Joins and branch facts (R4, R8, R16–R22)

**Branch atoms.** R4's rewrites are equivalences on integer comparisons; `¬lt → le(b,a)` is only valid for integer
orders, and R27's float cups must never pass through rules 1–3 (`¬f64.lt(a,b)` is *not* `f64.le(b,a)` with NaN). R4 lists
only `iNN` opcodes, but the `Head::FloatCmp` variant plus the `neg` flag means an implementer could apply the generic
negation table. Say explicitly: float atoms are stored with `neg` and never rewritten; rule 1 (gt→lt, ge→le) is fine
for floats, rule 3 is not.

**`eqz` of a predicate call.** parity relies on `call $is_even; i32.eqz; if` giving the then-arm `¬Pred` and the
else-arm `Pred`. Rule 2 says `eq(x,0)` for a *comparison* `x` → `¬x`; rule 4 handles predicate calls. The intended
reading (`eq(Pred-call, 0)` → `¬Pred`) is correct because `Pred` means "value ≠ 0", but it is not literally one of the
listed rewrites. Add it to rule 4.

**Intersection at joins** can only shrink and is taken over edges that are not dead, so `if … return end` keeps
`¬⟦c⟧`: correct. A block with **zero** incoming edges (every arm branches elsewhere) is handled only by accident: the
lane at `end` is the fall-through lane, which holds `False` (R22), and an intersection over zero edges keeps everything,
so the code after `end` is dead. That is the right answer, but state it as a rule ("no edges ⇒ the code after `end` is
dead") rather than relying on vacuous intersection; otherwise an implementer who initialises the intersection to the
first edge will panic on an empty list.

**Block results need φ too.** R8 is about locals, but a `block`/`if` with a `(result (T | R))` whose arms push
different ids must give the result value a fresh `#φ` and enter `R[v := #φ]` (the parity oracle already writes
`$hon_ok(#φ, $x)` on line 49). Add "the stack values of the frame's result arity are merged like locals".

**`br_if` taken edge.** The extra hypothesis `⟦c⟧` for a `prove` that feeds a taken-edge cup is sound (the cup is only
owed on the taken path). One subtlety: the `prove` sits *above* the `br_if` line, so its hypotheses "the `k` most recent
lane entries" are taken at the `prove` line while `⟦c⟧` is from the line below; the design says this, fine.

**`br_table`.** Per-edge atoms `eq(i, j)` / `ge_u(i, n)` are exactly Wasm's semantics; a label listed twice gets two
edges, each checked separately — sound and simple. Labels that are a `loop` get back-edge cups. OK.

**Join after `else` with a stored epoch.** Restoring `ε` at `else` and giving the join a fresh epoch when the arms
differ is sound; a load in the else-arm at an address loaded before the `if` correctly shares its id (no store on that
path). OK.

### A.3 Memory epochs and aliasing across calls (R10–R13)

The epoch discipline is conservative and sound as far as *memory* goes: every store, bulk op and impure call bumps
`ε`; load ids and memory-reading `Pred@ε` atoms are keyed by it; joins and loop heads with possibly-differing epochs get
a fresh one; purity is a call-graph property computed per module, with imports impure. I could not construct an
aliasing counterexample: two loads in one epoch of the same address id are the same value, and any store in between is
a new epoch regardless of address.

Points to tighten:

- **Pure functions that trap or loop forever.** Value-numbering two calls of a pure `$f` with the same args is fine
  (deterministic; if the first does not return, the second is unreachable), but only once A1's global reads are
  excluded.
- **`memory.grow`** is listed "outside v2" in §9 but R12 counts it as impure and §2 says `M` is a lower bound under
  growth — consistent; say in R12 that a module using `memory.grow` is accepted with `M = 65536·min`.
- **Entry epoch 0 is per function pass**, and a callee's `Pred@ε` facts about results are entered at the caller's
  post-call epoch: correct, because the callee's header is instantiated after R12 bumps `ε` for impure callees.
- **Imports.** An imported function with refined results is an assumption; the theorem (§6.1) should say the result
  refinements of imports enter with verdict *assumed* (nothing checks them).
- **Harness predicates that read memory** are excluded from R28 evaluation — good — but a runtime check (R35) of a
  memory-reading predicate is still fine (pure, no epoch bump).

### A.4 Wraparound in `prove k` (§3)

The explicit-wrap encoding is sound where it is specified: I checked `add`/`sub`/`mul-by-constant`/`shl`/`and 2ᵏ−1`/
`div_u` and `rem_u` by constant, `wrap_i64`, `extend_i32_u/s` and the signed-reading `σ` encoding against Wasm
semantics (script `f32bounds.py` in scratch for the `sub` cases; the rest by hand). The problem is what is *missing*,
and two of the gaps bite the one existing example.

**Missing result-range constraints (completeness, see issue 4).** The table gives `add(a,b) ↦ A + B − 2ʷq, q ∈ [0,1]`
and nothing else. `q` is *defined* by the values (`q = 1` iff `A + B ≥ 2ʷ`), but the encoding leaves it free, so the
hypotheses and the negated goal are both weaker than the truth. Weaker on both sides means more models, so the procedure
stays sound — but it loses even `eq(add(x, 0), x)`: the negated goal `X + 0 − 2³²q ≠ X` has the model `q = 1`. §3.3's
interval rule resolves `q` only when the exact result's interval is inside one width-window, which it often is not for
sums of two parameters. The fix is one sentence: *every term's linear form `T` carries the side constraint
`0 ≤ T ≤ 2ʷ − 1`* (this is exactly what makes `q` the quotient). The `$half` proof in parity needs it (the `i64.add` of
two sign-extensions has an unresolved `q` because each extension ranges over all of `[0, 2⁶⁴)`).

**`sub`'s `q = 1` window.** §3.3 says "inside `[2ʷ, 2ʷ⁺¹)` ⇒ `q = 1`"; that is the `add` window. For `sub` the window is
`[−2ʷ, 0)`. Write the rule as "`q` is the unique value with `T ∈ [0, 2ʷ)`" and both cases follow.

**Order: wraps must be resolved before products are expanded (issue 5).** `mul(a,b)` expands `A·B` "as a polynomial";
if `a = add(r, 1)` then `A = R + 1 − 2⁶⁴q₁` and `(R + 1 − 2⁶⁴q₁)²` has the coefficient `2¹²⁸`, which does not fit `i128`
and would return `Cap(coefficients)` for every i64 harness that squares `r + 1` — including the isqrt harness that §6.3
recommends. The interval pass (§3.3) runs after normalization (§3.2), so the `q₁ = 0` substitution comes too late.
Specify Step 1 as bottom-up: translate a term, immediately tighten its interval from its inputs' intervals, resolve its
own `q` if the window allows, *then* let its parent use it. The two global rounds of §3.3 remain for the constraints that
need hypotheses.

**`shr_s` and the other "opaque" rows contradict R3 and the example (issue 3).** R3's table says `shr_s` by a constant
is floor division of `s(·)`; §3.2's table puts `shr_s` among opaque leaves; `parity.expect.json` line 36 says the proof
of `$half` goes through "shr_s gives `2D ≤ S(x) ≤ 2D+1`". Pick the interpreted version and add the row:
`shr_s(a, k)` constant ⇒ fresh signed `D ∈ [−2ʷ⁻¹, 2ʷ⁻¹)` with `2ᵏD ≤ S(a) ≤ 2ᵏD + 2ᵏ − 1`, result `D + 2ʷσ_r` with the
usual `σ` side constraint. The same treatment makes `div_s`/`rem_s` by a *positive constant* linear (truncation toward
zero needs a case split on the sign of `S(a)`), which students will want for `/ 2`. Leave rotations, `xor`, `or` and
non-power-of-two masks opaque.

**The isqrt lesson actually works.** With wraps explicit, `prove` of `(r+1)² > n` from a harness in i32 fails with a
countermodel at `r = 65535` (`q ≠ 0`), and in i64 succeeds because `r ≤ 65536` gives `(r+1)² ≤ 2³² + …`. I
re-derived this on paper; the design's claim in §3.6 is right *provided* the bottom-up resolution above is implemented.

**Monomials.** Keying by sorted factor list and recomputing monomial intervals from factor intervals is sound (unsigned
factors are non-negative, so `[lo·lo, hi·hi]` is correct). Note that `r·r` from `mul(r, r)` and `r·r` from expanding
`(r+1)·(r+1)` must share the same monomial variable, which the sorted key gives. OK.

**Signed relations.** `lt_s(a,b) ↦ S(a) + 1 ≤ S(b)` with `S = A − 2ʷσ` and the σ window constraint is exact. The
`extend_i32_s` form `A + (2⁶⁴ − 2³²)σ` is correct (checked: `u64(sext(x)) = A − 2³² + 2⁶⁴` for negative `x`).

**Non-constant `div_u`/`rem_u`.** `r ≤ A` and `r + 1 ≤ B` are sound under-approximations. Fine. But note the R24 cup
is checked on the same line *after* the term is formed; nothing in §3 uses `b ≠ 0`, so no circularity.

**Constant divisor 0.** `div_u(a, 0)` with the table's `0·d ≤ A ≤ −1` is unsatisfiable, which makes any case containing
it unsat and hence any `prove` mentioning it "valid". In *code* this is harmless (the R24 cup on that line is refuted by
evaluation and the line traps before any later fact exists). In a **proposition** it is not: see issue 6 below.

**Float trunc bounds (R27).** The f64 example bounds are right. For f32 they must be recomputed per type:
`−2147483649.0` rounds to `−2147483648.0` in f32, so the stated bound would wrongly exclude `−2³¹` (incomplete, not
unsound); the correct exclusive f32 bound for `i32.trunc_f32_s` is `−2147483904.0`, and `2147483647.0` is not an f32
either (`HI = 2147483648.0` is, and is already exclusive). Verified in `f32bounds.py`. Say "per source type" and list the
eight constants.

### A.5 Unfolding of predicates, termination, measures (R29–R31)

**Automatic unfolding to depth 4** inside §3 is sound (replacing an atom by the symbolic value of a loop-free, total
body is an equivalence) and deterministic. Two gaps:

- **Predicates with refined parameters used in propositions (issue 6).** `$no_divisor_from` in 15 §3 has
  `(param $d (i64 | $at_least_2))` and its `div_u` by `$d` is proven *from that refinement*. Nothing stops a proposition
  `(fact (call $no_divisor_from $n 0))` — written by a student in a header, or instantiated by the kernel at a call site
  with `$d := #a` for an arbitrary `#a`. Evaluating it (R28 on constants; R35 as a runtime check; the runner's
  harness) traps inside the predicate, and R28 has no "trapped" outcome. Symbolically, the unfolded body reads
  `div_u(n, 0)` as "some `r ≤ n`", i.e. a value that does not exist, so §6.1's "predicates are total, so evaluating
  them in a proposition is meaningful" is false for such propositions. Fix: either (i) a predicate named in any
  proposition must have **unrefined** parameters (total on the full domain; `$no_divisor_from` would guard `d < 2`
  itself), or (ii) every proposition instantiation carries the predicate's parameter cups (which at a header is an
  extra precondition). (i) is the intro-friendly rule. The same applies to **inline `sexpr` propositions**: forbid
  `div_*`, `rem_*`, `trunc_*` in `sexpr` (or treat them as cups at the instantiation site).
- **Indirect recursion.** "Directly self-recursive at most" must be checked on the predicate call graph (a cycle
  `$p → $q → $p` is otherwise unfolded forever at depth 4 and evaluated forever at R28 — the budget saves R28 but not
  the claim of totality). State: the predicate call graph minus self-loops must be acyclic.

**Measures (R31)** are sound: unsigned readings are well-founded, the cup is checked at each recursive call under the
lane of that line, and the measure itself is non-recursive. Three details: (a) the measure's arguments `p` should be
the **entry** ids of the parameters (ghost code and predicates may `local.set` a parameter; say "entry ids"); (b) the
measure of a *lemma* has "the same params as `$f`" — `$f` has fact params, the measure cannot; say "the same value
params"; (c) nothing requires the measure to be defined on arguments that violate the predicate's refinements — moot
once A.5's rule (i) is adopted.

**`unfold` (R30)** enters `eq(call $p e, BODY₁)` as a value equation; with `Pred ≡ (value ≠ 0)` this is the right
shape and sound. The design should say the recursive calls inside `BODY₁` are value-numbered as ordinary pure calls
(same table), so a second `unfold` on `$p (n, d+1)` connects to them.

### A.6 Lemma and axiom trust (R33, R34, §7.1)

- Lemmas are checked by the same cards as code and erased; recursion via `lemma $f` inside `$f` with a decreasing
  measure is well-founded induction, and the induction hypothesis may be used for any smaller argument, so two
  recursive citations are fine. Sound.
- Contradictory fact params or refinements make a lemma vacuous but cannot be *called* without feeding the
  contradiction: sound.
- An LLM-owned lemma with an unproven body yields *assumed* facts, which vericoding rejects: good. But the rule
  "assumed only through student-zone axioms" needs the kernel to track **which** assumption each fact depends on
  (`assumptions: SmallVec<[Origin; 2]>` exists on `CupOut`; make sure `Fact` carries it too — currently `Fact.verdict`
  is just `Proven | Assumed`).
- The most-recent-match rule can pick an *assumed* fact over an equal *proven* one. Prefer proven on ties (cheap,
  deterministic).
- Axioms justified "outside Codillon" (open question 6): fine as long as they are student/instructor zone.

### A.7 The exact canonical match (R4, R5)

Lookup is an equality test on `(head, neg, signedness, width, canonical ids, epoch)`. Two ids are equal only if R1
built them from the same opcode, immediates, input ids and epoch, which (modulo A1/A2) means the same value. So
lookup never feeds a cup with a fact about a different value. The incompleteness is by design (`add(a,b)` vs
`add(b,a)`; `prove 1` fixes it). Two notes: (i) `ne(x, 0)` with `x` a 0/1 comparison rewrites to `x`, but `eq(x, 1)`
does not — add it, students will write `i32.const 1; i32.eq`; (ii) facts entered by *lookup-fed cups* are duplicates
and only shift "k most recent" (issue 10): do not re-enter them.

### A.8 Erasure (§1.8, `erase.py`)

Correct. No v2 construct changes the operand stack: block facts are not results (`bfact` vs `bresult`), fact locals
and proof lines become `nop`, lemma bodies become `nop`s and lemma headers lose only fact clauses, and `nop` in dead
code is valid under stack polymorphism. Line counts are preserved (asserted in `erase.py`). The erased program is the
same Wasm module the student would have written without proofs, so "the same meaning" holds exactly — in *strict*
mode. In *gradual* mode the executed program is the **instrumented** one, a different program; §4 says so, but the
runner (`run.mjs`) runs the erased one, and the oracles describe instrumented behaviour (issue 8). Small `erase.py`
points: a lemma is detected as "all results are facts"; a function with a `(param $h (fact …))` but a value result is
not a lemma by the grammar and would be erased wrongly (the grammar forbids it; reject it in the kernel). Comments
containing `;;` inside a `(fact …)` string cannot occur. OK.

## B. Completeness and implementability

(pending)

## C. Usability

(pending)

## D. Consistency

(pending)

## E. Prioritized fixes

(pending)
