.. include:: /icon_links.rst

.. _applications:

Applications
************

.. TODO add ensomap https://gitext.gfz-potsdam.de/stephane/HYSOMA-ENSOMAP

ImageMath
=========

.. _synthMix:

Regression-based unmixing (synthMix)
====================================


.. _Classification Workflow:

Classification Workflow
=======================

You can find the Classification Workflow in the menu bar :menuselection:`Applications --> Classification Workflow`

.. figure:: /img/classification_workflow.png

   Classification Workflow Application

Input Parameters:

* **Training Inputs**

  * :guilabel:`Raster`: Specify input raster based on which samples will be drawn for training a classifier.
  * :guilabel:`Reference`: Specify vector dataset with reference information. Has to have a column in the attribute table with a
    unique class identifier (numeric). This vector dataset is rasterized/burned on-the-fly onto the grid of
    the input raster in order to extract the sample. If the vector source is a polygon dataset, only polygons which cover more than
    75% of a pixel in the target grid are rasterized (this default behavior can be altered by pressing :kbd:`F1`,
    which will make these settings adjustable in the GUI).
  * :guilabel:`Attribute`: Attribute field in the reference vector layer which contains the unique class identifier.

* **Sampling**

  Once you specified all inputs in the Training inputs section, you can edit the class colors, names and class sample sizes
  in the Sampling submenu.

  * :guilabel:`Sample size` |combo| |spin| Specify the sample size per class, either relative in percent or in absolute pixel counts.
  * The total sample size is shown below
  * |cb0| :guilabel:`Save sample`: Activate this option and specify an output path to save the sample as a raster.

* **Training**

  * In the :guilabel:`Classifier` |combo| dropdown menu you can choose different classifiers (e.g. Random Forest, Support Vector Machine)
  * |mIconCollapse| :guilabel:`Model parameters`: Specify the parameters of the selected classifier.

     .. hint::

        Scikit-learn python syntax is used here, which means you can specify model parameters accordingly. Have a look at
        the scikit-learn documentation on the individual parameters, e.g. for the `RandomForestClassifier <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html>`_

  * |cb0| :guilabel:`Save model`: Activate this option to save the model file (:file:`.pkl`) to disk.

* **Mapping**

  * :guilabel:`Raster`: Specify the raster you would like to apply the trained classifier to (usually -but not necessarily-
    this is the same as used for training)
  * :guilabel:`Mask`: Specify a :ref:`mask <datatype_mask>` layer if you want to exclude certain areas from the prediction.

      * Outputs:

         * :guilabel:`Classification`: Output path where to write the classification image to.
         * :guilabel:`Probability`: Output path of the class probability image.

           .. hint:: This outputs the result of a classifiers ``predict_proba`` method. Note that depending on the classifier this
                     option might not be available or has to be activated in the model parameters (e.g. for the Support Vector Machine,
                     the line ``svc = SVC(probability=False)`` has to be altered to ``svc = SVC(probability=True)``
         * :guilabel:`RGB`: Generates a RGB visualisation based on the weighted sum of class colors and class probabilities.

* **Cross-validation Accuracy Assessment**

  * |cb0| Cross-validation with n-folds |spin|: Activate this setting to assess the accuracy of the classification by performing cross
    validation. Specify the desired number of folds (default: 3). HTML report will be generated at the specified output path.

.. admonition:: Run the classification workflow

   Once all parameters are entered, press the |action| button to start the classification workflow.

|

....

|

.. _Regression Workflow:

Regression Workflow
===================

You can find the Regression Workflow in the menu bar :menuselection:`Applications --> Classification Workflow`

.. seealso:: Have a look at the :ref:`Biomass Mapping Tutorial <tutorial_biomass>` for a use case example of the Regression Workflow Application.

Input Parameters:

* **Training Inputs**

  * :guilabel:`Raster`: Specify input raster based on which samples will be drawn for training a regressor.
  * :guilabel:`Reference`: Specify vector dataset with reference information. Has to have a numeric column in the attribute table with a
    target variable of interest. This vector dataset is rasterized/burned on-the-fly onto the grid of
    the input raster in order to extract the sample. If the vector source is a polygon dataset, all pixels will be drawn which
    intersect the polygon.

  * :guilabel:`Attribute`: Attribute field in the reference vector layer which contains the regression target variable.

* **Sampling**

  * :guilabel:`Number of Strata` |spin|: Specify the desired number of strata sampling. If you don't want to use
    stratified sampling, just enter ``1``.
  * :guilabel:`Min` & :guilabel:`Max`: Defines the value range in which samples should be drawn.
  * :guilabel:`Sample size` |combo| |spin|: Specify the sample size per stratum, either relative in percent or in absolute pixel counts.

    Every stratum is listed below with the value range that is covered by this stratum depicted in square brackets
    (e.g., ``Stratum 1: [1.0, 4.33]``). Furthermore, you can see and alter the number of pixels/samples for each stratum using the |spin| spinboxes.
  * |cb0| :guilabel:`Save sample`: Activate this option and specify an output path to save the sample as a raster.

* **Training**

  * In the :guilabel:`Regressor` |combo| dropdown menu you can choose different regressors (e.g. Random Forest, Support Vector Regression, Kernel Ridge Regression)
  * |mIconCollapse| :guilabel:`Model parameters`: Specify the parameters of the selected regressor.

     .. hint::

        Scikit-learn python syntax is used here, which means you can specify model parameters accordingly. Have a look at
        the scikit-learn documentation on the individual parameters, e.g. for the `RandomForestRegressor <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>`_

  * |cb0| :guilabel:`Save model`: Activate this option to save the model file (:file:`.pkl`) to disk.

* **Mapping**

  * :guilabel:`Input Raster`: Specify the raster you would like to apply the trained regressor to (usually -but not necessarily-
    this is the same as used for training)

* **Cross-validation Accuracy Assessment**

  * |cb0| Cross-validation with n-folds |spin|: Activate this setting to assess the accuracy of the regression by performing cross
    validation. Specify the desired number of folds (default: 3). HTML report will be generated at the specified output path.

.. admonition:: Run the classification workflow

   Once all parameters are entered, press the |action| button to start the regression workflow.


EO Time Series Viewer
=====================

Please visit `EO Time Series Viewer Documentation <https://eo-time-series-viewer.readthedocs.io/en/latest/>`_ for more information.

Agricultural Applications
=========================

Please visit `LMU Vegetation Apps Documentation <https://enmap-box-lmu-vegetation-apps.readthedocs.io/en/latest/>`_ for more information.
