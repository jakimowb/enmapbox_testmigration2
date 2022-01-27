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
*   it under the terms of the GNU General Public License as pclearublished by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.
                 *
*                                                                         *
***************************************************************************
"""
import argparse
import datetime
import fnmatch
import functools
import io
import itertools
import os
import pathlib
import re
import shutil
import site
import sys
import typing
# noinspection PyPep8Naming
import warnings
import configparser

site.addsitedir(pathlib.Path(__file__).parents[1])
import enmapbox
from enmapbox import DIR_REPO, __version__
from enmapbox.qgispluginsupport.qps.make.deploy import QGISMetadataFileWriter
from enmapbox.gui.utils import zipdir
from qgis.core import QgsFileUtils

########## Config Section
MAX_PLUGIN_SIZE = 10  # max plugin size in MB
CHECK_COMMITS = False

DIR_REPO = pathlib.Path(__file__).resolve().parents[1]
PATH_CONFIG_FILE = DIR_REPO / '.plugin.ini'

########## End of config section
assert PATH_CONFIG_FILE.is_file()


def scanfiles(root: typing.Union[str, pathlib.Path]) -> typing.Iterator[pathlib.Path]:
    """
    Recursively returns file paths in directory
    :param root: root directory to search in
    :return: pathlib.Path
    """

    for entry in os.scandir(root):
        if entry.is_dir(follow_symlinks=False):
            yield from scanfiles(entry.path)
        else:
            path = pathlib.Path(entry.path)
            if path.is_file():
                yield path


def fileRegex(root: str, pattern: str) -> typing.Pattern:
    """
    Create a regex to match a file pattern
    :param root:
    :param pattern:
    :return:
    """

    is_regex = False
    if pattern.startswith('rx:'):
        is_regex = True
        pattern = pattern[3:]

    if root:
        pattern = f'{root}/{pattern}'

    if is_regex:
        return re.compile(pattern)
    else:
        return re.compile(fnmatch.translate(pattern))


def create_enmapbox_plugin(include_testdata: bool = False, include_qgisresources: bool = False) -> pathlib.Path:
    assert (DIR_REPO / '.git').is_dir()

    DIR_DEPLOY = DIR_REPO / 'deploy'

    try:
        import git
        REPO = git.Repo(DIR_REPO)
        currentBranch = REPO.active_branch.name
        lastCommitSha = REPO.active_branch.commit.hexsha
        lastCommitDate = REPO.active_branch.commit.authored_datetime
        timestamp = re.split(r'[.+]', lastCommitDate.isoformat())[0]

    except Exception as ex:
        currentBranch = 'TEST'
        print(f'Unable to find git repo. Set currentBranch to "{currentBranch}"',
              file=sys.stderr)

        timestamp = re.split(r'[.+]', datetime.datetime.now().isoformat())[0]

    BUILD_NAME = '{}.{}.{}'.format(__version__, timestamp, currentBranch)
    BUILD_NAME = re.sub(r'[:-]', '', BUILD_NAME)
    BUILD_NAME = re.sub(r'[\\/]', '_', BUILD_NAME)
    PLUGIN_DIR = DIR_DEPLOY / 'enmapboxplugin'
    PLUGIN_ZIP = DIR_DEPLOY / 'enmapboxplugin.{}.zip'.format(BUILD_NAME)

    if PLUGIN_DIR.is_dir():
        shutil.rmtree(PLUGIN_DIR)
    os.makedirs(PLUGIN_DIR, exist_ok=True)

    PATH_METADATAFILE = PLUGIN_DIR / 'metadata.txt'

    config = configparser.ConfigParser()
    config.read(PATH_CONFIG_FILE)

    # set QGIS Metadata file values
    MD = QGISMetadataFileWriter()
    MD.mName = config['metadata']['name']
    MD.mDescription = config['metadata']['description']
    MD.mTags = config['metadata']['tags'].split()
    MD.mCategory = config['metadata']['category']
    MD.mAuthor = config['metadata']['authors'].split()
    MD.mIcon = config['metadata']['icon']
    MD.mHomepage = config['metadata']['homepage']
    MD.mAbout = enmapbox.ABOUT
    MD.mTracker = enmapbox.ISSUE_TRACKER
    MD.mRepository = enmapbox.REPOSITORY
    MD.mQgisMinimumVersion = enmapbox.MIN_VERSION_QGIS
    MD.mEmail = config['metadata']['email']
    MD.mHasProcessingProvider = True

    MD.mVersion = BUILD_NAME
    MD.writeMetadataTxt(PATH_METADATAFILE)

    # (re)-compile all enmapbox resource files
    from scripts.compile_resourcefiles import compileEnMAPBoxResources
    compileEnMAPBoxResources()

    # copy python and other resource files
    root = DIR_REPO.as_posix()
    ignore_rx = [fileRegex(None, p) for p in config['files'].get('ignore').split()]
    include_rx = [fileRegex(root, p) for p in config['files'].get('include').split()]
    exclude_rx = [fileRegex(root, p) for p in config['files'].get('exclude').split()]

    files = []
    for file in scanfiles(DIR_REPO):
        path = file.as_posix()
        ignored = False
        for rx in ignore_rx + exclude_rx:
            if rx.match(path):
                ignored = True
                break
        if ignored:
            continue
        for rx in include_rx:
            if rx.match(path):
                files.append(file)
                break

    for fileSrc in files:
        assert fileSrc.is_file()
        fileDst = PLUGIN_DIR / fileSrc.relative_to(DIR_REPO)
        os.makedirs(fileDst.parent, exist_ok=True)
        shutil.copy(fileSrc, fileDst.parent)

    # update metadata version

    f = open(DIR_REPO / 'enmapbox' / '__init__.py')
    lines = f.read()
    f.close()
    lines = re.sub(r'(__version__\W*=\W*)([^\n]+)', r'__version__ = "{}"\n'.format(BUILD_NAME), lines)
    f = open(PLUGIN_DIR / 'enmapbox' / '__init__.py', 'w')
    f.write(lines)
    f.flush()
    f.close()

    # include test data into test versions
    if include_testdata:
        if os.path.isdir(enmapbox.DIR_EXAMPLEDATA):
            DEST = PLUGIN_DIR / 'enmapbox' / 'exampledata'
            shutil.copytree(enmapbox.DIR_EXAMPLEDATA, DEST, dirs_exist_ok=True)

    if include_qgisresources and not re.search(currentBranch, 'master', re.I):
        qgisresources = pathlib.Path(DIR_REPO) / 'qgisresources'
        shutil.copytree(qgisresources, PLUGIN_DIR / 'qgisresources')

    createCHANGELOG(PLUGIN_DIR)

    # 5. create a zip
    print('Create zipfile...')
    zipdir(PLUGIN_DIR, PLUGIN_ZIP)

    pluginSize: int = os.stat(PLUGIN_ZIP).st_size

    if pluginSize > MAX_PLUGIN_SIZE * 2 ** 20:
        msg = f'{PLUGIN_ZIP.name} ({QgsFileUtils.representFileSize(pluginSize)}) ' + \
              f'exceeds maximum plugin size ({MAX_PLUGIN_SIZE} MB)'

        if re.search(currentBranch, 'master', re.I):
            warnings.warn(msg, Warning, stacklevel=2)
        else:
            print(msg, file=sys.stderr)
    else:
        print(f'Plugin Size ({QgsFileUtils.representFileSize(pluginSize)}) ok.')

    # 7. install the zip file into the local QGIS instance. You will need to restart QGIS!
    if True:
        info = []
        info.append('\n### To update/install the EnMAP-Box, run this command on your QGIS Python shell:\n')
        info.append('from pyplugin_installer.installer import pluginInstaller')
        info.append('pluginInstaller.installFromZipFile(r"{}")'.format(PLUGIN_ZIP))
        info.append('#### Close (and restart manually)\n')
        # print('iface.mainWindow().close()\n')
        info.append('QProcess.startDetached(QgsApplication.arguments()[0], [])')
        info.append('QgsApplication.quit()\n')
        info.append('## press ENTER\n')

        print('\n'.join(info))

    print(f'Finished building {BUILD_NAME}')
    return PLUGIN_ZIP


def createCHANGELOG(dirPlugin):
    """
    Reads the CHANGELOG.rst and creates the deploy/CHANGELOG (without extension!) for the QGIS Plugin Manager
    :return:
    """

    pathMD = os.path.join(DIR_REPO, 'CHANGELOG.rst')
    pathCL = os.path.join(dirPlugin, 'CHANGELOG')

    os.makedirs(os.path.dirname(pathCL), exist_ok=True)
    assert os.path.isfile(pathMD)
    #    import sphinx.transforms
    import docutils.core

    overrides = {'stylesheet': None,
                 'embed_stylesheet': False,
                 'output_encoding': 'utf-8',
                 }

    buffer = io.StringIO()
    html = docutils.core.publish_file(
        source_path=pathMD,
        writer_name='html5',
        destination=buffer,
        settings_overrides=overrides)

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
        with open(pathCL + '.html', 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_cleaned))
    s = ""


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

    path = create_enmapbox_plugin(include_testdata=args.testdata, include_qgisresources=args.qgisresources)

    if re.search(r'\.master\.', path.name):
        message = '\nVery important checklist. Do not remove!!!' \
                  '\nChecklist for release:' \
                  '\n  Run scripts\\runtests.bat (win) or scripts/runtests.sh (linux/mac)' \
                  '\n  Change log up-to-date?' \
                  '\n  Processing algo documentation up-to-date (run create_processing_rst)' \
                  '\n  Run weblink checker (in doc folder make linkcheck)' \
                  '\n  Check if box runs without optional dependencies (see tests/non-blocking-dependencies/readme.txt).' \
                  '\n  Version number increased? (enmapbox/__init__.py -> __version__)' \
                  '\n  QGIS Min-Version? (enmapbox/__init__.py -> MIN_VERSION_QGIS)' \
                  '\n  ZIP containing branch (i.e. master) information (GIT installed)?' \
                  '\n  Install ZIP and quick-test under the latest supported QGIS versions and OS, e.g.:' \
                  '\n      Andreas: latest Windows Conda QGIS' \
                  '\n      Fabian: Linux QGIS used in Greifswald-Teaching' \
                  '\n      Benjamin: latest OSGeo4W (maybe also MacOS?) QGIS' \
                  '\n  Plugin promotion (Slack, Email, ...)' \
                  '\n      RTD' \
                  '\n      Email an Saskia: update auf enmap.org (enmap news + enmap news letter)' \
                  '\n      Email an enmap_wiss@gfz-potsdam.de' \
                  '\n      Email an Ettore: reach out to PRISMA community' \
                  '\n      EOL Slack + EnMAP Slack' \
                  '\n      EOL Twitter'

        print(message)

    exit()
