# Prior art: visualizing specifications, refinement types, obligations, invariants and counterexamples in a program editor

*Research memo for a future Codillon in which types carry predicates (e.g. "i32 that is even"),
loops carry invariants, and memory carries representation invariants, and the editor has to make
spec-adherence bugs visually obvious. Read with `00-codillon-today.md`.*

## 0. Framing: what changes when types carry predicates

Today Codillon's validity checks are **decidable, local and total**. Every line either parses or
doesn't, and either type-checks or doesn't. The editor can always paint a verdict, and the verdict
is exact. A predicate-carrying type system breaks all three properties:

- **Decidability.** Whether `(i32.add x x)` is "even" is an SMT-style question. The answer can come
  back *proved*, *refuted with a witness*, *unknown* or *timeout*.
- **Locality.** A loop invariant that fails on line 14 often fails *because of* a missing fact on line 3.
- **Two kinds of truth.** Codillon already runs every program on every keystroke. Every predicate
  therefore has a second, empirical verdict: "held on every step of this run." That is not the same as "holds."

Almost every tool surveyed below runs into one or more of these problems. The useful lesson is
less any single widget than **how each tool represents epistemic state** (proved, refuted, observed,
unknown, stale), how it **localizes** a failure, and how it **produces a concrete picture** of the
failure.

---

## 1. Survey

### 1.1 Proof-assistant IDEs

**Lean 4 infoview and ProofWidgets.** Lean checks the whole buffer continuously, like Isabelle/PIDE.
A side "infoview" shows the goal state at the text cursor: hypotheses above a turnstile, the goal
below. Between successive tactic states, subexpressions are **diff-highlighted green (just added)
or red (about to be removed)**. Users can **pin** several source locations so their goal states
update live while editing elsewhere. Every displayed subexpression is a *presentation* that holds a
reference to its term, so hovering or clicking any part of a goal or error lazily fetches that part's
type or definition. ProofWidgets lets library authors register custom React renderers ("Expr
presenters"). The ITP 2023 paper shows two relevant ones. Shift-clicking two red-black-tree terms in
a goal renders both as trees, and you can see at a glance that they cannot be equal, "so an
invariant must have been violated". `withVennDisplay` renders the selected subset hypotheses as a
**Penrose-laid-out Venn diagram**.
([Nawrocki, Ayers, Ebner, ITP 2023](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2023.24);
[Lean widget docs](https://lean-lang.org/documentation/widgets/))
*Codillon lesson:* a predicate should be an **object you can select and re-present**. The same fact
can be shown as text, number-line or region. Selection, not a global mode switch, chooses the picture.

**Paperproof (Lean 4).** Paperproof redraws a tactic proof as nested boxes. **Hypotheses are green
nodes read top-down, goals are red nodes read bottom-up**, and tactics are transparent dashed boxes
between them. Opaque nodes mark what is in scope at the cursor. Darker boxes are variable scopes
you can click to zoom into. ([github.com/Paper-Proof/paperproof](https://github.com/Paper-Proof/paperproof))
*Codillon lesson:* "facts I have" vs. "facts I owe" is a strong two-color split. It maps onto
Codillon's existing **solid outputs (have)** vs. **open cups (owe)**.

**Isabelle/jEdit (PIDE).** Prover output is attached to source positions as colors, squiggles,
gutter icons (highest priority wins: error > warning > info), and a scaled **"text overview
column"** of small status rectangles on the right edge. Clicking the column jumps to the line.
Unprocessed and running text is tinted. A Theories panel summarizes each file with colored
rectangles; a thick border means finished or failed. Checking follows the **visible perspective**:
the prover prioritizes what the user is looking at.
([Isabelle/jEdit manual](https://isabelle.in.tum.de/doc/jedit.pdf))
*Codillon lesson:* when obligations are expensive, **check what's on screen first** and show
"not yet checked" as its own neutral state. Never show it as green.

**Agda.** Holes (`?`, `{! !}`) become numbered goals. Commands work *inside* a hole: give,
refine (insert the unique fitting constructor with new sub-holes) and **case-split** on a variable.
Problems are shown as **background tints, one color per checker**: yellow for unsolved metas or
constraints, light salmon for termination, wheat for coverage, peru for positivity, orange for a
missing definition, grey for dead code, and so on.
([Agda Emacs mode](https://agda.readthedocs.io/en/latest/tools/emacs-mode.html))
*Codillon lesson:* typed holes make "what is owed here" concrete. The nine-color legend is also a
**warning about color overload**: most users can't recall it.

**Idris 2.** Idris follows the same type-driven style as Agda: `?hole` names, add-clause,
case-split, proof search and make-lemma, all as editor actions. The type of each hole, with its
local context, is the main feedback channel.
([Idris 2 interactive editing](https://idris2.readthedocs.io/en/latest/tutorial/interactive.html))
*Codillon lesson:* an editor action that **splits an obligation into cases** (e.g. "x even / x odd")
gives a student something to do when a predicate fails.

**F\* (VS Code assistant).** The gutter carries a status lane: an **hourglass** for lines being
checked, "…" for lines scheduled, a **green dashed line** for fully verified, and a **blue dashed
line** for *light-checked only* (well-formed but not proved). The README warns that results after
admitted lines should be treated with suspicion. Hovering a tactic line shows the last dumped
proof state. ([fstar-vscode-assistant](https://github.com/FStarLang/fstar-vscode-assistant))
*Codillon lesson:* "type-checks" and "spec proved" are **different strengths of green**, and the
gutter must keep them apart.

### 1.2 Auto-active verifiers

**Dafny (VS Code).** Dafny has the most developed gutter vocabulary of any verifier IDE:
- A faint squiggly green line on methods awaiting verification. It becomes a **thin green bar**
  once verified, and an **animated firmer squiggle** while being verified.
- A failing method gets **two yellow vertical rails** marking the *error context*. Inside them,
  each line with a failing assertion gets a **red rectangle**, and each line whose assertions all
  pass gets a **green disk with a white check** ("can be used to check progress in a proof search").
- As soon as a line is edited, its icons turn **transparent and squiggly ("obsolete")**. Red error
  rectangles shrink to half width to show they may be stale. A method that used to verify shows a
  firm green squiggle rather than yellow rails while it is re-checked.
- Parse errors grey everything out and put a red triangle at the error.
- Hovering a definition shows per-assertion-batch statistics. `{:isolate_assertions}` splits a
  definition's obligations so each can fail or time out independently.
- Counterexamples (`--extract-counterexample`) come back as **assumptions you could paste into the
  code**. The manual says outright that Dafny "cannot guarantee that the counterexample it reports
  provably violates the assertion".

([Dafny ref §14.2 Gutter highlights](https://dafny.org/latest/DafnyRef/DafnyRef#sec-gutter-highlights);
[§13.7 verification debugging](https://dafny.org/latest/DafnyRef/DafnyRef#sec-verification-debugging))
*Codillon lesson:* copy the **error-context rails plus per-line verdicts** and the **visible
staleness**. Codillon's 0.25 s tweening is a natural way to animate "obsolete → re-checked."

**Dafny IDE (Visual Studio era) and the Boogie Verification Debugger.** Margins showed **dark
orange for edited-not-yet-sent and violet for being-verified**, answering "is the verifier done
yet?" A failure put a red dot on the return path. Clicking it laid **blue dots** along the control
path to the error. Each blue dot is a program state; selecting one fills a debugger-like pane with
**Value and Previous columns**. Underspecified solver values appear as `'7`-style placeholders, and
irrelevant variables are omitted.
([Leino & Wüstholz 2014](https://arxiv.org/abs/1404.6602);
[Le Goues, Leino, Moskal, SEFM 2011](https://www.microsoft.com/en-us/research/?p=342725))
Christakis, Leino, Müller and Wüstholz (TACAS 2016) went further. They combined the verifier with
dynamic symbolic execution, so a reported failure can be **confirmed by a concrete failing test**,
which tells genuine errors apart from spurious ones.
([MSR page](https://www.microsoft.com/en-us/research/publication/integrated-environment-diagnosing-verification-errors/))
(The "verification debugging" line is due to Le Goues/Leino/Moskal and Christakis et al. The
Fähndrich work that is related is Clousot; see below.)
*Codillon lesson:* a static counterexample should look like a **path of states you can scrub**,
the same as the runtime slider. Because Codillon can execute, it can **confirm** a witness by
running it, a step most verifiers have to bolt on.

**Clousot / Code Contracts (Fähndrich & Logozzo).** Clousot is an abstract-interpretation-based
contract checker inside Visual Studio. Warnings appear as squiggles, and the checker **proposes the
missing precondition** as a code fix ("suggested precondition: …"), inferred from the failing
assertion. ([Static contract checking with abstract interpretation](https://www.microsoft.com/en-us/research/publication/static-contract-checking-with-abstract-interpretation/))
*Codillon lesson:* when a refinement fails, offer the **weakest fix**, e.g. "require the input to
be even", as a one-click spec edit.

**Why3 IDE.** Why3 shows a **session tree** of file → theory → goal → transformation → prover
attempt. Status icons are a green check (proved), `?` (unproved) and *obsolete* (the proof no
longer matches the edited goal). **Split VC** on a conjunctive goal creates child subgoals that
pass or fail independently. Selecting a goal shows its "task" (premises plus goal) and highlights
the corresponding source. Counterexamples can be **interleaved with the source**, value by value.
([Why3 getting started](https://www.why3.org/doc/starting.html);
[gmain.ml counterexample display](https://gitlab.inria.fr/why3/why3/-/blob/d92706f798a7bd6185dab98cbf8e8d4392ac5d9d/src/ide/gmain.ml))
*Codillon lesson:* a compound predicate (`even ∧ < 100`) should **split into separately-colored
conjuncts**, so the student sees *which* clause failed.

**SPARK / GNATprove (GNAT Studio).** Each unproved check gets a magnifier icon. Clicking it draws
**the path on which proof failed inside the editor**, and where possible a **counterexample trace
with variable values at each program point** along that path. The underlying research is
Hauzar et al., which notes how hard it is to map SMT models back through the VC transformations.
([SPARK UG: investigating unproved checks](https://docs.adacore.com/R/docs/gnat-25.1/spark2014/html/spark2014_ug/en/source/how_to_investigate_unproved_checks.html);
[Counterexamples from proof failures in SPARK](https://hal.archives-ouvertes.fr/hal-01314885))
*Codillon lesson:* Codillon already writes one value per shape per line. A counterexample trace
can **reuse the slot-value rendering**, styled as "hypothetical."

**Frama-C (GUI, WP, Eva).** Each ACSL property gets a **status bullet**: green when some plug-in
proved it, yellow/orange when tried but unknown, red when invalid. There are also distinct
statuses for *valid under hypotheses* and *inconsistent* (two analyses disagree). The Eva
value-analysis panel shows per-expression abstract values. Integers are printed as an **interval
plus congruence**, e.g. `[0..100],0%2` meaning "even, between 0 and 100". This is the exact
"i32 that is even" abstraction. Values can be shown per call stack.
([Frama-C GUI](https://frama-c.com/html/gui.html);
[Eva GUI module](https://ocaml.org/p/frama-c/30.0/frama-c-eva.gui/Eva_gui/index.html))
*Codillon lesson:* intervals with congruences are an **existing, well-understood abstract domain**
that a picture can be built on directly. "Valid under hypotheses" is a status worth drawing.

**Viper IDE and Lizard.** The Viper VS Code IDE can step through **all states of symbolic
execution** and compare states visually. Lizard turns failed assertions, postconditions and
invariants into counterexamples **displayed next to the program**, aimed at heap-manipulating code
with quantified permissions.
([Viper IDE thesis](https://www.research-collection.ethz.ch/server/api/core/bitstreams/b82ae18c-66a9-410c-94c6-85c92944a9e4/content);
[viperproject/lizard](https://github.com/viperproject/lizard))
*Codillon lesson:* for memory specs, a **heap picture beside the code** beats a list of solver
values.

**Prusti, Creusot, Verus (Rust).** These tools mostly reuse rustc-style diagnostics, which are
multi-span: one span at the failing call or return, and a labeled secondary span at the clause
that failed. Verus labels a call site "precondition not satisfied" and the `requires` clause
"failed precondition". Creusot hands its obligations to the Why3 IDE.
Whiley added the same secondary location to say *which* postcondition clause failed.
([Verus guide](https://verus-lang.github.io/verus/guide/requires_ensures.html);
[Creusot](https://github.com/creusot-rs/creusot);
[Whiley 0.3.31](https://whiley.org/2014/10/09/whiley-v0.3.31-released/))
*Codillon lesson:* a spec failure always involves **two places**: where the promise is made and
where it is broken. Draw a connection between them, in the same idiom as Codillon's dataflow curves.

**KeY Symbolic Execution Debugger.** KeY draws a **symbolic execution tree**. Each node carries
its path condition and call stack, and the debugger can "**visualize all possible memory layouts**"
(aliasing configurations) of a node.
([SED](https://formal.kastel.kit.edu/~key/eclipse/SED/))
*Codillon lesson:* a symbolic heap is a **set of concrete pictures**. Show a few representative
ones instead of a formula.

**Liquid Haskell.** Errors read *"Liquid Type Mismatch. Inferred type `{v:Int | v == x-1}` is not
a subtype of Required type `{v:Int | v >= 0}` in context `x : {v:Int | v >= 0}`"*. This gives
the student a three-part structure: what you have, what's needed, and the facts in scope. Liquid
Haskell can also emit **HTML source with inferred refinement types on mouse-over** for every
binder. GuiLT (gradual liquid inference) addresses error localization by **enumerating candidate
refinements** that would make a program check.
([LH docs](https://ucsd-progsys.github.io/liquidhaskell/);
[UX.Annotate](https://hackage-origin.haskell.org/package/liquidhaskell-0.8.10.1/docs/Language-Haskell-Liquid-UX-Annotate.html);
[GuiLT, OOPSLA 2018](https://arxiv.org/abs/1807.02132))
*Codillon lesson:* "have ⊄ need" is a **subset question**, so it should be drawn as one: the
producer's region spilling outside the consumer's cup.

### 1.3 Live programming, holes and program-state visualization

**Hazel.** Every editor state is well-typed and *runnable*. Holes are inserted automatically.
Evaluation **proceeds around holes**, recording a closure for each one, so you can see the
environment that would flow into the hole while you decide what to write. The marked lambda calculus
(POPL 2024 Distinguished Paper) puts *every* type error inside a **non-empty hole** so the rest of
the program keeps typing and running. **Livelits** fill typed holes with live GUIs (color pickers,
sliders, tables) that are typed, compositional, and given live closure values.
([Omar et al. POPL 2019](https://arxiv.org/abs/1805.00155);
[Zhao et al. POPL 2024](https://popl24.sigplan.org/details/POPL-2024-popl-research-papers/70/Total-Type-Error-Localization-and-Recovery-with-Holes);
[Livelits, PLDI 2021](https://pldi21.sigplan.org/details/pldi-2021-papers/34/Filling-Typed-Holes-with-Live-GUIs))
*Codillon lesson:* a failed predicate shouldn't stop execution or the picture. Treat it as a
**marked boundary** and keep running. A livelit-style **spec widget** (drag interval endpoints,
pick a modulus) could author the predicate directly.

**Bret Victor, *Learnable Programming* and *Inventing on Principle*.** *Learnable Programming*
proposes **timelines** in which each executed line leaves a dot that is then replaced with the
value it produced, iterations side by side. Hovering a row isolates one line's values over time.
A **frame slider** chunks time coarser than a line, and **overlaying all frames** shows a whole
trajectory at once. Zooming out switches "from a table to a plot." *Inventing on Principle*'s
binary-search demo shows variable values beside each line *as the code is typed*, so an off-by-one
is visible immediately.
([Learnable Programming](https://worrydream.com/LearnableProgramming/);
[Inventing on Principle transcript](https://jamesclear.com/great-speeches/inventing-on-principle-by-bret-victor))
*Codillon lesson:* an invariant is a **property of the whole timeline**. Draw it across iterations
(overlay or table → plot), not only at the current step.

**Projection Boxes (Lerner, CHI 2020).** Each line gets an always-on box of runtime values per
iteration. The user **projects** (filters rows and columns) to reconfigure the view. Users were
not distracted by always-on display, but their preferences differed widely. Follow-up work found
the **"loop datavoid"** problem: incomplete loops produce no useful live data.
([Projection Boxes](https://cseweb.ucsd.edu/~lerner/pb/))
*Codillon lesson:* per-line right-margin annotation, Codillon's existing zone, scales if it is
**projectable**. Spec visualizations need a way to show something when there is no run data yet.

**Python Tutor.** Python Tutor shows stack frames on the left and heap objects on the right,
connected by **arrows for references**, with forward and back stepping. It has been used at very
large scale in intro courses.
([Guo, SIGCSE 2013](https://pg.ucsd.edu/publications/Online-Python-Tutor-web-based-program-visualization_SIGCSE-2013.pdf))
*Codillon lesson:* the frames-plus-heap-plus-arrows idiom is what novices already know, so it is
the right *concrete* half of an abstract-vs-concrete heap view.

**Sketch-n-Sketch.** Users directly manipulate SVG output, and the system **synthesizes the program
edit** using execution traces (output-directed programming).
([Hempel, Lubin, Chugh UIST 2019](https://arxiv.org/abs/1907.10699))
*Codillon lesson:* the inverse direction works for specs too. **Drag a violating value back inside
the region** and have the editor propose the spec or code change.

**Abstract debuggers (Goblint; Mopsa).** These put static-analysis results behind a
**debugger-style interface** (step, inspect, call stacks) over abstract states, delivered via LSP
and DAP. ([Holter et al., Onward! 2024](https://patricklam.ca/papers/24.onward.abs-debug.pdf);
[Mopsa](https://arxiv.org/abs/2407.12499))
*Codillon lesson:* the **slider can scrub abstract states** (intervals, congruences) as well as
concrete ones. Same control, different "ink."

**JetBrains MPS / mbeddr.** Projectional editing allows tables, math notation and state machines
inline in code. mbeddr has interface contracts (pre/post, protocol state machines) and model
checking, with **counterexamples lifted back to the DSL level** (e.g. state machine), not shown as
generated C. ([mbeddr](https://mbeddr.com/); [MPS](https://www.jetbrains.com/mps/))
*Codillon lesson:* Codillon is already a structured editor, so a spec can be a **first-class
projected widget**. Counterexamples must be shown at the student's level of abstraction (WAT
lines and values), not as solver terms.

### 1.4 Model finders, model checkers and property-based testing

**Alloy visualizer.** An instance or counterexample is drawn as a graph. **Themes** assign
shape and color per signature, and Magic Layout infers a theme. **Projection** over a signature
(often Time) splits the instance into per-tick frames. Alloy 6 shows a temporal trace as a
**current state on the left and next state on the right**, with a clickable state strip. The
evaluator runs arbitrary expressions on the instance. A known problem: layout is computed per
frame, so **nodes jump between frames**.
([Alloy visualizer docs](https://alloy.readthedocs.io/en/latest/tooling/visualizer.html);
[Improving the visualization of Alloy instances](https://arxiv.org/abs/1811.10817))
*Codillon lesson:* **layout stability across steps** matters. Codillon's tweened animation is
already the right instinct. Side-by-side "before and after this step" fits checking that an
invariant is re-established.

**Forge / Sterling and Cope-and-Drag (Brown).** Forge, a teaching-oriented Alloy relative, uses the
Sterling visualizer with **custom JS/D3 visualization scripts**. Cope-and-Drag (ECOOP 2025) adds a
tiny language of **layout constraints** (orientation, cycles, grouping) on top of the default
graph. The diagram stays draggable but cannot violate the constraints. In three user studies, short
CnD specifications improved comprehension over the default.
([CnD paper](https://arxiv.org/abs/2412.03310);
[Sterling discussion](https://alloytools.discourse.group/t/visualization-for-alloy-what-do-you-want/111))
*Codillon lesson:* for heap specs, a **few declarative layout hints** (a hash table drawn as a
row of buckets, a list drawn left-to-right) give most of the value of a custom visualizer.

**TLA+ Toolbox error-trace explorer.** A violating trace is a list of states. **Variables that
changed in a step are shown in red**, unchanged ones can be hidden, and user expressions are
evaluated per state (bold). On the mailing list, users have **misread the red "changed" highlight
as "violated here"**; the actual violation is only at the final state.
([learntla: Toolbox](https://learntla.com/topics/toolbox.html);
[TLA+ discussion](https://discuss.tlapl.us/msg02687.html))
*Codillon lesson:* never use the violation color for anything but violation. Show change with a
neutral cue such as motion or weight.

**Hypothesis and QuickCheck (shrinking).** Both report a **minimal failing example**. QuickCheck
prints `*** Failed! Falsified (after N tests and M shrinks)` with the shrunk input. Hypothesis
shrinks the underlying choice sequence. Its **explain phase** annotates each argument that could
be anything with `# or any other generated value`, and reports **lines executed only by failing
inputs, never by passing ones**.
([Hypothesis docs](https://hypothesis.readthedocs.io/en/latest/);
[falsify / shrinking](https://well-typed.com/blog/2023/04/falsify/))
*Codillon lesson:* show the **smallest** witness and mark **which parts of it matter**. "Lines
only failing runs reach" is a simple, very effective localization signal for a runtime-capable
editor.

### 1.5 Diagrams from mathematics, loop-invariant pedagogy, counterexample studies

**Penrose.** Penrose separates *what* (Substance: objects and predicates, in math-like notation)
from *how it looks* (Style), within a Domain of types and predicates. Layout comes from
**constrained numerical optimization**, so `IsSubset(A, B)` becomes "circle A inside circle B."
Lean's ProofWidgets uses it for Venn and commutative diagrams.
([Penrose, SIGGRAPH 2020](https://penrose.cs.cmu.edu/siggraph20))
*Codillon lesson:* refinement predicates are Substance. A small **Style for `even`, `<`, `∈`**
gives automatic diagrams for compound predicates.

**Graphical Loop Invariants (GLI) and CAFÉ (Liège).** Students first **draw** a loop invariant as
an informal diagram of the variables, their properties and relationships. Typically this is the
classic array-partition picture: a bar split at index `i` into a "done, property P" zone and a
"not yet" zone. Only then do they code. The tool checks that the code aligns with the diagram.
([CAFÉ, arXiv 2607.03001](https://arxiv.org/abs/2607.03001))
Fowler's RESOLVE-based study found loop invariants hard for *all* students, who build on
pre/postconditions to get there ([Learning loop invariants](https://par.nsf.gov/biblio/10195158)).
Dafny course reports cite students' **difficulty knowing what the verifier knows at a given
point** ([Noble et al. 2022](https://arxiv.org/abs/2205.00787)).
*Codillon lesson:* the **array-partition picture is the canonical invariant glyph**, and a
"what is known here" display at the cursor (like Lean's goal view) addresses the main complaint
of Dafny learners.

**Counterexample comprehension studies.** Bosch industrial studies found that engineers
understood and trusted model-checker results much more when counterexamples were **explained**
than when shown raw ([arXiv 2304.08950](https://arxiv.org/abs/2304.08950)). CEAM (AutoProof)
**minimizes integer values** in prover counter-models and makes them readable
([arXiv 2208.10492](https://arxiv.org/abs/2208.10492)).
*Codillon lesson:* raw solver models are unusable for novices. Small, concrete, explained
witnesses are the deliverable.

**Type-as-region metaphors.** I found **no IDE that draws refinement types as regions** on a
number line or Euler diagram. The closest are Frama-C Eva's printed interval-plus-congruence
values, Lean/Penrose Venn displays of subset hypotheses, and the school-math number-line
convention (filled dot = closed bound, hollow = open, shaded = solution set). *This is a real gap,
and Codillon could be the first to fill it.*

---

## 2. Synthesis

### (A) Design principles for spec visualization in a live editor

1. **Name the epistemic state, and never let two share a look.** Distinguish *proved*, *refuted
   by a concrete witness*, *held on this run only*, *unknown/timeout*, *assumed/admitted* and
   *stale*. F*'s green-vs-blue dashed lines and Dafny's thin bar vs. check-disk are the models. The
   most dangerous merge is "observed OK" with "proved."
2. **Every red must lead to a witness.** A refutation glyph is clickable and jumps the slider to
   the witnessing step, or to a hypothetical trace (Dafny/BVD, SPARK, Hypothesis). If there is no
   witness, use a different glyph (unknown, not wrong).
3. **Confirm witnesses by running them.** Codillon executes, so a solver counterexample can be
   replayed. Only a replayed witness gets the bomb-grade darkred; an unreplayed one is drawn
   "ghosted" (Christakis et al.; Dafny's own disclaimer).
4. **Show the gap, not just the verdict.** For a subtype check `have ⊆ need`, draw the *set
   difference* `have \ need`. That region is where counterexamples live, and its size and shape
   tell the student what fix is needed (Liquid Haskell's have/need/context, drawn).
5. **Two places, one line.** A broken promise links the clause that promised it to the site that
   broke it (Verus/Whiley multi-span). Use Codillon's curve idiom so spec flow looks like dataflow.
6. **Split compound predicates into conjuncts** that pass or fail separately (Why3 Split VC,
   Dafny isolate_assertions). The student should see "even ✓, < 100 ✗", not "predicate ✗".
7. **Stay on the line; detail on selection.** Keep Codillon's rule of no error panel. Each line
   gets one compact spec glyph in the right margin. Richer pictures (number line, region, heap
   diagram) open on hover or selection, Lean-presentation style, and can be **pinned**.
8. **Staleness is visible and animated.** On an edit, previous verdicts fade or squiggle (Dafny)
   and re-settle with a tween when re-checked. Never show a confident verdict for text that has
   changed since.
9. **Check what's being looked at first** (Isabelle perspective), and show "not yet checked" as
   neutral, never as green.
10. **Keep layout stable across time.** Steps, iterations and edits move things by tweening,
    never by re-layout jumps (Alloy's per-frame layout problem).
11. **Reserve the violation color.** Darkred means violated, never "changed" or "interesting"
    (TLA+ misreading). Show change with motion or weight.
12. **Minimal witnesses, with irrelevance marked.** Shrink, then mark which values could be
    anything (Hypothesis explain). Mark the lines only failing runs reach.
13. **The spec is editable through its picture.** Dragging an interval fence or picking a modulus
    edits the predicate (livelits, Sketch-n-Sketch). Dragging a violating value back into the
    region asks "relax the spec or fix the code?" and offers Clousot-style weakest-precondition
    suggestions.
14. **Cover the domain, not just the run.** Show how much of a predicate's region the current
    runs have actually exercised. One green run covers a point, not an interval.
15. **Be honest about what can't be drawn.** When an obligation is genuinely symbolic (quantified,
    nonlinear), fall back to text with a **concrete-instance sampler** rather than a misleading
    picture.

### (B) Catalog of candidate visual primitives

The rows below are written against Codillon's existing vocabulary: type shapes (rect/ellipse,
short/tall), input cups vs. solid outputs, dataflow curves, frame lines, the step slider, and
darkred.

**B1. Predicates on single numbers**

| Primitive | Encoding | Notes |
|---|---|---|
| **Refinement band** | A thin mini number line inset *under* the type shape, with the admitted region shaded in the type color. The runtime value at the current step is a dot. Dot outside the shading means darkred. | Base primitive. Reuses slot-value: the value is drawn *on* the band. |
| **Fences (bounds)** | Short vertical posts at the band's endpoints. **Filled post = inclusive, hollow = exclusive** (school-math convention). An unbounded side fades out with an arrow. | Strict vs. non-strict errors (`<` vs `<=`) become visible. |
| **Wraparound ring** | For i32/i64, the band can be drawn as a **ring (clock)** in which `0x7fffffff + 1` wraps to `-2^31`. Two tick marks show the **signed and unsigned readings** of the same bits. | Wasm-specific and important: Wasm ints have no signedness, so the operator chooses. An overflow bug is a dot jumping the seam. |
| **Congruence comb / stripes** | Parity and `x ≡ r (mod m)` as a **comb of teeth** on the band (only admitted residues get ticks), or as a striped fill whose period is `m` and whose phase is `r`. "Even" = every other tick lit. | Mirrors Eva's `[a..b],r%m`. Divisibility by 4 has sparser teeth, which reads as "stronger." |
| **Finite-set dots** | Enumerations (`x ∈ {0,1,2,3}`, opcodes, colors) as discrete dots on the band. | Good for small enums and flags. |
| **Region nesting (subtype)** | A refined type is drawn as a **smaller region inside** the base shape. `even ∧ <100` nests inside `even`, which nests inside `i32` (Euler/Penrose style). | Makes "stronger spec" literally a smaller picture. |
| **Spill (failed subtyping)** | At a dataflow connection, overlay the producer's band on the consumer cup's band. The part of the producer's region **outside** the cup's region is hatched darkred and "spills over the cup's rim." | The key glyph: the set difference, where counterexamples live. |
| **Conjunct chips** | A compound predicate is shown as small chips (`even`, `<100`), each with its own status. | Why3 split. |

**B2. Relations between values (dependent types and contracts)**

- **Anchored band.** For an output whose region depends on an input (`result ∈ [x, x+3]`),
  draw the output band with a faint **tether** to the input's dot. Scrubbing the slider moves the
  input dot, and the output's admitted window slides with it.
- **Relation plot.** For a binary relation (`y == 2x`, `y >= x`, `y ≡ x mod 2`), show a small
  **2D panel** with input on one axis, output on the other, and the spec region shaded (a line,
  half-plane or lattice). Each executed step adds an (x, y) point. Points outside the region are
  darkred and **clickable to jump the slider**. This turns "dependent result" into "points must
  stay on the shaded shape" and builds up a test-coverage picture over time (principle 14).
- **Pre/post ledger on the function frame.** At the function's top frame line, the `requires`
  bands sit on the input cups. At the `end`, the `ensures` bands sit on the result. A curve links a
  failing `ensures` chip to the `return` or `end` that broke it (two-place rule).
- **"Have / need / context" triptych** on hover: the inferred band, the required band, and the
  in-scope facts as chips. This is Liquid Haskell's error rendered as pictures.

**B3. Invariants over time (loops)**

- **Horizon line.** On the loop's frame line, draw a thin horizontal **horizon** at the loop
  head: the invariant must hold at that point every iteration. Each time the back-edge is taken,
  a tick lands on the horizon, **filled** if the invariant held and **darkred** if it broke.
  Visually, the loop must re-cross the line on each iteration. Entry ("established") and back-edge
  ("preserved") ticks look different, matching the two Hoare-logic obligations.
- **Invariant lane on the slider.** Add a lane under the step slider: one cell per iteration,
  colored by invariant status. Zoomed out, it becomes a sparkline, following Victor's "table →
  plot." The first darkred cell is the jump target.
- **Variant staircase.** A termination measure is a **descending staircase** beside the loop.
  A step that fails to descend, or drops below 0, is the violation.
- **Array-partition glyph.** For array or memory loops, show the GLI/Dijkstra bar with the index
  `i` as a moving divider. The left zone is labeled with the invariant's property (e.g. "sorted",
  "all even") and colored per element at runtime. An element on the "done" side that violates the
  property is drawn darkred.
- **Overlay ghosting.** Previous iterations' values are already grayscaled in Codillon. Add an
  optional **onion-skin overlay** of all iterations' dots on a refinement band, so drift toward a
  fence is visible before it crosses.

**B4. Memory and heap specifications (Wasm linear memory)**

- **Memory ribbon.** Linear memory as a horizontal ribbon of cells, the concrete view (Python
  Tutor's heap side). Footprints and `modifies` sets are **highlighted ranges**. A store outside the
  declared footprint is a darkred mark beyond a fence.
- **Abstract vs. concrete, aligned.** Put the abstract model (a set, map or sequence drawn as
  labeled tokens) above the concrete ribbon, and connect them with **abstraction curves**: each
  abstract element points to the cells that represent it, in the dataflow-curve idiom. The
  representation invariant is that **the alignment is clean**:
  - an *orphan* cell (allocated or occupied, but representing nothing) is darkred;
  - an *orphan* token (an abstract element with no concrete home) is darkred;
  - a *crooked* line is darkred. For a hash table, the key's line must land in bucket
    `hash(k) mod n`, and a key in the wrong bucket is visibly off-axis.
- **Layout hints, not custom renderers.** Declare that a region is "buckets of size 8" or "a
  sorted array," as in Cope-and-Drag, to get a readable default picture.
- **Possible-worlds strip** (KeY SED). When the spec is symbolic (aliasing unknown), show 2–3
  representative concrete configurations as thumbnails, labeled as samples.

**B5. Counterexamples and witnesses**

- **Witness pill on the slider.** A replayed counterexample is a darkred pill on the slider;
  clicking it jumps to the violating step, as with runtime traps today.
- **Ghost track.** An unconfirmed solver witness (not yet replayed) is a **dashed parallel
  track** above the real slider. Its values are drawn in outlined (not filled) shapes with a
  hypothetical style (BVD's `'7` placeholders become "?" shapes). Replaying it either promotes it to
  a solid pill or marks it **spurious** and discards it.
- **Shrunk input card.** The minimal inputs, with Hypothesis-style "any value" markers on
  irrelevant ones, and a "failing-only lines" tint in the gutter.
- **Before/after pair.** For invariant-preservation failures, show the state at loop head
  iteration k (holds) beside k+1 (broken), Alloy-6 style, with the offending changed value
  highlighted by motion, not by red, until the violated predicate itself is drawn.
- **Suggested fix chip.** "Require x even?" or "Weaken ensures to ≤?" (Clousot), applied by click
  and reverted by undo.

### (C) Known failure modes

1. **Clutter.** Per-line bands, curves, chips and fences multiply quickly. Agda's nine background
   colors and every-line projection boxes show that *defaults matter*. Default to one glyph per
   line and expand on selection. Projection Boxes users' preferences differed widely, so the
   display has to be configurable.
2. **False confidence from weak or vacuous specs.** A green check on `ensures true`, or after an
   `assume false` or admitted lemma, is still green. Mitigate with a "strength" cue (the region's
   size relative to the base type) and an explicit **"assumed"** style that marks everything
   downstream of it (F* README warning).
3. **Run-verified mistaken for proved.** Codillon's main temptation is that the slider shows
   every step green, so the student concludes the spec holds. One run covers a point; the band
   should show the **unexercised remainder** as distinctly unshaded or "unknown."
4. **Misread highlights.** Change shown as violation (TLA+), or a stale verdict shown as current
   (Dafny's reason for its squiggly-obsolete state).
5. **Spurious and underspecified witnesses.** Solver models can be wrong for the source program
   or meaningless (Dafny's disclaimer; BVD's `'7`). Showing them as fact destroys trust. Replay or
   label them.
6. **Doesn't scale.** 100k steps, 64 KiB pages and large arrays break per-element drawings. You
   need aggregation (sparklines, histograms, "first violation" jump) and Victor's
   table-to-plot shift.
7. **Meaningless when obligations are symbolic.** A number line can't show
   `∀ i < n. a[i] ≤ a[i+1]` or nonlinear `x*y < z`. Without values, there is nothing to plot.
   Fall back to text, concrete samples, or the array-partition glyph. Don't draw a fake region.
   (This is also Lerner's loop datavoid: no runs means no picture.)
8. **Timeouts are uninformative.** Dafny reports only "which definition timed out"; splitting into
   batches helps. A timeout must look like *unknown*, never like failure or success.
9. **Layout instability.** Re-layout per step (Alloy) breaks object identity across time.
10. **Wraparound blindness.** Drawing i32 on a straight infinite line hides exactly the overflow
    bugs Wasm students hit. Signed/unsigned confusion is invisible unless both readings are shown.
11. **Color-only encoding.** Red/green fails for color-blind users. Codillon's shape and glyph
    language (clef, ✗, bomb) is better; keep shape-plus-color redundancy (rails, comb teeth,
    hatching).
12. **Explanation debt.** Novices don't benefit from raw solver output (Bosch studies, CEAM). Every
    picture needs a one-sentence caption in Codillon's existing darkred commentary label.
