import hub.gdal.util, hub.ogr.util, hub.file, hub.rs.landsat
from hub.timing import tic, toc
import os, shutil, ogr

def moveShp(folder):
    print(folder)
    shpfolder = os.path.join(folder, 'Shapefiles')
    if os.path.exists(shpfolder):
        for file in hub.file.filesearch(shpfolder,'*.*'):
            shutil.copyfile(file, os.path.join(folder, os.path.basename(file)))
    shpfolder = os.path.join(folder, 'GIS_Files')
    if os.path.exists(shpfolder):
        for file in hub.file.filesearch(shpfolder,'*.*'):
            shutil.copyfile(file, os.path.join(folder, os.path.basename(file)))

def createBuffer(folder, buffdist):
    print(folder)
    shpfile = os.path.join(folder, os.path.basename(folder))+'.shp'
    shpfileBuffer = os.path.join(folder, os.path.basename(folder))+'_B'+str(buffdist)+'.shp'
    if not os.path.exists(shpfile): return
    print(shpfile)
    ds=ogr.Open(shpfile)
    drv=ds.GetDriver()
    if os.path.exists(shpfileBuffer):
        drv.DeleteDataSource(shpfileBuffer)
    drv.CopyDataSource(ds,shpfileBuffer)
    ds.Destroy()

    ds=ogr.Open(shpfileBuffer,1)
    lyr=ds.GetLayer(0)
    for i in range(0,lyr.GetFeatureCount()):
        feat=lyr.GetFeature(i)
        lyr.DeleteFeature(i)
        geom=feat.GetGeometryRef()
        feat.SetGeometry(geom.Buffer(float(buffdist)))
        lyr.CreateFeature(feat)
    ds.Destroy()

def checkCRS(folder):
    shpfile = os.path.join(folder, os.path.basename(folder))+'.shp'
    try:
        ds=ogr.Open(shpfile)
        layer=ds.GetLayer(0)
        layerSRS = layer.GetSpatialRef()
        ds.Destroy()
        noSRS = layerSRS.ExportToWkt()[0:25] != 'PROJCS["WGS_1984_UTM_Zone'
        if noSRS:
            print(folder)
            print(shpfile)
            print(layerSRS.ExportToWkt()[0:])
            #outshpfile = os.path.join(r't:\test', os.path.basename(folder)+'.shp')
            #hub.ogr.util.ogr2ogr(outshpfile, shpfile, '-a_srs EPSG:32632', verbose=True)

    except:
        print('problem occured')
        print(shpfile)

if __name__ == '__main__':
    root = 'H:\EuropeanDataCube\gis\MGRS_100km_1MIL_Files'
    folders = [os.path.join(root, folder) for folder in os.listdir(root)]
    for folder in folders:
        createBuffer(folder,100)







