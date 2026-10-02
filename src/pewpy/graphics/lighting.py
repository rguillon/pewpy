"""Shiny look for the 3D models: per-pixel lighting, specular highlights and reflections.

A GLSL shader replaces Panda3D's per-vertex lighting on everything under `render`. Models reflect a made-up
space environment (dark blue sky, a bright light panel up-left, a warm glow down-right), more so at grazing
angles (Fresnel), so metal edges catch the light. Unlit things (stars, bullets, see-through effects) call
`setShaderOff()` next to `setLightOff()`. All strengths are in `config.py` (placeholders until 05-visuals.md
is decided).

Each voxel face is bevelled: near its edges the shader bends the normal outwards, so every cube catches the
light on its rims like a real rounded block. The texture coordinates of a voxel face count cubes across it
(from 0; one face can cover several cubes, see pewpy.graphics.models) and every cube gets its rims; other shapes have
(0.5, 0.5) everywhere, which means no bevel.

Water (the ocean background) is a flat surface whose normal the shader sways with moving waves, for glints.

Voxel faces are flat and most of them face the camera, so they all reflect about the same direction: up and
back towards the camera. The light panel sits there, wide and soft, so ships get a sheen that changes as they
move across the screen.
"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, NodePath, Shader

from pewpy import config

VERTEX_SHADER = """
#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
uniform vec4 p3d_ColorScale;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

out vec3 v_position;
out vec3 v_normal;
out vec4 v_color;
out vec2 v_uv;
out vec3 v_model;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    v_position = (p3d_ModelViewMatrix * p3d_Vertex).xyz;
    v_model = p3d_Vertex.xyz;
    v_normal = p3d_NormalMatrix * p3d_Normal;
    v_color = p3d_Color * p3d_ColorScale;
    v_uv = p3d_MultiTexCoord0;
}
"""

FRAGMENT_SHADER = """
#version 150

uniform struct p3d_LightSourceParameters {
    vec4 color;
    vec4 position;  // directional lights: direction towards the light, w = 0 (view space)
} p3d_LightSource[2];
uniform struct { vec4 ambient; } p3d_LightModel;
uniform mat4 p3d_ViewMatrixInverse;
uniform mat3 p3d_NormalMatrix;
uniform float osg_FrameTime;

uniform float shininess;
uniform float specular;
uniform float reflectivity;
uniform float bevel_width;
uniform float bevel_strength;
uniform vec2 water_offset;  // where this strip of sea starts in its loop, so the waves continue across strips
uniform float water_loop;  // length of the sea's loop: the waves repeat exactly once per loop
uniform vec4 haze;  // color of the air, and how much of it covers the farthest ground (0: none)
uniform vec3 tint;  // time of day on the grounds (1, 1, 1: daylight)

in vec3 v_position;
in vec3 v_normal;
in vec4 v_color;
in vec2 v_uv;
in vec3 v_model;

out vec4 fragment_color;

// Distances from the camera where the haze starts, and over which it reaches full strength: the ground goes
// from about 3.3 (bottom of the screen) to 5 (top).
const float HAZE_NEAR = 3.3;
const float HAZE_RANGE = 1.9;

// What the models reflect, by world direction: X right, Y away from the camera, Z up the screen.
vec3 environment(vec3 d) {
    vec3 sky = mix(vec3(0.02, 0.02, 0.07), vec3(0.2, 0.26, 0.5), smoothstep(-0.5, 0.9, d.z));
    vec3 panel = vec3(1.0, 0.97, 0.92) * 1.4 * pow(max(dot(d, normalize(vec3(-0.35, -0.8, 0.5))), 0.0), 12.0);
    vec3 glow = vec3(1.0, 0.45, 0.2) * 0.8 * pow(max(dot(d, normalize(vec3(0.8, -0.2, -0.55))), 0.0), 6.0);
    return sky + panel + glow;
}

// Tilts the normal towards the nearest edges of a voxel face. The face's directions along u and v come from
// how the position and texture coordinates change between neighboring pixels.
vec3 bevel(vec3 n, vec2 uv) {
    vec3 dp1 = dFdx(v_position);
    vec3 dp2 = dFdy(v_position);
    vec2 duv1 = dFdx(uv);
    vec2 duv2 = dFdy(uv);
    vec3 along_u = cross(dp2, n) * duv1.x + cross(n, dp1) * duv2.x;
    vec3 along_v = cross(dp2, n) * duv1.y + cross(n, dp1) * duv2.y;
    float length_max = sqrt(max(dot(along_u, along_u), dot(along_v, along_v)));
    if (length_max < 1e-12) {
        return n;  // not a voxel face: the texture coordinates don't change
    }
    // Small on screen (far away or tiny ship), the rims would only be a pixel wide and flicker: fade them out.
    float voxel_pixels = 1.0 / max(fwidth(uv.x), fwidth(uv.y));
    float strength = bevel_strength * smoothstep(1.5, 6.0, voxel_pixels);
    vec2 offset = fract(uv) - 0.5;  // within the cube: faces covering several cubes bevel each one
    vec2 edge = sign(offset) * smoothstep(0.5 - bevel_width, 0.5, abs(offset));
    return normalize(n + (along_u * edge.x + along_v * edge.y) / length_max * strength);
}

// A wave number along the loop close to `k` that fits a whole number of times in the loop.
float looping(float k) {
    return 6.2831853 * max(1.0, floor(k * water_loop / 6.2831853 + 0.5)) / water_loop;
}

// Ripples on the water: the normal sways with a few moving sine waves. Uses the model position (X right,
// Z up the screen), so the waves scroll with the sea.
vec3 waves(vec3 n) {
    float t = osg_FrameTime;
    vec2 p = v_model.xz + water_offset;
    vec2 slope = vec2(
        sin(p.x * 47.0 + p.y * looping(13.0) + t * 1.3) + 0.6 * sin(p.x * 89.0 - p.y * looping(61.0) + t * 2.1),
        cos(p.y * looping(53.0) - p.x * 17.0 - t * 1.1) + 0.6 * cos(p.y * looping(97.0) + p.x * 71.0 + t * 1.7)
    ) * 0.06;
    return normalize(n + p3d_NormalMatrix * vec3(slope.x, 0.0, slope.y));
}

void main() {
    // The texture coordinates say what kind of face this is (see pewpy.graphics.models): 0 and up on voxel faces, counting
    // cubes (mode 0), -2 to -1 for glowing faces like lit windows (GLOW_UVS, mode 1), -3.5 for water (WATER_UV,
    // mode 2), -6 to -5 for burning faces like lava (BURN_UVS, mode 3).
    float mode = v_uv.x >= 0.0 ? 0.0 : ceil(-v_uv.x / 2.0);
    float glow = float(mode == 1.0);
    float water = float(mode == 2.0);
    float burn = float(mode == 3.0);
    // Time of day: the ground is tinted (darker at night), but its lights keep their own colors.
    vec3 base = v_color.rgb * mix(tint, vec3(1.0), max(glow, burn));
    vec2 uv = v_uv + vec2(2.0 * mode, 0.0);  // glowing and burning faces: 0 to 1 across
    vec3 bevelled = bevel(normalize(v_normal), uv);  // outside the branch: it uses screen derivatives
    vec3 n = water > 0.5 ? waves(normalize(v_normal)) : bevelled;
    vec3 to_eye = normalize(-v_position);
    // Water: small sharp glints and some reflection, kept low so the sea stays dark behind the bullets.
    float face_shininess = mix(shininess, 90.0, water);
    float face_specular = mix(specular, 0.35, water);
    float face_reflectivity = mix(reflectivity, 0.1, water);

    vec3 diffuse = p3d_LightModel.ambient.rgb;
    vec3 highlight = vec3(0.0);
    for (int i = 0; i < p3d_LightSource.length(); ++i) {
        vec3 to_light = normalize(p3d_LightSource[i].position.xyz);
        vec3 light = p3d_LightSource[i].color.rgb;
        diffuse += light * max(dot(n, to_light), 0.0);
        float facing = max(dot(n, normalize(to_light + to_eye)), 0.0);
        highlight += light * face_specular * pow(facing, face_shininess);
    }

    float fresnel = face_reflectivity + (1.0 - face_reflectivity) * pow(1.0 - max(dot(n, to_eye), 0.0), 5.0);
    vec3 reflected = (p3d_ViewMatrixInverse * vec4(reflect(-to_eye, n), 0.0)).xyz;
    vec3 mirror = environment(normalize(reflected)) * mix(vec3(1.0), base, 0.5);  // metal tints what it reflects

    vec3 lit = base * diffuse * (1.0 - fresnel * 0.5) + highlight + mirror * fresnel;
    if (glow > 0.5) {
        // A bright pane in a dark frame, whatever the lighting: reads as a window even when tiny.
        vec2 from_middle = abs(uv - 0.5);
        float pane = 1.0 - smoothstep(0.28, 0.36, max(from_middle.x, from_middle.y));
        lit = mix(base * 0.3, base * 1.5, pane);
    }
    if (burn > 0.5) {
        // Shines all over, flickering slowly.
        lit = base * (1.15 + 0.25 * sin(osg_FrameTime * 2.3 + v_model.x * 41.0 + v_model.z * 33.0));
    }
    // Atmosphere: the farther away (towards the top of the screen), the more the air's color shows.
    float far = clamp((length(v_position) - HAZE_NEAR) / HAZE_RANGE, 0.0, 1.0);
    lit = mix(lit, haze.rgb, haze.a * far);
    fragment_color = vec4(lit, v_color.a);
}
"""


def setup(base: ShowBase) -> None:
    """Light the game's scene, and turn on the shiny shader for everything under `render`."""
    light(base.render)


def light(root: NodePath) -> None:
    """A scene's lights (a soft ambient light and a sun) and the shiny shader, for everything under `root`: the
    game's scene, or another one drawn the same way (the level select's preview).
    """
    ambient = AmbientLight("ambient")
    ambient.setColor((0.35, 0.35, 0.4, 1))
    root.setLight(root.attachNewNode(ambient))
    sun = DirectionalLight("sun")
    sun.setColor((0.9, 0.9, 0.85, 1))
    sun_node = root.attachNewNode(sun)
    sun_node.setHpr(-30, 20, 0)  # shining away from the camera, lighting the faces the camera sees
    root.setLight(sun_node)
    shader = Shader.make(Shader.SL_GLSL, VERTEX_SHADER, FRAGMENT_SHADER)
    root.setShader(shader)
    root.setShaderInput("shininess", config.SHININESS)
    root.setShaderInput("specular", config.SPECULAR)
    root.setShaderInput("reflectivity", config.REFLECTIVITY)
    root.setShaderInput("bevel_width", config.BEVEL_WIDTH)
    root.setShaderInput("bevel_strength", config.BEVEL_STRENGTH)
    root.setShaderInput("water_offset", (0.0, 0.0))  # set on each strip of sea, see pewpy.scenery.background.view
    root.setShaderInput("water_loop", 1.0)
    root.setShaderInput("haze", (0.0, 0.0, 0.0, 0.0))  # set on the grounds, see pewpy.scenery.background.view
    root.setShaderInput("tint", (1.0, 1.0, 1.0))  # the same
