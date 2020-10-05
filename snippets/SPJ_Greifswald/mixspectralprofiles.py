
from osgeo import gdal
from enmapbox.testing import TestCase
from qgis.PyQt.QtCore import *


class Scripts(TestCase):

    def test_createProfiles(self):

        from enmapbox.gui import SpectralLibrary, SpectralProfile
        from enmapbox.gui.utils import file_search
        from enmapbox.externals.qps.speclib.io.asd import ASDSpectralLibraryIO, ASDBinaryFile
        import pathlib
        import os
        import numpy as np

        # Ordner mit den '*.asd.ref' Dateien
        dirRefl = pathlib.Path(r'F:\Temp\SPJ_Greifswald\Feldspektren') / 'Reflexion'
        # CSV mit den Angaben der Mischungen
        pathMixRecipe = pathlib.Path(__file__).parent / 'mischungen.csv'
        dirRoot = pathMixRecipe.parent
        os.makedirs(dirRoot, exist_ok=True)
        assert dirRefl.is_dir()
        assert pathMixRecipe.is_file()
        pathMixResultGPKG = dirRoot / 'mischungsergebnisse.gpkg'
        pathMixResultCSV  = dirRoot / 'mischungsergebnisse.csv'

        asd_files_ref = list(file_search(dirRefl, '*.asd.ref', recursive=True))

        rezept = np.recfromcsv(pathMixRecipe, encoding='utf-8')
        gruppen = np.unique(rezept.gruppe)

        speclib = SpectralLibrary()
        speclib.startEditing()

        for gruppe in gruppen:
            print(f'Mische Gruppe {gruppe}')
            i_grp = np.where(rezept.gruppe == gruppe)[0]
            basenames = [f'{n}.asd.ref' for n in rezept.basename[i_grp]]
            weights = rezept.gewicht[i_grp]
            nweights = weights / weights.sum()
            description = rezept.beschreibung[i_grp]
            asd_files = [p for p in asd_files_ref if os.path.basename(p) in basenames]
            profiles = ASDSpectralLibraryIO.readFrom(asd_files)
            assert len(profiles) == len(asd_files)
            for p, d in zip(profiles, description):
                if d != '':
                    p.setName(f'{p.name()} {d}')

            #speclib.addProfiles(profiles)

            mixed_profile = sum([p*w for p, w in zip(profiles, nweights)])
            assert isinstance(mixed_profile, SpectralProfile)
            mixed_profile.setName(f'Mischung Gruppe {gruppe}')
            speclib.addProfiles(mixed_profile)

        speclib.commitChanges()


        speclib.write(pathMixResultGPKG)
        speclib.write(pathMixResultCSV)

        dirTmpImages = dirRoot / 'tmpImages'
        os.makedirs(dirTmpImages, exist_ok=True)
        pathTmpImage = dirTmpImages / 'speclib2rasterimage.tif'
        source_images = speclib.writeRasterImages(pathTmpImage)
        from hubflow.core import SensorDefinition, Raster
        print(SensorDefinition.predefinedSensorNames())
        sensor: SensorDefinition = SensorDefinition.fromPredefined('Sentinel_2_Multi-Spectral_Instrument')

        from enmapbox.gui import parseWavelength
        resampledImages = []
        for pathSrc in source_images:

            # workaround https://bitbucket.org/hu-geomatics/enmap-box/issues/531/hubflow-fails-to-read-envi-style
            ds: gdal.Dataset = gdal.Open(pathSrc.as_posix(), gdal.GA_Update)
            wl, wlu = parseWavelength(ds)
            enviWL = f"{{{','.join([str(v) for v in wl])}}}"

            print(f'Wavelength: {enviWL}')
            print(f'Wavelength units: {wlu}')

            ds.SetMetadataItem('wavelength', enviWL, 'ENVI')
            ds.SetMetadataItem('wavelength_units', 'Nanometers', 'ENVI')
            ds.FlushCache()
            del ds

            # resample to Sentinel-2
            pathDst = dirTmpImages / f'{os.path.splitext(pathSrc.name)[0]}2sentinel.tif'
            raster = Raster(pathSrc.as_posix())
            sensor.resampleRaster(pathDst.as_posix(), raster, warpOptions=['SRC_METHOD=NO_GEOTRANSFORM'])
            resampledImages.append(pathDst)

        speclibS2 = SpectralLibrary()
        speclibS2.startEditing()
        for img in resampledImages:
            ds: gdal.Dataset = gdal.Open(img.as_posix())
            positions = []
            for x in range(ds.RasterXSize):
                for y in range(ds.RasterYSize):
                    positions.append(QPoint(x, y))
            sl: SpectralLibrary = SpectralLibrary.readFromRasterPositions(img, positions)
            assert len(sl) > 0
            speclibS2.addSpeclib(sl)
        speclibS2.commitChanges()

        pathMixResultS2GPKG = dirRoot / 'mischungsergebnisseS2.gpkg'
        pathMixResultS2CSV = dirRoot / 'mischungsergebnisseS2.csv'
        speclibS2.write(pathMixResultS2GPKG)
        speclibS2.write(pathMixResultS2CSV)
