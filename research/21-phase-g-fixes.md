# Phase G fix round (review 20, Gemini) — STATUS

Repo: /home/jmandel/hobby/codillon-refined, branch `proofs`. Regression tests: `src/v2/gfix_tests.rs`.
Commits (branch proofs, local only): 273577a e38a05f c1c26a5 6e9ff92 71e0911 3e81681 a059f4d 4a1bbc9 6a1e208 be75d92 cd51b04.
Baselines: probes-baseline.txt (Fable vericoding probes), adv-results-base/ (kernel-review adversarial programs).

| # | finding | reproduced? | outcome |
|---|---------|-------------|---------|
| 1 | lemmas skip R33 (loop/self-call proves False) | YES: `lemma $boom` (body `loop br end`) made a div-by-param VERIFIED; also via `call $spin` of a partial ordinary fn, `call $lemma` as code, mutual lemma recursion | FIXED e38a05f: R33 checks on lemmas (no loop/store/impure/value results; calls only to predicates; lemma edges in mutual-recursion scan; `call` of a lemma/axiom is an error). Tests f1_* |
| 2 | relational local refinement re-entered at join/loop head | YES: reviewer's program VERIFIED, traps at c=1. (Sub-claim 'path-insensitive groups mark upstream proofs Proven*' is conservative imprecision, not unsound: not changed.) | FIXED c1c26a5: `local.set $n` owes the cup of every refined local whose refinement names `$n` (R7); local refinements may not read memory (same hole via stores). Tests f2_* |
| 3 | refined global: no initializer cup, per-function groups | YES: init 0 vs `v≠0` proved a division; $reader proven with no checks while $setter's set was unfed; global refinement naming `$x` bound to the caller's local and proved `$x≠0` | FIXED 6e9ff92: initializer evaluated (module error + refinement becomes an assumption); unproven global.set cups anywhere become `Dep::Check(line)` of the refinement in every function (fixpoint); refinement may name only `v` and may not read memory. Tests f3_* |
| 4 | R35 shadow captures of later/sibling pure calls read 0 | YES: check `$pos($x)` on line 11 failed for x=5 because `call $pos` on line 14 shares the term (shadow still 0); same for a sibling `if` arm; negated refinement passed wrongly | FIXED 71e0911: a Call/Load term counts as captured for a check only if a birth of it dominates the check (earlier line, every block arm open at the birth still open at the check); otherwise the pure call is recomputed host-side. Test f4_* |
| 5 | non-terminating LLM bodies pass judge + adequacy | YES: isqrt session, body `loop br end unreachable` and `local.get $n; call $isqrt` both accepted (kernel VERIFIED: correct under partial correctness, so the kernel is right; acceptance was wrong) | FIXED a059f4d: judge rule (5) — $main, harnesses and LLM-owned value-param functions must finish on up to 16 small (0..100) precondition witnesses within 1M steps / depth 150, blamed only when the runaway happens inside an LLM-owned function (a costly student spec predicate is not blamed); adequacy Bench records harnesses whose original never finishes and the panel shows a red line. Not done: the 'DeadCode on exit cups' criterion (legit early-`return` bodies have a dead `)`). Tests f5_* |
| 6 | judge strictness only on touched functions | YES: parity session, gate inlines x>>1, `$half` left as `i32.const 0` → `accepted: $half_or_neg1 verified` | FIXED 3e81681: strict_reasons on touched ∪ every non-imported, non-axiom function whose body is not student-owned. Test f6_* |
| 7 | dead-code bypass of locked lines | YES: `local.get $x; return` above a locked `block (fact x<100) ;; @own` → `accepted: $f verified` | FIXED 4a1bbc9: kernel reports `dead_lines` per function; any student-zone line dead in the submission but live at session start is a boundary violation (`makes locked line N … unreachable`). Broader than the review's 'DeadCode-fed cups on student lines' (the block fact's cup sits on the LLM-owned `end`). Test f7_* |
| 8 | loop-param #φ / float cups not evaluated at runtime; f32 trunc bounds | YES (all three): check on a loop param was Unknown (silently passed, then trapped); `Key::Float` cups Unknown; `f32.const -2147483648; i32.trunc_f32_s` (valid) got bound `gt(-2^31, -2^31)` which is false | FIXED 6a1e208: exact per-source-width bounds; `eval_fop` (float arith/compare/convert/trunc/reinterpret as Wasm) used by kernel evaluation and the runtime checker; top loop param captured after the `loop` line (runs on entry and back edges). Residual: params below the top of a multi-param loop (and multi-value join results) still uncaptured → Unknown; noted, rare. Tests f8_* |
| 9 | pre_holds ignores fact params; vacuity ignores fact results | YES: `(param $h (fact (k<10)))` accepted k=12 as a witness; `(result (fact (u(k) ≥ 0)))` not flagged | FIXED be75d92: fact params evaluated in pre_holds (on zeroed run memory); fact results checked for tautology (provable with no hypotheses, via a synthetic `prove 0` function) → unconstraining. Implied-by-precondition fact results (hashtable `$remove`'s rep_ok preservation) are deliberately NOT flagged. Test f9_* |
| 10 | wide-line badges / vc-panel overlap | PARTLY: vc-panel overlap was already fixed in ecdee1e (panel pushes the listing; verified in shots/gcd-vc2.png). Wide-line badge still covered header text (shots/parity-40.png: VERIFIED over `$hon_ok`); stale hint ellipsized away (shots/hs-320.png) | FIXED cd51b04: on wide lines the badge and the pinned commentary sit on a sub-row in the inter-row gap below the glyphs (row pitch unchanged, so the proof geometry is untouched; shots/pmp-40c.png); stale-fact hint now first in the kernel diag and in run commentary (shots/hs-e-crop.png). |
| A14b | moving a student line within its own block | YES (not a boundary violation) | REJECTED as a boundary rule: moving a student line among LLM lines of its block is textually identical to the LLM deleting its own lines above and re-inserting them below, which is legitimate. Harmful effects are covered: `assume` never accepted in LLM code (strict), block facts are checked at every exit wherever the header sits, moves across blocks are rejected (context anchor), lines made dead are rejected (F7). Regression test a14b_* (passes). |

## Spec text changes for research/16 (coordinator to apply)

**§7.1, enforcement paragraph** — replace "(3) Mode is strict: every cup in LLM-owned code must be ..." through
"The round is accepted iff (1)–(4) hold" with:

> (3) Mode is strict: every cup in every LLM-owned function — touched by the round or not — must be **proven** or
> **assumed only through student-zone (instructor) axioms**, with an empty `depends_on_checks`; runtime-checked is an
> error. (4) Every harness `False` cup must be proven. (5) **The program must run.** The kernel's theorem is partial
> correctness (§6.1), which a body that never returns (`loop br end`, or a call to itself) satisfies for any spec. So
> `$main`, every harness, and every LLM-owned function whose parameters are all value parameters is run on up to 16
> inputs from its input list (§6.3) that satisfy its precondition and whose every argument is in 0..100; each run must
> finish within 1,000,000 steps and call depth 150. A run that runs out is an error only if it runs out inside an
> LLM-owned function (a costly student predicate is the student's business): `$isqrt(7) does not finish: $isqrt runs
> past 1000000 steps or calls`. In short, the submission is accepted only if every LLM-owned function is
> **strict-clean** and therefore VERIFIED (§4.1), and the program runs; the editor itself stays in gradual mode, so a
> rejected submission still runs. The round is accepted iff (1)–(5) hold; otherwise the kernel's diagnostics go back
> to the LLM.

**§7.2, mutation testing bullet** — append:

> If the original program itself does not finish on a harness input (the step budget runs out), the panel says so in
> red: a body that never returns satisfies any spec vacuously, and no mutant can be told apart on that input.


**§2 R7** — append: "A local's refinement may name other locals; it is the local's invariant, so a `local.set`/`local.tee`
of any local `$n` that the refinement of `$r` names also owes the cup `R_r[v := cur($r), $n := new]` (drawn on the
set line, kind Refinement of `$r`). A local's refinement may not call a memory-reading predicate (a store would
falsify it unseen); error on the local's line."

**§2 R9 / R14 (globals)** — add: "A global's refinement may name only `v` (and call pure, memory-free predicates);
naming a local or parameter, or reading memory, is a module error and the refinement is ignored. The initializer
must satisfy it (checked by evaluation, R28); otherwise a module error, and every function's copy of the refinement
is an assumption. Every `global.set $g` cup anywhere in the module that is not proven (unfed / runtime-checked /
resting on checks or assumes) is a dependency of `$g`'s refinement in *every* function: facts derived from it are
proven-relative-to those check lines (`*`) or assumed. (A caller still does not inherit a callee's internal checks;
a global's invariant is module-wide state, not a callee contract.)"

**§2 R33** — after "Ghost code may not contain loops, stores, or impure calls," insert: "may call (`call`) only
predicates (R29 keeps them total), has only fact results, and may recurse only directly through `lemma $self` with a
measure (R31); recursion through other lemmas is an error. A lemma is never the target of `call` (error: `$f is ghost
code: write lemma $f …`). These rules make every lemma total, which the erasure argument of §6 needs: a lemma that
could fail to return would 'prove' False and erase to `nop`."

**§2 R35** — add: "A pure call or load recorded in a shadow local is read by a check only if a capture of it dominates
the check (an earlier line whose enclosing block arms are all still open at the check); otherwise the host
re-evaluates the call. The top parameter of a loop is captured after the `loop` line (entry and every back edge).
Float terms are evaluated host-side as Wasm computes them."

**§2 R27** — replace the conversion bounds by: "defined iff lo < x < hi where lo, hi are the nearest values of the
source float type just outside the target range: for f64 sources −2^31−1 / 2^31 (i32_s), −2^63−2048 / 2^63
(i64_s); for f32 sources −2^31−256 / 2^31 (i32_s), −2^63−2^40 / 2^63 (i64_s); unsigned −1 / 2^32 or 2^64."

**§7.2 vacuity** — add: "Fact parameters are preconditions: witnesses must satisfy them too (evaluated on the run's
initial memory). A fact result the kernel proves with no hypotheses at all is **unconstraining** (a tautology). A
fact result merely implied by the preconditions (an invariant the function preserves) is not flagged."

## Results

- `cargo test`: 92 passed, 0 failed, 2 ignored (lib); 20 new tests in src/v2/gfix_tests.rs (f1×5, f2×2, f3×2, f4, f5×2,
  f6, f7, f8×3, f9, a14b) plus the copied fable_probes (3) and env-gated review_adv runner.
- Oracle 201/201. Fuzz (tests::fuzz) passes.
- Fable probes (fable_probes.rs): identical verdicts to baseline except A14a now lists 6 strict obligations instead of
  1 (F6 judges the untouched $gcd too); still not accepted. probes-after.txt.
- Kernel-review adversarial programs (adv/): only diff is the stale-hint now leading its diagnostic (adv-results/).
- clippy clean (native --all-targets and wasm32); cargo fmt applied.
- trunk --release build OK; all 13 v2 examples load headless with zero console errors (served from gfix/dist on :8977).

## Observations, not changed

- The v2 kernel already reported per-function verdicts correctly for F5 (partial correctness); only acceptance changed.
- F5's 'Feed::DeadCode on exit cups' criterion was not adopted: a correct body that ends in `return` has a dead `)`.
- Unknown runtime-check outcomes still pass silently (debug.rs/eval.rs). With F4/F8 the known sources are now only
  params below the top of a multi-param loop and multi-value join results.
- Review 20 §C.5 (DivS overflow on hypotheses, i128 back-substitution) and §B.2(4) (lazy `ite` division) are not in
  the §F list and were not addressed in this round.
