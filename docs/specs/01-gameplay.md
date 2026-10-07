# 01 — Gameplay

Units: see `00-vision.md`.

## Screens and flow

- **GAM-1** The game shall have exactly these screens, and shall only move between them as listed:

| Screen | Can go to |
|--------|-----------|
| Main menu | Ship select, Dev menu (and Quit, which closes the game) |
| Ship select | World select, Main menu; Dev menu (when picking for the AI) |
| World select | Level select, Ship select |
| Level select | Playing, AI playing, World select |
| Playing | Paused, Game over, Level complete |
| Paused | Playing, Main menu |
| Game over | Playing (Continue), Main menu |
| Level complete | Playing (next level), Main menu |
| Dev menu | Main menu, Model browser, Music browser, Background browser, Ship select (AI playing), Screenshots |
| Model browser, Music browser, Background browser, Screenshots | Dev menu |
| AI playing | Level select |

- **GAM-2** The game shall start on the main menu. What each screen shows is in `04-ui-audio.md`.

## Controls

- **GAM-3** The keyboard controls shall be:

| Action | Key |
|--------|-----|
| Move | Arrow keys (several at once for diagonals) |
| Fire | Space, held: firing goes on as long as it is held |
| Switch weapon | Shift: selects the next weapon, bullets → laser → missiles → bullets |
| Pause | Escape |
| Music on / off | M |
| Menus | Up/Down move the highlight, Enter chooses, Escape goes back |

- **GAM-4** Holding Shift shall not stop or change the effect of the other keys (firing goes on while switching).
- **GAM-5** The game shall be played with the keyboard only; the keys shall not be rebindable.
- **GAM-6** There shall be no special weapon or bomb.

## Player ship

### Movement

- **GAM-7** The ship's wanted velocity shall be the move direction times the ship's speed; a diagonal shall be
  normalised so it is no faster than a straight move.
- **GAM-8** The ship's velocity shall ease towards the wanted velocity with a little inertia: each frame of `dt`
  seconds, velocity += (wanted − velocity) × (1 − e^(−12 × dt)), so it gets most of the way in about 0.2 s and drifts
  briefly on release *(placeholder)*.
- **GAM-9** The ship shall never leave the play area: its hitbox stays inside it, and its speed across a border
  it touches drops to 0.
- **GAM-10** The ship's hitbox shall be a square of its size (see "Ships").
- **GAM-11** The ship's model shall roll up to 25° when moving sideways, in proportion to its sideways speed over
  its top speed, for looks only *(placeholder)*.

### Arrival and departure

- **GAM-12** At the start of each life the ship shall fly in from just below the bottom of the screen to its
  starting place (x = 0, y = −0.75) in 1.5 s, slowing down as it arrives (its distance left shrinking with the cube
  of the time left) *(placeholder)*. Meanwhile the player shall not be able to steer or fire, nothing shall hit the
  ship, and the waves shall not start.
- **GAM-13** Once a level is over (see `03-levels.md`), the ship shall fly away on its own through the top of the
  screen, faster and faster (gaining 3 wu/s² upwards, its sideways speed fading away with the same inertia as
  GAM-8) *(placeholder)*. Its shots in flight shall go on, and it shall still collect pickups it touches. The level
  shall count as completed once the whole ship is above the top of the screen.

### Health, damage and lives

- **GAM-14** The player shall start a game with 5 lives.
- **GAM-15** The ship shall start each life with its full health (see "Ships").
- **GAM-16** An enemy shot shall do 1 damage; colliding with an enemy (ramming) shall do 2 damage.
- **GAM-17** After any hit the ship shall be invulnerable for 1 s and blink (hidden every other tenth of a second).
- **GAM-18** At most one hit shall be taken per frame: enemy shots are checked first, then enemies.
- **GAM-19** When the ship's health reaches 0, the ship shall explode, the player shall lose one life and lose the
  secondary weapon, and the level shall restart from its beginning: every enemy, shot and pickup removed, the waves
  restarted, full health, and the score put back to what it was when the level started (so replaying waves cannot
  farm points) *(placeholder)*. There shall be no checkpoints.
- **GAM-20** Losing a life shall keep the weapon levels and the selected weapon.
- **GAM-21** When the last life is lost, the game shall show the Game over screen.

### Self-repair

- **GAM-22** A ship with a repair rate shall repair itself once Fire has not been held for 1.5 s, at its repair rate
  (health per second), up to its full health. Holding Fire (whatever the weapon) shall reset the 1.5 s wait.

### Ships

- **GAM-23** The player shall pick a ship before picking a world; the ship shall be kept for every life and level of
  that game. The default ship (first in the list) shall be the Vanguard.
- **GAM-24** The ships shall be *(placeholder numbers)*:

| Ship | Description | Health | Speed | Size (hitbox) | Repairs (health/s) |
|------|-------------|-------:|------:|--------------:|-------------------:|
| Vanguard | Balanced | 5 | 1.0 | 0.196 | 0.3 |
| Juggernaut | Heavy armor, a bit slower | 8 | 0.8 | 0.188 | 0.2 |
| Phantom | Fast, light armor, the best repairs | 3 | 1.3 | 0.141 | 0.5 |
| Tester | For testing: unkillable, fully upgraded | 99999 | 1.2 | 0.196 | none |

- **GAM-25** The Tester shall be a ship for testing the game: it shall start every level and every Continue with
  every weapon at its top level (pickups then add nothing but points), it shall not be compared with the other ships
  on the ship select, and the AI shall never fly it.
- **GAM-26** Weapons, lives and pickups shall work the same for every ship.

## Weapons

- **GAM-27** The ship shall carry three weapons from the start: bullets, laser and missiles. Only the selected one
  shall fire, while Fire is held. Shift shall switch to the next weapon instantly.
- **GAM-28** Each weapon shall have 5 levels and start at level 1. Bullets shall be selected at the start of a game.
- **GAM-29** The weapons shall share one reload wait: switching weapons shall not let the ship fire sooner than the
  previous weapon's rate allows.
- **GAM-30** Firing on a fixed rate shall not drift: time a shot comes late shall be taken off the next wait.
- **GAM-31** The player's shots shall fly until they are 0.05 beyond the edge of the screen (which shows more than the
  play area, see VIS-5).
- **GAM-32** Only enemies destroyed by the player's weapons (shots, laser, missile splash, secondary weapons) shall
  score points and possibly drop a pickup.

### Bullets (letter B, yellow)

- **GAM-33** Bullets shall be 0.02 × 0.05, fired from the middle of the top edge of the ship's hitbox, straight
  ahead or at the angles below:

| Level | Angles | Damage each | Shots per second | Speed |
|------:|--------|------------:|-----------------:|------:|
| 1 | 0° | 1.0 | 10 | 2.5 |
| 2 | −12°, 0°, +12° | 0.8 | 10 | 2.5 |
| 3 | −24°, −12°, 0°, +12°, +24° | 0.8 | 10 | 2.5 |
| 4 | −24°, −12°, 0°, +12°, +24° | 1.0 | 12 | 2.5 |
| 5 | −30° to +30°, every 10° (7 shots) | 1.0 | 12 | 2.5 |

- **GAM-34** A bullet shall hit the first enemy it overlaps and disappear, throwing a few sparks.

### Laser (letter L, cyan)

- **GAM-35** While the laser is selected and Fire is held, a beam shall go straight up from the top of the ship's
  hitbox to the top of the screen, centred on the ship.
- **GAM-36** Every enemy the beam touches shall take the level's damage per second, continuously (damage × frame
  time). An enemy counts as touched when it overlaps the beam across, its top is above the beam's bottom and its
  bottom is below the top of the screen.
- **GAM-37** At levels 1 and 2 the beam shall stop at the first enemy it touches (the lowest one) and damage only it;
  from level 3 it shall go through every enemy in its way:

| Level | Beam width | Damage per second | Goes through enemies |
|------:|-----------:|------------------:|---------------------|
| 1 | 0.03 | 8 | no |
| 2 | 0.05 | 12 | no |
| 3 | 0.08 | 18 | yes |
| 4 | 0.11 | 24 | yes |
| 5 | 0.14 | 32 | yes |

- **GAM-38** An enemy that cannot be hurt (a raised shield, an armored state) shall still stop a non-piercing beam,
  without damage.
- **GAM-39** Enemies touched by the beam shall flash white the whole time, and the beam shall throw sparks where it
  burns them.

### Missiles (letter M, orange)

- **GAM-40** Missiles shall be 0.03 × 0.07, fired from the ship's middle height, 0.05 in from the left and right edges
  of its hitbox.
- **GAM-41** A missile shall explode on the first enemy it hits, doing its damage to it; with splash, every other
  enemy whose middle is within the splash radius of the missile shall take the splash damage too.
- **GAM-42** A homing missile shall turn towards the nearest enemy whose middle is on screen (enemy projectiles
  included), at most 180° per second, keeping its speed; with no such enemy it shall fly straight on.
- **GAM-43** The missile levels shall be:

| Level | Pattern | Damage | Shots per second | Speed | Homing | Splash |
|------:|---------|-------:|-----------------:|------:|--------|--------|
| 1 | 1 missile per shot, from the right side then the left side in turn | 2.5 | 3 | 1.6 | no | none |
| 2 | as level 1 | 2.5 | 3 | 1.6 | yes | none |
| 3 | 2 missiles per shot, one from each side | 3.0 | 3 | 1.8 | yes | 1.5 within 0.1 |
| 4 | as level 3 | 3.5 | 3.5 | 2.0 | yes | 2.0 within 0.1 |
| 5 | as level 3 | 4.0 | 4 | 2.2 | yes | 2.5 within 0.1 |

- **GAM-44** Every missile shall explode in an orange fireball where it hits (a small one without splash, one the size
  of the splash radius with splash).

### Weapon rules

- **GAM-45** Going on to the next level shall keep the score, the lives, the weapon levels, the selected weapon and
  the secondary weapon.
- **GAM-46** Continue after a game over shall restart the current level with 5 lives, a score of 0, every weapon at
  level 1 (top level for the Tester), bullets selected and no secondary weapon *(placeholder; open: should Continue
  keep the score?)*.

## Secondary weapons

- **GAM-47** Some pickups shall give the ship a secondary weapon *(placeholder: everything after GAM-49)*. It shall
  fire on its own, whether Fire is held or not, on top of the selected weapon.
- **GAM-48** The ship shall carry at most one secondary weapon: picking one up shall replace the one carried.
- **GAM-49** When the ship is hit (shot or ram) while carrying a secondary weapon, the secondary weapon shall be
  destroyed instead of health (a small explosion on the ship in its color), the health shall stay, and the ship shall
  be invulnerable and blink for 1 s as after any hit.
- **GAM-50** Losing a life shall lose the secondary weapon; it shall be kept into the next level; Continue shall
  start without one.
- **GAM-51** The secondary weapon shall be drawn on top of the ship and shown on the HUD (see `04-ui-audio.md`).
- **GAM-52** Secondary weapons shall only aim at enemies whose middle is on screen, and not at a boss's core where one
  of its living parts covers it (see BOS-8). They shall score and make enemies drop pickups like the main weapons.
- **GAM-53** Secondary weapons shall not fire without a target, and shall fire at once when a target comes after a
  wait long enough.
- **GAM-54** The **turret** (letter T, green) shall be a small gun on the ship firing 5 shots per second at the
  nearest enemy, turning to aim at it: 0.6 damage per shot, speed 2.5, shots 0.025 × 0.025, fired from the ship's
  middle.
- **GAM-55** The **lightning gun** (letter Z, violet) shall strike every 0.6 s: the nearest enemy within 0.7 of the
  ship, then the nearest enemy not struck yet within 0.35 of the last one struck, up to 4 enemies, 2 damage each.
  The bolt shall show for 0.12 s, from the ship's nose to each enemy struck in turn.
- Open: should secondary weapons need Fire held? Should picking up the one already carried give points?

## Pickups

- **GAM-56** Pickups shall be 0.08 × 0.08, drift down at 0.25 per second, spin on themselves, and disappear once
  more than 0.2 beyond the play area.
- **GAM-57** The ship shall collect a pickup by touching it. Enemies and enemy shots shall not affect pickups.
- **GAM-58** A destroyed enemy that drops something (its drop chance, see the enemies) shall drop, at its middle *(the
  shares are placeholders)*:

| Pickup | Share | Look | Effect |
|--------|------:|------|--------|
| Upgrade capsule | 64% | A capsule showing its weapon's letter and color: B yellow, L cyan, M orange; the weapon drawn at random, each equally likely | Raises that weapon by one level, up to 5, without changing the selected weapon; at level 5 it gives 500 points instead |
| Extra life | 4% | A green gem with a little white ship on it | One more life, up to 9; with 9 lives it gives 1000 points instead *(placeholder)* |
| Secondary weapon | 8% | A capsule: T green (turret) or Z violet (lightning gun), each equally likely | Gives that secondary weapon |
| Repair | 24% | White with a red cross | Restores 2 health, up to the ship's full health |

## Scoring

- **GAM-59** The score shall go up by an enemy's points when the player's weapons destroy it (see the enemy files),
  and by the pickup bonuses above.
- **GAM-60** Rammed enemies, enemies that leave the screen, and enemies blown up when a final boss dies shall give
  no points.
- **GAM-65** There shall be no combo or score multiplier, no extra life from score (only from pickups), and no
  high score table: the score shows during play only.

## Difficulty

- **GAM-61** There shall be no difficulty setting.
- **GAM-62** The difficulty shall rise level by level, as described in `03-levels.md`: each level has a difficulty
  from 1 to 20, and each half of a level starts with a warm-up wave, then its main waves, then a finale of its
  signature enemies close together.

## Game over and victory

- **GAM-63** The game shall be over when the last life is lost; the Game over screen offers Continue or the main
  menu (see `04-ui-audio.md`).
- **GAM-64** The game shall be won by completing the last level, 8-6: the game shows "ALL LEVELS COMPLETE / YOU WIN!"
  and goes back to the main menu.
