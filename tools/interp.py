"""Tiny line-oriented interpreter for the Codillon-style refined WAT subset used in 03-sample-programs.
Line numbers are stable (1-based) so traces/obligations can cite them."""
import re, struct, copy

MASK = 0xFFFFFFFF
def s32(x):
    x &= MASK
    return x - (1 << 32) if x & 0x80000000 else x
def u32(x): return x & MASK

class Trap(Exception): pass
class SpecFail(Exception): pass
class StepLimit(Exception): pass

def parse_header(text):
    name = re.match(r'\(func (\$\w+)', text).group(1)
    params = re.findall(r'\(param (\$\w+)', text)
    has_result = '(result' in text
    if_result = None
    return name, params, has_result

class Func:
    def __init__(self, name, params, has_result, header_line):
        self.name, self.params, self.has_result, self.header_line = name, params, has_result, header_line
        self.lines = []  # (lineno, text)
        self.locals = []
        self.ghost_locals = []

def load_program(src):
    lines = src.split('\n')
    funcs = {}; globals_ = {}; ghost_globals = []
    cur = None
    for i, raw in enumerate(lines, 1):
        t = raw.strip()
        if not t: continue
        if t.startswith('(func '):
            name, params, hr = parse_header(t)
            cur = Func(name, params, hr, i); funcs[name] = cur; continue
        if t == ')' and cur is not None:
            cur.end_line = i; cur = None; continue
        if cur is None:
            m = re.match(r'\(global (\$\w+) \(mut i32\) \(i32.const (-?\d+)\)\)', t)
            if m: globals_[m.group(1)] = int(m.group(2))
            continue
        m = re.match(r'\(local (\$\w+) i32\)', t)
        if m: cur.locals.append(m.group(1)); continue
        m = re.match(r'\(@ghost local (\$\w+)', t)
        if m: cur.ghost_locals.append(m.group(1)); cur.lines.append((i, t)); continue
        cur.lines.append((i, t))
    for f in funcs.values():
        # matching structure
        f.match = {}; f.else_of = {}; stack = []
        for idx, (ln, t) in enumerate(f.lines):
            op = t.split()[0]
            if op in ('block', 'loop', 'if'): stack.append(idx)
            elif op == 'else': f.else_of[stack[-1]] = idx
            elif op == 'end': f.match[stack.pop()] = idx
        assert not stack, f.name
    return funcs, globals_

class Machine:
    def __init__(self, src, spec=None, step_limit=3_000_000, record=True):
        self.funcs, g = load_program(src)
        self.globals = dict(g)
        self.mem = bytearray(65536)
        self.spec = spec or {}
        self.step = 0
        self.step_limit = step_limit
        self.record = record
        self.log = []      # per-step records
        self.checks = []   # spec check events
        self.ghost = {'M': {}}
        self.fail_fast = False
    # memory
    def load(self, addr):
        a = u32(addr)
        if a + 4 > len(self.mem): raise Trap('out of bounds memory access')
        return struct.unpack_from('<i', self.mem, a)[0]
    def store(self, addr, val):
        a = u32(addr)
        if a + 4 > len(self.mem): raise Trap('out of bounds memory access')
        struct.pack_into('<i', self.mem, a, s32(val))
    def check(self, ln, kind, ok, env, detail='', step=None):
        ev = {'step': self.step if step is None else step, 'line': ln, 'kind': kind, 'ok': bool(ok)}
        if detail: ev['detail'] = detail
        self.checks.append(ev)
        if not ok and self.fail_fast: raise SpecFail(ev)
    def snap(self, fname, ln, text, stack, env):
        if not self.record: return
        self.log.append({'step': self.step, 'func': fname, 'line': ln, 'instr': text,
                         'stack': list(stack), 'locals': {k: v for k, v in env.items()},
                         'globals': dict(self.globals), 'M': dict(self.ghost['M']),
                         **({'slots': self.mem_view(self)} if getattr(self, 'mem_view', None) else {})})
    def tick(self):
        self.step += 1
        if self.step > self.step_limit: raise StepLimit(self.step)

    def call(self, name, args):
        f = self.funcs[name]
        env = {p: s32(a) for p, a in zip(f.params, args)}
        for l in f.locals: env[l] = 0
        for l in f.ghost_locals: env[l] = 0
        old = {'M': dict(self.ghost['M']), 'globals': dict(self.globals)}
        depth = getattr(self, 'depth', 0)
        # top-level call: requires attach to the callee's first step; nested: to the caller's `call` (enter) step
        rstep = self.step + 1 if depth == 0 else self.step
        sp = self.spec.get(f.header_line)
        if sp and 'requires' in sp:
            self.check(f.header_line, 'requires', sp['requires'](self, env), env, step=rstep)
        for (ln, t) in f.lines:
            if t.startswith('(@requires'):
                p = self.spec.get(ln)
                if p: self.check(ln, 'requires', p(self, env), env, step=rstep)
        self.depth = depth + 1
        try:
            result = self.run(f, env)
        finally:
            self.depth = depth
        env['result'] = result
        # nested: ensures attach to the caller's `call` (return) step, which is the next tick; top-level: last step
        estep = self.step if depth == 0 else self.step + 1
        if sp and 'ensures' in sp:
            self.check(f.header_line, 'ensures', sp['ensures'](self, env, old), env, step=estep)
        for (ln, t) in f.lines:
            if t.startswith('(@ensures'):
                p = self.spec.get(ln)
                if p: self.check(ln, 'ensures', p(self, env, old), env, step=estep)
        return result

    def run(self, f, env):
        L = f.lines; stack = []; ctrl = []; pc = 0
        measures = {}
        def arrive_loop(idx):
            # evaluate invariants/decreases directly following the loop line
            j = idx + 1
            while j < len(L) and L[j][1].startswith('(@'):
                ln, t = L[j]
                p = self.spec.get(ln)
                if t.startswith('(@invariant') and p:
                    self.check(ln, 'invariant', p(self, env), env)
                elif t.startswith('(@decreases') and p:
                    m = p(self, env)
                    prev = measures.get(ln)
                    ok = m >= 0 and (prev is None or m < prev)
                    self.check(ln, 'decreases', ok, env, detail=f'measure={m} prev={prev}')
                    measures[ln] = m
                j += 1
            return j
        while pc < len(L):
            ln, t = L[pc]
            if t.startswith('(@'):
                p = self.spec.get(ln)
                if t.startswith('(@assert') and p: self.check(ln, 'assert', p(self, env), env)
                elif t.startswith('(@ghost') and p and ':=' in t: p(self, env)
                pc += 1; continue
            parts = t.split(';;')[0].split()
            op = parts[0]; arg = parts[1] if len(parts) > 1 else None
            if op == 'end':
                ctrl.pop(); pc += 1; continue
            if op == 'else':
                pc = f.match[ctrl[-1][2]]; continue
            self.cur = (f.name, ln, t, list(stack), dict(env))
            self.tick()
            if op in ('block', 'loop'):
                label = arg if arg and arg.startswith('$') else None
                ctrl.append((op, label, pc, len(stack), 0))
                self.snap(f.name, ln, t, stack, env)
                pc += 1
                if op == 'loop': pc = arrive_loop(pc - 1)
                continue
            if op == 'if':
                c = stack.pop()
                arity = 1 if '(result' in t else 0
                ctrl.append(('if', None, pc, len(stack), arity))
                self.snap(f.name, ln, t, stack, env)
                if c: pc += 1
                elif pc in f.else_of: pc = f.else_of[pc] + 1
                else: pc = f.match[pc]
                continue
            if op in ('br', 'br_if'):
                take = True
                if op == 'br_if': take = stack.pop() != 0
                self.snap(f.name, ln, t, stack, env)
                if not take: pc += 1; continue
                k = len(ctrl) - 1
                while ctrl[k][1] != arg: k -= 1
                kind, label, start, height, arity = ctrl[k]
                if kind == 'loop':
                    del stack[height:]; del ctrl[k + 1:]
                    pc = arrive_loop(start)
                else:
                    keep = stack[len(stack) - arity:] if arity else []
                    del stack[height:]; stack.extend(keep)
                    del ctrl[k:]
                    pc = f.match[start] + 1
                continue
            if op == 'return':
                self.snap(f.name, ln, t, stack, env)
                return stack[-1] if f.has_result else None
            if op == 'unreachable':
                self.snap(f.name, ln, t, stack, env)
                raise Trap('unreachable')
            if op == 'call':
                f2 = self.funcs[arg]
                n = len(f2.params)
                args = stack[len(stack) - n:]; del stack[len(stack) - n:]
                self.snap(f.name, ln, t + '  (enter)', stack, env)
                r = self.call(arg, args)
                if f2.has_result: stack.append(r)
                self.tick()
                self.snap(f.name, ln, t + '  (return)', stack, env)
                pc += 1; continue
            # straight-line ops
            if op == 'local.get': stack.append(env[arg])
            elif op == 'local.set': env[arg] = stack.pop()
            elif op == 'local.tee': env[arg] = stack[-1]
            elif op == 'global.get': stack.append(self.globals[arg])
            elif op == 'global.set': self.globals[arg] = stack.pop()
            elif op == 'i32.const': stack.append(s32(int(arg)))
            elif op == 'drop': stack.pop()
            elif op == 'i32.eqz': stack.append(1 if stack.pop() == 0 else 0)
            elif op == 'i32.load':
                off = int(arg.split('=')[1]) if arg else 0
                a = stack.pop(); stack.append(self.load(u32(a) + off))
            elif op == 'i32.store':
                off = int(arg.split('=')[1]) if arg else 0
                v = stack.pop(); a = stack.pop(); self.store(u32(a) + off, v)
            else:
                b = stack.pop(); a = stack.pop()
                ua, ub = u32(a), u32(b)
                if op == 'i32.add': r = a + b
                elif op == 'i32.sub': r = a - b
                elif op == 'i32.mul': r = a * b
                elif op == 'i32.and': r = a & b
                elif op == 'i32.or': r = a | b
                elif op == 'i32.shr_s': r = a >> (ub & 31)
                elif op == 'i32.shr_u': r = ua >> (ub & 31)
                elif op in ('i32.rem_u', 'i32.rem_s', 'i32.div_u'):
                    if b == 0: raise Trap('integer divide by zero')
                    if op == 'i32.rem_u': r = ua % ub
                    elif op == 'i32.div_u': r = ua // ub
                    else:
                        q = abs(a) // abs(b); r = abs(a) - q * abs(b); r = -r if a < 0 else r
                elif op == 'i32.eq': r = int(a == b)
                elif op == 'i32.ne': r = int(a != b)
                elif op == 'i32.lt_s': r = int(a < b)
                elif op == 'i32.lt_u': r = int(ua < ub)
                elif op == 'i32.gt_s': r = int(a > b)
                elif op == 'i32.gt_u': r = int(ua > ub)
                elif op == 'i32.ge_s': r = int(a >= b)
                elif op == 'i32.ge_u': r = int(ua >= ub)
                else: raise NotImplementedError(op)
                stack.append(s32(r))
            self.snap(f.name, ln, t, stack, env)
            pc += 1
        return stack[-1] if f.has_result else None

def apply_edits(src, edits):
    lines = src.split('\n')
    for e in edits:
        if e[0] == 'replace':
            _, ln, old, new = e
            assert lines[ln - 1].strip() == old, (ln, lines[ln - 1], old)
            ind = lines[ln - 1][:len(lines[ln - 1]) - len(lines[ln - 1].lstrip())]
            lines[ln - 1] = ind + new
        elif e[0] == 'delete':
            _, a, b = e
            for ln in range(a, b + 1): lines[ln - 1] = ''
        elif e[0] == 'insert_after':
            _, ln, new = e
            ind = lines[ln - 1][:len(lines[ln - 1]) - len(lines[ln - 1].lstrip())]
            lines[ln - 1] = lines[ln - 1] + '\n' + ind + new  # NOTE: shifts later numbering
    return '\n'.join(lines)
