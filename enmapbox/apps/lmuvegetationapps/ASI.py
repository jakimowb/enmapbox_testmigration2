# -*- coding: utf-8 -*-
from hubflow.core import *
from gdalconst import *
import numpy as np
import struct
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from osgeo import gdal
import pyqtgraph as pg

from scipy.spatial import ConvexHull
import sys, os
from lmuvegetationapps.peakdetect import *
from scipy.interpolate import *

pathUI = os.path.join(os.path.dirname(__file__), 'GUI_ASI.ui')
pathUI2 = os.path.join(os.path.dirname(__file__), 'GUI_Nodat.ui')
pathUI_prg = os.path.join(os.path.dirname(__file__), 'GUI_ProgressBar.ui')


from enmapbox.gui.utils import loadUIFormClass


class ASI_GUI(QDialog, loadUIFormClass(pathUI)):
    def __init__(self, parent=None):
        super(ASI_GUI, self).__init__(parent)
        self.setupUi(self)
        QApplication.instance().installEventFilter(self)


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
        self.lookahead = 50
        self.max_ndvi_pos = None
        self.nodat = [-999]*2
        self.division_factor = 1.0
        self.calc_crs_flag = False

    def connections(self):
        self.gui.cmdInputImage.clicked.connect(lambda: self.open_file(mode="image"))
        self.gui.cmdOutputImage.clicked.connect(lambda: self.open_file(mode="output"))

        self.gui.lowWaveEdit.returnPressed.connect(lambda: self.limits_changed(self.gui.lowWaveEdit))
        self.gui.upWaveEdit.returnPressed.connect(lambda: self.limits_changed(self.gui.upWaveEdit))
        self.gui.peakLookEdit.returnPressed.connect(lambda: self.lookahead_changed())

        self.gui.spinDivisionFactor.returnPressed.connect(lambda: self.init_asi())
        self.gui.cmdFindNDVI.clicked.connect(lambda: self.init_asi())
        self.gui.checkSaveCrs.stateChanged.connect(lambda: self.calc_crs())

        self.gui.pushRun.clicked.connect(lambda: self.init_run())
        self.gui.pushClose.clicked.connect(lambda: self.gui.close())

    def open_file(self, mode):
        if mode == "image":
            bsq_input, _filter = QFileDialog.getOpenFileName(None, 'Select Input Image', '.', "ENVI Image (*.bsq)")
            if not bsq_input: return
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
                self.nodat[0] = meta[0]
        elif mode == "output":
            #result, _filter = QFileDialog.getSaveFileName(None, 'Specify Output File', '.', "ENVI Image(*.bsq)")
            result = QFileDialog.getSaveFileName(caption='Specify Output File', filter="ENVI Image (*.bsq)")[0]
            if not result:
                raise ImportError('Input file could not be read.  Please make sure it is a valid ENVI image')
            self.out_path = result
            self.out_path = self.out_path.replace("\\", "/")
            self.gui.txtOutputImage.setText(result)

    def get_image_meta(self, image, image_type):
        dataset = gdal.Open(image)
        if dataset is None:
            raise ValueError('%s could not be read. Please make sure it is a valid ENVI image' % image_type)
        else:
            nbands = dataset.RasterCount
            nrows = dataset.RasterYSize
            ncols = dataset.RasterXSize

            try:
                nodata = int("".join(dataset.GetMetadataItem('data_ignore_value', 'ENVI').split()))
                return nodata, nbands, nrows, ncols
            except:
                self.main.nodat_widget.init(image_type=image_type, image=image)
                self.main.nodat_widget.gui.setModal(True)  # parent window is blocked
                self.main.nodat_widget.gui.exec_()  # unlike .show(), .exec_() waits with execution of the code, until the app is closed
                return self.main.nodat_widget.nodat, nbands, nrows, ncols

    def limits_changed(self, textfeld):
        if self.image is None:
            QMessageBox.warning(self.gui, "No image loaded", "Please load an image, press 'Find' and adjust boundaries")
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
                self.limits = self.limits_reset
                self.gui.lowWaveEdit.setText(str(self.limits[0]))
                self.gui.upWaveEdit.setText(str(self.limits[1]))

            self.plot_example(self.max_ndvi_pos)

    def lookahead_changed(self):
        if self.image is None:
            QMessageBox.warning(self.gui, "No image loaded", "Please load an image, press 'Find' and adjust boundaries")
        else:
            self.lookahead = int(str(self.gui.peakLookEdit.text()))
            self.init_asi()
            self.plot_example(self.max_ndvi_pos)

    def calc_crs(self):
        if self.calc_crs_flag == False:
            self.calc_crs_flag = True
        else:
            self.calc_crs_flag = False

    def init_plot(self):
        labelStyle = {'color': '#FFF', 'font-size': '12px'}
        self.gui.rangeView.setLabel('left', text="Reflectance [%]", **labelStyle)
        self.gui.rangeView.setLabel('bottom', text="Wavelength [nm]", **labelStyle)

        self.gui.rangeView.plot(clear=False)
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        self.gui.rangeView.setXRange(350, 2500, padding=0)

        self.gui.crsView.setLabel('left', text="[-]", **labelStyle)
        self.gui.crsView.setLabel('bottom', text="Wavelength [nm]", **labelStyle)
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))
        self.gui.crsView.setXRange(350, 2500, padding=0)

    def plot_example(self, max_ndvi_pos):
        plot_spec = self.core.in_raster[:, max_ndvi_pos[1], max_ndvi_pos[2]]
        plot_spec = self.core.interp_watervapor_1d(plot_spec)

        cr_spectrum, full_hull_x = self.core.segmented_convex_hull_1d(plot_spec)

        self.gui.rangeView.plot(self.core.wl, plot_spec, clear=True, pen="g", fillLevel=0, fillBrush=(255, 255, 255, 30),
                                    name='maxNDVIspec')
        self.gui.rangeView.plot(self.core.wl, full_hull_x, clear=False, pen="r", fillLevel=0,
                                name='hull')
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.rangeView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))

        self.gui.crsView.plot(self.core.wl, cr_spectrum, clear=True, pen="g", fillLevel=0, fillBrush=(255, 255, 255, 30),
                                    name='cr_spec')
        self.gui.crsView.addItem(pg.InfiniteLine(1, angle=0, pen='r'))
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[0], pen="w"))
        self.gui.crsView.addItem(pg.InfiniteLine(self.limits[1], pen="w"))

    def init_asi(self):
        if self.image is None:
            QMessageBox.critical(self.gui, "No image selected", "Please select an image to continue!")
            return
        try:
            self.division_factor = float(self.gui.spinDivisionFactor.text())
        except:
            QMessageBox.critical(self.gui, "Error", "'%s' is not a valid division factor!" % self.gui.spinDivisionFactor.text())
            return

        if self.max_ndvi_pos is None:
            # show progressbar - window
            self.main.prg_widget.gui.lblCaption_l.setText("Searching NDVI max")
            self.main.prg_widget.gui.lblCaption_r.setText("Reading Input Image...this may take several minutes")
            self.main.prg_widget.gui.prgBar.setValue(0)
            self.main.prg_widget.gui.setModal(True)
            self.main.prg_widget.gui.show()
            self.main.QGis_app.processEvents()

        try:
            self.core = ASI_core(nodat_val=self.nodat, division_factor=self.division_factor)
            self.core.initialize_ASI(input=self.image, output=None,
                                     limits=self.limits, lookahead=self.lookahead, crs=self.calc_crs_flag, mode='find')
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
            self.max_ndvi_pos = self.core.findHighestNDVIindex(prg_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)


            #QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
        self.plot_example(self.max_ndvi_pos)
        return

    def init_run(self):
        if self.image is None:
            QMessageBox.critical(self.gui, "No image loaded", "Please load an image to continue!")
            return
        elif self.out_path is None:
            QMessageBox.critical(self.gui, "No output file selected", "Please select an output file for your image!")
            return
        elif self.gui.txtNodatOutput.text() == "":
            QMessageBox.warning(self.gui, "No Data Value", "Please specify No Data Value!")
            #QMessageBox.critical(self.gui, "No Data Value", "Please specify No Data Value!")
            return
        else:
            try:
                self.nodat[1] = int(self.gui.txtNodatOutput.text())
            except:
                QMessageBox.critical(self.gui, "Error", "'%s' is not a valid  No Data Value!" % self.gui.txtNodatOutput.text())
                return
        try:
            self.division_factor = float(self.gui.spinDivisionFactor.text())
        except:
            QMessageBox.critical(self.gui, "Error", "'%s' is not a valid division factor!" % self.gui.spinDivisionFactor.text())
            return


        # show progressbar - window
        self.main.prg_widget.gui.lblCaption_l.setText("Analyzing Spectral Integral")
        self.main.prg_widget.gui.lblCaption_r.setText("Reading Input Image...this may take several minutes")
        self.main.prg_widget.gui.prgBar.setValue(0)
        self.main.prg_widget.gui.setModal(True)
        self.main.prg_widget.gui.show()
        self.main.QGis_app.processEvents()

        try:
            iASI = ASI_core(nodat_val=self.nodat, division_factor=self.division_factor)
            iASI.initialize_ASI(input=self.image, output=self.out_path, lookahead=self.lookahead, limits=self.limits,
                                crs=self.calc_crs_flag, mode='run')
        except MemoryError:
            QMessageBox.critical(self.gui, 'error', "File too large to read")
            self.main.prg_widget.gui.allow_cancel = True
            self.main.prg_widget.gui.close()
        except ValueError as e:
            QMessageBox.critical(self.gui, 'error', str(e))
            self.main.prg_widget.gui.allow_cancel = True  # The window may be cancelled
            self.main.prg_widget.gui.close()
            return

        #try:  # give it a shot

        result, crs = iASI.execute_ASI(prg_widget=self.main.prg_widget, QGis_app=self.main.QGis_app)
        # except:
        #     QMessageBox.critical(self.gui, 'error', "An unspecific error occured.")
        #     self.main.prg_widget.gui.allow_cancel = True
        #     self.main.prg_widget.gui.close()
        #     return

        self.main.prg_widget.gui.lblCaption_r.setText("Writing Integral Output-File")
        self.main.QGis_app.processEvents()

        iASI.write_integral_image(result=result)

        if crs is not None:
            self.main.prg_widget.gui.lblCaption_r.setText("Writing CRS Output-File")
            self.main.QGis_app.processEvents()

            iASI.write_crs_image(crs=crs)
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
        self.gui.close()

    def abort(self, message):
        QMessageBox.critical(self.gui, "Error", message)

class ASI_core:

    def __init__(self, nodat_val, division_factor):
        self.nodat = nodat_val
        self.division_factor = division_factor
        self.initial_values()

    def initial_values(self):

        self.wavelengths = None
        self.limits = [550, 800]
        self.delta = 0
        self.pixel_total = None
        self.grid, self.nrows, self.ncols, self.nbands, self.in_raster = (None, None, None, None, None)

    def initialize_ASI(self, input, output, limits, lookahead, crs, mode):

        self.grid, self.wl, self.nbands, self.nrows, self.ncols, self.in_raster = self.read_image2(image=input)
        self.n_wl = len(self.wl)
        self.pixel_total = self.nrows * self.ncols
        self.calc_crs_flag = crs
        if mode == 'find':
            self.output = None
        elif mode == 'run':
            self.output = output
        self.limits = (self.find_closest(lambd=limits[0]), self.find_closest(lambd=limits[1]))
        self.low_limit, self.upp_limit = (self.limits[0], self.limits[1])
        self.lookahead = lookahead

        self.valid_wl = [self.wl[i] for i in range(self.n_wl) if
                         self.wl[i] >= self.low_limit and self.wl[i] <= self.upp_limit]
        self.valid_wl = [int(round(i, 0)) for i in self.valid_wl]

        self.valid_bands = [i for i, x in enumerate(self.wl) if x in list(self.valid_wl)]

    def read_image2(self, image):
        '''
        :param image:
        :return:
        '''
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
            raise ValueError("Wavelength units must be nanometers or micrometers. Got '%s' instead" % metadict['ENVI'][
                'wavelength units'])

        in_matrix = dataset.readAsArray()

        if self.division_factor != 1.0:
            in_matrix = in_matrix / self.division_factor

        wl = [float(item) * wave_convert for item in wave_dict]
        wl = [int(i) for i in wl]

        return grid, wl, nbands, nrows, ncols, in_matrix

    def write_integral_image(self, result):
        output = Raster.fromArray(array=result, filename=self.output, grid=self.grid)

        output.dataset().setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

        for band in output.dataset().bands():
            band.setDescription('Spectral Integral: [%i nm - %i nm]' % (self.limits[0], self.limits[1]))
            band.setNoDataValue(self.nodat[1])

    def write_crs_image(self, crs):  #
        crs_output = self.output.split(".")
        crs_output = crs_output[0] + "_crs" + "." + crs_output[1]
        output = Raster.fromArray(array=crs, filename=(crs_output), grid=self.grid)

        output.dataset().setMetadataItem('data ignore value', self.nodat[1], 'ENVI')

        for i, band in enumerate(output.dataset().bands()):
            #band.setDescription(self.valid_bands[i])
            band.setNoDataValue(self.nodat[1])

        output.dataset().setMetadataItem(key='wavelength', value=self.valid_wl, domain='ENVI')
        output.dataset().setMetadataItem(key='wavelength units', value='Nanometers', domain='ENVI')

    def find_closest(self, lambd):
        distances = [abs(lambd - self.wl[i]) for i in range(self.n_wl)]
        return self.wl[distances.index(min(distances))]

    def interp_watervapor_1d(self, in_array):
        x = np.arange(len(in_array))
        self.res = np.empty(shape=np.shape(in_array))
        default_exclude = [i for j in (range(983, 1129), range(1430, 1650), range(2050, 2151)) for i in j]
        in_array[default_exclude] = 0
        
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
        self.res3d = np.empty(shape=np.shape(in_matrix))
        default_exclude = [i for j in (range(983, 1129), range(1430, 1650), range(2050, 2151)) for i in j]
        in_matrix[default_exclude] = 0
        in_matrix[in_matrix == self.nodat[1]] = np.nan
        for row in range(in_matrix.shape[1]):
            for col in range(in_matrix.shape[2]):
                if not np.isnan(in_matrix[:, row, col]).any():
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
        valid_wl = range(350, 2501)
        window = in_array

        if not np.isnan(window).any():
            max_, min_ = peakdetect(window, lookahead=self.lookahead, delta=self.delta)
            full_hull_x = []
            full_hull_y = []
            if max_:  # if local maximum has been found
                x_max, y_max = map(list, zip(*max_))
                x = 0
                x_seq = np.append(x_max, len(window))
                # y_seq = np.append(y_max, window[-1])
                for i in x_seq:  # segmented convex hull with detected maxima as separators
                    wl_sample = valid_wl[x:i]

                    valid_array = list(zip(wl_sample, window[x:i]))
                    hull = self.convex_hull(valid_array)
                    hull_x, hull_y = list(zip(*hull))
                    full_hull_x = np.append(full_hull_x, hull_x)
                    full_hull_y = np.append(full_hull_y, hull_y)
                    x = i
            else:  # no local maximum -> upper hull over limits

                x_seq = np.append(0, len(window))
                # y_seq = np.append(window[0], window[-1])
                wl_sample = valid_wl[x_seq[0]:x_seq[-1]]

                valid_array = list(zip(wl_sample, window))
                hull = self.convex_hull(valid_array)
                hull_x, hull_y = list(zip(*hull))
                full_hull_x = hull_x
                # full_hull_y = hull_y

            interp_range = np.arange(len(valid_wl))
            hull_x_index = np.asarray([i for i, e in enumerate(valid_wl) if e in list(full_hull_x)])
            full_hull_x = interp1d(interp_range[hull_x_index], window[hull_x_index], axis=0, )
            full_hull_x = full_hull_x(interp_range)

        else:
            full_hull_x = np.nan
            # full_hull_y = np.nan

        cr_spectrum = window / full_hull_x

        return cr_spectrum, full_hull_x

    def segmented_convex_hull_3d(self, in_matrix, limits, lookahead=None, delta=None):
        low, up = limits
        if not low >= 350 and not up <= 2500:
            raise ValueError("Wavelength range must be between 350 and 2500 nm!")
        if low >= up:
            raise ValueError("Lower boundary must be smaller than upper boundary!")

        # in_matrix[in_matrix < 0] = 0
        in_matrix = self.interp_watervapor_3d(in_matrix)
        if self.calc_crs_flag == True:
            cr_spectrum = np.empty(shape=(len(self.valid_wl), np.shape(in_matrix)[1], np.shape(in_matrix)[2]))
        asi_result = np.empty(shape=(1, np.shape(in_matrix)[1], np.shape(in_matrix)[2]))

        for row in range(in_matrix.shape[1]):
            for col in range(in_matrix.shape[2]):
                if not np.isnan(in_matrix[:, row, col]).any():


                    window = in_matrix[self.valid_bands, row, col]
                    max_, min_ = peakdetect(window, lookahead=lookahead, delta=delta)

                    full_hull_x = []
                    full_hull_y = []
                    if max_:  # if local maximum has been found
                        x_max, y_max = map(list, zip(*max_))
                        x = 0
                        x_seq = np.append(x_max, len(window))
                        # y_seq = np.append(y_max, window[-1])
                        for i in x_seq:  # segmented convex hull with detected maxima as separators
                            wl_sample = self.valid_wl[x:i]
                            valid_array = list(zip(wl_sample, window[x:i]))
                            hull = self.convex_hull(valid_array)
                            hull_x, hull_y = list(zip(*hull))
                            full_hull_x = np.append(full_hull_x, hull_x)
                            full_hull_y = np.append(full_hull_y, hull_y)
                            x = i
                    else:  # no local maximum -> upper hull over limits
                        x_seq = np.append(0, len(window))
                        # y_seq = np.append(window[0], window[-1])
                        wl_sample = self.valid_wl[x_seq[0]:x_seq[-1]]
                        valid_array = list(zip(wl_sample, window))
                        hull = self.convex_hull(valid_array)
                        hull_x, hull_y = list(zip(*hull))
                        full_hull_x = hull_x
                        #full_hull_y = hull_y

                    interp_range = np.arange(len(self.valid_wl))
                    hull_x_index = np.asarray([i for i, e in enumerate(self.valid_wl) if e in list(full_hull_x)])
                    full_hull_x = interp1d(interp_range[hull_x_index], window[hull_x_index], axis=0, )
                    full_hull_x = full_hull_x(interp_range)

                else:
                    full_hull_x = np.nan
                    #full_hull_y = np.nan

                if self.calc_crs_flag == True:
                    cr_spectrum[:, row, col] = window / full_hull_x
                asi_result[:, row, col] = np.nansum(full_hull_x - window) / np.nansum(full_hull_x)
                self.prgbar_process(pixel_no=row * self.ncols + col)

        if self.calc_crs_flag == False:
            return asi_result, None
        else:
            return asi_result, cr_spectrum

    def execute_ASI(self, prg_widget=None, QGis_app=None):
        self.prg = prg_widget
        self.QGis_app = QGis_app
        res, crs = self.segmented_convex_hull_3d(self.in_raster, self.limits, lookahead=self.lookahead, delta=self.delta)

        return res, crs

    def findHighestNDVIindex(self, prg_widget=None, QGis_app=None):  # acc. to hNDVI Oppelt(2002)
        in_raster = self.in_raster
        if np.isnan(self.in_raster).any():
            self.in_raster[self.in_raster < 0.0] = np.nan

        self.prg = prg_widget
        self.QGis_app = QGis_app

        NDVI_closest = [self.find_closest(lambd=827), self.find_closest(lambd=668)]
        self.NDVI_bands = [i for i, x in enumerate(self.wl) if x in NDVI_closest]

        NDVI_raster = np.empty(shape=(1, np.shape(in_raster)[1], np.shape(in_raster)[2]))

        for row in range(np.shape(in_raster)[1]):
            for col in range(np.shape(in_raster)[2]):
                if np.nan not in self.in_raster[:, row, col]:
                    R827 = self.in_raster[self.NDVI_bands[1], row, col]
                    R668 = self.in_raster[self.NDVI_bands[0], row, col]

                    try:
                        NDVI_raster[:, row, col] = float(R827-R668)/float(R827+R668)

                    except ZeroDivisionError:
                        NDVI_raster[:, row, col] = 0.0

                    self.prgbar_process(pixel_no=row * self.ncols + col)

                if NDVI_raster[:, row, col] > 0.85:
                    break
            else:
                continue
            break

        self.max_index = np.unravel_index(np.nanargmax(NDVI_raster), NDVI_raster.shape)

        return self.max_index


    def prgbar_process(self, pixel_no):
        if self.prg:
            if self.prg.gui.lblCancel.text() == "-1":  # Cancel has been hit shortly before
                self.prg.gui.lblCancel.setText("")
                self.prg.gui.cmdCancel.setDisabled(False)
                raise ValueError("Calculation canceled")
            self.prg.gui.prgBar.setValue(pixel_no*100 // self.pixel_total)  # progress value is index-orientated
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
        self.asi_core = ASI_core(nodat_val=None, division_factor=None)
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


