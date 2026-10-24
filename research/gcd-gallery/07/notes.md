# Angle 07: The Bézout / Ideal View of `Gcd(a, b)`

## Angle in One Sentence
The dependent refinement type `Gcd(a, b)` is the singleton set containing the unique canonical generator $g \in \mathbb{N}$ of the principal ideal $a\mathbb{Z} + b\mathbb{Z} = \{ax + by \mid x, y \in \mathbb{Z}\} = g\mathbb{Z}$, making $g$ both the smallest positive linear combination of $a$ and $b$ and the step size of their combined lattice.

## Visual Encoding (Marks → Meaning)
- **Integer Number Lines ($\mathbb{Z}$) & Caliper Brackets**: The ambient base type of integers with small gray ticks at every integer and step-size brackets beneath the axis.
- **Purple Lattice Nodes (`#6A5ACD`) & Muted Fill (`#d9d5f2`)**: Elements inhabiting the ideal $a\mathbb{Z} + b\mathbb{Z} = g\mathbb{Z}$ and the refinement type region.
- **Double-Ringed Purple Node**: The unique generator $g \in \text{Gcd}(a, b)$—the first positive lattice point to the right of $0$ (or $0$ when $a = b = 0$).
- **Shaded Dashed Box on $(0, g)$**: The forbidden open gap of $g - 1$ unreachable integers, visually proving minimality ($a\mathbb{Z} + b\mathbb{Z} \subseteq g\mathbb{Z}$).
- **Navy Arcs, Nodes, and Badges (`#00008b`)**: Concrete values, input strides ($a\mathbb{Z}, b\mathbb{Z}$), and constructive Bézout certificates $(x, y)$ showing how hops of $+a$ and $+b$ reach $g$.
- **2-D Parallel Fibers in $\mathbb{Z}^2$**: Iso-value lines $ax + by = k g$ partitioning $\mathbb{Z}^2$, with kernel vector $(-b/g, a/g)$ shifting between equivalent certificates along a fiber.
- **Dark Red Crosses & Dashed `?` Circles (`#8b0000`)**: Type errors where a candidate grid $g'\mathbb{Z}$ mismatches $a\mathbb{Z} + b\mathbb{Z}$—either **off-grid collisions** ($ax + by \notin g'\mathbb{Z}$, grid too coarse) or **unreachable ghosts** ($g'\mathbb{Z} \setminus (a\mathbb{Z} + b\mathbb{Z})$, grid too fine).

## Prose-Off Claims per Figure
- **`fig-1.svg` (`a = 12, b = 8 → 4`)**: Combining strides of $12$ and $8$ carves out the lattice $12\mathbb{Z} + 8\mathbb{Z} = 4\mathbb{Z}$, whose smallest positive element and step size is $g = 12(1) + 8(-1) = 4$.
- **`fig-2.svg` (2-D Coefficient Lattice & Fibers)**: The map $(x, y) \mapsto 12x + 8y$ partitions $\mathbb{Z}^2$ into parallel fibers separated by an empty lattice-free corridor of width $4$, projecting onto $4\mathbb{Z}$.
- **`fig-3.svg` (`1071, 462 → 21` and Coprime `13, 8 → 1`)**: Extended Euclid preserves the ideal $r_i\mathbb{Z} + r_{i+1}\mathbb{Z} = a\mathbb{Z} + b\mathbb{Z}$ while shrinking remainders to the generator ($21$ via $1071(-3) + 462(7) = 21$, and $1$ for coprime $(13, 8)$ which saturates $\mathbb{Z}$).
- **`fig-4.svg` (Type Errors for `Gcd(12, 8)`)**: Candidate $g = 8$ is too coarse because reachable values $4$ and $12$ land off its grid ($12\mathbb{Z}+8\mathbb{Z} \not\subseteq 8\mathbb{Z}$), while $g = 2$ is too fine because odd multiples like $2, 6, 10$ are unreachable ghosts ($2\mathbb{Z} \not\subseteq 12\mathbb{Z}+8\mathbb{Z}$).
- **`fig-5.svg` (Duality, Edge Cases, and Codillon View)**: Divisibility $d \mid n$ is order-reversing ideal containment $n\mathbb{Z} \subseteq d\mathbb{Z}$ (so greatest common divisor is the smallest enclosing ideal), naturally handling $21\mathbb{Z} + 0\mathbb{Z} = 21\mathbb{Z}$ and $0\mathbb{Z} + 0\mathbb{Z} = \{0\}$.

## What This Angle Makes Obvious (and Where It Misleads)
Unlike divisor-set Venn diagrams—where "greatest" is an external ordering on a finite intersection—the Bézout/ideal view turns the universal quantifier ($\forall d.\, d \mid a \wedge d \mid b \to d \mid g$) into **geometric reachability**. A pair $(x, y)$ with $ax + by = g$ is a concrete, $O(1)$-checkable proof witness (erased at runtime) that $g$ inhabits the ideal, while the empty gap $(0, g)$ makes minimality visually unmistakable. Moreover, Euclid's step $(x, y) \mapsto (y, x \bmod y)$ is immediately seen as an ideal-preserving basis change.

**Weaknesses**: First, $a\mathbb{Z} + b\mathbb{Z}$ uses signed integers $\mathbb{Z}$ (one coefficient is $\le 0$), whereas WebAssembly instructions often use unsigned `u32`/`ℕ`. Second, large inputs like $(1071, 462)$ span many steps, requiring a zoomed inset near $0$.

## Integration into Codillon's Per-Instruction Display
As shown in `fig-5.svg`, each instruction in Codillon can display an inline **Live Ideal Strip**: a compact number line showing the invariant lattice $x\mathbb{Z} + y\mathbb{Z}$ in purple, register values $x, y$ as navy pebbles, and their ghost Bézout certificates. Stepping through `x mod y` keeps the purple ticks fixed while the navy pebbles hop leftward until $y = 0$ and $x$ rests on the generator $g$.
