# 02 — Enemies

> Units: speed in world units per second (the play area is 2.5 wide and 2.0 tall, the player moves at 1.0),
> health in damage points (the starting weapon does 1.0 per bullet).

## General rules

- Enemies collide with the player: the player takes 2 damage and the enemy is destroyed (no points). Ramming
  doesn't split a Splitter.
- Enemies appear just beyond the screen's edges and fly in (the tilted camera shows more than the play area: up
  to about y 1.65 at the top, x ±1.86 at the sides). They disappear once they are fully off screen again. They
  don't come back.
- Enemies only shoot (and Mine Layers only drop mines) while inside the play area (x -1.25 to 1.25, below y 1).
- Enemy bullets: speed 0.4 to 0.9, small (0.03), drawn as soft round dots, pink unless stated otherwise. 1 damage
  each.
- Enemies flash white for 0.05 s when hit, and the whole time the laser touches them.
- Only enemies destroyed by the player's weapons score and drop pickups (including those a missile's explosion
  destroys), not rammed ones. Every destroyed or rammed enemy explodes (see `05-visuals.md`).
- "Drops" gives the chance that a destroyed enemy leaves a pickup; when it does, 70% upgrade capsule, 30% repair
  (see `01-gameplay.md`).
- Looks: every enemy is a voxel model in its colors, drawn in `src/pewpy/models/<name>.json` and built in code
  (`src/pewpy/models.py`); the size given is its hitbox.
- "First appears in level" uses the worlds' places (see `03-levels.md`).

## Enemy weapons

Besides plain shots (pink, 0.03), enemies use:

- Colored and sized shots: blue (Sniper), big orange "heavy" shots (0.05: bosses, Rocket Truck), small pellets
  (0.022, Buckshot), violet shots that snake from side to side across their line of flight (0.06 either way, a
  wave every 0.7 s: Serpent), and a red laser beam (Lancer: 0.035 wide, from the Lancer down past the bottom of
  the screen, for 0.5 s; it goes on through the player, who is briefly invulnerable after a hit anyway).
- Projectiles that are small enemies of their own, launched by other enemies rather than placed by the waves: they
  can be shot down (a few points, no drops), and hitting the player they do 2 damage and are destroyed, like
  ramming. Enemy missiles are among the targets of the player's homing missiles.
    - Rocket (0.03 x 0.07, 1 health, 10 points): flies straight, from 0.25 speeding up by 1.0 per second to 1.1.
    - Homing missile (0.04 x 0.08, 2 health, 20 points): speed 0.45, turns towards the player at up to 100° per
      second for 3 s (its fuel), then flies straight on.
    - Cluster bomb (0.05, 1 health, 10 points): falls at 0.3 and after 1.2 s bursts into a ring of 8 shots (speed
      0.4), unless shot down first.

## Enemy catalog

### Enemy: Drone

- Look: grey armored drone with red markings, side vents and a red sensor eye, 0.1 x 0.1
- Health: 3
- Speed: 0.3
- Movement pattern: straight down
- Attack: one aimed shot at the player every 1.5 s, speed 0.6
- Points: 100
- Drops: 5%
- First appears in level: 1-1
- Notes: the basic enemy, used for most waves

### Enemy: Weaver

- Look: grey diamond-shaped interceptor with yellow wing stripes, 0.1 x 0.1
- Health: 2
- Speed: 0.35 down
- Movement pattern: sine wave, 0.25 amplitude left/right, one full wave every 2 s
- Attack: none
- Points: 80
- Drops: 5%
- First appears in level: 1-1
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
- First appears in level: 1-1
- Notes: blinks during the 0.8 s wait to warn the player

### Enemy: Gunship

- Look: wide grey armored gunship with dark red markings, two big engine nacelles and three cannons, 0.2 x 0.14
- Health: 8
- Speed: 0.15
- Movement pattern: straight down
- Attack: 3-shot spread straight down (-20°, 0°, +20°) every 2 s, speed 0.5
- Points: 300
- Drops: 20%
- First appears in level: 1-1
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
- First appears in level: 1-8 (Minefield)
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
- First appears in level: 2-1 (Ground Defense)
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
- First appears in level: 2-3 (Greenwood)
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
- First appears in level: 2-5 (Harvest Dusk)
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
- First appears in level: 1-2
- Notes: always in groups of 6 to 10, spaced 0.2 s apart along the same path

### Enemy: Sniper

- Look: thin grey ship with blue markings and a long gun barrel, 0.08 x 0.14
- Health: 5
- Speed: 0.3 on entry, then 0.15 sideways
- Movement pattern: comes down to y = 0.7 and stays there, sliding left and right between the screen edges
- Attack: every 3 s, glows white for 0.5 s (warning), then fires one fast aimed shot, speed 0.9, blue
- Points: 350
- Drops: 15%
- First appears in level: 1-2
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
- First appears in level: 1-8
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
- First appears in level: 1-8
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
- First appears in level: 1-8
- Notes: destroying it close to the player is dangerous

### Enemy: Rocketeer

- Look: grey ship with a rocket pod on each side (red-tipped rockets) and red-orange markings, 0.12 x 0.12
- Health: 5
- Speed: 0.2
- Movement pattern: straight down
- Attack: every 2.5 s, a pair of rockets (one per pod, 0.09 apart) straight down (see "Enemy weapons")
- Points: 250
- Drops: 10%
- First appears in level: 1-2 (Red Drift)
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
- First appears in level: 2-1 (Ground Defense)

### Enemy: Missile Silo

- Look: grey pad with hazard stripes and two dark hatch doors, 0.12 x 0.12
- Health: 7
- Speed: the ground's scroll speed, 30% of the level's (it is fixed to the ground, see 03-levels.md)
- Movement pattern: scrolls down with the background
- Attack: every 3.5 s, a homing missile launched upwards, which then turns round to chase the player
- Points: 350
- Drops: 15%
- First appears in level: 2-2 (Patchwork)
- Notes: ground levels only

### Enemy: Bomber

- Look: wide grey flying wing with four engines, a dark bomb bay in the middle and green markings, 0.22 x 0.12
- Health: 7
- Speed: 0.2 sideways
- Movement pattern: enters from the left or right edge and crosses the screen at a fixed height
- Attack: drops a cluster bomb every 1.6 s (see "Enemy weapons")
- Points: 400
- Drops: 20%
- First appears in level: 2-4 (Mire)

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
- First appears in level: 3-1 (Archipelago)

### Enemy: Serpent

- Look: grey ship with a wavy ribbed body, fins along its sides and violet markings, 0.12 x 0.14
- Health: 4
- Speed: 0.25
- Movement pattern: straight down
- Attack: every 1.6 s, 3 snaking shots aimed at the player, 18° apart, speed 0.45 (see "Enemy weapons")
- Points: 200
- Drops: 5%
- First appears in level: 1-4 (Starlit Reach)
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
- First appears in level: 1-6 (Green Veil)
- Notes: usually two side by side

## The second fleet

Picked by the user from the model candidates (see `04-ui-audio.md`, "Candidates"; `src/pewpy/fleet.py`). Their
models are the chosen drawings, renamed (`src/pewpy/models/<name>.json`); their hitbox is the drawing's size. Each
level has two waves of them, in its two biggest gaps; the heavies (Behemoth, Warhawk, Pincer, Stormcrow, Condor,
Rampart) at least 22 s before the boss, so the fights don't overlap. *(placeholder, see decisions.md: every number)*

### Enemy: Albatross

- Look: long thin straight wings, five engines (model candidate #001), 0.17 x 0.10
- Health: 6
- Speed: 0.18 down
- Movement pattern: glides down, weaving 0.3 to each side every 5 s
- Attack: every 2.5 s, a fan of 5 shots straight down to 40° either side, speed 0.45
- Points: 300
- Drops: 15%
- First appears in level: 1-6 (Green Veil)

### Enemy: Dart

- Look: tiny arrow (model candidate #008), 0.06 x 0.07
- Health: 1.5
- Speed: 0.7
- Movement pattern: dives, then at y 0.35 swerves once towards the player's side (and flies on that way)
- Attack: none: it rams
- Points: 80
- Drops: 3%
- First appears in level: 1-1 (Outer Belt)
- Notes: also launched in pairs by the Behemoth

### Enemy: Brawler

- Look: lopsided gunboat with one big side cannon and swept wings (model candidate #011), 0.19 x 0.13
- Health: 9
- Speed: 0.15 down, 0.08 sideways
- Movement pattern: comes down drifting from side to side (turning back at the edges)
- Attack: every 1.8 s, a heavy shot at the player from its cannon (off to one side), speed 0.5
- Points: 450
- Drops: 20%
- First appears in level: 3-5 (Polar Night)

### Enemy: Manta

- Look: very wide flat wing (model candidate #024), 0.21 x 0.10
- Health: 7
- Speed: 0.25 across
- Movement pattern: enters from a side at height `y` and crosses the screen
- Attack: every 0.35 s, a shot straight down (speed 0.5) from one wingtip, then the other
- Points: 400
- Drops: 20%
- First appears in level: 3-1 (Archipelago)

### Enemy: Hornet

- Look: small fighter with eight engines (model candidate #025), 0.15 x 0.07
- Health: 3
- Speed: 0.35 down, 0.35 sideways
- Movement pattern: zigzags down, turning every 0.6 s (towards the player first)
- Attack: a shot at the player at each turn, speed 0.55
- Points: 180
- Drops: 5%
- First appears in level: 1-4 (Starlit Reach)
- Notes: in columns of three

### Enemy: Mite

- Look: small wedge (model candidate #037), 0.09 x 0.06
- Health: 1.5
- Speed: 0.2 down, circling at 0.36
- Movement pattern: spirals down in a 0.12-wide circle
- Attack: every 2 s, a shot at the player, speed 0.5
- Points: 90
- Drops: 3%
- First appears in level: 1-1 (Outer Belt)
- Notes: usually three side by side

### Enemy: Outrider

- Look: small ship with gun pods on both sides and forward lances (model candidate #041), 0.10 x 0.11
- Health: 4
- Speed: 0.35 on entry, 0.7 when leaving
- Movement pattern: comes down to y 0.55, stays 5 s, then dives off the bottom
- Attack: every 1.5 s, a burst of 3 pairs of shots straight down from its pods, 0.12 s apart, speed 0.6
- Points: 220
- Drops: 10%
- First appears in level: 2-3 (Greenwood)

### Enemy: Condor

- Look: big cranked wing, eight engines (model candidate #059), 0.23 x 0.13
- Health: 18
- Speed: 0.1 down
- Movement pattern: straight down, slowly
- Attack: every 1.6 s, in turn: 2 homing missiles from its wingtips, or a spread of 7 shots at the player (30° either side), speed 0.5
- Points: 900
- Drops: 35%
- First appears in level: 4-2 (Red Canyon)

### Enemy: Needle

- Look: small ship with a long gun under its nose (model candidate #065), 0.11 x 0.09
- Health: 4
- Speed: 0.3 on entry, then up to 0.12 sideways
- Movement pattern: comes down to y 0.7, creeps after the player's side, leaves after 12 s by flying back up
- Attack: every 2.2 s, a stream of 5 shots straight down, 0.07 s apart, speed 0.8
- Points: 250
- Drops: 10%
- First appears in level: 2-4 (Mire)

### Enemy: Kestrel

- Look: swept-wing fighter with guns under its wings (model candidate #068), 0.18 x 0.10
- Health: 5
- Speed: 0.45 across, up to 0.5 up or down
- Movement pattern: enters from a side and swoops down, then back up, while crossing
- Attack: every 1.4 s, 3 shots at the player 12° apart, speed 0.5
- Points: 300
- Drops: 10%
- First appears in level: 2-1 (Ground Defense)
- Notes: in pairs

### Enemy: Javelin

- Look: long narrow dart with long swept wings (model candidate #087), 0.10 x 0.19
- Health: 5
- Speed: 0.3 on entry, 0.5 sideways when aiming, 1.4 diving
- Movement pattern: comes down to y 0.75, lines up with the player for up to 1.5 s (glowing white: a warning), then dives straight down
- Attack: none: it rams
- Points: 250
- Drops: 8%
- First appears in level: 3-2 (Pack Ice)

### Enemy: Tick

- Look: tiny ship with forward prongs (model candidate #095), 0.07 x 0.04
- Health: 1
- Speed: 0.45 up
- Movement pattern: comes in from the bottom of the screen and flies up and away
- Attack: one shot at the player on the way up (at y -0.2), speed 0.55
- Points: 100
- Drops: 5%
- First appears in level: 1-3 (Rubble Run)
- Notes: the only enemy from behind: in lines of three or four

### Enemy: Warhawk

- Look: big forward-swept fighter, eight engines (model candidate #109), 0.18 x 0.19
- Health: 20
- Speed: 0.3 on entry, 0.15 sideways
- Movement pattern: comes down to y 0.55, strafes from side to side for 16 s, then leaves by flying back up
- Attack: every 2.4 s, in turn: a spiral of 12 shots (0.1 s apart, speed 0.45), or 3 heavy shots at the player 10° apart, speed 0.5
- Points: 1000
- Drops: 50%
- First appears in level: 4-4 (High Peaks)
- Notes: a heavy: comes alone

### Enemy: Catamaran

- Look: two heavy hulls joined by a short deck (model candidate #146), 0.11 x 0.07
- Health: 7
- Speed: 0.2 down
- Movement pattern: straight down
- Attack: every 1.2 s, a snaking shot straight down (speed 0.45) from one hull, then the other
- Points: 350
- Drops: 15%
- First appears in level: 1-5 (Shard Belt)

### Enemy: Harrier

- Look: wide swept fighter with many guns (model candidate #172), 0.17 x 0.10
- Health: 6
- Speed: 0.3 on entry, then up to 0.15 sideways
- Movement pattern: comes down to y 0.6, drifts after the player's side, leaves after 10 s by flying back up
- Attack: every 2.5 s, a burst of 6 shots at the player, 0.08 s apart, scattered up to 8°, speed 0.6
- Points: 350
- Drops: 15%
- First appears in level: 3-3 (Cloud Deck)

### Enemy: Behemoth

- Look: huge delta-winged carrier (model candidate #206), 0.23 x 0.22
- Health: 30
- Speed: 0.1 down
- Movement pattern: straight down, slowly
- Attack: every 1.6 s, in turn: launches 2 Darts from its sides, or fires a ring of 12 shots (every other ring turned 15°), speed 0.4
- Points: 1500
- Drops: 60%
- First appears in level: 5-3 (Downtown)
- Notes: a heavy: comes alone

### Enemy: Wisp

- Look: small squat ship (model candidate #219), 0.07 x 0.06
- Health: 2
- Speed: 0.4 on entry
- Movement pattern: comes down to y 0.7; shows for 1.6 s, vanishes for 0.5 s (can't be hit), shows again elsewhere 0.15 lower; after 4 blinks, drops away at 0.6
- Attack: one shot at the player each time it shows (halfway through), speed 0.55
- Points: 150
- Drops: 8%
- First appears in level: 2-4 (Mire)

### Enemy: Rampart

- Look: tall armored ship between two heavy side walls (model candidate #232), 0.17 x 0.21
- Health: 12
- Speed: 0.12 down
- Movement pattern: straight down, slowly
- Attack: armored (darker, can't be hurt) for 3 s, then open for 1.2 s: as it opens, a wall of 7 shots across its width, straight down, speed 0.4
- Points: 600
- Drops: 30%
- First appears in level: 4-1 (Dune Sea)
- Notes: only hurt while open

### Enemy: Imp

- Look: small ship with a light tail (model candidate #237), 0.07 x 0.08
- Health: 2.5
- Speed: 0.3 down
- Movement pattern: straight down
- Attack: every 1.1 s, a cross of 4 shots (speed 0.45) turned 22.5° more with each volley
- Points: 120
- Drops: 5%
- First appears in level: 1-2 (Red Drift)

### Enemy: Howitzer

- Look: wide ship with long guns under its wings (model candidate #239), 0.19 x 0.10
- Health: 7
- Speed: 0.3 on entry, 0.08 sideways
- Movement pattern: comes down to y 0.75, edges from side to side, leaves after 12 s by flying back up
- Attack: every 2.6 s, lobs a shell (a cluster bomb, speed 0.5) that bursts into a ring of 8 shots where the player was when it fired
- Points: 400
- Drops: 15%
- First appears in level: 3-6 (Storm Top)

### Enemy: Stalker

- Look: narrow ship with two long engine wings (model candidate #251), 0.10 x 0.14
- Health: 4
- Speed: 0.18 down, up to 0.3 sideways
- Movement pattern: comes down slowly, chasing the player's side
- Attack: when lined up with the player (within 0.06), a pair of shots straight down from its guns, at most every 0.6 s, speed 0.6
- Points: 220
- Drops: 10%
- First appears in level: 2-1 (Ground Defense)

### Enemy: Spark

- Look: tiny lopsided drone (model candidate #266), 0.03 x 0.05
- Health: 1
- Speed: 0.55
- Movement pattern: turns towards the player at up to 150° per second for 4 s, then flies straight on
- Attack: none: it rams
- Points: 30
- Drops: 0%
- First appears in level: 1-2 (Red Drift)
- Notes: also released in pairs by the Brood

### Enemy: Broadside

- Look: wide gunboat with rows of guns on both sides (model candidate #272), 0.15 x 0.09
- Health: 7
- Speed: 0.22 across
- Movement pattern: enters from a side at height `y` and crosses the screen
- Attack: every 1.5 s, fans of 3 shots out to both flanks (25°, 45° and 65° from straight down), speed 0.45
- Points: 380
- Drops: 15%
- First appears in level: 3-2 (Pack Ice)

### Enemy: Rapier

- Look: long narrow ship, a blade with small wings (model candidate #281), 0.10 x 0.20
- Health: 3
- Speed: 0.9 down
- Movement pattern: streaks straight down
- Attack: every 0.3 s, a pair of shots out to both sides (speed 0.55, drifting down a little)
- Points: 250
- Drops: 5%
- First appears in level: 2-2 (Patchwork)

### Enemy: Freighter

- Look: boxy cargo ship with wide flat wings (model candidate #297), 0.14 x 0.09
- Health: 10
- Speed: 0.12 down
- Movement pattern: straight down, slowly
- Attack: every 1.4 s, drops a mine behind it (see Mine Layer)
- Points: 300
- Drops: 100%
- First appears in level: 2-5 (Harvest Dusk)
- Notes: always drops a pickup when shot down

### Enemy: Scrapper

- Look: lopsided junker with a turret on one side (model candidate #365), 0.10 x 0.09
- Health: 4
- Speed: 0.25 down, up to 0.25 sideways
- Movement pattern: drifts down, changing its sideways course every 0.5 s
- Attack: every 1.3 s, a shot at the player from its turret, speed 0.55
- Points: 200
- Drops: 10%
- First appears in level: 2-2 (Patchwork)

### Enemy: Brood

- Look: carrier with two big pods (model candidate #372), 0.15 x 0.11
- Health: 9
- Speed: 0.15 down
- Movement pattern: straight down
- Attack: every 2.2 s, releases 2 Sparks from its pods
- Points: 450
- Drops: 20%
- First appears in level: 3-4 (Sunset Isles)

### Enemy: Stormcrow

- Look: big swept wing with a long tail (model candidate #412), 0.21 x 0.15
- Health: 15
- Speed: 0.3 on entry, 0.06 sideways
- Movement pattern: comes down to y 0.6, drifts from side to side, leaves after 12 s by flying back up
- Attack: sweeps a stream of shots (every 0.09 s, speed 0.5) from 60° on one side of straight down to 60° on the other in 1.6 s, pauses 1.2 s, sweeps back
- Points: 800
- Drops: 35%
- First appears in level: 5-1 (Neon City)
- Notes: a heavy: comes alone

### Enemy: Pincer

- Look: big ship with two long prongs reaching forward (model candidate #422), 0.21 x 0.21
- Health: 22
- Speed: 0.3 on entry, then up to 0.12 sideways
- Movement pattern: comes down to y 0.55, creeps after the player's side, leaves after 16 s by flying back up
- Attack: every 4 s, glows white for 0.9 s (a warning), then fires two laser beams (0.03 wide) straight down from its prongs for 0.7 s, holding still; the gap between them is narrower than a ship
- Points: 1100
- Drops: 45%
- First appears in level: 5-2 (Refinery)
- Notes: a heavy: comes alone

## Bosses

> Placeholders chosen by Claude (see decisions.md): the rules in `src/pewpy/bosses.py`, every boss in
> `src/pewpy/boss_catalog.py`. Every level ends with its own boss (see `03-levels.md`), harder through each world.

General rules for every boss:

- A boss is a core and destructible parts around it (cannons, fins, turrets…). Each part is hit like an enemy of
  its own (shots, the laser, missiles and their splash), gives its own points and drops a pickup 30% of the time.
  Destroying the core destroys the parts left (without their points) and ends the fight; the core always drops a
  pickup.
- Looks: giant industrial ships (see `05-visuals.md`): grey armor plates with seams, a raised deck, often a
  command tower with windows and a glowing reactor, ribbed engine nacelles at the back, the boss's color as
  markings; parts are machines (turrets, cannons, launchers, clamps, generators...). Voxel models drawn in
  `src/pewpy/models/` (one per core or kind of part), with the same cubes as every other model; each drawing is
  about as big as its hitbox.
- Entry: comes down from above the screen at 0.25 and stops at y = 0.55, then sways left and right between the
  screen edges. It doesn't leave the screen and doesn't shoot before it stops.
- Health bar: at the top of the screen, with its name, for the core and parts together (see `04-ui-audio.md`).
- Phases: each phase has its own guns and sway speed. A phase ends when some parts are destroyed, or when the
  core's health falls below a fraction of its full health. At the start of each phase (and on arrival) the core
  flashes white and doesn't shoot for 1.2 s.
- Armored: in some phases shots bounce off the core (and the laser stops at it), which looks darker; its parts
  must be destroyed first.
- Guns: each belongs to the core or to a part and stops when its part is destroyed. Patterns: aimed (at the
  player), fan (around straight down, sometimes swinging left and right) and ring (all around; fired fast while
  turning, it makes a spiral), sometimes several shots in a row. Pink bullets, and big orange "heavy" ones
  (0.05 across).
- Ramming a boss or one of its parts: the player takes 2 damage, the boss isn't hurt.
- Hits make it brighter for a moment instead of white (it's shot at all the time).

### Boss: Sentinel

- Level: 1-1 (Outer Belt)
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

### Boss: Prowler

- Level: 1-2 (Red Drift)
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

### Boss: Rockbreaker

- Level: 1-3 (Rubble Run)
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

### Boss: Siege Pod

- Level: 1-4 (Starlit Reach)
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

### Boss: Twin Fang

- Level: 1-5 (Shard Belt)
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

### Boss: Relay Array

- Level: 1-6 (Green Veil)
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

### Boss: Mine Carrier

- Level: 1-7 (Cold Wake)
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

### Boss: Warden

- Level: 1-8 (Minefield)
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

### Boss: Thresher

- Level: 2-1 (Ground Defense)
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

### Boss: Picket

- Level: 2-2 (Patchwork)
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

- Level: 2-3 (Greenwood)
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

### Boss: Turbine

- Level: 2-4 (Mire)
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

### Boss: Silo Hauler

- Level: 2-5 (Harvest Dusk)
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

### Boss: Hive Carrier

- Level: 2-6 (Crater Fields)
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

### Boss: Tugmaster

- Level: 2-7 (Moonlit Woods)
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

### Boss: Harvester

- Level: 2-8 (Fogbound Fen)
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

### Boss: Clamp Barge

- Level: 3-1 (Archipelago)
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

### Boss: Pulsar

- Level: 3-2 (Pack Ice)
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

### Boss: Frigate

- Level: 3-3 (Cloud Deck)
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

### Boss: Delta Raider

- Level: 3-4 (Sunset Isles)
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

### Boss: Cryo Fortress

- Level: 3-5 (Polar Night)
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

### Boss: Grappler

- Level: 3-6 (Storm Top)
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

### Boss: Dreadnought

- Level: 3-7 (Dark Tide)
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

### Boss: Tidebreaker

- Level: 3-8 (Frozen Deep)
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

### Boss: Breacher

- Level: 4-1 (Dune Sea)
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

### Boss: Cyclone

- Level: 4-2 (Red Canyon)
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

### Boss: Borer

- Level: 4-3 (Ember Fields)
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

### Boss: Bastion

- Level: 4-4 (High Peaks)
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

### Boss: Foundry

- Level: 4-5 (Desert Night)
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

### Boss: Scavenger

- Level: 4-6 (Canyon Dusk)
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

### Boss: Magma Rig

- Level: 4-7 (Ashen Slopes)
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

### Boss: Colossus

- Level: 4-8 (Summit)
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

### Boss: Patrol Drone

- Level: 5-1 (Neon City)
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

### Boss: Enforcer

- Level: 5-2 (Refinery)
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

### Boss: Hover Tank

- Level: 5-3 (Downtown)
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

### Boss: Spire

- Level: 5-4 (Smelter)
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

### Boss: Sentry Grid

- Level: 5-5 (Neon Rain)
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

### Boss: Gunship Prime

- Level: 5-6 (Flare Stacks)
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

### Boss: Executor

- Level: 5-7 (Skyline)
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

### Boss: Overmind

- Level: 5-8 (The Core)
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
