# 24 — Automatic subsumption: the kernel finds the arithmetic

Status: design change to `16-v2-design.md` (card R5a; edits marked **[R5a]**), 2026-10-24.

## 1. What changed

Before: a cup was fed by exact lookup of a lane fact, by evaluation of an all-constant goal, or by a `prove k` line
directly above, which handed the top `k` lane facts to the decision procedure (§3). Any goal that was not literally a
lane fact needed a `prove` line, and the student had to count `k`.

After: a cup that lookup and evaluation cannot feed, and that no pending `prove` takes, is fed **automatically** when
§3 proves its goal from the in-scope facts relevant to it (card R5a). The kernel:

1. collects the lane at the cup's line (plus the taken-edge fact of a `br_if`/`br_table` edge cup);
2. keeps the facts that share a non-constant value with the goal — looking through predicate unfoldings, so a memory
   predicate reaches the loads it reads — closed transitively, in rings of distance from the goal (for `False`, all);
3. runs §3 on ring 1, then rings ≤ 2, and so on, always handing facts over top of lane first; within a ring it first
   tries the facts that rest on no assumption or runtime check; after a cap on the whole set it tries the 8 closest;
4. on success, drops facts one at a time (weaker facts first, then oldest first) while §3 still succeeds, and records
   what is left as the cup's feed. Verdict, assumptions and check dependencies come from those facts, exactly as for a
   `prove`.

A cup an explicit `prove` took is never auto-fed, even if that `prove` fails: the override is final.

Refinements, block and loop types, refined locals, fact parameters, lemmas and axioms are unchanged. They are how
the program *states* what is true; R5a only removes the bookkeeping line that said "and now use arithmetic".

## 2. Why

The user, on the first v2 editor: "I sort of thought the refinements were going to be part of the types themselves,
as extensions or refinements of the original web assembly types. Are you sure there need to be these separate proof
lines?" And before that: "The necessary preconditions for a proof are really not visually obvious here. I'm writing
prove 1 but it really isn't showing me what it's trying to prove."

Both complaints point at the same design error. A refinement type `(i32 | v < n)` is a type; subtyping between
refinement types is the checker's job in every refinement-type system (Liquid Haskell, F\*, Flux). Making the student
write `prove 2` at each subsumption turned a type-checking step into a proof script, and the count `k` was an
artefact of the lane's stack discipline, not of the mathematics. Worse, the line said nothing about *what* it proved;
the goal lived on the next line's cup. With R5a the cup itself is the obligation, and the drawing (§4 below) shows the
obligation and its evidence where they are.

## 3. What `prove k` is still for

`prove k` keeps exactly its R32 meaning and is consumed before R5a is tried. It is never required where R5a succeeds.
It is useful when:

- **the relevant set is too big.** Relevance is transitive, so in a long function a goal can pull in many facts and hit
  §3's caps (cases, constraints, variables). R5a then reports `the 14 relevant facts exceed the solver's limits …;
  choose facts with prove k`, and `prove k` with a well-placed fact order solves it;
- **an author wants a particular derivation drawn**, for teaching (the override example keeps one, with a comment);
- **steering in vericoding**: an LLM can pin a proof to the facts it intends, so a failure names those facts.

What is *not* a use any more: the routine "the guard implies the bound" step. Those lines are deleted from every
example. The remaining ways to fail are about missing **facts**, not missing proof lines: a missing invariant, a missing
guard, or a nonlinear step that needs a lemma.

## 4. Design principle: automation removes typing, not visibility

A proof the kernel found is drawn exactly like one the student wrote. Concretely (16 §8):

- every proof cup writes its proposition in readable infix next to its line, without hovering (`x ≠ 0`,
  `u(r) ≤ 65534`);
- every automatically fed cup draws an always-on wire from each fact it used; each fact chip shows its proposition,
  and its origin (`br_if line 8 not taken`) on hover;
- the reason (1–3 lines, plain words) is shown under the focused or cursor line, and a **show all proofs** toggle shows
  every line's reason at once;
- ex falso and never-run cases say so in words on the line.

The old account was printed in the kernel's term syntax (`and(mul($x, 2), 1)`). One infix printer now renders every
proposition the student sees: chips, cups, accounts and error messages.

## 5. Costs: search, caps, determinism

**Search.** R5a is not proof search. Per unfed cup it makes one §3 call per relevance ring (two if the ring holds
facts resting on assumptions or checks), one more on the 8 closest facts after a cap, and `|Us₀|` calls to minimize,
where `Us₀` is the set that succeeded; in vericoding, one more to ask whether `Us` is contradictory (§6). Each call is
bounded by §3's caps (256 cases, 256 constraints, 24 variables, 64 terms per atom, and 32 atoms per call), and the
function's R5a calls together by a budget of 16384 enumerated cases, a deterministic measure of work. Cups fed by
lookup or evaluation cost nothing new.

**Caps.** The caps are unchanged. Relevance keeps the hypothesis list small in practice because most facts in a lane
are about other values. When it does not, R5a degrades the way `prove` does: the cup is unfed, with a message that
names the cap (and the countermodel of the 8 closest facts, if they had one) and suggests `prove k`. The fallback set is
chosen by relevance distance, not recency: the parameter and local refinements a proof usually needs are old but close.

**Determinism.** The candidate list is the lane in lane order (a function of the text). Relevance rings are computed
over that list. §3 is deterministic given its ordered hypotheses, and R5a always orders them top of lane first, as
`prove k` does (§3's tie-breaks follow variable numbering, i.e. first appearance, so the order is pinned). The ring
stages, the 8-fact fallback (ring, then recency) and the drop order (weaker, then older) are fixed; the budget counts
cases, not time. So the feed, and therefore the drawing and the verdict, is a function of the text alone, on every machine:
the property §4.2 of the design relies on ("no unknown").

**Measured cost.** See §7 for timings on the examples (native, release build).

## 6. Soundness

**R5a derives nothing a `prove` could not.** Every candidate is a lane entry at the cup's line, the same set a `prove k`
with large `k` would reach (the 8-entry limit of `prove` is a syntactic convenience, not a soundness condition; §3 is
sound for any hypothesis list). The procedure is §3, unchanged. So an R5a feed is a valid derivation in the existing
calculus, and the trap-freedom theorem (16 §6.1) covers it without change.

**Provenance is exact.** The verdict is computed from the minimized feed `Us` by the §4.1 rules: a fact resting on an
`assume`, an axiom, an unproven lemma or a runtime check passes that on. Minimization only removes facts that the
proof does not need, so it can only shrink assumptions and check dependencies, never hide one that the proof uses: the
final call on `Us` is itself a `Valid` derivation, and `Us` is what is recorded and drawn. Because the ring stages and
the drops try facts resting on no assumption or check first, a cup is proven whenever proven facts suffice
(review S1). One rule needed tightening: before R5a an `assume` in scope was usually consumed by some `prove k`, which
poisoned the function's VERIFIED status; R5a may now prove every cup without it. §4.1 always said a VERIFIED function has
no `assume`, and the kernel now enforces exactly that: a reachable `assume` line keeps the function from being
strict-clean, whether or not a cup rests on it.

**Stale (frayed) facts.** Fraying (R7, R11) is a drawing of scope, not a retraction: a fact about the old value `#m` of
`$x` is still true of `#m`. R5a uses such a fact only when the goal's terms reach `#m` — for example a loop back edge
after `local.set $i (i32.add $i 1)`, whose new `$i` is `add(#m, 1)` and whose bound needs the old guard on `#m`. A goal
about a new value unrelated to `#m` never sees it (it fails relevance), and the cup reports the stale-fact hint as
before. Memory-predicate facts carry their epoch in the term, so an old-epoch fact never matches or implies a
new-epoch atom.

**Ex falso and the vericoding lock.** In a contradictory context §3 proves any goal, so R5a feeds every cup there,
which an LLM could exploit by making a locked line unreachable by reasoning. The judge's rule (6) (research/22 B3)
already rejects a locked line whose lane proves False, independently of feeding. Because R5a can find a contradiction
in a small relevant subset when the whole lane exceeds the caps, the kernel records every feed (R5a or `prove`) whose
facts contradict each other, and marks *reachable only ex falso* every probed (locked) line at which all of those facts
are still in scope — so a contradiction R5a finds on an LLM-owned line also condemns the locked lines after it in the
same arm (review B1). A contradiction belongs to the lane, and the lane only grows until its arm ends, so this is exact.
Native tests: `probe_catches_contradiction_found_by_auto` (whole lane over the caps, recent facts consistent, the
contradiction `x < y`, `y < x` found only by R5a) and `auto_does_not_discharge_a_locked_line_ex_falso`.

**No new reach, and no less.** R5a never looks into callee bodies, across memory epochs, or through unfoldings except
as §3 already does (R29 non-recursive predicates, depth 4). Relevance is computed over the unfolded terms, so it is not
weaker than `prove k` there either: `rep_ok()@ε` reaches the loads it reads, which are the same ids as the program's
loads of the same address in the same epoch (review B3; test `relevance_looks_through_unfolding`). A memory fact still
has to be carried by a loop fact or a fact parameter.

## 7. Effects on the examples

**`prove` lines, before → after** (`v2-examples/`; fact-handle `local.get $h` lines that only staged a `prove` went
with it):

| example | before | after | note |
|---|---|---|---|
| parity, parity-bug-gate | 4 | 0 | |
| parity-missing-proof | 3 | 0 | redesigned: missing fact (below) |
| isqrt, isqrt-harness-bug | 6 | 0 | |
| isqrt-wrong-cup | 6 | 1 | redesigned: the one line is the seeded wrong override |
| isqrt-missing-invariant | — | 0 | new seeded bug |
| gcd, gcd-bug-guard, gcd-vacuous | 6 | 0 | |
| primality | 15 | 1 | one deliberate `prove 7`, commented: it saves ~17 ms of search on one arm |
| hashtable, hashtable-stale, hashtable-bug-tombstone | 12 | 0 | |
| even-shift | — | 0 | new; the readability benchmark |
| prove-explain (editor demo) | 1 | 0 | the user's `br_if`/`unreachable` program |

**Verdicts.** Every unchanged example keeps every cup's verdict, cup for cup (the oracle comparison requires it). The
only verdict changes are the two seeded bugs that stopped being bugs: `parity-missing-proof` (a deleted `prove 1`) and
`isqrt-wrong-cup` (a `prove` fed to the wrong cup) became correct programs once R5a fed those cups. They were redesigned:

- **missing fact** — `parity-missing-proof`: `$half`'s parameter lost its type `(i32 | $is_even)`; its result cup is
  unfed with the countermodel x = 1 (the name is kept for link stability);
- **wrong override** — `isqrt-wrong-cup`: a deliberate `prove 1` before `local.set $r` names only the fall-through fact
  `(r+1)² ≤ n`, which cannot bound `r+1` linearly; an explicit `prove` is final, so the cup stays unfed;
- **missing invariant** — new `isqrt-missing-invariant`: `loop $grow` lost its fact `sq_le(r, n)`, and both exits of
  `block $done` are unfed.

Review S6's third proposal, a **weak guard** (`65535 → 65536` in isqrt), turned out not to be a bug: the second exit
test `(r+1)² > n` already bounds `r`, and R5a proves the refined local's cup from it. `hashtable-stale` survives as is:
the stale guard is relevant (the new `i` is `i@old + 1`), and §3 answers with the countermodel `i = 7`.

The hand-derived oracle was re-derived mechanically: line numbers remapped through the deletion, formerly `prove`-fed
cups take their feed (`by: "auto"`, the facts used) from the kernel, and the comparison then demands the same verdicts.
One cup the hand oracle had missed (a dead-code block fact in the gcd family) is now recorded.

**Timings** (native, release build, whole module re-checked, editor accounts on; average of 20 runs):

| example | functions | auto cups | ms per module | ms per function |
|---|---|---|---|---|
| parity | 6 | 4 | 1.5 | 0.25 |
| isqrt | 4 | 6 | 1.2 | 0.31 |
| gcd | 10 | 6 | 2.6 | 0.26 |
| primality (with its override) | 13 | 14 | 12.4 (5.6 without accounts) | 0.95 |
| primality (override removed) | 13 | 15 | 27.5 | 2.1, one function ~20 |
| hashtable | 16 | 12 | 1.6 | 0.10 |

Minimization dominates where it costs anything: the expensive `$from_agrees` arm makes ~21 §3 calls of ~1–3 ms
each, because its proof is inherently case-heavy (about 200 cases even on its minimal facts). Chunked (halving)
minimization was tried and was slower there, since the costly calls are the successful ones. That arm is exactly what
`prove k` is still for, and the example says so in a comment.
