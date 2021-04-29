.. include:: /icon_links.rst

.. _QGIS user manual: https://docs.qgis.org/testing/en/docs/user_manual
.. _Scikit-Learn: https://scikit-learn.org
.. _Scikit-Learn glossary: https://scikit-learn.org/stable/glossary.html

========
Glossary
========

This glossary gives an overview of how specific terms are used inside the EnMAP-Box.

All the terms that relate to GIS in general should be consistent with the terms given by the `QGIS user manual`_ and GUI.
Because the EnMAP-Box integrates into the QGIS GUI, we try to not (as far as possible) contradict or redefine terminology.

All terms that relate to machine learning should be consistent with the definitions given by `Scikit-Learn`_ and the
`Scikit-Learn glossary`_, because we wildly crosslink into the Scikit-Learn docs!

GIS and Remote Sensing
======================

.. glossary::

    attribute
    attributes
        A synonym for field.

    attribute table
    attribute tables
        A tabulated data table associated with a vector layer.
        Table columns and rows are referred to as fields and geographic features respectively.

    attribute value
    attribute values
        Refers to a single cell value inside the attribute table of a vector layer.

    band
    bands
        A :term:`raster layer` is composed of one or multiple bands.

    categorized layer
    categorized layers
        A categorized vector layer or categorized raster layer.

        .. image:: img/categorized_raster_layer.png
            :width: 32%
        .. image:: img/categorized_raster_layer_2.png
            :width: 32%
        .. image:: img/categorized_raster_layer_3.png
            :width: 32%

        .. image:: img/categorized_vector_layer.png
            :width: 32%
        .. image:: img/categorized_vector_layer_2.png
            :width: 32%

    categorized raster layer
    categorized raster layers
        A raster layer styled with a paletted/unique values renderer. The renderer defines the raster band storing the category values and a list of named and colored categories. Styles are usually stored as QML sidecar files.
        Category values don't have to be strictly consecutive.

        .. image:: img/categorized_raster_layer.png
            :width: 32%
        .. image:: img/categorized_raster_layer_2.png
            :width: 32%
        .. image:: img/categorized_raster_layer_3.png
            :width: 32%

        .. image:: img/categorized_raster_layer_styling.png

    categorized vector layer
    categorized vector layers
        A vector layer styled with a categorized symbol renderer. The renderer defines the vector field storing the category values (numbers or strings; expressions not yet supported) and a list of named and colored categories. Styles are usually stored as QML sidecar files.
        Note that in case of numerical category values, the values don’t have to be strictly consecutive.

        .. image:: img/categorized_vector_layer.png
            :width: 32%
        .. image:: img/categorized_vector_layer_2.png
            :width: 32%

        .. image:: img/categorized_vector_layer_styling.png

    categorized spectral library
    categorized spectral libraries
        A spectral library that is also a categorized vector layer.

        .. image:: img/categorized_spectral_library.png

    category
    categories
        A category has a value, a name and a color.

    classification layer
    classification layers
        A categorized raster layer that is assumed to represent a mapping of a contiguous area.

        .. image:: img/categorized_raster_layer.png

        *Note that there is currently no equivalent term for a contiguous vector polygon layer. We may introduce it in the future as needed. For now we expect users to rasterize such a vector layer into a raster layer.*

    class probability layer
    class probability layers
        A multi-band raster layer, where the bands represent class probabilities (values between 0 and 1) for a set of categories.

    class fraction layer
    class fraction layers
        A multi-band raster layer, where the bands represent class cover fractions (values between 0 and 1) for a set of categories.

    color
    colorS
        A color is specified by a red, green and blue component.
        Learn more here: https://htmlcolorcodes.com/

    continuous-valued raster layer
    continuous-valued raster layers
        A raster layer, where each band represents a continuous-valued variable. Variable names are given by the raster band names.

        .. image:: img/continuous-valued_raster_layer.png
            :width: 32%
        .. image:: img/continuous-valued_raster_layer_2.png
            :width: 32%
        .. image:: img/continuous-valued_raster_layer_3.png
            :width: 32%

    continuous-valued vector layer
    continuous-valued vector layers
        A vector layer with numeric fields representing continuous-valued variables. Variable names are given by field names.

        .. image:: img/continuous-valued_vector_layer.png
            :width: 32%
        .. image:: img/continuous-valued_vector_layer_2.png
            :width: 32%

    continuous-valued layer
    continuous-valued layers
        A continuous-valued vector layer or continuous-valued raster layer.

        .. image:: img/continuous-valued_raster_layer.png
            :width: 32%
        .. image:: img/continuous-valued_raster_layer_2.png
            :width: 32%
        .. image:: img/continuous-valued_raster_layer_3.png
            :width: 32%

        .. image:: img/continuous-valued_vector_layer.png
            :width: 32%
        .. image:: img/continuous-valued_vector_layer_2.png
            :width: 32%

    field
    fields
        Refers to a single column inside the attribute table of a vector layer.

    geographic feature
    geographic features
        Refers to a single row inside the attribute table of a vector layer.
        In a vector layer, a geographic feature is a logical element defined by a point, polyline or polygon.

        Note that in the context of GIS, the epithet "geographic" in "geographic feature" is usually skipped.
        In the context of EnMAP-Box, and machine learning in general, the term "feature" is used differently.
        See feature for details.

    grid
    grids
        A raster layer defining the spatial extent, coordinate reference system and the pixel size.

    hex-color
    hex-colors
        A color specified by a 6-digit hex-color string, where each color component is represented by a two digit hexadecimal number, e.g. red ‘#FF0000’, green ‘#00FF00’, blue ‘#0000FF’, black ‘#000000’, white ‘#FFFFFF’ and grey ‘#808080’.

    int-color
    int-colors
        A color specified by a single integer between 0 and 256^3 - 1, which can also be represented as a hex-color.

    labeled layer
    labeled layers
        A categorized layer or a continuous-valued layer.

    layer
    layers
        A vector layer or a raster layer.

    layer style
        The style of a layer can be defined in the Layer Styling panel and the Styling tab of the Layer Properties dialog.
        Some applications and algorithms take advantage of style information, e.g. for extracting category names and colors.

    line layer
    line layers
        A vector layer with line geometries.

    mask layer
        A mask raster layer or mask vector layer.

        .. image:: img/mask_raster_layer.png
            :width: 32%
        .. image:: img/mask_raster_layer_2.png
            :width: 32%
        .. image:: img/mask_raster_layer_3.png
            :width: 32%

        .. image:: img/mask_vector_layer.png
            :width: 32%
        .. image:: img/mask_vector_layer_2.png
            :width: 32%

    mask raster layer
        A raster layer interpreted as a binary mask. All no data (zero, if missing), inf and nan pixel evaluate to false, all other to true. Note that only the first band used by the renderer is considered.

        .. image:: img/mask_raster_layer.png
            :width: 32%
        .. image:: img/mask_raster_layer_2.png
            :width: 32%
        .. image:: img/mask_raster_layer_3.png
            :width: 32%

    mask vector layer
        A vector layer interpreted as a binary mask. Areas covered by a geometry evaluate to true, all other to false.

        .. image:: img/mask_vector_layer.png
            :width: 32%
        .. image:: img/mask_vector_layer_2.png
            :width: 32%

    pickle file
        A binary file ending on `.pkl` that contains a pickled Python object, usually a dictionary or list container.
        Pickle file content can be browsed via the EnMAP-Box Data Sources panel:

    .. image:: img/pickle_file.png

    pixel profile
    pixel profiles
        List of band values for a single pixel in a raster layer.

        .. image:: img/spectral_profile.png

    point layer
    point layers
        A vector layer with point geometries.

        .. image:: img/vector_layer_2.png

    polygon layer
    polygon layers
        A vector layer with polygon geometries.

        .. image:: img/vector_layer.png

    raster layer
    raster layers
        Any raster file that can be opened in QGIS as `QgsRasterLayer`.
        Elsewhere known as an image.

        .. image:: img/raster_layer.png

    regression layer
        A continuous-valued raster layer that is assumed to represent a mapping of a contiguous area.

        .. image:: img/continuous-valued_raster_layer.png
            :width: 32%

    rgb-color
        A color specified by a triplet of byte values (values between 0 and 255) representing the red, green and blue color components, e.g. red (255, 0, 0), green (0, 255, 0), blue (0, 0, 255), black (0, 0, 0), white (255, 255, 255) and grey (128, 128, 128).

    RGB image
        A 3-band byte raster layer with values ranging from 0 to 255.

    spectral library
        A vector layer with (at least) one special binary field containing pickled profile data and metadata.
        If a spectral library has exactly one such binary field, each geographic feature represents one spectral profile.
        In the case of `n` different binary fields, each vector feature represents `n` profiles.

        A spectral library is a collection of profiles with arbitrary profile-wise data and metadata,
        stored as pickled dictionaries inside (multiple) binary fields.
        Dictionary items are:

        * `x`: list of x values (e.g. wavelength)
        * `y`: list of y values (e.g. surface reflectance)
        * `xUnit`: x value units (e.g. nanometers)
        * `yUnit`: y value units (e.g. ???)
        * `bbl`: the bad bands list

        See `enmapbox.externals.qps.speclib.core.SpectralLibrary` for details.

        .. image:: img/spectral_library.png

    spectral profile
    spectral profiles
        A pixel profile in a spectral raster layer or a profile in a spectral library.

        .. image:: img/spectral_profile.png

    stratification layer
        A classification layer that is used to stratify an area into distinct subareas.

        .. image:: img/categorized_raster_layer.png

    stratum
    strata
        A category of a classifcation layer that is used as a stratification layer.
        Conceptually, a stratum can be seen as a binary mask with all pixels inside the stratum evaluating to True and all other pixels evaluating to False.

    spectral band
    spectral bands
        A :term:`band` inside a :term:`spectral raster layer`.
        A spectral band represents a measurement for a region of the electromagnetic spectrum around a specific :term:`center wavelength`.
        The region is typically described by a :term:`spectral response function`.

    spectral raster layer
    spectral raster layers
        A raster layer where the individual bands (i.e. :term:`spectral bands`) represent measurements across the electromagnetic spectrum.
        The measurement vector of a single pixel is called a :term:`spectral profile`)

        .. image:: img/raster_layer.png
        .. image:: img/spectral_profile.png

    table
        A vector layer with (potentially) missing geometry.

        *Note that in case of missing geometry, the vector layer icon looks like a table and layer styling is disabled.*

        .. image:: img/table.png

    vector feature
        Synonym for geographic feature.

    vector layer
    vector layers
        Any vector file that can be opened in QGIS as `QgsVectorLayer`.

        .. image:: img/vector_layer.png
        .. image:: img/vector_layer_2.png

Raster layer metadata
=====================

.. glossary::

    band description
    band name
        Defined by GDAL data model. Accessible via `gdal.Band.GetDescription()`.

    bbl
    bad bands list
        List of bad band multiplier values of each band, typically 0 for bad bands and 1 for good bands.


    center wavelength
        A synonym for :term:`wavelength`.

    fwhm
    full-width-at-half-maximum
        List of full-width-half-maximum (FWHM) values of each :term:`band`.
        Units should be the same as those used for :term:`wavelength` and set in the :term:`wavelength units` parameter.

        For historical reasons we store that information in ENVI format and domain.
        Accessible via `gdal.Dataset.GetMetadataItem('fwhm', 'ENVI')`.

    no data value
        Defined by GDAL data model. Accessible via `gdal.Band.GetNoDataValue()`.

    spectral response function
        todo

    wavelength
        List of center wavelength values of each :term:`band`.
        Units should be the same as those used for the :term:`fwhm` and set in the :term:`wavelength units` parameter.

       For historical reasons we store that information in ENVI format and domain.
       Accessible via `gdal.Dataset.GetMetadataItem('wavelength', 'ENVI')`.

    wavelength units
        Text string indicating one of the following wavelength units:
        `Micrometers`, `um`, `Nanometers`, `nm`, `Index`, `Unknown`

        For historical reasons we store that information in ENVI format and domain.
        Accessible via `gdal.Dataset.GetMetadataItem('wavelength units', 'ENVI')`.



Machine Learning
================

EnMAP-Box provides nearly all of it's machine learning related functionality by using `Scikit-Learn`_ in the background.
So we decided to also adopt related terminology and concepts as far as possible,
while still retaining the connection to GIS and remote sensing in the broader context of being a QGIS plugin.
Most of the following definitions are directly taken from the `Scikit-Learn glossary`_ as is, and only expanded if necessary.

.. glossary::

    classification
        The process of identifying which category an object (e.g. pixel or profile) belongs to.

    classifier
        A supervised predictor with a finite set of discrete possible output values.

    clusterer
        An unsupervised predictor with a finite set of discrete output values.

    clustering
        The process of automatic grouping of similar objects (e.g. pixel or profile) into sets.

    cross-validation
        The training set is split into k smaller sets and the following procedure is followed for each of the k "folds":

        * a model is trained using k-1 of the folds as training data

        * the resulting model is used to predict the targets of the remaining part of the data

        The performance can now be calculated from the predictions for the whole training set.

        .. image:: img/dataset_cross-val.png

        This approach can be computationally expensive,
        but does not waste too much data (as is the case when fixing an arbitrary validation set),
        which is a major advantage in problems where the number of samples is very small.


    dataset
        A dataset is a complete representation of a learning problem, combining feature data X and target data y.

        Datasets are often splitted into sub-datasets.
        One common splitting technique is the train-test split,
        where a part of the dataset is held out as a so-called training data used for fitting the estimator and
        another part is held out as a test dataset used for a final evaluation.

        When evaluating different settings (i.e. hyperparameters) for an estimator,
        yet another part of the dataset can be held out as a so-called validation set.
        Training proceeds on the training set, best parameters are found by evaluating against the validation set,
        and final evaluation can be done on the test set.
        Holding out a validation set can be avoided by using cross-validation for hyperparameter tuning.

        .. image:: img/dataset_tuning.png

    estimator

    evaluation metric
        Evaluation metrics give a measure of how well a model (e.g. a fitted classifier or regressor)  performs.

        See also https://scikit-learn.org/stable/modules/model_evaluation.html#

    feature
    features
    feature vector
        In QGIS and other GIS, the term feature is well defined as a logical element defined by a point,
        polyline or polygon inside a vector layer.
        In the context of the EnMAP-Box, we refere to it as geographic feature.

        In machine learning, a feature is a component in a so-called feature vector,
        which is a list of numeric quantities representing a sample in a dataset.
        A set of samples with feature data X and associated target data y or Y form a dataset.

        Elsewhere features are known as attributes, predictors, regressors, or independent variables.
        Estimators assume that features are numeric, finite and not missing.
        n_features indicates the number of features in a dataset.

    n_features
        The number of features in a dataset.

    n_outputs
        The number of outputs in a dataset.

    n_samples
        The number of samples in a dataset.

    n_targets
        Synonym for n_outputs.

    outputs
        Individual scalar/categorical variables per sample in the target.
        For example, in multilabel classification each possible label corresponds to a binary output.
        Also called responses, tasks or targets.

    regression
        The process of predicting a continuous-valued attribute associated with an object (e.g. pixel or profile).

    regressor
        A supervised predictor with continuous output values.

    sample
    samples
        We usually use this term as a noun to indicate a single feature vector.
        Elsewhere a sample is called an instance, data point, or observation.
        n_samples indicates the number of samples in a dataset, being the number of rows in a data array X.

    targets
        The dependent variable in supervised learning, passed as y to an estimator’s fit method.
        Also known as dependent variable, outcome variable, response variable, ground truth or label.

        See multiclass multioutput and continuous multioutput.

    test dataset
        The dataset used for final evaluation.

    training dataset
        The dataset used for training.

    transformer
        An estimator that transforms the input, usually only features X, into some transformed space (conventionally notated as Xt).

    validation dataset
        The dataset used for finding best parameters (i.e. hyperparameter tuning).

    X
        Denotes data that is observed at training and prediction time, used as independent variables in learning.
        The notation is uppercase to denote that it is ordinarily a matrix.

    y
    Y
        Denotes data that may be observed at training time as the dependent variable in learning,
        but which is unavailable at prediction time, and is usually the target of prediction.
        The notation may be uppercase to denote that it is a matrix, representing multi-output targets, for instance;
        but usually we use y and sometimes do so even when multiple outputs are assumed.
