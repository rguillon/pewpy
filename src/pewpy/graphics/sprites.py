"""Soft round sprites, drawn all at once: bullets, sparks, fireballs.

Each sprite is a circle (or an oval) that always faces the camera: solid in the middle, fading out towards its
edge. Like the particles, there is one small square drawn once per sprite (instancing), placed by the shader
from a float texture holding every sprite's position, size and color, filled each frame.
"""

import math
from array import array
from dataclasses import dataclass

from panda3d.core import (
    ColorBlendAttrib,
    Lens,
    NodePath,
    OmniBoundingVolume,
    Shader,
    Texture,
    TransparencyAttrib,
    Vec3,
)

from pewpy.graphics import models

Color = tuple[float, float, float, float]

VERTEX_SHADER = """
#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform sampler2D sprites;  // row 0: position (x, depth, y) and width, row 1: color and height
uniform vec2 focal;  // the lens's focal lengths: world size at the sprite's distance -> screen size

in vec4 p3d_Vertex;  // a square from -0.5 to 0.5 across (x) and up (z)

out vec2 v_corner;
out vec4 v_color;

void main() {
    vec4 place = texelFetch(sprites, ivec2(gl_InstanceID, 0), 0);
    vec4 look = texelFetch(sprites, ivec2(gl_InstanceID, 1), 0);
    vec2 size = vec2(place.w, look.a);
    // Facing the camera: the corners are moved on the screen around the projected middle, by the sprite's size
    // at its distance (clip coordinates are multiplied by the distance, so no division is needed).
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(place.xyz, 1.0);
    gl_Position.xy += p3d_Vertex.xz * size * focal;
    v_corner = p3d_Vertex.xz * 2.0;  // -1 to 1 across the sprite
    v_color = vec4(look.rgb, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 150

uniform float core;  // how much of the radius is solid before the edge fades out
uniform float hot;  // how much whiter the middle is

in vec2 v_corner;
in vec4 v_color;

out vec4 fragment_color;

void main() {
    float distance = length(v_corner);
    if (distance > 1.0) {
        discard;
    }
    float opacity = 1.0 - smoothstep(core, 1.0, distance);
    vec3 color = mix(v_color.rgb, vec3(1.0), hot * (1.0 - smoothstep(0.0, core, distance)));
    fragment_color = vec4(color * opacity, opacity);  // premultiplied: works for both blend modes
}
"""


@dataclass(frozen=True)
class Sprite:
    x: float  # world X
    y: float  # world Z (up the screen, like the game's y)
    width: float
    height: float
    color: Color
    depth: float = 0.0  # world Y (away from the camera)


class SpriteBatch:
    """Up to `capacity` sprites. `glow`: light is added to what's behind (sparks, fire); otherwise they're drawn
    over it, solid in the middle (bullets, readable on any background).
    """

    def __init__(self, render: NodePath, lens: Lens, capacity: int, glow: bool, core: float, hot: float) -> None:
        self.capacity = capacity
        mesh = models.MeshBuilder()
        mesh.quad(
            Vec3(-0.5, 0, -0.5), Vec3(0.5, 0, -0.5), Vec3(0.5, 0, 0.5), Vec3(-0.5, 0, 0.5), (1, 1, 1, 1), Vec3(0, 1, 0)
        )
        self.node = render.attachNewNode(mesh.build("sprites"))
        # Placed by the shader, anywhere: never skip drawing them because of the square's own bounds.
        self.node.node().setBounds(OmniBoundingVolume())
        self.node.node().setFinal(True)
        self.node.setShader(Shader.make(Shader.SL_GLSL, VERTEX_SHADER, FRAGMENT_SHADER), 10)
        horizontal, vertical = lens.getFov()
        focal = (1 / math.tan(math.radians(horizontal) / 2), 1 / math.tan(math.radians(vertical) / 2))
        self.node.setShaderInput("focal", focal)
        self.node.setShaderInput("core", core)
        self.node.setShaderInput("hot", hot)
        self.node.setLightOff()
        self.node.setTwoSided(True)
        self.node.setDepthWrite(False)  # see-through edges must not hide what's drawn after them
        self.node.setBin("fixed", 20)  # after the scene
        if glow:
            self.node.setAttrib(
                ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne)
            )
        else:  # "over", with colors already multiplied by their opacity
            self.node.setTransparency(TransparencyAttrib.MPremultipliedAlpha)
        self.data = Texture("sprites")
        self.data.setup2dTexture(capacity, 2, Texture.T_float, Texture.F_rgba32)
        self.data.setMinfilter(Texture.FT_nearest)
        self.data.setMagfilter(Texture.FT_nearest)
        self.node.setShaderInput("sprites", self.data)
        self.show([])

    def show(self, sprites: list[Sprite]) -> None:
        sprites = sprites[: self.capacity]
        self.data.setRamImage(pack(sprites, self.capacity))
        self.node.setInstanceCount(len(sprites))
        if sprites:
            self.node.show()
        else:
            self.node.hide()

    def destroy(self) -> None:
        self.node.removeNode()


def pack(sprites: list[Sprite], capacity: int) -> bytes:
    """The float texture's data: a row of positions and widths, then a row of colors and heights.

    Panda3D keeps RGBA textures in memory as blue, green, red, alpha: each texel is written in that order, so the
    shader reads .rgba = (x, depth, y, width) and (red, green, blue, height).
    """
    padding = [0.0] * (4 * (capacity - len(sprites)))
    places, looks = [], []
    for sprite in sprites:
        places += (sprite.y, sprite.depth, sprite.x, sprite.width)
        red, green, blue, _ = sprite.color
        looks += (blue, green, red, sprite.height)
    return array("f", places + padding + looks + padding).tobytes()
