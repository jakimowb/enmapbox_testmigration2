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
**************************************************************************
"""

import sys, os, site
from qgis.core import QgsApplication, QgsProcessingRegistry, QgsProcessingAlgorithm
import enmapbox

def run(debug=False, processing=False, applications=False, sources=None):
    '''
    Starts the EnMAP-Box GUI.

    :param debug: whether to run in debug mode
    :param processing: whether to load the processing framework
    :param applications: whether to load none core application
    :param sources: list of sources to be added
    :return:
    '''

    """
    
    :return:
    """
    from enmapbox.gui.utils import initQgisApplication
    qgisApp = initQgisApplication()
    import enmapbox
    enmapbox.DEBUG = debug
    enmapbox.LOAD_PROCESSING_FRAMEWORK = processing
    enmapbox.LOAD_EXTERNAL_APPS = applications

    from enmapbox.gui.enmapboxgui import EnMAPBox
    import qgis.utils

    enmapBox = EnMAPBox(qgis.utils.iface)
    enmapbox.initEnMAPBoxProcessingProvider()
    enmapBox.run()
    if sources is not None:
        enmapBox.addSources(sourceList=sources)

    qgisApp.exec_()


if __name__ == '__main__':
    thisDir = os.path.dirname(__file__)
    if thisDir in sys.path:
        sys.path.remove(thisDir)

    args = sys.argv[1:]


    run()
