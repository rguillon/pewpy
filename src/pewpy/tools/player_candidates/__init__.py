"""Generate player ship candidates: voxel drawings for the Player candidates screen (data/models/candidates/player/).

    make players                                   # 60 ships, a new random batch each time
    make players ARGS="--kind phantom --count 20"
    make players ARGS="--seed 1234"                # the same batch again
    make players ARGS="--append --count 10"        # add to the batch instead of replacing it

(or `uv run python -m pewpy.tools.player_candidates ...`). Then open Main menu > Player candidates in `make dev`.

Assembled like the enemy candidates (pewpy.tools.candidates) from the same kit of parts. A ship's class, in the
spirit of the game's three ships (01-gameplay.md, "Ships"), sets its size: vanguard (balanced), juggernaut (heavy,
broad, armored), phantom (light, slim). Everything else is picked on its own (kit/archetypes.py, `player_ship`): its
hull among the class's five; its wings' layout (one pair, crossed X wings, stacked pairs, a small pair forward of the
main one, a flying wing, or wings carrying two booms) and outline (any of ten); its engines (at the tail, one to
three; at the booms' tails; in pods on the wings or along the hull); its cockpit; one to three kinds of weapons; fins,
intakes, armor, an antenna; and its paint: always a bluish grey, like the game's ships, with colored bits (a livery
stripe, a nose cone, wing stripes, markings, sensors).

Like the game's ships they point up the screen (their nose on the first row, their flames "towards" the bottom), are
drawn finer ("scale": 2: about 20 to 43 cubes across, up to 0.14 in the world, like the ships' hitboxes), and list
no weapons (the player's guns don't fire from the model). To use one in the game, copy it to data/models/player/ and
name it in data/ships.json.
"""
