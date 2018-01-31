import numpy as np
from hubflow.types import *

def extractPixels(inputs, masks, grid, **kwargs):

    applier = Applier(defaultGrid=grid, **kwargs)
    for i, input in enumerate(inputs):
        name = 'input'+str(i)
        applier.setFlowInput(name=name, input=input)

    for i, mask in enumerate(masks):
        name = 'mask' + str(i)
        applier.setFlowMask(name=name, mask=mask)

    results = applier.apply(operatorType=_ExtractPixels, inputs=inputs, masks=masks)
    return results

class _ExtractPixels(ApplierOperator):

    def ufunc(self, inputs, masks):

        # calculate overall mask
        marray = self.full(value=True)
        nothingToExtract = False
        for i, mask in enumerate(masks):
            name = 'mask' + str(i)
            imarray = self.flowMaskArray(name=name, mask=mask)
            np.logical_and(marray, imarray, out=marray)
            if not marray.any():
                nothingToExtract = True
                break

        # extract values for all masked pixels
        result = list()
        for i, input in enumerate(inputs):
            name = 'input' + str(i)
            if nothingToExtract:
                zsize = self.flowInputZSize(name=name, input=input)
                dtype = np.uint8
                profiles = np.empty(shape=(zsize, 0), dtype=dtype)
            else:
                array = self.flowInputArray(name=name, input=input)
                profiles = array[:, marray[0]]
            result.append(profiles)
        return result

    @staticmethod
    def aggregate(blockResults, grid, inputs, *args, **kwargs):
        result = list()
        for i, input in enumerate(inputs):
            profilesList = [r[i] for r in blockResults]
            profiles = np.concatenate(profilesList, axis=1)
            result.append(profiles)
        return result
