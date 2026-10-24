#!/usr/bin/env python3
"""Minimal, reproducible fixes for angle 01 (divisibility lattice).
Reads gcdviz/01/fig-K.svg, applies exact string replacements (each asserted to
occur the expected number of times), writes gallery-build/fixed/01/fig-K.svg.
Figures without fixes are copied unchanged."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', 'gcdviz', '01'))
DST = os.path.normpath(os.path.join(HERE, '..', 'fixed', '01'))

FIXES = {
    1: [],
    2: [
        # LAYOUT: "4 ∤ 2 (misses 4)" touched the dashed red arrow from 4 to 2.
        ('<text x="139.0" y="319.5" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" font-weight="bold" fill="#8b0000">4 ∤ 2 (misses 4)</text>',
         '<text x="143.0" y="319.5" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" font-weight="bold" fill="#8b0000">4 ∤ 2 (misses 4)</text>', 1),
        # LAYOUT: "4 ∤ 6, 6 ∤ 8" collided with the rings of nodes 4 and 6; lift it above them.
        ('<text x="720.5" y="289.0" text-anchor="middle"',
         '<text x="720.5" y="279.0" text-anchor="middle"', 1),
        # LAYOUT: "g = 6 ✗" sat on the red Div(6) cone edge and the gray Div(12) hull edge.
        ('<text x="789.0" y="300.0" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11.5" font-weight="bold" fill="#8b0000">g = 6 ✗</text>',
         '<text x="790.0" y="271.0" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11.5" font-weight="bold" fill="#8b0000">g = 6 ✗</text>', 1),
    ],
    3: [],
    4: [
        # PALETTE: indigo #4b0082 is reserved for "unknown"; Div(2) is a known down-set.
        ('#4b0082', '#555555', 2),
        # LAYOUT: bold line overflowed its 388-px box on both sides.
        ('• When y = 0 in Euclid’s algorithm, x = 12 ALREADY inhabits Gcd(12, 0).',
         '• At y = 0 in Euclid’s loop, x = 12 already inhabits Gcd(12, 0).', 1),
    ],
    5: [
        # LAYOUT: takeaway line overflowed the 854-px footer box.
        ('Refinement Type Takeaway: The purple cone {1, 2, 4} is the compile-time proof certificate; the navy numbers (12,8) → (8,4) → (4,0) are the runtime values.',
         'Takeaway: the purple cone {1, 2, 4} is the compile-time proof certificate; the navy pairs (12,8) → (8,4) → (4,0) are runtime values.', 1),
    ],
}

os.makedirs(DST, exist_ok=True)
for k, reps in FIXES.items():
    with open(os.path.join(SRC, f'fig-{k}.svg'), encoding='utf-8') as fh:
        s = fh.read()
    for old, new, n in reps:
        c = s.count(old)
        assert c == n, f'fig-{k}: expected {n} of {old!r}, found {c}'
        s = s.replace(old, new)
    with open(os.path.join(DST, f'fig-{k}.svg'), 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f'fig-{k}: {len(reps)} fix(es) -> {DST}/fig-{k}.svg')
