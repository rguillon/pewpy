"""The mountains' painter (natural grounds without a style of their own): rock with strata, scree, snow, meadows, pines."""

GLSL = """
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

"""
