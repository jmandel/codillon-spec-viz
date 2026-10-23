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
