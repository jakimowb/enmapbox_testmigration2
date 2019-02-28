# -*- coding: utf-8 -*-


import sys
import os
import numpy as np
from scipy.interpolate import interp1d
from qgis.gui import *

#ensure to call QGIS before PyQtGraph
#from qgis.PyQt.QtCore import *
#from qgis.PyQt.QtGui import *

from qgis.PyQt.QtWidgets import *
from qgis.PyQt import uic
import pyqtgraph as pg
from lmuvegetationapps import call_model as mod
from enmapbox.gui.applications import EnMAPBoxApplication
from lmuvegetationapps.Spec2Sensor_cl import Spec2Sensor
#import enmapboxtestdata
import warnings
import csv

from enmapbox.gui.utils import loadUIFormClass

#import time

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_IVVRM_Inform_alpha.ui')
pathUI2 = os.path.join(os.path.dirname(__file__), 'GUI_LoadTxtFile.ui')
pathUI3 = os.path.join(os.path.dirname(__file__), 'GUI_Select_Wavelengths.ui')


class IVVRM_GUI(QDialog, loadUIFormClass(pathUI)):
    def __init__(self, parent=None):
        super(IVVRM_GUI, self).__init__(parent)
        self.setupUi(self)

class Load_Txt_File_GUI(QDialog, loadUIFormClass(pathUI2)):
    def __init__(self, parent=None):
        super(Load_Txt_File_GUI, self).__init__(parent)
        self.setupUi(self)

class Select_Wavelengths_GUI(QDialog, loadUIFormClass(pathUI3)):
    def __init__(self, parent=None):
        super(Select_Wavelengths_GUI, self).__init__(parent)
        self.setupUi(self)

class IVVRM:

    def __init__(self, main):
        self.main = main
        self.gui = IVVRM_GUI()
        self.special_chars()
        self.initial_values()
        self.update_slider_pos()
        self.update_lineEdit_pos()
        self.deactivate_sliders()
        self.para_init()
        self.select_model()
        self.mod_interactive()
        self.mod_exec()


    def special_chars(self):
        self.gui.lblCab.setText(u'[µg/cm²]')
        self.gui.lblCm.setText(u'[g/cm²]')
        self.gui.lblCar.setText(u'[µg/cm²]')
        self.gui.lblCanth.setText(u'[µg/cm²]')
        self.gui.lblCp.setText(u'[g/cm²]')
        self.gui.lblCcl.setText(u'[g/cm²]')
        self.gui.lblLAI.setText(u'[m²/m²]')

    def initial_values(self):
        self.lop = "prospectD"
        self.canopy_arch = "sail"
        self.colors = [tuple([219,183,255]), tuple([51,204,51]), tuple([69,30,234]), tuple([0,255,255]),
                        tuple([255,255,0]), tuple([0,0,0]), tuple([255,0,0]), tuple([255,255,255]),
                        tuple([255,124,128]), tuple([178,178,178]), tuple([144, 204, 154]),
                        tuple([255,153,255]), tuple([25,41,70]), tuple([169,139,100]),
                       tuple([255,153,51]), tuple([204, 0, 153]), tuple([172, 86, 38]), tuple([0,100,0]),
                       tuple([255,128,0]), tuple([153,76,0]), tuple([153,0,0])]
        self.lineEdits = [self.gui.N_lineEdit, self.gui.Cab_lineEdit, self.gui.Cw_lineEdit, self.gui.Cm_lineEdit,
                          self.gui.LAI_lineEdit, self.gui.lblFake, self.gui.LIDFB_lineEdit, self.gui.hspot_lineEdit,
                          self.gui.psoil_lineEdit, self.gui.SZA_lineEdit, self.gui.OZA_lineEdit, self.gui.rAA_lineEdit,
                          self.gui.Cp_lineEdit, self.gui.Ccl_lineEdit, self.gui.Car_lineEdit, self.gui.Canth_lineEdit,
                          self.gui.Cbrown_lineEdit, self.gui.LAIu_lineEdit, self.gui.CD_lineEdit, self.gui.SD_lineEdit,
                          self.gui.TreeH_lineEdit]
        self.para_names = ["N", "cab", "cw", "cm", "LAI", "typeLIDF", "LIDF", "hspot", "psoil", "tts", "tto", "psi",
                           "cp", "ccl", "car", "anth", "cbrown", "LAIu", "cd", "sd", "h"]
        self.lineEdits_dict = dict(zip(self.para_names, self.lineEdits))
        self.colors_dict = dict(zip(self.para_names, self.colors))
        self.penStyle = 1
        self.item = 1
        # self.plot_color = dict(zip(range(7), ["g", "r", "b", "y", "m", "c", "w"]))
        self.plot_count = 0
        self.current_slider = None

        self.data_mean = None
        self.para_dict = dict(zip(self.para_names, [None]*len(self.para_names)))
        self.para_dict["typeLIDF"] = 2
        self.bg_spec = None
        self.bg_type = "default"

    def update_slider_pos(self):
        self.gui.N_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.N_Slide, self.gui.N_lineEdit))
        self.gui.Cab_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Cab_Slide, self.gui.Cab_lineEdit))
        self.gui.Cw_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Cw_Slide, self.gui.Cw_lineEdit))
        self.gui.Cm_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Cm_Slide, self.gui.Cm_lineEdit))
        self.gui.Cp_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Cp_Slide, self.gui.Cp_lineEdit))
        self.gui.Ccl_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Ccl_Slide, self.gui.Ccl_lineEdit))
        self.gui.Car_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Car_Slide, self.gui.Car_lineEdit))
        self.gui.Canth_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Canth_Slide, self.gui.Canth_lineEdit))
        self.gui.Cbrown_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.Cbrown_Slide, self.gui.Cbrown_lineEdit))
        self.gui.LAI_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.LAI_Slide, self.gui.LAI_lineEdit))
        self.gui.LIDFB_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.LIDFB_Slide, self.gui.LIDFB_lineEdit))
        self.gui.hspot_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.hspot_Slide, self.gui.hspot_lineEdit))
        self.gui.psoil_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.psoil_Slide, self.gui.psoil_lineEdit))
        self.gui.OZA_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.OZA_Slide, self.gui.OZA_lineEdit))
        self.gui.SZA_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.SZA_Slide, self.gui.SZA_lineEdit))
        self.gui.rAA_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.rAA_Slide, self.gui.rAA_lineEdit))
        self.gui.LAIu_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.LAIu_Slide, self.gui.LAIu_lineEdit))
        self.gui.SD_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.SD_Slide, self.gui.SD_lineEdit))
        self.gui.TreeH_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.TreeH_Slide, self.gui.TreeH_lineEdit))
        self.gui.CD_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.CD_Slide, self.gui.CD_lineEdit))
    
    def update_lineEdit_pos(self):
        self.gui.N_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.N_lineEdit, self.gui.N_Slide))
        self.gui.Cab_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Cab_lineEdit, self.gui.Cab_Slide))
        self.gui.Cw_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Cw_lineEdit, self.gui.Cw_Slide))
        self.gui.Cm_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Cm_lineEdit, self.gui.Cm_Slide))
        self.gui.Cp_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Cp_lineEdit, self.gui.Cp_Slide))
        self.gui.Ccl_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Ccl_lineEdit, self.gui.Ccl_Slide))
        self.gui.Car_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Car_lineEdit, self.gui.Car_Slide))
        self.gui.Canth_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Canth_lineEdit, self.gui.Canth_Slide))
        self.gui.Cbrown_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.Cbrown_lineEdit, self.gui.Cbrown_Slide))
        self.gui.LAI_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.LAI_lineEdit, self.gui.LAI_Slide))
        self.gui.LIDFB_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.LIDFB_lineEdit, self.gui.LIDFB_Slide))
        self.gui.hspot_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.hspot_lineEdit, self.gui.hspot_Slide))
        self.gui.psoil_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.psoil_lineEdit, self.gui.psoil_Slide))
        self.gui.OZA_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.OZA_lineEdit, self.gui.OZA_Slide))
        self.gui.SZA_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.SZA_lineEdit, self.gui.SZA_Slide))
        self.gui.rAA_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.rAA_lineEdit, self.gui.rAA_Slide))
        self.gui.LAIu_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.LAIu_lineEdit, self.gui.LAIu_Slide))
        self.gui.SD_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.SD_lineEdit, self.gui.SD_Slide))
        self.gui.TreeH_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.TreeH_lineEdit, self.gui.TreeH_Slide))
        self.gui.CD_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.CD_lineEdit, self.gui.CD_Slide))

    def any_slider_change(self, slider, textfeld):
        if not self.current_slider == slider:
            self.plot_count += 1
        self.current_slider = slider
        my_value = str(slider.value() / 10000.0)
        textfeld.setText(my_value)

    def any_lineEdit_change(self, textfeld, slider,):
        try:
            my_value = int(float(textfeld.text()) * 10000)
            slider.setValue(my_value)
        except ValueError:
            QMessageBox.critical(self.gui, "Not a number", "'%s' is not a valid number" % textfeld.text())
            textfeld.setText(str(slider.value() / 10000.0))

    def select_s2s(self, sensor, trigger=True):
        self.sensor = sensor
        if sensor in ["EnMAP", "Sentinel2", "Landsat8"]:
            s2s = Spec2Sensor(sensor=sensor, nodat=-999)
            s2s.init_sensor()
            self.wl = s2s.wl_sensor
            self.plot_count += 1
        else:
            self.wl = range(400, 2501)

        if trigger:
            self.makePen(sensor=sensor)
            self.mod_exec()

    def select_background(self,bg_type):
        self.bg_type = bg_type
        if bg_type == "default":
            self.gui.B_DefSoilSpec.setEnabled(True)
            self.gui.B_LoadBackSpec.setEnabled(True)
            self.gui.BrightFac_Text.setEnabled(True)
            self.gui.psoil_Slide.setEnabled(True)
            self.gui.psoil_lineEdit.setEnabled(True)
            self.gui.push_SelectFile.setEnabled(False)
            self.gui.BackSpec_label.setEnabled(False)
            self.gui.BackSpec_label.setText("")
            self.bg_spec = None
            self.mod_exec()
        elif bg_type == "load":
            self.gui.B_DefSoilSpec.setEnabled(True)
            self.gui.B_LoadBackSpec.setEnabled(True)
            self.gui.BrightFac_Text.setEnabled(False)
            self.gui.psoil_Slide.setEnabled(False)
            self.gui.psoil_lineEdit.setEnabled(False)
            self.gui.push_SelectFile.setEnabled(True)
            self.gui.push_SelectFile.setText('Select File...')
            self.gui.BackSpec_label.setEnabled(True)


    def makePen(self, sensor):
        if sensor == "default":
            self.penStyle = 1
        elif sensor == "EnMAP":
            self.penStyle = 3
        elif sensor == "Sentinel2":
            self.penStyle = 2
        elif sensor == "Landsat8":
            self.penStyle = 4

    def select_LIDF(self, index):
        if index > 0:
            self.para_dict["typeLIDF"] = 1 # Beta Distribution
            self.para_dict["LIDF"] = index - 1
            self.gui.LIDFB_Slide.setDisabled(True)
            self.gui.LIDFB_lineEdit.setDisabled(True)
            self.mod_exec(item="LIDF")
        else:
            self.para_dict["typeLIDF"] = 2 # Ellipsoidal Distribution
            self.mod_exec(self.gui.LIDFB_Slide, item="LIDF")
            self.gui.LIDFB_Slide.setDisabled(False)
            self.gui.LIDFB_lineEdit.setDisabled(False)

    def deactivate_sliders(self):

        # Models
        self.gui.B_Prospect4.clicked.connect(lambda: self.select_model(lop="prospect4", canopy_arch=self.canopy_arch))
        self.gui.B_Prospect5.clicked.connect(lambda: self.select_model(lop="prospect5", canopy_arch=self.canopy_arch))
        self.gui.B_Prospect5b.clicked.connect(lambda: self.select_model(lop="prospect5B", canopy_arch=self.canopy_arch))
        self.gui.B_ProspectD.clicked.connect(lambda: self.select_model(lop="prospectD", canopy_arch=self.canopy_arch))
        self.gui.B_ProspectCp.clicked.connect(lambda: self.select_model(lop="prospectCp", canopy_arch=self.canopy_arch))

        self.gui.B_LeafModelOnly.clicked.connect(lambda: self.select_model(lop=self.lop, canopy_arch=None))
        self.gui.B_4Sail.clicked.connect(lambda: self.select_model(lop=self.lop, canopy_arch="sail"))
        self.gui.B_Inform.clicked.connect(lambda: self.select_model(lop=self.lop, canopy_arch="inform"))


    def select_model(self, lop="prospectD", canopy_arch="sail"):
        self.lop = lop

        if canopy_arch is None:
            self.canopy_arch = None
            self.gui.CanopyMP_Box.setDisabled(True)
            self.gui.ForestMP_Box.setDisabled(True)
            self.gui.BrightFac_Text.setEnabled(False)
            self.gui.psoil_Slide.setEnabled(False)
            self.gui.psoil_lineEdit.setEnabled(False)
            self.gui.push_SelectFile.setEnabled(False)
            self.gui.BackSpec_label.setEnabled(False)
            self.gui.B_DefSoilSpec.setEnabled(False)
            self.gui.B_LoadBackSpec.setEnabled(False)
            self.gui.LAI_Text.setText("Leaf Area Index (LAI)")

        elif canopy_arch == "inform":
            self.canopy_arch = canopy_arch
            self.gui.LAI_Text.setText("Single Tree Leaf Area Index (LAI)")
            self.gui.CanopyMP_Box.setDisabled(False)
            self.gui.ForestMP_Box.setDisabled(False)
            self.select_background(bg_type=self.bg_type)

        else:
            self.canopy_arch = canopy_arch
            self.gui.LAI_Text.setText("Leaf Area Index (LAI)")
            self.gui.CanopyMP_Box.setDisabled(False)
            self.gui.ForestMP_Box.setDisabled(True)
            self.select_background(bg_type=self.bg_type)

        if lop == "prospectD":
            self.gui.Canth_Slide.setDisabled(False)
            self.gui.Canth_lineEdit.setDisabled(False)
            self.gui.Canth_Text.setDisabled(False)

            self.gui.Cbrown_Slide.setDisabled(False)
            self.gui.Cbrown_lineEdit.setDisabled(False)
            self.gui.Cbrown_Text.setDisabled(False)

            self.gui.Car_Slide.setDisabled(False)
            self.gui.Car_lineEdit.setDisabled(False)
            self.gui.Car_Text.setDisabled(False)

            self.gui.Cp_Slide.setDisabled(True)
            self.gui.Cp_lineEdit.setDisabled(True)
            self.gui.Cp_Text.setDisabled(True)

            self.gui.Ccl_Slide.setDisabled(True)
            self.gui.Ccl_lineEdit.setDisabled(True)
            self.gui.Ccl_Text.setDisabled(True)

        elif lop == "prospectCp":
            self.gui.Canth_Slide.setDisabled(False)
            self.gui.Canth_lineEdit.setDisabled(False)
            self.gui.Canth_Text.setDisabled(False)

            self.gui.Cbrown_Slide.setDisabled(False)
            self.gui.Cbrown_lineEdit.setDisabled(False)
            self.gui.Cbrown_Text.setDisabled(False)

            self.gui.Car_Slide.setDisabled(False)
            self.gui.Car_lineEdit.setDisabled(False)
            self.gui.Car_Text.setDisabled(False)

            self.gui.Cp_Slide.setDisabled(False)
            self.gui.Cp_lineEdit.setDisabled(False)
            self.gui.Cp_Text.setDisabled(False)
    
            self.gui.Ccl_Slide.setDisabled(False)
            self.gui.Ccl_lineEdit.setDisabled(False)
            self.gui.Ccl_Text.setDisabled(False)

        elif lop == "prospect5B":
            self.gui.Canth_Slide.setDisabled(True)
            self.gui.Canth_lineEdit.setDisabled(True)
            self.gui.Canth_Text.setDisabled(True)

            self.gui.Cbrown_Slide.setDisabled(False)
            self.gui.Cbrown_lineEdit.setDisabled(False)
            self.gui.Cbrown_Text.setDisabled(False)

            self.gui.Car_Slide.setDisabled(False)
            self.gui.Car_lineEdit.setDisabled(False)
            self.gui.Car_Text.setDisabled(False)

            self.gui.Cp_Slide.setDisabled(True)
            self.gui.Cp_lineEdit.setDisabled(True)
            self.gui.Cp_Text.setDisabled(True)

            self.gui.Ccl_Slide.setDisabled(True)
            self.gui.Ccl_lineEdit.setDisabled(True)
            self.gui.Ccl_Text.setDisabled(True)

        elif lop == "prospect5":
            self.gui.Canth_Slide.setDisabled(True)
            self.gui.Canth_lineEdit.setDisabled(True)
            self.gui.Canth_Text.setDisabled(True)

            self.gui.Cbrown_Slide.setDisabled(True)
            self.gui.Cbrown_lineEdit.setDisabled(True)
            self.gui.Cbrown_Text.setDisabled(True)

            self.gui.Car_Slide.setDisabled(False)
            self.gui.Car_lineEdit.setDisabled(False)
            self.gui.Car_Text.setDisabled(False)

            self.gui.Cp_Slide.setDisabled(True)
            self.gui.Cp_lineEdit.setDisabled(True)
            self.gui.Cp_Text.setDisabled(True)

            self.gui.Ccl_Slide.setDisabled(True)
            self.gui.Ccl_lineEdit.setDisabled(True)
            self.gui.Ccl_Text.setDisabled(True)

        elif lop == "prospect4":
            self.gui.Canth_Slide.setDisabled(True)
            self.gui.Canth_lineEdit.setDisabled(True)
            self.gui.Canth_Text.setDisabled(True)

            self.gui.Cbrown_Slide.setDisabled(True)
            self.gui.Cbrown_lineEdit.setDisabled(True)
            self.gui.Cbrown_Text.setDisabled(True)

            self.gui.Car_Slide.setDisabled(True)
            self.gui.Car_lineEdit.setDisabled(True)
            self.gui.Car_Text.setDisabled(True)

            self.gui.Cp_Slide.setDisabled(True)
            self.gui.Cp_lineEdit.setDisabled(True)
            self.gui.Cp_Text.setDisabled(True)

            self.gui.Ccl_Slide.setDisabled(True)
            self.gui.Ccl_lineEdit.setDisabled(True)
            self.gui.Ccl_Text.setDisabled(True)

        #self.mod_exec()

    def para_init(self):
        self.select_s2s(sensor="default", trigger=False)
        self.para_dict["N"] = float(self.gui.N_lineEdit.text()) #0
        self.para_dict["cab"] = float(self.gui.Cab_lineEdit.text()) #1
        self.para_dict["cw"] = float(self.gui.Cw_lineEdit.text()) #2
        self.para_dict["cm"] = float(self.gui.Cm_lineEdit.text()) #3
        self.para_dict["LAI"] = float(self.gui.LAI_lineEdit.text()) #4
        self.para_dict["typeLIDF"] = float(2)  # 5
        self.para_dict["LIDF"] = float(self.gui.LIDFB_lineEdit.text()) #6
        self.para_dict["hspot"] = float(self.gui.hspot_lineEdit.text()) #7
        self.para_dict["psoil"] = float(self.gui.psoil_lineEdit.text()) #8
        self.para_dict["tts"] = float(self.gui.SZA_lineEdit.text()) #9
        self.para_dict["tto"] = float(self.gui.OZA_lineEdit.text()) #10
        self.para_dict["psi"] = float(self.gui.rAA_lineEdit.text()) #11
        self.para_dict["cp"] = float(self.gui.Cp_lineEdit.text())  # 12
        self.para_dict["ccl"] = float(self.gui.Ccl_lineEdit.text())  # 13
        self.para_dict["car"] = float(self.gui.Car_lineEdit.text()) #14
        self.para_dict["anth"] = float(self.gui.Canth_lineEdit.text()) #15
        self.para_dict["cbrown"] = float(self.gui.Cbrown_lineEdit.text()) #16
        self.para_dict["LAIu"] = float(self.gui.LAIu_lineEdit.text()) #17
        self.para_dict["cd"] = float(self.gui.CD_lineEdit.text()) #18
        self.para_dict["sd"] = float(self.gui.SD_lineEdit.text()) #19
        self.para_dict["h"] = float(self.gui.TreeH_lineEdit.text()) #20

    def mod_interactive(self):
        self.gui.N_Slide.valueChanged.connect(lambda: self.mod_exec(slider=self.gui.N_Slide, item="N"))
        self.gui.Cab_Slide.valueChanged.connect(lambda: self.mod_exec(slider=self.gui.Cab_Slide, item="cab"))
        self.gui.Cw_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cw_Slide, item="cw"))
        self.gui.Cm_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cm_Slide, item="cm"))
        self.gui.LAI_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LAI_Slide, item="LAI"))
        self.gui.LIDFB_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LIDFB_Slide, item="LIDF"))
        self.gui.hspot_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.hspot_Slide, item="hspot"))
        self.gui.psoil_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.psoil_Slide, item="psoil"))
        self.gui.SZA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.SZA_Slide, item="tts"))
        self.gui.OZA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.OZA_Slide, item="tto"))
        self.gui.rAA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.rAA_Slide, item="psi"))
        self.gui.Cp_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cp_Slide, item="cp"))
        self.gui.Ccl_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Ccl_Slide, item="ccl"))
        self.gui.Car_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Car_Slide, item="car"))
        self.gui.Canth_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Canth_Slide, item="anth"))
        self.gui.Cbrown_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cbrown_Slide, item="cbrown"))
        self.gui.LAIu_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LAIu_Slide, item="LAIu"))
        self.gui.SD_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.SD_Slide, item="sd"))
        self.gui.TreeH_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.TreeH_Slide, item="h"))
        self.gui.CD_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.CD_Slide, item="cd"))

        self.gui.SType_None_B.clicked.connect(lambda: self.select_s2s(sensor="default"))
        self.gui.SType_Sentinel_B.clicked.connect(lambda: self.select_s2s(sensor="Sentinel2"))
        self.gui.SType_Landsat_B.clicked.connect(lambda: self.select_s2s(sensor="Landsat8"))
        self.gui.SType_Enmap_B.clicked.connect(lambda: self.select_s2s(sensor="EnMAP"))

        self.gui.B_DefSoilSpec.clicked.connect(lambda: self.select_background(bg_type="default"))
        self.gui.B_LoadBackSpec.clicked.connect(lambda: self.select_background(bg_type="load"))
        self.gui.B_LoadBackSpec.pressed.connect(lambda: self.select_background(bg_type="load"))


        self.gui.LIDF_combobox.currentIndexChanged.connect(self.select_LIDF)

        self.gui.CheckPlotAcc.stateChanged.connect(lambda: self.txtColorBars())
        self.gui.pushClearPlot.clicked.connect(lambda: self.clear_plot(rescale=True, clearPlots=True))  #clear the plot canvas
        self.gui.cmdResetScale.clicked.connect(lambda: self.clear_plot(rescale=True, clearPlots=False))
        self.gui.Push_LoadInSitu.clicked.connect(lambda: self.open_file(type="in situ"))  #load own spectrum
        self.gui.push_SelectFile.clicked.connect(lambda: self.open_file(type="background"))  # load own spectrum

        self.gui.Push_Exit.clicked.connect(self.gui.accept)  #exit app
        self.gui.Push_ResetInSitu.clicked.connect(self.reset_in_situ)  #remove own spectrum from plot canvas

        self.gui.Push_SaveSpec.clicked.connect(self.save_spectrum)
        self.gui.Push_SaveParams.clicked.connect(self.save_paralist)

        self.gui.lblFake.setVisible(False)  # placeholder for typeLIDF object in coloring

    def txtColorBars(self):
        if self.gui.CheckPlotAcc.isChecked():
            for i, lineEdit in enumerate(self.lineEdits):
                color_str = "rgb%s" % str(self.colors[i])
                lineEdit.setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                stop:0 rgb(255, 255, 255), stop:0.849 rgb(255, 255, 255),
                stop:0.85 %s, stop:1 %s);""" % (color_str, color_str))

        else:
            for lineEdit in self.lineEdits:
                lineEdit.setStyleSheet("background - color: rgb(255, 255, 255);")

    def mod_exec(self, slider=None, item=None):

        if slider is not None and item is not None:
            self.para_dict[item] = slider.value() / 10000.0  # update para_list

        mod_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=-999, int_boost=1.0, s2s=self.sensor)
        self.myResult = mod_I.initialize_single(tts=self.para_dict["tts"], tto=self.para_dict["tto"], psi=self.para_dict["psi"],
                                           N=self.para_dict["N"], cab=self.para_dict["cab"], cw=self.para_dict["cw"],
                                           cm=self.para_dict["cm"], LAI=self.para_dict["LAI"], LIDF=self.para_dict["LIDF"],
                                           typeLIDF=self.para_dict["typeLIDF"], hspot=self.para_dict["hspot"], psoil=self.para_dict["psoil"],
                                           cp=self.para_dict["cp"], ccl=self.para_dict["ccl"], car=self.para_dict["car"],
                                           cbrown=self.para_dict["cbrown"], anth=self.para_dict["anth"], soil=self.bg_spec,
                                                LAIu=self.para_dict["LAIu"], cd=self.para_dict["cd"], sd=self.para_dict["sd"],
                                                h=self.para_dict["h"])

        if item is not None:
            self.item = item

        self.plotting()

    def plotting(self):

        if not self.gui.CheckPlotAcc.isChecked():
            #self.clear_plot()
            self.gui.graphicsView.plot(self.wl, self.myResult, clear=True, pen="g", fillLevel=0, fillBrush=(255, 255, 255, 30),
                                        name='modelled')

            self.gui.graphicsView.setYRange(0, 0.8, padding=0)
            self.gui.graphicsView.setLabel('left', text="Reflectance [%]")
            self.gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")
        else:
            myPen = pg.mkPen(color=self.colors_dict[self.item], style=self.penStyle)
            self.plot = self.gui.graphicsView.plot(self.wl, self.myResult, pen=myPen)
            self.plot_own_spec()
            self.gui.graphicsView.setYRange(0, 0.8, padding=0)
            self.gui.graphicsView.setLabel('left', text="Reflectance [%]")
            self.gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")

        if self.data_mean is not None and not self.gui.CheckPlotAcc.isChecked():
            self.plot_own_spec()
            warnings.filterwarnings('ignore')

            try:
                mae = np.nansum(abs(self.myResult - self.data_mean)) / len(self.myResult)
                rmse = np.sqrt(np.nanmean((self.myResult - self.data_mean)**2))
                nse = 1.0 - ((np.nansum((self.data_mean - self.myResult)**2)) /
                             (np.nansum((self.data_mean - (np.nanmean(self.data_mean)))**2)))
                mnse = 1.0 - ((np.nansum(abs(self.data_mean - self.myResult))) /
                              (np.nansum(abs(self.data_mean - (np.nanmean(self.data_mean))))))
                r_squared = ((np.nansum((self.data_mean - np.nanmean(self.data_mean)) * (self.myResult - np.nanmean(self.myResult))))
                             / ((np.sqrt(np.nansum((self.data_mean - np.nanmean(self.data_mean))**2)))
                                * (np.sqrt(np.nansum((self.myResult - np.nanmean(self.myResult))**2)))))**2

                errors = pg.TextItem("RMSE: %.4f" % rmse +
                                     "\nMAE: %.4f" % mae +
                                     "\nNSE: %.4f" % nse +
                                     "\nmNSE: %.2f" % mnse +
                                     '\n' + u'R²: %.2f' % r_squared, (100, 200, 255),
                                     border="w", anchor=(1, 0))
            except:
                errors = pg.TextItem("RMSE: sensors mismatch" +
                                     "\nMAE: sensors mismatch " +
                                     "\nNSE: sensors mismatch" +
                                     "\nmNSE: sensors mismatch" +
                                     '\n' + u'R²: sensors mismatch ', (100, 200, 255),
                                     border="w", anchor=(1, 0))
            errors.setPos(2500, 0.55)
            self.gui.graphicsView.addItem(errors)

            warnings.filterwarnings('once')

    def open_file(self, type):
        self.main.loadtxtfile.open(type=type)

    def reset_in_situ(self):
        self.data_mean = None
        self.mod_exec()

    def plot_own_spec(self):
        if self.data_mean is not None:
            self.gui.graphicsView.plot(self.wl_open, self.data_mean, name='observed')

    def clear_plot(self, rescale=False, clearPlots=False):
        if rescale:
            self.gui.graphicsView.setYRange(0, 0.6, padding=0)
            self.gui.graphicsView.setXRange(350, 2550, padding=0)

        if clearPlots:
            self.gui.graphicsView.clear()
            self.plot_count = 0

    def save_spectrum(self):
        specnameout = QFileDialog.getSaveFileName(caption='Save Modelled Spectrum',
                                                      filter="Text files (*.txt)")
        if not specnameout: return
        save_matrix = np.zeros(shape=(len(self.wl),2))
        save_matrix[:, 0] = self.wl
        save_matrix[:, 1] = self.myResult

        np.savetxt(specnameout[0],save_matrix, delimiter="\t", header="Wavelength_nm\tReflectance")

    def save_paralist(self):
        paralistout = QFileDialog.getSaveFileName(caption='Save Modelled Spectrum Parameters',
                                                      filter="Text files (*.txt)")
        if paralistout:
            with open(paralistout[0], "w") as file:
                for para_key in self.para_dict:
                    if self.lineEdits_dict[para_key].isEnabled():
                        file.write("%s\t%f\n" % (para_key, self.para_dict[para_key]))
            file.close()


class LoadTxtFile:
    def __init__(self, main):
        self.main = main
        self.gui = Load_Txt_File_GUI()
        self.connections()
        self.initial_values()

    def connections(self):
        self.gui.cmdOK.clicked.connect(lambda: self.OK())
        self.gui.cmdCancel.clicked.connect(self.gui.close)
        self.gui.cmdInputFile.clicked.connect(lambda: self.open_file())
        self.gui.radioHeader.toggled.connect(lambda: self.change_radioHeader())
        self.gui.cmbDelimiter.activated.connect(lambda: self.change_cmbDelimiter()) # "activated" signal is user interaction only
        self.gui.spinDivisionFactor.valueChanged.connect(lambda: self.change_division())

    def initial_values(self):
        self.header_bool = None
        self.filenameIn = None
        self.delimiter_str = ["Tab", "Space", ",", ";"]
        self.gui.cmbDelimiter.clear()
        self.gui.cmbDelimiter.addItems(self.delimiter_str)
        self.gui.tablePreview.setRowCount(0)
        self.gui.tablePreview.setColumnCount(0)
        self.gui.radioHeader.setDisabled(True)
        self.gui.radioHeader.setChecked(False)
        self.gui.cmbDelimiter.setDisabled(True)
        self.gui.spinDivisionFactor.setDisabled(True)
        self.gui.spinDivisionFactor.setValue(1.0)
        self.gui.cmdOK.setDisabled(True)
        self.gui.label.setStyleSheet("color: rgb(170, 0, 0);")
        self.gui.label.setText("No File selected")
        self.gui.lblInputFile.setText("")
        self.divide_by = 1.0
        self.open_type = None
        self.wl_open, self.data_mean, self.nbands = (None, None, None)

    def open(self, type):
        self.initial_values()
        self.open_type = type
        self.gui.setWindowTitle("Open %s Spectrum" % type)
        self.gui.show()

    def open_file(self):
        # file_choice = str(QFileDialog.getOpenFileName(caption='Select Spectrum File', filter="Text-File (*.txt *.csv)"))
        file_choice, _filter = QFileDialog.getOpenFileName(None, 'Select Spectrum File', '.', "(*.txt *.csv)")
        if not file_choice: # Cancel clicked
            if not self.filenameIn: self.houston(message="No File selected") # no file in memory
            return
        self.filenameIn = file_choice
        self.gui.lblInputFile.setText(self.filenameIn)
        self.gui.radioHeader.setEnabled(True)
        self.gui.cmbDelimiter.setEnabled(True)
        self.gui.spinDivisionFactor.setEnabled(True)
        self.header_bool = False
        self.inspect_file()

    def inspect_file(self):
        sniffer = csv.Sniffer()
        with open(self.filenameIn, 'r') as raw_file:
            self.dialect = sniffer.sniff(raw_file.readline())
            if self.dialect.delimiter == "\t":
                self.gui.cmbDelimiter.setCurrentIndex(0)
            elif self.dialect.delimiter == " ":
                self.gui.cmbDelimiter.setCurrentIndex(1)
            elif self.dialect.delimiter == ",":
                self.gui.cmbDelimiter.setCurrentIndex(2)
            elif self.dialect.delimiter == ";":
                self.gui.cmbDelimiter.setCurrentIndex(3)
            raw_file.seek(0)
            raw = csv.reader(raw_file, self.dialect)
            try:
                _ = int(next(raw)[0])
                self.header_bool = False
            except:
                self.header_bool = True
            self.gui.radioHeader.setChecked(self.header_bool)
            self.read_file()

    def change_radioHeader(self):
        self.header_bool = self.gui.radioHeader.isChecked()
        self.read_file()

    def change_cmbDelimiter(self):
        index = self.gui.cmbDelimiter.currentIndex()
        if index == 0: self.dialect.delimiter = "\t"
        elif index == 1: self.dialect.delimiter = " "
        elif index == 2: self.dialect.delimiter = ","
        elif index == 3: self.dialect.delimiter = ";"
        self.read_file()

    def change_division(self):
        self.divide_by = self.gui.spinDivisionFactor.value()
        self.read_file()

    def read_file(self):
        if not self.filenameIn: return
        header_offset = 0
        with open(self.filenameIn, 'r') as raw_file:
            raw_file.seek(0)
            raw = csv.reader(raw_file, self.dialect)

            data = list()
            for content in raw:
                data.append(content)

        n_entries = len(data)
        if self.header_bool:
            header = data[0]
            if not len(header) == len(data[1]):
                self.houston(message="Error: Data has %i columns, but header has %i columns" % (len(data[1]), len(header)))
                return
            header_offset += 1
            n_entries -= 1
        n_cols = len(data[0+header_offset])
        try:
            self.wl_open = [int(float(data[i+header_offset][0])) for i in range(n_entries)]
        except ValueError:
            self.houston(message="Error: Cannot read file. Please check delimiter and header!")
            return

        row_labels = [str(self.wl_open[i]) for i in range(n_entries)]

        wl_offset = 400 - self.wl_open[0]

        data_array = np.zeros(shape=(n_entries,n_cols-1))
        for data_list in range(n_entries):
            data_array[data_list,:] = np.asarray(data[data_list+header_offset][1:]).astype(dtype=np.float16)

        self.data_mean = np.mean(data_array, axis=1)/self.divide_by

        # populate QTableWidget:
        self.gui.tablePreview.setRowCount(n_entries)
        self.gui.tablePreview.setColumnCount(1)
        if self.header_bool:
            self.gui.tablePreview.setHorizontalHeaderLabels(('Reflectances', 'bla'))
        self.gui.tablePreview.setVerticalHeaderLabels(row_labels)

        for row in range(n_entries):
            item = QTableWidgetItem(str(self.data_mean[row]))
            self.gui.tablePreview.setItem(row, 0, item)

        # Prepare for Statistics
        if wl_offset > 0:
            self.data_mean = self.data_mean[wl_offset:]  # cut off first 50 Bands to start at Band 400
            self.wl_open = self.wl_open[wl_offset:]

        self.gui.label.setStyleSheet("color: rgb(0, 170, 0);")
        self.gui.label.setText("Ok. No Errors")
        self.gui.cmdOK.setEnabled(True)

    def houston(self, message):  # we have a problem
        self.gui.label.setStyleSheet("color: rgb(170, 0, 0);")
        self.gui.label.setText(message)
        self.gui.tablePreview.setRowCount(0)
        self.gui.tablePreview.setColumnCount(0)
        self.gui.cmdOK.setDisabled(True)

    def OK(self):
        self.nbands = len(self.wl_open)
        self.main.ivvrm.wl_open = self.wl_open
        self.main.select_wavelengths.populate()
        self.main.select_wavelengths.gui.setModal(True)
        self.main.select_wavelengths.gui.show()
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

    def populate(self):
        if self.main.loadtxtfile.nbands < 10: width = 1
        elif self.main.loadtxtfile.nbands < 100: width = 2
        elif self.main.loadtxtfile.nbands < 1000: width = 3
        else: width = 4

        if self.main.loadtxtfile.open_type == "in situ":
            self.default_exclude = [i for j in (range(960, 1021), range(1390, 1551), range(2000, 2101)) for i in j]
        elif self.main.loadtxtfile.open_type == "background":
            self.default_exclude = [i for j in (range(960, 1021), range(1390, 1551), range(2000, 2101)) for i in j]

        for i in range(self.main.loadtxtfile.nbands):
            if i in self.default_exclude:
                str_band_no = '{num:0{width}}'.format(num=i + 1, width=width)
                label = "band %s: %6.2f %s" % (str_band_no, self.main.loadtxtfile.wl_open[i], u'nm') # Ersetze durch variable Unit!
                self.gui.lstExcluded.addItem(label)
            else:
                str_band_no = '{num:0{width}}'.format(num=i+1, width=width)
                label = "band %s: %6.2f %s" %(str_band_no, self.main.loadtxtfile.wl_open[i], u'nm')
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

        for i in range(list_object.count()):
            item = list_object.item(i)
            list_object.setItemSelected(item, True)

        self.send(direction=direction)

    def OK(self):
        list_object = self.gui.lstExcluded
        raw_list = []
        for i in range(list_object.count()):
            item = list_object.item(i).text()
            raw_list.append(item)

        exclude_bands = [int(raw_list[i].split(" ")[1][:-1]) - 1 for i in range(len(raw_list))]

        if self.main.loadtxtfile.open_type == "in situ":
            self.main.ivvrm.data_mean = np.asarray([self.main.loadtxtfile.data_mean[i] if i not in exclude_bands
                                                   else np.nan for i in range(len(self.main.loadtxtfile.data_mean))])

        elif self.main.loadtxtfile.open_type == "background":
            water_absorption_ranges = self.generate_ranges(range_list=exclude_bands)

            for interp_bands in water_absorption_ranges:
                y = [self.main.loadtxtfile.data_mean[interp_bands[0]], self.main.loadtxtfile.data_mean[interp_bands[-1]]]
                f = interp1d([interp_bands[0], interp_bands[-1]], [y[0], y[1]])
                self.main.loadtxtfile.data_mean[interp_bands[1:-1]] = f(interp_bands[1:-1])

            self.main.ivvrm.bg_spec = self.main.loadtxtfile.data_mean
            self.main.ivvrm.gui.BackSpec_label.setText(os.path.basename(self.main.loadtxtfile.filenameIn))
            self.main.ivvrm.gui.push_SelectFile.setEnabled(False)
            self.main.ivvrm.gui.push_SelectFile.setText('File:')

        for list_object in [self.gui.lstIncluded, self.gui.lstExcluded]:
            list_object.clear()

        self.main.ivvrm.mod_exec()
        self.gui.close()

    def generate_ranges(self, range_list):
        water_absorption_ranges = list()
        last = -2
        start = -1

        for item in range_list:
            if item != last + 1:
                if start != -1:
                    water_absorption_ranges.append(range(start, last + 1))
                start = item
            last = item
        water_absorption_ranges.append(range(start, last + 1))
        return water_absorption_ranges

class MainUiFunc:
    def __init__(self):
        self.QGis_app = QApplication.instance()  # the QGIS-Application made accessible within the code

        self.ivvrm = IVVRM(self)

        self.loadtxtfile = LoadTxtFile(self)
        self.select_wavelengths = Select_Wavelengths(self)

    def show(self):
        self.ivvrm.gui.show()


if __name__ == '__main__':

    from enmapbox.testing import initQgisApplication
    #from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisApplication()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())



