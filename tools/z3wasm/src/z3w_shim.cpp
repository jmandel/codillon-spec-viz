// Minimal C shim over Z3's C API for a single-threaded wasm build.
// Exports z3w_new / z3w_eval / z3w_reset / z3w_free.
#include <z3.h>
#include <exception>
#include <new>
#include <string>
#include <emscripten/emscripten.h>

struct z3w {
    Z3_context ctx = nullptr;
    std::string out;  // last result; pointer returned to JS stays valid until next call
};

static Z3_context z3w_mk_ctx() {
    Z3_config cfg = Z3_mk_config();
    Z3_set_param_value(cfg, "model", "true");
    Z3_context c = Z3_mk_context(cfg);
    Z3_del_config(cfg);
    // The default handler printf()s and exit(1)s; we inspect error codes instead.
    Z3_set_error_handler(c, nullptr);
    return c;
}

extern "C" {

EMSCRIPTEN_KEEPALIVE z3w* z3w_new(void) {
    try {
        z3w* w = new z3w();
        w->ctx = z3w_mk_ctx();
        return w;
    } catch (...) {
        return nullptr;
    }
}

EMSCRIPTEN_KEEPALIVE const char* z3w_eval(z3w* w, const char* smtlib2) {
    if (!w || !w->ctx) return "error:no context";
    try {
        Z3_string r = Z3_eval_smtlib2_string(w->ctx, smtlib2 ? smtlib2 : "");
        Z3_error_code ec = Z3_get_error_code(w->ctx);
        if (ec != Z3_OK) {
            std::string msg = Z3_get_error_msg(w->ctx, ec);
            w->out = "error:" + msg;
        } else {
            w->out = r ? r : "";
        }
    } catch (std::bad_alloc&) {
        w->out = "error:out of memory";
    } catch (std::exception& e) {
        w->out = std::string("error:") + e.what();
    } catch (...) {
        w->out = "error:unknown exception";
    }
    return w->out.c_str();
}

// Drops all declarations, assertions, scopes and options by recreating the context.
EMSCRIPTEN_KEEPALIVE int z3w_reset(z3w* w) {
    if (!w) return -1;
    try {
        if (w->ctx) Z3_del_context(w->ctx);
        w->ctx = z3w_mk_ctx();
        w->out.clear();
        return 0;
    } catch (...) {
        w->ctx = nullptr;
        return -1;
    }
}

EMSCRIPTEN_KEEPALIVE void z3w_free(z3w* w) {
    if (!w) return;
    try { if (w->ctx) Z3_del_context(w->ctx); } catch (...) {}
    delete w;
}

EMSCRIPTEN_KEEPALIVE const char* z3w_version(void) {
    static std::string v;
    if (v.empty()) v = Z3_get_full_version();
    return v.c_str();
}

}
