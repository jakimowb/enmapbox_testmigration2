from PyQt5.QtGui import QColor
from osgeo import gdal
from qgis._core import QgsPalettedRasterRenderer

from hubdsm.algorithm.importenmapl1b import importEnmapL1B
from hubdsm.algorithm.remaprastervalues import remapRasterValues
from hubdsm.core.category import Category
from hubdsm.core.color import Color
from hubdsm.core.gdalraster import GdalRaster
from hubdsm.core.gdalrasterdriver import GdalRasterDriver, VRT_DRIVER
from hubdsm.processing.enmapalgorithm import *
from hubdsm.core.raster import Raster


class SaveLayerAsClassification(EnMAPAlgorithm):
    def displayName(self):
        return 'Save as Classification'

    def description(self):
        return 'Save raster layer with "Paletted/Unique values" renderer as classification with proper class names and color.'

    def group(self):
        return Group.CREATE_RASTER.value

    P_RASTER = 'raster'
    P_OUTRASTER = 'outraster'

    def defineCharacteristics(self):
        self.addParameter(
            EnMAPProcessingParameterRasterLayer(
                name=self.P_RASTER, description='Styled raster',
                help=Help(text='Raster layer with "Paletted/Unique values" renderer.')
            )
        )

        self.addParameter(
            EnMAPProcessingParameterRasterDestination(
                name=self.P_OUTRASTER, description='Classification', defaultValue='outClassification.vrt'
            )
        )

    def processAlgorithm_(self, parameters: Dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        classification = saveLayerAsClassification(
            qgsRasterLayer=self.parameter(parameters, self.P_RASTER, context),
            filename=self.parameter(parameters, self.P_OUTRASTER, context)
        )
        return {self.P_OUTRASTER: classification.band(1).filename}


def saveLayerAsClassification(qgsRasterLayer: QgsRasterLayer, filename: str) -> Raster:
    assert isinstance(qgsRasterLayer, QgsRasterLayer)
    assert isinstance(qgsRasterLayer.renderer(), QgsPalettedRasterRenderer)
    renderer: QgsPalettedRasterRenderer = qgsRasterLayer.renderer()

    raster = Raster.open(qgsRasterLayer.source()).select(selectors=[renderer.band()])
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

    driver = GdalRasterDriver.fromFilename(filename=filename)
    gdalBand = raster.band(1).gdalBand.translate(filename=filename, driver=driver)
    classification = Raster.open(gdalBand.raster)
    classification.setCategories(categories=categories)
    return classification
