import json, os, base64
W = os.path.dirname(os.path.abspath(__file__)) + '/src/'
REPO = '/home/jmandel/hobby/codalon-dependent-viz/'
OUT = REPO + 'artifacts/01-refined-codillon-v2.html'
F = '/home/jmandel/hobby/.agent-scratch/codalon-viz/codillon/public/fonts/'
b64 = lambda n: base64.b64encode(open(F + n, 'rb').read()).decode()
fonts = ("@font-face { font-family: 'MLMRoman12'; src: url(data:font/woff2;base64," + b64('mlmr12.woff2') + ") format('woff2'); font-weight: normal; font-style: normal; }\n"
         "@font-face { font-family: 'MLMSansDC10'; src: url(data:font/woff2;base64," + b64('mlmssdc10.woff2') + ") format('woff2'); font-weight: normal; font-style: normal; }\n")
sess = {}
for n in ('isqrt', 'parity', 'gcd'):
    d = json.load(open(REPO + f'editor/v2/examples/v2/sessions/{n}.json'))
    sess[n] = {'title': d['title'], 'turns': [{'note': t['note'], 'expect': t['expect'], 'line': min(e['replace_lines'][0] for e in t['response']['edits']) - 1} for t in d['turns']]}
body = ''.join(open(W + f).read() for f in ('body1.html', 'body2.html', 'body3.html', 'body4.html', 'body5.html'))
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Refined Codillon, version 2</title><link rel="icon" href="data:,">
<meta name="description" content="A walkthrough of Refined Codillon v2: refinements in the types, proofs the kernel finds and draws in a fact lane, block types as invariants, four verdicts, and vericoding, shown in the real editor.">
<style>
{fonts}
{open(W + 'style.css').read()}
</style></head>
<body>
{body}
<script>
// the recorded vericoding sessions (editor/v2/examples/v2/sessions/*.json): titles, turn notes and recorded outcomes
window.SESSIONS = {json.dumps(sess, ensure_ascii=False)};
{open(W + 'states.js').read()}
{open(W + 'page.js').read()}
</script>
</body></html>
'''
open(OUT, 'w').write(html)
print(len(html.encode()), 'bytes')
