# z3w: single-threaded Z3 for the browser (no SharedArrayBuffer, no COOP/COEP)

This is Z3 compiled to WebAssembly **without pthreads**. It runs in a plain Web Worker
on any static host, including GitHub Pages, which cannot set `Cross-Origin-Opener-Policy`
or `Cross-Origin-Embedder-Policy`. The module needs neither `crossOriginIsolated` nor
`SharedArrayBuffer`. Its linear memory is a normal, non-shared `WebAssembly.Memory`, and
the generated JS contains no references to `SharedArrayBuffer`, `Atomics` or `Worker`.

| file | purpose |
|---|---|
| `z3w.wasm` | Z3 plus the C shim (Release `-Os`) |
| `z3w.js` | ES module: the emscripten factory (`z3wModule`) plus the `Z3W` API |
| `z3w-worker.js` | Example module worker, protocol `{id, smtlib} -> {id, output, ms}` |
| `package.json` | `{"type":"module"}`, so Node loads `z3w.js` without a reparse warning |
| `build/` | Reproduction kit: `build.sh`, shim sources, tests, browser harness. The tests assume the original layout `<root>/{build.sh,src,test,dist}`, so copy `build/*` to a root that has `dist/` beside it |

## Version

* **Z3 5.3.1**, the latest stable GitHub release (published 2026-10-15). Tag `z3-5.3.1`,
  commit `ac9156f97cb44e56472e1c841f7a2beb1e976b24`. `Z3_get_full_version()` reports
  `5.3.1.0`.
* Emscripten **6.0.13** (`e13ee988ce3d87a738dd8f3661d02223308c412a`) from emsdk `latest`
  (2026-10-23). Binaryen version_133.

## API

```js
import { Z3W } from './z3w.js';
const z3 = await Z3W.create();          // optional arg: emscripten Module overrides (locateFile, wasmBinary, ...)
z3.eval('(declare-const x Int)(assert (> x 2))(check-sat)(get-model)');  // -> "sat\n(\n  (define-fun x () Int\n    3)\n)\n"
z3.eval('(assert (> zz 1))');           // -> 'error:(error "line 1 column 72: unknown constant zz")\n'  (see note on positions)
z3.reset();                              // fresh context: drops declarations, assertions, scopes and options
z3.free();
z3.version                               // "5.3.1.0"
```

* `eval` is synchronous. It runs on one persistent context, so declarations, assertions
  and `(push)`/`(pop)` scopes carry over between calls until `reset()`.
* Each `Z3W.create()` instantiates a separate wasm instance with its own memory.

### C shim (`build/src/z3w_shim.cpp`)

| export | behaviour |
|---|---|
| `z3w_new()` | `Z3_mk_config`, `model=true`, `Z3_mk_context`, then `Z3_set_error_handler(ctx, NULL)` (the default handler calls `exit(1)`) |
| `z3w_eval(h, text)` | `Z3_eval_smtlib2_string`. If `Z3_get_error_code != Z3_OK`, it returns `"error:" + Z3_get_error_msg(...)`. That message is Z3's whole output for the call, including the `(error "...")` line. Stray C++ exceptions are caught and also returned as `error:...` |
| `z3w_reset(h)` | Deletes and recreates the context, keeping the same handle |
| `z3w_free(h)` | Deletes the context and the handle |
| `z3w_version()` | Returns the result of `Z3_get_full_version()` |

### Worker protocol (`z3w-worker.js`)

```js
const w = new Worker(new URL('./z3w-worker.js', import.meta.url), { type: 'module' });
// unsolicited, once:  { ready: true, ms, version, crossOriginIsolated }   (or { ready:false, error })
w.postMessage({ id: 1, smtlib: '(check-sat)' });   // -> { id: 1, output: 'sat\n', ms: 0.4 }
w.postMessage({ id: 2, reset: true });             // -> { id: 2, output: '', ms }
```

The worker processes requests strictly in order. If the wasm instance traps (stack
overflow, OOM abort), the worker returns `error:<message>` and builds a new instance. To
cancel a runaway query from the page, call `worker.terminate()` and start a new worker.
Prefer `:rlimit` so that it never comes to that.

## Build

Run `build/build.sh [Os|O2] [jobs]`. It clones `z3-5.3.1` and emsdk into its own
directory if they are missing, then configures, builds and links. The full configure,
compile (880 TUs) and link took **421 s for -Os and 420 s for -O2 at `-j6`** on the
12-core host. Peak memory stayed comfortably under the 10 GB available. Installing emsdk
took about 1 minute.

```sh
source emsdk/emsdk_env.sh
emcmake cmake -G Ninja -S z3-src -B build-Os \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS=-fwasm-exceptions -DCMAKE_CXX_FLAGS=-fwasm-exceptions \
  -DCMAKE_C_FLAGS_RELEASE="-Os -DNDEBUG" -DCMAKE_CXX_FLAGS_RELEASE="-Os -DNDEBUG" \
  -DZ3_BUILD_LIBZ3_SHARED=OFF -DZ3_SINGLE_THREADED=ON -DZ3_POLLING_TIMER=ON \
  -DZ3_BUILD_EXECUTABLE=OFF -DZ3_BUILD_TEST_EXECUTABLES=OFF \
  -DZ3_BUILD_{PYTHON,JAVA,DOTNET,JULIA,OCAML,GO}_BINDINGS=OFF -DZ3_BUILD_DOCUMENTATION=OFF \
  -DZ3_ENABLE_EXAMPLE_TARGETS=OFF -DZ3_INCLUDE_GIT_HASH=OFF -DZ3_INCLUDE_GIT_DESCRIBE=OFF \
  -DZ3_LINK_TIME_OPTIMIZATION=OFF
ninja -C build-Os -j6 libz3
em++ -std=c++20 -Os -fwasm-exceptions -I z3-src/src/api src/z3w_shim.cpp build-Os/libz3.a -o out-Os/z3w.js \
  -sMODULARIZE=1 -sEXPORT_ES6=1 -sEXPORT_NAME=z3wModule -sENVIRONMENT=web,worker,node \
  -sALLOW_MEMORY_GROWTH=1 -sINITIAL_MEMORY=64MB -sMAXIMUM_MEMORY=4GB -sSTACK_SIZE=16MB -sFILESYSTEM=0 \
  -sEXPORTED_FUNCTIONS=_z3w_new,_z3w_eval,_z3w_reset,_z3w_free,_z3w_version,_malloc,_free \
  -sEXPORTED_RUNTIME_METHODS=UTF8ToString,stringToUTF8,lengthBytesUTF8 \
  --extern-post-js src/z3w_api.js
```

### Key choices

* **No pthreads.** CMake's `FindThreads` succeeds against emscripten's libc pthread
  stubs without adding `-pthread`, so no object is built with atomics or shared memory.
  `Z3_SINGLE_THREADED=ON` defines `SINGLE_THREAD`. That define compiles out the
  `std::thread` code in `smt_parallel`, `sat_solver` (parallel mode), `parallel_tactical`,
  `tactical.cpp` (`par-or` / `par-then`) and `nra_solver`.
* **Timers.** `Z3_POLLING_TIMER=ON` turns `scoped_timer` timeouts whose handler is a
  `cancel_eh<reslimit>` into a clock check inside `reslimit::inc()`. That is the case for
  `(set-option :timeout N)` and `try-for`. When no timeout is set, the check
  short-circuits and costs nothing. Without this option every timeout would try to start
  a `std::thread`. The deterministic `(set-option :rlimit N)` never needed a thread.
* **Exceptions.** Z3 relies on C++ exceptions (`z3_exception`, `default_exception`,
  out-of-memory). The build uses native wasm exception handling (`-fwasm-exceptions`,
  emscripten's default legacy encoding) for both libz3.a and the link. That needs Chrome
  or Edge 95+, Firefox 100+, Safari 15.2+ and Node 17+, and was verified on Chromium 154
  and Node 26.11.1. JS-emulated `-fexceptions` was not needed. It is larger and slower,
  and only matters for browsers older than those listed.
* **Stack.** `STACK_SIZE=16MB`, against emscripten's 64 KB default. Z3 recurses deeply.
  The official z3-solver npm build uses 20 MB. A 400,000-deep nested `(+ 1 (+ 1 ...))`
  term parses and solves.
* **Prior art.**
  * `cpitclaudel/z3.wasm` (2017) built with `--noomp`, JS exception catching,
    `ABORTING_MALLOC=0` and memory growth, and applied no source patches.
  * Z3's own `src/api/js` (npm `z3-solver`) also passes `-DZ3_SINGLE_THREADED=ON`, but it
    links with `-pthread` and `USE_PTHREADS`, for its async API and timeouts. That is
    exactly what requires COOP/COEP. This build drops that layer.

### Patches

**None.** Z3 5.3.1 builds unmodified for this target. CMake options and the shim cover
everything (`Z3_set_error_handler(ctx, NULL)` replaces the `exit(1)` default handler).
`build.sh` will still apply any `patches/*.patch` placed next to it.

### -Os vs -O2 (Node 26, fixed-work benchmark `build/test/bench.mjs`, min of 5, two rounds)

| | wasm raw | gzip -9 | brotli -q11 | PHP(11,10) rlimit 2M | bv-factor | NIA isqrt | quantifier f2 |
|---|---|---|---|---|---|---|---|
| **-Os (shipped)** | **10,526,640** | **3,566,498** | **2,390,802** | 1550–1572 ms | 27.6–28.4 | 17.5–17.8 | 41.8–44.7 |
| -O2 | 15,648,041 | 4,961,019 | 3,062,574 | 1543–1567 ms | 24.5–24.8 | 15.9–16.5 | 37.2–37.9 |

-Os is 33% smaller and between 0% and 15% slower, so it is the build shipped here.
Relinking with `-Oz` saved only 0.7%. `z3w.js` is 14,638 bytes raw, 5,209 gzip and
4,753 brotli. GitHub Pages serves gzip, so expect about **3.6 MB** on the wire.

## Test results (all pass)

The tests are in `build/test/tests.mjs`. Each test runs on a fresh context via `reset()`.
The Node figures are from `run-node.mjs ../dist 3`. The Chromium figures come from the
headless Chromium 154 page `test/browser/index.html` plus a module worker, served by
`python3 -m http.server` with **no COOP/COEP**: `crossOriginIsolated === false` in both
page and worker, and `typeof SharedArrayBuffer === 'undefined'`. All times are ms.

| test | result | Node first | Node best of 3 | Chromium cold profile | Chromium warm (2 runs) |
|---|---|---|---|---|---|
| load and instantiate (`Z3W.create`, localhost) | | 44 | | 49 in worker, 66 page wall | 47–60 |
| (a) QF_BV sat, `get-model` and `get-value` | sat with model | 131 | 60 | 149 | 71–83 |
| (b) QF_LIA unsat (2x+4y=7), push/pop, then sat plus `get-value` | unsat, sat | 16 | 1.9 | 18 | 2.5–2.7 |
| (c) QF_ABV byte-array memory, unaligned LE load32 over store32, model, then unsat under push | sat (model `w=#xcafe....`), unsat | 8.8 | 2.5 | 11.6 | 2.9–3.3 |
| (d) NIA: `0<=n`, `r*r<=n<(r+1)^2`, same for `s`, `r!=s` | **unsat (decided)** | 51 | 19 | 62 | 21 |
| (d2) NIA: same hypotheses together with `r<0` | **unsat (decided)** | 5.4 | 5.3 | 5.9 | 5.5–5.7 |
| (e) `:rlimit 2000000` on pigeonhole PHP(11,10), then `(reset)` and a trivial query | **unknown** (`reason-unknown "canceled"`), then sat | 1611 | 1571 | 1590 | 1580–1585 |
| (f1) bounded forall over `a[0..16)`, expanded into 16 equalities | unsat, sat `k=7` | 11 | 8.2 | 12.6 | 8.4–8.7 |
| (f2) the same as a `forall` with a pattern | unsat, sat `k=7` (E-matching/MBQI) | 64 | 44 | 86 | 48–51 |
| (h, extra) `:timeout 300` (polling timer) on PHP(11,10) | unknown | 374 | 374 | 426 | 423–431 |
| (i, extra) 20,000-deep nested term | sat | 31 | 26 | 46 | 46–48 |
| (g, extra) undeclared constant | `error:(error "line 1 column 33: unknown constant zz")` | 0.8 | 0.4 | 0.9 | 0.8–0.9 |
| stateful: `(push)` in one `eval`, `(pop)` in a later `eval` | works | <1 | | <1 | <1 |

"First" includes V8 tier-up, from Liftoff to TurboFan. Expect the first heavy query on a
page to run about 2x slower than later ones. The expanded form (f1) is about 5x faster
than the quantified form (f2), and both are decided. At this size either works, but
expanding bounded quantifiers is the safer default.

Other observations (`build/test/edge*.mjs`, `build/test/deep.mjs`):

* `(check-sat-using (try-for smt 200))` works and returns unknown after about 280 ms.
* `smt.threads=4` and `parallel.enable=true` are ignored, and the query still answers sat.
* `sat.threads=4` and the `par-or` tactic return **unknown**. Do not use them.
* After an rlimit-exhausted `check-sat`, the context stays usable. A later check with a
  larger or zero rlimit does real work and can return unsat.
* Rough rlimit calibration: about 1–1.3 M rlimit units per second on SAT-heavy work in
  Chromium and Node. The rate varies by theory, so calibrate on your own obligations.

## Limitations

* **Single-threaded and synchronous.** `check-sat` blocks the worker. Nothing can
  interrupt it from outside, because `Z3_interrupt` would need a second thread or shared
  memory. Bound every query with `(set-option :rlimit N)`, which is deterministic and
  reproducible across machines, and optionally `:timeout`, which uses wall-clock polling
  and is not reproducible. As a last resort, `worker.terminate()` and respawn the worker.
  That costs about 50–150 ms plus a cache hit on the wasm.
* Parallel features (`sat.threads>1`, `par-or`, `par-then`, the parallel tactic) do not
  work and return unknown. `smt.threads` is ignored.
* Output is returned only after the whole SMT-LIB text has run; nothing streams. After an
  error, Z3 still executes the remaining commands. `eval` then returns `"error:"` followed
  by the full output, including results printed after the error.
* **Error line and column numbers accumulate across `eval` calls on the same context.**
  Z3 reuses one SMT-LIB parser per context, so positions count from the context's
  creation or last `reset()`, not from the start of the current text. In the API example
  above, `column 72` is 59 characters from the first call plus 13. To map errors back to
  editor source, either `reset()` before each document or keep a running line and column
  offset.
* `reset()` recreates the context, so options set with `set-option` must be sent again.
  `(reset)` inside the SMT-LIB text also works.
* Memory grows up to 4 GB, starting at 64 MB. Out-of-memory surfaces as a Z3 error or a
  trap. A trap surfaces in JS as a catchable `WebAssembly.RuntimeError`. The instance is then
  dead, but a new `Z3W.create()` works; this was verified by forcing an out-of-bounds
  access. The worker rebuilds its instance automatically.
* There is no filesystem (`FILESYSTEM=0`), so `(include "file")` cannot read anything.
  Pass all text through `eval`.
* Browser support is bounded by wasm exception handling and module workers: Chrome 95+,
  Firefox 114+ (module workers), Safari 15.2+. Only Chromium 154 and Node 26 were tested.
* Download size is about 3.6 MB gzip. Serve it from the same origin. Emscripten uses
  `WebAssembly.instantiateStreaming`, which requires the `application/wasm` MIME type;
  GitHub Pages provides that.
