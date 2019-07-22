# -*- coding: utf-8 -*-
"""
Demonstrates GLVolumeItem for displaying volumetric data.

"""
import os, sys, re, pickle, enum
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
import numpy as np

from enmapbox.gui.utils import loadUIFormClass
from enmapbox.externals.qps.layerproperties import showLayerPropertiesDialog, rendererFromXml, rendererToXml
import enmapbox.externals.pyqtgraph as pg
import enmapbox.externals.qps.externals.pyqtgraph.opengl as gl
from enmapbox.externals.qps.externals.pyqtgraph.opengl.GLViewWidget import GLViewWidget
from enmapbox.externals.qps.externals.pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

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


def getColorRGBArrays(colorArray, shape:tuple):
    r = np.asarray([qRed(c) for c in colorArray]).reshape(shape)
    g = np.asarray([qGreen(c) for c in colorArray]).reshape(shape)
    b = np.asarray([qBlue(c) for c in colorArray]).reshape(shape)
    a = np.asarray([qAlpha(c) for c in colorArray]).reshape(shape)

    return r, g, b, a


if False:

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







def loadData(taskWrapper:QgsTask, dump):

    jobs = pickle.loads(dump)

    hasTask = isinstance(taskWrapper, QgsTask)
    results = []
    n = len(jobs)

    for i, job in enumerate(jobs):
        if hasTask and taskWrapper.isCanceled():
            return pickle.dumps(results)

        assert isinstance(job, RenderJob)
        lyr = job.rasterLayer()
        renderer = job.renderer()

        assert isinstance(lyr, QgsRasterLayer)
        assert isinstance(renderer, QgsRasterRenderer)

        nb = lyr.bandCount()
        ns = lyr.width()
        nl = lyr.height()

        if not job.hasSlicing():
            lyr.setRenderer(renderer)
            ext = lyr.extent()
            w = lyr.width()
            h = lyr.height()

            if True:
                w = int(w * 0.5)
                h = int(h * 0.5)

            block = renderer.block(1, ext, w, h)
            assert isinstance(block, QgsRasterBlock)
            colorArray = np.frombuffer(block.data(), dtype=QGIS2NUMPY_DATA_TYPES[block.dataType()])

            rgba = np.empty((h, w, 4), dtype=np.ubyte)

            red   = (colorArray >> 16) & 0xff
            green = (colorArray >> 8) & 0xff
            blue  = colorArray & 0xff
            alpha = colorArray >> 24

            rgba[..., 0] = red.reshape((h,w)) #np.asarray([qRed(c) for c in colorArray])
            rgba[..., 1] = green.reshape((h,w)) #np.asarray([qGreen(c) for c in colorArray])
            rgba[..., 2] = blue.reshape((h,w)) #np.asarray([qBlue(c) for c in colorArray])
            rgba[..., 3] = alpha.reshape((h,w)) #np.asarray([qAlpha(c) for c in colorArray])

            #rgba = rgba.reshape((h, w, 4))
            job.setRGBA(rgba)


        else:
            if isinstance(renderer, QgsSingleBandGrayRenderer):
                setBand = renderer.setGrayBand
            elif isinstance(renderer, QgsSingleBandPseudoColorRenderer):
                setBand = renderer.setBand
            elif isinstance(renderer, QgsSingleBandColorDataRenderer):
                setBand = lambda *args : None

            lyr.setRenderer(renderer)

            if job.sliceDim() == 'z':
                w = lyr.width()
                h = lyr.height()
                setBand(job.sliceIndex())

                block = renderer.block(job.sliceIndex(), lyr.extent(), w, h)
                assert isinstance(block, QgsRasterBlock)

                rgba = np.empty((h, w, 4), dtype=np.ubyte)

                colorArray = np.frombuffer(block.data(), dtype=QGIS2NUMPY_DATA_TYPES[block.dataType()])

                red = (colorArray >> 16) & 0xff
                green = (colorArray >> 8) & 0xff
                blue = colorArray & 0xff
                alpha = colorArray >> 24

                rgba[..., 0] = red.reshape((h, w))  # np.asarray([qRed(c) for c in colorArray])
                rgba[..., 1] = green.reshape((h, w))  # np.asarray([qGreen(c) for c in colorArray])
                rgba[..., 2] = blue.reshape((h, w))  # np.asarray([qBlue(c) for c in colorArray])
                rgba[..., 3] = alpha.reshape((h, w))  # np.asarray([qAlpha(c) for c in colorArray])

                job.setRGBA(rgba)

            else:
                # get slice extent with 1px width/height
                extent = lyr.extent()
                ext = QgsRectangle()

                if job.sliceDim() == 'x':
                    w = 1
                    npx = h = nl
                    ext.setYMaximum(extent.yMaximum())
                    ext.setYMinimum(extent.yMinimum())
                    cx = extent.xMinimum() + job.sliceIndex() * lyr.rasterUnitsPerPixelX()
                    ext.setXMinimum(cx)
                    ext.setXMaximum(cx + lyr.rasterUnitsPerPixelX())

                elif job.sliceDim() == 'y':
                    npx = w = ns
                    h = 1
                    ext.setXMinimum(extent.xMinimum())
                    ext.setXMaximum(extent.xMaximum())
                    cy = extent.yMinimum() + job.sliceIndex() * lyr.rasterUnitsPerPixelY()

                    ext.setYMaximum(cy + lyr.rasterUnitsPerPixelY())
                    ext.setYMinimum(cy)


                rgba = np.empty((npx, nb, 4), dtype=np.uint8)


                for b in range(nb):
                    setBand(b+1)

                    block = renderer.block(b, ext, w, h)

                    assert isinstance(block, QgsRasterBlock)
                    assert block.isValid()
                    assert block.dataType() != Qgis.UnknownDataType

                    colorArray = np.frombuffer(block.data(), dtype=QGIS2NUMPY_DATA_TYPES[block.dataType()])

                    red = (colorArray >> 16) & 0xff
                    green = (colorArray >> 8) & 0xff
                    blue = colorArray & 0xff
                    alpha = colorArray >> 24

                    rgba[:, b, 0] = red  # np.asarray([qRed(c) for c in colorArray])
                    rgba[:, b, 1] = green # np.asarray([qGreen(c) for c in colorArray])
                    rgba[:, b, 2] = blue  # np.asarray([qBlue(c) for c in colorArray])
                    rgba[:, b, 3] = alpha  # np.asarray([qAlpha(c) for c in colorArray])

                job.setRGBA(rgba)

        if job.rgba() is not None:
            results.append(job)

        if hasTask:
            taskWrapper.setProgress(i+1)
    return pickle.dumps(results)



    pass


def isSliceRenderer(r:QgsRasterRenderer)->bool:
    if r is None:
        return False
    return isinstance(r, (QgsSingleBandColorDataRenderer, QgsSingleBandGrayRenderer, QgsSingleBandPseudoColorRenderer))


class RenderJob(object):

    class JobType(enum.Enum):
        Normal=1
        SliceX=2
        SliceY=3
        SliceZ=4

    def __init__(self, id:str, layer:QgsRasterLayer, renderer:QgsRasterRenderer):

        self.mID = id
        self.mUri = layer.source()
        self.mDataProvider = layer.dataProvider().name()
        self.mRendererXML = rendererToXml(renderer).toString()
        self.mSliceDim = self.mSliceIndex = None
        self.mResults = None
        self.mRGBA = None

    def __eq__(self, other)->bool:
        if not isinstance(other, RenderJob):
            return False
        else:
            return self.mID == other.mID and \
                   self.mUri == other.mUri and \
                   self.mRendererXML == other.mRendererXML and \
                   self.mSliceDim == other.mSliceDim


    def id(self)->str:
        return self.mID

    def hasSlicing(self)->bool:
        return self.mSliceDim in ['x', 'y', 'z'] and isinstance(self.mSliceIndex, int)

    def setSlicing(self, sliceDim:str, sliceIndex:int):
        assert sliceDim in ['x','y','z']
        assert sliceIndex >= 0
        self.mSliceDim = sliceDim
        self.mSliceIndex = sliceIndex

    def rasterLayer(self)->QgsRasterLayer:
        return QgsRasterLayer(self.mUri, self.mID, self.mDataProvider)

    def renderer(self)->QgsRasterRenderer:
        return rendererFromXml(self.mRendererXML)

    def sliceDim(self)->str:
        return self.mSliceDim

    def sliceIndex(self)->int:
        return self.mSliceIndex

    def setResult(self, *args):

        self.mResults = args

    def results(self):
        return self.mResults

    def setRGBA(self, array):
        assert isinstance(array, np.ndarray)
        assert array.ndim == 3
        assert array.shape[2] == 4
        self.mRGBA = array

    def rgba(self)->np.ndarray:
        return self.mRGBA

pathUi = os.path.join(os.path.dirname(__file__), 'volumetric_gui.ui')
class VolumetricWidget(QWidget, loadUIFormClass(pathUi)):

    def __init__(self, *args, **kwds):

        super(VolumetricWidget, self).__init__(*args, **kwds)

        self.setupUi(self)

        self.mCanvas = QgsMapCanvas()
        self.mCanvas.setVisible(False)

        self.mSliceRenderer = None
        self.mTopPlaneRenderer = None

        self.mMapLayerComboBox.setAllowEmptyLayer(True)
        self.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)
        self.mMapLayerComboBox.layerChanged.connect(self.onLayerChanged)

        self.mLastConfig = None
        self.btnLoadData.clicked.connect(self.actionLoadData.trigger)
        self.btnSetRendererTopPlane.clicked.connect(self.actionSetRendererTopPlane.trigger)
        self.btnSetRendererSlices.clicked.connect(self.actionSetRendererSlices.trigger)
        self.btnResetGLView.clicked.connect(self.actionResetGLView.trigger)

        self.actionValidate.triggered.connect(self.onValidate)
        self.actionLoadData.triggered.connect(self.onLoadData)
        self.actionSetRendererTopPlane.triggered.connect(self.onSetTopPlaneRenderer)
        self.actionSetRendererSlices.triggered.connect(self.onSetSliceRenderer)
        self.actionResetGLView.triggered.connect(self.resetGLView)

        self.sliderX.valueChanged.connect(self.onValidate)
        self.sliderY.valueChanged.connect(self.onValidate)
        self.sliderZ.valueChanged.connect(self.onValidate)

        self.cbShowTopPlane.clicked.connect(lambda b: self.setGLItemVisbility('TOPPLANE', b))
        self.cbShowSliceX.clicked.connect(lambda b: self.setGLItemVisbility('SLICE_X', b))
        self.cbShowSliceY.clicked.connect(lambda b: self.setGLItemVisbility('SLICE_Y', b))
        self.cbShowSliceZ.clicked.connect(lambda b: self.setGLItemVisbility('SLICE_Z', b))
        self.cbShowBox.clicked.connect(lambda b: self.setGLItemVisbility('BOX', b))
        self.mJobs = dict()
        self.mLastJobs = []
        self.mGLItems = dict()

        w = self.glViewWidget()

        #center = w.opts['center']
        #dist = w.opts['distance']
        #elev = w.opts['elevation'] #* np.pi/180.
        #azim = w.opts['azimuth'] #* np.pi/180.

        self.mDefaultCAM = {}
        for k in ['distance', 'elevation', 'azimuth']:
            self.mDefaultCAM[k] = w.opts[k]

    def addGLItem(self, key, item):


        itemOld = self.mGLItems.get(key)
        if itemOld in self.glViewWidget().items:
            isVisible = itemOld.visible()
            item.setVisible(isVisible)
            self.glViewWidget().removeItem(itemOld)

        self.mGLItems[key] = item
        self.glViewWidget().addItem(item)

    def resetGLView(self):

        self.glViewWidget().setCameraPosition(**self.mDefaultCAM)

    def layerDims(self)->tuple:
        lyr = self.rasterLayer()
        if isinstance(lyr, QgsRasterLayer):
            ns = lyr.width()
            nl = lyr.height()
            nb = lyr.bandCount()
            return (nb, nl, ns)
        else:
            return (None, None, None)

    def rasterLayer(self)->QgsRasterLayer:
        return self.mMapLayerComboBox.currentLayer()

    def sliceRenderer(self)->QgsRasterRenderer:
        return self.mSliceRenderer

    def topPlaneRenderer(self)->QgsRasterRenderer:
        return self.mTopPlaneRenderer

    def onSetSliceRenderer(self):

        lyr = self.rasterLayer()
        if isinstance(lyr, QgsRasterLayer):
            lyr2 = QgsRasterLayer(lyr.source(), lyr.name(), lyr.dataProvider().name())
            r = self.sliceRenderer()
            if isSliceRenderer(r):
                lyr2.setRenderer(r)

            showLayerPropertiesDialog(lyr2, self.mCanvas)
            s = ""

            self.setSliceRenderer(lyr2.renderer())

        self.onValidate()

    def onSetTopPlaneRenderer(self):

        lyr = self.rasterLayer()
        if isinstance(lyr, QgsRasterLayer):
            lyr2 = QgsRasterLayer(lyr.source(), lyr.name(), lyr.dataProvider().name())
            r = self.topPlaneRenderer()
            if isinstance(r, QgsRasterRenderer):
                lyr2.setRenderer(r)
            showLayerPropertiesDialog(lyr2, self.mCanvas)
            s = ""
            self.setTopPlaneRenderer(lyr2.renderer())

        self.onValidate()

    def setSliceRenderer(self, renderer:QgsRasterRenderer):
        assert isinstance(renderer, (QgsSingleBandGrayRenderer, QgsSingleBandPseudoColorRenderer, QgsSingleBandColorDataRenderer))
        self.mSliceRenderer = renderer.clone()

    def setTopPlaneRenderer(self, renderer:QgsRasterRenderer):
        self.mTopPlaneRenderer = renderer.clone()

    def onLoadData(self):

        config = self.config()
        self.mLastConfig = config

        lyr = self.rasterLayer()

        jobTop = RenderJob('TOPPLANE', lyr, self.topPlaneRenderer())

        jobX = RenderJob('SLICE_X', lyr, self.sliceRenderer())
        jobX.setSlicing('x', self.x())

        jobY = RenderJob('SLICE_Y', lyr, self.sliceRenderer())
        jobY.setSlicing('y', self.y())

        jobZ = RenderJob('SLICE_Z', lyr, self.sliceRenderer())
        jobZ.setSlicing('z', self.z())

        jobList = [jobTop, jobX, jobY, jobZ]

        #job = [j for j in jobList if j not in self.mLastJobs]
        # jobList = [jobTop]

        dump = pickle.dumps(jobList)
        taskDescription = 'Load Top Plane'
        if True:
            self.onDataLoaded(loadData(None, dump))
        else:
            qgsTask = QgsTask.fromFunction(taskDescription, loadData, dump,
                                           on_finished=self.onAddSourcesAsyncFinished)

            tid = id(qgsTask)
            qgsTask.taskCompleted.connect(lambda *args, tid=tid: self.onRemoveTask(tid))
            qgsTask.taskTerminated.connect(lambda *args, tid=tid: self.onRemoveTask(tid))
            self.mTasks[tid] = qgsTask

    def setGLItemVisbility(self, key, b:bool):

        item = self.mGLItems.get(key)
        if isinstance(item, GLGraphicsItem):
            item.setVisible(b)
        else:
            print('Unknown item "{}"'.format(key))
        s = ""

    def glItemVisibility(self, key)->bool:
        item = self.mGLItems.get(key)
        if isinstance(item, GLGraphicsItem):
            return item.visible()
        else:
            return None

    def glViewWidget(self)->GLViewWidget:
        return self.openglWidget

    def onDataLoaded(self, dump):

        joblist = pickle.loads(dump)
        n = len(joblist)
        for i, job in enumerate(joblist):

            assert isinstance(job, RenderJob)
            print('Add {}'.format(job.id()))
            rgba = job.rgba()
            nb, nl, ns = self.layerDims()
            nnl, nns = rgba.shape[0:2]


            v1 = gl.GLImageItem(rgba)

            if job.mID == 'TOPPLANE':
                v1.scale(ns / nns, nl / nnl, 1)
                v1.translate(ns/2, nl/2, nb)
                v1.rotate(-90, 0, 0, 1)
            #box = gl.GLBoxItem(size=QVector3D(ns, nl, nb))
            #box.translate(-ns/2, -nl/2, 0)
            #v1.scale(1./ns, 1./nl, 1./nb)
            #v1.translate(-shape[1] / 2, -shape[2] / 2, 0)
            #default: xy plane
            if job.sliceDim() == 'z':
                v1.scale(ns / nns, nl / nnl, 1)
                v1.translate(-ns / 2, -nl / 2, job.sliceIndex())
                v1.rotate(-90, 0, 0, 1)
                #v1.translate(-ns / 2, -nl / 2, )

            elif job.sliceDim() == 'x':
                #
                v1.scale(ns / nns, 1, 1)
                v1.rotate(90, 0, 0, 1)
                v1.rotate(-90, 0, 1, 0)
                v1.translate((-ns + job.sliceIndex()) / 2, -nl / 2, nb)


            elif job.sliceDim() == 'y':
                v1.scale(1, nl / nnl, 1)
                v1.translate(-ns / 2, -nl / 2, nb)
                v1.rotate(-90, 1, 0, 0)



            self.addGLItem(job.mID, v1)
            #w = self.glViewWidget()
           # b = gl.GLBoxItem()
           # w.addItem(b)

            #ax2 = gl.GLAxisItem()
            #ax2.setParentItem(b)

            #b.translate(1, 1, 1)

            #,ä nw.addItem(v1)

    def onValidate(self)->bool:

        b = True
        b &= isinstance(self.topPlaneRenderer(), QgsRasterRenderer)
        b &= isSliceRenderer(self.sliceRenderer())
        b &= isinstance(self.rasterLayer(), QgsRasterLayer) and self.rasterLayer().isValid()

        self.btnLoadData.setEnabled(b)

        return b

    def config(self)->dict:
        lyr= self.rasterLayer()
        c = {'uri':lyr.source(), 'provider':lyr.dataProvider().name(),
             'x':self.x(), 'y':self.y(), 'z':self.z(),
             'rendererTop':self.topPlaneRenderer(), 'rendererSlices':self.sliceRenderer()
             }
        return c

    def setX(self, x:int):
        assert x > 0 and x < self.sliderX.maximum()
        self.sliderX.setValue(x)

    def x(self) -> int:
        return self.sliderX.value()


    def setY(self, y: int):
        assert y > 0 and y < self.sliderY.maximum()
        self.sliderY.setValue(y)

    def y(self)->int:
        return self.sliderY.value()


    def z(self) -> int:
        return self.sliderZ.value()

    def setZ(self, z: int):
        assert z > 0 and z < self.sliderZ.maximum()
        self.sliderZ.setValue(z)


    def onLayerChanged(self, lyr):

        b = isinstance(lyr, QgsRasterLayer)

        for item in self.glViewWidget().items:
            self.glViewWidget().removeItem(item)


        if b:

            nb = lyr.bandCount()
            ns = lyr.width()
            nl = lyr.height()

            self.sliderX.setRange(1, ns)
            self.sliderY.setRange(1, nl)
            self.sliderZ.setRange(1, nb)

            self.spinBoxX.setRange(1, ns)
            self.spinBoxY.setRange(1, nl)
            self.spinBoxZ.setRange(1, nb)

            self.mCanvas.setLayers([lyr])
            self.mCanvas.setDestinationCrs(lyr.crs())
            self.mCanvas.setExtent(lyr.extent())

            if not isinstance(self.topPlaneRenderer(), QgsRasterRenderer):
                self.setTopPlaneRenderer(lyr.renderer())

            if not isSliceRenderer(self.sliceRenderer()):
                band = self.z()
                renderer = QgsSingleBandGrayRenderer(lyr.dataProvider(), band)
                self.setSliceRenderer(renderer)


            w = self.glViewWidget()

            box = gl.GLBoxItem(size=QVector3D(ns, nl, nb))
            box.translate(-ns/2, -nl/2, 0)
            self.addGLItem('BOX', box)

            self.glViewWidget().setCameraPosition(distance=nb+10, elevation=nb)

            #for i in w.items:
            #    w.removeItem(i)


            #g = gl.GLGridItem(color='w')
            #w.addItem(g)

        else:
            self.mCanvas.setLayers([])
            self.sliderX.setRange(0, 0)
            self.sliderY.setRange(0, 0)
            self.sliderZ.setRange(0, 0)

            self.spinBoxX.setRange(0, 0)
            self.spinBoxY.setRange(0, 0)
            self.spinBoxZ.setRange(0, 0)

            b = False


        for w in [self.gbRendering, self.gbSlicing, self.gbPlot]:
            w.setEnabled(b)

        self.onValidate()

    def setRasterLayer(self, lyr:QgsRasterLayer):

        if isinstance(lyr, QgsRasterLayer):
            if lyr != self.rasterLayer():
                QgsProject.instance().addMapLayer(lyr)
                self.mMapLayerComboBox.setLayer(lyr)

        if lyr is None:
            self.mMapLayerComboBox.setLayer(None)

