import os, re, pathlib, datetime
import geoip2.database
from osgeo import ogr, osr
import urllib3

from enmapbox.gui.utils import file_search
dirLogfiles = r'R:\Project_EnMAP-Box\released_versions\FTP-ServerStats\Logfiles'

pathGeoLiteDB = r'C:\Users\geo_beja\Downloads\GeoLite2-City.mmdb'
#pathFTPStats = r'R:\Project_EnMAP-Box\documents\DownloadStatistics\120619_FileZilla Server.log'
dirResults = r'R:\Project_EnMAP-Box\released_versions'
pathShpOut = os.path.join(dirResults, 'statsShape.shp')

lines = []
for pathFTPStats in file_search(dirLogfiles, '*Server.log'):
    with open(pathFTPStats) as f:
        lines.extend(f.readlines())

FILES = {}
IPs = {}
#t = r'(000465) 19.06.2012 12:11:22 - enmapboxuser (141.20.141.25)> RETR /EnMAP-Box_v1.3/EnMAP-Box_win64.zip'
#
regex = re.compile(r'.*\((\d+)\) (\d+.\d+.\d+).* (enmapboxuser|enmapboxdev) \(([^)]+)\)> RETR (.*zip)$')
done = set()
for l in lines:

    match = regex.search(l)
    if match:
        id = match.group(1)
        date = match.group(2)
        dd,mm,yy = [int(v) for v in date.split('.')]
        assert yy > 2000
        date = datetime.date(yy,mm,dd)
        usr = match.group(3)
        ip = match.group(4)
        file = match.group(5)
        file = os.path.basename(file)
        t = (ip, usr, date, file)
        if t in done:
            continue

        if not file in FILES:
            FILES[file] = []

        FILES[file].append(t)

        if not ip in IPs.keys():
            IPs[ip] = []
        IPs[ip] = t

        done.add(t)


alldates = [t[2] for t in done ]
print('from {} to {}'.format(min(alldates), max(alldates)))

for file in sorted(list(FILES.keys())):
    cnt = len(FILES[file])
    print('{}\t{}'.format(file, cnt))

reader = geoip2.database.Reader(pathGeoLiteDB)
LOCATIONS = {}
for ip, t in IPs.items():
    response = reader.city(ip)
    latLon = (response.location.latitude, response.location.longitude)
    city = response.city.name
    cnt = len(t)
    if latLon not in LOCATIONS.keys():
        LOCATIONS[latLon] = (cnt, city)
    else:
        cntOld, city = LOCATIONS[latLon]
        LOCATIONS[latLon] = (cntOld + cnt, city)

for latLon, info in LOCATIONS.items():
    print('{}\t{}'.format(latLon, info))


dsMem = ogr.GetDriverByName('Memory').CreateDataSource('')
assert isinstance(dsMem, ogr.DataSource)
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
lyr = dsMem.CreateLayer('downloads', srs=srs, geom_type=ogr.wkbPoint)
assert isinstance(lyr, ogr.Layer)
lyr.CreateField(ogr.FieldDefn('dwnlds', ogr.OFTInteger))
lyr.CreateField(ogr.FieldDefn('city', ogr.OFTString))
ldef = lyr.GetLayerDefn()
assert isinstance(ldef, ogr.FeatureDefn)


for latLon, info in LOCATIONS.items():
    lat, lon = latLon
    cnts, city = info
    feature = ogr.Feature(ldef)
    assert isinstance(feature, ogr.Feature)
    pt = ogr.Geometry(ogr.wkbPoint)
    assert isinstance(pt, ogr.Geometry)
    pt.AddPoint(lon, lat)
    feature.SetGeometry(pt)

    feature.SetField('city', city)
    feature.SetField('dwnlds', cnts)
    lyr.CreateFeature(feature)
dsMem.FlushCache()

ogr.GetDriverByName('ESRI Shapefile').CopyDataSource(dsMem, pathShpOut)
