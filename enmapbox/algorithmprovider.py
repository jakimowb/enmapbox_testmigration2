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
from __future__ import absolute_import
import sys, os

from enmapbox import __version__
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.GeoAlgorithm import GeoAlgorithm


class EnMAPBoxAlgorithmProvider(AlgorithmProvider):
    def __init__(self):
        super(EnMAPBoxAlgorithmProvider, self).__init__()
        #internal list of GeoAlgorithms. Is used on re-loads and can be manipulated
        self._algs = []
        self.algs = []

    def getName(self):
        return 'EnMAP-Box'

    def getDescription(self):
        return 'EnMAP-Box ' + __version__

    def getIcon(self):
        from enmapbox.gui.enmapboxgui import getIcon
        return getIcon()

    def loadAlgorithms(self):
        self.algs = []
        self._loadAlgorithms()
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
            # update self._algs. This will be used if QGIS PF calls _loadAlgorithms
            if ga not in self._algs:
                ga.provider = self
                self._algs.append(ga)

            # update self.algs. This might be used by QGIS PF during runtime
            if ga not in self.algs:
                self.algs.append(ga)

        #append the QGIS PF algorithm list
        from processing.core.alglist import algList
        pAlgs = algList.algs[self.getName()]
        if len(self.algs) > 0:
            for ga in [ga for ga in self._algs \
                       if isinstance(ga, GeoAlgorithm) and ga not in pAlgs]:
                pAlgs[ga.commandLineName()] = ga
            algList.providerUpdated.emit(self.getName())

