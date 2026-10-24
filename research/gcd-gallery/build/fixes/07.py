#!/usr/bin/env python3
"""Audit fixes for angle 07 (Bezout / ideal view).
Reads gcdviz/07/fig-K.svg, applies exact string replacements, writes gallery-build/fixed/07/fig-K.svg."""
import os
BASE = '/home/jmandel/hobby/.agent-scratch/codalon-viz'
SRC = f'{BASE}/gcdviz/07'
DST = f'{BASE}/gallery-build/fixed/07'
IG = '<tspan font-style="italic">g</tspan>'

FIXES = {
    1: [
        # "g > 0" conjunct contradicts Gcd(0, 0) = {0} (fig-5); g ∈ ℕ with 12ℤ+8ℤ = gℤ already pins g = 4
        (f'{IG} ∈ ℕ | {IG} &gt; 0 ∧ 12ℤ + 8ℤ = {IG}ℤ', f'{IG} ∈ ℕ | 12ℤ + 8ℤ = {IG}ℤ', 1),
        ('>{ g ∈ ℕ | g &gt; 0 ∧ 12ℤ + 8ℤ = gℤ }</text>', '>{ g ∈ ℕ | 12ℤ + 8ℤ = gℤ }</text>', 1),
        # the gap box edge and the dotted leader ran through the key value label "4"
        ('<rect x="407.0" y="340.0" width="73.0" height="36.0"', '<rect x="407.0" y="340.0" width="73.0" height="28.0"', 1),
        ('<path d="M 480.0 370.0 L 480.0 431.0 L 508.0 431.0"', '<path d="M 480.0 400.0 L 480.0 431.0 L 508.0 431.0"', 1),
    ],
    2: [
        # SVG collapses "+24   k = +6" to "+24 k = +6", which reads as "24k"; add a separator
        ('   k = ', ',  k = ', 12),
    ],
    3: [
        # "g=21" label was struck through by the 462 - 3*(147) = 21 arrow
        ('<text x="546.3" y="230.0" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#6A5ACD" text-anchor="start" font-weight="bold">g=21</text>',
         '<text x="542.3" y="246.0" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#6A5ACD" text-anchor="middle" font-weight="bold">g=21</text>', 1),
        # unit-step box edges ran through the tick labels "0" and "1"
        ('<rect x="142.8" y="524.0" width="43.9" height="40.0"', '<rect x="142.8" y="524.0" width="43.9" height="30.0"', 1),
        # "unit step g = 1" and "3 − 2 = 1" ran together into one phrase
        ('<text x="164.7" y="518.0"', '<text x="156.0" y="518.0"', 1),
        ('<text x="230.6" y="518.0" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#6A5ACD" text-anchor="middle" font-weight="bold">3 − 2 = 1</text>',
         '<text x="240.0" y="518.0" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="11" fill="#6A5ACD" text-anchor="middle" font-weight="bold">3 − 2 = 1</text>', 1),
    ],
    4: [
        # same "g > 0" issue as fig-1
        (f'= {{ {IG} &gt; 0 | 12ℤ + 8ℤ = {IG}ℤ }}', f'= {{ {IG} ∈ ℕ | 12ℤ + 8ℤ = {IG}ℤ }}', 1),
    ],
    5: [
        # y' = 4 is a Bezout witness, not the invariant (the invariant is the ideal x'ℤ + y'ℤ = 4ℤ)
        ('= 4  (invariant!)</text>', '= 4  (Bézout witness)</text>', 1),
    ],
}

os.makedirs(DST, exist_ok=True)
for k in range(1, 6):
    s = open(f'{SRC}/fig-{k}.svg', encoding='utf-8').read()
    for old, new, n in FIXES.get(k, []):
        c = s.count(old)
        assert c == n, f'fig-{k}: expected {n} of {old[:70]!r}, found {c}'
        s = s.replace(old, new)
    open(f'{DST}/fig-{k}.svg', 'w', encoding='utf-8').write(s)
    print(f'fig-{k}: {len(FIXES.get(k, []))} replacement rules')
