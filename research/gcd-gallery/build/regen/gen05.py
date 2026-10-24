#!/usr/bin/env python3
"""Regenerated angle-05 figures (state-space invariant). Same concept as gcdviz/05/gen.py
(Gemini 3.1 Pro), redrawn for legibility: ivory background, arrows only from shaded cells and
light, no clipped labels, honest type-error colouring. Every number is computed here."""
import math, sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "Arial Narrow, Arial, sans-serif"
PUR, PURF, NAVY, RED, INK, GRAY = '#6A5ACD', '#d9d5f2', '#00008b', '#8b0000', '#222', '#888'

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def T(x, y, s, size=13, fill=INK, anchor='start', font=SERIF, extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(s)}</text>'

def head(w, h, title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            '<defs>'
            f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 1 L9 5 L0 9 z" fill="{PUR}"/></marker>'
            f'<marker id="ahn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M0 1 L9 5 L0 9 z" fill="{NAVY}"/></marker>'
            '</defs>',
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#fffff0"/>',
            T(w / 2, 32, title, 20, INK, 'middle')]

class Grid:
    def __init__(s, X0, Y0, C, N): s.X0, s.Y0, s.C, s.N = X0, Y0, C, N
    def p(s, x, y): return s.X0 + x * s.C, s.Y0 - y * s.C

def run(a, b):
    tr = [(a, b)]
    while tr[-1][1]:
        x, y = tr[-1]; tr.append((y, x % y))
    return tr

def draw_grid(o, G, inset, weak=None, label_every=4, axes=True):
    N, C = G.N, G.C
    h = C * 0.84
    # exit row band
    x0, y0 = G.p(0, 0)
    o.append(f'<rect x="{x0 - C/2:.1f}" y="{y0 - C/2:.1f}" width="{(N + 1) * C:.1f}" height="{C:.1f}" fill="#ecebdf"/>')
    for x in range(N + 1):
        for y in range(N + 1):
            cx, cy = G.p(x, y)
            if (x, y) in inset:
                o.append(f'<rect x="{cx - h/2:.1f}" y="{cy - h/2:.1f}" width="{h:.1f}" height="{h:.1f}" rx="2" fill="{PURF}" stroke="{PUR}" stroke-width="1.1"/>')
            elif weak and (x, y) in weak:
                o.append(f'<rect x="{cx - h/2:.1f}" y="{cy - h/2:.1f}" width="{h:.1f}" height="{h:.1f}" rx="2" fill="#efedf9" stroke="{PUR}" stroke-width="0.8" stroke-dasharray="2 2"/>')
            else:
                o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.6" fill="#c8c8bc"/>')
    if axes:
        for x in range(0, N + 1, label_every):
            cx, cy = G.p(x, 0)
            o.append(T(cx, cy + C / 2 + 13, str(x), 11, GRAY, 'middle', SANS))
        for y in range(0, N + 1, label_every):
            cx, cy = G.p(0, y)
            o.append(T(cx - C / 2 - 4, cy + 4, str(y), 11, GRAY, 'end', SANS))
        cx, cy = G.p(N, 0)
        o.append(T(cx + C / 2 + 4, cy + C / 2 + 13, 'x', 13, GRAY, 'start', SERIF, ' font-style="italic"'))
        cx, cy = G.p(0, N)
        o.append(T(cx - C / 2 - 4, cy - C / 2 - 4, 'y', 13, GRAY, 'end', SERIF, ' font-style="italic"'))

def arrow(o, G, a, b, color, width, op, marker, shorten=None):
    (x1, y1), (x2, y2) = G.p(*a), G.p(*b)
    d = math.hypot(x2 - x1, y2 - y1)
    s = shorten if shorten is not None else G.C * 0.42
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    o.append(f'<line x1="{x1 + ux*s*0.6:.1f}" y1="{y1 + uy*s*0.6:.1f}" x2="{x2 - ux*s:.1f}" y2="{y2 - uy*s:.1f}" stroke="{color}" stroke-width="{width}" opacity="{op}" marker-end="url(#{marker})"/>')

def draw_run(o, G, tr):
    for i in range(len(tr) - 1):
        arrow(o, G, tr[i], tr[i + 1], NAVY, 2.6, 1, 'ahn')
    for (x, y) in tr:
        cx, cy = G.p(x, y)
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{G.C*0.3:.1f}" fill="none" stroke="{NAVY}" stroke-width="2.2"/>')

def numline(o, G, yline, lit, bad=(), label=''):
    N, C = G.N, G.C
    xa, _ = G.p(0, 0); xb, _ = G.p(N, 0)
    o.append(f'<line x1="{xa - C/2:.1f}" y1="{yline}" x2="{xb + C/2:.1f}" y2="{yline}" stroke="#bbb" stroke-width="1"/>')
    for v in range(N + 1):
        cx, _ = G.p(v, 0)
        if v in lit:
            o.append(f'<circle cx="{cx:.1f}" cy="{yline}" r="{C*0.36:.1f}" fill="{PURF}" stroke="{PUR}" stroke-width="2"/>')
            o.append(T(cx, yline + 4.5, str(v), 12.5, INK, 'middle'))
        elif v in bad:
            r = C * 0.26
            o.append(f'<path d="M{cx-r:.1f} {yline-r:.1f} L{cx+r:.1f} {yline+r:.1f} M{cx-r:.1f} {yline+r:.1f} L{cx+r:.1f} {yline-r:.1f}" stroke="{RED}" stroke-width="2"/>')
        else:
            o.append(f'<circle cx="{cx:.1f}" cy="{yline}" r="2" fill="#c8c8bc"/>')
    if label:
        o.append(T(xb + C / 2 + 8, yline + 4.5, label, 14, PUR, 'start'))

def save(name, o):
    o.append('</svg>')
    with open(os.path.join(OUT, name), 'w') as f: f.write('\n'.join(o) + '\n')

def inv(N, g): return {(x, y) for x in range(N + 1) for y in range(N + 1) if math.gcd(x, y) == g}

def divs(n): return [d for d in range(1, n + 1) if n % d == 0]

# ---------------- fig-1: the invariant set, every arrow, the exit cell -----------------
def fig1():
    a, b, N = 12, 8, 20
    g = math.gcd(a, b)
    o = head(900, 680, f'Euclid never leaves the shaded set; it exits at ({g}, 0)')
    G = Grid(66, 548, 22.5, N)
    S = inv(N, g)
    draw_grid(o, G, S)
    arrows = [((x, y), (y, x % y)) for (x, y) in sorted(S) if y > 0]
    for s, t in arrows: arrow(o, G, s, t, PUR, 1.1, 0.55, 'ah')
    tr = run(a, b); draw_run(o, G, tr)
    ex, ey = G.p(g, 0)
    o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{G.C*0.48:.1f}" fill="none" stroke="{PUR}" stroke-width="2"/>')
    # projection to the type
    yl = 618
    o.append(f'<line x1="{ex:.1f}" y1="{ey + G.C*0.5 + 17:.1f}" x2="{ex:.1f}" y2="{yl - G.C*0.38:.1f}" stroke="{PUR}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    numline(o, G, yl, {g}, label=f'Gcd({a}, {b}) ⊂ ℕ')
    xa, _ = G.p(0, 0)
    o.append(T(xa - G.C/2, yl + 32, 'the exit row y = 0 meets the shaded set in one cell; its x is the only inhabitant', 12, GRAY, 'start', SANS))
    _, y0 = G.p(0, 0)
    xb, _ = G.p(N, 0)
    o.append(T(xb + G.C/2 + 8, y0 + 4, 'exit row  y = 0', 12, GRAY, 'start', SANS))
    # side panel: computed obligations
    land = sum(1 for s, t in arrows if t in S)
    lower = sum(1 for s, t in arrows if t[1] < s[1])
    exitc = sorted(c for c in S if c[1] == 0)
    cd = sorted(set(divs(a)) & set(divs(b)))
    X = 586; y = 92
    o.append(T(X, y, 'The loop state has a type:', 15)); y += 24
    o.append(T(X, y, f'Inv = {{(x, y) | Div(x) ∩ Div(y) = {{{", ".join(map(str, cd))}}}}}', 13.5, PUR)); y += 20
    o.append(T(X, y, f'     = {{(x, y) | gcd(x, y) = {g}}}', 13.5, PUR)); y += 34
    rows = [('entry', f'({a}, {b}) is shaded', (a, b) in S),
            ('preserved', f'{land} of {len(arrows)} arrows land shaded', land == len(arrows)),
            ('decreasing', f'{lower} of {len(arrows)} arrows go to a lower row', lower == len(arrows)),
            ('exit', 'shaded ∩ {y = 0} = {' + ', '.join(f'({p}, {q})' for p, q in exitc) + '}', exitc == [(g, 0)])]
    for k, txt, ok in rows:
        o.append(T(X, y, k, 12, GRAY, 'start', SANS))
        o.append(T(X + 74, y, txt + ('  ✓' if ok else '  ✗'), 13.5, INK if ok else RED)); y += 26
    y += 12
    o.append(T(X, y, 'light arrows: (x, y) → (y, x mod y) from', 12, GRAY, 'start', SANS)); y += 16
    o.append(T(X, y, f'every shaded cell in view ({len(arrows)} of them)', 12, GRAY, 'start', SANS)); y += 22
    o.append(T(X, y, 'navy: the run ' + ' → '.join(f'({p}, {q})' for p, q in tr), 12.5, NAVY, 'start', SANS)); y += 16
    o.append(T(X, y, f'shaded cells in view: {len(S)}', 12, GRAY, 'start', SANS))
    save('fig-1.svg', o)

# ---------------- fig-2: rays through the origin -----------------
def fig2():
    a, b, N = 12, 8, 20
    g = math.gcd(a, b)
    o = head(900, 640, f'Along each ray from 0, gcd counts 1, 2, 3, …; the set takes {g}')
    G = Grid(66, 560, 22.5, N)
    S = inv(N, g)
    dirs = sorted({(x // g, y // g) for (x, y) in S})
    ox, oy = G.p(0, 0)
    for (p, q) in dirs:
        m = min(N / p if p else 1e9, N / q if q else 1e9)
        ex, ey = G.p(p * m, q * m)
        o.append(f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#b9b4dc" stroke-width="0.9" stroke-dasharray="3 3"/>')
    draw_grid(o, G, S)
    # label gcd along three rays
    for (p, q) in [(3, 2), (1, 3), (5, 1)]:
        k = 1
        while p * k <= N and q * k <= N:
            cx, cy = G.p(p * k, q * k)
            on = (k == g)
            o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.5" fill="{"#fffff0" if not on else PURF}" stroke="{PUR if on else "#999"}" stroke-width="{1.6 if on else 0.8}"/>')
            o.append(T(cx, cy + 4, str(math.gcd(p * k, q * k)), 11.5, INK if on else '#666', 'middle', SANS))
            k += 1
    for (p, q), lab in [((3, 2), 'ray through (3, 2)'), ((1, 3), 'ray through (1, 3)'), ((5, 1), 'ray through (5, 1)')]:
        k = max(k for k in range(1, N + 1) if p * k <= N and q * k <= N)
        cx, cy = G.p(p * k, q * k)
        dx, dy = {(3, 2): (-58, 28), (1, 3): (12, -8), (5, 1): (12, -8)}[(p, q)]
        o.append(T(cx + dx, cy + dy, lab, 11.5, '#666', 'start', SANS))
    X = 586; y = 100
    o.append(T(X, y, 'Numbers in circles: gcd of that cell.', 13)); y += 28
    lines = ['On the ray through a primitive (p, q)',
             '(gcd(p, q) = 1) the cells are k·(p, q),',
             'and gcd(k·p, k·q) = k.',
             '',
             f'So every ray holds exactly one cell with',
             f'gcd = {g}: the cell k = {g}. The shaded set',
             'is one cell per ray, a "transversal".']
    for L in lines:
        o.append(T(X, y, L, 13.5)); y += 20
    y += 14
    o.append(T(X, y, f'Rays shown: {len(dirs)} directions with a', 12, GRAY, 'start', SANS)); y += 16
    o.append(T(X, y, f'shaded cell inside 0…{N}; each has one.', 12, GRAY, 'start', SANS))
    # verify claim
    for (p, q) in dirs:
        assert sum(1 for k in range(1, N + 1) if (p * k, q * k) in S) == 1
    save('fig-2.svg', o)

# ---------------- fig-3: dependence on (a, b) -----------------
def fig3():
    o = head(900, 520, 'Change the inputs and the shaded set, and the type, change')
    N = 15; C = 15.5
    pairs = [(13, 8), (15, 9), (0, 0)]
    for i, (a, b) in enumerate(pairs):
        g = math.gcd(a, b)
        X0 = 48 + i * 292
        G = Grid(X0, 392, C, N)
        S = inv(N, g)
        draw_grid(o, G, S, label_every=5)
        tr = run(a, b)
        draw_run(o, G, tr)
        ex, ey = G.p(g, 0)
        o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{C*0.5:.1f}" fill="none" stroke="{PUR}" stroke-width="2"/>')
        cx, _ = G.p(N / 2, 0)
        o.append(T(cx, 76, f'(a, b) = ({a}, {b})', 15, INK, 'middle'))
        o.append(T(cx, 94, f'shaded: gcd(x, y) = {g}   ({len(S)} cell{"s" if len(S) != 1 else ""})', 12, GRAY, 'middle', SANS))
        yl = 448
        o.append(f'<line x1="{ex:.1f}" y1="{ey + C*0.5 + 17:.1f}" x2="{ex:.1f}" y2="{yl - C*0.38:.1f}" stroke="{PUR}" stroke-width="1.3" stroke-dasharray="3 3"/>')
        numline(o, G, yl, {g})
        o.append(T(cx, yl + 30, f'Gcd({a}, {b}) = {{{g}}}', 15, PUR, 'middle'))
        o.append(T(cx, yl + 50, 'run: ' + ' → '.join(f'({p},{q})' for p, q in tr) if len(tr) < 5 else
                   'run: ' + ' → '.join(f'({p},{q})' for p, q in tr[:3]) + ' → … → ' + f'({tr[-1][0]},{tr[-1][1]})', 11.5, NAVY, 'middle', SANS))
    save('fig-3.svg', o)

# ---------------- fig-4: a too-weak invariant is a type error -----------------
def fig4():
    a, b, N = 12, 8, 20
    g = math.gcd(a, b)
    o = head(900, 680, 'Too-weak invariant "x, y both even": exit is not pinned to 4')
    G = Grid(66, 548, 22.5, N)
    W = {(x, y) for x in range(N + 1) for y in range(N + 1) if x % 2 == 0 and y % 2 == 0}
    S = inv(N, g)
    draw_grid(o, G, S & set(), weak=W)
    # arrows from weak set stay in weak set (preservation holds)
    arrows = [((x, y), (y, x % y)) for (x, y) in sorted(W) if y > 0]
    assert all(t in W for s, t in arrows)
    tr = run(a, b); draw_run(o, G, tr)
    exitW = sorted(c for c in W if c[1] == 0)
    bad = [c for c in exitW if c != (g, 0)]
    for (x, y) in bad:
        cx, cy = G.p(x, y); r = G.C * 0.3
        o.append(f'<rect x="{cx - G.C*0.42:.1f}" y="{cy - G.C*0.42:.1f}" width="{G.C*0.84:.1f}" height="{G.C*0.84:.1f}" rx="2" fill="#f6e3e3" stroke="{RED}" stroke-width="1.6"/>')
    ex, ey = G.p(g, 0)
    o.append(f'<rect x="{ex - G.C*0.42:.1f}" y="{ey - G.C*0.42:.1f}" width="{G.C*0.84:.1f}" height="{G.C*0.84:.1f}" rx="2" fill="{PURF}" stroke="{PUR}" stroke-width="1.6"/>')
    draw_run(o, G, tr)
    yl = 618
    for (x, y) in exitW:
        cx, cy = G.p(x, y)
        col = PUR if (x, y) == (g, 0) else RED
        o.append(f'<line x1="{cx:.1f}" y1="{cy + G.C*0.45 + 17:.1f}" x2="{cx:.1f}" y2="{yl - 9:.1f}" stroke="{col}" stroke-width="1.1" stroke-dasharray="3 3"/>')
    numline(o, G, yl, {g}, bad=[x for x, _ in bad], label=f'Gcd({a}, {b}) ⊂ ℕ')
    xa, _ = G.p(0, 0)
    o.append(T(xa - G.C/2, yl + 32, 'every dashed drop is a value the proof would allow; all but one miss the type', 12, GRAY, 'start', SANS))
    _, y0 = G.p(0, 0); xb, _ = G.p(N, 0)
    o.append(T(xb + G.C/2 + 8, y0 + 4, 'exit row  y = 0', 12, GRAY, 'start', SANS))
    X = 586; y = 92
    o.append(T(X, y, 'The invariant written (dashed cells):', 15)); y += 24
    o.append(T(X, y, "Inv′ = {(x, y) | 2 ∣ x ∧ 2 ∣ y}", 13.5, PUR)); y += 34
    land = sum(1 for s, t in arrows if t in W)
    rows = [('entry', f'({a}, {b}) ∈ Inv′', (a, b) in W),
            ('preserved', f'{land} of {len(arrows)} arrows stay in Inv′', land == len(arrows)),
            ('decreasing', 'y drops on every arrow', all(t[1] < s[1] for s, t in arrows))]
    for k, txt, ok in rows:
        o.append(T(X, y, k, 12, GRAY, 'start', SANS))
        o.append(T(X + 74, y, txt + '  ✓', 13.5, INK)); y += 26
    o.append(T(X, y, 'exit', 12, RED, 'start', SANS))
    o.append(T(X + 74, y, f'Inv′ ∩ {{y = 0}} has {len(exitW)} cells', 13.5, RED)); y += 20
    o.append(T(X + 74, y, f'⊈ Gcd({a}, {b}) × {{0}} = {{({g}, 0)}}  ✗', 13.5, RED)); y += 34
    o.append(T(X, y, 'Solid purple cell: the only exit allowed.', 12, GRAY, 'start', SANS)); y += 16
    o.append(T(X, y, 'Dark red: exits the weak invariant permits.', 12, GRAY, 'start', SANS)); y += 24
    o.append(T(X, y, 'The program is right; its invariant is too', 13)); y += 18
    o.append(T(X, y, 'weak to prove the result type.', 13))
    save('fig-4.svg', o)

fig1(); fig2(); fig3(); fig4()
print('ok')
