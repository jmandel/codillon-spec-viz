# Refined Codillon editor: examples

Live build of https://github.com/jmandel/codillon/tree/refined (a fork of codillon/codillon, LGPL-2.1).
Each name opens the editor on that program. Correct programs open at the last step; bugs open at the first failed check.

**Proofs.** Every obligation is also sent to Z3 (single-threaded WebAssembly, loaded on first use, runs in a worker). Proven lines are silent; refuted lines get ⚖ with the solver's counterexample state (replayable when it is a function-entry state); undecided lines get an indigo `?`. Across these examples: 419 obligations, 398 proven, 20 refuted, 1 undecided (`cubes`, on purpose). The hash tables take about 30 s to prove in the browser; small programs take under 2 s.
Deep-link format: `editor/#ex=<name>`, plus `&step=<n|last|fail>`, `&args=1,2` for `$main`'s arguments, `&embed=1` for iframes (`&fit=1` scales to the frame).

| example | kind | what it shows |
|---|---|---|
| [hello](./#ex=hello&step=last) | correct | plain program, no specs: today's Codillon, unchanged |
| [parity](./#ex=parity&step=last) | correct | halves 6, then 7; every check holds |
| [isqrt](./#ex=isqrt&step=last) | correct | isqrt(10) = 3; invariant and measure ∘4, ensures ∘1 |
| [gcd](./#ex=gcd&step=last) | correct | gcd(12, 8); the result's type depends on $a and $b |
| [triangle](./#ex=triangle&step=last) | correct | a refined local (local $i (i32 | 0 <= $i <= $n)) drawn as a number line |
| [parity-p1](./#ex=parity-p1&step=fail) | bug | gate inverted: @assert and $half's precondition fail at the call |
| [parity-p2](./#ex=parity-p2&step=fail) | bug | shr_u instead of shr_s: $half's ensures fails with 2147483646 |
| [parity-p3](./#ex=parity-p3&step=fail) | spec bug | the code is right, the spec is wrong: $h < $x fails at 0 |
| [isqrt-s1](./#ex=isqrt-s1&step=fail) | bug, passes this run | signed compare; the input search finds $isqrt(2147483646), which fails at step 695,119, beyond the 100,000-step budget (shown honestly) |
| [isqrt-args](./#ex=isqrt-args&args=26&step=last) | correct | $main takes an argument: change args= in the URL (here isqrt(26)) |
| [isqrt-s2](./#ex=isqrt-s2&step=fail) | spec bug | < and <= swapped in the spec: your run (n = 10) holds; the input search finds n = 0 (dashed track above the slider; click to replay) |
| [isqrt-s3](./#ex=isqrt-s3&step=fail) | bug | search starts at r = 1: invariant and measure fail on loop entry at n = 0 |
| [gcd-g1](./#ex=gcd-g1&step=fail) | bug | guard tests the wrong variable: remainder by zero (💣) |
| [gcd-g3](./#ex=gcd-g3&step=fail) | spec bug | invariant y <= x is never established on entry |
| [triangle-bug](./#ex=triangle-bug&step=fail) | bug | loop guard off by one: a refined local is set outside its type and spills |
| [spec-errors](./#ex=spec-errors&step=fail) | spec syntax | a malformed predicate (𝄞) and an unknown name (✗) |
| [hashtable](./#ex=hashtable&step=last) | correct, proven | the fixture sequence insert(3,30), insert(11,110), delete(3), lookup(11,−1); all 54 obligations proven one operation at a time from any state satisfying R (≈30 s) |
| [hashtable-a](./#ex=hashtable-a&step=fail) | bug | probe index not wrapped: probe invariant fails, then out-of-bounds trap |
| [hashtable-b](./#ex=hashtable-b&step=fail) | bug | lookup treats TOMB as EMPTY: $find's result check fails at step 241 (fixture numbering) |
| [hashtable-b2](./#ex=hashtable-b2&step=fail) | bug | delete writes EMPTY: R breaks at the delete |
| [hashtable-c](./#ex=hashtable-c&step=fail) | bug | insert skips the existing-key check: invariant k ∉ M fails |
| [hashtable-d](./#ex=hashtable-d&step=fail) | bug | load factor off by one: ensures R fails, then lookup probes until the 100,000-step budget |

Back to the study: [codillon-spec-viz](../)
