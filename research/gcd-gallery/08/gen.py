#!/usr/bin/env python3
"""
Generator for Dependent Type Family visualizations of Gcd(a, b) (Angle 08).
Generates fig-1.svg through fig-5.svg.
"""

import math
import html

# Palette strictly following rules (NO GREEN ANYWHERE)
BG = "#fffff0"
INK = "#222222"
PURPLE = "#6A5ACD"       # type / region purple
PURPLE_FILL = "#d9d5f2"  # muted fill for type region
PURPLE_LIGHT = "#eceaf9"
PURPLE_MID = "#9b8fe0"
PURPLE_DARK = "#483d8b"
RED = "#8b0000"          # ONLY for violation / type error
RED_FILL = "#f9e6e6"
INDIGO = "#4b0082"       # ONLY for "unknown"
NAVY = "#00008b"         # concrete run or value
NAVY_FILL = "#e6e8f9"
GRAY_DARK = "#555555"
GRAY_MID = "#888888"
GRAY_LIGHT = "#cccccc"
GRAY_FAINT = "#e6e6dc"

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"

def esc(s):
    return html.escape(str(s), quote=True)

def gcd(a, b):
    return math.gcd(a, b)

def divisors(n, max_d=16):
    if n == 0:
        return list(range(1, max_d + 1))
    return [d for d in range(1, n + 1) if n % d == 0]

def svg_header(width, height, title_text, subtitle_text=""):
    lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'  <defs>',
        f'    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{PURPLE_DARK}"/>',
        f'    </marker>',
        f'    <marker id="arrow-navy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">',
        f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{NAVY}"/>',
        f'    </marker>',
        f'    <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">',
        f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{RED}"/>',
        f'    </marker>',
        f'    <marker id="arrow-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">',
        f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{INK}"/>',
        f'    </marker>',
        f'    <marker id="arrow-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{GRAY_MID}"/>',
        f'    </marker>',
        f'  </defs>',
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="{BG}"/>',
        f'  <!-- Title banner -->',
        f'  <text x="32" y="34" font-family="{FONT_SERIF}" font-size="21" font-weight="bold" fill="{INK}">{esc(title_text)}</text>',
    ]
    if subtitle_text:
        lines.append(f'  <text x="32" y="54" font-family="{FONT_SANS}" font-size="13" fill="{GRAY_DARK}">{esc(subtitle_text)}</text>')
    lines.append(f'  <line x1="32" y1="64" x2="{width-32}" y2="64" stroke="{GRAY_LIGHT}" stroke-width="1"/>')
    return "\n".join(lines)

def svg_footer():
    return "</svg>\n"


# ============================================================================
# FIGURE 1: Dependent Type as a Fiber Over (a, b) = (12, 8)
# ============================================================================
def generate_fig1():
    W, H = 900, 620
    # Title <= 12 words: "Gcd(a, b) pulls a singleton set fiber over each input pair" (11 words)
    title = "Gcd(a, b) pulls a singleton set fiber over each input pair"
    subtitle = "A dependent type is an indexed family of sets (a, b) ↦ Gcd(a, b) ⊂ ℕ; for (12, 8), the fiber is {4}"
    out = [svg_header(W, H, title, subtitle)]

    # Left side: Base space (a, b) in {0..16} x {0..16}
    gx0, gy0 = 62, 495
    cell = 20.5
    N = 16

    out.append(f'  <!-- LEFT: Base Space (a, b) -->')
    out.append(f'  <text x="42" y="92" font-family="{FONT_SERIF}" font-size="15.5" font-weight="bold" fill="{INK}">1. Base Space of Input Values: (a, b) ∈ ℕ × ℕ</text>')
    out.append(f'  <text x="42" y="110" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_DARK}">Each cell (a, b) is shaded by the inhabitant of its fiber Gcd(a, b)</text>')

    def cell_xy(a, b):
        cx = gx0 + a * cell + cell / 2.0
        cy = gy0 - b * cell - cell / 2.0
        return cx, cy

    for a in range(N + 1):
        for b in range(N + 1):
            g = gcd(a, b)
            cx, cy = cell_xy(a, b)
            rx = cx - cell / 2.0
            ry = cy - cell / 2.0
            if a == 12 and b == 8:
                fill = PURPLE_FILL
                stroke = NAVY
                sw = 2.2
            elif g == 4:
                fill = "#d2ccf0"
                stroke = PURPLE
                sw = 0.8
            elif g == 1:
                fill = "#f7f6ee"
                stroke = "#dfded4"
                sw = 0.5
            elif g == 2:
                fill = "#ece9f8"
                stroke = "#d5d0ec"
                sw = 0.5
            elif g >= 6:
                fill = "#c2b9ea"
                stroke = "#b0a6e0"
                sw = 0.5
            else:
                fill = "#e2def4"
                stroke = "#cbc5e8"
                sw = 0.5

            out.append(f'  <rect x="{rx:.1f}" y="{ry:.1f}" width="{cell}" height="{cell}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
            txt_col = NAVY if (a == 12 and b == 8) else (PURPLE_DARK if g == 4 else (GRAY_MID if g == 1 else GRAY_DARK))
            fw = "bold" if (a == 12 and b == 8 or g == 4) else "normal"
            fs = 11 if (a == 12 and b == 8) else 9.2
            out.append(f'  <text x="{cx:.1f}" y="{cy+3.3:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="{fs}" font-weight="{fw}" fill="{txt_col}">{g}</text>')

    # Highlight (12, 8) with an outer ring and crosshairs
    cx12, cy8 = cell_xy(12, 8)
    out.append(f'  <line x1="{gx0}" y1="{cy8:.1f}" x2="{cx12 - cell/2:.1f}" y2="{cy8:.1f}" stroke="{NAVY}" stroke-width="1.5" stroke-dasharray="3,2"/>')
    out.append(f'  <line x1="{cx12:.1f}" y1="{gy0}" x2="{cx12:.1f}" y2="{cy8 + cell/2:.1f}" stroke="{NAVY}" stroke-width="1.5" stroke-dasharray="3,2"/>')
    out.append(f'  <rect x="{cx12 - cell/2 - 1.5:.1f}" y="{cy8 - cell/2 - 1.5:.1f}" width="{cell+3}" height="{cell+3}" fill="none" stroke="{NAVY}" stroke-width="2.2" rx="2"/>')

    # Axis labels
    for a in range(0, N + 1, 2):
        cx, _ = cell_xy(a, 0)
        col = NAVY if a == 12 else INK
        fw = "bold" if a == 12 else "normal"
        out.append(f'  <text x="{cx:.1f}" y="{gy0 + 16}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="{fw}" fill="{col}">{a}</text>')
    for b in range(0, N + 1, 2):
        _, cy = cell_xy(0, b)
        col = NAVY if b == 8 else INK
        fw = "bold" if b == 8 else "normal"
        out.append(f'  <text x="{gx0 - 9}" y="{cy + 4:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="11.5" font-weight="{fw}" fill="{col}">{b}</text>')

    out.append(f'  <text x="{gx0 + (N+1)*cell/2:.1f}" y="{gy0 + 36}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-style="italic" fill="{INK}">input a →</text>')
    out.append(f'  <text x="{gx0 - 32}" y="{gy0 - (N+1)*cell/2:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-style="italic" fill="{INK}" transform="rotate(-90 {gx0 - 32} {gy0 - (N+1)*cell/2:.1f})">input b →</text>')

    # Callout on base space for iso-gcd cells (g=4)
    out.append(f'  <text x="42" y="{gy0 + 58}" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">Purple cells (4,4), (4,8), (8,12), (12,8), (12,16)... all carry fiber {{4}}</text>')
    out.append(f'  <text x="42" y="{gy0 + 74}" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_DARK}">Faint cells have coprime inputs: fiber is {{1}}; cell (0,0) has fiber {{0}}</text>')

    # RIGHT SIDE: Pulled-out Fiber over (12, 8)
    fx0 = 472
    fw_box = 396
    fy0 = 122
    fh_box = 428

    out.append(f'  <!-- RIGHT: Pulled-out Fiber Over (12, 8) -->')
    out.append(f'  <text x="{fx0}" y="92" font-family="{FONT_SERIF}" font-size="15.5" font-weight="bold" fill="{INK}">2. Pulled-Out Fiber Over (a=12, b=8)</text>')
    out.append(f'  <text x="{fx0}" y="110" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_DARK}">Refinement selects the unique g with Div(g) = Div(12) ∩ Div(8)</text>')

    # Bundle projection / pullback cone from cell (12,8) to the fiber frame
    out.append(f'  <polygon points="{cx12+cell/2:.1f},{cy8-cell/2:.1f} {fx0},{fy0+20} {fx0},{fy0+fh_box-20} {cx12+cell/2:.1f},{cy8+cell/2:.1f}" fill="{PURPLE_FILL}" fill-opacity="0.32" stroke="none"/>')
    out.append(f'  <line x1="{cx12+cell/2:.1f}" y1="{cy8-cell/2:.1f}" x2="{fx0}" y2="{fy0+20}" stroke="{PURPLE}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    out.append(f'  <line x1="{cx12+cell/2:.1f}" y1="{cy8+cell/2:.1f}" x2="{fx0}" y2="{fy0+fh_box-20}" stroke="{PURPLE}" stroke-width="1.5" stroke-dasharray="4,3"/>')

    # Label on the pullback arrow
    mid_x = (cx12 + cell/2 + fx0) / 2.0 - 2
    out.append(f'  <rect x="{mid_x - 38:.1f}" y="{cy8 - 32:.1f}" width="84" height="36" rx="4" fill="{BG}" stroke="{PURPLE}" stroke-width="1.2"/>')
    out.append(f'  <text x="{mid_x + 4:.1f}" y="{cy8 - 17:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" font-weight="bold" fill="{PURPLE_DARK}">type index</text>')
    out.append(f'  <text x="{mid_x + 4:.1f}" y="{cy8 - 3:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" fill="{NAVY}">(12, 8) ↦ Gcd</text>')

    # Outer Fiber Box (The Ambient Type N and Refined Subset Gcd(12, 8))
    out.append(f'  <rect x="{fx0}" y="{fy0}" width="{fw_box}" height="{fh_box}" rx="8" fill="#faf9f2" stroke="{PURPLE}" stroke-width="2"/>')

    # Header inside Fiber Box: Type definition
    out.append(f'  <rect x="{fx0+12}" y="{fy0+12}" width="{fw_box-24}" height="52" rx="5" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="1.2"/>')
    out.append(f'  <text x="{fx0 + fw_box/2:.1f}" y="{fy0+32}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{INK}">Gcd(12, 8) = {{ g ∈ ℕ  |  Div(g) = Div(12) ∩ Div(8) }}</text>')
    out.append(f'  <text x="{fx0 + fw_box/2:.1f}" y="{fy0+51}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{NAVY}">Div(12) = {{1,2,3,4,6,12}}   ∩   Div(8) = {{1,2,4,8}}   =   {{1, 2, 4}}</text>')

    # Inside fiber box: Vertical number line for g in 0..12
    nl_x = fx0 + 62
    nl_y_bot = fy0 + fh_box - 26
    nl_y_top = fy0 + 90
    max_g = 12
    step_g = (nl_y_bot - nl_y_top) / max_g

    out.append(f'  <text x="{nl_x}" y="{nl_y_top - 10}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{GRAY_DARK}">g ∈ ℕ</text>')
    out.append(f'  <text x="{fx0 + 102}" y="{nl_y_top - 10}" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{GRAY_DARK}">Div(g) vs. target Div(12) ∩ Div(8) = {{1, 2, 4}}</text>')
    out.append(f'  <line x1="{nl_x}" y1="{nl_y_bot + 8}" x2="{nl_x}" y2="{nl_y_top + 2}" stroke="{GRAY_MID}" stroke-width="2" marker-end="url(#arrow-gray)"/>')

    target_divs = {1, 2, 4}

    for g in range(max_g + 1):
        gy = nl_y_bot - g * step_g
        if g == 4:
            # Highlight the singleton refinement type Gcd(12, 8) = {4}
            out.append(f'  <rect x="{fx0 + 14}" y="{gy - 12.5:.1f}" width="{fw_box - 28}" height="25" rx="12.5" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="2"/>')
            out.append(f'  <circle cx="{nl_x}" cy="{gy:.1f}" r="7" fill="{NAVY}" stroke="{BG}" stroke-width="1.5"/>')
            out.append(f'  <text x="{nl_x - 13}" y="{gy + 4:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{NAVY}">g = 4</text>')
            out.append(f'  <text x="{fx0 + 102}" y="{gy + 4:.1f}" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{NAVY}">Div(4) = {{1, 2, 4}} = Div(12) ∩ Div(8)</text>')
            out.append(f'  <rect x="{fx0 + fw_box - 82}" y="{gy - 8.5:.1f}" width="62" height="17" rx="4" fill="{PURPLE}" stroke="none"/>')
            out.append(f'  <text x="{fx0 + fw_box - 51}" y="{gy + 3.5:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="{BG}">IN FIBER</text>')
        else:
            out.append(f'  <circle cx="{nl_x}" cy="{gy:.1f}" r="3.5" fill="{BG}" stroke="{GRAY_MID}" stroke-width="1.3"/>')
            out.append(f'  <text x="{nl_x - 13}" y="{gy + 4:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="11" fill="{GRAY_DARK}">{g}</text>')

            if g == 0:
                div_str = "Div(0) = ℕ  (all naturals; too large)"
                col = GRAY_DARK
            else:
                ds = divisors(g)
                ds_str = "{" + ",".join(str(d) for d in ds) + "}"
                if g in (1, 2):
                    missing = sorted(target_divs - set(ds))
                    div_str = f"Div({g}) = {ds_str} ⊂ {{1,2,4}} (misses {','.join(str(m) for m in missing)})"
                    col = GRAY_DARK
                elif g in (8, 12):
                    extra = sorted(set(ds) - target_divs)
                    div_str = f"Div({g}) = {ds_str} (extra {','.join(str(e) for e in extra)} ∤ {'12' if g==8 else '8'})"
                    col = GRAY_DARK
                elif g in (3, 6):
                    div_str = f"Div({g}) = {ds_str} (3 ∣ 12 but 3 ∤ 8)"
                    col = GRAY_MID
                else:
                    div_str = f"Div({g}) = {ds_str} ≠ {{1, 2, 4}}"
                    col = GRAY_MID
            out.append(f'  <text x="{fx0 + 102}" y="{gy + 4:.1f}" font-family="{FONT_SANS}" font-size="11" fill="{col}">{esc(div_str)}</text>')

    # Bottom takeaway bar
    out.append(f'  <rect x="{fx0}" y="560" width="{fw_box}" height="42" rx="5" fill="{NAVY_FILL}" stroke="{NAVY}" stroke-width="1.2"/>')
    out.append(f'  <text x="{fx0 + fw_box/2:.1f}" y="577" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{NAVY}">Subtyping is Set Containment:  Gcd(12, 8) = {{4}}  ⊂  ℕ</text>')
    out.append(f'  <text x="{fx0 + fw_box/2:.1f}" y="593" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.2" fill="{INK}">Only g = 4 satisfies Div(g) = Div(12) ∩ Div(8); every other natural is excluded.</text>')

    out.append(svg_footer())
    with open("fig-1.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 2: Slicing the Family — Fix b = 8, Vary a ∈ 0..24
# ============================================================================
def generate_fig2():
    W, H = 900, 620
    # Title <= 12 words: "Fixing b = 8 slices the family into a periodic section" (11 words)
    title = "Fixing b = 8 slices the family into a periodic section"
    subtitle = "As input a varies, the fiber Gcd(a, 8) = {g | Div(g) = Div(a) ∩ {1,2,4,8}} jumps among {1}, {2}, {4}, {8}"
    out = [svg_header(W, H, title, subtitle)]

    max_a = 24
    x0 = 96
    x1 = 856
    dx = (x1 - x0) / max_a

    # TOP PANEL: The fiber bundle over a in 0..24 (with b = 8 fixed)
    y_bot = 355
    y_top = 118
    max_g = 10
    dy = (y_bot - y_top) / max_g

    out.append(f'  <!-- TOP PANEL: Bundle of 25 fibers for Gcd(a, 8) -->')
    out.append(f'  <text x="42" y="88" font-family="{FONT_SERIF}" font-size="15.5" font-weight="bold" fill="{INK}">1. Bundle of Fibers Gcd(a, 8) Over Slice b = 8  (each vertical line is one fiber ⊂ ℕ)</text>')

    # Background horizontal guide bands for Div(8) = {1, 2, 4, 8}
    for g in range(max_g + 1):
        gy = y_bot - g * dy
        if g in (1, 2, 4, 8):
            out.append(f'  <rect x="{x0 - 12}" y="{gy - 9:.1f}" width="{x1 - x0 + 24}" height="18" rx="3" fill="{PURPLE_LIGHT}" stroke="none"/>')
            out.append(f'  <line x1="{x0 - 12}" y1="{gy:.1f}" x2="{x1 + 12}" y2="{gy:.1f}" stroke="{PURPLE_MID}" stroke-width="1" stroke-dasharray="3,3"/>')
            out.append(f'  <text x="{x0 - 18}" y="{gy + 4:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{PURPLE_DARK}">g = {g}</text>')
        else:
            out.append(f'  <line x1="{x0}" y1="{gy:.1f}" x2="{x1}" y2="{gy:.1f}" stroke="{GRAY_FAINT}" stroke-width="0.8"/>')
            out.append(f'  <text x="{x0 - 18}" y="{gy + 4:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="11" fill="{GRAY_MID}">{g}</text>')

    # Label on left axis
    out.append(f'  <text x="26" y="{(y_top+y_bot)/2:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-style="italic" fill="{INK}" transform="rotate(-90 26 {(y_top+y_bot)/2:.1f})">Candidate value g in fiber Gcd(a, 8) →</text>')

    # Period-8 background boxes
    for p in range(3):
        px_start = x0 + (p * 8) * dx
        px_end = x0 + ((p + 1) * 8) * dx
        if p % 2 == 1:
            out.append(f'  <rect x="{px_start:.1f}" y="{y_top - 12}" width="{px_end - px_start:.1f}" height="{y_bot - y_top + 24}" fill="#f4f2e6" fill-opacity="0.45" stroke="none"/>')
        out.append(f'  <line x1="{px_start:.1f}" y1="{y_top - 18}" x2="{px_start:.1f}" y2="{y_bot + 16}" stroke="{PURPLE}" stroke-width="1" stroke-dasharray="4,2"/>')
        out.append(f'  <text x="{(px_start + px_end)/2:.1f}" y="{y_top - 6}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">period of length b = 8  (a ∈ [{p*8}..{p*8+7}])</text>')
    out.append(f'  <line x1="{x0 + 24*dx:.1f}" y1="{y_top - 18}" x2="{x0 + 24*dx:.1f}" y2="{y_bot + 16}" stroke="{PURPLE}" stroke-width="1" stroke-dasharray="4,2"/>')

    # Draw vertical fiber lines and un-inhabited dots
    section_pts = []
    for a in range(max_a + 1):
        ax = x0 + a * dx
        g_val = gcd(a, 8)
        gy_val = y_bot - g_val * dy
        section_pts.append((ax, gy_val, a, g_val))

        if a in (0, 12, 13):
            out.append(f'  <line x1="{ax:.1f}" y1="{y_top}" x2="{ax:.1f}" y2="{y_bot}" stroke="{NAVY}" stroke-width="2" stroke-opacity="0.45"/>')
        else:
            out.append(f'  <line x1="{ax:.1f}" y1="{y_top}" x2="{ax:.1f}" y2="{y_bot}" stroke="{GRAY_LIGHT}" stroke-width="1.2"/>')

        for g in range(max_g + 1):
            gy = y_bot - g * dy
            if g != g_val:
                r = 2.2 if g in (1, 2, 4, 8) else 1.5
                col = "#c5bfe0" if g in (1, 2, 4, 8) else GRAY_LIGHT
                out.append(f'  <circle cx="{ax:.1f}" cy="{gy:.1f}" r="{r}" fill="{BG}" stroke="{col}" stroke-width="1"/>')

    # Connect the section with a dashed purple trajectory
    poly_pts = " ".join(f"{ax:.1f},{gy:.1f}" for ax, gy, _, _ in section_pts)
    out.append(f'  <polyline points="{poly_pts}" fill="none" stroke="{PURPLE}" stroke-width="2" stroke-dasharray="4,2"/>')

    # Draw the singleton type pill and inhabitant dot on each fiber
    for ax, gy, a, g_val in section_pts:
        is_special = a in (0, 12, 13)
        pill_fill = NAVY_FILL if is_special else PURPLE_FILL
        pill_stroke = NAVY if is_special else PURPLE
        dot_fill = NAVY if is_special else PURPLE_DARK
        sw = 2.0 if is_special else 1.4
        out.append(f'  <rect x="{ax - 9:.1f}" y="{gy - 9:.1f}" width="18" height="18" rx="9" fill="{pill_fill}" stroke="{pill_stroke}" stroke-width="{sw}"/>')
        out.append(f'  <circle cx="{ax:.1f}" cy="{gy:.1f}" r="4" fill="{dot_fill}"/>')

    # Annotations for the 3 special fibers in the bundle (positioned in clear empty bands!)
    # 1) a = 0: Gcd(0, 8) = {8}
    ax0, gy0, _, _ = section_pts[0]
    out.append(f'  <rect x="{ax0 + 14:.1f}" y="{gy0 - 15:.1f}" width="190" height="32" rx="4" fill="{BG}" stroke="{NAVY}" stroke-width="1.2"/>')
    out.append(f'  <text x="{ax0 + 20:.1f}" y="{gy0 - 2:.1f}" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{NAVY}">a = 0: Gcd(0, 8) = {{8}}</text>')
    out.append(f'  <text x="{ax0 + 20:.1f}" y="{gy0 + 12:.1f}" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Div(0) = ℕ  ⇒  ℕ ∩ Div(8) = Div(8)</text>')

    # 2) a = 12: Gcd(12, 8) = {4} (placed at g=5.5..6.8 level above a=10..12)
    ax12, gy12, _, _ = section_pts[12]
    out.append(f'  <rect x="{ax12 - 140:.1f}" y="{gy12 - 60:.1f}" width="156" height="32" rx="4" fill="{BG}" stroke="{NAVY}" stroke-width="1.2"/>')
    out.append(f'  <line x1="{ax12 - 36:.1f}" y1="{gy12 - 28:.1f}" x2="{ax12 - 5:.1f}" y2="{gy12 - 9:.1f}" stroke="{NAVY}" stroke-width="1.2"/>')
    out.append(f'  <text x="{ax12 - 62:.1f}" y="{gy12 - 46:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{NAVY}">a = 12: Gcd(12, 8) = {{4}}</text>')
    out.append(f'  <text x="{ax12 - 62:.1f}" y="{gy12 - 32:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Div(12) ∩ Div(8) = {{1, 2, 4}}</text>')

    # 3) a = 13: Coprime Gcd(13, 8) = {1} — place callout at g=4.6..5.9 band to the left of the jump at a=16
    ax13, gy13, _, _ = section_pts[13]
    box13_y = y_bot - 6.0 * dy
    out.append(f'  <rect x="{ax13 - 2:.1f}" y="{box13_y:.1f}" width="174" height="32" rx="4" fill="{BG}" stroke="{NAVY}" stroke-width="1.2"/>')
    out.append(f'  <path d="M {ax13 + 12:.1f} {box13_y + 32:.1f} L {ax13 + 1:.1f} {gy13 - 10:.1f}" fill="none" stroke="{NAVY}" stroke-width="1.2" marker-end="url(#arrow-navy)"/>')
    out.append(f'  <text x="{ax13 + 5:.1f}" y="{box13_y + 14:.1f}" font-family="{FONT_SERIF}" font-size="11.2" font-weight="bold" fill="{NAVY}">a = 13 (coprime): Gcd(13, 8) = {{1}}</text>')
    out.append(f'  <text x="{ax13 + 5:.1f}" y="{box13_y + 28:.1f}" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Div(13) ∩ Div(8) = {{1}} = Div(1)</text>')

    # Forbidden horizontal levels callout on right at g=9 (completely open space above a=18..23)
    gy_forbid = y_bot - 9 * dy
    out.append(f'  <rect x="652" y="{gy_forbid - 11:.1f}" width="204" height="22" rx="3" fill="{BG}" stroke="{GRAY_MID}" stroke-width="1"/>')
    out.append(f'  <text x="754" y="{gy_forbid + 4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">g ∉ {{1,2,4,8}} never inhabited (g ∤ 8)</text>')

    # X-axis for a in 0..24
    for a in range(max_a + 1):
        ax = x0 + a * dx
        is_sp = a in (0, 12, 13)
        col = NAVY if is_sp else INK
        fw = "bold" if (is_sp or a % 8 == 0) else "normal"
        out.append(f'  <text x="{ax:.1f}" y="{y_bot + 20}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="{fw}" fill="{col}">{a}</text>')
    out.append(f'  <text x="{(x0+x1)/2:.1f}" y="{y_bot + 40}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13.5" font-style="italic" fill="{INK}">Varying input a (with second input fixed at b = 8) →</text>')

    # BOTTOM PANEL: Why the fiber jumps — Common divisor intersection Div(a) ∩ Div(8)
    by0 = 435
    out.append(f'  <!-- BOTTOM PANEL: Divisor Intersection Table Div(a) ∩ Div(8) -->')
    out.append(f'  <text x="42" y="{by0 - 14}" font-family="{FONT_SERIF}" font-size="15.5" font-weight="bold" fill="{INK}">2. Why the Fiber Moves: Common Divisors Div(a) ∩ Div(8) Determine the Singleton</text>')

    div8_rows = [8, 4, 2, 1]
    row_h = 26
    for idx, d in enumerate(div8_rows):
        ry = by0 + idx * row_h
        out.append(f'  <text x="{x0 - 14}" y="{ry + 17}" text-anchor="end" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INK}">{d} ∣ a ?</text>')
        for a in range(max_a + 1):
            ax = x0 + a * dx
            divides = (a == 0) or (a % d == 0)
            is_gcd = (gcd(a, 8) == d)
            if divides:
                fill = NAVY if (a in (0, 12, 13) and is_gcd) else (PURPLE if is_gcd else PURPLE_FILL)
                txt_col = BG if is_gcd else PURPLE_DARK
                stroke = NAVY if a in (0, 12, 13) else PURPLE
                out.append(f'  <rect x="{ax - 11:.1f}" y="{ry + 2}" width="22" height="21" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
                out.append(f'  <text x="{ax:.1f}" y="{ry + 16.5}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{txt_col}">{d}</text>')
            else:
                out.append(f'  <rect x="{ax - 11:.1f}" y="{ry + 2}" width="22" height="21" rx="3" fill="#f7f6ec" stroke="{GRAY_LIGHT}" stroke-width="0.7"/>')
                out.append(f'  <text x="{ax:.1f}" y="{ry + 16}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{GRAY_LIGHT}">·</text>')

    # Summary row at bottom: Resulting type Gcd(a, 8)
    ry_res = by0 + 4 * row_h + 8
    out.append(f'  <text x="{x0 - 14}" y="{ry_res + 16}" text-anchor="end" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">Gcd(a, 8) =</text>')
    for a in range(max_a + 1):
        ax = x0 + a * dx
        g_val = gcd(a, 8)
        is_sp = a in (0, 12, 13)
        col = NAVY if is_sp else PURPLE_DARK
        bg_c = NAVY_FILL if is_sp else PURPLE_LIGHT
        out.append(f'  <rect x="{ax - 12:.1f}" y="{ry_res + 1}" width="24" height="20" rx="4" fill="{bg_c}" stroke="{col}" stroke-width="{1.4 if is_sp else 0.8}"/>')
        out.append(f'  <text x="{ax:.1f}" y="{ry_res + 15}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" font-weight="bold" fill="{col}">{{{g_val}}}</text>')

    out.append(f'  <text x="{(x0+x1)/2:.1f}" y="596" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" fill="{INK}">A dependent function (a : ℕ) → Gcd(a, 8) is a section of this bundle: at every column a, its return value must land inside the purple ring {{gcd(a,8)}}.</text>')

    out.append(svg_footer())
    with open("fig-2.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 3: Type Error — Landing in the Wrong Fiber
# ============================================================================
def generate_fig3():
    W, H = 900, 620
    # Title <= 12 words: "A type error is a return value landing outside its fiber" (11 words)
    title = "A type error is a return value landing outside its fiber"
    subtitle = "For (a=12, b=8), the target type is the fiber Gcd(12, 8) = {4}; returning g = 2 or g = 8 misses the fiber"
    out = [svg_header(W, H, title, subtitle)]

    x0 = 84
    x1 = 444
    max_a = 16
    dx = (x1 - x0) / max_a
    y_bot = 515
    y_top = 152
    max_g = 12
    dy = (y_bot - y_top) / max_g

    out.append(f'  <!-- LEFT: Bundle over (a, 8) with target fiber at a = 12 -->')
    out.append(f'  <text x="36" y="92" font-family="{FONT_SERIF}" font-size="15.5" font-weight="bold" fill="{INK}">1. Fiber Space Over b = 8 (Focus at Input a = 12)</text>')
    out.append(f'  <text x="36" y="110" font-family="{FONT_SANS}" font-size="12" fill="{GRAY_DARK}">Well-typed output must land in the purple ring at a = 12</text>')

    # Highlight column a = 12 (the active fiber Gcd(12, 8))
    ax12 = x0 + 12 * dx
    out.append(f'  <rect x="{ax12 - 14:.1f}" y="{y_top - 12}" width="28" height="{y_bot - y_top + 24}" rx="6" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.5"/>')
    out.append(f'  <text x="{ax12:.1f}" y="{y_top - 18}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">Fiber Gcd(12, 8)</text>')

    # Horizontal grid lines for g in 0..12
    for g in range(max_g + 1):
        gy = y_bot - g * dy
        out.append(f'  <line x1="{x0}" y1="{gy:.1f}" x2="{x1}" y2="{gy:.1f}" stroke="{GRAY_FAINT}" stroke-width="1"/>')
        if g % 2 == 0 or g == 1:
            col = RED if g in (2, 8, 12) else (NAVY if g == 4 else GRAY_DARK)
            fw = "bold" if g in (2, 4, 8, 12) else "normal"
            out.append(f'  <text x="{x0 - 12}" y="{gy + 4:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="11.5" font-weight="{fw}" fill="{col}">g = {g}</text>')

    # Draw vertical fibers for a in 0..16
    for a in range(max_a + 1):
        ax = x0 + a * dx
        g_true = gcd(a, 8)
        gy_true = y_bot - g_true * dy
        if a != 12:
            out.append(f'  <line x1="{ax:.1f}" y1="{y_top}" x2="{ax:.1f}" y2="{y_bot}" stroke="{GRAY_LIGHT}" stroke-width="0.9"/>')
            out.append(f'  <circle cx="{ax:.1f}" cy="{gy_true:.1f}" r="5.5" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="1.2"/>')
            out.append(f'  <circle cx="{ax:.1f}" cy="{gy_true:.1f}" r="2.2" fill="{PURPLE_DARK}"/>')
        if a % 2 == 0:
            col = NAVY if a == 12 else INK
            fw = "bold" if a == 12 else "normal"
            out.append(f'  <text x="{ax:.1f}" y="{y_bot + 22}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="{fw}" fill="{col}">{a}</text>')

    out.append(f'  <text x="{(x0+x1)/2:.1f}" y="{y_bot + 42}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-style="italic" fill="{INK}">input a (with b = 8) →</text>')

    gy4 = y_bot - 4 * dy
    gy8 = y_bot - 8 * dy
    gy2 = y_bot - 2 * dy
    gy12 = y_bot - 12 * dy

    # Buggy horizontal line g = b = 8 (returning b unchanged!)
    out.append(f'  <line x1="{x0}" y1="{gy8:.1f}" x2="{ax12 - 10:.1f}" y2="{gy8:.1f}" stroke="{RED}" stroke-width="1.8" stroke-dasharray="5,3"/>')
    out.append(f'  <text x="{x0 + 6}" y="{gy8 - 7:.1f}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED}">buggy program: return b (= 8)</text>')

    # Point at (a=8, g=8) vs (a=12, g=8)
    ax8 = x0 + 8 * dx
    out.append(f'  <circle cx="{ax8:.1f}" cy="{gy8:.1f}" r="7" fill="none" stroke="{PURPLE_DARK}" stroke-width="2"/>')
    out.append(f'  <path d="M {ax8 + 8:.1f} {gy8 - 6:.1f} Q {(ax8+ax12)/2:.1f} {gy8 - 26:.1f} {ax12 - 10:.1f} {gy8 - 4:.1f}" fill="none" stroke="{RED}" stroke-width="1.6" marker-end="url(#arrow-red)"/>')
    out.append(f'  <text x="{(ax8+ax12)/2:.1f}" y="{gy8 - 19:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="{RED}">lands in Gcd(8,8), wrong fiber for a=12!</text>')

    # True inhabitant at (12, 4)
    out.append(f'  <circle cx="{ax12:.1f}" cy="{gy4:.1f}" r="10" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="2.5"/>')
    out.append(f'  <circle cx="{ax12:.1f}" cy="{gy4:.1f}" r="4.5" fill="{NAVY}"/>')

    # Wrong inhabitants at (12, 8), (12, 2), (12, 12) marked with dark red X
    for gy_err, lbl in [(gy12, "g=12"), (gy8, "g=8"), (gy2, "g=2")]:
        out.append(f'  <circle cx="{ax12:.1f}" cy="{gy_err:.1f}" r="8.5" fill="{RED_FILL}" stroke="{RED}" stroke-width="2"/>')
        out.append(f'  <line x1="{ax12 - 4.5:.1f}" y1="{gy_err - 4.5:.1f}" x2="{ax12 + 4.5:.1f}" y2="{gy_err + 4.5:.1f}" stroke="{RED}" stroke-width="2.2"/>')
        out.append(f'  <line x1="{ax12 - 4.5:.1f}" y1="{gy_err + 4.5:.1f}" x2="{ax12 + 4.5:.1f}" y2="{gy_err - 4.5:.1f}" stroke="{RED}" stroke-width="2.2"/>')

    # RIGHT PANEL: Detailed Anatomy of the 3 Type Errors vs 1 Valid Inhabitant for Gcd(12, 8)
    rx0 = 488
    rw = 380
    out.append(f'  <!-- RIGHT: Divisor-Set Proof Obligations at (a=12, b=8) -->')
    out.append(f'  <text x="{rx0}" y="92" font-family="{FONT_SERIF}" font-size="15.5" font-weight="bold" fill="{INK}">2. Why Wrong Candidates Fail the Predicate</text>')
    out.append(f'  <text x="{rx0}" y="110" font-family="{FONT_SANS}" font-size="12" fill="{GRAY_DARK}">Required type predicate:  Div(g) = Div(12) ∩ Div(8) = {{1, 2, 4}}</text>')

    cards = [
        {
            "g": 12,
            "gy": gy12,
            "cy": 132,
            "ok": False,
            "title": "TYPE ERROR: Candidate g = 12  (returns input a)",
            "wrong_fiber": "Inhabits Gcd(12, 0) or Gcd(12, 12), NOT Gcd(12, 8)",
            "violation": "12 ∤ 8  (Div(12) contains {3, 6, 12} outside Div(8))",
            "divs": [1, 2, 3, 4, 6, 12],
        },
        {
            "g": 8,
            "gy": gy8,
            "cy": 244,
            "ok": False,
            "title": "TYPE ERROR: Candidate g = 8  (returns input b)",
            "wrong_fiber": "Inhabits Gcd(8, 8) and Gcd(16, 8), NOT Gcd(12, 8)",
            "violation": "8 ∤ 12  (divisor 8 ∈ Div(8) fails to divide a = 12)",
            "divs": [1, 2, 4, 8],
        },
        {
            "g": 4,
            "gy": gy4,
            "cy": 356,
            "ok": True,
            "title": "WELL-TYPED: Candidate g = 4  ∈  Gcd(12, 8)",
            "wrong_fiber": "Unique inhabitant of fiber Gcd(12, 8) = {4}",
            "violation": "Div(4) = {1, 2, 4} = Div(12) ∩ Div(8)   (exact match)",
            "divs": [1, 2, 4],
        },
        {
            "g": 2,
            "gy": gy2,
            "cy": 468,
            "ok": False,
            "title": "TYPE ERROR: Candidate g = 2  (non-maximal common divisor)",
            "wrong_fiber": "Inhabits Gcd(2, 8) and Gcd(6, 8), NOT Gcd(12, 8)",
            "violation": "4 ∣ 12 ∧ 4 ∣ 8 but 4 ∤ 2  (Div(2) = {1, 2} misses 4)",
            "divs": [1, 2],
        },
    ]

    all_check_divs = [1, 2, 3, 4, 6, 8, 12]
    target_set = {1, 2, 4}

    for c in cards:
        cy = c["cy"]
        ch = 98
        ok = c["ok"]
        stroke_c = PURPLE if ok else RED
        fill_c = PURPLE_LIGHT if ok else "#fdf3f3"
        hdr_c = NAVY if ok else RED
        marker = "url(#arrow-navy)" if ok else "url(#arrow-red)"

        out.append(f'  <path d="M {ax12 + 12:.1f} {c["gy"]:.1f} C {ax12 + 45:.1f} {c["gy"]:.1f}, {rx0 - 35:.1f} {cy + ch/2:.1f}, {rx0 - 4:.1f} {cy + ch/2:.1f}" fill="none" stroke="{stroke_c}" stroke-width="1.8" marker-end="{marker}"/>')

        out.append(f'  <rect x="{rx0}" y="{cy}" width="{rw}" height="{ch}" rx="6" fill="{fill_c}" stroke="{stroke_c}" stroke-width="1.8"/>')
        out.append(f'  <text x="{rx0 + 12}" y="{cy + 20}" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{hdr_c}">{esc(c["title"])}</text>')
        out.append(f'  <text x="{rx0 + 12}" y="{cy + 37}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">{esc(c["wrong_fiber"])}</text>')
        out.append(f'  <text x="{rx0 + 12}" y="{cy + 54}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{hdr_c}">{esc(c["violation"])}</text>')

        out.append(f'  <text x="{rx0 + 12}" y="{cy + 80}" font-family="{FONT_SERIF}" font-size="11.5" fill="{INK}">Div({c["g"]}):</text>')
        px_start = rx0 + 68
        for idx, d in enumerate(all_check_divs):
            px = px_start + idx * 42
            py = cy + 65
            in_g = d in c["divs"]
            in_target = d in target_set
            if in_g and in_target:
                p_fill = PURPLE_FILL if ok else "#e4e0f5"
                p_str = PURPLE
                t_col = INK
                tag = ""
            elif in_g and not in_target:
                p_fill = RED
                p_str = RED
                t_col = BG
                tag = "extra!"
            elif (not in_g) and in_target:
                p_fill = BG
                p_str = RED
                t_col = RED
                tag = "missed!"
            else:
                p_fill = "#f4f3ea"
                p_str = GRAY_LIGHT
                t_col = GRAY_LIGHT
                tag = ""

            dash = 'stroke-dasharray="2,2"' if ((not in_g) and in_target) else ""
            out.append(f'  <rect x="{px}" y="{py}" width="36" height="22" rx="4" fill="{p_fill}" stroke="{p_str}" stroke-width="1.3" {dash}/>')
            out.append(f'  <text x="{px + 18}" y="{py + 15}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{t_col}">{d}</text>')
            if tag:
                out.append(f'  <text x="{px + 18}" y="{py + 31}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9.5" font-weight="bold" fill="{RED}">{tag}</text>')

    out.append(svg_footer())
    with open("fig-3.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 4: Euclid's Algorithm as Fiber-Preserving Transport Across (a, b)
# ============================================================================
def generate_fig4():
    W, H = 900, 620
    # Title <= 12 words: "Euclid steps across the base plane while preserving the fiber" (11 words)
    title = "Euclid steps across the base plane while preserving the fiber"
    subtitle = "Each step (x, y) ↦ (y, x mod y) moves to a simpler base point with the exact same fiber Div(x) ∩ Div(y)"
    out = [svg_header(W, H, title, subtitle)]

    gx0, gy0 = 58, 510
    cell = 17.5
    max_x, max_y = 21, 21

    out.append(f'  <!-- LEFT: Base Plane 0..21 x 0..21 with Two Euclid Trajectories -->')
    out.append(f'  <text x="36" y="92" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">1. Base Plane (x, y) ∈ [0..21]²: Level Sets of Equal Fiber</text>')
    out.append(f'  <text x="36" y="110" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_DARK}">Bottom row y = 0 is the stopping boundary where Gcd(x, 0) = {{x}}</text>')

    def c_xy(x, y):
        return gx0 + x * cell + cell / 2.0, gy0 - y * cell - cell / 2.0

    # Highlight y = 0 bottom row
    out.append(f'  <rect x="{gx0 - 2}" y="{gy0 - cell - 2:.1f}" width="{(max_x+1)*cell + 4:.1f}" height="{cell + 4:.1f}" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.5" rx="2"/>')

    for x in range(max_x + 1):
        for y in range(max_y + 1):
            g = gcd(x, y)
            cx, cy = c_xy(x, y)
            rx, ry = cx - cell/2.0, cy - cell/2.0
            if (x, y) in [(12, 8), (8, 4), (4, 0)]:
                fill = NAVY_FILL
                stroke = NAVY
                sw = 1.8
            elif (x, y) in [(21, 13), (13, 8), (8, 5), (5, 3), (3, 2), (2, 1), (1, 0)]:
                fill = PURPLE_FILL
                stroke = PURPLE_DARK
                sw = 1.6
            elif g == 4:
                fill = "#dcd6f5"
                stroke = "#b8aee8"
                sw = 0.6
            else:
                fill = "#f8f7ef" if g == 1 else "#eeeaf9"
                stroke = "#e2e1d5"
                sw = 0.4

            out.append(f'  <rect x="{rx:.1f}" y="{ry:.1f}" width="{cell}" height="{cell}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
            if (x, y) in [(12, 8), (8, 4), (4, 0), (21, 13), (13, 8), (8, 5), (5, 3), (3, 2), (2, 1), (1, 0)] or g == 4 or y == 0:
                col = NAVY if (x, y) in [(12, 8), (8, 4), (4, 0)] else (PURPLE_DARK if g == 4 or (x, y) in [(21, 13), (13, 8), (8, 5), (5, 3), (3, 2), (2, 1), (1, 0)] else GRAY_DARK)
                fw = "bold" if (g == 4 or y == 0 or (x, y) in [(21, 13), (13, 8), (8, 5), (5, 3), (3, 2), (2, 1)]) else "normal"
                out.append(f'  <text x="{cx:.1f}" y="{cy + 3.2:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="8.5" font-weight="{fw}" fill="{col}">{g}</text>')

    # Axis ticks
    for x in range(0, max_x + 1, 2):
        cx, _ = c_xy(x, 0)
        out.append(f'  <text x="{cx:.1f}" y="{gy0 + 15}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="10.5" fill="{INK}">{x}</text>')
    for y in range(0, max_y + 1, 2):
        _, cy = c_xy(0, y)
        out.append(f'  <text x="{gx0 - 8}" y="{cy + 3.5:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="10.5" fill="{INK}">{y}</text>')
    out.append(f'  <text x="{gx0 + (max_x+1)*cell/2:.1f}" y="{gy0 + 33}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-style="italic" fill="{INK}">state x (at y = 0, return x ∈ Gcd(x, 0) = {{x}}) →</text>')
    out.append(f'  <text x="{gx0 - 28}" y="{gy0 - (max_y+1)*cell/2:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-style="italic" fill="{INK}" transform="rotate(-90 {gx0 - 28} {gy0 - (max_y+1)*cell/2:.1f})">state y →</text>')

    # Draw Run A arrows: (12, 8) -> (8, 4) -> (4, 0)
    runA = [(12, 8), (8, 4), (4, 0)]
    for i in range(len(runA) - 1):
        x1, y1 = c_xy(*runA[i])
        x2, y2 = c_xy(*runA[i+1])
        out.append(f'  <path d="M {x1:.1f} {y1:.1f} Q {(x1+x2)/2 - 12:.1f} {(y1+y2)/2 - 14:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{NAVY}" stroke-width="2.4" marker-end="url(#arrow-navy)"/>')

    # Draw Run B arrows: (21, 13) -> (13, 8) -> (8, 5) -> (5, 3) -> (3, 2) -> (2, 1) -> (1, 0)
    runB = [(21, 13), (13, 8), (8, 5), (5, 3), (3, 2), (2, 1), (1, 0)]
    for i in range(len(runB) - 1):
        x1, y1 = c_xy(*runB[i])
        x2, y2 = c_xy(*runB[i+1])
        out.append(f'  <path d="M {x1:.1f} {y1:.1f} Q {(x1+x2)/2 + 8:.1f} {(y1+y2)/2 - 8:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{PURPLE_DARK}" stroke-width="2" marker-end="url(#arrow-purple)"/>')

    # Labels on trajectories in plane
    cx12_8, cy12_8 = c_xy(12, 8)
    out.append(f'  <rect x="{cx12_8 - 54:.1f}" y="{cy12_8 - 34:.1f}" width="110" height="20" rx="3" fill="{BG}" stroke="{NAVY}" stroke-width="1.2"/>')
    out.append(f'  <text x="{cx12_8 + 1:.1f}" y="{cy12_8 - 20:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">Run A: (12, 8) → {{4}}</text>')

    cx21_13, cy21_13 = c_xy(21, 13)
    out.append(f'  <rect x="{cx21_13 - 150:.1f}" y="{cy21_13 - 33:.1f}" width="154" height="20" rx="3" fill="{BG}" stroke="{PURPLE_DARK}" stroke-width="1.2"/>')
    out.append(f'  <text x="{cx21_13 - 73:.1f}" y="{cy21_13 - 19:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE_DARK}">Run B (coprime): (21,13) → {{1}}</text>')

    # RIGHT PANEL: Fiber-Preserving Transport Diagram
    rx0 = 468
    rw = 404
    out.append(f'  <!-- RIGHT: Fiber Equality Chains (Transport Along Loop Invariant) -->')
    out.append(f'  <text x="{rx0}" y="92" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">2. Dependent Type Equality Along Each Euclid Step</text>')
    out.append(f'  <text x="{rx0}" y="110" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_DARK}">Theorem: Div(x) ∩ Div(y) = Div(y) ∩ Div(x mod y)  ⇒  Gcd(x,y) = Gcd(y, x mod y)</text>')

    # Box 1: Run A (12, 8) -> (8, 4) -> (4, 0) with pulled-out fibers
    b1_y = 126
    b1_h = 236
    out.append(f'  <rect x="{rx0}" y="{b1_y}" width="{rw}" height="{b1_h}" rx="6" fill="#faf9f2" stroke="{NAVY}" stroke-width="1.6"/>')
    out.append(f'  <text x="{rx0 + 14}" y="{b1_y + 22}" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{NAVY}">Run A: (12, 8) → (8, 4) → (4, 0)   [Invariant Fiber = {{4}}]</text>')

    steps_A = [
        ("Start", "(12, 8)", "Gcd(12, 8)", "Div(12) ∩ Div(8) = {1,2,4}"),
        ("Step 1", "(8, 4)", "Gcd(8, 4)", "Div(8) ∩ Div(4) = {1,2,4}"),
        ("Halt (y=0)", "(4, 0)", "Gcd(4, 0)", "Div(4) ∩ ℕ = {1,2,4}"),
    ]

    col_xs = [rx0 + 70, rx0 + 202, rx0 + 334]
    f_top = b1_y + 58
    f_bot = b1_y + 168

    for idx, (st_lbl, pair_lbl, gcd_lbl, div_lbl) in enumerate(steps_A):
        cx = col_xs[idx]
        out.append(f'  <text x="{cx}" y="{b1_y + 42}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{GRAY_DARK}">{st_lbl}: {pair_lbl}</text>')
        out.append(f'  <rect x="{cx - 48}" y="{f_top}" width="96" height="{f_bot - f_top}" rx="6" fill="{BG}" stroke="{PURPLE}" stroke-width="1.4"/>')
        out.append(f'  <text x="{cx}" y="{f_top + 16}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">{gcd_lbl}</text>')

        nl_top = f_top + 28
        nl_bot = f_bot - 12
        out.append(f'  <line x1="{cx - 10}" y1="{nl_bot}" x2="{cx - 10}" y2="{nl_top}" stroke="{GRAY_MID}" stroke-width="1.2"/>')
        for g_tick in [0, 2, 4, 6, 8]:
            ty = nl_bot - (g_tick / 8.0) * (nl_bot - nl_top)
            if g_tick == 4:
                out.append(f'  <rect x="{cx - 38}" y="{ty - 9:.1f}" width="76" height="18" rx="9" fill="{PURPLE_FILL}" stroke="{NAVY}" stroke-width="1.5"/>')
                out.append(f'  <circle cx="{cx - 10}" cy="{ty:.1f}" r="4.5" fill="{NAVY}"/>')
                out.append(f'  <text x="{cx + 12}" y="{ty + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{NAVY}">g = 4</text>')
            else:
                out.append(f'  <circle cx="{cx - 10}" cy="{ty:.1f}" r="2" fill="{BG}" stroke="{GRAY_MID}" stroke-width="1"/>')
                out.append(f'  <text x="{cx - 20}" y="{ty + 3.5:.1f}" text-anchor="end" font-family="{FONT_SANS}" font-size="9.5" fill="{GRAY_MID}">{g_tick}</text>')

        out.append(f'  <text x="{cx}" y="{f_bot + 16}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" fill="{INK}">{div_lbl}</text>')

    ty4 = (f_bot - 12) - (4 / 8.0) * ((f_bot - 12) - (f_top + 28))
    for i in range(2):
        x_left = col_xs[i] + 48
        x_right = col_xs[i+1] - 48
        xm = (x_left + x_right) / 2.0
        out.append(f'  <line x1="{x_left - 8}" y1="{ty4:.1f}" x2="{x_right + 8}" y2="{ty4:.1f}" stroke="{NAVY}" stroke-width="2" stroke-dasharray="3,2"/>')
        out.append(f'  <rect x="{xm - 13:.1f}" y="{ty4 - 22:.1f}" width="26" height="16" rx="3" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="1"/>')
        out.append(f'  <text x="{xm:.1f}" y="{ty4 - 10:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{NAVY}">=</text>')

    out.append(f'  <text x="{rx0 + rw/2:.1f}" y="{b1_y + b1_h - 12}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{NAVY}">At y = 0: x = 4 ∈ Gcd(4, 0) = Gcd(8, 4) = Gcd(12, 8)  (Q.E.D. without extra proof!)</text>')

    # Box 2: Second pair — Run B: Coprime Fibonacci pair (21, 13) -> ... -> (1, 0) AND Edge case (0, 0) -> {0}
    b2_y = 378
    b2_h = 222
    out.append(f'  <rect x="{rx0}" y="{b2_y}" width="{rw}" height="{b2_h}" rx="6" fill="#faf9f2" stroke="{PURPLE_DARK}" stroke-width="1.6"/>')
    out.append(f'  <text x="{rx0 + 14}" y="{b2_y + 22}" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{PURPLE_DARK}">Run B (Coprime Pair): (21, 13) → 6 steps → (1, 0)   [Fiber = {{1}}]</text>')
    out.append(f'  <text x="{rx0 + 14}" y="{b2_y + 40}" font-family="{FONT_SANS}" font-size="11.2" fill="{INK}">Worst-case Fibonacci inputs step across 7 base points, all sharing fiber {{1}}:</text>')

    chain_y = b2_y + 62
    for idx, (bx, by) in enumerate(runB):
        px = rx0 + 14 + idx * 54
        out.append(f'  <rect x="{px}" y="{chain_y - 14}" width="45" height="36" rx="4" fill="{PURPLE_FILL}" stroke="{PURPLE_DARK}" stroke-width="1.2"/>')
        out.append(f'  <text x="{px + 22.5}" y="{chain_y}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="{INK}">({bx},{by})</text>')
        out.append(f'  <text x="{px + 22.5}" y="{chain_y + 15}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" font-weight="bold" fill="{PURPLE_DARK}">{{1}}</text>')
        if idx < len(runB) - 1:
            out.append(f'  <text x="{px + 49.5}" y="{chain_y + 5}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" font-weight="bold" fill="{NAVY}">=</text>')

    out.append(f'  <text x="{rx0 + 14}" y="{chain_y + 42}" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Div(21) ∩ Div(13) = {{1,3,7,21}} ∩ {{1,13}} = {{1}} = Div(1), so fiber is {{1}} throughout.</text>')

    # Edge Case Callout inside Box 2: Singularity at the Origin (0, 0) -> {0}
    ec_y = b2_y + 122
    out.append(f'  <rect x="{rx0 + 12}" y="{ec_y}" width="{rw - 24}" height="86" rx="5" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.3"/>')
    out.append(f'  <text x="{rx0 + 22}" y="{ec_y + 20}" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INK}">Origin Fiber (0, 0): Why Gcd(0, 0) = {{0}} Without Special Cases</text>')
    out.append(f'  <text x="{rx0 + 22}" y="{ec_y + 39}" font-family="{FONT_SANS}" font-size="11.2" fill="{INK}">• Every natural d divides 0 (since 0 = 0 · d), so Div(0) = ℕ.</text>')
    out.append(f'  <text x="{rx0 + 22}" y="{ec_y + 56}" font-family="{FONT_SANS}" font-size="11.2" fill="{INK}">• At (0, 0): Div(g) = Div(0) ∩ Div(0) = ℕ, holding ONLY for g = 0.</text>')
    out.append(f'  <text x="{rx0 + 22}" y="{ec_y + 74}" font-family="{FONT_SANS}" font-size="11.2" font-weight="bold" fill="{NAVY}">• Thus Gcd(0, 0) = {{0}} is the unique fiber inhabited by 0.</text>')

    out.append(svg_footer())
    with open("fig-4.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 5: Codillon Live Type-Inspector — Dependent Fiber View in the Editor
# ============================================================================
def generate_fig5():
    W, H = 900, 620
    # Title <= 12 words: "Codillon checks that every return path lands in Gcd(a, b)" (11 words)
    title = "Codillon checks that every return path lands in Gcd(a, b)"
    subtitle = "Per-instruction dependent fiber display: the loop preserves Gcd(x, y) = Gcd(a, b); a bad return is caught visually"
    out = [svg_header(W, H, title, subtitle)]

    # LEFT PANEL: Structured WebAssembly / Codillon Code with Per-Instruction Fiber Badges
    lx0 = 32
    lw = 432
    ly0 = 82
    lh = 520

    out.append(f'  <!-- LEFT: Codillon Structured Wasm Editor Panel -->')
    out.append(f'  <rect x="{lx0}" y="{ly0}" width="{lw}" height="{lh}" rx="8" fill="#faf9f2" stroke="{GRAY_MID}" stroke-width="1.5"/>')
    out.append(f'  <rect x="{lx0}" y="{ly0}" width="{lw}" height="32" rx="8" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="1.2"/>')
    out.append(f'  <text x="{lx0 + 14}" y="{ly0 + 21}" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{INK}">Codillon Structured Wasm:  fn euclid(a: ℕ, b: ℕ) → Gcd(a, b)</text>')

    # Function signature & symbolic target fiber badge
    out.append(f'  <rect x="{lx0 + 10}" y="{ly0 + 39}" width="{lw - 20}" height="40" rx="5" fill="{BG}" stroke="{PURPLE}" stroke-width="1.2"/>')
    out.append(f'  <text x="{lx0 + 18}" y="{ly0 + 55}" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">Target Return Fiber: Gcd(a, b) = {{ g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }}</text>')
    out.append(f'  <text x="{lx0 + 18}" y="{ly0 + 71}" font-family="{FONT_SANS}" font-size="11" fill="{NAVY}">Probe: (a=12, b=8) ⇒ target fiber {{4}}   |   symbolic g* in indigo</text>')

    insts = [
        ("1", "local.set (x, y) ← (a, b)", "x : {a},  y : {b}", "Gcd(x, y) = Gcd(a, b)", "(12, 8) → {4}", PURPLE, BG),
        ("2", "loop $euclid", "invariant: Div(x) ∩ Div(y) = Div(a) ∩ Div(b)", "Fiber Gcd(x, y) == Gcd(a, b)", "(12,8) → (8,4) → (4,0)", PURPLE, PURPLE_LIGHT),
        ("3", "  if (y == 0) then", "branch guard refines type of y:", "y : {0}  ⇒  Div(y) = Div(0) = ℕ", "iter 2: x = 4, y = 0", NAVY, NAVY_FILL),
        ("4", "    return x   ✓ [WELL-TYPED]", "Div(x) = Div(x) ∩ ℕ = Div(a) ∩ Div(b)", "x ∈ Gcd(x, 0) = Gcd(x, y) = Gcd(a, b)", "returns 4 ∈ {4}", NAVY, "#eef0fc"),
        ("5", "    return y   ✗ [WHAT IF BUG?]", "y : {0} ⇒ lands in fiber Gcd(0, 0) = {0}", "TYPE ERROR: {0} ≠ Gcd(a, b) for a∨b > 0", "0 ∉ {4} (wrong fiber!)", RED, RED_FILL),
        ("6", "  else", "branch guard: y > 0", "step (x, y) ← (y, x mod y)", "(12,8)↦(8,4)↦(4,0)", PURPLE, BG),
        ("7", "    br $euclid", "preserves Div(y) ∩ Div(x mod y) = Div(x) ∩ Div(y)", "Gcd(y, x mod y) = Gcd(x, y) = Gcd(a, b)", "keeps fiber {4}", PURPLE, BG),
    ]

    iy = ly0 + 86
    for num, code, line1, line2, probe, col, bg_c in insts:
        ih = 56 if num in ("4", "5") else 52
        sw = 1.9 if num in ("4", "5") else 1.1
        out.append(f'  <rect x="{lx0 + 10}" y="{iy}" width="{lw - 20}" height="{ih}" rx="5" fill="{bg_c}" stroke="{col}" stroke-width="{sw}"/>')
        out.append(f'  <text x="{lx0 + 18}" y="{iy + 16}" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{col if num in ("4","5") else INK}">{esc(code)}</text>')
        out.append(f'  <rect x="{lx0 + lw - 156}" y="{iy + 4}" width="138" height="16" rx="3" fill="{BG}" stroke="{col}" stroke-width="0.9"/>')
        out.append(f'  <text x="{lx0 + lw - 87}" y="{iy + 15.5}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.2" font-weight="bold" fill="{col}">{esc(probe)}</text>')
        out.append(f'  <text x="{lx0 + 22}" y="{iy + 32}" font-family="{FONT_SANS}" font-size="10.8" fill="{GRAY_DARK}">{esc(line1)}</text>')
        out.append(f'  <text x="{lx0 + 22}" y="{iy + 46}" font-family="{FONT_SERIF}" font-size="11" font-weight="bold" fill="{col}">{esc(line2)}</text>')
        iy += ih + 6

    # RIGHT PANEL: Symbolic Fiber Alignment + Live Fiber Inspector
    rx0 = 480
    rw = 388

    out.append(f'  <!-- RIGHT TOP: Symbolic Dependent Fiber Alignment -->')
    out.append(f'  <text x="{rx0}" y="96" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">Symbolic Fiber Verification (All Inputs a, b)</text>')
    out.append(f'  <text x="{rx0}" y="114" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_DARK}">Indigo marks unknown symbolic value g*; refinement proves fibers coincide</text>')

    sb_y = 124
    sb_h = 206
    out.append(f'  <rect x="{rx0}" y="{sb_y}" width="{rw}" height="{sb_h}" rx="7" fill="#faf9f2" stroke="{INDIGO}" stroke-width="1.6"/>')

    scols = [
        (rx0 + 68, "Entry Fiber", "Gcd(a, b)", "g* (unknown)", INDIGO),
        (rx0 + 194, "Loop Fiber", "Gcd(x, y)", "same g*", INDIGO),
        (rx0 + 320, "Exit (y = 0)", "Gcd(x, 0) = {x}", "x = g* ✓", NAVY),
    ]

    sf_top = sb_y + 46
    sf_bot = sb_y + 172
    gy_sym = sf_top + 52
    gy_zero = sf_bot - 18

    for cx, hdr, sub, badge, col in scols:
        out.append(f'  <text x="{cx}" y="{sb_y + 20}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{INK}">{hdr}</text>')
        out.append(f'  <text x="{cx}" y="{sb_y + 36}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{col}">{sub}</text>')
        out.append(f'  <rect x="{cx - 52}" y="{sf_top}" width="104" height="{sf_bot - sf_top}" rx="6" fill="{BG}" stroke="{PURPLE}" stroke-width="1.3"/>')
        nl_spine_x = cx - 32
        out.append(f'  <line x1="{nl_spine_x}" y1="{sf_bot - 8}" x2="{nl_spine_x}" y2="{sf_top + 10}" stroke="{GRAY_MID}" stroke-width="1.3" marker-end="url(#arrow-gray)"/>')

        # Symbolic g* ring
        out.append(f'  <rect x="{cx - 44}" y="{gy_sym - 11}" width="88" height="22" rx="11" fill="{PURPLE_FILL}" stroke="{INDIGO}" stroke-width="1.8"/>')
        out.append(f'  <circle cx="{nl_spine_x}" cy="{gy_sym}" r="5" fill="{INDIGO}"/>')
        out.append(f'  <text x="{cx + 8}" y="{gy_sym + 4}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="{INDIGO}">{badge}</text>')

        # 0 tick at bottom of fiber
        out.append(f'  <circle cx="{nl_spine_x}" cy="{gy_zero}" r="3" fill="{BG}" stroke="{GRAY_MID}" stroke-width="1"/>')
        if col != NAVY:
            out.append(f'  <text x="{nl_spine_x - 7}" y="{gy_zero + 3.5}" text-anchor="end" font-family="{FONT_SANS}" font-size="10" fill="{GRAY_DARK}">0</text>')

    # At Exit column (Col 3), show `return x` hitting g* vs `return y` (=0) hitting 0 (RED TYPE ERROR)
    cx3 = scols[2][0]
    nl3_x = cx3 - 32
    out.append(f'  <circle cx="{nl3_x}" cy="{gy_zero}" r="6.5" fill="{RED_FILL}" stroke="{RED}" stroke-width="1.8"/>')
    out.append(f'  <line x1="{nl3_x - 3.5}" y1="{gy_zero - 3.5}" x2="{nl3_x + 3.5}" y2="{gy_zero + 3.5}" stroke="{RED}" stroke-width="1.8"/>')
    out.append(f'  <line x1="{nl3_x - 3.5}" y1="{gy_zero + 3.5}" x2="{nl3_x + 3.5}" y2="{gy_zero - 3.5}" stroke="{RED}" stroke-width="1.8"/>')
    out.append(f'  <text x="{nl3_x - 10}" y="{gy_zero + 3.5}" text-anchor="end" font-family="{FONT_SANS}" font-size="10" fill="{RED}">0</text>')
    out.append(f'  <text x="{cx3 + 10}" y="{gy_zero + 4}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="{RED}">return y=0 ✗</text>')

    # Horizontal transport connectors across symbolic fibers
    for i in range(2):
        x_l = scols[i][0] + 44
        x_r = scols[i+1][0] - 44
        xm = (x_l + x_r) / 2.0
        out.append(f'  <line x1="{x_l}" y1="{gy_sym}" x2="{x_r}" y2="{gy_sym}" stroke="{INDIGO}" stroke-width="2" stroke-dasharray="3,2"/>')
        out.append(f'  <text x="{xm}" y="{gy_sym - 6}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INDIGO}">=</text>')

    out.append(f'  <text x="{rx0 + rw/2:.1f}" y="{sb_y + sb_h - 10}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.2" fill="{INK}">Even with g* unknown (indigo), Codillon proves Gcd(x,0) = {{x}} = Gcd(a,b)!</text>')

    # RIGHT BOTTOM: Concrete Trace Strip & Fiber Target Comparison for (12, 8) and (21, 0)
    rb_y = 348
    rb_h = 254
    out.append(f'  <!-- RIGHT BOTTOM: Concrete Fiber Target Inspector -->')
    out.append(f'  <rect x="{rx0}" y="{rb_y}" width="{rw}" height="{rb_h}" rx="7" fill="#faf9f2" stroke="{PURPLE}" stroke-width="1.6"/>')
    out.append(f'  <text x="{rx0 + 14}" y="{rb_y + 22}" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">Live Fiber Target Check in Codillon Gutter</text>')
    out.append(f'  <text x="{rx0 + 14}" y="{rb_y + 39}" font-family="{FONT_SANS}" font-size="11.2" fill="{GRAY_DARK}">Comparing well-typed `return x` vs. ill-typed `return y` at loop exit (y = 0):</text>')

    nl_x0 = rx0 + 28
    nl_x1 = rx0 + rw - 24
    nl_y1 = rb_y + 98
    max_n = 12
    dx_n = (nl_x1 - nl_x0) / max_n

    out.append(f'  <text x="{rx0 + 14}" y="{rb_y + 62}" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{NAVY}">Case 1: Inputs (a = 12, b = 8)   →   Target Fiber Gcd(12, 8) = {{4}}</text>')
    out.append(f'  <line x1="{nl_x0}" y1="{nl_y1}" x2="{nl_x1}" y2="{nl_y1}" stroke="{GRAY_MID}" stroke-width="2"/>')

    for n in range(max_n + 1):
        nx = nl_x0 + n * dx_n
        if n == 4:
            out.append(f'  <rect x="{nx - 13:.1f}" y="{nl_y1 - 15}" width="26" height="30" rx="13" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="2.2"/>')
            out.append(f'  <circle cx="{nx:.1f}" cy="{nl_y1}" r="5.5" fill="{NAVY}"/>')
            out.append(f'  <text x="{nx:.1f}" y="{nl_y1 - 20}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">return x (=4) ✓</text>')
            out.append(f'  <text x="{nx:.1f}" y="{nl_y1 + 26}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{NAVY}">4</text>')
        elif n == 0:
            out.append(f'  <circle cx="{nx:.1f}" cy="{nl_y1}" r="7.5" fill="{RED_FILL}" stroke="{RED}" stroke-width="2"/>')
            out.append(f'  <line x1="{nx - 4:.1f}" y1="{nl_y1 - 4}" x2="{nx + 4:.1f}" y2="{nl_y1 + 4}" stroke="{RED}" stroke-width="2"/>')
            out.append(f'  <line x1="{nx - 4:.1f}" y1="{nl_y1 + 4}" x2="{nx + 4:.1f}" y2="{nl_y1 - 4}" stroke="{RED}" stroke-width="2"/>')
            out.append(f'  <text x="{nx + 28:.1f}" y="{nl_y1 - 20}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED}">return y (=0) ✗</text>')
            out.append(f'  <text x="{nx:.1f}" y="{nl_y1 + 26}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{RED}">0</text>')
        else:
            out.append(f'  <circle cx="{nx:.1f}" cy="{nl_y1}" r="3" fill="{BG}" stroke="{GRAY_MID}" stroke-width="1.2"/>')
            out.append(f'  <text x="{nx:.1f}" y="{nl_y1 + 23}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="10.5" fill="{GRAY_DARK}">{n}</text>')

    # Second mini case: What if inputs are (21, 0)? Immediate exit on iter 0!
    nl_y2 = rb_y + 188
    out.append(f'  <text x="{rx0 + 14}" y="{rb_y + 150}" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">Case 2: Boundary Input (a = 21, b = 0)   →   Target Fiber Gcd(21, 0) = {{21}}</text>')
    out.append(f'  <line x1="{nl_x0}" y1="{nl_y2}" x2="{nl_x1}" y2="{nl_y2}" stroke="{GRAY_MID}" stroke-width="2"/>')

    for n in [0, 3, 6, 9, 12, 15, 18, 21]:
        nx = nl_x0 + (n / 21.0) * (nl_x1 - nl_x0)
        if n == 21:
            out.append(f'  <rect x="{nx - 15:.1f}" y="{nl_y2 - 15}" width="30" height="30" rx="14" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="2.2"/>')
            out.append(f'  <circle cx="{nx:.1f}" cy="{nl_y2}" r="5.5" fill="{NAVY}"/>')
            out.append(f'  <text x="{nx - 14:.1f}" y="{nl_y2 - 20}" text-anchor="end" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY}">halt iter 0: x = 21 ∈ Gcd(21, 0) ✓</text>')
            out.append(f'  <text x="{nx:.1f}" y="{nl_y2 + 26}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{NAVY}">21</text>')
        elif n == 0:
            out.append(f'  <circle cx="{nx:.1f}" cy="{nl_y2}" r="7.5" fill="{RED_FILL}" stroke="{RED}" stroke-width="2"/>')
            out.append(f'  <line x1="{nx - 4:.1f}" y1="{nl_y2 - 4}" x2="{nx + 4:.1f}" y2="{nl_y2 + 4}" stroke="{RED}" stroke-width="2"/>')
            out.append(f'  <line x1="{nx - 4:.1f}" y1="{nl_y2 + 4}" x2="{nx + 4:.1f}" y2="{nl_y2 - 4}" stroke="{RED}" stroke-width="2"/>')
            out.append(f'  <text x="{nx + 28:.1f}" y="{nl_y2 - 20}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED}">return y (=0) ✗</text>')
            out.append(f'  <text x="{nx:.1f}" y="{nl_y2 + 26}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{RED}">0</text>')
        else:
            out.append(f'  <circle cx="{nx:.1f}" cy="{nl_y2}" r="3" fill="{BG}" stroke="{GRAY_MID}" stroke-width="1.2"/>')
            out.append(f'  <text x="{nx:.1f}" y="{nl_y2 + 23}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="10.5" fill="{GRAY_DARK}">{n}</text>')

    out.append(f'  <text x="{rx0 + rw/2:.1f}" y="{rb_y + rb_h - 10}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">Runtime evidence is erased: only the plain integer 4 (or 21) flows on the Wasm stack.</text>')

    out.append(svg_footer())
    with open("fig-5.svg", "w") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    generate_fig5()
    print("Generated fig-1.svg through fig-5.svg successfully.")
