"""Every kind of ground, each in its own module.

The landscapes (landscapes.py Landscape), the floras standing on some of them (landscapes.py Flora), the settlements
built on others (settlement.py Settlement), and the outposts any of them can have (outposts.py).

The level's scenery names them (`ground.landscape`, `flora.kind`, `settlement.kind`, see pewpy.scenery.params); these
registries give each name its generator. Independent from Panda3D.
"""

from pewpy.scenery.ground.kinds import (
    canyon,
    city,
    clouds,
    desert,
    farmland,
    forest,
    geysers,
    hills,
    islands,
    level_ground,
    mountains,
    outposts,
    pack_ice,
    refinery,
    rolling,
    swamp,
    volcano,
)
from pewpy.scenery.ground.landscapes import Flora, Landscape
from pewpy.scenery.ground.settlement import Settlement

__all__ = ["FLORAS", "LANDSCAPES", "SETTLEMENTS", "outposts"]

LANDSCAPES: dict[str, Landscape] = {
    "mountains": mountains.Mountains(),
    "rolling": rolling.Rolling(),
    "level_ground": level_ground.LevelGround(),
    "hills": hills.Hills(),
    "islands": islands.Islands(),
    "desert": desert.Desert(),
    "forest": forest.Forest(),
    "canyon": canyon.Canyon(),
    "pack_ice": pack_ice.PackIce(),
    "volcano": volcano.Volcano(),
    "swamp": swamp.Swamp(),
    "clouds": clouds.Clouds(),
    "geysers": geysers.Geysers(),
}
FLORAS: dict[str, Flora] = {"palms": desert.Palms(), "dead_trees": swamp.DeadTrees(), "snags": geysers.Snags()}
SETTLEMENTS: dict[str, Settlement] = {
    "city": city.City(),
    "refinery": refinery.Refinery(),
    "farmland": farmland.Farmland(),
}
