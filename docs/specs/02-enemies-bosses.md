# 02 — Enemies: bosses

Part of `02-enemies.md` (the rules every enemy follows are there). Units: see `00-vision.md`.

Every level has two bosses of its own (see `03-levels.md`): a **mini boss** halfway, and a bigger, harder **final
boss** at the end. *(placeholder: every boss's numbers; not playtested)*

## Rules for every boss

- **BOS-1** A boss shall be a core with destructible parts mounted on it. Each part shall be hit like an enemy of its
  own (shots, the laser, missiles and their splash, secondary weapons), give its own points and drop a pickup 30% of
  the time. The core shall always drop a pickup when destroyed.
- **BOS-2** Destroying the core shall destroy the parts left, without their points, and end the fight.
- **BOS-3** Entry: a boss shall come down from above the screen (ENM-1) at 0.25 and stop at y = 0.55. Until it stops,
  neither it nor its parts shall shoot or be hurt (shots and the laser stop at them, harmlessly).
- **BOS-4** Once stopped, a boss shall sway sideways at its phase's sway speed (×W), right first, turning back where it
  (its parts included) would leave the play area's width. It shall never leave the screen.
- **BOS-5** Phases: a boss shall go through its phases in order. Each phase has its own guns and sway speed. A phase
  shall end when the parts it names are all destroyed, or when the core's health falls below the share of its full
  health it names; the last phase lasts until the end. When a phase ends, the next one shall start in the same frame.
- **BOS-6** At the start of each phase (its first one included) the core shall flash white (blinking every 0.1 s) and
  not shoot for 1.2 s.
- **BOS-7** Armored: in an armored phase the core shall not be hurt and shall look darker; its parts must be destroyed
  first. The player's weapons shall go through it as if it were not there: shots, missiles and the laser fly on to
  the parts behind it, and neither the homing missiles nor the secondary weapons aim at it.
- **BOS-8** Parts cover the core: a shot (or the laser, or a secondary weapon's aim) at a column of the core over
  which a living part is mounted shall fly over the core up to that part, as seen from above; a part in front of
  another shall be hit first, the one behind once the first is destroyed.
- **BOS-9** Guns: each gun shall belong to the core or to a part, and shall stop when its part is destroyed. A boss's
  guns shall fire even while it is off the play area, and their timing shall not drift (a late shot shortens the next
  wait).
- **BOS-10** When several parts fire a gun "taking turns", each of them shall fire it at the gun's interval, their
  first shots spread evenly over the interval in the order listed.
- **BOS-11** Gun patterns:
    - **aimed**: shots centred on the direction of the player;
    - **fan**: shots centred on straight down; a fan "swinging" N° left and right has its middle at
      N × sin(2π × age / 2 s);
    - **ring**: shots evenly all around, the first one straight down (unless the ring is turned);
    - **turned N° more each time**: the whole pattern turns by N° after each shot (positive towards +x);
    - **spiral**: a small ring fired very often while turning;
    - **N times in a row**: a volley of N shots, 0.15 s apart unless stated;
    - "first after N s": the gun's first shot comes N s after the phase's 1.2 s pause; otherwise right after it.
- **BOS-12** When hit, a boss and its parts shall get brighter for a moment instead of flashing white (it is shot at
  all the time).
- **BOS-13** Ramming a boss or one of its parts shall do the player 2 damage and not hurt the boss.
- **BOS-14** A boss shall explode in 5 blasts: one in the middle 1.3 times its size, and four of 0.6 to 0.7 times its
  size around it.
- **BOS-15** Health bar: while a boss is on screen, its name and its health (core and parts together) shall show at
  the top of the screen (see `04-ui-audio.md`).
- **BOS-16** Laser guns (final bosses): a laser shall fire red beams (ENM-12) straight down from under its core or
  part, which follow the boss as it sways. Each beam shall be announced 1 s before by a thin harmless red beam
  (0.008 wide, see-through) in the same place; the beam then fires for its duration. A beam and its warning shall
  vanish when their core or part is destroyed.
- **BOS-17** Projectile guns (final bosses): a gun may launch rockets (starting at 0.25 in its direction), homing
  missiles or cluster bombs (falling at 0.3 in its direction) (ENM-14) instead of shots.
- **BOS-18** Destroying a mini boss shall make every enemy shot vanish; the level goes on. Destroying a final boss
  ends the level (see `03-levels.md`).

## Mini bosses

- **BOS-19** Each mini boss shall be as follows. Parts are named by their kind and number; "health" and "points" of the
  core and of each part are separate. In each phase, the guns listed fire together.

### Boss: Sentinel

- Level 1-1 (High Peaks), mini boss.
- Look: a narrow patrol platform with wide solar wings and a command tower, a reactor glowing on each wing; 0.287 × 0.227.
- Core: 60 health, 1500 points.
- Parts (2): reactors 1 and 2 (reactors, 0.06 × 0.06, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 50%; sways at 0.1): the core fires a fan of 3 shots 20° apart around straight down, every 1.6 s, speed 0.45.
- Phase 2 (until the end; sways at 0.14): the core fires an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.55; the core fires a ring of 8 shots turned 22° more each time, every 3 s, speed 0.35, first after 1 s.

### Boss: Thresher

- Level 1-2 (Pine Ridge), mini boss.
- Look: a heavy hauler with cutting blades at its prow and turrets on its deck; 0.327 × 0.247.
- Core: 70 health, 1800 points.
- Parts (4): turrets 1 and 2 (turrets, 0.06 × 0.087, 25 health, 400 points each); turrets 3 and 4 (turrets, 0.047 × 0.067, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 50%; sways at 0.1): the core fires a fan of 4 shots 14° apart around straight down, every 1.4 s, speed 0.45.
- Phase 2 (until the end; sways at 0.14): the core fires 3 shots 10° apart aimed at the player, every 1.5 s, speed 0.55; the core fires a fan of 7 shots 12° apart around straight down, every 3 s, speed 0.35, first after 0.8 s.

### Boss: Prowler

- Level 1-3 (Glacier Pass), mini boss.
- Look: a swept-wing raider with a red reactor and a flak gun on each wing; 0.34 × 0.2.
- Core: 75 health, 1800 points.
- Parts (2): flaks 1 and 2 (flak guns, 0.06 × 0.087, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 50%; sways at 0.14): the core fires 3 shots 12° apart aimed at the player, every 1.5 s, speed 0.55.
- Phase 2 (until the end; sways at 0.2): the core fires a ring of 8 shots turned 22° more each time, every 1.8 s, speed 0.4; the core fires an aimed shot, every 1.2 s, speed 0.6, first after 0.6 s.

### Boss: Pulsar

- Level 1-4 (Stormcrest), mini boss.
- Look: a ring-shaped ship around a bright cyan reactor, gatlings on the ring; 0.26 × 0.3.
- Core: 90 health, 2200 points.
- Parts (2): gatlings 1 and 2 (gatlings, 0.02 × 0.047, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 50%; sways at 0.08): the core fires a ring of 10 shots turned 18° more each time, every 1.6 s, speed 0.38.
- Phase 2 (until the end; sways at 0.12): the core fires a 2-arm spiral of shots (a ring of 2 every 0.14 s, turning 12° each time), speed 0.42; the core fires a ring of 16 shots, every 3 s, speed 0.3, first after 1.5 s.

### Boss: Rockbreaker

- Level 1-5 (Dusk Peaks), mini boss.
- Look: a boxy mining ship with prow drills, powered by exposed reactors that shield its core; 0.327 × 0.273.
- Core: 60 health, 2000 points.
- Parts (4): reactors 1 and 2 (reactors, 0.06 × 0.06, 25 health, 400 points each); reactors 3 and 4 (reactors, 0.073 × 0.073, 25 health, 400 points each).
- Phase 1 (until reactors 1–4 are destroyed, the core armored; sways at 0.1): reactors 1–4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.8 s, speed 0.55; reactors 1–4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.8 s, speed 0.55, first after 0.9 s.
- Phase 2 (until the end; sways at 0.15): the core fires a fan of 5 shots 16° apart around straight down, every 1.6 s, speed 0.45; the core fires an aimed shot, 2 times in a row 0.15 s apart, every 2 s, speed 0.6, first after 0.8 s.

### Boss: Warden

- Level 1-6 (Summit), mini boss.
- Look: a wide battle station with side wings and a command tower, bristling with reactors, flak guns and beam emitters; 0.46 × 0.3.
- Core: 140 health, 5000 points.
- Parts (6): reactors 1 and 2 (reactors, 0.073 × 0.073, 25 health, 400 points each); flaks 3 and 4 (flak guns, 0.047 × 0.067, 25 health, 400 points each); emitters 5 and 6 (beam emitters, 0.06 × 0.12, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 55%; sways at 0.12): the core fires a fan of 5 shots 18° apart around straight down, every 1.6 s, speed 0.5; the core fires 2 shots 8° apart aimed at the player, 3 times in a row 0.15 s apart, every 2.2 s, speed 0.7, first after 0.8 s.
- Phase 2 (until the end; sways at 0.2): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning 13° each time), speed 0.45; the core fires an aimed heavy shot, every 1.8 s, speed 0.6, first after 0.5 s.

### Boss: Patrol Drone

- Level 2-1 (Greenwood), mini boss.
- Look: a cross-shaped patrol gunship with a tall tower and a gatling on each arm; 0.3 × 0.193.
- Core: 80 health, 2000 points.
- Parts (2): gatlings 1 and 2 (gatlings, 0.033 × 0.067, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 50%; sways at 0.14): the core fires 2 shots 10° apart aimed at the player, every 1.3 s, speed 0.6.
- Phase 2 (until the end; sways at 0.2): the core fires a fan of 5 shots 15° apart around straight down, every 1.6 s, speed 0.5; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 2.2 s, speed 0.65, first after 0.8 s.

### Boss: Cyclone

- Level 2-2 (Riverbend), mini boss.
- Look: a ring ship spinning its turrets around a sandy glowing core; 0.3 × 0.28.
- Core: 100 health, 2500 points.
- Parts (4): turrets 1 and 2 (turrets, 0.06 × 0.087, 25 health, 400 points each); turrets 3 and 4 (turrets, 0.06 × 0.087, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 66%; sways at 0.12): the core fires a 2-arm spiral of shots (a ring of 2 every 0.12 s, turning 12° each time), speed 0.42.
- Phase 2 (until the core's health falls below 33%; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning -14° each time), speed 0.44; the core fires an aimed shot, every 2 s, speed 0.6, first after 1 s.
- Phase 3 (until the end; sways at 0.2): the core fires a 4-arm spiral of shots (a ring of 4 every 0.16 s, turning 9° each time), speed 0.42; the core fires a ring of 12 shots, every 2.2 s, speed 0.35, first after 1.1 s.

### Boss: Siege Pod

- Level 2-3 (Deep Canopy), mini boss.
- Look: a rounded armored siege ship around a big orange reactor, smaller reactors on its hull; 0.3 × 0.3.
- Core: 110 health, 2500 points.
- Parts (4): reactors 1 and 2 (reactors, 0.06 × 0.06, 25 health, 400 points each); reactors 3 and 4 (reactors, 0.073 × 0.073, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 66%; sways at 0.1): the core fires a fan of 5 shots 15° apart around straight down, every 1.8 s, speed 0.45.
- Phase 2 (until the core's health falls below 33%; sways at 0.12): the core fires a 2-arm spiral of shots (a ring of 2 every 0.12 s, turning 11° each time), speed 0.45.
- Phase 3 (until the end; sways at 0.18): the core fires a ring of 12 shots turned 15° more each time, every 1.6 s, speed 0.4; the core fires an aimed heavy shot, every 2.2 s, speed 0.55, first after 0.8 s.

### Boss: Delta Raider

- Level 2-4 (Autumn Wood), mini boss.
- Look: a delta-winged raider with a teal reactor, twin cannons and flak guns on its wings; 0.407 × 0.24.
- Core: 110 health, 2600 points.
- Parts (4): flaks 1 and 2 (flak guns, 0.06 × 0.087, 25 health, 400 points each); cannons 3 and 4 (twin cannons, 0.047 × 0.1, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 66%; sways at 0.12): the core fires a fan of 5 shots 12° apart around straight down, its middle swinging 35° left and right, every 1.2 s, speed 0.5.
- Phase 2 (until the core's health falls below 33%; sways at 0.14): the core fires a fan of 3 shots 20° apart around straight down, its middle swinging 45° left and right, every 0.5 s, speed 0.45; the core fires an aimed shot, every 1.8 s, speed 0.6, first after 0.9 s.
- Phase 3 (until the end; sways at 0.18): the core fires a 2-arm spiral of shots (a ring of 2 every 0.1 s, turning 9° each time), speed 0.5; the core fires a fan of 5 heavy shots 18° apart around straight down, every 2.4 s, speed 0.4, first after 1 s.

### Boss: Breacher

- Level 2-5 (Twilight Grove), mini boss.
- Look: a wedge-shaped assault ship with a prow ram, gatlings and missile racks; 0.38 × 0.393.
- Core: 70 health, 2000 points.
- Parts (6): launchers 1 and 2 (missile racks, 0.047 × 0.053, 25 health, 400 points each); launchers 3 and 4 (missile racks, 0.047 × 0.053, 25 health, 400 points each); gatlings 5 and 6 (gatlings, 0.033 × 0.067, 25 health, 400 points each).
- Phase 1 (until gatlings 5 and 6 and launchers 1–4 are destroyed, the core armored; sways at 0.12): gatlings 5 and 6 and launchers 1–4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.55; gatlings 5 and 6 and launchers 1–4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.55, first after 0.8 s; the core fires a fan of 3 shots 18° apart around straight down, every 2.2 s, speed 0.45, first after 1.1 s.
- Phase 2 (until the end; sways at 0.18): the core fires 3 shots 12° apart aimed at the player, every 1.2 s, speed 0.6; the core fires a ring of 8 shots turned 22° more each time, every 2.4 s, speed 0.4, first after 0.6 s.

### Boss: Harvester

- Level 2-6 (Moonlit Woods), mini boss.
- Look: a heavy prow-shaped harvester with four engines and a green reactor, its deck lined with cannons and turrets; 0.567 × 0.447.
- Core: 100 health, 6000 points.
- Parts (10): cannons 1 and 2 (twin cannons, 0.06 × 0.133, 40 health, 800 points each); turrets 3 and 4 (turrets, 0.073 × 0.107, 40 health, 800 points each); turrets 5 and 6 (turrets, 0.073 × 0.107, 40 health, 800 points each); cannons 7 and 8 (twin cannons, 0.073 × 0.167, 40 health, 800 points each); cannons 9 and 10 (twin cannons, 0.073 × 0.167, 40 health, 800 points each).
- Phase 1 (until cannons 1, 2, 7, 8, 9, 10 and turrets 3–6 are destroyed, the core armored; sways at 0.12): cannons 1, 2, 7, 8, 9, 10 and turrets 3–6 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65; cannons 1, 2, 7, 8, 9, 10 and turrets 3–6 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65, first after 0.9 s; the core fires a fan of 3 heavy shots 25° apart around straight down, every 2.5 s, speed 0.4, first after 1.2 s.
- Phase 2 (until the end; sways at 0.18): the core fires a ring of 14 shots turned 13° more each time, every 2.2 s, speed 0.4; the core fires 3 shots 12° apart aimed at the player, every 1.4 s, speed 0.6, first after 0.7 s.

### Boss: Turbine

- Level 3-1 (Lush Veld), mini boss.
- Look: a ring-shaped ship around a glowing yellow turbine, missile racks and reactors on its rim; 0.3 × 0.293.
- Core: 110 health, 2600 points.
- Parts (4): reactors 1 and 2 (reactors, 0.073 × 0.073, 25 health, 400 points each); launchers 3 and 4 (missile racks, 0.047 × 0.053, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 66%; sways at 0.08): the core fires a 2-arm spiral of shots (a ring of 2 every 0.14 s, turning 12° each time), speed 0.42.
- Phase 2 (until the core's health falls below 33%; sways at 0.1): the core fires a 4-arm spiral of shots (a ring of 4 every 0.2 s, turning -9° each time), speed 0.4.
- Phase 3 (until the end; sways at 0.16): the core fires a ring of 12 shots turned 15° more each time, every 1.4 s, speed 0.42; the core fires an aimed heavy shot, every 2 s, speed 0.55, first after 0.7 s.

### Boss: Clamp Barge

- Level 3-2 (Winding Sands), mini boss.
- Look: a wide salvage barge with a command tower and coral markings, armed with cannons, flak and missile racks; 0.42 × 0.313.
- Core: 70 health, 2000 points.
- Parts (6): cannons 1 and 2 (twin cannons, 0.06 × 0.133, 25 health, 400 points each); flaks 3 and 4 (flak guns, 0.06 × 0.087, 25 health, 400 points each); launchers 5 and 6 (missile racks, 0.047 × 0.053, 25 health, 400 points each).
- Phase 1 (until launchers 5 and 6, cannons 1 and 2 and flaks 3 and 4 are destroyed, the core armored; sways at 0.12): launchers 5 and 6, cannons 1 and 2 and flaks 3 and 4 fire, taking turns, 2 shots 10° apart aimed at the player, every 1.6 s, speed 0.55; launchers 5 and 6, cannons 1 and 2 and flaks 3 and 4 fire, taking turns, 2 shots 10° apart aimed at the player, every 1.6 s, speed 0.55, first after 0.8 s; the core fires a fan of 3 shots 20° apart around straight down, every 2.2 s, speed 0.4, first after 1.1 s.
- Phase 2 (until the end; sways at 0.18): the core fires a ring of 10 shots turned 18° more each time, every 1.8 s, speed 0.4; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 1.6 s, speed 0.6, first after 0.8 s.

### Boss: Spire

- Level 3-3 (Kopje Country), mini boss.
- Look: a long command ship carrying a tall tower from stern to prow, cannons all along it; 0.353 × 0.56.
- Core: 120 health, 2800 points.
- Parts (8): cannons 1 and 2 (twin cannons, 0.06 × 0.133, 25 health, 400 points each); cannons 3 and 4 (twin cannons, 0.06 × 0.133, 25 health, 400 points each); cannons 5 and 6 (twin cannons, 0.047 × 0.1, 25 health, 400 points each); cannons 7 and 8 (twin cannons, 0.06 × 0.133, 25 health, 400 points each).
- Phase 1 (until the core's health falls below 66%; sways at 0.1): the core fires 3 shots 8° apart aimed at the player, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.65.
- Phase 2 (until the core's health falls below 33%; sways at 0.12): the core fires a 2-arm spiral of shots (a ring of 2 every 0.11 s, turning 11° each time), speed 0.46; the core fires a fan of 3 heavy shots 25° apart around straight down, every 2.4 s, speed 0.4, first after 1.2 s.
- Phase 3 (until the end; sways at 0.16): the core fires a ring of 16 shots turned 11° more each time, every 1.5 s, speed 0.4; the core fires a 3-arm spiral of shots (a ring of 3 every 0.16 s, turning -12° each time), speed 0.42, first after 0.5 s.

### Boss: Twin Fang

- Level 3-4 (Acacia Dusk), mini boss.
- Look: a wedge-shaped gunship with two fang-like prongs and rows of flak guns; 0.42 × 0.467.
- Core: 90 health, 2600 points.
- Parts (8): flaks 1 and 2 (flak guns, 0.06 × 0.087, 30 health, 500 points each); flaks 3 and 4 (flak guns, 0.06 × 0.087, 30 health, 500 points each); flaks 5 and 6 (flak guns, 0.047 × 0.067, 30 health, 500 points each); flaks 7 and 8 (flak guns, 0.06 × 0.087, 30 health, 500 points each).
- Phase 1 (until the core's health falls below 50%; sways at 0.12): flaks 1–8 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.6; flaks 1–8 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.6, first after 0.8 s; the core fires a fan of 3 shots 25° apart around straight down, every 2.2 s, speed 0.45, first after 1.1 s.
- Phase 2 (until the end; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.15 s, turning 12° each time), speed 0.42; flaks 1–8 fire, taking turns, a fan of 3 shots 15° apart around straight down, every 2 s, speed 0.5; flaks 1–8 fire, taking turns, a fan of 3 shots 15° apart around straight down, every 2 s, speed 0.5, first after 1 s.

### Boss: Frigate

- Level 3-5 (Long Grass), mini boss.
- Look: a long frigate with a command tower and a prow gun, turrets and flak along its deck; 0.34 × 0.567.
- Core: 90 health, 2400 points.
- Parts (8): turrets 1 and 2 (turrets, 0.047 × 0.067, 30 health, 500 points each); flaks 3 and 4 (flak guns, 0.047 × 0.067, 30 health, 500 points each); turrets 5 and 6 (turrets, 0.047 × 0.067, 30 health, 500 points each); turrets 7 and 8 (turrets, 0.047 × 0.067, 30 health, 500 points each).
- Phase 1 (until turrets 1, 2, 5, 6, 7, 8 and flaks 3 and 4 are destroyed, the core armored; sways at 0.1): turrets 1, 2, 5, 6, 7, 8 and flaks 3 and 4 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.6; turrets 1, 2, 5, 6, 7, 8 and flaks 3 and 4 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.6, first after 1 s; the core fires a fan of 5 shots 12° apart around straight down, every 2.4 s, speed 0.45, first after 0.5 s.
- Phase 2 (until the end; sways at 0.14): the core fires a fan of 3 heavy shots 30° apart around straight down, every 1.8 s, speed 0.45; the core fires 3 shots 10° apart aimed at the player, every 1.3 s, speed 0.6, first after 0.6 s.

### Boss: Tidebreaker

- Level 3-6 (Veld by Night), mini boss.
- Look: a heavy cruiser with a breakwater prow, cannons and flak batteries; 0.46 × 0.547.
- Core: 120 health, 7000 points.
- Parts (10): cannons 1 and 2 (twin cannons, 0.06 × 0.133, 40 health, 900 points each); flaks 3 and 4 (flak guns, 0.047 × 0.067, 40 health, 900 points each); flaks 5 and 6 (flak guns, 0.06 × 0.087, 40 health, 900 points each); flaks 7 and 8 (flak guns, 0.047 × 0.067, 40 health, 900 points each); cannons 9 and 10 (twin cannons, 0.047 × 0.1, 40 health, 900 points each).
- Phase 1 (until flaks 3–8 and cannons 1, 2, 9, 10 are destroyed, the core armored; sways at 0.1): flaks 3–8 and cannons 1, 2, 9, 10 fire, taking turns, a fan of 4 shots 12° apart around straight down, its middle swinging 30° left and right, every 1.1 s, speed 0.5; flaks 3–8 and cannons 1, 2, 9, 10 fire, taking turns, a fan of 4 shots 12° apart around straight down, its middle swinging 30° left and right, every 1.1 s, speed 0.5, first after 0.55 s; the core fires an aimed heavy shot, every 2.4 s, speed 0.55, first after 1 s.
- Phase 2 (until the core's health falls below 45%; sways at 0.14): the core fires a 2-arm spiral of shots (a ring of 2 every 0.1 s, turning 9° each time), speed 0.5; the core fires an aimed shot, every 1.2 s, speed 0.65, first after 0.6 s.
- Phase 3 (until the end; sways at 0.2): the core fires a ring of 16 shots turned 11° more each time, every 1.6 s, speed 0.42; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.7, first after 0.8 s.

### Boss: Picket

- Level 4-1 (Harvest Dusk), mini boss.
- Look: a slim picket ship with gun pods of twin cannons; 0.327 × 0.407.
- Core: 80 health, 2200 points.
- Parts (4): cannons 1 and 2 (twin cannons, 0.047 × 0.1, 25 health, 400 points each); cannons 3 and 4 (twin cannons, 0.06 × 0.133, 25 health, 400 points each).
- Phase 1 (until cannons 1–4 are destroyed, the core armored; sways at 0.1): cannons 1–4 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 1.7 s, speed 0.45; cannons 1–4 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 1.7 s, speed 0.45, first after 0.85 s; the core fires an aimed shot, every 2 s, speed 0.55, first after 0.5 s.
- Phase 2 (until the end; sways at 0.15): the core fires a ring of 12 shots turned 15° more each time, every 2 s, speed 0.4; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.6, first after 0.9 s.

### Boss: Bulwark

- Level 4-2 (Golden Fields), mini boss.
- Look: an armored ship with ramming plates in front and missile racks behind them; 0.367 × 0.373.
- Core: 90 health, 2400 points.
- Parts (6): launchers 1 and 2 (missile racks, 0.06 × 0.067, 30 health, 500 points each); launchers 3 and 4 (missile racks, 0.06 × 0.067, 30 health, 500 points each); launchers 5 and 6 (missile racks, 0.06 × 0.067, 30 health, 500 points each).
- Phase 1 (until launchers 1–6 are destroyed, the core armored; sways at 0.1): launchers 1–6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.6; launchers 1–6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.6, first after 0.75 s; the core fires a fan of 5 shots 18° apart around straight down, every 2.4 s, speed 0.4, first after 1.2 s.
- Phase 2 (until the end; sways at 0.14): the core fires a 2-arm spiral of shots (a ring of 2 every 0.12 s, turning 13° each time), speed 0.45; the core fires an aimed heavy shot, every 2 s, speed 0.55, first after 0.8 s.

### Boss: Borer

- Level 4-3 (Lavender Rows), mini boss.
- Look: a boring ship with a drill nose, beam emitters cutting the way ahead; 0.393 × 0.407.
- Core: 90 health, 2400 points.
- Parts (6): emitters 1 and 2 (beam emitters, 0.06 × 0.12, 30 health, 500 points each); emitters 3 and 4 (beam emitters, 0.06 × 0.12, 30 health, 500 points each); emitters 5 and 6 (beam emitters, 0.047 × 0.093, 30 health, 500 points each).
- Phase 1 (until emitters 1–6 are destroyed, the core armored; sways at 0.1): emitters 1–6 fire, taking turns, a ring of 8 shots turned 20° more each time, every 2 s, speed 0.38; emitters 1–6 fire, taking turns, a ring of 8 shots turned -20° more each time, every 2 s, speed 0.38, first after 1 s; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.6, first after 0.5 s.
- Phase 2 (until the end; sways at 0.15): the core fires a fan of 7 shots 12° apart around straight down, every 1.8 s, speed 0.45; the core fires an aimed heavy shot, every 1.6 s, speed 0.55, first after 0.8 s.

### Boss: Silo Hauler

- Level 4-4 (Orchard Country), mini boss.
- Look: a hauler carrying fuel silos, gatlings and a radar on its deck; 0.433 × 0.4.
- Core: 100 health, 2800 points.
- Parts (6): radars 1 and 2 (radars, 0.047 × 0.047, 35 health, 600 points each); gatlings 3 and 4 (gatlings, 0.033 × 0.067, 35 health, 600 points each); gatlings 5 and 6 (gatlings, 0.047 × 0.087, 35 health, 600 points each).
- Phase 1 (until gatlings 3–6 and radars 1 and 2 are destroyed, the core armored; sways at 0.1): gatlings 3–6 and radars 1 and 2 fire, taking turns, a ring of 6 shots turned 15° more each time, every 1.8 s, speed 0.4; gatlings 3–6 and radars 1 and 2 fire, taking turns, a ring of 6 shots turned -15° more each time, every 1.8 s, speed 0.4, first after 0.9 s; the core fires an aimed shot, 2 times in a row 0.15 s apart, every 2 s, speed 0.6, first after 0.5 s.
- Phase 2 (until the end; sways at 0.15): the core fires a fan of 5 shots 15° apart around straight down, its middle swinging 25° left and right, every 1.3 s, speed 0.5; the core fires a ring of 10 shots, every 2.5 s, speed 0.38, first after 1.2 s.

### Boss: Bastion

- Level 4-5 (Hay Moon), mini boss.
- Look: a fortress ship with thick walls and flak towers; 0.5 × 0.347.
- Core: 110 health, 2800 points.
- Parts (6): flaks 1 and 2 (flak guns, 0.047 × 0.067, 30 health, 500 points each); flaks 3 and 4 (flak guns, 0.06 × 0.087, 30 health, 500 points each); flaks 5 and 6 (flak guns, 0.06 × 0.087, 30 health, 500 points each).
- Phase 1 (until flaks 1–6 are destroyed, the core armored; sways at 0.08): flaks 1–6 fire, taking turns, 2 shots 10° apart aimed at the player, every 1.5 s, speed 0.6; flaks 1–6 fire, taking turns, 2 shots 10° apart aimed at the player, every 1.5 s, speed 0.6, first after 0.75 s; the core fires a fan of 3 heavy shots 25° apart around straight down, every 2.4 s, speed 0.4, first after 1.2 s.
- Phase 2 (until the end; sways at 0.12): the core fires a ring of 14 shots turned 13° more each time, every 1.8 s, speed 0.4; the core fires a fan of 5 shots 15° apart around straight down, its middle swinging 30° left and right, every 1.4 s, speed 0.5, first after 0.7 s.

### Boss: Reaper

- Level 4-6 (Last Harvest), mini boss.
- Look: a giant harvester with augers in front, flak guns and banks of missile racks; 0.487 × 0.387.
- Core: 120 health, 7500 points.
- Parts (8): flaks 1 and 2 (flak guns, 0.047 × 0.067, 25 health, 500 points each); launchers 3 and 4 (missile racks, 0.06 × 0.067, 25 health, 500 points each); launchers 5 and 6 (missile racks, 0.06 × 0.067, 20 health, 400 points each); launchers 7 and 8 (missile racks, 0.06 × 0.067, 20 health, 400 points each).
- Phase 1 (until launchers 5–8 are destroyed, the core armored; sways at 0.08): launchers 5–8 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.6; launchers 5–8 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.6, first after 0.8 s; launchers 5–8 fire, taking turns, a fan of 5 shots 14° apart around straight down, its middle swinging 25° left and right, every 2 s, speed 0.45, first after 0.4 s.
- Phase 2 (until flaks 1 and 2 and launchers 3 and 4 are destroyed, the core armored; sways at 0.12): flaks 1 and 2 and launchers 3 and 4 fire, taking turns, a ring of 10 shots turned 18° more each time, every 2.2 s, speed 0.38; flaks 1 and 2 and launchers 3 and 4 fire, taking turns, a ring of 10 shots turned -18° more each time, every 2.2 s, speed 0.38, first after 1.1 s; the core fires an aimed heavy shot, 2 times in a row 0.15 s apart, every 2 s, speed 0.55, first after 0.6 s.
- Phase 3 (until the end; sways at 0.15): the core fires a 3-arm spiral of shots (a ring of 3 every 0.15 s, turning 13° each time), speed 0.44; the core fires a fan of 5 shots 15° apart around straight down, its middle swinging 30° left and right, every 1.7 s, speed 0.5, first after 0.8 s.

### Boss: Enforcer

- Level 5-1 (Rust Pan), mini boss.
- Look: an enforcer gunship behind armor shields, a radar directing its flak; 0.313 × 0.36.
- Core: 90 health, 2400 points.
- Parts (4): flaks 1 and 2 (flak guns, 0.06 × 0.087, 35 health, 500 points each); radars 3 and 4 (radars, 0.06 × 0.06, 35 health, 500 points each).
- Phase 1 (until radars 3 and 4 and flaks 1 and 2 are destroyed, the core armored; sways at 0.12): the core fires an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.6; the core fires a fan of 3 shots 25° apart around straight down, every 2.4 s, speed 0.4, first after 1.2 s.
- Phase 2 (until the end; sways at 0.18): the core fires a ring of 10 shots turned 18° more each time, every 1.8 s, speed 0.42; the core fires 3 shots 10° apart aimed at the player, every 1.4 s, speed 0.65, first after 0.7 s.

### Boss: Hive Carrier

- Level 5-2 (Copper Flats), mini boss.
- Look: a carrier with two hangars, its swarms guided by radar dishes; 0.313 × 0.44.
- Core: 110 health, 3000 points.
- Parts (6): radars 1 and 2 (radars, 0.06 × 0.06, 30 health, 500 points each); radars 3 and 4 (radars, 0.047 × 0.047, 30 health, 500 points each); radars 5 and 6 (radars, 0.06 × 0.06, 30 health, 500 points each).
- Phase 1 (until radars 1–6 are destroyed, the core armored; sways at 0.14): radars 1–6 fire, taking turns, a fan of 3 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.2 s, speed 0.5; radars 1–6 fire, taking turns, a fan of 3 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.2 s, speed 0.5, first after 0.6 s; the core fires an aimed shot, every 2 s, speed 0.6, first after 1 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning 12° each time), speed 0.45.
- Phase 3 (until the end; sways at 0.2): the core fires 5 shots 8° apart aimed at the player, every 1.4 s, speed 0.65; the core fires a ring of 14 shots turned 13° more each time, every 2 s, speed 0.4, first after 0.7 s.

### Boss: Hover Tank

- Level 5-3 (Brine Pools), mini boss.
- Look: a heavy hover gunboat with gatling turrets around a reactor; 0.447 × 0.453.
- Core: 110 health, 2800 points.
- Parts (8): reactors 1 and 2 (reactors, 0.06 × 0.06, 30 health, 500 points each); gatlings 3 and 4 (gatlings, 0.047 × 0.087, 30 health, 500 points each); gatlings 5 and 6 (gatlings, 0.047 × 0.087, 30 health, 500 points each); gatlings 7 and 8 (gatlings, 0.047 × 0.087, 30 health, 500 points each).
- Phase 1 (until reactors 1 and 2 and gatlings 3–8 are destroyed, the core armored; sways at 0.1): reactors 1 and 2 and gatlings 3–8 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65; reactors 1 and 2 and gatlings 3–8 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65, first after 0.9 s; the core fires a ring of 8 shots turned 22° more each time, every 2.4 s, speed 0.38, first after 0.5 s.
- Phase 2 (until the end; sways at 0.14): the core fires a fan of 5 shots 14° apart around straight down, its middle swinging 30° left and right, every 1.1 s, speed 0.5; the core fires an aimed heavy shot, every 1.8 s, speed 0.55, first after 0.9 s.

### Boss: Cryo Fortress

- Level 5-4 (Mineral Dusk), mini boss.
- Look: a fortress ship with frosted cryo reactors and gatlings; 0.46 × 0.407.
- Core: 110 health, 2800 points.
- Parts (8): gatlings 1 and 2 (gatlings, 0.047 × 0.087, 35 health, 600 points each); gatlings 3 and 4 (gatlings, 0.047 × 0.087, 35 health, 600 points each); reactors 5 and 6 (reactors, 0.06 × 0.06, 35 health, 600 points each); reactors 7 and 8 (reactors, 0.073 × 0.073, 35 health, 600 points each).
- Phase 1 (until gatlings 1–4 and reactors 5–8 are destroyed, the core armored; sways at 0.08): gatlings 1–4 and reactors 5–8 fire, taking turns, a ring of 6 shots turned 10° more each time, every 1.6 s, speed 0.42; gatlings 1–4 and reactors 5–8 fire, taking turns, a ring of 6 shots turned -10° more each time, every 1.6 s, speed 0.42, first after 0.8 s; the core fires an aimed heavy shot, every 2.2 s, speed 0.5, first after 1.1 s.
- Phase 2 (until the end; sways at 0.12): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning 12° each time), speed 0.45; the core fires a fan of 5 shots 15° apart around straight down, every 2 s, speed 0.5, first after 1 s.

### Boss: Sentry Grid

- Level 5-5 (Dust Storm), mini boss.
- Look: a sentry ship laid out as a grid of missile-rack nodes; 0.38 × 0.36.
- Core: 110 health, 3000 points.
- Parts (6): launchers 1 and 2 (missile racks, 0.06 × 0.067, 22 health, 400 points each); launchers 3 and 4 (missile racks, 0.06 × 0.067, 22 health, 400 points each); launchers 5 and 6 (missile racks, 0.06 × 0.067, 22 health, 400 points each).
- Phase 1 (until launchers 3–6 are destroyed, the core armored; sways at 0.08): launchers 3–6 fire, taking turns, an aimed shot, every 1.4 s, speed 0.65; launchers 3–6 fire, taking turns, an aimed shot, every 1.4 s, speed 0.65, first after 0.7 s; launchers 1 and 2 fire, taking turns, a ring of 6 shots turned 20° more each time, every 2 s, speed 0.4, first after 0.3 s; launchers 1 and 2 fire, taking turns, a ring of 6 shots turned -20° more each time, every 2 s, speed 0.4, first after 1.3 s.
- Phase 2 (until launchers 1 and 2 are destroyed, the core armored; sways at 0.12): launchers 1 and 2 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.4 s, speed 0.65; launchers 1 and 2 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.4 s, speed 0.65, first after 0.7 s; the core fires a fan of 5 shots 15° apart around straight down, every 2 s, speed 0.45, first after 1 s.
- Phase 3 (until the end; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.13 s, turning 12° each time), speed 0.45; the core fires 3 shots 10° apart aimed at the player, every 1.6 s, speed 0.65, first after 0.8 s.

### Boss: Leviathan

- Level 5-6 (Night Crust), mini boss.
- Look: a long battleship lined with turrets from bow to stern; 0.42 × 0.587.
- Core: 130 health, 8500 points.
- Parts (10): turrets 1 and 2 (turrets, 0.06 × 0.087, 25 health, 500 points each); turrets 3 and 4 (turrets, 0.047 × 0.067, 25 health, 500 points each); turrets 5 and 6 (turrets, 0.06 × 0.087, 20 health, 500 points each); turrets 7 and 8 (turrets, 0.047 × 0.067, 20 health, 500 points each); turrets 9 and 10 (turrets, 0.047 × 0.067, 20 health, 500 points each).
- Phase 1 (until turrets 1–4 are destroyed, the core armored; sways at 0.07): turrets 1–4 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.7 s, speed 0.65; turrets 1–4 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.7 s, speed 0.65, first after 0.85 s; turrets 1–4 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 2.2 s, speed 0.45, first after 0.4 s; turrets 1–4 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 2.2 s, speed 0.45, first after 1.5 s.
- Phase 2 (until turrets 5–10 are destroyed, the core armored; sways at 0.1): turrets 5–10 fire, taking turns, a ring of 12 shots turned 15° more each time, every 2 s, speed 0.4; turrets 5–10 fire, taking turns, a ring of 12 shots turned -15° more each time, every 2 s, speed 0.4, first after 1 s; the core fires an aimed heavy shot, 2 times in a row 0.15 s apart, every 1.8 s, speed 0.6, first after 0.5 s.
- Phase 3 (until the end; sways at 0.13): the core fires a 3-arm spiral of shots (a ring of 3 every 0.13 s, turning 12° each time), speed 0.45; the core fires a fan of 7 shots 12° apart around straight down, its middle swinging 30° left and right, every 1.6 s, speed 0.52, first after 0.8 s.

### Boss: Relay Array

- Level 6-1 (Bright Ridges), mini boss.
- Look: a relay station of dish arrays, with beam emitters and a gatling; 0.473 × 0.373.
- Core: 110 health, 3000 points.
- Parts (6): emitters 1 and 2 (beam emitters, 0.06 × 0.12, 35 health, 600 points each); emitters 3 and 4 (beam emitters, 0.06 × 0.12, 35 health, 600 points each); gatlings 5 and 6 (gatlings, 0.033 × 0.067, 35 health, 600 points each).
- Phase 1 (until emitters 1–4 and gatlings 5 and 6 are destroyed, the core armored; sways at 0.1): emitters 1–4 and gatlings 5 and 6 fire, taking turns, a ring of 8 shots turned 20° more each time, every 2.2 s, speed 0.38; emitters 1–4 and gatlings 5 and 6 fire, taking turns, a ring of 8 shots turned -20° more each time, every 2.2 s, speed 0.38, first after 1.1 s; the core fires an aimed shot, every 1.6 s, speed 0.6, first after 0.5 s.
- Phase 2 (until the end; sways at 0.14): the core fires a 2-arm spiral of shots (a ring of 2 every 0.1 s, turning 10° each time), speed 0.48; the core fires a fan of 3 heavy shots 25° apart around straight down, every 2.4 s, speed 0.4, first after 1 s.

### Boss: Scavenger

- Level 6-2 (Striped Gullies), mini boss.
- Look: a patched-up salvager with wing batteries of beam emitters; 0.38 × 0.5.
- Core: 110 health, 3000 points.
- Parts (6): emitters 1 and 2 (beam emitters, 0.047 × 0.093, 35 health, 600 points each); emitters 3 and 4 (beam emitters, 0.06 × 0.12, 35 health, 600 points each); emitters 5 and 6 (beam emitters, 0.06 × 0.12, 35 health, 600 points each).
- Phase 1 (until emitters 1–6 are destroyed, the core armored; sways at 0.12): emitters 1–6 fire, taking turns, a fan of 4 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.3 s, speed 0.5; emitters 1–6 fire, taking turns, a fan of 4 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.3 s, speed 0.5, first after 0.65 s; the core fires an aimed shot, every 2 s, speed 0.6, first after 1 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.16): the core fires 5 shots 10° apart aimed at the player, every 1.4 s, speed 0.6; the core fires a ring of 10 shots turned 18° more each time, every 2.2 s, speed 0.4, first after 0.7 s.
- Phase 3 (until the end; sways at 0.2): the core fires a 2-arm spiral of shots (a ring of 2 every 0.09 s, turning 10° each time), speed 0.5; the core fires an aimed heavy shot, 2 times in a row 0.15 s apart, every 2 s, speed 0.55, first after 1 s.

### Boss: Mine Carrier

- Level 6-3 (Ochre Walls), mini boss.
- Look: a mine carrier with launch bays, radars, a turret and a beam emitter; 0.487 × 0.4.
- Core: 130 health, 3500 points.
- Parts (8): emitters 1 and 2 (beam emitters, 0.047 × 0.093, 35 health, 600 points each); turrets 3 and 4 (turrets, 0.06 × 0.087, 35 health, 600 points each); radars 5 and 6 (radars, 0.047 × 0.047, 35 health, 600 points each); radars 7 and 8 (radars, 0.06 × 0.06, 35 health, 600 points each).
- Phase 1 (until radars 5–8, turrets 3 and 4 and emitters 1 and 2 are destroyed, the core armored; sways at 0.1): radars 5–8, turrets 3 and 4 and emitters 1 and 2 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 1.8 s, speed 0.5; radars 5–8, turrets 3 and 4 and emitters 1 and 2 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 1.8 s, speed 0.5, first after 0.9 s; the core fires an aimed heavy shot, every 2.4 s, speed 0.5, first after 1.2 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.14): the core fires a ring of 10 shots turned 18° more each time, every 1.6 s, speed 0.4; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.65, first after 0.8 s.
- Phase 3 (until the end; sways at 0.18): the core fires a 3-arm spiral of shots (a ring of 3 every 0.13 s, turning -12° each time), speed 0.45; the core fires a fan of 5 heavy shots 18° apart around straight down, every 2.2 s, speed 0.45, first after 1 s.

### Boss: Foundry

- Level 6-4 (Red Dusk), mini boss.
- Look: a foundry ship with heavy presses, cannons and a beam emitter; 0.42 × 0.44.
- Core: 140 health, 3400 points.
- Parts (8): cannons 1 and 2 (twin cannons, 0.047 × 0.1, 35 health, 600 points each); cannons 3 and 4 (twin cannons, 0.06 × 0.133, 35 health, 600 points each); emitters 5 and 6 (beam emitters, 0.047 × 0.093, 35 health, 600 points each); cannons 7 and 8 (twin cannons, 0.047 × 0.1, 35 health, 600 points each).
- Phase 1 (until cannons 1, 2, 3, 4, 7, 8 and emitters 5 and 6 are destroyed, the core armored; sways at 0.08): cannons 1, 2, 3, 4, 7, 8 and emitters 5 and 6 fire, taking turns, a fan of 3 heavy shots 20° apart around straight down, every 2 s, speed 0.42; cannons 1, 2, 3, 4, 7, 8 and emitters 5 and 6 fire, taking turns, a fan of 3 heavy shots 20° apart around straight down, every 2 s, speed 0.42, first after 1 s; the core fires an aimed shot, every 1.6 s, speed 0.6, first after 0.5 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.12): the core fires a ring of 12 shots turned 15° more each time, every 1.5 s, speed 0.4; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.65, first after 0.7 s.
- Phase 3 (until the end; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.12 s, turning 13° each time), speed 0.45; the core fires a fan of 5 heavy shots 18° apart around straight down, every 2.4 s, speed 0.4, first after 1 s.

### Boss: Gunship Prime

- Level 6-5 (Rainbow Breaks), mini boss.
- Look: a heavy gunship with two big engines and beam emitters along its hull; 0.367 × 0.52.
- Core: 140 health, 3600 points.
- Parts (8): emitters 1 and 2 (beam emitters, 0.06 × 0.12, 30 health, 500 points each); emitters 3 and 4 (beam emitters, 0.047 × 0.093, 30 health, 500 points each); emitters 5 and 6 (beam emitters, 0.047 × 0.093, 30 health, 500 points each); emitters 7 and 8 (beam emitters, 0.06 × 0.12, 30 health, 500 points each).
- Phase 1 (until emitters 5–8 are destroyed, the core armored; sways at 0.08): emitters 5–8 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65; emitters 5–8 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65, first after 0.9 s; emitters 1–4 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 2 s, speed 0.45, first after 0.4 s; emitters 1–4 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 2 s, speed 0.45, first after 1.4 s.
- Phase 2 (until emitters 1–4 are destroyed, the core armored; sways at 0.12): emitters 1–4 fire, taking turns, a ring of 10 shots turned 18° more each time, every 2 s, speed 0.4; emitters 1–4 fire, taking turns, a ring of 10 shots turned -18° more each time, every 2 s, speed 0.4, first after 1 s; the core fires an aimed heavy shot, 2 times in a row 0.15 s apart, every 2 s, speed 0.55, first after 0.5 s.
- Phase 3 (until the end; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.12 s, turning 12° each time), speed 0.46; the core fires a fan of 5 shots 14° apart around straight down, its middle swinging 30° left and right, every 1.6 s, speed 0.5, first after 0.8 s.

### Boss: Colossus

- Level 6-6 (Dark Strata), mini boss.
- Look: a giant battle station with flak guns and missile racks on its outer and inner decks; 0.473 × 0.407.
- Core: 150 health, 8000 points.
- Parts (8): flaks 1 and 2 (flak guns, 0.047 × 0.067, 30 health, 600 points each); launchers 3 and 4 (missile racks, 0.06 × 0.067, 30 health, 600 points each); launchers 5 and 6 (missile racks, 0.047 × 0.053, 30 health, 600 points each); flaks 7 and 8 (flak guns, 0.047 × 0.067, 30 health, 600 points each).
- Phase 1 (until launchers 3 and 4 and flaks 1 and 2 are destroyed, the core armored; sways at 0.08): launchers 3 and 4 and flaks 1 and 2 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.7; launchers 3 and 4 and flaks 1 and 2 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.7, first after 1 s; flaks 7 and 8 and launchers 5 and 6 fire, taking turns, a fan of 3 shots 15° apart around straight down, every 1.6 s, speed 0.5, first after 0.5 s; flaks 7 and 8 and launchers 5 and 6 fire, taking turns, a fan of 3 shots 15° apart around straight down, every 1.6 s, speed 0.5, first after 1.3 s.
- Phase 2 (until flaks 7 and 8 and launchers 5 and 6 are destroyed, the core armored; sways at 0.12): flaks 7 and 8 and launchers 5 and 6 fire, taking turns, a ring of 8 shots turned 22° more each time, every 1.3 s, speed 0.45; flaks 7 and 8 and launchers 5 and 6 fire, taking turns, a ring of 8 shots turned -22° more each time, every 1.3 s, speed 0.45, first after 0.65 s; the core fires a fan of 5 heavy shots 20° apart around straight down, every 2.6 s, speed 0.4, first after 1 s.
- Phase 3 (until the end; sways at 0.15): the core fires a 4-arm spiral of shots (a ring of 4 every 0.16 s, turning 10° each time), speed 0.42; the core fires 3 shots 10° apart aimed at the player, every 1.5 s, speed 0.7, first after 0.7 s.

### Boss: Grappler

- Level 7-1 (Refinery), mini boss.
- Look: a salvage ship with grappling arms tipped with cannons; 0.367 × 0.373.
- Core: 130 health, 3200 points.
- Parts (6): cannons 1 and 2 (twin cannons, 0.06 × 0.133, 20 health, 400 points each); cannons 3 and 4 (twin cannons, 0.047 × 0.1, 20 health, 400 points each); cannons 5 and 6 (twin cannons, 0.06 × 0.133, 20 health, 400 points each).
- Phase 1 (until cannons 1–6 are destroyed, the core armored; sways at 0.1): cannons 1–6 fire, taking turns, a fan of 3 shots 15° apart around straight down, every 1.6 s, speed 0.5; cannons 1–6 fire, taking turns, a fan of 3 shots 15° apart around straight down, every 1.6 s, speed 0.5, first after 0.8 s; cannons 1–6 fire, taking turns, an aimed shot, every 1.4 s, speed 0.6, first after 0.4 s; cannons 1–6 fire, taking turns, an aimed shot, every 1.4 s, speed 0.6, first after 1.1 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.14): the core fires a ring of 12 shots turned 15° more each time, every 1.6 s, speed 0.4; the core fires an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.6, first after 0.8 s.
- Phase 3 (until the end; sways at 0.18): the core fires a 2-arm spiral of shots (a ring of 2 every 0.1 s, turning -10° each time), speed 0.5; the core fires a fan of 5 heavy shots 18° apart around straight down, every 2.6 s, speed 0.4, first after 1 s.

### Boss: Tugmaster

- Level 7-2 (Tank Farm), mini boss.
- Look: a space tug with two thrusters and a ram plate, radars and a reactor on deck; 0.407 × 0.373.
- Core: 130 health, 3500 points.
- Parts (6): radars 1 and 2 (radars, 0.06 × 0.06, 40 health, 700 points each); radars 3 and 4 (radars, 0.06 × 0.06, 30 health, 500 points each); reactors 5 and 6 (reactors, 0.073 × 0.073, 30 health, 500 points each).
- Phase 1 (until reactors 5 and 6 and radars 3 and 4 are destroyed, the core armored; sways at 0.08): reactors 5 and 6 and radars 3 and 4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.6; reactors 5 and 6 and radars 3 and 4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.6, first after 0.8 s; radars 1 and 2 fire, taking turns, a fan of 5 shots 15° apart around straight down, every 2 s, speed 0.45, first after 0.4 s.
- Phase 2 (until radars 1 and 2 are destroyed, the core armored; sways at 0.12): radars 1 and 2 fire, taking turns, a ring of 10 shots turned 18° more each time, every 1.6 s, speed 0.4; the core fires a fan of 3 heavy shots 30° apart around straight down, every 2.2 s, speed 0.4, first after 0.8 s.
- Phase 3 (until the end; sways at 0.16): the core fires a 2-arm spiral of shots (a ring of 2 every 0.1 s, turning 11° each time), speed 0.48; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.65, first after 0.8 s.

### Boss: Magma Rig

- Level 7-3 (Smelter), mini boss.
- Look: a mining rig with glowing furnaces and beam emitters; 0.367 × 0.347.
- Core: 150 health, 4000 points.
- Parts (4): emitters 1 and 2 (beam emitters, 0.06 × 0.12, 30 health, 500 points each); emitters 3 and 4 (beam emitters, 0.047 × 0.093, 30 health, 500 points each).
- Phase 1 (until emitters 3 and 4 are destroyed, the core armored; sways at 0.08): emitters 3 and 4 fire, taking turns, a ring of 8 shots turned 15° more each time, every 2 s, speed 0.38; emitters 3 and 4 fire, taking turns, a ring of 8 shots turned -15° more each time, every 2 s, speed 0.38, first after 1 s; emitters 1 and 2 fire, taking turns, an aimed shot, every 1.6 s, speed 0.65, first after 0.5 s; emitters 1 and 2 fire, taking turns, an aimed shot, every 1.6 s, speed 0.65, first after 1.3 s.
- Phase 2 (until emitters 1 and 2 are destroyed, the core armored; sways at 0.1): emitters 1 and 2 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65; emitters 1 and 2 fire, taking turns, an aimed shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.65, first after 0.9 s; the core fires a fan of 5 heavy shots 18° apart around straight down, every 2.4 s, speed 0.4, first after 0.5 s.
- Phase 3 (until the end; sways at 0.14): the core fires a 3-arm spiral of shots (a ring of 3 every 0.12 s, turning 12° each time), speed 0.45; the core fires a ring of 14 shots turned 10° more each time, every 2 s, speed 0.38, first after 1 s; the core fires an aimed shot, every 1.6 s, speed 0.65, first after 0.5 s.

### Boss: Dreadnought

- Level 7-4 (Pipe Maze), mini boss.
- Look: a narrow battleship with deck turrets and a bow gun of twin cannons; 0.313 × 0.513.
- Core: 150 health, 4000 points.
- Parts (6): cannons 1 and 2 (twin cannons, 0.047 × 0.1, 25 health, 500 points each); cannons 3 and 4 (twin cannons, 0.047 × 0.1, 25 health, 500 points each); cannons 5 and 6 (twin cannons, 0.06 × 0.133, 35 health, 700 points each).
- Phase 1 (until cannons 1–4 are destroyed, the core armored; sways at 0.08): cannons 1–4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.8 s, speed 0.6; cannons 1–4 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.8 s, speed 0.6, first after 0.9 s; cannons 1–4 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 2.2 s, speed 0.45, first after 0.4 s; cannons 1–4 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 2.2 s, speed 0.45, first after 1.5 s; cannons 5 and 6 fire, taking turns, an aimed heavy shot, every 2.6 s, speed 0.5, first after 1.2 s.
- Phase 2 (until cannons 5 and 6 are destroyed, the core armored; sways at 0.1): cannons 5 and 6 fire, taking turns, a fan of 5 shots 12° apart around straight down, its middle swinging 30° left and right, every 1 s, speed 0.5; the core fires a ring of 10 shots turned 18° more each time, every 2 s, speed 0.4, first after 0.5 s.
- Phase 3 (until the end; sways at 0.15): the core fires a 3-arm spiral of shots (a ring of 3 every 0.12 s, turning 11° each time), speed 0.45; the core fires 3 shots 10° apart aimed at the player, every 1.6 s, speed 0.65, first after 0.8 s.

### Boss: Flare Rig

- Level 7-5 (Flare Stacks), mini boss.
- Look: an oil rig turned warship, flare stacks and turrets on its platform; 0.38 × 0.353.
- Core: 165 health, 4300 points.
- Parts (4): turrets 1 and 2 (turrets, 0.047 × 0.067, 20 health, 400 points each); turrets 3 and 4 (turrets, 0.047 × 0.067, 20 health, 400 points each).
- Phase 1 (until turrets 1 and 2 are destroyed, the core armored; sways at 0.09): turrets 1 and 2 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.65; turrets 1 and 2 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.65, first after 0.75 s; turrets 1–4 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 2 s, speed 0.5, first after 0.4 s; turrets 1–4 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 2 s, speed 0.5, first after 1.4 s.
- Phase 2 (until turrets 3 and 4 are destroyed, the core armored; sways at 0.12): turrets 3 and 4 fire, taking turns, an aimed heavy shot, 2 times in a row 0.15 s apart, every 2 s, speed 0.55; turrets 3 and 4 fire, taking turns, an aimed heavy shot, 2 times in a row 0.15 s apart, every 2 s, speed 0.55, first after 1 s; turrets 1–4 fire, taking turns, a ring of 10 shots turned 18° more each time, every 2.4 s, speed 0.4; turrets 1–4 fire, taking turns, a ring of 10 shots turned -18° more each time, every 2.4 s, speed 0.4, first after 1.2 s.
- Phase 3 (until the end; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning 12° each time), speed 0.45; the core fires an aimed shot, 3 times in a row 0.15 s apart, every 1.9 s, speed 0.6, first after 0.7 s.

### Boss: Crucible

- Level 7-6 (Meltdown), mini boss.
- Look: a smelting block with furnaces on deck, beacons at the bow, missile racks and a reactor; 0.38 × 0.447.
- Core: 170 health, 9000 points.
- Parts (6): launchers 1 and 2 (missile racks, 0.06 × 0.067, 30 health, 600 points each); radars 3 and 4 (radars, 0.06 × 0.06, 30 health, 600 points each); reactors 5 and 6 (reactors, 0.073 × 0.073, 30 health, 600 points each).
- Phase 1 (until radars 3 and 4, reactors 5 and 6 and launchers 1 and 2 are destroyed, the core armored; sways at 0.09): launchers 1 and 2, radars 3 and 4 and reactors 5 and 6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.7; launchers 1 and 2, radars 3 and 4 and reactors 5 and 6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.7, first after 0.75 s; radars 3 and 4, reactors 5 and 6 and launchers 1 and 2 fire, taking turns, a ring of 12 shots turned 16° more each time, every 2.3 s, speed 0.38; radars 3 and 4, reactors 5 and 6 and launchers 1 and 2 fire, taking turns, a ring of 12 shots turned -16° more each time, every 2.3 s, speed 0.38, first after 1.15 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.13): the core fires a 3-arm spiral of shots (a ring of 3 every 0.15 s, turning 13° each time), speed 0.46; launchers 1 and 2, radars 3 and 4 and reactors 5 and 6 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 1.8 s, speed 0.55; launchers 1 and 2, radars 3 and 4 and reactors 5 and 6 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 1.8 s, speed 0.55, first after 0.9 s.
- Phase 3 (until the end; sways at 0.18): the core fires a ring of 16 shots turned 10° more each time, every 1.4 s, speed 0.4; the core fires an aimed heavy shot, 3 times in a row 0.2 s apart, every 2 s, speed 0.6, first after 0.7 s; launchers 1 and 2, radars 3 and 4 and reactors 5 and 6 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7; launchers 1 and 2, radars 3 and 4 and reactors 5 and 6 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7, first after 0.8 s.

### Boss: Executor

- Level 8-1 (Neon City), mini boss.
- Look: a command ship with blade wings, gatlings and a turret; 0.393 × 0.413.
- Core: 160 health, 4500 points.
- Parts (6): gatlings 1 and 2 (gatlings, 0.033 × 0.067, 30 health, 500 points each); gatlings 3 and 4 (gatlings, 0.033 × 0.067, 30 health, 500 points each); turrets 5 and 6 (turrets, 0.047 × 0.067, 30 health, 500 points each).
- Phase 1 (until turrets 5 and 6 and gatlings 1–4 are destroyed, the core armored; sways at 0.1): turrets 5 and 6 and gatlings 1–4 fire, taking turns, a ring of 10 shots turned 18° more each time, every 2.2 s, speed 0.38; turrets 5 and 6 and gatlings 1–4 fire, taking turns, a ring of 10 shots turned -18° more each time, every 2.2 s, speed 0.38, first after 1.1 s; gatlings 1–4 and turrets 5 and 6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.65, first after 0.5 s; gatlings 1–4 and turrets 5 and 6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.65, first after 1.3 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.14): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning 12° each time), speed 0.45; gatlings 1–4 and turrets 5 and 6 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 1.8 s, speed 0.5; gatlings 1–4 and turrets 5 and 6 fire, taking turns, a fan of 3 shots 18° apart around straight down, every 1.8 s, speed 0.5, first after 0.9 s.
- Phase 3 (until the end; sways at 0.18): the core fires a ring of 14 shots turned 11° more each time, every 1.5 s, speed 0.4; the core fires an aimed heavy shot, 3 times in a row 0.15 s apart, every 2.2 s, speed 0.55, first after 0.7 s; gatlings 1–4 and turrets 5 and 6 fire, taking turns, an aimed shot, every 1.5 s, speed 0.7; gatlings 1–4 and turrets 5 and 6 fire, taking turns, an aimed shot, every 1.5 s, speed 0.7, first after 0.75 s.

### Boss: Interdictor

- Level 8-2 (Downtown), mini boss.
- Look: an interceptor carrier with sensor-dish wings and turrets all over; 0.353 × 0.4.
- Core: 160 health, 4200 points.
- Parts (6): turrets 1 and 2 (turrets, 0.06 × 0.087, 30 health, 500 points each); turrets 3 and 4 (turrets, 0.06 × 0.087, 30 health, 500 points each); turrets 5 and 6 (turrets, 0.047 × 0.067, 30 health, 500 points each).
- Phase 1 (until turrets 1–6 are destroyed, the core armored; sways at 0.12): turrets 1–6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.4 s, speed 0.7; turrets 1–6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.4 s, speed 0.7, first after 0.7 s; turrets 1–6 fire, taking turns, a fan of 5 shots 12° apart around straight down, its middle swinging 20° left and right, every 2 s, speed 0.5; turrets 1–6 fire, taking turns, a fan of 5 shots 12° apart around straight down, its middle swinging 20° left and right, every 2 s, speed 0.5, first after 1 s.
- Phase 2 (until the end; sways at 0.16): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning -12° each time), speed 0.45; turrets 1–6 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7; turrets 1–6 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7, first after 0.8 s.

### Boss: Nightwatch

- Level 8-3 (Skyline), mini boss.
- Look: a dark gunboat with gatlings on deck and missile racks on its flanks; 0.34 × 0.513.
- Core: 165 health, 4400 points.
- Parts (6): gatlings 1 and 2 (gatlings, 0.047 × 0.087, 30 health, 500 points each); gatlings 3 and 4 (gatlings, 0.047 × 0.087, 30 health, 500 points each); launchers 5 and 6 (missile racks, 0.047 × 0.053, 30 health, 500 points each).
- Phase 1 (until gatlings 1 and 2 and launchers 5 and 6 are destroyed, the core armored; sways at 0.12): gatlings 1 and 2 and launchers 5 and 6 fire, taking turns, an aimed blue sniper shot, 2 times in a row 0.15 s apart, every 1.3 s, speed 0.72; gatlings 1 and 2 and launchers 5 and 6 fire, taking turns, an aimed blue sniper shot, 2 times in a row 0.15 s apart, every 1.3 s, speed 0.72, first after 0.65 s; gatlings 3 and 4 fire, taking turns, a fan of 3 shots 16° apart around straight down, every 1.8 s, speed 0.5; gatlings 3 and 4 fire, taking turns, a fan of 3 shots 16° apart around straight down, every 1.8 s, speed 0.5, first after 0.9 s.
- Phase 2 (until gatlings 3 and 4 are destroyed, the core armored; sways at 0.15): gatlings 3 and 4 fire, taking turns, a ring of 10 shots turned 18° more each time, every 2.2 s, speed 0.42; gatlings 3 and 4 fire, taking turns, a ring of 10 shots turned -18° more each time, every 2.2 s, speed 0.42, first after 1.1 s; the core fires an aimed heavy shot, 2 times in a row 0.15 s apart, every 1.8 s, speed 0.6, first after 0.5 s.
- Phase 3 (until the end; sways at 0.18): the core fires a 3-arm spiral of shots (a ring of 3 every 0.13 s, turning 13° each time), speed 0.46; the core fires a fan of 5 shots 14° apart around straight down, its middle swinging 30° left and right, every 1.5 s, speed 0.55, first after 0.8 s.

### Boss: Arc Tower

- Level 8-4 (Neon Rain), mini boss.
- Look: a floating power station with an arc emitter at the bow and flak nodes on deck; 0.527 × 0.387.
- Core: 170 health, 4600 points.
- Parts (8): flaks 1 and 2 (flak guns, 0.047 × 0.067, 30 health, 500 points each); flaks 3 and 4 (flak guns, 0.047 × 0.067, 30 health, 500 points each); flaks 5 and 6 (flak guns, 0.06 × 0.087, 30 health, 500 points each); emitters 7 and 8 (beam emitters, 0.06 × 0.12, 30 health, 500 points each).
- Phase 1 (until flaks 1–6 and emitters 7 and 8 are destroyed, the core armored; sways at 0.1): flaks 1–6 and emitters 7 and 8 fire, taking turns, a fan of 5 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.6 s, speed 0.55; flaks 1–6 and emitters 7 and 8 fire, taking turns, a fan of 5 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.6 s, speed 0.55, first after 0.8 s; flaks 1–6 and emitters 7 and 8 fire, taking turns, a ring of 10 shots turned 18° more each time, every 2.4 s, speed 0.38; flaks 1–6 and emitters 7 and 8 fire, taking turns, a ring of 10 shots turned -18° more each time, every 2.4 s, speed 0.38, first after 1.2 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.14): the core fires a 3-arm spiral of shots (a ring of 3 every 0.13 s, turning 14° each time), speed 0.46; flaks 1–6 and emitters 7 and 8 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.7; flaks 1–6 and emitters 7 and 8 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.6 s, speed 0.7, first after 0.8 s.
- Phase 3 (until the end; sways at 0.18): the core fires a ring of 16 shots turned 10° more each time, every 1.4 s, speed 0.42; the core fires an aimed heavy shot, 3 times in a row 0.15 s apart, every 2 s, speed 0.62, first after 0.7 s.

### Boss: Apex

- Level 8-5 (Night Grid), mini boss.
- Look: a sleek flagship with heavy wing guns and two reactors at its stern; 0.433 × 0.287.
- Core: 175 health, 4800 points.
- Parts (4): reactors 1 and 2 (reactors, 0.06 × 0.06, 30 health, 500 points each); reactors 3 and 4 (reactors, 0.06 × 0.06, 30 health, 500 points each).
- Phase 1 (until reactors 1–4 are destroyed, the core armored; sways at 0.1): reactors 1–4 fire, taking turns, an aimed heavy shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.6; reactors 1–4 fire, taking turns, an aimed heavy shot, 3 times in a row 0.15 s apart, every 1.8 s, speed 0.6, first after 0.9 s; reactors 1–4 fire, taking turns, a ring of 12 shots turned 16° more each time, every 2.2 s, speed 0.4; reactors 1–4 fire, taking turns, a ring of 12 shots turned -16° more each time, every 2.2 s, speed 0.4, first after 1.1 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.15): the core fires a 3-arm spiral of shots (a ring of 3 every 0.14 s, turning 13° each time), speed 0.46; reactors 1–4 fire, taking turns, a fan of 5 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.7 s, speed 0.55; reactors 1–4 fire, taking turns, a fan of 5 shots 12° apart around straight down, its middle swinging 25° left and right, every 1.7 s, speed 0.55, first after 0.85 s.
- Phase 3 (until the end; sways at 0.19): the core fires a ring of 16 shots turned -10° more each time, every 1.4 s, speed 0.42; the core fires an aimed heavy shot, 3 times in a row 0.2 s apart, every 1.9 s, speed 0.65, first after 0.7 s; reactors 1–4 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7; reactors 1–4 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7, first after 0.8 s.

### Boss: Overmind

- Level 8-6 (The Core), mini boss.
- Look: a massive command ship whose shield generators armor its core, cannons, turrets and gatlings on its sides; 0.42 × 0.413.
- Core: 160 health, 10000 points.
- Parts (6): cannons 1 and 2 (twin cannons, 0.047 × 0.1, 35 health, 700 points each); turrets 3 and 4 (turrets, 0.047 × 0.067, 35 health, 700 points each); gatlings 5 and 6 (gatlings, 0.047 × 0.087, 35 health, 700 points each).
- Phase 1 (until gatlings 5 and 6, cannons 1 and 2 and turrets 3 and 4 are destroyed, the core armored; sways at 0.1): cannons 1 and 2, turrets 3 and 4 and gatlings 5 and 6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.7; cannons 1 and 2, turrets 3 and 4 and gatlings 5 and 6 fire, taking turns, an aimed shot, 2 times in a row 0.15 s apart, every 1.5 s, speed 0.7, first after 0.75 s; gatlings 5 and 6, cannons 1 and 2 and turrets 3 and 4 fire, taking turns, a ring of 10 shots turned 18° more each time, every 2.4 s, speed 0.38; gatlings 5 and 6, cannons 1 and 2 and turrets 3 and 4 fire, taking turns, a ring of 10 shots turned -18° more each time, every 2.4 s, speed 0.38, first after 1.2 s.
- Phase 2 (until the core's health falls below 50%; sways at 0.14): the core fires a 3-arm spiral of shots (a ring of 3 every 0.16 s, turning 14° each time), speed 0.45; cannons 1 and 2, turrets 3 and 4 and gatlings 5 and 6 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 1.8 s, speed 0.55; cannons 1 and 2, turrets 3 and 4 and gatlings 5 and 6 fire, taking turns, a fan of 3 shots 20° apart around straight down, every 1.8 s, speed 0.55, first after 0.9 s.
- Phase 3 (until the end; sways at 0.2): the core fires a ring of 18 shots turned 10° more each time, every 1.4 s, speed 0.4; the core fires an aimed heavy shot, 3 times in a row 0.2 s apart, every 2 s, speed 0.6, first after 0.7 s; cannons 1 and 2, turrets 3 and 4 and gatlings 5 and 6 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7; cannons 1 and 2, turrets 3 and 4 and gatlings 5 and 6 fire, taking turns, an aimed shot, every 1.6 s, speed 0.7, first after 0.8 s.

## Final bosses

- **BOS-20** Each level shall end with its final boss, after its mini boss: bigger (0.46 to 1.21 wide, up to half
  the screen's width) and harder, with more parts and four phases. Its numbers shall follow from the level's
  difficulty d (1 to 20, see `03-levels.md`); write p = (d − 1) / 19.
- **BOS-21** Health and points: the core shall have 110 + 14 (d − 1) health and give 4000 + 400 d points; each part
  shall have round(16 + 1.6 (d − 1)) health and give 300 + 30 d points.
- **BOS-22** Each final boss shall have four attacks (see the table): its front parts', its back parts', its core's and
  its rage's. Each attack shall be one of these guns, getting faster and denser with the difficulty (values written
  "a → b" go linearly from a at d = 1 to b at d = 20; counts are rounded):

| Attack | Gun |
|--------|-----|
| aimed | 3 → 5 aimed heavy shots in a row, 0.12 s apart, every 1.6 → 1.1 s, speed 0.6 → 0.75 |
| sniper | 2 → 4 aimed blue sniper shots in a row, 0.2 s apart, every 1.5 → 1.1 s, speed 0.85 → 0.95 |
| fan | a fan of 5 → 9 shots 12° apart, swinging 25° left and right, every 1.8 → 1.3 s, speed 0.45 → 0.55 |
| ring | a ring of 12 → 20 shots, turned 9° more each time, every 2 → 1.4 s, speed 0.38 → 0.46 |
| spiral | a 2 → 4-arm spiral: a ring of 2 → 4 shots every 0.16 → 0.12 s, turned 13° more each time, speed 0.42 → 0.48 |
| wave | a fan of 3 → 5 snaking shots 20° apart, every 1.6 → 1.2 s, speed 0.45 → 0.55 |
| accel | 5 accelerating shots 8° apart aimed at the player, every 1.8 → 1.3 s, speed 0.55 → 0.7 |
| curve | a ring of 8 → 12 curving shots (35° per second), every 1.8 → 1.3 s, speed 0.35 → 0.4 |
| pellets | 7 → 11 pellets 6° apart aimed at the player, every 1.6 → 1.2 s, speed 0.6 → 0.7 |
| laser | a laser beam 0.07 wide every 4.5 → 3 s, lasting 1 → 1.4 s after its 1 s warning; from the core: two beams, a quarter of the core's width either side of its middle |
| missiles | 2 homing missiles 40° apart, aimed at the player, every 3.5 → 2.5 s |
| rockets | 3 rockets 25° apart around straight down, every 2.6 → 1.8 s |
| cluster | 2 → 3 cluster bombs 30° apart around straight down, every 3 → 2.2 s |

- **BOS-23** Front and back parts: the kinds of part (parts sharing a drawing) shall be ordered by the total of their
  parts' y positions, lowest first (ties by name); the first half of the kinds (rounded up) are the front parts, the
  others the back parts.
- **BOS-24** A group of parts firing an attack shall fire it taking turns (BOS-10), each part at the attack's interval
  times √(max(1, n / 2)), n being the number of parts in the group.
- **BOS-25** Phases, with a sway speed s = 0.08 + 0.004 d:
    1. Until the front parts are destroyed, the core armored, sway s: the front parts fire the front attack; from
       d = 8 the core also fires "aimed", first after 0.8 s.
    2. Until the back parts are destroyed, the core armored, sway s: the back parts fire the back attack, the core its
       attack, first after 0.6 s. This phase shall be skipped when every part is a front part.
    3. Until the core's health falls below 50%, sway s + 0.03: the core fires its attack, and the rage attack first
       after 0.9 s.
    4. Until the end, sway s + 0.06: the core fires the rage attack, the front attack first after 0.5 s, and a spiral
       (a ring below d = 6) first after 1 s.
- **BOS-26** Looks: final bosses shall be among the biggest models, bigger for the later levels; each hitbox is its
  model's size. Their parts are machines standing on the hull (see `05-visuals.md`).
- **BOS-27** The final bosses shall be:

| Level | Final boss | Difficulty | Size | Parts | Part health | Part points | Core health | Core points | Front, back, core, rage attacks | Look |
|-------|------------|-----------:|------|------:|------------:|------------:|------------:|------------:|--------------------------------|------|
| 1-1 | Avalanche | 1 | 0.5 × 0.3 | 6 | 16 | 330 | 110 | 4400 | fan, aimed, laser, ring | A snow-white mountain fortress coming down like an avalanche, twin cannons on its slopes. |
| 1-2 | Frostjaw | 2 | 0.513 × 0.28 | 6 | 18 | 360 | 124 | 4800 | pellets, fan, wave, ring | An icebreaker with a jagged frozen jaw, missile racks along its flanks. |
| 1-3 | Iron Summit | 3 | 0.58 × 0.333 | 8 | 19 | 390 | 138 | 5200 | aimed, rockets, laser, fan | An iron peak of stacked decks: turrets, cannons and two reactors at its summit. |
| 1-4 | Stormpeak | 4 | 0.54 × 0.327 | 6 | 21 | 420 | 152 | 5600 | wave, ring, curve, spiral | A storm-wreathed spire ship crackling with beam emitters. |
| 1-5 | Ridgebreaker | 5 | 0.673 × 0.493 | 12 | 22 | 450 | 166 | 6000 | rockets, pellets, laser, fan | A broad mining crawler with a ridge-splitting prow and a field of flak guns. |
| 1-6 | Highlord | 6 | 0.567 × 0.333 | 6 | 24 | 480 | 180 | 6400 | aimed, cluster, laser, curve | The Highlands' warlord: a crowned flagship with heavy cannons and flak towers. |
| 2-1 | Ironbark | 3 | 0.593 × 0.453 | 10 | 19 | 390 | 138 | 5200 | fan, accel, ring, pellets | A gnarled armored hulk like an iron-barked tree, reactors at its roots, missile racks in its branches. |
| 2-2 | Thornback | 4 | 0.513 × 0.393 | 8 | 21 | 420 | 152 | 5600 | pellets, curve, laser, wave | A spiny cruiser whose back bristles with flak guns like thorns. |
| 2-3 | Rootmaw | 5 | 0.967 × 0.427 | 12 | 22 | 450 | 166 | 6000 | rockets, wave, accel, spiral | A very wide ship spreading like roots around a gaping maw, turrets all over. |
| 2-4 | Wildfire | 6 | 0.74 × 0.493 | 12 | 24 | 480 | 180 | 6400 | accel, fan, laser, curve | A blazing raider wing packed with missile racks. |
| 2-5 | Grovekeeper | 7 | 0.633 × 0.427 | 10 | 26 | 510 | 194 | 6800 | curve, missiles, ring, laser | A tall guardian ship standing in a grove of flak towers. |
| 2-6 | Old Growth | 8 | 0.673 × 0.433 | 12 | 27 | 540 | 208 | 7200 | wave, rockets, laser, accel | An ancient, moss-dark battleship with beam emitters and radar dishes. |
| 3-1 | Bogmaw | 5 | 0.527 × 0.38 | 8 | 22 | 450 | 166 | 6000 | wave, pellets, curve, ring | A squat swamp hulk with a wide maw, missile racks and radars. |
| 3-2 | Mirelord | 6 | 0.933 × 0.727 | 12 | 24 | 480 | 180 | 6400 | missiles, fan, laser, wave | A huge, wide marsh barge, its deck a field of flak guns. |
| 3-3 | Fenwraith | 7 | 0.46 × 0.427 | 8 | 26 | 510 | 194 | 6800 | curve, accel, wave, spiral | A pale, ghostly ship drifting low, flak guns around two reactors. |
| 3-4 | Hydra | 8 | 0.573 × 0.373 | 8 | 27 | 540 | 208 | 7200 | wave, cluster, laser, curve | A many-headed warship: cannon, missile and flak heads on long necks. |
| 3-5 | Marsh Titan | 9 | 1.073 × 0.653 | 12 | 29 | 570 | 222 | 7600 | pellets, missiles, accel, laser | A colossal swamp titan, wider than half the screen, studded with radar dishes. |
| 3-6 | Drowned King | 10 | 0.567 × 0.433 | 10 | 30 | 600 | 236 | 8000 | curve, wave, laser, missiles | A barnacled royal flagship risen from the river, radar dishes and two gatlings. |
| 4-1 | Scarecrow | 7 | 0.633 × 0.387 | 10 | 26 | 510 | 194 | 6800 | pellets, rockets, fan, laser | A gaunt cross-shaped ship with ragged wings, reactors glowing like eyes. |
| 4-2 | Combine | 8 | 0.673 × 0.387 | 10 | 27 | 540 | 208 | 7200 | fan, accel, laser, cluster | A giant harvesting combine with a wide reaper bar and reactors along its body. |
| 4-3 | Locust | 9 | 1.073 × 0.6 | 12 | 29 | 570 | 222 | 7600 | missiles, pellets, curve, spiral | A swarm mother with long locust wings, reactors, missile racks and radars. |
| 4-4 | Granary | 10 | 0.873 × 0.613 | 12 | 30 | 600 | 236 | 8000 | cluster, aimed, laser, wave | A flying grain silo complex with radars, beam emitters and reactors. |
| 4-5 | Harrowmaster | 11 | 0.687 × 0.42 | 10 | 32 | 630 | 250 | 8400 | accel, rockets, laser, curve | A wide harrow ship dragging its tines, turrets on its frame and a big cannon. |
| 4-6 | Black Harvest | 12 | 0.78 × 0.38 | 12 | 34 | 660 | 264 | 8800 | curve, missiles, laser, accel | A black reaper ship with a long scythe wing and rows of reactors. |
| 5-1 | Maelstrom | 9 | 0.833 × 0.54 | 12 | 29 | 570 | 222 | 7600 | wave, curve, ring, laser | A whirling vortex ship ringed with gatlings and reactors. |
| 5-2 | Man O' War | 10 | 0.633 × 0.447 | 10 | 30 | 600 | 236 | 8000 | missiles, wave, laser, pellets | A jellyfish-like warship trailing beam emitters and cannons like stinging tentacles. |
| 5-3 | Typhoon | 11 | 1.007 × 0.613 | 12 | 32 | 630 | 250 | 8400 | curve, accel, wave, laser | A wide storm carrier, a wall of cannons along its front. |
| 5-4 | Tsunami | 12 | 0.767 × 0.74 | 12 | 34 | 660 | 264 | 8800 | wave, cluster, laser, spiral | A towering wave-shaped ship, reactors in its crest and gatlings below. |
| 5-5 | Abyssal | 13 | 1.147 × 0.88 | 12 | 35 | 690 | 278 | 9200 | sniper, missiles, curve, laser | A huge deep-sea leviathan, the biggest of its world, with gatlings and radar dishes. |
| 5-6 | Kraken | 14 | 0.667 × 0.807 | 12 | 37 | 720 | 292 | 9600 | wave, rockets, laser, curve | A tall tentacled monster ship, missile racks on its arms. |
| 6-1 | Mesa | 11 | 0.913 × 0.547 | 12 | 32 | 630 | 250 | 8400 | rockets, sniper, laser, fan | A flat-topped table mountain of armor, flak guns and cannons on its plateau. |
| 6-2 | Dust Devil | 12 | 0.62 × 0.4 | 10 | 34 | 660 | 264 | 8800 | curve, pellets, spiral, accel | A sand-colored ship whirling around a ring of reactors. |
| 6-3 | Landslide | 13 | 0.687 × 0.453 | 12 | 35 | 690 | 278 | 9200 | cluster, rockets, laser, wave | A tumbling slide of armor plates hiding missile racks. |
| 6-4 | Basilisk | 14 | 0.713 × 0.773 | 12 | 37 | 720 | 292 | 9600 | accel, sniper, laser, curve | A long serpent-king ship with a crested head, turrets, flak guns and reactors. |
| 6-5 | Sandworm | 15 | 0.593 × 0.58 | 12 | 38 | 750 | 306 | 10000 | missiles, wave, curve, laser | A segmented worm ship rising from the sand, cannons along its rings. |
| 6-6 | Monolith | 16 | 0.753 × 0.84 | 12 | 40 | 780 | 320 | 10400 | sniper, cluster, laser, accel | A tall black slab of a ship, turrets set in its faces. |
| 7-1 | Furnace | 13 | 1.207 × 0.773 | 12 | 35 | 690 | 278 | 9200 | fan, rockets, laser, pellets | A huge glowing furnace hulk, the widest boss of the game, lined with cannons. |
| 7-2 | Smokestack | 14 | 0.793 × 0.64 | 12 | 37 | 720 | 292 | 9600 | cluster, accel, curve, laser | A factory ship of chimneys and stacks, reactors and cannons between them. |
| 7-3 | Slag King | 15 | 0.58 × 0.607 | 12 | 38 | 750 | 306 | 10000 | pellets, missiles, laser, wave | A molten-armored king of the smelters, crowned with cannons. |
| 7-4 | Forgemaster | 16 | 0.673 × 0.547 | 12 | 40 | 780 | 320 | 10400 | rockets, sniper, laser, curve | An anvil-shaped forge ship, flak towers for hammers. |
| 7-5 | Inferno | 17 | 0.607 × 0.607 | 12 | 42 | 810 | 334 | 10800 | curve, cluster, laser, accel | A square fire ship of flaming stacks, turrets and cannons. |
| 7-6 | Reactor | 18 | 1.1 × 1.013 | 12 | 43 | 840 | 348 | 11200 | accel, missiles, laser, wave | A giant power plant in meltdown, flying: reactors, gatlings and flak guns. |
| 8-1 | Neon Tyrant | 15 | 0.833 × 0.727 | 12 | 38 | 750 | 306 | 10000 | sniper, accel, laser, curve | A neon-lit tyrant ship blazing with reactors. |
| 8-2 | Gridlock | 16 | 0.887 × 0.82 | 12 | 40 | 780 | 320 | 10400 | missiles, pellets, laser, wave | A flying city block of towers and traffic, missile racks and radars on its roofs. |
| 8-3 | Blackout | 17 | 1.06 × 0.873 | 12 | 42 | 810 | 334 | 10800 | curve, rockets, laser, accel | A huge dark ship that swallows the city lights, ringed with radar dishes. |
| 8-4 | Skybreaker | 18 | 0.727 × 0.62 | 12 | 43 | 840 | 348 | 11200 | wave, sniper, laser, cluster | A skyscraper warship piercing the clouds, reactors and flak guns on its floors. |
| 8-5 | Sovereign | 19 | 0.86 × 0.707 | 12 | 45 | 870 | 362 | 11600 | accel, missiles, laser, curve | The city's regal flagship, its gold-trimmed hull lined with gatlings and flak guns. |
| 8-6 | Singularity | 20 | 0.833 × 0.673 | 12 | 46 | 900 | 376 | 12000 | curve, cluster, laser, spiral | The last boss: a dark core collapsing into itself, turrets orbiting it. |
