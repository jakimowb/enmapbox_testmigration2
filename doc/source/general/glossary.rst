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

Index with all Terms
====================

:ref:`genindex`

GIS and Remote Sensing
======================

.. glossary::

    attribute
        A synonym for :term:`field`.

    attribute table
        A tabulated data table associated with a :term:`vector layer`.
        Table columns and rows are referred to as :term:`fields<field>` and :term:`geographic features<geographic feature>` respectively.

    attribute value
        Refers to a single cell value inside the :term:`attribute table` of a :term:`vector layer`.

    band
        A :term:`raster layer` is composed of one or multiple bands.

    categorized layer
        A :term:`categorized vector layer` or :term:`categorized raster layer`.

        .. image:: img/categorized_raster_layer.png
            :width: 24%
        .. image:: img/categorized_raster_layer_2.png
            :width: 24%
        .. image:: img/categorized_vector_layer.png
            :width: 24%
        .. image:: img/categorized_vector_layer_2.png
            :width: 24%

    categorized raster layer
        A :term:`raster layer` styled with a paletted/unique values renderer.
        The renderer defines the :term:`band` with :term:`category` values and a list of named and colored categories.
        Styles are usually stored as QML sidecar files.
        Category values don't have to be strictly consecutive.

        .. image:: img/categorized_raster_layer.png
            :width: 24%
        .. image:: img/categorized_raster_layer_2.png
            :width: 24%

        .. image:: img/categorized_raster_layer_styling.png

    categorized vector layer
        A :term:`vector layer` styled with a categorized symbol renderer.
        The renderer defines the :term:`field` storing the :term:`category` values
        (numbers or strings; expressions not yet supported) and a list of named and colored categories.
        Styles are usually stored as QML sidecar files.
        Note that in case of numerical category values, the values don’t have to be strictly consecutive.

        .. image:: img/categorized_vector_layer.png
            :width: 24%
        .. image:: img/categorized_vector_layer_2.png
            :width: 24%

        .. image:: img/categorized_vector_layer_styling.png

    categorized spectral library
        A :term:`spectral library` that is also a :term:`categorized vector layer`.

        .. image:: img/categorized_spectral_library.png

    category

    categories
        A category has a value, a name and a :term:`color`.

    classification layer
        A :term:`categorized raster layer` that is assumed to represent a mapping of a contiguous area.

        .. image:: img/categorized_raster_layer.png
            :width: 24%

        *Note that there is currently no equivalent term for a contiguous vector polygon layer. We may introduce it in the future as needed. For now we expect users to rasterize such a vector layer into a raster layer.*

    class probability layer
        A multi-band :term:`raster layer`, where the :term:`bands<band>` represent class probabilities (values between 0 and 1) for a set of :term:`categories`.

    class fraction layer
        A multi-band :term:`raster layer`, where the :term:`bands<band>` represent class cover fractions (values between 0 and 1) for a set of :term:`categories`.

    color
        An :term:`rgb-color`, :term:`hex-color` or :term:`int-color` specified by a red, green and blue component.
        Learn more here: https://htmlcolorcodes.com/

    continuous-valued raster layer
        A :term:`raster layer`, where each :term:`band` represents a continuous-valued variable.
        Variable names are given by the raster band names.

        .. image:: img/continuous-valued_raster_layer.png
            :width: 24%
        .. image:: img/continuous-valued_raster_layer_2.png
            :width: 24%

    continuous-valued vector layer
        A :term:`vector layer` with numeric :term:`fields<field>` representing continuous-valued variables.
        Variable names are given by field names.

        .. image:: img/continuous-valued_vector_layer.png
            :width: 24%
        .. image:: img/continuous-valued_vector_layer_2.png
            :width: 24%

    continuous-valued layer
        A :term:`continuous-valued vector layer` or :term:`continuous-valued raster layer`.

        .. image:: img/continuous-valued_raster_layer.png
            :width: 24%
        .. image:: img/continuous-valued_raster_layer_2.png
            :width: 24%

        .. image:: img/continuous-valued_vector_layer.png
            :width: 24%
        .. image:: img/continuous-valued_vector_layer_2.png
            :width: 24%

    field
        Refers to a single column inside the :term:`attribute table` of a :term:`vector layer`.

    geographic feature
        Refers to a single row inside the :term:`attribute table` of a :term:`vector layer`.
        In a :term:`vector layer`, a :term:`geographic feature` is a logical element defined by a point, polyline or polygon.

        Note that in the context of GIS, the epithet "geographic" in "geographic feature" is usually skipped.
        In the context of EnMAP-Box, and machine learning in general, the term "feature" is used differently.

        See :term:`feature` for details.

    grid
        A :term:`raster layer` defining the spatial extent, coordinate reference system and the pixel size.

    hex-color
        A :term:`color` specified by a 6-digit hex-color string,
        where each color component is represented by a two digit hexadecimal number,
        e.g. red `#FF0000`, green `#00FF00`, blue `#0000FF`, black `#000000`, white `#FFFFFF` and grey `#808080`.

    int-color
        A :term:`color` specified by a single integer between 0 and 256^3 - 1, which can also be represented as a :term:`hex-color`.

    labeled layer
        A :term:`categorized layer` or a :term:`continuous-valued layer`.

    layer
        A :term:`vector layer` or a :term:`raster layer`.

    layer style
        The style of a layer can be defined in the Layer Styling panel and the Styling tab of the Layer Properties dialog.
        Some applications and algorithms take advantage of style information, e.g. for extracting :term:`category` names and :term:`colors<color>`.

    mask layer
        A :term:`mask raster layer` or :term:`mask vector layer`.

        .. image:: img/mask_raster_layer.png
            :width: 24%
        .. image:: img/mask_raster_layer_2.png
            :width: 24%

        .. image:: img/mask_vector_layer.png
            :width: 24%
        .. image:: img/mask_vector_layer_2.png
            :width: 24%

    mask raster layer
        A :term:`raster layer` interpreted as a binary mask.
        All no data (zero, if missing), inf and nan pixel evaluate to false, all other to true.
        Note that only the first :term:`band` used by the renderer is considered.

        .. image:: img/mask_raster_layer.png
            :width: 24%
        .. image:: img/mask_raster_layer_2.png
            :width: 24%

    mask vector layer
        A :term:`vector layer` interpreted as a binary mask. Areas covered by a geometry evaluate to true, all other to false.

        .. image:: img/mask_vector_layer.png
            :width: 24%
        .. image:: img/mask_vector_layer_2.png
            :width: 24%

    pickle file
        A binary file ending on `.pkl` that contains a pickled Python object, usually a dictionary or list container.
        Pickle file content can be browsed via the EnMAP-Box Data Sources panel:

        .. image:: img/pickle_file.png

    pixel profile
        List of :term:`band` values for a single pixel in a :term:`raster layer`.

        .. image:: img/spectral_profile.png

    point layer
        A :term:`vector layer` with point geometries.

        .. image:: img/vector_layer_2.png
            :width: 24%

    polygon layer
        A :term:`vector layer` with polygon geometries.

        .. image:: img/vector_layer.png
            :width: 24%

    ployline layer
        A :term:`vector layer` with line geometries.

    raster layer
        Any raster file that can be opened in QGIS as `QgsRasterLayer`.
        Elsewhere known as an image.

        .. image:: img/raster_layer.png
            :width: 24%

    regression layer
        A :term:`continuous-valued raster layer` that is assumed to represent a mapping of a contiguous area.

        .. image:: img/continuous-valued_raster_layer.png
            :width: 24%

    rgb-color
        A :term:`color` specified by a triplet of byte values (values between 0 and 255) representing the red, green and blue color components, e.g. red (255, 0, 0), green (0, 255, 0), blue (0, 0, 255), black (0, 0, 0), white (255, 255, 255) and grey (128, 128, 128).

    RGB image
        A 3-band byte :term:`raster layer` with values ranging from 0 to 255.

    spectral band
        A :term:`band` inside a :term:`spectral raster layer`.
        A spectral band represents a measurement for a region of the electromagnetic spectrum around a specific :term:`center wavelength`.
        The region is typically described by a :term:`spectral response function`.

    spectral library
        A :term:`vector layer` with (at least) one special binary field containing pickled profile data and metadata.
        If a spectral library has exactly one such binary field, each :term:`geographic feature` represents one :term:`spectral profile`.
        In the case of `n` different binary fields, each geographic feature represents `n` profiles.

        A spectral library is a collection of profiles with arbitrary profile-wise data and metadata,
        stored as pickled dictionaries inside (multiple) binary fields.
        Dictionary items are:

        * `x`: list of x values (e.g. :term:`wavelength`)
        * `y`: list of y values (e.g. surface reflectance)
        * `xUnit`: x value units (e.g. nanometers)
        * `yUnit`: y value units (e.g. ???)
        * `bbl`: the :term:`bad bands list`

        See `enmapbox.externals.qps.speclib.core.SpectralLibrary` for details.

        .. image:: img/spectral_library.png

    spectral profile
        A :term:`pixel profile` in a :term:`spectral raster layer` or a profile in a :term:`spectral library`.

        .. image:: img/spectral_profile.png

    spectral raster layer
        A :term:`raster layer` where the individual bands (i.e. :term:`spectral bands<spectral band>`) represent measurements across the electromagnetic spectrum.
        The measurement vector of a single pixel is called a :term:`spectral profile`)

        .. image:: img/raster_layer.png
            :width: 24%

        .. image:: img/spectral_profile.png

    stratification layer
        A :term:`classification layer` that is used to stratify an area into distinct subareas.

        .. image:: img/categorized_raster_layer.png
            :width: 24%

    stratum
    strata
        A :term:`category` of a `classifcation layer` that is used as a :term:`stratification layer`.
        Conceptually, a stratum can be seen as a binary mask with all pixels inside the stratum evaluating to True and all other pixels evaluating to False.

    table
        A :term:`vector layer` with (potentially) missing geometry.

        *Note that in case of missing geometry, the vector layer icon looks like a table and layer styling is disabled.*

        .. image:: img/table.png

    vector feature
        Synonym for :term:`geographic feature`.

    vector layer
        Any vector file that can be opened in QGIS as `QgsVectorLayer`.

        .. image:: img/vector_layer.png
            :width: 24%
        .. image:: img/vector_layer_2.png
            :width: 24%

Raster Metadata
===============

.. glossary::

    band description
    band name
        Defined by GDAL data model. Accessible via `gdal.Band.GetDescription()`.

    bbl
    bad bands list
        List of bad band multiplier values of each :term:`band`, typically 0 for bad bands and 1 for good bands.


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
        The process of identifying which :term:`category` an object belongs to.

    classifier
        A supervised :term:`estimator` with a finite set of discrete possible :term:`output` values.

    clusterer
        An unsupervised :term:`estimator` with a finite set of discrete :term:`output` values.

    clustering
        The process of automatic grouping of similar objects into sets.

    cross-validation
        The training :term:`dataset` is split into k smaller sets and the following procedure is followed for each of the k "folds":

        * a model is trained using k-1 of the folds as training dataset

        * the resulting model is used to predict the :term:`targets` of the remaining part of the dataset

        The performance can now be calculated from the predictions for the whole training dataset.

        .. image:: img/dataset_cross-val.png

        This approach can be computationally expensive,
        but does not waste too much data (as is the case when fixing an arbitrary :term:`validation set`),
        which is a major advantage in problems where the number of :term:`samples<sample>` is very small.


    dataset
        A dataset is a complete representation of a learning problem, combining :term:`feature` data :term:`X` and :term:`target` data :term:`y`.
        Datasets are often splitted into sub-datasets.
        One common splitting technique is the train-test split,
        where a part of the dataset is held out as a so-called :term:`training dataset` used for fitting the :term:`estimator` and
        another part is held out as a :term:`test dataset` used for a final evaluation.

        When evaluating different settings (i.e. hyperparameters) for an :term:`estimator`,
        yet another part of the dataset can be held out as a so-called :term:`validation dataset`.
        Training proceeds on the training dataset,
        best parameters are found by evaluating against the validation dataset,
        and final evaluation can be done on the test dataset.
        Holding out a validation datase can be avoided by using :term:`cross-validation` for hyperparameter tuning.

        .. image:: img/dataset_tuning.png

    estimator
        An object which manages the estimation of a model. The model is estimated as a deterministic function.

    evaluation metric
        Evaluation metrics give a measure of how well a model (e.g. a :term:`classifier` or :term:`regressor`)  performs.

        See also https://scikit-learn.org/stable/modules/model_evaluation

    feature
    feature vector
        In QGIS and other GIS, the term feature is well defined as a logical element defined by a point,
        polyline or polygon inside a :term:`vector layer`.
        In the context of the EnMAP-Box, we refere to it as :term:`geographic feature`.

        In machine learning, a feature is a component in a so-called feature vector,
        which is a list of numeric quantities representing a :term:`sample` in a :term:`dataset`.
        A set of samples with feature data :term:`X` and associated target data :term:`y` or Y form a dataset.

        Elsewhere features are known as attributes, predictors, regressors, or independent variables.
        Estimators assume that features are numeric, finite and not missing.
        :term:`n_features` indicates the number of features in a dataset.

    n_features
        The number of :term:`features` in a :term:`dataset`.

    n_outputs
        The number of :term:`outputs<output>` in a :term:`dataset`.

    n_samples
        The number of :term:`samples<sample>` in a :term:`dataset`.

    n_targets
        Synonym for :term:`n_outputs`.

    output
        Individual scalar/categorical variables per :term:`sample` in the :term:`target`.

        Also called responses, tasks or targets.

    regression
        The process of predicting a continuous-valued attribute associated with an object.

    regressor
        A supervised :term:`estimator` with continuous :term:`output` values.

    sample
        We usually use this term as a noun to indicate a single :term:`feature vector`.

        Elsewhere a sample is called an instance, data point, or observation.
        :term:`n_samples` indicates the number of samples in a dataset,
        being the number of rows in a data array :term:`X`.

    target
        The dependent variable in supervised learning, passed as :term:`y` to an :term:`estimator`'s fit method.

        Also known as dependent variable, outcome variable, response variable, ground truth or label.

    test dataset
        The :term:`dataset` used for final evaluation.

    training dataset
        The :term:`dataset` used for training.

    transformer
        An :term:`estimator` that transforms the input, usually only feature data :term:`X`,
        into some transformed space (conventionally notated as Xt).

    validation dataset
        The :term:`dataset` used for finding best parameters (i.e. hyperparameter tuning).

    X
        Denotes data that is observed at training and prediction time, used as independent variables in learning.
        The notation is uppercase to denote that it is ordinarily a matrix.

    y
    Y
        Denotes data that may be observed at training time as the dependent variable in learning,
        but which is unavailable at prediction time, and is usually the target of prediction.
        The notation may be uppercase to denote that it is a matrix, representing multi-output targets, for instance;
        but usually we use y and sometimes do so even when multiple :term:`outputs<output>` are assumed.
