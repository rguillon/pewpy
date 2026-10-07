# 02 — Enemies: catalog

Part of `02-enemies.md` (the rules every enemy follows are there). Units: see `00-vision.md`.

Each entry is a requirement: the enemy shall look, measure, move, attack and come in groups as its lines state.

How to read an entry:

- **Body**: hitbox, health, points, chance to drop a pickup when shot down.
- **Moves** and **Attack**: what it does, in order. Unless stated otherwise it comes from the top (ENM-1), fires only
  on the play area (ENM-6), its guns are staggered (ENM-7) and its shots are plain (ENM-8). "Leaves" means it flies
  off the screen and disappears (ENM-3).
- **Groups**: the shapes its waves come in. The number in brackets is the group's base size: a level of difficulty
  d sends max(1, round(base × 1.073^(d−1))) of them, a line being cut down to fit 2.1 wu across (1.0 wu tall from a
  side). A column sends them one after another at the same place, a line side by side at the same time
  (see `03-levels.md`).
- **Unlock**: the difficulty from which the levels may send it, and the first level that does.

### Enemy: Drone (CAT-1)

- Look: a grey armored drone with red markings, side vents and a red sensor eye.
- Body: 0.1 × 0.1; 3 health; 100 points; drops 5%.
- Moves: straight down at 0.3.
- Attack: an aimed shot every 1.5 s, speed 0.6.
- Groups: a column at x −0.67 or 0.67, 0.5 s apart (5); a line at x 0, 0.2 apart (5.04); a line, 0.5 apart (4); a
  column at x −0.67 or 0.67, 0.45 s apart (3.39); a line, 0.33 apart (4.27); a column at x 0, 0.5 s apart (3.04).
- Unlock: difficulty 1; level 1-1. A warm-up enemy (see LVL-19).

### Enemy: Weaver (CAT-2)

- Look: a grey diamond-shaped interceptor with yellow wing stripes.
- Body: 0.1 × 0.1; 2 health; 80 points; drops 5%.
- Moves: down at 0.35, snaking from side to side around the column it came down: x = its starting x + 0.25 (×W) ×
  sin(2π × age / 2 s).
- Attack: none.
- Groups: columns 0.35 to 0.4 s apart at x 0, ±0.58 or ±0.67 (3.8 to 8), so the group snakes down the screen.
- Unlock: difficulty 1; level 1-1. A warm-up enemy.

### Enemy: Diver (CAT-3)

- Look: a grey arrowhead pointing down with orange markings, two rear engines and a red nose light.
- Body: 0.1 × 0.12; 2 health; 150 points; drops 5%.
- Moves: down at 0.5 to y = 0.5, then stops and waits 0.8 s, blinking (hidden every other 0.1 s) as a warning; then
  dives at 1.2 in a straight line towards where the player is when it starts diving, pointing the way it flies, and
  keeps going until it leaves.
- Attack: none; it tries to ram the player.
- Groups: a line at x 0, 0.83, 0.58 or 0.5 apart (3, 2.63, 3.87).
- Unlock: difficulty 1; level 1-1.

### Enemy: Gunship (CAT-4)

- Look: a wide grey armored gunship with dark red markings, two big engine nacelles and three cannons.
- Body: 0.268 × 0.188; 8 health; 300 points; drops 20%.
- Moves: straight down at 0.15.
- Attack: every 2 s, 3 shots straight down and 20° to each side, speed 0.5.
- Groups: one at x 0 (0.85); a line 1.33 apart (0.85).
- Unlock: difficulty 1; level 1-1.

### Enemy: Turret (CAT-5)

- Look: a grey gun emplacement with a dark dome, a red light and a barrel that turns to aim at the player.
- Body: 0.12 × 0.12; 6 health; 250 points; drops 10%.
- Moves: fixed to the ground (ENM-5).
- Attack: every 2.5 s, a burst of 3 aimed shots 0.15 s apart, speed 0.7.
- Groups: a line at x 0, 1.67, 1.0 or 0.83 apart (1.42, 1.13, 1.11): usually one on each side of the screen.
- Unlock: difficulty 5; level 1-5. Ground enemy: never sent in worlds without ground enemies (see `03-levels.md`).

### Enemy: Flak Cannon (CAT-6)

- Look: a grey octagonal gun emplacement with a dark gun housing, orange stripes and two barrels pointing down the
  screen.
- Body: 0.12 × 0.12; 5 health; 200 points; drops 10%.
- Moves: fixed to the ground (ENM-5).
- Attack: every 1.8 s, 2 pairs of parallel shots 0.2 s apart, one shot from each barrel (0.025 either side of its
  middle), straight down the screen (not aimed), speed 0.55.
- Groups: a line at x 0, 1.05 to 1.48 apart (0.56 to 1.47): usually one on each side of the screen.
- Unlock: difficulty 5; level 1-5. Ground enemy.

### Enemy: Swarmer (CAT-7)

- Look: a small grey dart with green markings, pointing where it flies.
- Body: 0.089 × 0.089; 1 health; 50 points; never drops.
- Moves: comes in from a side (ENM-2), flying straight in at 0.6; once inside the screen it turns towards straight
  down at up to 0.9 rad/s (÷W, about 31° per second) at the same speed, following a curve that bends down to the
  bottom of the screen.
- Attack: none.
- Groups: a column from the left or the right at y 0.3, 0.4, 0.5 or 0.6, 0.2 s apart (4.78 to 5.34), all following
  the same path.
- Unlock: difficulty 2; level 1-6. Also released by the Splitter.

### Enemy: Sniper (CAT-8)

- Look: a thin grey ship with blue markings and a long gun barrel.
- Body: 0.08 × 0.14; 5 health; 350 points; drops 15%.
- Moves: down at 0.3 to y = 0.7; there it stops and slides sideways at 0.15, towards the middle first, turning back
  at the screen's edges; after 12 s there it leaves by flying back up at 0.3.
- Attack: 3 s after each shot (the first one staggered), it glows white for 0.5 s as a warning, then fires one fast
  aimed sniper shot (blue), speed 0.9.
- Groups: a line 1.67 apart (0.93); one at x 0 (0.77).
- Unlock: difficulty 2; level 1-2.

### Enemy: Mine Layer (CAT-9)

- Look: a wide grey hauler with a purple mine bay and two engines.
- Body: 0.18 × 0.08; 4 health; 300 points; drops 10%.
- Moves: comes in from a side and crosses the screen at 0.35 (×W) at a fixed height.
- Attack: drops a mine (ENM-14) from the middle of its bottom edge every 1 s. Mines fill the lower part of the screen,
  forcing the player to shoot a path through.
- Groups: one from the left or the right at y 0.3 to 0.7 (0.34 to 0.54).
- Unlock: difficulty 5; level 1-5.

### Enemy: Shield Carrier (CAT-10)

- Look: a large square grey carrier with teal shield emitters and two engines, inside a see-through light blue bubble
  while its shield is up.
- Body: 0.2 × 0.2; 10 health; 500 points; drops 30%.
- Moves: straight down at 0.12.
- Attack: in a cycle of 3.5 s counted from its arrival: shield up for 2 s (it cannot be hurt; shots hitting it are
  absorbed without damage; it stops the laser), then shield down for 1.5 s. Each time the shield drops it fires a
  ring of 8 shots, one straight down, speed 0.45.
- Groups: one at x 0 (0.79); a line 1.33 apart (0.84).
- Unlock: difficulty 5; level 2-3. It teaches the player to time their shots.

### Enemy: Splitter (CAT-11)

- Look: a grey hub with three magenta-marked pods.
- Body: 0.14 × 0.14; 6 health; 200 points; drops 10%.
- Moves: straight down at 0.25.
- Attack: an aimed shot every 2 s, speed 0.5. When shot down (not when rammed), it releases 3 Swarmers at its middle,
  heading left-down, straight down and right-down (−135°, −90°, −45° from the right); each then behaves as a Swarmer
  (giving its own points).
- Groups: a line 1.33 or 0.83 apart (1.57, 1.6); a column at x 0, 1.5 s apart (2.36).
- Unlock: difficulty 5; level 1-5. Destroying it close to the player is dangerous.

### Enemy: Rocketeer (CAT-12)

- Look: a grey ship with a rocket pod on each side (red-tipped rockets) and red-orange markings.
- Body: 0.161 × 0.161; 5 health; 250 points; drops 10%.
- Moves: straight down at 0.2.
- Attack: every 2.5 s, a pair of rockets (ENM-14) from its bottom edge, 0.045 either side of its middle.
- Groups: a line at x 0, 1.17 apart (1.11): usually two side by side.
- Unlock: difficulty 2; level 1-2.

### Enemy: Hunter (CAT-13)

- Look: a grey delta-winged ship with missile rails under its wings and teal markings.
- Body: 0.14 × 0.12; 6 health; 350 points; drops 15%.
- Moves: down at 0.3 to y = 0.65; there it slides sideways at 0.12, towards the middle first, turning back at the
  screen's edges; after 10 s there it leaves by flying back up at 0.3.
- Attack: a homing missile (ENM-14) from the middle of its bottom edge every 3.2 s.
- Groups: one at x between −0.58 and 0.35 (0.29 to 0.76).
- Unlock: difficulty 5; level 1-5.

### Enemy: Bomber (CAT-14)

- Look: a wide grey flying wing with four engines, a dark bomb bay in the middle and green markings.
- Body: 0.358 × 0.196; 7 health; 400 points; drops 20%.
- Moves: comes in from a side and crosses the screen at 0.2 (×W) at a fixed height.
- Attack: drops a cluster bomb (ENM-14) from the middle of its bottom edge every 1.6 s.
- Groups: one from the left or the right at y 0.58 to 0.74 (0.26 to 0.68).
- Unlock: difficulty 7; level 2-5.

### Enemy: Lancer (CAT-15)

- Look: a narrow grey ship with a long glowing lance pointing down and red markings.
- Body: 0.155 × 0.217; 5 health; 350 points; drops 15%.
- Moves: down at 0.35 to y = 0.6; there it slides sideways at 0.2 towards the player's column (still once within 0.02
  of it), holding still while it charges and fires; after 12 s there, as soon as it is not charging or firing, it
  leaves by flying back up at 0.35.
- Attack: every 3.5 s, it glows white for 0.8 s (a warning), then fires a red laser beam (ENM-12) 0.035 wide from the
  middle of its bottom edge, for 0.5 s.
- Groups: one at x between −0.7 and 0.58 (0.3 to 0.58).
- Unlock: difficulty 9; level 3-5.

### Enemy: Serpent (CAT-16)

- Look: a grey ship with a wavy ribbed body, fins along its sides and violet markings.
- Body: 0.177 × 0.207; 4 health; 200 points; drops 5%.
- Moves: straight down at 0.25.
- Attack: every 1.6 s, 3 snaking shots (ENM-11) aimed at the player, 18° apart, speed 0.45.
- Groups: a column 0.8 s apart at x between −0.75 and 0.7 (0.78 to 2.71).
- Unlock: difficulty 3; level 1-3.

### Enemy: Buckshot (CAT-17)

- Look: a stubby square grey ship with a wide multi-barrelled gun and orange markings.
- Body: 0.186 × 0.186; 4 health; 250 points; drops 10%.
- Moves: down at 0.45 to y = 0.45, stops to fire, then dives down at 0.6 off the bottom of the screen.
- Attack: once stopped, 2 shotgun blasts, the first 0.3 s after it stops, the second 0.8 s later (fired even off the
  play area). Each blast is 7 pellets (ENM-11) aimed at the player, spread evenly over 50° (from −25° to +25°), at
  speeds 0.4, 0.525, 0.65, 0.483, 0.608, 0.442 and 0.567 in that order. After the second blast it dives.
- Groups: a line at x 0, 1.33 apart (0.93): usually two side by side.
- Unlock: difficulty 4; level 1-4.
