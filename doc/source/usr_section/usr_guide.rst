.. |openmapwindow| image:: ../../../enmapbox/gui/ui/icons/viewlist_mapdock.svg
    :width: 30px
.. |linkbasic| image:: ../../../enmapbox/gui/ui/icons/link_basic.svg
    :width: 30px
.. |linkscalecenter| image:: ../../../enmapbox/gui/ui/icons/link_mapscale_center.svg
    :width: 30px



.. _usr_guide:

==========
User Guide
==========


Image Classification
====================

.. note:: In this guide you will learn how to perform an image classification and validation using the EnMAP-Box and the
          test dataset that comes with it. The input image is a simulated EnMAP image acquired over the city of Berlin
          and a detailed vector dataset with the classes Roof, Pavement, Low vegetation, Tree, Soil and Other will be used as reference.

          .. figure:: ../img/graphical_model_classification.png

             Graphical model of the classification workflow presented in the steps below.


Load data / preprocessing
-------------------------

1. Go to :menuselection:`Project --> Load Example data`. When clicking for the first time, the software will ask you whether you want
   to download the data, confirm this, and then you should see the following datasets in your ``Data Sources`` panel.
     * EnMAP_BerlinUrbanGradient.bsq
     * HighResolution_BerlinUrbanGradient.bsq *(not needed here)*
     * LandCov_BerlinUrbanGradient.shp
     * SpecLib_BerlinUrbanGradient.sli *(not needed here)*


   .. attention:: Before fitting a classifier, you have to convert the vector reference dataset into a raster with the same
                  resolution as the image to be classified. See next step...

2. In the Processing Toolbox panel, go to :menuselection:`EnMAP-Box --> Create Raster --> Classification from Vector` and double-click
   on the algorithm (alternatively you might directly type 'Classification from Vector' into the search bar to find the algorithm).
     * Mind the help sidebar on the right of the window, where the algorithm and each of its parameters are described.
     * In the algorithm window, set the following parameters (most are default):

       * ``PixelGrid``: EnMAP_BerlinUrbanGradient.bsq
       * ``Vector``: LandCov_BerlinUrbanGradient.shp
       * ``Class id attribute``: Level_2_ID
       * ``Class Definition``:

        .. code-block:: batch

            ClassDefinition(classes=6, names=['Roof', 'Pavement', 'Low vegetation', 'Tree', 'Soil', 'Other'], colors=['#e60000', '#9c9c9c', '#98e600', '#267300', '#a87000', '#f5f57a'])

       * ``Minimal overall coverage``: 0.0
       * ``Minimal dominant coverage``: 0.0
       * ``Oversampling factor``: 1
       * Click **Run in Background**
       |

      .. note:: Those default settings might not always be a good choice, e.g. if you desire to use more pure pixels for
                the reference dataset, consider changing ``Minimal overall coverage`` and ``Minimal dominant coverage``,
                e.g. to 0.9 and 0.7, respectively, with an ``Oversampling factor`` of 2.

Fit classifier
--------------

3. Now we fit a random forest classifier. In the Processing Toolbox go to :menuselection:`EnMAP-Box --> Classification --> Fit RandomForestClassifier`.
   As ``Raster`` select *EnMAP_BerlinUrbanGradient.bsq*, as ``Classification`` select the image you just created in the previous step. In the ``Code``
   window change

   .. code-block:: python

      estimator = RandomForestClassifier()

   to

   .. code-block:: python

      estimator = RandomForestClassifier(n_estimators=100)

  This will increase the number of trees the random forest uses to 100. The default is at 10, which is a bit low. Specify the
  output path for the .pkl file and click **Run in Background**.

Predict image
-------------

4. Finally, to classify the image go to :menuselection:`EnMAP-Box --> Classification --> Predict Classification`.
   Select *EnMAP_BerlinUrbanGradient.bsq* as input ``Raster`` and the .pkl file from the previous step as ``Classifier``.
   Specify the output path and click **Run in Background**.

.. figure:: ../img/screenshot_classification_result.png

   Screenshot showing the classification result in the right Map View and the underlying EnMAP image & vector reference in left Map View.


Accuracy Assessment
-------------------

5. Go to :menuselection:`EnMAP-Box --> Accuracy Assessment --> Classification Performance`. Select the predicted image from
   step 4 as ``Prediction`` and the rasterized reference dataset from step 2 as ``Reference``. Specify the output path
   for the ``HTML Report`` or save to temporary file and select **Run in Background**.

   Now a HTML report should anatomically open. If not, open the .html file manually or in QGIS go to :menuselection:`View --> Panels --> Results Viewer`.

   .. figure:: ../img/screenshot_aareport.png

      Exemplary screenshot of a accuracy assessment HTML report

   .. important:: In this example we used the same dataset for training the classifier and assessing the accuracy of our
                  prediction, which is not good practise and results in exaggerated accuracies. One solution to this is to
                  split the reference dataset into a training and validation part. See the following section on how to do this
                  using the EnMAP-Box...

Splitting the reference data
----------------------------

.. note::
          Here we will repeat the classification process, but this time we are going to split the reference dataset into a training and
          a validation sample:

          .. figure:: ../img/split_training_reference.png

                      **left:** Rasterized vector reference dataset, **middle:** subset for training, **right:** subset for validation


* Select the algorithm :menuselection:`Random --> Random Points from Classification`. Under ``Classification`` select the
  rasterized reference dataset from step 2. For ``Number of Points per Class`` enter 0.3, which will randomly draw 30% of
  pixels from each class and return them as a point vector dataset.
* Go to :menuselection:`Masking --> Apply Mask to Raster`. Select the reference classification as ``Raster`` and the
  created point vector dataset as ``Mask``. Save the output with a useful name, such as *training.tif*.
  Then repeat this step with the same inputs, but this time use the ``Invert Mask`` setting and save your image as
  *validation.tif* or similar.
* Now repeat the classification workflow above starting from step 4. Only this time, use the training subset in step 4 as
  input under ``Labels`` for *Fit RandomForestClassifier*. Use the validation subset in step 5 as ``Reference`` in *Classification Performance*.


Image Regression
================


Graphical Modeller
==================

.. run as script from console.....

Spectral Library Import
=======================





