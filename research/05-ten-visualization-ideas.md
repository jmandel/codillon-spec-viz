# Ten visualization ideas for spec adherence in a refinement-typed Codillon

Author: coordinator (Claude), 2026-10-23. These are the ten concepts to be prototyped as ten
separate HTML artifacts. They all build on Codillon's existing vocabulary (see 00-codillon-today.md):
type = shape, dataflow = connection curve, badness = darkred, runtime = slider, one row of
annotations per instruction line, no error panels.

Shared premise for all ten: a refinement type is a *subset of the base type's value space*.
`i32` is the set of 2^32 values; `(i32 | even v)` is half of them; `(i32 | 0 <= v < n)` is a window
whose right edge depends on another value. A specification-adherence bug is always one of:
a value that lands outside its set (runtime), a set that is not contained in the set it flows into
(static), a fact that the checker cannot establish (unknown), or a spec that constrains nothing (vacuous).
Every idea below must make each of those four visually distinct.

---

## 1. Shape-as-value-space (containment typing)
**Concept.** Reinterpret Codillon's type shapes literally: the i32 rectangle *is* the i32 number line,
left edge INT_MIN, right edge INT_MAX (with a compressed, piecewise scale that keeps 0, small
integers and the extremes legible). A refinement is drawn as a *region inside the shape*: a filled
sub-interval for bounds, stripes for parity/congruence, a dot-pattern for finite sets, a tie-line to another
shape for a dependent bound. An input cup shows the region the instruction *requires*; an output
shows the region the instruction *provides*. Subtyping is literal containment: the provided region
must fit inside the required region. The runtime value at the current step is a dot inside the shape.
**Bug made obvious.** A static mismatch = the provided region visibly pokes outside the cup's region
(darkred overflow sliver, connection goes dotted at that point). A runtime violation = the dot sits in
the darkred sliver / outside the region at step k. Unknown = region drawn with a question-mark hatch.
Vacuous = region is the whole shape (nothing excluded) and the shape gets a hollow outline.
**Number theory.** isqrt: the result shape shows `[r, r+1)²`-style bound as a window that *moves with n*
as the slider moves. **Hash table.** Each memory slot is a tiny i32 triple of shapes; the `state` shape has
exactly three legal points (0,1,2); a `key` shape's region is "in M" (dot-pattern of model keys).
**Risk.** Scale compression inside a 30-px shape; must zoom on hover.

## 2. Wraparound ring with twin ticks (overflow made spatial)
**Concept.** Wasm integers have no signedness; the *operator* chooses (`gt_s` vs `gt_u`). Draw the i32
value space not as a line but as a **ring (clock)** with a seam at the top where `0x7fffffff + 1` wraps to
`−2^31`. Each refined value gets a small ring in the margin: the admitted region is a shaded arc with
fence posts (filled = inclusive, hollow = exclusive); the runtime value is a bead on the ring with **two
tick labels**, its signed and unsigned reading. Mathematical predicates (`($r+1)*($r+1)` in ℤ) are drawn
as a second, *unrolled* arc that may extend past the seam: the machine value is where that arc lands after
wrapping. Dependent bounds are fences tethered to another ring's bead; they move as the slider moves.
**Bug made obvious.** Overflow = the bead *jumps the seam*: the unrolled arc crosses the top of the clock
and the bead reappears on the far side, with the seam flashing darkred and the gutter showing `⚖`. Signed
vs unsigned confusion = the two tick labels disagree *and* the operator's chosen reading is the one outside
the fence. Un-masked index = bead runs past a fence at 16 on a 16-slot ring.
**Number theory.** isqrt: the `sq := sq + 2r + 1` ring shows `sq` creeping toward the seam as `r → 46340`;
the signed-comparison bug is the bead crossing the seam and then being read as negative by `gt_s`.
**Hash table.** The 16-slot table *is* a ring (index `& 15`), so the same glyph draws the probe sequence as
an arc around the table ring; the two rings rhyme.
**Risk.** Rings are small; need a hover zoom and a linear fallback for non-wrapping predicates.

## 3. Sequent fractions (hypotheses over conclusions)
**Concept.** Extend the fraction glyph from *stack types* to *knowledge*. Above the rule: the facts
known about the inputs at this point (predicate tokens, each attached to the input shape it concerns).
Below the rule: the facts the instruction's refined type *claims* about its outputs. The rule itself
encodes the obligation's status: solid = proven automatically; dashed with `?` = unproven (needs a hint);
broken (two offset segments) with darkred = false, and the counterexample values are written inside the
shapes exactly where runtime values would appear. A thin line from a conclusion back to the hypotheses
that justify it shows *why*.
**Bug made obvious.** A broken rule is the single most salient thing on screen; the counterexample is in
place; the hypothesis that was *needed but missing* is drawn as an empty, fade-up cup (Codillon's
"missing operand" idiom reused for "missing fact").
**Number theory.** isqrt loop body: `r*r <= n` above, `(r+1)*(r+1) <= n` below at the branch; the
overflow bug shows as the false sequent with r = 46341.
**Hash table.** `i32.store` of a key: hypotheses include "probe path so far all FULL with key != k";
conclusion is clause (iii) of the representation invariant.
**Risk.** Predicate tokens must be *tiny* and consistent (iconic, not textual) or the right margin becomes a wall of text.

## 4. Fact ribbons on connections (provenance and decay)
**Concept.** Connections already show *where a value goes*. Give each connection a *ribbon* of the facts
it carries: a thin band of one color-coded stripe per fact (even/odd = stripe pattern, bounds = band
width, equality = a knot). As a value passes through an operation, facts are *born* (an `i32.shl 1` births
"even"), *preserved* (even + even), or *die* (even + unknown). Death is drawn as the stripe fraying out
at the operation. A cup that *requires* a fact wears a small badge for it; a satisfied badge is filled, an
unsatisfied one is hollow.
**Bug made obvious.** A hollow badge on a cup with the frayed end of the needed stripe visible a few lines
above: the eye traces the ribbon up to the exact instruction where the fact was lost. Runtime: at step
k the ribbon segment carrying a fact that is actually false turns darkred from the producer onward.
**Number theory.** parity: `even` born at `i32.mul 2`, lost at `i32.add 1`, required at the result cup.
**Hash table.** The fact "index < cap" is born at `i32.and (cap-1)` and required at every `i32.load`;
forgetting the mask means the ribbon is never born: the badge stays hollow on every load.
**Risk.** Ribbon width and crossing connections; limit to ≤3 facts per ribbon, rest in hover.

## 5. Invariant lap chart on the loop frame
**Concept.** A loop frame (Codillon's vertical bracket) gets a *gate* at the `loop` line where the
invariant is checked, and a *lap chart* docked to the frame: rows = invariant clauses (plus the
termination measure), columns = iterations actually executed at the current slider position. Each cell
is a small square: ivory = holds, darkred = false, dashed = not evaluable. The measure row is a
descending bar sparkline. On entry, the gate also shows "established?" and on exit "implies
postcondition?" as two cells on the frame line itself.
**Bug made obvious.** Invariant not established = first column dark. Not preserved = a dark cell at
iteration k with the column above it ivory; the slider snaps there on click. Too-weak invariant = all
cells ivory but the exit cell (implies postcondition) is dashed/unknown: the student sees that the loop is
fine but doesn't *prove enough*. Non-termination = the measure sparkline flat or rising with a darkred cap.
**Number theory.** isqrt and gcd both have 2–3 clause invariants; perfect fit.
**Hash table.** The probe loop's invariant "all visited slots FULL with key != k" is a clause row; the
tombstone bug flips it at the lap where a tombstone is visited.
**Risk.** Long loops → thousands of columns; compress to a strip with the first failing lap pinned.

## 6. Model/memory mirror (two-picture alignment)
**Concept.** For data-structure specs, show the abstract model and the concrete memory as two aligned
pictures: the ghost map `M` as a row of key→value beads (sorted), the memory as the ring (or row) of
slots with state/key/value, and *strings* from each bead to the FULL slot that holds it. The probe
path from `hash(k)` to that slot is drawn as an arc along the ring. The representation invariant's
clauses are *geometric*: every bead has exactly one string (ii); every FULL slot has a bead (i);
no arc passes over an EMPTY slot (iii); bead count < ring size (iv). The pictures update with the slider.
**Bug made obvious.** Tombstone-as-empty: the arc for key B crosses a slot drawn as EMPTY → the arc is
broken with a darkred gap and B's bead loses its string (floats, dashed). Duplicate key: two strings
from one bead. Full table: the ring closes with no EMPTY slot, the probe arc wraps all the way round and
is drawn as a darkred spiral. Un-masked index: the string points off the ring.
**Number theory.** For scalar programs, the "model" is the mathematical function (e.g. floor √n) and the
mirror shows the math value vs the computed value as two beads that should coincide.
**Risk.** Only shines for data structures; the scalar case needs the degenerate form to stay consistent.

## 7. Witness steps on the slider (counterexamples as runs)
**Concept.** When the checker finds a static counterexample, don't show it as text: *run it*. The
counterexample's inputs become a synthetic execution that appears on the step slider alongside the
student's own run, distinguished by a new tick glyph (a broken seal) rather than 💣. Scrubbing to that
tick shows the ordinary Codillon runtime view (values in shapes, arrow at the line) *plus* the violated
predicate rendered with the concrete values substituted and the false sub-term underlined in darkred
(a "truth tree" one level deep). The same rendering is used when a dynamic contract check fails in the
student's own run, so static and dynamic failures look identical except for the tick glyph.
**Bug made obvious.** The slider gets a new darkred tick; the predicate with values substituted reads
like `46341*46341 = -2147479015 <= 100000000` with the overflowed product underlined: the student sees
the exact arithmetic that lied.
**Number theory.** isqrt overflow and gcd(0,0) edge cases.
**Hash table.** The 20-step tombstone sequence becomes a witness run whose last step fails `lookup ensures`.
**Risk.** Multiple counterexamples per program; show the shortest first, others collapsed.

## 8. Spec sampler: relation plots and edge-case grids (coverage, not proof)
**Concept.** Treat the spec as an oracle and *sample* it, then draw the samples **on the spec's own
shape**. For a dependent result (`r*r <= n < (r+1)*(r+1)`), a small 2D **relation plot** at the function
header: input on the x-axis, result on the y-axis, the spec region shaded in the type color (a staircase
here, a line for `y == 2x`, a half-plane for `y >= x`). Every executed call (the student's run, edge-case
probes 0, 1, −1, INT_MAX, INT_MIN, powers of two, and any solver witness) adds a point; points inside the
shading are ivory, outside are darkred and clickable (jump the slider there). For multi-input or
sequence-valued specs (the hash table) the plot degrades to an **edge-case grid**: rows = operation
templates, columns = key seeds; cell = holds / fails / excluded-by-requires / vacuous (pale stripe).
The unshaded, unvisited part of the input range is left visibly *blank* so one green run reads as
one point, never as proof.
**Bug made obvious.** Off-by-one and overflow bugs light up only the edge points (the top-right corner of
the plot for isqrt); a wrong spec lights up everything; a vacuous `ensures` has no shaded region at all
(and a `○` glyph); an inconsistent `requires` grays out every cell. The student reads *patterns*.
**Number theory.** isqrt and gcd are one- and two-input functions with drawable relations.
**Hash table.** The tombstone bug lights exactly the row "insert A, insert B colliding, delete A, lookup B".
**Risk.** Sampling is not proof; the plot must sit visually *below* proven status (ideas 3/5/10) and carry
a "sampled" label; large input spaces need log-scaled axes.

## 9. Envelope strips (trajectory inside the spec band over time)
**Concept.** For each refined local/global (and selected memory cells), a horizontal *strip* whose
x-axis is the step slider and y-axis is the value: the refinement is a shaded *band* (which can move,
e.g. `r*r <= n` makes a band whose top edge depends on n), the actual value is a stepped line. Strips
are stacked under the slider and share its x-axis, so scrubbing moves a cursor across all of them at once.
**Bug made obvious.** The line exits the band: the exit point is a darkred dot, the slider tick beneath
it is darkred, and the band edge that was crossed is labeled with the clause. A too-weak invariant shows
as a band far wider than the trajectory ever uses (slack), hinting that the spec could be tightened.
**Number theory.** isqrt's r climbing inside a band whose ceiling is √n; gcd's measure strip strictly decreasing.
**Hash table.** One strip per slot's `state` (three-level), plus a strip for `count` with a band [0, cap).
**Risk.** Many variables → many strips; default to refined values only, expandable.

## 10. Synthetic proof holes (goals as inserted lines)
**Concept.** Codillon already inserts synthetic `end` lines (dashed darkred box, 𝄠 in the gutter). Do the
same for proof: when an obligation at line L cannot be discharged, the editor inserts a synthetic *hole*
line immediately after L: a dashed box containing the goal drawn as a fraction (hypotheses above the
rule as shapes-with-regions, goal below), plus up to three suggestion chips (`assert …`, strengthen the
invariant with …, `lemma …`). The student can accept a chip (the hole becomes a real `assert`/invariant
line and the box solidifies), or edit the code so the hole vanishes (with Codillon's reveal/vanish
animation). A wrong hint shakes. A hole that is *false* (counterexample exists) has a broken rule and
is darkred; a hole that is merely *unknown* is indigo-dashed.
**Bug made obvious.** The program grows a visible darkred line exactly where the reasoning breaks,
in the code, in reading order. Unknown vs false are different colors and different glyphs.
**Number theory.** isqrt: the hole after the branch asks for `(r+1)*(r+1)` not to overflow; the chip
offers `requires n < 2147395600` or a widened i64 computation.
**Hash table.** The hole after the probe loop asks for "no EMPTY on the path", and the chip offers the
tombstone-aware invariant.
**Risk.** Holes must not fight the student for the cursor; they are read-only until accepted.

---

## Cross-cutting consistency rules for all ten prototypes
Six epistemic states, each with its own look, readable in grayscale (never color-only):
| state | color | line/shape style | glyph |
|---|---|---|---|
| proven | none (ivory) | solid, quiet | gray line number (silence is success) |
| refuted, witness replayed | darkred | solid, broken rule / spill / seam flash | `⚖` in gutter; darkred slider pill |
| refuted, witness not yet replayed | darkred outline only | dashed "ghost" track above the slider; outlined shapes | `⚖` hollow |
| held on this run only (dynamic check) | slategray | dotted | small `∘` tick count, never a check mark |
| unknown / timeout / needs hint | indigo | dashed, `?` | star-family (Codillon's "mystery" star) |
| assumed / admitted / vacuous | ghosted (50% opacity) | hollow outline | `○`; everything downstream also ghosted |
Also: stale verdicts (text edited since checking) fade to 40% and squiggle until re-checked.
- Keep ✗ invalid, 💣 trap, 𝄞 malformed, 𝄠 synthetic end. Gutter precedence: 💣 > 𝄞 > ⚖ > ✗ > unknown-star > number.
- No green anywhere. Darkred means *violated* and nothing else (never "changed", never "interesting").
- Compound predicates are split into **conjunct chips** that pass or fail separately.
- Every darkred leads to a witness one click away (slider jump); if there is no witness it is not darkred.
- Runtime values keep appearing *inside* shapes; predicates frame values, never replace them.
- Everything that appears/disappears/moves tweens (0.25s). The shake is reserved for *refused edits*.
- Annotations live in the right margin at fixed row height; richer pictures open on hover/selection and can be pinned.
- Surface syntax for specs follows 01-language-design.md: `(param $n (i32 | 0 <= $n))`, `(@invariant …)`,
  `(@decreases …)`, `(@ensures …)`, `(@assert …)`, `(@use lemma …)`, `(@ghost …)`, `(@region …)`.
