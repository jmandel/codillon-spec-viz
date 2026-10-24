#!/usr/bin/env python3
"""
Generator for Bézout / Ideal View visualizations of Gcd(a, b) as a refinement type.
Generates fig-1.svg through fig-5.svg.
"""

import math
import html

# Strict Palette (NO GREEN ANYWHERE)
BG = "#fffff0"          # ivory background
INK = "#222222"         # primary ink
PURPLE = "#6A5ACD"      # type / region / ideal generator purple
PURPLE_FILL = "#d9d5f2" # muted purple fill
PURPLE_LIGHT = "#eeecfa"
RED = "#8b0000"         # violation / type error ONLY
RED_FILL = "#f7dcdc"    # light red fill for error highlights
INDIGO = "#4b0082"      # unknown / symbolic
NAVY = "#00008b"        # concrete run / value / witness
GRAY_DARK = "#555555"
GRAY_MID = "#888888"
GRAY_LIGHT = "#cccccc"
GRAY_FAINT = "#e6e6dc"

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"


def esc(s):
    return html.escape(str(s))


class SVGBuilder:
    def __init__(self, width=900, height=600):
        self.width = width
        self.height = height
        self.elements = []
        self.defs = []

    def add_def(self, d):
        self.defs.append(d)

    def add(self, el):
        self.elements.append(el)

    def add_standard_markers(self):
        self.add_def(f'''
        <marker id="arrow-navy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{NAVY}"/>
        </marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{PURPLE}"/>
        </marker>
        <marker id="arrow-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{INK}"/>
        </marker>
        <marker id="arrow-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{GRAY_MID}"/>
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{RED}"/>
        </marker>
        ''')

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, rx=0, dash=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        op_attr = f' opacity="{opacity}"' if opacity != 1.0 else ''
        rx_attr = f' rx="{rx}" ry="{rx}"' if rx else ''
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{rx_attr}{d_attr}{op_attr}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1, dash=None, marker_end=None, marker_start=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        me_attr = f' marker-end="url(#{marker_end})"' if marker_end else ''
        ms_attr = f' marker-start="url(#{marker_start})"' if marker_start else ''
        op_attr = f' opacity="{opacity}"' if opacity != 1.0 else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{d_attr}{me_attr}{ms_attr}{op_attr}/>')

    def circle(self, cx, cy, r, fill=INK, stroke="none", sw=1, dash=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        op_attr = f' opacity="{opacity}"' if opacity != 1.0 else ''
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}{op_attr}/>')

    def path(self, d, fill="none", stroke=INK, sw=1.5, dash=None, marker_end=None, marker_start=None, opacity=1.0):
        d_attr = f' stroke-dasharray="{dash}"' if dash else ''
        me_attr = f' marker-end="url(#{marker_end})"' if marker_end else ''
        ms_attr = f' marker-start="url(#{marker_start})"' if marker_start else ''
        op_attr = f' opacity="{opacity}"' if opacity != 1.0 else ''
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_attr}{me_attr}{ms_attr}{op_attr}/>')

    def text(self, x, y, content, size=14, font=FONT_SERIF, fill=INK, anchor="start", weight="normal", style="normal", escape=True):
        txt = esc(content) if escape else content
        w_attr = f' font-weight="{weight}"' if weight != "normal" else ''
        s_attr = f' font-style="{style}"' if style != "normal" else ''
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{w_attr}{s_attr}>{txt}</text>')

    def render(self):
        out = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">',
            f'<defs>{"".join(self.defs)}</defs>',
            f'<rect x="0" y="0" width="{self.width}" height="{self.height}" fill="{BG}"/>'
        ]
        out.extend(self.elements)
        out.append('</svg>')
        return "\n".join(out)

    def save(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.render())


def draw_header(svg, title, subtitle, tag="BÉZOUT / IDEAL VIEW"):
    svg.rect(25, 16, 850, 58, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.2, rx=6)
    svg.text(42, 41, title, size=18, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(42, 62, subtitle, size=13, font=FONT_SERIF, fill=GRAY_DARK, escape=False)
    svg.rect(685, 23, 178, 22, fill=PURPLE_FILL, stroke=PURPLE, sw=0.8, rx=4)
    svg.text(774, 38, tag, size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")


def draw_step_bracket(svg, x1, x2, y, label, color=PURPLE, up=False):
    direction = -1 if up else 1
    h = 7 * direction
    mid = (x1 + x2) / 2.0
    d = f"M {x1:.1f} {y:.1f} L {x1:.1f} {y+h:.1f} L {x2:.1f} {y+h:.1f} L {x2:.1f} {y:.1f}"
    svg.path(d, fill="none", stroke=color, sw=1.6)
    svg.line(mid, y+h, mid, y+h+4*direction, stroke=color, sw=1.4)
    if label:
        ty = y + h + (16 if direction > 0 else -7)
        svg.text(mid, ty, label, size=11.5, font=FONT_SANS, fill=color, anchor="middle", weight="bold")


# =============================================================================
# FIGURE 1: The Ideal 12ℤ + 8ℤ = 4ℤ and its Unique Positive Generator (12, 8)
# =============================================================================
def generate_fig1():
    a, b = 12, 8
    g = math.gcd(a, b)
    assert g == 4

    svg = SVGBuilder(width=900, height=600)
    svg.add_standard_markers()

    # Title <= 12 words (11 words)
    draw_header(
        svg,
        "Linear combinations 12x + 8y form 4ℤ; gcd(12, 8) = 4 is its generator",
        f'Ideal characterization: <tspan font-style="italic">Gcd</tspan>(12, 8) = {{ <tspan font-style="italic">g</tspan> ∈ ℕ | <tspan font-style="italic">g</tspan> &gt; 0 ∧ 12ℤ + 8ℤ = <tspan font-style="italic">g</tspan>ℤ }} = {{ 4 }}',
        tag="FIG 1 · IDEAL (12, 8)"
    )

    n_min, n_max = -16, 24
    x_left, x_right = 115.0, 845.0
    span = n_max - n_min  # 40
    scale = (x_right - x_left) / span  # 18.25 px per integer

    def nx(n):
        return x_left + (n - n_min) * scale

    # --- SECTION 1: Input Strides 12ℤ and 8ℤ ---
    y_sec1 = 92
    svg.text(35, y_sec1 + 12, "1. Input generator strides on ℤ", size=14, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(268, y_sec1 + 12, "Each input alone generates a coarse lattice of multiples:", size=12.5, font=FONT_SANS, fill=GRAY_DARK)

    # Track 12Z
    y_12 = 142
    svg.text(35, y_12 - 2, "12ℤ = {12x}", size=13, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(35, y_12 + 13, "stride a = 12", size=11, font=FONT_SANS, fill=GRAY_DARK)
    svg.line(x_left - 8, y_12, x_right + 8, y_12, stroke=GRAY_LIGHT, sw=1.5)
    for n in range(n_min, n_max + 1):
        x = nx(n)
        if n % a == 0:
            svg.circle(x, y_12, 5.5, fill=NAVY, stroke=BG, sw=1.2)
            svg.text(x, y_12 + 18, f"{n}", size=11.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
            svg.text(x, y_12 - 10, f"12·({n//12})", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
        else:
            svg.line(x, y_12 - 3, x, y_12 + 3, stroke=GRAY_LIGHT, sw=1)

    x0, x12 = nx(0), nx(12)
    svg.path(f"M {x0+6:.1f} {y_12-6:.1f} Q {(x0+x12)/2:.1f} {y_12-30:.1f} {x12-6:.1f} {y_12-6:.1f}",
             stroke=NAVY, sw=1.5, dash="4,3", marker_end="arrow-navy")
    svg.text((x0+x12)/2, y_12 - 20, "stride a = +12", size=11.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    # Track 8Z
    y_8 = 205
    svg.text(35, y_8 - 2, "8ℤ = {8y}", size=13, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(35, y_8 + 13, "stride b = 8", size=11, font=FONT_SANS, fill=GRAY_DARK)
    svg.line(x_left - 8, y_8, x_right + 8, y_8, stroke=GRAY_LIGHT, sw=1.5)
    for n in range(n_min, n_max + 1):
        x = nx(n)
        if n % b == 0:
            svg.circle(x, y_8, 5.5, fill=NAVY, stroke=BG, sw=1.2)
            svg.text(x, y_8 + 18, f"{n}", size=11.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
            svg.text(x, y_8 - 10, f"8·({n//8})", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")
        else:
            svg.line(x, y_8 - 3, x, y_8 + 3, stroke=GRAY_LIGHT, sw=1)

    x8 = nx(8)
    svg.path(f"M {x0+6:.1f} {y_8-6:.1f} Q {(x0+x8)/2:.1f} {y_8-28:.1f} {x8-6:.1f} {y_8-6:.1f}",
             stroke=NAVY, sw=1.5, dash="4,3", marker_end="arrow-navy")
    svg.text((x0+x8)/2, y_8 - 19, "stride b = +8", size=11.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    # --- SECTION 2: The Ideal 12Z + 8Z = 4Z ---
    y_sec2 = 248
    svg.rect(25, y_sec2, 850, 212, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.4, rx=8, opacity=0.55)
    svg.text(40, y_sec2 + 23, "2. The Ideal  12ℤ + 8ℤ = { 12x + 8y | x, y ∈ ℤ } = 4ℤ", size=14.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(435, y_sec2 + 23, "Interfering strides +12 and −8 carve out a finer regular lattice of step g = 4:", size=12, font=FONT_SANS, fill=INK)

    y_ideal = 358
    x4 = nx(4)

    # Highlight the open interval (0, 4) as forbidden / empty gap
    svg.rect(x0, y_ideal - 18, x4 - x0, 36, fill=PURPLE_FILL, stroke=PURPLE, sw=1.2, dash="3,2")
    svg.rect(x0 - 115, y_ideal - 46, 128, 20, fill=PURPLE_FILL, stroke=PURPLE, sw=1, rx=4)
    svg.line(x0 + 13, y_ideal - 26, (x0+x4)/2 - 4, y_ideal - 18, stroke=PURPLE, sw=1.2)
    svg.text(x0 - 51, y_ideal - 32, "empty gap: no 12x+8y", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Bézout witness hops: 0 -> +12 -> +4 (via -8)
    # Draw +12 arc cleanly in the space below the section title
    svg.path(f"M {x0+3:.1f} {y_ideal-8:.1f} C {x0+45:.1f} {y_ideal-72:.1f}, {x12-45:.1f} {y_ideal-72:.1f}, {x12-2:.1f} {y_ideal-9:.1f}",
             stroke=NAVY, sw=2.2, marker_end="arrow-navy")
    svg.rect((x0+x12)/2 - 64, y_ideal - 74, 128, 19, fill=BG, stroke=NAVY, sw=1.2, rx=4)
    svg.text((x0+x12)/2, y_ideal - 60, "hop 1: +1·(12) = +12", size=11.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    # Draw -8 arc from 12 back to 4
    svg.path(f"M {x12-4:.1f} {y_ideal-8:.1f} C {x12-20:.1f} {y_ideal-44:.1f}, {x4+20:.1f} {y_ideal-44:.1f}, {x4+6:.1f} {y_ideal-10:.1f}",
             stroke=NAVY, sw=2.2, marker_end="arrow-navy")
    svg.rect((x4+x12)/2 - 58, y_ideal - 48, 116, 18, fill=BG, stroke=NAVY, sw=1.2, rx=4)
    svg.text((x4+x12)/2, y_ideal - 35, "hop 2: −1·(8) = −8", size=11.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    # Left label on ideal line
    svg.text(35, y_ideal - 2, "12ℤ + 8ℤ", size=13, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(35, y_ideal + 13, "= 4ℤ", size=13, font=FONT_SERIF, fill=PURPLE, weight="bold")

    # Number line axis
    svg.line(x_left - 10, y_ideal, x_right + 10, y_ideal, stroke=INK, sw=2)

    recipes = {
        -16: "−2(8)",
        -12: "−1(12)",
        -8:  "−1(8)",
        -4:  "−1(12)+1(8)",
        0:   "0(12)+0(8)",
        4:   "1(12)−1(8)",
        8:   "1(8)",
        12:  "1(12)",
        16:  "2(8)",
        20:  "1(12)+1(8)",
        24:  "2(12)"
    }

    for n in range(n_min, n_max + 1):
        x = nx(n)
        if n % g == 0:
            is_gen = (n == g)
            is_zero = (n == 0)
            if is_gen:
                svg.circle(x, y_ideal, 10.5, fill=PURPLE_FILL, stroke=PURPLE, sw=2.5)
                svg.circle(x, y_ideal, 5.5, fill=PURPLE, stroke=BG, sw=1.2)
            elif is_zero:
                svg.circle(x, y_ideal, 6.5, fill=INK, stroke=BG, sw=1.5)
            else:
                svg.circle(x, y_ideal, 5.5, fill=PURPLE, stroke=BG, sw=1.2)

            svg.text(x, y_ideal + 22, f"{n}", size=12.5 if is_gen else 11.5, font=FONT_SERIF,
                     fill=PURPLE if is_gen else INK, anchor="middle", weight="bold")
            svg.text(x, y_ideal + 37, recipes[n], size=11, font=FONT_SANS,
                     fill=NAVY if is_gen else GRAY_DARK, anchor="middle",
                     weight="bold" if is_gen else "normal")
        else:
            svg.circle(x, y_ideal, 2.0, fill=GRAY_MID)

    # Step brackets between adjacent multiples of 4
    for k in range(-4, 6):
        xa, xb = nx(k * 4), nx((k + 1) * 4)
        lbl = "step g = 4" if k == 0 else ("+4" if k not in (1, 2, 3, 4) else None)
        col = PURPLE if k == 0 else GRAY_MID
        draw_step_bracket(svg, xa + 2, xb - 2, y_ideal + 44, lbl, color=col, up=False)

    # Callout badge pointing to g = 4 placed cleanly in the bottom right space
    svg.rect(x4 + 28, y_ideal + 60, 260, 26, fill=PURPLE_FILL, stroke=PURPLE, sw=1.8, rx=5)
    svg.path(f"M {x4:.1f} {y_ideal+12:.1f} L {x4:.1f} {y_ideal+73:.1f} L {x4+28:.1f} {y_ideal+73:.1f}",
             fill="none", stroke=PURPLE, sw=1.8, dash="2,2")
    svg.text(x4 + 158, y_ideal + 77, "g = 4 : smallest positive element (generator)", size=12, font=FONT_SERIF, fill=PURPLE, anchor="middle", weight="bold")

    # --- SECTION 3: Refinement Type Meaning Box ---
    y_sec3 = 474
    svg.rect(25, y_sec3, 850, 108, fill=BG, stroke=PURPLE, sw=1.8, rx=8)
    svg.rect(25, y_sec3, 250, 108, fill=PURPLE_FILL, stroke=PURPLE, sw=1.8, rx=8)

    svg.text(150, y_sec3 + 28, "Refinement Type as Ideal Generator", size=13.5, font=FONT_SERIF, fill=INK, anchor="middle", weight="bold")
    svg.text(150, y_sec3 + 52, "Gcd(12, 8) =", size=15, font=FONT_SERIF, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(150, y_sec3 + 73, "{ g ∈ ℕ | g > 0 ∧ 12ℤ + 8ℤ = gℤ }", size=13, font=FONT_SERIF, fill=INK, anchor="middle")
    svg.text(150, y_sec3 + 94, "Singleton inhabitant: { 4 }", size=12.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    col1_x = 292
    col2_x = 582
    svg.text(col1_x, y_sec3 + 26, "(1) Closure / Reachability  (gℤ ⊆ 12ℤ + 8ℤ):", size=13, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(col1_x + 10, y_sec3 + 46, "Bézout witness (x, y) = (1, −1) proves:", size=12, font=FONT_SANS, fill=INK)
    svg.text(col1_x + 10, y_sec3 + 66, "12·(1) + 8·(−1) = 4  ∈  12ℤ + 8ℤ", size=13, font=FONT_SERIF, fill=NAVY, weight="bold")
    svg.text(col1_x + 10, y_sec3 + 86, "Every multiple 4k = 12(k) + 8(−k) is reachable.", size=12, font=FONT_SANS, fill=GRAY_DARK)

    svg.line(568, y_sec3 + 12, 568, y_sec3 + 96, stroke=GRAY_LIGHT, sw=1.2)

    svg.text(col2_x, y_sec3 + 26, "(2) Minimality / Divisibility  (12ℤ + 8ℤ ⊆ gℤ):", size=13, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(col2_x + 10, y_sec3 + 46, "4 divides both generators: 12 = 4·3 and 8 = 4·2.", size=12, font=FONT_SANS, fill=INK)
    svg.text(col2_x + 10, y_sec3 + 66, "⇒ 12x + 8y = 4·(3x + 2y) ∈ 4ℤ  for all x, y.", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(col2_x + 10, y_sec3 + 86, "No combination can land inside the gap (0, 4).", size=12, font=FONT_SANS, fill=GRAY_DARK)

    svg.save("fig-1.svg")
    print("Generated fig-1.svg")


# =============================================================================
# FIGURE 2: 2-D Coefficient Grid (x, y) ∈ ℤ² Projected to Ideal 12ℤ + 8ℤ = 4ℤ
# =============================================================================
def generate_fig2():
    a, b = 12, 8
    g = math.gcd(a, b)
    assert g == 4

    svg = SVGBuilder(width=900, height=640)
    svg.add_standard_markers()

    # Title <= 12 words (10 words)
    draw_header(
        svg,
        "Parallel fibers 12x + 8y = 4k partition ℤ² and project onto 4ℤ",
        f'Every lattice point (<tspan font-style="italic">x</tspan>, <tspan font-style="italic">y</tspan>) ∈ ℤ² is a Bézout certificate for <tspan font-style="italic">v</tspan> = 12<tspan font-style="italic">x</tspan> + 8<tspan font-style="italic">y</tspan>; kernel vector (−2, 3) shifts along a fiber.',
        tag="FIG 2 · 2-D LATTICE & FIBERS"
    )

    gx_left, gx_top, gx_w, gx_h = 30, 88, 490, 530
    svg.rect(gx_left, gx_top, gx_w, gx_h, fill=BG, stroke=GRAY_LIGHT, sw=1.2, rx=8)
    svg.text(gx_left + 16, gx_top + 24, "Coefficient Lattice  (x, y) ∈ ℤ²", size=15, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(gx_left + 235, gx_top + 24, "each node shows  v = 12x + 8y", size=12.5, font=FONT_SANS, fill=GRAY_DARK)

    cx0, cy0 = 275.0, 326.0
    step_x, step_y = 62.0, 56.0  # px per unit in x and y

    def pt(x, y):
        return (cx0 + x * step_x, cy0 - y * step_y)

    def fiber_pts(k, x_min=-3.25, x_max=3.25, y_min=-3.25, y_max=3.25):
        pts = []
        for x in [x_min, x_max]:
            y = (k - 3.0 * x) / 2.0
            if y_min - 1e-6 <= y <= y_max + 1e-6:
                pts.append((x, y))
        for y in [y_min, y_max]:
            x = (k - 2.0 * y) / 3.0
            if x_min - 1e-6 <= x <= x_max + 1e-6:
                pts.append((x, y))
        uniq = []
        for p in pts:
            if not any(abs(p[0]-q[0]) < 1e-4 and abs(p[1]-q[1]) < 1e-4 for q in uniq):
                uniq.append(p)
        uniq.sort(key=lambda p: p[0])
        return uniq

    # Shaded empty corridor between k=0 and k=1
    p0 = fiber_pts(0)
    p1 = fiber_pts(1)
    if len(p0) == 2 and len(p1) == 2:
        poly_coords = [pt(*p0[0]), pt(*p0[1]), pt(*p1[1]), pt(*p1[0])]
        d_poly = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in poly_coords) + " Z"
        svg.path(d_poly, fill=PURPLE_FILL, stroke="none", opacity=0.65)

    # Grid lines and outer margin coordinate labels (no overlap with circles!)
    for i in range(-3, 4):
        x1, y1 = pt(i, -3.25)
        x2, y2 = pt(i, 3.25)
        svg.line(x1, y1, x2, y2, stroke=GRAY_FAINT if i != 0 else GRAY_MID, sw=1.0 if i != 0 else 1.6)
        # Put x labels along the top margin of the grid
        svg.text(x1, pt(0, 3.25)[1] - 8, f"x={i}", size=11, font=FONT_SANS, fill=INK if i == 0 else GRAY_DARK, anchor="middle", weight="bold" if i == 0 else "normal")

        x3, y3 = pt(-3.25, i)
        x4, y4 = pt(3.25, i)
        svg.line(x3, y3, x4, y4, stroke=GRAY_FAINT if i != 0 else GRAY_MID, sw=1.0 if i != 0 else 1.6)
        # Put y labels along the left margin of the grid
        svg.text(pt(-3.25, 0)[0] - 8, y3 + 4, f"y={i}", size=11, font=FONT_SANS, fill=INK if i == 0 else GRAY_DARK, anchor="end", weight="bold" if i == 0 else "normal")

    # Draw parallel fibers 3x + 2y = k for k in -6..6
    for k in range(-6, 7):
        fpts = fiber_pts(k)
        if len(fpts) == 2:
            (x1, y1), (x2, y2) = pt(*fpts[0]), pt(*fpts[1])
            if k == 1:
                svg.line(x1, y1, x2, y2, stroke=PURPLE, sw=2.6)
            elif k == 0:
                svg.line(x1, y1, x2, y2, stroke=NAVY, sw=2.0, dash="5,3")
            else:
                svg.line(x1, y1, x2, y2, stroke=PURPLE, sw=1.0, dash="3,3", opacity=0.55)

    # Draw lattice points (x, y) and their linear combination values 12x + 8y FIRST, then callout badges on top
    for x in range(-3, 4):
        for y in range(-3, 4):
            val = a * x + b * y
            px, py = pt(x, y)
            is_g_fiber = (val == g)
            is_zero_fiber = (val == 0)

            if is_g_fiber:
                svg.circle(px, py, 13, fill=PURPLE, stroke=BG, sw=1.8)
                svg.text(px, py + 4, f"{val}", size=11.5, font=FONT_SANS, fill=BG, anchor="middle", weight="bold")
            elif is_zero_fiber:
                svg.circle(px, py, 11.5, fill=NAVY, stroke=BG, sw=1.5)
                svg.text(px, py + 4, "0", size=11, font=FONT_SANS, fill=BG, anchor="middle", weight="bold")
            else:
                svg.circle(px, py, 10.5, fill=BG, stroke=PURPLE if val > 0 else GRAY_MID, sw=1.2)
                svg.text(px, py + 4, f"{val}", size=11, font=FONT_SANS, fill=INK if val > 0 else GRAY_DARK, anchor="middle")

    # Coordinate badges for the two witnesses on k=1 fiber: (1, -1) and (-1, 2)
    for (wx, wy, dx, dy) in [(1, -1, 34, -14), (-1, 2, 34, -14)]:
        px, py = pt(wx, wy)
        bx, by = px + dx, py + dy
        svg.rect(bx - 24, by - 11, 48, 16, fill=PURPLE_FILL, stroke=PURPLE, sw=1.2, rx=3)
        svg.text(bx, by + 1, f"({wx},{wy})", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Highlight kernel shift arrow along k=1 fiber: from (1, -1) to (-1, 2), with label placed in the clean margin
    p_w1 = pt(1, -1)
    p_w2 = pt(-1, 2)
    svg.path(f"M {p_w1[0]-7:.1f} {p_w1[1]-9:.1f} Q {(p_w1[0]+p_w2[0])/2 - 18:.1f} {(p_w1[1]+p_w2[1])/2 + 12:.1f} {p_w2[0]+6:.1f} {p_w2[1]+11:.1f}",
             stroke=NAVY, sw=2.2, dash="4,2", marker_end="arrow-navy")
    # Put kernel shift callout box in the bottom-left corner of the grid box, below y=-3
    svg.rect(44, 518, 222, 36, fill=BG, stroke=NAVY, sw=1.3, rx=5)
    svg.text(155, 533, "Kernel shift along fiber: +(−2, +3)", size=11.5, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
    svg.text(155, 548, "since 12(−2) + 8(3) = 0", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    svg.rect(274, 518, 234, 36, fill=PURPLE_FILL, stroke=PURPLE, sw=1.3, rx=5)
    svg.text(391, 533, "Empty strip  0 < 12x + 8y < 4", size=11.5, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(391, 548, "has ZERO integer lattice points!", size=11, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")

    # Bottom summary inside left panel
    svg.rect(44, 562, 464, 44, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=5)
    svg.text(276, 580, "Closest parallel fiber to k = 0 is k = 1  (12x + 8y = 4):", size=12, font=FONT_SERIF, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(276, 597, "All solutions on fiber k = 1 are (1 − 2t, −1 + 3t) for t ∈ ℤ.", size=11.5, font=FONT_SANS, fill=INK, anchor="middle")

    # --- Right panel: Projection onto 1D Number Line (vertical) ---
    rx_left = 555
    svg.rect(rx_left, gx_top, 320, gx_h, fill=BG, stroke=GRAY_LIGHT, sw=1.2, rx=8)
    svg.text(rx_left + 16, gx_top + 24, "Projected Ideal  v ∈ 12ℤ + 8ℤ = 4ℤ", size=15, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(rx_left + 16, gx_top + 43, "Map (x, y) ↦ 12x + 8y collapses each fiber to 4k:", size=12, font=FONT_SANS, fill=GRAY_DARK)

    axis_x = 640.0
    vy_top, vy_bot = 152.0, 535.0
    v_min, v_max = -20, 24

    def vy(v):
        return vy_bot - (v - v_min) / (v_max - v_min) * (vy_bot - vy_top)

    # Highlight gap (0, 4) on vertical axis
    y_v0, y_v4 = vy(0), vy(4)
    svg.rect(axis_x - 16, y_v4, 32, y_v0 - y_v4, fill=PURPLE_FILL, stroke=PURPLE, sw=1.2, dash="3,2")

    # Clean projection connectors from right border of left panel (x=520) to vertical axis (axis_x=640)
    # Only draw for k in -3..4 where fiber exits or near right side cleanly
    for k in range(-3, 5):
        val = 4 * k
        target_y = vy(val)
        start_y = target_y + k * 4  # clean fan-out across the gap between panels
        col = PURPLE if k == 1 else (NAVY if k == 0 else GRAY_LIGHT)
        sw = 2.2 if k in (0, 1) else 1.1
        dash = None if k == 1 else "3,3"
        svg.path(f"M {520:.1f} {start_y:.1f} C {555:.1f} {start_y:.1f}, {595:.1f} {target_y:.1f}, {axis_x-13:.1f} {target_y:.1f}",
                 stroke=col, sw=sw, dash=dash,
                 marker_end="arrow-purple" if k == 1 else ("arrow-navy" if k == 0 else None))

    svg.line(axis_x, vy_top - 12, axis_x, vy_bot + 12, stroke=INK, sw=2)

    fiber_equations = {
        24:  "k = +6 : (2, 0), (0, 3)",
        20:  "k = +5 : (1, 1), (−1, 4)",
        16:  "k = +4 : (0, 2), (2, −1)",
        12:  "k = +3 : (1, 0), (−1, 3)",
        8:   "k = +2 : (0, 1), (2, −2)",
        4:   "k = +1 : (1, −1), (−1, 2) ★",
        0:   "k =  0 : (0, 0), (−2, 3), (2, −3)",
        -4:  "k = −1 : (−1, 1), (1, −2)",
        -8:  "k = −2 : (0, −1), (−2, 2)",
        -12: "k = −3 : (−1, 0), (1, −3)",
        -16: "k = −4 : (0, −2), (−2, 1)",
        -20: "k = −5 : (−1, −1)"
    }

    for v in range(v_min, v_max + 1):
        yv = vy(v)
        if v % 4 == 0:
            is_g = (v == 4)
            is_0 = (v == 0)
            if is_g:
                svg.circle(axis_x, yv, 9.5, fill=PURPLE_FILL, stroke=PURPLE, sw=2.2)
                svg.circle(axis_x, yv, 5, fill=PURPLE)
                svg.rect(axis_x + 15, yv - 12, 206, 22, fill=PURPLE_FILL, stroke=PURPLE, sw=1.5, rx=4)
                svg.text(axis_x + 22, yv + 4, f"+4   {fiber_equations[v]}", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")
            elif is_0:
                svg.circle(axis_x, yv, 6, fill=NAVY, stroke=BG, sw=1.2)
                svg.text(axis_x + 20, yv + 4, f" 0   {fiber_equations[v]}", size=11.5, font=FONT_SANS, fill=NAVY, weight="bold")
            else:
                svg.circle(axis_x, yv, 5, fill=PURPLE, stroke=BG, sw=1)
                sign_str = f"+{v}" if v > 0 else f"{v}"
                svg.text(axis_x + 20, yv + 4, f"{sign_str}   {fiber_equations[v]}", size=11, font=FONT_SANS, fill=INK)
        else:
            svg.line(axis_x - 3, yv, axis_x + 3, yv, stroke=GRAY_MID, sw=0.8)

    svg.rect(rx_left + 14, 562, 292, 44, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=5)
    svg.text(rx_left + 160, 580, "Quotient  ℤ² / ker(12x+8y)  ≅  4ℤ", size=12, font=FONT_SERIF, fill=PURPLE, anchor="middle", weight="bold")
    svg.text(rx_left + 160, 597, "Generator g = 4 is the step between adjacent fibers.", size=11.5, font=FONT_SANS, fill=INK, anchor="middle")

    svg.save("fig-2.svg")
    print("Generated fig-2.svg")


# =============================================================================
# FIGURE 3: Extended Euclid as Proof Witness Generator (1071, 462 -> 21) & Coprime (13, 8 -> 1)
# =============================================================================
def extended_gcd_steps(a, b):
    steps = []
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    steps.append((0, None, old_r, old_x, old_y, f"{a}({old_x}) + {b}({old_y}) = {old_r}"))
    steps.append((1, None, r, x, y, f"{a}({x}) + {b}({y}) = {r}"))
    step_idx = 2
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y
        rem_val = r
        assert a * x + b * y == rem_val
        steps.append((step_idx, q, rem_val, x, y, f"{a}({x}) + {b}({y}) = {rem_val}"))
        step_idx += 1
    return steps


def generate_fig3():
    a1, b1 = 1071, 462
    g1 = math.gcd(a1, b1)
    assert g1 == 21
    steps1 = extended_gcd_steps(a1, b1)
    assert steps1[3][2] == 21 and steps1[3][3] == -3 and steps1[3][4] == 7

    a2, b2 = 13, 8
    g2 = math.gcd(a2, b2)
    assert g2 == 1
    assert 13 * (-3) + 8 * 5 == 1

    svg = SVGBuilder(width=900, height=635)
    svg.add_standard_markers()

    # Title <= 12 words (11 words)
    draw_header(
        svg,
        "Extended Euclid preserves the ideal while shrinking remainders to the generator",
        f'Each remainder <tspan font-style="italic">r</tspan><tspan baseline-shift="sub" font-size="10">i</tspan> = <tspan font-style="italic">a</tspan><tspan font-style="italic">x</tspan><tspan baseline-shift="sub" font-size="10">i</tspan> + <tspan font-style="italic">b</tspan><tspan font-style="italic">y</tspan><tspan baseline-shift="sub" font-size="10">i</tspan> stays inside <tspan font-style="italic">a</tspan>ℤ + <tspan font-style="italic">b</tspan>ℤ until <tspan font-style="italic">r</tspan><tspan baseline-shift="sub" font-size="10">k+1</tspan> = 0 proves <tspan font-style="italic">r</tspan><tspan baseline-shift="sub" font-size="10">k</tspan> generates the whole ideal.',
        tag="FIG 3 · EXTENDED EUCLID"
    )

    # --- TOP PANEL: (a, b) = (1071, 462) -> g = 21 ---
    p1_y = 86
    svg.rect(25, p1_y, 850, 326, fill=BG, stroke=PURPLE, sw=1.5, rx=8)
    svg.rect(25, p1_y, 850, 32, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.0, rx=8)
    svg.text(42, p1_y + 21, "Case A:  a = 1071,  b = 462   ⇒   1071ℤ + 462ℤ = 21ℤ   (Gcd(1071, 462) = { 21 })", size=14.5, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(858, p1_y + 21, "Loop Invariant:  rᵢℤ + rᵢ₊₁ℤ = 1071ℤ + 462ℤ", size=12, font=FONT_SANS, fill=PURPLE, anchor="end", weight="bold")

    # Left sub-table: Extended Euclid trace
    tx, ty = 38, p1_y + 42
    col_w = [42, 48, 60, 48, 48, 224]  # sum = 470
    headers = ["Step", "Quot q", "Rem rᵢ", "xᵢ", "yᵢ", "Bézout Certificate (∈ 1071ℤ + 462ℤ)"]

    cur_x = tx
    svg.rect(tx, ty, sum(col_w), 24, fill=PURPLE_FILL, stroke=PURPLE, sw=1)
    for h_txt, w in zip(headers, col_w):
        svg.text(cur_x + w/2, ty + 16, h_txt, size=11, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
        cur_x += w

    for idx, (step_i, q, r_val, x_val, y_val, cert) in enumerate(steps1):
        ry = ty + 24 + idx * 29
        is_gcd_row = (r_val == 21)
        is_zero_row = (r_val == 0)
        row_fill = PURPLE_FILL if is_gcd_row else (BG if idx % 2 == 0 else PURPLE_LIGHT)
        row_stroke = PURPLE if is_gcd_row else GRAY_LIGHT
        svg.rect(tx, ry, sum(col_w), 29, fill=row_fill, stroke=row_stroke, sw=1.8 if is_gcd_row else 0.8)

        q_str = "—" if q is None else str(q)
        vals = [f"i = {step_i}", q_str, str(r_val), str(x_val), str(y_val), cert]
        cx = tx
        for c_idx, (v_str, w) in enumerate(zip(vals, col_w)):
            col_color = PURPLE if is_gcd_row else (NAVY if c_idx in (2, 5) and not is_zero_row else INK)
            fw = "bold" if (is_gcd_row or c_idx == 2) else "normal"
            svg.text(cx + w/2, ry + 19, v_str, size=11.5, font=FONT_SANS if c_idx < 5 else FONT_SERIF,
                     fill=col_color, anchor="middle", weight=fw)
            cx += w

    # Annotation under table (fits cleanly inside width 470)
    svg.rect(tx, ty + 178, sum(col_w), 88, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=5)
    svg.text(tx + 12, ty + 198, "Why i = 3 proves g = 21 ∈ Gcd(1071, 462):", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")
    svg.text(tx + 12, ty + 218, "• Reachability (21ℤ ⊆ 1071ℤ + 462ℤ):", size=11.5, font=FONT_SANS, fill=NAVY, weight="bold")
    svg.text(tx + 24, ty + 234, "Row i = 3 constructs  1071(−3) + 462(7) = 21.", size=11.5, font=FONT_SANS, fill=INK)
    svg.text(tx + 12, ty + 253, "• Exactness (1071ℤ + 462ℤ ⊆ 21ℤ):  Row i = 4 hits r₄ = 0, so 21 | 1071 and 21 | 462.", size=11.5, font=FONT_SANS, fill=INK, weight="bold")

    # Right sub-diagram: Shrinking remainders on the 21Z ideal lattice + zoomed lattice
    rx0 = 524
    svg.text(rx0, ty + 14, "Remainder Cascade on 1071ℤ + 462ℤ = 21ℤ", size=13.5, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(rx0, ty + 31, "Every remainder is an exact multiple of 21:", size=11.5, font=FONT_SANS, fill=GRAY_DARK)

    bar_y = ty + 82
    bar_x1, bar_x2 = rx0 + 12, 855.0
    bar_w = bar_x2 - bar_x1

    def bx(val):
        return bar_x1 + (val / 1071.0) * bar_w

    svg.line(bar_x1, bar_y, bar_x2, bar_y, stroke=INK, sw=2)
    for m in range(0, 52):
        v = m * 21
        x = bx(v)
        svg.line(x, bar_y - (4 if m % 5 == 0 else 2), x, bar_y + (4 if m % 5 == 0 else 2),
                 stroke=PURPLE if m % 5 == 0 else GRAY_LIGHT, sw=1)

    # Plot remainders: 1071, 462, 147, 21, 0 with non-overlapping labels
    for val in [0, 21, 147, 462, 1071]:
        x = bx(val)
        col = PURPLE if val == 21 else NAVY
        r = 6.5 if val == 21 else 4.8
        svg.circle(x, bar_y, r, fill=col, stroke=BG, sw=1.2)

    svg.text(bx(0), bar_y - 11, "0", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx(21) + 4, bar_y + 20, "g=21", size=11, font=FONT_SANS, fill=PURPLE, anchor="start", weight="bold")
    svg.text(bx(147), bar_y - 16, "147=7(21)", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
    svg.text(bx(462) + 8, bar_y + 20, "462 = 22·(21)", size=11, font=FONT_SANS, fill=NAVY, anchor="start", weight="bold")
    svg.text(bx(1071), bar_y + 20, "1071 = 51·(21)", size=11, font=FONT_SANS, fill=NAVY, anchor="end", weight="bold")

    # Remainder reduction arcs
    svg.path(f"M {bx(1071):.1f} {bar_y-6:.1f} Q {(bx(1071)+bx(147))/2:.1f} {bar_y-50:.1f} {bx(147)+5:.1f} {bar_y-6:.1f}",
             stroke=NAVY, sw=1.6, dash="4,2", marker_end="arrow-navy")
    svg.text((bx(1071)+bx(147))/2 + 25, bar_y - 32, "1071 − 2·(462) = 147", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    svg.path(f"M {bx(462):.1f} {bar_y+6:.1f} Q {(bx(462)+bx(21))/2:.1f} {bar_y+50:.1f} {bx(21)+4:.1f} {bar_y+6:.1f}",
             stroke=PURPLE, sw=1.8, marker_end="arrow-purple")
    svg.text((bx(462)+bx(21))/2 + 5, bar_y + 43, "462 − 3·(147) = 21", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # Zoomed-in view of 21Z near 0: [-21, 0, 21, 42, 63, 84, 105, 126, 147]
    zoom_box_y = ty + 142
    zoom_y = zoom_box_y + 66
    svg.rect(rx0, zoom_box_y, 336, 124, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.2, rx=6)
    svg.text(rx0 + 12, zoom_box_y + 19, "Zoomed Ideal Lattice  21ℤ  near 0:", size=12.5, font=FONT_SERIF, fill=PURPLE, weight="bold")

    zx1, zx2 = rx0 + 22, rx0 + 314
    z_min, z_max = -21, 147

    def zx(v):
        return zx1 + (v - z_min) / (z_max - z_min) * (zx2 - zx1)

    svg.rect(zx(0), zoom_y - 14, zx(21) - zx(0), 28, fill=PURPLE_FILL, stroke=PURPLE, sw=1, dash="2,2")
    svg.line(zx1 - 6, zoom_y, zx2 + 6, zoom_y, stroke=INK, sw=1.8)

    for k in range(-1, 8):
        v = k * 21
        x = zx(v)
        is_g = (v == 21)
        if is_g:
            svg.circle(x, zoom_y, 8, fill=PURPLE_FILL, stroke=PURPLE, sw=2)
            svg.circle(x, zoom_y, 4.5, fill=PURPLE)
        else:
            svg.circle(x, zoom_y, 4.5, fill=NAVY if v in (0, 147) else PURPLE)
        svg.text(x, zoom_y + 21, str(v), size=11, font=FONT_SANS, fill=PURPLE if is_g else INK, anchor="middle", weight="bold" if is_g else "normal")

    draw_step_bracket(svg, zx(0) + 1, zx(21) - 1, zoom_y - 16, "step g = 21", color=PURPLE, up=True)
    svg.text(rx0 + 168, zoom_box_y + 112, "20 integers sit strictly inside (0, 21) — none reachable!", size=11.5, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    # --- BOTTOM PANEL: Case B Coprime (13, 8) -> g = 1 (Full Z saturation) ---
    p2_y = 426
    svg.rect(25, p2_y, 850, 192, fill=BG, stroke=NAVY, sw=1.5, rx=8)
    svg.rect(25, p2_y, 850, 32, fill=PURPLE_LIGHT, stroke=NAVY, sw=1.0, rx=8)
    svg.text(42, p2_y + 21, "Case B (Coprime Saturation):  a = 13,  b = 8   ⇒   13ℤ + 8ℤ = 1ℤ = ℤ   (Gcd(13, 8) = { 1 })", size=14.5, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(858, p2_y + 21, "Bézout Witness: 13·(−3) + 8·(5) = −39 + 40 = +1", size=12, font=FONT_SANS, fill=NAVY, anchor="end", weight="bold")

    cy_line = p2_y + 118
    cx_left, cx_right = 55.0, 845.0
    c_min, c_max = -2, 16

    def cnx(n):
        return cx_left + (n - c_min) / (c_max - c_min) * (cx_right - cx_left)

    svg.rect(cnx(0), cy_line - 20, cnx(1) - cnx(0), 40, fill=PURPLE_FILL, stroke=PURPLE, sw=1.2)
    svg.text((cnx(0)+cnx(1))/2, cy_line - 26, "unit step g = 1", size=11.5, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    cascade_arcs = [
        (13, 5, "13 − 8 = 5", -38),
        (8,  3, "8 − 5 = 3",  -24),
        (5,  2, "5 − 3 = 2",  -38),
        (3,  1, "3 − 2 = 1",  -22),
    ]
    for v_start, v_end, lbl, arc_h in cascade_arcs:
        xs, xe = cnx(v_start), cnx(v_end)
        col = PURPLE if v_end == 1 else NAVY
        mk = "arrow-purple" if v_end == 1 else "arrow-navy"
        svg.path(f"M {xs:.1f} {cy_line-7:.1f} Q {(xs+xe)/2:.1f} {cy_line+arc_h*1.6:.1f} {xe+3:.1f} {cy_line-8:.1f}",
                 stroke=col, sw=1.7, dash="3,2" if v_end != 1 else None, marker_end=mk)
        svg.text((xs+xe)/2, cy_line + arc_h - 4, lbl, size=11, font=FONT_SANS, fill=col, anchor="middle", weight="bold")

    svg.line(cx_left - 12, cy_line, cx_right + 12, cy_line, stroke=INK, sw=2)

    for n in range(c_min, c_max + 1):
        x = cnx(n)
        is_one = (n == 1)
        is_input = n in (8, 13)
        if is_one:
            svg.circle(x, cy_line, 9.5, fill=PURPLE_FILL, stroke=PURPLE, sw=2.2)
            svg.circle(x, cy_line, 5, fill=PURPLE)
        elif is_input:
            svg.circle(x, cy_line, 6.5, fill=NAVY, stroke=BG, sw=1.2)
        else:
            svg.circle(x, cy_line, 5, fill=PURPLE, stroke=BG, sw=1)

        svg.text(x, cy_line + 23, str(n), size=12, font=FONT_SERIF,
                 fill=PURPLE if is_one else (NAVY if is_input else INK),
                 anchor="middle", weight="bold" if (is_one or is_input) else "normal")
        best_xy = min(((x_i, y_i) for x_i in range(-8, 9) for y_i in range(-8, 9) if 13*x_i + 8*y_i == n),
                      key=lambda p: abs(p[0]) + abs(p[1]))
        svg.text(x, cy_line + 38, f"({best_xy[0]},{best_xy[1]})", size=11, font=FONT_SANS,
                 fill=PURPLE if is_one else GRAY_DARK, anchor="middle", weight="bold" if is_one else "normal")

    svg.text(450, p2_y + 177, "Every integer n ∈ ℤ has a witness pair (x, y) shown below each tick: coprime inputs saturate the entire integer line (no gaps).",
             size=12, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")

    svg.save("fig-3.svg")
    print("Generated fig-3.svg")


# =============================================================================
# FIGURE 4: Type Error Visualized — Wrong Candidate Generators for Gcd(12, 8)
# =============================================================================
def generate_fig4():
    svg = SVGBuilder(width=900, height=650)
    svg.add_standard_markers()

    # Title <= 12 words (12 words)
    draw_header(
        svg,
        "Type errors: g = 8 misses combinations; g = 2 invents unreachable ghosts",
        f'Testing candidate <tspan font-style="italic">g</tspan> against <tspan font-style="italic">Gcd</tspan>(12, 8) = {{ <tspan font-style="italic">g</tspan> &gt; 0 | 12ℤ + 8ℤ = <tspan font-style="italic">g</tspan>ℤ }} requires two-way set equality: 12ℤ + 8ℤ ⊆ <tspan font-style="italic">g</tspan>ℤ and <tspan font-style="italic">g</tspan>ℤ ⊆ 12ℤ + 8ℤ.',
        tag="FIG 4 · TYPE ERRORS (12, 8)"
    )

    n_min, n_max = -8, 24
    x_left, x_right = 55.0, 845.0
    scale = (x_right - x_left) / (n_max - n_min)

    def nx(n):
        return x_left + (n - n_min) * scale

    # --- TRACK 1: Reference Truth 12Z + 8Z = 4Z ---
    t1_y = 88
    svg.rect(25, t1_y, 850, 126, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.5, rx=8)
    svg.rect(38, t1_y + 10, 212, 24, fill=PURPLE, stroke="none", rx=4)
    svg.text(144, t1_y + 26, "WELL-TYPED:  g = 4 ∈ Gcd(12, 8)", size=12, font=FONT_SANS, fill=BG, anchor="middle", weight="bold")
    svg.text(264, t1_y + 26, "Exact lattice match:  12ℤ + 8ℤ = 4ℤ   (both 12ℤ+8ℤ ⊆ 4ℤ and 4ℤ ⊆ 12ℤ+8ℤ hold)", size=13, font=FONT_SERIF, fill=INK, weight="bold")

    y_line1 = t1_y + 74
    svg.line(x_left - 10, y_line1, x_right + 10, y_line1, stroke=INK, sw=2)

    for n in range(n_min, n_max + 1):
        x = nx(n)
        if n % 4 == 0:
            is_g = (n == 4)
            if is_g:
                svg.circle(x, y_line1, 9, fill=PURPLE_FILL, stroke=PURPLE, sw=2.2)
                svg.circle(x, y_line1, 5, fill=PURPLE)
            else:
                svg.circle(x, y_line1, 5.5, fill=PURPLE, stroke=BG, sw=1.2)
            svg.text(x, y_line1 + 21, str(n), size=12, font=FONT_SERIF, fill=PURPLE if is_g else INK, anchor="middle", weight="bold")
            if n < n_max:
                draw_step_bracket(svg, x + 2, nx(n + 4) - 2, y_line1 - 13, "step 4" if n == 0 else None, color=PURPLE, up=True)
        else:
            svg.line(x, y_line1 - 2.5, x, y_line1 + 2.5, stroke=GRAY_MID, sw=0.8)

    svg.text(450, t1_y + 114, "Every reachable combination 12x + 8y lands on a purple dot, and every purple dot has a witness (x, y).", size=12, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    # --- TRACK 2: TYPE ERROR A: Candidate g = 8 (Too Coarse -> Off-Grid Collision) ---
    t2_y = 228
    svg.rect(25, t2_y, 850, 195, fill=BG, stroke=RED, sw=2.0, rx=8)
    svg.rect(38, t2_y + 12, 245, 25, fill=RED, stroke="none", rx=4)
    svg.text(160.5, t2_y + 29, "TYPE ERROR 1:  Candidate g = 8", size=12.5, font=FONT_SANS, fill=BG, anchor="middle", weight="bold")
    svg.text(298, t2_y + 29, "Grid 8ℤ is TOO COARSE — fails inclusion  12ℤ + 8ℤ ⊆ 8ℤ  (8 does not divide 12)", size=13.5, font=FONT_SERIF, fill=RED, weight="bold")

    y_line2 = t2_y + 104
    svg.line(x_left - 10, y_line2, x_right + 10, y_line2, stroke=INK, sw=2)

    for k in range(-1, 3):
        n_grid = k * 8
        xg = nx(n_grid)
        draw_step_bracket(svg, xg + 3, nx((k + 1) * 8) - 3, y_line2 + 26, "candidate step g = 8" if k == 0 else "step 8", color=GRAY_DARK, up=False)

    for n in range(n_min, n_max + 1):
        x = nx(n)
        in_actual = (n % 4 == 0)
        in_cand = (n % 8 == 0)

        if in_actual and in_cand:
            svg.circle(x, y_line2, 6, fill=NAVY, stroke=BG, sw=1.2)
            svg.text(x, y_line2 + 20, str(n), size=12, font=FONT_SERIF, fill=NAVY, anchor="middle", weight="bold")
        elif in_actual and not in_cand:
            svg.circle(x, y_line2, 10, fill=RED_FILL, stroke=RED, sw=2.2)
            svg.line(x - 5, y_line2 - 5, x + 5, y_line2 + 5, stroke=RED, sw=2.2)
            svg.line(x - 5, y_line2 + 5, x + 5, y_line2 - 5, stroke=RED, sw=2.2)
            svg.text(x, y_line2 + 21, str(n), size=12, font=FONT_SERIF, fill=RED, anchor="middle", weight="bold")

            lbl = "a = 12 OFF GRID!" if n == 12 else ("12(1)−8(1)=4 OFF GRID!" if n == 4 else "off 8ℤ")
            w_box = 140 if n in (4, 12) else 56
            svg.rect(x - w_box/2, y_line2 - 52, w_box, 22, fill=RED_FILL, stroke=RED, sw=1.2, rx=4)
            svg.line(x, y_line2 - 30, x, y_line2 - 12, stroke=RED, sw=1.5, marker_end="arrow-red")
            svg.text(x, y_line2 - 37, lbl, size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")
        else:
            svg.line(x, y_line2 - 2.5, x, y_line2 + 2.5, stroke=GRAY_LIGHT, sw=0.8)

    svg.text(450, t2_y + 181, "Counterexample witness: (x, y) = (1, 0) gives 12 ∈ 12ℤ+8ℤ, and (1, −1) gives 4 ∈ 12ℤ+8ℤ, but neither lies in 8ℤ!",
             size=12, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")

    # --- TRACK 3: TYPE ERROR B: Candidate g = 2 (Too Fine -> Unreachable Ghost Points) ---
    t3_y = 437
    svg.rect(25, t3_y, 850, 195, fill=BG, stroke=RED, sw=2.0, rx=8)
    svg.rect(38, t3_y + 12, 245, 25, fill=RED, stroke="none", rx=4)
    svg.text(160.5, t3_y + 29, "TYPE ERROR 2:  Candidate g = 2", size=12.5, font=FONT_SANS, fill=BG, anchor="middle", weight="bold")
    svg.text(298, t3_y + 29, "Grid 2ℤ is TOO FINE — fails reachability  2ℤ ⊆ 12ℤ + 8ℤ  (no x, y gives 12x + 8y = 2)", size=13.5, font=FONT_SERIF, fill=RED, weight="bold")

    y_line3 = t3_y + 104
    svg.line(x_left - 10, y_line3, x_right + 10, y_line3, stroke=INK, sw=2)

    ghost_callouts = {
        -6: ("ghost −6", 64),
        2:  ("GHOST: 12x+8y = 2 impossible!", 176),
        10: ("unreachable ghost 10", 118),
        18: ("unreachable ghost 18", 118),
    }

    for n in range(n_min, n_max + 1):
        x = nx(n)
        in_actual = (n % 4 == 0)
        in_cand = (n % 2 == 0)

        if in_actual and in_cand:
            svg.circle(x, y_line3, 5.5, fill=PURPLE, stroke=BG, sw=1.2)
            svg.text(x, y_line3 + 20, str(n), size=11.5, font=FONT_SERIF, fill=INK, anchor="middle", weight="bold")
        elif in_cand and not in_actual:
            svg.circle(x, y_line3, 8.5, fill=RED_FILL, stroke=RED, sw=2.0, dash="2.5,2")
            svg.text(x, y_line3 + 4, "?", size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")
            svg.text(x, y_line3 + 21, str(n), size=11.5, font=FONT_SERIF, fill=RED, anchor="middle", weight="bold")

            if n in ghost_callouts:
                lbl, w_box = ghost_callouts[n]
                svg.rect(x - w_box/2, y_line3 - 52, w_box, 22, fill=RED_FILL, stroke=RED, sw=1.2, rx=4)
                svg.line(x, y_line3 - 30, x, y_line3 - 11, stroke=RED, sw=1.5, marker_end="arrow-red")
                svg.text(x, y_line3 - 37, lbl, size=11, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")
        else:
            svg.line(x, y_line3 - 2, x, y_line3 + 2, stroke=GRAY_LIGHT, sw=0.8)

    draw_step_bracket(svg, nx(0) + 2, nx(2) - 2, y_line3 + 26, "step 2", color=RED, up=False)
    draw_step_bracket(svg, nx(2) + 2, nx(4) - 2, y_line3 + 26, "step 2", color=RED, up=False)

    svg.text(450, t3_y + 181, "Although 2 divides 12 and 8, every combination 12x + 8y = 4(3x + 2y) is a multiple of 4 — leaving all odd multiples of 2 as unreachable ghosts!",
             size=12, font=FONT_SANS, fill=RED, anchor="middle", weight="bold")

    svg.save("fig-4.svg")
    print("Generated fig-4.svg")


# =============================================================================
# FIGURE 5: Equivalence of Divisor & Ideal Characterizations + Edge Cases + Codillon View
# =============================================================================
def generate_fig5():
    svg = SVGBuilder(width=900, height=635)
    svg.add_standard_markers()

    # Title <= 12 words (11 words)
    draw_header(
        svg,
        "Subtyping is ideal containment; boundary inputs (21, 0) and (0, 0) follow",
        'Order-reversing duality: <tspan font-style="italic">d</tspan> divides <tspan font-style="italic">n</tspan>  ⇔  <tspan font-style="italic">n</tspan>ℤ ⊆ <tspan font-style="italic">d</tspan>ℤ, so greatest common divisor is the smallest enclosing ideal.',
        tag="FIG 5 · DUALITY & CODILLON"
    )

    # --- TOP LEFT PANEL: Order-Reversing Duality Diagram for (12, 8) ---
    tl_x, tl_y, tl_w, tl_h = 25, 86, 485, 302
    svg.rect(tl_x, tl_y, tl_w, tl_h, fill=BG, stroke=PURPLE, sw=1.5, rx=8)
    svg.text(tl_x + 16, tl_y + 24, "1. Duality: Divisors vs. Principal Ideals for (12, 8)", size=14.5, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(tl_x + 16, tl_y + 42, "d | a ∧ d | b   ⇔   aℤ ⊆ dℤ ∧ bℤ ⊆ dℤ   ⇔   (aℤ + bℤ) ⊆ dℤ", size=12, font=FONT_SERIF, fill=PURPLE, weight="bold")

    col_d_x = tl_x + 92
    col_i_x = tl_x + 335

    svg.text(col_d_x, tl_y + 66, "Common Divisors d", size=12, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
    svg.text(col_d_x, tl_y + 80, "(ordered by divisibility d₁ | d₂)", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    svg.text(col_i_x, tl_y + 66, "Enclosing Ideals dℤ", size=12, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")
    svg.text(col_i_x, tl_y + 80, "(ordered by set inclusion ⊇)", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle")

    levels = [
        (4, "d = 4  (GREATEST)", "4ℤ = {0, ±4, ±8, ±12, …}", "TIGHTEST FIT: 12ℤ + 8ℤ = 4ℤ", True),
        (2, "d = 2  (common div)", "2ℤ = {0, ±2, ±4, ±6, …}", "Strictly larger: 4ℤ ⊂ 2ℤ", False),
        (1, "d = 1  (unit div)",   "1ℤ = ℤ = {0, ±1, ±2, …}", "Largest: 4ℤ ⊂ 2ℤ ⊂ 1ℤ", False),
    ]

    for idx, (d_val, d_lbl, i_lbl, note, is_top) in enumerate(levels):
        ly = tl_y + 112 + idx * 60
        svg.rect(col_d_x - 72, ly - 16, 144, 34,
                 fill=PURPLE_FILL if is_top else BG,
                 stroke=PURPLE if is_top else GRAY_MID, sw=2.0 if is_top else 1.2, rx=5)
        svg.text(col_d_x, ly + 5, d_lbl, size=11.5, font=FONT_SANS,
                 fill=PURPLE if is_top else INK, anchor="middle", weight="bold" if is_top else "normal")

        svg.line(col_d_x + 78, ly, col_i_x - 118, ly, stroke=PURPLE if is_top else GRAY_MID, sw=1.5,
                 marker_start="arrow-purple" if is_top else "arrow-gray",
                 marker_end="arrow-purple" if is_top else "arrow-gray")
        svg.text((col_d_x + 78 + col_i_x - 118)/2, ly - 5, "⇔", size=12, font=FONT_SERIF, fill=PURPLE if is_top else GRAY_DARK, anchor="middle")

        svg.rect(col_i_x - 112, ly - 18, 240, 38,
                 fill=PURPLE_FILL if is_top else BG,
                 stroke=PURPLE if is_top else GRAY_MID, sw=2.0 if is_top else 1.2, rx=5)
        svg.text(col_i_x + 8, ly - 2, i_lbl, size=12, font=FONT_SERIF,
                 fill=PURPLE if is_top else INK, anchor="middle", weight="bold")
        svg.text(col_i_x + 8, ly + 14, note, size=11, font=FONT_SANS,
                 fill=NAVY if is_top else GRAY_DARK, anchor="middle", weight="bold" if is_top else "normal")

        if idx < 2:
            mid_y = ly + 30
            svg.text(col_d_x, mid_y + 4, "∣  (divides ↑)", size=11, font=FONT_SANS, fill=GRAY_DARK, anchor="middle", weight="bold")
            svg.text(col_i_x + 8, mid_y + 4, "⊂  (subset of ↓)", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")

    svg.rect(tl_x + 12, tl_y + 262, tl_w - 24, 28, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1, rx=4)
    svg.text(tl_x + tl_w/2, tl_y + 280, "Inputs: 12ℤ ⊂ 4ℤ and 8ℤ ⊂ 4ℤ  ⇒  Smallest ideal containing both is 12ℤ + 8ℤ = 4ℤ.",
             size=11.5, font=FONT_SANS, fill=INK, anchor="middle", weight="bold")

    # --- TOP RIGHT PANEL: Boundary Cases (21, 0) -> 21 and (0, 0) -> 0 ---
    tr_x, tr_y, tr_w, tr_h = 525, 86, 350, 302
    svg.rect(tr_x, tr_y, tr_w, tr_h, fill=BG, stroke=NAVY, sw=1.5, rx=8)
    svg.text(tr_x + 16, tr_y + 24, "2. Boundary Cases (Zero Inputs)", size=14.5, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(tr_x + 16, tr_y + 42, "Since 0·y = 0, the ideal 0ℤ is just the singleton {0}:", size=12, font=FONT_SANS, fill=GRAY_DARK)

    # Case 1: (21, 0) -> 21Z + 0Z = 21Z
    c1_y = tr_y + 56
    svg.rect(tr_x + 14, c1_y, tr_w - 28, 108, fill=PURPLE_LIGHT, stroke=PURPLE, sw=1.2, rx=6)
    svg.text(tr_x + 24, c1_y + 20, "Euclid Stopping State:  a = 21,  b = 0", size=13, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(tr_x + 24, c1_y + 38, "21ℤ + 0ℤ = 21ℤ + {0} = 21ℤ   ⇒   Gcd(21, 0) = { 21 }", size=12, font=FONT_SERIF, fill=PURPLE, weight="bold")

    ml1_y = c1_y + 66
    ml_x1, ml_x2 = tr_x + 36, tr_x + tr_w - 36
    svg.line(ml_x1, ml1_y, ml_x2, ml1_y, stroke=INK, sw=1.8)
    for idx_m, v in enumerate([-21, 0, 21, 42, 63]):
        mx = ml_x1 + idx_m * (ml_x2 - ml_x1) / 4.0
        is_g = (v == 21)
        svg.circle(mx, ml1_y, 7 if is_g else 4.5, fill=PURPLE if is_g else NAVY, stroke=BG, sw=1.2)
        svg.text(mx, ml1_y + 18, str(v), size=11, font=FONT_SANS, fill=PURPLE if is_g else INK, anchor="middle", weight="bold" if is_g else "normal")
    svg.text((ml_x1 + ml_x2)/2, c1_y + 100, "When y = 0, returning x = 21 immediately inhabits Gcd(a, b)!", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

    # Case 2: (0, 0) -> 0Z + 0Z = {0}
    c2_y = tr_y + 176
    svg.rect(tr_x + 14, c2_y, tr_w - 28, 112, fill=BG, stroke=GRAY_MID, sw=1.2, rx=6)
    svg.text(tr_x + 24, c2_y + 20, "Degenerate Collapse:  a = 0,  b = 0", size=13, font=FONT_SERIF, fill=INK, weight="bold")
    svg.text(tr_x + 24, c2_y + 38, "0ℤ + 0ℤ = {0} = 0ℤ   ⇒   Gcd(0, 0) = { 0 }", size=12, font=FONT_SERIF, fill=NAVY, weight="bold")

    ml2_y = c2_y + 66
    svg.line(ml_x1, ml2_y, ml_x2, ml2_y, stroke=GRAY_LIGHT, sw=1.8, dash="3,3")
    for idx_m, v in enumerate([-2, -1, 0, 1, 2]):
        mx = ml_x1 + idx_m * (ml_x2 - ml_x1) / 4.0
        if v == 0:
            svg.circle(mx, ml2_y, 8, fill=PURPLE_FILL, stroke=PURPLE, sw=2)
            svg.circle(mx, ml2_y, 4.5, fill=NAVY)
            svg.text(mx, ml2_y + 19, "g = 0 (only point!)", size=11, font=FONT_SANS, fill=PURPLE, anchor="middle", weight="bold")
        else:
            svg.circle(mx, ml2_y, 2.5, fill=GRAY_LIGHT)
            svg.text(mx, ml2_y + 18, str(v), size=11, font=FONT_SANS, fill=GRAY_MID, anchor="middle")
    svg.text((ml_x1 + ml_x2)/2, c2_y + 102, "General rule: g ∈ ℕ is the unique generator of aℤ+bℤ = gℤ.", size=11, font=FONT_SANS, fill=INK, anchor="middle")

    # --- BOTTOM PANEL: Codillon Per-Instruction Live Inspector Mockup ---
    bp_x, bp_y, bp_w, bp_h = 25, 404, 850, 212
    svg.rect(bp_x, bp_y, bp_w, bp_h, fill=BG, stroke=INK, sw=1.8, rx=8)
    svg.rect(bp_x, bp_y, bp_w, 30, fill=INK, stroke="none", rx=6)
    svg.text(bp_x + 16, bp_y + 20, "3. Codillon Structured Wasm Editor — Per-Instruction Refinement & Ideal Strip", size=13.5, font=FONT_SANS, fill=BG, weight="bold")
    svg.text(bp_x + bp_w - 16, bp_y + 20, "fn euclid(a: ℕ = 12, b: ℕ = 8) → { g : ℕ | gℤ = aℤ + bℤ }", size=12, font=FONT_SERIF, fill=PURPLE_FILL, anchor="end", weight="bold")

    rows = [
        ("loop entry",    "x = 12,  y = 8",  "12ℤ + 8ℤ = 4ℤ",  "x = 1(12)+0(8),  y = 0(12)+1(8)", 12, 8, False),
        ("step: x mod y", "x' = 8,  y' = 4", "8ℤ + 4ℤ = 4ℤ",   "y' = 1(12) − 1(8) = 4  (invariant!)", 8, 4, False),
        ("exit: y == 0",  "x'' = 4, y'' = 0","4ℤ + 0ℤ = 4ℤ",   "return x'' = 4  (inhabits Gcd(12, 8))", 4, 0, True),
    ]

    for r_idx, (instr, state_str, ideal_str, proof_str, xv, yv, is_ret) in enumerate(rows):
        ry = bp_y + 42 + r_idx * 54
        svg.rect(bp_x + 12, ry, bp_w - 24, 48, fill=PURPLE_LIGHT if is_ret else BG,
                 stroke=PURPLE if is_ret else GRAY_LIGHT, sw=1.6 if is_ret else 1.0, rx=5)

        svg.rect(bp_x + 20, ry + 9, 108, 30, fill=PURPLE if is_ret else NAVY, stroke="none", rx=4)
        svg.text(bp_x + 74, ry + 28, instr, size=12, font=FONT_SANS, fill=BG, anchor="middle", weight="bold")

        svg.text(bp_x + 140, ry + 21, state_str, size=12.5, font=FONT_SERIF, fill=NAVY, weight="bold")
        svg.text(bp_x + 140, ry + 38, f"Ideal: {ideal_str}", size=11.5, font=FONT_SANS, fill=PURPLE, weight="bold")

        strip_x1, strip_x2 = bp_x + 305, bp_x + 545
        strip_y = ry + 25
        svg.line(strip_x1, strip_y, strip_x2, strip_y, stroke=INK, sw=1.5)
        for v_tick in [0, 4, 8, 12]:
            tx_pos = strip_x1 + (v_tick / 12.0) * (strip_x2 - strip_x1)
            is_active_x = (v_tick == xv)
            is_active_y = (v_tick == yv)
            if v_tick == 4 and is_ret:
                svg.circle(tx_pos, strip_y, 7.5, fill=PURPLE_FILL, stroke=PURPLE, sw=2)
                svg.circle(tx_pos, strip_y, 4, fill=PURPLE)
            elif is_active_x or is_active_y:
                svg.circle(tx_pos, strip_y, 6, fill=NAVY, stroke=BG, sw=1)
            else:
                svg.circle(tx_pos, strip_y, 4, fill=PURPLE_FILL, stroke=PURPLE, sw=1)
            svg.text(tx_pos, strip_y + 17, str(v_tick), size=11, font=FONT_SANS, fill=INK, anchor="middle")
            if is_active_x and is_active_y:
                svg.text(tx_pos, strip_y - 9, "x,y", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
            elif is_active_x:
                svg.text(tx_pos, strip_y - 9, "x", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")
            elif is_active_y:
                svg.text(tx_pos, strip_y - 9, "y", size=11, font=FONT_SANS, fill=NAVY, anchor="middle", weight="bold")

        svg.text(bp_x + 568, ry + 28, proof_str, size=12, font=FONT_SANS,
                 fill=PURPLE if is_ret else INK, weight="bold" if is_ret else "normal")

    svg.save("fig-5.svg")
    print("Generated fig-5.svg")


if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    generate_fig5()
