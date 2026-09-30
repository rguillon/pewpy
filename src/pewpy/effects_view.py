"""Drawing the particles of effects.py: debris are small lit cubes, glowing particles soft circles (sprites.py).

Moving hundreds of nodes each frame is slow, so there is a single cube mesh drawn once per debris particle
(instancing). Each frame, their positions, colors and rotations are packed into a small float texture (one
column per particle) that the shader reads. The glowing ones go the same way through a SpriteBatch.
"""

from array import array

from panda3d.core import Lens, NodePath, OmniBoundingVolume, Shader, Texture, Vec3

from pewpy import models
from pewpy.effects import MAX_PARTICLES, Effects
from pewpy.sprites import Sprite, SpriteBatch

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


class EffectsView:
    """Debris are small lit cubes, tumbling; glowing particles (sparks, fireballs) are soft circles adding light."""

    def __init__(self, effects: Effects, render: NodePath, lens: Lens) -> None:
        self.effects = effects
        self.glows = SpriteBatch(render, lens, MAX_PARTICLES, glow=True, core=0.25, hot=0.6)
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
            Sprite(particle.x, particle.y, size, size, particle.color, depth=particle.z)
            for particle in self.effects.particles
            if particle.glow and (size := particle.current_size * GLOW_SIZE) > 0
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
