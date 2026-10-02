"""The desert's painter."""

GLSL = """
vec3 desert(vec2 p, float height, float mark, float flat_ground, float medium, float fine) {
    vec3 sand = mix(palette[0], palette[1], clamp(height * 2.5, 0.0, 1.0));
    sand *= 1.0 - 0.07 * (0.5 + 0.5 * sin(p.y * 260.0 + 8.0 * medium));  // wind ripples
    vec3 rock = mix(palette[2], palette[3], step(0.5, fract(height * 12.0 + 0.3 * medium)));
    rock = mix(rock, palette[4], smoothstep(0.9, 0.97, height) * smoothstep(0.85, 0.95, flat_ground));
    vec3 grass = palette[5] * (0.8 + 0.4 * fine);
    vec3 color = mix(sand, grass, smoothstep(0.3, 0.45, mark) * (1.0 - smoothstep(0.7, 0.8, mark)));
    return mix(color, rock * (0.85 + 0.3 * fine), smoothstep(0.7, 0.8, mark));
}

"""
