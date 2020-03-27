from dataclasses import dataclass, field

from hubdsm.core.color import Color


@dataclass(frozen=True)
class Category(object):
    name: str
    color: Color = field(default_factory=Color)
