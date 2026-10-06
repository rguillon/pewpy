"""Writing the final bosses (see the package)."""

import argparse
import json
from pathlib import Path

from pewpy.data import SOURCE_DATA as DATA
from pewpy.tools import final_bosses
from pewpy.tools.compact_json import compact_json
from pewpy.tools.final_bosses.plans import plan_boss
from pewpy.tools.final_bosses.writing import boss_json

PLANS = Path(__file__).with_name("plans.json")
OUT = DATA / "bosses" / "final_bosses.json"


def main() -> None:
    """Make the final bosses from their plans and write them."""
    parser = argparse.ArgumentParser(
        description=final_bosses.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--out", type=Path, default=OUT, help="where (default: the game's final bosses)")
    args = parser.parse_args()
    plans = json.loads(PLANS.read_text())
    bosses = {name: boss_json(plan_boss(plan), plan.get("note", "")) for name, plan in plans.items()}
    args.out.write_text(compact_json(bosses))
    print(f"{len(bosses)} final bosses written to {args.out}")


if __name__ == "__main__":
    main()
