GeoAlgorithms
#############

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

Fraction Performance
--------------------

Assesses the performance of class fractions in terms of AUC and ROC curves.

Prediction
~~~~~~~~~~

Specify class fraction raster to be evaluated.

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

Specify raster with defined class definition, e.g. classification or class fraction raster

....

Create additional Testdata
--------------------------

Based on the testdata additional datasets will be created using existing EnMAP-Box algorithms with predefined settings.

Create 30 m maps
~~~~~~~~~~~~~~~~

undocumented parameter

Create 3.6 m maps
~~~~~~~~~~~~~~~~~

undocumented parameter

Create labeled Library
~~~~~~~~~~~~~~~~~~~~~~

undocumented parameter

LandCover Classification for 6 classes at 30 m
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

LandCover Fraction for 6 classes at 30 m
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for fraction raster.

LandCover Classification for 6 classes at 3.6 m
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

LandCover Fraction for 6 classes at 3.6 m
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify output path for fraction raster.

Library with 30 m profiles and classification/fraction labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

undocumented parameter

....

Import Library
--------------

Import Library profiles and labels as Raster.

Library
~~~~~~~

Select path to an ENVI (e.g. .sli or .esl).

Import Profiles
~~~~~~~~~~~~~~~

undocumented parameter

Import Classification Labels (by classification scheme name)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

undocumented parameter

Import Regression Labels (by output names)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

undocumented parameter

Import Fraction Labels (by output names)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

undocumented parameter

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

Output Classification
~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

Output Regression
~~~~~~~~~~~~~~~~~

Specify output path for regression raster.

Output Fraction
~~~~~~~~~~~~~~~

Specify output path for fraction raster.

....

Open Test Maps
--------------

Opens testdata into current QGIS project (LandCov_BerlinUrbanGradient.shp, HighResolution_BerlinUrbanGradient.bsq, EnMAP_BerlinUrbanGradient.bsq, SpecLib_BerlinUrbanGradient.sli).

EnMAP (30m; 177 bands)
~~~~~~~~~~~~~~~~~~~~~~

File name: EnMAP_BerlinUrbanGradient.bsq

Simulated EnMAP data (based on 3.6m HyMap imagery) acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). It has a spectral resolution of 177 bands and a spatial resolution of 30m.

HyMap (3.6m; Blue, Green, Red, NIR bands)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

File name: HighResolution_BerlinUrbanGradient.bsq

HyMap image acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). This dataset was reduced to 4 bands (0.483, 0.558, 0.646 and 0.804 micrometers). The spatial resolution is 3.6m.

LandCover Layer
~~~~~~~~~~~~~~~

File name: LandCov_BerlinUrbanGradient.shp

Polygon shapefile containing land cover information on two classification levels. Derived from very high resolution aerial imagery and cadastral datasets.

Level 1 classes: Impervious; Other; Vegetation; Soil

Level 2 classes: Roof; Low vegetation; Other; Pavement; Tree; Soil

Library as Raster
~~~~~~~~~~~~~~~~~

File name: SpecLib_BerlinUrbanGradient.sli

Spectral library with 75 spectra (material level, level 2 and level 3 class information)

....

Open Test Library
-----------------

....

Unique Values from Raster Band
------------------------------

This algorithm returns unique values from a raster band as a list. The output will be shown in the log window and can the copied from there accordingly.

Raster
~~~~~~

Specify input raster.

Band
~~~~

Specify input raster band.

....

View Raster Metadata
--------------------

Prints all Raster metadata to log.

Raster
~~~~~~

Specify input raster.

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

Code
~~~~

Scikit-learn python code. See `GaussianProcessClassifier <http://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html>`_ for information on different parameters.

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassFraction'.

....

Fit LinearSVC
-------------

Fits a linear Support Vector Classification. Input data will be scaled and grid search is used for model selection.

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

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `LinearSVC <http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html>`_. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassFraction'.

....

Fit RandomForestClassifier
--------------------------

Fits a Random Forest Classifier

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

Code
~~~~

Scikit-learn python code. See `RandomForestClassifier <http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html>`_ for information on different parameters. If this code is not altered, scikit-learn default settings will be used. 'Hint: you might want to alter e.g. the n_estimators value (number of trees), as the default is 10. So the line of code might be altered to 'estimator = RandomForestClassifier(n_estimators=100).'

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassFraction'.

....

Fit SVC
-------

Fits a Support Vector Classification. Input data will be scaled and grid search is used for model selection.

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

Code
~~~~

Scikit-learn python code. For information on different parameters have a look at `SVC <http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html>`_. See `GridSearchCV <http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html>`_ for information on grid search and `StandardScaler <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>`_ for scaling.

Output Classifier
~~~~~~~~~~~~~~~~~

Specifiy output path for the classifier (.pkl). This file can be used for applying the classifier to an image using 'Classification -> Predict Classification' and 'Classification -> Predict ClassFraction'.

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

Predict Class Probability
-------------------------

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

Probability
~~~~~~~~~~~

Specify output path for fraction raster.

....

Clustering
==========

Fit AffinityPropagation
-----------------------

Fits a Affinity Propagation clusterer (input data will be scaled).

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Convolution, Morphology and Filtering
=====================================

Spatial Convolution AiryDisk2DKernel
------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Convolution Box2DKernel
-------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Convolution Gaussian2DKernel
------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Convolution MexicanHat2DKernel
--------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Convolution Moffat2DKernel
----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Convolution Ring2DKernel
--------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Convolution Tophat2DKernel
----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Convolution TrapezoidDisk2DKernel
-----------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spectral Convolution Box1DKernel
--------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spectral Convolution Gaussian1DKernel
-------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spectral Convolution MexicanHat1DKernel
---------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spectral Convolution SavitzkyGolay1DKernel
------------------------------------------

Applies `Savitzki Golay Filter <https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter>`_.

Raster
~~~~~~

Specify input raster.

Code
~~~~

Python code. See `scipy.signal.savgol_coeffs <http://scipy.github.io/devdocs/generated/scipy.signal.savgol_coeffs.html#scipy.signal.savgol_coeffs>`_ for information on different parameters.

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spectral Convolution Trapezoid1DKernel
--------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Binary Closing
------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Binary Dilation
-------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Binary Erosion
------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Binary Fill Holes
---------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Binary Opening
------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Binary Propagation
----------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Black Tophat
----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Gradient
------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Grey Closing
----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Grey Dilation
-----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Grey Erosion
----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Grey Opening
----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological Laplace
-----------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Morphological White Tophat
----------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Gaussian Gradient Magnitude
------------------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Generic Filter
-----------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Laplace
----------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Maximum Filter
-----------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Median Filter
----------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Minimum Filter
-----------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Percentile Filter
--------------------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Prewitt
----------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial  Sobel
--------------

undocumented

Raster
~~~~~~

Specify input raster.

Code
~~~~

undocumented

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Create Raster
=============

Classification from Fraction
----------------------------

Creates classification from class fraction. Winner class is equal to the class with maximum class fraction.

ClassFraction
~~~~~~~~~~~~~

Specify input raster.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal dominant coverage
~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Output Classification
~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

....

Classification from Vector
--------------------------

Creates a classification from a vector field with class ids.

Pixel Grid
~~~~~~~~~~

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

Minimal dominant coverage
~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Oversampling factor
~~~~~~~~~~~~~~~~~~~

Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.

Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

Output Classification
~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

....

Fraction from Classification
----------------------------

Derive (binarized) class fractions from a classification.

Classification
~~~~~~~~~~~~~~

Specify input raster.

Output Fraction
~~~~~~~~~~~~~~~

Specify output path for fraction raster.

....

Fraction from Vector
--------------------

Derives class fraction raster from a vector file with sufficient class information.

Pixel Grid
~~~~~~~~~~

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

Minimal dominant coverage
~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Oversampling factor
~~~~~~~~~~~~~~~~~~~

Defines the degree of detail by which the class information given by the vector is rasterized. An oversampling factor of 1 (default) simply rasterizes the vector on the target pixel grid.An oversampling factor of 2 will rasterize the vector on a target pixel grid with resolution twice as fine.An oversampling factor of 3 will rasterize the vector on a target pixel grid with resolution three times as fine, ... and so on.

Mind that larger values are always better (more accurate), but depending on the inputs, this process can be quite computationally intensive, when a higher factor than 1 is used.

Output Fraction
~~~~~~~~~~~~~~~

Specify output path for fraction raster.

....

Raster from Vector
------------------

Converts vector to raster (using `gdal rasterize <http://gdal.org/python/osgeo.gdal-module.html#RasterizeOptions>`_).

Pixel Grid
~~~~~~~~~~

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

Create Sample from synthetically mixed Endmembers
-------------------------------------------------

Derives a class fraction sample by synthetically mixing (pure) spectra from a classification sample.

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

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

Output Fraction
~~~~~~~~~~~~~~~

Specify output path for fraction raster.

....

Extract samples from raster and mask
------------------------------------

Extract samples from raster and mask.

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

....

Extract classification samples from raster and classification
-------------------------------------------------------------

Extract classification samples from raster and classification.

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

....

Extract regression samples from raster and regression
-----------------------------------------------------

Extract regression samples from raster and regression.

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

....

Extract fraction samples from raster and fraction
-------------------------------------------------

Extract fraction samples from raster and fraction.

Raster
~~~~~~

Specify input raster.

ClassFraction
~~~~~~~~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

List of values and ranges that are mapped to True, e.g. [1, 2, 5, range(5, 10)].

Background values
~~~~~~~~~~~~~~~~~

List of values and ranges that are mapped to False, e.g. [-9999, range(-10, 0)].

Output Mask
~~~~~~~~~~~

Specify output path for mask raster.

....

Apply Mask to Raster
--------------------

Pixels that are masked out are set to the raster no data value.

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

Fraction as RGB Raster
----------------------

Creates a RGB representation from given class fractions. The RGB color of a specific pixel is the weighted mean value of the original class colors, where the weights are given by the corresponding class propability.


ClassFraction
~~~~~~~~~~~~~

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

Resampling
==========

Spatial Resampling (Raster)
---------------------------

Resamples a Raster into a target grid.

Pixel Grid
~~~~~~~~~~

Specify input raster.

Raster
~~~~~~

Specify input raster.

Resampling Algorithm
~~~~~~~~~~~~~~~~~~~~

Specify resampling algorithm.

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Spatial Resampling (Mask)
-------------------------

Resamples a Mask into a target grid.

Pixel Grid
~~~~~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Output Mask
~~~~~~~~~~~

Specify output path for mask raster.

....

Spatial Resampling (Classification)
-----------------------------------

Resamples a Classification into a target grid.

Pixel Grid
~~~~~~~~~~

Specify input raster.

Classification
~~~~~~~~~~~~~~

Specify input raster.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Minimal dominant coverage
~~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have a coverage of the predominant class less than the specified value. This controls pixel purity.

Output Classification
~~~~~~~~~~~~~~~~~~~~~

Specify output path for classification raster.

....

Spatial Resampling (Regression)
-------------------------------

Resamples a Regression into a target grid.

Pixel Grid
~~~~~~~~~~

Specify input raster.

Regression
~~~~~~~~~~

Specify input raster.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Output Regression
~~~~~~~~~~~~~~~~~

Specify output path for regression raster.

....

Spatial Resampling (Fraction)
-----------------------------

Resamples a Fraction into a target grid.

Pixel Grid
~~~~~~~~~~

Specify input raster.

ClassFraction
~~~~~~~~~~~~~

Specify input raster.

Minimal overall coverage
~~~~~~~~~~~~~~~~~~~~~~~~

Mask out all pixels that have an overall coverage less than the specified value. This controls how edges between labeled and no data regions are treated.

Output Fraction
~~~~~~~~~~~~~~~

Specify output path for fraction raster.

....

Spectral Resampling
-------------------

Spectrally resample a raster.

Raster
~~~~~~

Select raster file which should be resampled.

[Options 1] Spectral characteristic from predefined sensor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

undocumented parameter

[Option 2] Spectral characteristic from Raster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Raster with defined wavelength and fwhm

[Option 3] Spectral characteristic from response function files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Select path to an ENVI (e.g. .sli or .esl).

Resampling Algorithm
~~~~~~~~~~~~~~~~~~~~

undocumented parameter

Output Raster
~~~~~~~~~~~~~

Specify output path for raster.

....

Transformation
==============

Fit FactorAnalysis
------------------

Fits a Factor Analysis.

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

Raster
~~~~~~

Specify input raster.

Mask
~~~~

Specified vector or raster is interpreted as a boolean mask.

In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.

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

