# -*- coding: utf-8 -*-

import numpy as np
import time
import gdal
from gdalconst import *
from osgeo import gdal
import struct
import os
from Sensor_Info import get_wl
import winsound


class RTM_Inversion:

    def __init__(self):
        self.error = None
        self.ctype = 0
        self.nbfits = 0
        self.noisetype = 0
        self.noiselevel = 0
        self.nodat = [0]*3
        self.exclude_bands, self.exclude_bands_model = (None, None)
        self.wl_sensor = None
        self.fwhm_sensor = None
        self.wl_compare = None
        self.n_wl = None
        self.offset = 0
        self.image = None
        self.image_out = None
        self.npara = None
        self.conversion_factor = None

        self.nrows, self.ncols, self.nbands = (None, None, None)
        self.geometry_matrix = None
        self.whichLUT = None
        self.LUT_base = None
        self.exclude_pixels = None
        self.whichpara = None

        # LUT:
        self.ntotal = None
        self.ns = None
        self.tts_LUT, self.tto_LUT, self.psi_LUT, self.nangles_LUT = (None, None, None, None)

        self.para_dict = {0: 'N', 1: 'cab', 2: 'cw', 3: 'cm', 4: 'LAI', 5: 'typeLIDF', 6: 'LIDF', 7: 'hspot',
                          8: 'psoil', 9: 'tts', 10: 'tto', 11: 'psi', 12: 'car', 13: 'anth', 14: 'cbrown'}
        self.para_names = [self.para_dict[i] for i in xrange(len(self.para_dict))]

    def read_image(self, image, nodat, dtype=np.float16, exclude_bands=[]):

        dataset = gdal.Open(image)
        nbands = dataset.RasterCount
        nrows = dataset.RasterYSize
        ncols = dataset.RasterXSize

        in_matrix = np.zeros((nrows, ncols, nbands-len(exclude_bands)))
        skip = 0

        for band_no in xrange(nbands):
            if band_no in exclude_bands:
                skip += 1
                continue
            band = dataset.GetRasterBand(band_no+1)
            scancol = band.ReadRaster(0,0, ncols, nrows, ncols, nrows, GDT_Float32)
            in_matrix[:, :, band_no-skip] = np.reshape(np.asarray(struct.unpack('f' * nrows * ncols, scancol),
                                                             dtype=dtype), (nrows, ncols))

        return nrows, ncols, nbands, in_matrix

    def get_geometry(self, geo_fixed, geo_image=None):

        #0: Generate geometry matrix
        self.geometry_matrix = np.empty(shape=(self.nrows, self.ncols, 3))
        self.geometry_matrix.fill(self.nodat[0])

        #1: import geometry-file from read_image or
        if geo_image:
            geometry_raw = self.read_image(geo_image, nodat=self.nodat[0])
            if not geometry_raw[0] == self.nrows or not geometry_raw[1] == self.ncols:
                exit("Geometry image and Sensor image do not match")
            self.geometry_matrix = geometry_raw[3]/100

        if not all(v is None for v in geo_fixed):
            for angle in xrange(3):
                if not geo_fixed[angle] is None:
                    self.geometry_matrix[:,:,angle] = geo_fixed[angle]

        try:
            self.geometry_matrix[0,0,0]
        except:
            exit("No geometry supplied")

        self.whichLUT = np.zeros(shape=(self.nrows, self.ncols),dtype=np.int16)

        for row in xrange(self.nrows):
            for col in xrange(self.ncols):
                angles = []
                angles.append(np.argmin(abs(self.geometry_matrix[row,col,0] - self.tts_LUT))) # tts
                angles.append(np.argmin(abs(self.geometry_matrix[row,col,1] - self.tto_LUT))) # tto
                angles.append(np.argmin(abs(self.geometry_matrix[row,col,2] - self.psi_LUT))) # psi
                self.whichLUT[row,col] = angles[2]*self.nangles_LUT[1]*self.nangles_LUT[0] + angles[1]*self.nangles_LUT[0] + angles[0]

    def add_noise(self, Ref_list, type, sigma):
        n_entries = len(Ref_list)
        sigma_c = (sigma/100) * self.conversion_factor  # sigma converted

        if type == 0: # no noise
            return Ref_list

        elif type == 1:  # additive noise
            Ref_noisy = [Ref_list[i] + np.random.normal(loc=0.0, scale=sigma_c) for i in xrange(n_entries)]
            # Ref_noisy = [Ref_noisy[i]*10 for i in xrange(len(Ref_noisy))]

        elif type == 2:  # multiplicative noise
            Ref_noisy = [Ref_list[i] * (1 + np.random.normal(loc=0.0, scale=sigma / 100)) for i in xrange(n_entries)]

        elif type == 3:  # inverse multiplicative noise
            Ref_noisy = [1 - ((1 - Ref_list[i]) * (1 + np.random.normal(loc=0.0, scale=sigma / 100))) for i in
                         xrange(n_entries)]

        Ref_noisy = [Ref_noisy[i] if Ref_noisy[i] > 0.0 else 0.1 for i in xrange(n_entries)]

        return Ref_noisy

    def visualize(self):
        #1: get wl and array with reflectances
        #2: 1dim array: plot single; 2dim: plot multiple
        pass

    def cost_fun(self, image_Ref, model_Ref, type):

        if type == 1: # RMSE
            delta = np.linalg.norm(model_Ref - image_Ref) / np.sqrt(self.n_wl)  # Numpy-Solution für RMSE (fast)
        elif type == 2: # MAE
            delta = sum(abs(image_Ref - model_Ref))
        elif type == 3: # mNSE
            delta = 1.0 - ((sum(abs(image_Ref - model_Ref))) /
                           (sum(abs(image_Ref - (np.mean(image_Ref))))))
        else:
            exit("wrong cost function type. Expected 1, 2 or 3; got %i instead" %type)

        return delta

    def inversion_setup(self, image, image_out, LUT_path, ctype, nbfits, nbfits_type, noisetype, noiselevel,
                        exclude_bands, out_mode, geo_image=None, geo_fixed=[None]*3, sensor=2,
                        nodat=[-999]*3, mask_image=None, which_para=range(15)):

        self.ctype = ctype
        self.nbfits = nbfits
        self.nbfits_type = nbfits_type
        self.noisetype = noisetype
        self.noiselevel = noiselevel
        self.exclude_bands = exclude_bands

        self.conversion_factor = 10000
        self.nodat = nodat
        self.out_mode = out_mode

        self.whichpara = which_para
        self.npara = len(which_para)
        self.image_out = image_out
        self.sensor_setup(sensor=sensor)
        self.nrows, self.ncols, self.nbands, self.image = self.read_image(image=image, nodat=nodat[1], dtype=np.float16,
                                                                          exclude_bands=self.exclude_bands)
        if mask_image is None:
            self.exclude_pixels = []
        else:
            self.masking(img=mask_image)
            if self.exclude_pixels is None: # Error within self.masking -> self.exclude_pixels is still None
                return self.error

        self.get_meta(LUT_path)
        self.get_geometry(geo_image=geo_image, geo_fixed=geo_fixed)  # generate list of LUT-names for each pixel

        self.out_matrix = np.empty(shape=(self.nrows, self.ncols, len(self.whichpara)))

    def masking(self, img):
        mask = self.read_image(img, nodat=-999)
        if not self.nrows == mask[0] or not self.ncols == mask[1]:
            self.error = "Input Image and Mask Image must have same dimensions! Input Image has [%ir, %ic], " \
                         "Mask Image has [%ir, %ic]" % (self.nrows, self.ncols, mask[0], mask[1])
            return
        self.exclude_pixels = np.squeeze(mask[3], axis=2) # turns [r,c,1] (1 band) into [r,c]

    def sensor_setup(self, sensor):
        self.wl_sensor, self.fwhm_sensor = get_wl(sensor=sensor)

        if sensor == 1: # ASD
            self.offset = 400 - self.wl_sensor[0]  # 400nm as first wavelength in the PROSAIL model family
            # self.exclude_bands = range(0, self.offset) + range(1009, 1129) + range(1371, 1650) # 350-400nm, 1359-1479nm, 1721-200nm
            self.exclude_bands_model = range(self.npara) + [((i - self.offset)) + self.npara for i in self.exclude_bands[self.offset:]]
        elif sensor == 2: # EnMAP
            # self.exclude_bands = range(78, 88) + range(128, 138) + range(161, 189) # Überlappung VNIR, Water1, Water2
            self.exclude_bands_model = range(self.npara) + [i + self.npara for i in self.exclude_bands]
        elif sensor == 3: # Sentinel-2
            # self.exclude_bands = [10]
            self.exclude_bands_model = range(self.npara) + [i + self.npara for i in self.exclude_bands]

        self.wl_compare = [self.wl_sensor[i] for i in xrange(len(self.wl_sensor)) if i not in self.exclude_bands]
        self.n_wl = len(self.wl_compare)

    def get_meta(self, file):

        with open(file, 'r') as metafile:
            metacontent = metafile.readlines()
            metacontent = [line.rstrip('\n') for line in metacontent]

        self.LUT_base = os.path.dirname(file) + "/" + metacontent[0].split("=")[1]
        self.ntotal = int(metacontent[1].split("=")[1])
        self.ns = int(metacontent[2].split("=")[1])
        temp = metacontent[3].split("=")[1].split(";")
        self.tts_LUT = [float(angle) for angle in temp[:-1]]
        temp = metacontent[4].split("=")[1].split(";")
        self.tto_LUT = [float(angle) for angle in temp[:-1]]
        temp = metacontent[5].split("=")[1].split(";")
        self.psi_LUT = [float(angle) for angle in temp[:-1]]

        self.nangles_LUT = [len(self.tts_LUT), len(self.tto_LUT), len(self.psi_LUT)]
        if self.nbfits_type == "rel":
            self.nbfits = int(self.ns * (self.nbfits/100.0))

    def run_inversion(self, prg_widget=None, QGis_app=None):

        pix_total = self.nrows * self.ncols
        for r in xrange(self.nrows):
            for c in xrange(self.ncols):

                pix_current = r*self.ncols + c + 1
                print "row: %i | col: %i" % (r, c)

                # Check if Pixel shall be excluded
                if len(self.exclude_pixels) > 0 and self.exclude_pixels[r,c] < 1:
                    self.out_matrix[r,c,:] = self.nodat[2]

                # Check if valid geometry exists:
                if any(self.geometry_matrix[r,c,i] for i in xrange(3)) == self.nodat[0]:
                    self.out_matrix[r,c,:] = self.nodat[2]

                estimates = np.zeros(self.ns)
                lut = np.load(self.LUT_base + "_" + str(self.whichLUT[r,c])+".npy")
                LUT_params = lut[0:15,:] # extract parameters
                lut = np.delete(lut, self.exclude_bands_model, axis=0) # delete exclude_bands_model - members

                # works only if files are separated by nstatistical (for each geometry)
                for run in xrange(self.ns):
                    if np.sum(lut[:,run]) < 1: continue
                    estimates[run] = self.cost_fun(self.image[r,c,:],
                                                   self.add_noise(Ref_list=lut[:,run], type=self.noisetype, sigma=self.noiselevel),
                                                   type=self.ctype)

                L1_subset = np.argpartition(estimates, self.nbfits)[0:self.nbfits] # get n best performing LUT-entries
                L1_subset = L1_subset[np.argsort(estimates[L1_subset])]
                result = np.median([LUT_params[:,i] for i in L1_subset], axis=0)

                self.out_matrix[r,c,:] = result
                if prg_widget:
                    prg_widget.gui.lblCaption_r.setText('Inverting pixel #%i of %i' % (pix_current, pix_total))
                    prg_widget.gui.prgBar.setValue(pix_current*100 // pix_total)
                    QGis_app.processEvents()


    def write_image(self):
        driver = gdal.GetDriverByName('ENVI')

        if self.out_mode == "single":
            destination = driver.Create(self.image_out, self.ncols, self.nrows, self.npara, gdal.GDT_Float32)
            for i in xrange(self.npara):
                band = destination.GetRasterBand(i+1)
                band.SetDescription(self.para_names[self.whichpara[i]])
                band.WriteArray(self.out_matrix[:,:,i])
            destination.SetMetadataItem('data ignore value', '-999', 'ENVI')

        elif self.out_mode == "individual":
            for i in xrange(self.npara):
                out = os.path.splitext(self.image_out)[0] + "_" + self.para_names[self.whichpara[i]] + os.path.splitext(self.image_out)[1]
                destination = driver.Create(out, self.ncols, self.nrows, 1, gdal.GDT_Float32)
                band = destination.GetRasterBand(1)
                band.SetDescription(self.para_names[self.whichpara[i]])
                band.WriteArray(self.out_matrix[:,:,i])
                destination.SetMetadataItem('data ignore value','-999','ENVI')
        
def example():
    ImageIn = "D:/ECST_II/Cope_BroNaVI/WW_nadir_short.bsq"
    ResultsOut = "D:/ECST_III/Processor/VegProc/results.bsq"
    GeometryIn = "D:/ECST_II/Cope_BroNaVI/Felddaten/Parameter/Geometry_DJ_w.bsq"
    LUT_dir = "D:/ECST_III/Processor/VegProc/results2/"
    LUT_name = "Martin_LUT4"
    
    # global Inversion input:
    costfun_type = 1
    nbest_fits = 5.0
    noisetype = 2
    noiselevel = 5.0 # percent
    sensor = 1 # ASD
    nodat_Geo = -999
    nodat_Image = -999
    nodat_Out = -999
    inversion_range = None
    
    # Fixed Geometry
    tts = None
    tto = None
    psi = None
    geometry_fixed = [tts, tto, psi]
    
    rtm = RTM_Inversion()
    rtm.inversion_setup(image=ImageIn, image_out=ResultsOut, LUT_dir=LUT_dir, LUT_name=LUT_name, ctype=costfun_type,
                     nbfits=nbest_fits, noisetype=noisetype, noiselevel=noiselevel, inversion_range=inversion_range,
                     geo_image=GeometryIn, geo_fixed=geometry_fixed, sensor=sensor, exclude_pixels=None,
                     nodat=[nodat_Geo, nodat_Image, nodat_Out], which_para=range(15))
    
    rtm.run_inversion()
    rtm.write_image()


if __name__ == '__main__':
    # print(example_single() / 1000.0)
    # plt.plot(range(len(example_single())), example_single() / 1000.0)
    # plt.show()
    example()