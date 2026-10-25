# 25 — Review of the R5a implementation (fork 5402fba..75568a2)

Reviewer: Fable, 2026-10-24. Read: `src/v2/kernel/auto.rs`, `kernel.rs` (`feed`, `finish`, `closure`,
`lane_is_false`, `stale_hint`, `refresh_view`), `solver.rs`, `solver/explain.rs`, `pretty.rs`, `vericode.rs`,
`proof_view.rs`. Probes ran natively in a scratch worktree (`fable_r5a_probes.rs`, 15 programs); accounts were read
from the live editor (`&proofs=all`, DOM dumped headless) for parity, even-shift, isqrt, isqrt-missing-invariant,
gcd, primality, hashtable-stale. Each item says **ran** or **reasoned**.

## 1. Verdict

**The kernel is sound and deterministic; the text it shows is not yet honest enough to ship.** Every adversarial
program behaved: auto-feeding never produced a Proven cup that an explicit `prove` could not. Stale locals, other arms,
joins, loop exits, memory and global epochs, `br_table` edges, dead-code `assume`s and unproven lemmas all fail or
inherit the right assumption (probes P1–P7, **ran**). Provenance is not laundered: the verdict is the dependency
closure of the minimized feed (`finish` → `closure`), clean-first picks the proven derivation when one exists (P9:
the axiom-only proof stays Assumed), and a non-minimal feed after a cap can only keep *more* dependencies. The
per-function case budget is order-independent across functions and never bites in practice (largest observed:
342 cases, `$from_agrees`; budget 16384). Same text gives the same output; no `HashMap` order reaches the output
(`first_bind` and `tight` are keyed lookups, `model` and `memo.keys()` are sorted).

What blocks is the printer: an id that moves from one local to another is renamed, so the gcd back-edge account
says the proof used `x ≠ 0` for a test the student wrote on `y`. Two should-fixes follow from the same corner:
the stale hint fires on a goal that is itself about the old value, and the promised countermodel is missing for the
commonest stale pattern (`i + 1`). The reachable-`assume` rule is right, but the judge does not report it.

## 2. Blocking

**B1 — a value that moves to another local is renamed in accounts (honesty).** `refresh_view` names each id by the
local *most recently bound* to it, and `i@L` versions only mark older values of the *same* local. After
`local.get $y; local.set $x` the old `y` id *is* the current `x`, so every fact about it reprints as `x`. Live gcd:
line 119 shows `gives y ≠ 0 if not taken`; the back-edge account on line 129 says `② x ≠ 0 — br_if on line 119 not
taken` and `① gcd_ref(x@116, x) = (x = 0 ? x@116 : gcd_ref(x, y)) — unfolded on line 124`, while line 124's own chip
reads `gcd_ref(x, y) = (y = 0 ? x : gcd_ref(y, t))`. The same fact has two spellings and the second attributes to
`x` a test made on `y`; a student checking the account against line 119 will conclude the solver is wrong. On line 116
the one id prints as `a` in the chip and `x` in the cup on the same line. **Ran** (live dump, gcd lines 116–129).
Fix: a fact keeps the names it was born with, versioned by the binding at its birth line (`y@119 ≠ 0`, or `y ≠ 0` with
the chip's own text), rather than being reprinted in the cup's view; §8's rule "two ids never print alike" needs
the converse, "one id prints one way".

## 3. Should-fix

**S1 — the countermodel is missing whenever the goal contains an `add`.** `render_model` keeps only `Term`/`Res`
variables; for `u(x) < 8 ⊢ u(x + 1) < 8` the solver returns `NotImplied([])`, so `auto_failure` prints nothing and the
line reads bare `needs ⟨u(x + 1) < 8⟩; nothing feeds it`. With `i32.shl` or `i32.mul` in place of the add the same
program prints `allows x = 4`. The flagship seeded bug has exactly this shape: `hashtable-stale` line 309 prints the
stale hint but not the `i@296 = 7` that research/24 §7 and §3.7 promise. **Ran** (P14; P13).

**S2 — the stale hint fires on a goal that is itself about the old value.** `stale_hint` asks only "goal mentions
`new`, some fact mentions `old`"; when `new` is a subterm of `old` (`i := i + 1` then `i := x`, so old `i` = `x + 1`
and new `i` = `x`) a cup about the old value gets `⟨u(i@14) ≤ 8⟩ (line 16) is about the old i (set at line 21)`,
naming a later set and a fact about the very value the goal is about. Require that the goal does *not* mention
`old`. **Ran** (P1 line 22).

**S3 — the judge accepts a function the new rule says is not VERIFIED.** `strict_reasons` reports cups and line
errors, never `strict_clean` itself. A judged function with a reachable instructor `assume` (allowed by `classify`)
and every cup clean yields no reason: `accepted: nothing changed; all verified` while `$f.verified = false`. With a
harness calling it the reason surfaces indirectly (`harness $fh is not VERIFIED: $f is not`). **Ran** (P12a/b).
Add a reason on the assume line when `!strict_clean` and nothing else explains it.

**S4 — "the facts of line 55 contradict each other" for one fact.** parity line 56 and even-shift line 42 are each
fed ex falso from a single fall-through fact that is impossible after unfolding; the label and the account ("these
facts cannot all hold together") speak of several. Say `the fact of line 55 cannot hold`. **Ran** (live).

**S5 — auto accounts list every fed fact as used.** `cup_account` for `Feed::Auto` prints all `hyps` without the
`(not needed)` mark the prove account has from `explain.used`. The sets agree while minimization completes; after a
`Cap`/`Inexact` drop or the budget they do not, and the label's `✓ from lines …` names facts the proof does not use.
**Reasoned** (no probe reached the budget: the `≠`/wrap splits are lazy, so 40 cups × 10 facts cost ~1 case each).

## 4. Nits

- **N1 Reachable-`assume` rule: right, reporting incomplete.** Dead-code assumes are ignored (P7 `$g` stays
  strict-clean; its fact never leaks, P7 `$f`), a lemma's assume propagates to callers as `assume` not `axiom`
  (P7 `$lm`/`$u`), predicates reject it. Only S3 is missing. **Ran.**
- **N2 Vericoding, no regression.** B1's fix holds: an ex-falso feed is recorded in `contras` and `lane_is_false`
  consults it while the set is in scope. The remaining gap (a consistent minimal subset proves the locked cup while
  the lane is contradictory beyond the top-8) existed for `prove k` too. Budget exhaustion can only unfeed the
  attacker's own cups; `contradictory` and `lane_is_false` are not budgeted; the counter is per `Pass`, and swapping
  function order leaves every cup identical (P11). **Ran** for the budget, **reasoned** for the probe.
- **N3 Clean-first trusts facts whose cleanliness is not known yet.** `clean()` at feed time sees a loop invariant
  as clean before its back edge is judged; the final verdict is right (`closure` runs in `finish`), but minimization
  may keep the loop fact over a proven alternative and lose VERIFIED. **Reasoned.**
- **N4 Wording.** isqrt 33: `using no facts … the facts' bounds would leave u(n) no possible value`; isqrt 55:
  `If computing r wraps around` where `r` means `r@33 + 1`. **Ran** (live).
- **N5 The 16384 budget is unreachable in practice** (max 342 observed) and the clean-first call repeats the previous
  ring's full call when the new ring adds only unclean facts. Harmless; the "0.1 s" note is unverified.
  **Reasoned.**
- **N6 Honest accounts checked and found right:** parity 38/45/48, even-shift 25/39, isqrt 37/55 (`r@33`),
  isqrt-missing-invariant 59 (`relative to the checks on lines 37, 50`), primality 103 (`assuming line 107`), gcd 71
  (`⊥ … (assuming line 105)`). Version names `result@48`, `r@33`, `x@116` are correct for same-local history.
  **Ran** (live).
