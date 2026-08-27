"""
Task: Simplify an expression, giving the answer as a fraction in simplest form.
Example: (20 - 8) / (20 + 8)  ->  3/7

Variations:
- numerator and denominator each have 1..3 numbers joined by + or -
- numbers up to 32, composites preferred; each side evaluates to 1..60
- the unreduced fraction always has a common factor to cancel
Distractors: other reduced fractions with small numerator and denominator.
"""

import math
import pathlib
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import build_exercise, run_standalone  # noqa: E402

SLUG = "simplify_fraction"
TITLE = "Simplify fractions"
TASK = "Simplify, giving your answer as a fraction in its simplest form:"

COMPOSITES = [n for n in range(4, 33)
              if any(n % k == 0 for k in range(2, n))]


def _pick(rng):
    return rng.choice(COMPOSITES) if rng.random() < 0.8 else rng.randint(2, 32)


def _side(rng):
    """Return (tex, value) for one side of the fraction."""
    count = rng.randint(1, 3)
    nums = [_pick(rng)]
    signs = []
    for _ in range(count - 1):
        signs.append(rng.choice("+-"))
        nums.append(_pick(rng))
    value = nums[0]
    for s, n in zip(signs, nums[1:]):
        value += n if s == "+" else -n
    tex = str(nums[0])
    for s, n in zip(signs, nums[1:]):
        tex += s + str(n)
    return tex, value


def _distractors(rng, correct):
    seen = {(correct.numerator, correct.denominator)}
    out = []
    while len(out) < 3:
        f = Fraction(rng.randint(1, 32), rng.randint(2, 32))
        key = (f.numerator, f.denominator)
        if f.denominator == 1 or key in seen:
            continue
        seen.add(key)
        out.append(rf"\frac{{{f.numerator}}}{{{f.denominator}}}")
    return out


def _make(rng):
    for _ in range(400):
        num_tex, num_val = _side(rng)
        den_tex, den_val = _side(rng)
        if not (1 <= num_val <= 60 and 1 <= den_val <= 60):
            continue
        if math.gcd(num_val, den_val) == 1:
            continue
        answer = Fraction(num_val, den_val)
        if answer.denominator == 1 or answer.denominator > 32:
            continue
        prompt = rf"\frac{{{num_tex}}}{{{den_tex}}}"
        correct = rf"\frac{{{answer.numerator}}}{{{answer.denominator}}}"
        return prompt, correct, _distractors(rng, answer)
    raise RuntimeError("could not build a fraction to simplify")


def build(rng):
    seen, out = set(), []
    for _ in range(500):
        if len(out) == 10:
            break
        prompt, correct, distractors = _make(rng)
        if prompt in seen:
            continue
        seen.add(prompt)
        out.append(build_exercise(SLUG, len(out), TASK, prompt, correct, distractors))
    assert len(out) == 10, f"{SLUG}: only built {len(out)} exercises"
    return out


if __name__ == "__main__":
    run_standalone(globals())
