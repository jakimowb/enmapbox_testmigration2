from __future__ import print_function
import os

import numpy
from sklearn.kernel_ridge import KernelRidge
from sklearn.grid_search import GridSearchCV
import matplotlib.pyplot as plt
from rios.pixelgrid import pixelGridFromFile, findCommonRegion, PixelGridDefn

from hub.timing import tic, toc
from enmapbox.processing.workflow.types import (Workflow, Image, ImageBlock, ImageCollection, ImageCollectionBlock,
    ImageCollectionList, ImageCollectionListBlock, assertType, GDALMeta, Date)


class Stacking(Workflow):

    def apply(self, info):

        scenes1 = assertType(self.inputs.scenes1, ImageCollectionListBlock)
        scenes2 = assertType(self.inputs.scenes2, ImageCollectionListBlock)

        fmask = list()
        sr = {i:list() for i in range(6)}
        bandNames = list()
        wavelength = list()
        for scenes in [scenes1, scenes2]:
            for id, scene in scenes.collections.items():
                bandNames.append(id)
                wavelength.append(Date.fromLandsatSceneID(id).decimalYear)
                fmask.append(scene.images[id+'_qa'].cube)
                for i in range(6):
                    sr[i].append(scene.images[id+'_sr'].cube[i])

        fmask = numpy.vstack(fmask)
        fmaskMeta = GDALMeta()
        fmaskMeta.setBandNames(bandNames)
        fmaskMeta.setNoDataValue(255)
        fmaskMeta.setMetadataItem('wavelength', wavelength)

        for i in range(6):
            sr[i] = numpy.array(sr[i])
        srMeta = GDALMeta()
        srMeta.setBandNames(bandNames)
        srMeta.setNoDataValue(-9999)
        srMeta.setMetadataItem('wavelength', wavelength)

        self.outputs.fmask = ImageBlock(cube=fmask, meta=fmaskMeta)
        for i, key in enumerate(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']):
            setattr(self.outputs, key, ImageBlock(cube=sr[i], meta=srMeta))


def test():

    # convert complete archive to LandsatX
    '''from lamos.operators.landsat_x import LandsatXComposer
    from lamos.processing.types import WRS2Footprint
    WRS2Footprint.createUtmLookup(infolder=r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test')
    composer = LandsatXComposer(inextension='.img')
    composer.composeWRS2Archive(infolder=r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test', outfolder=r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_LandsatX', processes=20)
    return'''

    workflow = Stacking()
    workflow.infiles.scenes1 = ImageCollectionList(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_LandsatX\221\070')
    workflow.infiles.scenes2 = ImageCollectionList(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_LandsatX\221\071')
    workflow.outfiles.fmask = Image(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_stacks\fmask')
    for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']:
        setattr(workflow.outfiles, key, Image(os.path.join(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_stacks_big', key)))

    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()
    #workflow.controls.setWindowXsize(10)
    #workflow.controls.setWindowYsize(10)

    pixelGrid = pixelGridFromFile(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test\221\071\LC82210712013162LGN00\LC82210712013162LGN00_cfmask.img')

    print
    # very small test region inside the overlapping region of both footprints
    if 0:
        pixelGrid.xMin = 202425
        pixelGrid.yMin = -1680165
        pixelGrid.xMax = pixelGrid.xMin + 30*10
        pixelGrid.yMax = pixelGrid.yMin + 30*10

    # region provided by Marcel
    if 1:
        pixelGrid.xMin = 149655
        pixelGrid.xMax = 254025
        pixelGrid.yMin = -1521285
        pixelGrid.yMax = -1809825

        pixelGrid.yMax = -1521285
        pixelGrid.yMin = -1809825

    workflow.controls.setReferencePixgrid(pixelGrid)
    workflow.controls.setResampleMethod('near')

    workflow.run()

if __name__ == '__main__':

    tic()

    test()
    toc()
