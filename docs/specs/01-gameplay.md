# 01 — Gameplay

## Global state

The game shall have a global state machine for each possible state to easily transition between states:

The states are:
- Main menu: start (to the ship selection), or quit
- Only with the dev tools (`make dev`, see `04-ui-audio.md`), screens opening from the main menu and going back to
  it:
  - Models: every ship and pickup model on show, for working on them
  - Bosses: every boss on show, a world per page
  - Enemy candidates, Boss candidates: numbered model candidates for new enemies (10 per page) and bosses (4 per
    page), to pick from
  - AI learning, AI rating: the AI learning to play while one of its brains plays on screen, and the levels'
    ratings for each ship (see `07-ai.md`); Escape goes back to the main menu
- World selection: select one of the worlds (see `03-levels.md`)
- Level selection: select one of the world's levels to play
- The actual game
- Pause menu: come back to the game or quit to the main menu.
- Game over menu: continue to restart the level or back to the main menu.
- Level complete: go on to the next level (into the next world after a world's last level) or back to the main
  menu; after the last level, "YOU WIN" and back to the main menu.


## Controls

| Action | Keyboard | Gamepad |
|--------|----------|---------|
| Move | arrow | TBD |
| Fire | space | TBD |
| Switch weapon | shift (cycles bullets → laser → missiles → bullets) | TBD |
| Special / bomb | crtl | TBD |
| Pause | escape | TBD |
| Menus | up/down arrows move the highlight, enter chooses, escape goes back | TBD |

- Auto-fire when holding the button? Yes: holding Fire keeps firing *(placeholder)*
- Rebindable keys? TBD

## Player ship

- Movement speed: 1.0 (the Vanguard's; see "Ships" below), in world units per second: 2 s to cross the play
  area from bottom to top *(placeholder unit; open: or express it in screen heights per second?)*
- Player movement have a little inertia: the speed eases towards the target in about 0.2 s, with a short drift
  on release (`responsiveness` in `data/rules.json`) *(placeholder)*
- full ship  Hitbox
- Starting lives: 5
- Health bar: 5 health per life (the Vanguard's; see "Ships" below). An enemy bullet does 1 damage, ramming an
  enemy 2. At 0 health the ship explodes, a life is lost and the level restarts (see "Game over and victory")
- Invulnerability time after being hit: 1 second (the ship blinks)
- Cant leave the screen edges
- The ship rolls up to 25° when moving sideways, for looks only (`PLAYER_BANK_ANGLE` in `app.py`) *(placeholder)*

### Ships

The player picks a ship before the world (see 04-ui-audio.md). It is kept for every life and level of the game.

| Ship | Health | Speed | Size (hitbox) | Special |
|------|--------|-------|---------------|---------|
| Vanguard | 5 | 1.0 | 0.12 | Balanced |
| Juggernaut | 8 | 0.8 | 0.14 | Heavy armor, a bit slower (and a bigger target) |
| Phantom | 3 | 1.3 | 0.10 | Repairs 0.5 health a second once it hasn't fired for 1.5 s, up to full |

*(numbers are a placeholder; in `data/ships.json`, the first one the default)* Weapons, lives and repairs work the same for
every ship; repairs fill up to the ship's own health.

## Weapons

> Units: damage per projectile, fire rate in shots per second, speed in world units per second
> (the play area is 2.5 wide and 2.0 tall). Angles are measured from straight up.

The ship carries three weapons from the start: **bullets**, **laser** and **missiles**. Only the selected one
fires; Shift switches to the next one, instantly. Each weapon has 5 upgrade levels and starts at level 1 *(the user's choice: it was 3)*.
The HUD shows the three weapons with their levels, the selected one highlighted. Every number below is data:
`data/weapons/player.json` (each level is a gun, like the enemies', see `06-technical.md`).

Shots fly until they are off the screen (the tilted camera shows more than the play area: up to about y 1.65).
Only enemies destroyed by the player's weapons score points and can drop pickups.

### Bullets (B, yellow)

Fast, reliable, good against groups at higher levels.

| Level | Pattern | Damage | Fire rate | Speed |
|-------|---------|--------|-----------|-------|
| 1 | single shot | 1.0 | 10.0 | 2.5 |
| 2 | 3-way spread: -12°, 0°, +12° | 0.8 each | 10.0 | 2.5 |
| 3 | 5-way spread: -24°, -12°, 0°, +12°, +24° | 0.8 each | 10.0 | 2.5 |
| 4 | 5-way spread: -24°, -12°, 0°, +12°, +24° | 1.0 each | 12.0 | 2.5 |
| 5 | 7-way spread: -30° to +30°, every 10° | 1.0 each | 12.0 | 2.5 |

Bullets are 0.02 x 0.05, fired from the ship's nose; they throw a few sparks where they hit.

### Laser (L, cyan)

A continuous beam straight up from the ship's nose, while Fire is held. Damage is per second while an enemy
touches the beam. Strong on a single target, but you have to line up.

| Level | Beam width | Damage per second | Pierces |
|-------|------------|-------------------|---------|
| 1 | 0.03 | 8.0 | no: the beam stops at the first enemy it touches |
| 2 | 0.05 | 12.0 | no |
| 3 | 0.08 | 18.0 | yes: the beam goes through every enemy above the ship |
| 4 | 0.11 | 24.0 | yes |
| 5 | 0.14 | 32.0 | yes |

The beam reaches the top of the screen when nothing stops it. A Shield Carrier's shield stops it without
damage. Enemies touching the beam flash white, and it throws sparks where it burns them.

### Missiles (M, orange)

Slow, heavy shots fired alternately from the left and right side of the ship. They explode on the first
enemy they hit.

| Level | Pattern | Damage | Fire rate | Speed | Notes |
|-------|---------|--------|-----------|-------|-------|
| 1 | 1 missile per shot, flies straight | 2.5 | 3.0 | 1.6 | |
| 2 | 1 missile per shot, homing | 2.5 | 3.0 | 1.6 | Turns toward the nearest enemy at up to 180°/s; flies straight if there is none |
| 3 | 2 missiles per shot (both sides at once), homing | 3.0 | 3.0 | 1.8 | Each explosion also does 1.5 damage to other enemies within 0.1 |
| 4 | 2 missiles per shot, homing | 3.5 | 3.5 | 2.0 | Splash 2.0 |
| 5 | 2 missiles per shot, homing | 4.0 | 4.0 | 2.2 | Splash 2.5 |

Missiles are 0.03 x 0.07, fired 0.05 in from each side of the ship. Homing missiles only aim at enemies on screen
(their middle anywhere the screen shows, above the play area too). Every missile explodes in an orange fireball where it hits.

### Weapon rules

- Upgrades come from upgrade capsules (see "Power-ups and pickups").
- Losing a life keeps the weapon levels and the selected weapon.
- Going on to the next level keeps the weapon levels, the score and the lives.
- "Continue" after game over resets all three weapons to level 1 and selects bullets.
- When the lives run out, display a game over screen (continue or back to the main menu)

## Secondary weapons

Some enemy drops give the ship a **secondary weapon** *(the user's idea)*. It fires on its own, whether Fire is
held or not, on top of the selected weapon. *(Everything below the first two rules is a placeholder;
`data/weapons/secondary.json`)*

- **A hit takes the secondary weapon instead of health** *(the user's choice)*: a shot or a ram while carrying one
  destroys the secondary weapon (a small explosion on the ship), the health stays, and the ship blinks,
  invulnerable for 1 second, as after any hit.
- The ship carries one secondary weapon at most: picking up another one replaces it.
- Losing a life loses the secondary weapon; it goes on to the next level; "Continue" starts without one.
- It is drawn on top of the ship, and shown on the HUD after the weapon levels (see `04-ui-audio.md`).

| Secondary | Pickup | What it does |
|-----------|--------|--------------|
| Turret | T, green | A little machine-gun turret on the ship: 5 shots a second at the nearest enemy on screen, turning to aim at it; 0.6 damage per shot, speed 2.5, shots 0.025 across. It doesn't fire without a target. |
| Lightning gun | Z, violet | Every 0.6 s, a bolt strikes the nearest enemy within 0.7 of the ship, then jumps to the nearest enemy not struck yet within 0.35 of the last one, up to 4 enemies; 2 damage to each. It waits for an enemy in range. The bolt shows for 0.12 s. |

Both only aim at enemies on screen (their middle anywhere the screen shows, above the play area too), and not at a
boss's core while its parts cover it. Like the main
weapons, they score and make enemies drop pickups.

- open: should they need Fire held? Should picking up the one already carried give points?

## Special / bomb

- Effect: TBD
- Number per life / how to get more: TBD

## Power-ups and pickups

| Pickup | Effect | Drop source / chance |
|--------|--------|----------------------|
| Upgrade capsule | Raises one weapon by one level (max 5), shown by its letter and color: B (yellow), L (cyan), M (orange). It doesn't change the selected weapon. At max level it gives 500 points instead. | Enemy drops, see "Drops" in `02-enemies.md`. Weapon picked at random, each equally likely. |
| Repair | Restores 2 health, up to the maximum. White with a red cross. | Enemy drops, see "Drops" in `02-enemies.md`. |
| Extra life | One more life, up to 9; beyond that, 1000 points. A green gem with a little white ship on it. *(the user's choice; look, cap and points are placeholders)* | Enemy drops: 4% of what enemies drop *(placeholder)* |
| Secondary weapon | Gives the ship a turret (T, green capsule) or a lightning gun (Z, violet capsule), see "Secondary weapons" | Enemy drops: 8% of what enemies drop, each equally likely *(placeholder)* |

- Pickups are 0.08 x 0.08, drift down at 0.25 units/s and disappear off the bottom of the screen.
- They are collected by touching them. Enemy bullets and enemies don't affect them.

## Scoring

- Points per enemy type: see `02-enemies.md`
- Combo / multiplier system: TBD
- Extra life thresholds: TBD
- High score table (local, how many entries, name entry): TBD

## Difficulty

- No dificulty level can be selected
- Difficulty ramp within a level: a warm-up wave, then the main waves, then a finale of the level's signature
  enemies close together
- Difficulty ramp across levels: each level has a difficulty from 1 (1-1) to 20 (8-6): 2 (world - 1) + level, so
  the levels of a world get harder one by one and a world starts as hard as the third level of the world before
  (see `03-levels.md`). With the difficulty, the generated levels (`pewpewdev/tools/make_levels.py`) scroll faster (0.2 to
  0.31), send bigger groups (about +7% per step), and send more: each half of a level has enemies adding up to a threat
  (their points) from 8600 to 22500, rising fast at first and slower later, spread over about 46 s, so harder
  levels are denser; the second half is as hard as a level 2 steps harder (see `03-levels.md`). New enemies come in
  along the way: each enemy unlocks at a difficulty (see "First appears in level" in `02-enemies-catalog.md` and
  `02-enemies-fleet.md`); a half's signature enemies, in its finale, are the ones the level unlocks first. Not playtested yet *(placeholder)*
- Continues: yes

## Game over and victory

- Game over condition: when the live counter reach zero and the player selected no to continue
- Losing a life puts the score back to what it was when the level started, so replaying waves can't farm
  points *(placeholder)*
- Continue restarts the current level with 5 lives, a score of 0 and the weapons at level 1 *(placeholder; open:
  should continue keep the score?)*
- Win condition: finishing the last level, 8-6 ("ALL LEVELS COMPLETE / YOU WIN")
