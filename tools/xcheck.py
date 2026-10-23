import json, subprocess, sys, os
from run import run
from interp import apply_edits
import erase, specs
B='/home/jmandel/.local/opt/binaryen-version_133/bin/wasm-opt'
def build(prog, edits, tag):
    src = apply_edits(open(prog).read(), edits)
    wat = erase.erase(src)
    import re
    funcs = re.findall(r'\(func (\$\w+)', wat)
    exports = '\n'.join(f'(export "{f[1:]}" (func {f}))' for f in funcs)
    open(f'build/{tag}.wat','w').write('(module\n'+wat+'\n'+exports+'\n)')
    r = subprocess.run([B, f'build/{tag}.wat', '-o', f'build/{tag}.wasm'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return f'build/{tag}.wasm'
def node(wasm, calls):
    r = subprocess.run(['node', 'runwasm.mjs', wasm, json.dumps(calls)], capture_output=True, text=True, timeout=20)
    return json.loads(r.stdout)
def xcheck(prog, spec, calls, edits=(), tag='t', spec_override=None, limit=100_000):
    os.makedirs('build', exist_ok=True)
    w = build(prog, edits, tag)
    m, outs, status, fails = run(prog, spec, calls, edits, spec_override, limit=limit)
    mine = [o[2] for o in outs] + ([] if status == 'ok' else [status])
    try: real = node(w, calls)
    except subprocess.TimeoutExpired: real = ['TIMEOUT(node)']
    return m, mine, real, status, fails
