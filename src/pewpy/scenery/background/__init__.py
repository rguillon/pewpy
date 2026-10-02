"""Per-level scrolling backgrounds (placeholder until 05-visuals.md is decided).

Each level picks one kind of background (`background` in its YAML file), a preset of `levels/sceneries.yaml` whose
values it can change (`scenery`, see pewpy.scenery.params):

- space: stars, a few dim nebula clouds far away, a distant planet.
- planet: flying high over a ground that scrolls slower than the enemies (see GROUND_SPEED).
- debris: stars and slowly tumbling asteroids at two depths.
- city: flying over a city: a grid of streets and buildings, lit windows.
- ocean: flying over a sea with islands; the water is a flat animated surface.
- desert, forest, canyon, geysers, farmland, pack_ice, volcano, swamp, clouds, refinery, mountains: more grounds, see
  pewpy.scenery.ground.

What a scenery has decides what's drawn: stars, nebulas, a distant planet, asteroids, a ground (pewpy.scenery.ground).

Everything sits behind the play plane (depth = world Y, farther from the camera as it grows). The camera is
tilted, so a layer covers a bigger area the farther it is: `View.area(depth)` gives the rectangle to fill,
`View.parallax(depth)` how fast something there seems to move on screen compared with the play plane.
This package only moves things around (scenery.py: the layers of a level's scenery; stars.py, drift.py, and layers/:
each kind of drifting layer); view.py draws them. Kept dark and muted so bullets stay easy to see.
"""

from pewpy.scenery.background.drift import Drifter, DriftLayer
from pewpy.scenery.background.layers.rocks import ROCK_SHAPES
from pewpy.scenery.background.scenery import Scenery, View, mist_depths
from pewpy.scenery.background.stars import Starfield, StarLayer
from pewpy.scenery.ground.terrain import Area

__all__ = ["ROCK_SHAPES", "Area", "DriftLayer", "Drifter", "Scenery", "StarLayer", "Starfield", "View", "mist_depths"]
