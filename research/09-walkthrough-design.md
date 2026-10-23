# Design spec: the single-page walkthrough ("Refined Codillon")

Purpose: one self-contained HTML page, written as a tutorial, that presents the *composed* design from
08-synthesis.md §5 as if it were the decided language and editor, and demonstrates it working on the three
programs. It is the deliverable a reader opens first. Builders: read 08-synthesis.md and 07-review-notes.md
before this file; they explain *why* each choice below was made.

File: `artifacts/00-refined-codillon.html` (also linked first from `index.html`). Self-contained, no network,
vanilla JS + inline SVG. Same style tokens as 06-artifact-brief-shared.md. Target ≤ 400 KB.

## The decision (state it as fact in the page)

**One idea.** A type is a set of values. A refinement `(i32 | P)` is a smaller set drawn *inside* the type's
shape. Everything else follows:
- A stack slot has a **provided** set (from its producer) and a **required** set (from its consumer).
  Typechecking is containment. A failed containment is drawn as a **spill**: the part of the provided set that
  lies outside the cup's rim, hatched darkred.
- Each instruction's fraction is a **sequent**: facts known about the inputs above the rule, facts claimed
  about the outputs below. The **rule is the verdict** (six styles, below).
- When an obligation cannot be discharged, the editor inserts a **hole line** after the instruction, in the
  same family as its synthetic `end`: dashed box, 𝄽 in the gutter, the goal as a fraction with witness values
  inside the shapes, and up to three suggestion chips (code / spec / invariant / lemma / admit).
- A counterexample is a **run**. It appears as a dashed ghost track above the step slider; replaying it drops a
  `⚖` pill onto a witness band of the slider, and scrubbing to it fills every shape with the values at that step.
- Density lives in **lenses**, opened by clicking a shape, a loop line, a region, or a function header:
  the integer **ring** (overflow and signedness), the loop **lap chart** (which lap broke which conjunct),
  the memory **mirror** (abstract map vs concrete slots), and the header **relation plot** (sampled coverage).
  Lenses are never on by default.

**Six epistemic states** (verbatim table from 05, end). Grayscale-safe; darkred means violated and nothing else;
there is no green. Cell *fill* comes from the run, *border and glyph* from the checker (05's rule).

**Gutter glyphs and precedence**: 💣 trap > 𝄞 malformed > ⚖ spec refuted > ✗ invalid > 𝄽 hole/unknown > number.
`⚖` goes at the obligation site *and* at the line to change when they differ.

**Mid-operation discipline**: an invariant may be false between checkpoints (loop-head arrivals, operation
boundaries, writes to a refined local). Mid-operation misalignment is drawn gray as "open", never darkred.

## Fixed sizes (resolve the open question from 08 §7)
- Unrefined i32 shape: 30×11 as today. **Refined** i32 shape: 72×12 with a piecewise scale (linear |v| ≤ 8 over
  the middle 60%, log to the walls). i64 is 72×20. Hover on any shape opens a 300 px zoom lens of the same shape
  with landmarks (INT_MIN, −8…8, INT_MAX) and the predicate text; click pins it.
- Fence posts 1.5 px, filled cap = inclusive, hollow = exclusive. Parity comb: teeth at ±2, ±4, ±6, ±8 then stripes.
  Finite set = sockets. Dependent bound = fence tethered by a 1 px dashed curve to the other value's dot.
- Spill: darkred 45° hatch, min 6 px wide, rising 3 px above the rim; the connection into that cup becomes dotted
  darkred for its last 30 px.
- Chips: 14 px tall, iconic glyph + optional 2–4 char text; hover gives the full predicate. **One shared chip
  vocabulary** (define it in the legend and use nowhere else): `≥0` bound, `[a,b)` window, `⫶` even/odd comb,
  `=` equality to a name, `∈M`/`∉M` membership, `R` rep-invariant, `inv` loop invariant, `↓` decreases,
  `u(·)` unsigned reading, `²` square/nonlinear, `∃`/`∀` quantifier, `⊥` false.
- Hole line: full width of the code column + margin; dashed darkred (false) / indigo (unknown) / slategray (dynamic)
  box; 𝄽 in the gutter; fraction left, chips right; "replay" button when a witness exists.

## Page structure (tutorial voice, second person, present tense; headings as written)

0. **Refined Codillon** — one paragraph: what Codillon is, what this adds, how to read the page (every picture is
   live: scrub, hover, click). A "before" strip: the current Codillon fraction/connection vocabulary on a 4-line
   snippet, then the same snippet "after" with one refinement, so the reader sees how little changes.
1. **A type is a set** — an interactive card: a single `(i32 | P)` shape with a predicate picker (`0 <= v`,
   `0 <= v < n`, `even v`, `v ∈ {0,1,2}`, `v == 2*x`) and a value slider; shows the region, fences, comb, sockets,
   tether, and the dot leaving the region. Below it the six states on one cup (the A·4 card from prototype 01/03).
2. **Reading a line** — one `i32.add` with the sequent fraction explained part by part (callouts with leader
   lines): provided set, required set, facts above, claims below, rule style, spill.
3. **Lesson 1 · parity** — `$half_or_neg1`/`$half` from the fixture. Show the precondition at a call site.
   Seed P1 (gate inverted): the cup on `call $half` spills on the odd teeth; a hole appears after the call with
   witness x = 3; accept the code chip, hole vanishes. Seed P3 (spec bug): no spill anywhere in the body, the hole
   attaches to the header's conjunct, the only chip is a spec chip. Teach: *blame goes where the fix goes*.
4. **Lesson 2 · integer square root** — the fixture isqrt. Walk the student path from 01 §5 as three states of
   the same listing, selectable as tabs ("no invariant yet", "signed attempt", "no lemma hint", "all proven"):
   - no invariant: hole after line 26 with a loop-head witness (n=3, r=5), ∞? on the loop; chip flies the
     invariant into lines 7–8.
   - signed attempt (S1): hole after the back-edge; ghost track "n = 2³¹−1, r = 46340 · one-iteration replay";
     replay fills shapes; the product shape on line 15 shows the **nub past the INT_MAX wall** and the wrap arc;
     clicking it opens the **ring lens** with the seam, the cut at the top for `gt_s`, and the twin ticks. Chips:
     `gt_u` (code) or tighten `requires` (spec).
   - no lemma: indigo unknown hole after line 15 with `∘ 4` and an apply? list; `(@use sq_lt_sq …)` closes it.
   - all proven: calm; clicking the `loop` line opens the **lap chart lens** showing every lap ivory and the exit
     cell proven. Also offer S2 and S3 from a "seed bug" select, and the header's **relation plot lens** (sampled,
     labelled "samples · not proof") showing S2 lighting every perfect square.
5. **Lesson 3 · a hash table** — the fixture table, folded to `$find`, `$lookup`, `$delete`, `$insert` with the
   spec lines visible. Explain `(@ghost $M)`, the region, R's five clauses as chips on the module line. Open the
   **mirror lens** (06) docked under the slider for this section: beads, slots, strings, probe arcs, "R open"
   gray mid-operation. Seed (b): R stays true; the hole at `$find`'s early return shows the TOMB on key 11's path
   with the mini strip, and the chips **fork**: fix the exit test (code) or strengthen (iii) (invariant) — accepting
   the second moves the hole to `delete`'s store and it is false there. Teach: "your code is fine, your spec is
   short" vs "your code is wrong" look different. Seed (d): the ring closes, the measure staircase in the lap
   chart fails, the hole offers the corrected clause (iv). Seed (a) briefly: 💣 beats ⚖.
6. **What the checker hands the editor** — the residue record (01 §2.8) shown once as a card, and a three-row
   table mapping surface constructs to Lean (`(T | P)` ↦ subtype, loop ↦ `termination_by`, `(@assume)` ↦ `sorry`).
   Keep it to ~150 words.
7. **Rules we kept** — the six-state table, gutter precedence, mid-operation discipline, "lenses never on by
   default", "no green", "⚖ at site and at fix". Then a short honest **Limits** list from 08 §7 (verdicts are
   mocked from the fixture; no solver runs here; sizes chosen, not tested with students).

## Engineering
- Reuse. The ten prototypes' sources are in `/home/jmandel/hobby/.agent-scratch/codalon-viz/`: `p10/` (interpreter
  `engine.js`, `checkers.js`, hole mechanics, chip editing, undo), `s03/` (sequent rendering, chips, `interp.js`),
  `src01/` (region/fence/comb/socket/spill drawing, zoom lens), `ring02/src` (ring lens), `05/` (lap chart),
  `gen06/` (mirror), `w07/` (ghost track, witness band, substituted-predicate card), `08/core.js` (sampler).
  Borrow freely but **unify**: one interpreter, one renderer for shapes, one chip vocabulary, one slider component.
- Fixture: `research/fixture.json`. The interpreter must reproduce its key frames (self-check in the footer, as
  p10 and 07 did).
- Interactions: ←/→ step; click shape → zoom lens; click `loop` line → lap chart; click function header →
  relation plot; mirror lens is a toggle in lesson 3; hole chips edit the listing with reveal/vanish tweens; undo.
- Performance: no layout jank while scrubbing (reuse DOM nodes; `requestAnimationFrame`; tween with CSS transitions).
- QA: headless Chromium screenshots of every section in every seeded state, plus a grayscale pass; zero console
  errors; keyboard reachable; page loads in < 1 s from `file://`.

## Quality bar
This page is what a reader judges the whole study by. It must be calmer and more legible than any of the ten:
less ink in the clean state, bigger type, consistent chips, no overlapping labels at 1400 px wide, and every bug
findable from the gutter in two seconds. If a prototype's device does not survive this standard, leave it out and
say so in Limits.
