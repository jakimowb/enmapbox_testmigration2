__author__ = 'janzandr'
import os

import numpy
import ogr

from enmapbox.hub.collections import Bunch


def deleteShapefile(shp):
    #driver =  ogr.GetDriverByName('ESRI Shapefile')
    #if os.path.exists(shp): driver.DeleteDataSource(shp)

    for extension in ['.dbf','.prj','.qpj','.shp','.shx']:
        enmapbox.hub.file.remove(shp.replace('.shp', extension))

def intersect(indir, outname, inname1, inname2):
    ogr.UseExceptions()
    datasource = ogr.Open(indir, True)

    # create layer
    SQL = """
        SELECT ST_Intersection(A.geometry, B.geometry) AS geometry, A.*, B.*
        FROM {0} A, {1} B
        WHERE ST_Intersects(A.geometry, B.geometry);
    """.format(inname1,inname2)
    layer = datasource.ExecuteSQL(SQL, dialect='SQLITE')

    # copy result back to datasource as a new shapefile
    deleteShapefile(os.path.join(indir, outname+'.shp'))
    layer2 = datasource.CopyLayer(layer, outname)

    # save, close
    layer = layer2 = None
    datasource.Destroy()

def getAttributes(shp, fields):
    shpfile = ogr.Open(shp)
    layer = shpfile.GetLayer(0)
    numberFeatures = layer.GetFeatureCount()
    result = Bunch()
    for field in fields:
        result[field] = numpy.array([layer.GetFeature(i).GetField(field) for i in range(numberFeatures)])
    shpfile.Destroy()
    return result

def getExtent(shp):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataset = driver.Open(shp, 0)
    layer = dataset.GetLayer()
    extent = numpy.array(layer.GetExtent())[[0,2,1,3]] # comes as [left, right, top, down) -> resort to [ul, lr]
    dataset.Destroy()
    return extent

def buffer(inshp, outshp, distance, quadsects):

    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDS = driver.Open(inshp, 0)
    inLayer = inDS.GetLayer()
    deleteShapefile(outshp)
    outDS = driver.CreateDataSource(outshp)
    outLayer = outDS.CreateLayer('mylayer', geom_type=ogr.wkbPolygon)

    # use the input FieldDefn to add a field to the output
    fieldDefn = inLayer.GetFeature(0).GetFieldDefnRef('ZONE')
    outLayer.CreateField(fieldDefn)

    # get the FeatureDefn for the output layer
    featureDefn = outLayer.GetLayerDefn()

    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    for inFeature in [inLayer.GetFeature(i) for i in range(inLayer.GetFeatureCount())]:

        # create a new feature
        outFeature = ogr.Feature(featureDefn)
        inGeometry = inFeature.GetGeometryRef()
        outGeometry = inGeometry.Buffer(distance, quadsects)
        outFeature.SetGeometry(outGeometry)
        outFeature.SetField('ZONE', inFeature.GetField('ZONE'))

        # add the feature to the output layer
        outLayer.CreateFeature(outFeature)

        # destroy the features
        inFeature.Destroy()
        outFeature.Destroy()

    # close the data sources
    inDS.Destroy(); outDS.Destroy()



if __name__ == '__main__':
    pass
    # indir = r'C:\Users\janzandr\Desktop\shapefiles\_'
    # name_roi_zone_intersect = 'utm_roi_intersection'
    # shp_roi_zone_intersect = os.path.join(indir, name_roi_zone_intersect+'.shp')
    # deleteShapefile(shp_roi_zone_intersect)
    # intersect(indir, name_roi_zone_intersect, 'utm_wgs84', 'roi_wgs84')
    #
    # # get utm zones in intersection
    #
    # values = getValues(shp_roi_zone_intersect, ['ZONE'])
    # zones = numpy.unique(values.ZONE)
    # zone = zones[0]
    #
    # # add buffer to utm zones
    # bufferDistance = 300 # in meter
    # bufferQuadsects = 10
    # shp_zone = os.path.join(indir, 'utm'+str(zone)+'n.shp')
    # shp_zoneBuffered = os.path.join(indir, 'utm'+str(zone)+'n_buffer'+str(bufferDistance)+'.shp')
    #
    # buffer(shp_zone, shp_zoneBuffered)
    #
