# Notes: Visualizing `Gcd(a, b)` in Codillon's Editor Idiom (Angle 10)

## Angle in One Sentence
Refinement types become spatial constraints inside Codillon's stack-effect fractions: each `i32` widens from a `30×11` box into an `84×14` hybrid log-linear number line where admitted sets are shaded regions, dependent result types like `Gcd(a, b)` appear as single sockets tethered to parameters, valid values seat in their sockets, and type errors spill over the rim in dark-red hatch.

## Visual Encoding (Mark → Meaning)
- **Fraction bar & stack shapes**: Open-top input cups above the rule represent stack values consumed; solid-bordered shapes below represent values produced.
- **Unrefined vs. Refined `i32`**: Unrefined `i32` is a `30×11` box; refined `{v : i32 | P(v)}` is an `84×14` number line (`INT_MIN` at left, `INT_MAX` at right, linear for `|v| ≤ 8` across the middle 60%, log across the outer 20% wings).
- **Purple shaded regions & notches (`#6A5ACD` / `#d9d5f2`)**: The admitted subset of `i32`. Divisor sets `Div(n)` appear as notches at each `d | n`; `Div(0) = ℕ` shades the non-negative range.
- **Result Socket & Indigo Tethers (`#4b0082`)**: On the return cup, `Gcd(a, b) = {g ∈ ℕ | Div(g) = Div(a) ∩ Div(b)}` is a singleton socket notched into the top rim and tethered by dashed curves to `param $a` and `param $b`.
- **Pale-Lavender Dataflow Ribbons (`#d9d5f2`)**: Connect each output shape to the input cup it feeds, visually enforcing subtyping as set containment (`⊆`).
- **Navy Bead & Bar (`#00008b`)**: A concrete value seated at its coordinate on the number line.
- **Dark-Red Hatch Spill (`#8b0000`)**: A value outside an input cup's admitted region or missing the `Gcd(a, b)` socket overflows the rim in dark-red hatch, signaling a type error.

## Per-Figure Claims ("Prose-Off" Test)
- **`fig-1.svg`**: Refining `i32` expands Codillon's `30×11` stack boxes into `84×14` number lines where valid divisors seat inside `[1, INT_MAX]`, `0` spills over the rim, and `Gcd(12, 8)` forms a single socket at `4` tethered to `$a = 12` and `$b = 8`.
- **`fig-2.svg`**: Across every instruction of Euclid's WAT loop on `(12, 8)`, lavender ribbons pour values into matching cups while preserving `Div(x) ∩ Div(y) = {1, 2, 4}`, until `y = 0` (`Div(0) = ℕ`) lets `x = 4` seat in the tethered `Gcd(12, 8)` return socket.
- **`fig-3.svg`**: Because `Gcd(a, b)` is indexed by `a` and `b`, changing the inputs—to `(1071, 462) → 21`, coprime `(13, 8) → 1`, `(21, 0) → 21`, or `(0, 0) → 0`—slides the tethered result socket along the number line.
- **`fig-4.svg`**: For `(12, 8)`, only `g = 4` satisfies `Div(g) = {1, 2, 4}`; returning a smaller common divisor (`g = 2`), a non-divisor of `a` (`g = 8`), or exiting early (`g = 12`) misses the socket at `4` and spills dark-red hatch over the cup rim.
- **`fig-5.svg`**: Subtyping is set containment—the singleton `{4}` funnels without spilling into wider supertype cups (`CommonDiv(12, 8) ⊆ Div(12) ⊆ Nat ⊆ i32`)—and all sockets, tethers, and proofs erase at compile time to `30×11` WebAssembly instructions.

## What This Angle Makes Obvious vs. Where It Misleads
- **Makes obvious**: It connects refinement type theory directly to WebAssembly code. Newcomers see *why* a type is a set (shaded region), *what* dependent typing means (tethers pulling the socket when `$a` or `$b` change), *how* dataflow induces subtyping (a ribbon must fit inside the receiving cup without spilling), and *why* `i32.rem_u` cannot divide by zero after `br_if $exit` narrows `$y` to `[1, MAX]`.
- **Weaknesses**: Drawing `Gcd(a, b)` as a 1D socket makes its *singleton inhabitant* `{g}` immediately salient, but compresses the lattice structure of `Div(a) ∩ Div(b)` into 1D ticks. Also, the logarithmic wings (`|v| > 8`) compress large integers into 20% of the width, requiring a hover inspector to distinguish adjacent large values.

## Integration in Codillon's Editor Display
In Codillon's WAT editor, the left gutter renders `30×11` stack fractions per instruction. When a student writes a refined signature, `i32` slots widen in-place to `84×14` number lines (`fig-2.svg`). Hovering over `return` or `i32.rem_u` opens the magnified inspector (`fig-1.svg` / `fig-4.svg`), highlights the dependency tethers to `$a` and `$b`, and displays concrete runs (`navy`) alongside spill diagnostics (`dark-red` hatch).
