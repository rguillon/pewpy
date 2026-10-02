"""The ground shader's fragment program (after the common part), in pieces: its inputs, a painter per kind of ground
(each in its own module, see STYLES), what's below height 0, and its main. Its colors come from `palette`
(`%(palette)s`: its size).
"""

from pewpy.scenery.ground.shader.glsl.ground import (
    built_up,
    canyon,
    cloud_deck,
    desert,
    fluid,
    forest,
    island,
    main,
    mountains,
    pack_ice,
    planet,
    scatter,
    swamp,
    uniforms,
    volcano,
)

PIECES = (
    uniforms,
    mountains,
    built_up,
    scatter,
    planet,
    island,
    desert,
    forest,
    canyon,
    pack_ice,
    volcano,
    swamp,
    cloud_deck,
    fluid,
    main,
)
GROUND_SHADER = "".join(piece.GLSL for piece in PIECES)
