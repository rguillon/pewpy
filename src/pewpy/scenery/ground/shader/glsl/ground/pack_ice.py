"""The pack ice's painter."""

GLSL = """
vec3 pack_ice(float mark, float flat_ground, float medium, float fine) {
    vec3 floe = palette[0] * (0.9 + 0.2 * medium) * (0.95 + 0.1 * fine);
    vec3 berg = mix(palette[1], palette[2], smoothstep(0.6, 0.9, flat_ground));
    return mix(floe, berg, mark);
}

"""
