"""
Shared helpers for exercise generators.

A generator module lives in a subject folder (e.g. ``math/``), is named
``NNN_name.py`` and exposes:

    SLUG   : short id, used for filenames and exercise ids
    TITLE  : human readable name
    build(rng) -> list[dict]   # rng is a seeded random.Random

Each dict returned by ``build`` is one exercise, produced with
``build_exercise(...)`` below. The runner (``run.py``) collects them all and
writes the data files that ``web/practice.html`` loads.

Math is rendered to standalone SVG images (via matplotlib mathtext) and embedded
as ``data:`` URIs, so the web app needs no JS libraries and no math fonts.
"""

import base64
import io
import json
import random
import re
from functools import lru_cache

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

matplotlib.rcParams["svg.fonttype"] = "path"      # embed glyphs as paths, no font needed
matplotlib.rcParams["mathtext.fontset"] = "cm"    # bundled Computer Modern

_STRIP = re.compile(
    rb"<\?xml[^>]*\?>\s*|<!DOCTYPE[^>]*>\s*|<!--.*?-->\s*|<metadata>.*?</metadata>\s*",
    re.S,
)


@lru_cache(maxsize=4096)
def render_math(tex: str, fontsize: int = 26) -> str:
    """Render a TeX math snippet to an SVG ``data:`` URI."""
    fig = plt.figure(figsize=(4, 1.4))
    fig.text(0.5, 0.5, f"${tex}$", fontsize=fontsize, ha="center", va="center")
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.06,
                transparent=True)
    plt.close(fig)
    svg = _STRIP.sub(b"", buf.getvalue())
    return "data:image/svg+xml;base64," + base64.b64encode(svg).decode("ascii")


def build_exercise(slug, idx, task, prompt_tex, correct_tex, distractor_texs):
    """Assemble one exercise dict: a task line, a prompt image and 4 options."""
    if len(distractor_texs) != 3:
        raise ValueError(f"{slug}[{idx}]: need exactly 3 distractors, got {len(distractor_texs)}")
    options = [{"img": render_math(correct_tex), "correct": True}]
    for d in distractor_texs:
        options.append({"img": render_math(d), "correct": False})
    return {
        "id": f"{slug}-{idx:02d}",
        "gen": slug,
        "task": task,
        "prompt": render_math(prompt_tex),
        "options": options,
    }


def run_standalone(g):
    """Tiny smoke test when a generator file is run directly."""
    rng = random.Random(g["SLUG"])
    ex = g["build"](rng)
    print(json.dumps(ex[0], indent=1)[:1200])
    print(f"... [{g['SLUG']}] built {len(ex)} exercises, "
          f"{len(ex[0]['options'])} options each")
