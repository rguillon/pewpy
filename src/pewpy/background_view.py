"""Drawing the backgrounds of background.py with Panda3D."""

from panda3d.core import Lens, NodePath, Point2, Point3, Vec3

from pewpy import background, ground_look, models
from pewpy.background import Area, Scenery
from pewpy.terrain import BIOMES, Terrain

AREA_MARGIN = 0.05  # world units beyond the screen edges, so nothing pops in at the edges
# Space levels pick one of each by their background seed (Scenery.variant). All dim and muted.
NEBULA_PALETTES: tuple[tuple[models.Color, ...], ...] = (
    ((0.1, 0.04, 0.14, 1), (0.03, 0.08, 0.12, 1), (0.06, 0.05, 0.14, 1)),  # purple and teal
    ((0.14, 0.05, 0.03, 1), (0.12, 0.08, 0.02, 1), (0.08, 0.03, 0.06, 1)),  # ember
    ((0.03, 0.1, 0.06, 1), (0.02, 0.07, 0.1, 1), (0.05, 0.09, 0.04, 1)),  # green
    ((0.03, 0.05, 0.14, 1), (0.02, 0.09, 0.13, 1), (0.07, 0.07, 0.12, 1)),  # deep blue
)
PLANET_PALETTES: tuple[tuple[models.Color, ...], ...] = (
    models.PLANET_COLORS,  # blue-violet
    ((0.25, 0.15, 0.1, 1), (0.3, 0.2, 0.12, 1), (0.22, 0.12, 0.1, 1)),  # rusty
    ((0.1, 0.2, 0.18, 1), (0.14, 0.22, 0.16, 1), (0.08, 0.16, 0.2, 1)),  # sea green
)
# See-through clouds over the grounds: a pale grey-blue, mixed with the air's color; each one more or less opaque.
MIST_COLOR: tuple[float, float, float] = (0.62, 0.65, 0.72)
MIST_AIR = 0.35
MIST_NIGHT = 0.55  # how bright clouds stay when the ground goes dark
MIST_OPACITY = (0.14, 0.34)
# Time of day (Level.time_of_day): (tint of the ground, tint of its haze and sky).
TIMES_OF_DAY: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]] = {
    "day": ((1.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    "dusk": ((1.0, 0.78, 0.66), (1.2, 0.8, 0.7)),
    "night": ((0.42, 0.48, 0.68), (0.35, 0.4, 0.6)),
}
# The ground is big and right behind the action: less shine than the ships (shader inputs, see lighting.py).
GROUND_LOOK = {"specular": 0.15, "reflectivity": 0.05, "bevel_strength": 0.5}
CITY_LOOK = {"specular": 0.35, "reflectivity": 0.12, "bevel_strength": 0.4}  # a bit of glass and metal
LOOKS = {  # by Biome.look; the water has its own, in the shader
    "ground": GROUND_LOOK,
    "city": CITY_LOOK,
    "matte": {"specular": 0.06, "reflectivity": 0.02, "bevel_strength": 0.4},  # sand, rock, fields, clouds
    "ice": {"specular": 0.5, "reflectivity": 0.15, "bevel_strength": 0.5},
}


class CameraView:
    """How much of each background layer the camera sees (implements background.View)."""

    def __init__(self, camera: NodePath, lens: Lens, render: NodePath) -> None:
        self.camera = camera
        self.lens = lens
        self.render = render

    def area(self, depth: float) -> Area:
        xs, zs = [], []
        for corner in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            near, far = Point3(), Point3()
            self.lens.extrude(Point2(*corner), near, far)
            near = self.render.getRelativePoint(self.camera, near)
            far = self.render.getRelativePoint(self.camera, far)
            point = near + (far - near) * ((depth - near.y) / (far.y - near.y))  # where the ray meets the layer
            xs.append(point.x)
            zs.append(point.z)
        margin = AREA_MARGIN
        return Area(min(xs) - margin, max(xs) + margin, min(zs) - margin, max(zs) + margin)

    def parallax(self, depth: float) -> float:
        return self._screen_speed(depth) / self._screen_speed(0.0)

    def _screen_speed(self, depth: float) -> float:
        """Screen distance covered by a small step down the screen, in the middle of a layer."""
        top, bottom = Point2(), Point2()
        self.lens.project(self.camera.getRelativePoint(self.render, Point3(0, depth, 0)), top)
        self.lens.project(self.camera.getRelativePoint(self.render, Point3(0, depth, -0.01)), bottom)
        return top.y - bottom.y


class BackgroundView:
    """Nodes for one Scenery, under their own root so switching levels removes them all at once."""

    def __init__(self, scenery: Scenery, render: NodePath, time_of_day: str = "day") -> None:
        self.scenery = scenery
        self.root = render.attachNewNode(f"background_{scenery.kind}")
        tint, air = TIMES_OF_DAY[time_of_day]
        self.mist_color: tuple[float, float, float] = MIST_COLOR
        if scenery.terrain:
            red, green, blue, amount = BIOMES[scenery.terrain.biome].haze
            haze = (red * air[0], green * air[1], blue * air[2], amount)
            self.root.setShaderInput("haze", haze)  # the air, far away
            self.root.setShaderInput("tint", tint)
            # Clouds: pale, in the air's color, lit like the ground but dimming less at night (the lights below
            # still catch them).
            red, green, blue = (
                (base * (MIST_NIGHT + (1 - MIST_NIGHT) * light)) * (1 - MIST_AIR) + far * MIST_AIR
                for base, light, far in zip(MIST_COLOR, tint, haze[:3], strict=True)
            )
            self.mist_color = (red, green, blue)
        self.star_nodes = [self._star_layer(layer) for layer in scenery.starfield.layers] if scenery.starfield else []
        self.layer_nodes = [[self._drifter(layer, drifter) for drifter in layer.drifters] for layer in scenery.layers]
        self.ground_nodes = self._ground(scenery.terrain) if scenery.terrain else []
        self.sync()

    def sync(self) -> None:
        if self.scenery.starfield:
            for layer, node in zip(self.scenery.starfield.layers, self.star_nodes, strict=True):
                node.setPos(0, background.STAR_DEPTH, -layer.offset)
        for layer, nodes in zip(self.scenery.layers, self.layer_nodes, strict=True):
            for drifter, node in zip(layer.drifters, nodes, strict=True):
                node.setPos(drifter.x, layer.depth, drifter.y)
                node.setHpr(*drifter.angle)
        terrain = self.scenery.terrain
        if terrain:
            for chunk, node in enumerate(self.ground_nodes):
                node.setPos(terrain.left, terrain.depth, terrain.chunk_top(chunk))

    def destroy(self) -> None:
        self.root.removeNode()

    def _star_layer(self, layer: background.StarLayer) -> NodePath:
        """One mesh with every star of the layer, twice: the second copy sits just above the first."""
        mesh = models.MeshBuilder()
        half = layer.size / 2
        color = (layer.brightness, layer.brightness, layer.brightness, 1.0)
        for copy in (0.0, layer.area.height):
            for x, y in layer.stars:
                left, right, bottom, top = x - half, x + half, y + copy - half, y + copy + half
                a, b, c, d = Vec3(left, 0, bottom), Vec3(right, 0, bottom), Vec3(right, 0, top), Vec3(left, 0, top)
                mesh.quad(a, b, c, d, color, Vec3(x, 1, y + copy))  # facing the camera (-Y)
        node = self.root.attachNewNode(mesh.build("stars"))
        node.setLightOff()  # stars glow on their own
        node.setShaderOff()
        # Stars are infinitely far: drawn first and leaving no depth, so everything else covers them.
        node.setBin("background", 0)
        node.setDepthWrite(False)
        return node

    def _drifter(self, layer: background.DriftLayer, drifter: background.Drifter) -> NodePath:
        if layer.kind == "mist":
            model = models.mist_model(drifter.shape)
            opacity = MIST_OPACITY[0] + (MIST_OPACITY[1] - MIST_OPACITY[0]) * (drifter.shape % 10) / 9
            model.setColor(*self.mist_color, opacity)
        elif layer.kind == "cloud":
            nebula = NEBULA_PALETTES[self.scenery.variant % len(NEBULA_PALETTES)]
            model = models.cloud_model(nebula[drifter.shape % len(nebula)], seed=drifter.shape)
        elif layer.kind == "planet":
            palette = PLANET_PALETTES[self.scenery.variant % len(PLANET_PALETTES)]
            model = models.distant_planet_model(palette, seed=self.scenery.variant)
        else:
            model = models.rock_model(drifter.shape)
        model.reparentTo(self.root)
        model.setScale(drifter.size)
        return model

    def _ground(self, terrain: Terrain) -> list[NodePath]:
        nodes = []
        for chunk in range(terrain.chunks):
            rows = terrain.chunk_rows(chunk)
            first = chunk * terrain.chunk_rows_count
            above = terrain.heights[first - 1]  # row -1 is the loop's last row
            below = terrain.heights[(first + len(rows)) % terrain.rows]
            shallows = terrain.chunk_shallows(chunk) if terrain.water else None
            node = ground_look.ground_chunk_model(
                terrain.biome,
                rows,
                terrain.chunk_kinds(chunk),
                terrain.voxel,
                above,
                below,
                terrain.max_height,
                shallows,
            )
            node.reparentTo(self.root)
            for name, value in LOOKS[BIOMES[terrain.biome].look].items():
                node.setShaderInput(name, value)
            node.setShaderInput("water_offset", (0.0, -first * terrain.voxel))  # this strip's place in the loop
            node.setShaderInput("water_loop", terrain.loop_length)
            nodes.append(node)
        return nodes
