# Angle 04: Euclid's Rectangle Tiling

## Angle in One Sentence
An `a×b` rectangle is tiled without overhang by `d×d` squares iff `d ∈ Div(a)∩Div(b)`, so Euclid's square-cutting step `(x,y) ↦ (y, x mod y)` visibly preserves the refinement type's evidence set `Div(x)∩Div(y)` until a zero remainder leaves the coarsest common tile `g = gcd(a,b)`.

## Visual Encoding (Mark → Meaning)
- **Navy outer rectangle (`a×b`, `#00008b`)**: A concrete input pair `(a,b)` or loop state `(x,y)` drawn to scale.
- **Purple square grid (`d×d`, stroke `#6A5ACD`, fill `#d9d5f2`)**: A valid common divisor `d ∈ Div(a)∩Div(b)` covering `a×b` with zero remainder; nested subgrids (`1×1`, `2×2`) inside a bold master tile (`g×g`) encode set equality `Div(g) = Div(a)∩Div(b)`.
- **Dark-red hatched overhang (`#8b0000` diagonal hatch outside the navy boundary)**: A type error or divisibility violation (`d ∤ a` or `d ∤ b`), turning a non-zero remainder into physical tile protrusion past the rectangle's edge.
- **Dashed red cut line**: One Euclidean division step `x = q·y + r` slicing off `q` squares of side `y` and leaving remainder rectangle `r×y`.
- **Indigo dashed rectangle (`#4b0082`)**: Compile-time unknown dimensions `(x,y)` with symbolic quotient `q` and remainder `r = x mod y`.
- **1D navy segment (height `0`)**: A degenerate `a×0` rectangle at termination, where `0 = 0·d` means every `d ∈ ℕ` tiles height `0` (`Div(0) = ℕ`).

## Per-Figure Claims (Prose-Off Reading)
- **`fig-1.svg`**: Among candidate square sides `d ∈ {1…6}` tested on a `12×8` rectangle, only `d ∈ {1,2,4}` tile without red overhang, and `g=4` is the unique inhabitant of `Gcd(12,8)` because its `4×4` master tile contains every valid common grid (`Div(4) = {1,2,4}`).
- **`fig-2.svg`**: Cutting `y×y` squares from an `x×y` rectangle (shown for `(12,8) → (8,4) → (4,0)` and `(30,18) → (18,12) → (12,6) → (6,0)`) never gains or loses a valid `d`-grid, keeping the refinement type `Gcd(x,y)` identical across loop steps.
- **`fig-3.svg`**: For coprime Fibonacci inputs `(13,8)`, five square cuts spiral down to `1×1` unit squares (`Gcd(13,8) = {1}`), whereas for `(21,0)` zero height is tiled by `0` copies of every `d ∈ ℕ` (`Div(0) = ℕ`), giving `Div(21)∩ℕ = Div(21)` and `Gcd(21,0) = {21}`.
- **`fig-4.svg`**: A wrong candidate violates `Gcd(12,8)` in one of two visible ways—`g=8` overhangs width `12` (`Div(8) ⊈ Div(12)∩Div(8)`), while `g=2` is too fine and is overhung by valid common tile `d=4` (`Div(12)∩Div(8) ⊈ Div(2)`)—and a buggy step `r' = (x mod y)−1` breaks subtyping by mutating the tile set from `{1,2,4}` to `{1}`.
- **`fig-5.svg`**: Across the dependent index plane `ℕ×ℕ`, Euclid's transitions travel strictly inside iso-type fibers `Gcd(x,y) = {g}` until reaching `(g,0)`, allowing compile-time verification of symbolic unknown `(x,y)` and runtime erasure of the tiling evidence.

## What This Angle Makes Obvious (and Where It Misleads)
**Makes obvious:** Why `x mod y` preserves common divisors. Algebraically, `Div(x)∩Div(y) = Div(y)∩Div(x mod y)` feels like a number-theoretic trick; geometrically, a `y×y` square is manifestly tiled by any `d` that tiles `y`, so slicing `y×y` off a `d`-tiled `x×y` rectangle leaves the remainder tiled by the exact same `d`-grid. It also makes both halves of the refinement predicate—soundness (`g` tiles `a×b`) and completeness (all common tiles nest inside `g`)—visually distinct.

**Weaknesses / where it misleads:**
1. *Scale limits:* When `a/b` or `a/d` is large (e.g., `(1071,462)`), individual `1×1` tiles become microscopic, requiring schematic ellipsis (`fig-5.svg`).
2. *Zero dimension:* A `21×0` or `0×0` rectangle has zero area, which can mislead students into thinking "nothing fits" unless drawn as a 1D segment where `0 = 0·d` requires zero tiles along the collapsed axis (`fig-3.svg`).

## Integration into Codillon's Per-Instruction Editor Display
In Codillon's structured WebAssembly editor, clicking a loop header, branch (`if (y == 0)`), or assignment (`(x,y) = (y, x % y)`) can display a compact inspector card (`fig-5.svg` Panel 2):
1. **Symbolic Tile Strip:** An indigo symbolic `x×y` rectangle split into `q` squares of side `y` plus remainder `r×y`, with a purple `d×d` witness tile locked across the cut line to prove invariance.
2. **Concrete PiP:** A miniature `(12,8)` rectangle highlighting the instruction's cut (or collapsing to `4×0` in the `then` branch), flashing dark-red overhang if an edit breaks the invariant.
