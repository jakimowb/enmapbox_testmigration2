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
        p = speclib[-1]
        w.setProfileValues(p)
        w.show()
        QAPP.exec_()


    def test_SpectralProfileValueTableModel(self):

        speclib = self.createSpeclib()
        p3 = speclib[2]
        self.assertIsInstance(p3, SpectralProfile)

        xUnit = p3.xUnit()
        yUnit = p3.yUnit()


        m = SpectralProfileValueTableModel()
        self.assertIsInstance(m, SpectralProfileValueTableModel)
        self.assertTrue(m.rowCount() == 0)
        self.assertTrue(m.columnCount() == 2)
        self.assertEqual('Y [-]', m.headerData(0, orientation=Qt.Horizontal, role=Qt.DisplayRole))
        self.assertEqual('X [-]', m.headerData(1, orientation=Qt.Horizontal, role=Qt.DisplayRole))

        m.setProfileData(p3)
        self.assertTrue(m.rowCount() == len(p3.values()['x']))
        self.assertEqual('Y [Reflectance]'.format(yUnit), m.headerData(0, orientation=Qt.Horizontal, role=Qt.DisplayRole))
        self.assertEqual('X [{}]'.format(xUnit), m.headerData(1, orientation=Qt.Horizontal, role=Qt.DisplayRole))

        m.setColumnValueUnit(0, '')

    def test_SpectralProfileEditorWidgetFactory(self):

        # init some other requirements
        print('initialize EnMAP-Box editor widget factories')
        # register Editor widgets, if not done before

        reg = QgsGui.editorWidgetRegistry()
        if len(reg.factories()) == 0:
            reg.initEditors()


        registerSpectralProfileEditorWidget()
        self.assertTrue(EDITOR_WIDGET_REGISTRY_KEY in reg.factories().keys())
        factory = reg.factories()[EDITOR_WIDGET_REGISTRY_KEY]
        self.assertIsInstance(factory, SpectralProfileEditorWidgetFactory)
        vl = self.createSpeclib()
        am = vl.actions()
        self.assertIsInstance(am, QgsActionManager)

        c = QgsMapCanvas()
        w = QWidget()
        w.setLayout(QVBoxLayout())
        dv = QgsDualView()
        dv.init(vl, c)
        dv.setView(QgsDualView.AttributeTable)
        dv.setAttributeTableConfig(vl.attributeTableConfig())
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
        w.show()
        w.resize(QSize(300,250))
        print(vl.fields().names())
        look = vl.fields().lookupField
        self.assertTrue(factory.fieldScore(vl, look(FIELD_FID)) == 0) #specialized support style + str len > 350
        self.assertTrue(factory.fieldScore(vl, look(FIELD_NAME)) == 5)
        self.assertTrue(factory.fieldScore(vl, look(FIELD_VALUES)) == 20)

        parent = QWidget()
        configWidget = factory.configWidget(vl, look(FIELD_VALUES), None)
        self.assertIsInstance(configWidget, SpectralProfileEditorConfigWidget)
        configWidget.show()

        self.assertIsInstance(factory.createSearchWidget(vl, 0, dv), QgsSearchWidgetWrapper)


        eww = factory.create(vl, 0, None, dv )
        self.assertIsInstance(eww, SpectralProfileEditorWidgetWrapper)
        self.assertIsInstance(eww.widget(), SpectralProfileEditorWidget)

        eww.valueChanged.connect(lambda v: print('value changed: {}'.format(v)))

        fields = vl.fields()
        vl.startEditing()
        value = eww.value()
        f = vl.getFeature(1)
        f.setAttribute('style', value)
        self.assertTrue(vl.updateFeature(f))

        QAPP.exec_()



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



