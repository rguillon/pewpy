"""The forest's painter."""

GLSL = """
// Under the canopy, each tree's round crown: bulging (the normal tilts away from its middle), in one of three
// greens, darker in the gaps between crowns.
vec3 forest(vec2 p, float mark, float medium, float fine, inout vec3 n) {
    vec2 towards;
    float id;
    float distance = nearest(p, 0.03, towards, id);
    vec3 green = id < 0.33 ? palette[0] : id < 0.66 ? palette[1] : palette[2];
    vec3 crowns = green * 1.15 * (0.75 + 0.5 * noise(p, 300.0)) * (1.0 - 0.45 * smoothstep(0.45, 0.8, distance));
    n = normalize(n + mark * 0.9 * vec3(-towards.x, 0.0, towards.y));
    vec3 clearing = mix(palette[3], palette[4], medium) * (0.85 + 0.3 * fine);
    return mix(clearing, crowns, mark);
}

"""
