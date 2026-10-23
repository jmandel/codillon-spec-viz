import math
from interp import s32, u32

def gcd_spec(x, y):
    while y: x, y = y, x % y
    return x

PARITY = {
    1: {'ensures': lambda m, e, o: e['result'] == (1 if e['$x'] % 2 == 0 else 0)},
    7: {'requires': lambda m, e: e['$x'] % 2 == 0,
        'ensures': lambda m, e, o: e['result'] + e['result'] == e['$x']},
    12: {'ensures': lambda m, e, o: (e['$x'] % 2 == 0 and 2 * e['result'] == e['$x']) or (e['$x'] % 2 == 1 and e['result'] == -1)},
    19: lambda m, e: e['$x'] % 2 == 0,
}
ISQRT = {
    1: {'requires': lambda m, e: e['$n'] >= 0,
        'ensures': lambda m, e, o: 0 <= e['result'] and e['result'] ** 2 <= e['$n'] < (e['result'] + 1) ** 2},
    7: lambda m, e: 0 <= e['$r'] and e['$r'] ** 2 <= e['$n'],
    8: lambda m, e: e['$n'] - e['$r'] ** 2,
}
GCD = {
    2: {'requires': lambda m, e: e['$a'] >= 0 and e['$b'] >= 0,
        'ensures': lambda m, e, o: e['result'] == gcd_spec(e['$a'], e['$b'])},
    12: lambda m, e: e['$x'] >= 0 and e['$y'] >= 0 and gcd_spec(e['$x'], e['$y']) == gcd_spec(e['$a'], e['$b']),
    13: lambda m, e: e['$y'],
}
POWMOD = {
    2: {'requires': lambda m, e: e['$b'] >= 0 and e['$e'] >= 0 and 1 <= e['$m'] <= 65536,
        'ensures': lambda m, e, o: 0 <= e['result'] < e['$m'] and e['result'] == pow(e['$b'], e['$e'], e['$m'])},
    18: lambda m, e: 0 <= e['$acc'] < e['$m'] and 0 <= e['$base'] < e['$m'] and e['$k'] >= 0,
    19: lambda m, e: (e['$acc'] * pow(e['$base'], e['$k'], e['$m'])) % e['$m'] == pow(e['$b'], e['$e'], e['$m']),
    20: lambda m, e: e['$k'],
}

# ---- hash table ----
BASE = 65440
def st(m, s): return m.load(BASE + 12 * s)
def key(m, s): return m.load(BASE + 12 * s + 4)
def val(m, s): return m.load(BASE + 12 * s + 8)
def h(k): return k & 7
def at(k, d): return (h(k) + d) & 7
def dist(k, s): return (s - h(k)) & 7
def R_clauses(m):
    M = m.ghost['M']; used = m.globals['$used']
    S = [st(m, s) for s in range(8)]
    r0 = all(x in (0, 1, 2) for x in S)
    r1 = all(key(m, s) in M and M[key(m, s)] == val(m, s) for s in range(8) if S[s] == 1)
    r2 = all(sum(1 for s in range(8) if S[s] == 1 and key(m, s) == k) == 1 for k in M)
    r3 = all(all(S[at(key(m, s), d)] != 0 for d in range(dist(key(m, s), s) + 1)) for s in range(8) if S[s] == 1)
    r4 = (sum(1 for x in S if x == 1) == len(M) and used == sum(1 for x in S if x != 0) and used < 8)
    return {'R0': r0, 'R1': r1, 'R2': r2, 'R3': r3, 'R4': r4}
def R(m): return all(R_clauses(m).values())

def path_ok_find(m, e):
    k = e['$k']
    for d in range(e['$j']):
        s = at(k, d)
        if not (st(m, s) == 2 or (st(m, s) == 1 and key(m, s) != k)): return False
    return True

HASH = {
    13: {'requires': lambda m, e: 0 <= e['$i'] < 8,
         'ensures': lambda m, e, o: e['result'] == BASE + 12 * e['$i']},
    20: {'ensures': lambda m, e, o: (e['result'] == -1 and e['$k'] not in m.ghost['M']) or
         (0 <= e['result'] < 8 and st(m, e['result']) == 1 and key(m, e['result']) == e['$k'])},
    21: lambda m, e: R(m),
    30: lambda m, e: 0 <= e['$j'] <= m.globals['$used'] and e['$i'] == at(e['$k'], e['$j']),
    31: path_ok_find,
    32: lambda m, e: 8 - e['$j'],
    62: lambda m, e: e.__setitem__('$j', e['$j'] + 1),
    67: {'ensures': lambda m, e, o: e['result'] == m.ghost['M'].get(e['$k'], e['$dflt'])},
    68: lambda m, e: R(m),
    69: lambda m, e, o: R(m),
    84: {'ensures': lambda m, e, o: e['result'] == (1 if e['$k'] in o['M'] else 0)},
    85: lambda m, e: R(m),
    86: lambda m, e, o: R(m) and m.ghost['M'] == {k: v for k, v in o['M'].items() if k != e['$k']},
    101: lambda m, e: m.ghost['M'].pop(e['$k'], None),
    104: {'ensures': lambda m, e, o: e['result'] == 1 or (e['result'] == 0 and e['$k'] not in m.ghost['M'] and m.globals['$used'] == 7)},
    105: lambda m, e: R(m),
    106: lambda m, e, o: R(m) and m.ghost['M'] == ({**o['M'], e['$k']: e['$x']} if e['result'] == 1 else o['M']),
    120: lambda m, e: m.ghost['M'].__setitem__(e['$k'], e['$x']),
    136: lambda m, e: e['$k'] not in m.ghost['M'] and 0 <= e['$j'] <= m.globals['$used'] and e['$i'] == at(e['$k'], e['$j']),
    137: lambda m, e: all(st(m, at(e['$k'], d)) != 0 for d in range(e['$j'])),
    138: lambda m, e: 8 - e['$j'],
    150: lambda m, e: e.__setitem__('$j', e['$j'] + 1),
    167: lambda m, e: m.ghost['M'].__setitem__(e['$k'], e['$x']),
}
