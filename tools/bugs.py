import specs
from specs import *
BUGS = {
 # ---- parity
 'P1': dict(prog='parity.rwat', spec=specs.PARITY, edits=[('delete', 15, 15)], calls=[('$half_or_neg1',[3])]),
 'P1b': dict(prog='parity.rwat', spec=specs.PARITY, edits=[('delete', 15, 15)], calls=[('$half_or_neg1',[4])]),
 'P2': dict(prog='parity.rwat', spec=specs.PARITY, edits=[('replace', 10, 'i32.shr_s', 'i32.shr_u')], calls=[('$half_or_neg1',[-4])]),
 'P2ok': dict(prog='parity.rwat', spec=specs.PARITY, edits=[('replace', 10, 'i32.shr_s', 'i32.shr_u')], calls=[('$half_or_neg1',[6])]),
 'P3': dict(prog='parity.rwat', spec=specs.PARITY, edits=[('replace', 7, '(func $half (param $x (i32 | v % 2 == 0)) (result (i32 | v + v == x))', '(func $half (param $x (i32 | v % 2 == 0)) (result (i32 | v + v == x && v < x))')],
            spec_override={7: {'requires': PARITY[7]['requires'], 'ensures': lambda m,e,o: 2*e['result']==e['$x'] and e['result'] < e['$x']}}, calls=[('$half_or_neg1',[0])]),
 # ---- isqrt
 'S1': dict(prog='isqrt.rwat', spec=specs.ISQRT, edits=[('replace', 17, 'i32.gt_u', 'i32.gt_s')], calls=[('$isqrt',[2147483647])], limit=2_000_000),
 'S1b': dict(prog='isqrt.rwat', spec=specs.ISQRT, edits=[('replace', 17, 'i32.gt_u', 'i32.gt_s')], calls=[('$isqrt',[2147395599])], limit=2_000_000),
 'S2': dict(prog='isqrt.rwat', spec=specs.ISQRT, edits=[('replace', 1, '(func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v <= n && n < (v + 1) * (v + 1)))', '(func $isqrt (param $n (i32 | 0 <= v)) (result (i32 | 0 <= v && v * v < n && n <= (v + 1) * (v + 1)))')],
            spec_override={1: {'requires': ISQRT[1]['requires'], 'ensures': lambda m,e,o: 0 <= e['result'] and e['result']**2 < e['$n'] <= (e['result']+1)**2}}, calls=[('$isqrt',[4])]),
 'S2ok': dict(prog='isqrt.rwat', spec=specs.ISQRT, edits=[], spec_override={1: {'requires': ISQRT[1]['requires'], 'ensures': lambda m,e,o: 0 <= e['result'] and e['result']**2 < e['$n'] <= (e['result']+1)**2}}, calls=[('$isqrt',[5])]),
 'S3': dict(prog='isqrt.rwat', spec=specs.ISQRT, edits=[('replace', 3, 'i32.const 0', 'i32.const 1')], calls=[('$isqrt',[0])]),
 'S3ok': dict(prog='isqrt.rwat', spec=specs.ISQRT, edits=[('replace', 3, 'i32.const 0', 'i32.const 1')], calls=[('$isqrt',[10])]),
 # ---- gcd
 'G1': dict(prog='gcd.rwat', spec=specs.GCD, edits=[('replace', 14, 'local.get $y', 'local.get $x')], calls=[('$gcd',[12, 8])]),
 'G1b': dict(prog='gcd.rwat', spec=specs.GCD, edits=[('replace', 14, 'local.get $y', 'local.get $x')], calls=[('$gcd',[0, 5])]),
 'G2': dict(prog='gcd.rwat', spec=specs.GCD, edits=[('delete', 14, 16), ('replace', 24, 'local.set $y', 'local.tee $y'), ('replace', 25, 'br $euclid', 'br_if $euclid')], calls=[('$gcd',[7, 0])]),
 'G2ok': dict(prog='gcd.rwat', spec=specs.GCD, edits=[('delete', 14, 16), ('replace', 24, 'local.set $y', 'local.tee $y'), ('replace', 25, 'br $euclid', 'br_if $euclid')], calls=[('$gcd',[12, 8])]),
 'G3': dict(prog='gcd.rwat', spec=specs.GCD, edits=[('replace', 12, '(@invariant 0 <= x && 0 <= y && gcd(x, y) == gcd(a, b))', '(@invariant 0 <= y && y <= x && gcd(x, y) == gcd(a, b))')],
            spec_override={12: lambda m,e: 0 <= e['$y'] <= e['$x'] and gcd_spec(e['$x'], e['$y']) == gcd_spec(e['$a'], e['$b'])}, calls=[('$gcd',[4, 6])]),
 # ---- powmod
 'M1': dict(prog='powmod.rwat', spec=specs.POWMOD, edits=[('delete', 7, 8)], calls=[('$pow_mod',[5, 0, 1])]),
 'M1b': dict(prog='powmod.rwat', spec=specs.POWMOD, edits=[('delete', 7, 8)], calls=[('$pow_mod',[5, 3, 1])]),
 'M2': dict(prog='powmod.rwat', spec=specs.POWMOD, edits=[('replace', 39, 'i32.rem_u', 'i32.rem_s')], calls=[('$pow_mod',[49999, 4, 50000])]),
 'M2b': dict(prog='powmod.rwat', spec=specs.POWMOD, edits=[('replace', 39, 'i32.rem_u', 'i32.rem_s')], calls=[('$pow_mod',[49999, 2, 50000])]),
 'M2ok': dict(prog='powmod.rwat', spec=specs.POWMOD, edits=[('replace', 39, 'i32.rem_u', 'i32.rem_s')], calls=[('$pow_mod',[46000, 77, 46341])]),
 # ---- hash
 'Ha': dict(prog='hash.rwat', spec=specs.HASH, edits=[('delete', 147, 148)], calls=[('$insert',[7,70]),('$insert',[15,150])]),
 'Hb': dict(prog='hash.rwat', spec=specs.HASH, edits=[('replace', 38, 'i32.lt_u', 'i32.ne')], calls=[('$insert',[3,30]),('$insert',[11,110]),('$delete',[3]),('$lookup',[11,-1])]),
 'Hb2': dict(prog='hash.rwat', spec=specs.HASH, edits=[('replace', 38, 'i32.lt_u', 'i32.ne')], calls=[('$insert',[3,30]),('$insert',[11,110]),('$delete',[3]),('$lookup',[11,-1]),('$insert',[11,111])]),
 'Hbp': dict(prog='hash.rwat', spec=specs.HASH, edits=[('replace', 99, 'i32.const 2', 'i32.const 0')], calls=[('$insert',[3,30]),('$insert',[11,110]),('$delete',[3]),('$lookup',[11,-1])]),
 'Hc': dict(prog='hash.rwat', spec=specs.HASH, edits=[('delete', 110, 123)], calls=[('$insert',[3,30]),('$insert',[3,31]),('$lookup',[3,-1])]),
 'Hd': dict(prog='hash.rwat', spec=specs.HASH, edits=[('replace', 125, 'i32.const 7', 'i32.const 8')], calls=[('$insert',[k,10*k]) for k in range(8)] + [('$lookup',[8,-1])]),
 'Hd_ok': dict(prog='hash.rwat', spec=specs.HASH, edits=[], calls=[('$insert',[k,10*k]) for k in range(8)] + [('$lookup',[8,-1])]),
 'Hb_ok': dict(prog='hash.rwat', spec=specs.HASH, edits=[], calls=[('$insert',[3,30]),('$insert',[11,110]),('$delete',[3]),('$lookup',[11,-1])]),
}
BUGS['S1cti'] = dict(prog='isqrt.rwat', spec=specs.ISQRT, edits=[('replace', 17, 'i32.gt_u', 'i32.gt_s'), ('replace', 3, 'i32.const 0', 'i32.const 46340')], calls=[('$isqrt',[2147483647])], limit=40)
