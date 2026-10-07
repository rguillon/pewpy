"""Write JSON compactly: each list or object on one line when it fits, else one item per line.

The tools write the game's enemies and bosses this way; to tidy hand-edited files:

    uv run python -m pewpy.makers.compact_json data/enemies/*.json data/bosses/*.json
"""

import json

WIDTH = 130  # columns: a bit wider than the code, so that a boss part or gun fits on a line


def compact_json(value: object) -> str:
    """`value` as JSON, indented by 2, its lists and objects on one line when they fit in WIDTH columns."""
    return _write(value, 0, 0) + "\n"


def _write(value: object, indent: int, column: int) -> str:
    """`value` starting at `column`, its lines indented by `indent` (room left for a comma after it)."""
    flat = json.dumps(value)
    if column + len(flat) < WIDTH or not isinstance(value, dict | list) or not value:
        return flat
    inner = " " * (indent + 2)
    if isinstance(value, dict):
        items = [
            f"{inner}{json.dumps(key)}: " + _write(item, indent + 2, len(inner) + len(json.dumps(key)) + 2)
            for key, item in value.items()
        ]
        return "{\n" + ",\n".join(items) + "\n" + " " * indent + "}"
    items = [inner + _write(item, indent + 2, len(inner)) for item in value]
    return "[\n" + ",\n".join(items) + "\n" + " " * indent + "]"
