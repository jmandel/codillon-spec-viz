# Synthesis: what a refinement-typed Codillon should draw

Coordinator write-up, 2026-10-23 (all ten prototypes reviewed). Inputs: the seven research documents, the ten prototypes in `artifacts/`,
the builders' self-scores and my review notes (07). Section numbers refer to files in this directory.

## 1. The vision, in one paragraph

Codillon already treats *validity* as something you see rather than read: types are shapes, dataflow is
curves, badness is dark red, and the program runs on every keystroke with a time-travel slider. The next
version keeps every one of those commitments and adds one idea: **a type is a set of values, and a refinement
is a smaller set drawn inside it.** `(i32 | even $v)` is half of the i32 rectangle; `(i32 | 0 <= $v < $n)` is a
window whose right edge is tethered to another value; a loop invariant is the set of states allowed at the
loop head; a hash table's representation invariant is the set of memories that line up with the ghost map.
Specification adherence then reduces to four visible situations, and every prototype had to make them
distinct: a value *outside* its set (runtime), a set that does not *fit* inside the set it flows into (static),
a fact the checker *cannot establish* (unknown), and a spec that *excludes nothing* (vacuous). Semantically
this is 01's design: refinements are Lean subtypes, stack types are Σ-telescopes, loops are tail-recursive
definitions with `termination_by`, proof-step lines are `have`/lemma application/`sorry`, every predicate is
decidable so an unproven obligation degrades to a runtime check (💣), and the checker's output is a *residue*
of obligation records each carrying a site, a status, a counterexample and a replay handle.

## 2. What Winstein's existing choices demand (04 §1, condensed)

No error panel; the program always runs even when wrong; silence means success; absence is drawn as a shape
(empty cup, stranded output, dashed synthetic `end`); badness is drawn as *frustrated intent* (a bad connection
reaching for a cup); identity is preserved across edits by tweening; runtime values live inside the shapes.
Every prototype was held to these, and the ones that score best are the ones that found the *existing* idiom to
extend rather than a new panel to add.

## 3. The six epistemic states (05, end)

| state | look |
|---|---|
| proven | nothing: gray line number |
| refuted, witness replayed | darkred, solid; `⚖` in the gutter; darkred slider pill |
| refuted, witness not replayed | darkred outline only; dashed ghost track above the slider; hollow `⚖` |
| held on this run only | slategray dotted; `∘ N` count; never a check mark |
| unknown / needs hint | indigo dashed, `?`, Codillon's mystery star |
| assumed / vacuous | ghosted 50%, hollow, `○`; everything downstream ghosted too |

All ten prototypes implement this table and all ten pass a grayscale check. The most important distinction
in practice turned out to be *proven* vs *held on this run only*: Codillon's slider makes every step look
fine, so "observed OK" must never be drawn like "proved". Prototype 05's rule (cell fill from the run,
border and glyph from the checker) is the cleanest implementation and should be adopted everywhere.

## 4. The ten prototypes: verdicts

Self-scores are the builders' (rubric in 04 §4: Salience, Blame, Grayscale, Vocabulary, Predicate-on-shape,
Causal trail, Witness, Ink, Scale, Edit continuity). My one-line verdict follows.

| # | idea | self-score (mean) | verdict |
|---|---|---|---|
| 01 | Shape as value space, spill glyph | 3.6 | **Core primitive.** The best predicate-on-shape of the ten; the spill is the right picture of a failed subtyping check. Costs shape width (30 → 140 px) and needs hover zoom. |
| 02 | Wraparound ring, twin ticks | 3.9 | **Keep for integers.** The only honest picture of Wasm's signless integers; the comparison operator as a cut at its seam is a real teaching device. Works as a lens, not as an always-on margin glyph. |
| 03 | Sequent fractions | 4.0 | **Core primitive.** Extends the existing fraction with the least new vocabulary; the rule-as-verdict and the empty cup for a missing fact are exactly Codillon's idiom. Chip density is the risk. |
| 04 | Fact ribbons | 3.8 | **Keep as the trail, on selection.** Facts born (✦), carried and frayed along the dataflow curves, with a ghost lane from a hollow badge back to the fray: the best causal trail of the ten. Too much ink always-on; needed *fact rails* for non-dataflow facts. |
| 05 | Invariant horizon, lap chart | 3.6 | **Keep for loops, on selection.** The gate/horizon/lap chart answers "which lap broke which conjunct" better than anything else; too tall to be always on. |
| 06 | Model / memory mirror | 3.8 | **Keep for data structures.** Representation invariants as geometry (strings, arcs, gaps) is the right picture; the "R open" gray mid-operation state is essential to keep the clean run calm. |
| 07 | Witness track | 3.8 | **Core mechanism.** Counterexamples as runs on a ghost track that replay onto the real slider; the substituted-predicate card is the best "why is this false" rendering. Complements, does not replace, the shape-level ideas. |
| 08 | Spec sampler | 3.5 | **Keep as a coverage layer.** Patterns (edges only, everything, nothing shaded) diagnose off-by-one, wrong spec and vacuous spec at a glance; must stay visibly subordinate to proof. |
| 09 | Envelope strips | 3.6 | **Keep for time.** Best single rendering of the overflow story (product line over the 2³¹−1 ceiling with the machine-reading echo); checkpoint discipline mirrors 06's "R open". |
| 10 | Synthetic proof holes | 4.2 | **Core mechanism.** A failed obligation becomes an inserted hole line with suggestion chips, exactly like the synthetic `end`; the only prototype with a real edit loop (accept, fly, re-derive, shake, undo). |

## 5. A composition, not a winner

The composition below is implemented as a single tutorial page, `artifacts/00-refined-codillon.html`, specified in
09-walkthrough-design.md. It is the page to read first.

The prototypes are not alternatives. They sort into three layers, and a coherent product takes one or two
from each:

1. **Always-on, per line (the margin).** 03's sequent fraction carrying 01's regions inside the shapes, with
   the spill glyph for a failed fit and the empty fade-up cup for a missing fact. One new gutter glyph (`⚖`)
   and the six-state styling. Nothing else is permanent.
2. **On failure (the residue).** 10's hole line appears after the offending instruction with the goal,
   the witness values in shapes, and chips. 07's ghost track / witness pill puts the counterexample on the
   slider; scrubbing to it fills the hole's shapes with live values and shows the substituted-predicate card.
   Clicking a hollow badge or a broken rule lights 04's ribbon trail back to the instruction where the fact was lost.
3. **On selection (the lenses).** Pin a value to get 02's ring (integers) or 09's strip (over time); pin a
   loop to get 05's lap chart; pin a memory region to get 06's mirror; pin a function header to get 08's
   relation plot or grid. Lenses are the place for density; the margin is not.

Two rules fell out of the review that no single idea doc stated: put `⚖` *both* at the obligation site and at
the line to change when they differ (03, 10), and distinguish "fails mid-operation but recovers by the
boundary" from "stays false" with a gray open state (06, 09, 05).

## 6. What the sample programs taught

- isqrt's overflow is unreachable on the slider (step ≈695k), so a static counterexample *must* be
  renderable as a one-iteration loop-head replay. Every prototype implemented this; 05's "⋯ 46 340 laps not
  run" hatch and 07's before/after card are the models.
- The tombstone bug never falsifies R; it falsifies a stronger property the buggy lookup silently assumes.
  The prototypes that drew that stronger property as its own chip (06, 05, 01, 10) made the bug legible; this
  is the "your code is fine, your spec is short" case from 04 F6, and it is the most teachable of the five.
- Clause (iv) of R as first written did not guarantee termination with tombstones (03 §B.2); the fixture
  corrected it. A spec bug in the brief itself is a good argument for 08's sampling layer.

## 7. Open questions

- Shape width. 01 needed 140 px rectangles; Codillon's are 30 px. A fixed-width glyph with hover zoom, or
  variable width only for refined values, is a design decision with layout consequences.
- Chip vocabulary. 03 and 10 each invented ~30 tiny icons. They need one shared set, and a legend that students
  can learn in a lesson.
- Lemma obligations. Builders disagreed whether to show the nonlinear isqrt lemma as unknown, dynamic or
  proven by default; 01 §2.6's rule (unknown is never shown as success) should decide it.
- Proof wires (unsat cores as curves, 01 §8) were drawn by 03 and 10 only on hover. Whether they belong
  always-on is untested.
- Everything here is mocked: the verdicts come from the fixture, the runs from small JS interpreters. A real
  checker (Z3/cvc5 in wasm, per 01 §2.6) with a 200 ms budget per obligation is the next engineering question.
