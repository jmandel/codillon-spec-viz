# 03 — Shared sample programs (refinement-annotated WAT) for the visualization prototypes

**Purpose.** Ten visualization prototypes will all draw the *same* programs, specs, proof obligations, and
counterexamples, so they can be compared side by side. This file is the single source for those programs:

- **Part A**: four small number-theoretic functions (parity gate, `isqrt`, `gcd`, `pow_mod`), each with a
  refinement spec, a per-line proof-obligation table, and 2–3 seeded bugs with concrete counterexamples.
- **Part B**: an 8-slot open-addressing hash table in linear memory (insert / lookup / delete with
  tombstones), an abstract ghost map `M`, a representation invariant `R`, and four seeded bugs (plus one variant).
- **Part C**: a JSON fixture holding all of the above (listings, refined signatures, obligations with status,
  and a step trace for each bug) for prototypes to embed verbatim.

**Everything here was executed, not just written.** Every listing was *erased* to plain WAT (refinements
stripped, spec lines turned into comments), validated with Binaryen `wasm-opt` v133, and run in V8 (Node 26).
A small line-level reference interpreter ran the same programs and also evaluated every spec clause at
runtime. For every scenario in this file, V8 and the interpreter return the same results and the same traps
(non-terminating runs were cut off by a timeout in both). The interpreter produced every step number, stack,
local, memory snapshot, and "first failing check" quoted below and in the fixture. Correct versions passed
every spec check on these inputs: hand-picked edge values (0, 1, ±small, INT_MAX, INT_MIN, perfect squares,
m = 1, m = 65536), 20–30 random inputs per Part A program, and 60 random 25-operation sequences for the hash
table. `isqrt` additionally passed n = 2147395599, 2147395600 and 2147483647 (≈695k steps each). Scripts are in
`~/hobby/.agent-scratch/codalon-viz/verify/` (scratch, not part of the repo).

**At a glance**

| program | lines (WAT + spec) | spec features shown | seeded bugs |
|---|---|---|---|
| A1 parity gate | 23 (22 + 1) | refined param (precondition), dependent result, path-sensitive refinement through `if` | P1 gate inverted (caller blamed) · P2 `shr_u` (subtle, negatives) · P3 "half < x" (**spec bug**, x = 0) |
| A2 `isqrt` | 27 (25 + 2) | loop invariant, `decreases`, overflow obligation | S1 signed compare (**subtle**, n ≥ 2147395600; non-termination at INT_MAX) · S2 `<`/`<=` swapped (**spec bug**, perfect squares) · S3 start at 1 (edge, n = 0) |
| A3 `gcd` | 29 (26 + 3) | recursive spec function, trap obligation (`rem_u` by 0) | G1 wrong guard variable (trap) · G2 do-while rewrite (**subtle**, b = 0 traps) · G3 invariant `y <= x` (**spec bug**, not established) |
| A4 `pow_mod` | 49 (45 + 4) | two-part invariant with modular algebra, unsigned-overflow bound | M1 acc not reduced (edge, m = 1) · M2 `rem_s` (**subtle**, m > 46341) |
| B hash table | 169 (139 + 30) | ghost map `M`, representation invariant `R` (5 clauses), probe-loop invariant, memory-safety obligations | (a) no wrap (OOB trap) · (b) TOMB treated as EMPTY in lookup (unreachable key) · (b′) delete writes EMPTY · (c) no existing-key check (duplicate) · (d) load-factor off by one (non-termination) |

---

## 1. Provisional refinement syntax

The syntax is a placeholder until the real one is chosen. It has two layers.

**(a) Refined value types, written inline wherever WAT puts a value type** (params and results):

| Form | Meaning |
|---|---|
| `(i32 \| P)` | an i32 whose value `v` satisfies predicate `P` |
| `(param $n (i32 \| 0 <= v))` | a precondition on one parameter: the caller must prove it, the body may assume it |
| `(result (i32 \| v * v <= n))` | a *dependent* result: `P` may name the parameters (`n`), and `v` is the returned value |

**(b) Spec lines `(@keyword ...)`**, one per editor line, written in WebAssembly's text-format *annotation*
syntax (the annotations proposal, which conforming parsers skip):

| Line | Where | Meaning / when a dynamic check fires |
|---|---|---|
| `(@requires P)` | right after the `(func` line | precondition; checked at the call (the *caller* is blamed) |
| `(@ensures P)` | right after the `(func` line | postcondition; `result` is the return value, `old(e)` the value at entry; checked when the function returns |
| `(@invariant P)` | directly after a `loop` line | holds every time control reaches the loop head: on entry, and after each `br` back to it |
| `(@decreases E)` | directly after a `loop` line | termination measure: `E >= 0` at every arrival and strictly smaller at every back-edge |
| `(@assert P)` | anywhere in a body | must hold when control passes this line |
| `(@ghost local $j i32)`, `(@ghost global $M (Map i32 i32))` | where `local`/`global` go | specification-only state with zero runtime cost; erased |
| `(@ghost j := j + 1)`, `(@ghost M := M[k := x])` | in a body | ghost update; "executes" when control passes |
| `(@define name(args) = expr)` | module level | spec function or predicate, such as `gcd`, `pow`, `st(s)`, `R` |

**Expression language.** Expressions range over mathematical integers. An i32 `x` denotes its *signed* value
unless written `u(x)` (unsigned). `+ - *` do not wrap. `%` is *Euclidean* modulo, so the result is in `[0, m)`
for `m > 0`: `-3 % 2 == 1`. Wasm's `i32.rem_s` gives `-1` there, and that difference is why the specs and the
code stay separate. `&` is bitwise on the two's-complement form. Other notation: `==>`, `&&`, `||`, `!`,
`forall`, `x in M`, `M[k]`, `M[k := v]`, `M \ {k}`, `|M|`, and `#{s | P}` (count).

**Erasure.** To get plain WAT that Codillon (and any Wasm tool) accepts, replace each `(T | P)` with `T` and
drop or comment out each `(@...)` line. Line numbers do not change, so every line number below refers to both
the refined listing and the erased program. Bugs that *delete* lines are applied by blanking those lines, which
also keeps the numbering.

**Codillon style.** One instruction per line. No folded forms. No `(module ...)` wrapper; Codillon edits the
module body directly. Locals are declared one per line. Indentation in the listings is cosmetic, because
Codillon draws frames itself. Only i32 is used, plus one page of linear memory in Part B. Spec lines are not
instructions, so a prototype should render them as annotation rows attached to the following
(`requires`/`ensures`/`invariant`) or current (`assert`/`ghost`) instruction line. **Unverified:** how
Codillon's line classifier treats a line that holds only an annotation. The `wast` crate ignores unregistered
annotations, so it may behave like a comment line, but an integration will want to recognize these lines
explicitly anyway.

**Proof-obligation status vocabulary** (used in the tables and the fixture):

| status | meaning |
|---|---|
| `none` | nothing to prove beyond ordinary Wasm typing |
| `auto` | follows from the refined types on the stack plus the current path condition (linear arithmetic or bit-vector facts); no annotation needed |
| `inv` | needs the loop invariant, or the hash table's representation invariant `R` |
| `lemma` | additionally needs a nonlinear, counting, or "unfold the definition once" lemma (a solver may or may not find it unaided) |
| `fails` | the obligation that a seeded bug breaks |

The **step** convention for traces: one step per executed instruction line. `block`, `loop`, `if`, `br*`,
`return` and `call` count; `else` and `end` do not. A `call` occupies two steps: *enter*, when the arguments
are popped, and *return*, when the result is pushed. `requires` checks attach to the call's enter step. For a
top-level call they attach instead to the callee's first step. `ensures` checks attach to the call's return
step, or for a top-level call to the callee's last step. Invariant and decreases checks attach to the `loop`
or `br` step that arrives at the loop head.

---
## Part A — small number-theoretic programs

### A1. Parity gate: `$is_even`, `$half`, `$half_or_neg1` (23 lines)

This is the smallest program in the set, and it introduces the central idea: *a value whose type says it is
even*. `$is_even` returns a flag refined by `x`. `$half` accepts only even inputs, and its parameter type
`(i32 | v % 2 == 0)` is a precondition. `$half_or_neg1` shows the *gate*: the `if` on the flag refines `x`
differently in each arm. In the else-arm, `x` has type `(i32 | v % 2 == 0)`, so the call to `$half` is
allowed there and nowhere else.

```wat
  1  (func $is_even (param $x i32) (result (i32 | v == (x % 2 == 0 ? 1 : 0)))
  2    local.get $x
  3    i32.const 1
  4    i32.and
  5    i32.eqz
  6  )
  7  (func $half (param $x (i32 | v % 2 == 0)) (result (i32 | v + v == x))
  8    local.get $x
  9    i32.const 1
 10    i32.shr_s
 11  )
 12  (func $half_or_neg1 (param $x i32) (result (i32 | (x % 2 == 0 && v + v == x) || (x % 2 == 1 && v == -1)))
 13    local.get $x
 14    call $is_even
 15    i32.eqz
 16    if (result i32)
 17      i32.const -1
 18    else
 19      (@assert x % 2 == 0)
 20      local.get $x
 21      call $half
 22    end
 23  )
```

Things to visualize: the "evenness" refinement *appears* at line 15/16 (it is a fact about `x` produced by a
test, not by an instruction that touches `x`), flows into the else-arm, and is *consumed* by the call on line 21.
The `(@assert ...)` on line 19 is optional; it only makes the arm's path condition visible.

**Proof obligations**

| lines | code | refined stack / facts after | obligation | status | why |
|---|---|---|---|---|---|
| 2–3 | `local.get $x; i32.const 1` | `[x, 1]` | - | **none** |  |
| 4 | `i32.and` | `[(i32 \| v == x & 1 && 0 <= v <= 1)]` | - | **none** |  |
| 5 | `i32.eqz` | `[(i32 \| v == (x & 1 == 0 ? 1 : 0))]` | post of $is_even: v == (x % 2 == 0 ? 1 : 0) | **auto** | bit-vector fact x & 1 == x % 2 (Euclidean %, also true for negative x) |
| 8–9 | `local.get $x; i32.const 1` | `[(i32 \| v == x && v % 2 == 0), 1]` | - | **none** | param refinement is assumed on entry |
| 10 | `i32.shr_s` | `[(i32 \| v == floor(x / 2))]` | post of $half: v + v == x | **auto** | arith. shift = floor division; with x even, 2*floor(x/2) == x |
| 13–14 | `local.get $x; call $is_even` | `[(i32 \| v == (x % 2 == 0 ? 1 : 0))]` | pre of $is_even: none | **auto** |  |
| 15 | `i32.eqz` | `[(i32 \| v == (x % 2 == 0 ? 0 : 1))]` | - | **none** |  |
| 16 | `if (result i32)` | `then: path x % 2 == 1 / else: path x % 2 == 0` | - | **auto** | the gate: the if refines x differently in each arm |
| 17 | `i32.const -1` | `[(i32 \| v == -1)]` | post (then-arm): x % 2 == 1 && v == -1 | **auto** |  |
| 19 | `(@assert x % 2 == 0)` |  | x % 2 == 0 | **auto** | path condition of the else-arm |
| 20–21 | `local.get $x; call $half` | `[(i32 \| v + v == x)]` | pre of $half: x % 2 == 0;  post (else-arm): x % 2 == 0 && v + v == x | **auto** | precondition discharged by the gate, not by $half |

**Seeded bugs**

| id | edit | kind | counterexample | runtime behaviour | failing obligation (static) | first dynamic check to fire |
|---|---|---|---|---|---|---|
| **P1** gate inverted | delete line 15 (`i32.eqz`) | ordinary code bug; the *caller* is blamed | `x = 3` → returns `1` (expected `-1`); `x = 4` → `-1` (expected `2`) | no trap; `$half(3)` computes `3 >> 1 = 1` | line 21, `pre of $half: x % 2 == 0`: the else-arm's path condition is now `x % 2 == 1` | step 8: `@assert` line 19; step 10: `requires` of `$half` at the call on line 21 |
| **P2** `shr_u` for `shr_s` | line 10: `i32.shr_s` → `i32.shr_u` | **subtle**: every even `x >= 0` is fine | `x = -4` → `2147483646` (expected `-2`); `x = INT_MIN` → `1073741824` | no trap; wrong (positive) answer | line 10, `post of $half: v + v == x`: `shr_u` yields `u(x)/2`, so `v + v == x + 2^32` for `x < 0` | step 15: `ensures` of `$half` (line 7) and of `$half_or_neg1` (line 12) |
| **P3** "half is smaller" | line 7: result `(i32 \| v + v == x)` → `(i32 \| v + v == x && v < x)` | **spec bug**: the program is right, the spec is wrong | `x = 0` → `0`, which is correct, but `0 < 0` is false; also every negative even `x` (`-4` → `-2 > -4`) | no trap; correct result | line 10, `post of $half` (the `v < x` conjunct) | step 15: `ensures` of `$half` (line 7) only. Fix the spec, not the code |

---

### A2. `$isqrt(n)`: integer square root by linear search (27 lines)

```wat
  1  (func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v <= n && n < (v + 1) * (v + 1)))
  2    (local $r i32)
  3    i32.const 0
  4    local.set $r
  5    block $done
  6      loop $grow
  7        (@invariant 0 <= r && r * r <= n)
  8        (@decreases n - r * r)
  9        local.get $r
 10        i32.const 1
 11        i32.add
 12        local.get $r
 13        i32.const 1
 14        i32.add
 15        i32.mul
 16        local.get $n
 17        i32.gt_u
 18        br_if $done
 19        local.get $r
 20        i32.const 1
 21        i32.add
 22        local.set $r
 23        br $grow
 24      end
 25    end
 26    local.get $r
 27  )
```

- **Spec**: `0 <= n` in, and the dependent result `v*v <= n < (v+1)*(v+1)` out.
- **Invariant** (line 7): `0 <= r && r*r <= n`.
- **Termination** (line 8): `n - r*r` stays `>= 0` (by the invariant) and drops by `2r+1 >= 1` on every
  back-edge. An equally valid measure is `46341 - r`.
- **Overflow hazard and how the spec exposes it.** Line 15 computes `(r+1)*(r+1)` in 32 bits. The invariant
  bounds `r` only by `r*r <= n <= 2^31-1`, so `r <= 46340`, and therefore `(r+1)^2 <= 46341^2 = 2147488281`.
  That value is **larger than `2^31-1 = 2147483647`** but **smaller than `2^32`**. A checker that must give
  the comparison on line 17 its mathematical meaning hits an obligation it cannot discharge for a *signed*
  compare: `(r+1)^2 <= 2^31-1` fails exactly when `r = 46340`, i.e. for `n >= 46340^2 = 2147395600`. The listing
  therefore compares **unsigned** (`i32.gt_u`, line 17). The obligation becomes `(r+1)^2 < 2^32`, which the
  invariant does give, and `u(n) == n` follows from `0 <= n`. Other correct fixes: tighten the precondition
  to `n < 2147395600`; compare `r + 1 > n / (r + 1)` with `i32.div_u`; or widen to i64. Bug **S1** below is
  the signed version.
- **Cost:** `isqrt(10)` takes 60 steps, but `isqrt(INT_MAX)` takes 695,115 steps, beyond Codillon's
  100k-step log. The overflow region **cannot be reached on the time-travel slider**; only the static
  obligation (or a counterexample-to-induction, see S1) can show it.

**Proof obligations**

| lines | code | refined stack / facts after | obligation | status | why |
|---|---|---|---|---|---|
| 3–4 | `i32.const 0; local.set $r` | `r == 0` | - | **none** |  |
| 6 | `loop $grow` |  | inv on entry: 0 <= 0 && 0*0 <= n;  measure n - 0 >= 0 | **auto** | uses param refinement 0 <= n |
| 9–11 | `local.get $r; i32.const 1; i32.add` | `[(i32 \| v == r + 1)]` | no signed overflow: r + 1 <= 2^31-1 | **lemma** | inv r*r <= n <= 2^31-1 gives r <= 46340 (nonlinear) |
| 12–14 | `local.get $r; i32.const 1; i32.add` | `[r+1, r+1]` | same as 9-11 | **lemma** |  |
| 15 | `i32.mul` | `[(i32 \| u(v) == (r+1)*(r+1))]` | no UNSIGNED overflow: (r+1)^2 < 2^32 | **lemma** | r <= 46340 => (r+1)^2 <= 2147488281 < 2^32. NB it CAN exceed 2^31-1 (r = 46340), so only an unsigned reading of v is faithful |
| 16–17 | `local.get $n; i32.gt_u` | `[(i32 \| v == ((r+1)^2 > n ? 1 : 0))]` | u(n) == n | **auto** | from 0 <= n |
| 18 | `br_if $done` | `taken: n < (r+1)^2 / fallthrough: (r+1)^2 <= n` | - | **auto** |  |
| 19–22 | `r := r + 1` | `r' == r + 1` | no signed overflow (as 9-11) | **lemma** |  |
| 23 | `br $grow` |  | inv preserved: 0 <= r' && r'*r' <= n;  measure: 0 <= n - r'^2 < n - r^2 | **auto** | r'^2 <= n is exactly the fallthrough path condition of line 18 |
| 26 | `local.get $r  (exit via br_if)` | `[(i32 \| v == r)]` | post: 0 <= r && r*r <= n && n < (r+1)^2 | **inv** | first two conjuncts from the invariant, the third from the taken branch at 18 |

**Seeded bugs**

| id | edit | kind | counterexample | runtime behaviour | failing obligation (static) | first dynamic check to fire |
|---|---|---|---|---|---|---|
| **S1** signed compare | line 17: `i32.gt_u` → `i32.gt_s` | **subtle**: correct for every `n < 2147395600` | `n = 2147483647` | no trap; **never terminates** (no i32 is signed-greater than INT_MAX). `n = 2147395600`, the smallest failing input, returns `289398` after ≈4.3M steps | line 17: the signed reading of line 15's product is faithful only if `(r+1)^2 <= 2^31-1`; at `r = 46340` the product `2147488281` wraps to `-2147479015`, so `gt_s` says "not greater" | step 695,119 (line 23 back-edge, `r = 46341`): invariant `r*r <= n` and `decreases` both fail. The fixture trace is the **counterexample-to-induction**: one iteration starting from the loop-head state `n = INT_MAX, r = 46340` (which satisfies the invariant) |
| **S2** strict/non-strict swapped | line 1: result `v * v <= n && n < (v+1)*(v+1)` → `v * v < n && n <= (v+1)*(v+1)` | **spec bug**: fails exactly on perfect squares | `n = 4` → `2`, which is correct, but `2*2 < 4` is false; also `n = 0, 1, 9, …` (`n = 5` passes) | no trap; correct result | line 26, `post: r*r < n`: the invariant gives `<=` and the exit gives `n < (r+1)^2`; nothing excludes `r*r == n` | step 45: `ensures` (line 1) at the final `local.get $r` |
| **S3** off-by-one start | line 3: `i32.const 0` → `i32.const 1` | **edge case**: only `n = 0` is wrong | `n = 0` → `1` (expected `0`) | no trap; wrong result. Every `n >= 1` is right, so tests on 1..100 pass | line 6, `inv on entry: 1*1 <= n`: only `0 <= n` is known | step 4 (`loop` entry): invariant and `decreases` (`0 - 1 < 0`) both fail |

---

### A3. `$gcd(a, b)`: Euclid's algorithm (29 lines)

```wat
  1  (@define gcd(x, y) = (y == 0 ? x : gcd(y, x % y)))
  2  (func $gcd (param $a (i32 | 0 <= v)) (param $b (i32 | 0 <= v)) (result (i32 | v == gcd(a, b)))
  3    (local $x i32)
  4    (local $y i32)
  5    (local $t i32)
  6    local.get $a
  7    local.set $x
  8    local.get $b
  9    local.set $y
 10    block $done
 11      loop $euclid
 12        (@invariant 0 <= x && 0 <= y && gcd(x, y) == gcd(a, b))
 13        (@decreases y)
 14        local.get $y
 15        i32.eqz
 16        br_if $done
 17        local.get $x
 18        local.get $y
 19        i32.rem_u
 20        local.set $t
 21        local.get $y
 22        local.set $x
 23        local.get $t
 24        local.set $y
 25        br $euclid
 26      end
 27    end
 28    local.get $x
 29  )
```

- **Spec**: the non-negative inputs `a`, `b` give `result == gcd(a, b)`, where `gcd` is the spec function on
  line 1 (`gcd(x, 0) = x`, `gcd(x, y) = gcd(y, x % y)`; note `gcd(0, 0) = 0`). The classical
  characterization is a lemma that follows from that definition, not the spec:
  `(result (i32 | v divides a && v divides b && forall d. (d divides a && d divides b) ==> d divides v))`.
  Prototypes that want a "why" story can show it as the meaning of `gcd(a, b)`.
- **Invariant** (line 12): `0 <= x && 0 <= y && gcd(x, y) == gcd(a, b)`. It is preserved by one unfolding of
  the definition, valid because `y != 0` past line 16.
- **Termination** (line 13): `decreases y`, since `0 <= x % y < y`.
- **The trap obligation**: `i32.rem_u` (line 19) traps on a zero divisor, Codillon's bomb glyph. Its
  precondition `y != 0` is discharged by the guard on lines 14–16, and it is the obligation that two of the
  three bugs break.

**Proof obligations**

| lines | code | refined stack / facts after | obligation | status | why |
|---|---|---|---|---|---|
| 6–9 | `x := a; y := b` | `x == a, y == b` | - | **none** |  |
| 11 | `loop $euclid` |  | inv on entry: 0 <= a && 0 <= b && gcd(a,b) == gcd(a,b);  measure b >= 0 | **auto** |  |
| 14–16 | `local.get $y; i32.eqz; br_if $done` | `taken: y == 0 / fallthrough: y != 0` | - | **auto** |  |
| 17–19 | `local.get $x; local.get $y; i32.rem_u` | `[(i32 \| v == x % y && 0 <= v < y)]` | no trap: y != 0;  u(x) == x and u(y) == y | **inv** | y != 0 from the guard at 16; non-negativity from the invariant |
| 20–24 | `t := x % y; x := y; y := t` | `x' == y, y' == x % y` | - | **none** |  |
| 25 | `br $euclid` |  | inv preserved: gcd(y, x % y) == gcd(x, y) == gcd(a, b);  measure 0 <= x % y < y | **lemma** | unfold the definition of gcd once (y != 0) |
| 28 | `local.get $x  (exit)` | `[(i32 \| v == x)]` | post: x == gcd(a, b) | **inv** | inv + exit condition y == 0 + gcd(x, 0) == x |

**Seeded bugs**

| id | edit | kind | counterexample | runtime behaviour | failing obligation (static) | first dynamic check to fire |
|---|---|---|---|---|---|---|
| **G1** guard tests the wrong variable | line 14: `local.get $y` → `local.get $x` | ordinary bug, shown as a trap | `gcd(12, 8)` | **traps** "integer divide by zero" (V8: "remainder by zero") at line 19, step 36, on the 3rd iteration (`x = 4, y = 0`). `gcd(0, 5)` instead returns `0` without trapping (expected `5`) | line 19, `no trap: y != 0`: the guard now proves `x != 0` | the trap itself (step 36); invariant checks before it all pass |
| **G2** do-while rewrite | delete lines 14–16; line 24: `local.set $y` → `local.tee $y`; line 25: `br $euclid` → `br_if $euclid` | **subtle edge case**: correct for every `b > 0` | `gcd(7, 0)` | **traps** at line 19 on step 9, the first iteration. `gcd(12, 8) = 4` as before | line 19, `no trap: y != 0`: on the first iteration `y == b`, and only `b >= 0` is known | the trap (step 9) |
| **G3** invariant too strong | line 12: `0 <= x && 0 <= y && …` → `0 <= y && y <= x && …` | **spec bug** (in a loop annotation): inductive, but not established on entry | `gcd(4, 6)` → `2`, which is correct | no trap; correct result | line 11, `inv on entry: b <= a`. Preservation does hold (`y' = x % y < y = x'`); Euclid's first iteration simply swaps a smaller `a` | step 6 (`loop` entry) only; the invariant holds at every later arrival (steps 18, 30, 42) |

---

### A4. `$pow_mod(b, e, m)`: square-and-multiply (49 lines)

```wat
  1  (@define pow(x, e) = (e == 0 ? 1 : x * pow(x, e - 1)))
  2  (func $pow_mod (param $b (i32 | 0 <= v)) (param $e (i32 | 0 <= v)) (param $m (i32 | 1 <= v && v <= 65536)) (result (i32 | 0 <= v && v < m && v == pow(b, e) % m))
  3    (local $acc i32)
  4    (local $base i32)
  5    (local $k i32)
  6    i32.const 1
  7    local.get $m
  8    i32.rem_u
  9    local.set $acc
 10    local.get $b
 11    local.get $m
 12    i32.rem_u
 13    local.set $base
 14    local.get $e
 15    local.set $k
 16    block $done
 17      loop $square
 18        (@invariant 0 <= acc && acc < m && 0 <= base && base < m && 0 <= k)
 19        (@invariant (acc * pow(base, k)) % m == pow(b, e) % m)
 20        (@decreases k)
 21        local.get $k
 22        i32.eqz
 23        br_if $done
 24        local.get $k
 25        i32.const 1
 26        i32.and
 27        if
 28          local.get $acc
 29          local.get $base
 30          i32.mul
 31          local.get $m
 32          i32.rem_u
 33          local.set $acc
 34        end
 35        local.get $base
 36        local.get $base
 37        i32.mul
 38        local.get $m
 39        i32.rem_u
 40        local.set $base
 41        local.get $k
 42        i32.const 1
 43        i32.shr_u
 44        local.set $k
 45        br $square
 46      end
 47    end
 48    local.get $acc
 49  )
```

- **Spec**: `0 <= b`, `0 <= e`, `1 <= m <= 65536`, and the result satisfies `0 <= v < m && v == b^e % m`.
- **Invariants** (lines 18–19): `acc` and `base` are reduced (`[0, m)`), `k >= 0`, and the accumulator
  equation `acc * base^k ≡ b^e (mod m)`.
- **Termination**: `decreases k`, since `k` is halved while `k > 0`.
- **Why `m <= 65536` and `rem_u`**: both products (lines 30, 37) multiply two values `<= m-1 <= 65535`, so
  they are `< 2^32` and an unsigned remainder is exact. They can exceed `2^31-1` (when `m > 46341`), so a
  signed remainder is not exact (bug M2). This is the same "unsigned saves you" pattern as `isqrt`.
- **Why `1 rem_u m`** on lines 6–8: when `m = 1`, the accumulator must start at `0`, not `1` (bug M1).

**Proof obligations**

| lines | code | refined stack / facts after | obligation | status | why |
|---|---|---|---|---|---|
| 6–9 | `acc := 1 rem_u m` | `[(i32 \| v == 1 % m)]` | no trap: m != 0 | **auto** | m >= 1 from the param refinement; note 1 % 1 == 0 |
| 10–13 | `base := b rem_u m` | `[(i32 \| v == b % m)]` | no trap: m != 0;  u(b) == b | **auto** |  |
| 14–15 | `k := e` | `k == e` | - | **none** |  |
| 17 | `loop $square` |  | inv on entry: 0 <= acc < m, 0 <= base < m, 0 <= k;  (acc * base^k) % m == b^e % m;  measure k >= 0 | **lemma** | (1 % m) * (b % m)^e == b^e (mod m) |
| 21–23 | `k == 0 ? br_if $done` | `taken: k == 0 / fallthrough: k > 0` | - | **auto** |  |
| 24–27 | `k & 1; if` | `then: k odd / else: k even` | - | **auto** |  |
| 28–30 | `acc * base` | `[(i32 \| u(v) == acc * base)]` | no unsigned overflow: acc * base < 2^32 | **lemma** | acc, base <= m - 1 <= 65535 so product <= 4294836225 < 2^32 |
| 31–33 | `rem_u m; acc :=` | `acc' == (acc * base) % m, 0 <= acc' < m` | no trap: m != 0 | **auto** |  |
| 35–37 | `base * base` | `[(i32 \| u(v) == base * base)]` | no unsigned overflow: base^2 < 2^32 | **lemma** | same bound as 28-30 |
| 38–40 | `rem_u m; base :=` | `base' == base^2 % m` | no trap: m != 0 | **auto** |  |
| 41–44 | `k := k shr_u 1` | `k' == floor(k / 2)` | u(k) == k | **auto** |  |
| 45 | `br $square` |  | inv preserved: acc' * base'^k' == acc * base^k (mod m);  measure 0 <= k' < k | **lemma** | odd k: acc*base*(base^2)^((k-1)/2); even k: acc*(base^2)^(k/2) |
| 48 | `local.get $acc  (exit)` | `[(i32 \| v == acc)]` | post: 0 <= acc < m && acc == b^e % m | **inv** | k == 0 so acc % m == b^e % m, and acc < m so acc % m == acc |

**Seeded bugs**

| id | edit | kind | counterexample | runtime behaviour | failing obligation (static) | first dynamic check to fire |
|---|---|---|---|---|---|---|
| **M1** accumulator not reduced | delete lines 7–8, so `acc` starts at `1` instead of `1 % m` | **edge case** `m = 1` | `pow_mod(5, 0, 1)` → `1`, outside `[0, 1)` | no trap; out-of-range result. `pow_mod(5, 3, 1)` happens to return the right `0`, yet the invariant still fails | line 17, `inv on entry: acc < m`: `1 < m` does not follow from `1 <= m` | step 10 (`loop` entry): invariant line 18; then `ensures` at step 14 |
| **M2** signed remainder | line 39: `i32.rem_u` → `i32.rem_s` | **subtle**: correct whenever `m <= 46341` | `pow_mod(49999, 4, 50000)` → `17025` (expected `1`) | no trap; wrong result. `49999^2 = 2499900001` wraps to `-1795067295`, and `rem_s` gives `base = -17295`. (`pow_mod(49999, 2, 50000)` returns the correct `1` because the two wrap errors cancel mod 50000, but the invariant still fails) | line 39 → inv line 18 `0 <= base`: `base*base` can exceed `2^31-1`, so the signed remainder can be negative | step 30 (2nd arrival at the loop head): both invariants (lines 18, 19); `ensures` at step 76 |

---
## Part B — open-addressing hash table in linear memory (169 lines: 139 WAT + 30 spec)

### B.1 Design decisions (fixed, so every prototype draws the same picture)

| Decision | Choice | Why |
|---|---|---|
| Capacity | `CAP = 8` slots (power of two) | small enough to draw every slot |
| Slot layout | 12 bytes: `+0` state (`0` EMPTY, `1` FULL, `2` TOMB), `+4` key, `+8` value | as specified in the brief |
| Table address | `BASE = 65440`, so slot `s` is at `65440 + 12*s` and the table ends exactly at the end of the single 64 KiB page | an unwrapped probe index 8 then addresses byte 65536 and **traps** (bug a). With `BASE = 0` it would silently read and write outside the table instead |
| Hash | `h(k) = k & 7` (low 3 bits) | collisions are visible by eye: keys congruent mod 8 collide (3, 11, 19, -5, …). Works for negative keys (`-5 & 7 = 3`). A multiplicative hash such as `(k * 0x9E3779B1) >>u 29` would only change `h`; nothing else in the spec changes. **The seeded collision is A = 3, B = 11: `3 & 7 = 11 & 7 = 3`.** |
| Probing | linear: `at(k, d) = (h(k) + d) & 7` | as specified |
| Counter | one global `$used` = number of non-EMPTY slots (FULL + TOMB) | the quantity that controls termination, see B.2 |
| Delete | writes TOMB; `used` unchanged | a TOMB keeps probe paths intact |
| Insert | `$find` first: if the key exists, update its value in place. Otherwise refuse when `used >= CAP-1`, else write into the first EMPTY slot on the probe path | **never reuses tombstones**. This simplification costs capacity: every insert of an absent key, including re-inserting a deleted key, uses up an EMPTY slot for good, so after 7 such inserts all new keys are refused (there is no rehash). In exchange the insert proof stays short. Reusing the *first* TOMB on the path without searching on for `k` is the classic real-world duplicate-key bug, and is a candidate for a later bug (c′) |
| Shared search | `$find(k)` returns the slot index holding `k`, or `-1`; used by `lookup`, `delete`, `insert` | one probe loop to visualize |

### B.2 Correction to the brief's clause (iv)

With tombstones, "count of FULL slots == |M| < capacity" is **not enough for probing to terminate**. Take 1
FULL slot and 7 TOMB slots: then `#FULL = 1 < 8`, but a lookup of an absent key skips all 8 slots forever,
because neither FULL nor TOMB stops the probe. Probing stops only at an EMPTY slot or at the key itself. So
clause (iv) here is: `#FULL == |M|` (bookkeeping) **and** `used == #non-EMPTY` **and** `used < CAP` (at least
one EMPTY slot exists). Bug (d) breaks exactly the last conjunct.

### B.3 Listing

```wat
  1  (memory 1)
  2  (global $used (mut i32) (i32.const 0))
  3  (@ghost global $M (Map i32 i32))
  4  (@define EMPTY = 0, FULL = 1, TOMB = 2, CAP = 8, BASE = 65440)
  5  (@define st(s) = load(BASE + 12*s), key(s) = load(BASE + 12*s + 4), val(s) = load(BASE + 12*s + 8))
  6  (@define h(k) = k & 7, at(k, d) = (h(k) + d) & 7, dist(k, s) = (s - h(k)) & 7)
  7  (@define R0 = forall s in 0..7. st(s) in {EMPTY, FULL, TOMB})
  8  (@define R1 = forall s. st(s) == FULL ==> key(s) in M && M[key(s)] == val(s))
  9  (@define R2 = forall k in M. #{s | st(s) == FULL && key(s) == k} == 1)
 10  (@define R3 = forall s. st(s) == FULL ==> forall d <= dist(key(s), s). st(at(key(s), d)) != EMPTY)
 11  (@define R4 = #{s | st(s) == FULL} == |M| && used == #{s | st(s) != EMPTY} && used < CAP)
 12  (@define R = R0 && R1 && R2 && R3 && R4)
 13  (func $slot (param $i (i32 | 0 <= v && v < CAP)) (result (i32 | v == BASE + 12*i))
 14    local.get $i
 15    i32.const 12
 16    i32.mul
 17    i32.const 65440
 18    i32.add
 19  )
 20  (func $find (param $k i32) (result (i32 | (v == -1 && !(k in M)) || (0 <= v && v < CAP && st(v) == FULL && key(v) == k)))
 21    (@requires R)
 22    (local $i i32)
 23    (local $p i32)
 24    (@ghost local $j i32)
 25    local.get $k
 26    i32.const 7
 27    i32.and
 28    local.set $i
 29    loop $probe
 30      (@invariant 0 <= j && j <= used && i == at(k, j))
 31      (@invariant forall d < j. st(at(k, d)) == TOMB || (st(at(k, d)) == FULL && key(at(k, d)) != k))
 32      (@decreases CAP - j)
 33      local.get $i
 34      call $slot
 35      local.tee $p
 36      i32.load
 37      i32.const 1
 38      i32.lt_u
 39      if
 40        i32.const -1
 41        return
 42      end
 43      local.get $p
 44      i32.load
 45      i32.const 1
 46      i32.eq
 47      local.get $p
 48      i32.load offset=4
 49      local.get $k
 50      i32.eq
 51      i32.and
 52      if
 53        local.get $i
 54        return
 55      end
 56      local.get $i
 57      i32.const 1
 58      i32.add
 59      i32.const 7
 60      i32.and
 61      local.set $i
 62      (@ghost j := j + 1)
 63      br $probe
 64    end
 65    unreachable
 66  )
 67  (func $lookup (param $k i32) (param $dflt i32) (result (i32 | v == (k in M ? M[k] : dflt)))
 68    (@requires R)
 69    (@ensures R)
 70    (local $i i32)
 71    local.get $k
 72    call $find
 73    local.tee $i
 74    i32.const 0
 75    i32.lt_s
 76    if
 77      local.get $dflt
 78      return
 79    end
 80    local.get $i
 81    call $slot
 82    i32.load offset=8
 83  )
 84  (func $delete (param $k i32) (result (i32 | v == (k in old(M) ? 1 : 0)))
 85    (@requires R)
 86    (@ensures R && M == old(M) \ {k})
 87    (local $i i32)
 88    local.get $k
 89    call $find
 90    local.tee $i
 91    i32.const 0
 92    i32.lt_s
 93    if
 94      i32.const 0
 95      return
 96    end
 97    local.get $i
 98    call $slot
 99    i32.const 2
100    i32.store
101    (@ghost M := M \ {k})
102    i32.const 1
103  )
104  (func $insert (param $k i32) (param $x i32) (result (i32 | v == 1 || (v == 0 && !(k in M) && used == CAP - 1)))
105    (@requires R)
106    (@ensures R && M == (result == 1 ? old(M)[k := x] : old(M)))
107    (local $i i32)
108    (local $p i32)
109    (@ghost local $j i32)
110    local.get $k
111    call $find
112    local.tee $i
113    i32.const 0
114    i32.ge_s
115    if
116      local.get $i
117      call $slot
118      local.get $x
119      i32.store offset=8
120      (@ghost M := M[k := x])
121      i32.const 1
122      return
123    end
124    global.get $used
125    i32.const 7
126    i32.ge_u
127    if
128      i32.const 0
129      return
130    end
131    local.get $k
132    i32.const 7
133    i32.and
134    local.set $i
135    loop $free
136      (@invariant !(k in M) && 0 <= j && j <= used && i == at(k, j))
137      (@invariant forall d < j. st(at(k, d)) != EMPTY)
138      (@decreases CAP - j)
139      local.get $i
140      call $slot
141      local.tee $p
142      i32.load
143      if
144        local.get $i
145        i32.const 1
146        i32.add
147        i32.const 7
148        i32.and
149        local.set $i
150        (@ghost j := j + 1)
151        br $free
152      end
153    end
154    local.get $p
155    i32.const 1
156    i32.store
157    local.get $p
158    local.get $k
159    i32.store offset=4
160    local.get $p
161    local.get $x
162    i32.store offset=8
163    global.get $used
164    i32.const 1
165    i32.add
166    global.set $used
167    (@ghost M := M[k := x])
168    i32.const 1
169  )
```

### B.4 The representation invariant `R` (lines 7–12)

| clause | formal (listing line) | in words |
|---|---|---|
| (o) `R0` | `forall s. st(s) in {EMPTY, FULL, TOMB}` (7) | well-formed states |
| (i) `R1` | `st(s) == FULL ==> key(s) in M && M[key(s)] == val(s)` (8) | every FULL slot is an entry of `M` |
| (ii) `R2` | `forall k in M. #{s \| st(s) == FULL && key(s) == k} == 1` (9) | every key of `M` sits in **exactly one** FULL slot |
| (iii) `R3` | `st(s) == FULL ==> forall d <= dist(key(s), s). st(at(key(s), d)) != EMPTY` (10) | **reachability**: walking from `h(key)` to the key's slot never crosses an EMPTY slot (TOMBs are fine) |
| (iv) `R4` | `#FULL == \|M\| && used == #{s \| st(s) != EMPTY} && used < CAP` (11) | counts agree, and at least one EMPTY slot exists, so every probe terminates |

`R` is required at entry and exit of `$find`, `$lookup`, `$delete` and `$insert`. In the middle of an
operation it can be false; for example, `insert` writes the state, key and value one store at a time
and updates the ghost `M` afterwards. The fixture therefore reports `R` only at operation boundaries.

### B.5 The probe-loop invariant (lines 30–32 in `$find`; 136–138 in `$insert`)

At the head of `loop $probe`, after `j` probes (`j` is a ghost counter):

1. `i == at(k, j)`: `i` is the j-th slot of `k`'s probe sequence (always in `[0, 8)` thanks to the mask).
2. `forall d < j. st(at(k,d)) == TOMB || (st(at(k,d)) == FULL && key(at(k,d)) != k)`: **every slot passed so
   far is non-EMPTY and does not hold `k`** (the brief's "all FULL with keys ≠ k", widened to allow TOMBs).
3. `0 <= j <= used`: the `j` slots passed are distinct and non-EMPTY, so there are at most `used` of them.
4. `decreases CAP - j`: with (3) and `used < CAP` (R4), `j` stays below `CAP`, so the loop runs at most 8 times.

Why the early exit on EMPTY (line 41, `return -1`) is right: if `k` were in `M` at slot `s`, R3 says no
EMPTY slot lies between `h(k)` and `s`. The current slot `at(k, j)` *is* EMPTY, so `s` would be at distance
`< j`, but (2) says none of those holds `k`. This is the most interesting obligation in the program, and it
needs the loop invariant, R2 and R3 together. `$insert`'s `loop $free` (136–138) uses the weaker
"non-EMPTY so far" plus `!(k in M)` (from `$find`'s dependent result), and its exit point is the EMPTY slot
that ends `k`'s path. Writing `k` there keeps R3 true by construction.

### B.6 Proof obligations by instruction group

| lines | code | refined stack / facts after | obligation | status | why |
|---|---|---|---|---|---|
| 14–18 | `$slot: i*12 + 65440` | `[(i32 \| v == BASE + 12*i)]` | no overflow; post v == BASE + 12*i | **auto** | i in [0,8) from the param refinement |
| 25–28 | `find: i := k & 7` | `i == h(k), 0 <= i < 8` | - | **auto** | bit-vector: x & 7 is in [0,8) for every i32, negative keys included |
| 29 | `loop $probe` |  | inv on entry: j == 0 <= used, i == at(k,0), path-so-far vacuous;  measure CAP - 0 >= 0 | **auto** |  |
| 33–35 | `call $slot; local.tee $p` | `[(i32 \| v == BASE + 12*i)]` | pre of $slot: 0 <= i < CAP | **inv** | i == at(k, j) is masked |
| 36 | `i32.load` | `[(i32 \| v == st(i))]` | in bounds: p + 4 <= 65536 | **auto** | p <= BASE + 84 = 65524 |
| 37–41 | `st(i) < FULL ? return -1` | `[(i32 \| v == -1)]` | post of $find: !(k in M) | **inv** | THE key step. R0 makes st(i) < 1 mean EMPTY. If k were in M at slot s, R3 says no EMPTY lies on path(h(k)..s); slot i = at(k,j) is EMPTY so s would be at distance < j, but the probe invariant says no slot at distance < j holds k. Needs inv + R2 + R3 |
| 43–51 | `(st(i) == FULL) & (key(i) == k)` | `[(i32 \| v == (st(i) == FULL && key(i) == k ? 1 : 0))]` | in bounds: p + 8 <= 65536 | **auto** |  |
| 52–54 | `match ? return i` | `[(i32 \| v == i)]` | post of $find: 0 <= i < CAP && st(i) == FULL && key(i) == k | **auto** | path condition |
| 56–61 | `i := (i + 1) & 7` | `i' == at(k, j + 1)` | - | **auto** |  |
| 62–63 | `j := j + 1; br $probe` |  | inv preserved: slot at distance j is TOMB or FULL-with-other-key; j + 1 <= used;  measure CAP - (j+1) < CAP - j, >= 0 | **lemma** | first part: fallthrough path conditions of 39 and 52. j+1 <= used: the j+1 visited slots are distinct (j < CAP) and all non-EMPTY, so j+1 <= #non-EMPTY == used (R4); pigeonhole/counting lemma |
| 65 | `unreachable` |  | this point is dead | **auto** | the loop body always ends in br; falling out is structurally impossible |
| 71–78 | `lookup: i := find(k); i < 0 ? return dflt` | `[(i32 \| v == dflt)]` | pre of $find: R;  post: !(k in M) so result == dflt | **auto** | from $find's dependent result type |
| 80–82 | `lookup: load val(i)` | `[(i32 \| v == val(i))]` | post: val(i) == M[k];  R preserved | **inv** | R1: a FULL slot holding k stores M[k]. R preserved because lookup writes nothing (frame) |
| 88–96 | `delete: i := find(k); absent ? return 0` | `[(i32 \| v == 0)]` | post: k not in old(M), M unchanged, R unchanged | **auto** |  |
| 97–101 | `delete: st(i) := TOMB; M := M \ {k}` |  | R after: R1 (slot i no longer FULL), R2 (k had exactly one slot), R3 (TOMB is not EMPTY, so no probe path gains an EMPTY), R4 (#FULL - 1 == \|M\| - 1; used unchanged) | **inv** | R3 is the reason deletion must write TOMB, never EMPTY |
| 110–115 | `insert: i := find(k); i >= 0 ?` | `then: st(i) == FULL && key(i) == k / else: !(k in M)` | pre of $find: R | **auto** |  |
| 116–120 | `insert(update): val(i) := x; M := M[k := x]` |  | R1 for slot i with the new M; other clauses untouched | **auto** |  |
| 124–130 | `used >= CAP-1 ? return 0` | `[(i32 \| v == 0)]` | post: !(k in M) && used == CAP - 1 | **auto** | used < CAP from R4 and used >= 7 |
| 131–135 | `i := h(k); loop $free` |  | inv on entry: !(k in M) (from find), j == 0, i == at(k, 0) | **auto** |  |
| 139–143 | `st(i) != EMPTY ?` |  | pre of $slot: 0 <= i < CAP;  load in bounds | **inv** |  |
| 144–151 | `i := (i+1) & 7; j := j + 1; br $free` |  | inv preserved (path so far non-EMPTY; j + 1 <= used);  measure | **lemma** | same counting lemma as find |
| 154–162 | `write FULL, k, x into EMPTY slot i` |  | stores in bounds | **auto** |  |
| 163–167 | `used := used + 1; M := M[k := x]` |  | R after: R1 (new slot maps k to x), R2 (k was absent: inv), R3 (path h(k)..i was non-EMPTY: inv; turning an EMPTY into FULL never breaks another key's path), R4 (#FULL + 1 == \|M\| + 1; used + 1 == #non-EMPTY because slot i WAS EMPTY; used + 1 < CAP because the check at 124-126 gave used < CAP - 1) | **inv** | R4's used < CAP is what keeps every probe loop terminating |

### B.7 Seeded bugs

For each bug the table gives the operation sequence that exposes it, what V8 does, the first *static*
obligation that fails, the first *dynamic* check that fires, and the first step at which `R` (or the
relevant clause) becomes false.

| id | edit | sequence (results) | static failure | first dynamic failure | R clause broken, and first step | runtime |
|---|---|---|---|---|---|---|
| **(a)** probe index not wrapped | delete lines 147–148 (`i32.const 7`, `i32.and`) in `$insert`'s `loop $free` | `insert(7,70)` → 1; `insert(15,150)` → **trap** (`15 & 7 = 7` collides with 7; the probe goes to index 8) | line 140, `pre of $slot: 0 <= i < CAP`: after line 146, `i == at(k,j) + 1`, which is 8 when `at(k,j) == 7` | step 143 (line 151 back-edge): invariant line 136 `i == at(k, j)` (`i = 8`); step 145: `requires` of `$slot` | **none**: the trap preempts every write. With `BASE = 0` there would be no trap; the entry would land in "slot 8" (bytes 96–107), outside the table, breaking **(ii)** (15 ∈ M but in no FULL slot) | 💣 "out of bounds memory access" at line 142, step 153 (address 65536) |
| **(b)** lookup treats TOMB as EMPTY | line 38: `i32.lt_u` (state < FULL, i.e. EMPTY) → `i32.ne` (state != FULL, i.e. EMPTY *or* TOMB) | `insert(3,30)` → 1; `insert(11,110)` → 1 (collides, goes to slot 4); `delete(3)` → 1 (slot 3 becomes TOMB); `lookup(11,-1)` → **-1** (expected 110) | line 41, `post of $find: !(k in M)`: the path condition at the early return is now "EMPTY or TOMB", but R3 only promises *no EMPTY* on a key's path | step 241: `$find` returns -1 to `lookup` (its result refinement fails); step 247: `lookup`'s `ensures` | **R stays true at every step**: delete correctly writes TOMB. What breaks is the *stronger* invariant the buggy code silently relies on, **(iii)-strong: "no non-FULL slot on any key's probe path"**. It becomes false at **step 217** (`delete`'s `i32.store`, line 100), when slot 3 on key 11's path turns TOMB | no trap; wrong answer. Cascade: a later `insert(11,111)` sees "absent" and writes a 2nd FULL slot for 11 (slot 5), which **does** break R2 **(ii)** |
| **(b′)** delete writes EMPTY | line 99: `i32.const 2` → `i32.const 0` | same sequence; `lookup(11,-1)` → **-1** | line 100: R3 after the store (an EMPTY now sits on key 11's path 3→4) | step 218: `delete`'s `ensures R` | **(iii)** and **(iv)** (`used` = 2 but only 1 slot is non-EMPTY), false from **step 217** (line 100) | no trap; wrong answer |
| **(c)** insert does not check for an existing key | delete lines 110–123 (the find-and-update group) | `insert(3,30)` → 1; `insert(3,31)` → 1; `lookup(3,-1)` → **30** (expected 31) | line 135, `inv on entry of $free: !(k in M)`: nothing establishes it any more | step 43: invariant line 136 at `loop $free` entry (2nd insert) | **(ii)** from **step 78** (line 159, key store: slots 3 *and* 4 FULL with key 3). At `insert`'s return (step 86) also **(i)** (ghost `M[3] = 31`, slot 3 still holds 30) and **(iv)** (`#FULL = 2 ≠ \|M\| = 1`) | no trap; stale value returned |
| **(d)** load-factor check off by one | line 125: `i32.const 7` → `i32.const 8` (refuse only when `used >= 8`) | `insert(k, 10k)` for `k = 0..7` → eight 1s (the correct program refuses the 8th with 0); then `lookup(8,-1)` → **never returns** | line 166, `R4 after insert: used + 1 < CAP`: the check now gives only `used < 8`, which R4 already guaranteed | step 488: the 8th `insert`'s `ensures R`; step 489/490: `lookup`/`$find` `requires R`; step 765: probe invariant `j <= used` and `decreases` fail (`j = 9`) | **(iv)**, conjunct `used < CAP`: false from **step 487** (line 166, `global.set $used` → 8) | no trap; `$find` probes 0,1,…,7,0,1,… forever. Codillon's 100k-step log fills up |

### B.8 Step-by-step: bug (b)

These are the key frames of the fixture's (b) trace (all 247 steps are summarized by these 23). `slots`
shows only non-EMPTY slots, as `index:[state,key,value]`. "(iii)-strong" is the property the buggy lookup
assumes.

| step | fn:line | op | stack | slots (non-EMPTY) | M | used | (iii)-strong | note |
|---|---|---|---|---|---|---|---|---|
| 17 | find:36 | `i32.load` | [0] | — | {} | 0 | ✓ | insert(3,30): find(3) probes slot 3: EMPTY |
| 22 | find:41 | `return` | [-1] | — | {} | 0 | ✓ | find(3) → -1 (absent) |
| 46 | insert:142 | `i32.load` | [0] | — | {} | 0 | ✓ | insert: first EMPTY on 3's path is slot 3 |
| 56 | insert:162 | `i32.store offset=8` | [] | 3:[1,3,30] | {} | 0 | ✓ | slot 3 written |
| 61 | insert:168 | `i32.const 1` | [1] | 3:[1,3,30] | {3↦30} | 1 | ✓ | insert returns 1; R holds |
| 78 | find:36 | `i32.load` | [1] | 3:[1,3,30] | {3↦30} | 1 | ✓ | insert(11,110): find(11) probes slot 3: FULL |
| 87 | find:48 | `i32.load offset=4` | [1, 3] | 3:[1,3,30] | {3↦30} | 1 | ✓ | key 3 ≠ 11, keep probing |
| 108 | find:36 | `i32.load` | [0] | 3:[1,3,30] | {3↦30} | 1 | ✓ | slot 4: EMPTY |
| 113 | find:41 | `return` | [-1] | 3:[1,3,30] | {3↦30} | 1 | ✓ | find(11) → -1 |
| 137 | insert:142 | `i32.load` | [1] | 3:[1,3,30] | {3↦30} | 1 | ✓ | insert: slot 3 non-EMPTY, skip |
| 155 | insert:142 | `i32.load` | [0] | 3:[1,3,30] | {3↦30} | 1 | ✓ | slot 4 EMPTY |
| 165 | insert:162 | `i32.store offset=8` | [] | 3:[1,3,30], 4:[1,11,110] | {3↦30} | 1 | ✓ | slot 4 written (collision resolved) |
| 170 | insert:168 | `i32.const 1` | [1] | 3:[1,3,30], 4:[1,11,110] | {3↦30, 11↦110} | 2 | ✓ | insert returns 1; R holds |
| 187 | find:36 | `i32.load` | [1] | 3:[1,3,30], 4:[1,11,110] | {3↦30, 11↦110} | 2 | ✓ | delete(3): find(3) probes slot 3: FULL |
| 196 | find:48 | `i32.load offset=4` | [1, 3] | 3:[1,3,30], 4:[1,11,110] | {3↦30, 11↦110} | 2 | ✓ | key 3 matches |
| 202 | find:54 | `return` | [3] | 3:[1,3,30], 4:[1,11,110] | {3↦30, 11↦110} | 2 | ✓ | find(3) → 3 |
| 217 | delete:100 | `i32.store` | [] | 3:[2,3,30], 4:[1,11,110] | {3↦30, 11↦110} | 2 | ✗ | slot 3 := TOMB. R still true; (iii)-strong now FALSE (11's path 3→4 has a non-FULL slot) |
| 218 | delete:102 | `i32.const 1` | [1] | 3:[2,3,30], 4:[1,11,110] | {11↦110} | 2 | ✗ | delete returns 1; R holds |
| 235 | find:36 | `i32.load` | [2] | 3:[2,3,30], 4:[1,11,110] | {11↦110} | 2 | ✗ | lookup(11): find(11) loads slot 3 state = 2 (TOMB) |
| 237 | find:38 | `i32.ne` | [1] | 3:[2,3,30], 4:[1,11,110] | {11↦110} | 2 | ✗ | BUG line 38: 2 != 1 → 1 ("treat as EMPTY") |
| 240 | find:41 | `return` | [-1] | 3:[2,3,30], 4:[1,11,110] | {11↦110} | 2 | ✗ | find returns -1 |
| 241 | lookup:72 | `call $find (return)` | [-1] | 3:[2,3,30], 4:[1,11,110] | {11↦110} | 2 | ✗ | ✗ find's result refinement fails: 11 ∈ M |
| 247 | lookup:78 | `return` | [-1] | 3:[2,3,30], 4:[1,11,110] | {11↦110} | 2 | ✗ | ✗ lookup ensures fails: returns -1, M[11] = 110 |

Things to visualize: through step 202 nothing is wrong. At step 217 nothing is *wrong* with the table either:
R holds, and a correct lookup would succeed. Under the buggy reading of TOMB, though, key 11 has become
unreachable. The failure *surfaces* 24 steps later, in a different function (`$find` called from `lookup`).
This gap between cause (delete) and symptom (lookup) is what the representation invariant is for.

---
## Part C — JSON fixture

### Schema

```text
{
  version: 1,
  conventions: { step, values, frame, hash_frame_extra, status },  // human-readable, same as §1
  programs: [ {
    id: "parity" | "isqrt" | "gcd" | "pow_mod" | "hashtable",
    title,
    lines: [string],             // the refined listing, line i+1 = lines[i]
                                 // line kind by prefix: "(func" header, "(@" spec, ")" close,
                                 // "(local" local, "(memory"/"(global" meta, else instruction
    functions: [ {name, line, signature} ],   // signature = the refined header line
    specs:     [ {line, text} ],              // every (@...) line
    obligations: [ {lines:[int], code, stack, obligation, status, kind} ],
                                 // status: none | auto | inv | lemma   (see §1)
                                 // kind: post | pre | inv-entry | inv-preserve | overflow | trap | branch | type | R | assert | dead
    correct_runs: {calls, results, total_steps, spec_checks_failed: 0},
    bugs: [ {
      id, title, category: "code" | "spec", flavor,
      edit,                      // human-readable
      edits: [ ["replace", line, old, new] | ["delete", fromLine, toLine] ],   // machine-applicable; deletions blank lines
      calls: [[fn, args]], expected_results, observed_results,   // observed may end in "trap: ..." or a non-termination note
      runtime,                   // what V8 does
      static_failure: {line, obligation, why, status: "fails"},
      first_dynamic_failure: {s, ln, kind},      // first spec check (or trap) that fires at runtime
      R_violation?,              // hash table only: which clause of R breaks and when
      op_boundaries?: [ {call, returned_at_step, R_false: [clause]} ],   // hash table only
      trace_note?,
      trace: [ frame ]           // key frames, chronological
    } ]
  } ]
}
frame = { s, fn, ln, op, stack: [bottom..top] after the step, loc: {name: value} incl. ghost locals,
          checks?: [ {ln, kind, ok} ], trap?,
          // hash table only:
          used, M: [[key, value]], slots: [[state, key, value] x 8],
          R?: {o, i, ii, iii, iv}      // present only at operation boundaries
          iii_strong?                  // bug (b) only
        }
```

Notes for consumers. Every bug's line numbers refer to the *original* listing; the edits keep numbering
because deletions blank lines. For S1 the trace is a counterexample-to-induction (see `trace_note`): its
frames carry small step numbers, but `first_dynamic_failure.s` is the real-run step (695,119). For (d), the
run was cut at 900 steps; the program does not terminate.

### Fixture

```json
{
 "version":1,
 "conventions":{
  "step":"one step per executed instruction line; `block`/`loop`/`if`/`br*`/`return`/`call` count, `else`/`end` do not; a `call` takes two steps (enter: args popped; return: result pushed). Spec checks happen after the step they are attached to.",
  "values":"i32 shown as signed decimal; predicates read them as mathematical integers (signed) unless written u(x)",
  "frame":"{s: step, fn, ln: line (1-based, in the program listing, which is the same for buggy variants because deleted lines are blanked, not removed), op, stack (after the step, bottom first), loc: locals incl. ghost, checks: spec checks evaluated at this step}",
  "hash_frame_extra":"used: global $used; M: ghost map as [key, value] pairs; slots: 8 x [state, key, value] (0 EMPTY, 1 FULL, 2 TOMB); R: truth of each clause of the representation invariant at that instant (only REQUIRED at function boundaries; transient falsity mid-operation is normal)",
  "status":"none = no obligation beyond Wasm typing; auto = discharged from the refined stack + path condition by linear/bit-vector reasoning; inv = needs the loop invariant or the representation invariant R; lemma = also needs a nonlinear, counting, or definitional lemma; fails = the obligation that a seeded bug breaks"
 },
 "programs":[
  {
   "id":"parity",
   "title":"Parity gate: is_even / half / half_or_neg1",
   "lines":[
    "(func $is_even (param $x i32) (result (i32 | v == (x % 2 == 0 ? 1 : 0)))",
    "  local.get $x",
    "  i32.const 1",
    "  i32.and",
    "  i32.eqz",
    ")",
    "(func $half (param $x (i32 | v % 2 == 0)) (result (i32 | v + v == x))",
    "  local.get $x",
    "  i32.const 1",
    "  i32.shr_s",
    ")",
    "(func $half_or_neg1 (param $x i32) (result (i32 | (x % 2 == 0 && v + v == x) || (x % 2 == 1 && v == -1)))",
    "  local.get $x",
    "  call $is_even",
    "  i32.eqz",
    "  if (result i32)",
    "    i32.const -1",
    "  else",
    "    (@assert x % 2 == 0)",
    "    local.get $x",
    "    call $half",
    "  end",
    ")"
   ],
   "functions":[
    {"name":"$is_even","line":1,"signature":"(func $is_even (param $x i32) (result (i32 | v == (x % 2 == 0 ? 1 : 0)))"},
    {"name":"$half","line":7,"signature":"(func $half (param $x (i32 | v % 2 == 0)) (result (i32 | v + v == x))"},
    {
     "name":"$half_or_neg1",
     "line":12,
     "signature":"(func $half_or_neg1 (param $x i32) (result (i32 | (x % 2 == 0 && v + v == x) || (x % 2 == 1 && v == -1)))"
    }
   ],
   "specs":[{"line":19,"text":"(@assert x % 2 == 0)"}],
   "obligations":[
    {"lines":[2,3],"code":"local.get $x; i32.const 1","stack":"[x, 1]","obligation":"-","status":"none"},
    {"lines":[4],"code":"i32.and","stack":"[(i32 | v == x & 1 && 0 <= v <= 1)]","obligation":"-","status":"none"},
    {
     "lines":[5],
     "code":"i32.eqz",
     "stack":"[(i32 | v == (x & 1 == 0 ? 1 : 0))]",
     "obligation":"post of $is_even: v == (x % 2 == 0 ? 1 : 0)",
     "status":"auto",
     "kind":"post"
    },
    {"lines":[8,9],"code":"local.get $x; i32.const 1","stack":"[(i32 | v == x && v % 2 == 0), 1]","obligation":"-","status":"none"},
    {"lines":[10],"code":"i32.shr_s","stack":"[(i32 | v == floor(x / 2))]","obligation":"post of $half: v + v == x","status":"auto","kind":"post"},
    {
     "lines":[13,14],
     "code":"local.get $x; call $is_even",
     "stack":"[(i32 | v == (x % 2 == 0 ? 1 : 0))]",
     "obligation":"pre of $is_even: none",
     "status":"auto",
     "kind":"pre"
    },
    {"lines":[15],"code":"i32.eqz","stack":"[(i32 | v == (x % 2 == 0 ? 0 : 1))]","obligation":"-","status":"none"},
    {"lines":[16],"code":"if (result i32)","stack":"then: path x % 2 == 1 / else: path x % 2 == 0","obligation":"-","status":"auto","kind":"branch"},
    {"lines":[17],"code":"i32.const -1","stack":"[(i32 | v == -1)]","obligation":"post (then-arm): x % 2 == 1 && v == -1","status":"auto","kind":"post"},
    {"lines":[19],"code":"(@assert x % 2 == 0)","obligation":"x % 2 == 0","status":"auto","kind":"assert"},
    {
     "lines":[20,21],
     "code":"local.get $x; call $half",
     "stack":"[(i32 | v + v == x)]",
     "obligation":"pre of $half: x % 2 == 0;  post (else-arm): x % 2 == 0 && v + v == x",
     "status":"auto",
     "kind":"pre"
    }
   ],
   "bugs":[
    {
     "id":"P1",
     "title":"gate inverted (forgot the negation)",
     "category":"code",
     "flavor":"ordinary; blame lands on the CALLER",
     "edit":"delete line 15 (`i32.eqz`)",
     "edits":[["delete",15,15]],
     "calls":[["half_or_neg1",[3]]],
     "expected_results":[-1],
     "observed_results":[1],
     "runtime":"no trap; $half(3) computes 3 >> 1 = 1 and $half_or_neg1 returns 1 (should be -1). For x = 4 it returns -1 (should be 2).",
     "static_failure":{
      "line":21,
      "obligation":"pre of $half: x % 2 == 0",
      "why":"with line 15 gone the else-arm runs when is_even(x) == 0, so its path condition is x % 2 == 1; the precondition is refuted (the @assert on line 19 fails the same way)",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":8,"ln":19,"kind":"assert"},
     "trace":[
      {"s":1,"fn":"half_or_neg1","ln":13,"op":"local.get $x","stack":[3],"loc":{"x":3}},
      {"s":2,"fn":"half_or_neg1","ln":14,"op":"call $is_even  (enter)","stack":[],"loc":{"x":3}},
      {"s":3,"fn":"is_even","ln":2,"op":"local.get $x","stack":[3],"loc":{"x":3}},
      {"s":4,"fn":"is_even","ln":3,"op":"i32.const 1","stack":[3,1],"loc":{"x":3}},
      {"s":5,"fn":"is_even","ln":4,"op":"i32.and","stack":[1],"loc":{"x":3}},
      {"s":6,"fn":"is_even","ln":5,"op":"i32.eqz","stack":[0],"loc":{"x":3}},
      {"s":7,"fn":"half_or_neg1","ln":14,"op":"call $is_even  (return)","stack":[0],"loc":{"x":3},"checks":[{"ln":1,"kind":"ensures","ok":true}]},
      {"s":8,"fn":"half_or_neg1","ln":16,"op":"if (result i32)","stack":[],"loc":{"x":3},"checks":[{"ln":19,"kind":"assert","ok":false}]},
      {"s":9,"fn":"half_or_neg1","ln":20,"op":"local.get $x","stack":[3],"loc":{"x":3}},
      {"s":10,"fn":"half_or_neg1","ln":21,"op":"call $half  (enter)","stack":[],"loc":{"x":3},"checks":[{"ln":7,"kind":"requires","ok":false}]},
      {"s":11,"fn":"half","ln":8,"op":"local.get $x","stack":[3],"loc":{"x":3}},
      {"s":12,"fn":"half","ln":9,"op":"i32.const 1","stack":[3,1],"loc":{"x":3}},
      {"s":13,"fn":"half","ln":10,"op":"i32.shr_s","stack":[1],"loc":{"x":3}},
      {"s":14,"fn":"half_or_neg1","ln":21,"op":"call $half  (return)","stack":[1],"loc":{"x":3},"checks":[{"ln":7,"kind":"ensures","ok":false},{"ln":12,"kind":"ensures","ok":false}]}
     ]
    },
    {
     "id":"P2",
     "title":"logical instead of arithmetic shift",
     "category":"code",
     "flavor":"subtle: every non-negative input is fine",
     "edit":"line 10: `i32.shr_s` -> `i32.shr_u`",
     "edits":[["replace",10,"i32.shr_s","i32.shr_u"]],
     "calls":[["half_or_neg1",[-4]]],
     "expected_results":[-2],
     "observed_results":[2147483646],
     "runtime":"no trap; returns 2147483646 for x = -4. Also x = INT_MIN returns 1073741824 (positive).",
     "static_failure":{
      "line":10,
      "obligation":"post of $half: v + v == x",
      "why":"shr_u gives v == u(x) / 2, which equals x / 2 only when 0 <= x; for x < 0, v + v == x + 2^32",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":15,"ln":7,"kind":"ensures"},
     "trace":[
      {"s":1,"fn":"half_or_neg1","ln":13,"op":"local.get $x","stack":[-4],"loc":{"x":-4}},
      {"s":2,"fn":"half_or_neg1","ln":14,"op":"call $is_even  (enter)","stack":[],"loc":{"x":-4}},
      {"s":3,"fn":"is_even","ln":2,"op":"local.get $x","stack":[-4],"loc":{"x":-4}},
      {"s":4,"fn":"is_even","ln":3,"op":"i32.const 1","stack":[-4,1],"loc":{"x":-4}},
      {"s":5,"fn":"is_even","ln":4,"op":"i32.and","stack":[0],"loc":{"x":-4}},
      {"s":6,"fn":"is_even","ln":5,"op":"i32.eqz","stack":[1],"loc":{"x":-4}},
      {"s":7,"fn":"half_or_neg1","ln":14,"op":"call $is_even  (return)","stack":[1],"loc":{"x":-4},"checks":[{"ln":1,"kind":"ensures","ok":true}]},
      {"s":8,"fn":"half_or_neg1","ln":15,"op":"i32.eqz","stack":[0],"loc":{"x":-4}},
      {"s":9,"fn":"half_or_neg1","ln":16,"op":"if (result i32)","stack":[],"loc":{"x":-4},"checks":[{"ln":19,"kind":"assert","ok":true}]},
      {"s":10,"fn":"half_or_neg1","ln":20,"op":"local.get $x","stack":[-4],"loc":{"x":-4}},
      {"s":11,"fn":"half_or_neg1","ln":21,"op":"call $half  (enter)","stack":[],"loc":{"x":-4},"checks":[{"ln":7,"kind":"requires","ok":true}]},
      {"s":12,"fn":"half","ln":8,"op":"local.get $x","stack":[-4],"loc":{"x":-4}},
      {"s":13,"fn":"half","ln":9,"op":"i32.const 1","stack":[-4,1],"loc":{"x":-4}},
      {"s":14,"fn":"half","ln":10,"op":"i32.shr_u","stack":[2147483646],"loc":{"x":-4}},
      {"s":15,"fn":"half_or_neg1","ln":21,"op":"call $half  (return)","stack":[2147483646],"loc":{"x":-4},"checks":[{"ln":7,"kind":"ensures","ok":false},{"ln":12,"kind":"ensures","ok":false}]}
     ]
    },
    {
     "id":"P3",
     "title":"\"half is smaller\" (spec bug)",
     "category":"spec",
     "flavor":"spec bug: program right, spec wrong",
     "edit":"line 7: result refinement `(i32 | v + v == x)` -> `(i32 | v + v == x && v < x)`",
     "edits":[
      [
       "replace",
       7,
       "(func $half (param $x (i32 | v % 2 == 0)) (result (i32 | v + v == x))",
       "(func $half (param $x (i32 | v % 2 == 0)) (result (i32 | v + v == x && v < x))"
      ]
     ],
     "calls":[["half_or_neg1",[0]]],
     "expected_results":[0],
     "observed_results":[0],
     "runtime":"no trap; returns the correct 0. Only the dynamic ensures check of $half fires. Fix the spec (drop `v < x`), not the code.",
     "static_failure":{
      "line":10,
      "obligation":"post of $half: v + v == x && v < x",
      "why":"v < x is false when x == 0 (0 < 0) and for every negative even x (-2 > -4)",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":15,"ln":7,"kind":"ensures"},
     "trace":[
      {"s":1,"fn":"half_or_neg1","ln":13,"op":"local.get $x","stack":[0],"loc":{"x":0}},
      {"s":2,"fn":"half_or_neg1","ln":14,"op":"call $is_even  (enter)","stack":[],"loc":{"x":0}},
      {"s":3,"fn":"is_even","ln":2,"op":"local.get $x","stack":[0],"loc":{"x":0}},
      {"s":4,"fn":"is_even","ln":3,"op":"i32.const 1","stack":[0,1],"loc":{"x":0}},
      {"s":5,"fn":"is_even","ln":4,"op":"i32.and","stack":[0],"loc":{"x":0}},
      {"s":6,"fn":"is_even","ln":5,"op":"i32.eqz","stack":[1],"loc":{"x":0}},
      {"s":7,"fn":"half_or_neg1","ln":14,"op":"call $is_even  (return)","stack":[1],"loc":{"x":0},"checks":[{"ln":1,"kind":"ensures","ok":true}]},
      {"s":8,"fn":"half_or_neg1","ln":15,"op":"i32.eqz","stack":[0],"loc":{"x":0}},
      {"s":9,"fn":"half_or_neg1","ln":16,"op":"if (result i32)","stack":[],"loc":{"x":0},"checks":[{"ln":19,"kind":"assert","ok":true}]},
      {"s":10,"fn":"half_or_neg1","ln":20,"op":"local.get $x","stack":[0],"loc":{"x":0}},
      {"s":11,"fn":"half_or_neg1","ln":21,"op":"call $half  (enter)","stack":[],"loc":{"x":0},"checks":[{"ln":7,"kind":"requires","ok":true}]},
      {"s":12,"fn":"half","ln":8,"op":"local.get $x","stack":[0],"loc":{"x":0}},
      {"s":13,"fn":"half","ln":9,"op":"i32.const 1","stack":[0,1],"loc":{"x":0}},
      {"s":14,"fn":"half","ln":10,"op":"i32.shr_s","stack":[0],"loc":{"x":0}},
      {"s":15,"fn":"half_or_neg1","ln":21,"op":"call $half  (return)","stack":[0],"loc":{"x":0},"checks":[{"ln":7,"kind":"ensures","ok":false},{"ln":12,"kind":"ensures","ok":true}]}
     ]
    }
   ],
   "correct_runs":{
    "calls":[["half_or_neg1",[6]],["half_or_neg1",[7]],["half_or_neg1",[-4]],["is_even",[-3]]],
    "results":[3,-1,-2,0],
    "total_steps":44,
    "spec_checks_failed":0
   }
  },
  {
   "id":"isqrt",
   "title":"Integer square root (linear search)",
   "lines":[
    "(func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v <= n && n < (v + 1) * (v + 1)))",
    "  (local $r i32)",
    "  i32.const 0",
    "  local.set $r",
    "  block $done",
    "    loop $grow",
    "      (@invariant 0 <= r && r * r <= n)",
    "      (@decreases n - r * r)",
    "      local.get $r",
    "      i32.const 1",
    "      i32.add",
    "      local.get $r",
    "      i32.const 1",
    "      i32.add",
    "      i32.mul",
    "      local.get $n",
    "      i32.gt_u",
    "      br_if $done",
    "      local.get $r",
    "      i32.const 1",
    "      i32.add",
    "      local.set $r",
    "      br $grow",
    "    end",
    "  end",
    "  local.get $r",
    ")"
   ],
   "functions":[{"name":"$isqrt","line":1,"signature":"(func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v <= n && n < (v + 1) * (v + 1)))"}],
   "specs":[{"line":7,"text":"(@invariant 0 <= r && r * r <= n)"},{"line":8,"text":"(@decreases n - r * r)"}],
   "obligations":[
    {"lines":[3,4],"code":"i32.const 0; local.set $r","stack":"r == 0","obligation":"-","status":"none"},
    {"lines":[6],"code":"loop $grow","obligation":"inv on entry: 0 <= 0 && 0*0 <= n;  measure n - 0 >= 0","status":"auto","kind":"inv-entry"},
    {
     "lines":[9,10,11],
     "code":"local.get $r; i32.const 1; i32.add",
     "stack":"[(i32 | v == r + 1)]",
     "obligation":"no signed overflow: r + 1 <= 2^31-1",
     "status":"lemma",
     "kind":"overflow"
    },
    {"lines":[12,13,14],"code":"local.get $r; i32.const 1; i32.add","stack":"[r+1, r+1]","obligation":"same as 9-11","status":"lemma","kind":"overflow"},
    {
     "lines":[15],
     "code":"i32.mul",
     "stack":"[(i32 | u(v) == (r+1)*(r+1))]",
     "obligation":"no UNSIGNED overflow: (r+1)^2 < 2^32",
     "status":"lemma",
     "kind":"overflow"
    },
    {
     "lines":[16,17],
     "code":"local.get $n; i32.gt_u",
     "stack":"[(i32 | v == ((r+1)^2 > n ? 1 : 0))]",
     "obligation":"u(n) == n",
     "status":"auto",
     "kind":"type"
    },
    {"lines":[18],"code":"br_if $done","stack":"taken: n < (r+1)^2 / fallthrough: (r+1)^2 <= n","obligation":"-","status":"auto","kind":"branch"},
    {"lines":[19,20,21,22],"code":"r := r + 1","stack":"r' == r + 1","obligation":"no signed overflow (as 9-11)","status":"lemma","kind":"overflow"},
    {
     "lines":[23],
     "code":"br $grow",
     "obligation":"inv preserved: 0 <= r' && r'*r' <= n;  measure: 0 <= n - r'^2 < n - r^2",
     "status":"auto",
     "kind":"inv-preserve"
    },
    {
     "lines":[26],
     "code":"local.get $r  (exit via br_if)",
     "stack":"[(i32 | v == r)]",
     "obligation":"post: 0 <= r && r*r <= n && n < (r+1)^2",
     "status":"inv",
     "kind":"post"
    }
   ],
   "bugs":[
    {
     "id":"S1",
     "title":"signed comparison of a product that may exceed 2^31-1",
     "category":"code",
     "flavor":"subtle: correct for every n < 46340^2 = 2147395600",
     "edit":"line 17: `i32.gt_u` -> `i32.gt_s`",
     "edits":[["replace",17,"i32.gt_u","i32.gt_s"]],
     "calls":[["isqrt",[2147483647]]],
     "expected_results":[46340],
     "observed_results":["(does not terminate)"],
     "runtime":"n = 2147483647: never terminates (no i32 is signed-greater than INT_MAX). n = 2147395600 (smallest failing input): returns 289398 after ~4.3M steps. The real run reaches the bad loop-head state (r = 46340) only at step 695,104, far past Codillon's 100k-step log, so the trace below is the counterexample-to-induction: start at a loop head satisfying the invariant and run one iteration (add 695,100 to each step number to get the real-run step).",
     "static_failure":{
      "line":17,
      "obligation":"the comparison must mean (r+1)^2 > n",
      "why":"signed reading of the line-15 product is faithful only if (r+1)^2 <= 2^31-1, i.e. r <= 46339; the invariant r*r <= n only gives r <= 46340. At r = 46340 the product 2147488281 wraps to -2147479015",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":695119,"ln":7,"kind":"invariant"},
     "trace_note":"counterexample-to-induction: one loop iteration from the loop-head state n = 2147483647, r = 46340 (which satisfies the invariant). Real-run step = s + 695100.",
     "trace":[
      {"s":4,"fn":"isqrt","ln":6,"op":"loop $grow","stack":[],"loc":{"n":2147483647,"r":46340},"checks":[{"ln":7,"kind":"invariant","ok":true},{"ln":8,"kind":"decreases","ok":true}]},
      {"s":5,"fn":"isqrt","ln":9,"op":"local.get $r","stack":[46340],"loc":{"n":2147483647,"r":46340}},
      {"s":6,"fn":"isqrt","ln":10,"op":"i32.const 1","stack":[46340,1],"loc":{"n":2147483647,"r":46340}},
      {"s":7,"fn":"isqrt","ln":11,"op":"i32.add","stack":[46341],"loc":{"n":2147483647,"r":46340}},
      {"s":8,"fn":"isqrt","ln":12,"op":"local.get $r","stack":[46341,46340],"loc":{"n":2147483647,"r":46340}},
      {"s":9,"fn":"isqrt","ln":13,"op":"i32.const 1","stack":[46341,46340,1],"loc":{"n":2147483647,"r":46340}},
      {"s":10,"fn":"isqrt","ln":14,"op":"i32.add","stack":[46341,46341],"loc":{"n":2147483647,"r":46340}},
      {"s":11,"fn":"isqrt","ln":15,"op":"i32.mul","stack":[-2147479015],"loc":{"n":2147483647,"r":46340}},
      {"s":12,"fn":"isqrt","ln":16,"op":"local.get $n","stack":[-2147479015,2147483647],"loc":{"n":2147483647,"r":46340}},
      {"s":13,"fn":"isqrt","ln":17,"op":"i32.gt_s","stack":[0],"loc":{"n":2147483647,"r":46340}},
      {"s":14,"fn":"isqrt","ln":18,"op":"br_if $done","stack":[],"loc":{"n":2147483647,"r":46340}},
      {"s":15,"fn":"isqrt","ln":19,"op":"local.get $r","stack":[46340],"loc":{"n":2147483647,"r":46340}},
      {"s":16,"fn":"isqrt","ln":20,"op":"i32.const 1","stack":[46340,1],"loc":{"n":2147483647,"r":46340}},
      {"s":17,"fn":"isqrt","ln":21,"op":"i32.add","stack":[46341],"loc":{"n":2147483647,"r":46340}},
      {"s":18,"fn":"isqrt","ln":22,"op":"local.set $r","stack":[],"loc":{"n":2147483647,"r":46341}},
      {"s":19,"fn":"isqrt","ln":23,"op":"br $grow","stack":[],"loc":{"n":2147483647,"r":46341},"checks":[{"ln":7,"kind":"invariant","ok":false},{"ln":8,"kind":"decreases","ok":false}]}
     ]
    },
    {
     "id":"S2",
     "title":"strict/non-strict swapped in the postcondition (spec bug)",
     "category":"spec",
     "flavor":"spec bug: fails exactly on perfect squares",
     "edit":"line 1: result `v * v <= n && n < (v + 1) * (v + 1)` -> `v * v < n && n <= (v + 1) * (v + 1)`",
     "edits":[
      [
       "replace",
       1,
       "(func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v <= n && n < (v + 1) * (v + 1)))",
       "(func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v < n && n <= (v + 1) * (v + 1)))"
      ]
     ],
     "calls":[["isqrt",[4]]],
     "expected_results":[2],
     "observed_results":[2],
     "runtime":"no trap; returns the correct 2 for n = 4 (also fails for n = 0, 1, 9, ...). n = 5 passes.",
     "static_failure":{
      "line":26,
      "obligation":"post: r*r < n",
      "why":"the invariant gives r*r <= n and the exit gives n < (r+1)^2; nothing excludes r*r == n",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":45,"ln":1,"kind":"ensures"},
     "trace":[
      {"s":4,"fn":"isqrt","ln":6,"op":"loop $grow","stack":[],"loc":{"n":4,"r":0},"checks":[{"ln":7,"kind":"invariant","ok":true},{"ln":8,"kind":"decreases","ok":true}]},
      {"s":14,"fn":"isqrt","ln":18,"op":"br_if $done","stack":[],"loc":{"n":4,"r":0}},
      {"s":19,"fn":"isqrt","ln":23,"op":"br $grow","stack":[],"loc":{"n":4,"r":1},"checks":[{"ln":7,"kind":"invariant","ok":true},{"ln":8,"kind":"decreases","ok":true}]},
      {"s":29,"fn":"isqrt","ln":18,"op":"br_if $done","stack":[],"loc":{"n":4,"r":1}},
      {"s":34,"fn":"isqrt","ln":23,"op":"br $grow","stack":[],"loc":{"n":4,"r":2},"checks":[{"ln":7,"kind":"invariant","ok":true},{"ln":8,"kind":"decreases","ok":true}]},
      {"s":44,"fn":"isqrt","ln":18,"op":"br_if $done","stack":[],"loc":{"n":4,"r":2}},
      {"s":45,"fn":"isqrt","ln":26,"op":"local.get $r","stack":[2],"loc":{"n":4,"r":2},"checks":[{"ln":1,"kind":"ensures","ok":false}]}
     ]
    },
    {
     "id":"S3",
     "title":"off-by-one initial value",
     "category":"code",
     "flavor":"edge case: wrong only for n = 0",
     "edit":"line 3: `i32.const 0` -> `i32.const 1`",
     "edits":[["replace",3,"i32.const 0","i32.const 1"]],
     "calls":[["isqrt",[0]]],
     "expected_results":[0],
     "observed_results":[1],
     "runtime":"no trap; isqrt(0) returns 1. Every n >= 1 is answered correctly, so tests on 1..100 all pass.",
     "static_failure":{"line":6,"obligation":"inv on entry: 1*1 <= n","why":"only 0 <= n is known","status":"fails"},
     "first_dynamic_failure":{"s":4,"ln":7,"kind":"invariant"},
     "trace":[
      {"s":1,"fn":"isqrt","ln":3,"op":"i32.const 1","stack":[1],"loc":{"n":0,"r":0},"checks":[{"ln":1,"kind":"requires","ok":true}]},
      {"s":2,"fn":"isqrt","ln":4,"op":"local.set $r","stack":[],"loc":{"n":0,"r":1}},
      {"s":3,"fn":"isqrt","ln":5,"op":"block $done","stack":[],"loc":{"n":0,"r":1}},
      {"s":4,"fn":"isqrt","ln":6,"op":"loop $grow","stack":[],"loc":{"n":0,"r":1},"checks":[{"ln":7,"kind":"invariant","ok":false},{"ln":8,"kind":"decreases","ok":false}]},
      {"s":5,"fn":"isqrt","ln":9,"op":"local.get $r","stack":[1],"loc":{"n":0,"r":1}},
      {"s":6,"fn":"isqrt","ln":10,"op":"i32.const 1","stack":[1,1],"loc":{"n":0,"r":1}},
      {"s":7,"fn":"isqrt","ln":11,"op":"i32.add","stack":[2],"loc":{"n":0,"r":1}},
      {"s":8,"fn":"isqrt","ln":12,"op":"local.get $r","stack":[2,1],"loc":{"n":0,"r":1}},
      {"s":9,"fn":"isqrt","ln":13,"op":"i32.const 1","stack":[2,1,1],"loc":{"n":0,"r":1}},
      {"s":10,"fn":"isqrt","ln":14,"op":"i32.add","stack":[2,2],"loc":{"n":0,"r":1}},
      {"s":11,"fn":"isqrt","ln":15,"op":"i32.mul","stack":[4],"loc":{"n":0,"r":1}},
      {"s":12,"fn":"isqrt","ln":16,"op":"local.get $n","stack":[4,0],"loc":{"n":0,"r":1}},
      {"s":13,"fn":"isqrt","ln":17,"op":"i32.gt_u","stack":[1],"loc":{"n":0,"r":1}},
      {"s":14,"fn":"isqrt","ln":18,"op":"br_if $done","stack":[],"loc":{"n":0,"r":1}},
      {"s":15,"fn":"isqrt","ln":26,"op":"local.get $r","stack":[1],"loc":{"n":0,"r":1},"checks":[{"ln":1,"kind":"ensures","ok":false}]}
     ]
    }
   ],
   "correct_runs":{"calls":[["isqrt",[10]],["isqrt",[16]],["isqrt",[0]]],"results":[3,4,0],"total_steps":150,"spec_checks_failed":0}
  },
  {
   "id":"gcd",
   "title":"Euclid gcd",
   "lines":[
    "(@define gcd(x, y) = (y == 0 ? x : gcd(y, x % y)))",
    "(func $gcd (param $a (i32 | 0 <= v)) (param $b (i32 | 0 <= v)) (result (i32 | v == gcd(a, b)))",
    "  (local $x i32)",
    "  (local $y i32)",
    "  (local $t i32)",
    "  local.get $a",
    "  local.set $x",
    "  local.get $b",
    "  local.set $y",
    "  block $done",
    "    loop $euclid",
    "      (@invariant 0 <= x && 0 <= y && gcd(x, y) == gcd(a, b))",
    "      (@decreases y)",
    "      local.get $y",
    "      i32.eqz",
    "      br_if $done",
    "      local.get $x",
    "      local.get $y",
    "      i32.rem_u",
    "      local.set $t",
    "      local.get $y",
    "      local.set $x",
    "      local.get $t",
    "      local.set $y",
    "      br $euclid",
    "    end",
    "  end",
    "  local.get $x",
    ")"
   ],
   "functions":[{"name":"$gcd","line":2,"signature":"(func $gcd (param $a (i32 | 0 <= v)) (param $b (i32 | 0 <= v)) (result (i32 | v == gcd(a, b)))"}],
   "specs":[
    {"line":1,"text":"(@define gcd(x, y) = (y == 0 ? x : gcd(y, x % y)))"},
    {"line":12,"text":"(@invariant 0 <= x && 0 <= y && gcd(x, y) == gcd(a, b))"},
    {"line":13,"text":"(@decreases y)"}
   ],
   "obligations":[
    {"lines":[6,7,8,9],"code":"x := a; y := b","stack":"x == a, y == b","obligation":"-","status":"none"},
    {
     "lines":[11],
     "code":"loop $euclid",
     "obligation":"inv on entry: 0 <= a && 0 <= b && gcd(a,b) == gcd(a,b);  measure b >= 0",
     "status":"auto",
     "kind":"inv-entry"
    },
    {
     "lines":[14,15,16],
     "code":"local.get $y; i32.eqz; br_if $done",
     "stack":"taken: y == 0 / fallthrough: y != 0",
     "obligation":"-",
     "status":"auto",
     "kind":"branch"
    },
    {
     "lines":[17,18,19],
     "code":"local.get $x; local.get $y; i32.rem_u",
     "stack":"[(i32 | v == x % y && 0 <= v < y)]",
     "obligation":"no trap: y != 0;  u(x) == x and u(y) == y",
     "status":"inv",
     "kind":"trap"
    },
    {"lines":[20,21,22,23,24],"code":"t := x % y; x := y; y := t","stack":"x' == y, y' == x % y","obligation":"-","status":"none"},
    {
     "lines":[25],
     "code":"br $euclid",
     "obligation":"inv preserved: gcd(y, x % y) == gcd(x, y) == gcd(a, b);  measure 0 <= x % y < y",
     "status":"lemma",
     "kind":"inv-preserve"
    },
    {"lines":[28],"code":"local.get $x  (exit)","stack":"[(i32 | v == x)]","obligation":"post: x == gcd(a, b)","status":"inv","kind":"post"}
   ],
   "bugs":[
    {
     "id":"G1",
     "title":"guard tests the wrong variable",
     "category":"code",
     "flavor":"trap (bomb glyph)",
     "edit":"line 14: `local.get $y` -> `local.get $x`",
     "edits":[["replace",14,"local.get $y","local.get $x"]],
     "calls":[["gcd",[12,8]]],
     "expected_results":[4],
     "observed_results":["trap: integer divide by zero"],
     "runtime":"gcd(12, 8): traps \"integer divide by zero\" (V8: \"remainder by zero\") at line 19 on the 3rd iteration (x = 4, y = 0). gcd(0, 5) returns 0 without trapping (should be 5).",
     "static_failure":{"line":19,"obligation":"no trap: y != 0 at i32.rem_u","why":"the guard now establishes x != 0, not y != 0","status":"fails"},
     "first_dynamic_failure":{"s":36,"ln":19,"kind":"trap: integer divide by zero"},
     "trace":[
      {"s":6,"fn":"gcd","ln":11,"op":"loop $euclid","stack":[],"loc":{"a":12,"b":8,"x":12,"y":8,"t":0},"checks":[{"ln":12,"kind":"invariant","ok":true},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":12,"fn":"gcd","ln":19,"op":"i32.rem_u","stack":[4],"loc":{"a":12,"b":8,"x":12,"y":8,"t":0}},
      {"s":18,"fn":"gcd","ln":25,"op":"br $euclid","stack":[],"loc":{"a":12,"b":8,"x":8,"y":4,"t":4},"checks":[{"ln":12,"kind":"invariant","ok":true},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":24,"fn":"gcd","ln":19,"op":"i32.rem_u","stack":[0],"loc":{"a":12,"b":8,"x":8,"y":4,"t":4}},
      {"s":30,"fn":"gcd","ln":25,"op":"br $euclid","stack":[],"loc":{"a":12,"b":8,"x":4,"y":0,"t":0},"checks":[{"ln":12,"kind":"invariant","ok":true},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":36,"fn":"gcd","ln":19,"op":"i32.rem_u","stack":[4,0],"loc":{"a":12,"b":8,"x":4,"y":0,"t":0},"trap":"integer divide by zero"}
     ]
    },
    {
     "id":"G2",
     "title":"do-while rewrite (test at the bottom)",
     "category":"code",
     "flavor":"subtle edge case: correct for every b > 0, traps for b = 0",
     "edit":"delete lines 14-16 (the top-of-loop guard); line 24: `local.set $y` -> `local.tee $y`; line 25: `br $euclid` -> `br_if $euclid`",
     "edits":[["delete",14,16],["replace",24,"local.set $y","local.tee $y"],["replace",25,"br $euclid","br_if $euclid"]],
     "calls":[["gcd",[7,0]]],
     "expected_results":[7],
     "observed_results":["trap: integer divide by zero"],
     "runtime":"gcd(7, 0) traps at line 19 on step 9 (before any iteration completes). gcd(12, 8) = 4 as before.",
     "static_failure":{"line":19,"obligation":"no trap: y != 0 at i32.rem_u","why":"on the first iteration y == b and only b >= 0 is known","status":"fails"},
     "first_dynamic_failure":{"s":9,"ln":19,"kind":"trap: integer divide by zero"},
     "trace":[
      {"s":1,"fn":"gcd","ln":6,"op":"local.get $a","stack":[7],"loc":{"a":7,"b":0,"x":0,"y":0,"t":0},"checks":[{"ln":2,"kind":"requires","ok":true}]},
      {"s":2,"fn":"gcd","ln":7,"op":"local.set $x","stack":[],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0}},
      {"s":3,"fn":"gcd","ln":8,"op":"local.get $b","stack":[0],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0}},
      {"s":4,"fn":"gcd","ln":9,"op":"local.set $y","stack":[],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0}},
      {"s":5,"fn":"gcd","ln":10,"op":"block $done","stack":[],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0}},
      {"s":6,"fn":"gcd","ln":11,"op":"loop $euclid","stack":[],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0},"checks":[{"ln":12,"kind":"invariant","ok":true},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":7,"fn":"gcd","ln":17,"op":"local.get $x","stack":[7],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0}},
      {"s":8,"fn":"gcd","ln":18,"op":"local.get $y","stack":[7,0],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0}},
      {"s":9,"fn":"gcd","ln":19,"op":"i32.rem_u","stack":[7,0],"loc":{"a":7,"b":0,"x":7,"y":0,"t":0},"trap":"integer divide by zero"}
     ]
    },
    {
     "id":"G3",
     "title":"invariant too strong: \"y <= x\" (spec bug)",
     "category":"spec",
     "flavor":"spec bug: inductive but not established on entry",
     "edit":"line 12: `0 <= x && 0 <= y && ...` -> `0 <= y && y <= x && ...`",
     "edits":[["replace",12,"(@invariant 0 <= x && 0 <= y && gcd(x, y) == gcd(a, b))","(@invariant 0 <= y && y <= x && gcd(x, y) == gcd(a, b))"]],
     "calls":[["gcd",[4,6]]],
     "expected_results":[2],
     "observed_results":[2],
     "runtime":"no trap; gcd(4, 6) returns the correct 2. The invariant check fails once, on loop entry, and holds on every later iteration.",
     "static_failure":{
      "line":11,
      "obligation":"inv on entry: b <= a",
      "why":"nothing orders a and b. (Preservation does hold: y' = x % y < y = x'; Euclid's first iteration swaps a < b.)",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":6,"ln":12,"kind":"invariant"},
     "trace":[
      {"s":6,"fn":"gcd","ln":11,"op":"loop $euclid","stack":[],"loc":{"a":4,"b":6,"x":4,"y":6,"t":0},"checks":[{"ln":12,"kind":"invariant","ok":false},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":18,"fn":"gcd","ln":25,"op":"br $euclid","stack":[],"loc":{"a":4,"b":6,"x":6,"y":4,"t":4},"checks":[{"ln":12,"kind":"invariant","ok":true},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":30,"fn":"gcd","ln":25,"op":"br $euclid","stack":[],"loc":{"a":4,"b":6,"x":4,"y":2,"t":2},"checks":[{"ln":12,"kind":"invariant","ok":true},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":42,"fn":"gcd","ln":25,"op":"br $euclid","stack":[],"loc":{"a":4,"b":6,"x":2,"y":0,"t":0},"checks":[{"ln":12,"kind":"invariant","ok":true},{"ln":13,"kind":"decreases","ok":true}]},
      {"s":46,"fn":"gcd","ln":28,"op":"local.get $x","stack":[2],"loc":{"a":4,"b":6,"x":2,"y":0,"t":0},"checks":[{"ln":2,"kind":"ensures","ok":true}]}
     ]
    }
   ],
   "correct_runs":{"calls":[["gcd",[12,8]],["gcd",[1071,462]],["gcd",[0,5]]],"results":[4,21,5],"total_steps":102,"spec_checks_failed":0}
  },
  {
   "id":"pow_mod",
   "title":"Modular exponentiation (square-and-multiply)",
   "lines":[
    "(@define pow(x, e) = (e == 0 ? 1 : x * pow(x, e - 1)))",
    "(func $pow_mod (param $b (i32 | 0 <= v)) (param $e (i32 | 0 <= v)) (param $m (i32 | 1 <= v && v <= 65536)) (result (i32 | 0 <= v && v < m && v == pow(b, e) % m))",
    "  (local $acc i32)",
    "  (local $base i32)",
    "  (local $k i32)",
    "  i32.const 1",
    "  local.get $m",
    "  i32.rem_u",
    "  local.set $acc",
    "  local.get $b",
    "  local.get $m",
    "  i32.rem_u",
    "  local.set $base",
    "  local.get $e",
    "  local.set $k",
    "  block $done",
    "    loop $square",
    "      (@invariant 0 <= acc && acc < m && 0 <= base && base < m && 0 <= k)",
    "      (@invariant (acc * pow(base, k)) % m == pow(b, e) % m)",
    "      (@decreases k)",
    "      local.get $k",
    "      i32.eqz",
    "      br_if $done",
    "      local.get $k",
    "      i32.const 1",
    "      i32.and",
    "      if",
    "        local.get $acc",
    "        local.get $base",
    "        i32.mul",
    "        local.get $m",
    "        i32.rem_u",
    "        local.set $acc",
    "      end",
    "      local.get $base",
    "      local.get $base",
    "      i32.mul",
    "      local.get $m",
    "      i32.rem_u",
    "      local.set $base",
    "      local.get $k",
    "      i32.const 1",
    "      i32.shr_u",
    "      local.set $k",
    "      br $square",
    "    end",
    "  end",
    "  local.get $acc",
    ")"
   ],
   "functions":[
    {
     "name":"$pow_mod",
     "line":2,
     "signature":"(func $pow_mod (param $b (i32 | 0 <= v)) (param $e (i32 | 0 <= v)) (param $m (i32 | 1 <= v && v <= 65536)) (result (i32 | 0 <= v && v < m && v == pow(b, e) % m))"
    }
   ],
   "specs":[
    {"line":1,"text":"(@define pow(x, e) = (e == 0 ? 1 : x * pow(x, e - 1)))"},
    {"line":18,"text":"(@invariant 0 <= acc && acc < m && 0 <= base && base < m && 0 <= k)"},
    {"line":19,"text":"(@invariant (acc * pow(base, k)) % m == pow(b, e) % m)"},
    {"line":20,"text":"(@decreases k)"}
   ],
   "obligations":[
    {"lines":[6,7,8,9],"code":"acc := 1 rem_u m","stack":"[(i32 | v == 1 % m)]","obligation":"no trap: m != 0","status":"auto","kind":"trap"},
    {
     "lines":[10,11,12,13],
     "code":"base := b rem_u m",
     "stack":"[(i32 | v == b % m)]",
     "obligation":"no trap: m != 0;  u(b) == b",
     "status":"auto",
     "kind":"trap"
    },
    {"lines":[14,15],"code":"k := e","stack":"k == e","obligation":"-","status":"none"},
    {
     "lines":[17],
     "code":"loop $square",
     "obligation":"inv on entry: 0 <= acc < m, 0 <= base < m, 0 <= k;  (acc * base^k) % m == b^e % m;  measure k >= 0",
     "status":"lemma",
     "kind":"inv-entry"
    },
    {"lines":[21,22,23],"code":"k == 0 ? br_if $done","stack":"taken: k == 0 / fallthrough: k > 0","obligation":"-","status":"auto","kind":"branch"},
    {"lines":[24,25,26,27],"code":"k & 1; if","stack":"then: k odd / else: k even","obligation":"-","status":"auto","kind":"branch"},
    {
     "lines":[28,29,30],
     "code":"acc * base",
     "stack":"[(i32 | u(v) == acc * base)]",
     "obligation":"no unsigned overflow: acc * base < 2^32",
     "status":"lemma",
     "kind":"overflow"
    },
    {
     "lines":[31,32,33],
     "code":"rem_u m; acc :=",
     "stack":"acc' == (acc * base) % m, 0 <= acc' < m",
     "obligation":"no trap: m != 0",
     "status":"auto",
     "kind":"trap"
    },
    {
     "lines":[35,36,37],
     "code":"base * base",
     "stack":"[(i32 | u(v) == base * base)]",
     "obligation":"no unsigned overflow: base^2 < 2^32",
     "status":"lemma",
     "kind":"overflow"
    },
    {"lines":[38,39,40],"code":"rem_u m; base :=","stack":"base' == base^2 % m","obligation":"no trap: m != 0","status":"auto","kind":"trap"},
    {"lines":[41,42,43,44],"code":"k := k shr_u 1","stack":"k' == floor(k / 2)","obligation":"u(k) == k","status":"auto","kind":"type"},
    {
     "lines":[45],
     "code":"br $square",
     "obligation":"inv preserved: acc' * base'^k' == acc * base^k (mod m);  measure 0 <= k' < k",
     "status":"lemma",
     "kind":"inv-preserve"
    },
    {
     "lines":[48],
     "code":"local.get $acc  (exit)",
     "stack":"[(i32 | v == acc)]",
     "obligation":"post: 0 <= acc < m && acc == b^e % m",
     "status":"inv",
     "kind":"post"
    }
   ],
   "bugs":[
    {
     "id":"M1",
     "title":"accumulator not reduced mod m",
     "category":"code",
     "flavor":"edge case m = 1",
     "edit":"delete lines 7-8 (`local.get $m`, `i32.rem_u`), so acc starts at 1 instead of 1 % m",
     "edits":[["delete",7,8]],
     "calls":[["pow_mod",[5,0,1]]],
     "expected_results":[0],
     "observed_results":[1],
     "runtime":"pow_mod(5, 0, 1) returns 1, outside [0, 1). pow_mod(5, 3, 1) happens to return the right 0, yet the invariant check still fires on loop entry.",
     "static_failure":{"line":17,"obligation":"inv on entry: acc < m","why":"1 < m is not implied by 1 <= m","status":"fails"},
     "first_dynamic_failure":{"s":10,"ln":18,"kind":"invariant"},
     "trace":[
      {"s":1,"fn":"pow_mod","ln":6,"op":"i32.const 1","stack":[1],"loc":{"b":5,"e":0,"m":1,"acc":0,"base":0,"k":0},"checks":[{"ln":2,"kind":"requires","ok":true}]},
      {"s":2,"fn":"pow_mod","ln":9,"op":"local.set $acc","stack":[],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":3,"fn":"pow_mod","ln":10,"op":"local.get $b","stack":[5],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":4,"fn":"pow_mod","ln":11,"op":"local.get $m","stack":[5,1],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":5,"fn":"pow_mod","ln":12,"op":"i32.rem_u","stack":[0],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":6,"fn":"pow_mod","ln":13,"op":"local.set $base","stack":[],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":7,"fn":"pow_mod","ln":14,"op":"local.get $e","stack":[0],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":8,"fn":"pow_mod","ln":15,"op":"local.set $k","stack":[],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":9,"fn":"pow_mod","ln":16,"op":"block $done","stack":[],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":10,"fn":"pow_mod","ln":17,"op":"loop $square","stack":[],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0},"checks":[{"ln":18,"kind":"invariant","ok":false},{"ln":19,"kind":"invariant","ok":true},{"ln":20,"kind":"decreases","ok":true}]},
      {"s":11,"fn":"pow_mod","ln":21,"op":"local.get $k","stack":[0],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":12,"fn":"pow_mod","ln":22,"op":"i32.eqz","stack":[1],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":13,"fn":"pow_mod","ln":23,"op":"br_if $done","stack":[],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0}},
      {"s":14,"fn":"pow_mod","ln":48,"op":"local.get $acc","stack":[1],"loc":{"b":5,"e":0,"m":1,"acc":1,"base":0,"k":0},"checks":[{"ln":2,"kind":"ensures","ok":false}]}
     ]
    },
    {
     "id":"M2",
     "title":"signed remainder after a product that overflows 2^31",
     "category":"code",
     "flavor":"subtle: correct whenever m <= 46341",
     "edit":"line 39: `i32.rem_u` -> `i32.rem_s`",
     "edits":[["replace",39,"i32.rem_u","i32.rem_s"]],
     "calls":[["pow_mod",[49999,4,50000]]],
     "expected_results":[1],
     "observed_results":[17025],
     "runtime":"pow_mod(49999, 4, 50000) returns 17025 (expected 1). pow_mod(49999, 2, 50000) returns the correct 1 because two wrap errors cancel mod 50000, but the invariant check still fires.",
     "static_failure":{
      "line":39,
      "obligation":"inv: 0 <= base' (via the refined result of rem)",
      "why":"rem_s reads base*base as signed; base <= 65535 so base^2 can exceed 2^31-1 and wrap negative, and rem_s of a negative is negative",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":30,"ln":18,"kind":"invariant"},
     "trace":[
      {"s":12,"fn":"pow_mod","ln":17,"op":"loop $square","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":1,"base":49999,"k":4},"checks":[{"ln":18,"kind":"invariant","ok":true},{"ln":19,"kind":"invariant","ok":true},{"ln":20,"kind":"decreases","ok":true}]},
      {"s":25,"fn":"pow_mod","ln":40,"op":"local.set $base","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":1,"base":-17295,"k":4}},
      {"s":30,"fn":"pow_mod","ln":45,"op":"br $square","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":1,"base":-17295,"k":2},"checks":[{"ln":18,"kind":"invariant","ok":false},{"ln":19,"kind":"invariant","ok":false},{"ln":20,"kind":"decreases","ok":true}]},
      {"s":43,"fn":"pow_mod","ln":40,"op":"local.set $base","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":1,"base":17025,"k":2}},
      {"s":48,"fn":"pow_mod","ln":45,"op":"br $square","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":1,"base":17025,"k":1},"checks":[{"ln":18,"kind":"invariant","ok":true},{"ln":19,"kind":"invariant","ok":false},{"ln":20,"kind":"decreases","ok":true}]},
      {"s":61,"fn":"pow_mod","ln":33,"op":"local.set $acc","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":17025,"base":17025,"k":1}},
      {"s":67,"fn":"pow_mod","ln":40,"op":"local.set $base","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":17025,"base":625,"k":1}},
      {"s":72,"fn":"pow_mod","ln":45,"op":"br $square","stack":[],"loc":{"b":49999,"e":4,"m":50000,"acc":17025,"base":625,"k":0},"checks":[{"ln":18,"kind":"invariant","ok":true},{"ln":19,"kind":"invariant","ok":false},{"ln":20,"kind":"decreases","ok":true}]},
      {"s":76,"fn":"pow_mod","ln":48,"op":"local.get $acc","stack":[17025],"loc":{"b":49999,"e":4,"m":50000,"acc":17025,"base":625,"k":0},"checks":[{"ln":2,"kind":"ensures","ok":false}]}
     ]
    }
   ],
   "correct_runs":{"calls":[["pow_mod",[2,10,1000]],["pow_mod",[3,200,65536]],["pow_mod",[5,0,1]]],"results":[24,45217,0],"total_steps":294,"spec_checks_failed":0}
  },
  {
   "id":"hashtable",
   "title":"Open-addressing hash table (8 slots, linear probing, tombstones)",
   "lines":[
    "(memory 1)",
    "(global $used (mut i32) (i32.const 0))",
    "(@ghost global $M (Map i32 i32))",
    "(@define EMPTY = 0, FULL = 1, TOMB = 2, CAP = 8, BASE = 65440)",
    "(@define st(s) = load(BASE + 12*s), key(s) = load(BASE + 12*s + 4), val(s) = load(BASE + 12*s + 8))",
    "(@define h(k) = k & 7, at(k, d) = (h(k) + d) & 7, dist(k, s) = (s - h(k)) & 7)",
    "(@define R0 = forall s in 0..7. st(s) in {EMPTY, FULL, TOMB})",
    "(@define R1 = forall s. st(s) == FULL ==> key(s) in M && M[key(s)] == val(s))",
    "(@define R2 = forall k in M. #{s | st(s) == FULL && key(s) == k} == 1)",
    "(@define R3 = forall s. st(s) == FULL ==> forall d <= dist(key(s), s). st(at(key(s), d)) != EMPTY)",
    "(@define R4 = #{s | st(s) == FULL} == |M| && used == #{s | st(s) != EMPTY} && used < CAP)",
    "(@define R = R0 && R1 && R2 && R3 && R4)",
    "(func $slot (param $i (i32 | 0 <= v && v < CAP)) (result (i32 | v == BASE + 12*i))",
    "  local.get $i",
    "  i32.const 12",
    "  i32.mul",
    "  i32.const 65440",
    "  i32.add",
    ")",
    "(func $find (param $k i32) (result (i32 | (v == -1 && !(k in M)) || (0 <= v && v < CAP && st(v) == FULL && key(v) == k)))",
    "  (@requires R)",
    "  (local $i i32)",
    "  (local $p i32)",
    "  (@ghost local $j i32)",
    "  local.get $k",
    "  i32.const 7",
    "  i32.and",
    "  local.set $i",
    "  loop $probe",
    "    (@invariant 0 <= j && j <= used && i == at(k, j))",
    "    (@invariant forall d < j. st(at(k, d)) == TOMB || (st(at(k, d)) == FULL && key(at(k, d)) != k))",
    "    (@decreases CAP - j)",
    "    local.get $i",
    "    call $slot",
    "    local.tee $p",
    "    i32.load",
    "    i32.const 1",
    "    i32.lt_u",
    "    if",
    "      i32.const -1",
    "      return",
    "    end",
    "    local.get $p",
    "    i32.load",
    "    i32.const 1",
    "    i32.eq",
    "    local.get $p",
    "    i32.load offset=4",
    "    local.get $k",
    "    i32.eq",
    "    i32.and",
    "    if",
    "      local.get $i",
    "      return",
    "    end",
    "    local.get $i",
    "    i32.const 1",
    "    i32.add",
    "    i32.const 7",
    "    i32.and",
    "    local.set $i",
    "    (@ghost j := j + 1)",
    "    br $probe",
    "  end",
    "  unreachable",
    ")",
    "(func $lookup (param $k i32) (param $dflt i32) (result (i32 | v == (k in M ? M[k] : dflt)))",
    "  (@requires R)",
    "  (@ensures R)",
    "  (local $i i32)",
    "  local.get $k",
    "  call $find",
    "  local.tee $i",
    "  i32.const 0",
    "  i32.lt_s",
    "  if",
    "    local.get $dflt",
    "    return",
    "  end",
    "  local.get $i",
    "  call $slot",
    "  i32.load offset=8",
    ")",
    "(func $delete (param $k i32) (result (i32 | v == (k in old(M) ? 1 : 0)))",
    "  (@requires R)",
    "  (@ensures R && M == old(M) \\ {k})",
    "  (local $i i32)",
    "  local.get $k",
    "  call $find",
    "  local.tee $i",
    "  i32.const 0",
    "  i32.lt_s",
    "  if",
    "    i32.const 0",
    "    return",
    "  end",
    "  local.get $i",
    "  call $slot",
    "  i32.const 2",
    "  i32.store",
    "  (@ghost M := M \\ {k})",
    "  i32.const 1",
    ")",
    "(func $insert (param $k i32) (param $x i32) (result (i32 | v == 1 || (v == 0 && !(k in M) && used == CAP - 1)))",
    "  (@requires R)",
    "  (@ensures R && M == (result == 1 ? old(M)[k := x] : old(M)))",
    "  (local $i i32)",
    "  (local $p i32)",
    "  (@ghost local $j i32)",
    "  local.get $k",
    "  call $find",
    "  local.tee $i",
    "  i32.const 0",
    "  i32.ge_s",
    "  if",
    "    local.get $i",
    "    call $slot",
    "    local.get $x",
    "    i32.store offset=8",
    "    (@ghost M := M[k := x])",
    "    i32.const 1",
    "    return",
    "  end",
    "  global.get $used",
    "  i32.const 7",
    "  i32.ge_u",
    "  if",
    "    i32.const 0",
    "    return",
    "  end",
    "  local.get $k",
    "  i32.const 7",
    "  i32.and",
    "  local.set $i",
    "  loop $free",
    "    (@invariant !(k in M) && 0 <= j && j <= used && i == at(k, j))",
    "    (@invariant forall d < j. st(at(k, d)) != EMPTY)",
    "    (@decreases CAP - j)",
    "    local.get $i",
    "    call $slot",
    "    local.tee $p",
    "    i32.load",
    "    if",
    "      local.get $i",
    "      i32.const 1",
    "      i32.add",
    "      i32.const 7",
    "      i32.and",
    "      local.set $i",
    "      (@ghost j := j + 1)",
    "      br $free",
    "    end",
    "  end",
    "  local.get $p",
    "  i32.const 1",
    "  i32.store",
    "  local.get $p",
    "  local.get $k",
    "  i32.store offset=4",
    "  local.get $p",
    "  local.get $x",
    "  i32.store offset=8",
    "  global.get $used",
    "  i32.const 1",
    "  i32.add",
    "  global.set $used",
    "  (@ghost M := M[k := x])",
    "  i32.const 1",
    ")"
   ],
   "functions":[
    {"name":"$slot","line":13,"signature":"(func $slot (param $i (i32 | 0 <= v && v < CAP)) (result (i32 | v == BASE + 12*i))"},
    {
     "name":"$find",
     "line":20,
     "signature":"(func $find (param $k i32) (result (i32 | (v == -1 && !(k in M)) || (0 <= v && v < CAP && st(v) == FULL && key(v) == k)))"
    },
    {"name":"$lookup","line":67,"signature":"(func $lookup (param $k i32) (param $dflt i32) (result (i32 | v == (k in M ? M[k] : dflt)))"},
    {"name":"$delete","line":84,"signature":"(func $delete (param $k i32) (result (i32 | v == (k in old(M) ? 1 : 0)))"},
    {
     "name":"$insert",
     "line":104,
     "signature":"(func $insert (param $k i32) (param $x i32) (result (i32 | v == 1 || (v == 0 && !(k in M) && used == CAP - 1)))"
    }
   ],
   "specs":[
    {"line":3,"text":"(@ghost global $M (Map i32 i32))"},
    {"line":4,"text":"(@define EMPTY = 0, FULL = 1, TOMB = 2, CAP = 8, BASE = 65440)"},
    {"line":5,"text":"(@define st(s) = load(BASE + 12*s), key(s) = load(BASE + 12*s + 4), val(s) = load(BASE + 12*s + 8))"},
    {"line":6,"text":"(@define h(k) = k & 7, at(k, d) = (h(k) + d) & 7, dist(k, s) = (s - h(k)) & 7)"},
    {"line":7,"text":"(@define R0 = forall s in 0..7. st(s) in {EMPTY, FULL, TOMB})"},
    {"line":8,"text":"(@define R1 = forall s. st(s) == FULL ==> key(s) in M && M[key(s)] == val(s))"},
    {"line":9,"text":"(@define R2 = forall k in M. #{s | st(s) == FULL && key(s) == k} == 1)"},
    {"line":10,"text":"(@define R3 = forall s. st(s) == FULL ==> forall d <= dist(key(s), s). st(at(key(s), d)) != EMPTY)"},
    {"line":11,"text":"(@define R4 = #{s | st(s) == FULL} == |M| && used == #{s | st(s) != EMPTY} && used < CAP)"},
    {"line":12,"text":"(@define R = R0 && R1 && R2 && R3 && R4)"},
    {"line":21,"text":"(@requires R)"},
    {"line":24,"text":"(@ghost local $j i32)"},
    {"line":30,"text":"(@invariant 0 <= j && j <= used && i == at(k, j))"},
    {"line":31,"text":"(@invariant forall d < j. st(at(k, d)) == TOMB || (st(at(k, d)) == FULL && key(at(k, d)) != k))"},
    {"line":32,"text":"(@decreases CAP - j)"},
    {"line":62,"text":"(@ghost j := j + 1)"},
    {"line":68,"text":"(@requires R)"},
    {"line":69,"text":"(@ensures R)"},
    {"line":85,"text":"(@requires R)"},
    {"line":86,"text":"(@ensures R && M == old(M) \\ {k})"},
    {"line":101,"text":"(@ghost M := M \\ {k})"},
    {"line":105,"text":"(@requires R)"},
    {"line":106,"text":"(@ensures R && M == (result == 1 ? old(M)[k := x] : old(M)))"},
    {"line":109,"text":"(@ghost local $j i32)"},
    {"line":120,"text":"(@ghost M := M[k := x])"},
    {"line":136,"text":"(@invariant !(k in M) && 0 <= j && j <= used && i == at(k, j))"},
    {"line":137,"text":"(@invariant forall d < j. st(at(k, d)) != EMPTY)"},
    {"line":138,"text":"(@decreases CAP - j)"},
    {"line":150,"text":"(@ghost j := j + 1)"},
    {"line":167,"text":"(@ghost M := M[k := x])"}
   ],
   "obligations":[
    {
     "lines":[14,15,16,17,18],
     "code":"$slot: i*12 + 65440",
     "stack":"[(i32 | v == BASE + 12*i)]",
     "obligation":"no overflow; post v == BASE + 12*i",
     "status":"auto",
     "kind":"post"
    },
    {"lines":[25,26,27,28],"code":"find: i := k & 7","stack":"i == h(k), 0 <= i < 8","obligation":"-","status":"auto","kind":"type"},
    {
     "lines":[29],
     "code":"loop $probe",
     "obligation":"inv on entry: j == 0 <= used, i == at(k,0), path-so-far vacuous;  measure CAP - 0 >= 0",
     "status":"auto",
     "kind":"inv-entry"
    },
    {
     "lines":[33,34,35],
     "code":"call $slot; local.tee $p",
     "stack":"[(i32 | v == BASE + 12*i)]",
     "obligation":"pre of $slot: 0 <= i < CAP",
     "status":"inv",
     "kind":"pre"
    },
    {"lines":[36],"code":"i32.load","stack":"[(i32 | v == st(i))]","obligation":"in bounds: p + 4 <= 65536","status":"auto","kind":"trap"},
    {
     "lines":[37,38,39,40,41],
     "code":"st(i) < FULL ? return -1",
     "stack":"[(i32 | v == -1)]",
     "obligation":"post of $find: !(k in M)",
     "status":"inv",
     "kind":"post"
    },
    {
     "lines":[43,44,45,46,47,48,49,50,51],
     "code":"(st(i) == FULL) & (key(i) == k)",
     "stack":"[(i32 | v == (st(i) == FULL && key(i) == k ? 1 : 0))]",
     "obligation":"in bounds: p + 8 <= 65536",
     "status":"auto",
     "kind":"trap"
    },
    {
     "lines":[52,53,54],
     "code":"match ? return i",
     "stack":"[(i32 | v == i)]",
     "obligation":"post of $find: 0 <= i < CAP && st(i) == FULL && key(i) == k",
     "status":"auto",
     "kind":"post"
    },
    {"lines":[56,57,58,59,60,61],"code":"i := (i + 1) & 7","stack":"i' == at(k, j + 1)","obligation":"-","status":"auto","kind":"type"},
    {
     "lines":[62,63],
     "code":"j := j + 1; br $probe",
     "obligation":"inv preserved: slot at distance j is TOMB or FULL-with-other-key; j + 1 <= used;  measure CAP - (j+1) < CAP - j, >= 0",
     "status":"lemma",
     "kind":"inv-preserve"
    },
    {"lines":[65],"code":"unreachable","obligation":"this point is dead","status":"auto","kind":"dead"},
    {
     "lines":[71,72,73,74,75,76,77,78],
     "code":"lookup: i := find(k); i < 0 ? return dflt",
     "stack":"[(i32 | v == dflt)]",
     "obligation":"pre of $find: R;  post: !(k in M) so result == dflt",
     "status":"auto",
     "kind":"post"
    },
    {
     "lines":[80,81,82],
     "code":"lookup: load val(i)",
     "stack":"[(i32 | v == val(i))]",
     "obligation":"post: val(i) == M[k];  R preserved",
     "status":"inv",
     "kind":"post"
    },
    {
     "lines":[88,89,90,91,92,93,94,95,96],
     "code":"delete: i := find(k); absent ? return 0",
     "stack":"[(i32 | v == 0)]",
     "obligation":"post: k not in old(M), M unchanged, R unchanged",
     "status":"auto",
     "kind":"post"
    },
    {
     "lines":[97,98,99,100,101],
     "code":"delete: st(i) := TOMB; M := M \\ {k}",
     "obligation":"R after: R1 (slot i no longer FULL), R2 (k had exactly one slot), R3 (TOMB is not EMPTY, so no probe path gains an EMPTY), R4 (#FULL - 1 == |M| - 1; used unchanged)",
     "status":"inv",
     "kind":"R"
    },
    {
     "lines":[110,111,112,113,114,115],
     "code":"insert: i := find(k); i >= 0 ?",
     "stack":"then: st(i) == FULL && key(i) == k / else: !(k in M)",
     "obligation":"pre of $find: R",
     "status":"auto",
     "kind":"pre"
    },
    {
     "lines":[116,117,118,119,120],
     "code":"insert(update): val(i) := x; M := M[k := x]",
     "obligation":"R1 for slot i with the new M; other clauses untouched",
     "status":"auto",
     "kind":"R"
    },
    {
     "lines":[124,125,126,127,128,129,130],
     "code":"used >= CAP-1 ? return 0",
     "stack":"[(i32 | v == 0)]",
     "obligation":"post: !(k in M) && used == CAP - 1",
     "status":"auto",
     "kind":"post"
    },
    {
     "lines":[131,132,133,134,135],
     "code":"i := h(k); loop $free",
     "obligation":"inv on entry: !(k in M) (from find), j == 0, i == at(k, 0)",
     "status":"auto",
     "kind":"inv-entry"
    },
    {"lines":[139,140,141,142,143],"code":"st(i) != EMPTY ?","obligation":"pre of $slot: 0 <= i < CAP;  load in bounds","status":"inv","kind":"pre"},
    {
     "lines":[144,145,146,147,148,149,150,151],
     "code":"i := (i+1) & 7; j := j + 1; br $free",
     "obligation":"inv preserved (path so far non-EMPTY; j + 1 <= used);  measure",
     "status":"lemma",
     "kind":"inv-preserve"
    },
    {
     "lines":[154,155,156,157,158,159,160,161,162],
     "code":"write FULL, k, x into EMPTY slot i",
     "obligation":"stores in bounds",
     "status":"auto",
     "kind":"trap"
    },
    {
     "lines":[163,164,165,166,167],
     "code":"used := used + 1; M := M[k := x]",
     "obligation":"R after: R1 (new slot maps k to x), R2 (k was absent: inv), R3 (path h(k)..i was non-EMPTY: inv; turning an EMPTY into FULL never breaks another key's path), R4 (#FULL + 1 == |M| + 1; used + 1 == #non-EMPTY because slot i WAS EMPTY; used + 1 < CAP because the check at 124-126 gave used < CAP - 1)",
     "status":"inv",
     "kind":"R"
    }
   ],
   "bugs":[
    {
     "id":"Ha",
     "title":"(a) probe index not wrapped",
     "category":"code",
     "flavor":"out-of-bounds trap",
     "edit":"delete lines 147-148 (`i32.const 7`, `i32.and`) in $insert's free-slot loop",
     "edits":[["delete",147,148]],
     "calls":[["insert",[7,70]],["insert",[15,150]]],
     "expected_results":[1,1],
     "observed_results":[1,"trap: out of bounds memory access"],
     "runtime":"insert(15, 150) traps \"out of bounds memory access\" at line 142 (address 65536 = BASE + 12*8).",
     "static_failure":{
      "line":140,
      "obligation":"pre of $slot: 0 <= i < CAP",
      "why":"after line 146 i == at(k, j) + 1, which is 8 when at(k, j) == 7. The back-edge invariant i == at(k, j+1) (line 136) fails first",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":143,"ln":136,"kind":"invariant"},
     "R_violation":"none: the trap fires before any write. With BASE = 0 instead of 65440 there would be no trap: \"slot 8\" (bytes 96..107) reads as EMPTY, the entry is written outside the table, and R2 (ii) fails because 15 is in M but in no FULL slot",
     "op_boundaries":[{"call":["insert",[7,70]],"returned_at_step":61,"R_false":[]}],
     "trace":[
      {"s":17,"fn":"find","ln":36,"op":"i32.load","stack":[0],"loc":{"k":7,"i":7,"p":65524,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":22,"fn":"find","ln":41,"op":"return","stack":[-1],"loc":{"k":7,"i":7,"p":65524,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":46,"fn":"insert","ln":142,"op":"i32.load","stack":[0],"loc":{"k":7,"x":70,"i":7,"p":65524,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":56,"fn":"insert","ln":162,"op":"i32.store offset=8","stack":[],"loc":{"k":7,"x":70,"i":7,"p":65524,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]]},
      {"s":61,"fn":"insert","ln":168,"op":"i32.const 1","stack":[1],"loc":{"k":7,"x":70,"i":7,"p":65524,"j":0},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]],"R":{"o":true,"i":true,"ii":true,"iii":true,"iv":true},"checks":[{"ln":104,"kind":"ensures","ok":true},{"ln":106,"kind":"ensures","ok":true}]},
      {"s":78,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":15,"i":7,"p":65524,"j":0},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]]},
      {"s":108,"fn":"find","ln":36,"op":"i32.load","stack":[0],"loc":{"k":15,"i":0,"p":65440,"j":1},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]]},
      {"s":113,"fn":"find","ln":41,"op":"return","stack":[-1],"loc":{"k":15,"i":0,"p":65440,"j":1},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]]},
      {"s":137,"fn":"insert","ln":142,"op":"i32.load","stack":[1],"loc":{"k":15,"x":150,"i":7,"p":65524,"j":0},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]]},
      {"s":143,"fn":"insert","ln":151,"op":"br $free","stack":[],"loc":{"k":15,"x":150,"i":8,"p":65524,"j":1},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]],"checks":[{"ln":136,"kind":"invariant","ok":false},{"ln":137,"kind":"invariant","ok":true},{"ln":138,"kind":"decreases","ok":true}]},
      {"s":145,"fn":"insert","ln":140,"op":"call $slot  (enter)","stack":[],"loc":{"k":15,"x":150,"i":8,"p":65524,"j":1},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]],"checks":[{"ln":13,"kind":"requires","ok":false}]},
      {"s":153,"fn":"insert","ln":142,"op":"i32.load","stack":[65536],"loc":{"k":15,"x":150,"i":8,"p":65536,"j":1},"used":1,"M":[[7,70]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1,7,70]],"trap":"out of bounds memory access"}
     ]
    },
    {
     "id":"Hb",
     "title":"(b) lookup treats TOMBSTONE as EMPTY",
     "category":"code",
     "flavor":"key becomes unreachable",
     "edit":"line 38: `i32.lt_u` (state < FULL, i.e. EMPTY) -> `i32.ne` (state != FULL, i.e. EMPTY or TOMB)",
     "edits":[["replace",38,"i32.lt_u","i32.ne"]],
     "calls":[["insert",[3,30]],["insert",[11,110]],["delete",[3]],["lookup",[11,-1]]],
     "expected_results":[1,1,1,110],
     "observed_results":[1,1,1,-1],
     "runtime":"lookup(11, -1) returns -1 (expected 110). No trap. Cascade: a later insert(11, 111) sees \"absent\" and writes a second FULL slot for 11 (slot 5), now breaking R2 (ii).",
     "static_failure":{
      "line":41,
      "obligation":"post of $find: !(k in M)",
      "why":"the path condition at the early return is now st(i) in {EMPTY, TOMB}; R3 (iii) only promises no EMPTY on a key's probe path, so a TOMB there says nothing about k",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":241,"ln":20,"kind":"ensures"},
     "R_violation":"R stays TRUE at every step (delete correctly writes TOMB). What breaks is the stronger invariant the buggy lookup silently relies on, iii_strong = \"no non-FULL slot on any key's probe path\". It becomes false at step 217 (delete's i32.store, line 100), when slot 3 on key 11's path turns TOMB. The first obligation to fail at runtime is $find's postcondition, at step 241 (find returns -1 to lookup)",
     "op_boundaries":[
      {"call":["insert",[3,30]],"returned_at_step":61,"R_false":[]},
      {"call":["insert",[11,110]],"returned_at_step":170,"R_false":[]},
      {"call":["delete",[3]],"returned_at_step":218,"R_false":[]},
      {"call":["lookup",[11,-1]],"returned_at_step":247,"R_false":[]}
     ],
     "trace":[
      {"s":17,"fn":"find","ln":36,"op":"i32.load","stack":[0],"loc":{"k":3,"i":3,"p":65476,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":22,"fn":"find","ln":41,"op":"return","stack":[-1],"loc":{"k":3,"i":3,"p":65476,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":46,"fn":"insert","ln":142,"op":"i32.load","stack":[0],"loc":{"k":3,"x":30,"i":3,"p":65476,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":56,"fn":"insert","ln":162,"op":"i32.store offset=8","stack":[],"loc":{"k":3,"x":30,"i":3,"p":65476,"j":0},"used":0,"M":[],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":61,"fn":"insert","ln":168,"op":"i32.const 1","stack":[1],"loc":{"k":3,"x":30,"i":3,"p":65476,"j":0},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":true,"ii":true,"iii":true,"iv":true},"iii_strong":true,"checks":[{"ln":104,"kind":"ensures","ok":true},{"ln":106,"kind":"ensures","ok":true}]},
      {"s":78,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":11,"i":3,"p":65476,"j":0},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":87,"fn":"find","ln":48,"op":"i32.load offset=4","stack":[1,3],"loc":{"k":11,"i":3,"p":65476,"j":0},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":108,"fn":"find","ln":36,"op":"i32.load","stack":[0],"loc":{"k":11,"i":4,"p":65488,"j":1},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":113,"fn":"find","ln":41,"op":"return","stack":[-1],"loc":{"k":11,"i":4,"p":65488,"j":1},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":137,"fn":"insert","ln":142,"op":"i32.load","stack":[1],"loc":{"k":11,"x":110,"i":3,"p":65476,"j":0},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":155,"fn":"insert","ln":142,"op":"i32.load","stack":[0],"loc":{"k":11,"x":110,"i":4,"p":65488,"j":1},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":165,"fn":"insert","ln":162,"op":"i32.store offset=8","stack":[],"loc":{"k":11,"x":110,"i":4,"p":65488,"j":1},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":170,"fn":"insert","ln":168,"op":"i32.const 1","stack":[1],"loc":{"k":11,"x":110,"i":4,"p":65488,"j":1},"used":2,"M":[[3,30],[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":true,"ii":true,"iii":true,"iv":true},"iii_strong":true,"checks":[{"ln":104,"kind":"ensures","ok":true},{"ln":106,"kind":"ensures","ok":true}]},
      {"s":187,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":3,"i":3,"p":65476,"j":0},"used":2,"M":[[3,30],[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":196,"fn":"find","ln":48,"op":"i32.load offset=4","stack":[1,3],"loc":{"k":3,"i":3,"p":65476,"j":0},"used":2,"M":[[3,30],[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":202,"fn":"find","ln":54,"op":"return","stack":[3],"loc":{"k":3,"i":3,"p":65476,"j":0},"used":2,"M":[[3,30],[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":true},
      {"s":217,"fn":"delete","ln":100,"op":"i32.store","stack":[],"loc":{"k":3,"i":3},"used":2,"M":[[3,30],[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[2,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":false},
      {"s":218,"fn":"delete","ln":102,"op":"i32.const 1","stack":[1],"loc":{"k":3,"i":3},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[2,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":true,"ii":true,"iii":true,"iv":true},"iii_strong":false,"checks":[{"ln":84,"kind":"ensures","ok":true},{"ln":86,"kind":"ensures","ok":true}]},
      {"s":235,"fn":"find","ln":36,"op":"i32.load","stack":[2],"loc":{"k":11,"i":3,"p":65476,"j":0},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[2,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":false},
      {"s":237,"fn":"find","ln":38,"op":"i32.ne","stack":[1],"loc":{"k":11,"i":3,"p":65476,"j":0},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[2,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":false},
      {"s":240,"fn":"find","ln":41,"op":"return","stack":[-1],"loc":{"k":11,"i":3,"p":65476,"j":0},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[2,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":false},
      {"s":241,"fn":"lookup","ln":72,"op":"call $find  (return)","stack":[-1],"loc":{"k":11,"dflt":-1,"i":0},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[2,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"iii_strong":false,"checks":[{"ln":20,"kind":"ensures","ok":false}]},
      {"s":247,"fn":"lookup","ln":78,"op":"return","stack":[-1],"loc":{"k":11,"dflt":-1,"i":-1},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[2,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":true,"ii":true,"iii":true,"iv":true},"iii_strong":false,"checks":[{"ln":67,"kind":"ensures","ok":false},{"ln":69,"kind":"ensures","ok":true}]}
     ]
    },
    {
     "id":"Hb_prime",
     "title":"(b') delete writes EMPTY instead of TOMBSTONE",
     "category":"code",
     "flavor":"the same symptom, caused on the delete side",
     "edit":"line 99: `i32.const 2` -> `i32.const 0`",
     "edits":[["replace",99,"i32.const 2","i32.const 0"]],
     "calls":[["insert",[3,30]],["insert",[11,110]],["delete",[3]],["lookup",[11,-1]]],
     "expected_results":[1,1,1,110],
     "observed_results":[1,1,1,-1],
     "runtime":"lookup(11, -1) returns -1 (expected 110).",
     "static_failure":{
      "line":100,
      "obligation":"R3 (iii) after delete's store",
      "why":"writing EMPTY into slot 3 places an EMPTY on key 11's path h(11)=3 .. 4",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":218,"ln":86,"kind":"ensures"},
     "R_violation":"R3 (iii) and R4 (iv: used == #non-EMPTY) become false at step 217 (line 100, the store)",
     "op_boundaries":[
      {"call":["insert",[3,30]],"returned_at_step":61,"R_false":[]},
      {"call":["insert",[11,110]],"returned_at_step":170,"R_false":[]},
      {"call":["delete",[3]],"returned_at_step":218,"R_false":["iii","iv"]},
      {"call":["lookup",[11,-1]],"returned_at_step":247,"R_false":["iii","iv"]}
     ],
     "trace":[
      {"s":217,"fn":"delete","ln":100,"op":"i32.store","stack":[],"loc":{"k":3,"i":3},"used":2,"M":[[3,30],[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":218,"fn":"delete","ln":102,"op":"i32.const 1","stack":[1],"loc":{"k":3,"i":3},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":true,"ii":true,"iii":false,"iv":false},"checks":[{"ln":84,"kind":"ensures","ok":true},{"ln":86,"kind":"ensures","ok":false}]},
      {"s":235,"fn":"find","ln":36,"op":"i32.load","stack":[0],"loc":{"k":11,"i":3,"p":65476,"j":0},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":240,"fn":"find","ln":41,"op":"return","stack":[-1],"loc":{"k":11,"i":3,"p":65476,"j":0},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":247,"fn":"lookup","ln":78,"op":"return","stack":[-1],"loc":{"k":11,"dflt":-1,"i":-1},"used":2,"M":[[11,110]],"slots":[[0,0,0],[0,0,0],[0,0,0],[0,3,30],[1,11,110],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":true,"ii":true,"iii":false,"iv":false},"checks":[{"ln":67,"kind":"ensures","ok":false},{"ln":69,"kind":"ensures","ok":false}]}
     ]
    },
    {
     "id":"Hc",
     "title":"(c) insert does not check for an existing key",
     "category":"code",
     "flavor":"duplicate key",
     "edit":"delete lines 110-123 (the find-and-update group at the top of $insert)",
     "edits":[["delete",110,123]],
     "calls":[["insert",[3,30]],["insert",[3,31]],["lookup",[3,-1]]],
     "expected_results":[1,1,31],
     "observed_results":[1,1,30],
     "runtime":"insert(3, 31) returns 1 but leaves two FULL slots with key 3; lookup(3, -1) returns the stale 30 (expected 31). No trap.",
     "static_failure":{"line":135,"obligation":"inv on entry of $free: !(k in M)","why":"nothing establishes that k is absent any more","status":"fails"},
     "first_dynamic_failure":{"s":43,"ln":136,"kind":"invariant"},
     "R_violation":"R2 (ii): from step 78 (line 159, key store) slots 3 and 4 are both FULL with key 3. At insert's return (step 86) R1 (i) is false too (ghost M[3] = 31 but slot 3 still holds 30) and so is R4 (iv) (#FULL = 2 but |M| = 1)",
     "op_boundaries":[
      {"call":["insert",[3,30]],"returned_at_step":34,"R_false":[]},
      {"call":["insert",[3,31]],"returned_at_step":86,"R_false":["i","ii","iv"]},
      {"call":["lookup",[3,-1]],"returned_at_step":132,"R_false":["i","ii","iv"]}
     ],
     "trace":[
      {"s":43,"fn":"insert","ln":135,"op":"loop $free","stack":[],"loc":{"k":3,"x":31,"i":3,"p":0,"j":0},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],"checks":[{"ln":136,"kind":"invariant","ok":false},{"ln":137,"kind":"invariant","ok":true},{"ln":138,"kind":"decreases","ok":true}]},
      {"s":53,"fn":"insert","ln":142,"op":"i32.load","stack":[1],"loc":{"k":3,"x":31,"i":3,"p":65476,"j":0},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":71,"fn":"insert","ln":142,"op":"i32.load","stack":[0],"loc":{"k":3,"x":31,"i":4,"p":65488,"j":1},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":78,"fn":"insert","ln":159,"op":"i32.store offset=4","stack":[],"loc":{"k":3,"x":31,"i":4,"p":65488,"j":1},"used":1,"M":[[3,30]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,3,0],[0,0,0],[0,0,0],[0,0,0]]},
      {"s":86,"fn":"insert","ln":168,"op":"i32.const 1","stack":[1],"loc":{"k":3,"x":31,"i":4,"p":65488,"j":1},"used":2,"M":[[3,31]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,3,31],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":false,"ii":false,"iii":true,"iv":false},"checks":[{"ln":104,"kind":"ensures","ok":true},{"ln":106,"kind":"ensures","ok":false}]},
      {"s":132,"fn":"lookup","ln":82,"op":"i32.load offset=8","stack":[30],"loc":{"k":3,"dflt":-1,"i":3},"used":2,"M":[[3,31]],"slots":[[0,0,0],[0,0,0],[0,0,0],[1,3,30],[1,3,31],[0,0,0],[0,0,0],[0,0,0]],"R":{"o":true,"i":false,"ii":false,"iii":true,"iv":false},"checks":[{"ln":67,"kind":"ensures","ok":false},{"ln":69,"kind":"ensures","ok":false}]}
     ]
    },
    {
     "id":"Hd",
     "title":"(d) load-factor check off by one",
     "category":"code",
     "flavor":"probe loop never terminates",
     "edit":"line 125: `i32.const 7` -> `i32.const 8` (refuse only when used >= 8)",
     "edits":[["replace",125,"i32.const 7","i32.const 8"]],
     "calls":[
      ["insert",[0,0]],
      ["insert",[1,10]],
      ["insert",[2,20]],
      ["insert",[3,30]],
      ["insert",[4,40]],
      ["insert",[5,50]],
      ["insert",[6,60]],
      ["insert",[7,70]],
      ["lookup",[8,-1]]
     ],
     "expected_results":[1,1,1,1,1,1,1,0,-1],
     "observed_results":[1,1,1,1,1,1,1,1,"(lookup does not terminate)"],
     "runtime":"The 8th insert succeeds (correct program refuses it with 0). lookup(8, -1) then probes slots 0,1,...,7,0,1,... forever: no trap, no result; Codillon's 100k-step log fills up.",
     "static_failure":{
      "line":166,
      "obligation":"R4 (iv) after insert: used + 1 < CAP",
      "why":"the check at 124-126 now only gives used < 8, which R4 already guaranteed; used + 1 <= 8 is all that follows",
      "status":"fails"
     },
     "first_dynamic_failure":{"s":488,"ln":106,"kind":"ensures"},
     "R_violation":"R4 (iv): used < CAP. False from step 487 (line 166, global.set $used = 8) of the 8th insert; checked false at its return, step 488",
     "op_boundaries":[
      {"call":["insert",[0,0]],"returned_at_step":61,"R_false":[]},
      {"call":["insert",[1,10]],"returned_at_step":122,"R_false":[]},
      {"call":["insert",[2,20]],"returned_at_step":183,"R_false":[]},
      {"call":["insert",[3,30]],"returned_at_step":244,"R_false":[]},
      {"call":["insert",[4,40]],"returned_at_step":305,"R_false":[]},
      {"call":["insert",[5,50]],"returned_at_step":366,"R_false":[]},
      {"call":["insert",[6,60]],"returned_at_step":427,"R_false":[]},
      {"call":["insert",[7,70]],"returned_at_step":488,"R_false":["iv"]}
     ],
     "trace":[
      {"s":487,"fn":"insert","ln":166,"op":"global.set $used","stack":[],"loc":{"k":7,"x":70,"i":7,"p":65524,"j":0},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":488,"fn":"insert","ln":168,"op":"i32.const 1","stack":[1],"loc":{"k":7,"x":70,"i":7,"p":65524,"j":0},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]],"R":{"o":true,"i":true,"ii":true,"iii":true,"iv":false},"checks":[{"ln":104,"kind":"ensures","ok":true},{"ln":106,"kind":"ensures","ok":false}]},
      {"s":489,"fn":"lookup","ln":71,"op":"local.get $k","stack":[8],"loc":{"k":8,"dflt":-1,"i":0},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]],"checks":[{"ln":68,"kind":"requires","ok":false}]},
      {"s":490,"fn":"lookup","ln":72,"op":"call $find  (enter)","stack":[],"loc":{"k":8,"dflt":-1,"i":0},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]],"checks":[{"ln":21,"kind":"requires","ok":false}]},
      {"s":505,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":0,"p":65440,"j":0},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":535,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":1,"p":65452,"j":1},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":565,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":2,"p":65464,"j":2},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":595,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":3,"p":65476,"j":3},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":625,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":4,"p":65488,"j":4},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":655,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":5,"p":65500,"j":5},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":685,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":6,"p":65512,"j":6},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":715,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":7,"p":65524,"j":7},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":745,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":0,"p":65440,"j":8},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":765,"fn":"find","ln":63,"op":"br $probe","stack":[],"loc":{"k":8,"i":1,"p":65440,"j":9},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]],"checks":[{"ln":30,"kind":"invariant","ok":false},{"ln":31,"kind":"invariant","ok":true},{"ln":32,"kind":"decreases","ok":false}]},
      {"s":775,"fn":"find","ln":36,"op":"i32.load","stack":[1],"loc":{"k":8,"i":1,"p":65452,"j":9},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]]},
      {"s":795,"fn":"find","ln":63,"op":"br $probe","stack":[],"loc":{"k":8,"i":2,"p":65452,"j":10},"used":8,"M":[[0,0],[1,10],[2,20],[3,30],[4,40],[5,50],[6,60],[7,70]],"slots":[[1,0,0],[1,1,10],[1,2,20],[1,3,30],[1,4,40],[1,5,50],[1,6,60],[1,7,70]],"checks":[{"ln":30,"kind":"invariant","ok":false},{"ln":31,"kind":"invariant","ok":true},{"ln":32,"kind":"decreases","ok":false}]}
     ]
    }
   ],
   "correct_runs":{
    "calls":[["insert",[3,30]],["insert",[11,110]],["delete",[3]],["lookup",[11,-1]],["lookup",[3,-1]]],
    "results":[1,1,1,110,-1],
    "total_steps":383,
    "spec_checks_failed":0
   }
  }
 ]
}
```
