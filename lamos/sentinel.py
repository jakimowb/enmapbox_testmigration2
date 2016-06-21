import os
import fnmatch
from subprocess import call
from subprocess import check_call


try:  # check if gdal is in path
    check_call('gdal_translate', shell=True)
except:  # pragma no cover
    print('Adding OSGeo4W64 to PATH variable.')
    os_environ_path = os.environ['PATH']
    os.environ['PATH'] = r"c:\OSGeo4W64\bin;"+os_environ_path
    os.environ['GDAL_DATA'] = r'c:\OSGeo4W64\share\\gdal'
    os.environ['GDAL_DRIVER_PATH'] = r'c:\OSGeo4W64\bin\gdalplugins'


s2pixel = {'B01': 60, 'B02': 10, 'B03': 10, 'B04': 10, 'B05': 20, 'B06': 20, 'B07': 20,
           'B08': 10, 'B8A': 20, 'B09': 60, 'B10': 60, 'B11': 20, 'B12': 20}

s2bandcombi = {'r10': ['B02', 'B03', 'B04', 'B08'],
               'r20': ['B05', 'B06', 'B07', 'B8A'],
               'r60': ['B01', 'B09', 'B10'],
               'vis': ['B02', 'B03', 'B04', 'B08'],
               'ldcm': ['B02', 'B03', 'B04', 'B8A', 'B11', 'B12'],
               'land': ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08',  'B8A', 'B11', 'B12'],
               'all': ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08',  'B8A', 'B09', 'B10',  'B11', 'B12']}

s2view = {'r10': {'bandcombi': 'r10', 'resolution': 10},
          'r20': {'bandcombi': 'r20', 'resolution': 20},
          'r60': {'bandcombi': 'r60', 'resolution': 60},
          'vis': {'bandcombi': 'vis', 'resolution': 10},
          'ldcm10': {'bandcombi': 'ldcm', 'resolution': 10},
          'ldcm20': {'bandcombi': 'ldcm', 'resolution': 20},
          'ldcm30': {'bandcombi': 'ldcm', 'resolution': 30},
          'land10': {'bandcombi': 'land', 'resolution': 10},
          'land20': {'bandcombi': 'land', 'resolution': 20},
          'land30': {'bandcombi': 'land', 'resolution': 30},
          'all10': {'bandcombi': 'all', 'resolution': 10}}


def gdalbuildvrt(in_files, vrt_file, tr=None, stack=True, quiet=True, srcnodata=None):

    if not os.path.exists(os.path.dirname(vrt_file)):
        os.makedirs(os.path.dirname(vrt_file))

    listfile = vrt_file + '_tmp'
    with open(listfile, 'w') as fl:
        fl.writelines(["%s\n" % file for file in in_files])

    cmd = 'gdalbuildvrt '
    if quiet:
        cmd += '-q '

    if srcnodata is not None:
        cmd += '-srcnodata %s ' % srcnodata

    if stack:
        cmd += '-separate '

    if tr is not None:
        cmd += '-resolution user -tr %s %s ' % (tr, tr)

    cmd += '-input_file_list '+listfile+' '+vrt_file

    if not quiet:
        print(cmd)
    call(cmd, shell=True)
    os.remove(listfile)


class BandGranule(object):

    def __init__(self, filename):

        basename = os.path.basename(filename)
        tags = basename.replace('.jp2', '').split('_')
        self.file = filename
        self.id = tags[-1]
        self.sensor_id = tags[0]
        self.product_type = tags[3]
        self.acquisition_date = tags[7]
        self.utm_zone = tags[-2][1:3]
        self.granule = tags[-2]
        self.pixel_size = s2pixel[self.id]


class Image(object):

    def __init__(self, safedir):

        self.msi_list = [BandGranule(os.path.join(dirpath, f))
                         for dirpath, dirnames, files in os.walk(safedir)
                         for f in fnmatch.filter(files, '*MSI*.jp2')]

        self.pvi_list = [os.path.join(dirpath, f)
                         for dirpath, dirnames, files in os.walk(safedir)
                         for f in fnmatch.filter(files, '*PVI*.jp2')]

        utm_zones = [band.utm_zone for band in self.msi_list]
        utm_zones = set(utm_zones)

        data = {}
        for zone in utm_zones:
            data[zone] = {key:  {'file': '', 'granules': []} for key in s2pixel.keys()}

        for band in self.msi_list:
            data[band.utm_zone][band.id]['granules'].append(band.file)

        self.safedir = safedir
        self.data = data
        self.mosaic = {key: '' for key in s2pixel.keys()}
        self.warp_files = []
        self.view_files = []

        # self.importdir = os.path.join(importdir, os.path.basename(self.safedir).replace('.SAFE', ''))
        #
        # if not os.path.exists(importdir):
        #     os.mkdir(importdir)

        if not os.path.exists(self.safedir):
            os.mkdir(self.safedir)

        tags = os.path.basename(self.safedir).replace('.SAFE', '').replace('.jp2', '').split('_')
        self.sensor_product = tags[3]
        self.date = tags[-1]

        # for band in s2pixel.keys():
        #     self.mosaic[band] = os.path.join(self.importdir, '%s_%s_mosxx_%s.img' % (self.sensor_product, self.date,
        #                                                                              band))
        print('Init %s' % os.path.basename(self.safedir))

    def create_vrts(self, epsg=None):

        for band in s2pixel.keys():
            warp_files = []
            for i, utm_zone in enumerate(self.data.keys()):
                vrt_file = os.path.join(self.safedir, '%s_%s_utm%s_%s.vrt' % (self.sensor_product, self.date,
                                                                              utm_zone, band))
                self.data[utm_zone][band]['file'] = vrt_file
                gdalbuildvrt(self.data[utm_zone][band]['granules'], vrt_file, stack=False)

                if epsg is not None:
                    warp_file = os.path.join(self.safedir,
                                             '%s_%s_e%s_%s.tmp%s.vrt' %
                                             (self.sensor_product, self.date, epsg, band, i+1))
                    warp_files.append(warp_file)
                    cmd = 'gdalwarp -q -of VRT -t_srs EPSG:%s -tr %s %s -overwrite -multi -r near %s %s' % \
                          (epsg, s2pixel[band], s2pixel[band], vrt_file, warp_file)
                    call(cmd, shell=True)

            if epsg is not None:
                mosaic_file = warp_files[0].replace('tmp1.', '')
                gdalbuildvrt(warp_files, mosaic_file, srcnodata=0, stack=False)
                # for warp_file in warp_files:
                #    os.remove(warp_file)

        for view in ['r10', 'r20', 'r60', 'ldcm10', 'land10']:
            warp_files = []
            for i, utm_zone in enumerate(self.data.keys()):
                in_files = [self.data[utm_zone][x]['file'] for x in s2bandcombi[s2view[view]['bandcombi']]]
                vrt_file = os.path.join(self.safedir,
                                        '%s_%s_utm%s_%s.vrt' %
                                        (self.sensor_product, self.date, utm_zone, view))
                gdalbuildvrt(in_files, vrt_file, tr=s2view[view]['resolution'], quiet=True, stack=True)

                if epsg is not None:
                    warp_file = os.path.join(self.safedir,
                                             '%s_%s_e%s_%s.tmp%s.vrt' %
                                             (self.sensor_product, self.date, epsg, view, i+1))
                    warp_files.append(warp_file)
                    cmd = 'gdalwarp -q -of VRT -t_srs EPSG:%s -tr %s %s -overwrite -multi -r near %s %s' % \
                          (epsg, s2view[view]['resolution'], s2view[view]['resolution'], vrt_file, warp_file)
                    call(cmd, shell=True)

            if epsg is not None:
                mosaic_file = warp_files[0].replace('tmp1.', '')
                self.warp_files.append(mosaic_file)
                gdalbuildvrt(warp_files, mosaic_file, srcnodata=0, stack=False)
                #
                # for warp_file in warp_files:
                #    os.remove(warp_file)

        print('Done')

    def export(self, outdir, view=None):

        if not os.path.exists(outdir):
            os.mkdir(outdir)

        for infile in fnmatch.filter(self.warp_files, '*'+view+'*'):

            outpath = os.path.join(outdir, os.path.basename(self.safedir))
            if not os.path.exists(outpath):
                os.mkdir(outpath)

            outfile = os.path.join(outpath, os.path.basename(infile).replace('vrt', 'img'))
            call('gdal_translate -q -of envi %s %s' % (infile, outfile), shell=True)

    def create_bands(self, epsg=None, skip_mosaic=False):

        if not os.path.exists(self.importdir):
            os.mkdir(self.importdir)

        for band in s2pixel.keys():
            for utm_zone in self.data.keys():
                vrt_file = os.path.join(self.importdir, '%s_%s_utm%s_%s.vrt' % (self.sensor_product, self.date,
                                                                                utm_zone, band))
                bsq_file = vrt_file.replace('vrt', 'img')
                self.data[utm_zone][band]['file'] = bsq_file
                if os.path.exists(bsq_file) is False and os.path.exists(self.mosaic[band]) is False:
                    gdalbuildvrt(self.data[utm_zone][band]['granules'], vrt_file, stack=False)
                    if epsg is None:
                        call('gdal_translate -q -of envi %s %s' % (vrt_file, bsq_file), shell=True)
                        os.remove(vrt_file)
                    else:
                        cmd = 'gdalwarp -of envi -t_srs EPSG:%s -tr %s %s -overwrite -multi -r near %s %s' % \
                               (epsg, s2pixel[band], s2pixel[band], vrt_file, bsq_file)
                        call(cmd, shell=True)
                        os.remove(vrt_file)

            if epsg is not None and skip_mosaic is False:
                if os.path.exists(self.mosaic[band]) is False:
                    infiles = [self.data[utm_zone][band]['file'] for utm_zone in self.data.keys()]
                    vrt_file = self.mosaic[band]+'.vrt'
                    gdalbuildvrt(infiles, vrt_file, srcnodata=0, stack=False)

                    call('gdal_translate -q -of envi %s %s' % (vrt_file, self.mosaic[band]), shell=True)
                    os.remove(vrt_file)
                    for f in infiles:
                        os.remove(f.replace('img', 'hdr'))
                        os.remove(f.replace('img', 'img.aux.xml'))
                        os.remove(f)

    def create_view(self, view, quiet=True):

        if not os.path.exists(self.safedir):
            os.mkdir(self.safedir)

        for i, utm_zone in enumerate(self.data.keys()):
            in_files = [self.data[utm_zone][x]['file'] for x in s2bandcombi[s2view[view]['bandcombi']]]
            vrt_file = os.path.join(self.safedir,
                                    '%s_%s_utm%s_%s.vrt' %
                                    (self.sensor_product, self.date, utm_zone, view))
            gdalbuildvrt(in_files, vrt_file, tr=s2view[view]['resolution'], quiet=True, stack=True)
