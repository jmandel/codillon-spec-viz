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

## 2. Fences on margin rulers
**Concept.** A second annotation column to the right of the fractions: for each instruction that
produces a value with a refinement, a small horizontal *ruler* (number line) with the predicate drawn as
*fences* (bounds), *hatching* (congruence classes), and *pins* (equality to another named value, with a
tie-line back to that value's ruler). The runtime value is a bead on the ruler. Dependent bounds are
fences whose position is tied to another bead (as the slider moves, the fence moves). Rulers for
the same variable across lines are vertically aligned so the eye can follow a value down the program.
**Bug made obvious.** The bead lands on the wrong side of a fence: fence turns darkred, bead gets a
💣-like "broken fence" glyph in the gutter at the first offending step; the slider tick for that step is darkred.
Static: the producer's permitted range (drawn as a bracket under the ruler) overhangs the consumer's fence.
**Number theory.** gcd: ruler for `$x` and `$y` with the invariant `gcd(x,y) = gcd(a,b)` as a pin to a
ghost bead; termination measure as a ruler that must strictly shrink each iteration (bead must move left).
**Hash table.** The probe index ruler has fences at 0 and cap; the un-masked index escapes past the fence.
**Risk.** Many rulers = clutter; show only for refined values and the hovered dataflow chain.

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

## 8. Spec sampler grid (edge-case heatmap at the function header)
**Concept.** Treat the spec as an oracle and *sample* it. At each function header, a small grid of
cells, one per sampled input (edge cases 0, 1, −1, INT_MAX, INT_MIN, powers of two, plus random, plus
any solver witness), ordered by magnitude. Cell fill: ivory = ensures holds; darkred = fails; gray =
excluded by requires; pale-striped = ensures was *vacuously* true (did not depend on the result).
Hover shows the input and output; click loads that input as the current run on the slider.
**Bug made obvious.** Off-by-one and overflow bugs light up only the *edge* cells; a wrong spec lights up
*everything*; a vacuous spec shows the pale stripe everywhere (and a hollow-outline glyph); an
inconsistent `requires` grays out every cell. Patterns, not messages.
**Number theory.** Perfect for isqrt/gcd/pow_mod: one-dimensional or two-dimensional grids.
**Hash table.** Inputs are short *operation sequences*; grid rows = sequence templates
(insert/insert-collide/delete/lookup…), columns = key seeds. The tombstone bug lights exactly the
row "insert A, insert B colliding, delete A, lookup B".
**Risk.** Sampling is not proof; must be visually subordinate to proven status (idea 3/5) and labeled as such.

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
- Status palette (never color-only; each also has a glyph/line style):
  - proven: ivory/none (silence is success, like a numbered line today)
  - unknown / needs hint: indigo, dashed, `?`
  - false with counterexample: darkred, broken/solid, new gutter glyph `⚖` ("spec violated")
  - checked only at runtime (dynamic): slate, dotted
  - vacuous / trivially true: hollow outline, glyph `○`
- Keep: ✗ invalid, 💣 trap, 𝄞 malformed, 𝄠 synthetic. Add exactly one new gutter glyph for spec violation.
- Runtime values keep appearing *inside* shapes; predicates never replace values, they frame them.
- Everything that appears/disappears animates (0.25s) so the student sees what their edit changed.
