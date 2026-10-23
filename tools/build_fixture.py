import json, re
import gen, data, specs
from bugs import BUGS
from bugmeta import META

PROGS = [
 ('parity', 'parity.rwat', 'Parity gate: is_even / half / half_or_neg1', data.PARITY_OBL, specs.PARITY),
 ('isqrt', 'isqrt.rwat', 'Integer square root (linear search)', data.ISQRT_OBL, specs.ISQRT),
 ('gcd', 'gcd.rwat', 'Euclid gcd', data.GCD_OBL, specs.GCD),
 ('pow_mod', 'powmod.rwat', 'Modular exponentiation (square-and-multiply)', data.POWMOD_OBL, specs.POWMOD),
 ('hashtable', 'hash.rwat', 'Open-addressing hash table (8 slots, linear probing, tombstones)', data.HASH_OBL, specs.HASH),
]
def kind(t):
    s = t.strip()
    if s.startswith('(func'): return 'func'
    if s.startswith('(@'): return 'spec'
    if s == ')': return 'close'
    if s.startswith('(local'): return 'local'
    if s.startswith('(memory') or s.startswith('(global'): return 'meta'
    return 'instr'

def select(meta, m, hashprog):
    sel = meta['sel']; log = m.log
    fails = {c['step'] for c in m.checks if not c['ok']}
    if sel == 'all': keep = log
    elif sel == 'cti': keep = [e for e in log if 4 <= e['step'] <= 19]
    elif sel == 'hb':
        want = {('$find', 36), ('$find', 41), ('$find', 48), ('$find', 54), ('$insert', 142), ('$insert', 162),
                ('$insert', 168), ('$delete', 100), ('$delete', 102), ('$lookup', 78)}
        keep = [e for e in log if (e['func'], e['line']) in want or e['step'] in fails or (e['func'] == '$find' and e['line'] == 38 and e['step'] > 218)]
        # drop the find(k)-inside-insert loads of the first insert (keep it short) except the decisive ones
    elif sel == 'hbp':
        keep = [e for e in log if e['step'] > 200 and ((e['func'], e['line']) in {('$delete', 100), ('$delete', 102), ('$find', 36), ('$find', 41), ('$lookup', 78)})]
    elif sel == 'hc':
        keep = [e for e in log if e['step'] > 34 and ((e['func'], e['line']) in {('$insert', 135), ('$insert', 142), ('$insert', 159), ('$insert', 168), ('$lookup', 82)})]
    elif sel == 'hd':
        keep = [e for e in log if (e['step'] >= 480 and ((e['func'], e['line']) in {('$insert', 166), ('$insert', 168), ('$find', 36)})) or e['step'] in fails]
        keep = [e for e in keep if e['step'] <= 800]
    else:
        keep = [e for e in log if e['line'] in sel or e['step'] in fails]
        keep.append(log[-1])
    # dedupe preserving order; ensure trap / last frame present
    seen = set(); out = []
    for e in keep + ([log[-1]] if log and 'trap' in log[-1] else []):
        if id(e) in seen: continue
        seen.add(id(e)); out.append(e)
    out.sort(key=lambda e: (e['step'], 'trap' in e))
    return out

def build():
    fixture = {'version': 1,
      'conventions': {
        'step': 'one step per executed instruction line; `block`/`loop`/`if`/`br*`/`return`/`call` count, `else`/`end` do not; a `call` takes two steps (enter: args popped; return: result pushed). Spec checks happen after the step they are attached to.',
        'values': 'i32 shown as signed decimal; predicates read them as mathematical integers (signed) unless written u(x)',
        'frame': '{s: step, fn, ln: line (1-based, in the program listing, which is the same for buggy variants because deleted lines are blanked, not removed), op, stack (after the step, bottom first), loc: locals incl. ghost, checks: spec checks evaluated at this step}',
        'hash_frame_extra': 'used: global $used; M: ghost map as [key, value] pairs; slots: 8 x [state, key, value] (0 EMPTY, 1 FULL, 2 TOMB); R: truth of each clause of the representation invariant at that instant (only REQUIRED at function boundaries; transient falsity mid-operation is normal)',
        'status': 'none = no obligation beyond Wasm typing; auto = discharged from the refined stack + path condition by linear/bit-vector reasoning; inv = needs the loop invariant or the representation invariant R; lemma = also needs a nonlinear, counting, or definitional lemma; fails = the obligation that a seeded bug breaks'},
      'programs': []}
    for pid, fname, title, obl, spec in PROGS:
        lines = open(fname).read().rstrip('\n').split('\n')
        hashprog = pid == 'hashtable'
        p = {'id': pid, 'title': title, 'lines': lines,
             'functions': [{'name': re.match(r'\s*\(func (\$\w+)', t).group(1), 'line': i + 1, 'signature': t.strip()} for i, t in enumerate(lines) if t.strip().startswith('(func')],
             'specs': [{'line': i + 1, 'text': t.strip()} for i, t in enumerate(lines) if t.strip().startswith('(@')],
             'obligations': [{k: v for k, v in o.items() if v != '' and k != 'why'} for o in obl], 'bugs': []}
        DEMO = {'parity': [('$half_or_neg1', [6]), ('$half_or_neg1', [7]), ('$half_or_neg1', [-4]), ('$is_even', [-3])],
                'isqrt': [('$isqrt', [10]), ('$isqrt', [16]), ('$isqrt', [0])],
                'gcd': [('$gcd', [12, 8]), ('$gcd', [1071, 462]), ('$gcd', [0, 5])],
                'pow_mod': [('$pow_mod', [2, 10, 1000]), ('$pow_mod', [3, 200, 65536]), ('$pow_mod', [5, 0, 1])],
                'hashtable': [('$insert', [3, 30]), ('$insert', [11, 110]), ('$delete', [3]), ('$lookup', [11, -1]), ('$lookup', [3, -1])]}[pid]
        from run import run as _run
        dm, douts, dstatus, dfails = _run(fname, spec, DEMO, record=False)
        assert dstatus == 'ok' and not dfails
        p['correct_runs'] = {'calls': [[fn.lstrip('$'), a] for fn, a in DEMO], 'results': [o[2] for o in douts], 'total_steps': dm.step, 'spec_checks_failed': 0}
        for meta in [mm for mm in META if mm['program'] == pid]:
            b = BUGS[meta['scenario']]
            m, outs, status, bounds = gen.execute(b, limit=900 if meta['id'] == 'Hd' else None, hashprog=hashprog)
            fails = [c for c in m.checks if not c['ok']]
            bsteps = {st for (_, _, st) in bounds}
            frames = [gen.frame(e, m.checks, hashprog, extra_R=(meta['id'] == 'Hb'), boundary_steps=bsteps) for e in select(meta, m, hashprog)]
            if status != 'ok': outs = outs + ['(lookup does not terminate)' if meta['id'] == 'Hd' else status]
            first = ({'s': fails[0]['step'], 'ln': fails[0]['line'], 'kind': fails[0]['kind']} if fails else None)
            if status.startswith('trap') and (first is None or first['s'] > m.step):
                first = {'s': m.step, 'ln': m.cur[1], 'kind': status}
            bug = {'id': meta['id'], 'title': meta['title'], 'category': meta['category'], 'flavor': meta['flavor'], 'edit': meta['edit'],
                   'edits': [list(e) for e in b.get('edits', [])] if meta['id'] != 'S1' else [list(e) for e in BUGS['S1']['edits']],
                   'calls': [[fn.lstrip('$'), args] for fn, args in (BUGS['S1']['calls'] if meta['id'] == 'S1' else b['calls'])],
                   'expected_results': meta['expected'],
                   'observed_results': outs if meta['id'] != 'S1' else ['(does not terminate)'],
                   'runtime': meta['runtime'], 'static_failure': {**meta['static'], 'status': 'fails'},
                   'first_dynamic_failure': first}
            if meta['id'] == 'S1': bug['first_dynamic_failure']['s'] += 695100
            if 'R_clause' in meta: bug['R_violation'] = meta['R_clause']
            if hashprog:
                bug['op_boundaries'] = [{'call': [fn.lstrip('$'), args], 'returned_at_step': st,
                                         'R_false': [k for k, v in gen.R_snap(e['slots'], e['M'], e['globals']['$used']).items() if not v and k != 'iii_strong']}
                                        for (fn, args, st) in bounds for e in [next(x for x in reversed(m.log) if x['step'] <= st)]]
            if meta['id'] == 'S1':
                bug['trace_note'] = 'counterexample-to-induction: one loop iteration from the loop-head state n = 2147483647, r = 46340 (which satisfies the invariant). Real-run step = s + 695100.'
            bug['trace'] = frames
            p['bugs'].append(bug)
        fixture['programs'].append(p)
    return fixture

def dump(o, ind=0):
    pad = ' ' * ind
    one = json.dumps(o, separators=(',', ':'), ensure_ascii=False)
    if not isinstance(o, (dict, list)) or len(one) <= 150 or (isinstance(o, dict) and 's' in o and 'ln' in o):
        return one
    if isinstance(o, list):
        return '[\n' + ',\n'.join(pad + ' ' + dump(x, ind + 1) for x in o) + '\n' + pad + ']'
    return '{\n' + ',\n'.join(pad + ' ' + json.dumps(k) + ':' + dump(v, ind + 1) for k, v in o.items()) + '\n' + pad + '}'

if __name__ == '__main__':
    fx = build()
    s = dump(fx)
    json.loads(s)
    open('fixture.json', 'w').write(s)
    for p in fx['programs']:
        for b in p['bugs']:
            print(p['id'], b['id'], 'frames', len(b['trace']), 'obs', b['observed_results'], 'first', b['first_dynamic_failure'])
            if 'op_boundaries' in b: print('    ', [(x['call'], x['returned_at_step'], x['R_false']) for x in b['op_boundaries']])
    print(len(s), 'bytes', s.count('\n'), 'lines')
