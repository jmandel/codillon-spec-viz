#!/usr/bin/env python3
"""Fixes for angle 10 (Codillon editor idiom). Reads gcdviz/10/fig-K.svg, writes gallery-build/fixed/10/fig-K.svg."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', '..', 'gcdviz', '10'))
DST = os.path.normpath(os.path.join(HERE, '..', 'fixed', '10'))

SANS = "font-family=\"'Arial Narrow', Arial, sans-serif\""
SERIF = "font-family=\"Georgia, 'Times New Roman', serif\""
MONO = "font-family=\"'Courier New', Courier, monospace\""

def rect_all(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#d9d5f2" fill-opacity="0.75"/>'

# Palette rule: indigo #4b0082 is reserved for "unknown"; tethers/labels here are type marks -> purple.
INDIGO = ('#4b0082', '#6A5ACD', None)   # None = replace all occurrences (count asserted > 0)

FIXES = {
    1: [
        INDIGO,
        ('>Any 32-bit int fits; 0 divisor undetected<',
         '>Any i32 fits; a 0 divisor traps only at run time<', 1),
    ],
    2: [
        INDIGO,
        ('>WAT INSTRUCTION<', '>WAT (ABRIDGED)<', 1),
        # label overlapped by the bar that starts at x=664
        ('>Common Div:<', '>Common:<', 3),
        # Div(0) = N: shade only [0, INT_MAX], not negative i32 values
        (rect_all('646.0', '491.0', '96.0', '14.0'), rect_all('694.0', '491.0', '48.0', '14.0'), 1),
    ],
    3: [
        INDIGO,
        ('>Div(462)={1,2,3,7,..,462}<', '>Div(462)={1,2,3,6,..,462}<', 1),
        ('>C. Zero Absorber: (a = 21, b = 0)', '>C. Zero Is the Identity: (a = 21, b = 0)', 1),
        ('>13 mod 8 = 5  →  8 mod 5 = 3  →  5 mod 3 = 2  →  3 mod 2 = 1<',
         '>13 mod 8=5 → 8 mod 5=3 → 5 mod 3=2 → 3 mod 2=1 → 2 mod 1=0<', 1),
        # Div(0) = N on params: shade only [0, INT_MAX]
        (rect_all('248.0', '448.0', '170.0', '16.0'), rect_all('333.0', '448.0', '85.0', '16.0'), 1),
        (rect_all('482.0', '448.0', '170.0', '16.0'), rect_all('567.0', '448.0', '85.0', '16.0'), 1),
        (rect_all('684.0', '448.0', '170.0', '16.0'), rect_all('769.0', '448.0', '85.0', '16.0'), 1),
        # Gcd(0,0) = {0}: the result cup must not be shaded as all of i32
        ('  ' + rect_all('498.0', '536.0', '340.0', '22.0') + '\n', '', 1),
        # g = 21 sits 3.4 px right of the +8 hairline; label the socket value so it does not read as 8
        (f'<text x="334.0" y="285.0" text-anchor="middle" {SANS} font-size="11" fill="#555555">+8</text>',
         f'<text x="329.0" y="285.0" text-anchor="end" {SANS} font-size="11" fill="#555555">+8</text>'
         f'<text x="339.0" y="285.0" text-anchor="start" {SANS} font-size="11" font-weight="bold" fill="#00008b">21</text>', 1),
        (f'<text x="334.0" y="571.0" text-anchor="middle" {SANS} font-size="11" fill="#555555">+8</text>',
         f'<text x="329.0" y="571.0" text-anchor="end" {SANS} font-size="11" fill="#555555">+8</text>'
         f'<text x="339.0" y="571.0" text-anchor="start" {SANS} font-size="11" font-weight="bold" fill="#00008b">21</text>', 1),
    ],
    4: [
        INDIGO,
        # ';;' starts a WAT line comment; two instructions on one line are just whitespace-separated
        ('>i32.const 2 ;; return<', '>i32.const 2  return<', 1),
        ('>local.get $b ;; return<', '>local.get $b  return<', 1),
        ('>local.get $x ;; br_if $exit<', '>local.get $x  br_if $exit<', 1),
        ('>Error 3: Buggy Loop Exit (br_if $x)<', '>Error 3: Exit Tests $x, Not $y<', 1),
    ],
    5: [
        INDIGO,
        # CommonDiv(12,8) and Div(12) are finite sets, not intervals: drop the interval shading, keep the notches
        ('  <rect x="182.2" y="230.0" width="24.8" height="20.0" fill="#d9d5f2" fill-opacity="0.85"/>\n', '', 1),
        ('  <rect x="182.2" y="314.0" width="58.7" height="20.0" fill="#d9d5f2" fill-opacity="0.85"/>\n', '', 1),
    ],
}

def main():
    os.makedirs(DST, exist_ok=True)
    for k in range(1, 6):
        with open(os.path.join(SRC, f'fig-{k}.svg'), encoding='utf-8') as f:
            s = f.read()
        for old, new, n in FIXES.get(k, []):
            c = s.count(old)
            if n is None:
                assert c > 0, (k, old)
            else:
                assert c == n, (k, old, c, n)
            s = s.replace(old, new)
        with open(os.path.join(DST, f'fig-{k}.svg'), 'w', encoding='utf-8') as f:
            f.write(s)
        print(f'fig-{k}: {len(FIXES.get(k, []))} fixes')

if __name__ == '__main__':
    main()
