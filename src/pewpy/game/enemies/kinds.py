"""Every kind of enemy by name, from the YAML files (see spec.py).

The first enemies (`enemies/catalog.yaml`, 02-enemies-catalog.md), the second fleet (`enemies/fleet.yaml`,
02-enemies-fleet.md), the projectiles and mines other enemies launch (`enemies/projectiles.yaml`, 02-enemies.md), and
the bosses (02-enemies-bosses.md): the mini bosses, one halfway through each level (`bosses/mini_bosses.yaml`), and
the final bosses, one at the end of each level (`bosses/final_bosses.yaml`, made by pewpewdev/tools/final_bosses/).
They're all enemies.
"""

from pewpy.game.enemies.spec import EnemySpec, load_enemy_specs

ENEMY_FILES = ("enemies/catalog.yaml", "enemies/fleet.yaml", "enemies/projectiles.yaml")

ENEMIES: dict[str, EnemySpec] = {kind: spec for name in ENEMY_FILES for kind, spec in load_enemy_specs(name).items()}
MINI_BOSSES = load_enemy_specs("bosses/mini_bosses.yaml")
FINAL_BOSSES = load_enemy_specs("bosses/final_bosses.yaml")
BOSSES: dict[str, EnemySpec] = {**MINI_BOSSES, **FINAL_BOSSES}
KINDS: dict[str, EnemySpec] = {**ENEMIES, **BOSSES}
