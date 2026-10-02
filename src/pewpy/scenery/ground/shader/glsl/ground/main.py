"""The ground shader's main: picks the painter by `style`, then lights and hazes the ground."""

GLSL = """
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
    } else if (style == 13.0) {
        ground = geysers(p, height, mark, flat_ground, medium, fine, smooth_surface);
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
