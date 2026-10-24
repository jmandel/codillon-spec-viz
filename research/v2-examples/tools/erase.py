#!/usr/bin/env python3
"""Erase Refined Codillon v2 text to plain WAT, line for line (design 16 §1.8).

usage: erase.py IN.wat [OUT.wat]      (writes to stdout if OUT is omitted)

The output has exactly as many lines as the input. Rules:
  - refinements (T | ...) -> T ; (fact ...) clauses deleted from headers and block lines
  - (local $h fact) -> comment
  - prove / lemma / unfold / assume, and local.get/set/tee of a fact local -> nop
  - every body line of a lemma (exported as lemma:<name> or axiom:<name>) -> nop
"""
import re
import sys

VALTYPES = ("i32", "i64", "f32", "f64")
PROOF_OPS = ("prove", "lemma", "unfold", "assume")


def split_comment(line):
    """Split at the first ';;' that is not inside a string literal."""
    in_str = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"' and (i == 0 or line[i - 1] != "\\"):
            in_str = not in_str
        elif not in_str and line.startswith(";;", i):
            return line[:i], line[i:]
        i += 1
    return line, ""


def match_paren(s, i):
    """s[i] == '('; return index just past the matching ')'."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "(":
            depth += 1
        elif s[j] == ")":
            depth -= 1
            if depth == 0:
                return j + 1
    return None  # unclosed (e.g. a "(func ..." header whose ")" is on a later line)


def head_tokens(s, i):
    return s[i + 1:].split(None, 2)


def erase_groups(code):
    """Delete (fact ...), (param $x (fact ...)), (result (fact ...)); turn (T | ...) into T."""
    out, i = [], 0
    while i < len(code):
        c = code[i]
        if c != "(":
            out.append(c)
            i += 1
            continue
        end = match_paren(code, i)
        if end is None:  # unclosed group: erase inside it, keep it open
            out.append("(" + erase_groups(code[i + 1:]))
            break
        group = code[i:end]
        inner = group[1:-1].strip()
        toks = inner.split()
        if toks and toks[0] == "fact":
            i = end
            continue
        if toks and toks[0] in ("param", "result"):
            rest = inner[len(toks[0]):].strip()
            if rest.startswith("$"):
                rest = rest.split(None, 1)[1] if len(rest.split(None, 1)) > 1 else ""
            if rest.startswith("(fact"):
                i = end
                continue
        if len(toks) >= 2 and toks[0] in VALTYPES and (toks[1].startswith("|") or toks[0].endswith("|")):
            out.append(toks[0])
            i = end
            continue
        # recurse into the group
        out.append("(" + erase_groups(group[1:-1]) + ")")
        i = end
    return "".join(out)


def tidy(s):
    s = s.rstrip()
    while "  )" in s:
        s = s.replace("  )", " )")
    return s


def erase(lines):
    out = []
    in_func = False
    lemma = False
    fact_locals = set()
    for raw in lines:
        line = raw.rstrip("\n")
        code, comment = split_comment(line)
        stripped = code.strip()
        indent = code[: len(code) - len(code.lstrip())]
        if stripped.startswith("(func"):
            in_func = True
            fact_locals = set()
            # lemma or axiom: marked by its export name (design 16 §1.7); its body is ghost code
            lemma = '(export "lemma:' in code or '(export "axiom:' in code
            # fact parameters are handles too (design 16 §1.5)
            for m in re.finditer(r"\(param\s+(\$[^\s()]+)\s+\(fact\b", code):
                fact_locals.add(m.group(1))
            out.append(tidy(erase_groups(code)) + ((" " + comment) if comment else ""))
            continue
        if in_func and stripped == ")":
            in_func = False
            lemma = False
            out.append(line)
            continue
        if in_func and stripped.startswith("(local"):
            toks = stripped[1:-1].split()
            if len(toks) == 3 and toks[2] == "fact":
                fact_locals.add(toks[1])
                out.append(indent + ";;~ " + line.strip())
                continue
            out.append(tidy(erase_groups(code)) + ((" " + comment) if comment else ""))
            continue
        if in_func and stripped and not stripped.startswith("("):
            toks = stripped.split()
            is_proof = toks[0] in PROOF_OPS or (
                toks[0] in ("local.get", "local.set", "local.tee") and len(toks) > 1 and toks[1] in fact_locals
            )
            if lemma or is_proof:
                out.append(indent + "nop ;;~ " + line.strip())
                continue
            out.append(tidy(erase_groups(code)) + ((" " + comment) if comment else ""))
            continue
        if not stripped:
            out.append(line)
            continue
        out.append(tidy(erase_groups(code)) + ((" " + comment) if comment else ""))
    return out


def main():
    src = open(sys.argv[1]).read().split("\n")
    if src and src[-1] == "":
        src = src[:-1]
    res = erase(src)
    assert len(res) == len(src), (len(res), len(src))
    text = "\n".join(res) + "\n"
    if len(sys.argv) > 2:
        open(sys.argv[2], "w").write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
