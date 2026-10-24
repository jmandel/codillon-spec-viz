# Codillon with refinement types: a visualization study

Live site: https://joshuamandel.com/codillon-spec-viz/ (GitHub Pages from `main`). Source: https://github.com/jmandel/codillon-spec-viz

Started 2026-10-23. Question: if Codillon (Keith Winstein's structured WebAssembly editor for Stanford's
CS 10N) grew refinement/dependent types grounded Lean-style, how should the editor *draw* specification
adherence so that a spec bug is as visually obvious as a type error is today?

This repository holds only the investigation: the research write-ups, the language sketch, the shared sample programs
and fixture, and the ten prototypes. Codillon itself lives at https://github.com/codillon/codillon and is not vendored here.

## Layout
- `research/` — the study, in reading order:
  - `00-codillon-today.md` — what Codillon draws today (types as shapes, dataflow curves, gutter glyphs, slider).
  - `01-language-design.md` — the refinement-typed language sketch: `(T | P)` types, `(@invariant)`, `(@decreases)`,
    `(@ensures)`, proof-step lines, ghost state, memory regions; obligations per instruction; Lean grounding.
  - `02-prior-art-visualization.md` — survey of proof-assistant IDEs, auto-active verifiers, live programming,
    model finders; synthesized principles and primitive catalog.
  - `03-sample-programs.md` + `fixture.json` — the shared programs (parity, isqrt, gcd, pow_mod, 8-slot hash table),
    their specs, per-line obligations, seeded bugs with executed counterexample traces.
  - `04-requirements-and-bug-taxonomy.md` — inferred design values, 15 failure modes, 10-criterion rubric.
  - `05-ten-visualization-ideas.md` — the ten concepts and the six-state status model all prototypes share.
  - `06-artifact-brief-shared.md` — the contract every prototype follows.
  - `07-review-notes.md` — coordinator review of each prototype with the builders' rubric self-scores.
  - `08-synthesis.md` — the summative write-up: vision, verdicts, recommended composition, open questions.
  - `09-walkthrough-design.md` — the spec for the single-page walkthrough.
- `artifacts/00-refined-codillon.html` — the tutorial walkthrough of the composed design (start here).
- `artifacts/gcd-as-a-type.html` — worked example: Euclid typed by Gcd(a, b), with the Lean proof in `proofs/`.
- `editor/` — live build of the Refined Codillon fork (github.com/jmandel/codillon, branch `refined`).
- `artifacts/01-…html` to `10-…html` — the ten competing prototypes. Open any from `file://`.
- `tools/` — the Python interpreter / spec checker / fixture generator used to produce the traces.

## Reviewing the prototypes
Each page has the same five sections: legend → primitive in isolation → isqrt (or gcd) with a step slider and a
"seed bug" control → hash table with the same → self-critique. Score with the rubric in `04-…` §4.
