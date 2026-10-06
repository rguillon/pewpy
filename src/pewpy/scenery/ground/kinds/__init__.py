"""Every kind of ground, each in its own module.

The landscapes (landscapes.py Landscape), the floras standing on some of them (landscapes.py Flora), the settlements
built on others (settlement.py Settlement), and the outposts any of them can have (outposts.py).

The level's scenery names them (`ground.landscape`, `flora.kind`, `settlement.kind`, see pewpy.scenery.params); these
registries give each name its generator. Independent from Panda3D.
"""

from pewpy.scenery.ground.kinds import (
    badlands,
    city,
    farmland,
    forest,
    level_ground,
    mountains,
    outposts,
    refinery,
    rolling,
    salt_pan,
    savanna,
)
from pewpy.scenery.ground.landscapes import Flora, Landscape
from pewpy.scenery.ground.settlement import Settlement

__all__ = ["FLORAS", "LANDSCAPES", "SETTLEMENTS", "outposts"]

LANDSCAPES: dict[str, Landscape] = {
    "mountains": mountains.Mountains(),
    "rolling": rolling.Rolling(),
    "level_ground": level_ground.LevelGround(),
    "forest": forest.Forest(),
    "salt_pan": salt_pan.SaltPan(),
    "savanna": savanna.Savanna(),
    "badlands": badlands.Badlands(),
}
FLORAS: dict[str, Flora] = {"acacias": savanna.Acacias()}
SETTLEMENTS: dict[str, Settlement] = {
    "city": city.City(),
    "refinery": refinery.Refinery(),
    "farmland": farmland.Farmland(),
}
