__author__ = 'janzandr'
import hub.rs.landsat
import xml.etree.ElementTree as ElementTree

def parseLandsatMeta(mtlfilename, espafilename):

    mtl = hub.rs.landsat.parseMTL(mtlfilename)
    tree = ElementTree.parse(espafilename)
    root = tree.getroot()

    metas = {'AcqDate': str(mtl['DATE_ACQUIRED']), #'1996-10-24',
             'AcqTime': mtl['SCENE_CENTER_TIME'],#'05:06:19',
             #'Additional': ["[['LMAX'- '193.000'- '365.000'- '264.000'- '221.000'- '30.200'- '15.303'- '16.500']- ['LMIN'- '-1.520'- '-2.840'- '-1.170'- '-1.510'- '-0.370'- '1.238'- '-0.150']- ['QCALMAX'- '255.0'- '255.0'- '255.0'- '255.0'- '255.0'- '255.0'- '255.0']- ['QCALMIN'- '1.0'- '1.0'- '1.0'- '1.0'- '1.0'- '1.0'- '1.0']]", "['REFERENCE_DATUM'- 'WGS84']", "['REFERENCE_ELLIPSOID'- 'WGS84']", "['GRID_CELL_SIZE_THM'- '30.000']", "['GRID_CELL_SIZE_REF'- '30.000']", "['ORIENTATION'- 'NUP']", "['RESAMPLING_OPTION'- 'CC']", "['MAP_PROJECTION'- 'UTM']", "['ZONE_NUMBER'- '43']"],
             #'EarthSunDist': mtl['EARTH_SUN_DISTANCE'],#0.99455305154098',
             #'FieldOfView': '14.92',
             #'IncidenceAngle': '-9999.99',
             #'Metafile': mtlfilename,
             #'PhysUnit': 'TOA_Reflectance in [0-10000]',
             'ProcLCode': mtl['DATA_TYPE'], #'L1T',
             #'Quality': ["['STRIPING_BAND1'- 'NONE']", "['STRIPING_BAND2'- 'NONE']", "['STRIPING_BAND3'- 'NONE']", "['STRIPING_BAND4'- 'NONE']", "['STRIPING_BAND5'- 'NONE']", "['STRIPING_BAND6'- 'NONE']", "['STRIPING_BAND7'- 'NONE']", "['BANDING'- 'N']", "['COHERENT_NOISE'- 'N']", "['MEMORY_EFFECT'- 'Y']", "['SCAN_CORRELATED_SHIFT'- 'Y']", "['INOPERABLE_DETECTORS'- 'N']", "['DROPPED_LINES'- 'N']"],
             'Satellite': mtl['SPACECRAFT_ID'],#'Landsat-5',
             'SceneID': mtl['LANDSAT_SCENE_ID'], #'L',
             'Sensor': mtl['SENSOR_ID'], #'TM',
             #'SolIrradiance': ['1962.56', '1819.19', '1545.76', '1029.95', '211.99', '78.42'],
             #'Subsystem': 'SAM',
             'SunAzimuth': mtl['SUN_AZIMUTH'],#'149.4789685',
             'SunElevation': mtl['SUN_ELEVATION'],#'32.5736115',
             #'ViewingAngle': '0',
             #'bands': '6',
             #'byte order': '0',
             #'coordinate system string': 'PROJCS["WGS_1984_UTM_Zone_43N",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",75],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]',
             #'corner coordinates lonlat': '[[72.0968572, 41.2628323], [75.0585286, 41.2994376], [72.1808746, 39.2706455], [75.056832, 39.304773]]',
             #'band names' : [i.get('name') for i in root.findall("./{http://espa.cr.usgs.gov/v1.2}bands/{http://espa.cr.usgs.gov/v1.2}band")],
             #'reflectance gain values' : [i.get('scale_factor', '') for i in root.findall("./{http://espa.cr.usgs.gov/v1.2}bands/{http://espa.cr.usgs.gov/v1.2}band")],
             #'data gain values': ['0.7658267716535433', '1.4481889763779527', '1.043976377952756', '0.876023622047244', '0.12035433070866142', '0.0655511811023622'],
             #'data offset values': ['-2.2858267716535434', '-4.288188976377953', '-2.213976377952756', '-2.386023622047244', '-0.4903543307086614', '-0.2155511811023622'],
             #'LayerBandsAssignment': ['1', '2', '3', '4', '5', '7'],
             #'data type': '2',
             #'file type': 'ENVI Standard',
             #'gResolution': '-99.0',
             #'header offset': '0',
             #'interleave': 'bsq',
             #'lines': '7381',
             #'map info': ['UTM', '1', '1', '256785.0', '4572015.0', '30.0', '30.0', '43', 'North', 'WGS-84'],
             #'overpass duraction sec': '24.6698677383',
             #'samples': '8271',
             #'scene length': '184.836174615',
             }

    # new keys (not used by Daniel)
    #metas['software version'] = [i.text for i in root.findall("./{http://espa.cr.usgs.gov/v1.2}bands/{http://espa.cr.usgs.gov/v1.2}band/{http://espa.cr.usgs.gov/v1.2}app_version")]
    metas['geometric accuracy'] = mtl.get('GEOMETRIC_RMSE_MODEL', 0)

    #'bandwidths': ['64.0', '80.0', '66.0', '127.0', '216.0', '251.0'],
    #'wavelength': ['486.3', '570.57', '660.6', '838.15', '1677.11', '2217.24'],
    #'wavelength units': 'Nanometers'

    return metas


if __name__ == '__main__':
    mtlfilename = r'H:\EuropeanDataCube\landsat\184\026\LC81840262013159LGN00\LC81840262013159LGN00_MTL.txt'
    espafilename = r'H:\EuropeanDataCube\landsat\184\026\LC81840262013159LGN00\LC81840262013159LGN00.xml'
  #  espafilename = r'H:\EuropeanDataCube\landsat\184\026\LE71840261999337SGS00\LE71840261999337SGS00.xml'
    espafilename = r'H:\EuropeanDataCube\landsat\184\026\LT41840261988195XXX04\LT41840261988195XXX04.xml'

    meta = parseLandsatMeta(mtlfilename, espafilename)
    print(meta['band names'])
#    for key in sorted(meta.keys()):print(key+':',meta[key])
