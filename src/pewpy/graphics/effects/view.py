"""Drawing the particles of the effects (system.py): debris are small lit cubes, glowing particles soft
circles (sprites.py).

Moving hundreds of nodes each frame is slow, so there is a single cube mesh drawn once per debris particle
(instancing). Each frame, their positions, colors and rotations are packed into a small float texture (one
column per particle) that the shader reads. The glowing ones go the same way through a SpriteBatch.
"""

import math
from array import array

from panda3d.core import Lens, NodePath, OmniBoundingVolume, Shader, Texture, Vec3

from pewpy.graphics import models
from pewpy.graphics.effects.laser import PHOTON_STRETCH
from pewpy.graphics.effects.system import MAX_PARTICLES, ParticleSystem
from pewpy.graphics.sprites import Sprite, SpriteBatch

VERTEX_SHADER = """
#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
uniform sampler2D particles;  // row 0: position (x, depth, y) and size, row 1: color, row 2: axis and angle

in vec4 p3d_Vertex;
in vec3 p3d_Normal;

out vec3 v_normal;
out vec4 v_color;

vec3 rotate(vec3 v, vec4 axis_angle) {
    vec3 k = axis_angle.xyz;
    float c = cos(axis_angle.w), s = sin(axis_angle.w);
    return v * c + cross(k, v) * s + k * dot(k, v) * (1.0 - c);
}

void main() {
    vec4 place = texelFetch(particles, ivec2(gl_InstanceID, 0), 0);
    vec4 spin = texelFetch(particles, ivec2(gl_InstanceID, 2), 0);
    vec4 world = vec4(place.xyz + rotate(p3d_Vertex.xyz * place.w, spin), 1.0);
    gl_Position = p3d_ModelViewProjectionMatrix * world;
    v_normal = p3d_NormalMatrix * rotate(p3d_Normal, spin);
    v_color = texelFetch(particles, ivec2(gl_InstanceID, 1), 0);
}
"""

FRAGMENT_SHADER = """
#version 150

uniform struct p3d_LightSourceParameters {
    vec4 color;
    vec4 position;
} p3d_LightSource[2];
uniform struct { vec4 ambient; } p3d_LightModel;

in vec3 v_normal;
in vec4 v_color;

out vec4 fragment_color;

void main() {
    vec3 n = normalize(v_normal);
    vec3 light = p3d_LightModel.ambient.rgb;
    for (int i = 0; i < p3d_LightSource.length(); ++i) {
        light += p3d_LightSource[i].color.rgb * max(dot(n, normalize(p3d_LightSource[i].position.xyz)), 0.0);
    }
    fragment_color = vec4(v_color.rgb * light, 1.0);
}
"""


GLOW_SIZE = 1.6  # a soft circle's diameter, for a particle of size 1 (its edge fades, so it's drawn bigger)
LASER_COLOR = (0.4, 0.92, 1.0, 1)
ENEMY_LASER_COLOR = (1.0, 0.3, 0.2, 1)
HIT_COLOR = (0.8, 1.0, 1.0, 1)
# Glows at the ship's nose while the laser is on (it pulses) and where it hits something (it flickers): a base
# size plus so many beam widths.
MUZZLE_GLOW = (0.05, 1.5)
HIT_GLOW = (0.07, 1.5)
HALO_WIDTH = 2.4  # the soft halo around the laser, in beam widths: glowing circles one beam width apart
HALO_COLOR = (0.05, 0.22, 0.32, 1)  # dim: they overlap and add up
ENEMY_HALO_COLOR = (0.32, 0.05, 0.03, 1)
HALO_SPRITES = 64  # at most, per beam (a long beam's circles are further apart)
LASER_SPRITES = 1024  # room in the glow batch for the lasers' streaks and halos, on top of the particles


class EffectsView:
    """Debris are small lit cubes, tumbling; glowing particles (sparks, fireballs) are soft circles adding light."""

    def __init__(self, effects: ParticleSystem, render: NodePath, lens: Lens) -> None:
        self.effects = effects
        self.glows = SpriteBatch(render, lens, MAX_PARTICLES + LASER_SPRITES, glow=True, core=0.25, hot=0.6)
        mesh = models.MeshBuilder()
        mesh.box(Vec3(0, 0, 0), Vec3(1, 1, 1), (1, 1, 1, 1))
        self.node = render.attachNewNode(mesh.build("particles"))
        # The cubes are placed by the shader, anywhere: never skip drawing them because of the mesh's bounds.
        self.node.node().setBounds(OmniBoundingVolume())
        self.node.node().setFinal(True)
        self.node.setShader(Shader.make(Shader.SL_GLSL, VERTEX_SHADER, FRAGMENT_SHADER), 10)
        self.data = Texture("particles")
        self.data.setup2dTexture(MAX_PARTICLES, 3, Texture.T_float, Texture.F_rgba32)
        self.data.setMinfilter(Texture.FT_nearest)
        self.data.setMagfilter(Texture.FT_nearest)
        self.node.setShaderInput("particles", self.data)
        self.sync()

    def sync(self) -> None:
        particles = [particle for particle in self.effects.particles if not particle.glow][:MAX_PARTICLES]
        self.glows.show([
            *(
                Sprite(particle.x, particle.y, size, size, particle.color, depth=particle.z)
                for particle in self.effects.particles
                if particle.glow and (size := particle.current_size * GLOW_SIZE) > 0
            ),
            *self._laser_sprites(),
        ])
        padding = [0.0] * (4 * (MAX_PARTICLES - len(particles)))
        places, colors, spins = [], [], []
        # Panda3D keeps RGBA textures in memory as blue, green, red, alpha: each texel is written in that order
        # so the shader reads .rgba = (x, depth, y, size), (red, green, blue, unused), (axis x, y, z, angle).
        for particle in particles:
            places += (particle.y, particle.z, particle.x, particle.current_size)
            red, green, blue, _ = particle.color
            colors += (blue, green, red, 0.0)
            axis_x, axis_y, axis_z = particle.axis
            spins += (axis_z, axis_y, axis_x, particle.angle)
        self.data.setRamImage(array("f", places + padding + colors + padding + spins + padding).tobytes())
        self.node.setInstanceCount(len(particles))
        if particles:
            self.node.show()
        else:
            self.node.hide()

    def _laser_sprites(self) -> list[Sprite]:
        """Streaks of light shooting along the lasers, a soft halo around each, a pulsing glow where it starts (the
        ship's nose, an enemy's muzzle) and a flickering one where the player's burns something.
        """
        sprites = []
        for photon in self.effects.light.photons:
            width = photon.size * GLOW_SIZE * photon.fade
            sprites.append(Sprite(photon.x, photon.y, width, width * PHOTON_STRETCH, photon.color))
        time = self.effects.time
        for laser in self.effects.light.lasers.values():
            halo = laser.width * HALO_WIDTH
            steps = min(int((laser.top - laser.bottom) / laser.width), HALO_SPRITES)
            step = (laser.top - laser.bottom) / max(steps, 1)
            color = ENEMY_HALO_COLOR if laser.hostile else HALO_COLOR
            sprites += [Sprite(laser.x, laser.bottom + i * step, halo, halo, color) for i in range(steps + 1)]
            muzzle = (MUZZLE_GLOW[0] + laser.width * MUZZLE_GLOW[1]) * (1.0 + 0.15 * math.sin(time * 31.0))
            sprites.append(
                Sprite(laser.x, laser.source, muzzle, muzzle, ENEMY_LASER_COLOR if laser.hostile else LASER_COLOR)
            )
            flicker = 1.0 + 0.25 * math.sin(time * 47.0) * math.sin(time * 13.0)
            hit = (HIT_GLOW[0] + laser.width * HIT_GLOW[1]) * flicker
            sprites += [Sprite(laser.x, y, hit, hit, HIT_COLOR) for y in laser.hits]
        return sprites
