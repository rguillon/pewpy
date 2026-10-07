"""Every kind of enemy by name, from the JSON files (see spec.py).

The first enemies (`enemies/catalog.json`, 02-enemies-catalog.md), the second fleet (`enemies/fleet.json`,
02-enemies-fleet.md), the projectiles and mines other enemies launch (`enemies/projectiles.json`, 02-enemies.md), and
the bosses (02-enemies-bosses.md): the mini bosses, one halfway through each level (`bosses/mini_bosses.json`), and
the final bosses, one at the end of each level (`bosses/final_bosses.json`, made from their plans by
pewpy.makers.final_bosses).
They're all enemies, read the same way: the files only sort them. The Dev menu's model browser (pewpy.dev) changes
some of them: `reload_kinds` reads them again.
"""

from pewpy.game.enemies.mounts import model_mounts
from pewpy.game.enemies.spec import EnemySpec, load_enemy_specs

ENEMY_FILES = ("enemies/catalog.json", "enemies/fleet.json", "enemies/projectiles.json")

ENEMIES: dict[str, EnemySpec] = {kind: spec for name in ENEMY_FILES for kind, spec in load_enemy_specs(name).items()}
MINI_BOSSES_FILE = "bosses/mini_bosses.json"
FINAL_BOSSES_FILE = "bosses/final_bosses.json"
MINI_BOSSES = load_enemy_specs(MINI_BOSSES_FILE)
FINAL_BOSSES = load_enemy_specs(FINAL_BOSSES_FILE)
BOSSES: dict[str, EnemySpec] = {**MINI_BOSSES, **FINAL_BOSSES}
KINDS: dict[str, EnemySpec] = {**ENEMIES, **BOSSES}


def drawings(kind: str) -> set[str]:
    """Return the models an enemy of `kind` shows: its own, its parts', those of every enemy it launches or releases."""
    found: set[str] = set()
    seen: set[str] = set()
    waiting = [kind]
    while waiting:
        spec = KINDS[waiting.pop()]
        seen.add(spec.kind)
        found |= {spec.drawing, *(part.spec.drawing for part in spec.parts)}
        waiting += spec.released() - seen
    return found - {""}


def reload_kinds() -> None:
    """Read every kind again from the files (and the weapons on their models), in the same dictionaries."""
    model_mounts.cache_clear()
    for kinds, files in (
        (ENEMIES, ENEMY_FILES),
        (MINI_BOSSES, (MINI_BOSSES_FILE,)),
        (FINAL_BOSSES, (FINAL_BOSSES_FILE,)),
    ):
        read = {kind: spec for name in files for kind, spec in load_enemy_specs(name).items()}
        kinds.clear()
        kinds.update(read)
    BOSSES.clear()
    BOSSES.update({**MINI_BOSSES, **FINAL_BOSSES})
    KINDS.clear()
    KINDS.update({**ENEMIES, **BOSSES})
