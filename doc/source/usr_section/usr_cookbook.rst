.. |openmapwindow| image:: ../../../enmapbox/gui/ui/icons/viewlist_mapdock.svg
    :width: 30px
.. |linkbasic| image:: ../../../enmapbox/gui/ui/icons/link_basic.svg
    :width: 30px
.. |linkscalecenter| image:: ../../../enmapbox/gui/ui/icons/link_mapscale_center.svg
    :width: 30px
.. |action| image:: ../img/action.svg
   :width: 40px


.. _usr_cookbook:

========
Cookbook
========

This section is a collection of 'recipes' for common tasks you can perform in the EnMAP-Box. If you miss topics,
feel free to suggest new entries here!


Working with the GUI
====================

Opening WMS data in a Map Window
================================


Using Processing Algorithms
===========================


Clip a raster with a vector
===========================

Clipping a raster to the bounds of a vector layer is fairly simple in the EnMAP-Box, since vector layers can be
interpreted as :ref:`masks <mask>`.

* Go to the Processing Algorithms and select *Masking -> Apply Mask to Raster*
* Under ``Raster`` select the raster layer you want to clip, and under ``Mask`` select the vector layer.
* Optional: If you want to 'invert the clip', which means that only pixels are included which are NOT within a polygon,
  simply activate the ``Invert Mask`` option.


  .. figure:: ../img/cb_cliprasterwvector.png
     :width: 100%

     Output example: Input raster (left), vector geometry for clipping (middle) and resulting output (right)


.. attention::

   This method will just mask the raster according to the vector geometries, the extent will not be altered,
   which means the raster will not be cropped to the extent of the vector layer. You may use the raster builder tool
   for this.


Create a spatial subset (crop)
==============================

Create a spectral subset
========================



.. _graphical_modeler:

Graphical Modeler
=================


.. note:: This section demonstrates how to use the Graphical Modeler in QGIS with EnMAP-Box processing algorithms
          in order to automate common workflows. Instead of manually clicking our way through the
          processing algorithms, we will build a model which combines all the steps and can potentially be reused and
          generalized for further applications of image classification.

          You can find general information on the Graphical Modeler in the `QGIS documentation <https://docs.qgis.org/2.8/en/docs/user_manual/processing/modeler.html>`_.

#. Start the EnMAP-Box and load the test dataset under :menuselection:`Project --> Load example data`.
#. In the menubar go to :menuselection:`Processing --> Graphical Modeler`. In the Modeler you have two major
   items or building blocks, which are the ``Inputs`` and ``Alogrithms``. The latter basically lists all algorithms
   available in the QGIS Processing Toolbox and the first lists all available types of inputs, which can be used by the
   processing algorithms.
#. For image classification we need at least an input raster and a reference dataset. In case of the EnMAP-Box testdata
   the reference dataset is a point shapefile. Under ``Inputs`` search for *Raster Layer* and select it (double-click or drag-and-drop).
   As ``Parameter Name`` you can for example choose *input_image*. Mind how this input graphically appears in the main window.
   Now again, look for *Vector Layer*, double-click, and assign a name, e.g. *reference_vector*.

   .. note:: You can of course change the ``Parameter name`` as you wish, but it might be easier to follow this guide when you use the suggestions.

#. Add a *Vector Field* input to the model. Enter *reference_field* as ``Parameter name`` and *reference_vector* as ``Parent layer``.
   Furthermore, add a *String input*, name it *cd_text* and deselect the ``Mandatory`` option. We are going to need those
   inputs for the following algorithm.
#. Now we need the *Classification from Vector* algorithm in order to rasterize the reference dataset. Find it in the
   ``Algorithms`` tab and select it.  Now enter the following parameters:
    * ``Pixel grid``: input_image
    * ``Vector``: reference_vector
    * ``Class id attribute``: reference_field
    * ``Minimal overall coverage``: 0.0
    * ``Minimal dominant coverage``: 0.0
    * ``Oversampling factor``: 1


#. Now add the *Fit RandomForestClassifier* algorithm to your model. In the dialog, select *input_image* as ``Raster`` and
   under ``Labels`` select *'Output Classification' from algorithm 'Classification from Vector'*. Leave the rest at default
   and click :guilabel:`OK`.

#. In the next step select the *Predict Classification* Algorithm. Under ``Raster`` select *input_image* and under ``Classifier``
   select *'Output Classifier' from algorithm 'Fit RandomForestClassifier'*. Enter a name under ``Output Classification``, e.g.
   *predicted_image*. Confirm with :guilabel:`OK`.
#. The model is already able to run and perform an image classification, but we will add the generation of an Accuracy Assessment.
   Look for the Algorithm *Classification Performance* and select it. Choose *'Output Classification' from algorithm 'Predict Classification'* as
   ``Prediction`` and *'Output Classification' from algorithm 'Classification from Vector'* as ``Reference``. Specify a name
   under ``HTML Report``, for example *accuracy_assessment*.

#. Under ``Model properties`` you can specify a name and a group for your model and save it.
#. Click the run button or press F5 to test your model. Use the following settings:

    * ``input_image``: enmap_berlin.bsq
    * ``reference_vector``: landcover_berlin_point.shp
    * ``reference_field``: level_2_id

   .. figure:: ../img/screenshot_graphical_model.png

      Screenshot of the final model and the resulting processing algorithm dialog (lower left)

#. After saving, your model will also appear in the Processing toolbox:

   .. image:: ../img/screenshot_toolbox_models.PNG

.. admonition:: Final remarks

   * Mind that this example was quite specific to the EnMAP test dataset. You might want to alter the model in a way that it
     is more generalizable or fitting for your specific use cases.
   * Also, consider extending the model inputs to have even more parameters to select from, e.g. by using the Number input type
     to make the parameter *Minimal overall coverage* from the algorithm *Classification from Vector* directly specifiable as a parameter
     in your model dialog.
   * Consider including a separate reference dataset as an additional selectable input parameter

Spectral Library
================


Map Algebra with ImageMath
==========================

You can open the ImageMath raster calculator under *Applications -> ImageMath*

Calculate NDVI
~~~~~~~~~~~~~~

* Make sure to open the testdatasets for this example
* Specify the input and output parameters according to the screenshot below (you can of course alter the names, but make
  sure to also adapt them in the script)

  .. image:: ../img/im_input_ndvi.png

* Enter this code in the editor on the right side. You do not need to alter ``Output Grid`` and ``Processing`` for now.

  .. code-block:: python

     # retrieve nodata value
     nodata = noDataValue(enmap)
     # select the red band
     red = enmap[38]
     # select the nir band
     nir = enmap[64]
     # calculate ndvi
     ndvi = (nir-red)/(nir+red)
     # set all cells to nodata that where nodata before
     ndvi[red == nodata] = nodata
     # set nodata value in the metadata
     setNoDataValue(ndvi, nodata)


* Click the run button |action|. The result should be listed in the ``Data Sources`` panel.

Mask raster with vector
~~~~~~~~~~~~~~~~~~~~~~~

* Make sure to open the testdatasets for this example
* Select *enmap_berlin.bsq* under ``Inputs`` and name it **enmap**. Further select *landcover_berlin_polygon.shp* and name
  it **mask**.
* Under ``Outputs`` specify output path and file and name it **result**


* Enter this code in the editor

  .. code-block:: python

     result = enmap
     # set all cells not covered by mask to nodata
     result[:, mask[0] == 0] = noDataValue(enmap)
     # specify nodata value
     setNoDataValue(result, noDataValue(enmap))
     # copy metadata to result raster
     setMetadata(result, metadata(enmap))

* Click the run button |action|. The result should be listed in the ``Data Sources`` panel.