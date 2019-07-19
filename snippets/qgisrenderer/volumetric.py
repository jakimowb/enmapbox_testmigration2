# -*- coding: utf-8 -*-
"""
Demonstrates GLVolumeItem for displaying volumetric data.

"""

STYLE = """
<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis minScale="1e+08" styleCategories="AllStyleCategories" maxScale="0" version="3.8.0-Zanzibar" hasScaleBasedVisibilityFlag="0">
 <flags>
  <Identifiable>1</Identifiable>
  <Removable>1</Removable>
  <Searchable>1</Searchable>
 </flags>
 <customproperties>
  <property value="false" key="WMSBackgroundLayer"/>
  <property value="false" key="WMSPublishDataSourceUrl"/>
  <property value="0" key="embeddedWidgets/count"/>
  <property value="Value" key="identify/format"/>
 </customproperties>
 <pipe>
  <rasterrenderer alphaBand="-1" classificationMin="0" band="175" classificationMax="1000" type="singlebandpseudocolor" opacity="1">
   <rasterTransparency/>
   <minMaxOrigin>
    <limits>MinMax</limits>
    <extent>WholeRaster</extent>
    <statAccuracy>Estimated</statAccuracy>
    <cumulativeCutLower>0.02</cumulativeCutLower>
    <cumulativeCutUpper>0.98</cumulativeCutUpper>
    <stdDevFactor>2</stdDevFactor>
   </minMaxOrigin>
   <rastershader>
    <colorrampshader classificationMode="1" clip="1" colorRampType="INTERPOLATED">
     <colorramp type="gradient" name="[source]">
      <prop v="215,25,28,255" k="color1"/>
      <prop v="43,131,186,255" k="color2"/>
      <prop v="0" k="discrete"/>
      <prop v="gradient" k="rampType"/>
      <prop v="0.25;253,174,97,255:0.5;255,255,191,255:0.75;171,221,164,255" k="stops"/>
     </colorramp>
     <item value="0" alpha="255" label="0" color="#d7191c"/>
     <item value="1192" alpha="255" label="1192" color="#fdae61"/>
     <item value="2384" alpha="255" label="2384" color="#ffffbf"/>
     <item value="3576" alpha="255" label="3576" color="#abdda4"/>
     <item value="4768" alpha="255" label="4768" color="#2b83ba"/>
    </colorrampshader>
   </rastershader>
  </rasterrenderer>
  <brightnesscontrast brightness="0" contrast="0"/>
  <huesaturation colorizeGreen="128" colorizeOn="0" saturation="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" colorizeStrength="100"/>
  <rasterresampler maxOversampling="2"/>
 </pipe>
 <blendMode>0</blendMode>
</qgis>
"""


## Add path to library (just for examples; you do not need this)
import time
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from enmapbox.testing import initQgisApplication
from qgis.PyQt import QtCore, QtGui
app = initQgisApplication()

import numpy as np

from enmapboxtestdata import enmap

from enmapbox import initAll
initAll()
import enmapbox.externals.pyqtgraph

from enmapbox.externals.qps.layerproperties import rendererFromXml
renderer2 = rendererFromXml(STYLE)




lyr1 = QgsRasterLayer(enmap)
lyr2 = QgsRasterLayer(enmap)
renderer2.setInput(lyr2.dataProvider())
lyr2.setRenderer(renderer2)
gl = enmapbox.externals.pyqtgraph.opengl

W = QWidget()
W.setLayout(QHBoxLayout())

glWidget = gl.GLViewWidget()
glWidget.opts['distance'] = 200
W.show()
glWidget.setWindowTitle('pyqtgraph example: GLVolumeItem')

RW = QgsSingleBandPseudoColorRendererWidget(lyr2, lyr2.extent())
RW.show()
glWidget.show()
#W.layout().addWidget(glWidget)
#W.layout().addWidget(RW)
# b = gl.GLBoxItem()
# w.addItem(b)
#g = gl.GLGridItem()
#g.scale(10, 10, 1)
#w.addItem(g)


QGIS2NUMPY_DATA_TYPES = {Qgis.Byte: np.byte,
                         Qgis.UInt16: np.uint16,
                         Qgis.Int16: np.int16,
                         Qgis.UInt32: np.uint32,
                         Qgis.Int32: np.int32,
                         Qgis.Float32: np.float32,
                         Qgis.Float64: np.float64,
                         Qgis.CFloat32: np.complex,
                         Qgis.CFloat64: np.complex64,
                         Qgis.ARGB32: np.uint32,
                         Qgis.ARGB32_Premultiplied: np.uint32}


nb = lyr1.bandCount()

width = 50
height = 100


ext = lyr1.extent()
ext.setXMinimum(ext.xMinimum()-200)

renderer1 = lyr1.renderer()




npx = width * height
d2 = np.empty((width, height,nb, 4), dtype=np.ubyte)
d1 = np.empty((width * height,nb), dtype=np.uint32)

px_coords = np.indices((width, height))

c_x = np.arange(width)
c_y = np.arange(height)

i_nodata = c_x = c_y = None
i_valid1D = i_valid2D = None
n_valid = None
data = None

t0 = time.time()

data = np.empty((width, height, nb + 1, 4),  dtype=np.ubyte)


def getColorRGBArrays(colorArray, shape):
    r = np.asarray([qRed(c) for c in colorArray]).reshape(shape)
    g = np.asarray([qGreen(c) for c in colorArray]).reshape(shape)
    b = np.asarray([qBlue(c) for c in colorArray]).reshape(shape)
    a = np.asarray([qAlpha(c) for c in colorArray]).reshape(shape)

    return r,g,b,a




for i_b in range(nb):

    if i_b == 0:
        block = renderer1.block(0, ext, width, height)
        colorArray = np.frombuffer(block.data(), dtype=QGIS2NUMPY_DATA_TYPES[block.dataType()])
        i_nodata = np.where(colorArray == 0)[0]

        r,g,b,a = getColorRGBArrays(colorArray, (width,height))

        #if len(i_nodata) > 0:
        #    a[i_nodata] = 5
        #    r[i_nodata] = 255
        #    g[i_nodata] = 0
        #    b[i_nodata] = 0

        data[:, :, 0, 0] = r
        data[:, :, 0, 1] = g
        data[:, :, 0, 2] = b
        data[:, :, 0, 3] = a

    renderer2.setBand(i_b+1)
    block = renderer2.block(i_b, ext, width, height)
    colorArray = np.frombuffer(block.data(), dtype=QGIS2NUMPY_DATA_TYPES[block.dataType()])
    r, g, b, a = getColorRGBArrays(colorArray, (width, height))

    data[:, :, i_b+1, 0] = r
    data[:, :, i_b+1, 1] = g
    data[:, :, i_b+1, 2] = b
    data[:, :, i_b+1, 3] = a

    #colorArray = colorArray[i_valid]

    #colorArray = [QColor(c).getRgb() for c in colorArray]

t1 = time.time()

v = gl.GLVolumeItem(data)
v.rotate(180,1,1,0)


v.translate(-width*0.5, -height*0.5, -nb*0.5)
v.scale(1,1,0.5)
glWidget.addItem(v)

t2 = time.time()

print('T1: {}'.format(t1-t0))
print('T2: {}'.format(t2-t1))
#ax = gl.GLAxisItem()
#w.addItem(ax)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys

    app.exec_()
