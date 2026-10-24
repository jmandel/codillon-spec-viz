# Review of the Phase G fix round (commits 273577a..cd51b04) — Fable

Probes: `~/hobby/codillon-refined/src/v2/fable_gfix_probes.rs` (registered in `mod.rs`; the six
that demonstrate holes are `#[ignore]`d with the finding's id — run with `--ignored`). Full
suite with the file added: 100 passed, 0 failed, 8 ignored. **ran** = executed a probe;
**read** = reasoned from the diff only.

## 1. Verdict

Not ready to merge as "F1–F9 closed". Six of the nine fixes hold against the variants I tried
(F2, F3, F4, F6, F8, F9 — F4/F8/F9 by reading only). Three are broken by a one-line variant of the
reviewer's own attack, and two of those are soundness-grade:

- **F1 (lemma totality) is still open at the kernel level.** A lemma may call predicates because
  "R29 keeps them total", but R29 checks only the predicate's own body: a predicate that `call`s
  a looping ordinary function inherits its False contract. All four functions VERIFIED, `f(0)`
  traps on `i32.div_u`. (ran)
- **F5 (the program must run) is bypassed by the blame rule.** A spin loop whose iterations spend
  most of their steps inside a student predicate trips the budget inside student code, so no one
  is blamed: `accepted: $isqrt verified`. (ran)
- **F7 (locked line made unreachable) is bypassed by constant conditions.** `i32.const 1; br_if 0`
  (or a constant-false `if`) plus `prove 1` makes the locked block fact provable ex falso while
  never executing it; the kernel's `dead_lines` is purely syntactic (`br`/`return`/`unreachable`),
  so the judge sees nothing. `accepted: $f verified`. (ran)

The A14b rejection reasoning holds (ran: an ordered zone comparison catches two student lines
swapped; a single line moved among LLM lines is equivalent to LLM-only edits).

## 2. Fix by fix

| # | status | probe (file: `fable_gfix_probes.rs`) | how |
|---|--------|----------------------------------------|-----|
| F1 | **broken** | `fable_f1_lemma_through_predicate_through_partial_callee`: `$spin` loops with result `(i32 \| (i32.ne v v))` (dead-fed, Proven); predicate `$p` does `call $spin; prove 1` and so proves `(i32 \| (i32.ne $a 0))`; lemma `$boom` calls `$p`; `$f` divides by `$x` after `lemma $boom $x`. Everything VERIFIED, `f(0)` traps. | ran |
| F1 | holds | `lemma $self` with a non-decreasing measure: `⟨u($m($x)) < u($m($x))⟩ nothing feeds it`, lemma not verified. Predicate→lemma→predicate cycle: both ends get `recursive through`. | ran |
| F2 | holds | `local.tee $n` instead of `local.set`: the R7 cup appears on the tee line (Refuted). A *parameter's* refinement naming another parameter: cup on `local.set $a` too. A local refinement naming a global: `unknown name $g` (rejected, so no alias path). | ran |
| F3 | holds | `global.set` in a lemma: `must be pure`. Global refinement via a predicate that reads another mutable global `$h`: the fact stays opaque (`$p($g)` is not unfolded), `$f` not verified and the gradual run fails the check at the division. See S2 for what this probe exposed. | ran |
| F4 | holds | Not probed. Dominance = earlier line with every enclosing arm still open; a capture inside a loop cannot dominate a check after it, and a stale capture from an earlier iteration is a different SSA term. | read |
| F5 | **broken** | `fable_f5_spin_loop_that_lives_in_a_student_predicate` (isqrt session): body `loop; (local.get $n; i64.extend_i32_u) ×2; call $is_isqrt; drop; ×k; br; end; unreachable`. k=1, 2 and 5 **accepted**; k=3, 4, 6 rejected only because the counter happened to trip in `$isqrt`. Also `fable_f5_functions_the_termination_rule_never_runs`: an LLM-owned function with a fact parameter, or with a precondition `v > 1000`, is never run — spinning bodies accepted for both. A bare `unreachable` body *is* rejected (`⟨False⟩ nothing feeds it`), so trap-based bypasses are closed. | ran |
| F6 | holds | Judged set = touched ∪ every non-imported, non-axiom, non-student-body function. Observed as a side effect: my first parity probe was rejected on the untouched `$half` stub (line 37). No bypass found: new non-lemma functions and imports are boundary violations, student bodies are frozen. | ran (incidentally) + read |
| F7 | **broken** | `fable_f7_constant_br_if_before_a_locked_line`: locked `block $b (fact (i32.lt_u $x 100)) ;; @own` at top level; LLM prepends `local.get $x; i32.const 1; br_if 0` and puts `prove 1` inside the block. Accepted. `fable_f7_constant_if_around_a_locked_line`: same with the block inside an LLM `if` whose condition becomes `i32.const 0`. Accepted. The `return` variant from the fix agent's test is caught because `go_dead` runs on `br`/`return`, not on folded conditions. | ran |
| F8 | holds | Not probed. The acknowledged residual (lower multi-param loop params, multi-value joins → Unknown, silently passing) is real but rare. | read |
| F9 | holds | Fix agent's test covers it. See S1: the same `pre_holds` could serve fact-param functions in `termination()`, which excludes them. | read |
| A14b | holds | `fable_a14b_then_to_else_keeps_context`: two `;; @own` lines of one block swapped → `adds a line to the locked spec` (ordered comparison). Then-arm → else-arm keeps the context string (`$f/if`), which is fine: the LLM could negate the condition and swap its own arms with the same effect. | ran |

## 3. New issues

### Blocking

**B1 — R29 totality is shallow, so lemmas are not total (F1 reopened).** `lemma_checks` allows
`call` of any `is_pred` function; `predicate_checks` forbids loops, impurity and unmeasured
recursion in the predicate *itself*, but `has_loop` is not propagated along calls and a
predicate may `call` any pure function. Reproducer: `fable_f1_lemma_through_predicate_through_partial_callee`
(ran: all VERIFIED, erased program traps). In vericoding the LLM cannot author `$p` or `$spin`
(both student-owned), so this is a kernel/§6 erasure soundness bug, not an LLM bypass. Fix: apply
the lemma rule to predicates and measures too — `call` only of predicates/measures (transitively
total), or propagate `has_loop`/"calls a non-predicate" along `calls` in `info.rs` and reject.

**B2 — F5's blame rule is dodgeable by construction.** `ran_out_in` is the innermost frame when
`steps > budget`; a loop in LLM code that calls a student predicate each iteration is blamed on
the student with probability ≈ (predicate steps)/(iteration steps). Reproducer:
`fable_f5_spin_loop_that_lives_in_a_student_predicate` (ran: k=1 accepted on the isqrt session).
No luck needed: the LLM can retry with another k. Fix: charge each step to the innermost
*LLM-owned* frame on the stack and exempt only *depth* runaways that start in student code (the
gcd spec-recursion case). A fib-like student predicate might then cause a loud false reject,
which beats a silent accept.

**B3 — F7 measures deadness syntactically (F7 reopened).** `dead_lines` is fed by `go_dead`
(`br`, `return`, `unreachable`, `br_table` errors). An `if` arm entered under a constant-false
condition, or a `br_if` fall-through under a constant-true one, is "live" to the judge but
provable ex falso and never executed. Reproducers: `fable_f7_constant_br_if_before_a_locked_line`
(works on a locked line at function top level — general), `fable_f7_constant_if_around_a_locked_line`
(ran: both accepted). Fix: (a) in `control`, when `terms.is_const(c)` decides the edge,
`go_dead` the impossible side; and (b) in the judge, cross `dead_zone` with runtime coverage from
the rule-(5) runs — a student-zone line executed at session start but by no run now is a
boundary violation. (a) closes constants; (b) also closes input-dependent `br_if` tricks.

### Should-fix

**S1 — Rule (5) silently skips common spec shapes.** `termination()` runs an LLM-owned function
only if all its params are value params, and `small()` demands every argument in 0..=100. A spec
with a fact parameter (hashtable's `rep_ok` style) or a precondition like `v > 1000` is never run
unless `$main`/a harness happens to reach it. Reproducer: `fable_f5_functions_the_termination_rule_never_runs`
(ran: spinning bodies accepted for both). The LLM cannot create the situation, but the student
gets no warning that (5) is off. Fix: drop the all-value-params condition (`runs_away` already
filters through `pre_holds`, which now evaluates fact params); when the small-witness list is
empty, widen the range (take the 16 smallest witnesses from `input_list`) and, if still empty,
report "rule (5) could not run `$f`" as a strict reason rather than passing.

**S2 — A function named only in a global's refinement is not a predicate.** `info.rs` collects
`named` from params, results, locals and block facts, not from `(global … (i32 | (call $p v)))`.
So `$p` escapes R29 entirely (loop, mutable-global read: no error), and the initializer check
evaluates it with a budget and reports the misleading `initializer does not satisfy its
refinement`. Reproducer: second half of `fable_f3_global_refinement_via_predicate_reading_another_global`
(ran). No unsoundness found (the fact stays opaque and becomes an assumption), but R9/R14's new
text promises "pure, memory-free predicates" and nothing enforces it. Fix: scan global
refinements in `analyze`.

### Nits

**N1 — Refuted cups are not runtime checks.** With a constant the kernel can fold, the R7 cup is
`Refuted` and the gradual run traps downstream (`fable_f2_tee_owes_the_cup_too`: trap at the
division, not `CheckFailed` at line 11). Pre-existing, not from this round; worth a sentence in
§4 (ran).

**N2 — `else` is not a context boundary** (`contexts()` pushes only on block/loop/if). Harmless
for the reasons in §2, but the A14 commentary should say so (ran).

**N3 — `termination()` runs only when strict is empty**, so the LLM learns about rule (5) only
on its last round. Run it always, list it last (read).

**N4 — research/21 calls F7's criterion "broader than the review's"**; it is narrower where it
matters (B3).

Not done: F4/F8 probes, oracle/fuzz re-runs, the editor-side F10 changes.
