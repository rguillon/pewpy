"""The savanna's painter: golden grass, streaked and patchy, greener in places, sandy riverbeds, grey rocks."""

GLSL = """
// Marks: 0 grass, 0.5 the riverbed's sand, 1 rock.
vec3 savanna(vec2 p, float mark, float flat_ground, float large, float medium, float fine) {
    vec3 grass = mix(palette[0], palette[1], smoothstep(0.35, 0.65, medium));  // dry and golden grass
    grass = mix(grass, palette[2], 0.7 * smoothstep(0.55, 0.75, large));  // greener where it's wetter
    grass *= (0.85 + 0.25 * noise(vec2(p.x * 3.0, p.y), 160.0)) * (0.92 + 0.16 * fine);  // tussocks, in the wind
    vec3 sand = palette[3] * (0.9 + 0.2 * fine) * (0.95 + 0.1 * noise(vec2(p.x, p.y * 4.0), 80.0));
    vec3 rock = palette[4] * (0.8 + 0.4 * fine) * (0.85 + 0.3 * smoothstep(0.4, 0.9, flat_ground));
    vec3 color = mix(grass, sand, smoothstep(0.3, 0.45, mark) * smoothstep(0.7, 0.55, mark));
    return mix(color, rock, smoothstep(0.75, 0.9, mark));
}

"""
