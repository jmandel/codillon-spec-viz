# 24 — Automatic subsumption: the kernel finds the arithmetic

Status: design change to `16-v2-design.md` (card R5a; edits marked **[R5a]**), 2026-10-24.

## 1. What changed

Before: a cup was fed by exact lookup of a lane fact, by evaluation of an all-constant goal, or by a `prove k` line
directly above, which handed the top `k` lane facts to the decision procedure (§3). Any goal that was not literally a
lane fact needed a `prove` line, and the student had to count `k`.

After: a cup that lookup and evaluation cannot feed, and that no pending `prove` takes, is fed **automatically** when
§3 proves its goal from the in-scope facts relevant to it (card R5a). The kernel:

1. collects the lane at the cup's line (plus the taken-edge fact of a `br_if`/`br_table` edge cup);
2. keeps the facts that share a non-constant value with the goal, closed transitively (for `False`, all of them);
3. runs §3 once on them, and once more on the 8 most recent of them if the first call hits a cap;
4. on success, drops facts one at a time (oldest first) while §3 still succeeds, and records what is left as the
   cup's feed. Verdict, assumptions and check dependencies come from those facts, exactly as for a `prove`.

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

**Search.** R5a is not proof search. Per unfed cup it makes at most two §3 calls to decide (the relevant set; after a
cap, its 8 most recent members) and `|Us₀|` calls to minimize, where `Us₀` is the set that succeeded. Each call is
bounded by §3's caps (256 cases, 256 constraints, 24 variables, 64 terms per atom), so the worst case per cup is a
constant times the cap cost. Cups fed by lookup or evaluation, the large majority, cost nothing new.

**Caps.** The caps are unchanged. Relevance keeps the hypothesis list small in practice because most facts in a lane
are about other values. When it does not, R5a degrades the way `prove` does: the cup is unfed, with a message that
names the cap and suggests `prove k`.

**Determinism.** The candidate list is the lane in lane order (a function of the text). Relevance is a fixed point over
that list. §3 is deterministic given its ordered hypotheses. The 8-fact fallback and the oldest-first drop order are
fixed. So the feed, and therefore the drawing and the verdict, is a function of the text alone, on every machine:
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
final call on `Us` is itself a `Valid` derivation, and `Us` is what is recorded and drawn.

**Stale (frayed) facts.** Fraying (R7, R11) is a drawing of scope, not a retraction: a fact about the old value `#m` of
`$x` is still true of `#m`. R5a uses such a fact only when the goal's terms reach `#m` — for example a loop back edge
after `local.set $i (i32.add $i 1)`, whose new `$i` is `add(#m, 1)` and whose bound needs the old guard on `#m`. A goal
about a new value unrelated to `#m` never sees it (it fails relevance), and the cup reports the stale-fact hint as
before. Memory-predicate facts carry their epoch in the term, so an old-epoch fact never matches or implies a
new-epoch atom.

**Ex falso and the vericoding lock.** In a contradictory context §3 proves any goal, so R5a feeds every cup there,
which an LLM could exploit by making a locked line unreachable by reasoning. The judge's rule (6) (research/22 B3)
already rejects a locked line whose lane proves False, independently of feeding. Because R5a can find a contradiction
in a small relevant subset when the whole lane exceeds the caps, the kernel additionally marks a locked line
*reachable only ex falso* whenever a cup on it is fed (by R5a or `prove`) from facts that contradict each other.

**No new reach.** R5a never looks into callee bodies, across memory epochs, or through unfoldings except as §3 already
does (R29 non-recursive predicates). A memory fact still has to be carried by a loop fact or a fact parameter.

## 7. Effects on the examples

(Filled in after the kernel change: `prove` lines per example before and after, any verdict that changed and why,
the reworked seeded bugs, and timings.)
