# Spec: "gcd as a type" — the simplest typed proof of Euclid's algorithm, visualized

A standalone page, `artifacts/gcd-as-a-type.html`. Goal: show the *simplest possible* fully typed Euclid's algorithm,
with the output typed as "the gcd of the inputs", and make the visualization express the **semantics of the type
system**, not just the run. Machine-checked proof: `proofs/EuclidGcd.lean` (Lean 4.35.0, core only).

## The one idea
Let Div(n) be the set of divisors of n (Div(0) = every natural number). Define

    Gcd(a, b) = { g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }

a **dependent refinement type**: a set of numbers that depends on a and b. It has exactly one inhabitant, the gcd.
Euclid's algorithm never changes the set Div(x) ∩ Div(y) of common divisors; it only shrinks y. When y = 0 the common
divisors are Div(x) ∩ Div(0) = Div(x), so x inhabits the type. That is the whole proof:

| obligation | as a type/set statement | picture |
|---|---|---|
| entry | (a, b) is in the invariant set | the start cell is shaded |
| preservation | every shaded state with y ≠ 0 steps to a shaded state | every arrow from a shaded cell lands in a shaded cell |
| termination | y strictly decreases (x mod y < y) | every arrow points to a lower row |
| exit | shaded ∩ {y = 0} ⊆ Gcd(a, b) × {0} | the bottom row meets the shaded region in exactly one cell, (gcd, 0) |
| the lemma | Div(y) ∩ Div(x mod y) = Div(x) ∩ Div(y), because x mod y = x − q·y | a d×d grid tiles an x×y rectangle iff it tiles the y×(x mod y) rectangle left after cutting q squares |

The invariant set {(x, y) | Div(x) ∩ Div(y) = Div(a) ∩ Div(b)} is exactly {(x, y) | Gcd(x, y) = Gcd(a, b)}: **the loop
never changes the type of the answer.** That sentence is the page's thesis.

## Type-system semantics the page must make visible
1. A type is a set of values; a refinement is a subset; a **dependent** type is a family of sets indexed by values
   (moving a or b redraws Gcd(a, b)).
2. A value of a refined type is a value **plus evidence** (Lean's subtype `{g // P g}`); here the evidence is a
   picture you can check: two rows of divisor dots coincide. At run time the evidence is **erased**: only the number moves.
3. A loop's state has a type too: the invariant is a **set of states**. Typing the loop is three containments and one
   decreasing measure (table above). Lean's recursion `euclid x : (y : Nat) → Gcd x y` with `termination_by y` is the
   same thing: the recursive call's type `Gcd y (x % y)` *equals* `Gcd x y` by the lemma.
4. A proof obligation is a containment (subtyping); a failure is the part that does not fit (the spill).
5. Proven ≠ held on this run: the state-space picture checks preservation for **every** shaded state in view, not just the
   ones the run visits; the lemma is what extends it to all of ℕ.

## Page structure (tutorial voice, interactive throughout; same style tokens and fonts as the walkthrough)
0. **Title and thesis.** "The type of the answer never changes." One paragraph. Inputs a, b chosen once at the top
   (sliders 0–60, presets (12, 8), (1071, 462) shown scaled, (21, 0), (0, 0), (13, 8) Fibonacci worst case) and shared by
   every panel below.
1. **The type Gcd(a, b).** A divisor strip: number line 1…N with rows Div(a), Div(b), and their intersection CD(a, b).
   Below it, a candidate g (slider): its row Div(g) laid directly against CD. Equal rows → the rule snaps solid
   and g is an inhabitant. Extra divisors spill as darkred dots above the row; missing ones are hollow darkred sockets.
   A number line 0…N shows the whole type as a set: exactly one lit point. Show Div(0) honestly (a full row with "…").
2. **Why a step keeps the divisors (the lemma).** An x × y rectangle. Pick a d from CD: a d-grid overlays and tiles it.
   "Step" cuts q = ⌊x/y⌋ y×y squares, leaving y × (x mod y); the same d-grid still tiles it. Pick a d not in CD: the grid
   misfits on some edge (darkred spill), before and after alike. Repeating to the end leaves g × g squares: the gcd is
   the side of the smallest square that tiles the original rectangle.
3. **The program.** Euclid in Codillon's real idiom (fractions LEFT of the code, pale ribbons, rounded brackets,
   pink loop bracket, MLModern; copy the rendering from `artifacts/00-refined-codillon.html`), with specs:
   ```
   (@define cd(d, x, y) = $x % d == 0 && $y % d == 0)
   (func $gcd (param $a (i32 | 0 <= $a)) (param $b (i32 | 0 <= $b))
              (result $g (i32 | forall d in 1..($a+$b+1): ($g % d == 0) == cd(d, $a, $b)))
     (local $x i32) (local $y i32) (local $t i32)
     local.get $a / local.set $x / local.get $b / local.set $y
     block $done
       loop $step
         (@invariant forall d in 1..($a+$b+1): cd(d, $x, $y) == cd(d, $a, $b))
         (@decreases $y)
         local.get $y / i32.eqz / br_if $done
         local.get $x / local.get $y / i32.rem_u / local.set $t
         local.get $y / local.set $x / local.get $t / local.set $y
         br $step
       end
     end
     local.get $x)
   ```
   (one instruction per line; the bounded quantifier is exact because a nonzero divisor of a or b is ≤ max(a, b), and
   every d divides 0). A step slider runs the real loop with values in the shapes. The result's refined shape shows
   the type as a single socket on its number line, and the returned value seats in it. All obligations are **proven**
   (by the Lean proof), so the listing is calm.
4. **The loop has a type.** State-space grid: x on one axis, y on the other (0…N). Shade the invariant set
   {(x, y) | gcd(x, y) = gcd(a, b)} (compute with real gcd; it is a striking lattice-of-rays pattern). Draw the run's
   trajectory as arrows linked to the slider in §3 (the current state cell pulses). Toggle "every state": draw the
   successor arrow from **every** shaded cell with y ≠ 0; all land in shaded cells and all point to a lower row.
   Highlight the bottom row y = 0: it meets the shaded set in exactly (g, 0), with a projection to §1's number line.
   Hovering any cell shows its Div(x) ∩ Div(y) row: the same picture as CD(a, b) for every shaded cell.
5. **What a type error looks like here.** Two seeded mistakes, each switchable, each drawn in the same vocabulary:
   - `return $y` instead of `$x`: the exit projects to 0; Div(0) is everything, so in §1 every non-divisor spills
     darkred. ⚖ on the return line; the result shape's dot misses its socket.
   - invariant too weak (`(@invariant 0 <= $y)`): the shaded set becomes the whole grid; the bottom row now meets it
     everywhere, and the exit containment fails: the extra bottom-row cells spill. The code is right; the spec is too
     short to prove the type. Show this case without ⚖ on the code. It is a hole on the invariant (indigo, unknown).
6. **The proof, line by line.** The Lean file verbatim (from `proofs/EuclidGcd.lean`), each part cross-linked to its
   picture (hover a Lean line → the matching picture highlights; and back): `Gcd` ↔ §1, the lemma ↔ §2, `| 0 =>` ↔ the
   bottom row, `| y + 1 =>` ↔ the arrows, `termination_by y` ↔ arrows point down, `gcd_type_is_a_singleton` ↔ one lit
   point. State that it was checked with Lean 4.35.0 (core library only) and link to the file on GitHub.
7. **Erasure.** One short closing panel: the same run with the evidence hidden is exactly Codillon today; the type
   adds pictures, not instructions. Link back to the walkthrough and the study index.

## Quality bar
Same as the walkthrough: calm when correct, darkred only for violated, six-state styling, works on a 412 px phone
(fit mode), zero console errors, self-contained (embed the MLModern fonts), screenshots reviewed by eye. Every number
on the page is computed, not typed in: gcd, divisor sets, the shaded region, the trajectory.
