from enmapboxplugin.EnMAPBoxGeoAlgorithm import EnMAPBoxGeoAlgorithm
from processing.core.outputs import OutputRaster

class HymapBerlinA(EnMAPBoxGeoAlgorithm):

    def defineCharacteristics(self):
        self.name = 'HymapBerlinA'
        self.group = 'Testdata'

        self.addOutput(OutputRaster('image', 'Image'))
        self.addOutput(OutputRaster('mask', 'Mask'))
        self.addOutput(OutputRaster('map', 'Predicted'))
        self.addOutput(OutputRaster('train', 'Train'))
        self.addOutput(OutputRaster('test', 'Test'))

    def processAlgorithm(self, progress):
        from enmapbox.testdata import HymapBerlinA as filenames
        self.setOutputValue('image', filenames.HymapBerlinA_image)
        self.setOutputValue('mask', filenames.HymapBerlinA_mask)
        self.setOutputValue('map', filenames.HymapBerlinA_truth)
        self.setOutputValue('train', filenames.HymapBerlinA_train)
        self.setOutputValue('test', filenames.HymapBerlinA_test)