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



from enmapbox import __version__
from qgis.core import *
from qgis.PyQt.QtGui import QIcon
from processing.core.ProcessingConfig import ProcessingConfig, Setting



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
        self.mSettingsPrefix = self.id().upper().replace(' ', '_')

    def initializeSettings(self):
        """This is the place where you should add config parameters
        using the ProcessingConfig class.

        This method is called when a provider is added to the
        Processing framework. By default it just adds a setting to
        activate or deactivate algorithms from the provider.
        """

        ProcessingConfig.setGroupIcon(self.name(), self.getIcon())
        ProcessingConfig.addSetting(Setting(self.name(), self.mSettingsPrefix+'_ACTIVATE',
                                            self.tr('Activates the EnMAP-Box'), True))
        ProcessingConfig.addSetting(Setting(self.name(), self.mSettingsPrefix+'_HELPPATH', 'Location of EnMAP-Box docs', 'default'))
        ProcessingConfig.readSettings()


    def emitUpdated(self):
        """
        Will inform the ProcessingConfig that Provider settings have been changed.
        """
        import processing.core.ProcessingConfig
        processing.core.ProcessingConfig.settingsWatcher.settingsChanged.emit()

    def getName(self):
        raise DeprecationWarning('Use id() instead')

    def getDescription(self):
        raise DeprecationWarning('Use name()')

    def getIcon(self):
        raise DeprecationWarning('Use icon()')

    def id(self)->str:
        """
        :return:
        """
        return ID

    def helpid(self)->str:
        return 'https://bitbucket.org/hu-geomatics/enmap-box/wiki/Home'

    def icon(self)->QIcon:
        """
        Returns the EnMAPBox icon
        :return: QIcon
        """
        from enmapbox.gui.enmapboxgui import getIcon
        return getIcon()

    def name(self)->str:
        """
        :return: str
        """
        return NAME

    def longName(self)->str:
        """
        :return: str
        """
        return LONG_NAME

    def defaultRasterFileExtension(self)->str:
        """
        :return: 'bsq'
        """
        return 'bsq'

    def defaultVectorFileExtension(self)->str:
        """
        :return: 'shp'
        """
        return 'shp'

    def supportedOutputRasterLayerExtensions(self)->list:
        return ['bsq','bil','bip','tif']

    def supportsNonFileBasedOutput(self)->bool:
        return False

    def load(self):
        """
        Loads the provider.
        :return: bool
        """
        self.refreshAlgorithms()
        return True

    def containsAlgorithm(self, algorithm:QgsProcessingAlgorithm)->bool:
        """
        Returns True if an algorithm with same name is already added.
        :param algorithm:
        :return:
        """
        for a in self.algorithms():
            if a.name() == algorithm.name():
                return True
        return False

    def unload(self):
        """
        This method is called when you remove the provider from
        Processing. Removal of config setting should be done here.
        """
        for key in list(ProcessingConfig.settings.keys()):
            if key.startswith(self.mSettingsPrefix):
                ProcessingConfig.removeSetting(key)
        #del ProcessingConfig.settingIcons[self.name()]
        #ProcessingConfig.removeSetting(GdalUtils.GDAL_HELP_PATH)


    def isActive(self)->bool:
        """Return True if the provider is activated and ready to run algorithms"""
        return True

    def setActive(self, active):
        ProcessingConfig.setSettingValue(self.mSettingsPrefix, active)


    def addAlgorithm(self, algorithm:QgsProcessingAlgorithm, _emitUpdated=True):
        """
        Adds a QgsProcessingAlgorithm to the EnMAPBoxAlgorithmProvider
        :param algorithm: QgsProcessingAlgorithm
        :param _emitUpdated: bool, True by default. set on False to not call .emitUpdated() automatically
        :return:
        """

        super(EnMAPBoxAlgorithmProvider,self).addAlgorithm(algorithm)
        self.mAlgorithms.append(algorithm)
        if _emitUpdated:
            self.emitUpdated()

    def addAlgorithms(self, algorithmns:list):
        """
        Adds a list of QgsProcessingAlgorithms. The self.emitUpdated() signal is called 1x afterwards.
        """
        assert isinstance(algorithmns, list)
        for a in algorithmns:
            self.addAlgorithm(a.create(), _emitUpdated = False)
        if len(algorithmns) > 0:
            self.emitUpdated()
        #self.refreshAlgorithms()

    def removeAlgorithm(self, algorithm:QgsProcessingAlgorithm):
        """
        Removes a single QgsProcessingAlgorithms
        :param algorithm: QgsProcessingAlgorithm
        """
        self.removeAlgorithms([algorithm])

    def removeAlgorithms(self, algorithms:list):
        """
        Removes a list of QgsProcessingAlgorithms
        :param algorithms: [list-of-QgsProcessingAlgorithms]
        """
        if isinstance(algorithms, QgsProcessingAlgorithm):
            algorithms = [algorithms]

        for a in algorithms:
            if a in self.mAlgorithms:
                self.mAlgorithms.remove(a)
        #self.refreshAlgorithms()

    def refreshAlgorithms(self, *args, **kwargs):

        copies = [a.create() for a in self.algorithms()]
        self.removeAlgorithms(self.algorithms())
        super(EnMAPBoxAlgorithmProvider,self).refreshAlgorithms()
        self.addAlgorithms(copies)

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        for alg in self.mAlgorithms:
            alg.provider = self
        self.addAlgorithms(self.mAlgorithms)

