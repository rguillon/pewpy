# 02 — Enemies: catalog

> Part of `02-enemies.md` (general rules and enemy weapons are there).
> Units: speed in world units per second (the play area is 2.5 wide and 2.0 tall, the player moves at 1.0),
> health in damage points (the starting weapon does 1.0 per bullet).

## Enemy catalog

### Enemy: Drone

- Look: grey armored drone with red markings, side vents and a red sensor eye, 0.1 x 0.1
- Health: 3
- Speed: 0.3
- Movement pattern: straight down
- Attack: one aimed shot at the player every 1.5 s, speed 0.6
- Points: 100
- Drops: 5%
- First appears in level: 1-1 (High Peaks)
- Notes: the basic enemy, used for most waves

### Enemy: Weaver

- Look: grey diamond-shaped interceptor with yellow wing stripes, 0.1 x 0.1
- Health: 2
- Speed: 0.35 down
- Movement pattern: sine wave, 0.25 amplitude left/right, one full wave every 2 s
- Attack: none
- Points: 80
- Drops: 5%
- First appears in level: 1-1 (High Peaks)
- Notes: comes in columns so the group snakes down the screen

### Enemy: Diver

- Look: grey arrowhead pointing down with orange markings, two rear engines and a red nose light, 0.1 x 0.12
- Health: 2
- Speed: 0.5 on entry, 1.2 when diving
- Movement pattern: comes down to y = 0.5 (upper quarter of the screen), waits 0.8 s, then dives in a straight
  line toward where the player was when it started diving, and keeps going off screen
- Attack: none, it tries to ram the player
- Points: 150
- Drops: 5%
- First appears in level: 1-1 (High Peaks)
- Notes: blinks during the 0.8 s wait to warn the player

### Enemy: Gunship

- Look: wide grey armored gunship with dark red markings, two big engine nacelles and three cannons, 0.2 x 0.14
- Health: 8
- Speed: 0.15
- Movement pattern: straight down
- Attack: 3-shot spread straight down (-20°, 0°, +20°) every 2 s, speed 0.5
- Points: 300
- Drops: 20%
- First appears in level: 1-1 (High Peaks)
- Notes: slow and tough, the first "take it down before it reaches you" enemy

### Enemy: Turret

- Look: grey gun emplacement with a dark dome, a red light and a barrel that turns to aim at the player, 0.12 x
  0.12
- Health: 6
- Speed: the ground's scroll speed, 30% of the level's (it is fixed to the ground, see 03-levels.md)
- Movement pattern: scrolls down with the background
- Attack: burst of 3 aimed shots, 0.15 s apart, every 2.5 s, speed 0.7
- Points: 250
- Drops: 10%
- First appears in level: 1-5 (Dusk Peaks)
- Notes: often placed in pairs on each side of the screen; ground levels only

### Enemy: Flak Cannon

- Look: grey octagonal gun emplacement with a dark gun housing, orange stripes and two barrels pointing down the
  screen, 0.12 x 0.12
- Health: 5
- Speed: the ground's scroll speed, 30% of the level's (it is fixed to the ground, see 03-levels.md)
- Movement pattern: scrolls down with the background
- Attack: every 1.8 s, 2 pairs of parallel shots (one per barrel, 0.05 apart), 0.2 s apart, straight down the
  screen (not aimed), speed 0.55
- Points: 200
- Drops: 10%
- First appears in level: 1-5 (Dusk Peaks)
- Notes: usually a pair, one on each side of the screen; ground levels only

### Enemy: Tank

- Look: grey tank with olive markings, treads along its top and bottom (it drives sideways) and a turret that turns
  to aim at the player, 0.16 x 0.12
- Health: 8
- Speed: the ground's scroll speed down (it is on the ground, 30% of the level's), and 0.1 sideways
- Movement pattern: crawls sideways over the ground, towards the middle of the screen first, turning back at the
  screen's edges
- Attack: one aimed shot every 2 s, speed 0.65
- Points: 300
- Drops: 15%
- First appears in level: 2-4 (Autumn Wood)
- Notes: alone or two in a row; ground levels only

### Enemy: Rocket Truck

- Look: grey truck with a rack of red-tipped rockets at the back and a yellow cab in front, pointing down the screen,
  0.1 x 0.16
- Health: 4
- Speed: the ground's scroll speed (30% of the level's) plus 0.15 (it drives down the road, faster than the ground)
- Movement pattern: straight down
- Attack: a big orange rocket (0.05, 1 damage) straight down the screen every 1.8 s, speed 0.5
- Points: 250
- Drops: 10%
- First appears in level: 2-5 (Twilight Grove)
- Notes: two or three in a column, down the same lane; ground levels only

### Enemy: Swarmer

- Look: small grey dart with green markings, pointing where it flies, 0.06 x 0.06
- Health: 1
- Speed: 0.6
- Movement pattern: enters from the left or right edge at the top third of the screen, flies straight in to the
  play area's edge, then follows a curve that bends down toward the bottom of the screen
- Attack: none
- Points: 50
- Drops: none
- First appears in level: 1-2 (Pine Ridge)
- Notes: always in groups of 6 to 10, spaced 0.2 s apart along the same path

### Enemy: Sniper

- Look: thin grey ship with blue markings and a long gun barrel, 0.08 x 0.14
- Health: 5
- Speed: 0.3 on entry, then 0.15 sideways
- Movement pattern: comes down to y = 0.7 and stays there, sliding left and right between the screen edges
- Attack: every 3 s, glows white for 0.5 s (warning), then fires one fast aimed shot, speed 0.9, blue
- Points: 350
- Drops: 15%
- First appears in level: 1-2 (Pine Ridge)
- Notes: leaves after 12 s by flying back up

### Enemy: Mine Layer

- Look: wide grey hauler with a purple mine bay and two engines, 0.18 x 0.08
- Health: 4
- Speed: 0.35 sideways
- Movement pattern: crosses the screen horizontally (left to right or right to left) at a fixed height
- Attack: drops a mine every 1 s. Mines are grey and purple spiked balls (0.06), 1 health, 20 points when shot, scroll down
  with the background (they spin), and do 2 damage on contact. Mines count as enemies: a level only ends once its
  mines are gone
- Points: 300
- Drops: 10%
- First appears in level: 2-6 (Moonlit Woods)
- Notes: mines fill the lower part of the screen, forcing the player to shoot a path through

### Enemy: Shield Carrier

- Look: large square grey carrier with teal shield emitters and two engines, 0.2 x 0.2, inside a see-through
  light blue bubble while the shield is up
- Health: 10
- Speed: 0.12
- Movement pattern: straight down
- Attack: shield up for 2 s (cannot be damaged), then shield down for 1.5 s, during which it fires a ring of
  8 bullets in all directions, speed 0.45. Shots hitting the shield are absorbed without damage; the shield
  also stops the laser
- Points: 500
- Drops: 30%
- First appears in level: 1-5 (Dusk Peaks)
- Notes: teaches the player to time their shots

### Enemy: Splitter

- Look: grey hub with three magenta-marked pods, 0.14 x 0.14
- Health: 6
- Speed: 0.25
- Movement pattern: straight down
- Attack: one aimed shot every 2 s, speed 0.5. When destroyed, it splits into 3 Swarmers that fly outward
  (left-down, straight down, right-down) at 0.6
- Points: 200 (the Swarmers give their own points)
- Drops: 10%
- First appears in level: 1-6 (Summit)
- Notes: destroying it close to the player is dangerous

### Enemy: Rocketeer

- Look: grey ship with a rocket pod on each side (red-tipped rockets) and red-orange markings, 0.12 x 0.12
- Health: 5
- Speed: 0.2
- Movement pattern: straight down
- Attack: every 2.5 s, a pair of rockets (one per pod, 0.09 apart) straight down (see "Enemy weapons")
- Points: 250
- Drops: 10%
- First appears in level: 1-2 (Pine Ridge)
- Notes: usually two side by side

### Enemy: Hunter

- Look: grey delta-winged ship with missile rails under its wings and teal markings, 0.14 x 0.12
- Health: 6
- Speed: 0.3 on entry, then 0.12 sideways
- Movement pattern: comes down to y = 0.65 and stays there, sliding left and right between the screen edges; leaves
  after 10 s by flying back up
- Attack: a homing missile every 3.2 s (see "Enemy weapons")
- Points: 350
- Drops: 15%
- First appears in level: 1-5 (Dusk Peaks)

### Enemy: Missile Silo

- Look: grey pad with hazard stripes and two dark hatch doors, 0.12 x 0.12
- Health: 7
- Speed: the ground's scroll speed, 30% of the level's (it is fixed to the ground, see 03-levels.md)
- Movement pattern: scrolls down with the background
- Attack: every 3.5 s, a homing missile launched upwards, which then turns round to chase the player
- Points: 350
- Drops: 15%
- First appears in level: 1-6 (Summit)
- Notes: ground levels only

### Enemy: Bomber

- Look: wide grey flying wing with four engines, a dark bomb bay in the middle and green markings, 0.22 x 0.12
- Health: 7
- Speed: 0.2 sideways
- Movement pattern: enters from the left or right edge and crosses the screen at a fixed height
- Attack: drops a cluster bomb every 1.6 s (see "Enemy weapons")
- Points: 400
- Drops: 20%
- First appears in level: 2-5 (Twilight Grove)

### Enemy: Lancer

- Look: narrow grey ship with a long glowing lance pointing down and red markings, 0.1 x 0.14
- Health: 5
- Speed: 0.35 on entry, then up to 0.2 sideways
- Movement pattern: comes down to y = 0.6, then slides towards the player's side (holding still while it charges
  and fires); leaves after 12 s by flying back up
- Attack: every 3.5 s, glows white for 0.8 s (warning), then fires its laser beam straight down for 0.5 s (see
  "Enemy weapons")
- Points: 350
- Drops: 15%
- First appears in level: 3-5 (Long Grass)

### Enemy: Serpent

- Look: grey ship with a wavy ribbed body, fins along its sides and violet markings, 0.12 x 0.14
- Health: 4
- Speed: 0.25
- Movement pattern: straight down
- Attack: every 1.6 s, 3 snaking shots aimed at the player, 18° apart, speed 0.45 (see "Enemy weapons")
- Points: 200
- Drops: 5%
- First appears in level: 1-3 (Glacier Pass)
- Notes: in columns of three

### Enemy: Buckshot

- Look: stubby square grey ship with a wide multi-barrelled gun and orange markings, 0.12 x 0.12
- Health: 4
- Speed: 0.45 on entry, 0.6 when leaving
- Movement pattern: comes down to y = 0.45, stops to fire, then dives off the bottom of the screen
- Attack: 2 shotgun blasts 0.8 s apart, each 7 small pellets aimed at the player, spread over 50°, at uneven speeds
  from 0.4 to 0.65 (see "Enemy weapons")
- Points: 250
- Drops: 10%
- First appears in level: 1-4 (Stormcrest)
- Notes: usually two side by side
