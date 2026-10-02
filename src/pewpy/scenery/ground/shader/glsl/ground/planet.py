"""The planet's painter."""

GLSL = """
vec3 planet(float height, float mark, float medium, float fine) {
    vec3 color = mix(palette[0], palette[1], clamp(height * 1.2 + 0.2 * (medium - 0.5), 0.0, 1.0));
    color = mix(color, palette[2], 0.5 * mark);  // craters' rims and the dust they threw out
    return color * (0.8 + 0.4 * fine);
}

"""
