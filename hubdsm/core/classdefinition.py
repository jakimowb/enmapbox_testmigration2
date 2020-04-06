from dataclasses import dataclass
from typing import List

from hubdsm.core.category import Category

@dataclass(frozen=True)
class ClassDefinition(object):
    categories: List[Category]

    @property
    def classes(self):
        return len(self.categories)
