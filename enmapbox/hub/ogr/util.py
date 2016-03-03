import enmapbox.hub.file
import os
import subprocess


def ogr2ogr(outfile, infile, options, verbose=True):

    enmapbox.hub.file.mkdir(os.path.dirname(outfile))
    enmapbox.hub.file.remove(outfile)

    cmd = 'ogr2ogr '+options+' '+outfile+' '+infile
    if verbose: print(cmd)
    subprocess.call(cmd, shell=True)

if __name__ == '__main__':

    infile = r'C:\Users\janzandr\Desktop\shapefiles\_\roi_wgs84.shp'
    outfile = r't:\roi_utm32.shp'
    options = '-t_srs EPSG:32632'
    ogr2ogr(outfile,infile, options)
