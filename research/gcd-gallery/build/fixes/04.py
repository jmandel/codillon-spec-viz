#!/usr/bin/env python3
"""Reproducible fixes for angle 04 (Euclid's rectangle tiling).
Reads gcdviz/04/fig-K.svg, applies exact string replacements, writes gallery-build/fixed/04/fig-K.svg."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'gcdviz', '04')
DST = os.path.join(ROOT, 'gallery-build', 'fixed', '04')

def cut_line(coords, width):
    # PALETTE: Euclid cut lines are not violations; dark red #8b0000 -> ink #222222.
    old = f'<line {coords} stroke="#8b0000" stroke-width="{width}" stroke-dasharray="4,2"/>'
    return (old, old.replace('#8b0000', '#222222'), 1)

FIXES = {
    2: [
        cut_line('x1="123.00" y1="112.00" x2="123.00" y2="192.00"', '2.2'),
        cut_line('x1="130.00" y1="281.00" x2="130.00" y2="363.00"', '2'),
        cut_line('x1="383.00" y1="295.00" x2="383.00" y2="341.00"', '2'),
        cut_line('x1="149.60" y1="484.00" x2="149.60" y2="585.60"', '2.2'),
        cut_line('x1="145.60" y1="550.40" x2="216.00" y2="550.40"', '2.2'),
        cut_line('x1="180.80" y1="546.40" x2="180.80" y2="585.60"', '2.2'),
        ('fill="#8b0000" text-anchor="middle" font-weight="bold">cut</text>',
         'fill="#222222" text-anchor="middle" font-weight="bold">cut</text>', 1),
        # LAYOUT: lemma labels "y × y" / "r × y" sat on the dashed mid-line (y=152); move into lower half.
        ('<text x="89.00" y="156.00" ', '<text x="89.00" y="174.00" ', 1),
        ('<text x="140.00" y="156.00" ', '<text x="140.00" y="174.00" ', 1),
        # MISLEADING: halting state (4, 0) is drawn as a 4×4 square; say it is the g×g tile, state is 4×0.
        ('font-weight="bold">0 remainder!</text>', 'font-weight="bold">g×g tile; state is 4×0</text>', 1),
        # MATH: Div(0) contains 0 (0 | 0); "all d ≥ 1" omits it.
        ('ℕ (all d ≥ 1)', 'ℕ (all d ≥ 0)', 1),
    ],
    3: [
        # MATH: Div(0) = ℕ must contain 0, otherwise Gcd(0, 0) = {0} (same panel) has no inhabitant in ℕ.
        ('Div(0) = ℕ = {1, 2, 3, …}.', 'Div(0) = ℕ = {0, 1, 2, …}.', 1),
        # NIT: the 21 × 0 rectangle has zero HEIGHT (b is the vertical side throughout the angle).
        ('Zero Width Preserves Div(a)', 'Zero Height Preserves Div(a)', 1),
        ('degenerate 0-width rectangle', 'degenerate 0-height rectangle', 1),
    ],
    5: [
        cut_line('x1="748.00" y1="142.00" x2="748.00" y2="242.00"', '2.2'),
        # MISLEADING: a fiber has many points; the singleton is the TYPE Gcd(x, y) = {g}.
        ('reveals the fiber&#x27;s unique inhabitant x = g!', 'reveals the type&#x27;s unique inhabitant x = g!', 1),
    ],
}

def main():
    os.makedirs(DST, exist_ok=True)
    for k in range(1, 6):
        with open(os.path.join(SRC, f'fig-{k}.svg'), encoding='utf-8') as f:
            s = f.read()
        for old, new, n in FIXES.get(k, []):
            c = s.count(old)
            assert c == n, f'fig-{k}: expected {n} occurrence(s) of {old!r}, found {c}'
            s = s.replace(old, new)
        with open(os.path.join(DST, f'fig-{k}.svg'), 'w', encoding='utf-8') as f:
            f.write(s)
        print(f'fig-{k}: {len(FIXES.get(k, []))} replacement(s)')

if __name__ == '__main__':
    main()
