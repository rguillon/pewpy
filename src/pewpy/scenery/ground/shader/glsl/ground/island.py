"""The ocean's islands' painter."""

GLSL = """
vec3 island(vec2 p, float height, float flat_ground, float medium, float fine) {
    float h = height + 0.08 * (medium - 0.5);
    vec3 color = mix(palette[0], palette[1], smoothstep(0.08, 0.15, h));  // beach, grass
    vec3 trees = palette[2] * (0.6 + 0.8 * noise(p, 220.0));
    color = mix(color, trees, smoothstep(0.4, 0.5, h));
    color = mix(color, palette[3], max(smoothstep(0.75, 0.85, h), 0.7 * smoothstep(0.75, 0.55, flat_ground)));
    return color * (0.85 + 0.3 * fine);
}

"""
