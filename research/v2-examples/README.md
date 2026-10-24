# v2 examples: the kernel's test oracle

These are the shared programs from `../03-sample-programs.md`, rewritten in Refined Codillon v2 syntax
(`../16-v2-design.md`): proofs as values in a fact lane, `prove k`, lemmas and axioms, predicates as Wasm functions,
and functional specs as harnesses that end in `unreachable`. Each `X.wat` comes with `X.expect.json`, which lists
**every cup** the kernel must report and the verdict it must give. The cups were derived by hand, using only the
rule cards R1–R35 and the decision procedure of §3.

## Inventory

| file | what it shows | cups | verdicts |
|---|---|---|---|
| `parity.wat` | evenness gate, `$half` precondition, `$hon_ok` relational result | 6 | 6 proven |
| `parity-missing-proof.wat` | **missing proof**: `prove 1` deleted in `$half` | 6 | 5 proven, 1 runtime-checked |
| `parity-bug-gate.wat` | code bug P1: gate inverted | 6 | 4 proven, 2 runtime-checked (both refuted by runs) |
| `isqrt.wat` | loop invariant as block type, refined local, monomial `r²`, harness | 9 | 9 proven |
| `isqrt-harness-bug.wat` | **spec bug**: harness computes in i32, `(r+1)²` wraps at r = 65535 | 9 | 8 proven, 1 runtime-checked (refuted at n = 2³²−1) |
| `isqrt-wrong-cup.wat` | **wrong proof**: a `prove` feeds the back-edge instead of `local.set` | 9 | 8 proven, 1 runtime-checked, plus a `prove has nothing to feed` line error |
| `gcd.wat` | `$gcd_ref` (recursive, measure), `unfold`, bounded `$is_gcd` predicate, 1 instructor axiom | 13 | 12 proven, 1 assumed |
| `gcd-bug-guard.wat` | code bug G1: guard on the wrong variable (div cup unfed) | 13 | 9 proven, 3 runtime-checked (2 refuted by runs), 1 assumed |
| `gcd-vacuous.wat` | **vacuous spec**: unsatisfiable harness precondition proves False without the axiom | 12 | 12 proven, flagged by the adequacy check |
| `primality.wat` | `$prime_spec` vs `$prime` (`d > n/d`), 3 measures, induction lemma, 3 instructor axioms | 30 | 18 proven, 12 assumed |
| `hashtable.wat` | 8-slot open addressing with tombstones; bounds on every load/store; `$rep_ok` over memory | 29 | 22 proven, 7 runtime-checked |
| `hashtable-stale.wat` | **wrong proof (stale fact)**: increment before the store | 29 | 21 proven, 8 runtime-checked (bounds cup refuted: OOB trap) |
| `hashtable-bug-tombstone.wat` | code bug: `$remove` writes 0, not a tombstone | 29 | 22 proven, 7 runtime-checked (2 refuted by runs) |

Axioms (all instructor-supplied, `axiom:` exports): `gcd_ref_is_gcd` (gcd.wat), `div_shrinks`, `sqrt_suffices`,
`nd_extend` (primality.wat; `nd_extend` is provable by induction in v2 and is an axiom only to keep the file short).
Lemmas with proofs: `lemma:from_agrees` (induction via `measure:from_agrees`), `lemma:prime_agrees`.

## `expect.json` format

```json
{ "source": "x.wat", "mode": "strict | gradual", "summary": "…",
  "cups": [ { "line": 36, "operand": 0, "kind": "ResultRefinement", "goal": "…", "verdict": "proven",
              "feed": { "by": "prove", "line": 35, "hyps": [ { "line": 31, "fact": "…", "origin": "…" } ] },
              "why": "…" } ],
  "runs": [ { "export": "harness:x", "expect": "pass" } ] }
```

- `line` is 1-based in the `.wat` file (erasure keeps line numbers). `operand` is the value operand the cup sits
  beside, in pop order (0 = deepest), or `null` for line-level cups (`False`, block/loop facts, measures).
- `kind` is `CupKind` from §4.3. `goal` is the proposition rendered with program names; `#x` is a canonical value id,
  `ε` a memory epoch.
- `verdict` is the kernel's static verdict in the file's `mode`. In strict mode a `runtime-checked` cup is an
  error; its text is in `strict_error`. `after_runs` gives the verdict after the recorded runs (refuted, with a witness).
- `feed.by` is `lookup` (with the matched fact), `prove` (the `prove` line and its hypotheses, top of lane first),
  `eval`, `dead` (ex falso after a branch), or `none`. Failed proves are in `prove_error`; stale facts in `stale_hint`.
- `assumptions` lists the axioms an `assumed` cup depends on; `adequacy` records vacuity results (§7.2).
- `runs`: `expect: "pass"` sweeps the standard input list and requires no trap at all; `"fails"` requires at least
  one trap; with `args`, the exact outcome (`ok`, `unreachable`, `div-by-zero`, `oob`). `domain: [lo, hi]` maps inputs
  into a range at run time only (slow spec predicates); the theorem is still for all inputs.

## Validation

```sh
node tools/run.mjs            # all examples; or name expect files
```

`tools/run.mjs` erases each file with `tools/erase.py` (same line count, asserted), assembles it with
`wasm-tools parse`, runs `wasm-tools validate`, instantiates it in Node, and runs every harness on 338–589 inputs
(edge values, then a deterministic xorshift sample). Erased files go to
`~/hobby/.agent-scratch/codalon-viz/v2design/erased/`. Last run: all 13 files erase, parse and validate; every correct
program's harness passes on all inputs; every bug variant fails on its recorded input.

The runs check the erased program (no runtime checks inserted), so a gradual-mode check that would fire first is
reported as a trap further on (for example `gcd-bug-guard` traps at `rem_u`, which is exactly the runtime-checked cup).

## What the runs do not check

The static verdicts are hand-derived, not machine-checked: there is no kernel yet (phase C). The derivations are in
each cup's `why`. They are the oracle the kernel must reproduce; where the kernel disagrees, either the kernel or a rule
card is wrong, and the disagreement should be resolved in `16-v2-design.md` first.
