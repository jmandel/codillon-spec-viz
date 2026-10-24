#!/usr/bin/env python3
"""Audit fixes for angle 08 (dependent type family / fibers).
Reads gcdviz/08/fig-K.svg, applies exact string replacements, writes gallery-build/fixed/08/fig-K.svg."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "gcdviz", "08")
DST = os.path.join(ROOT, "gallery-build", "fixed", "08")

# (old, new, expected_count)
FIXES = {
    1: [
        # MISLEADING: many purple cells carry other gcds (6, 8, 12, 16 ...); only the outlined ones are {4}
        ("Purple cells (4,4), (4,8), (8,12), (12,8), (12,16)... all carry fiber {4}",
         "Outlined cells (4,4), (4,8), (8,12), (12,8), (12,16)... all carry fiber {4}", 1),
    ],
    2: [
        # MISLEADING: the vertical line is the ambient ℕ; the fiber Gcd(a, 8) is the ringed singleton on it
        ("(each vertical line is one fiber ⊂ ℕ)",
         "(each vertical line is ℕ; its ring is the fiber)", 1),
    ],
    3: [
        # MISLEADING: the shaded column spans every candidate g (incl. the ✕ values 2, 8, 12); the fiber is only {4}
        (">Fiber Gcd(12, 8)</text>", ">ℕ over (12, 8)</text>", 1),
    ],
    4: [
        # MISLEADING: Div(x) ∩ Div(y) is the invariant set of common divisors, not the fiber itself
        ("moves to a simpler base point with the exact same fiber Div(x) ∩ Div(y)",
         "keeps Div(x) ∩ Div(y), so the fiber Gcd(x, y) never changes", 1),
        # LAYOUT: Run B label overflows its box (closing brace sits on the border)
        ('<rect x="284.2" y="240.8" width="154" height="20"',
         '<rect x="276.2" y="240.8" width="170" height="20"', 1),
    ],
    5: [
        # NIT: "a∨b > 0" is not well-formed; mean (a, b) ≠ (0, 0)
        ("TYPE ERROR: {0} ≠ Gcd(a, b) for a∨b &gt; 0",
         "TYPE ERROR: {0} ≠ Gcd(a, b) for (a, b) ≠ (0, 0)", 1),
        # LAYOUT: footer runs past both edges of the right-hand panel
        ("Runtime evidence is erased: only the plain integer 4 (or 21) flows on the Wasm stack.",
         "Proof erased at run time: only 4 (or 21) is on the Wasm stack.", 1),
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
