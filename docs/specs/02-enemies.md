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
- "Drops" gives the chance that a destroyed enemy leaves a pickup; when it does, 64% upgrade capsule, 4% extra life, 8% secondary
  weapon, 24% repair *(placeholder)* (see `01-gameplay.md`; the shares are in `data/rules.json`).
- Looks: every enemy is a voxel model in its colors, drawn in `data/models/<group>/<name>.json` (its description names
  its drawing) and built by `src/pewpy/graphics/models/`; the size given is its hitbox.
- Parts: any enemy can have destructible parts, like the bosses (see `02-enemies-bosses.md`): each is hit like an
  enemy of its own and gives its own points; the parts move with their enemy, and go with it when it is destroyed
  (without their points), rammed or leaves the screen. Their drawings are in their enemy's model file.
- "First appears in level" uses the worlds' places (see `03-levels.md`).
- What each enemy does is data: `data/enemies/` (`catalog.json`, `fleet.json`, `projectiles.json`), see
  `06-technical.md`, "Enemies as data".

## Enemy weapons

Shots come out of the weapons drawn on the enemy's model: a model lists its `weapons` (like its engines), each
numbered (1, 2...) with its kind (gun, gatling, cannon, turret, flak, missile, laser) and its barrel's tip, where the
shots leave it, facing down the screen. A gun names the weapons it fires from (`weapon`, or `weapons` to fire from
several at once), so one gun can be given per kind of shot; without them, an enemy's guns fire from its weapons in
turn (its state's first gun from weapon 1, the second from weapon 2...). The weapons turn with a model that faces the
way it flies. A model without weapons (or a gun with its own `origins`) fires from the gun's origins, as before.
The models the makers make (`src/pewpy/makers/`) always have weapons: at least one on an enemy, at least five on a boss (its core and
its parts together) *(the user's choice)*.

Besides plain shots (pink, 0.03), enemies use:

- Colored and sized shots: blue (Sniper), big orange "heavy" shots (0.05: bosses), small pellets
  (0.022, Buckshot), violet shots that snake from side to side across their line of flight (0.06 either way, a
  wave every 0.7 s: Serpent), and a red laser beam (Lancer: 0.035 wide, from the Lancer down past the bottom of
  the screen, for 0.5 s; it goes on through the player, who is briefly invulnerable after a hit anyway).
- Bosses' shots also come cyan, starting slow and speeding up ("accel"), and yellow, their path bending for 1.5 s
  then going straight ("curve"); bosses fire laser beams too, each announced 1 s before by a thin harmless red beam
  where it will be (see `02-enemies-bosses.md`).
- Projectiles that are small enemies of their own, launched by other enemies rather than placed by the waves: they
  can be shot down (a few points, no drops), and hitting the player they do 2 damage and are destroyed, like
  ramming. Enemy missiles are among the targets of the player's homing missiles.
    - Rocket (0.03 x 0.07, 1 health, 10 points): flies straight, from 0.25 speeding up by 1.0 per second to 1.1.
    - Homing missile (0.04 x 0.08, 2 health, 20 points): speed 0.45, turns towards the player at up to 100° per
      second for 3 s (its fuel), then flies straight on.
    - Cluster bomb (0.05, 1 health, 10 points): falls at 0.3 and after 1.2 s bursts into a ring of 8 shots (speed
      0.4), unless shot down first.

## Where the rest is

The catalog is split by section so each can be read on its own:

- `02-enemies-catalog.md` — Enemy catalog: Drone, Weaver, Diver, Gunship, Turret, Flak Cannon, Swarmer, Sniper, Mine Layer, Shield Carrier, Splitter, Rocketeer, Hunter, Bomber, Lancer, Serpent, Buckshot
- `02-enemies-fleet.md` — The second fleet: Albatross, Dart, Brawler, Manta, Hornet, Mite, Outrider, Condor, Needle, Kestrel, Javelin, Tick, Warhawk, Catamaran, Harrier, Behemoth, Wisp, Rampart, Imp, Howitzer, Stalker, Spark, Broadside, Rapier, Freighter, Scrapper, Brood, Stormcrow, Pincer
- `02-enemies-bosses.md` — Bosses (general rules, the mini bosses one by one, then the final bosses): Sentinel, Prowler, Rockbreaker, Siege Pod, Twin Fang, Relay Array, Mine Carrier, Warden, Thresher, Picket, Bulwark, Turbine, Silo Hauler, Hive Carrier, Tugmaster, Harvester, Clamp Barge, Pulsar, Frigate, Delta Raider, Cryo Fortress, Grappler, Dreadnought, Tidebreaker, Breacher, Cyclone, Borer, Bastion, Foundry, Scavenger, Magma Rig, Colossus, Patrol Drone, Enforcer, Hover Tank, Spire, Sentry Grid, Gunship Prime, Executor, Overmind
