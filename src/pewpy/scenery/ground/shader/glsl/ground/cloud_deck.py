"""The cloud deck's painter."""

GLSL = """
vec3 cloud_deck(float height, float flat_ground, float medium) {
    float lit = clamp(height + 0.35 * flat_ground * height + 0.15 * (medium - 0.5), 0.0, 1.0);  // lit tops
    return mix(palette[0], palette[1], lit);
}

"""
