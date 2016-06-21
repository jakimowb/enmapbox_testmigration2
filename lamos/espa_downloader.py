#!/usr/bin/env python

"""
Author: David Hill
Date: 01/31/2014
Purpose: A simple python client that will download all available (completed) scenes for a user order(s).
Requires: Python feedparser and standard Python installation.
Version: 1.0.1 adapted for HUB framework: after downloading images are extracted and the individual bands in binary
        format are compressed (Dirk Pflugmacher).
"""

import os
import tarfile
import argparse
import gzip
from collections import OrderedDict
import feedparser
from lamos import metacube

my_host='141.20.140.41'
my_database='metacube'
my_password="landsat"
my_user='geomatic'


try:
    import urllib.request as urllib2
except ImportError: # Python 2
    import urllib2


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


def compress_envi_file(img_file):

    hdr = read_hdr(img_file)
    if hdr.get('file compression', '0') == '0':
        with open(img_file, 'rb') as f_in:
            with gzip.open(img_file+'.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(img_file)
        os.rename(img_file+'.gz', img_file)

        hdr.update({'file compression': '1'})
        write_hdr(img_file, hdr)


def download_cdr(basedir, order='ALL', email=None, overwrite=False, compress=True, debug=False):
    con = Downloader(basedir, email=email)
    con.get_scenes(order=order, overwrite=overwrite, compress=compress, debug=debug)
    con.metacube.conn.close()


class SceneFeed(object):
    """SceneFeed parses the ESPA RSS Feed for the named email address and generates
    the list of Scenes that are available"""

    def __init__(self, email, host="http://espa.cr.usgs.gov"):
        """Construct a SceneFeed.

        Keyword arguments:
        email -- Email address orders were placed with
        host  -- http url of the RSS feed host
        """

        self.email = email

        if not host.startswith('http://'):
            host = ''.join(["http://", host])
        self.host = host

        self.feed_url = "%s/ordering/status/%s/rss/" % (self.host, self.email)

    def get_items(self, orderid='ALL'):
        """get_items generates Scene objects for all scenes that are available to be
        downloaded.  Supply an orderid to look for a particular order, otherwise all
        orders for self.email will be returned"""

        #yield Scenes with download urls
        feed = feedparser.parse(self.feed_url)

        for entry in feed.entries:

            #description field looks like this
            #'scene_status:thestatus,orderid:theid,orderdate:thedate'
            scene_order = entry.description.split(',')[1].split(':')[1]

            #only return values if they are in the requested order
            if orderid == "ALL" or scene_order == orderid:
                yield Scene(entry.link, scene_order, entry.title)


class Scene(object):

    def __init__(self, srcurl, orderid, sceneid):

        self.srcurl = srcurl

        self.orderid = orderid

        parts = self.srcurl.split("/")

        self.filename = parts[len(parts) - 1]

        self.name = self.filename.split('.tar.gz')[0]

        self.sceneid = sceneid


class Downloader(object):

    def __init__(self, basedir, email=None):
        self.basedir = basedir
        self.email = email
        self.metacube = metacube.Connection(host=my_host, database=my_database, password=my_password, user=my_user)

    def scene_path(self, scene):
        return os.path.join(self.basedir, scene.sceneid[3:6], scene.sceneid[6:9], scene.sceneid)

    def tgz_filename(self, scene):
        return os.path.join(self.basedir, scene.sceneid + '.tar.gz')

    def tmp_filename(self, scene):
        return os.path.join(self.basedir, scene.sceneid + '.part')

    def tmp_scene_path(self, scene):
        return os.path.join(self.basedir, scene.sceneid[3:6], scene.sceneid[6:9], '_tmp_' + scene.sceneid)

    def is_stored(self, scene):
        return os.path.exists(self.scene_path(scene))

    def is_downloaded(self, scene):
        return os.path.exists(self.tgz_filename(scene))

    def store(self, scene, overwrite=False, compress=True, debug=False):

        if self.is_stored(scene) and overwrite is False:
            print('Scene %s already exists. Set overwrite=True to update.' % scene.sceneid)
            return
        elif self.is_stored(scene):
            rmdir(self.scene_path(scene))

        # make sure we have a target to land the scenes
        if not os.path.exists(self.basedir):
            os.makedirs(self.basedir)
            print("Created target_directory:%s" % self.basedir)

        if not self.is_downloaded(scene):
            req = urllib2.urlopen(scene.srcurl)

            print("Downloading %s to %s" % (scene.sceneid, self.basedir))

            with open(self.tmp_filename(scene), 'wb') as target_handle:
                target_handle.write(req.read())
            req.close()

            os.rename(self.tmp_filename(scene), self.tgz_filename(scene))

        # extract
        tar = tarfile.open(self.tgz_filename(scene))
        tar.extractall(path=self.tmp_scene_path(scene))
        tar.close()

        for file in os.listdir(self.tmp_scene_path(scene)):
            if (file.startswith(scene.sceneid + '_B') or file.endswith('.gz')) \
                    and not file.startswith(scene.sceneid + '_BQA'):
                os.remove(os.path.join(self.tmp_scene_path(scene), file))

        if compress:
            for file in os.listdir(self.tmp_scene_path(scene)):
                if file.endswith('.img'):
                    compress_envi_file(os.path.join(self.tmp_scene_path(scene), file))

        if not debug:
            os.remove(self.tgz_filename(scene))

        with open(os.path.join(self.tmp_scene_path(scene), scene.sceneid + '.log'), 'w') as f_out:
            f_out.writelines('%s\n' % scene.filename)

        os.rename(self.tmp_scene_path(scene), self.scene_path(scene))

        # add scene to database
        self.metacube.add_scene(self.scene_path(scene))

    def get_scenes(self, order='ALL', overwrite=False, compress=True, debug=False):
        for scene in SceneFeed(self.email).get_items(order):
            self.store(scene, overwrite=overwrite, compress=compress, debug=debug)


if __name__ == '__main__':

    epilog = 'ESPA Bulk Download Client Version 1.0.0. [Tested with Python 2.7]\n ' \
             'Retrieves all completed scenes for the user/order\n' \
             'and places them into the target directory.\n' \
             'Scenes are organized by order.\n\n' \
             'It is safe to cancel and restart the client, as it will\n' \
             'only download scenes one time (per directory)\n \n'  \
             '*** Important ***\n' \
             'If you intend to automate execution of this script,\n' \
             'please take care to ensure only 1 instance runs at a time.\n' \
             'Also please do not schedule execution more frequently than\n' \
             'once per hour.\n' \
             ' \n' \
             '------------\n' \
             'Examples:\n' \
             '------------\n' \
             'Linux/Mac: ./espa_downloader.py -e your_email@server.com -o ALL -d /some/directory/with/free/space\n\n' \
             'Windows:   C:\python34\python espa_downloader.py -e your_email@server.com -o ALL ' \
             '-d C:\some\directory\with\\free\space\n'

    parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-e", "--email", required=True, help="email address for the user that submitted the order)")

    parser.add_argument("-o", "--order", default='ALL', type=str,
                        help="which order to download (use ALL for every order)")

    parser.add_argument("-d", "--target_directory", required=True,
                        help="where to store the downloaded scenes")

    parser.add_argument('--overwrite', action='store_true')

    parser.add_argument('--compress', default=True, type=bool)

    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    download_cdr(args.target_directory, order=args.order, email=args.email, overwrite=args.overwrite,
                 compress=args.compress, debug=args.debug)

