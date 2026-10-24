#!/usr/bin/env python3
"""
Generator for Prime-Exponent Space visualizations of Gcd(a, b) as a refinement type.
Generates fig-1.svg through fig-5.svg.
"""

import math
from xml.sax.saxutils import escape

# Palette constants (strictly no green!)
BG = "#fffff0"          # ivory
INK = "#222222"         # primary ink
PURPLE = "#6A5ACD"      # type / region border
PURPLE_FILL = "#d9d5f2" # muted purple fill for refinement type set / intersection box
RED = "#8b0000"         # dark red ONLY for violation / type error
RED_FILL = "#f5d6d6"    # soft red tint for error areas
INDIGO = "#4b0082"      # indigo ONLY for "unknown"
NAVY = "#00008b"        # concrete run or value
GRAY_DARK = "#555555"
GRAY_MID = "#888888"
GRAY_LIGHT = "#cccccc"
GRAY_FAINT = "#e8e8df"

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"

SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '-': '⁻'
}

def sup(n):
    return ''.join(SUPERSCRIPTS[c] for c in str(n))

def val_23(e2, e3):
    return (2 ** e2) * (3 ** e3)

def fmt_factor_23(e2, e3):
    return f"2{sup(e2)}·3{sup(e3)}"

def factorize(n, primes=(2, 3, 5, 7)):
    if n == 0:
        return {p: float('inf') for p in primes}
    res = {}
    temp = n
    for p in primes:
        cnt = 0
        while temp % p == 0:
            cnt += 1
            temp //= p
        res[p] = cnt
    return res

def divisors(n):
    if n == 0:
        return set()
    return {d for d in range(1, n + 1) if n % d == 0}

class SVGBuilder:
    def __init__(self, width=900, height=580):
        self.width = width
        self.height = height
        self.elements = []
        self.defs = []

    def add_def(self, d):
        self.defs.append(d)

    def add(self, el):
        self.elements.append(el)

    def rect(self, x, y, w, h, fill="none", stroke="none", stroke_width=1, rx=0, dash=None, opacity=1.0):
        attrs = f'x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"'
        if rx:
            attrs += f' rx="{rx}" ry="{rx}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f'<rect {attrs}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, stroke_width=1, dash=None, marker_end=None, marker_start=None, opacity=1.0):
        attrs = f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if marker_end:
            attrs += f' marker-end="url(#{marker_end})"'
        if marker_start:
            attrs += f' marker-start="url(#{marker_start})"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f'<line {attrs}/>')

    def path(self, d, fill="none", stroke=INK, stroke_width=1, dash=None, marker_end=None, opacity=1.0):
        attrs = f'd="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if marker_end:
            attrs += f' marker-end="url(#{marker_end})"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f'<path {attrs}/>')

    def circle(self, cx, cy, r, fill=INK, stroke="none", stroke_width=1.5, dash=None, opacity=1.0):
        attrs = f'cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f'<circle {attrs}/>')

    def text(self, x, y, content, font=FONT_SERIF, size=14, fill=INK, weight="normal", style="normal", anchor="start", raw=False):
        txt = content if raw else escape(str(content))
        attrs = (f'x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
                 f'fill="{fill}" font-weight="{weight}" font-style="{style}" text-anchor="{anchor}"')
        self.add(f'<text {attrs}>{txt}</text>')

    def pill_label(self, x, y, text_str, font=FONT_SANS, size=11, fill=INK, weight="normal", anchor="middle", bg=BG, pad_x=4, pad_y=2):
        # Draws a small background pill behind text to prevent line collisions
        est_w = len(text_str) * (size * 0.52) + 2 * pad_x
        est_h = size + 2 * pad_y
        if anchor == "middle":
            rx = x - est_w / 2
        elif anchor == "end":
            rx = x - est_w + pad_x
        else:
            rx = x - pad_x
        ry = y - size + 1 - pad_y
        self.rect(rx, ry, est_w, est_h, fill=bg, stroke="none", rx=3, opacity=0.88)
        self.text(x, y, text_str, font=font, size=size, fill=fill, weight=weight, anchor=anchor)

    def add_standard_markers(self):
        self.add_def(f'''
        <marker id="arrow-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="{INK}"/>
        </marker>
        <marker id="arrow-navy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="{NAVY}"/>
        </marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="{PURPLE}"/>
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="{RED}"/>
        </marker>
        <marker id="arrow-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="{GRAY_DARK}"/>
        </marker>
        <pattern id="hatch-red" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="8" stroke="{RED}" stroke-width="1.5" opacity="0.35"/>
        </pattern>
        <pattern id="hatch-navy" width="10" height="10" patternTransform="rotate(-30 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="10" stroke="{NAVY}" stroke-width="1.0" opacity="0.12"/>
        </pattern>
        ''')

    def render(self):
        out = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">',
            f'<defs>{"".join(self.defs)}</defs>',
            f'<rect x="0" y="0" width="{self.width}" height="{self.height}" fill="{BG}"/>',
        ]
        out.extend(self.elements)
        out.append('</svg>')
        return '\n'.join(out)

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.render())


def draw_header(svg, title, subtitle):
    # Title (<= 12 words)
    svg.text(36, 36, title, font=FONT_SERIF, size=20, weight="bold", fill=INK)
    svg.text(36, 56, subtitle, font=FONT_SANS, size=13, fill=GRAY_DARK)
    svg.line(36, 66, svg.width - 36, 66, stroke=GRAY_LIGHT, stroke_width=1)


# ==============================================================================
# FIGURE 1: a = 12, b = 8 -> gcd = 4
# ==============================================================================
def make_fig1():
    svg = SVGBuilder(900, 565)
    svg.add_standard_markers()

    # Title: 12 words
    draw_header(
        svg,
        "In prime-exponent space, Div(n) is a box and gcd is the corner.",
        "Concrete inputs a = 12 (2²·3¹) and b = 8 (2³·3⁰): each divisor d | n is a grid point inside the box [0, e₂(n)] × [0, e₃(n)]."
    )

    # Verify numbers in Python
    a, b = 12, 8
    g = math.gcd(a, b)
    assert g == 4
    div_a = divisors(a)
    div_b = divisors(b)
    div_g = divisors(g)
    assert div_g == (div_a & div_b)

    # Grid geometry: shifted slightly left to leave clean space for callout & right panel
    gx0, gy0 = 96, 430
    dx, dy = 96, 122
    max_e2, max_e3 = 4, 2

    def pt(e2, e3):
        return (gx0 + e2 * dx, gy0 - e3 * dy)

    # Pad around boxes so grid points and their labels sit comfortably inside or outside
    pad_a = 32
    x_a0, y_a1 = pt(0, 1)
    x_a1, y_a0 = pt(2, 0)
    svg.rect(x_a0 - pad_a, y_a1 - pad_a, (x_a1 - x_a0) + 2*pad_a, (y_a0 - y_a1) + 2*pad_a,
             fill="url(#hatch-navy)", stroke=NAVY, stroke_width=2, rx=9, dash="7,4")

    # Box for Div(b=8): [0..3] x [0..0]
    pad_b = 25
    x_b0, y_b1 = pt(0, 0)
    x_b1, y_b0 = pt(3, 0)
    svg.rect(x_b0 - pad_b, y_b1 - pad_b, (x_b1 - x_b0) + 2*pad_b, (y_b0 - y_b1) + 2*pad_b,
             fill="none", stroke=NAVY, stroke_width=2, rx=7, dash="3,3")

    # Box for Intersection Div(12) ∩ Div(8) = Div(4): [0..2] x [0..0]
    pad_g = 18
    x_g0, y_g1 = pt(0, 0)
    x_g1, y_g0 = pt(2, 0)
    svg.rect(x_g0 - pad_g, y_g1 - pad_g, (x_g1 - x_g0) + 2*pad_g, (y_g0 - y_g1) + 2*pad_g,
             fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.8, rx=6)

    # Grid lines
    for e2 in range(max_e2 + 1):
        x, y_bot = pt(e2, 0)
        _, y_top = pt(e2, max_e3)
        svg.line(x, y_bot, x, y_top - 28, stroke=GRAY_LIGHT, stroke_width=1)
        svg.text(x, y_bot + 62, f"e₂ = {e2}", font=FONT_SANS, size=12, fill=GRAY_DARK, anchor="middle")
        svg.text(x, y_bot + 77, f"(2{sup(e2)}={2**e2})", font=FONT_SANS, size=11, fill=GRAY_MID, anchor="middle")

    for e3 in range(max_e3 + 1):
        x_left, y = pt(0, e3)
        x_right, _ = pt(max_e2, e3)
        svg.line(x_left, y, x_right + 30, y, stroke=GRAY_LIGHT, stroke_width=1)
        svg.text(x_left - 38, y + 4, f"e₃ = {e3}", font=FONT_SANS, size=12, fill=GRAY_DARK, anchor="end")
        svg.text(x_left - 38, y + 18, f"(3{sup(e3)}={3**e3})", font=FONT_SANS, size=11, fill=GRAY_MID, anchor="end")

    # Axes with arrows
    svg.line(gx0, gy0, gx0 + max_e2 * dx + 38, gy0, stroke=INK, stroke_width=1.5, marker_end="arrow-ink")
    svg.line(gx0, gy0, gx0, gy0 - max_e3 * dy - 36, stroke=INK, stroke_width=1.5, marker_end="arrow-ink")
    svg.text(gx0 + max_e2 * dx + 38, gy0 + 28, "exponent of 2 (e₂)", font=FONT_SERIF, size=13, style="italic", fill=INK, anchor="end")
    svg.text(gx0 - 10, gy0 - max_e3 * dy - 44, "exponent of 3 (e₃)", font=FONT_SERIF, size=13, style="italic", fill=INK)

    # Draw lattice points
    for e2 in range(max_e2 + 1):
        for e3 in range(max_e3 + 1):
            v = val_23(e2, e3)
            x, y = pt(e2, e3)
            in_a = (v in div_a)
            in_b = (v in div_b)
            in_g = (v in div_g)

            if v == g:
                # THE inhabitant of Gcd(12, 8)
                svg.circle(x, y, 14, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=3)
                svg.circle(x, y, 6, fill=PURPLE, stroke=INK, stroke_width=1.5)
                svg.pill_label(x, y - 34, f"g = {v}", font=FONT_SERIF, size=15, weight="bold", fill=PURPLE, anchor="middle")
                svg.pill_label(x, y + 44, fmt_factor_23(e2, e3), font=FONT_SANS, size=11, weight="bold", fill=PURPLE, anchor="middle")
            elif v == a:
                svg.circle(x, y, 7, fill=NAVY, stroke=BG, stroke_width=1.5)
                svg.pill_label(x + 38, y - 10, f"a = {v}", font=FONT_SERIF, size=15, weight="bold", fill=NAVY, anchor="middle")
                svg.pill_label(x + 38, y + 8, f"({fmt_factor_23(e2, e3)})", font=FONT_SANS, size=11, fill=NAVY, anchor="middle")
            elif v == b:
                svg.circle(x, y, 7, fill=NAVY, stroke=BG, stroke_width=1.5)
                svg.pill_label(x, y - 34, f"b = {v}", font=FONT_SERIF, size=15, weight="bold", fill=NAVY, anchor="middle")
                svg.pill_label(x, y + 44, f"({fmt_factor_23(e2, e3)})", font=FONT_SANS, size=11, fill=NAVY, anchor="middle")
            elif in_g:
                svg.circle(x, y, 5.5, fill=PURPLE, stroke="none")
                svg.pill_label(x + 12, y - 24, f"{v}", font=FONT_SERIF, size=14, weight="bold", fill=INK, anchor="middle")
                svg.pill_label(x, y + 44, fmt_factor_23(e2, e3), font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
            elif in_a or in_b:
                svg.circle(x, y, 5.5, fill=NAVY, stroke="none")
                svg.pill_label(x + 14, y - 10, f"{v}", font=FONT_SERIF, size=13.5, weight="bold", fill=NAVY, anchor="start")
                svg.pill_label(x + 14, y + 7, fmt_factor_23(e2, e3), font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="start")
            else:
                svg.circle(x, y, 3.5, fill=GRAY_LIGHT, stroke=GRAY_MID, stroke_width=1)
                svg.text(x + 8, y - 6, f"{v}", font=FONT_SERIF, size=12, fill=GRAY_MID)

    # Direct box annotations on canvas
    # 1. Div(12) box label (above top dashed edge)
    svg.pill_label(gx0 + dx, gy0 - dy - pad_a - 10,
                   "Div(12) = {1, 2, 3, 4, 6, 12} : dashed box ≤ (2, 1)",
                   font=FONT_SANS, size=12, weight="bold", fill=NAVY, anchor="middle")

    # 2. Div(8) box label (pointed to dotted box edge at e2=3)
    bx_edge = gx0 + 3*dx + pad_b
    svg.path(f"M {bx_edge + 2} {gy0 - 12} L {bx_edge + 36} {gy0 - 28}", stroke=NAVY, stroke_width=1.4)
    svg.pill_label(bx_edge + 40, gy0 - 34, "Div(8) = {1, 2, 4, 8}", font=FONT_SANS, size=12, weight="bold", fill=NAVY, anchor="start")
    svg.pill_label(bx_edge + 40, gy0 - 19, "dotted box ≤ (3, 0)", font=FONT_SANS, size=11, fill=NAVY, anchor="start")

    # 3. Intersection box & singleton type callout (placed cleanly between grid and right panel)
    cx_box, cy_box = 342, 316
    svg.path(f"M {gx0 + 2*dx + 12} {gy0 - 14} Q {gx0 + 2*dx + 30} {gy0 - 65} {cx_box - 4} {cy_box + 28}",
             stroke=PURPLE, stroke_width=2.0, marker_end="arrow-purple")
    svg.rect(cx_box, cy_box, 226, 62, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=1.8, rx=6)
    svg.text(cx_box + 12, cy_box + 20, "Type Gcd(12, 8) = { 4 }", font=FONT_SERIF, size=14, weight="bold", fill=PURPLE)
    svg.text(cx_box + 12, cy_box + 38, "Unique top-right corner of", font=FONT_SANS, size=12, fill=INK)
    svg.text(cx_box + 12, cy_box + 53, "Div(12) ∩ Div(8) = {1, 2, 4}", font=FONT_SANS, size=12, weight="bold", fill=PURPLE)

    # Right-side pedagogical panel: Set vs Exponent equivalence
    px, py = 592, 92
    pw, ph = 276, 290
    svg.rect(px, py, pw, ph, fill="#f7f6eb", stroke=GRAY_LIGHT, stroke_width=1.2, rx=8)
    svg.text(px + 16, py + 26, "Why a Box Has One Corner", font=FONT_SERIF, size=15, weight="bold", fill=INK)
    svg.line(px + 16, py + 34, px + pw - 16, py + 34, stroke=GRAY_LIGHT, stroke_width=1)

    svg.text(px + 16, py + 56, "1. Divisibility is coordinatewise ≤ :", font=FONT_SANS, size=12, weight="bold", fill=INK)
    svg.text(px + 24, py + 74, "d | n   ⇔   e₂(d) ≤ e₂(n)  ∧  e₃(d) ≤ e₃(n)", font=FONT_SERIF, size=12, fill=INK)
    svg.text(px + 24, py + 91, "So Div(n) is the origin-anchored box ≤ n.", font=FONT_SANS, size=11.5, fill=GRAY_DARK)

    svg.text(px + 16, py + 118, "2. Common divisors = box intersection:", font=FONT_SANS, size=12, weight="bold", fill=INK)
    svg.text(px + 24, py + 136, "Div(a) ∩ Div(b) = box ≤ min(e(a), e(b))", font=FONT_SERIF, size=12, fill=INK)
    svg.text(px + 24, py + 154, "e₂: min(2, 3) = 2", font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")
    svg.text(px + 140, py + 154, "e₃: min(1, 0) = 0", font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")

    svg.text(px + 16, py + 182, "3. The refinement type:", font=FONT_SANS, size=12, weight="bold", fill=PURPLE)
    svg.rect(px + 16, py + 191, pw - 32, 46, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=1.2, rx=4)
    svg.text(px + 24, py + 210, "Gcd(12, 8) = { g ∈ ℕ |", font=FONT_SERIF, size=12.5, weight="bold", fill=INK)
    svg.text(px + 38, py + 228, "Div(g) = Div(12) ∩ Div(8) } = { 4 }", font=FONT_SERIF, size=12.5, weight="bold", fill=PURPLE)

    svg.text(px + 16, py + 258, "Only g = 4 = 2²·3⁰ generates this exact", font=FONT_SANS, size=11.5, fill=INK)
    svg.text(px + 16, py + 273, "purple box — making the type a singleton.", font=FONT_SANS, size=11.5, fill=INK)

    svg.save("fig-1.svg")


# ==============================================================================
# FIGURE 2: Dependent Type Family — 3 Rich Cases (72,48), (13,8 coprime), (24,0 zero)
# ==============================================================================
def make_fig2():
    svg = SVGBuilder(900, 600)
    svg.add_standard_markers()

    # Title: 11 words
    draw_header(
        svg,
        "As a dependent type, Gcd(a, b) reshapes its box across every input regime.",
        "Three input pairs index three different divisor-box intersections: interior overlap (72, 48), coprime collapse (13, 8), and identity with zero (24, 0)."
    )

    # Verify numbers
    assert math.gcd(72, 48) == 24
    assert math.gcd(13, 8) == 1
    assert math.gcd(24, 0) == 24

    # Three panels side by side
    pw, ph = 266, 480
    py = 82
    panels = [
        (32,  "Panel A: Interior Overlap", "a = 72 (2³·3²),  b = 48 (2⁴·3¹)"),
        (317, "Panel B: Coprime Collapse", "a = 13 (2⁰·3⁰·13¹),  b = 8 (2³·3⁰)"),
        (602, "Panel C: Zero Identity (Div(0) = ℕ)", "a = 24 (2³·3¹),  b = 0 (unbounded)"),
    ]

    for px, ptitle, psub in panels:
        svg.rect(px, py, pw, ph, fill="#faf9ec", stroke=GRAY_LIGHT, stroke_width=1.2, rx=8)
        svg.text(px + 14, py + 24, ptitle, font=FONT_SERIF, size=14, weight="bold", fill=INK)
        svg.text(px + 14, py + 42, psub, font=FONT_SANS, size=12, fill=NAVY, weight="bold")
        svg.line(px + 14, py + 50, px + pw - 14, py + 50, stroke=GRAY_LIGHT, stroke_width=1)

    # ------------------------------------------------------------------
    # PANEL A: a = 72 (3, 2), b = 48 (4, 1) -> gcd = 24 (3, 1)
    # ------------------------------------------------------------------
    px1 = 32
    gx1, gy1 = px1 + 48, py + 315
    dx1, dy1 = 44, 62

    def pt1(e2, e3):
        return (gx1 + e2 * dx1, gy1 - e3 * dy1)

    # Box Div(72): [0..3] x [0..2]
    x0, y1_ = pt1(0, 2)
    x1, y0_ = pt1(3, 0)
    svg.rect(x0 - 16, y1_ - 16, (x1 - x0) + 32, (y0_ - y1_) + 32,
             fill="url(#hatch-navy)", stroke=NAVY, stroke_width=1.8, rx=6, dash="6,3")

    # Box Div(48): [0..4] x [0..1]
    x0, y1_ = pt1(0, 1)
    x1, y0_ = pt1(4, 0)
    svg.rect(x0 - 13, y1_ - 13, (x1 - x0) + 26, (y0_ - y1_) + 26,
             fill="none", stroke=NAVY, stroke_width=1.8, rx=6, dash="2,3")

    # Box Div(24): [0..3] x [0..1]
    x0, y1_ = pt1(0, 1)
    x1, y0_ = pt1(3, 0)
    svg.rect(x0 - 10, y1_ - 10, (x1 - x0) + 20, (y0_ - y1_) + 20,
             fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.5, rx=5)

    # Grid & axes Panel A
    for e2 in range(5):
        x, yb = pt1(e2, 0)
        _, yt = pt1(e2, 3)
        svg.line(x, yb, x, yt, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(x, yb + 26, f"{e2}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
    for e3 in range(4):
        xl, y = pt1(0, e3)
        xr, _ = pt1(4, e3)
        svg.line(xl, y, xr + 14, y, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(xl - 20, y + 4, f"{e3}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

    svg.line(gx1, gy1, gx1 + 4*dx1 + 22, gy1, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
    svg.line(gx1, gy1, gx1, gy1 - 3*dy1 - 18, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
    svg.text(gx1 + 2*dx1, gy1 + 42, "exponent e₂ (of 2)", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
    svg.text(gx1 - 32, gy1 - 1.5*dy1, "e₃", font=FONT_SERIF, size=12, style="italic", fill=GRAY_DARK, anchor="middle")

    for e2 in range(5):
        for e3 in range(4):
            v = val_23(e2, e3)
            x, y = pt1(e2, e3)
            in_g = (e2 <= 3 and e3 <= 1)
            in_ab = (e2 <= 3 and e3 <= 2) or (e2 <= 4 and e3 <= 1)
            if (e2, e3) == (3, 1):
                svg.circle(x, y, 11, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.5)
                svg.circle(x, y, 5, fill=PURPLE)
                svg.pill_label(x + 2, y - 16, "g = 24", font=FONT_SERIF, size=12.5, weight="bold", fill=PURPLE, anchor="middle")
            elif (e2, e3) == (3, 2):
                svg.circle(x, y, 5.5, fill=NAVY)
                svg.pill_label(x + 8, y - 6, "a=72", font=FONT_SERIF, size=12, weight="bold", fill=NAVY, anchor="start")
            elif (e2, e3) == (4, 1):
                svg.circle(x, y, 5.5, fill=NAVY)
                svg.pill_label(x, y - 16, "b=48", font=FONT_SERIF, size=12, weight="bold", fill=NAVY, anchor="middle")
            elif in_g:
                svg.circle(x, y, 4, fill=PURPLE)
                if e2 == 0:
                    svg.pill_label(x + 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=INK, anchor="start", bg=PURPLE_FILL, pad_x=2, pad_y=1)
                else:
                    svg.pill_label(x - 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=INK, anchor="end", bg=PURPLE_FILL, pad_x=2, pad_y=1)
            elif in_ab:
                svg.circle(x, y, 4, fill=NAVY)
                if e2 == 0:
                    svg.pill_label(x + 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=NAVY, anchor="start", pad_x=2, pad_y=1)
                else:
                    svg.pill_label(x - 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=NAVY, anchor="end", pad_x=2, pad_y=1)
            else:
                svg.circle(x, y, 2.5, fill=GRAY_LIGHT)

    # Panel A bottom summary
    svg.rect(px1 + 14, py + 370, pw - 28, 94, fill=BG, stroke=PURPLE, stroke_width=1.2, rx=5)
    svg.text(px1 + 22, py + 390, "min((3, 2), (4, 1)) = (3, 1)", font=FONT_SERIF, size=12.5, weight="bold", fill=PURPLE)
    svg.text(px1 + 22, py + 408, "8 common divisors in 4×2 box:", font=FONT_SANS, size=11.5, fill=INK)
    svg.text(px1 + 22, py + 424, "{1, 2, 3, 4, 6, 8, 12, 24}", font=FONT_SERIF, size=11.5, fill=INK)
    svg.text(px1 + 22, py + 448, "Gcd(72, 48) = { 24 }", font=FONT_SERIF, size=13, weight="bold", fill=PURPLE)

    # ------------------------------------------------------------------
    # PANEL B: Coprime Collapse a = 13, b = 8 -> gcd = 1
    # Orthogonal axes e2 (horizontal) and e13 (vertical)
    # ------------------------------------------------------------------
    px2 = 317
    gx2, gy2 = px2 + 52, py + 315
    dx2, dy2 = 44, 62

    def pt2(e2, e13):
        return (gx2 + e2 * dx2, gy2 - e13 * dy2)

    # Box Div(13): [0..0] x [0..1] along vertical axis e13
    x0, y1_ = pt2(0, 1)
    x1, y0_ = pt2(0, 0)
    svg.rect(x0 - 16, y1_ - 16, (x1 - x0) + 32, (y0_ - y1_) + 32,
             fill="url(#hatch-navy)", stroke=NAVY, stroke_width=1.8, rx=6, dash="6,3")

    # Box Div(8): [0..3] x [0..0] along horizontal axis e2
    x0, y1_ = pt2(0, 0)
    x1, y0_ = pt2(3, 0)
    svg.rect(x0 - 14, y1_ - 14, (x1 - x0) + 28, (y0_ - y1_) + 28,
             fill="none", stroke=NAVY, stroke_width=1.8, rx=6, dash="2,3")

    # Intersection Box Div(1): [0..0] x [0..0] at origin!
    x0, y0_ = pt2(0, 0)
    svg.rect(x0 - 11, y0_ - 11, 22, 22,
             fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.5, rx=5)

    for e2 in range(5):
        x, yb = pt2(e2, 0)
        _, yt = pt2(e2, 2)
        svg.line(x, yb, x, yt - 20, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(x, yb + 26, f"{e2}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
    for e13 in range(3):
        xl, y = pt2(0, e13)
        xr, _ = pt2(4, e13)
        svg.line(xl, y, xr + 14, y, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(xl - 20, y + 4, f"{e13}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

    svg.line(gx2, gy2, gx2 + 4*dx2 + 22, gy2, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
    svg.line(gx2, gy2, gx2, gy2 - 2*dy2 - 35, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
    svg.text(gx2 + 2*dx2, gy2 + 42, "exponent e₂ (of 2)", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
    svg.text(gx2 - 30, gy2 - 1.2*dy2, "e₁₃", font=FONT_SERIF, size=12, style="italic", fill=GRAY_DARK, anchor="middle")

    for e2 in range(5):
        for e13 in range(3):
            v = (2 ** e2) * (13 ** e13)
            x, y = pt2(e2, e13)
            if (e2, e13) == (0, 0):
                svg.circle(x, y, 8, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2)
                svg.circle(x, y, 4.5, fill=PURPLE)
                svg.path(f"M {x + 8} {y - 8} L {x + 22} {y - 28}", stroke=PURPLE, stroke_width=1.5)
                svg.pill_label(x + 24, y - 30, "g = 1", font=FONT_SERIF, size=13, weight="bold", fill=PURPLE, anchor="start")
            elif (e2, e13) == (0, 1):
                svg.circle(x, y, 5.5, fill=NAVY)
                svg.pill_label(x + 16, y - 6, "a = 13 (2⁰·13¹)", font=FONT_SERIF, size=12, weight="bold", fill=NAVY, anchor="start")
            elif (e2, e13) == (3, 0):
                svg.circle(x, y, 5.5, fill=NAVY)
                svg.pill_label(x, y - 18, "b = 8", font=FONT_SERIF, size=12, weight="bold", fill=NAVY, anchor="middle")
            elif e13 == 0 and e2 <= 3:
                svg.circle(x, y, 4, fill=NAVY)
                svg.text(x, y - 16, f"{v}", font=FONT_SANS, size=11, fill=NAVY, anchor="middle")
            else:
                svg.circle(x, y, 2.5, fill=GRAY_LIGHT)
                if e2 == 3 and e13 == 1:
                    svg.text(x + 6, y - 6, f"{v}", font=FONT_SANS, size=11, fill=GRAY_MID)

    # Panel B annotation
    svg.pill_label(gx2 + 2.1*dx2, gy2 - 2*dy2 - 12, "Orthogonal prime axes", font=FONT_SANS, size=12, weight="bold", fill=INK, anchor="middle")
    svg.pill_label(gx2 + 2.1*dx2, gy2 - 2*dy2 + 5, "meet ONLY at origin (0, 0)!", font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold", anchor="middle")

    svg.rect(px2 + 14, py + 370, pw - 28, 94, fill=BG, stroke=PURPLE, stroke_width=1.2, rx=5)
    svg.text(px2 + 22, py + 390, "min((0, 1), (3, 0)) = (0, 0)", font=FONT_SERIF, size=12.5, weight="bold", fill=PURPLE)
    svg.text(px2 + 22, py + 408, "1×1 box at origin: only 2⁰·13⁰ = 1", font=FONT_SANS, size=11.5, fill=INK)
    svg.text(px2 + 22, py + 424, "Div(13) ∩ Div(8) = { 1 }", font=FONT_SERIF, size=11.5, fill=INK)
    svg.text(px2 + 22, py + 448, "Gcd(13, 8) = { 1 }  (coprime)", font=FONT_SERIF, size=13, weight="bold", fill=PURPLE)

    # ------------------------------------------------------------------
    # PANEL C: Zero Identity a = 24 (2^3 * 3^1), b = 0 (unbounded) -> gcd = 24
    # ------------------------------------------------------------------
    px3 = 602
    gx3, gy3 = px3 + 48, py + 315
    dx3, dy3 = 44, 62

    def pt3(e2, e3):
        return (gx3 + e2 * dx3, gy3 - e3 * dy3)

    # Unbounded quadrant for Div(0) = all of N (e2 < inf, e3 < inf)
    qx0, qy1 = pt3(0, 3)
    qx1, qy0 = pt3(4, 0)
    svg.rect(qx0 - 15, qy1 - 28, (qx1 - qx0) + 33, (qy0 - qy1) + 43,
             fill="url(#hatch-navy)", stroke=NAVY, stroke_width=1.5, rx=6, dash="4,4")
    svg.pill_label(qx0 + 88, qy1 - 12, "Div(0) = ℕ : unbounded (∞, ∞) ↗", font=FONT_SANS, size=11, weight="bold", fill=NAVY, anchor="middle")

    # Box Div(24) AND Intersection Div(24) ∩ Div(0) = Div(24): [0..3] x [0..1]
    x0, y1_ = pt3(0, 1)
    x1, y0_ = pt3(3, 0)
    svg.rect(x0 - 11, y1_ - 11, (x1 - x0) + 22, (y0_ - y1_) + 22,
             fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.8, rx=6)
    svg.rect(x0 - 14, y1_ - 14, (x1 - x0) + 28, (y0_ - y1_) + 28,
             fill="none", stroke=NAVY, stroke_width=1.5, rx=7, dash="6,3")

    for e2 in range(5):
        x, yb = pt3(e2, 0)
        _, yt = pt3(e2, 3)
        svg.line(x, yb, x, yt - 4, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(x, yb + 26, f"{e2}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
    for e3 in range(4):
        xl, y = pt3(0, e3)
        xr, _ = pt3(4, e3)
        svg.line(xl, y, xr + 14, y, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(xl - 20, y + 4, f"{e3}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

    svg.line(gx3, gy3, gx3 + 4*dx3 + 22, gy3, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
    svg.line(gx3, gy3, gx3, gy3 - 3*dy3 - 18, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
    svg.text(gx3 + 2*dx3, gy3 + 42, "exponent e₂ (of 2)", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
    svg.text(gx3 - 32, gy3 - 1.5*dy3, "e₃", font=FONT_SERIF, size=12, style="italic", fill=GRAY_DARK, anchor="middle")

    for e2 in range(5):
        for e3 in range(4):
            v = val_23(e2, e3)
            x, y = pt3(e2, e3)
            in_24 = (e2 <= 3 and e3 <= 1)
            if (e2, e3) == (3, 1):
                svg.circle(x, y, 11, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.5)
                svg.circle(x, y, 5, fill=PURPLE)
                svg.pill_label(x + 4, y - 16, "a = g = 24", font=FONT_SERIF, size=12, weight="bold", fill=PURPLE, anchor="middle")
            elif in_24:
                svg.circle(x, y, 4, fill=PURPLE)
                if e2 == 0:
                    svg.pill_label(x + 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=INK, anchor="start", bg=PURPLE_FILL, pad_x=2, pad_y=1)
                else:
                    svg.pill_label(x - 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=INK, anchor="end", bg=PURPLE_FILL, pad_x=2, pad_y=1)
            else:
                svg.circle(x, y, 3.5, fill=NAVY, opacity=0.45)
                if e3 <= 2:
                    if e2 == 0:
                        svg.pill_label(x + 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=NAVY, anchor="start", pad_x=2, pad_y=1)
                    else:
                        svg.pill_label(x - 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=NAVY, anchor="end", pad_x=2, pad_y=1)

    # Panel C bottom summary
    svg.rect(px3 + 14, py + 370, pw - 28, 94, fill=BG, stroke=PURPLE, stroke_width=1.2, rx=5)
    svg.text(px3 + 22, py + 390, "min((3, 1), (∞, ∞)) = (3, 1)", font=FONT_SERIF, size=12.5, weight="bold", fill=PURPLE)
    svg.text(px3 + 22, py + 408, "Every d ∈ ℕ divides 0 (0 = d · 0),", font=FONT_SANS, size=11.5, fill=INK)
    svg.text(px3 + 22, py + 424, "so Div(24) ∩ ℕ = Div(24).", font=FONT_SERIF, size=11.5, fill=INK)
    svg.text(px3 + 22, py + 448, "Gcd(24, 0) = { 24 }  (base case!)", font=FONT_SERIF, size=13, weight="bold", fill=PURPLE)

    svg.save("fig-2.svg")


# ==============================================================================
# FIGURE 3: Type Errors — Wrong Candidates Have Mismatched Boxes
# ==============================================================================
def make_fig3():
    svg = SVGBuilder(900, 610)
    svg.add_standard_markers()

    # Title: 11 words
    draw_header(
        svg,
        "A type error occurs whenever a candidate's box misses the target intersection.",
        "For inputs a = 12 (2²·3¹) and b = 8 (2³·3⁰), target type Gcd(12, 8) requires Div(g) = {1, 2, 4} (box [0, 2] × [0, 0]). Every other point fails."
    )

    # Three error cases side-by-side for (a=12, b=8)
    pw, ph = 266, 485
    py = 82
    panels = [
        (32,  "Error 1: Box Too Small (g = 2)", "Common divisor, but NOT greatest"),
        (317, "Error 2: Box Overflows b (g = 12)", "Divides a = 12, but fails to divide b = 8"),
        (602, "Error 3: Box Overflows a (g = 8)",  "Divides b = 8, but fails to divide a = 12"),
    ]

    for px, ptitle, psub in panels:
        svg.rect(px, py, pw, ph, fill="#faf9ec", stroke=RED, stroke_width=1.5, rx=8)
        svg.rect(px, py, pw, 48, fill=RED_FILL, stroke=RED, stroke_width=1.5, rx=8)
        svg.text(px + 12, py + 21, ptitle, font=FONT_SERIF, size=13.5, weight="bold", fill=RED)
        svg.text(px + 12, py + 39, psub, font=FONT_SANS, size=11.5, fill=INK)

    def draw_base_grid(px, cand_e2, cand_e3, mode):
        gx, gy = px + 48, py + 280
        dx, dy = 48, 86

        def pt(e2, e3):
            return (gx + e2 * dx, gy - e3 * dy)

        # Target box Div(12) ∩ Div(8) = [0..2] x [0..0] in purple
        tx0, ty1 = pt(0, 0)
        tx1, ty0 = pt(2, 0)

        if mode == "too_small":
            svg.rect(tx0 - 14, ty1 - 16, (tx1 - tx0) + 28, 32,
                     fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2, rx=6, dash="5,3")
            # Missing cell around (2,0) = 4
            mx, my = pt(2, 0)
            svg.rect(mx - 18, my - 18, 36, 36,
                     fill="url(#hatch-red)", stroke=RED, stroke_width=2, rx=5)
            # Candidate box [0..1]x[0..0]
            cx1, cy0 = pt(1, 0)
            svg.rect(tx0 - 10, ty1 - 11, (cx1 - tx0) + 20, 22,
                     fill="none", stroke=RED, stroke_width=2.5, rx=4)

        elif mode == "overflow_b":
            ox0, oy1 = pt(0, 1)
            ox1, oy0 = pt(2, 1)
            # Candidate full box
            svg.rect(ox0 - 15, oy1 - 16, (ox1 - ox0) + 30, (ty0 - oy1) + 32,
                     fill=RED_FILL, stroke=RED, stroke_width=2.5, rx=6)
            # Hatch the illegal top row {3, 6, 12}
            svg.rect(ox0 - 13, oy1 - 14, (ox1 - ox0) + 26, 32,
                     fill="url(#hatch-red)", stroke=RED, stroke_width=1.5, rx=4)
            # Target box [0..2]x[0..0]
            svg.rect(tx0 - 11, ty1 - 12, (tx1 - tx0) + 22, 24,
                     fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2, rx=4, dash="5,3")

        elif mode == "overflow_a":
            ox1, oy0 = pt(3, 0)
            svg.rect(tx0 - 15, ty1 - 16, (ox1 - tx0) + 30, 32,
                     fill=RED_FILL, stroke=RED, stroke_width=2.5, rx=6)
            # Hatch illegal cell at (3,0)=8
            mx, my = pt(3, 0)
            svg.rect(mx - 18, my - 18, 36, 36,
                     fill="url(#hatch-red)", stroke=RED, stroke_width=1.8, rx=4)
            # Target box [0..2]x[0..0]
            svg.rect(tx0 - 11, ty1 - 12, (tx1 - tx0) + 22, 24,
                     fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2, rx=4, dash="5,3")

        # Grid lines (only e3=0 and e3=1)
        for e2 in range(4):
            x, yb = pt(e2, 0)
            _, yt = pt(e2, 1)
            svg.line(x, yb, x, yt - 55, stroke=GRAY_LIGHT, stroke_width=0.8)
            svg.text(x, yb + 30, f"e₂={e2}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
        for e3 in range(2):
            xl, y = pt(0, e3)
            xr, _ = pt(3, e3)
            svg.line(xl, y, xr + 16, y, stroke=GRAY_LIGHT, stroke_width=0.8)
            svg.text(xl - 18, y + 4, f"e₃={e3}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

        svg.line(gx, gy, gx + 3*dx + 24, gy, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
        svg.line(gx, gy, gx, gy - dy - 62, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")

        # Plot points
        for e2 in range(4):
            for e3 in range(2):
                v = val_23(e2, e3)
                x, y = pt(e2, e3)
                is_cand = (e2 == cand_e2 and e3 == cand_e3)
                is_true_g = (e2 == 2 and e3 == 0)

                if is_cand:
                    svg.circle(x, y, 10, fill=RED_FILL, stroke=RED, stroke_width=2.5)
                    svg.circle(x, y, 4.5, fill=RED)
                    svg.pill_label(x, y - 20, f"✗ g={v}", font=FONT_SERIF, size=12.5, weight="bold", fill=RED, anchor="middle")
                elif is_true_g:
                    svg.circle(x, y, 6, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2)
                    svg.pill_label(x, y - 22, "4 (gcd)", font=FONT_SANS, size=11, weight="bold", fill=PURPLE, anchor="middle")
                elif e2 <= 2 and e3 == 0:
                    svg.circle(x, y, 4.5, fill=PURPLE)
                    svg.pill_label(x + 8, y - 15, f"{v}", font=FONT_SANS, size=11, fill=INK, anchor="start")
                elif (e2 <= 2 and e3 <= 1) or (e2 == 3 and e3 == 0):
                    col = RED if ((mode == "overflow_b" and e3 == 1 and e2 <= 2) or (mode == "overflow_a" and e2 == 3 and e3 == 0)) else NAVY
                    svg.circle(x, y, 4.5, fill=col)
                    svg.pill_label(x + 8, y - 12, f"{v}", font=FONT_SANS, size=11, weight="bold" if col == RED else "normal", fill=col, anchor="start")
                else:
                    svg.circle(x, y, 2.5, fill=GRAY_LIGHT)
                    svg.text(x + 6, y - 4, f"{v}", font=FONT_SANS, size=11, fill=GRAY_MID)

        return pt

    # Draw Panel 1: g = 2 (1, 0)
    pt_p1 = draw_base_grid(32, 1, 0, "too_small")
    mx, my = pt_p1(2, 0)
    # Place callout cleanly in top region above e3=1 row!
    svg.path(f"M {mx + 14} {my - 20} L {mx + 14} {my - 118}", stroke=RED, stroke_width=1.5, marker_end="arrow-red")
    svg.pill_label(mx - 12, my - 138, "Missing common divisor d = 4!", font=FONT_SANS, size=11.5, weight="bold", fill=RED, anchor="middle")
    svg.pill_label(mx - 12, my - 123, "(4 | 12 and 4 | 8, but 4 ∤ 2)", font=FONT_SANS, size=11, fill=RED, anchor="middle")

    # Panel 1 verdict box
    px1 = 32
    svg.rect(px1 + 12, py + 335, pw - 24, 136, fill=BG, stroke=RED, stroke_width=1.4, rx=5)
    svg.text(px1 + 20, py + 355, "Candidate: g = 2  (2¹·3⁰)", font=FONT_SERIF, size=12.5, weight="bold", fill=RED)
    svg.text(px1 + 20, py + 374, "• Div(2) = {1, 2}  ⊂  Div(12) ∩ Div(8)", font=FONT_SERIF, size=11.5, fill=INK)
    svg.text(px1 + 20, py + 394, "• Violated clause:", font=FONT_SANS, size=11.5, weight="bold", fill=RED)
    svg.text(px1 + 28, py + 411, "∀d. d | 12 ∧ d | 8  →  d | g", font=FONT_SERIF, size=12, fill=RED, weight="bold")
    svg.text(px1 + 20, py + 432, "• Counterexample Witness: d = 4", font=FONT_SANS, size=11.5, weight="bold", fill=RED)
    svg.text(px1 + 28, py + 449, "e₂(2) = 1 < min(2, 3) = 2   [TYPE ERROR]", font=FONT_SANS, size=11, weight="bold", fill=RED)

    # Draw Panel 2: g = 12 (2, 1)
    pt_p2 = draw_base_grid(317, 2, 1, "overflow_b")
    ox, oy = pt_p2(1, 1)
    svg.pill_label(ox + 15, oy - 50, "Illegal row e₃ = 1: {3, 6, 12} ∤ 8!", font=FONT_SANS, size=11.5, weight="bold", fill=RED, anchor="middle")
    svg.pill_label(ox + 15, oy - 35, "(e₃ = 1 exceeds e₃(8) = 0)", font=FONT_SANS, size=11, fill=RED, anchor="middle")

    px2 = 317
    svg.rect(px2 + 12, py + 335, pw - 24, 136, fill=BG, stroke=RED, stroke_width=1.4, rx=5)
    svg.text(px2 + 20, py + 355, "Candidate: g = 12  (2²·3¹)", font=FONT_SERIF, size=12.5, weight="bold", fill=RED)
    svg.text(px2 + 20, py + 374, "• Div(12) = {1,2,3,4,6,12} ⊄ Div(8)", font=FONT_SERIF, size=11.5, fill=INK)
    svg.text(px2 + 20, py + 394, "• Violated clause:", font=FONT_SANS, size=11.5, weight="bold", fill=RED)
    svg.text(px2 + 28, py + 411, "g | b   (requires 12 | 8, false!)", font=FONT_SERIF, size=12, fill=RED, weight="bold")
    svg.text(px2 + 20, py + 432, "• Counterexample Witness: d ∈ {3, 6, 12}", font=FONT_SANS, size=11.5, weight="bold", fill=RED)
    svg.text(px2 + 28, py + 449, "e₃(12) = 1 > e₃(8) = 0   [TYPE ERROR]", font=FONT_SANS, size=11, weight="bold", fill=RED)

    # Draw Panel 3: g = 8 (3, 0)
    pt_p3 = draw_base_grid(602, 3, 0, "overflow_a")
    ox3, oy3 = pt_p3(3, 0)
    svg.path(f"M {ox3} {oy3 - 34} L {ox3} {oy3 - 118}", stroke=RED, stroke_width=1.5, marker_end="arrow-red")
    svg.pill_label(ox3 - 36, oy3 - 138, "Overflow: 8 ∤ 12!", font=FONT_SANS, size=11.5, weight="bold", fill=RED, anchor="middle")
    svg.pill_label(ox3 - 36, oy3 - 123, "(e₂ = 3 exceeds e₂(12) = 2)", font=FONT_SANS, size=11, fill=RED, anchor="middle")

    px3 = 602
    svg.rect(px3 + 12, py + 335, pw - 24, 136, fill=BG, stroke=RED, stroke_width=1.4, rx=5)
    svg.text(px3 + 20, py + 355, "Candidate: g = 8  (2³·3⁰)", font=FONT_SERIF, size=12.5, weight="bold", fill=RED)
    svg.text(px3 + 20, py + 374, "• Div(8) = {1, 2, 4, 8}  ⊄  Div(12)", font=FONT_SERIF, size=11.5, fill=INK)
    svg.text(px3 + 20, py + 394, "• Violated clause:", font=FONT_SANS, size=11.5, weight="bold", fill=RED)
    svg.text(px3 + 28, py + 411, "g | a   (requires 8 | 12, false!)", font=FONT_SERIF, size=12, fill=RED, weight="bold")
    svg.text(px3 + 20, py + 432, "• Counterexample Witness: d = 8", font=FONT_SANS, size=11.5, weight="bold", fill=RED)
    svg.text(px3 + 28, py + 449, "e₂(8) = 3 > e₂(12) = 2   [TYPE ERROR]", font=FONT_SANS, size=11, weight="bold", fill=RED)

    svg.save("fig-3.svg")


# ==============================================================================
# FIGURE 4: Euclid's Algorithm Preserves the Intersection Box Until y = 0
# ==============================================================================
def make_fig4():
    svg = SVGBuilder(900, 580)
    svg.add_standard_markers()

    # Title: 11 words
    draw_header(
        svg,
        "Euclid's loop moves the outer boxes while locking their purple intersection.",
        "Trace on (72, 48) → (48, 24) → (24, 0): each modulo step (x, y) ↦ (y, x mod y) changes exponents of x, y but preserves Div(x) ∩ Div(y)."
    )

    # Verify Euclid trace in Python
    steps = []
    x, y = 72, 48
    while True:
        steps.append((x, y))
        if y == 0:
            break
        x, y = y, x % y
    assert steps == [(72, 48), (48, 24), (24, 0)]

    pw, ph = 266, 460
    py = 82
    configs = [
        (32,  "Step 0: Initial Inputs",     72, 48, "x = 72 (3, 2),  y = 48 (4, 1)", "72 mod 48 = 24"),
        (317, "Step 1: After First Modulo", 48, 24, "x = 48 (4, 1),  y = 24 (3, 1)", "48 mod 24 = 0"),
        (602, "Step 2: Termination (y = 0)", 24, 0,  "x = 24 (3, 1),  y = 0 (∞, ∞)", "Return x = 24 : Gcd(72, 48)"),
    ]

    for idx, (px, stitle, xv, yv, sub, trans_label) in enumerate(configs):
        svg.rect(px, py, pw, ph, fill="#faf9ec", stroke=GRAY_LIGHT, stroke_width=1.2, rx=8)
        svg.text(px + 14, py + 24, stitle, font=FONT_SERIF, size=14, weight="bold", fill=INK)
        svg.text(px + 14, py + 42, sub, font=FONT_SANS, size=12, weight="bold", fill=NAVY)
        svg.line(px + 14, py + 50, px + pw - 14, py + 50, stroke=GRAY_LIGHT, stroke_width=1)

        gx, gy = px + 46, py + 285
        dx, dy = 44, 62

        def pt(e2, e3):
            return (gx + e2 * dx, gy - e3 * dy)

        # Draw outer boxes for Div(x) and Div(y)
        if idx == 0:
            # x=72 (3,2), y=48 (4,1)
            x0, y1_ = pt(0, 2)
            x1, y0_ = pt(3, 0)
            svg.rect(x0 - 15, y1_ - 15, (x1 - x0) + 30, (y0_ - y1_) + 30,
                     fill="url(#hatch-navy)", stroke=NAVY, stroke_width=1.8, rx=6, dash="6,3")
            x0, y1_ = pt(0, 1)
            x1, y0_ = pt(4, 0)
            svg.rect(x0 - 13, y1_ - 13, (x1 - x0) + 26, (y0_ - y1_) + 26,
                     fill="none", stroke=NAVY, stroke_width=1.8, rx=6, dash="2,3")
        elif idx == 1:
            # x=48 (4,1), y=24 (3,1)
            x0, y1_ = pt(0, 1)
            x1, y0_ = pt(4, 0)
            svg.rect(x0 - 15, y1_ - 15, (x1 - x0) + 30, (y0_ - y1_) + 30,
                     fill="url(#hatch-navy)", stroke=NAVY, stroke_width=1.8, rx=6, dash="6,3")
        elif idx == 2:
            # x=24 (3,1), y=0 (inf, inf)
            qx0, qy1 = pt(0, 2)
            qx1, qy0 = pt(4, 0)
            svg.rect(qx0 - 15, qy1 - 35, (qx1 - qx0) + 35, (qy0 - qy1) + 50,
                     fill="url(#hatch-navy)", stroke=NAVY, stroke_width=1.5, rx=6, dash="4,4")
            svg.pill_label(qx0 + 92, qy1 - 16, "Div(y=0) = ℕ (unbounded ↗)", font=FONT_SANS, size=11, weight="bold", fill=NAVY, anchor="middle")

        # INVARIANT PURPLE BOX: Div(x) ∩ Div(y) = [0..3] x [0..1] in ALL 3 STEPS!
        ix0, iy1 = pt(0, 1)
        ix1, iy0 = pt(3, 0)
        svg.rect(ix0 - 10, iy1 - 10, (ix1 - ix0) + 20, (iy0 - iy1) + 20,
                 fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.8, rx=5)

        # Grid
        for e2 in range(5):
            x, yb = pt(e2, 0)
            _, yt = pt(e2, 2)
            svg.line(x, yb, x, yt - 25, stroke=GRAY_LIGHT, stroke_width=0.8)
            svg.text(x, yb + 24, f"{e2}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
        for e3 in range(3):
            xl, y = pt(0, e3)
            xr, _ = pt(4, e3)
            svg.line(xl, y, xr + 14, y, stroke=GRAY_LIGHT, stroke_width=0.8)
            svg.text(xl - 18, y + 4, f"{e3}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

        svg.line(gx, gy, gx + 4*dx + 20, gy, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
        svg.line(gx, gy, gx, gy - 2*dy - 35, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")

        # Points
        for e2 in range(5):
            for e3 in range(3):
                v = val_23(e2, e3)
                x, y = pt(e2, e3)
                in_inv = (e2 <= 3 and e3 <= 1)
                if (e2, e3) == (3, 1):
                    svg.circle(x, y, 10, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.5)
                    svg.circle(x, y, 4.5, fill=PURPLE)
                    lbl = "24" if idx == 0 else ("y=24" if idx == 1 else "x=24 ✓")
                    svg.pill_label(x, y - 16, lbl, font=FONT_SERIF, size=12, weight="bold", fill=PURPLE, anchor="middle")
                elif idx == 0 and (e2, e3) == (3, 2):
                    svg.circle(x, y, 5.5, fill=NAVY)
                    svg.pill_label(x + 8, y - 6, "x=72", font=FONT_SERIF, size=12, weight="bold", fill=NAVY, anchor="start")
                elif idx == 0 and (e2, e3) == (4, 1):
                    svg.circle(x, y, 5.5, fill=NAVY)
                    svg.pill_label(x, y - 18, "y=48", font=FONT_SERIF, size=12, weight="bold", fill=NAVY, anchor="middle")
                elif idx == 1 and (e2, e3) == (4, 1):
                    svg.circle(x, y, 5.5, fill=NAVY)
                    svg.pill_label(x, y - 18, "x=48", font=FONT_SERIF, size=12, weight="bold", fill=NAVY, anchor="middle")
                elif in_inv:
                    svg.circle(x, y, 4, fill=PURPLE)
                    if e2 == 0:
                        svg.pill_label(x + 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=INK, anchor="start", bg=PURPLE_FILL, pad_x=2, pad_y=1)
                    else:
                        svg.pill_label(x - 8, y - 6, f"{v}", font=FONT_SANS, size=11, fill=INK, anchor="end", bg=PURPLE_FILL, pad_x=2, pad_y=1)
                else:
                    svg.circle(x, y, 2.5, fill=GRAY_LIGHT)

        # Invariant status box at bottom of each panel
        svg.rect(px + 14, py + 325, pw - 28, 120, fill=BG, stroke=PURPLE, stroke_width=1.4, rx=5)
        svg.text(px + 22, py + 345, "Loop Invariant:", font=FONT_SANS, size=11.5, weight="bold", fill=PURPLE)
        svg.text(px + 22, py + 363, f"Div({xv}) ∩ Div({yv}) = Div(72) ∩ Div(48)", font=FONT_SERIF, size=11.5, weight="bold", fill=INK)
        svg.text(px + 22, py + 382, "Purple box FIXED at [0, 3] × [0, 1]", font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")
        if idx < 2:
            svg.text(px + 22, py + 404, f"Next step: {trans_label}", font=FONT_SANS, size=11.5, fill=NAVY, weight="bold")
            svg.text(px + 22, py + 422, "Outer box shrinks toward corner (3,1).", font=FONT_SANS, size=11, fill=GRAY_DARK)
        else:
            svg.text(px + 22, py + 404, "Since Div(0) = ℕ, Div(x) ∩ ℕ = Div(x).", font=FONT_SANS, size=11.5, fill=INK)
            svg.text(px + 22, py + 423, "∴ x = 24 inhabits Gcd(72, 48)! ∎", font=FONT_SERIF, size=12, weight="bold", fill=PURPLE)

    # Arrows connecting panels
    svg.path("M 299 240 L 315 240", stroke=PURPLE, stroke_width=2.5, marker_end="arrow-purple")
    svg.path("M 584 240 L 600 240", stroke=PURPLE, stroke_width=2.5, marker_end="arrow-purple")

    svg.save("fig-4.svg")


# ==============================================================================
# FIGURE 5: Beyond 2D — Arbitrary Primes via Small Multiples (1071, 462 -> 21)
# ==============================================================================
def make_fig5():
    svg = SVGBuilder(900, 620)
    svg.add_standard_markers()

    # Title: 11 words
    draw_header(
        svg,
        "Beyond two primes, high-dimensional divisor boxes decompose into per-prime minimum bars.",
        "For a = 1071 (3²·7¹·17¹) and b = 462 (2¹·3¹·7¹·11¹), the 5-D hyperbox [0, e_p] factors into independent 1-D intervals."
    )

    # Verify numbers in Python
    a, b = 1071, 462
    g = math.gcd(a, b)
    assert g == 21
    primes = [2, 3, 7, 11, 17]
    fa = factorize(a, primes)
    fb = factorize(b, primes)
    fg = factorize(g, primes)
    assert fa == {2: 0, 3: 2, 7: 1, 11: 0, 17: 1}
    assert fb == {2: 1, 3: 1, 7: 1, 11: 1, 17: 0}
    assert fg == {2: 0, 3: 1, 7: 1, 11: 0, 17: 0}

    # Top panel: Small Multiples of 1D Prime-Exponent Intervals
    top_x, top_y = 36, 82
    top_w, top_h = 828, 255
    svg.rect(top_x, top_y, top_w, top_h, fill="#faf9ec", stroke=GRAY_LIGHT, stroke_width=1.2, rx=8)
    svg.text(top_x + 18, top_y + 25,
             "5-D Hyperbox Decomposition: Each prime p ∈ {2, 3, 7, 11, 17} is an orthogonal coordinate axis",
             font=FONT_SERIF, size=14, weight="bold", fill=INK)
    svg.text(top_x + 18, top_y + 44,
             "Div(1071) has 3×2×2 = 12 divisors; Div(462) has 2×2×2×2 = 16 divisors. Their intersection is the Cartesian product of the purple intervals:",
             font=FONT_SANS, size=12, fill=GRAY_DARK)

    # Draw 5 prime columns
    col_w = 152
    for idx, p in enumerate(primes):
        cx = top_x + 22 + idx * 160
        cy = top_y + 60
        ch = 180
        ea, eb, eg = fa[p], fb[p], fg[p]

        svg.rect(cx, cy, col_w, ch, fill=BG, stroke=GRAY_LIGHT, stroke_width=1, rx=6)
        svg.text(cx + col_w/2, cy + 20, f"Prime p = {p}", font=FONT_SERIF, size=13.5, weight="bold", fill=INK, anchor="middle")
        svg.line(cx + 10, cy + 28, cx + col_w - 10, cy + 28, stroke=GRAY_LIGHT, stroke_width=0.8)

        # Vertical 1D axis for e_p from 0 to 2
        ay_bot = cy + 128
        ay_step = 36
        ax_mid = cx + 76

        # Axis line
        svg.line(ax_mid, ay_bot, ax_mid, ay_bot - 2 * ay_step - 16, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")

        for ep in range(3):
            yy = ay_bot - ep * ay_step
            svg.line(ax_mid - 28, yy, ax_mid + 28, yy, stroke=GRAY_LIGHT, stroke_width=0.8)
            svg.text(ax_mid - 34, yy + 4, f"e={ep}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

        # Bar for a (left of axis)
        ba_x = ax_mid - 20
        ba_top = ay_bot - ea * ay_step
        svg.rect(ba_x - 8, ba_top - 5, 12, (ay_bot - ba_top) + 10, fill="url(#hatch-navy)", stroke=NAVY, stroke_width=1.5, rx=3)
        svg.circle(ba_x - 2, ba_top, 4, fill=NAVY)
        svg.text(ba_x - 2, ba_top - 9, f"a:{ea}", font=FONT_SANS, size=11, weight="bold", fill=NAVY, anchor="middle")

        # Bar for b (right of axis)
        bb_x = ax_mid + 12
        bb_top = ay_bot - eb * ay_step
        svg.rect(bb_x - 4, bb_top - 5, 12, (ay_bot - bb_top) + 10, fill="none", stroke=NAVY, stroke_width=1.5, rx=3, dash="2,2")
        svg.circle(bb_x + 2, bb_top, 4, fill=NAVY)
        svg.text(bb_x + 6, bb_top - 9, f"b:{eb}", font=FONT_SANS, size=11, weight="bold", fill=NAVY, anchor="start")

        # Purple interval for min(ea, eb) right on the axis
        bg_top = ay_bot - eg * ay_step
        svg.rect(ax_mid - 6, bg_top - 6, 12, (ay_bot - bg_top) + 12, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2, rx=4)
        svg.circle(ax_mid, bg_top, 5, fill=PURPLE)

        # Bottom summary of this prime's contribution
        factor_val = p ** eg
        status = f"min({ea},{eb}) = {eg}"
        svg.text(cx + col_w/2, cy + 152, status, font=FONT_SERIF, size=12, weight="bold", fill=PURPLE, anchor="middle")
        svg.text(cx + col_w/2, cy + 170, f"factor {p}{sup(eg)} = {factor_val}", font=FONT_SANS, size=11.5, weight="bold" if eg > 0 else "normal", fill=PURPLE if eg > 0 else GRAY_MID, anchor="middle")

    # Bottom Left Panel: The Resulting 2D Active Slice (primes 3 and 7 where min > 0)
    bl_x, bl_y = 36, 352
    bl_w, bl_h = 415, 245
    svg.rect(bl_x, bl_y, bl_w, bl_h, fill="#faf9ec", stroke=PURPLE, stroke_width=1.5, rx=8)
    svg.text(bl_x + 16, bl_y + 24, "Active Subspace Projection (p = 3 × p = 7)", font=FONT_SERIF, size=14, weight="bold", fill=INK)
    svg.text(bl_x + 16, bl_y + 42, "Primes with min = 0 (2, 11, 17) collapse to e_p = 0:", font=FONT_SANS, size=11.5, fill=GRAY_DARK)

    gx, gy = bl_x + 70, bl_y + 185
    dx, dy = 82, 58

    def pt_37(e3, e7):
        return (gx + e3 * dx, gy - e7 * dy)

    # Active intersection box [0..1] x [0..1] in (e3, e7)
    x0, y1_ = pt_37(0, 1)
    x1, y0_ = pt_37(1, 0)
    svg.rect(x0 - 16, y1_ - 16, (x1 - x0) + 32, (y0_ - y1_) + 32,
             fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.5, rx=6)

    for e3 in range(3):
        x, yb = pt_37(e3, 0)
        _, yt = pt_37(e3, 1)
        svg.line(x, yb, x, yt - 25, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(x, yb + 24, f"e₃={e3} (3{sup(e3)})", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
    for e7 in range(2):
        xl, y = pt_37(0, e7)
        xr, _ = pt_37(2, e7)
        svg.line(xl, y, xr + 25, y, stroke=GRAY_LIGHT, stroke_width=0.8)
        svg.text(xl - 16, y + 4, f"e₇={e7}", font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

    svg.line(gx, gy, gx + 2*dx + 32, gy, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")
    svg.line(gx, gy, gx, gy - dy - 32, stroke=INK, stroke_width=1.2, marker_end="arrow-ink")

    for e3 in range(3):
        for e7 in range(2):
            v = (3 ** e3) * (7 ** e7)
            x, y = pt_37(e3, e7)
            if (e3, e7) == (1, 1):
                svg.circle(x, y, 10, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.5)
                svg.circle(x, y, 4.5, fill=PURPLE)
                svg.pill_label(x, y - 24, "g = 21 (3¹·7¹)", font=FONT_SERIF, size=12.5, weight="bold", fill=PURPLE, anchor="middle")
            elif e3 <= 1 and e7 <= 1:
                svg.circle(x, y, 4.5, fill=PURPLE)
                svg.text(x + 8, y - 8, f"{v}", font=FONT_SERIF, size=12, weight="bold", fill=INK, anchor="start")
            else:
                svg.circle(x, y, 4, fill=NAVY)
                svg.text(x + 8, y - 6, f"{v} (in Div(a))", font=FONT_SANS, size=11, fill=NAVY)

    svg.text(bl_x + 16, bl_y + 230, "Div(1071) ∩ Div(462) = {1, 3, 7, 21}  →  Gcd(1071, 462) = { 21 }",
             font=FONT_SERIF, size=12.5, weight="bold", fill=PURPLE)

    # Bottom Right Panel: Codillon Per-Instruction Live Inspector Mockup
    br_x, br_y = 468, 352
    br_w, br_h = 396, 245
    svg.rect(br_x, br_y, br_w, br_h, fill="#faf9ec", stroke=INK, stroke_width=1.4, rx=8)
    svg.rect(br_x, br_y, br_w, 32, fill="#eae8d5", stroke=INK, stroke_width=1.4, rx=8)
    svg.text(br_x + 14, br_y + 21, "Codillon Structured Wasm Editor — Refinement Type Widget", font=FONT_SANS, size=12, weight="bold", fill=INK)

    # Wasm instruction line
    svg.rect(br_x + 14, br_y + 44, br_w - 28, 52, fill=BG, stroke=GRAY_LIGHT, stroke_width=1, rx=4)
    svg.text(br_x + 24, br_y + 64, "(local.get $x)   ;; $x = 21  (after loop exit $y = 0)", font=FONT_SANS, size=12, weight="bold", fill=NAVY)
    svg.text(br_x + 24, br_y + 84, "Goal Type:  { g : i32 | Div(g) = Div(1071) ∩ Div(462) }", font=FONT_SERIF, size=12, weight="bold", fill=PURPLE)

    # Compact barcode inspector inside Codillon
    svg.text(br_x + 16, br_y + 116, "Prime-Exponent Barcode Proof (∀p. e_p(g) = min(e_p(a), e_p(b))):", font=FONT_SANS, size=11.5, weight="bold", fill=INK)

    # Table header
    tx = br_x + 16
    ty = br_y + 126
    svg.rect(tx, ty, br_w - 32, 92, fill=BG, stroke=PURPLE, stroke_width=1.2, rx=4)

    headers = [("Prime p", 38), ("e_p(1071)", 102), ("e_p(462)", 168), ("min = e_p(g)", 246), ("Status", 324)]
    for htext, hx in headers:
        svg.text(tx + hx, ty + 16, htext, font=FONT_SANS, size=11, weight="bold", fill=GRAY_DARK, anchor="middle")
    svg.line(tx + 6, ty + 22, tx + br_w - 38, ty + 22, stroke=GRAY_LIGHT, stroke_width=1)

    rows = [
        ("p = 2",  "0", "1", "0  (2⁰=1)", "✓ match"),
        ("p = 3",  "2", "1", "1  (3¹=3)", "✓ match"),
        ("p = 7",  "1", "1", "1  (7¹=7)", "✓ match"),
        ("p = 11, 17", "0, 1", "1, 0", "0  (p⁰=1)", "✓ match"),
    ]
    for r_i, (rp, ra, rb, rg, rstat) in enumerate(rows):
        ry = ty + 38 + r_i * 16
        svg.text(tx + 38,  ry, rp, font=FONT_SERIF, size=11, weight="bold", fill=INK, anchor="middle")
        svg.text(tx + 102, ry, ra, font=FONT_SANS, size=11, fill=NAVY, anchor="middle")
        svg.text(tx + 168, ry, rb, font=FONT_SANS, size=11, fill=NAVY, anchor="middle")
        svg.text(tx + 246, ry, rg, font=FONT_SANS, size=11, weight="bold", fill=PURPLE, anchor="middle")
        svg.text(tx + 324, ry, rstat, font=FONT_SANS, size=11, weight="bold", fill=PURPLE, anchor="middle")

    svg.text(br_x + 16, br_y + 234, "Product = 1 · 3 · 7 · 1 = 21  ⇒  Typecheck QED (evidence erased)",
             font=FONT_SANS, size=11, weight="bold", fill=PURPLE)

    svg.save("fig-5.svg")


if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    print("Generated fig-1.svg through fig-5.svg successfully.")
