# 24 — Review of automatic subsumption (R5a), commit 28a2b48

Reviewer: Fable, 2026-10-24. Read: the diff to `16-v2-design.md`, research/24, research/18, the v2 examples. Code
checked on `codillon-refined` branch `proofs`: `src/v2/kernel.rs`, uncommitted `src/v2/kernel/auto.rs`,
`src/v2/solver.rs`, `src/v2/term.rs`. Uncommitted code is in flux; claims marked **[code]** were checked against it.

## 1. Verdict

**Sound as a calculus change; not yet acceptable as a spec.** R5a derives nothing `prove k` could not: every
hypothesis is a lane entry at the cup's line, the procedure is §3, and facts are about canonical ids, so stale locals,
other arms, epochs and ghost code need no new argument **[code: `relevant` reads `self.lane` plus the edge entry, the
set `lookup`/`prove` see]**. Provenance is not laundered: the verdict is the dependency closure of the minimized feed,
and the final call on `Us` is itself a valid derivation **[code: `cup_deps[c] = used`, closed in `finish`]**.

Three things block: the vericoding ex-falso story is weaker than research/24 §6 claims (B1); the infix printer hides
the one ambiguity the design cares most about, old versus new value of a local (B2); and relevance is computed before
unfolding, so R5a is weaker than `prove k` for memory predicates while the spec says it is exactly as strong (B3).
None needs a new mechanism.

## 2. Blocking

**B1 — the ex-falso probe misses contradictions R5a finds on LLM-owned lines.** Rule (6) asks whether the whole lane
proves False, falling back to the 8 most recent entries **[code: `lane_is_false`]**; the new sentence adds only a cup
*on a locked line* fed from contradictory facts **[code: `probe_ex_falso`]**. Scenario: in a 40-fact LLM body, @3
`u(n) < 8` (refined local) and @31 `u(n) ≥ 8` (an LLM guard) contradict; the whole-lane call hits `Cap(cases)`, the
top-8 call does not see @3. On line 33 an LLM cup about `n` gets `Hs ⊇ {@3, @31}`, is fed ex falso, and the locked
`block (fact …) ;; @own` on line 35 counts as reached. Before R5a the LLM had to find the pair; now the kernel finds it
on every unfed cup. Fix: a contradiction belongs to the lane, which only grows until the arm ends, so **an ex-falso feed
on line L marks every probed line from L to the end of the current arm**. One `contradictory(Us)` call per auto-fed cup.

**B2 — the printer hides which value a fact is about.** §8 prints locals "by name when unambiguous", but the old and
new values of one local are the ambiguity R7's stale hint exists for. In `hashtable-stale.wat` the chip `u(i) < 8`
(about `#m`) and the cup `65504 + 4·i ≤ 65532` (about `add(#m,1)`) both print `i`: a fact that reads as sufficient, no
wire, and a dotted "bad" connection with no visible reason. Fix: version names across `local.set`/`tee`/φ, current
value plain (`i`), older ones marked (`i₀` or `i@12`), so two ids never print alike; the stale hint uses the same names.

**B3 — relevance before unfolding makes R5a weaker than `prove`.** `ids(rep_ok()@ε)` is the call term alone, so load
facts `mem32[65504]@ε = 0 …` are irrelevant and `Hs = ∅`. But §3 unfolds `rep_ok` (R29) into loads keyed by
`(addr, ε)`, the *same* term ids as the real loads **[code: `Terms::intern` hash-conses `Key::Load(.., addr, epoch)`;
`symex.rs:135` builds that key]**, so `prove 4` over those facts succeeds where R5a fails, against R5a step 1 and
research/24 §6. Fix: define `ids(A)` on the atom **after** R29 unfolding to depth 4, or state the gap and keep
`prove k` required for memory predicates.

## 3. Should-fix

**S1 — minimization finds the first minimal subset, not the cleanest.** Drops are oldest first, kept on `Valid`
**[code: `auto_feed`]**. Lane: @5 `u(x) < 8` proven, @9 `u(x) < 4` from an axiom (or a φ re-entry with
`depends_on_checks`); goal `u(x) < 16`. Dropping @5 still proves, so `Us = {@9}`: assumed (or proven\*) though a proven
derivation existed, and VERIFIED is lost. Fix: try the assumption-free, check-free subset of `Hs` first; widen only if
§3 fails there.

**S2 — "adding R5a never changes a cup that `prove` fed" is false.** Auto facts enter the lane **[code: `produced`]**,
so a previously unfed cup now shifts the top-`k` of later `prove k` lines; adding a guard upstream can break a
`prove 2` downstream. Either exempt kind-*auto* facts from the count, or (my preference, since joins and overrides
can then use them) delete the claim and say in R32 that auto facts count.

**S3 — a failed explicit `prove` is final; say so.** Code skips R5a for a cup a failed `prove` was taken for
(`taken[i]`) **[code]**; the premise "that … a pending `prove` leave unfed" reads the other way. The code is right:
write *a cup consumed by a `prove`, successful or not, is never auto-fed*.

**S4 — pin order and fallback.** Spec: `Hs` "keeps lane order (oldest first)"; code passes top first, as `prove` does
**[code: `hyps.reverse()`]**. FM tie-breaks are by variable number, i.e. order of first appearance, so `Inexact` versus
`Valid` can depend on order near the caps; name one order or the oracle diverges. Code also falls back on `Inexact`
and adopts the fallback only when `Valid`; spec says `Cap`. Minimization keeps a fact on `Cap`/`Inexact` too; say so.

**S5 — the fallback is the wrong 8.** "Most recent relevant" drops the oldest facts, which are the parameter and local
refinements proofs usually need. Deterministic and better: relevance *distance* (facts sharing an id with `G`, then
with those, …), ties by recency; the failure text names the ring it stopped at.

**S6 — two of three seeded proof bugs vanish.** `parity-missing-proof` and `isqrt-wrong-cup` become correct programs;
`hashtable-stale` survives and improves (the stale guard *is* relevant; §3 answers `u(i)=7`). Fill research/24 §7
before the kernel lands: a **missing invariant** (delete the `loop (fact …)`: back-edge proven, nothing after the
loop), a **weak guard** (`65535 → 65536`, countermodel at the wrap), one **wrong `prove k`** in the override example.
The lesson research/18 §4 called a cost (counting `k`) goes; "which facts justify this" stays, on the wires. Note it in
18 §3.

**S7 — stale text.** §1.1 list (1 prove, 2 lookup); R24 "needs `prove 1`"; R26 feeds; §3.7 title "all on the `prove`
line"; §4.3/§5.1 `Feed` without `Auto` **[code has it]**; §5.2 order; §6.3 rule 2; §7.3 "count `k`"; §9 "re-cited
with a fact local" and Q4 (R5a answers *yes* after "v2 says no"); §8's first chip bullet ("text on hover") against the
new one.

## 4. Nits

- **N1** §3.1's call count omits the `contradictory(Us)` call that §8 and B1 need; and there is no per-function
  budget (200 unfed cups × 32 facts × 256 cases is bounded but slow in the browser).
- **N2** The "32 atoms" cap is not in code **[code: `CAP_TERMS/VARS/CASES/CONS` only]**; with whole lanes handed
  over it now matters. Add or delete.
- **N3** Code puts the countermodel inline (`the 3 facts about these values allow u(i)=8`) **[code]**; §3.7 says
  "on hover". Inline is right; align. When the fallback call returns `NotImplied`, report that countermodel, not the cap.
- **N4** Always-on chip text needs a layout rule (column width, wrapping); give the account toggle a default and say
  whether it persists.
- **N5** An ex-falso feed deserves a `⊥` glyph in the cup (like `=` for evaluation): a solid cup in a region that
  never runs is the one case where "drawn like a proof the student wrote" misleads.
- **N6** Research/24 §7 is empty and the examples still carry 100 `prove` lines; the change is undemonstrated until
  they are deleted and the oracle re-derived.
