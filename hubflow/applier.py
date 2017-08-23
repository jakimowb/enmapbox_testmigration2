import gdal, numpy
import hubdc.applier
import hubflow.types
import hubflow.signals

class Applier(hubdc.applier.Applier):

    def __init__(self, defaultGrid=None, **kwargs):
        hubdc.applier.Applier.__init__(self, controls=kwargs.get('controls', None))
        self.controls.setProgressBar(kwargs.get('progressBar', None))
        if isinstance(defaultGrid, hubflow.types.Image):
            defaultGrid = defaultGrid.pixelGrid
        self.controls.setReferenceGrid(kwargs.get('grid', defaultGrid))
        self.kwargs = kwargs

    def apply(self, operator=None, description=None, *ufuncArgs, **ufuncKwargs):
        results = hubdc.applier.Applier.apply(self, operator=operator, description=description,
                                              overwrite=self.kwargs.get('overwrite', True), *ufuncArgs, **ufuncKwargs)
        for output in self.outputs.values():
            hubflow.signals.signals.fileCreated.emit(output.filename)
        return results

    def setInput(self, name, filename, noData=None, resampleAlg=gdal.GRA_NearestNeighbour):
        hubdc.applier.Applier.setInput(self, name=name, filename=filename, noData=noData, resampleAlg=resampleAlg, options=self.kwargs.get(name+'Options', None))

    def setOutput(self, name, filename):
        hubdc.applier.Applier.setOutput(self, name=name, filename=filename, options=self.kwargs.get(name+'Options', None))

    def setFlowImage(self, name, image, **kwargs):
        assert isinstance(image, hubflow.types.Image), image
        self.setInput(name, filename=image.filename)

    def setFlowMask(self, name, mask):
        if mask is None or mask.filename is None:
            pass
        elif isinstance(mask, hubflow.types.Mask):
           self.setInput(name, filename=mask.filename, resampleAlg=gdal.GRA_Mode)
        elif isinstance(mask, hubflow.types.Vector):
            self.setVector(name, filename=mask.filename, layer=mask.layer)
        else:
            raise Exception('wrong mask type')

    def setFlowClassification(self, name, classification):
        if classification is None or classification.filename is None:
            pass
        elif isinstance(classification, hubflow.types.Classification):
            self.setInput(name, filename=classification.filename)
        elif isinstance(classification, hubflow.types.VectorClassification):
            self.setVector(name, filename=classification.filename, layer=classification.layer)
        else:
            raise Exception('wrong classification type')

    def setFlowVector(self, name, vector):
        assert isinstance(vector, hubflow.types.Vector)
        self.setVector(name, filename=vector.filename, layer=vector.layer)

class ApplierOperator(hubdc.applier.ApplierOperator):

    def getFlowImageArray(self, name, image, indicies=None, overlap=0, dtype=None):
        assert isinstance(image, hubflow.types.Image)
        array = self.getArray(name, indicies=indicies, overlap=overlap, dtype=dtype)
        return array

    def getFlowMaskArray(self, name, mask, overlap=0):
        if mask is None or mask.filename is None:
            array = self.getFull(value=True, bands=1, dtype=numpy.bool, overlap=overlap)
        elif isinstance(mask, hubflow.types.Mask):
            array = self.getMaskArray(name=name, noData=0, ufunc=mask.ufunc, overlap=overlap)
        elif isinstance(mask, hubflow.types.Vector):
            array = self.getVectorArray(name=name, allTouched=mask.allTouched, filterSQL=mask.filterSQL, dtype=numpy.uint8)==1
        else:
            raise Exception('wrong mask type')
        return array

    def getFlowClassificationArray(self, name, classification, oversampling=1):
        if classification is None or classification.filename is None:
            array = numpy.array([])
        elif isinstance(classification, hubflow.types.Classification):
            array = self.getClassificationArray(name, minOverallCoverage=classification.minOverallCoverage, minWinnerCoverage=classification.minWinnerCoverage)
        elif isinstance(classification, hubflow.types.VectorClassification):
            ids = range(1, classification.classDefinition.classes + 1)
            array = self.getVectorCategoricalArray('vectorClassification', ids=ids, noData=0, oversampling=oversampling,
                                                            minOverallCoverage=classification.minOverallCoverage, minWinnerCoverage=classification.minWinnerCoverage,
                                                            burnAttribute=classification.idAttribute, allTouched=classification.allTouched, filterSQL=classification.filterSQL)
        return array

    def getFlowProbabilityArray(self, name, probability, oversampling=1):
        if probability is None or probability.filename is None:
            array = numpy.array([])
        elif isinstance(probability, hubflow.types.Classification):
            assert 0
        elif isinstance(probability, hubflow.types.VectorClassification):
            ids = range(1, probability.classDefinition.classes + 1)
            array = self.getVectorCategoricalFractionArray(name, ids=ids, minOverallCoverage=probability.minOverallCoverage, oversampling=oversampling,
                                                                 burnAttribute=probability.idAttribute, allTouched=probability.allTouched, filterSQL=probability.filterSQL)
        return array

    def getFlowVectorArray(self, name, vector, overlap=0):
        assert isinstance(vector, hubflow.types.Vector)
        return self.getVectorArray(name, initValue=vector.initValue, burnValue=vector.burnValue, burnAttribute=vector.burnAttribute,
                                   allTouched=vector.allTouched, filterSQL=vector.filterSQL, overlap=overlap, dtype=vector.dtype)

    def setFlowMetadataClassDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.types.ClassDefinition)
        self.setMetadataClassDefinition(name=name, classes=classDefinition.classes, classNames=classDefinition.names, classLookup=classDefinition.lookup)

    def setFlowMetadataProbabilityDefinition(self, name, classDefinition):
        assert isinstance(classDefinition, hubflow.types.ClassDefinition)
        self.setMetadataProbabilityDefinition(name=name, classes=classDefinition.classes, classNames=classDefinition.names, classLookup=classDefinition.lookup)
