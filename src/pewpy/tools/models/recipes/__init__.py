"""The recipes, one module per model, by the name of the model they make."""

from pewpy.tools.models.recipes.bomber import bomber
from pewpy.tools.models.recipes.drone import drone
from pewpy.tools.models.recipes.extra_life import extra_life
from pewpy.tools.models.recipes.gunship import gunship
from pewpy.tools.models.recipes.juggernaut import juggernaut
from pewpy.tools.models.recipes.phantom import phantom
from pewpy.tools.models.recipes.vanguard import vanguard
from pewpy.tools.models.registry import Recipe

__all__ = ["RECIPES"]

RECIPES: dict[str, Recipe] = {
    "player": vanguard,
    "player_heavy": juggernaut,
    "player_light": phantom,
    "drone": drone,
    "gunship": gunship,
    "bomber": bomber,
    "extra_life": extra_life,
}
