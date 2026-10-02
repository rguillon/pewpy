"""Scattered points, for the natural grounds' painters."""

GLSL = """
// Natural grounds. `height`: 0 to 1 of the ground's highest point; `mark`: the landscape's own (grounds/).

// The nearest of scattered points (about one per `size` world units, looping along y): the distance to it, the way
// to it, and a number of its own.
float nearest(vec2 p, float size, out vec2 towards, out float id) {
    float period = max(floor(ground_loop / size + 0.5), 1.0);
    vec2 q = vec2(p.x / size, p.y * period / ground_loop);
    vec2 i = floor(q);
    vec2 f = fract(q);
    float best = 10.0;
    for (int y = -1; y <= 1; ++y) {
        for (int x = -1; x <= 1; ++x) {
            vec2 cell = i + vec2(x, y);
            vec2 key = vec2(cell.x, mod(cell.y, period));
            vec2 d = vec2(x, y) + vec2(hash(key), hash(key + 17.3)) * 0.8 + 0.1 - f;
            float distance = dot(d, d);
            if (distance < best) {
                best = distance;
                towards = d;
                id = hash(key + 3.1);
            }
        }
    }
    return sqrt(best);
}

"""
