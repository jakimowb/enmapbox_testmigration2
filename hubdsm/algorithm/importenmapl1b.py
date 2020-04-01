from os.path import splitext
from osgeo import gdal


def importEnmapL1B(filenameMetadataXml: str, filenameVrt: str = None):
    '''Create VRT for given L1B product.'''
    if filenameVrt is None:
        filenameFull = filenameMetadataXml.replace('METADATA.XML', 'EnMAP-Box_FULL.vrt')
        filenameVnir = filenameMetadataXml.replace('METADATA.XML', 'EnMAP-Box_VNIR.vrt')
        filenameSwir = filenameMetadataXml.replace('METADATA.XML', 'EnMAP-Box_SWIR.vrt')
    else:
        assert filenameVrt.lower().endswith('.vrt')
        head, ext = splitext(filenameVrt)
        filenameVnir = f'{head}_VNIR{ext}'
        filenameSwir = f'{head}_SWIR{ext}'

    # read metadata
    import xml.etree.ElementTree as ET
    root = ET.parse(filenameMetadataXml).getroot()
    wavelength = [item.text for item in root.findall('specific/bandCharacterisation/bandID/wavelengthCenterOfBand')]
    fwhm = [item.text for item in root.findall('specific/bandCharacterisation/bandID/FWHMOfBand')]
    gains = [item.text for item in root.findall('specific/bandCharacterisation/bandID/GainOfBand')]
    offsets = [item.text for item in root.findall('specific/bandCharacterisation/bandID/OffsetOfBand')]

    # create VRTs
    # - VNIR
    ds = gdal.Open(filenameMetadataXml.replace('-METADATA.XML', '-SPECTRAL_IMAGE_VNIR.GEOTIFF'))
    options = gdal.TranslateOptions(format='VRT')
    dsVnir: gdal.Dataset = gdal.Translate(destName=filenameVnir, srcDS=ds, options=options)
    dsVnir.SetMetadataItem('wavelength', '{'+', '.join(wavelength[:dsVnir.RasterCount]) + '}', 'ENVI')
    dsVnir.SetMetadataItem('wavelength_units', 'nanometers', 'ENVI')
    dsVnir.SetMetadataItem('fwhm', '{'+', '.join(fwhm[:dsVnir.RasterCount]) + '}', 'ENVI')
    # - SWIR
    ds = gdal.Open(filenameMetadataXml.replace('-METADATA.XML', '-SPECTRAL_IMAGE_SWIR.GEOTIFF'))
    options = gdal.TranslateOptions(format='VRT')
    dsSwir: gdal.Dataset = gdal.Translate(destName=filenameSwir, srcDS=ds, options=options)
    assert len(wavelength[dsVnir.RasterCount:]) == dsSwir.RasterCount
    assert len(fwhm[dsVnir.RasterCount:]) == dsSwir.RasterCount
    dsSwir.SetMetadataItem('wavelength', '{'+', '.join(wavelength[dsVnir.RasterCount:]) + '}', 'ENVI')
    dsSwir.SetMetadataItem('wavelength_units', 'nanometers', 'ENVI')
    dsSwir.SetMetadataItem('fwhm', '{'+', '.join(fwhm[dsVnir.RasterCount:]) + '}', 'ENVI')

    # manipulate VRTs
    del dsVnir
    del dsSwir
    index = 0
    for filename in [filenameVnir, filenameSwir]:
        with open(filename) as file:
            lines = file.readlines()
        lines2 = list()
        for line in lines:
            lines2.append(line)
            if '<Description>' in line:
                lines2.append(f'    <Scale>{gains[index]}</Scale>\n')
                lines2.append(f'    <Offset>{offsets[index]}</Offset>\n')
                index += 1
        with open(filename, 'w') as file:
            file.writelines(lines2)
