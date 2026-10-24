# Angle 06: Refinement as Intersection of Predicates (Euler/Venn)

## Angle in One Sentence
A refinement type `{ g ∈ ℕ | P₁(g) ∧ P₂(g) ∧ P₃(g) }` is the geometric intersection of three predicate regions carved out of the base universe `ℕ`, where each added conjunct shrinks the set until `Gcd(a, b)` collapses to the singleton `{gcd(a, b)}`.

## Visual Encoding (Mark → Meaning)
- **Outer rectangular frame (`#f5f5eb` fill, gray border):** The unrefined base type universe `g ∈ ℕ = {0, 1, 2, …}`.
- **Three purple Euler circles (`#6A5ACD` / `#43368a` strokes, `#efedf9` / `#c3bceb` / `#d9d5f2` fills):** The three conjunct predicates defining `Gcd(a, b)`:
  - Solid circle `P₁(g): g ∣ a` (`Div(a)`);
  - Dashed circle `P₂(g): g ∣ b` (`Div(b)`);
  - Dotted circle `P₃(g): ∀d ∈ Div(a) ∩ Div(b). d ∣ g` (“greatest” in divisibility order—multiples of all common divisors).
- **Deepest purple central lens (`#d9d5f2` fill, heavy border):** The triple intersection `P₁ ∩ P₂ ∩ P₃ = Gcd(a, b)`.
- **Numbered circular pills:** Concrete natural numbers `g ∈ ℕ` placed in their exact boolean compartment (`000`..`111`, computed in Python).
- **Navy double-bordered pill (`#00008b` on `#e6eaf5`):** The unique inhabitant `g = gcd(a, b)` inside the triple intersection.
- **Dark red region & pills (`#8b0000` on `#fae6e6` / `#e3bcbc`):** A type error or specification leak—values admitted by a weakened specification (missing a conjunct) or candidate outputs landing outside a required circle.

## Per-Figure Claims (Prose-Off Test)
- **`fig-1.svg`:** Starting from `ℕ`, intersecting `P₁: g ∣ 12` (`{1,2,3,4,6,12}`), `P₂: g ∣ 8` (`{1,2,4,8}`), and `P₃: ∀d ∈ {1,2,4}. d ∣ g` (`{0,4,8,12,…}`) carves the universe down to the single inhabitant `Gcd(12, 8) = {4}`.
- **`fig-2.svg`:** Adding conjuncts creates nested subsets `Gcd(12, 8) = {4} ⊂ CommonDiv(12, 8) = {1,2,4} ⊂ Div(12) = {1,2,3,4,6,12} ⊂ ℕ`, making subtyping (`<:`) visually identical to set containment (`⊆`).
- **`fig-3.svg`:** Dropping any conjunct lets impostor values leak into the type (`1, 2` without `P₃`; `8` without `P₁`; `12` without `P₂`), and any candidate `g ≠ 4` fails type checking by falling outside at least one boundary.
- **`fig-4.svg`:** Because `Gcd(a, b)` is a dependent type indexed by `(a, b)`, varying inputs (`(13, 8)`, `(1071, 462)`, `(21, 0)`, `(0, 0)`) reshapes or expands individual circles (with `Div(0) = ℕ` filling the universe box), yet their triple intersection always has cardinality 1.
- **`fig-5.svg`:** Each step of Euclid’s loop `(12, 8) → (8, 4) → (4, 0)` expels non-common divisors from the outer crescents while locking `Div(x) ∩ Div(y) = {1, 2, 4}`, until `y = 0` expands `P₂` to `ℕ` so `x = 4` automatically inhabits `Gcd(12, 8)`.

## What This Angle Makes Obvious
1. **Conjunction is intersection; subtyping is containment:** Students immediately see why `{v : T | P ∧ Q} <: {v : T | P}`—intersecting another circle can only shrink the set of inhabitants.
2. **Why every specification clause is needed:** Each Venn compartment (`110`, `101`, `011`, `001`) holds a concrete impostor (`1, 2`, `12`, `8`, `0`) that leaks in when a conjunct is dropped.
3. **Why `0` belongs in `P₃` and `Gcd(0, 0) = {0}` requires no special case:** Using divisibility (`∀d. d ∣ g`) rather than `≤` places `0` inside `P₃` (`4 ∣ 0`), blocked by `P₁, P₂` when `a, b > 0` but surviving alone when `a = b = 0`.

## Weaknesses and Where It Misleads
- **Infinite sets look finite:** Both `ℕ` and `P₃ = {0, 4, 8, 12, …}` are infinite while `Div(12)` and `Div(8)` are finite; a bounded circle for `P₃` relies on ellipsis pills (`16, 20, …`) to avoid implying finiteness.
- **Dependency of `P₃` on `P₁ ∩ P₂`:** Unlike independent Venn sets, `P₃` quantifies over `d ∈ P₁ ∩ P₂`; the diagram shows `P₃`’s resulting extension rather than how `P₁ ∩ P₂` generates `P₃`.

## Living Inside Codillon's Per-Instruction Display
In Codillon’s editor, each instruction can show a compact **3-lens Euler badge** in the type gutter. Proven conjuncts fill in purple; violated conjuncts glow dark red (`#8b0000`) with a concrete counterexample witness from that compartment (e.g., `g = 2` in `110`). Stepping through a loop animates outer crescents shedding elements while the central intersection stays locked.
