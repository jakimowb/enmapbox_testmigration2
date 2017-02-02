__author__ = 'janzandr'
import hub.collections
import calendar, gdal
import xml.etree.ElementTree as ElementTree

def parseMTL(mtlfilename, filter=False):
    with open(mtlfilename) as file:
        lines = [line for line in file]

    metas = [line.strip().split(' = ') for line in lines]
    metas = [meta for meta in metas if len(meta) == 2]

    keyfilter = ['CLOUD_COVER', 'CPF_NAME', 'DATA_TYPE', 'DATE_ACQUIRED', 'DATUM', 'ELEVATION_SOURCE', 'ELLIPSOID',
            'GEOMETRIC_RMSE_MODEL', 'GEOMETRIC_RMSE_MODEL_X', 'GEOMETRIC_RMSE_MODEL_Y', 'GROUND_CONTROL_POINTS_MODEL',
            'LANDSAT_SCENE_ID', 'MAP_PROJECTION', 'METADATA_FILE_NAME', 'ORIENTATION', 'ORIGIN', 'OUTPUT_FORMAT',
            'PROCESSING_SOFTWARE_VERSION', 'REQUEST_ID', 'RESAMPLING_OPTION', 'SCENE_CENTER_TIME', 'SENSOR_ID',
            'SPACECRAFT_ID', 'STATION_ID', 'SUN_AZIMUTH', 'SUN_ELEVATION', 'UTM_ZONE', 'WRS_PATH', 'WRS_ROW']

    if filter:
        metas = {key:value.strip('"') for (key, value) in metas if key in keyfilter}
    else:
        metas = {key:value.strip('"') for (key, value) in metas}

    #metas = {key:value for (key, value) in metas if key in keyfilter}
    return metas

def getSceneIDInfo(sceneID):
    result = hub.collections.Bunch()
    result.id      = sceneID
    result.sensor  = sceneID[0:3]
    result.pathrow = sceneID[3:9]
    result.year    = int(sceneID[9:13])
    result.doy     = int(sceneID[13:16])
    result.yeardoy = sceneID[9:16]
    result.station = sceneID[16:19]
    result.decimalyear = result.year+result.doy/(366. if calendar.isleap(result.year) else 365.)

    date= calendar.datetime.datetime(result.year, 1, 1) + calendar.datetime.timedelta(result.doy - 1)
    result.day = date.day
    result.month = date.month
    return result

if __name__ == '__main__':
    mtlfilename = r'H:\EuropeanDataCube\landsat\184\026\LC81840262013159LGN00\LC81840262013159LGN00_MTL.txt'
    xmlfilename = r'H:\EuropeanDataCube\landsat\184\026\LC81840262013159LGN00\LC81840262013159LGN00.xml'

    #print(parseMTL(mtlfilename))
    metas = parseESPA(xmlfilename)
    print(metas['bands'])
