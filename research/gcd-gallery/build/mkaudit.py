import os
H = os.path.dirname(os.path.abspath(__file__))
order = ['01','02','03','04','05','06','07','08','09','10']
head = open(os.path.join(H, 'audit-head.md')).read()
parts = [head]
for nn in order:
    p = os.path.join(H, 'audits', f'{nn}.md')
    parts.append(open(p).read().strip() if os.path.exists(p) else f'### {nn}\n(audit missing)')
open('/home/jmandel/hobby/.agent-scratch/codalon-viz/gcdviz/audit.md', 'w').write('\n\n---\n\n'.join(parts) + '\n')
print('ok')
