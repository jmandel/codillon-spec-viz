# 16 — Refined Codillon v2: proofs as Wasm values, checked by a kernel

Status: phase A design (2026-10-24). Input: 15-input-proofs-as-values.md. Examples and test oracle: `v2-examples/`.
No Z3, no SMT. One deterministic kernel; an LLM is optional and never trusted.

## 0. Outline and decisions

| § | topic | one-line decision |
|---|---|---|
| 1 | Text syntax | Facts travel in a separate **fact lane** (scoped, persistent), never on the operand stack; propositions are folded Wasm expressions read as "≠ 0"; every v2 construct erases line-for-line (proof lines → `nop`, proof declarations → comment). |
| 2 | Rule cards | 35 numbered cards (R1–R35); each cup is fed by exactly one fact, found by exact canonical lookup or produced by the `prove k` line just above. |
| 3 | `prove k` | Linear integer arithmetic over unsigned readings with explicit wrap variables, monomials as atoms, interval pre-pass, Omega-lite elimination; caps: 64 terms, 24 variables, 32 atoms, 256 cases; failures name the hypotheses actually taken. |
| 4 | Verdicts | Four per-cup states: proven, refuted, runtime-checked, assumed, plus a *relative to checks at lines …* mark. Gradual mode is the editor default (programs always run); a function is **VERIFIED** only when strict-clean. The kernel never answers "unknown". |
| 5 | Data structures | Slots with canonical ids, a fact stack with frame marks, `fact_args`, scratch arena, memory epochs; one forward pass per function; re-check per function. |
| 6 | Theorem | All cups proven ⇒ no trap on any input meeting the entry contract, except call-stack exhaustion; partial correctness only; harnesses compute in i64. |
| 7 | Vericoding | Student owns headers, predicates, measures, harnesses, axioms; LLM owns bodies, proof lines, lemmas; adequacy = vacuity + 6 mutation operators; scripted sessions by default. |
| 8 | Visual mapping | Fact lane drawn as a column of fact chips right of the fraction; wires chip→cup; fraying at `local.set`; False cup on `unreachable`; four states grayscale-safe. |
| 9 | Limits | floats opaque, no `call_indirect`, no `memory.grow`, no termination for ordinary code, memory frame reasoning is runtime-checked. |

## 1. Text syntax

### 1.1 Where proofs travel: a fact lane, not the operand stack

Two designs were weighed.

*Proofs on the operand stack* (the sketch in 15 §1) makes a proof an ordinary operand: `local.get $nz` pushes it,
`i32.div_u` pops three things. It is maximally explicit, but it fails the other two tests:

- **Erasure.** A proof pushed by a line that also pushes a real value (an `if` arm receiving its branch proof, a call
  returning a value and a proof) cannot be erased line by line without changing the arm's stack type. Every proof
  producer would need its own line and every consumer a `local.set`/`local.get` dance (the 15 §1 sketch needs five
  extra lines for one division).
- **Stack order.** A proof sits under or over the operands it justifies; `prove 2` must find its two hypotheses at the
  right depth; a branch fact born at the top of an arm is buried under everything the arm computes. Intro students
  already find Wasm stack order the hardest part of Codillon.

*A fact lane* is a second, separate structure that holds **facts about values**. Facts enter it at fixed points (branch
arms, block exits, call results, function entry, `prove`, lemma lines). They are never popped by a consumer: a fact
stays in the lane until its scope (the enclosing block arm) ends, exactly like a path condition. Every proposition an
instruction needs is a **proof cup**, and every cup is fed by **exactly one fact**, chosen deterministically:

1. if the line above is a `prove k` (or a run of them), its output feeds the cup (§1.6);
2. otherwise the kernel looks the cup's proposition up in the lane by **exact canonical match** (same head, same
   canonical value ids, after the fixed atom normalization of card R4); the most recent match wins.

Lookup is an equality test over at most a few dozen records, not search. Explicitness is preserved where students need
it, on screen: every feed is drawn as a wire from the fact's birth line to the cup, always on (§8), and the cup's
proposition is printed in its fraction. Erasure is trivial: the lane does not exist at run time and no ordinary line
changes its stack effect. Stack-order bookkeeping disappears; ordering matters in exactly one place, the `k` most
recent lane entries that `prove k` takes as hypotheses, and those are drawn as `k` wires.

The price: the text alone does not say which fact feeds a cup. We accept it because the rule is deterministic and
local, because Codillon is a visual editor whose wires are the explicit form, and because the one ambiguous-looking
case (several equal facts) cannot change the verdict: equal facts are interchangeable.

Proof-typed locals remain, as **fact handles**: `local.set $h` names the lane's top entry, `local.get $h` re-enters
it at the top of the lane so a later `prove k` can take it as a hypothesis (§1.5).

### 1.2 Lines

A v2 file is a Codillon file: one module field part or one instruction per line, parsed line by line. The function
header is one line; locals, instructions and the closing `)` each have their own line. v2 adds no new line kinds:
every v2 construct is either an annotation *inside* an existing header/local/block line or a new **proof
instruction** that occupies a line of its own.

### 1.3 Grammar (EBNF; `ws` between tokens; `;;` comments as in WAT)

```
header      ::= "(func" id export* hparam* hresult*
export      ::= "(export" string ")"                          ;; special names in §1.7
hparam      ::= "(param" id vtype ")" | "(param" id prop ")"  ;; fact parameter: a precondition not about one value
hresult     ::= "(result" vtype ")"   | "(result" prop ")"    ;; at most one value result; fact results are postconditions
local       ::= "(local" id vtype ")" | "(local" id "fact" ")"
global      ::= "(global" id ( vtype | "(mut" vtype ")" ) "(" const-instr ")" ")"

vtype       ::= valtype | "(" valtype "|" refinement ")"
valtype     ::= "i32" | "i64" | "f32" | "f64"
refinement  ::= predref expr*                 ;; sugar for (call predref v expr*)
              | sexpr                         ;; a folded expression that mentions v
prop        ::= "(fact" sexpr ")"
predref     ::= id                            ;; a predicate function, §1.7

expr        ::= id | "v" | int | sexpr
sexpr       ::= "(" opname expr* ")" | "(call" predref expr* ")"
opname      ::= any pure integer Wasm opcode: iNN.{const,add,sub,mul,div_s,div_u,rem_s,rem_u,and,or,xor,
                shl,shr_s,shr_u,rotl,rotr,clz,ctz,popcnt,eqz,eq,ne,lt_s,lt_u,gt_s,gt_u,le_s,le_u,ge_s,ge_u,
                extend8_s,extend16_s}, i64.extend32_s, i32.wrap_i64, i64.extend_i32_s, i64.extend_i32_u
int         ::= WAT integer literal (decimal or 0x…, optional sign); typed by the operator it feeds

blockinstr  ::= ("block" | "loop" | "if") id? bfact* bparam* bresult*
bfact       ::= prop                          ;; invariant / exit fact of this block
bparam      ::= "(param" vtype ")"            ;; refinements allowed
bresult     ::= "(result" vtype ")"

proofinstr  ::= "prove" nat                   ;; nat = k, 0 ≤ k ≤ 8
              | "lemma" id expr*              ;; call a lemma or axiom function; args are its value params
              | "unfold" id expr*             ;; one-step unfolding of a recursive predicate
              | "assume" prop                 ;; student/instructor zone only (§7)
              | "local.get" id | "local.set" id | "local.tee" id     ;; when id is a fact local
```

**Meaning of names inside expressions.** `$x` denotes the *current value* of local or parameter `$x` at the line
where the expression is *instantiated*: the header (entry values); a block line's `(fact …)` clause is a template,
instantiated with the bindings current **at each edge that carries its cup** (for `block`/`if`: each `br` to the label and
the fall-through at `end`; for `loop`: the fall-in and each back-edge) and, when it enters the lane, with the bindings
after the join (`block`/`if`) or at the loop head (`loop`); a `lemma`/`unfold` line (current values). `v` denotes the value whose type is being refined. A refinement on parameter `$p` may mention
parameters declared before it. A result refinement may mention parameters; it means their **entry** values, even
if the body later `local.set`s a parameter. Integer literals take the type of the operator they feed.

**Propositions are folded Wasm.** `(fact E)` asserts "E evaluates **without trapping** to a nonzero i32" (decided 2026-10-24 after kernel review B5). So a fact used as a hypothesis also tells the kernel that every divisor inside it is nonzero (and no signed INT_MIN/−1 occurs), and a goal fact containing a division is provable only if its divisors are shown nonzero; a runtime check (R35) of a fact whose evaluation traps reports the fact as failed rather than trapping the program. There is no other logic
language: `¬E` is `(i32.eqz E)`, `E₁ ∧ E₂` is two `(fact …)` clauses (or `(i32.and E₁ E₂)` for 0/1 operands),
`False` is `(fact (i32.const 0))`, bounded quantifiers are predicate functions. Refinements are sugar:

| written | means |
|---|---|
| `(param $d (i64 \| $at_least_2))` | `$d : i64` and `(fact (call $at_least_2 $d))` on entry |
| `(result (i32 \| $is_gcd $a $b))` | result `v : i32` with `(fact (call $is_gcd v $a $b))` (relational) |
| `(param $i (i32 \| (i32.lt_u v 8)))` | `$i : i32` with `(fact (i32.lt_u $i 8))` |
| `(local $k (i32 \| (i32.lt_u v 8)))` | every `local.set $k` has a cup; every join/loop head re-enters the fact |

### 1.4 Branch facts

No syntax. A condition value `c` consumed by `if` or `br_if` produces the atom `⟦c⟧` ("c ≠ 0", normalized by R4: if
`c` was computed by a comparison or `eqz`, the atom is that comparison). `if` enters `⟦c⟧` at the top of the then-arm
and `¬⟦c⟧` at the top of the else-arm (even when the else is implicit). `br_if L` gives the taken edge `⟦c⟧` and
enters `¬⟦c⟧` on the fall-through. `br_table L₀ … Lₙ₋₁ D` gives the edge to `Lⱼ` the atom `(i32.eq i j)` and the
default edge `(i32.ge_u i n)`.

### 1.5 Fact locals

`(local $h fact)` declares a handle; a fact parameter `(param $h (fact P))` is a handle bound at entry to its fact. `local.set $h` binds `$h` to the lane's most recent entry (the lane is
unchanged; nothing is popped). `local.tee $h` is the same. `local.get $h` re-enters the bound fact at the top of the
lane, if that fact is still in scope; otherwise the line is an error, "`$h` holds a fact that ended at line N". A
handle never goes stale by assignment of ordinary locals, because facts are about values (R7); what goes stale is the
match between an old fact and a new value.

### 1.6 `prove k`, `lemma`, `unfold`, `assume`

- `prove k` takes the `k` most recent lane entries as hypotheses (drawn as `k` cups on its fraction), and produces
  one fact whose proposition is **the goal of the cup it feeds**: the first otherwise-unfed cup of the next ordinary
  instruction line. Proof lines between them are allowed. A run of `n` `prove` lines feeds the first `n` unfed cups
  in order. The produced fact also enters the lane, so later cups can find it by lookup (for a taken-edge cup of `br_if`/`br_table`,
only the edge's snapshot). A failure names the hypotheses it actually took. Decided by §3.
- `lemma $f e₁ … eₘ` calls a lemma function (pure, erased): the `eᵢ` are its value parameters, its fact parameters
  are cups on this line (fed like any cup), and its fact results enter the lane.
- `unfold $p e₁ … eₘ` enters the one-step unfolding of a recursive predicate (R30).
- `assume (fact E)` enters `E` with verdict *assumed*. It exists for teaching and for instructor scaffolding; the
  vericoding lock rejects it in LLM-owned code.

### 1.7 Special functions, by export name

| export name | role | checked how |
|---|---|---|
| (none needed) | **predicate**: any function named in a proposition | must be pure, total, loop-free, i32 result (R29) |
| `measure:<f>` | measure for the recursive predicate or lemma `<f>`; same params as `<f>`, `i32`/`i64` result read unsigned | pure, non-recursive (R31) |
| `axiom:<name>` | lemma without a proof (empty body); trusted, verdict *assumed* | student/instructor zone only |
| `harness:<name>` | functional-spec harness; params are the quantified inputs | ordinary function; its `unreachable` needs False (R26) |
| `lemma:<name>` | **lemma**: value params, fact params, only fact results | body is ghost: checked, never run, erased (R33) |

### 1.8 Erasure

Erasure is a per-line text transformation; it never adds or removes lines, so line numbers, step-slider positions and
Codillon diagnostics agree between the v2 text and the erased Wasm.

| line | erased to |
|---|---|
| header | refinements `(T \| …)` → `T`; `(param $h (fact …))` and `(result (fact …))` clauses deleted |
| `(local $x (T \| …))` | `(local $x T)` |
| `(local $h fact)` | `;;~ (local $h fact)` (comment) |
| block/loop/if line | `(fact …)` clauses deleted; refinements in block params/results → plain types |
| `prove`, `lemma`, `unfold`, `assume`, fact-local get/set/tee | `nop ;;~ <original text>` |
| every body line of a lemma or axiom (exported `lemma:`/`axiom:`) | `nop ;;~ <original text>` (header kept: value params remain, fact params/results deleted) |
| anything else | unchanged |

An erased lemma is a function with value parameters, no results and a body of `nop`s, which is valid Wasm.
`research/v2-examples/tools/erase.py` implements this table.

## 2. Rule cards

Conventions. `w` is the width (32 or 64). `u(x)` is the unsigned reading of a value, an integer in `[0, 2ʷ)`;
`s(x)` the signed reading in `[−2ʷ⁻¹, 2ʷ⁻¹)`. A **slot** is one input or output position of one line; each output slot
gets a **canonical id** (value number) `#n`. A **fact** is an atom about canonical ids with an origin line. "Enter F"
means push fact F onto the lane. A **cup** is a required atom on a line; the card says how it is drawn. Every error
appears as Codillon commentary at the far right of the line plus an empty (unfed) cup; there is no other channel.
Cards apply in **strict** and **gradual** mode alike except where §4 says an unfed cup becomes a runtime check.

Each card: **Premises** (what must be true of the inputs and lane) ⟹ **Conclusion** (new ids, facts, cups);
**Drawn**; **Error**.

### Values

**R1 — value numbering.** Premise: a pure line (any opcode of R2–R4, or a call to a pure function in the same memory
epoch) with input canonical ids `#a, #b, …`. Conclusion: the output id is `table[(opcode, immediates, #a, #b, …)]`,
allocating a fresh id on miss. Impure lines (loads after a store, impure calls, `local.get` of a parameter on entry)
allocate fresh ids. The table is cleared at the start of every function pass. Subterms of an instantiated proposition (a refinement,
block fact or lemma result such as `(i64.extend_i32_u v)`) are value-numbered through the same table as **virtual
slots** (no line), so code that later computes the same term gets the same id and lookup can match it. Commutative operands are *not* sorted
(the decision procedure handles commutation); `(i32.add #a #b)` and `(i32.add #b #a)` get different ids.
Drawn: nothing new; two slots with the same id show the same small id tag when hovered. Error: none.

**R2 — constants.** `iNN.const c` ⟹ output id `const(NN, c mod 2ʷ)`. All constants with the same type and bits share
one id. No cup, no fact. A constant is its own term, so facts like `(i32.lt_u #i 8)` mention the constant id of `8`.

**R3 — integer instruction classes.** Each pure integer opcode produces the term `op(#a, #b)` with exactly Wasm's
meaning; no fact is entered. The decision procedure (§3) and evaluator (R28) interpret terms as follows:

| class | opcodes | meaning on readings |
|---|---|---|
| ring | `add`, `sub`, `mul` | `u(r) = (u(a) ∘ u(b)) mod 2ʷ` — wraps silently, never traps |
| unsigned division | `div_u`, `rem_u` | `u(r) = ⌊u(a)/u(b)⌋`, `u(a) − u(b)·⌊u(a)/u(b)⌋`; cup R24 |
| signed division | `div_s`, `rem_s` | truncation toward zero on `s(·)`; `div_s` result taken mod 2ʷ; cups R24, R25 (`rem_s` has no R25 cup: `INT_MIN rem_s −1 = 0`) |
| bitwise | `and`, `or`, `xor` | bitwise on `u(·)`; `and` with a constant `2ᵏ−1` is `mod 2ᵏ` (linear, §3.2) |
| shifts | `shl`, `shr_u`, `shr_s`, `rotl`, `rotr` | shift count is `u(b) mod w`; `shl` by constant `k` is `·2ᵏ mod 2ʷ`, `shr_u` by constant `k` is `⌊·/2ᵏ⌋`, `shr_s` by constant is floor division of `s(·)` |
| counts | `clz`, `ctz`, `popcnt` | opaque to §3 except the range `[0, w]` |
| width | `i32.wrap_i64`, `i64.extend_i32_u`, `i64.extend_i32_s`, `extendN_s` | `mod 2³²`; `u(r)=u(a)`; `u(r)=s(a) mod 2⁶⁴`; sign-extension |

Drawn: the ordinary Codillon fraction. Error: only via R24/R25.

**R4 — comparisons, `eqz`, atom normalization.** A comparison `iNN.{eq,ne,lt_s,lt_u,gt_s,gt_u,le_s,le_u,ge_s,ge_u}`
or `eqz` produces an `i32` value that is exactly 0 or 1, with term `cmp(#a, #b)`. When such a value `#c` is consumed as a
**condition** (`if`, `br_if`, `select`) or named in a `(fact …)`, the atom `⟦#c⟧` is formed by these rewrites, applied
until none applies (all are equivalences, so the order is irrelevant):

1. `gt(a,b) → lt(b,a)`, `ge(a,b) → le(b,a)` (same signedness);
2. `eqz(x) → eq(x, 0)`; `ne(x, 0)` for a comparison or predicate call `x` → `x`; `eq(x, 0)` for a comparison or
   predicate call `x` → `¬x`; `¬¬A → A`;
3. `¬lt(a,b) → le(b,a)`, `¬le(a,b) → lt(b,a)`, `¬eq → ne`, `¬ne → eq`;
4. a non-comparison condition `x` → `ne(x, 0)`; a predicate call `(call $p …)` → `Pred($p, …)`, negated as
   `¬Pred($p, …)` (kept as a flag; no rewrite);
5. `eq` and `ne` are symmetric: their operands are put in ascending canonical-id order, constants last, so
   `eq(v, gcd_ref(a,b))` and `eq(gcd_ref(a,b), v)` have one normal form.

Two atoms **match** iff their normal forms are identical (same relation, signedness, width, head, canonical ids).
Drawn: comparison fractions are unchanged; the atom appears as a chip only when it becomes a fact (R16–R21).
Error: none.

**R5 — feeding a cup.** Premise: a cup with atom `G` on line `L`. Cups of a line are taken in order (value-operand
cups in pop order, then fact-parameter cups in parameter order, then edge cups, then the measure cup). If `prove` lines
directly above `L` have pending outputs, the first pending output feeds the first cup that neither lookup nor
evaluation can feed (R32). Otherwise lookup: scan the lane
from the top for a fact matching `G` (R4); the first match feeds the cup. Also: if every canonical id in `G` is a
constant, the cup may be fed by evaluation (R28). Conclusion: the cup is fed (a lookup-fed atom is not entered again, so it does not disturb `prove k`'s top-`k`); its
verdict is the feeding fact's verdict
(proven, or assumed if the fact's derivation depends on an `assume`/axiom; §4). Drawn: an always-on wire from the
feeding fact's chip (at its birth line) to the cup. Error (no feed): strict mode — `needs ⟨G⟩; nothing feeds it`, plus,
if the lane holds a fact that matches `G` except for one canonical id that is an older value of the same local,
`… ⟨G'⟩ is about the old $i (set at line N)` (the stale-fact hint, R7). Gradual mode — the cup becomes a runtime check (§4).

### Locals and globals

**R6 — `local.get $x`.** Premise: `cur[$x] = #n` (the id currently bound to `$x`). Conclusion: output id `#n`. Nothing
else: facts about `#n` already in the lane apply to this slot because they are about `#n`. Drawn: the ribbon from the
defining slot. Error: none.

**R7 — `local.set $x` / `local.tee $x`.** Premise: input id `#n`. If `$x` is declared `(T | R)`, a cup `R[v := #n]`.
Conclusion: `cur[$x] := #n`. Facts are untouched: facts mentioning the previous id `#m` of `$x` stay in the lane and
stay true (they are about the value `#m`), but cups that mention the new value of `$x` no longer match them. If the
cup is fed, enter `R[v := #n]` (so later reads need not re-prove it). Drawn: every lane chip that mentions `#m` and was
reachable through `$x` frays at this line (its ribbon unravels past this line, §8). Error: the refinement cup unfed →
`$x needs ⟨R⟩`. A local's refinement may name other locals; it is the local's invariant, so a
`local.set`/`local.tee` of any local `$n` that the refinement of `$r` names also owes the cup
`R_r[v := cur($r), $n := new]` (drawn on the set line, kind Refinement of `$r`). A local's refinement may not call a
memory-reading predicate (a store would falsify it unseen); error on the local's line.

**R8 — joins (merging local bindings).** At a point where control merges (the `end` of an `if` with two
fall-through arms, the `end` of a `block` that is the target of a `br`/`br_if`/`br_table`, a `loop` head), for each local
`$x`: if every incoming edge binds `$x` to the same id, keep it; otherwise allocate a fresh id `#φ` and bind it; if
`$x` is refined `(T | R)`, enter `R[v := #φ]` (the refinement is the local's own invariant; the cups of R7 and R19/R20
make it true on every edge). For a `loop`, the set of locals that may differ is found by a syntactic pre-scan of the loop
body for `local.set`/`local.tee` targets (all of them get a `#φ` at the loop head); the same pre-scan collects
`global.set` targets, and every mutable global if the body contains an impure call, and those globals get a `#φ` at the
loop head too (their refinements re-entered). **Block and `if` results** merge the same way: a result value that differs
across incoming edges is a fresh `#φ`, which carries only the frame's declared result refinements. Drawn: a small merge dot on the frame
bracket where `$x`'s ribbon is renumbered. Error: none.

**R9 — globals.** `global.get $g` returns `curg[$g]`. `global.set $g` binds it, with a cup if `$g` is refined (as R7).
Any impure call (R13) re-binds every mutable global to a fresh id, and enters its refinement if it has one. Immutable
globals get constant ids when initialized by a constant. Mutable globals are bound per function pass (a fresh id at
entry, φ-renamed at loop heads by R8), so no fact about one survives a `global.set` or impure call; and because pure
functions may not read them (R29), a predicate's value never depends on one. Drawn/Error: as R6/R7. A global's refinement may name only `v` (and call
pure, memory-free predicates); naming a local or parameter, or reading memory, is a module error and the refinement is
ignored. The initializer must satisfy it (checked by evaluation, R28); otherwise a module error, and every function's
copy of the refinement is an assumption. Every `global.set $g` cup anywhere in the module that is not proven (unfed,
runtime-checked, or resting on checks or assumes) is a dependency of `$g`'s refinement in *every* function: facts
derived from it are proven relative to those check lines (`*`) or assumed. (A caller still does not inherit a callee's
internal checks; a global's invariant is module-wide state, not a callee contract.)

### Memory

Let `M = 65536 · min` where `min` is the declared minimum page count of the module's single memory. Memory never
shrinks, so `M` is a valid lower bound on its size at every step, `memory.grow` included.

**R10 — loads.** Premise: `iNN.loadX offset=o` with address id `#a`, access width `N` bytes. Cup (bounds):
`(i32.le_u #a K)` with `K = M − o − N`; if `K < 0` the cup is `False` and the error reads `this access never fits in
memory (M bytes)`. Conclusion: output id `table[(opcode, o, #a, ε)]` where `ε` is the current memory epoch (R12), so two
loads of the same address in the same epoch are the same value. Narrow loads carry their range into §3 (`load8_u` is
`< 256`, `load16_u` is `< 65536`). Drawn: a proof cup to the right of the address cup, labelled `a ≤ K`. Error:
`needs ⟨u(a) ≤ K⟩ (bounds); nothing feeds it`.

**R11 — stores.** Premise: `iNN.storeX offset=o`, address `#a`, value `#x`. Cup: as R10. Conclusion: `ε := ε + 1`. Facts in
the lane are untouched (facts about values loaded in an earlier epoch remain true about those values), but facts whose
atoms carry an epoch (predicate calls that read memory, R12) no longer match cups in the new epoch. Drawn: the lane
chips that carry epoch `ε` fray at this line. Error: as R10.

**R12 — memory epochs.** The epoch `ε` is a counter in the function pass, starting at 0 on entry. It increments at
every store, `memory.fill`, `memory.copy`, and impure call. A predicate call that reads memory (contains a load in its
body or callees) is keyed and stored with the epoch it was evaluated in: its atom is `Pred($p, args)@ε`. At a join
whose incoming edges carry different epochs, and at a loop head whose body may bump the epoch (pre-scan, syntactic and
conservative: a store followed by `return` still counts), the join gets a fresh epoch. To carry a memory predicate into
a loop, state it as a loop fact (`loop (fact (call $rep_ok))`): its entry cup is in the entry epoch, its back-edge cups in
the head epoch (hashtable.wat, `$insert`). `memory.size` is a fresh value with the fact `(i32.ge_u #size min)` entered. Drawn: an epoch tick on the
frame bracket where it changes (only when some chip carries an epoch). Error: none.

### Calls and function boundaries

**R13 — `call $f`.** Premise: argument ids `#a₁ … #aₙ`. Cups: for each refined parameter `(param $pᵢ (T | Rᵢ))`, the
atom `Rᵢ[v := #aᵢ, $pⱼ := #aⱼ]`, and for each fact parameter `(param $h (fact P))` the atom `P[$pⱼ := #aⱼ]`, instantiated in the
caller's current epoch. Conclusion: if `$f` is impure (it stores, calls an import or an impure function,
grows memory, sets a global, or **reads a mutable global**), apply R12 and R9 first. The result id is `table[(call $f, #a…, ε if $f reads memory)]`
for a pure `$f`, fresh otherwise. Enter each result refinement `R[v := #r, $pⱼ := #aⱼ]` and each fact result, both in the epoch after the call. The callee's declared header is
the whole contract; its body is not consulted (except that a non-recursive predicate unfolds inside §3, R29). Drawn:
the call's fraction gains one proof cup per refined parameter, beside that parameter's cup; result facts appear as
chips on the call line. Error: `$f needs ⟨Rᵢ⟩ for $pᵢ; nothing feeds it`. An **imported** function's result refinements and fact results are entered with verdict *assumed* (the host is
trusted, not checked). Facts entered from a call inherit the verdict and check-dependencies of the cups that fed the
call's parameter cups (§4.1).

**R14 — function entry.** Each parameter gets a fresh id; parameter refinements and fact parameters are entered in order, origin = the
header line. Ordinary locals start bound to `const(T, 0)`. A refined local `(local $k (T | R))` has a cup `R[v := 0]` on its
declaration line (normally fed by evaluation, R28). `ε := 0`. Drawn: header chips. Error: on the local's line,
`$k starts at 0, which must satisfy ⟨R⟩`.

**R15 — function exit.** At the function's final `end` (if it can fall through) and at each `return`: the returned
id `#r` gets one cup per result refinement, `R[v := #r, $pⱼ := entry id of $pⱼ]`, and one cup per fact result
`(result (fact E))`, `E[$pⱼ := entry ids, $x := cur[$x]]`. Drawn: cups on the `return` line or on the closing `)` line.
Error: `result needs ⟨R⟩; nothing feeds it`.

### Control

Every control frame records `fact_mark` (lane height), `cur_saved` (local bindings), `eps_saved`, and a list of
**incoming edges** (snapshots of lane-above-mark, bindings and epoch) for its label. "Join" below means: bind locals by
R8 over the incoming edges; set `ε` by R12; cut the lane back to `fact_mark`; then re-enter every fact entered above the
mark that **matches a fact on every incoming edge** (intersection; it can only shrink); then enter the frame's declared
facts and result refinements, instantiated at the joined bindings, with origin = the `end` line.

**R16 — `block $l (fact E)* (result T|R)*`.** Entry: push a frame; lane and bindings unchanged. Every branch to `$l`
and the fall-through at `end` is an incoming edge and carries cups: each `E[cur]` and each result refinement on the
branched/returned value. At `end`: join. Drawn: the block's facts appear as chips on the `end` line; the cups appear on
each `br` line and on the `end` line. Error: `br $l needs ⟨E⟩` / `end of block needs ⟨E⟩`.

**R17 — `loop $l (fact E)* (param T|R)*`: invariants are block types.** Premise (fall-in edge): cups `E[cur]` on the
`loop` line, and refinement cups on loop params. Conclusion: push a frame; apply R8 to the locals found by the pre-scan
(fresh `#φ`, refined locals re-entered) and R12 (fresh epoch if the body may bump it); enter each `E[cur]` with origin =
the `loop` line. Every `br`/`br_if`/`br_table` to `$l` is a back-edge with cups `E[cur at the branch]`. The loop's `end` is
**not** a join (only fall-through reaches it): the lane after `end` is the lane of the fall-through path, cut to no
mark. There is no fixed-point iteration: the declared `E` is the whole loop summary. Drawn: invariant chips on the
loop line (pink bracket); back-edge cups on each branch line. Error: `loop entry needs ⟨E⟩` (on the loop line),
`back-edge needs ⟨E⟩` (on the branch line); the stale hint of R5 names the local whose `local.set` broke the match.

**R18 — `if $l? (fact E)* (result T|R)*`, `else`, `end`.** Premise: condition `#c`. Then-arm: push a frame; enter `⟦#c⟧`
(origin = the `if` line). At `else` (or at `end` if there is no `else`): record the then-arm's fall-through as an
incoming edge (if it can fall through), with cups `E[cur]`; restore bindings and epoch, cut to the mark, enter
`¬⟦#c⟧` (origin = the `if` line, drawn on the else side). At `end`: record the else-arm's fall-through edge (an absent
`else` is an arm that falls through immediately), then join. Consequence: `if … return end` keeps `¬⟦#c⟧` after `end`,
because the then-arm has no fall-through edge. Drawn: the then-fact chip on the `if` line, the else-fact chip on the
`else` line (or on `end` for an implicit else). Error: as R16.

**R19 — `br $l`.** Record an incoming edge for `$l`'s frame (for a loop: a back-edge) with its cups (R16/R17/R18). Then
the rest of the current arm is **dead** (R22).

**R20 — `br_if $l`.** Premise: condition `#c`. Taken edge: an incoming edge for `$l` whose lane has `⟦#c⟧` on top; its
cups are on the `br_if` line, and a `prove` feeding one of them gets `⟦#c⟧` as an extra hypothesis (drawn as a wire
from the `br_if`'s own condition cup), and its output enters only the taken edge's snapshot, never the fall-through
lane (R32). Fall-through: enter `¬⟦#c⟧` (origin = the `br_if` line). Drawn: the
fall-through chip on the `br_if` line; taken-edge cups on the same line, to the right of the condition cup.

**R21 — `br_table $l₀ … $lₙ₋₁ $d`.** Premise: index `#i`. Edge to `$lⱼ`: lane plus `(i32.eq #i j)`; edge to `$d`: lane plus
`(i32.ge_u #i n)`; each edge carries its target's cups (a target listed twice gets the disjunction only through two
separate edges, each checked). The rest of the arm is dead.

**R22 — `return`, and dead code.** `return` checks R15 at this point, then the rest of the arm is dead. In dead code
(after `br`, `br_table`, `return`, `unreachable`, until the arm's `else`/`end`) the lane holds the single extra fact
`False` with origin = the line that ended the arm; every cup there is fed by it (ex falso), mirroring Wasm's
stack-polymorphic typing. Dead code contributes no incoming edges. An `end` reached only by dead code stays dead unless its frame's label has
incoming edges (a `block`/`if` that was branched to); a `loop`'s `end` after a back-edge is therefore dead. Drawn: dead lines dimmed; their cups show a
faint wire to the ending line. Error: none.

**R23 — `select`, `drop`, `nop`.** `select` with `#a #b #c` produces `table[(select, #a, #b, ⟦#c⟧)]`, read by §3 as
`ite(⟦#c⟧, a, b)`. `drop` and `nop` do nothing to the lane.

### Trap obligations

Wasm arithmetic never traps; it wraps (R3). The only traps a v2 program can contain are the ones below, plus call-stack
exhaustion (carved out in §6). Each trap is a cup.

**R24 — division and remainder by zero.** `iNN.div_u`, `div_s`, `rem_u`, `rem_s` with divisor `#b`: cup `ne(#b, 0)`.
Typical feeds: the fall-through of `local.get $y; i32.eqz; br_if $done` enters `¬eq(#y,0) = ne(#y,0)` (R4 rule 3), an
exact match; a refinement such as `$at_least_2` needs `prove 1` (`u(b) ≥ 2 ⇒ b ≠ 0`). Drawn: a cup labelled `b ≠ 0` to the
right of the divisor cup. Error: `needs ⟨b ≠ 0⟩; nothing feeds it`.

**R25 — signed overflow of division.** `iNN.div_s` additionally has the cup `ne(#b, −1) ∨ ne(#a, INT_MIN)` (a disjunctive
cup: lookup accepts a fact matching either disjunct; `prove` gets the disjunction as its goal). `rem_s` has no such cup.
Drawn: cup labelled `¬(a = MIN ∧ b = −1)`. Error: likewise.

**R26 — `unreachable` consumes False.** Cup: `False`. Feeds: a `prove k` whose hypotheses are contradictory, or dead
code (R22). Conclusion: the rest of the arm is dead. This card is how functional specs work: a harness ends a failed
check in `unreachable`, so proving every `unreachable` cup proves the spec (§6). Drawn: a distinctive **False cup**
(an inverted, hatched cup, §8). Error: `reachable: needs False; nothing feeds it`.

**R27 — conversions and other traps.** `iNN.trunc_fMM_s/u` has two cups, `(fMM.gt #f LO)` and `(fMM.lt #f HI)`, where LO and HI are
the nearest values of the source float type just outside the target range: for f64 sources −2^31−1 / 2^31 (i32_s) and
−2^63−2048 / 2^63 (i64_s); for f32 sources −2^31−256 / 2^31 (i32_s) and −2^63−2^40 / 2^63 (i64_s); unsigned −1 / 2^32
or 2^64. The cups also
exclude NaN, since every comparison with NaN is 0. Floats are opaque to §3: these cups are fed only by exact lookup of a
float comparison fact, or by evaluation on constants. `trunc_sat` forms have no cup and are recommended. `call_indirect` has
the cup `CallIndirectOk`, which no rule produces: it is always runtime-checked (gradual) or an error (strict): "outside v2".

### Evaluation, predicates, unfolding

**R28 — evaluation on constants.** Premise: a cup, hypothesis or goal atom whose ids are all constants, and whose
head is a builtin or a predicate that does not read memory. Conclusion: run it on the reference interpreter with a
budget of **100,000 Wasm steps** (a fixed constant of the kernel). Nonzero → the cup is fed, origin "evaluation",
verdict proven. Zero → verdict **refuted**: `⟨G⟩ is false: $p(2, 7) = 0`. Budget exceeded → the cup is unfed with
`evaluation exceeded 100000 steps` (deterministic: the same text always gives the same outcome). Drawn: the cup is
filled with a small `=` mark instead of a wire. Error: as described.

**R29 — predicate functions; automatic unfolding.** A function named in any proposition is a **predicate**. It must
be: pure (no store, `memory.grow`, `global.set`, **no `global.get` of a mutable global**, no imports, no calls to
non-predicates), loop-free, `i32`-resulting,
free of refined or fact parameters (so it is total on every argument; partial domains are handled by guards inside),
directly self-recursive at most (with a measure, R31), and every cup in its body must be proven or fed by an axiom; a
runtime-checked cup is not allowed in a predicate (the kernel evaluates predicates, so they must be total). It may
read memory (its atoms then carry an epoch, R12). **Inside §3 only**, an atom `Pred($p, args)` for a non-recursive
`$p` is replaced by its body: the body is executed symbolically (straight-line code to terms; `if`/`br_if`/`return` to
`ite` terms), with nested non-recursive predicates unfolded to depth 4, recursive ones left as atoms. Lookup (R5) never
unfolds. Error (on the predicate's header): `predicate $p must be pure: line N stores` / `… has a loop` / `… is
recursive without measure:$p`.

**R30 — `unfold $p e₁ … eₙ`: one step of a recursive predicate.** Premise: `$p` is a recursive predicate. Conclusion:
enter the fact `eq((call $p e…), BODY₁)` where `BODY₁` is `$p`'s body executed symbolically once, with each recursive call
left as the atom `call $p (args)`. Unfolding never happens on its own. Drawn: a chip `p(n,d) ≡ …` on the line. Error:
`$p is not recursive; it unfolds automatically`.

**R31 — measures.** For a recursive predicate or lemma `$f` with `(export "measure:f")` function `$m`: each recursive call
site (a `call $f` in a predicate, a `lemma $f` in a lemma) with arguments `a′`, in a body whose parameters are `p`, has the
cup `lt_u((call $m a′), (call $m p))`. `$m` must be a non-recursive predicate-like function (pure, loop-free) with the
same parameters as `$f`, so §3 unfolds it. Drawn: a cup labelled `μ↓` on the recursive call. Error: `measure must
decrease: needs ⟨μ(a′) < μ(p)⟩`.

### Proof lines

**R32 — `prove k`.** Premises: `k ≤ 8`; hypotheses `H₁ … H_k` = the `k` most recent lane entries at this line (plus the
edge fact of R20 when it feeds a taken-edge cup); goal `G` = the cup this line feeds (R5). Conclusion: if §3 reports
**valid** for `H₁ ∧ … ∧ H_k ⇒ G`, the cup is fed and `G` enters the lane (origin = this line, verdict = proven, or
assumed if some `Hᵢ` is assumed, and relative to checks if some `Hᵢ` is, §4). **Edge cups:** when the fed cup is a
taken-edge cup of `br_if`/`br_table` (R20/R21), `G` enters only that edge's snapshot (the target's join or loop
summary), never the fall-through lane, where it would not be true. Drawn: a fraction with `k` proof cups above the rule (wired to the hypotheses' chips)
and one fact below (wired to the goal cup). Errors (on the `prove` line; the goal cup stays unfed) always **list the hypotheses actually taken**, so a
miscounted `k` is visible: `not implied by [u(i) < 8 @22, $sq_le(r,n) @31]: counterexample u(i)=8, u(n)=8`; `exceeds the 64-term cap; use a lemma`; `nothing to feed` (no cup below).
A failed `prove` never refutes the goal; it only fails to feed it.

**R33 — lemmas and axioms.** A lemma is exported as `lemma:<name>`; it has value params, fact params
`(param $h (fact P))` and only fact results. (Ordinary functions may also have fact params and fact results: they are
pre- and postconditions not about a single value, e.g. a memory invariant; callers feed them with cups as in R13.) Its body is **ghost code**: checked by every card above (case analysis with `if`, `prove`, `lemma`, recursion
with a measure = induction), never executed, erased to `nop`s. Ghost code may not contain loops, stores, or impure calls,
may call (`call`) only predicates (R29 keeps them total), has only fact results, and may recurse only directly through
`lemma $self` with a measure (R31); recursion through other lemmas is an error. A lemma is never the target of `call`
(error: `$f is ghost code: write lemma $f …`). These rules make every lemma total, which the erasure argument of §6
needs: a lemma that could fail to return would "prove" False and erase to `nop`. Ghost code
has no gradual mode: an unfed cup there is an error. The line `lemma $f e₁ … eₙ` has one cup per fact param,
`P[$params := e]` (plus the measure cup of R31 if `$f` is the enclosing lemma), and enters, in this order, the atoms
of its prove-fed cups and then each fact result `Q[$params := e]` (origin = this line). An **axiom** is exported
as `axiom:<name>` and has an empty body; its results enter with verdict **assumed**. A lemma with an error in its body
also produces assumed facts (reason: `lemma $f is unproven`). Error on the lemma line: `$f needs ⟨P⟩`.

**R34 — `assume (fact E)`.** Enters `E[cur]` with verdict assumed. Forbidden in LLM-owned code (§7) and in predicates.

**R35 — gradual mode: runtime checks.** In gradual mode, an unfed cup on an executable line (not ghost, not a
predicate) becomes a **runtime check**: before the instruction runs, the instrumented program evaluates the atom on
the concrete values (calling predicates). If it is false, Codillon stops with 💣 and `check failed: ⟨G⟩` on that line;
the cup's verdict becomes **refuted** for that recorded input. Strict mode (and vericoding mode, §7) reports unfed cups
as errors instead. A pure call or load recorded in a shadow local is read by a check only if a capture of it dominates
the check (an earlier line whose enclosing block arms are all still open at the check); otherwise the host
re-evaluates the call. The top parameter of a loop is captured after the `loop` line (on entry and on every back edge).
Float terms are evaluated host-side exactly as Wasm computes them. (Known gap: a check whose terms cannot be evaluated,
such as one naming a parameter below the top of a multi-parameter loop or a multi-value join result, currently passes.)

## 3. The decision procedure behind `prove k`

### 3.1 Contract

Input: hypotheses `H₁…H_k` (atoms, R4 normal form), a goal `G` (an atom, `False`, or the disjunction of R25), and read
access to the function's slot graph (the term behind every canonical id). Output, deterministically:
`Valid`, or `NotImplied(countermodel)`, or `Cap(which)`, or `Inexact(var)`. Only `Valid` feeds the cup. The procedure
never consults the lane; everything it may use is drawn as one of the `k` wires or is the meaning of an instruction.

**Fragment.** Quantifier-free linear integer arithmetic over the unsigned readings of `i32`/`i64` values, with Wasm
wraparound made explicit, plus: nonlinear monomials treated as atoms, opaque leaves with ranges, `ite` from `select`
and unfolded predicates, and propositional float atoms. **Caps** (constants of the kernel, printed on card R32):
64 terms per normalized atom; 32 atoms total (hypotheses, goal, definitional constraints); 24 integer variables
(including auxiliaries); 256 cases; 256 constraints alive at any elimination step; coefficients fit `i128`.

### 3.2 Step 1 — normalize terms to linear forms

Every id reachable from an atom is translated once (memoized in the scratch area, so shared subterms are one
variable) to a **linear form** `Σ cᵢ·xᵢ + c₀` over integer variables, together with side constraints. Each variable
has an interval. Translation is **bottom-up** (post-order over the term DAG): a term is translated only after its
inputs, its interval is computed from theirs immediately, and its own wrap variable is resolved at once if the interval
allows (§3.3); only then does its parent use it. Two rules apply to every row with a wrap variable `q`:

- **Result range.** The term's linear form `T` carries the side constraint `0 ≤ T ≤ 2ʷ − 1`. This is what makes `q` the
  quotient (`q` is the unique value putting `T` in range); without it `eq(add(x,0), x)` would have the model `q = 1`.
- **No expansion through an unresolved wrap.** `mul(a,b)` expands `A·B` only if neither `A` nor `B` still contains an
  unresolved wrap variable; otherwise the product is a monomial over the factors' canonical ids (keyed by the sorted
  id list). Expansion is retried per case after case-split substitution (§3.4), so i64 `(r+1)·(r+1)` expands to
  `r² + 2r + 1` as soon as `r+1`'s carry is fixed, and coefficients like `2¹²⁸` never arise.

| term | linear form and side constraints |
|---|---|
| leaf (param, `#φ`, load, impure call result, `clz`/`ctz`/`popcnt`, recursive or memory-reading predicate call, any other opaque term) | fresh variable `x ∈ [0, 2ʷ)` (narrower for narrow loads, counts, 0/1 comparison values) |
| constant `c` | `u(c)` |
| `add(a,b)` | `A + B − 2ʷ·q`, `q ∈ [0,1]` |
| `sub(a,b)` | `A − B + 2ʷ·q`, `q ∈ [0,1]` |
| `mul(a, c)`, `shl(a, c)` (constant) | `k·A − 2ʷ·q`, `k = c` (mul) or `2^(c mod w)` (shl), `q ∈ [0, k)` |
| `mul(a,b)` both non-constant | expand `A·B` as a polynomial; each degree-≥2 monomial (`r·r`, `i·j`) becomes a monomial variable, keyed by its sorted factor list; minus `2ʷ·q`, `q ≥ 0` |
| `div_u(a, c)`, `shr_u(a, k)` (constant `c ≥ 1`) | fresh `d` with `c·d ≤ A ≤ c·d + c − 1` |
| `rem_u(a, c)`, `and(a, 2ᵏ−1)` (constant `c ≥ 1`) | `A − c·d`, `d` fresh with the same bounds (so result `∈ [0, c)`) |
| `div_u`/`rem_u`/`div_s`/`rem_s` by the **constant 0** | in a hypothesis the fact is unsatisfiable-free only if never evaluated, so treat the term as an opaque leaf; in a goal the fact is false (it would trap) |
| `div_u(a,b)`, `rem_u(a,b)` non-constant | fresh variable `r` with `r ≤ A`; for `rem_u` also `r + 1 ≤ B`, because a real slot's value exists, so `b ≠ 0` (R24). For a **virtual** slot (from an unfolding or an instantiated proposition) the trap-free reading of facts applies: in a hypothesis, add `B ≥ 1`; in a goal, the `B = 0` case makes the goal false (it is provable only if `B ≥ 1` follows). The result bound `r ≤ A` and `r + 1 ≤ B` are applied only together with `B ≥ 1` (kernel review B5) |
| `wrap_i64(a)` | `A − 2³²·q` |
| `extend_i32_u(a)` | `A` |
| `extend_i32_s(a)`, signed reading `s(x)` | `A − 2ʷ·σ` (or `A + (2⁶⁴ − 2³²)·σ` for extend), `σ ∈ [0,1]` with `2ʷ⁻¹·σ ≤ A ≤ 2ʷ⁻¹ − 1 + 2ʷ⁻¹·σ` |
| `shr_s(a, k)` (constant) | `D + 2ʷ·τ`, `τ ∈ [0,1]`, `D` a signed variable in `[−2ʷ⁻¹⁻ᵏ, 2ʷ⁻¹⁻ᵏ)` with `2ᵏ·D ≤ S(a) ≤ 2ᵏ·D + 2ᵏ − 1`, where `S(a)` is the signed reading below |
| `div_s`, `rem_s`, rotations, `xor`/`or`, `and` with other masks, non-constant shifts | opaque leaf |
| comparison or `eqz` used as a value; `select`; unfolded predicate `if` | `ite(cond, t, e)`: a **case split** (3.4) |
| `call $p` non-recursive predicate | its body term (R29) |

Atoms become constraints: `lt_u(a,b)` → `A + 1 ≤ B`; `le_u` → `A ≤ B`; `eq` → `A = B`; `ne` → split `A + 1 ≤ B ∨ B + 1 ≤ A`;
signed relations use signed readings; `Pred`/`ne(x,0)` on a leaf → `x ≥ 1`; negations by R4. The goal is **negated**
and added; the problem is valid iff every case is unsatisfiable.

**The 64-term cap.** After expansion, an atom whose linear form has more than 64 terms (variables plus monomials) aborts
with `Cap(terms)`: `this fact expands to 71 terms (cap 64); state an intermediate fact with a lemma`. The cap is checked
on each atom after unfolding, before any solving, so it depends only on the text.

### 3.3 Step 2 — interval pre-pass and wrap elimination

Intervals start from the table above. Two fixed rounds then tighten them, in hypothesis order, using every
constraint that has a **single variable** against a constant (`x ≤ c`, `x ≥ c`, `x = c`, including the negated goal
when it has that shape). After each round, monomial intervals are recomputed from factor intervals, and every wrap
variable `q` is resolved if possible: `q` is set to the unique value that puts the exact result's whole interval inside
`[0, 2ʷ)`, if there is one (for `add`, `[0,2ʷ)` gives `q = 0` and `[2ʷ, 2ʷ⁺¹)` gives `q = 1`; for `sub`, `[0,2ʷ)` gives `q = 0`
and `[−2ʷ, 0)` gives `q = 1`). Terms whose wraps become resolvable after the hypothesis rounds are re-translated once,
bottom-up, with the tightened intervals. **These are the explicit no-overflow side conditions**: a wrap disappears only when the intervals
prove it cannot happen, and the reason is recorded (shown on hover of the `prove` fraction: `i+1 does not wrap: u(i) ≤ 7`).
A variable whose interval is a single point is substituted by its value (so `r = 65535` turns `r·r` into a constant).
Remaining wrap and sign variables with range `[0,1]` (`q` of `add`/`sub`, `σ`, `τ`) become **case splits** (3.4), so
they never reach elimination with their large `2ʷ` coefficients; in each case the chosen values are substituted, then
products whose factors became wrap-free are expanded (the per-case retry of §3.2). Other `q` and `d` are ordinary bounded
variables.

### 3.4 Step 3 — case splitting

Splits come only from unresolved `[0,1]` wrap/sign variables (two cases), `ne` constraints (two cases), `ite` terms
(two cases), and propositional float atoms (two cases, or none if the atom is also a hypothesis). They are enumerated in a fixed order (by the id of the splitting term) with
early exit: a case is abandoned as soon as it is unsatisfiable. More than 256 leaf cases → `Cap(cases)`.

### 3.5 Step 4 — Omega-lite on each case

Each case is a conjunction of linear constraints `Σ cᵢxᵢ ≤ d` and equalities over at most 24 integer variables.

1. **Equalities.** Take equalities in order. If one has a variable with coefficient ±1, solve for it (the
   lowest-numbered such variable) and substitute everywhere. Otherwise, if the gcd of its coefficients does not divide
   the constant, the case is unsatisfiable; else keep it as two inequalities.
2. **Tighten.** Divide each inequality by the gcd `g` of its coefficients and replace `d` by `⌊d/g⌋`. A constraint
   `0 ≤ d` with `d < 0` makes the case unsatisfiable. Drop duplicates; keep the tighter of two parallel constraints.
3. **Eliminate.** Choose the variable with the fewest (lower × upper) bound pairs, ties to the lowest number. Combine
   every lower bound with every upper bound (Fourier–Motzkin), then tighten. If every pair has a unit coefficient on the
   eliminated variable, the step is **exact** for integers. Otherwise it is the real shadow, which is sound for
   unsatisfiability; mark the case **inexact**.
4. Repeat until no variables remain. All constant constraints satisfied ⇒ the case is satisfiable: if every step was
   exact, back-substitute (each eliminated variable takes the least integer allowed by its bounds, in reverse order) to
   obtain a **countermodel**, mapped back to program names (`u($i) = 8, u($n) = 8`); if some step was inexact, return
   `Inexact(x)` instead.

More than 256 constraints alive → `Cap(constraints)`; an `i128` overflow → `Cap(coefficients)`. There is no other
source of nondeterminism: variable numbering is the order of first appearance in hypotheses, then goal.

### 3.6 Why this algorithm

- **Intro facts are unit-coefficient.** Bounds (`i < n`, `i + 1 ≤ n`, `16 + 4·i ≤ 44`), parity via `and 1`, guards, carries:
  nearly all eliminations are exact, so the procedure is complete where students live and returns real countermodels.
- **Wraparound is explicit, not ignored.** A wrap variable is either removed by an interval argument the student can
  read on hover, or stays in the problem, where it usually blocks the proof and the countermodel shows the wrapping
  value. That is the isqrt lesson in one mechanism.
- **Bit-blasting was rejected**: 64-bit multiplication is thousands of clauses and needs a SAT solver, which is search.
  Full Omega (splinters) was rejected for size; `Inexact` is rare, reported deterministically, and fixed with a lemma.
- **Nonlinear facts are atoms.** `r·r` and `(r+1)·(r+1)` share the monomial `r²`, so `(r+1)² = r² + 2r + 1` is linear
  reasoning. Facts that need real nonlinear reasoning (`x ≤ y ⇒ x² ≤ y²`) are lemmas or instructor axioms, by design.
- **Cost** is bounded by the caps: at most 256 cases × FM on ≤ 24 variables with ≤ 256 constraints; in practice a few
  microseconds per `prove`, so re-checking a function on each keystroke is instant.

### 3.7 Failure reports (all on the `prove` line; the goal cup stays unfed)

| result | commentary |
|---|---|
| `NotImplied(m)` | `not implied by [u($i) < 8 @22, $sq_le($r,$n) @31]: u($i)=8, u($n)=8` (every failure lists the hypotheses taken, with their birth lines) |
| `Inexact(x)` | `could not decide (inexact step on $r·$r); add a lemma` |
| `Cap(terms)` | `fact expands to 71 terms (cap 64)` |
| `Cap(cases)`, `Cap(constraints)`, `Cap(coefficients)` | `too many cases (cap 256)` etc. |
| no consumer | `prove has nothing to feed` |
| `k` too large | `only 3 facts in scope` |

## 4. The verdict model

### 4.1 Four states

Every cup ends a check in exactly one of four states.

| state | meaning | how it arises |
|---|---|---|
| **proven** | a derivation in the text feeds the cup, and none of its facts depends on an assumption | R5 lookup, R28 evaluation, R32 `prove`, R22 dead code |
| **refuted** | the cup's proposition is false for a concrete witness | R28 evaluation to 0 on constants, or a runtime check (R35) that failed on a recorded input, or a harness run that reached the cup's `unreachable` |
| **runtime-checked** | nothing feeds the cup; gradual mode compiles it into a check that runs before the instruction | R35 |
| **assumed** | fed, but the derivation uses an `assume`, an `axiom:` function, or an unproven lemma | R33, R34; the cup records which assumptions |

**Refuted, precisely.** Static refutation comes only from R28 (an all-constant atom evaluates to 0). Dynamic
refutation comes from a run of the **instrumented** program in gradual mode (checks inserted by R35): the first check
that fails on a recorded input refutes its cup, and the run stops there, so cups after it on that path stay
runtime-checked for that input. A harness `False` cup is also refuted when an instrumented run reaches its
`unreachable`. Runs of the erased program (the example runner) are tests of behaviour, not of individual cups.

A cup that is fed and also refuted by a run means that some premise of its derivation is false on that input: either
an `assume`/axiom (the kernel marks that line `contradicted by run (input …)`), or a runtime-checked cup upstream whose
check would have stopped the run first if the run had been instrumented (in gradual mode it always is, so in practice
this case only arises from erased-program tests).

**Relative to checks.** A derivation can be valid while resting on a fact whose own cup is runtime-checked: a join fact
whose arm cups are runtime-checked (R16–R18), a refined local re-entered at a φ (R8) when a `local.set` cup was
runtime-checked, a call result whose parameter cup was runtime-checked (R13). Every `Fact` therefore carries the set of
runtime-checked cup lines it depends on (§5.1), and every fed cup inherits the union over its feeding facts. A proven
or assumed cup with a non-empty set is shown as **proven\*/assumed\* — relative to checks at lines …** (§8), and
reported with `depends_on_checks: [lines]`. Nothing downstream of a runtime check ever shows as plain proven. The set is
per function: a caller does not inherit a callee's internal checks (it relies on the callee's contract, and the callee's
own status says whether that contract is verified).

**Modes and VERIFIED.** *Gradual* is the editor default for everyone: programs always run, unfed cups become checks,
and only refuted cups are errors. *Strict* reports every runtime-checked cup as an error (`needs ⟨G⟩; nothing feeds
it`). A function is **VERIFIED** (a badge on its header line) only when it is **strict-clean**: no runtime-checked cup,
no cup relative to checks, no `assume`, and every assumed cup rests only on instructor axioms; and every function it calls
is VERIFIED. Gradual mode shows the badge too, so a student sees which functions are proven while still running
everything. *Vericoding* (§7) accepts an LLM submission only if every function it touched is strict-clean.

### 4.2 Why there is no "unknown"

The kernel never answers the question "is this proposition true?". It answers "does the text contain a derivation of
it?", which is decided by a terminating, deterministic check: lookup is equality, evaluation has a fixed step budget,
and §3 always returns one of its four outcomes within its caps. When there is no derivation, the cup is *unfed*, a
fact about the text that the student can fix by adding a line, and gradual mode turns it into a runtime check, so the
program still runs and still tells the truth on every input it is given. "Refuted" is only ever claimed with a
concrete witness. A `prove` that fails is not "unknown" either: it is a line that failed, with a countermodel or a named
cap, and its cup is unfed. Compare v1, where Z3 could time out on the same text on a slower machine.

### 4.3 Per-cup kernel output (Rust)

```rust
pub enum Verdict { Proven, Refuted, RuntimeChecked, Assumed }

pub enum CupKind {
    Bounds,                 // R10/R11
    DivByZero, DivOverflow, // R24, R25
    Refinement { param: u32 },   // R13 call argument, R7 local.set/tee, R9 global.set
    ResultRefinement,       // R15
    BlockFact { label: u32 },    // R16/R18 exit fact (br or end)
    LoopEntry, BackEdge,    // R17
    FactParam { param: u32 },    // R33 lemma argument
    Measure,                // R31
    False,                  // R26
    Conversion, CallIndirect,    // R27
    LocalInit,              // R14
}

pub enum Feed {
    Lookup   { fact: FactId, origin_line: u32 },
    Prove    { prove_line: u32, hyps: SmallVec<[FactId; 8]>, wraps_removed: SmallVec<[WrapNote; 4]> },
    Eval     { steps: u32 },
    DeadCode { ended_at: u32 },
    Unfed,
}

pub enum Witness {
    Eval    { value: i64 },                         // R28: the predicate returned 0
    Run     { func: FuncIdx, args: Vec<u64>, step: u32 },  // R35 or a harness run
}

pub struct CupOut {
    pub line: u32,
    pub operand: Option<u8>,     // the value operand the cup sits beside (pop order, 0 = deepest); None = line-level
    pub kind: CupKind,
    pub goal: AtomText,          // rendered with program names: "u($i) < 8"
    pub verdict: Verdict,
    pub feed: Feed,
    pub assumptions: SmallVec<[Origin; 2]>,   // non-empty iff Assumed
    pub depends_on_checks: SmallVec<[u32; 2]>, // runtime-checked cup lines this derivation rests on (§4.1)
    pub witness: Option<Witness>,             // Some iff Refuted
    pub diag: Option<String>,                 // commentary text, if any
}

pub struct FuncOut {
    pub verified: bool,                       // strict-clean and all callees verified (§4.1)
    pub cups: Vec<CupOut>,
    pub line_errors: Vec<(u32, String)>,      // prove failures, predicate purity, stale-handle errors
    pub chips: Vec<ChipOut>,                  // lane facts to draw: (birth line, atom text, frayed_at: Option<u32>)
}
```

`v2-examples/*.expect.json` is a serialization of `cups` (§README there).

## 5. Checker data structures and algorithm

### 5.1 Structures (all flat vectors; no GC, no trees)

```rust
pub type SlotId = u32;   // index into slots
pub type CanonId = u32;  // value number; also an index into slots (the defining slot)
pub type FactId = u32;   // index into facts

pub struct Slot {                    // today's Codillon slot, plus two fields
    pub ty: ValType,
    pub line: u32,                   // defining line
    pub canon: CanonId,              // value number (R1)
    pub facts: Range<u32>,           // facts born on this slot's line (for drawing chips)
}

pub enum Head { Cmp { rel: Rel, signed: bool, wide: bool }, Pred(FuncIdx), False, FloatCmp(Opcode), Or2, Eq2 }
pub struct Fact {
    pub head: Head,
    pub neg: bool,
    pub args: Range<u32>,            // into fact_args
    pub epoch: Option<u32>,          // Some for memory-reading predicates (R12)
    pub origin: Origin,              // { line: u32, kind: OriginKind } (branch, entry, call, prove, lemma, eval, …)
    pub verdict: Verdict,            // Proven or Assumed (propagated to the cups it feeds)
    pub assumed_by: Range<u32>,      // into prov: assume/axiom origins this fact rests on (for §7.1 rule 3)
    pub checks: Range<u32>,          // into prov: runtime-checked cup lines this fact rests on (§4.1)
}
pub prov: Vec<u32>;                  // provenance arena (origin lines), shared by assumed_by and checks
pub fact_args: Vec<CanonId>;

pub struct Frame {                   // existing control-frame fields, plus:
    pub fact_mark: u32,              // lane height at entry
    pub locals_mark: u32,            // into a saved-bindings stack: cur[] at entry
    pub eps_at_entry: u32,
    pub edges: Range<u32>,           // incoming edges recorded for this label (into `edges`)
    pub declared: Range<u32>,        // its (fact …) clauses, as uninstantiated templates
}
pub struct Edge { pub lane: Range<u32>, pub bindings: Range<u32>, pub eps: u32 }  // lane slice copied to edge_facts

pub struct FuncState {
    slots: Vec<Slot>, facts: Vec<Fact>, fact_args: Vec<CanonId>,
    lane: Vec<FactId>,               // the fact lane: a stack of fact ids in scope
    cur: Vec<CanonId>,               // local index → current value number
    curg: Vec<CanonId>,              // mutable global index → current value number (saved/restored per frame like cur)
    saved: Vec<CanonId>,             // bindings saved per frame
    frames: Vec<Frame>, edges: Vec<Edge>, edge_facts: Vec<FactId>, edge_bindings: Vec<CanonId>,
    vn: HashMap<VnKey, CanonId>,     // cleared per pass
    // VnKey = (Opcode, Imm, args: SmallVec<[CanonId; 4]> /* any arity: calls, select */, epoch: u32 /* or 0 */)
    eps: u32, next_eps: u32,         // memory epoch (R12)
    handles: Vec<Option<FactId>>,    // fact locals and fact params (§1.5); saved/restored per frame
    pending: SmallVec<[PendingProve; 4]>,  // prove lines waiting for their consumer (R32)
    scratch: Scratch,                // §3 workspace, reset per prove
    out: FuncOut,
}
pub struct Scratch { terms: Vec<Lin>, memo: HashMap<CanonId, u32>, vars: Vec<Interval>, cons: Vec<Ineq>, cases: u32 }
```

Sizes: a `Slot` is 16 bytes plus the range; a `Fact` about 24 bytes; facts per function are bounded by the number of
branch, block, call, entry and proof lines (each enters at most a handful).

**Lifetimes nest.** (1) The pass: `slots`, `vn`, `facts`, `fact_args` (arenas cleared per function pass). (2) A frame:
`lane` above `fact_mark`, saved bindings, edges (cut at `end`). (3) One `prove` or evaluation: `scratch` (reset).

### 5.2 One pass per function

```
check_function(f):
  reset arenas; eps := 0; cur := fresh ids for params, const 0 for locals
  enter header refinements (R14); cups for refined locals' initial value (R14)
  push the function frame
  for each line L in body order:
    if L is a proof line: handle prove/lemma/unfold/assume/handle ops (R30–R34, §1.5); continue
    pop operand ids (Codillon already knows the inputs of every slot)
    compute cups for L (R7, R10, R11, R13, R15, R24–R27, R31, edge cups of R16–R21)
    feed each cup (R5): pending prove outputs first (§3 runs here), else lookup, else evaluation;
       record CupOut; if fed by prove or evaluation, enter the atom (a lookup-fed atom is already in the lane,
       and is not entered twice, so `prove k`'s top-k is not disturbed by lookups)
    apply L's effect: value numbering (R1–R4, R23), bindings (R6–R9), epoch (R11–R13),
       control (R16–R22): push frame / record edge / join / mark dead
  at the function end: R15 cups; any pending prove left → "nothing to feed"
```

Pre-scans (syntactic, linear): for each `loop`, the set of locals it assigns and whether it may bump the epoch; for
each function, purity and memory-reading (needed by R12/R13), computed once per module from the call graph.

No fixed-point iteration anywhere: loop heads use declared invariants and refined-local types (R17, R8), joins
intersect (they never need to re-run), and every other function is seen only through its header.

### 5.3 Incremental re-checking

An edit to a line inside function `f`'s body re-checks `f` only (cost: one pass plus its `prove`s). An edit to `f`'s
**header** (its contract) re-checks `f` and every function that calls `f` or uses `f` in a proposition. An edit to a
predicate's or measure's body re-checks the predicate and every function whose `prove`s unfolded it (recorded in a
per-function dependency set filled by §3 during the previous pass). Purity changes propagate along the call graph. The
kernel memoizes nothing else, so the result never depends on edit history.

## 6. What a fully proven program guarantees

### 6.1 Trap-freedom theorem

Let `f` be a function, and suppose every cup in `f` and in every function reachable from `f` through calls (and every
predicate, measure and lemma they use) is **proven**, with no `assume` and no axiom in its derivation. Then for every
argument tuple satisfying `f`'s parameter refinements, every execution of the erased Wasm `f` either

1. returns normally, with results satisfying `f`'s result refinements and fact results; or
2. runs forever (v2 proves no termination for ordinary code: loops and non-predicate recursion have no measures); or
3. is stopped by call-stack exhaustion, whose depth is implementation-defined (the **call-stack carve-out**).

It never executes a trapping instruction: no division by zero, no `INT_MIN / −1`, no out-of-bounds access, no invalid
conversion, no `unreachable`.

If some cups are **assumed**, the theorem holds relative to those assumptions. If some are **runtime-checked**, the
erased program with checks inserted satisfies the theorem with "trap" replaced by "a failed check stops the program at
the cup's line", which is what gradual mode runs.

*Proof sketch.* Standard progress-and-preservation over the Wasm small-step semantics with a lane invariant: at every
reachable line every lane fact is true of the current values (by induction on the cards: branch facts by the
semantics of `if`/`br_if`, joins by intersection, loop heads by entry and back-edge cups, call results by the callee's
proven exit cups, `prove` by soundness of §3, evaluation by the reference interpreter, lemmas by induction on their
measure). Every trapping instruction's cup is fed by a true fact, so its trap condition is false. Predicates are total
(measures, loop-free, all cups proven), so evaluating them in a proposition is meaningful. Value numbering is sound
because equal ids denote the same pure term over the same inputs in the same epoch.

### 6.2 Harnesses: functional correctness as trap-freedom

Trap-freedom alone is too weak (wrong answers do not trap) and too easy (`if (i < n) load else return 0`). A
functional spec is therefore an ordinary exported function `harness:<name>` that calls the code under test, computes a
check, and reaches `unreachable` iff the check fails:

```wat
(func $isqrt_harness (export "harness:isqrt") (param $n i32)
  local.get $n
  call $isqrt               ;; result fact: $is_isqrt(ext_u(#r), ext_u($n))
  i64.extend_i32_u
  local.get $n
  i64.extend_i32_u
  call $is_isqrt            ;; the check, the same predicate
  br_if 0                   ;; check passed: leave the function
  prove 2                   ;; hypotheses: ¬check (fall-through) and the call's result fact
  unreachable               ;; cup: False
)
```

The **same text** is a test and a theorem. Run on concrete inputs (Codillon's slider, or the example runner), it is a
test: reaching `unreachable` is a 💣 with a recorded input, which refutes the `False` cup. Checked by the kernel, the
`False` cup's proof says no input reaches it: the spec holds for all inputs (relative to §6.1's carve-outs).

### 6.3 Harness discipline

A harness can be wrong in the same ways as code; in particular, its own arithmetic wraps. Rules:

1. **Compute checks in a wider type.** Checks about `i32` code are computed in `i64` (`i64.extend_i32_u`/`_s` on every
   input), where products of two `i32` values cannot wrap (`(2³²−1)² < 2⁶⁴`). An `i64` program needs its checks to avoid
   products, or to compare with division (`d > n / d` instead of `d·d > n`). (A ghost unbounded integer type is
   deliberately left out of v2; §9.)
2. **One check per harness, as a predicate.** The check is a call to a pure predicate, so the same predicate can be
   a refinement on the function's result and the harness's `prove` is one step.
3. **Harness params are the quantified inputs**; refinements on them are the precondition. A harness with an
   unsatisfiable precondition is vacuous (§7.2).
4. The example runner calls each harness on a fixed input list (edge values, then a deterministic pseudo-random
   sample) and records the first input that reaches `unreachable`.

## 7. Vericoding mode

In vericoding mode the student owns the **specification** and an LLM (or the student, or a scripted session) writes
the **implementation and its proofs**. The kernel is the only judge; the LLM is never trusted, and the editor works
fully without one.

### 7.1 The ownership boundary

| owned by the student (locked while the LLM works) | owned by the LLM side |
|---|---|
| every function **header** line (types, refinements, fact params/results, exports) except lemma headers | bodies of ordinary functions |
| bodies of **predicates**, **measures** and **harnesses** | **lemma** functions, header and body |
| **axioms** (`axiom:` exports) and `assume` lines | proof lines: `prove`, `lemma`, `unfold`, fact locals |
| block-type `(fact …)` clauses written by the student (marked `;; @own`), the memory and global declarations | block-type facts and refined locals it adds |

Enforcement by the kernel, after every LLM round: (1) the student zone is hashed line by line when the session starts;
any difference rejects the whole round (`edited a locked line: 7`). (2) An LLM-side line may not contain `assume`,
define an `axiom:` export, add an import, or call a function that is not in the module at session start or defined by the
LLM as a lemma. (3) Mode is strict: every cup in every LLM-owned function (touched by the round or not) must be **proven** or
**assumed only through student-zone (instructor) axioms**, with an empty `depends_on_checks`; runtime-checked is an
error. (4) Every harness `False` cup must be proven. (5) **The program must run.** The kernel's theorem is partial
correctness (§6.1), which a body that never returns (`loop br end`, or a call to itself) satisfies for any spec. So
`$main`, every harness, and every LLM-owned function whose parameters are all value parameters is run on up to 16
inputs from its input list (§6.3) that satisfy its precondition and whose every argument is in 0..100; each run must
finish within 1,000,000 steps and call depth 150. A run that runs out is an error only if it runs out inside an
LLM-owned function (a costly student predicate is the student's business): `$isqrt(7) does not finish: $isqrt runs
past 1000000 steps or calls`. A student line made unreachable (dead) by LLM edits is a boundary violation. In short,
the submission is accepted only if every LLM-owned function is **strict-clean** and therefore VERIFIED (§4.1), and the
program runs; the editor itself stays in gradual mode, so a rejected submission still runs. The round is accepted iff
(1)–(5) hold; otherwise the kernel's diagnostics go back to the LLM.

### 7.2 Adequacy: is the spec worth proving?

A proof only says the code meets the spec. The adequacy panel checks the spec itself, without any LLM.

- **Vacuity of preconditions.** For each harness and each refined function, the kernel tries `prove k` with all
  parameter refinements as hypotheses and goal `False`. Valid ⇒ **vacuous** (every claim about this function holds
  trivially). Independently the runner looks for a **witness**: an input in the harness input list that satisfies all
  parameter refinements (by evaluation). No witness ⇒ *probably vacuous* (shown as a warning, not a verdict).
- **Vacuity of postconditions.** A result refinement is **unconstraining** if its cup can be proven at a fresh
  value: the kernel re-checks the function with the returned id replaced by a fresh leaf (havoc) and keeps the
  result-refinement cups' verdicts. Proven at a havoc value ⇒ the postcondition says nothing about the result.
- **Fact parameters and results.** Fact parameters are preconditions: witnesses must satisfy them too (evaluated on
  the run's initial memory). A fact result the kernel proves with no hypotheses at all is **unconstraining** (a
  tautology). A fact result merely implied by the preconditions (an invariant the function preserves) is not flagged.
- **Mutation testing.** The runner applies each operator below, one site at a time, to LLM-owned bodies only, keeping the
  line count and validity, and runs every harness on its input list. A mutant is **killed** if some harness reaches
  `unreachable` (or the mutant traps); otherwise it **survives**. Surviving mutants are listed by line; each survivor is
  either an equivalent mutant (the student marks it) or evidence that the spec is too weak. If the original program itself does not finish on a harness input (the step
  budget runs out), the panel says so in red: a body that never returns satisfies any spec vacuously, and no mutant
  can be told apart on that input.

| op | mutation | example |
|---|---|---|
| M1 | relational flip | `lt_u ↔ le_u`, `gt_s ↔ ge_s`, `eq ↔ ne` |
| M2 | signedness swap | `lt_u ↔ lt_s`, `div_u ↔ div_s`, `shr_u ↔ shr_s`, `extend_i32_u ↔ extend_i32_s` |
| M3 | constant off-by-one | `c → c + 1`, `c → c − 1` |
| M4 | arithmetic swap | `add ↔ sub`, `and ↔ or`, `shl ↔ shr_u` |
| M5 | operand swap | `local.get $a → local.get $b` (same type, same function) |
| M6 | condition inversion | insert or remove `i32.eqz` (an existing `i32.eqz` line becomes `nop`; a `nop` before `if`/`br_if` becomes `i32.eqz`) |

Mutation runs are dynamic (fast, needs no proofs). A mutant that the kernel still fully **proves** is a definite spec
gap and is reported first.

### 7.3 The LLM protocol

The LLM never talks to the kernel; the editor mediates. One **round**:

Request (JSON, sent to the model as one user message with the system prompt below):

```json
{ "module": "<full v2 text with line numbers>",
  "locked": [[1, 12], [40, 58]],
  "task": "make every cup in $isqrt proven and every harness False cup proven",
  "cups": [ { "line": 23, "goal": "u($r) ≤ 65535", "verdict": "runtime-checked", "diag": "nothing feeds it",
              "lane": [ { "line": 31, "fact": "$sq_le(ext_u($r), ext_u($n))" }, { "line": 36, "fact": "u($r) < 65535" } ] } ],
  "line_errors": [ [21, "not implied by [u($r) < 65535 @36, ¬gt_u(…) @50]: u($r)=65535"] ],
  "rules": "<the rule-card digest: card titles and one-line premises, ~2 KB>",
  "round": 2, "max_rounds": 6 }
```

Response (JSON only): `{ "edits": [ { "replace_lines": [a, b], "with": ["line", …] } ], "note": "…" }`. Each failing cup carries
its **lane snapshot** (the in-scope facts, top first, with birth lines), so the model can count `k` and see stale facts
instead of guessing. Edits may add or remove lines only inside LLM-owned ranges; the editor applies them, re-checks, and sends the next round until
accepted or `max_rounds`. The system prompt states the syntax of §1, the ownership table and "you cannot use assume or
axioms; failed proofs are reported with counterexamples".

**Sessions.** The default is an **offline scripted session**: a recorded transcript (`session.json`: the sequence of
requests and responses) replayed deterministically, so a classroom demo needs no network and no key. A live session is
optional: the student pastes an OpenRouter key and picks a model; the editor sends rounds to
`https://openrouter.ai/api/v1/chat/completions` from the browser and records the transcript in the same format, so
any live session can become a scripted one.

## 8. Visual mapping (for phase D)

Codillon's layout stays: fractions LEFT of each instruction at the indentation-driven x, cups above a rule, outputs
below, pale ~7 px ribbons from producer to consumer, rounded gray frame brackets (pink for loops), the step slider,
gutter glyphs, far-right darkred commentary. v2 adds:

- **Proof cups.** A proof cup is drawn in the same fraction, to the right of the value cups, as a **diamond-shaped cup**
  (value types keep rectangles/ellipses), with its goal in 8 pt condensed sans under it (`b ≠ 0`, `u(a) ≤ 65532`). A
  proof cup beside a specific operand (divisor, address, refined argument) sits immediately right of that operand's cup.
- **The fact lane** is drawn as a narrow column of **fact chips** between the fraction and the code: a chip appears on
  a fact's birth line (branch arm, `end`, `loop`, call, entry, `prove`, `lemma`), as a small diamond with the atom text on
  hover. The chip's **ribbon** runs down the lane column for as long as the fact is in scope, then ends at the frame's
  `end` (cut) or continues (join kept it).
- **Wires.** Every fed cup has an always-on wire from its feeding chip to the cup: a thin (2 px) purple curve,
  distinct from the pale value ribbons. Evaluation-fed cups show `=` inside the cup; dead-code-fed cups show a faint
  wire to the line that ended the arm.
- **Fraying.** At a `local.set $x`/`tee` that rebinds a value mentioned by a chip (R7), or a store that ends an
  epoch-carrying chip (R11), that chip's ribbon **frays** (splits into 3 diverging hairlines and fades over one line).
  A cup that fails because its only candidate fact is about the old value gets a dotted "bad" connection to the frayed
  ribbon, Codillon's existing mismatch idiom.
- **The False cup** on `unreachable`: an inverted, hatched diamond labelled `⊥`. Fed, it is calm; unfed, it is the only
  cup drawn with a darkred outline in gradual mode when a run reached it.
- **`prove k` fractions**: `k` diamond cups above the rule (wired to the hypotheses' chips), a diamond output below
  wired to the goal cup on the next instruction; hovering shows the removed wraps (`i+1 does not wrap: u(i) ≤ 7`) or the
  countermodel.
- **Gradual checks**: an unfed cup is drawn empty with Codillon's fade-up gradient, plus a small stopwatch tick to say
  "checked when run". If a run fails the check, the line gets 💣, as for any trap.

**The four states, grayscale-safe, in the v1 palette** (ivory `#fffff0` ground; purple `#6A5ACD`/`#483D8B` for types and
proof wires; darkred only for a violation; no green):

| state | cup fill | outline | wire | extra mark | in grayscale |
|---|---|---|---|---|---|
| proven | solid purple | solid | solid purple | — | solid dark fill |
| assumed | purple at 35 % with diagonal hatching | solid | dashed purple | small `A` on hover chip | hatched |
| runtime-checked | empty, fade-up gradient | dashed gray | none | stopwatch tick | empty, dashed |
| refuted | empty | **darkred**, double | — | witness in commentary, 💣 if from a run | empty, double outline |
| proven\* / assumed\* (relative to checks) | as proven / assumed | as proven / assumed | as proven / assumed, plus a dotted tail to each check | small stopwatch superscript; hover lists the check lines | as proven / assumed + superscript |

A **VERIFIED** badge (a small purple seal, not green) sits on the header line of each strict-clean function.
The four are distinguished by fill pattern (solid / hatched / empty-dashed / empty-double) as well as color, so they
survive grayscale printing and color-blind viewing.

## 9. Limits and open questions

**Limits (by design).**
- Floats are opaque (only exact-match float facts and constant evaluation); `trunc_sat` is the recommended conversion.
- `call_indirect`, tables, reference types, SIMD and multiple memories are outside v2 (cups are runtime-checked).
- No termination proofs for ordinary loops and recursion (partial correctness); predicates and lemmas are total.
- Memory reasoning is per-epoch: after a store, facts about memory-reading predicates are gone. There are no frame
  rules ("this store does not touch slot j"), so preservation of a memory representation invariant across a store is
  runtime-checked or needs an instructor axiom (the hash-table example shows both).
- Nonlinear arithmetic is only monomial atoms plus interval substitution; anything else is a lemma.
- `prove k` takes the `k` most recent lane entries; an older fact must be re-cited with a fact local.
- Call-stack exhaustion is carved out of the theorem.

**Open questions.**
1. *Re-citing.* Is `local.set $h` / `local.get $h` to reorder hypotheses tolerable for students, or should `prove`
   accept explicit chip references (e.g. `prove @14 @22`, line numbers) at the cost of edit-fragile text? The examples
   say it is fine for intro code (parity, isqrt, gcd use `prove 0`–`prove 3`) and clumsy for lemma bodies
   (primality's `$from_agrees` needs `prove 7` and three re-cited handles).
2. *Frame rules for memory.* A `stable` export convention (a predicate that reads only a declared address range,
   unaffected by stores outside it) would let the hash-table invariant survive stores. Worth the complexity?
3. *Ghost integers.* An unbounded ghost type would make harness overflow impossible; v2 uses `i64` instead. Is the
   i64 lesson (the isqrt harness bug) worth more than the convenience?
4. *Automatic `prove 0`.* Should the kernel try `prove` with zero hypotheses on every unfed cup (pure instruction
   semantics, e.g. `u(and(x,7)) ≤ 7`)? It is cheap and deterministic, but makes some feeds invisible in the text.
   v2 says no; examples write `prove 0`.
5. *Joins over branch edges.* Intersection across `br` edges needs lane snapshots per edge; measure the memory cost on
   the hash table before committing.
6. *Instructor axioms bridged to Lean.* The design allows `axiom:` facts justified outside Codillon (15 §3); the
   bridge itself is not specified here.
7. *Mutation budget.* With 6 operators the hash table yields ~150 mutants; is running all harnesses on each per edit fast
   enough in the browser, or should mutation run on demand only? (v2: on demand.)
8. *Congruence.* Opaque terms are keyed by canonical arguments, so `$p(#g)` and `$p(#h)` are unrelated even under a
   hypothesis `#g = #h`. The examples route around it by naming values in locals (gcd harness); a small congruence step
   in §3 would remove the workaround.
