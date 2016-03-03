import osgeo.gdal as gdal
import gdalconst

def openVRT(vrtfile):
    dataset = gdal.Open(vrtfile, gdalconst.GA_ReadOnly)
    return dataset

def readBand(dataset, pos, xoff, yoff, xsize, ysize):
    band = dataset.GetRasterBand(int(pos)+1)
    array = band.ReadAsArray(int(xoff), int(yoff), int(xsize), int(ysize))
    band = None
    return array

def readCube(dataset, xoff, yoff, xsize, ysize):
    subset = dataset.ReadAsArray(int(xoff), int(yoff), int(xsize), int(ysize))
    return subset

if __name__ == '__main__':
    vrtfile = r'A:\vrt\z21Landsat.clipped.vrt'
    dataset = openVRT(vrtfile)
    subset = readCube(dataset, 0, 0, 10,10)
    print(subset)
    dataset = None

