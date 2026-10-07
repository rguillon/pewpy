# 02 — Enemies: the second fleet

Part of `02-enemies.md` (the rules every enemy follows are there). Units: see `00-vision.md`. Entries read as in
`02-enemies-catalog.md`: each entry is a requirement, the enemy shall look, measure, move, attack and come in groups
as its lines state.

The heavies (Behemoth, Warhawk, Pincer, Stormcrow, Condor, Rampart) come alone. *(placeholder: every number)*

### Enemy: Dart (FLT-1)

- Look: a tiny arrow, pointing the way it flies.
- Body: 0.06 × 0.073; 1.5 health; 80 points; drops 3%.
- Moves: dives straight down at 0.7; on reaching y = 0.35 it swerves once: its sideways speed becomes 2 × (the
  player's x − its x), at most 0.8 either way, and it flies on that way.
- Attack: none; it rams.
- Groups: a column at x −0.5 or 0.58, 0.35 to 0.4 s apart (3.54 to 4).
- Unlock: difficulty 1; level 1-1. A warm-up enemy. Also launched in pairs by the Behemoth.

### Enemy: Mite (FLT-2)

- Look: a small wedge.
- Body: 0.087 × 0.067; 1.5 health; 90 points; drops 3%.
- Moves: spirals down in a circle: sideways speed −0.36 × sin(3 × age), vertical speed −0.2 + 0.36 × cos(3 × age)
  (a circle 0.12 in radius, 3 radians per second, while coming down at 0.2).
- Attack: an aimed shot every 2 s, speed 0.5.
- Groups: a line at x 0, 0.75 or 0.67 apart (2.85, 1.75): usually three side by side.
- Unlock: difficulty 1; level 1-1. A warm-up enemy.

### Enemy: Tick (FLT-3)

- Look: a tiny ship with forward prongs, pointing the way it flies.
- Body: 0.1 × 0.08; 1 health; 100 points; drops 5%.
- Moves: the only enemy from behind: it appears just below the bottom of the play area at its wave's x and flies
  straight up at 0.45, and away through the top.
- Attack: one aimed shot, speed 0.55, when it reaches y = −0.2.
- Groups: a line at x 0, 0.83 or 0.67 apart (2.71, 2.01): lines of three or four.
- Unlock: difficulty 2; level 1-2.

### Enemy: Spark (FLT-4)

- Look: a tiny lopsided drone, pointing the way it flies.
- Body: 0.033 × 0.067; 1 health; 30 points; never drops.
- Moves: flies at 0.55, starting straight down, turning towards the player at up to 150° per second for 4 s; then
  flies straight on.
- Attack: none; it rams.
- Groups: a column at x −0.67, 0 or 0.67, 0.3 s apart (2.37 to 4.83).
- Unlock: difficulty 2; level 1-2. Also released in pairs by the Brood.

### Enemy: Imp (FLT-5)

- Look: a small ship with a light tail.
- Body: 0.127 × 0.12; 2.5 health; 120 points; drops 5%.
- Moves: straight down at 0.3.
- Attack: every 1.1 s, a cross of 4 shots (a ring of 4), speed 0.45, turned 22.5° more with each volley.
- Groups: a line at x 0, 0.75 or 0.67 apart (2.67, 2.15).
- Unlock: difficulty 2; level 1-2.

### Enemy: Hornet (FLT-6)

- Look: a small fighter with eight engines.
- Body: 0.247 × 0.12; 3 health; 180 points; drops 5%.
- Moves: zigzags down: down at 0.35 and sideways at 0.35, starting away from the player's side, reversing every 0.6 s
  and at the screen's edges.
- Attack: an aimed shot every 0.6 s, speed 0.55 (not staggered); a shot due while off the play area is skipped.
- Groups: a column 0.9 s apart at x −0.33, 0 or 0.5 (1.92 to 2.71): columns of three.
- Unlock: difficulty 3; level 1-3.

### Enemy: Catamaran (FLT-7)

- Look: two heavy hulls joined by a short deck.
- Body: 0.22 × 0.173; 7 health; 350 points; drops 15%.
- Moves: straight down at 0.2.
- Attack: every 1.2 s, a snaking shot straight down, speed 0.45, from the bottom of one hull (6 cubes right of its
  middle), then the next time from the other (6 cubes left), in turn.
- Groups: a line at x 0, 1.17 apart (1.66).
- Unlock: difficulty 3; level 1-3.

### Enemy: Albatross (FLT-8)

- Look: long thin straight wings and five engines.
- Body: 0.273 × 0.16; 6 health; 300 points; drops 15%.
- Moves: glides down at 0.18, weaving around the column it came down: x = its starting x + 0.3 (×W) ×
  sin(2π × age / 5 s).
- Attack: every 2.5 s, a fan of 5 shots 20° apart (straight down to 40° either side), speed 0.45.
- Groups: one at x −0.33 or 0.33 (0.84, 0.79).
- Unlock: difficulty 4; level 1-4.

### Enemy: Kestrel (FLT-9)

- Look: a swept-wing fighter with guns under its wings.
- Body: 0.233 × 0.12; 5 health; 300 points; drops 10%.
- Moves: comes in from a side and crosses the screen at 0.45 (×W), swooping: vertical speed −0.5 × cos(1.2 × age),
  down first, then back up.
- Attack: every 1.4 s, 3 shots aimed at the player, 12° apart, speed 0.5.
- Groups: a column from the left at y 0.6 or from the right at y 0.55, 1.2 s apart (1.28, 1.32): in pairs.
- Unlock: difficulty 5; level 1-5.

### Enemy: Stalker (FLT-10)

- Look: a narrow ship with two long engine wings.
- Body: 0.113 × 0.16; 4 health; 220 points; drops 10%.
- Moves: down at 0.18, sliding sideways at 0.3 towards the player's column (still once within 0.02 of it).
- Attack: whenever the player is within 0.06 of its column, a pair of shots straight down from its two guns (3 cubes
  either side of its middle), speed 0.6, at most every 0.6 s.
- Groups: a line at x 0, 1.33 or 0.83 apart (1.4, 1.07).
- Unlock: difficulty 5; level 1-5.

### Enemy: Rapier (FLT-11)

- Look: a long narrow ship, a blade with small wings.
- Body: 0.1 × 0.207; 3 health; 250 points; drops 5%.
- Moves: streaks straight down at 0.9.
- Attack: every 0.3 s, a pair of shots out to both sides, flying at (−0.55, −0.1) and (0.55, −0.1).
- Groups: a column at x 0.5, 1 s apart (1.47); a column at x −0.5 or 0.5, 0.8 s apart (1.85, 0.96).
- Unlock: difficulty 6; level 1-6.

### Enemy: Scrapper (FLT-12)

- Look: a lopsided junker with a turret on one side.
- Body: 0.1 × 0.1; 4 health; 200 points; drops 10%.
- Moves: drifts down at 0.25; every 0.5 s it changes its sideways speed to 0.25 × sin(n × 2.4 + x × 7), where n counts
  the changes so far and x is where it is; it turns back at the screen's edges.
- Attack: an aimed shot every 1.3 s, speed 0.55, from its side turret (4.5 cubes left of its middle, 0.5 cube up).
- Groups: a line at x 0, 0.83 apart (1.64).
- Unlock: difficulty 6; level 1-6.

### Enemy: Outrider (FLT-13)

- Look: a small ship with gun pods on both sides and forward lances.
- Body: 0.113 × 0.14; 4 health; 220 points; drops 10%.
- Moves: down at 0.35 to y = 0.55, stays there 5 s, then dives down at 0.7 off the bottom.
- Attack: while it stays, every 1.5 s, a burst of 3 pairs of shots 0.12 s apart, straight down from its pods (6.5
  cubes either side of its middle), speed 0.6.
- Groups: a line at x 0, 1.33 apart (1.3).
- Unlock: difficulty 6; level 1-6.

### Enemy: Needle (FLT-14)

- Look: a small ship with a long gun under its nose.
- Body: 0.127 × 0.1; 4 health; 250 points; drops 10%.
- Moves: down at 0.3 to y = 0.7; there it creeps sideways at 0.12 towards the player's column (still once within 0.02
  of it); after 12 s there it leaves by flying back up at 0.3.
- Attack: every 2.2 s, a stream of 5 shots 0.07 s apart straight down from the middle of its bottom edge, speed 0.8.
- Groups: one at x 0 or 0.33 (0.68, 0.47).
- Unlock: difficulty 7; level 2-5.

### Enemy: Wisp (FLT-15)

- Look: a small squat ship.
- Body: 0.073 × 0.067; 2 health; 150 points; drops 8%.
- Moves: down at 0.4 to y = 0.7, then blinks: it shows for 1.6 s, then vanishes for 0.5 s (hidden, it cannot be
  hurt), then shows again 0.618 of the play area's width further across (wrapping round from one side to the other,
  its whole hitbox kept inside) and 0.15 lower. After vanishing for the 4th time it shows again where it was and drops
  away at 0.6.
- Attack: one aimed shot each time it shows, 0.8 s after it shows, speed 0.55 (fired even off the play area).
- Groups: a line at x 0, 1.33 or 0.83 apart (1.37, 1.32).
- Unlock: difficulty 7; level 2-5.

### Enemy: Freighter (FLT-16)

- Look: a boxy cargo ship with wide flat wings.
- Body: 0.313 × 0.2; 10 health; 300 points; always drops a pickup when shot down (100%).
- Moves: straight down at 0.12.
- Attack: every 1.4 s, drops a mine (ENM-14) behind it, from the middle of its top edge.
- Groups: one at x −0.5 or 0.5 (0.66, 0.6).
- Unlock: difficulty 7; level 2-5.

### Enemy: Manta (FLT-17)

- Look: a very wide flat wing.
- Body: 0.18 × 0.12; 7 health; 400 points; drops 20%.
- Moves: comes in from a side and crosses the screen at 0.25 (×W).
- Attack: every 0.35 s, a shot straight down, speed 0.5, from one wingtip (0.45 of its width right of its middle),
  then the next time from the other (0.45 left), in turn.
- Groups: a column from the left or the right at y 0.5, 1.2 s apart (0.46, 0.49).
- Unlock: difficulty 9; level 3-5.

### Enemy: Broadside (FLT-18)

- Look: a wide gunboat with rows of guns on both sides.
- Body: 0.167 × 0.1; 7 health; 380 points; drops 15%.
- Moves: comes in from a side and crosses the screen at 0.22 (×W).
- Attack: every 1.5 s, fans of 3 shots out to both flanks: 25°, 45° and 65° from straight down on each side (6 shots),
  speed 0.45.
- Groups: a column from the left or the right at y 0.45, 1.2 s apart (0.36, 0.47).
- Unlock: difficulty 10; level 3-6.

### Enemy: Javelin (FLT-19)

- Look: a long narrow dart with long swept wings.
- Body: 0.1 × 0.18; 5 health; 250 points; drops 8%.
- Moves: down at 0.3 to y = 0.75; then for up to 1.5 s it glows white (a warning) and slides sideways at 0.5 towards
  the player's column (still once within 0.03 of it); as soon as it is within 0.03 of the player's column, or after
  the 1.5 s, it dives straight down at 1.4.
- Attack: none; it rams.
- Groups: a column at x 0.5 or −0.5, 1.5 s apart (0.98, 0.94).
- Unlock: difficulty 10; level 3-6.

### Enemy: Harrier (FLT-20)

- Look: a wide swept fighter with many guns.
- Body: 0.167 × 0.107; 6 health; 350 points; drops 15%.
- Moves: down at 0.3 to y = 0.6; there it drifts sideways at 0.15 towards the player's column (still once within
  0.02 of it); after 10 s there it leaves by flying back up at 0.3.
- Attack: every 2.5 s, a burst of 6 aimed shots 0.08 s apart, speed 0.6, scattered: each turned off its aim by −7.04°,
  +6.84°, +0.13°, −6.97°, +6.91° and 0° in turn.
- Groups: one at x 0 or −0.33 (0.54, 0.45); a line at x 0, 1.5 apart (0.62).
- Unlock: difficulty 10; level 3-6.

### Enemy: Brawler (FLT-21)

- Look: a lopsided gunboat with one big side cannon and swept wings.
- Body: 0.3 × 0.22; 9 health; 450 points; drops 20%.
- Moves: comes down at 0.15 drifting sideways at 0.08 (to the right first), turning back at the screen's edges.
- Attack: every 1.8 s, an aimed heavy shot (ENM-11), speed 0.5, from its cannon (8.5 cubes left of its middle, 4.5
  cubes down).
- Groups: one at x −0.33 or 0.5 (0.5, 0.41).
- Unlock: difficulty 11; level 4-5.

### Enemy: Brood (FLT-22)

- Look: a carrier with two big pods.
- Body: 0.207 × 0.147; 9 health; 450 points; drops 20%.
- Moves: straight down at 0.15.
- Attack: every 2.2 s, releases 2 Sparks (FLT-4), one from each pod (7 cubes either side of its middle).
- Groups: one at x 0.33 or 0.5 (0.52, 0.38).
- Unlock: difficulty 11; level 4-5.

### Enemy: Howitzer (FLT-23)

- Look: a wide ship with long guns under its wings.
- Body: 0.193 × 0.147; 7 health; 400 points; drops 15%.
- Moves: down at 0.3 to y = 0.75; there it edges sideways at 0.08, towards the middle first, turning back at the
  screen's edges; after 12 s there it leaves by flying back up at 0.3.
- Attack: every 2.6 s, lobs a shell (a cluster bomb, ENM-14) straight at the player at 0.5, timed to burst into its
  ring of 8 shots where the player was when it fired.
- Groups: one at x 0.5 or −0.5 (0.49, 0.38).
- Unlock: difficulty 12; level 4-6.

### Enemy: Rampart (FLT-24)

- Look: a tall armored ship between two heavy side walls; darker while armored.
- Body: 0.247 × 0.273; 12 health; 600 points; drops 30%.
- Moves: straight down at 0.12.
- Attack: in a cycle of 4.2 s counted from its arrival: armored for 3 s (it cannot be hurt), then open for 1.2 s. As it
  opens it fires a wall of 7 shots straight down from its bottom edge, evenly across 0.9 of its width (every 0.15 of
  its width from −0.45 to +0.45), speed 0.4. It can only be hurt while open.
- Groups: one at x 0, −0.33 or 0.5 (0.3 to 0.44).
- Unlock: difficulty 13; level 5-5. A heavy.

### Enemy: Condor (FLT-25)

- Look: a big cranked wing with eight engines.
- Body: 0.313 × 0.193; 18 health; 900 points; drops 35%.
- Moves: straight down at 0.1.
- Attack: every 1.6 s, in turn: 2 homing missiles (ENM-14), one from each wingtip (0.42 of its width either side of
  its middle); or 7 aimed shots at −30°, −15°, 0°, +15°, +30°, −7.5° and +7.5°, speed 0.5.
- Groups: one at x 0 (0.35).
- Unlock: difficulty 14; level 5-6. A heavy.

### Enemy: Warhawk (FLT-26)

- Look: a big forward-swept fighter with eight engines.
- Body: 0.22 × 0.227; 20 health; 1000 points; drops 50%.
- Moves: down at 0.3 to y = 0.55; there it strafes sideways at 0.15, towards the middle first, turning back at the
  screen's edges; after 16 s there, as soon as it is not in the middle of a volley, it leaves by flying back up at
  0.3.
- Attack: 2.4 s after each attack has finished, in turn: a spiral of 12 shots 0.1 s apart, each turned 30° clockwise
  from the one before (starting 30° clockwise of straight down), speed 0.45; or 3 aimed heavy shots 10° apart, speed
  0.5.
- Groups: one at x 0 or 0.33 (0.34).
- Unlock: difficulty 15; level 6-5. A heavy.

### Enemy: Stormcrow (FLT-27)

- Look: a big swept wing with a long tail.
- Body: 0.287 × 0.22; 15 health; 800 points; drops 35%.
- Moves: down at 0.3 to y = 0.6; there it drifts sideways at 0.06, towards the middle first, turning back at the
  screen's edges; after 12 s there it leaves by flying back up at 0.3.
- Attack: in each 2.8 s counted from its stop, during the first 1.6 s, a shot every 0.09 s, speed 0.5, its direction
  sweeping evenly from 60° on one side of straight down to 60° on the other; then a 1.2 s pause; each sweep goes the
  other way round from the one before. Not staggered.
- Groups: one at x 0, −0.33 or 0.33 (0.26 to 0.33).
- Unlock: difficulty 17; level 7-5. A heavy.

### Enemy: Pincer (FLT-28)

- Look: a big ship with two long prongs reaching forward.
- Body: 0.42 × 0.4; 22 health; 1100 points; drops 45%.
- Moves: down at 0.3 to y = 0.55; there it creeps sideways at 0.12 towards the player's column (still once within
  0.02 of it), holding still while it charges and fires; after 16 s there, as soon as it is not charging or firing,
  it leaves by flying back up at 0.3.
- Attack: every 4 s, it glows white for 0.9 s (a warning), then fires two red laser beams (ENM-12) 0.03 wide straight
  down from its prongs (10.5 cubes either side of its middle) for 0.7 s. The gap between the beams is narrower than a
  ship: the player must get out from under it.
- Groups: one at x 0 or −0.33 (0.32, 0.28).
- Unlock: difficulty 18; level 7-6. A heavy.

### Enemy: Behemoth (FLT-29)

- Look: a huge delta-winged carrier.
- Body: 0.38 × 0.307; 30 health; 1500 points; drops 60%.
- Moves: straight down at 0.1.
- Attack: every 1.6 s, in turn: launches 2 Darts (FLT-1), one from each side (0.3 of its width either side of its
  middle, 0.25 of its height below it), flying outwards at (±0.3, −0.5); a ring of 12 shots turned 15° (none straight
  down), speed 0.4; 2 Darts again; a ring of 12 shots, one straight down, speed 0.4.
- Groups: one at x 0 or 0.33 (0.31, 0.28).
- Unlock: difficulty 18; level 7-6. A heavy.

## Model cubes

- **FLT-30** "Cubes" in this file are the models' voxels: 0.06 / 9 ≈ 0.00667 wu each (see `05-visuals.md`).
