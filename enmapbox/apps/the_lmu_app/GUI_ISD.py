# -*- coding: utf-8 -*-

import sys
import numpy as np
from sklearn.metrics import *
from math import sqrt
import pyqtgraph as pg

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import call_model as mod
from enmapbox.gui.applications import EnMAPBoxApplication
from Spec2Sensor_cl import Spec2Sensor

app = QApplication(sys.argv)
gui = uic.loadUi("GUI_ISD.ui")


class UiFunc:

    def __init__(self):
        self.initial_values()
        self.para_list = []
        self.update_slider_pos()
        self.update_lineEdit_pos()
        self.deactivate_sliders()
        self.para_init()
        self.select_model()
        self.mod_interactive()
        self.mod_exec()

    def initial_values(self):
        self.typeLIDF = 2
        self.lop = "prospectD"
        self.canopy_arch = "sail"
        self.plot_color = dict(zip(range(7), ["g", "r", "b", "y", "m", "c", "w"]))
        self.plot_count = 0
        self.current_slider = None
        self.data_mean = None

    def update_slider_pos(self):

        gui.N_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.N_Slide, gui.N_lineEdit))
        gui.Cab_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.Cab_Slide, gui.Cab_lineEdit))
        gui.Cw_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.Cw_Slide, gui.Cw_lineEdit))
        gui.Cm_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.Cm_Slide, gui.Cm_lineEdit))
        gui.Car_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.Car_Slide, gui.Car_lineEdit))
        gui.Canth_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.Canth_Slide, gui.Canth_lineEdit))
        gui.Cbrown_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.Cbrown_Slide, gui.Cbrown_lineEdit))
        gui.LAI_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.LAI_Slide, gui.LAI_lineEdit))
        gui.LIDFB_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.LIDFB_Slide, gui.LIDFB_lineEdit))
        gui.hspot_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.hspot_Slide, gui.hspot_lineEdit))
        gui.psoil_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.psoil_Slide, gui.psoil_lineEdit))
        gui.OZA_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.OZA_Slide, gui.OZA_lineEdit))
        gui.SZA_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.SZA_Slide, gui.SZA_lineEdit))
        gui.rAA_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.rAA_Slide, gui.rAA_lineEdit))
        gui.skyl_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.skyl_Slide, gui.skyl_lineEdit))
        gui.LAIu_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.LAIu_Slide, gui.LAIu_lineEdit))
        gui.SD_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.SD_Slide, gui.SD_lineEdit))
        gui.TreeH_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.TreeH_Slide, gui.TreeH_lineEdit))
        gui.CD_Slide.valueChanged.connect(lambda: self.any_slider_change(gui.CD_Slide, gui.CD_lineEdit))
    
    def update_lineEdit_pos(self):
        
        gui.N_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.N_lineEdit, gui.N_Slide))
        gui.Cab_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.Cab_lineEdit, gui.Cab_Slide))
        gui.Cw_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.Cw_lineEdit, gui.Cw_Slide))
        gui.Cm_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.Cm_lineEdit, gui.Cm_Slide))
        gui.Car_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.Car_lineEdit, gui.Car_Slide))
        gui.Canth_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.Canth_lineEdit, gui.Canth_Slide))
        gui.Cbrown_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.Cbrown_lineEdit, gui.Cbrown_Slide))
        gui.LAI_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.LAI_lineEdit, gui.LAI_Slide))
        gui.LIDFB_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.LIDFB_lineEdit, gui.LIDFB_Slide))
        gui.hspot_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.hspot_lineEdit, gui.hspot_Slide))
        gui.psoil_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.psoil_lineEdit, gui.psoil_Slide))
        gui.OZA_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.OZA_lineEdit, gui.OZA_Slide))
        gui.SZA_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.SZA_lineEdit, gui.SZA_Slide))
        gui.rAA_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.rAA_lineEdit, gui.rAA_Slide))
        gui.skyl_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.skyl_lineEdit, gui.skyl_Slide))
        gui.LAIu_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.LAIu_lineEdit, gui.LAIu_Slide))
        gui.SD_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.SD_lineEdit, gui.SD_Slide))
        gui.TreeH_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.TreeH_lineEdit, gui.TreeH_Slide))
        gui.CD_lineEdit.returnPressed.connect(lambda: self.any_lineEdit_change(gui.CD_lineEdit, gui.CD_Slide))

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
            QMessageBox.critical(gui, "Not a number", "'%s' is not a valid number" % textfeld.text())
            textfeld.setText(str(slider.value() / 10000.0))

    def select_s2s(self, sensor, trigger=True):
        self.sensor = sensor
        if not sensor == "default":
            s2s = Spec2Sensor(sensor=sensor, nodat=-999)
            s2s.init_sensor()
            self.wl = s2s.wl_sensor
            self.plot_count += 1
        else:
            self.wl = range(400, 2501)

        if trigger:
            self.mod_exec()

    def select_model(self, lop="prospectD", canopy_arch="sail"):
        self.lop = lop
        if canopy_arch == "None":
            self.canopy_arch = None
        else:
            self.canopy_arch = canopy_arch
        self.mod_exec()

    def select_LIDF(self, index):
        if index > 0:
            self.typeLIDF = 1 # Beta Distribution
            self.para_list[6] = index - 1
            gui.LIDFB_Slide.setDisabled(True)
            gui.LIDFB_lineEdit.setDisabled(True)
            self.mod_exec()
        else:
            self.typeLIDF = 2 # Ellipsoidal Distribution
            self.mod_exec(gui.LIDFB_Slide, item=6)
            gui.LIDFB_Slide.setDisabled(False)
            gui.LIDFB_lineEdit.setDisabled(False)

    def deactivate_sliders(self):
        gui.B_Prospect5b.toggled.connect(lambda: self.model_rb_click(gui.B_Prospect5b, gui.Canth_Slide, gui.Canth_lineEdit, gui.Canth_Text))

        gui.B_Prospect5.toggled.connect(lambda: self.model_rb_click(gui.B_Prospect5, gui.Canth_Slide, gui.Canth_lineEdit, gui.Canth_Text))
        gui.B_Prospect5.toggled.connect(lambda: self.model_rb_click(gui.B_Prospect5, gui.Cbrown_Slide, gui.Cbrown_lineEdit, gui.Cbrown_Text))

        gui.B_Prospect4.toggled.connect(lambda: self.model_rb_click(gui.B_Prospect4, gui.Canth_Slide, gui.Canth_lineEdit, gui.Canth_Text))
        gui.B_Prospect4.toggled.connect(lambda: self.model_rb_click(gui.B_Prospect4, gui.Cbrown_Slide, gui.Cbrown_lineEdit, gui.Cbrown_Text))
        gui.B_Prospect4.toggled.connect(lambda: self.model_rb_click(gui.B_Prospect4, gui.Car_Slide, gui.Car_lineEdit, gui.Car_Text))

    def model_rb_click(self, rbutton, slider, textfeld, text):
        if rbutton.isChecked():
            slider.setDisabled(True)
            textfeld.setDisabled(True)
            text.setDisabled(True)
        else:
            slider.setDisabled(False)
            textfeld.setDisabled(False)
            text.setDisabled(False)

    def para_init(self):
        self.select_s2s(sensor="default", trigger=False)
        self.para_list.append(float(gui.N_lineEdit.text())) #0
        self.para_list.append(float(gui.Cab_lineEdit.text())) #1
        self.para_list.append(float(gui.Cw_lineEdit.text())) #2
        self.para_list.append(float(gui.Cm_lineEdit.text())) #3
        self.para_list.append(float(gui.LAI_lineEdit.text())) #4
        self.para_list.append(float(2))  # 5
        self.para_list.append(float(gui.LIDFB_lineEdit.text())) #6
        self.para_list.append(float(gui.hspot_lineEdit.text())) #7
        self.para_list.append(float(gui.psoil_lineEdit.text())) #8
        self.para_list.append(float(gui.SZA_lineEdit.text())) #9
        self.para_list.append(float(gui.OZA_lineEdit.text())) #10
        self.para_list.append(float(gui.rAA_lineEdit.text())) #11
        self.para_list.append(float(gui.Car_lineEdit.text())) #12
        self.para_list.append(float(gui.Canth_lineEdit.text())) #13
        self.para_list.append(float(gui.Cbrown_lineEdit.text())) #14
        self.para_list.append(float(gui.skyl_lineEdit.text())) #15
        self.typeLIDF = 2

    def mod_interactive(self):
        gui.N_Slide.valueChanged.connect(lambda: self.mod_exec(slider=gui.N_Slide, item=0))
        gui.Cab_Slide.valueChanged.connect(lambda: self.mod_exec(slider=gui.Cab_Slide, item=1))
        gui.Cw_Slide.valueChanged.connect(lambda: self.mod_exec(gui.Cw_Slide, item=2))
        gui.Cm_Slide.valueChanged.connect(lambda: self.mod_exec(gui.Cm_Slide, item=3))
        gui.LAI_Slide.valueChanged.connect(lambda: self.mod_exec(gui.LAI_Slide, item=4))
        gui.LIDFB_Slide.valueChanged.connect(lambda: self.mod_exec(gui.LIDFB_Slide, item=6))
        gui.hspot_Slide.valueChanged.connect(lambda: self.mod_exec(gui.hspot_Slide, item=7))
        gui.psoil_Slide.valueChanged.connect(lambda: self.mod_exec(gui.psoil_Slide, item=8))
        gui.SZA_Slide.valueChanged.connect(lambda: self.mod_exec(gui.SZA_Slide, item=9))
        gui.OZA_Slide.valueChanged.connect(lambda: self.mod_exec(gui.OZA_Slide, item=10))
        gui.rAA_Slide.valueChanged.connect(lambda: self.mod_exec(gui.rAA_Slide, item=11))
        gui.Car_Slide.valueChanged.connect(lambda: self.mod_exec(gui.Car_Slide, item=12))
        gui.Canth_Slide.valueChanged.connect(lambda: self.mod_exec(gui.Canth_Slide, item=13))
        gui.Cbrown_Slide.valueChanged.connect(lambda: self.mod_exec(gui.Cbrown_Slide, item=14))
        gui.skyl_Slide.valueChanged.connect(lambda: self.mod_exec(gui.skyl_Slide, item=15))
        gui.LAIu_Slide.valueChanged.connect(lambda: self.mod_exec(gui.LAIu_Slide, item=16))
        gui.SD_Slide.valueChanged.connect(lambda: self.mod_exec(gui.SD_Slide, item=17))
        gui.TreeH_Slide.valueChanged.connect(lambda: self.mod_exec(gui.TreeH_Slide, item=18))
        gui.CD_Slide.valueChanged.connect(lambda: self.mod_exec(gui.CD_Slide, item=19))

        gui.SType_None_B.clicked.connect(lambda: self.select_s2s(sensor="default"))
        gui.SType_Sentinel_B.clicked.connect(lambda: self.select_s2s(sensor="Sentinel2"))
        gui.SType_Landsat_B.clicked.connect(lambda: self.select_s2s(sensor="Landsat8"))
        gui.SType_Enmap_B.clicked.connect(lambda: self.select_s2s(sensor="EnMAP"))

        gui.B_Prospect4.clicked.connect(lambda: self.select_model(lop="prospect4"))
        gui.B_Prospect5.clicked.connect(lambda: self.select_model(lop="prospect5"))
        gui.B_Prospect5b.clicked.connect(lambda: self.select_model(lop="prospect5B"))
        gui.B_ProspectD.clicked.connect(lambda: self.select_model(lop="prospectD"))

        gui.B_LeafModelOnly.clicked.connect(lambda: self.select_model(canopy_arch="None"))
        gui.B_4Sail.clicked.connect(lambda: self.select_model(canopy_arch="sail"))
        gui.B_Inform.clicked.connect(lambda: self.select_model(canopy_arch="inform"))

        gui.LIDF_combobox.currentIndexChanged.connect(self.select_LIDF)

        gui.pushClearPlot.clicked.connect(self.clearPlot)
        gui.Push_LoadInSitu.clicked.connect(self.open_file)
        gui.Push_Exit.clicked.connect(self.exit_GUI)
        gui.Push_ResetInSitu.clicked.connect(self.resetInSitu)

    def exit_GUI(self):
        QCoreApplication.instance().quit()

    def resetInSitu(self):
        self.data_mean = None
        self.mod_exec()

    def plot_own_spec(self):
        if self.data_mean is not None:
            self.plot = gui.graphicsView.plot(range(400, 2501), self.data_mean)

    def open_file(self):
        # Dialog to open own spectrum, .asc exported by ViewSpecPro as single file
        filename = str(QFileDialog.getOpenFileName(caption='Select Spectrum File'))
        self.data = np.genfromtxt(filename, delimiter="\t", skip_header=True)
        ## "\OSGEO4~1\apps\Python27\lib\site-packages\numpy\lib\npyio.py" changed endswith to endsWith to work:
        self.data = np.delete(self.data, 0, axis=1)

        self.data_mean = np.mean(self.data, axis=1)
        self.data_mean[1010:1071] = np.nan  # set atmospheric water vapour absorption bands to NaN
        self.data_mean[1440:1591] = np.nan
        self.data_mean[2050:2151] = np.nan
        self.data_mean = self.data_mean[50:]
        self.mod_exec()

    def clearPlot(self):
        gui.graphicsView.clear()
        self.plot_count = 0

    def mod_exec(self, slider=None, item=None):

        if slider is not None and item is not None:
            self.para_list[item] = slider.value() / 10000.0 # update para_list

        mod_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=-999, int_boost=1.0, s2s=self.sensor)
        myResult = mod_I.initialize_single(tts=self.para_list[9], tto=self.para_list[10], psi=self.para_list[11],
                                           N=self.para_list[0], cab=self.para_list[1], cw=self.para_list[2],
                                           cm=self.para_list[3], LAI=self.para_list[4], LIDF=self.para_list[6],
                                           typeLIDF=self.typeLIDF, hspot=self.para_list[7], psoil=self.para_list[8],
                                           car=self.para_list[12],
                                           cbrown=self.para_list[14], anth=self.para_list[13])




        if not gui.CheckPlotAcc.isChecked():
            self.clearPlot()
            self.plot = gui.graphicsView.plot(self.wl, myResult, pen="g")
            self.plot_own_spec()
            gui.graphicsView.setYRange(0, 0.6, padding=0)
            gui.graphicsView.setLabel('left', text="Reflectance [%]")
            gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")
        else:
            self.plot = gui.graphicsView.plot(self.wl, myResult,
                                              pen=self.plot_color[self.plot_count % 7])
            self.plot_own_spec()
            gui.graphicsView.setYRange(0, 0.6, padding=0)
            gui.graphicsView.setLabel('left', text="Reflectance [%]")
            gui.graphicsView.setLabel('bottom', text="Wavelength [nm]")

        if self.data_mean is not None and gui.SType_None_B.isChecked():
            mae = np.nansum(abs(myResult - self.data_mean)) / len(myResult)
            rmse = np.sqrt(np.nanmean((myResult - self.data_mean)))
            nse = 1 - ((np.nansum((myResult - self.data_mean))) /
                       (np.nansum(self.data_mean - (np.nanmean(self.data_mean))**2)))
            r_squared = ((np.nansum((self.data_mean - np.nanmean(self.data_mean)) * (myResult - np.nanmean(myResult)))) /
                         ((np.sqrt(np.nansum((self.data_mean - np.nanmean(self.data_mean))**2))) *
                          (np.sqrt(np.nansum((myResult - np.nanmean(myResult))**2)))))**2


            errors = pg.TextItem("RMSE: " + str(round(rmse, 6)) + "\nMAE: " + str(round(mae, 6)) + "\nmNSE: " +
                                 str(round(nse, 6)) + '\n' + u'R²: ' + str(round(r_squared, 6)),
                                 (100, 200, 255),
                                 border="w", anchor=(1, 0))
            errors.setPos(2500, 0.55)
            gui.graphicsView.addItem(errors)


if __name__ == '__main__':

    myUI = UiFunc()
    gui.show()
    sys.exit(app.exec_())


