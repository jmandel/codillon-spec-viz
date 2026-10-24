# gcd as a type: ten explorations

Raw material behind `artifacts/gcd-type-gallery.html`.

- `preamble.md` — the shared brief; `NN/PROMPT.md` — the full prompt each agent received (preamble + its angle).
- `NN/fig-*.svg`, `NN/notes.md`, `NN/gen.py` — each agent's original output, unmodified. Made with the pi CLI:
  Gemini 4 Argon for 01–04 and 06–10, Gemini 3.1 Pro for 05 (Argon kept stalling on that angle).
- `audit.md` — number-by-number audit of every figure (errors found, fixes, captions added).
- `build/fixes/NN.py` — scripted corrections applied to copies of the SVGs; `build/regen/gen05.py` — the redraw of
  angle 05; `build/build.py` and friends assemble the gallery page.

Angles: 01 divisibility lattice · 02 divisor strips · 03 prime-exponent boxes · 04 Euclid's rectangle tiling ·
05 state-space invariant · 06 nested predicate regions · 07 Bézout / ideal · 08 dependent type family ·
09 typing derivation · 10 Codillon editor idiom.
