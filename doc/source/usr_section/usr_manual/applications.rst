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

* Training Inputs

  * :guilabel:`Raster`
  * :guilabel:`Reference`
  * :guilabel:`Attribute`

* Sampling

  * :guilabel:`Sample size`
  * The total sample size is shown below
  * |cb0| :guilabel:`Save sample`: Activate this option and specify an output path to save the sample as a raster.

* Training

  * In the :guilabel:`Classifier` |combo| dropdown menu you can choose different classifiers (e.g. Random Forest, Support Vector Machine)
  * |mIconCollapse| :guilabel:`Model parameters`: Specify the parameters of the selected classifier.

     .. hint::

        Scikit-learn python syntax is used here, which means you can specify model parameters accordingly. Have a look at
        the scikit-learn documentation on the individual parameters, e.g. for the `RandomForestClassifier <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html>`_

  * |cb0| :guilabel:`Save model`: Activate this option to save the model file (:file:`.pkl`) to disk.

* Mapping

  * :guilabel:`Raster`:
  * :guilabel:`Mask`:

      * Outputs:

         * :guilabel:`Classification`
         * :guilabel:`Probability`
         * :guilabel:`RGB`

* Cross-validation Accuracy Assessment

.. admonition:: Run the classification workflow

   Once all parameters are entered, press the |action| button to start the classification workflow.


.. _Regression Workflow:

Regression Workflow
===================



EO Time Series Viewer
=====================

Please visit `EO Time Series Viewer Documentation <https://eo-time-series-viewer.readthedocs.io/en/latest/>`_ for more information.

Agricultural Applications
=========================

Please visit `LMU Vegetation Apps Documentation <https://enmap-box-lmu-vegetation-apps.readthedocs.io/en/latest/>`_ for more information.
