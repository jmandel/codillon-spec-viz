"""Prepare a standalone SVG for inlining: prefix ids, drop size attrs, strip externals."""
import re

def prep(svg_text, prefix, label):
    s = svg_text
    s = re.sub(r'<\?xml[^>]*\?>', '', s)
    s = re.sub(r'<!DOCTYPE[^>]*>', '', s)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    ids = re.findall(r'\sid="([^"]+)"', s)
    for i in sorted(set(ids), key=len, reverse=True):
        s = s.replace(f'id="{i}"', f'id="{prefix}{i}"')
        s = s.replace(f'url(#{i})', f'url(#{prefix}{i})')
        s = s.replace(f'href="#{i}"', f'href="#{prefix}{i}"')
    # leftover url(#..) referencing unknown ids would be a bug
    for ref in re.findall(r'url\(#([^)]+)\)', s):
        assert ref.startswith(prefix), (prefix, ref)
    assert not re.search(r'(xlink:)?href="(?!#)', s), 'external href'
    assert '<script' not in s and '<image' not in s and '@import' not in s and 'foreignObject' not in s
    m = re.search(r'<svg\b[^>]*>', s)
    root = m.group(0)
    vb = re.search(r'viewBox="([^"]+)"', root).group(1)
    new = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" class="fig" role="img" '
           f'aria-label="{label}" preserveAspectRatio="xMidYMid meet">')
    s = s[:m.start()] + new + s[m.end():]
    s = s.strip()
    return s, vb
