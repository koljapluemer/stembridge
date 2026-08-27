"""
Run every generator and write the data files consumed by web/practice.html.

    cd cms && uv run generators/run.py

Outputs (all under web/data/):
    exercises.js   window.EXERCISES = [...]   <- the app loads only this
    <slug>.json    one file per generator, for inspection
    index.json     manifest: generators, counts, subject, timestamp
"""

import datetime as dt
import importlib.util
import json
import pathlib
import random
import sys

GEN_DIR = pathlib.Path(__file__).resolve().parent
ROOT = GEN_DIR.parents[1]
DATA_DIR = ROOT / "web" / "data"


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    sys.path.insert(0, str(GEN_DIR))
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(GEN_DIR.glob("*/[0-9]*.py"))
    if not files:
        sys.exit("no generators found under generators/*/")

    all_exercises = []
    manifest = []
    for path in files:
        mod = load_module(path)
        rng = random.Random(mod.SLUG)          # stable output per generator
        exercises = mod.build(rng)
        (DATA_DIR / f"{mod.SLUG}.json").write_text(
            json.dumps(exercises, indent=1), encoding="utf-8")
        all_exercises.extend(exercises)
        manifest.append({
            "slug": mod.SLUG,
            "title": mod.TITLE,
            "subject": path.parent.name,
            "count": len(exercises),
            "file": f"{mod.SLUG}.json",
        })
        print(f"  {mod.SLUG:<20} {len(exercises):>3} exercises")

    (DATA_DIR / "exercises.js").write_text(
        "window.EXERCISES = " + json.dumps(all_exercises) + ";\n", encoding="utf-8")
    (DATA_DIR / "index.json").write_text(json.dumps({
        "generated": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "total": len(all_exercises),
        "generators": manifest,
    }, indent=1), encoding="utf-8")

    print(f"\n{len(all_exercises)} exercises from {len(manifest)} generators "
          f"-> {DATA_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
