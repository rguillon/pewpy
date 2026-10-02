"""The volcano's painter."""

GLSL = """
vec3 volcano(vec2 p, float height, float world_height, float fine, out vec3 glow) {
    vec3 rock = mix(palette[0], palette[1], smoothstep(0.5, 0.7, height));  // ash on top
    // Glowing cracks near the lava.
    glow = palette[2] * smoothstep(0.025, 0.0, world_height) * smoothstep(0.05, 0.0, abs(noise(p, 35.0) - 0.5));
    return rock * (0.8 + 0.4 * fine);
}

"""
