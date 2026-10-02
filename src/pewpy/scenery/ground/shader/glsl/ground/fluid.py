"""What's below height 0: water, lava, or gaps between clouds."""

GLSL = """
// What's below height 0. Water: waves (looping along y), shallows lighter, foam at the coasts, the sun's glints.
// Lava: a glowing flow under a drifting crust. Gaps between clouds: the dark ground far below, a few town lights.
float looping(float k) {
    return 6.2831853 * max(1.0, floor(k * ground_loop / 6.2831853 + 0.5)) / ground_loop;
}

vec3 fluid_surface(vec2 p, float depth, float shadow) {
    float t = osg_FrameTime;
    if (fluid < 1.5) {
        vec2 slope = vec2(
            sin(p.x * 47.0 + p.y * looping(13.0) + t * 1.3) + 0.6 * sin(p.x * 89.0 - p.y * looping(61.0) + t * 2.1),
            cos(p.y * looping(53.0) - p.x * 17.0 - t * 1.1) + 0.6 * cos(p.y * looping(97.0) + p.x * 71.0 + t * 1.7)
        ) * 0.05;
        vec3 n = normalize(vec3(slope.x, -1.0, -slope.y));  // the waves: only for glints, the water itself is flat
        vec3 color = mix(fluid_colors[1], fluid_colors[0], smoothstep(0.0, 0.05, depth));  // shallow, deep
        color *= 0.92 + 0.16 * noise(p + vec2(t * 0.005, 0.0), 30.0);  // slow swells
        float foam = smoothstep(0.005, 0.0, depth) * smoothstep(0.4, 0.6, noise(p + vec2(0.0, t * 0.01), 140.0));
        color = mix(color, fluid_colors[2], foam * 0.7);
        vec3 half_way = normalize(normalize(sun) + EYE);
        float glint = pow(max(dot(n, half_way), 0.0), 150.0) * 0.9 * (1.0 - shadow);
        return color * tint * daylight(vec3(0.0, -1.0, 0.0), shadow, 1.0) + (sun_color * glint + sky_color * 0.08) * tint;
    }
    if (fluid < 2.5) {
        float crust = smoothstep(0.42, 0.66, fbm(p + vec2(0.0, -t * 0.012), 10.0, 3));
        vec3 hot = fluid_colors[0] * (1.05 + 0.15 * sin(t * 2.3 + p.x * 41.0 + p.y * 33.0));
        return mix(hot, fluid_colors[1], crust * smoothstep(0.0, 0.012, depth));  // brightest at the shores
    }
    vec2 towards;
    float id;
    float distance = nearest(p, 0.04, towards, id);
    vec3 light = id < 0.03 ? fluid_colors[1] : id < 0.06 ? fluid_colors[2] : vec3(0.0);
    return fluid_colors[0] + light * smoothstep(0.12, 0.05, distance);
}

"""
