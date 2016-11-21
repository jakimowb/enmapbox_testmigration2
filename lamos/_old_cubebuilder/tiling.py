import hub.gdal.util, hub.gdal.api, hub.file, hub.rs.landsat
from hub.timing import tic, toc
import os, ogr, osr, numpy, multiprocessing.pool, datetime

def getMGRSTiles(pathrow, shpfile):

    dataSource = ogr.Open(shpfile)
    layer = dataSource.GetLayer(0)
    mgrstiles = list()
    for feature in layer:
        if str(int(feature.GetField('WRSPR'))) == str(pathrow):
            tilename = feature.GetField('GRID1MIL')+ feature.GetField('GRID100K')
            mgrstiles.append((tilename)) # (name, geometry)

    return mgrstiles

def tileScene((scenefolder, outfolder, mgrstiles)):

    sceneID = os.path.split(scenefolder)[-1]

    # define layer
    #               name               nodata
    layers = [('_BQA.img',                   '0'),
              ('_cfmask.img',                '255'),
              ('_cfmask_conf.img',           '255'),
              ('_land_water_mask.img',       '???'),   # NoData nicht definiert
              ('_sr_adjacent_cloud_qa.img',  '???'),   # NoData nicht definiert
              ('_sr_atmos_opacity.img',      '-9999'),

              ('_sr_band1.img',   '-9999'),
              ('_sr_band2.img',   '-9999'),
              ('_sr_band3.img',   '-9999'),
              ('_sr_band4.img',   '-9999'),
              ('_sr_band5.img',   '-9999'),
              ('_sr_band6.img',   '-9999'),
              ('_sr_band7.img',   '-9999'),

              ('_sr_cloud_qa.img',        '???'),    # NoData nicht definiert
              ('_sr_cloud.img',           '0'),
              ('_sr_cloud_shadow_qa.img', '???'), # NoData nicht definiert
              ('_sr_ddv_qa',              '???'), # NoData nicht definiert
              ('_sr_fill_qa',             '???'), # NoData nicht definiert
              ('_sr_land_water_qa.img',   '???'), # NoData nicht definiert
              ('_sr_snow_qa.img',         '???'), # NoData nicht definiert

              ('_toa_band6.img',    '-9999'),
              ('_toa_band10.img',   '-9999'),
              ('_toa_band11.img',   '-9999'),
              ('_toa_band6_qa.img', '1'),
              ('_toa_qa.img',       '1'),
              ]


    #layers = [('_sr_band3.img',   '-9999', defaultResampling)]

    print('  cut '+sceneID)
    for layername, nodata in layers:

        infile = os.path.join(scenefolder, sceneID+layername)

        if not os.path.exists(infile):
            continue

        # outroot = os.path.join(scenefolder, 'mgrs')

        pixelGridOffset = numpy.array((15,15))
        pixelGridSize = numpy.array((30,30))
        resolution = str(pixelGridSize[0])+' '+str(pixelGridSize[1])

        for tilename in mgrstiles:
            shpfile = r'H:\EuropeanDataCube\gis\reference_systems\mgrs\MGRS_100km_1MIL_Files\MGRS_100kmSQ_ID_'+tilename[0:3]+'\MGRS_100kmSQ_ID_'+tilename[0:3]+'_B100.shp'
            utmzoneMGRS = tilename[0:2]

            outroot = os.path.join(outfolder, utmzoneMGRS, tilename)
            hub.file.mkdir((outroot))
            outfile = os.path.join(outroot, sceneID, os.path.splitext(os.path.basename(infile))[0]+'_'+tilename+'.vrt' )
            if not os.path.exists(outfile):

                t_srs = ' -t_srs  EPSG:326'+utmzoneMGRS # always reproject to assure UTM XXN Zone

                # NoData option
                if nodata == '???':
                    no_data = ''
                else:
                    no_data = ' -srcnodata '+nodata+' -dstnodata '+nodata

                # snap tile to global pixel grid

                def getBoundingBox(tilename):
                    dataSource = ogr.Open(shpfile)
                    layer = dataSource.GetLayer(0)

                    for feature in layer:
                        if feature.GetField('MGRS') == tilename:
                            points = feature.geometry().GetGeometryRef(0).GetPoints()
                            xmin, ymin = numpy.min(numpy.array(points), axis=0)
                            xmax, ymax = numpy.max(numpy.array(points), axis=0)
                            tileboundingbox = {'xmin':xmin, 'ymin':ymin, 'xmax':xmax, 'ymax':ymax}
                    return tileboundingbox

                def snap(x, size, offset):
                    return x-((x-offset) % size)

                tileboundingbox = getBoundingBox(tilename)

                xmin = snap(tileboundingbox['xmin'], pixelGridSize[0], pixelGridOffset[0])
                xmax = snap(tileboundingbox['xmax'], pixelGridSize[0], pixelGridOffset[0])
                ymin = snap(tileboundingbox['ymin'], pixelGridSize[1], pixelGridOffset[1])
                ymax = snap(tileboundingbox['ymax'], pixelGridSize[1], pixelGridOffset[1])

                te = ' -te '+str(xmin)+' '+str(ymin)+' '+str(xmax)+' '+str(ymax)

                # create VRT file
                hub.gdal.util.gdalwarp(outfile, infile, '-of VRT -overwrite '+t_srs+' -tr '+resolution+no_data+te+' -cwhere "MGRS=\''+tilename+'\'" -cutline '+shpfile, verbose=0)

                # copy homogenised metadata from MTL and ESPA metafiles to VRT file
                mtlfile = os.path.join(scenefolder, sceneID+'_MTL.txt')
                espafile = os.path.join(scenefolder, sceneID+'.xml')
                meta = hub.rs.virtual.parseLandsatMeta(mtlfile, espafile)
                gdalMeta = hub.gdal.api.GDALMeta(outfile)
                gdalMeta.setBandNames([infile])
                gdalMeta.setMetadataItem('MTLFile', [mtlfile], mapToBands=True)
                gdalMeta.setMetadataItem('ESPAFile', [espafile], mapToBands=True)
                for key in ['AcqDate', 'AcqTime', 'ProcLCode', 'Satellite', 'SceneID', 'Sensor', 'SunAzimuth', 'SunElevation', 'geometric accuracy']:
                    gdalMeta.setMetadataItem(key, [meta[key]], mapToBands=True)
                gdalMeta.writeMeta(outfile)

#            print('  ...done '+outfile)
#        print('')

def tileFootprint(footprint, sensorfolder, tilesfolder, tilingshapefile, timerange=None):

    footprintFolder = os.path.join(sensorfolder, str(footprint)[0:3], str(footprint)[3:])
    scenefolders = [os.path.join(footprintFolder, scenefolder) for scenefolder in os.listdir(footprintFolder)]

    # get MGRS tiles covered by the footprint
    mgrstiles = getMGRSTiles(str(footprint), tilingshapefile)

    tic('tiling footprint '+str(footprint))
    if 1: # use multithreading?
        for scenefolder in scenefolders:
            date = datetime.date(int(scenefolder[-12:-8]),7,1)
            if date > timerange[0] and date < timerange[1]:
                tileScene((scenefolder, tilesfolder, mgrstiles))
    else:
        args = [(scenefolder, tilesfolder, mgrstiles) for scenefolder in scenefolders]
        import multiprocessing.pool
        pool = multiprocessing.pool.ThreadPool(20)
        pool.map(tileScene, args)
        try: pool.terminate()
        except: pass
    toc()
