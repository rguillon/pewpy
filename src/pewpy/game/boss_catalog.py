"""Every boss: one at the end of each level (02-enemies-bosses.md). Placeholders.

Sizes are hitboxes, and have the shape of the boss's drawing in `models/` (the model is drawn at that size with
square voxels). Parts are at (x, y) from the core's middle.
"""

from pewpy.game.bosses import CORE, BossSpec, Gun, PartSpec, Phase

BOSSES: dict[str, BossSpec] = {
    # 1-1: a patrol platform, no parts.
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
    # 1-2: a raider with swept wings, no parts.
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
            PartSpec("left drill", "rockbreaker_drill", -0.2, -0.04, 0.1, 0.16, 25.0, 400),
            PartSpec("right drill", "rockbreaker_drill", 0.2, -0.04, 0.1, 0.16, 25.0, 400),
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
    # 1-4: an armored siege ship, no parts, three phases on its health.
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
            PartSpec("left gun", "twin_fang_cannon", -0.19, -0.02, 0.1, 0.2, 30.0, 500),
            PartSpec("right gun", "twin_fang_cannon", 0.19, -0.02, 0.1, 0.2, 30.0, 500),
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
            PartSpec("left dish", "relay_array_dish", -0.26, 0.06, 0.14, 0.14, 35.0, 600),
            PartSpec("right dish", "relay_array_dish", 0.26, 0.06, 0.14, 0.14, 35.0, 600),
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
    # 1-7: a mine carrier with two launchers; armored, then two phases on its health.
    "mine_carrier": BossSpec(
        name="MINE CARRIER",
        drawing="mine_carrier",
        width=0.34,
        height=0.28,
        health=130.0,
        points=3500,
        parts=(
            PartSpec("left launcher", "mine_carrier_launcher", -0.27, -0.08, 0.12, 0.12, 35.0, 600),
            PartSpec("right launcher", "mine_carrier_launcher", 0.27, -0.08, 0.12, 0.12, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left launcher", Gun("fan", interval=1.8, speed=0.5, count=3, spread=20)),
                    ("right launcher", Gun("fan", interval=1.8, speed=0.5, count=3, spread=20, delay=0.9)),
                    (CORE, Gun("aimed", interval=2.4, speed=0.5, style="heavy", delay=1.2)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left launcher", "right launcher"),
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
    # 1-8, Orbit's boss: a battle station, no parts, two phases by health.
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
    # 2-1: a heavy hauler with cutters in front, no parts.
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
    # 2-2: a picket ship with two gun pods; armored until they're gone.
    "picket": BossSpec(
        name="PICKET",
        drawing="picket",
        width=0.2,
        height=0.26,
        health=80.0,
        points=2200,
        parts=(
            PartSpec("left gun pod", "picket_cannon", -0.19, 0.04, 0.16, 0.09, 25.0, 400),
            PartSpec("right gun pod", "picket_cannon", 0.19, 0.04, 0.16, 0.09, 25.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left gun pod", Gun("fan", interval=1.7, speed=0.45, count=3, spread=18)),
                    ("right gun pod", Gun("fan", interval=1.7, speed=0.45, count=3, spread=18, delay=0.85)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.55, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left gun pod", "right gun pod"),
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
    # 2-3: an armored ship with two rams in front; armored until they're gone.
    "bulwark": BossSpec(
        name="BULWARK",
        drawing="bulwark",
        width=0.28,
        height=0.3,
        health=90.0,
        points=2400,
        parts=(
            PartSpec("left ram", "bulwark_ram", -0.07, -0.2, 0.08, 0.14, 30.0, 500),
            PartSpec("right ram", "bulwark_ram", 0.07, -0.2, 0.08, 0.14, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left ram", Gun("aimed", interval=1.5, speed=0.6, volley=2)),
                    ("right ram", Gun("aimed", interval=1.5, speed=0.6, volley=2, delay=0.75)),
                    (CORE, Gun("fan", interval=2.4, speed=0.4, count=5, spread=18, delay=1.2)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left ram", "right ram"),
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
    # 2-4: a ship built around a spinning turbine, no parts: spirals, three phases.
    "turbine": BossSpec(
        name="TURBINE",
        drawing="turbine",
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
    # 2-5: a hauler with two fuel tanks; armored until they're gone.
    "silo_hauler": BossSpec(
        name="SILO HAULER",
        drawing="silo_hauler",
        width=0.26,
        height=0.24,
        health=100.0,
        points=2800,
        parts=(
            PartSpec("left tank", "silo_hauler_tank", -0.21, 0.04, 0.12, 0.19, 35.0, 600),
            PartSpec("right tank", "silo_hauler_tank", 0.21, 0.04, 0.12, 0.19, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left tank", Gun("ring", interval=1.8, speed=0.4, count=6, turn=15)),
                    ("right tank", Gun("ring", interval=1.8, speed=0.4, count=6, turn=-15, delay=0.9)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, volley=2, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left tank", "right tank"),
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
    # 2-6: a carrier with two hangars; armored, then two phases on its health.
    "hive_carrier": BossSpec(
        name="HIVE CARRIER",
        drawing="hive_carrier",
        width=0.22,
        height=0.3,
        health=110.0,
        points=3000,
        parts=(
            PartSpec("left hangar", "hive_carrier_launcher", -0.19, 0.06, 0.16, 0.18, 30.0, 500),
            PartSpec("right hangar", "hive_carrier_launcher", 0.19, 0.06, 0.16, 0.18, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left hangar", Gun("fan", interval=1.2, speed=0.5, count=3, spread=12, sweep=25)),
                    ("right hangar", Gun("fan", interval=1.2, speed=0.5, count=3, spread=12, sweep=25, delay=0.6)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, delay=1.0)),
                ),
                sway=0.14,
                armored=True,
                until_destroyed=("left hangar", "right hangar"),
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
    # 2-7: a space tug with two thrusters and a ram plate: thrusters, then the plate, then the core.
    "tugmaster": BossSpec(
        name="TUGMASTER",
        drawing="tugmaster",
        width=0.3,
        height=0.28,
        health=130.0,
        points=3500,
        parts=(
            PartSpec("left thruster", "tugmaster_engine", -0.23, 0.0, 0.12, 0.19, 30.0, 500),
            PartSpec("right thruster", "tugmaster_engine", 0.23, 0.0, 0.12, 0.19, 30.0, 500),
            PartSpec("ram plate", "tugmaster_plate", 0.0, -0.19, 0.22, 0.08, 40.0, 700),
        ),
        phases=(
            Phase(
                guns=(
                    ("left thruster", Gun("aimed", interval=1.6, speed=0.6, volley=2)),
                    ("right thruster", Gun("aimed", interval=1.6, speed=0.6, volley=2, delay=0.8)),
                    ("ram plate", Gun("fan", interval=2.0, speed=0.45, count=5, spread=15, delay=0.4)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left thruster", "right thruster"),
            ),
            Phase(
                guns=(
                    ("ram plate", Gun("ring", interval=1.6, speed=0.4, count=10, turn=18)),
                    (CORE, Gun("fan", interval=2.2, speed=0.4, count=3, spread=30, style="heavy", delay=0.8)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("ram plate",),
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
    # 3-1: a barge with two clamps; armored until they're gone.
    "clamp_barge": BossSpec(
        name="CLAMP BARGE",
        drawing="clamp_barge",
        width=0.26,
        height=0.2,
        health=70.0,
        points=2000,
        parts=(
            PartSpec("left clamp", "clamp_barge_clamp", -0.2, -0.08, 0.12, 0.14, 25.0, 400),
            PartSpec("right clamp", "clamp_barge_clamp", 0.2, -0.08, 0.12, 0.14, 25.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left clamp", Gun("aimed", interval=1.6, speed=0.55, count=2, spread=10)),
                    ("right clamp", Gun("aimed", interval=1.6, speed=0.55, count=2, spread=10, delay=0.8)),
                    (CORE, Gun("fan", interval=2.2, speed=0.4, count=3, spread=20, delay=1.1)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left clamp", "right clamp"),
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
    # 3-2: a ring-shaped pulse ship, no parts: rings.
    "pulsar": BossSpec(
        name="PULSAR",
        drawing="pulsar",
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
            PartSpec("left gun", "frigate_turret", -0.17, 0.02, 0.1, 0.1, 30.0, 500),
            PartSpec("right gun", "frigate_turret", 0.17, 0.02, 0.1, 0.1, 30.0, 500),
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
    # 3-4: a delta-winged raider, no parts: sweeping fans, three phases.
    "delta_raider": BossSpec(
        name="DELTA RAIDER",
        drawing="delta_raider",
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
    # 3-5: a fortress ship with two cryo cannons; armored until they're gone.
    "cryo_fortress": BossSpec(
        name="CRYO FORTRESS",
        drawing="cryo_fortress",
        width=0.3,
        height=0.26,
        health=110.0,
        points=2800,
        parts=(
            PartSpec("left cannon", "cryo_fortress_cannon", -0.23, 0.02, 0.12, 0.15, 35.0, 600),
            PartSpec("right cannon", "cryo_fortress_cannon", 0.23, 0.02, 0.12, 0.15, 35.0, 600),
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
    # 3-6: a salvage ship with four grapples; armored until they're all gone, then two phases.
    "grappler": BossSpec(
        name="GRAPPLER",
        drawing="grappler",
        width=0.26,
        height=0.26,
        health=130.0,
        points=3200,
        parts=(
            PartSpec("left grapple", "grappler_clamp", -0.2, -0.13, 0.08, 0.21, 20.0, 400),
            PartSpec("right grapple", "grappler_clamp", 0.2, -0.13, 0.08, 0.21, 20.0, 400),
            PartSpec("left inner grapple", "grappler_clamp", -0.09, -0.21, 0.08, 0.21, 20.0, 400),
            PartSpec("right inner grapple", "grappler_clamp", 0.09, -0.21, 0.08, 0.21, 20.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left grapple", Gun("fan", interval=1.6, speed=0.5, count=3, spread=15)),
                    ("right grapple", Gun("fan", interval=1.6, speed=0.5, count=3, spread=15, delay=0.8)),
                    ("left inner grapple", Gun("aimed", interval=1.4, speed=0.6, delay=0.4)),
                    ("right inner grapple", Gun("aimed", interval=1.4, speed=0.6, delay=1.1)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left grapple", "right grapple", "left inner grapple", "right inner grapple"),
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
            PartSpec("left front turret", "dreadnought_turret", -0.18, -0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("right front turret", "dreadnought_turret", 0.18, -0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("left rear turret", "dreadnought_turret", -0.26, 0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("right rear turret", "dreadnought_turret", 0.26, 0.1, 0.12, 0.12, 25.0, 500),
            PartSpec("bow gun", "dreadnought_cannon", 0.0, -0.24, 0.08, 0.11, 35.0, 700),
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
    # 3-8, Waters' boss: two missile batteries, then two phases of the core alone.
    "tidebreaker": BossSpec(
        name="TIDEBREAKER",
        drawing="tidebreaker",
        width=0.3,
        height=0.36,
        health=120.0,
        points=7000,
        parts=(
            PartSpec("left battery", "tidebreaker_launcher", -0.24, 0.04, 0.16, 0.22, 45.0, 900),
            PartSpec("right battery", "tidebreaker_launcher", 0.24, 0.04, 0.16, 0.22, 45.0, 900),
        ),
        phases=(
            Phase(
                guns=(
                    ("left battery", Gun("fan", interval=1.1, speed=0.5, count=4, spread=12, sweep=30)),
                    ("right battery", Gun("fan", interval=1.1, speed=0.5, count=4, spread=12, sweep=30, delay=0.55)),
                    (CORE, Gun("aimed", interval=2.4, speed=0.55, style="heavy", delay=1.0)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left battery", "right battery"),
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
    # 4-1: an assault ship with two breaching clamps; armored until they're gone.
    "breacher": BossSpec(
        name="BREACHER",
        drawing="breacher",
        width=0.24,
        height=0.24,
        health=70.0,
        points=2000,
        parts=(
            PartSpec("left clamp", "breacher_clamp", -0.17, -0.12, 0.1, 0.16, 25.0, 400),
            PartSpec("right clamp", "breacher_clamp", 0.17, -0.12, 0.1, 0.16, 25.0, 400),
        ),
        phases=(
            Phase(
                guns=(
                    ("left clamp", Gun("aimed", interval=1.6, speed=0.55, volley=2)),
                    ("right clamp", Gun("aimed", interval=1.6, speed=0.55, volley=2, delay=0.8)),
                    (CORE, Gun("fan", interval=2.2, speed=0.45, count=3, spread=18, delay=1.1)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left clamp", "right clamp"),
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
    # 4-2: a ring ship spinning its guns, no parts: spirals, three phases.
    "cyclone": BossSpec(
        name="CYCLONE",
        drawing="cyclone",
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
    # 4-3: a boring ship with two generators; armored until they're gone.
    "borer": BossSpec(
        name="BORER",
        drawing="borer",
        width=0.24,
        height=0.24,
        health=90.0,
        points=2400,
        parts=(
            PartSpec("left generator", "borer_generator", -0.2, 0.08, 0.14, 0.14, 30.0, 500),
            PartSpec("right generator", "borer_generator", 0.2, 0.08, 0.14, 0.14, 30.0, 500),
        ),
        phases=(
            Phase(
                guns=(
                    ("left generator", Gun("ring", interval=2.0, speed=0.38, count=8, turn=20)),
                    ("right generator", Gun("ring", interval=2.0, speed=0.38, count=8, turn=-20, delay=1.0)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, volley=3, delay=0.5)),
                ),
                sway=0.1,
                armored=True,
                until_destroyed=("left generator", "right generator"),
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
    # 4-4: a fortress ship with two turrets; armored until they're gone.
    "bastion": BossSpec(
        name="BASTION",
        drawing="bastion",
        width=0.32,
        height=0.23,
        health=110.0,
        points=2800,
        parts=(
            PartSpec("left turret", "bastion_turret", -0.25, -0.06, 0.12, 0.12, 30.0, 500),
            PartSpec("right turret", "bastion_turret", 0.25, -0.06, 0.12, 0.12, 30.0, 500),
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
    # 4-5: a foundry ship with two presses; armored, then two phases on its health.
    "foundry": BossSpec(
        name="FOUNDRY",
        drawing="foundry",
        width=0.28,
        height=0.3,
        health=140.0,
        points=3400,
        parts=(
            PartSpec("left press", "foundry_piston", -0.22, -0.1, 0.12, 0.14, 35.0, 600),
            PartSpec("right press", "foundry_piston", 0.22, -0.1, 0.12, 0.14, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left press", Gun("fan", interval=2.0, speed=0.42, count=3, spread=20, style="heavy")),
                    ("right press", Gun("fan", interval=2.0, speed=0.42, count=3, spread=20, style="heavy", delay=1.0)),
                    (CORE, Gun("aimed", interval=1.6, speed=0.6, delay=0.5)),
                ),
                sway=0.08,
                armored=True,
                until_destroyed=("left press", "right press"),
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
    # 4-6: a salvager with two wing batteries; armored, then two phases.
    "scavenger": BossSpec(
        name="SCAVENGER",
        drawing="scavenger",
        width=0.2,
        height=0.27,
        health=110.0,
        points=3000,
        parts=(
            PartSpec("left battery", "scavenger_launcher", -0.21, 0.05, 0.2, 0.13, 35.0, 600),
            PartSpec("right battery", "scavenger_launcher", 0.21, 0.05, 0.2, 0.13, 35.0, 600),
        ),
        phases=(
            Phase(
                guns=(
                    ("left battery", Gun("fan", interval=1.3, speed=0.5, count=4, spread=12, sweep=25)),
                    ("right battery", Gun("fan", interval=1.3, speed=0.5, count=4, spread=12, sweep=25, delay=0.65)),
                    (CORE, Gun("aimed", interval=2.0, speed=0.6, delay=1.0)),
                ),
                sway=0.12,
                armored=True,
                until_destroyed=("left battery", "right battery"),
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
    # 4-7: a mining rig with two furnaces and two cannons: furnaces, then cannons, then the core.
    "magma_rig": BossSpec(
        name="MAGMA RIG",
        drawing="magma_rig",
        width=0.3,
        height=0.28,
        health=150.0,
        points=4000,
        parts=(
            PartSpec("left furnace", "magma_rig_generator", -0.24, 0.1, 0.12, 0.14, 30.0, 500),
            PartSpec("right furnace", "magma_rig_generator", 0.24, 0.1, 0.12, 0.14, 30.0, 500),
            PartSpec("left cannon", "magma_rig_cannon", -0.36, -0.06, 0.1, 0.16, 30.0, 500),
            PartSpec("right cannon", "magma_rig_cannon", 0.36, -0.06, 0.1, 0.16, 30.0, 500),
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
    # 5-1: a patrol gunship, no parts.
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
    # 5-2: an enforcer behind two armor shields (they don't shoot); armored until they're gone.
    "enforcer": BossSpec(
        name="ENFORCER",
        drawing="enforcer",
        width=0.22,
        height=0.26,
        health=90.0,
        points=2400,
        parts=(
            PartSpec("left shield", "enforcer_shield", -0.18, -0.06, 0.12, 0.19, 35.0, 500),
            PartSpec("right shield", "enforcer_shield", 0.18, -0.06, 0.12, 0.19, 35.0, 500),
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
    # 5-3: a heavy gunboat with two turrets; armored until they're gone.
    "hover_tank": BossSpec(
        name="HOVER TANK",
        drawing="hover_tank",
        width=0.3,
        height=0.3,
        health=110.0,
        points=2800,
        parts=(
            PartSpec("left turret", "hover_tank_turret", -0.22, -0.02, 0.12, 0.15, 30.0, 500),
            PartSpec("right turret", "hover_tank_turret", 0.22, -0.02, 0.12, 0.15, 30.0, 500),
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
    # 5-4: a tall command ship, no parts, three phases on its health.
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
    # 5-5: a sentry ship with four nodes: the outer pair, then the inner pair, then the core.
    "sentry_grid": BossSpec(
        name="SENTRY GRID",
        drawing="sentry_grid",
        width=0.24,
        height=0.24,
        health=110.0,
        points=3000,
        parts=(
            PartSpec("left outer node", "sentry_grid_generator", -0.3, 0.06, 0.1, 0.1, 22.0, 400),
            PartSpec("right outer node", "sentry_grid_generator", 0.3, 0.06, 0.1, 0.1, 22.0, 400),
            PartSpec("left inner node", "sentry_grid_generator", -0.18, -0.13, 0.1, 0.1, 22.0, 400),
            PartSpec("right inner node", "sentry_grid_generator", 0.18, -0.13, 0.1, 0.1, 22.0, 400),
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
            PartSpec("left cannon", "gunship_prime_cannon", -0.18, -0.08, 0.1, 0.18, 30.0, 500),
            PartSpec("right cannon", "gunship_prime_cannon", 0.18, -0.08, 0.1, 0.18, 30.0, 500),
            PartSpec("left engine", "gunship_prime_engine", -0.3, 0.1, 0.12, 0.12, 30.0, 500),
            PartSpec("right engine", "gunship_prime_engine", 0.3, 0.1, 0.12, 0.12, 30.0, 500),
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
    # 5-7: a command ship with two generators and two blades; armored, then two phases on its health.
    "executor": BossSpec(
        name="EXECUTOR",
        drawing="executor",
        width=0.28,
        height=0.3,
        health=160.0,
        points=4500,
        parts=(
            PartSpec("left generator", "executor_generator", -0.32, 0.08, 0.12, 0.12, 30.0, 500),
            PartSpec("right generator", "executor_generator", 0.32, 0.08, 0.12, 0.12, 30.0, 500),
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
    # 5-8, Metropolis' boss: shield generators armor the core; cannons on the sides keep firing.
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
