"""Making a ship from the catalog's parts (see .parts): picking them for the size wanted, placing them where they fit.

A ship is made in steps, each part picked among the few nearest what the step wants (a hull about the ship's length,
wings reaching its width...) and placed where its mount goes on what's there: the hull on the axis; wings on its sides;
pods beside it or booms on the wings; engines on its tail, under the wings or on their tips; a cockpit on top or on
the nose; guns on the nose, on top, under the wings, on their tips or on a side; details on top, on the sides and
underneath. A part goes where it fits (see ship.Ship.fits), else another place or another part is tried.

Most ships are symmetric: every part off the axis comes with its mirror image. The others are lopsided (see LOPSIDED),
and their details are placed on one side or the other as often as in pairs.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from pewpy.generators.models.common.geometry import Rng, miss
from pewpy.generators.models.parts import Part, of_kind
from pewpy.generators.models.parts.hulls import PROFILES, hull_at, thickness
from pewpy.generators.models.parts.wings import OUTLINES, wing_at
from pewpy.generators.models.ships import paint
from pewpy.generators.models.ships.modules import KINDS, SIZES, module
from pewpy.generators.models.ships.ship import Placed, Ship, Spot

SYMMETRIC = 0.75  # the share of enemies' ships that are symmetric *(placeholder)*
PLAYER_SYMMETRIC = 0.85  # of the player's *(placeholder)*
LAYOUTS = {"classic": 0.4, "flying_wing": 0.12, "pods": 0.14, "booms": 0.14, "wingless": 0.2}  # how often each
PLAYER_LAYOUTS = {"classic": 0.5, "flying_wing": 0.15, "pods": 0.15, "booms": 0.2}
# How a lopsided ship is lopsided (one or two of them): its two wings different, a pod or a boom on one side only, a
# gun on one side, a command tower off its axis.
LOPSIDED = ("odd_wings", "one_pod", "side_gun", "tower")
CHOICES = 4  # a part is picked among the CHOICES nearest what's wanted
ROOM = (3, 0.06)  # rows the hull leaves for the engines behind it and the guns in front: 3, and 6% of the ship's
NOSE = (2, 0.05)  # rows ahead of its frame a ship's nose guns may reach: 2, or 5% of its length *(placeholder)*
BOOMS = ("cigar", "spindle", "needle", "dart", "teardrop")  # the hulls' profiles booms and pods are made of
REACH = 0.5  # a part on the hull is at most this share of its length (or 4 rows)...
TALL = 0.75  # ...and this share of its thickness (or 2 cubes) high: no big antenna on a tiny ship
COCKPIT_TALL = 1.0  # a cockpit sticks out more: up to the hull's thickness
THICKER = 1  # an engine or a pod is at most this many cubes thicker than the hull
TRIES = 12  # places (and parts) tried before giving up
SUPPORT = 0.6  # the share of a part on top that must stand on the ship...
PART_SUPPORT = 0.4  # ...of a destroyable part, which may overhang more *(placeholder)*
WING_OVERLAP = 0.5  # the share of a wing's cubes that may sink into the hull (its root)
DETAIL_SHARES = {
    "vent": 3.0,
    "intake": 1.5,
    "fin": 1.5,
    "antenna": 1.0,
    "sensor": 1.0,
    "tank": 1.0,
    "armor": 1.0,
    "light": 1.5,
    "greeble": 1.0,
}
AREA_PER_WEAPON = 900  # square cubes of an enemy for each weapon past the first few
PART_WIDTH = 40  # cubes of a ship's width for each size step of its destroyable parts *(placeholder)*
AREA_PER_DETAIL = 250  # square cubes of the ship for each detail past the first few
MAX_DETAILS = 40


@dataclass(frozen=True)
class Hull:
    """The main hull, placed on the axis, its tail on y = 0: its profile, row by row."""

    part: Part

    @property
    def length(self) -> int:
        """Return how many rows long it is."""
        return self.part.high[1] + 1

    def half(self, y: int) -> int:
        """Return how far its side is from the axis on row y (0 off the hull)."""
        return self.part.rows[y][0] if y in self.part.rows else 0

    def widest(self, y0: int, y1: int) -> int:
        """Return how far its side is from the axis at most, from row y0 to y1."""
        return max((self.half(y) for y in range(y0, y1 + 1)), default=0)

    def top(self, y: int) -> int:
        """Return its top's z on row y (the nearest row of the hull)."""
        return self.part.rows[self._on(y)][1]

    def bottom(self, y: int) -> int:
        """Return its bottom's z on row y (the nearest row of the hull)."""
        return self.part.rows[self._on(y)][2]

    def middle(self, y: int) -> int:
        """Return the z halfway up it on row y."""
        return (self.top(y) + self.bottom(y)) // 2

    def _on(self, y: int) -> int:
        return max(0, min(self.length - 1, y))


@dataclass(frozen=True)
class Wing:
    """A wing placed: its columns from its root out to its tip, each (x, back y, front y, lowest z, highest z)."""

    columns: list[tuple[int, int, int, int, int]]

    @classmethod
    def of(cls, placed: Placed) -> "Wing":
        """Return a placed wing's columns."""
        found: dict[int, tuple[int, int, int, int]] = {}
        for x, y, z in placed.cells():
            back, front, low, high = found.get(x, (y, y, z, z))
            found[x] = min(back, y), max(front, y), min(low, z), max(high, z)
        outward = sorted(found, key=lambda x: abs(x - placed.spot.x))
        return cls([(x, *found[x]) for x in outward])

    def at(self, share: float) -> tuple[int, int, int, int, int]:
        """Return the column `share` of the way from the root (0) to the tip (1)."""
        return self.columns[round(share * (len(self.columns) - 1))]


def mirrored(spot: Spot) -> Spot:
    """Return a spot's mirror image across the ship's axis."""
    return Spot(-spot.x, spot.y, spot.z, not spot.flip)


@dataclass
class Maker:
    """A ship being made to about `wanted` cubes (columns, rows): see the module's description."""

    rng: Rng
    wanted: tuple[float, float]
    player: bool = False
    parts: int = 0  # destroyable parts (a boss always has some, an enemy may)
    forced: bool | None = None  # symmetric (True) or lopsided (False) whatever the odds, if set
    least_armed: int = 1  # weapons it has at least, its destroyable parts' too
    ship: Ship = field(default_factory=Ship)
    symmetric: bool = field(init=False)
    lopsided: set[str] = field(init=False)
    layout: str = field(init=False)
    hull: Hull = field(init=False)
    wings: list[Wing] = field(default_factory=list)  # the main wings: the left one first, if any
    booms: list[Spot] = field(default_factory=list)  # where the booms (or the pods) are, their tails
    bounds: tuple[int, int, int, int] | None = None  # once framed: what the rest stays within (see `dress`)

    def __post_init__(self) -> None:
        """Pick whether it's symmetric (or how it's lopsided), and its layout."""
        rng = self.rng
        self.symmetric = rng.random() < (PLAYER_SYMMETRIC if self.player else SYMMETRIC)
        if self.forced is not None:
            self.symmetric = self.forced
        self.lopsided = set() if self.symmetric else set(rng.sample(LOPSIDED, rng.randint(1, 2)))
        layouts = PLAYER_LAYOUTS if self.player else LAYOUTS
        self.layout = rng.choices(list(layouts), list(layouts.values()))[0]

    def make(self) -> Ship:
        """Make the ship: its frame, then the rest (see `frame` and `dress`)."""
        self.frame()
        return self.dress()

    def frame(self) -> Ship:
        """Make what gives the ship its size: its hull, wings, pods or booms, engines."""
        self._hull()
        if self.layout != "wingless":
            self._wings()
            if self.rng.random() < 0.4 and self.layout in ("classic", "booms"):
                self._small_wings()
        if self.layout == "pods" or (self.layout == "wingless" and "one_pod" in self.lopsided):
            self._pods()
        if self.layout == "booms" and self.wings:
            self._booms()
        self._engines()
        return self.ship

    def dress(self) -> Ship:
        """Finish the framed ship: its cockpit, destroyable parts (a boss's), weapons, details; then paint it.

        What it gets stays within its frame (its columns and rows), but for nose_room(...) rows ahead of it: its size
        is its frame's.
        """
        xs = [x for x, _, _ in self.ship.cells]
        ys = [y for _, y, _ in self.ship.cells]
        self.bounds = (min(xs), max(xs), min(ys), max(ys) + nose_room(self.wanted[1]))
        self._cockpit()
        if self.parts:
            self._destroyable()
        self._arm()
        self._details()
        self._paint()
        return self.ship

    # Picking and placing

    def _pick(self, parts: list[Part], measure: Callable[[Part], tuple[float, ...]], want: tuple[float, ...]) -> Part:
        """Pick a part among the CHOICES whose `measure` is nearest `want`."""
        nearest = sorted(parts, key=lambda part: miss(measure(part), want))
        return self.rng.choice(nearest[:CHOICES])

    def _fitting(self, parts: list[Part], tall: float = TALL) -> list[Part]:
        """Return the parts small enough for the hull: short enough (see REACH), low enough (see `tall`)."""
        longest = max(4.0, self.hull.length * REACH)
        highest = max(2.0, self.hull.part.extent()[2] * tall)
        return [part for part in parts if part.extent()[1] <= longest and part.extent()[2] <= highest]

    def _thin(self, parts: list[Part]) -> list[Part]:
        """Return the parts no thicker than the hull allows an engine or a pod (see THICKER)."""
        return [part for part in parts if part.extent()[2] <= self.hull.part.extent()[2] + THICKER]

    def _pair(self, spot: Spot, part: Part) -> list[Spot]:
        """Return where a part goes for a spot: on the axis alone; else with its mirror image (or on one side only).

        A part that would run into its mirror image goes on the axis instead if it's symmetric, else nowhere.
        """
        if spot.x and _crosses(part, spot):
            spot = Spot(0, spot.y, spot.z)
            if not part.symmetric:
                return []
        if spot.x == 0 and part.symmetric:
            return [spot]
        if self.symmetric:
            return [spot, mirrored(spot)]
        return self.rng.choice([[spot, mirrored(spot)], [spot, mirrored(spot)], [spot], [mirrored(spot)]])

    def _put(self, part: Part, spots: list[Spot], overlap: float = 0.0) -> bool:
        """Place a part at the spots if it fits there (and within the frame, see `dress`); tell whether it did."""
        if not spots or not self._within(part, spots) or not self.ship.fits(part, spots, overlap):
            return False
        self.ship.place(part, spots)
        return True

    def _within(self, part: Part, spots: list[Spot]) -> bool:
        """Tell whether a part at the spots stays within the ship's frame (anywhere, while it's being framed)."""
        if self.bounds is None:
            return True
        left, right, back, front = self.bounds
        for spot in spots:
            x0, x1 = (
                (spot.x - part.high[0], spot.x - part.low[0])
                if spot.flip
                else (spot.x + part.low[0], spot.x + part.high[0])
            )
            if x0 < left or x1 > right or spot.y + part.low[1] < back or spot.y + part.high[1] > front:
                return False
        return True

    def _on_wings(self, share: float, spot_at: Callable[[tuple[int, int, int, int, int]], Spot | None]) -> list[Spot]:
        """Return where a part goes on each wing: `spot_at` a column `share` of the way out (see Wing.at).

        On the right wing it's mirrored. On a lopsided ship, it goes on both wings or on one of them.
        """
        spots = []
        for index, wing in enumerate(self.wings):
            spot = spot_at(wing.at(share))
            if spot is None:
                return []
            spots.append(Spot(spot.x, spot.y, spot.z, flip=index == 1))
        if self.symmetric or len(spots) < 2:
            return spots
        return self.rng.choice([spots, spots, spots[:1], spots[1:]])

    def _on_top(self, part: Part, x: int, y: int, *, flip: bool = False, support: float = SUPPORT) -> Spot | None:
        """Return the spot standing a part on what's at (x, y) (its origin there), or None if too little is there (less
        than `support` of it).
        """  # noqa: D205 - the summary needs two lines
        spot = Spot(x, y, 0, flip)
        columns = {spot.cell((px, py, 0))[:2] for px, py in part.footprint}
        under = [self.ship.tops[column] for column in columns if column in self.ship.tops]
        if len(under) < support * len(columns):
            return None
        return Spot(x, y, max(under) + 1 - part.low[2], flip)

    def _under(self, part: Part, x: int, y: int) -> Spot | None:
        """Return the spot hanging a part under what's at (x, y), or None if nothing is there."""
        if (x, y) not in self.ship.bottoms:
            return None
        return Spot(x, y, self.ship.bottoms[x, y] - 1 - part.high[2])

    def _under_front(self, part: Part, column: tuple[int, int, int, int, int], ahead: int = 0) -> Spot | None:
        """Return the spot hanging a part under a wing's column (see Wing), its front `ahead` of the wing's front."""
        x, back, front, _, _ = column
        return self._under(part, x, max(back, front - part.high[1] + ahead))

    def _side(self, part: Part, y: int, gap: int = 0) -> Spot:
        """Return the spot putting a part on the hull's left side, `gap` cubes off it, its back on row y."""
        reach = self.hull.widest(y + part.low[1], y + part.high[1])
        return Spot(-reach - 1 - gap, y, self.hull.middle(y + part.extent()[1] // 2))

    # The steps

    def _hull(self) -> None:
        """Put the main hull on the axis: about as long as the ship, as wide as its layout leaves it."""
        rng, (columns, rows) = self.rng, self.wanted
        width = {
            "wingless": rng.uniform(0.55, 0.9),
            "flying_wing": rng.uniform(0.2, 0.4),
            "pods": rng.uniform(0.2, 0.4),
        }.get(self.layout, rng.uniform(0.15, 0.35))
        length = rng.uniform(0.55, 0.8) if self.layout == "flying_wing" else rng.uniform(0.75, 0.95)
        length = max(4.0, rows * length - ROOM[0] - rows * ROOM[1])  # room for the engines and the guns
        part = _made_hull(rng.choice(list(PROFILES)), length, columns * width / 2)
        self.ship.place(part, [Spot(0, 0, 0)])
        self.hull = Hull(part)

    def _wings(self) -> None:
        """Put the main wings on the hull's sides, reaching the ship's width; different ones on an odd-winged ship."""
        rng, hull = self.rng, self.hull
        flying = self.layout == "flying_wing"
        chord = hull.length * (rng.uniform(0.6, 0.95) if flying else rng.uniform(0.25, 0.5))
        reach = max(2.0, self.wanted[0] / 2 - hull.widest(0, hull.length - 1) * 0.8)
        outlines = rng.sample(list(OUTLINES), 2)
        span, long = max(1, round(reach) - 1), max(2, round(chord))
        left = wing_at(outlines[0], span, long)
        right = wing_at(outlines[1], span, long) if "odd_wings" in self.lopsided else left
        for _ in range(TRIES):
            back = round(hull.length * (rng.uniform(0.0, 0.12) if flying else rng.uniform(0.05, 0.4)))
            lift = rng.choice([0, 0, 1, -1])  # its root a cube above or below the hull's middle, sometimes
            spots = [self._wing_spot(left, back, lift), mirrored(self._wing_spot(right, back, lift))]
            if self.ship.fits(left, spots[:1], WING_OVERLAP) and self.ship.fits(right, spots[1:], WING_OVERLAP):
                self.ship.place(left, spots[:1])
                self.ship.place(right, spots[1:])
                self.wings = [Wing.of(placed) for placed in self.ship.placed[-2:]]
                return

    def _wing_spot(self, part: Part, back: int, lift: int = 0) -> Spot:
        """Return where a left wing goes: its root on the hull's side (sinking into it), its trailing edge on `back`.

        Its root `lift` cubes above the hull's middle (but within the hull).
        """
        roots = sorted(y for x, y, _ in part.cells if x == 0)
        narrowest = min(self.hull.half(back + y) for y in roots)
        middle = back + roots[len(roots) // 2]
        z = self.hull.middle(middle) + lift
        return Spot(-narrowest, back, max(self.hull.bottom(middle), min(self.hull.top(middle), z)))

    def _small_wings(self) -> None:
        """Put a small pair of wings near the nose (canards) or the tail (a tailplane)."""
        rng, hull = self.rng, self.hull
        reach = max(1.5, (self.wanted[0] / 2 - hull.widest(0, hull.length - 1)) * rng.uniform(0.2, 0.4))
        part = wing_at(rng.choice(list(OUTLINES)), max(1, round(reach)), max(2, round(hull.length * 0.15)))
        canards = rng.random() < 0.5
        for _ in range(TRIES):
            back = round(hull.length * (rng.uniform(0.62, 0.78) if canards else rng.uniform(0.0, 0.08)))
            spot = self._wing_spot(part, back)
            if self._put(part, [spot, mirrored(spot)], WING_OVERLAP):
                return

    def _pods(self) -> None:
        """Put a pod beside the hull on each side (on one side only on a one-podded ship): engines or small hulls."""
        rng, hull = self.rng, self.hull
        long = hull.length * rng.uniform(0.4, 0.7)
        nacelles = self._thin(of_kind("engine", "pod"))
        if nacelles and rng.random() < 0.5:
            part = self._pick(nacelles, lambda part: (part.extent()[1],), (long,))
        else:
            part = _made_hull(
                rng.choice(BOOMS), long, max(1.0, hull.widest(0, hull.length - 1) * rng.uniform(0.2, 0.4))
            )
        for _ in range(TRIES):
            back = round(hull.length * rng.uniform(0.0, 0.3))
            inner = self._side(part, back, gap=rng.choice([0, 1, 2]))
            spot = Spot(inner.x + part.low[0], back, inner.z)  # its inner side against the hull's
            spots = [rng.choice([spot, mirrored(spot)])] if "one_pod" in self.lopsided else [spot, mirrored(spot)]
            if self._put(part, spots):
                self.booms = spots
                return

    def _booms(self) -> None:
        """Put a boom on each wing (on one only on a one-podded ship), sticking out behind it, a fin on its tail."""
        rng, hull = self.rng, self.hull
        half = max(1.0, hull.widest(0, hull.length - 1) * rng.uniform(0.2, 0.35))
        part = _made_hull(rng.choice(BOOMS), hull.length * rng.uniform(0.5, 0.8), half)
        behind = round(part.extent()[1] * rng.uniform(0.3, 0.55))
        spots = self._on_wings(rng.uniform(0.4, 0.75), lambda column: Spot(column[0], column[1] - behind, column[3]))
        if "one_pod" in self.lopsided:
            spots = [rng.choice(spots)]
        if not self._put(part, spots, overlap=0.15):
            return
        self.booms = spots
        fins = self._fitting(of_kind("fin", "top"))
        if not fins:
            return
        fin = self._pick(fins, lambda part: part.extent()[1:], (3, 3))
        for boom in spots:
            top = self._on_top(fin, boom.x, boom.y)
            if top is not None:
                self._put(fin, [top])

    def _engines(self) -> None:
        """Put the engines: on the tail, at the booms' tails, under the wings or on their tips. Always at least one."""
        rng = self.rng
        where = ["tail", "tail", "tail"] + (["wing_pods", "tip_pods"] if self.wings else [])
        where += ["booms", "booms"] if self.booms and self.layout == "booms" else []
        choice = rng.choice(where)
        if choice == "booms":
            self._boom_engines()
        elif choice != "tail":
            self._wing_engines(tip=choice == "tip_pods")
        if choice == "tail" or rng.random() < 0.4 or not self.ship.nozzles:
            self._tail_engines()
        if not self.ship.nozzles:  # nothing fitted: the smallest nozzle, right behind the hull
            part = of_kind("engine", "tail")[0]
            self.ship.place(part, [Spot(0, -part.high[1] - 1, self.hull.middle(0))])

    def _tail_engines(self) -> None:
        """Put one engine on the hull's tail, or two side by side, about as wide as the tail."""
        rng, hull = self.rng, self.hull
        tail = 2 * hull.widest(0, 1) + 1
        for _ in range(TRIES):
            pair = rng.random() < 0.4 and tail >= 5
            want = (tail / (2 if pair else 1), hull.length * 0.2)
            part = self._pick(self._thin(of_kind("engine", "tail")), lambda part: part.extent()[:2], want)
            spot = Spot(0, -part.high[1] - 1, hull.middle(0))
            if pair:
                spot = Spot(-part.high[0] - rng.choice([0, 1]), spot.y, spot.z)
            if self._put(part, [spot, mirrored(spot)] if pair else [spot]):
                return

    def _wing_engines(self, *, tip: bool) -> None:
        """Put an engine pod under each wing (or on its tip)."""
        rng = self.rng
        pods = self._thin(of_kind("engine", "pod"))
        if not pods:
            return
        for _ in range(TRIES):
            part = self._pick(pods, lambda part: part.extent()[1:2], (self.hull.length * rng.uniform(0.3, 0.6),))
            ahead = rng.randint(1, 3)

            def spot_at(column: tuple[int, int, int, int, int], part: Part = part, ahead: int = ahead) -> Spot:
                x, back, _, low, high = column
                return Spot(x, back - ahead, (low + high) // 2 if tip else low - 1 - part.high[2])

            if self._put(part, self._on_wings(1.0 if tip else rng.uniform(0.3, 0.7), spot_at)):
                return

    def _boom_engines(self) -> None:
        """Put a nozzle on each boom's tail."""
        for _ in range(TRIES):
            part = self._pick(self._thin(of_kind("engine", "tail")), lambda part: part.extent()[:1], (3,))
            spots = [Spot(boom.x, boom.y - part.high[1] - 1, boom.z, boom.flip) for boom in self.booms]
            if self._put(part, spots):
                return

    def _cockpit(self) -> None:
        """Put a cockpit: on top of the hull in its front half, or on its nose; a command tower off the axis."""
        rng, hull = self.rng, self.hull
        if "tower" in self.lopsided:
            towers = self._fitting([part for part in of_kind("cockpit") if not part.symmetric], COCKPIT_TALL)
            for _ in range(TRIES if towers else 0):
                part = rng.choice(towers)
                y = round(hull.length * rng.uniform(0.35, 0.6))
                x = rng.choice([value for value in range(-hull.half(y), hull.half(y) - 1) if value != -1] or [0])
                spot = self._on_top(part, x, y, flip=rng.random() < 0.5)
                if spot is not None and self._put(part, [spot]):
                    return
        noses = self._fitting(of_kind("cockpit", "nose"), COCKPIT_TALL)
        if noses and rng.random() < 0.15:
            nose = rng.choice(noses)
            if self._put(nose, [Spot(0, hull.length, hull.middle(hull.length - 1))]):
                return
        tops = self._fitting([part for part in of_kind("cockpit", "top") if part.symmetric], COCKPIT_TALL)
        for _ in range(TRIES if tops else 0):
            y = round(hull.length * rng.uniform(0.5, 0.75))
            room = 2 * hull.half(y) + 1
            want = (room * rng.uniform(0.5, 0.9), hull.length * rng.uniform(0.25, 0.45))
            part = self._pick(tops, lambda part: part.extent()[:2], want)
            spot = self._on_top(part, 0, y - part.extent()[1] // 2)
            if spot is not None and self._put(part, [spot]):
                return

    def _arm(self) -> None:
        """Arm it: guns or missiles on the nose, on top, under the wings, on their tips, on a side.

        An enemy gets one to three (more on a big one), and always at least one; the player's ship one or two.
        """
        rng = self.rng
        mounts = ["nose", "nose", "top"] + (["under", "under", "tip"] if self.wings else ["under"])
        area = self.wanted[0] * self.wanted[1]
        count = rng.randint(1, 2) if self.player else rng.randint(1, 3) + round(area / AREA_PER_WEAPON)
        if "side_gun" in self.lopsided:
            self._weapon("side")
        for mount in rng.choices(mounts, k=count):
            self._weapon(mount)
        for _ in range(TRIES):  # as many as it needs at least
            if self.ship.armed() >= max(1, self.least_armed):
                return
            self._weapon(rng.choice(mounts))
        barrel = of_kind("gun", "nose")[0]  # nothing fitted: barrels out of the nose, side by side
        front = max(y for _, y, _ in self.ship.cells) + 1
        for x in range(self.least_armed):
            if self.ship.armed() >= max(1, self.least_armed):
                return
            self.ship.place(barrel, [Spot(x, front, 0)] if x == 0 else [Spot(-x, front, 0), Spot(x, front, 0)])

    def _destroyable(self) -> None:
        """Stand its destroyable parts on it: modules of one to three kinds (see modules.py), sized to the ship, in
        mirrored pairs (one on the axis for an odd count; a lopsided ship's anywhere, alone or in pairs). One that
        fits nowhere is left out; if none fits, one stands on the axis all the same (a ship asked for parts has some).
        """  # noqa: D205 - the summary needs two lines
        rng = self.rng
        kinds = rng.sample(list(KINDS), rng.randint(1, 3))
        size = min(max(SIZES), rng.randint(0, 1) + round(self.wanted[0] / PART_WIDTH))
        left, group = self.parts, 0
        while left:
            pair = left >= 2 and (self.symmetric or rng.random() < 0.5)
            if self._stand(rng.choice(kinds), size, group, pair=pair):
                group += 1
            left -= 2 if pair else 1
        if not self.ship.destroyable:
            self._force(rng.choice(kinds))

    def _stand(self, kind: str, size: int, group: int, *, pair: bool) -> bool:
        """Stand a destroyable part (or a pair) on the hull, or a pair on the wings, where it fits, smaller if it must;
        tell whether it did.
        """  # noqa: D205 - the summary needs two lines
        rng, hull = self.rng, self.hull
        for smaller in range(size, -1, -1):
            part = module(rng, kind, smaller)
            for _ in range(TRIES):
                if pair and self.wings and rng.random() < 0.5:  # on the wings, a part on each
                    spots = self._on_wings(
                        rng.uniform(0.2, 0.7), lambda column, part=part: self._on_chord(part, column)
                    )
                    spots = spots if len(spots) == 2 else []
                else:
                    y = round(hull.length * rng.uniform(0.15, 0.85)) - part.high[1] // 2
                    half = hull.half(y + part.high[1] // 2)
                    if pair:
                        x = -rng.randint(part.high[0] + 1, max(part.high[0] + 1, half + part.high[0]))
                    else:
                        x = 0 if self.symmetric else rng.randint(-half, half)
                    spot = self._on_top(part, x, y, support=PART_SUPPORT)
                    spots = [spot, mirrored(spot)] if spot and pair else [spot] if spot else []
                if spots and self._within(part, spots) and self.ship.fits(part, spots):
                    self.ship.reserve(part, spots, group, kind)
                    return True
        return False

    def _on_chord(self, part: Part, column: tuple[int, int, int, int, int]) -> Spot | None:
        """Return the spot standing a part on a wing's column (see Wing), its middle on the column's middle row."""
        x, back, front, _, _ = column
        return self._on_top(part, x, (back + front) // 2 - part.high[1] // 2, support=PART_SUPPORT)

    def _force(self, kind: str) -> None:
        """Stand the smallest destroyable part of a kind on the axis, halfway along, on what's under it."""
        part = module(self.rng, kind, 0)
        y = self.hull.length // 2 - part.high[1] // 2
        columns = [(px, y + py) for px, py in part.footprint]
        z = max(self.ship.tops.get(column, 0) for column in columns) + 1 - part.low[2]
        self.ship.reserve(part, [Spot(0, y, z)], 0, kind)

    def _weapon(self, mount: str) -> bool:
        """Put a gun or missiles mounting a way (see parts.MOUNTS); tell whether it fitted."""
        rng = self.rng
        parts = self._fitting(of_kind("gun", mount) + of_kind("missile", mount))
        if mount == "side":
            parts = [part for part in parts if not part.symmetric]
        for _ in range(TRIES if parts else 0):
            part = rng.choice(parts)
            spots = self._weapon_spots(part, mount)
            if spots and self._put(part, spots):
                return True
        return False

    def _weapon_spots(self, part: Part, mount: str) -> list[Spot]:
        """Return where a weapon goes for its mount (none if there's no room)."""
        rng, hull = self.rng, self.hull
        if mount == "nose":
            if rng.random() < 0.6 and part.extent()[0] <= 2 * hull.half(hull.length - 1) + 3:
                return [Spot(0, hull.length, hull.middle(hull.length - 1))]
            y = hull.length - rng.randint(2, max(2, hull.length // 3))  # a pair on the cheeks
            return self._pair(Spot(-hull.half(y), y, hull.middle(y)), part)
        if mount == "top":
            y = round(hull.length * rng.uniform(0.2, 0.65))
            x = 0 if part.symmetric and rng.random() < 0.6 else -hull.half(y) + part.high[0]
            spot = self._on_top(part, x, y)
            return self._pair(spot, part) if spot else []
        if mount == "side":
            spot = self._side(part, round(hull.length * rng.uniform(0.2, 0.55)))
            return [rng.choice([spot, mirrored(spot)])]
        return self._wing_weapon_spots(part, mount)

    def _wing_weapon_spots(self, part: Part, mount: str) -> list[Spot]:
        """Return where a weapon goes on the wings' tips or under them (under the hull, without wings)."""
        rng = self.rng
        if not self.wings:
            spot = self._under(part, 0, round(self.hull.length * rng.uniform(0.3, 0.7)))
            return [spot] if spot else []
        if mount == "tip":
            return self._on_wings(1.0, lambda column: Spot(column[0], column[1], (column[3] + column[4]) // 2))
        ahead = rng.randint(0, 2)
        return self._on_wings(rng.uniform(0.3, 0.8), lambda column: self._under_front(part, column, ahead))

    def _details(self) -> None:
        """Put the details, more on a bigger ship; and, on most enemies, one or two of the bosses' built-in parts."""
        rng = self.rng
        columns, rows = self.wanted
        count = min(MAX_DETAILS, rng.randint(1, 3) + round(columns * rows / AREA_PER_DETAIL))
        fins = 0
        for kind in rng.choices(list(DETAIL_SHARES), list(DETAIL_SHARES.values()), k=count):
            if kind == "fin":
                if fins:
                    continue
                fins += 1
            fitting = self._fitting(of_kind(kind))
            if fitting:
                self._detail(rng.choice(fitting))

    def _detail(self, part: Part) -> bool:
        """Put a detail where its mount goes: on top (of the hull, or a wing), on a side, underneath."""
        rng, hull = self.rng, self.hull
        for _ in range(TRIES):
            if part.mount == "side":
                spot = self._side(part, rng.randint(0, max(0, hull.length - part.extent()[1])))
                spots = self._pair(spot, part)
            elif part.mount == "under":
                spots = self._under_spots(part)
            else:
                spots = self._top_spots(part)
            if spots and self._put(part, spots):
                return True
        return False

    def _top_spots(self, part: Part) -> list[Spot]:
        """Return where a detail on top goes: on the hull (a fin near its tail), or on a wing if it's flat."""
        rng, hull = self.rng, self.hull
        if self.wings and part.extent()[2] <= 2 and rng.random() < 0.25:
            along = rng.random()

            def spot_at(column: tuple[int, int, int, int, int]) -> Spot | None:
                x, back, front, _, _ = column
                return self._on_top(part, x, back + round(along * max(0, front - part.high[1] - back)))

            return self._on_wings(rng.uniform(0.2, 0.7), spot_at)
        last = max(0, hull.length - part.extent()[1] - 1)
        y = rng.randint(0, max(0, round(hull.length * 0.3))) if part.kind == "fin" else rng.randint(0, last)
        half = hull.half(y)
        if part.symmetric and rng.random() < 0.5:
            x = 0
        else:
            x = rng.randint(-half, 0) if half else 0
            if x and x + part.high[0] >= 0:  # its mirror image would sink into it
                x = -part.high[0] - 1
        spot = self._on_top(part, x, y)
        return self._pair(spot, part) if spot else []

    def _under_spots(self, part: Part) -> list[Spot]:
        """Return where a detail underneath goes: a drop tank under a wing; anything else under the hull."""
        rng, hull = self.rng, self.hull
        if self.wings and part.kind == "tank":
            return self._on_wings(rng.uniform(0.3, 0.8), lambda column: self._under_front(part, column))
        share = rng.uniform(0.0, 0.3) if part.kind == "fin" else rng.uniform(0.4, 0.8)
        spot = self._under(part, 0, round(hull.length * share))
        return [spot] if spot else []

    def _paint(self) -> None:
        """Paint its bits: a livery stripe, a nose cone or wing stripes (one or two of them, or none), markings."""
        rng, hull = self.rng, self.hull
        schemes = [
            lambda: None,
            lambda: paint.livery(rng, self.ship, hull.length),
            lambda: paint.nose_cone(rng, self.ship, hull.length, hull.widest(0, hull.length - 1)),
            lambda: paint.wing_stripes(rng, self.ship),
        ]
        for scheme in rng.sample(schemes, rng.choice([1, 1, 2])):
            scheme()
        if rng.random() < 0.6:
            paint.markings(rng, self.ship)


def _crosses(part: Part, spot: Spot) -> bool:
    """Tell whether a part at a spot reaches across the ship's axis (its mirror image would run into it)."""
    xs = [spot.cell(cell)[0] for cell in part.cells]
    return min(xs) <= 0 <= max(xs)


def nose_room(rows: float) -> int:
    """Return the rows a ship `rows` long gets ahead of its frame: for the guns on its nose."""
    return max(NOSE[0], round(rows * NOSE[1]))


def _made_hull(profile: str, length: float, half: float) -> Part:
    """Return a profile's hull made to a size (half widths to the half cube, so sizes repeat: see hulls.hull_at)."""
    half = max(0.5, round(half * 2) / 2)
    return hull_at(profile, max(4, round(length)), half, thickness(half))


def make_ship(
    rng: Rng,
    wanted: tuple[float, float],
    *,
    player: bool = False,
    parts: int = 0,
    symmetric: bool | None = None,
    least_armed: int = 1,
) -> Ship:
    """Make a ship of about `wanted` cubes, across and along: an enemy's, the player's (`player`), or a boss (with
    `parts` destroyable parts, `least_armed` weapons at least, symmetric or lopsided as it was if `symmetric` is set).
    Only the size differs: it's made the same way.
    """  # noqa: D205 - the summary needs two lines
    return Maker(rng, wanted, player=player, parts=parts, forced=symmetric, least_armed=least_armed).make()
