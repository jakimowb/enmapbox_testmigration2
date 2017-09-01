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
pathUI_prg = os.path.join(os.path.dirname(__file__),'GUI_ProgressBar.ui')

from enmapbox.gui.utils import loadUIFormClass

class Global_Inversion_GUI(QDialog, loadUIFormClass(pathUI)):
    
    def __init__(self, parent=None):
        super(Global_Inversion_GUI, self).__init__(parent)
        self.setupUi(self)

class Select_Wavelengths_GUI(QDialog, loadUIFormClass(pathUI2)):

    def __init__(self, parent=None):
        super(Select_Wavelengths_GUI, self).__init__(parent)
        self.setupUi(self)

class Nodat_GUI(QDialog, loadUIFormClass(pathUI3)):

    def __init__(self, parent=None):
        super(Nodat_GUI, self).__init__(parent)
        self.setupUi(self)

class PRG_GUI(QDialog, loadUIFormClass(pathUI_prg)):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        self.setupUi(self)

class Global_Inversion:

    def __init__(self, main):
        self.main = main
        self.gui = Global_Inversion_GUI()
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
        self.mask_image = None
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
        self.gui.cmdExcludeBands.clicked.connect(lambda: self.open_wavelength_selection())
        self.gui.cmdRun.clicked.connect(lambda: self.run_inversion())
        self.gui.cmdClose.clicked.connect(lambda: self.gui.close())

        self.gui.cmdDebug.clicked.connect(lambda: self.debug())

    def open_file(self, mode):
        if mode=="image":
            result = str(QFileDialog.getOpenFileName(caption='Select Input Image'))
            if not result: return
            self.image = result
            self.image = self.image.replace("\\", "/")
            try:
                meta = self.get_image_meta(image=self.image, image_type="Input Image")
            except ValueError as e:
                self.abort(message=str(e))
                return
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
        if self.image is None: raise ValueError('Input Image missing')
        elif not os.path.isfile(self.image): raise ValueError('Input Image does not exist')

        # LUT
        if self.LUT_path is None: raise ValueError('LUT metafile missing')
        elif not os.path.isfile(self.LUT_path): raise ValueError('LUT metafile does not exist')

        # Output path
        self.out_path = self.gui.txtOutputImage.text()
        self.out_path = self.out_path.replace("\\", "/")
        if self.out_path is None: raise ValueError('Output file missing')
        else:
            try:
                os.path.splitext(self.out_path)[1]
            except:
                self.out_path += ".bsq"

        # Geometry file:
        if self.geo_mode == "file":
            if self.geo_file is None: raise ValueError('Geometry-Input via file selected, but no file specified')
            elif not os.path.isfile(self.geo_file): raise ValueError('Geometry-Input file does not exist')

        elif self.geo_mode == "fix":
            if self.gui.txtSZA.text() == "" or self.gui.txtOZA.text() == "" or self.gui.txtRAA.text() == "":
                raise ValueError('Geometry-Input via fixed values selected, but angles are incomplete')
            else:
                try:
                    self.geo_fixed = [float(self.gui.txtSZA.text()), float(self.gui.txtOZA.text()), float(self.gui.txtRAA.text())]
                except ValueError:
                    raise ValueError('Cannot interpret Geometry angles as numbers')

        # Noise
        if not self.noisetype == 0:
            if self.gui.txtNoiseLevel.text() == "": raise ValueError('Please specify level for artificial noise')

            else:
                self.noiselevel = self.gui.txtNoiseLevel.text()
                try:
                    self.noiselevel = float(self.noiselevel)
                except ValueError:
                    raise ValueError('Cannot interpret noise level as decimal number')

        # Cost Function Type:
        if self.nbfits_type == "rel":
            if self.gui.txtRel.text() == "": raise ValueError('Please specify number of best fits')
            else:
                self.nbfits = self.gui.txtRel.text()
                try:
                    self.nbfits = float(self.nbfits)
                except ValueError:
                    raise ValueError('Cannot interpret number of best fits as a real number')

        elif self.nbfits_type == "abs":
            if self.gui.txtAbs.text() == "": raise ValueError('Please specify number of best fits')
            else:
                self.nbfits = self.gui.txtAbs.text()
                try:
                    self.nbfits = int(self.nbfits)
                except ValueError:
                    raise ValueError('Cannot interpret number of best fits as a real number')

        # Mask
        if not self.mask_image is None:
            if not os.path.isfile(self.mask_image): raise ValueError('Mask Image does not exist')

        if self.gui.txtNodatOutput.text() == "": raise ValueError('Please specify no data value for output')
        else:
            try:
                self.nodat[2] = int(self.gui.txtNodatOutput.text())
            except:
                raise ValueError('%s is not a valid no data value for output' % self.gui.txtNodatOutput.text())

    def get_image_meta(self, image, image_type):

        dataset = gdal.Open(image)
        if dataset is None: raise ValueError('%s could not be read. Please make sure it is a valid ENVI image' % image_type)
        else:
            nbands = dataset.RasterCount
            nrows = dataset.RasterYSize
            ncols = dataset.RasterXSize
            if image_type=="Mask Image": return nbands, nrows, ncols

            try:
                nodata = int("".join(dataset.GetMetadataItem('data_ignore_value', 'ENVI').split()))
                return nodata, nbands, nrows, ncols
            except:
                self.main.nodat_widget.init(image_type=image_type, image=image)
                self.main.nodat_widget.gui.setModal(True) # parent window is blocked
                self.main.nodat_widget.gui.exec_() # unlike .show(), .exec_() waits with execution of the code, until the app is closed
                return self.main.nodat_widget.nodat, nbands, nrows, ncols

    def run_inversion(self):

        try:
            self.check_and_assign()
        except ValueError as e:
            self.abort(message=str(e))
            return

        self.prg_widget = self.main.prg_widget
        self.prg_widget.gui.lblCaption_l.setText("Global Inversion")
        self.prg_widget.gui.lblCaption_r.setText("Setting up inversion...")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.prg_widget.gui.show()

        self.main.QGis_app.processEvents()

        inv = inverse.RTM_Inversion()

        # try:
        #     inv.inversion_setup(image=self.image, image_out=self.out_path, LUT_path=self.LUT_path, ctype=self.ctype,
        #                         nbfits=self.nbfits, nbfits_type=self.nbfits_type, noisetype=self.noisetype,
        #                         noiselevel=self.noiselevel, exclude_bands=self.exclude_bands, geo_image=self.geo_file,
        #                         geo_fixed=self.geo_fixed, sensor=self.sensor, mask_image=self.mask_image, out_mode=self.out_mode,
        #                         nodat=self.nodat, which_para=range(15))
        # except ValueError as e:
        #     self.abort(message="Failed to setup inversion: %s" % str(e))
        #     return


        inv.inversion_setup(image=self.image, image_out=self.out_path, LUT_path=self.LUT_path, ctype=self.ctype,
                                nbfits=self.nbfits, nbfits_type=self.nbfits_type, noisetype=self.noisetype,
                                noiselevel=self.noiselevel, exclude_bands=self.exclude_bands, geo_image=self.geo_file,
                                geo_fixed=self.geo_fixed, sensor=self.sensor, mask_image=self.mask_image, out_mode=self.out_mode,
                                nodat=self.nodat, which_para=range(15))

        try:
            inv.run_inversion(prg_widget=self.prg_widget, QGis_app=self.main.QGis_app)
        except ValueError as e:
            self.abort(message="An error occurred during inversion: %s" % str(e))
            return

        self.prg_widget.gui.lblCaption_r.setText("Writing Output-File...")
        self.main.QGis_app.processEvents()

        try:
            inv.write_image()
        except ValueError as e:
            self.abort(message="An error occurred while trying to write output-image: %s" % str(e))
            return

        self.prg_widget.gui.close()
        QMessageBox.information(self.gui, "Finish", "Inversion finished")
        self.gui.close()

    def open_wavelength_selection(self):
        try:
            self.invoke_selection()
        except ValueError as e:
            self.abort(message=str(e))

    def invoke_selection(self):
        # Check ImageIn
        if self.image is None: raise ValueError('Specify Input Image first')
        elif not os.path.isfile(self.image): raise ValueError('Input Image not found')

        # Read ImageIn
        dataset = gdal.Open(self.image)
        if dataset is None: raise ValueError('Input Image could not be read. Please make sure it is a valid ENVI image')

        try:
            wavelengths = "".join(dataset.GetMetadataItem('wavelength', 'ENVI').split())
            wavelengths = wavelengths.replace("{","")
            wavelengths = wavelengths.replace("}", "")
            wavelengths = wavelengths.split(",")
        except ValueError:
            raise ValueError('Input Image does not have wavelengths supplied. Check header file!')

        if dataset.GetMetadataItem('wavelength_units', 'ENVI') is None:
            raise ValueError('No wavelength units provided in ENVI header file')
        elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['nanometers', 'nm', 'nanometer']:
            wave_convert = 1
            self.wunit = u'nm'
        elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['micrometers', 'µm', 'micrometer']:
            wave_convert = 1000
            self.wunit = u"\u03bcm"
        else:
            raise ValueError("Wavelength units must be nanometers or micrometers. Got '%s' instead" % dataset.GetMetadataItem('wavelength_units', 'ENVI'))

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

        self.main.select_wavelengths.populate(default_exclude=pass_exclude)
        self.main.select_wavelengths.gui.setModal(True)
        self.main.select_wavelengths.gui.show()

    def debug(self):

        self.image = "D:/Temp/LUT/WW_0.bsq"
        self.out_path = "D:/Temp/LUT/debug/Restuls_Five.bsq"
        self.LUT_path = "D:/Temp/LUT/debug/Five_00meta.lut"
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
        self.prg_widget = self.main.prg_widget
        self.exclude_bands = range(0, 50) + range(1009, 1129) + range(1371, 1650) # 350-400nm, 1359-1479nm, 1721-200nm

        self.prg_widget.gui.lblCaption_l.setText("Global Inversion")
        self.prg_widget.gui.lblCaption_r.setText("Setting up inversion...")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.prg_widget.gui.show()

        self.main.QGis_app.processEvents()

        inv = inverse.RTM_Inversion()
        inv_setup = inv.inversion_setup(image=self.image, image_out=self.out_path, LUT_path=self.LUT_path, ctype=self.ctype,
                            nbfits=self.nbfits, nbfits_type=self.nbfits_type, noisetype=self.noisetype,
                            noiselevel=self.noiselevel, exclude_bands=self.exclude_bands, geo_image=self.geo_file,
                            geo_fixed=self.geo_fixed, sensor=self.sensor, mask_image=self.mask_image, out_mode=self.out_mode,
                            nodat=[-999]*3, which_para=range(15))

        if inv_setup:
            self.abort(message=inv_setup)
            return

        run_inv = inv.run_inversion(prg_widget=self.prg_widget, QGis_app=self.main.QGis_app)
        if run_inv:
            self.abort(message=run_inv)
            return

        self.prg_widget.gui.lblCaption_r.setText("Writing Output-File...")
        self.main.QGis_app.processEvents()

        write_inv = inv.write_image()
        if write_inv:
            self.abort(message=write_inv)
            return

        self.prg_widget.gui.close()
        QMessageBox.information(self.gui, "Finish", "Inversion finished")
        self.gui.close()

class Select_Wavelengths:
    def __init__(self, main):
        self.main = main
        self.gui = Select_Wavelengths_GUI()
        self.connections()

    def connections(self):
        self.gui.cmdSendExclude.clicked.connect(lambda: self.send(direction="in_to_ex"))
        self.gui.cmdSendInclude.clicked.connect(lambda: self.send(direction="ex_to_in"))
        self.gui.cmdAll.clicked.connect(lambda: self.select(select="all"))
        self.gui.cmdNone.clicked.connect(lambda: self.select(select="none"))
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())
        self.gui.cmdOK.clicked.connect(lambda: self.OK())

    def populate(self, default_exclude):
        if self.main.global_inversion.nbands < 10: width = 1
        elif self.main.global_inversion.nbands < 100: width = 2
        elif self.main.global_inversion.nbands < 1000: width = 3
        else: width = 4

        for i in xrange(self.main.global_inversion.nbands):
            if i in default_exclude:
                str_band_no = '{num:0{width}}'.format(num=i + 1, width=width)
                label = "band %s: %6.2f %s" % (str_band_no, self.main.global_inversion.wl[i], self.main.global_inversion.wunit)
                self.gui.lstExcluded.addItem(label)
            else:
                str_band_no = '{num:0{width}}'.format(num=i+1, width=width)
                label = "band %s: %6.2f %s" %(str_band_no, self.main.global_inversion.wl[i], self.main.global_inversion.wunit)
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
        self.gui.setDisabled(False)

    def select(self, select):
        self.gui.setDisabled(True)
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

        self.main.global_inversion.exclude_bands = [int(raw_list[i].split(" ")[1][:-1])-1 for i in xrange(len(raw_list))]
        exclude_string = " ".join(str(x+1) for x in self.main.global_inversion.exclude_bands)
        self.main.global_inversion.gui.txtExclude.setText(exclude_string)

        for list_object in [self.gui.lstIncluded, self.gui.lstExcluded]:
            list_object.clear()

        self.gui.close()

class Nodat:
    def __init__(self, main):
        self.main = main
        self.gui = Nodat_GUI()
        self.connections()
        self.image = None

    def init(self, image_type, image):
        topstring = '%s @ %s' % (image_type, image)
        self.gui.lblSource.setText(topstring)
        self.gui.txtNodat.setText("")
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

class PRG:
    def __init__(self, main):
        self.main = main
        self.gui = PRG_GUI()
        self.connections()

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.gui.close())


class MainUiFunc:
    def __init__(self):
        self.QGis_app = QApplication.instance()
        self.global_inversion = Global_Inversion(self)
        self.select_wavelengths = Select_Wavelengths(self)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.global_inversion.gui.show()

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    m = MainUiFunc()
    m.show()
    app.exec_()


