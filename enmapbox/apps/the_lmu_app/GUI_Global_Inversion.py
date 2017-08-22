# -*- coding: utf-8 -*-

import sys, os
import numpy as np
from qgis.gui import *
#ensure to call QGIS before PyQtGraph
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import Inverse_mode_cl as inverse
from enmapbox.gui.applications import EnMAPBoxApplication
from Spec2Sensor_cl import Spec2Sensor

pathUI = os.path.join(os.path.dirname(__file__),'GUI_Global_Inversion.ui')

from enmapbox.gui.utils import loadUIFormClass

class GUI_Global_Inversion(QDialog, loadUIFormClass(pathUI)):
    
    def __init__(self, parent=None):
        super(GUI_Global_Inversion, self).__init__(parent)
        self.setupUi(self)    

class UiFunc:

    def __init__(self):
        
        self.gui = GUI_Global_Inversion()
        self.initial_values()
        self.connections()

    def initial_values(self):
        self.ctype = 0
        self.nbfits = 0
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
        self.conversion_factor = None

        self.para_flat = [item for sublist in self.para_list for item in sublist]
        self.npara_flat = len(self.para_flat)

        self.LUT_path = None
        self.sensor = 1

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
        self.gui.radGeoFromFile.clicked.connect(lambda: self.select_geo(mode="file"))
        self.gui.radGeoFix.clicked.connect(lambda: self.select_geo(mode="fix"))
        self.gui.radGeoOff.clicked.connect(lambda: self.select_geo(mode="off"))

        # Artificial Noise
        self.gui.radNoiseOff.clicked.connect(lambda: self.select_noise(mode="off"))
        self.gui.radNoiseAdd.clicked.connect(lambda: self.select_noise(mode="add"))
        self.gui.radNoiseMulti.clicked.connect(lambda: self.select_noise(mode="multi"))
        self.gui.radNoiseInvMulti.clicked.connect(lambda: self.select_noise(mode="inv_multi"))

        # Cost Function
        self.gui.radRMSE.clicked.connect(lambda: self.select_costfun(mode="RMSE"))
        self.gui.radMAE.clicked.connect(lambda: self.select_costfun(mode="MAE"))
        self.gui.radRMSE.clicked.connect(lambda: self.select_costfun(mode="nMSE"))
        self.gui.radRel.clicked.connect(lambda: self.select_costfun(mode="rel"))
        self.gui.radAbs.clicked.connect(lambda: self.select_costfun(mode="rel"))

        # Execute
        self.gui.cmdRun.clicked.connect(lambda: self.run_inversion())
        self.gui.cmdClose.clicked.connect(lambda: self.gui.accept)

    def open_file(self, mode):
        if mode=="image":
            result = str(QFileDialog.getOpenFileName(caption='Select Input Image'))
            if result:
                self.gui.txtInputImage.setText(result)
                self.image = self.gui.txtInputImage.text().replace("\\", "/")
        elif mode=="lut":
            result = str(QFileDialog.getOpenFileName(caption='Select LUT meta-file'))
            if result:
                self.gui.txtInputLUT.setText(result)
                self.LUT_path = self.gui.txtInputLUT.text().replace("\\", "/")
        elif mode=="output":
            result = str(QFileDialog.getExistingDirectory(caption='Select Path for Output storage'))
            if result:
                self.gui.txtOutputImage.setText(result)
                self.out_path = self.gui.txtInputLUT.text().replace("\\", "/")
                if not self.out_path[-1] == "/": self.out_path += "/"

    def select_outputmode(self, mode):
        self.out_mode = mode

    def select_sensor(self, sensor):
        self.sensor = sensor

    def

    def txt_enables(self, para, mode):

        if mode=="fix":
            self.dict_objects[para][4].setEnabled(True)
            for i in xrange(5, 12):
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")

        elif mode=="gauss":
            for i in [4, 9, 10, 11]:
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")
            for i in xrange(5, 9):
                self.dict_objects[para][i].setEnabled(True)

        elif mode=="uni":
            for i in [4, 7, 8, 9, 10, 11]:
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")
            self.dict_objects[para][5].setEnabled(True)
            self.dict_objects[para][6].setEnabled(True)

        elif mode=="log":
            for i in xrange(4, 9):
                self.dict_objects[para][i].setEnabled(False)
                self.dict_objects[para][i].setText("")
            for i in [9, 10, 11]:
                self.dict_objects[para][i].setEnabled(True)

        if para in self.dict_checks:
            self.dict_checks[para] = mode

    def set_boundaries(self):
        self.dict_boundaries = {"N": [1.0, 3.0],
                            "chl": [0.0, 100.0],
                             "cw": [0.001, 0.7],
                             "cm": [0.001, 0.02],
                             "car": [0.0, 30.,0],
                             "cbr": [0.0, 1.0],
                             "canth": [0.0, 10.0],
                             "lai": [0.01, 10.0],
                             "alia": [0.0, 90.0],
                             "hspot": [0.0, 1.0],
                             "oza": [0.0, 80.0],
                             "sza": [0.0, 80.0],
                             "raa": [0.0, 180.0],
                             "psoil": [0.0, 1.0],
                             "laiu": [0.0, 100.0], # forest parameters temporary!
                             "sd": [0.0, 100.0],
                             "h": [0.0, 100.0],
                             "cd": [0.0, 100.0]}

    def select_s2s(self, sensor):
        self.sensor = sensor
        if not sensor == "default":
            s2s = Spec2Sensor(sensor=sensor, nodat=-999)
            s2s.init_sensor()
            self.wl = s2s.wl_sensor
        else:
            self.wl = range(400, 2501)

    def select_model(self, lop="prospectD", canopy_arch="sail"):
        self.lop = lop
        if canopy_arch == "None":
            self.canopy_arch = None
            self.gui.grp_canopy.setDisabled(True)
        else:
            self.canopy_arch = canopy_arch
            self.gui.grp_canopy.setDisabled(False)

        if lop=="prospectD":
            for para in self.para_list[0]:
                for object in xrange(12):
                    self.dict_objects[para][object].setDisabled(False)
            self.txt_enables(para="car", mode=self.dict_checks["car"])
            self.txt_enables(para="cbr", mode=self.dict_checks["cbr"])
            self.txt_enables(para="canth", mode=self.dict_checks["canth"])


        elif lop == "prospect5B":
            for para in self.para_list[0]:
                for object in xrange(12):
                    self.dict_objects[para][object].setDisabled(False)
            for object in xrange(12):
                self.dict_objects["canth"][object].setDisabled(True)
            self.txt_enables(para="car", mode=self.dict_checks["car"])
            self.txt_enables(para="cbr", mode=self.dict_checks["cbr"])

        elif lop == "prospect5":
            for para in self.para_list[0]:
                for object in xrange(12):
                    self.dict_objects[para][object].setDisabled(False)
                for object in xrange(12):
                    self.dict_objects["canth"][object].setDisabled(True)
                    self.dict_objects["cbr"][object].setDisabled(True)
            self.txt_enables(para="car", mode=self.dict_checks["car"])

        elif lop == "prospect4":
            for para in self.para_list[0]:
                for object in xrange(12):
                    self.dict_objects[para][object].setDisabled(False)
                for object in xrange(12):
                    self.dict_objects["canth"][object].setDisabled(True)
                    self.dict_objects["cbr"][object].setDisabled(True)
                    self.dict_objects["car"][object].setDisabled(True)

    def get_folder(self):
        path = str(QFileDialog.getExistingDirectory(caption='Select Directory for LUT'))

        if path:
            self.gui.txtPath.setText(path)
            self.path = self.gui.txtPath.text().replace("\\", "/")
            if not self.path[-1] == "/":
                self.path += "/"
            print self.path

    def test_LUT(self):
        model_I = mod.Init_Model(lop="prospectD", canopy_arch="sail", nodat=-999,
                                 int_boost=1000, s2s="default")
        model_I.initialize_multiple(LUT_dir="D:/ECST_III/Processor/VegProc/results_test/", LUT_name="Test1", ns=2000,
                                    tts=[20.0, 50.0, 4.0],
                                    tto=[0.0], psi=[45.0], N=[1.0, 2.5],
                                    cab=[0.0, 80.0, 45.0, 5.0], cw=[0.002, 0.02], cm=[0.018],
                                    LAI=[1.0, 8.0], LIDF=[20.0, 80.0, 40.0, 10.0], typeLIDF=[2],
                                    hspot=[0.1], psoil=[0.0, 1.0], car=[0.0, 15.0],
                                    cbrown=[0.0, 1.0], anth=[5.0])

    def run_LUT(self):
        self.get_inputs()
        if not self.check_inputs(): return

        model_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=self.nodat,
                                 int_boost=self.intboost, s2s=self.sensor)
        model_I.initialize_multiple(LUT_dir=self.path, LUT_name=self.LUT_name, ns=self.ns, tts=self.dict_vals['sza'],
                                    tto=self.dict_vals['oza'], psi=self.dict_vals['raa'], N=self.dict_vals['N'],
                                    cab=self.dict_vals['chl'], cw=self.dict_vals['cw'], cm=self.dict_vals['cm'],
                                    LAI=self.dict_vals['lai'], LIDF=self.dict_vals['alia'], typeLIDF=[2],
                                    hspot=self.dict_vals['hspot'], psoil=self.dict_vals['psoil'], car=self.dict_vals['car'],
                                    cbrown=self.dict_vals['cbr'], anth=self.dict_vals['canth'])

    def get_inputs(self):
        self.dict_vals = dict(zip(self.para_flat, ([] for i in xrange(self.npara_flat))))
        for para in self.dict_objects:
            for object in xrange(4, 12):
                if not self.dict_objects[para][object].text() == "":
                    try:
                        self.dict_vals[para].append(float(self.dict_objects[para][object].text()))
                    except ValueError:
                        QMessageBox.critical(self.gui, "Not a number", "'%s' is not a valid number" % self.dict_objects[para][object].text())
                        self.dict_vals = dict(zip(self.para_flat, ([] for i in xrange(self.npara_flat))))

        self.LUT_name = self.gui.txtLUTname.text()
        self.ns = int(self.gui.spinNS.value())
        self.intboost = int(self.gui.spinIntBoost.value())
        self.nodat = int(self.gui.spinNoData.value())

    def check_inputs(self):

        for i, key in enumerate(self.para_list[0]):
            if len(self.dict_vals[self.para_list[0][i]]) > 3:
                if self.dict_vals[self.para_list[0][i]][2] > self.dict_vals[self.para_list[0][i]][1] or \
                                self.dict_vals[self.para_list[0][i]][2] < self.dict_vals[self.para_list[0][i]][0]:
                    self.abort(message='Parameter %s: mean value must lie between min and max' % self.para_list[0][i])
                    return False
                elif self.dict_vals[self.para_list[0][i]][0] < self.dict_boundaries[key][0] or \
                                self.dict_vals[self.para_list[0][i]][1] > self.dict_boundaries[key][1]:
                    self.abort(message='Parameter %s: min / max out of allowed range!' % self.para_list[0][i])
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
                if len(self.dict_vals[self.para_list[1][i]]) > 3:
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

        if self.lop == "prospectD":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in xrange(len(self.para_list[0]))):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False
        elif self.lop == "prospect5B":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in xrange(len(self.para_list[0])-1)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False
        elif self.lop == "prospect5":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in xrange(len(self.para_list[0])-2)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False
        elif self.lop == "prospect4":
            if any(len(self.dict_vals[self.para_list[0][i]]) < 1 for i in xrange(len(self.para_list[0])-3)):
                self.abort(message='Leaf Optical Properties parameter(s) missing')
                return False

        if self.canopy_arch == "sail":
            if any(len(self.dict_vals[self.para_list[1][i]]) < 1 for i in xrange(len(self.para_list[1]))):
                self.abort(message='Canopy Architecture parameter(s) missing')
                return False

        if not os.path.isdir(self.gui.txtPath.text()):
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
            if len(self.dict_vals[para]) == 3 and any(self.dict_objects[para][i].isEnabled() for i in xrange(4)):
                self.nlut_total *= self.dict_vals[para][2]
        # print "total size of LUT: ", self.nlut_total
        self.gui.lcdNumber.display(self.nlut_total)

        # if self.speed is None: self.speedtest()
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

        self.gui.lcdSpeed.display(self.speed)

    def speedtest(self):

        model_I = mod.Init_Model(lop=self.lop, canopy_arch=self.canopy_arch, nodat=self.nodat,
                                 int_boost=self.intboost, s2s=self.sensor)
        time50x = model_I.initialize_multiple(LUT_dir=None, LUT_name=None, ns=100, tts=[20.0, 60.0], tto=[0.0, 40.0],
                                    psi=[0.0, 180.0], N=[1.1, 2.5], cab=[0.0, 80.0], cw=[0.0002, 0.02],
                                    cm=[0.0001, 0.005], LAI=[0.5, 8.0], LIDF=[10.0, 80.0], typeLIDF=[2],
                                    hspot=[0.1], psoil=[0.5], car=[0.0, 12.0], cbrown=[0.0, 1.0], anth=[0.0, 10.0],
                                    testmode=1)

        return time50x

    def abort(self, message):
        QMessageBox.critical(self.gui, "Parameter(s) missing!", message)

if __name__ == '__main__':
    from enmapbox.gui.sandbox import initQgisEnvironment
    app = initQgisEnvironment()
    myUI = UiFunc()
    myUI.gui.show()
    sys.exit(app.exec_())


