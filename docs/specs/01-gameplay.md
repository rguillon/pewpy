# 01 — Gameplay

## Global state

The game shall have a global state machine for each possible state to easily transition between states:

The states are:
- Main menu: start (to the world selection), models, bosses, enemy candidates, boss candidates, or quit
- Models: every ship and pickup model on show, for working on them (see `04-ui-audio.md`)
- Bosses: every boss on show, a world per page (see `04-ui-audio.md`)
- Enemy candidates, Boss candidates: numbered model candidates for new enemies (10 per page) and bosses (4 per
  page), to pick from (see `04-ui-audio.md`)
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

- Auto-fire when holding the button? Yes: holding Fire keeps firing *(placeholder, see decisions.md)*
- Rebindable keys? TBD

## Player ship

- Movement speed: 1.0 (the Vanguard's; see "Ships" below)
- Player movement have a little inertia
- full ship  Hitbox
- Starting lives: 5
- Health bar: 5 health per life (the Vanguard's; see "Ships" below). An enemy bullet does 1 damage, ramming an
  enemy 2. At 0 health the ship explodes, a life is lost and the level restarts (see "Game over and victory")
- Invulnerability time after being hit: 1 second (the ship blinks)
- Cant leave the screen edges

### Ships

The player picks a ship before the world (see 04-ui-audio.md). It is kept for every life and level of the game.

| Ship | Health | Speed | Size (hitbox) | Special |
|------|--------|-------|---------------|---------|
| Vanguard | 5 | 1.0 | 0.12 | Balanced |
| Juggernaut | 8 | 0.8 | 0.14 | Heavy armor, a bit slower (and a bigger target) |
| Phantom | 3 | 1.3 | 0.10 | Repairs 0.5 health a second once it hasn't fired for 1.5 s, up to full |

*(numbers are a placeholder, see decisions.md; `SHIPS` in `player.py`)* Weapons, lives and repairs work the same for
every ship; repairs fill up to the ship's own health.

## Weapons

> Units: damage per projectile, fire rate in shots per second, speed in world units per second
> (the play area is 2.5 wide and 2.0 tall). Angles are measured from straight up.

The ship carries three weapons from the start: **bullets**, **laser** and **missiles**. Only the selected one
fires; Shift switches to the next one, instantly. Each weapon has 5 upgrade levels and starts at level 1 *(the user's choice: it was 3, see decisions.md)*.
The HUD shows the three weapons with their levels, the selected one highlighted.

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

Missiles are 0.03 x 0.07, fired 0.05 in from each side of the ship. Homing missiles only aim at enemies inside
the play area. Every missile explodes in an orange fireball where it hits.

### Weapon rules

- Upgrades come from upgrade capsules (see "Power-ups and pickups").
- Losing a life keeps the weapon levels and the selected weapon.
- Going on to the next level keeps the weapon levels, the score and the lives.
- "Continue" after game over resets all three weapons to level 1 and selects bullets.
- When the lives run out, display a game over screen (continue or back to the main menu)

## Special / bomb

- Effect: TBD
- Number per life / how to get more: TBD

## Power-ups and pickups

| Pickup | Effect | Drop source / chance |
|--------|--------|----------------------|
| Upgrade capsule | Raises one weapon by one level (max 5), shown by its letter and color: B (yellow), L (cyan), M (orange). It doesn't change the selected weapon. At max level it gives 500 points instead. | Enemy drops, see "Drops" in `02-enemies.md`. Weapon picked at random, each equally likely. |
| Repair | Restores 2 health, up to the maximum. White with a red cross. | Enemy drops, see "Drops" in `02-enemies.md`. |
| Extra life | One more life, up to 9; beyond that, 1000 points. A green gem with a little white ship on it. *(the user's choice; look, cap and points are placeholders, see decisions.md)* | Enemy drops: 4% of what enemies drop *(placeholder)* |

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
- Difficulty ramp across levels: from 1-1 to 5-8 (40 levels), the generated levels send bigger groups (about
  +3.5% per level) and waves come faster (from about 3.5 s to 2.1 s apart); new enemies come in along the way
  (see "First appears in level" in `02-enemies.md`). Not playtested yet *(placeholder, see decisions.md)*
- Continues: yes

## Game over and victory

- Game over condition: when the live counter reach zero and the player selected no to continue
- Win condition: finishing the last level, 5-8 ("ALL LEVELS COMPLETE / YOU WIN")
