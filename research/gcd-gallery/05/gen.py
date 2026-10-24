import math

def gcd(a, b):
    return math.gcd(a, b)

def draw_grid(svg, max_x, max_y, cell_size, margin_x, margin_y):
    svg.append(f'<g stroke="#ccc" stroke-width="1">')
    for x in range(max_x + 1):
        cx = margin_x + x * cell_size
        svg.append(f'<line x1="{cx}" y1="{margin_y}" x2="{cx}" y2="{margin_y + max_y * cell_size}" />')
    for y in range(max_y + 1):
        cy = margin_y + (max_y - y) * cell_size
        svg.append(f'<line x1="{margin_x}" y1="{cy}" x2="{margin_x + max_x * cell_size}" y2="{cy}" />')
    svg.append('</g>')

    # Axes
    svg.append(f'<g font-family="Georgia, \\\'Times New Roman\\\', serif" font-size="12" fill="#222" text-anchor="middle">')
    for x in range(max_x + 1):
        if x % 2 == 0:
            cx = margin_x + x * cell_size
            cy = margin_y + max_y * cell_size + 15
            svg.append(f'<text x="{cx}" y="{cy}">{x}</text>')
    for y in range(max_y + 1):
        if y % 2 == 0:
            cx = margin_x - 15
            cy = margin_y + (max_y - y) * cell_size + 4
            svg.append(f'<text x="{cx}" y="{cy}">{y}</text>')
    
    # Axis labels
    svg.append(f'<text x="{margin_x + max_x * cell_size / 2}" y="{margin_y + max_y * cell_size + 35}" font-style="italic">x</text>')
    svg.append(f'<text x="{margin_x - 35}" y="{margin_y + max_y * cell_size / 2}" font-style="italic" transform="rotate(-90 {margin_x - 35} {margin_y + max_y * cell_size / 2})">y</text>')
    svg.append('</g>')

def draw_ray(svg, x, y, max_x, max_y, cell_size, margin_x, margin_y, stroke="#d9d5f2"):
    if x == 0 and y == 0: return
    multiplier = min(max_x / x if x > 0 else 999, max_y / y if y > 0 else 999)
    end_x = x * multiplier
    end_y = y * multiplier
    cx1 = margin_x
    cy1 = margin_y + max_y * cell_size
    cx2 = margin_x + end_x * cell_size
    cy2 = margin_y + (max_y - end_y) * cell_size
    svg.append(f'<line x1="{cx1}" y1="{cy1}" x2="{cx2}" y2="{cy2}" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="4,4" />')


def make_fig(filename, a, b, title, max_x, max_y, cell_size, margin_x, margin_y, weak_invariant=False, empty_target=False):
    width = 900
    height = margin_y * 2 + max_y * cell_size + 40
    
    svg = [f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #fffff0;">"""]
    svg.append(f"""<defs>
    <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto-start-reverse">
      <path d="M 0 0 L 6 3 L 0 6 z" fill="#6A5ACD" />
    </marker>
    <marker id="arrow-traj" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto-start-reverse">
      <path d="M 0 0 L 6 3 L 0 6 z" fill="#00008b" />
    </marker>
    <marker id="arrow-err" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto-start-reverse">
      <path d="M 0 0 L 6 3 L 0 6 z" fill="#8b0000" />
    </marker>
  </defs>""")
    
    svg.append(f"""<text x="{width/2}" y="30" font-family="Georgia, 'Times New Roman', serif" font-size="20" font-weight="bold" fill="#222" text-anchor="middle">{title}</text>""")
    
    draw_grid(svg, max_x, max_y, cell_size, margin_x, margin_y)
    
    target_g = gcd(a, b)
    
    # Shade the target cells and rays
    shaded = []
    for x in range(max_x + 1):
        for y in range(max_y + 1):
            g = gcd(x, y)
            if weak_invariant:
                # Type error: invariant is just that it's a multiple of 2, instead of exactly 4.
                if g % 2 == 0:
                    shaded.append((x, y))
            elif empty_target:
                if x == 0 and y == 0:
                    shaded.append((x, y))
            else:
                if g == target_g:
                    shaded.append((x, y))
                
    # Rays
    if empty_target:
        pass
    else:
        ray_stroke = "#e6a8a8" if weak_invariant else "#d9d5f2"
        for (x, y) in shaded:
            g = gcd(x, y)
            if g > 0:
                draw_ray(svg, x/g, y/g, max_x, max_y, cell_size, margin_x, margin_y, stroke=ray_stroke)

    fill_color = "#e6a8a8" if weak_invariant else "#d9d5f2"
    stroke_color = "#8b0000" if weak_invariant else "#6A5ACD"
    arrow_marker = "arrow-err" if weak_invariant else "arrow"

    for (x, y) in shaded:
        cx = margin_x + x * cell_size
        cy = margin_y + (max_y - y) * cell_size
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{cell_size/2 - 2}" fill="{fill_color}" stroke="{stroke_color}" stroke-width="1.5" />')
        
        # transition arrow
        if y > 0:
            nx, ny = y, x % y
            ncx = margin_x + nx * cell_size
            ncy = margin_y + (max_y - ny) * cell_size
            svg.append(f'<line x1="{cx}" y1="{cy}" x2="{ncx}" y2="{ncy}" stroke="{stroke_color}" stroke-width="1" stroke-dasharray="2,2" marker-end="url(#{arrow_marker})" />')
            
    # Trajectory for a, b
    traj = [(a, b)]
    x, y = a, b
    while y > 0:
        x, y = y, x % y
        traj.append((x, y))
        
    for i in range(len(traj) - 1):
        x1, y1 = traj[i]
        x2, y2 = traj[i+1]
        cx1 = margin_x + x1 * cell_size
        cy1 = margin_y + (max_y - y1) * cell_size
        cx2 = margin_x + x2 * cell_size
        cy2 = margin_y + (max_y - y2) * cell_size
        svg.append(f'<line x1="{cx1}" y1="{cy1}" x2="{cx2}" y2="{cy2}" stroke="#00008b" stroke-width="2.5" marker-end="url(#arrow-traj)" />')
        svg.append(f'<circle cx="{cx1}" cy="{cy1}" r="{cell_size/2}" fill="#00008b" />')
    
    # last point
    x1, y1 = traj[-1]
    cx1 = margin_x + x1 * cell_size
    cy1 = margin_y + (max_y - y1) * cell_size
    svg.append(f'<circle cx="{cx1}" cy="{cy1}" r="{cell_size/2}" fill="#00008b" />')
    
    # highlight exit row
    svg.append(f'<line x1="{margin_x}" y1="{margin_y + max_y * cell_size}" x2="{margin_x + max_x * cell_size}" y2="{margin_y + max_y * cell_size}" stroke="{stroke_color}" stroke-width="4" opacity="0.3" />')
    svg.append(f'<text x="{margin_x + max_x * cell_size + 10}" y="{margin_y + max_y * cell_size + 4}" font-family="Arial Narrow, Arial, sans-serif" font-size="14" fill="{stroke_color}">y = 0 (exit row)</text>')
    
    # exit cells annotations
    if weak_invariant:
        svg.append(f'<text x="{margin_x + max_x * cell_size/2}" y="{margin_y + max_y * cell_size + 45}" font-family="Arial Narrow, Arial, sans-serif" font-size="14" fill="#8b0000" text-anchor="middle">TYPE ERROR: Weak invariant meets exit row in many cells (2, 4, 6...). Return value is not unique!</text>')
    elif empty_target:
        svg.append(f'<text x="{margin_x}" y="{margin_y + max_y * cell_size + 45}" font-family="Arial Narrow, Arial, sans-serif" font-size="14" fill="#6A5ACD" text-anchor="middle">Single exit cell: (0, 0) -> gcd is 0</text>')
    else:
        svg.append(f'<text x="{margin_x + target_g * cell_size}" y="{margin_y + max_y * cell_size + 45}" font-family="Arial Narrow, Arial, sans-serif" font-size="14" fill="#6A5ACD" text-anchor="middle">Single exit cell: ({target_g}, 0) -> gcd is {target_g}</text>')
        svg.append(f'<line x1="{margin_x + target_g * cell_size}" y1="{margin_y + max_y * cell_size + 30}" x2="{margin_x + target_g * cell_size}" y2="{margin_y + max_y * cell_size + 10}" stroke="#6A5ACD" stroke-width="1.5" marker-end="url(#arrow)" />')
        
        if filename == "fig-1.svg":
            ray_label_x = margin_x + 10 * cell_size
            ray_label_y = margin_y + (max_y - 5) * cell_size + 15
            svg.append(f'<text x="{ray_label_x}" y="{ray_label_y}" font-family="Arial Narrow, Arial, sans-serif" font-size="12" fill="#6A5ACD" transform="rotate(-26.5 {ray_label_x} {ray_label_y})">Each ray meets the set exactly once</text>')
    
    svg.append('</svg>')
    
    with open(filename, "w") as f:
        f.write("\\n".join(svg))

make_fig("fig-1.svg", 12, 8, "Invariant set gcd(x,y) = 4 is closed under loop transitions.", 20, 20, 25, 60, 60)
make_fig("fig-2.svg", 13, 8, "Coprime pairs (gcd = 1) form a dense invariant set.", 16, 16, 30, 60, 60)
make_fig("fig-3.svg", 0, 0, "Zero-inputs (gcd = 0) has only the origin as its invariant set.", 10, 10, 40, 60, 60, empty_target=True)
make_fig("fig-4.svg", 12, 8, "TYPE ERROR: Invariant 'gcd is even' is too weak.", 20, 20, 25, 60, 60, weak_invariant=True)
