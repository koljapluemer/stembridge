"""
Task: Write a fraction as a recurring decimal.
Example: 1 2/3  ->  1.6 with a bar over the 6

Variations:
- whole part 0..9, proper fraction with denominator in {3, 6, 7, 9, 11}
- only keep fractions whose decimal actually recurs
Distractors: recurring-decimal answers of other fractions from the same pool.
"""

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import build_exercise, run_standalone  # noqa: E402

SLUG = "recurring_decimals"
TITLE = "Recurring decimals"
DENOMS = (3, 6, 7, 9, 11)
TASK = "Write as a recurring decimal:"


def long_division(n, d):
    """Return (whole, non_repeating, repeating) decimal digit strings."""
    whole, r = divmod(n, d)
    digits, seen = [], {}
    while r != 0 and r not in seen:
        seen[r] = len(digits)
        r *= 10
        digits.append(str(r // d))
        r %= d
    if r == 0:
        return str(whole), "".join(digits), ""
    start = seen[r]
    return str(whole), "".join(digits[:start]), "".join(digits[start:])


def prompt_tex(whole, num, den):
    frac = rf"\frac{{{num}}}{{{den}}}"
    return frac if whole == 0 else rf"{whole}\,{frac}"


def answer_tex(whole, nonrep, rep):
    return rf"{whole}.{nonrep}\overline{{{rep}}}"


def candidates():
    out = {}
    for den in DENOMS:
        for num in range(1, den):
            if math.gcd(num, den) != 1:
                continue
            for whole in range(0, 10):
                w, nonrep, rep = long_division(whole * den + num, den)
                if not rep:
                    continue
                out[answer_tex(w, nonrep, rep)] = (whole, num, den, w, nonrep, rep)
    return list(out.values())


def build(rng):
    pool = candidates()
    rng.shuffle(pool)
    chosen = pool[:10]
    answers = [answer_tex(c[3], c[4], c[5]) for c in pool]

    exercises = []
    for i, (whole, num, den, w, nonrep, rep) in enumerate(chosen):
        correct = answer_tex(w, nonrep, rep)
        wrong = [a for a in answers if a != correct]
        rng.shuffle(wrong)
        exercises.append(build_exercise(
            SLUG, i, TASK, prompt_tex(whole, num, den), correct, wrong[:3]))
    return exercises


if __name__ == "__main__":
    run_standalone(globals())
