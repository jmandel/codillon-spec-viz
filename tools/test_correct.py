from xcheck import xcheck
import specs, random
random.seed(1)
bad = 0
def chk(name, prog, spec, calls):
    global bad
    m, mine, real, status, fails = xcheck(prog, spec, calls, tag=name)
    agree = all((a == b) for a, b in zip(mine, real)) and len(mine) == len(real)
    if not agree or fails or status != 'ok':
        bad += 1; print('MISMATCH/FAIL', name, calls[:3], mine[:5], real[:5], status, fails[:2])
    return m
xs = [0,1,2,3,4,-1,-2,-3,-4,2147483647,-2147483648,1000,1001] + [random.randint(-2**31, 2**31-1) for _ in range(20)]
chk('parity', 'parity.rwat', specs.PARITY, [('$half_or_neg1',[x]) for x in xs])
for x in xs:
    chk('parity1', 'parity.rwat', specs.PARITY, [('$half_or_neg1',[x])])
ns = [0,1,2,3,4,5,8,9,10,15,16,17,24,25,26,99,100,101, 2000, 12345] + [random.randint(0, 3_000_000) for _ in range(10)]
for n in ns: chk('isqrt', 'isqrt.rwat', specs.ISQRT, [('$isqrt',[n])])
for a,b in [(0,0),(0,5),(5,0),(12,8),(8,12),(4,6),(17,5),(1071,462),(2147483647,2147483646),(2147483647, 0),(48,18)] + [(random.randint(0,2**31-1), random.randint(0,2**31-1)) for _ in range(20)]:
    chk('gcd', 'gcd.rwat', specs.GCD, [('$gcd',[a,b])])
for b,e,m in [(5,0,1),(5,3,1),(2,10,1000),(3,200,65536),(65535,2,65536),(49999,4,50000),(7,13,13),(0,0,7),(0,5,7),(123456,789,65521),(2147483647,2147483647,65536)] + [(random.randint(0,2**31-1), random.randint(0,2**31-1), random.randint(1,65536)) for _ in range(20)]:
    chk('powmod', 'powmod.rwat', specs.POWMOD, [('$pow_mod',[b,e,m])])
print('bad =', bad)
