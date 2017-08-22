import gdal, numpy
import hubdc.applier
import hubflow.types

class Applier(hubdc.applier.Applier):

    def setFlowMask(self, name, mask):
        if mask is None or mask.filename is None:
            pass
        elif isinstance(mask, hubflow.types.Mask):
           self.setInput(name, filename=mask.filename, resampleAlg=gdal.GRA_Mode)
        elif isinstance(mask, hubflow.types.Vector):
            self.setVector(name, filename=mask.filename, layer=mask.layer)
        else:
            raise Exception('wrong mask type')

    def setFlowVector(self, name, vector):
        assert isinstance(vector, hubflow.types.Vector)
        self.setVector(name, filename=vector.filename, layer=vector.layer)

class ApplierOperator(hubdc.applier.ApplierOperator):

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
