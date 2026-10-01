"""Drawing the smooth grounds of relief.py, and the props standing on the built-up ones: fine meshes painted by
shaders.

The ground shader works out what the ground is made of at every pixel. On natural grounds (the mountains): from
the height, the slope, how tucked-in the spot is (the relief's cavity) and procedural noise: rock with strata,
scree, snow, meadows, pines. On built-up grounds: from the layout's surface map (settlement.py: streets, pavements,
yards, fields...). Fine noise also bends the normal, so surfaces look rough at any distance.

The prop shader paints buildings, tanks, trees... from each face's material (props/): rows of windows
(more of them lit at dusk and night), glowing furnaces, flames and beacons, metal sheen, leafy crowns.

Their colors come from the level's scenery (params.py), as shader inputs: each painter reads its colors from
`palette` in the order STYLE_COLORS names them (built-up grounds: the settlement's, by surface, see SURFACE_SLOTS),
the fluid's from `fluid_colors`.

Both light with the same low sun, whose shadows (from the ground and from the props) are baked in a map of how
high the shadows reach (relief.py), read pixel by pixel: towers shade the streets and the roofs next to them.
Sky light, the level's haze and its time-of-day tint work like on the rest of the scene. The noise and the maps
loop with the ground (`ground_loop`), so there is no seam where the loop starts again.
"""

import numpy as np
from panda3d.core import (
    Geom,
    GeomEnums,
    GeomNode,
    GeomTriangles,
    GeomVertexArrayFormat,
    GeomVertexData,
    GeomVertexFormat,
    LVecBase3f,
    NodePath,
    PTA_LVecBase3f,
    SamplerState,
    Shader,
    Texture,
)

from pewpy.scenery.params import FLUID_COLORS, STYLE_COLORS, SceneryParams
from pewpy.scenery.relief import SHADOW_SOFTNESS, SUN_ALONG, SUN_RISE, Relief
from pewpy.scenery.settlement import Layout

# The ground shader's `style`: how it paints each kind of ground (anything else: 0, the mountains).
STYLES = {
    "city": 1.0,
    "refinery": 2.0,
    "farmland": 3.0,
    "planet": 4.0,
    "ocean": 5.0,
    "desert": 6.0,
    "forest": 7.0,
    "canyon": 8.0,
    "pack_ice": 9.0,
    "volcano": 10.0,
    "swamp": 11.0,
    "clouds": 12.0,
}
FLUIDS = {"water": 1.0, "lava": 2.0, "gap": 3.0}
PALETTE_SIZE = 16
# Built-up grounds' colors in the palette: the surface's number (settlement.py Surface) is its slot.
SURFACE_SLOTS = (
    "natural_low",
    "street",
    "pavement",
    "yard",
    "dirt_road",
    "wheat",
    "crop",
    "plowed",
    "lavender",
    "pasture_low",
    "farmyard",
    "natural_high",
    "pasture_high",
    "lamp",
)

VERTEX_SHADER = """
#version 150

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;
in vec4 p3d_MultiTexCoord0;

out vec3 v_position;
out vec3 v_normal;
out vec3 v_model;
out vec4 v_data;
out vec4 v_wall;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    v_position = (p3d_ModelViewMatrix * p3d_Vertex).xyz;
    v_normal = p3d_Normal;
    v_model = p3d_Vertex.xyz;
    v_data = p3d_Color;
    v_wall = p3d_MultiTexCoord0;
}
"""

# Shared by both fragment shaders: inputs, noise, shadows, light, haze.
COMMON = """
#version 150

uniform vec3 sun;  // towards the sun, model space
uniform vec4 haze;
uniform vec3 tint;
uniform float ground_offset;  // how far down the loop this strip starts (world units)
uniform float ground_loop;  // length of the loop: the noise and the maps repeat exactly once per loop
uniform float ground_width;
uniform sampler2D shadow_map;  // how high the shadows reach (world units), over the whole loop
uniform vec3 sun_color;
uniform vec3 sky_color;
uniform float haze_near;  // the haze starts this far from the camera...
uniform float haze_range;  // ...and is thickest this much farther

in vec3 v_position;
in vec3 v_normal;
in vec3 v_model;
in vec4 v_data;
in vec4 v_wall;

out vec4 fragment_color;

const vec3 EYE = vec3(0.0, -0.906, -0.423);  // towards the camera, from the ground (model space): tilted 25 degrees
const float SOFTNESS = %(softness)s;

float hash(vec2 cell) {
    return fract(sin(dot(cell, vec2(127.1, 311.7))) * 43758.5453);
}

// Value noise from 0 to 1, `scale` cells per world unit, looping along y once per ground loop.
float noise(vec2 p, float scale) {
    float period = max(floor(ground_loop * scale + 0.5), 1.0);
    vec2 q = vec2(p.x * scale, p.y * period / ground_loop);
    vec2 i = floor(q);
    vec2 f = fract(q);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(vec2(i.x, mod(i.y, period)));
    float b = hash(vec2(i.x + 1.0, mod(i.y, period)));
    float c = hash(vec2(i.x, mod(i.y + 1.0, period)));
    float d = hash(vec2(i.x + 1.0, mod(i.y + 1.0, period)));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Layers of noise, each twice as fine and half as strong. Few layers: finer ones would be smaller than a pixel,
// and every layer costs on every pixel of the ground.
float fbm(vec2 p, float scale, int layers) {
    float total = 0.0;
    float amplitude = 0.5;
    float norm = 0.0;
    for (int i = 0; i < layers; ++i) {
        total += amplitude * noise(p, scale);
        norm += amplitude;
        scale *= 2.03;
        amplitude *= 0.5;
    }
    return total / norm;
}

// Ground coordinates: x across, y down the loop (world units).
vec2 ground_point() {
    return vec2(v_model.x, ground_offset - v_model.z);
}

// 1 in the shadow of the ground or of the props, 0 in the sun (height: above the base layer).
float in_shadow(vec2 p, float height) {
    float reach = texture(shadow_map, vec2(p.x / ground_width, p.y / ground_loop)).r;
    return clamp((reach - height) / SOFTNESS + 0.5, 0.0, 1.0);
}

// 0 by day, about 0.4 at dusk, 1 at night (from the time-of-day tint).
float night() {
    return clamp((1.0 - (tint.r + tint.g + tint.b) / 3.0) / 0.45, 0.0, 1.0);
}

// Sunlight (blocked in shadows) and sky light (`open`: 0 in a deep hollow, 1 out in the open).
vec3 daylight(vec3 n, float shadow, float open) {
    float up = clamp(-n.y, 0.0, 1.0);
    return sun_color * max(dot(n, normalize(sun)), 0.0) * (1.0 - shadow) + sky_color * open * (0.6 + 0.4 * up);
}

vec3 hazy(vec3 lit) {
    float far = clamp((length(v_position) - haze_near) / haze_range, 0.0, 1.0);
    return mix(lit, haze.rgb, haze.a * far);
}
"""

GROUND_SHADER = """
uniform float style;  // what the ground is (STYLES)
uniform float fluid;  // what's below height 0: 0 nothing, 1 water, 2 lava, 3 gaps in clouds (FLUIDS)
uniform vec3 palette[%(palette)s];  // the painter's colors (STYLE_COLORS, SURFACE_SLOTS)
uniform vec3 fluid_colors[3];  // FLUID_COLORS
uniform float osg_FrameTime;
uniform sampler2D surface_map;  // built-up grounds: what covers each spot (settlement.py Surface) and its lot's number

// v_data: cavity, height (0 to 1 of the highest), depth under the fluid (world units), the landscape's mark

vec3 mountains(vec2 p, float height, float cavity, float flat_ground, float large, float medium, float fine,
               out float smooth_surface) {
    // Rock: dark grey-brown, banded in strata that follow the height (on steep faces), varied in patches.
    float strata = 0.5 + 0.5 * sin(height * 90.0 + medium * 6.0);
    strata = mix(0.5, strata, smoothstep(0.9, 0.6, flat_ground));
    vec3 rock = mix(palette[0], palette[1], strata * 0.6 + large * 0.4);
    rock *= 0.8 + 0.4 * fine;
    // Scree: paler gravel at the feet of the slopes.
    vec3 scree = palette[2] * (0.75 + 0.5 * fine);
    float scree_amount = smoothstep(0.35, 0.1, height) * smoothstep(0.02, 0.08, height) * (0.5 + medium);
    vec3 ground = mix(rock, scree, clamp(scree_amount, 0.0, 1.0));
    // Valley floors: meadows, and pine forest on the gentle lower slopes (dark green, speckled with trees).
    float valley = smoothstep(0.3, 0.15, height + 0.1 * large) * smoothstep(0.55, 0.8, flat_ground);
    vec3 meadow = mix(palette[3], palette[4], medium) * (0.85 + 0.3 * fine);
    float pines = smoothstep(0.42, 0.58, fbm(p, 45.0, 2) + 0.25 * (large - 0.5));
    vec3 pine = palette[5] * (0.5 + 0.9 * noise(p, 260.0));
    ground = mix(ground, mix(meadow, pine, pines), valley);
    // Snow: on the high ground where it can settle; steep faces stay bare rock, streaked with snow in gullies.
    float snow_line = 0.5 + 0.18 * (large - 0.5) - 0.25 * cavity;
    float settles = smoothstep(0.78, 0.9, flat_ground + 0.25 * (medium - 0.5) + 0.3 * cavity);
    float snow = smoothstep(snow_line, snow_line + 0.08, height) * settles;
    smooth_surface = snow;
    return mix(ground, palette[6] * (0.9 + 0.1 * fine), snow);
}

// Rows of a crop: stripes one way or the other (by the field's number), `strength` deep.
float furrows(vec2 p, float variant, float strength) {
    float along = mod(variant, 2.0) < 1.0 ? p.x : p.y;
    return 1.0 - strength + strength * (0.5 + 0.5 * sin(along * 6.2831853 / 0.012));
}

vec3 built_up(vec2 p, float large, float medium, float fine, out vec3 glow, out float smooth_surface) {
    vec4 texel = texture(surface_map, vec2(p.x / ground_width, p.y / ground_loop));
    float code = floor(texel.r * 255.0 + 0.5);
    float variant = floor(texel.g * 255.0 + 0.5);
    float shade = 0.9 + 0.2 * fract(variant * 0.618);  // each lot or field a little different
    glow = vec3(0.0);
    smooth_surface = 0.0;
    vec3 color;
    if (code == 1.0) {  // street: asphalt; at night, pools of amber lamp light at intervals
        color = palette[1] * (0.85 + 0.3 * fine);
        vec2 cell = floor(p / 0.1);
        float lamp = step(0.4, hash(cell)) * smoothstep(0.02, 0.0, length(fract(p / 0.1) - 0.5) * 0.1);
        glow = palette[13] * lamp * night() * 0.6;
    } else if (code == 2.0) {  // pavement: concrete slabs
        vec2 slab = abs(fract(p / 0.02) - 0.5);
        color = palette[2] * (0.9 + 0.2 * fine) * (1.0 - 0.15 * step(0.46, max(slab.x, slab.y)));
    } else if (code == 3.0) {  // refinery yard: concrete with dark stains
        color = palette[3] * shade * (1.0 - 0.45 * smoothstep(0.55, 0.8, fbm(p, 25.0, 2)));
    } else if (code == 4.0) {  // dirt road
        color = palette[4] * (0.8 + 0.4 * fine);
    } else if (code == 5.0) {  // wheat
        color = palette[5] * shade * furrows(p, variant, 0.15) * (0.9 + 0.2 * medium);
    } else if (code == 6.0) {  // green crops
        color = palette[6] * shade * furrows(p, variant, 0.25) * (0.9 + 0.2 * medium);
    } else if (code == 7.0) {  // plowed earth
        color = palette[7] * shade * furrows(p, variant, 0.35);
    } else if (code == 8.0) {  // lavender
        color = palette[8] * shade * furrows(p, variant, 0.3);
    } else if (code == 9.0) {  // pasture
        color = mix(palette[9], palette[12], medium) * shade * (0.85 + 0.3 * fine);
    } else if (code == 10.0) {  // farmyard: packed earth
        color = palette[10] * (0.85 + 0.3 * fine);
    } else if (style == 1.0) {  // park grass
        color = mix(palette[0], palette[11], medium) * (0.85 + 0.3 * fine);
    } else if (style == 2.0) {  // scrub and gravel
        color = mix(palette[0], palette[11], large) * (0.8 + 0.4 * fine);
    } else {  // grass
        color = mix(palette[0], palette[11], medium) * (0.85 + 0.3 * fine);
    }
    return color;
}

// Natural grounds. `height`: 0 to 1 of the ground's highest point; `mark`: the landscape's own (grounds/).

// The nearest of scattered points (about one per `size` world units, looping along y): the distance to it, the way
// to it, and a number of its own.
float nearest(vec2 p, float size, out vec2 towards, out float id) {
    float period = max(floor(ground_loop / size + 0.5), 1.0);
    vec2 q = vec2(p.x / size, p.y * period / ground_loop);
    vec2 i = floor(q);
    vec2 f = fract(q);
    float best = 10.0;
    for (int y = -1; y <= 1; ++y) {
        for (int x = -1; x <= 1; ++x) {
            vec2 cell = i + vec2(x, y);
            vec2 key = vec2(cell.x, mod(cell.y, period));
            vec2 d = vec2(x, y) + vec2(hash(key), hash(key + 17.3)) * 0.8 + 0.1 - f;
            float distance = dot(d, d);
            if (distance < best) {
                best = distance;
                towards = d;
                id = hash(key + 3.1);
            }
        }
    }
    return sqrt(best);
}

vec3 planet(float height, float mark, float medium, float fine) {
    vec3 color = mix(palette[0], palette[1], clamp(height * 1.2 + 0.2 * (medium - 0.5), 0.0, 1.0));
    color = mix(color, palette[2], 0.5 * mark);  // craters' rims and the dust they threw out
    return color * (0.8 + 0.4 * fine);
}

vec3 island(vec2 p, float height, float flat_ground, float medium, float fine) {
    float h = height + 0.08 * (medium - 0.5);
    vec3 color = mix(palette[0], palette[1], smoothstep(0.08, 0.15, h));  // beach, grass
    vec3 trees = palette[2] * (0.6 + 0.8 * noise(p, 220.0));
    color = mix(color, trees, smoothstep(0.4, 0.5, h));
    color = mix(color, palette[3], max(smoothstep(0.75, 0.85, h), 0.7 * smoothstep(0.75, 0.55, flat_ground)));
    return color * (0.85 + 0.3 * fine);
}

vec3 desert(vec2 p, float height, float mark, float flat_ground, float medium, float fine) {
    vec3 sand = mix(palette[0], palette[1], clamp(height * 2.5, 0.0, 1.0));
    sand *= 1.0 - 0.07 * (0.5 + 0.5 * sin(p.y * 260.0 + 8.0 * medium));  // wind ripples
    vec3 rock = mix(palette[2], palette[3], step(0.5, fract(height * 12.0 + 0.3 * medium)));
    rock = mix(rock, palette[4], smoothstep(0.9, 0.97, height) * smoothstep(0.85, 0.95, flat_ground));
    vec3 grass = palette[5] * (0.8 + 0.4 * fine);
    vec3 color = mix(sand, grass, smoothstep(0.3, 0.45, mark) * (1.0 - smoothstep(0.7, 0.8, mark)));
    return mix(color, rock * (0.85 + 0.3 * fine), smoothstep(0.7, 0.8, mark));
}

// Under the canopy, each tree's round crown: bulging (the normal tilts away from its middle), in one of three
// greens, darker in the gaps between crowns.
vec3 forest(vec2 p, float mark, float medium, float fine, inout vec3 n) {
    vec2 towards;
    float id;
    float distance = nearest(p, 0.03, towards, id);
    vec3 green = id < 0.33 ? palette[0] : id < 0.66 ? palette[1] : palette[2];
    vec3 crowns = green * 1.15 * (0.75 + 0.5 * noise(p, 300.0)) * (1.0 - 0.45 * smoothstep(0.45, 0.8, distance));
    n = normalize(n + mark * 0.9 * vec3(-towards.x, 0.0, towards.y));
    vec3 clearing = mix(palette[3], palette[4], medium) * (0.85 + 0.3 * fine);
    return mix(clearing, crowns, mark);
}

vec3 canyon(float height, float mark, float flat_ground, float medium, float fine) {
    vec3 rock = palette[int(mod(floor(height * 16.0 + 0.8 * medium), 4.0))];  // the four bands
    rock = mix(rock, palette[4], smoothstep(0.75, 0.85, height) * smoothstep(0.85, 0.95, flat_ground));
    vec3 sand = mix(palette[5], palette[6], smoothstep(0.55, 0.7, medium));  // green patches
    return mix(rock, sand, step(0.25, mark)) * (0.85 + 0.3 * fine);
}

vec3 pack_ice(float mark, float flat_ground, float medium, float fine) {
    vec3 floe = palette[0] * (0.9 + 0.2 * medium) * (0.95 + 0.1 * fine);
    vec3 berg = mix(palette[1], palette[2], smoothstep(0.6, 0.9, flat_ground));
    return mix(floe, berg, mark);
}

vec3 volcano(vec2 p, float height, float world_height, float fine, out vec3 glow) {
    vec3 rock = mix(palette[0], palette[1], smoothstep(0.5, 0.7, height));  // ash on top
    // Glowing cracks near the lava.
    glow = palette[2] * smoothstep(0.025, 0.0, world_height) * smoothstep(0.05, 0.0, abs(noise(p, 35.0) - 0.5));
    return rock * (0.8 + 0.4 * fine);
}

vec3 swamp(vec2 p, float mark, float medium, float fine) {
    vec3 mud = palette[0] * (1.0 - 0.35 * smoothstep(0.45, 0.7, medium)) * (0.85 + 0.3 * fine);
    vec3 reeds = mix(palette[1], palette[2], noise(p, 350.0));
    return mix(mud, reeds, mark);
}

vec3 cloud_deck(float height, float flat_ground, float medium) {
    float lit = clamp(height + 0.35 * flat_ground * height + 0.15 * (medium - 0.5), 0.0, 1.0);  // lit tops
    return mix(palette[0], palette[1], lit);
}

// What's below height 0. Water: waves (looping along y), shallows lighter, foam at the coasts, the sun's glints.
// Lava: a glowing flow under a drifting crust. Gaps between clouds: the dark ground far below, a few town lights.
float looping(float k) {
    return 6.2831853 * max(1.0, floor(k * ground_loop / 6.2831853 + 0.5)) / ground_loop;
}

vec3 fluid_surface(vec2 p, float depth, float shadow) {
    float t = osg_FrameTime;
    if (fluid < 1.5) {
        vec2 slope = vec2(
            sin(p.x * 47.0 + p.y * looping(13.0) + t * 1.3) + 0.6 * sin(p.x * 89.0 - p.y * looping(61.0) + t * 2.1),
            cos(p.y * looping(53.0) - p.x * 17.0 - t * 1.1) + 0.6 * cos(p.y * looping(97.0) + p.x * 71.0 + t * 1.7)
        ) * 0.05;
        vec3 n = normalize(vec3(slope.x, -1.0, -slope.y));  // the waves: only for glints, the water itself is flat
        vec3 color = mix(fluid_colors[1], fluid_colors[0], smoothstep(0.0, 0.05, depth));  // shallow, deep
        color *= 0.92 + 0.16 * noise(p + vec2(t * 0.005, 0.0), 30.0);  // slow swells
        float foam = smoothstep(0.005, 0.0, depth) * smoothstep(0.4, 0.6, noise(p + vec2(0.0, t * 0.01), 140.0));
        color = mix(color, fluid_colors[2], foam * 0.7);
        vec3 half_way = normalize(normalize(sun) + EYE);
        float glint = pow(max(dot(n, half_way), 0.0), 150.0) * 0.9 * (1.0 - shadow);
        return color * tint * daylight(vec3(0.0, -1.0, 0.0), shadow, 1.0) + (sun_color * glint + sky_color * 0.08) * tint;
    }
    if (fluid < 2.5) {
        float crust = smoothstep(0.42, 0.66, fbm(p + vec2(0.0, -t * 0.012), 10.0, 3));
        vec3 hot = fluid_colors[0] * (1.05 + 0.15 * sin(t * 2.3 + p.x * 41.0 + p.y * 33.0));
        return mix(hot, fluid_colors[1], crust * smoothstep(0.0, 0.012, depth));  // brightest at the shores
    }
    vec2 towards;
    float id;
    float distance = nearest(p, 0.04, towards, id);
    vec3 light = id < 0.03 ? fluid_colors[1] : id < 0.06 ? fluid_colors[2] : vec3(0.0);
    return fluid_colors[0] + light * smoothstep(0.12, 0.05, distance);
}

void main() {
    vec2 p = ground_point();
    float cavity = v_data.r;
    float height = v_data.g;
    float depth = v_data.b;
    float mark = v_data.a;
    float world_height = -v_model.y;
    vec3 n = normalize(v_normal);  // model space: x right, -y towards the camera ("up" for the ground), z up the screen
    float flat_ground = clamp(-n.y, 0.0, 1.0);  // 1 facing the camera, 0 on a cliff

    float large = fbm(p, 3.0, 3);
    float medium = fbm(p, 14.0, 2);
    float fine = fbm(p, 60.0, 2);
    vec3 glow = vec3(0.0);
    float smooth_surface = 0.0;
    vec3 ground;
    if (style > 0.5 && style < 3.5) {
        ground = built_up(p, large, medium, fine, glow, smooth_surface);
    } else if (style == 4.0) {
        ground = planet(height, mark, medium, fine);
    } else if (style == 5.0) {
        ground = island(p, height, flat_ground, medium, fine);
    } else if (style == 6.0) {
        ground = desert(p, height, mark, flat_ground, medium, fine);
    } else if (style == 7.0) {
        ground = forest(p, mark, medium, fine, n);
    } else if (style == 8.0) {
        ground = canyon(height, mark, flat_ground, medium, fine);
    } else if (style == 9.0) {
        ground = pack_ice(mark, flat_ground, medium, fine);
        smooth_surface = 1.0;
    } else if (style == 10.0) {
        ground = volcano(p, height, world_height, fine, glow);
    } else if (style == 11.0) {
        ground = swamp(p, mark, medium, fine);
    } else if (style == 12.0) {
        ground = cloud_deck(height, flat_ground, medium);
        smooth_surface = 1.0;
    } else {
        ground = mountains(p, height, cavity, flat_ground, large, medium, fine, smooth_surface);
    }

    // Rough surfaces: fine noise bends the normal (less on smooth ones, like snow).
    float e = 0.004;
    float here = noise(p, 70.0);
    vec2 bump = 0.6 * vec2(noise(p + vec2(e, 0.0), 70.0) - here, noise(p + vec2(0.0, e), 70.0) - here) / e;
    float roughness = (style > 0.5 && style < 3.5 ? 0.005 : 0.012) * (1.0 - 0.7 * smooth_surface);
    vec3 bumped = normalize(n + vec3(-bump.x, 0.0, bump.y) * roughness);

    float shadow = in_shadow(p, world_height);
    vec3 lit = ground * tint * daylight(bumped, shadow, 1.0 - 0.6 * cavity) + glow;
    if (fluid > 0.5) {
        float under = smoothstep(-0.0015, 0.0015, depth);  // the shore, where the depth crosses 0
        if (under > 0.0) {
            lit = mix(lit, fluid_surface(p, max(depth, 0.0), shadow), under);
        }
    }
    fragment_color = vec4(hazy(lit), 1.0);
}
"""

PROP_SHADER = """
// v_data: red, green, blue, material (props/); v_wall: along the wall, up the wall, the prop's seed, unused
uniform vec3 window_lights[2];
uniform vec3 glass_color;  // unlit windows
uniform vec3 furnace_color;
const float OFFICE = 1.0;
const float HOMES = 2.0;
const float FURNACE = 3.0;
const float LIGHT = 4.0;
const float FOLIAGE = 5.0;
const float METAL = 6.0;
const float ROOFING = 7.0;

// How much of this pixel is a window pane: the part of each `size` cell from `low` to `high` (shares across and up
// the cell), with edges softened over a pixel, so small windows don't shimmer as the ground scrolls.
float window(vec2 at, vec2 size, vec2 low, vec2 high, vec2 pixel) {
    vec2 in_cell = fract(at / size);
    vec2 edge = max(pixel / size, 1e-4);  // a pixel, in cells
    vec2 inside = smoothstep(low - edge, low + edge, in_cell) * (1.0 - smoothstep(high - edge, high + edge, in_cell));
    return inside.x * inside.y;
}

void main() {
    vec2 p = ground_point();
    float height = -v_model.y;
    vec3 n = normalize(v_normal);
    float material = floor(v_data.a + 0.5);
    vec3 base = v_data.rgb;
    float seed = v_wall.z;
    float wall = 1.0 - abs(n.y);  // 1 on upright faces
    vec3 glow = vec3(0.0);
    vec2 pixel = fwidth(v_wall.xy);  // how much of the wall one pixel covers (out here: not in a branch)

    if ((material == OFFICE || material == HOMES) && wall > 0.5) {
        // A grid of windows: floors up the wall, bays along it.
        vec2 size = material == OFFICE ? vec2(0.022, 0.03) : vec2(0.026, 0.034);
        vec2 cell = floor(v_wall.xy / size);
        float pane = window(v_wall.xy, size, vec2(0.2, 0.3), vec2(0.8, 0.85), pixel);
        pane *= step(0.0, v_wall.y);  // not below the base
        float lit_share = mix(0.15, material == OFFICE ? 0.5 : 0.35, night()) * (0.6 + 0.8 * fract(seed * 7.13));
        float lit = step(hash(cell + seed * 131.0), lit_share);
        vec3 light = fract(seed * 3.7) < 0.6 ? window_lights[0] : window_lights[1];
        base = mix(base, glass_color, pane * (1.0 - lit));
        glow = light * pane * lit * (0.5 + 0.5 * night());
    } else if (material == FURNACE && wall > 0.5) {
        // Rows of glowing furnace windows, flickering slowly.
        vec2 size = vec2(0.035, 0.035);
        float pane = window(v_wall.xy, size, vec2(0.15, 0.35), vec2(0.85, 0.7), pixel);
        float lit = step(0.3, hash(floor(v_wall.xy / size) + seed * 57.0));
        glow = furnace_color * pane * lit * (0.8 + 0.2 * sin(v_wall.x * 90.0 + seed * 20.0));
    } else if (material == LIGHT) {
        fragment_color = vec4(base * 1.2, 1.0);  // flames and beacons shine whatever the light and haze
        return;
    } else if (material == ROOFING) {  // gravel and tar, in patches, with panel seams
        vec2 seam = abs(fract(p / 0.03 + seed * 5.0) - 0.5);
        base *= (0.85 + 0.25 * noise(p, 90.0) + 0.1 * noise(p, 400.0)) * (1.0 - 0.12 * step(0.47, max(seam.x, seam.y)));
    } else if (material == FOLIAGE) {
        base *= 0.65 + 0.7 * noise(p + vec2(height * 3.0, 0.0), 300.0);
        n = normalize(n + 0.35 * vec3(noise(p, 250.0) - 0.5, 0.0, noise(p + 7.0, 250.0) - 0.5));
    }

    vec3 lit = base * tint * daylight(n, in_shadow(p, height + 0.002), 0.8) + glow;
    if (material == METAL) {  // a soft sheen from the sun
        vec3 to_eye = normalize(-v_position);
        vec3 half_way = normalize(normalize(sun) + vec3(0.0, -1.0, 0.0));
        lit += tint * sun_color * 0.15 * pow(max(dot(n, half_way), 0.0), 20.0) * (1.0 - in_shadow(p, height + 0.002));
    }
    fragment_color = vec4(hazy(lit), 1.0);
}
"""

_shaders: dict[str, Shader] = {}


def _shader(name: str) -> Shader:
    """Compiled once, shared by every strip."""
    if name not in _shaders:
        common = COMMON % {"softness": repr(SHADOW_SOFTNESS)}
        body = GROUND_SHADER % {"palette": PALETTE_SIZE} if name == "ground" else PROP_SHADER
        _shaders[name] = Shader.make(Shader.SL_GLSL, VERTEX_SHADER, common + body)
    return _shaders[name]


def _vertex_format() -> GeomVertexFormat:
    array = GeomVertexArrayFormat()
    array.addColumn("vertex", 3, GeomEnums.NT_float32, GeomEnums.C_point)
    array.addColumn("normal", 3, GeomEnums.NT_float32, GeomEnums.C_normal)
    array.addColumn("color", 4, GeomEnums.NT_float32, GeomEnums.C_color)
    array.addColumn("texcoord", 4, GeomEnums.NT_float32, GeomEnums.C_texcoord)
    return GeomVertexFormat.registerFormat(GeomVertexFormat(array))


def _geometry(name: str, vertices: np.ndarray, triangles: np.ndarray) -> NodePath:
    """A mesh from vertices of 14 floats (position, normal, color, texture data) and triangle corner indices."""
    data = GeomVertexData(name, _vertex_format(), Geom.UH_static)
    data.uncleanSetNumRows(len(vertices))
    data.modifyArrayHandle(0).copyDataFrom(
        memoryview(np.ascontiguousarray(vertices, dtype=np.float32).reshape(-1)).cast("B")
    )
    primitive = GeomTriangles(Geom.UH_static)
    primitive.setIndexType(GeomEnums.NT_uint32)
    handle = primitive.modifyVertices()
    handle.uncleanSetNumRows(len(triangles))
    handle.modifyHandle().copyDataFrom(memoryview(np.ascontiguousarray(triangles, dtype=np.uint32)).cast("B"))
    geom = Geom(data)
    geom.addPrimitive(primitive)
    node = GeomNode(name)
    node.addGeom(geom)
    return NodePath(node)


def maps(relief: Relief, layout: Layout | None) -> dict[str, Texture]:
    """The textures both shaders read over the whole loop: the shadow heights and, for built-up grounds, the
    surface map.
    """
    shadow = Texture("shadow_heights")
    heights = np.ascontiguousarray(relief.shadow_heights, dtype=np.float32)
    shadow.setup2dTexture(heights.shape[1], heights.shape[0], Texture.T_float, Texture.F_r32)
    shadow.setRamImage(heights.tobytes())  # the first row is at v = 0: the loop's start
    shadow.setWrapU(SamplerState.WM_clamp)
    shadow.setWrapV(SamplerState.WM_repeat)
    result = {"shadow_map": shadow}
    if layout is not None:
        surface = Texture("surface")
        texels = np.zeros((*layout.surface.shape, 4), dtype=np.uint8)
        # RGBA textures are kept as blue, green, red, alpha: red is the surface, green the lot's number.
        texels[..., 2] = layout.surface
        texels[..., 1] = layout.variant
        texels[..., 3] = 255
        surface.setup2dTexture(texels.shape[1], texels.shape[0], Texture.T_unsigned_byte, Texture.F_rgba8)
        surface.setRamImage(texels.tobytes())
        surface.setMagfilter(SamplerState.FT_nearest)
        surface.setMinfilter(SamplerState.FT_nearest)
        surface.setWrapU(SamplerState.WM_clamp)
        surface.setWrapV(SamplerState.WM_repeat)
        result["surface_map"] = surface
    return result


def palette(params: SceneryParams) -> list[tuple[float, float, float]]:
    """The ground painter's colors, in the slots it reads them from."""
    colors = [(0.0, 0.0, 0.0)] * PALETTE_SIZE
    ground = params.ground
    if ground is None:
        return colors
    if params.settlement is not None and not STYLE_COLORS[ground.style]:  # a built-up ground
        for name, color in params.settlement.colors.items():
            colors[SURFACE_SLOTS.index(name)] = color
    else:
        for slot, name in enumerate(STYLE_COLORS[ground.style]):
            colors[slot] = ground.colors[name]
    return colors


def _colors(name: str, colors: list[tuple[float, float, float]]) -> PTA_LVecBase3f:
    array = PTA_LVecBase3f.emptyArray(len(colors))
    for index, color in enumerate(colors):
        array[index] = LVecBase3f(*color)
    return array


def ground_inputs(
    path: NodePath, params: SceneryParams, textures: dict[str, Texture], loop: float, width: float
) -> None:
    """What both shaders need, set on the node above the ground's strips."""
    along_x, along_y = SUN_ALONG
    # Ground directions (x right, y down the screen, z towards the camera) -> model space (x, -z, -y).
    path.setShaderInput("sun", (along_x, -SUN_RISE, -along_y))
    path.setShaderInput("sun_color", params.light.sun)
    path.setShaderInput("sky_color", params.light.sky)
    path.setShaderInput("haze_near", params.haze.near)
    path.setShaderInput("haze_range", params.haze.range)
    path.setShaderInput("ground_loop", loop)
    path.setShaderInput("ground_width", width)
    style = params.ground.style if params.ground else ""
    path.setShaderInput("style", STYLES.get(style, 0.0))
    path.setShaderInput("palette", _colors("palette", palette(params)))
    fluid = params.fluid
    path.setShaderInput("fluid", FLUIDS[fluid.kind] if fluid else 0.0)
    fluid_colors = [(0.0, 0.0, 0.0)] * 3
    if fluid is not None:
        for slot, name in enumerate(FLUID_COLORS[fluid.kind]):
            fluid_colors[slot] = fluid.colors[name]
    path.setShaderInput("fluid_colors", _colors("fluid_colors", fluid_colors))
    props = params.props
    path.setShaderInput("window_lights", _colors("window_lights", list(props.window_lights)))
    path.setShaderInput("glass_color", props.glass)
    path.setShaderInput("furnace_color", props.furnace)
    path.setShaderInput("shadow_map", textures["shadow_map"])
    path.setShaderInput("surface_map", textures.get("surface_map", textures["shadow_map"]))


def relief_chunk_model(relief: Relief, first_row: int, rows: int, max_height: float) -> NodePath:
    """Rows `first_row` to `first_row + rows` of a relief (one more, from the next strip, to close the gap), as a
    mesh. The node's origin is the top-left corner, on the base layer: x right, z up the
    screen, heights towards the camera (-y).
    """
    picked = np.arange(first_row, first_row + rows + 1) % relief.rows
    heights = relief.heights[picked]
    normals = relief.normals[picked]
    lines, columns = heights.shape
    vertices = np.zeros((lines, columns, 14), dtype=np.float32)
    vertices[..., 0] = (np.arange(columns) * relief.step_x)[None, :]
    vertices[..., 1] = -heights
    vertices[..., 2] = (-np.arange(lines) * relief.step_y)[:, None]
    # Relief normals: x right, y down the rows, z towards the camera -> model: x, -z (towards the camera is -y), -y.
    vertices[..., 3] = normals[..., 0]
    vertices[..., 4] = -normals[..., 2]
    vertices[..., 5] = -normals[..., 1]
    vertices[..., 6] = relief.cavity[picked]
    vertices[..., 7] = heights / max_height
    vertices[..., 8] = relief.depth[picked]
    vertices[..., 9] = relief.marks[picked]
    index = np.arange(lines * columns, dtype=np.uint32).reshape(lines, columns)
    a, b = index[:-1, :-1], index[:-1, 1:]
    c, d = index[1:, :-1], index[1:, 1:]
    triangles = np.stack([a, c, b, b, c, d], axis=-1).reshape(-1)  # two per square, facing the camera
    path = _geometry("relief", vertices.reshape(-1, 14), triangles)
    path.setShader(_shader("ground"), 20)
    return path


def props_model(vertices: np.ndarray, triangles: np.ndarray) -> NodePath:
    """A strip's props (props.strip_arrays)."""
    path = _geometry("props", vertices, triangles)
    path.setShader(_shader("props"), 20)
    path.setTwoSided(True)
    return path
