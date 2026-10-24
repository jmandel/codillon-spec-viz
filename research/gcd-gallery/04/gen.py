#!/usr/bin/env python3
"""
Generator for Euclid's Rectangle Tiling visualizations of Gcd(a, b) as a refinement type.
Produces fig-1.svg through fig-5.svg.
"""

import math
import html

# Palette (strict compliance: NO green anywhere)
BG = "#fffff0"          # ivory background
INK = "#222222"         # primary ink
PURPLE = "#6A5ACD"      # type / region purple (SlateBlue)
PURPLE_FILL = "#d9d5f2" # muted purple fill
PURPLE_LIGHT = "#ece9fa"# lighter purple for subtle regions
RED = "#8b0000"         # dark red ONLY for violation / type error
RED_FILL = "#f7d6d6"    # light red fill for error overhang/violation
INDIGO = "#4b0082"      # indigo ONLY for "unknown"
NAVY = "#00008b"        # navy for concrete run or value
NAVY_FILL = "#dce2f7"   # light navy tint for concrete rectangles
GRAY_DARK = "#555555"
GRAY_MID = "#888888"
GRAY_LIGHT = "#cccccc"
GRAY_FAINT = "#e8e8dc"

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"


def divisors(n, cap=None):
    """Return sorted positive divisors of n. If n == 0, return up to cap."""
    if n == 0:
        if cap is None:
            raise ValueError("Div(0) is all of N; provide a cap")
        return list(range(1, cap + 1))
    return [d for d in range(1, n + 1) if n % d == 0]


def common_divisors(a, b):
    g = math.gcd(a, b)
    return divisors(g)


class SvgBuilder:
    def __init__(self, width=900, height=600):
        self.width = width
        self.height = height
        self.elements = []
        self.defs = []

    def add_def(self, s):
        self.defs.append(s)

    def add(self, s):
        self.elements.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", stroke_width=1,
             rx=0, dash=None, opacity=None):
        attrs = [f'x="{x:.2f}"', f'y="{y:.2f}"', f'width="{w:.2f}"', f'height="{h:.2f}"',
                 f'fill="{fill}"', f'stroke="{stroke}"']
        if stroke != "none":
            attrs.append(f'stroke-width="{stroke_width}"')
        if rx:
            attrs.append(f'rx="{rx}"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, stroke_width=1, dash=None,
             marker_end=None, marker_start=None, opacity=None):
        attrs = [f'x1="{x1:.2f}"', f'y1="{y1:.2f}"', f'x2="{x2:.2f}"', f'y2="{y2:.2f}"',
                 f'stroke="{stroke}"', f'stroke-width="{stroke_width}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker_end:
            attrs.append(f'marker-end="url(#{marker_end})"')
        if marker_start:
            attrs.append(f'marker-start="url(#{marker_start})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def circle(self, cx, cy, r, fill="none", stroke="none", stroke_width=1):
        attrs = [f'cx="{cx:.2f}"', f'cy="{cy:.2f}"', f'r="{r:.2f}"',
                 f'fill="{fill}"', f'stroke="{stroke}"']
        if stroke != "none":
            attrs.append(f'stroke-width="{stroke_width}"')
        self.add(f'<circle {" ".join(attrs)}/>')

    def path(self, d, fill="none", stroke=INK, stroke_width=1, dash=None, marker_end=None):
        attrs = [f'd="{d}"', f'fill="{fill}"', f'stroke="{stroke}"', f'stroke-width="{stroke_width}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker_end:
            attrs.append(f'marker-end="url(#{marker_end})"')
        self.add(f'<path {" ".join(attrs)}/>')

    def text(self, x, y, content, font=FONT_SERIF, size=14, fill=INK,
             anchor="start", weight="normal", style="normal", escape=True):
        txt = html.escape(str(content)) if escape else str(content)
        attrs = [f'x="{x:.2f}"', f'y="{y:.2f}"', f'font-family="{font}"',
                 f'font-size="{size}"', f'fill="{fill}"', f'text-anchor="{anchor}"']
        if weight != "normal":
            attrs.append(f'font-weight="{weight}"')
        if style != "normal":
            attrs.append(f'font-style="{style}"')
        self.add(f'<text {" ".join(attrs)}>{txt}</text>')

    def add_standard_defs(self):
        self.add_def(f'''
        <pattern id="errHatch" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
          <rect width="8" height="8" fill="{RED_FILL}"/>
          <line x1="0" y1="0" x2="0" y2="8" stroke="{RED}" stroke-width="2"/>
        </pattern>
        <pattern id="purpleHatch" width="8" height="8" patternTransform="rotate(-45 0 0)" patternUnits="userSpaceOnUse">
          <rect width="8" height="8" fill="{PURPLE_LIGHT}"/>
          <line x1="0" y1="0" x2="0" y2="8" stroke="{PURPLE}" stroke-width="1.2" opacity="0.45"/>
        </pattern>
        <marker id="arrowInk" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{INK}"/>
        </marker>
        <marker id="arrowPurple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{PURPLE}"/>
        </marker>
        <marker id="arrowNavy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{NAVY}"/>
        </marker>
        <marker id="arrowRed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{RED}"/>
        </marker>
        ''')

    def add_header(self, title_claim, subtitle_math):
        # Validate <= 12 words in title_claim
        words = title_claim.split()
        assert len(words) <= 12, f"Title exceeds 12 words ({len(words)}): {title_claim}"
        self.text(30, 34, title_claim, font=FONT_SERIF, size=20, fill=INK, weight="bold")
        self.text(30, 56, subtitle_math, font=FONT_SERIF, size=13.5, fill=GRAY_DARK, escape=False)
        self.line(30, 66, self.width - 30, 66, stroke=GRAY_LIGHT, stroke_width=1)

    def render(self):
        out = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">',
            f'<defs>{"".join(self.defs)}</defs>',
            f'<rect x="0" y="0" width="{self.width}" height="{self.height}" fill="{BG}"/>',
        ]
        out.extend(self.elements)
        out.append('</svg>')
        return "\n".join(out)


def draw_tiled_rect(svg, x0, y0, a, b, d, scale, show_dims=True,
                    rect_stroke=NAVY, tile_stroke=PURPLE,
                    valid_fill=PURPLE_FILL, show_overhang=True):
    """
    Draws an a x b rectangle at (x0, y0) with pixel scale `scale` per unit,
    overlaid with a d x d square tile grid.
    If d divides both a and b: clean purple tiling.
    If d fails to divide a or b: tiles up to ceil(a/d)*d or ceil(b/d)*d with dark-red overhang.
    """
    rw = a * scale
    rh = b * scale

    fits_a = (a % d == 0)
    fits_b = (b % d == 0)
    fits_both = fits_a and fits_b

    svg.rect(x0, y0, rw, rh, fill=valid_fill if fits_both else "#f2f2ea", stroke="none")

    nx_full = a // d
    ny_full = b // d
    nx_ceil = math.ceil(a / d)
    ny_ceil = math.ceil(b / d)

    step = d * scale

    for ix in range(nx_full):
        for iy in range(ny_full):
            tx = x0 + ix * step
            ty = y0 + iy * step
            svg.rect(tx, ty, step, step,
                     fill=valid_fill if fits_both else "#e5e3f3",
                     stroke=tile_stroke if fits_both else GRAY_MID,
                     stroke_width=1.0)

    if not fits_both and show_overhang:
        for ix in range(nx_ceil):
            for iy in range(ny_ceil):
                if ix >= nx_full or iy >= ny_full:
                    tx = x0 + ix * step
                    ty = y0 + iy * step
                    svg.rect(tx, ty, step, step, fill="url(#errHatch)", stroke=RED, stroke_width=1.3, dash="3,2")

        svg.rect(x0, y0, rw, rh, fill="none", stroke=rect_stroke, stroke_width=2.2)
    else:
        svg.rect(x0, y0, rw, rh, fill="none", stroke=rect_stroke, stroke_width=2.2)

    if show_dims:
        svg.text(x0 + rw / 2, y0 - 7, f"a = {a}", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
        svg.text(x0 - 7, y0 + rh / 2 + 4, f"b = {b}", font=FONT_SERIF, size=12, fill=NAVY, anchor="end", weight="bold")


# ============================================================================
# FIGURE 1: What a Common Divisor Is, and What the Refinement Type Selects
# ============================================================================
def make_fig1():
    a, b = 12, 8
    g = math.gcd(a, b)

    svg = SvgBuilder(900, 620)
    svg.add_standard_defs()

    svg.add_header(
        "Common Divisors Tile the a×b Rectangle; gcd Is the Largest",
        f'Refinement type: <tspan fill="{PURPLE}" font-weight="bold">Gcd(12, 8)</tspan> = '
        f'{{ g ∈ ℕ | <tspan fill="{PURPLE}">Div(g) = Div(12) ∩ Div(8)</tspan> }} = {{ {g} }}'
    )

    svg.text(30, 92, "1. Every candidate square side d ∈ {1 … 6} tested against the 12 × 8 rectangle:",
             font=FONT_SERIF, size=14, fill=INK, weight="bold")
    svg.text(535, 92, "d ∣ 12 ∧ d ∣ 8  ⇔  d×d squares tile 12×8 with zero overhang",
             font=FONT_SANS, size=12.5, fill=GRAY_DARK)

    candidates = [1, 2, 3, 4, 5, 6]
    scale = 7.0  # 12 * 7 = 84px, 8 * 7 = 56px; for d=5, 15 * 7 = 105px (fits comfortably inside 136px card!)

    card_w = 136
    card_h = 185
    start_x = 30
    gap_x = 140
    top_y = 106

    for idx, d in enumerate(candidates):
        cx = start_x + idx * gap_x
        cy = top_y
        fits_a = (a % d == 0)
        fits_b = (b % d == 0)
        fits = fits_a and fits_b
        is_gcd = (d == g)

        border_col = PURPLE if fits else RED
        border_w = 2.5 if is_gcd else (1.6 if fits else 1.2)
        card_bg = PURPLE_LIGHT if is_gcd else ("#f7f5fc" if fits else "#fcf8f8")
        svg.rect(cx, cy, card_w, card_h, fill=card_bg, stroke=border_col, stroke_width=border_w, rx=5)

        badge_fill = PURPLE if fits else RED
        svg.rect(cx, cy, card_w, 24, fill=badge_fill, stroke="none", rx=4)
        svg.rect(cx, cy + 12, card_w, 12, fill=badge_fill, stroke="none")
        status_str = f"d = {d}  (TILES)" if fits else f"d = {d}  (MISFITS)"
        svg.text(cx + card_w / 2, cy + 16, status_str, font=FONT_SANS, size=12, fill=BG, anchor="middle", weight="bold")

        rx0 = cx + 18
        ry0 = cy + 44
        draw_tiled_rect(svg, rx0, ry0, a, b, d, scale, show_dims=False)

        svg.text(rx0 + (a * scale) / 2, ry0 - 5, "12", font=FONT_SANS, size=11, fill=NAVY, anchor="middle")
        svg.text(rx0 - 4, ry0 + (b * scale) / 2 + 4, "8", font=FONT_SANS, size=11, fill=NAVY, anchor="end")

        rem_a = a % d
        rem_b = b % d
        if fits:
            q_a = a // d
            q_b = b // d
            svg.text(cx + card_w / 2, cy + 144, f"12 = {q_a}×{d},  8 = {q_b}×{d}",
                     font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle", weight="bold")
            svg.text(cx + card_w / 2, cy + 162, f"d ∈ Div(12) ∩ Div(8)",
                     font=FONT_SERIF, size=11.5, fill=PURPLE, anchor="middle")
            if is_gcd:
                svg.text(cx + card_w / 2, cy + 178, "★ coarsest grid (gcd)",
                         font=FONT_SANS, size=11.5, fill=NAVY, anchor="middle", weight="bold")
        else:
            probs = []
            if rem_a != 0:
                probs.append(f"12%{d}={rem_a}")
            if rem_b != 0:
                probs.append(f"8%{d}={rem_b}")
            svg.text(cx + card_w / 2, cy + 144, "Misfits: " + ", ".join(probs),
                     font=FONT_SANS, size=11.5, fill=RED, anchor="middle", weight="bold")
            svg.text(cx + card_w / 2, cy + 162, f"protrudes past 12×8",
                     font=FONT_SANS, size=11, fill=RED, anchor="middle")
            svg.text(cx + card_w / 2, cy + 178, f"d ∉ Div(12) ∩ Div(8)",
                     font=FONT_SERIF, size=11.5, fill=RED, anchor="middle")

    # Bottom Section
    svg.line(30, 308, 870, 308, stroke=GRAY_LIGHT, stroke_width=1)
    svg.text(30, 332, "2. Why the type { g ∈ ℕ | Div(g) = Div(12) ∩ Div(8) } has a single inhabitant g = 4:",
             font=FONT_SERIF, size=14, fill=INK, weight="bold")

    # Left panel: The Evidence Set (Valid Tile Sizes)
    ev_x, ev_y, ev_w, ev_h = 30, 348, 395, 245
    svg.rect(ev_x, ev_y, ev_w, ev_h, fill=PURPLE_LIGHT, stroke=PURPLE, stroke_width=1.8, rx=6)
    svg.text(ev_x + 14, ev_y + 24, "Common Tile Set  Div(12) ∩ Div(8) = { 1, 2, 4 }",
             font=FONT_SERIF, size=14, fill=PURPLE, weight="bold")
    svg.text(ev_x + 14, ev_y + 43, "Every valid d-tile grid nests inside the 4×4 master tile:",
             font=FONT_SANS, size=12, fill=INK)

    big_s = 17.0  # 12*17 = 204, 8*17 = 136
    bx = ev_x + 48
    by = ev_y + 68
    bw = a * big_s
    bh = b * big_s
    svg.rect(bx, by, bw, bh, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2.5)

    for i in range(1, a):
        svg.line(bx + i * big_s, by, bx + i * big_s, by + bh, stroke=PURPLE, stroke_width=0.5, opacity=0.35)
    for j in range(1, b):
        svg.line(bx, by + j * big_s, bx + bw, by + j * big_s, stroke=PURPLE, stroke_width=0.5, opacity=0.35)

    for i in range(2, a, 2):
        svg.line(bx + i * big_s, by, bx + i * big_s, by + bh, stroke=PURPLE, stroke_width=1.1, dash="3,2", opacity=0.75)
    for j in range(2, b, 2):
        svg.line(bx, by + j * big_s, bx + bw, by + j * big_s, stroke=PURPLE, stroke_width=1.1, dash="3,2", opacity=0.75)

    for i in range(4, a, 4):
        svg.line(bx + i * big_s, by, bx + i * big_s, by + bh, stroke=NAVY, stroke_width=2.4)
    for j in range(4, b, 4):
        svg.line(bx, by + j * big_s, bx + bw, by + j * big_s, stroke=NAVY, stroke_width=2.4)

    svg.text(bx + bw / 2, by - 7, "a = 12", font=FONT_SERIF, size=12.5, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx - 8, by + bh / 2 + 4, "b = 8", font=FONT_SERIF, size=12.5, fill=NAVY, anchor="end", weight="bold")

    lx = bx + bw + 24
    svg.rect(lx, by + 4, 4 * big_s, 4 * big_s, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2.2)
    for i in range(1, 4):
        svg.line(lx + i * big_s, by + 4, lx + i * big_s, by + 4 + 4 * big_s, stroke=PURPLE, stroke_width=0.6, opacity=0.5)
        svg.line(lx, by + 4 + i * big_s, lx + 4 * big_s, by + 4 + i * big_s, stroke=PURPLE, stroke_width=0.6, opacity=0.5)
    svg.line(lx + 2 * big_s, by + 4, lx + 2 * big_s, by + 4 + 4 * big_s, stroke=PURPLE, stroke_width=1.4, dash="3,2")
    svg.line(lx, by + 4 + 2 * big_s, lx + 4 * big_s, by + 4 + 2 * big_s, stroke=PURPLE, stroke_width=1.4, dash="3,2")

    svg.text(lx + 2 * big_s, by + 4 + 4 * big_s + 18, "Master tile: 4×4", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
    svg.text(lx + 2 * big_s, by + 4 + 4 * big_s + 34, "contains 2×2 & 1×1", font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle")
    svg.text(lx + 2 * big_s, by + 4 + 4 * big_s + 50, "Div(4) = {1, 2, 4}", font=FONT_SERIF, size=12, fill=PURPLE, anchor="middle", weight="bold")

    # Right panel: Set view of N showing the refinement predicate filtering N down to {4}
    rt_x, rt_y, rt_w, rt_h = 445, 348, 425, 245
    svg.rect(rt_x, rt_y, rt_w, rt_h, fill="#f9f8f2", stroke=INK, stroke_width=1.5, rx=6)
    svg.text(rt_x + 14, rt_y + 24, "Base Type ℕ Refined by Predicate  Div(g) = {1, 2, 4}",
             font=FONT_SERIF, size=14, fill=INK, weight="bold")

    rows = [
        (1, divisors(1), "missing tiles 2, 4", False),
        (2, divisors(2), "missing tile 4", False),
        (3, divisors(3), "tile 3 misfits; lacks 2, 4", False),
        (4, divisors(4), "exact match! g = 4 ∈ Gcd(12, 8)", True),
        (6, divisors(6), "tile 6 misfits; lacks 4", False),
        (8, divisors(8), "tile 8 misfits 12", False),
        (12, divisors(12), "tiles 3, 6, 12 misfit 8", False),
    ]

    ry_start = rt_y + 46
    row_h = 27
    for idx, (cand_g, divs_g, reason, is_member) in enumerate(rows):
        cy = ry_start + idx * row_h
        if is_member:
            svg.rect(rt_x + 10, cy - 15, rt_w - 20, 24, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.0, rx=4)
        else:
            svg.rect(rt_x + 10, cy - 15, rt_w - 20, 22, fill=BG, stroke=GRAY_LIGHT, stroke_width=0.8, rx=3)

        col_g = NAVY if is_member else GRAY_DARK
        svg.text(rt_x + 22, cy + 1, f"g = {cand_g}", font=FONT_SERIF, size=12.5, fill=col_g,
                 weight="bold" if is_member else "normal")

        divs_str = "{" + ", ".join(str(x) for x in divs_g) + "}"
        col_div = PURPLE if is_member else RED
        eq_sym = "=" if is_member else "≠"
        svg.text(rt_x + 82, cy + 1, f"Div({cand_g}) = {divs_str} {eq_sym} {{1, 2, 4}}",
                 font=FONT_SERIF, size=12, fill=col_div, weight="bold" if is_member else "normal")

        svg.text(rt_x + rt_w - 18, cy + 1, reason, font=FONT_SANS, size=11.5,
                 fill=NAVY if is_member else RED, anchor="end", weight="bold" if is_member else "normal")

    with open("fig-1.svg", "w") as f:
        f.write(svg.render())


# ============================================================================
# FIGURE 2: Euclid's Cut Sequence Preserves the Tile Set (Loop Invariant)
# ============================================================================
def make_fig2():
    svg = SvgBuilder(900, 650)
    svg.add_standard_defs()

    svg.add_header(
        "Cutting b×b Squares Never Changes Which d-Grids Tile the Remainder",
        f'Loop invariant: <tspan fill="{PURPLE}" font-weight="bold">Div(x) ∩ Div(y) = Div(y) ∩ Div(x mod y)</tspan> '
        f'⇒ refinement type <tspan fill="{PURPLE}" font-weight="bold">Gcd(x, y)</tspan> is identical at every step'
    )

    # Top: Algebraic & Geometric lemma visual
    svg.rect(30, 78, 840, 128, fill=PURPLE_LIGHT, stroke=PURPLE, stroke_width=1.5, rx=6)
    svg.text(46, 100, "Geometric Preservation Lemma:  x = q·y + r   ⇔   an x×y rectangle = (q squares of side y)  +  (remainder r×y)",
             font=FONT_SERIF, size=13.5, fill=INK, weight="bold")

    sc = 8.5
    lx0, ly0 = 55, 118
    svg.rect(lx0, ly0, 8 * sc, 8 * sc, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2)
    svg.rect(lx0 + 8 * sc, ly0, 4 * sc, 8 * sc, fill=NAVY_FILL, stroke=NAVY, stroke_width=2)
    for i in range(1, 3):
        svg.line(lx0 + i * 4 * sc, ly0, lx0 + i * 4 * sc, ly0 + 8 * sc, stroke=PURPLE, stroke_width=1.4, dash="3,2")
    svg.line(lx0, ly0 + 4 * sc, lx0 + 12 * sc, ly0 + 4 * sc, stroke=PURPLE, stroke_width=1.4, dash="3,2")
    svg.line(lx0 + 8 * sc, ly0 - 6, lx0 + 8 * sc, ly0 + 8 * sc + 6, stroke=RED, stroke_width=2.2, dash="4,2")
    svg.text(lx0 + 4 * sc, ly0 + 4 * sc + 4, "y × y", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
    svg.text(lx0 + 10 * sc, ly0 + 4 * sc + 4, "r × y", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
    svg.text(lx0 + 8 * sc, ly0 - 9, "cut", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")

    tx = 200
    svg.text(tx, 128, "• Forward (d ∣ x ∧ d ∣ y ⇒ d ∣ r):  Since d tiles y, d automatically tiles every y×y square.",
             font=FONT_SERIF, size=12.5, fill=INK)
    svg.text(tx + 14, 147, "Removing q tiled y×y squares from a tiled x×y rectangle leaves r = x − q·y tiled by the exact same d-grid.",
             font=FONT_SANS, size=12, fill=GRAY_DARK)
    svg.text(tx, 170, "• Backward (d ∣ y ∧ d ∣ r ⇒ d ∣ x):  Gluing q tiled y×y squares onto a tiled r×y rectangle tiles x = q·y + r.",
             font=FONT_SERIF, size=12.5, fill=INK)
    svg.text(tx + 14, 189, "Therefore Div(x) ∩ Div(y) = Div(y) ∩ Div(r) — no valid tile size is ever gained or lost!",
             font=FONT_SERIF, size=12.5, fill=PURPLE, weight="bold")

    # Middle section: Trace A: (12, 8) -> (8, 4) -> (4, 0)
    svg.text(30, 232, "Trace A:  (12, 8)  →  (8, 4)  →  (4, 0)     [ Common tile sizes fixed at {1, 2, 4} throughout ]",
             font=FONT_SERIF, size=14, fill=NAVY, weight="bold")

    steps_12_8 = [
        {
            "step": "Step 0 (Input)",
            "x": 12, "y": 8,
            "eq": "12 = 1·8 + 4",
            "type_str": "Gcd(12, 8) = {4}",
            "ev_str": "Div(12) ∩ Div(8) = {1, 2, 4}"
        },
        {
            "step": "Step 1 (After 1st Cut)",
            "x": 8, "y": 4,
            "eq": "8 = 2·4 + 0",
            "type_str": "Gcd(8, 4) = {4}",
            "ev_str": "Div(8) ∩ Div(4) = {1, 2, 4}"
        },
        {
            "step": "Step 2 (Halting State y = 0)",
            "x": 4, "y": 0,
            "eq": "Div(4) ∩ Div(0) = Div(4) ∩ ℕ = Div(4)",
            "type_str": "Gcd(4, 0) = {4}",
            "ev_str": "Div(4) = {1, 2, 4}"
        }
    ]

    cw, ch = 262, 178
    cy0 = 244
    for i, st in enumerate(steps_12_8):
        cx = 30 + i * 289
        svg.rect(cx, cy0, cw, ch, fill="#faf9f0", stroke=PURPLE, stroke_width=1.8, rx=6)
        svg.rect(cx, cy0, cw, 24, fill=PURPLE, stroke="none", rx=5)
        svg.rect(cx, cy0 + 12, cw, 12, fill=PURPLE, stroke="none")
        svg.text(cx + 10, cy0 + 16, st["step"], font=FONT_SANS, size=12, fill=BG, weight="bold")
        svg.text(cx + cw - 10, cy0 + 16, f"(x={st['x']}, y={st['y']})", font=FONT_SERIF, size=12, fill=BG, anchor="end", weight="bold")

        s1 = 9.0
        rx = cx + 28
        ry = cy0 + 42
        if st["x"] == 12 and st["y"] == 8:
            svg.rect(rx, ry, 8 * s1, 8 * s1, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2)
            svg.rect(rx + 8 * s1, ry, 4 * s1, 8 * s1, fill=NAVY_FILL, stroke=NAVY, stroke_width=2)
            for gx in range(4, 12, 4):
                svg.line(rx + gx * s1, ry, rx + gx * s1, ry + 8 * s1, stroke=PURPLE, stroke_width=1.2, dash="2,2")
            svg.line(rx, ry + 4 * s1, rx + 12 * s1, ry + 4 * s1, stroke=PURPLE, stroke_width=1.2, dash="2,2")
            svg.line(rx + 8 * s1, ry - 5, rx + 8 * s1, ry + 8 * s1 + 5, stroke=RED, stroke_width=2, dash="4,2")
            svg.text(rx + 4 * s1, ry + 4 * s1 + 4, "8×8", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
            svg.text(rx + 10 * s1, ry + 4 * s1 + 4, "4×8", font=FONT_SERIF, size=11.5, fill=NAVY, anchor="middle")
            tx = cx + 165
            svg.text(tx, ry + 12, "Tiles fitting:", font=FONT_SANS, size=11, fill=PURPLE, weight="bold")
            for td, dy_off in [(1, 20), (2, 34), (4, 54)]:
                svg.rect(tx, ry + dy_off, td * 4.5, td * 4.5, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=1.2)
                svg.text(tx + td * 4.5 + 6, ry + dy_off + td * 2.2 + 4, f"d={td}", font=FONT_SANS, size=11, fill=PURPLE)

        elif st["x"] == 8 and st["y"] == 4:
            svg.rect(rx, ry + 14, 8 * s1, 4 * s1, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2)
            svg.line(rx + 4 * s1, ry + 9, rx + 4 * s1, ry + 14 + 4 * s1 + 5, stroke=RED, stroke_width=2, dash="4,2")
            svg.text(rx + 2 * s1, ry + 14 + 2 * s1 + 4, "4×4", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
            svg.text(rx + 6 * s1, ry + 14 + 2 * s1 + 4, "4×4", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
            tx = cx + 165
            svg.text(tx, ry + 12, "Tiles fitting:", font=FONT_SANS, size=11, fill=PURPLE, weight="bold")
            for td, dy_off in [(1, 20), (2, 34), (4, 54)]:
                svg.rect(tx, ry + dy_off, td * 4.5, td * 4.5, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=1.2)
                svg.text(tx + td * 4.5 + 6, ry + dy_off + td * 2.2 + 4, f"d={td}", font=FONT_SANS, size=11, fill=PURPLE)

        else:
            svg.rect(rx + 10, ry + 10, 4 * s1, 4 * s1, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2.5)
            svg.text(rx + 10 + 2 * s1, ry + 10 + 2 * s1 + 4, "g = 4", font=FONT_SERIF, size=12.5, fill=NAVY, anchor="middle", weight="bold")
            svg.text(rx + 10 + 2 * s1, ry + 10 + 4 * s1 + 15, "0 remainder!", font=FONT_SANS, size=11, fill=NAVY, anchor="middle", weight="bold")
            tx = cx + 145
            svg.text(tx, ry + 12, "Div(0) = ℕ", font=FONT_SERIF, size=11.5, fill=PURPLE, weight="bold")
            svg.text(tx, ry + 28, "Div(4) ∩ ℕ", font=FONT_SERIF, size=11.5, fill=PURPLE)
            svg.text(tx, ry + 44, "= Div(4)", font=FONT_SERIF, size=11.5, fill=PURPLE, weight="bold")
            svg.text(tx, ry + 60, "= {1, 2, 4}", font=FONT_SERIF, size=11.5, fill=PURPLE, weight="bold")

        svg.text(cx + 12, cy0 + 132, st["eq"], font=FONT_SERIF, size=12, fill=INK, weight="bold")
        svg.text(cx + 12, cy0 + 150, st["ev_str"], font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")
        svg.text(cx + 12, cy0 + 168, f"Type: {st['type_str']}", font=FONT_SERIF, size=12, fill=NAVY, weight="bold")

        if i < 2:
            ax1 = cx + cw + 3
            ax2 = cx + 289 - 5
            ay = cy0 + ch / 2
            svg.line(ax1, ay, ax2, ay, stroke=PURPLE, stroke_width=2.2, marker_end="arrowPurple")
            svg.text((ax1 + ax2) / 2, ay - 8, "=", font=FONT_SERIF, size=16, fill=PURPLE, anchor="middle", weight="bold")

    # Bottom section: Trace B: (30, 18) -> (18, 12) -> (12, 6) -> (6, 0)
    svg.line(30, 438, 870, 438, stroke=GRAY_LIGHT, stroke_width=1)
    svg.text(30, 460, "Trace B (3 Cuts):  (30, 18)  →  (18, 12)  →  (12, 6)  →  (6, 0)     [ Common tile set {1, 2, 3, 6} preserved at every cut ]",
             font=FONT_SERIF, size=14, fill=NAVY, weight="bold")

    s2 = 5.2  # 30 * 5.2 = 156, 18 * 5.2 = 93.6
    bx0, by0 = 56, 488
    svg.rect(bx0, by0, 18 * s2, 18 * s2, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2)
    svg.rect(bx0 + 18 * s2, by0, 12 * s2, 12 * s2, fill="#c5bfe8", stroke=NAVY, stroke_width=2)
    svg.rect(bx0 + 18 * s2, by0 + 12 * s2, 6 * s2, 6 * s2, fill=NAVY_FILL, stroke=NAVY, stroke_width=2)
    svg.rect(bx0 + 24 * s2, by0 + 12 * s2, 6 * s2, 6 * s2, fill=NAVY_FILL, stroke=NAVY, stroke_width=2)

    for i in range(1, 5):
        svg.line(bx0 + i * 6 * s2, by0, bx0 + i * 6 * s2, by0 + 18 * s2, stroke=PURPLE, stroke_width=1.0, dash="2,2")
    for j in range(1, 3):
        svg.line(bx0, by0 + j * 6 * s2, bx0 + 30 * s2, by0 + j * 6 * s2, stroke=PURPLE, stroke_width=1.0, dash="2,2")

    svg.line(bx0 + 18 * s2, by0 - 4, bx0 + 18 * s2, by0 + 18 * s2 + 4, stroke=RED, stroke_width=2.2, dash="4,2")
    svg.line(bx0 + 18 * s2 - 4, by0 + 12 * s2, bx0 + 30 * s2 + 4, by0 + 12 * s2, stroke=RED, stroke_width=2.2, dash="4,2")
    svg.line(bx0 + 24 * s2, by0 + 12 * s2 - 4, bx0 + 24 * s2, by0 + 18 * s2 + 4, stroke=RED, stroke_width=2.2, dash="4,2")

    svg.text(bx0 + 9 * s2, by0 + 9 * s2 + 4, "Cut 1: 18×18", font=FONT_SERIF, size=11.5, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx0 + 24 * s2, by0 + 6 * s2 + 4, "Cut 2: 12×12", font=FONT_SERIF, size=11, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx0 + 21 * s2, by0 + 15 * s2 + 4, "6×6", font=FONT_SERIF, size=11, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx0 + 27 * s2, by0 + 15 * s2 + 4, "6×6", font=FONT_SERIF, size=11, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx0 + 15 * s2, by0 - 8, "a = 30", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx0 - 6, by0 + 9 * s2 + 4, "b = 18", font=FONT_SERIF, size=12, fill=NAVY, anchor="end", weight="bold")
    svg.text(bx0 + 15 * s2, by0 + 18 * s2 + 16, "All cuts align with 6×6 grid",
             font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(bx0 + 15 * s2, by0 + 18 * s2 + 31, "(and 3×3, 2×2, 1×1 subgrids)",
             font=FONT_SANS, size=11, fill=PURPLE, anchor="middle")

    # Right of Trace B: State table
    tx0 = 232
    ty0 = 475
    tw = 638
    th = 152
    svg.rect(tx0, ty0, tw, th, fill="#faf9f0", stroke=PURPLE, stroke_width=1.5, rx=6)

    headers = ["State (x, y)", "Euclidean Cut", "Div(x)", "Div(y)", "Div(x) ∩ Div(y)", "Refinement Type"]
    col_x = [tx0 + 10, tx0 + 92, tx0 + 195, tx0 + 322, tx0 + 422, tx0 + 528]
    for h_txt, cx_pos in zip(headers, col_x):
        svg.text(cx_pos, ty0 + 20, h_txt, font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")
    svg.line(tx0 + 8, ty0 + 26, tx0 + tw - 8, ty0 + 26, stroke=PURPLE, stroke_width=1)

    trace_b_rows = [
        ("(30, 18)", "30 = 1·18 + 12", "{1,2,3,5,6,10,15,30}", "{1,2,3,6,9,18}", "{1, 2, 3, 6}", "Gcd(30,18) = {6}"),
        ("(18, 12)", "18 = 1·12 + 6",  "{1,2,3,6,9,18}",       "{1,2,3,4,6,12}", "{1, 2, 3, 6}", "Gcd(18,12) = {6}"),
        ("(12, 6)",  "12 = 2·6 + 0",   "{1,2,3,4,6,12}",       "{1,2,3,6}",      "{1, 2, 3, 6}", "Gcd(12,6) = {6}"),
        ("(6, 0)",   "Halt: return 6", "{1,2,3,6}",            "ℕ (all d ≥ 1)",  "{1, 2, 3, 6}", "Gcd(6,0) = {6}"),
    ]
    for r_idx, r_data in enumerate(trace_b_rows):
        ry = ty0 + 48 + r_idx * 28
        if r_idx == 3:
            svg.rect(tx0 + 6, ry - 15, tw - 12, 22, fill=PURPLE_FILL, stroke="none", rx=3)
        for c_idx, val in enumerate(r_data):
            col = PURPLE if c_idx == 4 else (NAVY if c_idx in (0, 5) else INK)
            wt = "bold" if c_idx in (0, 4, 5) else "normal"
            svg.text(col_x[c_idx], ry, val, font=FONT_SANS if c_idx in (2, 3) else FONT_SERIF, size=11.5, fill=col, weight=wt)

    with open("fig-2.svg", "w") as f:
        f.write(svg.render())


# ============================================================================
# FIGURE 3: Second Pair & Boundary Cases — Coprime (13, 8) -> 1 and (21, 0) -> 21
# ============================================================================
def make_fig3():
    svg = SvgBuilder(900, 640)
    svg.add_standard_defs()

    svg.add_header(
        "Extreme Cases: Fibonacci Spiral Forces d = 1; Zero Width Preserves Div(a)",
        f'Comparing <tspan fill="{NAVY}" font-weight="bold">Gcd(13, 8) = {{1}}</tspan> (coprime: only 1×1 tiles fit) '
        f'and <tspan fill="{NAVY}" font-weight="bold">Gcd(21, 0) = {{21}}</tspan> (degenerate 0-width rectangle)'
    )

    # LEFT HALF: Coprime Fibonacci Pair (13, 8) -> gcd = 1
    lx, ly, lw, lh = 30, 80, 425, 535
    svg.rect(lx, ly, lw, lh, fill="#faf9f0", stroke=NAVY, stroke_width=1.6, rx=6)
    svg.text(lx + 14, ly + 24, "Case 1: Coprime Fibonacci Rectangle  (a = 13, b = 8)",
             font=FONT_SERIF, size=14.5, fill=NAVY, weight="bold")
    svg.text(lx + 14, ly + 43, "Worst-case 5 cuts: 13×8 → 8×5 → 5×3 → 3×2 → 2×1 → 1×0",
             font=FONT_SANS, size=12, fill=GRAY_DARK)

    sc = 16.5
    rx0 = lx + 42
    ry0 = ly + 66
    rw = 13 * sc
    rh = 8 * sc

    svg.rect(rx0, ry0, rw, rh, fill=PURPLE_LIGHT, stroke=NAVY, stroke_width=2.2)
    for ix in range(1, 13):
        svg.line(rx0 + ix * sc, ry0, rx0 + ix * sc, ry0 + rh, stroke=PURPLE, stroke_width=0.5, opacity=0.4)
    for iy in range(1, 8):
        svg.line(rx0, ry0 + iy * sc, rx0 + rw, ry0 + iy * sc, stroke=PURPLE, stroke_width=0.5, opacity=0.4)

    # Dissection boxes
    svg.rect(rx0, ry0, 8 * sc, 8 * sc, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2)
    svg.text(rx0 + 4 * sc, ry0 + 4 * sc + 5, "8 × 8", font=FONT_SERIF, size=14, fill=NAVY, anchor="middle", weight="bold")

    svg.rect(rx0 + 8 * sc, ry0, 5 * sc, 5 * sc, fill="#c9c3ec", stroke=NAVY, stroke_width=2)
    svg.text(rx0 + 10.5 * sc, ry0 + 2.5 * sc + 5, "5 × 5", font=FONT_SERIF, size=13, fill=NAVY, anchor="middle", weight="bold")

    svg.rect(rx0 + 10 * sc, ry0 + 5 * sc, 3 * sc, 3 * sc, fill="#b8b0e3", stroke=NAVY, stroke_width=2)
    svg.text(rx0 + 11.5 * sc, ry0 + 6.5 * sc + 4, "3×3", font=FONT_SERIF, size=11.5, fill=NAVY, anchor="middle", weight="bold")

    svg.rect(rx0 + 8 * sc, ry0 + 5 * sc, 2 * sc, 2 * sc, fill="#a69cd9", stroke=NAVY, stroke_width=2)
    svg.text(rx0 + 9 * sc, ry0 + 6 * sc + 4, "2×2", font=FONT_SERIF, size=11, fill=NAVY, anchor="middle", weight="bold")

    svg.rect(rx0 + 8 * sc, ry0 + 7 * sc, 1 * sc, 1 * sc, fill=NAVY, stroke=BG, stroke_width=1.2)
    svg.rect(rx0 + 9 * sc, ry0 + 7 * sc, 1 * sc, 1 * sc, fill=NAVY, stroke=BG, stroke_width=1.2)

    svg.text(rx0 + rw / 2, ry0 - 7, "a = 13 (prime)", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
    svg.text(rx0 - 6, ry0 + rh / 2 + 4, "b = 8", font=FONT_SERIF, size=12, fill=NAVY, anchor="end", weight="bold")

    svg.line(rx0 + 9 * sc, ry0 + 8 * sc + 2, rx0 + 9 * sc, ry0 + 8 * sc + 20, stroke=NAVY, stroke_width=1.5)
    svg.text(rx0 + 9 * sc, ry0 + 8 * sc + 33, "Final cut: two 1×1 squares (g = 1)",
             font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")

    mx = rx0 + rw + 18
    my = ry0 + 6
    svg.text(mx, my, "Why d = 2 fails:", font=FONT_SANS, size=11.5, fill=RED, weight="bold")
    svg.text(mx, my + 16, "2 tiles 8 (8 = 4×2),", font=FONT_SANS, size=11, fill=INK)
    svg.text(mx, my + 30, "but 13 = 6×2 + 1:", font=FONT_SANS, size=11, fill=RED, weight="bold")
    bar_s = 8.2
    svg.rect(mx, my + 42, 13 * bar_s, 14, fill=NAVY_FILL, stroke=NAVY, stroke_width=1.5)
    svg.text(mx + 6.5 * bar_s, my + 53, "length 13", font=FONT_SANS, size=11, fill=NAVY, anchor="middle")
    for k in range(7):
        col_f = "url(#errHatch)" if k == 6 else PURPLE_FILL
        col_s = RED if k == 6 else PURPLE
        svg.rect(mx + k * 2 * bar_s, my + 60, 2 * bar_s, 14, fill=col_f, stroke=col_s, stroke_width=1.2)
    svg.text(mx + 14 * bar_s, my + 87, "overhang!", font=FONT_SANS, size=11, fill=RED, anchor="end", weight="bold")

    sy = ly + 252
    svg.line(lx + 14, sy, lx + lw - 14, sy, stroke=GRAY_LIGHT, stroke_width=1)
    svg.text(lx + 14, sy + 22, "Step-by-Step Invariant across all 5 Fibonacci Cuts:",
             font=FONT_SERIF, size=13, fill=INK, weight="bold")

    fib_steps = [
        ("(13, 8)", "13 = 1·8 + 5",  "Div(13)={1,13}", "Div(8)={1,2,4,8}", "{1}"),
        ("(8, 5)",  "8 = 1·5 + 3",   "Div(8)={1,2,4,8}", "Div(5)={1,5}",   "{1}"),
        ("(5, 3)",  "5 = 1·3 + 2",   "Div(5)={1,5}",   "Div(3)={1,3}",     "{1}"),
        ("(3, 2)",  "3 = 1·2 + 1",   "Div(3)={1,3}",   "Div(2)={1,2}",     "{1}"),
        ("(2, 1)",  "2 = 2·1 + 0",   "Div(2)={1,2}",   "Div(1)={1}",       "{1}"),
        ("(1, 0)",  "Halt → g = 1",  "Div(1)={1}",     "Div(0)=ℕ",         "{1}"),
    ]
    for idx, (st_pair, cut_eq, da, db, inter) in enumerate(fib_steps):
        ry = sy + 44 + idx * 34
        is_last = (idx == 5)
        svg.rect(lx + 14, ry - 15, lw - 28, 28,
                 fill=PURPLE_FILL if is_last else BG,
                 stroke=PURPLE if is_last else GRAY_LIGHT,
                 stroke_width=1.5 if is_last else 0.8, rx=4)
        svg.text(lx + 22, ry + 3, st_pair, font=FONT_SERIF, size=12, fill=NAVY, weight="bold")
        svg.text(lx + 78, ry + 3, cut_eq, font=FONT_SANS, size=11.5, fill=INK)
        svg.text(lx + 175, ry + 3, f"{da} ∩ {db}", font=FONT_SANS, size=11, fill=GRAY_DARK)
        svg.text(lx + lw - 22, ry + 3, f"= {inter}", font=FONT_SERIF, size=12, fill=PURPLE, anchor="end", weight="bold")

    svg.text(lx + lw / 2, ly + lh - 18,
             "Result: Gcd(13, 8) = { g | Div(g) = {1} } = { 1 }  (only unit square tiles both)",
             font=FONT_SERIF, size=12.5, fill=NAVY, anchor="middle", weight="bold")

    # RIGHT HALF: Degenerate / Identity Case (21, 0) -> 21 and (0, 0) -> 0
    rx, ry, rw_box, rh_box = 470, 80, 400, 535
    svg.rect(rx, ry, rw_box, rh_box, fill="#faf9f0", stroke=PURPLE, stroke_width=1.6, rx=6)
    svg.text(rx + 14, ry + 24, "Case 2: Zero Side Length  (a = 21, b = 0  →  g = 21)",
             font=FONT_SERIF, size=14.5, fill=NAVY, weight="bold")
    svg.text(rx + 14, ry + 43, "Why Div(0) = ℕ in the type definition: every d tiles 0 (0 = 0 × d)!",
             font=FONT_SANS, size=12, fill=PURPLE, weight="bold")

    svg.rect(rx + 14, ry + 56, rw_box - 28, 92, fill=PURPLE_LIGHT, stroke=PURPLE, stroke_width=1.2, rx=5)
    svg.text(rx + 24, ry + 75, "Geometric meaning of  d ∣ 0  (for every d ∈ ℕ):",
             font=FONT_SERIF, size=12.5, fill=INK, weight="bold")
    svg.text(rx + 24, ry + 94, "• Zero copies of a d×d square cover height 0:  0 = 0 · d.",
             font=FONT_SANS, size=11.5, fill=INK)
    svg.text(rx + 24, ry + 113, "• So b = 0 imposes NO restriction on d:  Div(0) = ℕ = {1, 2, 3, …}.",
             font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")
    svg.text(rx + 24, ry + 133, "• Intersecting with Div(0) is identity:  Div(a) ∩ Div(0) = Div(a).",
             font=FONT_SERIF, size=12, fill=NAVY, weight="bold")

    svg.text(rx + 14, ry + 172, "Degenerate 21 × 0 rectangle (1D segment of length 21):",
             font=FONT_SERIF, size=13, fill=INK, weight="bold")

    seg_x = rx + 68
    s21 = 13.0  # 21 * 13 = 273px; for d=6, 24 * 13 = 312px -> fits inside box!
    seg_w = 21 * s21

    tile_tests_21 = [
        (21, True,  "21 = 1 × 21  (coarsest tile = gcd)"),
        (7,  True,  "21 = 3 × 7   (fits cleanly)"),
        (3,  True,  "21 = 7 × 3   (fits cleanly)"),
        (1,  True,  "21 = 21 × 1  (fits cleanly)"),
        (6,  False, "21 = 3 × 6 + 3  (overhangs by 3!)"),
    ]

    for idx, (d, fits, desc) in enumerate(tile_tests_21):
        ty = ry + 194 + idx * 50
        svg.text(rx + 14, ty + 13, f"d = {d}", font=FONT_SERIF, size=12.5,
                 fill=PURPLE if fits else RED, weight="bold")

        svg.line(seg_x, ty, seg_x + seg_w, ty, stroke=NAVY, stroke_width=3)
        svg.line(seg_x, ty - 4, seg_x, ty + 4, stroke=NAVY, stroke_width=2)
        svg.line(seg_x + seg_w, ty - 4, seg_x + seg_w, ty + 4, stroke=NAVY, stroke_width=2)

        n_ceil = math.ceil(21 / d)
        for k in range(n_ceil):
            ix0 = seg_x + k * d * s21
            iw = d * s21
            is_over = (k * d + d > 21)
            svg.rect(ix0, ty + 5, iw, 14,
                     fill="url(#errHatch)" if is_over else (PURPLE_FILL if d == 21 else "#ece9fa"),
                     stroke=RED if is_over else (NAVY if d == 21 else PURPLE),
                     stroke_width=1.6 if d == 21 else 1.1)

        svg.text(seg_x, ty + 32, desc, font=FONT_SANS, size=11.5,
                 fill=NAVY if d == 21 else (PURPLE if fits else RED),
                 weight="bold" if (d == 21 or not fits) else "normal")

    by_box = ry + 448
    svg.rect(rx + 14, by_box, rw_box - 28, 74, fill="#f3f1fa", stroke=NAVY, stroke_width=1.4, rx=5)
    svg.text(rx + 22, by_box + 20, "Corner Case:  Gcd(0, 0) = { g | Div(g) = Div(0) ∩ Div(0) = ℕ } = { 0 }",
             font=FONT_SERIF, size=12, fill=NAVY, weight="bold")
    svg.text(rx + 22, by_box + 40, "• Every d ∈ ℕ tiles a 0×0 point (0 = 0·d). Only g = 0 has Div(g) = ℕ.",
             font=FONT_SANS, size=11.5, fill=INK)
    svg.text(rx + 22, by_box + 58, "• Div(a) ∩ Div(b) makes gcd(21,0) = 21 and gcd(0,0) = 0 automatic!",
             font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")

    with open("fig-3.svg", "w") as f:
        f.write(svg.render())


# ============================================================================
# FIGURE 4: Type Errors in the Visual Language (Wrong Candidate Values & Buggy Step)
# ============================================================================
def make_fig4():
    svg = SvgBuilder(900, 650)
    svg.add_standard_defs()

    svg.add_header(
        "Type Errors: Overhanging Tiles or Missing Coarser Tiles Violate Gcd(12, 8)",
        f'A candidate <tspan fill="{INK}">g</tspan> inhabits <tspan fill="{PURPLE}" font-weight="bold">Gcd(a, b)</tspan> '
        f'iff (1) <tspan fill="{PURPLE}">g tiles a×b</tspan> (Div(g) ⊆ Div(a)∩Div(b)) AND '
        f'(2) <tspan fill="{PURPLE}">every common tile divides g</tspan> (Div(a)∩Div(b) ⊆ Div(g))'
    )

    col_w = 272
    col_h = 378
    y0 = 82

    # --- COLUMN 1: Error Type A: g = 8 (Too Large / Does Not Divide a) ---
    c1x = 30
    svg.rect(c1x, y0, col_w, col_h, fill="#fdf7f7", stroke=RED, stroke_width=2.0, rx=6)
    svg.rect(c1x, y0, col_w, 28, fill=RED, stroke="none", rx=5)
    svg.rect(c1x, y0 + 14, col_w, 14, fill=RED, stroke="none")
    svg.text(c1x + col_w / 2, y0 + 19, "TYPE ERROR 1:  Return g = 8  for (12, 8)",
             font=FONT_SANS, size=12.5, fill=BG, anchor="middle", weight="bold")

    svg.text(c1x + 12, y0 + 48, "Bug: returning input b = 8 instead of gcd",
             font=FONT_SANS, size=11.5, fill=RED, weight="bold")
    svg.text(c1x + 12, y0 + 66, "Violates Soundness:  g ∤ a   (8 ∤ 12)",
             font=FONT_SERIF, size=12.5, fill=RED, weight="bold")

    s = 12.2  # 12*12.2 = 146.4, 8*12.2 = 97.6; 16*12.2 = 195.2px
    rx1 = c1x + 42
    ry1 = y0 + 96
    svg.rect(rx1, ry1, 8 * s, 8 * s, fill="#e5e3f3", stroke=NAVY, stroke_width=1.8)
    svg.rect(rx1 + 8 * s, ry1, 4 * s, 8 * s, fill=RED_FILL, stroke=RED, stroke_width=1.5)
    svg.rect(rx1 + 12 * s, ry1, 4 * s, 8 * s, fill="url(#errHatch)", stroke=RED, stroke_width=2.2, dash="4,2")
    svg.rect(rx1, ry1, 12 * s, 8 * s, fill="none", stroke=NAVY, stroke_width=2.6)

    svg.text(rx1 + 6 * s, ry1 - 8, "True width a = 12", font=FONT_SERIF, size=11.5, fill=NAVY, anchor="middle", weight="bold")
    svg.text(rx1 + 14 * s, ry1 - 8, "+4 overhang!", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")
    svg.text(rx1 - 5, ry1 + 4 * s + 4, "b=8", font=FONT_SERIF, size=11.5, fill=NAVY, anchor="end", weight="bold")
    svg.text(rx1 + 4 * s, ry1 + 4 * s + 4, "8 × 8 tile", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
    svg.text(rx1 + 10 * s, ry1 + 4 * s - 2, "part", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")
    svg.text(rx1 + 10 * s, ry1 + 4 * s + 11, "4×8", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")

    # White pill label over the hatched overhang so it's crystal clear
    svg.rect(rx1 + 12.3 * s, ry1 + 3.0 * s, 3.4 * s, 2.0 * s, fill=BG, stroke=RED, stroke_width=1, rx=2)
    svg.text(rx1 + 14 * s, ry1 + 4.3 * s, "4×8", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")

    svg.line(rx1, ry1 + 8 * s + 14, rx1 + 16 * s, ry1 + 8 * s + 14, stroke=RED, stroke_width=1.5, marker_start="arrowRed", marker_end="arrowRed")
    svg.text(c1x + col_w / 2, ry1 + 8 * s + 30, "2 tiles × 8 = 16 ≠ 12  (12 mod 8 = 4 ≠ 0)",
             font=FONT_SANS, size=11.5, fill=RED, anchor="middle", weight="bold")

    svg.rect(c1x + 12, y0 + 248, col_w - 24, 116, fill=BG, stroke=RED, stroke_width=1.2, rx=4)
    svg.text(c1x + 20, y0 + 268, "Set Check:", font=FONT_SERIF, size=12.5, fill=INK, weight="bold")
    svg.text(c1x + 20, y0 + 288, "Div(8) = { 1, 2, 4, 8 }", font=FONT_SERIF, size=12, fill=RED, weight="bold")
    svg.text(c1x + 20, y0 + 307, "Div(12) ∩ Div(8) = { 1, 2, 4 }", font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")
    svg.text(c1x + 20, y0 + 330, "✗  8 ∈ Div(8)  but  8 ∉ Div(12) ∩ Div(8)", font=FONT_SANS, size=11.5, fill=RED, weight="bold")
    svg.text(c1x + 20, y0 + 349, "✗  Div(8) ⊈ Div(12) ∩ Div(8)  ⇒  8 ∉ Gcd(12,8)", font=FONT_SANS, size=11.5, fill=RED, weight="bold")

    # --- COLUMN 2: Error Type B: g = 2 (Common Divisor, Not GREATEST) ---
    c2x = 314
    svg.rect(c2x, y0, col_w, col_h, fill="#fdf7f7", stroke=RED, stroke_width=2.0, rx=6)
    svg.rect(c2x, y0, col_w, 28, fill=RED, stroke="none", rx=5)
    svg.rect(c2x, y0 + 14, col_w, 14, fill=RED, stroke="none")
    svg.text(c2x + col_w / 2, y0 + 19, "TYPE ERROR 2:  Return g = 2  for (12, 8)",
             font=FONT_SANS, size=12.5, fill=BG, anchor="middle", weight="bold")

    svg.text(c2x + 12, y0 + 48, "Bug: returning a non-maximal common divisor",
             font=FONT_SANS, size=11.5, fill=RED, weight="bold")
    svg.text(c2x + 12, y0 + 66, "Violates Completeness:  4 ∣ 12 ∧ 4 ∣ 8  but  4 ∤ 2",
             font=FONT_SERIF, size=12, fill=RED, weight="bold")

    rx2 = c2x + 16
    ry2 = y0 + 98
    s2 = 10.5  # 12*10.5 = 126, 8*10.5 = 84
    draw_tiled_rect(svg, rx2, ry2, 12, 8, 2, s2, show_dims=False)
    for ix in range(1, 3):
        svg.line(rx2 + ix * 4 * s2, ry2, rx2 + ix * 4 * s2, ry2 + 8 * s2, stroke=NAVY, stroke_width=2.2)
    svg.line(rx2, ry2 + 4 * s2, rx2 + 12 * s2, ry2 + 4 * s2, stroke=NAVY, stroke_width=2.2)
    svg.text(rx2, ry2 - 8, "2×2 tiles 12×8, and d=4 also tiles!", font=FONT_SANS, size=11, fill=NAVY, anchor="start", weight="bold")

    tx2 = rx2 + 12 * s2 + 38
    ty2 = ry2 + 16
    svg.rect(tx2, ty2, 4 * s2, 4 * s2, fill="url(#errHatch)", stroke=RED, stroke_width=2, dash="4,2")
    svg.rect(tx2, ty2, 2 * s2, 2 * s2, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2.4)
    svg.text(tx2 + 1 * s2, ty2 + 1 * s2 + 4, "g=2", font=FONT_SERIF, size=11, fill=NAVY, anchor="middle", weight="bold")
    svg.text(tx2 + 2 * s2, ty2 - 6, "d=4 > g=2!", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")
    svg.text(tx2 + 2 * s2, ty2 + 4 * s2 + 15, "4 ∤ 2", font=FONT_SERIF, size=12, fill=RED, anchor="middle", weight="bold")

    svg.text(c2x + col_w / 2, ry2 + 8 * s2 + 28,
             "2×2 is too fine: misses valid common tile d = 4",
             font=FONT_SANS, size=11.5, fill=RED, anchor="middle", weight="bold")

    svg.rect(c2x + 12, y0 + 248, col_w - 24, 116, fill=BG, stroke=RED, stroke_width=1.2, rx=4)
    svg.text(c2x + 20, y0 + 268, "Set Check:", font=FONT_SERIF, size=12.5, fill=INK, weight="bold")
    svg.text(c2x + 20, y0 + 288, "Div(2) = { 1, 2 }", font=FONT_SERIF, size=12, fill=RED, weight="bold")
    svg.text(c2x + 20, y0 + 307, "Div(12) ∩ Div(8) = { 1, 2, 4 }", font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")
    svg.text(c2x + 20, y0 + 330, "✗  4 ∈ Div(12) ∩ Div(8)  but  4 ∉ Div(2)", font=FONT_SANS, size=11.5, fill=RED, weight="bold")
    svg.text(c2x + 20, y0 + 349, "✗  Div(12) ∩ Div(8) ⊈ Div(2)  ⇒  2 ∉ Gcd(12,8)", font=FONT_SANS, size=11.5, fill=RED, weight="bold")

    # --- COLUMN 3: Unique Valid Inhabitant g = 4 ---
    c3x = 598
    svg.rect(c3x, y0, col_w, col_h, fill="#f7f5fc", stroke=PURPLE, stroke_width=2.2, rx=6)
    svg.rect(c3x, y0, col_w, 28, fill=PURPLE, stroke="none", rx=5)
    svg.rect(c3x, y0 + 14, col_w, 14, fill=PURPLE, stroke="none")
    svg.text(c3x + col_w / 2, y0 + 19, "WELL-TYPED:  Return g = 4  for (12, 8)",
             font=FONT_SANS, size=12.5, fill=BG, anchor="middle", weight="bold")

    svg.text(c3x + 12, y0 + 48, "Exact refinement match: both inclusions hold",
             font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")
    svg.text(c3x + 12, y0 + 66, "4 ∣ 12 ∧ 4 ∣ 8   AND   ∀d ∈ {1,2,4}. d ∣ 4",
             font=FONT_SERIF, size=12, fill=NAVY, weight="bold")

    rx3 = c3x + 16
    ry3 = y0 + 98
    draw_tiled_rect(svg, rx3, ry3, 12, 8, 4, s2, show_dims=False)
    svg.text(rx3 + 6 * s2, ry3 - 8, "4×4 tiles 12×8 (0 overhang)", font=FONT_SANS, size=11, fill=NAVY, anchor="middle", weight="bold")

    tx3 = rx3 + 12 * s2 + 38
    ty3 = ry3 + 16
    svg.rect(tx3, ty3, 4 * s2, 4 * s2, fill=PURPLE_FILL, stroke=NAVY, stroke_width=2.4)
    svg.line(tx3 + 2 * s2, ty3, tx3 + 2 * s2, ty3 + 4 * s2, stroke=PURPLE, stroke_width=1.3, dash="3,2")
    svg.line(tx3, ty3 + 2 * s2, tx3 + 4 * s2, ty3 + 2 * s2, stroke=PURPLE, stroke_width=1.3, dash="3,2")
    svg.text(tx3 + 2 * s2, ty3 - 6, "g=4 fits {1,2,4}", font=FONT_SANS, size=11, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(tx3 + 2 * s2, ty3 + 4 * s2 + 15, "Div(4)={1,2,4}", font=FONT_SERIF, size=11.5, fill=PURPLE, anchor="middle", weight="bold")

    svg.text(c3x + col_w / 2, ry3 + 8 * s2 + 28,
             "Coarsest common grid = unique inhabitant",
             font=FONT_SANS, size=11.5, fill=NAVY, anchor="middle", weight="bold")

    svg.rect(c3x + 12, y0 + 248, col_w - 24, 116, fill=BG, stroke=PURPLE, stroke_width=1.5, rx=4)
    svg.text(c3x + 20, y0 + 268, "Set Check:", font=FONT_SERIF, size=12.5, fill=INK, weight="bold")
    svg.text(c3x + 20, y0 + 288, "Div(4) = { 1, 2, 4 }", font=FONT_SERIF, size=12, fill=NAVY, weight="bold")
    svg.text(c3x + 20, y0 + 307, "Div(12) ∩ Div(8) = { 1, 2, 4 }", font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")
    svg.text(c3x + 20, y0 + 330, "✓  Div(4) ⊆ Div(12)∩Div(8)  (4 tiles 12×8)", font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")
    svg.text(c3x + 20, y0 + 349, "✓  Div(12)∩Div(8) ⊆ Div(4)  (all d tile 4)", font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")

    # --- BOTTOM PANEL: Buggy Program Transition ---
    by0 = 474
    bh = 154
    svg.rect(30, by0, 840, bh, fill="#fdf7f7", stroke=RED, stroke_width=2.0, rx=6)
    svg.text(46, by0 + 24, "TYPE ERROR 3 (Buggy Loop Step):  (x, y) → (y, (x mod y) − 1)   Destroys the Loop Invariant!",
             font=FONT_SERIF, size=14, fill=RED, weight="bold")
    svg.text(46, by0 + 44, "Suppose a buggy transition on (12, 8) computes remainder r' = (12 mod 8) − 1 = 3 instead of 4, stepping to (8, 3):",
             font=FONT_SANS, size=12.5, fill=INK)

    bs = 9.0
    bx1 = 55
    by1 = by0 + 64
    draw_tiled_rect(svg, bx1, by1, 12, 8, 4, bs, show_dims=False)
    svg.text(bx1 + 6 * bs, by1 - 5, "Pre-state (12, 8): 4×4 fits", font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(bx1 + 6 * bs, by1 + 8 * bs + 14, "Type: Gcd(12, 8) = {4}", font=FONT_SERIF, size=12, fill=PURPLE, anchor="middle", weight="bold")

    svg.line(bx1 + 12 * bs + 18, by1 + 4 * bs, bx1 + 12 * bs + 88, by1 + 4 * bs, stroke=RED, stroke_width=2.5, dash="4,2", marker_end="arrowRed")
    svg.text(bx1 + 12 * bs + 53, by1 + 4 * bs - 8, "BUGGY CUT", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")
    svg.text(bx1 + 12 * bs + 53, by1 + 4 * bs + 15, "r' = 3 ≠ 4", font=FONT_SERIF, size=11.5, fill=RED, anchor="middle", weight="bold")

    bx2 = bx1 + 12 * bs + 108
    by2 = by1 + 12
    draw_tiled_rect(svg, bx2, by2, 8, 3, 4, bs, show_dims=False)
    svg.text(bx2 + 4 * bs, by2 - 6, "Post-state (8, 3): 4×4 overhangs height 3!", font=FONT_SANS, size=11.5, fill=RED, anchor="middle", weight="bold")
    svg.text(bx2 + 4 * bs, by2 + 4 * bs + 16, "Type mutated: Gcd(8, 3) = {1} ≠ {4}", font=FONT_SERIF, size=12, fill=RED, anchor="middle", weight="bold")

    ex_x = 460
    svg.rect(ex_x, by0 + 56, 394, 84, fill=BG, stroke=RED, stroke_width=1.2, rx=4)
    svg.text(ex_x + 14, by0 + 76, "Refinement Type Checker Diagnosis at Loop Back-Edge:", font=FONT_SANS, size=12, fill=RED, weight="bold")
    svg.text(ex_x + 14, by0 + 96, "Expected return type:   Gcd(12, 8)  where  Div(12) ∩ Div(8) = {1, 2, 4}", font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")
    svg.text(ex_x + 14, by0 + 115, "Recursive call type:    Gcd(8, 3)   where  Div(8) ∩ Div(3)  = {1}", font=FONT_SERIF, size=12, fill=RED, weight="bold")
    svg.text(ex_x + 14, by0 + 133, "✗  Subtyping fails:  Gcd(8, 3) ⊈ Gcd(12, 8)  because  {1, 2, 4} ≠ {1}!", font=FONT_SANS, size=12, fill=RED, weight="bold")

    with open("fig-4.svg", "w") as f:
        f.write(svg.render())


# ============================================================================
# FIGURE 5: Dependent Type Family Indexed by (x,y) & Symbolic Proof in Codillon
# ============================================================================
def make_fig5():
    svg = SvgBuilder(900, 650)
    svg.add_standard_defs()

    svg.add_header(
        "Dependent Type Fibers Gcd(x, y) Collapse Along Euclid's Cut Trajectories",
        f'Dependent family <tspan fill="{PURPLE}" font-weight="bold">(x, y) ↦ Gcd(x, y)</tspan> over <tspan fill="{INK}">ℕ × ℕ</tspan>, '
        f'and symbolic evidence preservation for <tspan fill="{INDIGO}" font-weight="bold">unknown (x, y)</tspan>'
    )

    # LEFT PANEL: The (x, y) index plane partitioned into iso-type fibers
    lx, ly, lw, lh = 30, 80, 425, 540
    svg.rect(lx, ly, lw, lh, fill="#faf9f0", stroke=PURPLE, stroke_width=1.6, rx=6)
    svg.text(lx + 14, ly + 24, "1. Dependent Index Plane (x, y) and Iso-Type Fibers",
             font=FONT_SERIF, size=14, fill=INK, weight="bold")
    svg.text(lx + 14, ly + 42, "Every trajectory (x, y) → (y, x mod y) stays inside one fiber Gcd = {g}:",
             font=FONT_SANS, size=12, fill=GRAY_DARK)

    gx0 = lx + 58
    gy0 = ly + 390
    step = 26.5

    for i in range(13):
        px = gx0 + i * step
        py = gy0 - i * step
        svg.line(px, gy0, px, gy0 - 12 * step, stroke=GRAY_FAINT, stroke_width=1)
        svg.line(gx0, py, gx0 + 12 * step, py, stroke=GRAY_FAINT, stroke_width=1)
        svg.text(px, gy0 + 15, str(i), font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")
        svg.text(gx0 - 10, py + 4, str(i), font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="end")

    svg.line(gx0, gy0, gx0 + 12 * step + 10, gy0, stroke=INK, stroke_width=1.5)
    svg.line(gx0, gy0, gx0, gy0 - 12 * step - 10, stroke=INK, stroke_width=1.5)
    svg.text(gx0 + 6 * step, gy0 + 32, "width x ∈ ℕ", font=FONT_SERIF, size=12.5, fill=INK, anchor="middle", weight="bold")
    svg.text(gx0 - 34, gy0 - 6 * step, "y ∈ ℕ", font=FONT_SERIF, size=12.5, fill=INK, anchor="middle", weight="bold")

    # Draw trajectory lines FIRST so circles & numbers sit cleanly on top of arrows
    pts_g4 = [(12, 8), (8, 4), (4, 0)]
    for (x1, y1), (x2, y2) in zip(pts_g4, pts_g4[1:]):
        p1x, p1y = gx0 + x1 * step, gy0 - y1 * step
        p2x, p2y = gx0 + x2 * step, gy0 - y2 * step
        # Shorten endpoint slightly so arrowhead lands right on circle rim
        dx, dy = p2x - p1x, p2y - p1y
        dist = math.hypot(dx, dy)
        p2x_adj = p2x - (dx / dist) * 8.5
        p2y_adj = p2y - (dy / dist) * 8.5
        svg.line(p1x, p1y, p2x_adj, p2y_adj, stroke=PURPLE, stroke_width=2.5, marker_end="arrowPurple")

    pts_g3 = [(9, 6), (6, 3), (3, 0)]
    for (x1, y1), (x2, y2) in zip(pts_g3, pts_g3[1:]):
        p1x, p1y = gx0 + x1 * step, gy0 - y1 * step
        p2x, p2y = gx0 + x2 * step, gy0 - y2 * step
        dx, dy = p2x - p1x, p2y - p1y
        dist = math.hypot(dx, dy)
        p2x_adj = p2x - (dx / dist) * 8.0
        p2y_adj = p2y - (dy / dist) * 8.0
        svg.line(p1x, p1y, p2x_adj, p2y_adj, stroke=NAVY, stroke_width=2.0, dash="4,2", marker_end="arrowNavy")

    # Now draw fiber nodes on top
    for xv in range(13):
        for yv in range(13):
            g_val = math.gcd(xv, yv)
            px = gx0 + xv * step
            py = gy0 - yv * step
            if g_val == 4:
                svg.circle(px, py, 7.5, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=1.8)
                svg.text(px, py + 3.5, "4", font=FONT_SANS, size=11, fill=PURPLE, anchor="middle", weight="bold")
            elif g_val == 3:
                svg.circle(px, py, 6.5, fill=NAVY_FILL, stroke=NAVY, stroke_width=1.4)
                svg.text(px, py + 3.5, "3", font=FONT_SANS, size=11, fill=NAVY, anchor="middle", weight="bold")
            elif xv == 0 and yv == 0:
                svg.circle(px, py, 5, fill=GRAY_LIGHT, stroke=INK, stroke_width=1)
            else:
                svg.circle(px, py, 2.2, fill=GRAY_LIGHT, stroke="none")

    # Clean callout labels in empty grid cells (avoiding all (x,y) with gcd=3 or 4)
    svg.text(gx0 + 11.4 * step, gy0 - 8 * step - 11, "(12,8)", font=FONT_SANS, size=11, fill=PURPLE, anchor="end", weight="bold")
    svg.text(gx0 + 8 * step + 10, gy0 - 4 * step + 14, "(8,4)", font=FONT_SANS, size=11, fill=PURPLE, anchor="start", weight="bold")
    svg.text(gx0 + 4 * step + 14, gy0 - 9, "(4,0)★", font=FONT_SANS, size=11, fill=PURPLE, anchor="start", weight="bold")

    # Label for (9,6)->(6,3)->(3,0) placed cleanly at (9.2, 6.8)
    svg.text(gx0 + 9 * step - 10, gy0 - 6 * step - 11, "(9,6)→(6,3)→(3,0)", font=FONT_SANS, size=11, fill=NAVY, anchor="middle", weight="bold")

    # Bottom caption inside Left Panel
    svg.rect(lx + 12, ly + 436, lw - 24, 90, fill=PURPLE_LIGHT, stroke=PURPLE, stroke_width=1.2, rx=4)
    svg.text(lx + 20, ly + 455, "Dependent Type Reading:", font=FONT_SERIF, size=12.5, fill=PURPLE, weight="bold")
    svg.text(lx + 20, ly + 474, "• Fiber 4 = { (x, y) | Gcd(x, y) = {4} }  (purple: (12,8), (8,4), (4,0), …)",
             font=FONT_SANS, size=11.5, fill=PURPLE, weight="bold")
    svg.text(lx + 20, ly + 493, "• Fiber 3 = { (x, y) | Gcd(x, y) = {3} }  (navy: (9,6), (6,3), (3,0), …)",
             font=FONT_SANS, size=11.5, fill=NAVY, weight="bold")
    svg.text(lx + 20, ly + 512, "• Halting on x-axis (y = 0) reveals the fiber's unique inhabitant x = g!",
             font=FONT_SANS, size=11.5, fill=INK, weight="bold")

    # RIGHT PANEL: Symbolic Unknown (x, y) in Indigo (#4b0082) & Codillon Editor Inspector
    rx, ry, rw, rh = 470, 80, 400, 540
    svg.rect(rx, ry, rw, rh, fill="#faf9f0", stroke=INDIGO, stroke_width=1.6, rx=6)
    svg.text(rx + 14, ry + 24, "2. Symbolic Verification for Unknown (x, y) in Codillon",
             font=FONT_SERIF, size=14, fill=INDIGO, weight="bold")
    svg.text(rx + 14, ry + 42, "At compile time (x, y) are unknown (indigo), yet the proof is exact:",
             font=FONT_SANS, size=12, fill=GRAY_DARK)

    sx0 = rx + 28
    sy0 = ry + 68
    sq_s = 88

    svg.rect(sx0, sy0, sq_s, sq_s, fill=PURPLE_LIGHT, stroke=INDIGO, stroke_width=2)
    svg.rect(sx0 + sq_s, sy0, sq_s, sq_s, fill=PURPLE_LIGHT, stroke=INDIGO, stroke_width=2)
    svg.rect(sx0 + 2 * sq_s, sy0, 74, sq_s, fill="#f3f0fa", stroke=INDIGO, stroke_width=2, dash="4,2")
    svg.rect(sx0 + 2 * sq_s + 74, sy0, 58, sq_s, fill=PURPLE_FILL, stroke=INDIGO, stroke_width=2.2)

    d_step = 22
    for kx in range(1, int((2 * sq_s) // d_step)):
        svg.line(sx0 + kx * d_step, sy0, sx0 + kx * d_step, sy0 + sq_s, stroke=PURPLE, stroke_width=0.8, dash="2,2")
    for ky in range(1, 4):
        svg.line(sx0, sy0 + ky * d_step, sx0 + 2 * sq_s + 132, sy0 + ky * d_step, stroke=PURPLE, stroke_width=0.8, dash="2,2")

    cut_x = sx0 + 2 * sq_s + 74
    svg.line(cut_x, sy0 - 6, cut_x, sy0 + sq_s + 6, stroke=RED, stroke_width=2.2, dash="4,2")

    svg.text(sx0 + sq_s / 2, sy0 + sq_s / 2 + 4, "y × y", font=FONT_SERIF, size=13, fill=INDIGO, anchor="middle", weight="bold")
    svg.text(sx0 + 1.5 * sq_s, sy0 + sq_s / 2 + 4, "y × y", font=FONT_SERIF, size=13, fill=INDIGO, anchor="middle", weight="bold")
    svg.text(sx0 + 2 * sq_s + 37, sy0 + sq_s / 2 + 4, "… (q copies)", font=FONT_SERIF, size=12, fill=INDIGO, anchor="middle", style="italic")
    svg.text(cut_x + 29, sy0 + sq_s / 2 - 4, "r × y", font=FONT_SERIF, size=12.5, fill=INDIGO, anchor="middle", weight="bold")
    svg.text(cut_x + 29, sy0 + sq_s / 2 + 12, "(r = x%y)", font=FONT_SANS, size=11, fill=INDIGO, anchor="middle")

    svg.text(sx0 + 154, sy0 - 8, "unknown width x = q·y + r", font=FONT_SERIF, size=12.5, fill=INDIGO, anchor="middle", weight="bold")
    svg.text(sx0 - 6, sy0 + sq_s / 2 + 4, "y", font=FONT_SERIF, size=13, fill=INDIGO, anchor="end", weight="bold")

    svg.rect(sx0, sy0 + sq_s - d_step, d_step, d_step, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=1.8)
    svg.text(sx0 + d_step / 2, sy0 + sq_s - d_step / 2 + 4, "d", font=FONT_SERIF, size=11, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(sx0 + 154, sy0 + sq_s + 18,
             "For any unknown d:  (d ∣ x ∧ d ∣ y)  ⇔  (d ∣ y ∧ d ∣ (x mod y))",
             font=FONT_SERIF, size=12, fill=INDIGO, anchor="middle", weight="bold")

    ed_y = ry + 196
    ed_h = 330
    svg.rect(rx + 14, ed_y, rw - 28, ed_h, fill=BG, stroke=INK, stroke_width=1.5, rx=5)
    svg.rect(rx + 14, ed_y, rw - 28, 26, fill=INK, stroke="none", rx=4)
    svg.rect(rx + 14, ed_y + 13, rw - 28, 13, fill=INK, stroke="none")
    svg.text(rx + 26, ed_y + 17, "Codillon Structured Wasm — Live Refinement Type Pane",
             font=FONT_SANS, size=12, fill=BG, weight="bold")

    code_lines = [
        ("fn euclid(a: ℕ, b: ℕ) -> ", "g : { v ∈ ℕ | Div(v) = Div(a) ∩ Div(b) }", INDIGO),
        ("  let mut (x, y) = (a, b)",  "Invariant I: Div(x) ∩ Div(y) = Div(a) ∩ Div(b)", PURPLE),
        ("  loop {",                   "I holds on entry: Div(a) ∩ Div(b) = Div(a) ∩ Div(b)", PURPLE),
        ("    if (y == 0) {",          "Branch evidence: y = 0  ⇒  Div(y) = Div(0) = ℕ", NAVY),
        ("      return x",             "Div(x) = Div(x)∩ℕ = Div(x)∩Div(y) = Div(a)∩Div(b) ✓", NAVY),
        ("    }",                      "Else branch: y > 0  ⇒  x mod y is well-defined", GRAY_DARK),
        ("    (x, y) = (y, x % y)",    "Cut q squares: Div(y)∩Div(x%y) = Div(x)∩Div(y) ✓", PURPLE),
        ("  }",                        "Evidence erased at runtime; Wasm emits raw i32.rem_u", GRAY_DARK),
    ]

    cy_code = ed_y + 46
    for idx, (code_str, type_str, col) in enumerate(code_lines):
        y_pos = cy_code + idx * 35
        svg.rect(rx + 22, y_pos - 14, rw - 44, 30, fill="#f7f6ee" if idx % 2 == 0 else "#efeee4", stroke=GRAY_LIGHT, stroke_width=0.6, rx=3)
        svg.text(rx + 28, y_pos - 1, code_str, font="monospace", size=11.5, fill=INK, weight="bold")
        if type_str:
            svg.text(rx + 28, y_pos + 12, type_str, font=FONT_SANS, size=11, fill=col, weight="bold")

    with open("fig-5.svg", "w") as f:
        f.write(svg.render())


if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    print("Generated fig-1.svg through fig-5.svg successfully.")
