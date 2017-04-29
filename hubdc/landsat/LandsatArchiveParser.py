from os import listdir
from os.path import join, basename, isdir

class LandsatArchiveParser:

    @classmethod
    def getScenes(clf, archive, footprints):
        for footprint in footprints:
            path, row = footprint[:3], footprint[3:]
            for scene in listdir(join(archive, path, row)):
                folder = join(archive, path, row, scene)
                if isdir(folder):
                    yield folder

    @classmethod
    def getFilenames(clf, archive, footprints, names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask']):

        scenes = list(clf.getScenes(archive, footprints))
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

if __name__ == '__main__':
    cfmask, red, nir = LandsatArchiveParser.getFilenames(archive=r'C:\Work\data\gms\landsat',
                                                  footprints=['194024'], names=['cfmask', 'red', 'nir'])

