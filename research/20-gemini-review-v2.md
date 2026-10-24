# 20 — External Review of Refined Codillon v2 (PL, Verification, and CS Education)

Reviewer: External reviewer (Gemini)
Scope: Design (`research/15`, `16`, `18`), internal reviews (`16-review-fable`, `17-kernel-review-fable`, `19-editor-review-fable`), examples (`research/v2-examples/`), implementation (`codillon-refined` branch `proofs`, `src/v2/*.rs`, `src/proof_view.rs`, `src/vericode_ui.rs`), and live editor rendering (`editor/v2/`).

## A. Verdict

Refined Codillon v2 is a major architectural improvement over v1: replacing an external SMT solver and a separate annotation language with a deterministic, single-pass kernel over a scoped fact lane aligns verification directly with Codillon's core pedagogy—that program semantics are visible dataflow. The four-state verdict model (`proven`, `assumed`, `runtime-checked`, `refuted`, plus check-relative `*` provenance) eliminates solver timeouts and spurious loop-head counterexamples, while line-for-line erasure preserves execution fidelity. However, our audit uncovered several **new soundness and adequacy vulnerabilities** not caught by the internal reviews: (1) a critical ghost-code soundness break where lemmas (`export "lemma:..."`) are omitted from R33/R29 totality checks (`kernel.rs:2261`, `634`), allowing a lemma with `loop $l; br $l; end` or self-`call` to prove `False` (`(fact (i32.const 0))`), erase to `nop`, and cause a terminating `VERIFIED` program to trap at runtime (falsifying Theorem §6.1); (2) a relational local-refinement soundness hole in R7/R8 where mutating a referenced local `$n` after `local.set $r` allows `join`/`loop_head` to re-instantiate `$r`'s invariant against the new `$n` without proof; (3) unverified global initializers and function-local provenance groups in R9/R14 (`kernel.rs:549–556`) that let any module derive `False` from a contradictory global refinement; (4) control-flow-blind shadow-local capture in R35 (`kernel.rs:596`, `runtime.rs:132`) that evaluates unfed cups against an uninitialized `0` shadow when a pure call appears later or in another branch; and (5) a partial-correctness bypass in vericoding where an LLM can satisfy *any* specification—passing the ownership lock, strict kernel check, vacuity check, and mutation testing with zero survivors—via `loop $l; br $l; end; unreachable` or `call $f`. With the targeted fixes in §F, v2 will be a remarkably strong, honest platform for both introductory verification and specification-driven vericoding.

## B. The Design

### B.1 Is "proofs as values in a fact lane, checked by a kernel" the right foundation?

**For an introductory CS course: yes, with one pedagogical tension.**
The central design decision of v2 (`16-v2-design.md` §1.1)—moving proofs off the Wasm operand stack (where `15-input-proofs-as-values.md` §1 initially placed them) into a scoped, persistent **fact lane** while keeping propositions as folded pure Wasm expressions—solves the two fatal flaws of both v1 and stack-carried proofs:

1. **Zero stack-order distortion and exact line-for-line erasure.** Introductory students already struggle with Wasm operand stack discipline. Requiring them to interleave proof tokens on the value stack and `local.set`/`local.get` them around binary operators would obscure the algorithm being taught. Because the fact lane is a parallel, scope-disciplined structure and every v2 proof construct (`prove k`, `lemma`, `unfold`, `assume`, `(local $h fact)`) erases 1-for-1 to `nop` or a comment (§1.8), line numbers, step-slider positions, and stack frames remain identical between verified source and erased Wasm.
2. **One language for code, specifications, and tests.** Expressing propositions as pure Wasm expressions read as `≠ 0`, loop invariants as `(fact …)` clauses on `loop` block types (R17), and functional specifications as ordinary `harness:` functions ending in `unreachable` consuming `False` (R26, §6.2) means students never learn a second logical surface syntax. A harness is simultaneously a runnable test on Codillon's step slider and a universal theorem when its `False` cup is proven.
3. **Explicit wraparound instead of mysterious solver timeouts.** Replacing Z3 with the bounded `prove k` procedure (§3: interval pre-pass + explicit `2^w·q` wrap variables + degree-≥2 monomials as atoms + Omega-lite) turns machine-dependent `unknown` states into deterministic, local feedback. Crucially, the `isqrt` overflow lesson is no longer a magic Z3 countermodel: the student sees *why* `r + 1` does not wrap (`u($r) ≤ 65534` from the refined local `u($r) ≤ 65535` and the branch guard) and why squaring requires widening to `i64`.

The main pedagogical tension is **positional hypothesis indexing in `prove k`**. Because `prove k` consumes the `k` most recent entries in the fact lane, `k` acts as a de Bruijn window over an implicit context. In small intro functions (`parity`, `isqrt`, `gcd`), `k ∈ {0, 1, 2, 3}` is manageable because the editor draws explicit wires from the `k` chips into the `prove` sockets. However, inserting a branch or helper call between a fact's birth and `prove k` shifts the lane index (`isqrt-wrong-cup.wat`), and in larger proofs (`primality.wat`'s `$from_agrees`) students must manually juggle `(local $hq fact)` handles to re-cite older facts. Allowing optional birth-line or handle names on `prove` (16 §9 Q1) would preserve determinism while removing positional fragility.

**For vericoding: yes, in architecture, provided partial-correctness loopholes are closed.**
In v1, annotations (`@invariant`, `@requires`, `@assume`) lived in a flat namespace where an LLM could trivially weaken a spec to make verification pass. In v2, separating student-owned declarations (headers, predicates, measures, harnesses, axioms) from LLM-owned implementation bodies, proof lines, and lemmas (§7.1)—backed by a deterministic kernel with no SMT nondeterminism—is the right architecture for "students write specs, LLMs write verified code."

### B.2 New soundness concerns in the design (not covered by internal reviews 16, 17, 19)

Having read `16-review-fable.md`, `17-kernel-review-fable.md`, and `19-editor-review-fable.md`, we do not repeat their findings (mutable globals in predicates, loop global φ-renaming, `br_if` edge-cup leaks, virtual `rem_u` guards, `le0` sign flip, `poly_mul` zero-coefficient hang, vacuous lemma value-params, duplicate function shadowing, and spec-only mutation kills). Beyond those, we identified **four new soundness concerns** at the design/calculus level:

1. **Relational local refinements (`(local $r (T | R))`) are unsound across mutations of other locals at R8 joins and loop heads.**
   In §1.3, a local refinement `R` is an arbitrary `sexpr` or predicate call over `v` and any in-scope locals/parameters (e.g., `(local $r (i32 | (i32.le_u v $n)))`). Rule card R7 checks `R[v := #new, $n := cur[$n]]` only at `local.set $r` (and R14 at initialization). Rule card R8 then states that whenever `$r` is φ-merged at a join or loop head, the kernel unconditionally enters `R[v := #φ_r]` instantiated with the bindings *at the join/loop head*, arguing that *"the refinement is the local's own invariant; the cups of R7 and R19/R20 make it true on every edge."*
   **Why this is unsound:** R7 only checks `R` when `$r` is written, not when another local `$n` mentioned in `R` is written! Consider:
   ```wat
   (local $n i32)
   (local $r (i32 | (i32.le_u v $n))) ;; R14 LocalInit: u(0) ≤ u(0), proven by R28 eval
   i32.const 1
   if
     i32.const 10
     local.set $n
     i32.const 10
     local.set $r                     ;; R7 cup: u(10) ≤ u(10), proven by R28 eval
     i32.const 0
     local.set $n                     ;; $n is unrefined: no cup! Now $r = 10, $n = 0
   end
   ;; At `end` (R8 join): $r differs across arms (10 vs 0) ⇒ gets #φ_r.
   ;; $n is 0 on both arms ⇒ stays const 0.
   ;; R8 instantiates R[v := #φ_r, $n := cur[$n]] = (u(#φ_r) ≤ u(0)) and enters it as PROVEN!
   ```
   After `end`, the lane holds the `Proven` fact `u(#φ_r) ≤ 0` (so `#φ_r = 0`), allowing the function to prove `False` on the `then` path or divide by `10 - $r` (0 at runtime). Either local/global refinements must be syntactically restricted in §1.3 to mention only `v` and immutable values (constants and entry parameters, via `entry_bind`), or R7/R8 must also emit a cup for `$r`'s refinement whenever any local mentioned in `$r`'s refinement is mutated or φ-merged.

2. **Global refinements (R9, R14) lack initializer obligations and cross-function check provenance.**
   The grammar (§1.3) permits refined globals `(global $g (mut (i32 | R)) (i32.const c))`. R9 specifies a cup on `global.set $g` and re-enters `R` after impure calls, and R14 enters global refinements on function entry. However, the design specifies **no cup for the global's initializer `c`**, and §4.1 specifies `depends_on_checks` as a *per-function* set ("a caller does not inherit a callee's internal checks"). Consequently:
   - Declaring `(global $g (i32 | (i32.lt_u v 0)) (i32.const 0))` enters `u($g) < 0` on entry to every function with zero cups anywhere in the module, immediately proving `False` via `prove 1`.
   - Even with a valid initializer, if function `$setter` performs a `global.set $g` whose cup is `runtime-checked` (unfed in gradual mode) and does not call `$reader`, `$reader` enters `$g`'s refinement on entry (and after any impure call, R9) as unconditionally `Proven` (`VERIFIED`), even though `$setter` can violate the global invariant at runtime.

3. **Unmeasured recursion in ordinary functions and `call` inside lemmas compromises functional specs (R13, R31, R33).**
   By R31, ordinary functions need no termination measure; by R13, `call $f` immediately enters `$f`'s postcondition into the lane. Thus, any function `$f` can satisfy arbitrarily complex postconditions (and make every harness calling `$f` `VERIFIED`) via the 1-line body `call $f` (passing its own parameters). Worse, in R33, a lemma's recursion is only checked for a measure at `lemma $f` lines ("a `call $f` in a predicate, a `lemma $f` in a lemma", R31), overlooking that a ghost lemma body can execute an ordinary `call` or a `loop` unless explicitly forbidden and checked. As shown in §C.1, the implementation fails to enforce R33's ban on loops and unmeasured calls in lemmas, turning partial correctness in ghost code into unsoundness for terminating runtime code.

4. **Lazy `ite` / unfolded predicate division traps in §1.3 and §3.2 (`defined`).**
   After kernel review B5, §1.3 adopted the rule: *"`(fact E)` asserts 'E evaluates without trapping to a nonzero i32'."* In §3.2 (`solver.rs:698–763`), non-trapping is enforced by `defined()`, which collects only **eager** top-level divisions (`Key::Op`) and deliberately skips `Key::Ite` and unfolded `Key::Call` bodies ("Unfolded bodies (`ite`) and call bodies are not eager: their own guards decide"). However, inside `tr_op` (`solver.rs:510, 539`), a virtual division by constant `0` (`div_u(x, 0)`) inside the active branch of an `ite` or unfolded predicate is translated as a deterministic `opaque(t)` leaf (not a trap!), and a virtual `div_s(INT_MIN, -1)` is not checked in hypotheses (`solver.rs:731`). Thus, a goal containing `(select (i32.eq (i32.div_u $x 0) (i32.div_u $x 0)) 0 $c)` can be proven `Valid` under `$c ≠ 0` by reflexivity of the opaque leaf, even though evaluating the fact at runtime (R28/R35) traps.

## C. The Implementation

Spot-checking `src/v2/*.rs` against rule cards R1–R35 confirmed that the core one-pass architecture, value numbering (`term.rs`), Omega-lite (`solver.rs`), and dependency closure (`kernel.rs`) are cleanly engineered. However, we found **six concrete implementation defects** with exact `file:line` locations:

1. **Ghost lemmas (`export "lemma:..."`) bypass R33 restrictions on loops, impurity, value results, and unmeasured recursion (`src/v2/kernel.rs:2261`, `634–638`, `src/v2/info.rs:90–100`) — FALSIFIES THEOREM §6.1.**
   - In `src/v2/kernel.rs:2255–2263`, `Pass::predicate_checks()` begins with:
     ```rust
     if !(i.is_pred || i.is_measure) {
         return;
     }
     ```
     Because `func.is_lemma()` is never checked here (or anywhere else for R33's structural rules), a lemma body is permitted to contain `loop`, `i32.store`, impure calls, and value results!
   - **Exploit (proving `False` in a terminating `VERIFIED` program):** Define:
     ```wat
     (func $boom (export "lemma:boom") (result (fact (i32.const 0)))
       loop $l
         br $l
       end
     )
     ```
     In `Pass::run()`, `loop $l` emits 0 cups, `br $l` emits 0 cups and calls `self.go_dead(line)` (`src/v2/kernel.rs:1066`), and at `)` the result `(fact (i32.const 0))` is fed by `Feed::DeadCode` (`Verdict::Proven`, `strict_clean = true`, `verified = true`). Alternatively, replacing `loop $l; br $l; end` with `call $boom` also proves `(fact (i32.const 0))` with zero cups because `do_call` (`src/v2/kernel.rs:634–638`) only emits a `Measure` cup when `cx.info[g].is_pred || cx.info[g].is_measure || cx.info[g].measure.is_some()`.
   - Because `src/v2/erase.rs:114, 146` erases lemma bodies and `lemma $boom` lines to `nop`, any ordinary function can write `lemma $boom; prove 1; i32.const 1; i32.const 0; i32.div_u`—which the kernel marks `VERIFIED` with zero assumptions, and which **immediately traps on division by zero at runtime**.
   - Additionally, in `src/v2/info.rs:94–100`, `Ins::Lemma(c, args)` sets `fi.self_rec = true` when `g == i`, but unlike `Ins::Call` (`src/v2/info.rs:90`) never pushes `g` onto `fi.calls`, so `mutual_rec` (`src/v2/info.rs:133–153`) is blind to `lemma` edges.

2. **Refined globals have no initializer cup and use per-function `global_groups` (`src/v2/kernel.rs:474–479`, `536–556`, `639–646`, `1011–1019`, `1110–1120`).**
   - In `Pass::entry()` (`src/v2/kernel.rs:549–556`), every global with `g.ty.refine` has its refinement entered into the lane at `hl` (`self.enter(a, hl, "global refinement", deps)`), but unlike refined locals (`src/v2/kernel.rs:514–534`, `CupKind::LocalInit`), **no cup is ever emitted to check `g.init` against `g.ty.refine`**.
   - `self.global_groups` (`src/v2/kernel.rs:474–479`) creates a fresh empty `Dep::Group(g)` per function pass. In any function that does not itself execute `global.set`, `self.groups[g]` is empty, so `closure()` (`src/v2/kernel.rs:2315–2349`) marks the global refinement `Verdict::Proven` with `depends_on_checks = []`.
   - At `src/v2/kernel.rs:550, 640, 1015, 1112`, global refinements are instantiated with `self.cur_bind()`, binding any `$x` in the global's refinement to the current function's local `$x`.

3. **Relational local refinements use mutated `cur_bind()` at `join` and `loop_head`, while `local_groups` is path-insensitive (`src/v2/kernel.rs:521, 679, 688, 1004–1008, 1089–1098`).**
   - At `src/v2/kernel.rs:1004–1008` (`join`) and `1089–1098` (`loop_head`), φ-merged refined locals re-instantiate `r.refine` with `self.cur_bind()` and `vec![Dep::Group(g)]`, enabling the soundness bug detailed in §B.2 (1).
   - Because `self.local_groups[i]` (`src/v2/kernel.rs:467–473, 688`) is a single function-wide group, an unfed `local.set $r` at the bottom of a function adds its `Dep::Cup` to `groups[g]` and causes `closure()` at `finish()` to mark `prove`s inside an earlier, upstream loop as `depends_on_checks` (`Proven*`).

4. **R35 runtime-check instrumentation (`RuntimePlan`) has three capture/evaluation bugs (`src/v2/kernel.rs:593–609, 1071–1073` and `src/v2/runtime.rs:82–99, 132–179, 265–305`).**
   - **Unreached or later `Key::Call` / `Key::Load` shadow locals read as `0`:** `Pass::push` (`src/v2/kernel.rs:596–605`) records a `Birth { term: t, line: self.line, how: Capture::Top }` for every `Key::Call(..)` and `Key::Load(..)` instruction. `RuntimePlan::new` (`src/v2/runtime.rs:132`) puts all such `t` across the entire function into `born: HashSet<TermId>`, and `walk()` (`src/v2/runtime.rs:91–94`) stops at any `t ∈ born` without recursing into `t`'s arguments. If an unfed cup at line 15 checks `(call $p $x)` (or `¬(call $p $x)`) and the body later executes `local.get $x; call $p` at line 40 (or in an untaken `if` arm), both share canonical `TermId` `t`. When the check at line 15 runs, the shadow local captured at line 40 has not been written yet and holds `0`, so `Evaluator::term` (`src/v2/runtime.rs:266`) returns `0` instead of calling `$p($x)`!
   - **Loop parameter `#φ` leaves are never added to `births` (`src/v2/kernel.rs:1071–1073`):** `loop_head` pushes `#φ` leaves for `bt.params` without calling `self.birth(...)` (and `join` at `src/v2/kernel.rs:985` only captures `Capture::Top` when `nres == 1`). Any runtime check referencing a loop parameter hits `_ => Err("value of #φ was not captured")` in `Evaluator::term` (`src/v2/runtime.rs:300`), returning `CheckOutcome::Unknown`, which `src/v2/eval.rs:248` and `src/debug.rs` silently treat as passing.
   - **R27 float conversion cups are never checked at runtime (`src/v2/runtime.rs:269–303`) and `f32` bounds round wrongly (`src/v2/kernel.rs:568–577, 851–854`):** `Ins::Float` conversion cups (`iNN.trunc_fMM_s/u`) wrap `Key::Float("fMM.gt" / "fMM.lt", ...)` (`src/v2/kernel.rs:861–877`), which `Evaluator::term` (`src/v2/runtime.rs:269–303`) does not implement, returning `CheckOutcome::Unknown` on every run. And `trunc_bounds` (`src/v2/kernel.rs:572, 574`) casts `-2147483649.0f64 as f32` (`-2147483648.0f32`) and `-9223372036854777856.0f64 as f32` (`-9223372036854775808.0f32`), excluding valid `i32::MIN`/`i64::MIN` values in `f32`.

5. **`Solver::defined` skips `DivS` overflow on hypotheses and `Solver::omega` uses unchecked `i128` arithmetic in back-substitution (`src/v2/solver.rs:730–734, 1003, 1018`).**
   - At `src/v2/solver.rs:730–734`, `if hyp { self.le(&Lin::konst(1), &b.lin)?; continue; }` skips the `op == IOp::DivS` `INT_MIN / -1` check at lines 744–760, contradicting the doc comment at line 700.
   - At `src/v2/solver.rs:1003` and `1018`, back-substitution uses raw `rest += c * val...` instead of `mul`/`add`, risking overflow panics on 64-bit monomial bounds.

6. **`pre_holds` ignores `(param $h (fact E))` and `vacuity` ignores `(result (fact E))` (`src/v2/adequacy.rs:148–163, 247–271`).**
   - `pre_holds` (`src/v2/adequacy.rs:148–163`) checks only `func.value_params()`, ignoring `Decl::Fact` parameters when finding witnesses (`witnesses()`, `Bench::new()`).
   - `vacuity_inner` (`src/v2/adequacy.rs:247–271`) checks only `func.value_results()`, ignoring `(result (fact E))` postconditions (such as `$remove` and `$insert` in `hashtable.wat`).

## D. The Editor

### D.1 What is legible and honest for a freshman

Rendering all 13 examples, failure steps, and vericoding sessions in headless Chromium confirms that the visual mapping (`src/proof_view.rs`) succeeds on its core promise:

- **Calm when proven, loud only on a violation:** In `parity.png`, `isqrt-full.png`, and `gcd-bottom.png`, proven cups sit unobtrusively to the right of value cups as solid purple diamonds (`#6A5ACD`) fed by 2 px purple curves from fact chips in the 28 px lane. Darkred is reserved strictly for refuted cups (broken double-rimmed diamonds + 💣 + darkred opcode text) and failed `prove`/`strict` diagnostics (`parity-bug-gate.png` lines 46, 49; `gcd-bug-guard-bottom.png` lines 125, 132).
- **Fraying ribbons teach value-vs-variable staleness visually (`hashtable-stale-bottom.png` lines 314–324):** When `local.set $i` at line 318 increments `$i`, the fact chip born at `br_if $c` (line 314, `u($i) < u(8)`) frays into five darkred hairlines at line 318, and a dotted darkred mismatch curve links the fray directly to the refuted `i32.store` bounds cup at line 324. A freshman sees both the symptom and the cause at a glance.
- **Honest check-relative (`*`) and axiom badges:** Downstream proofs resting on a `runtime-checked` cup carry an indigo `*` (`parity-bug-gate.png` line 51, `isqrt-wrong-cup-full.png` line 39, `gcd-bug-guard-bottom.png` line 139) and demote the function's header badge from `♦ VERIFIED` to a dashed `N runtime checks` / `gradual` pill. Functions resting on instructor axioms display `♦ VERIFIED · 1 axiom` (`gcd-bottom.png` line 140) or `♦ VERIFIED · 3 axioms` (`primality-mid.png` line 118).

### D.2 Which states confuse a freshman (with screenshot citations)

1. **Pinned badges and rejection boxes collide with and obscure the specification text on wide lines (`parity.png` line 40, `parity-missing-proof.png` line 40, `isqrt-full.png` line 30, `gcd-bottom.png` lines 104–109, `primality-mid.png` lines 95, 112–118, `session-isqrt-turn2.png` line 30).**
   Because almost every refined function header is wider than the 1400 px viewport, `.wide-line` pins the header badge or note to the right edge of the window **directly over the code text**. In `parity.png` line 40, `♦ VERIFIED` sits on top of `(result (i32 | $hon_ok $x))`; in `gcd-bottom.png` line 109, `♦ VERIFIED` covers `(i32.eq (call ...))`; and in `session-isqrt-turn2.png` line 30, the red rejection banner `submission rejected: edited locked line 30 (was '(func $isqrt ...` completely covers the refined return type that the LLM tried to delete.
2. **The vericoding panel overlays the right 400 px of the code with no scroll margin (`gcd-vericode.png` lines 6, 19, 33; `gcd-vacuous-vericode.png` lines 1, 7, 20, 34).**
   `.vc-panel` is `position: fixed; width: 399px; right: 0`, and enabling `body.vc-on` adds no `padding-right` to the document column. As a result, every refined header and block `(fact …)` clause runs underneath the vericoding panel—hiding the exact student-owned specification text that vericoding mode is meant to inspect.
3. **Positional `prove k` "goal stealing" looks like the wrong `prove` failed (`isqrt-wrong-cup-full.png` lines 57–60).**
   In `isqrt-wrong-cup-full.png`, swapping `local.set $r` and `prove 2` leaves `local.set $r` at line 57 unfed (a quiet gray stopwatch, whose icon collides with the 5 fray hairlines of `$r` at the same coordinates), while `prove 2` at line 58 **steals the loop back-edge cup of `br $grow` (line 60) and succeeds in solid purple**, leaving `prove 3` at line 59 with no sockets and the red error `prove has nothing to feed`. A freshman looking at lines 58–59 will think `prove 3` is redundant and `prove 2` is working, when in fact `prove 2` was meant to feed line 57 above it.
4. **Spec overflow bugs tell the student to "add a lemma" (`isqrt-harness-bug-bottom.png` line 91), and vacuous/weak specs look 100% green outside vericoding mode (`gcd-vacuous.png`, `hashtable-bug-tombstone.png`).**
   In `isqrt-harness-bug-bottom.png` line 91, the student's `i32` predicate `$is_isqrt32` wraps on `(r+1)*(r+1)`. Because `$main` only runs `isqrt_harness(17)`, the dynamic run passes, and `prove 2` at line 91 reports: `prove failed: could not decide (inexact step on wrap(mul($isqrt($n), $isqrt($n)))); add a lemma`. Telling a freshman to "add a lemma" when their specification is *false* at `$n = -1` sends them on a wild goose chase; running the small edge-value witness sweep (`EDGES` includes `-1`) on harness failures would immediately refute line 92 with `$n = -1` instead. Likewise, `gcd-vacuous.png` and `hashtable-bug-tombstone.png` show `♦ VERIFIED` on every function in normal mode with no hint that the harness precondition is unsatisfiable until the user opens `vericode` (`gcd-vacuous-vericode.png`).
5. **Pinned diagnostic truncation cuts off the stale-fact line number (`hashtable-stale-bottom.png` line 324, `gcd-bug-guard-bottom.png` line 132).**
   Ellipsizing `.wide-line` notes at `min(46vw, 640px)` cuts off `hashtable-stale-bottom.png` line 324 at `... ⟨u($i) < u(8)⟩ (line 314) is about the ol...`, dropping `"old $i (set at line 318)"`—the most actionable piece of information in the message.

## E. Vericoding

### E.1 Is the ownership boundary and adequacy a sound basis for "students write specs an LLM must satisfy"?

**Conceptually, yes; as currently implemented, it has five exploitable loopholes.**
Pairing a content-and-context-anchored ownership lock (`SessionStart::zone_violation` and `forbidden` in `src/v2/vericode.rs`) with two-sided adequacy checking (`vacuity` + spec-only mutation testing in `src/v2/adequacy.rs`) is the right pedagogical design: the kernel prevents the LLM from weakening the student's spec or assuming unproven facts, while vacuity and mutation testing teach the student when *their spec* is contradictory (`gcd-vacuous-vericode.png`) or under-constrained (`hashtable-bug-tombstone`).

### E.2 What an adversarial LLM would try next (five concrete bypasses)

If an adversarial or reward-hacking LLM is tasked with making a submission accepted (`judge().accepted == true`) with zero surviving mutants in the adequacy panel, it can currently succeed without implementing the algorithm in five ways:

1. **The Unannotated Infinite Loop (`loop $l; br $l; end; unreachable`) or Circular Self-Call (`call $f`) — passes `judge()` AND reports 0 surviving mutants.**
   Because v2 proves partial correctness for ordinary functions, an LLM can replace the body of any target function `$f` (`$isqrt`, `$gcd`, `$half_or_neg1`, `$find`, `$insert`, `$remove`) with:
   ```wat
   loop $spin
     br $spin
   end
   unreachable
   ```
   (or push `$f`'s entry parameters and `call $f`).
   - **Why `SessionStart::judge()` accepts it:** `loop $spin` declares no `(fact …)` (0 `LoopEntry` cups); `br $spin` owes 0 `BackEdge` cups and enters dead code (R22); at `)` every postcondition cup is fed by `Feed::DeadCode` (`Verdict::Proven`, `verified = true`). The student's harness calls `$f`, receives `$f`'s postcondition by R13, proves its `False` cup, and inherits `verified = true`. `judge()` returns **`accepted: $f verified`**!
   - **Why `adequacy` reports 0 surviving mutants:** `mutants()` (`src/v2/adequacy.rs:344`) generates **0 mutants** for `loop $spin; br $spin; end; unreachable` (none of those instructions match M1–M6). Even if the LLM includes arithmetic inside the loop, `Bench::new` (`src/v2/adequacy.rs:424`) silently filters out every harness input where the base program exceeds 100,000 steps (`if r.is_ok() && it.steps <= 100_000`), and any mutant that diverges is classified as `Fate::RunsAway`, which `Fate::survives()` (`src/v2/adequacy.rs:381`) counts as **not surviving** (`false`)!

2. **The Ghost `lemma:boom` Ex-Falso Bomb (exploiting §C.1 in `src/v2/kernel.rs:2261`).**
   Because `vericode.rs:97, 271, 307` allows the LLM to define new `lemma:` functions and `kernel.rs:2261` omits lemmas from `predicate_checks()`, the LLM can add `(func $boom (export "lemma:boom") (result (fact (i32.const 0))) loop $l; br $l; end)` and insert `lemma $boom; prove 1` before every cup. Unlike Attack 1, the erased binary **terminates immediately** (`lemma` erases to `nop`). To also defeat mutation testing, the LLM only needs to hardcode or pass the deterministic 16–48 inputs generated by `input_list()` (`src/v2/adequacy.rs:19, 91`, which uses the fixed seed `0x9e37_79b9_7f4a_7c15 ^ (f as u64)`).

3. **Leaving uncalled target functions untouched (`src/v2/vericode.rs:360–369, 407–481`).**
   `SessionStart::judge()` checks `strict_reasons(&m, &out, &touched)`, which inspects **only** functions in `touched` and functions with `export "harness:..."` (`src/v2/vericode.rs:407–481`). In `public/examples/v2/sessions/parity.json`, the start state has two unproven functions (`$half` and `$half_or_neg1`), and the harness `$parity_ok` calls only `$half_or_neg1`. If the LLM computes `x >> 1` inline inside `$half_or_neg1` and **never edits `$half`**, `touched` is `["$half_or_neg1"]`, and `judge()` returns **`accepted: $half_or_neg1 verified`** while `$half` remains `i32.const 0` (`1 runtime check`, `verified = false`)! Even worse, on a module whose spec is stated via refined function headers with no `harness:` export, an LLM returning `"edits": []` gets `accepted: nothing changed; all verified` while every function in the module is unproven.

4. **Dead-code bypassing of student `;; @own` block invariants (`src/v2/vericode.rs:129–171`).**
   `contexts()` (`src/v2/vericode.rs:129–171`) anchors each student-owned line by its enclosing function and `block`/`loop`/`if` label stack, preventing the LLM from moving a `;; @own` line to another block. However, `contexts()` does not check reachability: the LLM can compute its return value and emit `return` (or `br`) on the line *immediately before* a student's `loop $grow (fact ...) ;; @own` inside the same block. The locked `;; @own` line keeps its exact text and block context (`zone_violation` is `None`), while sitting in dead code (R22) where all its cups are discharged by `Feed::DeadCode`.

5. **Hijacking exported student predicates (`src/v2/vericode.rs:21–35`).**
   In `student_bodies()` (`src/v2/vericode.rs:33`), a predicate or measure is student-owned only if `!plain_export(f)`—a heuristic added for `$prime` in `primality.wat`. If a student exports a specification predicate (e.g., `(export "is_sorted")`) to test it from the runner, `plain_export(f)` is `true`, so `classify()` makes the predicate body `Owner::Llm` and lets the LLM rewrite the predicate to `i32.const 1`.

## F. Prioritized Fixes

1. **Ghost lemmas (`export "lemma:..."`) are skipped by `Pass::predicate_checks` (`src/v2/kernel.rs:2261`) and `do_call` (`kernel.rs:634`), allowing a lemma with `loop $l; br $l; end` or self-`call` to prove `False` (`(fact (i32.const 0))`) and erase to `nop`.**
   Extend `predicate_checks` (`kernel.rs:2261`) and `info::analyze` (`info.rs:94`) to enforce R33 on every `func.is_lemma()` (no loops, no stores/impure ops, no value results, `Ins::Lemma` edges added to `fi.calls`, and `measure:` required for any self- or mutual recursion).

2. **A relational local refinement `(local $r (T | R))` that mentions another mutable local `$n` is unsoundly re-entered at `join` and `loop_head` (`src/v2/kernel.rs:1004, 1089`) with the new binding of `$n` even when `$n` was mutated after `local.set $r`.**
   Restrict local and global refinement expressions in R7/R8/R14 (`kernel.rs:521, 679, 1004, 1089`) to mention only `v`, constants, and immutable entry parameters (`entry_bind()`), or emit a refinement cup for `$r` whenever any local referenced in `$r`'s refinement is mutated or φ-merged.

3. **Refined globals `(global $g (T | R) (i32.const c))` have no initializer cup and use per-function `global_groups` (`src/v2/kernel.rs:474, 549–556`), allowing any function to derive `False` from a contradictory global refinement.**
   Check each refined global's initializer `g.init` against its refinement with empty local bindings at module check time, and propagate any ` runtime-checked` or `assumed` `global.set` cup across all functions in `check_module`.

4. **In `src/v2/kernel.rs:596` and `src/v2/runtime.rs:91, 132`, `Pass::push` records `Birth` captures for pure `Key::Call` and `Key::Load` terms and `RuntimePlan::new` treats them as globally `born`, causing earlier or sibling-branch runtime checks to read uninitialized `0` shadow locals.**
   Record `Birth` captures in `Pass::push` only for opaque leaves (`Key::Leaf`, `Key::Float`, and loads from older epochs), or restrict `born` in `RuntimePlan::new` to captures that strictly dominate the check's line.

5. **An adversarial LLM can pass `SessionStart::judge` (`src/v2/vericode.rs:344`) and get 0 surviving mutants in `adequacy.rs` on any specification by emitting `loop $spin; br $spin; end; unreachable` or a direct self-call `call $f`.**
   Require in `SessionStart::judge` (`vericode.rs:344`) and `Bench::new` (`adequacy.rs:424`) that `$main` and every harness succeed within the step budget on their witness inputs without `EvalErr::Budget` or `Feed::DeadCode` on function exit cups.

6. **`SessionStart::judge` (`src/v2/vericode.rs:362, 407`) checks `strict_reasons` only on `touched` functions and `harness:` exports, allowing an LLM to leave other unproven target functions (such as `$half` in `parity.json`) untouched and still be `accepted`.**
   Check `strict_reasons` (`vericode.rs:407`) on all non-student-owned functions in the module (Every function whose body is `Owner::Llm`), not solely on `touched`.

7. **An LLM can bypass a student's locked `;; @own` block invariant inside an LLM-owned body by inserting `return` or `br` on the line above it (`src/v2/vericode.rs:129`), leaving the locked line in dead code where `Feed::DeadCode` proves its cups.**
   Reject in `SessionStart::judge` any student-owned (`Owner::Student`) line whose cups are fed by `Feed::DeadCode` when they were not dead at session start.

8. **Loop parameter `#φ` leaves (`src/v2/kernel.rs:1071`) and `Key::Float` conversion comparisons (`src/v2/runtime.rs:269`) are not captured or evaluated in `RuntimePlan`, causing gradual-mode checks on loop parameters and `iNN.trunc_fMM_s/u` to return `CheckOutcome::Unknown` and silently pass.**
   Emit `Birth` captures for loop parameters at loop entry/back-edges, implement `Key::Float` comparisons in `runtime::Evaluator::term`, and fix `trunc_bounds` (`kernel.rs:568`) to use exact per-source-width `f32`/`f64` bounds.

9. **`pre_holds` (`src/v2/adequacy.rs:148`) ignores `(param $h (fact E))` preconditions and `vacuity_inner` (`adequacy.rs:247`) ignores `(result (fact E))` postconditions.**
   Evaluate `Decl::Fact` parameter clauses in `pre_holds` and include `Decl::Fact` result clauses in the havoc postcondition check of `vacuity_inner`.

10. **Pinned `.wide-line` badges/notes and the fixed `.vc-panel` overlay and occlude the right side of refined function headers (`parity.png` line 40, `session-isqrt-turn2.png` line 30, `gcd-vericode.png` lines 6–33).**
    Add `padding-right: 400px` to the document container when `body.vc-on` is active, place `.wide-line` badges/notes after the line text (or wrap them onto a sub-row) instead of overlaying the code, and print the stale-fact hint before the goal formula so ellipsis never clips the line number.
