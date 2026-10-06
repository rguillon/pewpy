"""Writing a batch of boss candidates (see the package)."""

import argparse
import json
from pathlib import Path

from pewpy.data import SOURCE_DATA
from pewpy.tools.boss_candidates.selection import generate
from pewpy.tools.common import batch

DEFAULT_OUT = SOURCE_DATA / "models" / "candidates" / "bosses"


def write(out: Path, number: int, candidate: dict) -> None:
    """Write a candidate in one file: its core's drawing, its parts' drawings (each once) and where the parts go."""
    parts: dict[str, dict] = {}  # the same part drawing placed twice is written once
    names: dict[str, str] = {}  # a part's name, by its drawing written out
    layout = []
    for part_drawing, x, y in candidate["parts"]:
        text = json.dumps(part_drawing)
        if text not in names:
            names[text] = chr(ord("a") + len(names))
            parts[names[text]] = part_drawing
        layout.append({"part": names[text], "x": round(x, 2), "y": round(y, 2)})
    model = candidate["core"] | ({"parts": parts, "layout": layout} if parts else {})
    (out / f"{number:03d}.json").write_text(json.dumps(model, indent=2) + "\n")


def main() -> None:
    """Generate the bosses the command line asks for and write them."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=200, help="how many bosses to write (default 200)")
    parser.add_argument("--pool", type=int, default=6, help="how many generated for each one kept (default 6)")
    batch.options(parser, DEFAULT_OUT, "the game's boss candidates")
    args = parser.parse_args()
    seed, first = batch.start(args)
    for number, candidate in enumerate(generate(args.count, seed, args.pool), start=first):
        write(args.out, number, candidate)
    batch.report("boss candidates", args.count, first, args.out, seed)


if __name__ == "__main__":
    main()
