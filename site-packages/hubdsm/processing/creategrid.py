from collections import OrderedDict

import numpy as np

from hubdsm.algorithm.aggregatebands import aggregateBands
from hubdsm.core.extent import Extent
from hubdsm.core.gdaldriver import VRT_DRIVER
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.projection import Projection
from hubdsm.core.raster import Raster
from hubdsm.core.resolution import Resolution
from hubdsm.core.shape import RasterShape
from hubdsm.core.size import Size
from hubdsm.processing.enmapalgorithm import *


class CreateGrid(EnMAPAlgorithm):
    def displayName(self):
        return 'Create Grid'

    def description(self):
        return 'Create an empty VRT raster that can be used as a pixel grid definition.'

    def group(self):
        return Group.CreateRaster.value

    P_EXTENT = 'extent'
    P_CRS = 'crs'
    P_RESOLUTION = 'resolution'
    P_OUTPUT_GRID = 'outgrid'

    def defineCharacteristics(self):
        self.addParameter(EnMAPProcessingParameterCrs(name=self.P_CRS, description='CRS'))
        self.addParameter(EnMAPProcessingParameterExtent(name=self.P_EXTENT, description='Extent'))
        self.addParameter(EnMAPProcessingParameterDouble(name=self.P_RESOLUTION, description='Resolution'))
        self.addParameter(
            EnMAPProcessingParameterRasterDestination(
                name=self.P_OUTPUT_GRID, description='Output Grid', defaultValue='grid.vrt'
            )
        )

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        extent_: QgsRectangle = self.parameter(parameters, self.P_EXTENT, context)
        crs: QgsCoordinateReferenceSystem = self.parameter(parameters, self.P_CRS, context)
        resolution: float = self.parameter(parameters, self.P_RESOLUTION, context)
        filename: str = self.parameter(parameters, self.P_OUTPUT_GRID, context)
        shape = RasterShape(
            z=1,
            y=int(round(extent_.height() / resolution, 0)),
            x=int(round(extent_.width() / resolution, 0))
        )
        extent = Extent(
            ul=Location(x=extent_.xMinimum(), y=extent_.yMaximum()),
            size=Size(x=resolution * shape[2], y=resolution * shape[1])
        )
        grid = Grid(
            extent=extent,
            resolution=Resolution(x=resolution, y=resolution), projection=Projection(wkt=crs.toWkt())
        )
        VRT_DRIVER.createFromShape(shape=shape, grid=grid, filename=filename)
        return {self.P_OUTPUT_GRID: filename}
