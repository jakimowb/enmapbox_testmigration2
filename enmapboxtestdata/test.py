import matplotlib
matplotlib.use('QT5Agg')
from matplotlib import pyplot

from unittest import TestCase
import enmapboxtestdata
from hubflow.core import *

class Test(TestCase):

    def test(self):

        print(Raster(enmapboxtestdata.enmap).dataset().shape())

        definitions = AttributeDefinitionEditor.readFromJson(
            enmapboxtestdata.landcover_polygons.replace('.shp', '.json'))
        for k, v in definitions.items():
            print(k, v)
        print(VectorClassification(enmapboxtestdata.landcover_polygons, classAttribute='level_1_id'))
        print(VectorClassification(enmapboxtestdata.landcover_polygons, classAttribute='level_2_id'))
        print(VectorClassification(enmapboxtestdata.landcover_polygons, classAttribute='level_3_id'))

        definitions = AttributeDefinitionEditor.readFromJson(enmapboxtestdata.landcover_points.replace('.shp', '.json'))
        for k, v in definitions.items():
            print(k, v)
        print(VectorClassification(enmapboxtestdata.landcover_polygons, classAttribute='level_1_id'))
        print(VectorClassification(enmapboxtestdata.landcover_polygons, classAttribute='level_2_id'))

        definitions = AttributeDefinitionEditor.readFromJson(enmapboxtestdata.library.replace('.sli', '.json'))
        for k, v in definitions.items():
            print(k, v)
        library = ENVISpectralLibrary(enmapboxtestdata.library)
        print(library.raster())
        print(library.attributeTable())
        print(library.attributeDefinitions())
        print(library.attributeNames())
        print(Classification.fromENVISpectralLibrary(filename='/vsimem/classification.bsq', library=library, attribute='level_1'))
        print(Classification.fromENVISpectralLibrary(filename='/vsimem/classification.bsq', library=library, attribute='level_2'))
        print(Classification.fromENVISpectralLibrary(filename='/vsimem/classification.bsq', library=library, attribute='level_3'))

    def test_create(self):
        enmapboxtestdata.createEnmapClassification()
        enmapboxtestdata.createEnmapFraction()
        print(enmapboxtestdata.createClassifier())
        print(enmapboxtestdata.createRegressor())
