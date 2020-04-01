from os.path import splitext
from typing import Tuple

from osgeo import gdal


def importEnmapL1B(
        filenameMetadataXml: str, filenameVnir: str = None, filenameSwir: str = None
) -> Tuple[gdal.Dataset, gdal.Dataset]:
    '''Return VNIR and SWIR VRT datasets with spectral information (wavelength and FWHM) and data gains/offsets.'''

    if filenameVnir is None:
        filenameVnir = filenameMetadataXml.replace('METADATA.XML', 'EnMAP-Box_VNIR.vrt')
    if filenameSwir is None:
        filenameSwir = filenameMetadataXml.replace('METADATA.XML', 'EnMAP-Box_SWIR.vrt')
    assert filenameVnir.lower().endswith('.vrt')
    assert filenameSwir.lower().endswith('.vrt')

    # read metadata
    import xml.etree.ElementTree as ET
    root = ET.parse(filenameMetadataXml).getroot()
    wavelength = [item.text for item in root.findall('specific/bandCharacterisation/bandID/wavelengthCenterOfBand')]
    fwhm = [item.text for item in root.findall('specific/bandCharacterisation/bandID/FWHMOfBand')]
    gains = [item.text for item in root.findall('specific/bandCharacterisation/bandID/GainOfBand')]
    offsets = [item.text for item in root.findall('specific/bandCharacterisation/bandID/OffsetOfBand')]

    # create VRTs
    ds = gdal.Open(filenameMetadataXml.replace('-METADATA.XML', '-SPECTRAL_IMAGE_VNIR.GEOTIFF'))
    options = gdal.TranslateOptions(format='VRT')
    dsVnir: gdal.Dataset = gdal.Translate(destName=filenameVnir, srcDS=ds, options=options)
    dsVnir.SetMetadataItem('wavelength', '{'+', '.join(wavelength[:dsVnir.RasterCount]) + '}', 'ENVI')
    dsVnir.SetMetadataItem('wavelength_units', 'nanometers', 'ENVI')
    dsVnir.SetMetadataItem('fwhm', '{'+', '.join(fwhm[:dsVnir.RasterCount]) + '}', 'ENVI')

    ds = gdal.Open(filenameMetadataXml.replace('-METADATA.XML', '-SPECTRAL_IMAGE_SWIR.GEOTIFF'))
    options = gdal.TranslateOptions(format='VRT')
    dsSwir: gdal.Dataset = gdal.Translate(destName=filenameSwir, srcDS=ds, options=options)
    dsSwir.SetMetadataItem('wavelength', '{'+', '.join(wavelength[dsVnir.RasterCount:]) + '}', 'ENVI')
    dsSwir.SetMetadataItem('wavelength_units', 'nanometers', 'ENVI')
    dsSwir.SetMetadataItem('fwhm', '{'+', '.join(fwhm[dsVnir.RasterCount:]) + '}', 'ENVI')

    rasterBands = list()
    rasterBands.extend(dsVnir.GetRasterBand(i+1) for i in range(dsVnir.RasterCount))
    rasterBands.extend(dsSwir.GetRasterBand(i+1) for i in range(dsSwir.RasterCount))
    rasterBand: gdal.Band
    for i, rasterBand in enumerate(rasterBands):
        rasterBand.SetScale(float(gains[i]))
        rasterBand.SetOffset(float(offsets[i]))
        rasterBand.FlushCache()

    return dsVnir, dsSwir
