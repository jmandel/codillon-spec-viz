#!/usr/bin/env node
// Erase, assemble, validate and run every example's harnesses (design 16 §6.3).
// usage: node tools/run.mjs [name.expect.json ...]      (default: every *.expect.json in the examples dir)
// Needs python3 and wasm-tools (WASM_TOOLS env var, default ~/.cargo/bin/wasm-tools).
import { execFileSync } from "node:child_process";
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from "node:fs";
import { join, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const here = dirname(fileURLToPath(import.meta.url));
const exdir = join(here, "..");
const wt = process.env.WASM_TOOLS ?? join(homedir(), ".cargo/bin/wasm-tools");
const out = process.env.ERASED_DIR ?? join(homedir(), "hobby/.agent-scratch/codalon-viz/v2design/erased");
mkdirSync(out, { recursive: true });

// ---- inputs: edge values first, then a deterministic pseudo-random sample ----
const EDGE32 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 17, 25, 36, 97, 100, 1000, 46340, 46341, 65535, 65536,
  2147395600, 2147483646, 2147483647, -1, -2, -3, -4, -5, -7, -8, -2147483648, -2147483647, 4294836225 | 0, 4294967294 | 0];
let seed = 0x9e3779b9;
function rnd32() { seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5; seed >>>= 0; return seed | 0; }
function smallRnd() { return (rnd32() >>> 0) % 200; }
function inputs(types, n) {
  const res = [];
  const conv = (t, x) => (t === "i64" ? BigInt.asIntN(64, BigInt(x)) : x | 0);
  if (types.length === 1) {
    for (const e of EDGE32) res.push([conv(types[0], e)]);
    for (let i = 0; i < n; i++) res.push([conv(types[0], i % 2 ? rnd32() : smallRnd())]);
  } else {
    const small = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 18, 30, 97, -1, 2147483647, -2147483648];
    const rec = (k, acc) => {
      if (k === types.length) { res.push(acc); return; }
      for (const e of small) rec(k + 1, [...acc, conv(types[k], e)]);
    };
    if (types.length <= 3) rec(0, []);
    for (let i = 0; i < n; i++) res.push(types.map((t) => conv(t, i % 3 ? smallRnd() : rnd32())));
  }
  return res;
}

function paramTypes(watText, exportName) {
  const line = watText.split("\n").find((l) => l.includes(`(export "${exportName}")`));
  if (!line) throw new Error(`no export ${exportName}`);
  return [...line.matchAll(/\(param\s+\$\S+\s+\(?(i32|i64)[\s)]/g)].map((m) => m[1]);
}

function call(inst, name, args) {
  try { inst.exports[name](...args); return "ok"; }
  catch (e) {
    if (!(e instanceof WebAssembly.RuntimeError)) throw e;
    const m = e.message;
    if (/unreachable/.test(m)) return "unreachable";
    if (/divi|remainder/.test(m)) return "div-by-zero";
    if (/out of bounds/.test(m)) return "oob";
    return "trap:" + m;
  }
}

const files = process.argv.slice(2).length ? process.argv.slice(2)
  : readdirSync(exdir).filter((f) => f.endsWith(".expect.json")).sort();
let failures = 0;
for (const f of files) {
  const expect = JSON.parse(readFileSync(join(exdir, basename(f)), "utf8"));
  const src = join(exdir, expect.source);
  const srcText = readFileSync(src, "utf8");
  const erased = join(out, expect.source.replace(/\.wat$/, ".erased.wat"));
  const wasm = erased.replace(/\.wat$/, ".wasm");
  execFileSync("python3", ["-I", join(here, "erase.py"), src, erased]);
  const nIn = srcText.split("\n").length, nOut = readFileSync(erased, "utf8").split("\n").length;
  execFileSync(wt, ["parse", erased, "-o", wasm]);
  execFileSync(wt, ["validate", wasm]);
  const { instance } = await WebAssembly.instantiate(readFileSync(wasm), {});
  const lines = [`${expect.source}: erased ${nIn}→${nOut} lines, parse+validate ok`];
  if (nIn !== nOut) { lines.push("  LINE COUNT MISMATCH"); failures++; }
  for (const r of expect.runs ?? []) {
    const types = paramTypes(srcText, r.export);
    if (r.args) {
      const args = r.args.map((a, i) => (types[i] === "i64" ? BigInt(a) : a | 0));
      const got = call(instance, r.export, args);
      const ok = got === r.expect;
      if (!ok) failures++;
      lines.push(`  ${ok ? "ok  " : "FAIL"} ${r.export}(${r.args.join(", ")}) → ${got} (expected ${r.expect})`);
    } else {
      let ins = inputs(types, r.samples ?? 300);
      if (r.domain) {   // run-time domain only (keeps slow spec predicates cheap); the theorem is still for all inputs
        const [lo, hi] = r.domain, span = BigInt(hi - lo + 1);
        ins = ins.map((a) => a.map((x, i) => {
          const v = BigInt(lo) + (BigInt.asUintN(64, BigInt(x)) % span);
          return types[i] === "i64" ? v : Number(v) | 0;
        }));
      }
      let first = null, count = 0;
      for (const a of ins) {
        const got = call(instance, r.export, a);
        if (got !== "ok") { count++; first ??= [a, got]; }
      }
      const ok = r.expect === "pass" ? count === 0 : count > 0;
      if (!ok) failures++;
      const firstTxt = first ? `; first: (${first[0].join(", ")}) → ${first[1]}` : "";
      lines.push(`  ${ok ? "ok  " : "FAIL"} ${r.export} on ${ins.length} inputs: ${count} traps${firstTxt} (expected ${r.expect})`);
    }
  }
  console.log(lines.join("\n"));
}
console.log(failures ? `${failures} FAILURE(S)` : "all ok");
process.exit(failures ? 1 : 0);
