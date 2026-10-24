# Task: visualize "gcd(a, b) as a type" in a refinement type system (one of ten parallel explorations)

## Context
We are designing visualizations for a refinement-typed version of Codillon (Keith Winstein's structured WebAssembly
editor for Stanford's intro course). In a refinement type system a type is a SET of values, a refinement `{v : T | P(v)}`
is a subset, a dependent type is a family of sets indexed by other values, subtyping is set containment, and a value
of a refined type is a value plus evidence that P holds (the evidence is erased at run time).

The running example: Euclid's algorithm with its output typed as "the gcd of the inputs". The simplest honest type is

    Gcd(a, b) = { g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }        (Div(n) = set of divisors of n; Div(0) = all of ℕ)

equivalently { g | g ∣ a ∧ g ∣ b ∧ ∀d. d ∣ a ∧ d ∣ b → d ∣ g }. It has exactly one inhabitant: the gcd. Euclid's loop
(x, y) → (y, x mod y) never changes Div(x) ∩ Div(y), and when y = 0 the common divisors are Div(x), so x inhabits the type.
Machine-checked in Lean: https://github.com/jmandel/codillon-spec-viz/blob/main/proofs/EuclidGcd.lean

The bar: a reader should come to DEEPLY UNDERSTAND THE TYPE by visually parsing the picture, not by reading prose.
Every figure must pass a "prose-off" test: with only in-figure labels, it conveys its claim (what the set is, what is in
or out, what depends on what, what would be a type error).

## Your deliverables (in your current working directory only)
1. 4–6 standalone SVG files `fig-1.svg`, `fig-2.svg`, … that develop YOUR ASSIGNED ANGLE (below) from simplest to
   richest. At least:
   - one figure for a = 12, b = 8 (gcd 4);
   - one for a second pair you choose that shows something new (e.g. 1071, 462 → 21; 21, 0 → 21; 0, 0 → 0; coprime 13, 8 → 1);
   - one figure that shows a TYPE ERROR in your visual language (a wrong candidate such as g = 2 or g = 8 for (12, 8),
     or a buggy program returning the wrong value), drawn so the error is obvious without prose.
2. `notes.md` (300–700 words): your angle in one sentence; the visual encoding (each mark → its meaning); for each figure
   the one-sentence claim a newcomer should read off it with prose hidden; what this angle makes obvious that others
   don't; its weaknesses or where it misleads; how it could live inside Codillon's per-instruction editor display.
3. When completely finished, write `DONE.txt` containing one line: the number of figures.

## SVG rules
- Static, self-contained SVG 1.1 (no scripts, no external fonts/images/links). `viewBox` set; width 900, height 400–800.
- Palette (no green anywhere): background #fffff0 (ivory); ink #222; type/region purple #6A5ACD and its muted fill
  #d9d5f2; dark red #8b0000 ONLY for a violation / type error; indigo #4b0082 only for "unknown"; navy #00008b for a
  concrete run or value; grays for context. Fonts: font-family="Georgia, 'Times New Roman', serif" for math and labels,
  "Arial Narrow, Arial, sans-serif" for small annotations (≥ 11 px).
- Every number must be COMPUTED correctly. Use python3 to compute divisor sets, gcds, lattices, etc., and generate the
  SVG programmatically (write a generator script `gen.py` in your directory; keep it).
- Direct labels, no legend tables. A title line inside each SVG stating its claim in ≤ 12 words.
- Quality check before you finish: validate each file with `xmllint --noout fig-N.svg`, render each to PNG with
  `rsvg-convert -w 1400 fig-N.svg -o fig-N.png`, LOOK AT the PNGs (you can read images), and fix overlaps, clipping,
  illegible text, and any wrong number. Iterate at least twice.
- Do not touch anything outside your working directory. Do not use git. Do not start servers.

## YOUR ASSIGNED ANGLE (08 of 10)
DEPENDENT TYPE FAMILY. The type is a function of (a, b): draw the (a, b) plane (e.g. 0..40 × 0..40) colored or marked by gcd(a, b) (a heat/structure map), and pull out FIBERS: for a chosen (a, b) the fiber is the singleton set Gcd(a,b) drawn on its own number line. Show families: fix b and vary a (Gcd(a, 8) as a function of a), showing how the singleton moves. Explain visually that a dependent type is a family of sets indexed by values, and that a function returning Gcd(a,b) must land in the fiber over its own inputs. Show a type error as a result landing in the wrong fiber.

Your working directory is /home/jmandel/hobby/.agent-scratch/codalon-viz/gcdviz/08 . Begin by writing gen.py there.
