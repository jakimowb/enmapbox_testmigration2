from osgeo import ogr, osr, gdal, gdal_array

import xml.etree

import os, re, fnmatch, sys, subprocess

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
            drive_map[drive] = path


regex_is_win_drive = re.compile(r'^[A-Z]:')

def getUNCPath(path):
    path = os.path.normpath(path)
    if is_windows:
        match = regex_is_win_drive.search(path)
        if match:
            path = drive_map[match.group()] + path[2:]
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
    data = src.GetMetadata(domain)
    for key, value in data.items():
        #print('Copy metadata: {} : {} {}'.format(domain, key, value))
        #print((key, value, domain))
        dst.SetMetadataItem(key, value, domain)

def callback(a):
    print('callback')
    s  = ""
    pass


def sentinel2_stip_to_vrt(pathXML, dirDst):
    pass



def sentinel2_granule_to_vrt(pathXML, pathDst, mode='all'):
    assert os.path.splitext(pathXML)[1].lower() == '.xml'

    import xml.etree.ElementTree as ET

    #fileType, typeID = parse_S2_product(os.path.basename(pathXML))

    tree = ET.parse(pathXML)

    block_size= 256



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
            dt = ds.GetRasterBand(1).DataType
            key = (ns, nl, gt, pr, dt)
            if key not in sources.keys():
                sources[key] = list()
            #todo: improve path handling to allow for absolute paths

            #sources[key].append(getUNCPath(path))

            sources[key].append(path)

    else:
        raise Exception('Unsupported product type:{}'.format(typeID))

    dn = os.path.dirname(pathDst)
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

    if len(results) == 0:
        results = None

    return results

def sentinel2_granule_to_envi(pathXML, pathDst, delete_temporary_vrt=True):
    """
    Reads an S2 granule XML and copies the data into the ENVI format
    :param pathXML:
    :param pathDst:
    :param delete_temporary_vrt:
    :return:
    """
    drvDst = gdal.GetDriverByName('ENVI')

    vrts = sorted(sentinel2_granule_to_vrt(pathXML, pathDst))

    for pathVRT in vrts:
        dn = os.path.dirname(pathVRT)
        os.makedirs(dn, exist_ok=True)
        bn = os.path.splitext(os.path.basename(pathVRT))[0]

        pathDst = os.path.join(dn, '{}.bsq'.format(bn))
        print('Copy {} -> {}...'.format(pathVRT, pathDst))
        dsVRT = gdal.Open(pathVRT)
        dsDst = drvDst.CreateCopy(pathDst, dsVRT)

        for domain in dsVRT.GetMetadataDomainList():
           copyMetadata(dsVRT,dsDst, domain)

        for b in range(dsVRT.RasterCount):
            bandSrc =dsVRT.GetRasterBand(b+1)
            bandDst = dsDst.GetRasterBand(b+1)
            bandDst.SetDescription(bandSrc.GetDescription())
            no_data = bandSrc.GetNoDataValue()
            if no_data is not None:
                bandDst.SetNoDataValue(no_data)
        dsDst = None
        if delete_temporary_vrt:
            os.remove(pathVRT)
    pass



def test():
    pathXML = r'Q:\Rohdaten\S2A\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE'
    pathXML = r'Q:\Rohdaten\S2A\S2A_OPER_PRD_MSIL1C_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE\GRANULE\S2A_OPER_MSI_L1C_TL_SGS__20151224T161331_A002636_T32UPD_N02.01\S2A_OPER_MTD_L1C_TL_SGS__20151224T161331_A002636_T32UPD.xml'
    pathDst = r'C:\Users\geo_beja\Documents\testS2.vrt'
    pathDst = r'T:\BJ_S2_L1C_Import\importedGranule.vrt'

    sentinel2_granule_to_envi(pathXML, pathDst, delete_temporary_vrt=False)


if __name__ == '__main__':

    test()
    print('Done')