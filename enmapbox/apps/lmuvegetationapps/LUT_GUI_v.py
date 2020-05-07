# -*- coding: utf-8 -*-

import sys, os
import numpy as np
from scipy.interpolate import interp1d

from qgis.gui import *
#ensure to call QGIS before PyQtGraph
from enmapbox.externals.qps.externals import pyqtgraph as pg
#import pyqtgraph as pg
#from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt import uic
import lmuvegetationapps.call_model_v as mod
from enmapbox.gui.applications import EnMAPBoxApplication
from lmuvegetationapps.Spec2Sensor_cl_v import Spec2Sensor
from scipy.stats import norm, uniform
import csv
import time

from enmapbox.gui.utils import loadUi

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_LUT.ui')
pathUI2 = os.path.join(os.path.dirname(__file__), 'GUI_ProgressBar.ui')
pathUI3 = os.path.join(os.path.dirname(__file__), 'GUI_LoadTxtFile.ui')
pathUI4 = os.path.join(os.path.dirname(__file__), 'GUI_Select_Wavelengths.ui')


class LUT_GUI(QDialog):
    def __init__(self, parent=None):
        super(LUT_GUI, self).__init__(parent)
        loadUi(pathUI, self)


class Load_Txt_File_GUI(QDialog):
    def __init__(self, parent=None):
        super(Load_Txt_File_GUI, self).__init__(parent)
        loadUi(pathUI3, self)


class Select_Wavelengths_GUI(QDialog):
    def __init__(self, parent=None):
        super(Select_Wavelengths_GUI, self).__init__(parent)
        loadUi(pathUI4, self)


class PRG_GUI(QDialog):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        loadUi(pathUI2, self)
        self.allow_cancel = False

    def closeEvent(self, event):
        if self.allow_cancel:
            event.accept()
        else:
            event.ignore()

# Class for event filter "Focus lost"
class Filter(QtCore.QObject):
    def __init__(self, gui=None, lut=None):
        super(Filter, self).__init__()
        self.gui = gui
        self.lut = lut

    def bypass(self, widget, event):
        self.eventFilter(widget=widget, event=event)

    def eventFilter(self, widget, event):
        # FocusOut event

        for para in self.lut.dict_objects:  # browse through all parameters
            if widget in self.lut.dict_objects[para]:
                break  # if widget (that called the event) is found in the para objects, then cancel the search and keep para

        if event.type() == QtCore.QEvent.FocusOut:
            if self.lut.dict_objects[para][0].isChecked():  # fix
                try:
                    vals = [float(self.lut.dict_objects[para][4].text())]  # needs to be of type "list" (even single values)
                    ns = self.gui.spinNS.value()
                    #self.lut.dict_objects[para][12].clear()
                    bar = pg.BarGraphItem(x=vals, height=ns, width=0.01)
                    self.lut.dict_objects[para][12].addItem(bar)
                    self.lut.dict_objects[para][12].plot(clear=True)
                    # if vals < 1.0:
                    #     self.lut.dict_objects[para][12].setrange(vals - width * 2, xVals[-1] + width * 2)
                except ValueError as e:
                    print(str(e))

            elif self.lut.dict_objects[para][1].isChecked():  # gauss
                try:
                    vals = [float(self.lut.dict_objects[para][i].text()) for i in [5,6,7,8]]
                    xIncr = (vals[1] - vals[0]) / 100.0
                    xVals = np.arange(vals[0], vals[1], xIncr)
                    #self.lut.dict_objects[para][12].clear()
                    self.lut.dict_objects[para][12].plot(xVals, norm.pdf(xVals, loc=vals[2], scale=vals[3]),
                                                         clear=True)
                except:
                    pass
            elif self.lut.dict_objects[para][2].isChecked():  # uniform
                try:
                    vals = [float(self.lut.dict_objects[para][i].text()) for i in [5, 6]]
                    xIncr = (vals[1] - vals[0]) / 100.0
                    xVals = np.arange(vals[0], vals[1], xIncr)
                    #self.lut.dict_objects[para][12].clear()
                    self.lut.dict_objects[para][12].plot(xVals, uniform.pdf(xVals, loc=vals[0], scale=vals[1]),
                                                         clear=True)
                except:
                    pass
            elif self.lut.dict_objects[para][3].isChecked():  # logical
                try:
                    vals = [float(self.lut.dict_objects[para][i].text()) for i in [9, 10, 11]]
                    xVals = np.linspace(start=vals[0], stop=vals[1], num=int(vals[2]))
                    ns = self.gui.spinNS.value()
                    width = (xVals[1]-xVals[0])/8
                    # self.lut.dict_objects[para][12].enableAutoRange(enable=False)
                    #self.lut.dict_objects[para][12].clear()
                    bar = pg.BarGraphItem(x=xVals, height=ns, width=width)
                    self.lut.dict_objects[para][12].addItem(bar)
                    self.lut.dict_objects[para][12].plot(clear=True)
                    if vals[1] < 1.0:
                        self.lut.dict_objects[para][12].setrange(xVals[0]-width*2, xVals[-1]+width*2)
                    # existingViewRect = self.lut.dict_objects[para][12].getViewBox().viewRange()
                    # print existingViewRect
                except:
                    pass


            # if len(self.dict_vals[self.para_list[0][i]]) > 3:
            #     if self.dict_vals[self.para_list[0][i]][2] > self.dict_vals[self.para_list[0][i]][1] or \
            #                     self.dict_vals[self.para_list[0][i]][2] < self.dict_vals[self.para_list[0][i]][0]:
            #         self.abort(message='Parameter %s: mean value must lie between min and max' % self.para_list[0][i])
            #         return False
            #     elif self.dict_vals[self.para_list[0][i]][0] < self.dict_boundaries[key][0] or \
            #                     self.dict_vals[self.para_list[0][i]][1] > self.dict_boundaries[key][1]:
            #         self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[0][i])
            #         return False
            # elif len(self.dict_vals[self.para_list[0][i]]) > 1:  # min and max specified
            #     if self.dict_vals[self.para_list[0][i]][0] < self.dict_boundaries[key][0] or \
            #                     self.dict_vals[self.para_list[0][i]][1] > self.dict_boundaries[key][1]:
            #         self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[0][i])
            #         return False
            # elif len(self.dict_vals[self.para_list[0][i]]) > 0:  # fixed value specified
            #     if self.dict_vals[self.para_list[0][i]][0] < self.dict_boundaries[key][0] or \
            #                     self.dict_vals[self.para_list[0][i]][0] > self.dict_boundaries[key][1]:
            #         self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[0][i])
            #         return False

            # return False so that the widget will also handle the event
            # otherwise it won't focus out
            return False
        else:
            # we don't care about other events
            return False

class LUT:

    def __init__(self, main):
        self.main = main
        self.gui = LUT_GUI()
        self._filter = Filter(gui=self.gui, lut=self)
        self.special_chars()
        self.initial_values()
        self.dictchecks()
        self.connections()
        for para in self.dict_objects:
            self.dict_objects[para][0].setChecked(True)
            self.txt_enables(para=para, mode="fix")
            for object in range(12):
                self.dict_objects["cp"][object].setDisabled(True)
                self.dict_objects["cbc"][object].setDisabled(True)
        self.set_boundaries()

    def special_chars(self):
        self.gui.lblCab.setText('Chlorophyll A + B (Cab) [µg/cm²] \n[0.0 - 100.0]')
        self.gui.lblCm.setText('Dry Matter Content (Cm) [g/cm²] \n[0.0001 - 0.02]')
        self.gui.lblCar.setText('Carotenoids (Ccx) [µg/cm²] \n[0.0 - 30.0]')
        self.gui.lblCanth.setText('Anthocyanins (Canth) [µg/cm²] \n[0.0 - 10.0]')
        self.gui.lblLAI.setText('Leaf Area Index (LAI) [m²/m²] \n[0.01 - 10.0]')
        self.gui.lblLAIu.setText('Undergrowth Leaf Area Index \n(LAI) [m²/m²] \n[0.01 - 10.0]')
        self.gui.lblCp.setText('Proteins (Cp) [g/cm²] \n[0.0 - 0.01]')
        self.gui.lblCbc.setText('Carbon-based constit. (CBC) [g/cm²] \n[0.0 - 0.01]')

    def initial_values(self):
        self.typeLIDF = 2
        self.lop = "prospectD"
        self.canopy_arch = "sail"
        self.para_list = [['N', 'chl', 'cw', 'cm', 'car', 'cbr', 'canth', 'cp', 'cbc'],
                          ['lai', 'alia', 'hspot', 'oza', 'sza', 'raa', 'psoil'],
                          ['laiu', 'sd', 'h', 'cd']]
        self.para_flat = [item for sublist in self.para_list for item in sublist]
        self.npara_flat = len(self.para_flat)

        self.N, self.chl, self.cw, self.cm, self.car, self.cbr, self.canth, self.cp, self.cbc, \
        self.lai, self.alia, self.hspot, self.oza, self.sza, self.raa, self.psoil, self.laiu, self.sd, self.h, self.cd \
            = ([] for i in range(self.npara_flat))

        self.depends = 0  # ...

        # self.all_inputs = [self.N, self.chl, self.cw, self.cm, self.car, self.cbr, self.canth, self.lai, self.alia,
        #                   self.hspot, self.oza, self.sza, self.raa, self.psoil, self.laiu, self.sd, self.h, self.cd]

        self.path = None
        self.LUT_name = None
        self.sensor = "default"


        self.ns = None
        self.nlut_total = None
        self.est_time = None
        self.nodat = None
        self.intboost = None
        self.speed = None
        self.bg_spec = None
        self.bg_type = "default"

    def dictchecks(self):

        self.dict_checks = {"car": None, "cbr": None, "canth": None, "cp": None, "cbc": None}

        self.dict_objects = {"N": [self.gui.radio_fix_N, self.gui.radio_gauss_N, self.gui.radio_uni_N,
                                 self.gui.radio_log_N, self.gui.txt_fix_N, self.gui.txt_gauss_min_N,
                                 self.gui.txt_gauss_max_N, self.gui.txt_gauss_mean_N, self.gui.txt_gauss_std_N,
                                 self.gui.txt_log_min_N, self.gui.txt_log_max_N, self.gui.txt_log_steps_N,
                                 self.gui.viewN],
                            "chl": [self.gui.radio_fix_chl, self.gui.radio_gauss_chl, self.gui.radio_uni_chl,
                                 self.gui.radio_log_chl, self.gui.txt_fix_chl, self.gui.txt_gauss_min_chl,
                                 self.gui.txt_gauss_max_chl, self.gui.txt_gauss_mean_chl, self.gui.txt_gauss_std_chl,
                                 self.gui.txt_log_min_chl, self.gui.txt_log_max_chl, self.gui.txt_log_steps_chl,
                                 self.gui.viewChl],
                            "cw": [self.gui.radio_fix_cw, self.gui.radio_gauss_cw, self.gui.radio_uni_cw,
                                 self.gui.radio_log_cw, self.gui.txt_fix_cw, self.gui.txt_gauss_min_cw,
                                 self.gui.txt_gauss_max_cw, self.gui.txt_gauss_mean_cw, self.gui.txt_gauss_std_cw,
                                 self.gui.txt_log_min_cw, self.gui.txt_log_max_cw, self.gui.txt_log_steps_cw,
                                 self.gui.viewCw],
                            "cm": [self.gui.radio_fix_cm, self.gui.radio_gauss_cm, self.gui.radio_uni_cm,
                                 self.gui.radio_log_cm, self.gui.txt_fix_cm, self.gui.txt_gauss_min_cm,
                                 self.gui.txt_gauss_max_cm, self.gui.txt_gauss_mean_cm, self.gui.txt_gauss_std_cm,
                                 self.gui.txt_log_min_cm, self.gui.txt_log_max_cm, self.gui.txt_log_steps_cm,
                                 self.gui.viewCm],
                            "car": [self.gui.radio_fix_car, self.gui.radio_gauss_car, self.gui.radio_uni_car,
                                 self.gui.radio_log_car, self.gui.txt_fix_car, self.gui.txt_gauss_min_car,
                                 self.gui.txt_gauss_max_car, self.gui.txt_gauss_mean_car, self.gui.txt_gauss_std_car,
                                 self.gui.txt_log_min_car, self.gui.txt_log_max_car, self.gui.txt_log_steps_car,
                                 self.gui.viewCar],
                            "cbr": [self.gui.radio_fix_cbr, self.gui.radio_gauss_cbr, self.gui.radio_uni_cbr,
                                 self.gui.radio_log_cbr, self.gui.txt_fix_cbr, self.gui.txt_gauss_min_cbr,
                                 self.gui.txt_gauss_max_cbr, self.gui.txt_gauss_mean_cbr, self.gui.txt_gauss_std_cbr,
                                 self.gui.txt_log_min_cbr, self.gui.txt_log_max_cbr, self.gui.txt_log_steps_cbr,
                                 self.gui.viewCbr],
                            "canth": [self.gui.radio_fix_canth, self.gui.radio_gauss_canth, self.gui.radio_uni_canth,
                                       self.gui.radio_log_canth, self.gui.txt_fix_canth, self.gui.txt_gauss_min_canth,
                                       self.gui.txt_gauss_max_canth, self.gui.txt_gauss_mean_canth, self.gui.txt_gauss_std_canth,
                                       self.gui.txt_log_min_canth, self.gui.txt_log_max_canth, self.gui.txt_log_steps_canth,
                                       self.gui.viewCanth],
                            "cp": [self.gui.radio_fix_cp, self.gui.radio_gauss_cp, self.gui.radio_uni_cp,
                                       self.gui.radio_log_cp, self.gui.txt_fix_cp, self.gui.txt_gauss_min_cp,
                                       self.gui.txt_gauss_max_cp, self.gui.txt_gauss_mean_cp,
                                       self.gui.txt_gauss_std_cp,
                                       self.gui.txt_log_min_cp, self.gui.txt_log_max_cp,
                                       self.gui.txt_log_steps_cp,
                                       self.gui.viewCp],
                            "cbc": [self.gui.radio_fix_cbc, self.gui.radio_gauss_cbc, self.gui.radio_uni_cbc,
                                       self.gui.radio_log_cbc, self.gui.txt_fix_cbc, self.gui.txt_gauss_min_cbc,
                                       self.gui.txt_gauss_max_cbc, self.gui.txt_gauss_mean_cbc,
                                       self.gui.txt_gauss_std_cbc,
                                       self.gui.txt_log_min_cbc, self.gui.txt_log_max_cbc,
                                       self.gui.txt_log_steps_cbc,
                                       self.gui.viewCbc],
                            "lai": [self.gui.radio_fix_lai, self.gui.radio_gauss_lai, self.gui.radio_uni_lai,
                                 self.gui.radio_log_lai, self.gui.txt_fix_lai, self.gui.txt_gauss_min_lai,
                                 self.gui.txt_gauss_max_lai, self.gui.txt_gauss_mean_lai, self.gui.txt_gauss_std_lai,
                                 self.gui.txt_log_min_lai, self.gui.txt_log_max_lai, self.gui.txt_log_steps_lai,
                                 self.gui.viewLAI],
                            "alia": [self.gui.radio_fix_alia, self.gui.radio_gauss_alia, self.gui.radio_uni_alia,
                                     self.gui.radio_log_alia, self.gui.txt_fix_alia, self.gui.txt_gauss_min_alia,
                                     self.gui.txt_gauss_max_alia, self.gui.txt_gauss_mean_alia, self.gui.txt_gauss_std_alia,
                                     self.gui.txt_log_min_alia, self.gui.txt_log_max_alia, self.gui.txt_log_steps_alia,
                                     self.gui.viewALIA],
                            "hspot": [self.gui.radio_fix_hspot, self.gui.radio_gauss_hspot, self.gui.radio_uni_hspot,
                                 self.gui.radio_log_hspot, self.gui.txt_fix_hspot, self.gui.txt_gauss_min_hspot,
                                 self.gui.txt_gauss_max_hspot, self.gui.txt_gauss_mean_hspot, self.gui.txt_gauss_std_hspot,
                                 self.gui.txt_log_min_hspot, self.gui.txt_log_max_hspot, self.gui.txt_log_steps_hspot,
                                 self.gui.viewHspot],
                            "oza": [self.gui.radio_fix_oza, self.gui.radio_gauss_oza, self.gui.radio_uni_oza,
                                 self.gui.radio_log_oza, self.gui.txt_fix_oza, self.gui.txt_gauss_min_oza,
                                 self.gui.txt_gauss_max_oza, self.gui.txt_gauss_mean_oza, self.gui.txt_gauss_std_oza,
                                 self.gui.txt_log_min_oza, self.gui.txt_log_max_oza, self.gui.txt_log_steps_oza,
                                 self.gui.viewOZA],
                            "sza": [self.gui.radio_fix_sza, self.gui.radio_gauss_sza, self.gui.radio_uni_sza,
                                 self.gui.radio_log_sza, self.gui.txt_fix_sza, self.gui.txt_gauss_min_sza,
                                 self.gui.txt_gauss_max_sza, self.gui.txt_gauss_mean_sza, self.gui.txt_gauss_std_sza,
                                 self.gui.txt_log_min_sza, self.gui.txt_log_max_sza, self.gui.txt_log_steps_sza,
                                 self.gui.viewSZA],
                            "raa": [self.gui.radio_fix_raa, self.gui.radio_gauss_raa, self.gui.radio_uni_raa,
                                 self.gui.radio_log_raa, self.gui.txt_fix_raa, self.gui.txt_gauss_min_raa,
                                 self.gui.txt_gauss_max_raa, self.gui.txt_gauss_mean_raa, self.gui.txt_gauss_std_raa,
                                 self.gui.txt_log_min_raa, self.gui.txt_log_max_raa, self.gui.txt_log_steps_raa,
                                 self.gui.viewRAA],
                            "psoil": [self.gui.radio_fix_psoil, self.gui.radio_gauss_psoil, self.gui.radio_uni_psoil,
                                 self.gui.radio_log_psoil, self.gui.txt_fix_psoil, self.gui.txt_gauss_min_psoil,
                                 self.gui.txt_gauss_max_psoil, self.gui.txt_gauss_mean_psoil, self.gui.txt_gauss_std_psoil,
                                 self.gui.txt_log_min_psoil, self.gui.txt_log_max_psoil, self.gui.txt_log_steps_psoil,
                                 self.gui.viewPsoil],
                            "laiu": [self.gui.radio_fix_laiu, self.gui.radio_gauss_laiu, self.gui.radio_uni_laiu,
                                 self.gui.radio_log_laiu, self.gui.txt_fix_laiu, self.gui.txt_gauss_min_laiu,
                                 self.gui.txt_gauss_max_laiu, self.gui.txt_gauss_mean_laiu, self.gui.txt_gauss_std_laiu,
                                 self.gui.txt_log_min_laiu, self.gui.txt_log_max_laiu, self.gui.txt_log_steps_laiu,
                                 self.gui.viewLAIu],
                            "sd": [self.gui.radio_fix_sd, self.gui.radio_gauss_sd, self.gui.radio_uni_sd,
                                 self.gui.radio_log_sd, self.gui.txt_fix_sd, self.gui.txt_gauss_min_sd,
                                 self.gui.txt_gauss_max_sd, self.gui.txt_gauss_mean_sd, self.gui.txt_gauss_std_sd,
                                 self.gui.txt_log_min_sd, self.gui.txt_log_max_sd, self.gui.txt_log_steps_sd,
                                 self.gui.viewSD],
                            "h": [self.gui.radio_fix_h, self.gui.radio_gauss_h, self.gui.radio_uni_h,
                                 self.gui.radio_log_h, self.gui.txt_fix_h, self.gui.txt_gauss_min_h,
                                 self.gui.txt_gauss_max_h, self.gui.txt_gauss_mean_h, self.gui.txt_gauss_std_h,
                                 self.gui.txt_log_min_h, self.gui.txt_log_max_h, self.gui.txt_log_steps_h,
                                 self.gui.viewH],
                            "cd": [self.gui.radio_fix_cd, self.gui.radio_gauss_cd, self.gui.radio_uni_cd,
                                 self.gui.radio_log_cd, self.gui.txt_fix_cd, self.gui.txt_gauss_min_cd,
                                 self.gui.txt_gauss_max_cd, self.gui.txt_gauss_mean_cd, self.gui.txt_gauss_std_cd,
                                 self.gui.txt_log_min_cd, self.gui.txt_log_max_cd, self.gui.txt_log_steps_cd,
                                 self.gui.viewCD]}

    def connections(self):
        # Sensor Type
        self.gui.SType_None_B.clicked.connect(lambda: self.select_s2s(sensor="default"))
        self.gui.SType_Sentinel_B.clicked.connect(lambda: self.select_s2s(sensor="Sentinel2"))
        self.gui.SType_Landsat_B.clicked.connect(lambda: self.select_s2s(sensor="Landsat8"))
        self.gui.SType_Enmap_B.clicked.connect(lambda: self.select_s2s(sensor="EnMAP"))

        # Models
        self.gui.B_Prospect4.clicked.connect(lambda: self.select_model(lop="prospect4", canopy_arch=self.canopy_arch))
        self.gui.B_Prospect5.clicked.connect(lambda: self.select_model(lop="prospect5", canopy_arch=self.canopy_arch))
        self.gui.B_Prospect5b.clicked.connect(lambda: self.select_model(lop="prospect5B", canopy_arch=self.canopy_arch))
        self.gui.B_ProspectD.clicked.connect(lambda: self.select_model(lop="prospectD", canopy_arch=self.canopy_arch))
        self.gui.B_ProspectPro.clicked.connect(lambda: self.select_model(lop="prospectPro", canopy_arch=self.canopy_arch))

        self.gui.B_LeafModelOnly.clicked.connect(lambda: self.select_model(lop=self.lop, canopy_arch=None))
        self.gui.B_4Sail.clicked.connect(lambda: self.select_model(lop=self.lop, canopy_arch="sail"))
        self.gui.B_Inform.clicked.connect(lambda: self.select_model(lop=self.lop, canopy_arch="inform"))

        #Select Background
        self.gui.B_DefSoilSpec.clicked.connect(lambda: self.select_background(bg_type="default"))
        self.gui.B_LoadBackSpec.clicked.connect(lambda: self.select_background(bg_type="load"))
        self.gui.B_LoadBackSpec.pressed.connect(lambda: self.select_background(bg_type="load"))
        self.gui.push_SelectFile.clicked.connect(lambda: self.open_file(type="background"))  # load own spectrum

        # dependencies:
        self.gui.CarCabCheck.stateChanged.connect(lambda: self.init_dependency(which='car_cab'))

        # Radio Buttons
        self.gui.radio_fix_N.clicked.connect(lambda: self.txt_enables(para="N", mode="fix"))
        self.gui.radio_gauss_N.clicked.connect(lambda: self.txt_enables(para="N", mode="gauss"))
        self.gui.radio_uni_N.clicked.connect(lambda: self.txt_enables(para="N", mode="uni"))
        self.gui.radio_log_N.clicked.connect(lambda: self.txt_enables(para="N", mode="log"))

        self.gui.radio_fix_chl.clicked.connect(lambda: self.txt_enables(para="chl", mode="fix"))
        self.gui.radio_gauss_chl.clicked.connect(lambda: self.txt_enables(para="chl", mode="gauss"))
        self.gui.radio_uni_chl.clicked.connect(lambda: self.txt_enables(para="chl", mode="uni"))
        self.gui.radio_log_chl.clicked.connect(lambda: self.txt_enables(para="chl", mode="log"))

        self.gui.radio_fix_cw.clicked.connect(lambda: self.txt_enables(para="cw", mode="fix"))
        self.gui.radio_gauss_cw.clicked.connect(lambda: self.txt_enables(para="cw", mode="gauss"))
        self.gui.radio_uni_cw.clicked.connect(lambda: self.txt_enables(para="cw", mode="uni"))
        self.gui.radio_log_cw.clicked.connect(lambda: self.txt_enables(para="cw", mode="log"))

        self.gui.radio_fix_cm.clicked.connect(lambda: self.txt_enables(para="cm", mode="fix"))
        self.gui.radio_gauss_cm.clicked.connect(lambda: self.txt_enables(para="cm", mode="gauss"))
        self.gui.radio_uni_cm.clicked.connect(lambda: self.txt_enables(para="cm", mode="uni"))
        self.gui.radio_log_cm.clicked.connect(lambda: self.txt_enables(para="cm", mode="log"))

        self.gui.radio_fix_car.clicked.connect(lambda: self.txt_enables(para="car", mode="fix"))
        self.gui.radio_gauss_car.clicked.connect(lambda: self.txt_enables(para="car", mode="gauss"))
        self.gui.radio_uni_car.clicked.connect(lambda: self.txt_enables(para="car", mode="uni"))
        self.gui.radio_log_car.clicked.connect(lambda: self.txt_enables(para="car", mode="log"))

        self.gui.radio_fix_canth.clicked.connect(lambda: self.txt_enables(para="canth", mode="fix"))
        self.gui.radio_gauss_canth.clicked.connect(lambda: self.txt_enables(para="canth", mode="gauss"))
        self.gui.radio_uni_canth.clicked.connect(lambda: self.txt_enables(para="canth", mode="uni"))
        self.gui.radio_log_canth.clicked.connect(lambda: self.txt_enables(para="canth", mode="log"))

        self.gui.radio_fix_cp.clicked.connect(lambda: self.txt_enables(para="cp", mode="fix"))
        self.gui.radio_gauss_cp.clicked.connect(lambda: self.txt_enables(para="cp", mode="gauss"))
        self.gui.radio_uni_cp.clicked.connect(lambda: self.txt_enables(para="cp", mode="uni"))
        self.gui.radio_log_cp.clicked.connect(lambda: self.txt_enables(para="cp", mode="log"))

        self.gui.radio_fix_cbc.clicked.connect(lambda: self.txt_enables(para="cbc", mode="fix"))
        self.gui.radio_gauss_cbc.clicked.connect(lambda: self.txt_enables(para="cbc", mode="gauss"))
        self.gui.radio_uni_cbc.clicked.connect(lambda: self.txt_enables(para="cbc", mode="uni"))
        self.gui.radio_log_cbc.clicked.connect(lambda: self.txt_enables(para="cbc", mode="log"))

        self.gui.radio_fix_cbr.clicked.connect(lambda: self.txt_enables(para="cbr", mode="fix"))
        self.gui.radio_gauss_cbr.clicked.connect(lambda: self.txt_enables(para="cbr", mode="gauss"))
        self.gui.radio_uni_cbr.clicked.connect(lambda: self.txt_enables(para="cbr", mode="uni"))
        self.gui.radio_log_cbr.clicked.connect(lambda: self.txt_enables(para="cbr", mode="log"))

        self.gui.radio_fix_lai.clicked.connect(lambda: self.txt_enables(para="lai", mode="fix"))
        self.gui.radio_gauss_lai.clicked.connect(lambda: self.txt_enables(para="lai", mode="gauss"))
        self.gui.radio_uni_lai.clicked.connect(lambda: self.txt_enables(para="lai", mode="uni"))
        self.gui.radio_log_lai.clicked.connect(lambda: self.txt_enables(para="lai", mode="log"))

        self.gui.radio_fix_alia.clicked.connect(lambda: self.txt_enables(para="alia", mode="fix"))
        self.gui.radio_gauss_alia.clicked.connect(lambda: self.txt_enables(para="alia", mode="gauss"))
        self.gui.radio_uni_alia.clicked.connect(lambda: self.txt_enables(para="alia", mode="uni"))
        self.gui.radio_log_alia.clicked.connect(lambda: self.txt_enables(para="alia", mode="log"))

        self.gui.radio_fix_hspot.clicked.connect(lambda: self.txt_enables(para="hspot", mode="fix"))
        self.gui.radio_gauss_hspot.clicked.connect(lambda: self.txt_enables(para="hspot", mode="gauss"))
        self.gui.radio_uni_hspot.clicked.connect(lambda: self.txt_enables(para="hspot", mode="uni"))
        self.gui.radio_log_hspot.clicked.connect(lambda: self.txt_enables(para="hspot", mode="log"))

        self.gui.radio_fix_oza.clicked.connect(lambda: self.txt_enables(para="oza", mode="fix"))
        self.gui.radio_gauss_oza.clicked.connect(lambda: self.txt_enables(para="oza", mode="gauss"))
        self.gui.radio_uni_oza.clicked.connect(lambda: self.txt_enables(para="oza", mode="uni"))
        self.gui.radio_log_oza.clicked.connect(lambda: self.txt_enables(para="oza", mode="log"))

        self.gui.radio_fix_sza.clicked.connect(lambda: self.txt_enables(para="sza", mode="fix"))
        self.gui.radio_gauss_sza.clicked.connect(lambda: self.txt_enables(para="sza", mode="gauss"))
        self.gui.radio_uni_sza.clicked.connect(lambda: self.txt_enables(para="sza", mode="uni"))
        self.gui.radio_log_sza.clicked.connect(lambda: self.txt_enables(para="sza", mode="log"))

        self.gui.radio_fix_raa.clicked.connect(lambda: self.txt_enables(para="raa", mode="fix"))
        self.gui.radio_gauss_raa.clicked.connect(lambda: self.txt_enables(para="raa", mode="gauss"))
        self.gui.radio_uni_raa.clicked.connect(lambda: self.txt_enables(para="raa", mode="uni"))
        self.gui.radio_log_raa.clicked.connect(lambda: self.txt_enables(para="raa", mode="log"))

        self.gui.radio_fix_psoil.clicked.connect(lambda: self.txt_enables(para="psoil", mode="fix"))
        self.gui.radio_gauss_psoil.clicked.connect(lambda: self.txt_enables(para="psoil", mode="gauss"))
        self.gui.radio_uni_psoil.clicked.connect(lambda: self.txt_enables(para="psoil", mode="uni"))
        self.gui.radio_log_psoil.clicked.connect(lambda: self.txt_enables(para="psoil", mode="log"))

        self.gui.radio_fix_sd.clicked.connect(lambda: self.txt_enables(para="sd", mode="fix"))
        self.gui.radio_gauss_sd.clicked.connect(lambda: self.txt_enables(para="sd", mode="gauss"))
        self.gui.radio_uni_sd.clicked.connect(lambda: self.txt_enables(para="sd", mode="uni"))
        self.gui.radio_log_sd.clicked.connect(lambda: self.txt_enables(para="sd", mode="log"))

        self.gui.radio_fix_laiu.clicked.connect(lambda: self.txt_enables(para="laiu", mode="fix"))
        self.gui.radio_gauss_laiu.clicked.connect(lambda: self.txt_enables(para="laiu", mode="gauss"))
        self.gui.radio_uni_laiu.clicked.connect(lambda: self.txt_enables(para="laiu", mode="uni"))
        self.gui.radio_log_laiu.clicked.connect(lambda: self.txt_enables(para="laiu", mode="log"))

        self.gui.radio_fix_h.clicked.connect(lambda: self.txt_enables(para="h", mode="fix"))
        self.gui.radio_gauss_h.clicked.connect(lambda: self.txt_enables(para="h", mode="gauss"))
        self.gui.radio_uni_h.clicked.connect(lambda: self.txt_enables(para="h", mode="uni"))
        self.gui.radio_log_h.clicked.connect(lambda: self.txt_enables(para="h", mode="log"))

        self.gui.radio_fix_cd.clicked.connect(lambda: self.txt_enables(para="cd", mode="fix"))
        self.gui.radio_gauss_cd.clicked.connect(lambda: self.txt_enables(para="cd", mode="gauss"))
        self.gui.radio_uni_cd.clicked.connect(lambda: self.txt_enables(para="cd", mode="uni"))
        self.gui.radio_log_cd.clicked.connect(lambda: self.txt_enables(para="cd", mode="log"))

        # Buttons
        self.gui.cmdRun.clicked.connect(lambda: self.run_LUT())
        self.gui.cmdClose.clicked.connect(lambda: self.gui.close())
        self.gui.cmdOpenFolder.clicked.connect(lambda: self.get_folder())
        self.gui.cmdLUTcalc.clicked.connect(lambda: self.get_lutsize())
        # self.gui.cmdPlot.clicked.connect(lambda: self.plot_para())
        # self.gui.cmdTest.clicked.connect(lambda: self.test_LUT()) #debug

        # Focus Out (Line Edits)
        for para in self.dict_objects:
            for i in range(4,12): # 4: fixed; 5-8: min, max, mean, std; 9-11: logical min, max, step
                self.dict_objects[para][i].installEventFilter(self._filter)

    def txt_enables(self, para, mode):

        if mode=="fix":
            self.dict_objects[para][4].setEnabled(True)
            for i in range(5, 12):
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")

        elif mode=="gauss":
            for i in [4, 9, 10, 11]:
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")
            for i in range(5, 9):
                self.dict_objects[para][i].setEnabled(True)

        elif mode=="uni":
            for i in [4, 7, 8, 9, 10, 11]:
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")
            self.dict_objects[para][5].setEnabled(True)
            self.dict_objects[para][6].setEnabled(True)

        elif mode=="log":
            for i in range(4, 9):
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")
            for i in [9, 10, 11]:
                self.dict_objects[para][i].setEnabled(True)

        if para in self.dict_checks:
            self.dict_checks[para] = mode

    def init_dependency(self, which):
        if which == 'car_cab' and self.depends == 0:
            self.depends = 1
            for object in range(12):
                self.dict_objects["car"][object].setDisabled(True)
        else:
            self.depends = 0
            for object in range(12):
                self.dict_objects["car"][object].setDisabled(False)
        # if which == 'placeholder_1' ...


    def set_boundaries(self):
        self.dict_boundaries = {"N": [1.0, 3.0],  # 0
                            "chl": [0.0, 100.0],  # 1
                             "cw": [0.001, 0.7],  # 2
                             "cm": [0.0001, 0.02],  # 3
                             "car": [0.0, 30.0],  # 4
                             "cbr": [0.0, 1.0],  # 5
                             "canth": [0.0, 10.0],  # 6
                             "lai": [0.01, 10.0],  # 7
                             "cp": [0.0, 0.01],  # 8
                             "cbc": [0.0, 0.01],  # 9
                             "alia": [0.0, 90.0],  # 10
                             "hspot": [0.0, 1.0],  # 11
                             "oza": [0.0, 89.0],  # 12
                             "sza": [0.0, 89.0],  # 13
                             "raa": [0.0, 180.0],  # 14
                             "psoil": [0.0, 1.0],  # 15
                             "laiu": [0.01, 10.0],  # 16 forest parameters temporary!
                             "sd": [0.0, 5000.0],  # 17
                             "h": [0.0, 50.0],  # 18
                             "cd": [0.0, 30.0]}  # 19

    def select_s2s(self, sensor):
        self.sensor = sensor
        if not sensor == "default":
            s2s = Spec2Sensor(sensor=sensor, nodat=-999)
            s2s.init_sensor()
            self.wl = s2s.wl_sensor
            self.gui.spinIntBoost.setValue(10000)
        else:
            self.wl = range(400, 2501)
            self.gui.spinIntBoost.setValue(1)

    def select_model(self, lop="prospectD", canopy_arch="sail"):
        self.lop = lop
        if canopy_arch is None:
            self.canopy_arch = None
            self.gui.BackSpec_label.setEnabled(False)
            self.gui.B_DefSoilSpec.setEnabled(False)
            self.gui.B_LoadBackSpec.setEnabled(False)
            self.gui.grp_canopy.setDisabled(True)
            self.gui.grp_forest.setDisabled(True)
        elif canopy_arch == "sail":
            self.canopy_arch = canopy_arch
            self.gui.lblLAI.setText("Leaf Area Index (LAI) [m2/m2]\n[0.01-10.0]")
            self.gui.grp_canopy.setDisabled(False)
            self.gui.grp_forest.setDisabled(True)
            self.gui.B_Prospect5.setDisabled(False)
            self.gui.B_Prospect4.setDisabled(False)
            self.gui.B_Prospect5b.setDisabled(False)
            self.select_background(bg_type=self.bg_type)
        elif canopy_arch == "inform":
            self.canopy_arch = canopy_arch
            self.gui.lblLAI.setText("Single Tree \nLeaf Area Index (LAI) [m2/m2]\n[0.01-10.0]")
            self.gui.grp_canopy.setDisabled(False)
            self.gui.grp_forest.setDisabled(False)
            self.gui.lblLAIu.setDisabled(False)
            #self.gui.B_Prospect5.setDisabled(True)
            #self.gui.B_Prospect4.setDisabled(True)
            #self.gui.B_Prospect5b.setDisabled(True)
            #self.gui.B_ProspectD.setChecked(True)
            self.select_background(bg_type=self.bg_type)

        if lop == "prospectPro":
            for para in self.para_list[0]:
                for object in range(4):
                    self.dict_objects[para][object].setDisabled(False)
            self.txt_enables(para="car", mode=self.dict_checks["car"])
            self.txt_enables(para="cbr", mode=self.dict_checks["cbr"])
            self.txt_enables(para="canth", mode=self.dict_checks["canth"])
            self.txt_enables(para="cp", mode=self.dict_checks["cp"])
            self.txt_enables(para="cbc", mode=self.dict_checks["cbc"])

        if lop == "prospectD":
            for para in self.para_list[0]:
                for object in range(4):
                    self.dict_objects[para][object].setDisabled(False)
            for object in range(12):
                self.dict_objects["cp"][object].setDisabled(True)
                self.dict_objects["cbc"][object].setDisabled(True)
            self.txt_enables(para="car", mode=self.dict_checks["car"])
            self.txt_enables(para="cbr", mode=self.dict_checks["cbr"])
            self.txt_enables(para="canth", mode=self.dict_checks["canth"])

        elif lop == "prospect5B":
            for para in self.para_list[0]:
                for object in range(4):
                    self.dict_objects[para][object].setDisabled(False)
            for object in range(12):
                self.dict_objects["canth"][object].setDisabled(True)
                self.dict_objects["cp"][object].setDisabled(True)
                self.dict_objects["cbc"][object].setDisabled(True)
            self.txt_enables(para="car", mode=self.dict_checks["car"])
            self.txt_enables(para="cbr", mode=self.dict_checks["cbr"])

        elif lop == "prospect5":
            for para in self.para_list[0]:
                for object in range(4):
                    self.dict_objects[para][object].setDisabled(False)
                for object in range(12):
                    self.dict_objects["canth"][object].setDisabled(True)
                    self.dict_objects["cbr"][object].setDisabled(True)
                    self.dict_objects["cp"][object].setDisabled(True)
                    self.dict_objects["cbc"][object].setDisabled(True)
            self.txt_enables(para="car", mode=self.dict_checks["car"])

        elif lop == "prospect4":
            for para in self.para_list[0]:
                for object in range(4):
                    self.dict_objects[para][object].setDisabled(False)
                for object in range(12):
                    self.dict_objects["canth"][object].setDisabled(True)
                    self.dict_objects["cbr"][object].setDisabled(True)
                    self.dict_objects["car"][object].setDisabled(True)
                    self.dict_objects["cp"][object].setDisabled(True)
                    self.dict_objects["cbc"][object].setDisabled(True)

    def select_background(self, bg_type):
        self.bg_type = bg_type
        if bg_type == "default":
            self.gui.B_DefSoilSpec.setEnabled(True)
            self.gui.B_LoadBackSpec.setEnabled(True)
            self.gui.push_SelectFile.setEnabled(False)
            self.gui.BackSpec_label.setEnabled(False)
            self.gui.BackSpec_label.setText("")
            self.bg_spec = None

            for para in self.para_list[1]:
                for object in range(4):
                    self.dict_objects[para][object].setDisabled(False)
                for object in range(12):
                    self.dict_objects["psoil"][object].setDisabled(False)

        elif bg_type == "load":
            self.gui.B_DefSoilSpec.setEnabled(True)
            self.gui.B_LoadBackSpec.setEnabled(True)
            self.gui.push_SelectFile.setEnabled(True)
            self.gui.push_SelectFile.setText('Select File...')
            self.gui.BackSpec_label.setEnabled(True)

            for para in self.para_list[1]:
                for object in range(4):
                    self.dict_objects[para][object].setDisabled(False)
                for object in range(12):
                    self.dict_objects["psoil"][object].setDisabled(True)


    def get_folder(self):
        path = str(QFileDialog.getExistingDirectory(caption='Select Directory for LUT'))

        if path:
            self.gui.lblOutPath.setText(path)
            self.path = self.gui.lblOutPath.text().replace("\\", "/")
            if not self.path[-1] == "/":
                self.path += "/"

    def get_inputs(self):
        self.dict_vals = dict(zip(self.para_flat, ([] for _ in range(self.npara_flat))))
        for para in self.dict_objects:

            for object in range(4, 12):
                if not self.dict_objects[para][object].text() == "":
                    try:
                        self.dict_vals[para].append(float(self.dict_objects[para][object].text()))
                    except ValueError:
                        QMessageBox.critical(self.gui, "Not a number", "'%s' is not a valid number" % self.dict_objects[para][object].text())
                        self.dict_vals = dict(zip(self.para_flat, ([] for i in range(self.npara_flat))))  # reset dict_vals
                        return

        self.LUT_name = self.gui.txtLUTname.text()
        self.ns = int(self.gui.spinNS.value())
        self.intboost = int(self.gui.spinIntBoost.value())
        self.nodat = int(self.gui.spinNoData.value())

    def check_inputs(self):

        for i, key in enumerate(self.para_list[0]):
            if key == 'car' and self.depends != 0:
                continue
            elif len(self.dict_vals[self.para_list[0][i]]) > 3:
                if self.dict_vals[self.para_list[0][i]][2] > self.dict_vals[self.para_list[0][i]][1] or \
                                self.dict_vals[self.para_list[0][i]][2] < self.dict_vals[self.para_list[0][i]][0]:
                    self.abort(message='Parameter %s: mean value must lie between min and max' % self.para_list[0][i])
                    return False
                elif self.dict_vals[self.para_list[0][i]][0] < self.dict_boundaries[key][0] or \
                                self.dict_vals[self.para_list[0][i]][1] > self.dict_boundaries[key][1]:
                    self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[0][i])
                    #print(self.para_list[0][0])
                    return False
            elif len(self.dict_vals[self.para_list[0][i]]) > 1:  # min and max specified
                if self.dict_vals[self.para_list[0][i]][0] < self.dict_boundaries[key][0] or \
                                self.dict_vals[self.para_list[0][i]][1] > self.dict_boundaries[key][1]:
                    self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[0][i])
                    return False
            elif len(self.dict_vals[self.para_list[0][i]]) > 0:  # fixed value specified
                if self.dict_vals[self.para_list[0][i]][0] < self.dict_boundaries[key][0] or \
                                self.dict_vals[self.para_list[0][i]][0] > self.dict_boundaries[key][1]:
                    self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[0][i])
                    return False

        if self.canopy_arch == "sail":
            for i, key in enumerate(self.para_list[1]):
                if key == 'car' and self.depends != 0:
                    continue
                elif len(self.dict_vals[self.para_list[1][i]]) > 3:
                    if self.dict_vals[self.para_list[1][i]][2] > self.dict_vals[self.para_list[1][i]][1] or \
                                    self.dict_vals[self.para_list[1][i]][2] < self.dict_vals[self.para_list[1][i]][0]:
                        self.abort(message='Parameter %s: mean value must lie between min and max' % self.para_list[1][i])
                        return False
                    elif self.dict_vals[self.para_list[1][i]][0] < self.dict_boundaries[key][0] or \
                                    self.dict_vals[self.para_list[1][i]][1] > self.dict_boundaries[key][1]:
                        self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[1][i])
                        return False
                elif len(self.dict_vals[self.para_list[1][i]]) > 1:  # min and max specified
                    if self.dict_vals[self.para_list[1][i]][0] < self.dict_boundaries[key][0] or \
                                    self.dict_vals[self.para_list[1][i]][1] > self.dict_boundaries[key][1]:
                        self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[1][i])
                        return False
                elif len(self.dict_vals[self.para_list[1][i]]) > 0:  # min and max specified
                    if self.dict_vals[self.para_list[1][i]][0] < self.dict_boundaries[key][0] or \
                                    self.dict_vals[self.para_list[1][i]][0] > self.dict_boundaries[key][1]:
                        self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[1][i])
                        return False
        if self.lop == "prospectPro":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in range(len(self.para_list[0])-1)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False
        if self.lop == "prospectD":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in range(len(self.para_list[0])-2)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False
        elif self.lop == "prospect5B":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in range(len(self.para_list[0])-3)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False
        elif self.lop == "prospect5":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in range(len(self.para_list[0])-4)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False
        elif self.lop == "prospect4":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in range(len(self.para_list[0])-5)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False

        if self.canopy_arch == "sail" and self.bg_type == "default":
            if any(len(self.dict_vals[self.para_list[1][i]]) < 1 for i in range(len(self.para_list[1]))):
                self.abort(message='Canopy Architecture parameter(s) missing')
                return False

        if self.canopy_arch == "sail" and self.bg_type == "load":
            if any(len(self.dict_vals[self.para_list[1][i]]) < 1 for i in range(len(self.para_list[1])-1)):
                self.abort(message='Canopy Architecture parameter(s) missing')
                return False

        if self.canopy_arch == "inform":
            if any(len(self.dict_vals[self.para_list[2][i]]) < 1 for i in range(len(self.para_list[2]))):
                self.abort(message='Forest Canopy Architecture parameter(s) missing')
                return False

        if not os.path.isdir(self.gui.lblOutPath.text()):
            self.abort(message='Incorrect Path')
            return False

        if self.LUT_name == "" or self.LUT_name is None:
            self.abort(message='Incorrect LUT name')
            return False

        return True

    def get_lutsize(self):
        self.get_inputs()
        self.nlut_total = self.ns
        for para in self.dict_vals:
            if len(self.dict_vals[para]) == 3 and any(self.dict_objects[para][i].isEnabled() for i in range(4)):
                self.nlut_total *= self.dict_vals[para][2]

        if self.speed is None:
            self.speedtest()
        time50x = self.speedtest()
        self.speed = time50x*self.nlut_total/50

        if self.speed > 172800:
            self.gui.lblTimeUnit.setText("days")
            self.speed /= 86400
        elif self.speed > 10800:
            self.gui.lblTimeUnit.setText("hours")
            self.speed /= 3600
        elif self.speed > 120:
            self.gui.lblTimeUnit.setText("min")
            self.speed /= 60
        else:
            self.gui.lblTimeUnit.setText("sec")

        self.gui.lcdNumber.display(self.nlut_total)
        self.gui.lcdSpeed.display(self.speed)

    def plot_para(self):

        min = 1.0
        max = 3.0
        mean = 1.7
        sigma = 0.3
        ns = 2000

        # bla = truncnorm((min - mean) / sigma, (max - mean) / sigma, loc=mean, scale=sigma).rvs(ns)

        xVals = np.arange(1.0, 3.0, 0.001)
        self.gui.viewN.plot(xVals, norm.pdf(xVals, loc=1.7, scale=0.3), clear=True)
        # self.gui.viewN.setRange(rect=None, range=(0,15), yRange=(0,50), padding=None, update=True, disableAutoRange=True)

        # self.gui.graphicsView.plot(self.wl, self.myResult, pen="g", fillLevel=0, fillBrush=(255, 255, 255, 30),
        #                            name='modelled')
        #
        # self.gui.graphicsView.setYRange(0, 0.6, padding=0)
        # self.gui.graphicsView.setLabel('left', text="Reflectance [%]")
        # self.gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")

    def speedtest(self):

        model_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=self.nodat,
                                 int_boost=self.intboost, s2s=self.sensor)
        time50x = model_I.initialize_vectorized(LUT_dir=None, LUT_name=None, ns=100, tts=[20.0, 60.0], tto=[0.0, 40.0],
                                    psi=[0.0, 180.0], N=[1.1, 2.5], cab=[0.0, 80.0], cw=[0.0002, 0.02],
                                    cm=[0.0001, 0.005], LAI=[0.5, 8.0], LIDF=[10.0, 80.0], typeLIDF=[2],
                                    hspot=[0.1], psoil=[0.5], car=[0.0, 12.0],
                                    cbrown=[0.0, 1.0], anth=[0.0, 10.0], cp=[0.001], cbc=[0.01],
                                                soil=[0.1]*2101, depends=0, testmode=True)

        return time50x/2

    def test_LUT(self):

        self.main.prg_widget.gui.lblCaption_l.setText("Global Inversion")
        self.main.prg_widget.gui.lblCaption_r.setText("Setting up inversion...")
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()


        # model_I = mod.Init_Model(lop="prospect4", canopy_arch=None, nodat=-999,
        #                          int_boost=1, s2s="default")
        # model_I.initialize_multiple(LUT_dir="D:/Temp/LUT/", LUT_name="One", ns=3,
        #                             tts=[],
        #                             tto=[], psi=[], N=[1.0],
        #                             cab=[0.0, 8.0, 9], cw=[0.2, 1.0, 5], cm=[0.018],
        #                             LAI=[], LIDF=[], typeLIDF=[],
        #                             hspot=[], psoil=[], car=[],
        #                             cbrown=[], anth=[], prgbar_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)

        model_I = mod.Init_Model(lop="prospectD", canopy_arch="sail", nodat=-999,
                                 int_boost=1, s2s="default")
        model_I.initialize_multiple(LUT_dir="D:/Temp/LUT_debug/", LUT_name="Test", ns=100,
                                    tts=[20,50,3],
                                    tto=[0,30,2], psi=[0], N=[1.0],
                                    cab=[1.0, 80.0, 5], cw=[0.02, 0.04, 3], cm=[0.018],
                                    LAI=[5.0], LIDF=[45.0], typeLIDF=[2],
                                    hspot=[0.1], psoil=[0.5], car=[],
                                    cbrown=[], anth=[], cp=[], cbc=[], LAIu=[], cd=[], sd=[], h=[], depends=0,
                                    prgbar_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)

        # model_I = mod.Init_Model(lop="prospectD", canopy_arch="sail", nodat=-999,
        #                          int_boost=1000, s2s="default")
        # lut_run = model_I.initialize_multiple(LUT_dir="D:/Work/Temp/LUT/", LUT_name="One", ns=2000,
        #                             tts=[20.0, 50.0, 4.0],
        #                             tto=[0.0], psi=[45.0], N=[1.0, 2.5],
        #                             cab=[0.0, 80.0, 45.0, 5.0], cw=[0.002, 0.02], cm=[0.018],
        #                             LAI=[1.0, 8.0], LIDF=[20.0, 80.0, 40.0, 10.0], typeLIDF=[2],
        #                             hspot=[0.1], psoil=[0.0, 1.0], car=[0.0, 15.0],
        #                             cbrown=[0.0, 1.0], anth=[5.0], prgbar_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)

        QMessageBox.information(self.gui, "Successfull", "The Look-Up-Table has successfully been created!")

    def run_LUT(self):
        self.get_inputs()
        if not self.check_inputs():
            return
        self.get_lutsize()
        self.gui.lcdNumber.display(self.nlut_total)
        self.gui.lcdSpeed.display(self.speed)
        self.main.QGis_app.processEvents()

        self.main.prg_widget.gui.lblCaption_l.setText("Global Inversion")
        self.main.prg_widget.gui.lblCaption_r.setText("Setting up inversion...")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()


        try:
            model_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=self.nodat,
                                     int_boost=self.intboost, s2s=self.sensor)
        except ValueError as e:
            self.abort(message="An error occurred while initializing the LUT: %s" % str(e))
            self.main.prg_widget.gui.lblCancel.setText("")
            self.main.prg_widget.gui.close()
            return

        try:
            model_I.initialize_vectorized(LUT_dir=self.path, LUT_name=self.LUT_name, ns=self.ns,
                                        tts=self.dict_vals['sza'], tto=self.dict_vals['oza'], psi=self.dict_vals['raa'], 
                                        N=self.dict_vals['N'], cab=self.dict_vals['chl'], cw=self.dict_vals['cw'], 
                                        cm=self.dict_vals['cm'], LAI=self.dict_vals['lai'], LIDF=self.dict_vals['alia'], 
                                        typeLIDF=[2], hspot=self.dict_vals['hspot'], psoil=self.dict_vals['psoil'], 
                                        car=self.dict_vals['car'], cbrown=self.dict_vals['cbr'], soil=self.bg_spec,
                                        anth=self.dict_vals['canth'], cp=self.dict_vals['cp'],
                                        cbc=self.dict_vals['cbc'], LAIu=self.dict_vals['laiu'],
                                        cd=self.dict_vals['cd'], sd=self.dict_vals['sd'], h=self.dict_vals['h'],
                                        prgbar_widget=self.main.prg_widget, QGis_app=self.main.QGis_app,
                                        depends=self.depends)

        except ValueError as e:
            self.abort(message="An error occured while creating the LUT: %s" % str(e))
            self.main.prg_widget.gui.lblCancel.setText("")
            self.main.prg_widget.gui.close()
            return

        QMessageBox.information(self.gui, "Successfull", "The Look-Up-Table has successfully been created!")
        self.main.prg_widget.gui.lblCancel.setText("")
        self.main.prg_widget.gui.allow_cancel = True
        self.main.prg_widget.gui.close()
        #self.gui.close()

    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)

    def open_file(self, type):
        self.main.loadtxtfile.open(type=type)

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
        self.main.LUT.wl_open = self.wl_open
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

            self.main.LUT.bg_spec = self.main.loadtxtfile.data_mean
            self.main.LUT.gui.BackSpec_label.setText(os.path.basename(self.main.loadtxtfile.filenameIn))
            self.main.LUT.gui.push_SelectFile.setEnabled(False)
            self.main.LUT.gui.push_SelectFile.setText('File:')

        for list_object in [self.gui.lstIncluded, self.gui.lstExcluded]:
            list_object.clear()

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

class PRG:
    def __init__(self, main):
        self.main = main
        self.gui = PRG_GUI()
        self.gui.lblCancel.setVisible(False)
        self.connections()

    def connections(self):
        self.gui.cmdCancel.clicked.connect(lambda: self.cancel())

    def cancel(self):
        self.gui.allow_cancel = True
        self.gui.cmdCancel.setDisabled(True)
        self.gui.lblCancel.setText("-1")

class MainUiFunc:
    def __init__(self):
        self.QGis_app = QApplication.instance()
        self.LUT = LUT(self)

        self.loadtxtfile = LoadTxtFile(self)

        self.select_wavelengths = Select_Wavelengths(self)

        self.prg_widget = PRG(self)

    def show(self):
        self.LUT.gui.show()

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    from enmapbox.testing import initQgisApplication
    app = initQgisApplication()
    m = MainUiFunc()
    m.show()
    sys.exit(app.exec_())


