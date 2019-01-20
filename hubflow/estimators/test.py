from unittest import TestCase
from hubflow.core import *
import enmapboxtestdata
from .custom import FeatureSubsetter

CUIProgressBar.SILENT = False

tmpfile = lambda basename: r'c:\output\{}'.format(basename)
enmap = Raster(enmapboxtestdata.enmap)

class Test(TestCase):

    def test_FeatureSubsetter(self):

        featureSubsetter = Transformer(sklEstimator=FeatureSubsetter(indices=[0, -1]))
        featureSubsetter.transform(filename=tmpfile('raster.bsq'), raster=enmap)


if __name__ == '__main__':
    Test().test_FeatureSubsetter()