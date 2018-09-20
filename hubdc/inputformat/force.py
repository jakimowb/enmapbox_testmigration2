from hubdc.core2 import *
import fnmatch

LND_BAND_NAMES = ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']
LNDS = ['LND04', 'LND05', 'LND07', 'LND08']
LND04, LND05, LND07, LND08 = LNDS
SEN2A = 'SEN2A'

def sentinel2Raster(folder, date, ext, geometry, tilingScheme):
    raster = Raster(name='{}_SEN2A'.format(date), date=Date.parse(date))
    for subproduct, bands in [('BOA', 10), ('CLD', 1), ('HOT', 1), ('QAI', 1), ('VZN', 1)]:
        filename = join(folder, '{}_LEVEL2_SEN2A_{}{}'.format(date, subproduct, ext))
        for index in range(bands):

            name = subproduct
            wavelength = None
            if subproduct == 'BOA':
                name = ['Blue', 'Green', 'Red', 'RedEdge1', 'RedEdge2', 'RedEdge3', 'NIR', 'NIR2', 'SWIR1', 'SWIR2'][index]
                wavelength = [0.492, 0.560, 0.665, 0.704, 0.740, 0.783, 0.833, 0.865, 1.614, 2.202][index]

            raster.addBand(band=Band(filename=filename, index=index, mask=None, name=name, date=date,
                                     wavelength=wavelength, geometry=geometry, tilingScheme=tilingScheme))

    raster = raster.updateMask(mask=raster.select(0).not_equal(-9999))
    return raster

def landsatRaster(folder, date, sensor, ext, geometry, tilingScheme):
    assert sensor in LNDS
    raster = Raster(name='{}_{}'.format(date, sensor), date=date)
    for subproduct, bands in [('BOA', 6), ('CLD', 1), ('HOT', 1), ('QAI', 1), ('VZN', 1)]:
        filename = join(folder, '{}_LEVEL2_{}_{}{}'.format(date, sensor, subproduct, ext))
        for index in range(bands):

            wavelength = None
            name = subproduct
            if subproduct == 'BOA':
                name = ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2'][index]
                wavelength = {'LND04': [0.486, 0.571, 0.659, 0.839, 1.679, 2.217],
                              'LND05': [0.486, 0.570, 0.660, 0.838, 1.677, 2.217],
                              'LND07': [0.478, 0.561, 0.661, 0.834, 1.650, 2.208],
                              'LND08': [0.482, 0.561, 0.654, 0.864, 1.609, 2.201]}[sensor][index]

            raster.addBand(band=Band(filename, index=index, mask=None, name=name, date=date,
                                     wavelength=wavelength, geometry=geometry, tilingScheme=tilingScheme))
    raster = raster.updateMask(mask=raster.select(0).not_equal(-9999))
    return raster


tilingScheme = TilingScheme()
tilingScheme.addTile(name='X0069_Y0043',
                     extent=Extent(xmin=4526026.0, xmax=4556026.0, ymin=3254919.5, ymax=3284919.5,
                                   projection=Projection(wkt='PROJCS["ETRS89/LAEAEurope",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["latitude_of_center",52],PARAMETER["longitude_of_center",10],PARAMETER["false_easting",4321000],PARAMETER["false_northing",3210000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","3035"]]')))
tilingScheme.addTile(name='X0070_Y0043',
                     extent=Extent(xmin=4556026.0, xmax=4586026.0, ymin=3254919.5, ymax=3284919.5,
                                   projection=Projection(wkt='PROJCS["ETRS89/LAEAEurope",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],PROJECTION["Lambert_Azimuthal_Equal_Area"],PARAMETER["latitude_of_center",52],PARAMETER["longitude_of_center",10],PARAMETER["false_easting",4321000],PARAMETER["false_northing",3210000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","3035"]]')))
def collections(folder, ext):
    sensors = LNDS + [SEN2A]
    rasters = {sensor: dict() for sensor in sensors}
    geometries = {sensor: dict() for sensor in sensors}
    patterns = {sensor: '*_LEVEL2_{}_BOA{}'.format(sensor, ext) for sensor in sensors}
    for tilename in tilingScheme.tiles():
        extent = tilingScheme.extent(name=tilename)
        for filename in listdir(join(folder, tilename)):
            for sensor in sensors:
                if fnmatch.fnmatch(filename, patterns[sensor]):
                    date = filename[:8]
                    key = date
                    if key not in rasters[sensor]:
                        if sensor in LNDS:
                            raster = landsatRaster(folder=folder, date=Date.parse(date), sensor=sensor, ext=ext, geometry=None, tilingScheme=tilingScheme)
                        else:
                            raster = sentinel2Raster(folder=folder, date=Date.parse(date), ext=ext, geometry=None, tilingScheme=tilingScheme)
                        rasters[sensor][key] = raster
                    if key in geometries[sensor]:
                        geometries[sensor][key] = extent.union(other=geometries[sensor][key])
                    else:
                        geometries[sensor][key] = extent

    for sensor in rasters:
        for key, raster in rasters[sensor].items():
            for band in raster.bands():
                band._geometry = geometries[sensor][key]

    collections = list()
    for sensor in sensors:
        collection = Collection()
        collection._rasters = list(rasters[sensor].values())
        collections.append(collection)

    class L2Collections(object):
        def __init__(self, collections):
            self._collections = collections

        def _get(self, i):
            c = self._collections[i]
            assert isinstance(c, Collection)
            return c

        def __iter__(self):
            for c in self._collections:
                assert isinstance(c, Collection)
                yield c

        @property
        def l4(self):
            return self._get(0)

        @property
        def l5(self):
            return self._get(1)

        @property
        def l7(self):
            return self._get(2)

        @property
        def l8(self):
            return self._get(3)

        @property
        def s2(self):
            return self._get(4)

    return L2Collections(collections)