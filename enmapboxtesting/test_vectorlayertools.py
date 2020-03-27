from enmapbox.testing import TestObjects, EnMAPBoxTestCase
from enmapbox.externals.qps.vectorlayertools import VectorTools

class TestCasesVectorLayerTools(EnMAPBoxTestCase):


    def test_VectorLayerTools(self):
        lyr0 = TestObjects.createVectorLayer()
        lyr = TestObjects.createVectorLayer()

        f0 = lyr0.getFeature(0)
        tools = VectorTools()

        tools.startEditing(lyr)
        #tools.addFeature(lyr, None, f0.geometry(), f0)
        tools.stopEditing(lyr, True)
        tools.stopEditing(lyr, False)
        tools.commitError(lyr)
        tools.saveEdits(lyr)
        tools.commitError(lyr)



