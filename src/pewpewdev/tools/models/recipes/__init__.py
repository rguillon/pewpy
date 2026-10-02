"""The recipes, one module per model, by the name of the model they make."""

from pewpewdev.tools.models.recipes.bomber import bomber
from pewpewdev.tools.models.recipes.drone import drone
from pewpewdev.tools.models.recipes.extra_life import extra_life
from pewpewdev.tools.models.recipes.gunship import gunship
from pewpewdev.tools.models.recipes.juggernaut import juggernaut
from pewpewdev.tools.models.recipes.phantom import phantom
from pewpewdev.tools.models.recipes.vanguard import vanguard
from pewpewdev.tools.models.registry import Recipe

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
