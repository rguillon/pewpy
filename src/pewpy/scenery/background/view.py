"""Drawing the backgrounds (see pewpy.scenery.background) with Panda3D."""

from panda3d.core import Lens, NodePath, Point2, Point3, Vec3

from pewpy.graphics import models
from pewpy.scenery import background, params
from pewpy.scenery.background import Area, Scenery
from pewpy.scenery.ground import props, shader
from pewpy.scenery.ground.terrain import Terrain
from pewpy.scenery.params import Color3, SceneryParams

AREA_MARGIN = 0.05  # world units beyond the screen edges, so nothing pops in at the edges


def _opaque(color: Color3) -> models.Color:
    return (color[0], color[1], color[2], 1.0)


def space_color() -> models.Color:
    """What the camera clears to around the game area and behind the menus: space's sky."""
    return _opaque(params.resolve("space").sky)


def sky_color(scenery: SceneryParams, time_of_day: str = "day") -> models.Color:
    """What shows where a background draws nothing (between clouds...): its sky, tinted by the time of day."""
    air = scenery.times_of_day[time_of_day].air
    red, green, blue = scenery.sky
    return (red * air[0], green * air[1], blue * air[2], 1.0)


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
        look = scenery.params
        times = look.times_of_day[time_of_day]
        tint, air = times.ground, times.air
        mist = look.mist
        self.mist_color: tuple[float, float, float] = mist.color
        if scenery.terrain:
            red, green, blue = look.haze.color
            haze = (red * air[0], green * air[1], blue * air[2], look.haze.amount)
            self.root.setShaderInput("haze", haze)  # the air, far away
            self.root.setShaderInput("tint", tint)
            # Clouds: pale, in the air's color, lit like the ground but dimming less at night (the lights below
            # still catch them).
            red, green, blue = (
                (base * (mist.night + (1 - mist.night) * light)) * (1 - mist.air) + far * mist.air
                for base, light, far in zip(mist.color, tint, haze[:3], strict=True)
            )
            self.mist_color = (red, green, blue)
        self.star_depth = look.stars.depth if look.stars else 0.0
        self.star_nodes = [self._star_layer(layer) for layer in scenery.starfield.layers] if scenery.starfield else []
        self.layer_nodes = [[self._drifter(layer, drifter) for drifter in layer.drifters] for layer in scenery.layers]
        self.ground_nodes = self._ground(scenery.terrain) if scenery.terrain else []
        self.sync()

    def sync(self) -> None:
        if self.scenery.starfield:
            for layer, node in zip(self.scenery.starfield.layers, self.star_nodes, strict=True):
                node.setPos(0, self.star_depth, -layer.offset)
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
        look = self.scenery.params
        if layer.kind == "mist":
            model = models.mist_model(drifter.shape)
            low, high = look.mist.opacity
            model.setColor(*self.mist_color, low + (high - low) * (drifter.shape % 10) / 9)
        elif layer.kind == "cloud" and look.nebulas is not None:
            palettes = look.nebulas.palettes
            nebula = palettes[self.scenery.variant % len(palettes)]
            model = models.cloud_model(_opaque(nebula[drifter.shape % len(nebula)]), seed=drifter.shape)
        elif layer.kind == "planet" and look.planet is not None:
            palettes = look.planet.palettes
            palette = tuple(_opaque(color) for color in palettes[self.scenery.variant % len(palettes)])
            model = models.distant_planet_model(palette, seed=self.scenery.variant)
        else:
            colors = tuple(_opaque(color) for color in look.rocks.colors) if look.rocks else ()
            model = models.rock_model(drifter.shape, colors)
        model.reparentTo(self.root)
        model.setScale(drifter.size)
        return model

    def _ground(self, terrain: Terrain) -> list[NodePath]:
        return self._relief(terrain)

    def _relief(self, terrain: Terrain) -> list[NodePath]:
        """A smooth ground: a mesh per strip painted by the ground shader, and the props standing on it
        (shader.py).
        """
        relief = terrain.relief
        ground = self.root.attachNewNode("relief")
        textures = shader.maps(relief, terrain.layout)
        width = (relief.columns - 1) * relief.step_x
        look = terrain.scenery
        shader.ground_inputs(ground, look, textures, terrain.loop_length, width)
        max_height = look.ground.max_height if look.ground else 1.0
        nodes = []
        for chunk in range(terrain.chunks):
            strip = ground.attachNewNode(f"strip_{chunk}")
            strip.setShaderInput("ground_offset", chunk * terrain.chunk_height)
            model = shader.relief_chunk_model(relief, chunk * terrain.relief_rows, terrain.relief_rows, max_height)
            model.reparentTo(strip)
            standing = terrain.chunk_props(chunk)
            if standing:
                vertices, triangles = props.strip_arrays(standing, chunk * terrain.chunk_height, look.props)
                shader.props_model(vertices, triangles).reparentTo(strip)
            nodes.append(strip)
        return nodes
