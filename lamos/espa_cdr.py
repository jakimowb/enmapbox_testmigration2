#! /usr/bin/env python
from __future__ import print_function
import sys
import os
import tarfile
import argparse
import datetime
import subprocess
import logging
import fnmatch
import yaml
import shutil
import zipfile
import ogr
import osr
import gdal
from collections import OrderedDict
from lamos import metacube

espa_version = 2016.0301
SKIP = -1
ERROR = 1
SUCCESS = 0
image_count = 0
my_host = '141.20.140.41'
my_database = 'metacube'
my_password = "landsat"
my_user = 'geomatic'

# check environmental variables
envars = ['LEDAPS_AUX_DIR', 'L8_AUX_DIR', 'ESUN', 'ESPA_LAND_MASS_POLYGON']
for envar in envars:
    if os.getenv(envar) is None:
        print("%s environmental variable not set" % envar)
    else:
        espa_aux_dir = os.path.dirname(os.getenv('LEDAPS_AUX_DIR'))

if os.getenv('ESPA_LAND_MASS_POLYGON'):
    if os.path.isfile(os.getenv('ESPA_LAND_MASS_POLYGON')) is False:
        print("%s is missing" % os.getenv('ESPA_LAND_MASS_POLYGON'))


def cdr_batch_create(inpath, outpath, filter='L[ECMT]*.tar.[gb]z', overwrite=False, process_sr=True, write_toa=True,
                     multithread=False, prob=22.5, cldpix=3, sdpix=3, compress=True, debug=False,
                     remove_tgz=False, warp_esa=True, offline=False, warp_year=None, warp_doy=None):

    # run batch mode
    tgz_list = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(inpath)
                for f in fnmatch.filter(files, filter)]

    for tgz_file in tgz_list:
        print('Processing %s' % tgz_file)

        fname = os.path.basename(tgz_file)
        sceneid = get_sceneid_from_filename(fname)
        path_scene = os.path.join(outpath, sceneid[3:6], sceneid[6:9], sceneid)
        log_filename = os.path.join(path_scene, sceneid + '.log')

        if not os.path.isfile(log_filename):
            this_image = Processor(tgz_file, outpath, offline=offline)

            this_image.make_all(overwrite=overwrite, process_sr=process_sr, write_toa=write_toa,
                                multithread=multithread, prob=prob, cldpix=cldpix, sdpix=sdpix,
                                warp_year=warp_year, warp_doy=warp_doy, compress=compress, debug=debug, warp_esa=warp_esa)

            if this_image.status == SUCCESS and remove_tgz is True:
                os.remove(tgz_file)


def cdr_create(file_archive, outpath):

    fname = os.path.basename(file_archive)
    sceneid = get_sceneid_from_filename(fname)
    path_scene = os.path.join(outpath, sceneid[3:6], sceneid[6:9], sceneid)
    log_filename = os.path.join(path_scene, sceneid+'.log')

    if os.path.isfile(log_filename):
        return SKIP, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sceneid, 'already processed. Skipped.'

    skip_file = os.path.join(outpath, 'skip.txt')
    if os.path.isfile(skip_file):
        skip_scenes = read_list(skip_file)
        if sceneid in skip_scenes:
            return SKIP, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sceneid, 'already processed. Skipped.'

    this_image = Processor(file_archive, outpath, batch_logger=sys_logger, offline=args.offline)
    if this_image.status == SKIP:
        return this_image.status, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), this_image.sceneid, 'Skipping %s' % file_archive

    try:
        this_image.make_all(overwrite=args.overwrite, process_sr=args.process_sr, write_toa=args.write_toa,
                            multithread=args.multithread, prob=args.prob, cldpix=args.cldpix, sdpix=args.sdpix,
                            compress=args.compress, debug=args.debug, warp_esa=args.warp_esa, polynom=args.polynom,
                            warp_band=args.warp_band, warp_resampling=args.warp_resampling, warp_year=args.warp_year,
                            warp_doy=args.warp_doy, warp_parameter_file=args.warp_parameter_file)
        return this_image.status, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), this_image.sceneid, this_image.info
    except IOError as e:
        return ERROR, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sceneid, 'I/O error in: %s' % file_archive


def cdr_move(sceneid_list, input_path, output_path, debug=False, overwrite=False):
    for sceneid in sceneid_list:
        cdr_in = os.path.join(input_path, sceneid[3:6], sceneid[6:9], sceneid)
        cdr_out = os.path.join(output_path, sceneid[3:6], sceneid[6:9], sceneid)
        print('Moving ' + cdr_in + ' to ' + cdr_out)
        for root, dirs, files in os.walk(cdr_in):
            for fname in files:
                relative_file = os.path.relpath(os.path.join(root, fname), cdr_in)
                in_file = os.path.join(cdr_in, relative_file)
                out_file = os.path.join(cdr_out, relative_file)
                if os.path.isfile(out_file) and not overwrite:
                    print('%s file exists. Use overwrite keyword.' % out_file)
                else:
                    if not debug:
                        if not os.path.isdir(os.path.dirname(out_file)):
                            os.makedirs(os.path.dirname(out_file))
                        os.rename(in_file, out_file)
        if not debug:
            rmdir(cdr_in)


def cdr_copy(sceneid_list, input_path, output_path, debug=False, overwrite=False):
    for sceneid in sceneid_list:
        cdr_in = os.path.join(input_path, sceneid[3:6], sceneid[6:9], sceneid)
        cdr_out = os.path.join(output_path, sceneid[3:6], sceneid[6:9], sceneid)
        print('Copying ' + cdr_in + ' to ' + cdr_out)
        for root, dirs, files in os.walk(cdr_in):
            for fname in files:
                relative_file = os.path.relpath(os.path.join(root, fname), cdr_in)
                in_file = os.path.join(cdr_in, relative_file)
                out_file = os.path.join(cdr_out, relative_file)
                if os.path.isfile(out_file) and not overwrite:
                    print('%s file exists. Use overwrite keyword.' % out_file)
                else:
                    if not debug:
                        if not os.path.isdir(os.path.dirname(out_file)):
                            os.makedirs(os.path.dirname(out_file))
                        shutil.copyfile(in_file, out_file)


def cloud_proximity(cloud_file, overwrite=False, compress=True):

    proximity_file = cloud_file.replace('_cfmask.img', '_cproximity.img')
    if os.path.isfile(proximity_file) and not overwrite:
        print('Proximity file already exists. Skipping..')
        return

    if not os.path.isfile(cloud_file):
        print("Error: cloud file does not exist or is not accessible: %s" % cloud_file)
        return

    # open source file
    src_ds = gdal.Open(cloud_file)

    if src_ds is None:
        print('Unable to open %s' % cloud_file)
        return ERROR

    srcband = src_ds.GetRasterBand(1)

    # Try opening the destination file as an existing file.
    try:
        driver = gdal.IdentifyDriver(proximity_file)
        if driver is not None:
            dst_ds = gdal.Open(proximity_file, gdal.GA_Update)
            dstband = dst_ds.GetRasterBand(1)
        else:
            dst_ds = None
    except:
        dst_ds = None

    #     Create output file.
    if dst_ds is None:
        drv = gdal.GetDriverByName('envi')
        dst_ds = drv.Create( proximity_file,
                             src_ds.RasterXSize, src_ds.RasterYSize, 1,
                             gdal.GetDataTypeByName('int16'), [])

        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
        dst_ds.SetProjection(src_ds.GetProjectionRef())

        dstband = dst_ds.GetRasterBand(1)

    gdal.ComputeProximity(srcband, dstband, ['VALUES=2,4', 'NODATA=30000', 'distunits=GEO', 'maxdist=30000'], callback=None)

    srcband = None
    dstband = None
    src_ds = None
    dst_ds = None

    if compress:
        compress_envi_file(proximity_file)


def compress_envi_file(img_file):

    hdr = read_hdr(img_file)
    if hdr.get('file compression', '0') == '0':

        subprocess.call(['gzip', '-q', img_file])
        #with open(img_file, 'rb') as f_in:
        #    with gzip.open(img_file+'.gz', 'wb') as f_out:
        #        f_out.writelines(f_in)
        #os.remove(img_file)

        os.rename(img_file+'.gz', img_file)

        hdr.update({'file compression': '1'})
        write_hdr(img_file, hdr)


def counter(res):

    global image_count

    image_count -= 1

    try:
        ok, time, sceneid, message = res
    except:
        print(res)
        return

    if ok != SKIP:
        if ok == SUCCESS:
            sys_logger.info('%s - %s %s images left..' % (sceneid, message, image_count))
        else:
            sys_logger.error('%s - %s %s images left..' % (sceneid, message, image_count))


def error_callback(execption):
    print('Error callback:', file=sys.stderr)
    print(execption, file=sys.stderr)


def file_search(path, pattern='*', directory=False, full_names=True):

    if directory:
        rlist = [dirpath for dirpath, dirnames, files in os.walk(path)
                 if fnmatch.fnmatch(os.path.basename(dirpath), pattern)]
    else:
        rlist = [os.path.join(dirpath, f)
                 for dirpath, dirnames, files in os.walk(path)
                 for f in fnmatch.filter(files, pattern)]

    if not full_names:
        rlist = [os.path.basename(x) for x in rlist]

    return rlist


def get_sceneid_from_filename(file_basename):

    if file_basename.lower().endswith('zip'):

        if file_basename[10:13] == 'TM_':
            sensor = 'T'
        elif file_basename[10:13] == 'ETM':
            sensor = 'E'
        elif file_basename[10:13] == 'MSS':
            sensor = 'M'
        elif file_basename[10:13] == 'OLI':
            sensor = 'C'

        ayear = int(file_basename[21:25])
        amonth = int(file_basename[25:27])
        aday = int(file_basename[27:29])
        adoy = (datetime.datetime(ayear, amonth, aday) - datetime.datetime(ayear, 1, 1)).days + 1
        wpath = file_basename[61:64]
        wrow = file_basename[66:69]
        scene_id = file_basename[0] + sensor + file_basename[3] + wpath + wrow + str(ayear) + '{0:03d}'.format(adoy) + 'ESA00'

    else:
        scene_id = file_basename[0:-7]

    return scene_id


def image_coordinates(hdr):

    gt = hdr.get('map info').split(', ')[3:7]
    ft = [float(x) for x in gt]

    offset_x = ft[2] / 2.0
    offset_y = ft[3] / 2.0

    lx = ft[0] + offset_x
    uy = ft[1] - offset_y
    rx = ft[0] + float(hdr.get('samples')) * ft[2] - offset_x
    ly = ft[1] - float(hdr.get('lines')) * ft[3] + offset_y

    return (lx, uy), (rx, ly)


def read_hdr(img_file):

    hdr_files = [img_file[:-3]+'.hdr', img_file[:-4]+'.hdr', img_file+'.hdr']
    hdr_files = [hdr_file for hdr_file in hdr_files if os.path.isfile(hdr_file)]
    if len(hdr_files) != 1:
        print('Unable to find unique HDR for '+img_file)
        return None
    else:
        hdr_file = hdr_files[0]

    hdr = OrderedDict()
    cont = False
    with open(hdr_file, 'r') as f:
        for line in f:
            if cont:
                hdr[attr_name] += line.strip()
                if hdr[attr_name].endswith('}'):
                    cont = False
            else:
                items = line.split('=', 1)
                if len(items) > 1:
                    attr_name = items[0].strip()
                    attr_value = items[1].strip()
                    hdr[attr_name] = attr_value
                    if hdr[attr_name].startswith('{'):
                        cont = True
                    if hdr[attr_name].endswith('}'):
                        cont = False
    return hdr


def read_list(text_file):
    with open(text_file) as f:
        content = f.readlines()
        content = [line.rstrip('\n') for line in content]
    return content


def read_mtl(mtl_file):
    mtldata = {}
    with open(mtl_file, 'r') as f:
        for line in f:
            items = line.strip()
            items = [item.strip() for item in items.replace('"', '').split('=')]

            # stop reading if not two elements are returned
            # likely end of file
            if len(items) != 2:
                break

            tag = items[0].upper()
            value = items[1]
            if value == 'L1_METADATA_FILE':
                continue
            if tag in ['END;', 'END']:
                break

            # empty group_data dictionary if group field,
            # append it to master dictionary
            # or fill it otherwise

            if tag in ['BEGIN_GROUP', 'GROUP']:
                group_name = value
                group_data = {}
            elif tag == 'END_GROUP':
                mtldata[group_name] = group_data
            else:
                group_data[tag] = yaml.load(value)

    da = mtldata.get('PRODUCT_METADATA').get('DATE_ACQUIRED')
    if da is None:
        da = mtldata.get('PRODUCT_METADATA').get('ACQUISITION_DATE')
    mtldata['PRODUCT_METADATA']['DATE_ACQUIRED'] = datetime.datetime(da.year, da.month, da.day)
    return mtldata


def read_ortho_ini(ini_file):
    ini_data = {}
    with open(ini_file, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                items = line.strip()
                items = [item.strip() for item in items.replace('"', '').split('=')]

                if len(items) == 2:
                    tag = items[0].upper()
                    value = items[1]
                    ini_data[tag] = yaml.load(value)

    return ini_data


def rmdir(path):
        if os.path.exists(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)


def tgz_delete(tgz_dir, dry_run=True):

    tgz_list = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(tgz_dir)
                for f in fnmatch.filter(files, '*.tar.gz')]

    for tgz_file in tgz_list:
        mtl_file = tgz_file.replace('.tar.gz', '.mtl.txt')
        if os.path.isfile(mtl_file):
            pass
        else:
            print('Removing %s' % tgz_file)
            if not dry_run:
                os.remove(tgz_file)


def tgz_convert_esa_batch(inpath, outpath, filter='LS*.ZIP'):

    zip_list = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(inpath)
                for f in fnmatch.filter(files, filter)]

    for zip_file in zip_list:
        print('Importing %s' % os.path.basename(zip_file))
        tgz_convert_esa(zip_file, outpath)


def tgz_convert_esa(zip_file, outpath, overwrite=False):

    zip = zipfile.ZipFile(zip_file)
    esasceneid = os.path.basename(zip_file)[:-4]
    temppath = os.path.join(outpath, esasceneid)

    sid = get_sceneid_from_filename(esasceneid)

    scene_outpath = os.path.join(outpath, sid[3:6], sid[6:9])
    if not os.path.exists(scene_outpath):
        os.makedirs(scene_outpath)

    tgz_file = os.path.join(scene_outpath, sid+'.tar.gz')

    if os.path.isfile(tgz_file) and not overwrite:
        print('%s exists. Use overwrite keyword.' % tgz_file)
        return

    if not os.path.exists(temppath):
        os.makedirs(temppath)

    zip.extractall(temppath)

    file_list = [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk(temppath) for f in files]
    mtl_file = fnmatch.filter(file_list, '*MTL.txt')[0]
    sceneid = os.path.basename(mtl_file).replace('_MTL.txt', '')

    if sceneid != sid:
        print('SceneID mismatch in %s. Change to %s.' % (sid, sceneid))
        scene_outpath = os.path.join(outpath, sceneid[3:6], sceneid[6:9])

    if not os.path.exists(scene_outpath):
        os.makedirs(scene_outpath)

    if not os.path.isfile(tgz_file):

        # copy mtl file
        shutil.copyfile(mtl_file, os.path.join(scene_outpath, sceneid+'.mtl.txt'))

        with tarfile.open(tgz_file, "w:gz") as tar:
            for name in file_list:
                tgzname = os.path.basename(name)
                tgzname = tgzname[:-3] + tgzname[-3:].lower()
                if tgzname.startswith(esasceneid):
                    tgzname = tgzname.replace(esasceneid, sceneid)
                tar.add(name, arcname=tgzname)

    rmdir(temppath)


def tgz_delete_l1g(inpath, filter='L[ECMT]*.tar.[gb]z'):

    # run batch mode
    tgz_list = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(inpath)
                for f in fnmatch.filter(files, filter)]

    for tgz_file in tgz_list:

        # check if LPGS image
        tar_wofile = os.path.join(os.path.dirname(tgz_file), os.path.basename(tgz_file).replace('.tar.gz', '._wo.txt'))
        if os.path.isfile(tar_wofile):
            os.remove(tar_wofile)
            os.remove(tgz_file)

        # check metadata (if already extracted) for data type
        tar_mtlfile = os.path.join(os.path.dirname(tgz_file), os.path.basename(tgz_file).replace('.tar.gz', '.mtl.txt'))
        if os.path.isfile(tar_mtlfile):
            mtl = read_mtl(tar_mtlfile)
            if len(mtl) > 0:
                if mtl.get('PRODUCT_METADATA').get('DATA_TYPE') != 'L1T' and \
                   mtl.get('PRODUCT_METADATA').get('PRODUCT_TYPE') != 'L1T':
                    print('Deleted %s.' % tgz_file)
                    os.remove(tar_mtlfile)
                    os.remove(tgz_file)


def tgz_find(inpath, scene_ids):

    sceneids = tuplefy(scene_ids)

    scene_stations = [x[16:19].lower() for x in sceneids]
    archive_files = ['' for x in sceneids]

    if 'esa' in set(scene_stations):
        zip_list = [os.path.join(dirpath, f)
                    for dirpath, dirnames, files in os.walk(inpath)
                    for f in fnmatch.filter(files, 'L*.ZIP')]

        for zip_file in zip_list:
            file_sid = get_sceneid_from_filename(os.path.basename(zip_file))
            if file_sid in sceneids:
                archive_files[sceneids.index(file_sid)] = zip_file

    if '' in archive_files:
        tgz_list = [os.path.join(dirpath, f)
            for dirpath, dirnames, files in os.walk(inpath)
            for f in fnmatch.filter(files, 'L*.tar.gz')]

        for tgz_file in tgz_list:
            file_sid = get_sceneid_from_filename(os.path.basename(tgz_file))
            if file_sid in sceneids:
                archive_files[sceneids.index(file_sid)] = tgz_file

    return archive_files


def tgz_move_l1g(inpath, outpath, filter='L[ECMT]*.tar.[gb]z'):

    tgz_list = [os.path.join(dirpath, f)
                for dirpath, dirnames, files in os.walk(inpath)
                for f in fnmatch.filter(files, filter)]

    if os.path.exists(outpath) is False:
        os.makedirs(outpath)

    i = 0

    for tgz_file in tgz_list:

        print('Processing %s' % tgz_file)
        fname = os.path.basename(tgz_file)
        sceneid = fname[0:-7]

        # check if LPGS image
        tar__wofile = os.path.join(os.path.dirname(tgz_file), sceneid + '._wo.txt')
        if os.path.isfile(tar__wofile):
            print('%s - Not an LPGS image.' % sceneid)
            os.rename(tar__wofile, os.path.join(outpath, os.path.basename(tar__wofile)))
            os.rename(tgz_file, os.path.join(outpath, os.path.basename(tgz_file)))
            i += 1

        # check metadata (if already extracted) for data type
        tar_mtlfile = os.path.join(os.path.dirname(tgz_file), sceneid + '.mtl.txt')
        if os.path.isfile(tar_mtlfile):
            mtl = read_mtl(tar_mtlfile)
            if len(mtl) > 0:
                if mtl.get('PRODUCT_METADATA').get('DATA_TYPE') != 'L1T' and \
                   mtl.get('PRODUCT_METADATA').get('PRODUCT_TYPE') != 'L1T':
                    print('%s - DATA_TYPE not L1T' % sceneid)
                    os.rename(tar_mtlfile, os.path.join(outpath, os.path.basename(tar_mtlfile)))
                    os.rename(tgz_file, os.path.join(outpath, os.path.basename(tgz_file)))
                    i += 1

    print('Moved %s files' % i)


def tgz_organize(import_path, output_path, debug=False, suffix='tar.gz'):

    for root, dirs, files in os.walk(import_path):
        for fname in files:
            if fname.endswith(suffix):
                in_file = os.path.join(root, fname)

                if suffix == 'ZIP':
                    wpath = fname[61:64]
                    wrow = fname[66:69]
                else:
                    wpath = fname[3:6]
                    wrow = fname[6:9]

                outpath = os.path.join(output_path, wpath, wrow)
                out_file = os.path.join(outpath, fname)
                print('Moving ' + in_file + ' to ' + out_file)
                if not debug:
                    if not os.path.isdir(outpath):
                        os.makedirs(outpath)
                    if not os.path.isfile(out_file):
                        os.rename(in_file, out_file)
                    else:
                        print('%s file exists.' % out_file)


def tgz_move_unprocessed(import_path, output_path, processed_scenes=None, debug=False, ending='.tar.gz'):
    for root, dirs, files in os.walk(import_path):
        for fname in files:
            if fname.endswith(ending):
                in_file = os.path.join(root, fname)
                outpath = os.path.join(output_path, fname[3:6], fname[6:9])
                sceneid = fname[0:21]
                out_file = os.path.join(outpath, fname)
                if processed_scenes.isin({sceneid}).any() == False:
                    print('Moving ' + in_file + ' to ' + out_file)
                    if not debug:
                        if not os.path.isdir(outpath):
                            os.makedirs(outpath)
                        if not os.path.isfile(out_file):
                            os.rename(in_file, out_file)
                        else:
                            print('%s file exists.' % out_file)


def tgz_unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (get_sceneid_from_filename(os.path.basename(x)) in
                                   seen or seen_add(get_sceneid_from_filename(os.path.basename(x))))]


def transform_utm2geo(coordinate, utm_zone=None, hemisphere='north'):

    img_srs = osr.SpatialReference()

    if hemisphere.lower().startswith('n'):
        h = 600
    else:
        h = 700

    img_srs.ImportFromEPSG(32000 + h + utm_zone)

    geo_srs = osr.SpatialReference()
    geo_srs.ImportFromEPSG(4326)
    coordTransform = osr.CoordinateTransformation(img_srs, geo_srs)

    # create a geometry from coordinates
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(coordinate[0], coordinate[1])

    # transform point
    point.Transform(coordTransform)

    # print point in EPSG 4326
    return point.GetPoint_2D()


def tuplefy(data):

    if type(data) is int or type(data) is str:
        return tuple([data, ])
    elif type(data) is tuple:
        return data
    else:
        return tuple(data)


def update_mtl(mtl_file, attributes):

    # update xml file
    with open(mtl_file, 'r') as f_in:
        mtl_content = [line for line in f_in.readlines()]

    if 'GEOMETRIC_RMSE_VERIFY' not in ''.join(mtl_content):
        ind = [mtl_content.index(x) for x in mtl_content if x.lstrip().startswith('GEOMETRIC_RMSE_MODEL ')]
        mtl_content.insert(ind[0] - 1, '    GEOMETRIC_RMSE_VERIFY = -1\n')

    with open(mtl_file, 'w') as f_out:
        for line in mtl_content:
            splits = line.split('=')
            for attribute in attributes.keys():
                if attribute in splits[0].lower():
                    splits[1] = ' %s' % attributes.get(attribute)
            line = '='.join(splits).replace('\n', '')
            f_out.writelines(line + '\n')


def write_hdr(img_file, hdr):

    hdr_files = [img_file[:-3]+'.hdr', img_file[:-4]+'.hdr', img_file+'.hdr']
    hdr_files = [hdr_file for hdr_file in hdr_files if os.path.isfile(hdr_file)]
    if len(hdr_files) != 1:
        print('Unable to find unique HDR for '+img_file)
        return None
    else:
        hdr_file = hdr_files[0]

    with open(hdr_file, 'w') as f_out:
        f_out.writelines('ENVI\n')
        for key in iter(hdr.keys()):
            f_out.writelines(" = ".join([key, hdr[key]])+"\n")


def write_ortho_parameter_file(param_file, chip_size=15, cp_seed_win=30, max_shift=5, max_num_high_corr=3,
                               max_num_iter=1, acceptable_corr=0.6, min_acceptable_ncp=10,
                               max_ave_error=0.5, max_acceptable_rmse=0.75,
                               preliminary_registration=0, coarse_scale=10, coarse_max_shift=150,
                               coarse_cp_seed_win=5):

    with open(param_file, 'w') as f_out:
        f_out.writelines('PARAMETER_FILE\n')
        f_out.writelines('\n')
        f_out.writelines('# 1 = use preliminary registration based on coarse resolution images\n')
        f_out.writelines('# 0 = not use preliminary registration\n')
        f_out.writelines('PRELIMINARY_REGISTRATION = %s\n' % preliminary_registration)
        f_out.writelines('\n')
        f_out.writelines('# aggregation scale of coarse resolution image to be used for preliminary registration\n')
        f_out.writelines('COARSE_SCALE = %s\n' % coarse_scale)
        f_out.writelines('\n')
        f_out.writelines('# maximum shift that can be detected from coarse resolution image\n')
        f_out.writelines('# this equals to COARSE_SCALE*COARSE_MAX_SHIFT in fine resolution image\n')
        f_out.writelines('COARSE_MAX_SHIFT = %s\n' % coarse_max_shift)
        f_out.writelines('\n')
        f_out.writelines('# interval distance (in pixels) for placing initial tie points '
                         'for preliminary registration\n')
        f_out.writelines('COARSE_CP_SEED_WIN = %s\n' % coarse_cp_seed_win)
        f_out.writelines('\n')
        f_out.writelines('# control chip size (in pixels) for matching test  \n')
        f_out.writelines('CHIP_SIZE  = %s\n' % chip_size)
        f_out.writelines('\n')
        f_out.writelines('# interval distance (in fine pixels) for placing initial tie points for '
                         'precise registration\n')
        f_out.writelines('# smaller distance contains more tie point seeds \n')
        f_out.writelines('CP_SEED_WIN = %s\n' % cp_seed_win)
        f_out.writelines('\n')
        f_out.writelines('# maximum possible shift (in fine pixels) between base and warp images \n')
        f_out.writelines('# void if "PRELIMINARY_REGISTRATION = 1" (program will reset it automatically)\n')
        f_out.writelines('MAX_SHIFT = %s \n' % max_shift)
        f_out.writelines('\n')
        f_out.writelines('# allowed number of high correlation matching in searching range\n')
        f_out.writelines('MAX_NUM_HIGH_CORR = %s\n' % max_num_high_corr)
        f_out.writelines('\n')
        f_out.writelines('# minimum acceptable correlation coefficient for a matching tie point\n')
        f_out.writelines('ACCEPTABLE_CORR = %s\n' % acceptable_corr)
        f_out.writelines(' \n')
        f_out.writelines('# minimum required number of control point for registration attempt \n')
        f_out.writelines('MIN_ACCEPTABLE_NCP = %s\n' % min_acceptable_ncp)
        f_out.writelines('\n')
        f_out.writelines('# maximum allowed average error (in pixel) for precise registration\n')
        f_out.writelines('MAX_AVE_ERROR = %s \n' % max_ave_error)
        f_out.writelines('\n')
        f_out.writelines('# maximum number of iterations if tie point testing fails\n')
        f_out.writelines('MAX_NUM_ITER = %s\n' % max_num_iter)
        f_out.writelines('\n')
        f_out.writelines('# maximum acceptable RMSE for tie points\n')
        f_out.writelines('MAX_ACCEPTABLE_RMSE = %s\n' % max_acceptable_rmse)
        f_out.writelines('\n')
        f_out.writelines('END\n')


class Processor(object):

    def __init__(self, file_archive, outpath, bindir=None, batch_logger=None, offline=False):

        self.mtl = {}
        self.status = SUCCESS
        self.info = ''
        self.path_root = outpath
        self.file_archive = file_archive
        if offline is False:
            self.metacube = metacube.Connection(host=my_host, database=my_database, password=my_password, user=my_user)
        else:
            self.metacube = None

        # create console logger if no (file) batch logger is passed when initializing object
        if batch_logger is not None:
            self.batch_logger = batch_logger
        else:
            self.batch_logger = logging.getLogger('MAIN')
            self.batch_logger.setLevel(logging.INFO)
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)
            fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')
            ch.setFormatter(formatter)
            # add the handlers to the logger
            self.batch_logger.addHandler(ch)

        # set up path names
        if not os.path.isfile(file_archive):
            self.status = ERROR
            self.info = 'Unable to access: %s' % file_archive
            self.batch_logger.error(self.info)
            self.sceneid = None
            return

        self.sceneid = get_sceneid_from_filename(os.path.basename(file_archive))
        self.station = self.sceneid[16:19]
        self.doy = int(self.sceneid[13:16])

        if self.station == 'ESA':
            if os.path.exists(os.path.dirname(self.path_scene_tmp())):
                dirlist = os.listdir(os.path.dirname(self.path_scene_tmp()))
                match = [f for f in fnmatch.filter(dirlist, self.sceneid[:16]+'*')
                         if os.path.isdir(os.path.join(os.path.dirname(self.path_scene_tmp()), f))]
                if len(match) == 1:
                    self.status = SKIP

        # take care of CDR archive files
        if '-SC' in self.file_archive:
            if os.path.exists(os.path.dirname(self.path_scene_tmp())):
                dirlist = os.listdir(os.path.dirname(self.path_scene_tmp()))
                match = [f for f in fnmatch.filter(dirlist, self.sceneid[:16]+'*')
                         if os.path.isdir(os.path.join(os.path.dirname(self.path_scene_tmp()), f))]
                if len(match) == 1:
                    self.sceneid = match[0]

        self.file_xml = self.sceneid + '.xml'
        self.file_mtl = self.sceneid + '_MTL.txt'
        self.file_log = self.sceneid + '.log'
        self.date_acquired = datetime.datetime(int(self.sceneid[9:13]), 1, 1) + datetime.timedelta(
            days=int(self.sceneid[13:16])-1)

        # create logger
        self.logger = logging.getLogger(self.sceneid)
        self.logger.setLevel(logging.INFO)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        # create formatter and add it to the handlers
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(ch)

        if os.path.isfile(self.path_scene_tmp(filename=self.file_mtl)):
            self.mtl = read_mtl(self.path_scene_tmp(filename=self.file_mtl))

        if os.path.exists(self.path_scene_tmp()):
            self._init_file_logger(filename=self.path_scene_tmp(filename=self.file_log))

        # setup bindir
        if bindir is None:
            self._bindir = ''
        else:
            self._bindir = bindir

    def __del__(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
        if self.metacube is not None:
            self.metacube.conn.close()

    def __repr__(self):
        for key, value in vars(self).items():
            print(key, ':', value)
        return 'Processor Object'

    def path_scene(self, filename=''):
        if len(filename) == 0:
            rst = os.path.join(self.path_root, self.sceneid[3:6], self.sceneid[6:9], self.sceneid)
        else:
            rst = os.path.join(self.path_root, self.sceneid[3:6], self.sceneid[6:9], self.sceneid, filename)
        return rst

    def path_scene_tmp(self, filename='', prefix='_tmp_'):
        if len(filename) == 0:
            rst = os.path.join(self.path_root, self.sceneid[3:6], self.sceneid[6:9], prefix + self.sceneid)
        else:
            rst = os.path.join(self.path_root, self.sceneid[3:6], self.sceneid[6:9], prefix + self.sceneid, filename)
        return rst

    def _init_file_logger(self, filename=None):
        fh = logging.FileHandler(filename)
        fh.setLevel(logging.INFO)
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def callcmd(self, cmdstr=None, mydir=None):

        self.logger.info('Running: %s' % " ".join(cmdstr))
        try:
            with open(self.path_scene_tmp(filename=self.file_log), "a") as logfile:
                subprocess.check_call(cmdstr, stdout=logfile)
        except subprocess.CalledProcessError as e:
            self.logger.error('Error in ' + cmdstr[0])
            self.logger.error(e.output)
            if mydir:
                os.chdir(mydir)
            self.status = ERROR
            return ERROR

    def compress(self):
        for f in os.listdir(self.path_scene_tmp()):
            if f.endswith('.img'):
                compress_envi_file(self.path_scene_tmp(filename=f))

    def cleanup(self):

        # delete L7 slc-off
        path_gapmask = self.path_scene_tmp(filename='gap_mask')
        if os.path.exists(path_gapmask):
            for root, dirs, files in os.walk(path_gapmask, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path_gapmask)

        if self.sceneid[0:3] == 'LC8':
            delete_these_files = [self.sceneid+'_toa_band'+s for s in ['1.', '2', '3', '4', '5', '6', '7', '8', '9']]
            delete_these_files += [self.sceneid+'_B'+s for s in ['1', '2', '3', '4', '5', '6', '7', '8', '9']]
            delete_these_files += ['tmp']
            delete_these_files = tuple(delete_these_files)
        else:
            delete_these_files = [self.sceneid+'_toa_band'+s for s in ['1', '2', '3', '4', '5', '7']]
            delete_these_files += [self.sceneid+'_B'+s for s in ['1', '2', '3', '4', '5', '6', '7', '8']]
            delete_these_files += ['lndcal', 'lndsr', 'README.GTF', 'LogReport', 'tmp']
            delete_these_files = tuple(delete_these_files)

        # delete
        for file in os.listdir(self.path_scene_tmp()):
            if file.startswith(delete_these_files) or file.endswith('.gz'):
                os.remove(self.path_scene_tmp(filename=file))

        self.logger.info('Done cleaning up.')

    def check_sr(self, path):

        if self.sceneid[0:3] == 'LC8':
            srfiles = [self.sceneid + '_sr_band%s.img' % b for b in (1, 2, 3, 4, 5, 6, 7)]
        else:
            srfiles = [self.sceneid + '_sr_band%s.img' % b for b in (1, 2, 3, 4, 5, 7)]

        if os.path.exists(path):
            missing_files = []
            existing_files = os.listdir(path)
            for name in srfiles:
                # find and delete zero-size img files
                if name not in existing_files or os.stat(os.path.join(path, name)).st_size == 0:
                    missing_files.append(name)
        else:
            missing_files = srfiles

        return len(missing_files), missing_files

    def check_thermal(self, path):

        if self.sceneid[0:3] == 'LC8':
            thermalfiles = [self.sceneid + '_toa_band%s.img' % b for b in [10]]
        else:
            thermalfiles = [self.sceneid + '_sr_band%s.img' % b for b in [6]]

        if os.path.exists(path):
            missing_files = []
            existing_files = os.listdir(path)
            for name in thermalfiles:
                # find and delete zero-size img files
                if name not in existing_files or os.stat(os.path.join(path, name)).st_size == 0:
                    missing_files.append(name)
        else:
            missing_files = thermalfiles

        return len(missing_files), missing_files

    def check_cloudmask(self, path):

        cmfiles = [self.sceneid + '_' + n for n in ['cfmask.img', 'cfmask_conf.img']]

        if os.path.exists(path):
            missing_files = []
            existing_files = os.listdir(path)
            for name in cmfiles:
                # find and delete zero-size img files
                if name not in existing_files or os.stat(os.path.join(path, name)).st_size == 0:
                    missing_files.append(name)
        else:
            missing_files = cmfiles

        return len(missing_files), missing_files

    def convert_lpgs_to_espa(self, del_src_files=True):

        if os.path.isfile(self.path_scene_tmp(filename=self.file_mtl)) is False:
            self.logger.error("Error: MTL file does not exist or is not accessible: " + self.file_mtl)
            self.status = ERROR
            return ERROR

        mydir = os.getcwd()
        os.chdir(self.path_scene_tmp())

        cmdstr = [os.path.join(self._bindir, 'convert_lpgs_to_espa'), '--mtl', self.file_mtl, '--xml',
                  self.file_xml]
        if del_src_files is True:
            cmdstr += '--del_src_files'
        self.callcmd(cmdstr=cmdstr, mydir=mydir)

        os.chdir(mydir)

    def extract_archive(self):

        if self.file_archive.lower().endswith('zip'):

            esa_sceneid = os.path.basename(self.file_archive)[:-4]
            if not os.path.exists(self.path_scene_tmp()):
                os.makedirs(self.path_scene_tmp())

            with zipfile.ZipFile(self.file_archive) as zip_file:
                for member in zip_file.namelist():
                    filename = os.path.basename(member)
                    # skip directories
                    if not filename:
                        continue

                    filename = filename[:-3] + filename[-3:].lower()
                    if filename.startswith(esa_sceneid):
                        filename = filename.replace(esa_sceneid, self.sceneid)

                    if filename.endswith('_MTL.txt'):
                        mtl_id = os.path.basename(filename).replace('_MTL.txt', '')
                        if mtl_id != self.sceneid:
                            print('SceneID mismatch in %s. Id might be: %s' % (self.sceneid, mtl_id))

                    # copy file (taken from zipfile's extract)
                    source = zip_file.open(member)
                    target = open(os.path.join(self.path_scene_tmp(), filename), "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)

        elif self.file_archive.lower().endswith('tar.gz'):

            # filenames
            tardir = os.path.dirname(self.file_archive)
            tar_mtlfile = os.path.join(tardir, self.sceneid + '.mtl.txt')
            tar__wofile = os.path.join(tardir, self.sceneid + '._wo.txt')

            try:
                tar = tarfile.open(self.file_archive)
            except IOError:
                self.info = 'Unable to open %s' % self.file_archive
                self.batch_logger.error(self.info)
                self.status = ERROR
                return

            tar.extractall(path=self.path_scene_tmp())
            tar.close()

            # copy metadata file to archive file to speed up reading of the metadata from the archive
            for name in os.listdir(self.path_scene_tmp()):
                if name.endswith('MTL.txt'):
                    shutil.copyfile(self.path_scene_tmp(filename=name), tar_mtlfile)
                if name.endswith('_WO.txt'):
                    shutil.copyfile(self.path_scene_tmp(filename=name), tar__wofile)

            if '-SC' in self.file_archive:
                file_mtl = fnmatch.filter(os.listdir(self.path_scene_tmp()), '*_MTL.txt')
                if len(file_mtl) == 0:
                    self.info = 'Unable to open mtl file for %s' % self.sceneid
                    self.batch_logger.error(self.info)
                    self.status = ERROR
                    return

                self.file_mtl = file_mtl[0]
                old_path_scene = self.path_scene_tmp()
                self.sceneid = self.file_mtl[:21]
                self.file_xml = self.sceneid + '.xml'
                self.file_log = self.sceneid + '.log'
                if old_path_scene != self.path_scene_tmp():
                    os.rename(old_path_scene, self.path_scene_tmp())

            # create log-file handler if it does not already exist
            if os.path.isfile(self.path_scene_tmp(filename=self.file_log)) is False:
                self._init_file_logger(filename=self.path_scene_tmp(filename=self.file_log))

            self.mtl = read_mtl(self.path_scene_tmp(filename=self.file_mtl))
            self.logger.info('Extracted %s ' % self.file_archive)

        else:
            self.logger.error('Unknown archive type.')
        self.mtl = read_mtl(os.path.join(self.path_scene_tmp(), self.file_mtl))

    def ortho_find_baseimage(self, warp_doy=None, warp_year=None):

        base_img_root = os.path.join(espa_aux_dir, 'georeference')

        # base image
        base_img_dir = os.path.join(base_img_root, self.sceneid[3:6], self.sceneid[6:9])
        if not os.path.exists(base_img_dir):
            self.logger.error('Could not find reference image path: %s' % base_img_dir)
            self.status = ERROR
            return None

        base_mtl_list = file_search(base_img_dir, '*_MTL.txt')
        if len(base_mtl_list) == 0:
            self.logger.error('Could not find a reference image in %s' % base_img_dir)
            self.status = ERROR
            return None

        if warp_year is not None:
            warp_years = range(min(warp_year), max(warp_year) + 1)
            try:
                match = [x for x in base_mtl_list if int(os.path.basename(os.path.dirname(x))[9:13]) in warp_years]
                base_mtl_list = match
            except:
                self.logger.error('Could not find a reference image in year: %s' % ', '.join(warp_year))
                self.status = ERROR
                return ERROR

        if warp_doy is not None:
            warp_doys = range(min(warp_doy), max(warp_doy) + 1)
            try:
                match = [x for x in base_mtl_list if int(os.path.basename(os.path.dirname(x))[13:16]) in warp_doys]
                base_mtl_list = match
            except:
                self.logger.error('Could not find a reference image in doy range: %s' % ', '.join(warp_doy))
                self.status = ERROR
                return ERROR

        if len(base_mtl_list) > 1:
            doy_diff = []
            for base_mtl_file in base_mtl_list:
                try:
                    doy = int(os.path.basename(os.path.dirname(base_mtl_file))[13:16])
                except:
                    doy = 9999
                doy_diff.append(abs(doy - self.doy))

            doy_sort = [x for x in doy_diff]
            doy_sort.sort()
            doy_inds = [doy_diff.index(x) for x in doy_sort]
            base_mtl_file = [base_mtl_list[x] for x in doy_inds]

        else:
            base_mtl_file = base_mtl_list[0]

        return base_mtl_file

    def ortho(self, dem_file=None, polynom=2, warp_resampling='CC', warp_parameter_file='lndortho.cps_par.ini',
              out_pixel_size=30, option='r', warp_band=4, out_extent='BASE', base_order=1, warp_doy=None,
              warp_year=None):

        param_file = self.sceneid + '.inp'

        base_img_root = os.path.join(espa_aux_dir, 'georeference')
        cp_parameters_file = os.path.join(base_img_root, warp_parameter_file)
        file_list = os.listdir(self.path_scene_tmp())

        warp_infiles = fnmatch.filter(file_list, '*_B[1234567]*.[tT][iI][fF]')
        if len(warp_infiles) == 0:
            print('Could not find warp image tiffs in %s' % self.path_scene_tmp())

        warp_infiles.sort()
        warp_base_match_band_file = fnmatch.filter(file_list, '*_B%s*.[tT][iI][fF]' % warp_band)[0]
        warp_test_match_band_file = warp_base_match_band_file[:-3] + 'img'
        warp_outfiles = [x[:-3].replace('_VCID_', '') + 'img' for x in warp_infiles]

        mtl = read_mtl(os.path.join(self.path_scene_tmp(), self.file_mtl))
        utm_zone = mtl.get('PROJECTION_PARAMETERS').get('UTM_ZONE')

        # base image
        base_img_dir = os.path.join(base_img_root, self.sceneid[3:6], self.sceneid[6:9])
        if not os.path.exists(base_img_dir):
            self.logger.error('Could not find reference image path: %s' % base_img_dir)
            self.status = ERROR
            return ERROR

        base_mtl_list = file_search(base_img_dir, '*_MTL.txt')
        if len(base_mtl_list) == 0:
            self.logger.error('Could not find a reference image in %s' % base_img_dir)
            self.status = ERROR
            return ERROR

        if warp_year is not None:
            warp_years = range(min(warp_year), max(warp_year)+1)
            try:
                match = [x for x in base_mtl_list if int(os.path.basename(os.path.dirname(x))[9:13]) in warp_years]
                base_mtl_list = match
            except:
                self.logger.error('Could not find a reference image in year: %s' % ', '.join(warp_year))
                self.status = ERROR
                return ERROR

        if warp_doy is not None:
            warp_doys = range(min(warp_doy), max(warp_doy)+1)
            try:
                match = [x for x in base_mtl_list if int(os.path.basename(os.path.dirname(x))[13:16]) in warp_doys]
                base_mtl_list = match
            except:
                self.logger.error('Could not find a reference image in doy range: %s' % ', '.join(warp_doy))
                self.status = ERROR
                return ERROR

        if len(base_mtl_list) > 1:
            doy_diff = []
            for base_mtl_file in base_mtl_list:
                try:
                    doy = int(os.path.basename(os.path.dirname(base_mtl_file))[13:16])
                except:
                    doy = 9999
                doy_diff.append(abs(doy - self.doy))

            doy_sort = [x for x in doy_diff]
            doy_sort.sort()
            doy_inds = [doy_sort.index(x) for x in doy_diff]

            if base_order > len(doy_diff):
                k = len(doy_diff) - 1
            else:
                k = base_order - 1

            base_mtl_file = base_mtl_list[doy_inds.index(k)]
        else:
            base_mtl_file = base_mtl_list[0]

        base_image = file_search(os.path.dirname(base_mtl_file), '*_[bB]%s*.[Tt][Ii][Ff]' % warp_band)
        if len(base_image) == 0:
            self.logger.error('Could not find reference image in %s' % base_img_dir)
            self.status = ERROR
            return ERROR
        else:
            base_image = base_image[0]

        base_satellite = "Landsat" + os.path.basename(base_mtl_file)[2]
        warp_satellite = "Landsat" + self.sceneid[2]

        ortho_ini = read_ortho_ini(warp_parameter_file)
        min_num_cp_selected = ortho_ini.get('MIN_ACCEPTABLE_NCP')

        with open(os.path.join(self.path_scene_tmp(), param_file), 'w') as f_out:
            f_out.writelines('PARAMETER_FILE\n')
            f_out.writelines('\n')
            f_out.writelines('# LANDSAT base image \n')
            f_out.writelines('BASE_FILE_TYPE = GEOTIFF\n')
            f_out.writelines('BASE_NSAMPLE = -1\n')
            f_out.writelines('BASE_NLINE = -1\n')
            f_out.writelines('BASE_PIXEL_SIZE = -1\n')
            f_out.writelines('BASE_UPPER_LEFT_CORNER = -1, -1\n')
            f_out.writelines('BASE_LANDSAT = %s\n' % base_image)
            f_out.writelines('UTM_ZONE = %s\n' % utm_zone)
            f_out.writelines('BASE_SATELLITE = %s\n' % base_satellite)
            f_out.writelines('\n')
            f_out.writelines('# Landsat warp images\n')
            f_out.writelines('WARP_FILE_TYPE = GEOTIFF\n')
            f_out.writelines('WARP_NSAMPLE = -1\n')
            f_out.writelines('WARP_NLINE = -1\n')
            f_out.writelines('WARP_PIXEL_SIZE = -1\n')
            f_out.writelines('WARP_UPPER_LEFT_CORNER = -1, -1\n')
            f_out.writelines('WARP_NBANDS = %s\n' % len(warp_infiles))
            f_out.writelines('WARP_SATELLITE = %s\n' % warp_satellite)
            f_out.writelines('WARP_ORIENTATION_ANGLE = 0\n')
            f_out.writelines('WARP_LANDSAT_BAND  = %s\n' % ', '.join(warp_infiles))
            f_out.writelines('WARP_BASE_MATCH_BAND = %s\n' % warp_base_match_band_file)
            f_out.writelines('\n')
            f_out.writelines('# Landsat orthorectied output images\n')
            f_out.writelines('OUT_PIXEL_SIZE = %s\n' % out_pixel_size)
            f_out.writelines('# NN-nearest neighbor; BI-bilinear interpolation; CC-cubic convolution #\n')
            f_out.writelines('RESAMPLE_METHOD = %s\n' % warp_resampling.upper())
            f_out.writelines('# BASE-use base map extent; WARP-use warp map extent; DEF-user defined extent #\n')
            f_out.writelines('OUT_EXTENT = %s\n' % out_extent)
            f_out.writelines('OUT_LANDSAT_BAND =  %s\n' % ', '.join(warp_outfiles))
            f_out.writelines('OUT_BASE_MATCH_BAND = %s\n' % warp_test_match_band_file)
            f_out.writelines('OUT_BASE_POLY_ORDER = %s\n' % polynom)
            f_out.writelines('\n')
            f_out.writelines('# ancillary input for orthorectification process\n')
            if dem_file is not None:
                f_out.writelines('INPUT_DEM_FILE = %s\n' % dem_file)
            if cp_parameters_file is not None:
                f_out.writelines('CP_PARAMETERS_FILE = %s\n' % cp_parameters_file)
            f_out.writelines('\n')
            f_out.writelines('END\n')

        # need to delete the images created by convert_lpgs_to_espa before proceeding with the orthorectifaction
        for f in warp_outfiles:
            os.remove(os.path.join(self.path_scene_tmp(), f))
            os.remove(os.path.join(self.path_scene_tmp(), f.replace('img', 'hdr')))

        mydir = os.getcwd()
        os.chdir(self.path_scene_tmp())
        cmdstr = ['ortho', '-'+option, param_file]
        self.callcmd(cmdstr=cmdstr, mydir=mydir)
        for f in warp_infiles:
            os.remove(os.path.join(self.path_scene_tmp(), f))
        os.chdir(mydir)

        # read results form log-file
        with open(os.path.join(self.path_scene_tmp(), self.file_log), 'r') as f:
            ready = False
            failed = False
            matching_test_passed = False
            rmse_model = -1
            num_cp_selected = 0
            n_samples = 0
            n_lines = 0
            for line in f:
                if 'Orthorectification Processing Fails!' in line:
                    failed = True
                if 'doing precise registration and resampling' in line:
                    ready = True
                if ready and 'Num_CP_Selected' in line and 'RMSE' in line:
                    num_cp_selected, rmse_model = (x.split("=")[1].replace(' ', '') for x in line.split(','))
                    num_cp_selected = int(num_cp_selected)
                    rmse_model = float(rmse_model) * out_pixel_size
                if ready and 'number of samples' in line:
                    n_samples = line.split('=')[1].replace(' ', '')
                if ready and 'number of lines' in line:
                    n_lines = line.split('=')[1].replace(' ', '')
                if 'matching test passed' in line:
                    matching_test_passed = True

        if matching_test_passed:
            geometric_rmse_verify = rmse_model
        else:
            geometric_rmse_verify = 9999

        if rmse_model > out_pixel_size or num_cp_selected < min_num_cp_selected:
            failed = True

        if failed:
            self.logger.error('Unable to georeference %s' % (os.path.basename(self.file_archive)))
            self.status = ERROR
            return ERROR
        else:
            attributes = {'ground_control_points_model': num_cp_selected,
                          'geometric_rmse_model': rmse_model,
                          'geometric_rmse_verify': geometric_rmse_verify}
            update_mtl(os.path.join(self.path_scene_tmp(), self.file_mtl), attributes)

            # get new coordinates to update the xml
            hdr = read_hdr(os.path.join(self.path_scene_tmp(), warp_outfiles[0]))
            bbox = image_coordinates(hdr)
            utm_zone = int(hdr.get('map info').split(', ')[7])
            hemisphere = hdr.get('map info').split(', ')[8]
            ul_geo = transform_utm2geo(bbox[0], utm_zone=utm_zone, hemisphere=hemisphere)
            lr_geo = transform_utm2geo(bbox[1], utm_zone=utm_zone, hemisphere=hemisphere)

            # update xml file
            with open(os.path.join(self.path_scene_tmp(), self.file_xml), 'r') as f_out:
                xml_content = [line for line in f_out.readlines()]

            with open(os.path.join(self.path_scene_tmp(), self.file_xml), 'w') as f_out:
                for line in xml_content:
                    splits = line.split(' ')

                    if 'location="UL"' in splits:
                        for i, tag in enumerate(splits):
                            if tag.startswith('x='):
                                splits[i] = 'x="%s"' % "{0:.6f}".format(bbox[0][0])
                            elif tag.startswith('y='):
                                splits[i] = 'y="%s"/>' % "{0:.6f}".format(bbox[0][1])
                            elif tag.startswith('latitude='):
                                splits[i] = 'latitude="%s"' % "{0:.6f}".format(ul_geo[1])
                            elif tag.startswith('longitude='):
                                splits[i] = 'longitude="%s"/>' % "{0:.6f}".format(ul_geo[0])

                    if 'location="LR"' in splits:
                        for i, tag in enumerate(splits):
                            if tag.startswith('x='):
                                splits[i] = 'x="%s"' % "{0:.6f}".format(bbox[1][0])
                            elif tag.startswith('y='):
                                splits[i] = 'y="%s"/>' % "{0:.6f}".format(bbox[1][1])
                            elif tag.startswith('latitude='):
                                splits[i] = 'latitude="%s"' % "{0:.6f}".format(lr_geo[1])
                            elif tag.startswith('longitude='):
                                splits[i] = 'longitude="%s"/>' % "{0:.6f}".format(lr_geo[0])

                    if 'product="L1T"' in splits:
                        for i, tag in enumerate(splits):
                            if tag.startswith('nlines'):
                                splits[i] = 'nlines="%s"' % n_lines
                            elif tag.startswith('nsamps'):
                                splits[i] = 'nsamps="%s"' % n_samples

                    line = ' '.join(splits).replace('\n', '')
                    f_out.writelines(line + '\n')

            self.logger.info('%s, %s, %s, %s, Passed' % (self.file_archive, self.sceneid, rmse_model, num_cp_selected))

    def make_land_water_mask(self):

        if self.sceneid[0:3] == 'LC8':

            env_path = os.getenv('PATH')
            py27path = os.getenv('PY27PATH')
            os.environ['PATH'] = py27path + ':' + env_path

            mydir = os.getcwd()
            os.chdir(self.path_scene_tmp())

            if not os.path.isfile(self.path_scene_tmp(filename=self.file_xml)):
                msg = "Error: XML file does not exist or is not accessible: " + self.file_xml
                self.logger.error(msg)
                return ERROR

            cmdstr = [os.path.join(self._bindir, 'create_land_water_mask'), '--xml', self.file_xml]
            self.callcmd(cmdstr=cmdstr, mydir=mydir)

            os.chdir(mydir)
            os.environ['PATH'] = env_path

        else:
            self.logger.warning('Not a Landsat 8 image')

    def make_surface_reflectance(self, process_sr=True, write_toa=True, multithread=True):

        if self.sceneid[0:3] == 'LC8':
            self.run_l8sr(multithread=multithread, write_toa=write_toa)
        else:
            self.run_ledaps(process_sr=process_sr)

    def make_cloud_proximity(self, compress=compress):

        cloud_file = os.path.join(self.path_scene_tmp(), self.sceneid + '_cfmask.img')
        proximity_file = os.path.join(self.path_scene_tmp(), self.sceneid + '_cproximity.img')
        if not os.path.isfile(cloud_file):
            msg = "Error: cloud file does not exist or is not accessible: " + cloud_file
            self.logger.error(msg)
            self.status = ERROR
            return ERROR

        cloud_proximity(cloud_file, compress=compress)

    def run_l8sr(self, process_sr=True, write_toa=True, multithread=True):

        msg = 'Surface reflectance processing of Landsat file: %s' % self.file_xml
        self.logger.info(msg)

        # make sure the XML file exists
        if not os.path.isfile(self.path_scene_tmp(filename=self.file_xml)):
            msg = "Error: XML file does not exist or is not accessible: " + self.file_xml
            self.logger.error(msg)
            self.status = ERROR
            return ERROR

        self.make_land_water_mask()

        # get the path of the XML file and change directory to that location
        # for running this script.  save the current working directory for
        # return to upon error or when processing is complete.  Note: use
        # abspath to handle the case when the filepath is just the filename
        # and doesn't really include a file path (i.e. the current working
        # directory).
        mydir = os.getcwd()

        if not os.access(self.path_scene_tmp(), os.W_OK):
            msg = 'Path of XML file is not writable: %s.' % self.path_scene_tmp()
            self.logger.error(msg)
            self.status = ERROR
            return ERROR

        os.chdir(self.path_scene_tmp())

        # pull the date from the XML filename to determine which auxiliary
        # file should be used for input.  Example: LC80410272013181LGN00.xml
        # uses L8ANC2013181.hdf_fused.
        aux_file = 'L8ANC' + self.file_xml[9:16] + '.hdf_fused'

        # run surface reflectance algorithm, checking the return status.  exit
        # if any errors occur.
        if process_sr:
            process_sr_opt_str = "--process_sr=true"
        else:
            process_sr_opt_str = "--process_sr=false"
        if write_toa:
            write_toa_opt_str = "--write_toa"
        else:
            write_toa_opt_str = ""

        if multithread:
            binstring = "l8_sr_openmp"
        else:
            binstring = "l8_sr"

        cmdstr = [os.path.join(self._bindir, binstring), '--xml', self.file_xml, '--aux', aux_file]
        cmdstr += [process_sr_opt_str, write_toa_opt_str]
        self.callcmd(cmdstr=cmdstr, mydir=mydir)

        # successful completion.  return to the original directory.
        os.chdir(mydir)

    def run_ledaps(self, process_sr=True):

        # open the log file if it exists; use line buffering for the output
        msg = 'LEDAPS processing of Landsat XML file: %s' % self.file_xml
        self.logger.info(msg)

        # make sure the XML file exists
        if not os.path.isfile(self.path_scene_tmp(filename=self.file_xml)):
            msg = ("Error: XML file does not exist or is not accessible: %s"
                   % self.file_xml)
            self.logger.info(msg)
            self.status = ERROR
            return ERROR

        # get the path of the XML file and change directory to that location
        # for running this script.  save the current working directory for
        # return to upon error or when processing is complete.  Note: use
        # abspath to handle the case when the filepath is just the filename
        # and doesn't really include a file path (i.e. the current working
        # directory).
        mydir = os.getcwd()

        if not os.access(self.path_scene_tmp(), os.W_OK):
            msg = ('Path of XML file is not writable: %s.'
                   '  LEDAPS needs write access to the XML directory.'
                   % self.path_scene_tmp())
            self.logger.info(msg)
            self.status = ERROR
            return ERROR

        os.chdir(self.path_scene_tmp())

        # run LEDAPS modules, checking the return status of each module.
        # exit if any errors occur.
        cmdstr = [os.path.join(self._bindir, 'lndpm'), self.file_xml]
        self.callcmd(cmdstr=cmdstr, mydir=mydir)

        cmdstr = [os.path.join(self._bindir, 'lndcal'), "lndcal.%s.txt" % self.sceneid]
        self.callcmd(cmdstr=cmdstr, mydir=mydir)

        if process_sr is True:

            cmdstr = [os.path.join(self._bindir, 'lndsr'), "lndsr.%s.txt" % self.sceneid]
            self.callcmd(cmdstr=cmdstr, mydir=mydir)

            cmdstr = [os.path.join(self._bindir, 'lndsrbm.ksh'), "lndsr.%s.txt" % self.sceneid]
            self.callcmd(cmdstr=cmdstr, mydir=mydir)

        # successful completion.  return to the original directory.
        self.logger.info('Completion of LEDAPS.')
        os.chdir(mydir)

    def make_cloudmask(self, prob=22.5, cldpix=3, sdpix=3, verbose=False):

        if os.path.isfile(self.path_scene_tmp(filename=self.file_xml)) is False:
            self.logger.error("Error: XML file does not exist or is not accessible: " + self.file_xml)
            self.status = ERROR
            return ERROR

        # rough check if TOA are available
        # if len(self.file_toa) < 6:
        #     self.logger.error('Unable to find TOA files. CFMask needs them.')
        #     self.status = ERROR
        #     return ERROR
        #     # self.make_surface_reflectance(process_sr=False)

        env_path = os.getenv('PATH')
        py27path = os.getenv('PY27PATH')
        os.environ['PATH'] = py27path + ':' + env_path

        mydir = os.getcwd()

        if self.sceneid[0:3] == 'LC8':
            exe = os.path.join(self._bindir, 'l8cfmask')
        else:
            exe = os.path.join(self._bindir, 'cfmask')

        if verbose:
            verbose_str = '--verbose'
        else:
            verbose_str = ''

        os.chdir(self.path_scene_tmp())
        cmdstr = [exe, '--xml', self.file_xml, '--prob', str(prob), '--cldpix', str(cldpix), '--sdpix', str(sdpix)]
        cmdstr += [verbose_str]
        self.callcmd(cmdstr=cmdstr, mydir=mydir)

        os.chdir(mydir)
        os.environ['PATH'] = env_path

    def make_all(self, overwrite=False, process_sr=True, write_toa=True, multithread=False, warp_band=4,
                 warp_resampling='CC', prob=22.5, cldpix=3, sdpix=3, compress=True, debug=False, warp_esa=False,
                 polynom=2, warp_year=None, warp_doy=None, warp_parameter_file='lndortho.cps_par.ini'):

        # check if LPGS image
        tar__wofile = os.path.join(os.path.dirname(self.file_archive), self.sceneid + '._wo.txt')
        if os.path.isfile(tar__wofile):
            self.info = 'Not an LPGS image.'
            self.status = ERROR
            return

        # check metadata (if already extracted) for data type
        tar_mtlfile = os.path.join(os.path.dirname(self.file_archive), self.sceneid + '.mtl.txt')
        if os.path.isfile(tar_mtlfile):
            self.mtl = read_mtl(tar_mtlfile)
            if len(self.mtl) > 0:
                if self.mtl.get('PRODUCT_METADATA').get('DATA_TYPE') != 'L1T' and \
                   self.mtl.get('PRODUCT_METADATA').get('PRODUCT_TYPE') != 'L1T':
                    self.info = 'DATA_TYPE not L1T.'
                    self.status = ERROR
                    return

                # only process Landsat 8 scenes if sun zenith angles less than 76 degrees
                if self.mtl.get('PRODUCT_METADATA').get('SPACECRAFT_ID') == 'LANDSAT_8':
                    sun_elevation = self.mtl.get('IMAGE_ATTRIBUTES').get('SUN_ELEVATION')
                    if sun_elevation is not None:
                        sza = 90 - sun_elevation
                        if sza > 76:
                            self.info = 'SUN ZENITH ANGLE too large: %s' % sza
                            self.status = ERROR
                            return

        if (self.check_sr(self.path_scene())[0] == 0) and \
                (self.check_cloudmask(self.path_scene())[0] == 0) and not overwrite:
            self.status = SUCCESS
            self.info = 'Surface reflectance files exist. Use overwrite keyword.'
            return

        if self.status == SUCCESS:
            self.extract_archive()

        if self.status != SUCCESS:
            self.__del__()
            rmdir(self.path_scene_tmp())
            self.info = 'Error extracting archive file.'
            self.status = ERROR
            return

        # lets stop here if archive file is already a CDR
        if '-SC' in self.file_archive:
            self.compress()
        else:
            # check data type (if L1T) again
            self.mtl = read_mtl(os.path.join(self.path_scene_tmp(), self.file_mtl))
            if self.mtl.get('PRODUCT_METADATA').get('DATA_TYPE') != 'L1T' and \
               self.mtl.get('PRODUCT_METADATA').get('PRODUCT_TYPE') != 'L1T':
                self.__del__()
                rmdir(self.path_scene_tmp())
                self.status = ERROR
                self.info = 'DATA_TYPE not L1T.'
                return

            if self.station == 'ESA' and warp_esa:
                self.convert_lpgs_to_espa(del_src_files=False)
                self.ortho(polynom=polynom, warp_band=warp_band, warp_resampling=warp_resampling,
                           warp_parameter_file=warp_parameter_file, warp_year=None, warp_doy=None)
            else:
                self.convert_lpgs_to_espa(del_src_files=True)

            if self.status == SUCCESS:
                self.make_surface_reflectance(process_sr=process_sr,
                                              write_toa=write_toa, multithread=multithread)
            if self.status == SUCCESS:
                self.make_cloudmask(prob=prob, cldpix=cldpix, sdpix=sdpix)

            if self.status == SUCCESS:
                self.cleanup()
                if compress:
                    self.compress()

        # close scene logger
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        check_sr = self.check_sr(self.path_scene_tmp())
        check_cm = self.check_cloudmask(self.path_scene_tmp())
        if (check_cm[0] == 0) and (check_sr[0] == 0):
            # self.batch_logger.info(('%s - Process successful.' % self.sceneid))

            # rename folder
            if os.path.exists(self.path_scene()):
                rmdir(self.path_scene())
            os.rename(self.path_scene_tmp(), self.path_scene())
            if self.metacube is not None:
                self.metacube.add_scene(self.path_scene())
            self.info = 'Process successful.'
            return
        else:
            missing = check_sr[1] + check_cm[1]
            self.batch_logger.debug('%s - Could not create: %s' % (self.sceneid, ', '.join(missing)))
            if not debug:
                rmdir(self.path_scene_tmp())
            self.status = ERROR
            self.info = 'Finished with errors.'
            return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Atmospheric correction and cloud masking of Landsat data.')
    parser.add_argument("input", help="Single Landsat tgz archive file or directory to multiple tgz files.")
    parser.add_argument("output", help="Root directory for processed Landsat data.")
    parser.add_argument('--process_sr', default=True, type=bool)
    parser.add_argument('--write_toa', default=True, type=bool)
    parser.add_argument('--prob', default=22.5, type=float)
    parser.add_argument('--cldpix', default=3, type=int)
    parser.add_argument('--sdpix', default=3, type=int)
    parser.add_argument('--polynom', default=2, type=int)
    parser.add_argument('--cores', default=1, type=int)
    parser.add_argument('--path', nargs=2, default=[0, 0], type=int, help="from and to WRS-2 path")
    parser.add_argument('--row', nargs=2, default=[0, 0], type=int, help="from and to WRS-2 row")
    parser.add_argument('--year', nargs=2, default=[0, 0], type=int, help="from and to year")
    parser.add_argument('--doy', nargs=2, default=[0, 0], type=int, help="day of year")
    parser.add_argument('--filter', default='L[ECMT]*.tar.[gb]z', type=str)
    parser.add_argument('--multithread', action='store_true')
    parser.add_argument('--skip_compression', action='store_false', dest='compress')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--warp_esa', action='store_true')
    parser.add_argument('--warp_band', default=4, type=int)
    parser.add_argument('--warp_year', nargs=2, default=None, type=int)
    parser.add_argument('--warp_doy', nargs=2, default=None, type=int)
    parser.add_argument('--warp_resampling', default='CC', type=str,
                        help="CC - cubic convolution, NN - nearest neighbor, BI - bilinear")
    parser.add_argument('--warp_parameter_file', default='lndortho.cps_par.ini', type=str)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--offline', action='store_true')
#    parser.add_argument('--call', nargs='+', dest='commands')
    parser.add_argument('--version', action='version', version='espa_cdr %s' % espa_version)
    args = parser.parse_args()

    sys_logger = logging.getLogger('MAIN')
    sys_logger.setLevel(logging.INFO)

    # create console handler with a higher log level
    chm = logging.StreamHandler()
    chm.setLevel(logging.INFO)
    fmtm = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter_main = logging.Formatter(fmt=fmtm, datefmt='%Y-%m-%d %H:%M:%S')
    chm.setFormatter(formatter_main)
    sys_logger.addHandler(chm)

    if os.path.isfile(args.input):
        # run single image mode
        cdr_create(args.input, args.output)
    else:

        # create file handler for batch processing
        log_filename = 'espa_cdr_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'
        fhm = logging.FileHandler(os.path.join(args.output, log_filename))
        fhm.setLevel(logging.INFO)
        fhm.setFormatter(formatter_main)
        sys_logger.addHandler(fhm)

        import multiprocessing

        # run batch mode
        tgz_list = [os.path.join(dirpath, f)
                    for dirpath, dirnames, files in os.walk(args.input)
                    for f in fnmatch.filter(files, args.filter)]

        tgz_list = tgz_unique(tgz_list)

        if args.path[0] != 0:
            wrs_path = range(args.path[0], args.path[1] + 1)
            tgz_list = [f for f in tgz_list if int(get_sceneid_from_filename(os.path.basename(f))[3:6]) in wrs_path]
            sys_logger.info('Path filter set to: %s-%s.' % tuple(args.path))
            del wrs_path

        if args.row[0] != 0:
            wrs_row = range(args.row[0], args.row[1] + 1)
            tgz_list = [f for f in tgz_list if int(get_sceneid_from_filename(os.path.basename(f))[6:9]) in wrs_row]
            sys_logger.info('Row filter set to: %s-%s.' % tuple(args.row))
            del wrs_row

        if args.year[0] != 0:
            year_range = range(args.year[0], args.year[1] + 1)
            tgz_list = [f for f in tgz_list if int(get_sceneid_from_filename(os.path.basename(f))[9:13]) in year_range]
            sys_logger.info('Year filter set: %s-%s.' % tuple(args.year))

        if args.doy[0] != 0:
            doy_range = range(args.doy[0], args.doy[1] + 1)
            tgz_list = [f for f in tgz_list if int(get_sceneid_from_filename(os.path.basename(f))[13:16]) in doy_range]
            sys_logger.info('DOY filter set: %s-%s.' % tuple(args.doy))

        image_count = len(tgz_list)
        sys_logger.info('Found %s Landsat images in archive.' % image_count)

        if tgz_list:

            if args.cores == 1:
                for tgz_file in tgz_list:
                    res = cdr_create(tgz_file, args.output)
                    counter(res)
            else:
                pool = multiprocessing.Pool(processes=args.cores)
                for i in tgz_list:
                    pool.apply_async(cdr_create, (i, args.output), {}, counter)
                pool.close()
                pool.join()

    sys.exit()
