# tools — how the sample programs and fixture were produced

Everything in `research/03-sample-programs.md` and `research/fixture.json` was *executed*, not just written.

- `*.rwat` — the refinement-annotated WAT listings (parity, isqrt, gcd, powmod, hash). One instruction or
  annotation per line; line numbers are the ones cited everywhere else.
- `erase.py` — strips refinements and `(@…)` lines to plain WAT (line numbers preserved).
- `interp.py` — a small line-oriented interpreter for the Wasm subset with i32 wraparound, traps, a step limit,
  and hooks for spec checks; `specs.py` holds the predicate checks for each program; `apply_edits` seeds bugs.
- `bugs.py`, `bugmeta.py` — the seeded-bug edits and their metadata (counterexamples, failing obligations).
- `run.py`, `show.py`, `xcheck.py`, `runwasm.mjs` — run a program/bug, print a trace, and cross-check results
  against V8 (Node) on the erased WAT compiled with Binaryen's `wasm-opt`.
- `test_correct.py`, `test_bugs.py`, `test_more.py` — the checks that were run: correct versions pass every spec
  clause on edge values and random inputs; each seeded bug fails exactly as documented.
- `gen.py`, `data.py`, `build_fixture.py`, `assemble.py` — regenerate the fixture and the markdown document:

```sh
cd tools && python3 build_fixture.py && python3 assemble.py
```

Requires Python 3 only; the V8 cross-check additionally needs Node and `wasm-opt` on PATH.
