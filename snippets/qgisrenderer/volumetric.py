# -*- coding: utf-8 -*-
"""
Demonstrates GLVolumeItem for displaying volumetric data.

"""
import os, sys, re, pickle, enum, time
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

KEY_DEFAULT_TRANSFORM = 'CUBEVIEW/DEFAULT_TRANSFORM'
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



def qaRed(array:np.ndarray)->np.ndarray:
    return (array >> 16) & 0xff

def qaGreen(array:np.ndarray)->np.ndarray:
    return (array >> 8) & 0xff

def qaBlue(array:np.ndarray)->np.ndarray:
    return array & 0xff

def qaAlpha(array:np.ndarray)->np.ndarray:
    return array >> 24


class CubeViewWidget(GLViewWidget):

    def __init__(self, *args, **kwds):
        super(CubeViewWidget, self).__init__(*args, *kwds)

        self.mTextLabels = []

    def addTextLabel(self, pos:QVector3D, text:str, color=QColor('white')):
        assert isinstance(text, str)
        self.mTextLabels.append((pos, text, color))
    def paintGL(self, *args, **kwds):
        GLViewWidget.paintGL(self, *args, **kwds)

        #from OpenGL.GL import glEnable, glDisable, GL_DEPTH_TEST
        #glEnable(GL_DEPTH_TEST)
        for (pos, text, color) in self.mTextLabels:
            self.qglColor(color)
            assert isinstance(pos, QVector3D)
            self.renderText(pos.x(), pos.y(), pos.z(), text)
        #glDisable(GL_DEPTH_TEST)

        dist = self.opts['distance']
        elev = self.opts['elevation']
        azim = self.opts['azimuth']

        info = 'dist: {} elev: {} azim: {}'.format(dist, elev, azim)
        self.renderText(0,10, info)
        c = self.opts['center']
        info = 'Center: {} {} {}'.format(c.x(), c.y(), c.z())
        self.renderText(0, 20, info)

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
        t0 = time.time()
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

        if job.id() == 'CUBE':
            ext = lyr.extent()
            w = lyr.width()
            h = lyr.height()
            lyr.setRenderer(renderer)
            if True:
                w = min(w, 500)
                h = min(h, 500)
            if isinstance(renderer, QgsSingleBandGrayRenderer):
                setBand = renderer.setGrayBand
            elif isinstance(renderer, QgsSingleBandPseudoColorRenderer):
                setBand = renderer.setBand
            elif isinstance(renderer, QgsSingleBandColorDataRenderer):
                setBand = lambda *args : None
            elif isinstance(renderer, QgsMultiBandColorRenderer):
                setBand = lambda *args : None
            # x, y, z, RGBA
            rgba = np.empty((h,w, nb, 4), dtype=np.uint8)

            for b in range(nb):
                setBand(b + 1)

                block = renderer.block(0, ext, w, h)

                assert isinstance(block, QgsRasterBlock)
                assert block.isValid()
                assert block.dataType() != Qgis.UnknownDataType

                colorArray = np.frombuffer(block.data(), dtype=QGIS2NUMPY_DATA_TYPES[block.dataType()])

                rgba[:,:, b, 0] = qaRed(colorArray).reshape((h, w))  # np.asarray([qRed(c) for c in colorArray])
                rgba[:,:, b, 1] = qaGreen(colorArray).reshape((h, w))  # np.asarray([qGreen(c) for c in colorArray])
                rgba[:,:, b, 2] = qaBlue(colorArray).reshape((h, w)) # np.asarray([qBlue(c) for c in colorArray])
                rgba[:,:, b, 3] = qaAlpha(colorArray).reshape((h, w))  # np.asarray([qAlpha(c) for c in colorArray])

            rgba = np.rot90(rgba, axes=(0,1))
            #rgba = np.flip(rgba, axis=2)
            #rgba = np.flip(rgba, axis=1)
            job.setRGBA3D(rgba)

        elif job.id() == 'TOPPLANE':
            lyr.setRenderer(renderer)
            ext = lyr.extent()
            w = lyr.width()
            h = lyr.height()

            if True:
                w = min(w, 1024)
                h = min(h, 1024)

            block = renderer.block(1, ext, w, h)
            assert isinstance(block, QgsRasterBlock)
            colorArray = np.frombuffer(block.data(), dtype=QGIS2NUMPY_DATA_TYPES[block.dataType()])

            rgba = np.empty((h, w, 4), dtype=np.ubyte)

            rgba[..., 0] = qaRed(colorArray).reshape((h,w)) #np.asarray([qRed(c) for c in colorArray])
            rgba[..., 1] = qaGreen(colorArray).reshape((h,w)) #np.asarray([qGreen(c) for c in colorArray])
            rgba[..., 2] = qaBlue(colorArray).reshape((h,w)) #np.asarray([qBlue(c) for c in colorArray])
            rgba[..., 3] = qaAlpha(colorArray).reshape((h,w)) #np.asarray([qAlpha(c) for c in colorArray])

            rgba = np.rot90(rgba, axes=(0,1))
            job.setRGBA2D(rgba)



        elif job.hasSlicing():
            if isinstance(renderer, QgsSingleBandGrayRenderer):
                setBand = renderer.setGrayBand
            elif isinstance(renderer, QgsSingleBandPseudoColorRenderer):
                setBand = renderer.setBand
            elif isinstance(renderer, QgsSingleBandColorDataRenderer):
                setBand = lambda *args : None
            elif isinstance(renderer, QgsMultiBandColorRenderer):
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

                rgba[..., 0] = qaRed(colorArray).reshape((h, w))  # np.asarray([qRed(c) for c in colorArray])
                rgba[..., 1] = qaGreen(colorArray).reshape((h, w))  # np.asarray([qGreen(c) for c in colorArray])
                rgba[..., 2] = qaBlue(colorArray).reshape((h, w))  # np.asarray([qBlue(c) for c in colorArray])
                rgba[..., 3] = qaAlpha(colorArray).reshape((h, w))  # np.asarray([qAlpha(c) for c in colorArray])

                job.setRGBA2D(rgba)

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

                    rgba[:, b, 0] = qaRed(colorArray)
                    rgba[:, b, 1] = qaGreen(colorArray)
                    rgba[:, b, 2] = qaBlue(colorArray)
                    rgba[:, b, 3] = qaAlpha(colorArray)

                job.setRGBA2D(rgba)

        if job.rgba2D() is not None or job.rgba3D() is not None:
            results.append(job)
            print('TIME JOB {} {}'.format(job.id(), time.time()-t0))

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
        self.mRGBA2D = None
        self.mRGBA3D = None

        self.mOffset = QVector3D(0,0,0)
        self.mScale = (1, 1, 1)


    def __eq__(self, other)->bool:
        if not isinstance(other, RenderJob):
            return False
        else:
            return self.mID == other.mID and \
                   self.mUri == other.mUri and \
                   self.mRendererXML == other.mRendererXML
    def __hash__(self):
        return hash((self.mID, self.mUri, self.mRendererXML))

    def id(self)->str:
        return self.mID
    def rasterLayer(self)->QgsRasterLayer:
        return QgsRasterLayer(self.mUri, self.mID, self.mDataProvider)

    def renderer(self)->QgsRasterRenderer:
        return rendererFromXml(self.mRendererXML)

    def setRGBA2D(self, array:np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.ndim == 3
        assert array.shape[2] == 4
        self.mRGBA2D = array

    def rgba2D(self)->np.ndarray:
        return self.mRGBA2D

    def setRGBA3D(self, array:np.ndarray):
        assert isinstance(array, np.ndarray)
        assert array.ndim == 4
        assert array.shape[3] == 4
        self.mRGBA3D = array

    def rgba3D(self)->np.ndarray:
        return self.mRGBA3D

pathUi = os.path.join(os.path.dirname(__file__), 'volumetric_gui.ui')
class VolumetricWidget(QWidget, loadUIFormClass(pathUi)):

    def __init__(self, *args, **kwds):

        super(VolumetricWidget, self).__init__(*args, **kwds)

        self.setupUi(self)

        self.mCanvas = QgsMapCanvas()
        self.mCanvas.setVisible(False)

        self.mSliceRenderer = None
        self.mTopPlaneRenderer = None

        self.mBandScaleFactor = 1

        self.mRGBATopPlane = None
        self.mRGBACube = None

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

        self.sliderX.valueChanged.connect(lambda : self.setSlice('x'))
        self.sliderY.valueChanged.connect(lambda : self.setSlice('y'))
        self.sliderZ.valueChanged.connect(lambda : self.setSlice('z'))
        self.sliderZScale.valueChanged.connect(self.onZScaleChanged)

        self.cbShowTopPlane.clicked.connect(lambda b: self.setGLItemVisbility('TOPPLANE', b))
        self.cbShowSliceX.clicked.connect(lambda b: self.setGLItemVisbility('SLICE_X', b))
        self.cbShowSliceY.clicked.connect(lambda b: self.setGLItemVisbility('SLICE_Y', b))
        self.cbShowSliceZ.clicked.connect(lambda b: self.setGLItemVisbility('SLICE_Z', b))
        self.cbShowBox.clicked.connect(lambda b: self.setGLItemVisbility('BOX', b))
        self.cbShowCube.clicked.connect(lambda b: self.setGLItemVisbility('CUBE', b))
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

    def addGLItems(self, key, items):

        if not isinstance(items, list):
            items = [items]
        itemsOld = self.mGLItems.get(key, [])

        wasVisible = None

        for item in itemsOld:
            if item in self.glViewWidget().items:
                if wasVisible is None:
                    wasVisible = item.visible()
                    for itemNew in items:
                        itemNew.setVisible(wasVisible)

                self.glViewWidget().removeItem(item)

        self.mGLItems[key] = items
        for item in items:
            self.glViewWidget().addItem(item)

    def resetGLView(self):
        distance = self.mDefaultCAM['distance']
        elevation = self.mDefaultCAM['elevation']
        azimuth = self.mDefaultCAM['azimuth']
        if True:
            nb, nl, ns = self.layerDims()

            if ns is None:
                ns = nl = nb = 1
            center = QVector3D(0.5 * ns, -0.5 * nl, -0.5 * nb)
            elevation = 22 #°
            azimuth = -66
            self.glViewWidget().opts['center'] = center
            self.glViewWidget().update()
            distance = center.length()*5

        self.glViewWidget().setCameraPosition(distance=distance, elevation=elevation, azimuth=azimuth)

    def layerDims(self)->tuple:
        lyr = self.rasterLayer()
        if isinstance(lyr, QgsRasterLayer):
            ns = lyr.width()
            nl = lyr.height()
            nb = lyr.bandCount()
            return (nb, nl, ns)
        else:
            return (None, None, None)

    def cubeDims(self)->tuple:
        """
        Returns the cube dimensions in (nb, nl, ns) order
        :return:
        """
        if isinstance(self.mRGBACube, np.ndarray):
            nns, nnl, nnb = self.mRGBACube.shape[0:3]
            return nnb, nnl, nns
        else:
            return (None, None, None)

    def topPlaneDims(self)->tuple:
        """
        Returns the TOPPLANE dimensions as (nl, ns)
        :return: tuple
        """
        if isinstance(self.mRGBATopPlane, np.ndarray):
            return self.mRGBATopPlane.shape[0:3]
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
            if isinstance(r, QgsRasterRenderer):
                lyr2.setRenderer(r)
            showLayerPropertiesDialog(lyr2, None)
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
        assert isinstance(renderer, QgsRasterRenderer)
        self.mSliceRenderer = renderer.clone()

    def setTopPlaneRenderer(self, renderer:QgsRasterRenderer):
        self.mTopPlaneRenderer = renderer.clone()

    def onLoadData(self):

        config = self.config()
        self.mLastConfig = config

        lyr = self.rasterLayer()

        jobTop = RenderJob('TOPPLANE', lyr, self.topPlaneRenderer())
        jobCube = RenderJob('CUBE', lyr, self.sliceRenderer())

        #jobX = RenderJob('SLICE_X', lyr, self.sliceRenderer())
        #jobX.setSlicing('x', self.x())

        #jobY = RenderJob('SLICE_Y', lyr, self.sliceRenderer())
        #jobY.setSlicing('y', self.y())

        #jobZ = RenderJob('SLICE_Z', lyr, self.sliceRenderer())
        #jobZ.setSlicing('z', self.z())



        #jobList = [jobTop, jobX, jobY, jobZ]
        jobList = [jobCube, jobTop]

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

        for item in self.mGLItems.get(key, []):
            if isinstance(item, GLGraphicsItem):
                item.setVisible(b)
            else:
                raise Exception('No a GLGraphicsItem')
        s = ""

    def glItemVisibility(self, key:str)->bool:
        if key == 'CUBE':
            return self.cbShowCube.isChecked()
        elif key == 'SLICE_X':
            return self.cbShowSliceX.isChecked()
        elif key == 'SLICE_Y':
            return self.cbShowSliceY.isChecked()
        elif key == 'SLICE_Z':
            return self.cbShowSliceZ.isChecked()
        elif key == 'TOPPLANE':
            return self.cbShowTopPlane.isChecked()
        elif key == 'BOX':
            return self.cbShowBox.isChecked()
        return False

    def glViewWidget(self)->CubeViewWidget:
        return self.openglWidget

    def onDataLoaded(self, dump):

        joblist = pickle.loads(dump)
        n = len(joblist)
        for i, job in enumerate(joblist):

            assert isinstance(job, RenderJob)
            print('Add {}'.format(job.id()))
            nb, nl, ns = self.layerDims()

            if job.id() == 'CUBE':
                self.setRGBACube(job.rgba3D())
            elif job.id() == 'TOPPLANE':
                self.setRGBATopPlane(job.rgba2D())
            continue
            #box = gl.GLBoxItem(size=QVector3D(ns, nl, nb))
            #box.translate(-ns/2, -nl/2, 0)
            #v1.scale(1./ns, 1./nl, 1./nb)
            #v1.translate(-shape[1] / 2, -shape[2] / 2, 0)
            #default: xy plane
            #elif job.id().startswith('SLICE'):
            """
                rgba = job.rgba2D()
                nnl, nns = rgba.shape[0:2]
                v1 = gl.GLImageItem(rgba)

                if job.sliceDim() == 'z':
                    v1.scale(ns / nns, nl / nnl, 1)
                    v1.translate(-ns / 2, -nl / 2, job.sliceIndex())
                    v1.rotate(-90, 0, 0, 1)
                    #v1.translate(-ns / 2, -nl / 2, )

                elif job.sliceDim() == 'x':
                    rgba = job.rgba2D()
                    nnl, nns = rgba.shape[0:2]
                    v1 = gl.GLImageItem(rgba)
                    v1.scale(ns / nns, 1, 1)
                    v1.rotate(90, 0, 0, 1)
                    v1.rotate(-90, 0, 1, 0)
                    v1.translate((-ns + job.sliceIndex()) / 2, -nl / 2, nb)


                elif job.sliceDim() == 'y':
                    rgba = job.rgba2D()
                    nnl, nns = rgba.shape[0:2]
                    v1 = gl.GLImageItem(rgba)
                    v1.scale(1, nl / nnl, 1)
                    v1.translate(-ns / 2, -nl / 2, nb)
                    v1.rotate(-90, 1, 0, 0)

                self.addGLItems(job.id(), v1)


            #w = self.glViewWidget()
           # b = gl.GLBoxItem()
           # w.addItem(b)

            #ax2 = gl.GLAxisItem()
            #ax2.setParentItem(b)

            #b.translate(1, 1, 1)

            #,ä nw.addItem(v1)
            """
    def onValidate(self)->bool:

        b = True
        b &= isinstance(self.topPlaneRenderer(), QgsRasterRenderer)
        b &= isinstance(self.sliceRenderer(), QgsRasterRenderer)
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


    def setRGBATopPlane(self, rgba:np.ndarray):
        pass

    def setRGBACube(self, rgba:np.ndarray):

        assert isinstance(rgba, np.ndarray)
        assert rgba.ndim == 4
        assert rgba.shape[3] == 4
        assert rgba.dtype == np.uint8

        t0 = time.time()

        self.mRGBACube = rgba

        # layer and cube dimensions
        nb, nl, ns = self.layerDims()
        nnb, nnl, nns = self.cubeDims()

        # scaling factors (in case we sampled less/more pixels than in the layer)
        sx, sy, sb = ns / nns, nl / nnl, nb / nnb

        #x = x2*sx
        if False:
            items = []
            isVisible = self.glItemVisibility('CUBE')
            stepX = stepY = stepZ = 100
            for x in range(0, nns, stepX):
                x2 = min(x + stepX, nns)
                for y in range(0, nnl, stepY):
                    y2 = min(y + stepY, nnl)
                    for z in range(0, nnb, stepZ):
                        z2 = min(z + stepZ, nnb)
                        block = rgba[x:x2, y:y2, z:z2, :]
                        # do not plot empty blocks
                        if np.all(block == 0):
                            continue
                        item = gl.GLVolumeItem(block, sliceDensity=1, smooth=False)
                        item.scale(sx, sy, sb)
                        item.rotate(180, 1, 0, 0)
                        item.setVisible(isVisible)
                        item.translate(x*sx, y*sy, z*sb)
                        item.setProperty(KEY_DEFAULT_TRANSFORM, item.transform())
                        items.append(item)

            # apply zScale
            z = self.zScale()
            for item in items:
                assert isinstance(item, GLGraphicsItem)
                item.scale(1,1,z)

            self.addGLItems('CUBE', items)

            print('TIME CUBE {}  {}'.format(time.time() - t0, rgba.shape))

        self.setSlice('x')
        self.setSlice('y')
        self.setSlice('z')

    def setSlice(self, dim:str):
        assert dim in ['x','y','z']

        t0 = time.time()
        nb, nl, ns = self.layerDims()
        nnb, nnl, nns = self.cubeDims()

        if nb is None or nnb is None:
            return
        # scaling factors (in case we sampled less/more pixels than in the layer)
        sx, sy, sb = ns / nns, nl / nnl, nb / nnb

        # slice subset
        z1, y1, x1 = nnb, nnl, nns
        x0 = y0 = z0 = 0

        if dim == 'x':
            x0 = self.x()-1
            x1 = x0 + 1
        elif dim == 'y':
            y0 = self.y()-1
            y1 = y0 + 1
        elif dim == 'z':
            z0 = self.z()-1
            z1 = z0 + 1

        sliceData = self.mRGBACube[x0:x1, y0:y1, z0:z1, :]
        items = []
        isVisible = self.glItemVisibility('CUBE')

        if True: #volumentric
            stepX = stepY = stepZ = 500
            shp = sliceData.shape
            for x in range(0, shp[0], stepX):
                x2 = min(x + stepX, shp[0])

                for y in range(0, shp[1], stepY):
                    y2 = min(y + stepY, shp[1])

                    for z in range(0, shp[2], stepZ):
                        z2 = min(z + stepZ, shp[2])
                        block = sliceData[x:x2, y:y2, z:z2, :]

                        # do not plot empty blocks
                        if np.all(block == 0):
                            continue

                        item = gl.GLVolumeItem(block, sliceDensity=1, smooth=False)
                        item.scale(sx, sy, sb)
                        item.setVisible(isVisible)
                        item.translate((x+x0)*sx, -(y+y0)*sy, -(z+z0)*sb)
                        item.setProperty(KEY_DEFAULT_TRANSFORM, item.transform())
                        items.append(item)

            # apply zScale
            z = self.zScale()
            for item in items:
                assert isinstance(item, GLGraphicsItem)
                item.scale(1, 1, z)

            self.addGLItems('SLICE_{}'.format(dim.upper()), items)

        print('SLICE {}  {}'.format(dim, time.time() - t0))

    def zScale(self)->int:
        return int(self.sliderZScale.value())

    def setZSCale(self, z:int):
        self.sliderZScale.setValue(z)

    def onZScaleChanged(self):
        z = self.zScale()
        for key, items in self.mGLItems.items():
            for item in items:
                assert isinstance(item, GLGraphicsItem)
                tranformDefault = item.property(KEY_DEFAULT_TRANSFORM)
                if isinstance(tranformDefault, QMatrix4x4):
                    item.setTransform(tranformDefault)
                    item.scale(1,1,z) #scale will update the item

    def onLayerChanged(self, lyr):

        b = isinstance(lyr, QgsRasterLayer)

        for item in self.glViewWidget().items:
            self.glViewWidget().removeItem(item)


        if b:

            nb = lyr.bandCount()
            ns = lyr.width()
            nl = lyr.height()

            minEdge = 0.1 * min(ns, nl)

            if nb < minEdge:
                self.mBandScaleFactor = minEdge / nb
            else:
                self.mBandScaleFactor = 1


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

            if not isinstance(self.sliceRenderer(), QgsRasterRenderer):
                band = self.z()
                band = 1

                if False:
                    stats = lyr.dataProvider().bandStatistics(band, QgsRasterBandStats.Min | QgsRasterBandStats.Max)
                    minValue = stats.minimumValue
                    maxValue = stats.maximumValue


                    # create shader for the renderer
                    shader = QgsRasterShader(minValue, maxValue)
                    colorRampShaderFcn = QgsColorRampShader(minValue, maxValue)
                    colorRampShaderFcn.setColorRampType(QgsColorRampShader.Interpolated)
                    colorRampShaderFcn.setClassificationMode(QgsColorRampShader.Continuous)
                    colorRampShaderFcn.setClip(True)

                    items = []
                    for index in range(10):
                        items.append(QgsColorRampShader.ColorRampItem(index, QColor('#{0:02d}{0:02d}{0:02d}'.format(index)),
                                                                      "{}".format(index)))
                    colorRampShaderFcn.setColorRampItemList(items)
                    shader.setRasterShaderFunction(colorRampShaderFcn)
                    # create instance to test
                    rasterRenderer = QgsSingleBandPseudoColorRenderer(lyr.dataProvider(), band, shader)
                    #lyr.setRenderer(rasterRenderer)

                else:
                    l2 = QgsRasterLayer(lyr.source())
                    renderer = QgsSingleBandGrayRenderer(l2.dataProvider(), band)
                    l2.setRenderer(renderer)
                    l2.setContrastEnhancement(
                        QgsContrastEnhancement.StretchToMinimumMaximum,
                        QgsRasterMinMaxOrigin.MinMax)

                    self.setSliceRenderer(l2.renderer().clone())


            w = self.glViewWidget()

            box = gl.GLBoxItem(size=QVector3D(ns, -nl, -nb))
            #box.translate(0, 0, nb)
            box.setProperty(KEY_DEFAULT_TRANSFORM, box.transform())
            box.scale(1,1,self.zScale())
            self.addGLItems('BOX', box)

            ax = gl.GLAxisItem(size=QVector3D(ns, -nl, -nb))

            #ax.translate(0, nl, nb)
            #ax.rotate(180, 0, 1, 0)
            ax.setProperty(KEY_DEFAULT_TRANSFORM, ax.transform())
            ax.scale(1,1,self.zScale())
            self.addGLItems('AXIS', ax)

            #w = self.glViewWidget()
            #w.mTextLabels.clear()
            #w.addTextLabel(QVector3D(0, 0, 0), 'Bands')
            #w.addTextLabel(QVector3D(0, nl+1, nb), 'Lines')
            #w.addTextLabel(QVector3D(ns+1, 0, nb), 'Columns')

            self.resetGLView()

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
            self.mBandScaleFactor = 1

        for w in [self.gbRendering, self.gbPlotting]:
            w.setEnabled(b)

        self.onValidate()

    def setRasterLayer(self, lyr:QgsRasterLayer):

        if isinstance(lyr, QgsRasterLayer):
            if lyr != self.rasterLayer():
                QgsProject.instance().addMapLayer(lyr)
                self.mMapLayerComboBox.setLayer(lyr)

        if lyr is None:
            self.mMapLayerComboBox.setLayer(None)

