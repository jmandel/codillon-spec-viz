# Divisor Strips on a Number Line: Visualizing `Gcd(a, b)` as a Refinement Type

## Our Angle in One Sentence
We represent each $n \in \mathbb{N}$ by its **divisor strip** $\mathrm{Div}(n)$—a row of pins on a divisor number line—and visualize $\mathrm{Gcd}(a, b) = \{ g \in \mathbb{N} \mid \mathrm{Div}(g) = \mathrm{Div}(a) \cap \mathrm{Div}(b) \}$ as purple **sockets** $\mathrm{CD}(a, b)$ that a candidate $g$'s pins must fill with neither empty sockets nor spilled pins.

## Visual Encoding (Mark $\to$ Meaning)
- **Horizontal divisor axis (top strips):** Divisor candidates $d \in \mathbb{N}$ ($0, 1, 2, \dots$), aligned vertically across rows.
- **Solid navy pin ($\bullet$, `#00008b`):** Divisor membership $d \mid n$ on $\mathrm{Div}(n)$.
- **Faint gray dot (`#cccccc`):** Non-divisor ($d \nmid n$).
- **Purple ring socket ($\odot$, `#6A5ACD` border, `#d9d5f2` fill):** Required common divisor $d \in \mathrm{CD}(a, b) = \mathrm{Div}(a) \cap \mathrm{Div}(b)$.
- **Vertical purple pillar (`#d9d5f2`):** Column guide highlighting an invariant common divisor.
- **Navy pin seated in purple socket:** Verified match ($d \mid g$ and $d \in \mathrm{CD}(a, b)$).
- **Hollow dashed dark-red socket with `?` (`#8b0000`):** **Missing divisor error** ($d \in \mathrm{CD}(a, b)$ but $d \nmid g$).
- **Dark-red crossed pin (`#8b0000` $\times$):** **Spilled divisor error** ($d \mid g$ but $d \notin \mathrm{CD}(a, b)$).
- **Rightward arrow with $\cdots\;\forall d \in \mathbb{N}$:** The infinite strip $\mathrm{Div}(0) = \mathbb{N}$, since $0 = d \cdot 0$ for all $d \in \mathbb{N}$.
- **Bottom value axis ($g \in \mathbb{N}$):** The refinement type drawn as a subset of $\mathbb{N}$—a purple pill around the unique inhabitant $g = \gcd(a, b)$ and dark-red $\times$ on rejected values.

## Per-Figure Claims ("Prose-Off" Readout)
- **`fig-1.svg` ($a = 12, b = 8 \to 4$):** Intersecting $\mathrm{Div}(12)$ and $\mathrm{Div}(8)$ yields the socket strip $\mathrm{CD}(12, 8) = \{1, 2, 4\}$, which is matched exclusively by $\mathrm{Div}(4)$, carving out the singleton set $\{4\}$ on the value line.
- **`fig-2.svg` (Type errors for $(12, 8)$):** Wrong candidates fail the socket test in two distinct ways: $g = 2$ leaves socket $4$ empty (too small), $g = 8$ spills pin $8$ outside the sockets (too large), and $g = 6$ both misses socket $4$ and spills pins $3, 6$.
- **`fig-3.svg` (Euclid's loop $(12, 8) \to (8, 4) \to (4, 0)$):** Each modulo step alters $\mathrm{Div}(x)$ and $\mathrm{Div}(y)$ while keeping their intersection strip $\mathrm{CD}(x, y) = \{1, 2, 4\}$ invariant; at $y = 0$, $\mathrm{Div}(0) = \mathbb{N}$ acts as the intersection identity, forcing $\mathrm{Div}(x) = \mathrm{CD}(a, b)$.
- **`fig-4.svg` (Extreme pairs $(13, 8) \to 1$ and $(0, 0) \to 0$):** Coprime inputs share only the single socket $\{1\}$, whereas $(0, 0)$ creates infinitely many sockets $\mathrm{CD}(0, 0) = \mathbb{N}$ that reject every positive integer ($g = 12$ leaves infinitely many sockets empty) and admit only $g = 0$.
- **`fig-5.svg` (Subtyping and half-specifications):** Splitting $\mathrm{Div}(g) = \mathrm{CD}$ into $\mathrm{Div}(g) \subseteq \mathrm{CD}$ (no spills: $\{1, 2, 4\}$) and $\mathrm{CD} \subseteq \mathrm{Div}(g)$ (no empty sockets: $\{0, 4, 8, 12, \dots\}$) shows subtyping as set containment whose intersection is $\mathrm{Gcd}(12, 8) = \{4\}$.

## What This Angle Makes Obvious (and Where It Struggles)
**Strengths:**
1. **Why "greatest" needs no `<` or `max`:** Set equality $\mathrm{Div}(g) = \mathrm{CD}(a, b)$ visually forces $g$ to be greatest—any smaller common divisor leaves a socket empty.
2. **Two-sided refinement anatomy:** Readers immediately separate $\mathrm{Div}(g) \subseteq \mathrm{CD}$ from $\mathrm{CD} \subseteq \mathrm{Div}(g)$ as *no spills* vs. *no empty sockets*.
3. **Why $y = 0$ closes the proof:** Because $\mathrm{Div}(0)$ fills every position on $\mathbb{N}$, intersecting $\mathrm{Div}(x)$ with $\mathrm{Div}(0)$ visibly leaves $\mathrm{Div}(x)$ intact.

**Weaknesses:**
1. **Linear scale limit:** A literal number line fits small numbers ($n \le 20$) cleanly; large inputs like $(1071, 462)$ require compressed or factor-filtered axes.
2. **Two number lines:** Readers must distinguish the top *divisor axis* ($d \in \mathbb{N}$, internal evidence) from the bottom *value axis* ($g \in \mathbb{N}$, the inhabited type).

## Integration into Codillon's Per-Instruction Editor Display
In Codillon's WebAssembly editor, each variable binding or instruction carries a 16 px **sparkline strip** in the right gutter: purple sockets show the target $\mathrm{CD}(a, b)$ while navy pins show the current value's divisors. Across a `loop`, the sockets form continuous vertical rails confirming `(i32.rem_u)` preserves the invariant, while a buggy return highlights inline dark-red spilled pins or hollow sockets.
