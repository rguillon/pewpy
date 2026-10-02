"""The built-up grounds' painter (city, refinery, farmland): from the layout's surface map."""

GLSL = """
// Rows of a crop: stripes one way or the other (by the field's number), `strength` deep.
float furrows(vec2 p, float variant, float strength) {
    float along = mod(variant, 2.0) < 1.0 ? p.x : p.y;
    return 1.0 - strength + strength * (0.5 + 0.5 * sin(along * 6.2831853 / 0.012));
}

vec3 built_up(vec2 p, float large, float medium, float fine, out vec3 glow, out float smooth_surface) {
    vec4 texel = texture(surface_map, vec2(p.x / ground_width, p.y / ground_loop));
    float code = floor(texel.r * 255.0 + 0.5);
    float variant = floor(texel.g * 255.0 + 0.5);
    float shade = 0.9 + 0.2 * fract(variant * 0.618);  // each lot or field a little different
    glow = vec3(0.0);
    smooth_surface = 0.0;
    vec3 color;
    if (code == 1.0) {  // street: asphalt; at night, pools of amber lamp light at intervals
        color = palette[1] * (0.85 + 0.3 * fine);
        vec2 cell = floor(p / 0.1);
        float lamp = step(0.4, hash(cell)) * smoothstep(0.02, 0.0, length(fract(p / 0.1) - 0.5) * 0.1);
        glow = palette[13] * lamp * night() * 0.6;
    } else if (code == 2.0) {  // pavement: concrete slabs
        vec2 slab = abs(fract(p / 0.02) - 0.5);
        color = palette[2] * (0.9 + 0.2 * fine) * (1.0 - 0.15 * step(0.46, max(slab.x, slab.y)));
    } else if (code == 3.0) {  // refinery yard: concrete with dark stains
        color = palette[3] * shade * (1.0 - 0.45 * smoothstep(0.55, 0.8, fbm(p, 25.0, 2)));
    } else if (code == 4.0) {  // dirt road
        color = palette[4] * (0.8 + 0.4 * fine);
    } else if (code == 5.0) {  // wheat
        color = palette[5] * shade * furrows(p, variant, 0.15) * (0.9 + 0.2 * medium);
    } else if (code == 6.0) {  // green crops
        color = palette[6] * shade * furrows(p, variant, 0.25) * (0.9 + 0.2 * medium);
    } else if (code == 7.0) {  // plowed earth
        color = palette[7] * shade * furrows(p, variant, 0.35);
    } else if (code == 8.0) {  // lavender
        color = palette[8] * shade * furrows(p, variant, 0.3);
    } else if (code == 9.0) {  // pasture
        color = mix(palette[9], palette[12], medium) * shade * (0.85 + 0.3 * fine);
    } else if (code == 10.0) {  // farmyard: packed earth
        color = palette[10] * (0.85 + 0.3 * fine);
    } else if (style == 1.0) {  // park grass
        color = mix(palette[0], palette[11], medium) * (0.85 + 0.3 * fine);
    } else if (style == 2.0) {  // scrub and gravel
        color = mix(palette[0], palette[11], large) * (0.8 + 0.4 * fine);
    } else {  // grass
        color = mix(palette[0], palette[11], medium) * (0.85 + 0.3 * fine);
    }
    return color;
}

"""
