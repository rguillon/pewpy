"""Writing a batch of boss candidates (see the package)."""

import argparse
import json
from pathlib import Path

from pewpy.data import SOURCE_DATA
from pewpy.tools.boss_candidates.selection import generate
from pewpy.tools.common import batch

DEFAULT_OUT = SOURCE_DATA / "models" / "candidates" / "bosses"


def write(out: Path, number: int, candidate: dict) -> None:
    """Write a candidate: its core's drawing, its parts' drawings (each once) and where the parts go."""
    name = f"{number:03d}"
    (out / f"{name}.json").write_text(json.dumps(candidate["core"], indent=2) + "\n")
    drawings: dict[str, str] = {}  # the same part drawing placed twice is written once
    layout = []
    for part_drawing, x, y in candidate["parts"]:
        text = json.dumps(part_drawing, indent=2) + "\n"
        if text not in drawings:
            drawings[text] = f"{name}_{chr(ord('a') + len(drawings))}"
            (out / f"{drawings[text]}.json").write_text(text)
        layout.append({"drawing": drawings[text], "x": round(x, 2), "y": round(y, 2)})
    (out / f"{name}.parts.json").write_text(json.dumps({"parts": layout}, indent=2) + "\n")


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
