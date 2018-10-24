# coding=utf-8
"""Resources test.

"""
__author__ = 'benjamin.jakimow@geo.hu-berlin.de'
__date__ = '2017-07-17'
__copyright__ = 'Copyright 2017, Benjamin Jakimow'

import unittest

import tempfile
from qgis import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from enmapbox.gui.utils import *
from enmapbox.gui.classificationscheme import *
import enmapboxtestdata

QGIS_APP = initQgisApplication()



from unittest import TestCase
class TestsClassificationScheme(TestCase):

    def createClassScheme(self)->ClassificationScheme:

        cs = ClassificationScheme()
        cs.addClass(ClassInfo(name='unclassified', color=QColor('black')))
        cs.addClass(ClassInfo(name='Class A', color=QColor('green')))
        cs.addClass(ClassInfo(name='Class B', color=QColor('blue')))
        return cs

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


    def testClassificationScheme(self):
        cs = ClassificationScheme.create(3)

        self.assertIsInstance(cs, ClassificationScheme)
        self.assertEqual(cs[0].color(), DEFAULT_UNCLASSIFIEDCOLOR)
        c = ClassInfo(label=1, name='New Class', color=QColor('red'))
        cs.addClass(c)
        self.assertEqual(cs[3], c)
        cs.resetLabels()
        self.assertEqual(cs[3].label(), 3)

    def test_json_pickle(self):
        cs = self.createClassScheme()

        j = cs.json()
        self.assertIsInstance(j, str)
        cs2 = ClassificationScheme.fromJSON(j)
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



        QGIS_APP.exec_()



    def test_dialog(self):
        w = ClassificationSchemeWidget()
        self.assertIsInstance(w.classificationScheme(), ClassificationScheme)
        w.show()
        w.btnAddClasses.click()
        w.btnAddClasses.click()

        self.assertTrue(len(w.classificationScheme()) == 2)
        QGIS_APP.exec_()


    def test_io_CSV(self):

        testDir = os.path.dirname(enmapboxtestdata.speclib)
        csvFiles = file_search(testDir, 'Speclib.*.classdef.csv')

        pathTmp = tempfile.mktemp(suffix='.csv')
        for pathCSV in csvFiles:
            #read from CSV
            classScheme = ClassificationScheme.fromCsv(pathCSV)
            self.assertIsInstance(classScheme, ClassificationScheme)
            self.assertTrue(len(classScheme) > 0)

            #todo: other tests

            classScheme.saveToCsv(pathTmp)

            classScheme2 = ClassificationScheme.fromCsv(pathTmp)
            self.assertIsInstance(classScheme2, ClassificationScheme)
            self.assertEqual(classScheme, classScheme2)

    def test_io_QML(self):

        testDir = os.path.dirname(enmapboxtestdata.speclib)
        qmFiles = file_search(testDir, 'LandCov_*.qml')

        pathTmp = tempfile.mktemp(suffix='.qml')
        for pathQML in qmFiles:
            # read from QML
            classScheme = ClassificationScheme.fromQml(pathQML)
            self.assertIsInstance(classScheme, ClassificationScheme)
            self.assertTrue(len(classScheme) > 0)

            # todo: other QML specific tests

            #write to QML
            classScheme.saveToQml(pathTmp)

            classScheme2 = ClassificationScheme.fromQml(pathTmp)
            self.assertIsInstance(classScheme2, ClassificationScheme)
            self.assertEqual(classScheme, classScheme2)





        s = ""

if __name__ == "__main__":

    unittest.main()



