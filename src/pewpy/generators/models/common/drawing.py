"""A 3D drawing from its cubes, and its weapons numbered (see pewpy.game.enemies.mounts)."""


def layered_drawing(cells: dict[tuple[int, int, int], str], width: int, height: int, colors: dict) -> dict:
    """Make a 3D drawing of `width` columns and `height` rows.

    Its layers from the top (nearest the camera) down, symmetric around the middle plane (the game puts the middle one
    on it), and the color of each character it uses.
    """
    extent = max(abs(layer) for _, _, layer in cells)
    layers = [
        ["".join(cells.get((x, y, layer), ".") for x in range(width)) for y in range(height)]
        for layer in range(-extent, extent + 1)
    ]
    used = set(cells.values())
    return {
        "layers": layers,
        "palette": {char: {"color": entry["color"]} for char, entry in colors.items() if char in used},
    }


# The order weapons are numbered in: by kind (so a description can map one gun per kind of shot), then left to right.
WEAPON_KINDS = ("gun", "gatling", "cannon", "turret", "flak", "missile", "laser")


def numbered_weapons(weapons: list[tuple[str, float, float]]) -> list[dict]:
    """Return a model's weapons, (kind, column, row) each, numbered from 1: by kind (see WEAPON_KINDS), then x."""
    ordered = sorted(weapons, key=lambda weapon: (WEAPON_KINDS.index(weapon[0]), weapon[1], weapon[2]))
    return [{"number": number, "kind": kind, "x": x, "y": y} for number, (kind, x, y) in enumerate(ordered, start=1)]
