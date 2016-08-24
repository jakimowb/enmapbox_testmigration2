__author__ = 'geo_beja'

import sys
import os
import fnmatch
import subprocess
import re
import copy
import numpy as np
import time, datetime
from osgeo import ogr, gdal, osr, gdal_array
import shutil
import gzip
import collections
import multiprocessing
import itertools

mkdir = lambda p : os.makedirs(p, exist_ok=True)

def initializeGDAL(requiredGDALDrivers=None,requiredOGRDrivers=None):
    registerErrorHandler()
    errors = list()
    if isinstance(requiredGDALDrivers, list):
        missing = [name for name in requiredGDALDrivers if gdal.GetDriverByName(name) is None]
        if len(missing) > 0:
            errors.append('Missing raster/ GDAL driver(s):')
            errors.extend(missing)

    if isinstance(requiredOGRDrivers, list):
        missing = [name for name in requiredOGRDrivers if ogr.GetDriverByName(name) is None]
        if len(missing) > 0:
            errors.append('Missing vector / OGR driver(s):')
            errors.extend(missing)

    if len(errors) > 0:
        raise Exception('\n'.join(errors))

def registerErrorHandler():
    print('Register GDAL error handler')
    gdal.UseExceptions()
    gdal.PushErrorHandler(gdal_error_handler)

def gdal_error_handler(err_class, err_num, err_msg):
    errtype = {
            gdal.gdalconst.CE_None:'None',
            gdal.gdalconst.CE_Debug:'Debug',
            gdal.gdalconst.CE_Warning:'Warning',
            gdal.gdalconst.CE_Failure:'Failure',
            gdal.gdalconst.CE_Fatal:'Fatal'
    }
    err_msg = err_msg.replace('\n',' ')
    err_class = errtype.get(err_class, 'None')
    info = ['GDAL Message:']
    info.append('  {} Number: {}'.format(err_class, err_num))
    info.append('  {} Message: {}'.format(err_class, err_msg))
    info = '\n'.join(info)
    if err_class in ['None','Debug']:
        print(info)
    elif err_class in ['Warning']:
        print(info, file=sys.stderr)
    else:
        raise Exception(info)



def raster2ENVISpectralLibrary(path_src, path_sli, path_mask = None, data_ignore_value = 0, spectra_names = None):
    """
    Converts a 2-D raster image into an 1-D ENVI Spectral Library.
    :param path_src:
    :param path_sli: output path of
    :param path_mask: a mask file to exclude single pixels in path_src
    :return:
    """
    dsSrc = gdal.Open(path_src)

    nb = dsSrc.RasterCount
    band_names = list()
    dataSrc = dsSrc.ReadAsArray()


    mask = np.ndarray(dataSrc[0,:].shape, dtype='bool')
    mask.fill(True)
    for b in range(0, nb):
        band = dsSrc.GetRasterBand(b+1)
        band_names.append(band.GetDescription())
        div = band.GetNoDataValue()
        if div:
            mask &= (dataSrc[b,:] != div)

    if path_mask:
        dsMsk = gdal.Open()
        for b in range(1,dsMsk.RasterCount+1):
            mskBand = dsMsk.GetRasterBand(b)
            div = mskBand.GetNoDataValue()
            if not div:
                div = data_ignore_value
            mask &= (mskBand.ReadAsArray() != div)


    mask = mask.flatten()
    dataSrc = np.reshape(dataSrc, (nb, -1))
    dataSrc = dataSrc[:, np.where(mask)[0]]
    nSpectra = dataSrc.shape[1]

    if spectra_names:
        assert len(spectra_names) == nSpectra

    ds = gdal_array.SaveArray(dataSrc, path_sli, format='ENVI')
    if spectra_names:
        ds.SetMetadataItem('spectra names', ','.join(spectra_names),  'ENVI')
    ds = None
    hdr = read_envi_header(path_sli)
    hdr['file type'] = 'ENVI Spectral Library'
    write_envi_header(path_sli, hdr)




def changeVRTFileDrives(vrtFile, oldPathRegex, newPath):
    '''
    This method changes the source drive paths within a VRt file
    :param dirVRT:
    :param oldDrive:
    :param newDrive:
    :return:
    '''
    if type(oldPathRegex) == str:
        oldPathRegex = re.compile(oldPathRegex)

    if os.path.isdir(vrtFile):
        vrtFiles = file_search(vrtFile, '*.vrt', recursive=True)
        print('Replace path in {} vrt files...'.format(len(vrtFiles)))
        for vrtFile in vrtFiles:
            changeVRTFileDrives(vrtFile, oldPathRegex, newPath)
    else:
        regRepl = re.compile(oldPathRegex)
        regSrc = re.compile(r'<SourceFilename')
        lines = []
        with open(vrtFile, mode='r') as f:
            lines = f.readlines()

        for i in range(0,len(lines)):
            if regSrc.search(lines[i]) and regRepl.search(lines[i]):
                nl = re.sub(regRepl, newPath,lines[i])
                lines[i] = nl

        with open(vrtFile, mode='w') as f:
            f.writelines(lines)


def error_callback(execption):
    print('Error callback:', file=sys.stderr)
    print(execption, file=sys.stderr)


def createPyramids_parallel(files, levels=[2,4,8,16] \
        , vrtSubLevels=None \
        , r='nearest' \
        , ro=True \
        , b=None \
        , clean=False \
        , n_processes=None \
        ):

    if n_processes is None:
        n_processes = max([1,int(multiprocessing.cpu_count() * 0.5)])

    Pool = multiprocessing.Pool(processes=n_processes)
    kwds = {'vrtSubLevels':vrtSubLevels, 'levels':levels, 'clean':clean, 'b':b,'ro':ro, 'r':r}

    for file in files:
        Pool.apply_async(createPyramids, (file,), kwds, None, error_callback)
    Pool.close()
    print('Wait for finishing all processes...')
    Pool.join()

def createPyramids(file \
        , levels=[2,4,8,16] \
        , vrtSubLevels=None \
        , r='nearest' \
        , ro=True \
        , b=None \
        , clean=False \
        ):

    if type(file) == list or type(file) == set:
        for file in file:
            createPyramids(file, levels=levels, vrtSubLevels=vrtSubLevels, r=r, ro=ro, clean=clean)

    if not os.path.isfile(file):
        raise Exception('{} is not a file'.format(file))

    #check for VRT
    isVRT = file.lower().endswith('.vrt')
    ds = gdal.Open(file)

    if ds.GetDriver().ShortName == gdal.GetDriverByName('VRT').ShortName and vrtSubLevels is not None:

        vrtSrcFiles = getVRTSourceFiles(file)
        createPyramids(vrtSrcFiles, levels=vrtSubLevels)
        levels = vrtSubLevels

    ds = None

    cmd = 'gdaladdo '
    if clean:
        cmd += ' -clean'
    else:
        if r:
            ' -r {} '.format(r)
        if ro :
            cmd += ' -ro '
        if b is not None:
            cmd += ' -b '+ ' -b '.join(map(str, b))

    cmd += ' "{}"'.format(file)
    cmd += ' '+' '.join(map(str,levels))

    print(cmd)
    val = subprocess.check_call(cmd, shell=True)
    print(val)




def file_search(rootDir, wildcard, recursive=False, ignoreCase=False):
    if not os.path.isdir(rootDir):
        print("Path is not a directory:{}".format(rootDir), file=sys.stderr)

    results = []

    for root, dirs, files in os.walk(rootDir):
        for file in files:
            if (ignoreCase and fnmatch.fnmatch(file.lower(), wildcard.lower())) \
                    or fnmatch.fnmatch(file, wildcard):
                results.append(os.path.join(root, file))
        if not recursive:
            break
    return results


def createImageSubsets(srcFiles, refShp, dstDir, dstPrefix='subset.', sql=None, dstSRS=None):
    shp = ogr.Open(refShp)
    if shp is None:
        raise Exception('Can not open ' + refShp)

    layers = []
    for i in range(0, shp.GetLayerCount()):
        lyr = shp.GetLayerByIndex(i)
        layers.append(lyr.GetName())

    print('Layer names: {}'.format(layers))

    # get extent
    if sql is not None:
        lyr = shp.ExecuteSQL(sql)
    else:
        lyr = shp.GetLayerByIndex(0)

    if lyr == None:
        raise Exception('Can not open layer')

    lyrSRS = lyr.GetSpatialRef()
    nFeatures = lyr.GetFeatureCount()
    if nFeatures == 0:
        raise Exception('Layer is empty')


    #extent = lyr.GetExtent(1)
    geomColl = ogr.Geometry(ogr.wkbGeometryCollection)
    for feature in lyr:
        geomColl.AddGeometry(feature.GetGeometryRef())
    extent = geomColl.GetEnvelope()

    print('#selected features: {} MBB:{}'.format(nFeatures, extent))


    for srcFile in srcFiles:

        srcRaster = gdal.Open(srcFile)
        if srcRaster == None:
            raise Exception('Can not open ' + srcFile)

        srcSRS = osr.SpatialReference()
        wkt = srcRaster.GetProjection()
        srcSRS.ImportFromWkt(wkt)
        envi_md = srcRaster.GetMetadata_Dict('ENVI')
        src_filelist = srcRaster.GetFileList()
        if dstSRS == None:
            _dstSRS = srcSRS
        else:
            _dstSRS = dstSRS
        dstFile = os.path.join(dstDir, '{}{}'.format(dstPrefix, os.path.basename(srcFile)))

        #
        #convert shape coordinates to raster coordinates
        t = osr.CoordinateTransformation(lyrSRS, _dstSRS)
        ul = t.TransformPoint(min(extent[0:2]), max(extent[2:4]))
        lr = t.TransformPoint(max(extent[0:2]), min(extent[2:4]))

        dstWKT = _dstSRS.ExportToWkt()
        cmd = ['gdalwarp']
        cmd.append('-of ENVI')
        cmd.append('-t_srs ' + dstWKT)
        #-te xmin ymin xmax ymax:
        cmd.append('-te {} {} {} {}'.format(ul[0], lr[1], lr[0], ul[1]))
        cmd.append('-r near')
        cmd.append('-overwrite')
        cmd.append(srcFile)
        cmd.append(dstFile)
        cmd = ' '.join(cmd)
        #cmd = ['gdalbuildvrt','-separate','-input_file_list',pathFileList,path_vrt]


        print(cmd)
        os.makedirs(os.path.dirname(dstFile), exist_ok=True)
        p = subprocess.check_call(cmd)




def translate2ENVI(src_path, dst_path):

    ds = gdal.Open(src_path)
    mdAdd = ds.GetMetadata_Dict()
    ds = None


    cmd = 'gdal_translate -of ENVI {} {}'.format(src_path,dst_path)
    print(cmd)
    val = subprocess.check_call(cmd)

    ds = gdal.Open(dst_path)
    fl = ds.GetFileList()
    ds = None

    pathHdr = list(filter(lambda x: x.lower().endswith('hdr'), fl))[0]

    if not os.path.isfile(pathHdr):
        raise Exception('Can not find header for '+dst_path)

    fw = open(pathHdr, mode='a')
    protected = ['samples','lines','bands','band names','file type','header offset','data type','interleave','byte order' \
                'map info','coordinate system string']

    for mdKey in mdAdd:
        if mdKey not in protected:
            value = str(mdAdd[mdKey])
            if isinstance(mdAdd[mdKey], list) or re.findall('^[^{]+,', value):
                value = '{'+re.sub('[\[\]()]','',value)+'}'
            fw.write('{} = {}\n'.format(mdKey, value))
    fw.close()



def addFeature(lyr, geom, values):
    assert type(lyr) is ogr.Layer
    assert type(geom) is ogr.Geometry
    assert isinstance(values, dict)

    feature = ogr.Feature(lyr.GetLayerDefn())
    feature.SetGeometry(geom)
    for key, value in values.items():
        t = type(value)
        if t is int or np.issubdtype(t, np.integer):
            v = int(value)
        elif t is float or np.issubdtype(t, np.float):
            v = float(value)
        elif t is str or np.issubdtype(t, np.str):
            v = str(value)
        else:
            raise NotImplemented()
        feature.SetField(key, v)
    lyr.CreateFeature(feature)

def createLayer(ds, lyrName, examples, srs=None, geom_type=ogr.wkbPoint):
    """
    Adds a new layer to a OGR DataSource and creates fields with types like in the example data
    :param ds:
    :param lyrName:
    :param examples:
    :param srs:
    :param geom_type:
    :return:
    """
    assert type(ds) is ogr.DataSource
    assert type(lyrName) is str
    assert isinstance(examples, dict)

    lyr = ds.CreateLayer(lyrName, srs=srs, geom_type=geom_type)
    for key, value in examples.items():
        t = type(value)
        oft = ogr.OFTString
        if t is int or np.issubdtype(t, np.integer):
            oft = ogr.OFTInteger
        elif t is float or np.issubdtype(t, np.float):
            oft = ogr.OFTReal
        elif t is str or np.issubdtype(t, np.str):
            oft = ogr.OFTString
        else:
            s = ""
            raise NotImplemented()
        lyr.CreateField(ogr.FieldDefn(key, oft))

    return lyr



def read_envi_header(path):


    ds = gdal.Open(path)
    files = ds.GetFileList()
    ds=None
    pathHDR = [f for f in files if f.lower().endswith('.hdr')][0]

    f = open(pathHDR, 'r')
    lines = f.readlines()
    lines = list(map(lambda x:x.strip(), lines))
    lines = list(filter(lambda x:len(x) > 0, lines))
    f.close()
    if lines[0] != 'ENVI':
        raise IOError('File is not an ENVI Header')
    tags = {}
    i = 0
    try:
        while i < len(lines):
            if lines[i].find('=') == -1:
                i += 1
                continue
            (key, val) = lines[i].split('=')
            key = key.strip()
            val = val.strip()
            if val[0] == '{':
                str = val
                while str[-1] != '}':
                    i += 1
                    str += lines[i].strip()

                if re.match('(description|coordinate system string|map info)', key):
                    tags[key] = str[1:-1]
                else:
                    vals = str[1:-1].split(',')
                    for j in range(len(vals)):
                        vals[j] = vals[j].strip()
                    tags[key] = vals
            else:
                tags[key] = val
            i += 1
    except:
        raise IOError("Error while reading ENVI file header.")
    return tags

def setNoDataValue(ds, nodata_value):
    ds = _getDS(ds, GA = gdal.GA_Update)
    for band in [ds.GetRasterBand(b+1) for b in range(ds.RasterCount)]:
        band.SetNoDataValue(nodata_value)
    if ds.GetDriver().ShortName == 'ENVI':
        if nodata_value is not None:
            ds.SetMetadataItem('data ignore value', str(nodata_value), 'ENVI')

    ds.FlushCache()

def setBandNames(ds, bandnames):
    ds = _getDS(ds, GA = gdal.GA_Update)
    assert len(bandnames) == ds.RasterCount
    for i, bandName in enumerate(bandnames):
        ds.GetRasterBand(i+1).SetDescription(bandnames[i])

    drvName = ds.GetDriver().ShortName
    if drvName == 'ENVI':
        bn = readBandNames(ds)
        bn = '{'+','.join(bn)+'}'
        ds.SetMetadataItem('band names', bn , 'ENVI')
    ds.FlushCache()

def GPX2PointShape(gpxFiles, dstShp):
    """

    :param gpxFiles: list of gpx files.
    :param dstShp:  path of output shape file
    """
    drvDst = ogr.GetDriverByName('ESRI Shapefile')
    drvMEM = ogr.GetDriverByName('Memory')

    if os.path.exists(dstShp):
        drvDst.DeleteDataSource(dstShp)

    mem = drvMEM.CreateDataSource('')
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    memLyr = mem.CreateLayer('points', srs, ogr.wkbPoint)

    lDef = None

    for pathGPX in gpxFiles:

        src = ogr.Open(pathGPX)
        if None is src:
            raise Exception('Can not open ' + pathGPX)

        for srcLyr in src:
            lName = srcLyr.GetName()
            nFeatures = srcLyr.GetFeatureCount()
            if nFeatures == 0 or None is re.search(r"(way|track_)points", lName, re.IGNORECASE):
                continue

            srcDef = srcLyr.GetLayerDefn()
            if lDef is None:
                # copy standard GPX fields
                for i in range(0, srcDef.GetFieldCount()):
                    fDef = srcDef.GetFieldDefn(i)
                    fName = fDef.GetName()
                    fTypeName = fDef.GetTypeName()
                    if fTypeName == 'DateTime':
                        dtField = ogr.FieldDefn(fName, ogr.OFTString)
                        memLyr.CreateField(dtField)
                    else:
                        memLyr.CreateField(fDef)

                #add field to contain the source file name
                srcGPXField = ogr.FieldDefn('srcfile', ogr.OFTString)
                memLyr.CreateField(srcGPXField)
                lDef = memLyr.GetLayerDefn()

                #print attributes
                print('Output fields')
                for i in range(0, lDef.GetFieldCount()):
                    fdef = lDef.GetFieldDefn(i)
                    print('{} : "{}" type: {}'.format(i, fdef.GetName(), fdef.GetTypeName()))

            # copy the features from src file to output file
            print('Copy {} features from layer {} src file {}'.format(nFeatures, lName, pathGPX))
            for srcFeature in srcLyr:
                newFeature = ogr.Feature(lDef)
                #copy src data + geometry
                newFeature.SetFrom(srcFeature)
                newFeature.SetField('srcfile', pathGPX)
                memLyr.CreateFeature(newFeature)

    # todo: sort layer features and remove duplicates

    #write MEM to disk
    print('Write memory data to ' + pathShp)
    drvDst.CopyDataSource(mem, pathShp, ['OVERWRITE=YES'])

def getVRTSourceFiles(path_vrt):
    import xml.etree.ElementTree as ET
    vrtXML = ET.parse(path_vrt)

    rootDir = os.path.dirname(path_vrt)

    srcFiles = set()
    for x in vrtXML.findall('.//SimpleSource') + vrtXML.findall('.//ComplexSource'):
        srcFile = x.find('./SourceFilename')
        if srcFile is not None:
            attr = srcFile.attrib
            path = srcFile.text
            isRelative = ('relativeToVRT' in attr) and attr['relativeToVRT'] == '1'
            if isRelative:
                path = os.path.join(rootDir, path.replace('/','\\'))
            srcFiles.add(path)

    return srcFiles



def rasterizeLayer(refRaster, dsVector, layerName, lyrField, layer=None, pathDst=None):

    if type(refRaster) is not gdal.Dataset:
        refRaster = gdal.Open(refRaster)


    if layer is None:
        if type(dsVector) is not ogr.DataSource:
            dsVector = ogr.Open(dsVector)

        layerNames = [dsVector.GetLayerByIndex(i).GetName() for i in range(dsVector.GetLayerCount())]
        if layerName is not None:
            assert layerName in layerNames
        else:
            layerName = layerNames[0]

        layer = dsVector.GetLayerByName(layerName)

    srs_srs = layer.GetSpatialRef()
    srs_dst = osr.SpatialReference()
    srs_dst.ImportFromWkt(refRaster.GetProjection())
    ldefn = layer.GetLayerDefn()
    geomType = ldefn.GetGeomType()
    fieldNames = []
    for i in range(0, ldefn.GetFieldCount()):
        fdef = ldefn.GetFieldDefn(i)
        fieldNames.append(fdef.GetName())

    assert lyrField in fieldNames

    fdefn = ldefn.GetFieldDefn(fieldNames.index(lyrField))
    ogrType = fdefn.GetType()
    ogrTypeName = fdefn.GetTypeName()
    mapTypeOGR  = [ogr.OFTInteger, ogr.OFTReal, ogr.OFTString]
    mapTypeGDAL = [gdal.GDT_Int16, gdal.GDT_Float32, gdal.GDT_Float32]
    eType = mapTypeGDAL[mapTypeOGR.index(ogrType)]

    if not srs_dst.IsSame(srs_srs):
        trans = osr.CoordinateTransformation(srs_srs, srs_dst)
        drvMemory = ogr.GetDriverByName('Memory')
        dsM = drvMemory.CreateDataSource('')
        dsM.CreateLayer(layerName, srs = srs_dst, geom_type=geomType)
        lyr = dsM.GetLayerByName(layerName)
        lyr.CreateField(fdefn)

        for feat in layer:
            geom = feat.GetGeometryRef().Clone()
            geom.Transform(trans)
            outFeature = ogr.Feature(lyr.GetLayerDefn())
            outFeature.SetGeometry(geom)
            #print('copy gid {}'.format(feat.GetField(lyrField)))
            outFeature.SetField(lyrField, feat.GetField(lyrField))
            lyr.CreateFeature(outFeature)


        layer = None
        layer = lyr


    ns = refRaster.RasterXSize
    nl = refRaster.RasterYSize
    drvMEM = gdal.GetDriverByName('MEM')
    dsR = drvMEM.Create('', ns, nl, eType=eType)
    dsR.SetProjection(refRaster.GetProjection())
    dsR.SetGeoTransform(refRaster.GetGeoTransform())

    band = dsR.GetRasterBand(1)
    band.Fill(-1)
    print('Burn polygons...')
        #gdal.RasterizeLayer(refRaster,[1], lyr, None, None, [0], ["ATTRIBUTE={}".format('gid')])
    err = gdal.RasterizeLayer(dsR,[1], layer, options=["ATTRIBUTE={}".format(lyrField),"ALL_TOUCHED=FALSE"])
    assert err in [gdal.CE_None, gdal.CE_Warning]

    data = dsR.GetRasterBand(1).ReadAsArray()
    #r2 = [data.min(), data.max()]
    if pathDst:
        print('Write '+pathDst)
        drvENVI = gdal.GetDriverByName('ENVI')
        drvENVI.CreateCopy(pathDst, dsR)
    return data


def createENVI_MOS(path_mos, path_vrt=None, src_files=None):
    # check inputs
    if path_vrt is not None:
        raise NotImplemented()

    elif src_files is not None:
        raise NotImplemented()
    else:
        raise NameError('Please specify either path_vrt or src_files')

    pass



class VRTBuilder(object):
    def __init__(self):
        self.virtualBands = list()
        self.maskband = None

    def addMaskBand(self, SourceImages, bandname=None):
        assert self.maskband is None, 'MaskBand already defined'

        if not isinstance(SourceImages, list):
            tmp = list()
            tmp.append(SourceImages)
            SourceImages = tmp

        for img in SourceImages:
            assert type(img) is VRTBuilderImageSource

        self.maskband = SourceImages

    def addVirtualBandsFromImage(self, src_path, bandnames=None):
        assert type(src_path) is str and os.path.exists(src_path)
        ds = gdal.Open(src_path)
        assert ds is not None

        bands = ds.RasterCount

        if bandnames:
            assert len(bandnames) == bands, 'Please provide a band name for each of the {} input band'.format(bands)
        else:
            bandnames = list()
            bn = os.path.basename(src_path)
            for b in range(1, bands+1):
                name = ds.GetRasterBand(b).GetDescription()
                if name == '':
                    name = '{}:{}'.format(bn,b)
                bandnames.append(name)


        for b in range(1, bands+1):
            vBandSrc = VRTBuilderImageSource(src_path, b)
            self.addVirtualBand(vBandSrc, bandname=bandnames[b-1])

    def addVirtualBand(self, SourceImages, bandname=None):

        if not isinstance(SourceImages, list):
            tmp = list()
            tmp.append(SourceImages)
            SourceImages = tmp

        for img in SourceImages:
            assert type(img) is VRTBuilderImageSource

        if bandname is None:
            bandname = 'Band {}'.format(len(self.virtualBands)+1)

        self.virtualBands.append((SourceImages, bandname))

    def writeVRT(self, pathVRT, gdalbuildvrtkw=None, nodatavalue=None):

        srcImgs = set()
        for srcBandList, _ in self.virtualBands:
            for srcBand in srcBandList:
                srcImgs.add(srcBand.path)
        if self.maskband is not None:
            for srcBand in self.maskband:
                srcImgs.add((srcBand.path))

        srcImgs = list(srcImgs)

        #write UNC paths

        map = dict()
        is_windows = sys.platform.lower().startswith('win')
        if is_windows:
            cmd = subprocess.Popen('net use', shell=True, stdout=subprocess.PIPE)
            lines = [line.decode(encoding='iso8859-1') for line in cmd.stdout]

            for line in lines:
                if re.search(r'[A-Z]:[ ]+[\\]{2}', line):
                    parts = re.split(r'[ ]+', line)
                    drive = parts[1]
                    path =  parts[2]
                    map[drive] = path


        is_windows_drive = re.compile(r'^[A-Z]:')
        def getUNCPath(path):
            path = os.path.normpath(path)

            if is_windows:
                match = is_windows_drive.search(path)
                if match:
                    path = map[match.group()] + path[2:]

            return path

        srcImgs = [getUNCPath(p) for p in srcImgs]


        pathTmp = pathVRT+'.tmpfilelist.txt'

        fw = open(pathTmp, mode='w')
        for srcFile in srcImgs:
            fw.write('{}\n'.format(srcFile))
        fw.close()
        cmd = 'gdalbuildvrt '
        if gdalbuildvrtkw:
            for key in gdalbuildvrtkw:
                cmd += ' '+key + ' '
        cmd +=' -overwrite -separate -input_file_list "{}" "{}"'.format(pathTmp, pathVRT)
        print(cmd)
        val = subprocess.check_call(cmd, shell=True)
        os.remove(pathTmp)



        #modify XML
        #1. read image related info
        import xml.etree.ElementTree as ET
        xmlstring = open(pathVRT).read()
        xmlstring = re.sub('xmlns[^=]*="[^"]+"', '', xmlstring, count=1)
        XML = ET.fromstring(xmlstring)

        dt = XML.find('./VRTRasterBand').attrib['dataType']
        #del VRTBand1

        INFO = dict()
        for srcImgXML in XML.findall(".//SimpleSource") + XML.findall(".//ComplexSource"):
            path = srcImgXML.find('./SourceFilename').text
            INFO[path] = copy.deepcopy(srcImgXML)

        #remove existing VRTBands
        for VRTBand in XML.findall('VRTRasterBand'):
            XML.remove(VRTBand)


        if nodatavalue:
            NDV = ET.Element('NoDataValue')
            NDV.text = '{}'.format(nodatavalue)
            NDV.tail=' \n'
            XML.append(NDV)


        #add mask band
        if self.maskband is not None:
            MskBand = ET.Element('MaskBand')
            MskBand.tail = '\n  '
            MskBand.text = '\n  '
            path = getUNCPath(self.maskband[0].path)
            refXML = INFO[path]
            dtMsk = refXML.find('./SourceProperties').attrib['DataType']

            VRTBand = ET.Element('VRTRasterBand')
            VRTBand.attrib['dataType'] = dtMsk
            VRTBand.tail = '\n  '
            VRTBand.text='\n  '

            #add Source Band
            for srcBand in self.maskband:
                path = getUNCPath(srcBand.path)
                band = srcBand.band
                VRTSrcBand = copy.deepcopy(INFO[path])
                VRTSrcBand.find('SourceBand').text = 'mask,'+VRTSrcBand.find('SourceBand').text
                VRTBand.append(VRTSrcBand)
            MskBand.append(VRTBand)
            XML.append(MskBand)


        #add VRTBands according to own definition
        vrt_bands = 0
        for srcBandList, bandName in self.virtualBands:
            vrt_bands += 1
            VRTBand = ET.Element('VRTRasterBand')
            VRTBand.attrib['dataType'] = dt
            VRTBand.attrib['band'] = str(vrt_bands)
            VRTBand.tail = '\n  '
            VRTBandDescription = ET.Element('Description')
            VRTBandDescription.tail = '\n    '
            VRTBandDescription.text = bandName
            VRTBand.append(VRTBandDescription)
            #add Source Bands
            for srcBand in srcBandList:
                path = getUNCPath(srcBand.path)
                band = srcBand.band
                VRTSrcBand = copy.deepcopy(INFO[path])
                VRTSrcBand.find('SourceBand').text = str(band)
                VRTBand.append(VRTSrcBand)
            XML.append(VRTBand)

        ETree = ET.ElementTree(XML)
        ETree.write(pathVRT)




class VRTBuilderImageSource(object):

    def __init__(self, path, band, _skip_test=False):
        assert os.path.exists(path)
        if not _skip_test:
            ds = gdal.Open(path)
            assert ds is not None
            assert ds.GetRasterBand(band) is not None
            ds = None

        self.path = path
        self.band = band





def createVRT(pathVRT, subdatasets, vrt_kwds=None, metadata=None, bandnames=None, gt=None, nodata=None, colorIntRGBBands=None, mode='stack'):
    assert len(subdatasets) > 0, 'Please specify input files'


    assert mode in ['stack','mosaic']

    if not isinstance(subdatasets, list):
        subdatasets = [subdatasets]

    subdatasets = [(readDimensions(p)[2], p) for p in subdatasets]
    ref_nb = subdatasets[0][0]
    for nb, _ in subdatasets:
        assert nb == ref_nb, 'All subdatasets need to have {} bands'.format(ref_nb)

    VRT = VRTBuilder()
    if mode == 'stack':
        l = len(subdatasets) * ref_nb
        if bandnames != None:
            assert len(bandnames) == l, 'Number of bandnames must be {}'.format(l)
        else:
            bandnames = ['Band {}'.format(b+1) for b in range(l)]

        i = 0
        for _, path in subdatasets:
            for b in range(ref_nb):
                VRT.addVirtualBand(VRTBuilderImageSource(path, b+1), bandnames[i])
                i += 1

    elif mode == 'mosaic':
        if bandnames != None:
            assert len(bandnames) == ref_nb
        else:
            bandnames = readBandNames(subdatasets[0][1])

        for b in range(ref_nb):
            VRTBandImages = [VRTBuilderImageSource(path, b+1) for _, path in subdatasets]
            VRT.addVirtualBand(VRTBandImages)

    if vrt_kwds:
        if not isinstance(vrt_kwds, list):
            vrt_kwds = list(vrt_kwds)

    VRT.writeVRT(pathVRT, gdalbuildvrtkw=vrt_kwds)

    parts = os.path.splitext(pathVRT)



    #pathTmp =  parts[0]+'.tmpfilelist.txt'
    #fw = open(pathTmp, mode='w')
    #for srcFile in subdatasets:
    #    fw.write('{}\n'.format(srcFile))
    #fw.close()

    #cmd = 'gdalbuildvrt {} -overwrite -separate -input_file_list "{}" "{}"'.format(gridInfo, pathTmp, pathVRT)

    #print(cmd)
    #val = subprocess.check_call(cmd)

    #if val != 0 or not os.path.exists(pathVRT):
    #    raise Exception('Can not create '+pathVRT)

    ds = gdal.Open(pathVRT, gdal.GA_Update)


    if metadata:
        for key in metadata.keys():
            value = str(metadata[key])
            if isinstance(metadata[key], list):
                value = '{'+re.sub('[\[\]()]','',value)+'}'

            k = key
            if k == 'AcquisitionDate':
                k = 'acquisition time'
            ds.SetMetadataItem(k, value)
    if bandnames:
        b = 1
        for name in bandnames:
            ds.GetRasterBand(b).SetDescription(name)
            b += 1

    if gt:
        _gt = ds.GetGeoTransform()
        if _gt == (0,1,0,0,0,1):
            ds.SetGeoTransform(gt)

    if nodata:
        if len(nodata) == ds.RasterCount:
            for b in range(1, ds.RasterCount+1):
                ds.GetRasterBand(b).SetNoDataValue(nodata[b-1])

    if colorIntRGBBands:
        if len(colorIntRGBBands) != 3:
            raise Exception('colorIntRGBBands must contain 3 band number corresponding to R G B')

        ds.GetRasterBand(colorIntRGBBands[0]).SetColorInterpretation(gdal.GCI_RedBand)
        ds.GetRasterBand(colorIntRGBBands[1]).SetColorInterpretation(gdal.GCI_GreenBand)
        ds.GetRasterBand(colorIntRGBBands[2]).SetColorInterpretation(gdal.GCI_BlueBand)
    #os.remove(pathTmp)

def readDimensions(ds):
    ds = _getDS(ds)
    return ds.RasterXSize, ds.RasterYSize, ds.RasterCount


def readBandArray(ds, band=1):
    if type(ds) is str:
        ds = gdal.Open(ds)

    return ds.GetRasterBand(band).ReadAsArray()

def readNoDataValue(ds):
    return readNoDataValues(ds)[0]

def readNoDataValues(ds):
    ds = _getDS(ds)
    bn = []
    for b in range(1, ds.RasterCount+1):
        bn.append(ds.GetRasterBand(b).GetNoDataValue())
    return bn


def transform_to_square(array, no_data_value):

    if array.ndim == 1:
        nb = 1
        npx = len(array)
    else:
        nb = array.shape[0]
        npx = np.product(array.shape[1:])

    nl = ns = int(np.ceil(np.sqrt(npx)))
    array2 = np.ndarray((nb, int(nl*ns)), dtype=array.dtype)
    array2.fill(no_data_value)
    array2[:,0:npx] = array.reshape((nb, npx))

    return array2.reshape((nb, nl, ns))



def readLabels(ds, band = 1):
    if type(ds) is str:
            ds = gdal.Open(ds)
    return ds.GetRasterBand(band).GetCategoryNames()

readClassNames = readLabels

def readClassColors(ds, band=1):
    if type(ds) is str:
        ds = gdal.Open(ds)
    b = ds.GetRasterBand(band)

    ct = b.GetColorTable()
    result = None
    if ct is not None:
        result = list()
        for i in range(ct.GetCount()):
            c = ct.GetColorEntry(i)
            result.append(c)

    return result


def readClassInfos(ds, band=1):
    if type(ds) is str:
        ds = gdal.Open(ds)

    class_names = readLabels(ds, band=band)
    class_colors = readClassColors(ds, band=band)
    return class_names, class_colors



def readBandNames(ds):
    ds = _getDS(ds)
    return [ds.GetRasterBand(b+1).GetDescription() for b in range(ds.RasterCount)]

def readGeoInfo(dsSrc):
    if type(dsSrc) is str:
        dsSrc = gdal.Open(dsSrc)

    return dsSrc.GetGeoTransform(), dsSrc.GetProjection()

def readAsMask(ds, exclude=[0], include=None):
    '''
    Return a True-False / Boolean mask
    :param ds: path or gdal dataset that has the mask data. By default exclude is set to [0]
    :param exclude: values that are to exclude
    :param include: values that are to include
    :return:
    '''


    if type(ds) is str:
        ds = gdal.Open(ds)
    data = gdal_array.DatasetReadAsArray(ds)
    shape = data.shape
    mask = np.ones(shape, dtype='bool')
    if exclude is not None:
        if not isinstance(exclude, list):
            exclude = [exclude]

        for e in exclude:
            mask = np.logical_and(mask, data == e)
    elif include is not None:
        mask *= False
        if not isinstance(include, list):
            include = [include]

        for i in include:
            mask = np.logical_or(mask, data == i)

    return mask


def SaveArray(array, path, format='ENVI', prototype=None, \
              no_data=None, \
              class_names=None, class_colors=None, \
              band_names=None):

    if array.ndim == 2:
        nb = 1
        nl, ns = array.shape
    else:
        nb, nl, ns = array.shape

    if prototype is None:
        pt = None
    else:
        pt = _getDS(prototype)
        if class_names is None:
            class_names = pt.GetRasterBand(1).GetCategoryNames()
        if class_colors is None:
            class_colors = readClassColors(pt)
        if band_names is None:
            pt_band_names = readBandNames(pt)
            if nb == len(pt_band_names):
                band_names = pt_band_names


    print('Write {}...'.format(path))
    ds = gdal_array.SaveArray(array, path, format=format, prototype=pt)
    nb = ds.RasterCount

    if no_data is not None:
        setNoDataValue(ds, no_data)

    if band_names is not None:
        assert len(band_names) == nb
        for b in range(nb):
            band = ds.GetRasterBand(b+1)
            band.SetDescription(band_names[b])


    has_categorical_data = class_names is not None or class_colors is not None

    if has_categorical_data:
        setClassificationInfo(ds, class_names, label_colors=class_colors)

    #add ENVI format specific values
    if format == 'ENVI':
        if no_data is not None:
            ds.SetMetadataItem('data_ignore_value', str(no_data), 'ENVI')
        if has_categorical_data:
            ds.SetMetadataItem('file_type', 'ENVI Classification', 'ENVI')

    ds.FlushCache()
    return ds

regYYYYDOY = re.compile(r'(19|20)\d{2}[0123]\d{2}') #regex to catch year and DOY
regYYYYMMDD = re.compile(r'(19|20)\d{2}[-.]\d{2}[-.]\d{2}')
regYYYY = re.compile(r'(19|20)\d{2}')
def parseAcquisitionDate(text):
    match = regYYYYMMDD.search(text)
    if match:
        return np.datetime64(match.group())
    match = regYYYYDOY.search(text)
    if match:
        return getDateTime64FromYYYYDOY(match.group())
    match = regYYYY.search(text)
    if match:
        return np.datetime64(match.group())
    return None


def getDateTime64FromYYYYDOY(yyyydoy):
    return getDateTime64FromDOY(yyyydoy[0:4], yyyydoy[4:7])

def getDateTime64FromDOY(year, doy):
        if type(year) is str:
            year = int(year)
        if type(doy) is str:
            doy = int(doy)
        return np.datetime64('{:04d}-01-01'.format(year)) + np.timedelta64(doy-1, 'D')



def getImageDate(ds):
    ds = _getDS(ds)

    path = ds.GetFileList()[0]
    to_check = [os.path.basename(path), os.path.dirname(path)]

    regAcqDate = re.compile(r'(acquisition (time|date|day)|acqdate)', re.I)
    for key, value in ds.GetMetadata_Dict().items():
        if regAcqDate.search(key):
            to_check.insert(0, value)

    for text in to_check:
        date = parseAcquisitionDate(text)
        if date:
            return date

    raise Exception('Can not identify acquisition date of {}'.format(path))


def changeClassColors(ds, color_lut):

    ds = _getDS(ds, GA = gdal.GA_Update)

    class_names, class_colors = readClassInfos(ds)
    for class_name, new_color in color_lut.items():
        if class_name in class_names:
            class_colors[class_names.index(class_name)] = new_color

    setClassificationInfo(ds, class_names, label_colors=class_colors)



def setClassificationInfo(ds, label_names, label_values=None, label_colors=None, b=1):
    """
    Adds the classification scheme to an image.
    :param ds: gdal.Dataset or path to raster image.
    :param label_names: label names, corresponding to
    :param label_values: the class integer value. By default [0,1,... nclasses-1]
    :param label_colors: list of RGB or RGBA tuples. By default a rainbow color stretch is used with label 0 = black.
    :param b: band number of the raster band to append the categorical labels.
    :return:
    """
    ds = _getDS(ds, GA=gdal.GA_Update)

    band = ds.GetRasterBand(b)
    assert b is not None

    n = len(label_names)

    if label_colors:
        assert len(label_colors) == n
        for i, c in enumerate(label_colors):
            v = list(c)
            if len(v) == 3:
                v.append(255) #add alpha dimension
            assert len(v) == 4, 'Color tuple has {} values'.format(len(v))
            label_colors[i] = tuple(v)
    else:
        import matplotlib.cm
        label_colors = list()
        cmap = matplotlib.cm.get_cmap('brg', n)
        for i in range(n):
            if i == 0:
                c = (0,0,0, 255)
            else:
                c = tuple([int(255*c) for c in cmap(i)])
            label_colors.append(c)


    if label_values:
        assert len(label_values) == n
    else:
        label_values = [i for i in range(n)]

    CT = gdal.ColorTable()
    names = list()
    for value in sorted(label_values):
        i = label_values.index(value)
        names.append(label_names[i])
        CT.SetColorEntry(value, label_colors[i])

    band.SetCategoryNames(names)
    band.SetColorTable(CT)
    band.FlushCache()

    drvName = ds.GetDriver().ShortName
    if drvName == 'ENVI':
        class_lookup = list(itertools.chain.from_iterable([CT.GetColorEntry(i)[0:3] for i in range(CT.GetCount())]))
        class_lookup = '{'+','.join(['{}'.format(int(c)) for c in class_lookup])+'}'
        band.SetMetadataItem('class_lookup', class_lookup, 'ENVI')
        band.SetMetadataItem('class lookup', class_lookup, 'ENVI')
        ds.SetMetadataItem('class_lookup', class_lookup, 'ENVI')
        ds.SetMetadataItem('class lookup', class_lookup, 'ENVI')
    ds.FlushCache()


def setSpatialRef(dsDst, proj, trans):
    '''
    Sets the projection and geotransformation
    :param dsDst:
    :param proj:
    :param trans:
    :return:
    '''
    if type(dsDst) is str:
        dsDst = gdal.Open(dsDst, gdal.GA_Update)
    dsDst.SetProjection(proj)
    dsDst.SetGeoTransform(trans)

def getSpatialRef(dsSrc):
    '''
    returns the projection and geotransformation
    :param dsSrc: path or dataset
    :return:
    '''
    dsSrc = _getDS(dsSrc)
    proj  = dsSrc.GetProjection()
    trans = dsSrc.GetGeoTransform()
    return proj, trans

def copySpatialRef(dsSrc, dsDst):
    dsSrc = _getDS(dsSrc)
    dsDst = _getDS(dsDst)
    if dsSrc.RasterXSize != dsDst.RasterXSize or \
       dsSrc.RasterYSize != dsDst.RasterYSize:
        raise Exception('Spatial dimensions in px does not match! ({},{}) vs ({},{})'.format(\
            dsSrc.RasterXSize, dsSrc.RasterYSize, \
            dsDst.RasterXSize, dsDst.RasterYSize))

    dsDst.SetProjection(dsSrc.GetProjection())
    dsDst.SetGeoTransform(dsSrc.GetGeoTransform())


def compress_envi_file(path):
    ds = gdal.Open(path)
    files = ds.GetFileList()
    m = ds.GetMetadataItem('file compression','ENVI')
    if m is not None and int(m) == 1:
            return
    ds = None

    path_img = files[0]
    import stuff
    tic = stuff.time_tic()
    print('Compress {}...'.format(path_img))
    path_hdr = [f for f in files if f.lower().endswith('.hdr')][0]
    path_tmp = path_img + '.{}{}.tmp'.format(datetime.date.today(), time.time())
    os.rename(path_img, path_tmp)

    with open(path_tmp, 'rb') as f_in:
        with gzip.open(path_img, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    with open(path_hdr, 'a') as file:
        file.write('file compression = 1 \n')
    os.remove(path_tmp)

    stuff.time_toc(tic)
    s = ""
    pass


def readExtent(ds):

    if type(ds) is str:
        ds = gdal.Open(ds)

    gt = ds.GetGeoTransform()
    xl = []
    yl = []
    for x in [0,ds.RasterXSize]:
        for y in [0, ds.RasterYSize]:
           cx,cy = translatePx2Coordinate(gt, x,y)
           xl.append(cx)
           yl.append(cy)

    return [min(xl), min(yl), max(xl), max(yl)]

def translatePxBox(gt, ulx, uly, dx, dy):

    pxX = [ulx, ulx+dx]
    pxY = [uly, uly+dy]

    c = list()
    for x in pxX:
        for y in pxY:
            c.append(translatePx2Coordinate(gt, x, y))

    cX = [d[0] for d in c]
    cY = [d[1] for d in c]

    return [min(cX), min(cY), max(cX), max(cY)]


def translatePx2Coordinate(gt, pxX, pxY, center=False):
    cx = gt[0] + pxX*gt[1] + pxY*gt[2]
    cy = gt[3] + pxX*gt[4] + pxY*gt[5]
    if center:
        cx += gt[1]*0.5
        cy += gt[5]*0.5
    return cx, cy

def clip2Grid(pathSrc, pathDst, pathRef, resampling=gdal.GRA_NearestNeighbour, drv='ENVI'):
    '''
    Clips and warps a source raster to the raster grid and projection of a reference raster.
    :param pathSrc:
    :param pathDst:
    :param pathRef:
    :param resampling:
    :return:
    '''

    dsSrc = gdal.Open(pathSrc)
    dsRef = gdal.Open(pathRef)

    drvDst = gdal.GetDriverByName(drv)
    drvMEM = gdal.GetDriverByName('MEM')

    src_eType = dsSrc.GetRasterBand(1).DataType
    src_ns, src_nl, src_nb = readDimensions(dsSrc)
    src_proj, src_gt = getSpatialRef(dsSrc)

    ref_ns, ref_nl, ref_nb = readDimensions(dsRef)
    ref_proj, ref_gt = getSpatialRef(dsRef)

    dsMEM = drvMEM.Create('', ref_ns, ref_nl, src_nb, src_eType)
    dsMEM.SetProjection(ref_proj)
    dsMEM.SetGeoTransform(ref_gt)
    dsMEM.SetDescription(dsSrc.GetDescription())
    #copy band specific stuff
    for b in range(1, src_nb+1):
        dst_band = dsMEM.GetRasterBand(b)
        src_band = dsSrc.GetRasterBand(b)
        nodata = src_band.GetNoDataValue()
        if nodata:
            dst_band.SetNoDataValue(nodata)
            dst_band.Fill(nodata)

        dst_band.SetDescription(src_band.GetDescription())
        dst_band.SetColorTable(src_band.GetColorTable())
    #copy metadata
    domains = dsSrc.GetMetadataDomainList()
    for domain in [d for d in domains if d != 'IMAGE_STRUCTURE']:
        md = dsSrc.GetMetadata(domain)
        dsMEM.SetMetadata(md, domain)
    """
    ReprojectImage(Dataset src_ds, Dataset dst_ds, char const * src_wkt=None, char const * dst_wkt=None,
        GDALResampleAlg eResampleAlg=GRA_NearestNeighbour, double WarpMemoryLimit=0.0,
        double maxerror=0.0, GDALProgressFunc callback=0, void * callback_data=None) -> CPLErr
    """
    print('Reproject to new grid...')
    gdal.ReprojectImage(dsSrc, dsMEM, src_proj, ref_proj, resampling)
    if drvDst != drvMEM:
        dsFinal = drvDst.CreateCopy(pathDst, dsMEM)
    else:
        dsFinal = dsMEM
    print('Clipping done')
    return dsFinal

def _getDS(path_or_ds, GA = gdal.GA_ReadOnly):
    if type(path_or_ds) is gdal.Dataset:
        ds = path_or_ds
    else:
        ds = gdal.Open(path_or_ds, GA)
    return ds

def createSpatialReference(wkt):
    if type(wkt) is osr.SpatialReference:
        srs = wkt
    else:
        assert type(wkt) is str
        srs = osr.SpatialReference()
        srs.ImportFromWkt(wkt)
    return srs

def is_equal_SpatialReference(wktA, wktB):
    srsA = createSpatialReference(wktA)
    srsB = createSpatialReference(wktB)
    return srsA.IsSame(srsB)

def check_spatial_consistency(dsA, dsB):
    dsA = _getDS(dsA)
    dsB = _getDS(dsB)

    assert dsA.RasterXSize == dsB.RasterXSize
    assert dsA.RasterYSize == dsB.RasterYSize
    assert dsA.GetGeoTransform() == dsB.GetGeoTransform()
    assert is_equal_SpatialReference(dsA.GetProjection(), dsB.GetProjection()) #srsA.IsSame(srsB)



def check_file_consistency(files, check_bands = True):
    """
    This methods checks whether a list of files can be opened by GDAL
    :param files:
    :param check_bands:
    :return: None in case all files could be opened, otherwise a list where the opening failed
    """
    failed = set()
    for f in files:
        try:
            ds = gdal.Open(f)
            if ds is None:
                failed.append(f)
            elif check_bands:
                for b in range(ds.RasterCount):
                    band = ds.GetRasterBand(b+1)
                    if band is None:
                        failed.append(f)
                        continue
        except:
            failed.add(f)

    failed = sorted(list(failed))

    if len(failed) == 0:
        failed = None
    return failed


jp = os.path.join

def main():
    registerErrorHandler()

    test_ENVI_metadata()


def test_ENVI_metadata():

    """
    Test gdal API ENVI driver implementation
    see http://www.exelisvis.com/docs/ENVIHeaderFiles.html for official supported meta tags

    """
    import re, sys, os
    import numpy as np
    from osgeo import gdal, gdal_array


    testdir = r'C:\Users\geo_beja\Documents\tmp'
    mkdir(testdir)

    data = np.ones((2, 30, 40), dtype='int')

    saveFile = lambda p : gdal_array.SaveArray(data, os.path.join(testdir, p), format='ENVI')

    def check_hdr_tag(ds , tag):
        ds.FlushCache()
        pathHdr = [p for p in ds.GetFileList() if p.endswith('.hdr')][0]
        bn = os.path.basename(pathHdr)

        with open(pathHdr) as f:
            lines = f.readlines()

        is_match = re.compile('^[ ]*'+tag+'[ ]*=')
        matchedLines = [line for line in lines if is_match.search(line)]

        l = len(matchedLines)
        if l == 0:
            print('"{}" failed on tag "{}"!'.format(bn, tag), file=sys.stderr)
            return False
        elif l > 1:
            print('"{}" failed on tag "{}": multiple ({}) matches:\n\t{}'.format(bn, tag,l, '\n\t'.join(matchedLines)), file=sys.stderr)
            return False

        print('"{}" success: "{}"'.format(bn, matchedLines[0].replace('\n','')))
        return True

    #define hdr test cases
    # test no-data value
    if True:
        check = lambda ds : check_hdr_tag(ds, 'data ignore value')
        ds = saveFile('A_nodata_API')
        for b in [ds.GetRasterBand(b + 1) for b in range(ds.RasterCount)]:
            b.SetNoDataValue(-1)
        check(ds)

        ds = saveFile('A_nodata_ENVI')
        ds.SetMetadataItem('data ignore value', '-1', 'ENVI')
        check(ds)

        ds = saveFile('A_nodata_BOTH')
        ds.SetMetadataItem('data_ignore_value', '-1', 'ENVI')
        for b in [ds.GetRasterBand(b + 1) for b in range(ds.RasterCount)]:
            b.SetNoDataValue(-1)
        check(ds)

    if True:

        def check(ds):
            check_hdr_tag(ds, 'wavelength')
            check_hdr_tag(ds, 'wavelength units')

        ds = saveFile('B_Metadata_API')
        ds.SetMetadataItem('wavelength', '{200,300}', 'ENVI')
        ds.SetMetadataItem('wavelength units', 'nm', 'ENVI')
        check(ds)

    if True:

        def check(ds):
            check_hdr_tag(ds, 'class names')
            check_hdr_tag(ds, 'class lookup')
            check_hdr_tag(ds, 'classes')

        class_names = ['unclassified', 'foo', 'bar']
        data = np.ones((1, 30, 40), dtype='int')
        ds = saveFile('C_Metadata_API')
        for band in [ds.GetRasterBand(b+1) for b in range(ds.RasterCount)]:
            ds.SetCategoryNames(class_names)



    print('Metadatatests done')


if __name__ == '__main__':
    main()
