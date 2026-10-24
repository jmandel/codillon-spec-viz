#!/usr/bin/env python3
"""
Generator for Divisor Strips on a Number Line visualizations of Gcd(a, b) as a refinement type.
Produces fig-1.svg through fig-5.svg.
"""

import html

# Palette (strictly following instructions, NO GREEN anywhere)
BG = "#fffff0"          # ivory
INK = "#222222"         # primary ink
PURPLE = "#6A5ACD"      # type / region / target socket
PURPLE_FILL = "#d9d5f2" # muted purple fill
PURPLE_LIGHT = "#efedfa"# subtle purple tint
RED = "#8b0000"         # violation / type error ONLY
RED_FILL = "#f9e6e6"    # soft background for error callouts
INDIGO = "#4b0082"      # unknown
NAVY = "#00008b"        # concrete value / run / dot
NAVY_LIGHT = "#e6eaf5"  # light navy tint
GRAY_DARK = "#555555"
GRAY_MID = "#888888"
GRAY_LIGHT = "#cccccc"
GRAY_FAINT = "#e8e8dc"

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'Arial Narrow', Arial, sans-serif"


def divisors(n, max_d):
    """Return set of divisors d in 0..max_d such that d | n.
    In N, d | n iff exists k in N such that n = d * k.
    For n = 0: every d in 0..max_d divides 0 (since 0 = d * 0).
    For n > 0: d = 0 does NOT divide n; d > 0 divides n iff n % d == 0.
    """
    res = set()
    for d in range(0, max_d + 1):
        if n == 0:
            res.add(d)
        else:
            if d > 0 and n % d == 0:
                res.add(d)
    return res


def esc(s):
    return html.escape(str(s), quote=True)


class SVGCanvas:
    def __init__(self, width=900, height=560):
        self.width = width
        self.height = height
        self.elements = []
        self.defs = []

    def add_def(self, d):
        self.defs.append(d)

    def add(self, el):
        self.elements.append(el)

    def rect(self, x, y, w, h, fill="none", stroke="none", stroke_width=1, rx=0, dash=None, opacity=1.0):
        attrs = f'x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"'
        if stroke != "none":
            attrs += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        if rx > 0:
            attrs += f' rx="{rx}" ry="{rx}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f"<rect {attrs}/>")

    def line(self, x1, y1, x2, y2, stroke=INK, stroke_width=1, dash=None, marker_end=None, opacity=1.0):
        attrs = f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{stroke_width}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if marker_end:
            attrs += f' marker-end="url(#{marker_end})"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f"<line {attrs}/>")

    def circle(self, cx, cy, r, fill="none", stroke="none", stroke_width=1.5, dash=None, opacity=1.0):
        attrs = f'cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"'
        if stroke != "none":
            attrs += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f"<circle {attrs}/>")

    def path(self, d, fill="none", stroke=INK, stroke_width=1.5, dash=None, marker_end=None, opacity=1.0):
        attrs = f'd="{d}" fill="{fill}"'
        if stroke != "none":
            attrs += f' stroke="{stroke}" stroke-width="{stroke_width}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if marker_end:
            attrs += f' marker-end="url(#{marker_end})"'
        if opacity < 1.0:
            attrs += f' opacity="{opacity}"'
        self.add(f"<path {attrs}/>")

    def text(self, x, y, content, font=FONT_SERIF, size=14, fill=INK, anchor="start", weight="normal", style="normal", raw=False):
        body = content if raw else esc(content)
        attrs = (
            f'x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}"'
        )
        self.add(f"<text {attrs}>{body}</text>")

    def add_standard_markers(self):
        self.add_def(f'''
        <marker id="arrow-ink" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 9 5 L 0 9 z" fill="{INK}"/>
        </marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 9 5 L 0 9 z" fill="{PURPLE}"/>
        </marker>
        <marker id="arrow-navy" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 9 5 L 0 9 z" fill="{NAVY}"/>
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 9 5 L 0 9 z" fill="{RED}"/>
        </marker>
        <marker id="arrow-gray" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 9 5 L 0 9 z" fill="{GRAY_DARK}"/>
        </marker>
        ''')

    def render(self):
        out = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}">',
        ]
        if self.defs:
            out.append("<defs>" + "\n".join(self.defs) + "</defs>")
        out.append(f'<rect x="0" y="0" width="{self.width}" height="{self.height}" fill="{BG}"/>')
        out.extend(self.elements)
        out.append("</svg>")
        return "\n".join(out)


def draw_header(svg, title, subtitle_raw):
    svg.text(32, 34, title, font=FONT_SERIF, size=20, fill=INK, weight="bold")
    svg.text(32, 55, subtitle_raw, font=FONT_SERIF, size=13.5, fill=GRAY_DARK, raw=True)
    svg.line(32, 66, svg.width - 32, 66, stroke=GRAY_LIGHT, stroke_width=1)


def draw_strip_row(
    svg,
    y,
    x0,
    dx,
    max_n,
    label_main,
    label_sub,
    active_set=None,
    socket_set=None,
    mode="input",
    show_infinity=False,
    infinity_active=False,
    infinity_socket=False,
    row_bg=None,
    badge_text=None,
    badge_color=INK,
    badge_bg="none",
    badge_x=688,
):
    """
    Draw a single divisor strip row along d = 0 .. max_n.
    """
    left_box = 28
    right_end = badge_x - 10
    if row_bg:
        svg.rect(left_box, y - 21, right_end - left_box, 42, fill=row_bg, stroke=PURPLE if mode == "socket" else "none",
                 stroke_width=1.2 if mode == "socket" else 0, rx=6)

    # Row labels on left
    svg.text(40, y - 2 if label_sub else y + 5, label_main, font=FONT_SERIF, size=14, fill=INK, raw=True)
    if label_sub:
        svg.text(40, y + 14, label_sub, font=FONT_SANS, size=11.5, fill=GRAY_DARK, raw=True)

    # Track baseline
    line_end = x0 + max_n * dx + (26 if show_infinity else 12)
    svg.line(x0, y, line_end, y, stroke=GRAY_LIGHT, stroke_width=1.2,
             marker_end="arrow-gray" if show_infinity else None)

    active_set = active_set or set()
    socket_set = socket_set or set()

    for d in range(0, max_n + 1):
        cx = x0 + d * dx
        svg.line(cx, y - 4, cx, y + 4, stroke=GRAY_LIGHT, stroke_width=1)

        if mode == "input":
            if d in active_set:
                svg.circle(cx, y, 6.5, fill=NAVY, stroke=BG, stroke_width=1.2)
            else:
                svg.circle(cx, y, 2.0, fill=GRAY_LIGHT)

        elif mode == "socket":
            if d in socket_set:
                svg.circle(cx, y, 9.5, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2)
                svg.circle(cx, y, 2.5, fill=PURPLE)
            else:
                svg.circle(cx, y, 2.0, fill=GRAY_LIGHT)

        elif mode == "test":
            in_sock = d in socket_set
            in_act = d in active_set
            if in_sock and in_act:
                svg.circle(cx, y, 10.0, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2)
                svg.circle(cx, y, 6.0, fill=NAVY)
            elif in_sock and not in_act:
                svg.circle(cx, y, 10.5, fill=RED_FILL, stroke=RED, stroke_width=2.3, dash="3,2")
                svg.text(cx, y + 4, "?", font=FONT_SANS, size=11, fill=RED, anchor="middle", weight="bold")
            elif in_act and not in_sock:
                svg.circle(cx, y, 10.5, fill=RED_FILL, stroke=RED, stroke_width=1.5)
                svg.circle(cx, y, 6.0, fill=RED)
                svg.line(cx - 8.5, y - 8.5, cx + 8.5, y + 8.5, stroke=RED, stroke_width=1.8)
                svg.line(cx - 8.5, y + 8.5, cx + 8.5, y - 8.5, stroke=RED, stroke_width=1.8)
            else:
                svg.circle(cx, y, 2.0, fill=GRAY_LIGHT)

    if show_infinity:
        cx_inf = line_end + 8
        if mode == "input" and infinity_active:
            svg.text(cx_inf, y + 4, "⋯ ∀d ∈ ℕ", font=FONT_SERIF, size=12, fill=NAVY, weight="bold")
        elif mode == "socket" and infinity_socket:
            svg.text(cx_inf, y + 4, "⋯ ∀d ∈ ℕ", font=FONT_SERIF, size=12, fill=PURPLE, weight="bold")
        elif mode == "test":
            if infinity_socket and infinity_active:
                svg.text(cx_inf, y + 4, "⋯ ∀d ∈ ℕ", font=FONT_SERIF, size=12, fill=NAVY, weight="bold")
            elif infinity_socket and not infinity_active:
                svg.text(cx_inf, y + 4, "⋯ ∞ empty", font=FONT_SANS, size=11.5, fill=RED, weight="bold")
            elif not infinity_socket and infinity_active:
                svg.text(cx_inf, y + 4, "⋯ ∞ spill", font=FONT_SANS, size=11.5, fill=RED, weight="bold")
            else:
                svg.text(cx_inf, y + 4, "⋯", font=FONT_SERIF, size=13, fill=GRAY_MID)

    if badge_text:
        bw = svg.width - 28 - badge_x
        if badge_bg != "none":
            svg.rect(badge_x, y - 15, bw, 30, fill=badge_bg, stroke=badge_color, stroke_width=1.3, rx=5)
        svg.text(badge_x + bw / 2, y + 4.5, badge_text, font=FONT_SANS, size=12, fill=badge_color, anchor="middle", weight="bold", raw=True)


# ==============================================================================
# FIGURE 1: Canonical example a = 12, b = 8 -> gcd = 4
# ==============================================================================
def make_fig_1():
    svg = SVGCanvas(width=900, height=565)
    svg.add_standard_markers()

    draw_header(
        svg,
        "Gcd(12, 8) Is the Unique Number Whose Divisor Strip Matches CD(12, 8)",
        'Refinement type: <tspan font-style="italic">Gcd</tspan>(12, 8) = { <tspan font-style="italic">g</tspan> ∈ ℕ │ <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>) = <tspan font-style="italic">Div</tspan>(12) ∩ <tspan font-style="italic">Div</tspan>(8) }',
    )

    x0 = 225
    dx = 36
    max_n = 12
    badge_x = 684

    div12 = divisors(12, max_n)
    div8 = divisors(8, max_n)
    cd = div12 & div8
    div4 = divisors(4, max_n)

    # Top column header: divisor ruler d
    y_ruler = 95
    svg.text(40, y_ruler + 4, "Divisor axis  d ∈ ℕ", font=FONT_SANS, size=12, fill=GRAY_DARK, weight="bold")
    for d in range(0, max_n + 1):
        cx = x0 + d * dx
        is_cd = d in cd
        svg.text(
            cx,
            y_ruler + 4,
            str(d),
            font=FONT_SERIF,
            size=13.5 if is_cd else 12,
            fill=PURPLE if is_cd else GRAY_DARK,
            anchor="middle",
            weight="bold" if is_cd else "normal",
        )
        if is_cd:
            svg.line(cx, y_ruler + 12, cx, 336, stroke=PURPLE_FILL, stroke_width=6)
        svg.line(cx, y_ruler + 12, cx, 336, stroke=GRAY_FAINT, stroke_width=1, dash="2,2")

    y_12 = 135
    y_8 = 185
    y_cd = 248
    y_g4 = 320

    draw_strip_row(
        svg,
        y_12,
        x0,
        dx,
        max_n,
        label_main='<tspan font-style="italic">Div</tspan>(12)',
        label_sub="d &gt; 0 dividing 12",
        active_set=div12,
        mode="input",
        badge_text="{1, 2, 3, 4, 6, 12}",
        badge_color=NAVY,
        badge_bg=NAVY_LIGHT,
        badge_x=badge_x,
    )

    draw_strip_row(
        svg,
        y_8,
        x0,
        dx,
        max_n,
        label_main='<tspan font-style="italic">Div</tspan>(8)',
        label_sub="d &gt; 0 dividing 8",
        active_set=div8,
        mode="input",
        badge_text="{1, 2, 4, 8}",
        badge_color=NAVY,
        badge_bg=NAVY_LIGHT,
        badge_x=badge_x,
    )

    for d in cd:
        cx = x0 + d * dx
        svg.line(cx, y_12 + 7, cx, y_cd - 11, stroke=PURPLE, stroke_width=1.6, dash="2,2")

    svg.text(130, 217, "∩  intersect columns", font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle", weight="bold")

    draw_strip_row(
        svg,
        y_cd,
        x0,
        dx,
        max_n,
        label_main='<tspan font-weight="bold" fill="#6A5ACD">CD(12, 8)</tspan> = <tspan font-style="italic">Div</tspan>(12) ∩ <tspan font-style="italic">Div</tspan>(8)',
        label_sub="Type requirement (purple sockets)",
        socket_set=cd,
        mode="socket",
        row_bg=PURPLE_LIGHT,
        badge_text="Target sockets: {1, 2, 4}",
        badge_color=PURPLE,
        badge_bg=PURPLE_FILL,
        badge_x=badge_x,
    )

    for d in cd:
        cx = x0 + d * dx
        svg.line(cx, y_cd + 11, cx, y_g4 - 12, stroke=PURPLE, stroke_width=1.5, marker_end="arrow-purple")

    svg.text(130, 288, "drop candidate into sockets", font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle")

    draw_strip_row(
        svg,
        y_g4,
        x0,
        dx,
        max_n,
        label_main='Candidate <tspan font-weight="bold" fill="#00008b">g = 4</tspan> : <tspan font-style="italic">Div</tspan>(4)',
        label_sub="Every socket filled; 0 spills",
        active_set=div4,
        socket_set=cd,
        mode="test",
        row_bg="#f6f5fc",
        badge_text="EXACT MATCH (4 : Gcd(12,8))",
        badge_color=PURPLE,
        badge_bg=PURPLE_FILL,
        badge_x=badge_x,
    )

    # Callout for socket anatomy under g=4
    cx_4 = x0 + 4 * dx
    svg.path(f"M {cx_4} {y_g4 + 13} L {cx_4} {y_g4 + 34} L {cx_4 + 18} {y_g4 + 34}", stroke=PURPLE, stroke_width=1.2)
    svg.text(cx_4 + 22, y_g4 + 38, "Navy pin seated in purple socket (d | g  and  d ∈ CD)", font=FONT_SANS, size=11.5, fill=INK)

    # Bottom Section: The refinement type as a subset of N on a number line
    y_box = 382
    svg.rect(28, y_box, 844, 158, fill="#faf8ee", stroke=PURPLE, stroke_width=1.5, rx=8)
    svg.text(
        44,
        y_box + 25,
        'Resulting Refinement Type on the Value Line:   <tspan font-weight="bold" fill="#6A5ACD">Gcd(12, 8)</tspan> = { <tspan font-style="italic">g</tspan> ∈ ℕ │ <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>) = {1, 2, 4} } = <tspan font-weight="bold" fill="#6A5ACD">{ 4 }</tspan>',
        font=FONT_SERIF,
        size=14.5,
        fill=INK,
        raw=True,
    )
    svg.text(
        44,
        y_box + 44,
        "Out of all natural numbers g ∈ ℕ, only g = 4 has divisor strip {1, 2, 4}. The refinement carves out a singleton subset:",
        font=FONT_SANS,
        size=12,
        fill=GRAY_DARK,
    )

    y_nl = y_box + 102
    svg.text(44, y_nl + 5, "Value axis  g ∈ ℕ", font=FONT_SERIF, size=13.5, fill=INK, weight="bold")
    svg.line(x0, y_nl, x0 + max_n * dx + 35, y_nl, stroke=INK, stroke_width=1.8, marker_end="arrow-ink")

    for g in range(0, max_n + 1):
        cx = x0 + g * dx
        svg.line(cx, y_nl - 5, cx, y_nl + 5, stroke=INK, stroke_width=1.2)
        if g == 4:
            svg.rect(cx - 17, y_nl - 24, 34, 48, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2, rx=15)
            svg.circle(cx, y_nl, 7.5, fill=NAVY, stroke=BG, stroke_width=1.5)
            svg.text(cx, y_nl + 19, "4", font=FONT_SERIF, size=14, fill=NAVY, anchor="middle", weight="bold")
            svg.text(cx, y_nl - 31, "unique inhabitant", font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle", weight="bold")
        else:
            svg.circle(cx, y_nl, 3.0, fill=GRAY_LIGHT, stroke=GRAY_MID, stroke_width=1)
            svg.text(cx, y_nl + 19, str(g), font=FONT_SERIF, size=12, fill=GRAY_MID, anchor="middle")
            if g in (8, 12):
                lbl = "input b" if g == 8 else "input a"
                svg.text(cx, y_nl + 34, lbl, font=FONT_SANS, size=11, fill=GRAY_DARK, anchor="middle")

    # Connect EXACT MATCH badge on the right cleanly into the bottom refinement box
    svg.path(
        f"M {badge_x + 94} {y_g4 + 16} L {badge_x + 94} {y_box - 4}",
        stroke=PURPLE,
        stroke_width=1.8,
        dash="4,3",
        marker_end="arrow-purple",
    )

    return svg


# ==============================================================================
# FIGURE 2: Type Errors in Divisor-Strip Language (for a = 12, b = 8)
# ==============================================================================
def make_fig_2():
    svg = SVGCanvas(width=900, height=625)
    svg.add_standard_markers()

    draw_header(
        svg,
        "Type Errors Are Empty Sockets (Too Small) or Spilled Pins (Too Large)",
        'Testing candidate values <tspan font-style="italic">g</tspan> against the socket specification <tspan font-weight="bold" fill="#6A5ACD">CD(12, 8) = {1, 2, 4}</tspan>',
    )

    x0 = 225
    dx = 36
    max_n = 12
    badge_x = 684
    cd = divisors(12, max_n) & divisors(8, max_n)

    # Ruler at top
    y_ruler = 92
    svg.text(40, y_ruler + 4, "Divisor axis  d ∈ ℕ", font=FONT_SANS, size=12, fill=GRAY_DARK, weight="bold")
    for d in range(0, max_n + 1):
        cx = x0 + d * dx
        is_cd = d in cd
        svg.text(
            cx,
            y_ruler + 4,
            str(d),
            font=FONT_SERIF,
            size=13.5 if is_cd else 12,
            fill=PURPLE if is_cd else GRAY_DARK,
            anchor="middle",
            weight="bold" if is_cd else "normal",
        )
        if is_cd:
            svg.line(cx, y_ruler + 10, cx, 455, stroke=PURPLE_FILL, stroke_width=6)
        svg.line(cx, y_ruler + 10, cx, 455, stroke=GRAY_FAINT, stroke_width=1, dash="2,2")

    # Target socket strip at top
    y_cd = 132
    draw_strip_row(
        svg,
        y_cd,
        x0,
        dx,
        max_n,
        label_main='<tspan font-weight="bold" fill="#6A5ACD">Target CD(12, 8)</tspan>',
        label_sub="Required sockets {1, 2, 4}",
        socket_set=cd,
        mode="socket",
        row_bg=PURPLE_LIGHT,
        badge_text="SPECIFICATION: {1, 2, 4}",
        badge_color=PURPLE,
        badge_bg=PURPLE_FILL,
        badge_x=badge_x,
    )

    # Candidate 1: g = 2 (Too small / missing socket 4)
    y_g2 = 208
    draw_strip_row(
        svg,
        y_g2,
        x0,
        dx,
        max_n,
        label_main='Wrong <tspan font-weight="bold" fill="#8b0000">g = 2</tspan> : <tspan font-style="italic">Div</tspan>(2)',
        label_sub="Common divisor, not greatest",
        active_set=divisors(2, max_n),
        socket_set=cd,
        mode="test",
        row_bg="#fcf3f3",
        badge_text="ERROR: missing d = 4",
        badge_color=RED,
        badge_bg=RED_FILL,
        badge_x=badge_x,
    )
    cx4 = x0 + 4 * dx
    svg.text(cx4 + 20, y_g2 + 32, "↑ Empty socket: 4 ∈ CD(12,8) but 4 ∤ 2", font=FONT_SANS, size=11.5, fill=RED, anchor="middle", weight="bold")

    # Candidate 2: g = 8 (Too large / extra divisor 8 spills)
    y_g8 = 288
    draw_strip_row(
        svg,
        y_g8,
        x0,
        dx,
        max_n,
        label_main='Wrong <tspan font-weight="bold" fill="#8b0000">g = 8</tspan> : <tspan font-style="italic">Div</tspan>(8)',
        label_sub="Divides b = 8, fails g | 12",
        active_set=divisors(8, max_n),
        socket_set=cd,
        mode="test",
        row_bg="#fcf3f3",
        badge_text="ERROR: d = 8 spills",
        badge_color=RED,
        badge_bg=RED_FILL,
        badge_x=badge_x,
    )
    cx8 = x0 + 8 * dx
    svg.text(cx8, y_g8 + 32, "↑ Spilled divisor: 8 | 8 but 8 ∉ CD(12,8)", font=FONT_SANS, size=11.5, fill=RED, anchor="middle", weight="bold")

    # Candidate 3: g = 6 (Both errors simultaneously: misses 4, spills 3 and 6)
    y_g6 = 368
    draw_strip_row(
        svg,
        y_g6,
        x0,
        dx,
        max_n,
        label_main='Wrong <tspan font-weight="bold" fill="#8b0000">g = 6</tspan> : <tspan font-style="italic">Div</tspan>(6)',
        label_sub="Divides a = 12, fails g | 8",
        active_set=divisors(6, max_n),
        socket_set=cd,
        mode="test",
        row_bg="#fcf3f3",
        badge_text="ERROR: misses 4; spills 3, 6",
        badge_color=RED,
        badge_bg=RED_FILL,
        badge_x=badge_x,
    )
    cx3 = x0 + 3 * dx
    cx6 = x0 + 6 * dx
    svg.text((cx3 + cx6) / 2 + 12, y_g6 + 32, "↑ 3, 6 spill out  &amp;  socket 4 is empty", font=FONT_SANS, size=11.5, fill=RED, anchor="middle", weight="bold", raw=True)

    # Candidate 4: g = 4 (Exact fit)
    y_g4 = 442
    draw_strip_row(
        svg,
        y_g4,
        x0,
        dx,
        max_n,
        label_main='Valid <tspan font-weight="bold" fill="#00008b">g = 4</tspan> : <tspan font-style="italic">Div</tspan>(4)',
        label_sub="Div(4) = CD(12, 8)",
        active_set=divisors(4, max_n),
        socket_set=cd,
        mode="test",
        row_bg=PURPLE_LIGHT,
        badge_text="WELL-TYPED: 0 empty, 0 spills",
        badge_color=PURPLE,
        badge_bg=PURPLE_FILL,
        badge_x=badge_x,
    )

    # Bottom: Number line showing rejected candidates vs unique inhabitant
    y_box = 482
    svg.rect(28, y_box, 844, 124, fill="#faf8ee", stroke=PURPLE, stroke_width=1.4, rx=8)
    svg.text(
        44,
        y_box + 22,
        'Two Halves of the Refinement Predicate on the Value Line <tspan font-style="italic">g</tspan> ∈ ℕ:',
        font=FONT_SERIF,
        size=14,
        fill=INK,
        weight="bold",
        raw=True,
    )
    svg.text(
        44,
        y_box + 40,
        '• No spilled pins  (Div(g) ⊆ CD(a,b))  ⇔  g divides both a and b.      • No empty sockets  (CD(a,b) ⊆ Div(g))  ⇔  every common divisor divides g.',
        font=FONT_SANS,
        size=11.8,
        fill=GRAY_DARK,
    )

    y_nl = y_box + 82
    svg.text(44, y_nl + 5, "Candidate  g ∈ ℕ", font=FONT_SERIF, size=13, fill=INK, weight="bold")
    svg.line(x0, y_nl, x0 + max_n * dx + 30, y_nl, stroke=INK, stroke_width=1.8, marker_end="arrow-ink")

    rejected = {2: "missing 4", 6: "spills 3,6", 8: "spills 8"}
    for g in range(0, max_n + 1):
        cx = x0 + g * dx
        svg.line(cx, y_nl - 4, cx, y_nl + 4, stroke=INK, stroke_width=1)
        if g == 4:
            svg.rect(cx - 17, y_nl - 20, 34, 42, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2, rx=14)
            svg.circle(cx, y_nl, 7.0, fill=NAVY, stroke=BG, stroke_width=1.4)
            svg.text(cx, y_nl + 18, "4", font=FONT_SERIF, size=13.5, fill=NAVY, anchor="middle", weight="bold")
            svg.text(cx, y_nl - 25, "Gcd(12,8)", font=FONT_SANS, size=11, fill=PURPLE, anchor="middle", weight="bold")
        elif g in rejected:
            svg.circle(cx, y_nl, 7.0, fill=RED_FILL, stroke=RED, stroke_width=2)
            svg.line(cx - 5, y_nl - 5, cx + 5, y_nl + 5, stroke=RED, stroke_width=2)
            svg.line(cx - 5, y_nl + 5, cx + 5, y_nl - 5, stroke=RED, stroke_width=2)
            svg.text(cx, y_nl + 19, str(g), font=FONT_SERIF, size=13, fill=RED, anchor="middle", weight="bold")
            svg.text(cx, y_nl + 33, rejected[g], font=FONT_SANS, size=11, fill=RED, anchor="middle")
        else:
            svg.circle(cx, y_nl, 2.5, fill=GRAY_LIGHT, stroke=GRAY_MID, stroke_width=1)
            svg.text(cx, y_nl + 18, str(g), font=FONT_SERIF, size=12, fill=GRAY_MID, anchor="middle")

    return svg


# ==============================================================================
# FIGURE 3: Euclid's Algorithm Preserves the Common-Divisor Strip CD(x, y)
# ==============================================================================
def make_fig_3():
    svg = SVGCanvas(width=900, height=625)
    svg.add_standard_markers()

    draw_header(
        svg,
        "Euclid’s Steps Change the Pair (x, y) Without Changing the Strip CD(x, y)",
        'Loop invariant: <tspan font-style="italic">CD</tspan>(<tspan font-style="italic">x</tspan>, <tspan font-style="italic">y</tspan>) = <tspan font-style="italic">CD</tspan>(<tspan font-style="italic">y</tspan>, <tspan font-style="italic">x</tspan> mod <tspan font-style="italic">y</tspan>), and since <tspan font-style="italic">Div</tspan>(0) = ℕ, stopping at <tspan font-style="italic">y</tspan> = 0 forces <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">x</tspan>) = <tspan font-style="italic">CD</tspan>(<tspan font-style="italic">a</tspan>, <tspan font-style="italic">b</tspan>)',
    )

    x0 = 264
    dx = 36
    max_n = 12
    cd = divisors(12, max_n) & divisors(8, max_n)

    # Ruler at top
    y_ruler = 90
    svg.text(36, y_ruler + 4, "Divisor axis  d ∈ ℕ", font=FONT_SANS, size=12, fill=GRAY_DARK, weight="bold")
    for d in range(0, max_n + 1):
        cx = x0 + d * dx
        is_cd = d in cd
        svg.text(
            cx,
            y_ruler + 4,
            str(d),
            font=FONT_SERIF,
            size=13.5 if is_cd else 12,
            fill=PURPLE if is_cd else GRAY_DARK,
            anchor="middle",
            weight="bold" if is_cd else "normal",
        )
        if is_cd:
            svg.rect(cx - 9, y_ruler + 12, 18, 380, fill=PURPLE_FILL, stroke="none", opacity=0.65)
            svg.line(cx, y_ruler + 12, cx, 492, stroke=PURPLE, stroke_width=1.2, dash="3,3")
        else:
            svg.line(cx, y_ruler + 12, cx, 492, stroke=GRAY_FAINT, stroke_width=1, dash="2,2")

    def draw_state_block(y_top, step_title, x_val, y_val, note_right):
        svg.rect(28, y_top, 844, 112, fill="#fbfaf2", stroke=GRAY_LIGHT, stroke_width=1.2, rx=6)
        # Left state card (strictly for step name and (x, y) pair)
        svg.rect(36, y_top + 12, 134, 88, fill=PURPLE_LIGHT if y_val == 0 else "#f2f2e6", stroke=PURPLE if y_val == 0 else GRAY_LIGHT, stroke_width=1.2, rx=5)
        svg.text(103, y_top + 42, step_title, font=FONT_SANS, size=12, fill=PURPLE if y_val == 0 else GRAY_DARK, anchor="middle", weight="bold")
        svg.text(103, y_top + 68, f"(x, y) = ({x_val}, {y_val})", font=FONT_SERIF, size=15, fill=NAVY, anchor="middle", weight="bold")

        y1 = y_top + 26
        y2 = y_top + 56
        y3 = y_top + 88

        # Strip labels in dedicated column x = 180..252
        svg.text(180, y1 + 4, f"Div({x_val})", font=FONT_SERIF, size=12.5, fill=NAVY)
        svg.text(180, y2 + 4, f"Div({y_val})" + (" = ℕ" if y_val == 0 else ""), font=FONT_SERIF, size=12.5, fill=NAVY, weight="bold" if y_val == 0 else "normal")
        svg.text(180, y3 + 4, f"CD({x_val}, {y_val})", font=FONT_SERIF, size=12.5, fill=PURPLE, weight="bold")

        div_x = divisors(x_val, max_n)
        div_y = divisors(y_val, max_n)
        cd_xy = div_x & div_y

        # Row 1: Div(x)
        svg.line(x0, y1, x0 + max_n * dx + 16, y1, stroke=GRAY_LIGHT, stroke_width=1)
        for d in range(0, max_n + 1):
            cx = x0 + d * dx
            if d in div_x:
                svg.circle(cx, y1, 5.5, fill=NAVY)
            else:
                svg.circle(cx, y1, 1.8, fill=GRAY_LIGHT)

        # Row 2: Div(y) (with honest Div(0) = all of N!)
        svg.line(x0, y2, x0 + max_n * dx + (28 if y_val == 0 else 16), y2, stroke=NAVY if y_val == 0 else GRAY_LIGHT, stroke_width=1.2,
                 marker_end="arrow-navy" if y_val == 0 else None)
        for d in range(0, max_n + 1):
            cx = x0 + d * dx
            if d in div_y:
                svg.circle(cx, y2, 5.5, fill=NAVY)
            else:
                svg.circle(cx, y2, 1.8, fill=GRAY_LIGHT)
        if y_val == 0:
            svg.text(x0 + max_n * dx + 36, y2 + 4, "⋯ ∀d ∈ ℕ", font=FONT_SERIF, size=12, fill=NAVY, weight="bold")

        # Row 3: CD(x,y)
        svg.line(x0, y3, x0 + max_n * dx + 16, y3, stroke=PURPLE, stroke_width=1.2)
        for d in range(0, max_n + 1):
            cx = x0 + d * dx
            if d in cd_xy:
                svg.circle(cx, y3, 8.5, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2)
                svg.circle(cx, y3, 4.5, fill=NAVY if y_val == 0 else PURPLE)
            else:
                svg.circle(cx, y3, 1.8, fill=GRAY_LIGHT)

        # Right annotation column
        bx = x0 + max_n * dx + 36
        if y_val != 0:
            svg.text(bx, y1 + 6, note_right[0], font=FONT_SANS, size=12, fill=GRAY_DARK, raw=True)
            svg.text(bx, y3 + 4, note_right[1], font=FONT_SANS, size=12, fill=PURPLE, weight="bold", raw=True)
        else:
            svg.text(bx, y1 + 4, note_right[0], font=FONT_SANS, size=12, fill=NAVY, weight="bold", raw=True)
            svg.text(bx, y3 + 4, note_right[1], font=FONT_SANS, size=12, fill=PURPLE, weight="bold", raw=True)

    draw_state_block(
        108,
        "INITIAL INPUTS",
        12,
        8,
        ["12 mod 8 = 4", "CD(12, 8) = {1, 2, 4}"],
    )

    svg.text(103, 235, "↓  step: (12, 8) ↦ (8, 4)", font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle", weight="bold")

    draw_state_block(
        244,
        "AFTER STEP 1",
        8,
        4,
        ["8 mod 4 = 0", "CD(8, 4) = {1, 2, 4}"],
    )

    svg.text(103, 371, "↓  step: (8, 4) ↦ (4, 0)", font=FONT_SANS, size=11.5, fill=PURPLE, anchor="middle", weight="bold")

    draw_state_block(
        380,
        "BASE CASE (y = 0)",
        4,
        0,
        ["Div(4) ∩ ℕ = Div(4)", "Div(4) = CD(12, 8) ✓"],
    )

    # Bottom summary + number line
    y_box = 504
    svg.rect(28, y_box, 844, 102, fill="#faf8ee", stroke=PURPLE, stroke_width=1.5, rx=8)
    svg.text(
        44,
        y_box + 23,
        'Why <tspan font-style="italic">y</tspan> = 0 Proves <tspan font-style="italic">x</tspan> : <tspan font-weight="bold" fill="#6A5ACD">Gcd(12, 8)</tspan>:   Because <tspan font-style="italic">Div</tspan>(0) = ℕ (every <tspan font-style="italic">d</tspan> divides 0 = <tspan font-style="italic">d</tspan>·0), intersecting with <tspan font-style="italic">Div</tspan>(0) changes nothing!',
        font=FONT_SERIF,
        size=13.8,
        fill=INK,
        raw=True,
    )
    svg.text(
        44,
        y_box + 42,
        "Chain of equal strips:   CD(12, 8)  =  CD(8, 4)  =  CD(4, 0)  =  Div(4) ∩ ℕ  =  Div(4).   Therefore x = 4 inhabits Gcd(12, 8).",
        font=FONT_SANS,
        size=12,
        fill=PURPLE,
        weight="bold",
    )

    y_nl = y_box + 74
    svg.text(44, y_nl + 5, "Return value  x ∈ ℕ", font=FONT_SERIF, size=13, fill=INK, weight="bold")
    svg.line(x0, y_nl, x0 + max_n * dx + 30, y_nl, stroke=INK, stroke_width=1.8, marker_end="arrow-ink")
    for g in range(0, max_n + 1):
        cx = x0 + g * dx
        svg.line(cx, y_nl - 4, cx, y_nl + 4, stroke=INK, stroke_width=1)
        if g == 4:
            svg.rect(cx - 17, y_nl - 19, 34, 39, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.2, rx=14)
            svg.circle(cx, y_nl, 7.0, fill=NAVY, stroke=BG, stroke_width=1.4)
            svg.text(cx, y_nl + 16, "4", font=FONT_SERIF, size=13, fill=NAVY, anchor="middle", weight="bold")
        elif g in (8, 12):
            svg.circle(cx, y_nl, 4.0, fill=GRAY_MID)
            svg.text(cx, y_nl + 16, str(g), font=FONT_SERIF, size=12, fill=GRAY_DARK, anchor="middle")
        else:
            svg.circle(cx, y_nl, 2.2, fill=GRAY_LIGHT)
            svg.text(cx, y_nl + 16, str(g), font=FONT_SERIF, size=11.5, fill=GRAY_MID, anchor="middle")

    cx12, cx8, cx4 = x0 + 12 * dx, x0 + 8 * dx, x0 + 4 * dx
    svg.path(f"M {cx12} {y_nl - 6} Q {(cx12 + cx8)/2} {y_nl - 24} {cx8 + 4} {y_nl - 6}", stroke=NAVY, stroke_width=1.4, dash="3,2", marker_end="arrow-navy")
    svg.path(f"M {cx8 - 4} {y_nl - 6} Q {(cx8 + cx4)/2} {y_nl - 24} {cx4 + 18} {y_nl - 6}", stroke=NAVY, stroke_width=1.4, dash="3,2", marker_end="arrow-navy")

    return svg


# ==============================================================================
# FIGURE 4: Boundary Pairs (Coprime (13, 8) -> 1  AND  Degenerate (0, 0) -> 0)
# ==============================================================================
def make_fig_4():
    svg = SVGCanvas(width=900, height=640)
    svg.add_standard_markers()

    draw_header(
        svg,
        "Extreme Strips: Coprime Inputs Collapse to {1}; Zero Inputs Fill All of ℕ",
        'The same definition <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>) = <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">a</tspan>) ∩ <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">b</tspan>) handles coprime numbers and <tspan font-style="italic">a</tspan> = <tspan font-style="italic">b</tspan> = 0 without special cases',
    )

    x0 = 215
    dx = 30
    max_n = 13
    badge_x = 706

    # ---- PANEL A: Coprime a = 13, b = 8 -> gcd = 1 ----
    yA = 80
    svg.rect(24, yA, 852, 254, fill="#fbfaf2", stroke=GRAY_LIGHT, stroke_width=1.3, rx=8)
    svg.text(
        40,
        yA + 24,
        'Case A — Coprime Inputs (a = 13, b = 8):   Div(13) and Div(8) share only d = 1, so Gcd(13, 8) = { 1 }',
        font=FONT_SERIF,
        size=15,
        fill=INK,
        weight="bold",
    )

    yrA = yA + 45
    for d in range(0, max_n + 1):
        cx = x0 + d * dx
        svg.text(cx, yrA, str(d), font=FONT_SERIF, size=11.5, fill=PURPLE if d == 1 else GRAY_DARK, anchor="middle", weight="bold" if d == 1 else "normal")
        if d == 1:
            svg.line(cx, yrA + 5, cx, yA + 188, stroke=PURPLE_FILL, stroke_width=7)
        svg.line(cx, yrA + 5, cx, yA + 188, stroke=GRAY_FAINT, stroke_width=1)

    div13 = divisors(13, max_n)
    div8 = divisors(8, max_n)
    cdA = div13 & div8

    draw_strip_row(svg, yA + 70, x0, dx, max_n, '<tspan font-style="italic">Div</tspan>(13) (prime)', None, active_set=div13, mode="input", badge_text="{1, 13}", badge_color=NAVY, badge_bg=NAVY_LIGHT, badge_x=badge_x)
    draw_strip_row(svg, yA + 103, x0, dx, max_n, '<tspan font-style="italic">Div</tspan>(8)', None, active_set=div8, mode="input", badge_text="{1, 2, 4, 8}", badge_color=NAVY, badge_bg=NAVY_LIGHT, badge_x=badge_x)
    draw_strip_row(svg, yA + 138, x0, dx, max_n, '<tspan font-weight="bold" fill="#6A5ACD">CD(13, 8)</tspan>', None, socket_set=cdA, mode="socket", badge_text="Single socket: {1}", badge_color=PURPLE, badge_bg=PURPLE_FILL, badge_x=badge_x)
    draw_strip_row(svg, yA + 174, x0, dx, max_n, 'Candidate <tspan font-weight="bold" fill="#00008b">g = 1</tspan> : <tspan font-style="italic">Div</tspan>(1)', None, active_set=divisors(1, max_n), socket_set=cdA, mode="test", badge_text="1 : Gcd(13, 8) ✓", badge_color=PURPLE, badge_bg=PURPLE_FILL, badge_x=badge_x)

    ynlA = yA + 220
    svg.text(40, ynlA + 4, "Type  Gcd(13, 8) = {1}", font=FONT_SERIF, size=13, fill=PURPLE, weight="bold")
    svg.line(x0, ynlA, x0 + max_n * dx + 24, ynlA, stroke=INK, stroke_width=1.5, marker_end="arrow-ink")
    for g in range(0, max_n + 1):
        cx = x0 + g * dx
        if g == 1:
            svg.rect(cx - 14, ynlA - 14, 28, 36, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2, rx=12)
            svg.circle(cx, ynlA, 6.0, fill=NAVY, stroke=BG, stroke_width=1.2)
            svg.text(cx, ynlA + 17, "1", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
        else:
            svg.circle(cx, ynlA, 2.2, fill=GRAY_LIGHT)
            svg.text(cx, ynlA + 17, str(g), font=FONT_SERIF, size=11, fill=GRAY_MID, anchor="middle")

    # ---- PANEL B: Zero Inputs a = 0, b = 0 -> gcd = 0 ----
    yB = 348
    svg.rect(24, yB, 852, 274, fill="#fbfaf2", stroke=GRAY_LIGHT, stroke_width=1.3, rx=8)
    svg.text(
        40,
        yB + 24,
        'Case B — All-Zero Inputs (a = 0, b = 0):   Every d ∈ ℕ divides 0 (since 0 = d · 0), so Div(0) = ℕ and Gcd(0, 0) = { 0 }',
        font=FONT_SERIF,
        size=15,
        fill=INK,
        weight="bold",
    )

    yrB = yB + 45
    for d in range(0, max_n + 1):
        cx = x0 + d * dx
        svg.text(cx, yrB, str(d), font=FONT_SERIF, size=11.5, fill=PURPLE, anchor="middle", weight="bold")
        svg.line(cx, yrB + 5, cx, yB + 195, stroke=PURPLE_FILL, stroke_width=5)

    div0 = divisors(0, max_n)

    draw_strip_row(
        svg, yB + 72, x0, dx, max_n,
        '<tspan font-style="italic">Div</tspan>(0) = ℕ', None,
        active_set=div0, mode="input", show_infinity=True, infinity_active=True,
        badge_text="All d ∈ ℕ (incl. 0)", badge_color=NAVY, badge_bg=NAVY_LIGHT, badge_x=badge_x,
    )
    draw_strip_row(
        svg, yB + 108, x0, dx, max_n,
        '<tspan font-weight="bold" fill="#6A5ACD">CD(0, 0)</tspan> = ℕ ∩ ℕ', None,
        socket_set=div0, mode="socket", show_infinity=True, infinity_socket=True,
        badge_text="Infinite sockets: ℕ", badge_color=PURPLE, badge_bg=PURPLE_FILL, badge_x=badge_x,
    )
    draw_strip_row(
        svg, yB + 144, x0, dx, max_n,
        'Wrong <tspan font-weight="bold" fill="#8b0000">g = 12</tspan> : <tspan font-style="italic">Div</tspan>(12)', None,
        active_set=divisors(12, max_n), socket_set=div0, mode="test", show_infinity=True, infinity_socket=True, infinity_active=False,
        badge_text="ERROR: ∞ empty sockets", badge_color=RED, badge_bg=RED_FILL, badge_x=badge_x,
    )
    draw_strip_row(
        svg, yB + 180, x0, dx, max_n,
        'Valid <tspan font-weight="bold" fill="#00008b">g = 0</tspan> : <tspan font-style="italic">Div</tspan>(0)', None,
        active_set=div0, socket_set=div0, mode="test", show_infinity=True, infinity_socket=True, infinity_active=True,
        badge_text="0 : Gcd(0, 0) ✓", badge_color=PURPLE, badge_bg=PURPLE_FILL, badge_x=badge_x,
    )

    ynlB = yB + 238
    svg.text(40, ynlB + 4, "Type  Gcd(0, 0) = {0}", font=FONT_SERIF, size=13, fill=PURPLE, weight="bold")
    svg.line(x0, ynlB, x0 + max_n * dx + 24, ynlB, stroke=INK, stroke_width=1.5, marker_end="arrow-ink")
    for g in range(0, max_n + 1):
        cx = x0 + g * dx
        if g == 0:
            svg.rect(cx - 14, ynlB - 14, 28, 36, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2, rx=12)
            svg.circle(cx, ynlB, 6.0, fill=NAVY, stroke=BG, stroke_width=1.2)
            svg.text(cx, ynlB + 17, "0", font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
        elif g == 12:
            svg.circle(cx, ynlB, 5.5, fill=RED_FILL, stroke=RED, stroke_width=1.6)
            svg.line(cx - 4, ynlB - 4, cx + 4, ynlB + 4, stroke=RED, stroke_width=1.6)
            svg.line(cx - 4, ynlB + 4, cx + 4, ynlB - 4, stroke=RED, stroke_width=1.6)
            svg.text(cx, ynlB + 17, "12", font=FONT_SERIF, size=11.5, fill=RED, anchor="middle", weight="bold")
        else:
            svg.circle(cx, ynlB, 2.2, fill=GRAY_LIGHT)
            svg.text(cx, ynlB + 17, str(g), font=FONT_SERIF, size=11, fill=GRAY_MID, anchor="middle")
    svg.text(x0 + 7.2 * dx, ynlB - 14, "Every g > 0 has only finitely many divisors, leaving infinitely many sockets empty!", font=FONT_SANS, size=11.5, fill=RED, anchor="middle")

    return svg


# ==============================================================================
# FIGURE 5: Dependent Type Family & Subtyping as Socket-Inclusion
# ==============================================================================
def make_fig_5():
    svg = SVGCanvas(width=900, height=595)
    svg.add_standard_markers()

    draw_header(
        svg,
        "Subtyping Splits Into Two Strip Rules Whose Intersection Is Gcd(a, b)",
        'Half-types:  <tspan font-style="italic">CommonDiv</tspan>(12, 8) (no spills: <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>) ⊆ <tspan font-style="italic">CD</tspan>)  ∩  <tspan font-style="italic">CommonMultOfCD</tspan>(12, 8) (no empty sockets: <tspan font-style="italic">CD</tspan> ⊆ <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>))  =  <tspan font-weight="bold" fill="#6A5ACD">Gcd(12, 8)</tspan>',
    )

    x0 = 240
    dx = 33
    max_n = 12
    cd = divisors(12, max_n) & divisors(8, max_n)

    svg.text(36, 92, "All Candidates g ∈ 0..12 Tested Against Sockets CD(12, 8) = {1, 2, 4}", font=FONT_SERIF, size=14.5, fill=INK, weight="bold")
    svg.text(36, 110, "Each row is Div(g); each column is d ∈ 0..12. Purple columns d ∈ {1, 2, 4} are the required sockets.", font=FONT_SANS, size=12, fill=GRAY_DARK)

    candidates = [
        (1, "Div(1) ⊂ CD", "common divisor (misses 2, 4)"),
        (2, "Div(2) ⊂ CD", "common divisor (misses 4)"),
        (4, "Div(4) = CD", "EXACT MATCH  →  4 : Gcd(12, 8)"),
        (8, "CD ⊂ Div(8)", "multiple of 4 (spills 8)"),
        (12, "CD ⊂ Div(12)", "multiple of 4 (spills 3, 6, 12)"),
        (0, "CD ⊂ Div(0)=ℕ", "multiple of 4 (spills all d ∉ {1,2,4})"),
        (6, "incomparable", "misses 4  AND  spills 3, 6"),
    ]

    y_mat_top = 136
    row_h = 34

    for d in range(0, max_n + 1):
        cx = x0 + d * dx
        is_cd = d in cd
        svg.text(cx, y_mat_top - 8, str(d), font=FONT_SERIF, size=12.5, fill=PURPLE if is_cd else GRAY_DARK, anchor="middle", weight="bold" if is_cd else "normal")
        if is_cd:
            svg.rect(cx - 11, y_mat_top, 22, len(candidates) * row_h, fill=PURPLE_FILL, opacity=0.55)

    for idx, (g, rel_str, desc_str) in enumerate(candidates):
        ry = y_mat_top + idx * row_h + row_h / 2
        div_g = divisors(g, max_n)
        is_exact = (g == 4)
        is_sub = div_g.issubset(cd)
        is_sup = cd.issubset(div_g)

        if is_exact:
            svg.rect(32, ry - row_h / 2 + 2, 836, row_h - 4, fill=PURPLE_LIGHT, stroke=PURPLE, stroke_width=1.8, rx=5)
        else:
            svg.line(32, ry + row_h / 2, 868, ry + row_h / 2, stroke=GRAY_FAINT, stroke_width=1)

        g_color = PURPLE if is_exact else (NAVY if (is_sub or is_sup) else RED)
        svg.text(44, ry + 4, f"g = {g}", font=FONT_SERIF, size=13.5, fill=g_color, weight="bold")
        svg.text(106, ry + 4, rel_str, font=FONT_SANS, size=12, fill=PURPLE if is_exact else GRAY_DARK, weight="bold" if is_exact else "normal")

        svg.line(x0, ry, x0 + max_n * dx, ry, stroke=GRAY_LIGHT, stroke_width=1)

        for d in range(0, max_n + 1):
            cx = x0 + d * dx
            in_sock = d in cd
            in_act = d in div_g
            if in_sock and in_act:
                svg.circle(cx, ry, 7.5, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=1.8)
                svg.circle(cx, ry, 4.2, fill=NAVY)
            elif in_sock and not in_act:
                svg.circle(cx, ry, 7.5, fill=RED_FILL, stroke=RED, stroke_width=1.8, dash="2,2")
            elif in_act and not in_sock:
                svg.circle(cx, ry, 5.5, fill=RED)
                svg.line(cx - 6, ry - 6, cx + 6, ry + 6, stroke=RED, stroke_width=1.4)
                svg.line(cx - 6, ry + 6, cx + 6, ry - 6, stroke=RED, stroke_width=1.4)
            else:
                svg.circle(cx, ry, 1.8, fill=GRAY_LIGHT)

        bx = x0 + max_n * dx + 20
        svg.text(bx, ry + 4, desc_str, font=FONT_SANS, size=12, fill=PURPLE if is_exact else (RED if g == 6 else GRAY_DARK), weight="bold" if is_exact else "normal")

    # Bottom Panel: Subtyping as set containment of 3 number-line strips!
    y_sub = 390
    svg.rect(28, y_sub, 844, 184, fill="#faf8ee", stroke=PURPLE, stroke_width=1.5, rx=8)
    svg.text(
        44,
        y_sub + 24,
        'Subtyping Is Set Containment on the Value Number Line:   <tspan font-weight="bold" fill="#6A5ACD">Gcd(12, 8)</tspan> ⊆ CommonDiv(12, 8)   and   <tspan font-weight="bold" fill="#6A5ACD">Gcd(12, 8)</tspan> ⊆ MultOfCD(12, 8)',
        font=FONT_SERIF,
        size=14,
        fill=INK,
        raw=True,
    )

    nl_x0 = 330
    nl_dx = 40

    def draw_type_line(y_line, title_left, sub_left, members, highlight_singleton=False):
        svg.text(44, y_line - 2, title_left, font=FONT_SERIF, size=13, fill=PURPLE if highlight_singleton else INK, weight="bold", raw=True)
        svg.text(44, y_line + 13, sub_left, font=FONT_SANS, size=11.5, fill=GRAY_DARK, raw=True)
        svg.line(nl_x0, y_line, nl_x0 + max_n * nl_dx + 25, y_line, stroke=INK, stroke_width=1.4, marker_end="arrow-ink")
        for g in range(0, max_n + 1):
            cx = nl_x0 + g * nl_dx
            if g in members:
                svg.circle(cx, y_line, 8.5 if highlight_singleton else 7.0, fill=PURPLE_FILL, stroke=PURPLE, stroke_width=2.0 if highlight_singleton else 1.5)
                svg.circle(cx, y_line, 4.5, fill=NAVY)
                svg.text(cx, y_line + 18, str(g), font=FONT_SERIF, size=12, fill=NAVY, anchor="middle", weight="bold")
            else:
                svg.circle(cx, y_line, 2.0, fill=GRAY_LIGHT)
                svg.text(cx, y_line + 18, str(g), font=FONT_SERIF, size=11, fill=GRAY_MID, anchor="middle")

    draw_type_line(
        y_sub + 58,
        'No-Spills Type:  { <tspan font-style="italic">g</tspan> │ <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>) ⊆ <tspan font-style="italic">CD</tspan> }',
        "g divides both 12 and 8   →   {1, 2, 4}",
        {1, 2, 4},
    )

    draw_type_line(
        y_sub + 103,
        'No-Empty-Sockets Type:  { <tspan font-style="italic">g</tspan> │ <tspan font-style="italic">CD</tspan> ⊆ <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>) }',
        "every d ∈ CD divides g   →   {0, 4, 8, 12, …}",
        {0, 4, 8, 12},
    )

    draw_type_line(
        y_sub + 148,
        'Intersection Type:  <tspan fill="#6A5ACD">Gcd(12, 8)</tspan> = { <tspan font-style="italic">g</tspan> │ <tspan font-style="italic">Div</tspan>(<tspan font-style="italic">g</tspan>) = <tspan font-style="italic">CD</tspan> }',
        "subtype of both: {1, 2, 4} ∩ {0, 4, 8, 12, …} = {4}",
        {4},
        highlight_singleton=True,
    )

    cx4 = nl_x0 + 4 * nl_dx
    svg.rect(cx4 - 15, y_sub + 44, 30, 128, fill="none", stroke=PURPLE, stroke_width=1.8, dash="3,2", rx=13)

    return svg


def main():
    figs = [
        ("fig-1.svg", make_fig_1()),
        ("fig-2.svg", make_fig_2()),
        ("fig-3.svg", make_fig_3()),
        ("fig-4.svg", make_fig_4()),
        ("fig-5.svg", make_fig_5()),
    ]
    for fname, svg in figs:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(svg.render())
        print(f"Wrote {fname}")


if __name__ == "__main__":
    main()
