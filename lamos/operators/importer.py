from __future__ import division
from lamos.types import Applier, ApplierInput, ApplierOutput, MGRSArchive, MGRSFootprint
import numpy
from hub.timing import tic, toc
import hub.ogr.util, os, hub.gdal.util
from hub.gdal.api import GDALMeta

class LucasImportApplier:

    def __init__(self, inshapefile, outfolder, footprints, buffer):

        self.inshapefile = inshapefile
        self.outfolder = outfolder
        self.footprints = footprints
        self.buffer = buffer


    def apply(self):

        class_names =  ['unclassified', 'artificial land', 'cropland',  'forest broadleaved', 'forest coniferous', 'forest mixed', 'shrubland', 'grasland',    'bare land',   'water',   'wetland',   'snow ice']
        class_lookup = [0, 0, 0,        255, 0, 0,         255, 255, 0, 0, 230, 0,            0, 100, 150,         0, 150, 50,     255, 150, 0, 210, 210, 100, 150, 150, 150, 0, 0, 255, 170, 0, 170, 255, 255, 255]
        classes = len(class_names)

        for mgrsFootprint in [MGRSFootprint.fromShp(name) for name in self.footprints]:
            print(mgrsFootprint.name)
            outfile = os.path.join(self.outfolder, mgrsFootprint.subfolders(), 'lucas', 'lucas.shp')
            outfile2 = outfile.replace('.shp', '_lc4.img')
            if os.path.exists(outfile2):
                continue

            # clip shp
            ul, lr = mgrsFootprint.getBoundingBox()
            clipdst = '-clipdst ' + str(ul[0]) + ' ' + str(ul[1]) + ' ' + str(lr[0]) + ' ' + str(lr[1]) + ' '
            t_srs = '-t_srs EPSG:326' + mgrsFootprint.utm + ' '
            options = clipdst + t_srs
            hub.ogr.util.ogr2ogr(outfile=outfile, infile=self.inshapefile, options=options)

            # rasterize cliped shape
            a = '-a LC4_ID '
            a_nodata = '-a_nodata 0 '
            init = '-init 0 '
            tr = '-tr 30 30 '
            ul, lr = mgrsFootprint.getBoundingBox(buffer=self.buffer, snap='landsat')
            te = '-te ' + str(ul[0]) + ' ' + str(min(ul[1], lr[1])) + ' ' + str(lr[0]) + ' ' + str(max(ul[1], lr[1])) + ' '
            ot = '-ot Byte '
            of = '-of ENVI '
            options = a + a_nodata + te + tr + ot + of
            hub.gdal.util.gdal_rasterize(outfile=outfile2, infile=outfile, options=options)
            meta = GDALMeta(outfile2)
            meta.setMetadataItem('file_type', 'ENVI Classification')
            meta.setMetadataItem('classes', classes)
            meta.setMetadataItem('class_names', class_names)
            meta.setMetadataItem('class lookup', class_lookup)
            meta.setNoDataValue(0)
            meta.writeMeta(outfile2)

class AndreyDaraImportApplier:

    def __init__(self, inshapefile, outfolder, footprints, buffer):

        self.inshapefile = inshapefile
        self.outfolder = outfolder
        self.footprints = footprints
        self.buffer = buffer


    def apply(self):

        class_names =  ['unclassified', 'non-cropland', 'cropland']
        class_lookup = [0, 0, 0,        0, 255, 0,      255, 0, 0]
        classes = len(class_names)

        for mgrsFootprint in [MGRSFootprint.fromShp(name) for name in self.footprints]:
            print(mgrsFootprint.name)
            outfile = os.path.join(self.outfolder, mgrsFootprint.subfolders(), 'reference', '2007.shp')
            outfile2 = outfile.replace('.shp', '_class.img')
            if os.path.exists(outfile2):
                continue

            # clip shp
            ul, lr = mgrsFootprint.getBoundingBox()
            clipdst = '-clipdst ' + str(ul[0]) + ' ' + str(ul[1]) + ' ' + str(lr[0]) + ' ' + str(lr[1]) + ' '
            t_srs = '-t_srs EPSG:326' + mgrsFootprint.utm + ' '
            options = clipdst + t_srs
            hub.ogr.util.ogr2ogr(outfile=outfile, infile=self.inshapefile, options=options)

            # rasterize cliped shape
            a = '-a class_ '
            a_nodata = '-a_nodata 0 '
            init = '-init 0 '
            tr = '-tr 30 30 '
            ul, lr = mgrsFootprint.getBoundingBox(buffer=self.buffer, snap='landsat')
            te = '-te ' + str(ul[0]) + ' ' + str(min(ul[1], lr[1])) + ' ' + str(lr[0]) + ' ' + str(max(ul[1], lr[1])) + ' '
            ot = '-ot Byte '
            of = '-of ENVI '
            options = a + a_nodata + te + tr + ot + of
            hub.gdal.util.gdal_rasterize(outfile=outfile2, infile=outfile, options=options)
            meta = GDALMeta(outfile2)
            meta.setMetadataItem('file_type', 'ENVI Classification')
            meta.setMetadataItem('classes', classes)
            meta.setMetadataItem('class_names', class_names)
            meta.setMetadataItem('class lookup', class_lookup)
            meta.setNoDataValue(0)
            meta.writeMeta(outfile2)

def test():

    MGRSFootprint.shpRoot = r'C:\Work\data\gms\gis\MGRS_100km_1MIL_Files'

    inshapefile = r'C:\Work\data\gms\lucas\eu27_lucas_2012_subset1.shp'
    outfolder = r'C:\Work\data\gms\lucasMGRS'
    mgrsFootprints = ['32UPC', '32UQC', '33UTT', '33UUT']

    importer = LucasImportApplier(inshapefile=inshapefile, outfolder=outfolder, footprints=mgrsFootprints, buffer=300)
    importer.apply()


def testAD():

    MGRSFootprint.shpRoot = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files'

    inshapefile = r'\\141.20.140.91\NAS_Projects\Baltrak\Andrey\SHP\2007.shp'
    outfolder = r'\\141.20.140.91\NAS_Work\EuropeanDataCube\4ad\referenceMGRS'
    mgrsFootprints = ['41ULS','41ULT','41ULU','41UMS','41UMT','41UMU','41UMV','41UNS','41UNT','41UNU','41UNV','41UPS','41UPT','41UPU','41UPV']

    importer = AndreyDaraImportApplier(inshapefile=inshapefile, outfolder=outfolder, footprints=mgrsFootprints, buffer=300)
    importer.apply()


if __name__ == '__main__':

    tic()
    testAD()
    toc()
