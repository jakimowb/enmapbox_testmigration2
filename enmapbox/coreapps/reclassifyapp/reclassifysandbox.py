# -*- coding: utf-8 -*-

"""
***************************************************************************
    hubreclassify/sandbox.py

    An exemplary sandbox to play around and test how and if things work.
    ---------------------
    Date                 : Juli 2017
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

"""
Sandbox examples that show how to run own EnMAP-box applications without starting a QGIS GUI Instance

"""
import qgis
def sandboxWithEnMapBox(loadPF=False):
    """
    A minimum example that shows how to load the EnMAP-Box
    :param loadPF: Set on True to initialize the QGIS Processing Framework as well (takes longer)
    :return:
    """
    """Minimum example to the this application"""
    from enmapbox.gui.utils import initQgisApplication, sandboxPureGui
    qgsApp = initQgisEnvironment()
    sandboxPureGui(loadProcessingFramework=loadPF, loadExampleData=False)
    from enmapbox.gui.enmapboxgui import EnMAPBox
    EnMAPBox.instance().openExampleData()

    qgsApp.exec_()
    qgsApp.quit()


def sandboxGuiOnly():
    """
    Show & Test the GUI, without any EnMAP-Box / QGIS
    :return:
    """
    from enmapbox.gui.utils import initQgisApplication
    qgsApp = initQgisApplication()
    from reclassifyapp.reclassifydialog import ReclassifyDialog
    ui1 = ReclassifyDialog()

    def onSignal(*args):
        print(args)


    ui1.accepted.connect(lambda: onSignal(('Accepted',ui1.reclassificationSettings())))
    ui1.rejected.connect(lambda: onSignal('Rejected'))

    ui1.show()

    from enmapbox.gui.utils import jp
    from enmapbox import DIR_REPO

    pathSrc = jp(DIR_REPO, 'tmp/testclassification.tif')
    pathDst = jp(DIR_REPO, 'tmp/reclassified.tif')
    ui1.addSrcRaster(pathSrc)
    from enmapbox.gui.classificationscheme import ClassificationScheme
    ui1.setDstClassification(ClassificationScheme.create(3))
    ui1.setDstRaster(pathDst)
    def runReclassification(**settings):
        # return {'pathSrc': pathSrc, 'pathDst': pathDst, 'LUT': LUT,
        #        'classNames': dstScheme.classNames(), 'classColors': dstScheme.classColors()}
        if len(settings) > 0:
            import reclassify
            reclassify.reclassify(settings['pathSrc'],
                                  settings['pathDst'],
                                  settings['dstClassScheme'],
                                  settings['labelLookup'])
    ui1.accepted.connect(lambda: runReclassification(**ui1.reclassificationSettings()))


    qgsApp.exec_()
    qgsApp.quit()

if __name__ == '__main__':
    if True: sandboxGuiOnly()
    if False: sandboxWithEnMapBox(loadPF=False)

