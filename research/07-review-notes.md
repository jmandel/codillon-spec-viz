# Coordinator review notes (filled in as each prototype lands)

Scores are the builder's self-scores on the rubric in 04 §4 (Salience, Blame, Grayscale discrimination,
Vocabulary continuity, Predicate-on-shape, Causal trail, Concrete witness, Ink economy, Scale, Edit continuity),
followed by the coordinator's own observations from the screenshots and the file.

## 06 · Model/memory mirror — self 4,4,4,4,3,4,5,4,3,3
- Hash table is the centerpiece and it works: at the tombstone step the arc for key 11 is cut with a ✂ gap at slot 3, bead 11 lifts and its string frays, counters underline the discrepancy, and the clause chips below split R into (o)…(iv) with the one false chip darkred and clickable. The "R open" gray state is the key move that keeps the no-bug run calm mid-operation.
- Honest about bug (b): R itself stays true; it adds a chip "(iii) as line 38 reads it" to show which stronger property the buggy lookup silently relies on. That is exactly the "your code is fine / your spec is short" discrimination the rubric asks for.
- Scalar form (math bead vs computed bead with the invariant band between) is a reasonable degenerate case but weaker than the data-structure case. Scale limit ~8 beads, as the builder says.
- Deviations worth keeping: pills only at first failure per clause; "lemma" obligations shown as unknown or dynamic by the builder's judgment.

## 09 · Envelope strips — self 4,3,4,4,3,3,5,4,3,3
- Re-executes every program with a line-level JS interpreter that reproduces all 187 fixture key frames, so the strips are dense and the slider steps are real. Good engineering; the `#selftest` mode steps every scenario.
- The S1 picture is the best single rendering of the overflow story so far: the product strip rises above the 2^31−1 ceiling, a dotted "machine reads −2147479015" echo drops to the bottom, r steps above √n, the decreases staircase falls below 0, all on one shared x-axis.
- Checkpoint discipline (violations only count at loop-head arrivals / operation boundaries / refined writes; mid-operation excursions are gray dashed) is the right semantics and mirrors 06's "R open".
- Weak spots the builder names honestly: blame sits at the obligation site not the edit (S3: ⚖ on line 6, fix on line 3); "unknown" only appears in Section A; boolean facts have no strip (bug c first goes darkred at step 86, not 43).

## 07 · Witness track — self 4,3,4,5,2,4,5,5,3,3
- The core move works and is the most Codillon-native of the three so far: a solver witness is a dashed ghost track above the slider, replay drops it onto the real slider as a ringed ⚖ pill on its own "witness band" labelled w1…wN beside the student's run; the S1 view shows the one-iteration loop-head replay with a before/after card, a darkred input cup on `i32.gt_s`, and a dashed wrap-blame curve back to `i32.mul` annotated "46341·46341 = 2147488281 → −2147479015".
- The substituted-predicate card (values on top, evaluated sides below, false conjunct underlined, later conjuncts dimmed) is the clearest rendering of *why* a predicate is false in any prototype; the hash-table version splits `$find`'s either/or ensures into groups.
- Spurious witnesses are handled honestly: struck through, obligation falls back to unknown. Six states demonstrated on one obligation in A3.
- Weakness the builder admits and I agree with: shapes never carry predicates (predicate-on-shape 2); facts only appear in the card when something fails. This idea is a complement to 01/03/04, not a substitute.

## 05 · Invariant horizon — self 4,4,5,4,2,3,5,3,3,3
- The gate + horizon + lap chart reads well on isqrt: at the S1 replay the chart hatches "⋯ 46 340 laps not run", drops a ◇ injected column, then one back-edge column with `r·r ≤ n` dark, the staircase at −4634 and the L15 overflow row dark. The hatch for un-run laps is an honest and reusable device.
- Cells get fill from the run and border/glyph from the checker: a clean separation of "held on this run" from "proven" that other prototypes should copy.
- On the hash table the chart is dense but legible: the column header shows the slot visited (□/■/⊠) so the tombstone lap is self-identifying; the "(iii)-strong" chip in the memory strip says "false since step 217" and jumps there.
- Cost is real: each chart is 5–7 rows tall, which breaks the fixed-row-height requirement for loops (builder scores Scale 3, Ink 3 and I agree). Fine as an on-selection panel; too heavy as always-on.

## 08 · Spec sampler — self 4,3,4,3,3,2,5,3,4,4
- The patterns do the talking, exactly as intended: a wrong spec (`v*v == n`) lights every non-square; a vacuous `ensures true` has no shading and all-hollow points; the "too weak" spec is proven but the shading is a fat wedge the dots never fill; `requires false` grays the whole gcd grid. The isqrt plot's four panels (n<0 excluded, 0–36 linear, √-scaled middle, near INT_MAX) make the S1 corner case findable.
- Hash-table grid works as a diagnostic matrix: bug (c) lights exactly one row across all columns, (d) lights the two "fill to 8" rows (one as ⚖, one as ☆ unfinished). Each failing cell carries the line number of its first failed check.
- Honest framing: "SAMPLES · NOT PROOF" header, "blank area = never run, not fine", and the proof verdict line sits above the samples. The builder correctly notes nothing here proves anything; verdicts come from the fixture.
- Weak on causal trail (2): a lit cell tells you *that* and *where the first check failed*, not *why*; pairs naturally with 07's substituted-predicate card or 03's sequents.

## 01 · Shape-as-value-space (containment / spill) — self 4,3,4,4,4,3,4,3,4,3
- The most literal extension of Codillon's vocabulary: the rectangle is the number line (linear for |v|≤8, log to the walls), fences with filled/hollow caps, a comb for parity, sockets for finite sets, and the spill as a hatched darkred sliver above the cup's rim. Predicate-on-shape is the strongest of any prototype (parity, bounds and sets read without text).
- The overflow story is drawn as a *nub past the INT_MAX wall* for the mathematical value and a dotted wrap arc to where the machine reads it; before replay the spill is a dashed ghost with "n = 2³¹−1", after replay it is solid hatch. Correct six-state behaviour.
- Cost: shapes had to grow from 30 px to 140 px wide to be legible, and the spill slivers are small (6 px minimum); at page zoom the bug is findable from the gutter ⚖ and the dotted darkred connection more than from the sliver itself. Hover zoom carries the detail. Ink economy suffers because every refined shape always draws its region.
- Memory panel reuses the same cups per slot field (state sockets {0,1,2} with EMPTY removed while on a probe path; key sockets = keys of M; value socket = M[key]) — a clean way to make R geometric per cell, complementary to 06's whole-structure view.

## 02 · Wraparound ring — self 4,4,4,4,3,3,5,4,4,4
- The ring is a genuinely Wasm-native idea: 0 at the bottom, the signed seam at the top, the unsigned seam at the bottom, the comparison operator drawn as a *cut* at its seam that swings from bottom to top when `gt_u` becomes `gt_s`. The mathematical term spirals outward past the seam and the bead lands where it wraps. Twin tick labels (s/u) with the operator's reading in bold.
- The table ring and the i32 ring rhyme as hoped: bug (a) runs the probe arc off the table ring through the seam to a phantom "slot 8 = address 65536"; bug (d) closes the ring with a darkred inner circle and spirals the probe.
- The builder's loupe (a linear integer strip under any ring whose values fit in ~200 consecutive integers) is a necessary addition: the fisheye alone cannot separate small integers, which is where S2/S3 live.
- Weakness: 22 px margin rings only separate refuted from everything else in grayscale; the detail lives in the pinned lens rings. Predicates live beside the type shapes, not inside them (unlike 01).

## 03 · Sequent fractions — self 4,4,4,5,4,4,5,3,4,3
- Closest to Codillon's existing fraction: the rule itself is the verdict (solid / dashed-indigo-star / dotted-slate-with-count / snapped-apart darkred / hollow halves / faded ○). Facts are ~30 tiny iconic chips sitting on "seats" above and below the rule; a required fact floats off its seat when refuted; a missing fact is Codillon's empty fade-up cup holding the chip with a dotted wire to the line that should have supplied it.
- Bug (b) at line 41: the broken rule shows k=11, i=3 and an empty cup for "st = EMPTY", plus the right panel's operation-level sequent "R at entry ⊢ R at exit" that stays open mid-operation. Bug (c) line 159 shows a *valid step resting on a false premise*: a solid rule with a darkred hypothesis, which no other prototype distinguishes.
- Honest weakness, which I confirm from the zoomed shot: at normal size the snapped rule is subtle; the gutter ⚖ and commentary carry first glance. Chips are dense enough that the legend is required reading. Ink economy 3: the clean view has one indigo/dotted rule (the nonlinear lemma left as unknown on purpose).
- Builder puts ⚖ at both the obligation site and the line to change; worth adopting as a rule.

## 10 · Synthetic proof holes — self 5,4,4,5,3,4,4,5,5,3
- The strongest *editing* story and the most Codillon-native mechanism: the hole is a dashed inserted row with 𝄽 (a quarter rest, "a measured silence the bar still owes") in the gutter, exactly where the synthetic `end` idiom already lives. Hypotheses on top with witness values in shapes, broken rule, goal split into conjunct chips, and up to three suggestion chips tagged code / spec / invariant / lemma / admit.
- The S1 hole after `br $grow` reads completely without prose: `$n 2147483647 · $r 46340 · v₁₅ −2147479015 (46341² wrapped past 2³¹−1)` above a snapped rule, `r'·r' ≤ n  2147488281 ≤ 2147483647` below in darkred, chips "17: i32.gt_s → i32.gt_u" and "tighten requires".
- Walks 01 §5's three-stage student path for real: accepting each stage's first chip flies the new line to where it belongs (invariant lines 7–8), re-derives holes with reveal/collapse animations, shakes on a refused lemma instance, and ghosts everything downstream of an `(@assume …)`. Undo exists.
- The hash-table hole at `$find`'s early return embeds a mini memory strip showing key 11 past the TOMB and offers either the tombstone-aware test or the stronger invariant the buggy code assumes (which then moves the hole to delete's store and is false there). This is the best illustration of "fix the code or fix the spec" as a visible fork.
- Weaknesses: predicate-on-shape 3 (facts appear only in holes), scale 3 (functions without holes are folded; Codillon has no folding today).
