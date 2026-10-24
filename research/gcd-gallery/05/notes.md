# Notes: State-Space Invariant

## Angle
By plotting the algorithm's loop state (x, y) on a Cartesian grid, we can visualize the type `gcd(x, y) = gcd(a, b)` as an invariant subset of the state space, with Euclid's trajectory mapping to a specific path that remains within this subset until uniquely terminating at `(g, 0)`.

## Visual Encoding
- **Grid and axes:** The state space of all possible `(x, y)` pairs in $\mathbb{N} \times \mathbb{N}$.
- **Purple shaded circles:** Cells that belong to the invariant set `{ (x, y) | gcd(x, y) = g }`.
- **Dashed purple arrows:** All valid state transitions `(x, y) \to (y, x \bmod y)` originating from the invariant set, proving closure (all arrows point to another shaded cell and go down in $y$).
- **Navy blue circles and thick arrows:** A concrete run of Euclid's algorithm for a specific pair of inputs, serving as an explicit proof of termination.
- **Pale dashed rays from the origin:** The "primitive rays" structure of the set. Each primitive ray contains exactly one shaded cell, revealing that the invariant set forms a transversal across all such rays.
- **Translucent purple horizontal line (y = 0):** The exit condition for the loop. 
- **Dark red cells, arrows, and text (Figure 4 only):** A type error depicting a violation, showing a poorly chosen, too-weak invariant set that fails to constrain the final output to a unique value.

## Figure Claims
- **Figure 1 (12, 8 → 4):** The invariant set `gcd(x, y) = 4` is closed under loop transitions, each primitive ray intersects the set precisely once, and the set meets the termination row uniquely at `(4, 0)`.
- **Figure 2 (13, 8 → 1):** When the inputs are coprime, the invariant set `gcd(x, y) = 1` is dense, containing exactly the first integer coordinate encountered on every possible primitive ray.
- **Figure 3 (0, 0 → 0):** For zero-inputs, the algorithm begins and ends immediately at the origin, which is the only cell in its invariant set.
- **Figure 4 (Type Error):** An invariant like "gcd(x, y) is even" is too weak because its shaded set meets the exit row in multiple places, meaning the return value is no longer uniquely determined.

## Strengths
This angle perfectly captures the dual geometric-algebraic nature of the invariant. It makes it immediately obvious *why* the loop is correct (all transitions stay within the shaded set and strictly decrease in y) and *why* the return value is uniquely typed (the set intersects `y=0` at exactly one cell). The ray structure also illuminates how the refinement type partitions $\mathbb{N} \times \mathbb{N}$ into non-overlapping equivalence classes.

## Weaknesses
The grid approach doesn't scale well to realistically large integers; it only works for small instructional examples (like values < 25). Additionally, the visualization treats transitions as instantaneous geometric jumps, hiding the arithmetic intuition behind *why* `x mod y` preserves the common divisors (unlike a tiling or subtraction-area visualization).

## Integration in Codillon
In Codillon's per-instruction editor, this visualization could serve as a live "type debugger." When writing the loop, the editor would display a zoomed-in grid centered on the current state.
- Before the loop, the grid highlights the singleton set of the input `(a, b)`.
- Inside the loop body, the grid lights up the entire invariant set `gcd(x, y) = g`. 
- Clicking on any cell in the invariant set would render the predicted trajectory down to the $x$-axis.
- If the user writes a buggy transition (e.g., `x, y = y, x - 1`), the transition arrows would instantly turn red, breaking out of the purple invariant set and signaling a type error visually before the compiler even generates an error message.