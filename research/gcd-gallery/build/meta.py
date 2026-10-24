import html
from meta_template import TEMPLATE
from meta_angles import ANGLES, AUDIT_LOG, RECOMMEND

E = html.escape

SECTIONS = [
    dict(id='s-is', navtitle='What the type is', kicker='Part I · five angles', title='What the type is',
         question='What set is Gcd(a, b)?',
         intro_html='Five pictures of the same set, from the most literal to the most algebraic. Each has to make '
                    'two things visible: the common divisors Div(a) ∩ Div(b), and why exactly one g has that set as '
                    'its own divisors. Each also draws a wrong candidate, g = 2 (too small: it misses the common divisor 4) '
                    'or g = 8 (too big: 8 does not divide 12), as a type error.',
         angles=['02', '06', '01', '03', '07']),
    dict(id='s-depends', navtitle='How it depends', kicker='Part II · one angle', title='How it depends on its inputs',
         question='How does the set change with a and b?',
         intro_html='A dependent type is a family of sets, one per input. Angle 08 is the one picture whose subject is that '
                    'family itself; most other angles show dependence too, as small multiples of a few pairs (see the '
                    '“shows dependence” column of the <a href="#compare">comparison</a>).',
         angles=['08']),
    dict(id='s-inhabits', navtitle='Why Euclid inhabits it', kicker='Part III · three angles',
         title='Why Euclid’s program inhabits it',
         question='Why does Euclid’s loop return a member?',
         intro_html='The proof has one lemma and three obligations: a step (x, y) → (y, x mod y) keeps Div(x) ∩ Div(y); '
                    'the loop starts inside the invariant, stays inside it, and makes y smaller; and at y = 0 the '
                    'invariant pins x to the type. The tiling shows the lemma, the state space shows the loop, and the '
                    'derivation shows how the obligations compose.',
         angles=['04', '05', '09']),
    dict(id='s-editor', navtitle='In the editor', kicker='Part IV · one angle', title='How it would look in the editor',
         question='What would a student see in Codillon?',
         intro_html='Codillon draws every instruction’s stack effect as a fraction of small shapes. This angle widens '
                    'those shapes into number lines so that a refined i32 shows its admitted set, and the result of '
                    '<code>$gcd</code> becomes a one-slot socket tied to the parameters.',
         angles=['10']),
]


def map_html():
    by = {A['nn']: A for A in ANGLES}
    out = ['<div class="map">']
    for i, s in enumerate(SECTIONS):
        names = ' · '.join(f'<b>{nn}</b> {E(by[nn]["short"])}' for nn in s['angles'])
        out.append(f'<a href="#{s["id"]}"><div class="kicker">{["I", "II", "III", "IV"][i]} · {E(s["title"])}</div>'
                   f'<div class="q">{E(s["question"])}</div><div class="ns2">{names}</div></a>')
    out.append('</div>')
    return '\n'.join(out)


def yn(v):
    word, rest = v
    return f'<span class="yn {word}">{word}</span>{E(rest)}'


def compare_html():
    by = {A['nn']: A for A in ANGLES}
    order = [nn for s in SECTIONS for nn in s['angles']]
    rows = []
    for nn in order:
        A = by[nn]
        t = A['table']
        uses = ''.join(f'<span class="use">{E(u)}</span>' for u in t['use'])
        rows.append('<tr>'
                    f'<td class="an"><a href="#a{nn}"><span class="nnum">{nn}</span>{E(A["short"])}</a></td>'
                    f'<td data-l="drawn as"><span class="v">{E(t["drawn"])}</span></td><td data-l="type error"><span class="v">{E(t["error"])}</span></td>'
                    f'<td data-l="dependence"><span class="v">{yn(t["dep"])}</span></td><td data-l="loop correct"><span class="v">{yn(t["loop"])}</span></td>'
                    f'<td data-l="best use"><span class="v">{uses}</span></td></tr>')
    head = ('<thead><tr><th>Angle</th><th>The type is drawn as</th><th>A type error looks like</th>'
            '<th>Shows dependence?</th><th>Shows why the loop is correct?</th><th>Best use</th></tr></thead>')
    rec = ''.join(f'<div><h4>{E(r["where"])}</h4><div class="pick">{E(r["pick"])}</div><p>{r["why"]}</p></div>'
                  for r in RECOMMEND['cards'])
    return ('<div class="kicker">Part V</div><h2>Compare all ten</h2>'
            '<p class="secintro">Each row is one angle, in the order of this page. “Shows dependence” asks whether the '
            'picture makes the family Gcd(a, b) visible, not just one member of it; “shows why the loop is correct” asks '
            'whether it carries the invariant argument, not just the final answer.</p>'
            f'<div class="tablewrap"><table class="cmp">{head}<tbody>{"".join(rows)}</tbody></table></div>'
            f'<h3 style="margin-top:22px">Recommendation</h3><p>{RECOMMEND["lead"]}</p>'
            f'<div class="rec">{rec}</div><p>{RECOMMEND["tail"]}</p>')


def audit_html():
    by = {A['nn']: A for A in ANGLES}
    order = [nn for s in SECTIONS for nn in s['angles']]
    parts = ['<div class="kicker">Appendix</div><h2>Audit log</h2>',
             f'<p class="secintro">{AUDIT_LOG["lead"]}</p>',
             '<details class="auditlog"><summary>Show every finding and fix, angle by angle</summary>']
    for nn in order:
        items = ''.join(f'<li>{x}</li>' for x in AUDIT_LOG['items'][nn])
        parts.append(f'<h5><a href="#a{nn}">{nn} · {E(by[nn]["heading"])}</a></h5><ul>{items}</ul>')
    parts.append('</details>')
    return '\n'.join(parts)
