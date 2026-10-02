"""The base of every enemy, independent from rendering.

Each enemy moves itself in `update` and returns the bullets or enemies it creates.
"""

from dataclasses import dataclass
from typing import ClassVar

from pewpy import config
from pewpy.game.entities import Entity

TOP = config.PLAY_HEIGHT / 2
HALF_WIDTH = config.PLAY_WIDTH / 2
HIT_FLASH_TIME = 0.05


@dataclass(eq=False)
class Enemy(Entity):
    """Base enemy: flies with its velocity and never shoots. Subclasses add behavior in `behave`."""

    side_entry: ClassVar[bool] = False  # True: enters from the left/right edge instead of the top
    fire_interval: ClassVar[float] = 1.0
    drop_chance: ClassVar[float] = 0.0  # chance to leave a pickup when shot down
    rammable: ClassVar[bool] = True  # False: ramming it hurts the player but doesn't destroy it (bosses)
    ground: ClassVar[bool] = False  # True: sits or drives on the ground (levels over water or clouds have none)
    leaves_screen: ClassVar[bool] = True  # False: stays in the game even beyond the edges (bosses)
    faces_travel: ClassVar[bool] = False  # True: its model turns to point the way it flies (it doesn't only go down)

    health: float = 3.0
    points: int = 100
    fire_cooldown: float = 0.0
    flash_time: float = 0.0
    age: float = 0.0

    def update(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        self.age += dt
        self.flash_time = max(0.0, self.flash_time - dt)
        created = self.behave(dt, target, scroll_speed)
        self.move(dt)
        return created

    def behave(self, dt: float, target: Entity, scroll_speed: float) -> list[Entity]:
        return []

    @property
    def vulnerable(self) -> bool:
        return True

    def hit(self, damage: float) -> None:
        if not self.vulnerable:
            return
        self.health -= damage
        self.flash_time = HIT_FLASH_TIME
        if self.health <= 0:
            self.alive = False

    def on_destroyed(self) -> list["Enemy"]:
        """Enemies created when this one is shot down."""
        return []

    def wreckage(self) -> list["Enemy"]:
        """Enemies destroyed along with this one (a boss's parts), without points."""
        return []

    def explosions(self) -> list[tuple[float, float, float]]:
        """(x, y, size) of each explosion when it blows up."""
        return [(self.x, self.y, max(self.width, self.height))]

    @property
    def kind_name(self) -> str:
        """What it is, for the effects (debris colors): its class name, like "Drone"."""
        return type(self).__name__

    def enter_from_side(self, direction: int) -> None:
        """Set up movement for a side entry; `direction` is 1 when entering from the left, -1 from the right."""

    def appearance(self) -> str:
        """How to draw the enemy right now: "normal", "flash" (white), "hit" (brighter), "shield",
        "armored" (darker) or "hidden".
        """
        return "flash" if self.flash_time > 0 else "normal"

    @property
    def on_screen(self) -> bool:
        return self.y < TOP and abs(self.x) < HALF_WIDTH

    def _reloaded(self, dt: float) -> bool:
        """Count down to the next shot; True when it's time to fire (only while on screen)."""
        self.fire_cooldown -= dt
        if self.fire_cooldown <= 0 and self.on_screen:
            self.fire_cooldown = self.fire_interval
            return True
        return False
