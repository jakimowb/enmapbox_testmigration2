""""
This example shows how read and access a QGIS RasterRenderer Definition from XML (copy & paste from QGIS layers)

"""
import os, sys, re
from osgeo import gdal
from qgis.core import *
from qgis.gui import *
from PyQt4.Qt import *

SRC_DIR = os.path.dirname(__file__)

path1 = os.path.join(SRC_DIR, 'style1.txt') #XML QgsSingleBandPseudoColorRenderer
path2 = os.path.join(SRC_DIR, 'style2.txt') #XML QgsPalettedRasterRenderer


def readRenderer(text):
    dom = QDomDocument()
    dom.setContent(text)
    root = dom.documentElement()
    elem = root.elementsByTagName('rasterrenderer').item(0).toElement()
    renderer = None
    if re.search('rasterrenderer[^\n]*singlebandpseudocolor', text):
        #renderer = QgsSingleBandPseudoColorRenderer(None, 0, None)
        #renderer.readXML(elem)
        renderer = QgsSingleBandPseudoColorRenderer.create(elem, None)

    elif re.search('rasterrenderer[^\n]*paletted', text):

        #renderer = QgsPalettedRasterRenderer(None, 1, [])
        #renderer.readXML(elem)
        renderer = QgsPalettedRasterRenderer.create(elem, None)
    return renderer

for p in [path1, path2]:
    r = readRenderer(''.join(open(p).readlines()))
    print('Info {} {}'.format(r, type(r)))
    if isinstance(r, QgsSingleBandPseudoColorRenderer):
        print('Class min-max: [{},{}]'.format(r.classificationMin(), r.classificationMax()))
        shader = r.shader()
        if isinstance(shader, QgsRasterShader):
            shaderFunction =  shader.rasterShaderFunction()
            if isinstance(shaderFunction, QgsColorRampShader):
                print('Value\nColor\tLabel')
                for ci in shaderFunction.colorRampItemList():
                    print('{} {} {}'.format(ci.value, ci.color.getRgb(), ci.label))

                    s = ""

    elif isinstance(r, QgsPalettedRasterRenderer):
        print('nColors:{}'.format(r.nColors()))
        v = r.colors().rgba()
        for i in range(r.nColors()):
            print('Class name {}:"{}"'.format(i+1, r.label(i)))

            #this should be possible with QGIS 2.0 to return the class colors
            # -> could be parsed in XML as well
            #print('{}'.format(r.colors[i].getRgb())



