#!/usr/bin/env python3
"""
Generator for Divisibility Lattice Visualizations of Gcd(a, b) as a Refinement Type.
Angle 01: Divisibility Hasse diagram, down-sets Div(a) and Div(b), their intersection,
and Gcd(a, b) as the unique top element (meet a ∧ b) whose down-set equals Div(a) ∩ Div(b).
"""

import math
from typing import Dict, List, Tuple, Set, Optional

# Palette (strict compliance: NO GREEN ANYWHERE)
BG_IVORY = "#fffff0"
INK = "#222222"
INK_MUTED = "#555555"
INK_LIGHT = "#888888"
GRAY_FAINT = "#d8d6c8"
GRAY_BOX = "#f3f1e4"

PURPLE = "#6A5ACD"        # Type / region purple
PURPLE_FILL = "#d9d5f2"   # Muted purple fill
PURPLE_LIGHT = "#ece9fa"  # Lighter purple tint
INDIGO = "#4b0082"        # Unknown / abstract
NAVY = "#00008b"          # Concrete run or value
NAVY_FILL = "#e2e6f7"     # Soft navy tint for Div(a) / Div(b) cones
RED_ERROR = "#8b0000"     # Violation / type error ONLY
RED_FILL = "#f9e2e2"      # Light error fill

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"


def gcd(a: int, b: int) -> int:
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)


def divisors(n: int) -> List[int]:
    if n <= 0:
        raise ValueError("divisors() requires positive integer for finite listing")
    return [d for d in range(1, n + 1) if n % d == 0]


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def prime_factorization(n: int) -> Dict[int, int]:
    factors: Dict[int, int] = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors


def hasse_edges(nodes: List[int]) -> List[Tuple[int, int, int]]:
    """
    Return directed cover edges (u, v, p) where u | v and v/u = p is prime,
    for u, v in nodes.
    """
    edges = []
    for u in sorted(nodes):
        for v in sorted(nodes):
            if v > u and v % u == 0:
                q = v // u
                if is_prime(q):
                    edges.append((u, v, q))
    return edges


def factor_str(n: int) -> str:
    if n == 1:
        return "1"
    f = prime_factorization(n)
    sup_map = {0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶"}
    parts = []
    for p in sorted(f.keys()):
        e = f[p]
        if e == 1:
            parts.append(f"{p}")
        else:
            parts.append(f"{p}{sup_map.get(e, '^' + str(e))}")
    return "·".join(parts)


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_header(width: int, height: int) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'  <defs>',
        f'    <marker id="arrow-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        f'      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{INK_MUTED}"/>',
        f'    </marker>',
        f'    <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">',
        f'      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{PURPLE}"/>',
        f'    </marker>',
        f'    <marker id="arrow-navy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">',
        f'      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{NAVY}"/>',
        f'    </marker>',
        f'    <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">',
        f'      <path d="M 0 1.5 L 8.5 5 L 0 8.5 z" fill="{RED_ERROR}"/>',
        f'    </marker>',
        f'  </defs>',
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="{BG_IVORY}"/>',
    ]


def svg_footer() -> List[str]:
    return ["</svg>"]


def grid_2_3_pos(
    n: int,
    origin_x: float,
    origin_y: float,
    vx2: Tuple[float, float],
    vx3: Tuple[float, float],
) -> Tuple[float, float]:
    """Position a number of form 2^i * 3^j on a 2D lattice."""
    f = prime_factorization(n)
    e2 = f.get(2, 0)
    e3 = f.get(3, 0)
    x = origin_x + e2 * vx2[0] + e3 * vx3[0]
    y = origin_y + e2 * vx2[1] + e3 * vx3[1]
    return (x, y)


def collinear(pts: List[Tuple[float, float]], eps: float = 1.0) -> bool:
    if len(pts) <= 2:
        return True
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return True
    for x, y in pts[1:-1]:
        dist = abs((x - x0) * dy - (y - y0) * dx) / L
        if dist > eps:
            return False
    return True


def convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def expand_polygon(pts: List[Tuple[float, float]], pad: float) -> str:
    """
    Create a clean, smooth SVG path enclosing a set of lattice points:
    - 1 point: circle of radius pad
    - collinear points (e.g. {1, 2, 4} or {1, 2, 4, 8} or {1, 3, 9}): stadium capsule
    - 2D polygon (e.g. Div(12), Div(6), Div(18)): smooth offset convex polygon
    """
    uniq = sorted(set(pts))
    if not uniq:
        return ""
    if len(uniq) == 1:
        x, y = uniq[0]
        return (
            f"M {x - pad:.1f} {y:.1f} "
            f"A {pad:.1f} {pad:.1f} 0 1 0 {x + pad:.1f} {y:.1f} "
            f"A {pad:.1f} {pad:.1f} 0 1 0 {x - pad:.1f} {y:.1f} Z"
        )
    if collinear(uniq):
        # Find the two extreme endpoints along the line
        p_start = uniq[0]
        p_end = uniq[-1]
        x1, y1 = p_start
        x2, y2 = p_end
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1.0
        # Normal vector (left of direction p_start -> p_end)
        nx, ny = -dy / L * pad, dx / L * pad
        p1 = (x1 + nx, y1 + ny)
        p2 = (x2 + nx, y2 + ny)
        p3 = (x2 - nx, y2 - ny)
        p4 = (x1 - nx, y1 - ny)
        # Sweep-flag=0 draws the outer semicircle around p_end and p_start
        return (
            f"M {p1[0]:.1f} {p1[1]:.1f} "
            f"L {p2[0]:.1f} {p2[1]:.1f} "
            f"A {pad:.1f} {pad:.1f} 0 0 0 {p3[0]:.1f} {p3[1]:.1f} "
            f"L {p4[0]:.1f} {p4[1]:.1f} "
            f"A {pad:.1f} {pad:.1f} 0 0 0 {p1[0]:.1f} {p1[1]:.1f} Z"
        )

    hull = convex_hull(uniq)
    n = len(hull)
    cx = sum(p[0] for p in hull) / n
    cy = sum(p[1] for p in hull) / n
    out_pts = []
    for i in range(n):
        p_prev = hull[(i - 1) % n]
        p_curr = hull[i]
        p_next = hull[(i + 1) % n]
        e1x, e1y = p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]
        l1 = math.hypot(e1x, e1y) or 1.0
        n1x, n1y = e1y / l1, -e1x / l1
        if (p_curr[0] + n1x - cx) ** 2 + (p_curr[1] + n1y - cy) ** 2 < (p_curr[0] - cx) ** 2 + (p_curr[1] - cy) ** 2:
            n1x, n1y = -n1x, -n1y

        e2x, e2y = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        l2 = math.hypot(e2x, e2y) or 1.0
        n2x, n2y = e2y / l2, -e2x / l2
        if (p_curr[0] + n2x - cx) ** 2 + (p_curr[1] + n2y - cy) ** 2 < (p_curr[0] - cx) ** 2 + (p_curr[1] - cy) ** 2:
            n2x, n2y = -n2x, -n2y

        bx, by = n1x + n2x, n1y + n2y
        bl = math.hypot(bx, by) or 1.0
        bx, by = bx / bl, by / bl
        dot = max(0.55, bx * n1x + by * n1y)
        scale = min(pad * 1.38, pad / dot)
        out_pts.append((p_curr[0] + bx * scale, p_curr[1] + by * scale))

    cmds = []
    m = len(out_pts)
    corner_r = min(20.0, pad * 0.55)
    for i in range(m):
        p_prev = out_pts[(i - 1) % m]
        p_curr = out_pts[i]
        p_next = out_pts[(i + 1) % m]
        v1x, v1y = p_prev[0] - p_curr[0], p_prev[1] - p_curr[1]
        l1 = math.hypot(v1x, v1y) or 1.0
        v2x, v2y = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        l2 = math.hypot(v2x, v2y) or 1.0
        r1 = min(corner_r, l1 * 0.35)
        r2 = min(corner_r, l2 * 0.35)
        s1 = (p_curr[0] + v1x / l1 * r1, p_curr[1] + v1y / l1 * r1)
        s2 = (p_curr[0] + v2x / l2 * r2, p_curr[1] + v2y / l2 * r2)
        if i == 0:
            cmds.append(f"M {s1[0]:.1f} {s1[1]:.1f}")
        else:
            cmds.append(f"L {s1[0]:.1f} {s1[1]:.1f}")
        cmds.append(f"Q {p_curr[0]:.1f} {p_curr[1]:.1f} {s2[0]:.1f} {s2[1]:.1f}")
    cmds.append("Z")
    return " ".join(cmds)


def draw_title_banner(
    out: List[str],
    title: str,
    subtitle: str,
    fig_num: str,
    width: int = 900,
) -> None:
    out.append(f'  <!-- Title Banner -->')
    out.append(f'  <text x="26" y="32" font-family="{FONT_SERIF}" font-size="18.5" font-weight="bold" fill="{INK}">{escape_xml(title)}</text>')
    out.append(f'  <text x="26" y="53" font-family="{FONT_SANS}" font-size="12.5" fill="{INK_MUTED}">{escape_xml(subtitle)}</text>')
    # Pill badge on top-right
    badge_w = max(210.0, len(fig_num) * 6.5 + 20.0)
    bx = width - 26 - badge_w
    out.append(f'  <rect x="{bx:.1f}" y="15" width="{badge_w:.1f}" height="22" rx="11" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.0"/>')
    out.append(f'  <text x="{bx + badge_w/2:.1f}" y="30" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{PURPLE}">{escape_xml(fig_num)}</text>')
    out.append(f'  <line x1="26" y1="64" x2="{width - 26}" y2="64" stroke="{GRAY_FAINT}" stroke-width="1.2"/>')


# ============================================================================
# FIGURE 1: a = 12, b = 8 -> Gcd(12, 8) = {4}
# ============================================================================
def generate_fig_1() -> None:
    width, height = 900, 625
    out = svg_header(width, height)

    draw_title_banner(
        out,
        title="Gcd(12, 8) is the unique top of the down-set intersection Div(12) ∩ Div(8)",
        subtitle="In the divisibility lattice of lcm(12, 8) = 24, each divisor set Div(n) is a downward cone; their intersection has top element 4.",
        fig_num="FIG 1 · CANONICAL LATTICE (12, 8)",
        width=width,
    )

    a, b = 12, 8
    L = lcm(a, b)  # 24
    g = gcd(a, b)  # 4
    nodes = divisors(L)       # [1, 2, 3, 4, 6, 8, 12, 24]
    div_a = set(divisors(a))  # {1, 2, 3, 4, 6, 12}
    div_b = set(divisors(b))  # {1, 2, 4, 8}
    common = div_a & div_b    # {1, 2, 4}

    # Lattice geometry: shifted right so left-most node 8 has ample room for labels
    origin_x, origin_y = 338.0, 524.0
    vx2 = (-72.0, -96.0)
    vx3 = (104.0, -96.0)
    pos = {n: grid_2_3_pos(n, origin_x, origin_y, vx2, vx3) for n in nodes}

    # 1. Draw down-set hulls
    pts_a = [pos[n] for n in div_a]
    pts_b = [pos[n] for n in div_b]
    pts_c = [pos[n] for n in common]

    path_a = expand_polygon(pts_a, 44.0)
    path_b = expand_polygon(pts_b, 40.0)
    path_c = expand_polygon(pts_c, 30.0)

    out.append(f'  <!-- Down-set cones -->')
    out.append(f'  <path d="{path_a}" fill="{NAVY_FILL}" fill-opacity="0.45" stroke="{NAVY}" stroke-width="1.8" stroke-dasharray="6,4"/>')
    out.append(f'  <path d="{path_b}" fill="{GRAY_BOX}" fill-opacity="0.60" stroke="{INK_MUTED}" stroke-width="1.8" stroke-dasharray="3,3"/>')
    out.append(f'  <path d="{path_c}" fill="{PURPLE_FILL}" fill-opacity="0.75" stroke="{PURPLE}" stroke-width="2.5"/>')

    # Direct region labels on the lattice (carefully positioned outside cone borders)
    p12 = pos[12]
    out.append(f'  <text x="{p12[0] + 54:.1f}" y="{p12[1] - 42:.1f}" font-family="{FONT_SERIF}" font-size="14.5" font-weight="bold" fill="{NAVY}">Down-set Div(12)</text>')
    out.append(f'  <text x="{p12[0] + 54:.1f}" y="{p12[1] - 24:.1f}" font-family="{FONT_SANS}" font-size="12" fill="{NAVY}">{{d ∈ ℕ | d ∣ 12}} = {{1, 2, 3, 4, 6, 12}}</text>')
    out.append(f'  <text x="{p12[0] + 54:.1f}" y="{p12[1] - 8:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">All divisors reachable below 12</text>')

    # Label for Div(8): placed above-left of node 8 inside canvas (x >= 26)
    p8 = pos[8]
    out.append(f'  <text x="26" y="{p8[1] - 66:.1f}" font-family="{FONT_SERIF}" font-size="14.5" font-weight="bold" fill="{INK}">Down-set Div(8)</text>')
    out.append(f'  <text x="26" y="{p8[1] - 48:.1f}" font-family="{FONT_SANS}" font-size="12" fill="{INK_MUTED}">{{d ∈ ℕ | d ∣ 8}} = {{1, 2, 4, 8}}</text>')
    out.append(f'  <line x1="78" y1="{p8[1] - 42:.1f}" x2="{p8[0] - 26:.1f}" y2="{p8[1] - 20:.1f}" stroke="{INK_MUTED}" stroke-width="1.2" stroke-dasharray="2,2"/>')

    # Label for Intersection Div(12) ∩ Div(8)
    p2 = pos[2]
    out.append(f'  <text x="26" y="{p2[1] + 10:.1f}" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{PURPLE}">Intersection Div(12) ∩ Div(8)</text>')
    out.append(f'  <text x="26" y="{p2[1] + 28:.1f}" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{PURPLE}">= {{1, 2, 4}} = Div(4)</text>')
    out.append(f'  <text x="26" y="{p2[1] + 44:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">Common divisors form a down-set</text>')
    out.append(f'  <line x1="168" y1="{p2[1] + 22:.1f}" x2="{p2[0] - 34:.1f}" y2="{p2[1] + 8:.1f}" stroke="{PURPLE}" stroke-width="1.4"/>')

    # Label for 24 = lcm(12, 8)
    p24 = pos[24]
    out.append(f'  <text x="{p24[0] + 32:.1f}" y="{p24[1] - 4:.1f}" font-family="{FONT_SERIF}" font-size="13" font-style="italic" fill="{INK_MUTED}">24 = lcm(12, 8) = 12 ∨ 8 (join)</text>')
    out.append(f'  <text x="{p24[0] + 32:.1f}" y="{p24[1] + 13:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_LIGHT}">ambient Hasse diagram: Div(24)</text>')

    # 2. Draw Hasse cover edges
    edges = hasse_edges(nodes)
    out.append(f'  <!-- Hasse cover edges (u | v with v/u prime) -->')
    for u, v, p in edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        r_start = 23.0
        r_end = 27.0 if v == g else 23.0
        sx, sy = x1 + dx / dist * r_start, y1 + dy / dist * r_start
        ex, ey = x2 - dx / dist * r_end, y2 - dy / dist * r_end

        in_common = (u in common) and (v in common)
        in_a_or_b = ((u in div_a and v in div_a) or (u in div_b and v in div_b))

        if in_common:
            stroke = PURPLE
            sw = "2.8"
            dash = ""
            marker = 'marker-end="url(#arrow-purple)"'
        elif in_a_or_b:
            stroke = INK_MUTED
            sw = "1.8"
            dash = ""
            marker = 'marker-end="url(#arrow-ink)"'
        else:
            stroke = INK_LIGHT
            sw = "1.3"
            dash = 'stroke-dasharray="4,3"'
            marker = ""

        out.append(f'  <line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{stroke}" stroke-width="{sw}" {dash} {marker}/>')
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        offset_x = -14 if p == 2 else 14
        lbl_col = PURPLE if in_common else INK_LIGHT
        out.append(f'  <text x="{mx + offset_x:.1f}" y="{my + 4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{lbl_col}">×{p}</text>')

    # 3. Draw nodes
    out.append(f'  <!-- Lattice nodes -->')
    for n in nodes:
        x, y = pos[n]
        if n == g:
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="27" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="3.2"/>')
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="21" fill="#ffffff" stroke="{PURPLE}" stroke-width="2.0"/>')
            out.append(f'  <text x="{x:.1f}" y="{y + 1:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="16" font-weight="bold" fill="{PURPLE}">{n}</text>')
            out.append(f'  <text x="{x:.1f}" y="{y + 14:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" fill="{PURPLE}">{factor_str(n)}</text>')
        elif n in (a, b):
            col = NAVY if n == a else INK
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="#ffffff" stroke="{col}" stroke-width="2.6"/>')
            out.append(f'  <text x="{x:.1f}" y="{y + 1:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{col}">{n}</text>')
            out.append(f'  <text x="{x:.1f}" y="{y + 13:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{INK_MUTED}">{factor_str(n)}</text>')
            tag = "a = 12" if n == a else "b = 8"
            out.append(f'  <rect x="{x - 24:.1f}" y="{y - 39:.1f}" width="48" height="16" rx="4" fill="{col}"/>')
            out.append(f'  <text x="{x:.1f}" y="{y - 27:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="#ffffff">{tag}</text>')
        elif n in common:
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.8"/>')
            out.append(f'  <text x="{x:.1f}" y="{y + 1:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">{n}</text>')
            out.append(f'  <text x="{x:.1f}" y="{y + 13:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{INK_MUTED}">{factor_str(n)}</text>')
        elif n in div_a:
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="#ffffff" stroke="{NAVY}" stroke-width="1.6"/>')
            out.append(f'  <text x="{x:.1f}" y="{y + 1:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14" fill="{INK}">{n}</text>')
            out.append(f'  <text x="{x:.1f}" y="{y + 13:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{INK_MUTED}">{factor_str(n)}</text>')
        else:
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="{BG_IVORY}" stroke="{INK_LIGHT}" stroke-width="1.4" stroke-dasharray="3,2"/>')
            out.append(f'  <text x="{x:.1f}" y="{y + 1:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14" fill="{INK_MUTED}">{n}</text>')
            out.append(f'  <text x="{x:.1f}" y="{y + 13:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{INK_LIGHT}">{factor_str(n)}</text>')

    # Callout badge on node 4 (placed to the left of 4 so it never obscures the ×2 edge)
    p4 = pos[4]
    out.append(f'  <rect x="{p4[0] - 134:.1f}" y="{p4[1] - 11:.1f}" width="102" height="20" rx="4" fill="{PURPLE}"/>')
    out.append(f'  <text x="{p4[0] - 83:.1f}" y="{p4[1] + 3:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="#ffffff">TOP = 12 ∧ 8 = 4</text>')

    # 4. Right-hand Visual Encoding & Refinement Type Anatomy Panel
    px, py, pw, ph = 556.0, 86.0, 318.0, 494.0
    out.append(f'  <!-- Right Panel: Refinement Type Definition & Order Guide -->')
    out.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="8" fill="{GRAY_BOX}" stroke="{GRAY_FAINT}" stroke-width="1.5"/>')

    # Section A: The Refinement Type
    out.append(f'  <text x="{px + 14:.1f}" y="{py + 25:.1f}" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{PURPLE}">The Refinement Type Gcd(12, 8)</text>')
    out.append(f'  <rect x="{px + 12:.1f}" y="{py + 35:.1f}" width="{pw - 24:.1f}" height="68" rx="6" fill="#ffffff" stroke="{PURPLE}" stroke-width="1.8"/>')
    out.append(f'  <text x="{px + pw/2:.1f}" y="{py + 57:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{INK}">Gcd(a, b) = {{ g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }}</text>')
    out.append(f'  <text x="{px + pw/2:.1f}" y="{py + 78:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" fill="{PURPLE}">For (12, 8):  Div(g) = {{1, 2, 4}}  ⟺  g = 4</text>')
    out.append(f'  <text x="{px + pw/2:.1f}" y="{py + 95:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">Singleton set {{4}} — exactly one inhabitant</text>')

    # Section B: Why "Down-set Equality" pins down the Top Element
    y_b = py + 126
    out.append(f'  <text x="{px + 14:.1f}" y="{y_b:.1f}" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{INK}">Why Down-Set Equality = Lattice Meet</text>')
    out.append(f'  <text x="{px + 14:.1f}" y="{y_b + 20:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">1. Every number n generates a down-set Div(n):</text>')
    out.append(f'  <text x="{px + 26:.1f}" y="{y_b + 36:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">all nodes reachable by stepping down (÷2, ÷3).</text>')
    out.append(f'  <text x="{px + 14:.1f}" y="{y_b + 56:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">2. Intersecting two down-sets gives a down-set:</text>')
    out.append(f'  <text x="{px + 26:.1f}" y="{y_b + 72:.1f}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{PURPLE}">Div(12) ∩ Div(8) = {{1, 2, 4}}.</text>')
    out.append(f'  <text x="{px + 14:.1f}" y="{y_b + 92:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">3. By antisymmetry of divisibility, at most one</text>')
    out.append(f'  <text x="{px + 26:.1f}" y="{y_b + 108:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">generator g has Div(g) = {{1, 2, 4}}: its</text>')
    out.append(f'  <text x="{px + 26:.1f}" y="{y_b + 124:.1f}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{PURPLE}">unique top element g = 4 (meet 12 ∧ 8).</text>')

    # Section C: Three Equivalences Box
    y_c = py + 270
    out.append(f'  <rect x="{px + 12:.1f}" y="{y_c:.1f}" width="{pw - 24:.1f}" height="112" rx="6" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2"/>')
    out.append(f'  <text x="{px + 20:.1f}" y="{y_c + 20:.1f}" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">Three Equivalent Views of g = 4:</text>')
    out.append(f'  <text x="{px + 18:.1f}" y="{y_c + 40:.1f}" font-family="{FONT_SANS}" font-size="11" fill="{INK}">• Common divisor: 4 ∣ 12 and 4 ∣ 8 (4 ∈ Div(12)∩Div(8))</text>')
    out.append(f'  <text x="{px + 20:.1f}" y="{y_c + 59:.1f}" font-family="{FONT_SANS}" font-size="11.2" fill="{INK}">• Greatest (top): ∀d ∈ {{1, 2, 4}}, d ∣ 4 (all purple</text>')
    out.append(f'  <text x="{px + 30:.1f}" y="{y_c + 74:.1f}" font-family="{FONT_SANS}" font-size="11.2" fill="{INK}">arrows inside the intersection climb to 4)</text>')
    out.append(f'  <text x="{px + 20:.1f}" y="{y_c + 95:.1f}" font-family="{FONT_SANS}" font-size="11.2" font-weight="bold" fill="{PURPLE}">• Exponent min: 2^min(2,3) · 3^min(1,0) = 2²·3⁰ = 4</text>')

    # Section D: Coordinate Compass (Prime Factors)
    y_d = py + 404
    out.append(f'  <text x="{px + 14:.1f}" y="{y_d:.1f}" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">Hasse Diagram Axes (Prime Factors):</text>')
    cx_comp, cy_comp = px + 60, y_d + 58
    out.append(f'  <line x1="{cx_comp:.1f}" y1="{cy_comp:.1f}" x2="{cx_comp - 30:.1f}" y2="{cy_comp - 36:.1f}" stroke="{INK}" stroke-width="1.8" marker-end="url(#arrow-ink)"/>')
    out.append(f'  <line x1="{cx_comp:.1f}" y1="{cy_comp:.1f}" x2="{cx_comp + 42:.1f}" y2="{cy_comp - 36:.1f}" stroke="{INK}" stroke-width="1.8" marker-end="url(#arrow-ink)"/>')
    out.append(f'  <circle cx="{cx_comp:.1f}" cy="{cy_comp:.1f}" r="3.5" fill="{INK}"/>')
    out.append(f'  <text x="{cx_comp - 34:.1f}" y="{cy_comp - 41:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{INK}">×2</text>')
    out.append(f'  <text x="{cx_comp + 48:.1f}" y="{cy_comp - 41:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{INK}">×3</text>')
    out.append(f'  <text x="{px + 126:.1f}" y="{y_d + 24:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">Up-left step multiplies by 2</text>')
    out.append(f'  <text x="{px + 126:.1f}" y="{y_d + 42:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">Up-right step multiplies by 3</text>')
    out.append(f'  <text x="{px + 126:.1f}" y="{y_d + 60:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">u ∣ v iff a path climbs u →* v</text>')

    # Bottom footer annotation
    out.append(f'  <text x="26" y="604" font-family="{FONT_SANS}" font-size="12" fill="{INK_MUTED}">Refinement view: Base type ℕ = all lattice nodes; Predicate P(g) ≔ (Div(g) = Div(12) ∩ Div(8)) selects the single node whose down-cone matches the purple cone.</text>')

    out.extend(svg_footer())
    with open("fig-1.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 2: TYPE ERRORS on (12, 8) — Three Ways a Candidate Fails
# ============================================================================
def generate_fig_2() -> None:
    width, height = 900, 650
    out = svg_header(width, height)

    draw_title_banner(
        out,
        title="Type Errors in Gcd(12, 8): Why g = 2, g = 8, and g = 6 Are Rejected",
        subtitle="A candidate g inhabits Gcd(12, 8) iff its down-set Div(g) equals the target intersection Div(12) ∩ Div(8) = {1, 2, 4}.",
        fig_num="FIG 2 · TYPE ERROR ANATOMY (12, 8)",
        width=width,
    )

    a, b = 12, 8
    L = lcm(a, b)  # 24
    nodes = divisors(L)
    div_a = set(divisors(a))
    div_b = set(divisors(b))
    target = div_a & div_b  # {1, 2, 4}
    edges = hasse_edges(nodes)

    panels = [
        {
            "cand": 2,
            "title": "Case A: Candidate g = 2",
            "verdict": "TYPE ERROR: Too Small (Not Top)",
            "clause_fail": "Fails: ∀d ∈ Div(12)∩Div(8), d ∣ g",
            "witness": "Witness d = 4:  4 ∣ 12 and 4 ∣ 8, but 4 ∤ 2",
            "set_cmp": "Div(2) = {1, 2}  ⊊  {1, 2, 4}",
            "line1": "2 is inside the common down-set, but sits",
            "line2": "below top element 4 (leaves 4 uncovered).",
        },
        {
            "cand": 8,
            "title": "Case B: Candidate g = 8",
            "verdict": "TYPE ERROR: Outside Div(12)",
            "clause_fail": "Fails: g ∣ 12  (not a common divisor)",
            "witness": "Witness d = 8 ∈ Div(8), but 8 ∉ Div(12)",
            "set_cmp": "Div(8) = {1, 2, 4, 8}  ⊋  {1, 2, 4}",
            "line1": "8 climbs one ×2 step past the meet 4;",
            "line2": "its down-set spills outside Div(12).",
        },
        {
            "cand": 6,
            "title": "Case C: Candidate g = 6",
            "verdict": "TYPE ERROR: Incomparable Branch",
            "clause_fail": "Fails BOTH: 6 ∤ 8  and  4 ∤ 6",
            "witness": "Spills into ×3 branch (3, 6) AND misses 4",
            "set_cmp": "Div(6) = {1, 2, 3, 6}  ≠  {1, 2, 4}",
            "line1": "6 is in Div(12) only; its cone neither",
            "line2": "contains nor is contained in {1, 2, 4}.",
        },
    ]

    panel_w = 274.0
    panel_h = 528.0
    gap = 16.0
    start_x = 23.0
    panel_y = 82.0

    for idx, pinfo in enumerate(panels):
        cand = pinfo["cand"]
        div_c = set(divisors(cand))
        px = start_x + idx * (panel_w + gap)
        py = panel_y

        out.append(f'  <!-- Panel {idx + 1}: Candidate g = {cand} -->')
        out.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="{panel_h:.1f}" rx="8" fill="#ffffff" stroke="{GRAY_FAINT}" stroke-width="1.6"/>')

        # Header banner (Red error header)
        out.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="52" rx="8" fill="{RED_FILL}" stroke="{RED_ERROR}" stroke-width="1.5"/>')
        out.append(f'  <text x="{px + 12:.1f}" y="{py + 21:.1f}" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{RED_ERROR}">{escape_xml(pinfo["title"])}   ✗</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{py + 41:.1f}" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{RED_ERROR}">{escape_xml(pinfo["verdict"])}</text>')

        # Mini lattice coordinates inside panel (shifted slightly right for clean left margin)
        orig_x = px + 148.0
        orig_y = py + 340.0
        vx2 = (-39.0, -63.0)
        vx3 = (56.0, -63.0)
        pos = {n: grid_2_3_pos(n, orig_x, orig_y, vx2, vx3) for n in nodes}

        # Faint outlines of Div(12) and Div(8) for context
        path_a = expand_polygon([pos[n] for n in div_a], 24.0)
        path_b = expand_polygon([pos[n] for n in div_b], 22.0)
        out.append(f'  <path d="{path_a}" fill="none" stroke="{INK_LIGHT}" stroke-width="1.0" stroke-dasharray="3,3"/>')
        out.append(f'  <path d="{path_b}" fill="none" stroke="{INK_LIGHT}" stroke-width="1.0" stroke-dasharray="3,3"/>')

        # Target intersection Div(12) ∩ Div(8) = {1, 2, 4} in purple
        path_target = expand_polygon([pos[n] for n in target], 22.0)
        out.append(f'  <path d="{path_target}" fill="{PURPLE_FILL}" fill-opacity="0.62" stroke="{PURPLE}" stroke-width="2.0"/>')

        # Candidate's down-set Div(cand) in dashed dark red
        path_cand = expand_polygon([pos[n] for n in div_c], 17.5)
        out.append(f'  <path d="{path_cand}" fill="{RED_FILL}" fill-opacity="0.38" stroke="{RED_ERROR}" stroke-width="2.2" stroke-dasharray="5,3"/>')

        # Draw edges
        for u, v, p in edges:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            sx, sy = x1 + dx / dist * 14.0, y1 + dy / dist * 14.0
            ex, ey = x2 - dx / dist * 14.0, y2 - dy / dist * 14.0
            in_t = (u in target) and (v in target)
            col = PURPLE if in_t else GRAY_FAINT
            sw = "2.0" if in_t else "1.2"
            out.append(f'  <line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" stroke-width="{sw}"/>')

        # Draw nodes first so callout labels sit cleanly on top
        for n in nodes:
            x, y = pos[n]
            in_t = n in target
            in_c = n in div_c

            if n == cand:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="17" fill="{RED_FILL}" stroke="{RED_ERROR}" stroke-width="2.8"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{RED_ERROR}">{n}</text>')
            elif n == 4:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="15.5" fill="#ffffff" stroke="{PURPLE}" stroke-width="2.4"/>')
                if 4 not in div_c:
                    out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="19.5" fill="none" stroke="{RED_ERROR}" stroke-width="1.6" stroke-dasharray="3,2"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">{n}</text>')
            elif in_c and not in_t:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="{RED_FILL}" stroke="{RED_ERROR}" stroke-width="1.8"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{RED_ERROR}">{n}</text>')
            elif in_t and in_c:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="13.5" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.6"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" fill="{INK}">{n}</text>')
            else:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="12.5" fill="{BG_IVORY}" stroke="{INK_LIGHT}" stroke-width="1.1"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" fill="{INK_LIGHT}">{n}</text>')

        # Special error callout arrows and well-inside-panel labels
        p4 = pos[4]
        out.append(f'  <rect x="{p4[0] - 56:.1f}" y="{p4[1] - 8:.1f}" width="36" height="15" rx="3" fill="{PURPLE}"/>')
        out.append(f'  <text x="{p4[0] - 38:.1f}" y="{p4[1] + 3:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="bold" fill="#ffffff">Top=4</text>')
        if cand == 2:
            x2, y2 = pos[2]
            x4, y4 = pos[4]
            out.append(f'  <text x="{px + 12:.1f}" y="{y2 + 4:.1f}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{RED_ERROR}">g = 2 ✗</text>')
            out.append(f'  <path d="M {x4 + 20:.1f} {y4 - 2:.1f} Q {x4 + 54:.1f} {(y4 + y2)/2 - 8:.1f} {x2 + 19:.1f} {y2 - 4:.1f}" fill="none" stroke="{RED_ERROR}" stroke-width="2.0" stroke-dasharray="4,2" marker-end="url(#arrow-red)"/>')
            out.append(f'  <text x="{x4 + 46:.1f}" y="{(y4 + y2)/2 - 8:.1f}" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED_ERROR}">4 ∤ 2 (misses 4)</text>')
        elif cand == 8:
            x8, y8 = pos[8]
            x12, y12 = pos[12]
            out.append(f'  <text x="{x8:.1f}" y="{y8 - 23:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{RED_ERROR}">g = 8 ✗</text>')
            out.append(f'  <line x1="{x8 + 18:.1f}" y1="{y8:.1f}" x2="{x12 - 16:.1f}" y2="{y12:.1f}" stroke="{RED_ERROR}" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#arrow-red)"/>')
            mx, my = (x8 + x12) / 2, (y8 + y12) / 2
            out.append(f'  <text x="{mx:.1f}" y="{my - 7:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED_ERROR}">8 ∤ 12</text>')
        elif cand == 6:
            x4, y4 = pos[4]
            x6, y6 = pos[6]
            out.append(f'  <text x="{x6 + 21:.1f}" y="{y6 + 4:.1f}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{RED_ERROR}">g = 6 ✗</text>')
            out.append(f'  <line x1="{x4 + 19:.1f}" y1="{y4:.1f}" x2="{x6 - 19:.1f}" y2="{y6:.1f}" stroke="{RED_ERROR}" stroke-width="1.8" stroke-dasharray="4,3"/>')
            mx, my = (x4 + x6) / 2, (y4 + y6) / 2
            out.append(f'  <text x="{mx:.1f}" y="{my - 7:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="{RED_ERROR}">4 ∤ 6, 6 ∤ 8</text>')

        # Bottom diagnostic card inside each panel
        diag_y = py + 372.0
        out.append(f'  <line x1="{px + 12:.1f}" y1="{diag_y:.1f}" x2="{px + panel_w - 12:.1f}" y2="{diag_y:.1f}" stroke="{GRAY_FAINT}" stroke-width="1.2"/>')
        out.append(f'  <rect x="{px + 12:.1f}" y="{diag_y + 10:.1f}" width="{panel_w - 24:.1f}" height="32" rx="5" fill="{RED_FILL}" stroke="{RED_ERROR}" stroke-width="1.2"/>')
        out.append(f'  <text x="{px + panel_w/2:.1f}" y="{diag_y + 30:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{RED_ERROR}">{escape_xml(pinfo["set_cmp"])}</text>')

        out.append(f'  <text x="{px + 12:.1f}" y="{diag_y + 62:.1f}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{RED_ERROR}">{escape_xml(pinfo["clause_fail"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{diag_y + 81:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">{escape_xml(pinfo["witness"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{diag_y + 106:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">{escape_xml(pinfo["line1"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{diag_y + 123:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">{escape_xml(pinfo["line2"])}</text>')

    # Bottom synthesis bar
    out.append(f'  <rect x="23" y="618" width="854" height="24" rx="4" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.0"/>')
    out.append(f'  <text x="450" y="634" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{INK}">Visual Type-Check Rule: Red dashed cone Div(g) must coincide EXACTLY with purple target cone Div(12) ∩ Div(8) = {{1, 2, 4}}.</text>')

    out.extend(svg_footer())
    with open("fig-2.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 3: Dependent Type Family — Contrasting (12, 8) vs (18, 12) vs (9, 8)
# ============================================================================
def generate_fig_3() -> None:
    width, height = 900, 650
    out = svg_header(width, height)

    draw_title_banner(
        out,
        title="Dependent Type Family (a, b) ↦ Gcd(a, b): Input Values Shift the Meet",
        subtitle="Within the same ambient divisibility lattice Div(72), changing parameters (a, b) re-indexes the cones and relocates the type's inhabitant.",
        fig_num="FIG 3 · DEPENDENT TYPE INDEXING",
        width=width,
    )

    L = 72
    nodes = divisors(L)  # [1, 2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 72]
    edges = hasse_edges(nodes)

    cases = [
        {
            "a": 12,
            "b": 8,
            "g": gcd(12, 8),
            "header": "Instance 1: Gcd(12, 8) = {4}",
            "sub": "Pure power-of-2 intersection",
            "formula": "Div(12) ∩ Div(8) = {1, 2, 4} = Div(4)",
            "exp_note": "min((2,1), (3,0)) = (2,0) → 2²·3⁰ = 4",
            "insight": "Meet lands on the left boundary (×2 axis).",
        },
        {
            "a": 18,
            "b": 12,
            "g": gcd(18, 12),
            "header": "Instance 2: Gcd(18, 12) = {6}",
            "sub": "Mixed 2·3 rectangle intersection",
            "formula": "Div(18) ∩ Div(12) = {1, 2, 3, 6} = Div(6)",
            "exp_note": "min((1,2), (2,1)) = (1,1) → 2¹·3¹ = 6",
            "insight": "Meet shifts to interior node 6 = 2·3.",
        },
        {
            "a": 9,
            "b": 8,
            "g": gcd(9, 8),
            "header": "Instance 3: Gcd(9, 8) = {1} (Coprime)",
            "sub": "Orthogonal axes meet only at bottom 1",
            "formula": "Div(9) ∩ Div(8) = {1} = Div(1)",
            "exp_note": "min((0,2), (3,0)) = (0,0) → 2⁰·3⁰ = 1",
            "insight": "Disjoint prime axes collapse cone to {1}.",
        },
    ]

    panel_w = 274.0
    panel_h = 492.0
    gap = 16.0
    start_x = 23.0
    panel_y = 118.0

    # Top Dependency Banner
    out.append(f'  <rect x="23" y="74" width="854" height="34" rx="6" fill="{GRAY_BOX}" stroke="{PURPLE}" stroke-width="1.3"/>')
    out.append(f'  <text x="450" y="96" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">Dependent Type Signature:   Gcd : (a : ℕ) → (b : ℕ) → Type     where   Gcd(a, b) ≔ {{ g ∈ ℕ | Div(g) = Div(a) ∩ Div(b) }}</text>')

    for idx, c in enumerate(cases):
        a, b, g = c["a"], c["b"], c["g"]
        div_a = set(divisors(a))
        div_b = set(divisors(b))
        common = div_a & div_b

        px = start_x + idx * (panel_w + gap)
        py = panel_y

        out.append(f'  <!-- Panel {idx + 1}: ({a}, {b}) -> {g} -->')
        out.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="{panel_h:.1f}" rx="8" fill="#ffffff" stroke="{GRAY_FAINT}" stroke-width="1.6"/>')

        # Panel Header
        out.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="48" rx="8" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.4"/>')
        out.append(f'  <text x="{px + 12:.1f}" y="{py + 21:.1f}" font-family="{FONT_SERIF}" font-size="14.5" font-weight="bold" fill="{PURPLE}">{escape_xml(c["header"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{py + 39:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">{escape_xml(c["sub"])}</text>')

        # Lattice coordinates inside panel
        orig_x = px + 146.0
        orig_y = py + 344.0
        vx2 = (-35.0, -52.0)
        vx3 = (48.0, -52.0)
        pos = {n: grid_2_3_pos(n, orig_x, orig_y, vx2, vx3) for n in nodes}

        # Down-set hulls (now smooth stadium capsules for collinear sets!)
        path_a = expand_polygon([pos[n] for n in div_a], 21.0)
        path_b = expand_polygon([pos[n] for n in div_b], 19.5)
        path_c = expand_polygon([pos[n] for n in common], 17.5)

        out.append(f'  <path d="{path_a}" fill="{NAVY_FILL}" fill-opacity="0.45" stroke="{NAVY}" stroke-width="1.5" stroke-dasharray="5,3"/>')
        out.append(f'  <path d="{path_b}" fill="{GRAY_BOX}" fill-opacity="0.58" stroke="{INK_MUTED}" stroke-width="1.5" stroke-dasharray="3,3"/>')
        out.append(f'  <path d="{path_c}" fill="{PURPLE_FILL}" fill-opacity="0.80" stroke="{PURPLE}" stroke-width="2.3"/>')

        # Edges
        for u, v, p in edges:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            sx, sy = x1 + dx / dist * 13.0, y1 + dy / dist * 13.0
            ex, ey = x2 - dx / dist * 13.0, y2 - dy / dist * 13.0
            in_c = (u in common) and (v in common)
            in_ab = ((u in div_a and v in div_a) or (u in div_b and v in div_b))
            col = PURPLE if in_c else (INK_MUTED if in_ab else GRAY_FAINT)
            sw = "2.2" if in_c else ("1.4" if in_ab else "1.0")
            out.append(f'  <line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" stroke-width="{sw}"/>')

        # Nodes
        for n in nodes:
            x, y = pos[n]
            if n == g:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="16.5" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="2.8"/>')
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="12.5" fill="#ffffff" stroke="{PURPLE}" stroke-width="1.5"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{PURPLE}">{n}</text>')
            elif n in (a, b):
                col = NAVY if n == a else INK
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="#ffffff" stroke="{col}" stroke-width="2.2"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{col}">{n}</text>')
                lbl = f"a={a}" if n == a else f"b={b}"
                out.append(f'  <rect x="{x - 18:.1f}" y="{y - 31:.1f}" width="36" height="14" rx="3" fill="{col}"/>')
                out.append(f'  <text x="{x:.1f}" y="{y - 21:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="#ffffff">{lbl}</text>')
            elif n in common:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="12.5" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.5"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11.5" fill="{INK}">{n}</text>')
            elif n in div_a or n in div_b:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="#ffffff" stroke="{INK_MUTED}" stroke-width="1.2"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" fill="{INK_MUTED}">{n}</text>')
            else:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{BG_IVORY}" stroke="{GRAY_FAINT}" stroke-width="1.0"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="10.5" fill="{INK_LIGHT}">{n}</text>')

        # Callout pill on g
        gx, gy = pos[g]
        if idx == 0:
            bx_g, by_g = gx - 54, gy - 8
        elif idx == 1:
            bx_g, by_g = gx - 54, gy - 8
        else:
            bx_g, by_g = gx + 22, gy - 8
        out.append(f'  <rect x="{bx_g:.1f}" y="{by_g:.1f}" width="34" height="16" rx="4" fill="{PURPLE}"/>')
        out.append(f'  <text x="{bx_g + 17:.1f}" y="{by_g + 12:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="#ffffff">g={g}</text>')

        # Bottom summary box inside panel
        by = py + 372.0
        out.append(f'  <line x1="{px + 12:.1f}" y1="{by:.1f}" x2="{px + panel_w - 12:.1f}" y2="{by:.1f}" stroke="{GRAY_FAINT}" stroke-width="1.2"/>')
        out.append(f'  <rect x="{px + 12:.1f}" y="{by + 10:.1f}" width="{panel_w - 24:.1f}" height="30" rx="5" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2"/>')
        out.append(f'  <text x="{px + panel_w/2:.1f}" y="{by + 29:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE}">{escape_xml(c["formula"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{by + 60:.1f}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{INK}">Exponent meet:</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{by + 78:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">{escape_xml(c["exp_note"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{by + 102:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{PURPLE}">{escape_xml(c["insight"])}</text>')

    # Footer note
    out.append(f'  <text x="450" y="632" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" fill="{INK_MUTED}">Notice: 4 ∈ Gcd(12, 8) is well-typed in Panel 1, but 4 ∉ Gcd(18, 12) and 4 ∉ Gcd(9, 8) — the type itself moves with the values (a, b).</text>')

    out.extend(svg_footer())
    with open("fig-3.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 4: Subtyping as Lattice Order & The Universal Top Element 0
# ============================================================================
def generate_fig_4() -> None:
    width, height = 900, 625
    out = svg_header(width, height)

    draw_title_banner(
        out,
        title="Divisibility IS Subtyping on Divisor Cones — and 0 Is the Universal Top",
        subtitle="Because d ∣ n ⟺ Div(d) ⊆ Div(n), subtyping is set containment of down-sets; since every d divides 0, Div(0) = ℕ makes 0 the identity for ∧.",
        fig_num="FIG 4 · SUBTYPING & ZERO TOP (12, 0)",
        width=width,
    )

    # Left half: Nested Divisor Cones Div(2) ⊂ Div(4) ⊂ Div(12)
    lx, ly, lw, lh = 26.0, 82.0, 416.0, 505.0
    out.append(f'  <!-- Left Panel: Subtyping as Set Containment of Down-Sets -->')
    out.append(f'  <rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="{lh:.1f}" rx="8" fill="#ffffff" stroke="{GRAY_FAINT}" stroke-width="1.6"/>')
    out.append(f'  <rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="48" rx="8" fill="{GRAY_BOX}" stroke="{GRAY_FAINT}" stroke-width="1.2"/>')
    out.append(f'  <text x="{lx + 14:.1f}" y="{ly + 21:.1f}" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">1. Subtyping = Down-Set Containment</text>')
    out.append(f'  <text x="{lx + 14:.1f}" y="{ly + 40:.1f}" font-family="{FONT_SANS}" font-size="12" fill="{INK_MUTED}">Every divisibility edge d ∣ n is a subset inclusion Div(d) ⊆ Div(n)</text>')

    nodes_12 = divisors(12)  # [1, 2, 3, 4, 6, 12]
    edges_12 = hasse_edges(nodes_12)
    orig_x1, orig_y1 = lx + 212.0, ly + 356.0
    vx2_1 = (-66.0, -72.0)
    vx3_1 = (90.0, -72.0)
    pos1 = {n: grid_2_3_pos(n, orig_x1, orig_y1, vx2_1, vx3_1) for n in nodes_12}

    # Nested hulls: Div(12) ⊃ Div(4) ⊃ Div(2)
    p_div12 = expand_polygon([pos1[n] for n in divisors(12)], 36.0)
    p_div4 = expand_polygon([pos1[n] for n in divisors(4)], 27.0)
    p_div2 = expand_polygon([pos1[n] for n in divisors(2)], 19.5)

    out.append(f'  <path d="{p_div12}" fill="{NAVY_FILL}" fill-opacity="0.40" stroke="{NAVY}" stroke-width="1.8"/>')
    out.append(f'  <path d="{p_div4}" fill="{PURPLE_FILL}" fill-opacity="0.65" stroke="{PURPLE}" stroke-width="2.2"/>')
    out.append(f'  <path d="{p_div2}" fill="#ffffff" fill-opacity="0.75" stroke="{INDIGO}" stroke-width="1.8" stroke-dasharray="4,2"/>')

    # Labels on nested shells (positioned cleanly outside capsule borders)
    out.append(f'  <text x="{pos1[12][0] + 40:.1f}" y="{pos1[12][1] - 10:.1f}" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{NAVY}">Div(12)</text>')
    out.append(f'  <text x="{pos1[4][0] - 32:.1f}" y="{pos1[4][1] - 12:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">Div(4)</text>')
    out.append(f'  <text x="{pos1[2][0] - 28:.1f}" y="{pos1[2][1] + 6:.1f}" text-anchor="end" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{INDIGO}">Div(2)</text>')

    for u, v, p in edges_12:
        x1, y1 = pos1[u]
        x2, y2 = pos1[v]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        sx, sy = x1 + dx / dist * 16.0, y1 + dy / dist * 16.0
        ex, ey = x2 - dx / dist * 16.0, y2 - dy / dist * 16.0
        in_4 = (u in divisors(4)) and (v in divisors(4))
        col = PURPLE if in_4 else NAVY
        out.append(f'  <line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" stroke-width="2.0" marker-end="url(#arrow-ink)"/>')

    for n in nodes_12:
        x, y = pos1[n]
        col = PURPLE if n in divisors(4) else NAVY
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="15.5" fill="#ffffff" stroke="{col}" stroke-width="2.0"/>')
        out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{col}">{n}</text>')

    # Isomorphism box at bottom of left panel
    by1 = ly + 402.0
    out.append(f'  <rect x="{lx + 14:.1f}" y="{by1:.1f}" width="{lw - 28:.1f}" height="88" rx="6" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.3"/>')
    out.append(f'  <text x="{lx + lw/2:.1f}" y="{by1 + 22:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{INK}">Order-Embedding Isomorphism:</text>')
    out.append(f'  <text x="{lx + lw/2:.1f}" y="{by1 + 44:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">1 ∣ 2 ∣ 4 ∣ 12   ⟺   Div(1) ⊊ Div(2) ⊊ Div(4) ⊊ Div(12)</text>')
    out.append(f'  <text x="{lx + lw/2:.1f}" y="{by1 + 65:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">Type-level subtyping {escape_xml("{d | d ∣ g} ⊆ {d | d ∣ a}")} IS value-level g ∣ a.</text>')
    out.append(f'  <text x="{lx + lw/2:.1f}" y="{by1 + 81:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">Greatest subtype inside Div(a) and Div(b) = intersection Div(a) ∩ Div(b).</text>')

    # Right half: Why Div(0) = ℕ and Gcd(12, 0) = {12}
    rx, ry, rw, rh = 458.0, 82.0, 416.0, 505.0
    out.append(f'  <!-- Right Panel: Zero as Top Element of the Divisibility Lattice -->')
    out.append(f'  <rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="{rh:.1f}" rx="8" fill="#ffffff" stroke="{GRAY_FAINT}" stroke-width="1.6"/>')
    out.append(f'  <rect x="{rx:.1f}" y="{ry:.1f}" width="{rw:.1f}" height="48" rx="8" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.4"/>')
    out.append(f'  <text x="{rx + 14:.1f}" y="{ry + 21:.1f}" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{PURPLE}">2. Edge Case b = 0: Why Gcd(12, 0) = {{12}}</text>')
    out.append(f'  <text x="{rx + 14:.1f}" y="{ry + 40:.1f}" font-family="{FONT_SANS}" font-size="12" fill="{INK_MUTED}">Since d · 0 = 0 for every d ∈ ℕ, every number divides 0:  Div(0) = ℕ</text>')

    # Draw outer universal box representing Div(0) = ℕ
    ubx, uby, ubw, ubh = rx + 18.0, ry + 62.0, rw - 36.0, 328.0
    out.append(f'  <rect x="{ubx:.1f}" y="{uby:.1f}" width="{ubw:.1f}" height="{ubh:.1f}" rx="14" fill="{GRAY_BOX}" stroke="{INK_MUTED}" stroke-width="2.0" stroke-dasharray="6,4"/>')
    out.append(f'  <text x="{ubx + 14:.1f}" y="{uby + 21:.1f}" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">Universal Down-Set Div(0) = ℕ (all natural numbers)</text>')

    # Node 0 at the absolute top of the lattice
    z_x, z_y = rx + 206.0, uby + 52.0
    out.append(f'  <circle cx="{z_x:.1f}" cy="{z_y:.1f}" r="19" fill="#ffffff" stroke="{INK}" stroke-width="2.6"/>')
    out.append(f'  <text x="{z_x:.1f}" y="{z_y + 5:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="15" font-weight="bold" fill="{INK}">0</text>')
    out.append(f'  <rect x="{z_x + 25:.1f}" y="{z_y - 10:.1f}" width="132" height="20" rx="4" fill="{INK}"/>')
    out.append(f'  <text x="{z_x + 91:.1f}" y="{z_y + 4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="#ffffff">b = 0 (Top of ℕ, ∣)</text>')
    out.append(f'  <text x="{ubx + 14:.1f}" y="{z_y + 4:.1f}" font-family="{FONT_SANS}" font-size="11" font-style="italic" fill="{INK_MUTED}">∀n ∈ ℕ, n ∣ 0 (n·0 = 0)</text>')

    # Position Div(12) inside Div(0)
    orig_x2, orig_y2 = rx + 206.0, uby + 286.0
    vx2_2 = (-60.0, -58.0)
    vx3_2 = (80.0, -58.0)
    pos2 = {n: grid_2_3_pos(n, orig_x2, orig_y2, vx2_2, vx3_2) for n in nodes_12}

    # Hull of Div(12) = Div(12) ∩ Div(0)
    p2_div12 = expand_polygon([pos2[n] for n in nodes_12], 29.0)
    out.append(f'  <path d="{p2_div12}" fill="{PURPLE_FILL}" fill-opacity="0.72" stroke="{PURPLE}" stroke-width="2.5"/>')

    # Dotted divisibility rays from finite lattice up to 0
    for top_n in (4, 12, 6):
        tx, ty = pos2[top_n]
        out.append(f'  <line x1="{tx:.1f}" y1="{ty - 16:.1f}" x2="{z_x + (tx - z_x)*0.22:.1f}" y2="{z_y + 21:.1f}" stroke="{INK_MUTED}" stroke-width="1.4" stroke-dasharray="4,4" marker-end="url(#arrow-ink)"/>')

    # Edges of Div(12)
    for u, v, p in edges_12:
        x1, y1 = pos2[u]
        x2, y2 = pos2[v]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        sx, sy = x1 + dx / dist * 15.0, y1 + dy / dist * 15.0
        ex, ey = x2 - dx / dist * 15.0, y2 - dy / dist * 15.0
        out.append(f'  <line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{PURPLE}" stroke-width="2.2" marker-end="url(#arrow-purple)"/>')

    # Nodes of Div(12)
    for n in nodes_12:
        x, y = pos2[n]
        if n == 12:
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="18.5" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="3.0"/>')
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="#ffffff" stroke="{PURPLE}" stroke-width="1.8"/>')
            out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">12</text>')
            out.append(f'  <rect x="{x + 23:.1f}" y="{y - 10:.1f}" width="128" height="20" rx="4" fill="{PURPLE}"/>')
            out.append(f'  <text x="{x + 87:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="bold" fill="#ffffff">a = 12 = 12 ∧ 0 (TOP)</text>')
        else:
            out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="#ffffff" stroke="{PURPLE}" stroke-width="1.6"/>')
            out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" fill="{INK}">{n}</text>')

    # Explanation box at bottom of right panel
    by2 = ry + 402.0
    out.append(f'  <rect x="{rx + 14:.1f}" y="{by2:.1f}" width="{rw - 28:.1f}" height="88" rx="6" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.3"/>')
    out.append(f'  <text x="{rx + rw/2:.1f}" y="{by2 + 22:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13.5" font-weight="bold" fill="{PURPLE}">Div(12) ∩ Div(0)  =  Div(12) ∩ ℕ  =  Div(12)</text>')
    out.append(f'  <text x="{rx + rw/2:.1f}" y="{by2 + 44:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" fill="{INK}">Intersecting with the whole universe ℕ leaves Div(12) unchanged!</text>')
    out.append(f'  <text x="{rx + rw/2:.1f}" y="{by2 + 64:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{NAVY}">• When y = 0 in Euclid’s algorithm, x = 12 ALREADY inhabits Gcd(12, 0).</text>')
    out.append(f'  <text x="{rx + rw/2:.1f}" y="{by2 + 81:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">• Even Gcd(0, 0) works: Div(0) ∩ Div(0) = ℕ = Div(0), with top element 0.</text>')

    out.append(f'  <text x="450" y="608" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" fill="{INK_MUTED}">Defining Gcd via Down-Set Equality Div(g) = Div(a) ∩ Div(b) handles 0 effortlessly without ad-hoc "greatest" exceptions.</text>')

    out.extend(svg_footer())
    with open("fig-4.svg", "w") as f:
        f.write("\n".join(out))


# ============================================================================
# FIGURE 5: Euclid's Algorithm (12, 8) → (8, 4) → (4, 0) as Cone Contraction
# ============================================================================
def generate_fig_5() -> None:
    width, height = 900, 660
    out = svg_header(width, height)

    draw_title_banner(
        out,
        title="Euclid's Algorithm Slides the Outer Cones Down to Their Invariant Meet",
        subtitle="Each step (x, y) ↦ (y, x mod y) shrinks the upper cones while preserving Div(x) ∩ Div(y) = {1, 2, 4}, until y = 0 exposes x = 4 as the top.",
        fig_num="FIG 5 · EUCLID'S INVARIANT TRACE",
        width=width,
    )

    # Top invariant equation banner
    out.append(f'  <rect x="23" y="74" width="854" height="36" rx="6" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.5"/>')
    out.append(f'  <text x="450" y="97" text-anchor="middle" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">Loop Invariant:   Gcd(12, 8)  =  Gcd(8, 4)  =  Gcd(4, 0)  =  {{4}}     because   Div(x) ∩ Div(y) = Div(y) ∩ Div(x mod y) = {{1, 2, 4}}</text>')

    nodes = [1, 2, 3, 4, 6, 8, 12]
    edges = hasse_edges(nodes)

    steps = [
        {
            "step_title": "Step 0: Entry (x = 12, y = 8)",
            "code": "euclid(12, 8)  →  y ≠ 0",
            "x": 12,
            "y": 8,
            "div_x": set(divisors(12)),
            "div_y": set(divisors(8)),
            "common": {1, 2, 4},
            "type_eq": "Target Type: Gcd(12, 8)",
            "explain1": "Two distinct cones Div(12) and Div(8)",
            "explain2": "overlap on {1, 2, 4}, hidden below 12 & 8.",
        },
        {
            "step_title": "Step 1: Modulo (x = 8, y = 4)",
            "code": "12 mod 8 = 4  →  euclid(8, 4)",
            "x": 8,
            "y": 4,
            "div_x": set(divisors(8)),
            "div_y": set(divisors(4)),
            "common": {1, 2, 4},
            "type_eq": "Gcd(8, 4) = Gcd(12, 8)",
            "explain1": "×3 branch {3, 6, 12} is shed; y = 4 now",
            "explain2": "lands directly on the purple meet {1, 2, 4}!",
        },
        {
            "step_title": "Step 2: Base Case (x = 4, y = 0)",
            "code": "8 mod 4 = 0  →  return x = 4",
            "x": 4,
            "y": 0,
            "div_x": set(divisors(4)),
            "div_y": set(nodes),
            "common": {1, 2, 4},
            "type_eq": "x = 4 : Gcd(4, 0) = Gcd(12, 8) ✓",
            "explain1": "Since Div(0) = ℕ, Div(4) ∩ Div(0) = Div(4).",
            "explain2": "Cone of x = 4 IS the intersection — Q.E.D.",
        },
    ]

    panel_w = 266.0
    panel_h = 468.0
    gap = 26.0
    start_x = 23.0
    panel_y = 122.0

    for idx, st in enumerate(steps):
        px = start_x + idx * (panel_w + gap)
        py = panel_y
        xv, yv = st["x"], st["y"]
        div_x = st["div_x"]
        div_y = st["div_y"]
        common = st["common"]

        out.append(f'  <!-- Step Panel {idx}: ({xv}, {yv}) -->')
        out.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="{panel_h:.1f}" rx="8" fill="#ffffff" stroke="{GRAY_FAINT}" stroke-width="1.6"/>')

        # Step Header
        hdr_fill = PURPLE_FILL if idx == 2 else GRAY_BOX
        hdr_stroke = PURPLE if idx == 2 else GRAY_FAINT
        out.append(f'  <rect x="{px:.1f}" y="{py:.1f}" width="{panel_w:.1f}" height="50" rx="8" fill="{hdr_fill}" stroke="{hdr_stroke}" stroke-width="1.5"/>')
        out.append(f'  <text x="{px + 12:.1f}" y="{py + 21:.1f}" font-family="{FONT_SERIF}" font-size="14" font-weight="bold" fill="{INK}">{escape_xml(st["step_title"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{py + 40:.1f}" font-family="{FONT_SANS}" font-size="12" font-weight="bold" fill="{NAVY}">{escape_xml(st["code"])}</text>')

        # Lattice coordinates inside panel (shifted right slightly so 8 and 4 have room on left)
        orig_x = px + 150.0
        orig_y = py + 332.0
        vx2 = (-38.0, -58.0)
        vx3 = (58.0, -58.0)
        pos = {n: grid_2_3_pos(n, orig_x, orig_y, vx2, vx3) for n in nodes}

        # If step 2 (y = 0), draw universal box Div(0) = ℕ around the lattice
        if yv == 0:
            out.append(f'  <rect x="{px + 14:.1f}" y="{py + 62:.1f}" width="{panel_w - 28:.1f}" height="296" rx="10" fill="{GRAY_BOX}" fill-opacity="0.55" stroke="{INK_MUTED}" stroke-width="1.6" stroke-dasharray="5,3"/>')
            out.append(f'  <text x="{px + 24:.1f}" y="{py + 80:.1f}" font-family="{FONT_SANS}" font-size="11.5" font-weight="bold" fill="{INK_MUTED}">Div(y = 0) = ℕ (entire space)</text>')
            z_x, z_y = px + panel_w - 46.0, py + 92.0
            out.append(f'  <circle cx="{z_x:.1f}" cy="{z_y:.1f}" r="14" fill="#ffffff" stroke="{INK}" stroke-width="2.0"/>')
            out.append(f'  <text x="{z_x:.1f}" y="{z_y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{INK}">0</text>')
            out.append(f'  <rect x="{z_x - 54:.1f}" y="{z_y - 8:.1f}" width="36" height="16" rx="3" fill="{INK}"/>')
            out.append(f'  <text x="{z_x - 36:.1f}" y="{z_y + 4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="#ffffff">y=0</text>')
        else:
            path_x = expand_polygon([pos[n] for n in div_x], 24.0)
            path_y = expand_polygon([pos[n] for n in div_y], 21.5)
            out.append(f'  <path d="{path_x}" fill="{NAVY_FILL}" fill-opacity="0.45" stroke="{NAVY}" stroke-width="1.6" stroke-dasharray="5,3"/>')
            out.append(f'  <path d="{path_y}" fill="{GRAY_BOX}" fill-opacity="0.60" stroke="{INK_MUTED}" stroke-width="1.6" stroke-dasharray="3,3"/>')

        # Invariant purple intersection hull Div(x) ∩ Div(y) = {1, 2, 4}
        path_c = expand_polygon([pos[n] for n in common], 18.0)
        out.append(f'  <path d="{path_c}" fill="{PURPLE_FILL}" fill-opacity="0.80" stroke="{PURPLE}" stroke-width="2.4"/>')

        # Edges
        for u, v, p in edges:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            sx, sy = x1 + dx / dist * 13.5, y1 + dy / dist * 13.5
            ex, ey = x2 - dx / dist * 13.5, y2 - dy / dist * 13.5
            in_c = (u in common) and (v in common)
            active = (u in div_x and v in div_x) or (yv != 0 and u in div_y and v in div_y)
            col = PURPLE if in_c else (INK_MUTED if active else GRAY_FAINT)
            sw = "2.2" if in_c else ("1.4" if active else "1.0")
            out.append(f'  <line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" stroke-width="{sw}"/>')

        # Nodes
        for n in nodes:
            x, y = pos[n]
            if n == 4:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="16.5" fill="{PURPLE_FILL}" stroke="{PURPLE}" stroke-width="2.8"/>')
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="12.5" fill="#ffffff" stroke="{PURPLE}" stroke-width="1.5"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{PURPLE}">4</text>')
                if idx == 1:
                    out.append(f'  <rect x="{x - 56:.1f}" y="{y - 8:.1f}" width="36" height="16" rx="3" fill="{INK}"/>')
                    out.append(f'  <text x="{x - 38:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="#ffffff">y=4</text>')
                elif idx == 2:
                    out.append(f'  <rect x="{x - 62:.1f}" y="{y - 8:.1f}" width="42" height="16" rx="3" fill="{PURPLE}"/>')
                    out.append(f'  <text x="{x - 41:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="#ffffff">x=4 ✓</text>')
            elif n == xv:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="14.5" fill="#ffffff" stroke="{NAVY}" stroke-width="2.4"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{NAVY}">{n}</text>')
                out.append(f'  <rect x="{x - 18:.1f}" y="{y - 33:.1f}" width="36" height="15" rx="3" fill="{NAVY}"/>')
                out.append(f'  <text x="{x:.1f}" y="{y - 22:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="#ffffff">x={n}</text>')
            elif n == yv:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="14.5" fill="#ffffff" stroke="{INK}" stroke-width="2.4"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12.5" font-weight="bold" fill="{INK}">{n}</text>')
                out.append(f'  <rect x="{x - 18:.1f}" y="{y - 33:.1f}" width="36" height="15" rx="3" fill="{INK}"/>')
                out.append(f'  <text x="{x:.1f}" y="{y - 22:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10.5" font-weight="bold" fill="#ffffff">y={n}</text>')
            elif n in common:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.6"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" fill="{INK}">{n}</text>')
            else:
                out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{BG_IVORY}" stroke="{GRAY_FAINT}" stroke-width="1.1"/>')
                out.append(f'  <text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="11" fill="{INK_LIGHT}">{n}</text>')

        # Transition arrows between panels
        if idx < 2:
            ax1 = px + panel_w + 3
            ax2 = px + panel_w + gap - 5
            ay = py + 210
            out.append(f'  <line x1="{ax1:.1f}" y1="{ay:.1f}" x2="{ax2:.1f}" y2="{ay:.1f}" stroke="{PURPLE}" stroke-width="2.4" marker-end="url(#arrow-purple)"/>')

        # Bottom explanation card inside panel
        by = py + 366.0
        out.append(f'  <line x1="{px + 12:.1f}" y1="{by:.1f}" x2="{px + panel_w - 12:.1f}" y2="{by:.1f}" stroke="{GRAY_FAINT}" stroke-width="1.2"/>')
        out.append(f'  <rect x="{px + 12:.1f}" y="{by + 10:.1f}" width="{panel_w - 24:.1f}" height="28" rx="5" fill="{PURPLE_LIGHT}" stroke="{PURPLE}" stroke-width="1.2"/>')
        out.append(f'  <text x="{px + panel_w/2:.1f}" y="{by + 28:.1f}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="12" font-weight="bold" fill="{PURPLE}">{escape_xml(st["type_eq"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{by + 58:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK}">{escape_xml(st["explain1"])}</text>')
        out.append(f'  <text x="{px + 12:.1f}" y="{by + 76:.1f}" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">{escape_xml(st["explain2"])}</text>')

    # Bottom Proof-Erasure Takeaway Box
    out.append(f'  <rect x="23" y="604" width="854" height="40" rx="6" fill="{GRAY_BOX}" stroke="{PURPLE}" stroke-width="1.3"/>')
    out.append(f'  <text x="450" y="622" text-anchor="middle" font-family="{FONT_SERIF}" font-size="13" font-weight="bold" fill="{INK}">Refinement Type Takeaway: The purple cone {{1, 2, 4}} is the compile-time proof certificate; the navy numbers (12,8) → (8,4) → (4,0) are the runtime values.</text>')
    out.append(f'  <text x="450" y="638" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" fill="{INK_MUTED}">At runtime all cones are erased, leaving only integer modulo steps—guaranteed to halt at the unique top element 4.</text>')

    out.extend(svg_footer())
    with open("fig-5.svg", "w") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    generate_fig_1()
    generate_fig_2()
    generate_fig_3()
    generate_fig_4()
    generate_fig_5()
    print("Generated fig-1.svg through fig-5.svg successfully.")
