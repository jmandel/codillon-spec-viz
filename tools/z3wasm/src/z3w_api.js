
// ---- z3w high-level API (appended after the emscripten module factory) ----
// import { Z3W } from './z3w.js';
// const z3 = await Z3W.create();  z3.eval('(declare-const x Int)(assert (> x 2))(check-sat)(get-model)');
export const Z3W = {
  /**
   * Instantiate a fresh wasm module and one Z3 context.
   * @param {object} [moduleArg] optional emscripten Module overrides (e.g. { locateFile, wasmBinary, print, printErr }).
   * @returns {Promise<{eval(text:string):string, reset():void, free():void, version:string, module:object}>}
   */
  async create(moduleArg = {}) {
    const M = await z3wModule(moduleArg);
    const h = M._z3w_new();
    if (!h) throw new Error('z3w_new failed');
    let live = true;
    const check = () => { if (!live) throw new Error('z3w context already freed'); };
    return {
      module: M,
      version: M.UTF8ToString(M._z3w_version()),
      /** Evaluate SMT-LIB2 text; returns Z3's output, or "error:<message>" on a Z3 error. */
      eval(text) {
        check();
        const n = M.lengthBytesUTF8(text) + 1;
        const p = M._malloc(n);
        if (!p) throw new Error('z3w: malloc failed');
        try {
          M.stringToUTF8(text, p, n);
          return M.UTF8ToString(M._z3w_eval(h, p));
        } finally {
          M._free(p);
        }
      },
      /** Drop all declarations, assertions, scopes and options (fresh context). */
      reset() { check(); if (M._z3w_reset(h) !== 0) throw new Error('z3w_reset failed'); },
      free() { if (live) { live = false; M._z3w_free(h); } },
    };
  },
};
