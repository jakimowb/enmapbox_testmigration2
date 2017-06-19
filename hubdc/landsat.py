from os import listdir
from os.path import join, basename, dirname, isdir, exists
from osgeo import ogr, osr
from hubdc.model import PixelGrid

class LandsatArchiveParser:

    @classmethod
    def getFootprints(cls, archive):
        footprints = list()
        for path in listdir(archive):
            if (len(path) != 3 or path < '000' or path > '999'): continue
            for row in listdir(join(archive, path)):
                if (len(row) != 3 or row < '000' or row > '999'): continue
                footprints.append(path+row)
        return footprints

    @classmethod
    def getScenes(cls, archive, footprints):
        scenes = list()
        for footprint in footprints:
            path, row = footprint[:3], footprint[3:]
            if exists(join(archive, path, row)):
                for scene in listdir(join(archive, path, row)):
                    folder = join(archive, path, row, scene)
                    if isdir(folder):
                        scenes.append(folder)
        return scenes

    @classmethod
    def getFilenames(cls, archive, footprints, names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask']):

        def findExtension(filenameWithoutExtension):
            for extension in ['.img', '.tif']:
                filename = filenameWithoutExtension + extension
                if exists(filename):
                    return filename
            return filenameWithoutExtension + '.???'

        scenes = cls.getScenes(archive, footprints)
        filenames = dict()
        for name in names:
            filenames[name] = list()
            for scene in scenes:
                if name == 'cfmask':
                    filenames[name].append(findExtension(join(scene, basename(scene) + '_cfmask')))
                elif basename(scene).startswith('LT') or basename(scene).startswith('LE'):
                    index = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'].index(name)
                    filenames[name].append(findExtension(join(scene, basename(scene)+['_sr_band' + str(i) for i in [1, 2, 3, 4, 5, 7]][index])))
                elif basename(scene).startswith('LC8'):
                    index = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'].index(name)
                    filenames[name].append(findExtension(join(scene, basename(scene)+['_sr_band' + str(i) for i in [1, 2, 3, 4, 5, 6, 7]][index])))
                else:
                    raise Exception('unknown landsat scene: '+scene)

        # skip currupted scenes
        valid = [True]*len(scenes)
        for name in names:
            for i, filename in enumerate(filenames[name]):
                if valid[i] is False: continue
                if filename.endswith('???'):
                    valid[i] = False
                    print('skipped invalid scene: '+dirname(filename))
        if not all(valid):
            filenames = {name : [f for f, v in zip(filenames[name], valid) if v] for name in names}

        return [filenames[name] for name in names]

class LandsatCollection1ArchiveParser:

    @classmethod
    def getFootprints(cls, archive):
        footprints = list()
        for path in listdir(archive):
            if (len(path) != 3 or path < '000' or path > '999'): continue
            for row in listdir(join(archive, path)):
                if (len(row) != 3 or row < '000' or row > '999'): continue
                footprints.append(path+row)
        return footprints

    @classmethod
    def getScenes(cls, archive, footprints):
        scenes = list()
        for footprint in footprints:
            path, row = footprint[:3], footprint[3:]
            if exists(join(archive, path, row)):
                for scene in listdir(join(archive, path, row)):
                    folder = join(archive, path, row, scene)
                    if isdir(folder):
                        scenes.append(folder)
        return scenes

    @classmethod
    def getFilenames(cls, archive, footprints, names=['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'cfmask']):

        def findFile(folder, pattern):
            import fnmatch
            import os

            for bname in os.listdir(folder):
                for extension in ['.img', '.tif', '']:
                    if fnmatch.fnmatch(bname, pattern+extension):
                        return join(folder, bname)

            return join(folder, '*' + pattern + '*.???')

        scenes = cls.getScenes(archive, footprints)
        filenames = dict()
        names = ['MTL.txt']+names
        for name in names:
            filenames[name] = list()
            for scene in scenes:
                if name not in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']:
                    filenames[name].append(findFile(folder=scene, pattern='*'+name))
                elif basename(scene).startswith('LT') or basename(scene).startswith('LE'):
                    index = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2'].index(name)
                    filenames[name].append(findFile(folder=scene, pattern=['*sr_band' + str(i) for i in [1, 2, 3, 4, 5, 7]][index]))
                elif basename(scene).startswith('LC'):
                    index = ['aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2'].index(name)
                    filenames[name].append(findFile(folder=scene, pattern=['*sr_band' + str(i) for i in [1, 2, 3, 4, 5, 6, 7]][index]))
                else:
                    raise Exception('unknown landsat scene: '+scene)

        # skip currupted scenes
        valid = [True]*len(scenes)
        for name in names:
            for i, filename in enumerate(filenames[name]):
                if valid[i] is False: continue
                if filename.endswith('???'):
                    valid[i] = False
                    print('skipped invalid scene: '+dirname(filename))
        if not all(valid):
            filenames = {name : [f for f, v in zip(filenames[name], valid) if v] for name in names}

        filenamesOrdered = [filenames[name] for name in names]
        mtl = filenamesOrdered[0]
        images = filenamesOrdered[1:]
        return mtl, images
