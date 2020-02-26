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
import os, sys
from enmapbox.gui.utils import file_search

from requests.auth import HTTPBasicAuth
from http.client import responses
import xml.etree.ElementTree as ET
from xml.dom import minidom
from qgis.PyQt.QtCore import *

#from pb_tool import pb_tool # install with: pip install pb_tool

import enmapbox
from enmapbox import DIR_REPO, __version__
import git

CHECK_COMMITS = False
INCLUDE_TESTDATA = False  #includes the testdata folder for none-master versions


########## Config Section


########## End of config section
REPO = git.Repo(DIR_REPO)
pathCfg = jp(DIR_REPO, 'pb_tool.cfg')
CFG = pb_tool.get_config(pathCfg)
PLUGIN_NAME = CFG.get('plugin', 'name')


currentBranch = REPO.active_branch.name

if currentBranch == 'master':
    INCLUDE_TESTDATA = False

timestamp = ''.join(np.datetime64(datetime.datetime.now()).astype(str).split(':')[0:-1]).replace('-','')
buildID = '{}.{}.{}'.format(re.search(r'(\.?[^.]*){2}', __version__).group()
                            , timestamp,
                            re.sub(r'[\\/]','_', currentBranch))

DIR_DEPLOY = jp(DIR_REPO, 'deploy')

PLUGIN_REPO_XML_REMOTE = os.path.join(DIR_DEPLOY, 'qgis_plugin_develop.xml')
PLUGIN_REPO_XML_LOCAL  = os.path.join(DIR_DEPLOY, 'qgis_plugin_develop_local.xml')
URL_DOWNLOADS = r'https://bitbucket.org/hu-geomatics/enmap-box/downloads'
URL_WIKI = r'https://api.bitbucket.org/2.0/repositories/hu-geomatics/enmap-box/wiki/src'


def remove_shortcutVisibleInContextMenu(rootDir):

    uiFiles = file_search(rootDir, '*.ui', recursive=True)

    regex = re.compile(r'<property name="shortcutVisibleInContextMenu">[^<]*<bool>true</bool>[^<]*</property>', re.MULTILINE)


    for p in uiFiles:
        assert isinstance(p, str)
        assert os.path.isfile(p)

        with open(p, encoding='utf-8') as f:
            xml = f.read()

        if 'shortcutVisibleInContextMenu' in xml:
            print('remove "shortcutVisibleInContextMenu" properties from {}'.format(p))
            xml = regex.sub('', xml)

            with open(p, 'w', encoding='utf-8') as f:
                f.write(xml)


def rm(p):
    """
    Remove files or directory 'p'
    :param p: path of file or directory to be removed.
    """
    if os.path.isfile(p):
        os.remove(p)
    elif os.path.isdir(p):
        shutil.rmtree(p)


def cleanDir(d):
    """
    Remove content from directory 'd'
    :param d: directory to be cleaned.
    """
    assert os.path.isdir(d)
    for root, dirs, files in os.walk(d):
        for p in dirs + files: rm(jp(root, p))
        break



def mkDir(d, delete=False):
    """
    Make directory.
    :param d: path of directory to be created
    :param delete: set on True to delete the directory contents, in case the directory already existed.
    """
    if delete and os.path.isdir(d):
        cleanDir(d)
    if not os.path.isdir(d):
        os.makedirs(d)


def create_enmapbox_plugin():

    # local pb_tool configuration file.
    pathCfg = jp(DIR_REPO, 'pb_tool.cfg')
    cfg = pb_tool.get_config(pathCfg)
    cdir = os.path.dirname(pathCfg)
    pluginname = cfg.get('plugin', 'name')
    dirPlugin = jp(DIR_DEPLOY, pluginname)
    os.chdir(cdir)

    mkDir(DIR_DEPLOY)

    if os.path.isdir(dirPlugin):
        print('Remove old build folder...')
        shutil.rmtree(dirPlugin, ignore_errors=True)

    # required to choose andy DIR_DEPLOY of choice
    # issue tracker: https://github.com/g-sherman/plugin_build_tool/issues/4

    if True:
        # 1. clean an existing directory = the enmapboxplugin folder
        if os.path.isdir(DIR_DEPLOY):
            try:
                pb_tool.clean_deployment(ask_first=False)
            except:
                pass




        if currentBranch not in ["develop", "master"]:
            print('Skipped automatic version update because current branch is not "develop" or "master". ')
        else:
            # 2. set the version to all relevant files
            # r = REPO.git.execute(['git','diff', '--exit-code']).split()
            diffs = [r for r in REPO.index.diff(None) if 'deploy.py' not in str(r)]
            if CHECK_COMMITS and len(diffs) > 0:
                # there are diffs. we need to commit them first.
                # This should not be done automatically, as each commit should contain a proper commit message
                raise Exception('Please commit all changes first.')

        # 2. Compile. Basically call pyrcc to create the resources.rc file
        # I don't know how to call this from pure python

        #try:
        #    pb_tool.compile_files(cfg)
        #except Exception as ex:
        #    print('Failed to compile resources')
        #    print(ex)

        from scripts.compileresourcefiles import compileEnMAPBoxResources
        compileEnMAPBoxResources()

        # 3. Deploy = write the data to the new enmapboxplugin folder
        pb_tool.deploy_files(pathCfg, DIR_DEPLOY, 'default', quick=True, confirm=False)

        if True:
            remove_shortcutVisibleInContextMenu(DIR_DEPLOY)

        # 4. As long as we can not specify in the pb_tool.cfg which file types are not to deploy,
        # we need to remove them afterwards.
        # issue: https://github.com/g-sherman/plugin_build_tool/issues/5
        print('Remove files...')

        if True:
            # delete help folder
            shutil.rmtree(os.path.join(dirPlugin, *['help']), ignore_errors=True)
        for f in file_search(DIR_DEPLOY, re.compile('(svg|pyc)$'), recursive=True):
            os.remove(f)

    #update metadata version
    if True:
        pathMetadata = jp(dirPlugin, 'metadata.txt')
        # update version number in metadata
        f = open(pathMetadata)
        lines = f.readlines()
        f.close()
        lines = re.sub('version=.*\n', 'version={}\n'.format(buildID), ''.join(lines))
        f = open(pathMetadata, 'w')
        f.write(lines)
        f.flush()
        f.close()

        pathPackageInit = jp(dirPlugin, *['enmapbox', '__init__.py'])
        f = open(pathPackageInit)
        lines = f.read()
        f.close()
        lines = re.sub(r'(__version__\W*=\W*)([^\n]+)', r'__version__ = "{}"\n'.format(buildID), lines)
        f = open(pathPackageInit, 'w')
        f.write(lines)
        f.flush()
        f.close()



    pluginname = cfg.get('plugin', 'name')
    pathZip = jp(DIR_DEPLOY, '{}.{}.zip'.format(pluginname, buildID))
    dirPlugin = jp(DIR_DEPLOY, pluginname)

    # include test data into test versions
    if INCLUDE_TESTDATA and not re.search(currentBranch, 'master', re.I):
        if os.path.isdir(enmapbox.DIR_TESTDATA):

            shutil.copytree(enmapbox.DIR_TESTDATA, os.path.join(dirPlugin, os.path.basename(enmapbox.DIR_TESTDATA)))
        s = ""

    createCHANGELOG(dirPlugin)

    # 5. create a zip
    print('Create zipfile...')
    from enmapbox.gui.utils import zipdir

    zipdir(dirPlugin, pathZip)

    # 6. Update XML repositories
    updateRepositoryXML()


    # 7. install the zip file into the local QGIS instance. You will need to restart QGIS!
    if True:
        info = []
        info.append('\n### To update/install the EnMAP-Box, run this command on your QGIS Python shell:\n')
        info.append('from pyplugin_installer.installer import pluginInstaller')
        info.append('pluginInstaller.installFromZipFile(r"{}")'.format(pathZip))
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

    # 1. update deploy/EnMAP-Box and
    #    create deploy/EnMAP-Box.<version>.<branch>.zip
    import getopt
    try:
        print(sys.argv)
        opts, args = getopt.getopt(sys.argv[1:], "t")
    except getopt.GetoptError as err:
        print(err)

    for o, a in opts:
        if o == '-t':
            INCLUDE_TESTDATA = True

    create_enmapbox_plugin()
    exit()

