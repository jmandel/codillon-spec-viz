# A minimal calculus for "Euclid returns the gcd", with pictures that compose

Design note for `artifacts/gcd-foundations.html` (2026-10-23). Independent of 13; written without reading it.
Standalone checker: `proofs/minimal/check-euclid.cjs` (output in `proofs/minimal/output.txt`).

The question: the smallest type theory in which Euclid can be written with its output typed as the gcd of the
inputs and proved, with one picture per rule and proofs that are pictures plugged together. Lean does it
(`proofs/EuclidGcd.lean`) with inductive families, universes, subtypes and tactics, none of which a student can see.

## The calculus: types as finite sets of states

**One idea.** A type is a set. The state of the program is a tuple of small naturals; here `(x, y)` for fixed
parameters `(a, b)`, every variable in `0..32`. A type `{s | P}` is the set of states where `P` holds; a judgment
`c : A ⇒ B` says a fragment started anywhere in `A` runs without trapping and ends in `B`; a function's type is the
set of values it may return. Nothing else: no dependent function space, no universes, no quantifier the reader
instantiates, no proof terms. The divisor set `Div(e)` is a *value* (a 32-bit mask over `d = 1..32`), so
"`Div(r) = CD(a, b)`" is an equation between two things the evaluator computes, not a `∀d`.

```
e ::= n | x | e mod e                       S ::= Div(e) | CD(e, e)
P ::= true | e = e | e ≠ e | e < e | e ≤ e | S = S | S ⊆ S | P ∧ P
c ::= x̄ := ē | c ; c | while P inv I measure e do c        fun f(ā) : {r | P} = c ; return e
```

**Five rules.** ASSIGN `x̄ := ē : A ⇒ ē(A)` (premise: `ē` defined on every state of `A`; picture: panel, dock,
panel of the exact image). SEQ `c₁ : A ⇒ B`, `c₂ : B ⇒ C` ⊢ `c₁;c₂ : A ⇒ C` (premise: the output set of `c₁`
equals the declared input of `c₂`; picture: two pictures sharing one panel). SUB `c : A ⇒ B′`, `B′ ⊆ B` ⊢
`c : A ⇒ B` (picture: `B′` solid over `B` pale). WHILE `c : I ∧ b ⇒ I` and the measure drops on every row ⊢
`while b … : I ⇒ I ∧ ¬b` (picture: head panel, the body's picture, its last panel overlaid back onto the head, a
triangle plot). FUN `c : U ⇒ {s | P[e/r]}` ⊢ `fun f(ā) : {r | P} = c; return e` (picture: a column panel
projected onto a strip of values). SUB is one-sided because forward ASSIGN computes exact images, so input-side
weakening is never needed. The measure premise is the total-correctness side condition in set form: for every `k`,
`body(I ∧ b ∧ {m = k}) ⊆ {m < k}`.

**Why minimal.** One rule per construct of the program plus the one rule that lets a proof argue. Remove SUB and
the invariant cannot be entered or left; remove the measure and termination is unproved; remove ASSIGN's
definedness premise and `x mod 0` passes silently. There is no IF because Euclid has none (it would be a sixth
picture: split a panel by the test, two pictures, union).

## The type of the answer

`{r | Div(r) = CD(a, b)}`: the divisors of `r` are exactly the common divisors of `a` and `b`. Compared with
`r = gcd(a, b)` for a recursively defined spec function, it says what the gcd *is* rather than how Euclid computes
it (the recursive spec is circular as a specification). Compared with "greatest common divisor" it needs no order,
is right at `gcd(0, 0) = 0`, and, decisively, makes the invariant a picture of a set that does not move:
`I = {CD(x, y) = CD(a, b)}`. Euclid's step `(x, y) ↦ (y, x mod y)` keeps the common divisors; the exit `y = 0`
turns `CD(x, 0)` into `Div(x)`. The type has exactly one inhabitant for every `(a, b)`.

## The trusted base, plainly

1. **The evaluator** (25 lines): `mod` (undefined when the divisor is 0), comparisons, `Div` as a bitmask over
   `d = 1..32` with `Div(0)` = every `d`, simultaneous assignment.
2. **Enumeration as the decision procedure.** Every leaf premise (containment, set equality, definedness, measure
   decrease) is decided by evaluating the formula on all 1089 states of a slice, and the all-slices check repeats
   this for all 1089 pairs `(a, b)`. For this bounded domain the result is a proof. It is also true that exhaustive
   testing of the *program* would have been a proof for this domain; the derivation earns its keep by saying *why*
   (the invariant) in a form whose size does not grow with the domain. The same tree is the proof for 32-bit
   integers once three leaf facts (`CD(y, x mod y) = CD(x, y)` for `y ≠ 0`; `x mod y < y` for `y ≠ 0`;
   `CD(x, 0) = Div(x)`) are discharged by lemma or SMT instead of enumeration; the page names them on hover.
3. **The checker** (~120 lines, one case per rule) and the fact that every picture is drawn from the checker's own
   sets, never from a second renderer.

What the calculus cannot do: unbounded domains, 32-bit wraparound, conditionals, nested loops, calls, memory,
ghost state, quantifiers, and invariant search. A weak or missing invariant is refused, not repaired.

## How the pictures compose

Six encodings, each shown once as a specimen and used nowhere else in any other sense: a **set of values** is
filled cells on a line; a **set of states** is filled cells on the `(x, y)` grid; **membership** is a ring (one run
state) sitting in a filled cell, dark red if it ever sits in an empty one; **containment** is the set we have
(solid) over the set we claim (pale), a dark-red cell being a state we have that the claim excludes; **the measure
decreases** is a (before, after) dot plot strictly below the diagonal; **trusted vs. derived** is a dotted `eval`
tag on leaves the evaluator settled versus the rule name on the dock that derives the next panel.

Composition is docking: SEQ draws the shared panel once (the page shows the two parts, then the merged picture);
SUB re-draws an output panel over a larger set; WHILE overlays the body's last panel onto the head and joins them
with the back-edge ribbon; FUN projects the last panel onto the result strip. Euclid's derivation is three rows
(enter, loop, exit) with overlays at the three places the proof argues. A mismatch keeps the shape: the dock turns
dark red, the overlay shows dark-red cells, the ribbon is tinted. Four seeded mistakes: `return y` (exit overlay);
the one-sided invariant `CD(a,b) ⊆ CD(x,y)` (preserved and established, but nine exit candidates); the guard on
`x` (a body input state where `x mod y` is undefined); and `I ∧ y ≤ x` (fails only when `a < b`, so the slice can
be calm while the all-slices check refuses 528 of 1089). Panels are filled from the derivation first; the run
slider then adds a navy ring moving through them, one state inside sets already proved. Changing `a` or `b`
refills every panel in place, so cells tween and the types read as functions of the inputs.

## Mapping onto Codillon

Codillon draws one instruction per line, types as shapes to the left of the code, dataflow as pale ribbons and a
sticky step slider. The calculus fits that frame with little new vocabulary:

- **Per line, one panel.** Each Wasm instruction is an ASSIGN on the state (locals plus stack slots). Its fraction
  gains a *state panel* in the margin: the set of states after this line, computed as the exact image of the panel
  above it. Straight-line code is SEQ, so adjacent panels are the same set and need no connector beyond the
  existing ribbon.
- **The stack is part of the state.** `local.get $y; local.get $x; local.get $y; i32.rem_u; local.set $y;
  local.set $x` is the calculus' `x, y := y, x mod y` spread over six lines; the intermediate panels are projections
  of a state with two stack slots onto two chosen coordinates, with the others listed. Codillon's per-slot value
  display is the ring in the panel.
- **The loop bracket carries the invariant.** Codillon already brackets `loop … end` with a pale frame and marks a
  taken loop with a circle. The frame gains the invariant panel at its head, the overlay at `br $loop` (the back
  edge, with the ribbon to the head), and the measure triangle on the frame line; `br_if $done` splits the head
  panel into continue and exit panels.
- **The contract is the function header's fraction.** The result strip sits where the header's output shape is;
  the divisor rows are its hover zoom.
- **Failure and evidence keep Codillon's idiom.** A dark-red overlay cell is the spec-level bad connection, with
  `⚖` in the gutter and the premise as the commentary label; the step slider moves the ring, which is never a
  verdict; the six states of 05 apply, with the all-slices check pending drawn as "unknown".

The checker is enumeration today, which is enough for Codillon's teaching range; with an SMT backend for i32 the
derivation tree, the pictures and the docking grammar would not change.
