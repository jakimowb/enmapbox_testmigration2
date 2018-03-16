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
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.core.Processing import Processing


NAME = 'enmapbox'
DESCRIPTION = "EnMAP-Box 3"

class EnMAPBoxAlgorithmProvider(AlgorithmProvider):


    """
    The EnMAPBoxAlgorithmProvider contains the GeoAlgorithms under the umbrella of the EnMAP-Box.
    It enhances the "standard" processing.core.AlgorithmProvider by functionality to add and remove GeoAlgorithms during runtime.
    """
    def __init__(self):
        super(EnMAPBoxAlgorithmProvider, self).__init__()
        #internal list of GeoAlgorithms. Is used on re-loads and can be manipulated
        self._algs = []

        #the list of GeoAlgorithms that will be used by the Processing Framework
        self.algs = []
        self.settingsName = 'ACTIVATE_' + self.getName().upper().replace(' ', '_')

    def initializeSettings(self):
        """This is the place where you should add config parameters
        using the ProcessingConfig class.

        This method is called when a provider is added to the
        Processing framework. By default it just adds a setting to
        activate or deactivate algorithms from the provider.
        """
        ProcessingConfig.settingIcons[self.getDescription()] = self.getIcon()

        ProcessingConfig.addSetting(Setting(self.getDescription(), self.settingsName,
                                            self.tr('Activate'), self.activate))


    def unload(self):
        """Do here anything that you want to be done when the provider
        is removed from the list of available ones.

        This method is called when you remove the provider from
        Processing. Removal of config setting should be done here.
        """

        ProcessingConfig.removeSetting(self.settingsName)

    def getName(self):
        """Returns the name to use to create the command-line name.
           Should be a short descriptive name of the provider.
        """
        return NAME


    def getDescription(self):
        """Returns the full name of the provider, as it is shown in the Processing Tool Box"""
        return DESCRIPTION

    def getIcon(self):
        from enmapbox.gui.enmapboxgui import getIcon
        return getIcon()

    def loadAlgorithms(self):
        self.algs = []
        self._loadAlgorithms()
        #ensure that all loaded GeoAlgorithms have this class instance as provider
        for alg in self.algs:
            alg.provider = self

    def _loadAlgorithms(self):
        #load other algorithms
        self.algs.extend(self._algs[:])

    def appendAlgorithms(self, geoAlgorithms):
        """
        Allows to add GeoAlgorithms during runtime
        :param geoAlgorithms: list-of-GeoAlgorithms
        """

        for ga in [ga for ga in geoAlgorithms if isinstance(ga, GeoAlgorithm)]:
            assert isinstance(ga, GeoAlgorithm)
            # update self._algs. This will be used if QGIS PF calls _loadAlgorithms
            if ga not in self._algs:
                ga.provider = self
                self._algs.append(ga)

            # update self.algs. This might be used by QGIS PF during runtime
            if ga not in self.algs:
                self.algs.append(ga)

        #append the GeoAlgorithms to the QGIS PF algorithm list
        from processing.core.alglist import algList

        #in case the processing framework was de-activated and activated again, we need to ensure that this provider instance is
        #part of it
        if self.getName() not in algList.algs.keys():
            Processing.addProvider(self)

        pAlgs = algList.algs[self.getName()]
        if len(self.algs) > 0:
            for ga in [ga for ga in self._algs \
                       if isinstance(ga, GeoAlgorithm) and ga not in pAlgs]:
                pAlgs[ga.commandLineName()] = ga

            algList.providerUpdated.emit(self.getName())

