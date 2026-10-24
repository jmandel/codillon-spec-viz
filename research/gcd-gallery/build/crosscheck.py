import re, math, glob, html
def texts(p):
    s = open(p).read()
    out = []
    for m in re.finditer(r'<text\b[^>]*>(.*?)</text>', s, re.S):
        t = re.sub(r'<[^>]+>', '', m.group(1)); out.append(html.unescape(t))
    return out
def divs(n): return [d for d in range(1, n+1) if n % d == 0]
bad = []; n_ok = {'div':0,'gcd':0,'mod':0,'eq':0}
files = sorted(glob.glob('fixed/*/fig-*.svg')) + sorted(glob.glob('regen/05/fig-*.svg'))
for p in files:
    for t in texts(p):
        t2 = t.replace('−','-').replace(' ',' ')
        for m in re.finditer(r'Div\((\d+)\)\s*∩\s*Div\((\d+)\)\s*=\s*\{([\d,\s]+)\}', t2):
            a, b = int(m.group(1)), int(m.group(2)); got = [int(x) for x in re.findall(r'\d+', m.group(3))]
            want = sorted(set(divs(a) if a else range(1, 10**4)) & set(divs(b) if b else range(1, 10**4)))
            if got != want: bad.append((p, 'Cap', t))
            else: n_ok['cap'] = n_ok.get('cap', 0) + 1
        for m in re.finditer(r'(?<!∩ )(?<!∩)Div\((\d+)\)\s*=\s*\{([\d,\s]+)\}', t2):
            n = int(m.group(1)); got = [int(x) for x in re.findall(r'\d+', m.group(2))]
            if got != divs(n): bad.append((p, 'Div', t))
            else: n_ok['div'] += 1
        for m in re.finditer(r'Gcd\((\d+),\s*(\d+)\)\s*=\s*\{\s*(\d+)\s*\}', t2):
            a, b, g = map(int, m.groups())
            if math.gcd(a, b) != g: bad.append((p, 'Gcd', t))
            else: n_ok['gcd'] += 1
        for m in re.finditer(r'(\d+)\s*mod\s*(\d+)\s*=\s*(\d+)', t2):
            a, b, r = map(int, m.groups())
            if b == 0 or a % b != r: bad.append((p, 'mod', t))
            else: n_ok['mod'] += 1
        for m in re.finditer(r'(\d+)\s*[·*]\s*\((-?\d+)\)\s*\+\s*(\d+)\s*[·*]\s*\((-?\d+)\)\s*=\s*(?:-?\d+\s*\+\s*\d+\s*=\s*)?\+?(-?\d+)', t2):
            a, x, b, y, v = map(int, m.groups())
            if a*x + b*y != v: bad.append((p, 'bez', t))
            else: n_ok['eq'] += 1
print(n_ok); print(len(bad)); [print(b) for b in bad[:40]]
