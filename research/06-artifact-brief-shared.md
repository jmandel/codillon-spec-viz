# Shared brief for the ten HTML prototypes

Read, in order: 00-codillon-today.md (what exists), 05-ten-visualization-ideas.md (your assigned idea and the
cross-cutting rules at the end), 03-sample-programs.md (the programs, specs, seeded bugs and the JSON fixture
you must embed), and skim 01-language-design.md and 04-requirements-and-bug-taxonomy.md (rubric at the end).

## Deliverable
One self-contained file `artifacts/NN-<slug>.html` (NN = your idea number, two digits). No external network
resources: no CDN scripts, no web fonts, no images. Vanilla HTML + CSS + JS + inline SVG only. Must open from
`file://` in Chromium and render with no console errors. Target ~800–2000 lines; quality over quantity.

## Page structure (identical across all ten so the reviewer can compare)
1. **Header**: idea number and name, one-paragraph statement of the metaphor, and a *legend* showing every
   visual primitive the artifact introduces, each with its meaning (proven / unknown / false / dynamic / vacuous
   distinctions must all be present in the legend).
2. **Section A — the primitive in isolation**: 2–4 tiny instruction snippets (3–6 lines each) that show the
   primitive on a single value: e.g. `(i32 | even)`, `(i32 | 0 <= v < n)`, a dependent result, one static
   mismatch, one runtime violation. Interactive where it helps (a slider or toggle).
3. **Section B — number theory**: the isqrt (or gcd, if your idea fits gcd better; say which) program from
   03-sample-programs.md rendered in the Codillon idiom (one instruction per line, gutter, fractions/type
   shapes on the right, connections if your idea uses them), with the spec, a working step slider over the
   fixture trace, and a **"Seed bug" control** offering the seeded bugs from the fixture. When a bug is seeded,
   the program text changes on the affected line and the visualization must make the spec-adherence failure
   obvious *without* any prose error message (a short commentary label in Codillon's floated-right darkred style
   is allowed, but the picture must carry it).
4. **Section C — hash table**: the open-addressing hash table from 03-sample-programs.md, with the model/
   memory state visible as your idea dictates, a step slider over the fixture's operation sequence trace, and the
   seeded bugs (at minimum the tombstone-as-empty bug and one other). Same rule: the picture must carry it.
5. **Footer — self-critique**: 5–8 bullets: what the primitive makes obvious, what it hides, how it scales,
   what it would cost to implement in Codillon's Rust/SVG architecture, and your scores on the rubric in
   04-requirements-and-bug-taxonomy.md.

## Style tokens (match Codillon; do not invent a new look)
- Background `#fffff0` (ivory). Code 22–24px, `font-family: "Latin Modern Roman", "CMU Serif", "Computer Modern",
  Georgia, "Times New Roman", serif`. Small labels 10–12px condensed sans:
  `font-family: "Latin Modern Sans", "Fira Sans Condensed", "Roboto Condensed", "Arial Narrow", sans-serif`.
- Type colors: i32 `#6A5ACD`, i64 `#483D8B`, f32 `#228B22`, f64 `#006400`, unknown `#000`. Muted fill =
  color mixed 70% toward ivory. Meta lines (func/param/result/import) `indigo`. Comments `darkblue`.
- Shapes: i32 = rectangle 30×11 (input cup = open-top outline, output = solid), i64 = 30×19 rectangle,
  f32 = 30×11 ellipse, f64 = 30×19 ellipse, unknown = 5-point star. Inputs above a 1px rule, outputs below.
- Badness = `darkred` only. Unknown/needs-hint = `indigo` + dashed. Dynamic-only = `slategray` + dotted.
  Vacuous = hollow outline + `○`. Proven = nothing extra (silence is success).
- Gutter glyphs (20px, darkred unless noted): `𝄞` malformed, `✗` invalid, `💣` trap, `𝄠` synthetic end,
  `⚖` spec violated (new), gray line number otherwise.
- Connections: cubic curves 2px in the type color from output shape to input cup; mismatches 1px dotted.
- Slider: sticky at top of the section, ticks; current step darkblue pill, error step darkred pill.
- Animate state changes with CSS transitions (~250ms). A rejected edit shakes (translateX ±5px, 250ms).

## Interactivity requirements
- Step slider drives: current-line arrow, values inside shapes, your idea's runtime primitive, memory view.
- Seed-bug control: a `<select>` or radio group; selecting a bug rewrites the affected program line(s) and
  swaps to that bug's fixture trace. "No bug" must look calm (mostly ivory, numbered lines).
- Hover on any primitive shows a small tooltip with the underlying predicate text and status. Hover is
  supplementary: nothing may be *only* discoverable by hover.
- Keyboard: ←/→ step the slider.

## Quality bar and self-check (mandatory before you finish)
- Render it headless and look at it: `chromium --headless --disable-gpu --screenshot=/home/jmandel/hobby/.agent-scratch/codalon-viz/shots/NN.png --window-size=1400,3200 file:///home/jmandel/hobby/codalon-dependent-viz/artifacts/NN-<slug>.html` then view the PNG with the Read tool. Fix layout bugs you see. Repeat at least twice.
- Check for JS errors: `chromium --headless --disable-gpu --enable-logging=stderr --v=0 --dump-dom file://... 2>&1 | grep -i -E 'error|uncaught' | head` (or run the JS logic through `node` where feasible).
- Verify with your own eyes that: (1) the no-bug state is calm; (2) each seeded bug produces a change in the
  *picture* that a reviewer would notice within two seconds; (3) false, unknown, dynamic and vacuous statuses are
  visually distinct and all appear somewhere in the page; (4) runtime values appear inside shapes as the slider moves.
- Do not modify files outside `artifacts/NN-*.html` (you may write scratch files under
  `/home/jmandel/hobby/.agent-scratch/codalon-viz/`). Do not run git commands.
