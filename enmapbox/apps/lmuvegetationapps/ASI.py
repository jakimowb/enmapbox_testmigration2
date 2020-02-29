# -*- coding: utf-8 -*-
from hubflow.core import *
#from gdalconst import *
import numpy as np
#import struct
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
#from osgeo import gdal
import pyqtgraph as pg

#from scipy.spatial import ConvexHull
import sys, os
from lmuvegetationapps.peakdetect import *
from scipy.interpolate import *
import warnings

from enmapbox.gui.utils import loadUIFormClass

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_ASI.ui')
pathUI2 = os.path.join(os.path.dirname(__file__), 'GUI_Nodat.ui')
pathUI_prg = os.path.join(os.path.dirname(__file__), 'GUI_ProgressBar.ui')


class ASI_GUI(QDialog, loadUIFormClass(pathUI)):
    def __init__(self, parent=None):
        super(ASI_GUI, self).__init__(parent)
        self.setupUi(self)
        QApplication.instance().installEventFilter(self)
        self.rangeView.setBackground(QColor('black'))
        self.crsView.setBackground(QColor('black'))


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


class ASI:
    def __init__(self, main):
        self.main = main
        self.gui = ASI_GUI()
        #self.core = ASI_core()
        self.initial_values()
        self.connections()
        self.init_plot()

    def initial_values(self):
        self.image = None
        self.limits = [550, 800]
        self.limits_reset = [550, 800]
        self.lookahead = 9
        self.max_ndvi_pos = None
        self.ndvi_spec = None
        self.nodat = [-999]*2
        self.division_factor = 1.0
        self.calc_crs_flag = False
        self.calc_3band_flag = False

    def connections(self):
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdOutputImage.clicked.connect(lambda: self.open_file(mode="output"))

        self.gui.lowWaveEdit.returnPressed.connect(lambda: self.limits_changed(self.gui.lowWaveEdit))
        self.gui.upWaveEdit.returnPressed.connect(lambda: self.limits_changed(self.gui.upWaveEdit))
        self.gui.peakLookEdit.returnPressed.connect(lambda: self.lookahead_changed())

        self.gui.spinDivisionFactor.returnPressed.connect(lambda: self.division_factor_changed())
        self.gui.cmdFindNDVI.clicked.connect(lambda: self.init_asi(mode='init'))
        self.gui.checkSaveCrs.stateChanged.connect(lambda: self.calc_crs())
        self.gui.checkSave3Band.stateChanged.connect(lambda: self.calc_3band())

        self.gui.pushFullRange.clicked.connect(lambda: self.plot_change(mode="full"))
        self.gui.pushSetRange.clicked.connect(lambda: self.plot_change(mode="zoom"))

        self.gui.pushRun.clicked.connect(lambda: self.init_asi(mode='run'))
        self.gui.pushClose.clicked.connect(lambda: self.gui.close())

    def open_file(self, mode):
        if mode == "image":
            bsq_input, _filter = QFileDialog.getOpenFileName(None, 'Select Input Image', '.', "ENVI Image (*.bsq)")
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
            #result, _filter = QFileDialog.getSaveFileName(None, 'Specify Output File', '.', "ENVI Image(*.bsq)")
            result = QFileDialog.getSaveFileName(caption='Specify Output File', filter="ENVI Image (*.bsq)")[0]
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
            QMessageBox.warning(self.gui, "No image loaded", "Please load an image, press 'Find' and adjust boundaries")
        elif self.max_ndvi_pos is None:
            QMessageBox.warning(self.gui, "No image loaded",
                                "press 'Find' to initialize plot canvas")
        else:
            if textfeld == self.gui.lowWaveEdit:
                try: self.limits[0] = int(str(textfeld.text()))
                except ValueError:
                    QMessageBox.critical(self.gui, "Not a number", "'%s' is not a valid number" % textfeld.text())
            elif textfeld == self.gui.upWaveEdit:
                try: self.limits[1] = int(str(textfeld.text()))
                except ValueError:
                    QMessageBox.critical(self.gui, "Not a number", "'%s' is not a valid number" % textfeld.text())
                self.limits[1] = int(str(textfeld.text()))
            if not self.limits[1] > self.limits[0]:
                ValueError(QMessageBox.critical(self.gui, "Error", "Lower boundary not smaller than upper"))
                self.limits[1] = self.limits[0] + 1
                self.gui.lowWaveEdit.setText(str(self.limits[0]))
                self.gui.upWaveEdit.setText(str(self.limits[1]))

            self.plot_example(self.max_ndvi_pos)

    def lookahead_changed(self):
        if self.image is None:
            QMessageBox.warning(self.gui, "No image loaded",
                                "Please load an image, press 'Find' and adjust boundaries")
        else:
            try:
                self.lookahead = int(str(self.gui.peakLookEdit.text()))
            except ValueError:
                QMessageBox.critical(self.gui, "Integer required",
                                     "'%s is not a valid integer" % (self.gui.peakLookEdit.text()))
            self.init_asi(mode='init')
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
                QMessageBox.critical(self.gui, "Integer required",
                                     "'%s' is not a valid integer" % self.gui.neighborEdit.text())
        self.init_asi(mode='init')
        self.plot_example(self.max_ndvi_pos)

    def calc_crs(self):
        if not self.calc_crs_flag:
            self.calc_crs_flag = True
        else:
            self.calc_crs_flag = False

    def calc_3band(self):
        if not self.calc_3band_flag:
            self.calc_3band_flag = True
            self.gui.lowWaveEdit.setText(str(460))
            self.limits[0] = 460
            self.gui.upWaveEdit.setText(str(1105))
            self.limits[1] = 1105
            self.init_plot()
            if self.max_ndvi_pos:
                self.plot_example(max_ndvi_pos=self.max_ndvi_pos)
        else:
            self.calc_3band_flag = False
            self.gui.lowWaveEdit.setText(str(self.limits_reset[0]))
            self.limits[0] = self.limits_reset[0]
            self.gui.upWaveEdit.setText(str(self.limits_reset[1]))
            self.limits[1] = self.limits_reset[1]
            self.init_plot()
            if self.max_ndvi_pos:
                self.plot_example(max_ndvi_pos=self.max_ndvi_pos)


    def init_plot(self):
        labelStyle = {'color': '#FFF', 'font-size': '12px'}
        self.gui.rangeView.setLabel('left', text="Reflectance [%]", **labelStyle)
        self.gui.rangeView.setLabel('bottom', text="Wavelength [nm]", **labelStyle)

        self.gui.rangeView.plot(clear=True)
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        self.gui.rangeView.setXRange(350, 2500, padding=0)

        self.gui.crsView.plot(clear=True)
        self.gui.crsView.setLabel('left', text="[-]", **labelStyle)
        self.gui.crsView.setLabel('bottom', text="Wavelength [nm]", **labelStyle)
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        self.gui.crsView.setXRange(350, 2500, padding=0)

        self.gui.lblPixelLocation.setText("")


    def plot_example(self, max_ndvi_pos):
        self.gui.lblPixelLocation.setText("Image pixel: row: %s | col: %s" % (
            str(max_ndvi_pos[1]), str(max_ndvi_pos[2])))
        self.gui.lblPixelLocation.setStyleSheet('color: green')
        plot_spec = self.core.interp_watervapor_1d(self.core.ndvi_spec / self.division_factor)

        cr_spectrum, full_hull_x = self.core.segmented_convex_hull_1d(plot_spec)

        self.gui.rangeView.plot(self.core.wl, plot_spec, clear=True, pen="g", fillLevel=0, 
                                fillBrush=(255, 255, 255, 30), name='maxNDVIspec')
        self.gui.rangeView.plot(self.core.wl, full_hull_x, clear=False, pen="r", fillLevel=0,
                                name='hull')
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))

        self.gui.crsView.plot(self.core.wl, cr_spectrum, clear=True, pen="g", fillLevel=0, 
                              fillBrush=(255, 255, 255, 30), name='cr_spec')
        self.gui.crsView.addItem(pg.InfiniteLine(0, angle=0, pen='r'))
        self.gui.crsView.addItem(pg.InfiniteLine(1, angle=0, pen='w'))
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))

    def plot_change(self, mode):
        if mode == 'zoom':
            low, high = self.limits
            self.gui.rangeView.setXRange(low, high)
            self.gui.crsView.setXRange(low, high)

        if mode == 'full':
            low, high = [350, 2500]
            self.gui.rangeView.setXRange(low, high)
            self.gui.crsView.setXRange(low, high)

    def init_asi(self, mode):
        if mode == 'init':
            if self.image is None:
                QMessageBox.critical(self.gui, "No image selected", "Please select an image to continue!")
                return
            try:
                self.division_factor = float(self.gui.spinDivisionFactor.text())
            except:
                QMessageBox.critical(self.gui, "Error", "'%s' is not a valid division factor!" % self.gui.spinDivisionFactor.text())
                return

            if not self.max_ndvi_pos:
                # show progressbar - window
                self.main.prg_widget.gui.lblCaption_l.setText("Searching NDVI > 0.85")
                self.main.prg_widget.gui.lblCaption_r.setText(
                    "Reading Input Image...this may take some time")
                self.main.prg_widget.gui.prgBar.setValue(0)
                self.main.prg_widget.gui.setModal(True)
                self.main.prg_widget.gui.show()
                self.main.QGis_app.processEvents()

                # try
                self.core = ASI_core(nodat_val=self.nodat, division_factor=self.division_factor,
                                     max_ndvi_pos=self.max_ndvi_pos, ndvi_spec=self.ndvi_spec)
                self.core.initialize_ASI(input=self.image, output=None,
                                         limits=self.limits, lookahead=self.lookahead,
                                         crs=self.calc_crs_flag,
                                         calc3band=self.calc_3band_flag, mode='find')
                self.core.in_raster = self.core.read_image(image=self.image)

                # except MemoryError:
                #     QMessageBox.critical(self.gui, 'error', "File too large to read. More RAM needed")
                #     self.main.prg_widget.gui.allow_cancel = True
                #     self.main.prg_widget.gui.close()
                # except ValueError as e:
                #     QMessageBox.critical(self.gui, 'error', str(e))
                #     self.main.prg_widget.gui.allow_cancel = True  # The window may be cancelled
                #     self.main.prg_widget.gui.close()
                #     return
                self.max_ndvi_pos, self.ndvi_spec = self.core.findHighestNDVIindex(
                    in_raster=self.core.in_raster,
                    prg_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)
                #QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
                self.main.prg_widget.gui.allow_cancel = True
                self.main.prg_widget.gui.close()

            else:
                self.core = ASI_core(nodat_val=self.nodat, division_factor=self.division_factor,
                                     max_ndvi_pos=self.max_ndvi_pos, ndvi_spec=self.ndvi_spec)
                self.core.initialize_ASI(input=self.image, output=None,
                                         limits=self.limits, lookahead=self.lookahead,
                                         crs=self.calc_crs_flag,
                                         calc3band=self.calc_3band_flag, mode='find')

            self.plot_example(self.max_ndvi_pos)
        if mode == 'run':
            if self.image is None:
                QMessageBox.critical(self.gui, "No image loaded",
                                     "Please load an image to continue!")
                return
            try:
                self.out_path = str(self.gui.txtOutputImage.text())
            except:
                QMessageBox.warning(self.gui, "No output file selected",
                                    "Please select an output file for your image!")
                return

            # show progressbar - window
            self.main.prg_widget.gui.lblCancel.setText("")
            self.main.prg_widget.gui.lblCaption_l.setText("Analyzing Spectral Integral")
            self.main.prg_widget.gui.lblCaption_r.setText(
                "Reading Input Image...this may take several minutes")
            self.main.prg_widget.gui.prgBar.setValue(0)
            self.main.prg_widget.gui.setModal(True)
            self.main.prg_widget.gui.show()
            self.main.QGis_app.processEvents()
            try:
                self.iASI = ASI_core(nodat_val=self.nodat, division_factor=self.division_factor,
                                max_ndvi_pos=self.max_ndvi_pos, ndvi_spec=self.ndvi_spec)
                self.iASI.initialize_ASI(input=self.image, output=self.out_path,
                                        lookahead=self.lookahead,
                                        limits=self.limits, crs=self.calc_crs_flag,
                                        calc3band=self.calc_3band_flag, mode='run')
            except MemoryError:
                QMessageBox.critical(self.gui, 'error', "File too large to read")
                self.main.prg_widget.gui.allow_cancel = True
                self.main.prg_widget.gui.close()
            except ValueError as e:
                QMessageBox.critical(self.gui, 'error', str(e))
                self.main.prg_widget.gui.allow_cancel = True  # The window may be cancelled
                self.main.prg_widget.gui.close()
                return

            if self.gui.txtNodatOutput.text() == "":
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
            try:
                self.iASI.in_raster = self.core.in_raster[self.iASI.valid_bands, :, :]
                if self.division_factor != 1.0:
                    self.iASI.in_raster = np.divide(self.iASI.in_raster, self.division_factor)
                del self.core.in_raster
            except:
                self.iASI.in_raster = self.iASI.read_image_window(image=self.image)
                if self.division_factor != 1.0:
                    self.iASI.in_raster = np.divide(self.iASI.in_raster, self.division_factor)


            # try:  # give it a shot
            result, crs, res3band = self.iASI.execute_ASI(in_raster=self.iASI.in_raster,
                                                          prg_widget=self.main.prg_widget,
                                                          QGis_app=self.main.QGis_app)
            # except:
            #     QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
            #     self.main.prg_widget.gui.allow_cancel = True
            #     self.main.prg_widget.gui.close()
            #     return
            if not self.calc_3band_flag:
                self.main.prg_widget.gui.lblCaption_r.setText("Writing Integral Output-File")
                self.main.QGis_app.processEvents()
                self.iASI.write_integral_image(result=result)

            if self.calc_crs_flag:
                self.main.prg_widget.gui.lblCaption_r.setText("Writing CRS Output-File")
                self.main.QGis_app.processEvents()
                self.iASI.write_crs_image(crs=crs)

            if self.calc_3band_flag:
                self.main.prg_widget.gui.lblCaption_r.setText("Writing 3-Band Output-File")
                self.main.QGis_app.processEvents()
                self.iASI.write_3band_image(res3band=res3band)

            # try:
            #
            # except:
            #     #QMessageBox.critical(self.gui, 'error', "An unspecific error occured while trying to write image data")
            #     self.main.prg_widget.gui.allow_cancel = True
            #     self.main.prg_widget.gui.close()
            #     return

            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()

            QMessageBox.information(self.gui, "Finish", "Integration finished successfully")
            # self.gui.close()

    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)


class ASI_core:

    def __init__(self, nodat_val, division_factor, max_ndvi_pos, ndvi_spec):
        self.nodat = nodat_val
        self.division_factor = division_factor
        self.max_ndvi_pos = max_ndvi_pos
        self.ndvi_spec = ndvi_spec
        self.initial_values()

    def initial_values(self):
        self.wavelengths = None
        self.limits = [550, 800]
        self.delta = 0
        self.pixel_total = None
        self.grid, self.nrows, self.ncols, self.nbands = (None, None, None, None)
        self.default_exclude = [i for j in
                                (range(983, 1129), range(1430, 1650), range(2050, 2151))
                                for i in j]
        self.enmap_exclude = range(78, 88)

    def initialize_ASI(self, input, output, limits, lookahead, crs, calc3band, mode):
        self.grid, self.wl, self.nbands, self.nrows, self.ncols = self.read_image_meta(image=input)
        self.n_wl = len(self.wl)
        self.pixel_total = self.nrows * self.ncols
        self.calc_crs_flag = crs
        self.calc_3band_flag = calc3band
        if mode == 'find':
            self.output = None
        elif mode == 'run':
            self.output = output

        self.limits = (self.find_closest_wl(lambd=limits[0]), self.find_closest_wl(lambd=limits[1]))
        self.low_limit, self.upp_limit = (self.limits[0], self.limits[1])
        self.lookahead = lookahead
        if len(self.wl) == 242:  # temporary solution for overlapping EnMap-Testdata Bands
            self.wl = np.delete(self.wl, self.enmap_exclude)  # temporary solution!
            self.n_wl = len(self.wl)
            self.nbands = len(self.wl)

        self.valid_wl = [self.wl[i] for i in range(self.n_wl) if
                         self.wl[i] >= self.low_limit and self.wl[i] <= self.upp_limit]
        self.valid_wl = [int(round(i, 0)) for i in self.valid_wl]

        self.valid_bands = [i for i, x in enumerate(self.wl) if x in list(self.valid_wl)]

    def read_image(self, image):
        dataset = openRasterDataset(image)
        raster = dataset.readAsArray()
        if len(self.wl) > 2000:
            try:
                raster[self.default_exclude, :, :] = 0
            except:
                pass
        if len(raster) == 242:  # temporary solution for overlapping EnMap-Testdata Bands
            raster = np.delete(raster, self.enmap_exclude, axis=0)  # temporary solution!
        return raster

    def read_image_window(self, image):
        dataset = openRasterDataset(image)
        raster = dataset.readAsArray()
        if len(self.wl) > 2000:
            try:
                raster[self.default_exclude, :, :] = 0
            except:
                pass
        if len(raster) == 242:  # temporary solution for overlapping EnMap-Testdata Bands
            raster = np.delete(raster, self.enmap_exclude, axis=0)  # temporary solution!
        window = raster[self.valid_bands, :, :]
        return window

    @staticmethod
    def read_image_meta(image):
        dataset = openRasterDataset(image)

        if dataset.grid() is not None:
            grid = dataset.grid()
        else:
            raise Warning('No coordinate system information provided in ENVI header file')
        metadict = dataset.metadataDict()
        nrows = int(metadict['ENVI']['lines'])
        ncols = int(metadict['ENVI']['samples'])
        nbands = int(metadict['ENVI']['bands'])

        try:
            wave_dict = metadict['ENVI']['wavelength']
        except:
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

        wl = [float(item) * wave_convert for item in wave_dict]
        wl = [int(i) for i in wl]

        return grid, wl, nbands, nrows, ncols

    def write_integral_image(self, result):
        #result = result.astype(float)

        output = RasterDataset.fromArray(array=result, filename=self.output, grid=self.grid,
                                         driver=EnviDriver())

        output.setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

        for band in output.bands():
            band.setDescription('Spectral Integral: [%i nm - %i nm]' %
                                (self.limits[0], self.limits[1]))
            band.setNoDataValue(self.nodat[1])



    def write_crs_image(self, crs):  #
        #band_string_nr = ['band ' + str(x) for x in self.valid_bands + 1]
        crs_output = self.output.split(".")
        crs_output = crs_output[0] + "_crs" + "." + crs_output[1]
        output = RasterDataset.fromArray(array=crs, filename=crs_output, grid=self.grid,
                                         driver=EnviDriver())

        output.setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

        for i, band in enumerate(output.bands()):
            #band.setDescription(band_string_nr[i])
            band.setNoDataValue(self.nodat[1])

        output.setMetadataItem(key='wavelength', value=self.valid_wl, domain='ENVI')
        output.setMetadataItem(key='wavelength units', value='Nanometers', domain='ENVI')

    def write_3band_image(self, res3band):
        band_str_nr = ['Car/Cab', 'Cab', 'H2O']
        bands_output = self.output.split(".")
        bands_output = bands_output[0] + "_3band_car_cab_h2o" + "." + bands_output[1]
        output = RasterDataset.fromArray(array=res3band, filename=bands_output, grid=self.grid,
                                         driver=EnviDriver())

        output.setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

        for i, band in enumerate(output.bands()):
            band.setDescription(band_str_nr[i])
            band.setNoDataValue(self.nodat[1])

    def find_closest_wl(self, lambd):
        distances = [abs(lambd - self.wl[i]) for i in range(self.n_wl)]
        return self.wl[distances.index(min(distances))]

    def find_closest_value(self, lambd, array):
        distances = [abs(lambd - array[i]) for i in range(len(array))]
        return array[distances.index(min(distances))]

    def interp_watervapor_1d(self, in_array):
        x = np.arange(len(in_array))
        self.res = np.empty(shape=np.shape(in_array))

        if np.nan not in in_array:
            idx = np.asarray(np.nonzero(in_array))
            idx = idx.flatten()

            interp = interp1d(x[idx], in_array[idx], axis=0, fill_value='extrapolate')
            self.res = interp(x)
        else:
            self.res = in_array
        self.res[self.res < 0] = 0
        return self.res

    def interp_watervapor_3d(self, in_matrix):
        x = np.arange(len(in_matrix))
        try:
            in_matrix[self.default_exclude] = 0
        except: pass
        self.res3d = np.empty(shape=np.shape(in_matrix))
        for row in range(in_matrix.shape[1]):
            for col in range(in_matrix.shape[2]):
                if np.mean(in_matrix[:, row, col]) != self.nodat[0]:
                    idx = np.asarray(np.nonzero(in_matrix[:, row, col]))
                    idx = idx.flatten()
                    interp = interp1d(x[idx], in_matrix[idx, row, col], axis=0, fill_value='extrapolate')
                    self.res3d[:, row, col] = interp(x)
                else:
                    self.res3d[:, row, col] = in_matrix[:, row, col]
        return self.res3d

    def convex_hull(self, points):
        """Computes the convex hull of a set of 2D points.

        Input: an iterable sequence of (x, y) pairs representing the points.
        Output: a list of vertices of the convex hull in counter-clockwise order,
          starting from the vertex with the lexicographically smallest coordinates.
        Implements Andrew's monotone chain algorithm. O(n log n) complexity.
        """

        # Sort the points lexicographically (tuples are compared lexicographically).
        # Remove duplicates to detect the case we have just one unique point.
        points = sorted(set(points))

        # Boring case: no points or a single point, possibly repeated multiple times.
        if len(points) <= 1:
            return points

        # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
        # Returns a positive value, if OAB makes a counter-clockwise turn,
        # negative for clockwise turn, and zero if the points are collinear.
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        # Build lower hull # ## lower hull not needed ##
        # lower = []
        # for p in points:
        #     while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
        #         lower.pop()
        #     lower.append(p)

        # Build upper hull
        self.upper = []
        for p in reversed(points):
            while len(self.upper) >= 2 and cross(self.upper[-2], self.upper[-1], p) <= 0:
                self.upper.pop()
            self.upper.append(p)

        # Concatenation of the lower and upper hulls gives the convex hull.
        # Last point of each list is omitted because it is repeated at the beginning of the other list.
        return self.upper[:]  # lower[:-1] + upper[:-1]

    def segmented_convex_hull_1d(self, in_array):
        '''
        :param in_array: convex hull example only
        :return:
        '''
        if not np.isnan(in_array).any():
            max_, min_ = peakdetect(in_array, lookahead=self.lookahead, delta=self.delta)
            full_hull_x = []
            full_hull_y = []
            if max_:  # if local maximum has been found
                x_max, y_max = map(list, zip(*max_))
                x = 0
                x_seq = np.append(x_max, len(in_array))
                # y_seq = np.append(y_max, in_array[-1])
                for i in x_seq:  # segmented convex hull with detected maxima as separators
                    wl_sample = self.wl[x:i]
                    valid_array = list(zip(wl_sample, in_array[x:i]))
                    hull = self.convex_hull(valid_array)
                    hull_x, hull_y = list(zip(*hull))
                    full_hull_x = np.append(full_hull_x, hull_x)
                    full_hull_y = np.append(full_hull_y, hull_y)
                    x = i
            else:  # no local maximum -> upper hull over limits
                x_seq = np.append(0, len(in_array))
                # y_seq = np.append(in_array[0], in_array[-1])
                wl_sample = self.wl[x_seq[0]:x_seq[-1]]
                valid_array = list(zip(wl_sample, in_array))
                hull = self.convex_hull(valid_array)
                hull_x, hull_y = list(zip(*hull))
                full_hull_x = hull_x
                # full_hull_y = hull_y

            interp_range = np.arange(len(self.wl))
            hull_x_index = np.asarray([i for i, e in enumerate(self.wl) if e in list(full_hull_x)])
            full_hull_x = interp1d(interp_range[hull_x_index], in_array[hull_x_index])
            full_hull_x = full_hull_x(interp_range)

        else:
            full_hull_x = np.nan
            # full_hull_y = np.nan

        cr_spectrum = (full_hull_x - in_array) / full_hull_x

        return cr_spectrum, full_hull_x

    def segmented_convex_hull_3d(self, in_matrix, limits, lookahead=None, delta=None):

        self.prg.gui.lblCaption_l.setText("Calculating convex hull and continuum removed spectra...")

        low, up = limits
        if not low >= 350 and not up <= 2500:
            raise ValueError("Wavelength range must be between 350 and 2500 nm!")
        if low >= up:
            raise ValueError("Lower boundary must be smaller than upper boundary!")

        # in_matrix[in_matrix < 0] = 0
        if len(self.valid_bands) > 2000:
            in_matrix = self.interp_watervapor_3d(in_matrix)
        if self.calc_crs_flag == True:
            cr_spectrum = np.empty(shape=(len(self.valid_wl), np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        else: cr_spectrum = None
        asi_result = np.empty(shape=(1, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        for row in range(in_matrix.shape[1]):
            for col in range(in_matrix.shape[2]):
                if np.mean(in_matrix[:, row, col]) != self.nodat[0]:
                    window = in_matrix[:, row, col]
                    max_, min_ = peakdetect(window, lookahead=lookahead, delta=delta)
                    full_hull_x = []
                    #full_hull_y = []
                    if max_:  # if local maximum has been found
                        x_max, y_max = map(list, zip(*max_))
                        x_seq = np.append(x_max, len(window))
                        if self.valid_wl[x_seq[0]] > 650:
                            force_p = int(self.find_closest_value(554, self.valid_wl))
                            c_band = self.valid_wl.index(force_p)
                            x_seq = np.insert(x_seq, 0, c_band)
                        x = 0
                        for i in x_seq:  # segmented convex hull with detected maxima as separators
                            wl_sample = self.valid_wl[x:i]
                            valid_array = list(zip(wl_sample, window[x:i]))
                            hull = self.convex_hull(valid_array)
                            hull_x, hull_y = list(zip(*hull))
                            full_hull_x = np.append(full_hull_x, hull_x)
                            x = i
                    else:  # no local maximum -> upper hull over limits
                        # y_seq = np.append(window[0], window[-1])
                        if self.calc_3band_flag:
                            force_p = int(self.find_closest_value(554, self.valid_wl))
                            c_band = self.valid_wl.index(force_p)
                            x_seq = [len(window)]
                            x_seq = np.insert(x_seq, 0, c_band)
                            x = 0
                            for i in x_seq:
                                wl_sample = self.valid_wl[x:i]
                                valid_array = list(zip(wl_sample, window[x:i]))
                                hull = self.convex_hull(valid_array)
                                hull_x, hull_y = list(zip(*hull))
                                full_hull_x = np.append(full_hull_x, hull_x)
                                x = i
                        else:
                            valid_array = list(zip(self.valid_wl, window))
                            hull = self.convex_hull(valid_array)
                            hull_x, hull_y = list(zip(*hull))
                            full_hull_x = hull_x

                    interp_range = np.arange(len(self.valid_wl))
                    hull_x_index = np.asarray([i for i, e in enumerate(self.valid_wl) if
                                               e in list(full_hull_x)])
                    full_hull_x = interp1d(interp_range[hull_x_index], window[hull_x_index])
                    contiguous_hull_x = full_hull_x(interp_range)

                else:
                    contiguous_hull_x = np.nan
                    #full_hull_y = np.nan
                if self.calc_crs_flag:
                    if np.mean(in_matrix[:, row, col]) != self.nodat[0]:
                        try:
                            cr_spectrum[:, row, col] = 1 - (in_matrix[:, row, col] / contiguous_hull_x)
                        except ZeroDivisionError:
                            cr_spectrum[:, row, col] = 0
                    else:
                        cr_spectrum[:, row, col] = self.nodat[1]

                asi_result[:, row, col] = \
                    (np.nansum(contiguous_hull_x) - np.nansum(in_matrix[:, row, col])) / \
                    np.nansum(contiguous_hull_x)

                self.prgbar_process(pixel_no=row * self.ncols + col)

        if self.calc_crs_flag:
            cr_spectrum[np.isnan(cr_spectrum)] = 0

        return asi_result, cr_spectrum

    def segmented_convex_hull_3d_3band(self, in_matrix, limits, lookahead=None, delta=None):

        self.prg.gui.lblCaption_l.setText("Separating Ccx, Cab, and H2o integral ranges...")

        low, up = limits
        if not low >= 350 and not up <= 2500:
            raise ValueError("Wavelength range must be between 350 and 2500 nm!")
        if low >= up:
            raise ValueError("Lower boundary must be smaller than upper boundary!")

        res3band = np.empty(shape=(3, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        absorb_area = np.empty(shape=(3, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        hull_area = np.empty(shape=(3, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        # test
        cr_absorb_area = np.empty(shape=(3, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        ones_sum = np.empty(shape=(3, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        ones = np.ones_like(in_matrix)
        #in_matrix = self.interp_watervapor_3d(in_matrix)

        closest = [self.find_closest_value(553, self.valid_wl), self.find_closest_value(554, self.valid_wl),
                        self.find_closest_value(787, self.valid_wl),
                        self.find_closest_value(900, self.valid_wl),
                        self.find_closest_value(1105, self.valid_wl)]

        closest_bands = [i for i, x in enumerate(self.valid_wl) if x in closest]
        if len(closest_bands) < 5:
            closest_bands.insert(0, closest_bands[0])
        # window = in_matrix[self.valid_bands, :, :]

        for row in range(in_matrix.shape[1]):
            for col in range(in_matrix.shape[2]):
                if np.mean(in_matrix[:, row, col]) != self.nodat[0]:
                    window = in_matrix[:, row, col]
                    max_, min_ = peakdetect(window, lookahead=lookahead, delta=delta)
                    full_hull_x = []
                    green_peak = 0
                    if max_:  # if local maximum has been found
                        x_max, y_max = map(list, zip(*max_))
                        x = 0
                        nir_peak = max([
                            self.valid_wl[i] for i in x_max if 850 < self.valid_wl[i] < 970],
                            default=[])
                        x_seq = np.append(x_max, len(window))
                        # if self.valid_wl[x_seq[0]] < 550:
                        #     res3band[:, row, col] = np.nan
                        #     continue
                        if self.valid_wl[x_seq[0]] > 650:
                            force_p = int(self.find_closest_value(554, self.valid_wl))
                            c_band = self.valid_wl.index(force_p)
                            x_seq = np.insert(x_seq, 0, c_band)
                            closest_bands[1] = x_seq[0]
                            green_peak = 0
                        else:
                            if 545 < self.valid_wl[x_seq[0]] < 600:
                                closest_bands[1] = x_seq[0]
                                green_peak = 1
                        if nir_peak:
                            closest_bands[3] = self.valid_wl.index(nir_peak)
                        for i in x_seq:  # segmented convex hull with detected maxima as separators
                            wl_sample = self.valid_wl[x:i]
                            valid_array = list(zip(wl_sample, window[x:i]))
                            hull = self.convex_hull(valid_array)
                            hull_x, hull_y = list(zip(*hull))
                            full_hull_x = np.append(full_hull_x, hull_x)
                            x = i
                    else:  # no local maximum -> upper hull over limits
                        nir_peak = 0
                        force_p = int(closest[1])
                        force_p2 = int(closest[3])
                        c_band = self.valid_wl.index(force_p)
                        edge_band = self.valid_wl.index(force_p2)
                        x_seq = [len(window)]
                        x_seq = np.insert(x_seq, 0, c_band)
                        x_seq = np.insert(x_seq, 1, edge_band)
                        x = 0
                        for i in x_seq:
                            wl_sample = self.valid_wl[x:i]
                            valid_array = list(zip(wl_sample, window[x:i]))
                            hull = self.convex_hull(valid_array)
                            hull_x, hull_y = list(zip(*hull))
                            full_hull_x = np.append(full_hull_x, hull_x)
                            x = i

                    interp_range = np.arange(len(self.valid_wl))
                    hull_x_index = np.asarray(
                        [i for i, e in enumerate(self.valid_wl) if e in list(full_hull_x)])

                    full_hull_x = interp1d(interp_range[hull_x_index], window[hull_x_index])
                    contiguous_hull_x = full_hull_x(interp_range)

                    indices = np.nonzero(np.isin(contiguous_hull_x, window))[0]

                    item0 = next((self.valid_wl[indices[l]] for l in range(len(indices)) if
                                  500 < self.valid_wl[indices[l]] < 550), None)
                    item1 = next((self.valid_wl[indices[l]] for l in range(len(indices)) if
                                  550 < self.valid_wl[indices[l]] < 700), None)
                    item2 = next((self.valid_wl[indices[l]] for l in range(len(indices)) if
                                  700 < self.valid_wl[indices[l]] < 800), None)
                    item3 = next((self.valid_wl[indices[l]] for l in range(len(indices)) if
                                  910 < self.valid_wl[indices[l]] < 950), None)
                    item4 = next((self.valid_wl[indices[l]] for l in range(len(indices)) if
                                  970 < self.valid_wl[indices[l]] < 1105), None)
                    if item0:
                        closest_bands[0] = self.valid_wl.index(item0)
                    if item1 and green_peak != 1:
                        closest_bands[1] = self.valid_wl.index(item1)
                    if item2:
                        closest_bands[2] = self.valid_wl.index(item2)
                    if item3 and nir_peak == 0:
                        closest_bands[3] = self.valid_wl.index(item3)
                    if item4:
                        closest_bands[4] = self.valid_wl.index(item4)
                else:
                    contiguous_hull_x = np.nan
                k = 0
                if np.mean(in_matrix[:, row, col]) == self.nodat[0]:
                    res3band[:, row, col] = np.nan
                    continue
                if np.max(in_matrix[:, row, col]) > 1:  # bad pixel exclusion with reflectances > 1
                    res3band[:, row, col] = 0
                    continue
                for j, i in enumerate(closest_bands):
                    if j == 1:  # skip the red shoulder
                        k = i
                        continue
                    if j == 2:
                        j -= 1  # avoid j-overflow for size 2
                    if j == 3:
                        k = i
                        j -= 1
                        continue
                    if j == 4:
                        j -= 2
                    try:

                        # absorb_area[j, row, col] = np.nansum(np.log(1/in_matrix[k:i, row, col])) - \
                        #                                (np.nansum(np.log(1/contiguous_hull_x[k:i])))
                        # hull_area[j, row, col] = np.nansum(np.log(1 / in_matrix[k:i, row, col]))
                        #res3band[j, row, col] = absorb_area[j, row, col] / hull_area[j, row, col]

                        cr_absorb_area[j, row, col] = np.nansum((np.log(1/in_matrix[k:i, row, col]) -
                                                                 np.log(1/contiguous_hull_x[k:i])) /
                                                                np.log(1/in_matrix[k:i, row, col]))
                        ones_sum[j, row, col] = np.nansum(ones[k:i, row, col])
                        absorb_area[j, row, col] = np.nansum(np.log(1 / in_matrix[k:i, row, col]) -
                                                             np.log(1 / contiguous_hull_x[k:i]))  # / np.nansum(contiguous_hull_x[k:i])
                        hull_area[j, row, col] = np.nansum(np.log(1 / in_matrix[k:i, row, col]))
                        res3band[j, row, col] = absorb_area[j, row, col] / hull_area[j, row, col]
                        #res3band[j, row, col] = cr_absorb_area[j, row, col] / ones_sum[j, row, col]
                    except ZeroDivisionError:
                        res3band[j, row, col] = np.nan

                    # if j == 0 and res3band[j, row, col] > 1:
                    #     res3band[j, row, col] = 0

                    k = i

                # max_ = np.amax(ones_sum, axis=1, keepdims=True)
                # res3band = absorb_area/max_

                self.prgbar_process(pixel_no=row * self.ncols + col)
        # perc = np.percentile(hull_area, 90, axis=1, keepdims=True)
        # perc = np.percentile(perc, 90, axis=2, keepdims=True)
        max_hull_1 = np.nanmean(hull_area, axis=1, keepdims=True)
        max_hull_2 = np.nanmean(max_hull_1, axis=2, keepdims=True)
        max_1 = np.amax(ones_sum, axis=1, keepdims=True)
        max_ = np.amax(max_1, axis=2, keepdims=True)
        #print(max_hull_2)
        #res3band = absorb_area / max_hull_2
        cr_absorb_area[cr_absorb_area < 0] = 0
        res3band[0, :, :] = cr_absorb_area[0, :, :] / max_[0]
        res3band[1, :, :] = cr_absorb_area[1, :, :] / max_[1]
        res3band[2, :, :] = absorb_area[2, :, :] / max_hull_2[2]

        res3band[res3band < 0] = 0
        res3band[~np.isfinite(res3band)] = self.nodat[1]
        return res3band

    def execute_ASI(self, in_raster, prg_widget=None, QGis_app=None):
        self.prg = prg_widget
        self.QGis_app = QGis_app
        res, crs, res3band = None, None, None

        if self.calc_3band_flag:
            res3band = self.segmented_convex_hull_3d_3band(in_matrix=in_raster,
                                                           limits=self.limits,
                                                           lookahead=self.lookahead,
                                                           delta=self.delta)

        if self.calc_crs_flag:
            res, crs = self.segmented_convex_hull_3d(in_matrix=in_raster, limits=self.limits,
                                                     lookahead=self.lookahead, delta=self.delta)

        if not self.calc_3band_flag and not self.calc_crs_flag:
            res, crs = self.segmented_convex_hull_3d(in_matrix=in_raster, limits=self.limits,
                                                     lookahead=self.lookahead, delta=self.delta)
            crs = None

        return res, crs, res3band

    def findHighestNDVIindex(self, in_raster, prg_widget=None, QGis_app=None):  # acc. to hNDVI Oppelt(2002)

        self.prg = prg_widget
        self.QGis_app = QGis_app

        NDVI_closest = [self.find_closest_wl(lambd=827), self.find_closest_wl(lambd=668)]
        self.NDVI_bands = [i for i, x in enumerate(self.wl) if x in NDVI_closest]

        for row in range(np.shape(in_raster)[1]):
            for col in range(np.shape(in_raster)[2]):
                if np.mean(in_raster[:, row, col]) != self.nodat[0]:
                    R827 = in_raster[self.NDVI_bands[1], row, col]
                    R668 = in_raster[self.NDVI_bands[0], row, col]
                    try:
                        NDVI = float(R827 - R668) / float(R827 + R668)
                    except ZeroDivisionError:
                        NDVI = 0
                    self.prgbar_process(pixel_no=row * self.ncols + col)
                    if NDVI > 0.85 and NDVI <= 1.0:
                        self.NDVI = NDVI
                        self.row = row
                        self.col = col
                        self.ndvi_spec = in_raster[:, row, col]
                        break
                else:
                    continue
            else:
                continue
            break

        self.max_index = [self.NDVI, self.row, self.col]  # raster pos where NDVI > 0.85 was found

        return self.max_index, self.ndvi_spec

    def prgbar_process(self, pixel_no):
        if self.prg:
            if self.prg.gui.lblCancel.text() == "-1":  # Cancel has been hit shortly before
                self.prg.gui.lblCancel.setText("")
                self.prg.gui.cmdCancel.setDisabled(False)
                QMessageBox.information(self.prg.gui, "Cancelled", "Calculation cancelled")
            self.prg.gui.prgBar.setValue(pixel_no*100 // self.pixel_total)  # progress value is index-orientated
            #self.prg.gui.lblCaption_l.setText("Processing...")
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
        self.asi = ASI(self)
        self.asi_core = ASI_core(nodat_val=None, division_factor=None, max_ndvi_pos=None,
                                 ndvi_spec=None)
        self.nodat_widget = Nodat(self)
        self.prg_widget = PRG(self)

    def show(self):
        self.asi.gui.show()

if __name__ == '__main__':
    gui = True
    if gui == True:
        from enmapbox.testing import initQgisApplication
        app = initQgisApplication()
        m = MainUiFunc()
        m.show()
        sys.exit(app.exec_())




