#!/usr/bin/env python3
"""
gen.py - Generate SVG figures for Angle 09: Typing Derivation as Composed Pictures
Visualizes gcd(a, b) as a refinement type through composable state-set tiles and docking ports.
"""

import math
import html

# Palette strictly following instructions (NO GREEN ANYWHERE)
BG = "#fffff0"          # ivory background
INK = "#222222"         # primary ink
PURPLE = "#6A5ACD"      # type / region border & accent (slate blue / purple)
PURPLE_FILL = "#d9d5f2" # muted purple fill for type sets
PURPLE_LIGHT = "#efedfa"# subtle purple tint for backgrounds/containers
RED = "#8b0000"         # dark red ONLY for violation / type error
RED_FILL = "#f9e2e2"    # light red fill ONLY for violation / type error
INDIGO = "#4b0082"      # indigo ONLY for "unknown" / abstract symbolic
NAVY = "#00008b"        # navy for concrete run or value
GRAY_DARK = "#555555"   # secondary labels
GRAY_MID = "#888888"    # grid lines, context borders
GRAY_LIGHT = "#dedede"  # muted non-member dots / grid
GRAY_BG = "#f5f5e8"     # subtle panel background

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"


def divisors(n, max_d=999):
    """Return sorted list of positive divisors of n. For n=0, returns 1..max_d."""
    if n == 0:
        return list(range(1, max_d + 1))
    return [d for d in range(1, abs(n) + 1) if n % d == 0 and d <= max_d]


def common_divisors(a, b, max_d=999):
    if a == 0 and b == 0:
        return list(range(1, max_d + 1))
    return divisors(math.gcd(a, b), max_d)


def inv_states(a, b, max_x=14, max_y=12):
    """Return set of (x, y) in [0..max_x] x [0..max_y] where gcd(x, y) == gcd(a, b)."""
    g = math.gcd(a, b)
    pts = set()
    for x in range(max_x + 1):
        for y in range(max_y + 1):
            if math.gcd(x, y) == g:
                pts.add((x, y))
    return pts


def euclid_trace(a, b):
    """Return list of (x, y) states in Euclid's algorithm."""
    pts = [(a, b)]
    x, y = a, b
    while y != 0:
        x, y = y, x % y
        pts.append((x, y))
    return pts


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

    def add_standard_defs(self):
        # Arrow markers in INK, PURPLE, NAVY, RED, GRAY_MID, INDIGO
        markers = [
            ("arrow-ink", INK),
            ("arrow-purple", PURPLE),
            ("arrow-navy", NAVY),
            ("arrow-red", RED),
            ("arrow-gray", GRAY_MID),
            ("arrow-indigo", INDIGO),
        ]
        for mid, col in markers:
            self.add_def(f'''
            <marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5"
                    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{col}"/>
            </marker>''')

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, rx=0, dash=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ''
        rx_attr = f' rx="{rx}" ry="{rx}"' if rx else ''
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{rx_attr}{d_attr}{op_attr}/>')

    def circle(self, cx, cy, r, fill="none", stroke="none", sw=1, dash=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ''
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}{op_attr}/>')

    def ellipse(self, cx, cy, rx, ry, fill="none", stroke="none", sw=1, dash=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ''
        self.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}{op_attr}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1, dash=None, marker_end=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        m_attr = f' marker-end="url(#{marker_end})"' if marker_end else ''
        op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{sw}"{d_attr}{m_attr}{op_attr}/>')

    def path(self, d, fill="none", stroke=INK, sw=1, dash=None, marker_end=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        m_attr = f' marker-end="url(#{marker_end})"' if marker_end else ''
        op_attr = f' opacity="{opacity}"' if opacity < 1.0 else ''
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}{m_attr}{op_attr}/>')

    def text(self, x, y, txt, size=13, font=FONT_SERIF, fill=INK, anchor="start",
             weight="normal", style="normal", escape=True):
        content = html.escape(str(txt)) if escape else str(txt)
        w_attr = f' font-weight="{weight}"' if weight != "normal" else ''
        s_attr = f' font-style="{style}"' if style != "normal" else ''
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
                 f'fill="{fill}" text-anchor="{anchor}"{w_attr}{s_attr}>{content}</text>')

    def title_block(self, claim_text, subtitle_text):
        # Top header bar
        self.text(24, 30, claim_text, size=18, font=FONT_SERIF, fill=INK, weight="bold")
        self.text(24, 49, subtitle_text, size=12.5, font=FONT_SANS, fill=GRAY_DARK)
        self.line(24, 57, self.width - 24, 57, stroke=GRAY_LIGHT, sw=1)

    def render(self):
        defs_str = "\n".join(self.defs)
        body_str = "\n  ".join(self.elements)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">
  <defs>
    {defs_str}
  </defs>
  <rect x="0" y="0" width="{self.width}" height="{self.height}" fill="{BG}"/>
  {body_str}
</svg>
'''


# ==============================================================================
# Helper visual components for "Typing Derivation as Composed Pictures"
# ==============================================================================

def draw_puzzle_tile(svg, x, y, w, h, title, rule_badge="", border_col=INK, fill_col="#ffffff"):
    """
    Draw a rule judgment tile with a clean header bar and optional rule badge.
    """
    svg.rect(x, y, w, h, fill=fill_col, stroke=border_col, sw=1.8, rx=6)
    hdr_fill = PURPLE_LIGHT if border_col != RED else RED_FILL
    svg.rect(x, y, w, 24, fill=hdr_fill, stroke=border_col, sw=1.2, rx=6)
    # Cover bottom rounded corners of header bar cleanly
    svg.rect(x + 1, y + 18, w - 2, 6, fill=hdr_fill, stroke="none")
    svg.line(x, y + 24, x + w, y + 24, stroke=border_col, sw=1.2)
    svg.text(x + 10, y + 16.5, title, size=12.5, font=FONT_SERIF,
             fill=INK if border_col != RED else RED, weight="bold")
    if rule_badge:
        svg.text(x + w - 8, y + 16, rule_badge, size=11, font=FONT_SANS,
                 fill=PURPLE if border_col != RED else RED, anchor="end", weight="bold")


def draw_dock_connector(svg, x1, y1, x2, y2, label="⊆", ok=True, vertical=False):
    """
    Draw a visual docking connector between two ports:
    shows the containment / subtyping bridge P_out ⊆ P_in (or ⊈ in dark red when broken).
    """
    col = PURPLE if ok else RED
    fill = PURPLE_FILL if ok else RED_FILL
    mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    span = abs(x2 - x1) if not vertical else abs(y2 - y1)

    if not vertical:
        # Stop arrow 5px before right socket so arrowhead doesn't overlap socket ring
        svg.line(x1 + 4, y1, x2 - 5, y2, stroke=col, sw=2.2 if ok else 2.6,
                 dash=None if ok else "4,3", marker_end="arrow-purple" if ok else "arrow-red")
        svg.circle(x1, y1, 4.0, fill=col, stroke=BG, sw=1)
        svg.circle(x2, y2, 4.0, fill=BG, stroke=col, sw=1.8)
        bw = 24 if span < 50 else 28
        bh = 18
        svg.rect(mx - bw/2, my - bh/2, bw, bh, fill=fill, stroke=col, sw=1.4, rx=9)
        svg.text(mx, my + 4.5, label, size=12, font=FONT_SERIF, fill=col, anchor="middle", weight="bold")
    else:
        svg.line(x1, y1 + 4, x2, y2 - 5, stroke=col, sw=2.2 if ok else 2.6,
                 dash=None if ok else "4,3", marker_end="arrow-purple" if ok else "arrow-red")
        svg.circle(x1, y1, 4.0, fill=col, stroke=BG, sw=1)
        svg.circle(x2, y2, 4.0, fill=BG, stroke=col, sw=1.8)
        bw, bh = 28, 18
        svg.rect(mx - bw/2, my - bh/2, bw, bh, fill=fill, stroke=col, sw=1.4, rx=9)
        svg.text(mx, my + 4.5, label, size=12, font=FONT_SERIF, fill=col, anchor="middle", weight="bold")


def draw_state_grid(svg, gx, gy, gw, gh, a, b, max_x=12, max_y=8,
                    mode="inv_all", highlight_pts=None, trace_edges=None,
                    wrong_pts=None, show_axes_labels=True, cell_r=3.3):
    """
    Draw a miniature 2D state-space grid of (x, y) in [0..max_x] x [0..max_y].
    """
    svg.rect(gx, gy, gw, gh, fill="#ffffff", stroke=GRAY_MID, sw=1, rx=3)

    pad_l = 22 if show_axes_labels else 12
    pad_r = 16 if show_axes_labels else 12
    pad_t = 14 if show_axes_labels else 10
    pad_b = 19 if show_axes_labels else 10
    pw = gw - pad_l - pad_r
    ph = gh - pad_t - pad_b

    def pt_xy(xv, yv):
        px = gx + pad_l + (xv / max_x) * pw
        py = gy + pad_t + ph - (yv / max_y) * ph
        return px, py

    inv = inv_states(a, b, max_x, max_y)
    if mode == "entry":
        type_pts = {(a, b)}
    elif mode == "inv_all":
        type_pts = inv
    elif mode == "inv_pos":
        type_pts = {(x, y) for (x, y) in inv if y > 0}
    elif mode == "inv_zero":
        type_pts = {(x, y) for (x, y) in inv if y == 0}
    elif mode == "custom":
        type_pts = set(highlight_pts or [])
    else:
        type_pts = inv

    # Highlight y=0 line or y>0 zone lightly if relevant
    if mode == "inv_zero":
        x0, y0 = pt_xy(0, 0)
        x1, _ = pt_xy(max_x, 0)
        svg.rect(x0 - 5, y0 - 6, (x1 - x0) + 10, 12, fill=PURPLE_FILL, stroke=PURPLE, sw=0.8, rx=4, opacity=0.7)
    elif mode == "inv_pos":
        x0, y_top = pt_xy(0, max_y)
        x1, y_bot = pt_xy(max_x, 1)
        svg.rect(x0 - 4, y_top - 4, (x1 - x0) + 8, (y_bot - y_top) + 8,
                 fill=PURPLE_LIGHT, stroke=PURPLE, sw=0.7, rx=3, dash="2,2", opacity=0.7)

    # Draw all grid points
    for xv in range(max_x + 1):
        for yv in range(max_y + 1):
            px, py = pt_xy(xv, yv)
            if (xv, yv) in type_pts:
                svg.circle(px, py, cell_r + 1.8, fill=PURPLE_FILL, stroke=PURPLE, sw=1.0)
                svg.circle(px, py, cell_r - 0.8, fill=PURPLE, stroke="none")
            else:
                svg.circle(px, py, 1.3, fill=GRAY_LIGHT, stroke="none")

    # Draw wrong points if any (in RED)
    if wrong_pts:
        for (xv, yv) in wrong_pts:
            if xv <= max_x and yv <= max_y:
                px, py = pt_xy(xv, yv)
                svg.circle(px, py, cell_r + 2.5, fill=RED_FILL, stroke=RED, sw=1.6)
                svg.circle(px, py, cell_r - 0.5, fill=RED, stroke="none")

    # Draw concrete trace points / edges if provided
    if trace_edges:
        for (x1, y1), (x2, y2), col in trace_edges:
            px1, py1 = pt_xy(x1, y1)
            px2, py2 = pt_xy(x2, y2)
            mk = "arrow-navy" if col == NAVY else ("arrow-red" if col == RED else "arrow-purple")
            svg.line(px1, py1, px2, py2, stroke=col, sw=1.6, marker_end=mk)

    if highlight_pts and mode != "custom":
        for (xv, yv) in highlight_pts:
            if xv <= max_x and yv <= max_y:
                px, py = pt_xy(xv, yv)
                svg.circle(px, py, cell_r + 1.2, fill="none", stroke=NAVY, sw=1.8)

    if show_axes_labels:
        # x axis ticks
        for xv in [0, 4, 8, 12] if max_x == 12 else [0, max_x // 2, max_x]:
            if xv <= max_x:
                px, py = pt_xy(xv, 0)
                svg.text(px, gy + gh - 4, str(xv), size=10, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
        # y axis ticks
        for yv in [0, 4, 8] if max_y == 8 else [0, max_y]:
            if yv <= max_y:
                px, py = pt_xy(0, yv)
                svg.text(gx + 15, py + 3.5, str(yv), size=10, font=FONT_SANS, fill=GRAY_DARK, anchor="end")
        # Place x and y axis titles cleanly at mid-axes so they never collide with ticks
        svg.text(gx + pad_l + pw * 0.5, gy + gh - 3, "x", size=10.5, font=FONT_SERIF, fill=INK, anchor="middle", style="italic")
        svg.text(gx + 8, gy + pad_t + ph * 0.25, "y", size=10.5, font=FONT_SERIF, fill=INK, anchor="middle", style="italic")


# ==============================================================================
# FIGURE 1: The Visual Grammar of a Refinement Judgment & Target Type Gcd(12, 8)
# ==============================================================================
def generate_fig1():
    svg = SvgBuilder(900, 575)
    svg.add_standard_defs()

    svg.title_block(
        "A refinement type is a set; a typing judgment is a set-to-set pipe",
        "Visual grammar for (a = 12, b = 8): target type Gcd(12, 8), state-set ports, and subtyping docks (⊆)"
    )

    # --- LEFT PANEL: Target Type Gcd(12, 8) as Divisor-Set Equality ---
    lx, ly, lw, lh = 24, 72, 415, 480
    draw_puzzle_tile(svg, lx, ly, lw, lh,
                     "1. Target Refinement Type:  Gcd(12, 8)",
                     "Set of inhabitants", border_col=PURPLE, fill_col="#ffffff")

    svg.text(lx + 14, ly + 44,
             "Gcd(a, b)  =  { g ∈ ℕ  |  Div(g) = Div(a) ∩ Div(b) }",
             size=13.5, font=FONT_SERIF, fill=INK, weight="bold")

    # Show Div(12), Div(8), and their intersection Div(12) ∩ Div(8) = {1, 2, 4}
    div_box_y = ly + 56
    svg.rect(lx + 14, div_box_y, lw - 28, 86, fill=GRAY_BG, stroke=GRAY_MID, sw=1, rx=4)

    d12 = set(divisors(12))
    d8 = set(divisors(8))
    d_inter = d12 & d8

    rows_info = [
        ("Div(12)", d12, GRAY_DARK, "#e8e8e8"),
        ("Div(8)", d8, GRAY_DARK, "#e8e8e8"),
        ("Div(12) ∩ Div(8)", d_inter, PURPLE, PURPLE_FILL),
    ]
    for r_idx, (r_label, r_set, r_col, r_fill) in enumerate(rows_info):
        ry = div_box_y + 19 + r_idx * 26
        svg.text(lx + 24, ry + 4, r_label, size=12, font=FONT_SERIF,
                 fill=r_col, weight="bold" if r_idx == 2 else "normal")
        for n in range(1, 13):
            cx = lx + 145 + (n - 1) * 22
            if n in r_set:
                svg.circle(cx, ry, 8.5, fill=r_fill, stroke=r_col, sw=1.4 if r_idx == 2 else 1.0)
                svg.text(cx, ry + 4, str(n), size=11, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
            else:
                svg.circle(cx, ry, 2.0, fill=GRAY_LIGHT, stroke="none")

    # Candidate test table: which g ∈ {1..12} has Div(g) == {1, 2, 4}?
    svg.text(lx + 14, ly + 162,
             "Filter candidates g ∈ ℕ by testing Div(g) = {1, 2, 4}:",
             size=12.5, font=FONT_SANS, fill=INK, weight="bold")

    candidates = [
        (1, "{1}", "missing 2, 4", False),
        (2, "{1, 2}", "missing 4 (too small)", False),
        (3, "{1, 3}", "3 ∉ {1,2,4}", False),
        (4, "{1, 2, 4}", "exact match!  g = 4 ∈ Gcd(12, 8)", True),
        (6, "{1, 2, 3, 6}", "3, 6 ∉ {1,2,4}", False),
        (8, "{1, 2, 4, 8}", "extra divisor 8 (8 ∤ 12)", False),
        (12, "{1, 2, 3, 4, 6, 12}", "extra divisors 3, 6, 12", False),
    ]

    cy_start = ly + 184
    for idx, (g_val, div_str, reason, is_ok) in enumerate(candidates):
        ry = cy_start + idx * 29
        if is_ok:
            svg.rect(lx + 14, ry - 13, lw - 28, 25, fill=PURPLE_FILL, stroke=PURPLE, sw=1.8, rx=4)
            svg.circle(lx + 30, ry - 0.5, 8.5, fill=NAVY, stroke=PURPLE, sw=1.5)
            svg.text(lx + 30, ry + 3.5, str(g_val), size=11, font=FONT_SANS, fill="#ffffff", anchor="middle", weight="bold")
            svg.text(lx + 50, ry + 4, f"Div({g_val}) = {div_str}", size=12, font=FONT_SERIF, fill=INK, weight="bold")
            svg.text(lx + lw - 22, ry + 4, reason, size=11.5, font=FONT_SANS, fill=PURPLE, anchor="end", weight="bold")
        else:
            svg.rect(lx + 14, ry - 13, lw - 28, 25, fill="#fafafa", stroke=GRAY_LIGHT, sw=1, rx=3)
            svg.circle(lx + 30, ry - 0.5, 7.5, fill="#eeeeee", stroke=GRAY_MID, sw=1)
            svg.text(lx + 30, ry + 3.5, str(g_val), size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
            svg.text(lx + 50, ry + 4, f"Div({g_val}) = {div_str}", size=11.5, font=FONT_SERIF, fill=GRAY_DARK)
            svg.text(lx + lw - 22, ry + 4, reason, size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="end")

    # Singleton set visual at bottom of Left Panel (cleanly separated from mini number line)
    sy = ly + 394
    svg.rect(lx + 14, sy, lw - 28, 72, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.4, rx=5)
    svg.text(lx + 26, sy + 20, "Resulting Type Set:", size=12, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(lx + 26, sy + 40, "Gcd(12, 8) = { 4 }", size=14, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(lx + 26, sy + 58, "(singleton subset of ℕ)", size=11.5, font=FONT_SANS, fill=GRAY_DARK)

    # Mini number line 0..12 on the right half of the box
    nl_x = lx + 210
    nl_y = sy + 32
    svg.line(nl_x, nl_y, nl_x + 172, nl_y, stroke=GRAY_MID, sw=1.4)
    for n in range(0, 13, 2):
        nx = nl_x + (n / 12.0) * 172
        svg.circle(nx, nl_y, 2.3, fill=GRAY_MID)
        svg.text(nx, nl_y + 21, str(n), size=10.5, font=FONT_SANS,
                 fill=NAVY if n == 4 else GRAY_DARK, anchor="middle",
                 weight="bold" if n == 4 else "normal")
    # Highlight 4
    n4x = nl_x + (4 / 12.0) * 172
    svg.ellipse(n4x, nl_y, 9.5, 11.5, fill=PURPLE_FILL, stroke=PURPLE, sw=1.8)
    svg.circle(n4x, nl_y, 4.2, fill=NAVY)
    svg.text(n4x, nl_y - 15, "g = 4", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    # --- RIGHT PANEL: Visual Grammar of Typing Judgments & Docking ---
    rx, ry, rw, rh = 458, 72, 418, 480
    draw_puzzle_tile(svg, rx, ry, rw, rh,
                     "2. Visual Grammar: Judgments as Composable Pipes",
                     "How tiles dock", border_col=INK, fill_col="#ffffff")

    # Part A: Single Judgment Tile
    svg.text(rx + 16, ry + 44,
             "A. One Typing Judgment Tile:   ⊢  { x ∈ P }   stmt   { x' ∈ Q }",
             size=12.5, font=FONT_SANS, fill=INK, weight="bold")

    tx, ty, tw, th = rx + 20, ry + 54, rw - 40, 118
    svg.rect(tx, ty, tw, th, fill=GRAY_BG, stroke=INK, sw=1.5, rx=6)
    # Left Port (Pre-state set P)
    svg.rect(tx + 12, ty + 14, 110, 90, fill="#ffffff", stroke=PURPLE, sw=1.5, rx=4)
    svg.text(tx + 67, ty + 30, "Pre-set P", size=11.5, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")
    svg.ellipse(tx + 67, ty + 62, 36, 20, fill=PURPLE_FILL, stroke=PURPLE, sw=1.5)
    svg.circle(tx + 58, ty + 60, 3.5, fill=NAVY)
    svg.circle(tx + 75, ty + 65, 3.5, fill=NAVY)
    svg.text(tx + 67, ty + 97, "allowed inputs", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    # Center transform arrow (program step)
    svg.line(tx + 128, ty + 59, tx + 242, ty + 59, stroke=INK, sw=2.2, marker_end="arrow-ink")
    svg.rect(tx + 145, ty + 36, 82, 20, fill="#ffffff", stroke=INK, sw=1, rx=3)
    svg.text(tx + 186, ty + 50, "stmt / body", size=11.5, font=FONT_SERIF, fill=INK, anchor="middle", style="italic")
    svg.text(tx + 186, ty + 76, "maps every v ∈ P", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
    svg.text(tx + 186, ty + 90, "into post-set Q", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    # Right Port (Post-state set Q)
    svg.rect(tx + 254, ty + 14, 112, 90, fill="#ffffff", stroke=PURPLE, sw=1.5, rx=4)
    svg.text(tx + 310, ty + 30, "Post-set Q", size=11.5, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")
    svg.ellipse(tx + 310, ty + 62, 28, 17, fill=PURPLE_FILL, stroke=PURPLE, sw=1.5)
    svg.circle(tx + 305, ty + 61, 3.5, fill=NAVY)
    svg.circle(tx + 316, ty + 64, 3.5, fill=NAVY)
    svg.text(tx + 310, ty + 97, "guaranteed outputs", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    # Part B: Valid Docking (Subsumption / Set Containment Q1 ⊆ P2)
    svg.text(rx + 16, ry + 196,
             "B. Valid Composition Dock (Subtyping = Set Containment Q₁ ⊆ P₂):",
             size=12, font=FONT_SANS, fill=PURPLE, weight="bold")

    bx, by, bw, bh = rx + 20, ry + 206, rw - 40, 110
    svg.rect(bx, by, bw, bh, fill="#ffffff", stroke=PURPLE, sw=1.4, rx=6)

    # Left dock port Q1
    svg.rect(bx + 14, by + 14, 125, 82, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
    svg.text(bx + 76, by + 30, "Tile 1 Out: Q₁", size=11.5, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
    svg.ellipse(bx + 76, by + 60, 24, 16, fill=PURPLE_FILL, stroke=PURPLE, sw=1.6)
    svg.circle(bx + 70, by + 59, 3, fill=NAVY)
    svg.circle(bx + 82, by + 62, 3, fill=NAVY)

    # Connector bridge
    draw_dock_connector(svg, bx + 139, by + 55, bx + 235, by + 55, label="⊆", ok=True)
    svg.text(bx + 187, by + 84, "Q₁ fits inside P₂", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Right dock port P2 showing Q1 nested inside P2
    svg.rect(bx + 235, by + 14, 129, 82, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
    svg.text(bx + 299, by + 30, "Tile 2 In: P₂", size=11.5, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
    svg.ellipse(bx + 299, by + 60, 42, 23, fill=PURPLE_FILL, stroke=PURPLE, sw=1.5)
    svg.ellipse(bx + 295, by + 60, 22, 14, fill="none", stroke=PURPLE, sw=1.2, dash="3,2")
    svg.circle(bx + 290, by + 59, 3, fill=NAVY)
    svg.circle(bx + 301, by + 62, 3, fill=NAVY)

    # Part C: Type Error / Broken Dock (Q1 ⊈ P2)
    svg.text(rx + 16, ry + 340,
             "C. Broken Dock (Type Error = Output Leaks Outside Input Set):",
             size=12, font=FONT_SANS, fill=RED, weight="bold")

    cx, cy, cw, ch = rx + 20, ry + 350, rw - 40, 114
    svg.rect(cx, cy, cw, ch, fill=RED_FILL, stroke=RED, sw=1.5, rx=6, opacity=0.35)
    svg.rect(cx, cy, cw, ch, fill="none", stroke=RED, sw=1.5, rx=6)

    # Left dock port Q1 (too wide / shifted)
    svg.rect(cx + 14, cy + 14, 125, 86, fill="#ffffff", stroke=RED, sw=1.2, rx=4)
    svg.text(cx + 76, cy + 30, "Tile 1 Out: Q₁", size=11.5, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")
    svg.ellipse(cx + 76, cy + 62, 38, 20, fill=RED_FILL, stroke=RED, sw=1.5)
    svg.circle(cx + 62, cy + 62, 3, fill=NAVY)
    svg.circle(cx + 98, cy + 58, 4, fill=RED)

    # Broken connector bridge
    draw_dock_connector(svg, cx + 139, cy + 57, cx + 235, cy + 57, label="⊈", ok=False)
    svg.text(cx + 187, cy + 86, "TYPE ERROR!", size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")

    # Right dock port P2 showing point leaking outside
    svg.rect(cx + 235, cy + 14, 129, 86, fill="#ffffff", stroke=RED, sw=1.2, rx=4)
    svg.text(cx + 299, cy + 30, "Tile 2 In: P₂", size=11.5, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
    svg.ellipse(cx + 282, cy + 64, 25, 18, fill=PURPLE_FILL, stroke=PURPLE, sw=1.5)
    # Leaking region + offending witness dot
    svg.ellipse(cx + 302, cy + 64, 34, 18, fill="none", stroke=RED, sw=1.4, dash="3,2")
    svg.circle(cx + 324, cy + 64, 4.5, fill=RED, stroke="#ffffff", sw=1)
    svg.text(cx + 340, cy + 50, "leak!", size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")

    with open("fig-1.svg", "w") as f:
        f.write(svg.render())


# ==============================================================================
# FIGURE 2: The Inductive Heart — Loop Rule Tile for (a = 12, b = 8)
# ==============================================================================
def generate_fig2():
    svg = SvgBuilder(900, 610)
    svg.add_standard_defs()

    svg.title_block(
        "Loop rule tile: body preserves Inv while measure y strictly drops",
        "Inside the [WHILE] judgment for (a = 12, b = 8): why (x, y) ← (y, x mod y) closes the invariant cycle"
    )

    # Outer Loop Rule Container
    ox, oy, ow, oh = 24, 70, 852, 520
    draw_puzzle_tile(svg, ox, oy, ow, oh,
                     "Rule [WHILE-INV]   for   while (y ≠ 0) { (x, y) ← (y, x mod y) }   on input (a = 12, b = 8)",
                     "Loop Invariant:  Inv(x, y)  ≡  Div(x) ∩ Div(y) = Div(12) ∩ Div(8) = {1, 2, 4}",
                     border_col=PURPLE, fill_col="#ffffff")

    # --- TOP ROW: 3 panels showing (1) Pre-set Inv ∧ y≠0, (2) Body map & Measure y, (3) Post-set Inv ---
    p1x, p1y, pw, ph = 42, 108, 248, 224
    p2x = 326
    p3x = 610

    # Panel 1: Loop Body Pre-set: Inv ∧ (y ≠ 0)
    svg.rect(p1x, p1y, pw, ph, fill=GRAY_BG, stroke=PURPLE, sw=1.5, rx=5)
    svg.text(p1x + 10, p1y + 19, "Body Input Port:  Inv ∧ (y ≠ 0)", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(p1x + 10, p1y + 35, "Active states with gcd(x,y) = 4, y > 0", size=11, font=FONT_SANS, fill=GRAY_DARK)
    draw_state_grid(svg, p1x + 12, p1y + 43, pw - 24, 150, 12, 8, max_x=12, max_y=8,
                    mode="inv_pos", highlight_pts=[(12, 8), (8, 4)])
    svg.text(p1x + pw/2, p1y + 211, "y = 0 row excluded by guard y ≠ 0", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle")

    # Arrow from Panel 1 to Panel 2
    svg.line(p1x + pw, p1y + 115, p2x, p1y + 115, stroke=PURPLE, sw=2.2, marker_end="arrow-purple")

    # Panel 2: Body Transformation + Termination Measure y
    svg.rect(p2x, p1y, pw, ph, fill="#ffffff", stroke=INK, sw=1.6, rx=5)
    svg.text(p2x + 10, p1y + 19, "Body Step & Measure:  y' < y", size=12.5, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(p2x + 10, p1y + 35, "(x', y') = (y, x mod y) preserves divisors", size=11, font=FONT_SANS, fill=GRAY_DARK)

    # Draw preservation algebra badge
    svg.rect(p2x + 12, p1y + 44, pw - 24, 48, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=4)
    svg.text(p2x + pw/2, p1y + 62, "d ∣ x ∧ d ∣ y  ⟺  d ∣ y ∧ d ∣ (x mod y)",
             size=11.5, font=FONT_SERIF, fill=INK, anchor="middle", weight="bold")
    svg.text(p2x + pw/2, p1y + 81, "∴  Div(x') ∩ Div(y') = Div(x) ∩ Div(y) = {1,2,4}",
             size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Well-founded measure staircase inside Panel 2
    svg.rect(p2x + 12, p1y + 100, pw - 24, 114, fill=GRAY_BG, stroke=GRAY_MID, sw=1, rx=4)
    svg.text(p2x + 20, p1y + 116, "Measure  y ∈ ℕ  strictly decreases:", size=11, font=FONT_SANS, fill=INK, weight="bold")
    steps = [
        ("(12, 8)", 8, 0),
        ("(8, 4)", 4, 1),
        ("(4, 0)", 0, 2),
    ]
    for s_label, y_val, idx in steps:
        bx = p2x + 26 + idx * 72
        by_bot = p1y + 192
        bh_bar = (y_val / 8.0) * 50
        if bh_bar > 0:
            svg.rect(bx, by_bot - bh_bar, 36, bh_bar, fill=PURPLE_FILL, stroke=PURPLE, sw=1.4, rx=2)
        else:
            svg.line(bx, by_bot, bx + 36, by_bot, stroke=NAVY, sw=2.5)
        svg.text(bx + 18, by_bot - bh_bar - 5, f"y={y_val}", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
        svg.text(bx + 18, by_bot + 14, s_label, size=10.5, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
        if idx < 2:
            svg.line(bx + 40, by_bot - 22, bx + 68, by_bot - 10, stroke=NAVY, sw=1.5, marker_end="arrow-navy")

    # Arrow from Panel 2 to Panel 3
    svg.line(p2x + pw, p1y + 115, p3x, p1y + 115, stroke=PURPLE, sw=2.2, marker_end="arrow-purple")

    # Panel 3: Body Post-set: Inv (full invariant including y=0)
    svg.rect(p3x, p1y, pw, ph, fill=GRAY_BG, stroke=PURPLE, sw=1.5, rx=5)
    svg.text(p3x + 10, p1y + 19, "Body Output Port:  Inv", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(p3x + 10, p1y + 35, "Lands inside Inv (including y = 0 exit)", size=11, font=FONT_SANS, fill=GRAY_DARK)
    edges_12_8 = [
        ((12, 8), (8, 4), NAVY),
        ((8, 4), (4, 0), NAVY),
    ]
    draw_state_grid(svg, p3x + 12, p1y + 43, pw - 24, 150, 12, 8, max_x=12, max_y=8,
                    mode="inv_all", highlight_pts=[(12, 8), (8, 4), (4, 0)], trace_edges=edges_12_8)
    svg.text(p3x + pw/2, p1y + 211, "Every mapped state stays in purple Inv set", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle")

    # --- ROUTING CHANNEL (y = 332..382) between top row and bottom container ---
    # Bottom container starts at y = 382
    bot_y = 382
    svg.rect(42, bot_y, 816, 192, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.2, rx=6)
    svg.text(56, bot_y + 21, "How the Loop Rule Closes & Splits on Guard y:", size=13, font=FONT_SERIF, fill=INK, weight="bold")

    # 1. Left Box: Loop Invariant Set Inv
    svg.rect(58, bot_y + 34, 190, 144, fill="#ffffff", stroke=PURPLE, sw=1.4, rx=5)
    svg.text(153, bot_y + 52, "Loop Invariant Set Inv", size=12, font=FONT_SERIF, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(153, bot_y + 68, "7 states in [0..12] × [0..8]:", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
    svg.text(153, bot_y + 86, "y > 0 : (0,4), (4,4), (8,4), (12,4),", size=11, font=FONT_SANS, fill=INK, anchor="middle")
    svg.text(153, bot_y + 102, "(4,8), (12,8)  → 6 states", size=11, font=FONT_SANS, fill=INK, anchor="middle")
    svg.line(70, bot_y + 112, 236, bot_y + 112, stroke=GRAY_LIGHT, sw=1)
    svg.text(153, bot_y + 130, "y = 0 : (4, 0) ONLY!", size=12, font=FONT_SERIF, fill=NAVY, anchor="middle", weight="bold")
    svg.text(153, bot_y + 148, "Div(x)∩ℕ = Div(x) = {1,2,4}", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
    svg.text(153, bot_y + 163, "forces unique x = 4", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    # Guard diamond / splitter positioned at x = 345
    gx, gy = 345, bot_y + 106
    svg.path(f"M {gx} {gy-34} L {gx+54} {gy} L {gx} {gy+34} L {gx-54} {gy} Z",
             fill="#ffffff", stroke=INK, sw=1.8)
    svg.text(gx, gy - 3, "Guard", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
    svg.text(gx, gy + 11, "y = 0 ?", size=12, font=FONT_SERIF, fill=INK, anchor="middle", weight="bold")

    svg.line(248, gy, gx - 54, gy, stroke=PURPLE, sw=2.2, marker_end="arrow-purple")

    # Branch 1 (UP): y != 0 feeds back into Panel 1 (Body Input Port)
    # Routed cleanly to the right of the header text, then across the channel at y=354
    svg.path(f"M {gx} {gy-34} L {gx} 354 L 166 354 L 166 {p1y+ph}",
             fill="none", stroke=PURPLE, sw=2.2, marker_end="arrow-purple")
    svg.rect(205, 344, 102, 20, fill=PURPLE_FILL, stroke=PURPLE, sw=1.2, rx=8)
    svg.text(256, 358, "y ≠ 0 : repeat", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Feedback from Panel 3 (Body Output Inv) into Loop Invariant box
    svg.path(f"M {p3x + pw/2} {p1y + ph} L {p3x + pw/2} 354 L 435 354 L 435 {bot_y + 62} L 248 {bot_y + 62}",
             fill="none", stroke=PURPLE, sw=2.0, dash="5,3", marker_end="arrow-purple")
    svg.rect(495, 344, 185, 20, fill=PURPLE_FILL, stroke=PURPLE, sw=1.2, rx=8)
    svg.text(587.5, 358, "Body Post ⊆ Inv (inductive dock)", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Branch 2 (RIGHT): y == 0 exits loop with Inv ∧ (y = 0)
    svg.line(gx + 54, gy, 476, gy, stroke=PURPLE, sw=2.5, marker_end="arrow-purple")
    svg.rect(403, gy - 25, 66, 19, fill=PURPLE_FILL, stroke=PURPLE, sw=1, rx=6)
    svg.text(436, gy - 12, "y = 0 : exit", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Exit Port Box: Inv ∧ (y = 0)  ==  {(4, 0)}
    ex, ey, ew, eh = 476, bot_y + 34, 366, 144
    svg.rect(ex, ey, ew, eh, fill="#ffffff", stroke=PURPLE, sw=1.8, rx=5)
    svg.text(ex + 14, ey + 20, "Loop Exit Port:   Inv(x, y) ∧ (y = 0)", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(ex + 14, ey + 38, "Because Div(0) = ℕ,  Div(x) ∩ Div(0) = Div(x):", size=11.5, font=FONT_SANS, fill=INK)
    svg.rect(ex + 14, ey + 46, ew - 28, 34, fill=PURPLE_FILL, stroke=PURPLE, sw=1.2, rx=4)
    svg.text(ex + ew/2, ey + 68, "Inv(x, 0)   ⟺   Div(x) = Div(12) ∩ Div(8)   ⟺   x ∈ Gcd(12, 8)",
             size=11.8, font=FONT_SERIF, fill=INK, anchor="middle", weight="bold")

    svg.text(ex + 14, ey + 102, "Concrete run on (12, 8):", size=11.5, font=FONT_SANS, fill=NAVY, weight="bold")
    svg.text(ex + 14, ey + 122, "(12, 8)  →  (8, 4)  →  (4, 0)   ⇒   exits at unique point x = 4",
             size=12, font=FONT_SERIF, fill=NAVY, weight="bold")

    with open("fig-2.svg", "w") as f:
        f.write(svg.render())


# ==============================================================================
# FIGURE 3: Full Composed Typing Derivation Chain for (a = 12, b = 8)
# ==============================================================================
def generate_fig3():
    svg = SvgBuilder(900, 600)
    svg.add_standard_defs()

    svg.title_block(
        "Complete typing derivation: four docked tiles prove result : Gcd(12, 8)",
        "End-to-end proof pipeline from input (a = 12, b = 8) through loop invariant to return x = 4"
    )

    # Top program banner showing the 4 stages aligned with the 4 tiles below
    svg.rect(24, 66, 852, 34, fill=GRAY_BG, stroke=GRAY_MID, sw=1, rx=5)
    svg.text(38, 88, "Euclid(12, 8):", size=13, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(145, 88, "① (x, y) ← (12, 8)", size=12.5, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(310, 88, ";   ② while (y ≠ 0) { (x, y) ← (y, x mod y) }", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(605, 88, ";   ③ assert y = 0", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(745, 88, ";   ④ return x", size=12.5, font=FONT_SERIF, fill=NAVY, weight="bold")

    # Four horizontal tiles connected by 3 docking bridges
    # Leave 36px between top banner (y=100) and tiles (ty=136) for the self-loop arc on Tile 2!
    ty = 136
    th = 320

    # --- TILE 1: [INIT] Entry ---
    t1x, t1w = 24, 178
    draw_puzzle_tile(svg, t1x, ty, t1w, th, "Tile 1: Entry", "[INIT]", border_col=INK)
    svg.text(t1x + 10, ty + 42, "Stmt: (x,y) := (12,8)", size=11.5, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(t1x + 10, ty + 58, "Post-set E = {(12, 8)}", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")
    draw_state_grid(svg, t1x + 10, ty + 68, t1w - 20, 145, 12, 8, max_x=12, max_y=8,
                    mode="entry", highlight_pts=[(12, 8)])
    svg.rect(t1x + 10, ty + 224, t1w - 20, 84, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=4)
    svg.text(t1x + 16, ty + 242, "Check E ⊆ Inv:", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(t1x + 16, ty + 260, "Div(12)∩Div(8)", size=11, font=FONT_SERIF, fill=INK)
    svg.text(t1x + 16, ty + 276, "= {1, 2, 4} ✓", size=11.5, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(t1x + 16, ty + 296, "(12, 8) ∈ Inv", size=11.5, font=FONT_SERIF, fill=PURPLE, weight="bold")

    # --- DOCK 1: Entry ⊆ Inv ---
    draw_dock_connector(svg, t1x + t1w, ty + 140, 242, ty + 140, label="⊆", ok=True)
    svg.text(222, ty + 118, "Dock 1", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(222, ty + 172, "E ⊆ Inv", size=11, font=FONT_SERIF, fill=PURPLE, anchor="middle")

    # --- TILE 2: [WHILE] Loop Invariant ---
    t2x, t2w = 242, 196
    draw_puzzle_tile(svg, t2x, ty, t2w, th, "Tile 2: Loop", "[WHILE]", border_col=PURPLE)
    svg.text(t2x + 10, ty + 42, "Pre/Post: Inv(x, y)", size=11.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(t2x + 10, ty + 58, "Div(x)∩Div(y) = {1,2,4}", size=11, font=FONT_SANS, fill=GRAY_DARK)
    edges = [((12, 8), (8, 4), NAVY), ((8, 4), (4, 0), NAVY)]
    draw_state_grid(svg, t2x + 10, ty + 68, t2w - 20, 145, 12, 8, max_x=12, max_y=8,
                    mode="inv_all", highlight_pts=[(12, 8), (8, 4), (4, 0)], trace_edges=edges)
    # Self-loop badge above Tile 2 (in the 100..136 gap)
    svg.path(f"M {t2x + 50} {ty} C {t2x + 50} {ty - 19}, {t2x + 146} {ty - 19}, {t2x + 146} {ty}",
             fill="none", stroke=PURPLE, sw=1.8, marker_end="arrow-purple")
    svg.text(t2x + 98, ty - 18, "body preserves Inv, y↓", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    svg.rect(t2x + 10, ty + 224, t2w - 20, 84, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=4)
    svg.text(t2x + 16, ty + 242, "Invariant preserved:", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(t2x + 16, ty + 260, "(12,8) → (8,4) → (4,0)", size=11, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(t2x + 16, ty + 278, "Measure y: 8 > 4 > 0", size=11, font=FONT_SANS, fill=INK)
    svg.text(t2x + 16, ty + 296, "Exits when y = 0", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")

    # --- DOCK 2: Loop Exit = Inv ∧ (y=0) ---
    draw_dock_connector(svg, t2x + t2w, ty + 140, 478, ty + 140, label="⊆", ok=True)
    svg.text(458, ty + 118, "Dock 2", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(458, ty + 172, "¬(y≠0)", size=11, font=FONT_SERIF, fill=PURPLE, anchor="middle")

    # --- TILE 3: [EXIT] Post-Loop Slice Inv ∧ (y = 0) ---
    t3x, t3w = 478, 196
    draw_puzzle_tile(svg, t3x, ty, t3w, th, "Tile 3: Exit Slice", "[SUB]", border_col=PURPLE)
    svg.text(t3x + 10, ty + 42, "Set: Inv(x, y) ∧ (y = 0)", size=11.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(t3x + 10, ty + 58, "Intersect Inv with row y = 0", size=11, font=FONT_SANS, fill=GRAY_DARK)
    draw_state_grid(svg, t3x + 10, ty + 68, t3w - 20, 145, 12, 8, max_x=12, max_y=8,
                    mode="inv_zero", highlight_pts=[(4, 0)])
    svg.rect(t3x + 10, ty + 224, t3w - 20, 84, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=4)
    svg.text(t3x + 16, ty + 242, "Why y = 0 collapses Inv:", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(t3x + 16, ty + 260, "Div(x) ∩ Div(0) = Div(x)", size=11, font=FONT_SERIF, fill=INK)
    svg.text(t3x + 16, ty + 278, "⇒ Div(x) = {1, 2, 4}", size=11, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(t3x + 16, ty + 296, "Unique state: (4, 0)", size=11.5, font=FONT_SERIF, fill=NAVY, weight="bold")

    # --- DOCK 3: Project x : Gcd(12, 8) ---
    draw_dock_connector(svg, t3x + t3w, ty + 140, 714, ty + 140, label="⊆", ok=True)
    svg.text(694, ty + 118, "Dock 3", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(694, ty + 172, "proj x", size=11, font=FONT_SERIF, fill=PURPLE, anchor="middle")

    # --- TILE 4: [RETURN] Output Type Gcd(12, 8) ---
    t4x, t4w = 714, 162
    draw_puzzle_tile(svg, t4x, ty, t4w, th, "Tile 4: Return", "[RET]", border_col=PURPLE)
    svg.text(t4x + 10, ty + 42, "Type: Gcd(12, 8)", size=11.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(t4x + 10, ty + 58, "{g | Div(g)={1,2,4}}", size=11, font=FONT_SANS, fill=GRAY_DARK)

    nl_box_x, nl_box_y, nl_box_w, nl_box_h = t4x + 10, ty + 68, t4w - 20, 145
    svg.rect(nl_box_x, nl_box_y, nl_box_w, nl_box_h, fill="#ffffff", stroke=GRAY_MID, sw=1, rx=3)
    svg.text(nl_box_x + nl_box_w/2, nl_box_y + 15, "Output g ∈ ℕ", size=11, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")

    for g_cand in range(1, 13):
        col_i = (g_cand - 1) % 4
        row_i = (g_cand - 1) // 4
        cx = nl_box_x + 24 + col_i * 31
        cy = nl_box_y + 44 + row_i * 35
        if g_cand == 4:
            svg.circle(cx, cy, 11.5, fill=PURPLE_FILL, stroke=PURPLE, sw=2.0)
            svg.circle(cx, cy, 4.5, fill=NAVY)
            svg.text(cx, cy - 14, "g=4", size=10.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
        else:
            svg.circle(cx, cy, 8, fill="#f3f3f3", stroke=GRAY_LIGHT, sw=1)
            svg.text(cx, cy + 3.5, str(g_cand), size=10, font=FONT_SANS, fill=GRAY_MID, anchor="middle")

    svg.rect(t4x + 10, ty + 224, t4w - 20, 84, fill=PURPLE_FILL, stroke=PURPLE, sw=1.5, rx=4)
    svg.text(t4x + t4w/2, ty + 245, "Q.E.D.", size=12, font=FONT_SERIF, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(t4x + t4w/2, ty + 265, "x = 4 ∈ Gcd(12, 8)", size=12, font=FONT_SERIF, fill=NAVY, anchor="middle", weight="bold")
    svg.text(t4x + t4w/2, ty + 285, "Evidence erased", size=11, font=FONT_SANS, fill=INK, anchor="middle")
    svg.text(t4x + t4w/2, ty + 300, "at run time → 4", size=11, font=FONT_SANS, fill=INK, anchor="middle")

    # --- BOTTOM SUMMARY BAR: Sequent / Proof Tree Conclusion ---
    by = 472
    svg.rect(24, by, 852, 104, fill="#ffffff", stroke=PURPLE, sw=1.8, rx=6)
    svg.text(40, by + 23,
             "Composed Derivation Rule (All 3 Docks Lock):",
             size=13, font=FONT_SANS, fill=PURPLE, weight="bold")

    # Inference rule line (fit cleanly within 852px box)
    svg.text(425, by + 48,
             "① (12,8) ∈ Inv       ② {Inv ∧ y≠0} body {Inv}  (y↓)       ③ Inv ∧ (y=0)  ⊆  { (x, 0) | x ∈ Gcd(12,8) }",
             size=12.2, font=FONT_SERIF, fill=INK, anchor="middle")
    svg.line(65, by + 58, 780, by + 58, stroke=INK, sw=1.6)
    svg.text(790, by + 62, "[EUCLID-GCD]", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(425, by + 84,
             "⊢   Euclid(12, 8)  :  Gcd(12, 8)   =   { g ∈ ℕ  |  Div(g) = Div(12) ∩ Div(8) }   =   { 4 }",
             size=13.5, font=FONT_SERIF, fill=NAVY, anchor="middle", weight="bold")

    with open("fig-3.svg", "w") as f:
        f.write(svg.render())


# ==============================================================================
# FIGURE 4: Dependent Type Indexing Across Input Pairs: (13, 8), (21, 0), (0, 0)
# ==============================================================================
def generate_fig4():
    svg = SvgBuilder(900, 620)
    svg.add_standard_defs()

    svg.title_block(
        "Same derivation template adapts to coprime (13, 8) and zero edge cases",
        "Dependent type Gcd(a, b) is a family of sets indexed by (a, b); the proof skeleton stays identical"
    )

    # Explain dependent indexing at top
    svg.rect(24, 66, 852, 36, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.2, rx=5)
    svg.text(40, 89,
             "Dependent Type Family:   (a, b : ℕ)  ↦  Inv(a,b) = {(x,y) | Div(x)∩Div(y) = Div(a)∩Div(b)}   ──►   Gcd(a,b) = {g | Div(g) = Div(a)∩Div(b)}",
             size=12.5, font=FONT_SERIF, fill=INK, weight="bold")

    cases = [
        {
            "title": "Case A: Coprime Inputs  (a = 13, b = 8)   →   gcd = 1   (5 loop iterations: Fibonacci worst-case)",
            "a": 13, "b": 8, "g": 1,
            "div_line1": "Div(13) ∩ Div(8) = {1, 13} ∩ {1, 2, 4, 8}",
            "div_line2": "= { 1 }   (coprime: only 1 divides both)",
            "trace_str": "(13,8)→(8,5)→(5,3)→(3,2)→(2,1)→(1,0)",
            "loop_line1": "Dense Inv (coprime pairs);",
            "loop_line2": "5 Fibonacci steps",
            "exit_note": "Inv ∧ (y=0) = {(1, 0)}",
            "ret_note": "Gcd(13, 8) = { 1 }",
            "max_x": 13, "max_y": 8,
        },
        {
            "title": "Case B: Zero Input Edge Case  (a = 21, b = 0)   →   gcd = 21   (0 loop steps: immediate exit)",
            "a": 21, "b": 0, "g": 21,
            "div_line1": "Since Div(0) = ℕ:  Div(21) ∩ Div(0)",
            "div_line2": "= Div(21) ∩ ℕ = {1, 3, 7, 21}",
            "trace_str": "(21, 0)   [y = 0 at entry → 0 body steps]",
            "loop_line1": "0 iterations! Guard y ≠ 0 is",
            "loop_line2": "false immediately at entry",
            "exit_note": "Inv ∧ (y=0) = {(21, 0)}",
            "ret_note": "Gcd(21, 0) = { 21 }",
            "max_x": 21, "max_y": 7,
        },
        {
            "title": "Case C: Double-Zero Singularity  (a = 0, b = 0)   →   gcd = 0   (only number divisible by all of ℕ)",
            "a": 0, "b": 0, "g": 0,
            "div_line1": "Div(0) ∩ Div(0) = ℕ ∩ ℕ = ℕ",
            "div_line2": "(every d ∈ ℕ divides 0 since 0 = 0·d)",
            "trace_str": "(0, 0)   [0 steps; only g=0 has Div(g)=ℕ]",
            "loop_line1": "Inv = {(0, 0)} is a singleton",
            "loop_line2": "set throughout!",
            "exit_note": "Inv ∧ (y=0) = {(0, 0)}",
            "ret_note": "Gcd(0, 0) = { 0 }",
            "max_x": 8, "max_y": 6,
        }
    ]

    for idx, c in enumerate(cases):
        ry = 114 + idx * 164
        rh = 152
        svg.rect(24, ry, 852, rh, fill="#ffffff", stroke=INK, sw=1.4, rx=6)
        svg.rect(24, ry, 852, 24, fill=GRAY_BG, stroke=INK, sw=1.0, rx=6)
        svg.rect(25, ry + 18, 850, 6, fill=GRAY_BG, stroke="none")
        svg.line(24, ry + 24, 876, ry + 24, stroke=INK, sw=1.0)
        svg.text(36, ry + 16.5, c["title"], size=12.5, font=FONT_SERIF, fill=INK, weight="bold")

        # Box 1: Divisor Intersection & Entry (x=36..264)
        b1x, by_box, b1w, bh_box = 36, ry + 32, 228, 112
        svg.rect(b1x, by_box, b1w, bh_box, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
        svg.text(b1x + 8, by_box + 16, f"1. Entry ({c['a']}, {c['b']}) ∈ Inv", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")
        svg.text(b1x + 8, by_box + 34, c["div_line1"], size=11, font=FONT_SERIF, fill=INK)
        svg.text(b1x + 8, by_box + 49, c["div_line2"], size=11, font=FONT_SERIF, fill=INK)
        svg.rect(b1x + 8, by_box + 58, b1w - 16, 46, fill="#ffffff", stroke=GRAY_MID, sw=0.8, rx=3)
        svg.text(b1x + 12, by_box + 73, "Run trace:", size=10.5, font=FONT_SANS, fill=GRAY_DARK, weight="bold")
        svg.text(b1x + 12, by_box + 91, c["trace_str"], size=10.8, font=FONT_SERIF, fill=NAVY, weight="bold")

        # Dock 1 -> 2
        draw_dock_connector(svg, b1x + b1w, by_box + 56, 300, by_box + 56, label="⊆", ok=True)

        # Box 2: Invariant Grid & Trajectory (x=300..604)
        b2x, b2w = 300, 304
        svg.rect(b2x, by_box, b2w, bh_box, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
        svg.text(b2x + 10, by_box + 16, f"2. Loop Invariant Set  Inv({c['a']}, {c['b']})", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")

        tr = euclid_trace(c["a"], c["b"])
        tr_edges = [(tr[i], tr[i+1], NAVY) for i in range(len(tr)-1)]
        draw_state_grid(svg, b2x + 10, by_box + 22, 134, 84, c["a"], c["b"],
                        max_x=c["max_x"], max_y=c["max_y"],
                        mode="inv_all", highlight_pts=tr, trace_edges=tr_edges,
                        show_axes_labels=False, cell_r=2.3)
        svg.text(b2x + 152, by_box + 40, c["loop_line1"], size=11, font=FONT_SANS, fill=INK, weight="bold")
        svg.text(b2x + 152, by_box + 55, c["loop_line2"], size=11, font=FONT_SANS, fill=INK, weight="bold")
        svg.text(b2x + 152, by_box + 78, "Exit slice y = 0:", size=11, font=FONT_SANS, fill=GRAY_DARK)
        svg.text(b2x + 152, by_box + 95, c["exit_note"], size=11.5, font=FONT_SERIF, fill=PURPLE, weight="bold")

        # Dock 2 -> 3
        draw_dock_connector(svg, b2x + b2w, by_box + 56, 640, by_box + 56, label="⊆", ok=True)

        # Box 3: Return Type Set Gcd(a, b) (x=640..864)
        b3x, b3w = 640, 224
        svg.rect(b3x, by_box, b3w, bh_box, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.5, rx=4)
        svg.text(b3x + 10, by_box + 18, f"3. Return Type  Gcd({c['a']}, {c['b']})", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")
        svg.rect(b3x + 12, by_box + 28, b3w - 24, 44, fill=PURPLE_FILL, stroke=PURPLE, sw=1.4, rx=4)
        svg.circle(b3x + 36, by_box + 50, 13, fill=NAVY, stroke=PURPLE, sw=1.5)
        svg.text(b3x + 36, by_box + 54, str(c["g"]), size=12, font=FONT_SANS, fill="#ffffff", anchor="middle", weight="bold")
        svg.text(b3x + 58, by_box + 47, c["ret_note"], size=12.5, font=FONT_SERIF, fill=INK, weight="bold")
        svg.text(b3x + 58, by_box + 64, f"unique inhabitant g = {c['g']}", size=11, font=FONT_SANS, fill=PURPLE)
        svg.text(b3x + 12, by_box + 94, f"Div({c['g']}) = Div({c['a']}) ∩ Div({c['b']}) ✓", size=11.5, font=FONT_SERIF, fill=NAVY, weight="bold")

    with open("fig-4.svg", "w") as f:
        f.write(svg.render())


# ==============================================================================
# FIGURE 5: Type Errors as Broken Docks (Failing Compositions in Dark Red)
# ==============================================================================
def generate_fig5():
    svg = SvgBuilder(900, 620)
    svg.add_standard_defs()

    svg.title_block(
        "Type error: a buggy program or wrong candidate breaks a composition dock",
        "Each bug localizes to one dark-red dock (⊈) with an explicit counterexample witness for (a = 12, b = 8)"
    )

    # --- PANEL 1: Bug 1 — Premature Loop Exit `while (y > 4)` returns x = 8 (too large: 8 ∤ 12) ---
    ry1, rh = 70, 170
    draw_puzzle_tile(svg, 24, ry1, 852, rh,
                     "Bug 1 (Wrong Candidate g = 8):   Premature Loop Exit   while (y > 4)   →   Returns x = 8 on (12, 8)",
                     "TYPE ERROR AT DOCK 2 (EXIT ⊈ TARGET)", border_col=RED, fill_col="#ffffff")

    # Tile 1: Entry OK
    svg.rect(38, ry1 + 34, 175, 124, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
    svg.text(48, ry1 + 52, "Tile 1: Entry [OK]", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(48, ry1 + 70, "(x, y) = (12, 8) ∈ Inv", size=11.5, font=FONT_SERIF, fill=INK)
    svg.text(48, ry1 + 90, "Div(12)∩Div(8) = {1,2,4}", size=11, font=FONT_SANS, fill=GRAY_DARK)
    svg.text(48, ry1 + 112, "Entry dock holds ✓", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")

    draw_dock_connector(svg, 213, ry1 + 96, 255, ry1 + 96, label="⊆", ok=True)

    # Tile 2: Loop with weak guard `while (y > 4)`
    svg.rect(255, ry1 + 34, 245, 124, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
    svg.text(265, ry1 + 52, "Tile 2: Loop  while (y > 4)", size=11.5, font=FONT_SANS, fill=INK, weight="bold")
    svg.text(265, ry1 + 70, "Run: (12, 8) → (8, 4) → STOPS!", size=11.5, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(265, ry1 + 88, "Exit state set is Inv ∧ (y ≤ 4)", size=11, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(265, ry1 + 106, "Contains witness (x = 8, y = 4)", size=11, font=FONT_SERIF, fill=RED, weight="bold")
    svg.text(265, ry1 + 124, "where y ≠ 0 so Div(x) ≠ Div(x)∩Div(y)", size=11, font=FONT_SANS, fill=GRAY_DARK)

    # BROKEN DOCK 2!
    draw_dock_connector(svg, 500, ry1 + 96, 556, ry1 + 96, label="⊈", ok=False)
    svg.text(528, ry1 + 72, "BROKEN!", size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")

    # Tile 3: Target Gcd(12, 8) rejects x = 8
    svg.rect(556, ry1 + 34, 306, 124, fill=RED_FILL, stroke=RED, sw=1.6, rx=4)
    svg.text(568, ry1 + 52, "Target Port:  x ∈ Gcd(12, 8) = {4}", size=12, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(568, ry1 + 72, "Counterexample witness:  x = 8", size=12, font=FONT_SERIF, fill=RED, weight="bold")
    svg.rect(568, ry1 + 80, 282, 46, fill="#ffffff", stroke=RED, sw=1.2, rx=3)
    svg.text(578, ry1 + 98, "Div(8) = {1, 2, 4, 8}  ≠  {1, 2, 4}", size=11.5, font=FONT_SERIF, fill=RED, weight="bold")
    svg.text(578, ry1 + 116, "Offending divisor: 8 ∣ 8  but  8 ∤ 12 !", size=11, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(568, ry1 + 144, "Set leak: {x | Inv(x,y) ∧ y≤4} = {0, 4, 8, 12} ⊈ {4}", size=11, font=FONT_SANS, fill=RED, weight="bold")

    # --- PANEL 2: Bug 2 — Wrong Candidate g = 2 (Body breaks Invariant: `(x, y) ← (y div 2, x mod y)`) ---
    ry2 = 254
    draw_puzzle_tile(svg, 24, ry2, 852, rh,
                     "Bug 2 (Wrong Candidate g = 2):   Corrupt Body   (x, y) ← (y div 2, x mod y)   →   Returns x = 2 on (12, 8)",
                     "TYPE ERROR AT BODY DOCK (BODY POST ⊈ INV)", border_col=RED, fill_col="#ffffff")

    # Pre-port Inv ∧ y≠0
    svg.rect(38, ry2 + 34, 212, 124, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
    svg.text(48, ry2 + 52, "Body Pre-Port: Inv ∧ (y ≠ 0)", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(48, ry2 + 72, "Input state: (x = 8, y = 4) ∈ Inv", size=11.5, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(48, ry2 + 92, "Common divisors before step:", size=11, font=FONT_SANS, fill=GRAY_DARK)
    svg.text(48, ry2 + 110, "Div(8) ∩ Div(4) = {1, 2, 4} ✓", size=11.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(48, ry2 + 134, "Buggy step maps (8, 4) ↦ (2, 0)", size=11, font=FONT_SANS, fill=RED, weight="bold")

    # BROKEN INDUCTIVE DOCK!
    draw_dock_connector(svg, 250, ry2 + 96, 306, ry2 + 96, label="⊈", ok=False)
    svg.text(278, ry2 + 72, "BROKEN!", size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")

    # Body Post-port showing (2, 0) outside Inv
    svg.rect(306, ry2 + 34, 250, 124, fill=RED_FILL, stroke=RED, sw=1.6, rx=4)
    svg.text(316, ry2 + 52, "Body Post-Port Leaks Out of Inv!", size=11.5, font=FONT_SANS, fill=RED, weight="bold")
    draw_state_grid(svg, 316, ry2 + 60, 130, 90, 12, 8, max_x=12, max_y=8,
                    mode="inv_all", highlight_pts=[(12, 8), (8, 4)],
                    wrong_pts=[(2, 0)],
                    trace_edges=[((12, 8), (8, 4), NAVY), ((8, 4), (2, 0), RED)],
                    show_axes_labels=False, cell_r=2.5)
    svg.text(454, ry2 + 80, "Witness:", size=11, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(454, ry2 + 98, "(2, 0) ∉ Inv", size=12, font=FONT_SERIF, fill=RED, weight="bold")
    svg.text(454, ry2 + 118, "Div(2)∩Div(0)", size=11, font=FONT_SERIF, fill=INK)
    svg.text(454, ry2 + 134, "= {1, 2} ≠ {1,2,4}", size=11, font=FONT_SERIF, fill=RED, weight="bold")

    # Consequence box on right
    svg.rect(570, ry2 + 34, 292, 124, fill="#ffffff", stroke=RED, sw=1.4, rx=4)
    svg.text(582, ry2 + 52, "Why g = 2 Fails Gcd(12, 8):", size=12, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(582, ry2 + 72, "2 divides 12 and 2 divides 8, BUT:", size=11.5, font=FONT_SANS, fill=INK)
    svg.rect(582, ry2 + 80, 268, 46, fill=RED_FILL, stroke=RED, sw=1.0, rx=3)
    svg.text(592, ry2 + 98, "Div(2) = {1, 2}  ⊊  Div(12) ∩ Div(8) = {1, 2, 4}", size=11.5, font=FONT_SERIF, fill=RED, weight="bold")
    svg.text(592, ry2 + 116, "Missing common divisor:  4 ∣ 12 ∧ 4 ∣ 8,  4 ∤ 2", size=11, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(582, ry2 + 144, "2 is a common divisor, NOT greatest!", size=11, font=FONT_SANS, fill=RED, weight="bold")

    # --- PANEL 3: Bug 3 — Wrong Return Expression `return y` instead of `return x` (returns 0 on (12, 8)) ---
    ry3 = 438
    draw_puzzle_tile(svg, 24, ry3, 852, rh,
                     "Bug 3 (Wrong Return Variable):   return y   instead of   return x   →   Returns 0 on (12, 8)",
                     "TYPE ERROR AT DOCK 3 (RETURN PROJECTION ⊈ TARGET)", border_col=RED, fill_col="#ffffff")

    # Exit Slice Port OK: {(4, 0)}
    svg.rect(38, ry3 + 34, 240, 124, fill=GRAY_BG, stroke=PURPLE, sw=1.2, rx=4)
    svg.text(48, ry3 + 52, "Tile 3: Loop Exit Slice [OK]", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(48, ry3 + 72, "State at loop exit: (x = 4, y = 0)", size=11.5, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(48, ry3 + 92, "Inv(4, 0) ∧ (y = 0) holds ✓", size=11, font=FONT_SANS, fill=PURPLE, weight="bold")
    svg.text(48, ry3 + 114, "x-coordinate has Div(4) = {1,2,4}", size=11, font=FONT_SANS, fill=INK)
    svg.text(48, ry3 + 132, "y-coordinate is 0 (Div(0) = ℕ)", size=11, font=FONT_SANS, fill=RED, weight="bold")

    # Project y instead of x
    svg.rect(294, ry3 + 34, 200, 124, fill=RED_FILL, stroke=RED, sw=1.4, rx=4)
    svg.text(304, ry3 + 52, "Buggy Return:  return y", size=11.5, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(304, ry3 + 74, "Projects 2nd coordinate y:", size=11, font=FONT_SANS, fill=INK)
    svg.text(304, ry3 + 96, "{ y | (x,y) ∈ {(4,0)} } = { 0 }", size=12, font=FONT_SERIF, fill=RED, weight="bold")
    svg.text(304, ry3 + 120, "Candidate output: g = 0", size=11.5, font=FONT_SERIF, fill=RED, weight="bold")

    # BROKEN DOCK 3!
    draw_dock_connector(svg, 494, ry3 + 96, 550, ry3 + 96, label="⊈", ok=False)
    svg.text(522, ry3 + 72, "BROKEN!", size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")

    # Target Gcd(12, 8) rejects g = 0
    svg.rect(550, ry3 + 34, 312, 124, fill=RED_FILL, stroke=RED, sw=1.6, rx=4)
    svg.text(562, ry3 + 52, "Target Port:  Gcd(12, 8) = {4}", size=12, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(562, ry3 + 72, "Counterexample witness:  g = 0", size=12, font=FONT_SERIF, fill=RED, weight="bold")
    svg.rect(562, ry3 + 80, 288, 46, fill="#ffffff", stroke=RED, sw=1.2, rx=3)
    svg.text(572, ry3 + 98, "Div(0) = ℕ = {1, 2, 3, 4, 5, …}  ≠  {1, 2, 4}", size=11.5, font=FONT_SERIF, fill=RED, weight="bold")
    svg.text(572, ry3 + 116, "0 ∤ 12 and 0 ∤ 8 :  { 0 } ⊈ Gcd(12, 8) = { 4 }", size=11, font=FONT_SANS, fill=RED, weight="bold")
    svg.text(562, ry3 + 144, "Dock check catches swapped register instantly!", size=11, font=FONT_SANS, fill=RED, weight="bold")

    with open("fig-5.svg", "w") as f:
        f.write(svg.render())


if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    generate_fig5()
    print("Generated fig-1.svg through fig-5.svg successfully.")
