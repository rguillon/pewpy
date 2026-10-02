"""Writing the final bosses (see the package)."""

import argparse
from pathlib import Path

from pewpewdev.paths import DATA
from pewpewdev.tools import final_bosses
from pewpewdev.tools.final_bosses.plans import plan_boss
from pewpewdev.tools.final_bosses.writing import boss_data
from pewpewdev.yamlfiles import dump_yaml
from pewpy.data import read_yaml

PLANS = Path(__file__).with_name("plans.yaml")
OUT = DATA / "bosses" / "final_bosses.yaml"


def main() -> None:
    """Make the final bosses from their plans and write them."""
    parser = argparse.ArgumentParser(
        description=final_bosses.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--out", type=Path, default=OUT, help="where (default: the game's final bosses)")
    args = parser.parse_args()
    plans = read_yaml(PLANS)
    bosses = {name: boss_data(plan_boss(plan), plan.get("note", "")) for name, plan in plans.items()}
    args.out.write_text(dump_yaml(bosses))
    print(f"{len(bosses)} final bosses written to {args.out}")


if __name__ == "__main__":
    main()
