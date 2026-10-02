"""What the ground shader reads besides the common inputs."""

GLSL = """
uniform float style;  // what the ground is (STYLES)
uniform float fluid;  // what's below height 0: 0 nothing, 1 water, 2 lava, 3 gaps in clouds (FLUIDS)
uniform vec3 palette[%(palette)s];  // the painter's colors (STYLE_COLORS, SURFACE_SLOTS)
uniform vec3 fluid_colors[3];  // FLUID_COLORS
uniform float osg_FrameTime;
uniform sampler2D surface_map;  // built-up grounds: what covers each spot (settlement.py Surface) and its lot's number

// v_data: cavity, height (0 to 1 of the highest), depth under the fluid (world units), the landscape's mark

"""
