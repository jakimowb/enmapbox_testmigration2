from __future__ import print_function
import os
import numpy


from enmapbox.processing.workflow import (ProductBA, ProductFA,
                                          ProductCollectionBA, ProductCollectionFA,
                                          GDALMeta, Date, assertType,
                                          BlockAssociations, FilenameAssociations,
                                          FilenameAssociationsCollection, BlockAssociationsCollection,
                                          ImageBA, ImageFA,
                                          Workflow)
from hub.file import mkdir, filesearch
from hub.timing import tic, toc

class LandsatBA(ProductBA):

    def addBlock(self, sr_cube, qa_cube, sr_meta, qa_meta):

        BlockAssociations._addBlock(self, 'sr', sr_cube, sr_meta)
        BlockAssociations._addBlock(self, 'qa', qa_cube, qa_meta)
        return self

    def getAcquisitionDate(self):
        return self.srMeta.getAcquisitionDate()

    def getCubeByName(self, bandName):

        bandNames = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']
        if bandName in bandNames:
            return self.getCube(self.productName+'_sr')[bandNames.index(bandName)]

        if bandName == 'fmask':
            return self.getCube(self.productName+'_qa')[0]

        raise Exception('unknown band name: '+str(bandName))

    @property
    def sr(self):
        return self.getCube(self.productName+'_sr')

    @property
    def srMeta(self):
        return self.getMeta(self.productName+'_sr')

    @property
    def qa(self):
        return self.getCube(self.productName+'_qa')

    @property
    def qaMeta(self):
        return self.getMeta(self.productName+'_qa')


class LandsatFA(ProductFA):

    BlockAssociationsClass = LandsatBA
    inExtensions = ['.img','.tif','.vrt']
    outExtension = '.img'

    def getAcquisitionDate(self):
        return Date.fromYearDoy(year=int(self.productName[9:13]), doy=int(self.productName[13:16]))


class LandsatCollectionBA(ProductCollectionBA):

    ProductBAClass = LandsatBA

    def getTimeseriesProduct(self, productName):

        productBA = ProductBA(productName=productName)
        bandNames = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'fmask']
        products = self._collection

        # special handling for empty collection
        if len(products) == 0:
            for bandName in bandNames:
                meta = GDALMeta()
                cube = numpy.zeros((0,0,0))
                productBA.addBlock(key=bandName, cube=cube, meta=meta)
            return productBA

        dates = list()
        decimalYears = list()
        for landsatBA in products:
            date = landsatBA.getAcquisitionDate()
            dates.append(date)
            decimalYears.append(date.decimalYear)

        zipSorted = sorted(list(zip(products, decimalYears)), key=lambda tup: tup[-1])
        products, decimalYear = zip(*zipSorted)

        metas = [landsatBA.srMeta for landsatBA in products]
        metaKeys = ['satellite', 'sunelevation', 'geometric_accuracy', 'sunazimuth',
            'acqtime', 'acqdate', 'proclcode', 'sceneid', 'sensor']

        for bandName in bandNames:

            # create cube
            cube = list()
            for landsatBA in self._collection:
                cube.append(landsatBA.getCubeByName(bandName))
            cube = numpy.array(cube)

            # create meta
            meta = GDALMeta()
            for metaKey in metaKeys:
                meta.setMetadataItem(metaKey, [imeta.getMetadataItem(metaKey) for imeta in metas])
            meta.setMetadataItem('wavelength', decimalYear)
            meta.setBandNames([imeta.getMetadataItem('sceneid') for imeta in metas])
            if bandName == 'fmask':
                meta.setNoDataValue(255)
            else:
                meta.setNoDataValue(metas[0].getNoDataValue())

            # create product
            productBA.addBlock(key=bandName, cube=cube, meta=meta)

        return productBA


class LandsatCollectionFA(ProductCollectionFA):

    BlockAssociationsClass = LandsatCollectionBA
    ProductFAClass = LandsatFA



class WorkflowIOLandsat(Workflow):

    def apply(self, info):

        landsatBA = self.inputs.landsat
        landsatCopyBA = LandsatBA(productName=landsatBA.productName)\
            .addBlock(sr_cube=landsatBA.sr,
                      qa_cube=landsatBA.qa,
                      sr_meta=landsatBA.srMeta,
                      qa_meta=landsatBA.qaMeta)
        self.outputs.landsat = landsatCopyBA


class WorkflowIOLandsatCollection(Workflow):

    def apply(self, info):

        landsatCollectionBA = self.inputs.collection
        assert isinstance(landsatCollectionBA, LandsatCollectionBA)
        landsatCollectionCopyBA = LandsatCollectionBA()
        for landsatBA in landsatCollectionBA:
            landsatCollectionCopyBA.append(landsatBA)

        self.outputs.collection = landsatCollectionCopyBA

class WorkflowLandsatTimeseries(Workflow):

    def apply(self, info):

        landsatCollectionBA = assertType(self.inputs.landsatCollection, LandsatCollectionBA)

        timeseriesProduct = landsatCollectionBA.getTimeseriesProduct(productName='timeseries')

        self.outputs.timeseriesProduct = timeseriesProduct

def testIOLandsat():

    workflow = WorkflowIOLandsat()
    workflow.infiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00')
    #workflow.infiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS\32\32UPC\LC81930242015276LGN00')

    workflow.outfiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyLandsat\32\32UPC\LC81930242015276LGN00')
    workflow.controls.setNumThreads(1)
    workflow.run()

def testIOLandsatCollection():

    workflow = WorkflowIOLandsatCollection()
    workflow.infiles.collection =  LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS\32\32UPC')
    workflow.outfiles.collection = LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS_GTiff\32\32UPC')
    workflow.controls.setOutputDriverGTiff()
    workflow.controls.setNumThreads(1)
    workflow.run()

def testLandsatTimeseries():

    workflow = WorkflowLandsatTimeseries()
    workflow.infiles.landsatCollection = LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC')
    workflow.outfiles.timeseriesProduct = ProductFA(r'C:\Work\data\gms\new_timeseries\32\32UPC')

    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverENVI()
    workflow.run()

if __name__ == '__main__':
    tic()
    #testIOLandsat()
    testIOLandsatCollection()
    #testLandsatTimeseries()
    toc()