from xcheck import xcheck
from run import run
import specs, random
for n in [2147395599, 2147395600, 2147483647]:
    m, outs, status, fails = run('isqrt.rwat', specs.ISQRT, [('$isqrt',[n])], limit=2_000_000, record=False)
    print('isqrt', n, outs, status, 'checks', len(m.checks), 'fails', len(fails), 'steps', m.step)
# hash: random op sequences
random.seed(7)
bad=0
for trial in range(60):
    keys = random.sample(range(-20, 40), 10)
    calls=[]; model={}; expect=[]
    for _ in range(25):
        op = random.choice(['insert','insert','lookup','delete'])
        k = random.choice(keys)
        if op=='insert': calls.append(('$insert',[k, random.randint(0,999)]))
        elif op=='lookup': calls.append(('$lookup',[k,-1]))
        else: calls.append(('$delete',[k]))
    m, mine, real, status, fails = xcheck('hash.rwat', specs.HASH, calls, tag='hash')
    # independent dict model (insert refused when used==7)
    if mine != real or fails or status!='ok':
        bad+=1; print('BAD', calls, mine, real, status, fails[:2])
print('hash bad', bad, 'last checks', len(m.checks), 'used', m.globals)
