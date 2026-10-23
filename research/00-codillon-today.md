# Codillon today (as of upstream main, Oct 2026)

Source: https://github.com/codillon/codillon (LGPL-2.1). Keith Winstein is the principal author
(42 of the last 50 commits). Co-advised with Chris Gregg. Brown Institute Magic Grant 2025–26:
"a curriculum revolving around music and signal processing, and a purpose-built WebAssembly editor"
for Stanford CS 10N (an intro course). Local clone: ~/hobby/.agent-scratch/codalon-viz/codillon

## What it is
A browser-based *structured text editor* for the WebAssembly text format (WAT), written in Rust,
compiled to wasm, rendering directly to DOM + SVG (no framework). One instruction per line.
Students write small Wasm modules (i32/i64/f32/f64 only; no SIMD, no reference types) that call
host "draw" imports (point, clear, set_color, set_extent…) to draw on a canvas. Programs are
continuously re-parsed, re-validated, instrumented, and *re-executed* on every keystroke, with a
time-travel step slider over the execution log (up to 100k steps).

## Visual vocabulary for *validity* (this is what we must build on)
Aesthetic: ivory background (#fffff0), MLModern (LaTeX-like) serif at 24pt for code,
condensed sans for small labels. Hand-drawn SVG icons. Smooth tweened animations (0.25s)
for everything appearing/disappearing/moving; "shake" animation when an edit is rejected.

1. **Gutter glyphs per line** (darkred, 20pt, in the left margin, instead of the line number):
   - `𝄞` (treble clef) — *malformed* line (doesn't parse).
   - `✗` — *invalid* line (parses, but fails Wasm validation; also used for an instruction whose
     output is never consumed = "stranded" value).
   - `💣` — *runtime error* on this line (trap, e.g. divide by zero, unreachable); line text turns darkred.
   - `𝄠` — a *synthetic* `end` was auto-inserted before this line (dashed darkred box shows it).
   - Line number (gray) when nothing is wrong. Meta lines (func/import/global) indigo.
2. **Commentary**: the reason for a malformed/invalid/runtime error is rendered as a small darkred
   bordered label floated right on the same line (CSS `data-commentary`). No separate error panel, ever.
3. **Type "fractions"**: to the right of each instruction, its stack effect is drawn as a fraction-like
   glyph: *inputs on top* (open "cup" shapes, muted fill, type-colored stroke), a rule, and *outputs
   below* (solid filled shapes). Shape encodes type: i32 = short rectangle, i64 = tall rectangle,
   f32 = short ellipse, f64 = tall ellipse, unknown/polymorphic = star ("mystery"). Colors:
   i32 #6A5ACD (slate blue), i64 #483D8B, f32 #228B22 (forest green), f64 #006400, unknown black.
   An input cup with nothing feeding it is drawn *empty* with a fade-up gradient (missing operand).
   An output that is never consumed is drawn in a "stranded" style (thick stroke) and the line gets ✗.
4. **Connections**: smooth SVG curves from each producer's output shape to the consumer's input cup
   (the dataflow through the operand stack made explicit). A *mismatch* (wrong type arriving) is drawn as
   a thin dotted "bad" connection that visibly *tries* to reach the cup but is routed into it awkwardly.
5. **Frames**: block / loop / if / func bodies are indented and bracketed by thin vertical frame lines;
   an *unclosed* frame shows a `⊘` ("end of all prohibitions" road sign) symbol. Loops actually taken
   at runtime get a small "loop" label on the frame line.
6. **Runtime**: a sticky step slider at the top with tick labels (current step = darkblue pill;
   a step that errored = darkred pill). A navy arrow icon points at the instruction executing at the
   selected step. Each fraction's shapes show the *actual runtime value* at that step inside the shape
   (`slot-value`, 8pt); values from an earlier iteration are grayscaled ("old"). The drawing canvas
   shows the program's graphical output at that step.
7. **Editing discipline**: edits that would make the module un-"validizable" are reverted with a shake;
   `end`s are inserted synthetically; duplicate symbols disable lines (rendered "inactive" with reason).

## Design ethos to preserve
- Validity is *spatial and continuous*: shown on the code, as you type, never in a modal or console.
- Types are *shapes*, dataflow is *lines*, badness is *darkred*, runtime is a *slider*.
- One instruction per line → one row of annotations per line; the right margin is the annotation zone.
- Everything animates between states so the student sees *what changed* when they changed something.
- Hand-crafted glyphs with a musical/typographic wit (clef for malformed, bomb for trap).
