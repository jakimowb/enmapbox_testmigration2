from __future__ import print_function
import os
import numpy

from enmapbox.processing.workflow import GDALMeta, Workflow, ImageFA, ImageBA, FilenameAssociationsCollection, BlockAssociationsCollection
from lamos.workflow.types import LandsatFA, LandsatBA, LandsatCollectionFA, LandsatCollectionBA
from hub.file import mkdir, filesearch
from hub.timing import tic, toc

def assertType(obj, type):
    assert isinstance(obj, type) # makes PyCharm aware of the type!
    return obj

def calculateBandStatistics(collectionBA, start, end):
    assert isinstance(collectionBA, LandsatCollectionBA)


    return

class ClassificationWorkflow(Workflow):

    def apply(self, info):

        landsatCollectionBA = assertType(self.inputs.collection, LandsatCollectionBA)
        landsatCollectionBA.filterDate(start=Date)


        statisticsCollection = BlockAssociationsCollection()
        self.outputs.statisticsCollection = statisticsCollection


def testClassificationWorkflow():

    workflow = ClassificationWorkflow()
    workflow.infiles.collection = LandsatCollectionFA(r'C:\Work\data\gms\landsatXMGRS_ENVI\32\32UPC')
    workflow.outfiles.statisticsCollection = FilenameAssociationsCollection(r'C:\Work\data\gms\CLF_Workflow\32\32UPC')
    workflow.controls.setNumThreads(1)
    workflow.run()


if __name__ == '__main__':
    tic()
    #test1()
    #testIOImage()
    #testIOLandsat()
    #testIOCollection()
    #testIOProduct()
    testIOLandsatCollection()
    #testLandsatTimeseries()
    toc()