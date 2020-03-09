# -*- coding: utf-8 -*-

# enpt_enmapboxapp, A QGIS EnMAPBox plugin providing a GUI for the EnMAP processing tools (EnPT)
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module provides a QGIS EnMAPBox GUI for the EnMAP processing tools (EnPT)."""

import os
from os.path import expanduser
from datetime import date
from subprocess import Popen, PIPE, check_output, CalledProcessError
from threading import Thread
from queue import Queue
from multiprocessing import cpu_count
from glob import glob
import psutil

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMenu, QAction, QDialog, QHBoxLayout, QLabel, QPushButton
from enmapbox.gui.applications import EnMAPBoxApplication
from qgis.core import \
    (QgsProcessingAlgorithm,
     QgsProcessingParameterFile,
     QgsProcessingParameterNumber,
     QgsProcessingParameterFolderDestination,
     QgsProcessingParameterBoolean,
     QgsProcessingParameterString,
     QgsProcessingContext,
     QgsProcessingFeedback,
     NULL
     )
from .version import __version__


VERSION = __version__
LICENSE = 'GNU GPL-3'
APP_DIR = os.path.dirname(__file__)

APP_NAME = 'EnPT EnMAPBox App'


class EnPTEnMAPBoxApp(EnMAPBoxApplication):
    """
    This Class inherits from an EnMAPBoxApplication
    """

    def __init__(self, enmapBox, parent=None):
        super(EnPTEnMAPBoxApp, self).__init__(enmapBox, parent=parent)

        self.name = APP_NAME
        self.version = VERSION
        self.licence = LICENSE

    def icon(self):
        """
        This function returns the QIcon of your Application
        :return: QIcon()
        """
        return QIcon(os.path.join(APP_DIR, 'icon.png'))

    def menu(self, appMenu):
        """
        Returns a QMenu that will be added to the parent `appMenu`
        :param appMenu:
        :return: QMenu
        """
        assert isinstance(appMenu, QMenu)
        """
        Specify menu, submenus and actions that become accessible from the EnMAP-Box GUI
        :return: the QMenu or QAction to be added to the "Applications" menu.
        """

        # this way you can add your QMenu/QAction to an other menu entry, e.g. 'Tools'
        # appMenu = self.enmapbox.menu('Tools')

        menu = appMenu.addMenu('EnPT (EnMAP Processing Tools)')
        menu.setIcon(self.icon())

        # add a QAction that starts a process of your application.
        # In this case it will open your GUI.
        a = menu.addAction('Start EnPT GUI')
        assert isinstance(a, QAction)
        a.triggered.connect(self.startGUI)
        appMenu.addMenu(menu)

        return menu

    def processingAlgorithms(self):
        """
        This function returns the QGIS Processing Framework GeoAlgorithms specified by your application
        :return: [list-of-GeoAlgorithms]
        """

        return [EnPTAlgorithm(), ]

    def startGUI(self):
        """
        Opens a GUI
        :param args:
        :return:
        """

        w = ExampleAppGUI(self.enmapbox.ui)
        w.show()


class ExampleAppGUI(QDialog):
    """
    A minimal graphical user interface
    """

    def __init__(self, parent=None):
        super(ExampleAppGUI, self).__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(os.path.join(APP_DIR, 'icon.png')))
        self.setMinimumWidth(400)
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('This is only a placeholder for a later QT version of the EnPT GUI.\n'
                                'Please use the EnMAP processing tool algorithm in the processing toolbox.'))
        self.btn = QPushButton('OK!')

        # clicking the button will print "Hello World" to the python CLI
        self.btn.clicked.connect(lambda: print('Pressing the OK button does NOT start EnPT!'))
        layout.addWidget(self.btn)
        self.setMinimumSize(self.sizeHint())


def printDictionary(parameters):
    """
    An algorithm that just prints the provided parameter dictionary
    """
    print('Parameters:')
    for key, parameter in parameters.items():
        print('{} = {}'.format(key, parameter))


class EnPTAlgorithm(QgsProcessingAlgorithm):
    # NOTE: The parameter assignments made here follow the parameter names in enpt/options/options_schema.py

    # Input parameters
    P_json_config = 'json_config'
    P_anaconda_root = 'anaconda_root'
    P_CPUs = 'CPUs'
    P_path_l1b_enmap_image = 'path_l1b_enmap_image'
    P_path_l1b_enmap_image_gapfill = 'path_l1b_enmap_image_gapfill'
    P_path_dem = 'path_dem'
    P_average_elevation = 'average_elevation'
    P_output_dir = 'output_dir'
    P_working_dir = 'working_dir'
    P_n_lines_to_append = 'n_lines_to_append'
    P_disable_progress_bars = 'disable_progress_bars'
    P_path_earthSunDist = 'path_earthSunDist'
    P_path_solar_irr = 'path_solar_irr'
    P_scale_factor_toa_ref = 'scale_factor_toa_ref'
    P_enable_keystone_correction = 'enable_keystone_correction'
    P_enable_vnir_swir_coreg = 'enable_vnir_swir_coreg'
    P_path_reference_image = 'path_reference_image'
    P_enable_ac = 'enable_ac'
    P_auto_download_ecmwf = 'auto_download_ecmwf'
    P_enable_ice_retrieval = 'enable_ice_retrieval'
    P_enable_cloud_screening = 'enable_cloud_screening'
    P_scale_factor_boa_ref = 'scale_factor_boa_ref'
    P_run_smile_P = 'run_smile_P'
    P_run_deadpix_P = 'run_deadpix_P'
    P_deadpix_P_algorithm = 'deadpix_P_algorithm'
    P_deadpix_P_interp_spectral = 'deadpix_P_interp_spectral'
    P_deadpix_P_interp_spatial = 'deadpix_P_interp_spatial'
    P_ortho_resampAlg = 'ortho_resampAlg'

    # # Output parameters
    P_OUTPUT_RASTER = 'outraster'
    # P_OUTPUT_VECTOR = 'outvector'
    # P_OUTPUT_FILE = 'outfile'
    P_OUTPUT_FOLDER = 'outfolder'

    def group(self):
        return 'Pre-Processing'

    def groupId(self):
        return 'PreProcessing'

    def name(self):
        return 'EnPTAlgorithm'

    def displayName(self):
        return 'EnMAP processing tool algorithm (v%s)' % __version__

    def createInstance(self, *args, **kwargs):
        return type(self)()

    @staticmethod
    def _get_default_anaconda_root():
        if os.name == 'nt':
            return 'C:\\ProgramData\\Anaconda3'
        else:
            return ''  # FIXME is there a default location in Linux/OSX?

    @staticmethod
    def _get_default_output_dir():
        userhomedir = expanduser('~')

        default_enpt_dir = \
            os.path.join(userhomedir, 'Documents', 'EnPT', 'Output') if os.name == 'nt' else\
            os.path.join(userhomedir, 'EnPT', 'Output')

        outdir_nocounter = os.path.join(default_enpt_dir, date.today().strftime('%Y%m%d'))

        counter = 1
        while os.path.isdir('%s__%s' % (outdir_nocounter, counter)):
            counter += 1

        return '%s__%s' % (outdir_nocounter, counter)

    def initAlgorithm(self, configuration=None):
        self.addParameter(QgsProcessingParameterFile(
            name=self.P_json_config, description='Configuration JSON template file',
            behavior=QgsProcessingParameterFile.File, extension='json',
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_anaconda_root,
            description='Anaconda root directory (which contains the EnPT Python environment in a subdirectory)',
            behavior=QgsProcessingParameterFile.Folder,
            defaultValue=self._get_default_anaconda_root(),
            optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            name=self.P_CPUs,
            description='Number of CPU cores to be used for processing',
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=cpu_count(), minValue=0, maxValue=cpu_count(),
            optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_path_l1b_enmap_image,
            description='L1B EnMAP image (zip-archive or root directory)'))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_path_l1b_enmap_image_gapfill,
            description='Adjacent EnMAP L1B image to be used for gap-filling (zip-archive or root directory)',
            optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_path_dem,
            description='Input path of digital elevation model in map or sensor geometry; GDAL compatible file '
                        'format \n(must cover the EnMAP L1B data completely if given in map geometry or must have the '
                        'same \npixel dimensions like the EnMAP L1B data if given in sensor geometry)',
            optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            name=self.P_average_elevation,
            description='Average elevation in meters above sea level \n'
                        '(may be provided if no DEM is available and ignored if DEM is given)',
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=0,
            optional=True))

        self.addParameter(QgsProcessingParameterFolderDestination(
            name=self.P_output_dir,
            description='Output directory where processed data and log files are saved',
            defaultValue=self._get_default_output_dir(),
            optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_working_dir,
            description='Directory to be used for temporary files',
            behavior=QgsProcessingParameterFile.Folder,
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            name=self.P_n_lines_to_append,
            description='Number of lines to be added to the main image [if not given, use the whole imgap]',
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_disable_progress_bars,
            description='Disable all progress bars during processing',
            defaultValue=True,
            optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_path_earthSunDist,
            description='Input path of the earth sun distance model',
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_path_solar_irr,
            description='Input path of the solar irradiance model',
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            name=self.P_scale_factor_toa_ref,
            description='Scale factor to be applied to TOA reflectance result',
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=10000,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_enable_keystone_correction,
            description='Keystone correction',
            defaultValue=False,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_enable_vnir_swir_coreg,
            description='VNIR/SWIR co-registration',
            defaultValue=False,
            optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_path_reference_image,
            description='Reference image for co-registration.',
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_enable_ac,
            description='Enable atmospheric correction using SICOR algorithm',
            defaultValue=True,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_auto_download_ecmwf,
            description='Automatically download ECMWF data for atmospheric correction',
            defaultValue=False,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_enable_ice_retrieval,
            description='Enable ice retrieval (increases accuracy of water vapour retrieval)',
            defaultValue=True,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_enable_cloud_screening,
            description='Cloud screening during atmospheric correction',
            defaultValue=False,
            optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            name=self.P_scale_factor_boa_ref,
            description='Scale factor to be applied to BOA reflectance result',
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=10000,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_run_smile_P,
            description='Smile detection and correction (provider smile coefficients are ignored)',
            defaultValue=False,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_run_deadpix_P,
            description='Dead pixel correction',
            defaultValue=True,
            optional=True))

        self.addParameter(QgsProcessingParameterString(
            name=self.P_deadpix_P_algorithm,
            description="Algorithm for dead pixel correction ('spectral' or 'spatial')",
            defaultValue='spectral',
            multiLine=False,
            optional=True))

        self.addParameter(QgsProcessingParameterString(
            name=self.P_deadpix_P_interp_spectral,
            description="Spectral interpolation algorithm to be used during dead pixel correction "
                        "('linear', 'bilinear', 'cubic', 'spline')",
            defaultValue='linear',
            multiLine=False,
            optional=True))

        self.addParameter(QgsProcessingParameterString(
            name=self.P_deadpix_P_interp_spatial,
            description="Spatial interpolation algorithm to be used during dead pixel correction "
                        "('linear', 'bilinear', 'cubic', 'spline')",
            defaultValue='linear',
            multiLine=False,
            optional=True))

        self.addParameter(QgsProcessingParameterString(
            name=self.P_ortho_resampAlg,
            description="Ortho-rectification resampling algorithm ('nearest', 'bilinear', 'gauss')",
            defaultValue='bilinear',
            multiLine=False,
            optional=True))

    @staticmethod
    def _run_cmd(cmd, qgis_feedback=None, **kwargs):
        """Execute external command and get its stdout, exitcode and stderr.

        Code based on: https://stackoverflow.com/a/31867499

        :param cmd: a normal shell command including parameters
        """
        def reader(pipe, queue):
            try:
                with pipe:
                    for line in iter(pipe.readline, b''):
                        queue.put((pipe, line))
            finally:
                queue.put(None)

        process = Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1, shell=True, **kwargs)
        q = Queue()
        Thread(target=reader, args=[process.stdout, q]).start()
        Thread(target=reader, args=[process.stderr, q]).start()

        # for _ in range(2):
        for source, line in iter(q.get, None):
            if qgis_feedback.isCanceled():
                # qgis_feedback.reportError('CANCELED')

                proc2kill = psutil.Process(process.pid)
                for proc in proc2kill.children(recursive=True):
                    proc.kill()
                proc2kill.kill()

                raise KeyboardInterrupt

            linestr = line.decode('latin-1').rstrip()
            # print("%s: %s" % (source, linestr))
            if source.name == 3:
                qgis_feedback.pushInfo(linestr)
            if source.name == 4:
                qgis_feedback.reportError(linestr)

        exitcode = process.poll()

        return exitcode

    @staticmethod
    def _locate_EnPT_Anaconda_environment(user_root):
        anaconda_rootdir = None

        if user_root and os.path.exists(user_root):
            anaconda_rootdir = user_root

        elif 'ANACONDA_ROOT' in os.environ and os.path.exists(os.environ['ANACONDA_ROOT']):
            anaconda_rootdir = os.environ['ANACONDA_ROOT']

        else:
            possPaths = \
                ['C:\\ProgramData\\Anaconda3',
                 'C:\\Users\\%s\\Anaconda3' % os.getenv('username')
                 ] if os.name == 'nt' else \
                []

            for rootDir in possPaths:
                if os.path.exists(rootDir):
                    anaconda_rootdir = rootDir

        if not anaconda_rootdir and user_root or 'ANACONDA_ROOT' in os.environ:
            raise NotADirectoryError("No valid Anaconda root directory given - "
                                     "neither via the GUI, nor via the 'ANACONDA_ROOT' environment variable.")

        # set ENPT_PYENV_ACTIVATION environment variable
        os.environ['ENPT_PYENV_ACTIVATION'] = os.path.join(anaconda_rootdir, 'Scripts', 'activate.bat')

        return anaconda_rootdir

    @staticmethod
    def _locate_enpt_run_script():
        try:
            if os.name == 'nt':
                # Windows
                return check_output('where enpt_run_cmd.bat', shell=True).decode('UTF-8').strip()
                # return "D:\\Daten\\Code\\python\\enpt_enmapboxapp\\bin\\enpt_run_cmd.bat"
            else:
                # Linux / OSX
                return check_output('which enpt_run_cmd.sh', shell=True).decode('UTF-8').strip()
                # return 'enpt_run_cmd.sh '

        except CalledProcessError:
            raise EnvironmentError('The EnPT run script could not be found. Please make sure, that enpt_enmapboxapp '
                                   'is correctly installed into your QGIS Python environment.')

    @staticmethod
    def _prepare_enpt_environment():
        os.environ['PYTHONUNBUFFERED'] = '1'

        enpt_env = os.environ.copy()
        enpt_env["PATH"] = ';'.join([i for i in enpt_env["PATH"].split(';') if 'OSGEO' not in i])  # actually not needed
        if "PYTHONHOME" in enpt_env.keys():
            del enpt_env["PYTHONHOME"]
        if "PYTHONPATH" in enpt_env.keys():
            del enpt_env["PYTHONPATH"]

        # FIXME is this needed?
        enpt_env['IPYTHONENABLE'] = 'True'
        enpt_env['PROMPT'] = '$P$G'
        enpt_env['PYTHONDONTWRITEBYTECODE'] = '1'
        enpt_env['PYTHONIOENCODING'] = 'UTF-8'
        enpt_env['TEAMCITY_VERSION'] = 'LOCAL'
        enpt_env['O4W_QT_DOC'] = 'C:/OSGEO4~3/apps/Qt5/doc'
        if 'SESSIONNAME' in enpt_env.keys():
            del enpt_env['SESSIONNAME']

        # import pprint
        # s = pprint.pformat(enpt_env)
        # with open('D:\\env.json', 'w') as fp:
        #     fp.write(s)

        return enpt_env

    def processAlgorithm(self, parameters, context, feedback):
        assert isinstance(parameters, dict)
        assert isinstance(context, QgsProcessingContext)
        assert isinstance(feedback, QgsProcessingFeedback)

        anaconda_root = self._locate_EnPT_Anaconda_environment(parameters[self.P_anaconda_root])
        feedback.pushInfo('Found Anaconda installation at %s.' % anaconda_root)

        # remove all parameters not to be forwarded to the EnPT CLI
        parameters = {k: v for k, v in parameters.items() if k not in ['anaconda_root']}

        # print parameters and console call to log
        # for key in sorted(parameters):
        #     feedback.pushInfo('{} = {}'.format(key, repr(parameters[key])))
        keyval_str = ' '.join(['--{} {}'.format(key, parameters[key])
                               for key in sorted(parameters)
                               if parameters[key] not in [None, NULL, 'NULL', '']])
        print(parameters)
        print(keyval_str + '\n\n')
        feedback.pushInfo("\nCalling EnPT with the following command:\n"
                          "python enpt_cli.py %s\n\n" % keyval_str)

        # prepare environment for subprocess
        enpt_env = self._prepare_enpt_environment()
        path_enpt_runscript = self._locate_enpt_run_script()

        # run EnPT in subprocess that activates the EnPT Anaconda environment
        feedback.pushDebugInfo('Using %s to start EnPT.' % path_enpt_runscript)
        feedback.pushInfo("The log messages of the EnMAP processing tool are written to the *.log file "
                          "in the specified output folder.")

        self._run_cmd("%s %s" % (path_enpt_runscript, keyval_str),
                      qgis_feedback=feedback,
                      env=enpt_env)

        # list output dir
        outdir = parameters['output_dir']
        outraster_matches = glob(os.path.join(outdir, '*', '*SPECTRAL_IMAGE.GEOTIFF'))
        outraster = outraster_matches[0] if len(outraster_matches) > 0 else None

        feedback.pushInfo("The output folder '%s' contains:\n" % outdir)
        feedback.pushCommandInfo('\n'.join([os.path.basename(f) for f in os.listdir(outdir)]) + '\n')

        if outraster:
            subdir = os.path.dirname(outraster_matches[0])
            feedback.pushInfo("...where the folder '%s' contains:\n" % os.path.dirname(subdir))
            feedback.pushCommandInfo('\n'.join([os.path.basename(f) for f in os.listdir(subdir)]) + '\n')

        # return outputs
        return {
            self.P_OUTPUT_RASTER: outraster,
            # self.P_OUTPUT_VECTOR: parameters[self.P_OUTPUT_RASTER],
            # self.P_OUTPUT_FILE: parameters[self.P_OUTPUT_RASTER],
            self.P_OUTPUT_FOLDER: outdir
        }

    @staticmethod
    def shortHelpString(*args, **kwargs):
        """Example:

        '<p>Here comes the HTML documentation.</p>' \
        '<h3>With Headers...</h3>' \
        '<p>and Hyperlinks: <a href="www.google.de">Google</a></p>'

        :param args:
        :param kwargs:
        """

        text = '<p>General information about this EnMAP box app can be found ' \
               '<a href="http://enmap.gitext.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp/doc/">here</a>.</p>' \
               '<p>Type <i>python enpt_cli.py -h</i> into a shell to get further information about individual ' \
               'parameters.</p>'

        return text

    def helpString(self):
        return self.shortHelpString()

    @staticmethod
    def helpUrl(*args, **kwargs):
        return 'http://enmap.gitext.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp/doc/'


if __name__ == '__main__':

    from enmapbox.testing import initQgisApplication

    # this will initialize the QApplication/QgsApplication which runs in the background
    # see https://qgis.org/api/classQgsApplication.html for details
    qgsApp = initQgisApplication()

    if False:  # test GUI without EnMAP-Box
        w = ExampleAppGUI()
        w.show()

    else:
        from enmapbox.gui.enmapboxgui import EnMAPBox

        EB = EnMAPBox(None)
        EB.run()
        EB.openExampleData(mapWindows=2)
        app = EnPTEnMAPBoxApp(EB)
        EB.addApplication(app)

    # start the GUI thread
    qgsApp.exec_()
