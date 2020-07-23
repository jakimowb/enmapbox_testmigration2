from os.path import basename, exists

import numpy as np

from osgeo import gdal
from qgis._core import QgsRasterLayer, QgsRectangle, QgsCoordinateReferenceSystem

from hubdsm.core.extent import Extent
from hubdsm.core.grid import Grid
from hubdsm.core.location import Location
from hubdsm.core.projection import Projection
from hubdsm.core.raster import Raster
from hubdsm.core.resolution import Resolution
from hubdsm.core.size import Size


def importPrismaL2D(filenameHe5: str, filenameSpectral: str = None) -> gdal.Dataset:
    '''Return raster with correct interleave and spectral information (wavelength and FWHM).'''

    assert isPrismaL2DProduct(filenameHe5=filenameHe5)
    assert isinstance(filenameHe5, str)
    if filenameSpectral is None:
        filenameSpectral = filenameHe5.replace('.he5', '.tif')
    assert isinstance(filenameSpectral, str)

    ds: gdal.Dataset = gdal.Open(filenameHe5)
    meta = ds.GetMetadata()

    filenameSwir = ds.GetSubDatasets()[0][0]
    assert filenameSwir.endswith('SWIR_Cube')
    filenameVnir = ds.GetSubDatasets()[2][0]
    assert filenameVnir.endswith('VNIR_Cube')

    arrayVnir = gdal.Open(filenameVnir).ReadAsArray()
    arraySwir = gdal.Open(filenameSwir).ReadAsArray()
    array = np.vstack((np.transpose(arrayVnir, [1, 0, 2]), np.transpose(arraySwir, [1, 0, 2])))
    xmin = float(meta['Product_ULcorner_easting'])
    ymax = float(meta['Product_ULcorner_northing'])
    xmax = float(meta['Product_LRcorner_easting'])
    ymin = float(meta['Product_LRcorner_northing'])
    size = Size(x=xmax - xmin, y=ymax - ymin)
    resolution = Resolution(x=size.x / array.shape[2], y=size.y / array.shape[1])
    grid = Grid(
        extent=Extent(ul=Location(x=xmin, y=ymax), size=size),
        resolution=resolution,
        projection=Projection.fromEpsg(int(meta['Epsg_Code']))
    )

    Raster.createFromArray(array=array, grid=grid, filename=filenameSpectral)

    #    r = Raster.open(filenameLatitude)

    assert 0
    # r'HDF5:"C:\Users\janzandr\Downloads\PRS_L2C_STD_20200209102459_20200209102503_0001\PRS_L2C_STD_20200209102459_20200209102503_0001.he5"://HDFEOS/SWATHS/PRS_L2C_AEX/Geolocation_Fields/Latitude'

    # read metadata
    import xml.etree.ElementTree as ET
    root = ET.parse(filenameMetadataXml).getroot()

    wavelength = [item.text for item in root.findall('specific/bandCharacterisation/bandID/wavelengthCenterOfBand')]
    fwhm = [item.text for item in root.findall('specific/bandCharacterisation/bandID/FWHMOfBand')]
    gains = [item.text for item in root.findall('specific/bandCharacterisation/bandID/GainOfBand')]
    offsets = [item.text for item in root.findall('specific/bandCharacterisation/bandID/OffsetOfBand')]

    # create VRTs
    filename = filenameMetadataXml.replace('-METADATA.XML', '-SPECTRAL_IMAGE.TIF')
    assert exists(filename)
    ds = gdal.Open(filename)
    options = gdal.TranslateOptions(format='VRT')
    ds: gdal.Dataset = gdal.Translate(destName=filenameSpectral, srcDS=ds, options=options)
    ds.SetMetadataItem('wavelength', '{' + ', '.join(wavelength[:ds.RasterCount]) + '}', 'ENVI')
    ds.SetMetadataItem('wavelength_units', 'nanometers', 'ENVI')
    ds.SetMetadataItem('fwhm', '{' + ', '.join(fwhm[:ds.RasterCount]) + '}', 'ENVI')

    rasterBands = [ds.GetRasterBand(i + 1) for i in range(ds.RasterCount)]
    rasterBand: gdal.Band
    for i, rasterBand in enumerate(rasterBands):
        rasterBand.SetScale(float(gains[i]))
        rasterBand.SetOffset(float(offsets[i]))
        rasterBand.FlushCache()
    return ds


def isPrismaL2DProduct(filenameHe5: str):
    # r'PRS_L2D_STD_20200327103506_20200327103510_0001.he5'
    basename_ = basename(filenameHe5)
    valid = True
    valid &= basename_.startswith('PRS_L2D')
    valid &= basename_.endswith('.he5')
    return valid
