# -*- coding: utf-8 -*-
from hubflow.core import *
import numpy as np
import scipy
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import os
from sklearn.externals import joblib
import gdal
from gdalconst import *
import struct
import warnings

from lmuvegetationapps.Sensor_Info import get_wl

class Functions:

    def __init__(self, main):
        self.m = main
        self.file_ext = None
        self.model_name = None
        self.selecter = None

    def ann(self, X, y, activation, solver, alpha, max_iter=500):
        self.model_name = "ann"
        self.file_ext = ".ann"
        return MLPRegressor(activation=activation, solver=solver, alpha=alpha, max_iter=max_iter).fit(X, y)

class Process:

    def __init__(self, main):
        self.m = main
        self.nbands = None
        self.nrows = None
        self.ncols = None
        self.npara = None

        self.para_dict = {"N": 0, "cab": 1, "car": 2, "anth": 3, "cbrown": 4, "cw": 5, "cm": 6, "cp": 7, "ccl": 8,
                          "LAI": 9, "typeLIDF": 10, "LIDF": 11, "hspot": 12, "psoil": 13, "tts": 14, "tto": 15,
                          "psi": 16, "N2_can4": 17}

        self.conv = {
            "N": ["N", [1.0, 2.2], 1],
            "cab": ["chlorophyll", [10, 80], 1],
            "cw": ["EWT_S", [0.01, 0.007], 1000],
            "cm": ["LMA", [0.0025, 0.006], 1000],
            "LAI": ["greenLAI", [0.0, 8.0], 1],
            "typeLIDF": ["typeLIDF", [1.0, 2.0], 1],
            "LIDF": ["ALIA_S", [10, 80], 1],
            "hspot": ["hspot", [0.0, 0.1], 100],
            "psoil": ["psoil", [0.0, 1.0], 10],
            "tts": ["tts"],
            "tto": ["tto"],
            "psi": ["psi"],
            "cp": ["cp", [0.0, 0.002], 1000],
            "ccl": ["ccl", [0.0, 0.005], 1000],
            "car": ["Car", [0.0, 20.0], 1],
            "anth": ["Canth", [0.0, 5.0], 1],  # Name, ylim/xlim, boost
            "cbrown": ["brown_pigments", [0.0, 1.0], 10],
            "N2_can4": ["N2_can4", [0, 30], 1]}

        self.wl_sensor = {1: 13, 2: 242, 3: 8, 4: 126}

        # 0: 'N', 1: 'cab', 2: 'cw', 3: 'cm', 4: 'LAI', 5: 'typeLIDF', 6: 'LIDF', 7: 'hspot',
        # 8: 'psoil', 9: 'tts', 10: 'tto', 11: 'psi', 12: 'cp', 13: ccl, 14: car, 15: anth, 16: cbrown

    def NDVI(self, red, nir, in_matrix, thr):
        NDVI_out = (in_matrix[:, :, nir] - in_matrix[:, :, red]) / (in_matrix[:, :, nir] + in_matrix[:, :, red])
        NDVI_out = np.nan_to_num(NDVI_out)
        NDVI_out = np.where(NDVI_out > thr, 1, 0)
        return NDVI_out

    def read_image(self, image, dtype=np.float16):  # routine for loading bsq images, no bands are skipped anymore

        dataset = gdal.Open(image)
        self.nbands = dataset.RasterCount
        self.nrows = dataset.RasterYSize
        self.ncols = dataset.RasterXSize

        bands = range(self.nbands)

        in_matrix = np.zeros((self.nrows, self.ncols, self.nbands))
        for i, band in enumerate(bands):
            band = dataset.GetRasterBand(band + 1)
            scancol = band.ReadRaster(0, 0, self.ncols, self.nrows, self.ncols, self.nrows, GDT_Float32)
            in_matrix[:, :, i] = np.reshape(np.asarray(struct.unpack('f' * self.nrows * self.ncols, scancol),
                                                             dtype=dtype), (self.nrows, self.ncols))
        return self.nrows, self.ncols, self.nbands, in_matrix  # return a tuple back to the last function (type "dtype")

    def write_image(self, out_matrix, image_out, whichpara):
        npara = len(whichpara)
        driver = gdal.GetDriverByName('ENVI')
        destination = driver.Create(image_out, self.ncols, self.nrows, npara, gdal.GDT_Float32)
        for i, para in enumerate(whichpara):
            band = destination.GetRasterBand(i+1)
            band.SetDescription(para[0]) # temp! "para[0]" für whichpara=[['LAI']]
            band.WriteArray(out_matrix[:,:,i])
        destination.SetMetadataItem('data ignore value', str(-999), 'ENVI')

    def which_model(self, geometry_matrix, geo):
        nrows = geometry_matrix.shape[0]
        ncols = geometry_matrix.shape[1]
        tts, tto, psi = geo
        whichModel = np.zeros(shape=((nrows, ncols, 3)), dtype=np.int16)

        for row in range(nrows):
            for col in range(ncols):
                # for the supplied geometry: find closest match in LUT
                angles = []
                angles.append(np.argmin(abs(geometry_matrix[row, col, 0] - tts)))  # tts
                angles.append(np.argmin(abs(geometry_matrix[row, col, 1] - tto)))  # tto
                angles.append(np.argmin(abs(geometry_matrix[row, col, 2] - psi)))  # psi
                whichModel[row, col, 0] = angles[2] * len(tto) * len(tts) + angles[1] * len(tts) + angles[0]
        return whichModel

class Application:
    def __init__(self, main):
        self.m = main
        self.global_list = ["LAI", "LIDF", "cab", "car", "anth", "cbrown", "N", "cm", "hspot"]
        self.ann_activation = None
        self.ann_solver = None
        self.ann_max_iter = None
        self.ann_alpha = None
        self.ml_params_dict_ann = None

    def setparams(self, noise=None, para=None):

        #################
        ## Algorithmus ##
        #################

        # Pfad für die Models (entweder zum Abspeichern nach dem Training, oder zum Abruf bei Predictions!)
        self.model_dir = r"E:\ECST_III\Processor\ML\Models\20200320/"
        self.algorithmus = 'ann' # 'ann', 'gpr', 'svr', 'rforest'
        warnings.filterwarnings('ignore')

        ################
        ## Prediction ##
        ################

        # Input Image für die Predictions
        self.ImgIn = r"F:\Flugdaten2/Cali/BA_mosaic_su_cut.bsq"  # Oder hier nur das Subset mit den Felddaten? # Geo fehlt
        self.GeoIn = None

        self.int_boost_geo = 100 # Geometrien von 0 bis 9000 erhalten boost_geo = 100 -> 0° - 90°

        # Output der predicted Variablen
        self.ResOut = r"E:\ECST_III\Processor\ML\Output\20200320\California_BA_summer2.bsq"

        # Von welchem Sensor sind die Daten?
        self.sensor_nr = 2  # 1 = Sentinel, 2 = EnMAP, 3 = Landsat8, 4 = HyMap

        # Sollen NDVI-Werte mit niedrigem Threshold ausgeklammert werden?
        # self.mask_ndvi = {} # Nein
        self.ndvi_thr = 0.05
        self.mask_ndvi = {'red': 47, 'nir': 69, 'thr': self.ndvi_thr}  # Kanal für RED (ca. 668nm), Kanal für NIR (ca. 827nm), Threshold # Hymap: 16, 27 # EnMAP: 47, 69

        # Distribute Geo?
        self.spatial_geo = True

        ##############
        ## Training ##
        ##############

        # Liste an Variablen, die trainiert werden sollen
        self.para_list = para
        self.para_boost = True # scale parameter to range ~0-10 (das verbessert für manche Algorithmen die Qualität der Schätzung)
        self.cv = 7  # neue Version: keine CV mehr

        # Noise
        self.conversion_factor = 10000 # EnMAP: 10000, FieldSpec: 1
        self.noise_type = noise[0]
        self.sigma = noise[1]

        # Soll ein Image als Maske eingelesen werden?
        self.mask_image = None
        # self.mask_image = r"F:\SPARC\SPARC2003/HyMap_AtmCor/Barrax_BC_mask2.bsq"

        self.para_list_flat = [item for sublist in self.para_list for item in sublist]


    def predict_from_dump(self):

        nrows, ncols, nbands, in_matrix = self.m.proc.read_image(image=self.ImgIn, dtype=np.int)  # Todo: hub-API

        with open(self.model_dir + 'ann_mlp_paras.lut', 'r') as mlra_meta:
            metacontent = mlra_meta.readlines()
            metacontent = [line.rstrip('\n') for line in metacontent]
        self.tts = [float(i) for i in metacontent[6].split("=")[1].split(";")]
        self.tto = [float(i) for i in metacontent[7].split("=")[1].split(";")]
        self.psi = [float(i) for i in metacontent[8].split("=")[1].split(";")]

        if self.GeoIn:
            geometry_matrix = self.m.proc.read_geometry(GeoIn=self.GeoIn, int_boost_geo=self.int_boost_geo)
        else:
            geometry_matrix = np.zeros(shape=(nrows,ncols,3))
            geometry_matrix[:,:,0] = 45*self.int_boost_geo  # Todo: Abgreifen der Werte aus der GUI / setparams

        if self.mask_image:
            _, _, _, self.mask = self.m.proc.read_image(image=self.mask_image, dtype=np.int8)

        if not self.spatial_geo:  # get rid of spatial distribution of geometry (tts, tto, psi) within image
            geometry_matrix[geometry_matrix < 0] = np.nan
            geometry_matrix[:, :, 0] = np.nanmean(geometry_matrix[:, :, 0])
            geometry_matrix[:, :, 1] = np.nanmean(geometry_matrix[:, :, 1])
            geometry_matrix[:, :, 2] = np.nanmean(geometry_matrix[:, :, 2])
            # print("Geometry means: ", geometry_matrix[0,0,0], geometry_matrix[0,0,1], geometry_matrix[0,0,2])

        if self.mask_ndvi:
            self.ndvi_mask = self.m.proc.NDVI(red=self.mask_ndvi['red'], nir=self.mask_ndvi['nir'], in_matrix=in_matrix,
                                              thr=self.mask_ndvi['thr'])

        whichModel = self.m.proc.which_model(geometry_matrix=geometry_matrix, geo=(self.tts, self.tto, self.psi))
        self.whichModel_unique = np.unique(whichModel)  # find out, which "whichModels" are actually found in the geo_image

        whichModel_coords = list()

        # Temp!
        # for iwhichModel in self.whichModel_unique:
        #     whichModel_coords.append(np.where((whichModel[:,:,0] == iwhichModel) & (self.mask[:,:,0] > 0) & (self.ndvi_mask > 0))) # add i,j coordinates to list for each whichModel that is not masked

        whichModel_coords.append(np.where((in_matrix[:, :, 0] is not np.nan) & (self.ndvi_mask > 0)))


        # # Öffne das Parameter-Meta File des ML um nachzusehen, welche Parameter antrainiert wurden -> "para"
        # with open(self.model_dir + self.ml_model_name + '_paras.lut', 'r') as para_file:
        #     para = para_file.readline()
        # para_from_ml = para.split(";")
        # if para_from_ml[-1] == '':
        #     del para_from_ml[-1]
        # self.whichpara_dict = dict(zip(para_from_ml, range(len(para_from_ml))))  # Die Reihenfolge muss bekannt sein

        self.whichparas = self.para_list  # Temp Fernerkundung, Diss, bzw. es bleibt fix

        nrows, ncols, nbands = in_matrix.shape
        out_matrix = np.full(shape=(nrows, ncols, len(self.para_list)), fill_value=-999.0)
        out_matrix = self.predict(image=in_matrix, whichModel_coords=whichModel_coords, out_matrix=out_matrix)

        # out_matrix = np.expand_dims(out_matrix, axis=1)
        # print("dims out: ", out_matrix.shape)
        self.m.proc.write_image(out_matrix=out_matrix, image_out=self.ResOut, whichpara=self.para_list)

    def predict(self, image, whichModel_coords, out_matrix):
        nrows, ncols, nbands = image.shape
        image = image.reshape((-1, nbands))  # collapse rows and cols into 1 dimension

        for ipara, para in enumerate(self.whichparas):
            process_dict = joblib.load(self.model_dir + 'ann_mlp_{}.proc'.format(para))
            image_para = np.copy(image)

            if process_dict['log_transform']:
                image_para[image_para > 0] = np.log(1/image_para[image_para > 0])
                image_para[image_para == np.inf] = 0
                # print("Is nan?", np.isnan(image_para).any())  # For debugging
                # print("Nans:", np.argwhere(np.isnan(image_para)))

            if process_dict['scaler']:
                image_para = process_dict['scaler'].transform(image_para)

            if process_dict['pca']:
                image_para = process_dict['pca'].transform(image_para)

            nbands_para = image_para.shape[1]  # nr. of bands may have changed (select, pca)

            # Temp
            image_para = image_para.reshape((nrows, ncols, nbands_para))  # back into 2D-shape

            n_geo = len(self.tts) * len(self.tto) * len(self.psi)

            mod = list()
            for igeo in range(n_geo):
                mod.append(joblib.load(self.model_dir + 'ann_mlp_{:d}_{}.ann'.format(igeo, para)))

            # Temp
            for i_imodel, imodel in enumerate(self.whichModel_unique):
                if whichModel_coords[i_imodel][0].size == 0:
                    continue  # after masking, not all 'imodels' are present in the image
                result = mod[imodel].predict(image_para[whichModel_coords[i_imodel][0], whichModel_coords[i_imodel][1], :])
                out_matrix[whichModel_coords[i_imodel][0], whichModel_coords[i_imodel][1], ipara] = result / self.m.proc.conv[para][2]

            # result = mod[0].predict(image_para).reshape((nrows, ncols))
            # out_matrix[:, :, ipara] = result / self.m.proc.conv[para][2]

        return out_matrix


class MainFunction:
    def __init__(self):
        self.func = Functions(self)
        self.proc = Process(self)
        self.app = Application(self)

if __name__ == '__main__':
    m = MainFunction()
    para = ['LAI', 'LIDF', 'cm', 'cab'] # Predict
    m.app.setparams(noise=[1, 4], para=para)
    m.app.predict_from_dump()
