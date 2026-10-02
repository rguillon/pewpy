"""The geyser basin's painter."""

GLSL = """
// Marks: the mats up to 0.5 (at the water's edge), the terraced mounds from 0.75 (dry) to 1 (water on their ledges).
vec3 geysers(vec2 p, float height, float mark, float flat_ground, float medium, float fine, out float smooth_surface) {
    // The crust: pale sinter, mottled, with a few cracks.
    float cracks = smoothstep(0.02, 0.0, abs(noise(p, 30.0) - 0.5)) * smoothstep(0.45, 0.65, medium);
    vec3 crust = mix(palette[0], palette[1], medium) * (0.93 + 0.14 * fine) * (1.0 - 0.25 * cracks);
    // The mats round the pools: rust on the outside, then orange, then pale yellow at the water's edge.
    float m = mark + 0.06 * (medium - 0.5) + 0.04 * (fine - 0.5);
    vec3 mat = mix(palette[4], palette[3], smoothstep(0.12, 0.25, m));
    mat = mix(mat, palette[2], smoothstep(0.35, 0.45, m)) * (0.88 + 0.24 * noise(p, 150.0));
    float mats = smoothstep(0.015, 0.09, m) * smoothstep(0.62, 0.55, mark);
    // The terraces: bright sinter streaked orange down the risers, the ledges creamy under clear shallow water.
    float streaks = smoothstep(0.45, 0.7, noise(vec2(p.x * 3.0, p.y), 90.0));
    vec3 sinter = palette[1] * 1.3 * (0.95 + 0.1 * fine);
    sinter = mix(sinter, palette[3], smoothstep(0.95, 0.75, flat_ground) * (0.2 + 0.5 * streaks));
    vec3 ledges = mix(sinter, palette[7] * (0.92 + 0.16 * medium), smoothstep(0.8, 0.95, mark));
    float terraces = smoothstep(0.6, 0.7, mark);
    vec3 color = mix(mix(crust, mat, mats), ledges, terraces);
    smooth_surface = 0.7 * (1.0 - mats) * (1.0 - 0.5 * terraces);
    // The ridges: dark pines, bare rock where steep.
    vec3 pines = palette[5] * (0.55 + 0.9 * noise(p, 260.0));
    vec3 wood = mix(palette[6] * (0.8 + 0.4 * fine), pines, smoothstep(0.45, 0.75, flat_ground));
    float ridge = smoothstep(0.1, 0.18, height + 0.06 * (medium - 0.5)) * (1.0 - terraces);
    smooth_surface *= 1.0 - ridge;
    return mix(color, wood, ridge);
}

"""
