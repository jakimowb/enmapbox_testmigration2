.. |action| image:: ../img/action.svg
   :width: 40px

.. |reset_plot| image:: ../img/pyqtgraph_reset.png
   :width: 15px


###########
User Manual
###########


The GUI
#######


Toolbar
=======

Data Sources
============


Data Views
==========


|
|
|

Tools
######

Scatter Plot
============

The Scatter Plot tool allows you to plot the values of two bands against each other. You can specify the following settings:

 * **Band X:** Choose the raster (first dropdown menu) and the band (second dropdown menu) to be plotted on the X-axis.
   ``Min`` and ``Max`` depict the limits of the axis. By default, Min and Max will be automatically derived. You can also
   manually specify the limits of the axis by entering another value.
 * **Band Y:** Same as above, just for the Y-axis.
 * **Mask (optional):** You can specify a mask here, so that pixels which are covered by the mask will not be included in the
   scatterplot.
 * **Accuracy:** Can either be set to *Estimated (faster)* or *Actual (slower)*. Defines whether to use a subset of pixels for calculation
   or all of them.
 * **Number of Bins:** Defines the number of bins in x and y direction.

After you entered all settings, click the |action| button to create the plot.

.. figure:: ../img/scatterplot_tool.png

   Screenshot of the Scatter Plot Tool

**Scatterplot Navigation**

* The plot window is interactive, which means you can zoom in and out using the mouse.
* Reset the plot window to the default zoom level by clicking the |reset_plot| button in the lower left of the plot window.
* Right-clicking inside the plot offers you several additional options.
* Change the color scheme of the plot by right-clicking into the color bar on the right.




Metadata editor
===============

Reclassify
==========

Raster Builder
==============




Applications
############

ImageMath
=========

Image Statistics
================

Synthmix Regression Mapper
==========================

EO Time Series Viewer
=====================

Please visit `Read the Docs - EO Time Series Viewer for more information <https://eo-time-series-viewer.readthedocs.io/en/latest/>`_

Agricultural Applications
=========================

IVVRM
~~~~~

**Interactive Visualization of Vegetation Reflectance Models:**




|
|
|


Processing Data Types
#####################

General processing schema
=========================

.. todo:: add figure

Raster
======

**Supported output filetypes:**

* .tif
* ...
* ...
* ...
* ...

Mask
====

Mask files can be used to exclude pixels from certain processes. This allows to constrain operations on regions of
interest only and to reduce computational costs. Any GDAL/OGR readable raster or vector file can be interpreted as a boolean mask.

    * In case of a vector, all pixels covered by features are interpreted as True, all other pixels as False.

    * In case of a raster, all pixels that are equal to the no data value (default is 0) are interpreted as False, all other pixels as True.
      Multiband rasters are first evaluated band wise. The final mask for a given pixel is True, if all band wise masks for that pixel are True.
      It is assumed that all pixels with a value of zero mark a position that is to be masked and neglected during a specific operation.

Classification
==============

Regression
==========

Fraction
========

Spectral Library
================

Sample
======

Fit
===



|
|
|



.. include:: ../geoalgorithms/ga.rst


