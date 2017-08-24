# -*- coding: utf-8 -*-

import sys, os
import numpy as np
from qgis.gui import *
#ensure to call QGIS before PyQtGraph
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from osgeo import gdal
import Inverse_mode_cl as inverse
from enmapbox.gui.applications import EnMAPBoxApplication
from Spec2Sensor_cl import Spec2Sensor

pathUI = os.path.join(os.path.dirname(__file__),'GUI_Global_Inversion.ui')
pathUI2 = os.path.join(os.path.dirname(__file__),'GUI_Select_Wavelengths.ui')

from enmapbox.gui.utils import loadUIFormClass

class GUI_Global_Inversion(QDialog, loadUIFormClass(pathUI)):
    
    def __init__(self, parent=None):
        super(GUI_Global_Inversion, self).__init__(parent)
        self.setupUi(self)    

class GUI_Select_Wavelengths(QDialog, loadUIFormClass(pathUI2)):

    def __init__(self, parent=None):
        super(GUI_Select_Wavelengths, self).__init__(parent)
        self.setupUi(self)

class UiFunc:

    def __init__(self):
        
        self.gui = GUI_Global_Inversion()
        # self.myUI2 = UiFunc2()
        self.initial_values()
        self.connections()

    def initial_values(self):
        self.ctype = 0
        self.nbfits = 0
        self.nbfits_type = "rel"
        self.noisetype = 0
        self.noiselevel = 0
        self.nodat = [0] * 3
        self.exclude_bands, self.exclude_bands_model = (None, None)
        self.wl_compare = None
        self.inversion_range = None
        self.n_wl = None
        self.image = None
        self.out_path = None
        self.out_mode = "single"

        self.geo_mode = "off"
        self.geo_file = None
        self.geo_fixed = [None]*3

        self.conversion_factor = None

        self.LUT_path = None
        self.sensor = 1
        self.wl = None

    def connections(self):

        # Input Images
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdInputLUT.clicked.connect(lambda: self.open_file(mode="lut"))

        # Output Images
        self.gui.cmdOutputImage.clicked.connect(lambda: self.open_file(mode="output"))
        self.gui.radOutSingle.clicked.connect(lambda: self.select_outputmode(mode="single"))
        self.gui.radOutIndividual.clicked.connect(lambda: self.select_outputmode(mode="individual"))

        # Sensor Type
        self.gui.radFullRange.clicked.connect(lambda: self.select_sensor(sensor=1))
        self.gui.radEnMAP.clicked.connect(lambda: self.select_sensor(sensor=2))
        self.gui.radSentinel.clicked.connect(lambda: self.select_sensor(sensor=3))
        self.gui.radLandsat.clicked.connect(lambda: self.select_sensor(sensor=4))

        # Geometry
        self.gui.cmdGeoFromFile.clicked.connect(lambda: self.open_file(mode="geo"))
        self.gui.radGeoFromFile.clicked.connect(lambda: self.select_geo(mode="file"))
        self.gui.radGeoFix.clicked.connect(lambda: self.select_geo(mode="fix"))
        self.gui.radGeoOff.clicked.connect(lambda: self.select_geo(mode="off"))

        # Artificial Noise
        self.gui.radNoiseOff.clicked.connect(lambda: self.select_noise(mode=0))
        self.gui.radNoiseAdd.clicked.connect(lambda: self.select_noise(mode=1))
        self.gui.radNoiseMulti.clicked.connect(lambda: self.select_noise(mode=2))
        self.gui.radNoiseInvMulti.clicked.connect(lambda: self.select_noise(mode=3))

        # Cost Function
        self.gui.radRMSE.clicked.connect(lambda: self.select_costfun(mode=1))
        self.gui.radMAE.clicked.connect(lambda: self.select_costfun(mode=2))
        self.gui.radmNSE.clicked.connect(lambda: self.select_costfun(mode=3))
        self.gui.radRel.clicked.connect(lambda: self.select_costfun(type="rel"))
        self.gui.radAbs.clicked.connect(lambda: self.select_costfun(type="abs"))

        # Execute
        self.gui.cmdExcludeBands.clicked.connect(lambda: self.invoke_selection())
        self.gui.cmdRun.clicked.connect(lambda: self.run_inversion())
        self.gui.cmdClose.clicked.connect(lambda: self.gui.accept)

    def open_file(self, mode):
        if mode=="image":
            result = str(QFileDialog.getOpenFileName(caption='Select Input Image'))
            if result:
                self.gui.txtInputImage.setText(result)
        elif mode=="lut":
            result = str(QFileDialog.getOpenFileName(caption='Select LUT meta-file'))
            if result:
                self.gui.txtInputLUT.setText(result)
        elif mode=="output":
            result = str(QFileDialog.getExistingDirectory(caption='Select Path for Output storage'))
            if result:
                self.gui.txtOutputImage.setText(result)
        elif mode=="geo":
            result = str(QFileDialog.getOpenFileName(caption='Select Geometry Image'))
            if result:
                self.gui.txtGeoFromFile.setText(result)

    def select_outputmode(self, mode):
        self.out_mode = mode

    def select_sensor(self, sensor):
        self.sensor = sensor

    def select_geo(self, mode):
        if mode=="off":
            self.gui.txtGeoFromFile.setDisabled(True)
            self.gui.cmdGeoFromFile.setDisabled(True)
            self.gui.txtSZA.setDisabled(True)
            self.gui.txtOZA.setDisabled(True)
            self.gui.txtRAA.setDisabled(True)
        if mode=="file":
            self.gui.txtGeoFromFile.setDisabled(False)
            self.gui.cmdGeoFromFile.setDisabled(False)
            self.gui.txtSZA.setDisabled(True)
            self.gui.txtOZA.setDisabled(True)
            self.gui.txtRAA.setDisabled(True)
        if mode=="fix":
            self.gui.txtGeoFromFile.setDisabled(True)
            self.gui.cmdGeoFromFile.setDisabled(True)
            self.gui.txtSZA.setDisabled(False)
            self.gui.txtOZA.setDisabled(False)
            self.gui.txtRAA.setDisabled(False)
        self.geo_mode = mode

    def select_noise(self, mode):
        if mode==0:
            self.gui.txtNoiseLevel.setDisabled(True)
        else:
            self.gui.txtNoiseLevel.setDisabled(False)
        self.noisetype = mode

    def select_costfun(self, mode=None, type=None):
        if mode: self.ctype = mode
        if type:
            if type=="rel":
                self.gui.txtAbs.setDisabled(True)
                self.gui.txtRel.setDisabled(False)
            elif type=="abs":
                self.gui.txtAbs.setDisabled(False)
                self.gui.txtRel.setDisabled(True)
            self.nbfits_type = type

    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)

    def check_and_assign(self):

        # Image In
        self.image = self.gui.txtInputImage.text()
        self.image = self.image.replace("\\", "/")
        if self.image is None:
            self.abort(message='Input Image missing')
        elif not os.path.isfile(self.image):
            self.abort(message='Input Image could not be read')

        # LUT
        self.LUT_path = self.gui.txtInputLUT.text()
        self.LUT_path = self.LUT_path.replace("\\", "/")
        if self.LUT_path is None:
            self.abort(message='LUT metafile missing')
        elif not os.path.isfile(self.LUT_path):
            self.abort(message='LUT metafile could not be read')

        # Output path
        self.out_path = self.gui.txtOutputImage.text()
        self.out_path = self.out_path.replace("\\", "/")
        if self.out_path is None:
            self.abort(message='Output path missing')
        elif not os.path.isdir(self.out_path):
            self.abort(message='Output path could not be opened')
        else:
            if not self.out_path[-1] == "/":
                self.out_path += "/"

        # Geometry file:
        if self.geo_mode == "file":
            self.geo_file = self.gui.txtGeoFromFile.text()
            self.geo_file = self.geo_file.replace("\\", "/")
            if self.geo_file is None:
                self.abort(message='Geometry-Input via file selected, but no file specified')
            elif not os.path.isfile(self.geo_file):
                self.abort(message='Geometry-Input file could not be read')
        elif self.geo_mode == "fix":
            if self.gui.txtSZA.text() == "" or self.gui.txtOZA.text() == "" or self.gui.txtRAA.text() == "":
                self.abort(message='Geometry-Input via fixed values selected, but angles are incomplete')
            else:
                try:
                    self.geo_fixed = [float(self.gui.txtSZA.text()), float(self.gui.txtOZA.text()), float(self.gui.txtRAA.text())]
                except ValueError:
                    self.abort(message='Cannot interpret Geometry angles as numbers')

        # Noise
        if not self.noisetype == 0:
            if self.gui.txtNoiseLevel.text() == "":
                self.abort(message='Please specify level for artificial noise')
            else:
                self.noiselevel = self.gui.txtNoiseLevel.text()
                try:
                    self.noiselevel = float(self.noiselevel)
                except ValueError:
                    self.abort(message='Cannot interpret noise level as decimal number')

        # Cost Function Type:
        if self.nbfits_type == "rel":
            if self.gui.txtRel.text() == "":
                self.abort(message='Please specify number of best fits')
            else:
                self.nbfits = self.gui.txtRel.text()
                try:
                    self.nbfits = float(self.nbfits)
                except ValueError:
                    self.abort(message='Cannot interpret number of best fits as a real number')
        elif self.nbfits_type == "abs":
            if self.gui.txtAbs.text() == "":
                self.abort(message='Please specify number of best fits')
            else:
                self.nbfits = self.gui.txtAbs.text()
                try:
                    self.nbfits = int(self.nbfits)
                except ValueError:
                    self.abort(message='Cannot interpret number of best fits as a real number')




        ImageIn = "D:/ECST_II/Cope_BroNaVI/WW_nadir_short.bsq"
        ResultsOut = "D:/ECST_III/Processor/VegProc/results.bsq"
        GeometryIn = "D:/ECST_II/Cope_BroNaVI/Felddaten/Parameter/Geometry_DJ_w.bsq"
        LUT_dir = "D:/ECST_III/Processor/VegProc/results2/"
        LUT_name = "Martin_LUT4"

    def run_inversion(self):

        self.check_and_assign()

        inv = inverse.RTM_Inversion()
        inv.inversion_setup(image=self.image, image_out=self.out_path, LUT_path=self.LUT_path, ctype=self.ctype,
                            nbfits=self.nbfits, nbfits_type=self.nbfits_type, noisetype=self.noisetype,
                            noiselevel=self.noiselevel, inversion_range=None, geo_image=self.geo_file,
                            geo_fixed=self.geo_fixed, sensor=self.sensor, exclude_pixels=None,
                            nodat=[-999]*3, which_para=range(15))

        # inv.inversion_setup(image=self.image, image_out=self.out_path, LUT_dir=LUT_dir, LUT_name=LUT_name,
        #                     ctype=costfun_type,
        #                     nbfits=nbest_fits, noisetype=noisetype, noiselevel=noiselevel,
        #                     inversion_range=inversion_range,
        #                     geo_image=GeometryIn, geo_fixed=geometry_fixed, sensor=sensor, exclude_pixels=None,
        #                     nodat=[nodat_Geo, nodat_Image, nodat_Out], which_para=range(15))

        inv.run_inversion()
        inv.write_image()

    def invoke_selection(self):

        # Check ImageIn
        self.image = self.gui.txtInputImage.text()
        self.image = self.image.replace("\\", "/")
        if self.image is None:
            self.abort(message='Specify Input Image first')
        elif not os.path.isfile(self.image):
            self.abort(message='Input Image could not be read')

        # Read ImageIn
        dataset = gdal.Open(self.image)
        if dataset is None:
            self.abort(message='Input Image could not be read. Please make sure it is a valid ENVI image')
        wavelengths = "".join(dataset.GetMetadataItem('wavelength', 'ENVI').split())
        wavelengths = wavelengths.replace("{","")
        wavelengths = wavelengths.replace("}", "")
        wavelengths = wavelengths.split(",")

        if dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['nanometers', 'nm', 'nanometer']:
            print "I shouldn't be raised"
            wave_convert = 1
            self.wunit = u'nm'
        elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['micrometers', 'µm', 'micrometer']:
            wave_convert = 1000
            self.wunit = u"\u03bcm"
        else:
            self.abort(message="No wavelength units provided in ENVI header file")

        self.wl = [float(item) * wave_convert for item in wavelengths]
        self.nbands = dataset.RasterCount
        self.nrows = dataset.RasterYSize
        self.ncols = dataset.RasterXSize

        pass_exclude = []

        if not self.gui.txtExclude.text() == "":
            try:
                pass_exclude = self.gui.txtExclude.text().split(" ")
                pass_exclude = [int(pass_exclude[i])-1 for i in xrange(len(pass_exclude))]
            except:
                self.gui.txtExclude.setText("")
                pass_exclude = []
            
        myUI2.populate(default_exclude=pass_exclude)
        myUI2.gui.show()

class UiFunc2:
    def __init__(self):
        self.gui = GUI_Select_Wavelengths()
        self.connections()

    def connections(self):
        self.gui.cmdSendExclude.clicked.connect(lambda: self.send(direction="in_to_ex"))
        self.gui.cmdSendInclude.clicked.connect(lambda: self.send(direction="ex_to_in"))
        self.gui.cmdAll.clicked.connect(lambda: self.select(select="all"))
        self.gui.cmdNone.clicked.connect(lambda: self.select(select="none"))
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())
        self.gui.cmdOK.clicked.connect(lambda: self.OK())

    def populate(self, default_exclude):
        if myUI.nbands < 10: width = 1
        elif myUI.nbands < 100: width = 2
        elif myUI.nbands < 1000: width = 3
        else: width = 4

        for i in xrange(myUI.nbands):
            if i in default_exclude:
                str_band_no = '{num:0{width}}'.format(num=i + 1, width=width)
                label = "band %s: %6.2f %s" % (str_band_no, myUI.wl[i], myUI.wunit)
                self.gui.lstExcluded.addItem(label)
            else:
                str_band_no = '{num:0{width}}'.format(num=i+1, width=width)
                label = "band %s: %6.2f %s" %(str_band_no, myUI.wl[i], myUI.wunit)
                self.gui.lstIncluded.addItem(label)

    def send(self, direction):
        if direction == "in_to_ex":
            origin = self.gui.lstIncluded
            destination = self.gui.lstExcluded
        elif direction == "ex_to_in":
            origin = self.gui.lstExcluded
            destination = self.gui.lstIncluded

        for item in origin.selectedItems():
            index = origin.indexFromItem(item).row()
            destination.addItem(origin.takeItem(index))

        origin.sortItems()
        destination.sortItems()

    def select(self, select):
        if select == "all":
            list_object = self.gui.lstIncluded
            direction = "in_to_ex"
        elif select == "none":
            list_object = self.gui.lstExcluded
            direction = "ex_to_in"

        for i in xrange(list_object.count()):
            item = list_object.item(i)
            list_object.setItemSelected(item, True)

        self.send(direction=direction)

    def OK(self): # buggy!
        # Read excluded bands form QListWidget
        list_object = self.gui.lstExcluded
        raw_list = []
        for i in xrange(list_object.count()):
            item = list_object.item(i).text()
            raw_list.append(item)

        myUI.exclude_bands = [int(raw_list[i].split(" ")[1][:-1])-1 for i in xrange(len(raw_list))]
        exclude_string = " ".join(str(x+1) for x in myUI.exclude_bands)
        myUI.gui.txtExclude.setText(exclude_string)

        for list_object in [self.gui.lstIncluded, self.gui.lstExcluded]:
            list_object.clear()

        self.gui.close()

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    myUI = UiFunc()
    myUI2 = UiFunc2()
    myUI.gui.show()
    sys.exit(app.exec_())


