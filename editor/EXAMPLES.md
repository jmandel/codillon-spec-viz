# Refined Codillon editor: examples

Live build of https://github.com/jmandel/codillon/tree/refined (a fork of codillon/codillon, LGPL-2.1).
Each name opens the editor on that program. Correct programs open at the last step; bugs open at the first failed check.
Deep-link format: `editor/#ex=<name>`, plus `&step=<n|last|fail>`, plus `&embed=1` for iframes.

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
| [isqrt-s1](./#ex=isqrt-s1&step=fail) | bug, passes this run | signed compare; the failing input needs ~695,000 steps (phase 4 searches for it) |
| [isqrt-s2](./#ex=isqrt-s2&step=fail) | spec bug | < and <= swapped in the spec: ensures fails at n = 4 |
| [isqrt-s3](./#ex=isqrt-s3&step=fail) | bug | search starts at r = 1: invariant and measure fail on loop entry at n = 0 |
| [gcd-g1](./#ex=gcd-g1&step=fail) | bug | guard tests the wrong variable: remainder by zero (💣) |
| [gcd-g3](./#ex=gcd-g3&step=fail) | spec bug | invariant y <= x is never established on entry |
| [triangle-bug](./#ex=triangle-bug&step=fail) | bug | loop guard off by one: a refined local is set outside its type and spills |
| [spec-errors](./#ex=spec-errors&step=fail) | spec syntax | a malformed predicate (𝄞) and an unknown name (✗) |
| [hashtable](./#ex=hashtable&step=fail) | partial | all spec lines parse; ghost-map checks show "? not checked" until phase 4 |

Back to the study: [codillon-spec-viz](../)
