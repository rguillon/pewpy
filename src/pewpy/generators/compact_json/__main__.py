"""Rewrite JSON files compactly (see pewpy.generators.compact_json), to tidy hand-edited enemies and bosses.

uv run python -m pewpy.generators.compact_json data/enemies/*.json data/bosses/*.json
"""

import json
import sys
from pathlib import Path

from pewpy.generators.compact_json import compact_json


def main() -> None:
    """Rewrite the JSON files named on the command line compactly."""
    for name in sys.argv[1:]:
        path = Path(name)
        path.write_text(compact_json(json.loads(path.read_text())))


if __name__ == "__main__":
    main()
