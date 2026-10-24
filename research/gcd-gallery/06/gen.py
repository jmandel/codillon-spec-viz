#!/usr/bin/env python3
"""
Generator for Angle 06: Refinement as Intersection of Predicates (Euler/Venn).
Computes all divisor sets, intersections, subtyping chains, type-error witnesses,
dependent parameter variations, and Euclid loop steps in Python, and writes
standalone SVG 1.1 files fig-1.svg .. fig-5.svg.
"""

import html
import math

# Strict palette (NO green anywhere)
BG_IVORY = "#fffff0"
INK = "#222222"
PURPLE = "#6A5ACD"
PURPLE_FILL = "#d9d5f2"
PURPLE_MID = "#c3bceb"
PURPLE_LIGHT = "#efedf9"
PURPLE_DARK = "#43368a"
RED_ERR = "#8b0000"
RED_FILL = "#fae6e6"
RED_MID = "#e3bcbc"
INDIGO_UNK = "#4b0082"
NAVY_VAL = "#00008b"
NAVY_FILL = "#e6eaf5"
GRAY_DARK = "#444444"
GRAY_MID = "#6e6e6e"
GRAY_LIGHT = "#bbbbbb"
GRAY_FAINT = "#e4e4d8"
GRAY_BOX = "#f5f5eb"
WHITE = "#ffffff"

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def divides(d: int, n: int) -> bool:
    """True iff d | n in N (where d | 0 holds for all d in N, and 0 | n iff n == 0)."""
    if n == 0:
        return True
    if d == 0:
        return False
    return (n % d) == 0


def div_set(n: int, universe: list[int]) -> set[int]:
    """Return {g in universe | g | n}."""
    return {g for g in universe if divides(g, n)}


def common_div_set(a: int, b: int, universe: list[int]) -> set[int]:
    """Return Div(a) intersect Div(b) within universe."""
    return div_set(a, universe) & div_set(b, universe)


def p_max_set(a: int, b: int, universe: list[int], check_domain: list[int] | None = None) -> set[int]:
    """Return {g in universe | forall d in CommonDiv(a, b). d | g}."""
    dom = check_domain if check_domain is not None else universe
    cdivs = common_div_set(a, b, dom)
    return {g for g in universe if all(divides(d, g) for d in cdivs)}


def euler_partition(a: int, b: int, universe: list[int]) -> dict[str, list[int]]:
    """
    Partition `universe` into the 8 regions of the 3-set Euler diagram:
    bit 0 (hundreds): Pa = {g | g | a}
    bit 1 (tens):     Pb = {g | g | b}
    bit 2 (ones):     Pm = {g | forall d in CommonDiv(a,b). d | g}
    """
    pa = div_set(a, universe)
    pb = div_set(b, universe)
    max_d = max(a, b, max(universe)) + 1
    full_dom = list(range(0, max_d + 1))
    pm = p_max_set(a, b, universe, full_dom)

    regions: dict[str, list[int]] = {
        f"{ia}{ib}{im}": []
        for ia in (0, 1)
        for ib in (0, 1)
        for im in (0, 1)
    }
    for g in universe:
        key = f"{int(g in pa)}{int(g in pb)}{int(g in pm)}"
        regions[key].append(g)
    return regions


def svg_header(width: int, height: int) -> list[str]:
    return [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="{BG_IVORY}" />',
    ]


def svg_footer() -> list[str]:
    return ["</svg>"]


def draw_num_pill(
    cx: float,
    cy: float,
    val: int | str,
    fill: str = WHITE,
    stroke: str = GRAY_MID,
    text_color: str = INK,
    r: float = 13.5,
    stroke_width: float = 1.4,
    bold: bool = False,
    font_size: int = 13,
) -> str:
    fw = "bold" if bold else "normal"
    s = str(val)
    if len(s) <= 2:
        return (
            f'<g>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" />'
            f'<text x="{cx:.1f}" y="{cy + font_size * 0.35:.1f}" text-anchor="middle" '
            f'font-family="{FONT_SERIF}" font-size="{font_size}" font-weight="{fw}" fill="{text_color}">{esc(s)}</text>'
            f'</g>'
        )
    else:
        w = max(2 * r, len(s) * 7.2 + 12)
        return (
            f'<g>'
            f'<rect x="{cx - w/2:.1f}" y="{cy - r:.1f}" width="{w:.1f}" height="{2*r:.1f}" rx="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
            f'<text x="{cx:.1f}" y="{cy + font_size * 0.35:.1f}" text-anchor="middle" '
            f'font-family="{FONT_SERIF}" font-size="{font_size}" font-weight="{fw}" fill="{text_color}">{esc(s)}</text>'
            f'</g>'
        )


def draw_check_badge(cx: float, cy: float, ok: bool, label: str) -> str:
    color = PURPLE_DARK if ok else RED_ERR
    bg = PURPLE_LIGHT if ok else RED_FILL
    sym = "✓" if ok else "✗"
    w = max(68, len(label) * 6.4 + 24)
    return (
        f'<g>'
        f'<rect x="{cx - w/2:.1f}" y="{cy - 10:.1f}" width="{w:.1f}" height="20" rx="4" '
        f'fill="{bg}" stroke="{color}" stroke-width="1.2" />'
        f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" '
        f'font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{color}">{sym} {esc(label)}</text>'
        f'</g>'
    )


# ============================================================================
# FIGURE 1: Three Conjuncts Carve Gcd(12, 8) = {4} Out of N
# ============================================================================
def generate_fig1() -> None:
    W, H = 900, 650
    a, b = 12, 8
    u = list(range(0, 13))
    part = euler_partition(a, b, u)
    pa_set = sorted(div_set(a, u))
    pb_set = sorted(div_set(b, u))
    cdiv_set = sorted(common_div_set(a, b, u))
    gcd_set = part["111"]
    assert gcd_set == [4], f"Expected [4], got {gcd_set}"

    lines = svg_header(W, H)

    # Defs: clipPaths for exact 3-circle Venn intersections
    cax, cay, car = 205, 295, 132
    cbx, cby, cbr = 345, 295, 132
    cmx, cmy, cmr = 275, 410, 132

    lines.append("  <defs>")
    lines.append(f'    <clipPath id="f1-pa"><circle cx="{cax}" cy="{cay}" r="{car}" /></clipPath>')
    lines.append(f'    <clipPath id="f1-pb"><circle cx="{cbx}" cy="{cby}" r="{cbr}" /></clipPath>')
    lines.append(f'    <clipPath id="f1-pm"><circle cx="{cmx}" cy="{cmy}" r="{cmr}" /></clipPath>')
    lines.append("  </defs>")

    # Title (<= 12 words)
    lines.append(
        f'  <text x="450" y="32" text-anchor="middle" font-family="{FONT_SERIF}" '
        f'font-size="21" font-weight="bold" fill="{INK}">'
        f'Three Conjuncts Carve Gcd(12, 8) = {{4}} Out of &#x2115;</text>'
    )
    # Subtitle formula bar
    lines.append(
        f'  <rect x="24" y="44" width="852" height="32" rx="6" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2" />'
    )
    lines.append(
        f'  <text x="450" y="65" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14.5" fill="{INK}">'
        f'Gcd(12, 8) = {{ g &#x2208; &#x2115;  |  '
        f'<tspan font-weight="bold" fill="{PURPLE_DARK}">P&#x2081;: g &#x2223; 12</tspan>   &#x2227;   '
        f'<tspan font-weight="bold" fill="{PURPLE_DARK}">P&#x2082;: g &#x2223; 8</tspan>   &#x2227;   '
        f'<tspan font-weight="bold" fill="{PURPLE_DARK}">P&#x2083;: &#x2200;d &#x2208; Div(12)&#x2229;Div(8). d &#x2223; g</tspan>'
        f' }} = {{ <tspan font-weight="bold" fill="{NAVY_VAL}">4</tspan> }}</text>'
    )

    # LEFT PANEL: Universe N box (x: 24..530, y: 88..626)
    lines.append(
        f'  <rect x="24" y="88" width="506" height="538" rx="8" fill="{GRAY_BOX}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <text x="38" y="112" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">'
        f'Base Type Universe: g &#x2208; &#x2115; = {{0, 1, 2, &#x2026;, 12, &#x2026;}}</text>'
    )
    lines.append(
        f'  <text x="38" y="129" font-family="{FONT_SANS}" font-size="12" fill="{GRAY_DARK}">'
        f'Each predicate is a subset of &#x2115;; conjunction (&#x2227;) is region intersection (&#x2229;)</text>'
    )

    # Base translucent fills for the 3 circles
    lines.append(f'  <circle cx="{cax}" cy="{cay}" r="{car}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')
    lines.append(f'  <circle cx="{cbx}" cy="{cby}" r="{cbr}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')
    lines.append(f'  <circle cx="{cmx}" cy="{cmy}" r="{cmr}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')

    # Pairwise intersections (medium tint)
    lines.append(
        f'  <g clip-path="url(#f1-pa)"><circle cx="{cbx}" cy="{cby}" r="{cbr}" fill="{PURPLE_MID}" fill-opacity="0.55" /></g>'
    )
    lines.append(
        f'  <g clip-path="url(#f1-pa)"><circle cx="{cmx}" cy="{cmy}" r="{cmr}" fill="{PURPLE_MID}" fill-opacity="0.40" /></g>'
    )
    lines.append(
        f'  <g clip-path="url(#f1-pb)"><circle cx="{cmx}" cy="{cmy}" r="{cmr}" fill="{PURPLE_MID}" fill-opacity="0.40" /></g>'
    )

    # Triple intersection (Gcd(12, 8) = {4}): rich purple fill + strong border
    lines.append(
        f'  <g clip-path="url(#f1-pa)"><g clip-path="url(#f1-pb)">'
        f'<circle cx="{cmx}" cy="{cmy}" r="{cmr}" fill="{PURPLE_FILL}" />'
        f'</g></g>'
    )

    # Circle outlines
    lines.append(
        f'  <circle cx="{cax}" cy="{cay}" r="{car}" fill="none" stroke="{PURPLE}" stroke-width="2.2" />'
    )
    lines.append(
        f'  <circle cx="{cbx}" cy="{cby}" r="{cbr}" fill="none" stroke="{PURPLE}" stroke-width="2.2" stroke-dasharray="7,4" />'
    )
    lines.append(
        f'  <circle cx="{cmx}" cy="{cmy}" r="{cmr}" fill="none" stroke="{PURPLE_DARK}" stroke-width="2.2" stroke-dasharray="3,3" />'
    )

    # Highlight rim around the triple intersection
    lines.append(
        f'  <g clip-path="url(#f1-pa)"><g clip-path="url(#f1-pb)">'
        f'<circle cx="{cmx}" cy="{cmy}" r="{cmr}" fill="none" stroke="{PURPLE_DARK}" stroke-width="4.0" />'
        f'</g></g>'
    )
    lines.append(
        f'  <g clip-path="url(#f1-pa)"><g clip-path="url(#f1-pm)">'
        f'<circle cx="{cbx}" cy="{cby}" r="{cbr}" fill="none" stroke="{PURPLE_DARK}" stroke-width="4.0" />'
        f'</g></g>'
    )
    lines.append(
        f'  <g clip-path="url(#f1-pb)"><g clip-path="url(#f1-pm)">'
        f'<circle cx="{cax}" cy="{cay}" r="{car}" fill="none" stroke="{PURPLE_DARK}" stroke-width="4.0" />'
        f'</g></g>'
    )

    # Direct Region Labels for the 3 circles
    lines.append(
        f'  <rect x="36" y="140" width="195" height="38" rx="5" fill="{WHITE}" stroke="{PURPLE}" stroke-width="1.3" />'
    )
    lines.append(
        f'  <text x="44" y="156" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE_DARK}">'
        f'P&#x2081;(g): g &#x2223; 12</text>'
    )
    lines.append(
        f'  <text x="44" y="171" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'Div(12) = {{{", ".join(map(str, pa_set))}}}</text>'
    )

    lines.append(
        f'  <rect x="322" y="140" width="195" height="38" rx="5" fill="{WHITE}" stroke="{PURPLE}" stroke-width="1.3" stroke-dasharray="5,3" />'
    )
    lines.append(
        f'  <text x="330" y="156" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE_DARK}">'
        f'P&#x2082;(g): g &#x2223; 8</text>'
    )
    lines.append(
        f'  <text x="330" y="171" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'Div(8) = {{{", ".join(map(str, pb_set))}}}</text>'
    )

    lines.append(
        f'  <rect x="120" y="548" width="310" height="40" rx="5" fill="{WHITE}" stroke="{PURPLE_DARK}" stroke-width="1.3" stroke-dasharray="3,2" />'
    )
    lines.append(
        f'  <text x="275" y="564" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE_DARK}">'
        f'P&#x2083;(g): &#x2200;d &#x2208; {{1, 2, 4}}. d &#x2223; g   (&#x201c;greatest&#x201d;)</text>'
    )
    lines.append(
        f'  <text x="275" y="580" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'Multiples of common divisors = {{0, 4, 8, 12, 16, &#x2026;}}</text>'
    )

    # Region 100: Pa only -> [3, 6]
    assert part["100"] == [3, 6]
    lines.append(draw_num_pill(118, 255, 3, fill=WHITE, stroke=PURPLE))
    lines.append(draw_num_pill(152, 255, 6, fill=WHITE, stroke=PURPLE))
    lines.append(
        f'  <text x="135" y="284" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'divides 12 only</text>'
    )

    # Region 010: Pb only -> []
    assert part["010"] == []
    lines.append(
        f'  <text x="415" y="256" text-anchor="middle" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{GRAY_MID}">'
        f'&#x2205;</text>'
    )
    lines.append(
        f'  <text x="415" y="274" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_MID}">'
        f'(all d &#x2223; 8 are &#x2264;4</text>'
    )
    lines.append(
        f'  <text x="415" y="287" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_MID}">'
        f'or multiples of 4)</text>'
    )

    # Region 110: Pa & Pb & not Pm -> [1, 2]
    assert part["110"] == [1, 2]
    lines.append(draw_num_pill(257, 232, 1, fill=WHITE, stroke=PURPLE_DARK))
    lines.append(draw_num_pill(293, 232, 2, fill=WHITE, stroke=PURPLE_DARK))
    lines.append(
        f'  <text x="275" y="205" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE_DARK}">'
        f'common, not greatest</text>'
    )
    lines.append(
        f'  <text x="275" y="260" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'(4 &#x2224; 1, 4 &#x2224; 2)</text>'
    )

    # Region 101: Pa & Pm & not Pb -> [12]
    assert part["101"] == [12]
    lines.append(draw_num_pill(185, 372, 12, fill=WHITE, stroke=PURPLE_DARK))
    lines.append(
        f'  <text x="185" y="399" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'12 &#x2224; 8</text>'
    )

    # Region 011: Pb & Pm & not Pa -> [8]
    assert part["011"] == [8]
    lines.append(draw_num_pill(365, 372, 8, fill=WHITE, stroke=PURPLE_DARK))
    lines.append(
        f'  <text x="365" y="399" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'8 &#x2224; 12</text>'
    )

    # Region 001: Pm only -> [0] (plus 16, 20, ...)
    assert part["001"] == [0]
    lines.append(draw_num_pill(242, 482, 0, fill=WHITE, stroke=PURPLE_DARK))
    lines.append(draw_num_pill(295, 482, "16, 20, …", fill=GRAY_BOX, stroke=GRAY_MID, font_size=11.5))
    lines.append(
        f'  <text x="275" y="512" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'4 &#x2223; 0 (0 = 4&#xB7;0), but 0 &#x2224; 12, 0 &#x2224; 8</text>'
    )

    # Region 111: Triple Intersection Gcd(12, 8) = {4}
    assert part["111"] == [4]
    lines.append(
        draw_num_pill(
            275, 326, 4,
            fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL,
            r=18, stroke_width=2.6, bold=True, font_size=16
        )
    )
    lines.append(
        f'  <text x="275" y="299" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{NAVY_VAL}">'
        f'Gcd(12, 8)</text>'
    )
    lines.append(
        f'  <text x="275" y="356" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY_VAL}">'
        f'singleton</text>'
    )

    # Region 000: Outside all 3 in 0..12 -> [5, 7, 9, 10, 11]
    assert part["000"] == [5, 7, 9, 10, 11]
    lines.append(
        f'  <text x="42" y="458" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{GRAY_MID}">'
        f'Outside all three</text>'
    )
    lines.append(
        f'  <text x="42" y="472" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_MID}">'
        f'(neither divisor nor</text>'
    )
    lines.append(
        f'  <text x="42" y="485" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_MID}">'
        f'multiple of 4):</text>'
    )
    out_coords = [(54, 508), (86, 508), (118, 508), (54, 540), (86, 540)]
    for (ox, oy), val in zip(out_coords, part["000"]):
        lines.append(draw_num_pill(ox, oy, val, fill=GRAY_BOX, stroke=GRAY_LIGHT, text_color=GRAY_MID, r=12.5, font_size=12))
    lines.append(
        draw_num_pill(465, 508, "13, 14, 15, …", fill=GRAY_BOX, stroke=GRAY_LIGHT, text_color=GRAY_MID, r=12.5, font_size=11)
    )

    # RIGHT PANEL: Progressive Conjunct Sieve on 0..12 (x: 546..876, y: 88..626)
    lines.append(
        f'  <rect x="546" y="88" width="330" height="538" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <text x="562" y="112" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">'
        f'Conjunct Sieve on Window 0..12</text>'
    )
    lines.append(
        f'  <text x="562" y="129" font-family="{FONT_SANS}" font-size="12" fill="{GRAY_DARK}">'
        f'Each conjunct eliminates values until one remains</text>'
    )

    stages = [
        (
            "Stage 0: Base Type (13 in 0..12)",
            "{ g ∈ ℕ }",
            set(u),
            148,
        ),
        (
            "Stage 1: Add P₁ (6 divisors of 12)",
            "{ g ∈ ℕ | g ∣ 12 }",
            set(pa_set),
            252,
        ),
        (
            "Stage 2: Add P₁ ∧ P₂ (3 common divisors)",
            "{ g ∈ ℕ | g ∣ 12 ∧ g ∣ 8 }",
            set(cdiv_set),
            356,
        ),
        (
            "Stage 3: Add P₁ ∧ P₂ ∧ P₃ (singleton {4})",
            "{ g ∈ ℕ | g ∣ 12 ∧ g ∣ 8 ∧ ∀d∈{1,2,4}. d ∣ g }",
            set(gcd_set),
            460,
        ),
    ]

    for idx, (st_title, st_formula, active_set, y0) in enumerate(stages):
        is_final = idx == 3
        box_fill = PURPLE_LIGHT if is_final else GRAY_BOX
        box_stroke = PURPLE_DARK if is_final else GRAY_LIGHT
        lines.append(
            f'  <rect x="558" y="{y0}" width="306" height="84" rx="6" fill="{box_fill}" stroke="{box_stroke}" stroke-width="1.3" />'
        )
        lines.append(
            f'  <text x="568" y="{y0 + 17}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">'
            f'{esc(st_title)}</text>'
        )
        lines.append(
            f'  <text x="568" y="{y0 + 34}" font-family="{FONT_SERIF}" font-size="12" fill="{INK}">'
            f'{esc(st_formula)}</text>'
        )
        for g in u:
            gx = 573 + g * 23.0
            gy = y0 + 60
            if g in active_set:
                if is_final:
                    lines.append(
                        draw_num_pill(
                            gx, gy, g,
                            fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL,
                            r=10.5, stroke_width=2.2, bold=True, font_size=11
                        )
                    )
                else:
                    lines.append(
                        draw_num_pill(
                            gx, gy, g,
                            fill=PURPLE_FILL, stroke=PURPLE_DARK, text_color=INK,
                            r=10.0, stroke_width=1.5, bold=True, font_size=11
                        )
                    )
            else:
                lines.append(
                    draw_num_pill(
                        gx, gy, g,
                        fill=WHITE, stroke=GRAY_FAINT, text_color=GRAY_LIGHT,
                        r=9.5, stroke_width=1.0, bold=False, font_size=10
                    )
                )
        if idx < 3:
            ay = y0 + 84
            lines.append(
                f'  <line x1="711" y1="{ay}" x2="711" y2="{ay + 18}" stroke="{PURPLE_DARK}" stroke-width="1.8" />'
            )
            lines.append(
                f'  <polygon points="711,{ay + 20} 706,{ay + 12} 716,{ay + 12}" fill="{PURPLE_DARK}" />'
            )

    lines.append(
        f'  <rect x="558" y="556" width="306" height="58" rx="6" fill="{NAVY_FILL}" stroke="{NAVY_VAL}" stroke-width="1.4" />'
    )
    lines.append(
        f'  <text x="568" y="575" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{NAVY_VAL}">'
        f'Key Property: Singleton Refinement Type</text>'
    )
    lines.append(
        f'  <text x="568" y="592" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'Because P&#x2081; &#x2229; P&#x2082; &#x2229; P&#x2083; = {{4}}, any term e : Gcd(12, 8)</text>'
    )
    lines.append(
        f'  <text x="568" y="606" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'is guaranteed at compile time to evaluate to 4.</text>'
    )

    lines.extend(svg_footer())
    with open("fig-1.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ============================================================================
# FIGURE 2: Stronger Refinement Means Smaller Region: Subtyping as Set Containment
# ============================================================================
def generate_fig2() -> None:
    W, H = 900, 620
    a, b = 12, 8
    u = list(range(0, 13))
    pa = div_set(a, u)
    cdiv = common_div_set(a, b, u)
    gcd_s = euler_partition(a, b, u)["111"]

    ring0_only = sorted(set(u) - pa)       # [0, 5, 7, 8, 9, 10, 11]
    ring1_only = sorted(pa - cdiv)         # [3, 6, 12]
    ring2_only = sorted(cdiv - set(gcd_s)) # [1, 2]
    ring3_only = sorted(gcd_s)             # [4]

    assert ring0_only == [0, 5, 7, 8, 9, 10, 11]
    assert ring1_only == [3, 6, 12]
    assert ring2_only == [1, 2]
    assert ring3_only == [4]

    lines = svg_header(W, H)

    # Title (<= 12 words)
    lines.append(
        f'  <text x="450" y="32" text-anchor="middle" font-family="{FONT_SERIF}" '
        f'font-size="21" font-weight="bold" fill="{INK}">'
        f'Stronger Refinement Means Smaller Region: Subtyping as Set Containment</text>'
    )

    # Top Subtyping Chain Banner
    lines.append(
        f'  <rect x="24" y="44" width="852" height="34" rx="6" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2" />'
    )
    lines.append(
        f'  <text x="450" y="66" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14.5" fill="{INK}">'
        f'<tspan font-weight="bold" fill="{NAVY_VAL}">Gcd(12, 8) = {{4}}</tspan>'
        f'   &#x2282; / &lt;:   '
        f'<tspan font-weight="bold" fill="{PURPLE_DARK}">CommonDiv(12, 8) = {{1, 2, 4}}</tspan>'
        f'   &#x2282; / &lt;:   '
        f'<tspan font-weight="bold" fill="{PURPLE}">Div(12) = {{1, 2, 3, 4, 6, 12}}</tspan>'
        f'   &#x2282; / &lt;:   '
        f'<tspan font-weight="bold" fill="{GRAY_DARK}">&#x2115;</tspan>'
        f'</text>'
    )

    # LEFT PANEL: Nested Euler Containment Diagram (x: 24..534, y: 90..596)
    lines.append(
        f'  <rect x="24" y="90" width="510" height="506" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <text x="40" y="114" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">'
        f'Nested Euler Diagram: Each Added Conjunct Shrinks the Set</text>'
    )
    lines.append(
        f'  <text x="40" y="131" font-family="{FONT_SANS}" font-size="12" fill="{GRAY_DARK}">'
        f'Logical implication P &#x21D2; Q corresponds to geometric containment {{g | P}} &#x2286; {{g | Q}}</text>'
    )

    # Ring 0: T0 = N (outer rounded box inside left panel)
    lines.append(
        f'  <rect x="40" y="144" width="478" height="436" rx="14" fill="{GRAY_BOX}" stroke="{GRAY_MID}" stroke-width="2.0" />'
    )
    lines.append(
        f'  <text x="56" y="167" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{GRAY_DARK}">'
        f'T&#x2080; = &#x2115; = {{ g &#x2208; &#x2115; | true }}</text>'
    )
    lines.append(
        f'  <text x="498" y="167" text-anchor="end" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_MID}">'
        f'Dropped before P&#x2081; (g &#x2224; 12):</text>'
    )

    # Place Ring 0 elements [0, 5, 7, 8, 9, 10, 11] + "13, 14, …" along top/bottom of T0
    r0_top_coords = [(68, 195), (104, 195), (140, 195), (176, 195), (384, 195), (420, 195), (456, 195)]
    for (cx, cy), val in zip(r0_top_coords, ring0_only):
        lines.append(draw_num_pill(cx, cy, val, fill=WHITE, stroke=GRAY_MID, text_color=GRAY_DARK, r=13))
    lines.append(draw_num_pill(448, 552, "13, 14, …", fill=WHITE, stroke=GRAY_LIGHT, text_color=GRAY_MID, r=12.5, font_size=11.5))

    # Ring 1: T1 = Div(12) = {g in N | g | 12}
    lines.append(
        f'  <ellipse cx="279" cy="382" rx="218" ry="178" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="2.2" />'
    )
    lines.append(
        f'  <text x="279" y="232" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{PURPLE_DARK}">'
        f'T&#x2081; = Div(12) = {{ g &#x2208; &#x2115; | g &#x2223; 12 }}</text>'
    )
    lines.append(
        f'  <text x="279" y="248" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">'
        f'+ Conjunct P&#x2081;(g): keeps 6 divisors of 12</text>'
    )

    # Place Ring 1 elements [3, 6, 12] in the crescent of T1 \ T2
    r1_coords = [(106, 360), (106, 404), (452, 382)]
    for (cx, cy), val in zip(r1_coords, ring1_only):
        lines.append(draw_num_pill(cx, cy, val, fill=WHITE, stroke=PURPLE, text_color=INK, r=14, bold=True))
    lines.append(
        f'  <text x="106" y="434" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'3 &#x2224; 8, 6 &#x2224; 8</text>'
    )
    lines.append(
        f'  <text x="452" y="412" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'12 &#x2224; 8</text>'
    )

    # Ring 2: T2 = CommonDiv(12, 8) = {g in N | g | 12 & g | 8}
    lines.append(
        f'  <ellipse cx="279" cy="404" rx="146" ry="132" fill="{PURPLE_MID}" fill-opacity="0.65" stroke="{PURPLE_DARK}" stroke-width="2.4" stroke-dasharray="6,3" />'
    )
    lines.append(
        f'  <text x="279" y="302" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{PURPLE_DARK}">'
        f'T&#x2082; = CommonDiv(12, 8)</text>'
    )
    lines.append(
        f'  <text x="279" y="318" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">'
        f'+ Conjunct P&#x2082;(g): g &#x2223; 8 (keeps {{1, 2, 4}})</text>'
    )

    # Place Ring 2 elements [1, 2] in crescent of T2 \ T3
    lines.append(draw_num_pill(184, 415, 1, fill=WHITE, stroke=PURPLE_DARK, text_color=INK, r=14, bold=True))
    lines.append(draw_num_pill(374, 415, 2, fill=WHITE, stroke=PURPLE_DARK, text_color=INK, r=14, bold=True))
    lines.append(
        f'  <text x="184" y="444" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'4 &#x2224; 1</text>'
    )
    lines.append(
        f'  <text x="374" y="444" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'4 &#x2224; 2</text>'
    )

    # Ring 3: T3 = Gcd(12, 8) = {4}
    lines.append(
        f'  <ellipse cx="279" cy="436" rx="68" ry="68" fill="{PURPLE_FILL}" stroke="{NAVY_VAL}" stroke-width="3.2" />'
    )
    lines.append(
        f'  <text x="279" y="392" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{NAVY_VAL}">'
        f'T&#x2083; = Gcd(12, 8)</text>'
    )
    lines.append(
        f'  <text x="279" y="407" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{NAVY_VAL}">'
        f'+ Conjunct P&#x2083;(g)</text>'
    )
    lines.append(
        draw_num_pill(
            279, 442, 4,
            fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL,
            r=19, stroke_width=2.8, bold=True, font_size=17
        )
    )
    lines.append(
        f'  <text x="279" y="480" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{NAVY_VAL}">'
        f'unique inhabitant</text>'
    )

    # RIGHT PANEL: Logical Implication vs Subtyping (x: 550..876, y: 90..596)
    lines.append(
        f'  <rect x="550" y="90" width="326" height="506" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <text x="566" y="114" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">'
        f'Why Adding a Conjunct Creates a Subtype</text>'
    )
    lines.append(
        f'  <text x="566" y="131" font-family="{FONT_SANS}" font-size="11.5" fill="{GRAY_DARK}">'
        f'Upcasting drops a conjunct; every inner value is valid outside</text>'
    )

    cards = [
        (
            "T₃ = Gcd(12, 8)",
            "{ g ∈ ℕ | g ∣ 12 ∧ g ∣ 8 ∧ ∀d∈Common. d ∣ g }",
            "Inhabitants: { 4 }   (cardinality = 1)",
            "Evidence carried: (4 ∣ 12,  4 ∣ 8,  ∀d∈{1,2,4}. d ∣ 4)",
            148,
            NAVY_FILL,
            NAVY_VAL,
        ),
        (
            "T₂ = CommonDiv(12, 8)",
            "{ g ∈ ℕ | g ∣ 12 ∧ g ∣ 8 }",
            "Inhabitants: { 1, 2, 4 }   (cardinality = 3)",
            "Forgets P₃ (‘greatest’); admits non-maximal divisors 1, 2",
            258,
            PURPLE_FILL,
            PURPLE_DARK,
        ),
        (
            "T₁ = Div(12)",
            "{ g ∈ ℕ | g ∣ 12 }",
            "Inhabitants: { 1, 2, 3, 4, 6, 12 }   (cardinality = 6)",
            "Forgets P₂ (g ∣ 8); admits 3, 6, 12",
            368,
            PURPLE_LIGHT,
            PURPLE,
        ),
        (
            "T₀ = ℕ (Unrefined Base Type)",
            "{ g ∈ ℕ | true }",
            "Inhabitants: { 0, 1, 2, 3, 4, 5, … }   (infinite)",
            "Forgets P₁ (g ∣ 12); admits every natural number",
            478,
            GRAY_BOX,
            GRAY_MID,
        ),
    ]

    for idx, (ctitle, cform, cset, cev, cy, cfill, cstroke) in enumerate(cards):
        lines.append(
            f'  <rect x="564" y="{cy}" width="298" height="82" rx="6" fill="{cfill}" stroke="{cstroke}" stroke-width="1.5" />'
        )
        lines.append(
            f'  <text x="574" y="{cy + 18}" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">'
            f'{esc(ctitle)}</text>'
        )
        lines.append(
            f'  <text x="574" y="{cy + 35}" font-family="{FONT_SERIF}" font-size="11.5" fill="{PURPLE_DARK}">'
            f'{esc(cform)}</text>'
        )
        lines.append(
            f'  <text x="574" y="{cy + 52}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{INK}">'
            f'{esc(cset)}</text>'
        )
        lines.append(
            f'  <text x="574" y="{cy + 69}" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
            f'{esc(cev)}</text>'
        )

        if idx < 3:
            ay = cy + 82
            lines.append(
                f'  <line x1="600" y1="{ay}" x2="600" y2="{ay + 24}" stroke="{PURPLE_DARK}" stroke-width="1.8" />'
            )
            lines.append(
                f'  <polygon points="600,{ay + 26} 595,{ay + 18} 605,{ay + 18}" fill="{PURPLE_DARK}" />'
            )
            lines.append(
                f'  <text x="612" y="{ay + 17}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE_DARK}">'
                f'subtype (&lt;:) / subset (&#x2282;) &#x2014; drop 1 conjunct</text>'
            )

    lines.extend(svg_footer())
    with open("fig-2.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ============================================================================
# FIGURE 3: Type Errors and Too-Weak Specifications (What Each Conjunct Blocks)
# ============================================================================
def generate_fig3() -> None:
    W, H = 900, 680
    a, b = 12, 8
    u = list(range(0, 13))
    part = euler_partition(a, b, u)
    assert part["111"] == [4]

    lines = svg_header(W, H)

    # Title (<= 12 words)
    lines.append(
        f'  <text x="450" y="32" text-anchor="middle" font-family="{FONT_SERIF}" '
        f'font-size="21" font-weight="bold" fill="{INK}">'
        f'Every Missing Conjunct Lets Impostor Values Leak Into the Type</text>'
    )
    lines.append(
        f'  <text x="450" y="52" text-anchor="middle" font-family="{FONT_SANS}" font-size="13" fill="{GRAY_DARK}">'
        f'A candidate value g for Gcd(12, 8) is a type error (dark red) whenever it lands outside at least one conjunct boundary</text>'
    )

    # 3 Columns for the 3 failure modes (width 276 each, y: 66..482)
    panels = [
        {
            "x": 20,
            "title": "1. Drop P₃ (“Greatest”)",
            "spec": "Weak Spec: { g ∈ ℕ | g ∣ 12 ∧ g ∣ 8 }",
            "bug_code": "return 2   // common divisor",
            "impostors": [1, 2],
            "focus_val": 2,
            "p1_ok": True,
            "p2_ok": True,
            "p3_ok": False,
            "viol_text": "Fails P₃: d = 4 is common, 4 ∤ 2",
            "leak_region": "110",
            "caption": "Admits non-greatest common divisors 1, 2.",
        },
        {
            "x": 312,
            "title": "2. Drop P₁ (“Divides a = 12”)",
            "spec": "Weak Spec: { g ∈ ℕ | g ∣ 8 ∧ ∀d∈Common. d ∣ g }",
            "bug_code": "return b   // returns 8",
            "impostors": [8],
            "focus_val": 8,
            "p1_ok": False,
            "p2_ok": True,
            "p3_ok": True,
            "viol_text": "Fails P₁: 8 ∤ 12 (does not divide a)",
            "leak_region": "011",
            "caption": "Input b = 8 satisfies P₂ ∧ P₃ and leaks in.",
        },
        {
            "x": 604,
            "title": "3. Drop P₂ (“Divides b = 8”)",
            "spec": "Weak Spec: { g ∈ ℕ | g ∣ 12 ∧ ∀d∈Common. d ∣ g }",
            "bug_code": "return a   // returns 12",
            "impostors": [12],
            "focus_val": 12,
            "p1_ok": True,
            "p2_ok": False,
            "p3_ok": True,
            "viol_text": "Fails P₂: 12 ∤ 8 (does not divide b)",
            "leak_region": "101",
            "caption": "Input a = 12 leaks in (no P₁∧P₂ admits 0).",
        },
    ]

    # Defs for mini Venn diagrams in each panel
    lines.append("  <defs>")
    for idx, p in enumerate(panels):
        px = p["x"]
        cax, cay, cr = px + 106, 236, 62
        cbx, cby = px + 170, 236
        cmx, cmy = px + 138, 290
        lines.append(f'    <clipPath id="f3-pa-{idx}"><circle cx="{cax}" cy="{cay}" r="{cr}" /></clipPath>')
        lines.append(f'    <clipPath id="f3-pb-{idx}"><circle cx="{cbx}" cy="{cby}" r="{cr}" /></clipPath>')
        lines.append(f'    <clipPath id="f3-pm-{idx}"><circle cx="{cmx}" cy="{cmy}" r="{cr}" /></clipPath>')
        lines.append(
            f'    <clipPath id="f3-not-pm-{idx}">'
            f'<path d="M {px} 150 H {px+276} V 380 H {px} Z '
            f'M {cmx + cr} {cmy} A {cr} {cr} 0 1 0 {cmx - cr} {cmy} A {cr} {cr} 0 1 0 {cmx + cr} {cmy} Z" clip-rule="evenodd" />'
            f'</clipPath>'
        )
        lines.append(
            f'    <clipPath id="f3-not-pa-{idx}">'
            f'<path d="M {px} 150 H {px+276} V 380 H {px} Z '
            f'M {cax + cr} {cay} A {cr} {cr} 0 1 0 {cax - cr} {cay} A {cr} {cr} 0 1 0 {cax + cr} {cay} Z" clip-rule="evenodd" />'
            f'</clipPath>'
        )
        lines.append(
            f'    <clipPath id="f3-not-pb-{idx}">'
            f'<path d="M {px} 150 H {px+276} V 380 H {px} Z '
            f'M {cbx + cr} {cby} A {cr} {cr} 0 1 0 {cbx - cr} {cby} A {cr} {cr} 0 1 0 {cbx + cr} {cby} Z" clip-rule="evenodd" />'
            f'</clipPath>'
        )
    lines.append("  </defs>")

    for idx, p in enumerate(panels):
        px = p["x"]
        cax, cay, cr = px + 106, 236, 62
        cbx, cby = px + 170, 236
        cmx, cmy = px + 138, 290

        # Panel frame
        lines.append(
            f'  <rect x="{px}" y="66" width="276" height="418" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
        )
        # Header
        lines.append(
            f'  <rect x="{px}" y="66" width="276" height="46" rx="8" fill="{RED_FILL}" stroke="{RED_ERR}" stroke-width="1.5" />'
        )
        lines.append(
            f'  <text x="{px + 138}" y="86" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{RED_ERR}">'
            f'{esc(p["title"])}</text>'
        )
        lines.append(
            f'  <text x="{px + 138}" y="103" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" fill="{INK}">'
            f'{esc(p["spec"])}</text>'
        )

        # Buggy program line
        lines.append(
            f'  <rect x="{px + 12}" y="120" width="252" height="24" rx="4" fill="{GRAY_BOX}" stroke="{RED_ERR}" stroke-width="1.0" />'
        )
        lines.append(
            f'  <text x="{px + 20}" y="136" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{RED_ERR}">'
            f'Buggy return:  {esc(p["bug_code"])}</text>'
        )

        # Draw mini Venn circles
        lines.append(f'  <circle cx="{cax}" cy="{cay}" r="{cr}" fill="{PURPLE_LIGHT}" fill-opacity="0.55" />')
        lines.append(f'  <circle cx="{cbx}" cy="{cby}" r="{cr}" fill="{PURPLE_LIGHT}" fill-opacity="0.55" />')
        lines.append(f'  <circle cx="{cmx}" cy="{cmy}" r="{cr}" fill="{PURPLE_LIGHT}" fill-opacity="0.55" />')

        # Shade the leaked impostor region in RED_FILL
        if p["leak_region"] == "110":
            lines.append(
                f'  <g clip-path="url(#f3-pa-{idx})"><g clip-path="url(#f3-pb-{idx})"><g clip-path="url(#f3-not-pm-{idx})">'
                f'<rect x="{px}" y="150" width="276" height="230" fill="{RED_MID}" />'
                f'</g></g></g>'
            )
        elif p["leak_region"] == "011":
            lines.append(
                f'  <g clip-path="url(#f3-pb-{idx})"><g clip-path="url(#f3-pm-{idx})"><g clip-path="url(#f3-not-pa-{idx})">'
                f'<rect x="{px}" y="150" width="276" height="230" fill="{RED_MID}" />'
                f'</g></g></g>'
            )
        elif p["leak_region"] == "101":
            lines.append(
                f'  <g clip-path="url(#f3-pa-{idx})"><g clip-path="url(#f3-pm-{idx})"><g clip-path="url(#f3-not-pb-{idx})">'
                f'<rect x="{px}" y="150" width="276" height="230" fill="{RED_MID}" />'
                f'</g></g></g>'
            )

        # True Gcd center {4}
        lines.append(
            f'  <g clip-path="url(#f3-pa-{idx})"><g clip-path="url(#f3-pb-{idx})">'
            f'<circle cx="{cmx}" cy="{cmy}" r="{cr}" fill="{PURPLE_FILL}" />'
            f'</g></g>'
        )

        # Circle borders (dropped conjunct shown with faint gray/red dashed line; active ones in purple)
        s_pa = RED_ERR if not p["p1_ok"] else PURPLE
        s_pb = RED_ERR if not p["p2_ok"] else PURPLE
        s_pm = RED_ERR if not p["p3_ok"] else PURPLE_DARK
        lines.append(f'  <circle cx="{cax}" cy="{cay}" r="{cr}" fill="none" stroke="{s_pa}" stroke-width="1.8" />')
        lines.append(f'  <circle cx="{cbx}" cy="{cby}" r="{cr}" fill="none" stroke="{s_pb}" stroke-width="1.8" stroke-dasharray="5,3" />')
        lines.append(f'  <circle cx="{cmx}" cy="{cmy}" r="{cr}" fill="none" stroke="{s_pm}" stroke-width="1.8" stroke-dasharray="2,2" />')

        # Circle mini labels
        lines.append(f'  <text x="{cax - 24}" y="{cay - 68}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{s_pa}">P&#x2081;: g&#x2223;12</text>')
        lines.append(f'  <text x="{cbx + 24}" y="{cby - 68}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{s_pb}">P&#x2082;: g&#x2223;8</text>')
        lines.append(f'  <text x="{cmx}" y="{cmy + 76}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{s_pm}">P&#x2083;: &#x2200;d&#x2208;Common. d&#x2223;g</text>')

        # True inhabitant 4 in center
        lines.append(draw_num_pill(px + 138, 252, 4, fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL, r=12, stroke_width=2.0, bold=True, font_size=12))

        # Impostor pills in red!
        if p["leak_region"] == "110":
            lines.append(draw_num_pill(px + 123, 206, 1, fill=RED_FILL, stroke=RED_ERR, text_color=RED_ERR, r=12, stroke_width=2.0, bold=True, font_size=12))
            lines.append(draw_num_pill(px + 153, 206, 2, fill=RED_FILL, stroke=RED_ERR, text_color=RED_ERR, r=13, stroke_width=2.4, bold=True, font_size=13))
            lines.append(f'  <text x="{px + 138}" y="168" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED_ERR}">LEAKED!</text>')
        elif p["leak_region"] == "011":
            lines.append(draw_num_pill(px + 182, 275, 8, fill=RED_FILL, stroke=RED_ERR, text_color=RED_ERR, r=13.5, stroke_width=2.4, bold=True, font_size=13))
            lines.append(f'  <text x="{px + 225}" y="278" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED_ERR}">LEAK!</text>')
        elif p["leak_region"] == "101":
            lines.append(draw_num_pill(px + 94, 275, 12, fill=RED_FILL, stroke=RED_ERR, text_color=RED_ERR, r=13.5, stroke_width=2.4, bold=True, font_size=13))
            lines.append(f'  <text x="{px + 48}" y="278" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED_ERR}">LEAK!</text>')

        # Predicate check badges for the focus impostor value
        fv = p["focus_val"]
        lines.append(
            f'  <text x="{px + 138}" y="384" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{INK}">'
            f'Checking candidate g = {fv} against Gcd(12, 8):</text>'
        )
        lines.append(draw_check_badge(px + 50, 404, p["p1_ok"], f"{fv} ∣ 12"))
        lines.append(draw_check_badge(px + 132, 404, p["p2_ok"], f"{fv} ∣ 8"))
        lines.append(draw_check_badge(px + 220, 404, p["p3_ok"], f"4 ∣ {fv}"))

        # Violation box
        lines.append(
            f'  <rect x="{px + 10}" y="422" width="256" height="48" rx="4" fill="{RED_FILL}" stroke="{RED_ERR}" stroke-width="1.2" />'
        )
        lines.append(
            f'  <text x="{px + 138}" y="440" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED_ERR}">'
            f'TYPE ERROR: {esc(p["viol_text"])}</text>'
        )
        lines.append(
            f'  <text x="{px + 138}" y="458" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{INK}">'
            f'{esc(p["caption"])}</text>'
        )

    # BOTTOM MATRIX: Diagnostic Table of Candidate Values vs the Three Conjuncts (y: 498..664)
    lines.append(
        f'  <rect x="20" y="498" width="860" height="166" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <text x="36" y="520" font-family="{FONT_SERIF}" font-size="14.5" font-weight="bold" fill="{INK}">'
        f'Refinement Type Checker as a 3-Conjunct Gate for Gcd(12, 8): Only g = 4 Passes All Three</text>'
    )

    candidates = [
        (4, "g = 4 (True gcd)", True, True, True, "TYPE CHECKS: 4 ∈ Gcd(12, 8)", True),
        (2, "g = 2 (Common div)", True, True, False, "TYPE ERROR: 4 ∤ 2 (fails P₃)", False),
        (8, "g = 8 (Input b)", False, True, True, "TYPE ERROR: 8 ∤ 12 (fails P₁)", False),
        (12, "g = 12 (Input a)", True, False, True, "TYPE ERROR: 12 ∤ 8 (fails P₂)", False),
        (0, "g = 0 (Zero)", False, False, True, "TYPE ERROR: 0 ∤ 12, 0 ∤ 8 (fails P₁, P₂)", False),
        (6, "g = 6 (Divisor of 12)", True, False, False, "TYPE ERROR: 6 ∤ 8, 4 ∤ 6 (fails P₂, P₃)", False),
    ]

    # Table headers
    hy = 540
    lines.append(f'  <line x1="32" y1="{hy + 6}" x2="868" y2="{hy + 6}" stroke="{GRAY_LIGHT}" stroke-width="1.2" />')
    lines.append(f'  <text x="40" y="{hy}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{GRAY_DARK}">Candidate Value</text>')
    lines.append(f'  <text x="245" y="{hy}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P₁: g ∣ 12</text>')
    lines.append(f'  <text x="375" y="{hy}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P₂: g ∣ 8</text>')
    lines.append(f'  <text x="520" y="{hy}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P₃: ∀d∈&#x7b;1, 2, 4&#x7d;. d ∣ g</text>')
    lines.append(f'  <text x="640" y="{hy}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{GRAY_DARK}">Refinement Verdict</text>')

    for r_idx, (cval, clabel, ok1, ok2, ok3, verdict, is_good) in enumerate(candidates):
        # Verify in Python!
        assert ok1 == divides(cval, 12)
        assert ok2 == divides(cval, 8)
        assert ok3 == all(divides(d, cval) for d in [1, 2, 4])
        ry = 560 + r_idx * 18
        row_bg = NAVY_FILL if is_good else (RED_FILL if r_idx % 2 == 1 else WHITE)
        lines.append(f'  <rect x="32" y="{ry - 12}" width="836" height="17" rx="2" fill="{row_bg}" fill-opacity="0.55" />')
        t_col = NAVY_VAL if is_good else INK
        fw = "bold" if is_good else "normal"
        lines.append(f'  <text x="40" y="{ry}" font-family="{FONT_SERIF}" font-size="11.5" font-weight="{fw}" fill="{t_col}">{esc(clabel)}</text>')

        for cx_col, ok_flag in [(245, ok1), (375, ok2), (520, ok3)]:
            sym = "✓ holds" if ok_flag else "✗ FAILS"
            scol = PURPLE_DARK if ok_flag else RED_ERR
            lines.append(f'  <text x="{cx_col}" y="{ry}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{scol}">{sym}</text>')

        v_col = NAVY_VAL if is_good else RED_ERR
        lines.append(f'  <text x="640" y="{ry}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{v_col}">{esc(verdict)}</text>')

    lines.extend(svg_footer())
    with open("fig-3.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ============================================================================
# FIGURE 4: Dependent Types: How Input Pairs (a, b) Reshape the Euler Regions
# ============================================================================
def generate_fig4() -> None:
    W, H = 900, 680

    # Verify the 4 cases mathematically in Python
    # Case 1: Coprime (13, 8) -> gcd = 1
    u1 = list(range(0, 14))
    p1 = euler_partition(13, 8, u1)
    assert p1["111"] == [1]
    assert p1["110"] == []  # No smaller common divisor exists!

    # Case 2: Composite rich pair (1071, 462) -> gcd = 21
    u2 = list(range(0, 1072))
    p2 = euler_partition(1071, 462, u2)
    assert p2["111"] == [21]
    assert p2["110"] == [1, 3, 7]

    # Case 3: Zero right input (21, 0) -> gcd = 21
    u3 = list(range(0, 45))
    p3 = euler_partition(21, 0, u3)
    assert p3["111"] == [21]
    assert p3["110"] == [1, 3, 7]
    assert p3["100"] == []  # Since Div(0) = N, Div(21) \ Div(0) is empty!

    # Case 4: Both zero (0, 0) -> gcd = 0
    u4 = list(range(0, 10))
    p4 = euler_partition(0, 0, u4)
    assert p4["111"] == [0]
    assert p4["110"] == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    lines = svg_header(W, H)

    # Title (<= 12 words)
    lines.append(
        f'  <text x="450" y="32" text-anchor="middle" font-family="{FONT_SERIF}" '
        f'font-size="21" font-weight="bold" fill="{INK}">'
        f'Dependent Types: Input Values (a, b) Reshape the Conjunct Regions</text>'
    )
    lines.append(
        f'  <text x="450" y="52" text-anchor="middle" font-family="{FONT_SANS}" font-size="13" fill="{GRAY_DARK}">'
        f'Gcd(a, b) is a family of sets indexed by (a, b): changing the term indices moves the boundaries, yet P&#x2081; &#x2229; P&#x2082; &#x2229; P&#x2083; always has size 1</text>'
    )

    # Defs for 4 quadrant clip paths
    lines.append("  <defs>")
    # Q1: (13, 8) at top-left (x: 20..440, y: 66..356)
    q1_ax, q1_ay, q1_r = 165, 212, 62
    q1_bx, q1_by = 235, 212
    lines.append(f'    <clipPath id="f4-q1-pa"><circle cx="{q1_ax}" cy="{q1_ay}" r="{q1_r}" /></clipPath>')
    lines.append(f'    <clipPath id="f4-q1-pb"><circle cx="{q1_bx}" cy="{q1_by}" r="{q1_r}" /></clipPath>')

    # Q2: (1071, 462) at top-right (x: 460..880, y: 66..356)
    q2_ax, q2_ay, q2_r = 610, 192, 66
    q2_bx, q2_by = 684, 192
    q2_mx, q2_my = 647, 250
    lines.append(f'    <clipPath id="f4-q2-pa"><circle cx="{q2_ax}" cy="{q2_ay}" r="{q2_r}" /></clipPath>')
    lines.append(f'    <clipPath id="f4-q2-pb"><circle cx="{q2_bx}" cy="{q2_by}" r="{q2_r}" /></clipPath>')
    lines.append(f'    <clipPath id="f4-q2-pm"><circle cx="{q2_mx}" cy="{q2_my}" r="{q2_r}" /></clipPath>')

    # Q3: (21, 0) at bottom-left (x: 20..440, y: 372..662)
    q3_ax, q3_ay, q3_r = 175, 526, 62
    q3_mx, q3_my = 245, 526
    lines.append(f'    <clipPath id="f4-q3-pa"><circle cx="{q3_ax}" cy="{q3_ay}" r="{q3_r}" /></clipPath>')
    lines.append(f'    <clipPath id="f4-q3-pm"><circle cx="{q3_mx}" cy="{q3_my}" r="{q3_r}" /></clipPath>')
    lines.append("  </defs>")

    # ------------------------------------------------------------------------
    # QUADRANT 1: Coprime (a = 13, b = 8) -> Gcd(13, 8) = {1}
    # ------------------------------------------------------------------------
    lines.append(
        f'  <rect x="20" y="66" width="420" height="290" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <rect x="20" y="66" width="420" height="40" rx="8" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2" />'
    )
    lines.append(
        f'  <text x="34" y="85" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">'
        f'Case A: Coprime Inputs (a = 13, b = 8) &#x2192; Gcd(13, 8) = {{1}}</text>'
    )
    lines.append(
        f'  <text x="34" y="100" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">'
        f'CommonDiv(13, 8) = {{1}}, so P&#x2083; (&#x2200;d&#x2208;{{1}}. d &#x2223; g) is all of &#x2115;!</text>'
    )

    # Outer box inside Q1 representing P3 = N (also Universe N)
    lines.append(
        f'  <rect x="34" y="114" width="392" height="190" rx="8" fill="{GRAY_BOX}" stroke="{PURPLE_DARK}" stroke-width="1.8" stroke-dasharray="3,2" />'
    )
    lines.append(
        f'  <text x="44" y="131" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">'
        f'P&#x2083;(g): 1 &#x2223; g holds for ALL g &#x2208; &#x2115;  (P&#x2083; expands to the whole box)</text>'
    )

    # Circles P1 and P2 inside P3
    lines.append(f'  <circle cx="{q1_ax}" cy="{q1_ay}" r="{q1_r}" fill="{PURPLE_LIGHT}" fill-opacity="0.8" />')
    lines.append(f'  <circle cx="{q1_bx}" cy="{q1_by}" r="{q1_r}" fill="{PURPLE_LIGHT}" fill-opacity="0.8" />')
    lines.append(
        f'  <g clip-path="url(#f4-q1-pa)"><circle cx="{q1_bx}" cy="{q1_by}" r="{q1_r}" fill="{PURPLE_FILL}" /></g>'
    )
    lines.append(f'  <circle cx="{q1_ax}" cy="{q1_ay}" r="{q1_r}" fill="none" stroke="{PURPLE}" stroke-width="2.0" />')
    lines.append(f'  <circle cx="{q1_bx}" cy="{q1_by}" r="{q1_r}" fill="none" stroke="{PURPLE}" stroke-width="2.0" stroke-dasharray="6,3" />')

    lines.append(f'  <text x="{q1_ax - 42}" y="{q1_ay - 66}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">P&#x2081;: g &#x2223; 13</text>')
    lines.append(f'  <text x="{q1_bx + 42}" y="{q1_by - 66}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">P&#x2082;: g &#x2223; 8</text>')

    # Elements of (13, 8)
    lines.append(draw_num_pill(130, 212, 13, fill=WHITE, stroke=PURPLE, r=13))
    lines.append(draw_num_pill(200, 212, 1, fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL, r=16, stroke_width=2.5, bold=True, font_size=14))
    lines.append(draw_num_pill(260, 194, 2, fill=WHITE, stroke=PURPLE, r=12))
    lines.append(draw_num_pill(260, 228, 4, fill=WHITE, stroke=PURPLE, r=12))
    lines.append(draw_num_pill(282, 211, 8, fill=WHITE, stroke=PURPLE, r=12))
    lines.append(draw_num_pill(368, 198, 0, fill=WHITE, stroke=GRAY_MID, r=12))
    lines.append(draw_num_pill(368, 232, "3, 5, 6, …", fill=WHITE, stroke=GRAY_LIGHT, text_color=GRAY_MID, r=12, font_size=11))

    lines.append(
        f'  <text x="230" y="324" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'P&#x2081; &#x2229; P&#x2082; = {{1}} is already a singleton; P&#x2083; = &#x2115; cuts nothing further.</text>'
    )
    lines.append(
        f'  <text x="230" y="342" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{NAVY_VAL}">'
        f'Result: Gcd(13, 8) = {{1}}</text>'
    )

    # ------------------------------------------------------------------------
    # QUADRANT 2: Rich Composite Pair (a = 1071, b = 462) -> Gcd = {21}
    # ------------------------------------------------------------------------
    lines.append(
        f'  <rect x="460" y="66" width="420" height="290" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <rect x="460" y="66" width="420" height="40" rx="8" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2" />'
    )
    lines.append(
        f'  <text x="474" y="85" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">'
        f'Case B: Euclid Example (a = 1071, b = 462) &#x2192; Gcd = {{21}}</text>'
    )
    lines.append(
        f'  <text x="474" y="100" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">'
        f'1071 = 3&#xB2;&#xB7;7&#xB7;17 (12 divisors),  462 = 2&#xB7;3&#xB7;7&#xB7;11 (16 divisors)</text>'
    )

    lines.append(f'  <circle cx="{q2_ax}" cy="{q2_ay}" r="{q2_r}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')
    lines.append(f'  <circle cx="{q2_bx}" cy="{q2_by}" r="{q2_r}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')
    lines.append(f'  <circle cx="{q2_mx}" cy="{q2_my}" r="{q2_r}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')
    lines.append(
        f'  <g clip-path="url(#f4-q2-pa)"><g clip-path="url(#f4-q2-pb)">'
        f'<circle cx="{q2_mx}" cy="{q2_my}" r="{q2_r}" fill="{PURPLE_FILL}" />'
        f'</g></g>'
    )
    lines.append(f'  <circle cx="{q2_ax}" cy="{q2_ay}" r="{q2_r}" fill="none" stroke="{PURPLE}" stroke-width="1.9" />')
    lines.append(f'  <circle cx="{q2_bx}" cy="{q2_by}" r="{q2_r}" fill="none" stroke="{PURPLE}" stroke-width="1.9" stroke-dasharray="6,3" />')
    lines.append(f'  <circle cx="{q2_mx}" cy="{q2_my}" r="{q2_r}" fill="none" stroke="{PURPLE_DARK}" stroke-width="1.9" stroke-dasharray="3,2" />')

    lines.append(f'  <text x="530" y="132" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P&#x2081;: g &#x2223; 1071</text>')
    lines.append(f'  <text x="720" y="132" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P&#x2082;: g &#x2223; 462</text>')
    lines.append(f'  <text x="795" y="280" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P&#x2083;: 21 &#x2223; g</text>')

    # Elements in Q2
    # 110: [1, 3, 7]
    lines.append(draw_num_pill(635, 152, "1, 3, 7", fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
    # 111: [21]
    lines.append(draw_num_pill(647, 208, 21, fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL, r=15.5, stroke_width=2.5, bold=True, font_size=13.5))
    # 100: [9, 17, 51, 119, 153, 357]
    lines.append(draw_num_pill(568, 178, "9, 17, 51", fill=WHITE, stroke=PURPLE, r=11, font_size=10.5))
    # 010: [2, 6, 11, 14, 22, 33, 66, 77, 154, 231]
    lines.append(draw_num_pill(726, 178, "2, 6, 11, 14…", fill=WHITE, stroke=PURPLE, r=11, font_size=10.5))
    # 101: [63, 357, 1071]
    lines.append(draw_num_pill(592, 236, "63, 1071", fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=10.5))
    # 011: [42, 231, 462]
    lines.append(draw_num_pill(704, 236, "42, 462", fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=10.5))
    # 001: [0, 84, ...]
    lines.append(draw_num_pill(647, 290, "0, 84, …", fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=10.5))

    lines.append(
        f'  <text x="670" y="324" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'CommonDiv(1071, 462) = {{1, 3, 7, 21}}; P&#x2083; cuts {{1, 3, 7}} away.</text>'
    )
    lines.append(
        f'  <text x="670" y="342" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{NAVY_VAL}">'
        f'Result: Gcd(1071, 462) = {{21}}</text>'
    )

    # ------------------------------------------------------------------------
    # QUADRANT 3: Zero Right Input (a = 21, b = 0) -> Gcd(21, 0) = {21}
    # ------------------------------------------------------------------------
    lines.append(
        f'  <rect x="20" y="372" width="420" height="290" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <rect x="20" y="372" width="420" height="40" rx="8" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2" />'
    )
    lines.append(
        f'  <text x="34" y="391" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">'
        f'Case C: Stopping Case (a = 21, b = 0) &#x2192; Gcd(21, 0) = {{21}}</text>'
    )
    lines.append(
        f'  <text x="34" y="406" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">'
        f'Every d &#x2208; &#x2115; divides 0 (0 = d&#xB7;0), so P&#x2082;: Div(0) = &#x2115;!</text>'
    )

    # Outer box in Q3 is P2: Div(0) = N
    lines.append(
        f'  <rect x="34" y="420" width="392" height="190" rx="8" fill="{GRAY_BOX}" stroke="{PURPLE}" stroke-width="2.0" stroke-dasharray="6,3" />'
    )
    lines.append(
        f'  <text x="44" y="438" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">'
        f'P&#x2082;(g): g &#x2223; 0 holds for ALL g &#x2208; &#x2115;  (Div(0) = &#x2115; is the whole box)</text>'
    )

    lines.append(f'  <circle cx="{q3_ax}" cy="{q3_ay}" r="{q3_r}" fill="{PURPLE_LIGHT}" fill-opacity="0.8" />')
    lines.append(f'  <circle cx="{q3_mx}" cy="{q3_my}" r="{q3_r}" fill="{PURPLE_LIGHT}" fill-opacity="0.8" />')
    lines.append(
        f'  <g clip-path="url(#f4-q3-pa)"><circle cx="{q3_mx}" cy="{q3_my}" r="{q3_r}" fill="{PURPLE_FILL}" /></g>'
    )
    lines.append(f'  <circle cx="{q3_ax}" cy="{q3_ay}" r="{q3_r}" fill="none" stroke="{PURPLE}" stroke-width="2.0" />')
    lines.append(f'  <circle cx="{q3_mx}" cy="{q3_my}" r="{q3_r}" fill="none" stroke="{PURPLE_DARK}" stroke-width="2.0" stroke-dasharray="3,2" />')

    lines.append(f'  <text x="{q3_ax - 38}" y="{q3_ay - 66}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">P&#x2081;: g &#x2223; 21</text>')
    lines.append(f'  <text x="{q3_mx + 48}" y="{q3_my - 66}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">P&#x2083;: &#x2200;d&#x2208;Div(21). d&#x2223;g</text>')

    # Elements of (21, 0)
    lines.append(draw_num_pill(136, 510, 1, fill=WHITE, stroke=PURPLE, r=12))
    lines.append(draw_num_pill(136, 540, 3, fill=WHITE, stroke=PURPLE, r=12))
    lines.append(draw_num_pill(162, 525, 7, fill=WHITE, stroke=PURPLE, r=12))
    lines.append(draw_num_pill(210, 526, 21, fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL, r=15.5, stroke_width=2.5, bold=True, font_size=14))
    lines.append(draw_num_pill(272, 510, 0, fill=WHITE, stroke=PURPLE_DARK, r=12))
    lines.append(draw_num_pill(275, 542, "42, 63…", fill=WHITE, stroke=PURPLE_DARK, r=11.5, font_size=10.5))

    lines.append(
        f'  <text x="230" y="630" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'Because Div(0) = &#x2115;, Div(21) &#x2229; Div(0) = Div(21), whose greatest element is 21.</text>'
    )
    lines.append(
        f'  <text x="230" y="648" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{NAVY_VAL}">'
        f'Result: Gcd(21, 0) = {{21}}   (why Euclid returns a when b = 0!)</text>'
    )

    # ------------------------------------------------------------------------
    # QUADRANT 4: Both Zero (a = 0, b = 0) -> Gcd(0, 0) = {0}
    # ------------------------------------------------------------------------
    lines.append(
        f'  <rect x="460" y="372" width="420" height="290" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
    )
    lines.append(
        f'  <rect x="460" y="372" width="420" height="40" rx="8" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2" />'
    )
    lines.append(
        f'  <text x="474" y="391" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">'
        f'Case D: Degenerate Corner (a = 0, b = 0) &#x2192; Gcd(0, 0) = {{0}}</text>'
    )
    lines.append(
        f'  <text x="474" y="406" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">'
        f'Div(0) &#x2229; Div(0) = &#x2115;; only g = 0 is divisible by every d &#x2208; &#x2115;!</text>'
    )

    # Outer box in Q4 is P1 = P2 = N
    lines.append(
        f'  <rect x="474" y="420" width="392" height="190" rx="8" fill="{PURPLE_LIGHT}" fill-opacity="0.5" stroke="{PURPLE}" stroke-width="2.0" />'
    )
    lines.append(
        f'  <text x="486" y="438" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">'
        f'P&#x2081;(g): g &#x2223; 0 = &#x2115;   and   P&#x2082;(g): g &#x2223; 0 = &#x2115;   (both expand to all of &#x2115;)</text>'
    )

    # Non-zero numbers in P1 & P2 \ P3
    for idx_n, val_n in enumerate([1, 2, 3, 4, 5]):
        lines.append(draw_num_pill(515 + idx_n * 38, 472, val_n, fill=WHITE, stroke=PURPLE, r=12.5))
    lines.append(draw_num_pill(740, 472, "6, 7, 8, …", fill=WHITE, stroke=PURPLE, r=12.5, font_size=11.5))
    lines.append(
        f'  <text x="670" y="500" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{GRAY_DARK}">'
        f'All g &gt; 0 fail P&#x2083; (e.g. d = g+1 divides 0, but (g+1) &#x2224; g)</text>'
    )

    # Inner circle P3 = {0}
    lines.append(
        f'  <ellipse cx="670" cy="554" rx="115" ry="44" fill="{PURPLE_FILL}" stroke="{NAVY_VAL}" stroke-width="2.6" stroke-dasharray="3,2" />'
    )
    lines.append(
        f'  <text x="628" y="546" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">'
        f'P&#x2083;(g): &#x2200;d &#x2208; &#x2115;. d &#x2223; g</text>'
    )
    lines.append(
        f'  <text x="628" y="564" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{NAVY_VAL}">'
        f'Gcd(0, 0) = {{0}}</text>'
    )
    lines.append(
        draw_num_pill(735, 554, 0, fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL, r=17, stroke_width=2.6, bold=True, font_size=15)
    )

    lines.append(
        f'  <text x="670" y="630" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
        f'Divisibility order (d &#x2223; g), not &#x2264;, makes 0 the top of the lattice (&#x2200;d. d &#x2223; 0).</text>'
    )
    lines.append(
        f'  <text x="670" y="648" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{NAVY_VAL}">'
        f'Result: Gcd(0, 0) = {{0}} without any special case in the type!</text>'
    )

    lines.extend(svg_footer())
    with open("fig-4.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ============================================================================
# FIGURE 5: Euclid's Algorithm Preserves the Intersection Until P2 Becomes N
# ============================================================================
def generate_fig5() -> None:
    W, H = 900, 650

    # Compute Euclid steps for (12, 8)
    steps = []
    x, y = 12, 8
    u = list(range(0, 13))
    while True:
        part = euler_partition(x, y, u)
        cdiv = sorted(common_div_set(x, y, u))
        steps.append((x, y, part, cdiv))
        if y == 0:
            break
        x, y = y, x % y

    assert len(steps) == 3
    assert steps[0][0:2] == (12, 8)
    assert steps[1][0:2] == (8, 4)
    assert steps[2][0:2] == (4, 0)
    for sx, sy, spart, scdiv in steps:
        assert scdiv == [1, 2, 4]
        assert spart["111"] == [4]

    lines = svg_header(W, H)

    # Title (<= 12 words)
    lines.append(
        f'  <text x="450" y="32" text-anchor="middle" font-family="{FONT_SERIF}" '
        f'font-size="21" font-weight="bold" fill="{INK}">'
        f'Euclid&#x2019;s Loop Reshapes Outer Circles While Locking Their Intersection</text>'
    )
    lines.append(
        f'  <text x="450" y="52" text-anchor="middle" font-family="{FONT_SANS}" font-size="13" fill="{GRAY_DARK}">'
        f'Loop invariant: Div(x) &#x2229; Div(y) = {{1, 2, 4}} and Gcd(x, y) = {{4}} never move as (x, y) steps (12, 8) &#x2192; (8, 4) &#x2192; (4, 0)</text>'
    )

    # Defs for the 3 step Venn diagrams
    lines.append("  <defs>")
    col_xs = [20, 312, 604]
    for idx, px in enumerate(col_xs):
        cax, cay, cr = px + 106, 250, 62
        cbx, cby = px + 170, 250
        cmx, cmy = px + 138, 304
        lines.append(f'    <clipPath id="f5-pa-{idx}"><circle cx="{cax}" cy="{cay}" r="{cr}" /></clipPath>')
        lines.append(f'    <clipPath id="f5-pb-{idx}"><circle cx="{cbx}" cy="{cby}" r="{cr}" /></clipPath>')
        lines.append(f'    <clipPath id="f5-pm-{idx}"><circle cx="{cmx}" cy="{cmy}" r="{cr}" /></clipPath>')
    lines.append("  </defs>")

    step_titles = [
        "Step 0 (Entry): (x, y) = (12, 8)",
        "Step 1 (After mod): (x, y) = (8, 4)",
        "Step 2 (Exit y = 0): (x, y) = (4, 0)",
    ]
    step_notes = [
        "12 mod 8 = 4; step to (8, 4)",
        "8 mod 4 = 0; step to (4, 0)",
        "y = 0: Div(0) = ℕ, so x = 4 ∈ Gcd(12, 8)!",
    ]

    for idx, (px, (sx, sy, spart, scdiv)) in enumerate(zip(col_xs, steps)):
        cax, cay, cr = px + 106, 250, 62
        cbx, cby = px + 170, 250
        cmx, cmy = px + 138, 304

        lines.append(
            f'  <rect x="{px}" y="68" width="276" height="404" rx="8" fill="{WHITE}" stroke="{GRAY_MID}" stroke-width="1.5" />'
        )
        hdr_fill = NAVY_FILL if sy == 0 else PURPLE_LIGHT
        hdr_stroke = NAVY_VAL if sy == 0 else PURPLE
        lines.append(
            f'  <rect x="{px}" y="68" width="276" height="44" rx="8" fill="{hdr_fill}" stroke="{hdr_stroke}" stroke-width="1.4" />'
        )
        lines.append(
            f'  <text x="{px + 138}" y="87" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">'
            f'{esc(step_titles[idx])}</text>'
        )
        lines.append(
            f'  <text x="{px + 138}" y="104" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE_DARK}">'
            f'Gcd({sx}, {sy}) = Gcd(12, 8) = {{4}}</text>'
        )

        if sy == 0:
            # In Step 2, y = 0 means P2: g | 0 is the entire universe box!
            lines.append(
                f'  <rect x="{px + 14}" y="124" width="248" height="258" rx="8" fill="{PURPLE_LIGHT}" fill-opacity="0.45" stroke="{PURPLE}" stroke-width="2.0" stroke-dasharray="6,3" />'
            )
            lines.append(
                f'  <text x="{px + 138}" y="142" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">'
                f'P&#x2082;: g &#x2223; 0 expands to ALL of &#x2115;</text>'
            )

        # Draw circles
        lines.append(f'  <circle cx="{cax}" cy="{cay}" r="{cr}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')
        if sy != 0:
            lines.append(f'  <circle cx="{cbx}" cy="{cby}" r="{cr}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')
        lines.append(f'  <circle cx="{cmx}" cy="{cmy}" r="{cr}" fill="{PURPLE_LIGHT}" fill-opacity="0.7" />')

        # Pairwise & Triple intersection
        if sy != 0:
            lines.append(
                f'  <g clip-path="url(#f5-pa-{idx})"><circle cx="{cbx}" cy="{cby}" r="{cr}" fill="{PURPLE_MID}" fill-opacity="0.6" /></g>'
            )
            lines.append(
                f'  <g clip-path="url(#f5-pa-{idx})"><g clip-path="url(#f5-pb-{idx})">'
                f'<circle cx="{cmx}" cy="{cmy}" r="{cr}" fill="{PURPLE_FILL}" />'
                f'</g></g>'
            )
        else:
            # When sy == 0, P1 & P2 is just P1! And P1 & P2 & P3 is P1 & P3!
            lines.append(
                f'  <circle cx="{cax}" cy="{cay}" r="{cr}" fill="{PURPLE_MID}" fill-opacity="0.55" />'
            )
            lines.append(
                f'  <g clip-path="url(#f5-pa-{idx})">'
                f'<circle cx="{cmx}" cy="{cmy}" r="{cr}" fill="{PURPLE_FILL}" />'
                f'</g>'
            )

        # Outlines
        lines.append(f'  <circle cx="{cax}" cy="{cay}" r="{cr}" fill="none" stroke="{PURPLE}" stroke-width="2.0" />')
        if sy != 0:
            lines.append(f'  <circle cx="{cbx}" cy="{cby}" r="{cr}" fill="none" stroke="{PURPLE}" stroke-width="2.0" stroke-dasharray="5,3" />')
        lines.append(f'  <circle cx="{cmx}" cy="{cmy}" r="{cr}" fill="none" stroke="{PURPLE_DARK}" stroke-width="2.0" stroke-dasharray="2,2" />')

        # Labels
        lines.append(f'  <text x="{cax - 24}" y="{cay - 68}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P&#x2081;: g&#x2223;{sx}</text>')
        if sy != 0:
            lines.append(f'  <text x="{cbx + 24}" y="{cby - 68}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P&#x2082;: g&#x2223;{sy}</text>')
        lines.append(f'  <text x="{cmx}" y="{cmy + 75}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" font-weight="bold" fill="{PURPLE_DARK}">P&#x2083;: &#x2200;d&#x2208;{{1,2,4}}. d&#x2223;g</text>')

        # Place elements according to exact partition `spart`
        # Locked center: 110 has [1, 2], 111 has [4]
        if sy != 0:
            lines.append(draw_num_pill(px + 124, 218, 1, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
            lines.append(draw_num_pill(px + 152, 218, 2, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
            lines.append(draw_num_pill(px + 138, 266, 4, fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL, r=14.5, stroke_width=2.5, bold=True, font_size=13.5))
        else:
            lines.append(draw_num_pill(px + 92, 224, 1, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
            lines.append(draw_num_pill(px + 120, 224, 2, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
            lines.append(draw_num_pill(px + 118, 272, 4, fill=NAVY_FILL, stroke=NAVY_VAL, text_color=NAVY_VAL, r=15.5, stroke_width=2.6, bold=True, font_size=14))

        # Outer elements that shift between steps!
        if idx == 0:
            # (12, 8): 100=[3,6], 101=[12], 011=[8], 001=[0]
            lines.append(draw_num_pill(px + 66, 232, 3, fill=WHITE, stroke=PURPLE, r=11, font_size=11))
            lines.append(draw_num_pill(px + 66, 258, 6, fill=WHITE, stroke=PURPLE, r=11, font_size=11))
            lines.append(draw_num_pill(px + 92, 290, 12, fill=WHITE, stroke=PURPLE_DARK, r=11.5, font_size=11))
            lines.append(draw_num_pill(px + 184, 290, 8, fill=WHITE, stroke=PURPLE_DARK, r=11.5, font_size=11))
            lines.append(draw_num_pill(px + 138, 342, 0, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
        elif idx == 1:
            # (8, 4): 100=[], 101=[8], 011=[], 001=[0, 12]
            lines.append(draw_num_pill(px + 92, 290, 8, fill=WHITE, stroke=PURPLE_DARK, r=11.5, font_size=11))
            lines.append(draw_num_pill(px + 122, 342, 0, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
            lines.append(draw_num_pill(px + 154, 342, 12, fill=WHITE, stroke=PURPLE_DARK, r=11.5, font_size=11))
            lines.append(f'  <text x="{px + 72}" y="245" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" fill="{GRAY_MID}">3,6,12</text>')
            lines.append(f'  <text x="{px + 72}" y="257" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" fill="{GRAY_MID}">expelled</text>')
        elif idx == 2:
            # (4, 0): P2=N, so 011 (P2 & P3 \ P1) has [0, 8, 12]
            lines.append(draw_num_pill(px + 162, 308, 8, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))
            lines.append(draw_num_pill(px + 162, 336, 12, fill=WHITE, stroke=PURPLE_DARK, r=11.5, font_size=11))
            lines.append(draw_num_pill(px + 132, 342, 0, fill=WHITE, stroke=PURPLE_DARK, r=11, font_size=11))

        # Step footer box
        lines.append(
            f'  <rect x="{px + 12}" y="394" width="252" height="66" rx="5" fill="{GRAY_BOX}" stroke="{GRAY_LIGHT}" stroke-width="1.2" />'
        )
        lines.append(
            f'  <text x="{px + 138}" y="412" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE_DARK}">'
            f'Locked: Div({sx}) &#x2229; Div({sy}) = {{1, 2, 4}}</text>'
        )
        lines.append(
            f'  <text x="{px + 138}" y="430" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{NAVY_VAL}">'
            f'Locked: P&#x2081; &#x2229; P&#x2082; &#x2229; P&#x2083; = {{4}}</text>'
        )
        lines.append(
            f'  <text x="{px + 138}" y="449" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">'
            f'{esc(step_notes[idx])}</text>'
        )

        # Arrows between panels (drawn after all panels)
    for idx_a in (0, 1):
        ax = col_xs[idx_a] + 276
        lines.append(f'  <line x1="{ax + 2}" y1="266" x2="{ax + 30}" y2="266" stroke="{NAVY_VAL}" stroke-width="2.5" />')
        lines.append(f'  <polygon points="{ax + 34},266 {ax + 24},260 {ax + 24},272" fill="{NAVY_VAL}" />')

    # BOTTOM PANEL: Why Return x Type-Checks at y = 0 (Codillon Proof Obligation)
    lines.append(
        f'  <rect x="20" y="488" width="860" height="142" rx="8" fill="{NAVY_FILL}" stroke="{NAVY_VAL}" stroke-width="1.6" />'
    )
    lines.append(
        f'  <text x="38" y="512" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{NAVY_VAL}">'
        f'How the Euler Diagram Explains Euclid&#x2019;s Return Proof Obligation in One Glance</text>'
    )
    lines.append(
        f'  <text x="38" y="535" font-family="{FONT_SERIF}" font-size="13" fill="{INK}">'
        f'1. <tspan font-weight="bold" fill="{PURPLE_DARK}">Loop Invariant (Conservation of Intersection):</tspan> '
        f'For all d, (d &#x2223; x &#x2227; d &#x2223; y) &#x21D4; (d &#x2223; y &#x2227; d &#x2223; (x mod y)). '
        f'Thus the lens P&#x2081; &#x2229; P&#x2082; = {{1, 2, 4}} and P&#x2083; never change.</text>'
    )
    lines.append(
        f'  <text x="38" y="558" font-family="{FONT_SERIF}" font-size="13" fill="{INK}">'
        f'2. <tspan font-weight="bold" fill="{PURPLE_DARK}">Outer Shedding:</tspan> '
        f'Each modulo step strips non-common divisors from the outer crescents (first 3, 6, 12 leave P&#x2081;; then 8 leaves P&#x2081;).</text>'
    )
    lines.append(
        f'  <text x="38" y="581" font-family="{FONT_SERIF}" font-size="13" fill="{INK}">'
        f'3. <tspan font-weight="bold" fill="{PURPLE_DARK}">Exit Collapse (y = 0):</tspan> '
        f'When y = 0, P&#x2082; (g &#x2223; 0) becomes &#x2115;, so CommonDiv(x, 0) = Div(x). '
        f'Since x &#x2223; x (P&#x2081;) and every d &#x2208; Div(x) divides x (P&#x2083;),</text>'
    )
    lines.append(
        f'  <text x="54" y="602" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{NAVY_VAL}">'
        f'x = 4 automatically inhabits P&#x2081; &#x2229; P&#x2082; &#x2229; P&#x2083; = Gcd(x, 0) = Gcd(12, 8) = {{4}}.   Q.E.D.</text>'
    )

    lines.extend(svg_footer())
    with open("fig-5.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    generate_fig5()
    print("Generated fig-1.svg .. fig-5.svg successfully.")
