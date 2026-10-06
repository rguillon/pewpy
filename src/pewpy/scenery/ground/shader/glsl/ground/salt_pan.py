"""The salt pan's painter: a white crust cracked into plates with raised edges, wet and darker by the brine."""

GLSL = """
// How far a point is from the edge between two plates (about one per `size` world units, looping along y), and
// a number of its plate's own.
float plates(vec2 p, float size, out float id) {
    float period = max(floor(ground_loop / size + 0.5), 1.0);
    vec2 q = vec2(p.x / size, p.y * period / ground_loop);
    vec2 i = floor(q);
    vec2 f = fract(q);
    float first = 10.0;
    float second = 10.0;
    for (int y = -1; y <= 1; ++y) {
        for (int x = -1; x <= 1; ++x) {
            vec2 cell = i + vec2(x, y);
            vec2 key = vec2(cell.x, mod(cell.y, period));
            float distance = length(vec2(x, y) + vec2(hash(key), hash(key + 17.3)) * 0.8 + 0.1 - f);
            if (distance < first) {
                second = first;
                first = distance;
                id = hash(key + 3.1);
            } else if (distance < second) {
                second = distance;
            }
        }
    }
    return second - first;
}

// Marks: how far from the brine (0 at its shore, 1 well away).
vec3 salt_pan(vec2 p, float mark, float medium, float fine, out float smooth_surface) {
    float id;
    float edge = plates(p, 0.11, id);
    vec3 crust = mix(palette[0], palette[1], 0.6 * id + 0.4 * medium) * (0.95 + 0.1 * fine);
    float ridge = smoothstep(0.2, 0.05, edge);
    vec3 color = mix(mix(crust, palette[2], ridge), palette[3], smoothstep(0.04, 0.0, edge));
    smooth_surface = 0.8 * (1.0 - ridge);
    return mix(palette[4] * (0.9 + 0.2 * fine), color, smoothstep(0.0, 0.4, mark));
}

"""
