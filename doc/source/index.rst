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

::

    """
    Calculate Normalized Difference Vegetation Index (NDVI) for a Landsat 5.
    """

    import tempfile
    import os
    import numpy
    from hubdc.applier import Applier, ApplierOperator, ApplierInputRaster, ApplierOutputRaster
    from hubdc.testdata import LT51940232010189KIS01

    # Set up input and output filenames.
    applier = Applier()
    applier.inputRaster.setRaster(key='red', value=ApplierInputRaster(filename=LT51940232010189KIS01.red))
    applier.inputRaster.setRaster(key='nir', value=ApplierInputRaster(filename=LT51940232010189KIS01.nir))
    applier.outputRaster.setRaster(key='ndvi', value=ApplierOutputRaster(filename=os.path.join(tempfile.gettempdir(), 'ndvi.img')))

    # Set up the operator to be applied
    class NDVIOperator(ApplierOperator):
        def ufunc(operator):
            red = operator.inputRaster.getRaster(key='red').getImageArray()
            nir = operator.inputRaster.getRaster(key='nir').getImageArray()
            ndvi = numpy.float32(nir-red)/(nir+red)
            operator.outputRaster.getRaster(key='ndvi').setImageArray(array=ndvi)

    # Apply the operator to the inputs, creating the outputs.
    applier.apply(operator=NDVIOperator)
    print(applier.outputRaster.getRaster(key='ndvi').filename)


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
