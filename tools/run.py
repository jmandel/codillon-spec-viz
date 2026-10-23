import json, sys
from interp import Machine, Trap, SpecFail, StepLimit, apply_edits
import specs

def run(prog_file, spec, calls, edits=(), spec_override=None, limit=100_000, record=True):
    src = apply_edits(open(prog_file).read(), edits)
    sp = dict(spec)
    if spec_override: sp.update(spec_override)
    m = Machine(src, sp, step_limit=limit, record=record)
    outs = []; status = 'ok'
    try:
        for fn, args in calls:
            outs.append((fn, args, m.call(fn, args)))
    except Trap as t: status = f'trap: {t}'
    except StepLimit as s: status = f'step limit {s}'
    fails = [c for c in m.checks if not c['ok']]
    return m, outs, status, fails

if __name__ == '__main__':
    def show(title, *a, **k):
        m, outs, status, fails = run(*a, **k)
        print(f'--- {title}: steps={m.step} status={status}')
        for o in outs: print('   ', o)
        print('    first failing checks:', fails[:3], f'(total {len(fails)})')
        return m
    P = specs
    # parity
    for x in [0, 1, 2, 3, -4, -3, 2147483647, -2147483648]:
        show(f'parity half_or_neg1({x})', 'parity.rwat', P.PARITY, [('$half_or_neg1', [x])])
