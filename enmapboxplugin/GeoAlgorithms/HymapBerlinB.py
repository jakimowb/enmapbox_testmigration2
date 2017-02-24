from enmapboxplugin.EnMAPBoxGeoAlgorithm import EnMAPBoxGeoAlgorithm
from processing.core.outputs import OutputRaster

class HymapBerlinB(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'HymapBerlinB'
        self.group = 'Testdata'

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('map', 'Predicted'))
        self.addOutput(OutputRaster('train', 'Train'))
        self.addOutput(OutputRaster('test', 'Test'))

    def processAlgorithm(self, progress):
        from enmapbox.testdata import HymapBerlinB as filenames
        self.setOutputValue('image', filenames.HymapBerlinB_image)
        self.setOutputValue('mask', filenames.HymapBerlinB_mask)
        self.setOutputValue('map', filenames.HymapBerlinB_truth)
        self.setOutputValue('train', filenames.HymapBerlinB_train)
        self.setOutputValue('test', filenames.HymapBerlinB_test)