#!/usr/bin/env python3
"""Assemble artifacts/gcd-type-gallery.html from audited/fixed SVGs and meta.py."""
import html, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgprep import prep
import meta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = '/home/jmandel/hobby/codalon-dependent-viz/artifacts/gcd-type-gallery.html'
E = html.escape


def svg_path(nn, k):
    if nn == '05':
        return os.path.join(HERE, 'regen', '05', f'fig-{k}.svg')
    p = os.path.join(HERE, 'fixed', nn, f'fig-{k}.svg')
    if not os.path.exists(p):
        if os.environ.get('ALLOW_SRC'):
            return f'/home/jmandel/hobby/.agent-scratch/codalon-viz/gcdviz/{nn}/fig-{k}.svg'
        raise SystemExit(f'missing fixed figure {p}')
    return p


def fig_html(nn, k, caption, cls):
    raw = open(svg_path(nn, k), encoding='utf-8').read()
    svg, vb = prep(raw, f'f{nn}{k}-', E(f'Angle {nn}, figure {k}: {caption}'))
    fid = f'f{nn}-{k}'
    btn = ('<button class="zoom" type="button" aria-expanded="false" '
           f'aria-controls="{fid}" title="Enlarge this figure">enlarge</button>')
    return (f'<figure class="{cls}" id="{fid}">'
            f'<div class="svgbox">{svg}</div>'
            f'<figcaption><span class="fn">fig. {int(k)}</span> {E(caption)} {btn}</figcaption>'
            f'</figure>')


def divs(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def chips(ds, cls=''):
    return ''.join(f'<span class="chip {cls}">{d}</span>' for d in ds)


def hero_example():
    a, b = 12, 8
    g = math.gcd(a, b)
    da, db = divs(a), divs(b)
    cd = sorted(set(da) & set(db))
    assert cd == divs(g)
    rows = [
        (f'Div({a})', chips(da), ''),
        (f'Div({b})', chips(db), ''),
        (f'Div({a}) ∩ Div({b})', chips(cd, 'p'), 'the common divisors'),
        (f'Div({g})', chips(divs(g), 'p'), f'equal, so {g} is in the type'),
        ('Div(2)', chips(divs(2)) + '<span class="chip miss">4</span>', 'missing 4: 2 is not'),
        ('Div(8)', chips(divs(8)[:3]) + '<span class="chip bad">8</span>', '8 ∤ 12: 8 is not'),
    ]
    out = ['<div class="ex">']
    for lab, cs, note in rows:
        out.append(f'<div class="exr"><span class="exl">{lab}</span><span class="exc">{cs}</span>'
                   f'<span class="exn">{note}</span></div>')
    out.append(f'<div class="exr res"><span class="exl">Gcd({a}, {b})</span><span class="exc">'
               f'<span class="type">{{ {g} }}</span></span><span class="exn">exactly one inhabitant</span></div>')
    out.append('</div>')
    return '\n'.join(out)


def angle_html(A):
    nn = A['nn']
    figs = A['figs']  # list of (k, caption)
    strong = A['strong']
    parts = [f'<article class="angle" id="a{nn}">']
    parts.append('<header class="ah">'
                 f'<span class="num">{nn}</span>'
                 f'<div><h3>{E(A["heading"])}</h3>'
                 f'<div class="meta">{E(A["angle"])} · {E(A["model"])} · {len(figs)} figures</div></div>'
                 '</header>')
    parts.append(f'<p class="claim">{E(A["claim"])}</p>')
    cap = dict(figs)
    parts.append(fig_html(nn, strong, cap[strong], 'hero'))
    enc = ''.join(f'<li><span class="mk">{E(m)}</span> <span class="ar">→</span> {E(v)}</li>' for m, v in A['encoding'])
    parts.append('<div class="facts">'
                 f'<div class="enc"><h4>Encoding</h4><ul>{enc}</ul></div>'
                 f'<div class="side"><h4>What it hides</h4><p>{E(A["hides"])}</p>'
                 f'<h4>Audit</h4><p class="audit">{A["audit_html"]}</p>'
                 + (f'<p class="also">{A["also_html"]}</p>' if A.get('also_html') else '') +
                 '</div></div>')
    rest = [(k, c) for k, c in figs if k != strong]
    if rest:
        parts.append('<div class="thumbs">' + ''.join(fig_html(nn, k, c, 'thumb') for k, c in rest) + '</div>')
    parts.append('</article>')
    return '\n'.join(parts)


def main():
    fonts = open(os.path.join(HERE, 'fonts.css')).read()
    css = open(os.path.join(HERE, 'page.css')).read()
    js = open(os.path.join(HERE, 'page.js')).read()
    angles = {A['nn']: A for A in meta.ANGLES}
    nav = []
    body = []
    for si, sec in enumerate(meta.SECTIONS):
        sub = ''.join(f'<li><a href="#a{nn}"><span class="nnum">{nn}</span><span class="lbl"> {E(angles[nn]["short"])}</span></a></li>'
                      for nn in sec['angles'])
        nav.append(f'<li class="ns"><a href="#{sec["id"]}"><span class="long">{E(sec["navtitle"])}</span>'
                   f'<span class="short">{["I", "II", "III", "IV"][si]}</span></a><ul>{sub}</ul></li>')
        body.append(f'<section class="sec" id="{sec["id"]}">')
        body.append(f'<div class="kicker">{E(sec["kicker"])}</div><h2>{E(sec["title"])}</h2>')
        body.append(f'<p class="secintro">{sec["intro_html"]}</p>')
        for nn in sec['angles']:
            body.append(angle_html(angles[nn]))
        body.append('</section>')
    nav.append('<li class="ns"><a href="#compare">Compare all ten</a></li>')
    nav.append('<li class="ns"><a href="#audit">Audit log</a></li>')

    page = meta.TEMPLATE
    rep = {
        '{{FONTS}}': fonts, '{{CSS}}': css, '{{JS}}': js,
        '{{NAV}}': '\n'.join(nav), '{{BODY}}': '\n'.join(body),
        '{{EXAMPLE}}': hero_example(), '{{COMPARE}}': meta.compare_html(),
        '{{AUDIT}}': meta.audit_html(), '{{MAP}}': meta.map_html(),
    }
    for k, v in rep.items():
        assert k in page, k
        page = page.replace(k, v)
    assert '{{' not in page
    # no external fetches: only data: urls and same-page/relative links in <a>
    for m in re.finditer(r'\b(src|href)="([^"]*)"', page):
        attr, url = m.groups()
        if attr == 'src':
            raise SystemExit(f'unexpected src= {url}')
    for m in re.finditer(r'url\(([^)]*)\)', page):
        u = m.group(1).strip('\'"')
        assert u.startswith('#') or u.startswith('data:'), u
    ids = re.findall(r'\sid="([^"]+)"', page)
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, dup
    open(OUT, 'w', encoding='utf-8').write(page)
    print('wrote', OUT, len(page), 'bytes;', len(ids), 'ids')


if __name__ == '__main__':
    main()
