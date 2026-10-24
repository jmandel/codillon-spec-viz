# Notes: Typing Derivation as Composed Pictures (Angle 09)

## Our Angle in One Sentence
A refinement-type proof for Euclid's algorithm is a modular pipeline of docked judgment tiles where each instruction maps an input state set into an output state set, every composition joint is a visual set-containment test (⊆), and any bug breaks a specific dock (⊈) with a counterexample witness.

## Visual Encoding (Mark → Meaning)
- **Rule Tile (`[INIT]`, `[WHILE]`, `[SUB]`, `[RET]`)**: A refinement typing judgment `⊢ {v ∈ P} stmt {v' ∈ Q}` with a left pre-state port and right post-state port.
- **2D Grid `(x, y)` & 1D Line `g`**: Muted gray dots (`#dedede`) show the unrefined base type `ℕ²` or `ℕ`.
- **Purple Halo & Fill (`#6A5ACD`, `#d9d5f2`)**: A refinement type—the subset of states satisfying the predicate, such as `Inv(x, y)` or `Gcd(a, b)`.
- **Docking Bridge with `⊆` Pill (`#6A5ACD`)**: The subtyping rule joining tile `i`'s post-port `Qᵢ` to tile `(i+1)`'s pre-port `Pᵢ₊₁`, locking when `Qᵢ ⊆ Pᵢ₊₁`.
- **Navy Ring & Arrows (`#00008b`)**: A concrete run `(x₀,y₀) → (x₁,y₁) → …` inside the purple set, paired with decreasing measure bars for `y ∈ ℕ`.
- **Dark Red Broken Dock (`⊈`, `#8b0000` & `#f9e2e2`)**: A type error where a post-state set leaks outside the next tile's pre-state set, highlighting the offending witness state.

## Claims Read Off Each Figure (Prose-Off Test)
- **`fig-1.svg`**: The refinement type `Gcd(12,8)` filters `ℕ` by divisor-set equality `Div(g) = Div(12) ∩ Div(8) = {1,2,4}` down to `{4}`, and judgments compose when one tile's output set fits inside (`⊆`) the next tile's input set.
- **`fig-2.svg`**: The `[WHILE-INV]` tile for `(12,8)` closes its inductive cycle because `(x,y) ← (y, x mod y)` maps every active state in `Inv ∧ (y≠0)` back into `Inv` while strictly decreasing `y` (`8 > 4 > 0`) until exiting on `y=0` at `(4,0)`.
- **`fig-3.svg`**: Four docked tiles—Entry `(12,8) ∈ Inv`, Loop preserving `Inv`, Exit slice `Inv ∧ (y=0) = {(4,0)}`, and Return projection—lock end-to-end to prove `Euclid(12,8) : Gcd(12,8) = {4}`.
- **`fig-4.svg`**: Indexing the dependent type family `Gcd(a,b)` across coprime `(13,8) → 1`, zero-input `(21,0) → 21`, and double-zero `(0,0) → 0` reshapes the purple set `Inv(a,b)` inside the tiles while preserving the exact same docking skeleton.
- **`fig-5.svg`**: Program bugs and wrong candidates (`g=8`, `g=2`, `g=0` for `(12,8)`) appear as dark-red broken docks (`⊈`) at the exact joint where containment fails—premature exit at Dock 2, invariant violation at the Body Dock, or wrong return register at Dock 3.

## What This Angle Makes Obvious (and Where It Misleads)
- **What it makes obvious**: Unlike a static Venn diagram or divisor lattice, composed judgment tiles show *how a program constructs evidence step by step*. It makes visual why loop invariants are both widened (to absorb all loop steps) and narrowed (sliced by `y=0` at loop exit so `Div(x) ∩ Div(0) = Div(x)` collapses to a singleton). Above all, it turns *fault localization* into a sight-check: a reader immediately sees *which* rule joint broke and *which* state leaked out.
- **Weaknesses / where it misleads**: Repeating miniature `(x,y)` grids across four docked tiles trades spatial resolution for structural clarity; for large inputs like `(1071,462)`, full grids cannot be drawn at 1:1 scale and must be zoomed or summarized. Moreover, drawing concrete trace arrows in navy inside the purple invariant set can tempt newcomers to think the proof only checks the single run `(12,8) → (8,4) → (4,0)`, rather than universally quantifying over all purple states in `Inv ∧ (y≠0)`.

## How This Lives Inside Codillon's Per-Instruction Editor Display
In Codillon's structured WebAssembly editor, each Wasm instruction (`local.set`, `loop ... br_if`, `return`) is a visual card. Our tile-and-dock grammar maps directly onto Codillon's instruction stack:
1. **Margin State-Set Ports**: Each instruction card displays a compact 60×60px state-set thumbnail on its entry and exit edges, showing the live refinement set `Inv(a,b)` for test inputs `(a,b)`.
2. **Snap-Fit Subtyping Joints**: Between adjacent instructions, Codillon renders a connector pill (`⊆` in purple `#6A5ACD`). When a student edits an instruction or loop guard, any broken implication turns that connector dark red (`⊈` `#8b0000`) and highlights the leaking counterexample `(x,y)` in the margin port.
