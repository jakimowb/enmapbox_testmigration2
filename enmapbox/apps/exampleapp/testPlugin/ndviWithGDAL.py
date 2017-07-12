def ndviWithGDAL(infile, outfile, progress=None):

    from osgeo import gdal
    from numpy import array, float32, argmin, abs

    if progress is None:
        progress = PrintProgress()

    # open spectral image and get wavelength infos
    inDS = gdal.Open(infile)
    wavelength = inDS.GetMetadataItem('wavelength', 'ENVI')
    wavelengthUnits = inDS.GetMetadataItem('wavelength_units', 'ENVI')

    if wavelength is None or wavelengthUnits is None:
        raise Exception('missing wavelength information')

    wavelength = array([float(v) for v in wavelength.strip()[1:-1].split(',')])
    if wavelengthUnits.lower() == 'micrometers':
        wavelength *= 1000

    # locate red and nir wavebands
    redBandNumber = int(argmin(abs(wavelength - 655.)) + 1)
    nirBandNumber = int(min(abs(wavelength - 865.)) + 1)
    progress.setText('red band found at band number: ' + str(redBandNumber))
    progress.setText('nir band found at band number: ' + str(nirBandNumber))

    # calculate ndvi
    red = inDS.GetRasterBand(redBandNumber).ReadAsArray().astype(float32)
    nir = inDS.GetRasterBand(nirBandNumber).ReadAsArray().astype(float32)
    ndvi = (nir - red) / (nir + red)

    # apply no data mask
    mask = red == inDS.GetRasterBand(redBandNumber).GetNoDataValue()
    mask += nir == inDS.GetRasterBand(nirBandNumber).GetNoDataValue()
    noDataValue = -1.
    ndvi[mask] = noDataValue

    # write ndvi to file
    driver = gdal.GetDriverByName('ENVI')
    creationOptions = ['INTERLEAVE=BSQ']
    ysize, xsize = ndvi.shape
    bands = 1
    eType = gdal.GDT_Float32
    outDS = driver.Create(outfile, xsize, ysize, bands, eType, creationOptions)
    outDS.GetRasterBand(1).WriteArray(ndvi)
    outDS.GetRasterBand(1).SetNoDataValue(noDataValue)
    outDS.SetProjection(inDS.GetProjection())
    outDS.SetGeoTransform(inDS.GetGeoTransform())
    outDS = None

class PrintProgress(object):
    def setText(self, v): print(v)
    def setInfo(self, v): pass
    def setProgress(self, v): pass
