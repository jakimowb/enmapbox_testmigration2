# -*- coding: utf-8 -*-

"""
***************************************************************************
    create_plugin.py
    Script to build the EnMAP-Box QGIS Plugin from Repository code
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.
                 *
*                                                                         *
***************************************************************************
"""
# noinspection PyPep8Naming

import os, sys, re, shutil, zipfile, datetime, requests, http, mimetypes, pathlib
import docutils
import docutils.writers
from qgis.PyQt.QtXml import *
import typing
import argparse
from enmapbox.gui.utils import file_search

from requests.auth import HTTPBasicAuth
from http.client import responses
import xml.etree.ElementTree as ET

from qgis.PyQt.QtCore import *

from enmapbox.externals.qps.make.deploy import QGISMetadataFileWriter

import enmapbox
from enmapbox import DIR_REPO, __version__


CHECK_COMMITS = False

########## Config Section

MD = QGISMetadataFileWriter()
MD.mName = 'EnMAP-Box 3'
MD.mDescription = 'Imaging Spectroscopy and Remote Sensing for QGIS'
MD.mTags = ['Raster']
MD.mCategory = 'Analysis'
MD.mAuthor = 'Andreas Rabe, Benjamin Jakimow, Sebastian van der Linden'
MD.mIcon = 'enmapbox/gui/ui/icons/enmapbox.png'
MD.mHomepage = 'http://www.enmap.org/'
MD.mAbout = 'The EnMAP-Box is designed to process and visualize hyperspectral remote sensing data, and particularly developed to handle EnMAP products.'
MD.mTracker = 'https://bitbucket.org/hu-geomatics/enmap-box/issues'
MD.mRepository = 'https://bitbucket.org/hu-geomatics/enmap-box.git'
MD.mQgisMinimumVersion = '3.10'
MD.mEmail = 'enmapbox@enmap.org'

########## End of config section

def scantree(path, pattern=re.compile('.$')) -> typing.Iterator[pathlib.Path]:
    """
    Recursively returns file paths in directory
    :param path: root directory to search in
    :param pattern: str with required file ending, e.g. ".py" to search for *.py files
    :return: pathlib.Path
    """
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path, pattern=pattern)
        elif entry.is_file and pattern.search(entry.path):
            yield pathlib.Path(entry.path)


def create_enmapbox_plugin(include_testdata: bool = False, include_qgisresources: bool = False):

    DIR_REPO = pathlib.Path(__file__).resolve().parents[1]
    assert (DIR_REPO / '.git').is_dir()

    DIR_DEPLOY = DIR_REPO / 'deploy'

    try:
        import git
        REPO = git.Repo(DIR_REPO)
        currentBranch = REPO.active_branch.name
    except Exception as ex:
        currentBranch = 'TEST'
        print('Unable to find git repo. Set currentBranch to "{}"'.format(currentBranch))

    timestamp = datetime.datetime.now().isoformat().split('.')[0]

    BUILD_NAME = '{}.{}.{}'.format(__version__, timestamp, currentBranch)
    BUILD_NAME = re.sub(r'[:-]', '', BUILD_NAME)
    BUILD_NAME = re.sub(r'[\\/]', '_', BUILD_NAME)
    PLUGIN_DIR = DIR_DEPLOY / 'enmapboxplugin'
    PLUGIN_ZIP = DIR_DEPLOY / 'enmapboxplugin.{}.zip'.format(BUILD_NAME)

    if PLUGIN_DIR.is_dir():
        shutil.rmtree(PLUGIN_DIR)
    os.makedirs(PLUGIN_DIR, exist_ok=True)

    PATH_METADATAFILE = PLUGIN_DIR / 'metadata.txt'
    MD.mVersion = BUILD_NAME
    MD.writeMetadataTxt(PATH_METADATAFILE)

    #1. (re)-compile all enmapbox resource files

    from scripts.compile_resourcefiles import compileEnMAPBoxResources
    compileEnMAPBoxResources()

    # copy python and other resource files
    pattern = re.compile(r'\.(py|svg|png|txt|ui|tif|qml|md|js|css)$')
    files = list(scantree(DIR_REPO / 'enmapbox', pattern=pattern))
    files.extend(list(scantree(DIR_REPO / 'site-packages', pattern=pattern)))
    files.extend(list(scantree(DIR_REPO / 'hubflow', pattern=pattern)))
    files.extend(list(scantree(DIR_REPO / 'hubdc', pattern=pattern)))
    files.extend(list(scantree(DIR_REPO / 'hubdsm', pattern=pattern)))
    files.extend(list(scantree(DIR_REPO / 'enmapboxgeoalgorithms', pattern=pattern)))
    # add unit tests
    files.extend(list(scantree(DIR_REPO / 'enmapboxtesting', pattern=re.compile(r'\.py$'))))
    files.append(DIR_REPO / '__init__.py')
    files.append(DIR_REPO / 'CHANGELOG.rst')
    files.append(DIR_REPO / 'CONTRIBUTORS.rst')
    files.append(DIR_REPO / 'LICENSE.md')
    files.append(DIR_REPO / 'LICENSE.txt')
    files.append(DIR_REPO / 'requirements.txt')
    files.append(DIR_REPO / 'requirements_developer.txt')

    for fileSrc in files:
        assert fileSrc.is_file()
        fileDst = PLUGIN_DIR / fileSrc.relative_to(DIR_REPO)
        os.makedirs(fileDst.parent, exist_ok=True)
        shutil.copy(fileSrc, fileDst.parent)

    #update metadata version

    f = open(DIR_REPO / 'enmapbox' / '__init__.py')
    lines = f.read()
    f.close()
    lines = re.sub(r'(__version__\W*=\W*)([^\n]+)', r'__version__ = "{}"\n'.format(BUILD_NAME), lines)
    f = open(PLUGIN_DIR  / 'enmapbox' / '__init__.py', 'w')
    f.write(lines)
    f.flush()
    f.close()

    # include test data into test versions
    if include_testdata and not re.search(currentBranch, 'master', re.I):
        if os.path.isdir(enmapbox.DIR_TESTDATA):
            shutil.copytree(enmapbox.DIR_TESTDATA, PLUGIN_DIR / 'enmapboxtestdata')

    if include_qgisresources and not re.search(currentBranch, 'master', re.I):
        qgisresources = pathlib.Path(DIR_REPO) / 'qgisresources'
        shutil.copytree(qgisresources, PLUGIN_DIR / 'qgisresources')

    createCHANGELOG(PLUGIN_DIR)

    # 5. create a zip
    print('Create zipfile...')
    from enmapbox.gui.utils import zipdir

    zipdir(PLUGIN_DIR, PLUGIN_ZIP)

    # 7. install the zip file into the local QGIS instance. You will need to restart QGIS!
    if True:
        info = []
        info.append('\n### To update/install the EnMAP-Box, run this command on your QGIS Python shell:\n')
        info.append('from pyplugin_installer.installer import pluginInstaller')
        info.append('pluginInstaller.installFromZipFile(r"{}")'.format(PLUGIN_ZIP))
        info.append('#### Close (and restart manually)\n')
        #print('iface.mainWindow().close()\n')
        info.append('QProcess.startDetached(QgsApplication.arguments()[0], [])')
        info.append('QgsApplication.quit()\n')
        info.append('## press ENTER\n')

        print('\n'.join(info))

        from qgis.PyQt.QtGui import QClipboard, QGuiApplication

        #cb = QGuiApplication.clipboard()
        #if isinstance(cb, QClipboard):
        #    cb.setText('\n'.join(info))


    print('Finished')


def createCHANGELOG(dirPlugin):
    """
    Reads the CHANGELOG.rst and creates the deploy/CHANGELOG (without extension!) for the QGIS Plugin Manager
    :return:
    """

    pathMD = os.path.join(DIR_REPO, 'CHANGELOG.rst')
    pathCL = os.path.join(dirPlugin, 'CHANGELOG')

    os.makedirs(os.path.dirname(pathCL), exist_ok=True)
    assert os.path.isfile(pathMD)
    import sphinx.transforms
    import docutils.core

    overrides = {'stylesheet':None,
                 'embed_stylesheet':False,
                 'output_encoding':'utf-8',
                 }

    html = docutils.core.publish_file(source_path=pathMD, writer_name='html5', settings_overrides=overrides)

    from xml.dom import minidom
    xml = minidom.parseString(html)
    #  remove headline
    for i, node in enumerate(xml.getElementsByTagName('h1')):
        if i == 0:
            node.parentNode.removeChild(node)
        else:
            node.tagName = 'h4'

    for node in xml.getElementsByTagName('link'):
        node.parentNode.removeChild(node)

    for node in xml.getElementsByTagName('meta'):
        if node.getAttribute('name') == 'generator':
            node.parentNode.removeChild(node)


    xml = xml.getElementsByTagName('body')[0]
    html = xml.toxml()
    html_cleaned = []
    for line in html.split('\n'):
        # line to modify
        line = re.sub(r'class="[^"]*"', '', line)
        line = re.sub(r'id="[^"]*"', '', line)
        line = re.sub(r'<li><p>', '<li>', line)
        line = re.sub(r'</p></li>', '</li>', line)
        line = re.sub(r'</?(dd|dt|div|body)[ ]*>', '', line)
        line = line.strip()
        if line != '':
            html_cleaned.append(line)
    # make html compact

    with open(pathCL, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_cleaned))

    if False:
        with open(pathCL+'.html', 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_cleaned))
    s = ""


def updateRepositoryXML(path:str=None):
    """
    Creates the XML files:
        deploy/qgis_plugin_develop.xml - to be uploaded to the bitbucket repository
        deploy/qgis_plugin_develop_local.xml - can be used as local QGIS Repository source
    :param path: str, optional, path of local *.zip which has been build with build()
    :return:
    """
    if not isinstance(path, str):
        zipFiles = list(file_search(DIR_DEPLOY, PLUGIN_NAME+'*.zip'))
        zipFiles.sort(key=lambda f:os.path.getctime(f))
        path = zipFiles[-1]

    assert isinstance(path, str)
    assert os.path.isfile(path)
    assert os.path.splitext(path)[1] == '.zip'

    os.makedirs(DIR_DEPLOY, exist_ok=True)
    bn = os.path.basename(path)
    version = re.search(r'^' + PLUGIN_NAME + '\.(.*)\.zip$', bn).group(1)
    s = ""
    """
 <?xml-stylesheet type="text/xsl" href="plugins.xsl" ?>
<plugins>
   <pyqgis_plugin name="EnMAP-Box (develop version)" version="3.2.20180904T1723.DEVELOP">
        <description><![CDATA[EnMAP-Box development version]]></description>
        <about><![CDATA[EnMAP-Box Preview.]]></about>
        <version>3.2.20180904T1723.DEVELOP</version>
        <trusted>True</trusted>
        <qgis_minimum_version>3.4.4</qgis_minimum_version>
        <qgis_maximum_version>3.99.0</qgis_maximum_version>
        <homepage><![CDATA[https://bitbucket.org/hu-geomatics/enmap-box/]]></homepage>
        <file_name>EnMAP-Box.3.3.20180904T1723.develop.snapshot.zip</file_name>
        <icon></icon>
        <author_name><![CDATA[HU Geomatics]]></author_name>
        <download_url>https://bitbucket.org/hu-geomatics/enmap-box/downloads/enmapboxplugin.3.2.20180904T1723.develop.snapshot.zip</download_url>
        <uploaded_by><![CDATA[jakimowb]]></uploaded_by>
        <experimental>False</experimental>
        <deprecated>False</deprecated>
        <tracker><![CDATA[https://bitbucket.org/hu-geomatics/enmap-box/issues/]]></tracker>
        <repository><![CDATA[https://bitbucket.org/hu-geomatics/enmap-box/src]]></repository>
        <tags><![CDATA[Remote Sensing]]></tags>
        <downloads>0</downloads>
        <average_vote>0.0</average_vote>
        <rating_votes>0</rating_votes>
        <external_dependencies></external_dependencies>
        <server>True</server>
    </pyqgis_plugin>
</plugins>
    """
    download_url = URL_DOWNLOADS+'/'+bn

    root = ET.Element('plugins')
    plugin = ET.SubElement(root, 'pyqgis_plugin')
    plugin.attrib['name'] = "EnMAP-Box (develop version)"
    plugin.attrib['version'] = '{}'.format(version)
    ET.SubElement(plugin, 'description').text = r'EnMAP-Box development version'
    ET.SubElement(plugin, 'about').text = 'Preview'
    ET.SubElement(plugin, 'version').text = version
    ET.SubElement(plugin, 'qgis_minimum_version').text = '3.4'
    ET.SubElement(plugin, 'qgis_maximum_version').text = '3.99'
    ET.SubElement(plugin, 'homepage').text = enmapbox.HOMEPAGE
    ET.SubElement(plugin, 'file_name').text = bn
    ET.SubElement(plugin, 'icon').text = 'enmapbox.png'
    ET.SubElement(plugin, 'author_name').text = 'Andreas Rabe, Benjamin Jakimow, Fabian Thiel, Sebastian van der Linden'
    ET.SubElement(plugin, 'download_url').text = download_url
    ET.SubElement(plugin, 'deprecated').text = 'False'
    #is this a supported tag????
    #ET.SubElement(plugin, 'external_dependencies').text = ','.join(enmapbox.DEPENDENCIES)
    ET.SubElement(plugin, 'tracker').text = enmapbox.ISSUE_TRACKER
    ET.SubElement(plugin, 'repository').text = enmapbox.REPOSITORY
    ET.SubElement(plugin, 'tags').text = 'Remote Sensing, Raster'
    ET.SubElement(plugin, 'experimental').text = 'False'

    tree = ET.ElementTree(root)

    xml = ET.tostring(root)
    dom = minidom.parseString(xml)
    #<?xml version="1.0"?>
    #<?xml-stylesheet type="text/xsl" href="plugins.xsl" ?>
    #pi1 = dom.createProcessingInstruction('xml', 'version="1.0"')
    url_xsl = 'https://plugins.qgis.org/static/style/plugins.xsl'
    pi2 = dom.createProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="{}"'.format(url_xsl))

    dom.insertBefore(pi2, dom.firstChild)

    xmlRemote = dom.toprettyxml(encoding='utf-8').decode('utf-8')

    with open(PLUGIN_REPO_XML_REMOTE, 'w') as f:
        f.write(xmlRemote)

    import pathlib
    uri = pathlib.Path(path).as_uri()
    xmlLocal = re.sub(r'<download_url>.*</download_url>', r'<download_url>{}</download_url>'.format(uri), xmlRemote)
    with open(PLUGIN_REPO_XML_LOCAL, 'w') as f:
        f.write(xmlLocal)

   # tree.write(pathXML, encoding='utf-8', pretty_print=True, xml_declaration=True)
    #https://bitbucket.org/hu-geomatics/enmap-box/raw/HEAD/qgis_plugin_develop.xml

def uploadDeveloperPlugin():
    urlDownloads = 'https://api.bitbucket.org/2.0/repositories/hu-geomatics/enmap-box/downloads'
    assert os.path.isfile(PLUGIN_REPO_XML_REMOTE)

    if True:
        #copy to head
        bnXML = os.path.basename(PLUGIN_REPO_XML_REMOTE)
        pathNew = os.path.join(DIR_REPO, bnXML)
        print('Copy {}\n\tto {}'.format(PLUGIN_REPO_XML_REMOTE, pathNew))
        shutil.copy(PLUGIN_REPO_XML_REMOTE, pathNew)

        try:
            import git
            REPO = git.Repo(DIR_REPO)
            for diff in REPO.index.diff(None):
                if diff.a_path == bnXML:
                    REPO.git.execute(['git', 'commit', '-m', "'updated {}'".format(bnXML), bnXML])

            REPO.git.push()
        except Exception as ex:
            print(ex,file=sys.stderr)

    UPLOADS = {urlDownloads:[]}    #urlRepoXML:[PLUGIN_REPO_XML],
                #urlDownloads:[PLUGIN_REPO_XML]}
    doc = minidom.parse(PLUGIN_REPO_XML_REMOTE)
    for tag in doc.getElementsByTagName('file_name'):
        bn = tag.childNodes[0].nodeValue
        pathFile = os.path.join(DIR_DEPLOY, bn)
        assert os.path.isfile(pathFile)
        UPLOADS[urlDownloads].append(pathFile)

    for url, paths in UPLOADS.items():
        UPLOADS[url] = [p.replace('\\','/') for p in paths]

    skeyUsr = 'enmapbox-repo-username'
    settings = QSettings('HU Geomatics', 'enmabox-development-team')
    usr = settings.value(skeyUsr, '')
    pwd = ''
    auth = HTTPBasicAuth(usr, pwd)
    auth_success = False
    while not auth_success:
        try:
            if False: #print curl command(s) to be used in shell
                print('# CURL command(s) to upload enmapbox plugin build')
                for url, paths in UPLOADS.items():

                    cmd = ['curl']
                    if auth.username:
                        tmp = '-u {}'.format(auth.username)
                        if auth.password:
                            tmp += ':{}'.format(auth.password)
                        cmd.append(tmp)
                        del tmp
                    cmd.append('-X POST {}'.format(urlDownloads))
                    for f in paths:
                        cmd.append('-F files=@{}'.format(f))
                    cmd = ' '.join(cmd)

                    print(cmd)
                    print('# ')
            # files = {'file': ('test.csv', 'some,data,to,send\nanother,row,to,send\n')}

            if True: #upload

                session = requests.Session()
                session.auth = auth

                for url, paths in UPLOADS.items():
                    for path in paths:
                        print('Upload {} \n\t to {}...'.format(path, url))
                        #mimeType = mimetypes.MimeTypes().guess_type(path)[0]
                        #files = {'file': (open(path, 'rb'), mimeType)}
                        files = {'files':open(path, 'rb')}

                        r = session.post(url, auth=auth, files=files)
                        #r = requests.post(url, auth=auth, data = open(path, 'rb').read())
                        r.close()
                        assert isinstance(r, requests.models.Response)

                        for f in files.values():
                            if isinstance(f, tuple):
                                f = f[0]
                            f.close()

                        info = 'Status {} "{}"'.format(r.status_code, responses[r.status_code])
                        if r.status_code == 401:
                            print(info, file=sys.stderr)
                            from qgis.gui import QgsCredentialDialog
                            #from qgis.core import QgsCredentialsConsole

                            d = QgsCredentialDialog()
                            #d = QgsCredentialsConsole()
                            ok, usr, pwd = d.request(url, auth.username, auth.password)
                            if ok:
                                auth.username = usr
                                auth.password = pwd
                                session.auth = auth
                                continue
                            else:

                                raise Exception('Need credentials to access {}'.format(url))
                        elif not r.status_code in [200,201]:
                            print(info, file=sys.stderr)
                        else:
                            print(info)
                            auth_success = True

        except Exception as ex:
            pass

    if auth_success:
        settings.setValue(skeyUsr, session.auth.username)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Install testdata')
    parser.add_argument('-t', '--testdata',
                        required=False,
                        default=False,
                        help='Add enmapboxtestdata directory to plugin zip',
                        action='store_true')
    parser.add_argument('-q', '--qgisresources',
                        required=False,
                        default=False,
                        help='Add qgisresources directory to plugin zip. This is only required for test environments',
                        action='store_true')

    args = parser.parse_args()

    create_enmapbox_plugin(include_testdata=args.testdata, include_qgisresources=args.qgisresources)
    exit()

