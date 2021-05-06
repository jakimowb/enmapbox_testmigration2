from typing import List

from PyQt5.QtGui import QColor
from dataclasses import dataclass
from qgis.core import QgsPalettedRasterRenderer

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

    @staticmethod
    def fromQgsPalettedRasterRenderer(renderer: QgsPalettedRasterRenderer) -> List['Category']:
        assert isinstance(renderer, QgsPalettedRasterRenderer)
        categories = list()
        for c in renderer.classes():
            assert isinstance(c, QgsPalettedRasterRenderer.Class)
            qcolor: QColor = c.color
            category = Category(
                id=c.value,
                name=c.label,
                color=Color(red=qcolor.red(), green=qcolor.green(), blue=qcolor.blue())
            )
            categories.append(category)
        return categories
