from __future__ import print_function
import os
import numpy


from enmapbox.processing.workflow import (ProductCollectionBA, ProductCollectionFA, GDALMeta,
                                          BlockAssociations, FilenameAssociations,
                                          FilenameAssociationsCollection, BlockAssociationsCollection,
                                          ImageBA, ImageFA,
                                          Workflow)
from hub.file import mkdir, filesearch
from hub.timing import tic, toc

class LandsatBA(BlockAssociations):

    def addBlock(self, sr_cube, qa_cube, sr_meta, qa_meta):

        BlockAssociations._addBlock(self, 'sr', sr_cube, sr_meta)
        BlockAssociations._addBlock(self, 'qa', qa_cube, qa_meta)
        return self

    @property
    def sr(self):
        return self.getCube('sr')

    @property
    def srMeta(self):
        return self.getMeta('sr')

    @property
    def qa(self):
        return self.getCube('qa')

    @property
    def qaMeta(self):
        return self.getMeta('qa')

    @property
    def blue(self):
        return self.getCube('sr')[0]

    @property
    def green(self):
        return self.getCube('sr')[1]

    @property
    def red(self):
        return self.getCube('sr')[2]

    @property
    def nir(self):
        return self.getCube('sr')[3]

    @property
    def swir1(self):
        return self.getCube('sr')[4]

    @property
    def swir2(self):
        return self.getCube('sr')[5]

    @property
    def fmask(self):
        return self.getCube('qa')[0]


class LandsatFA(FilenameAssociations):

    BlockAssociationsClass = LandsatBA
    inExtensions = ['.img','.tif','.vrt']
    outExtension = '.img'

    def __init__(self, dirname):
        FilenameAssociations.__init__(self)
        self.dirname = dirname
        self.scene = os.path.basename(dirname)

    def _linkInputFiles(self):
        for key in ['sr', 'qa']:
            filename = None
            for ext in self.inExtensions:
                basename = self.scene + '_' + key + ext
                filename = os.path.join(self.dirname, basename)
                if os.path.exists(filename):
                    break
            if filename is None:
                raise Exception('No filename found.')
            self._addImage(key=key, filename=filename)

    def _linkOutputFiles(self, outputs):
        for key in ['sr', 'qa']:
            basename = self.scene + '_' + key + self.outExtension
            filename = os.path.join(self.dirname, basename)
            self._addImage(key=key, filename=filename)


class LandsatCollectionBA(ProductCollectionBA):

    ProductBAClass = LandsatBA


class LandsatCollectionFA(ProductCollectionFA):

    BlockAssociationsClass = LandsatCollectionBA
    ProductFAClass = LandsatFA



class MyWorkflowIOLandsat(Workflow):

    def apply(self, info):

        landsatBA = self.inputs.landsat
        landsatCopyBA = LandsatBA().addBlock(sr_cube=landsatBA.sr,
                                             qa_cube=landsatBA.qa,
                                             sr_meta=landsatBA.srMeta,
                                             qa_meta=landsatBA.qaMeta)
        self.outputs.landsat = landsatCopyBA


class MyWorkflowIOLandsatCollection(Workflow):

    def apply(self, info):

        landsatCollectionBA = self.inputs.collection
        assert isinstance(landsatCollectionBA, LandsatCollectionBA)
        landsatCollectionCopyBA = LandsatCollectionBA()
        for landsatBA in landsatCollectionBA:
            landsatCollectionCopyBA.append(landsatBA)

        self.outputs.collection = landsatCollectionCopyBA


def testIOLandsat():

    workflow = MyWorkflowIOLandsat()
    workflow.infiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC\LC81930242015276LGN00')
    #workflow.infiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS\32\32UPC\LC81930242015276LGN00')

    workflow.outfiles.landsat = LandsatFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyLandsat\32\32UPC\LC81930242015276LGN00')
    workflow.controls.setNumThreads(1)
    workflow.run()

def testIOLandsatCollection():

    workflow = MyWorkflowIOLandsatCollection()
    workflow.infiles.collection =  LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC')
    workflow.outfiles.collection = LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI_CopyCollection\32\32UPC')
    workflow.controls.setNumThreads(1)
    workflow.run()


if __name__ == '__main__':
    tic()
    #testIOLandsat()
    testIOLandsatCollection()
    toc()