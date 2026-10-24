# Prime-Exponent Space: Visualizing `Gcd(a, b)` as a Refinement Type

## Our Angle in One Sentence
Mapping each integer `n` to its prime-exponent vector `(e₂, e₃, …)` turns divisibility `d | n` into coordinatewise inequality `e(d) ≤ e(n)`, each divisor set `Div(n)` into an origin-anchored box, common divisors `Div(a) ∩ Div(b)` into box intersection, and the refinement type `Gcd(a, b) = { g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }` into the unique top-right corner of that intersection box.

## Visual Encoding (Mark → Meaning)
- **Grid Coordinates `(e₂, e₃, …)`:** Prime exponents (`2^e₂ · 3^e₃ …`). Moving right multiplies by 2; moving up multiplies by 3.
- **Origin-Anchored Navy Boxes (dashed for `a`, dotted for `b`):** Divisor sets `Div(a)` and `Div(b)` spanning `[0, e₂] × [0, e₃]`; every point inside divides the box's corner.
- **Filled Purple Box (`#d9d5f2` fill, `#6A5ACD` border):** The common-divisor set `Div(a) ∩ Div(b)` spanning `[0, min(e_p(a), e_p(b))]`, which any inhabitant `g` must generate as `Div(g)`.
- **Double-Ringed Purple Corner Node:** The sole value `g` whose divisor box equals the purple intersection—showing why `Gcd(a, b)` is a singleton `{g}`.
- **Dark Red Box and Hatched Regions (`#8b0000`):** Type errors where a wrong candidate `g'` generates a box `Div(g')` that under-fills the purple target (missing a common divisor) or overflows it (failing to divide `a` or `b`).
- **Unbounded Hashed Quadrant `(∞, ∞)`:** The divisor set `Div(0) = ℕ`, since every integer divides 0.

## Per-Figure Claims ("Prose-Off" Test)
- **`fig-1.svg` (`a=12, b=8 → 4`):** `Div(12)` is the `3×2` box below `(2,1)` and `Div(8)` is the `4×1` box below `(3,0)`; their purple intersection `[0,2]×[0,0]` has the unique top-right corner `g = 4 = 2²·3⁰`, the sole inhabitant of `Gcd(12, 8)`.
- **`fig-2.svg` (Dependent Regimes: `(72,48)`, `(13,8)`, `(24,0)`):** Indexing `Gcd(a, b)` by different inputs reshapes the intersection box: interior overlap yields corner `24 = 2³·3¹` for `(72,48)`, orthogonal prime axes collapse the box to the origin `1 = 2⁰·13⁰` for coprime `(13,8)`, and intersecting with the unbounded quadrant `Div(0) = ℕ` leaves `Div(24)` unchanged so `Gcd(24,0) = {24}`.
- **`fig-3.svg` (Type Errors on `(12,8)`):** Every candidate other than `g = 4` mismatches the target box `[0,2]×[0,0]`: `g = 2` leaves an uncovered red cell at `d = 4` (`4 ∤ 2`), `g = 12` overflows upward into `e₃ = 1` (`{3,6,12} ∤ 8`), and `g = 8` overflows rightward to `e₂ = 3` (`8 ∤ 12`).
- **`fig-4.svg` (Euclid's Invariant on `(72,48) → (48,24) → (24,0)`):** Each step `(x,y) ↦ (y, x mod y)` shifts the outer navy boxes while locking their purple intersection `[0,3]×[0,1]`, until `y = 0` makes `Div(y) = ℕ` and `x = 24` sits at the purple corner.
- **`fig-5.svg` (Beyond 2D via Small Multiples on `(1071,462) → 21`):** Across primes `p ∈ {2,3,7,11,17}`, the 5-D divisor hyperbox factors into independent 1-D intervals `[0, min(e_p(a), e_p(b))]`, projecting onto the active slice `3¹·7¹ = 21`.

## What This Angle Makes Obvious (and Where It Misleads)
Prime-exponent space makes **singleton uniqueness** and **set containment** visually immediate: because every origin-anchored box has *one* top-right corner, the equivalence between `Div(g) = Div(a) ∩ Div(b)` and `g = gcd(a, b)` is an instant geometric fact. Violating any clause of the refinement predicate (`g ∤ a`, `g ∤ b`, or `∃d. d|a ∧ d|b ∧ d∤g`) produces a distinct spatial error: overflowing Box `a`, overflowing Box `b`, or under-filling their intersection.

Its main weakness is **additive opacity**: while multiplication and divisibility become clean box geometry, addition and modulo (`x mod y`) jump nonlinearly across prime axes and can introduce fresh primes. Readers must not assume Euclid's algorithm factors numbers at runtime; prime exponents explain *what the refinement type means*, whereas Euclid's loop preserves the intersection box without factoring. Representing `0` also requires an explicit unbounded-quadrant convention.

## Living Inside Codillon's Per-Instruction Editor Display
In Codillon's inspector, this angle lives as the **Prime-Exponent Barcode Widget** (`fig-5.svg`): for concrete runs or counterexamples, Codillon renders compact 1-D min-bars per active prime alongside a 2-D slice of the top two shared primes. Stepping through Euclid's loop shrinks outer navy bars while locking purple intersection bars, and any buggy return highlights the mismatched prime bar in dark red with witness `d`.
