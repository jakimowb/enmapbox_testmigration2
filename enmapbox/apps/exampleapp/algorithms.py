

def dummyAlgorithm(*args, **kwds):
    print('Dummy Algorithm started')
    if len(args) > 0:
        print('Print arguments:')
        for i, arg in enumerate(args):
            print('Arg{}:{}'.format(i+1,str(arg)))
    else:
        print('No arguments defined')
    if len(kwds) > 0:
        print('Print keywords:')
        for k, v in kwds.items():
            print('Kwd {}={}'.format(k,str(v)))
    else:
        print('No keywords defined')
    print('Dummy Algorithm finished')


def ndvi(infile, outfile, redBandNumber=None, nirBandNumber=None, progress=None):

    from osgeo import gdal
    from numpy import array, float32, argmin, abs

    if progress is None:
        progress = PrintProgress()

    # open spectral image and get wavelength infos
    inDS = gdal.Open(infile)

    if redBandNumber is None or nirBandNumber is None:
        wavelength = inDS.GetMetadataItem('wavelength', 'ENVI')
        wavelengthUnits = inDS.GetMetadataItem('wavelength_units', 'ENVI')

        if wavelength is None or wavelengthUnits is None:
            raise Exception('missing wavelength information')

        wavelength = array([float(v) for v in wavelength.strip()[1:-1].split(',')])
        if wavelengthUnits.lower() == 'micrometers':
            wavelength *= 1000

        # locate missing red / nir waveband
        if redBandNumber is None:
            redBandNumber = int(argmin(abs(wavelength - 655.)) + 1)
            progress.setText('red band found at band number: ' + str(redBandNumber))

        if nirBandNumber is None:
            nirBandNumber = int(min(abs(wavelength - 865.)) + 1)
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
