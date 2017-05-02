from os import listdir
from os.path import join, basename, isdir, exists
from osgeo import ogr, osr
from hubdc.model.PixelGrid import PixelGrid

class LandsatArchiveParser:

    @classmethod
    def getScenes(cls, archive, footprints):
        for footprint in footprints:
            path, row = footprint[:3], footprint[3:]
            if exists(join(archive, path, row)):
                for scene in listdir(join(archive, path, row)):
                    folder = join(archive, path, row, scene)
                    if isdir(folder):
                        yield folder

    @classmethod
    def getFilenames(cls, archive, footprints, names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask']):

        scenes = list(cls.getScenes(archive, footprints))
        for name in names:
            filenames = list()
            for scene in scenes:
                if name == 'cfmask':
                    filenames.append(join(scene, basename(scene) + '_cfmask.img'))
                elif basename(scene).startswith('LT') or basename(scene).startswith('LE'):
                    index = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'].index(name)
                    filenames.append(join(scene, basename(scene)+['_sr_band' + str(i) for i in [1, 2, 3, 4, 5, 7]][index])+'.img')
                elif basename(scene).startswith('LC8'):
                    index = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'].index(name)
                    filenames.append(join(scene, basename(scene)+['_sr_band' + str(i) for i in [1, 2, 3, 4, 5, 6, 7]][index])+'.img')
                else:
                    continue
            yield filenames
