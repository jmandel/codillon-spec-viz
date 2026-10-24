# Implementing Refined Codillon in the real editor

Started 2026-10-23. Fork: https://github.com/jmandel/codillon, branch `refined`, local clone `~/hobby/codillon-refined`.
Built editor is deployed into this repo at `editor/` so the walkthrough can embed live states and deep-link to them.

## What "real" means here (honest scope)
Codillon re-validates and re-runs the program on every keystroke. The cheapest *real* version of the design keeps that
loop and adds specifications that are **parsed, erased from the binary, and checked at run time** at well-defined
checkpoints, with failures drawn in Codillon's own idiom. That gives four of the six epistemic states for real:

| state | real in this implementation? |
|---|---|
| refuted, witness replayed | yes: a check failed on an actual run (yours, or a searched input) |
| refuted, not yet replayed | yes: an input search found a failing input that has not been loaded into the slider |
| held on this run only | yes: every check that passed, with a count |
| assumed / vacuous | yes: `(@assume …)` lines; a refinement that is syntactically `true` |
| unknown | only as "never reached on any run" (no checker ran) |
| proven | phase 5: verification conditions discharged by Z3 in the browser |

The editor must never draw "held on this run" like "proven".

## Phases (each ends with a local commit, a build, screenshots, and a coordinator review before push)

**Phase 1 — Deep links and embedding.**
- Load a program from the URL: `#ex=<name>` fetches `examples/<name>.wat` (relative to the page); `#src=<base64url of deflate-raw UTF-8>` carries the text inline. Also `step=<n|last|fail>` to position the slider after the run, and `embed=1` for iframe use (no page margins; post `{type:"codillon-height", height}` to `window.parent` on every layout change).
- A program loaded from a link must not overwrite the user's own saved program: save under `codillon_content:<link-hash>` instead of `codillon_content`.
- A small "share" affordance that copies a `#src=` link for the current text and step.
- No change in behaviour when the URL has no fragment.

**Phase 2 — Spec syntax, parsed and erased.** Follow `01-language-design.md` §1, with these decisions:
- Predicates name values by `$name` only (params, locals, named results, globals, `@define`d names). A refined result must be named: `(result $r (i32 | 0 <= $r))`. No bare `v`. (This resolves the binder inconsistency the Gemini review flagged.)
- Header sugar: `(param $n (i32 | P))`, `(result $r (i32 | P))`, `(local $x (i32 | P))`. Annotation lines, one per line: `(@requires P)`, `(@ensures P)`, `(@invariant P)`, `(@decreases e)`, `(@assert P)`, `(@assume P)`, `(@define name(a, b) = e)`, `(@ghost global $M (map i32 i32))` (phase 4).
- Predicate language as 01 §1.7: mathematical integers (no wraparound), signed reading of i32 by default, `u($x)`, `&& || ! ==>`, comparison chains, `+ - * / %` (Euclidean), `old(e)`, bounded `forall`/`exists`, `load(addr)` / `load8(addr)` for memory, calls to `@define`d functions.
- Spec lines are erased before compilation: annotation lines contribute nothing; header sugar becomes the plain type. Erasure must not change line numbering or Codillon's one-instruction-per-line structure.
- A malformed predicate is a *malformed line* (𝄞 with commentary), exactly like malformed code.
- Pure-Rust parser and evaluator with unit tests (`cargo test`).

**Phase 3 — Runtime checking and drawing.**
- Checkpoints: function entry (`requires`, param refinements), function exit (`ensures`, result refinements, `old`), loop-head arrival (`invariant`; `decreases` must strictly decrease and stay ≥ 0 between consecutive arrivals), `@assert` lines, and `local.set`/`local.tee` of a refined local.
- Implement by extending Codillon's instrumentation (the `codillon_debug` imports): the host needs the values of params, locals and memory at each checkpoint. Record what is missing; evaluate host-side.
- Drawing (Codillon idiom, see `11-real-codillon-comparison.md`):
  - gutter `⚖` on the spec line that failed, and on the instruction at which it was checked; precedence 💣 > 𝄞 > ⚖ > ✗ > number;
  - darkred commentary at the far right: the predicate with values substituted and the false conjunct marked, e.g. `r*r <= n : 46341·46341 = 2147488281 ≤ 2147483647 ✗`;
  - a darkred slider pill at each step where a check failed (distinct from the trap pill);
  - refined shapes: an i32 with a refinement is drawn 84×14 as a number line (linear |v| ≤ 8 across the middle 60%, log to the walls) with the admitted region shaded, fence posts (filled = inclusive, hollow = exclusive), a parity comb, and the runtime value as a dot; a value outside its region spills (darkred hatch over the rim);
  - "held on this run" is a slategray `∘N` next to a spec line; never a check mark.
- Spec lines themselves render like Codillon's meta lines (indigo) with their own gutter state.

**Phase 4 — Inputs and witnesses.**
- Let `$main` take parameters, with default arguments given by `(@run 10)` on the main header or `#args=` in the URL.
- Witness search: for a function with refined params, run it (in a worker or synchronously with a step budget) on edge inputs admitted by `requires` (0, 1, −1, 2, small squares, powers of two, INT_MAX, INT_MIN, values near the region's fences) and report the first failing input. Show it as a dashed ghost track above the slider (`⚖ input n = 0 · not replayed`); clicking loads it as the run (`refuted, replayed`).
- Ghost state: `(@ghost global $M (map i32 i32))` and `(@set $M := $M[$k -> $v])` executed host-side, enough for the hash table.

**Phase 5 — Proofs with Z3 (decided 2026-10-24: Z3 in the browser).** Replace "held on this run" with real verdicts
where the solver can decide them. Numeric witness search stays as a cheap first signal, but proofs are the answer.
- *Verification conditions, modularly.* For every function, symbolically execute the stack machine from its contract:
  params and memory arbitrary subject to `requires` (and param refinements, and the module invariant for exported
  functions), ghost state as SMT values. Loops are cut at `@invariant`: entry obligation, then an arbitrary state
  satisfying the invariant (havoc what the body writes), body, back-edge obligation, `decreases` obligation. Calls use the
  callee's contract (prove its requires, assume its ensures); `@define`s are unfolded; `@assert` is an obligation and then
  a fact; `@assume` is a fact. No histories of calls are ever needed: the hash table is proved one operation at a time from
  any state satisfying R.
- *Encoding.* Machine values are 32-bit bitvectors with exact Wasm semantics (wraparound, signed/unsigned compares,
  traps as obligations: division by zero, out-of-bounds memory). Spec terms are mathematical integers, linked by the signed
  or `u()` reading. Memory is an SMT array; loads and stores of the program's widths. Bounded quantifiers with constant
  bounds ≤ 64 are expanded; others are quantifiers with triggers. Ghost maps are a pair of arrays (domain, values).
- *Solver.* Z3 compiled to WebAssembly **single-threaded** (decided 2026-10-24), built by us with emscripten so it needs
  no SharedArrayBuffer and therefore no COOP/COEP headers or service worker on GitHub Pages; embedding pages need nothing.
  Interface: SMT-LIB2 text in, Z3's text out, in a Web Worker; budgets via `(set-option :rlimit N)` (deterministic, no
  timer thread); results cached by a hash of the obligation. Build script and patches: see the z3wasm README once it lands.
- *Verdicts and drawing.*
  - **proven** — silence (gray line number); runtime `∘N` counts are dropped for proven obligations.
  - **refuted** — the model is decoded into a concrete pre-state (params, locals at the loop head, memory slots, ghost map)
    and drawn as a witness of kind *contract state* ("allowed by the spec; may be unreachable: either the code is wrong or the
    spec is too weak"). If it is a function-entry state, it is replayable: run the function in a fresh instance with memory
    and globals set from the model, on the slider. Loop-head states are shown as a state card (one-iteration replay if feasible).
  - **unknown** (timeout, nonlinear, quantifiers) — indigo `?`, never darkred; runtime checks still run and show `∘N`.
  - the commentary names the obligation kind (precondition at call, postcondition, invariant on entry, invariant preserved,
    measure, no trap) and substitutes the model's values.
- *Targets.* parity: all proven; P1–P3 refuted with models. isqrt: proven with a `(@use …)` hint or by Z3's nonlinear
  arithmetic; S1 refuted at the loop head (`n = 2³¹−1, r = 46340`); S2, S3 refuted. triangle and triangle-bug. hash table:
  clean version proven (one operation at a time from R); (a), (b), (b′), (c), (d) refuted with contract-state models
  drawn as the 8 slots and the ghost map. gcd: proven if the solver can (with a lemma hint), otherwise honestly unknown.
- *Tests.* Natively, run the same VCs through Z3 (the `z3` crate or the z3 binary) in `cargo test`, so verdicts are
  regression-tested outside the browser.

**Phase 6 — Walkthrough integration.** Example files for every walkthrough state in `editor/examples/`, the built editor
deployed at `editor/`, and the walkthrough's lessons switched to live `<iframe>`s (embed mode) with "open in editor ↗" links
that open the same state in a new tab. The simulated listings stay only where the real editor cannot yet show something
(holes with suggestion chips, lenses), and the page says so.

## Build
`PATH=~/.cargo/bin:$PATH RUSTFLAGS='--cfg getrandom_backend="wasm_js"' ~/hobby/.agent-scratch/codalon-viz/tool/bin/trunk build --release --public-url /codillon-spec-viz/editor/`
then copy `dist/` to `codalon-dependent-viz/editor/`. Screenshots: `tools/codillon-shot.mjs` (extend it to use `#ex=`).
