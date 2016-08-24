__author__ = 'geo_beja'


import pickle
import os,sys, re, copy
from osgeo import gdal, osr, ogr, gdal_array

#import GDAL_Helper
import sklearn.svm
import inspect
import sklearn.ensemble
import numpy as np
import rios, rios.applier
import itertools
import time
import six
import matplotlib
#from bj import stuff, GDAL_Helper

def dTimeString(t0):
    return (np.datetime64('now') - t0).astype(str)



class GDAL_Helper(object):
    """
    A tiny class with static routines that support GDAL data access
    The functions here are a subset of GDAL_Helper.py
    """
    @staticmethod
    def readNoDataValue(ds):
        return GDAL_Helper.readNoDataValues(ds)[0]

    @staticmethod
    def readNoDataValues(ds):
        ds = GDAL_Helper._getDS(ds)
        bn = []
        for b in range(1, ds.RasterCount+1):
            bn.append(ds.GetRasterBand(b).GetNoDataValue())
        return bn

    @staticmethod
    def SaveArray(array, path, format='ENVI', prototype=None, \
                  no_data=None, \
                  class_names=None, class_colors=None, \
                  band_names=None):

        assert path is not None

        nb, nl, ns = get_array_dims(array)

        if prototype is None:
            pt = None
        else:
            pt = GDAL_Helper._getDS(prototype)
            pt_class_names, pt_class_colors = GDAL_Helper.readClassInfos(pt)
            if class_names is None:
                class_names = pt_class_names
            if class_colors is None:
                class_colors = pt_class_colors
            if band_names is None:
                pt_band_names = GDAL_Helper.readBandNames(pt)
                if nb == len(pt_band_names):
                    band_names = pt_band_names


        print('Write {}...'.format(path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        gdal_array.SaveArray(array, path, format=format, prototype=pt)

        ds = gdal.Open(path)
        #set metadata
        if no_data is not None:
            GDAL_Helper.setNoDataValue(ds, no_data)

        if band_names is not None:
            GDAL_Helper.setBandNames(ds, band_names)

        has_categorical_data = class_names is not None or class_colors is not None
        if has_categorical_data:
            GDAL_Helper.setClassificationInfo(ds, class_names, label_colors=class_colors)

        ds.FlushCache()
        return ds

    @staticmethod
    def readDimensions(ds):
        ds = GDAL_Helper._getDS(ds)
        return ds.RasterXSize, ds.RasterYSize, ds.RasterCount


    @staticmethod
    def setClassificationInfo(ds, label_names, label_values=None, label_colors=None, b=1):
        """
        Adds the classification scheme to an image.
        :param ds: gdal.Dataset or path to raster image.
        :param label_names: label names, corresponding to
        :param label_values: the class integer value. By default [0,1,... nclasses-1]
        :param label_colors: list of RGB or RGBA tuples. By default a rainbow color stretch is used with label 0 = black.
        :param b: band number of the raster band to append the categorical labels.
        :return:
        """
        ds = GDAL_Helper._getDS(ds)

        band = ds.GetRasterBand(b)
        assert b is not None

        n = len(label_names)

        if label_colors:
            assert len(label_colors) == n
            for i, c in enumerate(label_colors):
                v = list(c)
                if len(v) == 3:
                    v.append(255) #add alpha dimension
                assert len(v) == 4, 'Color tuple has {} values'.format(len(v))
                label_colors[i] = tuple(v)
        else:
            import matplotlib.cm
            label_colors = list()
            cmap = matplotlib.cm.get_cmap('brg', n)
            for i in range(n):
                if i == 0:
                    c = (0,0,0, 255)
                else:
                    c = tuple([int(255*c) for c in cmap(i)])
                label_colors.append(c)


        if label_values:
            assert len(label_values) == n
        else:
            label_values = [i for i in range(n)]

        CT = gdal.ColorTable()
        names = list()
        for value in sorted(label_values):
            i = label_values.index(value)
            names.append(label_names[i])
            CT.SetColorEntry(value, label_colors[i])

        band.SetCategoryNames(names)
        band.SetColorTable(CT)

        drvName = ds.GetDriver().ShortName
        if drvName == 'ENVI':
            class_lookup = list(itertools.chain.from_iterable([CT.GetColorEntry(i)[0:3] for i in range(CT.GetCount())]))
            ds.SetMetadataItem('class lookup', '{'+','.join(['{}'.format(int(c)) for c in class_lookup])+'}', 'ENVI')



    @staticmethod
    def setBandNames(ds, bandnames):
        ds = GDAL_Helper._getDS(ds)
        assert len(bandnames) == ds.RasterCount
        for i, bandName in enumerate(bandnames):
            ds.GetRasterBand(i+1).SetDescription(bandnames[i])

        drvName = ds.GetDriver().ShortName
        if drvName == 'ENVI':
            bn = GDAL_Helper.readBandNames(ds)
            bn = '{'+','.join(bn)+'}'
            ds.SetMetadataItem('band names', bn , 'ENVI')

    @staticmethod
    def setNoDataValue(ds, no_data):
        ds = GDAL_Helper._getDS(ds)
        for band in [ds.GetRasterBand(b+1) for b in range(ds.RasterCount)]:
            band.SetNoDataValue(no_data)
        if ds.GetDriver().ShortName == 'ENVI':
            if no_data is not None:
                ds.SetMetadataItem('data ignore value', str(no_data), 'ENVI')

        ds.FlushCache()

    @staticmethod
    def readBandNames(ds):
        ds = GDAL_Helper._getDS(ds)
        return [ds.GetRasterBand(i+1).GetDescription() for i in range(ds.RasterCount)]

    @staticmethod
    def get_dataset_properties(ds):
        if type(ds) is str:
            ds = gdal.Open(ds)
        nb = ds.RasterCount
        ns = ds.RasterXSize
        nl = ds.RasterYSize
        b1 = ds.GetRasterBand(1)
        band_names =GDAL_Helper.readBandNames(ds)
        dt = b1.GetDataType()
        no_data = b1.GetNoDataValue()
        return (nb, nl, ns, dt, no_data, band_names)

    @staticmethod
    def _getDS(ds):
        if type(ds) is str:
            ds = gdal.Open(ds)
        return ds

    @staticmethod
    def _check_spatial_size(ds1, ds2):
        ds1 = GDAL_Helper._getDS(ds1)
        ds2 = GDAL_Helper._getDS(ds2)

        assert ds1.RasterXSize == ds2.RasterXSize
        assert ds2.RasterYSize == ds2.RasterYSize

    @staticmethod
    def readClassInfos(ds):
        ds = GDAL_Helper._getDS(ds)
        band = ds.GetRasterBand(1)
        class_names = band.GetCategoryNames()
        ct = band.GetColorTable()

        class_colors = None
        if ct is not None:
            class_colors = list()
            for i in range(ct.GetCount()):
                c = ct.GetColorEntry(i)
                class_colors.append(c)
            if len(class_colors) > len(class_names):
                class_colors = class_colors[0: len(class_names)]
            assert len(class_colors) == len(class_names)
        return class_names, class_colors

    @staticmethod
    def get_image_data(dsF, dsM=None, dsL=None, xoff=None, yoff = None, xsize=None, ysize=None):
        t0 = np.datetime64('now')
        dsF = GDAL_Helper._getDS(dsF)

        if dsM:
            dsM = GDAL_Helper._getDS(dsM)
            GDAL_Helper._check_spatial_size(dsF, dsM)
        if dsL:
            dsL = GDAL_Helper._getDS(dsL)
            GDAL_Helper._check_spatial_size(dsF, dsM)

        #get feature data
        dataF = dsF.ReadAsArray(xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize)
        bandNames = [dsF.GetRasterBand(i+1).GetDescription() for i in range(dsF.RasterCount)]
        no_data_f = dsF.GetRasterBand(1).GetNoDataValue()
        t_features = (dataF, bandNames, no_data_f)

        #get label data
        t_label = None
        if dsL:
            dataL = dsL.GetRasterBand(1).ReadAsArray(xoff=xoff, yoff=yoff, win_xsize=xsize, win_ysize=ysize)
            no_data_l = dsL.GetRasterBand(1).GetNoDataValue()

        #get mask data
        dataM = None
        if dsM:
            dataM = dsM.GetRasterBand(1).ReadAsArray(xoff=xoff, yoff=yoff, win_xsize=xsize, win_ysize=ysize)

        #print('Tile loading ({}/{}) ({}/{})required: {}'.format(xoff, yoff, xsize, ysize, dTimeString(t0)))
        return t_features, t_label, dataM



def _no_rios_apply_files(SM, pathFeatures, pathMask, modelIO, **spatial_kwds):
    t_f, _, src_mask = GDAL_Helper.get_image_data(pathFeatures, dsM=pathMask, **spatial_kwds)
    src_features, src_featurenames, src_nodata = t_f
    src_features, src_mask = SM._homogenize_img_inputdata(src_features, src_featurenames, src_nodata, src_mask, modelIO.masking)
    results = SM.apply_data(src_features, data_mask=src_mask, modelIO=modelIO)
    return results, spatial_kwds

def _rios_apply_files(info, infiles, outfiles, otherargs):
    bx = info.xblock
    by = info.yblock
    bt = info.xtotalblocks * by + bx + 1
    id = '{},{}'.format(bx+1,by+1)
    text = 'Predict tile block {} ({} of {}). Load image data...'.format(id, bt, info.xtotalblocks*info.ytotalblocks)
    #print(text)
    #sys.stdout.write(text)
    t0 = np.datetime64('now')

    SM = SupervisedModel._restore_dump(otherargs.sm)
    #SM = SupervisedModel.restore(otherargs.path_sm)
    modelIO = otherargs.modelio
    src_features, src_featurenames, src_nodata, src_mask = _rios_read_img_data(info, infiles)
    src_features, src_mask = SM._homogenize_img_inputdata(src_features, src_featurenames, src_nodata, src_mask, modelIO.masking)
    #print('Tile block {} loaded in {}'.format(id, dTimeString(t0)))
    results = SM.apply_data(src_features, data_mask=src_mask, modelIO=modelIO)

    for key, data in results.items():
        outfiles.__dict__[key] = data
    #print('All results collected for tile block {}'.format(id))

def _rios_read_img_data(info, infiles):
    ds = info.getGDALDatasetFor(infiles.features)
    src_featurenames = [ds.GetRasterBand(i+1).GetDescription() for i in range(ds.RasterCount)]
    src_nodata = ds.GetRasterBand(1).GetNoDataValue()
    if 'mask' in infiles.__dict__.keys():
        src_mask = infiles.mask
    else:
        src_mask = None
    src_features = infiles.features

    return src_features, src_featurenames, src_nodata, src_mask




def get_array_dims(array):
    if array.ndim == 2:
        nb = 1
        nl, ns = array.shape
    else:
        nb, nl, ns = array.shape
    return nb, nl, ns

def extract_labeled_feature_library(pathSrcImg, pathSrcVec
                                    , label_field, layer_name=None
                                    , pathSrcMsk=None, masked_values=[0], mask_interpretation=False
                                    , pathLibFeatures=None, pathLibLabels=None
                                    , of = 'ENVI'
                                    , missing_label_name ='unclassified', missing_label_value= 0, missing_feature_value=-9999
                                    , squared=True
                                    ):

    #read vector data, extract label names
    drvMemory = ogr.GetDriverByName('Memory')
    drvMEM = gdal.GetDriverByName('MEM')


    assert missing_label_value is not None
    assert missing_label_name is not None
    assert mask_interpretation in [True,False]

    #load entire vector data set into memory (increases processing speed)
    dsVectorFeatures = drvMemory.CopyDataSource(ogr.Open(pathSrcVec), '')
    dsRasterFeatures = GDAL_Helper._getDS(pathSrcImg)
    if missing_feature_value is None:
        missing_feature_value = dsRasterFeatures.GetRasterBand(1).GetNoDataValue()

    if squared:
        assert missing_feature_value is not None



    layer_names = [lyr.GetName() for lyr in dsVectorFeatures]

    if layer_name is None:
        layer_name = layer_names[0]
    else:
        assert layer_name in layer_names, 'Layer "{}" does not exist in {}'.format(layer_name, pathSrcVec)

    #delete all not required layers
    [dsVectorFeatures.DeleteLayer(l) for l in layer_names if l != layer_name]


    lyr_src = dsVectorFeatures.GetLayerByName(layer_name)
    lyr_def = lyr_src.GetLayerDefn()

    field_names = [lyr_def.GetFieldDefn(i).GetName() for i in range(lyr_def.GetFieldCount())]
    assert label_field in field_names, 'Layer "{}" missed field / column "{}"'.format(layer_name, label_field)
    field_def = lyr_def.GetFieldDefn(field_names.index(label_field))


    #collect all n label names. They will be used to define the classification scheme,
    #like:
    #  label_names  = ['unclassified', 'label name 1', 'forest', ... 'last label name']
    #  label_values = [0,1,2,..., n]

    label_names = set()

    field_type = field_def.GetType()
    [label_names.add(feature.GetField(label_field)) for feature in lyr_src]
    lyr_src.ResetReading() #important! because we want to iterate over all features again

    if missing_label_name in label_names:
        label_names.remove(missing_label_name)

    label_names = [missing_label_name] + [str(v) for v in sorted(list(label_names))]
    label_values = [missing_label_value] + list(range(1, len(label_names)))

    #get spatial ref vector layer and raster data set.
    lyr_srs = lyr_src.GetSpatialRef()
    target_srs = osr.SpatialReference()
    target_srs.ImportFromWkt(dsRasterFeatures.GetProjection())
    trans = osr.CoordinateTransformation(lyr_srs, target_srs) #convert vector geometries into raster srs

    #create a temporary vector layer that contains:
    # the feature geometries (in raster data set projection)
    # the raster label value


    tmp_lyr_name = layer_name + '_tmp'
    lyr_tmp = dsVectorFeatures.CreateLayer(tmp_lyr_name, srs = target_srs, geom_type=lyr_def.GetGeomType())
    #add integer field for label values
    lyr_tmp.CreateField(ogr.FieldDefn(label_field, ogr.OFTInteger))
    for feature_src in lyr_src:
        geom = feature_src.GetGeometryRef().Clone()
        geom.Transform(trans)
        feature_tmp = ogr.Feature(lyr_tmp.GetLayerDefn())
        feature_tmp.SetGeometry(geom)

        value_src = feature_src.GetField(label_field)
        value_tmp = label_values[label_names.index(value_src)]
        feature_tmp.SetField(label_field, value_tmp)
        lyr_tmp.CreateFeature(feature_tmp)


    #rasterize the temporary labeled feature layer
    ns = dsRasterFeatures.RasterXSize
    nl = dsRasterFeatures.RasterYSize

    if max(label_values) < 256:
        eType = gdal.GDT_Byte
    else:
        eType = gdal.GDT_UInt16
    dsRasterTmp = drvMEM.Create('', ns, nl, eType=eType)
    dsRasterTmp.SetProjection(dsRasterFeatures.GetProjection())
    dsRasterTmp.SetGeoTransform(dsRasterFeatures.GetGeoTransform())
    band = dsRasterTmp.GetRasterBand(1)
    band.Fill(0) #by default = unclassified = 0
    print('Burn geometries...')
    #gdal.RasterizeLayer(refRaster,[1], lyr, None, None, [0], ["ATTRIBUTE={}".format('gid')])
    err = gdal.RasterizeLayer(dsRasterTmp,[1], lyr_tmp, options=["ATTRIBUTE={}".format(label_field), "ALL_TOUCHED=FALSE"])

    assert err in [gdal.CE_None, gdal.CE_Warning], 'Something failed with gdal.RasterizeLayer'

    extracted_labels = band.ReadAsArray()

    dsVectorFeatures = None
    dsRasterTmp = None


    pixel_positions = np.where(extracted_labels > 0)
    pixel_positions = np.rec.fromarrays([pixel_positions[0], pixel_positions[1]], names=['y','x'])
    pixel_positions.sort(order='y')

    #todo: tile based reading
    extracted_features  = dsRasterFeatures.ReadAsArray()[:, pixel_positions.y, pixel_positions.x]
    extracted_labels    = extracted_labels[pixel_positions.y, pixel_positions.x]

    true_label_mask     = extracted_labels != 0

    if missing_feature_value: #exclude feature pixel with no_data values
        np.logical_and(true_label_mask, extracted_features[0,:] != missing_feature_value, out=true_label_mask)

    if pathSrcMsk: #exclude explicitly masked feature pixel
        dsM = gdal.Open(pathSrcMsk)
        feature_mask = dsM.GetRasterBand(1).ReadAsArray()[pixel_positions.y, pixel_positions.x]
        dsM = None
        assert feature_mask.shape == extracted_labels.shape

        if mask_interpretation == True: #include only pixel with a value in masked_values
            tmp_mask = np.zeros(extracted_labels.shape, dtype='bool')
            for v in masked_values:
                np.logical_or(tmp_mask, feature_mask == v, out=tmp_mask)
        else: #exclude pixels with a value in masked_values
            tmp_mask = np.ones(extracted_labels.shape, dtype='bool')
            for v in masked_values:
                np.logical_and(tmp_mask, feature_mask != v, out=tmp_mask)
        np.logical_and(true_label_mask, tmp_mask, out=true_label_mask)
        tmp_mask = None

    pixel_positions2 = np.where(true_label_mask == True)[0]
    extracted_features = extracted_features[:,pixel_positions2]
    extracted_labels = extracted_labels[pixel_positions2]

    pixel_positions = pixel_positions[pixel_positions2]


    if squared:
        extracted_labels    = transform_to_square(extracted_labels, missing_label_value)[0, :]
        extracted_features  = transform_to_square(extracted_features, missing_feature_value)

    assert extracted_features.shape[1:3] == extracted_labels.shape
    #write features and labels

    if pathLibFeatures:
        GDAL_Helper.SaveArray(extracted_features, pathLibFeatures, format=of,
                              no_data=missing_feature_value,
                              band_names=GDAL_Helper.readBandNames(dsRasterFeatures))
    if pathLibLabels:
        GDAL_Helper.SaveArray(extracted_labels, pathLibLabels, format=of, no_data = missing_label_value, class_names=label_names)

    return extracted_features, extracted_labels, label_names, pixel_positions



class Model_IO(object):
        """
        Class to store meta-information on model I/O
        """
        def __init__(self, model, predict = None, predict_proba=None, predict_log_proba=None):

            self.members = [name for name, x in inspect.getmembers(model, predicate=inspect.ismethod) if not name.startswith('_') ]

            self.outputs = list()
            self.masking = None
            self.masks = list()
            if predict is not None:
                self.add_output('predict', predict)
            if predict_proba is not None:
                self.add_output('predict_proba',predict_proba)
            if predict_log_proba is not None:
                self.add_output('predict_log_proba',predict_log_proba)

            pass


        def set_masking(self, masked_values, mask_value_interpretation):
            """
            Specified the interpretation of an external mask
            :param masked_values: scalar or list of values that are to be masked
            :param mask_value_interpretation: False if masked_values are to exclude, True if all others are to exclude
            """
            if not isinstance(masked_values, list):
                masked_values = [masked_values]
            assert type(mask_value_interpretation) is bool

            self.masking = (masked_values, mask_value_interpretation)

        def add_mask_input(self, pathMask, masked_values, interpretation):
            """
            [Experimental] flexible definition of mask to exclude feature pixels from processing
            :param masked_values:
            :param interpretation:
            :return:
            """

            pass

        def add_output(self, model_output_function, no_data_value, pathDstImg=None):
            """
            Specified the image output and how it relate to sklear model routines
            :param model_output_function: name of sklear model return function
            :param no_data_value: numeric value to be used in case of masked pixels, e.g. -9999
            :param pathDstImg: path where to write the results of model_output_function
            """
            assert model_output_function in self.members
            assert model_output_function not in [t[0] for t in self.outputs], 'Output function "{}" already added'.format(model_output_function)

            self.outputs.append((model_output_function, no_data_value, pathDstImg))

        def __len__(self):
            return len(self.outputs)

class SupervisedModel(object):
    """
    A wrapper to apply scikit-learn models on raster image data
    """



    def __init__(self, model, name='Anonymous Model', tilesize=500):
        """

        :param model: scikit-learn model
        :param name: model name, default= 'Anonymous Model'
        :param tilesize: RIOS tile size
        :return: SupervisedModel
        """
        self.info = dict()
        self.Model = model
        self.name = name
        self.setWindowSize(tilesize)


        #define model attributes
        self.pathTrainingFeatures = None
        self.pathTrainingLabels=None
        self.n_trainingsamples=None
        self.categoryNames = None


    def setWindowSize(self,size):
        """
        Sets the windo sie that will be processed.
        :param size:
        :return:
        """
        if isinstance(size, list) or isinstance(size, tuple):
            assert len(size) == 2
            self.windowsizex = size[0]
            self.windowsizey = size[1]
        else:
            self.windowsizex = self.windowsizey = size

    @staticmethod
    def _get_unique_bandnames(names):
        """
        Returns a list of unique band names. Uses existing band names or creates arbitrary ones
        :param dataset:
        :return:
        """
        unique_names = list()
        for i, name in enumerate(names):
            if name == '':
                name = 'Band{}'.format(i)
            if name in unique_names:
                name = '{}{}'.format(name, i+1)
            unique_names.append(name)
        return unique_names

    def __repr__(self):
        info = list()
        for k in self.__dict__.keys():
            info.append('{}={}'.format(k,str(self.__dict__[k])))
        info.append(str(self.Model))
        return 'Model "{}"'.format(self.name, ','.join(info))

    def readClassLabels(self, dataset):
        band = dataset.GetRasterBand(1)
        label_names = band.GetCategoryNames()
        label_colors = list()
        CT = band.GetColorTable()
        for i in range(CT.GetCount()):
            label_colors.append(CT.GetColorEntry(i))
        return label_names, label_colors


    def train(self, pathFeatures, pathLabels, bandNames=None, scaling=None, grid_search=None, create_learning_curve=False):
        t0 = np.datetime64('now')
        assert os.path.exists(pathFeatures)
        assert os.path.exists(pathLabels)

        self.pathTrainingFeatures = pathFeatures
        self.pathTrainingLabels = pathLabels

        dsF = gdal.Open(pathFeatures)
        dsL = gdal.Open(pathLabels)


        if scaling is not None:
            if type(scaling) is str:
                if scaling == 'MinMax':
                    print('Scale input features by min-max')
                    self.scaler = sklearn.preprocessing.MinMaxScaler()
                elif scaling == 'Standard':
                    print('Scale input features by standard deviation')
                    self.scaler = sklearn.preprocessing.StandardScaler()
                elif scaling == 'Scale':
                    print('Scale input features by standardization')
                    self.scaler = sklearn.preprocessing.scale()
            else:
                #todo: assert that scaling is a proper sklearn skaler
                self.scaler == scaling
        else:
            print('Do not scale input features')
            self.scaler = None

        src_nodata = dsF.GetRasterBand(1).GetNoDataValue()
        data_features = dsF.ReadAsArray()
        nb, nl, ns = data_features.shape
        labelBand = dsL.GetRasterBand(1)
        data_labels = labelBand.ReadAsArray()
        assert data_labels.shape == (nl, ns), 'Training features and labels must have same spatial dimension'

        class_names, class_colors = GDAL_Helper.readClassInfos(dsL)
        if class_names:
            self.categoryNames = class_names
            self.categoryColors = class_colors
            #todo: check base classifier
            #it's a classification task. mask labels with value 0
            masking = ([0], False)

        else:
            #it's a regression task. mask labels with no-data value
            masking = ([labelBand.GetNoDataValue()], False)



        src_featurenames = self._get_unique_bandnames(GDAL_Helper.readBandNames(dsF))

        if bandNames:
            for b in bandNames:
                assert b in src_featurenames, 'Bandname "{}" does not exist in feature image {}.'.format(b, pathFeatures)
            self.bandNames = bandNames
        else:
            self.bandNames = src_featurenames

        data_features, data_mask = self._homogenize_img_inputdata(data_features, src_featurenames, src_nodata, data_labels, masking)

        #convert to 1D indices, sklearn-style
        idx1D = np.where(data_mask == True)
        data_features = data_features[:, idx1D[0], idx1D[1]]  # use only non-masked features
        data_labels = data_labels[idx1D[0], idx1D[1]]

        assert data_features.ndim == 2
        assert data_labels.ndim == 1

        #scale input data
        if self.scaler is not None:
            data_features = self.scaler.transform(data_features)

        #turn dimensions to sklearn style [n_samples, n_features]
        data_features = data_features.transpose()


        self.n_trainingsamples = len(data_labels)
        self.n_features = nb

        self.ParameterSearch = None
        hasParameterSearch = self.Model.__class__.__name__ in ['GridSearchCV','RandomizedSearchCV']

        info = list()
        info.append('Model: {}'.format(self.name))

        if hasParameterSearch:
            self.ParameterSearch = self.Model
            print('Fit "{}" by {} ...'.format(self.name, self.ParameterSearch.__class__.__name__))
            #stratify by training labels.
            typeCV = type(self.Model.cv)
            if typeCV in [sklearn.cross_validation.StratifiedKFold, sklearn.cross_validation.KFold]:
                if typeCV is sklearn.cross_validation.StratifiedKFold:
                    n_folds = self.Model.cv.n_folds
                    self.ParameterSearch.cv = sklearn.cross_validation.StratifiedKFold(data_labels, n_folds)

            self.ParameterSearch.fit(data_features, data_labels)
            print('Use best parametrization as final model')
            for key in ['best_score_', 'best_params_','oob_score_']:
                if key in self.Model.__dict__.keys():
                    k = key
                    if k[-1] == '_':
                        k = k[0:-1]
                    info.append('  {} = {}'.format(k, str(self.Model.__dict__[key])))

            self.Model = self.ParameterSearch.best_estimator_
        else:
            print('Fit "{}" ...'.format(self.name))
            self.Model.fit(data_features, data_labels)

        self.learning_curve = None
        if create_learning_curve:
            #todo: add switch to handle different machine learners
            self.learning_curve = self._get_RFC_learning_curve(self.Model, data_labels, data_labels)


        print('\n'.join(info))
        dt = np.datetime64('now')-t0
        print('Calibration done: {}'.format(dt.astype(str)))
        return info

    def _get_RFC_learning_curve(self, RFC, X, y):
        """Compute out-of-bag score"""
        raise NotImplementedError()
        import sklearn.ensemble.forest
        import sklearn.utils
        import sklearn.ensemble.forest
        assert RFC.n_outputs_ == 1
        X = sklearn.utils.check_array(X, dtype=sklearn.ensemble.forest.DTYPE, accept_sparse='csr')

        n_classes_ = RFC.n_classes_
        n_samples = y.shape[0]

        oob_decision_function = []
        oob_score = 0.0
        mean_oob_scores = []
        predictions = []

        for k in range(RFC.n_outputs_):
            predictions.append(np.zeros((n_samples, n_classes_)))

        for estimator in RFC.estimators_:
            unsampled_indices = sklearn.ensemble.forest._generate_unsampled_indices(
                estimator.random_state, n_samples)
            p_estimator = estimator.predict_proba(X[unsampled_indices, :],
                                                  check_input=False)

            if RFC.n_outputs_ == 1:
                p_estimator = [p_estimator]

            for k in range(RFC.n_outputs_):
                predictions[k][unsampled_indices, :] += p_estimator[k]

        predictions = predictions[0]
        oob_score += np.mean(y == np.argmax(predictions, axis=1), axis=0)


        mean_oob_scores.append(oob_score / k+1)


        return mean_oob_scores

    """
    @staticmethod
    def getBandNamesFromRegex(ds, bandRegex=None):

        if type(ds) is str:
            assert os.path.exists(ds), 'File does not exists: '+str(ds)
            ds = gdal.Open(ds)
        assert ds is not None
        gdalBandNames = [ds.GetRasterBand(b).GetDescription() for b in range(1, ds.RasterCount+1)]
        if type(bandRegex) is str:
            bandRegex = [bandRegex]
        if bandRegex:
            bandNames = list()
            for b, r in itertools.product(gdalBandNames, bandRegex):
                if re.search(r,b) and b not in bandNames:
                        bandNames.append(b)
        else:
            bandNames = gdalBandNames
        return bandNames
    """

    def apply_data(self, data_features, data_mask=None, modelIO=None, predict=None, predict_proba=None, predict_log_proba=None ):
        """
        Applies ML model functions on image-like input array

        :param data_features: feature array of for [n_bands, n_lines, n_samples], dtype=any
        :param data_mask: mask array of size [n_lines, n_samples] and dtype=bool
        :param modelIO: optional,
        specifies which model function are to be used and which ignore value is used in case a pixel is masked.
        See SupervisedModel.Model_IO for details

        :return: dictionary with returned model results.
        """
        if modelIO is None:

            modelIO = Model_IO(self.Model)
            if predict is not None:
                modelIO.add_output('predict', predict)
            if predict_proba is not None:
                modelIO.add_output('predict_proba', predict_proba)
            if predict_log_proba is not None:
                modelIO.add_output('predict_log_proba', predict_log_proba)

        nb, nl, ns = data_features.shape
        nl = np.uint64(nl)
        ns = np.uint64(ns)

        npx = nl * ns

        assert nb == len(self.bandNames)

        #mask and convert data to sklear model required dimensions
        if data_mask is not None:
            assert data_mask.dtype == np.bool
            assert data_mask.shape == (nl, ns)
            data_mask = data_mask.flatten()
        else:
            data_mask = np.ones((npx,), dtype='bool')

        data_features = np.resize(data_features, (nb, npx))

        #convert to 1D indices, sklearn-style
        idx1D = np.where(data_mask == True)[0]
        all_masked = len(idx1D) == 0
        if not all_masked:
            data_features = data_features[:, idx1D]  # use only non-masked features
        else:
            data_features = data_features[:, [0]]  # use one fake pixel, just to get an exemplary model return to determine output products

        if self.scaler is not None:
            data_features = self.scaler.transform(data_features)

        #turn dimensions to sklearn style [n_samples, n_features]
        data_features = data_features.transpose()


        results = dict()
        t0 = np.datetime64('now')
        f_names = ','.join('"{}"'.format(n[0]) for n in modelIO.outputs)
        print('Apply {} on {} px using {} job(s)'.format(f_names, npx, self.Model.n_jobs))

        for model_output_function, _ , _ in modelIO.outputs:

            func = getattr(self.Model, model_output_function)
            func_result = func(data_features)
            #handel returned values
            if re.search('^predict_.*proba$', model_output_function):
                 func_result = func_result.transpose()
            results[model_output_function] = func_result
            #print('Model required {} for "{}" on {}'.format(dTimeString(t1), model_output_function, jobinfo))
        print('Time required for {} pixel: {} '.format(npx, dTimeString(t0)))

        #return output as raster grid

        idx2d = np.resize(np.indices((nl, ns)), (2, nl * ns))
        for model_output_function, no_data_value , _ in modelIO.outputs:
            data = results[model_output_function]
            if data.ndim == 1:
                nb_out = 1
            else:
                nb_out = data.shape[0]
            data2 = np.zeros((nb_out, nl, ns), dtype=data.dtype)
            data2.fill(no_data_value)  # fill with no_data value

            if not all_masked:
                data2[:, idx2d[0][idx1D], idx2d[1][idx1D]] = data
            # results[prediction] = data2
            results[model_output_function] = data2

        return results


    def _homogenize_img_inputdata(self, src_features, src_feature_names, no_data, src_mask, masking):
        # handle 2D data from hear on
        (nb, nl, ns) = src_features.shape
        if src_mask is not None:
            assert (nl, ns) == src_mask.shape

        src_feature_names = self._get_unique_bandnames(src_feature_names)


        missing = [n for n in self.bandNames if n not in src_feature_names]
        if len(missing) > 0:

            nf_model = len(self.bandNames)
            if len(src_feature_names) != nf_model:
                raise Exception('Model was trained on {} features. Neither the feature names nor the number of features match'.format(nf_model))
            else:
                six.print_('Missing feature names: {}'.format('"'+'","'.join(missing)+'"'),file=sys.stderr)
                six.print_('Continue using all {} features'.format(nf_model),file=sys.stderr )
                src_feature_names = self.bandNames

        #extract band of interest.
        idx = np.asarray([src_feature_names.index(n) for n in self.bandNames], dtype='int16')
        data_features = src_features[idx, :]

        data_mask = np.ones((nl, ns), dtype='bool')
        # create True/False mask from src mask values
        if src_mask is not None and masking is not None:
            masked_values, interpretation = masking
            if interpretation == False:
                for v in masked_values:
                    if v:
                        np.logical_and(data_mask, src_mask != v, out=data_mask)
            else:
                for v in masked_values:
                    if v:
                        np.logical_or(data_mask, src_mask == v, out=data_mask)

        # account for infinite or no-data values in feature data
        for i in range(nb):
            np.logical_and(data_mask, np.isfinite(data_features[i,:]), out=data_mask)
            if no_data:
                np.logical_and(data_mask, data_features[i,:] != no_data, out=data_mask)
        return data_features, data_mask

    def apply_files(self, pathFeatures, pathMask=None, masked_values_interpretation=False, masked_values=0,
                    path_predict=None, path_predict_proba=None, path_predict_log_proba=None, buggy_rios=True,
                    windowsize=None, numThread=1, n_jobs=1, _bb_px=None):
        """
        Runs the model on raster images
        :param pathFeatures: image path with input features
        :param path_predict: path output returned from model "predict" function
        :param path_predict_proba: path output returned from model "predict_proba" function
        :param path_predict_log_proba: path output returned from model "predict_log_prob" function
        :param pathMask: path of mask image
        :param buggy_rios:
        :param windowsize:
        :param numThread:
        :param n_jobs:
        :param masked_values: scalar or list of values that are to be masked within pathMask image
        :param masked_values_interpretation: how masked values are interpreted. False (default) will exclude masked_values,
        True will run the model only on for pixels labeled with a value in masked_values


        """

        assert os.path.exists(pathFeatures), pathFeatures
        if pathMask:
            assert os.path.exists(pathMask)

        assert n_jobs > 0
        print('Apply model on {}.'.format(pathFeatures))
        modelIO = Model_IO(self.Model)
        if path_predict:
            modelIO.add_output('predict', 0, pathDstImg=path_predict)
        if path_predict_proba:
            modelIO.add_output('predict_proba', -9999., pathDstImg=path_predict_proba)
        if path_predict_log_proba:
            modelIO.add_output('predict_log_proba', -9999., pathDstImg=path_predict_log_proba)
        modelIO.set_masking(masked_values, masked_values_interpretation)
        assert len(modelIO) > 0
        self.Model.set_params(n_jobs=n_jobs)

        if windowsize: #use tiling scheme

            self.setWindowSize(windowsize)

            if buggy_rios:
                #do your own tiling
                import multiprocessing
                pool = multiprocessing.Pool(processes=numThread)

                dsF = gdal.Open(pathFeatures)
                ns = dsF.RasterXSize
                nl = dsF.RasterYSize

                data_results = None
                async_results = list()
                def tiling_callback(returns):
                    tile_results, spatial_kwds = returns
                    xoff = spatial_kwds['xoff']
                    yoff = spatial_kwds['yoff']
                    xsize = spatial_kwds['xsize']
                    ysize = spatial_kwds['ysize']

                    nonlocal data_results
                    if data_results is None:
                        data_results = dict()
                        for key, array in tile_results.items():
                            out_nb, _, _ = get_array_dims(array)
                            data_results[key] = np.ndarray((out_nb, nl, ns), dtype=array.dtype)

                    for key, array in tile_results.items():
                        dst_array = data_results[key]
                        dst_array[:,yoff:yoff+ysize, xoff:xoff+xsize] = array
                    s = ""
                    pass

                wsizex = self.windowsizex
                wsizey = self.windowsizey
                if wsizex == -1:
                    wsizex = ns
                if wsizey == -1:
                    wsizey = nl

                for xoff in range(0, ns, wsizex):
                    xsize = wsizex
                    if xoff + xsize >= ns:
                        xsize = ns - xoff
                    for yoff in range(0, nl, wsizey):
                        ysize = wsizey
                        if yoff + ysize >= nl:
                            ysize = nl - yoff

                        #append all arguments for the processing routine
                        args = (copy.deepcopy(self), pathFeatures, pathMask, copy.deepcopy(modelIO))
                        spatial_kwds = {'xoff':xoff,'yoff':yoff, 'xsize':xsize, 'ysize':ysize}

                        #results = _no_rios_apply_files(*args, **spatial_kwds)
                        ar = pool.apply_async(_no_rios_apply_files \
                                         , args=args, kwds=spatial_kwds \
                                         , callback=tiling_callback \
                                         , error_callback=error_callback)
                        async_results.append(ar)

                pool.close()
                print('Wait until all tiles have been finished...')
                pool.join()

                #save the returned data arrays
                self._save_output_data(data_results, modelIO, pathFeatures)


            else:
                infiles = rios.applier.FilenameAssociations()
                outfiles = rios.applier.FilenameAssociations()
                infiles.features = pathFeatures
                if pathMask:
                    infiles.mask = pathMask
                otherargs = rios.applier.OtherInputs()
                #otherargs.bandnames=self.bandNames
                #otherargs.scaler = self.scaling
                otherargs.modelio = modelIO
                import tempfile
                #x, path_sm = tempfile.mkstemp(prefix='tmp.',suffix='.pyrfc')
                #self.save(path_sm)
                #otherargs.path_sm = path_sm
                #otherargs.sm = copy.copy(self)
                otherargs.sm = self._dump()

                controls = rios.applier.ApplierControls()
                controls.windowxsize = self.windowsizex
                controls.windowysize = self.windowsizey
                controls.thematic = True
                controls.setOutputDriverName('ENVI')
                controls.setCreationOptions([])
                controls.omitPyramids = True
                controls.calcStats = False
                controls.referenceImage = pathFeatures
                assert numThread >= 1

                if numThread > 1:
                    controls.setNumThreads(numThread)
                    controls.setJobManagerType('pbs')
                    #controls.setJobManagerType('multiprocessing')

                rios.applier.apply(_rios_apply_files, infiles, outfiles, otherArgs=otherargs, controls=controls)
            #os.remove(path_sm)
        else: #normal non-tiled predictions

            dsF = gdal.Open(pathFeatures)
            src_features = dsF.ReadAsArray()
            src_feature_names = self._get_unique_bandnames(GDAL_Helper.readBandNames(dsF))
            no_data = dsF.GetRasterBand(1).GetNoDataValue()
            src_mask = None
            if pathMask:
                src_mask = gdal_array.LoadFile(pathMask)

            src_features, src_mask = self._homogenize_img_inputdata(src_features, src_feature_names, no_data, src_mask, modelIO.masking)

            #todo: consistency checks

            data_results = self.apply_data(src_features, src_mask, modelIO=modelIO)
            #save the returned data arrays
            self._save_output_data(data_results, modelIO, pathFeatures)


        #post-processing logic, setting metadata


        self._set_output_metadata(modelIO)

        print('Done.')

    def _save_output_data(self, data_results, modelIO, pathFeatures):
        for model_output_function, no_data_value, pathDstImg in modelIO.outputs:
            result_data = data_results[model_output_function]
            GDAL_Helper.SaveArray(result_data, pathDstImg \
                                  , prototype=pathFeatures \
                                  , no_data=no_data_value)

    def _set_output_metadata(self, modelIO):
        for model_output_function, no_data_value, pathDstImg in modelIO.outputs:
            dsF = gdal.Open(pathDstImg, gdal.GA_Update)

            if self.categoryNames:
                if model_output_function == 'predict':
                    GDAL_Helper.setClassificationInfo(dsF, self.categoryNames, label_colors=self.categoryColors)
                elif model_output_function in ['predict_proba', 'predict_log_proba']:
                    GDAL_Helper.setNoDataValue(dsF, no_data_value)
                    GDAL_Helper.setBandNames(dsF, self.categoryNames)
                else:
                    GDAL_Helper.setNoDataValue(dsF, no_data_value)
            else:
                GDAL_Helper.setNoDataValue(dsF, no_data_value)

    def _dump(self):
        modeldata = self.__dict__
        return pickle.dumps(modeldata)

    @staticmethod
    def _restore_dump(dump):
        modeldata = pickle.loads(dump)
        model = SupervisedModel(modeldata['Model'])
        for k in model.__dict__.keys():
            if k in modeldata.keys():
                model.__dict__[k] = modeldata[k]
            else:
                print('Can not make use of restored key {}'.format(k))
        for k in modeldata.keys():
            if k not in model.__dict__.keys():
                model.__dict__[k] = modeldata[k]
        return model

    def save(self, path):

        #create new directory if required
        os.makedirs(os.path.dirname(path), exist_ok=True)

        #save the pickle binary
        with open(path, 'wb') as f:
            print('Save model in {}...'.format(path))
            f.write(self._dump())
            #modeldata = self.__dict__
            #pickle.dump(modeldata.copy(), f)
        print("Model '{}' saved to {}".format(self.name, path))


    @staticmethod
    def restore(path):
        """
        Restores a model
        :param path:
        :return:
        """

        model = None
        with open(path, 'rb') as f:
            print('Restore model from {}...'.format(path))
            dump = f.read()
            model = SupervisedModel._restore_dump(dump)

        return model




def cluster_sampling_image(pathFeatures, n_samples, \
                           pathStratification=None, \
                           *args, **kwargs \
                           ):
    """
    Samples pixel from an image
    :param pathFeatures: path of feature image
    :param n_samples: number of pixels to sample from image.
        If pathStratification is given you can use a list of (stratum label, samples) to define n_samples per stratum.
        Otherwise n_samples is drawn from each stratum.

    :param pathStratification: stratification, optional
    :param n_clusters: number of kmeans clusters to sample from with all features related to a stratum
    :param n_jobs: number of cpu to be in kmeans clustering
    :return: (image_indices, sampled_features, sampled_strata)
        with image_indices showing the sampled 2D pixel indices whre sampled_features and sampled_strata come from

    """
    ns, nl, nb = GDAL_Helper.readDimensions(pathFeatures)

    strata_label_samples = list()
    if pathStratification is not None:
        dimsStrat = GDAL_Helper.readDimensions(pathStratification)[0:2]
        if dimsStrat != (ns, nl):
            s = ""
        assert (ns, nl) == dimsStrat,'Feature and stratification images must have same spatial size'
        all_strata_names, _ = GDAL_Helper.readClassInfos(pathStratification)
        strata_data = gdal_array.LoadFile(pathStratification)

        n_strata = len(all_strata_names)

        if isinstance(n_samples, list):
            for t in n_samples:
                l, n = t
                if type(l) is str:
                    assert l in all_strata_names
                    l = all_strata_names.index(l)
                assert l < n_strata
                assert n >= 0
                strata_label_samples.append((l,n))
        else:
            assert np.isscalar(n_samples) and n_samples > 0
            for l in range(1, n_strata+1):
                strata_label_samples.append((l, n_samples))


    else:
        assert np.isscalar(n_samples)
        strata_label_samples.append((1,n_samples))
        strata_data = np.ones((nl, ns), dtype='uint8')

    feature_data = gdal_array.LoadFile(pathFeatures)

    ndv = GDAL_Helper.readNoDataValues(pathFeatures)
    #mask out ignored pixels from sampling
    if ndv is not None:
        #we are optimistic and assume that if there are no data pixels, than they are marked in the first feature

        strata_data[np.where(feature_data[0,]) == ndv] = 0
        #for i, n in enumerate(ndv):
        #    strata_data[np.where(feature_data[i,]) == ndv] = 0

    nb, nl, ns = feature_data.shape
    strata_data = strata_data.flatten()
    feature_data = np.resize(feature_data, (nb, nl*ns))

    indices = cluster_sampling_data(feature_data, strata_data, strata_label_samples , \
                                    *args, **kwargs)
    #convert from 1d to 2d indices
    grid = np.resize(np.indices((nl, ns)), (2, nl*ns))
    return grid[:,indices], feature_data[:, indices], strata_data[indices]

def cluster_sampling_data(feature_data, strata_data, strata_label_samples, *args, **kwargs):
    """
    Samples indices in the feature data set
    :param feature_data: feature data set to get represenative samples from
    :param strata_data: stratification of feature data set
    :param strata_label_samples: list of (label value,n samples) that define how many samples are to choose from which stratum labeled by label
    :param n_clusters: number of kmeans clusters to sample from
    :param n_jobs: number of cpu / cores to be used in kmeans clustering
    :return:
    """
    import sklearn
    import sklearn.cluster
    assert feature_data.ndim == 2
    assert strata_data.ndim == 1
    assert feature_data.shape[1] == strata_data.shape[0]

    kmeans = sklearn.cluster.KMeans(*args, **kwargs)
    n_clusters = kmeans.n_clusters
    print(kmeans)

    selected_1d_indices = list()
    for t in strata_label_samples:
        l, n_to_sample = t

        is_stratum = np.where(strata_data == l)[0]
        n_is_stratum = len(is_stratum)
        if n_to_sample == 0 or n_is_stratum == 0:
            continue

        selected_indices = []
        rest = []

        if n_to_sample >= n_is_stratum:
            print('Take all features labeled with {}...'.format(l))
            selected_1d_indices.append(is_stratum)
        else:
            missing = n_to_sample
            per_cluster = int(missing / n_clusters)

            if n_clusters > 1:
                print('Cluster {} features labeled with {}...'.format(n_is_stratum, l))
                if is_stratum.max() >= feature_data.shape[1]:
                    s = ""
                cluster_indices = kmeans.fit_predict(feature_data[:,is_stratum].transpose())
            else:
                cluster_indices = np.zeros(is_stratum.shape)

            for c_index in range(n_clusters):

                is_cluster = np.random.permutation(np.where(cluster_indices == c_index)[0])
                print('Sample from cluster {}/{} ({} px total)...'.format(c_index+1, n_clusters, len(is_cluster)))
                selected_indices.append(is_cluster[0:per_cluster])
                rest.append(is_cluster[per_cluster:])


            selected_indices = np.concatenate(selected_indices)
            rest = np.concatenate(rest)

            missing = missing - len(selected_indices)

            if missing > 0:
                selected_indices = np.concatenate((selected_indices, rest[0:missing]))

            selected_1d_indices.append(is_stratum[selected_indices])

    selected_1d_indices = np.concatenate(selected_1d_indices)
    selected_1d_indices.sort()
    return selected_1d_indices




def error_callback(errors):
    print('Error!')
    s = ""
    print(errors)

def get_class_colors(n, cmap='brg', unclassified=(0,0,0,255), reverse=False):

    cmap = matplotlib.cm.get_cmap(cmap, n)

    ci = range(n-1)

    if reverse:
        ci = reversed(ci)
    label_colors = [unclassified]
    for i in ci:
        label_colors.append(tuple([int(255*c) for c in cmap(i)]))
    return label_colors


def analyze_class_probabilities(pathProb, path_dmin=None, path_dminC=None):
    """

    :param pathProb: path of image containing the class probabilitie
    :param path_dmin: path of output image with dMin
        dMin  = difference between highest and second highest class probability
    :param path_dminC: path of output classification image with classified dMin
    """
    probs = gdal_array.LoadFile(pathProb)
    nd = GDAL_Helper.readNoDataValue(pathProb)
    nf, nl, ns = probs.shape
    probs = np.resize(probs, (nf, nl * ns))
    # get minimum difference in class probabilities.
    # the less this distance, the more confusion
    prob_d = probs.max(axis=0) - probs
    prob_d.sort(axis=0)
    dMin = prob_d[1, :]
    dMinC = np.zeros(dMin.shape, dtype='uint8')
    thresholds = [-1, 0.05, .10, .25, .50, .75, 1.]
    class_names = []
    for l, t in enumerate(thresholds):
        if l == 0:
            class_names.append('unclassified')
            continue
        class_names.append('<= {}%'.format(t * 100.))
        is_class = np.where(np.logical_and(dMin > thresholds[l - 1], dMin <= t))[0]
        dMinC[is_class] = l
    class_colors = get_class_colors(len(class_names), cmap='hsv', reverse=False)
    if nd:
        is_nodata = np.where(probs == nd)[0]
        dMin[is_nodata] = -1.
        dMinC[is_nodata] = 0

    mean_dMin = dMin[np.where(probs != nd)[0]].mean()
    dMin = np.resize(dMin, (nl, ns))
    dMinC = np.resize(dMinC, (nl, ns))
    GDAL_Helper.SaveArray(dMin, path_dmin, no_data=-1, band_names=['Min.class.prob.difference'], prototype=pathProb)
    GDAL_Helper.SaveArray(dMinC, path_dminC, band_names=['difference classes'], class_names=class_names,
                         class_colors=class_colors, prototype=pathProb)

    return mean_dMin


def transform_to_square(array, no_data_value):

    if array.ndim == 1:
        nb = 1
        npx = len(array)
    else:
        nb = array.shape[0]
        npx = np.product(array.shape[1:])

    nl = ns = int(np.ceil(np.sqrt(npx)))
    array2 = np.ndarray((nb, int(nl*ns)), dtype=array.dtype)
    array2.fill(no_data_value)
    array2[:,0:npx] = array.reshape((nb, npx))

    return array2.reshape((nb, nl, ns))

def examples():
    #abbreviations
    jp = os.path.join
    mkDir = lambda path : os.makedirs(path, exist_ok=True)
    #some paths
    dirTestdata = r'C:\Users\geo_beja\Documents\Repositories\sensecarbon\bj\christin_abel\testdata'

    #multispectra-image, e.g. "Landsat"
    pathImg = jp(dirTestdata, 'example_img.tif')
    pathMsk = jp(dirTestdata, 'example_fmask.tif')
    #a vector data set, e.g. shapefile
    pathVec = jp(dirTestdata, 'labels.shp')
    label_field = 'label_name' #"column" in vector data set that contains the label names

    dirCalibration = jp(dirTestdata, '01_Calibration')
    dirPrediction = jp(dirTestdata, '02_Predictions')
    mkDir(dirCalibration)
    mkDir(dirPrediction)


    pathCal_Features = jp(dirCalibration, 'lib_features.tif')
    pathCal_Labels   = jp(dirCalibration, 'lib_labels.tif')
    pathModel = jp(dirCalibration, 'MyModel.pyrfc')

    pathPredictedLabels = jp(dirPrediction, 'predictedLabels.bsq')
    pathLabelProbabilites = jp(dirPrediction, 'labelProbabilities.bsq')


    #1. extract a labeled feature library
    if True:
        results = extract_labeled_feature_library(
            pathImg, pathVec, label_field #required input arguments
            , pathLibFeatures=pathCal_Features, pathLibLabels=pathCal_Labels #optional outputs
            , pathSrcMsk=pathMsk #use the fmask
            , masked_values=[0], mask_interpretation=True #use fmask pixels with value=0 only
            )
        extracted_features, extracted_labels, label_names, pixel_positions = results
        s = ""


    #2. calibrate and save a RFC model
    if True:
        RFCM = sklearn.ensemble.RandomForestClassifier()
        SM = SupervisedModel(RFCM)
        SM.train(pathCal_Features, pathCal_Labels)
        SM.save(pathModel)


    #3a. restore and apply the RFC model on the on /entire/ image in one step. this might exceed your memory
    if True:
        pathPred_Features = pathImg #
        SM = SupervisedModel.restore(pathModel)
        SM.apply_files(pathPred_Features, path_predict=pathPredictedLabels,
                       path_predict_proba=pathLabelProbabilites)

    #3b. do it tile based
    if True:
        pathPred_Features = pathImg #
        windowsize = (-1, 5) #use tiles of full image width and 5 lines
        numThread = 2 #process numThread tiles in parallen
        buggy_rios = True #rios sucks and is somehow buggy.
        SM = SupervisedModel.restore(pathModel)
        SM.apply_files(pathPred_Features, path_predict=pathPredictedLabels,
                       path_predict_proba=pathLabelProbabilites, buggy_rios=buggy_rios, windowsize=windowsize,
                       numThread=numThread, n_jobs=5)


    pass

if __name__ == '__main__':

    examples()
