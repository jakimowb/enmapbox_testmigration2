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
# noinspection PyPep8Naming
import unittest
from enmapbox.gui.utils import *
from enmapbox.dependencycheck import installTestdata
installTestdata(False)
from enmapboxtestdata import *
QAPP = initQgisApplication(qgisResourceDir=DIR_QGISRESOURCES)
from osgeo import gdal
gdal.AllRegister()
from .spectrallibraries import *

class TestInit(unittest.TestCase):

    def setUp(self):

        self.SP = None
        self.SPECLIB = None
        self.lyr1 = QgsRasterLayer(hymap)
        self.lyr2 = QgsRasterLayer(enmap)
        self.layers = [self.lyr1, self.lyr2]
        QgsProject.instance().addMapLayers(self.layers)

    def createSpeclib(self):
        from enmapboxtestdata import hymap


        #for dx in range(-120, 120, 90):
        #    for dy in range(-120, 120, 90):
        #        pos.append(SpatialPoint(ext.crs(), center.x() + dx, center.y() + dy))

        speclib = SpectralLibrary()
        p1 = SpectralProfile()
        p1.setName('No Geometry')

        p1.setValues(x=[0.2, 0.3, 0.2, 0.5, 0.7], y = [1, 2, 3, 4, 5])
        p2 = SpectralProfile()
        p2.setName('No Geom & NoData')

        p3 = SpectralProfile()
        p3.setValues(x = [250., 251., 253., 254., 256.], y = [0.2, 0.3, 0.2, 0.5, 0.7])
        p3.setXUnit('nm')

        p4 = SpectralProfile()
        p4.setValues(x = [0.250, 0.251, 0.253, 0.254, 0.256], y = [0.22, 0.333, 0.222, 0.555, 0.777])
        p4.setXUnit('um')

        path = hymap
        ext = SpatialExtent.fromRasterSource(path)
        posA = ext.spatialCenter()
        posB = SpatialPoint(posA.crs(), posA.x()+60, posA.y()+ 90)

        p5 = SpectralProfile.fromRasterSource(path, posA)
        p5.setName('Position A')
        p6 = SpectralProfile.fromRasterSource(path, posB)
        p6.setName('Position B')
        speclib.addProfiles([p1, p2, p3, p4, p5, p6])

        return speclib


    def test_fields(self):

        f1 = createQgsField('foo', 9999)

        self.assertEqual(f1.name(),'foo')
        self.assertEqual(f1.type(), QVariant.Int)
        self.assertEqual(f1.typeName(), 'int')

        f2 = createQgsField('bar', 9999.)
        self.assertEqual(f2.type(), QVariant.Double)
        self.assertEqual(f2.typeName(), 'double')

        f3 = createQgsField('text', 'Hello World')
        self.assertEqual(f3.type(), QVariant.String)
        self.assertEqual(f3.typeName(), 'varchar')

        fields = QgsFields()
        fields.append(f1)
        fields.append(f2)
        fields.append(f3)

        serialized = qgsFields2str(fields)
        self.assertIsInstance(serialized,str)

        fields2 = str2QgsFields(serialized)
        self.assertIsInstance(fields2, QgsFields)
        self.assertEqual(fields.count(), fields2.count())
        for i in range(fields.count()):
            f1 = fields.at(i)
            f2 = fields2.at(i)
            self.assertEqual(f1.type(), f2.type())
            self.assertEqual(f1.name(), f2.name())
            self.assertEqual(f1.typeName(), f2.typeName())


    def test_AttributeDialog(self):

        speclib = self.createSpeclib()

        d = AddAttributeDialog(speclib)
        d.exec_()

        if d.result() == QDialog.Accepted:
            field = d.field()
            self.assertIsInstance(field, QgsField)
            s = ""
        s = ""


    def test_SpectralProfile(self):

        sp = SpectralProfile()
        d = sp.values()
        self.assertIsInstance(d, dict)
        for k in ['x','y','xUnit','yUnit']:
            self.assertTrue(k in d.keys())
            v = d[k]
            self.assertTrue(v == None)


        y = [0.23, 0.4, 0.3, 0.8, 0.7]
        x = [300, 400, 600, 1200, 2500]
        sp.setValues(y=y)
        d = sp.values()
        self.assertIsInstance(d, dict)
        self.assertListEqual(d['y'], y)
        self.assertEqual(d['x'], None)
        self.assertEqual(d['xUnit'], None)
        self.assertEqual(d['yUnit'], None)
        sp.setValues(x=x)
        d = sp.values()
        self.assertListEqual(d['x'], x)
        #todo: implement must fail cases


        sClone = sp.clone()
        self.assertIsInstance(sClone, SpectralProfile)
        self.assertEqual(sClone, sp)
        sClone.setId(-9999)
        self.assertEqual(sClone, sp)



        canvas = QgsMapCanvas()
        canvas.setLayers(self.layers)
        canvas.setExtent(self.lyr2.extent())
        canvas.setDestinationCrs(self.lyr1.crs())
        pos = SpatialPoint(self.lyr2.crs(), *self.lyr2.extent().center())
        profiles = SpectralProfile.fromMapCanvas(canvas, pos)
        self.assertIsInstance(profiles, list)
        self.assertEqual(len(profiles), 2)
        for p in profiles:
            self.assertIsInstance(p, SpectralProfile)
            self.assertIsInstance(p.geometry(), QgsGeometry)
            self.assertTrue(p.hasGeometry())


        yVal = [0.23, 0.4, 0.3, 0.8, 0.7]
        xVal = [300,400, 600, 1200, 2500]
        sp1 = SpectralProfile()
        sp1.setValues(x=xVal, y=yVal)

        name = 'missingAttribute'
        sp1.setMetadata(name, 'myvalue')
        self.assertTrue(name not in sp1.fieldNames())
        sp1.setMetadata(name, 'myvalue', addMissingFields=True)
        self.assertTrue(name in sp1.fieldNames())
        self.assertEqual(sp1.metadata(name), 'myvalue')
        sp1.removeField(name)
        self.assertTrue(name not in sp1.fieldNames())

        sp1.setXUnit('nm')
        self.assertEqual(sp1.xUnit(), 'nm')

        self.assertEqual(sp1, sp1)


        for sp2 in[sp1.clone(), copy.copy(sp1), sp1.__copy__()]:
            self.assertIsInstance(sp2, SpectralProfile)
            self.assertEqual(sp1, sp2)


        dump = pickle.dumps(sp1)
        sp2 = pickle.loads(dump)
        self.assertIsInstance(sp2, SpectralProfile)
        self.assertEqual(sp1, sp2)
        self.assertEqual(sp1.values(), sp2.values())


        dump = pickle.dumps([sp1, sp2])
        loads = pickle.loads(dump)

        for i, p1 in enumerate([sp1, sp2]):
            p2 = loads[i]
            self.assertIsInstance(p1, SpectralProfile)
            self.assertIsInstance(p2, SpectralProfile)
            self.assertEqual(p1.values(), p2.values())
            self.assertEqual(p1.name(), p2.name())
            self.assertEqual(p1.id(), p2.id())


        sp2 = SpectralProfile()
        sp2.setValues(x=xVal, y=yVal, xUnit='um')
        self.assertNotEqual(sp1, sp2)
        sp2.setValues(xUnit='nm')
        self.assertEqual(sp1, sp2)
        sp2.setYUnit('reflectance')
        self.assertNotEqual(sp1, sp2)




        values = [('key','value'),('key', 100),('Üä','ÜmlÄute')]
        for md in values:
            k, d = md
            sp1.setMetadata(k,d)
            v2 = sp1.metadata(k)
            self.assertEqual(v2, None)

        for md in values:
            k, d = md
            sp1.setMetadata(k, d, addMissingFields=True)
            v2 = sp1.metadata(k)
            self.assertEqual(d, v2)

        self.SP = sp1


        dump = pickle.dumps(sp1)

        unpickled = pickle.loads(dump)
        self.assertIsInstance(unpickled, SpectralProfile)
        self.assertEqual(sp1, unpickled)
        self.assertEqual(sp1.values(), unpickled.values())
        self.assertEqual(sp1.geometry().asWkt(), unpickled.geometry().asWkt())
        dump = pickle.dumps([sp1, sp2])
        unpickled = pickle.loads(dump)
        self.assertIsInstance(unpickled, list)
        r1, r2 = unpickled
        self.assertEqual(sp1.values(), r1.values())
        self.assertEqual(sp2.values(), r2.values())
        self.assertEqual(sp2.geometry().asWkt(), r2.geometry().asWkt())



    def test_speclib_mimedata(self):

        sp1 = SpectralProfile()
        sp1.setName('Name A')
        sp1.setValues(y=[0, 4, 3, 2, 1], x=[450, 500, 750, 1000, 1500])

        sp2 = SpectralProfile()
        sp2.setName('Name B')
        sp2.setValues(y=[3, 2, 1, 0, 1], x=[450, 500, 750, 1000, 1500])

        sl1 = SpectralLibrary()

        self.assertEqual(sl1.name(), 'SpectralLibrary')
        sl1.setName('MySpecLib')
        self.assertEqual(sl1.name(), 'MySpecLib')

        sl1.addProfiles([sp1, sp2])


        for format in [MIMEDATA_TEXT, MIMEDATA_SPECLIB, MIMEDATA_SPECLIB_LINK]:
            print('Test MimeData I/O "{}"'.format(format))
            mimeData = sl1.mimeData(format)
            self.assertIsInstance(mimeData, QMimeData)
            slRetrievd = SpectralLibrary.readFromMimeData(mimeData)
            self.assertIsInstance(slRetrievd, SpectralLibrary)

            n = len(slRetrievd)
            self.assertEqual(n, len(sl1))
            for p, pr in zip(sl1.profiles(), slRetrievd.profiles()):
                self.assertIsInstance(p, SpectralProfile)
                self.assertIsInstance(pr, SpectralProfile)
                self.assertEqual(p.fieldNames(),pr.fieldNames())
                self.assertEqual(p.yValues(), pr.yValues())

                self.assertEqual(p.xValues(), pr.xValues())
                self.assertEqual(p.xUnit(), pr.xUnit())
                self.assertEqual(p.name(), pr.name())
                self.assertEqual(p, pr)


            self.assertEqual(sl1, slRetrievd)



    def test_SpectralLibrary(self):


        self.assertListEqual(vsiSpeclibs(), [])

        sp1 = SpectralProfile()
        sp1.setName('Name 1')
        sp1.setValues(y=[1, 1, 1, 1, 1], x=[450, 500, 750, 1000, 1500])

        sp2 = SpectralProfile()
        sp2.setName('Name 2')
        sp2.setValues(y=[2, 2, 2, 2, 2], x=[450, 500, 750, 1000, 1500])

        speclib = SpectralLibrary()
        self.assertEqual(len(vsiSpeclibs()), 1)
        self.assertEqual(len(list(SpectralLibrary.instances())), 1)

        sl2 = SpectralLibrary()
        self.assertEqual(len(vsiSpeclibs()), 2)
        self.assertEqual(len(list(SpectralLibrary.instances())), 2)

        del sl2
        self.assertEqual(len(vsiSpeclibs()), 1)


        self.assertEqual(speclib.name(), 'SpectralLibrary')
        speclib.setName('MySpecLib')
        self.assertEqual(speclib.name(), 'MySpecLib')

        speclib.addProfiles([sp1, sp2])
        self.assertEqual(len(speclib),2)

        # test subsetting

        p = speclib[0]
        self.assertIsInstance(p, SpectralProfile)
        self.assertIsInstance(p.values(), dict)

        if p.values() != sp1.values():
            s = ""

        self.assertEqual(p.values(), sp1.values(), msg='Unequal values:\n\t{}\n\t{}'.format(str(p.values()), str(sp1.values())))
        self.assertEqual(speclib[0].values(), sp1.values())
        self.assertEqual(speclib[0].style(), sp1.style())
        #self.assertNotEqual(speclib[0], sp1) #because sl1 has an FID


        subset = speclib[0:1]
        self.assertIsInstance(subset, list)
        self.assertEqual(len(subset), 1)


        self.assertEqual(set(speclib.allFeatureIds()), set([1,2]))
        slSubset = speclib.speclibFromFeatureIDs(fids=2)
        self.assertEqual(set(speclib.allFeatureIds()), set([1, 2]))
        self.assertIsInstance(slSubset, SpectralLibrary)

        refs = list(SpectralLibrary.instances())
        self.assertTrue(len(refs) == 2)

        self.assertEqual(len(slSubset), 1)
        self.assertEqual(slSubset[0].values(), speclib[1].values())

        n = len(vsiSpeclibs())
        dump = pickle.dumps(speclib)
        restoredSpeclib = pickle.loads(dump)
        self.assertIsInstance(restoredSpeclib, SpectralLibrary)
        self.assertEqual(len(vsiSpeclibs()), n+1)
        self.assertEqual(len(speclib), len(restoredSpeclib))

        for i in range(len(speclib)):
            p1 = speclib[i]
            r1 = restoredSpeclib[i]

            if p1.values() != r1.values():
                s  =""

            self.assertEqual(p1.values(), r1.values(), msg='dumped and restored values are not the same')

        restoredSpeclib.addProfiles([sp2])
        self.assertNotEqual(speclib, restoredSpeclib)
        self.assertEqual(restoredSpeclib[-1].values(), sp2.values())


        #read from image

        if self.lyr1.isValid():
            center1 = self.lyr1.extent().center()
            center2 = SpatialPoint.fromSpatialExtent(SpatialExtent.fromLayer(self.lyr1))
        else:
            center1 = SpatialExtent.fromRasterSource(self.lyr1.source()).spatialCenter()
            center2 = SpatialExtent.fromRasterSource(self.lyr1.source()).spatialCenter()
            s  =""
        speclib = SpectralLibrary.readFromRasterPositions(hymap,center1)
        slSubset = SpectralLibrary.readFromRasterPositions(hymap,center2)
        restoredSpeclib = SpectralLibrary.readFromRasterPositions(hymap,[center1, center2])

        for sl in [speclib, slSubset]:
            self.assertIsInstance(sl, SpectralLibrary)
            self.assertTrue(len(sl) == 1)
            self.assertIsInstance(sl[0], SpectralProfile)
            self.assertTrue(sl[0].hasGeometry())

        self.assertTrue(len(restoredSpeclib) == 2)

        n1 = len(speclib)
        n2 = len(slSubset)

        speclib.addProfiles(slSubset[:])
        self.assertTrue(len(speclib) == n1+n2)
        speclib.addProfiles(slSubset[:])
        self.assertTrue(len(speclib) == n1 + n2 + n2)


    def test_others(self):

        self.assertEqual(23, toType(int, '23'))
        self.assertEqual([23, 42], toType(int, ['23','42']))
        self.assertEqual(23., toType(float, '23'))
        self.assertEqual([23., 42.], toType(float, ['23','42']))

        self.assertTrue(findTypeFromString('23') is int)
        self.assertTrue(findTypeFromString('23.3') is float)
        self.assertTrue(findTypeFromString('xyz23.3') is str)
        self.assertTrue(findTypeFromString('') is str)

        regex = CSVSpectralLibraryIO.REGEX_BANDVALUE_COLUMN

        #REGEX to identify band value column names

        for text in ['b1', 'b1_']:
            match = regex.match(text)
            self.assertEqual(match.group('band'), '1')
            self.assertEqual(match.group('xvalue'), None)
            self.assertEqual(match.group('xunit'), None)


        match = regex.match('b1 23.34 nm')
        self.assertEqual(match.group('band'), '1')
        self.assertEqual(match.group('xvalue'), '23.34')
        self.assertEqual(match.group('xunit'), 'nm')


    def test_io(self):

        sl1 = self.createSpeclib()
        tempDir = tempfile.gettempdir()
        tempDir = os.path.join(DIR_REPO, *['test','outputs'])
        pathESL = os.path.join(tempDir,'speclibESL.esl')
        pathCSV = os.path.join(tempDir,'speclibCSV.csv')

        #test clipboard IO
        QApplication.clipboard().setMimeData(QMimeData())
        self.assertFalse(ClipboardIO.canRead())
        writtenFiles = ClipboardIO.write(sl1)
        self.assertEqual(len(writtenFiles), 0)
        self.assertTrue(ClipboardIO.canRead())
        sl1b = ClipboardIO.readFrom()
        self.assertIsInstance(sl1b, SpectralLibrary)
        self.assertEqual(sl1, sl1b)

        #!!! clear clipboard
        QApplication.clipboard().setMimeData(QMimeData())


        #test ENVI Spectral Library
        writtenFiles = EnviSpectralLibraryIO.write(sl1, pathESL)
        n = 0
        for path in writtenFiles:
            self.assertTrue(os.path.isfile(path))
            self.assertTrue(path.endswith('.sli'))

            basepath = os.path.splitext(path)[0]
            pathHDR = basepath + '.hdr'
            pathCSV = basepath + '.csv'
            self.assertTrue(os.path.isfile(pathHDR))
            self.assertTrue(os.path.isfile(pathCSV))

            self.assertTrue(EnviSpectralLibraryIO.canRead(path))
            sl_read1 = EnviSpectralLibraryIO.readFrom(path)
            self.assertIsInstance(sl_read1, SpectralLibrary)
            sl_read2 = SpectralLibrary.readFrom(path)
            self.assertIsInstance(sl_read2, SpectralLibrary)
            print(sl_read1)
            self.assertTrue(len(sl_read1) > 0)
            self.assertEqual(sl_read1, sl_read2)
            n += len(sl_read1)
        self.assertEqual(len(sl1) - 1, n ) #-1 because of a missing data profile


        #TEST CSV writing
        writtenFiles = sl1.exportProfiles(pathCSV)
        self.assertIsInstance(writtenFiles, list)
        self.assertTrue(len(writtenFiles) == 1)

        n = 0
        for path in writtenFiles:
            self.assertTrue(CSVSpectralLibraryIO.canRead(path))
            sl_read1 = CSVSpectralLibraryIO.readFrom(path)
            sl_read2 = SpectralLibrary.readFrom(path)

            self.assertIsInstance(sl_read1, SpectralLibrary)
            self.assertIsInstance(sl_read2, SpectralLibrary)

            n += len(sl_read1)
        self.assertEqual(n, len(sl1)-1)





        self.SPECLIB = sl1


    def test_mergeSpeclibs(self):

        sp = SpectralProfile()
        fieldName = 'newField'
        sp.setMetadata(fieldName, 'foo', addMissingFields=True)
        sl = SpectralLibrary()
        sl.startEditing()
        sl.addAttribute(createQgsField(fieldName, ''))
        sl.commitChanges()
        self.assertIn(fieldName, sl.fieldNames())

        sl = SpectralLibrary()
        sl.addProfiles(sp)

        sl = SpectralLibrary()
        self.assertTrue(fieldName not in sl.fieldNames())
        self.assertTrue(len(sl) == 0)
        sl.addProfiles(sp, addMissingFields=False)
        self.assertTrue(fieldName not in sl.fieldNames())
        self.assertTrue(len(sl) == 1)


        sl = SpectralLibrary()
        self.assertTrue(fieldName not in sl.fieldNames())
        sl.addProfiles(sp, addMissingFields=True)
        self.assertTrue(fieldName in sl.fieldNames())
        self.assertTrue(len(sl) == 1)
        p = sl[0]
        self.assertIsInstance(p, SpectralProfile)
        self.assertEqual(p.metadata(fieldName), sp.metadata(fieldName))

    def test_SpectralProfileEditorWidget(self):

        speclib = self.createSpeclib()

        w = SpectralProfileEditorWidget()
        p = speclib[-1]
        w.setProfileValues(p)
        w.show()
        QAPP.exec_()




    def test_SpectralProfileEditorWidgetFactory(self):

        # init some other requirements
        print('initialize EnMAP-Box editor widget factories')
        # register Editor widgets, if not done before
        reg = QgsGui.editorWidgetRegistry()
        if len(reg.factories()) == 0:
            reg.initEditors()

        if not 'SpectralProfile' in reg.factories().keys():
            spectralProfileEditorWidgetFactory = SpectralProfileEditorWidgetFactory('SpectralProfile')
            reg.registerWidget('SpectralProfile', spectralProfileEditorWidgetFactory)
        else:
            spectralProfileEditorWidgetFactory = reg.factories()['SpectralProfile']

        self.assertTrue('SpectralProfile' in reg.factories().keys())

        factory = reg.factories()['SpectralProfile']
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
        self.assertTrue(factory.fieldScore(vl, 0) == 0) #specialized support style + str len > 350
        self.assertTrue(factory.fieldScore(vl, 1) == 5)
        self.assertTrue(factory.fieldScore(vl, 2) == 5)
        self.assertTrue(factory.fieldScore(vl, 3) == 20)



        self.assertIsInstance(factory.configWidget(vl, 0, dv), QgsEditorConfigWidget)
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


    def test_speclibWidget(self):

        speclib = self.createSpeclib()
        p = SpectralLibraryWidget()
        p.addSpeclib(speclib)
        p.show()
        QgsProject.instance().addMapLayer(p.speclib())

        self.assertEqual(p.speclib(), speclib)

        self.assertIsInstance(p.speclib(), SpectralLibrary)
        fieldNames = p.speclib().fieldNames()
        self.assertIsInstance(fieldNames, list)

        if False:
            #self.assertIsInstance(p.mModel, SpectralLibraryTableModel)
            #self.assertTrue(p.mModel.headerData(0, Qt.Horizontal) == fieldNames[0])
            cs = [speclib[0], speclib[3], speclib[-1]]
            p.setAddCurrentSpectraToSpeclibMode(False)
            p.setCurrentSpectra(cs)
            self.assertTrue(len(p.speclib()) == 0)
            p.addCurrentSpectraToSpeclib()
            self.assertTrue(len(p.speclib()) == len(cs))
            #self.assertEqual(p.speclib()[:], cs)

            #p.speclib().removeProfiles(p.speclib()[:])
            #self.assertTrue(len(p.speclib()) == 0)

            #p.setAddCurrentSpectraToSpeclibMode(True)
            #p.setCurrentSpectra(cs)
            #self.assertTrue(len(p.speclib()) == len(cs))

        QAPP.exec_()


    def test_plotWidget(self):

        speclib = self.createSpeclib()
        model = SpectralLibraryTableModel(speclib=speclib)
        w = SpectralLibraryPlotWidget()
        w.setModel(model)
        w.show()
        self.assertIsInstance(w, SpectralLibraryPlotWidget)

        pdis = [i for i in w.plotItem.items if isinstance(i, SpectralProfilePlotDataItem)]
        self.assertTrue(len(speclib), len(pdis))
        for pdi in pdis:
            self.assertTrue(pdi.isVisible())


        p = speclib[3]
        fid = p.id()

        speclib.removeProfiles(p)

        pdis = [i for i in w.plotItem.items if isinstance(i, SpectralProfilePlotDataItem)]
        for pdi in pdis:
            self.assertFalse(pdi.mProfile.id() == fid)

        QAPP.exec_()

    def test_editing(self):

        slib = self.createSpeclib()
        self.assertTrue(len(slib) > 0)
        slw = SpectralLibraryWidget()
        slw.speclib().addSpeclib(slib)
        slw.show()
        slw.actionToggleEditing.setChecked(True)
        idx = slw.mModel.createIndex(0,slw.speclib().fieldNames().index('name'))
        f = slw.mModel.feature(idx)
        self.assertIsInstance(f, QgsFeature)

        p = slw.mModel.spectralProfile(idx)
        self.assertIsInstance(p, SpectralProfile)
        slw.mModel.setData(idx, 'mynewname', role=Qt.EditRole)
        #self.assertTrue()
        QAPP.exec_()



if __name__ == '__main__':

    import json

    txt = json.dumps([0,1,2])

    unittest.main()
