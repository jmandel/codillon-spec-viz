// usage: node runwasm.mjs file.wasm '[["fn",[args]],...]'  -> JSON results (or trap message)
import fs from 'fs';
const [,, file, callsJson] = process.argv;
const { instance } = await WebAssembly.instantiate(fs.readFileSync(file));
const out = [];
for (const [fn, args] of JSON.parse(callsJson)) {
  try { out.push(instance.exports[fn.replace('$','')](...args)); }
  catch (e) { out.push('TRAP: ' + e.message); break; }
}
console.log(JSON.stringify(out));
