import sys, math, re, io
from os.path import dirname, join, exists, abspath


from collections import defaultdict
from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtXml import QDomDocument
from PyQt5 import uic
from osgeo import gdal

import weakref
import numpy as np

def loadUIFormClass(pathUi, from_imports=False, resourceSuffix=''):
    RC_SUFFIX =  resourceSuffix
    assert exists(pathUi), '*.ui file does not exist: {}'.format(pathUi)

    #parse *.ui xml and replace *.h by qgis.gui
    doc = QDomDocument()

    #remove new-lines. this prevents uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
    #to mess up the *.ui xml
    f = open(pathUi, 'r')
    txt = ''.join(f.readlines())
    f.close()
    doc.setContent(txt)

    # Replace *.h file references in <customwidget> with <class>Qgs...</class>, e.g.
    #       <header>qgscolorbutton.h</header>
    # by    <header>qgis.gui</header>
    # this is require to compile QgsWidgets on-the-fly
    elem = doc.elementsByTagName('customwidget')
    for child in [elem.item(i) for i in range(elem.count())]:
        child = child.toElement()
        className = str(child.firstChildElement('class').firstChild().nodeValue())
        if className.startswith('Qgs'):
            cHeader = child.firstChildElement('header').firstChild()
            cHeader.setNodeValue('qgis.gui')

    #collect resource file locations
    elem = doc.elementsByTagName('include')
    qrcPathes = []
    for child in [elem.item(i) for i in range(elem.count())]:
        path = child.attributes().item(0).nodeValue()
        if path.endswith('.qrc'):
            qrcPathes.append(path)



    buffer = io.StringIO()  # buffer to store modified XML
    buffer.write(doc.toString())
    buffer.flush()
    buffer.seek(0)


    #make resource file directories available to the python path (sys.path)
    baseDir = dirname(pathUi)
    tmpDirs = []
    for qrcPath in qrcPathes:
        d = abspath(join(baseDir, dirname(qrcPath)))
        if d not in sys.path:
            tmpDirs.append(d)
    sys.path.extend(tmpDirs)

    #load form class
    try:
        FORM_CLASS, _ = uic.loadUiType(buffer, resource_suffix=RC_SUFFIX)
    except SyntaxError as ex:
        FORM_CLASS, _ = uic.loadUiType(pathUi, resource_suffix=RC_SUFFIX)

    buffer.close()

    #remove temporary added directories from python path
    for d in tmpDirs:
        sys.path.remove(d)

    return FORM_CLASS

