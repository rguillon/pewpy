"""What the industrial ships carry, each in its own module.

On the left of their core (`edge`: its outer column), or on both sides.
"""

from pewpewdev.tools.candidates.industrial.attachments.antenna import antenna
from pewpewdev.tools.candidates.industrial.attachments.boom import boom
from pewpewdev.tools.candidates.industrial.attachments.cannon import cannon
from pewpewdev.tools.candidates.industrial.attachments.containers import containers
from pewpewdev.tools.candidates.industrial.attachments.fins import fins
from pewpewdev.tools.candidates.industrial.attachments.mandible import mandible
from pewpewdev.tools.candidates.industrial.attachments.nacelle import nacelle
from pewpewdev.tools.candidates.industrial.attachments.radiator import radiator
from pewpewdev.tools.candidates.industrial.attachments.turret import turret
from pewpewdev.tools.candidates.industrial.attachments.wing_delta import wing_delta
from pewpewdev.tools.candidates.industrial.attachments.wing_straight import wing_straight
from pewpewdev.tools.candidates.industrial.attachments.wing_swept import wing_swept

ATTACHMENTS = [wing_delta, wing_swept, wing_straight, nacelle, boom, mandible, fins, turret, cannon, containers,
               radiator, antenna]  # fmt: skip
