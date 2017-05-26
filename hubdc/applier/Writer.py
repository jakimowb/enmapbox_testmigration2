from hubdc import CreateFromArray

class Writer():

    WRITE_ARRAY, SET_META, SET_NODATA, CLOSE_DATASETS, CLOSE_WRITER = range(5)

    @classmethod
    def handleTask(cls, task, args, outputDatasets):
        if task is cls.WRITE_ARRAY:
            cls.writeArray(outputDatasets, *args)
        elif task is cls.SET_META:
            cls.setMetadataItem(outputDatasets, *args)
        elif task is cls.SET_NODATA:
            cls.setNoDataValue(*args)
        elif task is cls.CLOSE_DATASETS:
            cls.closeDatasets(outputDatasets, *args)
        elif task is cls.CLOSE_WRITER:
            pass
        else:
            raise ValueError(str(task))

    @staticmethod
    def createDataset(outputDatasets, filename, array, grid, format, creationOptions):
        outputDatasets[filename] = CreateFromArray(pixelGrid=grid, array=array,
                                                   dstName=filename,
                                                   format=format,
                                                   creationOptions=creationOptions)

    @staticmethod
    def closeDatasets(outputDatasets, createEnviHeader):
        for filename, ds in outputDatasets.items():
            outputDataset = outputDatasets.pop(filename)
            if createEnviHeader:
                outputDataset.writeENVIHeader()
            outputDataset.flushCache()
            outputDataset.close()

    @staticmethod
    def writeArray(outputDatasets, filename, array, subgrid, maingrid, format, creationOptions):

        if filename not in outputDatasets:
            Writer.createDataset(outputDatasets, filename, array, maingrid, format, creationOptions)
        else:
            outputDatasets[filename].writeArray(array=array, pixelGrid=subgrid)
            outputDatasets[filename].flushCache()

    @staticmethod
    def setMetadataItem(outputDatasets, filename, key, value, domain):
        outputDatasets[filename].setMetadataItem(key=key, value=value, domain=domain)
        if key=='band names' and domain=='ENVI':
            for dsBand, bandName in zip(outputDatasets[filename], value):
                dsBand.setDescription(bandName)

    @staticmethod
    def setNoDataValue(outputDatasets, filename, value):
        for dsBand in outputDatasets[filename]:
            dsBand.setNoDataValue(value)
