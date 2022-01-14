# -*- coding: utf-8 -*-

"""
***************************************************************************

    ---------------------
    Date                 : 30.11.2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin jakimow at geo dot hu-berlin dot de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import datetime
import math
# noinspection PyPep8Naming
import os
import pathlib
import time
import unittest
import numpy as np
import xmlrunner
from PyQt5.QtCore import QVariant
from osgeo import ogr, gdal

from qgis.PyQt.QtCore import QSize, QMimeData, QUrl, QPoint, Qt
from qgis.PyQt.QtGui import QDropEvent
from qgis.PyQt.QtWidgets import QCheckBox, QProgressDialog, QApplication, QToolBar, QVBoxLayout, QPushButton, \
    QToolButton, QAction, QComboBox, QWidget, QDialog
from qgis.core import QgsApplication, QgsProject, QgsRasterLayer, QgsVectorLayer, QgsField, QgsWkbTypes, \
    QgsActionManager
from qgis.gui import QgsOptionsDialogBase, QgsSearchWidgetWrapper, QgsMapCanvas, \
    QgsDualView, QgsGui
from qps.layerproperties import AddAttributeDialog
from qps.plotstyling.plotstyling import PlotStyle
from qps.speclib import FIELD_VALUES
from qps.speclib.core import profile_field_list, is_spectral_library
from qps.speclib.core.spectrallibrary import defaultCurvePlotStyle, SpectralLibrary
from qps.speclib.core.spectralprofile import SpectralProfile
from qps.speclib.gui.spectrallibraryplotwidget import SpectralProfilePlotDataItem, \
    SpectralProfilePlotWidget, SpectralLibraryPlotWidgetStyleWidget, \
    SpectralLibraryPlotWidget, SpectralProfilePlotXAxisUnitModel
from qps.speclib.gui.spectrallibrarywidget import SpectralLibraryWidget, SpectralLibraryPanel
from qps.speclib.gui.spectralprofileeditor import SpectralProfileTableModel, SpectralProfileEditorWidget, \
    SpectralProfileEditorWidgetWrapper, SpectralProfileEditorConfigWidget, SpectralProfileEditorWidgetFactory, \
    registerSpectralProfileEditorWidget
from qps.testing import TestObjects, TestCase, StartOptions
from qps.unitmodel import UnitConverterFunctionModel, BAND_NUMBER
from qps.utils import setToolButtonDefaultActionMenu, METRIC_EXPONENTS
from qpstestdata import enmap, hymap


class TestSpeclibWidgets(TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwds) -> None:

        options = StartOptions.All

        super(TestSpeclibWidgets, cls).setUpClass(*args, options=options)

        from qps import initAll
        initAll()

        gdal.UseExceptions()
        gdal.PushErrorHandler(TestSpeclibWidgets.gdal_error_handler)
        ogr.UseExceptions()

    @staticmethod
    def gdal_error_handler(err_class, err_num, err_msg):
        errtype = {
            gdal.CE_None: 'None',
            gdal.CE_Debug: 'Debug',
            gdal.CE_Warning: 'Warning',
            gdal.CE_Failure: 'Failure',
            gdal.CE_Fatal: 'Fatal'
        }
        err_msg = err_msg.replace('\n', ' ')
        err_class = errtype.get(err_class, 'None')
        print('Error Number: %s' % (err_num))
        print('Error Type: %s' % (err_class))
        print('Error Message: %s' % (err_msg))

    def setUp(self):
        super().setUp()
        reg = QgsGui.editorWidgetRegistry()
        if len(reg.factories()) == 0:
            reg.initEditors()

        registerSpectralProfileEditorWidget()
        from qps import registerEditorWidgets
        registerEditorWidgets()

        from qps import registerMapLayerConfigWidgetFactories
        registerMapLayerConfigWidgetFactories()

    def tearDown(self):
        super().tearDown()
        QApplication.processEvents()

    @classmethod
    def tearDownClass(cls):
        super(TestSpeclibWidgets, cls).tearDownClass()

    @unittest.skipIf(False, '')
    def test_PyQtGraphPlot(self):
        import qps.externals.pyqtgraph as pg
        # pg.systemInfo()

        plotWidget = pg.plot(title="Three plot curves")

        item1 = pg.PlotItem(x=[1, 2, 3], y=[2, 3, 4], color='white')
        plotWidget.plotItem.addItem(item1)
        self.assertIsInstance(plotWidget, pg.PlotWidget)

        self.showGui(plotWidget)

    @unittest.skipIf(False, '')
    def test_SpectraLibraryPlotDataItem(self):

        profile = SpectralProfile()
        self.assertIsInstance(profile, SpectralProfile)
        import numpy as np
        yValues = np.asarray(
            [700., np.nan, 954.0, 1714.0, 1584.0, 1771.0, np.nan, 2302.0, np.nan, 1049.0, 2670.0, np.nan, 800.])
        xValues = np.asarray([0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1])

        profile.setValues(xValues, yValues)

        yValues = profile.yValues()
        xValues = profile.xValues()

        self.assertTrue(any([math.isnan(v) for v in yValues]))

        print('plot {}'.format(yValues))
        # w0 = pg.plot(yValues, connect='finite')

        pdi = SpectralProfilePlotDataItem()

        self.assertIsInstance(pdi, SpectralProfilePlotDataItem)

        style = PlotStyle.fromPlotDataItem(pdi)

        plotStyle = defaultCurvePlotStyle()
        plotStyle.setLineWidth(10)
        plotStyle.setLineColor('red')
        plotStyle.setMarkerColor('green')
        plotStyle.setMarkerLinecolor('blue')
        plotStyle.setMarkerSymbol('Triangle')
        plotStyle.apply(pdi)

        ps2 = PlotStyle.fromPlotDataItem(pdi)
        self.assertEqual(plotStyle, ps2)

        w1 = profile.plot()
        w2 = pdi.plot()
        self.showGui([w1])

    def test_SpectralLibraryPlotTemporalProfiles(self):

        speclib = SpectralLibrary()

        sp1 = SpectralProfile()
        xvalues = np.datetime64('2012-08-15T15') + np.arange(255)
        yvalues = np.arange(len(xvalues))
        sp1.setValues(x=xvalues, y=yvalues, xUnit='DateTime')

        sp2 = SpectralProfile()
        sp2.setValues(x=[230, 240], y=[3, 2], xUnit='DOY')

        sp3 = SpectralProfile()
        sp3.setValues(x=[340, 380], y=[4, 4], xUnit='nm')

        self.assertTrue(speclib.startEditing())
        speclib.addProfiles([sp1, sp2, sp3])
        self.assertTrue(speclib.commitChanges())
        w = SpectralLibraryWidget(speclib=speclib)
        self.showGui(w)

    def test_SpectralLibraryPlotWidget(self):
        speclib = TestObjects.createSpectralLibrary()
        from qps.speclib.gui.spectrallibraryplotwidget import SpectralLibraryPlotWidget
        from qps.resources import ResourceBrowser
        w = SpectralLibraryPlotWidget()
        rb = ResourceBrowser()

        self.showGui([w, rb])

    def test_UnitConverterFunctionModel(self):

        m = UnitConverterFunctionModel()

        v = np.asarray([100, 200, 300])

        for dst in ['um', 'μm', u'μm']:
            f = m.convertFunction('nm', dst)
            r = f(v, 'X')
            self.assertListEqual(list(r), [0.1, 0.2, 0.3], msg='Failed to convert from nm to {}'.format(dst))

        r = m.convertFunction('nm', 'nm')(v, 'X')
        self.assertListEqual(list(r), [100, 200, 300])

    def test_SpectralLibraryPlotWidget_units(self):

        slib = SpectralLibrary()

        p1 = SpectralProfile()
        p2 = SpectralProfile()

        p1.setValues(x=[.1, .2, .3, .4], y=[20, 30, 40, 30], xUnit='um')
        p2.setValues(x=[100, 200, 300, 400], y=[21, 31, 41, 31], xUnit='nm')
        slib.startEditing()
        slib.addProfiles([p1, p2])
        slib.commitChanges()
        dualView = QgsDualView()
        canvas = QgsMapCanvas()
        dualView.init(slib, canvas)

        pw = SpectralLibraryPlotWidget()
        pw.setDualView(dualView)

        self.showGui(pw)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPlotColorSchemeWidget(self):

        w = SpectralLibraryPlotWidgetStyleWidget()
        self.assertIsInstance(w, SpectralLibraryPlotWidgetStyleWidget)
        self.showGui(w)

    @unittest.skipIf(False, '')
    def test_SpectralProfileValueTableModel(self):

        speclib = TestObjects.createSpectralLibrary()
        p3 = speclib[2]
        self.assertIsInstance(p3, SpectralProfile)

        xUnit = p3.xUnit()
        yUnit = p3.yUnit()

        if yUnit is None:
            yUnit = '-'
        if xUnit is None:
            xUnit = '-'

        m = SpectralProfileTableModel()

        self.assertIsInstance(m, SpectralProfileTableModel)
        self.assertTrue(m.rowCount() == 0)
        # self.assertTrue(m.columnCount() == 2)
        self.assertEqual('x', m.headerData(0, orientation=Qt.Horizontal, role=Qt.DisplayRole))
        self.assertEqual('y', m.headerData(1, orientation=Qt.Horizontal, role=Qt.DisplayRole))

        m.setProfile(p3)
        self.assertTrue(m.rowCount() == len(p3.xValues()))
        self.assertEqual('x'.format(yUnit), m.headerData(0, orientation=Qt.Horizontal, role=Qt.DisplayRole))
        self.assertEqual('y'.format(xUnit), m.headerData(1, orientation=Qt.Horizontal, role=Qt.DisplayRole))

        # m.setColumnValueUnit(0, '')

    @unittest.skipIf(False, '')
    def test_SpectralProfileEditorWidget(self):

        self.assertIsInstance(QgsApplication.instance(), QgsApplication)
        SLIB = TestObjects.createSpectralLibrary()
        self.assertIsInstance(SLIB, SpectralLibrary)
        w = SpectralProfileEditorWidget()
        self.assertIsInstance(w, QWidget)

        p = SLIB[-1]
        w.setProfile(p)

        self.showGui(w)
        self.assertTrue(True)

    @unittest.skipIf(False, '')
    def test_toolbarStackedActions(self):

        tb = QToolBar()
        a1 = tb.addAction('Action1')
        a2 = tb.addAction('ActionA2')

        a21 = QAction('A2.1')
        a22 = QAction('A2.2')
        a22.setCheckable(True)

        setToolButtonDefaultActionMenu(a2, [a21, a22])

        btn2 = tb.findChildren(QToolButton)[2]
        self.assertIsInstance(btn2, QToolButton)

        self.showGui(tb)

    def test_UnitComboBox(self):

        cb = QComboBox()
        model = SpectralProfilePlotXAxisUnitModel()
        for k in METRIC_EXPONENTS.keys():
            model.addUnit(k)

        cb.setModel(model)

        self.showGui(cb)

    @unittest.skipIf(False, '')
    def test_SpectralProfileEditorWidgetFactory(self):

        reg = QgsGui.editorWidgetRegistry()
        if len(reg.factories()) == 0:
            reg.initEditors()

        from qps.speclib import EDITOR_WIDGET_REGISTRY_KEY
        self.assertTrue(EDITOR_WIDGET_REGISTRY_KEY in reg.factories().keys())
        factory = reg.factories()[EDITOR_WIDGET_REGISTRY_KEY]
        self.assertIsInstance(factory, SpectralProfileEditorWidgetFactory)

        vl = TestObjects.createSpectralLibrary()

        am = vl.actions()
        self.assertIsInstance(am, QgsActionManager)

        c = QgsMapCanvas()
        w = QWidget()
        w.setLayout(QVBoxLayout())

        print('STOP 1', flush=True)
        dv = QgsDualView()
        print('STOP 2', flush=True)
        dv.init(vl, c)
        print('STOP 3', flush=True)
        dv.setView(QgsDualView.AttributeTable)
        print('STOP 4', flush=True)
        dv.setAttributeTableConfig(vl.attributeTableConfig())
        print('STOP 5', flush=True)
        cb = QCheckBox()
        cb.setText('Show Editor')

        def onClicked(b: bool):
            if b:
                dv.setView(QgsDualView.AttributeEditor)
            else:
                dv.setView(QgsDualView.AttributeTable)

        cb.clicked.connect(onClicked)
        w.layout().addWidget(dv)
        w.layout().addWidget(cb)

        w.resize(QSize(300, 250))
        print(vl.fields().names())
        look = vl.fields().lookupField
        print('STOP 4', flush=True)
        parent = QWidget()
        configWidget = factory.configWidget(vl, look(FIELD_VALUES), None)
        self.assertIsInstance(configWidget, SpectralProfileEditorConfigWidget)

        self.assertIsInstance(factory.createSearchWidget(vl, 0, dv), QgsSearchWidgetWrapper)

        eww = factory.create(vl, 0, None, dv)
        self.assertIsInstance(eww, SpectralProfileEditorWidgetWrapper)
        self.assertIsInstance(eww.widget(), SpectralProfileEditorWidget)

        eww.valueChanged.connect(lambda v: print('value changed: {}'.format(v)))

        fields = vl.fields()
        vl.startEditing()
        value = eww.value()
        f = vl.getFeature(1)
        self.assertTrue(vl.updateFeature(f))

        self.showGui([w, configWidget])
        vl.commitChanges()

    @unittest.skipIf(TestCase.runsInCI(), 'unknown error. runs in single mode')
    def test_SpectralLibraryWidget_ClassFields(self):

        w = SpectralLibraryWidget()
        from qpstestdata import speclib_labeled
        sl = SpectralLibrary.readFrom(speclib_labeled)
        self.assertIsInstance(sl, QgsVectorLayer)
        self.assertTrue(len(sl) > 0)
        w.addSpeclib(sl)
        self.showGui(w)

    def test_dropping_speclibs(self):

        files = []

        for root, dirs, f in os.walk(pathlib.Path(__file__).parents[1] / 'qpstestdata'):
            for file in f:
                files.append(pathlib.Path(root) / file)

        slw = SpectralLibraryWidget()
        # drop a valid speclib
        md = QMimeData()
        from qpstestdata import speclib
        sl = SpectralLibrary.readFrom(speclib)
        self.assertIsInstance(sl, SpectralLibrary) and len(sl) > 0
        md.setUrls([QUrl.fromLocalFile(speclib)])
        event = QDropEvent(QPoint(0, 0), Qt.CopyAction, md, Qt.LeftButton, Qt.NoModifier)
        print('Drop {}'.format(speclib), flush=True)
        slw.dropEvent(event)
        self.assertEqual(len(slw.speclib()), len(sl))

        # drop random files
        slw = SpectralLibraryWidget()
        self.assertTrue(len(slw.speclib()) == 0)
        n = 0
        for file in files:
            n += 1
            if n >= 10:
                break
            md = QMimeData()
            md.setUrls([QUrl.fromLocalFile(file.as_posix())])
            print('# Drop {}'.format(file.name), flush=True)
            event = QDropEvent(QPoint(0, 0), Qt.CopyAction, md, Qt.LeftButton, Qt.NoModifier)
            slw.dropEvent(event)
            QApplication.processEvents()
            # delete dropped spectra
            slw.speclib().startEditing()
            slw.speclib().deleteFeatures(slw.speclib().allFeatureIds())
            slw.speclib().commitChanges()
            s = ""

        self.showGui(slw)

    def test_CurrentProfiles(self):

        w = SpectralLibraryWidget()

        def onClicked(*args):
            sl = TestObjects.createSpectralLibrary(2)
            w.setCurrentProfiles(sl[:])

        btnAddTempProfiles = QPushButton('Add Temp Profiles')
        btnAddTempProfiles.clicked.connect(onClicked)

        w2 = QWidget()
        l = QVBoxLayout()
        l.addWidget(btnAddTempProfiles)
        l.addWidget(w)
        w2.setLayout(l)
        self.showGui(w2)
        s = ""

    def test_SpectralLibraryWidget_ViewTypes(self):

        w = SpectralLibraryWidget()
        w.show()

        w.setViewVisibility(SpectralLibraryWidget.ViewType.Empty)
        self.assertFalse(w.mSpeclibPlotWidget.isVisible())
        self.assertFalse(w.pageProcessingWidget.isVisible())
        self.assertFalse(w.mMainView.isVisible())

        w.setViewVisibility(SpectralLibraryWidget.ViewType.ProcessingView)
        self.assertFalse(w.mSpeclibPlotWidget.isVisible())
        self.assertEqual(w.mMainView.view(), QgsDualView.AttributeTable)
        self.assertFalse(w.mMainView.isVisible())
        self.assertTrue(w.pageProcessingWidget.isVisible())

        w.setViewVisibility(SpectralLibraryWidget.ViewType.Standard)
        self.assertFalse(w.pageProcessingWidget.isVisible())
        self.assertTrue(w.mMainView.isVisible())
        self.assertEqual(w.mMainView.view(), QgsDualView.AttributeTable)
        self.assertTrue(w.mSpeclibPlotWidget.isVisible())
        self.assertTrue(w.mMainView.isVisible())

        w.setViewVisibility(SpectralLibraryWidget.ViewType.ProfileView)
        self.assertTrue(w.mSpeclibPlotWidget.isVisible())
        self.assertFalse(w.mMainView.isVisible())
        self.assertFalse(w.pageProcessingWidget.isVisible())

        self.showGui(w)

    def test_SpectralLibraryWidget_empty_vectorlayer(self):

        vl = TestObjects.createVectorLayer()

        slw = SpectralLibraryWidget(speclib=vl)
        self.assertTrue(not is_spectral_library(slw.speclib()))
        self.assertIsInstance(slw, SpectralLibraryWidget)
        self.showGui(slw)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryWidget(self):

        from qpstestdata import enmap, landcover, enmap_pixel

        l1 = QgsRasterLayer(enmap, 'EnMAP')
        l2 = QgsVectorLayer(landcover, 'LandCover')
        l3 = QgsVectorLayer(enmap_pixel, 'Points of Interest')
        QgsProject.instance().addMapLayers([l1, l2, l3])

        sl1 = TestObjects.createSpectralLibrary(5, wlu='Nanometers', n_bands=[177, 6])
        sl1.setName(' My Speclib')

        sl2 = TestObjects.createSpectralLibrary(3, wlu='Nanometers', n_bands=[177, 6])

        slw = SpectralLibraryWidget(speclib=sl1)

        sl1.startEditing()
        sl1.addSpeclib(sl2)

        profiles = TestObjects.spectralProfiles(4, fields=sl1.fields(), n_bands=[7, 12])
        slw.setCurrentProfiles(profiles)
        fids_a = sl1.allFeatureIds()
        # sl1.commitChanges()
        # fids_b = sl1.allFeatureIds()

        QgsProject.instance().addMapLayer(slw.speclib())

        self.assertEqual(slw.speclib(), sl1)
        self.assertIsInstance(slw.speclib(), SpectralLibrary)
        fieldNames = slw.speclib().fieldNames()
        self.assertIsInstance(fieldNames, list)

        cs = [sl1[0], sl1[3], sl1[-1]]
        l = len(sl1)
        self.assertTrue(slw.speclib() == sl1)

        # from qps.resources import ResourceBrowser
        # b = ResourceBrowser()

        self.showGui([slw])

    @unittest.skipIf(False, '')
    def test_SpectralLibraryPanel(self):

        sp = SpectralLibraryPanel()
        self.showGui(sp)

    @unittest.skipIf(False, '')
    def test_SpectralLibraryWidgetCanvas(self):

        # speclib = self.createSpeclib()

        lyr = QgsRasterLayer(hymap)
        h, w = lyr.height(), lyr.width()
        speclib = SpectralLibrary.readFromRasterPositions(enmap, [QPoint(0, 0), QPoint(w - 1, h - 1), QPoint(2, 2)])
        slw = SpectralLibraryWidget(speclib=speclib)

        QgsProject.instance().addMapLayers([lyr, slw.speclib()])

        canvas = QgsMapCanvas()

        canvas.setLayers([lyr, slw.speclib()])
        canvas.setDestinationCrs(slw.speclib().crs())
        canvas.setExtent(slw.speclib().extent())

        def setLayers():
            canvas.mapSettings().setDestinationCrs(slw.mCanvas.mapSettings().destinationCrs())
            canvas.setExtent(slw.canvas().extent())
            canvas.setLayers(slw.canvas().layers())

        slw.sigMapCenterRequested.connect(setLayers)
        slw.sigMapExtentRequested.connect(setLayers)

        self.showGui([canvas, slw])

    @unittest.skipIf(False, '')
    def test_editing(self):

        slib = TestObjects.createSpectralLibrary()
        self.assertTrue(len(slib) > 0)
        slw = SpectralLibraryWidget()
        slw.speclib().startEditing()
        slw.speclib().addSpeclib(slib)

        slw.mActionToggleEditing.setChecked(True)

        # self.assertTrue()
        self.showGui(slw)

    @unittest.skipIf(False, '')
    def test_speclibAttributeWidgets(self):

        speclib = TestObjects.createSpectralLibrary()

        slw = SpectralLibraryWidget(speclib=speclib)

        import qps.layerproperties
        propertiesDialog = qps.layerproperties.LayerPropertiesDialog(speclib, None)
        self.assertIsInstance(propertiesDialog, QgsOptionsDialogBase)
        self.showGui([slw, propertiesDialog])

    def test_addAttribute(self):

        slw = SpectralLibraryWidget()
        self.assertIsInstance(slw, SpectralLibraryWidget)
        sl = slw.speclib()
        self.assertIsInstance(sl, SpectralLibrary)
        sl.startEditing()

        attr = QgsField(name='test',
                        type=QVariant.Int,
                        typeName='Int')

        sl.addAttribute(attr)
        conf1 = sl.attributeTableConfig()
        conf2 = slw.mMainView.attributeTableConfig()

        self.assertEqual(len(conf1.columns()), len(conf2.columns()))
        names = []
        for c1, c2 in zip(conf1.columns(), conf2.columns()):
            self.assertEqual(c1.name, c2.name)
            self.assertEqual(c1.type, c2.type)
            self.assertEqual(c1.hidden, c2.hidden)
            names.append(c1.name)
        # self.assertTrue(attr.name() in names)
        s = ""

        self.showGui(slw)

    @unittest.skipIf(TestCase.runsInCI(), 'Runs in single mode but not batch more. Reason unknown')
    def test_SpectralLibraryWidgetThousands(self):

        import qpstestdata

        pathSL = os.path.join(os.path.dirname(qpstestdata.__file__), 'roberts2017_urban.sli')

        if True and os.path.exists(pathSL):
            t0 = datetime.datetime.now()

            speclib = SpectralLibrary.readFrom(pathSL)

            dt = datetime.datetime.now() - t0
            print('Reading required : {}'.format(dt))
        else:
            speclib = TestObjects.createSpectralLibrary(5000)

        t0 = datetime.datetime.now()

        w = SpectralLibraryWidget()
        w.addSpeclib(speclib)
        for field in profile_field_list(speclib):
            w.spectralLibraryPlotWidget().createProfileVis(field=field)
        dt = datetime.datetime.now() - t0
        print('Adding speclib required : {}'.format(dt))

        self.showGui(w)

    def test_delete_speclib(self):

        speclib = TestObjects.createSpectralLibrary(10)
        QgsProject.instance().addMapLayer(speclib)
        w = SpectralLibraryWidget(speclib=speclib)
        w.show()

        QgsProject.instance().removeAllMapLayers()

        assert w.speclib() is None

    def test_speclibImportSpeed(self):

        pathRaster = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapboxtestdata\enmap_berlin.bsq'
        # pathPoly = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapboxtestdata\landcover_berlin_polygon.shp'
        pathPoly = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapboxtestdata\landcover_berlin_point.shp'

        for p in [pathRaster, pathPoly]:
            if not os.path.isfile(p):
                return

        progressDialog = QProgressDialog()
        # progress_handler.show()
        vl = QgsVectorLayer(pathPoly)
        vl.setName('Polygons')
        rl = QgsRasterLayer(pathRaster)
        rl.setName('Raster Data')
        if not vl.isValid() and rl.isValid():
            return

        max_spp = 1  # seconds per profile

        def timestats(t0, sl, info='time'):
            dt = time.time() - t0
            spp = dt / len(sl)
            pps = len(sl) / dt
            print('{}: dt={}sec spp={} pps={}'.format(info, dt, spp, pps))
            return dt, spp, pps

        t0 = time.time()
        sl = SpectralLibrary.readFromVector(vl, rl, progress_handler=progressDialog)
        dt, spp, pps = timestats(t0, sl, info='read profiles')
        self.assertTrue(spp <= max_spp, msg='{} seconds per profile are too much!')

        self.assertTrue(progressDialog.value() == -1)
        t0 = time.time()
        sl.startEditing()
        sl.addSpeclib(sl)
        sl.commitChanges()
        dt, spp, pps = timestats(t0, sl, info='merge speclibs')
        self.assertTrue(spp <= max_spp, msg='too slow!')

        sl0 = SpectralLibrary()
        t0 = time.time()
        sl0.startEditing()
        sl0.addSpeclib(sl)
        dt, spp, pps = timestats(t0, sl, info='merge speclibs2')
        self.assertTrue(spp <= max_spp, msg='too slow!')

        w = SpectralLibraryWidget()

        t0 = time.time()
        w.addSpeclib(sl)

        dt = time.time() - t0

        QgsProject.instance().addMapLayers([vl, rl])
        w = SpectralLibraryWidget()
        self.showGui(w)

    def test_SpectralProfileImportPointsDialog(self):

        lyrRaster = QgsRasterLayer(enmap)
        lyrRaster.setName('EnMAP')
        h, w = lyrRaster.height(), lyrRaster.width()

        pxPositions = [QPoint(0, 0), QPoint(w - 1, h - 1)]

        speclib1 = SpectralLibrary.readFromRasterPositions(enmap, pxPositions)
        speclib1.setName('Extracted Spectra')
        self.assertIsInstance(speclib1, SpectralLibrary)
        self.assertTrue(len(speclib1) > 0)

        vl1 = TestObjects.createVectorLayer(QgsWkbTypes.Polygon)
        vl2 = TestObjects.createVectorLayer(QgsWkbTypes.LineGeometry)
        vl3 = TestObjects.createVectorLayer(QgsWkbTypes.Point)

        layers = [vl1, vl2, vl3]
        # layers = [speclib1]

        QgsProject.instance().addMapLayers(layers)
        from qps.speclib.io.rastersources import SpectralProfileImportPointsDialog

        def onFinished(code):
            self.assertTrue(code in [QDialog.Accepted, QDialog.Rejected])

            if code == QDialog.Accepted:
                slib = d.speclib()
                self.assertTrue(d.isFinished())
                self.assertIsInstance(slib, SpectralLibrary)
                self.assertIsInstance(d.profiles(), list)
                self.assertTrue(len(d.profiles()) == len(slib))
                print('Returned {} profiles from {} and {}'.format(len(slib), d.vectorSource().source(),
                                                                   d.rasterSource().source()))

        for vl in layers:
            d = SpectralProfileImportPointsDialog()
            self.assertIsInstance(d, SpectralProfileImportPointsDialog)
            d.setRasterSource(lyrRaster)
            d.setVectorSource(vl)
            d.show()
            self.assertEqual(lyrRaster, d.rasterSource())
            self.assertEqual(vl, d.vectorSource())

            d.finished.connect(onFinished)
            d.run(run_async=False)
            while not d.isFinished():
                QApplication.processEvents()
            d.hide()
            d.close()

        # self.showGui(d)

    @unittest.skipIf(TestCase.runsInCI(), 'Opens blocking dialog')
    def test_AttributeDialog(self):

        SLIB = TestObjects.createSpectralLibrary()
        d = AddAttributeDialog(SLIB)
        self.showGui(d)

    def test_SpectralLibraryWidgetProgressDialog(self):

        slib = TestObjects.createSpectralLibrary(3000)
        self.assertIsInstance(slib, SpectralLibrary)
        self.assertTrue(slib.isValid())

    def test_SpectralLibraryWidgetCurrentProfilOverlayerXUnit(self):

        sw = SpectralLibraryWidget()
        self.assertIsInstance(sw, SpectralLibraryWidget)
        pw = sw.plotWidget()
        self.assertIsInstance(pw, SpectralProfilePlotWidget)
        self.assertEqual(pw.xAxis().unit(), BAND_NUMBER)
        slib = TestObjects.createSpectralLibrary(10)

        xunits = []
        for p in slib:
            self.assertIsInstance(p, SpectralProfile)
            u = p.xUnit()
            if u not in xunits:
                xunits.append(u)

        sw = SpectralLibraryWidget(speclib=slib)
        self.assertEqual(sw.speclib(), slib)
        sw.updatePlot()

        sw = SpectralLibraryWidget()
        sw.updatePlot()
        sp = slib[0]
        sw.setCurrentProfiles([sp])
        sw.updatePlot()


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'), buffer=False)
