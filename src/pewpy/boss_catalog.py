"""Every boss: one at the end of each level (02-enemies.md, "Bosses"). Placeholders, see decisions.md.

Sizes are hitboxes, and have the shape of the boss's drawing in `models/` (the model is drawn at that size with
square voxels). Parts are at (x, y) from the core's middle.
"""

from pewpy.bosses import CORE, BossSpec, Gun, PartSpec, Phase

BOSSES: dict[str, BossSpec] = {
    # 1-1: a satellite, no parts.
    "sentinel": BossSpec(
        name="SENTINEL",
        drawing="sentinel",
        width=0.26,
        height=0.2,
        health=60.0,
        points=1500,
        phases=(
            Phase(guns=((CORE, Gun("fan", interval=1.6, speed=0.45, count=3, spread=20)),), sway=0.1, until_below=0.5),
            Phase(
                guns=(
                    (CORE, Gun("aimed", interval=2.0, speed=0.55, volley=3)),
                    (CORE, Gun("ring", interval=3.0, speed=0.35, count=8, turn=22, delay=1.0)),
                ),
                sway=0.14,
            ),
        ),
    ),
    # 1-2: a red manta fighter, no parts.
    "prowler": BossSpec(
        name="PROWLER",
        drawing="prowler",
        width=0.34,
        height=0.2,
        health=75.0,
        points=1800,
        phases=(
            Phase(
                guns=((CORE, Gun("aimed", interval=1.5, speed=0.55, count=3, spread=12)),), sway=0.14, until_below=0.5
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.8, speed=0.4, count=8, turn=22)),
                    (CORE, Gun("aimed", interval=1.2, speed=0.6, delay=0.6)),
                ),
                sway=0.2,
            ),
        ),
    ),
    # 1-3: a mining ship with two drills; armored until they're gone.
    "rockbreaker": BossSpec(
        name="ROCKBREAKER",
        drawing="rockbreaker",
        width=0.26,
        height=0.22,
        health=60.0,
        points=2000,
        parts=(
            PartSpec("left drill", "rock_drill", -0.2, -0.04, 0.1, 0.16, 25.0, 400),
            PartSpec("right drill", "rock_drill", 0.2, -0.04, 0.1, 0.16, 25.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left drill", Gun("aimed", interval=1.8, speed=0.55, volley=2)),
                    ("right drill", Gun("aimed", interval=1.8, speed=0.55, volley=2, delay=0.9)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left drill", "right drill"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=1.6, speed=0.45, count=5, spread=16)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, volley=2, delay=0.8)),
                ),
                sway=0.15,
            ),
        ),
    ),
    # 1-4: a round siege pod, no parts, three phases on its health.
    "siege_pod": BossSpec(
        name="SIEGE POD",
        drawing="siege_pod",
        width=0.3,
        height=0.3,
        health=110.0,
        points=2500,
        phases=(
            Phase(guns=((CORE, Gun("fan", interval=1.8, speed=0.45, count=5, spread=15)),), sway=0.1, until_below=0.66),
            Phase(
                guns=((CORE, Gun("ring", interval=0.12, speed=0.45, count=2, turn=11)),), sway=0.12, until_below=0.33
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.6, speed=0.4, count=12, turn=15)),
                    (CORE, Gun("aimed", interval=2.2, speed=0.55, style="heavy", delay=0.8)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 1-5: two side guns that can be left alive: the core isn't armored.
    "twin_fang": BossSpec(
        name="TWIN FANG",
        drawing="twin_fang",
        width=0.24,
        height=0.26,
        health=90.0,
        points=2600,
        parts=(
            PartSpec("left gun", "fang_gun", -0.19, -0.02, 0.1, 0.2, 30.0, 500),
            PartSpec("right gun", "fang_gun", 0.19, -0.02, 0.1, 0.2, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left gun", Gun("aimed", interval=1.6, speed=0.6, volley=2)),
                    ("right gun", Gun("aimed", interval=1.6, speed=0.6, volley=2, delay=0.8)),
                    (CORE, Gun("fan", interval=2.2, speed=0.45, count=3, spread=25, delay=1.1)),
                ),
                sway=0.12,
                until_below=0.5,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.15, speed=0.42, count=3, turn=12)),
                    ("left gun", Gun("fan", interval=2.0, speed=0.5, count=3, spread=15)),
                    ("right gun", Gun("fan", interval=2.0, speed=0.5, count=3, spread=15, delay=1.0)),
                ),
                sway=0.16,
            ),
        ),
    ),
    # 1-6: a relay station with two dishes; armored until they're gone.
    "relay_array": BossSpec(
        name="RELAY ARRAY",
        drawing="relay_array",
        width=0.3,
        height=0.24,
        health=110.0,
        points=3000,
        parts=(
            PartSpec("left dish", "relay_dish", -0.26, 0.06, 0.14, 0.14, 35.0, 600),
            PartSpec("right dish", "relay_dish", 0.26, 0.06, 0.14, 0.14, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left dish", Gun("ring", interval=2.2, speed=0.38, count=8, turn=20)),
                    ("right dish", Gun("ring", interval=2.2, speed=0.38, count=8, turn=-20, delay=1.1)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.6, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left dish", "right dish"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.1, speed=0.48, count=2, turn=10)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=3, spread=25, style="heavy", delay=1.0)),
                ),
                sway=0.14,
            ),
        ),
    ),
    # 1-7: a mine carrier with two mine pods; armored, then two phases on its health.
    "mine_mother": BossSpec(
        name="MINE MOTHER",
        drawing="mine_mother",
        width=0.34,
        height=0.28,
        health=130.0,
        points=3500,
        parts=(
            PartSpec("left pod", "mine_pod", -0.27, -0.08, 0.12, 0.12, 35.0, 600),
            PartSpec("right pod", "mine_pod", 0.27, -0.08, 0.12, 0.12, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left pod", Gun("fan", interval=1.8, speed=0.5, count=3, spread=20)),
                    ("right pod", Gun("fan", interval=1.8, speed=0.5, count=3, spread=20, delay=0.9)),
                    (CORE, Gun("aimed", interval=2.4, speed=0.5, style="heavy", delay=1.2)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left pod", "right pod"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.6, speed=0.4, count=10, turn=18)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.65, volley=3, delay=0.8)),
                ),
                sway=0.14,
                until_below=0.5,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.13, speed=0.45, count=3, turn=-12)),
                    (CORE, Gun("fan", interval=2.2, speed=0.45, count=5, spread=18, style="heavy", delay=1.0)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 1-8, Orbit's boss: no parts, two phases by health.
    "warden": BossSpec(
        name="WARDEN",
        drawing="warden",
        width=0.46,
        height=0.3,
        health=140.0,
        points=5000,
        phases=(
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=1.6, speed=0.5, count=5, spread=18)),
                    (CORE, Gun("aimed", interval=2.2, speed=0.7, count=2, spread=8, volley=3, delay=0.8)),
                ),
                sway=0.12,
                until_below=0.55,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.14, speed=0.45, count=3, turn=13)),
                    (CORE, Gun("aimed", interval=1.8, speed=0.6, style="heavy", delay=0.5)),
                ),
                sway=0.2,
            ),
        ),
    ),
    # 2-1: a threshing machine, no parts.
    "thresher": BossSpec(
        name="THRESHER",
        drawing="thresher",
        width=0.3,
        height=0.22,
        health=70.0,
        points=1800,
        phases=(
            Phase(guns=((CORE, Gun("fan", interval=1.4, speed=0.45, count=4, spread=14)),), sway=0.1, until_below=0.5),
            Phase(
                guns=(
                    (CORE, Gun("aimed", interval=1.5, speed=0.55, count=3, spread=10)),
                    (CORE, Gun("fan", interval=3.0, speed=0.35, count=7, spread=12, delay=0.8)),
                ),
                sway=0.14,
            ),
        ),
    ),
    # 2-2: a scarecrow with two straw arms; armored until they're gone.
    "scarecrow": BossSpec(
        name="SCARECROW",
        drawing="scarecrow",
        width=0.2,
        height=0.26,
        health=80.0,
        points=2200,
        parts=(
            PartSpec("left arm", "straw_arm", -0.19, 0.04, 0.16, 0.09, 25.0, 400),
            PartSpec("right arm", "straw_arm", 0.19, 0.04, 0.16, 0.09, 25.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left arm", Gun("fan", interval=1.7, speed=0.45, count=3, spread=18)),
                    ("right arm", Gun("fan", interval=1.7, speed=0.45, count=3, spread=18, delay=0.85)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.55, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left arm", "right arm"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=2.0, speed=0.4, count=12, turn=15)),
                    (CORE, Gun("aimed", interval=1.8, speed=0.6, volley=3, delay=0.9)),
                ),
                sway=0.15,
            ),
        ),
    ),
    # 2-3: a beetle with two horns in front; armored until they're gone.
    "beetle": BossSpec(
        name="BEETLE",
        drawing="beetle",
        width=0.28,
        height=0.3,
        health=90.0,
        points=2400,
        parts=(
            PartSpec("left horn", "beetle_horn", -0.07, -0.2, 0.08, 0.14, 30.0, 500),
            PartSpec("right horn", "beetle_horn", 0.07, -0.2, 0.08, 0.14, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left horn", Gun("aimed", interval=1.5, speed=0.6, volley=2)),
                    ("right horn", Gun("aimed", interval=1.5, speed=0.6, volley=2, delay=0.75)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=5, spread=18, delay=1.2)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left horn", "right horn"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.12, speed=0.45, count=2, turn=13)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.55, style="heavy", delay=0.8)),
                ),
                sway=0.14,
            ),
        ),
    ),
    # 2-4: windmill sails, no parts: spirals, three phases on its health.
    "windmill": BossSpec(
        name="WINDMILL",
        drawing="windmill",
        width=0.3,
        height=0.3,
        health=110.0,
        points=2600,
        phases=(
            Phase(
                guns=((CORE, Gun("ring", interval=0.14, speed=0.42, count=2, turn=12)),), sway=0.08, until_below=0.66
            ),
            Phase(guns=((CORE, Gun("ring", interval=0.2, speed=0.4, count=4, turn=-9)),), sway=0.1, until_below=0.33),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.4, speed=0.42, count=12, turn=15)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.55, style="heavy", delay=0.7)),
                ),
                sway=0.16,
            ),
        ),
    ),
    # 2-5: a walking barn with two silos; armored until they're gone.
    "silo_walker": BossSpec(
        name="SILO WALKER",
        drawing="silo_walker",
        width=0.26,
        height=0.24,
        health=100.0,
        points=2800,
        parts=(
            PartSpec("left silo", "silo", -0.21, 0.04, 0.12, 0.19, 35.0, 600),
            PartSpec("right silo", "silo", 0.21, 0.04, 0.12, 0.19, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left silo", Gun("ring", interval=1.8, speed=0.4, count=6, turn=15)),
                    ("right silo", Gun("ring", interval=1.8, speed=0.4, count=6, turn=-15, delay=0.9)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, volley=2, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left silo", "right silo"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=1.3, speed=0.5, count=5, spread=15, sweep=25)),
                    (CORE, Gun("ring", interval=2.5, speed=0.38, count=10, delay=1.2)),
                ),
                sway=0.15,
            ),
        ),
    ),
    # 2-6: a hornet queen with two wings; armored, then two phases on its health.
    "hornet_queen": BossSpec(
        name="HORNET QUEEN",
        drawing="hornet_queen",
        width=0.22,
        height=0.3,
        health=110.0,
        points=3000,
        parts=(
            PartSpec("left wing", "hornet_wing", -0.19, 0.06, 0.16, 0.18, 30.0, 500),
            PartSpec("right wing", "hornet_wing", 0.19, 0.06, 0.16, 0.18, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left wing", Gun("fan", interval=1.2, speed=0.5, count=3, spread=12, sweep=25)),
                    ("right wing", Gun("fan", interval=1.2, speed=0.5, count=3, spread=12, sweep=25, delay=0.6)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, delay=1.0)),
                ),
                sway=0.14,
                armored=True,
                until_destroyed=("left wing", "right wing"),
            ),
            Phase(guns=((CORE, Gun("ring", interval=0.14, speed=0.45, count=3, turn=12)),), sway=0.16, until_below=0.5),
            Phase(
                guns=(
                    (CORE, Gun("aimed", interval=1.4, speed=0.65, count=5, spread=8)),
                    (CORE, Gun("ring", interval=2.0, speed=0.4, count=14, turn=13, delay=0.7)),
                ),
                sway=0.2,
            ),
        ),
    ),
    # 2-7: a red tractor with two wheels and a plow: wheels, then the plow, then the core.
    "tractor_king": BossSpec(
        name="TRACTOR KING",
        drawing="tractor_king",
        width=0.3,
        height=0.28,
        health=130.0,
        points=3500,
        parts=(
            PartSpec("left wheel", "tractor_wheel", -0.23, 0.0, 0.12, 0.19, 30.0, 500),
            PartSpec("right wheel", "tractor_wheel", 0.23, 0.0, 0.12, 0.19, 30.0, 500),
            PartSpec("plow", "tractor_plow", 0.0, -0.19, 0.22, 0.08, 40.0, 700),
        ),
        phases=(
            Phase(
                guns=(
                    ("left wheel", Gun("aimed", interval=1.6, speed=0.6, volley=2)),
                    ("right wheel", Gun("aimed", interval=1.6, speed=0.6, volley=2, delay=0.8)),
                    ("plow", Gun("fan", interval=2.0, speed=0.45, count=5, spread=15, delay=0.4)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left wheel", "right wheel"),
            ),
            Phase(
                guns=(
                    ("plow", Gun("ring", interval=1.6, speed=0.4, count=10, turn=18)),
                    (CORE, Gun("fan", interval=2.2, speed=0.4, count=3, spread=30, style="heavy", delay=0.8)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("plow",),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.1, speed=0.48, count=2, turn=11)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.65, volley=3, delay=0.8)),
                ),
                sway=0.16,
            ),
        ),
    ),
    # 2-8, Heartland's boss: two cannons; the core is armored until both are gone.
    "harvester": BossSpec(
        name="HARVESTER",
        drawing="harvester",
        width=0.34,
        height=0.26,
        health=100.0,
        points=6000,
        parts=(
            PartSpec("left cannon", "harvester_cannon", -0.26, 0.02, 0.14, 0.18, 40.0, 800),
            PartSpec("right cannon", "harvester_cannon", 0.26, 0.02, 0.14, 0.18, 40.0, 800),
        ),
        phases=(
            Phase(
                guns=(
                    ("left cannon", Gun("aimed", interval=1.8, speed=0.65, volley=3)),
                    ("right cannon", Gun("aimed", interval=1.8, speed=0.65, volley=3, delay=0.9)),
                    (CORE, Gun("fan", interval=2.5, speed=0.4, count=3, spread=25, style="heavy", delay=1.2)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left cannon", "right cannon"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=2.2, speed=0.4, count=14, turn=13)),
                    (CORE, Gun("aimed", interval=1.4, speed=0.6, count=3, spread=12, delay=0.7)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 3-1: a crab with two claws; armored until they're gone.
    "crab": BossSpec(
        name="CRAB",
        drawing="crab",
        width=0.26,
        height=0.2,
        health=70.0,
        points=2000,
        parts=(
            PartSpec("left claw", "crab_claw", -0.2, -0.08, 0.12, 0.14, 25.0, 400),
            PartSpec("right claw", "crab_claw", 0.2, -0.08, 0.12, 0.14, 25.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left claw", Gun("aimed", interval=1.6, speed=0.55, count=2, spread=10)),
                    ("right claw", Gun("aimed", interval=1.6, speed=0.55, count=2, spread=10, delay=0.8)),
                    (CORE, Gun("fan", interval=2.2, speed=0.4, count=3, spread=20, delay=1.1)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left claw", "right claw"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.8, speed=0.4, count=10, turn=18)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.6, volley=3, delay=0.8)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 3-2: a jellyfish, no parts: rings.
    "jellyfish": BossSpec(
        name="JELLYFISH",
        drawing="jellyfish",
        width=0.26,
        height=0.3,
        health=90.0,
        points=2200,
        phases=(
            Phase(guns=((CORE, Gun("ring", interval=1.6, speed=0.38, count=10, turn=18)),), sway=0.08, until_below=0.5),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.14, speed=0.42, count=2, turn=12)),
                    (CORE, Gun("ring", interval=3.0, speed=0.3, count=16, delay=1.5)),
                ),
                sway=0.12,
            ),
        ),
    ),
    # 3-3: a frigate with two deck guns; armored until they're gone.
    "frigate": BossSpec(
        name="FRIGATE",
        drawing="frigate",
        width=0.22,
        height=0.36,
        health=90.0,
        points=2400,
        parts=(
            PartSpec("left gun", "deck_gun", -0.17, 0.02, 0.1, 0.1, 30.0, 500),
            PartSpec("right gun", "deck_gun", 0.17, 0.02, 0.1, 0.1, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left gun", Gun("aimed", interval=2.0, speed=0.6, volley=3)),
                    ("right gun", Gun("aimed", interval=2.0, speed=0.6, volley=3, delay=1.0)),
                    (CORE, Gun("fan", interval=2.4, speed=0.45, count=5, spread=12, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left gun", "right gun"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=1.8, speed=0.45, count=3, spread=30, style="heavy")),
                    (CORE, Gun("aimed", interval=1.3, speed=0.6, count=3, spread=10, delay=0.6)),
                ),
                sway=0.14,
            ),
        ),
    ),
    # 3-4: a manta ray, no parts: sweeping fans, three phases on its health.
    "manta": BossSpec(
        name="MANTA",
        drawing="manta",
        width=0.4,
        height=0.23,
        health=110.0,
        points=2600,
        phases=(
            Phase(
                guns=((CORE, Gun("fan", interval=1.2, speed=0.5, count=5, spread=12, sweep=35)),),
                sway=0.12,
                until_below=0.66,
            ),
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=0.5, speed=0.45, count=3, spread=20, sweep=45)),
                    (CORE, Gun("aimed", interval=1.8, speed=0.6, delay=0.9)),
                ),
                sway=0.14,
                until_below=0.33,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.1, speed=0.5, count=2, turn=9)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=5, spread=18, style="heavy", delay=1.0)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 3-5: an ice fortress with two ice cannons; armored until they're gone.
    "iceberg_fort": BossSpec(
        name="ICEBERG FORT",
        drawing="iceberg_fort",
        width=0.3,
        height=0.26,
        health=110.0,
        points=2800,
        parts=(
            PartSpec("left cannon", "ice_cannon", -0.23, 0.02, 0.12, 0.15, 35.0, 600),
            PartSpec("right cannon", "ice_cannon", 0.23, 0.02, 0.12, 0.15, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left cannon", Gun("ring", interval=1.6, speed=0.42, count=6, turn=10)),
                    ("right cannon", Gun("ring", interval=1.6, speed=0.42, count=6, turn=-10, delay=0.8)),
                    (CORE, Gun("aimed", interval=2.2, speed=0.5, style="heavy", delay=1.1)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left cannon", "right cannon"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.14, speed=0.45, count=3, turn=12)),
                    (CORE, Gun("fan", interval=2.0, speed=0.5, count=5, spread=15, delay=1.0)),
                ),
                sway=0.12,
            ),
        ),
    ),
    # 3-6: a kraken with four tentacles; armored until they're all gone, then two phases on its health.
    "kraken": BossSpec(
        name="KRAKEN",
        drawing="kraken",
        width=0.26,
        height=0.26,
        health=130.0,
        points=3200,
        parts=(
            PartSpec("left tentacle", "kraken_tentacle", -0.2, -0.13, 0.08, 0.21, 20.0, 400),
            PartSpec("right tentacle", "kraken_tentacle", 0.2, -0.13, 0.08, 0.21, 20.0, 400),
            PartSpec("left inner tentacle", "kraken_tentacle", -0.09, -0.21, 0.08, 0.21, 20.0, 400),
            PartSpec("right inner tentacle", "kraken_tentacle", 0.09, -0.21, 0.08, 0.21, 20.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left tentacle", Gun("fan", interval=1.6, speed=0.5, count=3, spread=15)),
                    ("right tentacle", Gun("fan", interval=1.6, speed=0.5, count=3, spread=15, delay=0.8)),
                    ("left inner tentacle", Gun("aimed", interval=1.4, speed=0.6, delay=0.4)),
                    ("right inner tentacle", Gun("aimed", interval=1.4, speed=0.6, delay=1.1)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left tentacle", "right tentacle", "left inner tentacle", "right inner tentacle"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.6, speed=0.4, count=12, turn=15)),
                    (CORE, Gun("aimed", interval=1.5, speed=0.6, volley=2, delay=0.8)),
                ),
                sway=0.14,
                until_below=0.5,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.1, speed=0.5, count=2, turn=-10)),
                    (CORE, Gun("fan", interval=2.6, speed=0.4, count=5, spread=18, style="heavy", delay=1.0)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 3-7: a battleship with four turrets and a bow gun: turrets, then the bow gun, then the core.
    "dreadnought": BossSpec(
        name="DREADNOUGHT",
        drawing="dreadnought",
        width=0.24,
        height=0.37,
        health=150.0,
        points=4000,
        parts=(
            PartSpec("left front turret", "naval_turret", -0.18, -0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("right front turret", "naval_turret", 0.18, -0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("left rear turret", "naval_turret", -0.26, 0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("right rear turret", "naval_turret", 0.26, 0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("bow gun", "bow_gun", 0.0, -0.24, 0.08, 0.11, 35.0, 700),
        ),
        phases=(
            Phase(
                guns=(
                    ("left front turret", Gun("aimed", interval=1.8, speed=0.6, volley=2)),
                    ("right front turret", Gun("aimed", interval=1.8, speed=0.6, volley=2, delay=0.9)),
                    ("left rear turret", Gun("fan", interval=2.2, speed=0.45, count=3, spread=20, delay=0.4)),
                    ("right rear turret", Gun("fan", interval=2.2, speed=0.45, count=3, spread=20, delay=1.5)),
                    ("bow gun", Gun("aimed", interval=2.6, speed=0.5, style="heavy", delay=1.2)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left front turret", "right front turret", "left rear turret", "right rear turret"),
            ),
            Phase(
                guns=(
                    ("bow gun", Gun("fan", interval=1.0, speed=0.5, count=5, spread=12, sweep=30)),
                    (CORE, Gun("ring", interval=2.0, speed=0.4, count=10, turn=18, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("bow gun",),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.12, speed=0.45, count=3, turn=11)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.65, count=3, spread=10, delay=0.8)),
                ),
                sway=0.15,
            ),
        ),
    ),
    # 3-8, Waters' boss: two fins, then two phases of the core alone.
    "leviathan": BossSpec(
        name="LEVIATHAN",
        drawing="leviathan",
        width=0.3,
        height=0.36,
        health=120.0,
        points=7000,
        parts=(
            PartSpec("left fin", "leviathan_fin", -0.24, 0.04, 0.16, 0.22, 45.0, 900),
            PartSpec("right fin", "leviathan_fin", 0.24, 0.04, 0.16, 0.22, 45.0, 900),
        ),
        phases=(
            Phase(
                guns=(
                    ("left fin", Gun("fan", interval=1.1, speed=0.5, count=4, spread=12, sweep=30)),
                    ("right fin", Gun("fan", interval=1.1, speed=0.5, count=4, spread=12, sweep=30, delay=0.55)),
                    (CORE, Gun("aimed", interval=2.4, speed=0.55, style="heavy", delay=1.0)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left fin", "right fin"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.1, speed=0.5, count=2, turn=9)),
                    (CORE, Gun("aimed", interval=1.2, speed=0.65, delay=0.6)),
                ),
                sway=0.14,
                until_below=0.45,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.6, speed=0.42, count=16, turn=11)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.7, volley=3, delay=0.8)),
                ),
                sway=0.2,
            ),
        ),
    ),
    # 4-1: a scorpion with two pincers; armored until they're gone.
    "scorpion": BossSpec(
        name="SCORPION",
        drawing="scorpion",
        width=0.24,
        height=0.24,
        health=70.0,
        points=2000,
        parts=(
            PartSpec("left pincer", "scorpion_pincer", -0.17, -0.12, 0.1, 0.16, 25.0, 400),
            PartSpec("right pincer", "scorpion_pincer", 0.17, -0.12, 0.1, 0.16, 25.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left pincer", Gun("aimed", interval=1.6, speed=0.55, volley=2)),
                    ("right pincer", Gun("aimed", interval=1.6, speed=0.55, volley=2, delay=0.8)),
                    (CORE, Gun("fan", interval=2.2, speed=0.45, count=3, spread=18, delay=1.1)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left pincer", "right pincer"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("aimed", interval=1.2, speed=0.6, count=3, spread=12)),
                    (CORE, Gun("ring", interval=2.4, speed=0.4, count=8, turn=22, delay=0.6)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 4-2: a whirlwind of sand, no parts: spirals, three phases on its health.
    "dust_devil": BossSpec(
        name="DUST DEVIL",
        drawing="dust_devil",
        width=0.28,
        height=0.28,
        health=100.0,
        points=2500,
        phases=(
            Phase(
                guns=((CORE, Gun("ring", interval=0.12, speed=0.42, count=2, turn=12)),), sway=0.12, until_below=0.66
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.14, speed=0.44, count=3, turn=-14)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, delay=1.0)),
                ),
                sway=0.16,
                until_below=0.33,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.16, speed=0.42, count=4, turn=9)),
                    (CORE, Gun("ring", interval=2.2, speed=0.35, count=12, delay=1.1)),
                ),
                sway=0.2,
            ),
        ),
    ),
    # 4-3: a sandworm's head with two body segments; armored until they're gone.
    "sandworm": BossSpec(
        name="SANDWORM",
        drawing="sandworm",
        width=0.24,
        height=0.24,
        health=90.0,
        points=2400,
        parts=(
            PartSpec("left segment", "worm_segment", -0.2, 0.08, 0.14, 0.14, 30.0, 500),
            PartSpec("right segment", "worm_segment", 0.2, 0.08, 0.14, 0.14, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left segment", Gun("ring", interval=2.0, speed=0.38, count=8, turn=20)),
                    ("right segment", Gun("ring", interval=2.0, speed=0.38, count=8, turn=-20, delay=1.0)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, volley=3, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left segment", "right segment"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=1.8, speed=0.45, count=7, spread=12)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.55, style="heavy", delay=0.8)),
                ),
                sway=0.15,
            ),
        ),
    ),
    # 4-4: a fort on a mesa with two turrets; armored until they're gone.
    "mesa_fort": BossSpec(
        name="MESA FORT",
        drawing="mesa_fort",
        width=0.32,
        height=0.23,
        health=110.0,
        points=2800,
        parts=(
            PartSpec("left turret", "colossus_turret", -0.25, -0.06, 0.12, 0.12, 30.0, 500),
            PartSpec("right turret", "colossus_turret", 0.25, -0.06, 0.12, 0.12, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left turret", Gun("aimed", interval=1.5, speed=0.6, count=2, spread=10)),
                    ("right turret", Gun("aimed", interval=1.5, speed=0.6, count=2, spread=10, delay=0.75)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=3, spread=25, style="heavy", delay=1.2)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left turret", "right turret"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.8, speed=0.4, count=14, turn=13)),
                    (CORE, Gun("fan", interval=1.4, speed=0.5, count=5, spread=15, sweep=30, delay=0.7)),
                ),
                sway=0.12,
            ),
        ),
    ),
    # 4-5: a lava golem with two fists; armored, then two phases on its health.
    "lava_golem": BossSpec(
        name="LAVA GOLEM",
        drawing="lava_golem",
        width=0.28,
        height=0.3,
        health=140.0,
        points=3400,
        parts=(
            PartSpec("left fist", "golem_fist", -0.22, -0.1, 0.12, 0.14, 35.0, 600),
            PartSpec("right fist", "golem_fist", 0.22, -0.1, 0.12, 0.14, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left fist", Gun("fan", interval=2.0, speed=0.42, count=3, spread=20, style="heavy")),
                    ("right fist", Gun("fan", interval=2.0, speed=0.42, count=3, spread=20, style="heavy", delay=1.0)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.6, delay=0.5)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left fist", "right fist"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.5, speed=0.4, count=12, turn=15)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.65, volley=3, delay=0.7)),
                ),
                sway=0.12,
                until_below=0.5,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.12, speed=0.45, count=3, turn=13)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=5, spread=18, style="heavy", delay=1.0)),
                ),
                sway=0.16,
            ),
        ),
    ),
    # 4-6: a vulture with two wings; armored, then two phases on its health.
    "vulture": BossSpec(
        name="VULTURE",
        drawing="vulture",
        width=0.2,
        height=0.27,
        health=110.0,
        points=3000,
        parts=(
            PartSpec("left wing", "vulture_wing", -0.21, 0.05, 0.2, 0.13, 35.0, 600),
            PartSpec("right wing", "vulture_wing", 0.21, 0.05, 0.2, 0.13, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left wing", Gun("fan", interval=1.3, speed=0.5, count=4, spread=12, sweep=25)),
                    ("right wing", Gun("fan", interval=1.3, speed=0.5, count=4, spread=12, sweep=25, delay=0.65)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, delay=1.0)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left wing", "right wing"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("aimed", interval=1.4, speed=0.6, count=5, spread=10)),
                    (CORE, Gun("ring", interval=2.2, speed=0.4, count=10, turn=18, delay=0.7)),
                ),
                sway=0.16,
                until_below=0.5,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.09, speed=0.5, count=2, turn=10)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.55, volley=2, style="heavy", delay=1.0)),
                ),
                sway=0.2,
            ),
        ),
    ),
    # 4-7: an oil rig with two furnaces and two cannons: furnaces, then cannons, then the core.
    "magma_rig": BossSpec(
        name="MAGMA RIG",
        drawing="magma_rig",
        width=0.3,
        height=0.28,
        health=150.0,
        points=4000,
        parts=(
            PartSpec("left furnace", "furnace", -0.24, 0.1, 0.12, 0.14, 30.0, 500),
            PartSpec("right furnace", "furnace", 0.24, 0.1, 0.12, 0.14, 30.0, 500),
            PartSpec("left cannon", "rig_cannon", -0.36, -0.06, 0.1, 0.16, 30.0, 500),
            PartSpec("right cannon", "rig_cannon", 0.36, -0.06, 0.1, 0.16, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left furnace", Gun("ring", interval=2.0, speed=0.38, count=8, turn=15)),
                    ("right furnace", Gun("ring", interval=2.0, speed=0.38, count=8, turn=-15, delay=1.0)),
                    ("left cannon", Gun("aimed", interval=1.6, speed=0.65, delay=0.5)),
                    ("right cannon", Gun("aimed", interval=1.6, speed=0.65, delay=1.3)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left furnace", "right furnace"),
            ),
            Phase(
                guns=(
                    ("left cannon", Gun("aimed", interval=1.8, speed=0.65, volley=3)),
                    ("right cannon", Gun("aimed", interval=1.8, speed=0.65, volley=3, delay=0.9)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=5, spread=18, style="heavy", delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left cannon", "right cannon"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.12, speed=0.45, count=3, turn=12)),
                    (CORE, Gun("ring", interval=2.0, speed=0.38, count=14, turn=10, delay=1.0)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.65, delay=0.5)),
                ),
                sway=0.14,
            ),
        ),
    ),
    # 4-8, Badlands' boss: four turrets, the outer pair first, then the inner pair, then the core.
    "colossus": BossSpec(
        name="COLOSSUS",
        drawing="colossus",
        width=0.34,
        height=0.3,
        health=150.0,
        points=8000,
        parts=(
            PartSpec("left outer", "colossus_turret", -0.3, -0.02, 0.12, 0.12, 30.0, 600),
            PartSpec("right outer", "colossus_turret", 0.3, -0.02, 0.12, 0.12, 30.0, 600),
            PartSpec("left inner", "colossus_turret", -0.1, -0.2, 0.12, 0.12, 30.0, 600),
            PartSpec("right inner", "colossus_turret", 0.1, -0.2, 0.12, 0.12, 30.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left outer", Gun("aimed", interval=2.0, speed=0.7, volley=3)),
                    ("right outer", Gun("aimed", interval=2.0, speed=0.7, volley=3, delay=1.0)),
                    ("left inner", Gun("fan", interval=1.6, speed=0.5, count=3, spread=15, delay=0.5)),
                    ("right inner", Gun("fan", interval=1.6, speed=0.5, count=3, spread=15, delay=1.3)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left outer", "right outer"),
            ),
            Phase(
                guns=(
                    ("left inner", Gun("ring", interval=1.3, speed=0.45, count=8, turn=22)),
                    ("right inner", Gun("ring", interval=1.3, speed=0.45, count=8, turn=-22, delay=0.65)),
                    (CORE, Gun("fan", interval=2.6, speed=0.4, count=5, spread=20, style="heavy", delay=1.0)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left inner", "right inner"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.16, speed=0.42, count=4, turn=10)),
                    (CORE, Gun("aimed", interval=1.5, speed=0.7, count=3, spread=10, delay=0.7)),
                ),
                sway=0.15,
            ),
        ),
    ),
    # 5-1: a patrol drone, no parts.
    "patrol_drone": BossSpec(
        name="PATROL DRONE",
        drawing="patrol_drone",
        width=0.3,
        height=0.2,
        health=80.0,
        points=2000,
        phases=(
            Phase(
                guns=((CORE, Gun("aimed", interval=1.3, speed=0.6, count=2, spread=10)),), sway=0.14, until_below=0.5
            ),
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=1.6, speed=0.5, count=5, spread=15)),
                    (CORE, Gun("aimed", interval=2.2, speed=0.65, volley=3, delay=0.8)),
                ),
                sway=0.2,
            ),
        ),
    ),
    # 5-2: a riot enforcer behind two shields (they don't shoot); armored until they're gone.
    "enforcer": BossSpec(
        name="ENFORCER",
        drawing="enforcer",
        width=0.22,
        height=0.26,
        health=90.0,
        points=2400,
        parts=(
            PartSpec("left shield", "riot_shield", -0.18, -0.06, 0.12, 0.19, 35.0, 500),
            PartSpec("right shield", "riot_shield", 0.18, -0.06, 0.12, 0.19, 35.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    (CORE, Gun("aimed", interval=1.6, speed=0.6, volley=2)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=3, spread=25, delay=1.2)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left shield", "right shield"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.8, speed=0.42, count=10, turn=18)),
                    (CORE, Gun("aimed", interval=1.4, speed=0.65, count=3, spread=10, delay=0.7)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 5-3: a hover tank with two turrets; armored until they're gone.
    "hover_tank": BossSpec(
        name="HOVER TANK",
        drawing="hover_tank",
        width=0.3,
        height=0.3,
        health=110.0,
        points=2800,
        parts=(
            PartSpec("left turret", "tank_turret", -0.22, -0.02, 0.12, 0.15, 30.0, 500),
            PartSpec("right turret", "tank_turret", 0.22, -0.02, 0.12, 0.15, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left turret", Gun("aimed", interval=1.8, speed=0.65, volley=3)),
                    ("right turret", Gun("aimed", interval=1.8, speed=0.65, volley=3, delay=0.9)),
                    (CORE, Gun("ring", interval=2.4, speed=0.38, count=8, turn=22, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left turret", "right turret"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("fan", interval=1.1, speed=0.5, count=5, spread=14, sweep=30)),
                    (CORE, Gun("aimed", interval=1.8, speed=0.55, style="heavy", delay=0.9)),
                ),
                sway=0.14,
            ),
        ),
    ),
    # 5-4: a spire, no parts, three phases on its health.
    "spire": BossSpec(
        name="SPIRE",
        drawing="spire",
        width=0.22,
        height=0.36,
        health=120.0,
        points=2800,
        phases=(
            Phase(
                guns=((CORE, Gun("aimed", interval=1.6, speed=0.65, count=3, spread=8, volley=2)),),
                sway=0.1,
                until_below=0.66,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.11, speed=0.46, count=2, turn=11)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=3, spread=25, style="heavy", delay=1.2)),
                ),
                sway=0.12,
                until_below=0.33,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.5, speed=0.4, count=16, turn=11)),
                    (CORE, Gun("ring", interval=0.16, speed=0.42, count=3, turn=-12, delay=0.5)),
                ),
                sway=0.16,
            ),
        ),
    ),
    # 5-5: a sentry core with four nodes: the outer pair, then the inner pair, then the core.
    "sentry_grid": BossSpec(
        name="SENTRY GRID",
        drawing="sentry_grid",
        width=0.24,
        height=0.24,
        health=110.0,
        points=3000,
        parts=(
            PartSpec("left outer node", "sentry_node", -0.3, 0.06, 0.1, 0.1, 22.0, 400),
            PartSpec("right outer node", "sentry_node", 0.3, 0.06, 0.1, 0.1, 22.0, 400),
            PartSpec("left inner node", "sentry_node", -0.18, -0.13, 0.1, 0.1, 22.0, 400),
            PartSpec("right inner node", "sentry_node", 0.18, -0.13, 0.1, 0.1, 22.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left outer node", Gun("aimed", interval=1.4, speed=0.65)),
                    ("right outer node", Gun("aimed", interval=1.4, speed=0.65, delay=0.7)),
                    ("left inner node", Gun("ring", interval=2.0, speed=0.4, count=6, turn=20, delay=0.3)),
                    ("right inner node", Gun("ring", interval=2.0, speed=0.4, count=6, turn=-20, delay=1.3)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left outer node", "right outer node"),
            ),
            Phase(
                guns=(
                    ("left inner node", Gun("aimed", interval=1.4, speed=0.65, volley=2)),
                    ("right inner node", Gun("aimed", interval=1.4, speed=0.65, volley=2, delay=0.7)),
                    (CORE, Gun("fan", interval=2.0, speed=0.45, count=5, spread=15, delay=1.0)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left inner node", "right inner node"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.13, speed=0.45, count=3, turn=12)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.65, count=3, spread=10, delay=0.8)),
                ),
                sway=0.16,
            ),
        ),
    ),
    # 5-6: a heavy gunship with two cannons and two engines: cannons, then engines, then the core.
    "gunship_prime": BossSpec(
        name="GUNSHIP PRIME",
        drawing="gunship_prime",
        width=0.24,
        height=0.33,
        health=140.0,
        points=3600,
        parts=(
            PartSpec("left cannon", "prime_cannon", -0.18, -0.08, 0.1, 0.18, 30.0, 500),
            PartSpec("right cannon", "prime_cannon", 0.18, -0.08, 0.1, 0.18, 30.0, 500),
            PartSpec("left engine", "prime_engine", -0.3, 0.1, 0.12, 0.12, 30.0, 500),
            PartSpec("right engine", "prime_engine", 0.3, 0.1, 0.12, 0.12, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left cannon", Gun("aimed", interval=1.8, speed=0.65, volley=3)),
                    ("right cannon", Gun("aimed", interval=1.8, speed=0.65, volley=3, delay=0.9)),
                    ("left engine", Gun("fan", interval=2.0, speed=0.45, count=3, spread=20, delay=0.4)),
                    ("right engine", Gun("fan", interval=2.0, speed=0.45, count=3, spread=20, delay=1.4)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left cannon", "right cannon"),
            ),
            Phase(
                guns=(
                    ("left engine", Gun("ring", interval=2.0, speed=0.4, count=10, turn=18)),
                    ("right engine", Gun("ring", interval=2.0, speed=0.4, count=10, turn=-18, delay=1.0)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.55, volley=2, style="heavy", delay=0.5)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left engine", "right engine"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.12, speed=0.46, count=3, turn=12)),
                    (CORE, Gun("fan", interval=1.6, speed=0.5, count=5, spread=14, sweep=30, delay=0.8)),
                ),
                sway=0.16,
            ),
        ),
    ),
    # 5-7: an executor robot with two generators and two blades; armored, then two phases on its health.
    "executor": BossSpec(
        name="EXECUTOR",
        drawing="executor",
        width=0.28,
        height=0.3,
        health=160.0,
        points=4500,
        parts=(
            PartSpec("left generator", "overmind_generator", -0.32, 0.08, 0.12, 0.12, 30.0, 500),
            PartSpec("right generator", "overmind_generator", 0.32, 0.08, 0.12, 0.12, 30.0, 500),
            PartSpec("left blade", "executor_blade", -0.2, -0.1, 0.1, 0.22, 30.0, 500),
            PartSpec("right blade", "executor_blade", 0.2, -0.1, 0.1, 0.22, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left generator", Gun("ring", interval=2.2, speed=0.38, count=10, turn=18)),
                    ("right generator", Gun("ring", interval=2.2, speed=0.38, count=10, turn=-18, delay=1.1)),
                    ("left blade", Gun("aimed", interval=1.6, speed=0.65, volley=2, delay=0.5)),
                    ("right blade", Gun("aimed", interval=1.6, speed=0.65, volley=2, delay=1.3)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left generator", "right generator"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.14, speed=0.45, count=3, turn=12)),
                    ("left blade", Gun("fan", interval=1.8, speed=0.5, count=3, spread=18)),
                    ("right blade", Gun("fan", interval=1.8, speed=0.5, count=3, spread=18, delay=0.9)),
                ),
                sway=0.14,
                until_below=0.5,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.5, speed=0.4, count=14, turn=11)),
                    (CORE, Gun("aimed", interval=2.2, speed=0.55, volley=3, style="heavy", delay=0.7)),
                    ("left blade", Gun("aimed", interval=1.5, speed=0.7)),
                    ("right blade", Gun("aimed", interval=1.5, speed=0.7, delay=0.75)),
                ),
                sway=0.18,
            ),
        ),
    ),
    # 5-8, Metropolis' boss: shield generators armor the core; cannons on the sides keep firing until destroyed.
    "overmind": BossSpec(
        name="OVERMIND",
        drawing="overmind",
        width=0.3,
        height=0.3,
        health=160.0,
        points=10000,
        parts=(
            PartSpec("left generator", "overmind_generator", -0.24, 0.14, 0.12, 0.12, 35.0, 700),
            PartSpec("right generator", "overmind_generator", 0.24, 0.14, 0.12, 0.12, 35.0, 700),
            PartSpec("left cannon", "overmind_cannon", -0.37, -0.08, 0.1, 0.16, 35.0, 700),
            PartSpec("right cannon", "overmind_cannon", 0.37, -0.08, 0.1, 0.16, 35.0, 700),
        ),
        phases=(
            Phase(
                guns=(
                    ("left cannon", Gun("aimed", interval=1.5, speed=0.7, volley=2)),
                    ("right cannon", Gun("aimed", interval=1.5, speed=0.7, volley=2, delay=0.75)),
                    ("left generator", Gun("ring", interval=2.4, speed=0.38, count=10, turn=18)),
                    ("right generator", Gun("ring", interval=2.4, speed=0.38, count=10, turn=-18, delay=1.2)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left generator", "right generator"),
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=0.16, speed=0.45, count=3, turn=14)),
                    ("left cannon", Gun("fan", interval=1.8, speed=0.55, count=3, spread=20)),
                    ("right cannon", Gun("fan", interval=1.8, speed=0.55, count=3, spread=20, delay=0.9)),
                ),
                sway=0.14,
                until_below=0.5,
            ),
            Phase(
                guns=(
                    (CORE, Gun("ring", interval=1.4, speed=0.4, count=18, turn=10)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, volley=3, gap=0.2, style="heavy", delay=0.7)),
                    ("left cannon", Gun("aimed", interval=1.6, speed=0.7)),
                    ("right cannon", Gun("aimed", interval=1.6, speed=0.7, delay=0.8)),
                ),
                sway=0.2,
            ),
        ),
    ),
}
