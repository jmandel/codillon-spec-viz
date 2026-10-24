#!/usr/bin/env python3
"""Audit fixes for angle 09 (typing derivation as composed pictures).
Reads gcdviz/09/fig-K.svg, applies exact string replacements, writes gallery-build/fixed/09/fig-K.svg."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "gcdviz", "09")
DST = os.path.join(ROOT, "gallery-build", "fixed", "09")

# (old, new, expected_count)
FIXES = {
    2: [
        # LAYOUT: line overflows its 224-px box on both sides; the {1,2,4} value is already in the header
        ("∴  Div(x&#x27;) ∩ Div(y&#x27;) = Div(x) ∩ Div(y) = {1,2,4}",
         "∴  Div(x&#x27;) ∩ Div(y&#x27;) = Div(x) ∩ Div(y)", 1),
    ],
    4: [
        # MISLEADING: the 0..21 × 0..7 window hides (0,21), (21,21), (42,21)...; Inv(21,0) is not a singleton
        ("2. Loop Invariant Set  Inv(21, 0)", "2. Loop Invariant Set  Inv(21, 0), y ≤ 7 shown", 1),
    ],
    5: [
        # MISLEADING: holds at the witness (8,4) but not for every y ≠ 0 (e.g. (4,8))
        ("where y ≠ 0 so Div(x) ≠ Div(x)∩Div(y)", "at (8, 4): Div(8) ≠ Div(8) ∩ Div(4)", 1),
        # MATH: {x | ∃y ≤ 4. gcd(x,y)=4} = all multiples of 4 (infinite), not just {0,4,8,12}
        ("= {0, 4, 8, 12} ⊈ {4}", "= {0, 4, 8, 12, …} ⊈ {4}", 1),
        # MATH: the buggy body (x,y) ← (y div 2, x mod y) sends (12,8) to (4,4), not (8,4);
        # re-anchor the witness on the real buggy run (12,8) → (4,4) → (2,0)
        ("Input state: (x = 8, y = 4) ∈ Inv", "Input state: (x = 4, y = 4) ∈ Inv", 1),
        ("Div(8) ∩ Div(4) = {1, 2, 4} ✓", "Div(4) ∩ Div(4) = {1, 2, 4} ✓", 1),
        ("Buggy step maps (8, 4) ↦ (2, 0)", "Buggy step maps (4, 4) ↦ (2, 0)", 1),
        ('<line x1="434.0" y1="324.0" x2="398.7" y2="359.0" stroke="#00008b"',
         '<line x1="434.0" y1="324.0" x2="363.3" y2="359.0" stroke="#00008b"', 1),
        ('<line x1="398.7" y1="359.0" x2="345.7" y2="394.0" stroke="#8b0000"',
         '<line x1="363.3" y1="359.0" x2="345.7" y2="394.0" stroke="#8b0000"', 1),
        ('<circle cx="398.7" cy="359.0" r="3.7" fill="none" stroke="#00008b"',
         '<circle cx="363.3" cy="359.0" r="3.7" fill="none" stroke="#00008b"', 1),
        # MATH: per the definition 0 ∣ 0, so 0 ∈ Div(0) = ℕ = {0, 1, 2, ...}
        ("Div(0) = ℕ = {1, 2, 3, 4, 5, …}", "Div(0) = ℕ = {0, 1, 2, 3, 4, …}", 1),
    ],
}


def main():
    os.makedirs(DST, exist_ok=True)
    for k in range(1, 6):
        with open(os.path.join(SRC, f"fig-{k}.svg"), encoding="utf-8") as f:
            s = f.read()
        for old, new, n in FIXES.get(k, []):
            c = s.count(old)
            assert c == n, f"fig-{k}: expected {n} of {old!r}, found {c}"
            s = s.replace(old, new)
        with open(os.path.join(DST, f"fig-{k}.svg"), "w", encoding="utf-8") as f:
            f.write(s)
        print(f"fig-{k}: {len(FIXES.get(k, []))} fix(es)")


if __name__ == "__main__":
    main()
