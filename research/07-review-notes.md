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
