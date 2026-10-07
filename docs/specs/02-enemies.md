# 02 — Enemies

Units: see `00-vision.md`. Each enemy is described in `02-enemies-catalog.md` (the first enemies),
`02-enemies-fleet.md` (the second fleet) and `02-enemies-bosses.md` (the bosses).

## Coming in and leaving

- **ENM-1** An enemy coming from the top shall appear just above the top edge of the screen, out of sight: its middle
  as far above the screen's top edge as its highest point (its parts included) is above its middle (bosses start half
  their height higher still). It shall appear at the x its wave gives, moved inwards if needed so that it is entirely
  (its parts included) inside the play area's width.
- **ENM-2** An enemy coming from a side ("side entry") shall appear just beyond the left or right edge of the screen,
  at the height its wave gives, and fly across the screen at its crossing speed (×W), pointing the way it goes.
- **ENM-3** An enemy shall disappear, without points and without exploding, once it is more than 0.2 beyond any edge
  of the screen (the bottom edge being the play area's, y = −1). It shall never come back.
- **ENM-4** Bosses shall never leave the screen; they stay until destroyed.
- **ENM-5** Ground enemies (Turret, Flak Cannon) shall be fixed to the ground: they move down at the ground's speed,
  30% of the level's scroll speed (see `03-levels.md`).

## Shooting

- **ENM-6** An enemy shall only fire while its middle is on the play area (y below 1 and x between −1.25 and 1.25),
  unless stated otherwise: a shot that comes due while it is off the play area shall wait until it is on it.
- **ENM-7** Enemies of a group shall not fire all at once: an enemy whose gun is "staggered" shall fire its first
  shot after a random wait between 0.3 s and its gun's interval.
- **ENM-8** Unless stated otherwise, enemy shots shall be plain shots: 0.03 × 0.03, pink, 1 damage, flying straight
  at their speed until 0.05 beyond the screen.
- **ENM-9** Shots shall leave from the weapons drawn on the enemy's model (the tips of its barrels), or from the
  places the enemy's description gives. A model's weapons shall turn with a model that faces the way it flies.
- **ENM-10** "Aimed" shall mean aimed at the player's middle at the moment of firing. A pattern of several aimed shots
  shall be centred on that direction.
- **ENM-11** Shot kinds:

| Kind | Look | Size | Behaviour |
|------|------|-----:|-----------|
| Plain | Pink | 0.03 | Straight |
| Sniper | Blue | 0.03 | Straight |
| Heavy | Orange, bigger | 0.05 | Straight |
| Pellet | Pink, small | 0.022 | Straight |
| Snaking ("wave") | Violet | 0.03 | Snakes from side to side across its line of flight: 0.06 to each side, one full wave every 0.7 s |
| Accelerating ("accel") | Cyan | 0.03 | Starts at 35% of its speed, speeds up by 90% of its speed per second, up to 1.8 times its speed |
| Curving ("curve") | Yellow | 0.03 | Its path turns by its curve rate (degrees per second, counter-clockwise) for 1.5 s, then it flies straight |

- **ENM-12** A **laser beam** shall go straight down from its muzzle to 0.1 below the bottom of the play area, for
  its duration, doing 1 damage on contact. It shall go on through the player (the player is invulnerable for a moment
  after a hit anyway) and shall not hurt the player again while the player is invulnerable.
- **ENM-13** An enemy that "charges" before firing shall glow white for its charge time, then fire; the wait to its
  next shot shall start after it fires. An enemy that "holds" shall stand still while charging and while its beam
  lasts.

## Projectiles

- **ENM-14** Some enemies shall launch projectiles: small enemies of their own, which can be shot down (a few points,
  no drops), are targets for the player's homing missiles and secondary weapons, and do 2 damage when they hit the
  player, like a ram (they are destroyed doing so). The waves never place them on their own.

| Projectile | Size | Health | Points | Behaviour |
|------------|-----:|-------:|-------:|-----------|
| Rocket | 0.03 × 0.07 | 1 | 10 | Flies straight, starting at 0.25 and speeding up by 1.0 per second to 1.1; points the way it flies |
| Homing missile | 0.04 × 0.08 | 2 | 20 | Flies at 0.45, turning towards the player at up to 100° per second for 3 s (its fuel), then flies straight on; points the way it flies |
| Cluster bomb | 0.05 × 0.05 | 1 | 10 | Falls at 0.3; after 1.2 s (unless shot down first) it bursts: it blows up (no points) and fires a ring of 8 plain shots at speed 0.4, the first one 22.5° off straight down; it spins |
| Mine | 0.06 × 0.06 | 1 | 20 | Spiked ball, does not move by itself: drifts straight down at the level's scroll speed; it spins |

- **ENM-15** Mines and other projectiles shall count as enemies for the end of a level (a level only ends once they
  are gone).

## Being hit

- **ENM-16** An enemy shall lose health equal to the damage of each hit, unless it cannot be hurt in its current
  state; at 0 health it shall be destroyed.
- **ENM-17** An enemy shall flash white for 0.05 s when hit (bosses shall get brighter instead, see BOS-12).
- **ENM-18** Every destroyed or rammed enemy shall explode, with debris in its own colors (see `05-visuals.md`).
- **ENM-19** When the player's weapons destroy an enemy, the player shall score its points, and it shall drop a
  pickup with its drop chance (see GAM-58). Rammed enemies give no points and drop nothing.
- **ENM-20** When the player collides with an enemy that can be rammed, the enemy shall be destroyed and the player
  shall take 2 damage. Ramming shall not trigger what an enemy does when shot down (a Splitter does not split).

## Parts

- **ENM-21** Any enemy may have destructible parts (bosses always do). A part shall be hit like an enemy of its own,
  give its own points and drop a pickup with its own drop chance; it moves with its enemy.
- **ENM-22** When an enemy is destroyed, its parts left shall be destroyed with it, without their points. A part shall
  disappear with its enemy, never by leaving the screen on its own.

## Looks

- **ENM-23** Every enemy shall be a voxel model in its own colors, about the size of its hitbox (see
  `05-visuals.md`). Enemies that point "the way they fly" turn their model along their velocity; others point down
  the screen.
- **ENM-24** Enemy groups and the levels they first appear in are listed with each enemy; how the levels use them is
  in `03-levels.md`.
