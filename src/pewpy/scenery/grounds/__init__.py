"""Every kind of ground, each in its own module: the landscapes (landscapes.py Landscape), the floras standing on some
of them (landscapes.py Flora) and the settlements built on others (settlement.py Settlement).

The level's scenery names them (`ground.landscape`, `flora.kind`, `settlement.kind`, see params.py); these registries
give each name its generator. Independent from Panda3D.
"""

from pewpy.scenery.grounds import (
    canyon,
    city,
    clouds,
    desert,
    farmland,
    forest,
    hills,
    islands,
    level_ground,
    mountains,
    pack_ice,
    refinery,
    rolling,
    swamp,
    volcano,
)
from pewpy.scenery.landscapes import Flora, Landscape
from pewpy.scenery.settlement import Settlement

__all__ = ["FLORAS", "LANDSCAPES", "SETTLEMENTS"]

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
}
FLORAS: dict[str, Flora] = {"palms": desert.Palms(), "dead_trees": swamp.DeadTrees()}
SETTLEMENTS: dict[str, Settlement] = {
    "city": city.City(),
    "refinery": refinery.Refinery(),
    "farmland": farmland.Farmland(),
}
