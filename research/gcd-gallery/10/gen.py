#!/usr/bin/env python3
"""
gen.py - Generate 5 standalone SVG figures visualizing 'gcd(a, b) as a type'
in Codillon's Editor Idiom (Angle 10 of 10).
"""

import math

# Palette strictly adhering to rules (NO GREEN ANYWHERE)
BG = "#fffff0"          # ivory background
INK = "#222222"         # primary ink
GRAY_DARK = "#555555"   # secondary labels
GRAY_MID = "#888888"    # subtle lines / ticks
GRAY_LIGHT = "#d8d8d0"  # subtle rules / grid
GRAY_FAINT = "#f2f2e6"  # code row shading
PURPLE = "#6A5ACD"      # type / region border & sockets
PURPLE_FILL = "#d9d5f2" # admitted region fill / dataflow ribbons
INDIGO = "#4b0082"      # symbolic / unknown / tether
NAVY = "#00008b"        # concrete run / value
RED = "#8b0000"         # type error / violation ONLY
RED_FILL = "#f5d6d6"    # soft error highlight (derived from #8b0000)

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"
FONT_MONO = "'Courier New', Courier, monospace"

INT_MIN = -2147483648
INT_MAX = 2147483647

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def divisors(n, cap=24):
    """Compute exact positive divisors of n. If n == 0, returns list up to cap."""
    n = abs(int(n))
    if n == 0:
        return list(range(1, cap + 1))
    return [d for d in range(1, n + 1) if n % d == 0]

def gcd_val(a, b):
    return math.gcd(int(a), int(b))

def common_divisors(a, b, cap=24):
    return divisors(gcd_val(a, b), cap=cap)

def nl_frac(v):
    """
    Map an i32 value v in [INT_MIN, INT_MAX] to [0.0, 1.0] along a refined i32 shape:
    - Middle 60% ([0.20, 0.80]) is linear for |v| <= 8.
    - Outer 20% on each side ([0.0, 0.20] and [0.80, 1.0]) is logarithmic from 8 to INT_MAX / -INT_MIN.
    """
    if v < INT_MIN:
        v = INT_MIN
    if v > INT_MAX:
        v = INT_MAX
    if abs(v) <= 8:
        return 0.50 + 0.30 * (v / 8.0)
    elif v > 8:
        ratio = math.log(v / 8.0) / math.log(INT_MAX / 8.0)
        return 0.80 + 0.20 * ratio
    else:
        ratio = math.log(abs(v) / 8.0) / math.log(abs(INT_MIN) / 8.0)
        return 0.20 - 0.20 * ratio

def nl_x(v, x0, w):
    return x0 + w * nl_frac(v)

def svg_header(width, height, title_text, subtitle_text=""):
    defs = f"""  <defs>
    <pattern id="err-hatch" width="6" height="6" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
      <rect width="6" height="6" fill="{RED_FILL}" fill-opacity="0.72"/>
      <line x1="0" y1="0" x2="0" y2="6" stroke="{RED}" stroke-width="2.2"/>
    </pattern>
    <marker id="arrow-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{INK}"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{PURPLE}"/>
    </marker>
    <marker id="arrow-indigo" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{INDIGO}"/>
    </marker>
    <marker id="arrow-navy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{NAVY}"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{RED}"/>
    </marker>
  </defs>"""
    sub_svg = ""
    if subtitle_text:
        sub_svg = f'\n  <text x="28" y="54" font-family="{FONT_SANS}" font-size="13" fill="{GRAY_DARK}">{esc(subtitle_text)}</text>'
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{defs}
  <rect x="0" y="0" width="{width}" height="{height}" fill="{BG}"/>
  <text x="28" y="34" font-family="{FONT_SERIF}" font-size="20" font-weight="bold" fill="{INK}">{esc(title_text)}</text>{sub_svg}
  <line x1="28" y1="64" x2="{width-28}" y2="64" stroke="{GRAY_LIGHT}" stroke-width="1"/>
"""

def svg_footer():
    return "</svg>\n"

def draw_unrefined_shape(x, y, w=30, h=11, is_cup=False, val=None, label=None):
    """Draw standard Codillon unrefined i32 shape (30x11)."""
    out = []
    if is_cup:
        out.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{BG}" stroke="none"/>')
        out.append(f'  <path d="M {x:.1f} {y:.1f} L {x:.1f} {y+h:.1f} L {x+w:.1f} {y+h:.1f} L {x+w:.1f} {y:.1f}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    else:
        out.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="1.5"/>')
    if val is not None:
        out.append(f'  <text x="{x+w/2:.1f}" y="{y+h-2:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">{val}</text>')
    if label:
        out.append(f'  <text x="{x+w/2:.1f}" y="{y-4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{label}</text>')
    return "\n".join(out)

def draw_refined_nl(x, y, w=84, h=14, is_cup=False, region=None, sockets=None,
                    active_socket=None, concrete_val=None, spill_val=None,
                    show_scale=False, rim_Color=PURPLE):
    """
    Draw a refined i32 shape (default 84x14, or scaled up for close-ups).
    region: tuple (v_min, v_max) to shade as admitted interval, or 'all'
    sockets: list of integer values to draw as small divisor marks/notches
    active_socket: single integer value for the exact singleton socket {g}
    concrete_val: integer value seated inside the shape (navy bead/bar)
    spill_val: integer value that violates the refinement (draws red hatch spill over the rim!)
    """
    out = []
    # Base background
    out.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{BG}" stroke="none"/>')

    # Admitted interval shading
    if region == "all":
        out.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PURPLE_FILL}" fill-opacity="0.75"/>')
    elif isinstance(region, tuple):
        rx1 = nl_x(region[0], x, w)
        rx2 = nl_x(region[1], x, w)
        rw = max(2.0, rx2 - rx1)
        out.append(f'  <rect x="{rx1:.1f}" y="{y:.1f}" width="{rw:.1f}" height="{h:.1f}" fill="{PURPLE_FILL}" fill-opacity="0.85"/>')
        out.append(f'  <line x1="{rx1:.1f}" y1="{y:.1f}" x2="{rx1:.1f}" y2="{y+h:.1f}" stroke="{PURPLE}" stroke-width="1.2"/>')
        out.append(f'  <line x1="{rx2:.1f}" y1="{y:.1f}" x2="{rx2:.1f}" y2="{y+h:.1f}" stroke="{PURPLE}" stroke-width="1.2"/>')

    # Zone boundary hairlines (-8 and +8 at 20% and 80%, 0 at 50%)
    x_m8 = x + 0.20 * w
    x_zero = x + 0.50 * w
    x_p8 = x + 0.80 * w
    out.append(f'  <line x1="{x_m8:.1f}" y1="{y:.1f}" x2="{x_m8:.1f}" y2="{y+h:.1f}" stroke="{GRAY_LIGHT}" stroke-width="0.9" stroke-dasharray="2,2"/>')
    out.append(f'  <line x1="{x_p8:.1f}" y1="{y:.1f}" x2="{x_p8:.1f}" y2="{y+h:.1f}" stroke="{GRAY_LIGHT}" stroke-width="0.9" stroke-dasharray="2,2"/>')
    out.append(f'  <line x1="{x_zero:.1f}" y1="{y:.1f}" x2="{x_zero:.1f}" y2="{y+h:.1f}" stroke="{GRAY_MID}" stroke-width="1.0"/>')

    # Candidate / divisor notches (if sockets provided)
    if sockets:
        for s in sockets:
            sx = nl_x(s, x, w)
            sw = max(2.4, w * 0.018)
            out.append(f'  <rect x="{sx - sw/2:.1f}" y="{y+1:.1f}" width="{sw:.1f}" height="{h-2:.1f}" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="0.9"/>')

    # Singleton socket (e.g., Gcd(a,b) result socket)
    if active_socket is not None:
        sx = nl_x(active_socket, x, w)
        sw = max(5.0, w * 0.032)
        out.append(f'  <rect x="{sx - sw/2:.1f}" y="{y:.1f}" width="{sw:.1f}" height="{h:.1f}" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="1.8"/>')
        if is_cup:
            out.append(f'  <path d="M {sx - sw/2 - 2:.1f} {y-2:.1f} L {sx - sw/2:.1f} {y:.1f} L {sx - sw/2:.1f} {y+h:.1f} L {sx + sw/2:.1f} {y+h:.1f} L {sx + sw/2:.1f} {y:.1f} L {sx + sw/2 + 2:.1f} {y-2:.1f}" fill="none" stroke="{PURPLE}" stroke-width="1.8"/>')

    # Concrete value seated inside
    if concrete_val is not None:
        vx = nl_x(concrete_val, x, w)
        r = max(2.8, min(6.5, h * 0.34))
        out.append(f'  <line x1="{vx:.1f}" y1="{y:.1f}" x2="{vx:.1f}" y2="{y+h:.1f}" stroke="{NAVY}" stroke-width="2.0"/>')
        out.append(f'  <circle cx="{vx:.1f}" cy="{y+h/2:.1f}" r="{r:.1f}" fill="{NAVY}" stroke="{BG}" stroke-width="1.0"/>')

    # Outer rim: cup (open top) or output block (closed box)
    border_col = RED if spill_val is not None else rim_Color
    if is_cup:
        out.append(f'  <path d="M {x:.1f} {y-2:.1f} L {x:.1f} {y+h:.1f} L {x+w:.1f} {y+h:.1f} L {x+w:.1f} {y-2:.1f}" fill="none" stroke="{border_col}" stroke-width="1.8"/>')
    else:
        out.append(f'  <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{border_col}" stroke-width="1.8"/>')

    # Spill effect (dark-red hatch over the rim!)
    if spill_val is not None:
        vx = nl_x(spill_val, x, w)
        sw = max(14.0, w * 0.075)
        sh = max(10.0, h * 0.72)
        out.append(f'  <path d="M {vx - sw*0.7:.1f} {y+2:.1f} C {vx - sw*0.9:.1f} {y - sh:.1f}, {vx + sw*0.9:.1f} {y - sh:.1f}, {vx + sw*0.7:.1f} {y+2:.1f} L {vx + sw*0.45:.1f} {y+h-2:.1f} L {vx - sw*0.45:.1f} {y+h-2:.1f} Z" fill="url(#err-hatch)" stroke="{RED}" stroke-width="1.6"/>')
        out.append(f'  <circle cx="{vx:.1f}" cy="{y - sh*0.35:.1f}" r="{max(3.2, min(6.0, h*0.3)):.1f}" fill="{RED}" stroke="{BG}" stroke-width="1.0"/>')

    # Scale labels if requested (adapts label wording to width so it never overlaps!)
    if show_scale:
        ty = y + h + 13
        min_lbl = "INT_MIN" if w >= 300 else "MIN"
        max_lbl = "INT_MAX" if w >= 300 else "MAX"
        out.append(f'  <text x="{x:.1f}" y="{ty:.1f}" text-anchor="start" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{min_lbl}</text>')
        out.append(f'  <text x="{x_m8:.1f}" y="{ty:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">-8</text>')
        out.append(f'  <text x="{x_zero:.1f}" y="{ty:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{INK}">0</text>')
        out.append(f'  <text x="{x_p8:.1f}" y="{ty:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">+8</text>')
        out.append(f'  <text x="{x+w:.1f}" y="{ty:.1f}" text-anchor="end" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{max_lbl}</text>')

    return "\n".join(out)

def draw_ribbon(x1, y1, w1, x2, y2, w2, color=PURPLE_FILL, stroke=PURPLE, opacity=0.55):
    """Draw a smooth pale-lavender dataflow ribbon from output shape (x1,y1,w1) to input cup (x2,y2,w2)."""
    ym = (y1 + y2) / 2.0
    path = (f"M {x1:.1f} {y1:.1f} "
            f"C {x1:.1f} {ym:.1f}, {x2:.1f} {ym:.1f}, {x2:.1f} {y2:.1f} "
            f"L {x2+w2:.1f} {y2:.1f} "
            f"C {x2+w2:.1f} {ym:.1f}, {x1+w1:.1f} {ym:.1f}, {x1+w1:.1f} {y1:.1f} Z")
    return f'  <path d="{path}" fill="{color}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="0.9" stroke-opacity="0.7"/>'


# ============================================================================
# FIGURE 1: Vocabulary & Scale — Unrefined vs Refined i32, Seating vs Spill,
# and Dependent Result Cup Gcd(a, b)
# ============================================================================
def generate_fig1():
    W, H = 900, 560
    out = [svg_header(
        W, H,
        "Refined Stack Fractions: From Flat i32 Boxes to Dependent Number-Line Cups",
        "Codillon draws each instruction's stack effect as inputs above a bar and outputs below; refinements turn 30×11 boxes into 84×14 number lines."
    )]

    # --- TOP PANEL: 3-column comparison of Codillon stack fractions ---
    out.append(f'  <rect x="28" y="78" width="844" height="190" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')
    out.append(f'  <text x="44" y="100" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">1. Codillon Stack-Fraction Idiom (1:1 Editor Scale vs. Refined Number-Line Scale)</text>')

    # Column A: Unrefined i32.rem_u
    cx1 = 155
    out.append(f'  <text x="{cx1}" y="124" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">A. Unrefined i32 (30×11 px)</text>')
    out.append(f'  <text x="{cx1}" y="141" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">Any 32-bit int fits; 0 divisor undetected</text>')
    out.append(draw_unrefined_shape(cx1 - 36, 165, 30, 11, is_cup=True, val="12", label="a"))
    out.append(draw_unrefined_shape(cx1 + 6, 165, 30, 11, is_cup=True, val="8", label="b"))
    out.append(f'  <line x1="{cx1-46}" y1="181" x2="{cx1+46}" y2="181" stroke="{INK}" stroke-width="2.0"/>')
    out.append(draw_unrefined_shape(cx1 - 15, 186, 30, 11, is_cup=False, val="4"))
    out.append(f'  <text x="{cx1+56}" y="185" font-family="{FONT_MONO}" font-size="13" font-weight="bold" fill="{INK}">i32.rem_u</text>')
    out.append(f'  <text x="{cx1}" y="222" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">Open-top cups = inputs consumed</text>')
    out.append(f'  <text x="{cx1}" y="238" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">Solid box = output produced</text>')

    # Divider
    out.append(f'  <line x1="305" y1="112" x2="305" y2="254" stroke="{GRAY_LIGHT}" stroke-width="1"/>')

    # Column B: Refined i32 (84x14) with valid seating
    cx2 = 455
    out.append(f'  <text x="{cx2}" y="124" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">B. Refined i32 (84×14 px) — Valid Seat</text>')
    out.append(f'  <text x="{cx2}" y="141" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">Divisor cup requires {{y ∈ i32 | y ≥ 1}}</text>')
    out.append(draw_refined_nl(cx2 - 90, 162, 84, 14, is_cup=True, region=(0, INT_MAX), concrete_val=12))
    out.append(draw_refined_nl(cx2 + 6, 162, 84, 14, is_cup=True, region=(1, INT_MAX), concrete_val=8))
    out.append(f'  <text x="{cx2-48}" y="156" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">x = 12 ∈ [0, MAX]</text>')
    out.append(f'  <text x="{cx2+48}" y="156" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">y = 8 ∈ [1, MAX]</text>')
    out.append(f'  <line x1="{cx2-98}" y1="181" x2="{cx2+98}" y2="181" stroke="{INK}" stroke-width="2.0"/>')
    out.append(draw_refined_nl(cx2 - 42, 186, 84, 14, is_cup=False, region=(0, 7), concrete_val=4))
    out.append(f'  <text x="{cx2}" y="218" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{NAVY}">Result 4 seats inside shaded [0, y−1]</text>')
    out.append(f'  <text x="{cx2}" y="236" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">Purple region = admitted subset of i32</text>')

    # Divider
    out.append(f'  <line x1="605" y1="112" x2="605" y2="254" stroke="{GRAY_LIGHT}" stroke-width="1"/>')

    # Column C: Refined i32 with SPILL (violation)
    cx3 = 740
    out.append(f'  <text x="{cx3}" y="124" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{RED}">C. Out-of-Region Value SPILLS</text>')
    out.append(f'  <text x="{cx3}" y="141" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{RED}">Passing y = 0 into {{y ∈ i32 | y ≥ 1}}</text>')
    out.append(draw_refined_nl(cx3 - 42, 168, 84, 14, is_cup=True, region=(1, INT_MAX), spill_val=0))
    out.append(f'  <line x1="{cx3-52}" y1="187" x2="{cx3+52}" y2="187" stroke="{RED}" stroke-width="2.0"/>')
    out.append(f'  <text x="{cx3}" y="215" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED}">y = 0 lands outside [1, INT_MAX]</text>')
    out.append(f'  <text x="{cx3}" y="233" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{RED}">Dark-red hatch spills over cup rim!</text>')

    # --- BOTTOM PANEL: Close-up of the Hybrid Log-Linear Number Line & Dependent Gcd(a,b) Socket ---
    out.append(f'  <rect x="28" y="282" width="844" height="258" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')
    out.append(f'  <text x="44" y="305" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">2. Magnified Anatomy of a Dependent Result Cup: Gcd(a, b) = {{ g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }}</text>')

    # Parameter shapes a = 12 and b = 8 at top of bottom panel
    pa_x, pa_y, pw, ph = 165, 336, 195, 20
    pb_x, pb_y = 545, 336
    out.append(f'  <text x="{pa_x - 10}" y="{pa_y + 14}" text-anchor="end" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">param $a = 12</text>')
    out.append(draw_refined_nl(pa_x, pa_y, pw, ph, is_cup=False, region=(0, INT_MAX), sockets=divisors(12), concrete_val=12))
    out.append(f'  <text x="{pa_x + pw/2}" y="{pa_y - 6}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{PURPLE}">Div(12) = {{1, 2, 3, 4, 6, 12}}</text>')

    out.append(f'  <text x="{pb_x - 10}" y="{pb_y + 14}" text-anchor="end" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">param $b = 8</text>')
    out.append(draw_refined_nl(pb_x, pb_y, pw, ph, is_cup=False, region=(0, INT_MAX), sockets=divisors(8), concrete_val=8))
    out.append(f'  <text x="{pb_x + pw/2}" y="{pb_y - 6}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{PURPLE}">Div(8) = {{1, 2, 4, 8}}</text>')

    # Magnified 520x32 Result Cup in center-bottom
    rc_x, rc_y, rc_w, rc_h = 190, 434, 520, 34
    out.append(draw_refined_nl(rc_x, rc_y, rc_w, rc_h, is_cup=True, sockets=[1, 2], active_socket=4, concrete_val=4, show_scale=True))

    # Zone bracket annotations below the magnified cup
    by = rc_y + rc_h + 26
    x_20 = rc_x + 0.20 * rc_w
    x_80 = rc_x + 0.80 * rc_w
    out.append(f'  <line x1="{rc_x}" y1="{by}" x2="{x_20-3}" y2="{by}" stroke="{GRAY_MID}" stroke-width="1.2" marker-start="url(#arrow-ink)" marker-end="url(#arrow-ink)"/>')
    out.append(f'  <text x="{(rc_x+x_20)/2:.1f}" y="{by+14}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">20% log [INT_MIN, −8]</text>')

    out.append(f'  <line x1="{x_20+3}" y1="{by}" x2="{x_80-3}" y2="{by}" stroke="{PURPLE}" stroke-width="1.5" marker-start="url(#arrow-purple)" marker-end="url(#arrow-purple)"/>')
    out.append(f'  <text x="{(x_20+x_80)/2:.1f}" y="{by+14}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE}">60% linear scale |v| ≤ 8 (exact integer ticks)</text>')

    out.append(f'  <line x1="{x_80+3}" y1="{by}" x2="{rc_x+rc_w}" y2="{by}" stroke="{GRAY_MID}" stroke-width="1.2" marker-start="url(#arrow-ink)" marker-end="url(#arrow-ink)"/>')
    out.append(f'  <text x="{(x_80+rc_x+rc_w)/2:.1f}" y="{by+14}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">20% log [+8, INT_MAX]</text>')

    # Integer ticks inside the linear zone
    for v in range(-8, 9):
        tx = nl_x(v, rc_x, rc_w)
        out.append(f'  <line x1="{tx:.1f}" y1="{rc_y+rc_h-5:.1f}" x2="{tx:.1f}" y2="{rc_y+rc_h:.1f}" stroke="{GRAY_MID}" stroke-width="0.9"/>')
        if v in (-6, -4, -2, 1, 2, 6):
            out.append(f'  <text x="{tx:.1f}" y="{rc_y+rc_h-7:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{v}</text>')

    # Dashed tether curves from param $a (val 12) and param $b (val 8) to the singleton socket g = 4
    a12_x = nl_x(12, pa_x, pw)
    b8_x = nl_x(8, pb_x, pw)
    g4_x = nl_x(4, rc_x, rc_w)

    out.append(f'  <path d="M {a12_x:.1f} {pa_y+ph:.1f} C {a12_x:.1f} {pa_y+ph+55:.1f}, {g4_x-30:.1f} {rc_y-45:.1f}, {g4_x-4:.1f} {rc_y-3:.1f}" fill="none" stroke="{INDIGO}" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrow-indigo)"/>')
    out.append(f'  <path d="M {b8_x:.1f} {pb_y+ph:.1f} C {b8_x:.1f} {pb_y+ph+55:.1f}, {g4_x+30:.1f} {rc_y-45:.1f}, {g4_x+4:.1f} {rc_y-3:.1f}" fill="none" stroke="{INDIGO}" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrow-indigo)"/>')

    # Pill background behind the tether label so curves never clash with text!
    out.append(f'  <rect x="295" y="366" width="350" height="36" rx="5" fill="{BG}" fill-opacity="0.92" stroke="{INDIGO}" stroke-width="1.0" stroke-dasharray="3,2"/>')
    out.append(f'  <text x="470" y="381" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INDIGO}">Dependent socket tethered to $a and $b</text>')
    out.append(f'  <text x="470" y="396" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Unique g with Div(g) = {{1, 2, 4}} is g = 4 (returned 4 seats in socket)</text>')

    out.append(f'  <text x="{rc_x - 12}" y="{rc_y + 21}" text-anchor="end" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">result Gcd(a, b)</text>')

    out.append(svg_footer())
    with open("fig-1.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 2: Full Codillon WAT Editor Listing for Euclid's Algorithm on (12, 8) -> 4
# ============================================================================
def generate_fig2():
    W, H = 900, 740
    out = [svg_header(
        W, H,
        "Euclid in Codillon's Editor: Stack Fractions Preserve Div(x) ∩ Div(y) to Seat 4",
        "Left gutter: 1:1 refined stack fractions (84×14 px) with pale-lavender dataflow ribbons. Right panel: step-by-step trace for (a=12, b=8)."
    )]

    # Left Gutter Header (Codillon Editor View)
    out.append(f'  <rect x="24" y="76" width="535" height="642" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')
    out.append(f'  <rect x="24" y="76" width="535" height="28" rx="6" fill="{GRAY_FAINT}" stroke="{GRAY_LIGHT}" stroke-width="1.0"/>')
    out.append(f'  <text x="125" y="95" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{INK}">STACK FRACTION (84×14)</text>')
    out.append(f'  <text x="295" y="95" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{INK}">WAT INSTRUCTION</text>')
    out.append(f'  <text x="468" y="95" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{PURPLE}">REFINEMENT / INVARIANT</text>')

    # Parameter Header inside Editor
    pa_x, pa_y = 52, 122
    pb_x, pb_y = 144, 122
    out.append(f'  <text x="{pa_x+42}" y="{pa_y-5}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{INK}">param $a = 12</text>')
    out.append(draw_refined_nl(pa_x, pa_y, 84, 14, is_cup=False, region=(0, INT_MAX), sockets=divisors(12), concrete_val=12))
    out.append(f'  <text x="{pb_x+42}" y="{pb_y-5}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{INK}">param $b = 8</text>')
    out.append(draw_refined_nl(pb_x, pb_y, 84, 14, is_cup=False, region=(0, INT_MAX), sockets=divisors(8), concrete_val=8))
    out.append(f'  <text x="236" y="126" font-family="{FONT_MONO}" font-size="11" font-weight="bold" fill="{INK}">(func $gcd (param $a $b)</text>')
    out.append(f'  <text x="236" y="140" font-family="{FONT_MONO}" font-size="11" fill="{GRAY_DARK}">  (result Gcd(a,b))</text>')
    out.append(f'  <text x="412" y="133" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE}">Div(12)∩Div(8) = {{1, 2, 4}}</text>')

    rows = [
        {
            "yc": 176, "code": "(loop $step", "note": "Inv: Div(x)∩Div(y) = Div(a)∩Div(b)",
            "cups": [], "outs": []
        },
        {
            "yc": 222, "code": "  local.get $y", "note": "{v = y} (iter 1: 8; exit: 0)",
            "cups": [],
            "outs": [{"x": 85, "reg": (0, INT_MAX), "sock": [1,2,4], "val": 8}]
        },
        {
            "yc": 276, "code": "  i32.eqz", "note": "y=0 ⟹ Div(x)=Div(a)∩Div(b)",
            "cups": [{"x": 85, "reg": (0, INT_MAX), "sock": [1,2,4], "val": 8}],
            "outs": [{"x": 85, "reg": (0, 1), "sock": [0], "val": 0}]
        },
        {
            "yc": 330, "code": "  br_if $exit", "note": "if 1 (y=0), jump to return",
            "cups": [{"x": 85, "reg": (0, 1), "sock": [0], "val": 0}],
            "outs": []
        },
        {
            "yc": 376, "code": "  local.get $y", "note": "save old y = 8 (becomes x')",
            "cups": [],
            "outs": [{"x": 48, "reg": (1, INT_MAX), "sock": [1,2,4], "val": 8}]
        },
        {
            "yc": 426, "code": "  local.get $x", "note": "push x = 12",
            "cups": [],
            "outs": [{"x": 140, "reg": (0, INT_MAX), "sock": [1,2,4], "val": 12}]
        },
        {
            "yc": 476, "code": "  local.get $y", "note": "push y = 8 ∈ [1, INT_MAX]",
            "cups": [],
            "outs": [{"x": 140, "reg": (1, INT_MAX), "sock": [1,2,4], "val": 8}]
        },
        {
            "yc": 534, "code": "  i32.rem_u", "note": "{r < y | Div(y)∩Div(r)=Div(x)∩Div(y)}",
            "cups": [
                {"x": 48, "reg": (0, INT_MAX), "sock": [1,2,4], "val": 12},
                {"x": 140, "reg": (1, INT_MAX), "sock": [1,2,4], "val": 8}
            ],
            "outs": [{"x": 94, "reg": (0, 7), "sock": [1,2,4], "val": 4}]
        },
        {
            "yc": 592, "code": "  local.set $y $x", "note": "(x', y') ← (8, 4); br $step",
            "cups": [
                {"x": 48, "reg": (1, INT_MAX), "sock": [1,2,4], "val": 8},
                {"x": 140, "reg": (0, 7), "sock": [1,2,4], "val": 4}
            ],
            "outs": []
        },
        {
            "yc": 646, "code": "local.get $x", "note": "at exit y=0, so x = 4",
            "cups": [],
            "outs": [{"x": 94, "reg": None, "sock": [1,2], "active": 4, "val": 4}]
        },
        {
            "yc": 698, "code": "return)", "note": "4 seats in Gcd(12,8) = {4}",
            "cups": [{"x": 94, "reg": None, "sock": [1,2], "active": 4, "val": 4}],
            "outs": []
        }
    ]

    # Pale-lavender dataflow ribbons
    out.append(draw_ribbon(85, 222+17, 84, 85, 276-17, 84))
    out.append(draw_ribbon(85, 276+17, 84, 85, 330-17, 84))
    out.append(draw_ribbon(48, 376+17, 84, 48, 592-17, 84, opacity=0.32))
    out.append(draw_ribbon(140, 426+17, 84, 48, 534-17, 84, opacity=0.45))
    out.append(draw_ribbon(140, 476+17, 84, 140, 534-17, 84, opacity=0.55))
    out.append(draw_ribbon(94, 534+17, 84, 140, 592-17, 84, opacity=0.55))
    out.append(draw_ribbon(94, 646+17, 84, 94, 698-17, 84, opacity=0.65))

    # Clean vertical tether tracks along the left gutter margin (x=31 and x=38) from param $a and $b to return cup socket!
    sock_x = nl_x(4, 94, 84)
    a_x = nl_x(12, pa_x, 84)
    b_x = nl_x(8, pb_x, 84)
    out.append(f'  <path d="M {a_x:.1f} {pa_y+14:.1f} L {a_x:.1f} 146 L 31 146 L 31 670 L {sock_x-3:.1f} 670 L {sock_x-3:.1f} {698-19:.1f}" fill="none" stroke="{INDIGO}" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arrow-indigo)"/>')
    out.append(f'  <path d="M {b_x:.1f} {pb_y+14:.1f} L {b_x:.1f} 152 L 38 152 L 38 664 L {sock_x+3:.1f} 664 L {sock_x+3:.1f} {698-19:.1f}" fill="none" stroke="{INDIGO}" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arrow-indigo)"/>')

    # Render each instruction row
    for idx, r in enumerate(rows):
        yc = r["yc"]
        if idx % 2 == 1:
            out.append(f'  <rect x="230" y="{yc-22}" width="324" height="44" fill="{GRAY_FAINT}" fill-opacity="0.6"/>')
        if r["cups"] or r["outs"]:
            xs = [c["x"] for c in r["cups"]] + [o["x"] for o in r["outs"]]
            x_min = min(xs) - 4
            x_max = max(xs) + 84 + 4
            out.append(f'  <line x1="{x_min}" y1="{yc}" x2="{x_max}" y2="{yc}" stroke="{INK}" stroke-width="1.8"/>')
        for c in r["cups"]:
            out.append(draw_refined_nl(c["x"], yc - 17, 84, 14, is_cup=True,
                                       region=c.get("reg"), sockets=c.get("sock"),
                                       active_socket=c.get("active"), concrete_val=c.get("val")))
        for o in r["outs"]:
            out.append(draw_refined_nl(o["x"], yc + 3, 84, 14, is_cup=False,
                                       region=o.get("reg"), sockets=o.get("sock"),
                                       active_socket=o.get("active"), concrete_val=o.get("val")))
        out.append(f'  <text x="236" y="{yc+4}" font-family="{FONT_MONO}" font-size="12" font-weight="bold" fill="{INK}">{esc(r["code"])}</text>')
        out.append(f'  <text x="380" y="{yc+4}" font-family="{FONT_SANS}" font-size="11" fill="{PURPLE}">{esc(r["note"])}</text>')

    # --- RIGHT PANEL: Unrolled Loop Invariant & Execution Trace for (12, 8) ---
    out.append(f'  <rect x="572" y="76" width="304" height="642" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')
    out.append(f'  <text x="588" y="100" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">Loop Invariant Across All Steps</text>')
    out.append(f'  <text x="588" y="118" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">Every step replaces (x, y) with (y, x mod y) while</text>')
    out.append(f'  <text x="588" y="133" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">keeping Div(x) ∩ Div(y) = {{1, 2, 4}} invariant:</text>')

    steps = [
        ("Entry (Step 0)", 12, 8, "Div(12)={1,2,3,4,6,12}", "Div(8)={1,2,4,8}", "Div(12)∩Div(8) = {1, 2, 4}", 152),
        ("After 12 mod 8 = 4", 8, 4, "Div(8)={1,2,4,8}", "Div(4)={1,2,4}", "Div(8)∩Div(4) = {1, 2, 4}", 294),
        ("After 8 mod 4 = 0 (Exit)", 4, 0, "Div(4)={1,2,4}", "Div(0)=ℕ (all naturals)", "Div(4)∩ℕ = Div(4) = {1, 2, 4}", 436),
    ]

    for title, xv, yv, dx_str, dy_str, inv_str, sy in steps:
        out.append(f'  <rect x="586" y="{sy}" width="276" height="128" rx="5" fill="{GRAY_FAINT}" stroke="{GRAY_LIGHT}" stroke-width="1.0"/>')
        out.append(f'  <text x="596" y="{sy+18}" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">{title}: (x={xv}, y={yv})</text>')

        # Draw x shape (shifted right to x=646, width=96 so labels never collide)
        out.append(f'  <text x="596" y="{sy+40}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">x = {xv}</text>')
        out.append(draw_refined_nl(646, sy+29, 96, 14, is_cup=False, region=(0, INT_MAX), sockets=divisors(xv, cap=12), concrete_val=xv))
        out.append(f'  <text x="748" y="{sy+40}" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{dx_str}</text>')

        # Draw y shape
        out.append(f'  <text x="596" y="{sy+66}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">y = {yv}</text>')
        y_reg = "all" if yv == 0 else (0, INT_MAX)
        out.append(draw_refined_nl(646, sy+55, 96, 14, is_cup=False, region=y_reg, sockets=divisors(yv, cap=12), concrete_val=yv))
        out.append(f'  <text x="748" y="{sy+66}" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{dy_str}</text>')

        # Common divisors bar
        out.append(f'  <text x="596" y="{sy+92}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE}">Common Div:</text>')
        out.append(draw_refined_nl(664, sy+81, 84, 14, is_cup=False, sockets=[1, 2], active_socket=4))
        out.append(f'  <text x="754" y="{sy+92}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE}">= {{1, 2, 4}}</text>')
        out.append(f'  <text x="596" y="{sy+116}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{INDIGO}">{inv_str} ⟹ socket = 4</text>')

    # Final QED box at bottom right
    out.append(f'  <rect x="586" y="582" width="276" height="122" rx="5" fill="{PURPLE_FILL}" fill-opacity="0.35" stroke="{PURPLE}" stroke-width="1.5"/>')
    out.append(f'  <text x="598" y="604" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">Why y = 0 Unlocks the Return Cup:</text>')
    out.append(f'  <text x="598" y="624" font-family="{FONT_SANS}" font-size="11" fill="{INK}">• Every d ∈ ℕ divides 0 (0 = 0 · d), so Div(0) = ℕ.</text>')
    out.append(f'  <text x="598" y="642" font-family="{FONT_SANS}" font-size="11" fill="{INK}">• At br_if $exit: Div(x) = Div(x) ∩ ℕ = Div(a) ∩ Div(b).</text>')
    out.append(f'  <text x="598" y="660" font-family="{FONT_SANS}" font-size="11" fill="{INK}">• Thus x = 4 satisfies Div(x) = Div(12) ∩ Div(8),</text>')
    out.append(f'  <text x="598" y="678" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">  and seats cleanly in the Gcd(12, 8) socket!</text>')

    out.append(svg_footer())
    with open("fig-2.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 3: Dependent Socket Retargeting Across Input Pairs
# (1071, 462 -> 21 in log zone; 13, 8 -> 1 coprime; 21, 0 -> 21; 0, 0 -> 0)
# ============================================================================
def generate_fig3():
    W, H = 900, 660
    out = [svg_header(
        W, H,
        "Dependent Socket Retargeting: Changing (a, b) Slides the Result Socket",
        "Because Gcd(a, b) is indexed by a and b, the dashed tethers pull the result cup's socket across linear and logarithmic zones."
    )]

    cases = [
        {
            "title": "A. Log-Scale Inputs & Output: (a = 1071, b = 462) → gcd = 21",
            "sub1": "Both inputs and gcd = 21 lie in the right logarithmic zone (> +8);",
            "sub2": "Euclid takes 3 remainder steps: 1071 → 462 → 147 → 21 → 0.",
            "a": 1071, "b": 462, "g": 21,
            "div_a_lbl": "Div(1071)={1,3,7,..,1071}",
            "div_b_lbl": "Div(462)={1,2,3,7,..,462}",
            "inter_lbl": "Div(1071) ∩ Div(462) = {1, 3, 7, 21} = Div(21)",
            "trace": "1071 mod 462 = 147  →  462 mod 147 = 21  →  147 mod 21 = 0",
            "x": 28, "y": 82
        },
        {
            "title": "B. Coprime Inputs: (a = 13, b = 8) → gcd = 1",
            "sub1": "No common prime factors: Div(13) = {1, 13} and Div(8) = {1, 2, 4, 8}",
            "sub2": "intersect only at {1}, pulling the result socket to g = 1.",
            "a": 13, "b": 8, "g": 1,
            "div_a_lbl": "Div(13) = {1, 13}",
            "div_b_lbl": "Div(8) = {1, 2, 4, 8}",
            "inter_lbl": "Div(13) ∩ Div(8) = {1} = Div(1)",
            "trace": "13 mod 8 = 5  →  8 mod 5 = 3  →  5 mod 3 = 2  →  3 mod 2 = 1",
            "x": 464, "y": 82
        },
        {
            "title": "C. Zero Absorber: (a = 21, b = 0) → gcd = 21",
            "sub1": "Because Div(0) = ℕ (every number divides 0), intersecting with",
            "sub2": "Div(0) leaves Div(21) unchanged; loop exits on first check.",
            "a": 21, "b": 0, "g": 21,
            "div_a_lbl": "Div(21) = {1, 3, 7, 21}",
            "div_b_lbl": "Div(0) = ℕ (all naturals)",
            "inter_lbl": "Div(21) ∩ ℕ = {1, 3, 7, 21} = Div(21)",
            "trace": "y = 0 immediately at loop entry  →  br_if $exit  →  return 21",
            "x": 28, "y": 368
        },
        {
            "title": "D. Degenerate Origin: (a = 0, b = 0) → gcd = 0",
            "sub1": "Both divisor sets are all of ℕ: Div(0) ∩ Div(0) = ℕ. The unique",
            "sub2": "natural g ∈ ℕ whose divisor set is all of ℕ is g = 0!",
            "a": 0, "b": 0, "g": 0,
            "div_a_lbl": "Div(0) = ℕ (all naturals)",
            "div_b_lbl": "Div(0) = ℕ (all naturals)",
            "inter_lbl": "Div(0) ∩ Div(0) = ℕ = Div(0)  ⟹  socket at g = 0",
            "trace": "y = 0 immediately at loop entry  →  br_if $exit  →  return 0",
            "x": 464, "y": 368
        }
    ]

    for c in cases:
        bx, by = c["x"], c["y"]
        bw, bh = 408, 268
        a, b, g = c["a"], c["b"], c["g"]
        out.append(f'  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.3"/>')
        out.append(f'  <text x="{bx+14}" y="{by+22}" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">{esc(c["title"])}</text>')
        out.append(f'  <text x="{bx+14}" y="{by+39}" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{esc(c["sub1"])}</text>')
        out.append(f'  <text x="{bx+14}" y="{by+53}" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{esc(c["sub2"])}</text>')

        # Param a and b shapes (width 170 each)
        pa_x, pa_y = bx + 18, by + 80
        pb_x, pb_y = bx + 220, by + 80
        pw, ph = 170, 16

        reg_a = "all" if a == 0 else (0, INT_MAX)
        reg_b = "all" if b == 0 else (0, INT_MAX)
        sock_a = divisors(a, cap=16) if a != 0 else None
        sock_b = divisors(b, cap=16) if b != 0 else None

        out.append(f'  <text x="{pa_x}" y="{pa_y-5}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">$a={a}</text>')
        out.append(f'  <text x="{pa_x+170}" y="{pa_y-5}" text-anchor="end" font-family="{FONT_SANS}" font-size="11" fill="{PURPLE}">{esc(c["div_a_lbl"])}</text>')
        out.append(draw_refined_nl(pa_x, pa_y, pw, ph, is_cup=False, region=reg_a, sockets=sock_a, concrete_val=a))

        out.append(f'  <text x="{pb_x}" y="{pb_y-5}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">$b={b}</text>')
        out.append(f'  <text x="{pb_x+170}" y="{pb_y-5}" text-anchor="end" font-family="{FONT_SANS}" font-size="11" fill="{PURPLE}">{esc(c["div_b_lbl"])}</text>')
        out.append(draw_refined_nl(pb_x, pb_y, pw, ph, is_cup=False, region=reg_b, sockets=sock_b, concrete_val=b))

        # Result cup Gcd(a, b) (width 340)
        rc_x, rc_y, rc_w, rc_h = bx + 34, by + 168, 340, 22
        common_socks = [d for d in common_divisors(a, b, cap=21) if d != g] if (a != 0 or b != 0) else None
        out.append(draw_refined_nl(rc_x, rc_y, rc_w, rc_h, is_cup=True,
                                   region=("all" if g == 0 else None),
                                   sockets=common_socks, active_socket=g, concrete_val=g, show_scale=True))

        # Fraction bar below result cup
        out.append(f'  <line x1="{rc_x-10}" y1="{rc_y+rc_h+19}" x2="{rc_x+rc_w+10}" y2="{rc_y+rc_h+19}" stroke="{INK}" stroke-width="1.8"/>')

        # Tethers from $a and $b to socket g in result cup
        ax_pos = nl_x(a, pa_x, pw)
        bx_pos = nl_x(b, pb_x, pw)
        gx_pos = nl_x(g, rc_x, rc_w)

        out.append(f'  <path d="M {ax_pos:.1f} {pa_y+ph:.1f} C {ax_pos:.1f} {pa_y+ph+35:.1f}, {gx_pos-14:.1f} {rc_y-32:.1f}, {gx_pos-2:.1f} {rc_y-2:.1f}" fill="none" stroke="{INDIGO}" stroke-width="1.6" stroke-dasharray="4,3" marker-end="url(#arrow-indigo)"/>')
        out.append(f'  <path d="M {bx_pos:.1f} {pb_y+ph:.1f} C {bx_pos:.1f} {pb_y+ph+35:.1f}, {gx_pos+14:.1f} {rc_y-32:.1f}, {gx_pos+2:.1f} {rc_y-2:.1f}" fill="none" stroke="{INDIGO}" stroke-width="1.6" stroke-dasharray="4,3" marker-end="url(#arrow-indigo)"/>')

        # Pill callout label in the midpoint between params and result cup so tethers never obscure text
        out.append(f'  <rect x="{bx+54}" y="{by+114}" width="{bw-108}" height="20" rx="4" fill="{BG}" fill-opacity="0.92" stroke="{INDIGO}" stroke-width="0.9" stroke-dasharray="2,2"/>')
        out.append(f'  <text x="{bx+bw/2:.1f}" y="{by+128:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{INDIGO}">{esc(c["inter_lbl"])}</text>')

        # Bottom trace summary
        out.append(f'  <text x="{bx+14}" y="{by+bh-28}" font-family="{FONT_MONO}" font-size="11" fill="{INK}">{esc(c["trace"])}</text>')
        out.append(f'  <text x="{bx+14}" y="{by+bh-11}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">Result g = {g} seats cleanly inside Gcd({a}, {b}) socket</text>')

    out.append(svg_footer())
    with open("fig-3.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 4: Type Errors — Why Wrong Candidates & Buggy Programs SPILL Over the Rim
# ============================================================================
def generate_fig4():
    W, H = 900, 620
    out = [svg_header(
        W, H,
        "Type Errors Spill Over the Rim: Any Return Value ≠ gcd(12, 8) = 4 Is Rejected",
        "Gcd(12, 8) = { g ∈ ℕ | Div(g) = {1, 2, 4} } is a singleton set {4}. Returning 2, 8, or 12 violates the refinement and spills."
    )]

    # Top Banner: The three conjuncts of Gcd(12, 8) and the single valid socket at 4
    out.append(f'  <rect x="28" y="78" width="844" height="122" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')
    out.append(f'  <text x="44" y="100" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">Reference Specification for (a = 12, b = 8): Div(12) ∩ Div(8) = {{1, 2, 3, 4, 6, 12}} ∩ {{1, 2, 4, 8}} = {{1, 2, 4}}</text>')
    out.append(f'  <text x="44" y="118" font-family="{FONT_SANS}" font-size="12" fill="{GRAY_DARK}">To inhabit Gcd(12, 8), candidate g must satisfy:  (1) g | 12   ∧   (2) g | 8   ∧   (3) ∀d ∈ {{1, 2, 4}} . d | g.   Only g = 4 satisfies all three.</text>')

    # Draw the valid reference cup in the top banner
    ref_x, ref_y, ref_w, ref_h = 180, 142, 540, 24
    out.append(draw_refined_nl(ref_x, ref_y, ref_w, ref_h, is_cup=True, sockets=[1, 2], active_socket=4, concrete_val=4, show_scale=True))
    g4_rx = nl_x(4, ref_x, ref_w)
    out.append(f'  <text x="{g4_rx}" y="{ref_y-6}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">Valid socket at g = 4 (seated)</text>')
    out.append(f'  <text x="{ref_x-12}" y="{ref_y+16}" text-anchor="end" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">Gcd(12, 8) Cup:</text>')

    # Three Error Columns below
    cols = [
        {
            "title": "Error 1: Common Divisor Too Small",
            "cand": "Candidate g = 2 in return cup:",
            "val": 2,
            "code_bad": "i32.const 2 ;; return",
            "why1": "✓ 2 | 12 and 2 | 8 (common divisor)",
            "why2": "✗ Fails (3): d = 4 ∈ Div(12)∩Div(8),",
            "why3": "   but 4 ∤ 2! (Div(2) = {1, 2} ⊊ {1, 2, 4})",
            "div_g": [1, 2],
            "missing": "Actual Div(2) — missing 4:",
            "x": 28
        },
        {
            "title": "Error 2: Divides b Only (Not a)",
            "cand": "Candidate g = 8 in return cup:",
            "val": 8,
            "code_bad": "local.get $b ;; return",
            "why1": "✓ 8 | 8 and ∀d ∈ {1,2,4}. d | 8",
            "why2": "✗ Fails (1): 8 ∤ 12 (12 mod 8 = 4 ≠ 0)!",
            "why3": "   (Div(8) = {1, 2, 4, 8} ⊋ {1, 2, 4})",
            "div_g": [1, 2, 4, 8],
            "missing": "Actual Div(8) — extra 8 ∉ Div(12):",
            "x": 314
        },
        {
            "title": "Error 3: Buggy Loop Exit (br_if $x)",
            "cand": "Returns g = 12 (exits on step 1):",
            "val": 12,
            "code_bad": "local.get $x ;; br_if $exit",
            "why1": "✓ 12 | 12 and ∀d ∈ {1,2,4}. d | 12",
            "why2": "✗ Fails (2): 12 ∤ 8 (exited before y=0)!",
            "why3": "   (Div(12) = {1,2,3,4,6,12} ≠ {1,2,4})",
            "div_g": [1, 2, 3, 4, 6, 12],
            "missing": "Actual Div(12) — extra {3,6,12}:",
            "x": 600
        }
    ]

    for c in cols:
        cx = c["x"]
        cw, ch = 272, 392
        cy = 214
        v = c["val"]

        out.append(f'  <rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="6" fill="{BG}" stroke="{RED}" stroke-width="1.5"/>')
        out.append(f'  <rect x="{cx}" y="{cy}" width="{cw}" height="30" rx="6" fill="{RED_FILL}" stroke="{RED}" stroke-width="1.0"/>')
        out.append(f'  <text x="{cx+cw/2}" y="{cy+20}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{RED}">{esc(c["title"])}</text>')

        # Buggy WAT instruction snippet + 1:1 editor stack fraction with SPILL
        out.append(f'  <text x="{cx+14}" y="{cy+52}" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{INK}">{esc(c["cand"])}</text>')
        out.append(f'  <rect x="{cx+14}" y="{cy+60}" width="{cw-28}" height="24" rx="3" fill="{GRAY_FAINT}" stroke="{GRAY_LIGHT}"/>')
        out.append(f'  <text x="{cx+22}" y="{cy+76}" font-family="{FONT_MONO}" font-size="11.5" font-weight="bold" fill="{RED}">{esc(c["code_bad"])}</text>')

        # Magnified Result Cup (width 236, height 24) showing socket at 4 and SPILL at v
        mc_x, mc_y, mc_w, mc_h = cx + 18, cy + 142, 236, 24
        out.append(draw_refined_nl(mc_x, mc_y, mc_w, mc_h, is_cup=True,
                                   sockets=[1, 2], active_socket=4, spill_val=v, show_scale=True, rim_Color=RED))
        out.append(f'  <line x1="{mc_x-6}" y1="{mc_y+mc_h+18}" x2="{mc_x+mc_w+6}" y2="{mc_y+mc_h+18}" stroke="{RED}" stroke-width="2.0"/>')

        # Callout arrows for socket at 4 vs spill at v (well separated vertically and horizontally)
        sx4 = nl_x(4, mc_x, mc_w)
        sxv = nl_x(v, mc_x, mc_w)
        out.append(f'  <text x="{sx4 - 16 if v > 4 else sx4 + 22:.1f}" y="{mc_y-30}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE}">Socket=4</text>')
        out.append(f'  <line x1="{sx4}" y1="{mc_y-25}" x2="{sx4}" y2="{mc_y-3}" stroke="{PURPLE}" stroke-width="1.3" marker-end="url(#arrow-purple)"/>')

        spill_lbl_x = sxv - 28 if v < 4 else sxv + 18
        out.append(f'  <text x="{spill_lbl_x:.1f}" y="{mc_y-22}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED}">Spill g={v}!</text>')

        # Divisor set mismatch visual comparison
        out.append(f'  <text x="{cx+14}" y="{cy+212}" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INK}">Why g = {v} Misses the Socket:</text>')
        out.append(f'  <text x="{cx+14}" y="{cy+232}" font-family="{FONT_SANS}" font-size="11" fill="{INK}">{esc(c["why1"])}</text>')
        out.append(f'  <text x="{cx+14}" y="{cy+250}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED}">{esc(c["why2"])}</text>')
        out.append(f'  <text x="{cx+14}" y="{cy+268}" font-family="{FONT_SANS}" font-size="11" fill="{RED}">{esc(c["why3"])}</text>')

        # Mini comparison of Div(g) vs Target Div(12)∩Div(8)
        out.append(f'  <rect x="{cx+14}" y="{cy+284}" width="{cw-28}" height="92" rx="4" fill="{GRAY_FAINT}" stroke="{GRAY_LIGHT}"/>')
        out.append(f'  <text x="{cx+22}" y="{cy+302}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE}">Required: Div(12)∩Div(8) = {{1, 2, 4}}</text>')
        out.append(draw_refined_nl(cx+22, cy+308, cw-44, 14, is_cup=False, sockets=[1, 2, 4], active_socket=4))

        out.append(f'  <text x="{cx+22}" y="{cy+340}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED}">{esc(c["missing"])}</text>')
        out.append(draw_refined_nl(cx+22, cy+346, cw-44, 14, is_cup=False, sockets=c["div_g"], rim_Color=RED))

    out.append(svg_footer())
    with open("fig-4.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 5: Subtyping as Set Containment & Evidence Erasure at Runtime
# ============================================================================
def generate_fig5():
    W, H = 900, 560
    out = [svg_header(
        W, H,
        "Subtyping Funnel & Evidence Erasure: Singleton {4} Shrinks Into Any Supertype Cup",
        "Left: Subtyping is set containment (narrower region pours into wider cup without spilling). Right: Proof tethers erase to plain 30×11 Wasm i32."
    )]

    # --- LEFT PANEL: Subtyping as Set Containment Funnel for (a=12, b=8) ---
    out.append(f'  <rect x="28" y="78" width="465" height="456" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')
    out.append(f'  <text x="44" y="102" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">1. Subtyping Is Set Containment (A ≤: B ⟺ A ⊆ B)</text>')
    out.append(f'  <text x="44" y="120" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">A narrower output region pours cleanly into any wider input cup:</text>')

    CupX = 64
    CupW = 220

    levels = [
        {
            "y": 146,
            "name": "Gcd(12, 8) = {4}",
            "desc": "Singleton: Div(g) = Div(12) ∩ Div(8)",
            "reg": None, "sock": [4], "active": 4,
            "w_left": nl_x(4, CupX, CupW) - 3, "w_right": nl_x(4, CupX, CupW) + 3
        },
        {
            "y": 230,
            "name": "CommonDiv(12, 8) = {1, 2, 4}",
            "desc": "Drops maximality: g | 12 ∧ g | 8",
            "reg": (1, 4), "sock": [1, 2, 4], "active": None,
            "w_left": nl_x(1, CupX, CupW), "w_right": nl_x(4, CupX, CupW)
        },
        {
            "y": 314,
            "name": "Div(12) = {1, 2, 3, 4, 6, 12}",
            "desc": "Drops b-divisibility: g | 12",
            "reg": (1, 12), "sock": [1, 2, 3, 4, 6, 12], "active": None,
            "w_left": nl_x(1, CupX, CupW), "w_right": nl_x(12, CupX, CupW)
        },
        {
            "y": 398,
            "name": "Nat = {g ∈ i32 | g ≥ 0}",
            "desc": "Non-negative integers [0, INT_MAX]",
            "reg": (0, INT_MAX), "sock": None, "active": None,
            "w_left": nl_x(0, CupX, CupW), "w_right": CupX + CupW
        },
        {
            "y": 480,
            "name": "Unrefined i32 = [MIN, MAX]",
            "desc": "Full 32-bit range (any value seats)",
            "reg": "all", "sock": None, "active": None,
            "w_left": CupX, "w_right": CupX + CupW
        }
    ]

    # Draw funnel ribbons between levels first
    for i in range(len(levels) - 1):
        curr = levels[i]
        nxt = levels[i+1]
        y1 = curr["y"] + 20
        y2 = nxt["y"]
        x1_l, x1_r = curr["w_left"], curr["w_right"]
        x2_l, x2_r = nxt["w_left"], nxt["w_right"]
        ym = (y1 + y2) / 2.0
        path = (f"M {x1_l:.1f} {y1:.1f} "
                f"C {x1_l:.1f} {ym:.1f}, {x2_l:.1f} {ym:.1f}, {x2_l:.1f} {y2:.1f} "
                f"L {x2_r:.1f} {y2:.1f} "
                f"C {x2_r:.1f} {ym:.1f}, {x1_r:.1f} {ym:.1f}, {x1_r:.1f} {y1:.1f} Z")
        out.append(f'  <path d="{path}" fill="{PURPLE_FILL}" fill-opacity="0.55" stroke="{PURPLE}" stroke-width="1.0" stroke-dasharray="3,2"/>')
        out.append(f'  <text x="52" y="{ym+4:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">⊆</text>')

    # Draw each level's refined cup and full unclipped labels
    for idx, lv in enumerate(levels):
        ly = lv["y"]
        out.append(draw_refined_nl(CupX, ly, CupW, 20, is_cup=(idx > 0),
                                   region=lv["reg"], sockets=lv["sock"],
                                   active_socket=lv["active"], concrete_val=4,
                                   show_scale=(idx == len(levels)-1)))
        out.append(f'  <text x="294" y="{ly+9}" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INK}">{esc(lv["name"])}</text>')
        out.append(f'  <text x="294" y="{ly+23}" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">{esc(lv["desc"])}</text>')

    # --- RIGHT PANEL: Compile-Time Refined Value+Evidence vs Runtime Erased Wasm ---
    out.append(f'  <rect x="508" y="78" width="364" height="456" rx="6" fill="{BG}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')
    out.append(f'  <text x="524" y="102" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">2. Evidence Erasure at Compile Time</text>')
    out.append(f'  <text x="524" y="120" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">A refined value is (v, proof); at runtime only v = 4 remains.</text>')

    # Top Box: Compile-time Editor View (84x14 + tethers + proof certificate)
    out.append(f'  <rect x="524" y="138" width="332" height="178" rx="5" fill="{GRAY_FAINT}" stroke="{PURPLE}" stroke-width="1.4"/>')
    out.append(f'  <text x="536" y="158" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">Compile-Time Codillon Editor View</text>')
    out.append(f'  <text x="536" y="175" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Value + Evidence:  (4,  pf : Div(4) = Div(12) ∩ Div(8))</text>')

    # Mini param a, b and tethered result cup inside compile-time box
    out.append(draw_refined_nl(550, 196, 110, 14, is_cup=False, region=(0, INT_MAX), sockets=divisors(12), concrete_val=12))
    out.append(f'  <text x="605" y="191" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">$a = 12</text>')
    out.append(draw_refined_nl(700, 196, 110, 14, is_cup=False, region=(0, INT_MAX), sockets=divisors(8), concrete_val=8))
    out.append(f'  <text x="755" y="191" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">$b = 8</text>')

    out.append(draw_refined_nl(580, 254, 190, 20, is_cup=True, sockets=[1, 2], active_socket=4, concrete_val=4))
    out.append(f'  <line x1="570" y1="278" x2="780" y2="278" stroke="{INK}" stroke-width="1.8"/>')

    gx = nl_x(4, 580, 190)
    ax = nl_x(12, 550, 110)
    bx = nl_x(8, 700, 110)
    out.append(f'  <path d="M {ax:.1f} 210 C {ax:.1f} 234, {gx-10:.1f} 234, {gx-2:.1f} 252" fill="none" stroke="{INDIGO}" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrow-indigo)"/>')
    out.append(f'  <path d="M {bx:.1f} 210 C {bx:.1f} 234, {gx+10:.1f} 234, {gx+2:.1f} 252" fill="none" stroke="{INDIGO}" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrow-indigo)"/>')
    out.append(f'  <text x="675" y="302" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INDIGO}">84×14 number-line cup + tethers + Lean proof term</text>')

    # Erasure Arrow (centered with non-clipping label)
    out.append(f'  <line x1="585" y1="322" x2="585" y2="362" stroke="{INK}" stroke-width="2.0" marker-end="url(#arrow-ink)"/>')
    out.append(f'  <text x="598" y="340" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INK}">Erase refinements &amp; evidence</text>')
    out.append(f'  <text x="598" y="355" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">(zero runtime space or time overhead)</text>')

    # Bottom Box: Runtime WebAssembly Execution (30x11 unrefined i32)
    out.append(f'  <rect x="524" y="370" width="332" height="148" rx="5" fill="{GRAY_FAINT}" stroke="{INK}" stroke-width="1.4"/>')
    out.append(f'  <text x="536" y="392" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">Runtime WebAssembly Engine View</text>')
    out.append(f'  <text x="536" y="410" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">Standard unrefined Wasm stack fraction (30×11 px):</text>')

    ux = 605
    out.append(draw_unrefined_shape(ux - 36, 438, 30, 11, is_cup=True, val="12", label="$a"))
    out.append(draw_unrefined_shape(ux + 6, 438, 30, 11, is_cup=True, val="8", label="$b"))
    out.append(f'  <line x1="{ux-44}" y1="454" x2="{ux+44}" y2="454" stroke="{INK}" stroke-width="2.0"/>')
    out.append(draw_unrefined_shape(ux - 15, 459, 30, 11, is_cup=False, val="4"))
    out.append(f'  <text x="{ux+60}" y="458" font-family="{FONT_MONO}" font-size="12" font-weight="bold" fill="{INK}">call $gcd → 4 : i32</text>')

    out.append(f'  <text x="536" y="494" font-family="{FONT_SANS}" font-size="11" fill="{NAVY}">• Number line, sockets, and tethers are compile-time only.</text>')
    out.append(f'  <text x="536" y="510" font-family="{FONT_SANS}" font-size="11" fill="{NAVY}">• Wasm VM executes raw i32 instructions guaranteed spill-free.</text>')

    out.append(svg_footer())
    with open("fig-5.svg", "w") as f:
        f.write("\n".join(out))


def main():
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    generate_fig5()
    print("Generated fig-1.svg through fig-5.svg successfully.")

if __name__ == "__main__":
    main()
