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

Applications / Tools
####################



Image Statistics
================

Reclassify
==========


Scatterplot
===========


Virtual Raster Builder
======================


imageMath Calculator
====================

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
* .vrt
* .bil
* .bsq
* .bip

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

... PICKLE File


|
|
|



.. include:: ../geoalgorithms/ga.rst


