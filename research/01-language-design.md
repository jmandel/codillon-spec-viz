# Refined Codillon: a language design

*The semantic foundation for a Codillon where types are predicates. The visualization is designed separately (see §8 for the data it can rely on).*

## 0. Design principles

1. **It is still Wasm, one instruction per line.** Annotations are extra *lines*, never extra
   syntax inside instruction lines. When you erase them, what's left is the module the student would
   have written anyway, byte for byte.
2. **Every operand slot carries a predicate.** Codillon already gives each stack operand a *slot*
   (`SlotUse` in `utils.rs`) and draws a wire from producer to consumer. In the refined language a
   slot has a *provided* refinement (what its producer guarantees) and a *required* refinement (what
   its consumer needs). An obligation is a wire whose provided side has to imply its required side.
3. **Every predicate is decidable by evaluation.** Quantifiers are bounded, and maps are finite. So
   any obligation that hasn't been proven can still be *checked at runtime*, and the program always
   runs. This is gradual verification, with Codillon's 💣 as the failure mode.
4. **Overflow is a fact, not an error.** Instructions have their real wrap-around semantics. A wrap
   only matters when it breaks something the student claimed, and then the counterexample says which
   instruction wrapped.
5. **Lean is the meaning.** Each construct maps to a Lean 4 notion (subtype, Prop, `termination_by`,
   `have`, `sorry`). The in-browser engine is a fast, untrusted way to discharge goals that can be
   stated as Lean theorems.

## 1. Syntax

There are seven construct families. Concretely, all of them are stored as WebAssembly custom
annotations `(@…)`, which standard tools skip. That makes erasure literal: `wat2wasm` produces the
same binary from the annotated file as from the plain one. The editor shows the friendlier sugar
used below. For example, `(param $n (i32 | 0 <= $n))` is stored as `(param $n i32) (@where 0 <= $n)`.

### 1.1 Refined value types `(T | P)`

A refinement can go anywhere a value type can appear. The binder is the declared name.

```wat
(param  $n  (i32 | 0 <= $n))                   ;; caller must prove it; body may assume it
(result $r  (i32 | even($r)))                   ;; results may be named (ghost name, for specs)
(local  $i  (i32 | 0 <= $i <= 16))              ;; flow-insensitive: every local.set must re-establish
(global $count (mut (i32 | 0 <= $count < 16)) (i32.const 0))
block $B (result (i32 | $_ > 0))                ;; label type ($_ = the anonymous value): br $B must carry a positive i32
```

A refinement on a **param** is a precondition. On a **result** it is a postcondition. On a **local
or global** it is a *lifelong promise*: it is checked at every `set`/`tee` and at initialization
(Wasm locals start at 0, so `(local $i (i32 | 1 <= $i))` gets an obligation at function entry), and
it is assumed at every `get`. On a **label** it constrains the values carried by `br`. Unrefined
locals are tracked *flow-sensitively* (the checker knows their exact current value), so students
only refine a local when they want a promise that lasts through loops.

### 1.2 Function contracts

```wat
(func $insert (export "insert")
  (param $k (i32 | $k != 0)) (param $v i32)
  (result $ok (i32 | $ok == 0 || $ok == 1))
  (@requires P)          ;; relational preconditions over several params / state
  (@ensures  Q)          ;; may mention old(e) = value of e at entry
  (@modifies $T $M)      ;; regions/globals the function may change; everything else is framed
  (@decreases e)         ;; only for recursive functions
  …)
```

At **module level**, `(@invariant P)` is a representation invariant. It must hold after
instantiation, and it is an implicit `requires`+`ensures` of every *exported* function. Internal
helpers may break it temporarily. This is the Eiffel, Spec# and Dafny `Valid()` idea, and it is the
"rep invariant" that intro data-structure courses already teach.

### 1.3 Frame annotations

These lines go directly after a `loop`, `block` or `if` line, in the frame's body:

```wat
loop $L
  (@invariant 0 <= $i <= $n && $acc == $i * ($i - 1) / 2)
  (@decreases $n - $i)
```

- `@invariant` on a loop has to hold every time control reaches the loop head, both on entry and on
  every `br $L`.
- `@decreases e` on a loop: at every `br $L`, the new value of `e` must satisfy `0 <= e_new < e_old`.
- `@ensures Q` on a `block` or `if` is an optional *summary*. Each exit must establish `Q`, and after
  `end` the checker remembers `Q` instead of the full path-by-path history. It is a readability tool
  and is never required.

### 1.4 Proof steps

Each proof step is its own line. Only four exist:

| line | meaning | Lean analogue |
|---|---|---|
| `(@assert P)` | prove `P` here; afterwards it is a known fact | `have h : P := by auto` |
| `(@use lemma a b …)` | instantiate a lemma; its `ensures` becomes a fact | `have := lemma a b (by auto)` |
| `(@witness x := e)` | supply the witness for the next `exists x` goal | `⟨e, by auto⟩` |
| `(@assume P)` | take `P` without proof; **checked at runtime**; drawn as a warning | `sorry`, guarded by `decide` |

### 1.5 Definitions, pure functions, lemmas, ghosts

```wat
(@def even (x) x % 2 == 0)                         ;; Prop-valued definition (decidable)
(@def slot (h t) (h + t) % 16)                     ;; spec-level function on ℤ

(func $hash (@pure) (param $k i32) (result $h (i32 | 0 <= $h < 16)) …)   ;; usable inside predicates

(@lemma sq_lt_sq (x b) (requires 0 <= x && 0 <= b && x*x < b*b) (ensures x < b))  ;; from stdlib

(@ghost (global $M (map i32 i32) (map.empty)))     ;; specification-only state
(@set $M := $M[$k -> $v])                          ;; ghost update (a line in the body)
```

A `@pure` Wasm function must be loop-free, non-recursive, and must not touch memory or mutable
globals. Its body *is* its definition: the checker unfolds it inside predicates, the way Liquid
Haskell reflects functions. Lemmas come from a small standard library proven once in Lean, or the
student writes them with a body of `@assert`/`@use` lines (recursive `@use` with `@decreases` is
induction). Ghost state is erased from the product but **really executed** in checked runs, as a
host-side map behind `codillon_debug`-style imports.

### 1.6 Memory regions

Raw linear memory is a byte array, and that is hard for students and for solvers alike. A region
declaration gives a slice of memory a typed layout:

```wat
(memory 1)
(@region $T (at 1024) (array 16 (struct (key i32) (val i32))))   ;; bytes [1024, 1152)
```

In predicates, `$T[i].key` and `$T[i].val` are i32 arrays. Every load or store that touches the
region must land exactly on one field with the matching width, and this is an obligation. Regions
must be disjoint (checked at declaration). Stores outside all regions must not overlap any region.
Under these rules the checker can model each field as its own array of i32, a typed-heap model in
the style of Burstall–Bornat and VCC. Framing is then free: a store to `$T[i].val` changes nothing
else. Fields may be refined, as in `(struct (key (i32 | $_ != -1)) …)`, and those refinements are
checked at each store.

### 1.7 The predicate language

Predicates use infix notation, because students already read math that way:

```
P ::= e == e | e != e | e < e | e <= e | e <= e < e      (chains)
    | P && P | P || P | !P | P ==> P | true | false
    | forall x in e..e: P | exists x in e..e: P          (bounded, half-open)
    | forall k in $M: P | k in $M                         (finite maps)
    | name(e, …)                                          (@def predicates)
e ::= $x | n | e + e | e - e | e * e | e / e | e % e      (mathematical ℤ; / and % Euclidean, as Lean)
    | u($x)                                               (unsigned reading of an i32)
    | i32.add(e, e) | i32.shl(e, e) | …                   (any i32 op, with exact Wasm semantics)
    | $f(e, …)                                            (@pure functions)
    | $T[e].field | $M[e] | $M[e -> e] | old(e)
    | if P then e else e
```

**An i32 name in a predicate denotes its signed integer value**, which is how students read
numbers. `u($x)` gives the unsigned reading. `+` and `*` in predicates are mathematical and never
overflow, while `i32.add(a, b)` means the machine operation. Partial operations in specs, such as
`$M[k]` (which needs `k in $M`), `$T[i]` (which needs `0 <= i < 16`) and `/ 0`, produce
*well-formedness* obligations for the spec itself. Conjunction is ordered, so in
`k in $M && $M[k] == v` the right conjunct may rely on the left. This is Lean's `m[k]'h`
discipline.

## 2. Semantics

### 2.1 The refined stack type is a symbolic state

At each line ℓ the checker holds a symbolic state

```
Σℓ = ⟨ Φ ; S ; L ; G ; H ⟩
     Φ  path condition (facts known here)
     S  operand stack: a list of symbolic terms, one per slot
     L  locals → terms      G  globals (real and ghost) → terms      H  region arrays + raw bytes
```

The *refined stack type* at ℓ is `{ x₁ … xₖ : i32 | Φ ∧ xᵢ = S[i] }`. The fraction drawn for an
instruction is a function between two such types. Its inputs are the slots it pops, each annotated
with what this instruction **requires**. Its outputs are the slots it pushes, each annotated with
what it **provides**, which is the strongest fact the checker derived. Codillon's existing slot
indices become symbolic variable names, and its connection graph becomes the def–use graph of the
verification conditions.

This is forward symbolic execution (strongest postcondition) over Wasm's structured control flow.
Forward is chosen over backward weakest-precondition (Dafny/Boogie style) because it yields a state
*per line*, which is exactly what a per-line display needs. For per-instruction Hoare logic on a
stack machine, the prior art is Bannwart & Müller's bytecode logic. The use of indexed stack types
for Wasm follows Wasm-prechk (Geller, Frank & Bowman, POPL 2024), which uses them to remove dynamic
checks.

### 2.2 Instructions

Notation: `wrap(z)` is the unique `y ∈ [-2³¹, 2³¹)` with `y ≡ z (mod 2³²)`. A fresh output slot is `v`.

| instruction | pops | provides `v` with | obligation (required) |
|---|---|---|---|
| `i32.const c` | – | `v == c` | – |
| `local.get $x` | – | `v == L[$x]` (plus `$x`'s refinement) | – |
| `local.set $x` / `tee` | `a` | `L[$x] := a` | refinement of `$x` holds of `a` |
| `global.get/set` | | as for locals, over `G` | refinement of the global |
| `i32.add/sub/mul` | `a b` | `v == wrap(a ± b)`, `wrap(a*b)` | – |
| `i32.div_s` | `a b` | `v == a quot b` (truncating) | `b != 0 && !(a == -2³¹ && b == -1)` |
| `i32.div_u/rem_u` | `a b` | `u(v) == u(a) / u(b)` etc. | `b != 0` |
| `i32.rem_s` | `a b` | Wasm's truncated remainder | `b != 0` |
| `i32.and/or/xor/shl/shr_s/shr_u/rotl` | `a b` | the bit-vector op | – |
| `i32.eqz`, `eq`, `lt_s`, `le_u`, … | | `v == (if a < b then 1 else 0)`; the `_u` forms compare `u(a) < u(b)` | – |
| `select` | `a b c` | `v == (if c != 0 then a else b)` | – |
| `i32.load off` | `a` | `v == $T[i].f` if the address hits region field `f`; otherwise `v == mem32(u(a)+off)` | `u(a)+off+4 <= memsize`; region conformance |
| `i32.store off` | `a x` | `H := H[$T[i].f ↦ x]` | bounds; conformance; field refinement; region ∈ `@modifies` |
| `call $f` | args | ensures of `$f`, with `old` = pre-call; havoc `$f`'s `@modifies` | requires of `$f` and param refinements |
| `unreachable` | | — (state becomes ⊥) | `false`: prove this line is dead |
| `drop`, `nop` | | | – |

i64 follows the same rules with 64-bit wrap. f32/f64 slots may carry comparison-only refinements
(`0.0 <= $x <= 1.0`, `!isnan($x)`). Float arithmetic is opaque to the prover: the result slot gets
only facts the student asserts. Float refinements are therefore mostly *runtime-checked*. That is
the honest choice for the course's audio and signal material.

### 2.3 Control

- **`if`** pops `c`. The then-arm starts with `Φ ∧ c ≠ 0` and the else-arm with `Φ ∧ c = 0`. At
  `end` the arm states are **joined exactly**, as a disjunction of path conditions with
  `ite`-merged terms. Forward blocks therefore never *need* annotations.
- **`block $B`**: every `br $B`, every taken `br_if $B`, and the fallthrough `end` contribute a path
  to the exit. If the label type or `@ensures` is refined, each contributing path gets an
  obligation.
- **`loop $L`** with invariant `I` and measure `m`:
  1. On entry, the obligation is `I`.
  2. The head state *havocs the loop frame* (the locals, globals and regions written on some path
     from the head back to a `br $L`) and assumes `I`, all declared refinements, and `m₀ == m`.
     Anything the loop does not change survives without being mentioned. So the slogan for students
     is **"an invariant only has to talk about what the loop changes."**
  3. At each `br $L` (or taken `br_if $L`), the obligation is `I ∧ 0 <= m < m₀`.
  4. With no `@invariant`, the invariant is `true`. Facts about changed state are then lost at the
     head, and the residue tells the student so (§5).
- **`br_if`** splits the path in two: taken (`c ≠ 0`, plus the target's obligations) and fallthrough
  (`c = 0`). **`br`**, **`return`** and **`unreachable`** leave the state at ⊥, where every
  obligation holds trivially. This is the refinement-level meaning of Codillon's polymorphic "star"
  slot.
- **Function**: the entry state is the requires, the param refinements, locals equal to 0 (each
  refined local is checked against 0), and the module invariant if the function is exported. At
  `end`/`return` the obligations are the result refinements, `@ensures`, and the module invariant if
  exported.

### 2.4 Overflow, honestly

Students write their claims over ℤ. The machine computes in ℤ/2³². The checker connects the two
with one fact, `-2³¹ <= z < 2³¹ ⟹ wrap(z) = z`, together with congruence facts that survive
wrapping (`wrap(z) ≡ z mod 2ᵏ` for k ≤ 32). This has three consequences:

- `i32.shl $x 1` provably returns an **even** number for every `$x`, wraps included, because evenness
  is a congruence mod 2.
- `(result $r (i32 | $r == 2 * $x))` **fails**, with the counterexample `$x = 1073741824`.
- A hash function that multiplies by `0x9E3779B1` and wraps on purpose raises **no** obligation.
  Nothing claims the product is mathematically exact.

Overflow is never an obligation in itself. Each refuted obligation's counterexample is replayed
concretely, and every arithmetic instruction where `wrap(z) ≠ z` in that run is reported as **wrap
blame** ("wrapped at line 25: 2147395600 + 92680 → −2147479016"). For teaching there is an opt-in
`(@nowrap)` function attribute (Verus/SPARK style). Under it, every `add/sub/mul` carries the
obligation that it does not wrap.

### 2.5 Where obligations live

Every obligation has a **site**, and the site determines how it is drawn:

| kind | site | examples |
|---|---|---|
| *wire* | an input slot of an instruction | divisor ≠ 0; address in bounds; call argument; `local.set` refinement |
| *frame* | a `br`/`br_if`/`end`/`return` line plus its target frame | loop invariant on entry and back-edge; `decreases`; ensures; label type |
| *line* | an annotation line | `@assert`, `@use` preconditions, `@witness`, spec well-formedness |

### 2.6 What is decided automatically

The **automatic fragment** is what the editor guarantees to decide within its time budget (target
≈200 ms per obligation, in a Web Worker, cached by a hash of the sliced verification condition). It
is a quantifier-free combination of the following theories:

- linear integer arithmetic, with `/` and `%` by constants (Presburger, so congruences such as
  `wrap(h+t) & 15 == (h+t) % 16`): Lean's `omega`
- fixed-width bit-vectors (and, or, shifts, comparisons; bit-blasting): `bv_decide`
- polynomial **normalization**: `(r+1)*(r+1)` and `r*r + 2*r + 1` are the same term, and a nonlinear
  monomial is treated as an opaque atom (`ring_nf`, then `linarith`)
- arrays (regions), finite maps (ghost models), uninterpreted functions
- bounded quantifiers: **expanded** when the bound is a constant ≤ 64 (`decide`, `fin_cases`), and
  otherwise instantiated from terms in the goal.

Three things fall **outside** the fragment: nonlinear *inequalities* (`x*x < b*b ⟹ x < b`), the
choice of an existential witness when the bound is symbolic, and anything that needs induction.
These need a student-supplied `@assert`, `@witness` or `@use`. The engine (Z3 or cvc5 compiled to
Wasm) may still prove some of these opportunistically, and it says so ("proved with nonlinear
search"). A result of *unknown* is never shown as success.

### 2.7 Termination

Loops without `@decreases` are accepted under **partial correctness** and get an ∞? mark: "if this
returns, the spec holds". This is exactly Lean's `partial def` versus well-founded recursion, so
termination can be a later lesson. Recursive functions use `(@decreases e)` in the header, and each
recursive `call` gets the obligation `0 <= e' < e`. Codillon's step budget remains the runtime
backstop.

### 2.8 What "typechecks" means, and the residue

**Definition.** A module *typechecks* when every obligation is proven. **Intended theorem**, to be
mechanized against a Wasm semantics such as WasmCert or Iris-Wasm: for every call to an exported
function whose arguments satisfy its requires, in a state satisfying the module invariant, and
assuming every host import honors its contract, execution does not trap, every `@assert` holds, and
if the call returns, its ensures and the module invariant hold. If every loop and recursive function
has `@decreases`, the call returns.

The checker never stops at a single error. Its output is the **residue**: a list of obligations,
each with:

```
{ site: line 29 (br $grow) → frame loop $grow,
  kind: invariant-preservation, conjunct: 2,
  goal: u($sq) == ($r+1)*($r+1),                  -- in the student's names, after substitution
  status: proven | refuted | unknown(reason) | pending,
  used: [lines 10, 15, 20]                        -- unsat core, for proven goals
  counterexample: { $n: 2147395600, $r: 46339, $sq: 2147395600 },
  cex_kind: input | loop-head-state,              -- reachable vs. "invariant too weak"
  wrap_blame: [line 25],
  runtime: held 38 times this run | failed at step 1712 }
```

The distinction between *input* and *loop-head-state* counterexamples matters for teaching. A
failure of invariant *preservation* produces a state at the loop head that satisfies the invariant
but breaks it after one iteration. That state may not be reachable. Reachable or not, it shows that
the invariant is **too weak** or the code is wrong. The editor first tries a shallow bounded
unrolling from entry to find a *reachable* input. Otherwise it offers a **one-iteration replay**:
load the state into the locals and run the body up to the back edge.

## 3. Grounding in Lean-style type theory

| surface | Lean 4 reading |
|---|---|
| `i32` | `BitVec 32`; a predicate's `$x` is `x.toInt`, and `u($x)` is `x.toNat` |
| `(i32 \| P)` | the subtype `{x : BitVec 32 // P x}` with `[DecidablePred P]` |
| `@def p (x) …` | `def p (x : Int) : Prop := …` together with a `Decidable` instance |
| `@pure` func | a `def`: its body is its definitional unfolding |
| stack type at a line | a Σ-telescope `Σ (x₁ … xₖ : BitVec 32), Φ x₁ … xₖ` |
| instruction's fraction | a function between Σ-types; its proof part is the obligation |
| function contract | `(a : Args) → (σ : World) → Req a σ → {(r, σ') // Ens a σ r σ'}`, i.e. a Hoare triple over a Wasm state monad (compare Lean's `Std.Do`/`mvcgen`) |
| `loop` + `@invariant I` + `@decreases m` | a local tail-recursive `go` whose precondition is `I`, with `termination_by m`; without `@decreases` it is `partial def` |
| `@assert`, `@use`, `@witness` | `have`, applying a lemma, an anonymous-constructor witness |
| `@assume` | `sorry`, except that it is guarded at runtime |
| `unreachable` | `absurd`: control reaching it requires a proof of `False` |
| ghost state | computationally irrelevant fields of `World` (erased from the product) |
| the automatic fragment | `omega`, `bv_decide`, `decide`, `ring_nf`, `simp` with map lemmas |

**Edit time vs. run time.** At edit time a proof is a solver certificate, a chain of hint lines, or
a lemma application. Like Lean's `Prop`, proofs are erased from the program that runs, so a fully
proven program executes with no checks beyond Wasm's own.

**A runtime check is a proof found by evaluation.** Every refinement is decidable, so an unproven
obligation `P` compiles to `if decide P then continue else trap`. In Lean, `decide P = true` yields
a genuine proof of `P` (`of_decide_eq_true`), valid for *this execution*. When the check fails, the
step gets Codillon's 💣 with commentary such as "invariant broken: u($sq) == ($r+1)*($r+1) —
2147479015 vs 2147488281". This is hybrid type checking (Flanagan) and gradual verification (Bader,
Aldrich & Tanter), in a form students can see: **every ✓ removes a runtime check, and every unproven
line costs one.** The instrumentation already exists: Codillon rebuilds an instrumented binary with
`codillon_debug` imports on every keystroke, and contract checks and ghost updates are additional
imports of the same kind. Exported-function preconditions and host-import postconditions are always
checked dynamically, because the host is outside the proof.

**Lean as an escape hatch.** Any obligation can be printed as a Lean theorem. The standard-library
lemmas are proven in Lean with Mathlib, so the in-browser solver is a convenience and not the
trusted base. An instructor can re-check the residue of a whole problem set in Lean.

## 4. Teaching ladder

**Level 0: plain Wasm.** Nothing changes, except that the checker quietly proves trap-freedom
(`div` by zero, memory bounds, `unreachable`). Lines that might trap get a faint "?" before they ever
run.

**Level 1: the smallest meaningful spec.** It is one refinement, and it immediately exposes
overflow:

```wat
(func $abs (param $x i32) (result $r (i32 | 0 <= $r))
  local.get $x
  i32.const 0
  i32.lt_s
  if (result i32)
    i32.const 0
    local.get $x
    i32.sub                ;; ← wrap blame
  else
    local.get $x
  end)                     ;; ✗ 0 <= $r   counterexample $x = -2147483648, $r = -2147483648
```

The fix is `(param $x (i32 | $x != -2147483648))`. That moves the obligation to every *caller*,
which shows the student that specifications are contracts.

**Level 2: properties as types.** `(@def even (x) x % 2 == 0)` with
`(result $r (i32 | even($r)))` on a body `local.get $x / i32.const 1 / i32.shl` is proven even though the operation wraps.
Changing the result to `$r == 2*$x` fails. The pair teaches the difference between congruences and
magnitudes.

**Level 3: ranges and memory.** `(param $i (i32 | 0 <= $i < 16))` turns a bounds obligation at
`i32.load` from ✗ to ✓. Students learn that a precondition is what makes an access safe.

**Level 4: loop invariants and measures.** Sum-to-n first, then isqrt (§5). The characteristic
error is "invariant not preserved", shown with a loop-head counterexample.

**Level 5: data structures.** Regions, a ghost model, a representation invariant, and `@assert`
stepping stones, ending with the hash table (§6).

Errors always appear in the same form: one obligation, at one line, in the student's own names,
with concrete numbers.

## 5. Worked example A: integer square root

The spec is `0 <= r ∧ r² <= n < (r+1)²` for every `0 <= n <= 2³¹−1`. The trap is that `(r+1)²` can
reach 46341² = 2,147,488,281, which is more than `2³¹−1`.

```wat
 1 (func $isqrt (export "isqrt")
 2   (param $n (i32 | 0 <= $n))
 3   (result $root (i32 | 0 <= $root && $root*$root <= $n < ($root+1)*($root+1)))
 4   (local $r (i32 | 0 <= $r <= 46340))
 5   (local $sq i32)                     ;; invariant: u($sq) == ($r+1)^2
 6   i32.const 1
 7   local.set $sq
 8   block $done
 9     loop $grow
10       (@invariant $r*$r <= $n && u($sq) == ($r+1)*($r+1))
11       (@decreases $n - $r*$r)
12       local.get $sq
13       local.get $n
14       i32.gt_u
15       br_if $done                     ;; exit when (r+1)^2 > n
16       (@use sq_lt_sq ($r+1) 46341)
17       local.get $r
18       i32.const 1
19       i32.add
20       local.set $r                    ;; r := r+1
21       local.get $sq
22       local.get $r
23       i32.const 2
24       i32.mul
25       i32.add
26       i32.const 1
27       i32.add
28       local.set $sq                   ;; sq := sq + 2r + 1  = (r+1)^2 for the new r
29       br $grow
30     end
31   end
32   local.get $r
33 )
```

**Obligations (final version: all ✓).** Below, `r` is the value at the loop head and `r' = r+1`.

| line | obligation | how |
|---|---|---|
| entry | `$r = 0` satisfies `0 <= $r <= 46340` | auto |
| 9 (entry) | `0*0 <= n ∧ u(1) == 1*1` | auto (needs `0 <= n` from line 2) |
| 14 | provides `c == (u(sq) > u(n))`. Since `n >= 0`, `u(n) == n` | auto (bit-vector) |
| 16 | lemma precondition `(r+1)*(r+1) < 46341*46341` from `u(sq) <= n <= 2³¹−1` | auto: linear, with `(r+1)²` as an atom |
| 19 | provides `wrap(r+1)`, which equals `r+1` because `r+1 <= 46340` | auto |
| 20 | `0 <= r' <= 46340` | auto, from line 16's fact |
| 24, 25, 27 | the provided values never wrap *as unsigned*: `r'² + 2r' + 1 <= 2³¹−1 + 92681 < 2³²` | auto: normalization plus linear |
| 29 | invariant: `r'² <= n` (it was `u(sq)`) ∧ `u(sq_new) == (r'+1)²` | auto: normalization |
| 29 | decreases: `0 <= n − r'² < n − r²`, using `2r+1 > 0` | auto |
| 32–33 | ensures: `r² <= n` (invariant), `n < (r+1)²` (exit fact `u(sq) > n`), `0 <= r` (refinement) | auto |

**The student's path to this version, and the residue at each step:**

1. *No invariant (lines 10–11 missing).* At line 33, `$root*$root <= $n` is refuted with a
   **loop-head state** counterexample `{n: 3, r: 5, sq: 100}`. The message reads: "the loop forgets
   everything about $r and $sq. Say what stays true at the top of the loop." Line 9 also shows ∞?.
2. *A signed first attempt* (`i32.gt_s` and invariant `$sq == ($r+1)*($r+1)`). Line 29, invariant
   conjunct 2, is refuted. The loop-head counterexample is `{n: 2147395600, r: 46339, sq: 2147395600}`.
   After one iteration, `sq = −2147479015` but `(r+1)² = 2147488281`. Wrap blame falls on line 25
   (`2147395600 + 92680`). This is the honest-overflow lesson: the value is correct as an unsigned
   number, so the fix is `u(...)` together with `gt_u`.
3. *Without line 16.* Line 20 shows `unknown (nonlinear)`: `(r+1)*(r+1) < 2147488281 ⟹ r+1 <= 46340`.
   Lemma autocomplete (Codillon already has an autocomplete engine) suggests `sq_lt_sq`, because its
   conclusion has the shape of the goal. This is Lean's `apply?`.

## 6. Worked example B: an open-addressing hash table

There are 16 slots of `(key, val)` at address 1024. Key 0 means empty, so keys must be nonzero.
Collisions use linear probing, and there is no deletion (tombstones are a later exercise). The
abstract model is a ghost map `$M`.

```wat
(memory 1)
(@region $T (at 1024) (array 16 (struct (key i32) (val i32))))
(@ghost (global $M (map i32 i32) (map.empty)))
(@def slot (h t) (h + t) % 16)

(func $hash (@pure) (param $k i32) (result $h (i32 | 0 <= $h < 16))
  local.get $k
  i32.const 0x9E3779B1
  i32.mul                  ;; wraps on purpose: no obligation
  i32.const 28
  i32.shr_u)               ;; ✓ 0 <= h < 16 (bit-vector)

(func $slot_addr (@pure) (param $h i32) (param $t i32)
  (result $a (i32 | $a == 1024 + 8 * slot($h, $t)))
  local.get $h
  local.get $t
  i32.add
  i32.const 15
  i32.and                  ;; wrap(h+t) & 15 == (h+t) % 16: a congruence, so ✓
  i32.const 3
  i32.shl
  i32.const 1024
  i32.add)

(@def Rep ()
  (forall i in 0..16:
     $T[i].key != 0 ==>
          $T[i].key in $M && $M[$T[i].key] == $T[i].val                       ;; R1 sound
       && (forall s in 0..((i - $hash($T[i].key)) % 16):                       ;; R2 no gaps
             $T[slot($hash($T[i].key), s)].key != 0))
  && (forall k in $M: k != 0 && exists i in 0..16: $T[i].key == k)              ;; R3 complete
  && (forall i in 0..16: forall j in 0..16:
        $T[i].key != 0 && $T[i].key == $T[j].key ==> i == j))                   ;; R4 unique
(@invariant Rep())          ;; module invariant: holds initially (zeroed memory, empty map)
```

R2 is the property that makes open addressing work. Between a key's home slot and the slot where it
actually sits, there is never an empty slot. That guarantees a probe for the key cannot stop early.

### 6.1 `lookup`

```wat
(func $lookup (export "lookup")
  (param $k (i32 | $k != 0))
  (result $v (i32 | $v == (if $k in $M then $M[$k] else 0)))
  (local $h i32) (local $t (i32 | 0 <= $t <= 16)) (local $a i32) (local $key i32)
  local.get $k
  call $hash
  local.set $h
  block $absent
    loop $probe
      (@invariant forall s in 0..$t: $T[slot($h,s)].key != 0 && $T[slot($h,s)].key != $k)
      (@decreases 16 - $t)
      local.get $t
      i32.const 16
      i32.eq
      br_if $absent            ;; [L5] probed all 16 slots
      local.get $h
      local.get $t
      call $slot_addr
      local.tee $a
      i32.load                 ;; [L1] key
      local.tee $key
      i32.eqz
      br_if $absent            ;; [L4] empty slot: k is absent
      local.get $key
      local.get $k
      i32.eq
      if
        local.get $a
        i32.load offset=4      ;; [L2] val
        return                 ;; [L3]
      end
      local.get $t
      i32.const 1
      i32.add
      local.set $t             ;; [L6]
      br $probe                ;; [L7]
    end
  end
  i32.const 0
)
```

`$h == $hash($k)` is known, because `$hash` is pure and its result is unfolded. Memory and `$M` are
not written anywhere in the loop, so they are not havocked and `Rep()` survives the loop without
being restated.

| tag | obligation | how |
|---|---|---|
| L1 | `1024 + 8*slot(h,t) + 4 <= 65536`; the address is `&$T[slot(h,t)].key` | auto (linear plus congruence) |
| L2 | `addr + 4` is `&$T[slot(h,t)].val` | auto |
| L3 | ensures `T[i].val == (if k in M then M[k] else 0)`, where `i = slot(h,t)` and `T[i].key == k` | auto: R1 at `i` |
| L4 | ensures `0 == …`, i.e. `!(k in M)`, given an empty slot at `slot(h,t)` | auto by **finite expansion**. Suppose k sits at `j` (R3) and let `d = (j−h)%16`. If `d < t` the invariant is contradicted; if `d = t` the slot is empty; if `d > t`, R2 at `j` is contradicted. This is the hardest goal in the course. |
| L5 | `!(k in M)` when `t == 16` | auto by expansion: `{slot(h,s) | s < 16}` covers all 16 slots |
| L6 | `0 <= t+1 <= 16` (since `t != 16`) | auto |
| L7 | the invariant extended to `s = t`; `16 − (t+1) < 16 − t` | auto |
| exit | `Rep()` holds after the call | free: `lookup` has no `@modifies` |

L4 and L5 are automatic only because the capacity is the constant 16, so the quantifiers expand.
Make the capacity a parameter and both become student work. L5 then needs
`(@witness s := (j - $h) % 16)`, and L4 is best stated once as a lemma `gap_means_absent`. This is a
good "why constants help" discussion.

### 6.2 `insert`

```wat
(func $insert (export "insert")
  (param $k (i32 | $k != 0)) (param $v i32)
  (result $ok (i32 | ($ok == 1 && $M == old($M)[$k -> $v])
                  || ($ok == 0 && $M == old($M))))
  (@modifies $T $M)
  (local $h i32) (local $t (i32 | 0 <= $t <= 16)) (local $a i32) (local $key i32)
  local.get $k
  call $hash
  local.set $h
  block $full
    loop $probe
      (@invariant forall s in 0..$t: $T[slot($h,s)].key != 0 && $T[slot($h,s)].key != $k)
      (@decreases 16 - $t)
      local.get $t
      i32.const 16
      i32.eq
      br_if $full
      local.get $h
      local.get $t
      call $slot_addr
      local.tee $a
      i32.load
      local.tee $key
      i32.eqz
      if                               ;; empty slot: claim it
        (@assert !($k in $M))          ;; [I2] stepping stone (same argument as L4)
        local.get $a
        local.get $v
        i32.store offset=4             ;; [I1]
        local.get $a
        local.get $k
        i32.store                      ;; [I1]
        (@set $M := $M[$k -> $v])
        i32.const 1
        return                         ;; [I3]
      end
      local.get $key
      local.get $k
      i32.eq
      if                               ;; key present: overwrite the value
        local.get $a
        local.get $v
        i32.store offset=4             ;; [I1]
        (@set $M := $M[$k -> $v])
        i32.const 1
        return                         ;; [I4]
      end
      local.get $t
      i32.const 1
      i32.add
      local.set $t
      br $probe
    end
  end
  i32.const 0                          ;; [I5] table full
)
```

The stores sit only on paths that `return`, so no store reaches `br $probe`. The loop frame is
therefore `{$t, $a, $key}`, and memory is still not havocked. That is why the same one-line
invariant works here as in `lookup`.

| tag | obligation | how |
|---|---|---|
| I1 | each store lands on `$T[i].key`/`.val` and `$T ∈ @modifies`; `$M` is set only by ghost lines | auto |
| I2 | `!(k in M)` (the L4 argument, from the invariant, the empty slot, R2 and R3) | auto by expansion; without the line, the same reasoning is folded into I3 |
| I3 | `ok == 1 ∧ M' == old(M)[k -> v]` | auto (ghost update) |
| I3·R1 | slot `i`: `M'[k] == v == T'[i].val`; any other slot `j` has a key in `M`, so ≠ k (I2), so it is unchanged | auto |
| I3·R2 | slot `i`: `(i − h)%16 == t`, and the probed slots `< t` are nonempty (invariant); for other slots, filling slots only adds nonempty ones | auto (expansion) |
| I3·R3 | `dom M' = dom M ∪ {k}`, with k at `i` | auto |
| I3·R4 | `k` appears nowhere else (I2 + R1) | auto |
| I4 | `ok == 1`, `M' == M[k -> v]`; R1 at `i` (by R4 no other slot holds `k`); keys unchanged, so R2–R4 still hold | auto |
| I5 | `ok == 0 ∧ M == old(M)`; nothing was written, so `Rep` is unchanged | auto (frame) |
| loop | as L6/L7 | auto |

**What a student sees along the way.** If the student forgets the `t == 16` exit, the obligation
at `local.set $t` (`t+1 <= 16`) is refuted. The loop-head counterexample is `t = 16`, with all 16
slots full of other keys, which is a full table. If the student forgets `(@set $M := …)` in the
empty-slot branch, the ensures at I3 is refuted with the input `{k: 7, v: 1, M: {}}`, and R1 fails
there too: key 7 is in memory but not in `$M`. With checks on, that run shows a 💣 at the
module-invariant check on the `return`. If the student increments `$t` by 2 to "probe faster", the invariant is refuted at `br $probe`. It
claims that slot `slot(h, t+1)` was checked, and it never was. The counterexample is a loop-head
state in which that skipped slot holds `k`.

## 7. Related systems, and how each shaped a choice

- **Liquid Haskell / Liquid Types**: refinements on value types, and decidable logic so that checking
  is automatic. From here: `(T | P)`, reflection of `@pure` functions, and (as a future editor
  assist) qualifier-based *inference* of simple loop invariants, offered as a ghosted suggestion the
  student accepts.
- **Dafny**: loop invariants and `decreases`, `old`, `modifies`, ghost state, `assert` as a
  stepping stone, and lemmas as ghost procedures. These are the most familiar teaching vocabulary,
  so the surface syntax follows it.
- **F\*** and **Verus**: Verus (Lattuada et al.) makes overflow obligations explicit for machine
  integers. Here that is the opt-in `@nowrap`, and the default is demand-driven wrap facts. F\*'s
  split of the logic into effects informs the separation of erased ghost state from real state.
- **Lean 4**: the meaning of everything (§3), the decidability requirement, and the tactic analogues
  for the automatic fragment.
- **Wasm-prechk** (Geller, Frank & Bowman, POPL 2024): indexed types on the Wasm *stack* that remove
  dynamic checks. It is the closest precedent for refining stack slots directly rather than
  translating to a higher-level language first.
- **Iris-Wasm** (Rao et al., PLDI 2023) and **WasmCert**: the target semantics for a mechanized
  soundness proof. Regions are a deliberately weaker, first-order stand-in for separation logic.
  Students never see `∗`.

**Open questions.** (1) Exact path joining can blow up exponentially. Small programs are fine, and
`@ensures` on a block is the student-visible cut. (2) Should spec well-formedness errors (`$M[k]`
without `k in $M`) be ✗ (invalid) rather than an obligation? (3) Host-callback re-entrancy, and
exported memory written by JavaScript, both void the module invariant. The current proposal forbids
both when `@invariant` is used. (4) Float refinements stay runtime-only until there is an interval
domain.

## 8. What the visualization layer can rely on

For each **line**: an obligation list (the residue records of §2.8) and a status of
proven/refuted/unknown/pending/assumed.

For each **slot**: its symbolic term, its provided refinement (pretty-printed in source names; the
viz decides how much of Φ to show), its required refinement from the consumer, and the obligation id
on its wire.

For each **frame**: its invariant and measure, its havoc set (what the loop forgets), and its exits
with their obligations.

For each **refuted obligation**: a concrete counterexample, its kind (input or loop-head state), its
wrap blame, and a replay handle that feeds the existing time-travel slider.

For each **proven obligation**: an unsat core, given as the set of lines whose facts were used. These
are natural candidates for "proof wires" drawn in the same style as Codillon's dataflow curves.

At **run time**: a per-obligation count of checks that held, and the step at which a check failed (💣).
