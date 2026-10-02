"""The canyon's painter."""

GLSL = """
vec3 canyon(float height, float mark, float flat_ground, float medium, float fine) {
    vec3 rock = palette[int(mod(floor(height * 16.0 + 0.8 * medium), 4.0))];  // the four bands
    rock = mix(rock, palette[4], smoothstep(0.75, 0.85, height) * smoothstep(0.85, 0.95, flat_ground));
    vec3 sand = mix(palette[5], palette[6], smoothstep(0.55, 0.7, medium));  // green patches
    return mix(rock, sand, step(0.25, mark)) * (0.85 + 0.3 * fine);
}

"""
