"""The props' fragment program (after the common part): painted from each face's material (props/)."""

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
