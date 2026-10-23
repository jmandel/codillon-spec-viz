import json, re
from interp import Machine, apply_edits, Trap, StepLimit
import specs, data
from bugs import BUGS

def mv(m): return [[specs.st(m, s), specs.key(m, s), specs.val(m, s)] for s in range(8)]

def R_snap(slots, M, used):
    S = [x[0] for x in slots]
    h = lambda k: k & 7; at = lambda k, d: (h(k) + d) & 7; dist = lambda k, s: (s - h(k)) & 7
    r = {}
    r['o'] = all(x in (0, 1, 2) for x in S)
    r['i'] = all(slots[s][1] in M and M[slots[s][1]] == slots[s][2] for s in range(8) if S[s] == 1)
    r['ii'] = all(sum(1 for s in range(8) if S[s] == 1 and slots[s][1] == k) == 1 for k in M)
    r['iii'] = all(all(S[at(slots[s][1], d)] != 0 for d in range(dist(slots[s][1], s) + 1)) for s in range(8) if S[s] == 1)
    r['iv'] = sum(1 for x in S if x == 1) == len(M) and used == sum(1 for x in S if x != 0) and used < 8
    # strengthened (iii): no non-FULL slot on any key's probe path (what a lookup that stops at TOMB silently assumes)
    r['iii_strong'] = all(all(S[at(slots[s][1], d)] == 1 for d in range(dist(slots[s][1], s) + 1)) for s in range(8) if S[s] == 1)
    return r

def execute(b, limit=None, hashprog=False):
    src = apply_edits(open(b['prog']).read(), b.get('edits', ()))
    sp = dict(b['spec']); sp.update(b.get('spec_override') or {})
    m = Machine(src, sp, step_limit=limit or b.get('limit', 100_000))
    if hashprog: m.mem_view = mv
    outs = []; status = 'ok'; boundaries = []
    try:
        for fn, args in b['calls']:
            outs.append(m.call(fn, args)); boundaries.append((fn, args, m.step))
    except Trap as t:
        status = 'trap: ' + str(t)
        fn, ln, txt, stack, env = m.cur
        m.log.append({'step': m.step, 'func': fn, 'line': ln, 'instr': txt, 'stack': stack, 'locals': env,
                      'globals': dict(m.globals), 'M': dict(m.ghost['M']), 'trap': str(t),
                      **({'slots': mv(m)} if hashprog else {})})
    except StepLimit as s:
        status = f'no termination within {limit or b.get("limit", 100_000)} steps'
    return m, outs, status, boundaries

def frame(e, checks, hashprog, extra_R=False, boundary_steps=()):
    f = {'s': e['step'], 'fn': e['func'].lstrip('$'), 'ln': e['line'], 'op': e['instr'],
         'stack': e['stack'], 'loc': {k.lstrip('$'): v for k, v in e['locals'].items()}}
    if hashprog:
        f['used'] = e['globals']['$used']; f['M'] = sorted([[k, v] for k, v in e['M'].items()])
        f['slots'] = e['slots']
        R = R_snap(e['slots'], e['M'], e['globals']['$used'])
        if e['step'] in boundary_steps:
            f['R'] = {k: v for k, v in R.items() if k != 'iii_strong'}
        if extra_R: f['iii_strong'] = R['iii_strong']
    if 'trap' in e: f['trap'] = e['trap']
    cs = [c for c in checks if c['step'] == e['step']]
    if cs: f['checks'] = [{'ln': c['line'], 'kind': c['kind'], 'ok': c['ok']} for c in cs]
    return f
