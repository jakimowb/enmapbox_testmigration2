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

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_Global_Inversion.ui')
pathUI2 = os.path.join(os.path.dirname(__file__),'GUI_Select_Wavelengths.ui')
pathUI3 = os.path.join(os.path.dirname(__file__),'GUI_Nodat.ui')

from enmapbox.gui.utils import loadUIFormClass

class GUI_Global_Inversion(QDialog, loadUIFormClass(pathUI)):
    
    def __init__(self, parent=None):
        super(GUI_Global_Inversion, self).__init__(parent)
        self.setupUi(self)    

class GUI_Select_Wavelengths(QDialog, loadUIFormClass(pathUI2)):

    def __init__(self, parent=None):
        super(GUI_Select_Wavelengths, self).__init__(parent)
        self.setupUi(self)

class GUI_Nodat(QDialog, loadUIFormClass(pathUI3)):

    def __init__(self, parent=None):
        super(GUI_Nodat, self).__init__(parent)
        self.setupUi(self)

class UiFunc:

    def __init__(self):
        
        self.gui = GUI_Global_Inversion()
        self.initial_values()
        self.connections()
        self.select_sensor(self.sensor)

    def initial_values(self):
        self.ctype = 1
        self.nbfits = 0
        self.nbfits_type = "rel"
        self.noisetype = 0
        self.noiselevel = 0
        self.nodat = [-999] * 3
        self.exclude_bands, self.exclude_bands_model = (None, None)
        self.wl_compare = None
        self.inversion_range = None
        self.n_wl = None
        self.image = None
        self.out_path = None
        self.out_mode = "single"
        self.flags =[[0,0],[0],[0],[0,0]] # to be edited!

        self.geo_mode = "off"
        self.geo_file = None
        self.geo_fixed = [None]*3

        self.conversion_factor = None


        self.LUT_path = None
        self.sensor = 2 # 1 = ASD, 2 = EnMAP, 3 = Sentinel2, 4 = Landsat8
        self.wl = None

    def connections(self):

        # Input Images
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdInputLUT.clicked.connect(lambda: self.open_file(mode="lut"))
        self.gui.cmdInputMask.clicked.connect(lambda: self.open_file(mode="mask"))

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
        self.gui.cmdClose.clicked.connect(lambda: self.gui.close())

        self.gui.cmdDebug.clicked.connect(lambda: self.debug())

    def open_file(self, mode):
        if mode=="image":
            result = str(QFileDialog.getOpenFileName(caption='Select Input Image'))
            if not result: return
            self.image = result
            self.image = self.image.replace("\\", "/")
            meta = self.get_image_meta(image=self.image, image_type="Input Image")
            if None in meta:
                self.image = None
                self.nodat[0] = None
                self.gui.lblInputImage.setText("")
                return
            else:
                self.gui.lblInputImage.setText(result)
                self.gui.lblNodatImage.setText(str(meta[0]))
                self.nodat[0] = meta[0]
        elif mode=="lut":
            result = str(QFileDialog.getOpenFileName(caption='Select LUT meta-file', filter="LUT-file (*.lut)"))
            if not result: return
            self.LUT_path = result
            self.LUT_path = self.LUT_path.replace("\\", "/")
            self.gui.lblInputLUT.setText(result)
        elif mode=="output":
            result = str(QFileDialog.getSaveFileName(caption='Specify Output-file(s)', filter="ENVI Image (*.bsq)"))
            if not result: return
            self.out_path = result
            self.out_path = self.out_path.replace("\\", "/")
            self.gui.txtOutputImage.setText(result)
        elif mode=="geo":
            result = str(QFileDialog.getOpenFileName(caption='Select Geometry Image'))
            if not result: return
            self.geo_file = result
            self.geo_file = self.geo_file.replace("\\", "/")
            meta = self.get_image_meta(image=self.geo_file, image_type="Geometry Image")
            if None in meta:
                self.geo_file = None
                self.nodat[1] = None
                self.gui.lblGeoFromFile.setText("")
                return
            else:
                self.gui.lblGeoFromFile.setText(result)
                self.gui.lblNodatGeoImage.setText(str(meta[0]))
                self.nodat[1] = meta[0]
        elif mode=="mask":
            result = str(QFileDialog.getOpenFileName(caption='Select Mask Image'))
            if not result: return
            self.mask_image = result
            self.mask_image = self.mask_image.replace("\\", "/")
            meta = self.get_image_meta(image=self.mask_image, image_type="Mask Image")
            if meta[1] is None: # No Data is unimportant for mask file, but dimensions must exist (image readable)
                self.mask_image = None
                self.gui.lblInputMask.setText("")
                return
            else:
                self.gui.lblInputMask.setText(result)

    def select_outputmode(self, mode):
        self.out_mode = mode

    def select_sensor(self, sensor):
        self.sensor = sensor

        if sensor == 1: # ASD
            self.exclude_bands = range(0, 51) + range(1009, 1129) + range(1371, 1650) # 350-400nm, 1359-1479nm, 1721-200nm
        elif sensor == 2: # EnMAP
            self.exclude_bands = range(78, 88) + range(128, 138) + range(161, 189) # Überlappung VNIR, Water1, Water2
        elif sensor == 3: # Sentinel-2
            self.exclude_bands = [10]

        self.gui.txtExclude.setText(" ".join(str(i) for i in self.exclude_bands))
        self.gui.txtExclude.setCursorPosition(0)

    def select_geo(self, mode):
        if mode=="off":
            self.gui.lblGeoFromFile.setDisabled(True)
            self.gui.cmdGeoFromFile.setDisabled(True)
            self.gui.txtSZA.setDisabled(True)
            self.gui.txtOZA.setDisabled(True)
            self.gui.txtRAA.setDisabled(True)
        if mode=="file":
            self.gui.lblGeoFromFile.setDisabled(False)
            self.gui.cmdGeoFromFile.setDisabled(False)
            self.gui.txtSZA.setDisabled(True)
            self.gui.txtOZA.setDisabled(True)
            self.gui.txtRAA.setDisabled(True)
        if mode=="fix":
            self.gui.lblGeoFromFile.setDisabled(True)
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
        if self.image is None:
            self.abort(message='Input Image missing')
            return -1
        elif not os.path.isfile(self.image):
            self.abort(message='Input Image does not exist')
            return -1

        # LUT
        if self.LUT_path is None:
            self.abort(message='LUT metafile missing')
            return -1
        elif not os.path.isfile(self.LUT_path):
            self.abort(message='LUT metafile does not exist')
            return -1

        # Output path
        self.out_path = self.gui.txtOutputImage.text()
        self.out_path = self.out_path.replace("\\", "/")
        if self.out_path is None:
            self.abort(message='Output file missing')
            return -1
        else:
            try:
                os.path.splitext(self.out_path)[1]
            except:
                self.out_path += ".bsq"

        # Geometry file:
        if self.geo_mode == "file":
            if self.geo_file is None:
                self.abort(message='Geometry-Input via file selected, but no file specified')
                return -1
            elif not os.path.isfile(self.geo_file):
                self.abort(message='Geometry-Input file does not exist')
                return -1

        elif self.geo_mode == "fix":
            if self.gui.txtSZA.text() == "" or self.gui.txtOZA.text() == "" or self.gui.txtRAA.text() == "":
                self.abort(message='Geometry-Input via fixed values selected, but angles are incomplete')
                return -1
            else:
                try:
                    self.geo_fixed = [float(self.gui.txtSZA.text()), float(self.gui.txtOZA.text()), float(self.gui.txtRAA.text())]
                except ValueError:
                    self.abort(message='Cannot interpret Geometry angles as numbers')
                    return -1

        # Noise
        if not self.noisetype == 0:
            if self.gui.txtNoiseLevel.text() == "":
                self.abort(message='Please specify level for artificial noise')
                return -1
            else:
                self.noiselevel = self.gui.txtNoiseLevel.text()
                try:
                    self.noiselevel = float(self.noiselevel)
                except ValueError:
                    self.abort(message='Cannot interpret noise level as decimal number')
                    return -1

        # Cost Function Type:
        if self.nbfits_type == "rel":
            if self.gui.txtRel.text() == "":
                self.abort(message='Please specify number of best fits')
                return -1
            else:
                self.nbfits = self.gui.txtRel.text()
                try:
                    self.nbfits = float(self.nbfits)
                except ValueError:
                    self.abort(message='Cannot interpret number of best fits as a real number')
                    return -1
        elif self.nbfits_type == "abs":
            if self.gui.txtAbs.text() == "":
                self.abort(message='Please specify number of best fits')
                return -1
            else:
                self.nbfits = self.gui.txtAbs.text()
                try:
                    self.nbfits = int(self.nbfits)
                except ValueError:
                    self.abort(message='Cannot interpret number of best fits as a real number')
                    return -1

        # Mask
        if not self.mask_image is None and not os.path.isfile(self.mask_image):
            self.abort(message='Mask Image does not exist')
            return -1

        if self.gui.txtNodatOutput.text() == "":
            self.abort(message='Please specify no data value for output')
            return -1
        else:
            try:
                self.nodat[2] = int(self.gui.txtNodatOutput.text())
            except:
                self.abort(message='%s is not a valid no data value for output' % self.gui.txtNodatOutput.text())
                return -1

        return 1

    def get_image_meta(self, image, image_type):

        dataset = gdal.Open(image)
        if dataset is None:
            self.abort(message='%s could not be read. Please make sure it is a valid ENVI image' % image_type)
            return None
        else:
            nbands = dataset.RasterCount
            nrows = dataset.RasterYSize
            ncols = dataset.RasterXSize
            if image_type=="Mask Image": return nbands, nrows, ncols

            try:
                nodata = int("".join(dataset.GetMetadataItem('data_ignore_value', 'ENVI').split()))
                return nodata, nbands, nrows, ncols
            except:
                myUI3.init(image_type=image_type, image=image)
                myUI3.gui.setModal(True) # parent window is blocked
                myUI3.gui.exec_() # unlike .show(), .exec_() waits with execution of the code, until the app is closed
                return myUI3.nodat, nbands, nrows, ncols

    def run_inversion(self):

        cas = self.check_and_assign()
        if cas < 0:
            return

        inv = inverse.RTM_Inversion()
        inv_setup = inv.inversion_setup(image=self.image, image_out=self.out_path, LUT_path=self.LUT_path, ctype=self.ctype,
                            nbfits=self.nbfits, nbfits_type=self.nbfits_type, noisetype=self.noisetype,
                            noiselevel=self.noiselevel, exclude_bands=self.exclude_bands, geo_image=self.geo_file,
                            geo_fixed=self.geo_fixed, sensor=self.sensor, mask_image=self.mask_image, out_mode=self.out_mode,
                            nodat=self.nodat, which_para=range(15))
        if inv_setup:
            self.abort(message=inv_setup)
            return

        run_inv = inv.run_inversion()
        if run_inv:
            self.abort(message=run_inv)
            return

        write_inv = inv.write_image()
        if write_inv:
            self.abort(message=write_inv)
            return

        QMessageBox.information(self.gui, "Finish", "Inversion finished")

    def invoke_selection(self):

        # Check ImageIn
        if self.image is None:
            self.abort(message='Specify Input Image first')
            return
        elif not os.path.isfile(self.image):
            self.abort(message='Input Image not found')
            return

        # Read ImageIn
        dataset = gdal.Open(self.image)
        if dataset is None:
            self.abort(message='Input Image could not be read. Please make sure it is a valid ENVI image')
            return
        wavelengths = "".join(dataset.GetMetadataItem('wavelength', 'ENVI').split())
        wavelengths = wavelengths.replace("{","")
        wavelengths = wavelengths.replace("}", "")
        wavelengths = wavelengths.split(",")

        if dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['nanometers', 'nm', 'nanometer']:
            wave_convert = 1
            self.wunit = u'nm'
        elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['micrometers', 'µm', 'micrometer']:
            wave_convert = 1000
            self.wunit = u"\u03bcm"
        else:
            self.abort(message="No wavelength units provided in ENVI header file")
            return

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
        myUI2.gui.setModal(True)
        myUI2.gui.show()

    def debug(self):

        self.image = "D:/Temp/LUT/WW_nadir_short.bsq"
        self.out_path = "D:/Temp/LUT/Out/myresults.bsq"
        self.LUT_path = "D:/Temp/LUT/Test_Lut_00meta.lut"
        self.ctype = 2
        self.nbfits = 20
        self.nbfits_type = "abs"
        self.noisetype = 1
        self.noiselevel = 5.0
        self.geo_file = None
        self.geo_fixed = [35.0, 0.0, 0.0]
        self.sensor = 1
        self.mask_image = None
        self.out_mode = "individual"

        inv = inverse.RTM_Inversion()
        inv_setup = inv.inversion_setup(image=self.image, image_out=self.out_path, LUT_path=self.LUT_path, ctype=self.ctype,
                            nbfits=self.nbfits, nbfits_type=self.nbfits_type, noisetype=self.noisetype,
                            noiselevel=self.noiselevel, exclude_bands=[], geo_image=self.geo_file,
                            geo_fixed=self.geo_fixed, sensor=self.sensor, mask_image=self.mask_image, out_mode=self.out_mode,
                            nodat=[-999]*3, which_para=range(15))
        if inv_setup:
            self.abort(message=inv_setup)
            return

        run_inv = inv.run_inversion()
        if run_inv:
            self.abort(message=run_inv)
            return

        write_inv = inv.write_image()
        if write_inv:
            self.abort(message=write_inv)
            return

        QMessageBox.information(self.gui, "Finish", "Inversion finished")

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

    def OK(self):
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

class UiFunc3:
    def __init__(self):
        self.gui = GUI_Nodat()
        self.connections()
        self.image = None

    def init(self, image_type, image):
        topstring = '%s @ %s' % (image_type, image)
        self.gui.lblSource.setText(topstring)
        self.gui.txtNodat.setText("")
        # if image_type == "Input Image": self.which_nodat = 0
        # elif image_type == "Geometry Image": self.which_nodat = 1
        # elif image_type == "Output Image": self.which_nodat = 2
        self.image = image
        self.nodat = None

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())
        self.gui.cmdOK.clicked.connect(lambda: self.OK())

    def OK(self):
        if self.gui.txtNodat.text() == "":
            QMessageBox.critical(self.gui, "No Data", "A no data value must be supplied for this image!")
            return
        else:
            try:
                nodat = int(self.gui.txtNodat.text())
            except:
                QMessageBox.critical(self.gui, "No number", "'%s' is not a valid number" % self.gui.txtNodat.text())
                self.gui.txtNodat.setText("")
                return
        self.nodat = nodat
        self.gui.close()

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    myUI = UiFunc()
    myUI2 = UiFunc2()
    myUI3 = UiFunc3()
    myUI.gui.show()
    sys.exit(app.exec_())


