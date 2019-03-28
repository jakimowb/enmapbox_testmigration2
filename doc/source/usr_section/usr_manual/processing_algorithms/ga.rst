Processing Algorithms
#####################

Accuracy Assessment
===================

Classification Performance
--------------------------

Assesses the performance of a classification.

Prediction
~~~~~~~~~~

Specify classification raster be evaluated

Reference
~~~~~~~~~

Specify reference classification raster (i.e. ground truth).

HTML Report
~~~~~~~~~~~

Specify output path for HTML report file (.html).

....


Clustering Performance
----------------------

Assesses the performance of a clusterer.

Prediction
~~~~~~~~~~

Specify clustering raster to be evaluated.

Reference
~~~~~~~~~

Specify reference clustering raster (i.e. ground truth).

HTML Report
~~~~~~~~~~~

Specify output path for HTML report file (.html).

....


ClassProbability Performance
----------------------------

Assesses the performance of class probabilities in terms of AUC and ROC curves.

Prediction
~~~~~~~~~~

Specify class probability raster to be evaluated.

Reference
~~~~~~~~~

Specify reference classification raster (i.e. ground truth).

HTML Report
~~~~~~~~~~~

Specify output path for HTML report file (.html).

....

Regression Performance
----------------------

Assesses the performance of a regression.

Prediction
~~~~~~~~~~

Specify regression raster to be evaluated.

Reference
~~~~~~~~~

Specify reference regression raster (i.e. ground truth).

HTML Report
~~~~~~~~~~~

Specify output path for HTML report file (.html).

....

Auxilliary
==========

ClassDefinition from Raster
---------------------------

Creates a Class Definition string from a classification input raster for the usage in other EnMAP-Box algorithms (e.g. 'Classification from Vector'). See Log window for result.

Raster
~~~~~~

Specify raster with defined class definition, e.g. classification or class probability raster

....

Create additional Testdata
--------------------------

Based on the testdata additional datasets will be created using existing EnMAP-Box algorithms with predefined settings.

LandCover L2 Classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for LandCover L2 Classification.

LandCover L2 ClassProbability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for LandCover L2 ClassProbability.

Output Sample
~~~~~~~~~~~~~

Specify output path for sample (.pkl).

Output ClassificationSample
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

Output ClassProbabilitySample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

Output RegressionSample
~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

Open Testdata
-------------

Opens testdata into current QGIS project (LandCov_BerlinUrbanGradient.shp, HighResolution_BerlinUrbanGradient.bsq, EnMAP_BerlinUrbanGradient.bsq, SpecLib_BerlinUrbanGradient.sli).

EnMAP (30m; 177 bands)
~~~~~~~~~~~~~~~~~~~~~~

File name: EnMAP_BerlinUrbanGradient.bsq

Simulated EnMAP data (based on 3.6m HyMap imagery) acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). It has a spectral resolution of 177 bands and a spatial resolution of 30m.

HyMap (3.6m; Blue, Green, Red, NIR bands)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

File name: HighResolution_BerlinUrbanGradient.bsq

HyMap image acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km² (2.4 x 1.8 km). This dataset was reduced to 4 bands (0.483, 0.558, 0.646 and 0.804 micrometers). The spatial resolution is 3.6m.

LandCover Layer
~~~~~~~~~~~~~~~

File name: LandCov_BerlinUrbanGradient.shp

Polygon shapefile containing land cover information on two classification levels. Derived from very high resolution aerial imagery and cadastral datasets.

Level 1 classes: Impervious; Other; Vegetation; Soil

Level 2 classes: Roof; Low vegetation; Other; Pavement; Tree; Soil

ENVI Spectral Library
~~~~~~~~~~~~~~~~~~~~~

File name: SpecLib_BerlinUrbanGradient.sli

Spectral library with 75 spectra (material level, level 2 and level 3 class information)

....

Scale Sample Features
---------------------

Scales the features of a sample by a user defined factor (can be used for matching datasets).
Use case: A sample from a spectral library should be used for classifying a raster. The spectral library sample has float surface reflectance values between 0 and 1 and the raster integer surface reflectances between 0 and 1000. In order to match the datasets, you can rescale the sample by a factor of 1000.

Sample
~~~~~~

Specify path to sample file (.pkl).

Scale factor
~~~~~~~~~~~~

Scale factor that is applied to all features.

Output Sample
~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

Unique Values from Vector Attribute 
------------------------------------

This algorithm returns unique values from vector attributes as a list, which is also usable as Class Definition in other algorithms. The output will be shown in the log window and can the copied from there accordingly.

Vector
~~~~~~

Specify input vector.

Field
~~~~~

Specify field of vector layer for which unique values should be derived.

....

Classification
==============

Fit GaussianProcessClassifier
-----------------------------

Fits Gaussian Process Classifier. See `Gaussian Processes <http://scikit-learn.org/stable/modules/gaussian_process.html>`_ for further information.

ClassificationSample
~~~~~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `GaussianProcessClassifier <http://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html>`_ for information on different parameters.

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassProbability'.

....

Fit LinearSVC
-------------

Fits a linear Support Vector Classification. Input data will be scaled and grid search is used for model selection.

ClassificationSample
~~~~~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `LinearSVC <http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html>`_. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassProbability'.

....

Fit RandomForestClassifier
--------------------------

Fits a Random Forest Classifier

ClassificationSample
~~~~~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `RandomForestClassifier <http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html>`_ for information on different parameters. If this code is not altered, scikit-learn default settings will be used. 'Hint: you might want to alter e.g. the n_estimators value (number of trees), as the default is 10. So the line of code might be altered to 'estimator = RandomForestClassifier(n_estimators=100).'

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassProbability'.

....

Fit SVC
-------

Fits a Support Vector Classification. Input data will be scaled and grid search is used for model selection.

ClassificationSample
~~~~~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `SVC <http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html>`_. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassProbability'.

....

Predict Classification
----------------------

Applies a classifier to a raster.

Raster
~~~~~~

Select raster file which should be classified.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Classifier
~~~~~~~~~~

Select path to a classifier file (.pkl).

Output Classification
~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

....

Predict ClassProbability
------------------------

Applies a classifier to a raster.

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Classifier
~~~~~~~~~~

Select path to a classifier file (.pkl).

Prediction
~~~~~~~~~~

Specify output path for raster.

....

Clustering
==========

Fit AffinityPropagation
-----------------------

Fits a Affinity Propagation clusterer (input data will be scaled).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `AffinityPropagation <http://scikit-learn.org/stable/modules/generated/sklearn.cluster.AffinityPropagation.html>`_. See `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for information on scaling

Output Clusterer
~~~~~~~~~~~~~~~~

Specifiy output path for the clusterer (.pkl). This file can be used for applying the clusterer to an image using 'Clustering -> Predict Clustering'.

....

Fit Birch
---------

Fits a Birch clusterer (input data will be scaled).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `Birch <http://scikit-learn.org/stable/modules/generated/sklearn.cluster.Birch.html>`_. See `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for information on scaling

Output Clusterer
~~~~~~~~~~~~~~~~

Specifiy output path for the clusterer (.pkl). This file can be used for applying the clusterer to an image using 'Clustering -> Predict Clustering'.

....

Fit KMeans
----------

Fits a KMeans clusterer (input data will be scaled).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `KMeans <http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html>`_. See `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for information on scaling

Output Clusterer
~~~~~~~~~~~~~~~~

Specifiy output path for the clusterer (.pkl). This file can be used for applying the clusterer to an image using 'Clustering -> Predict Clustering'.

....

Fit MeanShift
-------------

Fits a MeanShift clusterer (input data will be scaled).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `MeanShift <http://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html>`_. See `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for information on scaling

Output Clusterer
~~~~~~~~~~~~~~~~

Specifiy output path for the clusterer (.pkl). This file can be used for applying the clusterer to an image using 'Clustering -> Predict Clustering'.

....

Predict Clustering
------------------

Applies a clusterer to a raster.

Raster
~~~~~~

Select raster file which should be clustered.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Clusterer
~~~~~~~~~

Select path to a clusterer file (.pkl).

Clustering
~~~~~~~~~~

Specify output path for classification raster.

....

Create Raster
=============

Classification from ClassProbability
------------------------------------

Creates classification from class probability. Winner class is equal to the class with maximum class probability.

ClassProbability
~~~~~~~~~~~~~~~~

Specify input raster.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Output Classification
~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

....

Classification from Vector
--------------------------

Creates a classification from a vector field with class ids.

PixelGrid
~~~~~~~~~

Specify input raster.

Vector
~~~~~~

Specify input vector.

Class id attribute
~~~~~~~~~~~~~~~~~~

Vector field specifying the class ids.

Class Definition
~~~~~~~~~~~~~~~~

Enter a class definition, e.g.:

ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])

For supported named colors see the `W3C recognized color keyword names <https://www.w3.org/TR/SVG/types.html#ColorKeywords>`_.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Oversampling factor
~~~~~~~~~~~~~~~~~~~

Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.

Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

Output Classification
~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

....

ClassProbability from Classification
------------------------------------

Derive (binarized) class probabilities from a classification.

Classification
~~~~~~~~~~~~~~

Specify input raster.

Output ClassProbability
~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for class probability raster.

....

ClassProbability from Vector
----------------------------

Derives class probability raster from a vector file with sufficient class information.

PixelGrid
~~~~~~~~~

Specify input raster.

Vector
~~~~~~

Specify input vector.

Class id attribute
~~~~~~~~~~~~~~~~~~

Vector field specifying the class ids.

Class Definition
~~~~~~~~~~~~~~~~

Enter a class definition, e.g.:

ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])

For supported named colors see the `W3C recognized color keyword names <https://www.w3.org/TR/SVG/types.html#ColorKeywords>`_.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Oversampling factor
~~~~~~~~~~~~~~~~~~~

Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.

Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

Output ClassProbability
~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for class probability raster.

....

Raster from Vector
------------------

Converts vector to raster (using `gdal rasterize <http://gdal.org/python/osgeo.gdal-module.html#RasterizeOptions>`_).

PixelGrid
~~~~~~~~~

Specify input raster.

Vector
~~~~~~

Specify input vector.

Init Value
~~~~~~~~~~

Pre-initialization value for the output raster before burning. Note that this value is not marked as the nodata value in the output raster.

Burn Value
~~~~~~~~~~

Fixed value to burn into each pixel, which is covered by a feature (point, line or polygon).

Burn Attribute
~~~~~~~~~~~~~~

Specify numeric vector field to use as burn values.

All touched
~~~~~~~~~~~

Enables the ALL_TOUCHED rasterization option so that all pixels touched by lines or polygons will be updated, not just those on the line render path, or whose center point is within the polygon.

Filter SQL
~~~~~~~~~~

Create SQL based feature selection, so that only selected features will be used for burning.

Example: Level_2 = 'Roof' will only burn geometries where the Level_2 attribute value is equal to 'Roof', others will be ignored. This allows you to subset the vector dataset on-the-fly.

Data Type
~~~~~~~~~

Specify output datatype.

No Data Value
~~~~~~~~~~~~~

Specify output no data value.

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Create Sample
=============

ClassificationSample from ENVI Spectral Library
-----------------------------------------------

Derive ClassificationSample from ENVI Spectral Library.

ENVI Spectral Library
~~~~~~~~~~~~~~~~~~~~~

Select path to an ENVI (e.g. .sli or .esl).

ClassDefinition prefix
~~~~~~~~~~~~~~~~~~~~~~

Class definition prefixes allow the selection of a specific class definition (i.e. 'class names' and 'class lookup') and class mapping (i.e. 'class spectra names') stored in the spectral library .hdr file).

For example, inside the `EnMAP-Box testdata spectral library <file:///C:\Work\source\enmap-box-testdata\enmapboxtestdata\SpecLib_BerlinUrbanGradient.hdr>`_, the prefixes 'level 1' and 'level 2' are defined.

Output ClassificationSample
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassificationSample from ClassProbabilitySample
------------------------------------------------

Derive ClassificationSample from ClassProbabilitySample. Winner class is selected by the maximum probability decision.

ClassProbabilitySample
~~~~~~~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Output ClassificationSample
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassificationSample from Raster and ClassProbability
-----------------------------------------------------

Derives classification sample from raster and class probability raster.

Raster
~~~~~~

Specify input raster.

ClassProbability
~~~~~~~~~~~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Output ClassificationSample
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassificationSample from Raster and Vector
-------------------------------------------

Derives classification sample from raster and vector.

Raster
~~~~~~

Specify input raster.

Vector
~~~~~~

Specify input vector.

Class id attribute
~~~~~~~~~~~~~~~~~~

Vector field specifying the class ids.

Class Definition
~~~~~~~~~~~~~~~~

Enter a class definition, e.g.:

ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])

For supported named colors see the `W3C recognized color keyword names <https://www.w3.org/TR/SVG/types.html#ColorKeywords>`_.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Oversampling factor
~~~~~~~~~~~~~~~~~~~

Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.

Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Output ClassificationSample
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassProbabilitySample from synthetically mixed ClassificationSample
--------------------------------------------------------------------

Derives a class probability sample by synthetically mixing (pure) spectra from a ClassificationSample.

ClassificationSample
~~~~~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

n
~

Total number of samples to be generated.

Likelihood for mixing complexity 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifies the probability of mixing spectra from 2 classes.

Likelihood for mixing complexity 3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifies the probability of mixing spectra from 3 classes.

Class likelihoods
~~~~~~~~~~~~~~~~~

Specifies the likelihoods for drawing spectra from individual classes.

In case of 'equalized', all classes have the same likelihhod to be drawn from.

In case of 'proportional', class likelihoods scale with their sizes.

Output ClassProbabilitySample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassificationSample from Raster and Classification
---------------------------------------------------

Derives a classification sample from raster (defines the grid) and classification.

Raster
~~~~~~

Specify input raster.

Classification
~~~~~~~~~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Output ClassificationSample
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassProbabilitySample from ClassificationSample
------------------------------------------------

Derives a class probability sample from a classification sample.

ClassificationSample
~~~~~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Output ClassProbabilitySample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassProbabilitySample from Raster and Classification
-----------------------------------------------------

Derives a class probability sample from raster and classification.

Raster
~~~~~~

Specify input raster.

Classification
~~~~~~~~~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Output ClassProbabilitySample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassProbabilitySample from Raster and ClassProbability
-------------------------------------------------------

Derives class probability sample from raster and class probability.

Raster
~~~~~~

Specify input raster.

ClassProbability
~~~~~~~~~~~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Output ClassProbabilitySample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

ClassProbabilitySample from Raster and Vector
---------------------------------------------

Derives class probability sample from raster and vector.

Raster
~~~~~~

Specify input raster.

Vector
~~~~~~

Specify input vector.

Class id attribute
~~~~~~~~~~~~~~~~~~

Vector field specifying the class ids.

Class Definition
~~~~~~~~~~~~~~~~

Enter a class definition, e.g.:

ClassDefinition(names=['Urban', 'Forest', 'Water'], colors=['red', '#00FF00', (0, 0, 255)])

For supported named colors see the `W3C recognized color keyword names <https://www.w3.org/TR/SVG/types.html#ColorKeywords>`_.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal winner class coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Oversampling factor
~~~~~~~~~~~~~~~~~~~

Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.

Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Output ClassProbabilitySample
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

RegressionSample from Raster and Regression
-------------------------------------------

Derives Regression sample from raster and regression.

Raster
~~~~~~

Specify input raster.

Regression
~~~~~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Output RegressionSample
~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

UnsupervisedSample from ENVI Spectral Library
---------------------------------------------

Derives unsupervised sample from ENVI spectral library.

ENVI Spectral Library
~~~~~~~~~~~~~~~~~~~~~

Select path to an ENVI (e.g. .sli or .esl).

Output Sample
~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

UnsupervisedSample from raster and mask
---------------------------------------

Derives unsupervised sample from raster and mask.

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Output Sample
~~~~~~~~~~~~~

Specify output path for sample (.pkl).

....

Masking
=======

Build Mask from Raster
----------------------

Builds a mask from a raster based on user defined values and value ranges.

Raster
~~~~~~

Specify input raster.

Foreground values
~~~~~~~~~~~~~~~~~

List of values that are mapped to True, e.g. [1, 2, 5].

Foreground ranges
~~~~~~~~~~~~~~~~~

List of [min, max] ranges, e.g. [[1, 3], [5, 7]]. Values inside those ranges are mapped to True.

Background values
~~~~~~~~~~~~~~~~~

List of values that are mapped to False, e.g. [1, 2, 5].

Background ranges
~~~~~~~~~~~~~~~~~

List of [min, max] ranges, e.g. [[-999, 0], [10, 255]]. Values inside those ranges are mapped to False.

Output Mask
~~~~~~~~~~~

Specify output path for mask raster.

....

Apply Mask to Raster. Pixels that are masked out are set to the raster no data value.
-------------------------------------------------------------------------------------



Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Masked Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Post-Processing
===============

ClassProbability as RGB Raster
------------------------------

Creates a RGB representation from given class probabilities. The RGB color of a specific pixel is the weighted mean value of the original class colors, where the weights are given by the corresponding class propability.


ClassProbability
~~~~~~~~~~~~~~~~

Specify input raster.

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Random
======

Random Points from Classification
---------------------------------

Randomly samples a user defined amount of points/pixels from a classification raster and returns them as a vector dataset.

Classification
~~~~~~~~~~~~~~

Specify input raster.

Number of Points per Class
~~~~~~~~~~~~~~~~~~~~~~~~~~

Has to be a number or a list of numbers. When a single integer number is given (e.g. 100), equalised random sample will be taken, i.e. in this case 100 samples per class. For taking a disproportional random sample, where the amount of samples should differ between classes, provide a list of numbers. This list has to have as many arguments as classes in the classification and has to be ordered according to the classes (e.g. '[100, 70, 90]' in the case of three classes, 100 samples will be taken from the first class, 70 from the second, etc.). For a proportional stratified random sampling provide a float value between 0 and 1 (e.g. 0.3 for randomly drawing 30% of pixels in each class).

Output Vector
~~~~~~~~~~~~~

Specify output path for the vector.

....

Random Points from Mask
-----------------------

Randomly draws defined number of points from Mask and returns them as vector dataset.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Number of Points
~~~~~~~~~~~~~~~~

Number of points to sample from mask.

Output Vector
~~~~~~~~~~~~~

Specify output path for the vector.

....

Regression
==========

Fit GaussianProcessRegressor
----------------------------

Fits Gaussian Process Regression. See `Gaussian Processes <http://scikit-learn.org/stable/modules/gaussian_process.html>`_ for further information.

RegressionSample
~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `GaussianProcessRegressor <http://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html>`_ for information on different parameters.

Output Regressor
~~~~~~~~~~~~~~~~

Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

....

Fit KernelRidge
---------------

Fits a KernelRidge Regression. Click `here <http://scikit-learn.org/stable/modules/kernel_ridge.html>`_ for additional information.

RegressionSample
~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `KernelRidge <http://scikit-learn.org/stable/modules/generated/sklearn.kernel_ridge.KernelRidge.html>`_ for information on different parameters. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

Output Regressor
~~~~~~~~~~~~~~~~

Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

....

Fit LinearSVR
-------------

Fits a Linear Support Vector Regression.

RegressionSample
~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `LinearSVR <http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVR.html>`_ for information on different parameters. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

Output Regressor
~~~~~~~~~~~~~~~~

Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

....

Fit RandomForestRegressor
-------------------------

Fits a Random Forest Regression.

RegressionSample
~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `RandomForestRegressor <http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>`_ for information on different parameters.

Output Regressor
~~~~~~~~~~~~~~~~

Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

....

Fit SVR
-------

Fits a Support Vector Regression.

RegressionSample
~~~~~~~~~~~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `SVR <http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html>`_ for information on different parameters. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

Output Regressor
~~~~~~~~~~~~~~~~

Specifiy output path for the regressor (.pkl). This file can be used for applying the regressor to an image using 'Regression -> Predict Regression'.

....

Predict Regression
------------------

Applies a regressor to an raster.

Raster
~~~~~~

Select raster file which should be regressed.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Regressor
~~~~~~~~~

Select path to a regressor file (.pkl).

Output Regression
~~~~~~~~~~~~~~~~~

Specify output path for regression raster.

....

Transformation
==============

Fit FactorAnalysis
------------------

Fits a Factor Analysis.

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `FactorAnalysis <http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FactorAnalysis.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit FastICA
-----------

Fits a FastICA (Independent Component Analysis).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `FastICA <http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FastICA.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit FeatureAgglomeration
------------------------

Fits a Feature Agglomeration.

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `FeatureAgglomeration <http://scikit-learn.org/stable/modules/generated/sklearn.cluster.FeatureAgglomeration.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit Imputer
-----------

Fits an Imputer (Imputation transformer for completing missing values).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `Imputer <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Imputer.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit KernelPCA
-------------

Fits a Kernel PCA (Principal Component Analysis).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `KernelPCA <http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit MaxAbsScaler
----------------

Fits a MaxAbsScaler (scale each feature by its maximum absolute value). See also `examples for different scaling methods <http://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>`_.

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `MaxAbsScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MaxAbsScaler.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit MinMaxScaler
----------------

Fits a MinMaxScaler (transforms features by scaling each feature to a given range). See also `examples for different scaling methods <http://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>`_.

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `MinMaxScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit Normalizer
--------------

Fits a Normalizer (normalizes samples individually to unit norm). See also `examples for different scaling methods <http://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>`_.

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `Normalizer <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Normalizer.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit PCA
-------

Fits a PCA (Principal Component Analysis).

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `PCA <http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit QuantileTransformer
-----------------------

Fits a Quantile Transformer (transforms features using quantiles information). See also `examples for different scaling methods <http://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>`_

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `quantile_transform <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.quantile_transform.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit RobustScaler
----------------

Fits a Robust Scaler (scales features using statistics that are robust to outliers). Click `here <http://scikit-learn.org/0.18/auto_examples/preprocessing/plot_robust_scaling.html>`_ for example. See also `examples for different scaling methods <http://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>`_.

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `RobustScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Fit StandardScaler
------------------

Fits a Standard Scaler (standardizes features by removing the mean and scaling to unit variance). See also `examples for different scaling methods <http://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html>`_.

Sample
~~~~~~

Specify path to sample file (.pkl).

Code
~~~~

Scikit-learn python code. See `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for information on different parameters.

Output Transformer
~~~~~~~~~~~~~~~~~~

Specifiy output path for the transformer (.pkl). This file can be used for applying the transformer to an image using 'Transformation -> Transform Raster' and 'Transformation -> InverseTransform Raster'.

....

Transform Raster
----------------

Applies a transformer to an raster.

Raster
~~~~~~

Select raster file which should be regressed.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Transformer
~~~~~~~~~~~

Select path to a transformer file (.pkl).

Transformation
~~~~~~~~~~~~~~

Specify output path for raster.

....

InverseTransform Raster
-----------------------

Performs an inverse transformation on an previously transformed raster (i.e. output of 'Transformation -> Transform Raster'). Works only for transformers that have an 'inverse_transform(X)' method. See scikit-learn documentations.

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Transformer
~~~~~~~~~~~

Select path to a transformer file (.pkl).

Inverse Transformation
~~~~~~~~~~~~~~~~~~~~~~

Specify output path for raster.

....

