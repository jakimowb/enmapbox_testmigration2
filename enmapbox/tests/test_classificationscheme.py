# coding=utf-8
"""Resources test.

"""
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest

import tempfile
from qgis import *
from qgis.core import *
from qgis.gui import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from enmapbox.gui.utils import *
from enmapbox.gui.classificationscheme import *
import enmapboxtestdata


SHOW_GUIS = True

QGIS_APP = initQgisApplication()



from unittest import TestCase
class TestsClassificationScheme(TestCase):

    def createClassScheme(self)->ClassificationScheme:

        cs = ClassificationScheme()
        cs.addClass(ClassInfo(name='unclassified', color=QColor('black')))
        cs.addClass(ClassInfo(name='Class A', color=QColor('green')))
        cs.addClass(ClassInfo(name='Class B', color=QColor('blue')))
        return cs

    def createRasterLayer(self)->QgsRasterLayer:

        rl = QgsRasterLayer(enmapboxtestdata.hires)

        renderer = QgsPalettedRasterRenderer(rl, 1)
        assert isinstance(renderer, QgsPalettedRasterRenderer)


        return rl

    def createVectorLayer(self)->QgsVectorLayer:
        # create layer
        vl = QgsVectorLayer("Point", "temporary_points", "memory")
        vl.startEditing()
        # add fields
        vl.addAttribute(QgsField("name", QVariant.String))
        vl.addAttribute(QgsField("class_label", QVariant.Int))
        vl.addAttribute(QgsField("class_name", QVariant.String))
        f = QgsFeature(vl.fields())
        f.setAttribute('name', 'f1')
        f.setAttribute('class_label', 2)
        f.setAttribute('class_name', 'Class A')
        vl.addFeature(f)
        vl.commitChanges()

        cs = self.createClassScheme()
        confValues = {'classes': cs.json()}
        conf = vl.attributeTableConfig()
        vl.setEditorWidgetSetup(vl.fields().lookupField('class_label'), QgsEditorWidgetSetup(EDITOR_WIDGET_REGISTRY_KEY, confValues))
        vl.setEditorWidgetSetup(vl.fields().lookupField('class_name'), QgsEditorWidgetSetup(EDITOR_WIDGET_REGISTRY_KEY, confValues))



        return vl

    def testClassInfo(self):
        name = 'TestName'
        label = 2
        color = QColor('green')
        c = ClassInfo(name=name, label=label, color=color)
        self.assertEqual(c.name(), name)
        self.assertEqual(c.label(), label)
        self.assertEqual(c.color(), color)

        name2 = 'TestName2'
        label2 = 3
        color2 = QColor('red')
        c.setLabel(label2)
        c.setColor(color2)
        c.setName(name2)
        self.assertEqual(c.name(), name2)
        self.assertEqual(c.label(), label2)
        self.assertEqual(c.color(), color2)


    def test_ClassificationScheme(self):
        cs = ClassificationScheme.create(3)

        self.assertIsInstance(cs, ClassificationScheme)
        self.assertEqual(cs[0].color(), DEFAULT_UNCLASSIFIEDCOLOR)
        c = ClassInfo(label=1, name='New Class', color=QColor('red'))
        cs.addClass(c)
        self.assertEqual(cs[3], c)
        cs._updateLabels()
        self.assertEqual(cs[3].label(), 3)

        self.assertEqual(cs.headerData(0, Qt.Horizontal, Qt.DisplayRole), 'Label')
        self.assertEqual(cs.headerData(1, Qt.Horizontal, Qt.DisplayRole), 'Name')
        self.assertEqual(cs.headerData(2, Qt.Horizontal, Qt.DisplayRole), 'Color')

        self.assertEqual(cs.data(cs.createIndex(0,0), Qt.DisplayRole), 0)
        self.assertEqual(cs.data(cs.createIndex(0,1), Qt.DisplayRole), cs[0].name())
        self.assertEqual(cs.data(cs.createIndex(0,2), Qt.DisplayRole), cs[0].color().name())
        self.assertEqual(cs.data(cs.createIndex(0,2), Qt.BackgroundColorRole), cs[0].color())

        self.assertIsInstance(cs.data(cs.createIndex(0,0), role=Qt.UserRole), ClassInfo)



    def test_json_pickle(self):
        cs = self.createClassScheme()

        j = cs.json()
        self.assertIsInstance(j, str)
        cs2 = ClassificationScheme.fromJson(j)
        self.assertIsInstance(cs2, ClassificationScheme)
        self.assertEqual(cs, cs2)

        p = cs.pickle()
        self.assertIsInstance(p, bytes)

        cs3 = ClassificationScheme.fromPickle(p)
        self.assertIsInstance(cs3, ClassificationScheme)
        self.assertEqual(cs3, cs)




    def test_ClassInfoComboBox(self):
        scheme = self.createClassScheme()


        w = ClassificationSchemeComboBox()
        w.show()
        w.setClassificationScheme(scheme)
        self.assertIsInstance(w.classificationScheme(), ClassificationScheme)
        w.setCurrentIndex(2)
        self.assertIsInstance(w.currentClassInfo(), ClassInfo)
        self.assertEqual(w.currentClassInfo(), scheme[2])

        if SHOW_GUIS:
            QGIS_APP.exec_()


    def test_ClassificationSchemeEditorWidgetFactory(self):

        # init some other requirements
        print('initialize EnMAP-Box editor widget factories')
        # register Editor widgets, if not done before

        reg = QgsGui.editorWidgetRegistry()
        if len(reg.factories()) == 0:
            reg.initEditors()


        registerClassificationSchemeEditorWidget()
        self.assertTrue(EDITOR_WIDGET_REGISTRY_KEY in reg.factories().keys())
        factory = reg.factories()[EDITOR_WIDGET_REGISTRY_KEY]
        self.assertIsInstance(factory, ClassificationSchemeWidgetFactory)

        vl = self.createVectorLayer()



        c = QgsMapCanvas()
        w = QWidget()
        w.setLayout(QVBoxLayout())
        dv = QgsDualView()
        dv.init(vl, c)
        dv.setView(QgsDualView.AttributeTable)
        dv.setAttributeTableConfig(vl.attributeTableConfig())
        dv.show()
        cb = QCheckBox()
        cb.setText('Show Editor')
        def onClicked(b:bool):
            if b:
                dv.setView(QgsDualView.AttributeEditor)
            else:
                dv.setView(QgsDualView.AttributeTable)
        cb.clicked.connect(onClicked)
        w.layout().addWidget(dv)
        w.layout().addWidget(cb)
        vl.startEditing()
        w.show()
        w.resize(QSize(300,250))
        print(vl.fields().names())
        look = vl.fields().lookupField

        self.assertTrue(factory.fieldScore(vl, look('class_label')) == 20)
        self.assertTrue(factory.fieldScore(vl, look('class_name')) == 20)

        parent = QWidget()
        configWidget = factory.configWidget(vl, look('class_label'), None)
        self.assertIsInstance(configWidget, ClassificationSchemeEditorConfigWidget)
        configWidget.show()

        self.assertIsInstance(factory.createSearchWidget(vl, 0, dv), QgsSearchWidgetWrapper)

        eww = factory.create(vl, 0, None, dv )
        self.assertIsInstance(eww, ClassificationSchemeEditorWidgetWrapper)
        self.assertIsInstance(eww.widget(), ClassificationSchemeComboBox)

        eww.valueChanged.connect(lambda v: print('value changed: {}'.format(v)))


        if SHOW_GUIS:
            QGIS_APP.exec_()



    def test_ClassificationSchemeWidget(self):

        MAP_LAYER_STORES
        w = ClassificationSchemeWidget()
        self.assertIsInstance(w.classificationScheme(), ClassificationScheme)
        w.show()



        w.btnAddClasses.click()
        w.btnAddClasses.click()

        self.assertTrue(len(w.classificationScheme()) == 2)

        if SHOW_GUIS:
            QGIS_APP.exec_()

    def test_ClassificationSchemeComboBox(self):

        cs = self.createClassScheme()

        w = ClassificationSchemeComboBox(classification=cs)
        w.show()

        self.assertTrue(len(w.classificationScheme()) == 3)

        if SHOW_GUIS:
            QGIS_APP.exec_()


    def test_io_CSV(self):

        testDir = os.path.dirname(enmapboxtestdata.library)

        pathTmp = tempfile.mktemp(suffix='.csv')

        cs = self.createClassScheme()
        self.assertIsInstance(cs, ClassificationScheme)
        path = cs.saveToCsv(pathTmp)
        self.assertTrue(os.path.isfile(path))

        cs2 = ClassificationScheme.fromCsv(pathTmp)
        self.assertIsInstance(cs2, ClassificationScheme)
        self.assertEqual(cs, cs2)


    def test_io_RasterRenderer(self):


        cs = self.createClassScheme()
        self.assertIsInstance(cs, ClassificationScheme)

        r = cs.rasterRenderer()
        self.assertIsInstance(r, QgsPalettedRasterRenderer)



        cs2 = ClassificationScheme.fromRasterRenderer(r)
        self.assertIsInstance(cs2, ClassificationScheme)
        self.assertEqual(cs, cs2)

    def test_io_FeatureRenderer(self):


        cs = self.createClassScheme()
        self.assertIsInstance(cs, ClassificationScheme)

        r = cs.featureRenderer()
        self.assertIsInstance(r, QgsCategorizedSymbolRenderer)

        cs2 = ClassificationScheme.fromFeatureRenderer(r)
        self.assertIsInstance(cs2, ClassificationScheme)
        self.assertEqual(cs, cs2)


    def test_io_QML(self):
        cs = self.createClassScheme()
        self.assertIsInstance(cs, ClassificationScheme)

        pathTmp = tempfile.mktemp(suffix='.qml')
        warnings.warn('need QML test', NotImplementedError)

        s = ""
if __name__ == "__main__":

    SHOW_GUIS = True
    unittest.main()



