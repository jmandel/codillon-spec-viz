# Fix round 2 (review 22, Fable): STATUS

Repo: /home/jmandel/hobby/codillon-refined, branch `proofs`, committed locally only (not pushed).
Commits: 2c80b1e (probes, as-is), 8aacf6e, d5b5af9, 71ee431, 6f90b73, ae50164, c3b0588 (fmt).
Regression tests: `src/v2/fable_gfix_probes.rs` (Fable's probes, now un-ignored and tightened, plus new ones).

| # | finding | reproduced? | fix commit | test(s) |
|---|---------|-------------|------------|---------|
| B1 | predicate totality is shallow; a lemma proves False through a predicate calling a looping fn | YES: all four functions VERIFIED, `f(0)` traps | 8aacf6e: R29 is now inductive. Every function reached by `call` from a predicate or measure is itself a predicate (info.rs propagation), so the looping or unmeasured-recursive callee gets the R29 checks on its own header | `fable_f1_lemma_through_predicate_through_partial_callee` (loop and self-recursion variants) |
| B2 | runaway blame depends on where the counter trips | YES: isqrt k=1, 2, 5 accepted | d5b5af9: stack rule. When the budget or depth limit trips, the innermost LLM-owned frame on the call stack is blamed; the runaway is excused only if no LLM frame is live | `fable_f5_spin_loop_that_lives_in_a_student_predicate` (k = 1..6, each rejected naming `$isqrt`) |
| B3 | a locked line is skipped by a constant `if`/`br_if` and discharged ex falso | YES: both variants accepted | 71ee431: (a) the kernel treats an arm or edge whose condition folds to False as dead code; (b) `check_module_probing` reports locked lines in LLM bodies where the lane proves False, or where a locked block is left only on contradictory edges; the judge rejects any that are new since session start | `fable_f7_constant_if_around_a_locked_line`, `fable_f7_constant_br_if_before_a_locked_line`, `b3_locked_line_reached_only_ex_falso_is_rejected` (tautology `x>=u0`, unfolded LLM helper, two contradictory facts, block exit only ex falso), `b3_honest_guard_is_accepted` |
| S1 | rule (5) skips fact-param functions and those with no witness in 0..100 | YES: spinning `$g` (fact param) and `$big` (`v>1000`) accepted | 6f90b73: every LLM-owned function is run. Witnesses satisfy fact params (evaluated); if none is small, take the 16 closest to zero from a 256-entry list; with no witness, the function passes only if a `$main`/harness run of rule (5) entered it, else "termination unchecked" error | `fable_f5_functions_the_termination_rule_never_runs`, `s1_no_witness_is_unchecked_unless_main_reaches_it` |
| S2 | global refinements are not scanned for `is_pred` | YES (R29 never ran on `$p`) | ae50164: `analyze` scans global refinements. A refinement calling an impure or looping predicate is a module error and is ignored, instead of producing the misleading "initializer does not satisfy" error | `fable_f3_global_refinement_via_predicate_reading_another_global` |
| N3 | rule (5) only runs when everything else is clean | (read) | 6f90b73: runs whenever the text is in bounds and parses; its reasons are listed last | covered by the above |
| N1, N2 | Refuted cups are not runtime checks; `else` is not a context boundary | — | spec text only (below) | — |
| N4 | research/21 calls F7 "broader" | — | not mine to edit; the corrected wording is in the spec text below | — |

## Design choices

- **B1.** The spec already says a predicate makes "no calls to non-predicates". Applied literally (the call target
  must be named in a proposition), it breaks gcd (`$is_gcd` → `$common`, `$no_cd_above`), hashtable (`$rep_ok` →
  `$rep_from`) and isqrt (`$is_isqrt` → `$sq_le`). Those helpers are predicate-shaped but are only ever *called*.
  So "predicate" now means named in a proposition (functions or global refinements), or called from a predicate or
  measure, transitively. Totality then follows by induction: loop-free, pure, measured direct recursion only, every
  callee total. Lemmas keep their own rule (they may `call` only predicates).
- **B2.** I chose the stack rule over the two alternatives suggested. A per-function self-step share, or charging
  each student-predicate call as one step, can both be dodged: the LLM picks the predicate's arguments, so it can make
  the predicate arbitrarily expensive and its own share arbitrarily small. With the stack rule, where the counter lands
  is irrelevant. The cost is a loud false reject if an implementation calls a student predicate that alone exceeds
  1M steps on a small input. The gcd case (a deep spec predicate checked by its harness after `$gcd` returns) is still
  not blamed. The justification is in the doc comment of `adequacy::runs_away`.
- **B3.**
  - Making arms *proven* infeasible by the solver into dead code was tried and dropped. The solver unfolds pure,
    loop-free LLM callees, so a correct implementation makes a harness's failure arm dead. That is sound, but it turned
    parity's harness `prove 2`/`unreachable` into dead code (a display change) and, under the old rule, a boundary
    violation.
  - So the kernel's dead code stays syntactic plus constant folding. Ex falso is a separate, judge-only probe
    (`false_ctx_lines`), asked with the whole lane and then with its 8 most recent entries.
  - The dead-line and ex-falso rules now look only at locked lines inside LLM-owned bodies. A harness's failure arm
    is *meant* to become unreachable, and the LLM cannot edit student bodies.
  - New: a locked block whose every exit is contradictory, or which has no exit at all while its header is live (the
    LLM `return`s inside it), is a violation.
- **S1.** I chose this rule as the least surprising: run every LLM-owned function on its witnesses (widening if
  needed); if there are none, accept coverage by a `$main`/harness run; otherwise report an error. The error never
  stays silent, and the fix it suggests (add a harness) is the student's normal tool.

## Spec text for research/16 (coordinator to apply)

**§2 R29**: replace the first sentence ("A function named in any proposition is a **predicate**.") with:

> A function named in any proposition (a parameter, result, local, block or global refinement, a fact, an `unfold`
> or `assume` line) is a **predicate**, and so is every function a predicate or measure `call`s, transitively. (So a
> predicate makes no calls to non-predicates: its helpers are predicates too and meet every rule below. Totality is
> then inductive. An ordinary function that loops would otherwise hand the predicate its vacuously proven result
> refinement, i.e. False.)

Also append to R29's error list: "`$g's refinement calls $p, which is not a valid predicate` (module error on the global;
the refinement is ignored)."

**§2 R33**: replace "may call (`call`) only predicates (R29 keeps them total)" with:

> may call (`call`) only predicates, which R29 keeps total *including everything they call*

**§2 R22 (dead code)**: append:

> An `if` arm, a `br_if` fall-through or taken edge, or a `br_table` edge whose condition folds to a constant that
> rules it out is dead code, like the code after `br`: control never takes it. (A condition false only by reasoning
> is not dead code; it enters a fact that contradicts the lane, and the vericoding judge treats that separately, §7.1.)

**§4 (runtime checks)**: add (N1):

> A cup the kernel **refutes** (evaluation or a constant fold shows it false) is not compiled into a runtime check:
> the gradual run reaches the trap or `unreachable` the cup guards, rather than stopping at the cup with a failed check.

**§7.1 enforcement**: replace from "(5) **The program must run.**" through "is a boundary violation." with:

> (5) **The program must run.** The kernel's theorem is partial correctness (§6.1), which a body that never returns
> (`loop br end`, or a call to itself) satisfies for any spec. So `$main`, every harness and every LLM-owned function
> are run, each on up to 16 inputs from its input list (§6.3) that satisfy its precondition. Fact parameters are part
> of the precondition and are evaluated on the run's initial memory. The inputs are the ones whose every argument is
> in 0..100 if there are any; otherwise the 16 closest to zero from a wider list. Each run must finish within
> 1,000,000 steps and call depth 150. A run that runs out is an error when **any LLM-owned function is on the call
> stack** at that moment, wherever the counter trips: `$isqrt(7) does not finish: $isqrt runs past 1000000 steps or
> calls`. Only a runaway in student code that no LLM-owned frame is running (a costly spec predicate checking a
> result) is the student's business. An LLM-owned function that no listed input satisfies counts as run if a run of
> `$main` or a harness entered it; otherwise it is an error: `termination of $f is unchecked: …; a harness that calls
> it would let the judge run it`. Rule (5) is checked whenever the text is in bounds and parses, and its reasons are
> listed after the others.
> (6) **Locked lines must be reached.** A locked line inside an LLM-owned body must not become, compared with the
> session start:
> - **dead code** (R22: after `br`/`return`/`unreachable`, or under a constant-false condition: `makes locked line N
>   unreachable`);
> - **reachable only ex falso**, i.e. the kernel proves False from the lane there (a branch decided by reasoning, an
>   unfolded helper, two contradictory facts: `makes locked line N reachable only ex falso`). Its obligations would be
>   vacuous;
> - for a locked block header, a block that is left **only on contradictory edges, or never** (e.g. a `return`
>   inside it): its block facts would never be checked.
>
> These are boundary violations. Lines in student-owned bodies (harnesses, `$main`, predicates) are exempt: the
> LLM cannot edit them, and a harness's `unreachable` arm is *meant* to become unreachable once the implementation is
> right.

and change "The round is accepted iff (1)–(5) hold" to "(1)–(6)".

**§7.1, zone comparison**: add (N2):

> A line's context is the chain of enclosing `block`/`loop`/`if` headers; `else` is not a boundary, so a student
> line moved from the then-arm to the else-arm keeps its context. This is harmless: the LLM could negate the condition
> and swap its own arms to the same effect.

## Verification

- `cargo test --release --lib`: 111 passed, 0 failed, 2 ignored. The 2 ignored are pre-existing from round 1; none
  of Fable's six hole demonstrations is still ignored.
- Oracle (`oracle_report`) and the fuzz regressions (`prove_regressions_found_by_fuzzing`) pass as part of the suite. (There is no separate fuzz test in the tree.)
- `cargo clippy --release --all-targets`: clean. `cargo clippy --release --target wasm32-unknown-unknown`: clean.
  `cargo fmt` applied (c3b0588).
- **Examples and sessions.**
  - I took a snapshot before any change (`snap-base.txt`): per-function verified, strict_clean, errors and cup
    verdict and feed for all 13 examples, each example's self-judgement, and every turn of the 3 recorded sessions.
  - After each fix it was byte-identical: `snap-b1/b2/b3/s1/s2.txt`. All 12 session turns get their recorded verdicts,
    and the final turns are still accepted.
- Fable's vericoding probes (`fable_probes.rs`): identical to round 1's `probes-after.txt` (`probes-after.txt`).
- Kernel-review adversarial programs (`adv-results/` vs `../gfix/adv-results/`): the only change is that `$odd2` (in
  `more.txt`), called by the predicate `$even2`, is now a predicate and gets "recursive through `$even2`" on its own
  header. This is expected under B1.
- `trunk build --release` (gfix2/dist) succeeds. All 13 v2 examples load in headless chromium with zero console errors
  or exceptions (`shots/*.png`).

## Open

- **Termination is still dynamic.** Rule (5) samples inputs. A body that spins only on inputs outside the sample
  (e.g. `if x == 77777 loop…`) still passes. The wider fallback can also falsely reject a correct but slow
  implementation on a large witness (e.g. `$big(-1)` = 2^32−1 runs first, because inputs are sorted by min(|signed|,
  unsigned)).
- **The ex-falso probe depends on the solver.** If the whole lane hits the cap or is inexact, the probe falls back to
  the 8 most recent entries. A contradiction buried deeper and stated only in terms the solver can't decide would be
  missed. But a `prove k` in the LLM's code can use only ≤ 8 recent entries too, so exploiting it would need a
  lookup-fed or join-carried contradiction. I have no probe showing one.
- **Locked lines in student bodies are exempt** from the dead and ex-falso rules (see B3). Deadness there comes only
  from callees (proven, and run by rule (5)) and the student's own code.
- **The new B3 rule can reject a legitimate answer.** If a correct implementation makes a student's defensive
  `;; @own` line inside an LLM body provably impossible, it is rejected. None of the examples or sessions does this.
- **Not changed:**
  - research/21's wording (N4); the corrected statement is the §7.1 (6) text above.
  - The editor's display of `false_ctx_lines`: the kernel reports them only when probed, i.e. in the judge.
