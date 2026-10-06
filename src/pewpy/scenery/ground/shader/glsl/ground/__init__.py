"""The ground shader's fragment program (after the common part), in pieces.

Its inputs, a painter per kind of ground (each in its own module, see STYLES), what's below height 0, and its main.
Its colors come from `palette` (`%(palette)s`: its size).
"""

from pewpy.scenery.ground.shader.glsl.ground import (
    built_up,
    canyon,
    fluid,
    forest,
    main,
    mountains,
    salt_pan,
    savanna,
    scatter,
    uniforms,
)

PIECES = (
    uniforms,
    mountains,
    built_up,
    scatter,
    forest,
    canyon,
    salt_pan,
    savanna,
    fluid,
    main,
)
GROUND_SHADER = "".join(piece.GLSL for piece in PIECES)
