#!/usr/bin/env python3
"""Reproducible fixes for angle 03 (prime-exponent space).
Reads gcdviz/03/fig-K.svg, applies exact string replacements, writes gallery-build/fixed/03/fig-K.svg."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'gcdviz', '03')
DST = os.path.join(ROOT, 'gallery-build', 'fixed', '03')

FIXES = {
    3: [
        # LAYOUT: panel-1 label "12" sat on the red arrow at x=190; centre it over its point (176, 276).
        ('<rect x="180" y="252" width="19.44" height="15" fill="#fffff0"',
         '<rect x="166.28" y="252" width="19.44" height="15" fill="#fffff0"', 1),
        ('<text x="184" y="264" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#00008b" '
         'font-weight="normal" font-style="normal" text-anchor="start">12</text>',
         '<text x="176" y="264" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#00008b" '
         'font-weight="normal" font-style="normal" text-anchor="middle">12</text>', 1),
        # NIT: "{3, 6, 12} ∤ 8" applies ∤ to a set; state it per element.
        ('Illegal row e₃ = 1: {3, 6, 12} ∤ 8!', 'Illegal row e₃ = 1: 3, 6, 12 ∤ 8!', 1),
    ],
    4: [
        # MISLEADING: "Outer box shrinks toward corner (3,1)." -- x's box widens 72→48 (e₂ 3→4) and
        # y's box grows to all of ℕ at 48 mod 24 = 0. Say what actually happens at each step.
        ('<text x="54" y="504" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#555555" '
         'font-weight="normal" font-style="normal" text-anchor="start">Outer box shrinks toward corner (3,1).</text>',
         '<text x="54" y="504" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#555555" '
         'font-weight="normal" font-style="normal" text-anchor="start">New y = 24: its box is exactly the purple box.</text>', 1),
        ('<text x="339" y="504" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#555555" '
         'font-weight="normal" font-style="normal" text-anchor="start">Outer box shrinks toward corner (3,1).</text>',
         '<text x="339" y="504" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#555555" '
         'font-weight="normal" font-style="normal" text-anchor="start">New x = 24 at the corner; Div(new y = 0) = ℕ.</text>', 1),
    ],
    5: [
        # LAYOUT: tick labels touched the purple box edge (left at x=90, bottom at y=553).
        ('<text x="90" y="541" ', '<text x="85" y="541" ', 1),
        ('<text x="90" y="483" ', '<text x="85" y="483" ', 1),
        ('<text x="106" y="561" ', '<text x="106" y="566" ', 1),
        ('<text x="188" y="561" ', '<text x="188" y="566" ', 1),
        ('<text x="270" y="561" ', '<text x="270" y="566" ', 1),
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
