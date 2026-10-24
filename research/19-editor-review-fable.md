# 19 — Editor review (phase D visualization, phase E vericoding), by Fable

Independent review of the editor side of Refined Codillon v2 on branch `proofs` of `codillon-refined`. Written
incrementally while phase E lands; the head reviewed is noted per section. Nothing here was committed to the branch.

Spec: 16-v2-design.md §4, §7, §8. Native look: 11-real-codillon-comparison.md.
Screenshots: `~/hobby/.agent-scratch/codalon-viz/vis-review/shots/`.

## Verdict

**Phase D: ship.** The drawing is honest (no cup is drawn proven without a `Proven` verdict; `*` marks every
check-relative cup), calm when proven, loud only on a real violation, grayscale-safe, native to Codillon's layout,
and cheap (1–7 ms). The departures from §8 that mattered (else-arm chips on the `if` line, bombs on unfed cups,
notes off-screen on wide programs) were fixed during the review and re-verified.

**Phase E: ship, as of ecdee1e (STATUS: DONE).** The boundary and the judge are sound against 26 adversarial
submissions, and the editor works fully without an LLM. Three blocking holes found by those probes (a
vacuous-precondition lemma proving anything; a duplicate-name lemma shadowing a student predicate; mutation kills
credited to the implementation's own invariants) were fixed and re-verified with the same probes. The lock in the
editor is the kernel's own zone check, sessions replay offline through the real kernel, the adequacy panel reports
vacuity and spec-only kills honestly and says how many inputs it used, and the OpenRouter path is opt-in,
key-gated, and keeps the key out of the page, URL and console. The should-fix list from the first UI pass (panel
overlap, hand-edit verdicts, dual-role lemmas, sessions after a live attempt, autocomplete under a refusal) was
closed in ecdee1e and re-verified.

**Residual, non-blocking:** a student line moved *within* its own block is not a boundary violation (A14b; harmless
for `assume`, which blocks VERIFIED anyway); `×` on the panel leaves vericoding mode rather than just hiding the
panel; the pinned failure note is ellipsized at `min(46vw, 640px)` and the stale-fact hint can be the part cut;
"HTTP 401: Missing Authentication header" for a fake key should be checked once with a real key.

## Blocking issues

**B1. A vacuous-precondition lemma proves anything (kernel R33, exposed by vericoding).** `lemma $f e…` emits
no cup for a *refined value parameter* of `$f`, only for fact params. So an LLM lemma with an unsatisfiable
refinement on a value param, `prove 1` to derive ⊥ from it, and `unreachable` has every result fact "proven" by dead
code, and the call site gets the result fact for free. The judge accepts the submission and `$gcd` and the harness
show VERIFIED. Reproducer (gcd.wat @5794629; lines 1-based):

```
138: lemma $vac2 $x $a $b          ;; replaces `unfold $gcd_ref $x $y`
139: nop                           ;; replaces `prove 3`
+   (func $vac2 (export "lemma:vac2") (param $x (i32 | (i32.lt_u v 0))) (param $a i32) (param $b i32) (result (fact (i32.eq $x (call $gcd_ref $a $b))))
+     prove 1
+     unreachable
+   )
```
Kernel output: `$gcd` cup @140 ResultRefinement Proven by `Lookup{origin 138}`; `$vac2` False cup Proven by
`prove 1` from the param fact, result cup Proven by `DeadCode`; no cup at all on line 138. Probe `A19` in
`vis-review/snap/src/v2/fable_probes.rs`. Fix: a refined value param of a lemma is sugar for a fact param (§1.3), so
the lemma line must carry a `Refinement{param}` cup for each, as `call` does (R13). (The same hole exists for a
student calling such a lemma outside vericoding; only the exploit is new.)

**B2. Duplicate function names bypass the ownership boundary.** The parser accepts two functions with one name and
`func_index` resolves to the first. `forbidden()` skips a new function whose name is already in `self.funcs`, and
`classify()` owns a lemma's header and body to the LLM. So the LLM can insert a *lemma* named like a student
predicate, placed before it, and every `call $is_gcd` now runs the LLM's body; the student's text is untouched, the
zone hash matches, and the judge says `accepted: $is_gcd, $is_gcd verified`. Reproducer (gcd.wat @5794629): insert
before line 73 (`(func $is_gcd …`):
```
(func $is_gcd (export "lemma:shadow") (param $g i32) (param $a i32) (param $b i32) (result i32)
  i32.const 1
)
```
Probe `A13`. Fix: make a duplicate function name a parse error in `Module::parse_lines` (the kernel should refuse it
regardless of vericoding), and in `forbidden()` compare by *index/identity*, not by name membership.

**Status of B1/B2:** fixed in 749bcd8 and re-verified with the same probes: A19 → `not accepted: ⟨u($x) < u(0)⟩
nothing feeds it` at the lemma line; A13/A17 → `rejected: redefines $is_gcd: a function name may be defined once`
plus a parse error `duplicate function name`. A10 (honest shift) still accepted.

**B4. Mutation kills are attributed to the implementation's own checks, not the spec (adequacy.rs `fate`).**
Mutants run instrumented in gradual mode, so a mutant that breaks the LLM's own loop invariant is "killed" by that
invariant's runtime check. On gcd @5794629, 18 of the 27 "killed by check" mutants die at lines 120/123/134 (the
LLM's `loop`/`block` fact clauses), not at the harness ⊥ or the header refinement. §7.2 defines a kill as a harness
reaching `unreachable` or a trap. The panel would therefore call a weak spec strong. Reproducer: probe
`fable_adequacy` (prints kills by line and the line's owner). Fix: instrument only spec-derived cups (harness `False`,
header/`ResultRefinement`, trap cups) when running mutants, and report "killed by spec" / "killed by own invariants" /
"runs away" separately.

**Status of B4:** fixed in 2347415 (`spec_cup` keeps only harness ⊥, result/contract refinements and trap cups as
checks for the mutation run; body invariants are set aside; a mutant caught only by them is `Fate::OwnOnly`, a
survivor; `RunsAway` is its own fate). Re-verified with `fable_adequacy`: on gcd the same 34 mutants now die 18 at
the harness `unreachable`, 5 at `i32.rem_u` (trap), 4 at the result refinement, 4 run away, 0 own-only; parity,
isqrt, hashtable, primality likewise report 0 own-only. The earlier "kills" were real after all, but now the panel
can prove it.

**B3. (phase D, visual) Failure commentary off-screen on wide programs.** See §1; `#ex=v2/hashtable-stale&step=fail`
at 1400 px: the darkred note starts at x = 1423.

**Status of B3:** fixed in 712aade (the code grid gets one window-wide column, `minmax(0, 1fr)`, so notes float at the
visible edge; lines wider than the window get `wide-line` and pin their note absolutely). Re-verified on my build of
2347415: at 1400 px the two notes on 323/324 end at x = 1377 (`e-stale-bomb.png`); in 390 px fit mode they sit at the
right edge like Codillon's own (`e-stale-phone.png`); 8 lines carry `wide-line`; console clean. Residual nit: the
pinned note is ellipsized at `min(46vw, 640px)`, and on 324 the cut falls exactly before the useful half ("… is about
the old $…" loses "set at line 318"); the hover title has it all. Consider putting the stale-fact hint first.

**Open blocking issues: none** as of 2347415. B1, B2, B4 (phase E) and B3 (phase D) are all fixed and re-verified.

## 1. Visual honesty and clarity (phase D @ 4170b58)

Reviewed from my own build of 4170b58 (`vis-review/dist-d`), 13 examples at 1400 px, crops at 2x, plus a 390 px
embed. Zero console errors or exceptions on any example. Proof-layer draw: 3.3 ms on hashtable (release, headless).

**The four states.** Checked on parity-bug-gate (lines 44–52), gcd-bug-guard (118–129), primality (84–90),
hashtable-stale (316–326); shots `d-*.png`, grayscale check `d-parity-gray.png`.

- *Proven*: solid purple diamond, solid 2 px wire from its chip. Reads at once. "Calm when proven" holds: gcd,
  isqrt, parity, hashtable, primality have no darkred anywhere; the only loud element is the VERIFIED seal.
- *Proven\**: same cup plus an indigo `*` at the upper-right corner (parity 51, 52; gcd-bug-guard 122). Legible at
  1x; the hover says "relative to checks at line 47". No dotted tails to the checks (known limit; see §2).
- *Assumed*: hatched fill at 70 % opacity, dashed wire, a small open circle at the corner (primality 89–90, gcd 153).
  Correct, but the palest of the four; at 1x the hatch reads as "light purple". The prove sockets inherit the hatch
  when the goal is assumed, which is right.
- *Runtime-checked*: empty, fade-up gradient, gray dashed rim, and a half-opacity 💣 beside it. Distinct from the
  others in color and in grayscale (empty dashed). See §2 on the bomb.
- *Refuted*: ivory fill, darkred broken double rim (dashed outer, solid inner), full 💣, darkred instruction text,
  bomb gutter glyph (gcd-bug-guard 125, parity 49, hashtable-stale 324). Unmistakable; the double rim survives
  grayscale.
- *Failed prove*: darkred dashed numbered sockets with dashed wires from the hypotheses taken (parity 46,
  hashtable-stale 323). Good idea and clear in color. In grayscale a failed socket and a runtime-checked cup are
  both "empty dashed diamond"; the socket's digit and the dashed wire are the only tells.

**Bug variants, two-second test** (fail step):

| example | what you see first | verdict |
|---|---|---|
| gcd-bug-guard | 💣 gutter + darkred `i32.rem_u` + refuted cup at 125; the guard's `local.get $x` is 3 lines up | obvious |
| parity-bug-gate | 💣 at `call $half` 49, failed socket at 46, two red notes | obvious |
| hashtable-stale | 💣 at 324; darkred fray at `local.set $i` 318 with a dotted bad connection down to the cup; failed socket at 323 | obvious, and the *cause* is drawn, not just the symptom; best frame in the set |
| isqrt-wrong-cup | one dashed cup at 57 with a faint bomb; "prove has nothing to feed" is far right on 59 | visible but quiet: nothing darkred near the code; you find it from the gradual badge and the far-right note |
| isqrt-harness-bug | red "could not decide (inexact step on wrap(mul…)); add a lemma" | fine (a text failure, as it must be) |
| parity-missing-proof | no darkred at all: a `1 runtime check` pill on the header and one quiet note | quiet by design (gradual mode); the pill is the only cue |
| gcd-vacuous, hashtable-bug-tombstone | identical to the clean versions (every function VERIFIED; the same 7 `$rep_ok`/`False` checks on hashtable) | expected: these are spec gaps, phase E's adequacy panel is the only place they can show |

**Fact lane legibility.** On hashtable and primality the lane holds at most two chips per line and the trunks are
slotted 3.5 px apart, so the long vertical runs (e.g. `$rep_ok` at 249, the loop fact over 316–326) stay readable.
Long trunks fade to 55 %, which keeps the function-length ribbons from dominating. Chip hover text is complete
(`fact ⟨…⟩ enters the lane (if else-arm); stale from line N`). The 2 px purple wires are clearly distinct from the
7 px pale value ribbons, as §8 asks.

**Misleading or dishonest?** No cup is drawn proven without `Verdict::Proven`; `look()` maps verdicts one-to-one and
`star` is set iff `depends_on_checks` is non-empty (proof_view.rs 108–117, 963). Two softer honesty points:

1. **Else-arm chips sit on the `if` line.** The kernel births the else-arm fact at the `if` (origin "if else-arm"),
   and the chip is drawn there, so its ribbon runs down *through the then-arm*, where the fact is false
   (gcd 9→15, primality 65→71, hashtable 47, 53, 73, 80, 132, 297). Hover text says "else-arm" but the picture says "in scope from
   `if`". Should fix: place the chip on the `else` line (or at `if` but start the trunk at `else`).
2. **VERIFIED on axiom-dependent functions.** primality shows 14 VERIFIED seals while 10 cups are assumed via
   instructor axioms (lines 112–116). This is what §4.1 specifies, but the badge gives no hint; a hatched cup under
   a VERIFIED seal invites "which is it?". Suggest `VERIFIED · 3 axioms` on the badge (and `A` on axiom chips, which
   §8 asks for and is missing).

**Native look.** Fractions left of code at indentation x, pale ribbons, rounded brackets (gray/green/purple/pink
frames are upstream Codillon's own, commit 1d592f5), navy chevron arrow, far-right darkred commentary, bomb and
✗ gutter glyphs: all preserved. The lane is a 28 px gap that the frames and arrow were widened to include, so
nothing of Codillon's moved. The proof lines (`prove`, `lemma`, `unfold`) in italic slate are a sensible echo of v1's
spec lines. Fact-clause washes (`(fact …)` on block types) are quiet and dashed.

**Phone fit** (`#ex=v2/hashtable&step=last&embed=1` at 390 px): the page scales to width (`d-phone-ht.png`), no
horizontal scroll (scrollWidth 390), badges and cups scale with it. Works.

**Commentary off-screen on wide programs (must fix).** Codillon floats the darkred note to the right edge of the
*line*, and v2's `(fact …)` block types make lines 2184 px wide on hashtable-stale. At a 1400 px window the failure
note for line 324 ("check failed: ⟨u(shl(add($i, 1), 2)) ≤ u(28)⟩ with $i = 7 — ⟨u($i) < u(8)⟩ (line 314) is about
the old $i (set at line 318)") starts at x = 1423, entirely off-screen; same for gcd-bug-guard's notes. The student
sees the bomb and must scroll right to read why. Reproduce: `#ex=v2/hashtable-stale&step=fail` at 1400 px. Fix:
pin the note to the viewport's right edge (`position: sticky; right: 0` on the comment span or a max-width tied to
`100vw`), or wrap it under the line when the line is wider than the viewport.

**Re-check after a01a8da + 712aade (my build of 2347415, `e-*.png`):** else-arm chips now sit on the `else` line
(gcd 12, 43, 50, 95; the ribbon no longer crosses the then-arm); runtime-checked cups carry a small gray stopwatch
(`.pv-watch`, no bombs left: `pv-bomb` count 0 on isqrt-wrong-cup, 1 stopwatch), though on `local.set $r` (isqrt 57)
it sits in the fray's hairlines and is hard to see at 1x; the seal reads `VERIFIED · 1 axiom` / `· 3 axioms` on
primality's four axiom-dependent functions; axiom chips carry a 7.5 px `A` (primality 84), legible at 2x, marginal
at 1x. All 13 examples: console clean, draw 1.2–7.2 ms.

## 2. Fidelity to §8: departures

| §8 says | built | judgement |
|---|---|---|
| Proof cup beside its operand, goal text in 8 pt under the cup | all proof cups right of the value cups, no goal text; goal only on hover | acceptable: the text would not fit at 45 px line pitch; hover carries goal + verdict + feed. Operand adjacency is lost on multi-operand lines (`i32.store` has two cups: address and value, both at the right) |
| Chip on every fact's birth line, ribbon runs for the fact's scope, cut at `end` | chips only for facts that feed something or that a stale hint points at; trunk runs to the farthest consumer (or to the fray) | acceptable, and better: a chip for every fact drowns hashtable. But the scope end is never drawn, so a student cannot see where a fact *stops* being usable unless it frays |
| Else-arm chip at the arm | at the `if` line → **fixed in a01a8da** (chip on `else`) | was should-fix (§1.1); verified |
| Runtime-checked: stopwatch tick | half-opacity 💣 → **fixed in 712aade** (gray stopwatch) | was should-fix: a bomb is Codillon's *trap happened* glyph and seven faded ones sat on the clean hashtable; verified, see the placement nit in §1 |
| Refuted: darkred double outline | dashed outer + solid inner | acceptable (reads as "broken") |
| False cup: inverted hatched diamond `⊥` | ordinary diamond with `⊥` text | acceptable |
| Assumed: small `A` on hover chip | open circle at the corner; nothing on the chip | acceptable; add `A` on axiom-born chips when cheap |
| Fray: 3 hairlines | 5 hairlines, darkred when a cup needed the fact, plus the dotted bad connection | good, exceeds spec |
| proven\*: dotted tail to each check | `*` only | acceptable for D; the hover lists the lines |
| VERIFIED seal only | VERIFIED seal, or a dashed `gradual` / `N runtime checks` pill | good addition: the pill is how you find the one unfed cup in isqrt-wrong-cup |
| Gradual run failure: 💣 on the line | 💣 on the line and beside the cup, instruction text darkred, slider failure pill outlined | good |
| `prove k`: k cups above the rule wired to hypotheses, output diamond below wired to the goal cup | as specified, plus failed-prove sockets in darkred | good |

## 3. Phase E: vericoding mode

### 3.1 Ownership boundary (code-level enforcement, adversarial edits)

Probes prepared against gcd.wat (student zone: lines 1–6 `$main`, headers, predicate/measure/harness bodies, the
axiom at 108; LLM zone: `$gcd` body 111–140, proof lines, lemmas). Each should be *rejected by the kernel* with the
reason the spec names, not merely blocked by a read-only widget:

| # | edit | expected |
|---|---|---|
| A1 | weaken the student header 110 to `(result i32)` | rejected: edited a locked line |
| A2 | replace `prove 3` (133) with `assume (fact …)` | rejected: assume in LLM code |
| A3 | add `(func $cheat (export "axiom:cheat") … (result (fact (call $is_gcd …))))` in the LLM zone and `lemma $cheat` | rejected: axiom defined by the LLM side |
| A4 | add a lemma with a fact result and an empty/unproven body, use it | rejected: assumed via a non-instructor assumption / lemma not strict-clean |
| A5 | change the harness body: `unreachable` (154) → `nop` | rejected: locked line |
| A6 | add `(import "env" "f" (func $f …))` | rejected: import |
| A7 | add an ordinary (non-lemma) function and call it | rejected: call to a function not in the module at session start |
| A8 | drop `prove 2` at 153 (harness proof line, LLM-owned) | rejected: harness `False` cup not proven |
| A9 | delete a student line (shortening a locked range) | rejected |
| A10 | insert an honest LLM line *above* the student zone (shifts every later line number) | must be *accepted*: the lock must follow content, not absolute line numbers |
| A11 | student header unchanged except trailing whitespace or a `;;` comment | either accept or reject, but deterministically and with a message |
| A12 | call `$gcd_ref_ok` (the axiom) with hypotheses the LLM "proved" via a runtime-checked chain | rejected: `depends_on_checks` non-empty |

**Results @5794629** (probe file `vis-review/snap/src/v2/fable_probes.rs`, `cargo test fable_probes -- --nocapture`;
the judge is `SessionStart::judge`, pure Rust, so the boundary is enforced in the kernel layer, not the UI):

| # | result | note |
|---|---|---|
| A1 | rejected: `edited a locked line: 110 (was …)` | good; the strict list still explains what broke |
| A2 | rejected: `adds an assume` | good |
| A3 | rejected: `adds an axiom ($cheat): only the instructor may` | good |
| A4 | rejected: `edited a locked line: 152 (was lemma $gcd_ref_ok …)` | the harness's proof lines are student-owned (harness *body*), so the LLM cannot write harness proofs at all; consistent with §7.1's table, but note that then §7.1 (4) is really a check on the *student's* text |
| A5 | rejected: locked line 154 | good |
| A6 | rejected: `adds an import ($oracle)` | good |
| A7 | rejected: calls `$helper` not in module; `adds a function ($helper)` | good |
| A8 | rejected (locked line; same as A4) | — |
| A9 | rejected: `adds a line to the locked spec` + `does not parse: function is not closed` | good; message is a little off (it was a deletion) |
| A10 | **accepted**: `$gcd verified` | good: the lock follows content order, not line numbers |
| A11 | rejected: edited a locked line | deterministic; trailing comments count as edits (acceptable) |
| A12 | (covered by A14b) `rests on runtime checks` → not accepted | good |
| A13 | **accepted** — see **B2** | duplicate-name lemma shadows a student predicate |
| A14 | moving an instructor `assume` within LLM code is *not* a boundary violation (`crossed=false`); the submission still fails strict mode because any `assume` kills VERIFIED | the zone is an ordered list of trimmed student lines, so a student line that moves among LLM lines is invisible. Harmless for `assume`; for a `;; @own` fact clause it lets the LLM move a student-placed invariant to another block. Should fix: record each student line's *anchor* (enclosing function + preceding student line) or forbid student lines inside LLM bodies from moving |
| A17 | shadowing `$gcd_ref` by a lemma: not accepted (strict), but again not a boundary violation | B2 |
| A18 | lemma with `unreachable` body: not accepted, `⟨False⟩ nothing feeds it` in the lemma | good |
| A19 | **accepted** — see **B1** | vacuous refined param on a lemma |

Second batch @749bcd8 (`fable_probes2`), all behaving:

| # | edit | result |
|---|---|---|
| A20 | add a lemma that is also a harness (`lemma:h2` + `harness:h2`) with body `unreachable` | not a boundary violation; not accepted (`harness $h2 is not VERIFIED`). Harmless to the judge, but `Bench::new` would treat it as a harness and use it to kill mutants; consider rejecting dual-role lemmas |
| A21 | lemma that is also `measure:gcd_ref` | not accepted (strict); same remark |
| A22 | append `;; @own` to an LLM line | rejected: `adds a line to the locked spec` |
| A23 | `call 2` (numeric index to a student function) | rejected: `calls 2, which is neither in the module nor a new lemma` (a false positive for honest numeric calls; acceptable) |
| A24 | add `(global …)` | rejected: adds a line to the locked spec |
| A25 | lemma with a `(fact (i32.const 0))` param, used to derive the result | not accepted: `⟨False⟩ nothing feeds it` at the lemma line |

Full suite at 749bcd8: 67 passed, 1 ignored.

Other code observations: `judge()` runs `check_module(&m, false)` (strict) on the whole module, and `strict_reasons`
reports cups only for *touched* functions plus every harness `False` cup and harness VERIFIED status; `touched()`
diffs trimmed function text by name, so a renamed lemma counts as touched twice (old gone, new added), fine.
`strict_ok` accepts assumptions only of kind `"axiom"`. `play_round` rolls back a crossing round and keeps a merely
unproven one, as §7.1 says.

### 3.2 Adequacy panel (vacuity, mutants) @5794629 (`src/v2/adequacy.rs`; probe `fable_adequacy`)

**Vacuity of preconditions** is sound as implemented: the function body is replaced by `prove k; unreachable`
(`k` = refined value params + fact params) and the row is vacuous iff the `False` cup is `Proven` by `Feed::Prove`
(not by evaluation or dead code). Across the 12 examples only `gcd-vacuous: $gcd_harness vac=true, witnesses 0/64`
is flagged; no false positive. The witness search tries at most 64 inputs (edge values, module constants ±1, a
deterministic xorshift sample), so "0 witnesses" is correctly a warning. Each vacuity pass takes 0.2–2.5 ms native.

**Unconstraining postconditions**: body `call $__havoc; prove k` with an injected import; "unconstraining" iff the
`ResultRefinement` cup is `Proven`. Skipped when the precondition is vacuous (right, since then anything proves). No
example trips it. One caveat: the havoc import shifts function indices by one and the code accounts for it (`f2 =
f + 1`), but only because the import is inserted at line 0; fine as long as that stays.

**Mutation testing**: M1–M6 are generated exactly as the table says, on `Owner::Llm` lines of non-lemma functions,
proof lines excluded; each mutant is run on the harness inputs whose *original* run succeeds within 100 k steps.
Determinism holds (xorshift seeds, fixed edge list). Timing native: gcd 34 mutants 47 ms, isqrt 24 / 106 ms,
hashtable 168 / 237 ms, so a browser pass is ~1–3 s and should run off the input path.

**Do survivors really survive?** Yes in the sense defined: no bench input distinguished them. gcd's three survivors
(`$x→$a`, `$y→$b` on the first iteration, `rem_u→rem_s`) are plausible equivalents or near-equivalents on the
inputs tried; hashtable's 99 survivors are mostly `local.get` swaps in branches the 16 inputs never reach. The
bench is small: `input_list` caps at 64 and, for two-parameter functions, the edge-pair grid alone is 100 entries,
so the xorshift sample is *never* reached (`out.truncate(cap)` after the grid); and `Bench::new` takes 16 witnesses
per harness. Survivors are therefore over-reported on anything with branches. Should fix: interleave the sample
with the grid, and let the panel say "on N inputs".

**Do kills mean the spec caught it? Mostly not — B4.** `fate()` runs the mutant *instrumented in gradual mode*, so
any unfed cup is a check, and `EvalErr::CheckFailed` kills. On gcd 27 of 34 mutants are "killed by check", but by
line: 120 `loop $euclid (fact …)` ×8 and 134 `br $euclid` ×7 (the LLM's own loop invariant), 123 `br_if $done` ×3
(the LLM's block fact), 126 `i32.rem_u` ×5 (a real trap cup: legitimate), 140 `)` ×4 (the student's result
refinement: legitimate). So 18 of 27 kills come from the implementation's *own annotations*, which the mutation
also broke, not from the spec. Same on isqrt (54, 61 `br_if`/`br`: LLM facts) and hashtable (252 `return` is the
header refinement, legitimate; but 222 `i32.load` bounds and the LLM block facts are not spec). §7.2 says a mutant
is killed only when "some harness reaches `unreachable` (or the mutant traps)". A panel built on this would tell the
student their spec is strong when it is the LLM's invariants that are. Fix: run mutants with checks only on
spec-derived cups (harness `False`, header refinements/`ResultRefinement`, trap cups R10/R11/R24/R25/R27) or on the
erased program, and classify kills by source so the panel can show "killed by the spec" vs "killed by its own
invariants". Budget exhaustion ("runs away": gcd 4, hashtable 3) is also counted as killed; acceptable, but it
should be its own column.

**"Proven" survivors.** isqrt reports six survivors the kernel still fully proves (`65535→65536` at 37,
`ge_u→gt_u`, `extend_i32_u→_s` …). §7.2 calls these "a definite spec gap"; they are not: an *equivalent* mutant
(e.g. `extend_i32_u→extend_i32_s` on a value proven < 2^31) is fully provable too. The panel should say "proven:
equivalent, or a spec gap" and let the student mark equivalents, as §7.2 already proposes for survivors.

### 3.3 LLM path (OpenRouter key handling, offline operation) @5794629

`src/v2/llm.rs` holds the protocol only: request/response JSON per §7.3 (module text with line numbers, locked
ranges, failing cups with their lane snapshots, line errors, rule digest, round counters, and the previous
judgement's reasons), `chat_body` (temperature 0, system prompt + one user message), `parse_response` (first `{` to
last `}`), `play_round`, the recorded-session format, and the `Live` state machine with a transport-agnostic
`next_body`/`on_reply`. No fetch, no key, no storage here; "never fires without a key" and "key kept out of
logs/URLs" are judged on the editor UI in §3.4 (both hold). `Live::on_reply` ends the session on the
first unparsable reply (`done = true`) rather than re-asking once; a model that wraps JSON in prose is handled by
`parse_response`, but one that returns two JSON objects is not. The three recorded sessions
(`public/examples/v2/sessions/{gcd,isqrt,parity}.json`) replay deterministically in the unit tests, so the offline
default of §7.3 is in place at the library level; the editor player is pending.

### 3.4 The editor UI @662301c (`src/vericode_ui.rs`, `vericode_html.rs`; my build `dist-e2`, shots `e2-*.png`)

**Lock refusal is the kernel's check.** `vc_guard` (vericode_ui.rs 286) runs `SessionStart::zone_violation` on the
edited text and bails out of the change handler, so the editor's refusal and the judge's rejection are literally the
same function; the UI adds a padlock, a shake and the note `locked: the runner $main — the student owns it`
(`e2-lock-refused.png`). Tested: typing into `i32.const 12` (student `$main`) leaves the text unchanged; typing into
`prove 0` (LLM zone) is applied and re-checked (`e2-llm-edit.png`). Locked lines get dimmer gutter numbers; 125 of
gcd's 155 lines are locked, which the panel states. One gap: a hand edit in the LLM zone is judged (badges update)
but the panel shows no accepted/not-accepted verdict for it; only session and live rounds do. §7 lets "the student"
play the LLM side, so the verdict line should follow hand edits too.

**Sessions.** `#session=gcd` loads the recorded start text and shows ⏮ / ▶ next turn / ⏭ all with `turn n/m`;
`#session=gcd&turn=1`, `parity&turn=1` land on the right turn. Playing gcd to the end goes through turn 3 `rejected:
adds an axiom ($gcd_step): only the instructor may` (the round is rolled back) and turn 4 `◆ accepted: $gcd
verified`, after which every badge is VERIFIED and the harness `VERIFIED · 1 axiom`. The transcript lists each
turn's note, edits, the kernel's reasons and the failing cups sent back with their lane snapshots. All offline:
zero network requests other than the page's own files.

**Adequacy panel.** Rows: `109 $gcd no precondition`, `140 $gcd_harness (harness) no precondition`, timings, then
`mutants 34/34 · killed by the spec 29 · 1 survive · 4 run away`, a per-operator line, and the survivor list; clicking
a survivor scrolls to its line, highlights it and shows `mutant M2 survives: i32.rem_u → i32.rem_s` with a small
overlay of the mutated operator (`e2-mutant-focus.png`). The "A survivor is an equivalent mutant or a spec too weak
to tell it apart" line answers my §3.2 note about "definite spec gap". Counts differ from my native probe (29 killed
vs 27, 1 survivor vs 3) because the panel's bench uses more harness inputs; the number of inputs should be shown
beside the mutant line, as the vacuity line already does. Mutation runs in the background (84 ms here) with the
interpreter depth bounded; no jank observed.

**Strict toggle / `#strict=1`.** On hashtable every runtime-checked cup turns into a darkred `strict: … needs ⟨G⟩;
nothing feeds it` note (7 of them) and the quiet notes vanish; the header pills still read `N runtime checks`, which
in strict mode should read `N unproven` or similar.

**OpenRouter path (checked with CDP network capture).**
- No key: the LLM section has only the key/model inputs and `save`; there is no ask button, and the page makes no
  request to any host but its own, across every deep link I loaded.
- Key saved: stored in `localStorage` (`codillon_openrouter_key`, trimmed), shown as `key ••••2345 (this browser
  only)`, input is `type=password`; the key does not appear in the page HTML, in the URL/hash, in the share link
  params (`link.rs` only knows `mode`, `session`, `turn`, `strict`) or in the console. `forget` removes it (the
  handler runs on a timer tick, so it is gone a moment after the click).
- Ask: exactly one `OPTIONS` + one `POST https://openrouter.ai/api/v1/chat/completions` with `Authorization`,
  `Content-Type`, `X-Title`; the body is the §7.3 request (module text, locked ranges, cups, rules) and never the
  key. With a fake key OpenRouter answered `HTTP 401: OpenRouter: Missing Authentication header`, shown in a darkred
  box (`e2-llm-asked.png`). The header was on the wire per CDP, so this is probably OpenRouter's wording for an
  invalid key, but it is worth one try with a real key. The default model string is a product name
  (`anthropic/claude-sonnet-4.5` here, `claude-opus-5.5` in d889640); fine as a default, since the student edits it.
- After a live attempt the SESSION block switches to `live session · round 1/6` and the three recorded-session
  buttons disappear; a reload brings them back. Should offer a way back without reloading.
- Persistence choice: the key survives browser restarts (localStorage, not sessionStorage). Acceptable given the
  explicit "(this browser only)" and `forget`, but a shared classroom machine argues for sessionStorage.

**Panel layout (should fix).** The panel is `position: fixed`, 399 px wide at the right of a 1400 px window, and the
text column gets no right padding, so code wider than ~986 px runs under the panel: every function header with a
refinement (gcd 19, 33, 61, 104–109, 140) and every `(fact …)` block line is cut (`e2-gcd-top-panel.png`,
`e2-mutant-focus.png` lines 117/119). Those are exactly the student's locked spec lines, the ones vericoding mode is
about. The pinned commentary and badges already stop at the panel's edge (356ce71 says "wide-line badges pinned"),
but the text does not. Fix: give the document `padding-right` equal to the panel width while `vc-on` (so the
horizontal scroll reaches the end of the line), or let the panel push the layout instead of overlaying it.

Also: the autocomplete popup (`i32.const`) still opens when typing on a locked line, under the refusal.

**Re-check at the head, 356ce71 (my build `dist-e3`, `e3-*.png`).** gcd-vacuous in vericoding mode now flags the
spec gap in three places: a darkred `vacuous spec: the kernel proves this precondition false…` note on the harness
header, a boxed `$gcd_harness (harness) VACUOUS … 0/64 inputs satisfy it` row, and `No harness input satisfies a
precondition, so no run can tell a mutant apart: every mutant survives` above the 34 survivors (capped list). The
vacuity line now says `64 evaluated inputs per function`; parity shows `precondition satisfiable (31/64 inputs)`.
Panel line numbers follow the gutter (110/141, matching the editor). Badges on wide headers are pinned at the
panel's edge (they now overlay the cut text: readable, a little untidy); the code text itself still runs under the
panel, so the overlap item above stands. Default model string is `anthropic/claude-opus-5.5`. Native suite at the
head: 70 passed, 1 ignored; console clean on all 13 examples and on the `mode=vericode`, `session=`, `strict=1`
deep links.

**663527f (model presets).** Settings only: two presets (Claude Opus 5.5 default; DeepSeek V4.1 Flash with
`provider.sort = throughput`) plus a custom id, the choice stored in `localStorage` beside the key; `max_tokens`
32 000. Key handling is unchanged (still only in the `Authorization` header). Unit tests check the request body
(`provider` absent for the default, present for the throughput preset). Native suite 70 passed. Not rebuilt for the
browser; nothing here touches the kernel, the lock or the drawing.

**ecdee1e (should-fix round), final pass on my build `dist-e4`, shots `e4-*.png`, STATUS.md now DONE.**

| item | result |
|---|---|
| panel covers the code | fixed: the listing is pushed (scrollWidth 2930 → 3243); scrolling to x = 1858 moves header 6's right edge to −430, i.e. wide lines scroll out from under the fixed panel; the pinned badges remain |
| collapse | `×` collapses to a `vericode` tab at bottom-right (`e4-collapsed.png`). Note it also *leaves* vericoding mode (body loses `vc-on`, locks lift); the tab re-enters. Acceptable, but a student may read `×` as "hide the panel", not "unlock the spec" |
| embed / fit (390 px, `embed=1`) | the panel is `static` and stacks below the listing (`e4-phone-vc.png`); no horizontal scroll |
| hand edits judged | typing `3` into `prove 0` now shows `rejected: does not parse: unknown instruction `pro3ve`` in the panel |
| autocomplete under a refusal | none: typing on a locked line shows only the padlock, shake and note |
| recorded sessions after a live attempt | the three session buttons stay (`load` ×3) |
| student line moved | A14c (assume moved out of the loop to function level) → `rejected: moved locked line 118 (…) out of its place ($gcd/block $done/loop $euclid → $gcd/)`. A14b (moved within the same block) is still invisible: the anchor is function + enclosing blocks, not order within a block. Residual, low: an `assume` blocks VERIFIED anyway; a `;; @own` block line moved within its parent block is the remaining case |
| one role per function | A20/A21 → `does not parse: $h2 has 2 roles (lemma, harness); a function may be one of lemma, axiom, harness, measure` |
| harness inputs | panel: `mutants 34/34 on 24 harness inputs`; `vacuity … 64 evaluated inputs per function` |
| key path re-run | unchanged: no request without a key; one OPTIONS + one POST with `Authorization` on ask; key absent from page/URL/console; `forget` clears storage |
| console | clean on all 13 examples and on `session=isqrt|parity|gcd`, `hashtable&mode=vericode&strict=1`, `primality&mode=vericode` |
| native suite | 72 passed, 1 ignored (my 3 probe tests included) |

## 4. Bugs: console, interactions, performance

Phase D @ 4170b58, own build:

- Console: no errors, warnings, exceptions or failed loads on any of the 13 examples at `step=last` and
  `step=fail`, nor on the 390 px embed, nor while editing.
- Live edit: clicking into `i32.const 12` on gcd and inserting a character re-ran erasure, kernel, run and draw with
  no console output; the malformed line got Codillon's darkred "unknown operator" note, the badges stayed, and
  restoring the text restored the proofs. Proof draw 2.1 ms after the edit.
- Performance: `codillonProofMs` 3.3 ms on hashtable (674 SVG paths, 58 proof wires, 20 chips), well under a
  frame. The proof layers are re-rendered as two `innerHTML` strings with a string-equality cache
  (graphics.rs `set_proof_layers`), so an unchanged scene costs one string compare.
- Slider vs. refutation: at `#ex=v2/gcd-bug-guard&step=5` the refuted cup and its 💣 stay drawn at line 125 (the
  refutation is a fact about the run, so this is right) but the "check failed … with $y = 0" note is gone, because it
  rides on Codillon's per-step `runtime_error`. The hover still says "refuted by the run". Minor: consider keeping the
  note as a quiet note at other steps.
- Visual: the failure commentary can land off-screen on wide programs (§1, must fix). No other layout faults seen:
  no cup overlaps a value cup on any example; prove sockets squeeze to 2.5 px half-diagonal only when a line has
  more than ~6 hypotheses (none in the examples has more than 4).

## Method and log

- Snapshot clone `~/hobby/.agent-scratch/codalon-viz/vis-review/snap` (never the working tree); wasm builds
  `dist-d` (4170b58), `dist-e` (2347415), `dist-e2` (662301c), `dist-e3` (356ce71), each served locally.
- Headless Chromium over CDP: `vis-review/drive.mjs` (navigate, eval, click, key, clip/viewport/full shots, console,
  exceptions and network capture) and the phase-D driver `vis/shot.mjs` for the 13-example console sweeps.
- Adversarial and adequacy probes as a Rust test module added only to the snapshot:
  `vis-review/snap/src/v2/fable_probes.rs` (`cargo test --release fable_probes fable_probes2 fable_adequacy --
  --nocapture`), 25 boundary probes A1–A25 and per-example vacuity/mutation dumps.
- Commits reviewed in order: 4170b58 (D) → 5794629 (E core) → 749bcd8 (B1/B2) → 2347415 (B4) → a01a8da, 712aade
  (D fixes) → 662301c (UI) → d889640 → 356ce71 (UI polish) → 663527f (presets) → ecdee1e (should-fix round;
  STATUS DONE). Native suite at each: 67 → 70 → 72 passed. Wasm builds: `dist-d`, `dist-e`, `dist-e2`, `dist-e3`,
  `dist-e4` (ecdee1e).
- Shots in `vis-review/shots/`: `d-*` phase D at 4170b58, `e-*` at 2347415, `e2-*` at 662301c, `e3-*` at 356ce71,
  `e4-*` at ecdee1e.
