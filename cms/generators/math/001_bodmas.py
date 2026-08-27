"""
Task: Find the value of an arithmetic expression, following BODMAS.
Example: 10 - 10 / 2 + 2 x 2

Variations:
- 3 to 5 numbers (leaves), operators + - x /
- built from a random expression tree so every division is exact
- final value kept in 0..50
Distractors: values you get by breaking BODMAS
- evaluating strictly left to right
- doing + and - before x and /
- the correct value nudged by a small amount
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import build_exercise, run_standalone  # noqa: E402

SLUG = "bodmas"
TITLE = "BODMAS"
TASK = "Find the value of:"

PREC = {"+": 1, "-": 1, "*": 2, "/": 2}
SYM = {"+": "+", "-": "-", "*": r"\times", "/": r"\div"}


def _tree(rng, k):
    """Random expression tree with k leaves; ops chosen so division is exact."""
    if k == 1:
        v = rng.randint(1, 9)
        return ("num", v), v
    lk = rng.randint(1, k - 1)
    left, lv = _tree(rng, lk)
    right, rv = _tree(rng, k - lk)
    choices = ["+", "-", "*"]
    if rv != 0 and lv % rv == 0:
        choices.append("/")
    op = rng.choice(choices)
    v = {"+": lv + rv, "-": lv - rv, "*": lv * rv,
         "/": lv // rv if rv else 0}[op]
    return (op, left, right), v


def _walk(node):
    yield node
    if node[0] != "num":
        yield from _walk(node[1])
        yield from _walk(node[2])


def _render(node, parent_prec=0, right=False, parent_op=None):
    if node[0] == "num":
        return str(node[1])
    op = node[0]
    p = PREC[op]
    s = (f"{_render(node[1], p, False, op)} {SYM[op]} "
         f"{_render(node[2], p, True, op)}")
    if p < parent_prec or (p == parent_prec and right and parent_op in ("-", "/")):
        return rf"\left({s}\right)"
    return s


def _lex(tex):
    """Token list of the *displayed* expression (minimal parentheses)."""
    tex = (tex.replace(r"\left(", " ( ").replace(r"\right)", " ) ")
              .replace(r"\times", " * ").replace(r"\div", " / "))
    return tex.split()


def _eval(tokens, prec):
    """Evaluate a token list. prec=None -> strict left to right."""
    pos = 0

    def group():
        nonlocal pos
        vals, ops = [], []
        while pos < len(tokens):
            t = tokens[pos]
            pos += 1
            if t == "(":
                vals.append(group())
            elif t == ")":
                break
            elif t in ("+", "-", "*", "/"):
                ops.append(t)
            else:
                vals.append(float(t))
        return combine(vals, ops)

    def combine(vals, ops):
        if prec is None:
            acc = vals[0]
            for i, op in enumerate(ops):
                acc = _apply(acc, op, vals[i + 1])
            return acc
        vals, ops = vals[:], ops[:]
        for level in prec:
            i = 0
            while i < len(ops):
                if ops[i] in level:
                    vals[i] = _apply(vals[i], ops[i], vals[i + 1])
                    del vals[i + 1]
                    del ops[i]
                else:
                    i += 1
        return vals[0]

    return group()


def _apply(a, op, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    return a / b


def _node_value(node):
    if node[0] == "num":
        return node[1]
    a, b = _node_value(node[1]), _node_value(node[2])
    return _apply(a, node[0], b) if node[0] != "/" else a // b


def _make(rng):
    for _ in range(2000):
        tree, val = _tree(rng, rng.randint(3, 5))
        ops = {n[0] for n in _walk(tree) if n[0] != "num"}
        if not (ops & {"*", "/"} and ops & {"+", "-"}):
            continue                       # every question must exercise precedence
        if not (0 <= val <= 50):
            continue
        if any(not (-30 <= _node_value(n) <= 120) for n in _walk(tree)):
            continue                       # keep intermediate numbers sane
        tex = _render(tree)
        toks = _lex(tex)

        # distractors from breaking BODMAS: no precedence, and reversed precedence
        wrong = set()
        for prec in (None, [("+", "-"), ("*", "/")]):
            try:
                w = _eval(toks, prec)
            except ZeroDivisionError:
                continue
            if abs(w - round(w)) < 1e-9:
                wrong.add(int(round(w)))
        wrong.discard(val)
        wrong = [w for w in wrong if -30 <= w <= 120]
        if not wrong:
            continue                       # no interesting distractor -> try again

        pool = sorted(wrong)
        rng.shuffle(pool)
        for delta in (1, -1, 2, -2, 3, -3, 4, 5):   # pad with near misses
            if len(pool) >= 3:
                break
            cand = val + delta
            if cand != val and cand >= 0 and cand not in pool:
                pool.append(cand)
        return tex, str(val), [str(x) for x in pool[:3]]
    raise RuntimeError("could not build a BODMAS expression")


def build(rng):
    seen, out = set(), []
    for _ in range(500):
        if len(out) == 10:
            break
        tex, correct, distractors = _make(rng)
        if tex in seen:
            continue
        seen.add(tex)
        out.append(build_exercise(SLUG, len(out), TASK, tex, correct, distractors))
    assert len(out) == 10, f"{SLUG}: only built {len(out)} exercises"
    return out


if __name__ == "__main__":
    run_standalone(globals())
