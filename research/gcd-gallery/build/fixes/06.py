#!/usr/bin/env python3
"""Audit fixes for angle 06 (refinement as nested predicate regions / Venn).
Reads gcdviz/06/fig-K.svg, applies exact string replacements, writes gallery-build/fixed/06/fig-K.svg."""
import os
BASE = '/home/jmandel/hobby/.agent-scratch/codalon-viz'
SRC = f'{BASE}/gcdviz/06'
DST = f'{BASE}/gallery-build/fixed/06'
GEO = "Georgia, 'Times New Roman', serif"

FIXES = {
    1: [
        # P2-only compartment is empty because every divisor of 8 divides 12 or is a multiple of 4 (old reason: "<=4")
        ('>(all d &#x2223; 8 are &#x2264;4</text>', '>(each d &#x2223; 8 divides 12</text>', 1),
        ('>or multiples of 4)</text>', '>or is a multiple of 4)</text>', 1),
        # "13, 14, 15, ..." implied every n >= 13 is outside all regions; 16, 20, ... are in P3
        ('>13, 14, 15, …</text>', '>13, 14, 15, 17, …</text>', 1),
        # P3 is the multiples of EVERY common divisor (not of any)
        ('>Multiples of common divisors = {0, 4, 8, 12, 16, &#x2026;}</text>',
         '>Multiples of every common divisor = {0, 4, 8, 12, 16, &#x2026;}</text>', 1),
    ],
    2: [
        # subtitle crossed the dashed T2 boundary
        ('>+ Conjunct P&#x2082;(g): g &#x2223; 8 (keeps {1, 2, 4})</text>', '>+ P&#x2082;(g): g &#x2223; 8 (keeps {1, 2, 4})</text>', 1),
        # subtitle ran onto the right panel border
        ('>Upcasting drops a conjunct; every inner value is valid outside</text>',
         '>Upcasting drops a conjunct; inner values stay valid</text>', 1),
    ],
    3: [
        # pills 1 and 2 straddled the P1/P2 boundaries; shrink + nudge so they sit wholly in P1 and P2 and outside P3
        ('<circle cx="143.0" cy="206.0" r="12.0" fill="#fae6e6" stroke="#8b0000" stroke-width="2.0" /><text x="143.0" y="210.2"',
         '<circle cx="146.0" cy="212.0" r="10.0" fill="#fae6e6" stroke="#8b0000" stroke-width="2.0" /><text x="146.0" y="216.2"', 1),
        ('<circle cx="173.0" cy="206.0" r="13.0" fill="#fae6e6" stroke="#8b0000" stroke-width="2.4" /><text x="173.0" y="210.6"',
         '<circle cx="169.0" cy="212.0" r="11.0" fill="#fae6e6" stroke="#8b0000" stroke-width="2.4" /><text x="169.0" y="216.6"', 1),
        # error badges overflowed their boxes
        ('>TYPE ERROR: Fails P₁: 8 ∤ 12 (does not divide a)</text>', '>TYPE ERROR: Fails P₁: 8 ∤ 12 = a</text>', 1),
        ('>TYPE ERROR: Fails P₂: 12 ∤ 8 (does not divide b)</text>', '>TYPE ERROR: Fails P₂: 12 ∤ 8 = b</text>', 1),
        # garbled reason
        ('>Input a = 12 leaks in (no P₁∧P₂ admits 0).</text>', '>Input a = 12 satisfies P₁ ∧ P₃ and leaks in.</text>', 1),
    ],
    4: [
        # Case B: pills listed incomplete sets without an ellipsis (101 = {63, 357, 1071}, 011 = {42, 231, 462},
        # 100 = {9, 17, 51, 119, 153}) and straddled circle boundaries; re-place so each lies inside its compartment
        ('<rect x="603.8" y="141.0" width="62.4" height="22.0" rx="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="635.0" y="155.8"',
         '<rect x="625.0" y="158.0" width="44.0" height="22.0" rx="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="647.0" y="172.8"', 1),
        ('<rect x="529.6" y="167.0" width="76.8" height="22.0" rx="11.0" fill="#ffffff" stroke="#6A5ACD" stroke-width="1.4" /><text x="568.0" y="181.7" text-anchor="middle" font-family="' + GEO + '" font-size="10.5" font-weight="normal" fill="#222222">9, 17, 51</text>',
         '<rect x="547.0" y="169.0" width="66.0" height="22.0" rx="11.0" fill="#ffffff" stroke="#6A5ACD" stroke-width="1.4" /><text x="580.0" y="183.7" text-anchor="middle" font-family="' + GEO + '" font-size="10.5" font-weight="normal" fill="#222222">9, 17, 51, …</text>', 1),
        ('<rect x="673.2" y="167.0" width="105.6" height="22.0" rx="11.0" fill="#ffffff" stroke="#6A5ACD" stroke-width="1.4" /><text x="726.0" y="181.7" text-anchor="middle" font-family="' + GEO + '" font-size="10.5" font-weight="normal" fill="#222222">2, 6, 11, 14…</text>',
         '<rect x="681.0" y="169.0" width="66.0" height="22.0" rx="11.0" fill="#ffffff" stroke="#6A5ACD" stroke-width="1.4" /><text x="714.0" y="183.7" text-anchor="middle" font-family="' + GEO + '" font-size="10.5" font-weight="normal" fill="#222222">2, 6, 11, …</text>', 1),
        ('<rect x="557.2" y="225.0" width="69.6" height="22.0" rx="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="592.0" y="239.7" text-anchor="middle" font-family="' + GEO + '" font-size="10.5" font-weight="normal" fill="#222222">63, 1071</text>',
         '<rect x="583.0" y="233.0" width="56.0" height="20.0" rx="10.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="611.0" y="246.2" text-anchor="middle" font-family="' + GEO + '" font-size="9" font-weight="normal" fill="#222222">63, 357, 1071</text>', 1),
        ('<rect x="672.8" y="225.0" width="62.4" height="22.0" rx="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="704.0" y="239.7" text-anchor="middle" font-family="' + GEO + '" font-size="10.5" font-weight="normal" fill="#222222">42, 462</text>',
         '<rect x="657.0" y="234.0" width="54.0" height="20.0" rx="10.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="684.0" y="247.2" text-anchor="middle" font-family="' + GEO + '" font-size="9" font-weight="normal" fill="#222222">42, 231, 462</text>', 1),
        # Case C: "42, 63..." pill poked out of P3
        ('<rect x="243.8" y="530.5" width="62.4" height="23.0" rx="11.5" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="275.0" y="545.7"',
         '<rect x="238.8" y="528.5" width="62.4" height="23.0" rx="11.5" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="270.0" y="543.7"', 1),
        # Case D: "g | 0 = N" read as "g divides (0 = N)"
        ('>P&#x2081;(g): g &#x2223; 0 = &#x2115;   and   P&#x2082;(g): g &#x2223; 0 = &#x2115;   (both expand to all of &#x2115;)</text>',
         '>P&#x2081; = {g | g &#x2223; 0} = &#x2115;   and   P&#x2082; = {g | g &#x2223; 0} = &#x2115;   (both are all of &#x2115;)</text>', 1),
    ],
    5: [
        # pills 1, 2 straddled the P1/P2 boundary (steps 0 and 1)
        ('<circle cx="144.0" cy="218.0" r="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="144.0" y="221.8"',
         '<circle cx="148.0" cy="222.0" r="9.5" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="148.0" y="225.8"', 1),
        ('<circle cx="172.0" cy="218.0" r="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="172.0" y="221.8"',
         '<circle cx="168.0" cy="222.0" r="9.5" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="168.0" y="225.8"', 1),
        ('<circle cx="436.0" cy="218.0" r="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="436.0" y="221.8"',
         '<circle cx="440.0" cy="222.0" r="9.5" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="440.0" y="225.8"', 1),
        ('<circle cx="464.0" cy="218.0" r="11.0" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="464.0" y="221.8"',
         '<circle cx="460.0" cy="222.0" r="9.5" fill="#ffffff" stroke="#43368a" stroke-width="1.4" /><text x="460.0" y="225.8"', 1),
        # "3,6,12 expelled" sat inside the Div(8) crescent, i.e. in the compartment they were expelled from
        ('<text x="384" y="245" text-anchor="middle" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="10.5" fill="#6e6e6e">3,6,12</text>',
         '<text x="340" y="196" text-anchor="middle" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="10.5" fill="#6e6e6e">3,6,12</text>', 1),
        ('<text x="384" y="257" text-anchor="middle" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="10.5" fill="#6e6e6e">expelled</text>',
         '<text x="340" y="208" text-anchor="middle" font-family="\'Arial Narrow\', Arial, sans-serif" font-size="10.5" fill="#6e6e6e">expelled</text>', 1),
        # P3 label sat on the bottom edge of the dashed P2 = N box in step 2
        ('<rect x="618" y="124" width="248" height="258" rx="8"', '<rect x="618" y="124" width="248" height="264" rx="8"', 1),
        # "strips non-common divisors" is wrong for step 2 (P2 grows to N) and omits 8 moving from P2 to P1 at step 1
        ('Each modulo step strips non-common divisors from the outer crescents (first 3, 6, 12 leave P&#x2081;; then 8 leaves P&#x2081;).</text>',
         'Step 1 drops 3, 6, 12 from P&#x2081; and moves 8 from P&#x2082; to P&#x2081;; step 2 drops 8 from P&#x2081; while P&#x2082; grows to &#x2115;.</text>', 1),
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
    print(f'fig-{k}: {len(FIXES.get(k, []))} replacements')
