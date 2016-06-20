import hub.file, hub.gdal.util, hub.envi, hub.gdal.api
import subprocess, os, sys

root = r'H:\EuropeanDataCube\auxiliary\elevation\srtm1arc'
infiles = hub.file.filesearch(root, '*.bil')
outfileVRT = root+'_mosaick.vrt'
if not os.path.exists(outfileVRT):
    hub.gdal.util.mosaic(outfileVRT,infiles,)
outfileENVI = outfileVRT.replace('.vrt','.img')
if not os.path.exists(outfileENVI):
    hub.gdal.util.gdal_translate(outfileENVI, outfileVRT, '-of ENVI')

cubefolder = r'H:\EuropeanDataCube\testCaseAR_Big\cubes'
reffiles = hub.file.filesearch(cubefolder, 'bandcfmask.img')
for reffile in reffiles:
    demFile = reffile.replace('cubes','elevation').replace('bandcfmask.img','dem.img')

    meta = hub.gdal.api.GDALMeta(reffile)
    options =  ' -of ENVI -r cubic -overwrite'
    options += ' -te '+' '.join([str(v) for v in meta.boundingBox2])
    options += ' -tr '+str(meta.pixelXSize)+' '+str(abs(meta.pixelYSize))
    options += ' -t_srs '+meta.Projection

    hub.gdal.util.gdalwarp(demFile, outfileENVI, options)
    hub.gdal.util.gdaldem(demFile.replace('dem','slope'), demFile, 'slope -of ENVI')
    hub.gdal.util.gdaldem(demFile.replace('dem','aspect'), demFile, 'aspect -of ENVI')


sys.exit()


#root = r'H:\EuropeanDataCube\auxiliary\elevation\demTest'
#input_dem   = os.path.join(root, 'dem.img')

input_dem   = outfileENVI

# terrain slope angle
output_slope_map = os.path.join(root, 'slope.img')
options = '-of ENVI -s 111120120'
cmd ='gdaldem slope options input_dem output_slope_map'
cmd = cmd.replace('input_dem', input_dem)
cmd = cmd.replace('output_slope_map', output_slope_map)
cmd = cmd.replace('options', options)
print(cmd)
subprocess.call(cmd, shell=True)

# topographic aspect angle
output_aspect_map = os.path.join(root, 'aspect.img')
options = '-of ENVI' # any other options needed?
cmd ='gdaldem aspect options input_dem output_aspect_map'
cmd = cmd.replace('input_dem', input_dem)
cmd = cmd.replace('output_aspect_map', output_aspect_map)
cmd = cmd.replace('options', options)
print(cmd)
subprocess.call(cmd, shell=True)
