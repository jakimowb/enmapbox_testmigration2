import os
import hub.file
import hub.gdal.api
import hub.gdal.util
import hub.rs.virtual


class Cube():

    def __init__(self, folder):
        self.folder = folder

    def getMGRSTiles(self):
        mgrstiles = list()
        for utmzone in os.listdir(self.folder):
            for mgrstile in os.listdir(os.path.join(self.folder, utmzone)):
                mgrstiles.append(mgrstile)
        return mgrstiles

    def getFolder(self, mgrstile):
        return os.path.join(self.folder, mgrstile[0:2], mgrstile)

    def getFiles(self, mgrstile, extension=None):

        if extension is not None:
            pattern = '*.'+extension
            filenames = hub.file.filesearch(self.getFolder(mgrstile), pattern)
            basenames = [os.path.basename(filename) for filename in filenames]
            result = {os.path.splitext(key)[0]:value for key,value in zip(basenames, filenames)}
        else:
            imgFilenames = self.getFiles(mgrstile, 'img')
            vrtFilenames = self.getFiles(mgrstile, 'vrt')
            result = dict()
            for key in imgFilenames.keys()+vrtFilenames.keys():
                if imgFilenames.has_key(key): result[key] = imgFilenames[key]
                else: result[key] = vrtFilenames[key]

        return result

    def readStackData(self, mgrstile, extension=None, names=None):
        datafiles = self.getFiles(mgrstile, extension)
        if not names: names = datafiles.keys()
        data = hub.collections.Bunch({key:hub.gdal.api.readCube(filename) for key,filename in datafiles.items() if key in names})
        return data

    def readStackMeta(self, mgrstile, extension=None, names=None):

        datafiles = self.getFiles(mgrstile, extension)
        if not names: names = datafiles.keys()
        meta = hub.collections.Bunch({key:hub.gdal.api.GDALMeta(filename) for key,filename in datafiles.items() if key in names})


        '''
        metafiles = self.getFiles(mgrstile, 'json')
        if not names: names = metafiles.keys()
        meta = hub.collections.Bunch({key:hub.file.restoreJSON(filename) for key,filename in metafiles.items() if key in names or key=='meta'})
        '''
        return meta

    def readStack(self, mgrstile, extension='img', names=None):
        return (self.readStackData(mgrstile, extension=extension, names=names), self.readStackMeta(mgrstile, names=names))

    def writeStackData(self, mgrstile, data, srsfilename=None):
        for key in data.keys():
            hub.gdal.api.writeCube(data[key], os.path.join(self.getFolder(mgrstile), key+'.img'), srsfilename)

    def writeStackMeta(self, mgrstile, meta):
        for key, gdalMeta in meta.items():
            gdalMeta.writeMeta(os.path.join(self.getFolder(mgrstile), key+'.img'))

    def writeStack(self, mgrstile, data, meta, srsfilename=None):
        self.writeStackData(mgrstile, data, srsfilename)
        self.writeStackMeta(mgrstile, meta)

    def getSRS(self, mgrstile, extension='img'):
        # use the first found image as SRS file
        return self.getFiles(mgrstile, extension).values()[0]

def test():
    cube = Cube(r'\\141.20.140.91\NAS_Work\EuropeanDataCube\testCaseAR\cubes')
    meta = cube.readStackMeta('32UNB',names=['band4','band8'])
    print(meta)

if __name__ == '__main__':
    test()