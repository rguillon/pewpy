# 02 — Enemies: the second fleet

> Part of `02-enemies.md` (general rules and enemy weapons are there).
> Units: speed in world units per second (the play area is 2.5 wide and 2.0 tall, the player moves at 1.0),
> health in damage points (the starting weapon does 1.0 per bullet).

## The second fleet

Picked by the user from the model candidates (see `04-ui-audio.md`, "Candidates"; `src/pewpy/game/enemies/fleet.py`). Their
models are the chosen drawings, renamed (`src/pewpy/models/<name>.json`); their hitbox is the drawing's size. Each
level has two waves of them, in its two biggest gaps; the heavies (Behemoth, Warhawk, Pincer, Stormcrow, Condor,
Rampart) at least 22 s before the boss, so the fights don't overlap. *(placeholder: every number)*

### Enemy: Albatross

- Look: long thin straight wings, five engines (model candidate #001), 0.17 x 0.10
- Health: 6
- Speed: 0.18 down
- Movement pattern: glides down, weaving 0.3 to each side every 5 s
- Attack: every 2.5 s, a fan of 5 shots straight down to 40° either side, speed 0.45
- Points: 300
- Drops: 15%
- First appears in level: 1-4 (Stormcrest)

### Enemy: Dart

- Look: tiny arrow (model candidate #008), 0.06 x 0.07
- Health: 1.5
- Speed: 0.7
- Movement pattern: dives, then at y 0.35 swerves once towards the player's side (and flies on that way)
- Attack: none: it rams
- Points: 80
- Drops: 3%
- First appears in level: 1-1 (High Peaks)
- Notes: also launched in pairs by the Behemoth

### Enemy: Brawler

- Look: lopsided gunboat with one big side cannon and swept wings (model candidate #011), 0.19 x 0.13
- Health: 9
- Speed: 0.15 down, 0.08 sideways
- Movement pattern: comes down drifting from side to side (turning back at the edges)
- Attack: every 1.8 s, a heavy shot at the player from its cannon (off to one side), speed 0.5
- Points: 450
- Drops: 20%
- First appears in level: 4-5 (Hay Moon)

### Enemy: Manta

- Look: very wide flat wing (model candidate #024), 0.21 x 0.10
- Health: 7
- Speed: 0.25 across
- Movement pattern: enters from a side at height `y` and crosses the screen
- Attack: every 0.35 s, a shot straight down (speed 0.5) from one wingtip, then the other
- Points: 400
- Drops: 20%
- First appears in level: 3-5 (Witchlight)

### Enemy: Hornet

- Look: small fighter with eight engines (model candidate #025), 0.15 x 0.07
- Health: 3
- Speed: 0.35 down, 0.35 sideways
- Movement pattern: zigzags down, turning every 0.6 s (towards the player first)
- Attack: a shot at the player at each turn, speed 0.55
- Points: 180
- Drops: 5%
- First appears in level: 1-3 (Glacier Pass)
- Notes: in columns of three

### Enemy: Mite

- Look: small wedge (model candidate #037), 0.09 x 0.06
- Health: 1.5
- Speed: 0.2 down, circling at 0.36
- Movement pattern: spirals down in a 0.12-wide circle
- Attack: every 2 s, a shot at the player, speed 0.5
- Points: 90
- Drops: 3%
- First appears in level: 1-1 (High Peaks)
- Notes: usually three side by side

### Enemy: Outrider

- Look: small ship with gun pods on both sides and forward lances (model candidate #041), 0.10 x 0.11
- Health: 4
- Speed: 0.35 on entry, 0.7 when leaving
- Movement pattern: comes down to y 0.55, stays 5 s, then dives off the bottom
- Attack: every 1.5 s, a burst of 3 pairs of shots straight down from its pods, 0.12 s apart, speed 0.6
- Points: 220
- Drops: 10%
- First appears in level: 1-6 (Summit)

### Enemy: Condor

- Look: big cranked wing, eight engines (model candidate #059), 0.23 x 0.13
- Health: 18
- Speed: 0.1 down
- Movement pattern: straight down, slowly
- Attack: every 1.6 s, in turn: 2 homing missiles from its wingtips, or a spread of 7 shots at the player (30° either side), speed 0.5
- Points: 900
- Drops: 35%
- First appears in level: 5-6 (Dark Tide)

### Enemy: Needle

- Look: small ship with a long gun under its nose (model candidate #065), 0.11 x 0.09
- Health: 4
- Speed: 0.3 on entry, then up to 0.12 sideways
- Movement pattern: comes down to y 0.7, creeps after the player's side, leaves after 12 s by flying back up
- Attack: every 2.2 s, a stream of 5 shots straight down, 0.07 s apart, speed 0.8
- Points: 250
- Drops: 10%
- First appears in level: 3-3 (Mistmarsh)

### Enemy: Kestrel

- Look: swept-wing fighter with guns under its wings (model candidate #068), 0.18 x 0.10
- Health: 5
- Speed: 0.45 across, up to 0.5 up or down
- Movement pattern: enters from a side and swoops down, then back up, while crossing
- Attack: every 1.4 s, 3 shots at the player 12° apart, speed 0.5
- Points: 300
- Drops: 10%
- First appears in level: 1-5 (Dusk Peaks)
- Notes: in pairs

### Enemy: Javelin

- Look: long narrow dart with long swept wings (model candidate #087), 0.10 x 0.19
- Health: 5
- Speed: 0.3 on entry, 0.5 sideways when aiming, 1.4 diving
- Movement pattern: comes down to y 0.75, lines up with the player for up to 1.5 s (glowing white: a warning), then dives straight down
- Attack: none: it rams
- Points: 250
- Drops: 8%
- First appears in level: 3-6 (Fogbound Fen)

### Enemy: Tick

- Look: tiny ship with forward prongs (model candidate #095), 0.07 x 0.04
- Health: 1
- Speed: 0.45 up
- Movement pattern: comes in from the bottom of the screen and flies up and away
- Attack: one shot at the player on the way up (at y -0.2), speed 0.55
- Points: 100
- Drops: 5%
- First appears in level: 1-2 (Pine Ridge)
- Notes: the only enemy from behind: in lines of three or four

### Enemy: Warhawk

- Look: big forward-swept fighter, eight engines (model candidate #109), 0.18 x 0.19
- Health: 20
- Speed: 0.3 on entry, 0.15 sideways
- Movement pattern: comes down to y 0.55, strafes from side to side for 16 s, then leaves by flying back up
- Attack: every 2.4 s, in turn: a spiral of 12 shots (0.1 s apart, speed 0.45), or 3 heavy shots at the player 10° apart, speed 0.5
- Points: 1000
- Drops: 50%
- First appears in level: 6-5 (Switchbacks)
- Notes: a heavy: comes alone

### Enemy: Catamaran

- Look: two heavy hulls joined by a short deck (model candidate #146), 0.11 x 0.07
- Health: 7
- Speed: 0.2 down
- Movement pattern: straight down
- Attack: every 1.2 s, a snaking shot straight down (speed 0.45) from one hull, then the other
- Points: 350
- Drops: 15%
- First appears in level: 1-3 (Glacier Pass)

### Enemy: Harrier

- Look: wide swept fighter with many guns (model candidate #172), 0.17 x 0.10
- Health: 6
- Speed: 0.3 on entry, then up to 0.15 sideways
- Movement pattern: comes down to y 0.6, drifts after the player's side, leaves after 10 s by flying back up
- Attack: every 2.5 s, a burst of 6 shots at the player, 0.08 s apart, scattered up to 8°, speed 0.6
- Points: 350
- Drops: 15%
- First appears in level: 3-6 (Fogbound Fen)

### Enemy: Behemoth

- Look: huge delta-winged carrier (model candidate #206), 0.23 x 0.22
- Health: 30
- Speed: 0.1 down
- Movement pattern: straight down, slowly
- Attack: every 1.6 s, in turn: launches 2 Darts from its sides, or fires a ring of 12 shots (every other ring turned 15°), speed 0.4
- Points: 1500
- Drops: 60%
- First appears in level: 7-6 (Meltdown)
- Notes: a heavy: comes alone

### Enemy: Wisp

- Look: small squat ship (model candidate #219), 0.07 x 0.06
- Health: 2
- Speed: 0.4 on entry
- Movement pattern: comes down to y 0.7; shows for 1.6 s, vanishes for 0.5 s (can't be hit), shows again elsewhere 0.15 lower; after 4 blinks, drops away at 0.6
- Attack: one shot at the player each time it shows (halfway through), speed 0.55
- Points: 150
- Drops: 8%
- First appears in level: 2-6 (Moonlit Woods)

### Enemy: Rampart

- Look: tall armored ship between two heavy side walls (model candidate #232), 0.17 x 0.21
- Health: 12
- Speed: 0.12 down
- Movement pattern: straight down, slowly
- Attack: armored (darker, can't be hurt) for 3 s, then open for 1.2 s: as it opens, a wall of 7 shots across its width, straight down, speed 0.4
- Points: 600
- Drops: 30%
- First appears in level: 5-5 (Squall Line)
- Notes: only hurt while open

### Enemy: Imp

- Look: small ship with a light tail (model candidate #237), 0.07 x 0.08
- Health: 2.5
- Speed: 0.3 down
- Movement pattern: straight down
- Attack: every 1.1 s, a cross of 4 shots (speed 0.45) turned 22.5° more with each volley
- Points: 120
- Drops: 5%
- First appears in level: 1-2 (Pine Ridge)

### Enemy: Howitzer

- Look: wide ship with long guns under its wings (model candidate #239), 0.19 x 0.10
- Health: 7
- Speed: 0.3 on entry, 0.08 sideways
- Movement pattern: comes down to y 0.75, edges from side to side, leaves after 12 s by flying back up
- Attack: every 2.6 s, lobs a shell (a cluster bomb, speed 0.5) that bursts into a ring of 8 shots where the player was when it fired
- Points: 400
- Drops: 15%
- First appears in level: 4-6 (Last Harvest)

### Enemy: Stalker

- Look: narrow ship with two long engine wings (model candidate #251), 0.10 x 0.14
- Health: 4
- Speed: 0.18 down, up to 0.3 sideways
- Movement pattern: comes down slowly, chasing the player's side
- Attack: when lined up with the player (within 0.06), a pair of shots straight down from its guns, at most every 0.6 s, speed 0.6
- Points: 220
- Drops: 10%
- First appears in level: 2-4 (Autumn Wood)

### Enemy: Spark

- Look: tiny lopsided drone (model candidate #266), 0.03 x 0.05
- Health: 1
- Speed: 0.55
- Movement pattern: turns towards the player at up to 150° per second for 4 s, then flies straight on
- Attack: none: it rams
- Points: 30
- Drops: 0%
- First appears in level: 1-3 (Glacier Pass)
- Notes: also released in pairs by the Brood

### Enemy: Broadside

- Look: wide gunboat with rows of guns on both sides (model candidate #272), 0.15 x 0.09
- Health: 7
- Speed: 0.22 across
- Movement pattern: enters from a side at height `y` and crosses the screen
- Attack: every 1.5 s, fans of 3 shots out to both flanks (25°, 45° and 65° from straight down), speed 0.45
- Points: 380
- Drops: 15%
- First appears in level: 3-6 (Fogbound Fen)

### Enemy: Rapier

- Look: long narrow ship, a blade with small wings (model candidate #281), 0.10 x 0.20
- Health: 3
- Speed: 0.9 down
- Movement pattern: streaks straight down
- Attack: every 0.3 s, a pair of shots out to both sides (speed 0.55, drifting down a little)
- Points: 250
- Drops: 5%
- First appears in level: 1-6 (Summit)

### Enemy: Freighter

- Look: boxy cargo ship with wide flat wings (model candidate #297), 0.14 x 0.09
- Health: 10
- Speed: 0.12 down
- Movement pattern: straight down, slowly
- Attack: every 1.4 s, drops a mine behind it (see Mine Layer)
- Points: 300
- Drops: 100%
- First appears in level: 2-5 (Twilight Grove)
- Notes: always drops a pickup when shot down

### Enemy: Scrapper

- Look: lopsided junker with a turret on one side (model candidate #365), 0.10 x 0.09
- Health: 4
- Speed: 0.25 down, up to 0.25 sideways
- Movement pattern: drifts down, changing its sideways course every 0.5 s
- Attack: every 1.3 s, a shot at the player from its turret, speed 0.55
- Points: 200
- Drops: 10%
- First appears in level: 3-4 (Sunken Bog)

### Enemy: Brood

- Look: carrier with two big pods (model candidate #372), 0.15 x 0.11
- Health: 9
- Speed: 0.15 down
- Movement pattern: straight down
- Attack: every 2.2 s, releases 2 Sparks from its pods
- Points: 450
- Drops: 20%
- First appears in level: 4-5 (Hay Moon)

### Enemy: Stormcrow

- Look: big swept wing with a long tail (model candidate #412), 0.21 x 0.15
- Health: 15
- Speed: 0.3 on entry, 0.06 sideways
- Movement pattern: comes down to y 0.6, drifts from side to side, leaves after 12 s by flying back up
- Attack: sweeps a stream of shots (every 0.09 s, speed 0.5) from 60° on one side of straight down to 60° on the other in 1.6 s, pauses 1.2 s, sweeps back
- Points: 800
- Drops: 35%
- First appears in level: 7-5 (Flare Stacks)
- Notes: a heavy: comes alone

### Enemy: Pincer

- Look: big ship with two long prongs reaching forward (model candidate #422), 0.21 x 0.21
- Health: 22
- Speed: 0.3 on entry, then up to 0.12 sideways
- Movement pattern: comes down to y 0.55, creeps after the player's side, leaves after 16 s by flying back up
- Attack: every 4 s, glows white for 0.9 s (a warning), then fires two laser beams (0.03 wide) straight down from its prongs for 0.7 s, holding still; the gap between them is narrower than a ship
- Points: 1100
- Drops: 45%
- First appears in level: 7-6 (Meltdown)
- Notes: a heavy: comes alone
