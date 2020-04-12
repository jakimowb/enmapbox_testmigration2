from dataclasses import dataclass

from hubdsm.core.color import Color


@dataclass(frozen=True)
class Category(object):
    id: int
    name: str
    color: Color

    def __post_init__(self):
        assert isinstance(id, int) >= 0
        assert isinstance(self.name, str)
        assert isinstance(self.color, Color)
