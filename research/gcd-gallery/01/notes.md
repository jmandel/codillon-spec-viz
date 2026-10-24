# Angle 01: The Divisibility Lattice

## Angle in One Sentence
Order $\mathbb{N}$ by divisibility ($u \mid v$) into a prime-factor Hasse diagram where each divisor set $\mathrm{Div}(n)$ is a downward cone (down-set), so the refinement type $\mathrm{Gcd}(a, b) = \{g \in \mathbb{N} \mid \mathrm{Div}(g) = \mathrm{Div}(a) \cap \mathrm{Div}(b)\}$ is visibly the unique top element (lattice meet $a \wedge b$) of the intersected cones.

## Visual Encoding (Mark → Meaning)
- **Lattice node (circle with $n$ and $2^i \cdot 3^j$)**: A natural number in base type $\mathbb{N}$, placed on prime-exponent axes (up-left $\times 2$, up-right $\times 3$).
- **Directed cover edge ($u \to v$ labeled $\times p$)**: Prime step $v = u \cdot p$; $u \mid v$ iff a directed path climbs from $u$ to $v$.
- **Dashed navy / gray hull ($\mathrm{Div}(a)$, $\mathrm{Div}(b)$)**: Principal down-set $\{d \in \mathbb{N} \mid d \mid n\}$ of all nodes reachable below an input parameter.
- **Solid purple shaded hull ($\mathrm{Div}(a) \cap \mathrm{Div}(b)$)**: Common-divisor down-set—the refinement predicate's target region.
- **Double-ringed purple node with `TOP` badge ($g = a \wedge b$)**: The unique inhabitant of $\mathrm{Gcd}(a, b)$ whose down-set $\mathrm{Div}(g)$ matches the purple cone.
- **Dark red ring and dashed red hull (`#8b0000`)**: A type error—a candidate $g$ whose cone $\mathrm{Div}(g)$ mismatches the purple target cone.

## Per-Figure Claims (Prose-Off Readout)
- **`fig-1.svg`**: In the divisibility lattice $\mathrm{Div}(24)$, the down-sets $\mathrm{Div}(12)$ and $\mathrm{Div}(8)$ intersect in $\{1, 2, 4\} = \mathrm{Div}(4)$, whose unique top element is $g = 4$.
- **`fig-2.svg`**: Any candidate other than $4$ fails type-checking because its red down-set $\mathrm{Div}(g)$ mismatches the purple target $\{1, 2, 4\}$—missing $4$ ($g = 2$), spilling outside $\mathrm{Div}(12)$ ($g = 8$), or diverging onto the $\times 3$ branch ($g = 6$).
- **`fig-3.svg`**: $\mathrm{Gcd}(a, b)$ is a dependent family of types indexed by values: moving $(a, b)$ inside $\mathrm{Div}(72)$ shifts the cone intersection and relocates the inhabitant from $4$ to $6$ to $1$.
- **`fig-4.svg`**: Divisibility $d \mid n$ is down-set containment $\mathrm{Div}(d) \subseteq \mathrm{Div}(n)$ (subtyping), and because every natural number divides $0$, $\mathrm{Div}(0) = \mathbb{N}$ sits at the lattice top so $\mathrm{Gcd}(12, 0) = \{12\}$.
- **`fig-5.svg`**: Each Euclidean step $(x, y) \mapsto (y, x \bmod y)$ shrinks the outer cones downward while leaving their purple intersection $\{1, 2, 4\}$ invariant, until $y = 0$ makes $\mathrm{Div}(y) = \mathbb{N}$ and exposes $x = 4$ as the top.

## What This Angle Makes Obvious
1. **Why the refinement type is a singleton**: By antisymmetry of divisibility on $\mathbb{N}$, a down-set has at most one generator $g$; seeing $\{1, 2, 4\}$ as a downward capsule makes it immediate that $4$ is its sole apex.
2. **Why "greatest" means Lattice Top, not arithmetic $\le$**: On $(12, 0)$, arithmetic "greatest" breaks because $\mathrm{Div}(0) = \mathbb{N}$ is infinite, yet in the divisibility order $0$ is the universal top ($n \mid 0$ for all $n$), making $\mathrm{Div}(12) \cap \mathrm{Div}(0) = \mathrm{Div}(12)$ effortless.
3. **Why $g = 2$ and $g = 8$ fail for dual reasons**: $g = 2$ lies inside the purple cone ($2 \mid 12 \wedge 2 \mid 8$) but below the apex ($4 \nmid 2$), whereas $g = 8$ covers the purple cone ($4 \mid 8$) but spills outside $\mathrm{Div}(12)$.

## Weaknesses and Where It Misleads
- **Dimension explosion with many primes**: Numbers $2^i \cdot 3^j$ form a clean 2D grid, but three primes require a 3D projection and four or more primes become cluttered hypercubes.
- **Additive modulo is jumped, not drawn**: While multiplication and divisibility are grid edges, $x \bmod y$ jumps across branches; its invariant $\mathrm{Div}(x) \cap \mathrm{Div}(y) = \mathrm{Div}(y) \cap \mathrm{Div}(x \bmod y)$ is shown as a preserved region rather than derived from grid geometry.

## Integration into Codillon's Editor Display
In Codillon's structured WebAssembly editor, each instruction row can embed a compact **Hasse sparkline** bound to `(x, y)`:
- As a student steps through `(i32.rem_u (local.get $x) (local.get $y))`, the outer cones contract step-by-step around the invariant purple meet cone.
- If a student returns a buggy value $g$, Codillon overlays the dark-red hull $\mathrm{Div}(g)$ against the purple target $\mathrm{Div}(a) \cap \mathrm{Div}(b)$ and highlights the witness node ($d = 4$ or $d = 8$) where the refinement predicate fails.
