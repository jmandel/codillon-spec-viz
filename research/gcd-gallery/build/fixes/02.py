#!/usr/bin/env python3
"""Minimal, reproducible fixes for angle 02 (divisor strips on a number line).
Reads gcdviz/02/fig-K.svg, applies exact string replacements (each asserted to
occur the expected number of times), writes gallery-build/fixed/02/fig-K.svg.
Figures without fixes are copied unchanged."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', 'gcdviz', '02'))
DST = os.path.normpath(os.path.join(HERE, '..', 'fixed', '02'))

ARROW = ('<text x="{x}" y="{y}" font-family="\'Arial Narrow\', Arial, sans-serif" '
         'font-size="11.5" fill="#8b0000" text-anchor="{a}" font-weight="bold" font-style="normal">')

FIXES = {
    1: [
        # MISLEADING: "0 spills" on a figure whose divisor axis contains d = 0 reads as "divisor 0 spills".
        ('Every socket filled; 0 spills', 'Every socket filled; no spills', 1),
    ],
    2: [
        # MISLEADING: the "↑" pointers were centred text, so each arrow sat under the wrong column
        # (under d=2 instead of 4, under d=5 instead of 8, between 2 and 3). Left-anchor each
        # label so its "↑" sits under the column it refers to (columns at x = 225 + 36·d).
        (ARROW.format(x='389.0', y='240.0', a='middle') + '↑ Empty socket',
         ARROW.format(x='365.0', y='240.0', a='start') + '↑ Empty socket', 1),      # d = 4
        (ARROW.format(x='513.0', y='320.0', a='middle') + '↑ Spilled divisor',
         ARROW.format(x='509.0', y='320.0', a='start') + '↑ Spilled divisor', 1),   # d = 8
        (ARROW.format(x='399.0', y='400.0', a='middle') + '↑ 3, 6 spill out',
         ARROW.format(x='329.0', y='400.0', a='start') + '↑ 3, 6 spill out', 1),    # d = 3
        # MISLEADING: "0 empty, 0 spills" collides with the number 0 on the divisor axis.
        ('WELL-TYPED: 0 empty, 0 spills', 'WELL-TYPED: exact match', 1),
    ],
    3: [],
    4: [],
    5: [
        # MATH: only 7 candidates are drawn (g = 1, 2, 4, 8, 12, 0, 6), not all of 0..12.
        ('All Candidates g ∈ 0..12 Tested Against Sockets',
         'Candidates g ∈ {0, 1, 2, 4, 6, 8, 12} Tested Against Sockets', 1),
        # MISLEADING: the same half-type is called CommonMultOfCD in the subtitle and MultOfCD below.
        ('CommonMultOfCD', 'MultOfCD', 1),
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
