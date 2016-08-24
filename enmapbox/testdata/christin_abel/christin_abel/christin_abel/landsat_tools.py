__author__ = 'geo_beja'

import re
from osgeo import gdal, osr, ogr, gdal_array
import os
import fnmatch, shutil, sys, re
import numpy as np

from gdal_tools


regLSID = re.compile(r'L[EMCT][1234578]\d{6}(19|20)\d{5}[a-zA-Z]{3}\d{2}')
regLS_SR_Dir = re.compile(r'L[EMCT][1234578]\d+-SC(19|20)\d+')






def writeBandStack(pathDst, bandStackData, nodata=None, refDS=None, of='ENVI'):

    nb = len(bandStackData)
    assert nb > 0
    bandNames = list(bandStackData.keys())
    shape = bandStackData[bandNames[0]].shape
    ns = shape[1]
    nl = shape[0]
    eType = gdal.GDT_Float32

    drv = gdal.GetDriverByName(of)
    ds = drv.Create(pathDst, ns,nl, nb, eType=eType)
    if nodata:
        ds.SetMetadataItem('data ignore value', str(nodata), 'ENVI')

    if refDS:
        assert ns == refDS.RasterXSize
        assert nl == refDS.RasterYSize
        gdal_tools.copySpatialRef(refDS, ds)

    for b in range(0,nb):
        bandName = bandNames[b]
        band = ds.GetRasterBand(b+1)
        if nodata:
            band.SetNoDataValue(nodata)
            band.Fill(nodata)
        band.SetDescription(bandName)
        band.WriteArray(bandStackData[bandName])


    print('Done')

def findFMask(dir, id):
    candidates = file_search(dir, '*{}*mask*.*'.format(id))
    candidates = [c for c in candidates if re.search('c?fmask.(tif|img|bsq)$', c, re.I)]

    return candidates[0]


def landsatFolder2VRT(dirLS, dirVRT, recursive=False, te=None, tr=None, dateprefix=False, pattern='*', lamos=False):
    '''
    This routine reads a folder with landsat product output of:
      LEDAPS (old, one hdf)
      LEDAPS (new, multiple hdf)
      Landsat surface reflectance + cmask from USGS server)
    and writes an VRT with following bands:
        <scene_id>_BOA.vrt -> surface reflectance VRT with band names
                'B','G','R','NIR','SWIR1','SWIR2'
        <scene_id>_Flags.vrt -> cloud & quality flag VRT
        <scene_id>_FMask.vrt -> cloud mask produced by FMask or better

    :param dirLS:
    :param pathVRT:
    :return:
    '''


    if isinstance(dirLS, list):
        for dir in dirLS:
            landsatFolder2VRT(dir, dirVRT, recursive=recursive, dateprefix=dateprefix, pattern=pattern)
        return

    if not os.path.isdir(dirLS):
        print('not a directory:'.format(dirLS))
        return


    bn = os.path.basename(dirLS)
    if not (regLSID.search(bn) or regLS_SR_Dir.search(bn)):
        if recursive:
            for root, dirs, files in os.walk(dirLS):
                for dir in dirs:
                    landsatFolder2VRT(os.path.join(root, dir), dirVRT, recursive=recursive, dateprefix=dateprefix, pattern=pattern)
            return
        else:
            raise Exception('Not a Landsat folder: {}'.format(dirLS))


    #retrieve valid scene ids
    sceneIDs = set()
    for file in file_search(dirLS, pattern):
        sceneid = LandsatSceneID.extractSceneID(os.path.basename(file))
        if sceneid:
            sceneIDs.add(sceneid)


    for sceneid in sceneIDs:
        pathXML = file_search(dirLS, sceneid+'.xml', ignoreCase=True, firstOrNone=True)
        #pathSR  = file_search(dirLS, sceneid+'_sr_*.tif*', ignoreCase=True, firstOrNone=True)
        pathHDF = file_search(dirLS, 'lndsr*'+sceneid+'*.HDF', ignoreCase=True, firstOrNone=True)

        pathMTL = file_search(dirLS, '*'+sceneid+'*MTL.txt', ignoreCase=True, firstOrNone=True)
        pathMsk = findFMask(dirLS, sceneid)

        LID = LandsatSceneID(sceneid)
        if LID.sensor not in ['LC8','LE7','LT5', 'LT4']:
            raise NotImplemented('Sensor '+LID.sensor)

        #find source bands by reading the HDF subdataset names
        bandRegexFlg = ['bandQA','.*cloud','cloud_QA','cloud_shadow_QA','adjacent_cloud_QA']
        if LID.sensor == 'LC8':
            bandRegexBOA   = ['band0?2','band0?3','band0?4','band0?5','band0?6','band0?7']

        else:
            bandRegexBOA   = ['band0?1','band0?2','band0?3','band0?4','band0?5','band0?7']



        def findXMLDatasets(XML, regex, dir):
            subdatasets = list()
            bandnames = list()
            nodata = list()

            for band in XML.findall(".//band"):
                bname = band.attrib['name']
                if 'fill_value' in band.attrib.keys():
                    nodatavalue = float(band.attrib['fill_value'])
                else:
                    nodatavalue = None

                path = os.path.join(dir, band.find('file_name').text)
                for pattern in regex:
                    if re.search(pattern, bname) and os.path.exists(path):
                        subdatasets.append(path)
                        bandnames.append(bname)
                        nodata.append(nodatavalue)
                        break
            if len(subdatasets) == 0:
                raise Exception('Can not find any band of:'+' '.join(regex))
            return subdatasets, bandnames, nodata

        def findHDFSubdataset(ds, regex):
            subdatasets = list()
            bandnames = list()
            nodata = list()
            for sub in ds.GetSubDatasets():
                for pattern in regex:
                    if re.search(pattern, sub[0]) or re.search(pattern, sub[1]):
                        subdatasets.append(sub[0])
                        bandnames.append(sub[1])

                        d = gdal.Open(sub[0])
                        nodata.append(d.GetRasterBand(1).GetNoDataValue())

                        d = None

                        break
            if len(subdatasets) == 0:
                raise Exception('Can not find any band of:'+' '.join(regex))
            return subdatasets, bandnames, nodata


        if pathXML:
            #read USGS surface reflectance product
            import xml.etree.ElementTree as ET
            xmlstring = open(pathXML).read()
            xmlstring = re.sub('xmlns[^=]*="[^"]+"', '', xmlstring, count=1)
            XML = ET.fromstring(xmlstring)
            #ET.register_namespace('','http://espa.cr.usgs.gov/v1.1')

            zone = XML.find('.//zone_code').text
            srs = 'EPSG:326{:02d}'.format(int(zone))

            sdBOA, bnHdfBOA, noDataBOA = findXMLDatasets(XML, bandRegexBOA, dirLS)

            sdFlg, bnHdfFlg, noDataFlg = findXMLDatasets(XML, bandRegexFlg, dirLS)




            ds = gdal.Open(sdBOA[0])
            gt = ds.GetGeoTransform()
            ds = None
            if gt == (0,1,0,0,0,1):
                raise Exception('Missing projection')
            pass

        elif pathHDF and pathMTL and pathMsk:
            #read LEDAPS HDF
            zone = readMTLFile(pathMTL, tagsOfInterest=['UTM_ZONE'])['UTM_ZONE']
            srs = 'EPSG:326{:02d}'.format(int(zone))

            ds = gdal.Open(pathHDF)
            gt = ds.GetGeoTransform()
            if gt[1] == 1:
                gt = gdal.Open(pathMsk).GetGeoTransform()


            sdBOA, bnHdfBOA, noDataBOA = findHDFSubdataset(ds, bandRegexBOA)
            sdFlg, bnHdfFlg, noDataFlg = findHDFSubdataset(ds, bandRegexFlg)

            if not noDataBOA[0]:
                noDataBOA = [-1000 for nodata in noDataBOA]


            pass

        else:
            print('Can not interprete/find required scene components for {} in folder {}'.format(sceneid, dirLS), file=sys.stderr)
            continue

        if gt[1] == 1:
            raise Exception('Can not specify geo-transformation / map-info')

        #gridInfo
        vrt_kwds = list()
        vrt_kwds.append('-a_srs "{}" '.format(srs))
        if te != None:
            vrt_kwds.append('-te {} {} {} {} '.format(te[0],te[1], te[2], te[3]))
        if tr != None:
            vrt_kwds.append('-tr {} {} '.format(tr[0],tr[1]))

        #create the VRTs
        enviMD = dict()
        enviMD['sensor type'] = ['Landsat OLI','Landsat ETM+','Landsat TM','Landsat TM'][['LC8','LE7','LT5','LT4'].index(LID.sensor)]
        enviMD['band names']  = ['B','G','R','NIR', 'SWIR1', 'SWIR2']
        enviMD['wavelength units']  = 'micrometers'
        enviMD['center wavelength'] = [0.49,0.56,0.66,0.84,1.65,2.20]
        bandNamesFlg = ['cloud_QA','cloud_shadow_QA','adjacent_cloud_QA']

        os.makedirs(dirVRT, exist_ok=True)
        basename = sceneid
        if dateprefix:
            basename = '{}_{}'.format(str(LID.date), sceneid)
        pathVRT_BOA = os.path.join(dirVRT, basename+'_BOA.vrt')
        pathVRT_Flg = os.path.join(dirVRT, basename+'_Flg.vrt')
        pathVRT_Msk = os.path.join(dirVRT, basename+'_Msk.vrt')
        if 'sr_band2' in bnHdfBOA:
            is_match = re.compile('.*sr_band\d')
            bnHdfBOA = [b for b in bnHdfBOA if is_match.search(b)]
            sdBOA = [b for b in sdBOA if is_match.search(os.path.basename(b))]

        gdal_tools.createVRT(pathVRT_BOA, sdBOA, vrt_kwds=vrt_kwds, bandnames=enviMD['band names'], gt=gt, \
                                                metadata=enviMD, nodata=noDataBOA)

        #

        #gdal_tools.createVRT(pathVRT_Flg, sdFlg, vrt_kwds=vrt_kwds, bandnames=bnHdfFlg, gt=gt)
        #vrt_kwds.append('-overwrite -srcnodata 255 -vrtnodata 255 -hidenodata')
        #vrt_kwds.append('-overwrite -srcnodata None ')
        #vrt_kwds.append('-overwrite -srcnodata 255')
        #gdal_tools.createVRT(pathVRT_Msk, pathMsk, vrt_kwds=vrt_kwds, gt=gt)

        drvVRT = gdal.GetDriverByName('VRT')

        drvVRT.CreateCopy(pathVRT_Flg, gdal.Open(sdFlg[0]))
        vrtMskMEM = drvVRT.CreateCopy("", gdal.Open(pathMsk))
        vrtMskMEM.GetRasterBand(1).SetNoDataValue(255)
        vrtMskMEM.GetRasterBand(1).SetMetadataItem("HideNoDataValue","1")
        drvVRT.CreateCopy(pathVRT_Msk, vrtMskMEM)
        vrtMskMEM = None
        #data = gdal_array.LoadFile(pathVRT_Msk)

        ds = gdal.Open(pathVRT_BOA, gdal.GA_Update)
        #set R-G-B default to 4-5-3
        ds.GetRasterBand(4).SetColorInterpretation(gdal.GCI_RedBand)
        ds.GetRasterBand(5).SetColorInterpretation(gdal.GCI_GreenBand)
        ds.GetRasterBand(3).SetColorInterpretation(gdal.GCI_BlueBand)
        ds = None

fmask_flags = [0,1,2,3,4,255]
fmask_flag_names = ['clear land','clear water','cloud shadow','snow','cloud','no observation']
def get_fmask_flag_counts(fmask_array):
    '''

    :param fmask_array: array with fmask flag values

    :return:

    Flags https://github.com/prs021/fmask
    0 => clear land pixel
    1 => clear water pixel
    2 => cloud shadow
    3 => snow
    4 => cloud
    255 => no observation
    '''



    n_flags = len(fmask_flags)
    flag_counts = np.ndarray((n_flags), dtype='uint32')
    for i, flag in enumerate(fmask_flags):
        flag_counts[i] = (fmask_array == flag).sum()

    return flag_counts



def repairL8LEDAPS_Metadata(pathHDF,  pathDstHDF):

    fmask = file_search(os.path.dirname(pathHDF), 'fmask.*')[0]
    ds = gdal.Open(fmask)
    gt  = ds.GetGeoTransform()
    srs = ds.GetProjection()
    ds = None
    drvMEM = gdal.GetDriverByName('MEM')

    dsIn = gdal.Open(pathHDF)
    drvHDF = dsIn.GetDriver()
    dsTmp = drvMEM.CreateCopy('', dsIn)
    dsTmp.SetGeoTransform(gt)
    dsTmp.SetProjection(srs)
    drvHDF.CreateCopy(pathDstHDF, dsTmp)
    dsTmp = None

    pass

def getYearDOYFromDateTime64(dt64):
    if type(dt64) is str:
        dt64 = np.datetime64(dt64)
    year = dt64.astype('datetime64[Y]')
    doy = (dt64 - year).astype('int')+1
    year = year.astype('int')+1970

    return (year,doy)

def getDateTime64FromYYYYDOY(yyyydoy):
    return getDateTime64FromDOY(yyyydoy[0:4], yyyydoy[4:7])

def getDateTime64FromDOY(year, doy):
        if type(year) is str:
            year = int(year)
        if type(doy) is str:
            doy = int(doy)
        return np.datetime64('{:04d}-01-01'.format(year)) + np.timedelta64(doy-1, 'D')



class LandsatSceneID(object):

    def __init__(self, text):

        self.id = self.extractSceneID(text)
        self.sensor = self.id[0:3]
        self.path = int(self.id[3:6])
        self.row = int(self.id[6:9])
        self.year = int(self.id[9:13])
        self.doy = int(self.id[13:16])
        self.date = getDateTime64FromDOY(self.year, self.doy)
        self.decimalyear = self.year + (self.doy - 1) / 365



    @staticmethod
    def extractSceneID(text):
        """Returns the most-right landsat scene identifier of a string"""
        assert type(text) is str
        match = [m.group() for m in regLSID.finditer(text) if m is not None]
        if len(match) == 0:
            match = None
        else:
            #take the last
            match = match[-1]
        return match

def dir_search(rootDir, wildcard, recursive=False, ignoreCase=False, firstOrNone=False, required=False):
    assert os.path.isdir(rootDir), "Path is not a directory:{}".format(rootDir)
    results = []
    for root, dirs, files in os.walk(rootDir):
        for dir in dirs:
            if (ignoreCase and fnmatch.fnmatch(dir.lower(), wildcard.lower())) \
                    or fnmatch.fnmatch(dir, wildcard):
                results.append(os.path.join(root, dir))
        if not recursive:
            break

    if firstOrNone:
        if len(results) > 0:
            results = results[0]
        else:
            results = None
    if required and results is None:
        raise Exception('Unable to find directory "{}"'.format(wildcard))
    return results

def file_search(rootDir, wildcard, recursive=False, ignoreCase=False, firstOrNone=False):
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
    if firstOrNone:
        if len(results) == 0:
            results = None
        else:
            results = results[0]
    return results


def readXMLFile(pathXML, tagsOfInterest=None):

    pass

def readMTLFile(pathMTL, tagsOfInterest=None, verbose=False):
    """Returns the tag names and values inside a MTL File

    """
    has_toi = tagsOfInterest is not None

    if not type(pathMTL) is str:
        results = dict()
        for path in pathMTL:

            result = readMTLFile(path, tagsOfInterest=tagsOfInterest, verbose=verbose)
            if results != None:
                sceneid = LandsatSceneID.extractSceneID(path)
                results[sceneid] = result

        return  results
    else:
        results = dict()
        for line in open(pathMTL):
            if re.match(r'^[ ]*GROUP',line):
                continue
            parts = line.split('=')
            if len(parts) == 2:
                tagname = parts[0].strip()
                if has_toi and tagname not in tagsOfInterest:
                    continue

                results[tagname] = parts[1].strip()
        return results

def checkLEDAPS_HDF(path):

    ds = gdal.Open(path)
    if ds is None:
        print('Can not open '+path)
        return False
    sub = ds.GetSubDatasets()
    nsub = len(sub)

    if nsub == 0:
        print('Missing subdatasets in '+path)
        return False

    regex = re.compile('.*band0?1.*')
    found = False
    for s in sub:
        if regex.findall(s[1]):
            found = True
            break
    if not found:
        print('Can not find landsat band descriptions in '+path)
        return False

    ds = None
    return True

def remove_old_ESPA_SR(root_dir):
    import shutil
    sceneIDs = set()
    dirs = dir_search(root_dir, 'L*-SC*')


    for dir in dirs:
        m = regLS_SR_Dir.findall(os.path.basename(dir))[0]
        id = m.split('-')[0]
        sceneIDs.add(id)

    for id in list(sceneIDs):

        id_dirs = sorted([d for d in dirs if os.path.basename(d).startswith(id)])
        if len(id_dirs) > 1:
            for d in id_dirs[0:-1]:
                s = ''
                shutil.rmtree(d)
                #os.removedirs(d)




def main():

    gdal_tools.registerErrorHandler()

    p = r'Y:\LandsatData\Landsat_NovoProgresso\LC82270652013252LGN00\LC82270652013252LGN00_cfmask.img'

    s = ""
    if True:
        dirLS = r'H:\LandsatData\Landsat_ESPA\LC82270652014223-SC20151118214345'
        dirVRT = r'O:\SenseCarbonProcessing\BJ_NOC\QGIS'
        landsatFolder2VRT(dirLS, dirVRT)
        exit(0)
    if False:

        root = r'H:\LandsatData\Landsat_SR'
        remove_old_ESPA_SR(root)
        exit(0)
    if False:
        pathSrc = r'Y:\BJ_NOC\01_RasterData\00_VRTs\02_Cutted\2014-08-11_LC82270652014223LGN00_BOA.vrt'
        pathMsk = r'Y:\BJ_NOC\01_RasterData\00_VRTs\02_Cutted\2014-08-11_LC82270652014223LGN00_Msk.vrt'
        pathDst = r'Y:\BJ_NOC\01_RasterData\02_Segmented\EVI_NBR.bsq'

        writeMetric(pathSrc, pathDst, ['EVI','NBR'], nodata=-999, pathMsk=pathMsk, msk_include=0,  scale2int=False)


    if False:
        dirSrc = []

        dirSrc.append(r'B:\PreprocessedLandsatData\227_065')
        dirSrc.append(r'X:\LandsatData\Landsat_SR')

        dirVRT = r'X:\LandsatData\Landsat_SR_Test'

        os.makedirs(dirVRT, exist_ok=True)
        landsatFolder2VRT(dirSrc, dirVRT, recursive=True, dateprefix=True, pattern='*227065*')


        vrtPaths = file_search(dirVRT, '*.vrt')

        vrtData = dict()
        for path in file_search(dirVRT, '*.vrt'):
            f = open(path, 'r')
            lines = f.readlines()
            f.close()
            vrtData[path] = lines


        paths = list(vrtData.keys())
        for p in paths:
            os.remove(p)
        paths.sort()
        for p in paths:
            f = open(p, 'w')
            f.writelines(vrtData[p])
            f.close()


    if False:
        import shutil
        dir = r'X:\LandsatData\L8'
       # dir = r'X:\LandsatData\PA_MT_Coverage2013\L1T_Archives\unpacked'
        toDelete = []
        isOK = []
        for root, dirs, files in os.walk(dir):
            for dir in dirs:
                pathDir = os.path.join(root,dir)
                pathMTL = file_search(pathDir,'*MTL.txt')
                pathHDF = file_search(pathDir,'*.hdf')
                id = extractSceneID(dir)
                if len(pathHDF) == 0:
                    toDelete.append(pathDir)
                    continue

                d = readMTLFile(pathMTL, tagsOfInterest=['PROCESSING_SOFTWARE_VERSION','GROUND_CONTROL_POINTS_VERSION'])
                d = d[id]
                if 'GROUND_CONTROL_POINTS_VERSION' not in d:
                    toDelete.append(pathDir)
                elif d['GROUND_CONTROL_POINTS_VERSION'] != '2':
                    toDelete.append(pathDir)
                else:
                    isOK.append(pathDir)


            break

        for dir in toDelete:
            print(dir)

        for dir in toDelete:
            shutil.rmtree(dir)


        files = file_search(dir, 'LC8*MTL.txt', recursive=True, ignoreCase=True)
        outdates = []
        for file in files:
            id = extractSceneID(file)
            d = readMTLFile(file, tagsOfInterest=['PROCESSING_SOFTWARE_VERSION','GROUND_CONTROL_POINTS_VERSION'])

            if not 'GROUND_CONTROL_POINTS_VERSION' in d:
                outdates.append(id)
            else:
                if int(d['GROUND_CONTROL_POINTS_VERSION']) < 2:
                    outdates.append(id)




        pass



if __name__ == '__main__':
    gdal.UseExceptions()
    gdal.PushErrorHandler(gdal_tools.gdal_error_handler)
    main()
