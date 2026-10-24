# Audit of the ten gcd-as-a-type angles (for artifacts/gcd-type-gallery.html)

Scope: every figure in gcdviz/NN/fig-*.svg (NN = 01…10). For each figure, every number and claim in its text
was extracted and recomputed independently in Python (divisor sets, intersections, gcds, prime exponents,
lattice structure, Bézout coefficients, Euclid traces, tilings, fibers, invariant sets drawn on grids, Venn
compartments, the reasons given for each type error). Each SVG was validated with `xmllint --noout`,
rendered with `rsvg-convert` and inspected by eye for overlaps and clipping.

Source directories were not modified. Fixes are applied by reproducible scripts in
`.agent-scratch/codalon-viz/gallery-build/fixes/NN.py`, which read the source SVGs and write corrected copies to
`gallery-build/fixed/NN/`; the page inlines those copies. Angle 05 was redrawn from its own design by
`gallery-build/regen/gen05.py` (see its section). Classes: MATH (wrong number or false claim), MISLEADING
(true but reads wrong), LAYOUT (overlap/clipping), PALETTE (colour rule broken), NIT.

## Summary

| angle | figures | MATH fixed | other fixes | excluded | hero on the page |
|---|---|---|---|---|---|
| 01 divisibility lattice | 5 | 0 | 6 (1 palette, 5 layout) | none | fig-1 |
| 02 divisor strips | 5 | 1 | 4 misleading | none | fig-5 |
| 03 prime-exponent space | 5 | 0 | 4 (misleading, layout, nit) | none | fig-1 |
| 04 rectangle tiling | 5 | 2 (Div(0) written without 0) | 6 (palette, misleading, layout) | none | fig-2 |
| 05 state-space invariant | 4 | 0 (one nit) | all four redrawn (background, density, clipping, palette) | none | fig-1 (redrawn) |
| 06 predicate regions | 5 | 0 | 16 (misleading, layout, nit) | none | fig-1 |
| 07 Bézout / ideal | 5 | 0 | 8 (misleading, layout) | none | fig-1 |
| 08 dependent family | 5 | 0 | 7 (misleading, layout, nit) | none | fig-2 |
| 09 typing derivation | 5 | 3 (all fig-5) | 3 | none | fig-3 |
| 10 Codillon editor idiom | 5 | 4 (all fig-3) | about 10 (misleading, palette, layout, nit) | none (fig-2 captioned "abridged") | fig-4 |

Unchanged from source: 01 fig-1, fig-3; 02 fig-3, fig-4; 03 fig-1, fig-2; 04 fig-1, fig-4; 09 fig-1, fig-3.
On the page, 01's hero is fig-1, not the auditor's pick (fig-2): the section is about what the type *is*.

## Final cross-check (after fixes, over all 49 figures on the page)
`gallery-build/crosscheck.py` extracts every SVG text line and recomputes each equality of these forms:
`Div(n) = {…}` (73), `Div(a) ∩ Div(b) = {…}` (38 + 3 written as `{…} ∩ {…} = {…}`, checked by eye),
`Gcd(a, b) = {g}` (66), `x mod y = r` (20), Bézout `a·(x) + b·(y) = v` (2). All 202 hold.
All 49 inlined SVGs pass `xmllint --noout`. None has scripts, images, foreignObject or external hrefs.


---

### 01 — Divisibility lattice

**Checked:**
- fig-1: Div(12)={1,2,3,4,6,12} ✓, Div(8)={1,2,4,8} ✓, Div(12)∩Div(8)={1,2,4}=Div(4) ✓, lcm(12,8)=24 ✓, Div(24) has 8 nodes and exactly 10 cover edges (1–2, 1–3, 2–4, 2–6, 3–6, 4–8, 4–12, 6–12, 8–24, 12–24) ✓, all drawn with the correct ×2/×3 labels; node placement checked (×2 = (−72,−96), ×3 = (+104,−96) on every edge) ✓; hull membership checked geometrically (navy hull = Div(12), gray capsule = Div(8), purple capsule = {1,2,4}) ✓; exponent min 2^min(2,3)·3^min(1,0)=4 ✓; prime-factor sublabels 2², 2·3, 2³, 2²·3, 2³·3 ✓.
- fig-2: g=2: Div(2)={1,2} ⊊ {1,2,4}, witness 4∤2 ✓. g=8: Div(8)={1,2,4,8} ⊋ {1,2,4}, 8∤12 ✓. g=6: Div(6)={1,2,3,6} ≠ {1,2,4}, 6∤8 and 4∤6, incomparable with {1,2,4} ✓. Red cones enclose exactly Div(2), Div(8), Div(6) ✓.
- fig-3: Div(72) = 12 nodes ✓, lattice coordinates consistent ✓. Gcd(12,8)=4, Gcd(18,12)=6 with Div(18)∩Div(12)={1,2,3,6}, Gcd(9,8)=1 with {1} ✓; exponent pairs (2,1)/(3,0), (1,2)/(2,1), (0,2)/(3,0) and their mins (2,0), (1,1), (0,0) ✓; hulls enclose the right node sets in all three panels ✓; 4 ∉ Gcd(18,12), 4 ∉ Gcd(9,8) ✓.
- fig-4: covers of Div(12) (7 edges) ✓; 1∣2∣4∣12 ⟺ Div(1)⊊Div(2)⊊Div(4)⊊Div(12) ✓; Div(g)⊆Div(a) ⟺ g∣a (also true for 0) ✓; Div(0)=ℕ, Gcd(12,0)={12}, Gcd(0,0)={0} ✓.
- fig-5: Euclid trace (12,8)→(8,4)→(4,0), 12 mod 8=4, 8 mod 4=0 ✓; CD invariant {1,2,4} at every step ✓; Div(12)∖Div(8)={3,6,12} ("×3 branch shed") ✓; Div(4)∩Div(0)=Div(4) ✓.
- Palette: no green; #8b0000 used only in fig-2 (plus an unused marker def elsewhere) ✓; #4b0082 misuse in fig-4 (see below).

**Findings and fixes:**
- [fig-1] No errors found. NIT: "Base type ℕ = all lattice nodes" — the drawn lattice is only Div(24); NIT: 10-px prime-factor sublabels are below the 11-px annotation floor (legible). Not fixed.
- [fig-2] LAYOUT — "4 ∤ 2 (misses 4)" touched the dashed red 4→2 arrow → x 139→143.
- [fig-2] LAYOUT — "4 ∤ 6, 6 ∤ 8" collided with the rings of nodes 4 and 6 → y 289→279.
- [fig-2] LAYOUT — "g = 6 ✗" sat on the red Div(6) cone edge and gray Div(12) hull edge → moved to (790, 271).
- [fig-2] NIT — Case B "Fails: g ∣ 12 (not a common divisor)" names the failing condition (parallel to Case A) but can be read as an assertion. Not fixed.
- [fig-3] No errors found.
- [fig-4] PALETTE — Div(2) hull and label "Div(2)" in indigo #4b0082 (reserved for "unknown") → #555555 (2 occurrences).
- [fig-4] LAYOUT — "• When y = 0 in Euclid’s algorithm, x = 12 ALREADY inhabits Gcd(12, 0)." overflowed its box on both sides → "• At y = 0 in Euclid’s loop, x = 12 already inhabits Gcd(12, 0)."
- [fig-4] NIT — "Order-Embedding Isomorphism" (it is an order embedding); dashed 4→0, 6→0, 12→0 arrows are divisibility, not Hasse covers. Not fixed.
- [fig-5] LAYOUT — footer "Refinement Type Takeaway: The purple cone … are the runtime values." overflowed the footer box → "Takeaway: the purple cone {1, 2, 4} is the compile-time proof certificate; the navy pairs (12,8) → (8,4) → (4,0) are runtime values."
- [fig-5] MISLEADING — title/subtitle "Slides the Outer Cones Down" / "shrinks the upper cones": true for this trace (Div(12)∪Div(8) ⊃ Div(8)∪Div(4)) but not in general (13,8)→(8,5) brings in 5 ∉ Div(13)∪Div(8). Only the intersection is invariant. Not fixed (claim is about the drawn trace; flag in caption).

**Verdict per figure:**
- fig-1: include
- fig-2: include-with-fix
- fig-3: include
- fig-4: include-with-fix
- fig-5: include-with-fix

**Strongest figure:** fig-2 — three side-by-side lattices make "too small", "too big" and "wrong branch" visibly different failures of one cone-equality test.

**Gallery copy**
- heading: Top of two cones
- claim: In the divisibility lattice, Div(a) and Div(b) are downward cones; Gcd(a, b) is the single node whose own cone equals their overlap.
- encoding:
  - node position → prime exponents (up-left ×2, up-right ×3)
  - arrow u → v → v = u·p, so u ∣ v
  - dashed hull → Div(a) or Div(b), everything below the input
  - purple capsule → Div(a) ∩ Div(b), the target cone
  - dark-red cone → Div(g) of a wrong candidate
- per-figure captions:
  - fig-1: Div(12) and Div(8) overlap in {1, 2, 4}; that overlap is exactly the cone below 4.
  - fig-2: 2 sits inside the overlap but misses 4; 8 leaves Div(12); 6 strays onto the ×3 branch.
  - fig-3: Same lattice, different inputs: the overlap and its top move to 4, 6, then 1.
  - fig-4: d ∣ n is cone containment; 0 sits above everything, so Gcd(12, 0) = {12}.
  - fig-5: Euclid’s steps (12,8) → (8,4) → (4,0) change the cones but never their overlap {1, 2, 4}.
- hides: It only stays readable for two primes, mod steps jump across the lattice rather than following edges, and fig-5’s “cones shrink” holds for this trace, not in general.
- table row: Hasse diagram of divisor cones | red cone not equal to the purple cone | yes, cones move with (a, b) | partly, invariant overlap shown, not derived | teaching the definition

---

### 02 — Divisor strips on a number line

**Checked:** (column positions parsed from circle cx: x = x0 + step·d, every filled/hollow/crossed mark mapped to its d)
- fig-1: Div(12) pins at {1,2,3,4,6,12} ✓, Div(8) pins at {1,2,4,8} ✓, sockets CD(12,8) = {1,2,4} ✓, Div(4) pins fill exactly {1,2,4} ✓, d = 0 shown as a non-member of Div(12), Div(8) (0 ∤ 12, 0 ∤ 8) ✓, value line lights only 4 ✓.
- fig-2: g=2 pins {1,2}, empty socket 4 ✓; g=8 pins {1,2,4}, spill 8 ✓; g=6 pins {1,2}, spills 3, 6, empty socket 4 ✓; g=4 exact ✓; value line: ✗ at 2, 6, 8, lit 4 ✓; "No spills ⇔ g divides a and b", "No empty sockets ⇔ every common divisor divides g" ✓.
- fig-3: (12,8) → (8,4) → (4,0), 12 mod 8 = 4, 8 mod 4 = 0 ✓; rows Div(12), Div(8), Div(8), Div(4), Div(4) correct ✓; Div(0) row has pins at every d ∈ 0..12 including 0 ✓; CD(12,8)=CD(8,4)=CD(4,0)={1,2,4} ✓; return line lights 4 with 12 → 8 → 4 trail ✓.
- fig-4: Div(13)={1,13}, Div(8)={1,2,4,8}, CD={1}, Gcd(13,8)={1} ✓; Div(0)=ℕ and CD(0,0)=ℕ rows include d=0 ✓; g=12 pins at {1,2,3,4,6,12}, empty sockets at {0,5,7,8,9,10,11,13} ✓; g=0 fills all ✓; Gcd(0,0)={0} ✓.
- fig-5: rows g=1 (empty 2,4), g=2 (empty 4), g=4 (exact), g=8 (spill 8), g=12 (spill 3,6,12), g=0 (spill 0,3,5–12), g=6 (empty 4, spill 3,6) ✓; {g ≤ 12 | Div(g) ⊆ CD} = {1,2,4} ✓, {g ≤ 12 | CD ⊆ Div(g)} = {0,4,8,12} ✓, intersection {4} ✓; ⊂ labels (Div(1) ⊂ CD, CD ⊂ Div(8), …) ✓.
- Palette: no green; #8b0000 only on violations (plus unused marker defs); no indigo ✓.

**Findings and fixes:**
- [fig-1] MISLEADING — "Every socket filled; 0 spills": on an axis that contains d = 0 this reads as "divisor 0 spills" → "Every socket filled; no spills". NIT: "d > 0 dividing 12" is redundant (0 ∤ 12 anyway); not fixed.
- [fig-2] MISLEADING — the three "↑" pointers were centred text, so each arrow sat under the wrong column: "↑ Empty socket: 4 ∈ CD(12,8) but 4 ∤ 2" pointed at d≈2, "↑ Spilled divisor: 8 | 8 but 8 ∉ CD(12,8)" at d≈5, "↑ 3, 6 spill out & socket 4 is empty" between 2 and 3 → left-anchored so "↑" sits under d = 4, d = 8 and d = 3 respectively.
- [fig-2] MISLEADING — "WELL-TYPED: 0 empty, 0 spills" (same 0 ambiguity) → "WELL-TYPED: exact match".
- [fig-2] NIT — ASCII "|" instead of "∣" in "8 | 8", "fails g | 12", "fails g | 8"; title says spilled pins mean "Too Large" although g = 6 is incomparable, not larger. Not fixed.
- [fig-3] No errors found.
- [fig-4] No errors found.
- [fig-5] MATH — heading "All Candidates g ∈ 0..12 Tested Against Sockets…" but only 7 values are drawn (3, 5, 7, 9, 10, 11 absent) → "Candidates g ∈ {0, 1, 2, 4, 6, 8, 12} Tested Against Sockets…".
- [fig-5] MISLEADING — the multiples half-type is named "CommonMultOfCD(12, 8)" in the subtitle and "MultOfCD(12, 8)" below → subtitle renamed to "MultOfCD".

**Verdict per figure:**
- fig-1: include-with-fix
- fig-2: include-with-fix
- fig-3: include
- fig-4: include
- fig-5: include-with-fix

**Strongest figure:** fig-5 — one grid shows every candidate’s pins against the sockets and then splits the type into “no spills” ∩ “no empty sockets” = {4}.

**Gallery copy**
- heading: Pins in sockets
- claim: Gcd(a, b) is the one number whose row of divisors fills every common-divisor socket exactly, with no socket left empty and no pin spilling.
- encoding:
  - column → a candidate divisor d = 0, 1, 2, …
  - navy pin → d divides this row’s number
  - purple socket → d is a common divisor of a and b
  - hollow dark-red socket → common divisor the candidate misses
  - crossed dark-red pin → candidate divisor that is not common
- per-figure captions:
  - fig-1: Div(12) and Div(8) agree on sockets 1, 2, 4; only Div(4) fills exactly those, so the type is {4}.
  - fig-2: g = 2 leaves socket 4 empty, g = 8 spills 8, g = 6 does both.
  - fig-3: Each Euclid step changes both rows but leaves the sockets {1, 2, 4}; at y = 0 the full row Div(0) changes nothing.
  - fig-4: Coprime 13, 8 share one socket {1}; for (0, 0) every d is a socket and only g = 0 fills them.
  - fig-5: “No spills” gives {1, 2, 4}, “no empty sockets” gives {0, 4, 8, …}; both together give {4}.
- hides: A literal number line only works for small numbers and shows divisors as unrelated dots, so the order structure behind “greatest” stays implicit.
- table row: rows of divisor dots against sockets | hollow red socket or crossed red pin | partly, sockets recomputed per (a, b) | yes, socket row unchanged across steps | teaching the definition; debugging a program

---

### 03 — Prime-exponent space

**Checked:**
- fig-1 (12, 8): 12 = 2²·3¹ → point (2,1), 8 = 2³·3⁰ → (3,0) ✓. Div(12)={1,2,3,4,6,12} ✓, Div(8)={1,2,4,8} ✓, Div(12)∩Div(8)={1,2,4} ✓; min(2,3)=2, min(1,0)=0 ✓; g = 4 = 2²·3⁰ ✓. Grid values 9,18,36,72,144 / 24,48 / 16 = 2^e₂·3^e₃ ✓. Geometry (x = 96+96·e₂, y = 430−122·e₃): dashed box spans e₂∈[0,2], e₃∈[0,1]; dotted box e₂∈[0,3], e₃=0; purple box e₂∈[0,2], e₃=0 ✓. Navy points = divisors outside the overlap (3, 6, 12, 8) ✓.
- fig-2: 72 = 2³·3², 48 = 2⁴·3¹, min = (3,1) → 24 ✓; Div(72)∩Div(48) = {1,2,3,4,6,8,12,24} (8 = 4×2 points) ✓. 13 = 13¹, 8 = 2³, min = (0,0) → 1, Div(13)∩Div(8) = {1} ✓; 104 = 2³·13 at (3,1) ✓. (24, 0): min((3,1),(∞,∞)) = (3,1), Gcd(24,0) = {24} ✓; row labels 9,18,36,72,144 / 3,6,12,48 / 1,2,4,8,16 ✓. All three panels' box extents parsed from rect coordinates and match the exponent ranges ✓.
- fig-3: g=2 → Div(2)={1,2} ⊂ {1,2,4} (strict) ✓, witness 4 (4|12, 4|8, 4∤2) ✓, e₂(2)=1 < min(2,3)=2 ✓; g=12 → Div(12)∖Div(8) = {3,6,12} ✓, e₃(12)=1 > e₃(8)=0 ✓, 12∤8 ✓; g=8 → Div(8)∖Div(12) = {8} ✓, e₂(8)=3 > e₂(12)=2 ✓. Red boxes/hatched cells sit at the right exponents (g=2 box e₂∈[0,1]; missing cell e₂=2; g=12 box [0,2]×[0,1] with row e₃=1 hatched; g=8 box e₂∈[0,3] with cell e₂=3 hatched) ✓. Dark red used only for these violations ✓.
- fig-4: 72 mod 48 = 24, 48 mod 24 = 0 ✓; (3,2),(4,1),(3,1) ✓; Div(48)∩Div(24) = Div(24) = Div(72)∩Div(48) ✓; purple box [0,3]×[0,1] in all three panels ✓; box extents parsed ✓.
- fig-5: 1071 = 3²·7·17 ✓, 462 = 2·3·7·11 ✓; |Div(1071)| = 3·2·2 = 12 ✓, |Div(462)| = 2⁴ = 16 ✓; per-prime mins 2:0, 3:1, 7:1, 11:0, 17:0 ✓ (bar heights parsed: 36 px per exponent unit, all correct); Div(1071)∩Div(462) = {1,3,7,21} ✓; 9, 63 ∈ Div(1071) ✓; product 1·3·7·1 = 21 ✓.
- Palette: no green; indigo unused; #8b0000 appears only in fig-3 (violations) plus unused marker defs elsewhere ✓.

**Findings and fixes:**
- [fig-1] No errors found. (Nit only: the dotted Div(8) border runs through the halos of labels "1" and "2"; legible.)
- [fig-2] LAYOUT (nit) — label halos for "3", "6", "12" on row e₃=1 cut notches in the purple box's top border (panels A and C) → not fixed: cosmetic and the labels stay legible.
- [fig-2] NIT — the label for e₂=0 sits right of its point and the rest sit left of theirs, so "1 2", "3 6", "9 18" sit in the same gap between columns 0 and 1 → not fixed: reading order is still unambiguous.
- [fig-2] MISLEADING (minor) — Div(0) = ℕ is drawn as a closed dashed box over the visible grid and reads as bounded. It also covers only positive integers: 0 ∈ Div(0) has no exponent point. → not fixed: it is labelled "unbounded (∞, ∞) ↗", and the gallery's "hides" line covers the rest.
- [fig-3] LAYOUT — in panel 1 the red arrow (x=190) runs through the label "12" of point (2,1) → fixed: centred "12" over its point (x=176).
- [fig-3] NIT — "Illegal row e₃ = 1: {3, 6, 12} ∤ 8!" applies ∤ to a set → fixed: "Illegal row e₃ = 1: 3, 6, 12 ∤ 8!".
- [fig-4] MISLEADING — both "Outer box shrinks toward corner (3,1)." captions. At 72→48, x's box gets wider (e₂ 3→4). At 48 mod 24 = 0, y's box grows to all of ℕ. → fixed: step 0 "New y = 24: its box is exactly the purple box."; step 1 "New x = 24 at the corner; Div(new y = 0) = ℕ."
- [fig-4] NIT — divisors outside the overlap (9, 18, 36 of 72; 16 of 48) are gray here but navy in fig-2 → not fixed: the box outlines still show membership.
- [fig-5] LAYOUT — tick labels "e₇=0/1" (x=90) touch the purple box's left edge, and "e₃=k (3^k)" (y=561) touch its bottom → fixed: moved to x=85 and y=566.

**Verdict per figure:** fig-1 include; fig-2 include; fig-3 include-with-fix; fig-4 include-with-fix; fig-5 include-with-fix.

**Strongest figure:** fig-1: two outlined boxes, one filled overlap and a single ringed corner show "Div(g) = Div(a) ∩ Div(b) has exactly one solution" without any prose.

**Gallery copy**
- heading: Prime-exponent boxes
- claim: Plot each number by its exponents of 2 and 3: Div(n) becomes the box below n, and Gcd(a, b) is the one point whose box is exactly the overlap.
- encoding:
  - grid point (e₂, e₃) → the number with 2-exponent e₂ and 3-exponent e₃
  - navy dashed / dotted box → Div(a), Div(b): every point inside divides the corner
  - purple filled box → Div(a) ∩ Div(b), the box below the componentwise minimum
  - double-ringed purple corner → g, the only inhabitant of Gcd(a, b)
  - dark-red hatch → candidate box overflows a or b, or misses a divisor
- per-figure captions:
  - fig-1: Div(12) and Div(8) are boxes; their overlap {1, 2, 4} has one top-right corner, 4 = 2²·3⁰.
  - fig-2: Changing the inputs reshapes the overlap: (72, 48) gives 24, coprime (13, 8) collapses to 1, and (24, 0) leaves Div(24).
  - fig-3: Wrong g for (12, 8): 2's box misses 4; 12's overflows b = 8; 8's overflows a = 12.
  - fig-4: Euclid on (72, 48): the outer boxes change each step, but the purple overlap stays [0,3]×[0,1] until y = 0.
  - fig-5: 1071 and 462 involve five primes; the box splits into one min-bar per prime, giving 3¹·7¹ = 21.
- hides: The picture needs factorizations Euclid never computes: a remainder can raise an exponent (1071 mod 462 = 147 = 3·7²), and 0 has no point, so Div(0) = ℕ is only a convention.
- table row: origin-anchored boxes on a prime-exponent grid | candidate's box overflows a's or b's box, or falls short | yes — the overlap box reshapes with every (a, b) | partly — overlap stays fixed, but boxes jump unpredictably | teaching the definition

---

### 04 — Euclid's rectangle tiling

**Checked:**
- fig-1: d=1…6 against 12×8. Tiles for d ∈ {1,2,4} ✓ (12 = 12·1 = 6·2 = 3·4; 8 = 8·1 = 4·2 = 2·4). Misfits: 8 % 3 = 2; 12 % 5 = 2 and 8 % 5 = 3; 8 % 6 = 2 ✓. Every small multiple is drawn at 7 px/unit (84×56 = 12×8, 3:2) ✓. Tile counts: 12×8, 6×4 and 3×2 grids; d=3 has 4 columns plus a 3rd row overhanging by 1; d=5 overhangs by 3 to the right and 2 below; d=6 has a 2nd row overhanging by 4 ✓. Nesting panel: 204×136 = 12×8 at 17 px/unit, bold 4-grid, dashed 2-grid, 1-grid; master tile 68 px = 4 ✓. Table: Div(1)={1}, Div(2)={1,2}, Div(3)={1,3}, Div(4)={1,2,4}, Div(6)={1,2,3,6}, Div(8)={1,2,4,8}, Div(12)={1,2,3,4,6,12}. The stated missing or misfitting tiles are all correct ✓.
- fig-2: 12 = 1·8 + 4, 8 = 2·4 + 0 ✓; drawn at 9 px/unit (8×8 = 72², 4×8 = 36×72, 8×4 = 72×36), cut lines at the right offsets ✓. Div(12)∩Div(8) = Div(8)∩Div(4) = Div(4) = {1,2,4} ✓. Trace B: 30 = 1·18 + 12, 18 = 1·12 + 6, 12 = 2·6 + 0 ✓. Div(30) = {1,2,3,5,6,10,15,30}, Div(18) = {1,2,3,6,9,18}, Div(12) = {1,2,3,4,6,12}, Div(6) = {1,2,3,6} ✓. Every intersection is {1,2,3,6} ✓. Drawing at 5.2 px/unit: 156×93.6 = 30×18; squares 18, 12, 6, 6; dashed 6-grid every 31.2 px ✓. Lemma sketch: y×y region is square (68×68) ✓.
- fig-3: 13 = 1·8+5, 8 = 1·5+3, 5 = 1·3+2, 3 = 1·2+1, 2 = 2·1+0 (5 steps) ✓. Spiral at 16.5 px/unit: squares 8, 5, 3, 2, 1, 1 are placed exactly (13×8 = 214.5×132) ✓. Every row of the table intersects to {1} ✓. d=2 strip: 6 tiles + a 7th overhanging 13 by 1 ✓. 21×0 strips at 13 px/unit: 21 = 1·21 = 3·7 = 7·3 = 21·1 (1, 3, 7, 21 tiles drawn) ✓; d=6: 4 tiles = 24, overhang 3 ✓. Gcd(0,0) = {0} ✓.
- fig-4: g=8: 2 tiles × 8 = 16 ≠ 12, 12 mod 8 = 4, overhang 4×8 drawn at 12.2 px/unit (part 4×8 + overhang 4×8) ✓. Div(8) ⊈ Div(12)∩Div(8) = {1,2,4} ✓. g=2: 4|12, 4|8, 4∤2 ✓; 2-grid and 4-grid drawn at 10.5 px/unit; inset 4-tile is twice the side of the 2-tile ✓. g=4: 3×2 tiles ✓; both inclusions hold ✓. Buggy step: (12 mod 8) − 1 = 3 → (8, 3); Div(8)∩Div(3) = {1}; Gcd(8,3) = {1} ⊄ {4} = Gcd(12,8) ✓. Post-state drawn 8×3 (72×27 at 9 px/unit), 4×4 tiles overhang by 1 ✓.
- fig-5: gcd = 3 cells in [0,12]² are exactly the 13 marked (0,3),(3,0),(3,3),(3,6),(3,9),(3,12),(6,3),(6,9),(9,3),(9,6),(9,12),(12,3),(12,9) ✓. gcd = 4 cells are exactly the 9 marked (0,4),(4,0),(4,4),(4,8),(4,12),(8,4),(8,12),(12,4),(12,8) ✓. Trajectories (12,8)→(8,4)→(4,0) and (9,6)→(6,3)→(3,0) ✓. Symbolic lemma (d|x ∧ d|y) ⇔ (d|y ∧ d|x mod y) holds for y > 0 (else-branch) ✓. Code-pane derivations are correct ✓.
- Palette: no green; indigo only for the unknown (x, y) panel ✓. Dark red marks overhangs and type errors, except for the cut lines listed below.

**Findings and fixes:**
- [fig-1] No errors found.
- [fig-2] PALETTE — Euclid cut lines are dark red #8b0000 (lemma, steps 0–1, three lines in trace B, plus the "cut" label) but are not violations → fixed: recoloured to ink #222222.
- [fig-2] MATH — Div(0) in the trace-B table is "ℕ (all d ≥ 1)", but 0 | 0, so 0 ∈ Div(0) → fixed: "ℕ (all d ≥ 0)".
- [fig-2] MISLEADING — the halting state (x=4, y=0) is drawn as a 4×4 square captioned "0 remainder!", which reads as a 4×4 state → fixed: caption now "g×g tile; state is 4×0" (geometry unchanged).
- [fig-2] LAYOUT — lemma labels "y × y" and "r × y" sit on the dashed mid-line → fixed: moved down into the lower half (y 156 → 174).
- [fig-2] NIT — the "Tiles fitting" key squares are at half the rectangle's scale (d=4 drawn 18 px; the rectangle's 4 is 36 px) → not fixed: they are a key, not a measurement.
- [fig-2] LAYOUT (nit) — the "cut" label almost touches the lemma heading → not fixed.
- [fig-3] MATH — "Div(0) = ℕ = {1, 2, 3, …}" contradicts the same panel's "Gcd(0, 0) = … = { 0 }" and "Only g = 0 has Div(g) = ℕ", because 0 ∉ {1, 2, 3, …} → fixed: "{0, 1, 2, …}".
- [fig-3] NIT — "Zero Width" / "0-width rectangle", but in 21 × 0 the zero side is b, the height (drawn as a horizontal segment) → fixed: "Zero Height" / "0-height".
- [fig-4] No errors found.
- [fig-5] PALETTE — the q·y | r cut line in the symbolic strip is dark red → fixed: #222222.
- [fig-5] MISLEADING — "reveals the fiber's unique inhabitant x = g". A fiber has many points; the singleton is the type Gcd(x, y) = {g} → fixed: "the type's unique inhabitant".
- [fig-5] NIT — the return-type line "g : { v ∈ ℕ | … }" is indigo (reserved for unknowns) → not fixed: defensible, since a and b are unknown at compile time.

**Verdict per figure:** fig-1 include; fig-2 include-with-fix; fig-3 include-with-fix; fig-4 include; fig-5 include-with-fix.

**Strongest figure:** fig-2 (fixed): to-scale cuts of 12×8 and 30×18 carry the same purple grid through every step, so the loop invariant is visible.

**Gallery copy**
- heading: Euclid's square tiling
- claim: A common divisor is a square tile that exactly fills the a×b rectangle; cutting off b×b squares keeps every such tile, ending at the largest, the gcd.
- encoding:
  - navy rectangle → input pair or loop state (x, y), drawn to scale
  - purple d×d grid → a common divisor: tiles both sides with nothing left over
  - dark-red hatched overhang → d does not divide a side: a type error
  - black dashed cut → one Euclid step removing q squares of side y
  - indigo rectangle → unknown (x, y) at compile time
- per-figure captions:
  - fig-1: Of square sizes 1–6, only 1, 2, 4 tile 12×8 without overhang; every valid grid nests in the 4×4 tile.
  - fig-2: Cutting y×y squares off x×y never adds or removes a fitting tile: (12, 8) keeps {1,2,4}, (30, 18) keeps {1,2,3,6}.
  - fig-3: Coprime 13×8 spirals down to 1×1 squares; a 21×0 strip's zero height accepts every tile, leaving Div(21): Gcd(21, 0) = {21}.
  - fig-4: Wrong answers for (12, 8): 8×8 tiles overhang width 12; 2×2 misses the 4×4 tile; a buggy remainder changes the type.
  - fig-5: Points with equal gcd form fibers; each Euclid step stays in its fiber; a symbolic cut proves it for unknown (x, y).
- hides: Only small inputs fit to scale (1071 × 462 must be schematic), zero sides have no area so Div(0) = ℕ is a convention, and "largest tile" can hide the clause that every common tile nests inside g.
- table row: a×b rectangle tiled by d×d squares | tiles overhang the edge, or a coarser tile is missed | yes — rectangle shape is the index (a, b) | yes — cut squares carry exactly the same tiles | teaching the definition; debugging a program

---

### 05 — State-space invariant (Gemini 3.1 Pro; figures redrawn for the gallery)
**Checked:** 
- Original fig-1 (12, 8): the 21 shaded cells in 0…20² are exactly {(x, y) | gcd(x, y) = 4} ✓; the 20 dashed successor arrows (x, y) → (y, x mod y) from shaded cells with y ≠ 0 all land on shaded cells and all lower y ✓; run (12, 8) → (8, 4) → (4, 0) ✓; exit row meets the set only at (4, 0) ✓.
- Original fig-2 (13, 8): 161 shaded cells in 0…16² = {gcd = 1} ✓; 160 arrows ✓; run 13,8 → 8,5 → 5,3 → 3,2 → 2,1 → 1,0 ✓.
- Original fig-3 (0, 0): only (0, 0) shaded = {gcd = 0} ✓.
- Original fig-4: 121 shaded cells = {gcd(x, y) even} ✓ (includes (0, 0), since gcd(0, 0) = 0 is even).
- "Each primitive ray meets the set exactly once": on the ray through primitive (p, q), gcd(k·p, k·q) = k, so exactly the k = g cell is shaded ✓ (asserted for all 21 directions in view for g = 4).
**Findings and fixes:**
- [all] LAYOUT — no background rect (ivory only via a CSS style attribute; transparent in rsvg and image viewers).
- [fig-1, fig-2, fig-4] LAYOUT — arrow fields and one ray per shaded cell drawn at full strength; in fig-2 (160 arrows) and fig-4 (110 arrows + 121 rays) the set itself is hard to see.
- [fig-3] LAYOUT — label "Single exit cell: (0, 0) -> gcd is 0" is centred on the left margin and clipped to "ingle exit cell…"; the figure is a near-empty 10×10 grid.
- [fig-4] PALETTE / MISLEADING — the whole weak-invariant set (121 cells, including the correct exit cell (4, 0)) is painted dark red, although only the exit containment fails; dark red should mark only the extra exit cells.
- [fig-4] MATH (nit) — "meets exit row in many cells (2, 4, 6...)" omits (0, 0), which is in the weak set.
- → Fix: all four figures were regenerated by gallery-build/regen/gen05.py from the same computed sets (source untouched): ivory background; successor arrows only from shaded cells, thin and translucent, with obligations counted in a side panel (entry / preserved 20 of 20 / decreasing 20 of 20 / exit = {(4, 0)}); the rays get their own figure with gcd = k written along three rays; dependence shown as three small multiples (13, 8) → {1}, (15, 9) → {3}, (0, 0) → {0} instead of a lone (0, 0) grid; the too-weak invariant ("x, y both even", a genuine invariant) is drawn in pale purple, and only the 10 wrong exit cells (0, 2, 6, …, 20) and their projections are dark red. Every count in the new figures is computed and asserted.
**Verdict per figure:** original figures replaced by redrawn fig-1…fig-4 (same idea, same pairs except (15, 9) added).
**Strongest figure:** fig-1 — the invariant set, every successor arrow, and the single exit cell projected onto Gcd(12, 8) in one picture.
**Gallery copy**
- heading: The loop's state has a type
- claim: The invariant is the set of states (x, y) with gcd(x, y) = gcd(a, b); every Euclid step stays inside it, moves down, and exits at the single cell (g, 0).
- encoding: shaded cell → state (x, y) in the invariant set | light arrow → one loop step (x, y) → (y, x mod y) | navy rings and arrows → the actual run | exit row y = 0 → loop exit; its one shaded cell projects to Gcd(a, b) | dark red exit cells → results a too-weak invariant would allow
- captions: fig-1 "All 20 arrows from shaded cells land shaded and go down; the exit row meets the set only at (4, 0)." fig-2 "On each ray through the origin gcd counts 1, 2, 3, …; the set picks the k = 4 cell on every ray." fig-3 "Changing (a, b) changes the shaded set: coprime inputs give a dense set, (0, 0) a single point." fig-4 "A true but too-weak invariant (both even) passes entry and preservation and fails exit: 11 exit cells, only (4, 0) allowed."
- hides: It shows that the loop preserves the set but not why x mod y keeps the common divisors, and grids only reach small numbers.
- table row: grid of loop states, invariant shaded | exit row meets the set in many cells | yes: shaded set redrawn per (a, b) | yes: closure, descent, one exit cell | debugging a program; teaching the proof

---

### 06 — Refinement as nested predicate regions (Euler/Venn)

**Checked:** (every pill position tested in python against the circle/ellipse geometry; all 83 number pills (some listing several values) have their centre in the correct compartment, before and after fixes)
- fig-1: Div(12)={1,2,3,4,6,12} ✓, Div(8)={1,2,4,8} ✓, common {1,2,4} ✓, P₃ = 4ℕ = {0,4,8,12,16,…} ✓. Compartments: 100={3,6} ✓, 110={1,2} ✓, 101={12} ✓, 011={8} ✓, 111={4} ✓, 001={0,16,20,…} ✓, 010=∅ ✓, 000={5,7,9,10,11,13,14,15,17,…} ✓. Annotations "4 ∤ 1, 4 ∤ 2", "12 ∤ 8", "8 ∤ 12", "4 ∣ 0 … 0 ∤ 12, 0 ∤ 8" ✓. Sieve: 13 values in 0..12 ✓, stage 1 highlights {1,2,3,4,6,12} ✓, stage 2 {1,2,4} ✓, stage 3 {4} ✓.
- fig-2: nested regions T₁=Div(12) ⊃ T₂={1,2,4} ⊃ T₃={4}; pills 0,5,7,8,9,10,11 outside T₁ (all ∤ 12) ✓; 3,6,12 in T₁∖T₂ ✓; 1,2 in T₂∖T₃ ✓; 4 in T₃ ✓. Cardinalities 1, 3, 6, infinite ✓. Evidence triple (4∣12, 4∣8, ∀d∈{1,2,4}. d∣4) ✓.
- fig-3: leaked compartments are P₁∩P₂∖P₃ ∋ 1, 2; P₂∩P₃∖P₁ ∋ 8; P₁∩P₃∖P₂ ∋ 12 ✓ (geometry and shading both checked). Check badges and table: g=4 ✓✓✓; g=2 fails P₃ (4∤2) ✓; g=8 fails P₁ ✓; g=12 fails P₂ ✓; g=0 fails P₁,P₂, holds P₃ ✓; g=6 fails P₂ (6∤8), P₃ (4∤6) ✓.
- fig-4: (13,8): Div(13)={1,13}, common {1}, P₃=ℕ ✓; 13∈100, 2,4,8∈010, 0 and 3,5,6,… in P₃ only ✓. (1071,462): 1071=3²·7·17 (12 divisors) ✓, 462=2·3·7·11 (16 divisors) ✓, common {1,3,7,21} ✓, P₃ = 21ℕ ✓; 110={1,3,7} ✓, 100={9,17,51,119,153}, 010={2,6,11,14,22,33,66,77,154}, 101={63,357,1071}, 011={42,231,462}, 001∋0,84,105,… ✓. (21,0): Div(0)=ℕ, common = Div(21)={1,3,7,21} ✓, 0,42,63 ∈ P₂∩P₃∖P₁ ✓. (0,0): only g=0 satisfies ∀d∈ℕ. d∣g ✓ (d=g+1 counterexample ✓).
- fig-5: (12,8)→(8,4)→(4,0): 12 mod 8 = 4 ✓, 8 mod 4 = 0 ✓; Div(8)∩Div(4) = Div(4)∩Div(0) = {1,2,4} ✓; every pill in all three panels in its correct compartment (e.g. step 1: 8∈101, 0,12∈001) ✓. Footer identity (d∣x ∧ d∣y) ⇔ (d∣y ∧ d∣x mod y) ✓.
- Palette: #8b0000 only in fig-3 (leaks / failed checks / dropped conjunct) ✓; no indigo; no green ✓.

**Findings and fixes:**
- [fig-1] MISLEADING — P₂-only "∅" justified as "(all d ∣ 8 are ≤4 / or multiples of 4)"; ≤4 is not the reason → "(each d ∣ 8 divides 12 / or is a multiple of 4)".
- [fig-1] MISLEADING — outside pill "13, 14, 15, …" implies every n ≥ 13 is outside all circles, but 16, 20, … are in P₃ → "13, 14, 15, 17, …".
- [fig-1] NIT — "Multiples of common divisors" (reads as union) → "Multiples of every common divisor".
- [fig-2] LAYOUT — "+ Conjunct P₂(g): g ∣ 8 (keeps {1, 2, 4})" crossed the dashed T₂ boundary → "+ P₂(g): g ∣ 8 (keeps {1, 2, 4})".
- [fig-2] LAYOUT — "Upcasting drops a conjunct; every inner value is valid outside" ran onto the panel border → "Upcasting drops a conjunct; inner values stay valid".
- [fig-3] LAYOUT — pills 1 and 2 straddled the P₂ / P₁ boundaries → shrunk (r 12/13 → 10/11) and moved to (146,212), (169,212), wholly inside P₁∩P₂∖P₃.
- [fig-3] LAYOUT — badges "TYPE ERROR: Fails P₁: 8 ∤ 12 (does not divide a)" / "…P₂: 12 ∤ 8 (does not divide b)" overflowed their boxes → "…8 ∤ 12 = a" / "…12 ∤ 8 = b".
- [fig-3] MISLEADING — "Input a = 12 leaks in (no P₁∧P₂ admits 0)." is garbled (P₂ is the dropped conjunct) → "Input a = 12 satisfies P₁ ∧ P₃ and leaks in."
- [fig-4] MISLEADING — Case B pills listed incomplete compartments without an ellipsis: "63, 1071" (missing 357), "42, 462" (missing 231), "9, 17, 51" (missing 119, 153) → "63, 357, 1071", "42, 231, 462", "9, 17, 51, …", "2, 6, 11, …".
- [fig-4] LAYOUT — Case B pills straddled circle boundaries (e.g. "1, 3, 7" spanned beyond the P₁∩P₂ lens) → re-placed by a search so each pill lies inside its compartment (the 101/011 pills now use 9 px text and still touch the P₃ edge by ~2 px; the compartments are too small for anything larger). Case C "42, 63…" pill nudged inside P₃.
- [fig-4] NIT — Case D "P₁(g): g ∣ 0 = ℕ" reads as "g divides (0 = ℕ)" → "P₁ = {g | g ∣ 0} = ℕ   and   P₂ = {g | g ∣ 0} = ℕ   (both are all of ℕ)".
- [fig-5] LAYOUT — pills 1, 2 straddled the P₁/P₂ boundary in steps 0 and 1 → r 11 → 9.5, moved to y = 222 inside the lens.
- [fig-5] LAYOUT — step 2 "P₃: ∀d∈{1,2,4}. d∣g" sat on the bottom edge of the dashed P₂ = ℕ box → box height 258 → 264.
- [fig-5] MISLEADING — "3,6,12 expelled" was printed inside the Div(8) crescent, the compartment they had left → moved outside P₁ (340, 196/208).
- [fig-5] MISLEADING — footer "Each modulo step strips non-common divisors from the outer crescents (first 3, 6, 12 leave P₁; then 8 leaves P₁)" is false for step 2 (P₂ grows to ℕ) and omits 8 moving from P₂ to P₁ → "Step 1 drops 3, 6, 12 from P₁ and moves 8 from P₂ to P₁; step 2 drops 8 from P₁ while P₂ grows to ℕ."
- [fig-5] NIT (not fixed) — step-0 header "Gcd(12, 8) = Gcd(12, 8) = {4}" is a tautology produced by the template; harmless.

**Verdict per figure:** fig-1 include-with-fix; fig-2 include-with-fix; fig-3 include-with-fix; fig-4 include-with-fix; fig-5 include-with-fix. (No MATH errors in any figure.)

**Strongest figure:** fig-1 — every one of the eight compartments is populated with correct witnesses, so the reader sees directly that only 4 survives all three conjuncts, and the side sieve repeats the narrowing on 0..12.

**Gallery copy**
- heading: Conjuncts as overlapping regions
- claim: Each conjunct of Gcd(a, b) is a region of ℕ; their triple intersection always holds exactly one number, and dropping any conjunct lets impostors in.
- encoding:
  - Solid circle → P₁: g ∣ a (the divisors of a)
  - Dashed circle → P₂: g ∣ b (the divisors of b)
  - Dotted circle → P₃: every common divisor divides g
  - Number pill in a compartment → exactly which conjuncts that value satisfies
  - Dark red region or pill → value a weakened spec wrongly admits
- per-figure captions:
  - fig-1: Gcd(12, 8): each compartment holds its own witnesses; only 4 lies in all three circles, as the 0..12 sieve confirms.
  - fig-2: Nested regions: adding a conjunct shrinks the set, so {4} ⊂ {1, 2, 4} ⊂ Div(12) ⊂ ℕ; subtyping is containment.
  - fig-3: Drop one conjunct and an impostor leaks in: 2 without P₃, 8 without P₁, 12 without P₂.
  - fig-4: The type is indexed by (a, b): coprime, large, (21, 0) and (0, 0) inputs reshape the circles, yet one value remains.
  - fig-5: Euclid's steps (12, 8) → (8, 4) → (4, 0) reshape the outer circles while the common lens {1, 2, 4} stays fixed.
- hides: Equal-sized circles hide that Div(a) is finite while P₃ and ℕ are infinite, and that P₃ is computed from P₁ ∩ P₂ rather than being an independent set.
- table row: Three overlapping circles carved out of ℕ | Wrong value sits in a red, missing-conjunct compartment | partly — circles redrawn for each (a, b) | yes — the common lens stays fixed as circles change | teaching the definition

---

### 07 — Bézout / ideal view

**Checked:** (all equations, certificates and positions recomputed in python)
- fig-1: 12ℤ ticks 12·(−1..2) = −12, 0, 12, 24 ✓; 8ℤ ticks 8·(−2..3) = −16 … 24 ✓; all points at x = 407 + 18.25·v ✓. Combined line −16 … 24 step 4 with certificates −2(8), −1(12), −1(8), −1(12)+1(8)=−4, 0, 1(12)−1(8)=4, 1(8), 1(12), 2(8), 1(12)+1(8)=20, 2(12) — all 11 ✓. Hops +12 then −8 land on 4 ✓. 12·1 + 8·(−1) = 4 ✓; 4k = 12k + 8(−k) ✓; 12 = 4·3, 8 = 4·2, 12x + 8y = 4(3x + 2y) ✓.
- fig-2: all 49 lattice nodes (x, y ∈ −3..3) labelled 12x + 8y correctly ✓; positive values purple-stroked, others gray ✓; all 13 fiber lines satisfy 12x + 8y = 4k exactly at both endpoints (k = −6..6) ✓; shaded strip is between k = 0 and k = 1 ✓; kernel (−2, 3): 12(−2) + 8(3) = 0 ✓; kernel arrow runs (1, −1) → (−1, 2) ✓; fiber k = 1 = {(1 − 2t, −1 + 3t)} ✓; all 24 certificate pairs in the right-hand list evaluate to their row value 4k ✓.
- fig-3: extended-Euclid table recomputed: (r, x, y) = (1071, 1, 0), (462, 0, 1), q=2 → (147, 1, −2), q=3 → (21, −3, 7), q=7 → (0, 22, −51) ✓; every row certificate 1071x + 462y = r ✓. 1071 − 2·462 = 147, 462 − 3·147 = 21 ✓; 147 = 7·21, 462 = 22·21, 1071 = 51·21 ✓; cascade positions on scale 0→1071 ✓; zoomed 21ℤ ticks −21 … 147 evenly spaced ✓; "20 integers strictly inside (0, 21)" ✓. Coprime case: 13·(−3) + 8·5 = −39 + 40 = 1 ✓; 13−8=5, 8−5=3, 5−3=2, 3−2=1 ✓; all 19 witness pairs under −2 … 16 satisfy 13x + 8y = n ✓.
- fig-4: positions x = 252.5 + 24.6875·v ✓. g = 4 row: lattice = 4ℤ ✓. g = 8: grid points {−8, 0, 8, 16, 24} ⊂ 8ℤ ✓; crosses at {−4, 4, 12, 20} — reachable but ∉ 8ℤ ✓; witnesses (1, 0) → 12, (1, −1) → 4 ✓. g = 2: reachable dots = multiples of 4 ✓; ghosts {−6, −2, 2, 6, 10, 14, 18, 22} ≡ 2 mod 4 ✓; 12x + 8y = 2 impossible ✓.
- fig-5: common divisors of (12, 8) = {1, 2, 4} ✓; 4ℤ ⊂ 2ℤ ⊂ ℤ ✓; d ∣ a ∧ d ∣ b ⇔ aℤ + bℤ ⊆ dℤ ✓; 21ℤ + 0ℤ = 21ℤ ✓; 0ℤ + 0ℤ = {0} ✓. Editor strip: (12, 8) → (8, 4) → (4, 0) (12 mod 8 = 4, 8 mod 4 = 0) with x/y markers at the right ticks ✓; 1(12) − 1(8) = 4 ✓.
- Palette: #8b0000 used only in fig-4 for the two wrong candidates (other figures contain only an unused red arrow-marker definition) ✓; no indigo; no green ✓.

**Findings and fixes:**
- [fig-1] LAYOUT — the key label "4" under the generator was struck through by the dashed gap-box edge and the dotted leader line → gap box height 36 → 28; leader now starts at y = 400, below the labels.
- [fig-1] MISLEADING — "Gcd(12, 8) = { g ∈ ℕ | g > 0 ∧ 12ℤ + 8ℤ = gℤ }" (subtitle and summary box): the extra "g > 0" contradicts fig-5's Gcd(0, 0) = {0} and is not needed (g ∈ ℕ with gℤ = 12ℤ + 8ℤ already gives 4) → removed "g > 0 ∧" in both places.
- [fig-1] NIT (not fixed) — tick labels "0(12)+0(8)" and "1(12)−1(8)" nearly touch; numerals use hyphen-minus "-12" while certificates use "−".
- [fig-2] NIT — SVG collapses "+24   k = +6" to "+24 k = +6", which reads as "24k" → separator added: "+24,  k = +6" (12 rows).
- [fig-3] LAYOUT — "g=21" label was struck through by the "462 − 3·(147) = 21" arrow → moved below-left to (542.3, 246).
- [fig-3] LAYOUT — the "unit step g = 1" box edges ran through the tick labels "0" and "1" → box height 40 → 30.
- [fig-3] LAYOUT — "unit step g = 1" and "3 − 2 = 1" ran together as one phrase → labels moved apart (x 164.7 → 156, 230.6 → 240).
- [fig-3] NIT (not fixed) — at the 0..1071 scale the 0 and 21 nodes overlap; the zoomed 21ℤ inset beside it compensates.
- [fig-4] MISLEADING — subtitle "Gcd(12, 8) = { g > 0 | 12ℤ + 8ℤ = gℤ }": same g > 0 issue → "{ g ∈ ℕ | 12ℤ + 8ℤ = gℤ }".
- [fig-5] MISLEADING — "y' = 1(12) − 1(8) = 4  (invariant!)": y' = 4 is a Bézout witness; the invariant is the ideal x'ℤ + y'ℤ = 4ℤ → "(Bézout witness)".
- [fig-5] NIT (not fixed) — title "Subtyping is ideal containment": section 1 shows the divisibility order mirroring ideal containment, not subtyping between refinement types.

**Verdict per figure:** fig-1 include-with-fix; fig-2 include-with-fix; fig-3 include-with-fix; fig-4 include-with-fix; fig-5 include-with-fix. (No MATH errors in any figure.)

**Strongest figure:** fig-1 — on one number line the reader sees 12ℤ and 8ℤ merge into 4ℤ, the empty gap (0, 4), and the certificate 12·1 + 8·(−1) = 4 reaching the generator.

**Gallery copy**
- heading: Gcd as ideal generator
- claim: The combinations ax + by are exactly the multiples gℤ of one number; Gcd(a, b) = {g}, the lattice step (its smallest positive point unless a = b = 0).
- encoding:
  - Purple dot on ℤ → a value ax + by reachable by some (x, y)
  - Double-ringed dot → the generator g, first positive reachable point
  - Shaded box (0, g) → the gap no combination can land in
  - Navy arc or (x, y) label → Bézout certificate reaching that value
  - Red ✕ / dashed ? → reachable point off a wrong grid / unreachable grid point
- per-figure captions:
  - fig-1: Strides 12 and 8 combine into the finer lattice 4ℤ; the witness 12·1 + 8·(−1) = 4 reaches its first positive point.
  - fig-2: Each (x, y) ∈ ℤ² certifies 12x + 8y; fibers 12x + 8y = 4k collapse onto 4ℤ, with empty strips between.
  - fig-3: Extended Euclid on (1071, 462) ends at 1071·(−3) + 462·7 = 21; coprime (13, 8) reaches every integer.
  - fig-4: Wrong candidates for Gcd(12, 8): grid 8ℤ misses reachable 4 and 12; grid 2ℤ contains unreachable ghosts 2, 6, 10, …
  - fig-5: Divisibility mirrors ideal containment: gcd generates the smallest ideal containing a and b; (21, 0), (0, 0) need no special case.
- hides: It needs signed coefficients in ℤ (one of x, y is negative) while the program works in ℕ, and it never shows the divisor sets the type is actually defined by.
- table row: Number line and 2-D lattice of ax + by | Red ✕ off a wrong grid, or unreachable ghost | partly — one lattice drawn per (a, b) pair | yes — each Euclid step keeps the same ideal | teaching the definition; debugging a program

---

### 08 — Dependent type family / fibers

**Checked:**
- fig-1: all 289 base-plane cells (a, b ∈ 0..16) parsed from rect/text coordinates; every printed value equals gcd(a, b) ✓ (0 mismatches). The 21 cells with gcd = 4 are exactly the ones with the purple outline (plus the navy-selected (12, 8)) ✓. Crosshair at a = 12 (x = 318.2) and b = 8 (y = 320.8) on the right cell ✓. Fiber spine: Div(12) = {1,2,3,4,6,12}, Div(8) = {1,2,4,8}, ∩ = {1,2,4} ✓; every row g = 0..12 checked (Div(1) = {1} misses 2,4; Div(2) misses 4; Div(3) "3 ∣ 12 but 3 ∤ 8"; Div(6) = {1,2,3,6}; Div(8) "extra 8 ∤ 12"; Div(12) "extra 3,6,12 ∤ 8"; Div(0) = ℕ) ✓; g = 4 is the only match ✓. Caption cells (4,4), (4,8), (8,12), (12,8), (12,16) all have gcd 4 ✓; (0,0) shows 0 ✓. Tints: gcd 1 → #f7f6ee, 2 → #ece9f8, {0,3,5} → #e2def4, 4 → #d2ccf0, ≥ 6 → #c2b9ea (bucketed, see findings).
- fig-2: a = 0..24, b = 8: each fiber dot sits at g = gcd(a, 8) (25/25 ✓); bottom row {8},{1},{2},{1},{4},… = gcd(a, 8) (25/25 ✓); divisibility rows 8∣a, 4∣a, 2∣a, 1∣a correct in all 100 cells ✓, darkest cell in each column = gcd ✓. Period 8 ✓ (brackets at a = 0, 8, 16, 24). Gcd(0, 8) = {8} via Div(0) = ℕ ✓; Gcd(12, 8) = {4} ✓; Gcd(13, 8) = {1}, Div(13) ∩ Div(8) = {1} ✓; "g ∉ {1,2,4,8} never inhabited (g ∤ 8)" ✓ (0 ∤ 8 under the definition).
- fig-3: background dots for a = 0..16 (a ≠ 12) at g = gcd(a, 8) ✓. g = 12: inhabits Gcd(12, 0), Gcd(12, 12) ✓, 12 ∤ 8, extras {3, 6, 12} ✓. g = 8: inhabits Gcd(8, 8), Gcd(16, 8) ✓, 8 ∤ 12 ✓. g = 2: inhabits Gcd(2, 8), Gcd(6, 8) ✓; "4 ∣ 12 ∧ 4 ∣ 8 but 4 ∤ 2" ✓. g = 4: Div(4) = {1,2,4} ✓. Div-box chips (extra!/missed!) match each set ✓. "return b (= 8) lands in Gcd(8, 8)" ✓.
- fig-4: all 484 cells (x, y ∈ 0..21) parsed: the 21 gcd-4 cells are exactly the labelled/tinted "4" cells ✓; gcd-1 cells all share the lightest tint ✓; trajectory cells labelled with correct gcd ✓. Run A path endpoints decode to (12,8) → (8,4) → (4,0) ✓. Run B path decodes to (21,13) → (13,8) → (8,5) → (5,3) → (3,2) → (2,1) → (1,0) ✓ = Euclid trace, 6 steps, 7 points ✓. Div(21) ∩ Div(13) = {1,3,7,21} ∩ {1,13} = {1} ✓. Div(4) ∩ ℕ = {1,2,4} ✓. Gcd(0,0) = {0} argument (Div(0) = ℕ; only g = 0 has Div(g) = ℕ) ✓.
- fig-5: (12, 8) loop exits at iteration 2 with (4, 0) ✓; (21, 0) halts at iteration 0 ✓; number lines (0..12 step 28 px; 0..21 step 16 px) put 4 and 21 at the right x ✓; return y = 0 ∉ {4}, {21} ✓; Div(x) ∩ ℕ = Div(x) at y = 0 ✓.
- Palette: no green; #8b0000 used only on violations (✕, extra!/missed!, buggy return); #4b0082 only for the symbolic unknown g* (fig-5) ✓.

**Findings and fixes:**
- [fig-1] MISLEADING — "Purple cells (4,4), (4,8), (8,12), (12,8), (12,16)... all carry fiber {4}": most purple cells carry other values (6, 8, 12, 16 …); the {4} cells are the outlined ones → changed "Purple cells" to "Outlined cells".
- [fig-1] NIT — "Each cell (a, b) is shaded by the inhabitant of its fiber": tints are bucketed (gcd 0, 3 and 5 share one tint; every gcd ≥ 6 shares one). The printed numbers carry the exact value → not fixed (would need restyle).
- [fig-1] LAYOUT — the dashed crosshair strikes through the numbers in row b = 8 and column a = 12, and the "type index" callout covers cells (15, 8), (16, 8), (15, 9), (16, 9) → not fixed (no free space beside the grid; values recoverable from symmetry).
- [fig-2] MISLEADING — "(each vertical line is one fiber ⊂ ℕ)": the line is the ambient ℕ; the fiber Gcd(a, 8) is the ringed singleton on it (as everywhere else in the angle) → "(each vertical line is ℕ; its ring is the fiber)".
- [fig-2] NIT — title "slices the family into a periodic section": the slice is a family; the dashed curve is the section → not fixed.
- [fig-3] MISLEADING — the purple column labelled "Fiber Gcd(12, 8)" spans every candidate, including the ✕ values 2, 8, 12, so it reads as if they were in the fiber → label changed to "ℕ over (12, 8)".
- [fig-3] NIT — subtitle names only g = 2 and g = 8 while the figure also rejects g = 12 → not fixed.
- [fig-4] MISLEADING — subtitle "with the exact same fiber Div(x) ∩ Div(y)" calls the common-divisor set the fiber → "keeps Div(x) ∩ Div(y), so the fiber Gcd(x, y) never changes".
- [fig-4] LAYOUT — "Run B (coprime): (21,13) → {1}" overflowed its label box (closing brace on the border) → box widened (x 284.2→276.2, width 154→170).
- [fig-4] NIT — "Theorem: Div(x) ∩ Div(y) = Div(y) ∩ Div(x mod y)" omits the y ≠ 0 precondition; heading "Level Sets of Equal Fiber" but only the {4} and {1} level sets are distinguished → not fixed (space; would need restyle).
- [fig-5] NIT — "TYPE ERROR: {0} ≠ Gcd(a, b) for a∨b > 0" is ill-formed → "for (a, b) ≠ (0, 0)".
- [fig-5] LAYOUT — footer "Runtime evidence is erased: only the plain integer 4 (or 21) flows on the Wasm stack." ran past both edges of the right panel → "Proof erased at run time: only 4 (or 21) is on the Wasm stack."

**Verdict per figure:**
- fig-1: include-with-fix
- fig-2: include-with-fix
- fig-3: include-with-fix
- fig-4: include-with-fix
- fig-5: include-with-fix

**Strongest figure:** fig-2 — you watch the singleton fiber jump among {8}, {1}, {2}, {4} as a slides with b fixed, which shows exactly what "a family of sets indexed by values" means.

**Gallery copy**
- heading: A family of singleton fibers
- claim: Gcd(a, b) is not one set but a family indexed by the inputs: over each (a, b) sits the singleton {gcd(a, b)}, and results must land in their own fiber.
- encoding:
  - grid cell (a, b) → one index of the family, labelled gcd(a, b)
  - vertical line over an input → the ambient return type ℕ
  - purple ring on that line → the fiber Gcd(a, b), a one-element set
  - navy dot → a concrete returned value
  - dark-red ✕ → a value sitting in another input's fiber
- per-figure captions:
  - fig-1: Base plane labelled by gcd; the fiber over (12, 8) keeps only g = 4, since Div(4) = {1, 2, 4}.
  - fig-2: Fix b = 8 and slide a: the singleton jumps among {1}, {2}, {4}, {8} with period 8, including Gcd(0, 8) = {8}.
  - fig-3: Over (12, 8), returning 8, 2 or 12 is a type error: each value inhabits some other input's fiber.
  - fig-4: Euclid's steps (12,8)→(8,4)→(4,0) and (21,13)→…→(1,0) stay on one level set until y = 0, where Gcd(x, 0) = {x}.
  - fig-5: An editor gutter tracks the fiber per instruction: return x lands in Gcd(a, b); return y = 0 does not.
- hides: Every fiber is a singleton, so "fiber" and "value" blur, the base-plane tints lump many gcds together, and the divisor sets that explain membership live in side panels, not in the plane.
- table row: (a, b) plane with a singleton over each point | result dot sitting in a neighbouring input's fiber | yes — the fiber visibly moves as a varies | partly — Euclid's path stays on one level set | teaching the definition

---

### 09 — Typing derivation as composed pictures

**Checked:**
- fig-1: Div(12) dots at 1,2,3,4,6,12 ✓, Div(8) at 1,2,4,8 ✓, intersection 1,2,4 ✓ (x = 169 + 22(n−1)). Candidate rows: Div(1) = {1} missing 2, 4 ✓; Div(2) missing 4 ✓; Div(3) 3 ∉ {1,2,4} ✓; Div(4) = {1,2,4} exact match ✓; Div(6) = {1,2,3,6} ✓; Div(8) extra 8 (8 ∤ 12) ✓; Div(12) extras 3, 6, 12 ✓. Number line 0..12 places g = 4 at x = 291.3 ✓. Grammar panels (pre/post sets, ⊆ dock, ⊈ leak) consistent.
- fig-2: Inv = {(x, y) ∈ [0..12]×[0..8] | gcd(x, y) = 4} = {(4,0), (0,4), (4,4), (8,4), (12,4), (4,8), (12,8)}, 7 states ✓; input port marks exactly the 6 with y > 0 ✓; output port marks all 7 ✓; text "y > 0 … → 6 states", "y = 0 : (4, 0) ONLY" ✓. Image of the body on Inv ∧ y ≠ 0 = {(4,0), (8,4)} ⊆ Inv ✓. Run arrows decode to (12,8) → (8,4) → (4,0) ✓. Measure bars 50 : 25 : 0 px for y = 8, 4, 0 ✓. "d ∣ x ∧ d ∣ y ⟺ d ∣ y ∧ d ∣ (x mod y)" ✓; Inv(x, 0) ⟺ Div(x) = {1,2,4} ⟺ x = 4 ✓.
- fig-3: Tile 1 marks only (12, 8) ✓; Tile 2 marks exactly the 7 Inv states above ✓ and the run (12,8) → (8,4) → (4,0) ✓; Tile 3 marks only (4, 0) on the y = 0 row ✓; Tile 4 highlights g = 4 among 1..12 ✓. Docks: E ⊆ Inv, ¬(y ≠ 0) slice, proj x ✓. Composed rule premises and conclusion Gcd(12, 8) = {4} ✓.
- fig-4: each mini-grid parsed cell by cell against {(x, y) | gcd(x, y) = gcd(a, b)} on its window: Case A (13, 8), window 0..13 × 0..8, 126 cells, marked set = gcd-1 set exactly ✓; Case B (21, 0), window 0..21 × 0..7, 176 cells, marked = {(21, 0)} = truth on window ✓; Case C (0, 0), window 0..8 × 0..6, 63 cells, marked = {(0, 0)} ✓. Case A run arrows decode to (13,8) → (8,5) → (5,3) → (3,2) → (2,1) → (1,0) = Euclid trace, 5 iterations ✓. Div(13) ∩ Div(8) = {1} ✓; Div(21) ∩ ℕ = {1,3,7,21} ✓; Inv(0, 0) = {(0, 0)} ✓; exit slices {(1,0)}, {(21,0)}, {(0,0)} ✓.
- fig-5: Bug 1 `while (y > 4)` on (12, 8): (12,8) → (8,4), stops, returns 8 ✓; 8 ∤ 12 ✓; {x | ∃y ≤ 4. gcd(x, y) = 4} = all multiples of 4 (see findings). Bug 2 body (x, y) ← (y div 2, x mod y): actual run (12,8) → (4,4) → (2,0), returns 2 ✓; (8,4) ↦ (2,0) and (4,4) ↦ (2,0) both true; Div(2) ∩ Div(0) = {1,2} ≠ {1,2,4} ✓; mini-grid marks exactly the 7 Inv states ✓, red ring at (2, 0) ✓. Bug 3 return y at (4, 0) gives 0; 0 ∤ 12, 0 ∤ 8 ✓.
- Palette: no green; #8b0000 (and its tint #f9e2e2) only on broken docks, leaks and witnesses; #4b0082 appears only in an unused marker definition ✓.

**Findings and fixes:**
- [fig-2] LAYOUT — "∴ Div(x') ∩ Div(y') = Div(x) ∩ Div(y) = {1,2,4}" overflows its 224-px box on both sides → dropped the trailing "= {1,2,4}" (already stated in the header).
- [fig-3] NIT — circled step numbers ①–④ depend on a fallback font (in rsvg they render as boxed digits) → not fixed (still legible).
- [fig-4] MISLEADING — "Loop Invariant Set Inv(21, 0)" drawn on a 0..21 × 0..7 window shows a single point, so it reads as though Inv(21, 0) = {(21, 0)}; it also contains (0, 21), (21, 21), (42, 21), … → title now "Inv(21, 0), y ≤ 7 shown".
- [fig-4] NIT — mini-grids have no axis ticks, so the window ranges cannot be read off → not fixed.
- [fig-5] MATH — "Set leak: {x | Inv(x,y) ∧ y≤4} = {0, 4, 8, 12} ⊈ {4}": the set is every multiple of 4 (infinite), not just the four values in the window → "{0, 4, 8, 12, …}".
- [fig-5] MISLEADING — "where y ≠ 0 so Div(x) ≠ Div(x)∩Div(y)" is stated as a general rule but is false for e.g. (4, 8) → "at (8, 4): Div(8) ≠ Div(8) ∩ Div(4)".
- [fig-5] MATH — Bug 2's navy arrow (12, 8) → (8, 4) is the correct Euclid step, not the buggy body, which sends (12, 8) to (4, 4). The leak witness "(8, 4) ↦ (2, 0)" is not on the buggy run → witness moved to the real run: "Input state: (x = 4, y = 4)", "Div(4) ∩ Div(4) = {1, 2, 4}", "Buggy step maps (4, 4) ↦ (2, 0)", navy arrow now ends at (4, 4), red arrow starts there, navy ring moved to (4, 4).
- [fig-5] MATH — "Div(0) = ℕ = {1, 2, 3, 4, 5, …}" omits 0, but 0 ∣ 0 under the page's definition (and Gcd(0, 0) = {0} depends on it) → "{0, 1, 2, 3, 4, …}".
- [fig-1] No errors found (NIT: the candidate list skips g = 0, the "too large" case Div(0) = ℕ).

**Verdict per figure:**
- fig-1: include
- fig-2: include-with-fix
- fig-3: include
- fig-4: include-with-fix
- fig-5: include-with-fix

**Strongest figure:** fig-3 — the whole proof fits in one row: the entry, loop, exit-slice and return tiles visibly dock through ⊆ joints, ending at Gcd(12, 8) = {4}.

**Gallery copy**
- heading: Proof as docked tiles
- claim: Typing Euclid as Gcd(a, b) is a chain of set-to-set judgments joined by containments; the loop invariant makes every dock fit, ending in the singleton {gcd}.
- encoding:
  - tile → one typing judgment: pre-state set in, post-state set out
  - purple dots on the (x, y) grid → states satisfying the invariant
  - purple ⊆ pill between tiles → output set fits inside the next input set
  - navy arrows → one concrete run inside the invariant set
  - dark-red ⊈ dock with ringed point → failing joint and its counterexample state
- per-figure captions:
  - fig-1: Gcd(12, 8) filters ℕ down to {4}; a judgment is a set-to-set tile, and tiles compose when output ⊆ next input.
  - fig-2: The loop rule: the step maps every Inv state with y ≠ 0 back into Inv while y drops 8 > 4 > 0.
  - fig-3: Four tiles (entry, loop, exit slice y = 0, return) dock to prove Euclid(12, 8) : Gcd(12, 8) = {4}.
  - fig-4: Same skeleton for (13, 8), (21, 0) and (0, 0): only the purple invariant set changes, giving {1}, {21}, {0}.
  - fig-5: Three bugs, three broken docks: early exit returns 8, a corrupt body leaks (2, 0), return y gives 0.
- hides: Each picture checks one input pair on a finite window, so the premise "for every state in Inv" looks like inspecting a few dots, and the measure argument is shown, not proved.
- table row: chain of docked set-to-set judgment tiles | dark-red ⊈ dock with a leaking witness state | partly — same skeleton, invariant reshaped per (a, b) | yes — invariant kept, y drops, exit slice ⊆ target | debugging a program; inside the editor

---

### 10 — Codillon's editor idiom (stack-effect fractions, refined i32 number lines, result socket)

**Checked:**
- Number-line mapping (all figs): gen.py's hybrid scale matches the brief (|v| ≤ 8 linear over the middle 60%, log to INT_MIN/INT_MAX over 20% each side). Every navy bead, notch and socket was located in the SVG and mapped back to a value. All are correct: 1→0.5375, 2→0.575, 4→0.65, 8→0.800, 12→0.804, 21→0.810, 462→0.842, 1071→0.851 of width. Spill blobs sit at 0 (fig-1), and at 2, 8 and 12 (fig-4).
- fig-1: Div(12)={1,2,3,4,6,12} ✓, Div(8)={1,2,4,8} ✓, notches at exactly those values ✓. Unique g with Div(g)={1,2,4} is 4 ✓. Panel A `i32.rem_u` has a=12 in the left (deeper) cup and b=8 in the right (top) cup → 12 rem 8 = 4 ✓, the correct WebAssembly operand order. Panel B: x=12 ∈ [0,MAX], y=8 ∈ [1,MAX], result 4 ∈ [0, y−1]=[0,7] ✓. Panel C: 0 ∉ [1,MAX] spills ✓.
- fig-2: the figure's loop body (`local.get $y; i32.eqz; br_if; local.get $y; local.get $x; local.get $y; i32.rem_u; local.set $y; local.set $x`) was simulated for (12,8):
  - iter 1: y=8, eqz=0, branch not taken; stack [8,12,8]; rem_u pops 8 then 12 → 12 mod 8 = 4; set y=4, then x=8.
  - iter 2: y=4, eqz=0; rem_u 8 mod 4 = 0; set y=0, x=4.
  - iter 3: y=0, eqz=1, branch taken; exit `local.get $x` = 4 ✓.
  - Every gutter value matches iteration 1: 8 / eqz 0 / br_if consumes 0 / 8 / 12 / 8 / rem_u cups 12 (left) and 8 (right) → 4 / local.set cups 8 and 4 / exit 4 / return 4 ✓.
  - eqz output region [0,1] ✓; post-br_if y region [1,MAX] ✓; rem_u output [0,7] ✓.
  - Right panel: (12,8)→(8,4)→(4,0) ✓. CD = {1,2,4} at each step ✓. Div(4)∩ℕ = Div(4) ✓.
- fig-3: the loop was simulated for every pair.
  - (1071,462): 1071 mod 462=147, 462 mod 147=21, 147 mod 21=0 ✓; 3 remainder steps ✓. Div(1071)={1,3,7,9,17,21,51,63,119,153,357,1071} and Div(462)={1,2,3,6,7,11,14,21,22,33,42,66,77,154,231,462}; all 12 + 16 notches are placed correctly. ∩ = {1,3,7,21} = Div(21) ✓.
  - (13,8): 5 iterations, remainders 5,3,2,1,0 → 1 ✓. Div(13)∩Div(8)={1} ✓.
  - (21,0) and (0,0): exit at the first check → 21 and 0 ✓. Div(g)=ℕ forces g=0 ✓.
- fig-4: Div(12)∩Div(8)={1,2,4} ✓; only g=4 satisfies g|12 ∧ g|8 ∧ 4|g ✓.
  - g=2: 4∤2, and Div(2)={1,2} ⊊ {1,2,4} ✓.
  - g=8: 8∤12 (12 mod 8 = 4) ✓, and {1,2,4,8} ⊋ {1,2,4} ✓.
  - g=12: 12∤8 ✓, extra divisors {3,6,12} ✓.
  - The buggy test `local.get $x br_if $exit` exits at once with 12 ✓.
- fig-5: {4} ⊆ {1,2,4} ⊆ Div(12) ⊆ [0,MAX] ⊆ i32 ✓. The runtime fraction (cups 12 and 8, output 4) matches gcd(12,8)=4 ✓.
- Palette: no green anywhere. #8b0000 is used only for spills and error columns (plus the defs) ✓. Indigo #4b0082 is used for tethers and labels, which is a violation.

**Findings and fixes:**
- [all] PALETTE — indigo #4b0082 is used for tethers, the tether pill ("Dependent socket tethered to $a and $b") and the "⟹ socket = 4" lines. These are type marks, not "unknown" → recoloured to purple #6A5ACD.
- [fig-1] NIT — "Any 32-bit int fits; 0 divisor undetected". In WebAssembly, `i32.rem_u` by 0 traps → "Any i32 fits; a 0 divisor traps only at run time".
- [fig-1,2,3,4,5] MISLEADING — result cups draw thin lavender notches at the other common divisors (1, 2; or 1, 3, 7) next to the singleton socket, in the same fill as "admitted region". In fig-4, "Spill g=2!" lands on a purple notch at 2. Not fixed (it is an encoding choice); the caption must say the bold socket is the only inhabitant.
- [fig-1,2,4] MISLEADING — on the log wing, 8 and 12 sit at 0.800 vs 0.804 of the width (≈0.35 px apart on an 84 px shape). x=12 and y=8 beads look identical, and so do the g=8 and g=12 spills. Not fixable without changing the scale; the text labels disambiguate.
- [fig-2] MISLEADING — the listing is not a valid or complete WAT program. This is the most serious remaining issue.
  - It has no `block $exit`, so `br_if $exit` targets an undefined label.
  - It never initialises the locals (`local.get $a / local.set $x / local.get $b / local.set $y`). Locals start at 0, so the listing as written returns 0.
  - It has no `br $step` or `end` lines; `br $step` appears only in a note, and without it the loop body runs once.
  - "local.set $y $x" puts two instructions on one row, which breaks the one-instruction-per-line idiom. The research program also uses `$t`, which this listing omits.
  - Header "WAT INSTRUCTION" → "WAT (ABRIDGED)". The rest is not fixable without re-layout; the caption must say "abridged".
- [fig-2] MISLEADING — stack columns are inconsistent. The `local.get $x` output is drawn in the right column, and its ribbon crosses to rem_u's left cup. The saved-y=8 ribbon runs down the left column behind rem_u's left cup, which holds 12, so it can read as 8 being the dividend. The operand order is still correct: x is deeper/left and y is top/right. Not fixed (layout).
- [fig-2] LAYOUT — the colon of "Common Div:" is hidden under the bar that starts at x=664 (×3) → "Common:".
- [fig-2] MISLEADING — the exit-step y=0 shape (Div(0)=ℕ) is shaded across all of i32, including negatives → shading clipped to [0, INT_MAX].
- [fig-2] NIT — the gutter shows iteration-1 values and the exit value (x=4) together with no visual marker. Not fixed.
- [fig-3] MATH — "Div(462)={1,2,3,7,..,462}" skips the divisor 6 → "{1,2,3,6,..,462}".
- [fig-3] MATH — "C. Zero Absorber". 0 is the identity for gcd (gcd(21,0)=21); the absorbing element is 1 → "C. Zero Is the Identity".
- [fig-3] MISLEADING — the coprime trace stops at "3 mod 2 = 1", but the loop needs 2 mod 1 = 0 to exit → "13 mod 8=5 → 8 mod 5=3 → 5 mod 3=2 → 3 mod 2=1 → 2 mod 1=0".
- [fig-3] MISLEADING — the g=21 socket is 3.4 px right of the +8 hairline, with "+8" printed directly under it, so it reads as g = 8. Fix (panels A and C): "+8" moved left and a navy "21" label added under the socket.
- [fig-3] MATH — panel D draws the result cup Gcd(0,0) shaded across all of i32, but the type is {0} → shading removed, so only the socket at 0 remains. The Div(0) parameters ($b=0 in C; $a and $b in D) were shaded including negatives → clipped to [0, INT_MAX].
- [fig-4] MISLEADING — "i32.const 2 ;; return", "local.get $b ;; return", "local.get $x ;; br_if $exit". In WAT, `;;` starts a comment, so the second instruction is commented out → separated by spaces ("i32.const 2  return" etc.), which is valid flat WAT.
- [fig-4] NIT — "Error 3: Buggy Loop Exit (br_if $x)". `br_if` takes a label, not a local → "Error 3: Exit Tests $x, Not $y".
- [fig-5] MISLEADING — CommonDiv(12,8) and Div(12) are drawn as shaded intervals [1,4] and [1,12]. The shading admits 3 (and 5, 7–11) → interval shading removed; the divisor notches remain.
- [fig-5] NIT — the "⊆" glyphs sit horizontally between vertically stacked levels. A rotated glyph renders like "∩", so they were left as is. The caption "84×14 number-line cup" sits under a 190×20 close-up. Not fixed.

**Verdict per figure:**
- fig-1: include-with-fix
- fig-2: include-with-fix. The caption must say the listing is abridged (no init, no block/br/end; last row is local.set $y; local.set $x).
- fig-3: include-with-fix
- fig-4: include-with-fix
- fig-5: include-with-fix

**Strongest figure:** fig-4. It shows the singleton socket, three wrong returns spilling over the rim, and the divisor-set reason for each, all in the editor's own vocabulary and with every number correct.

**Gallery copy**
- heading: The type as a socket
- claim: Inside Codillon's stack fractions, Gcd(a, b) is a one-slot socket on the result's i32 number line, tethered to a and b; the right return seats, anything else spills.
- encoding:
  - cup above the rule / box below → value consumed / value produced by the instruction
  - wide number line → refined i32 (linear for |v| ≤ 8, log toward INT_MIN/INT_MAX)
  - shaded band → values the refinement admits
  - bold socket tethered to a, b → Gcd(a, b), its single admitted value
  - dark-red hatch over the rim → value outside its type: a type error
- per-figure captions:
  - fig-1: Plain 30×11 i32 boxes widen into number lines; values seat in shaded regions, 0 spills from a divisor cup, Gcd(12, 8) is one socket.
  - fig-2: Abridged Euclid listing with refined fractions for (12, 8): 12 rem_u 8 = 4, common divisors stay {1, 2, 4}, and 4 seats.
  - fig-3: Change the inputs and the tethered socket moves: 21 for (1071, 462), 1 for (13, 8), 21 for (21, 0), 0 for (0, 0).
  - fig-4: Returning 2, 8 or 12 instead of 4 misses the socket and spills; each miss traces to a divisor set that differs from {1, 2, 4}.
  - fig-5: {4} fits every wider type down to plain i32, and at run time the sockets and tethers erase to a plain 12, 8 → 4.
- hides: The log wing crushes 8, 12, 21, 462 and 1071 into a few pixels, the thin notches beside the socket look admitted but are not, and the listing is abridged.
- table row: one-slot socket on result's number line | value spills over the cup rim in dark red | yes, tethers from a, b move the socket | partly, invariant {1,2,4} is annotated, not drawn | inside the editor; debugging a program
