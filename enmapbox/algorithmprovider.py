# -*- coding: utf-8 -*-

"""
***************************************************************************
    __main__
    ---------------------
    Date                 : August 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import sys, os

from enmapbox import __version__
from qgis.core import *
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.core.Processing import Processing


ID = 'enmapbox'
NAME = 'EnMAP-Box'
LONG_NAME = 'EnMAP-Box (build {})'.format(__version__)

class EnMAPBoxAlgorithmProvider(QgsProcessingProvider):


    """
    The EnMAPBoxAlgorithmProvider contains the GeoAlgorithms under the umbrella of the EnMAP-Box.
    It enhances the "standard" processing.core.AlgorithmProvider by functionality to add and remove GeoAlgorithms during runtime.
    """
    def __init__(self):
        super(EnMAPBoxAlgorithmProvider, self).__init__()
        #internal list of GeoAlgorithms. Is used on re-loads and can be manipulated
        self.mAlgorithms = []
        self.mSettingsName = self.id().upper().replace(' ', '_')

    def initializeSettings(self):
        """This is the place where you should add config parameters
        using the ProcessingConfig class.

        This method is called when a provider is added to the
        Processing framework. By default it just adds a setting to
        activate or deactivate algorithms from the provider.
        """
        ProcessingConfig.settingIcons[self.name()] = self.getIcon()

        ProcessingConfig.addSetting(Setting(self.name(), self.mSettingsName,
                                            self.tr('Activate'), self.activate))


    def unload(self):
        """Do here anything that you want to be done when the provider
        is removed from the list of available ones.

        This method is called when you remove the provider from
        Processing. Removal of config setting should be done here.
        """

        ProcessingConfig.removeSetting(self.mSettingsName)

    def getName(self):
        raise DeprecationWarning('Use id() instead')

    def id(self):
        return ID

    def helpid(self):
        return 'https://bitbucket.org/hu-geomatics/enmap-box/wiki/Home'

    def getDescription(self):
        raise DeprecationWarning('Use name()')

    def getIcon(self):
        raise DeprecationWarning('Use icon()')

    def icon(self):
        from enmapbox.gui.enmapboxgui import getIcon
        return getIcon()

    def name(self):
        return NAME

    def longName(self):
        return LONG_NAME

    def defaultRasterFileExtension(self):
        return 'bsq'

    def defaultVectorFileExtension(self):
        return 'shq'

    def supportedOutputRasterLayerExtensions(self):
        return ['tif','vrt','bil','bsq','bip']

    def supportsNonFileBasedOutput(self):
        return True

    def supportsNonFileBasedOutput(self):
        return False

    def load(self):
        """
        Loads the provider.
        :return:
        """

        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.mSettingsName, 'ACTIVATE',
                                            self.tr('Activates the EnMAP-Box'), True))
        ProcessingConfig.addSetting(Setting(
            self.mSettingsName,
            'helppath',
            'Location of EnMAP-Box docs', 'default'))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        """
        Unloads the provider.
        """

        ProcessingConfig.removeSetting(self.mSettingsName)
        del ProcessingConfig.settingIcons[self.name()]
        #ProcessingConfig.removeSetting(GdalUtils.GDAL_HELP_PATH)


    def isActive(self):
        """Return True if the provider is activated and ready to run algorithms"""
        return True
        #return ProcessingConfig.getSetting(self.settingsName)

    def setActive(self, active):
        ProcessingConfig.setSettingValue(self.mSettingsName, active)


    def loadAlgorithms(self):

        for alg in self.mAlgorithms:
            alg.provider = self

    """
    def addAlgorithm(self, algorithm):
        assert isinstance(algorithm, QgsProcessingAlgorithm)

        # update self._algs. This will be used if QGIS PF calls _loadAlgorithms
        if algorithm not in self.mAlgorithms:
            algorithm.setProvider(self)
            self.mAlgorithms.append(algorithm)

        # update self.algs. This might be used by QGIS PF during runtime
        if algorithm not in self.algs:
            self.algs.append(algorithm)


        #in case the processing framework was de-activated and activated again, we need to ensure that this provider instance is
        #part of it
        reg = QgsApplication.processingRegistry()
        if self.getName() not in algList.algs.keys():
            Processing.addProvider(self)

        pAlgs = algList.algs[self.getName()]
        if len(self.algs) > 0:
            for ga in [ga for ga in self.mAlgorithms \
                       if isinstance(ga, GeoAlgorithm) and ga not in pAlgs]:
                pAlgs[ga.commandLineName()] = ga

            algList.providerUpdated.emit(self.getName())
    """


if __name__ == '__main__':
    from enmapbox.gui.utils import *
    app = initQgisApplication()

    iface = QgisInterfaceMockup.create()





    from enmapbox.gui.enmapboxgui import EnMAPBox
    from enmapbox.algorithmprovider import EnMAPBoxAlgorithmProvider
    import qgis.utils
    p = EnMAPBoxAlgorithmProvider()

    reg = QgsApplication.processingRegistry()
    reg.addProvider(p)
    from processing.gui.ConfigDialog import ConfigDialog
    dlg1 = ConfigDialog()
    dlg1.show()

    #from processing.algs.exampleprovider.ExampleAlgorithm import ExampleAlgorithm
    from processing.algs.gdal.buildvrt import buildvrt
    p.addAlgorithm(buildvrt())

    from processing.gui.ProcessingToolbox import ProcessingToolbox
    dlg2 = ProcessingToolbox()
    dlg2.show()

    app.exec_()