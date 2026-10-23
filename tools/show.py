import sys, specs
from run import run
from bugs import BUGS
def mv(m): return [[specs.st(m,s), specs.key(m,s), specs.val(m,s)] for s in range(8)]
def go(name, start=0, end=10**9, hash_=False):
    b = BUGS[name]
    from interp import Machine, apply_edits, Trap, StepLimit
    src = apply_edits(open(b['prog']).read(), b.get('edits', ()))
    sp = dict(b['spec']); sp.update(b.get('spec_override') or {})
    m = Machine(src, sp, step_limit=b.get('limit', 100000))
    if hash_: m.mem_view = mv
    st='ok'
    try:
        for fn, args in b['calls']: print('CALL', fn, args, '->', m.call(fn, args))
    except Exception as e: st = repr(e)
    ck = {}
    for c in m.checks: ck.setdefault(c['step'], []).append(c)
    for e in m.log:
        if start <= e['step'] <= end:
            loc = {k.lstrip('$'): v for k, v in e['locals'].items()}
            extra = ''
            if hash_: extra = f" used={e['globals'].get('$used')} M={e['M']} slots={[tuple(x) for x in e['slots'] if x!=[0,0,0]] }"
            fl = [f"{c['kind']}@{c['line']}:{'ok' if c['ok'] else 'FAIL'}" for c in ck.get(e['step'], [])]
            print(f"{e['step']:4} {e['func']:14} L{e['line']:<3} {e['instr']:28} stack={e['stack']} {loc}{extra} {' '.join(fl)}")
    print('status', st)
    return m
if __name__ == '__main__':
    name = sys.argv[1]; a = int(sys.argv[2]) if len(sys.argv) > 2 else 0; z = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    go(name, a, z, hash_=name.startswith('H'))
