# Spec-adherence visualization for Codillon: requirements and bug taxonomy

Scope: the *visualization layer* of a future Codillon whose value types carry predicates
(refinements such as "i32 that is even", intervals, loop invariants, function contracts, a
representation invariant over linear memory). The checker technology (SMT, abstract
interpretation, runtime checks) is out of scope. What matters here is how its verdicts appear.
Spec syntax is written informally below (`;; @requires n >= 0`). The notation is not settled.

Evidence comes from upstream `codillon/src` (graphics.rs, line.rs, editor.rs, utils.rs, syntax.rs),
`public/codillon.css`, and the 50 most recent commit subjects.

---

## 1. Inferred design values, and what each implies for specs

1. **Diagnostics live on the code. There is no error panel.**
   *Evidence:* `line.rs::conform()` writes every reason (runtime error, malformed, inactive,
   invalid) into one `data-commentary` attribute, and CSS floats it right on that line. The gutter
   glyph replaces the line number (`.invalid-line::before`). No list or console exists.
   *Constraint:* there is no "verification results" pane. Every obligation is drawn at a code
   location: a line, a cup, a connection, or a frame. A hover may add detail but must not be
   the only place a failure appears.

2. **The program always runs, even when it is wrong.**
   *Evidence:* `fix_validity` ("validize") inserts default operands for missing parameters, swaps
   an invalid op for a `bailout`, or prepends `unreachable` so the stack becomes polymorphic. The
   module is instrumented and re-executed on every keystroke.
   *Constraint:* a failed obligation is reported and then *assumed* so that checking (and
   execution) continues downstream. One failure must not blank out the facts below it. Runtime
   contract checks should record and continue where that is safe, so the slider still covers the
   whole run.

3. **The editor refuses nonsense but tolerates wrongness.**
   *Evidence:* `editor.rs` reverts an edit only when the module is not "validizable" and
   `line.shake()`s the restored lines. Ordinary type errors are accepted and drawn.
   *Constraint:* a spec that does not parse may be refused or marked with 𝄞. A spec that is false,
   unprovable, or vacuous is never refused. It is *drawn*. Verification never blocks typing.

4. **Identity persists across edits, so change is visible.**
   *Evidence:* #251 "Identify lines and fractions with long-lived identity", #283/#284 identity
   propagated to connections ("rehoming"), #291 "Animate fractions and connections", #292/#296
   fixes for animation glitches, #285 move to requestAnimationFrame. Every geometric attribute is
   a `Tween`.
   *Constraint:* facts, obligations, and counterexamples need stable identities keyed to the
   things they annotate. When an edit breaks a proof, the student sees the fact *detach*, *fade*,
   or *turn* in place. The scene is never re-rendered from scratch.

5. **Badness is drawn as frustrated intent.**
   *Evidence:* #275 "Draw 'bad' connections showing where operands are 'trying' to go" and #282.
   In `refresh_targets`, a mismatch shortens the reader offset (0.6×), bends the second control
   point sideways (`read_x + 1.5*slope`), and tweens `badness`. The curve visibly fails to seat
   in the cup.
   *Constraint:* a predicate mismatch (right shape, insufficient fact) is the same idea one level
   up: the value reaches the cup but does not *fit*. It belongs to the same visual family as type
   mismatch while staying clearly distinguishable from it.

6. **Absence is drawn as a shape, not a sentence.**
   *Evidence:* empty input cups use the `fade-up` gradient (`make_empty`). Never-consumed outputs
   are drawn `_stranded` with a thick stroke. A synthetic `end` gets a dashed darkred box and 𝄠.
   An unclosed frame shows ⊘.
   *Constraint:* a fact that is *needed but not supplied*, such as an invariant missing at a loop
   head, is drawn as an empty slot. A spec that constrains nothing, such as an ensures clause that
   never mentions the result, is drawn as *stranded*.

7. **Literal honesty: never show a claim the system doesn't hold.**
   *Evidence:* #263 replaced ∞ with "> 99,999" for TooManyTicks. #274 "Don't attempt to show type
   of a synthetic end". #272 "Remove 'old' filter when value not present". Unknown types get an
   explicit "mystery" star and are never guessed.
   *Constraint:* *unproven*, *false*, *timed out*, *assumed*, and *checked only on this run* are
   five different epistemic states and must look different. Never round "not refuted" up to
   "proven", or "unproven" down to "wrong".

8. **Silence means success. Show only what is in play.**
   *Evidence:* a healthy line shows a gray line number and nothing else. The canvas is hidden
   unless the graphics API is *ever* used (#264/#265). Fractions are omitted for synthetic lines.
   *Constraint:* a proven obligation costs almost no ink. No green checkmarks. The spec layer must
   not turn a clean program into a wall of status.

9. **Concrete values over abstractions.**
   *Evidence:* `set_slot_value` writes the actual runtime value inside each shape. Values from
   earlier iterations are grayscaled ("old"). #293 labels loops that actually ran. The arrow
   placement after calls and recursion is handled carefully (#261, #262).
   *Constraint:* a symbolic counterexample must become a concrete run that the student scrubs with
   the existing slider, with values in the existing shapes. Abstract facts should come with a
   witness.

10. **A small, hand-made glyph vocabulary with typographic wit, one glyph per gutter.**
    *Evidence:* 𝄞 malformed, ✗ invalid, 💣 trap, 𝄠 synthetic end, ⊘ unclosed, a navy arrow for
    the current step. `conform()` sets a strict priority (runtime > malformed > inactive >
    invalid).
    *Constraint:* add at most two or three new gutter glyphs, from the same family, readable at
    20pt next to the existing ones. Define a precedence that says which glyph wins the single
    gutter slot.

11. **Frames are first-class structure.**
    *Evidence:* #287/#288 refined function and `else` frames. #295 moved the unclosed loop end to
    meet the ⊘. #293 added the "loop" label on frame lines.
    *Constraint:* loop invariants, termination measures, function contracts, and "open" (temporarily
    broken) representation invariants attach to frames. A frame's *top* and *bottom* are
    meaningful places to put marks.

12. **Responsiveness on every keystroke.**
    *Evidence:* #268 packed `Option<SlotUse>` into 4 bytes. #257 shrank `ExecutionStep`. Runs of
    up to 100k steps are recorded per edit, and execution happens in a worker.
    *Constraint:* verification is incremental and asynchronous. The visual layer needs a calm
    *pending* or *stale* state that does not flash between verdicts while a solver runs.

---

## 2. Taxonomy of specification-adherence failure modes

Legend for **Where detected**:
- **S**: edit-time static proof attempt.
- **C**: edit-time counterexample (solver model or fuzzing, replayed concretely).
- **R**: runtime dynamic check during the normal instrumented run.

The **Must jump out** field names what has to be visually obvious and where: gutter, right-margin
fraction, connection, frame, slider, or memory view.

**F1. Precondition violated at a call site.**
The caller passes a value whose known facts don't entail the callee's `requires`.
*Example:* `;; @requires d != 0` on `div`. The call site has `local.get $x` with `$x` unconstrained.
*Detected:* S (unprovable), C (`$x=0`), R.
*Must jump out:* the *call line's* input cup carries the required predicate. The incoming
connection is "bad" in the predicate sense: it arrives but does not seat. The gutter mark is on the
**caller** line, never inside the callee. The counterexample value (0) appears in the shape.

**F2. Postcondition unprovable.**
The verifier can't show `ensures` from the body, but it has no counterexample either.
*Example:* `;; @ensures result >= 0` on `abs` with non-linear reasoning.
*Detected:* S.
*Must jump out:* the function's **closing frame / return point** shows the ensures predicate as
*unknown* (star-family mark, not darkred). It must be visibly different from F3. A "why" trail
names the path or exit that couldn't be shown.

**F3. Postcondition false (counterexample).**
Inputs exist that make the body return a result violating `ensures`.
*Example:* `abs(x)` returns `x` when `x = INT_MIN`.
*Detected:* C, R.
*Must jump out:* a darkred mark at the **exit** the bad path took. The **slider** gains a
counterexample run with a darkred pill at the failing step. The arrow sits at the return, and the
offending value shows in the output shape.

**F4. Loop invariant not established on entry.**
The facts at loop entry don't imply the invariant.
*Example:* `;; @invariant i <= n` with `i` initialised to `n+1`.
*Detected:* S, C, R (checked at the first loop-head visit).
*Must jump out:* the mark sits on the **top of the loop frame**, at the entry edge. The faulty
code is *before* the loop, so the connection from the initialising store to the frame is the
highlighted culprit.

**F5. Loop invariant not preserved by the body.**
Invariant ∧ guard, run through the body, doesn't re-establish the invariant.
*Example:* `;; @invariant sum is even` and the body does `sum += i`.
*Detected:* S, C (a two-iteration witness), R (at iteration k).
*Must jump out:* the mark sits on the **back-edge / bottom of the loop frame**. The slider points
to the *iteration* that broke it, using "old" grayscale to show the prior iteration's values next
to current ones. It must not look like F4.

**F6. Invariant too weak to prove the postcondition.**
The program is correct but the spec is inadequate.
*Example:* `;; @invariant i <= n` is preserved, but `ensures result == n*(n+1)/2` needs
`sum == i*(i+1)/2`.
*Detected:* S (post unprovable). C finds *no* real counterexample, but finds an "induction
counterexample" that satisfies the invariant without being reachable.
*Must jump out:* blame goes to the **invariant on the frame**, not the code. A *needed-but-missing
fact* is drawn as an **empty cup** (fade-up) at the loop head. Real runs show the postcondition
holding on the slider. The verdict reads "your code is fine, your spec is short."

**F7. Spec inconsistent or vacuous.**
`requires false` (or contradictory clauses) makes everything "proven". Alternatively, an `ensures`
that is trivially true or never mentions the result.
*Example:* `;; @requires x > 0 && x < 0`, or `;; @ensures result == result`.
*Detected:* S (a satisfiability or vacuity check).
*Must jump out:* a vacuous precondition renders the body as **unreachable**, ghosted with
polymorphic stars just as Codillon already treats code after `unreachable`. Success must look
*suspicious*, not green. A trivial ensures is drawn **stranded**: it has no connection to any
output.

**F8. Termination / measure failure.**
A loop or recursion has no measure that strictly decreases and stays bounded below.
*Example:* `;; @decreases n - i` with a path that skips `i++`.
*Detected:* S, C, R (the measure fails to decrease at iteration k, or hits a TooManyTicks
step budget).
*Must jump out:* the **loop frame label** ("loop" today) carries the measure's value per
iteration, a decreasing sequence. The failing iteration is a slider pill. With no measure at all,
the mark is ⊘-like (an unclosed proof, not an error).

**F9. Integer overflow / wraparound breaks an arithmetic fact.**
A fact that holds over ℤ fails in i32.
*Example:* `x > 0 ⇒ x+1 > 0` fails at `x = 2147483647`.
*Detected:* S, C, R.
*Must jump out:* the **output shape of the arithmetic op** loses or contradicts its predicate.
The interval visibly *wraps* (e.g. drawn crossing the shape's edge), and the counterexample value
appears in the shape. The culprit is the `i32.add` line, not the later use.

**F10. Refinement lost through an operation.**
An op produces a value about which the needed fact is unknown, though no fact is *false*.
*Example:* `even + odd` produces unknown parity, and a later cup requires `even`.
*Detected:* S.
*Must jump out:* the predicate inscription is present on the inputs and **absent on the output**.
The *fraction where knowledge was dropped* is identifiable by tracing connections back from the
failing cup, without reading text.

**F11. Store breaks a representation invariant (memory/aliasing).**
A store leaves linear memory in a state violating the data structure invariant at a point where
the invariant must hold.
*Example:* a hash-table insert writes a key into slot `h(k)+1` without updating `count`. Or two
pointers alias the same bucket.
*Detected:* S, C, R (checked at function exit or at calls).
*Must jump out:* the **memory view** highlights the offending cells and the store line that wrote
them. The region where the invariant is legitimately "open" (between the first store and
re-establishment) is drawn like a frame. A failure looks like an **unclosed** region (⊘) at the
exit that needed it closed.

**F12. Ghost/model divergence.**
Concrete memory no longer abstracts to the ghost model (e.g. map `M`).
*Example:* after `insert(k,v)` the model says `M[k]=v`, but a probe of memory finds the old value.
*Detected:* C, R (evaluate the abstraction function at each step).
*Must jump out:* a **memory view** with model and concrete side by side at the slider step. The
divergent key is highlighted in both, and the first step where they disagree is a slider pill.

**F13. Unreachable-but-necessary case.**
Either an `unreachable` or "impossible" branch is reachable (its infeasibility can't be shown or is
refuted), or a branch is proven dead only because the precondition is too strong, leaving its
obligations vacuously discharged.
*Example:* a `br_table` default marked `unreachable` with `tag` in `[0,3]`, while a caller passes 4.
*Detected:* S, C, R (💣 today).
*Must jump out:* the `unreachable` line shows *whether infeasibility is proven*. A refuted case has
a counterexample run to it. Dead-by-assumption code is **ghosted** the same way as F7.

**F14. Dynamic contract failure at runtime step k.**
A runtime-checked (unproven) predicate evaluates false during the actual run.
*Example:* `;; @check result < 256` fails on step 4,812.
*Detected:* R.
*Must jump out:* a **darkred slider pill** at k, distinct from a trap's pill. The arrow is at the
line. Values in the shapes show *why* the predicate is false. Line text turns darkred, as with
💣, but with a different glyph.

**F15. True obligation the solver can't decide (needs a hint).**
The obligation is valid but beyond automation (non-linear arithmetic, quantifier instantiation,
induction).
*Example:* `(a*b) % 2 == 0` given `a` even.
*Detected:* S (timeout/unknown). C finds nothing, and R never fails.
*Must jump out:* the **unknown** state (as in F2), *plus* positive evidence: "0 counterexamples in N
runs". It needs an affordance at the obligation to add a hint/lemma, and it must **never be
darkred**.

---

## 3. Requirements for visualization primitives

### 3.1 Consistency with the existing vocabulary
- **R1 MUST** keep the existing invariants: types are shapes, dataflow is lines, badness is
  darkred, runtime is the slider, and annotations live in the right margin of the line they
  describe.
- **R2 MUST NOT** recolor or reshape existing type glyphs to carry spec status. Shape and color
  stay *type* channels.
- **R3 MUST** add no more than three new gutter glyphs. They come from the same typographic/musical
  family, are distinguishable from 𝄞 ✗ 💣 𝄠 ⊘ at 20pt and in grayscale, and follow a stated
  precedence that extends `conform()`'s (proposed: trap > malformed > spec-false > invalid >
  spec-unknown > number).
- **R4 SHOULD** reuse existing visual idioms for analogous spec ideas:
  - empty cup (fade-up) for a needed-but-missing fact
  - stranded stroke for a spec that constrains nothing
  - the ⊘/unclosed treatment for open invariants or missing measures
  - dashed outline (like the synthetic-end box) for *assumed*
  - ghosted/polymorphic rendering for vacuous or dead regions
  - "old" grayscale for prior-iteration witnesses

### 3.2 Predicate layered onto type shape
- **R5 MUST** render a refinement as a *modification inside or on* the existing type shape, such
  as an inscription, notch, fill pattern, or interval tick. It is not a separate text box, so
  "i32" and "i32 that is even" remain recognizably the same species.
- **R6 MUST** make three states readable on a shape without hovering: *carries the fact*,
  *fact unknown*, and *fact contradicted*. F10 depends on telling the first two apart.
- **R7 SHOULD** give interval/range refinements a compact geometric form (a bar or ticks on the
  shape), so wraparound (F9) is a visible event rather than a text change.
- **R8 SHOULD** make predicate text available on demand (hover/focus) in the existing
  `slot-value` label font. The default view is iconic.

### 3.3 Obligations and connections
- **R9 MUST** model every obligation as a *cup demanding a fact*: call inputs (requires), function
  exit (ensures), loop head (invariant), store targets (rep invariant). The *supplier* of the fact
  is reached by following existing connections.
- **R10 MUST** draw a *predicate-unsatisfied* connection as a sibling of today's "bad" connection:
  it arrives and fails to seat. It must be distinguishable from a type mismatch by a non-color
  channel such as dash pattern or seating geometry.
- **R11 MUST** place blame where the fix belongs: caller line for F1, callee exit for F2/F3, frame
  top for F4, frame bottom for F5, invariant for F6, the dropping operation for F10, the store for
  F11.
- **R12 SHOULD** provide a one-gesture "why" trail that lights up the chain of fractions and
  connections back to where the needed fact was last present (F6, F10).

### 3.4 Counterexamples and the slider
- **R13 MUST** turn every counterexample (C) into a concrete run, loadable into the existing
  slider, with values in the existing shapes and the arrow at the failing step. A counterexample
  is "a run you can scrub", not a solver dump.
- **R14 MUST** keep the student's own run and solver-supplied runs visually distinct. For example,
  a run selector shows which input produced the timeline, so a counterexample is never mistaken
  for "my program did this".
- **R15 MUST** give spec failures on the slider their own pill style, distinct from trap pills
  (`bad-slider-tick`) by shape or glyph as well as color.
- **R16 SHOULD** show per-iteration witnesses for loop facts (invariant and measure values on the
  frame) using the "old" grayscale for previous iterations.
- **R17 SHOULD** offer a memory view for F11/F12, with model and concrete state side by side at
  the current step and divergent cells marked.

### 3.5 Epistemic status without a traffic light
- **R18 MUST** distinguish *proven*, *assumed* (unchecked, trusted), *checked at runtime*,
  *unknown* (no proof, no counterexample), *false*, and *vacuous*.
- **R19 MUST** make *proven* the quietest state (no added mark beyond the predicate itself) and
  make *false* the only state that uses darkred. *Unknown* uses the mystery-star family, and
  *vacuous* uses ghosting.
- **R20 MUST NOT** use green, or any three-color red/amber/green scheme. Status must not be carried
  by hue alone.
- **R21 SHOULD** show *checked at runtime* as a passive mark that becomes a positive stamp only
  when the slider passes a step where the check actually ran and passed.
- **R22 MUST** show *pending* (solver still running) and *stale* (verdict from an earlier edit)
  calmly. No flicker between verdicts while typing, and the last known verdict stays dimmed until
  replaced.

### 3.6 Scale (100-line programs)
- **R23 MUST** keep per-line spec ink within the existing right-margin column and line height. No
  row may grow taller because of spec annotations.
- **R24 MUST** show obligations as marks at their locations. Long-range relations (a precondition
  defined 60 lines above) are summarized locally, with the far end revealed on demand.
- **R25 SHOULD** make the gutter alone enough to find every *false* obligation by scrolling. A
  sticky-slider overview (ticks for spec failures) helps with off-screen issues.

### 3.7 Animation and identity
- **R26 MUST** give facts, obligations, and counterexample runs long-lived identities so that
  tweens show *what changed*. When an edit breaks a proof, the fact visibly detaches from the
  connection or fades from the shape at the responsible line.
- **R27 SHOULD** briefly emphasize newly failing obligations (on the order of the existing 0.25s
  tweens) and never emphasize unchanged failures repeatedly.
- **R28 MUST NOT** use the shake animation for spec failures. Shake means "edit refused".

### 3.8 Accessibility
- **R29 MUST** distinguish every status in grayscale and at 200% zoom, using shape, glyph, dash,
  or position alongside color.
- **R30 MUST** give every mark an accessible text equivalent in the existing `data-commentary`
  idiom. The commentary names the predicate, the status, and the blamed location.
- **R31 SHOULD** keep motion optional (respect `prefers-reduced-motion`) without losing
  information. A state change must also be readable from the end state.

---

## 4. Evaluation rubric for prototype mockups

Each prototype is an HTML mockup showing (a) a clean version and (b) a version with one seeded bug
drawn from §2. Score each criterion 1–5:
- 1 = fails
- 3 = works with effort or explanation
- 5 = immediate and unambiguous

| # | Criterion | Question the reviewer answers by looking |
|---|-----------|------------------------------------------|
| 1 | **Salience** | Without reading a legend, can I put my finger on the seeded bug's line within ~5 seconds? |
| 2 | **Blame locality** | Is the strongest mark at the place that must change (caller vs callee vs invariant vs spec vs the operation that dropped the fact), not merely where the failure surfaced? |
| 3 | **Kind discrimination (grayscale)** | With color removed, can I tell *false* from *unknown* from *vacuous* from *spec-too-weak* from *runtime-failed*? |
| 4 | **Vocabulary continuity** | Would a current Codillon user still read types as shapes, dataflow as lines, and darkred as bad, and do the new glyphs look like they belong to the clef/bomb family? |
| 5 | **Predicate on shape** | Can I read which values carry which facts (e.g. "this i32 is even", "this one lost it") from the shapes, without opening text? |
| 6 | **Causal trail** | Can I follow connections from the failing obligation back to where the needed fact was last present or first violated? |
| 7 | **Concrete witness** | Is there a scrubbable concrete run (values in shapes, arrow, slider pill) that demonstrates the bug, reachable in one action and clearly labeled as a counterexample rather than the user's run? |
| 8 | **Ink economy** | In the clean version, is success nearly silent, with no traffic-light wall, and is *proven* vs *assumed* vs *runtime-checked* still discoverable? |
| 9 | **Scale** | On the ~100-line variant, do annotations stay in the right margin at fixed row height, and can I still find the bug by scanning the gutter? |
| 10 | **Edit continuity** | Does the mockup show (or concretely specify) the transition from the pre-edit state to the broken state, so that the fact visibly detaches at the responsible line, without shake or wholesale re-render? |

**Suggested seeded bugs for a fair comparison.** Use one per mockup set, rotated across
prototypes:
- F1, precondition at a call
- F5, invariant not preserved
- F6, spec too weak (correct program)
- F7, `requires false`
- F9, overflow
- F10, parity lost
- F11/F12, hash-table store

Weight criteria 1–3 double when picking finalists. A prototype that scores below 3 on criterion 3
(kind discrimination) or criterion 2 (blame) should be rejected regardless of total. These are the
two failures that make a spec bug *look like* a different bug.
