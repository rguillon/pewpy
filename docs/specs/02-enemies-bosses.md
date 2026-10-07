# 02 — Enemies: bosses

> Part of `02-enemies.md` (general rules and enemy weapons are there).
> Units: speed in world units per second (the play area is 2.5 wide and 2.0 tall, the player moves at 1.0),
> health in damage points (the starting weapon does 1.0 per bullet).

## Bosses

> Placeholders chosen by Claude: a boss is an enemy like any other, only described differently (see
> `06-technical.md`): the mini bosses in `data/bosses/mini_bosses.json`, the final bosses in
> `data/bosses/final_bosses.json` (made from plans, see below). Every level has two bosses
> of its own (see `03-levels.md`): a mini boss halfway (the "Boss: ..." sections below) and a bigger, harder final
> boss at the end (see "Final bosses"), harder through each world.

General rules for every boss:

- A boss is a core and destructible parts around it (cannons, fins, turrets…). Each part is hit like an enemy of
  its own (shots, the laser, missiles and their splash), gives its own points and drops a pickup 30% of the time.
  Destroying the core destroys the parts left (without their points) and ends the fight; the core always drops a
  pickup.
- Looks: giant industrial ships (see `05-visuals.md`): grey armor plates with seams, a raised deck, often a
  command tower with windows and a glowing reactor, ribbed engine nacelles at the back, the boss's color as
  markings; parts are machines (turrets, cannons, launchers, clamps, generators...). One voxel model per boss in
  `data/models/bosses/`, its core's drawing with its kinds of part's drawings in it (see `05-visuals.md`), with the
  same cubes as every other model; each drawing is about as big as its hitbox. The newest bosses (Reaper, Leviathan,
  Flare Rig, Crucible, Interdictor, Nightwatch, Arc Tower, Apex) are made by the makers (`src/pewpy/makers/bosses/`)
  in real 3D, their parts standing on the hull.
- Entry: comes down from above the screen at 0.25 and stops at y = 0.55, then sways left and right between the
  screen edges. It doesn't leave the screen and doesn't shoot before it stops; until then, it and its parts can't be
  hurt (shots and the laser stop at them, harmlessly).
- Health bar: at the top of the screen, with its name, for the core and parts together (see `04-ui-audio.md`).
- Phases: each phase has its own guns and sway speed. A phase ends when some parts are destroyed, or when the
  core's health falls below a fraction of its full health. At the start of each phase (and on arrival) the core
  flashes white and doesn't shoot for 1.2 s.
- Armored: in some phases shots bounce off the core (and the laser stops at it), which looks darker; its parts
  must be destroyed first.
- Parts mounted on the hull: a shot (or the laser) under a living part flies over the core up to that part, as seen
  from above; parts standing in front of others are hit first, and the ones behind them once they are destroyed.
- Guns: each belongs to the core or to a part and stops when its part is destroyed. Patterns: aimed (at the
  player), fan (around straight down, sometimes swinging left and right) and ring (all around; fired fast while
  turning, it makes a spiral), sometimes several shots in a row. Pink bullets, and big orange "heavy" ones
  (0.05 across); also blue "sniper" shots, small pellets (0.022), violet shots snaking across their line of flight
  (like the Serpent's), cyan "accel" shots (starting at 35% of their speed, speeding up by 90% of it per second, up
  to 1.8 times it) and yellow "curve" shots (their path bending by 35° per second for 1.5 s, then straight on).
- Projectiles: a gun can launch rockets, homing missiles or cluster bombs (see `02-enemies.md`) in its pattern's
  directions instead of shots.
- Lasers: a laser gun fires red beams straight down from under its core or part, past the bottom of the screen, 0.07
  wide, for 1 to 1.4 s; the beams follow the boss as it sways. Each beam is announced 1 s before by a thin harmless
  red beam (0.008 wide, see-through) where it will be, so the player knows it's time to move *(the user's idea)*.
  A beam vanishes when its core or part is destroyed.
- Ramming a boss or one of its parts: the player takes 2 damage, the boss isn't hurt.
- Hits make it brighter for a moment instead of white (it's shot at all the time).

### Boss: Sentinel

- Level: 1-1 (High Peaks)
- Look and size: a narrow patrol platform with wide solar wings and a command tower, blue markings, 0.26 x 0.2; no parts
- Health: 60
- Phases:
    1. Down to 50% of the core's health: sways at 0.1
    2. Until the end: sways at 0.14
- Attacks per phase:
    1. The core: a fan of 3 shots 20° apart every 1.6 s, speed 0.45
    2. The core: 3 aimed shots in a row every 2 s, speed 0.55 and a ring of 8 every 3 s, turning, speed 0.35
- Weak points: none
- Time limit? No
- Points: 1500

### Boss: Thresher

- Level: 1-2 (Pine Ridge)
- Look and size: a heavy hauler with three pairs of cutting blades at the prow, yellow markings, 0.3 x 0.22; no parts
- Health: 70
- Phases:
    1. Down to 50% of the core's health: sways at 0.1
    2. Until the end: sways at 0.14
- Attacks per phase:
    1. The core: a fan of 4 shots 14° apart every 1.4 s, speed 0.45
    2. The core: 3 aimed shots 10° apart every 1.5 s, speed 0.55 and a fan of 7 shots 12° apart every 3 s, speed 0.35
- Weak points: none
- Time limit? No
- Points: 1800

### Boss: Prowler

- Level: 1-3 (Glacier Pass)
- Look and size: a delta-winged raider with a small red reactor and a prow gun, 0.34 x 0.2; no parts
- Health: 75
- Phases:
    1. Down to 50% of the core's health: sways at 0.14
    2. Until the end: sways at 0.2
- Attacks per phase:
    1. The core: 3 aimed shots 12° apart every 1.5 s, speed 0.55
    2. The core: a ring of 8 every 1.8 s, turning, speed 0.4 and an aimed shot every 1.2 s, speed 0.6
- Weak points: none
- Time limit? No
- Points: 1800

### Boss: Pulsar

- Level: 1-4 (Stormcrest)
- Look and size: a ring-shaped ship around a bright cyan reactor, 0.26 x 0.3; no parts
- Health: 90
- Phases:
    1. Down to 50% of the core's health: sways at 0.08
    2. Until the end: sways at 0.12
- Attacks per phase:
    1. The core: a ring of 10 every 1.6 s, turning, speed 0.38
    2. The core: a 2-arm spiral (every 0.14 s), speed 0.42 and a ring of 16 every 3 s, speed 0.3
- Weak points: none
- Time limit? No
- Points: 2200

### Boss: Rockbreaker

- Level: 1-5 (Dusk Peaks)
- Look and size: a boxy mining ship with yellow markings and two prow drills, 0.26 x 0.22; two drills (0.1 x 0.16, 25
  health, 400 points each)
- Health: 60 (core)
- Phases:
    1. Until both drills are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.15
- Attacks per phase:
    1. Each drill: 2 aimed shots in a row every 1.8 s, speed 0.55
    2. The core: a fan of 5 shots 16° apart every 1.6 s, speed 0.45 and 2 aimed shots in a row every 2 s, speed 0.6
- Weak points: both drills
- Time limit? No
- Points: 2000

### Boss: Warden

- Level: 1-6 (Summit)
- Look and size: a wide battle station with side wings, a command tower, a red reactor and prow guns, 0.46 x 0.3; no
  parts
- Health: 140
- Phases:
    1. Down to 55% of the core's health: sways at 0.12
    2. Until the end: sways at 0.2
- Attacks per phase:
    1. The core: a fan of 5 shots 18° apart every 1.6 s, speed 0.5 and 2 aimed shots 8° apart, 3 times in a row every
       2.2 s, speed 0.7
    2. The core: a 3-arm spiral (every 0.14 s), speed 0.45 and an aimed heavy shot every 1.8 s, speed 0.6
- Weak points: none
- Time limit? No
- Points: 5000

### Boss: Patrol Drone

- Level: 2-1 (Greenwood)
- Look and size: a cross-shaped patrol gunship with a tall tower and cyan markings, 0.3 x 0.2; no parts
- Health: 80
- Phases:
    1. Down to 50% of the core's health: sways at 0.14
    2. Until the end: sways at 0.2
- Attacks per phase:
    1. The core: 2 aimed shots 10° apart every 1.3 s, speed 0.6
    2. The core: a fan of 5 shots 15° apart every 1.6 s, speed 0.5 and 3 aimed shots in a row every 2.2 s, speed 0.65
- Weak points: none
- Time limit? No
- Points: 2000

### Boss: Cyclone

- Level: 2-2 (Riverbend)
- Look and size: a ring-shaped ship around a sandy glowing core, 0.28 x 0.28; no parts
- Health: 100
- Phases:
    1. Down to 66% of the core's health: sways at 0.12
    2. Down to 33% of the core's health: sways at 0.16
    3. Until the end: sways at 0.2
- Attacks per phase:
    1. The core: a 2-arm spiral (every 0.12 s), speed 0.42
    2. The core: a 3-arm spiral (every 0.14 s), speed 0.44 and an aimed shot every 2 s, speed 0.6
    3. The core: a 4-arm spiral (every 0.16 s), speed 0.42 and a ring of 12 every 2.2 s, speed 0.35
- Weak points: none
- Time limit? No
- Points: 2500

### Boss: Siege Pod

- Level: 2-3 (Deep Canopy)
- Look and size: a rounded armored siege ship around a big orange reactor, 0.3 x 0.3; no parts
- Health: 110
- Phases:
    1. Down to 66% of the core's health: sways at 0.1
    2. Down to 33% of the core's health: sways at 0.12
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. The core: a fan of 5 shots 15° apart every 1.8 s, speed 0.45
    2. The core: a 2-arm spiral (every 0.12 s), speed 0.45
    3. The core: a ring of 12 every 1.6 s, turning, speed 0.4 and an aimed heavy shot every 2.2 s, speed 0.55
- Weak points: none
- Time limit? No
- Points: 2500

### Boss: Delta Raider

- Level: 2-4 (Autumn Wood)
- Look and size: a delta-winged raider with a teal reactor and a prow gun, 0.4 x 0.23; no parts
- Health: 110
- Phases:
    1. Down to 66% of the core's health: sways at 0.12
    2. Down to 33% of the core's health: sways at 0.14
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. The core: a fan of 5 shots 12° apart swinging 35° left and right every 1.2 s, speed 0.5
    2. The core: a fan of 3 shots 20° apart swinging 45° left and right every 0.5 s, speed 0.45 and an aimed shot every
       1.8 s, speed 0.6
    3. The core: a 2-arm spiral (every 0.1 s), speed 0.5 and a fan of 5 heavy shots 18° apart every 2.4 s, speed 0.4
- Weak points: none
- Time limit? No
- Points: 2600

### Boss: Breacher

- Level: 2-5 (Twilight Grove)
- Look and size: a wedge-shaped assault ship with a prow ram gun and orange markings, 0.24 x 0.24; two clamps (0.1 x
  0.16, 25 health, 400 points each)
- Health: 70 (core)
- Phases:
    1. Until both clamps are destroyed, the core is armored: sways at 0.12
    2. Until the end: sways at 0.18
- Attacks per phase:
    1. Each clamp: 2 aimed shots in a row every 1.6 s, speed 0.55; The core: a fan of 3 shots 18° apart every 2.2 s,
       speed 0.45
    2. The core: 3 aimed shots 12° apart every 1.2 s, speed 0.6 and a ring of 8 every 2.4 s, turning, speed 0.4
- Weak points: both clamps
- Time limit? No
- Points: 2000

### Boss: Harvester

- Level: 2-6 (Moonlit Woods)
- Look and size: a heavy prow-shaped ship with four engines, a tower, prow guns and a green reactor, 0.34 x 0.26; two
  cannons (0.14 x 0.18, 40 health, 800 points each)
- Health: 100 (core)
- Phases:
    1. Until both cannons are destroyed, the core is armored: sways at 0.12
    2. Until the end: sways at 0.18
- Attacks per phase:
    1. Each cannon: 3 aimed shots in a row every 1.8 s, speed 0.65; The core: a fan of 3 heavy shots 25° apart every 2.5
       s, speed 0.4
    2. The core: a ring of 14 every 2.2 s, turning, speed 0.4 and 3 aimed shots 12° apart every 1.4 s, speed 0.6
- Weak points: both cannons
- Time limit? No
- Points: 6000

### Boss: Turbine

- Level: 3-1 (Lush Veld)
- Look and size: a ring-shaped ship around a big glowing yellow turbine core, 0.3 x 0.3; no parts
- Health: 110
- Phases:
    1. Down to 66% of the core's health: sways at 0.08
    2. Down to 33% of the core's health: sways at 0.1
    3. Until the end: sways at 0.16
- Attacks per phase:
    1. The core: a 2-arm spiral (every 0.14 s), speed 0.42
    2. The core: a 4-arm spiral (every 0.2 s), speed 0.4
    3. The core: a ring of 12 every 1.4 s, turning, speed 0.42 and an aimed heavy shot every 2 s, speed 0.55
- Weak points: none
- Time limit? No
- Points: 2600

### Boss: Clamp Barge

- Level: 3-2 (Winding Sands)
- Look and size: a wide salvage barge with a command tower and coral markings, 0.26 x 0.2; two clamps (0.12 x 0.14, 25
  health, 400 points each)
- Health: 70 (core)
- Phases:
    1. Until both clamps are destroyed, the core is armored: sways at 0.12
    2. Until the end: sways at 0.18
- Attacks per phase:
    1. Each clamp: 2 aimed shots 10° apart every 1.6 s, speed 0.55; The core: a fan of 3 shots 20° apart every 2.2 s,
       speed 0.4
    2. The core: a ring of 10 every 1.8 s, turning, speed 0.4 and 3 aimed shots in a row every 1.6 s, speed 0.6
- Weak points: both clamps
- Time limit? No
- Points: 2000

### Boss: Spire

- Level: 3-3 (Kopje Country)
- Look and size: a long command ship carrying a tall tower from stern to prow, violet markings, 0.22 x 0.36; no parts
- Health: 120
- Phases:
    1. Down to 66% of the core's health: sways at 0.1
    2. Down to 33% of the core's health: sways at 0.12
    3. Until the end: sways at 0.16
- Attacks per phase:
    1. The core: 3 aimed shots 8° apart, 2 times in a row every 1.6 s, speed 0.65
    2. The core: a 2-arm spiral (every 0.11 s), speed 0.46 and a fan of 3 heavy shots 25° apart every 2.4 s, speed 0.4
    3. The core: a ring of 16 every 1.5 s, turning, speed 0.4 and a 3-arm spiral (every 0.16 s), speed 0.42
- Weak points: none
- Time limit? No
- Points: 2800

### Boss: Twin Fang

- Level: 3-4 (Acacia Dusk)
- Look and size: a wedge-shaped gunship with a command tower, cyan markings, 0.24 x 0.26; two guns (0.1 x 0.2, 30
  health, 500 points each)
- Health: 90 (core)
- Phases:
    1. Down to 50% of the core's health: sways at 0.12
    2. Until the end: sways at 0.16
- Attacks per phase:
    1. Each gun: 2 aimed shots in a row every 1.6 s, speed 0.6; The core: a fan of 3 shots 25° apart every 2.2 s, speed
       0.45
    2. The core: a 3-arm spiral (every 0.15 s), speed 0.42; Each gun: a fan of 3 shots 15° apart every 2 s, speed 0.5
- Weak points: both guns
- Time limit? No
- Points: 2600

### Boss: Frigate

- Level: 3-5 (Long Grass)
- Look and size: a long frigate with a command tower, a prow gun and blue markings, 0.22 x 0.36; two guns (0.1 x 0.1, 30
  health, 500 points each)
- Health: 90 (core)
- Phases:
    1. Until both guns are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.14
- Attacks per phase:
    1. Each gun: 3 aimed shots in a row every 2 s, speed 0.6; The core: a fan of 5 shots 12° apart every 2.4 s, speed
       0.45
    2. The core: a fan of 3 heavy shots 30° apart every 1.8 s, speed 0.45 and 3 aimed shots 10° apart every 1.3 s, speed
       0.6
- Weak points: both guns
- Time limit? No
- Points: 2400

### Boss: Tidebreaker

- Level: 3-6 (Veld by Night)
- Look and size: a heavy prow-shaped battleship with four engines, a tower and a cyan reactor, 0.3 x 0.36; two batterys
  (0.16 x 0.22, 45 health, 900 points each)
- Health: 120 (core)
- Phases:
    1. Until both batterys are destroyed, the core is armored: sways at 0.1
    2. Down to 45% of the core's health: sways at 0.14
    3. Until the end: sways at 0.2
- Attacks per phase:
    1. Each battery: a fan of 4 shots 12° apart swinging 30° left and right every 1.1 s, speed 0.5; The core: an aimed
       heavy shot every 2.4 s, speed 0.55
    2. The core: a 2-arm spiral (every 0.1 s), speed 0.5 and an aimed shot every 1.2 s, speed 0.65
    3. The core: a ring of 16 every 1.6 s, turning, speed 0.42 and 3 aimed shots in a row every 2 s, speed 0.7
- Weak points: both batterys
- Time limit? No
- Points: 7000

### Boss: Picket

- Level: 4-1 (Harvest Dusk)
- Look and size: a narrow picket ship with wide wings and a tall tower, green markings, 0.2 x 0.26; two gun pods (0.16 x
  0.09, 25 health, 400 points each)
- Health: 80 (core)
- Phases:
    1. Until both gun pods are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.15
- Attacks per phase:
    1. Each gun pod: a fan of 3 shots 18° apart every 1.7 s, speed 0.45; The core: an aimed shot every 2 s, speed 0.55
    2. The core: a ring of 12 every 2 s, turning, speed 0.4 and 3 aimed shots in a row every 1.8 s, speed 0.6
- Weak points: both gun pods
- Time limit? No
- Points: 2200

### Boss: Bulwark

- Level: 4-2 (Golden Fields)
- Look and size: a thick armored block with a wide deck, vent banks and green markings, 0.28 x 0.3; two rams (0.08 x
  0.14, 30 health, 500 points each)
- Health: 90 (core)
- Phases:
    1. Until both rams are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.14
- Attacks per phase:
    1. Each ram: 2 aimed shots in a row every 1.5 s, speed 0.6; The core: a fan of 5 shots 18° apart every 2.4 s, speed
       0.4
    2. The core: a 2-arm spiral (every 0.12 s), speed 0.45 and an aimed heavy shot every 2 s, speed 0.55
- Weak points: both rams
- Time limit? No
- Points: 2400

### Boss: Borer

- Level: 4-3 (Lavender Rows)
- Look and size: a prow-shaped mining ship with a big drill gun and orange markings, 0.24 x 0.24; two generators (0.14 x
  0.14, 30 health, 500 points each)
- Health: 90 (core)
- Phases:
    1. Until both generators are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.15
- Attacks per phase:
    1. Each generator: a ring of 8 every 2 s, turning, speed 0.38; The core: 3 aimed shots in a row every 2 s, speed 0.6
    2. The core: a fan of 7 shots 12° apart every 1.8 s, speed 0.45 and an aimed heavy shot every 1.6 s, speed 0.55
- Weak points: both generators
- Time limit? No
- Points: 2400

### Boss: Silo Hauler

- Level: 4-4 (Orchard Country)
- Look and size: a twin-hulled hauler joined by a bridge with a command tower, red markings, 0.26 x 0.24; two tanks
  (0.12 x 0.19, 35 health, 600 points each)
- Health: 100 (core)
- Phases:
    1. Until both tanks are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.15
- Attacks per phase:
    1. Each tank: a ring of 6 every 1.8 s, turning, speed 0.4; The core: 2 aimed shots in a row every 2 s, speed 0.6
    2. The core: a fan of 5 shots 15° apart swinging 25° left and right every 1.3 s, speed 0.5 and a ring of 10 every
       2.5 s, speed 0.38
- Weak points: both tanks
- Time limit? No
- Points: 2800

### Boss: Bastion

- Level: 4-5 (Hay Moon)
- Look and size: a wide fortress block with a tower, prow guns and a rust-orange reactor, 0.32 x 0.23; two turrets (0.12
  x 0.12, 30 health, 500 points each)
- Health: 110 (core)
- Phases:
    1. Until both turrets are destroyed, the core is armored: sways at 0.08
    2. Until the end: sways at 0.12
- Attacks per phase:
    1. Each turret: 2 aimed shots 10° apart every 1.5 s, speed 0.6; The core: a fan of 3 heavy shots 25° apart every 2.4
       s, speed 0.4
    2. The core: a ring of 14 every 1.8 s, turning, speed 0.4 and a fan of 5 shots 15° apart swinging 30° left and right
       every 1.4 s, speed 0.5
- Weak points: both turrets
- Time limit? No
- Points: 2800

### Boss: Reaper

- Level: 4-6 (Last Harvest)
- Look and size: a giant harvester (boss candidate #036, in real 3D): a wide brown hull with toothed drill cones at the
  back, augers and a cutter at the bow, 0.41 x 0.33; two augers (0.05 x 0.09, 20 health, 400 points each), a cutter
  (0.11 x 0.15, 30 health, 600 points) and two drills (0.1 x 0.16, 25 health, 500 points each)
- Health: 120 (core)
- Phases:
    1. Until both augers and the cutter are destroyed, the core is armored: sways at 0.08
    2. Until both drills are destroyed, the core is armored: sways at 0.12
    3. Until the end: sways at 0.15
- Attacks per phase:
    1. Each auger: 2 aimed shots in a row every 1.6 s, speed 0.6; The cutter: a fan of 5 shots 14° apart swinging 25°
       left and right every 2 s, speed 0.45
    2. Each drill: a ring of 10 every 2.2 s, turning, speed 0.38; The core: 2 aimed heavy shots in a row every 2 s,
       speed 0.55
    3. The core: a 3-arm spiral (every 0.15 s), speed 0.44 and a fan of 5 shots 15° apart swinging 30° left and right
       every 1.7 s, speed 0.5
- Weak points: both augers, the cutter and both drills
- Time limit? No
- Points: 7500

### Boss: Enforcer

- Level: 5-1 (Rust Pan)
- Look and size: a wedge-shaped enforcer with a wide command tower and amber markings, 0.22 x 0.26; two shields (0.12 x
  0.19, 35 health, 500 points each)
- Health: 90 (core)
- Phases:
    1. Until both shields are destroyed, the core is armored: sways at 0.12
    2. Until the end: sways at 0.18
- Attacks per phase:
    1. The core: 2 aimed shots in a row every 1.6 s, speed 0.6 and a fan of 3 shots 25° apart every 2.4 s, speed 0.4
    2. The core: a ring of 10 every 1.8 s, turning, speed 0.42 and 3 aimed shots 10° apart every 1.4 s, speed 0.65
- Weak points: both shields
- Time limit? No
- Points: 2400

### Boss: Hive Carrier

- Level: 5-2 (Copper Flats)
- Look and size: a long carrier with wide hangar wings and amber markings, 0.22 x 0.3; two hangars (0.16 x 0.18, 30
  health, 500 points each)
- Health: 110 (core)
- Phases:
    1. Until both hangars are destroyed, the core is armored: sways at 0.14
    2. Down to 50% of the core's health: sways at 0.16
    3. Until the end: sways at 0.2
- Attacks per phase:
    1. Each hangar: a fan of 3 shots 12° apart swinging 25° left and right every 1.2 s, speed 0.5; The core: an aimed
       shot every 2 s, speed 0.6
    2. The core: a 3-arm spiral (every 0.14 s), speed 0.45
    3. The core: 5 aimed shots 8° apart every 1.4 s, speed 0.65 and a ring of 14 every 2 s, turning, speed 0.4
- Weak points: both hangars
- Time limit? No
- Points: 3000

### Boss: Hover Tank

- Level: 5-3 (Brine Pools)
- Look and size: a heavy gunboat block with a cyan reactor and a prow gun, 0.3 x 0.3; two turrets (0.12 x 0.15, 30
  health, 500 points each)
- Health: 110 (core)
- Phases:
    1. Until both turrets are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.14
- Attacks per phase:
    1. Each turret: 3 aimed shots in a row every 1.8 s, speed 0.65; The core: a ring of 8 every 2.4 s, turning, speed
       0.38
    2. The core: a fan of 5 shots 14° apart swinging 30° left and right every 1.1 s, speed 0.5 and an aimed heavy shot
       every 1.8 s, speed 0.55
- Weak points: both turrets
- Time limit? No
- Points: 2800

### Boss: Cryo Fortress

- Level: 5-4 (Mineral Dusk)
- Look and size: a fortress block with an icy blue reactor and a command tower, 0.3 x 0.26; two cannons (0.12 x 0.15, 35
  health, 600 points each)
- Health: 110 (core)
- Phases:
    1. Until both cannons are destroyed, the core is armored: sways at 0.08
    2. Until the end: sways at 0.12
- Attacks per phase:
    1. Each cannon: a ring of 6 every 1.6 s, turning, speed 0.42; The core: an aimed heavy shot every 2.2 s, speed 0.5
    2. The core: a 3-arm spiral (every 0.14 s), speed 0.45 and a fan of 5 shots 15° apart every 2 s, speed 0.5
- Weak points: both cannons
- Time limit? No
- Points: 2800

### Boss: Sentry Grid

- Level: 5-5 (Dust Storm)
- Look and size: a rounded sentry ship around a big cyan reactor, 0.24 x 0.24; two outer nodes (0.1 x 0.1, 22 health,
  400 points each) and two inner nodes (0.1 x 0.1, 22 health, 400 points each)
- Health: 110 (core)
- Phases:
    1. Until both outer nodes are destroyed, the core is armored: sways at 0.08
    2. Until both inner nodes are destroyed, the core is armored: sways at 0.12
    3. Until the end: sways at 0.16
- Attacks per phase:
    1. Each outer node: an aimed shot every 1.4 s, speed 0.65; Each inner node: a ring of 6 every 2 s, turning, speed
       0.4
    2. Each inner node: 2 aimed shots in a row every 1.4 s, speed 0.65; The core: a fan of 5 shots 15° apart every 2 s,
       speed 0.45
    3. The core: a 3-arm spiral (every 0.13 s), speed 0.45 and 3 aimed shots 10° apart every 1.6 s, speed 0.65
- Weak points: both outer nodes and both inner nodes
- Time limit? No
- Points: 3000

### Boss: Leviathan

- Level: 5-6 (Night Crust)
- Look and size: an arrowhead battleship (boss candidate #196, in real 3D): a long grey hull, two red reactors by the
  stern tower, turrets on its wings and nodes at their tips, 0.45 x 0.59; two turrets (0.13 x 0.15, 25 health, 500
  points each), two nodes (0.07 x 0.08, 20 health, 400 points each) and two reactors (0.1 x 0.12, 20 health, 500 points
  each)
- Health: 130 (core)
- Phases:
    1. Until both turrets and both nodes are destroyed, the core is armored: sways at 0.07
    2. Until both reactors are destroyed, the core is armored: sways at 0.1
    3. Until the end: sways at 0.13
- Attacks per phase:
    1. Each turret: 3 aimed shots in a row every 1.7 s, speed 0.65; Each node: a fan of 3 shots 18° apart every 2.2 s,
       speed 0.45
    2. Each reactor: a ring of 12 every 2 s, turning, speed 0.4; The core: 2 aimed heavy shots in a row every 1.8 s,
       speed 0.6
    3. The core: a 3-arm spiral (every 0.13 s), speed 0.45 and a fan of 7 shots 12° apart swinging 30° left and right
       every 1.6 s, speed 0.52
- Weak points: both turrets, both nodes and both reactors
- Time limit? No
- Points: 8500

### Boss: Relay Array

- Level: 6-1 (Bright Ridges)
- Look and size: a cross-shaped relay ship with a tall tower and a blue reactor, 0.3 x 0.24; two dishes (0.14 x 0.14, 35
  health, 600 points each)
- Health: 110 (core)
- Phases:
    1. Until both dishes are destroyed, the core is armored: sways at 0.1
    2. Until the end: sways at 0.14
- Attacks per phase:
    1. Each dish: a ring of 8 every 2.2 s, turning, speed 0.38; The core: an aimed shot every 1.6 s, speed 0.6
    2. The core: a 2-arm spiral (every 0.1 s), speed 0.48 and a fan of 3 heavy shots 25° apart every 2.4 s, speed 0.4
- Weak points: both dishes
- Time limit? No
- Points: 3000

### Boss: Scavenger

- Level: 6-2 (Striped Gullies)
- Look and size: a delta-winged salvager with a command tower and ochre markings, 0.2 x 0.27; two batterys (0.2 x 0.13,
  35 health, 600 points each)
- Health: 110 (core)
- Phases:
    1. Until both batterys are destroyed, the core is armored: sways at 0.12
    2. Down to 50% of the core's health: sways at 0.16
    3. Until the end: sways at 0.2
- Attacks per phase:
    1. Each battery: a fan of 4 shots 12° apart swinging 25° left and right every 1.3 s, speed 0.5; The core: an aimed
       shot every 2 s, speed 0.6
    2. The core: 5 aimed shots 10° apart every 1.4 s, speed 0.6 and a ring of 10 every 2.2 s, turning, speed 0.4
    3. The core: a 2-arm spiral (every 0.09 s), speed 0.5 and 2 aimed heavy shots in a row every 2 s, speed 0.55
- Weak points: both batterys
- Time limit? No
- Points: 3000

### Boss: Mine Carrier

- Level: 6-3 (Ochre Walls)
- Look and size: a heavy carrier with four engines and a purple reactor, 0.34 x 0.28; two launchers (0.12 x 0.12, 35
  health, 600 points each)
- Health: 130 (core)
- Phases:
    1. Until both launchers are destroyed, the core is armored: sways at 0.1
    2. Down to 50% of the core's health: sways at 0.14
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. Each launcher: a fan of 3 shots 20° apart every 1.8 s, speed 0.5; The core: an aimed heavy shot every 2.4 s,
       speed 0.5
    2. The core: a ring of 10 every 1.6 s, turning, speed 0.4 and 3 aimed shots in a row every 2 s, speed 0.65
    3. The core: a 3-arm spiral (every 0.13 s), speed 0.45 and a fan of 5 heavy shots 18° apart every 2.2 s, speed 0.45
- Weak points: both launchers
- Time limit? No
- Points: 3500

### Boss: Foundry

- Level: 6-4 (Red Dusk)
- Look and size: a heavy foundry block around a big molten reactor, 0.28 x 0.3; two presses (0.12 x 0.14, 35 health, 600
  points each)
- Health: 140 (core)
- Phases:
    1. Until both presses are destroyed, the core is armored: sways at 0.08
    2. Down to 50% of the core's health: sways at 0.12
    3. Until the end: sways at 0.16
- Attacks per phase:
    1. Each press: a fan of 3 heavy shots 20° apart every 2 s, speed 0.42; The core: an aimed shot every 1.6 s, speed
       0.6
    2. The core: a ring of 12 every 1.5 s, turning, speed 0.4 and 3 aimed shots in a row every 2 s, speed 0.65
    3. The core: a 3-arm spiral (every 0.12 s), speed 0.45 and a fan of 5 heavy shots 18° apart every 2.4 s, speed 0.4
- Weak points: both presses
- Time limit? No
- Points: 3400

### Boss: Gunship Prime

- Level: 6-5 (Rainbow Breaks)
- Look and size: a long heavy gunship with a tower, prow guns and an amber reactor, 0.24 x 0.33; two cannons (0.1 x
  0.18, 30 health, 500 points each) and two engines (0.12 x 0.12, 30 health, 500 points each)
- Health: 140 (core)
- Phases:
    1. Until both cannons are destroyed, the core is armored: sways at 0.08
    2. Until both engines are destroyed, the core is armored: sways at 0.12
    3. Until the end: sways at 0.16
- Attacks per phase:
    1. Each cannon: 3 aimed shots in a row every 1.8 s, speed 0.65; Each engine: a fan of 3 shots 20° apart every 2 s,
       speed 0.45
    2. Each engine: a ring of 10 every 2 s, turning, speed 0.4; The core: 2 aimed heavy shots in a row every 2 s, speed
       0.55
    3. The core: a 3-arm spiral (every 0.12 s), speed 0.46 and a fan of 5 shots 14° apart swinging 30° left and right
       every 1.6 s, speed 0.5
- Weak points: both cannons and both engines
- Time limit? No
- Points: 3600

### Boss: Colossus

- Level: 6-6 (Dark Strata)
- Look and size: a huge armored fortress block with four engines, a tower, prow guns and a glowing furnace, 0.34 x 0.3;
  two outers (0.12 x 0.12, 30 health, 600 points each) and two inners (0.12 x 0.12, 30 health, 600 points each)
- Health: 150 (core)
- Phases:
    1. Until both outers are destroyed, the core is armored: sways at 0.08
    2. Until both inners are destroyed, the core is armored: sways at 0.12
    3. Until the end: sways at 0.15
- Attacks per phase:
    1. Each outer: 3 aimed shots in a row every 2 s, speed 0.7; Each inner: a fan of 3 shots 15° apart every 1.6 s,
       speed 0.5
    2. Each inner: a ring of 8 every 1.3 s, turning, speed 0.45; The core: a fan of 5 heavy shots 20° apart every 2.6 s,
       speed 0.4
    3. The core: a 4-arm spiral (every 0.16 s), speed 0.42 and 3 aimed shots 10° apart every 1.5 s, speed 0.7
- Weak points: both outers and both inners
- Time limit? No
- Points: 8000

### Boss: Grappler

- Level: 7-1 (Refinery)
- Look and size: a wedge-shaped salvage ship with a teal reactor, 0.26 x 0.26; two grapples (0.08 x 0.21, 20 health, 400
  points each) and two inner grapples (0.08 x 0.21, 20 health, 400 points each)
- Health: 130 (core)
- Phases:
    1. Until both grapples and both inner grapples are destroyed, the core is armored: sways at 0.1
    2. Down to 50% of the core's health: sways at 0.14
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. Each grapple: a fan of 3 shots 15° apart every 1.6 s, speed 0.5; Each inner grapple: an aimed shot every 1.4 s,
       speed 0.6
    2. The core: a ring of 12 every 1.6 s, turning, speed 0.4 and 2 aimed shots in a row every 1.5 s, speed 0.6
    3. The core: a 2-arm spiral (every 0.1 s), speed 0.5 and a fan of 5 heavy shots 18° apart every 2.6 s, speed 0.4
- Weak points: both grapples and both inner grapples
- Time limit? No
- Points: 3200

### Boss: Tugmaster

- Level: 7-2 (Tank Farm)
- Look and size: a squat space tug with a big red reactor, 0.3 x 0.28; two thrusters (0.12 x 0.19, 30 health, 500 points
  each) and a ram plate (0.22 x 0.08, 40 health, 700 points)
- Health: 130 (core)
- Phases:
    1. Until both thrusters are destroyed, the core is armored: sways at 0.08
    2. Until the ram plate is destroyed, the core is armored: sways at 0.12
    3. Until the end: sways at 0.16
- Attacks per phase:
    1. Each thruster: 2 aimed shots in a row every 1.6 s, speed 0.6; Ram plate: a fan of 5 shots 15° apart every 2 s,
       speed 0.45
    2. Ram plate: a ring of 10 every 1.6 s, turning, speed 0.4; The core: a fan of 3 heavy shots 30° apart every 2.2 s,
       speed 0.4
    3. The core: a 2-arm spiral (every 0.1 s), speed 0.48 and 3 aimed shots in a row every 2 s, speed 0.65
- Weak points: both thrusters and the ram plate
- Time limit? No
- Points: 3500

### Boss: Magma Rig

- Level: 7-3 (Smelter)
- Look and size: a mining rig block around a molten reactor, with smoke stacks, 0.3 x 0.28; two furnaces (0.12 x 0.14,
  30 health, 500 points each) and two cannons (0.1 x 0.16, 30 health, 500 points each)
- Health: 150 (core)
- Phases:
    1. Until both furnaces are destroyed, the core is armored: sways at 0.08
    2. Until both cannons are destroyed, the core is armored: sways at 0.1
    3. Until the end: sways at 0.14
- Attacks per phase:
    1. Each furnace: a ring of 8 every 2 s, turning, speed 0.38; Each cannon: an aimed shot every 1.6 s, speed 0.65
    2. Each cannon: 3 aimed shots in a row every 1.8 s, speed 0.65; The core: a fan of 5 heavy shots 18° apart every 2.4
       s, speed 0.4
    3. The core: a 3-arm spiral (every 0.12 s), speed 0.45 and a ring of 14 every 2 s, turning, speed 0.38 and an aimed
       shot every 1.6 s, speed 0.65
- Weak points: both furnaces and both cannons
- Time limit? No
- Points: 4000

### Boss: Dreadnought

- Level: 7-4 (Pipe Maze)
- Look and size: a long battleship with a central tower, a prow gun and red markings, 0.24 x 0.37; two front turrets
  (0.12 x 0.12, 25 health, 500 points each), two rear turrets (0.12 x 0.12, 25 health, 500 points each) and a bow gun
  (0.08 x 0.11, 35 health, 700 points)
- Health: 150 (core)
- Phases:
    1. Until both front turrets and both rear turrets are destroyed, the core is armored: sways at 0.08
    2. Until the bow gun is destroyed, the core is armored: sways at 0.1
    3. Until the end: sways at 0.15
- Attacks per phase:
    1. Each front turret: 2 aimed shots in a row every 1.8 s, speed 0.6; Each rear turret: a fan of 3 shots 20° apart
       every 2.2 s, speed 0.45; Bow gun: an aimed heavy shot every 2.6 s, speed 0.5
    2. Bow gun: a fan of 5 shots 12° apart swinging 30° left and right every 1 s, speed 0.5; The core: a ring of 10
       every 2 s, turning, speed 0.4
    3. The core: a 3-arm spiral (every 0.12 s), speed 0.45 and 3 aimed shots 10° apart every 1.6 s, speed 0.65
- Weak points: both front turrets, both rear turrets and the bow gun
- Time limit? No
- Points: 4000

### Boss: Flare Rig

- Level: 7-5 (Flare Stacks)
- Look and size: a flare rig (boss candidate #185, in real 3D): a dark hull lit amber, spiked flak towers, missile
  launchers and gun pods, 0.38 x 0.35; two guns (0.11 x 0.11, 20 health, 400 points each), two launchers (0.09 x 0.13,
  20 health, 400 points each) and two flaks (0.11 x 0.1, 20 health, 400 points each)
- Health: 165 (core)
- Phases:
    1. Until both guns are destroyed, the core is armored: sways at 0.09
    2. Until both launchers are destroyed, the core is armored: sways at 0.12
    3. Until the end: sways at 0.16
- Attacks per phase:
    1. Each gun: 2 aimed shots in a row every 1.5 s, speed 0.65; Each flak: a fan of 3 shots 20° apart every 2 s, speed
       0.5
    2. Each launcher: 2 aimed heavy shots in a row every 2 s, speed 0.55; Each flak: a ring of 10 every 2.4 s, turning,
       speed 0.4
    3. The core: a 3-arm spiral (every 0.14 s), speed 0.45 and 3 aimed shots in a row every 1.9 s, speed 0.6
- Weak points: both guns, both launchers and both flaks
- Time limit? No
- Points: 4300

### Boss: Crucible

- Level: 7-6 (Meltdown)
- Look and size: a smelting block (boss candidate #157, in real 3D): a pale green armored box with a funnel at the
  stern, dish furnaces on deck and beacons at the bow, 0.37 x 0.45; two beacons (0.07 x 0.07, 30 health, 600 points
  each) and two furnaces (0.1 x 0.09, 30 health, 600 points each)
- Health: 170 (core)
- Phases:
    1. Until both furnaces are destroyed, the core is armored: sways at 0.09
    2. Down to 50% of the core's health: sways at 0.13
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. Each beacon: 2 aimed shots in a row every 1.5 s, speed 0.7; Each furnace: a ring of 12 every 2.3 s, turning,
       speed 0.38
    2. The core: a 3-arm spiral (every 0.15 s), speed 0.46; Each beacon: a fan of 3 shots 18° apart every 1.8 s, speed
       0.55
    3. The core: a ring of 16 every 1.4 s, turning, speed 0.4 and 3 aimed heavy shots in a row every 2 s, speed 0.6;
       Each beacon: an aimed shot every 1.6 s, speed 0.7
- Weak points: both beacons and both furnaces
- Time limit? No
- Points: 9000

### Boss: Executor

- Level: 8-1 (Neon City)
- Look and size: a heavy prow-shaped command ship with a violet reactor, 0.28 x 0.3; two generators (0.12 x 0.12, 30
  health, 500 points each) and two blades (0.1 x 0.22, 30 health, 500 points each)
- Health: 160 (core)
- Phases:
    1. Until both generators are destroyed, the core is armored: sways at 0.1
    2. Down to 50% of the core's health: sways at 0.14
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. Each generator: a ring of 10 every 2.2 s, turning, speed 0.38; Each blade: 2 aimed shots in a row every 1.6 s,
       speed 0.65
    2. The core: a 3-arm spiral (every 0.14 s), speed 0.45; Each blade: a fan of 3 shots 18° apart every 1.8 s, speed
       0.5
    3. The core: a ring of 14 every 1.5 s, turning, speed 0.4 and 3 aimed heavy shots in a row every 2.2 s, speed 0.55;
       Each blade: an aimed shot every 1.5 s, speed 0.7
- Weak points: both generators and both blades
- Time limit? No
- Points: 4500

### Boss: Interdictor

- Level: 8-2 (Downtown)
- Look and size: a blue interceptor carrier (boss candidate #125, in real 3D): a rounded armored hull, sensor dishes on
  its wings, cannons at the bow, 0.29 x 0.33; two cannons (0.05 x 0.08, 30 health, 500 points each) and two dishs (0.07
  x 0.1, 30 health, 500 points each)
- Health: 160 (core)
- Phases:
    1. Until both dishs are destroyed, the core is armored: sways at 0.12
    2. Until the end: sways at 0.16
- Attacks per phase:
    1. Each cannon: 2 aimed shots in a row every 1.4 s, speed 0.7; Each dish: a fan of 5 shots 12° apart swinging 20°
       left and right every 2 s, speed 0.5
    2. The core: a 3-arm spiral (every 0.14 s), speed 0.45; Each cannon: an aimed shot every 1.6 s, speed 0.7
- Weak points: both cannons and both dishs
- Time limit? No
- Points: 4200

### Boss: Nightwatch

- Level: 8-3 (Skyline)
- Look and size: a black gunboat traced with cyan lights (boss candidate #122, in real 3D), turrets on deck and guns on
  its flanks, 0.25 x 0.33; two guns (0.06 x 0.07, 30 health, 500 points each) and two turrets (0.06 x 0.09, 30 health,
  500 points each)
- Health: 165 (core)
- Phases:
    1. Until both turrets are destroyed, the core is armored: sways at 0.12
    2. Until both guns are destroyed, the core is armored: sways at 0.15
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. Each turret: 2 aimed sniper shots in a row every 1.3 s, speed 0.72; Each gun: a fan of 3 shots 16° apart every
       1.8 s, speed 0.5
    2. Each gun: a ring of 10 every 2.2 s, turning, speed 0.42; The core: 2 aimed heavy shots in a row every 1.8 s,
       speed 0.6
    3. The core: a 3-arm spiral (every 0.13 s), speed 0.46 and a fan of 5 shots 14° apart swinging 30° left and right
       every 1.5 s, speed 0.55
- Weak points: both guns and both turrets
- Time limit? No
- Points: 4400

### Boss: Arc Tower

- Level: 8-4 (Neon Rain)
- Look and size: a power station (boss candidate #180, in real 3D): a grey hull lit violet, spiked arc emitters and
  nodes glowing pink, 0.39 x 0.29; two emitters (0.13 x 0.11, 30 health, 500 points each) and two nodes (0.11 x 0.1, 30
  health, 500 points each)
- Health: 170 (core)
- Phases:
    1. Until both nodes are destroyed, the core is armored: sways at 0.1
    2. Down to 50% of the core's health: sways at 0.14
    3. Until the end: sways at 0.18
- Attacks per phase:
    1. Each emitter: a fan of 5 shots 12° apart swinging 25° left and right every 1.6 s, speed 0.55; Each node: a ring
       of 10 every 2.4 s, turning, speed 0.38
    2. The core: a 3-arm spiral (every 0.13 s), speed 0.46; Each emitter: 2 aimed shots in a row every 1.6 s, speed 0.7
    3. The core: a ring of 16 every 1.4 s, turning, speed 0.42 and 3 aimed heavy shots in a row every 2 s, speed 0.62
- Weak points: both emitters and both nodes
- Time limit? No
- Points: 4600

### Boss: Apex

- Level: 8-5 (Night Grid)
- Look and size: a flagship (boss candidate #113, in real 3D): a broad grey hull with a big dish on its bow deck, heavy
  cannon blocks on its wings and beam emitters at the stern, 0.43 x 0.29; two cannons (0.11 x 0.18, 30 health, 500
  points each) and two emitters (0.09 x 0.09, 30 health, 500 points each)
- Health: 175 (core)
- Phases:
    1. Until both emitters are destroyed, the core is armored: sways at 0.1
    2. Down to 50% of the core's health: sways at 0.15
    3. Until the end: sways at 0.19
- Attacks per phase:
    1. Each cannon: 3 aimed heavy shots in a row every 1.8 s, speed 0.6; Each emitter: a ring of 12 every 2.2 s,
       turning, speed 0.4
    2. The core: a 3-arm spiral (every 0.14 s), speed 0.46; Each cannon: a fan of 5 shots 12° apart swinging 25° left
       and right every 1.7 s, speed 0.55
    3. The core: a ring of 16 every 1.4 s, turning, speed 0.42 and 3 aimed heavy shots in a row every 1.9 s, speed 0.65;
       Each cannon: an aimed shot every 1.6 s, speed 0.7
- Weak points: both cannons and both emitters
- Time limit? No
- Points: 4800

### Boss: Overmind

- Level: 8-6 (The Core)
- Look and size: a rounded command ship around a huge glowing violet core, 0.3 x 0.3; two generators (0.12 x 0.12, 35
  health, 700 points each) and two cannons (0.1 x 0.16, 35 health, 700 points each)
- Health: 160 (core)
- Phases:
    1. Until both generators are destroyed, the core is armored: sways at 0.1
    2. Down to 50% of the core's health: sways at 0.14
    3. Until the end: sways at 0.2
- Attacks per phase:
    1. Each cannon: 2 aimed shots in a row every 1.5 s, speed 0.7; Each generator: a ring of 10 every 2.4 s, turning,
       speed 0.38
    2. The core: a 3-arm spiral (every 0.16 s), speed 0.45; Each cannon: a fan of 3 shots 20° apart every 1.8 s, speed
       0.55
    3. The core: a ring of 18 every 1.4 s, turning, speed 0.4 and 3 aimed heavy shots in a row every 2 s, speed 0.6;
       Each cannon: an aimed shot every 1.6 s, speed 0.7
- Weak points: both generators and both cannons
- Time limit? No
- Points: 10000

## Final bosses

> Placeholders chosen by Claude, not playtested: `data/bosses/final_bosses.json`, made from the plans in `data/bosses/final_plans.json` by
> `src/pewpy/makers/final_bosses/` (when a new model is saved in the Dev menu's browser, see `04-ui-audio.md`).

Each level ends with a final boss, after its mini boss (see `03-levels.md`): bigger (0.5 to 0.77 wide, about half
the screen for the last ones) and harder, with more parts and four phases. Same general rules as every boss (see
"Bosses" above).

- Looks: made by the makers (`src/pewpy/makers/bosses/`, see `04-ui-audio.md`) in real 3D, among the biggest, the bigger
  for the later levels: their core in `data/models/bosses/<name>.json`, their parts' drawings in
  `<name>_a.json`, `<name>_b.json`... Each hitbox is its drawing's size.
- Health, for a level of difficulty d (1 to 20): the core 110 + 14 (d - 1), each part 16 + 1.6 (d - 1) (rounded).
  Points: the core 4000 + 400 d, each part 300 + 30 d.
- Four attacks each (see the table): the front parts', the back parts', the core's and its rage's. Each attack gets
  faster and denser with the difficulty (at d 1 → at d 20):
    - aimed: 3 → 5 heavy shots in a row at the player every 1.6 → 1.1 s, speed 0.6 → 0.75
    - sniper: 2 → 4 blue shots in a row at the player every 1.5 → 1.1 s, speed 0.85 → 0.95
    - fan: 5 → 9 shots 12° apart, swinging 25° left and right, every 1.8 → 1.3 s, speed 0.45 → 0.55
    - ring: 12 → 20 all around, turning, every 2 → 1.4 s, speed 0.38 → 0.46
    - spiral: a 2 → 4-arm spiral (every 0.16 → 0.12 s), speed 0.42 → 0.48
    - wave: 3 → 5 snaking shots 20° apart every 1.6 → 1.2 s, speed 0.45 → 0.55
    - accel: 5 accelerating shots 8° apart at the player every 1.8 → 1.3 s, speed 0.55 → 0.7
    - curve: a ring of 8 → 12 curving shots every 1.8 → 1.3 s, speed 0.35 → 0.4
    - pellets: 7 → 11 pellets 6° apart at the player every 1.6 → 1.2 s, speed 0.6 → 0.7
    - laser: a beam (two, a quarter of the core's width either side of its middle, from the core) every 4.5 → 3 s,
      for 1 → 1.4 s, after its 1 s warning
    - missiles: 2 homing missiles 40° apart every 3.5 → 2.5 s
    - rockets: 3 rockets 25° apart every 2.6 → 1.8 s
    - cluster: 2 → 3 cluster bombs 30° apart every 3 → 2.2 s
- Parts: the front ones are the kinds of parts nearest the bottom of the screen (half of the kinds, rounded up), the
  back ones the others. A group of parts fires its attack in turn, part after part, about as often in all as two
  parts would (the more parts, the slower each).
- Phases (sway 0.08 + 0.004 d):
    1. Until the front parts are destroyed, the core is armored: they fire the front attack (and from d 8 the core
       fires "aimed" too)
    2. Until the back parts are destroyed, the core is armored: they fire the back attack, the core its attack
       (skipped when all the parts are front ones)
    3. Down to 50% of the core's health, sways 0.03 faster: the core fires its attack and the rage attack
    4. Until the end, sways 0.06 faster: the core fires the rage attack, the front attack and a spiral (a ring
       below d 6)
- Weak points: every part. Time limit? No.

| Level | Final boss | Level name | After the mini boss | Candidate | Size | Parts x health | Core health | Attacks (front, back, core, rage) | Points |
|-------|------------|------------|---------------------|-----------|------|----------------|-------------|-----------------------------------|--------|
| 1-1 | Avalanche | High Peaks | Sentinel | #167 | 0.5 x 0.287 | 6 x 16 | 110 | fan, aimed, laser, ring | 4400 |
| 1-2 | Frostjaw | Pine Ridge | Thresher | #187 | 0.513 x 0.287 | 8 x 18 | 124 | pellets, fan, wave, ring | 4800 |
| 1-3 | Iron Summit | Glacier Pass | Prowler | #070 | 0.547 x 0.313 | 4 x 19 | 138 | aimed, rockets, laser, fan | 5200 |
| 1-4 | Stormpeak | Stormcrest | Pulsar | #179 | 0.54 x 0.327 | 9 x 21 | 152 | wave, ring, curve, spiral | 5600 |
| 1-5 | Ridgebreaker | Dusk Peaks | Rockbreaker | #064 | 0.5 x 0.353 | 6 x 22 | 166 | rockets, pellets, laser, fan | 6000 |
| 1-6 | Highlord | Summit | Warden | #068 | 0.567 x 0.327 | 7 x 24 | 180 | aimed, cluster, laser, curve | 6400 |
| 2-1 | Ironbark | Greenwood | Patrol Drone | #063 | 0.5 x 0.373 | 11 x 19 | 138 | fan, accel, ring, pellets | 5200 |
| 2-2 | Thornback | Riverbend | Cyclone | #163 | 0.5 x 0.393 | 5 x 21 | 152 | pellets, curve, laser, wave | 5600 |
| 2-3 | Rootmaw | Deep Canopy | Siege Pod | #040 | 0.68 x 0.293 | 7 x 22 | 166 | rockets, wave, accel, spiral | 6000 |
| 2-4 | Wildfire | Autumn Wood | Delta Raider | #034 | 0.54 x 0.373 | 6 x 24 | 180 | accel, fan, laser, curve | 6400 |
| 2-5 | Grovekeeper | Twilight Grove | Breacher | #002 | 0.553 x 0.367 | 11 x 26 | 194 | curve, missiles, ring, laser | 6800 |
| 2-6 | Old Growth | Moonlit Woods | Harvester | #131 | 0.553 x 0.367 | 6 x 27 | 208 | wave, rockets, laser, accel | 7200 |
| 3-1 | Bogmaw | Lush Veld | Turbine | #099 | 0.527 x 0.387 | 6 x 22 | 166 | wave, pellets, curve, ring | 6000 |
| 3-2 | Mirelord | Winding Sands | Clamp Barge | #085 | 0.52 x 0.4 | 7 x 24 | 180 | missiles, fan, laser, wave | 6400 |
| 3-3 | Fenwraith | Kopje Country | Spire | #165 | 0.513 x 0.413 | 5 x 26 | 194 | curve, accel, wave, spiral | 6800 |
| 3-4 | Hydra | Acacia Dusk | Twin Fang | #138 | 0.58 x 0.373 | 5 x 27 | 208 | wave, cluster, laser, curve | 7200 |
| 3-5 | Marsh Titan | Long Grass | Frigate | #028 | 0.607 x 0.373 | 9 x 29 | 222 | pellets, missiles, accel, laser | 7600 |
| 3-6 | Drowned King | Veld by Night | Tidebreaker | #109 | 0.567 x 0.427 | 9 x 30 | 236 | curve, wave, laser, missiles | 8000 |
| 4-1 | Scarecrow | Harvest Dusk | Picket | #042 | 0.64 x 0.4 | 8 x 26 | 194 | pellets, rockets, fan, laser | 6800 |
| 4-2 | Combine | Golden Fields | Bulwark | #074 | 0.673 x 0.387 | 11 x 27 | 208 | fan, accel, laser, cluster | 7200 |
| 4-3 | Locust | Lavender Rows | Borer | #083 | 0.7 x 0.387 | 10 x 29 | 222 | missiles, pellets, curve, spiral | 7600 |
| 4-4 | Granary | Orchard Country | Silo Hauler | #066 | 0.607 x 0.447 | 10 x 30 | 236 | cluster, aimed, laser, wave | 8000 |
| 4-5 | Harrowmaster | Hay Moon | Bastion | #010 | 0.647 x 0.427 | 9 x 32 | 250 | accel, rockets, laser, curve | 8400 |
| 4-6 | Black Harvest | Last Harvest | Reaper | #103 | 0.74 x 0.373 | 10 x 34 | 264 | curve, missiles, laser, accel | 8800 |
| 5-1 | Maelstrom | Rust Pan | Enforcer | #024 | 0.66 x 0.427 | 10 x 29 | 222 | wave, curve, ring, laser | 7600 |
| 5-2 | Man O' War | Copper Flats | Hive Carrier | #039 | 0.633 x 0.447 | 8 x 30 | 236 | missiles, wave, laser, pellets | 8000 |
| 5-3 | Typhoon | Brine Pools | Hover Tank | #003 | 0.687 x 0.413 | 8 x 32 | 250 | curve, accel, wave, laser | 8400 |
| 5-4 | Tsunami | Mineral Dusk | Cryo Fortress | #096 | 0.527 x 0.553 | 8 x 34 | 264 | wave, cluster, laser, spiral | 8800 |
| 5-5 | Abyssal | Dust Storm | Sentry Grid | #058 | 0.607 x 0.493 | 7 x 35 | 278 | sniper, missiles, curve, laser | 9200 |
| 5-6 | Kraken | Night Crust | Leviathan | #102 | 0.5 x 0.6 | 4 x 37 | 292 | wave, rockets, laser, curve | 9600 |
| 6-1 | Mesa | Bright Ridges | Relay Array | #152 | 0.713 x 0.433 | 10 x 32 | 250 | rockets, sniper, laser, fan | 8400 |
| 6-2 | Dust Devil | Striped Gullies | Scavenger | #191 | 0.72 x 0.44 | 12 x 34 | 264 | curve, pellets, spiral, accel | 8800 |
| 6-3 | Landslide | Ochre Walls | Mine Carrier | #183 | 0.74 x 0.467 | 10 x 35 | 278 | cluster, rockets, laser, wave | 9200 |
| 6-4 | Basilisk | Red Dusk | Foundry | #048 | 0.573 x 0.607 | 6 x 37 | 292 | accel, sniper, laser, curve | 9600 |
| 6-5 | Sandworm | Rainbow Breaks | Gunship Prime | #094 | 0.607 x 0.573 | 9 x 38 | 306 | missiles, wave, curve, laser | 10000 |
| 6-6 | Monolith | Dark Strata | Colossus | #031 | 0.553 x 0.633 | 8 x 40 | 320 | sniper, cluster, laser, accel | 10400 |
| 7-1 | Furnace | Refinery | Grappler | #158 | 0.733 x 0.48 | 10 x 35 | 278 | fan, rockets, laser, pellets | 9200 |
| 7-2 | Smokestack | Tank Farm | Tugmaster | #156 | 0.66 x 0.533 | 8 x 37 | 292 | cluster, accel, curve, laser | 9600 |
| 7-3 | Slag King | Smelter | Magma Rig | #047 | 0.593 x 0.6 | 10 x 38 | 306 | pellets, missiles, laser, wave | 10000 |
| 7-4 | Forgemaster | Pipe Maze | Dreadnought | #084 | 0.673 x 0.54 | 10 x 40 | 320 | rockets, sniper, laser, curve | 10400 |
| 7-5 | Inferno | Flare Stacks | Flare Rig | #043 | 0.607 x 0.613 | 8 x 42 | 334 | curve, cluster, laser, accel | 10800 |
| 7-6 | Reactor | Meltdown | Crucible | #049 | 0.647 x 0.593 | 10 x 43 | 348 | accel, missiles, laser, wave | 11200 |
| 8-1 | Neon Tyrant | Neon City | Executor | #110 | 0.687 x 0.6 | 4 x 38 | 306 | sniper, accel, laser, curve | 10000 |
| 8-2 | Gridlock | Downtown | Interdictor | #186 | 0.673 x 0.613 | 11 x 40 | 320 | missiles, pellets, laser, wave | 10400 |
| 8-3 | Blackout | Skyline | Nightwatch | #081 | 0.707 x 0.587 | 8 x 42 | 334 | curve, rockets, laser, accel | 10800 |
| 8-4 | Skybreaker | Neon Rain | Arc Tower | #072 | 0.767 x 0.553 | 11 x 43 | 348 | wave, sniper, laser, cluster | 11200 |
| 8-5 | Sovereign | Night Grid | Apex | #121 | 0.74 x 0.607 | 8 x 45 | 362 | accel, missiles, laser, curve | 11600 |
| 8-6 | Singularity | The Core | Overmind | #155 | 0.767 x 0.6 | 7 x 46 | 376 | curve, cluster, laser, spiral | 12000 |
