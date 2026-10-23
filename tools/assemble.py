import json, data
OUT = '/home/jmandel/hobby/codalon-dependent-viz/research/03-sample-programs.md'
def esc(s): return str(s).replace('|', '\\|')
def listing(f):
    lines = open(f).read().rstrip('\n').split('\n')
    return '```wat\n' + '\n'.join(f'{i:3}  {t}' for i, t in enumerate(lines, 1)) + '\n```'
def obl(rows):
    out = ['| lines | code | refined stack / facts after | obligation | status | why |', '|---|---|---|---|---|---|']
    for r in rows:
        ls = r['lines']; L = str(ls[0]) if len(ls) == 1 else f'{ls[0]}–{ls[-1]}'
        out.append(f"| {L} | `{esc(r['code'])}` | {('`'+esc(r['stack'])+'`') if r['stack'] else ''} | {esc(r['obligation'])} | **{r['status']}** | {esc(r['why'])} |")
    return '\n'.join(out)
fx = json.load(open('fixture.json'))
hb = next(b for p in fx['programs'] for b in p['bugs'] if b['id'] == 'Hb')
NOTES = {17: 'insert(3,30): find(3) probes slot 3: EMPTY', 22: 'find(3) → -1 (absent)', 46: 'insert: first EMPTY on 3\'s path is slot 3',
         56: 'slot 3 written', 61: 'insert returns 1; R holds', 78: 'insert(11,110): find(11) probes slot 3: FULL', 87: 'key 3 ≠ 11, keep probing',
         108: 'slot 4: EMPTY', 113: 'find(11) → -1', 137: 'insert: slot 3 non-EMPTY, skip', 155: 'slot 4 EMPTY', 165: 'slot 4 written (collision resolved)',
         170: 'insert returns 1; R holds', 187: 'delete(3): find(3) probes slot 3: FULL', 196: 'key 3 matches', 202: 'find(3) → 3',
         217: 'slot 3 := TOMB. R still true; (iii)-strong now FALSE (11\'s path 3→4 has a non-FULL slot)', 218: 'delete returns 1; R holds',
         235: 'lookup(11): find(11) loads slot 3 state = 2 (TOMB)', 237: 'BUG line 38: 2 != 1 → 1 ("treat as EMPTY")', 240: 'find returns -1',
         241: '✗ find\'s result refinement fails: 11 ∈ M', 247: '✗ lookup ensures fails: returns -1, M[11] = 110'}
rows = ['| step | fn:line | op | stack | slots (non-EMPTY) | M | used | (iii)-strong | note |', '|---|---|---|---|---|---|---|---|---|']
for f in hb['trace']:
    sl = ' '.join(f'{i}:{s}' for i, s in enumerate(f['slots']) if s[0] != 0).replace(' ', '')
    sl = ', '.join(f'{i}:[{s[0]},{s[1]},{s[2]}]' for i, s in enumerate(f['slots']) if s[0] != 0)
    M = '{' + ', '.join(f'{k}↦{v}' for k, v in f['M']) + '}'
    rows.append(f"| {f['s']} | {f['fn']}:{f['ln']} | `{f['op'].replace('  ', ' ')}` | {f['stack']} | {sl or '—'} | {M} | {f['used']} | {'✓' if f['iii_strong'] else '✗'} | {NOTES.get(f['s'], '')} |")
HB = '\n'.join(rows)
missing = [f['s'] for f in hb['trace'] if f['s'] not in NOTES]
assert not missing, missing
doc = ''.join(open(f'tpl/{n}').read() for n in ['00-intro.md', '10-partA.md', '20-partB.md', '30-partC.md'])
for k, v in {'{{LISTING:parity}}': listing('parity.rwat'), '{{LISTING:isqrt}}': listing('isqrt.rwat'), '{{LISTING:gcd}}': listing('gcd.rwat'),
             '{{LISTING:powmod}}': listing('powmod.rwat'), '{{LISTING:hash}}': listing('hash.rwat'),
             '{{OBL:parity}}': obl(data.PARITY_OBL), '{{OBL:isqrt}}': obl(data.ISQRT_OBL), '{{OBL:gcd}}': obl(data.GCD_OBL),
             '{{OBL:powmod}}': obl(data.POWMOD_OBL), '{{OBL:hash}}': obl(data.HASH_OBL), '{{HBTABLE}}': HB,
             '{{FIXTURE}}': open('fixture.json').read()}.items():
    assert k in doc, k
    doc = doc.replace(k, v)
assert '{{' not in doc
open(OUT, 'w').write(doc)
print(len(doc), doc.count('\n'))
