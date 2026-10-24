# Review of 16-v2-design.md (Refined Codillon v2) — independent reviewer (Fable)

Reviewed: `16-v2-design.md` (draft, §0–§9, ~11,100 words, mtime 12:10), `15-input-proofs-as-values.md`,
`v2-examples/parity*.wat|expect.json`, `v2-examples/tools/erase.py`, `run.mjs`. Written incrementally; the
"most important issues" list is kept current. Scratch checks live in `~/hobby/.agent-scratch/codalon-viz/v2review/`.

## Verdict

The pivot is right and the document is close to implementable: the fact lane, "exactly one feed per cup", declared
loop invariants with no fixed point, and the four verdict states are a coherent kernel with no search anywhere. The
rule cards cover every construct the parity example uses, and the erasure table is correct (the erased program has the
same meaning as the source, because no v2 construct touches the operand stack). I found **four concrete soundness holes**
(mutable globals read by pure/predicate functions are not keyed by any epoch; loop heads do not φ-rename globals; a
`prove` feeding a `br_if` edge cup leaks its goal into the fall-through lane; unguarded `r + 1 ≤ B` constraints on
virtual `rem_u`/`div_u` terms make any `prove` vacuously valid when the divisor can be 0),
and a cluster of **under-specifications in §3** that an implementer would otherwise have to guess (result-range
constraints for wrapped terms, the order of wrap resolution versus polynomial expansion, the variable cap 16 vs 24, the
`vn` key being fixed at three operands). None of these needs a new mechanism; each is a one-line card fix. The 13:29
revision of the design (made while this review was in progress) already closed several findings — `shr_s`, guarded
`rem_u` in virtual terms, refined predicate params, lookup re-entry, dead `end`s, lemma export names — and §F records
exactly what remains. The student-facing burden on parity, isqrt and the gcd loop is fine (four to six `prove` lines
per function); primality is capstone material; the real usability risk is the positional "k most recent lane entries"
rule, which is edit-fragile for students and the LLM loop alike. With F.2 items 1–8 applied, the design is ready for
phase C.

*Reading guide.* Items in the list below marked **[fixed 13:29]** were addressed by the revision and are kept for the
record; §F.2 is the authoritative open list.

## Most important issues (prioritized; details in §A–§E below)

1. **Soundness — mutable globals.** Predicates and "pure" functions may `global.get` a mutable global, but their call
   value-numbers and `Pred(...)` atoms carry no global state. Counterexample A1 proves `b ≠ 0` and then divides by zero.
   Fix: purity forbids reading mutable globals, or a global epoch is bumped by every `global.set`/impure call and keyed
   like the memory epoch.
2. **Soundness — loops and globals.** R8's loop-head pre-scan renames only locals; a `global.set` in the body leaves
   the pre-loop global id live on the next iteration (A2). Fix: pre-scan `global.set` targets (and impure calls) and
   φ-rename `curg` at loop heads, as for locals.
2b. **Soundness — `prove` output leaks past `br_if`.** R32 enters the proved goal into the lane even when the goal was a
   taken-edge cup proven with R20's extra hypothesis `⟦c⟧` (A3). Fix: outputs for edge cups go on the edge snapshot
   only. The isqrt oracle already assumes this.
2c. **Soundness — partial operations in virtual terms** **[mostly fixed 13:29]**: §3.2 now guards virtual `rem_u`
   with `B = 0 ∨ r + 1 ≤ B`. Residue: a *constant* divisor 0 still yields the unsatisfiable `0·d ≤ A ≤ −1`; make it an
   opaque leaf.
3. **[fixed 13:29] Design/example contradiction — `shr_s`.** §3.2 lists `shr_s` as an opaque leaf; `parity.expect.json` and R3
   both assume `shr_s` by a constant is floor division of `s(·)`. Fix §3.2 (add the row with its σ variable), or `$half`
   cannot be proven.
4. **Spec gap — wrapped terms need result-range constraints.** §3.2 gives `add` as `A + B − 2ʷq, q ∈ [0,1]` with no
   `0 ≤ A + B − 2ʷq < 2ʷ`; without it `q` is free and even `x + 0 = x` fails (incompleteness, not unsoundness; but
   `$half`'s proof needs it). State: every term's linear form is constrained to its width range.
5. **Spec gap — order of wrap resolution versus expansion.** `(r+1)·(r+1)` in i64 expands to coefficients `2¹²⁸`
   (i128 overflow → `Cap(coefficients)`) unless the inner `q` is resolved to 0 *before* the product is expanded. Make
   the interval pass run bottom-up per term during Step 1, not after it.
6. **[mostly fixed 13:29: R29 now forbids refined/fact params on predicates] Propositions can trap / predicates with refined params used in propositions.** An inline `(fact (i64.div_u v $d))`
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
10. **Usability — "k most recent" is invisible and shifts.** **[re-entry half fixed 13:29: R5/§5.2 no longer re-enter
    lookup-fed atoms.]** Inserting an unrelated `call` or `br_if` between a hypothesis and its `prove` still silently
    changes the hypotheses (isqrt-wrong-cup is a two-line swap). Print the hypotheses actually taken in every `prove`
    failure; add the lane snapshot to the LLM round's `line_errors`; give `prove` hypothesis chips always-on labels.

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

### A.9 Two more holes found by tracing the isqrt and gcd examples against the cards as written

**Hole A3 — a `prove` that feeds a `br_if` taken-edge cup leaks its goal into the fall-through lane.** R20 gives such a
`prove` the extra hypothesis `⟦c⟧`; R32 then says "the cup is fed **and `G` enters the lane**". `G` was proven *under*
`⟦c⟧`, which is false on the fall-through path. Counterexample:

```wat
(func $a3 (param $n i32) (param $d i32) (result i32)
  block $b (fact (i32.ne $d 0))
    local.get $d
    i32.eqz
    i32.eqz              ;; c ≡ ne(#d, 0)
    prove 0              ;; goal: the block's exit fact ne(#d,0) on the taken edge; hypothesis ⟦c⟧ = ne(#d,0): valid
    br_if $b             ;; R32 as written: ne(#d,0) now sits in the fall-through lane
    local.get $n
    local.get $d
    i32.div_u            ;; cup ne(#d,0): exact lookup finds it — "proven"; traps when d = 0
    return
  end
  i32.const 1)
```

`isqrt.expect.json` silently assumes the fix: at line 49 it lists the hypotheses of `prove 2` as the line-36
fall-through fact and the invariant, which is only right if line 35's output did *not* enter the lane. Fix R32/R20:
a `prove` output feeding an edge cup enters only that edge's lane snapshot (equivalently, never enters the current
lane); outputs feeding line-local cups (`local.set`, `call`, `div`, `unreachable`, `loop` entry) enter as before.

**Hole A4 — unconditional existence constraints on partial operations in virtual terms.** §3.2 gives non-constant
`rem_u(a,b)` the side constraints `r ≤ A, r + 1 ≤ B` "(the value exists, so `b ≠ 0`)". That is true for a term computed
by a *line* (the line's R24 cup guards it), but the same table is applied to **virtual** terms: unfoldings (R29/R30),
lemma and axiom results, header propositions. There `b` can be 0 and `r + 1 ≤ 0` makes the case unsatisfiable, so the
`prove` is "valid" for any goal:

```wat
(func $a4 (param $n i32) (param $y i32) (result i32)
  unfold $gcd_ref $n $y   ;; H: gcd_ref(n,y) = ite(eq(y,0), n, gcd_ref(y, rem_u(n,y)))   (gcd.wat's $gcd_ref)
  local.get $n
  local.get $y
  prove 1                 ;; goal ne(#y,0) for the cup below; negated goal y = 0 ⇒ virtual rem_u(n,y) has r+1 ≤ 0: unsat ⇒ Valid
  i32.div_u               ;; cup ne(#y,0) "proven"; traps at y = 0
)
```

The constant form has the same defect: `div_u(a, 0)` ↦ `0·d ≤ A ≤ −1` is unsatisfiable, so any case mentioning it is
vacuously closed. `gcd.expect.json` line 135 even says "the unfolding's `rem_u(#x, 0)` is a virtual slot; its range
constraint is guarded (§3.2), so it is harmless" — but §3.2 contains no guard. Fix: for `div_u`/`rem_u` (and the new
`div_s`/`rem_s` rows) emit the constraints under the guard `B ≥ 1` — implement as a case split on `B = 0` in which the
result is an unconstrained leaf — and treat a constant divisor `0` as an opaque leaf. The gcd proofs at lines 128 and
134 must still pass with the guard (they do: `ne(#y,0)` resp. `eq(#y,0)` decides the `ite` before the `rem_u` matters).
This is a good regression test for the kernel.

**Related: the "fed and refuted ⇒ an assumption is false" inference (§4.1) is wrong in gradual mode.** In
`gcd-bug-guard.expect.json` the harness `False` cup is *assumed* (via the true axiom) and the erased run reaches
`unreachable`; the culprit is the runtime-checked divisor cup upstream, not the axiom. Say: the inference holds only
when every cup reachable from the harness is proven or assumed; otherwise attribute the failure to the first failing
check of the *instrumented* run.

## B. Completeness and implementability

### B.1 Coverage: every construct the examples use, against the cards

| construct (example, line) | card | status |
|---|---|---|
| `(param $x (i32 \| $is_even))`, `(result (i32 \| $is_half $x))` (parity) | §1.3, R13–R15 | covered |
| `(result (i32 \| (call $is_isqrt (i64.extend_i32_u v) …)))` — sexpr refinement with virtual subterms (isqrt 27) | §1.3, R1 virtual slots | covered |
| `(local $r (i32 \| (i32.le_u v 65535)))` (isqrt 28) | R7, R8, R14 | covered; R14's `LocalInit` cup fed by evaluation |
| `block $done (fact …)` with two facts (gcd 113) | R16 | covered, **but §1.3 says block-line names mean "values on arrival"; R16 and both examples need exit-time values**. Rewrite §1.3: `loop` facts are read at each arrival, `block`/`if` facts at each exit. |
| `loop $grow (fact …)` invariant (isqrt 31, gcd 115) | R17 | covered |
| `if (fact …)` without result (primality 125, 136, 171) | R18/R16 | covered; say that an `if` may carry facts and no result |
| `prove 0` before `loop` (isqrt 30, gcd 114) | R17, R32 | covered |
| `prove k` before `br_if` (edge cup + `⟦c⟧`) | R20, R32 | covered after fixing A3 |
| `prove k` **between operand pushes** and the consumer (primality 23, 68, 122) | §1.6 "proof lines between them are allowed" | covered; worth an explicit sentence and a visual note (the fraction sits mid-operand) |
| a run of two `prove` lines feeding two cups of one `lemma` line (primality 149–151) | R5, R32 | covered, but the **lane seen by the second `prove`** is unspecified: R32 says the first output "enters the lane", the oracle assumes it does not shift the second's hypotheses. Codify: all `prove`s of a run read the lane as it stood before the run; outputs enter when the consumer line is processed, after lookups and before that line's own results. |
| `unfold $gcd_ref $x $y`, `unfold $nd $n 2 2` (constant args) | R30 | covered |
| `lemma $f $n (i64.add $d 1)` — sexpr argument | §1.3 `lemma id expr*`, R33 | covered |
| axioms with fact params (primality 109–113, gcd 103) | R33 | covered |
| recursive lemma with measure = induction (primality 115–161) | R31, R33 | covered |
| `local.get $h1` where `$h1` is a **fact parameter** (primality 121, 128) | §1.5 covers `(local $h fact)` only | **gap**: say fact params are handles bound at entry |
| `local.set $hq` binding an `if`'s else-fact (primality 131) | §1.5 | covered |
| `measure:` with the lemma's value params only (primality 162) | R31 "same params" | fix the wording (value params) |
| harness `br_if 0` to the function frame | R19/R20 | say label depth may name the function body |
| `(fact (i32.eq (i32.eqz (call …)) (i32.eqz (call …))))` — `eq` of two comparison values (primality 115) | R4 | covered as a plain `eq` atom over `ite` terms; **orientation**: `eq(a,b)` and `eq(b,a)` do not match by lookup. Sort the two ids for `eq`/`ne` in R4 (symmetric, sound). |
| `i64.shr_u $n 1` in an axiom result (primality 109) | §3.2 row | covered |
| `i32.shr_s` by constant (parity 34) | R3 vs §3.2 | **contradiction** (issue 3) |
| `select`, `br_table`, memory, globals, `trunc` | R21, R23, R10–R12, R9, R27 | cards exist, **no example exercises them** — the hash-table example mentioned in §9 is not in `v2-examples/` yet |

### B.2 Data structures (§5.1)

Implementable with these corrections:

- `vn: HashMap<(Opcode, Imm, [CanonId; 3], u32), CanonId>` cannot key a `call` with more than three arguments
  (`$nd` has three, `$no_cd_above` three, a harness may have more). Key on `(Opcode, Imm, Range<u32>)` into an
  `vn_args: Vec<CanonId>` arena with a hash of the slice, or use `SmallVec<[CanonId; 4]>`.
- `Fact` needs `assumptions: Range<u32>` (or a small set) so a cup fed through several assumed facts can list which
  axioms it depends on; `verdict: Proven | Assumed` alone cannot drive §7.1's "assumed only through student-zone
  axioms".
- `handles` and `curg` (globals) need per-frame save/restore like `cur` (A.1).
- Edge snapshots copy the lane slice above the mark — fine, but a `loop` inside a `block` with two `br_if $done`
  edges copies the loop's lane twice; the cost is linear in facts in scope per edge and is acceptable for intro code
  (the hash table should be measured, as §9 Q5 says).
- `Head::Eq2` for R30 relates a canonical id to a *virtual term id*; say that `BODY₁` is materialised as virtual slots
  in the same `slots`/`vn` arenas so a second `unfold` of the recursive call inside it connects (gcd 123/133 relies on
  `rem_u(#x,#y)` in the unfolding having the same id as line 121's).

### B.3 The one-pass algorithm (§5.2)

The sketch is right; three orderings must be pinned down because the oracles depend on them:

1. **Per line**: pop operands → compute cups → feed cups (pending `prove` outputs first, then lookup, then
   evaluation) → **enter the fed atoms that are new** (R7 refinement, `prove` outputs, lemma results, call results;
   *not* lookup-fed duplicates) → apply the line's effect (ids, bindings, epoch, control). The gcd oracle at line 128
   (hypotheses `[unfold, ne(#y,0), invariant]`) is only right if line 121's lookup-fed `ne(#y,0)` was *not* re-entered;
   §5.2's "on success enter the fed atom" must be narrowed accordingly.
2. **Edge cups** (`br`, `br_if`, `br_table`, fall-through at `else`/`end`): fed from the edge's own lane (with `⟦c⟧`
   on top for `br_if`); `prove` outputs for them go onto the edge snapshot only (A3).
3. **Loop head**: φ-rename locals (and globals, A2), fresh epoch if needed, re-enter refined-local facts, then enter
   invariants; the fall-in cups are instantiated at the *pre-rename* bindings. Order matters for "k most recent": the
   isqrt oracle at line 35 takes `[invariant, refined-local fact]` as the two most recent, which is the order above.

With these, the pass is deterministic and needs no fixed point. The pre-scan for loops (locals assigned, epoch bumps,
and now globals) is linear in the body.

### B.4 The decision procedure (§3): is it fully specified and deterministic?

Deterministic: yes, given the stated variable order (first appearance in hypotheses, then goal), the case order (by
splitting-term id) and the fixed elimination choice. Fully specified: not yet. Besides issues 3–5 and A4:

- **Variable cap**: §0 says 16, §3.1 says 24. Pick one and count the auxiliaries honestly: the isqrt back-edge proof
  has `r, n, q(i32 add), q(i64 add)×2, q(mul)×2, monomial r², d (ext)…` — about 10; primality's `prove 7` has ~15.
  24 is the safer choice.
- **"32 atoms (hypotheses, goal, definitional constraints)"**: if side constraints count, `(r+1)·(r+1) ≤ n` alone
  contributes a dozen; say the cap counts *atoms* and let constraints fall under the 256-alive cap.
- **Range constraints for every term** (issue 4) and the **bottom-up wrap resolution** (issue 5) are needed for every
  example proof that involves `i64.extend_i32_u` sums or products — i.e. isqrt lines 35, 49, 54, 56 and parity 35.
- **Interval tightening scope**: §3.3 uses only single-variable constraints against constants. The isqrt line-36 proof
  needs `u(r) = 65535` from `u(r) ≤ 65535` (refined local) and `65535 ≤ u(r)` (edge) — both single-variable, fine. The
  line-56 proof needs `u(r) ≤ 65534` from `lt_u(#r, 65535)` → `R + 1 ≤ 65535` — also single-variable after moving the
  constant. State that the pre-pass normalises `x + c ≤ d` to `x ≤ d − c`.
- **`ite` in hypotheses**: an `ite` whose condition is decided by another hypothesis (gcd 128: `ne(#y,0)` decides
  `ite(eq(#y,0), …)`) still costs a case split in §3.4 unless the pre-pass evaluates the condition first. Add: before
  splitting, resolve `ite` conditions that are literally a hypothesis or its negation (cheap, and halves most cases).
- **Opaque leaves for recursive predicate calls** are keyed by canonical args (gcd: three `gcd_ref(·,·)` leaves). Say
  that the leaf variable is keyed by the call's canonical id so equal calls share a variable.
- **Countermodel printing** should give both readings (`u($x) = 4294967295`, `s($x) = −1`); students think signed.

### B.5 Tools and oracles

- `erase.py`: correct on all nine `.wat` files by construction (asserted line counts); the lemma test "all results are
  facts" also classifies axioms (empty bodies) correctly.
- `run.mjs` `paramTypes` regex `\(param\s+\$\S+\s+(i32|i64)\)` **does not match refined parameters**
  (`(param $a (i32 | …))`), so `gcd-vacuous`'s harness gets one argument instead of two (the missing one becomes 0),
  and any harness with a refined input is run wrongly. Parse the erased header instead, and filter inputs by the
  precondition as §6.3 rule 3 requires (otherwise a legitimate `b ≠ 0` precondition is "refuted" by `b = 0`).
- The oracles do not say which program `runs` executes; `after_runs` in `parity-bug-gate` describes the instrumented
  program while `run.mjs` runs the erased one (issue 8).
- `primality.expect.json` omits the cup on line 134 (`i64.rem_u` in `$from_agrees`, fed by lookup of line 122's
  output). Every other oracle lists every cup; keep that invariant so the kernel can be diffed against them.

## C. Usability for intro students and for the vericoding loop

### C.1 Proof burden on the examples

| example | code lines | proof lines | extra spec text | judgement |
|---|---|---|---|---|
| parity | ~25 | 4 `prove` | 2 refinements, 1 harness | right for week one: every `prove` is "the branch fact says so" |
| isqrt | ~30 | 6 `prove` (`0,2,2,2,3`), 1 refined local, 1 invariant, 1 block fact | 2 predicates (10 lines), harness | reasonable; the refined local `r ≤ 65535` is the one non-obvious idea and it *is* the isqrt lesson |
| gcd | ~25 | 2 `unfold`, 2 `prove 3`, 1 `prove 0`, 1 invariant with 2 exit facts | 4 predicates (~60 lines), 1 axiom, 2 measures | the implementation proof is small and elegant; the spec side (`$no_cd_above` + measure + axiom) is instructor material |
| primality | ~50 | `$from_agrees`: 44 lines of ghost code, `prove 7`, 3 axioms, 2 handles | 2 predicates with measures | a capstone project, not an exercise; say so in the README |

So the burden where students live (parity, isqrt, the gcd loop) is four to six one-token lines per function. Good.

### C.2 Where students will get stuck

1. **"Which facts does `prove 3` take?"** The rule is positional and the lane is a side structure the text never
   shows. The isqrt-wrong-cup variant is exactly this failure, and it is a *swap of two lines*. Mitigations the design
   already has (wires, chips) only work on screen; the `prove` failure text must name the hypotheses it took, in order,
   and the countermodel. Consider `prove` printing its hypotheses as a hover list even when it succeeds.
2. **Block facts read at exit, loop facts read at arrival** (B.1): make the syntax carry it — e.g. `(fact …)` on a
   `block` is drawn on the `end` line, which §8 already does; the text §1.3 must say it too.
3. **Stale facts after `local.set`** are the main conceptual hurdle; fraying ribbons plus the R5 hint
   ("about the old `$i`, set at line N") are the right treatment. Add the hint also when the only candidate differs by
   `eq` orientation or commutation ("same fact with operands swapped; add `prove 1`").
4. **Unsigned countermodels** for signed code: print both readings (B.4).
5. **Writing specs as Wasm predicates** is verbose (`$is_half` is 10 lines for `2v = x`); that is the course's
   language, so acceptable, but the editor should offer the predicate skeleton (params, `if (result i32)`, `end`).
6. **`prove 0`** for pure-semantics facts (`and 1` parity, `rem_u < b`) will puzzle students ("prove nothing?"). Label
   it in the UI as "by arithmetic" and keep open question 4 answered "no" (explicit is better for the LLM loop too).

### C.3 The fact lane on screen

Chips are diamonds with text **on hover** (§8). For the positional `prove k` rule the student has to see the *order* of
the last few chips at a glance; a column of unlabeled diamonds does not give it. Recommend: always-on 8 pt labels on
the `k` chips wired into a `prove` (the same style as cup goals), and a running index or stacking so recency is visible.
Everything else in §8 (always-on wires, False cup, four fills) is explicit enough and grayscale-safe.

### C.4 The LLM loop (§7.3)

- The round request carries cups and line errors but **not the lane** at the failing line. Since hypotheses are
  positional, the model cannot know what `prove 2` will see. Add per-error: the lane's last 8 atoms with birth lines.
- `line_errors` should include the countermodel in both readings and, for `Cap`, the term count.
- The ownership rule "LLM may add refined locals and block facts" is right; it should also be allowed to add
  `(local $h fact)` handles (it is, under "proof lines: … fact locals") — fine.
- Guard against the model editing a locked line by *renumbering*: the lock is by line range, edits shift lines, so
  the editor must re-derive ranges from the hashed content after every applied edit (the text says "hashed line by
  line", good; say the ranges are recomputed).
- Round cost: a full re-check per round is one pass per function; fine.

## D. Consistency

### D.1 With 15 and the approved plan

- 15 §1's stack-carried proofs were dropped in favour of the lane, with the two reasons given (erasure, stack order).
  The trade is argued honestly in §1.1 and I agree with it; the one cost (text does not name the feed) is mitigated
  by the deterministic rule and the wires.
- 15 §2's data structures are kept (slots + canon + facts + marks), the 64-term cap is kept, "no bigints" is kept
  (i128 coefficients). 15's "coefficients are u32/u64 with Wasm wraparound" would have been unsound for the solver;
  i128 with a cap is the right correction.
- 15 §3's prime example is reproduced faithfully (with `d > n/d`), and the "clear vs fast" lemma became
  `$from_agrees`/`$prime_agrees` with axioms where 15 anticipated them.
- Plan items A–G: A is this document; B's examples are landing with seeded bugs (code bug, missing proof, wrong cup,
  spec bug, vacuous spec) — all five bug kinds from the v1 taxonomy appear; D's four states and gradual mode are
  specified; E's lock/adequacy/scripted sessions are specified. Nothing in the plan is contradicted.
- 15's "gradual mode: unfed cup falls back to a runtime check, drawn as an empty cup with 💣" is kept (R35).

### D.2 Internal inconsistencies (each is one sentence to fix)

1. §1.3 "block line: the values on arrival" vs R16 and examples (exit-time instantiation for `block`/`if`).
2. R3 (`shr_s` by constant = floor division) vs §3.2 (`shr_s` opaque); parity needs the former.
3. §0 "16 variables" vs §3.1 "24 integer variables".
4. §5.2 "on success enter the fed atom" vs the gcd oracle (lookup-fed cups not re-entered) and vs §1.1 "a fact stays in
   the lane … never popped" (re-entering creates duplicates that shift `k`).
5. R32 "`G` enters the lane" at the `prove` line vs the oracles (enters at the consumer; not at all for edge cups).
6. R7 "if the cup is fed, enter `R[v := #n]`" vs R8 "enter `R[v := #φ]`" unconditionally: in gradual mode a
   runtime-checked `local.set` still yields a *proven* fact at the next join. Either both enter (with a
   "relative to checks" marker) or R8 enters only when every edge's cup was proven.
7. §4.1 "fed and refuted ⇒ an assumption is false" vs `gcd-bug-guard` (the axiom is true; an upstream check is
   missing).
8. §9 says `memory.grow` is outside v2; R12 and §2's `M` handle it. Keep R12's version.
9. R31 "same params as `$f`" vs lemmas with fact params (`measure:from_agrees` has value params only).
10. §1.5 covers `(local $h fact)`; primality uses `local.get` on fact *params*.
11. §6.3 rule 4 (runner calls each harness on an input list) and rule 3 (refinements are the precondition) vs
    `run.mjs` (ignores preconditions, mis-parses refined params).

## E. Prioritized fixes (problem → fix)

**Must fix before phase C (soundness)**

1. Predicates/pure functions may read mutable globals, unkeyed → purity forbids `global.get` of `(mut …)` globals
   (or add a global epoch keyed like `ε`).
2. Loop heads φ-rename only locals → pre-scan `global.set` and impure calls; φ-rename `curg` at the head.
3. `prove` output for a `br_if` edge cup enters the fall-through lane → outputs for edge cups go on the edge snapshot only.
4. `rem_u`/`div_u` side constraints are unconditional in virtual terms → guard with `B ≥ 1` (case split); constant
   divisor 0 is an opaque leaf.
5. Predicates with refined params can be named in propositions with violating arguments; inline `sexpr` may trap →
   predicates used in propositions have unrefined params; no `div`/`rem`/`trunc` inside inline `sexpr`; R28 gets a
   "trapped" outcome (= unfed, with the trap named) for safety.
6. Float atoms could pass through R4's negation rewrites → float atoms keep `neg`, never rewritten (rule 1 only).
7. §4.1 misattributes refutations to assumptions in gradual mode → attribute to the first failing check of the
   instrumented run; the inference holds only when all reachable cups are proven/assumed.

**Must fix before phase C (the examples do not check otherwise)**

8. `shr_s` opaque in §3.2 → add the floor-division row with a signed `D` and `σ` (and `div_s`/`rem_s` by positive constants).
9. No result-range constraint on wrapped terms → every term's linear form carries `0 ≤ T ≤ 2ʷ − 1`.
10. Wraps resolved after expansion → bottom-up per-term interval tightening during Step 1, before any product expands.
11. `eq`/`ne` orientation defeats lookup → sort the two canonical ids in R4.
12. Block facts "read on arrival" → read at each exit; `loop` facts at each arrival.
13. Lookup-fed cups re-enter their atom → only new facts enter; a run of `prove`s reads the lane as it stood before
    the run; outputs enter at the consumer line.

**Should fix (implementability)**

14. `vn` key `[CanonId; 3]` → variable-length argument slice.
15. Variable cap 16 vs 24; "32 atoms" ambiguous → 24; atoms exclude side constraints.
16. Block/`if` result values at joins → φ-merge like locals; enter the result refinement at `#φ`.
17. Zero-edge joins → "no incoming edges ⇒ code after `end` is dead", stated.
18. `Fact` lacks assumption provenance → add it (needed by §7.1 rule 3 and §4.1).
19. `handles`, `curg` not saved per frame → save/restore like `cur`; fact params are entry-bound handles.
20. Indirect predicate recursion unchecked → predicate call graph minus self-loops must be acyclic.
21. Measure args → entry ids of value params only.
22. Imports' result refinements → enter as *assumed*; say so in R13/§6.1.
23. f32 trunc bounds → per-source-type constants (eight values).
24. `ite` conditions decided by a hypothesis → resolve before splitting.
25. `run.mjs` → parse refined params; filter inputs by precondition; say which program (erased vs instrumented) `runs` describes.
26. `primality.expect.json` → add the line-134 cup.

**Usability (phase D/E)**

27. `prove` failure text → list hypotheses taken, in order; countermodel in both readings; term count on `Cap`.
28. Chips for `prove` hypotheses → always-on labels; visible recency.
29. LLM round → include the lane's last 8 atoms at each failing line.
30. R5 stale hint → also for orientation/commutation near-misses.
31. README → label primality as a capstone; parity/isqrt/gcd as the student path.

## F. Final pass (design at 13:29, examples README at 13:28, all 13 examples present)

The design was revised while this review was being written. I re-read the whole document and re-ran
`node tools/run.mjs` (all 13 files erase line-for-line, parse, validate; every correct harness passes on 338–589 inputs;
every bug variant fails on its recorded input — the README's claim holds). Status of each finding against the revised text:

### F.1 Fixed by the revision (no further action)

- **`shr_s`** (issue 3): §3.2 now has the row `D + 2ʷτ` with `2ᵏD ≤ S(a) ≤ 2ᵏD + 2ᵏ − 1`. Correct; parity line 35 is
  provable.
- **Guarded `rem_u` in virtual terms** (A4, the `rem_u` half): §3.2 now splits `B = 0 ∨ r + 1 ≤ B` for virtual slots.
  The `div_u(a,b)` row (`r ≤ A` only) was already satisfiable for `B = 0`.
- **Predicates with refined params** (issue 6, main part): R29 now requires predicates to be "free of refined or fact
  parameters (so it is total on every argument)". That closes the trap-in-proposition hole for predicate calls.
- **Lookup-fed cups are not re-entered** (issue 10 / D.2 item 4): R5 and §5.2 now say so explicitly; the gcd oracle's
  hypothesis lists are consistent with the text.
- **R4 rule 2** now covers predicate calls and `¬¬A → A` (A.2).
- **Zero-edge joins / dead `end`** (fix 17): R22 now says an `end` reached only by dead code stays dead unless its
  label has incoming edges.
- **Fact params are handles** (fix 19, second half): §1.5 now says so.
- **Lemma identification** by `lemma:` export (§1.7, §1.8); `erase.py` was updated accordingly (13:26) and no longer
  classifies `$remove` (whose only result is a fact) as a lemma. Verified on the erased hash table.
- **Cup order on a line** (R5) and the **order of lane entry for a `lemma` line** (R33: prove-fed cup atoms, then
  results) are now specified; the primality oracle at lines 149–151 matches.
- **Loop-head epochs** (R12) now state the pre-scan is syntactic and conservative, and show the loop-fact idiom for
  memory predicates (hashtable `$insert`).
- **Fact params/results on ordinary functions** (R13, R33) are now explicit; hashtable uses them as the memory
  invariant's pre/postcondition, and the oracle's chaining (`$insert`'s fact result feeds the next call's fact param in
  the epoch after the call) is the right reading of R13.

### F.2 Still open after the revision (unchanged text; see the sections cited)

| # | finding | where in the design | status |
|---|---|---|---|
| 1 | A1: pure/predicate functions may `global.get` a mutable global; no keying | R1, R9, R29 purity list | **open, soundness** |
| 2 | A2: loop heads do not φ-rename globals | R8 pre-scan ("`local.set`/`local.tee` targets") | **open, soundness** |
| 3 | A3: `prove` output for a `br_if` edge cup enters the fall-through lane | R32 "`G` enters the lane", R20 | **open, soundness** (the isqrt oracle assumes the fix) |
| 4 | A4 residue: a **constant** divisor 0 (`div_u(a,0)`, `rem_u(a,0)`) gives `0·d ≤ A ≤ −1`, unsat, in virtual terms | §3.2 rows for constant `c` | open, soundness (rare); make `c = 0` an opaque leaf |
| 5 | No result-range constraint `0 ≤ T < 2ʷ` on wrapped terms | §3.2 | **open, completeness**; §3.3's new "unresolved `q` ∈ [0,1] become case splits" does not fix it: in the `q = 1` case nothing contradicts a wrong `q`, so `x + 0 = x` still gets a countermodel |
| 6 | Expansion before wrap resolution → `2¹²⁸` coefficients for i64 `(r+1)²` | §3.2 vs §3.3 order | open; the new case-split rule for `q` helps only if expansion happens *per case after substitution*; say which |
| 7 | §1.3 "block line (the values on arrival)" vs exit-time instantiation in R16 and gcd/isqrt | §1.3 | open, text |
| 8 | §0 "16 variables" vs §3.1/§3.5 "24" | §0 | open, text |
| 9 | `vn` key `[CanonId; 3]` | §5.1 | open, implementability |
| 10 | `eq`/`ne` orientation in lookup | R4 | open, usability (gcd's `eq(v, gcd_ref)` vs `eq(gcd_ref, …)` works only because the author wrote them the same way round) |
| 11 | Block/`if` result values need φ at joins | R8 | open, text (oracles already use `#φ`) |
| 12 | `Fact` lacks assumption provenance | §5.1 | open, implementability (§7.1 rule 3 needs it) |
| 13 | §4.1 "fed and refuted ⇒ an assumption is false" | §4.1 | open; wrong when an upstream cup is runtime-checked (gcd-bug-guard) |
| 14 | Verdict downstream of runtime-checked cups shown as *proven* (R8, R13 chaining) | R8, R13, §4 | open; the hashtable oracle marks line 371 "proven relative to `$remove`'s runtime-checked postcondition" — the UI needs a visible marker for "proven, relative to checks at …", or vericoding mode will be the only place the distinction is enforced |
| 15 | Inline `sexpr` propositions with `div`/`rem`/`trunc` can trap at R28/R35; R28 has no "trapped" outcome | §1.3, R28 | open, minor |
| 16 | Float atoms through R4 negation rewrites | R4/R27 | open, text |
| 17 | Imports' result refinements must be *assumed* | R13, §6.1 | open, text |
| 18 | f32 `trunc` bounds per source type | R27 | open, text |
| 19 | `run.mjs` mis-parses refined harness params; ignores preconditions | tools | open |
| 20 | `primality.expect.json` lacks the line-134 cup | oracle | open |
| 21 | `handles`/`curg` per-frame save/restore; indirect predicate recursion check; measure args = entry ids of value params | §5.1, R29, R31 | open, implementability |

### F.3 The hash-table example (new since the first pass)

I traced all 29 cups in `hashtable.expect.json` against the revised cards. They are consistent with the text given the
two unstated conventions already noted (edge-cup `prove` outputs do not enter the fall-through lane; block/`if` result
φ). Specific checks:

- Bounds cups by `prove 0`: `and(·,7)` → `[0,7]`, `shl 2` with `q ∈ [0,4)` resolved to 0 → `≤ 28`. Correct, and a nice
  demonstration that masking needs no invariant. The address expression on line 175 contains an unresolved `add` wrap
  (`hash(k) + i`), which is harmless because the `and` bounds the result regardless; with the new case-split rule for
  `q` this costs two cases. Fine.
- `$find`'s contract (`$slot_or_none`) feeding `$remove`'s store bounds through the implicit-else fact `ne(#j, −1)`
  (R18's "consequence") is the best illustration in the suite of why contracts are the bridge between functions.
- The epoch story (`$insert`: entry `@0`, head `@ε′`, back-edge still `@ε′` because storing arms return, result after
  a store unprovable) is exactly R12 as revised, and the three runtime-checked `$rep_ok` result cups are honest about the
  missing frame rule (§9 Q2). This is the example that will decide Q2: 7 of 29 cups are runtime-checked for want of it.
- `hashtable-stale` is the cleanest "fact about the old value" case in the suite (guard about `#i`, store built from
  `#i′`), and the erased run traps OOB at `65504 + 32`; the oracle's `oob` expectation is confirmed by the runner.
- One oracle nit: the `$chain_ok`/`$no_dup`/`$rep_from` measure proofs list two hypotheses each but need only
  `ne($n, 0)`; harmless.
- Open question 8 (congruence) is well observed: `$p(#g)` vs `$p(#h)` under `#g = #h` does not match, and the harness
  works around it by `local.set $g`. A one-step congruence closure over the `k` hypotheses' equalities (substitute
  equal ids before translation) would be deterministic and cheap; I would add it to §3.2 rather than leave it open.

### F.4 README

Accurate and useful. Two additions: (i) say that `runs` are of the **erased** program (it does, in "Validation") and
that `after_runs` in the parity oracle describes the *instrumented* program (it does not; issue 8); (ii) mark
`primality.wat` as capstone material in the inventory. The format section should list `prove_error`, `stale_hint`,
`strict_error`, `after_runs`, `adequacy`, `axioms`, `lemmas` as optional keys (they appear in the files but only some
are documented).

### F.5 Closing assessment

With the revision, the design has no remaining contradiction with its own examples except §1.3's "values on arrival"
sentence and the two conventions the oracles assume (F.2 items 3 and 11). The three soundness items that remain (F.2
1–3) are each a one-line card change and none disturbs any example. Items 5–6 are the ones most likely to surprise the
implementer, because the examples' `prove` lines will fail without them. Everything else is text. I would proceed to
phase C with F.2 items 1–8 applied to the document first, and I would add a kernel regression test for each of the
counterexamples A1–A4 and for gcd lines 128/134 under the guarded `rem_u` rule.
