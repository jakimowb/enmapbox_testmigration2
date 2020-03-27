from dataclasses import dataclass

from hubdsm.core.shape import GridShape


@dataclass
class ProcessingOptions(object):
    shape: GridShape
