""""
This example shows how read and access a QGIS RasterRenderer Definition from XML (copy & paste from QGIS layers)

"""
import os, sys, re
from osgeo import gdal
from qgis.core import *
from qgis.gui import *


SRC_DIR = os.path.dirname(__file__)

examples = [
     os.path.join(SRC_DIR, 'style1.txt') #XML QgsSingleBandPseudoColorRenderer
    ,os.path.join(SRC_DIR, 'style2.txt') #XML QgsPalettedRasterRenderer
    ,os.path.join(SRC_DIR, 'style3.txt') #XML
]


RENDER_CLASSES = {}
RENDER_CLASSES['rasterrenderer'] = {
    'singlebandpseudocolor':QgsSingleBandPseudoColorRenderer,
    'paletted':QgsPalettedRasterRenderer
}
RENDER_CLASSES['renderer-v2'] = {
    'categorizedSymbol':QgsCategorizedSymbolRendererV2
}



def readRenderer(text):
    """
    Reads a string `text` and returns the first QgsRasterRenderer or QgsFeatureRenderer (if defined).
    :param text:
    :return:
    """
    dom = QDomDocument()
    dom.setContent(text)
    root = dom.documentElement()


    for baseClass, renderClasses in RENDER_CLASSES.items():
        elements = root.elementsByTagName(baseClass)
        if elements.count() > 0:
            elem = elements.item(0).toElement()
            typeName = elem.attributes().namedItem('type').nodeValue()
            if typeName in renderClasses.keys():
                rClass = renderClasses[typeName]
                if baseClass == 'rasterrenderer':
                    return rClass.create(elem, None)
                elif baseClass == 'renderer-v2':
                    return rClass.create(elem)
    return None

for p in examples:
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
        v = r.colors().rgba2D()
        for i in range(r.nColors()):
            print('Class name {}:"{}"'.format(i+1, r.label(i)))

            #this should be possible with QGIS 2.0 to return the class colors
            # -> could be parsed in XML as well
            #print('{}'.format(r.colors[i].getRgb())

    elif isinstance(r, QgsCategorizedSymbolRendererV2):
        for i, cat in enumerate(r.categories()):
            assert isinstance(cat, QgsRendererCategoryV2)
            print(re.sub('[\n]','','{}:{}'.format(i,cat.dump())))


