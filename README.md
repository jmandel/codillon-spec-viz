# Codillon with refinement types: a visualization study

Live site: https://joshuamandel.com/codillon-spec-viz/ (GitHub Pages from `main`). Source: https://github.com/jmandel/codillon-spec-viz

Started 2026-10-23. Question: if Codillon (Keith Winstein's structured WebAssembly editor for Stanford's
CS 10N) grew refinement/dependent types grounded Lean-style, how should the editor *draw* specification
adherence so that a spec bug is as visually obvious as a type error is today?

This repository holds only the investigation: the research write-ups, the language sketch, the shared sample programs
and fixture, and the ten prototypes. Codillon itself lives at https://github.com/codillon/codillon and is not vendored here.

## Version 2: proofs as values

The study's current design. Version 1 (below) wrote specifications as annotations beside the code, checked them at run
time and proved them with Z3. Version 2 makes proofs Wasm values in a **fact lane** (a comparison followed by `if` or
`br_if` gives each arm a fact; every proposition an instruction needs is a cup fed by exactly one fact), uses refined
block and function types as the only spec syntax, has `unreachable` consume a proof of False (so a harness ending in
`unreachable` is a functional spec), discharges arithmetic with `prove k` and a small deterministic decision procedure,
treats predicates and lemmas as Wasm functions, and checks everything with a kernel that has no Z3 and no "unknown".
A vericoding mode lets an LLM write bodies and proofs against a spec the student owns.

- `research/15-input-proofs-as-values.md` — why: the design conversation that started v2.
- `research/16-v2-design.md` — what: fact lane, rule cards R1–R35, the decision procedure, the four verdicts,
  vericoding mode, limits.
- `research/18-annotations-to-proofs-as-values.md` — why v1 was replaced: what it did well, what it bent, what v2
  changes and costs, the same isqrt in both syntaxes, and what is not done yet.
- `research/16-review-fable.md`, `research/17-kernel-review-fable.md` — independent reviews of the design and of the
  kernel (soundness holes and blocking bugs B1–B5, all fixed).
- `research/v2-examples/` — the shared programs in v2 syntax with seeded bugs; each `.expect.json` lists every cup's
  verdict (the kernel's test oracle, 201/201).
- `editor/v2/` — live build of the v2 kernel in the editor (github.com/jmandel/codillon, branch `proofs`); its
  visualization is in progress. Deep links: `editor/v2/#ex=v2/parity&step=last`, `editor/v2/#ex=v2/isqrt&step=last`,
  `editor/v2/#ex=v2/gcd-bug-guard&step=fail`.

## Version 1 (first iteration)

Everything below is the first iteration, kept as its record. `research/08-synthesis.md` now opens with a pointer to v2.

### Layout
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
  - `10-gemini-review.md`, `11-real-codillon-comparison.md`, `12-implementation-plan.md`, `13-gcd-as-a-type.md`, `14-minimal-calculus.md`.
  - `15`–`18` and `v2-examples/` — version 2 (see above).
- `artifacts/00-refined-codillon.html` — the tutorial walkthrough of the composed design (start here).
- `artifacts/gcd-as-a-type.html` — worked example: Euclid typed by Gcd(a, b), with the Lean proof in `proofs/`.
- `artifacts/gcd-type-gallery.html` — ten audited visual angles on Gcd(a, b) as a type, consolidated; sources in `research/gcd-gallery/`.
- `artifacts/gcd-foundations.html` — the same example in a five-rule calculus (types as finite sets of states) with an in-page proof checker; standalone checker in `proofs/minimal/`.
- `artifacts/real-editor.html` — write-up of the real editor: six live demos (deep links), verdicts, how the proofs work.
- `editor/` — live build of the v1 Refined Codillon fork (github.com/jmandel/codillon, branch `refined`).
- `artifacts/01-…html` to `10-…html` — the ten competing prototypes. Open any from `file://`.
- `tools/` — the Python interpreter / spec checker / fixture generator used to produce the traces.

### Reviewing the prototypes
Each page has the same five sections: legend → primitive in isolation → isqrt (or gcd) with a step slider and a
"seed bug" control → hash table with the same → self-critique. Score with the rubric in `04-…` §4.
