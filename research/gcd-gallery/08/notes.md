# Dependent Type Family: Visualizing `Gcd(a, b)` as a Fiber Bundle

## Angle in One Sentence
A dependent refinement type `Gcd(a, b) = { g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }` is an indexed family of subsets of `ℕ` over the base plane `(a, b) ∈ ℕ × ℕ` whose fiber over each input pair is `{gcd(a, b)}`, and a well-typed function must land in the fiber over its own inputs.

## Visual Encoding (Mark → Meaning)
- **Base-space grid cell `(a, b)`:** An input pair indexing the type family, shaded in purple tones by the inhabitant of its fiber `Gcd(a, b)`.
- **Vertical spine with open gray circles (`g ∈ ℕ`):** The ambient return type `ℕ` pulled out above a base point `(a, b)`.
- **Purple pill/ring (`#6A5ACD` stroke, `#d9d5f2` fill):** The refined subset `Gcd(a, b) ⊂ ℕ` carved out by `Div(g) = Div(a) ∩ Div(b)`.
- **Solid navy dot (`#00008b`):** A concrete runtime value inhabiting the fiber (`g = 4` inside `Gcd(12, 8)`).
- **Dashed purple curve (`fig-2`):** A dependent function `(a : ℕ) → Gcd(a, 8)` drawn as a section across fibers.
- **Dark red circle with `✕` (`#8b0000`) and divisor tags (`extra!` / `missed!`):** A type error—a return value landing outside the target fiber over `(a, b)` because `Div(g) ≠ Div(a) ∩ Div(b)`.
- **Indigo dot and ring (`#4b0082`):** A symbolically unknown inhabitant `g*` during static verification.

## Per-Figure Claims ("Prose-Off" Test)
- **`fig-1.svg`:** `Gcd(a, b)` is a family of subsets of `ℕ` indexed by `(a, b)`; pulling out the fiber over `(12, 8)` yields `{4}` because only `g = 4` satisfies `Div(g) = Div(12) ∩ Div(8) = {1, 2, 4}`.
- **`fig-2.svg`:** Fixing `b = 8` and varying `a` slices the family into a period-8 bundle of fibers whose inhabitants jump among `{1}`, `{2}`, `{4}`, and `{8}` according to `Div(a) ∩ Div(8)` (including `Gcd(0, 8) = {8}` and coprime `Gcd(13, 8) = {1}`).
- **`fig-3.svg`:** A type error is a return value landing in the wrong fiber over `a = 12`—such as `g = 8` (inhabiting `Gcd(8, 8)` since `8 ∤ 12`) or `g = 2` (inhabiting `Gcd(2, 8)` since `Div(2)` misses `4`).
- **`fig-4.svg`:** Euclid's step `(x, y) ↦ (y, x mod y)` moves across the `(x, y)` plane along level sets preserving `Gcd(x, y)`—for `(12, 8) → (8, 4) → (4, 0)` on `{4}`, coprime `(21, 13) → … → (1, 0)` on `{1}`, and `(0, 0)` on `{0}`—until `y = 0` where `Gcd(x, 0) = {x}`.
- **`fig-5.svg`:** Codillon verifies `euclid(a, b)` by aligning the symbolic entry fiber `Gcd(a, b)`, loop fiber `Gcd(x, y)`, and exit fiber `Gcd(x, 0) = {x}`, accepting `return x` while flagging `return y` (`= 0`) as landing in the wrong fiber.

## What This Angle Makes Obvious
1. **Why "dependent" means indexed family:** `Gcd(a, b)` is visibly a map from values `(a, b)` to sets `Gcd(a, b) ⊂ ℕ`, not one fixed subset.
2. **Wrong fiber vs. non-integer:** Candidates like `g = 8` or `g = 2` for `(12, 8)` are valid naturals that inhabit *other* fibers (`Gcd(8, 8)` or `Gcd(2, 8)`), showing why they fail for `(12, 8)`.
3. **Why Euclid's exit needs no extra proof:** Preserving `Gcd(x, y) = Gcd(y, x mod y)` transports the type unchanged to `y = 0`, where `Div(0) = ℕ` makes `x ∈ Gcd(x, 0)` immediate.

## Weaknesses and Where It Misleads
- **Dimensional budget:** Because the 2D base space `(a, b)` and 1D fiber `g` consume three dimensions, divisor sets `Div(a) ∩ Div(b)` appear in linked strips (`fig-2`, `fig-3`) rather than inside each grid cell.
- **Singleton conflation:** Because every fiber has size 1, learners could conflate `{4}` with `4` unless the ambient spine `ℕ` and subset pill `{4} ⊂ ℕ` stay distinct.

## Living Inside Codillon's Editor Display
As shown in `fig-5.svg`, Codillon can display a **Fiber Gutter** beside the Wasm AST: each instruction links its active fiber `Gcd(x, y)` by `=` bridges to `Gcd(a, b)`. Under `if (y == 0)`, `y : {0}` collapses `Gcd(x, 0)` to `{x}`, marking `return x` valid (`✓`) and `return y` a red fiber mismatch (`✕`), while live probes plot concrete values against `{4}` or `{21}`.
