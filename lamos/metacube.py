#! /usr/bin/env python
import os
import fnmatch
import logging
from collections import OrderedDict
import itertools
import subprocess
import psycopg2
import glob
import gzip
import zipfile
import pandas as pd
import datetime
import shutil

try:
    import urllib.request as urllib2
except ImportError: # Python 2
    import urllib2


mtl_dict = OrderedDict([('LANDSAT_SCENE_ID', 'CHAR(21) PRIMARY KEY'),
                        ('FILE_DATE', 'timestamp'),
                        ('STATION_ID', 'CHAR(3)'),
                        ('PROCESSING_SOFTWARE_VERSION', 'VARCHAR(15)'),
                        ('DATA_TYPE', 'VARCHAR(12)'),
                        ('ELEVATION_SOURCE', 'VARCHAR(15)'),
                        ('SPACECRAFT_ID', 'VARCHAR(15)'),
                        ('SENSOR_ID', 'VARCHAR(12)'),
                        ('WRS_PATH', 'integer'),
                        ('WRS_ROW', 'integer'),
                        ('NADIR_OFFNADIR', 'VARCHAR(12)'),
                        ('DATE_ACQUIRED', 'date'),
                        ('SCENE_CENTER_TIME', 'time'),
                        ('CORNER_UL_LAT_PRODUCT', 'numeric'),
                        ('CORNER_UL_LON_PRODUCT', 'numeric'),
                        ('CORNER_UR_LAT_PRODUCT', 'numeric'),
                        ('CORNER_UR_LON_PRODUCT', 'numeric'),
                        ('CORNER_LL_LAT_PRODUCT', 'numeric'),
                        ('CORNER_LL_LON_PRODUCT', 'numeric'),
                        ('CORNER_LR_LAT_PRODUCT', 'numeric'),
                        ('CORNER_LR_LON_PRODUCT', 'numeric'),
                        ('CORNER_UL_PROJECTION_X_PRODUCT', 'numeric'),
                        ('CORNER_UL_PROJECTION_Y_PRODUCT', 'numeric'),
                        ('CORNER_UR_PROJECTION_X_PRODUCT', 'numeric'),
                        ('CORNER_UR_PROJECTION_Y_PRODUCT', 'numeric'),
                        ('CORNER_LL_PROJECTION_X_PRODUCT', 'numeric'),
                        ('CORNER_LL_PROJECTION_Y_PRODUCT', 'numeric'),
                        ('CORNER_LR_PROJECTION_X_PRODUCT', 'numeric'),
                        ('CORNER_LR_PROJECTION_Y_PRODUCT', 'numeric'),
                        ('METADATA_FILE_NAME', 'VARCHAR(30)'),
                        ('BPF_NAME_OLI', 'VARCHAR(50)'),
                        ('BPF_NAME_TIRS', 'VARCHAR(50)'),
                        ('CPF_NAME', 'VARCHAR(50)'),
                        ('RLUT_FILE_NAME', 'VARCHAR(50)'),
                        ('CLOUD_COVER', 'numeric'),
                        ('CLOUD_COVER_LAND', 'numeric'),
                        ('GROUND_CONTROL_POINTS_MODEL', 'integer'),
                        ('GEOMETRIC_RMSE_VERIFY', 'numeric'),
                        ('GEOMETRIC_RMSE_MODEL', 'numeric'),
                        ('GEOMETRIC_RMSE_MODEL_Y', 'numeric'),
                        ('GEOMETRIC_RMSE_MODEL_X', 'numeric'),
                        ('IMAGE_QUALITY_OLI', 'integer'),
                        ('IMAGE_QUALITY_TIRS', 'integer'),
                        ('TIRS_SSM_POSITION_STATUS', 'VARCHAR(15)'),
                        ('ROLL_ANGLE', 'numeric'),
                        ('SUN_AZIMUTH', 'numeric'),
                        ('SUN_ELEVATION', 'numeric'),
                        ('EARTH_SUN_DISTANCE', 'numeric'),
                        ('K1_CONSTANT_BAND_10', 'numeric'),
                        ('K1_CONSTANT_BAND_11', 'numeric'),
                        ('K2_CONSTANT_BAND_10', 'numeric'),
                        ('K2_CONSTANT_BAND_11', 'numeric'),
                        ('MAP_PROJECTION', 'VARCHAR(15)'),
                        ('DATUM', 'VARCHAR(15)'),
                        ('ELLIPSOID', 'VARCHAR(15)'),
                        ('UTM_ZONE', 'integer'),
                        ('DAY_OF_YEAR', 'integer'),
                        ('FILE_LOCATION', 'text')])


def read_hdr(img_file):

    hdr_files = [img_file[:-3]+'.hdr', img_file[:-4]+'.hdr', img_file+'.hdr']
    hdr_files = [hdr_file for hdr_file in hdr_files if os.path.isfile(hdr_file)]
    if len(hdr_files) != 1:
        print('Unable to find unique HDR for '+img_file)
        return None
    else:
        hdr_file = hdr_files[0]

    hdr = OrderedDict()
    with open(hdr_file, 'r') as f:
        for line in f:
            items = line.split(sep='=', maxsplit=1)
            if len(items) > 1:
                attr_name = items[0].strip()
                attr_value = items[1].strip()
                hdr[attr_name] = attr_value
    return hdr


def rmdir(path):
        if os.path.exists(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)


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


def write_list(text_file, content):
    with open(text_file, 'w') as f_out:
        for element in content:
            f_out.writelines('%s\n' % element)


def read_list(text_file):
    with open(text_file) as f:
        content = f.readlines()
        content = [line.rstrip('\n') for line in content]
    return content


def tuplefy(data):

    if type(data) is int or type(data) is str:
        return tuple([data, ])
    elif type(data) is tuple:
        return data
    else:
        return tuple(data)


def sensor_lookup(sensors):

    if type(sensors) is str:
        sensors_cp = [sensors]
    else:
        sensors_cp = sensors

    sensor_dict = {'ETM': ('LANDSAT_ETM', 'LANDSAT_ETM_SLC_OFF'),
                   'TM': ['LANDSAT_TM'],
                   'OLI_TIRS': ['OLI_TIRS'],
                   'OLI': ['OLI'],
                   'TIRS': ['TIRS']}
    result=[]

    for s in sensors_cp:
        y = sensor_dict.get(s)
        if y is not None:
            for x in y:
                result.append(x)
    return tuplefy(result)


def read_mtl(mtl_file):

    with open(mtl_file, 'r') as f:
        mtldata = {line.split('=')[0].strip(): (line.split('=')[1].strip().strip('"')) for line in f
                   if (len(line.split('=')) == 2) & (line.split('=')[0].strip() not in ['END_GROUP', 'GROUP', 'END'])}
    return mtldata


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


class Scene(object):

    def __init__(self):
        pass


class Connection(object):

    def __init__(self, cubedir=None, tempdir=None,
                 host='localhost', database="metacube", user="geomatic", password=None,
                 start_date=None, end_date=None, bbox=None, srid=4326, doy_range=None,
                 max_cloudcover=80, utm_zone=None, sensors=None):

        # create logger
        self.logger = logging.getLogger(user)
        self.logger.setLevel(logging.INFO)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt=fmt, datefmt='%Y-%m-%d %H:%M:%S')
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(ch)

        # setup properties
        self.cubedir = cubedir
        self.srid = str(srid)
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.bbox = bbox
        self.utm_zone = utm_zone
        self.max_cloudcover = max_cloudcover
        self.end_date = end_date
        self.start_date = start_date
        self.doy_range = doy_range
        self.sensors = sensors
        self.debug = True

        if tempdir is None:
            import tempfile
            self.tempdir = tempfile.gettempdir()
            # self.tempdir = os.path.join(self.cubedir, '_tmp')
        else:
            self.tempdir = tempdir

        try:
            self.conn = psycopg2.connect(host=host, database=database, user=user, password=password)
            self.cursor = self.conn.cursor()
        except RuntimeError:
            self.logger.error("Unable to connect to %s." % database)

    def __del__(self):

        self.cursor.close()
        self.conn.close()

        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def pg_count(self, table):
        """!Count the number of rows.
        @param table            : Name of the table to count rows.
        """
        sql_count = 'SELECT COUNT(*) FROM "' + table + '"'
        try:
            self.cursor.execute(sql_count)
        except:
            self.conn.rollback()
        n = self.cursor.fetchall()[0][0]
        return n

    def pg_select(self, table, columns, where='', limit='', df=False):
        """!Query and get the results of query.
        @param table            : Name of the table to parse.
        @param columns          : Name of columns to parse separating with comma(,).
        @param where            : Advanced search option for 'where' statement.
        """
        # Make a SQL statement.
        if where == '':
                sql_select = 'SELECT '+columns+' FROM "'+table + '" ' + limit
        else:
                sql_select = 'SELECT '+columns+' FROM '+table+' WHERE '+where+' '+limit
        # Execute the SQL statement.
        try:
            self.cursor.execute(sql_select)
            columns = [record.__getattribute__('name') for record in self.cursor.description]
            data = self.cursor.fetchall()
        except:
            self.conn.rollback()

        # Get the results.
        if df:
            result = pd.DataFrame(data, columns=columns)
        else:
            result = [x[0] for x in data]
        return result

        self.conn.commit()

    def pg_updatecol(self, table, columns, where=''):
        """!Update the values of columns.
        @param table            : Name of the table to parse.
        @param columns          : Keys values pair of column names and values to update.
        @param where            : Advanced search option for 'where' statement.
        """
        # Make a SQL statement.
        parse = ''
        for i in range(len(columns)):
                parse = parse + '"' + str(dict.keys(columns)[i]) + '"=' + str(dict.values(columns)[i]) + ','
        parse = parse.rstrip(',')

        if where == '':
                sql_update_col = 'UPDATE "' + table + '" SET ' + parse
        else:
                sql_update_col = 'UPDATE "' + table + '" SET ' + parse + ' WHERE ' + where
        # Execute the SQL statement.
        self.cursor.execute(sql_update_col)

    def pg_addcol(self, table, column, dtype):
        """!Add a column to the table.
        @param table            : Name of the table to add to.
        @param column           : Name of a column for adding.
        @param dtype            : Data type of the new column.
        """
        # Make a SQL statement.
        sql_addcol = 'ALTER TABLE "' + table + '" ADD COLUMN "' + column + '" ' + dtype
        # Execute the SQL statement.
        self.cursor.execute(sql_addcol)

    def pg_dropcol(self, table, column):
        """!Drop a column from the table.
        @param table            : Name of the table.
        @param column           : Name of the column to drop.
        """
        # Make a SQL statement.
        sql_dropcol = 'ALTER TABLE "' + table + '" DROP COLUMN "' + column + '"'
        # Execute the SQL statement.
        self.cursor.execute(sql_dropcol)

    def pg_add_shapefile(self, shape_filename, table_name=None, table_name_prefix='', srid=None):

        os_environ_path = os.environ['PATH']
        if os.name == 'nt' and 'PostgreSQL' not in os_environ_path:
            os.environ['PATH'] = r"c:\\Program Files\\PostgreSQL\\9.4\\bin\\;"+os_environ_path

        os.environ['PGPASSWORD'] = self.password

        if table_name is None:
            table_name = table_name_prefix + os.path.basename(shape_filename).replace('.shp', '')

        self.cursor.execute("DROP TABLE IF EXISTS  %s" % table_name)

        cmdstr = 'shp2pgsql -I -s %s %s %s.%s | psql -d %s -U %s -h localhost' % \
                 (srid, shape_filename, 'public',
                  table_name, self.database, self.user)

        try:
            print('Calling subprocess..')
            print(cmdstr)
            subprocess.call(cmdstr, shell=True)
        except:
            os.environ['PATH'] = os_environ_path

        os.environ['PATH'] = os_environ_path
        del os.environ['PGPASSWORD']

    def pg_addgeomcol(self, table, column, gtype, dim=2):
        """!Add a geometry column to the table.
        @param table            : Name of the table.
        @param column           : Name of the column for adding.
        @param gtype            : Geometry type of the new column.
        @param dim              : Dimension of the geometry. default is 2.
        """
        # Make a SQL statement.
        parse = "'public','" + table + "','" + column + "'," + self.srid + ",'" + gtype + "'," + str(dim)
        sql_addgeomcol = 'SELECT AddGeometryColumn (' + parse + ');'
        # Excute the SQL statement.
        self.cursor.execute(sql_addgeomcol)

    def pg_drop_view(self, view):
        # drop if table exists
        self.cursor.execute("DROP VIEW IF EXISTS %s" % view)
        self.conn.commit()

    def pg_dropConstraintSrid(self, table, column):
        """!Drop information of spatial reference system.
        @param table            : Name of the table.
        @param column           : Name of the column to drop.
        """
        # Make a SQL statement.
        sql_drop_constraint = 'ALTER TABLE "' + table + '" DROP CONSTRAINT "enforce_srid_' + column + '"'
        # Excute the SQL statement.
        self.cursor.execute(sql_drop_constraint)

    def pg_addConstraintSrid(self, table, column):
        """!Add information of spatial reference system.
        @param table            : Name of the table.
        @param column           : Name of the column to add SRID constraint.
        """
        # Make a SQL statement.
        sql_update_srid='UPDATE "' + table + '" SET "' + column+'" = ST_SetSRID("' + column + '",'+ self.srid + ')'
        # Execute the SQL statement.
        self.cursor.execute(sql_update_srid)
        # Make a SQL statement.
        sql_update_srid_c = 'ALTER TABLE "' + table + '" ADD CONSTRAINT "enforce_srid_' + column + \
                            '" CHECK(SRID("' + column + '")=' + self.srid + ')'
        # Execute the SQL statement.
        self.cursor.execute(sql_update_srid_c)

    def pg_wkb2text(self, wkb):
        """!Convert OGC Well Known Binary(WKB) format to OGC Enhanced Well Known Text(EWKT) format.
        @param wkb      : Input binary.
        """
        # Make a SQL statement.
        sql_select = "SELECT ST_AsEWKT('" + wkb + "'::geometry)"
        # Execute the SQL statement.
        self.cursor.execute(sql_select)
        # Get the results.
        results = self.cursor.fetchall()[0][0].split(";")[1]
        # Returns the results.
        return results

    def pg_ewkt(self, coordinates):

        if len(coordinates) == 2:
            points = ((coordinates[0][0], coordinates[0][1]),
                      (coordinates[1][0], coordinates[0][1]),
                      (coordinates[1][0], coordinates[1][1]),
                      (coordinates[0][0], coordinates[1][1]),
                      (coordinates[0][0], coordinates[0][1]))
        else:
            points = coordinates

        polygon = 'POLYGON(('
        for point in points:
            polygon += '%s %s, ' % point
        polygon = polygon[:-2] + '))'
        return polygon

    def pg_table_exists(self, table_name):
        self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name,))
        return self.cursor.fetchone()[0]

    def pg_vacuum(self, table_name, option='ANALYZE'):
        old_isolation_level = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        query = "VACUUM %s %s" % (option, table_name)
        self.cursor.execute(query)
        self.conn.commit()
        self.conn.set_isolation_level(old_isolation_level)

    def pg_update_geometry_landsat_cube(self):

        # update geometry and date based on bulk metadata
        self.cursor.execute("UPDATE landsat_cube AS l "
                            "SET "
                            "geom=ST_GeomFromText('POLYGON(('"
                            "|| a.upperleftcornerlongitude || ' ' || a.upperleftcornerlatitude || ', ' "
                            "|| a.upperrightcornerlongitude || ' ' || a.upperrightcornerlatitude || ', ' "
                            "|| a.lowerrightcornerlongitude || ' ' || a.lowerrightcornerlatitude || ', ' "
                            "|| a.lowerleftcornerlongitude || ' ' || a.lowerleftcornerlatitude || ', ' "
                            "|| a.upperleftcornerlongitude || ' ' || a.upperleftcornerlatitude || '))', 4326) "
                            "FROM landsat_archive AS a WHERE l.landsat_scene_id = a.sceneid;")
        self.conn.commit()

    def pg_create_table_landsat_esa(self):

        # delete archive table if it exists already, we will build from scratch
        self.cursor.execute("DROP TABLE IF EXISTS landsat_esa")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS landsat_esa ("
                            "Mission text, "
                            "Sensor text, "
                            "Product text, "
                            "INV text, "
                            "COLLECTION text, "
                            "Start timestamp without time zone, "
                            "Stop timestamp without time zone, "
                            "Status text, "
                            "ACQUISITIONDESCRIPTOR text, "
                            "PRODUCT_URL text, "
                            "Swath text, "
                            "Track int NOT NULL, "
                            "Frame int NOT NULL, "
                            "THUMBNAIL_URL text, "
                            "Orbit bigint NOT NULL, "
                            "CloudPercentage int NOT NULL, "
                            "Download_URL text, "
                            "PASSTIME text, "
                            "Pass text, "
                            "SCENE_CENTER text, "
                            "FOOTPRINT text, "
                            "Display boolean NOT NULL, "
                            "Mosaic boolean NOT NULL, "
                            "Action boolean NOT NULL, "
                            "esa_id text, "
                            "product_type text, "
                            "acquisition_date date, "
                            "scene_id char(21), "
                            "day_of_year numeric);")

        self.conn.commit()

    def scene_path(self, sceneid):
        self.cursor.execute("SELECT file_location FROM landsat_cube WHERE landsat_scene_id = %s;", (sceneid,))
        scene_path = self.cursor.fetchall()
        if len(scene_path) == 0:
            scene_path = ''
        else:
            scene_path = scene_path[0][0]
        # os.path.join(self.cubedir, sceneid[3:6], sceneid[6:9], sceneid)
        return scene_path

    def add_scene(self, directory, commit=True, table='landsat_cube'):

        mtl_file = glob.glob(os.path.join(directory, '*_MTL.txt'))

        if len(mtl_file) == 0:
            print('No valid MTL file found in %s.' % directory)
            return
        else:
            mtl_file = mtl_file[0]

        mtl = read_mtl(mtl_file)

        # coordinate columns for constructing the scene boundary
        points = [('CORNER_UL_LON_PRODUCT', 'CORNER_UL_LAT_PRODUCT'),
                  ('CORNER_UR_LON_PRODUCT', 'CORNER_UR_LAT_PRODUCT'),
                  ('CORNER_LR_LON_PRODUCT', 'CORNER_LR_LAT_PRODUCT'),
                  ('CORNER_LL_LON_PRODUCT', 'CORNER_LL_LAT_PRODUCT'),
                  ('CORNER_UL_LON_PRODUCT', 'CORNER_UL_LAT_PRODUCT')]

        # build value string for inserting the polygon into table
        poly_value = 'POLYGON(('
        for point in points:
            poly_value += '%s %s, ' % (mtl[point[0]], mtl[point[1]])
        poly_value = poly_value[:-2] + '))'

        mtl['DAY_OF_YEAR'] = mtl.get('LANDSAT_SCENE_ID')[13:16]
        mtl['FILE_LOCATION'] = os.path.dirname(mtl_file)

        values = [mtl.get(key) for key in mtl_dict]
        values.append(poly_value)
        values = tuple(values)
        inserts = ["%s"] * (len(values)-1)
        inserts.append('ST_GeomFromText(%s, %s)' % ('%s', self.srid))
        inserts = ', '.join(inserts)
        try:
            self.cursor.execute("" "INSERT INTO  " + table + " VALUES (" + inserts + ") ;" "", values)
        except:
            self.conn.rollback()
            self.cursor.execute("DELETE FROM " + table + " WHERE landsat_scene_id = %s;", (mtl.get('LANDSAT_SCENE_ID'),))
            self.cursor.execute("" "INSERT INTO  " + table + " VALUES (" + inserts + ") ;" "", values)

        if commit:
            self.conn.commit()

    def copy_scene(self, sceneids, outpath, debug=False):

        if not os.path.exists(outpath):
            os.mkdir(outpath)

        if type(sceneids) is str:
            sceneids = [sceneids]

        for sid in sceneids:
            from_path = self.scene_path(sid)
            to_path = os.path.join(outpath, sid[3:6], sid[6:9], sid)

            if not os.path.exists(to_path):
                for root, dirs, files in os.walk(from_path):
                    for fname in files:
                        relative_file = os.path.relpath(os.path.join(root, fname), from_path)
                        in_file = os.path.join(from_path, relative_file)
                        out_file = os.path.join(to_path, relative_file)
                        if os.path.isfile(out_file):
                            print('%s file exists.' % out_file)
                        else:
                            if not debug:
                                if not os.path.isdir(os.path.dirname(out_file)):
                                    os.makedirs(os.path.dirname(out_file))
                                shutil.copyfile(in_file, out_file)
                print('Copied ' + from_path + ' to ' + to_path)
            else:
                print('% exists.' + to_path)

    def move_scene(self, sceneids, outpath, delete_meta_entry=False):

        if not os.path.exists(outpath):
            os.mkdir(outpath)

        if type(sceneids) is str:
            sceneids = [sceneids]

        for sid in sceneids:
            old_path = self.scene_path(sid)
            new_path = os.path.join(outpath, sid[3:6], sid[6:9], sid)
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            os.rename(old_path, new_path)

            if delete_meta_entry:
                self.cursor.execute("DELETE FROM landsat_cube WHERE landsat_scene_id = %s;", (sid,))
            else:
                self.cursor.execute("UPDATE landsat_cube SET file_location = %s "
                                    "WHERE landsat_scene_id = %s;", (new_path, sid))

            print('Moved %s' % sid)

        self.conn.commit()

    def delete_scenes(self, sceneids):

        if type(sceneids) is str:
            sceneids = [sceneids]

        for sid in sceneids:
            scene_path = self.scene_path(sid)
            self.cursor.execute("DELETE FROM landsat_cube WHERE landsat_scene_id = %s;", (sid,))
            rmdir(scene_path)

        self.conn.commit()

    def get_landsat_esa_usgs(self, view=None, path=0, row=0):

        if view is not None:
            query = "CREATE OR REPLACE VIEW %s AS " % view
        else:
            query = ""

        # add view landsat coverage
        query += "SELECT e.*, a.*, c.landsat_scene_id " \
                 "from landsat_esa as e " \
                 "FULL OUTER JOIN landsat_archive as a " \
                 "ON e.track = a.path and e.frame = a.row and " \
                 "e.acquisition_date = a.acquisitiondate " \
                 "LEFT OUTER JOIN landsat_cube as c " \
                 "ON e.scene_id = c.landsat_scene_id "

        if path != 0:
            query += " WHERE (e.track = %s and e.frame = %s) or (a.path = %s and a.row = %s)" % (path, row, path, row)

        query += ";"

        self.cursor.execute(query)

        if view is None:
            columns = [record.__getattribute__('name') for record in self.cursor.description]

            data = self.cursor.fetchall()
            result = pd.DataFrame(data, columns=columns)
            self.conn.commit()
            return result
        else:
            self.conn.commit()

    def get_landsat_esa_gtc(self, view=None, esa_only=True, archive_dir=None, path=None, row=None, unique_esa=True):

        if view is not None:
            query = "CREATE OR REPLACE VIEW %s AS " % view
        else:
            query = ""

        if archive_dir is not None:
            eid_list = [f.replace('.ZIP', '') for dirpath, dirnames, files in os.walk(archive_dir)
                        for f in fnmatch.filter(files, '*.ZIP')]
        else:
            eid_list = []

        values = []

        # add view landsat coverage
        query += "SELECT "

        if unique_esa:
            query += "DISTINCT ON (e.scene_id) "

        query += "e.*, a.sceneid as usgs_scene_id, " \
                 "a.data_type_l1 as usgs_data_type, c.landsat_scene_id " \
                 "from landsat_esa as e " \
                 "LEFT OUTER JOIN landsat_archive as a " \
                 "ON e.track = a.path and e.frame = a.row and " \
                 "e.acquisition_date = a.acquisitiondate " \
                 "LEFT OUTER JOIN landsat_cube as c " \
                 "ON e.scene_id = c.landsat_scene_id " \
                 "WHERE e.product_type = 'GTC'"# \
                 #"ORDER BY e.scene_id"

        if esa_only:
            query += " and (a.sceneid is null or a.data_type_l1 = 'L1G')"

        if path is not None:
            if len(path) == 2:
                query += " and e.track between %s and %s"
                values += path
            else:
                query += " and e.track = %s"
                values += [path]

        if row is not None:
            if len(row) == 2:
                query += " and e.frame between %s and %s"
                values += row
            else:
                query += " and e.frame = %s"
                values += [row]

        if self.doy_range is not None:
            query += " and e.day_of_year between %s and %s"
            values += self.doy_range

        if self.max_cloudcover is not None:
            query += " and e.cloudpercentage <= %s"
            values += [self.max_cloudcover]

        if self.start_date is not None:
            query += " and e.acquisition_date >= %s "
            values += [self.start_date]

        if self.end_date is not None:
            query += " and a.acquisition_date <= %s "
            values += [self.end_date]

        query += ";"

        self.cursor.execute(query, tuple(values))

        if view is None:
            columns = [record.__getattribute__('name') for record in self.cursor.description]

            data = self.cursor.fetchall()
            result = pd.DataFrame(data, columns=columns)
            self.conn.commit()
            if len(eid_list) > 0:
                result = result[~result.esa_id.isin(eid_list)]

            print('Found %s records.' % result.shape[0])
            return result
        else:
            self.conn.commit()

    def get_landsat_coverage(self, view=None):

        if view is not None:
            query = "CREATE OR REPLACE VIEW %s AS " % view
        else:
            query = ""

        # add view landsat coverage
        query += "SELECT w.gid, w.geom, l.wrs_path, l.wrs_row, l.count, " \
                 "(l.wrs_path * 1000 + l.wrs_row) as pathrow " \
                 "FROM landsat_wrs2_descending w " \
                 "RIGHT JOIN landsat_local_count l ON w.path = l.wrs_path and w.row = l.wrs_row;"

        self.cursor.execute(query)

        if view is None:
            columns = [record.__getattribute__('name') for record in self.cursor.description]

            data = self.cursor.fetchall()
            result = pd.DataFrame(data, columns=columns)
            self.conn.commit()
            return result
        else:
            self.conn.commit()

    def get_landsat_scenes(self, view=None):

        if view is not None:
            query = "CREATE OR REPLACE VIEW %s AS " % view
        else:
            query = ""

        query += "SELECT * FROM landsat_cube WHERE cloud_cover < %s "
        values = [self.max_cloudcover]

        if self.bbox is not None:
            polygon = self.pg_ewkt(self.bbox)
            query += "AND ST_INTERSECTS(geom, ST_GeomFromText(%s, %s)) "
            values.append(polygon)
            values.append(self.srid)

        if self.utm_zone is not None:
            query += "AND utm_zone in %s "
            values.append(tuplefy(self.utm_zone))

        if self.sensors is not None:
            query += "AND sensor_id in %s "
            values.append(tuplefy(self.sensors))

        if self.doy_range is not None:
            query += "AND day_of_year >= %s AND day_of_year <= %s "
            values.append(self.doy_range[0])
            values.append(self.doy_range[1])

        if self.start_date is not None:
            query += "AND date_acquired >= %s "
            values.append(self.start_date)

        if self.end_date is not None:
            query += "AND date_acquired <= %s "
            values.append(self.end_date)

        query += "ORDER BY landsat_scene_id;"

        if self.debug:
            self.logger.info(query % tuple(values))
        self.cursor.execute(query, tuple(values))

        if view is None:
            columns = [record.__getattribute__('name') for record in self.cursor.description]

            sceneid = self.cursor.fetchall()
            # sceneid = [s[0] for s in sceneid]
            sceneid = pd.DataFrame(sceneid, columns=columns)
            self.conn.commit()
            return sceneid
        else:
            self.conn.commit()

    def get_landsat_strays(self, view=None, group=False, export=False):

        if view is not None:
            query = "CREATE OR REPLACE VIEW %s AS " % view
        else:
            query = ""

        query += "SELECT c.landsat_scene_id FROM landsat_cube c " \
                 "LEFT JOIN landsat_archive a ON c.landsat_scene_id = a.sceneid " \
                 "WHERE a.sceneid ISNULL "
        values = []

        if self.start_date is not None:
            query += "AND c.date_acquired >= %s "
            values.append(self.start_date)

        if self.end_date is not None:
            query += "AND c.date_acquired <= %s "
            values.append(self.end_date)

        query += "ORDER BY substring(c.landsat_scene_id, 4, 13) ;"

        if self.debug:
            self.logger.info(query % tuplefy(values))
        self.cursor.execute(query, tuplefy(values))

        if view is None:

            strays = [m[0] for m in self.cursor.fetchall()]

            if group:
                strays_dict = {footprint: list(sids) for footprint, sids in
                               itertools.groupby(strays, lambda sub: int(sub[3:9]))}

                if export:
                    for k in strays_dict.keys():
                        write_list(os.path.join(self.cubedir, 'info_scenes_strays_%s.txt' % k), strays_dict[k])
            else:
                write_list(os.path.join(self.cubedir, 'info_scenes_strays_all.txt'), strays)

            self.logger.info('Done.')
            return strays
        else:
            self.conn.commit()

    def get_landsat_obsolete(self):
        self.cursor.execute("SELECT esa.landsat_scene_id FROM ( "
                            "SELECT l.wrs_path, l.wrs_row, l.date_acquired, l.station_id, l.landsat_scene_id "
                            "FROM landsat_cube l "
                            "WHERE l.station_id='ESA') as esa "
                            "LEFT JOIN ( "
                            "SELECT l.wrs_path, l.wrs_row, l.date_acquired, l.station_id FROM landsat_cube l "
                            "WHERE l.station_id != 'ESA') as c "
                            "ON esa.wrs_path=c.wrs_path and esa.wrs_row=c.wrs_row "
                            "AND esa.date_acquired = c.date_acquired WHERE c.station_id NOTNULL ;")

        obsolete = [m[0] for m in self.cursor.fetchall()]
        return obsolete

    def get_landsat_archive(self, group=False, footprint=None, export=False, data_type=None, archive_only=True):

        query = "SELECT l.sceneid FROM landsat_archive l "
        values = []

        sql_where_or_and = "WHERE "
        if footprint is not None:
            footprints = tuplefy(footprint)
            if -1 in footprints:
                query += "RIGHT JOIN landsat_coverage c ON l.path = c.wrs_path and l.row = c.wrs_row "

            else:
                query += "WHERE l.path = %s and l.row = %s "
                values.append(footprints[0])
                values.append(footprints[1])
                sql_where_or_and = "AND "

        else:
            if self.bbox is not None:
                polygon = self.pg_ewkt(self.bbox)
            else:
                self.logger.warning('No geographic region specified for selection. Using boundary of data cube.')
                self.cursor.execute("SELECT ST_AsText(st_extent(geom)) FROM landsat_cube;")
                polygon = self.cursor.fetchall()[0][0]

            query += "RIGHT JOIN ( SELECT path, row from landsat_wrs2_descending "
            query += "WHERE ST_INTERSECTS(geom, ST_GeomFromText(%s, %s)) "
            query += ") as selection ON l.path = selection.path AND l.row = selection.row "
            values.append(polygon)
            values.append(self.srid)

        query += sql_where_or_and + "l.cloudcoverfull < %s "
        values.append(self.max_cloudcover)

        if self.start_date is not None:
            query += "AND l.acquisitiondate >= %s "
            values.append(self.start_date)

        if self.end_date is not None:
            query += "AND l.acquisitiondate <= %s "
            values.append(self.end_date)

        if self.utm_zone is not None:
            query += "AND utm_zone in %s "
            values.append(tuplefy(self.utm_zone))

        if self.sensors is not None:
            query += "AND sensor in %s "
            values.append(sensor_lookup(self.sensors))

        if self.doy_range is not None:
            query += "AND cast(substr(sceneid, 14, 3) as integer) between %s AND %s "
            values.append(self.doy_range[0])
            values.append(self.doy_range[1])

        if data_type is None:
            product_type = ('L1T', 'PR')
        else:
            product_type = tuplefy(data_type)

        query += "AND l.data_type_l1 in %s "
        values.append(product_type)

        if archive_only:
            query += "AND l.sceneid NOT IN (SELECT landsat_scene_id FROM landsat_cube) "

        query += ";"
        if self.debug:
            self.logger.info(query % tuple(values))

        try:
            self.cursor.execute(query, tuple(values))
            self.conn.commit()
        except:
            self.logger.error(self.cursor.statusmessage)
            self.logger.error('Unable to execute query.')
            self.conn.rollback()
            return None

        # self.cursor.execute("SELECT * FROM ("
        #                     "SELECT sceneid from landsat_archive "
        #                     "WHERE ST_INTERSECTS(geom, ST_GeomFromText(%s, %s)) "
        #                     "AND acquisitiondate >= %s AND acquisitiondate <= %s "
        #                     "AND cloudcoverfull < %s "
        #                     "AND data_type_l1 in ('L1T', 'PR')"
        #                     "AND sceneid not in landsat_cube.landsat_scene_id) as selection "
        #                     "LEFT JOIN landsat_cube ON "
        #                     "selection.sceneid = landsat_cube.landsat_scene_id "
        #                     "WHERE landsat_cube.landsat_scene_id ISNULL "
        #                     "ORDER BY substring(selection.sceneid, 4, 13) ;",
        #                     (polygon, self.srid, self.start_date, self.end_date, max_cloudcover))

        missing = [m[0] for m in self.cursor.fetchall()]
        count = len(missing)
        missing = sorted(missing, key= lambda sub: int(sub[3:16]))

        if group:

            missing_dict = {fp: list(sids) for fp, sids in
                            itertools.groupby(missing, lambda sub: int(sub[3:9]))}

            if export and self.cubedir is not None:
                for k in missing_dict.keys():
                    write_list(os.path.join(self.cubedir, 'info_scenes_new_%s.txt' % k), missing_dict[k])

            missing = missing_dict

        else:
            if export:
                write_list(os.path.join(self.cubedir, 'info_scenes_new_all.txt'), missing)

        print('Found %s records.' % count)
        return missing

    def get_landsat_updates(self, group=False, export=False):

        self.cursor.execute("SELECT c.landsat_scene_id FROM landsat_cube c "
                            "LEFT JOIN landsat_archive a on c.landsat_scene_id=a.sceneid "
                            "WHERE a.sceneid NOTNULL "
                            "AND date_part('DAY', a.dateupdated - c.file_date) > 10 "
                            "AND c.date_acquired between %s AND %s "
                            "ORDER BY substring(c.landsat_scene_id, 4, 13);",
                            (self.start_date, self.end_date))

        # SELECT a.dateupdated, a.dateupdated - c.file_date, c.* FROM landsat_cube c
        # LEFT JOIN landsat_archive a on c.landsat_scene_id=a.sceneid
        # WHERE a.sceneid NOTNULL and date_part('DAY', a.dateupdated - c.file_date) > 10
        # ORDER BY substring(a.sceneid, 4, 13);

        outdated = [m[0] for m in self.cursor.fetchall()]

        if group:
            outdated_dict = {fp: list(sids) for fp, sids in
                             itertools.groupby(outdated, lambda sub: int(sub[3:9]))}

            if export:
                for k in outdated_dict.keys():
                    write_list(os.path.join(self.cubedir, 'info_scenes_outdated_%s.txt' % k), outdated_dict[k])

            outdated = outdated_dict
        else:
            if export:
                write_list(os.path.join(self.cubedir, 'info_scenes_outdated_all.txt'), outdated)

        self.logger.info('Done.')
        return outdated

    def download_landsat_bulkmetadata(self, file_name, overwrite=False):

        if not os.path.isdir(self.tempdir):
            os.mkdir(self.tempdir)

        metadata_url = 'http://landsat.usgs.gov/metadata_service/bulk_metadata_files/'
        outfile = os.path.join(self.tempdir, file_name)
        if os.path.exists(outfile) and overwrite is not True:
            self.logger.info('Downloading %s.. File exists. Use OVERWRITE keyword to update.' % file_name)
        else:
            self.logger.info('Downloading %s' % outfile)
            req = urllib2.urlopen(os.path.join(metadata_url, file_name))
            with open(outfile, 'wb') as target_handle:
                target_handle.write(req.read())
            req.close()

    def setup_landsat_cube(self, filter='L[ECMT][1234578]*'):

        if self.cubedir is None or os.path.exists(self.cubedir) is False:
            self.logger.info('Unable to access cubedir.')
            return

        if not self.pg_table_exists('landsat_archive') or not self.pg_table_exists('countries') or not \
                self.pg_table_exists('landsat_wrs2_descending'):
            self.logger.info('A number of prerequisite tables are missing. First run:'
                  'object.setup_landsat_archive_metadata(), '
                  'object.setup_countries()'
                  'object.setup_landsat_wrs()')
            return

        import time
        start = time.clock()

        self.cursor.execute("DROP TABLE IF EXISTS landsat_cube_refresh;")

        try:
            sql_ct = ""
            for key, value in mtl_dict.items():
                sql_ct += "%s %s, " % (key, value)
            sql_ct = sql_ct[:-2] + ")"
            sql_ct = "CREATE TABLE landsat_cube_refresh (" + sql_ct
            self.cursor.execute(sql_ct)
        except Exception:
            self.conn.rollback()
            self.cursor.execute("DROP TABLE IF EXISTS landsat_cube_refresh CASCADE")
        self.conn.commit()

        self.pg_addgeomcol('landsat_cube_refresh', 'geom', 'POLYGON', dim=2)
        self.conn.commit()

        self.logger.info('Importing records..')
        for dirpath, dirnames, files in os.walk(self.cubedir):
            for dirs in fnmatch.filter(dirnames, filter):
                self.add_scene(os.path.join(dirpath, dirs), table='landsat_cube_refresh', commit=False)
        self.conn.commit()

        self.logger.info('Vacuuming..')
        self.pg_vacuum('landsat_cube_refresh')

        # update geometry and date based on bulk metadata
        self.cursor.execute("UPDATE landsat_cube_refresh AS l "
                            "SET "
                            "geom=ST_GeomFromText('POLYGON(('"
                            "|| a.upperleftcornerlongitude || ' ' || a.upperleftcornerlatitude || ', ' "
                            "|| a.upperrightcornerlongitude || ' ' || a.upperrightcornerlatitude || ', ' "
                            "|| a.lowerrightcornerlongitude || ' ' || a.lowerrightcornerlatitude || ', ' "
                            "|| a.lowerleftcornerlongitude || ' ' || a.lowerleftcornerlatitude || ', ' "
                            "|| a.upperleftcornerlongitude || ' ' || a.upperleftcornerlatitude || '))', 4326) "
                            "FROM landsat_archive AS a WHERE l.landsat_scene_id = a.sceneid;")

        # update bulk metadata on what scenes are available as cdr
        # print('Adding local info to landsat archive metadata')
        # self.cursor.execute("UPDATE landsat_archive AS a "
        #                     "SET local_cdr = TRUE "
        #                     "FROM landsat_cube AS c "
        #                     "WHERE a.sceneid = c.landsat_scene_id;")

        # drop if table exists
        self.cursor.execute("DROP TABLE IF EXISTS landsat_cube CASCADE;")
        self.cursor.execute("ALTER TABLE landsat_cube_refresh RENAME TO landsat_cube;")
        self.conn.commit()

        self.cursor.execute('CREATE INDEX landsat_cube_gix ON landsat_cube USING GIST (geom);')
        self.conn.commit()

        # add views
        self.cursor.execute("CREATE OR REPLACE VIEW landsat_local_count AS SELECT wrs_path, wrs_row, "
                            "count(wrs_path) FROM landsat_cube GROUP BY wrs_path, wrs_row;")
        self.get_landsat_coverage(view="landsat_coverage")

        self.conn.commit()

        # add global metadata to local db
        # self.cursor.execute("CREATE TABLE landsat_join AS "
        #                     "SELECT "
        #                     "l.*, g.flightpath, g.dateupdated, g.browseurl, g.upperleftcornerlatitude, "
        #                     "g.upperleftcornerlongitude, g.upperrightcornerlatitude, g.upperrightcornerlongitude, "
        #                     "g.lowerleftcornerlatitude, g.lowerleftcornerlongitude, g.lowerrightcornerlatitude, "
        #                     "g.lowerrightcornerlongitude, g.scenecenterlatitude, g.scenecenterlongitude "
        #                     "FROM landsat_cube AS l "
        #                     "LEFT JOIN landsat_archive AS g ON l.landsat_scene_id = g.sceneid;")

        self.logger.info('Imported %s records in %1.2fs' % (self.pg_count('landsat_cube'), time.clock() - start))

    def setup_landsat_esa(self, csv_dir=r'/Users/dirk/Workspace/eusample/metadata'):

        def esa_sceneid(id):

                if id[10:13] == 'TM_':
                    sensor = 'T'
                elif id[10:13] == 'ETM':
                    sensor = 'E'
                elif id[10:13] == 'MSS':
                    sensor = 'M'
                elif id[10:13] == 'OLI':
                    sensor = 'C'

                ayear = int(id[21:25])
                amonth = int(id[25:27])
                aday = int(id[27:29])
                adoy = (datetime.datetime(ayear, amonth, aday) - datetime.datetime(ayear, 1, 1)).days + 1
                wpath = id[61:64]
                wrow = id[66:69]
                doy = '{0:03d}'.format(adoy)
                sceneid = id[0] + sensor + id[3] + wpath + wrow + str(ayear) + doy + 'ESA00'

                return sceneid

        self.pg_create_table_landsat_esa()

        from odo import odo

        csv_list = [os.path.join(dirpath, f)
                    for dirpath, dirnames, files in os.walk(csv_dir)
                    for f in fnmatch.filter(files, '*.csv')]

        for csv_file in csv_list:

            md = pd.read_csv(csv_file)
            md.drop('Id', axis=1, inplace=True)
            md['esa_id'] = md['Download_URL'].map(lambda x: os.path.basename(x).replace('.ZIP', ''))
            md['product_type'] = md['esa_id'].map(lambda x: x[14:17])
            md['acquisition_date'] = md['esa_id'].map(lambda x: datetime.datetime(int(x[21:25]), int(x[25:27]), int(x[27:29])))
            md['scene_id'] = md['esa_id'].map(esa_sceneid)
            md['day_of_year'] = md['scene_id'].map(lambda x: int(x[13:16]))

            md.columns = map(str.lower, md.columns)
            odo(md, 'postgresql://%s:%s@%s:5432/%s::landsat_esa' % (self.user, self.password, self.host, self.database))

        self.cursor.execute("DROP TABLE IF EXISTS landsat_esa_temp;")
        self.cursor.execute("ALTER TABLE landsat_esa RENAME TO landsat_esa_temp;")
        self.conn.commit()

        self.pg_create_table_landsat_esa()
        self.cursor.execute("INSERT INTO landsat_esa SELECT DISTINCT * FROM landsat_esa_temp")
        self.cursor.execute("DROP TABLE IF EXISTS landsat_esa_temp;")

        self.conn.commit()
        self.pg_vacuum('landsat_esa')
        self.logger.info('Done.')

    # def setup_landsat_archive_blaze(self, wrs_path=[], wrs_row=[], europe=True):
    #
    #     import sqlite3
    #     from blaze import Data, odo
    #
    #     db_file = '/Users/dirk/Workspace/landsat.db'
    #     output = 'sqlite:///%s::%s' % (db_file, 'landsat_archive')
    #     # output = '/Users/dirk/Workspace/landsat.csv'
    #
    #     cols = ['sceneID', 'sensor', 'acquisitionDate', 'dateUpdated', 'browseAvailable', 'browseURL', 'path',
    #             'row', 'upperLeftCornerLatitude', 'upperLeftCornerLongitude', 'upperRightCornerLatitude',
    #             'upperRightCornerLongitude', 'lowerLeftCornerLatitude', 'lowerLeftCornerLongitude',
    #             'lowerRightCornerLatitude', 'lowerRightCornerLongitude', 'sceneCenterLatitude',
    #             'sceneCenterLongitude', 'cloudCover', 'cloudCoverFull', 'dayOrNight', 'sunElevation',
    #             'sunAzimuth', 'receivingStation', 'imageQuality1', 'DATA_TYPE_L1', 'cartURL', 'ELEVATION_SOURCE',
    #             'GROUND_CONTROL_POINTS_MODEL', 'GROUND_CONTROL_POINTS_VERIFY', 'GEOMETRIC_RMSE_MODEL',
    #             'GEOMETRIC_RMSE_VERIFY', 'UTM_ZONE']
    #
    #     conn = sqlite3.connect(db_file)
    #     cursor = conn.cursor()
    #
    #     # delete archive table if it exists already, we will build from scratch
    #     cursor.execute("DROP TABLE IF EXISTS landsat_archive2")
    #     conn.commit()
    #     conn.close()
    #     #db = Data('sqlite:///%s' % db_file)
    #
    #     # download if necessary
    #     # self.download_landsat_bulkmetadata(gz_filebase, overwrite=update)
    #
    #     gz_file = os.path.join(self.tempdir, 'LANDSAT_*.csv.gz')
    #
    #     # self.logger.info('Importing %s' % gz_file)
    #     data = Data(gz_file)[cols]
    #
    #     # drop records from other regions to save space if desired
    #     if europe:
    #         wrs_path = [150, 250]
    #         wrs_row = [5, 50]
    #
    #     if len(wrs_path) != 0 and len(wrs_row) != 0:
    #         data = data[data.path.isin(range(wrs_path[0], wrs_path[1]+1)) &
    #                     data.row.isin(range(wrs_row[0], wrs_row[1]+1))]
    #
    #     odo(data, output)

    def setup_landsat_archive_metadata(self, wrs_path=None, wrs_row=None, bbox=None, europe=True, debug=False):


        # global metadata file names
        bulk_metadata_files = ['LANDSAT_8.csv.gz', 'LANDSAT_ETM.csv.gz', 'LANDSAT_ETM_SLC_OFF.csv.gz',
                               'LANDSAT_TM-1980-1989.csv.gz', 'LANDSAT_TM-1990-1999.csv.gz',
                               'LANDSAT_TM-2000-2009.csv.gz', 'LANDSAT_TM-2010-2012.csv.gz']

        self.cursor.execute('SELECT create_landsat_archive();')
        self.conn.commit()

        for gz_filebase in bulk_metadata_files:

            gz_file = os.path.join(self.tempdir, gz_filebase)
            csv_file = gz_file.replace('.gz', '')

            # download if necessary
            self.download_landsat_bulkmetadata(gz_filebase, overwrite=True)

            try:
                self.logger.info('Extracting ' + gz_file)
                with open(csv_file, 'wb') as f_out:
                    with gzip.open(gz_file) as f_in:
                        f_out.writelines(f_in)
            except IOError:
                self.logger.error('Unable to open %s' % os.path.join(self.tempdir, gz_file))
                return

            self.logger.info('Importing %s' % csv_file)
            self.cursor.execute("COPY landsat_archive_refresh FROM '" + csv_file + "' HEADER DELIMITER ',' CSV;")
            self.conn.commit()
            os.remove(csv_file)
            if not debug:
                os.remove(gz_file)

        # drop records from other regions to save space if desired
        if wrs_path is None and wrs_row is None:
            if europe:
                wrs_path = [150, 250]
                wrs_row = [5, 50]

        if wrs_path is not None and wrs_row is not None:
            self.cursor.execute("DELETE FROM landsat_archive_refresh "
                                "WHERE path NOT BETWEEN %s and %s OR row NOT BETWEEN %s and %s;",
                                (wrs_path[0], wrs_path[1], wrs_row[0], wrs_row[1]))

        self.pg_addgeomcol('landsat_archive_refresh', 'geom', 'POLYGON', dim=2)
        self.cursor.execute("UPDATE landsat_archive_refresh SET geom=ST_GeomFromText('POLYGON(('"
                            "|| upperleftcornerlongitude || ' ' || upperleftcornerlatitude || ', '"
                            "|| upperrightcornerlongitude || ' ' || upperrightcornerlatitude || ', '"
                            "|| lowerrightcornerlongitude || ' ' || lowerrightcornerlatitude || ', '"
                            "|| lowerleftcornerlongitude || ' ' || lowerleftcornerlatitude || ', '"
                            "|| upperleftcornerlongitude || ' ' || upperleftcornerlatitude || '))', 4326);")

        self.conn.commit()
        self.pg_vacuum('landsat_archive_refresh')

        self.cursor.execute("DROP TABLE IF EXISTS landsat_archive;")
        self.cursor.execute("ALTER TABLE landsat_archive_refresh RENAME TO landsat_archive;")
        self.conn.commit()

        self.logger.info('Done.')

    def setup_landsat_wrs(self, debug=False):

        file_basenames = ['wrs2_descending.zip', 'wrs1_descending.zip']

        url = 'http://landsat.usgs.gov/documents/'
        outdir = os.path.join(self.tempdir, 'wrs')

        if not os.path.exists(outdir):
                os.mkdir(outdir)

        for file_base in file_basenames:
            local_file = os.path.join(outdir, file_base)
            # retrieve wrs shapefiles from usgs
            if not os.path.isfile(local_file):
                self.logger.info('Downloading %s' % file_base)
                req = urllib2.urlopen(os.path.join(url, file_base))
                with open(local_file, 'wb') as target_handle:
                    target_handle.write(req.read())
                req.close()

            with zipfile.ZipFile(local_file) as zf:
                zf.extractall(outdir)

            shapefile = local_file.replace('zip', 'shp')
            table_name = 'landsat_' + os.path.basename(shapefile).replace('.shp', '')

            self.pg_add_shapefile(shapefile, table_name=table_name, srid=4326)

            self.cursor.execute('CREATE INDEX ' + table_name + '_gix ON ' + table_name + ' USING GIST (geom);')

            self.conn.commit()
            self.pg_vacuum(table_name)

        if not debug:
            for fn in os.listdir(outdir):
                os.remove(os.path.join(outdir, fn))
            os.rmdir(outdir)

    def setup_countries(self, debug=False):

        # url = 'http://geocommons.com/overlays/33578.zip'
        url = 'http://thematicmapping.org/downloads/TM_WORLD_BORDERS-0.3.zip'
        outdir = os.path.join(self.tempdir, 'countries')

        if not os.path.exists(outdir):
                os.mkdir(outdir)

        # retrieve wrs shapefiles from url
        self.logger.info('Downloading %s' % url)
        local_file = os.path.join(outdir, os.path.basename(url))
        req = urllib2.urlopen(url)
        with open(local_file, 'wb') as target_handle:
            target_handle.write(req.read())
        req.close()

        with zipfile.ZipFile(local_file) as zf:
            zf.extractall(outdir)

        shapefile = os.path.join(outdir, 'TM_WORLD_BORDERS-0.3.shp')

        self.pg_add_shapefile(shapefile, table_name='countries', srid=4326)

        self.cursor.execute('CREATE INDEX countries_gix ON countries USING GIST (geom);')

        self.conn.commit()
        self.pg_vacuum('countries')

        if not debug:
            for fn in os.listdir(outdir):
                os.remove(os.path.join(outdir, fn))
            os.rmdir(outdir)

    def setup_continents(self, debug=False):

        url = 'http://pubs.usgs.gov/of/2006/1187/basemaps/continents/continents.zip'
        outdir = os.path.join(self.tempdir, 'continents')

        if not os.path.exists(outdir):
                os.mkdir(outdir)

        # retrieve wrs shapefiles from url
        self.logger.info('Downloading %s' % url)
        local_file = os.path.join(outdir, os.path.basename(url))
        req = urllib2.urlopen(url)
        with open(local_file, 'wb') as target_handle:
            target_handle.write(req.read())
        req.close()

        with zipfile.ZipFile(local_file) as zf:
            zf.extractall(outdir)

        shapefile = os.path.join(outdir, 'continent.shp')

        self.cursor.execute("DROP TABLE IF EXISTS continents")

        self.pg_add_shapefile(shapefile, table_name='continents', srid=4326)

        self.conn.commit()
        self.pg_vacuum('continents')

        if not debug:
            for fn in os.listdir(outdir):
                os.remove(os.path.join(outdir, fn))
            os.rmdir(outdir)

