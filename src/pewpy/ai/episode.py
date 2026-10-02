"""Playing a level with a pilot, headless, as fast as the computer goes.

Training plays with one life (an episode ends at the first death) and grades the run (`fitness`); rating plays by
the game's rules (its lives, restarting the level after each death) and only asks whether the level was cleared.
"""

from dataclasses import dataclass

from pewpy.ai.brain import Brain
from pewpy.ai.pilot import Pilot
from pewpy.game.boss_catalog import BOSSES
from pewpy.game.level import Level
from pewpy.game.player import SHIPS
from pewpy.game.world import World

DT = 1 / 60
OVERTIME = 90.0  # seconds per boss before giving up (an AI that only dodges a boss forever)

# Grading a training run, as a weighted sum: how far into the level it got (in seconds: surviving is the first
# thing to learn), its score, how much of the final boss it destroyed, and clearing the level (more with health left).
PER_SECOND = 1.0
PER_POINT = 1 / 250
BOSS_DAMAGE = 60.0
CLEARED = 150.0
HEALTH_LEFT = 30.0


@dataclass(frozen=True)
class Outcome:
    cleared: bool
    time: float  # seconds played, every life included
    progress: float  # how far into the level (its last life), from 0 to 1 (the final boss's arrival), then to 2 (the
    # final boss destroyed)
    score: int
    lives_lost: int
    health_left: float  # share of the last life's health

    @property
    def fitness(self) -> float:
        bonus = CLEARED + HEALTH_LEFT * self.health_left if self.cleared else 0.0
        return PER_SECOND * self.time + PER_POINT * self.score + BOSS_DAMAGE * max(self.progress - 1, 0.0) + bonus


def boss_time(level: Level) -> float:
    """When the final boss comes, on the waves' clock (see World.wave_time)."""
    return max((wave.time for wave in level.waves), default=0.0)


def play(level: Level, brain: Brain, ship: str, seed: int, lives: int = 1) -> Outcome:
    """Play `level` with `brain` flying `ship` until it is cleared, the lives are gone or time is up."""
    world = World(level, seed=seed, lives=lives, ship=SHIPS[ship])
    pilot = Pilot(brain)
    arrival = boss_time(level)
    limit = arrival + OVERTIME * max(sum(wave.enemy in BOSSES for wave in level.waves), 1)
    boss_seen = 0.0
    played = 0.0
    while not world.completed and not world.game_over and world.time < limit:
        world.update(DT, pilot.fly(world))
        played += DT
        boss = world.boss
        final = not any(spawn.enemy in BOSSES for spawn in world.pending_spawns)
        if boss is not None and final:
            boss_seen = max(boss_seen, 1.0 - boss.health_fraction)
    if world.completed:
        progress = 2.0
    else:
        reached = min(world.wave_time / arrival, 1.0) if arrival else 1.0
        progress = reached + boss_seen if reached >= 1.0 or boss_seen else reached
    return Outcome(
        cleared=world.completed,
        time=played,
        progress=progress,
        score=world.score,
        lives_lost=lives - max(world.lives, 0),
        health_left=max(world.player.health, 0.0) / world.ship.health if world.completed else 0.0,
    )
