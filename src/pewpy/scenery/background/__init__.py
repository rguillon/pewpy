"""Per-level scrolling backgrounds (placeholder until 05-visuals.md is decided).

Each level picks one kind of background (`background` in its JSON file), a preset of `levels/sceneries.json` whose
values it can change (`scenery`, see pewpy.scenery.params):

- space (behind the menus): stars, a few dim nebula clouds far away, a distant planet.
- city: flying high over a city, its ground scrolling slower than the enemies (see GROUND_SPEED): a grid of streets
  and buildings, lit windows.
- mountains, forest, savanna, farmland, salt_pan, badlands, refinery: more grounds, see pewpy.scenery.ground.

What a scenery has decides what's drawn: stars, nebulas, a distant planet, a ground (pewpy.scenery.ground).

Everything sits behind the play plane (depth = world Y, farther from the camera as it grows). The camera is
tilted, so a layer covers a bigger area the farther it is: `View.area(depth)` gives the rectangle to fill,
`View.parallax(depth)` how fast something there seems to move on screen compared with the play plane.
This package only moves things around (scenery.py: the layers of a level's scenery; stars.py, drift.py, and layers/:
each kind of drifting layer); view.py draws them. Kept dark and muted so bullets stay easy to see.
"""

from pewpy.scenery.background.drift import Drifter, DriftLayer
from pewpy.scenery.background.scenery import Scenery, View, mist_depths
from pewpy.scenery.background.stars import Starfield, StarLayer
from pewpy.scenery.ground.terrain import Area

__all__ = ["Area", "DriftLayer", "Drifter", "Scenery", "StarLayer", "Starfield", "View", "mist_depths"]
