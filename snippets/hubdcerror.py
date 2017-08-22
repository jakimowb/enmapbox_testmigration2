from hubdc import HUBDC_VERSION
from hubflow import HUBFLOW_VERSION
from hubdc.applier import ApplierControls
from hubflow.types import *
from enmapboxtestdata import enmap
import numpy
image = Image(enmap)

controls = ApplierControls().setReferenceGridByImage(image.filename)
controls.setNumThreads(None)

print('hubdc   : ' + HUBDC_VERSION)
print('hubflow : ' + HUBFLOW_VERSION)
print('numpy   : ' +numpy.version.version)

i1 = 10
i2 = 20
(min1, min2), (max1, max2), (n1, n2) = image.basicStatistics(bandIndicies=[i1, i2])
m, xedges, yedges = image.scatterMatrix(image2=image, bandIndex=i1, bandIndex2=i2,
                                        range=[float(min1), float(max1)], \
                                        range2=[float(min2), float(max2)], bins=10,
                                        controls=controls)

s = ""