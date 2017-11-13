Welcome to the HUB-Datacube documentation!
==========================================

The HUB-Datacube (HUBDC) offers a high level interface for integrating heterogeneous raster and vector datasets
into a user-defined reference pixel grid, resulting in an analysis-ready datacube.
The data model is build on top of
`GDAL <http://gdal.org>`_ and
`Numpy <http://www.numpy.org>`_, and was greatly inspired by the
`Raster I/O Simplification (RIOS) <http://rioshome.org>`_ project.

Like RIOS, HUBDC provides functionality which makes it easy to write raster processing code in Python,
but it gives the user more flexibility and has some performance improvements.

Example
-------

.. image:: images/ndvi.png

.. literalinclude:: examples/example.py

See :doc:`ApplierExamples` for more information.

.. toctree::
    :maxdepth: 1
    :caption: Contents:

    ApplierExamples.rst
    Downloads.rst
    hubdc_applier.rst
    hubdc_model.rst
    hubdc_testdata.rst
    indices.rst

.. codeauthor:: Andreas Rabe
