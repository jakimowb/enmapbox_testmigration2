# -*- coding: utf-8 -*-

"""
***************************************************************************
    enpt_enmapboxapp/enpt_enmapboxapp.py

    This module provides a QGIS EnMAPBox GUI for the EnMAP processing tools (EnPT).
    ---------------------
    Date                 : Juli 2018
    Copyright            : (C) 2018 by Daniel Scheffler
    Email                : daniel.scheffler@gfz-potsdam.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import os
import shlex
from subprocess import Popen, PIPE
from multiprocessing import cpu_count

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMenu, QAction, QWidget, QHBoxLayout, QLabel, QPushButton
from enmapbox.gui.applications import EnMAPBoxApplication
from qgis.core import *

VERSION = '0.0.1'
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

        menu = appMenu.addMenu('My Example App')
        menu.setIcon(self.icon())

        # add a QAction that starts a process of your application.
        # In this case it will open your GUI.
        a = menu.addAction('Show ExampleApp GUI')
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


class ExampleAppGUI(QWidget):
    """
    A minimal graphical user interface
    """

    def __init__(self, parent=None):
        super(ExampleAppGUI, self).__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(os.path.join(APP_DIR, 'icon.png')))
        self.setMinimumWidth(400)
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Hello World'))
        self.btn = QPushButton('Click me')

        # clicking the button will print "Hello World" to the python CLI
        self.btn.clicked.connect(lambda: print('Hello World'))
        layout.addWidget(self.btn)
        self.setLayout(layout)


def printDictionary(parameters):
    """
    An algorithm that just prints the provided parameter dictionary
    """
    print('Parameters:')
    for key, parameter in parameters.items():
        print('{} = {}'.format(key, parameter))


class EnPTAlgorithm(QgsProcessingAlgorithm):
    P_json_config = 'json_config'
    P_CPUs = 'CPUs'
    P_path_l1b_enmap_image = 'path_l1b_enmap_image'
    P_path_l1b_enmap_image_gapfill = 'path_l1b_enmap_image_gapfill'
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
    P_sicor_cache_dir = 'sicor_cache_dir'
    P_auto_download_ecmwf = 'auto_download_ecmwf'
    P_enable_cloud_screening = 'enable_cloud_screening'
    P_scale_factor_boa_ref = 'scale_factor_boa_ref'
    P_run_smile_P = 'run_smile_P'
    P_run_deadpix_P = 'run_deadpix_P'
    P_deadpix_P_algorithm = 'deadpix_P_algorithm'
    P_deadpix_P_interp = 'deadpix_P_interp'
    P_ortho_resampAlg = 'ortho_resampAlg'

    @staticmethod
    def group():
        return APP_NAME

    @staticmethod
    def name():
        return 'EnPTAlgorithm'

    @staticmethod
    def displayName():
        return 'EnMAP processing tools algorithm'

    def createInstance(self, *args, **kwargs):
        return type(self)()

    def initAlgorithm(self, configuration=None):
        self.addParameter(QgsProcessingParameterFile(
            name=self.P_json_config, description='Configuration JSON template file',
            behavior=QgsProcessingParameterFile.File, extension='json',
            defaultValue=None, optional=True))

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

        self.addParameter(QgsProcessingParameterFolderDestination(
            name=self.P_output_dir,
            description='Output directory where processed data and log files are saved',
            defaultValue=None, optional=True))

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_working_dir,
            description='Output directory where processed data and log files are saved',
            behavior=QgsProcessingParameterFile.Folder,
            defaultValue=None, optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            name=self.P_n_lines_to_append,
            description='Number of lines to be added to the main image [if not given, use the whole imgap]',
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_disable_progress_bars,
            description='Disable all progress bars during processing',
            defaultValue=False,
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

        self.addParameter(QgsProcessingParameterFile(
            name=self.P_sicor_cache_dir,
            description='SICOR cache directory',
            behavior=QgsProcessingParameterFile.Folder,
            defaultValue=None,
            optional=True))

        self.addParameter(QgsProcessingParameterBoolean(
            name=self.P_auto_download_ecmwf,
            description='Automatically download ECMWF data for atmospheric correction',
            defaultValue=False,
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
            name=self.P_deadpix_P_interp,
            description="Interpolation algorithm to be used during dead pixel correction "
                        "('linear', 'bilinear', 'cubic', 'spline')",
            defaultValue='linear',
            multiLine=False,
            optional=True))

        self.addParameter(QgsProcessingParameterNumber(
            name=self.P_ortho_resampAlg,
            description="Ortho-rectification resampling algorithm",
            defaultValue=1,
            type=QgsProcessingParameterNumber.Integer,
            optional=True))

    @staticmethod
    def _run_cmd(cmd, no_stdout=False, no_stderr=False):
        """Execute external command and get its stdout, exitcode and stderr.
        :param cmd: a normal shell command including parameters
        """

        proc = Popen(shlex.split(cmd), stdout=None if no_stdout else PIPE, stderr=None if no_stderr else PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode

        return out, exitcode, err

    def processAlgorithm(self, parameters, context, feedback):
        assert isinstance(parameters, dict)
        assert isinstance(context, QgsProcessingContext)
        assert isinstance(feedback, QgsProcessingFeedback)

        # print all parameters to log
        for key in sorted(parameters):
            feedback.pushInfo('{} = {}'.format(key, repr(parameters[key])))

        # validate that ENPT_PYENV environment variable is correctly set
        if 'ENPT_PYENV_ACTIVATION' not in os.environ:
            raise EnvironmentError("Environment variable 'ENPT_PYENV_ACTIVATION' is not set. "
                                   "Please check that the EnPT Python environment is correctly installed.")

        if not os.path.exists(os.environ['ENPT_PYENV_ACTIVATION']):
            raise EnvironmentError("The EnPT Python environment activation script cannot be found at %s. "
                                   "Please check that the EnPT Python environment is correctly installed."
                                   % os.environ['ENPT_PYENV_ACTIVATION'])

        # run EnPT via command line
        keyval_str = ' '.join(['--{} {}'.format(key, parameters[key])
                               for key in sorted(parameters) if parameters[key] is not None])
        if os.name == 'nt':
            # Windows
            self._run_cmd('call enpt_run_cmd.bat ' + keyval_str)
        else:
            # Linux / OSX
            self._run_cmd('enpt_run_cmd.sh ' + keyval_str)

        # return outputs
        return {self.P_OUTPUT_RASTER: parameters[self.P_OUTPUT_RASTER],
                self.P_OUTPUT_VECTOR: parameters[self.P_OUTPUT_RASTER],
                self.P_OUTPUT_FILE: parameters[self.P_OUTPUT_RASTER],
                self.P_OUTPUT_FOLDER: parameters[self.P_OUTPUT_RASTER]}

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
               '<a href="https://gitext.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp">here</a>.</p>' \
               '<p>Type <i>python enpt_cli.py -h</i> into a shell to get further information about individual ' \
               'parameters.</p>'

        return text

    def helpString(self):
        return self.shortHelpString()

    @staticmethod
    def helpUrl(*args, **kwargs):
        return 'www.google.de'


if __name__ == '__main__':

    from enmapbox.gui.utils import initQgisApplication

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
