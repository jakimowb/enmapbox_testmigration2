# -*- coding: utf-8 -*-

import gdal
from gdalconst import *
import numpy as np
import struct

from scipy.optimize import minimize
from scipy.interpolate import interp1d

# ======================================================================================================================
# function definitions
# ======================================================================================================================

class PWR_core:

    def __init__(self, nodat_val):
        self.nodat_val = nodat_val
        self.initial_values()

    def initial_values(self):
        self.wavelengths = None
        self.abs_coef = None
        self.low_lim = None
        self.upp_lim = None
        self.pixel_total = None
        self.nrows, self.ncols, self.nbands, self.in_raster = (None, None, None, None)

    def initialize_PWR(self, input, output, lims, NDVI_th=0.37):
        self.wl, self.nrows, self.ncols, self.nbands, self.in_raster = self.read_image(image=input)
        self.n_wl = len(self.wl)
        self.pixel_total = self.nrows * self.ncols
        self.output = output
        self.low_lim, self.upp_lim = (self.find_closest(lambd=lims[0]), self.find_closest(lambd=lims[1]))
        self.NDVI_th = NDVI_th

        content = np.genfromtxt("water_absorp_coef.txt", skip_header=True)
        wl = [int(content[i, 0]) for i in range(len(content[:, 0]))]
        abs_coef = content[:, 1]
        n_wl = len(wl)
        self.get_abscoef = dict(zip(wl, abs_coef))  # Dictionary mapping wavelength to absorption coefficient

        # self.wl_closest = [self.find_closest(wl[i]) for i in xrange(n_wl) if wl[i] >= self.low_lim and wl[i] <= self.upp_lim] # wavelengths used for inversion that exist in image
        # self.wl_closest = sorted(list(set(self.wl_closest)))

        self.valid_wl = [self.wl[i] for i in xrange(self.n_wl) if self.wl[i] >= self.low_lim and self.wl[i] <= self.upp_lim]
        self.valid_bands = [i for i, x in enumerate(self.wl) if x in self.valid_wl]  # indices of input image bands used
        self.abs_coef = np.asarray([self.get_abscoef[self.valid_wl[i]] for i in xrange(len(self.valid_wl))]) # abs coefficients of water for bands used

        NDVI_closest = [self.find_closest(lambd=827), self.find_closest(lambd=668)]
        self.NDVI_bands = [i for i,x in enumerate(self.wl) if x in NDVI_closest]


    def read_image(self, image, dtype=np.float32):
        '''
        :param image: ENVI-grid with spectral information
        :param dtype: deprecated
        :return: matrix(rows, cols, nbands, reflectances)
        '''

        dataset = gdal.Open(image)
        nbands = dataset.RasterCount
        nrows = dataset.RasterYSize
        ncols = dataset.RasterXSize

        in_matrix = np.zeros((nrows, ncols, nbands))

        for band_no in xrange(nbands):
            band = dataset.GetRasterBand(band_no + 1)
            scancol = band.ReadRaster(0, 0, ncols, nrows, ncols, nrows, GDT_Float32)
            in_matrix[:, :, band_no] = np.reshape(np.asarray(struct.unpack('f' * nrows * ncols, scancol),
                                                             dtype=np.float32), (nrows, ncols))
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
        elif dataset.GetMetadataItem('wavelength_units', 'ENVI').lower() in ['micrometers', 'µm', 'micrometer']:
            wave_convert = 1000
        else:
            raise ValueError("Wavelength units must be nanometers or micrometers. Got '%s' instead" % dataset.GetMetadataItem('wavelength_units', 'ENVI'))

        wl = [float(item) * wave_convert for item in wavelengths]

        return wl, nrows, ncols, nbands, in_matrix

    def find_closest(self, lambd):
        distances = [abs(lambd - self.wl[i]) for i in range(self.n_wl)]  # Get distances of input WL to all sensor WLs
        return self.wl[distances.index(min(distances))]

    def NDVI(self, row, col):
        R827 = self.in_raster[row,col,self.NDVI_bands[1]]
        R668 = self.in_raster[row,col,self.NDVI_bands[0]]

        try:
            ndvi = float(R827-R668)/float(R827+R668)
        except ZeroDivisionError:
            ndvi = 0.0

        return ndvi

    def execute_PWR(self, prg_widget=None, QGis_app=None):
        self.prg = prg_widget
        self.QGis_app = QGis_app
        res_raster = np.zeros([self.nrows, self.ncols])  # result raster of minimized d-values
        for row in range(self.nrows):
            for col in range(self.ncols):
                if self.NDVI(row=row, col=col) < self.NDVI_th:
                    res_raster[row, col] = self.nodat_val[1]
                    continue
                d = 0.0  # initial d-value for minimization algorithm
                res = minimize(self.lambert_beer_ob_fun, d, args=[row, col], method='Nelder-Mead', tol=1e-6)
                res = res.x / 10.0 # conversion to cm
                res_raster[row, col] = res
                self.prgbar_process(pixel_no=row*self.nrows+col)

        res_raster[np.isnan(res_raster)] = self.nodat_val[1]

        return res_raster

    def lambert_beer_ob_fun(self, d, *args):
        '''
        :param d: spectrally active waterlayer in [mm]
        :param args: init: rows and cols
        :return: minimization of ssr (sum of squared residuals)
        '''
        row = args[0][0]
        col = args[0][1]

        r = self.in_raster[row, col, self.valid_bands] / (np.exp(-1 * self.abs_coef * d))
        slope = (r[-1] - r[0]) / (len(r) - 0)
        intercept = r[0]
        residuals = (slope * np.arange(0, len(r)) + intercept) - r[0:]
        ssr = np.nansum((residuals) ** 2)
        return ssr

    def write_image(self, result):
        driver = gdal.GetDriverByName('ENVI')

        destination = driver.Create(self.output, self.ncols, self.nrows, 1, gdal.GDT_Float32)
        band = destination.GetRasterBand(1)
        band.SetDescription("Plant Active Water")
        band.WriteArray(result)
        destination.SetMetadataItem('data ignore value', str(self.nodat_val[1]), 'ENVI')

        out_raster = None
        driver = None

    def prgbar_process(self, pixel_no):
        if self.prg:
            if self.prg.gui.lblCancel.text() == "-1": # Cancel has been hit shortly before
                self.prg.gui.lblCancel.setText("")
                self.prg.gui.cmdCancel.setDisabled(False)
                raise ValueError("Calculation of Plant Water canceled")
            self.prg.gui.prgBar.setValue(pixel_no*100 // (self.pixel_total)) # progress value is index-orientated
            self.prg.gui.lblCaption_l.setText("Calculating Water Content")
            self.prg.gui.lblCaption_r.setText("pixel %i of %i" % (pixel_no, self.pixel_total))
            self.QGis_app.processEvents() # mach ma neu

if __name__ == '__main__':
    pass