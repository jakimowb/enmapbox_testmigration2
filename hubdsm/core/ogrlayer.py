# from __future__ import annotations
from dataclasses import dataclass
from os.path import exists

from osgeo import gdal, ogr

from hubdsm.core.extent import Extent
from hubdsm.core.location import Location
from hubdsm.core.projection import Projection
from hubdsm.core.size import Size


@dataclass(frozen=True)
class OgrLayer(object):
    """OGR vector layer dataset."""
    ogrLayer: ogr.Layer
    ogrDataSource: ogr.DataSource

    def __post_init__(self):
        assert isinstance(self.ogrLayer, ogr.Layer)

    @staticmethod
    def open(filename: str, layerNameOrIndex=None) -> 'OgrLayer':
        from hubdsm.core.ogrdatasource import OgrDataSource
        return OgrDataSource.open(filename=filename).layer(nameOrIndex=layerNameOrIndex)

    @property
    def projection(self):
        """Return projection."""
        return Projection(wkt=self.ogrLayer.GetSpatialRef().ExportToWkt())

    @property
    def extent(self):
        """Return layer extent."""
        xmin, xmax, ymin, ymax = self.ogrLayer.GetExtent()
        return Extent(ul=Location(x=xmin, y=ymax), size=Size(x=xmax - xmin, y=ymax - ymin))

    # def rasterizeAsArray(
    #         self, grid: Grid, gdt: int = None, initValue=0, burnValue=1, burnAttribute=None, allTouched=False,
    #         filterSQL: str = None
    # ) -> np.ndarray:
    #     '''Return rasterization as 2d array.'''
    #     assert isinstance(grid, Grid)
    #     if gdt is None:
    #         gdt = gdal.GDT_Float32
    #     self.ogrLayer.SetAttributeFilter(filterSQL)
    #     self.ogrLayer.SetSpatialFilter(grid.extent.geometry.ogrGeometry)
    #     gdalRaster = MEM_DRIVER.create(grid=grid, bands=1, gdt=gdt)
    #     gdalRaster.band(number=1).fill(value=initValue)
    #     rasterizeLayerOptions = list()
    #     if allTouched:
    #         rasterizeLayerOptions.append('ALL_TOUCHED=TRUE')
    #     if burnAttribute:
    #         rasterizeLayerOptions.append('ATTRIBUTE=' + burnAttribute)
    #     gdal.RasterizeLayer(
    #         gdalRaster.gdalDataset, [1], self.ogrLayer, burn_values=[burnValue], options=rasterizeLayerOptions
    #     )
    #     gdal.RasterizeOptions()
    #     self.ogrLayer.SetAttributeFilter(None)
    #     return gdalRaster.band(number=1).readAsArray()
