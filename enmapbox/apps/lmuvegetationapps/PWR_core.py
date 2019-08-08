# -*- coding: utf-8 -*-
from hubflow.core import *
from hubdc.core import *
import gdal
from gdalconst import *
import numpy as np
import struct
import os

from scipy.optimize import minimize_scalar
from scipy.interpolate import interp1d
from numba import jit

# ======================================================================================================================
# function definitions
# ======================================================================================================================


class PWR_core:

    def __init__(self, nodat_val, division_factor):
        self.nodat_val = nodat_val
        self.division_factor = division_factor
        self.initial_values()

    def initial_values(self):
        self.wavelengths = None
        self.abs_coef = None
        self.low_lim = None
        self.upp_lim = None
        self.pixel_total = None
        self.grid, self.nrows, self.ncols, self.nbands, self.in_raster = \
            (None, None, None, None, None)

    def initialize_PWR(self, input, output, lims, NDVI_th=0.0):
        self.grid, self.wl, self.nbands, self.nrows, self.ncols, self.in_raster = \
            self.read_image2(image=input)

        #print(self.grid)

        self.n_wl = len(self.wl)
        self.pixel_total = self.nrows * self.ncols
        self.output = output
        self.low_lim, self.upp_lim = (self.find_closest(lambd=lims[0]), self.find_closest(lambd=lims[1]))
        self.NDVI_th = NDVI_th

        absorption_file = os.path.join(os.path.dirname(__file__), 'water_abs_coeff.txt')
        content = np.genfromtxt(absorption_file, skip_header=True)
        wl = [int(content[i, 0]) for i in range(len(content[:, 0]))]
        abs_coef = content[:, 1]
        # n_wl = len(wl)
        self.get_abscoef = dict(zip(wl, abs_coef))  # Dictionary mapping wavelength to absorption coefficient

        # self.wl_closest = [self.find_closest(wl[i]) for i in range(n_wl) if wl[i] >= self.low_lim and wl[i] <= self.upp_lim] # wavelengths used for inversion that exist in image
        # self.wl_closest = sorted(list(set(self.wl_closest)))

        self.valid_wl = [self.wl[i] for i in range(self.n_wl) if
                         self.wl[i] >= self.low_lim and self.wl[i] <= self.upp_lim]
        self.valid_wl = [int(round(i, 0)) for i in self.valid_wl]

        # if len(self.wl) == 242:  # check if input image is EnMAP data
        #
        #     self.valid_wl = np.array(self.valid_wl)
        #
        #     # remove EnMAP wavelength overlap (only take wavelength bands of SWIR Detector)
        #     index_drop = np.where(np.diff(self.valid_wl) < 0)[0] + 1
        #     index_low = np.argmin(self.valid_wl < self.valid_wl[index_drop])
        #     self.valid_wl = np.delete(self.valid_wl, np.arange(index_low, index_drop))
        #
        #     wl_enmap_corr = np.delete(self.wl, 82)  # delete band 82 (944 nm) to avoid duplicate using enumerate
        #
        #     self.valid_bands = [i for i, x in enumerate(wl_enmap_corr) if x in list(self.valid_wl)]
        #else:
        self.valid_bands = [i for i, x in enumerate(self.wl) if x in list(self.valid_wl)]  # indices of input image bands used

        self.abs_coef = np.asarray([self.get_abscoef[self.valid_wl[i]] for i in range(len(self.valid_wl))]) # abs coefficients of water for bands used

        NDVI_closest = [self.find_closest(lambd=827), self.find_closest(lambd=668)]
        self.NDVI_bands = [i for i, x in enumerate(self.wl) if x in NDVI_closest]

    def read_image2(self, image):
        '''
        :param image:
        :return:
        '''
        dataset = openRasterDataset(image)

        grid = dataset.grid()
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
            raise ValueError("Wavelength units must be nanometers or micrometers. Got '%s' instead" % metadict['ENVI']['wavelength units'])

        in_matrix = dataset.readAsArray()
        
        if self.division_factor != 1.0:
            in_matrix = in_matrix / self.division_factor
            
        wl = [float(item) * wave_convert for item in wave_dict]
        wl = [int(i) for i in wl]

        return grid, wl, nbands, nrows, ncols, in_matrix

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
        #print(dataset.GetMetadata)
        #print(dataset.GetMetadataItem('wavelength', 'ENVI'))
        try:
            wavelengths = "".join(dataset.GetMetadataItem('wavelength', 'ENVI').split())
            wavelengths = wavelengths.replace("{", "")
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

        in_matrix = np.zeros((nbands, nrows, ncols))

        for band_no in range(nbands):
            band = dataset.GetRasterBand(band_no + 1)
            scancol = band.ReadRaster1(0, 0, ncols, nrows, ncols, nrows, GDT_Float32)
            in_matrix[band_no, :, :] = np.reshape(np.asarray(struct.unpack('f' * nrows * ncols, scancol),
                                                             dtype=np.float32), (nrows, ncols))

        if self.division_factor != 1.0:
            in_matrix = in_matrix / self.division_factor

        wl = [float(item) * wave_convert for item in wavelengths]
        wl = [int(round(item, 0)) for item in wl]

        return wl, nbands, nrows, ncols, in_matrix

    def find_closest(self, lambd):
        distances = [abs(lambd - self.wl[i]) for i in range(self.n_wl)]  # Get distances of input WL to all sensor WLs
        #print(self.wl[distances.index(min(distances))])
        return self.wl[distances.index(min(distances))]

    def NDVI(self, row, col):
        R860 = self.in_raster[self.NDVI_bands[1], row, col]
        R1240 = self.in_raster[self.NDVI_bands[0], row, col]

        try:
            NDVI = float(R860-R1240)/float(R860+R1240)
        except ZeroDivisionError:
            NDVI = 0.0

        return NDVI
    
    #@jit(nopython=True)
    def execute_PWR(self, prg_widget=None, QGis_app=None):
        self.prg = prg_widget
        self.QGis_app = QGis_app
        res_raster = np.zeros([1, self.nrows, self.ncols])  # result raster of minimized d-values
        d = 0.0
        for row in range(self.nrows):
            for col in range(self.ncols):
                if self.NDVI(row=row, col=col) < self.NDVI_th:
                    res_raster[:, row, col] = self.nodat_val[1]
                    continue
                  # initial d-value for minimization algorithm
                res = minimize_scalar(self.lambert_beer_ob_fun, d, args=[row, col], method='bounded', bounds=(0.0, 1.0))
                res = res.x  # result in [cm] optically active water
                res_raster[:, row, col] = res
                self.prgbar_process(pixel_no=row*self.ncols+col)

        res_raster[np.isnan(res_raster)] = self.nodat_val[1]
        #print(res_raster.shape)
        #print(res_raster)
        return res_raster
    
    def lambert_beer_ob_fun(self, d, *args):
        '''
        :param d: spectrally active waterlayer in [mm]
        :param args: init: rows and cols
        :return: minimization of ssr (sum of squared residuals)
        '''
        row = args[0][0]
        col = args[0][1]

        const_a = 3.523431  # empirical constant (calibrated using 50.000 PROSPECT spectra)

        r = self.in_raster[self.valid_bands, row, col] / (np.exp(-1 * self.abs_coef * d * const_a))
        slope = (r[-1] - r[0]) / (len(r) - 0)
        intercept = r[0]
        residuals = (slope * np.arange(0, len(r)) + intercept) - r[0:]
        ssr = np.nansum(abs(residuals))
        return ssr

    def write_image(self, result):

        output = Raster.fromArray(array=result, filename=self.output, grid=self.grid)

        output.dataset().setMetadataItem('data ignore value', self.nodat_val[1], 'ENVI')

        for band in output.dataset().bands():
            band.setDescription('Plant Active Water [cm]')
            band.setNoDataValue(self.nodat_val[1])


        # driver = gdal.GetDriverByName('ENVI')
        #
        # destination = driver.Create(self.output, self.ncols, self.nrows, 1, gdal.GDT_Float32)
        # band = destination.GetRasterBand(1)
        # band.SetDescription("Plant Active Water")
        # band.WriteArray(result)
        # destination.SetMetadataItem('data ignore value', str(self.nodat_val[1]), 'ENVI')
        #
        # destination = None
        # driver = None

    def prgbar_process(self, pixel_no):
        if self.prg:
            if self.prg.gui.lblCancel.text() == "-1":  # Cancel has been hit shortly before
                self.prg.gui.lblCancel.setText("")
                self.prg.gui.cmdCancel.setDisabled(False)
                raise ValueError("Calculation of Plant Water canceled")
            self.prg.gui.prgBar.setValue(pixel_no*100 // self.pixel_total)  # progress value is index-orientated
            self.prg.gui.lblCaption_l.setText("Calculating Water Content")
            self.prg.gui.lblCaption_r.setText("pixel %i of %i" % (pixel_no, self.pixel_total))
            self.QGis_app.processEvents()  # mach ma neu

if __name__ == '__main__':
    #pass
    PWR = PWR_core(division_factor=1, nodat_val=-9999)
    image = PWR.read_image2("Z:/2018_MNI_campaign\EnMAP\EnMAP_Tetris_Pixel\multi_year_sets\MA_0_2017_2018.bsq")
    test = PWR.initialize_PWR(image, output="Z:/2018_MNI_campaign\EnMAP/", lims=[930, 1060])
    #out = PWR.write_image("Z:\Matthias/test.bsq")

