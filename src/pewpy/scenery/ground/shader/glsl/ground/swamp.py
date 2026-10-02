"""The swamp's painter."""

GLSL = """
vec3 swamp(vec2 p, float mark, float medium, float fine) {
    vec3 mud = palette[0] * (1.0 - 0.35 * smoothstep(0.45, 0.7, medium)) * (0.85 + 0.3 * fine);
    vec3 reeds = mix(palette[1], palette[2], noise(p, 350.0));
    return mix(mud, reeds, mark);
}

"""
