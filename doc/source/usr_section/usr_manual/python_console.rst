.. include:: /icon_links.rst

.. _python_console:

QGIS Python Console
*******************

The QGIS Python Console allows the user to interact with the current state of QGIS.
For example, returning the map layer instance of the currently selected layer inside the QGIS Layer panel, use::

    >>> iface.activeLayer()
    <qgis._core.QgsRasterLayer object at 0x25D43C60>

We provide similar functionality for directly accessing raster/vector data and corresponding HUB Datacube instances.

Active Layer Data
=================

To directly access the data of a raster layer or the attribute table of a vector layer, use `enmapbox.Qgis.activeData()`.

    >>> import enmapbox

In case of a raster, a 3d numpy array is returned with shape = (bands, lines, samples).

    >>> array = enmapbox.Qgis.activeData()
    >>> array.shape
    (177, 400, 220)

To only read single raster band data use the `index` parameter::

    >>> array = enmapbox.Qgis.activeData(index=0) # first band only
    >>> array.shape
    (400, 220)

In case of a vector, an ordered dictionary is returned with field names as keys and associated lists of attribute values::

    >>> enmapbox.Qgis.activeData()
    OrderedDict([('level_1_id', [1, 2, 2, 3, 4]),
                 ('level_1', ['impervious', 'vegetation', 'vegetation', 'soil', 'water']),
                 ('level_2_id', [1, 2, 3, 4, 5]),
                 ('level_2', ['impervious', 'low vegetation', 'tree', 'soil', 'water'])])

Active Layer Datasets
=====================

To directly create a raster or vector dataset use `enmapbox.Qgis.activeDataset()`.

    >>> import enmapbox

In case of a raster, a HUB Datacube RasterDataset is returned.
See the `Developer Cookbook <https://enmap-box.readthedocs.io/en/latest/dev_section/dev_cookbook/hubdc/usage/core.html#raster-dataset>`_ for details::

    >>> enmapbox.Qgis.activeDataset()
    RasterDataset(gdalDataset=<osgeo.gdal.Dataset; proxy of <Swig Object of type 'GDALDatasetShadow *' at 0x20D6D290> >)

In case of a vector, a HUB Datacube VectorDataset is returned.
See the `Developer Cookbook <https://enmap-box.readthedocs.io/en/latest/dev_section/dev_cookbook/hubdc/usage/core.html#vector-dataset>`_ for details::

    >>> enmapbox.Qgis.activeDataset()
    VectorDataset(ogrDataSource=<osgeo.gdal.Dataset; proxy of <Swig Object of type 'GDALDatasetShadow *' at 0x20BB9F68> >, layerNameOrIndex=0)

