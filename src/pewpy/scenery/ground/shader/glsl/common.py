"""What both fragment programs start with: inputs, noise, shadows, light, haze."""

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
