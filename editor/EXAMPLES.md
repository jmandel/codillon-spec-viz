# Refined Codillon editor (live build)

Built from https://github.com/jmandel/codillon/tree/refined (fork of codillon/codillon, LGPL-2.1).
Open an example: `editor/#ex=<name>` — add `&step=fail` to jump to the first failed check, `&embed=1` for iframes.

| example | shows |
|---|---|
| `parity` | everything holds (6, then 7) |
| `parity-p1` | gate inverted: `@assert` and `$half`'s precondition fail at the call |
| `parity-p2` | `shr_u`: `$half`'s ensures fails with 2147483646 |
| `parity-p3` | spec bug: `$h < $x` fails at 0 |
| `isqrt` | all checks hold; invariant and measure ∘N |
| `isqrt-s1` | signed compare; passes on this run (the failing input is beyond the step budget) |
| `isqrt-s2` | spec bug: ensures fails at n = 4 |
| `isqrt-s3` | invariant and measure fail on loop entry at n = 0 |
| `gcd`, `gcd-g1`, `gcd-g3` | correct; trap; invariant fails on entry |
| `triangle`, `triangle-bug` | refined local; a `local.set` outside its type spills |
| `spec-errors` | a malformed predicate (𝄞) and an unknown name (✗) |
| `hashtable` | spec lines parse; ghost-map checks show "? not checked" until phase 4 |
