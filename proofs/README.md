# Machine-checked proofs

`EuclidGcd.lean` — Euclid's algorithm whose return type *is* its specification:
`Gcd a b := { g : Nat // ∀ d, d ∣ g ↔ d ∣ a ∧ d ∣ b }` (a number whose divisors are exactly the common divisors).
Core Lean only, no Mathlib. Check with:

```sh
cd proofs && lean EuclidGcd.lean     # prints 4, 21, 0 from the #evals; no errors
```
Toolchain pinned in `lean-toolchain` (Lean 4.35.0).

`minimal/` — the same theorem in a five-rule calculus where types are finite sets of states (variables in 0..32).
`node minimal/check-euclid.cjs 32` checks the derivation on all 1089 (a, b) slices and confirms that four seeded mistakes are refused; see `minimal/output.txt`.
