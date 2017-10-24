# -*- coding: utf-8 -*-

import sys, os
import numpy as np
from scipy.interpolate import interp1d


from qgis.gui import *
#ensure to call QGIS before PyQtGraph
import pyqtgraph as pg
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import call_model as mod
from enmapbox.gui.applications import EnMAPBoxApplication
from Spec2Sensor_cl import Spec2Sensor
import warnings


pathUI = os.path.join(os.path.dirname(__file__), 'GUI_IVVM.ui')
from enmapbox.gui.utils import loadUIFormClass

class IVVM_GUI(QDialog, loadUIFormClass(pathUI)):
    
    def __init__(self, parent=None):
        super(IVVM_GUI, self).__init__(parent)
        self.setupUi(self)    

class IVVM:

    def __init__(self, main):
        self.main = main
        self.gui = IVVM_GUI()
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
        self.typeLIDF = 2
        self.lop = "prospectD"
        self.canopy_arch = "sail"
        self.colors = [tuple([219,183,255]), tuple([51,204,51]), tuple([69,30,234]), tuple([0,255,255]),
                        tuple([255,255,0]), tuple([0,0,0]), tuple([255,0,0]), tuple([255,255,255]),
                        tuple([255,124,128]), tuple([178,178,178]), tuple([144, 204, 154]),
                        tuple([255,153,255]), tuple([25,41,70]), tuple([169,139,100]),
                       tuple([255,153,51]), tuple([204, 0, 153]), tuple([172, 86, 38])]
        self.lineEdits = [self.gui.N_lineEdit, self.gui.Cab_lineEdit, self.gui.Cw_lineEdit, self.gui.Cm_lineEdit,
                          self.gui.LAI_lineEdit, self.gui.lblFake, self.gui.LIDFB_lineEdit, self.gui.hspot_lineEdit,
                          self.gui.psoil_lineEdit, self.gui.SZA_lineEdit, self.gui.OZA_lineEdit, self.gui.rAA_lineEdit,
                          self.gui.Cp_lineEdit, self.gui.Ccl_lineEdit, self.gui.Car_lineEdit, self.gui.Canth_lineEdit,
                          self.gui.Cbrown_lineEdit]
        self.penStyle = 1
        self.item = 1
        # self.plot_color = dict(zip(range(7), ["g", "r", "b", "y", "m", "c", "w"]))
        self.plot_count = 0
        self.current_slider = None
        self.data_mean = None
        self.para_list = []
        self.bg_spec = None
        self.bg_type = "default"

    # def color_constructor(self, color):
    #     if color == "g":
    #         rgb_string = "rgb(%i, %i, %i)" % (0, 255, 0)
    #     elif color == "r":
    #         rgb_string = "rgb(%i, %i, %i)" % (255, 0, 0)
    #     elif color == "b":
    #         rgb_string = "rgb(%i, %i, %i)" % (0, 0, 255)
    #     elif color == "y":
    #         rgb_string = "rgb(%i, %i, %i)" % (255, 255, 0)
    #     elif color == "m":
    #         rgb_string = "rgb(%i, %i, %i)" % (255, 0, 255)
    #     elif color == "c":
    #         rgb_string = "rgb(%i, %i, %i)" % (0, 255, 255)
    #     elif color == "w":
    #         rgb_string = "rgb(%i, %i, %i)" % (255, 255, 255)
    #     return rgb_string

    # def style_constructor(self, colors):
    #
    #     # assume colors=["y", "r"]
    #     n = len(colors)
    #     color_str = [] # list for all the RGB-values
    #     for color in colors:
    #         color_str.append(self.color_constructor(color=color))
    #     color_str = [x for pair in zip(color_str, color_str) for x in pair] # duplicate all colors (start & stop)
    #
    #     style_str = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 " # "Intro"
    #
    #     style_str += ", stop:1 %s);" % self.color_constructor(color="w") # "Outro"
    #
    #     print style_str

    # def flag_colors(self):
        # self.style_constructor(colors=["y", "r"])
        # self.gui.color_N.setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
        # stop:0 """ + self.color_constructor("y") + """, stop:0.499 rgb(255, 255, 0),
        # stop:0.501 rgb(255, 0, 0), stop:1 rgb(255, 0, 0));""")
        # self.gui.color_Cab.setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
        # stop:0 rgb(255, 0, 0), stop:1 rgb(255, 0, 0));""")
        # self.gui.color_Cw.setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
        # stop:0 rgb(255, 0, 0), stop:0.330 rgb(255, 0, 0),
        # stop:0.335 rgb(0, 255, 0), stop:0.665 rgb(0, 255, 0),
        # stop:0.670 rgb(0,0,255), stop:1 rgb(0, 0, 255));""")

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
        self.gui.skyl_Slide.valueChanged.connect(lambda: self.any_slider_change(self.gui.skyl_Slide, self.gui.skyl_lineEdit))
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
        self.gui.skyl_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(self.gui.skyl_lineEdit, self.gui.skyl_Slide))
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
            self.gui.BackSpec_lineEdit.setEnabled(False)
        elif bg_type == "load":
            self.gui.B_DefSoilSpec.setEnabled(True)
            self.gui.B_LoadBackSpec.setEnabled(True)
            self.gui.BrightFac_Text.setEnabled(False)
            self.gui.psoil_Slide.setEnabled(False)
            self.gui.psoil_lineEdit.setEnabled(False)
            self.gui.push_SelectFile.setEnabled(True)
            self.gui.BackSpec_lineEdit.setEnabled(True)

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
            self.typeLIDF = 1 # Beta Distribution
            self.para_list[6] = index - 1
            self.gui.LIDFB_Slide.setDisabled(True)
            self.gui.LIDFB_lineEdit.setDisabled(True)
            self.mod_exec(item=6)
        else:
            self.typeLIDF = 2 # Ellipsoidal Distribution
            self.mod_exec(self.gui.LIDFB_Slide, item=6)
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
        self.gui.B_Inform.clicked.connect(lambda: self.select_model(canopy_arch="inform"))

    def select_model(self, lop="prospectD", canopy_arch="sail"):
        self.lop = lop

        if canopy_arch is None:
            self.canopy_arch = None
            self.gui.CanopyMP_Box.setDisabled(True)
            self.gui.BrightFac_Text.setEnabled(False)
            self.gui.psoil_Slide.setEnabled(False)
            self.gui.psoil_lineEdit.setEnabled(False)
            self.gui.push_SelectFile.setEnabled(False)
            self.gui.BackSpec_lineEdit.setEnabled(False)
            self.gui.B_DefSoilSpec.setEnabled(False)
            self.gui.B_LoadBackSpec.setEnabled(False)
        else:
            self.canopy_arch = canopy_arch
            self.gui.CanopyMP_Box.setDisabled(False)
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

        self.mod_exec()

    def para_init(self):
        self.select_s2s(sensor="default", trigger=False)
        self.para_list.append(float(self.gui.N_lineEdit.text())) #0
        self.para_list.append(float(self.gui.Cab_lineEdit.text())) #1
        self.para_list.append(float(self.gui.Cw_lineEdit.text())) #2
        self.para_list.append(float(self.gui.Cm_lineEdit.text())) #3
        self.para_list.append(float(self.gui.LAI_lineEdit.text())) #4
        self.para_list.append(float(2))  # 5
        self.para_list.append(float(self.gui.LIDFB_lineEdit.text())) #6
        self.para_list.append(float(self.gui.hspot_lineEdit.text())) #7
        self.para_list.append(float(self.gui.psoil_lineEdit.text())) #8
        self.para_list.append(float(self.gui.SZA_lineEdit.text())) #9
        self.para_list.append(float(self.gui.OZA_lineEdit.text())) #10
        self.para_list.append(float(self.gui.rAA_lineEdit.text())) #11
        self.para_list.append(float(self.gui.Cp_lineEdit.text()))  # 12
        self.para_list.append(float(self.gui.Ccl_lineEdit.text()))  # 13
        self.para_list.append(float(self.gui.Car_lineEdit.text())) #14
        self.para_list.append(float(self.gui.Canth_lineEdit.text())) #15
        self.para_list.append(float(self.gui.Cbrown_lineEdit.text())) #16
        self.para_list.append(float(self.gui.skyl_lineEdit.text())) #17
        self.typeLIDF = 2

    def mod_interactive(self):
        self.gui.N_Slide.valueChanged.connect(lambda: self.mod_exec(slider=self.gui.N_Slide, item=0))
        self.gui.Cab_Slide.valueChanged.connect(lambda: self.mod_exec(slider=self.gui.Cab_Slide, item=1))
        self.gui.Cw_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cw_Slide, item=2))
        self.gui.Cm_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cm_Slide, item=3))
        self.gui.LAI_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LAI_Slide, item=4))
        self.gui.LIDFB_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LIDFB_Slide, item=6))
        self.gui.hspot_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.hspot_Slide, item=7))
        self.gui.psoil_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.psoil_Slide, item=8))
        self.gui.SZA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.SZA_Slide, item=9))
        self.gui.OZA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.OZA_Slide, item=10))
        self.gui.rAA_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.rAA_Slide, item=11))
        self.gui.Cp_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cp_Slide, item=12))
        self.gui.Ccl_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Ccl_Slide, item=13))
        self.gui.Car_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Car_Slide, item=14))
        self.gui.Canth_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Canth_Slide, item=15))
        self.gui.Cbrown_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.Cbrown_Slide, item=16))
        self.gui.skyl_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.skyl_Slide, item=17))
        self.gui.LAIu_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.LAIu_Slide, item=18))
        self.gui.SD_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.SD_Slide, item=19))
        self.gui.TreeH_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.TreeH_Slide, item=20))
        self.gui.CD_Slide.valueChanged.connect(lambda: self.mod_exec(self.gui.CD_Slide, item=21))

        self.gui.SType_None_B.clicked.connect(lambda: self.select_s2s(sensor="default"))
        self.gui.SType_Sentinel_B.clicked.connect(lambda: self.select_s2s(sensor="Sentinel2"))
        self.gui.SType_Landsat_B.clicked.connect(lambda: self.select_s2s(sensor="Landsat8"))
        self.gui.SType_Enmap_B.clicked.connect(lambda: self.select_s2s(sensor="EnMAP"))

        self.gui.B_DefSoilSpec.clicked.connect(lambda: self.select_background(bg_type="default"))
        self.gui.B_LoadBackSpec.clicked.connect(lambda: self.select_background(bg_type="load"))
        self.gui.push_SelectFile.clicked.connect(self.open_soil)

        self.gui.LIDF_combobox.currentIndexChanged.connect(self.select_LIDF)

        self.gui.CheckPlotAcc.stateChanged.connect(lambda: self.txtColorBars())
        self.gui.pushClearPlot.clicked.connect(lambda: self.clear_plot(rescale=True, clearPlots=True))  #clear the plot canvas
        self.gui.cmdResetScale.clicked.connect(lambda: self.clear_plot(rescale=True, clearPlots=False))
        self.gui.Push_LoadInSitu.clicked.connect(self.open_file)  #load own spectrum
        self.gui.Push_Exit.clicked.connect(self.gui.accept)  #exit app
        self.gui.Push_ResetInSitu.clicked.connect(self.reset_in_situ)  #remove own spectrum from plot canvas

        self.gui.Push_SaveSpec.clicked.connect(self.save_spectrum)
        self.gui.Push_SaveParams.clicked.connect(self.save_paralist)

        self.gui.lblFake.setVisible(False) # placeholder for typeLIDF object in coloring

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
            self.para_list[item] = slider.value() / 10000.0  # update para_list

        mod_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=-999, int_boost=1.0, s2s=self.sensor)
        self.myResult = mod_I.initialize_single(tts=self.para_list[9], tto=self.para_list[10], psi=self.para_list[11],
                                           N=self.para_list[0], cab=self.para_list[1], cw=self.para_list[2],
                                           cm=self.para_list[3], LAI=self.para_list[4], LIDF=self.para_list[6],
                                           typeLIDF=self.typeLIDF, hspot=self.para_list[7], psoil=self.para_list[8],
                                            cp=self.para_list[12], ccl=self.para_list[13], car=self.para_list[14],
                                           cbrown=self.para_list[16], anth=self.para_list[15], soil=self.bg_spec)

        # self.myResult[960:1021] = np.nan  # set atmospheric water vapour absorption bands to NaN
        # self.myResult[1390:1541] = np.nan
        if not item is None: self.item = item
        self.plotting()

    def plotting(self):

        if not self.gui.CheckPlotAcc.isChecked():
            self.clear_plot()
            self.gui.graphicsView.plot(self.wl, self.myResult, pen="g", fillLevel=0, fillBrush=(255, 255, 255, 30),
                                        name='modelled')

            self.gui.graphicsView.setYRange(0, 0.6, padding=0)
            self.gui.graphicsView.setLabel('left', text="Reflectance [%]")
            self.gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")
        else:
            myPen = pg.mkPen(color=self.colors[self.item], style=self.penStyle)
            self.plot = self.gui.graphicsView.plot(self.wl, self.myResult, pen=myPen)
            self.plot_own_spec()
            self.gui.graphicsView.setYRange(0, 0.6, padding=0)
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

                errors = pg.TextItem("RMSE: " + str(round(rmse, 6)) +
                                     "\nMAE: " + str(round(mae, 6)) +
                                     "\nNSE: " + str(round(nse, 6)) +
                                     "\nmNSE: " + str(round(mnse, 6)) +
                                     '\n' + u'R²: ' + str(round(r_squared, 6)), (100, 200, 255),
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

    def open_file(self):
        # Dialog to open own spectrum, .asc exported by ViewSpecPro as single file
        filenameIn = str(QFileDialog.getOpenFileName(caption='Select Spectrum File'))
        if not filenameIn: return
        self.data = np.genfromtxt(filenameIn, delimiter="\t", skip_header=True)
        ## "\OSGEO4~1\apps\Python27\lib\site-packages\numpy\lib\npyio.py" changed endswith to endsWith to work:
        self.wl_open = self.data[:,0]
        self.offset = 400 - int(self.wl_open[0])
        self.data_mean = np.delete(self.data, 0, axis=1)
        self.data_mean = np.mean(self.data_mean, axis=1)
        if self.offset > 0:
            self.data_mean = self.data_mean[self.offset:]  # cut off first 50 Bands to start at Band 400
            self.wl_open = self.wl_open[self.offset:]

        water_absorption_bands = range(1360, 1421) + range(1790, 1941) + range(2400, 2501)
        self.data_mean = np.asarray([self.data_mean[i] if self.wl_open[i] not in water_absorption_bands
                                     else np.nan for i in xrange(len(self.data_mean))])


        # try:
        #     self.data_mean[960:1021] = np.nan  # set atmospheric water vapour absorption bands to NaN
        #     self.data_mean[1390:1541] = np.nan
        #     self.data_mean[2000:2101] = np.nan
        # except:
        #     QMessageBox.critical(self.gui, "error", "Cannot display selected spectrum")
        #     return
        self.mod_exec()

    def open_soil(self):
        # Dialog to open background as .csv or textfile
        filenameIn = str(QFileDialog.getOpenFileName(caption='Select Soil Spectrum'))
        if not filenameIn: return
        data = np.genfromtxt(filenameIn, delimiter="\t", skip_header=True)
        ## "\OSGEO4~1\apps\Python27\lib\site-packages\numpy\lib\npyio.py" changed endswith to endsWith to work:
        wl_open = data[:, 0]
        data_open = data[:, 1]
        offset = 400 - int(wl_open[0])

        if offset > 0:
            data_open = data_open[offset:]  # cut off first 50 Bands to start at Band 400
            wl_open = wl_open[offset:]

        # linear interpolation water absorption

        # water_absorption_bands = [range(1360, 1421), range(1790, 1941), range(2400, 2501)]
        water_absorption_bands = [range(959, 1022), range(1390, 1541)]

        for interp_bands in water_absorption_bands:
            y = [data_open[interp_bands[0]], data_open[interp_bands[-1]]]
            f = interp1d([interp_bands[0], interp_bands[-1]], [y[0], y[1]])
            data_open[interp_bands[1:-1]] = f(interp_bands[1:-1])

        self.bg_spec = data_open

        self.mod_exec()

    def reset_in_situ(self):
        self.data_mean = None
        self.mod_exec()

    def plot_own_spec(self):
        if self.data_mean is not None:
            self.gui.graphicsView.plot(self.wl_open, self.data_mean, name='observed')

    def clear_plot(self, rescale=False, clearPlots=True):
        if rescale:
            self.gui.graphicsView.setYRange(0, 0.6, padding=0)
            self.gui.graphicsView.setXRange(350, 2550, padding=0)

        if clearPlots:
            self.gui.graphicsView.clear()
            self.plot_count = 0

    def save_spectrum(self):
        specnameout = str(QFileDialog.getSaveFileName(caption='Save Modelled Spectrum',
                                                      filter="Text files (*.txt)"))
        if not specnameout: return
        save_matrix = np.zeros(shape=(len(self.wl),2))
        save_matrix[:,0] = self.wl
        save_matrix[:,1] = self.myResult
        np.savetxt(specnameout, save_matrix, delimiter="\t", header="wavelength (nm)")

    def save_paralist(self):
        paralistout = str(QFileDialog.getSaveFileName(caption='Save Modelled Spectrum',
                                                      filter="Text files (*.txt)"))
        if paralistout:
            with open(paralistout, "w") as file:
                file.write("N, Cab, Cw, Cm, LAI, LIDF, ALIA, hspot, psoil, SZA, OZA, rAA, Cp, Ccl, Car, Canth, Cbrown, skyl\n")
                file.write(','.join(str(line) for line in self.para_list))

class MainUiFunc:
    def __init__(self):
        self.isd = IVVM(self)
    def show(self):
        self.isd.gui.show()

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())


