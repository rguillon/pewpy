"""Every kind of enemy by name, from the JSON files (see spec.py): the first enemies (`enemies/catalog.json`,
02-enemies-catalog.md), the second fleet (`enemies/fleet.json`, 02-enemies-fleet.md), the projectiles and mines other
enemies launch (`enemies/projectiles.json`, 02-enemies.md), and the bosses (02-enemies-bosses.md): the mini bosses, one
halfway through each level (`bosses/mini_bosses.json`), and the final bosses, one at the end of each level
(`bosses/final_bosses.json`, made by pewpewdev/tools/final_bosses/). They're all enemies.
"""

from pewpy.game.enemies.spec import EnemySpec, load_enemy_specs

ENEMY_FILES = ("enemies/catalog.json", "enemies/fleet.json", "enemies/projectiles.json")

ENEMIES: dict[str, EnemySpec] = {kind: spec for name in ENEMY_FILES for kind, spec in load_enemy_specs(name).items()}
MINI_BOSSES = load_enemy_specs("bosses/mini_bosses.json")
FINAL_BOSSES = load_enemy_specs("bosses/final_bosses.json")
BOSSES: dict[str, EnemySpec] = {**MINI_BOSSES, **FINAL_BOSSES}
KINDS: dict[str, EnemySpec] = {**ENEMIES, **BOSSES}
