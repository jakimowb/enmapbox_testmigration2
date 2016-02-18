from osgeo import ogr, osr, gdal, gdal_array

import xml.etree

import os, re, fnmatch, sys, subprocess
import collections

#CONSTANSTS, GLOBAL VALUES

#see https://earth.esa.int/documents/247904/685211/Sentinel-2_User_Handbook
S2_PRODUCTS = [ ('L0_Granule'   , 'MSI_L0__GR') \
              , ('L0_Datastrip' , 'MSI_L0__DS') \
              , ('L1A_Granule'  , 'MSI_L1A_GR') \
              , ('L1A_Datastrip', 'MSI_L1A_DS') \
              , ('L1B_Granule'  , 'MSI_L1B_GR') \
              , ('L1B_Datastrip', 'MSI_L1B_DS') \
              , ('L1C_Granule'  , 'MSI_L1C_TL') \
              , ('L1C_Datastrip', 'MSI_L1C_DS') \
            ]

#see https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/naming-convention
#S2_GRANULE_REGEX = re.compile('S2[ABCD]_(OPER|TEST|USER)_(MSI_)_MSI_(L0__(GR|DS)|L1A_(GR|DS)|L1B_(GR|DS)|L1C_(TL|DS))_')



#see table 1: https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2/instrument-payload/resolution-and-swath
S2_MSI_DATA = [ (10,'B02',490,65) \
              , (10,'B03',560,35) \
              , (10,'B04',665,30) \
              #, (10,'B8A',842,115) \
              , (10,'B08',842,115) \
              , (20,'B05',705,15 ) \
              , (20,'B06',740,15 )\
              , (20,'B07',783,20 ) \
              , (20,'B8A',865,20) \
              , (20,'B11',1610,90) \
              , (20,'B12',2190,180) \
              , (60,'B01',443,20) \
              , (60,'B09',945,20) \
              , (60,'B10',1380,30) \
              ]
S2_BANDKEYS = [t[1] for t in S2_MSI_DATA]
#accessor to this table via bandKey
getS2_BandIndex = lambda bandKey : S2_BANDKEYS.index(bandKey)
getS2_SpatialResolution = lambda bandKey : S2_MSI_DATA[getS2_BandIndex(bandKey)][0]
getS2_CentralWavelength = lambda bandKey : S2_MSI_DATA[getS2_BandIndex(bandKey)][2]
getS2_BandWidth = lambda bandKey : S2_MSI_DATA[getS2_BandIndex(bandKey)][3]
getS2_BandKey = lambda t : os.path.splitext(os.path.basename(t))[0].split('_')[-1]

#GDAL constants
GDT_Values = [gdal.GDT_Byte, gdal.GDT_UInt16, gdal.GDT_UInt32, gdal.GDT_Float32, gdal.GDT_Float64 \
                           , gdal.GDT_CInt16, gdal.GDT_CInt32, gdal.GDT_CFloat32, gdal.GDT_CFloat64]

GDT_Names =  ['Byte', 'UInt16', 'UInt32', 'Float32', 'Float64' \
                    , 'CInt16', 'CInt32', 'CFloat32', 'CFloat64']

#provide UNC paths
is_windows = sys.platform.lower().startswith('win')
drive_map = dict()
if is_windows:
    cmd = subprocess.Popen('net use', shell=True, stdout=subprocess.PIPE)
    lines = [line.decode(encoding='iso8859-1') for line in cmd.stdout]

    for line in lines:
        if re.search(r'[A-Z]:[ ]+[\\]{2}', line):
            parts = re.split(r'[ ]+', line)
            drive = parts[1]
            path =  parts[2]
            #drive_map[drive] = '\\\\?\\\\UNC\\'+path[2:]
            drive_map[drive] = path


regex_is_win_drive = re.compile(r'^[A-Z]:')

def getUNCPath(path):
    path = os.path.normpath(path)
    if is_windows:
        match = regex_is_win_drive.search(path)
        if match:
            pathUNC = drive_map[match.group()] + path[2:]
            #pathUNC = '\\\\?\\UNC\\' + drive_map[match.group()][2:] + path[2:]

            if False and os.path.exists(path):
                if os.path.exists(pathUNC):
                    path = pathUNC
                else:
                    print('Failed to convert\n{}\n into UNC path\n{}'.format(path, pathUNC), file=sys.stderr)

    return path



def file_search(rootdir, wildcard, recursive=False, ignoreCase=False):
    assert rootdir is not None
    if not os.path.isdir(rootdir):
        print("Path is not a directory:{}".format(rootdir), file=sys.stderr)

    results = []

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if (ignoreCase and fnmatch.fnmatch(file.lower(), wildcard.lower())) \
                    or fnmatch.fnmatch(file, wildcard):
                results.append(os.path.join(root, file))
        if not recursive:
            break
    return results



def parse_S2_product(text):
    for (fileType, fileNaming) in S2_PRODUCTS:
        if re.search(r'S2[ABCD]_.*_{}_'.format(fileNaming), text):
            return fileType, fileNaming
    return None


def copyMetadata(src,dst,domain):
    data = src.GetMetadata_Dict(domain)
    for key, value in data.items():
        #print('Copy metadata: {} : {} {}'.format(domain, key, value))
        #print((key, value, domain))
        dst.SetMetadataItem(key, value, domain)

def callback_progress(a, b, c):
    #print('callback')
    sys.stdout.write('\r{:.1f} %'.format(a*100))
    if a >= 1.0:
        print('')

    pass


def gdal_to_gdal(pathSrc, pathDst, drv='ENVI', options=None):
    """
    Creates a copy from gdal raster to gdal raster but takes additional care on metadata issues.
    :param pathSrc:
    :param pathDst:
    :param drv:
    :param options:
    :return:
    """
    if options is None:
        options = []
    assert isinstance(options, list)

    drvDst = gdal.GetDriverByName(drv)
    assert drvDst is not None

    os.makedirs(os.path.dirname(pathDst), exist_ok=True)

    print('Copy {} \n  to {} ...'.format(pathSrc, pathDst))

    dsSrc = gdal.Open(pathSrc)
    assert dsSrc is not None

    #CreateCopy(Driver self, char const * utf8_path, Dataset src, int strict=1, char ** options=None, GDALProgressFunc callback=0,
    dsDst = drvDst.CreateCopy(pathDst, dsSrc, 1, options, callback_progress, 'gdal_to_gdal:copy')

    assert dsDst is not None

    for domain in dsSrc.GetMetadataDomainList():
       copyMetadata(dsSrc,dsDst, domain)

    for b in range(dsSrc.RasterCount):
        bandSrc =dsSrc.GetRasterBand(b+1)
        bandDst = dsDst.GetRasterBand(b+1)
        bandDst.SetDescription(bandSrc.GetDescription())
        no_data = bandSrc.GetNoDataValue()
        if no_data is not None:
            bandDst.SetNoDataValue(no_data)

    return dsDst


class S2_Granule(object):

    def __init__(self, text):
        text = os.path.basename(text)


def sentinel2_strip_to_envi(pathXML, dirDst ,resolutions=[10,20,60], unc=False, tiledirs=False, mosaic_vrt=True):
    vrts = sentinel2_strip_to_vrt(pathXML, dirDst, resolutions=resolutions, unc=unc, block_size = 256, tiledirs=tiledirs)

    for pathSrc in vrts:
        dn = os.path.dirname(pathSrc)
        bn = os.path.basename(pathSrc)
        pathDst = os.path.join(dn, '{}.bsq'.format(os.path.splitext(bn)[0]))
        gdal_to_gdal(pathSrc, pathDst, drv='ENVI')

    if mosaic_vrt:
        pathVRT = os.path.join(dirDst, 'Tile_Overview.vrt')



def sentinel2_strip_to_vrt(pathXML, dirDst ,resolutions=[10,20,60], unc=False, block_size = 256, tiledirs=False):
    assert os.path.splitext(pathXML)[1].lower() == '.xml'
    import xml.etree.ElementTree as ET
    tree = ET.parse(pathXML).getroot()

    granuleIDs = collections.OrderedDict()

    for elem in tree.findall('*//Product_Organisation/Granule_List/Granules'):
        id = elem.get('granuleIdentifier')
        image_ids = list()
        for image_id in elem.findall('IMAGE_ID'):
            image_ids.append(image_id.text)
        granuleIDs[id] = image_ids

    vrts = list()

    dn = os.path.dirname(pathXML)
    dir_granules = os.path.join(dn, 'GRANULE')
    for granuleID in granuleIDs.keys():
        dir_granule = os.path.join(dir_granules, granuleID)
        assert os.path.exists(dir_granule)
        parts = granuleID.split('_')
        parts[2] = 'MTD'
        granuleID2 = '_'.join(parts[0:10])
        pathXMLGranule = os.path.join(dir_granule, granuleID2+'.xml')

        assert os.path.exists(pathXMLGranule)

        if tiledirs:
            pathDst = os.path.join(dirDst, *[parts[9],granuleID+'.vrt'])
        else:
            pathDst = os.path.join(dirDst, granuleID+'.vrt')
        vrts.extend(sentinel2_granule_to_vrt(pathXMLGranule, pathDst, resolutions=resolutions, unc=unc, block_size=block_size))

    vrts = [v for v in vrts if v is not None]

    return vrts



def sentinel2_granule_to_vrt(pathXML, pathDst, resolutions=[10,20,60], mode='all', unc=False, block_size = 256):
    """
    Create a VRt representation that accesses the S2 SNAP File structure
    :param pathXML: xml on granule / tile level
    :param pathDst: target file name. Will be appended by spatial resolution hint: <file name>_20m.vrt
    :param mode:
    :param unc:
    :param block_size: vrt block size parameter
    :return:
    """
    assert os.path.splitext(pathXML)[1].lower() == '.xml'
    import xml.etree.ElementTree as ET
    tree = ET.parse(pathXML)
    #fileType, typeID = parse_S2_product(os.path.basename(pathXML))

    def getChild(tag_name, text=None, attrib={}):
        e = ET.Element(tag_name, attrib=attrib)
        if text:
            gdal_array.gdalconst
            e.text = str(text)
        return e


    meta_locations = [('TILE_ID','*/TILE_ID') \
                    , ('DATASTRIP_ID','*/DATASTRIP_ID') \
                    , ('SENSING_TIME','*/SENSING_TIME') \
                    , ('ARCHIVING_TIME', '*/Archiving_Info/ARCHIVING_TIME')
                    , ('HORIZONTAL_CS_NAME','*/Tile_Geocoding/HORIZONTAL_CS_NAME') \
                    , ('HORIZONTAL_CS_CODE','*/Tile_Geocoding/HORIZONTAL_CS_CODE') \
                      ]

    vrtMetaDataDomain = 'ENVI'

    meta_data = dict()

    for key, xpath in meta_locations:
        elem = tree.find(xpath)
        if elem is not None:
            meta_value = elem.text
            meta_data[key] = meta_value

    assert 'TILE_ID' in meta_data.keys()

    dn = os.path.dirname(pathXML)
    dn_img_data = os.path.join(dn, 'IMG_DATA')
    dn_aux_data = os.path.join(dn, 'AUX_DATA')
    dn_qi_data  = os.path.join(dn, 'QI_DATA')

    fileType, typeID = parse_S2_product(meta_data['TILE_ID'])

    sources = dict()
    if typeID == 'MSI_L1C_TL':
        granules = file_search(dn_img_data, '*'+typeID+'*.jp2')

        for path in granules:
            ds  = gdal.Open(path)
            ns = ds.RasterXSize
            nl = ds.RasterYSize
            assert ds.RasterCount == 1
            gt = ds.GetGeoTransform()
            pr = ds.GetProjection()

            if abs(gt[1]) not in resolutions:

                continue

            dt = ds.GetRasterBand(1).DataType
            key = (ns, nl, gt, pr, dt)
            if key not in sources.keys():
                sources[key] = list()
            #todo: improve path handling to allow for absolute paths

            if unc:
                path = getUNCPath(path)

            sources[key].append(path)

            #sources[key].append(path)

    else:
        raise Exception('Unsupported product type:{}'.format(typeID))

    dn = os.path.dirname(pathDst)
    os.makedirs(dn, exist_ok=True)

    bn = os.path.basename(pathDst)
    rn = os.path.splitext(bn)[0]

    drv = gdal.GetDriverByName('VRT')

    block_size_str = '{}'.format(block_size)

    results = list()


    for (ns, nl, gt, pr, dt), srcFiles in sources.items():
        srcFiles = sorted(srcFiles, key=getS2_BandKey)
        bandKeys = [getS2_BandKey(f) for f in srcFiles]
        wl = [getS2_CentralWavelength(b) for b in bandKeys]

        pathDst = os.path.join(dn, '{}_{}m.vrt'.format(rn, int(abs(gt[1]))))

        results.append(pathDst)

        print('Write {}...'.format(pathDst))
        nb = len(srcFiles)
        vrtDS = drv.Create(pathDst, ns, nl, nb, eType=dt)
        vrtDS.SetProjection(pr)
        vrtDS.SetGeoTransform(gt)

        if True:
            vrtDS.SetMetadataItem('wavelength units', 'nm', vrtMetaDataDomain)
            vrtDS.SetMetadataItem('acquisition time',meta_data['SENSING_TIME'] ,vrtMetaDataDomain)
            vrtDS.SetMetadataItem('wavelength','{'+','.join([str(w) for w in wl])+'}',vrtMetaDataDomain)

            for key, value in meta_data.items():
                vrtDS.SetMetadataItem(key, value, vrtMetaDataDomain)


        dt_str = GDT_Names[GDT_Values.index(dt)]
        ns_str = '{}'.format(ns)
        nl_str = '{}'.format(nl)

        for i, srcFile in enumerate(srcFiles):
            options = list()
            #options['subclass'] = "VRTRasterBand"
            options.append('SourceFilename='+srcFile)
            options.extend('relativeToVRT=false')

            bn = os.path.basename(srcFile)
            bandKey = os.path.splitext(bn)[0].split('_')[-1]


            band = vrtDS.GetRasterBand(i+1)
            band.SetDescription('{} {}nm ({})'.format(bandKey, wl[i], bn))




            XML = ET.Element('SimpleSource')
            XML.append(getChild('SourceFilename',text=srcFile))
            XML.append(getChild('SourceBand',text=1))
            XML.append(getChild('SourceProperties' \
                        , attrib={'RasterXSize':"{}".format(ns), 'RasterYSize':"{}".format(nl) \
                                 ,'DataType':"{}".format(dt_str) \
                                 ,'BlockXSize':block_size_str, 'BlockYSize':block_size_str \
                                  }))

            XML.append(getChild('SrcRect', attrib={'xOff':'0','yOff':'0', 'xSize':ns_str, 'ysize':nl_str}))
            XML.append(getChild('DstRect', attrib={'xOff':'0','yOff':'0', 'xSize':ns_str, 'ysize':nl_str}))

            txt = ET.tostring(XML, encoding='us-ascii', method='xml').decode('utf8')

            band.SetMetadataItem('source_0',txt, 'new_vrt_sources')


        vrtDS = None

    return results


def sentinel2_granule_to_envi(pathXML, pathDst, delete_temporary_vrt=True, resolutions=[10,20,60]):
    """
    Reads an S2 granule XML and copies the data into the ENVI format
    :param pathXML:
    :param pathDst:
    :param delete_temporary_vrt:
    :return:
    """
    drv = 'ENVI'

    vrts = sentinel2_granule_to_vrt(pathXML, pathDst, resolutions=resolutions)
    if vrts:
        vrts = sorted(vrts)

        for pathVRT in vrts:
            dn = os.path.dirname(pathVRT)
            bn = os.path.splitext(os.path.basename(pathVRT))[0]

            pathDst = os.path.join(dn, '{}.bsq'.format(bn))
            gdal_to_gdal(pathVRT, pathDst, drv=drv)

            if delete_temporary_vrt:
                os.remove(pathVRT)
    pass

def printAllMetadata(p):
    ds = gdal.Open(p)

    import xml.etree.ElementTree as ET

    def printMetadata(gdalObject):
        for domain in gdalObject.GetMetadataDomainList():
            print('Metadata domain: "{}"'.format(domain))
            domainData = gdalObject.GetMetadata_Dict(domain)
            for key, value in domainData.items():
                if key.startswith('<?xml'):
                    xmlText = key+'='+value
                    tree = ET.fromstring(xmlText)

                    print(key, ' XML Dump:')
                    ET.dump(tree)

                else:
                    print(key,'=',value)
            print('')

    print('Image metadata')
    printMetadata(ds)
    for b in range(ds.RasterCount):
        print('Band {} metadata:'.format(b+1))
        band = ds.GetRasterBand(b+1)
        printMetadata(band)
        print('---')


def test():

    p = r'Q:\Rohdaten\S2A\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE\GRANULE\S2A_OPER_MSI_L1C_TL_SGS__20151224T161331_A002636_T32UNC_N02.01\IMG_DATA\S2A_OPER_MSI_L1C_TL_SGS__20151224T161331_A002636_T32UNC_B02.jp2'
    printAllMetadata(p)
    #for drv in [gdal.GetDriver(i) for i in range(gdal.GetDriverCount())]: drv.GetDescription()
    resolutions = [20]
    if False:
        pathXML_Granule = r'Q:\Rohdaten\S2A\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE'
        pathXML_Granule = r'Q:\Rohdaten\S2A\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE\GRANULE\S2A_OPER_MSI_L1C_TL_SGS__20151224T161331_A002636_T32UPD_N02.01\S2A_OPER_MTD_L1C_TL_SGS__20151224T161331_A002636_T32UPD.xml'
        pathDst = r'C:\Users\geo_beja\Documents\testS2.vrt'
        pathDst = r'T:\BJ_S2_L1C_Import\importedGranule.vrt'

        sentinel2_granule_to_envi(pathXML_Granule, pathDst, delete_temporary_vrt=False, resolutions=resolutions)

    if True:
        pathXML_Strip = r'Q:\Rohdaten\S2A\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE\S2A_OPER_MTD_SAFL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.xml'
        dirDstStrip = r'T:\BJ_S2_L1C_Import\importedStrip'
        #sentinel2_strip_to_vrt(pathXML_Strip, dirDstStrip, tiledirs=True)
        sentinel2_strip_to_envi(pathXML_Strip, dirDstStrip, resolutions=resolutions, tiledirs=True)

if __name__ == '__main__':
    import enmapbox.gdal_tools
    enmapbox.gdal_tools.initializeGDAL()
    test()
    print('Done')