import os
from eb import Image

class Landsat:

    def __init__(self, folder):
        self.folder = folder
        self.sceneId = os.path.basename(folder)
        self.MTLFile = os.path.join(self.folder, self.sceneId + '_MTL.txt')
        self.ESPAFile = os.path.join(self.folder, self.sceneId + '.xml')
        self.FMaskFile = os.path.join(self.folder, self.sceneId + '_cfmask.img')

    def SRBandFile(self, i):
        return os.path.join(self.folder, self.sceneId + '_sr_band' + str(i) + '.txt')

    def TOABandFile(self, i):
        return os.path.join(self.folder, self.sceneId + '_toa_band' + str(i) + '.txt')


class Landsat8(Landsat):

    @property
    def BlueFile(self): return self.SRBandFile(2)

    @property
    def GreenFile(self): return self.SRBandFile(3)

    @property
    def RedFile(self): return self.SRBandFile(4)

    @property
    def NIRFile(self): return self.SRBandFile(5)

    @property
    def SWIR1File(self): return self.SRBandFile(6)

    @property
    def SWIR2File(self): return self.SRBandFile(7)


if __name__ == '__main__':

    lc8 = Landsat8(r'C:\Work\data\LC81930232015084LGN00')
    lc8Image = Image(lc8.BlueFile)
    lc8Image.