import sys
from xcheck import xcheck
from bugs import BUGS
sel = sys.argv[1:] or list(BUGS)
for name in sel:
    b = BUGS[name]
    m, mine, real, status, fails = xcheck(b['prog'], b['spec'], b['calls'], b.get('edits', ()), tag=name, spec_override=b.get('spec_override'), limit=b.get('limit', 100_000))
    print(f'=== {name}: status={status} steps={m.step}\n   interp={mine}\n   wasm  ={real}')
    for f in fails[:4]: print('   FAIL', f)
    print('   #fails', len(fails))
