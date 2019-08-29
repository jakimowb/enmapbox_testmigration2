# -*- coding: utf-8 -*-
from hubflow.core import *
import numpy as np
import numpy.ma as ma
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import Qt
import pyqtgraph as pg
from scipy.stats import mode

import sys, os
from scipy.interpolate import *
from scipy.signal import savgol_filter

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_iREIP.ui')
pathUI2 = os.path.join(os.path.dirname(__file__), 'GUI_Nodat.ui')
pathUI_prg = os.path.join(os.path.dirname(__file__), 'GUI_ProgressBar.ui')

from enmapbox.gui.utils import loadUIFormClass


class iREIP_GUI(QDialog, loadUIFormClass(pathUI)):
    def __init__(self, parent=None):
        super(iREIP_GUI, self).__init__(parent)
        self.setupUi(self)
        QApplication.instance().installEventFilter(self)

        self.rangeView.setBackground(QColor('black'))
        self.firstDerivView.setBackground(QColor('black'))
        self.secondDerivView.setBackground(QColor('black'))


class Nodat_GUI(QDialog, loadUIFormClass(pathUI2)):
    def __init__(self, parent=None):
        super(Nodat_GUI, self).__init__(parent)
        self.setupUi(self)


class PRG_GUI(QDialog, loadUIFormClass(pathUI_prg)):
    def __init__(self, parent=None):
        super(PRG_GUI, self).__init__(parent)
        self.setupUi(self)
        self.allow_cancel = False

    def closeEvent(self, event):
        if self.allow_cancel:
            event.accept()
        else:
            event.ignore()


class iREIP:
    def __init__(self, main):
        self.main = main
        self.gui = iREIP_GUI()
        self.initial_values()
        self.connections()
        self.init_plot()

    def initial_values(self):
        self.image = None
        self.out_path = None
        self.limits = [680, 750]
        self.neighbors = 13
        self.max_ndvi_pos = None
        self.nodat = [-999] * 2
        self.division_factor = 1.0
        self.calc_deriv_flag = [False, False]  # First, Second Derivative [First, Second]

    def connections(self):
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdOutputImage.clicked.connect(lambda: self.open_file(mode="output"))

        self.gui.lowWaveEdit.returnPressed.connect(
            lambda: self.limits_changed(self.gui.lowWaveEdit))
        self.gui.upWaveEdit.returnPressed.connect(
            lambda: self.limits_changed(self.gui.upWaveEdit))
        self.gui.neighborEdit.returnPressed.connect(lambda: self.neighbors_changed())

        self.gui.spinDivisionFactor.returnPressed.connect(lambda: self.division_factor_changed())
        self.gui.cmdFindNDVI.clicked.connect(lambda: self.init_ireip())

        self.gui.checkFirstDeriv.stateChanged.connect(lambda: self.calc_deriv())
        self.gui.checkSecondDeriv.stateChanged.connect(lambda: self.calc_deriv())

        self.gui.pushFullRange.clicked.connect(lambda: self.plot_change(mode="full"))
        self.gui.pushSetRange.clicked.connect(lambda: self.plot_change(mode="zoom"))

        self.gui.pushRun.clicked.connect(lambda: self.init_run())
        self.gui.pushClose.clicked.connect(lambda: self.gui.close())

    def open_file(self, mode):
        if mode == "image":
            bsq_input = QFileDialog.getOpenFileName(caption='Specify Output File',
                                                    filter="ENVI Image (*.bsq)")[0]
            if not bsq_input:
                return
            if self.image is not None:
                self.reset()
            self.image = bsq_input
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
                self.gui.lblInputImage.setText(bsq_input)
                self.gui.lblNodatImage.setText(str(meta[0]))
                self.gui.txtNodatOutput.setText(str(meta[0]))
                self.nodat[0] = meta[0]
        elif mode == "output":
            # result, _filter = QFileDialog.getSaveFileName(None, 'Specify Output File', '.', "ENVI Image(*.bsq)")
            result = \
            QFileDialog.getSaveFileName(caption='Specify Output File',
                                        filter="ENVI Image (*.bsq)")[0]
            self.out_path = result
            self.out_path = self.out_path.replace("\\", "/")
            self.gui.txtOutputImage.setText(result)

    def get_image_meta(self, image, image_type):
        dataset = openRasterDataset(image)
        if dataset is None:
            raise ValueError(
                '%s could not be read. Please make sure it is a valid ENVI image' % image_type)
        else:
            metadict = dataset.metadataDict()

            nrows = int(metadict['ENVI']['lines'])
            ncols = int(metadict['ENVI']['samples'])
            nbands = int(metadict['ENVI']['bands'])
            if nbands < 2:
                raise ValueError("Input is not a multi-band image")
            try:
                nodata = int(metadict['ENVI']['data ignore value'])
                return nodata, nbands, nrows, ncols
            except:
                self.main.nodat_widget.init(image_type=image_type, image=image)
                self.main.nodat_widget.gui.setModal(True)  # parent window is blocked
                self.main.nodat_widget.gui.exec_()  # unlike .show(), .exec_() waits with execution of the code, until the app is closed
                return self.main.nodat_widget.nodat, nbands, nrows, ncols

    def reset(self):
        self.max_ndvi_pos = None
        self.init_plot()

    def limits_changed(self, textfeld):
        if self.image is None:
            QMessageBox.warning(self.gui, "No image loaded",
                                "Please load an image, press 'Find' and adjust boundaries")
        else:
            if textfeld == self.gui.lowWaveEdit:
                try:
                    self.limits[0] = int(str(textfeld.text()))
                except ValueError:
                    QMessageBox.critical(self.gui, "Not a number",
                                         "'%s' is not a valid number" % textfeld.text())
                    textfeld.setText(str(self.limits[0]))
            elif textfeld == self.gui.upWaveEdit:
                try:
                    self.limits[1] = int(str(textfeld.text()))
                except ValueError:
                    QMessageBox.critical(self.gui, "Not a number",
                                         "'%s' is not a valid number" % textfeld.text())
                    textfeld.setText(str(self.limits[1]))
                self.limits[1] = int(str(textfeld.text()))
            if not self.limits[1] > self.limits[0]:
                ValueError(QMessageBox.critical(self.gui, "Error",
                                                "Lower boundary not smaller than upper"))

                self.gui.lowWaveEdit.setText(str(self.limits[0]))
                self.gui.upWaveEdit.setText(str(self.limits[0] + 1))

            if self.max_ndvi_pos == None:
                self.init_plot()
            else:
                self.plot_example(self.max_ndvi_pos)

    def neighbors_changed(self):
        if self.image is None:
            QMessageBox.warning(self.gui, "No image loaded",
                                "Please load an image, press 'Find' and adjust boundaries")
        else:
            try:
                self.neighbors = int(str(self.gui.neighborEdit.text()))
            except ValueError:
                QMessageBox.critical(self.gui, "Not a number",
                                     "'%s' is not a valid number" % self.gui.neighborEdit.text())
                self.gui.neighborEdit.setText(str(self.neighbors))
            if (self.neighbors % 2) == 0:
                QMessageBox.warning(self.gui, "Savitzky-Golay Error", "Neighbor value must be odd")
                self.neighbors += 1
                self.gui.neighborEdit.setText(str(self.neighbors))
            if not self.neighbors > 2:
                QMessageBox.warning(self.gui, "Savitzky-Golay Error", "Window length must be > 2")
                self.neighbors = 3
                self.gui.neighborEdit.setText(str(self.neighbors))
            self.init_ireip()
            self.plot_example(self.max_ndvi_pos)

    def division_factor_changed(self):
        if self.image is None:
            QMessageBox.warning(self.gui, "No image loaded",
                                "Please load an image, press 'Find' and adjust boundaries")
        else:
            try:
                self.division_factor = int(str(self.gui.spinDivisionFactor.text()))
                self.gui.spinDivisionFactor.setText(str(self.division_factor))
            except ValueError:
                QMessageBox.critical(self.gui, "Not a number",
                                     "'%s' is not a valid number" % self.gui.neighborEdit.text())
        self.init_ireip()
        self.plot_example(self.max_ndvi_pos)

    def calc_deriv(self):
        if self.gui.checkFirstDeriv.isChecked():
            self.calc_deriv_flag[0] = True
        else:
            self.calc_deriv_flag[0] = False
        if self.gui.checkSecondDeriv.isChecked():
            self.calc_deriv_flag[1] = True
        else:
            self.calc_deriv_flag[1] = False

    def init_plot(self):
        labelStyle = {'color': '#FFF', 'font-size': '12px'}

        self.gui.lblPixelLocation.setText("")

        self.gui.rangeView.plot(clear=True)
        self.gui.rangeView.setLabel(axis='left', text="Reflectance [%]", **labelStyle)
        self.gui.rangeView.setLabel('bottom', text="Wavelength [nm]", **labelStyle)

        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        self.gui.rangeView.setXRange(350, 2500, padding=0)

        self.gui.firstDerivView.plot(clear=True)
        self.gui.firstDerivView.setLabel('left', text="[-]", **labelStyle)
        self.gui.firstDerivView.setLabel('bottom', text="Wavelength [nm]", **labelStyle)
        self.gui.firstDerivView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.firstDerivView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        self.gui.firstDerivView.setXRange(350, 2500, padding=0)

        self.gui.secondDerivView.plot(clear=True)
        self.gui.secondDerivView.setLabel('left', text="[-]", **labelStyle)
        self.gui.secondDerivView.setLabel('bottom', text="Wavelength [nm]", **labelStyle)
        self.gui.secondDerivView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.secondDerivView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        self.gui.secondDerivView.setXRange(350, 2500, padding=0)

    def plot_example(self, max_ndvi_pos):
        self.gui.lblPixelLocation.setText("Image pixel: row: %s | col: %s" % (
            str(max_ndvi_pos[1]), str(max_ndvi_pos[2])))
        self.gui.lblPixelLocation.setStyleSheet('color: green')
        plot_spec = self.core.in_raster[:, max_ndvi_pos[1], max_ndvi_pos[2]]

        if len(self.core.valid_wl) > 2000:
            plot_spec = self.core.interp_watervapor_1d(plot_spec)

        smooth_array, first_deriv, second_deriv, self.reip = self.core.derivate_1d(
            plot_spec)

        self.gui.rangeView.plot(self.core.wl, smooth_array, clear=True, pen="g", fillLevel=0,
                                fillBrush=(255, 255, 255, 30),
                                name='maxNDVIspec')
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))

        self.gui.firstDerivView.plot(self.core.wl, first_deriv, clear=True, pen="g", fillLevel=0,
                              fillBrush=(255, 255, 255, 30),
                              name='first_deriv')
        self.gui.firstDerivView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.firstDerivView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))

        self.gui.secondDerivView.plot(self.core.wl, second_deriv, clear=True, pen="g", fillLevel=0,
                              fillBrush=(255, 255, 255, 30),
                              name='second_deriv')
        self.gui.secondDerivView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.secondDerivView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        if self.reip is not None:
            self.gui.secondDerivView.addItem(
                pg.InfiniteLine(self.reip,
                                pen=pg.mkPen(color=(200, 200, 255), style=Qt.DotLine)))

            self.gui.ipLabel.setText("Inflection point found at")
            self.gui.ipLabel.setStyleSheet('color: green')
            self.gui.ipPosLabel.setText("{:6.2f}".format(self.reip) + " nm")
            self.gui.ipPosLabel.setStyleSheet('color: green')
        else:
            self.gui.ipLabel.setText("No unique inflection point found")
            self.gui.ipLabel.setStyleSheet('color: red')
            self.gui.ipPosLabel.setText("")

    def plot_change(self, mode):
        if mode == 'zoom':
            low, high = self.limits
            self.gui.rangeView.setXRange(low, high)
            self.gui.firstDerivView.setXRange(low, high)
            self.gui.secondDerivView.setXRange(low, high)

        if mode == 'full':
            low, high = [350, 2500]
            self.gui.rangeView.setXRange(low, high)
            self.gui.firstDerivView.setXRange(low, high)
            self.gui.secondDerivView.setXRange(low, high)

    def init_ireip(self):
        if self.image is None:
            QMessageBox.critical(self.gui, "No image selected",
                                 "Please select an image to continue!")
            return

        if self.max_ndvi_pos is None:
            # show progressbar - window
            self.main.prg_widget.gui.lblCaption_l.setText("Searching NDVI > 0.85")
            self.main.prg_widget.gui.lblCaption_r.setText(
                "Reading Input Image...this may take several minutes")
            self.main.prg_widget.gui.prgBar.setValue(0)
            self.main.prg_widget.gui.setModal(True)
            self.main.prg_widget.gui.show()
            self.main.QGis_app.processEvents()

        try:
            self.division_factor = int(str(self.gui.spinDivisionFactor.text()))
            self.core = iREIP_core(nodat_val=self.nodat, division_factor=self.division_factor)

            self.core.initialize_iREIP(input=self.image, output=None,
                                       limits=self.limits,
                                       deriv=self.calc_deriv_flag,
                                       neighbors=self.neighbors, mode='find')
        except MemoryError:
            QMessageBox.critical(self.gui, 'error', "File too large to read. More RAM needed")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
        except ValueError as e:
            QMessageBox.critical(self.gui, 'error', str(e))
            self.main.prg_widget.gui.allow_cancel = True  # The window may be cancelled
            self.main.prg_widget.gui.close()
            return

        if self.max_ndvi_pos is None:
            self.max_ndvi_pos = self.core.findHighestNDVIindex(prg_widget=self.main.prg_widget,
                                                               QGis_app=self.main.QGis_app)

            # QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
        self.plot_example(self.max_ndvi_pos)
        return

    def init_run(self):
        if self.image is None:
            QMessageBox.critical(self.gui, "No image loaded", "Please load an image to continue!")
            return
        elif self.out_path is None:
            QMessageBox.critical(self.gui, "No output file selected",
                                 "Please select an output location for your image!")
            return
        elif self.gui.txtNodatOutput.text() == "":
            QMessageBox.warning(self.gui, "No Data Value", "Please specify No Data Value!")
            # QMessageBox.critical(self.gui, "No Data Value", "Please specify No Data Value!")
            return
        else:
            try:
                self.nodat[1] = int(self.gui.txtNodatOutput.text())
            except:
                QMessageBox.critical(self.gui, "Error",
                                     "'%s' is not a valid  No Data Value!" % self.gui.txtNodatOutput.text())
                return
        try:
            self.division_factor = float(self.gui.spinDivisionFactor.text())
        except:
            QMessageBox.critical(self.gui, "Error",
                                 "'%s' is not a valid division factor!" % self.gui.spinDivisionFactor.text())
            return

        # show progressbar - window
        self.main.prg_widget.gui.lblCaption_l.setText("Searching REIP position")
        self.main.prg_widget.gui.lblCaption_r.setText(
            "Reading Input Image...this may take several minutes")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()

        try:
            iREIP = iREIP_core(nodat_val=self.nodat, division_factor=self.division_factor)
            iREIP.initialize_iREIP(input=self.image, output=self.out_path,
                                   limits=self.limits,
                                   deriv=self.calc_deriv_flag, neighbors=self.neighbors, mode='run')
        except MemoryError:
            QMessageBox.critical(self.gui, 'error', "File too large to read")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
        except ValueError as e:
            QMessageBox.critical(self.gui, 'error', str(e))
            self.main.prg_widget.gui.allow_cancel = True  # The window may be cancelled
            self.main.prg_widget.gui.close()
            return

        # try:  # give it a shot

        result, first_deriv, second_deriv = iREIP.execute_iREIP(prg_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)
        # except:
        #     QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
        #     self.main.prg_widget.gui.allow_cancel = True
        #     self.main.prg_widget.gui.close()
        #     return

        self.main.prg_widget.gui.lblCaption_r.setText("Writing REIP Output-File")
        self.main.QGis_app.processEvents()

        iREIP.write_ireip_image(result=result)

        if first_deriv is not None:
            self.main.prg_widget.gui.lblCaption_r.setText("Writing 1st Derivative Output-File")
            self.main.QGis_app.processEvents()

            iREIP.write_deriv_image(deriv=first_deriv, mode="first")

        if second_deriv is not None:
            self.main.prg_widget.gui.lblCaption_r.setText("Writing 2nd Derivative Output-File")
            self.main.QGis_app.processEvents()

            iREIP.write_deriv_image(deriv=second_deriv, mode="second")

        # try:
        #
        # except:
        #     #QMessageBox.critical(self.gui, 'error', "An unspecific error occured while trying to write image data")
        #     self.main.prg_widget.gui.allow_cancel = True
        #     self.main.prg_widget.gui.close()
        #     return

        self.main.prg_widget.gui.allow_cancel = True
        self.main.prg_widget.gui.close()

        QMessageBox.information(self.gui, "Finish", "Calculation finished successfully")
        #self.gui.close()

    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)

class iREIP_core:

    def __init__(self, nodat_val, division_factor):
        self.nodat = nodat_val
        self.division_factor = division_factor
        self.initial_values()

    def initial_values(self):

        self.wavelengths = None
        self.limits = None
        self.delta = 0
        self.pixel_total = None
        #self.grid, self.nrows, self.ncols, self.nbands, self.in_raster = (
        #None, None, None, None, None)

    def initialize_iREIP(self, input, output, limits, deriv, neighbors, mode):
        self.grid, self.wl, self.nbands, self.nrows, self.ncols, \
        self.in_raster = self.read_image2(image=input)
        self.n_wl = len(self.wl)
        self.pixel_total = self.nrows * self.ncols
        self.neighbors = neighbors
        self.calc_deriv_flag = deriv
        if mode == 'find':
            self.output = None
        elif mode == 'run':
            self.output = output
        self.limits = (self.find_closest(lambd=limits[0]), self.find_closest(lambd=limits[1]))
        self.low_limit, self.upp_limit = (self.limits[0], self.limits[1])

        self.valid_wl = [self.wl[i] for i in range(self.n_wl) if
                         self.wl[i] >= self.low_limit and self.wl[i] <= self.upp_limit]
        self.valid_wl = [int(round(i, 0)) for i in self.valid_wl]

        self.valid_bands = [i for i, x in enumerate(self.wl) if x in list(self.valid_wl)]

        self.default_exclude = [i for j in (range(983, 1129), range(1430, 1650), range(2050, 2151))
                                for i in j]


    def read_image2(self, image):
        '''
        :param image:
        :return:
        '''
        dataset = openRasterDataset(image)

        if dataset.grid() is not None:
            grid = dataset.grid()
        else:
            warnings.warn('No coordinate system information provided in ENVI header file')
            grid = None

        metadict = dataset.metadataDict()

        nrows = int(metadict['ENVI']['lines'])
        ncols = int(metadict['ENVI']['samples'])
        nbands = int(metadict['ENVI']['bands'])
        try:
            wave_dict = metadict['ENVI']['wavelength']
        except ValueError:
            raise ValueError('No wavelength units provided in ENVI header file')

        if metadict['ENVI']['wavelength'] is None:
            raise ValueError('No wavelength units provided in ENVI header file')
        elif metadict['ENVI']['wavelength units'].lower() in \
                ['nanometers', 'nm', 'nanometer']:
            wave_convert = 1
        elif metadict['ENVI']['wavelength units'].lower() in \
                ['micrometers', 'µm', 'micrometer']:
            wave_convert = 1000
        else:
            raise ValueError(
                "Wavelength units must be nanometers or micrometers. Got '%s' instead" %
                metadict['ENVI'][
                    'wavelength units'])

        in_matrix = dataset.readAsArray()

        if self.division_factor != 1.0:
            in_matrix = in_matrix / self.division_factor

        wl = [float(item) * wave_convert for item in wave_dict]
        wl = [int(i) for i in wl]

        return grid, wl, nbands, nrows, ncols, in_matrix

    def write_ireip_image(self, result):
        output = Raster.fromArray(array=result, filename=self.output, grid=self.grid)

        output.dataset().setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

        for band in output.dataset().bands():
            band.setDescription(
                'Inflection point between %i and %i nm' % (self.limits[0], self.limits[1]))
            band.setNoDataValue(self.nodat[1])

    def write_deriv_image(self, deriv, mode):  #

        if mode == "first":
            band_string_nr = ['band ' + str(x) for x in self.valid_bands]
            deriv_output = self.output.split(".")
            deriv_output = deriv_output[0] + "_1st_deriv" + "." + deriv_output[1]
            output = Raster.fromArray(array=deriv, filename=deriv_output, grid=self.grid)

            output.dataset().setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

            for i, band in enumerate(output.dataset().bands()):
                band.setDescription(band_string_nr[i])
                band.setNoDataValue(self.nodat[1])

            output.dataset().setMetadataItem(key='wavelength', value=self.valid_wl, domain='ENVI')
            output.dataset().setMetadataItem(key='wavelength units', value='Nanometers', domain='ENVI')

        if mode == "second":
            band_string_nr = ['band ' + str(x) for x in self.valid_bands]
            deriv_output = self.output.split(".")
            deriv_output = deriv_output[0] + "_2nd_deriv" + "." + deriv_output[1]
            output = Raster.fromArray(array=deriv, filename=deriv_output, grid=self.grid)

            output.dataset().setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

            for i, band in enumerate(output.dataset().bands()):
                band.setDescription(band_string_nr[i])
                band.setNoDataValue(self.nodat[1])

            output.dataset().setMetadataItem(key='wavelength', value=self.valid_wl, domain='ENVI')
            output.dataset().setMetadataItem(key='wavelength units', value='Nanometers', domain='ENVI')


    def find_closest(self, lambd):
        distances = [abs(lambd - self.wl[i]) for i in range(self.n_wl)]
        return self.wl[distances.index(min(distances))]

    def interp_watervapor_1d(self, in_array):
        x = np.arange(len(in_array))
        in_array[self.default_exclude] = 0
        if not np.isnan(in_array).any():
            idx = np.asarray(np.nonzero(in_array))
            idx = idx.flatten()
            interp = interp1d(x[idx], in_array[idx], axis=0, fill_value='extrapolate')
            res = interp(x)
        else:
            res = in_array
        res[res < 0] = 0
        return res

    def interp_watervapor_3d(self, in_matrix):
        x = np.arange(len(in_matrix))
        in_matrix[self.default_exclude] = 0
        res3d = np.empty(shape=np.shape(in_matrix))
        for row in range(in_matrix.shape[1]):
            for col in range(in_matrix.shape[2]):
                if not np.isnan(in_matrix[:, row, col]).any():
                    idx = np.asarray(np.nonzero(in_matrix[:, row, col]))
                    idx = idx.flatten()
                    interp = interp1d(x[idx], in_matrix[idx, row, col], axis=0,
                                      fill_value='extrapolate')
                    res3d[:, row, col] = interp(x)
                else:
                    res3d[:, row, col] = in_matrix[:, row, col]
        return res3d

    def derivate_1d(self, in_array):  # derivative for plot canvases

        smooth_array = savgol_filter(in_array[:], window_length=self.neighbors, polyorder=2)
        first_deriv = np.gradient(smooth_array)
        second_deriv = np.gradient(first_deriv)
        window = second_deriv[self.valid_bands]
        try:
            reip_index_1 = int(np.where(np.sign(window[:-1]) != np.sign(window[1:]))[0])
            reip_index_2 = int(np.where(np.sign(window[:-1]) != np.sign(window[1:]))[0]) + 1
            val_1 = (window[reip_index_1])
            val_2 = (window[reip_index_2])
            reip_pos_1 = int(self.valid_wl[reip_index_1])
            reip_pos_2 = int(self.valid_wl[reip_index_2])
            steps = (reip_pos_2 - reip_pos_1)**2 + 100
            pos_wl, tracker = list(zip(*(list(zip(*(
                np.linspace(reip_pos_1, reip_pos_2, steps), np.linspace(val_1, val_2, steps)))))))
            reip_pos_index = (np.abs(list(tracker))).argmin()
            reip_pos = pos_wl[reip_pos_index]

        except:
            warnings.warn(
                "REIP is not unique. Amplify Savitzky-Golay filter or decrease the range width.")
            reip_pos = None

        return smooth_array, first_deriv, second_deriv, reip_pos

    def derivate_3d(self, in_matrix):  # derivatives for output

        reip_pos = np.empty(shape=(1, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))

        smooth_matrix = savgol_filter(in_matrix, window_length=self.neighbors, polyorder=2, axis=0)
        smooth_window = smooth_matrix[self.valid_bands, :, :]

        d1 = np.gradient(smooth_window, axis=0)
        d2 = np.gradient(d1, axis=0)

        for row in range(in_matrix.shape[1]):
            for col in range(in_matrix.shape[2]):
                #  check for sign change within set range of 2. derivative
                reip_index_1 = np.where(np.sign(d2[:-1, row, col]) != np.sign(d2[1:, row, col]))[0]
                reip_index_2 = \
                    np.where(np.sign(d2[:-1, row, col]) != np.sign(d2[1:, row, col]))[0] + 1
                if len(reip_index_1) != 1 or len(reip_index_2) != 1:
                    reip_pos[:, row, col] = self.nodat[1]
                else:
                    #  resolve accuracy of IP-position
                    reip_index_1 = int(reip_index_1)
                    reip_index_2 = int(reip_index_2)
                    val_1 = d2[reip_index_1, row, col]
                    val_2 = d2[reip_index_2, row, col]
                    reip_pos_1 = self.valid_wl[reip_index_1]
                    reip_pos_2 = self.valid_wl[reip_index_2]
                    steps = (reip_pos_2 - reip_pos_1) ** 2 + 100
                    pos_wl, tracker = list(zip(*(list(zip(*(
                        np.linspace(reip_pos_1, reip_pos_2, steps),
                        np.linspace(val_1, val_2, steps)))))))
                    reip_pos_index = (np.abs(list(tracker))).argmin()
                    reip_pos[:, row, col] = pos_wl[reip_pos_index]

                self.prgbar_process(pixel_no=row * self.ncols + col)

        if self.calc_deriv_flag[0] is False and self.calc_deriv_flag[1] is False:
            return reip_pos, None, None
        elif self.calc_deriv_flag[0] is True and self.calc_deriv_flag[1] is False:
            return reip_pos, d1, None
        elif self.calc_deriv_flag[0] is False and self.calc_deriv_flag[1] is True:
            return reip_pos, None, d2
        else:
            return reip_pos, d1, d2

    def execute_iREIP(self, prg_widget=None, QGis_app=None):
        self.prg = prg_widget
        self.QGis_app = QGis_app
        res, first_deriv, second_deriv = self.derivate_3d(self.in_raster)

        return res, first_deriv, second_deriv

    def findHighestNDVIindex(self, prg_widget=None, QGis_app=None):  # acc. to hNDVI Oppelt(2002)

        self.prg = prg_widget
        self.QGis_app = QGis_app

        NDVI_closest = [self.find_closest(lambd=827), self.find_closest(lambd=668)]
        self.NDVI_bands = [i for i, x in enumerate(self.wl) if x in NDVI_closest]

        for row in range(np.shape(self.in_raster)[1]):
            for col in range(np.shape(self.in_raster)[2]):
                if np.mean(self.in_raster[:, row, col]) != self.nodat[0]:
                    R827 = self.in_raster[self.NDVI_bands[1], row, col]
                    R668 = self.in_raster[self.NDVI_bands[0], row, col]
                    try:
                        NDVI = float(R827 - R668) / float(R827 + R668)
                    except ZeroDivisionError:
                        NDVI = 0
                    self.prgbar_process(pixel_no=row * self.ncols + col)
                    if NDVI > 0.85:
                        self.NDVI = NDVI
                        self.row = row
                        self.col = col
                        break
                else:
                    continue
            else:
                continue
            break

        self.max_index = [self.NDVI, self.row, self.col]  # raster pos where NDVI > 0.85 was found

        return self.max_index

    def prgbar_process(self, pixel_no):
        if self.prg:
            if self.prg.gui.lblCancel.text() == "-1":  # Cancel has been hit shortly before
                self.prg.gui.lblCancel.setText("")
                self.prg.gui.cmdCancel.setDisabled(False)
                raise ValueError("Calculation canceled")
            self.prg.gui.prgBar.setValue(
                pixel_no * 100 // self.pixel_total)  # progress value is index-orientated
            self.prg.gui.lblCaption_l.setText("Processing...")
            self.prg.gui.lblCaption_r.setText("pixel %i of %i" % (pixel_no, self.pixel_total))
            self.QGis_app.processEvents()


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
            QMessageBox.critical(self.gui, "No Data",
                                 "A no data value must be supplied for this image!")
            return
        else:
            try:
                nodat = int(float(self.gui.txtNodat.text()))
            except:
                QMessageBox.critical(self.gui, "No number",
                                     "'%s' is not a valid number" % self.gui.txtNodat.text())
                self.gui.txtNodat.setText("")
                return

        self.nodat = nodat
        self.gui.close()


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
        self.ireip = iREIP(self)
        self.ireip_core = iREIP_core(nodat_val=None, division_factor=None)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.ireip.gui.show()


if __name__ == '__main__':
    gui = True
    if gui == True:
        from enmapbox.testing import initQgisApplication

        app = initQgisApplication()
        m = MainUiFunc()
        m.show()
        sys.exit(app.exec_())


